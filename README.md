# amh-todo

A tiny to-do CLI: `python todo.py add TEXT`, `python todo.py list`. `python todo.py remove ID`. Tests: `python -m unittest`.

`python todo.py edit ID TEXT` replaces an item's text and prints `edited ID`.
It keeps the item's ID, completion status, and other fields. An unknown ID prints
`no item ID` to stderr and exits 1; a missing or malformed ID or missing text
prints usage and exits 2. These errors do not change the file. Set `TODO_FILE`
to use a separate JSON file while trying commands or debugging.

Storage: todo.json is `{"items": [...], "next_id": N}`. Use `load()`/`save(items)`; `save` keeps the
stored `next_id`, so removed ids are never reused. Seed-format files (a bare list) still load.
