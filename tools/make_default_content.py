"""Builds Seeding/DefaultContent.json from the texts of the HTML prototype (docs/prototype).

Usage: python3 tools/make_default_content.py Seeding/DefaultContent.json
"""
import json, sys

EN = "en-US"

def btn(label, link, style):
    return {"type": "ButtonLinkBlock", "label": label, "link": link, "style": style}

def cta(heading, subtitle="A 20-minute call with {founder} — no obligation."):
    return {"type": "CallToActionBlock", "heading": heading, "subtitle": subtitle,
            "buttons": [btn("Schedule a call", "page:ContactPage", "navy"), btn("Send a message", "page:ContactPage#message", "outline")]}

def doc(name, ref=None, shared=None, culture=None):
    item = {"names": {EN: name}}
    if ref: item["ref"] = ref
    if shared: item["shared"] = shared
    if culture: item["cultures"] = {EN: culture}
    return item

settings = doc("Site Settings", shared={
    "founderName": "[Founder Name]",
    "founderRole": "Founder, Broudo Holdings",
    "contactEmail": "[email@broudoholdings.com]",
    "phone": "[+1 000 000 0000]",
    "companyName": "Broudo Holdings [LLC]",
    "registeredIn": "[State]",
    "mailingAddress": "[Mailing address]",
    "footerTagline": "Real estate development in Atlanta and Florida.",
    "legalDisclaimer": "[Disclaimer: the information on this site is general and does not constitute an offer to sell or a solicitation to buy any security. Final wording to be reviewed by counsel.]",
})

def market(ref, name, short, left, top, label, city):
    return doc(name, ref, {"shortName": short, "mapLeft": left, "mapTop": top, "heroLabel": label,
                           "intro": f"[One sentence on why we build in {city}.]"}, {"contentBlocks": [
        {"type": "ReasonsBlock", "eyebrow": "Why this market", "heading": "The numbers behind the decision.", "items": [
            {"type": "ReasonItemBlock", "value": "[+0.0%]", "title": "Population growth", "text": "[One line on population trends in the metro area.]", "source": "[source, date]"},
            {"type": "ReasonItemBlock", "value": "[000K]", "title": "Employment", "text": "[One line on major employers and job growth.]", "source": "[source, date]"},
            {"type": "ReasonItemBlock", "value": "[$000K]", "title": "Home prices", "text": "[One line on median prices and price trends.]", "source": "[source, date]"},
            {"type": "ReasonItemBlock", "value": "[0.0 mo]", "title": "Housing demand", "text": "[One line on inventory and days on market.]", "source": "[source, date]"},
        ]},
        {"type": "TextMediaBlock", "eyebrow": "What we do here", "heading": "[Type of projects] in [neighborhoods].",
         "body": "[Which neighborhoods, what kind of homes, who buys them, and how our local team operates here.]",
         "chips": "[Neighborhood]\n[Neighborhood]\n[Neighborhood]", "imageLabel": "Area map / neighborhood photo", "background": "white"},
        {"type": "MarketProjectsBlock", "heading": f"Projects in {city}", "linkLabel": "All projects", "link": "page:ProjectsPage"},
        cta(f"Want to hear more about {city}?"),
    ]})

markets = [
    market("atlanta", "Atlanta, Georgia", "Atlanta, GA", 66, 56, "OPENING PHOTO — ATLANTA", "Atlanta"),
    market("florida", "Florida", "Florida", 72, 76, "OPENING PHOTO — FLORIDA", "Florida"),
]

BODY = ("<p>[The starting point — what the property looked like and why we chose it.]</p>"
        "<p>[What we did — scope of work, design decisions, materials.]</p>"
        "<p>[The result — the finished home and what happened next.]</p>")
UPDATES = [
    {"type": "ProjectUpdateBlock", "title": "Acquisition closed", "text": "[Short update — one or two sentences.]"},
    {"type": "ProjectUpdateBlock", "title": "Demolition and framing", "text": "[Short update — one or two sentences.]"},
    {"type": "ProjectUpdateBlock", "title": "Finishes and handover", "text": "[Short update — one or two sentences.]"},
]

def project(ref, market_ref, location, ptype, status, results=False):
    shared = {"projectType": ptype, "projectStatus": status, "market": "ref:" + market_ref, "locationLabel": location}
    culture = {"neighborhood": "[Neighborhood]", "summary": "[Project summary, up to two lines.]", "body": BODY, "updates": UPDATES}
    if results:
        culture.update({"showResults": True, "resultValue": "[+00%]", "resultNote": "[Value before vs. after — shown only when enabled]"})
    return doc(f"[Project name {ref.upper()}]", ref, shared, culture)

projects = [
    project("a", "atlanta", "Atlanta, GA", "newConstruction", "completed"),
    project("b", "atlanta", "Atlanta, GA", "renovation", "sold", results=True),
    project("c", "florida", "[City], FL", "newConstruction", "inProgress"),
    project("d", "atlanta", "Atlanta, GA", "renovation", "forSale"),
    project("e", "florida", "[City], FL", "newConstruction", "planning"),
    project("f", "florida", "[City], FL", "renovation", "completed"),
]

def text_page(name, lead):
    return doc(name, shared={"hideFromNavigation": True, "noIndex": False}, culture={"contentBlocks": [
        {"type": "PageIntroBlock", "eyebrow": "Legal", "heading": name, "lead": lead},
        {"type": "RichTextBlock", "body": "<p>[Wording to be reviewed by counsel.]</p>"},
    ]})

text_pages = [
    text_page("Privacy policy", "[How we collect, use and protect personal information.]"),
    text_page("Accessibility statement", "[Our commitment to an accessible website, and how to reach us about accessibility.]"),
    text_page("Disclaimer", "[The information on this site is general and does not constitute an offer to sell or a solicitation to buy any security.]"),
]

pages = {
    "HomePage": [
        {"type": "HeroBlock", "eyebrow": "Real estate development · USA", "heading": "Homes built with care, in Atlanta and Florida.",
         "intro": "New construction and renovation in two growing U.S. markets — led personally by [Founder Name], with transparent reporting at every stage.",
         "photoLabel": "HERO PHOTO / SHORT VIDEO — LEAD PROJECT",
         "buttons": [btn("Schedule a call", "page:ContactPage", "brass"), btn("View projects", "page:ProjectsPage", "outlineLight")]},
        {"type": "StatsBlock", "items": [
            {"type": "StatItemBlock", "value": "[00]", "label": "Completed projects"},
            {"type": "StatItemBlock", "value": "[00]", "label": "Units delivered"},
            {"type": "StatItemBlock", "value": "[$00M]", "label": "Total project value"},
            {"type": "StatItemBlock", "value": "2", "label": "U.S. markets"},
        ]},
        {"type": "FounderIntroBlock", "eyebrow": "Meet the founder", "quote": "[A short first-person line on why I build — one sentence.]",
         "body": "[Two or three sentences in the founder’s voice: background, what drew them to U.S. real estate, and how they work with investors and partners.]",
         "linkLabel": "Read the full story", "link": "page:AboutPage"},
        {"type": "MarketsMapBlock", "eyebrow": "Our markets", "heading": "Two markets, chosen for growth and demand.",
         "linkLabel": "Explore the markets", "link": "page:MarketsPage", "mapLabel": "MAP OF THE UNITED STATES"},
        {"type": "FeaturedProjectsBlock", "eyebrow": "Selected projects", "heading": "Recent work, from first sketch to handover.",
         "projects": ["ref:a", "ref:b", "ref:c"], "linkLabel": "All projects", "link": "page:ProjectsPage"},
        {"type": "DisciplinesBlock", "eyebrow": "What we do", "heading": "Two disciplines, one standard.", "items": [
            {"type": "DisciplineItemBlock", "heading": "New construction", "mediaStyle": "photo", "imageLabel": "New construction photo",
             "body": "Single-family homes built from the ground up on carefully selected lots — design, permits, construction and sale, managed end to end."},
            {"type": "DisciplineItemBlock", "heading": "Renovation", "mediaStyle": "beforeAfter",
             "body": "Existing homes acquired, fully renovated and brought back to market — documented with before-and-after photography from the same angle."},
        ]},
        cta("Let’s talk about what you’re looking for."),
    ],
    "AboutPage": [
        {"type": "StoryBlock", "eyebrow": "About", "heading": "One name on the door. A full team behind it.",
         "body": "[Founder story, first person — background and what led to real estate.]\n[Why U.S. real estate, and why Atlanta and Florida in particular.]\n[How I work with investors and partners today.]"},
        {"type": "TimelineBlock", "eyebrow": "Milestones", "heading": "How we got here.", "items": [
            {"type": "TimelineItemBlock", "year": "[Year]", "text": "First project — [city, type]"},
            {"type": "TimelineItemBlock", "year": "[Year]", "text": "Entered the Atlanta market"},
            {"type": "TimelineItemBlock", "year": "[Year]", "text": "Entered the Florida market"},
            {"type": "TimelineItemBlock", "year": "[Year]", "text": "[Key project or milestone]"},
        ]},
        {"type": "PrinciplesBlock", "eyebrow": "How we work", "heading": "Four principles behind every project.", "items": [
            {"type": "PrincipleItemBlock", "heading": "Transparency", "body": "Partners see the numbers, the progress and the problems — as they happen."},
            {"type": "PrincipleItemBlock", "heading": "Close supervision", "body": "Every site is managed by a local team and reviewed personally on a regular schedule."},
            {"type": "PrincipleItemBlock", "heading": "Regular reporting", "body": "Written updates with photos, budget and timeline, on a fixed cadence."},
            {"type": "PrincipleItemBlock", "heading": "Build quality", "body": "Materials and finishes chosen to last — homes we would be proud to live in."},
        ]},
        cta("Let’s talk about what you’re looking for."),
    ],
    "ProjectsPage": [
        {"type": "PageIntroBlock", "eyebrow": "Projects", "heading": "Our work, market by market.",
         "lead": "Every project we’ve planned, built, renovated and sold — with the details that matter."},
    ],
    "ContactPage": [
        {"type": "ContactBlock", "eyebrow": "Contact", "heading": "I’d be glad to talk with you.", "formHeading": "Send a message",
         "topics": "Investing\nPartnership\nBuying a home\nOther", "privacyNote": "By submitting you agree to our privacy policy.",
         "successMessage": "Thank you — {founder} will get back to you personally."},
        {"type": "NewsletterBlock", "heading": "PROJECT UPDATES BY EMAIL", "placeholder": "Your email", "submitLabel": "Subscribe",
         "successMessage": "Thanks — you’re on the list."},
    ],
}

content = {
    "_about": "Default content from the HTML prototype, loaded into empty pages by DefaultContentSeeder (development only). Values: 'page:Alias' = link to that section page, 'ref:x' = a document below with that ref, blocks = objects with a 'type'. Generated by tools/make_default_content.py.",
    "settings": settings,
    "children": [
        {"parent": "MarketsPage", "type": "MarketPage", "items": markets},
        {"parent": "ProjectsPage", "type": "ProjectPage", "items": projects},
        {"parent": "HomePage", "type": "TextPage", "items": text_pages},
    ],
    "pages": {alias: {EN: blocks} for alias, blocks in pages.items()},
}

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(content, f, ensure_ascii=False, indent=2)
    f.write("\n")
