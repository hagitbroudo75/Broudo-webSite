# Broudo Holdings — website (English)

Static site: plain HTML, CSS and a small JavaScript file. No build step, no dependencies.

## Open it in VS Code

1. Unzip the folder and open it in VS Code (File → Open Folder).
2. Install the **Live Server** extension (by Ritwick Dey).
3. Right-click `index.html` → **Open with Live Server**. The site opens in your browser and refreshes on every save.

## Structure

```
index.html        Home
about.html        About
projects.html     Projects list (filters by market / type / status)
project.html      Project page template
markets.html      Market page template (Atlanta)
contact.html      Contact
assets/css/styles.css   All styles — brand colors are CSS variables at the top
assets/js/main.js       Mobile menu, project filters, before/after slider, demo forms
assets/img/             Favicon and logo SVG — put your photos here
```

## What to fill in

Everything in `[square brackets]` is a placeholder: founder name, numbers, project details, email, phone, WhatsApp number (`https://wa.me/[NUMBER]`), Calendly link (`[CALENDLY_LINK]`), company entity and state.

**Photos:** every grey box with a label (class `ph`) is a photo placeholder. Replace it with an image, for example:

```html
<div class="ph ratio-4-3">Project photo</div>
<!-- becomes -->
<img class="ratio-4-3 media-cover" src="assets/img/project-1.jpg" alt="Front of the renovated home on [street]">
```

For the home-page hero, add a background image to the section:
`<section class="hero" style="background-image:url('assets/img/hero.jpg')">`

## Still to connect

- **Forms** — currently demo only (they show a thank-you message and send nothing). Connect to Formspree, Netlify Forms, your CMS, or a server endpoint; see the comment in `assets/js/main.js`.
- **Maps** — the map areas are placeholders. Embed Google Maps or Mapbox.
- **Hebrew version** — the EN / עב switcher is in the header; the Hebrew (RTL) pages are not built yet.
- **Legal** — privacy policy, accessibility statement, disclaimer (wording to be reviewed by counsel).
- **CMS** — per the spec, projects and markets should eventually come from a content management system. The card markup in `projects.html` is the template for each project.
