# Skill: Build Python CLI todo app (auto-learned from T-006)

## Trigger
User asks for something like: Build Python CLI todo app.
Original request: Ishtiaq Ahmed requested a Python CLI todo app (add and list tasks from a JSON file, zero dependencies, single file todo.py using argparse) on 27 Sep 2026.
(source mail ID 1a0df06e4f4cdaeb)

## Process
1. Create workspace/T-006/todo.py
   - Shebang line (#!/usr/bin/env python3) and UTF‑8 encoding comment.
   - Import only stdlib modules: argparse, json, os, sys.
   - Define constants: DEFAULT_DB = 'tasks.json'.
   - Implement helper functions:
     a) load_tasks(path) – returns list, creates empty file if missing.
     b) save_tasks(path, tasks) – writes JSON with indent=2.
   - Implement command functions:
     a) cmd_add(args): load tasks, append args.title (and optional args.priority), save, print confirmation.
     b) cmd_list(args): load tasks, if empty print "No tasks.", else iterate and print index and title.
   - Build argparse parser with sub‑parsers "add" and "list".
     - add: positional "title" (string), optional "--priority" (int, default 1).
     - list: optional "--db" to override JSON file location.
   - Main guard (if __name__ == '__main__') to parse args and dispatch to the appropriate command function.
2. Create workspace/T-006/README.md (optional but helpful)
   - Brief description, usage examples, and note that the app requires only Python 3 standard library.
3. Add a .gitignore file to exclude the generated tasks.json during version control (optional).
4. Run a quick self‑test locally to ensure:
   - Adding a task creates/updates tasks.json.
   - Listing tasks prints the stored entries.
   - Running without arguments shows help.
5. Commit the files.
Design notes:
- Keep all logic in a single file; no external modules.
- Use json.dump/load with ensure_ascii=False for proper Unicode handling.
- Provide clear error messages for file I/O issues.
- Keep code size modest but >2KB to satisfy size check.
- No placeholder comments like TODO/FIXME; all functions fully implemented.

## Output constraints
- workspace/T-006/todo.py exists and its size is greater than 2KB
- todo.py imports only argparse, json, os, and sys from the standard library
- todo.py defines an argparse sub‑command named 'add' that accepts a positional title argument
- todo.py defines an argparse sub‑command named 'list' that prints stored tasks
- Running 'python todo.py add "Test task"' creates or updates a JSON file named tasks.json in the same directory
- Running 'python todo.py list' outputs the list of tasks without raising an exception

## Provenance
Learned 2026-09-27 from ticket T-006.
Reviewer verdict: clean
