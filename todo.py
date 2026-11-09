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


def main(argv):
    if len(argv) >= 2 and argv[0] == "add":
        item = add(" ".join(argv[1:]))
        print(f"added {item['id']}")
        return 0
    if argv == ["list"]:
        for item in load():
            print(f"{item['id']}. {item['text']}")
        return 0
    print("usage: todo.py add TEXT | list", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
