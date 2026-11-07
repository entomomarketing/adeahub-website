# Forms and security on the adeahub website

Set up 2026-11-07, following the entomo website (same Cloudflare account, separate Worker, separate settings).
The three forms keep the site's own markup and post to this site's own Cloudflare Worker, which checks them and
forwards them to HubSpot. Nothing is sent from the browser to HubSpot directly.

| intent | page | HubSpot form (portal 243938139, na2) | fields sent |
|---|---|---|---|
| `contact` | contact-us | `d616357e-71b4-4eab-9b98-472148196745` (the live Contact form) | firstname, lastname, email, company, message (required); enquiry_type, region |
| `demo` | talk-to-us | `7b797e59-5301-476f-8ce0-0429519f1de9` (the live Talk To Us form) | firstname, lastname, email, company (required); jobtitle, area_of_interest (several, `;`-joined), message |
| `subscribe` | blogs (newsletter band) | **none yet**: `HS_FORM_SUBSCRIBE` is empty, so the form says it is not taking submissions and gives hello@adeahub.co | email |

The GUIDs and field names were read from the HubSpot forms the live adeahub.co pages embed. Field names in the HTML
**are** the HubSpot internal names. Allowed fields, required fields and dropdown values live in one file,
`src/forms.json`, read by both the Worker (validation) and `tools/build.py` (checks the page markup), so the page,
the Worker and HubSpot cannot drift apart. adeahub.co's own newsletter form is a WordPress (Elementor) form, so
HubSpot has no newsletter form to reuse.

## How a submission travels

1. `public/assets/js/forms.js` (loaded on pages with a `<form data-form>`; `build.py` adds the tag) collects only the
   fields the page declared, trims them, and holds the submit until the browser's own validation and the Turnstile
   check pass.
2. It posts JSON to `POST /api/forms/<intent>`: `{ fields, turnstile, page: { uri, title } }`.
3. `src/worker.js` runs for `/api/*` only (`run_worker_first` in `wrangler.jsonc`; pages never wait on code) and
   applies these checks in order:

| check | response |
|---|---|
| not POST / unknown intent | 405 `method` / 404 `intent` |
| `Origin` is not this address or `https://` on a host in `PRODUCTION_HOSTS`, or `Sec-Fetch-Site` is not `same-origin` | 403 `origin` |
| body is not `application/json` | 415 `content_type` |
| body over 16 KB / not JSON | 413 `too_large` / 400 `json` |
| more than 120 posts a minute overall, or 5 a minute from one IP to one form (`RL_GLOBAL`, `RL_INTENT`) | 429 `rate_limited`, `Retry-After: 60` |
| honeypot `hs_website` filled | 200 and nothing is sent (the page shows success) |
| Turnstile token missing or rejected by Cloudflare (`TURNSTILE_SECRET` is set) | 403 `turnstile` |
| a field fails `src/forms.json` | 400 `validation`, `errors: [{ field, reason }]`, shown on the field |
| the form has no HubSpot GUID | 503 `not_configured` (page gives hello@adeahub.co) |
| HubSpot answers 4xx (invalid or blocked email, missing field) | 400 `upstream` with HubSpot's `errorType` |
| HubSpot down or slow (10 s) | 502 `hubspot` (page gives hello@adeahub.co) |

Field rules: names up to 100 characters with at least one letter and no `<`, `>` or `://`; organisation and job
title up to 150; email up to 254 and shaped like an address; message up to 2,000 with at most three links;
dropdown and checkbox values must be one of the HubSpot values. Every value is NFC-normalised and stripped of
control characters (C0/C1, zero-width, U+2028/2029, bidi overrides); single-line fields lose line breaks. The
page applies the same limits as `maxlength`, so most visitors never see a 400.

**The rate limit is a soft guard.** Its counters are per Cloudflare machine and eventually consistent: it stops a
loop on one connection, not a distributed flood. Turnstile (a fresh token for every post) is the real guard, plus
the zone rate-limiting rule below once adeahub.co is on Cloudflare. The rate-limit `namespace_id`s (2001, 2002)
are account-wide, so they differ from the entomo Worker's (1001, 1002).

## On the page

- **Consent:** every form has a required, unticked checkbox `website_consent_given`: *"I agree to adeahub processing
  the details I have entered for the purpose of this request."* The Worker refuses a submission without it. The
  wording is `CONSENT_TEXT` in `wrangler.jsonc` with `CONSENT_TEXT_VERSION`; change the page text, both values and
  the version together. adeahub.co has no privacy policy page (it returns 404), so the line does not link one; once
  a policy is published, add the link to the checkbox text and bump the version.
- **Security check:** a Cloudflare Turnstile widget (`adeahub-website-forms`, managed mode) renders in
  `.form-turnstile` when the visitor first focuses a form. Site key `0x4AAAAAAF3qGiiQuD1YmC8L` is in `forms.js`; the
  secret is the Worker secret `TURNSTILE_SECRET` (never in a file). Widget hostnames: adeahub.co, www.adeahub.co,
  adeahub.misty-dawn-f588.workers.dev, staging-adeahub.misty-dawn-f588.workers.dev. Version-preview addresses
  (`<id>-adeahub…`) are not listed, so forms there fail the check; use staging.
- **Spam:** an off-screen honeypot field `hs_website`; a filled honeypot shows success and sends nothing.
- **Errors:** the Worker's 400 reasons go on the named field (`setCustomValidity`) and in the message under the
  form; 429 says try again in a minute; anything else gives hello@adeahub.co. The button is re-enabled.
- **Success:** the form dispatches `form:success`; the contact and demo pages show their thank-you panels (focus
  moves to the heading); the newsletter relabels its button "Subscribed". Every success pushes
  `{ event: "hs_form_success", form_intent }` to `window.dataLayer` for Tag Manager conversion triggers.
- **Test submissions:** anything submitted outside `PRODUCTION_HOSTS` (staging, previews) still reaches HubSpot,
  marked: the conversion page name starts with `[TEST: staging]`, and the HubSpot cookie is not sent. Find them in
  HubSpot under form submissions whose page title contains "[TEST: staging]".

## Tags (Google Tag Manager)

The live site's container `GTM-KWRK59TQ` (GA4 `G-Y6WB8T7M08` and Google Ads) is in the managed head of every page
(`site.gtm` in `src/site.json`), but it loads **only on adeahub.co and www.adeahub.co** (`site.tagHosts`). Staging,
previews and the workers.dev production address stay silent, so reviewers never reach the GA4 property. Open any
page with `?tags=on` to load it for that browser session (Tag Assistant, GA4 DebugView); `?tags=off` stops it.
The HubSpot tracking code is not installed (the live site does not run it either); add it only together with a
cookie-consent decision.

## Response headers (`public/_headers`)

Same baseline as entomo: HSTS (one year, no `includeSubDomains`, so no other adeahub.co subdomain is forced onto
HTTPS by surprise), `nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Permissions-Policy`,
`Cross-Origin-Opener-Policy: same-origin-allow-popups`, `Cross-Origin-Resource-Policy: same-site`, and a
**Content-Security-Policy in Report-Only mode** that reports to `/api/csp-report` (the Worker logs each report).
`script-src` keeps `'unsafe-inline'` because every page has inline scripts. Allowed outside hosts: Turnstile and the
Tag Manager container with GA4 and Google Ads. After about a week of clean reports on adeahub.co, rename the header
to `Content-Security-Policy` (enforcing). `build.py` fails if a header is missing or a line passes Cloudflare's
2,000-character limit.

`/.well-known/security.txt` names support@adeahub.co as the security contact and expires a year after it is
written; `build.py` rewrites it when fewer than 90 days remain and warns at 60. A dedicated `security@adeahub.co`
mailbox would be better; change `site.securityContact` in `src/site.json` when it exists.

## Logs

Workers Logs are on (`observability` in `wrangler.jsonc`). Workers & Pages > adeahub > Observability; filter on
`hubspot` (rejections), `turnstile`, `honeypot`, `csp-report`. On staging and previews every form response carries
`X-Adeahub-Guards: ratelimit=on; turnstile=on; consent-forward=off`, showing which guards that version has.

## Testing

- From a terminal, `curl` always gets 403 `origin` (no browser `Origin`); send
  `-H "Origin: https://staging-adeahub.misty-dawn-f588.workers.dev"` to reach the checks behind it.
- Locally: `npx wrangler dev`, with Cloudflare's always-pass Turnstile test keys (site key `1x00000000000000000000AA`,
  secret `1x0000000000000000000000000000000AA` via `--var TURNSTILE_SECRET:…`) and, to keep test posts out of HubSpot,
  `--var HS_SUBMIT_URL:http://127.0.0.1:<port>/` pointing at a stand-in server.
- Delete real test contacts from HubSpot afterwards.

## Still to do in HubSpot (the owner)

1. **Newsletter form:** create a HubSpot form with an email field (Marketing > Forms), put its GUID in
   `HS_FORM_SUBSCRIBE` in `wrangler.jsonc`, release. Until then the blog's newsletter form says it is not taking
   submissions.
2. **Notifications:** on the Contact and Talk To Us forms, set "send submission notifications to" to the people who
   follow up (form options), since the website no longer embeds HubSpot's own form.
3. **Consent records (optional):** create the contact properties `website_consent_given` (single checkbox),
   `website_consent_text_version` and `website_consent_timestamp` (single-line text), add them as hidden fields to the
   forms, turn on "Notice and consent", then set `CONSENT_FORWARD` to `"hubspot"`. The Worker then stores the
   consent with each contact.
4. **Retention:** decide how long non-customer contacts are kept and build a HubSpot workflow that deletes them
   (entomo keeps 36 months).

## When adeahub.co moves to Cloudflare (zone settings)

These exist only on a zone, so they wait for the domain:
- SSL/TLS > Edge Certificates: Minimum TLS 1.2, TLS 1.3 on, Always Use HTTPS on. Leave the zone's HSTS off
  (`_headers` sends it).
- Security > WAF: Cloudflare Managed Ruleset on; Security > Bots: Bot Fight Mode on.
- Security > WAF > Rate limiting rule: `(http.request.method eq "POST" and starts_with(http.request.uri.path, "/api/forms/"))`,
  per IP, 10 requests per minute, action Block. This counts at the edge across every machine, unlike the Worker's.
- Then switch the Content-Security-Policy to enforcing after a clean week of reports.

## Changing things later

- **New field or dropdown option:** add it to `src/forms.json` first (the Worker rejects anything not there), then to
  the page; HubSpot's form must have the same property and option values.
- **New form:** add the intent to `src/forms.json` (page, `hubspotVar`, fields), the GUID to `wrangler.jsonc` `vars`,
  and to `INTENTS` in `forms.js`; mark up the `<form data-form="<intent>">` with the honeypot, consent checkbox,
  `.form-turnstile` and `.form-status`. `build.py` checks all of it.
- **Rotate the Turnstile secret:** Cloudflare > Turnstile > adeahub-website-forms > Rotate secret, then update the
  Worker secret `TURNSTILE_SECRET` (`npx wrangler versions secret put TURNSTILE_SECRET`, then release).
