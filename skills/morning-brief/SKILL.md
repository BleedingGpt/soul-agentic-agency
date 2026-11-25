# Skill: morning-brief

## Trigger
User asks for an inbox summary, a morning brief, or "anything new about X, tell me on WhatsApp".

## Process
1. `gmail_search` with the topic (or "newer_than:1d" for everything fresh).
2. Condense to ≤5 bullets: who, what, what action is needed.
3. `wa_send` the brief to the user's self-chat — ONLY after approval gate passes.

## Output constraints
- Bullets, not paragraphs. Numbers and deadlines preserved verbatim.
- Never invent mail that was not in the observations.
- If inbox is empty, say so in one line — do not pad.
