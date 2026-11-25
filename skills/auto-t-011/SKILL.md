# Skill: Create single-file coming-soon page (auto-learned from T-011)

## Trigger
User asks for something like: Create single-file coming-soon page.
Original request: Ishtiaq Ahmed requested a single-file index.html website with header 'S.O.U.L.', a 'Launching Soon' section, a paragraph about the ticket agency, and a footer with contact test@example.com, zero dependencies, needed by today (29 Sep 2026).
(source mail ID 1a0eb18d866ceea4)

## Process
1. Create workspace/T-011/index.html
   - Add <!DOCTYPE html> and <html lang="en"> structure.
   - Include <meta charset="UTF-8"> and <meta name="viewport" content="width=device-width, initial-scale=1.0"> for responsiveness.
   - Embed a <style> block that defines simple layout: body centering, header/footer styling, font family, and spacing. No external CSS files.
   - Body content:
     a. <header> with an <h1> containing the exact text "S.O.U.L.".
     b. <main> containing:
        i. <section class="launch"> with an <h2> "Launching Soon".
        ii. <p> describing the ticket agency (e.g., "We are the S.O.U.L. agency, delivering timely ticket solutions.").
     c. <footer> with a <p> that includes the contact email "test@example.com".
   - Ensure there are no <link> or <script src> tags, and no placeholder comments like TODO/FIXME/lorem.
2. Validate the file size is reasonable (>500 bytes) to confirm content is present.
3. Commit the file to the workspace.

## Output constraints
- index.html exists in workspace/T-011/
- index.html size is greater than 500 bytes
- The file contains the exact header text "S.O.U.L."
- The file contains the phrase "Launching Soon"
- The footer includes the email address test@example.com
- No external <link> or <script src> tags are present and no TODO/FIXME placeholders exist

## Provenance
Learned 2026-09-29 from ticket T-011.
Reviewer verdict: clean
