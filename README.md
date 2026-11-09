# amh-todo

A tiny to-do CLI: `python todo.py add TEXT`, `python todo.py list`.
Use `python todo.py remove ID` to delete an item while keeping other IDs intact.
Use `python todo.py list --open` to show only unfinished items.
Lists keep the stored order and show `[ ]` for open items and `[x]` for completed
items. Older items without a `done` field count as open. Listing never writes
the data file.

Data lives in `todo.json`; set `TODO_FILE` to use a different path. The program
uses only the Python standard library and requires no installation.

Run `python -m unittest` for all tests, or `python -m unittest -v test_list`
for list formatting, filtering, legacy files, usage errors and read-only checks.

Storage: todo.json is `{"items": [...], "next_id": N}`. Use `load()`/`save(items)`; `save` keeps the
stored `next_id`, so removed ids are never reused. Seed-format files (a bare list) still load.
