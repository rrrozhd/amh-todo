"""A tiny to-do list kept in a JSON file (todo.json, or the path in TODO_FILE)."""
import json
import os
import sys


def path():
    return os.environ.get("TODO_FILE", "todo.json")


def load():
    try:
        with open(path()) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save(items):
    with open(path(), "w") as f:
        json.dump(items, f, indent=2)


def add(text):
    items = load()
    item = {"id": max((i["id"] for i in items), default=0) + 1, "text": text}
    items.append(item)
    save(items)
    return item


USAGE = "usage: todo.py add TEXT | list [--open] | done ID | remove ID | edit ID TEXT"


def done(item_id):
    """Mark item item_id done; return False if there is no such item."""
    items = load()
    for item in items:
        if item["id"] == item_id:
            item["done"] = True
            save(items)
            return True
    return False


def main(argv):
    if argv and argv[0] == "done":
        try:
            if len(argv) != 2:
                raise ValueError
            item_id = int(argv[1])
        except ValueError:
            print(USAGE, file=sys.stderr)
            return 2
        if not done(item_id):
            print(f"no item {item_id}", file=sys.stderr)
            return 1
        print(f"done {item_id}")
        return 0
    if len(argv) >= 2 and argv[0] == "add":
        item = add(" ".join(argv[1:]))
        print(f"added {item['id']}")
        return 0
    if argv == ["list"]:
        for item in load():
            print(f"{item['id']}. {item['text']}")
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
