# Skill: Create an app (auto-learned from T-014)

## Trigger
User asks for something like: Create an app.
Original request: Ishtiaq Ahmed requested to create an app (email received Tue, 29 Sep 2026).
(source mail ID 1a0eb33e1ebac263)

## Process
1. workspace/T-014/README.md – brief project description, setup instructions, and how to run the app.
2. workspace/T-014/package.json – Node.js project manifest with name, version, scripts ("start": "node server.js"), and Express as a dependency.
3. workspace/T-014/server.js – Minimal Express server that serves static files from a 'public' directory and listens on PORT 3000 (or env var).
4. workspace/T-014/public/index.html – Basic HTML5 page containing:
   - <head> with meta charset, viewport, title, link to style.css.
   - <body> with a hero section (h1, subtitle), a navigation bar, a main content placeholder, and a footer.
   - Script tag loading app.js.
5. workspace/T-014/public/style.css – Simple responsive CSS styling for the hero, nav, and layout; no placeholder lorem text.
6. workspace/T-014/public/app.js – Small JavaScript file initializing a console log and placeholder for future interactivity.
7. workspace/T-014/.gitignore – Exclude node_modules and OS‑specific files.
8. workspace/T-014/.eslintrc.json – Optional lint config to enforce no TODO/FIXME comments.
Design notes: • Keep all content generic (e.g., "Welcome to Your App") so it can be renamed later. • Ensure files are UTF‑8 encoded and use LF line endings. • No hard‑coded secrets; environment variables are referenced only for the port.
9. Verify that the project builds and runs: `npm install` then `npm start` should launch the server and serve index.html at http://localhost:3000.

## Output constraints
- workspace/T-014/package.json exists and includes an "express" dependency and a "start" script
- workspace/T-014/server.js exists and starts an Express server listening on a port
- workspace/T-014/public/index.html exists and its file size is greater than 1KB
- All source files under workspace/T-014 contain no TODO, FIXME, or lorem placeholder text
- README.md exists and contains at least three lines of usage instructions
- Running `npm start` from workspace/T-014 launches the server without errors and serves index.html

## Provenance
Learned 2026-09-29 from ticket T-014.
Reviewer verdict: clean
