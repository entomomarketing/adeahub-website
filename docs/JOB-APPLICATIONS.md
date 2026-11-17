# Job applications on the adeahub website

The careers page (`/careers/`, added 2026-11-17) invites open applications: there are no role pages yet. The
page is the site's own; the application form on it is a HubSpot form, embedded and given the site's look by
`public/assets/js/job-apply.js`. This is the same approach as the entomo website's role pages.

**Why this form is embedded and the other three are not.** The contact, demo and newsletter forms go through the
site's Worker (`docs/FORMS-AND-SECURITY.md`). An application carries a CV, and HubSpot's form-submission API does
not accept files; HubSpot's own embedded form does. A side benefit: the form's fields are edited in HubSpot, with
no change to the site.

**Status: the form is not connected yet.** `FORM_ID` in `job-apply.js` is empty, so the page shows "Online
applications open shortly" and sends people to the contact page (enquiry type Careers). Nothing from HubSpot loads
until the ID is set. To connect it, do the one-time setup below and put the form ID in `FORM_ID`.

## One-time setup in HubSpot (portal 243938139, the adeahub account)

### 1. Contact properties (Settings > Properties > Contact properties > Create property)

Create them in a group such as "Job applications". Use exactly these **internal names**: the page writes to the
last four, and the same names are used on the entomo site, so role pages can be added later without new properties.

| label | internal name | field type | notes |
|---|---|---|---|
| CV | `cv_file` | File | one file |
| Cover letter | `cover_letter_file` | File | one file |
| Area of interest | `job_area_of_interest` | Dropdown select | options: Engineering; Product; Delivery and implementation; Support services; Commercial; Finance, legal and marketing; Other (the areas the careers page lists) |
| Note from the applicant | `application_message` | Multi-line text | |
| Role applied for | `job_applied_for` | Single-line text | filled by the page: "Open application" |
| Role slug | `job_slug` | Single-line text | filled by the page: `open-application` |
| Role location | `job_location` | Single-line text | filled by the page (empty for open applications) |
| Application source | `application_source` | Single-line text | filled by the page; starts with `[TEST: staging]` for tests |

Existing properties reused: First name, Last name, Email, Phone number, City, Country/Region, LinkedIn URL.

### 2. The form (Marketing > Forms)

The quickest reliable route is to **clone the existing "Talk To Us" form** and change its fields: a clone is the
same kind of form as the two the live site already embeds, which is the kind this embed is tested with. Name it
**Job application**.

| field | required | layout |
|---|---|---|
| First name, Last name | yes | side by side |
| Email, Phone number | yes | side by side |
| City, Country/Region | no | side by side |
| LinkedIn URL | no | |
| Area of interest (`job_area_of_interest`) | no | |
| CV (`cv_file`) | **yes** | help text: "PDF or Word, up to 10 MB" |
| Cover letter (`cover_letter_file`) | no | |
| Note from the applicant (`application_message`) | no | label: "Anything you would like us to know" |
| Role applied for, Role slug, Role location, Application source | hidden | toggle "Make this field hidden" |

Options:

- **Consent:** turn on the consent checkbox ("Notice and consent"), required, with the text *"I agree to adeahub
  processing the details I have entered to consider me for roles."* The other forms on the site ask for the same
  consent.
- **Submit button:** "Submit application".
- **After submit:** an inline thank-you message, for example "Thank you for applying. Our talent team will review
  your application and contact you if there is a match."
- **Pre-populate fields with known values:** off (people apply from shared computers).
- **Spam protection (CAPTCHA):** on. The site's Turnstile check covers only the Worker's forms, not this one. The
  site's security policy already allows reCAPTCHA's hosts.
- **Set contacts as marketing contacts:** off, so applicants do not count against the marketing-contact tier.
- **Notifications:** send submission notifications to the talent team's inbox.
- **Style:** leave HubSpot's defaults. The page replaces them: Outfit, the site's input and button styles, two
  columns for side-by-side fields, a dashed upload area (`FORM_CSS` in `job-apply.js`).

Publish, open **Share > Embed code**, and copy the form ID (the `formId` value, a GUID).

### 3. Trusted domains

Settings > Tracking & Analytics > Tracking code > Advanced > Site domains: add
`staging-adeahub.misty-dawn-f588.workers.dev`, `adeahub.misty-dawn-f588.workers.dev` and `adeahub.co`.
HubSpot can mark submissions from domains that are not listed as spam.

### 4. Connect it

Put the form ID in `FORM_ID` at the top of `public/assets/js/job-apply.js`, run `python3 tools/build.py` (the
script link carries a version hash), commit to `staging`, and submit one test application on the staging address
(with the owner's go-ahead: it creates a contact). Check that the CV arrives, that the four hidden fields are
filled, and that the thank-you message shows. Delete the test contact afterwards.

## How it works on the page

- The page holds `<div id="job-apply-form" data-job-title="Open application" data-job-slug="open-application"
  data-job-location="">` with the fallback inside it. `tools/build.py` adds the script tag to any page that has
  this element.
- With a `FORM_ID`, the script shows a loading placeholder, loads HubSpot's embed
  (`https://js-na2.hsforms.net/forms/embed/v2.js`, `hbspt.forms.create`), and HubSpot draws the form in an iframe
  it writes into the element. The iframe is same-origin, so the script adds the site's styles to it and fills the
  four hidden fields. If the embed does not arrive within 15 seconds, the fallback comes back.
- Submissions from anywhere but adeahub.co and the workers.dev production address are marked
  `[TEST: staging]` in `application_source`.
- Every accepted application pushes `{ event: "hs_form_success", form_intent: "job_application", job_slug, job_title,
  job_location }` to the dataLayer for Tag Manager.
- The Content-Security-Policy (report-only) in `public/_headers` allows `*.hsforms.net` (script), `*.hsforms.com`
  (form data, submission) and `www.gstatic.com` (reCAPTCHA).

## How applications appear in HubSpot

- Each application is a submission on the contact (Marketing > Forms > Job application > Submissions), with the CV
  and cover letter as file links.
- A contact who applies twice keeps both submissions on the timeline; the contact properties show the latest.
- Test applications: `application_source` starts with `[TEST: staging]`.

## Copy on the careers page

The page states only what the site already says elsewhere: the verified figures (35M+ users, 8,500+ health
facilities, 200M+ patient records, 17+ locations, 25+ years), the five core values from the About page, and the
team areas visible in the About page's team titles. The three "What happens next" steps and the line about how
application details are used were written for this page and should be confirmed by whoever owns hiring.

## Later: posting roles

The entomo website generates one page per role from a JSON file per role (`tools/jobs/` in its repository), each
embedding this same HubSpot form with the role in the hidden fields, plus job-posting structured data for Google.
The same model fits here: role pages would set `data-job-title`, `data-job-slug` and `data-job-location` on their
own `#job-apply-form` element, and the careers page would list them above the open application.
