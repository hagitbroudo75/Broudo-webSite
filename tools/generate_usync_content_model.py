"""Generates the uSync files of the Broudo Holdings content model (document types, element types, data types, templates).

After running it: start the site (uSync imports the settings at startup), then run uSync "Export" in the
backoffice so the files are rewritten in uSync's own format; otherwise uSync keeps reporting them as changed.
"""
import json
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from block_labels import BLOCK_LABELS


ROOT = Path(__file__).resolve().parents[1]
SYNC_ROOT = ROOT / "uSync" / "v18"
CONTENT_TYPES = SYNC_ROOT / "ContentTypes"
DATA_TYPES = SYNC_ROOT / "DataTypes"
TEMPLATES = SYNC_ROOT / "Templates"
NAMESPACE = uuid.UUID("5f0c3d7e-2b8a-4c61-9e1d-b7a40f6c2e93")
PREFIX = "Broudo"


def key_for(alias):
    return str(uuid.uuid5(NAMESPACE, alias))


def safe_file(value):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in value)


def load_data_types():
    result = {}
    for path in DATA_TYPES.glob("*.config"):
        root = ET.parse(path).getroot()
        info = root.find("Info")
        result.setdefault(info.findtext("EditorAlias"), {
            "key": root.attrib["Key"],
            "ui": info.findtext("EditorUIAlias"),
        })
    return result


DATA_TYPES_BY_EDITOR = load_data_types()


def field(alias, name, editor, tab="content", options=None):
    return {"alias": alias, "name": name, "editor": editor, "tab": tab, "options": options}


def text(alias, name, tab="content"):
    return field(alias, name, "text", tab)


def area(alias, name, tab="content"):
    return field(alias, name, "textarea", tab)


def number(alias, name, tab="content"):
    return field(alias, name, "number", tab)


def decimal(alias, name, tab="content"):
    return field(alias, name, "decimal", tab)


def image(alias, name, tab="content"):
    return field(alias, name, "image", tab)


def url(alias, name, tab="content"):
    return field(alias, name, "url", tab)


def date(alias, name, tab="content"):
    return field(alias, name, "date", tab)


def boolean(alias, name, tab="content"):
    return field(alias, name, "boolean", tab)


def dropdown(alias, name, options, tab="content"):
    return field(alias, name, "dropdown", tab, options)


def blocks(alias, name, allowed, tab="content"):
    return field(alias, name, "blockList", tab, allowed)


BLOCKS = {
    "ButtonLinkBlock": [text("label", "Label"), url("link", "Link"), dropdown("style", "Style", ["brass", "navy", "outline", "outlineLight", "textLink"])],
    "HeroBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), area("intro", "Intro"), image("backgroundImage", "Background image"), text("photoLabel", "Label when there is no image"), blocks("buttons", "Buttons", ["ButtonLinkBlock"])],
    "StatsBlock": [blocks("items", "Items", ["StatItemBlock"])],
    "StatItemBlock": [text("value", "Value"), text("label", "Label")],
    "FounderIntroBlock": [text("eyebrow", "Eyebrow"), area("quote", "Quote"), area("body", "Text"), image("portrait", "Portrait (empty: from Site Settings)"), text("linkLabel", "Link label"), url("link", "Link")],
    "MarketsMapBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), text("linkLabel", "Link label"), url("link", "Link"), image("mapImage", "Map image"), text("mapLabel", "Label when there is no map")],
    "FeaturedProjectsBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), field("projects", "Projects (empty: the first three)", "contentPickerMultiple"), text("linkLabel", "Link label"), url("link", "Link")],
    "DisciplinesBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), blocks("items", "Disciplines", ["DisciplineItemBlock"])],
    "DisciplineItemBlock": [text("heading", "Heading"), area("body", "Description"), dropdown("mediaStyle", "Display (photo: one image, beforeAfter: before/after)", ["photo", "beforeAfter"]), image("image", "Image"), text("imageLabel", "Label when there is no image"), image("beforeImage", "Before image"), image("afterImage", "After image")],
    "CallToActionBlock": [text("heading", "Heading"), text("subtitle", "Subtitle ({founder} = founder name)"), blocks("buttons", "Buttons", ["ButtonLinkBlock"])],
    "StoryBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), area("body", "Text (one paragraph per line)"), image("portrait", "Portrait (empty: from Site Settings)"), field("photos", "Site photos", "multiImage")],
    "TimelineBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), blocks("items", "Milestones", ["TimelineItemBlock"])],
    "TimelineItemBlock": [text("year", "Year"), text("text", "Text")],
    "PrinciplesBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), blocks("items", "Principles", ["PrincipleItemBlock"])],
    "PrincipleItemBlock": [text("heading", "Heading"), area("body", "Description")],
    "PageIntroBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), area("lead", "Intro")],
    "ReasonsBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), blocks("items", "Items", ["ReasonItemBlock"])],
    "ReasonItemBlock": [text("value", "Value"), text("title", "Heading"), area("text", "Explanation"), text("source", "Source")],
    "TextMediaBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), area("body", "Text (one paragraph per line)"), area("chips", "Tags (one per line)"), image("image", "Image"), text("imageLabel", "Label when there is no image"), dropdown("background", "Background", ["limestone", "white"])],
    "MarketProjectsBlock": [text("heading", "Heading (empty: Projects in + market name)"), text("linkLabel", "Link label"), url("link", "Link")],
    "ContactBlock": [text("eyebrow", "Eyebrow"), text("heading", "Heading"), text("formHeading", "Form heading"), area("topics", "Enquiry topics (one per line)"), area("privacyNote", "Privacy note"), area("successMessage", "Message after sending")],
    "NewsletterBlock": [text("heading", "Newsletter heading"), text("placeholder", "Email field placeholder"), text("submitLabel", "Button label"), area("successMessage", "Message after signing up")],
    "RichTextBlock": [field("body", "Content", "richtext")],
    "ProjectUpdateBlock": [date("date", "Date"), text("title", "Heading"), area("text", "Text"), image("image", "Image")],
    "NavigationLinkBlock": [text("label", "Label"), url("link", "Link")],
}


SEO_FIELDS = [
    text("seoTitle", "SEO title", "seo"),
    area("seoDescription", "SEO description", "seo"),
    image("openGraphImage", "Social sharing image", "seo"),
    boolean("noIndex", "Hide from search engines", "seo"),
]
STANDARD_FIELDS = [
    text("navigationLabel", "Navigation label", "settings"),
    boolean("hideFromNavigation", "Hide from navigation", "settings"),
]

PAGE_BLOCKS = {
    "HomePage": ["HeroBlock", "StatsBlock", "FounderIntroBlock", "MarketsMapBlock", "FeaturedProjectsBlock", "DisciplinesBlock", "TextMediaBlock", "CallToActionBlock"],
    "AboutPage": ["StoryBlock", "TimelineBlock", "PrinciplesBlock", "StatsBlock", "TextMediaBlock", "CallToActionBlock"],
    "ProjectsPage": ["PageIntroBlock", "TextMediaBlock", "CallToActionBlock"],
    "MarketsPage": ["PageIntroBlock", "TextMediaBlock", "CallToActionBlock"],
    "MarketPage": ["ReasonsBlock", "TextMediaBlock", "MarketProjectsBlock", "StatsBlock", "CallToActionBlock"],
    "ContactPage": ["ContactBlock", "NewsletterBlock", "TextMediaBlock", "CallToActionBlock"],
    "TextPage": ["PageIntroBlock", "RichTextBlock", "TextMediaBlock", "CallToActionBlock"],
}

PROJECT_TYPES = ["newConstruction", "renovation"]
PROJECT_STATUSES = ["planning", "inProgress", "completed", "sold", "forSale"]

DOCUMENTS = {
    "SiteSettings": {"name": "Site Settings", "root": True, "icon": "icon-settings", "fields": [
        text("founderName", "Founder name"), text("founderRole", "Founder role"), image("founderPortrait", "Founder portrait"),
        text("contactEmail", "Email"), text("phone", "Phone"), text("whatsAppNumber", "WhatsApp number (digits only, with country code)"), url("bookingUrl", "Booking link (Calendly)"),
        text("companyName", "Company name", "company"), text("registeredIn", "Registered in", "company"), area("mailingAddress", "Mailing address", "company"),
        text("footerTagline", "Footer tagline", "company"), area("legalDisclaimer", "Legal disclaimer", "company"),
        url("linkedInUrl", "LinkedIn", "company"), url("instagramUrl", "Instagram", "company"),
        blocks("primaryNavigation", "Main navigation (empty: the site pages)", ["NavigationLinkBlock"], "navigation"),
        blocks("footerNavigation", "Footer EXPLORE links (empty: the site pages)", ["NavigationLinkBlock"], "navigation"),
    ]},
    "HomePage": {"name": "Home Page", "root": True, "icon": "icon-home", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "AboutPage": {"name": "About Page", "icon": "icon-user", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "ProjectsPage": {"name": "Projects Page", "icon": "icon-thumbnail-list", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "ProjectPage": {"name": "Project", "icon": "icon-home", "compositions": ["SeoComposition"], "fields": [
        dropdown("projectType", "Project type", PROJECT_TYPES), dropdown("projectStatus", "Status", PROJECT_STATUSES),
        field("market", "Market", "contentPicker"), text("locationLabel", "Location on the card (e.g. Atlanta, GA)"), text("neighborhood", "Neighborhood"),
        area("summary", "Summary (card and SEO)"), field("body", "About the project", "richtext"),
        image("heroImage", "Main image"), text("heroImageAltText", "Main image alt text"),
        number("livingArea", "Living area (sq ft)", "details"), number("bedrooms", "Bedrooms", "details"), decimal("bathrooms", "Bathrooms", "details"),
        number("lotSize", "Lot size (sq ft)", "details"), number("year", "Year", "details"), date("startDate", "Start date", "details"),
        date("completionDate", "Completion date", "details"), number("durationMonths", "Duration (months)", "details"),
        image("beforeImage", "Before", "media"), image("afterImage", "After", "media"), field("gallery", "Gallery", "multiImage", "media"),
        image("areaMapImage", "Area map (general area only)", "media"),
        blocks("updates", "Progress updates", ["ProjectUpdateBlock"], "updates"),
        boolean("showResults", "Show results", "updates"), text("resultValue", "Result (e.g. +24%)", "updates"), text("resultNote", "Result note", "updates"),
    ]},
    "MarketsPage": {"name": "Markets Page", "icon": "icon-map", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "MarketPage": {"name": "Market", "icon": "icon-map-location", "compositions": ["SeoComposition"], "fields": [
        text("shortName", "Short name (e.g. Atlanta, GA)"), area("intro", "Intro sentence"), image("heroImage", "Hero image"), text("heroLabel", "Label when there is no image"),
        number("mapLeft", "Home map position: % from left"), number("mapTop", "Home map position: % from top"),
    ]},
    "ContactPage": {"name": "Contact Page", "icon": "icon-message", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "TextPage": {"name": "Text Page", "icon": "icon-document", "compositions": ["SeoComposition", "StandardPageComposition"]},
}

DOCUMENTS["SeoComposition"] = {"name": "SEO Settings", "composition": True, "fields": SEO_FIELDS}
DOCUMENTS["StandardPageComposition"] = {"name": "Page Settings", "composition": True, "fields": STANDARD_FIELDS}
for page_alias, allowed_blocks in PAGE_BLOCKS.items():
    DOCUMENTS[page_alias]["fields"] = DOCUMENTS[page_alias].get("fields", []) + [blocks("contentBlocks", "Content blocks", allowed_blocks)]

PARENTAGE = {
    "HomePage": ["AboutPage", "ProjectsPage", "MarketsPage", "ContactPage", "TextPage"],
    "ProjectsPage": ["ProjectPage"],
    "MarketsPage": ["MarketPage"],
}


EDITOR_MAP = {
    "text": "Umbraco.TextBox",
    "textarea": "Umbraco.TextArea",
    "number": "Umbraco.Integer",
    "decimal": "Umbraco.Decimal",
    "boolean": "Umbraco.TrueFalse",
    "richtext": "Umbraco.RichText",
    "image": "Umbraco.MediaPicker3",
    "multiImage": "Umbraco.MediaPicker3",
    "url": "Umbraco.MultiUrlPicker",
    "date": "Umbraco.DateTime",
    "contentPicker": "Umbraco.ContentPicker",
    "contentPickerMultiple": "Umbraco.MultiNodeTreePicker",
    "dropdown": "Umbraco.DropDown.Flexible",
    "blockList": "Umbraco.BlockList",
}


def create_data_type(name, editor_alias, ui_alias, config):
    key = key_for("datatype:" + name)
    root = ET.Element("DataType", {"Key": key, "Alias": name, "Level": "1"})
    info = ET.SubElement(root, "Info")
    ET.SubElement(info, "Name").text = name
    ET.SubElement(info, "EditorAlias").text = editor_alias
    ET.SubElement(info, "EditorUIAlias").text = ui_alias
    ET.SubElement(root, "Config").text = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    write_xml(root, DATA_TYPES / (safe_file(name) + ".config"))
    return key


def write_xml(root, path):
    # uSync names its own exports differently (e.g. lower case); drop any file that holds the same item
    key = root.attrib.get("Key")
    for existing in path.parent.glob("*.config") if path.parent.exists() else []:
        if existing.name != path.name and key and f'Key="{key}"' in existing.read_text(encoding="utf-8-sig")[:400]:
            existing.unlink()
    ET.indent(root, space="  ")
    xml = ET.tostring(root, encoding="unicode", xml_declaration=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + xml + "\n", encoding="utf-8")


def ensure_data_types():
    def configure_field(owner, item):
        editor = item["editor"]
        editor_alias = EDITOR_MAP[editor]
        name = f"{PREFIX} - {owner} - {item['alias']}"
        if editor == "dropdown":
            item["dataTypeKey"] = create_data_type(name, editor_alias, "Umb.PropertyEditorUi.Dropdown", {"items": item["options"], "multiple": False})
        elif editor == "decimal":
            item["dataTypeKey"] = create_data_type(f"{PREFIX} - Decimal", editor_alias, "Umb.PropertyEditorUi.Decimal", {"step": "0.5"})
        elif editor == "date":
            item["dataTypeKey"] = ET.parse(DATA_TYPES / "DatePicker.config").getroot().attrib["Key"]
        elif editor == "contentPicker":
            item["dataTypeKey"] = DATA_TYPES_BY_EDITOR[editor_alias]["key"]
        elif editor == "contentPickerMultiple":
            item["dataTypeKey"] = create_data_type(name, editor_alias, "Umb.PropertyEditorUi.MultiDocumentPicker", {"minNumber": 0, "maxNumber": 0})
        elif editor == "multiImage":
            item["dataTypeKey"] = create_data_type(name, editor_alias, "Umb.PropertyEditorUi.MediaPicker", {"multiple": True, "validationLimit": {"min": 0}})
        elif editor == "blockList":
            item["dataTypeKey"] = create_data_type(name, editor_alias, "Umb.PropertyEditorUi.BlockList", {
                "blocks": [{"contentElementTypeKey": key_for("contenttype:" + block), "label": BLOCK_LABELS.get(block, "{=heading}"), "editorSize": "medium", "forceHideContentEditorInOverlay": False} for block in item["options"]],
                "validationLimit": {},
                "useSingleBlockMode": False,
                "useLiveEditing": False,
                "useInlineEditingAsDefault": False,
            })

    for alias, fields in BLOCKS.items():
        for item in fields:
            configure_field(alias, item)
    for alias, document in DOCUMENTS.items():
        for item in document.get("fields", []):
            configure_field(alias, item)


def datatype_key(item):
    if "dataTypeKey" in item:
        return item["dataTypeKey"]
    if item["editor"] == "image":
        return ET.parse(DATA_TYPES / "MediaPicker.config").getroot().attrib["Key"]
    return DATA_TYPES_BY_EDITOR[EDITOR_MAP[item["editor"]]]["key"]


def build_content_type(alias, spec, element=False):
    key = key_for("contenttype:" + alias)
    root = ET.Element("ContentType", {"Key": key, "Alias": alias, "Level": "1"})
    info = ET.SubElement(root, "Info")
    ET.SubElement(info, "Name").text = spec["name"]
    ET.SubElement(info, "Icon").text = spec.get("icon", "icon-box" if element else "icon-document")
    ET.SubElement(info, "Thumbnail").text = ""
    ET.SubElement(info, "Description").text = ""
    ET.SubElement(info, "AllowAtRoot").text = str(spec.get("root", False)).lower()
    ET.SubElement(info, "ListView").text = "00000000-0000-0000-0000-000000000000"
    ET.SubElement(info, "Variations").text = "Culture"
    ET.SubElement(info, "IsElement").text = str(element).lower()
    if spec.get("compositions"):
        compositions = ET.SubElement(info, "Compositions")
        for composition in spec["compositions"]:
            ET.SubElement(compositions, "Composition", {"Key": key_for("contenttype:" + composition)}).text = composition
    template = alias if spec.get("template") else ""
    ET.SubElement(info, "DefaultTemplate").text = template
    allowed_templates = ET.SubElement(info, "AllowedTemplates")
    if template:
        ET.SubElement(allowed_templates, "Template", {"Key": key_for("template:" + alias)}).text = alias

    groups = {}
    for item in spec.get("fields", []):
        groups.setdefault(item["tab"], []).append(item)

    tabs = ET.SubElement(root, "Tabs")
    tab_names = {"content": "Content", "details": "Details", "media": "Images", "updates": "Updates and results", "company": "Company and footer", "navigation": "Navigation", "seo": "SEO", "settings": "Settings"}
    for sort, tab_alias in enumerate(groups, start=1):
        tab = ET.SubElement(tabs, "Tab")
        ET.SubElement(tab, "Key").text = key_for(f"tab:{alias}:{tab_alias}")
        ET.SubElement(tab, "Caption").text = tab_names.get(tab_alias, tab_alias)
        ET.SubElement(tab, "Alias").text = tab_alias
        ET.SubElement(tab, "Type").text = "Tab"
        ET.SubElement(tab, "SortOrder").text = str(sort)

    generic = ET.SubElement(root, "GenericProperties")
    sort_order = 0
    for tab_alias, tab_fields in groups.items():
        for item in tab_fields:
            sort_order += 1
            prop = ET.SubElement(generic, "GenericProperty")
            ET.SubElement(prop, "Key").text = key_for(f"property:{alias}:{item['alias']}")
            ET.SubElement(prop, "Name").text = item["name"]
            ET.SubElement(prop, "Alias").text = item["alias"]
            ET.SubElement(prop, "Definition").text = datatype_key(item)
            ET.SubElement(prop, "Type").text = EDITOR_MAP[item["editor"]]
            ET.SubElement(prop, "Mandatory").text = "false"
            ET.SubElement(prop, "Validation").text = ""
            ET.SubElement(prop, "Description").text = ""
            ET.SubElement(prop, "SortOrder").text = str(sort_order)
            ET.SubElement(prop, "Tab", {"Alias": tab_alias}).text = tab_names.get(tab_alias, tab_alias)
            ET.SubElement(prop, "MandatoryMessage").text = ""
            ET.SubElement(prop, "ValidationRegExpMessage").text = ""
            ET.SubElement(prop, "LabelOnTop").text = "false"
            ET.SubElement(prop, "Variations").text = "Culture"

    structure = ET.SubElement(root, "Structure")
    for index, child in enumerate(PARENTAGE.get(alias, [])):
        ET.SubElement(structure, "ContentType", {"Key": key_for("contenttype:" + child), "SortOrder": str(index)}).text = child

    write_xml(root, CONTENT_TYPES / (alias + ".config"))


def build_template(alias):
    root = ET.Element("Template", {"Key": key_for("template:" + alias), "Alias": alias, "Level": "1"})
    ET.SubElement(root, "Name").text = alias
    ET.SubElement(root, "Parent")
    write_xml(root, TEMPLATES / (alias + ".config"))


def main():
    ensure_data_types()
    for alias, spec in DOCUMENTS.items():
        if not spec.get("composition") and alias != "SiteSettings":
            spec["template"] = True
            build_template(alias)
    for alias, spec in BLOCKS.items():
        build_content_type(alias, {"name": alias, "fields": spec}, element=True)
    for alias, spec in DOCUMENTS.items():
        build_content_type(alias, spec)

    print(f"Generated {len(BLOCKS) + len(DOCUMENTS)} content types in {CONTENT_TYPES}")


if __name__ == "__main__":
    main()
