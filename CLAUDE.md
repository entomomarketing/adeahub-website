# CLAUDE.md

Guidance for Claude Code when working in this repository. `README.md` covers the same ground for people.

## Project overview

The **adeahub** marketing website: a static site (HTML pages, one compiled Tailwind stylesheet, one small
shared script, optimised images). No framework and no npm. `public/` is both the source you edit and the
folder that gets deployed; `python3 tools/build.py` regenerates the shared parts in place and checks the site.

Preview: `python3 -m http.server 8765 --directory public`, then open http://127.0.0.1:8765/.
Links are relative (`../platform/`), so pages need a web server; opening them via `file://` won't resolve folder URLs.

## Repository layout

| Path | What it is |
|---|---|
| `public/<slug>/index.html` | one folder per page; URLs match adeahub.co exactly (table below) |
| `public/404.html` | not-found page (root-relative links because it is served at any depth) |
| `public/embeds/ah-*-animated.html` | animated product previews loaded by `<iframe>` (homepage "One platform", AH Connect hero, AH Outbreak hero). `noindex`; don't edit them for a single page |
| `public/assets/css/site.css` | **generated** by the build from `src/css/site.css` (Tailwind + header/footer + polish). Never edit |
| `public/assets/css/base.css` | shared design-system rules: type roles (`.h-section`, `.h-cta`, `.t-label`, `.tag-chip`), surfaces (`.card`, `.feature`, `.stat-row`/`.stat`), reveal, btn-glow/shimmer, blobs, card hovers. Hand-edited. Linked *before* page `<style>`s |
| `public/assets/js/site.js` | shared behaviour: header scroll state, dropdowns (click/Escape), mobile menu, scroll reveal, count-up, solution-card tilt |
| `public/assets/images/` | `brand/ home/ hospitals/ logos/clients/ logos/hospitals/ team/ flags/ blog/ about/ social/` |
| `public/assets/fonts/` | self-hosted Outfit (site) and Inter (only inside mock-ups), WOFF2 + OFL licences |
| `public/assets/downloads/` | company profile PDF, media kit ZIP |
| `public/robots.txt, sitemap.xml, llms.txt, site.webmanifest` | **generated** by the build |
| `src/site.json` | site facts + per-page title, description, schema type, social card. The single source of SEO metadata |
| `src/css/site.css` | stylesheet source: fonts, header/footer CSS, Tailwind directives, polish layer |
| `wrangler.jsonc` | Cloudflare Worker config (see Staging and production) |
| `tools/build.py` | the build (see below) |
| `tools/chrome.py` | header + footer markup |
| `tools/social_cards.py` | regenerates `assets/images/social/*.jpg` (needs Chrome + Pillow) |
| `tools/icons/` | cached Lucide SVGs used by the build; `tools/.bin/` (gitignored) holds the pinned Tailwind CLI |
| `docs/` | background notes: `2026-03-repositioning-changelog.md` explains copy/naming decisions — read it before changing them |
| `design/` | prototypes, not deployed |

Live URL → repo file: `/` → `public/index.html`; every other live URL `/<slug>/` → `public/<slug>/index.html`
(`platform`, `ah-engage`, `ah-care`, `ah-connect`, `ah-insights`, `ah-outbreak-management`, `workwise`,
`about-us`, `customers`, `newsroom`, `blogs`, `contact-us`, `talk-to-us`).

## The build

```sh
python3 tools/build.py          # regenerate + check (exit 1 on any error)
python3 tools/build.py --check  # check only
```

It rewrites only the marked regions of each page and is idempotent:

- `<!-- site:head:start/end -->` meta, title, description, canonical, robots, Open Graph/Twitter, icons, font preload, `base.css`, `site.js`, JSON-LD — from `src/site.json`
- `<!-- site:css:start/end -->` the `site.css` link, deliberately placed **after** the page's own `<style>` blocks so Tailwind utilities override page CSS exactly as the old in-browser Tailwind CDN did. Page styles that used to sit in `<body>` now sit right after this marker
- `<!-- site:header:start/end -->` and `<!-- site:footer:start/end -->` from `tools/chrome.py`
- `<i data-lucide="name" class="…"></i>` → inline Lucide SVG (downloaded once into `tools/icons/`)
- compiles Tailwind 3.4.17 (standalone CLI, checksum-verified) and versions `site.css`/`site.js`/`base.css` URLs with `?v=<hash>`
- writes sitemap.xml (lastmod from git), robots.txt, llms.txt, site.webmanifest, 404.html (first run)
- checks: one `<h1>` per page, every local link/asset exists, every `<img>` has `alt`, JSON-LD parses, no CDN leftovers, title ≤ 60 chars, description 120–160 chars, social card present

**Never hand-edit generated regions, `site.css`, sitemap/robots/llms.txt.** Change `src/`, `tools/chrome.py` or `tailwind.config.js` and rebuild.
After changing a page `<h1>`, run `python3 tools/social_cards.py` too.

## Staging and production (Cloudflare)

Hosted as the Cloudflare Worker `adeahub` (`wrangler.jsonc`, assets = `public/`, `public/_headers` for cache and
security headers). Same Cloudflare account as the entomo website, but independent: never touch the `entomo`
Worker, and never change `name` in `wrangler.jsonc`.

- `staging` branch → https://staging-adeahub.misty-dawn-f588.workers.dev (branch preview, `noindex` automatically)
- `main` branch → production, https://adeahub.misty-dawn-f588.workers.dev; adeahub.co still points at WordPress
- Cloudflare Workers Builds deploys on push; no build runs there, so commit `public/` fully built.
- Work on `staging`. Production changes only through a pull request `staging` → `main` that the owner merges
  (`main` is protected). Never push or merge to `main` yourself unless the owner asks for that release.

## Relationship to the live site (adeahub.co)

The live site is a WordPress/Elementor rebuild of this repo, later hand-edited. On 2026-10-29 the repo was brought on par with it. Rules set by the owner:

- **Content comes from live**: text, stats, links, images, sections, new components and brand colours.
- **Do not copy WordPress downgrades** (static screenshots replacing HTML/CSS mock-ups, lost decoration/motion, literal "— " eyebrows, icon-font look-alikes, HubSpot form styling, system fonts, copy-paste inconsistencies). Keep the repo design.
- **Do not copy live's errors** (typos, wrong links, stale stats, old product names, @adeahub.com leftovers, duplicated paragraphs, stray elements). Put the correct version and tell the owner.
- Live errors deliberately not copied: the "About Us" title band above the About hero, the stray "10 February 2026" date on Newsroom, "platfor" and the duplicated AI paragraph on WorkWise, "See how AH Connect…" links pointing to Talk To Us, invisible white-on-white "AH Care" headings.
- The 3 blog posts and the press release link to WordPress URLs on adeahub.co that do not exist in this repo.

## Brand & design rules (set by management)

- No `uppercase` CSS on brand taglines, product names or nav subtitles. "Powering modern healthcare" is always lowercase.
- Product names: AH Engage / AH Care / AH Connect / AH Insights / AH Outbreak Management / WorkWise (blue "Work" + "Wise"). Never "adeahub providers / connect / insight", never "AH Insight".
- Brand name is lowercase "adeahub" everywhere.
- CTAs: navbar "Talk To Us" → `talk-to-us/`; mobile-menu "Talk to us" → `contact-us/`; hero and banner "Talk to us" → `talk-to-us/`; "Request a demo" only in the mega-menus and footer.
- Verified statistics: 35M+ users on platform, 8,500+ health facilities (with the comma), 200M+ patient records, 17+ locations, 25+ years. Don't put unconfirmed figures (country/office/module counts) in metadata.
- Email domain adeahub.co (hello@, sales@, press@, support@, partnerships@, apac@, mea@, ame@). Malaysia toll-free: "Malaysia (Local): 1800 819 624".

## Colours

Tailwind tokens (`tailwind.config.js`): `adeahub-blue` `#5298F8` and `adeahub-yellow` `#F3D06F` (brand, fills/backgrounds/icons/large shapes), `adeahub-lightbg` (= blue, solid blue sections), `adeahub-gray`. Never reintroduce `#5BA8E5` or `#F4D06F`.

Text on light backgrounds must meet WCAG AA, which brand blue alone does not (2.9:1):
- `text-adeahub-ink` `#186BDC` for body-size blue text, labels, links, pills (≥ 4.5:1 on white and the pale-blue tints)
- `text-adeahub-heading` `#408DF7` for large blue text (≥ 24px, or ≥ 18.66px bold; ≥ 3:1)
- grey body text `#6B6B6B` (not `#7A7A7A`/`#9E9E9E`), `text-gray-500` (not `gray-400`) for text, `#DC2626` / `#15803D` / `#8A6500` for red/green/gold labels
- Known exception, owner's call: white or yellow text on the brand-blue sections is 2.9:1

## Page architecture

Each page: managed head → page `<style>`s → `site.css` → (moved body styles) → skip link + `<header id="main-nav" class="snav">` → `<main id="main">` → page sections → `<footer class="sfoot">` → page-specific inline scripts. Shared behaviour lives in `site.js`; do not re-add per-page copies of the menu/reveal/counter scripts.

- Content width 1140px: `max-w-[1188px] mx-auto px-6` (a few sections use 1120/1152px).
- Design system (keep it): dot-grid texture and floating blobs on blue sections (plus the soft top-light/deeper-base shading from `site.css`), `btn-glow` / `btn-shimmer` CTAs, card hover lifts, pulsing hero badge dots, scroll reveal, count-up counters, solution-card tilt.
- No eyebrow labels (owner decision, Nov 2026): no small spaced-out caps or dash labels above section headings, in the mega-menus or the footer; they read as AI-generated. Headings stand on their own. Labels that carry information stay, styled as `.t-label` (role lines such as "CMO · CMIO", placed *under* the card title), `.tag-chip` (product/feature names such as "WorkWise AI", "Powered by adea AI") or plain card meta ("Case Study", blog read time). Small labels never use `uppercase` or wide `tracking-*`.
- Type scale (checked against entomo.co): nav 16px (15px at 768–1023px), mega-menu titles 16px with 14px descriptions, section titles `.h-section` (30→40px, lh 1.12, −0.022em), closing CTA titles `.h-cta` (34→48px), body 16px/1.6+, card text 15px, meta 13–14px, nothing readable below 13px outside product mock-ups. No `font-light` below 22px and no `italic` (Outfit has no italic face, so browsers fake it).
- Figures: a set of stats is a `.stat-row` of `.stat` items separated by hairlines (`.on-light` on white), never glass boxes. Repeated capability grids are `.feature` items (top rule, brand-blue `.feature-ico` tile), not same-size shadow cards. Icons are Lucide (`<i data-lucide>`), never emoji or emoji-style images.
- Scroll reveal: add `reveal` (fade up), `reveal-left`, `reveal-right`, plus `reveal-d1`…`reveal-d5` delays. Hidden states are scoped to `html.js` (set by an inline script in the head) so content is never invisible without JavaScript. Elements on screen at load reveal immediately.
- Counters: write the final figure in the HTML (`<span class="counter">30,000+</span>`); `site.js` counts up to exactly that text. `data-target` is no longer needed.
- Hospital carousels (home, customers): one set of `.ah-card`s in `.ah-cards-track`; the page script clones it for the loop and adds auto-scroll, drag/fling and `.ah-nav` arrows. Never duplicate cards by hand.
- Product mock-ups (Care/Engage/Insights heroes, Insights AI chat, Care/WorkWise desktop frames) are pictures: wrapper `role="img"` + `aria-label`, inner `aria-hidden="true" inert`, fake controls `tabindex="-1"`. Keep that when editing them. Vision-section and Outbreak phone mock-ups stay HTML/CSS (live's screenshots of them are a downgrade).
- Homepage hero photo is a `<picture>` (AVIF/WebP, 720w/1406w, desktop only, preloaded with `fetchpriority="high"` via `src/site.json`).
- Headings: one `<h1>`, no skipped levels. Hyphenated words in `<h1>`s are wrapped in `whitespace-nowrap` (headings use `text-wrap: balance`).

## Images

WebP, ≈ 2× the largest rendered size, lowercase-dash names describing the subject. Every `<img>` needs `alt` (organisation names for logos and hospital photos, `alt=""` only for decorative duplicates such as a flag beside its country name), `width`/`height`, and `loading="lazy" decoding="async"` when below the first screen. Hospital photos have `-sm.webp` (640w) variants used via `srcset`/`sizes`. Flags and small icons get `object-fit: contain` from `site.css`.

## Verification before finishing a change

`python3 tools/build.py` must report 0 errors. For visual or behavioural changes also check desktop (1440) and phone (390) widths: no console errors, no horizontal scroll, menus/carousels/tabs/forms work, and axe/Lighthouse show no new issues.
