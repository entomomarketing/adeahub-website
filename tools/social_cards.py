#!/usr/bin/env python3
"""Generate the 1200x630 social sharing cards (Open Graph / LinkedIn / X) for every page.

    python3 tools/social_cards.py

Writes public/assets/images/social/<page key>.jpg, which tools/build.py references in each page's
og:image / twitter:image tags. Each card uses the page's own <h1> as its headline, in the site's
design (brand blue, dot grid, floating blobs, Outfit). Needs Google Chrome (headless screenshot) and
Pillow (`pip3 install pillow`) for the JPEG conversion. Re-run after changing a page headline.
"""
import html, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
OUT = os.path.join(PUB, "assets", "images", "social")
CHROME = next((c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome") or "",
                           shutil.which("chromium") or "", shutil.which("chrome") or ""] if c and os.path.exists(c)), None)

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Outfit;font-weight:100 900;src:url('{fonts}/outfit-latin.woff2') format('woff2');}}
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;overflow:hidden;font-family:Outfit,sans-serif;background:#5298F8;color:#fff;position:relative}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.16) 1.4px,transparent 1.4px);background-size:28px 28px}}
.blob1{{position:absolute;left:-120px;top:-140px;width:520px;height:520px;border-radius:50%;background:rgba(255,255,255,.12);filter:blur(60px)}}
.blob2{{position:absolute;right:-140px;bottom:-220px;width:460px;height:460px;border-radius:50%;background:rgba(243,208,111,.2);filter:blur(80px)}}
.ring{{position:absolute;border-radius:50%;border:2px solid rgba(255,255,255,.18)}}
.r1{{right:-150px;top:-150px;width:520px;height:520px}} .r2{{right:-70px;top:-70px;width:360px;height:360px;border-color:rgba(255,255,255,.12)}}
.wrap{{position:absolute;inset:64px 72px;display:flex;flex-direction:column}}
.logo{{align-self:flex-start;background:#fff;border-radius:999px;padding:14px 26px 14px 22px;box-shadow:0 10px 30px rgba(17,24,39,.15)}}
.logo img{{height:40px;display:block}}
.eyebrow{{margin-top:auto;display:flex;align-items:center;gap:12px;font-size:22px;font-weight:800;letter-spacing:.12em;color:#F3D06F}}
.eyebrow:before{{content:'';width:34px;height:3px;border-radius:3px;background:#F3D06F}}
h1{{margin-top:18px;font-weight:700;letter-spacing:-.02em;line-height:1.06;font-size:{size}px;max-width:1000px;text-wrap:balance}}
.foot{{margin-top:34px;display:flex;justify-content:space-between;align-items:center;font-size:24px;color:rgba(255,255,255,.92)}}
.foot b{{font-weight:600}}
</style></head><body><div class="dots"></div><div class="blob1"></div><div class="blob2"></div><div class="ring r1"></div><div class="ring r2"></div>
<div class="wrap"><div class="logo"><img src="{logo}" alt=""></div><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>
<div class="foot"><span>Powering modern healthcare</span><b>adeahub.co</b></div></div></body></html>"""

def h1_text(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", s, re.S)
    t = re.sub(r"<br\s*/?>", " ", m.group(1))
    t = re.sub(r"<span[^>]*sr-only[^>]*>.*?</span>", "", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()

def main():
    if not CHROME: sys.exit("Google Chrome not found")
    from PIL import Image
    cfg = json.load(open(os.path.join(ROOT, "src", "site.json")))
    pages = cfg["pages"] + [{"key": "notfound", "file": "404.html", "breadcrumb": "adeahub"}]
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for pg in pages:
        title = h1_text(os.path.join(PUB, pg["file"]))
        name = pg.get("service", {}).get("name") or pg.get("breadcrumb") or "adeahub"
        if pg["key"] == "home": name = "adeahub"
        # product pages lead their h1 with the product name; keep the claim as the headline
        for prefix in ("WorkWise by entomo ", name + " "):
            if title.startswith(prefix) and len(title) > len(prefix) + 12: title = title[len(prefix):]; break
        size = 76 if len(title) <= 48 else 64 if len(title) <= 80 else 54
        doc = TEMPLATE.format(fonts="file://" + os.path.join(PUB, "assets", "fonts"), logo="file://" + os.path.join(PUB, "assets", "images", "brand", "adeahub-logo.png"),
                              eyebrow=html.escape(name), title=html.escape(title), size=size)
        src = os.path.join(tmp, pg["key"] + ".html"); png = os.path.join(tmp, pg["key"] + ".png")
        open(src, "w", encoding="utf-8").write(doc)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--allow-file-access-from-files", "--virtual-time-budget=1500", "--window-size=1200,630",
                        f"--screenshot={png}", "file://" + src], check=True, capture_output=True)
        Image.open(png).convert("RGB").crop((0, 0, 1200, 630)).save(os.path.join(OUT, pg["key"] + ".jpg"), quality=86, optimize=True, progressive=True)
        print(f"{pg['key']:10} {os.path.getsize(os.path.join(OUT, pg['key'] + '.jpg')) // 1024:4} KB  {title}")
    shutil.rmtree(tmp)

if __name__ == "__main__":
    main()
