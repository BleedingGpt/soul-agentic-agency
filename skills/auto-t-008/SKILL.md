# Skill: Decide on manuscript transfer (auto-learned from T-008)

## Trigger
User asks for something like: Decide on manuscript transfer.
Original request: Elsevier reminded Mr. Ahmed to decide whether to transfer manuscript SCICO-D-26-00707 to suggested journals
(source mail ID 1a0e1c2e31bd7051)

## Process
1. Create workspace/T-008/decision.md
   - Title: "Manuscript Transfer Decision – SCICO‑D‑26‑00707"
   - Sections:
     * Background (summary of Elsevier reminder and manuscript details)
     * Transfer Options (list of suggested journals with brief scope notes)
     * Evaluation Criteria (impact factor, audience, open‑access policy, timeline)
     * Recommendation (clear yes/no decision with justification)
     * Next Steps (actions for the author and Elsevier contact)
   - Ensure the file is at least 1 KB of prose.
2. Create workspace/T-008/email_template.txt
   - Subject line: "Decision on Transfer of Manuscript SCICO‑D‑26‑00707"
   - Body includes a polite greeting, reference to the reminder email (ID 1a0e1c2e31bd7051), the decision (accept or decline), brief rationale, and request for confirmation of next steps.
   - No placeholder tags like {{...}}; all text is concrete.
   - Ensure the file is at least 500 bytes.
3. Add a .gitkeep file in workspace/T-008/ if the folder would otherwise be empty after creation (to satisfy repository tooling).

## Output constraints
- workspace/T-008/decision.md exists and its size is >1024 bytes
- workspace/T-008/email_template.txt exists and its size is >500 bytes
- Both files contain no TODO, FIXME, or lorem ipsum placeholder text
- No embedded API keys, passwords, or other secrets appear in any file
- The email_template.txt includes a subject line and a complete email body

## Provenance
Learned 2026-09-28 from ticket T-008.
Reviewer verdict: clean
