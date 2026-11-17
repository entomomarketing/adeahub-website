/* adeahub job application form: the HubSpot "Job application" form, embedded on the careers page.
   The page gives <div id="job-apply-form" data-job-title data-job-slug data-job-location> holding the fallback
   (a route through the contact page). HubSpot renders the form (with the CV upload) inside that element; this
   script only:
   - swaps the fallback for the form once FORM_ID is set (empty FORM_ID = the fallback stays, nothing loads),
   - gives the form the site's look (HubSpot draws it in an iframe the page's own CSS cannot reach),
   - tells the form what the application is for, through its hidden fields,
   - marks submissions from anywhere but production as tests,
   - pushes hs_form_success to the dataLayer for Tag Manager conversion triggers.

   Why HubSpot's own form and not the Worker (src/worker.js) like the other forms: an application carries a CV,
   and HubSpot's form-submission API does not accept files; its embedded form does. Same approach as the entomo
   website. The form is created in HubSpot, so its fields can be changed there without touching the site.
   Setup and the field list: docs/JOB-APPLICATIONS.md. */
(function () {
  "use strict";
  // ---- the only settings. FORM_ID is the form's ID in HubSpot (Share > Embed code).
  var PORTAL_ID = "243938139";
  var REGION = "na2";
  var FORM_ID = "";   // HubSpot "Job application" form; empty = the page keeps its fallback
  var EMBED_SCRIPT = "https://js-na2.hsforms.net/forms/embed/v2.js";
  var PRODUCTION_HOSTS = ["adeahub.co", "www.adeahub.co", "adeahub.misty-dawn-f588.workers.dev"];
  // ----

  var box = document.getElementById("job-apply-form");
  if (!box || !FORM_ID) return;
  var job = {
    title: box.getAttribute("data-job-title") || "",
    slug: box.getAttribute("data-job-slug") || "",
    location: box.getAttribute("data-job-location") || ""
  };
  var isTest = PRODUCTION_HOSTS.indexOf(location.hostname) === -1;
  var fallbackHtml = box.innerHTML;

  function fallback(message) {
    box.innerHTML = fallbackHtml;
    var note = box.querySelector("[data-job-fallback-title]");
    if (note && message) note.textContent = message;
  }

  // HubSpot contact properties filled by the page (hidden fields on the form; see docs/JOB-APPLICATIONS.md)
  var hidden = {
    job_applied_for: job.title + (job.location ? " (" + job.location + ")" : ""),
    job_slug: job.slug,
    job_location: job.location,
    application_source: (isTest ? "[TEST: staging] " : "") + "website " + location.hostname
  };

  // The site's form look, for the document HubSpot draws the form in. Colours and sizes mirror .form-input,
  // .form-consent and the submit buttons of the contact and demo forms.
  var FONT = location.origin + "/assets/fonts/outfit-latin.woff2";
  var FORM_CSS = [
    '@font-face{font-family:"Outfit";font-weight:100 900;font-display:swap;src:url("' + FONT + '") format("woff2");}',
    'html,body{margin:0;padding:0;background:transparent;}',
    // !important throughout the controls: a HubSpot form theme adds its own, more specific rules for fonts and buttons
    'body,form,form *,.submitted-message,.submitted-message *{font-family:"Outfit",ui-sans-serif,system-ui,sans-serif!important;box-sizing:border-box;}',
    '.hs-form{color:#374151;-webkit-font-smoothing:antialiased;}',
    '.hs-form fieldset{max-width:none!important;border:0;margin:0;padding:0;}',
    '.hs-form fieldset.form-columns-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 24px;}',
    '.hs-form fieldset.form-columns-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 24px;}',
    '.hs-form fieldset .hs-form-field{width:auto!important;float:none!important;}',
    '.hs-form .input{margin:0!important;}',
    '@media (max-width:419px){.hs-form fieldset.form-columns-2,.hs-form fieldset.form-columns-3{grid-template-columns:minmax(0,1fr);}}',
    '.hs-form-field{margin:0 0 22px;}',
    '.hs-form-field>label,.hs-form-field>label span{font-size:15px!important;line-height:22px!important;font-weight:600!important;color:#374151!important;}',
    '.hs-form-field>label{display:block;margin:0 0 8px;}',
    '.hs-form-field>label .hs-form-required{color:#186BDC!important;margin-left:3px;}',
    '.hs-form legend.hs-field-desc{display:block;margin:-4px 0 8px;padding:0;font-size:13.5px;line-height:20px;font-weight:400;color:#6B6B6B;}',
    '.hs-form input[type=text],.hs-form input[type=email],.hs-form input[type=tel],.hs-form input[type=number],.hs-form input[type=url],.hs-form select,.hs-form textarea{width:100%!important;height:auto!important;min-height:49px;margin:0;padding:12px 16px!important;font-size:15.2px!important;line-height:22px!important;color:#111827!important;background-color:#FAFAFA!important;border:1.5px solid #E5E7EB!important;border-radius:12px!important;outline:none;transition:border-color .2s,box-shadow .2s,background .2s;-webkit-appearance:none;appearance:none;}',
    '.hs-form select{height:auto!important;min-height:49px;padding-right:44px;cursor:pointer;background-repeat:no-repeat;background-position:right 16px center;background-size:16px;background-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%236B7280\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpath d=\'m6 9 6 6 6-6\'/%3E%3C/svg%3E");}',
    '.hs-form textarea{min-height:112px!important;resize:vertical;}',
    '.hs-form input::placeholder,.hs-form textarea::placeholder{color:#9CA3AF;}',
    '.hs-form input:focus,.hs-form select:focus,.hs-form textarea:focus{border-color:#5298F8!important;background-color:#fff!important;box-shadow:0 0 0 3px rgba(82,152,248,.12);}',
    '.hs-form input.invalid,.hs-form input.error,.hs-form select.invalid,.hs-form select.error,.hs-form textarea.invalid,.hs-form textarea.error{border-color:#DC2626!important;}',
    // the CV and cover-letter uploads: a dashed drop area with a button-like chooser
    '.hs-form input[type=file]{display:block;width:100%!important;height:auto!important;min-height:66px;padding:14px 16px!important;font-size:14px!important;line-height:36px!important;color:#4B5563!important;background:#F8FAFD!important;border:1.5px dashed #C9D8EE!important;border-radius:12px!important;cursor:pointer;transition:border-color .2s,background .2s;}',
    '.hs-form input[type=file]:hover,.hs-form input[type=file]:focus{border-color:#5298F8!important;background:#F3F8FF!important;outline:none;}',
    '.hs-form input[type=file]::file-selector-button{height:36px;margin:0 14px 0 0;padding:0 16px;font:inherit;font-size:14px;line-height:34px;font-weight:600;color:#186BDC;background:#fff;border:1px solid #C9D8EE;border-radius:9999px;cursor:pointer;}',
    '.hs-form ul.inputs-list{list-style:none;margin:0;padding:0;}',
    '.hs-form ul.inputs-list li{margin:0 0 8px;}',
    '.hs-form ul.inputs-list label,.hs-form ul.inputs-list label span{font-size:14px!important;line-height:21px!important;font-weight:400!important;color:#4B5563!important;}',
    '.hs-form ul.inputs-list label{display:block;position:relative;margin:0;padding-left:30px;cursor:pointer;}',
    '.hs-form ul.inputs-list label .hs-form-required{color:#186BDC!important;margin-left:3px;}',
    '.hs-form ul.inputs-list input[type=checkbox],.hs-form ul.inputs-list input[type=radio]{position:absolute;left:0;top:2px;width:17.6px!important;height:17.6px!important;min-height:0;margin:0;padding:0!important;accent-color:#5298F8;cursor:pointer;-webkit-appearance:auto;appearance:auto;}',
    '.hs-form .legal-consent-container,.hs-form .hs-richtext{font-size:14px;line-height:21px;color:#4B5563;}',
    '.hs-form .legal-consent-container .hs-form-booleancheckbox-display>span{margin-left:0!important;}',
    '.hs-form .hs-richtext p{margin:0 0 12px;}',
    '.hs-form a{color:#186BDC;text-decoration:underline;text-underline-offset:2px;}',
    '.hs-form ul.hs-error-msgs{list-style:none;margin:6px 0 0;padding:0;}',
    '.hs-form ul.hs-error-msgs label,.hs-form ul.hs-error-msgs label span,.hs-form .hs-error-msg{display:block;padding-left:0!important;font-size:13.5px!important;line-height:20px!important;font-weight:500!important;color:#DC2626!important;cursor:default;}',
    '.hs-form .hs_error_rollup{margin:0 0 14px;padding:10px 14px;border-radius:12px;background:#FEF2F2;}',
    '.hs-form .hs-submit{margin:6px 0 0;}',
    '.hs-form .hs-submit .actions{margin:0;padding:0;}',
    '.hs-form input[type=submit],.hs-form .hs-button{width:100%!important;height:auto!important;margin:0;padding:16px 32px!important;font-size:18px!important;line-height:28px!important;font-weight:700!important;letter-spacing:0!important;text-transform:none!important;color:#fff!important;text-align:center;background:#5298F8!important;border:0!important;border-radius:12px!important;cursor:pointer;box-shadow:0 8px 26px rgba(82,152,248,.30);transition:transform .25s cubic-bezier(.16,1,.3,1),box-shadow .25s cubic-bezier(.16,1,.3,1),background .2s;-webkit-appearance:none;appearance:none;}',
    '.hs-form input[type=submit]:hover,.hs-form .hs-button:hover{background:#3d89f5!important;transform:translateY(-2px);box-shadow:0 12px 30px -8px rgba(82,152,248,.55);}',
    '.hs-form input[type=submit]:focus-visible,.hs-form .hs-button:focus-visible{outline:3px solid rgba(82,152,248,.45);outline-offset:3px;}',
    '.submitted-message{padding:8px 0;font-family:"Outfit",ui-sans-serif,system-ui,sans-serif;font-size:18px;line-height:28px;color:#111827;text-align:center;}',
    '.submitted-message p{margin:0 0 8px;}',
    '@media (prefers-reduced-motion:reduce){.hs-form *{transition:none!important;}}'
  ].join("");

  function frameDoc() {
    var iframe = box.querySelector("iframe.hs-form-iframe, iframe[id^='hs-form-iframe']");
    try { return iframe && (iframe.contentDocument || iframe.contentWindow.document); } catch (e) { return null; }
  }
  function formRoot(form) {
    // onFormReady hands over a jQuery-like object whose querySelector may not reach the fields, so the iframe's
    // own document is the reliable root; the passed form is used only when it truly holds them
    var doc = frameDoc(), inner = doc && doc.querySelector("form");
    if (inner) return inner;
    if (form && form.querySelector && form.querySelector("input, select, textarea")) return form;
    return null;
  }
  function styleForm(doc) {
    // the page's stylesheet cannot cross into the iframe, so the look is added to the iframe document itself;
    // without an iframe (a raw-HTML form) the same rules go into the page
    try {
      doc = doc || document;
      if (doc.getElementById("adeahub-form-css")) return;
      var style = doc.createElement("style");
      style.id = "adeahub-form-css";
      style.textContent = FORM_CSS;
      (doc.head || doc.documentElement).appendChild(style);
    } catch (e) { if (window.console) console.warn("job form: could not style the form", e); }
  }
  function fill(form) {
    var root = formRoot(form);
    if (!root) return false;                                         // not ready yet; the caller retries
    styleForm(root.ownerDocument);
    Object.keys(hidden).forEach(function (name) {
      var field = root.querySelector('input[name="' + name + '"], textarea[name="' + name + '"]');
      if (!field) { if (window.console) console.warn("job form: no hidden field named", name); return; }
      field.value = hidden[name];
      field.dispatchEvent(new Event("input", { bubbles: true }));    // HubSpot reads the value on input/change
      field.dispatchEvent(new Event("change", { bubbles: true }));
    });
    return true;
  }

  function create() {
    window.hbspt.forms.create({
      region: REGION,
      portalId: PORTAL_ID,
      formId: FORM_ID,
      target: "#job-apply-form",
      cssClass: "job-hs-form",
      css: "",                                    // drop HubSpot's default stylesheet; FORM_CSS replaces it
      formInstanceId: job.slug || "job",
      onFormReady: function ($form) {
        var form = $form && $form.length ? $form[0] : $form;         // this embed may hand over a jQuery object
        var loading = box.querySelector(".job-form-loading");
        if (loading) loading.remove();
        box.classList.add("is-ready");
        var tries = 0;
        (function attempt() {
          if (fill(form) || ++tries > 10) return;                    // up to ~5s, then give up quietly
          setTimeout(attempt, 500);
        })();
      },
      onFormSubmitted: function () {
        try {
          (window.dataLayer = window.dataLayer || []).push({
            event: "hs_form_success", form_intent: "job_application", form_id: FORM_ID,
            job_slug: job.slug, job_title: job.title, job_location: job.location
          });
        } catch (e) {}
        box.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  }

  // the form is on its way: show a quiet placeholder until HubSpot has drawn it
  box.innerHTML = '<div class="job-form-loading" role="status"><span></span><span></span><span></span><span class="sr-only">Loading the application form</span></div>';
  var s = document.createElement("script");
  s.src = EMBED_SCRIPT;
  s.charset = "utf-8";
  s.onload = function () {
    try { create(); } catch (e) {
      if (window.console) console.error("job form: embed failed", e);
      fallback("The application form did not load");
    }
  };
  s.onerror = function () { fallback("The application form did not load"); };
  document.body.appendChild(s);
  // if HubSpot never calls back (blocked script, network), return to the fallback instead of an endless placeholder
  setTimeout(function () { if (!box.classList.contains("is-ready") && box.querySelector(".job-form-loading")) fallback("The application form did not load"); }, 15000);
})();
