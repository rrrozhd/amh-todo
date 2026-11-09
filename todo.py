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
    if argv in (["list"], ["list", "--open"]):
        for item in load():
            done = item.get("done", False)
            if argv == ["list", "--open"] and done:
                continue
            marker = "x" if done else " "
            print(f"{item['id']}. [{marker}] {item['text']}")
        return 0
    print("usage: todo.py add TEXT | list [--open] | done ID | remove ID | edit ID TEXT",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
