# amh-todo

A tiny to-do CLI: `python todo.py add TEXT`, `python todo.py list`. `python todo.py remove ID`. Tests: `python -m unittest`.

Storage: todo.json is `{"items": [...], "next_id": N}`. Use `load()`/`save(items)`; `save` keeps the
stored `next_id`, so removed ids are never reused. Seed-format files (a bare list) still load.
