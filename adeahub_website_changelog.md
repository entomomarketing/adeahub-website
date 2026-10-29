# adeahub Website — Change Log
**Project:** adeahub digital health platform website (HTML/Tailwind CSS)
**Date:** March 2026
**Scope:** Full-site strategic repositioning — from SaaS product pitch to Core Platform / Infrastructure pitch
**Based on:** Management feedback, research document analysis, project knowledge files

---

## Strategic Direction

The overarching instruction across all pages was to move from a "typical innovative SaaS pitch" to an "Infrastructure / Core Platform" pitch, modelled on how SAP, Epic, and Oracle Health position themselves. The specific pillars of this pivot were:

- **Lead with scale, longevity, and trust** — not features and workflows
- **Establish the heritage narrative** — 1998 lineage → MySejahtera 2020 → Dedalus AMEA acquisition 2025 → adeahub today
- **Rebrand the four products with the "AH" prefix** across all pages
- **Embed the Agentic Layer narrative** — AI as embedded platform intelligence, not a bolt-on feature
- **Use verified, accurate statistics** — 200M+ patient records, 35M+ users, 3,200+ facilities, 25+ years
- **Remove all-caps / uppercase CSS** from brand taglines and product names
- **Replace "Request a Demo" with "Talk to Our Team" / "Talk to Our Healthcare Team"** throughout

---

## Files Changed

### 1. `index.html` — Homepage

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` | Updated to include platform-level description | Brand positioning |
| Navbar subtitle | Removed `uppercase` CSS class; "Powering Modern Healthcare" → "Powering modern healthcare" | Management feedback: no all-caps |
| Navbar dropdown — all 4 products | Renamed to AH Health App / AH Provider / AH Connect / AH Insights with persona subtitles | Management directive |
| Navbar dropdown subtitles | Personal Health App → "For Patients & Caregivers"; HIS → "For Healthcare Workers & Admins"; Interoperability → "For Devices & Applications"; Analytics → "For Decision Makers" | Persona mapping from management feedback |
| Navbar CTA | "Request a Demo" → "Talk to Our Team" | Management feedback |
| Mobile menu — all 4 products | Same renaming as desktop dropdown | Consistency |
| Mobile menu CTA | "Request a Demo" → "Talk to Our Team" | Management feedback |
| Hero badge | Updated platform descriptor | Core platform framing |
| Hero heading | Updated to lead with infrastructure/scale framing | Research: SAP/Epic/Oracle positioning |
| Trust bar stats | "14M+ Users" → "35M+ Platform Users"; "50M+ Records" → "200M+ Patient Records" | Project knowledge files (verified stats) |
| Four solutions section | Product cards renamed: adeahub PHA → AH Health App, providers → AH Provider, connect → AH Connect, insight → AH Insights | Management directive |
| Solutions card subtitles | Mapped to personas: Patients & Caregivers / Healthcare Workers & Admins / Devices & Applications / Decision Makers | Management directive |
| Platform section | Rewritten to infrastructure narrative; "Agentic Layer" terminology added | Management feedback on AI positioning |
| Brand Heritage section | New "1998 → 2020 → 2025 → Today" timeline narrative added | Management directive |
| Outcomes section | Stats and outcomes updated to align with verified data | Project knowledge files |
| CTA section | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| Footer tagline | Removed `uppercase` CSS; "Powering Modern Healthcare" → "Powering modern healthcare" | Management feedback |

---

### 2. `about_us.html` — About Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` + meta description | Updated to reflect 200M patient records, 25+ year heritage | Verified stats from project knowledge |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency across site |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency across site |
| Hero CTA | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| Our Story body copy | Founding year 2010 → 1998; "50M patient records" → "200M patient records"; narrative updated to include 1998 regional lineage, MySejahtera 2020, Dedalus 2025 acquisition | Management directive; verified from project knowledge |
| Timeline — complete rewrite | 7 milestones added/rewritten: 1998 (Regional IT Heritage), 2010 (entomo Founded), 2015 (Regional Scale), 2020 (MySejahtera — National Scale), 2021 (Global Recognition), 2025 (Dedalus AMEA Acquisition), Today (adeahub — The Core Healthcare Platform) | Management directive: establish heritage narrative |
| By the Numbers stats | "50M+ Patient Records" → "200M+ Patient Records"; "20 years" → "25 years" | Verified stats |
| CTA section | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

### 3. `adeahub_platform.html` — Platform Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` + meta description | New title: "adeahub Platform — The Core Healthcare Platform for Asia, the Middle East, and Africa"; meta updated with FHIR-native, 200M+ records, 3,200+ facilities | Core platform positioning |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency |
| Hero heading | "An Open, Modular Digital Health Platform Built for Scale" → "The Source of Truth for Healthcare Operations" | Core platform / infrastructure framing |
| Hero subtext | Rewritten: "More than an EHR. More than a patient app. adeahub is the operational core..." | Research: SAP/Epic infrastructure positioning |
| Hero CTAs | Added second CTA: "Explore the Four Pillars" (linking to `#pillars` anchor); Primary: "Talk to a Platform Architect" | Clearer wayfinding |
| Architecture diagram layer labels | adeahub PHA → AH Health App; adeahub providers → AH Provider; adeahub connect → AH Connect; adeahub insight → AH Insights | Management directive |
| Section 2 — Platform Overview narrative | Rewritten to infrastructure-first, core platform framing; "Healthcare systems don't fail because of lack of technology..." | Research: SAP/Epic positioning language |
| NEW section — Agentic Layer Callout | Entirely new section added between Section 2 and Section 3: "The adeahub Agentic Layer" with 5 capability pills | Management directive: AI as embedded intelligence, not bolt-on |
| Section 3 — Four Pillars | Added `id="pillars"` anchor; heading updated: "Four Integrated Layers. One Unified Platform." → "One Platform. Four Integrated Pillars. A Role for Everyone in Healthcare." | Core platform narrative |
| Four pillar card headings | adeahub providers → AH Provider; adeahub PHA → AH Health App; adeahub connect → AH Connect; adeahub insight → AH Insights | Management directive |
| Stats bar | "30,000+ Daily Users" → "35M+ Platform Users" | Verified stats (MySejahtera + platform users) |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

### 4. `adeahub_pha.html` — AH Health App Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` | "adeahub PHA — Patient Engagement Platform..." → "AH Health App — Patient Engagement Platform..." | Management directive |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency |
| Hero h1 | "adeahub Personal Health App" → "AH Health App" | Management directive |
| Hero CTA | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| CTA section button | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| All body text | "adeahub PHA" → "AH Health App" throughout all section copy | Management directive |
| Footer sibling product links | "adeahub providers/connect/insight" → "AH Provider / AH Connect / AH Insights" with correct href links | Management directive + link fix |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

### 5. `adeahub_providers.html` — AH Provider Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` | "adeahub providers \| Hospital Information System" → "AH Provider — Hospital Information System \| adeahub" | Management directive |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency |
| Hero h1 | "adeahub providers" → "AH Provider" | Management directive |
| Hero CTA | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| CTA section button | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| All body text | "adeahub providers" → "AH Provider" throughout all section copy | Management directive |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

### 6. `adeahub_connect.html` — AH Connect Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` | "adeahub connect \| FHIR Interoperability..." → "AH Connect — FHIR Interoperability... \| adeahub" | Management directive |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency |
| Hero h1 | "adeahub connect" → "AH Connect" | Management directive |
| Hero diagram central hub label | "adeahub connect" → "AH Connect" | Consistency |
| Hero CTA | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| CTA section button | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| All body text | "adeahub connect" → "AH Connect" throughout all section copy | Management directive |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

### 7. `adeahub_insight.html` — AH Insights Page

| Section | What Changed | Source / Rationale |
|---|---|---|
| Page `<title>` | "adeahub insight \| Healthcare Intelligence & Analytics" → "AH Insights — Healthcare Intelligence & Analytics \| adeahub" | Management directive |
| Navbar | All product names → AH naming; CTA → "Talk to Our Team"; subtitle → lowercase | Consistency |
| Mobile menu | All product names → AH naming; CTA → "Talk to Our Team" | Consistency |
| Hero h1 | "adeahub insight" → "AH Insights" | Management directive |
| Hero CTA | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| CTA section button | "Request a Demo" → "Talk to Our Healthcare Team" | Management feedback |
| All body text | "adeahub insight" → "AH Insights" throughout all section copy | Management directive |
| Footer tagline | Removed `uppercase` CSS; text lowercased | Management feedback |

---

## Statistics Used — Verification Notes

| Stat | Value Used | Source |
|---|---|---|
| Patient records | 200M+ | Project knowledge files (Dedalus AMEA acquisition) |
| Platform users | 35M+ | MySejahtera peak user base (project knowledge) |
| Healthcare facilities | 3,200+ | Project knowledge files (Dedalus AMEA) |
| Years of heritage | 25+ | 1998 lineage (regional HIS roots) |
| Countries | 12+ | Project knowledge files |
| HIMSS Stage 7 | 6 hospitals | Project knowledge files |
| MySejahtera worldwide rank | #1 install penetration | Data.ai (2021), project knowledge files |

---

## New Content Added

### Agentic Layer Callout Section (adeahub_platform.html)
A new section was inserted between the Platform Overview narrative and the Four Pillars section. This section introduces the adeahub Agentic Layer as embedded platform intelligence — not an add-on. It includes five capability pills:
- Clinical Decision Support
- Predictive Risk Stratification
- Automated Triage & Alerts
- Population Health Modelling
- Intelligent Documentation

### Heritage Timeline (about_us.html)
Seven-milestone timeline completely rewritten to establish the 1998-to-today heritage narrative:
1. 1998 — Healthcare IT Heritage
2. 2010 — entomo Founded
3. 2015 — Regional Scale
4. 2020 — MySejahtera National Scale
5. 2021 — Global Recognition (awards)
6. 2025 — Dedalus AMEA Acquisition
7. Today — adeahub, The Core Healthcare Platform

---

## Design & Brand Rules Applied

- **No uppercase CSS** on brand taglines, product names, or navigation subtitles throughout all 7 pages
- **"Powering modern healthcare"** consistently lower-case across all page navbar subtitles and footer taglines
- **AH prefix** used consistently: AH Health App, AH Provider, AH Connect, AH Insights
- **Persona subtitles** in all navigation dropdowns: For Patients & Caregivers / For Healthcare Workers & Admins / For Devices & Applications / For Decision Makers
- **CTA language**: Desktop/mobile navbar → "Talk to Our Team"; Hero and CTA sections → "Talk to Our Healthcare Team" / "Talk to a Platform Architect"
- **Brand tone** maintained throughout: authoritative, outcome-driven, empathetic, confidence without hyperbole
