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
    "ButtonLinkBlock": [text("label", "תווית"), url("link", "קישור"), dropdown("style", "סגנון", ["brass", "navy", "outline", "outlineLight", "textLink"])],
    "HeroBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), area("intro", "פתיח"), image("backgroundImage", "תמונת רקע"), text("photoLabel", "תווית כשאין תמונה"), blocks("buttons", "כפתורים", ["ButtonLinkBlock"])],
    "StatsBlock": [blocks("items", "נתונים", ["StatItemBlock"])],
    "StatItemBlock": [text("value", "ערך"), text("label", "תווית")],
    "FounderIntroBlock": [text("eyebrow", "כותרת משנה"), area("quote", "ציטוט"), area("body", "טקסט"), image("portrait", "פורטרט (ריק: מהגדרות האתר)"), text("linkLabel", "תווית קישור"), url("link", "קישור")],
    "MarketsMapBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), text("linkLabel", "תווית קישור"), url("link", "קישור"), image("mapImage", "תמונת מפה"), text("mapLabel", "תווית כשאין מפה")],
    "FeaturedProjectsBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), field("projects", "פרויקטים (ריק: שלושת הראשונים)", "contentPickerMultiple"), text("linkLabel", "תווית קישור"), url("link", "קישור")],
    "DisciplinesBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), blocks("items", "תחומים", ["DisciplineItemBlock"])],
    "DisciplineItemBlock": [text("heading", "כותרת"), area("body", "תיאור"), dropdown("mediaStyle", "תצוגה (photo: תמונה אחת, beforeAfter: לפני/אחרי)", ["photo", "beforeAfter"]), image("image", "תמונה"), text("imageLabel", "תווית כשאין תמונה"), image("beforeImage", "תמונת לפני"), image("afterImage", "תמונת אחרי")],
    "CallToActionBlock": [text("heading", "כותרת"), text("subtitle", "שורת משנה ({founder} = שם המייסד)"), blocks("buttons", "כפתורים", ["ButtonLinkBlock"])],
    "StoryBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), area("body", "טקסט (פסקה בכל שורה)"), image("portrait", "פורטרט (ריק: מהגדרות האתר)"), field("photos", "תמונות מהשטח", "multiImage")],
    "TimelineBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), blocks("items", "אבני דרך", ["TimelineItemBlock"])],
    "TimelineItemBlock": [text("year", "שנה"), text("text", "טקסט")],
    "PrinciplesBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), blocks("items", "עקרונות", ["PrincipleItemBlock"])],
    "PrincipleItemBlock": [text("heading", "כותרת"), area("body", "תיאור")],
    "PageIntroBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), area("lead", "פתיח")],
    "ReasonsBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), blocks("items", "נתונים", ["ReasonItemBlock"])],
    "ReasonItemBlock": [text("value", "ערך"), text("title", "כותרת"), area("text", "הסבר"), text("source", "מקור")],
    "TextMediaBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), area("body", "טקסט (פסקה בכל שורה)"), area("chips", "תגיות (אחת בכל שורה)"), image("image", "תמונה"), text("imageLabel", "תווית כשאין תמונה"), dropdown("background", "רקע", ["limestone", "white"])],
    "MarketProjectsBlock": [text("heading", "כותרת (ריק: Projects in + שם השוק)"), text("linkLabel", "תווית קישור"), url("link", "קישור")],
    "ContactBlock": [text("eyebrow", "כותרת משנה"), text("heading", "כותרת"), text("formHeading", "כותרת הטופס"), area("topics", "נושאי פנייה (אחד בכל שורה)"), area("privacyNote", "הערת פרטיות"), area("successMessage", "הודעה אחרי שליחה")],
    "NewsletterBlock": [text("heading", "כותרת ההרשמה"), text("placeholder", "טקסט בשדה הדוא״ל"), text("submitLabel", "תווית כפתור"), area("successMessage", "הודעה אחרי הרשמה")],
    "RichTextBlock": [field("body", "תוכן", "richtext")],
    "ProjectUpdateBlock": [date("date", "תאריך"), text("title", "כותרת"), area("text", "טקסט"), image("image", "תמונה")],
    "NavigationLinkBlock": [text("label", "תווית"), url("link", "קישור")],
}


SEO_FIELDS = [
    text("seoTitle", "כותרת SEO", "seo"),
    area("seoDescription", "תיאור SEO", "seo"),
    image("openGraphImage", "תמונת שיתוף", "seo"),
    boolean("noIndex", "הסתרה ממנועי חיפוש", "seo"),
]
STANDARD_FIELDS = [
    text("navigationLabel", "תווית ניווט", "settings"),
    boolean("hideFromNavigation", "הסתרה מהתפריט", "settings"),
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
    "SiteSettings": {"name": "הגדרות אתר", "root": True, "icon": "icon-settings", "fields": [
        text("founderName", "שם המייסד"), text("founderRole", "תפקיד המייסד"), image("founderPortrait", "תמונת המייסד"),
        text("contactEmail", "דוא״ל"), text("phone", "טלפון"), text("whatsAppNumber", "מספר WhatsApp (ספרות בלבד, עם קידומת מדינה)"), url("bookingUrl", "קישור לקביעת שיחה (Calendly)"),
        text("companyName", "שם החברה", "company"), text("registeredIn", "מדינת רישום", "company"), area("mailingAddress", "כתובת למשלוח דואר", "company"),
        text("footerTagline", "משפט בתחתית האתר", "company"), area("legalDisclaimer", "גילוי נאות", "company"),
        url("linkedInUrl", "LinkedIn", "company"), url("instagramUrl", "Instagram", "company"),
        blocks("primaryNavigation", "ניווט ראשי (ריק: עמודי האתר)", ["NavigationLinkBlock"], "navigation"),
        blocks("footerNavigation", "קישורי EXPLORE בתחתית (ריק: עמודי האתר)", ["NavigationLinkBlock"], "navigation"),
    ]},
    "HomePage": {"name": "דף הבית", "root": True, "icon": "icon-home", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "AboutPage": {"name": "אודות", "icon": "icon-user", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "ProjectsPage": {"name": "פרויקטים", "icon": "icon-thumbnail-list", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "ProjectPage": {"name": "פרויקט", "icon": "icon-home", "compositions": ["SeoComposition"], "fields": [
        dropdown("projectType", "סוג פרויקט", PROJECT_TYPES), dropdown("projectStatus", "סטטוס", PROJECT_STATUSES),
        field("market", "שוק", "contentPicker"), text("locationLabel", "מיקום בכרטיס (למשל Atlanta, GA)"), text("neighborhood", "שכונה"),
        area("summary", "תקציר (לכרטיס ול-SEO)"), field("body", "על הפרויקט", "richtext"),
        image("heroImage", "תמונה ראשית"), text("heroImageAltText", "טקסט חלופי לתמונה הראשית"),
        number("livingArea", "שטח מגורים (sq ft)", "details"), number("bedrooms", "חדרי שינה", "details"), decimal("bathrooms", "חדרי רחצה", "details"),
        number("lotSize", "גודל מגרש (sq ft)", "details"), number("year", "שנה", "details"), date("startDate", "התחלה", "details"),
        date("completionDate", "סיום", "details"), number("durationMonths", "משך בחודשים", "details"),
        image("beforeImage", "לפני", "media"), image("afterImage", "אחרי", "media"), field("gallery", "גלריה", "multiImage", "media"),
        image("areaMapImage", "מפת אזור (אזור כללי בלבד)", "media"),
        blocks("updates", "עדכוני התקדמות", ["ProjectUpdateBlock"], "updates"),
        boolean("showResults", "הצגת תוצאות", "updates"), text("resultValue", "תוצאה (למשל +24%)", "updates"), text("resultNote", "הסבר לתוצאה", "updates"),
    ]},
    "MarketsPage": {"name": "שווקים", "icon": "icon-map", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "MarketPage": {"name": "שוק", "icon": "icon-map-location", "compositions": ["SeoComposition"], "fields": [
        text("shortName", "שם קצר (למשל Atlanta, GA)"), area("intro", "משפט פתיחה"), image("heroImage", "תמונת פתיחה"), text("heroLabel", "תווית כשאין תמונה"),
        number("mapLeft", "מיקום במפת הבית: אחוז משמאל"), number("mapTop", "מיקום במפת הבית: אחוז מלמעלה"),
    ]},
    "ContactPage": {"name": "צור קשר", "icon": "icon-message", "compositions": ["SeoComposition", "StandardPageComposition"]},
    "TextPage": {"name": "עמוד טקסט", "icon": "icon-document", "compositions": ["SeoComposition", "StandardPageComposition"]},
}

DOCUMENTS["SeoComposition"] = {"name": "הגדרות SEO משותפות", "composition": True, "fields": SEO_FIELDS}
DOCUMENTS["StandardPageComposition"] = {"name": "הגדרות עמוד משותפות", "composition": True, "fields": STANDARD_FIELDS}
for page_alias, allowed_blocks in PAGE_BLOCKS.items():
    DOCUMENTS[page_alias]["fields"] = DOCUMENTS[page_alias].get("fields", []) + [blocks("contentBlocks", "אזורי תוכן", allowed_blocks)]

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
    tab_names = {"content": "תוכן", "details": "פרטים", "media": "תמונות", "updates": "עדכונים ותוצאות", "company": "חברה ותחתית", "navigation": "ניווט", "seo": "SEO", "settings": "הגדרות"}
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
