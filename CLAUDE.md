# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **adeahub** marketing website — a static HTML/CSS/JS site for a healthcare platform company. No build tools, no package manager, no framework. Pages open directly in a browser, or serve the folder with `python3 -m http.server 8765` and open http://127.0.0.1:8765/index.html.

## Relationship to the live site (adeahub.co)

The live site https://adeahub.co is a WordPress/Elementor rebuild of this repo that was then edited by hand on WordPress. On 2026-10-29 this repo was brought back on par with the live site page by page. Rules for keeping it in sync, set by the site owner:

- **Content comes from live**: text, stats, links, images, sections, new components (e.g. carousel arrows/drag, About team tabs) and brand colours.
- **Do not copy WordPress downgrades.** Where live's design is worse than this repo's because of WordPress/Elementor/HubSpot limitations, keep the repo design: static screenshots replacing HTML/CSS mock-ups, lost dot-grid/blob/ring decoration, lost glow/shimmer/hover/reveal motion, literal "— " text instead of styled eyebrow labels, icon-font look-alikes, HubSpot-default form styling, system-font fallbacks, copy-paste style inconsistencies.
- **Do not copy live's errors.** Put the correct version (typos, wrong link targets, stale stats, old product names, @adeahub.com leftovers, duplicated paragraphs, stray elements) and tell the owner so live can be fixed too.

Live URL → repo file:

| Live URL | Repo file |
|---|---|
| `/` | `index.html` |
| `/platform/` | `adeahub_platform.html` |
| `/ah-engage/` | `adeahub_engage.html` |
| `/ah-care/` | `adeahub_care.html` |
| `/ah-connect/` | `adeahub_connect.html` |
| `/ah-insights/` | `adeahub_insights.html` |
| `/ah-outbreak-management/` | `adeahub_outbreak.html` |
| `/workwise/` | `workwise.html` |
| `/about-us/` | `about_us.html` |
| `/customers/` | `customers.html` |
| `/newsroom/` | `newsroom.html` |
| `/blogs/` | `Blogs.html` (capital B — links must match the case) |
| `/contact-us/` | `contact_us.html` |
| `/talk-to-us/` | `request_demo.html` |

Other files: `ah-engage-animated.html`, `ah-care-animated.html`, `ah-connect-animated.html`, `ah-insights-animated.html`, `ah-outbreak-animated.html` are the animated product previews embedded via `<iframe>` in the homepage "One platform" section (the live site loads the same files). `nav-dropdown-preview.html` and `adeahub-platform-composite.html` are design scratch files, not linked from the site.

## Tech Stack

- **Tailwind CSS** — loaded via CDN (`https://cdn.tailwindcss.com`), configured inline per page with a `tailwind.config` script block
- **Lucide Icons** — loaded via CDN (`https://unpkg.com/lucide@latest`), activated with `lucide.createIcons()` at the bottom of each page
- **Google Fonts** — Outfit (weights 300–800), loaded via `<link>` in `<head>`
- No JavaScript framework; all interactivity is vanilla JS

`Images/` holds all assets: `Hospitals/` (case-study photos, prefer the `.webp` versions), `logos/` (hospital logos, `.webp`), `Clients_logos/` (the 14 homepage marquee logos, `.webp`), `Leaders/` (team portraits), plus per-page folders added during the sync.

## Brand & Design Rules

These rules apply across every page — they were set by management and must be preserved:

- **No uppercase CSS** (`text-uppercase`, `uppercase` Tailwind class) on brand taglines, product names, or nav subtitles
- **"Powering modern healthcare"** is always lowercase — in both the navbar subtitle and footer tagline
- **Product names**: AH Engage / AH Care / AH Connect / AH Insights / AH Outbreak Management / WorkWise (rendered as a blue "Work" + "Wise"). Never the old names "adeahub providers / connect / insight". Live's mega-menu says "AH Insight" by mistake; the repo uses "AH Insights".
- **Brand name** is lowercase "adeahub" everywhere, including inside quotes.
- **CTA language**:
  - Navbar button: "Talk To Us" → `request_demo.html`; mobile menu button: "Talk to us" → `contact_us.html`
  - Hero sections and CTA banners: "Talk to us" → `request_demo.html`
  - "Request a demo" appears only as the small link inside the mega-menus and the footer button
- **Verified statistics** (from the owner): 35M+ users on platform, 8,500+ health facilities (with the comma), 200M+ patient records, 17+ locations, 25+ years
- Email domain is adeahub.co (hello@, sales@, press@, support@, partnerships@, apac@, mea@, ame@). Malaysia toll-free: "Malaysia (Local): 1800 819 624".

## Brand Colors (CSS variables + Tailwind tokens)

```css
--blue: #5298F8        /* primary brand blue (updated 2026-10-29, was #5BA8E5) */
--yellow: #F3D06F      /* accent / CTA yellow (updated 2026-10-29, was #F4D06F) */
--blue-pale: rgba(82,152,248,0.10)
```

Tailwind custom colors: `adeahub-blue`, `adeahub-yellow`, `adeahub-gray`, `adeahub-lightbg` (= the blue, used for the solid blue sections). Never reintroduce `#5BA8E5` or `#F4D06F`.

## Shared Page Architecture

Every page follows the same structure:

1. `<head>` — Tailwind CDN + config, Lucide CDN, Google Fonts, page `<style>`, then the generated `<!-- live-head -->` block (favicon + canonical/Open Graph tags copied from adeahub.co) and the generated `<style id="site-chrome">`
2. `<nav id="main-nav" class="snav">` — generated header: Platform · Products ▾ (750px mega panel) · Resources ▾ (500px panel) · About Us · Contact Us · "Talk To Us" button. The current page's item (Platform / About Us / Contact Us) is blue, as on live. `#mobile-menu` order matches live: Products list, Platform, Resources list, About Us, Contact Us, "Talk to us" → contact_us.html.
3. Page-specific sections
4. `<footer class="sfoot">` — generated, identical on every page
5. `<script>lucide.createIcons();</script>` — must be called after body
6. Mobile menu toggle script (vanilla JS, `#mobile-menu-btn` / `#mobile-menu` / `#hamburger-icon` / `#close-icon`)
7. Scroll-reveal script using `IntersectionObserver` (classes: `reveal`, `reveal-left`, `reveal-right`, with delay modifiers `reveal-d1` through `reveal-d5`)

**Never hand-edit the header, footer or the generated head blocks in a page.** Change them in `tools/site_chrome.py` and run `python3 tools/site_chrome.py` from the repo root; it rewrites all 14 pages and is safe to re-run. Header/footer layout, sizes and positions were measured on adeahub.co at 1440px; the frosted header, CTA shimmer, mega-menu gradient strip, eyebrow labels, chevrons, 40px icon tiles and footer social icons are the repo's original design (live's versions were WordPress downgrades).

## Layout and design conventions

- Content width is 1140px: section containers use `max-w-[1188px] mx-auto px-6`. A few sections use 1120px or 1152px.
- The repo's design system stays: `.section-label` eyebrows (22×2px bar, 800 weight, 0.12em letter-spacing; blue on white, yellow on blue), dot-grid texture and floating blobs on blue sections, `btn-glow` / `btn-shimmer` on primary CTAs, hover lifts on cards, pulsing hero badge dots, scroll reveal and count-up counters.
- Page-specific values (font sizes, card radii, shadows) are Tailwind arbitrary values or small page-scoped `<style>` rules, mostly measured on live.
- `html, body { overflow-x: clip }` (in site-chrome) stops slide-in animations from causing sideways scroll on phones without breaking the sticky header.

## Homepage and page specifics

- Homepage hero photo is `Images/hero.webp` as a CSS background on the right half (as on live).
- Hospital carousels (homepage and customers.html): one set of static `.ah-card` blocks inside `.ah-cards-track`; a script at the bottom clones the set once for a seamless loop and adds auto-scroll, pause on hover, click/touch drag with fling, and left/right `.ah-nav` arrows. Edit the cards in the markup, never duplicate them by hand.
- "Proven at scale" logo marquee uses the 14 `Images/Clients_logos/*.webp` files.
- The platform diagrams use `Images/adea-AI-default.svg` for the adea AI layer.
- AH Care, AH Engage and AH Insights inline their hero dashboard/phone mock-ups (scoped CSS under a wrapper id, script at the bottom). The homepage "One platform" section, the AH Connect hero and the AH Outbreak hero load `ah-*-animated.html` via iframes; don't edit those files for a single page.
- Vision sections (Care, Engage, Connect, WorkWise, Outbreak) and Outbreak's "What it covers" phone are HTML/CSS mock-ups. Live replaced them with static screenshots of these same mock-ups; keep the HTML versions.
- Live errors deliberately NOT copied (fix them on live too): the "About Us" WordPress title band above the About hero, the stray "10 February 2026" date atop Newsroom's Media Inquiries card, "platfor" and the duplicated AI paragraph on WorkWise, "See how AH Connect…" links pointing to Talk To Us, and the invisible white-on-white "AH Care" headings inside stat cards.

## Scroll Reveal Pattern

Elements animate in on scroll by adding `.visible` via `IntersectionObserver`. Apply these classes to elements that should animate:
- `reveal` — fade up
- `reveal-left` — slide from left
- `reveal-right` — slide from right
- `reveal-d1` through `reveal-d5` — staggered delays (0.1s–0.5s)

## Changelog

`adeahub_website_changelog.md` documents the strategic changes made during the March 2026 repositioning (infrastructure/core platform narrative). Consult it to understand why specific copy or naming decisions were made before changing them.
