"""A tiny to-do list kept in a JSON file (todo.json, or the path in TODO_FILE).

The file holds {"items": [...], "next_id": N}. next_id only ever grows, so a
removed id is never handed out again. Files written by the seed version are a
bare list of items; they still load, with next_id taken as max id + 1.
"""
import json
import os
import sys

USAGE = "usage: todo.py add TEXT | list [--open] | done ID | remove ID | edit ID TEXT"


def path():
    return os.environ.get("TODO_FILE", "todo.json")


def _read():
    """Return (items, next_id) from disk, accepting the seed's bare-list format."""
    try:
        with open(path()) as f:
            data = json.load(f)
    except FileNotFoundError:
        return [], 1
    if isinstance(data, list):
        items, next_id = data, 1
    else:
        items, next_id = data.get("items", []), data.get("next_id", 1)
    next_id = max(next_id, max((i["id"] for i in items), default=0) + 1)
    return items, next_id


def load():
    return _read()[0]


def save(items):
    """Write items, keeping the high-water next_id already on disk."""
    _, next_id = _read()
    next_id = max(next_id, max((i["id"] for i in items), default=0) + 1)
    with open(path(), "w") as f:
        json.dump({"items": items, "next_id": next_id}, f, indent=2)


def add(text):
    items, next_id = _read()
    item = {"id": next_id, "text": text}
    items.append(item)
    save(items)
    return item


def remove(item_id):
    """Delete the item with item_id; return False if there is none."""
    items = load()
    kept = [i for i in items if i["id"] != item_id]
    if len(kept) == len(items):
        return False
    save(kept)
    return True


def parse_id(arg):
    """Return arg as an int id, or None if it is not an integer."""
    try:
        return int(arg)
    except ValueError:
        return None


def usage():
    print(USAGE, file=sys.stderr)
    return 2


def no_item(item_id):
    print(f"no item {item_id}", file=sys.stderr)
    return 1


def main(argv):
    if len(argv) >= 2 and argv[0] == "add":
        item = add(" ".join(argv[1:]))
        print(f"added {item['id']}")
        return 0
    if argv == ["list"]:
        for item in load():
            print(f"{item['id']}. {item['text']}")
        return 0
    if argv and argv[0] == "remove":
        item_id = parse_id(argv[1]) if len(argv) == 2 else None
        if item_id is None:
            return usage()
        if not remove(item_id):
            return no_item(item_id)
        print(f"removed {item_id}")
        return 0
    if argv and argv[0] == "edit":
        item_id = parse_id(argv[1]) if len(argv) >= 3 else None
        if item_id is None:
            return usage()
        items = load()
        for item in items:
            if item["id"] == item_id:
                item["text"] = " ".join(argv[2:])
                save(items)
                print(f"edited {item_id}")
                return 0
        return no_item(item_id)
    return usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
