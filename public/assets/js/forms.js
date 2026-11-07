/* adeahub website forms. Binds every <form data-form="<intent>"> (contact, demo, subscribe; the schema is
   src/forms.json) and posts it as JSON to this site's own Worker, POST /api/forms/<intent> (src/worker.js), which
   validates it again, checks the Cloudflare Turnstile token and forwards it to HubSpot.

   Markup a form needs (tools/build.py checks it): field names = HubSpot internal names; the honeypot
   <input name="hs_website"> inside .hp-field; the consent checkbox name="website_consent_given" value="true" required;
   an empty <div class="form-turnstile"></div>; <p class="form-status" role="alert" hidden></p>.
   On success the form dispatches "form:success" (detail: { intent, fields }) for the page to show its thank-you
   state; a form with data-done="label" instead just relabels its button. See docs/FORMS-AND-SECURITY.md. */
(function () {
  "use strict";
  var API_PATH = "/api/forms/";
  var TURNSTILE_SITEKEY = "0x4AAAAAAF3qGiiQuD1YmC8L";   // public site key of the "adeahub-website-forms" Turnstile widget (2026-11-07); empty = no challenge shown
  var TURNSTILE_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
  var INTENTS = { contact: 1, demo: 1, subscribe: 1 };
  // the same limits the Worker enforces, applied as maxlength so the browser stops the visitor first
  var LIMITS = { firstname: 100, lastname: 100, email: 254, company: 150, jobtitle: 150, message: 2000 };
  var HONEYPOT = "hs_website";
  var FALLBACK = "hello@adeahub.co";
  // C0/C1 controls, zero-width characters, Unicode line separators, bidi overrides (mirrors src/worker.js)
  var CONTROL = /[\u0000-\u0008\u000B-\u001F\u007F-\u009F\u200B-\u200D\uFEFF\u2028\u2029\u202A-\u202E\u2066-\u2069]/g;

  function tidy(value, multiline) {
    var v = String(value == null ? "" : value).replace(CONTROL, "");
    if (multiline) return v.replace(/\r\n?/g, "\n").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
    return v.replace(/\s+/g, " ").trim();
  }

  // { name: value | [values] }: only the fields the page's own markup declared (other scripts, such as the
  // Turnstile widget, add inputs to forms, and the Worker refuses unknown field names)
  function collect(form) {
    var out = {};
    function add(name, value, multiline) {
      var v = tidy(value, multiline);
      if (!v && name !== HONEYPOT) return;
      if (name in out) { if (!Array.isArray(out[name])) out[name] = [out[name]]; out[name].push(v); }
      else out[name] = v;
    }
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled || !form.formNames[el.name]) return;
      if (el.closest && el.closest(".form-turnstile")) return;
      if (el.type === "submit" || el.type === "button" || el.type === "reset") return;
      if (el.type === "checkbox" || el.type === "radio") { if (el.checked) add(el.name, el.value); return; }
      if (el.tagName === "SELECT") {
        var o = el.options[el.selectedIndex];
        add(el.name, o && !o.disabled ? (o.hasAttribute("value") ? o.value : o.text) : "");
        return;
      }
      add(el.name, el.value, el.tagName === "TEXTAREA");
    });
    if (!(HONEYPOT in out)) out[HONEYPOT] = "";
    return out;
  }

  function statusEl(form) { return form.querySelector(".form-status"); }
  function submitButton(form) { return form.querySelector('[type="submit"]'); }
  function showStatus(form, html, isInfo) {
    var st = statusEl(form);
    if (!st) return;
    st.innerHTML = html; st.hidden = false;
    st.classList.toggle("is-info", !!isInfo);
  }
  function clearStatus(form) { var st = statusEl(form); if (st) { st.hidden = true; st.textContent = ""; delete st.dataset.turnstile; } }

  function track(form) {
    try { (window.dataLayer = window.dataLayer || []).push({ event: "hs_form_success", form_intent: form.dataset.form }); } catch (e) {}
  }
  function succeed(form, fields) {
    form.classList.add("is-sent");
    if (form.dataset.done) {
      var btn = submitButton(form);
      if (btn) { btn.textContent = form.dataset.done; btn.disabled = true; }
      Array.prototype.forEach.call(form.querySelectorAll("input:not([type=hidden]):not([type=checkbox])"), function (i) { i.value = ""; });
      showStatus(form, "Thank you. You are subscribed.", true);
    }
    form.dispatchEvent(new CustomEvent("form:success", { bubbles: true, detail: { intent: form.dataset.form, fields: fields } }));
  }

  function hubspotMessage(type) {
    if (type === "INVALID_EMAIL") return "Please check the email address and try again.";
    if (type === "BLOCKED_EMAIL") return "Please use your work email address.";
    if (type === "REQUIRED_FIELD") return "Please fill in every required field.";
    return "";
  }
  function label(form, name) {
    var el = form.elements[name];
    if (el && el.id) { var l = form.querySelector('label[for="' + el.id + '"]'); if (l) return l.textContent.replace(/[*()]|Optional/g, "").trim(); }
    return name.replace(/_/g, " ");
  }
  function fail(form, err) {
    var mail = '<a href="mailto:' + FALLBACK + '">' + FALLBACK + "</a>";
    var msg = "Something went wrong and nothing was sent. Please try again, or email " + mail + ".";
    var code = err && err.code;
    if (code === "validation") {
      var first = null, errs = err.errors || [];
      errs.forEach(function (e) {
        var el = e.field && form.elements[e.field];
        if (el && el.setCustomValidity) { el.setCustomValidity(e.reason); if (!first) first = el; }
      });
      msg = errs.length ? "Please check " + label(form, errs[0].field) + ": " + errs[0].reason + "." : "Please check the form and try again.";
      if (first && form.reportValidity) form.reportValidity();
    } else if (code === "turnstile") { msg = "The security check did not pass. Please try again."; resetTurnstile(form); }
    else if (code === "rate_limited") msg = "Too many attempts from this connection. Please try again in a minute.";
    else if (code === "upstream") msg = (err.errors && err.errors.length && hubspotMessage(err.errors[0].reason)) || msg;
    else if (code === "not_configured") msg = "This form is not taking submissions yet. Please email " + mail + ".";
    showStatus(form, msg);
    if (window.console && console.warn) console.warn("form submission failed", err);
  }

  // ---- Turnstile: loaded on the first focus of a form, one widget per form, token read at submit
  var turnstileLoading = false, turnstileReady = [];
  function loadTurnstile(cb) {
    if (!TURNSTILE_SITEKEY || window.turnstile) { cb(); return; }
    turnstileReady.push(cb);
    if (turnstileLoading) return;
    turnstileLoading = true;
    var s = document.createElement("script"); s.src = TURNSTILE_SRC; s.async = true; s.defer = true;
    s.onload = function () { turnstileReady.splice(0).forEach(function (f) { f(); }); };
    s.onerror = function () { document.querySelectorAll("form[data-form]").forEach(function (f) { showStatus(f, "The security check could not load. Please refresh the page and try again."); }); };
    document.head.appendChild(s);
  }
  function renderTurnstile(form) {
    if (!TURNSTILE_SITEKEY || form.turnstileId != null) return;
    var slot = form.querySelector(".form-turnstile");
    if (!slot || !window.turnstile) return;
    form.turnstileId = window.turnstile.render(slot, {
      sitekey: TURNSTILE_SITEKEY, theme: "light", size: "flexible", action: form.dataset.form,
      callback: function () { var st = statusEl(form); if (st && st.dataset.turnstile) clearStatus(form); },
      "error-callback": function () { showStatus(form, "The security check could not load. Please refresh the page and try again."); var st = statusEl(form); if (st) st.dataset.turnstile = "1"; }
    });
  }
  function turnstileToken(form) {
    if (!TURNSTILE_SITEKEY || form.turnstileId == null || !window.turnstile) return "";
    try { return window.turnstile.getResponse(form.turnstileId) || ""; } catch (e) { return ""; }
  }
  function resetTurnstile(form) {
    if (form.turnstileId != null && window.turnstile) { try { window.turnstile.reset(form.turnstileId); } catch (e) {} }
  }

  function send(form) {
    var btn = submitButton(form), labelHtml = btn ? btn.innerHTML : "";
    if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
    clearStatus(form);
    var fields = collect(form);
    var body = { fields: fields, turnstile: turnstileToken(form), page: { uri: location.href.split("#")[0], title: document.title } };
    fetch(API_PATH + form.dataset.form, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), credentials: "same-origin" })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) { if (!r.ok) throw data; return data; });
      })
      .then(function () {
        if (btn && !form.dataset.done) { btn.innerHTML = labelHtml; btn.disabled = false; }
        track(form); succeed(form, fields);
      })
      .catch(function (err) {
        if (btn) { btn.disabled = false; btn.innerHTML = labelHtml; }
        resetTurnstile(form);
        fail(form, err);
      });
  }

  function bind(form) {
    if (!INTENTS[form.dataset.form]) return;
    form.formNames = {};
    Array.prototype.forEach.call(form.elements, function (el) { if (el.name) form.formNames[el.name] = true; });
    form.setAttribute("novalidate", "");   // validity is reported by reportValidity() on submit, with our own messages
    Object.keys(LIMITS).forEach(function (n) {
      var el = form.elements[n];
      if (el && el.setAttribute && !el.getAttribute("maxlength")) el.setAttribute("maxlength", String(LIMITS[n]));
    });
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.setCustomValidity) el.addEventListener("input", function () { el.setCustomValidity(""); });
      if (el.setCustomValidity && el.type === "checkbox") el.addEventListener("change", function () { el.setCustomValidity(""); });
    });
    if (TURNSTILE_SITEKEY) {
      var armed = false;
      form.addEventListener("focusin", function () { if (armed) return; armed = true; loadTurnstile(function () { renderTurnstile(form); }); });
    }
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (form.classList.contains("is-sent") && form.dataset.done) return;
      if (typeof form.reportValidity === "function" && !form.reportValidity()) return;
      if (TURNSTILE_SITEKEY && !turnstileToken(form)) {
        showStatus(form, "Please complete the security check first.", true);
        var st = statusEl(form); if (st) st.dataset.turnstile = "1";
        loadTurnstile(function () { renderTurnstile(form); });
        return;
      }
      send(form);
    });
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll("form[data-form]"), bind); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
