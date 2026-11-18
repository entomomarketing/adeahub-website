#!/usr/bin/env python3
"""Build the adeahub website in place.

    python3 tools/build.py            # regenerate everything, then run the checks
    python3 tools/build.py --check    # only run the checks (exit code 1 on errors)

public/ is both the source you edit and the folder you deploy. The build is idempotent and only
rewrites the generated parts of each page:

  <!-- site:head:start --> … <!-- site:head:end -->      meta tags, canonical, social tags, JSON-LD (from src/site.json)
  <!-- site:css:start -->  … <!-- site:css:end -->       link to the compiled stylesheet (kept after page <style>s)
  (assets/css/base.css, the shared design-system rules, is linked inside site:head, i.e. BEFORE page <style>s)
  <!-- site:header:start --> … <!-- site:header:end -->  skip link + header/mega-menus/mobile menu (tools/chrome.py)
  <!-- site:footer:start --> … <!-- site:footer:end -->  footer (tools/chrome.py)
  <i data-lucide="name" …></i>                           replaced by the inline Lucide SVG (cached in tools/icons/)

and writes public/assets/css/site.css (Tailwind, from src/css/site.css), sitemap.xml, robots.txt,
llms.txt, site.webmanifest, .well-known/security.txt, 404.html and the favicon set. The checks also hold every
<form data-form> to src/forms.json and public/_headers to the security baseline. Needs only Python 3; the pinned standalone
Tailwind CLI is downloaded (and checksum-verified) into tools/.bin/ on first use.
"""
import argparse, datetime, hashlib, html, json, os, platform, posixpath, re, stat, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import chrome  # noqa: E402

TW_VERSION = "3.4.17"
TW_SHA256 = {
    "macos-arm64": "a1d0c7985759accca0bf12e51ac1dcbf0f6cf2fffb62e6e0f62d091c477a10a3",
    "macos-x64": "6cbdad74be776c087ffa5e9a057512c54898f9fe8828d3362212dfe32fc933a3",
    "linux-x64": "7d24f7fa191d2193b78cd5f5a42a6093e14409521908529f42d80b11fde1f1d4",
    "linux-arm64": "69b1378b8133192d7d2feb12a116fa12d035594f58db3eff215879e4ad8cf39b",
    "windows-x64.exe": "67f1c5e3f5a03406a7bf5badf5ada09b79f3ae78ec43450c15f7e983068da346",
}
LUCIDE_VERSION = "1.69.0"
CURRENT_NAV = {"platform": "platform", "about": "about", "contact": "contact"}  # pages whose top-nav item is highlighted

errors, warnings = [], []
def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

def read(p): return open(p, encoding="utf-8").read()
def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p) or read(p) != s:
        open(p, "w", encoding="utf-8").write(s)
def esc(s): return html.escape(s, quote=True)
def digest(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()[:10]

def fill(s, name, content, required=True):
    pat = re.compile(rf"<!-- site:{name}:start -->.*?<!-- site:{name}:end -->", re.S)
    if not pat.search(s):
        if required: err(f"missing <!-- site:{name}:start/end --> markers")
        return s
    return pat.sub(lambda _: f"<!-- site:{name}:start -->\n{content}\n<!-- site:{name}:end -->", s, count=1)

# ───────────────────────── icons ─────────────────────────
ICON_DIR = os.path.join(ROOT, "tools", "icons")
def lucide_svg(name):
    path = os.path.join(ICON_DIR, name + ".svg")
    if not os.path.exists(path):
        url = f"https://unpkg.com/lucide-static@{LUCIDE_VERSION}/icons/{name}.svg"
        try:
            data = urllib.request.urlopen(url, timeout=30).read().decode()
        except Exception as e:
            err(f"icon '{name}' not cached and download failed ({e})"); return None
        os.makedirs(ICON_DIR, exist_ok=True); open(path, "w").write(data)
    return read(path)

ATTR_RE = re.compile(r'([\w:-]+)(?:\s*=\s*"([^"]*)")?')
def inline_icons(s):
    def repl(m):
        attrs = dict((k, v if v is not None else "") for k, v in ATTR_RE.findall(m.group(1)))
        name = attrs.pop("data-lucide")
        src = lucide_svg(name)
        if src is None: return m.group(0)
        inner = re.sub(r"\s+", " ", re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)).strip()
        inner = re.sub(r"\s*/>", "/>", inner).replace("> <", "><")
        base = {"xmlns": "http://www.w3.org/2000/svg", "width": "24", "height": "24", "viewBox": "0 0 24 24",
                "fill": "none", "stroke": "currentColor", "stroke-width": "2", "stroke-linecap": "round",
                "stroke-linejoin": "round"}
        cls = ("lucide lucide-" + name + " " + attrs.pop("class", "")).strip()
        attrs.pop("aria-hidden", None)
        base.update(attrs)
        out = "".join(f' {k}="{v}"' for k, v in base.items())
        return f'<svg{out} class="{cls}" aria-hidden="true">{inner}</svg>'
    return re.sub(r'<i\s+([^>]*\bdata-lucide="[^"]+"[^>]*)>\s*</i>', repl, s)

# ───────────────────────── tailwind ─────────────────────────
def tailwind_bin():
    sysname = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}[platform.system()]
    arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"
    key = f"{sysname}-{arch}" + (".exe" if sysname == "windows" else "")
    path = os.path.join(ROOT, "tools", ".bin", f"tailwindcss-{TW_VERSION}-{key}")
    if not os.path.exists(path):
        url = f"https://github.com/tailwindlabs/tailwindcss/releases/download/v{TW_VERSION}/tailwindcss-{key}"
        print(f"downloading Tailwind CLI {TW_VERSION} ({key}) …")
        data = urllib.request.urlopen(url, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != TW_SHA256[key]:
            sys.exit("Tailwind CLI checksum mismatch — refusing to run it")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").write(data)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path

def build_css():
    out = os.path.join(PUB, "assets", "css", "site.css")
    subprocess.run([tailwind_bin(), "-c", os.path.join(ROOT, "tailwind.config.js"), "-i", os.path.join(ROOT, "src", "css", "site.css"),
                    "-o", out, "--minify"], cwd=ROOT, check=True, capture_output=True)
    return out

# ───────────────────────── head / JSON-LD ─────────────────────────
def abs_url(site, path): return site["url"].rstrip("/") + "/" + path

def org_node(site):
    o = {"@type": "Organization", "@id": abs_url(site, "#organization"), "name": site["name"], "url": abs_url(site, ""),
         "logo": {"@type": "ImageObject", "@id": abs_url(site, "#logo"), "url": abs_url(site, site["logo"]), "width": 511, "height": 146, "caption": site["name"]},
         "image": {"@id": abs_url(site, "#logo")}, "description": site["description"], "slogan": site["tagline"],
         "email": site["email"], "sameAs": site["sameAs"], "areaServed": site["areaServed"], "knowsAbout": site["knowsAbout"],
         "parentOrganization": {"@type": "Organization", "name": site["parentOrganization"]},
         "contactPoint": [dict({"@type": "ContactPoint", "availableLanguage": "English"}, **c) for c in site["contactPoints"]]}
    return o

def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def faq_nodes(s):
    qa = []
    for item in re.findall(r'<div class="faq-item\b.*?</div>\s*</div>', s, re.S):
        q = re.search(r'<button[^>]*faq-trigger[^>]*>\s*<span[^>]*>(.*?)</span>', item, re.S)
        a = re.search(r'<div class="faq-answer[^"]*">(.*?)</div>', item, re.S)
        if q and a: qa.append({"@type": "Question", "name": text_of(q.group(1)), "acceptedAnswer": {"@type": "Answer", "text": text_of(a.group(1))}})
    return qa

def team_nodes(s, site):
    people = []
    for img, name, role in re.findall(r'<img [^>]*src="[^"]*team/([\w-]+)\.webp"[^>]*>\s*<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', s, re.S):
        people.append({"@type": "Person", "name": text_of(name), "jobTitle": text_of(role),
                       "image": abs_url(site, f"assets/images/team/{img}.webp"), "worksFor": {"@id": abs_url(site, "#organization")}})
    seen, out = set(), []
    for p in people:
        if p["name"] not in seen: seen.add(p["name"]); out.append(p)
    return out

def jsonld(site, page, s):
    url = abs_url(site, page["path"])
    webpage = {"@type": page["type"], "@id": url + "#webpage", "url": url, "name": page["title"], "description": page["description"],
               "isPartOf": {"@id": abs_url(site, "#website")}, "about": {"@id": abs_url(site, "#organization")},
               "inLanguage": site["language"], "primaryImageOfPage": {"@type": "ImageObject", "url": abs_url(site, f"assets/images/social/{page['key']}.jpg"), "width": 1200, "height": 630}}
    graph = [org_node(site),
             {"@type": "WebSite", "@id": abs_url(site, "#website"), "url": abs_url(site, ""), "name": site["name"],
              "description": site["tagline"], "publisher": {"@id": abs_url(site, "#organization")}, "inLanguage": site["language"]},
             webpage]
    if page["path"]:
        webpage["breadcrumb"] = {"@id": url + "#breadcrumb"}
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": abs_url(site, "")},
            {"@type": "ListItem", "position": 2, "name": page["breadcrumb"], "item": url}]})
    if "service" in page:
        sv = page["service"]
        node = {"@type": "Service", "@id": url + "#service", "name": sv["name"], "serviceType": sv["serviceType"], "category": sv["category"],
                "description": page["description"], "url": url, "provider": {"@id": abs_url(site, "#organization")},
                "brand": {"@type": "Brand", "name": site["name"]}, "areaServed": site["areaServed"]}
        graph.append(node); webpage["mainEntity"] = {"@id": url + "#service"}
    if page.get("faq"):
        qa = faq_nodes(s)
        if qa:
            graph.append({"@type": "FAQPage", "@id": url + "#faq", "url": url, "mainEntity": qa, "isPartOf": {"@id": url + "#webpage"}})
        else:
            warn(f"{page['file']}: faq=true but no FAQ items found")
    if page.get("team"):
        people = team_nodes(s, site)
        if people:
            graph[0] = dict(graph[0], employee=people)
            webpage["mainEntity"] = {"@id": abs_url(site, "#organization")}
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

def tags_script(site):
    """Google Tag Manager, loaded only on the production hosts (site.tagHosts), never on staging or previews.
    ?tags=on / ?tags=off switches it for the browser session (sessionStorage), for Tag Assistant on a preview.
    window.dataLayer always exists, so forms.js can push hs_form_success either way."""
    hosts = "|".join(re.escape(h) for h in site.get("tagHosts", []))
    gtm = site.get("gtm", "")
    if not gtm or not hosts: return "<script>window.dataLayer=window.dataLayer||[];</script>"
    return ("<script>window.dataLayer=window.dataLayer||[];(function(w,d,s,l,i){var q=/[?&]tags=(on|off)\\b/.exec(location.search);"
            "try{if(q)sessionStorage.setItem('tags',q[1]);}catch(e){}" f"var on=/^({hosts})$/.test(location.hostname);"
            "try{var f=sessionStorage.getItem('tags');if(f==='on')on=true;if(f==='off')on=false;}catch(e){}if(!on)return;"
            "w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var t=d.getElementsByTagName(s)[0],j=d.createElement(s);"
            "j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;t.parentNode.insertBefore(j,t);})"
            f"(window,document,'script','dataLayer','{gtm}');</script>")

def head_html(site, page, p, s, js_v, base_v):
    url = abs_url(site, page["path"])
    og_img = abs_url(site, f"assets/images/social/{page['key']}.jpg")
    title, desc = esc(page["title"]), esc(page["description"])
    robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    L = ['<meta charset="utf-8">',
         "<script>document.documentElement.classList.add('js')</script>",
         tags_script(site),
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<meta name="color-scheme" content="light">',
         f"<title>{title}</title>",
         f'<meta name="description" content="{desc}">',
         f'<meta name="robots" content="{robots}">']
    if not page.get("noindex"): L.append(f'<link rel="canonical" href="{url}">')
    L += [f'<meta name="theme-color" content="{site["themeColor"]}">',
          f'<link rel="icon" href="{p}favicon.ico" sizes="48x48">',
          f'<link rel="icon" href="{p}assets/images/brand/icon-192.png" type="image/png" sizes="192x192">',
          f'<link rel="apple-touch-icon" href="{p}apple-touch-icon.png">',
          f'<link rel="manifest" href="{p}site.webmanifest">',
          f'<link rel="preload" href="{p}assets/fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>']
    for pl in page.get("preload", []):
        extra = "".join(f' {k}="{esc(v if k != "imagesrcset" else ", ".join(p + x.strip() for x in v.split(",")))}"' for k, v in pl.items() if k not in ("href", "as"))
        L.append(f'<link rel="preload" href="{p}{pl["href"]}" as="{pl["as"]}"{extra} fetchpriority="high">')
    L += ['<meta property="og:type" content="website">',
          f'<meta property="og:site_name" content="{site["name"]}">',
          f'<meta property="og:locale" content="{site["locale"]}">',
          f'<meta property="og:title" content="{title}">',
          f'<meta property="og:description" content="{desc}">',
          f'<meta property="og:url" content="{url}">',
          f'<meta property="og:image" content="{og_img}">',
          '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
          f'<meta property="og:image:alt" content="{title}">',
          '<meta name="twitter:card" content="summary_large_image">',
          f'<meta name="twitter:title" content="{title}">',
          f'<meta name="twitter:description" content="{desc}">',
          f'<meta name="twitter:image" content="{og_img}">',
          f'<link rel="stylesheet" href="{p}assets/css/base.css?v={base_v}">',
          f'<script src="{p}assets/js/site.js?v={js_v}" defer></script>']
    if "data-form=" in s:   # pages with a form load the form script (assets/js/forms.js, see docs/FORMS-AND-SECURITY.md)
        L.append(f'<script src="{p}assets/js/forms.js?v={digest(os.path.join(PUB, "assets", "js", "forms.js"))}" defer></script>')
    if not page.get("noindex"):
        L.append(f'<script type="application/ld+json">{jsonld(site, page, s)}</script>')
    return "\n".join(L)

# ───────────────────────── 404 page ─────────────────────────
NOT_FOUND_BODY = """<main id="main" class="bg-white">
    <section class="relative overflow-hidden bg-[#5298F8] text-white">
        <div class="absolute inset-0 dot-grid-white pointer-events-none" aria-hidden="true"></div>
        <div class="relative max-w-[1188px] mx-auto px-6 py-24 md:py-32 text-center">
            <p class="text-[0.7rem] font-extrabold tracking-[0.12em] text-[#F3D06F]">ERROR 404</p>
            <h1 class="mt-4 text-[40px] md:text-[56px] leading-[1.08] font-bold tracking-tight">We couldn&rsquo;t find that page</h1>
            <p class="mt-5 max-w-[560px] mx-auto text-[18px] leading-[28px] text-white/85">The page may have moved or no longer exists. These links will get you back on track.</p>
            <div class="mt-9 flex flex-wrap justify-center gap-4">
                <a href="/" class="inline-block bg-[#F3D06F] text-[#111827] text-[16px] leading-[16px] font-medium px-8 py-[14px] rounded-full transition-transform hover:-translate-y-0.5">Go to the homepage</a>
                <a href="/talk-to-us/" class="inline-block bg-white/10 border border-white/40 text-white text-[16px] leading-[16px] font-medium px-8 py-[14px] rounded-full transition-colors hover:bg-white/20">Talk to us</a>
            </div>
        </div>
    </section>
    <section class="max-w-[1188px] mx-auto px-6 py-16">
        <h2 class="text-[22px] font-semibold text-gray-900">Popular pages</h2>
        <ul class="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 text-[15px]">
            <li><a class="block rounded-2xl border border-gray-200 px-5 py-4 font-medium text-gray-800 hover:border-[#5298F8] hover:text-[#2563EB] transition-colors" href="/platform/">Platform</a></li>
            <li><a class="block rounded-2xl border border-gray-200 px-5 py-4 font-medium text-gray-800 hover:border-[#5298F8] hover:text-[#2563EB] transition-colors" href="/customers/">Customers</a></li>
            <li><a class="block rounded-2xl border border-gray-200 px-5 py-4 font-medium text-gray-800 hover:border-[#5298F8] hover:text-[#2563EB] transition-colors" href="/about-us/">About us</a></li>
            <li><a class="block rounded-2xl border border-gray-200 px-5 py-4 font-medium text-gray-800 hover:border-[#5298F8] hover:text-[#2563EB] transition-colors" href="/contact-us/">Contact us</a></li>
        </ul>
    </section>
</main>"""

def ensure_404(site):
    path = os.path.join(PUB, "404.html")
    if not os.path.exists(path):
        write(path, '<!DOCTYPE html>\n<html lang="en">\n<head>\n<!-- site:head:start -->\n<!-- site:head:end -->\n<style>.dot-grid-white{background-image:radial-gradient(circle,rgba(255,255,255,.14) 1px,transparent 1px);background-size:28px 28px;}</style>\n'
              '<!-- site:css:start -->\n<!-- site:css:end -->\n</head>\n<body class="bg-white text-gray-700">\n<!-- site:header:start -->\n<!-- site:header:end -->\n'
              + NOT_FOUND_BODY + '\n<!-- site:footer:start -->\n<!-- site:footer:end -->\n</body>\n</html>\n')
    return {"key": "notfound", "file": "404.html", "path": "404.html", "title": "Page not found | adeahub",
            "description": "The page you were looking for could not be found. Explore the adeahub digital health platform, products, customers and contact details.",
            "type": "WebPage", "noindex": True, "root_relative": True}

# ───────────────────────── embeds ─────────────────────────
EMBED_FONTS = ("<style id=\"embed-fonts\">"
               "@font-face{font-family:'Outfit';font-weight:100 900;font-display:swap;src:url(../assets/fonts/outfit-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}"
               "html,body{overflow:hidden;}"
               "@font-face{font-family:'Inter';font-weight:100 900;font-display:swap;src:url(../assets/fonts/inter-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}"
               "</style>")
def build_embeds():
    d = os.path.join(PUB, "embeds")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html"): continue
        path = os.path.join(d, f); s = read(path)
        s = re.sub(r'\s*<link[^>]*fonts\.googleapis\.com[^>]*>', "", s)
        s = re.sub(r'\s*<link rel="preconnect"[^>]*fonts\.g[^>]*>', "", s)
        s = re.sub(r'<style id="embed-fonts">.*?</style>', lambda _: EMBED_FONTS, s, flags=re.S)
        if 'id="embed-fonts"' not in s:
            s = s.replace("<title>", EMBED_FONTS + "\n<title>", 1)
        # previews are illustrations: their fake controls must not take keyboard focus
        s = re.sub(r"<button\b(?![^>]*\btype=)", '<button type="button"', s)
        s = re.sub(r"<input\b(?![^>]*\btype=)", '<input type="text"', s)
        s = re.sub(r"<(button|input|a|select|textarea)\b(?![^>]*tabindex)", r'<\1 tabindex="-1"', s)
        if 'name="robots"' not in s:
            s = s.replace("<title>", '<meta name="robots" content="noindex">\n<title>', 1)
        write(path, s)

# ───────────────────────── site files ─────────────────────────
def site_files(site, pages):
    base = site["url"].rstrip("/")
    today = datetime.date.today().isoformat()
    def lastmod(f):
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", os.path.join("public", f)], cwd=ROOT, capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", os.path.join("public", f)], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return today if (dirty or not r.stdout.strip()) else r.stdout.strip()
    urls = "".join(f"  <url>\n    <loc>{base}/{pg['path']}</loc>\n    <lastmod>{lastmod(pg['file'])}</lastmod>\n    <priority>{pg['priority']}</priority>\n  </url>\n"
                   for pg in pages if not pg.get("noindex"))
    write(os.path.join(PUB, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    write(os.path.join(PUB, "robots.txt"), "# adeahub.co: all crawlers, including search and AI answer engines, are welcome.\n"
          "User-agent: *\nAllow: /\nDisallow: /embeds/\n\n" f"Sitemap: {base}/sitemap.xml\n")
    lines = [f"# {site['name']}", "", f"> {site['description']}", "",
             "Key facts: 35M+ users on the platform, 8,500+ health facilities, 200M+ patient records, 17+ locations, 25+ years of healthcare IT heritage. Parent company: entomo.", "",
             "## Products", ""]
    for pg in pages:
        if "service" in pg: lines.append(f"- [{pg['service']['name']}]({base}/{pg['path']}): {pg['description']}")
    lines += ["", "## Company", ""]
    for pg in pages:
        if "service" not in pg and pg["path"] and not pg.get("noindex"):
            lines.append(f"- [{pg['breadcrumb']}]({base}/{pg['path']}): {pg['description']}")
    lines += ["", "## Contact", "", f"- General enquiries: {site['email']}"] + [f"- {c['contactType'].capitalize()}: {c['email']}" for c in site["contactPoints"]]
    write(os.path.join(PUB, "llms.txt"), "\n".join(lines) + "\n")
    manifest = {"name": site["name"], "short_name": site["name"], "description": site["tagline"], "start_url": "/", "display": "browser",
                "background_color": "#ffffff", "theme_color": site["themeColor"],
                "icons": [{"src": "/assets/images/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "/assets/images/brand/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    write(os.path.join(PUB, "site.webmanifest"), json.dumps(manifest, indent=2) + "\n")
    # security.txt (RFC 9116): rewritten only when missing or within 90 days of its expiry, so builds stay idempotent
    sec = os.path.join(PUB, ".well-known", "security.txt")
    if security_txt_days_left() < 90:
        expires = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00.000Z")
        write(sec, f"Contact: mailto:{site['securityContact']}\nExpires: {expires}\nPreferred-Languages: en\n"
                   f"Canonical: {base}/.well-known/security.txt\n")

def security_txt_days_left():
    sec = os.path.join(PUB, ".well-known", "security.txt")
    if not os.path.exists(sec): return -1
    m = re.search(r"^Expires: (\d{4}-\d{2}-\d{2})", read(sec), re.M)
    if not m: return -1
    return (datetime.date.fromisoformat(m.group(1)) - datetime.date.today()).days

# ───────────────────────── forms and headers ─────────────────────────
def check_forms(rel, s, schema):
    """Every <form data-form> must match src/forms.json (the Worker rejects anything else) and carry the guards."""
    for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>", s, re.S):
        attrs, body = m.group(1), m.group(2)
        im = re.search(r'data-form="([^"]+)"', attrs)
        if not im: err(f"{rel}: <form> without data-form (it would not submit anywhere)"); continue
        intent = im.group(1); spec = schema["intents"].get(intent)
        if not spec: err(f"{rel}: data-form=\"{intent}\" is not an intent in src/forms.json"); continue
        allowed = set(spec["required"]) | set(spec["optional"]) | {"hs_website", "website_consent_given"}
        controls = re.findall(r"<(input|select|textarea)\b([^>]*)>", body)
        names = {}
        for tag, a in controls:
            n = re.search(r'\bname="([^"]+)"', a)
            if n: names.setdefault(n.group(1), []).append((tag, a))
        for n in names:
            if n not in allowed: err(f"{rel}: form \"{intent}\" has field name=\"{n}\" that src/forms.json does not allow")
        for n in spec["required"]:
            if n not in names: err(f"{rel}: form \"{intent}\" is missing required field {n}")
            elif not any(re.search(r"\brequired\b", a) for _, a in names[n]): err(f"{rel}: form \"{intent}\" field {n} must be marked required")
        for n, opts in schema["options"].items():
            if n not in names: continue
            if names[n][0][0] == "select":
                sm = re.search(rf'<select\b[^>]*name="{n}"[^>]*>(.*?)</select>', body, re.S)
                vals = [html.unescape(re.search(r'value="([^"]*)"', o).group(1) if 'value="' in o else t).strip()
                        for o, t in re.findall(r"<option\b([^>]*)>([^<]*)</option>", sm.group(1)) if "disabled" not in o]
            else:
                vals = [html.unescape(re.search(r'value="([^"]*)"', a).group(1)) for _, a in names[n]]
            for v in vals:
                if v not in opts: err(f"{rel}: form \"{intent}\" offers {n}=\"{v}\", not a value in src/forms.json (HubSpot would reject it)")
        if "hs_website" not in names or 'class="hp-field"' not in body: err(f"{rel}: form \"{intent}\" lacks the honeypot (.hp-field with name=\"hs_website\")")
        if spec.get("consent") and not any(re.search(r"\brequired\b", a) and 'value="true"' in a for _, a in names.get("website_consent_given", [])):
            err(f"{rel}: form \"{intent}\" lacks the required consent checkbox (name=\"website_consent_given\" value=\"true\" required)")
        if 'class="form-turnstile"' not in body: err(f"{rel}: form \"{intent}\" lacks the Turnstile slot <div class=\"form-turnstile\">")
        if 'class="form-status' not in body: err(f"{rel}: form \"{intent}\" lacks <p class=\"form-status\" role=\"alert\" hidden>")

def check_headers():
    path = os.path.join(PUB, "_headers")
    if not os.path.exists(path): err("public/_headers is missing"); return
    s = read(path)
    for i, line in enumerate(s.splitlines(), 1):
        if len(line) > 2000: err(f"public/_headers line {i} is {len(line)} characters (Cloudflare's limit is 2,000)")
    for h in ("Content-Security-Policy", "Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy",
              "Permissions-Policy", "Cross-Origin-Opener-Policy", "Cross-Origin-Resource-Policy"):
        if h not in s: err(f"public/_headers does not set {h}")
    if "report-uri /api/csp-report" not in s: err("public/_headers: the CSP must report to /api/csp-report")

# ───────────────────────── checks ─────────────────────────
def check_page(rel, s):
    here = posixpath.dirname(rel)
    h1s = len(re.findall(r"<h1\b", s))
    if h1s != 1: err(f"{rel}: expected exactly one <h1>, found {h1s}")
    for bad in ("cdn.tailwindcss.com", "unpkg.com/lucide", "fonts.googleapis.com", "data-lucide=", "Images/"):
        if bad in s: err(f"{rel}: still references {bad}")
    for img in re.findall(r"<img\b[^>]*>", s):
        if " alt=" not in img: err(f"{rel}: <img> without alt: {img[:120]}")
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", s, flags=re.S)
    for attr, ref in re.findall(r'\b(href|src|srcset|poster)="([^"]+)"', body) + [("url", u) for u in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", body)]:
        for one in ([x.strip().split(" ")[0] for x in ref.split(",")] if attr == "srcset" else [ref]):
            if re.match(r"^(https?:|mailto:|tel:|#|data:|javascript:)", one) or not one: continue
            path = one.split("#")[0].split("?")[0]
            if rel == "404.html" and path.startswith("/"): target = path.lstrip("/")
            else: target = posixpath.normpath(posixpath.join(here, path))
            if target.endswith("/") or target in (".", "") or os.path.isdir(os.path.join(PUB, target)): target = posixpath.join(target, "index.html")
            if not os.path.exists(os.path.join(PUB, target)): err(f"{rel}: broken link/asset {one}")
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(m)
        except Exception as e: err(f"{rel}: invalid JSON-LD ({e})")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    cfg = json.load(open(os.path.join(ROOT, "src", "site.json")))
    site, pages = cfg["site"], list(cfg["pages"])
    pages.append(ensure_404(site))
    for pg in pages:
        if len(pg["title"]) > 60: warn(f"{pg['file']}: title is {len(pg['title'])} chars (keep <= 60)")
        if not 110 <= len(pg["description"]) <= 160: warn(f"{pg['file']}: description is {len(pg['description'])} chars (aim for 120-160)")

    if not a.check:
        js_v = digest(os.path.join(PUB, "assets", "js", "site.js"))
        base_v = digest(os.path.join(PUB, "assets", "css", "base.css"))
        def render(pg, css_v):
            path = os.path.join(PUB, pg["file"]); s = read(path)
            p = "/" if pg.get("root_relative") else "../" * pg["file"].count("/")
            s = fill(s, "header", chrome.header(p, CURRENT_NAV.get(pg["key"])))
            s = fill(s, "footer", chrome.footer(p))
            s = inline_icons(s)
            s = fill(s, "head", head_html(site, pg, p, s, js_v, base_v))
            s = fill(s, "css", f'<link rel="stylesheet" href="{p}assets/css/site.css?v={css_v}">')
            write(path, s)
        for pg in pages: render(pg, "pending")      # write markup first so Tailwind sees every class
        css_v = digest(build_css())
        for pg in pages: render(pg, css_v)
        build_embeds()
        site_files(site, pages)

    schema = json.load(open(os.path.join(ROOT, "src", "forms.json")))
    for pg in pages:
        s = read(os.path.join(PUB, pg["file"]))
        check_page(pg["file"], s)
        check_forms(pg["file"], s, schema)
        if not os.path.exists(os.path.join(PUB, "assets", "images", "social", pg["key"] + ".jpg")):
            warn(f"{pg['file']}: no social card (run python3 tools/social_cards.py)")
    for intent, spec in schema["intents"].items():
        if 'data-form="' + intent + '"' not in read(os.path.join(PUB, spec["page"])): err(f"src/forms.json: intent {intent} has no form on {spec['page']}")
    check_headers()
    days = security_txt_days_left()
    if days < 0: err("public/.well-known/security.txt is missing or expired (run python3 tools/build.py)")
    elif days < 60: warn(f"public/.well-known/security.txt expires in {days} days (run python3 tools/build.py)")
    for f in sorted(os.listdir(os.path.join(PUB, "embeds"))):
        if f.endswith(".html") and "fonts.googleapis.com" in read(os.path.join(PUB, "embeds", f)): err(f"embeds/{f}: still loads Google Fonts")
    for w in warnings: print("warning:", w)
    for e in errors: print("ERROR:", e)
    print(f"{'checked' if a.check else 'built'} {len(pages)} pages: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
