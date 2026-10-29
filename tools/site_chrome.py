#!/usr/bin/env python3
"""Shared site header (nav + mega-menus + mobile menu), footer and <head> extras for every page.

Edit the header/footer HERE, then run from the repo root:
    python3 tools/site_chrome.py            # rewrite all pages
    python3 tools/site_chrome.py --dry-run  # list pages it would touch
It replaces each page's site <nav id="main-nav">…</nav> and <footer>…</footer>, and refreshes the
scoped <style id="site-chrome"> and the <!-- live-head --> block (favicon + canonical/Open Graph tags)
in <head>. Design values were measured on https://adeahub.co at 1440px on 2026-10-29. Idempotent.
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry-run" in sys.argv

CSS = r"""
<style id="site-chrome">
/* ── Site header / mega-menus / footer — values measured on adeahub.co (2026-10-29) ── */
html,body{overflow-x:clip;} /* stop slide-in animations and decorative overhangs from causing sideways scroll on phones */
.snav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.95);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 4px 10px rgba(0,0,0,.08);font-family:'Outfit',sans-serif;}
.snav-inner{max-width:1188px;margin:0 auto;padding:0 24px;height:84px;display:flex;align-items:center;justify-content:space-between;}
.snav-brand{display:flex;flex-direction:column;align-items:flex-start;text-decoration:none;flex-shrink:0;}
.snav-brand img{height:39px;width:auto;display:block;}
.snav-tag{display:block;font-size:13px;line-height:13px;font-weight:300;color:#6B7280;padding-left:8px;margin-top:2px;}
.snav-menu{display:none;align-items:center;}
@media (min-width:768px){.snav-menu{display:flex;}}
.snav-links{display:flex;align-items:center;list-style:none;margin:0;padding:0;}
.snav-links>li{position:relative;}
.snav-link{display:flex;align-items:center;gap:6px;padding:0 15px;font-size:14px;line-height:21px;font-weight:500;color:#4B5563;text-decoration:none;background:none;border:0;cursor:pointer;font-family:inherit;transition:color .2s;}
.snav-links>li:hover>.snav-link,.snav-link:focus-visible,.snav-link.is-current{color:#5298F8;}
.snav-link svg{width:11px;height:11px;margin-right:6px;stroke:currentColor;fill:none;stroke-width:2;}
.snav-cta{margin-left:20px;display:inline-block;background:#F3D06F;color:#111827;font-size:16px;line-height:16px;font-weight:500;padding:14px 32px;border-radius:9999px;text-decoration:none;white-space:nowrap;transition:transform .3s;}
.snav-cta{position:relative;overflow:hidden;}
.snav-cta::after{content:'';position:absolute;top:0;left:-100%;width:55%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.22),transparent);}
.snav-cta:hover{transform:translateY(-8px);}
.snav-cta:hover::after{left:160%;transition:left .55s ease;}
.snav-burger{display:block;color:#4B5563;padding:4px;background:none;border:0;cursor:pointer;}
@media (min-width:768px){.snav-burger{display:none;}}
/* mega panels */
.snav-dd .snav-panel{position:absolute;top:100%;padding-top:16px;display:none;z-index:60;}
.snav-dd:hover .snav-panel,.snav-dd:focus-within .snav-panel{display:block;animation:snavDrop .18s ease forwards;}
@keyframes snavDrop{from{opacity:0;transform:translateY(-6px);}to{opacity:1;transform:translateY(0);}}
.snav-dd-products .snav-panel{left:-150px;}
.snav-dd-resources .snav-panel{left:0;}
.snav-card{background:#fff;border-radius:16px;box-shadow:0 0 28px rgba(0,0,0,.14);overflow:hidden;}
.snav-dd-products .snav-card{width:750px;}
.snav-dd-resources .snav-card{width:500px;}
.snav-card-head{background:linear-gradient(135deg,#f0f6ff,#eef4ff);border-bottom:1px solid #dbeafe;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;line-height:18px;color:#5298F8;}
.snav-label{display:inline-flex;align-items:center;gap:6px;font-size:.65rem;font-weight:800;letter-spacing:.12em;}
.snav-label::before{content:'';display:inline-block;width:18px;height:2px;background:#5298F8;border-radius:2px;}
.snav-card-head a{color:#5298F8;text-decoration:none;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:4px;}
.snav-chev{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.5;}
.snav-card-body{padding:16px 16px 16px 8px;}
.snav-grid{display:grid;grid-template-columns:1fr 1fr;}
.snav-group{border-bottom:1px solid #F1F1F1;margin-bottom:8px;}
.snav-group:last-child{border-bottom:0;margin-bottom:0;}
.snav-item{display:flex;align-items:flex-start;gap:13px;padding:10px 12px;border-radius:12px;text-decoration:none;transition:background .15s;}
.snav-item:hover{background:#f0f6ff;}
.snav-ico{flex-shrink:0;width:40px;height:40px;border-radius:10px;background:#EFF6FF;color:#5298F8;display:flex;align-items:center;justify-content:center;transition:background .15s;}
.snav-item:hover .snav-ico{background:#dbeafe;}
.snav-ico svg{width:18px;height:18px;stroke:#5298F8;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;}
.snav-title{font-size:14px;line-height:18px;font-weight:600;color:#000;margin:0 0 5px;}
.snav-title span{color:#5298F8;}
.snav-text{font-size:12px;line-height:21px;color:#7A7A7A;margin:0;}
.snav-text strong{font-weight:700;display:block;}
.snav-item:hover .snav-title{color:#5298F8;}
.snav-card-foot{background:#FAFAFA;border-top:1px solid #fff;padding:16px;display:flex;justify-content:flex-end;}
.snav-card-foot a{background:#EFF6FF;color:#5298F8;font-size:12px;line-height:18px;font-weight:600;padding:6px 14px;border-radius:20px;text-decoration:none;display:inline-flex;align-items:center;gap:4px;}
/* footer */
.sfoot{background:#fff;font-family:'Outfit',sans-serif;}
.sfoot-inner{max-width:1188px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr;gap:40px;}
@media (min-width:768px){.sfoot-inner{grid-template-columns:1fr 1fr;}}
@media (min-width:1024px){.sfoot-inner{grid-template-columns:456px 228px 228px 228px;gap:0;}}
.sfoot-logo img{height:36px;width:auto;display:block;}
.sfoot-tag{margin:20px 0 0;max-width:320px;font-size:14px;line-height:19px;color:#9E9E9E;}
.sfoot-social{margin-top:20px;display:flex;gap:10px;}
.sfoot-social a{width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:8px;transition:background .2s,border-color .2s;}
.sfoot-social a:hover{background:#dbeafe;border-color:#bfdbfe;}
.sfoot-social svg{width:15px;height:15px;}
.sfoot-h{margin:0 0 16px;font-size:.65rem;line-height:17px;font-weight:800;letter-spacing:.12em;color:#5298F8;}
.sfoot-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;}
.sfoot-list a{font-size:14px;line-height:21px;color:#54595F;text-decoration:none;transition:color .2s;display:block;width:fit-content;}
.sfoot-list a.sfoot-mail{display:flex;align-items:center;gap:5px;}
.sfoot-list a:hover{color:#5298F8;}
.sfoot-list b{color:#5298F8;font-weight:700;}
.sfoot-list svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;}
.sfoot-btn{margin-top:16px;display:inline-flex;align-items:center;gap:8px;background:#F3D06F;color:#000;font-size:12px;line-height:19px;font-weight:700;padding:4px 16px;border-radius:32px;text-decoration:none;}
.sfoot-btn svg{width:12px;height:12px;stroke:#000;fill:none;stroke-width:2.5;}
.sfoot-copy{border-top:1px solid #F1F1F1;}
.sfoot-copy p{max-width:1188px;margin:0 auto;padding:16px 24px;text-align:center;font-size:12px;line-height:17px;color:#9E9E9E;}
</style>
"""

ICON = {
    "phone": '<svg viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>',
    "building": '<svg viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/></svg>',
    "copy": '<svg viewBox="0 0 24 24"><rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    "chart": '<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M8 17v-5M13 17V8M18 17v-9"/></svg>',
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "user": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/></svg>',
}
CHEV = '<svg viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>'
CHEVR = '<svg class="snav-chev" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>'

def item(href, icon, title_html, tag, desc=None):
    txt = f'<strong>{tag}</strong>' + (desc if desc else "")
    return (f'<a href="{href}" class="snav-item"><span class="snav-ico">{ICON[icon]}</span>'
            f'<span><p class="snav-title">{title_html}</p><p class="snav-text">{txt}</p></span></a>')

def nav(current):
    def cur(name): return " is-current" if current == name else ""
    products = (
        '<div class="snav-panel"><div class="snav-card">'
        '<div class="snav-card-head"><span class="snav-label">adeahub products</span><a href="adeahub_platform.html">View platform overview ' + CHEVR + '</a></div>'
        '<div class="snav-card-body">'
        '<div class="snav-group snav-grid">'
        + item("adeahub_engage.html", "phone", "<span>AH</span> Engage", "Digital front door for patients", "Appointments, health records &amp; care journeys")
        + item("adeahub_care.html", "building", "<span>AH</span> Care", "Health information system", "25+ clinical &amp; admin modules, multi-site")
        + '</div><div class="snav-group snav-grid">'
        + item("adeahub_connect.html", "copy", "<span>AH</span> Connect", "Interoperability &amp; health data exchange", "FHIR server, integration engine &amp; API gateway")
        + item("adeahub_insights.html", "chart", "<span>AH</span> Insights", "Healthcare intelligence &amp; analytics", "Population health, real-time analytics &amp; AI/ML")
        + item("adeahub_outbreak.html", "shield", "<span>AH</span> Outbreak Management", "Manage disease outbreaks", "Detection, tracing, monitoring &amp; containment")
        + '</div><div class="snav-group">'
        + item("workwise.html", "user", "<span>Work</span>Wise", "Healthcare workforce experience platform", "Performance, learning &amp; workforce intelligence for healthcare teams")
        + '</div></div>'
        '<div class="snav-card-foot"><a href="request_demo.html">Request a demo ' + CHEVR + '</a></div>'
        '</div></div>')
    resources = (
        '<div class="snav-panel"><div class="snav-card">'
        '<div class="snav-card-head"><span class="snav-label">Resources</span></div>'
        '<div class="snav-card-body">'
        '<div class="snav-group">' + item("newsroom.html", "phone", "Newsroom", "Press releases &amp; company announcements") + '</div>'
        '<div class="snav-group">' + item("customers.html", "copy", "Customers", "Case studies &amp; client outcomes") + '</div>'
        '<div class="snav-group">' + item("Blogs.html", "user", "Blog", "Insights, perspectives &amp; best practices") + '</div>'
        '</div>'
        '<div class="snav-card-foot"><a href="request_demo.html">Request a demo ' + CHEVR + '</a></div>'
        '</div></div>')
    A = 'class="block py-2.5 px-3 rounded-lg text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors font-medium text-sm"'
    def m(h, t): return f'        <a href="{h}" {A}>{t}</a>\n'
    D = '        <div class="my-2 border-t border-gray-100"></div>\n'
    mobile = ('    <div id="mobile-menu" class="hidden md:hidden bg-white border-t border-gray-100 px-5 py-4">\n'
              '        <p class="text-[0.65rem] font-bold uppercase tracking-widest text-gray-400 pb-2">Products</p>\n'
              + m("adeahub_engage.html", "AH Engage") + m("adeahub_care.html", "AH Care") + m("adeahub_connect.html", "AH Connect")
              + m("adeahub_outbreak.html", "AH Outbreak Management") + m("adeahub_insights.html", "AH Insights") + m("workwise.html", "WorkWise")
              + D + m("adeahub_platform.html", "Platform") + D
              + '        <p class="text-[0.65rem] font-bold uppercase tracking-widest text-gray-400 pt-1 pb-2">Resources</p>\n'
              + m("newsroom.html", "Newsroom") + m("customers.html", "Customers") + m("Blogs.html", "Blog")
              + D + m("about_us.html", "About Us") + D + m("contact_us.html", "Contact Us")
              + '        <div class="pt-3 pb-1">\n'
              '            <a href="contact_us.html" class="block text-gray-900 text-center px-5 py-3 rounded-full hover:opacity-90 transition-colors font-semibold text-sm" style="background:#F3D06F;">Talk to us</a>\n'
              '        </div>\n    </div>\n')
    return (
        '<nav id="main-nav" class="snav">\n'
        '    <div class="snav-inner">\n'
        '        <a href="index.html" class="snav-brand"><img src="Images/AdeaHub-Logo-Default.webp" alt="adeahub logo"><span class="snav-tag">Powering modern healthcare</span></a>\n'
        '        <div class="snav-menu">\n'
        '            <ul class="snav-links">\n'
        f'                <li><a href="adeahub_platform.html" class="snav-link{cur("platform")}">Platform</a></li>\n'
        f'                <li class="snav-dd snav-dd-products"><button type="button" class="snav-link" aria-haspopup="true">Products {CHEV}</button>{products}</li>\n'
        f'                <li class="snav-dd snav-dd-resources"><button type="button" class="snav-link" aria-haspopup="true">Resources {CHEV}</button>{resources}</li>\n'
        f'                <li><a href="about_us.html" class="snav-link{cur("about")}">About Us</a></li>\n'
        f'                <li><a href="contact_us.html" class="snav-link{cur("contact")}">Contact Us</a></li>\n'
        '            </ul>\n'
        '            <a href="request_demo.html" class="snav-cta">Talk To Us</a>\n'
        '        </div>\n'
        '        <button id="mobile-menu-btn" class="snav-burger" aria-label="Toggle menu">\n'
        '            <svg id="hamburger-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>\n'
        '            <svg id="close-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>\n'
        '        </button>\n'
        '    </div>\n'
        + mobile +
        '</nav>')

LINKEDIN = '<svg viewBox="0 0 448 512"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/></svg>'
ENVELOPE = '<svg viewBox="0 0 512 512"><path d="M464 64H48C21.49 64 0 85.49 0 112v288c0 26.51 21.49 48 48 48h416c26.51 0 48-21.49 48-48V112c0-26.51-21.49-48-48-48zm0 48v40.805c-22.422 18.259-58.168 46.651-134.587 106.49-16.841 13.247-50.201 45.072-73.413 44.701-23.208.375-56.579-31.459-73.413-44.701C106.18 199.465 70.425 171.067 48 152.805V112h416zM48 400V214.398c22.914 18.251 55.409 43.862 104.938 82.646 21.857 17.205 60.134 55.186 103.062 54.955 42.717.231 80.509-37.199 103.053-54.947 49.528-38.783 82.032-64.401 104.947-82.653V400H48z"/></svg>'
MAIL_OUTLINE = '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>'
GH_LINKEDIN = '<svg viewBox="0 0 24 24" fill="#4b5563"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.125 2.062 2.062 0 0 1 0 4.125zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
GH_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>'
ARROW = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def footer():
    def li(h, inner): return f'                    <li><a href="{h}">{inner}</a></li>\n'
    return (
        '<footer class="sfoot">\n'
        '    <div class="sfoot-inner">\n'
        '        <div>\n'
        '            <a href="index.html" class="sfoot-logo"><img src="Images/adeahub-logo-footer.webp" alt="adeahub"></a>\n'
        '            <p class="sfoot-tag">Modern software to deliver personalised healthcare at scale.</p>\n'
        f'            <div class="sfoot-social"><a href="https://www.linkedin.com/company/adeahub/" target="_blank" rel="noopener" aria-label="LinkedIn">{GH_LINKEDIN}</a><a href="mailto:hello@adeahub.co" aria-label="Email">{GH_MAIL}</a></div>\n'
        '        </div>\n'
        '        <div>\n'
        '            <p class="sfoot-h">Products</p>\n'
        '            <ul class="sfoot-list">\n'
        + li("adeahub_engage.html", "<b>AH</b> Engage") + li("adeahub_care.html", "<b>AH</b> Care") + li("adeahub_connect.html", "<b>AH</b> Connect")
        + li("adeahub_outbreak.html", "<b>AH</b> Outbreak Management") + li("adeahub_insights.html", "<b>AH</b> Insights") + li("workwise.html", "<b>Work</b>Wise") +
        '            </ul>\n'
        '        </div>\n'
        '        <div>\n'
        '            <p class="sfoot-h">Company</p>\n'
        '            <ul class="sfoot-list">\n'
        + li("adeahub_platform.html", "Platform") + li("about_us.html", "About Us") + li("customers.html", "Customers")
        + li("newsroom.html", "Newsroom") + li("Blogs.html", "Blog") + li("contact_us.html", "Contact Us") +
        '            </ul>\n'
        '        </div>\n'
        '        <div>\n'
        '            <p class="sfoot-h">Get in touch</p>\n'
        '            <ul class="sfoot-list">\n'
        f'                <li><a href="mailto:hello@adeahub.co" target="_blank" class="sfoot-mail">{MAIL_OUTLINE}hello@adeahub.co</a></li>\n'
        '            </ul>\n'
        f'            <a href="request_demo.html" class="sfoot-btn">Request a demo {ARROW}</a>\n'
        '        </div>\n'
        '    </div>\n'
        '    <div class="sfoot-copy"><p>&copy; 2026 adeahub. All rights reserved.</p></div>\n'
        '</footer>')


def head_block(name, page_html=""):
    """Favicon links plus the page's existing canonical/Open Graph tags (copied from adeahub.co)."""
    keep = []
    m = re.search(r'<!-- live-head:start.*?-->(.*?)<!-- live-head:end -->', page_html, re.S)
    if m:
        keep = [l.strip() for l in m.group(1).strip().splitlines()
                if l.strip() and 'Images/favicon/' not in l]
    lines = ['<!-- live-head:start (favicon + canonical/social tags as on adeahub.co) -->',
             '<link rel="icon" href="Images/favicon/cropped-Entomo-Box-Logos-scaled-1-32x32.png" sizes="32x32">',
             '<link rel="icon" href="Images/favicon/cropped-Entomo-Box-Logos-scaled-1-192x192.png" sizes="192x192">',
             '<link rel="apple-touch-icon" href="Images/favicon/cropped-Entomo-Box-Logos-scaled-1-180x180.png">',
             '<meta name="msapplication-TileImage" content="Images/favicon/cropped-Entomo-Box-Logos-scaled-1-270x270.png">'] + keep
    lines.append('<!-- live-head:end -->')
    return "\n".join(lines)

CURRENT = {"adeahub_platform.html": "platform", "about_us.html": "about", "contact_us.html": "contact"}

def site_nav_span(s):
    for m in re.finditer(r'<nav\b[^>]*>', s):
        tag = m.group(0)
        if 'id="main-nav"' in tag or re.search(r'class="[^"]*\bsticky\b', tag) or 'class="snav"' in tag:
            # find matching </nav> accounting for nested <nav>
            depth, i = 0, m.start()
            for t in re.finditer(r'<nav\b|</nav>', s[m.start():]):
                depth += 1 if t.group(0) == "<nav" else -1
                if depth == 0:
                    return m.start(), m.start() + t.end()
    return None

def main():
    done = []
    for p in sorted(glob.glob(os.path.join(REPO, "*.html"))):
        name = os.path.basename(p)
        s = open(p, encoding="utf-8").read()
        sp = site_nav_span(s)
        if not sp or "<footer" not in s:
            continue
        s = s[:sp[0]] + nav(CURRENT.get(name)) + s[sp[1]:]
        fi = s.find("<footer"); fe = s.find("</footer>", fi) + len("</footer>")
        s = s[:fi] + footer() + s[fe:]
        hb = head_block(name, s)
        s = re.sub(r'\n?<style id="site-chrome">.*?</style>\n?', "\n", s, flags=re.S)
        s = re.sub(r'\n?<!-- live-head:start.*?<!-- live-head:end -->\n?', "\n", s, flags=re.S)
        s = s.replace("</head>", hb + "\n" + CSS.strip() + "\n</head>", 1)
        if not DRY:
            open(p, "w", encoding="utf-8").write(s)
        done.append(name)
    print(("would update" if DRY else "updated"), len(done), "pages:", ", ".join(done))

if __name__ == "__main__":
    main()
