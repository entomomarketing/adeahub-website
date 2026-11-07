# adeahub.co website

The marketing website for **adeahub**, the digital health platform. It is a static site: plain HTML pages,
one compiled stylesheet, one small script, and optimised images. There is no framework and nothing to
install to view it.

## Folder structure

```
adeahub-website/
├── public/                     ← the website. Deploy THIS folder, nothing else.
│   ├── index.html              /                       (home)
│   ├── platform/index.html     /platform/
│   ├── ah-engage/index.html    /ah-engage/
│   ├── ah-care/ …              /ah-care/, /ah-connect/, /ah-insights/, /ah-outbreak-management/, /workwise/
│   ├── about-us/ …             /about-us/, /customers/, /newsroom/, /blogs/, /contact-us/, /talk-to-us/
│   ├── 404.html                "page not found" page (served by the host for unknown URLs)
│   ├── embeds/                 animated product previews loaded in <iframe>s (not indexed)
│   ├── assets/
│   │   ├── css/site.css        compiled Tailwind + header/footer + polish (generated, do not edit)
│   │   ├── css/base.css        shared design-system rules (scroll reveal, CTA glow, section labels …)
│   │   ├── js/site.js          shared behaviour (menus, scroll reveal, counters, card tilt)
│   │   ├── fonts/              self-hosted Outfit + Inter (WOFF2, with OFL licences)
│   │   ├── images/             brand/ home/ hospitals/ logos/{clients,hospitals}/ team/ flags/ icons/ blog/ about/ social/
│   │   └── downloads/          company profile PDF, media kit ZIP
│   ├── robots.txt, sitemap.xml, llms.txt, site.webmanifest     (generated)
│   └── favicon.ico, apple-touch-icon.png
├── src/
│   ├── site.json               page titles, descriptions, structured data facts  ← SEO lives here
│   └── css/site.css            stylesheet source (Tailwind entry)
├── tools/
│   ├── build.py                one command that regenerates everything and checks the site
│   ├── chrome.py               the shared header and footer markup
│   ├── social_cards.py         regenerates the 1200×630 social sharing images
│   └── icons/                  cached Lucide icons (SVG)
├── tailwind.config.js          brand colours and fonts for Tailwind
├── docs/                       background notes (e.g. the March 2026 repositioning changelog)
└── design/                     design prototypes; not part of the website
```

URLs match the live site (adeahub.co) exactly, so the site can replace it without broken links or lost
search rankings. Each page is a folder with an `index.html`, which gives clean addresses like `/platform/`.

## Previewing locally

```sh
python3 -m http.server 8765 --directory public
```

then open <http://127.0.0.1:8765/>. Links are relative, so the site also works from a sub-folder
(for example a GitHub Pages preview); only the 404 page assumes it is served from the domain root.

## Editing

- **Page content**: edit the page's `index.html` in `public/` directly. Use Tailwind classes as before.
- **Titles, descriptions, social text, structured data**: edit `src/site.json`, then run the build.
- **Header or footer**: edit `tools/chrome.py`, then run the build. Never edit the header/footer inside a page.
- **Shared styles**: header/footer and polish in `src/css/site.css`; reusable design-system rules in `public/assets/css/base.css`.
- **Icons**: write `<i data-lucide="icon-name" class="w-5 h-5"></i>` (names from <https://lucide.dev/icons>); the build turns it into an inline SVG.
- **Images**: add WebP files (see "Images" below) under the matching `public/assets/images/` folder and always set `alt`, `width` and `height`.

After any change, run:

```sh
python3 tools/build.py
```

It rewrites the generated parts of every page (head tags, header, footer, icons), compiles the CSS with
the pinned Tailwind CLI (downloaded and checksum-verified on first run, no npm needed), regenerates the
sitemap, robots.txt, llms.txt and manifest, and checks every page for broken links and images, missing
alt text, heading problems and invalid structured data. It exits with an error if anything is broken.

If a page headline changes, also run `python3 tools/social_cards.py` (needs Google Chrome and
`pip3 install pillow`) to refresh its social sharing image.

## Images

- Use WebP, sized to about twice the largest size the image is shown at (logos ~120–300 px wide, card photos 1000 px, portraits 700 px).
- Encode with `cwebp -q 78 -m 6 -sharp_yuv in.png -o out.webp` (photos) or `-q 90 -alpha_q 100` (logos).
- Name files in lowercase-with-dashes after what they show, e.g. `hospitals/siriraj-hospital.webp`.
- Images below the first screen get `loading="lazy" decoding="async"`; never lazy-load the hero image.

## Deploying

Upload the contents of `public/` to any static host (Cloudflare Pages, Netlify, Vercel, S3/CloudFront,
Nginx, Apache). Configure the host to:

1. serve `404.html` for unknown URLs, with status 404;
2. compress text files (Brotli or gzip — most hosts do this automatically);
3. send these cache headers:
   - `*.html`: `Cache-Control: no-cache`
   - `assets/css/*`, `assets/js/*` (URLs carry a `?v=` content hash): `Cache-Control: public, max-age=31536000, immutable`
   - `assets/fonts/*`: `public, max-age=31536000, immutable`
   - `assets/images/*`, `assets/downloads/*`: `public, max-age=2592000` (30 days; rename a file to update it immediately)
4. send basic security headers: `Strict-Transport-Security: max-age=31536000; includeSubDomains`,
   `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`,
   `X-Frame-Options: SAMEORIGIN`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.

The canonical URLs, sitemap and social tags all point at `https://adeahub.co`; change `site.url` in
`src/site.json` if the site is ever served from another domain.

## Quality bar

Every page should keep: one `<h1>`, no broken links, no console errors, no sideways scrolling at 390 px,
WCAG 2.2 AA colour contrast (brand blue `#5298F8` is for fills and large shapes; use `text-adeahub-ink`
for small blue text and `text-adeahub-heading` for large blue headings), and Lighthouse scores in the
high 90s. GitHub Actions runs `python3 tools/build.py --check` on every push and pull request
(`.github/workflows/check-site.yml`). `CLAUDE.md` has the detailed rules used when editing with Claude Code.
