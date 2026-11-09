import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import todo


class EditTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.file = Path(directory.name) / "todo.json"
        environment = patch.dict(os.environ, {"TODO_FILE": str(self.file)})
        environment.start()
        self.addCleanup(environment.stop)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = todo.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_edit_legacy_item_preserves_order_and_other_fields(self):
        items = [
            {"id": 8, "text": "keep", "done": False},
            {"id": 2, "text": "old", "tag": "work"},
            {"id": 11, "text": "also keep", "done": True},
        ]
        self.file.write_text(json.dumps(items))
        self.assertEqual(self.run_cli("edit", "2", "new", "text"),
                         (0, "edited 2\n", ""))
        items[1]["text"] = "new text"
        self.assertEqual(todo.load(), items)
        self.assertFalse(todo.load()[1].get("done", False))

    def test_edit_completed_item_persists_in_fresh_process(self):
        self.file.write_text(json.dumps([
            {"id": 4, "text": "old", "done": True, "note": "keep"}
        ]))
        result = subprocess.run(
            [sys.executable, str(Path(todo.__file__).resolve()),
             "edit", "+4", "new text"],
            capture_output=True, text=True,
        )
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, "edited 4\n", ""))
        self.assertEqual(todo.load(), [
            {"id": 4, "text": "new text", "done": True, "note": "keep"}
        ])

    def test_unknown_id_leaves_file_unchanged(self):
        self.file.write_text('[{"id": 7, "text": "keep"}]\n')
        before = self.file.read_bytes()
        for item_id in ("99", "0", "-1"):
            with self.subTest(item_id=item_id):
                self.assertEqual(self.run_cli("edit", item_id, "new"),
                                 (1, "", f"no item {int(item_id)}\n"))
                self.assertEqual(self.file.read_bytes(), before)

    def test_unknown_id_does_not_create_storage(self):
        self.assertEqual(self.run_cli("edit", "2", "new"),
                         (1, "", "no item 2\n"))
        self.assertFalse(self.file.exists())

    def test_wrong_usage_leaves_file_unchanged(self):
        self.file.write_text('[{"id": 7, "text": "keep"}]\n')
        before = self.file.read_bytes()
        for args in (("edit",), ("edit", "7"), ("edit", "oops", "text"),
                     ("edit", "1.5", "text")):
            with self.subTest(args=args):
                code, out, err = self.run_cli(*args)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("usage: "), err)
                self.assertEqual(self.file.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
