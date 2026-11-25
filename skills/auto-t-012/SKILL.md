# Skill: Construct single page website (auto-learned from T-012)

## Trigger
User asks for something like: Construct single page website.
Original request: Ishtiaq Ahmed requests a single-page website featuring a hero section, navbar, footer, and an About Us section with good UI. Email dated Tue, 29 Sep 2026.
(source mail ID 1a0eb1f080d7d124)

## Process
1. workspace/T-012/index.html
   - <!DOCTYPE html> with <html lang="en">, <head> linking style.css and script.js.
   - <header> containing a <nav> with logo placeholder and anchor links: Home, About, Contact (footer link).
   - <section id="hero" class="hero">
       * Full‑width background image (placeholder URL) with overlay text: title, subtitle, and a CTA button.
     </section>
   - <section id="about" class="about">
       * <h2>About Us</h2>
       * Two <p> paragraphs describing the organization (sample lorem text to be replaced).
       * Optional <img> or illustration placeholder.
     </section>
   - <footer class="footer">
       * Simple copyright line and social icon placeholders.
     </footer>
   - Include semantic HTML5 elements, no inline styles, and no TODO/FIXME comments.

2. workspace/T-012/style.css
   - CSS reset (e.g., box‑sizing, margin/padding reset).
   - Variables for primary colors, fonts, and spacing.
   - Layout: flexbox for navbar, grid/flex for hero overlay, responsive breakpoints (mobile ≤768px, tablet ≤1024px).
   - Styling for hero: background‑size: cover; centered text with contrast overlay.
   - Navbar: sticky at top, hamburger menu for mobile (display:none on larger screens).
   - About section: max‑width container, readable line‑height, optional image styling.
   - Footer: dark background, centered text, small icons.
   - Ensure accessibility: focus outlines, sufficient color contrast.

3. workspace/T-012/script.js
   - DOMContentLoaded listener.
   - Smooth scroll behavior for internal anchor links.
   - Mobile menu toggle: add/remove a .open class on the nav list when hamburger icon is clicked.
   - No external libraries; pure vanilla JS.
   - No console.log debugging statements left.

4. workspace/T-012/assets/ (optional folder)
   - Placeholder hero.jpg (can be a 1‑pixel image or a comment indicating where to place the image).
   - Placeholder logo.svg.
   - Ensure the folder exists even if empty, to satisfy asset referenc

## Output constraints
- index.html exists and its file size is greater than 1KB
- style.css exists and contains at least one CSS variable definition
- script.js exists and includes a DOMContentLoaded event listener
- navbar links use href="#hero" and href="#about" and scroll to the correct sections
- about section contains at least two <p> elements with non‑empty text
- no file in the workspace/T-012 directory contains the strings TODO, FIXME, or lorem

## Provenance
Learned 2026-09-29 from ticket T-012.
Reviewer verdict: clean
