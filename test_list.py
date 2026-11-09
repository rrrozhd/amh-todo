import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import todo


class ListTest(unittest.TestCase):
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

    def write_items(self, items):
        self.file.write_text(json.dumps(items, indent=2))

    def test_list_formats_mixed_and_legacy_items_in_stored_order(self):
        self.write_items([
            {"id": 7, "text": "legacy task"},
            {"id": 3, "text": "finished", "done": True},
            {"id": 12, "text": "still open", "done": False},
        ])
        before = self.file.read_bytes()
        self.assertEqual(self.run_cli("list"), (
            0, "7. [ ] legacy task\n3. [x] finished\n12. [ ] still open\n", ""))
        self.assertEqual(self.file.read_bytes(), before)

    def test_open_filter_keeps_legacy_items_and_preserves_file(self):
        self.write_items([
            {"id": 7, "text": "legacy task", "extra": "retained"},
            {"id": 3, "text": "finished", "done": True},
            {"id": 12, "text": "still open", "done": False},
        ])
        before = self.file.read_bytes()
        self.assertEqual(self.run_cli("list", "--open"), (
            0, "7. [ ] legacy task\n12. [ ] still open\n", ""))
        self.assertEqual(self.file.read_bytes(), before)

    def test_empty_and_missing_lists_are_empty_and_read_only(self):
        for args in [("list",), ("list", "--open")]:
            with self.subTest(args=args, missing=True):
                self.assertEqual(self.run_cli(*args), (0, "", ""))
                self.assertFalse(self.file.exists())
        self.write_items([])
        for args in [("list",), ("list", "--open")]:
            with self.subTest(args=args, missing=False):
                self.assertEqual(self.run_cli(*args), (0, "", ""))
                self.assertEqual(self.file.read_text(), "[]")

    def test_all_done_items_are_filtered_out(self):
        self.write_items([{"id": 2, "text": "finished", "done": True}])
        self.assertEqual(self.run_cli("list", "--open"), (0, "", ""))

    def test_unsupported_list_arguments_print_usage_without_writing(self):
        self.write_items([{"id": 1, "text": "retained"}])
        before = self.file.read_bytes()
        for args in [("--done",), ("extra",), ("--open", "extra"),
                     ("--open", "--open")]:
            with self.subTest(args=args):
                code, out, err = self.run_cli("list", *args)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("usage: todo.py "))
                self.assertEqual(self.file.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
