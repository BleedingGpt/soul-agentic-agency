# Skill: Write a Python dice roller CLI (auto-learned from T-005)

## Trigger
User asks for something like: Write a Python dice roller CLI.
Original request: dice.py: roll NdS notation (e.g. 2d6), secrets module, zero dependencies.

## Process
1. Create file `workspace/T-005/dice.py`.
   - Add a Unix shebang (`#!/usr/bin/env python3`).
   - Include module docstring describing purpose and usage.
   - Import only `argparse`, `re`, `secrets`, and `sys` from the standard library.
2. Implement argument parsing:
   - Use `argparse.ArgumentParser` with a positional argument `notation` (e.g., "2d6").
   - Provide `-h/--help` automatically.
3. Parse the NdS notation:
   - Compile a regex `^(?P<count>\d*)d(?P<sides>\d+)$`.
   - Default count to 1 if omitted (e.g., "d20").
   - Convert captured groups to integers and validate that both are > 0.
4. Generate rolls using `secrets.randbelow(sides) + 1` inside a list comprehension, iterating `count` times.
5. Compute the total sum of rolls.
6. Print results:
   - If `count` > 1, output "Rolls: X, Y, Z" followed by "Total: N" on the same line.
   - If `count` == 1, output just the single roll value.
7. Implement error handling:
   - If the notation does not match the regex or contains non‑positive numbers, print an error to `stderr` and exit with status code 1.
8. Ensure the script is executable (`chmod +x dice.py` is not part of code but implied for CLI use).
9. Add a `if __name__ == "__main__":` guard to invoke the main function.
10. Verify there are no placeholder comments such as TODO, FIXME, or lorem ipsum.

Design notes:
- Using `secrets` guarantees cryptographically‑secure randomness without extra dependencies.
- Regular expression parsing keeps the logic concise and avoids manual string splitting errors.
- The script remains a single file for simplicity and zero‑dependency compliance.
- Output format is deterministic for testing: a comma‑separated list of rolls followed by the total, making it easy to assert correctness.

## Output constraints
- dice.py exists in workspace/T-005 and starts with a shebang line
- dice.py imports only argparse, re, secrets, and sys from the standard library
- Running `python dice.py 2d6` prints a comma‑separated list of two integers and a total sum on stdout
- Providing an invalid notation (e.g., `abc`) causes the script to write an error message to stderr and exit with a non‑zero status code
- dice.py contains no lines with TODO, FIXME, or lorem placeholder comments

## Provenance
Learned 2026-09-25 from ticket T-005.
Reviewer verdict: clean
