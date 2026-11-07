"""Shared site header (skip link, nav, mega-menus, mobile menu) and footer, rendered for every page.

Edit the header/footer HERE, then run `python3 tools/build.py`. Styles live in src/css/site.css
(section "Site header / footer"). Every function takes `p`, the relative path from the page to the
site root ("" for the homepage, "../" for /platform/ and the other one-level pages), so the site works
from any folder or sub-path. Header/footer layout and sizes were measured on adeahub.co at 1440px;
the frosted header, CTA shimmer, mega-menu cards, chevrons, icon tiles
and footer social icons are the repo's own design.
"""
import datetime

# Page key -> URL path (relative to the site root, directory style)
URL = {
    "home": "", "platform": "platform/", "engage": "ah-engage/", "care": "ah-care/", "connect": "ah-connect/",
    "insights": "ah-insights/", "outbreak": "ah-outbreak-management/", "workwise": "workwise/",
    "about": "about-us/", "customers": "customers/", "newsroom": "newsroom/", "blogs": "blogs/",
    "contact": "contact-us/", "demo": "talk-to-us/",
}

def u(p, key):
    """Link from a page at prefix p to page `key` (homepage -> './' or '../')."""
    return (p + URL[key]) or "./"

ICON = {
    "phone": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>',
    "building": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/></svg>',
    "copy": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3v18h18"/><path d="M8 17v-5M13 17V8M18 17v-9"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "user": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/></svg>',
    "network": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M12 12V8"/></svg>',
    "users": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "news": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"/></svg>',
    "hospital": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6v4M14 14h-4M14 18h-4M14 8h-4"/><path d="M18 12h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2h2"/><path d="M18 22V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v18"/></svg>',
    "pen": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"/><path d="M16.38 3.62a1 1 0 0 1 3 3L7.37 18.64a2 2 0 0 1-.85.5l-2.87.84a.5.5 0 0 1-.62-.62l.84-2.87a2 2 0 0 1 .5-.85z"/></svg>',
}
CHEV = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
CHEVR = '<svg class="snav-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'

def item(href, icon, title_html, tag, desc=None):
    txt = f'<strong>{tag}</strong>' + (desc if desc else "")
    return (f'<a href="{href}" class="snav-item"><span class="snav-ico">{ICON[icon]}</span>'
            f'<span><span class="snav-title">{title_html}</span><span class="snav-text">{txt}</span></span></a>')

def header(p, current=None):
    def cur(name):
        return (' is-current" aria-current="page' if current == name else "")
    products = (
        '<div class="snav-panel"><div class="snav-card">'
        '<div class="snav-card-head"><span class="snav-label">adeahub products</span><a href="' + u(p, "platform") + '">View platform overview ' + CHEVR + '</a></div>'
        '<div class="snav-card-body">'
        '<div class="snav-group snav-grid">'
        + item(u(p, "engage"), "phone", "<span>AH</span> Engage", "Digital front door for patients", "Appointments, health records &amp; care journeys")
        + item(u(p, "care"), "building", "<span>AH</span> Care", "Health information system", "25+ clinical &amp; admin modules, multi-site")
        + '</div><div class="snav-group snav-grid">'
        + item(u(p, "connect"), "network", "<span>AH</span> Connect", "Interoperability &amp; health data exchange", "FHIR server, integration engine &amp; API gateway")
        + item(u(p, "insights"), "chart", "<span>AH</span> Insights", "Healthcare intelligence &amp; analytics", "Population health, real-time analytics &amp; AI/ML")
        + item(u(p, "outbreak"), "shield", "<span>AH</span> Outbreak Management", "Manage disease outbreaks", "Detection, tracing, monitoring &amp; containment")
        + '</div><div class="snav-group">'
        + item(u(p, "workwise"), "users", "<span>Work</span>Wise", "Healthcare workforce experience platform", "Performance, learning &amp; workforce intelligence for healthcare teams")
        + '</div></div>'
        '<div class="snav-card-foot"><a href="' + u(p, "demo") + '">Request a demo ' + CHEVR + '</a></div>'
        '</div></div>')
    resources = (
        '<div class="snav-panel"><div class="snav-card">'
        '<div class="snav-card-head"><span class="snav-label">Resources</span></div>'
        '<div class="snav-card-body">'
        '<div class="snav-group">' + item(u(p, "newsroom"), "news", "Newsroom", "Press releases &amp; company announcements") + '</div>'
        '<div class="snav-group">' + item(u(p, "customers"), "hospital", "Customers", "Case studies &amp; client outcomes") + '</div>'
        '<div class="snav-group">' + item(u(p, "blogs"), "pen", "Blog", "Insights, perspectives &amp; best practices") + '</div>'
        '</div>'
        '<div class="snav-card-foot"><a href="' + u(p, "demo") + '">Request a demo ' + CHEVR + '</a></div>'
        '</div></div>')
    A = 'class="block py-3 px-3 rounded-xl text-gray-800 hover:bg-blue-50 hover:text-adeahub-ink transition-colors font-medium text-base"'
    def m(key, t):
        aria = ' aria-current="page"' if current == key else ""
        return f'        <a href="{u(p, key)}" {A}{aria}>{t}</a>\n'
    D = '        <div class="my-2 border-t border-gray-100"></div>\n'
    mobile = ('    <nav id="mobile-menu" class="hidden md:hidden bg-white border-t border-gray-100 px-5 py-4" aria-label="Mobile">\n'
              '        <p class="px-3 pb-1 text-[13px] font-semibold text-gray-500">Products</p>\n'
              + m("engage", "AH Engage") + m("care", "AH Care") + m("connect", "AH Connect")
              + m("outbreak", "AH Outbreak Management") + m("insights", "AH Insights") + m("workwise", "WorkWise")
              + D + m("platform", "Platform") + D
              + '        <p class="px-3 pt-1 pb-1 text-[13px] font-semibold text-gray-500">Resources</p>\n'
              + m("newsroom", "Newsroom") + m("customers", "Customers") + m("blogs", "Blog")
              + D + m("about", "About Us") + D + m("contact", "Contact Us")
              + '        <div class="pt-3 pb-1">\n'
              f'            <a href="{u(p, "contact")}" class="block text-gray-900 text-center px-5 py-3.5 rounded-full hover:opacity-90 transition-colors font-semibold text-base" style="background:#F3D06F;">Talk to us</a>\n'
              '        </div>\n    </nav>\n')
    return (
        '<a class="skip-link" href="#main">Skip to content</a>\n'
        '<header id="main-nav" class="snav">\n'
        '    <div class="snav-inner">\n'
        f'        <a href="{u(p, "home")}" class="snav-brand"><img src="{p}assets/images/brand/adeahub-logo.webp" alt="adeahub" width="137" height="39" fetchpriority="high"><span class="snav-tag">Powering modern healthcare</span></a>\n'
        '        <nav class="snav-menu" aria-label="Main">\n'
        '            <ul class="snav-links">\n'
        f'                <li><a href="{u(p, "platform")}" class="snav-link{cur("platform")}">Platform</a></li>\n'
        f'                <li class="snav-dd snav-dd-products"><button type="button" class="snav-link" aria-haspopup="true" aria-expanded="false">Products {CHEV}</button>{products}</li>\n'
        f'                <li class="snav-dd snav-dd-resources"><button type="button" class="snav-link" aria-haspopup="true" aria-expanded="false">Resources {CHEV}</button>{resources}</li>\n'
        f'                <li><a href="{u(p, "about")}" class="snav-link{cur("about")}">About Us</a></li>\n'
        f'                <li><a href="{u(p, "contact")}" class="snav-link{cur("contact")}">Contact Us</a></li>\n'
        '            </ul>\n'
        f'            <a href="{u(p, "demo")}" class="snav-cta">Talk To Us</a>\n'
        '        </nav>\n'
        '        <button id="mobile-menu-btn" type="button" class="snav-burger" aria-label="Open menu" aria-controls="mobile-menu" aria-expanded="false">\n'
        '            <svg id="hamburger-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>\n'
        '            <svg id="close-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>\n'
        '        </button>\n'
        '    </div>\n'
        + mobile +
        '</header>')

GH_LINKEDIN = '<svg viewBox="0 0 24 24" fill="#4b5563" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.125 2.062 2.062 0 0 1 0 4.125zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
GH_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>'
MAIL_OUTLINE = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def footer(p):
    def li(key, inner): return f'                    <li><a href="{u(p, key)}">{inner}</a></li>\n'
    year = datetime.date.today().year
    return (
        '<footer class="sfoot">\n'
        '    <div class="sfoot-inner">\n'
        '        <div>\n'
        f'            <a href="{u(p, "home")}" class="sfoot-logo"><img src="{p}assets/images/brand/adeahub-logo-footer.webp" alt="adeahub" width="189" height="36" loading="lazy" decoding="async"></a>\n'
        '            <p class="sfoot-tag">Modern software to deliver personalised healthcare at scale.</p>\n'
        f'            <div class="sfoot-social"><a href="https://www.linkedin.com/company/adeahub/" target="_blank" rel="noopener" aria-label="adeahub on LinkedIn">{GH_LINKEDIN}</a><a href="mailto:hello@adeahub.co" aria-label="Email adeahub">{GH_MAIL}</a></div>\n'
        '        </div>\n'
        '        <nav aria-label="Products">\n'
        '            <p class="sfoot-h">Products</p>\n'
        '            <ul class="sfoot-list">\n'
        + li("engage", "<b>AH</b> Engage") + li("care", "<b>AH</b> Care") + li("connect", "<b>AH</b> Connect")
        + li("outbreak", "<b>AH</b> Outbreak Management") + li("insights", "<b>AH</b> Insights") + li("workwise", "<b>Work</b>Wise") +
        '            </ul>\n'
        '        </nav>\n'
        '        <nav aria-label="Company">\n'
        '            <p class="sfoot-h">Company</p>\n'
        '            <ul class="sfoot-list">\n'
        + li("platform", "Platform") + li("about", "About Us") + li("customers", "Customers")
        + li("newsroom", "Newsroom") + li("blogs", "Blog") + li("contact", "Contact Us") +
        '            </ul>\n'
        '        </nav>\n'
        '        <div>\n'
        '            <p class="sfoot-h">Get in touch</p>\n'
        '            <ul class="sfoot-list">\n'
        f'                <li><a href="mailto:hello@adeahub.co" class="sfoot-mail">{MAIL_OUTLINE}hello@adeahub.co</a></li>\n'
        '            </ul>\n'
        f'            <a href="{u(p, "demo")}" class="sfoot-btn">Request a demo {ARROW}</a>\n'
        '        </div>\n'
        '    </div>\n'
        f'    <div class="sfoot-copy"><p>&copy; {year} adeahub. All rights reserved.</p></div>\n'
        '</footer>')
