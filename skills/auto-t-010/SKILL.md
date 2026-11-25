# Skill: Build single-file coming-soon page (auto-learned from T-010)

## Trigger
User asks for something like: Build single-file coming-soon page.
Original request: Ishtiaq Ahmed requested building a single-file website (index.html) with header 'S.O.U.L.', a 'Launching Soon' paragraph about the ticket agency, and a footer with contact test@example.com, needed by today.
(source mail ID 1a0eb11372d1aca2)

## Process
1. Create file workspace/T-010/index.html.
   - Add a <!DOCTYPE html> document with <html>, <head>, and <body> sections.
   - In <head>, set <meta charset="UTF-8"> and a <title>Launching Soon – S.O.U.L.</title>.
   - Include minimal inline CSS to style the header, paragraph, and footer (centered layout, simple fonts).
   - In <body>:
     a) <header> element containing an <h1> with the exact text "S.O.U.L.".
     b) <main> element with a <p> that includes the phrase "Launching Soon" and a brief description of the ticket agency.
     c) <footer> element with a mailto link displaying "test@example.com".
   - Ensure no placeholder text (e.g., Lorem ipsum) or TODO/FIXME comments remain.
2. Validate the file size is reasonable (>2 KB) to confirm content is present.

## Output constraints
- workspace/T-010/index.html exists
- index.html size is greater than 2KB
- index.html contains an <h1> element with the exact text "S.O.U.L."
- index.html contains a paragraph that includes the phrase "Launching Soon"
- index.html footer includes the email address test@example.com
- index.html contains no TODO, FIXME, or lorem placeholder text

## Provenance
Learned 2026-09-29 from ticket T-010.
Reviewer verdict: clean
