/* adeahub website Worker. Static assets are served by the ASSETS binding; this script runs only for /api/*
   (assets.run_worker_first in wrangler.jsonc), so pages never wait on code.

   POST /api/forms/<intent>  checks the origin, size and rate, drops honeypot hits, verifies Cloudflare Turnstile,
                             validates and cleans every field against src/forms.json, then forwards the submission to
                             HubSpot's Forms API (portal HS_PORTAL, one HubSpot form per intent).
   POST /api/csp-report      receives Content-Security-Policy reports and logs them (Workers Logs).

   Settings (wrangler.jsonc vars; secrets in the dashboard or with `wrangler versions secret put`):
     TURNSTILE_SECRET  secret of the "adeahub website" Turnstile widget; unset = tokens are not verified (logged).
     HS_FORM_<INTENT>  HubSpot form GUID per intent; empty = that form answers 503 "not_configured".
     PRODUCTION_HOSTS  hosts whose submissions are real; anywhere else (staging, version previews) they reach
                       HubSpot marked "[TEST: staging]" and without the visitor cookie.
     CONSENT_FORWARD   "hubspot" once the consent properties exist on the HubSpot forms (docs/FORMS-AND-SECURITY.md);
                       anything else = consent is required from the visitor but not written to HubSpot.
   Modelled on the entomo website's Worker (same account, separate Worker); see docs/FORMS-AND-SECURITY.md. */
import SCHEMA from "./forms.json";

const MAX_BODY = 16 * 1024;
const HUBSPOT = "https://api-na2.hsforms.com/submissions/v3/integration/submit/";
const TURNSTILE_VERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
const TEST_PREFIX = "[TEST: staging] ";
const HONEYPOT = "hs_website";
const CONSENT = "website_consent_given";

// C0/C1 controls, zero-width characters, the Unicode line and paragraph separators, bidi overrides
const CONTROL = /[\u0000-\u0008\u000B-\u001F\u007F-\u009F\u200B-\u200D\uFEFF\u2028\u2029\u202A-\u202E\u2066-\u2069]/g;
const EMAIL = /^[^\s@<>]+@[^\s@<>]+\.[A-Za-z]{2,}$/;
const LETTER = /\p{L}/u;
const IP = /^[0-9A-Fa-f:.]{2,45}$/;

function json(status, body, extra) {
  const h = Object.assign({ "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }, extra || {});
  return new Response(JSON.stringify(body), { status, headers: h });
}
function hostList(env) {
  return (env.PRODUCTION_HOSTS || "").split(",").map(s => s.trim().toLowerCase()).filter(Boolean);
}
function clean(value, multiline) {
  let v = String(value == null ? "" : value).normalize("NFC").replace(CONTROL, "");
  if (multiline) {
    v = v.replace(/\r\n?/g, "\n").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n");
    return v.split("\n").map(l => l.trim()).join("\n").trim();
  }
  return v.replace(/\s+/g, " ").trim();
}
function validateOne(name, raw) {
  const rule = SCHEMA.fields[name];
  const multi = rule.kind === "enum-multi";
  const values = Array.isArray(raw) ? raw : [raw];
  if (!multi && values.length > 1) return { error: "one value expected" };
  if (values.length > 20) return { error: "too many values" };
  const out = [];
  for (const r of values) {
    if (r !== null && typeof r === "object") return { error: "is not valid" };
    const v = clean(r, rule.kind === "multiline");
    if (!v) continue;
    if (rule.max && v.length > rule.max) return { error: "must be " + rule.max + " characters or fewer" };
    switch (rule.kind) {
      case "name":
      case "text":
        if (!LETTER.test(v)) return { error: "must contain letters" };
        if (/[<>]/.test(v) || /:\/\//.test(v)) return { error: "contains characters that are not allowed" };
        break;
      case "email":
        if (!EMAIL.test(v)) return { error: "is not a valid email address" };
        break;
      case "multiline":
        if ((v.match(/https?:\/\//gi) || []).length > 3) return { error: "contains too many links" };
        if (/[<>]/.test(v)) return { error: "contains characters that are not allowed" };
        break;
      case "enum":
      case "enum-multi":
        if (!(SCHEMA.options[name] || []).includes(v)) return { error: "is not one of the offered options" };
        break;
    }
    if (!out.includes(v)) out.push(v);
  }
  return { value: multi ? out.join(";") : (out[0] || "") };
}
function validate(intent, fields) {
  const spec = SCHEMA.intents[intent], errors = [], cleaned = {};
  const allowed = new Set([...spec.required, ...spec.optional]);
  let consent = false;
  for (const name of Object.keys(fields)) {
    if (name === HONEYPOT) continue;
    if (name === CONSENT) { consent = fields[name] === "true"; continue; }
    if (!allowed.has(name)) { errors.push({ field: name, reason: "is not a field on this form" }); continue; }
    const r = validateOne(name, fields[name]);
    if (r.error) errors.push({ field: name, reason: r.error });
    else if (r.value) cleaned[name] = r.value;
  }
  for (const name of spec.required) if (!cleaned[name] && !errors.some(e => e.field === name)) errors.push({ field: name, reason: "is required" });
  if (spec.consent && !consent) errors.push({ field: CONSENT, reason: "please tick the consent box" });
  return { errors, cleaned };
}
async function turnstileOk(env, token, ip) {
  if (!env.TURNSTILE_SECRET) { console.log("turnstile: not configured, skipping"); return true; }
  if (!token || typeof token !== "string" || token.length > 2048) return false;
  const body = new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token });
  if (ip) body.set("remoteip", ip);
  try {
    const r = await fetch(TURNSTILE_VERIFY, { method: "POST", body, signal: AbortSignal.timeout(8000) });
    const d = await r.json();
    if (!d.success) console.log("turnstile: rejected", JSON.stringify(d["error-codes"] || []));
    return !!d.success;
  } catch (e) { console.log("turnstile: verify failed", String(e)); return false; }
}
function cookieValue(request, name) {
  const m = (request.headers.get("Cookie") || "").match("(?:^|; )" + name + "=([^;]*)");
  try { return m ? decodeURIComponent(m[1]) : ""; } catch (e) { return ""; }
}

async function handleForm(request, env, url, intent) {
  if (request.method !== "POST") return json(405, { ok: false, code: "method" }, { Allow: "POST" });
  if (!Object.prototype.hasOwnProperty.call(SCHEMA.intents, intent)) return json(404, { ok: false, code: "intent" });
  const production = hostList(env).includes(url.hostname);
  // same-origin browser posts only: the Origin header must be this address (or https:// on a production host),
  // and Sec-Fetch-Site, when the browser sends it, must say same-origin
  const origin = request.headers.get("Origin"), sfs = request.headers.get("Sec-Fetch-Site");
  const origins = [url.origin, ...hostList(env).map(h => "https://" + h)];
  if (!origins.includes(origin) || (sfs && sfs !== "same-origin")) return json(403, { ok: false, code: "origin" });
  if (!(request.headers.get("Content-Type") || "").toLowerCase().startsWith("application/json")) return json(415, { ok: false, code: "content_type" });
  const len = Number(request.headers.get("Content-Length") || 0);
  if (len > MAX_BODY) return json(413, { ok: false, code: "too_large" });
  const text = await request.text();
  if (text.length > MAX_BODY) return json(413, { ok: false, code: "too_large" });
  let body; try { body = JSON.parse(text); } catch (e) { return json(400, { ok: false, code: "json" }); }
  if (!body || typeof body !== "object") return json(400, { ok: false, code: "json" });
  const ip = request.headers.get("CF-Connecting-IP") || "";
  // soft guard: the counters are per Cloudflare machine; Turnstile (a fresh token per post) is the real one
  if (env.RL_GLOBAL && !(await env.RL_GLOBAL.limit({ key: "forms" })).success) return json(429, { ok: false, code: "rate_limited", retryAfter: 60 }, { "Retry-After": "60" });
  if (env.RL_INTENT && !(await env.RL_INTENT.limit({ key: intent + ":" + ip })).success) return json(429, { ok: false, code: "rate_limited", retryAfter: 60 }, { "Retry-After": "60" });
  const fields = body.fields && typeof body.fields === "object" && !Array.isArray(body.fields) ? body.fields : {};
  if (fields[HONEYPOT]) { console.log("honeypot: dropped", intent); return json(200, { ok: true }); }
  if (!(await turnstileOk(env, body.turnstile, ip))) return json(403, { ok: false, code: "turnstile" });
  const { errors, cleaned } = validate(intent, fields);
  if (errors.length) return json(400, { ok: false, code: "validation", errors });

  const guid = env[SCHEMA.intents[intent].hubspotVar];
  if (!guid || !env.HS_PORTAL) { console.log("hubspot: form not configured", intent); return json(503, { ok: false, code: "not_configured" }); }
  const page = body.page && typeof body.page === "object" ? body.page : {};
  const pageUri = typeof page.uri === "string" && page.uri.startsWith(origin + "/") ? page.uri.split("#")[0].slice(0, 500) : origin + "/";
  const pageName = (production ? "" : TEST_PREFIX) + clean(page.title || "").slice(0, 200);
  const hsFields = Object.entries(cleaned).map(([name, value]) => ({ objectTypeId: "0-1", name, value }));
  const payload = { submittedAt: Date.now(), fields: hsFields, context: { pageUri, pageName } };
  const hutk = production ? cookieValue(request, "hubspotutk") : "";
  if (hutk && /^[0-9a-f]{32}$/.test(hutk)) payload.context.hutk = hutk;
  if (IP.test(ip)) payload.context.ipAddress = ip;
  if (SCHEMA.intents[intent].consent && env.CONSENT_FORWARD === "hubspot") {
    hsFields.push({ objectTypeId: "0-1", name: CONSENT, value: "true" });
    hsFields.push({ objectTypeId: "0-1", name: "website_consent_text_version", value: env.CONSENT_TEXT_VERSION || "" });
    hsFields.push({ objectTypeId: "0-1", name: "website_consent_timestamp", value: new Date().toISOString() });
    payload.legalConsentOptions = { consent: { consentToProcess: true, text: env.CONSENT_TEXT || "", communications: [] } };
  }
  let r;
  try {
    r = await fetch((env.HS_SUBMIT_URL || HUBSPOT) + env.HS_PORTAL + "/" + guid, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: AbortSignal.timeout(10000)
    });
  } catch (e) { console.log("hubspot: unreachable", String(e)); return json(502, { ok: false, code: "hubspot" }); }
  if (r.ok) return json(200, { ok: true });
  let detail = {}; try { detail = await r.json(); } catch (e) {}
  console.log("hubspot: rejected", intent, r.status, JSON.stringify(detail).slice(0, 500));
  if (r.status >= 400 && r.status < 500) return json(400, { ok: false, code: "upstream", errors: (detail.errors || []).map(e => ({ field: "", reason: e.errorType || "rejected" })) });
  return json(502, { ok: false, code: "hubspot" });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      const m = url.pathname.match(/^\/api\/forms\/([a-z_]{1,32})\/?$/);
      if (m) {
        const res = await handleForm(request, env, url, m[1]);
        // on staging and version previews only: which guards this deployment actually has
        if (!hostList(env).includes(url.hostname)) {
          res.headers.set("X-Adeahub-Guards", "ratelimit=" + (env.RL_INTENT && env.RL_GLOBAL ? "on" : "off") + "; turnstile=" + (env.TURNSTILE_SECRET ? "on" : "off") + "; consent-forward=" + (env.CONSENT_FORWARD || "off"));
        }
        return res;
      }
      if (url.pathname === "/api/csp-report") {
        if (request.method !== "POST") return json(405, { ok: false }, { Allow: "POST" });
        const t = await request.text();
        console.log("csp-report", t.slice(0, 2000));
        return new Response(null, { status: 204 });
      }
      return json(404, { ok: false, code: "not_found" });
    }
    return env.ASSETS.fetch(request);
  }
};
