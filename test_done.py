import contextlib
import io
import json
import os
import tempfile
import unittest

import todo


class DoneTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = os.path.join(self.dir.name, "todo.json")
        os.environ["TODO_FILE"] = self.file

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = todo.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def read_bytes(self):
        with open(self.file, "rb") as f:
            return f.read()

    def test_done_marks_item_and_persists(self):
        self.run_cli("add", "a")
        self.run_cli("add", "b")
        self.assertEqual(self.run_cli("done", "2"), (0, "done 2\n", ""))
        items = {i["id"]: i for i in todo.load()}
        self.assertTrue(items[2]["done"])
        self.assertFalse(items[1].get("done", False))
        self.assertEqual(items[2]["text"], "b")

    def test_done_is_idempotent(self):
        self.run_cli("add", "a")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("done", "1"), (0, "done 1\n", ""))
        self.assertEqual(todo.load(), [{"id": 1, "text": "a", "done": True}])

    def test_done_preserves_other_fields_and_ids(self):
        with open(self.file, "w") as f:
            json.dump([{"id": 3, "text": "x", "extra": 7}, {"id": 5, "text": "y"}], f)
        self.assertEqual(self.run_cli("done", "5")[0], 0)
        self.assertEqual(
            todo.load(),
            [{"id": 3, "text": "x", "extra": 7}, {"id": 5, "text": "y", "done": True}],
        )

    def test_done_on_legacy_seed_file(self):
        with open(self.file, "w") as f:
            json.dump([{"id": 1, "text": "old"}], f, indent=2)
        self.assertEqual(self.run_cli("done", "1"), (0, "done 1\n", ""))
        self.assertTrue(todo.load()[0]["done"])

    def test_unknown_id_exits_1_without_writing(self):
        self.run_cli("add", "a")
        before = self.read_bytes()
        for arg in ("9", "0", "-1"):
            code, out, err = self.run_cli("done", arg)
            self.assertEqual((code, out, err), (1, "", f"no item {int(arg)}\n"))
        self.assertEqual(self.read_bytes(), before)

    def test_unknown_id_echoes_parsed_int(self):
        self.run_cli("add", "a")
        self.assertEqual(self.run_cli("done", "+09"), (1, "", "no item 9\n"))

    def test_bad_usage_exits_2_without_writing(self):
        self.run_cli("add", "a")
        before = self.read_bytes()
        for argv in (("done",), ("done", "x"), ("done", "1", "2"), ("done", "1.5")):
            code, out, err = self.run_cli(*argv)
            self.assertEqual(code, 2, argv)
            self.assertEqual(out, "")
            self.assertTrue(err.startswith("usage:"), err)
        self.assertEqual(self.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
