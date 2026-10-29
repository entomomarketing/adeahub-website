# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **adeahub** marketing website — a static HTML/CSS/JS site for a healthcare platform company. No build tools, no package manager, no framework. Pages are opened directly in a browser.

## Tech Stack

- **Tailwind CSS** — loaded via CDN (`https://cdn.tailwindcss.com`), configured inline per page with a `tailwind.config` script block
- **Lucide Icons** — loaded via CDN (`https://unpkg.com/lucide@latest`), activated with `lucide.createIcons()` at the bottom of each page
- **Google Fonts** — Outfit (weights 300–800), loaded via `<link>` in `<head>`
- No JavaScript framework; all interactivity is vanilla JS

## Site Structure

| File | Page |
|---|---|
| `index.html` | Homepage |
| `adeahub_platform.html` | Platform overview |
| `adeahub_pha.html` | AH Health App (patient-facing product) |
| `adeahub_providers.html` | AH Provider (HIS for healthcare workers) |
| `adeahub_connect.html` | AH Connect (FHIR interoperability layer) |
| `adeahub_insight.html` | AH Insights (analytics/BI product) |
| `about_us.html` | About / company history |
| `customers.html` | Customer stories |
| `newsroom.html` | News / press |
| `Blogs.html` | Blog listing |
| `contact_us.html` | Contact form |
| `request_demo.html` | Demo request form |
| `workwise.html` | WorkWise product page |

Backup files (`* backup.html`) are snapshots — do not edit them.

`Images/` holds all assets, organized into `Clients_logos/`, `logos/`, and `Hospitals/` subdirectories.

## Brand & Design Rules

These rules apply across every page — they were set by management and must be preserved:

- **No uppercase CSS** (`text-uppercase`, `uppercase` Tailwind class) on brand taglines, product names, or nav subtitles
- **"Powering modern healthcare"** is always lowercase — in both the navbar subtitle and footer tagline
- **Product names**: AH Health App / AH Provider / AH Connect / AH Insights (not the old "adeahub PHA / providers / connect / insight" names)
- **CTA language**:
  - Navbar (desktop + mobile): "Talk to Our Team"
  - Hero sections and CTA banners: "Talk to Our Healthcare Team" or "Talk to a Platform Architect"
  - Never use "Request a Demo"
- **Verified statistics** to use: 200M+ patient records, 35M+ platform users, 3,200+ facilities, 25+ years, 12+ countries

## Brand Colors (CSS variables + Tailwind tokens)

```css
--blue: #6396F1        /* primary brand blue */
--yellow: #F2C747      /* accent / CTA yellow */
--blue-pale: rgba(99,150,241,0.10)
```

Tailwind custom colors: `adeahub-blue`, `adeahub-yellow`, `adeahub-gray`

## Shared Page Architecture

Every page follows the same structure:

1. `<head>` — Tailwind CDN + config, Lucide CDN, Google Fonts
2. `<nav>` — sticky navbar with desktop dropdown and `#mobile-menu` toggle
3. Page-specific sections
4. `<footer>` — consistent across all pages
5. `<script>lucide.createIcons();</script>` — must be called after body
6. Mobile menu toggle script (vanilla JS, `#mobile-menu-btn` / `#mobile-menu`)
7. Scroll-reveal script using `IntersectionObserver` (classes: `reveal`, `reveal-left`, `reveal-right`, with delay modifiers `reveal-d1` through `reveal-d5`)

When editing one page's navbar or footer, the same change typically needs to be applied to all other pages for consistency.

## Scroll Reveal Pattern

Elements animate in on scroll by adding `.visible` via `IntersectionObserver`. Apply these classes to elements that should animate:
- `reveal` — fade up
- `reveal-left` — slide from left
- `reveal-right` — slide from right
- `reveal-d1` through `reveal-d5` — staggered delays (0.1s–0.5s)

## Changelog

`adeahub_website_changelog.md` documents all strategic changes made during the March 2026 repositioning (infrastructure/core platform narrative). Consult it to understand why specific copy or naming decisions were made before changing them.
