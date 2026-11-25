# Skill: Create single-page website (auto-learned from T-013)

## Trigger
User asks for something like: Create single-page website.
Original request: Ishtiaq Ahmed requested a single-page website with a hero section, navbar, footer, good UI, and an About Us section (email dated Tue, 29 Sep 2026).
(source mail ID 1a0eb28fd4e61f3f)

## Process
1. Create workspace/T-013/index.html
   - <!DOCTYPE html> with <html lang="en">
   - <head> includes meta charset, viewport, title, link to style.css, optional link to Google Font.
   - <body> contains:
     a. <nav> with logo placeholder and navigation links (Home, About, Contact).
     b. <header class="hero"> with a prominent heading, sub‑heading, and call‑to‑action button.
     c. <section id="about" class="about-us"> with a heading, paragraph describing the organization, and optional image.
     d. <footer> with copyright notice and contact email.
   - Include script tag linking to script.js at end of body.
2. Create workspace/T-013/style.css
   - Reset/normalize basics.
   - Styles for nav: fixed top, flex layout, responsive collapse.
   - Hero section: full‑viewport height, background image (placeholder URL), centered text, button styling.
   - About Us section: max‑width container, readable typography, optional image float.
   - Footer: dark background, centered text, small padding.
   - Media queries for mobile friendliness.
3. Create workspace/T-013/script.js
   - Simple toggle function for mobile navigation menu (adds/removes .open class on nav ul).
   - Event listener on hamburger icon.
4. Add a README.md in workspace/T-013 describing how to view the site locally (open index.html in a browser).

## Output constraints
- workspace/T-013/index.html exists and contains <nav>, a <header class="hero">, a <section id="about">, and a <footer> element
- workspace/T-013/style.css exists and is linked from index.html via a <link rel="stylesheet"> tag
- workspace/T-013/script.js exists and is referenced from index.html via a <script src="script.js"></script> tag
- No file in workspace/T-013 contains the strings TODO, FIXME, or lorem ipsum
- All HTML, CSS, and JS files are non‑empty (size > 1KB) and use UTF‑8 encoding

## Provenance
Learned 2026-09-29 from ticket T-013.
Reviewer verdict: clean
