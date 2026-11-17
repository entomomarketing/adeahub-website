# The careers page and its form

`/careers/` (added 2026-11-17) invites people to introduce themselves. There are no role pages and the page
makes no promise that roles will open. It exists only in this repository: adeahub.co has no careers page.

## The form ("Introduce yourself")

The page has its own form, `<form data-form="careers">`, sent the same way as the contact, demo and newsletter
forms: `public/assets/js/forms.js` posts it to the site's Worker (`POST /api/forms/careers`), which applies every
check described in `docs/FORMS-AND-SECURITY.md` (origin, rate limit, honeypot, Turnstile, consent, field
validation) and forwards it to HubSpot. On success the page shows its thank-you panel.

| field | name | required | checked as |
|---|---|---|---|
| First name, Last name | `firstname`, `lastname` | yes | names |
| Email | `email` | yes | email address |
| Phone | `phone` | no | digits, spaces, `+ ( ) - .`, at least six digits |
| Where you work or study now | `company` | yes | text |
| Area of interest | `job_area` | no | one of the seven areas in `src/forms.json` |
| Where you are based | `region` | no | one of the Contact form's three regions |
| LinkedIn profile | `linkedin_url` | no | web address; `https://` is added if it was left out |
| Link to your CV or portfolio | `cv_url` | no | web address, as above |
| About you | `about` | yes | up to 1,500 characters, at most three links |

**Where it arrives in HubSpot.** HubSpot has no job-application form, so the Worker delivers this form through the
existing **Contact** form (`HS_FORM_CONTACT`) with **Enquiry Type = Careers**, an option that form already has. Name,
email, organisation and region go to HubSpot as fields. Everything else is written into the Contact form's message,
one labelled line each, followed by what the person wrote:

```
Careers application from the website
Area of interest: Delivery and implementation
Phone: +60 12 345 6789
LinkedIn: https://linkedin.com/in/…
CV or portfolio: https://drive.google.com/…

Ten years implementing hospital systems…
```

To find them in HubSpot: Contact form submissions (or contacts) where Enquiry Type is Careers. The mapping is the
`hubspot` block of the `careers` intent in `src/forms.json`; `hubspotFields` in `src/worker.js` applies it. "Where
you work or study now" is required because the Contact form requires Organisation.

**No file upload.** HubSpot's form-submission API does not accept files, so the form asks for a link to a CV or a
LinkedIn profile instead of an upload.

## If CV uploads are wanted later

HubSpot's own embedded form is the supported way to take a file without an API key (the entomo website's role
pages work this way). It needs a "Job application" form created in adeahub's HubSpot account with file-type
properties, and a script that embeds and restyles it. That script was written and tested on 2026-11-17 and then
replaced by the form above: it is `public/assets/js/job-apply.js` in commit `28b9f4a`, with the HubSpot setup steps
in that commit's version of this file. Restoring it also means allowing HubSpot's hosts in the Content-Security-Policy
again (same commit).

A dedicated HubSpot form would also keep applicants apart from sales enquiries and allow "set contacts as marketing
contacts" to be switched off for them. With the Contact-form route, applicants are created the same way as any
contact-form enquiry.

## Copy and people on the page

- The copy states only what the site already says: the verified figures (35M+ users, 8,500+ health facilities,
  200M+ patient records, 17+ locations, 25+ years), the five core values from the About page, and the team areas
  visible in the About page's team titles. The "What happens next" steps and the line "We use these details only to
  consider you for roles at adeahub" were written for this page and should be confirmed by whoever owns hiring.
- "Meet some of the team" shows eight real colleagues, chosen as a mix of regions and crafts (owner's request,
  2026-11-17: no founder, people from different regions): two from the MEA team, one each from India, Malaysia &
  Brunei, Singapore and Thailand, and two from Global Functions. Portraits, names and roles come from the About page;
  the region line is the About page team group (a title's ", Singapore" moves to that line). When someone's title
  changes or they leave, update both pages.
- The other five photos are stock photographs, not adeahub staff, and the page does not present them as staff.

## Photo credits

All five are from Unsplash under the [Unsplash License](https://unsplash.com/license) (free for commercial use, no
attribution required), downloaded 2026-11-17, cropped and converted to WebP in `public/assets/images/careers/`.

| file | photographer | source |
|---|---|---|
| `team-around-laptop.webp` (hero) | Vitaly Gariev | https://unsplash.com/photos/diverse-team-collaborating-around-a-laptop-in-office-yd_RKGH_RH4 |
| `clinicians-reviewing-tablet.webp` (hero, small) | Vitaly Gariev | https://unsplash.com/photos/2kopEHjST-g |
| `team-at-conference-table.webp` | Ngital | https://unsplash.com/photos/six-colleagues-collaborating-around-a-conference-table-with-laptops-RdEFWm0N84o |
| `clinical-team-in-hospital-corridor.webp` | Luis Melendez | https://unsplash.com/photos/Pd4lRfKo16U |
| `colleagues-at-laptop.webp` | Vitaly Gariev | https://unsplash.com/photos/two-colleagues-collaborating-on-a-laptop-in-office-YDWdxElP3XI |

The Unsplash License covers the photographs; it does not include a release from the people shown. That is normal
for stock used as general illustration, and a reason not to caption these people as employees or quote them.

## Later: posting roles

The entomo website generates one page per role from a JSON file per role (`tools/jobs/` in its repository), plus
job-posting structured data for Google. The same model fits here: role pages listed on the careers page above the
"Introduce yourself" form. Roles with applications by CV are the point at which the embedded HubSpot form above is
worth setting up.
