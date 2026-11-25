# Skill: Build Python CLI todo app (auto-learned from T-007)

## Trigger
User asks for something like: Build Python CLI todo app.
Original request: Ishtiaq Ahmed requested on Sun, 27 Sep 2026 to build a Python CLI todo app (single file todo.py, zero dependencies) that can add and list tasks from a JSON file using argparse.
(source mail ID 1a0df139cff808c6)

## Process
1. Create file workspace/T-007/todo.py
   - Shebang line (optional) and module docstring describing the CLI.
   - Imports: argparse, json, pathlib, sys.
   - Define constant TASK_FILE = Path(__file__).with_name('tasks.json').
   - Helper functions:
     a) load_tasks() -> list: reads TASK_FILE if it exists, returns list, else []
     b) save_tasks(tasks): writes list to TASK_FILE with json.dump(indent=2).
   - Command functions:
     a) cmd_add(args): loads tasks, appends args.task (string), saves, prints confirmation.
     b) cmd_list(args): loads tasks, if empty prints "No tasks.", else iterates and prints "{i}. {task}".
   - main():
     * Create top‑level ArgumentParser(prog='todo', description='Simple CLI todo app').
     * Add subparsers for 'add' and 'list'.
       - add: positional argument 'task' (string), help='Task description'.
       - list: no extra args.
     * Set defaults to appropriate command functions.
     * Parse args and invoke the selected function.
   - Guard: if __name__ == '__main__': main()
2. Ensure the file contains no placeholder comments like TODO/FIXME and no hard‑coded secrets.
3. The file will be >100 bytes to satisfy size check.
4. No external packages are imported; only standard library modules are used.
5. The script will create or update tasks.json in the same folder, fulfilling persistence.
6. Provide clear, user‑friendly output for both commands.

## Output constraints
- workspace/T-007/todo.py exists
- workspace/T-007/todo.py size is greater than 100 bytes
- todo.py contains imports of argparse and json (no missing imports)
- todo.py does not contain any TODO, FIXME, or lorem placeholder comments
- Running 'python todo.py add "Sample task"' creates or updates a tasks.json file in the same directory
- Running 'python todo.py list' prints each stored task prefixed by its index number

## Provenance
Learned 2026-09-27 from ticket T-007.
Reviewer verdict: clean
