# Skill: Construct calendar app (auto-learned from T-023)

## Trigger
User asks for something like: Construct calendar app.
Original request: Ishtiaq Ahmed requested construction of a calendar app on 29 Sep 2026.
(source mail ID 1a0eb8a09bb1008a)

## Process
1. workspace/T-023/index.html – basic HTML5 skeleton with a <header> (title and navigation buttons), a <section id="calendar" class="calendar"></section> for the month grid, and a hidden <dialog id="event-modal"> for adding events. Include links to style.css and app.js.
2. workspace/T-023/style.css – CSS reset, layout for the hero/header, responsive grid for the calendar (7 columns, auto rows), styling for day cells, selected day highlight, and modal appearance. Ensure at least one rule targets the .calendar class.
3. workspace/T-023/app.js – JavaScript module that:
   • Generates the current month’s days and injects them into #calendar.
   • Handles previous/next month navigation.
   • Opens the event modal on day click, saves events to localStorage, and re‑renders event markers.
   • Exposes an initCalendar() function called on DOMContentLoaded.
4. workspace/T-023/README.md – brief usage instructions, list of files, and note that the app works offline.
5. workspace/T-023/.gitignore – ignore node_modules (if any) and OS files; no secrets.
Design notes: • Use semantic HTML (header, main, section, dialog). • Keep all text user‑visible (no lorem ipsum). • Ensure the app is responsive (mobile‑friendly). • No external libraries; pure vanilla JS/CSS for easy verification.

## Output constraints
- index.html exists and its file size is greater than 2KB
- style.css exists and contains a CSS rule that selects the .calendar class
- app.js exists and defines a function named initCalendar
- No file in workspace/T-023 contains the strings TODO, FIXME, or lorem
- README.md exists and mentions the three core files (index.html, style.css, app.js)

## Provenance
Learned 2026-09-29 from ticket T-023.
Reviewer verdict: clean
