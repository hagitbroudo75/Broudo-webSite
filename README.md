# Broudo Holdings — אתר Umbraco

אתר Umbraco 18.2 שנבנה מאב-הטיפוס ב-HTML (`docs/prototype`), באותו מבנה כמו GemmaHomes.

## הרצה

הקוד נמצא כאן (iCloud), אבל האתר רץ מעותק מקומי: `~/Projects/BroudoHoldings-local`.

```bash
tools/sync-local.sh run    # מעתיק לעותק המקומי ומפעיל את האתר
```

- אתר: https://localhost:44373 (או http://localhost:56478)
- ממשק ניהול: https://localhost:44373/umbraco (אותו משתמש וסיסמה כמו ב-GemmaHomes)

בהפעלה הראשונה Umbraco מותקן לבד, uSync מייבא את מודל התוכן, והתוכן ההתחלתי נטען מ-`Seeding/DefaultContent.json`.
התוכן נטען רק לעמודים ריקים, כך שתוכן שנערך בממשק הניהול לא נדרס.

## מבנה התוכן

| עמוד | סוג | מה יש בו |
|---|---|---|
| Home | `HomePage` | Hero, פס נתונים, היכרות עם המייסד, מפת שווקים, פרויקטים נבחרים, תחומי פעילות, קריאה לפעולה |
| About | `AboutPage` | הסיפור, ציר זמן, עקרונות |
| Projects | `ProjectsPage` → `ProjectPage` | רשימה עם סינון לפי שוק, סוג וסטטוס. כל פרויקט הוא עמוד עם פרטים, לפני/אחרי, גלריה ועדכונים |
| Markets | `MarketsPage` → `MarketPage` | מפנה לשוק הראשון. בכל שוק: נתוני שוק, טקסט ותמונה, והפרויקטים של אותו שוק (אוטומטית) |
| Contact | `ContactPage` | פנייה וטופס, פרטי חברה והרשמה לעדכונים |
| Privacy policy וכו׳ | `TextPage` | עמודי טקסט. מופיעים בשורה המשפטית בתחתית, לא בתפריט |
| Site Settings | `SiteSettings` | שם המייסד ותמונתו, דוא״ל, טלפון, WhatsApp, Calendly, פרטי החברה, גילוי נאות, LinkedIn/Instagram |

- כשאין תמונה, מוצגת המסגרת האפורה עם התווית, כמו באב-הטיפוס. אחרי שבוחרים תמונה, היא ממלאת את המסגרת.
- במפת דף הבית מופיעה סיכה לכל שוק שיש לו מיקום במפה (אחוז משמאל / מלמעלה), עם מספר הפרויקטים שלו.

## שינוי מודל התוכן

1. עורכים את `tools/generate_usync_content_model.py` (ואת `tools/block_labels.py` לבלוק חדש). השמות והתוויות בממשק הניהול באנגלית.
2. מריצים `python3 tools/generate_usync_content_model.py`.
3. מוסיפים או מעדכנים את ה-partial ב-`Views/Partials/Blocks/{Alias}.cshtml`.
4. מפעילים מחדש. אחר כך כדאי להריץ uSync Export בממשק הניהול.

התוכן ההתחלתי נוצר מ-`tools/make_default_content.py` (`python3 tools/make_default_content.py Seeding/DefaultContent.json`).

## בדיקת התבניות

`dotnet build` לא מקמפל את קובצי ה-cshtml. כדי לבדוק את כולם, מעתיקים את הפרויקט לתיקייה זמנית ומריצים
`dotnet build -p:RazorCompileOnBuild=true`.

## האתר בענן (Render)

האתר רץ ב-Render כ-Docker (`Dockerfile`), לפי ההגדרות ב-`render.yaml`. כל push ל-main מעלה גרסה חדשה.

- מסד הנתונים, התמונות שהועלו ומפתחות ההתחברות נשמרים בדיסק הקבוע `/var/data` (ראו `appsettings.Production.json`), ולכן לא נמחקים בעדכון גרסה.
- בהפעלה הראשונה בשרת נוצרים מנהל האתר (מהמשתנים שהוזנו ב-Render) והתוכן ההתחלתי. משם והלאה התוכן נערך בממשק הניהול בענן, והוא נפרד מהתוכן במחשב.
- גיבוי: Render מצלם את הדיסק פעם ביום.

## עדיין לא מחובר

- טפסים: כרגע הדגמה בלבד (`wwwroot/js/main.js`).
- מפות: מקום שמור (מפת דף הבית, תצוגת Map בעמוד הפרויקטים, מפת אזור בפרויקט).
- עברית: סוגי התוכן מוגדרים לפי שפה, כך שאפשר להוסיף he-IL. עדיין חסרים תוכן בעברית והתאמות RTL ב-CSS.
