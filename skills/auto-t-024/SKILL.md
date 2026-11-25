# Skill: Construct demo calendar app (auto-learned from T-024)

## Trigger
User asks for something like: Construct demo calendar app.
Original request: Ishtiaq Ahmed (user@example.com) requested a demo calendar app to be constructed.
(source mail ID 1a0eb8a7d23a8e14)

## Process
1. Create workspace/T-024/index.html
   - Boilerplate HTML5 with <head> linking style.css and script.js.
   - Hero section with <h1>Demo Calendar App</h1> and brief description.
   - <div id="calendar"></div> placeholder where JS will render the month grid.
   - Navigation buttons (Prev, Next) and a button to open "Add Event" modal.
   - Modal markup hidden by default for entering event title and date.
   - Footer with author credit.
2. Create workspace/T-024/style.css
   - Reset/normalize basics.
   - Styles for .hero, .calendar (grid layout 7 columns), .day cells, navigation buttons, and modal overlay.
   - Responsive adjustments for mobile view.
3. Create workspace/T-024/script.js
   - Immediately‑invoked function that defines initCalendar().
   - Build current month grid, attach click handlers to navigation buttons to shift month.
   - Simple in‑memory event storage; when user adds an event via modal, display it inside the appropriate day cell.
   - Export initCalendar and call it on DOMContentLoaded.
4. Create workspace/T-024/README.md
   - Short description, how to open index.html, brief overview of the code structure, and note that no external dependencies are required.
5. Add a .gitignore file (optional) to exclude node_modules if any future extensions are added.
6. Run a quick sanity check: open index.html in a browser, verify month view appears, navigation works, and adding an event shows text in the day cell.

## Output constraints
- workspace/T-024/index.html exists and its size is greater than 1KB
- workspace/T-024/style.css exists and contains a CSS rule for a .calendar class
- workspace/T-024/script.js exists and defines a function named initCalendar
- No file in workspace/T-024 contains the strings TODO, FIXME, or lorem
- Opening index.html in a browser displays a month grid with navigation arrows and an Add Event button
- Adding an event via the modal updates the corresponding day cell without page reload

## Provenance
Learned 2026-09-29 from ticket T-024.
Reviewer verdict: clean
