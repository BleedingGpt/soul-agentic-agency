# Skill: Build Python expense tracker CLI (auto-learned from T-009)

## Trigger
User asks for something like: Build Python expense tracker CLI.
Original request: Ishtiaq Ahmed requested building a Python CLI (expense.py) with add <amount> <note> and total commands, storing data in expenses.json using only the standard library, needed by today.
(source mail ID 1a0eb11ebcc1b94e)

## Process
1. Create `workspace/T-009/expense.py`.
   - Import `argparse`, `json`, `sys`, `pathlib`.
   - Define constants: `DATA_FILE = Path(__file__).with_name('expenses.json')`.
   - Implement a helper `load_expenses()` that reads the JSON file, returns a list, and creates an empty list if the file does not exist or is invalid.
   - Implement a helper `save_expenses(expenses)` that writes the list back to the JSON file with `indent=2`.
   - Define `cmd_add(args)`:
        * Parse `args.amount` as `float` (raise error on failure).
        * Append a dict `{"amount": amount, "note": args.note}` to the loaded list.
        * Save the list and print a confirmation message.
   - Define `cmd_total(_args)`:
        * Load expenses, compute `sum(e["amount"] for e in expenses)`.
        * Print the total formatted to two decimal places.
   - Set up `argparse.ArgumentParser` with sub‑parsers `add` and `total`.
   - Map sub‑commands to the functions above.
   - Include a `main()` guard (`if __name__ == "__main__": main()`).
   - Add docstrings and inline comments, but no TODO/FIXME placeholders.
2. Create `workspace/T-009/expenses.json` containing an empty JSON array (`[]`).
3. (Optional) Add a minimal `README.md` describing usage, but not required for acceptance.
4. Run a quick self‑test to ensure the script executes without errors and that `add` updates the JSON file and `total` reports the correct sum.

## Output constraints
- workspace/T-009/expense.py exists and its size is at least 500 bytes
- workspace/T-009/expenses.json exists and contains valid JSON (an array)
- expense.py runs without raising exceptions for `python expense.py add 10 test`
- after adding two expenses, `python expense.py total` outputs the correct summed amount
- expense.py contains no lines with TODO, FIXME, or placeholder lorem text
- expense.py uses only modules from the Python standard library

## Provenance
Learned 2026-09-29 from ticket T-009.
Reviewer verdict: clean
