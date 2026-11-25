# Skill: Create single page website (auto-learned from T-018)

## Trigger
User asks for something like: Create single page website.
Original request: Ishtiaq Ahmed requests a single page website with a navbar, footer, and About Us section.
(source mail ID 1a0eb76c6904dd09)

## Process
1. Create workspace/T-018/index.html
   - <!DOCTYPE html> with <html lang="en">
   - <head> includes meta charset, viewport, title, link to style.css, script defer to script.js
   - <body> contains:
     a. <header> with <nav> element, an unordered list of links (Home, About, Contact) and a hamburger button for mobile.
     b. <main> with a <section id="about-us" class="about-us"> containing a heading and placeholder paragraph describing the company.
     c. <footer> with copyright text and simple navigation links.
   - Use semantic tags and minimal placeholder text (no lorem ipsum).
2. Create workspace/T-018/style.css
   - Reset basic margins/padding.
   - Style the navbar: horizontal layout on desktop, hidden menu on mobile, hamburger button styling.
   - Style the About Us section with spacing and readable typography.
   - Style the footer with background color and centered text.
   - Ensure the file size is >1KB by including comments and sufficient CSS rules.
3. Create workspace/T-018/script.js
   - Add a click listener to the hamburger button that toggles a "open" class on the nav list for mobile display.
   - Keep the script concise (<200 lines) and free of console.log debugging statements.
4. Verify all files are saved in the specified folder and that the HTML correctly references the CSS and JS files.

## Output constraints
- workspace/T-018/index.html exists and contains a <nav> element
- workspace/T-018/index.html contains a <footer> element
- workspace/T-018/index.html includes a <section> with id="about-us"
- workspace/T-018/style.css exists and is linked in index.html via a <link> tag
- workspace/T-018/script.js exists and is referenced in index.html with a <script defer> tag
- No file in workspace/T-018 contains the strings TODO, FIXME, or lorem

## Provenance
Learned 2026-09-29 from ticket T-018.
Reviewer verdict: clean
