import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

import todo

HERE = os.path.dirname(os.path.abspath(__file__))


class RemoveTest(unittest.TestCase):
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

    def run_process(self, *argv):
        """Run todo.py in a fresh interpreter, as a user would."""
        env = dict(os.environ, TODO_FILE=self.file)
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "todo.py"), *argv],
            capture_output=True, text=True, env=env,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def write_raw(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f)

    def read_raw(self):
        with open(self.file) as f:
            return f.read()

    def ids(self):
        return [i["id"] for i in todo.load()]

    def test_remove_middle_keeps_other_ids(self):
        for text in ("a", "b", "c"):
            self.run_cli("add", text)
        self.assertEqual(self.run_cli("remove", "2"), (0, "removed 2\n", ""))
        self.assertEqual(self.ids(), [1, 3])
        self.assertEqual([i["text"] for i in todo.load()], ["a", "c"])

    def test_removed_highest_id_not_reused_across_processes(self):
        self.run_process("add", "a")
        self.run_process("add", "b")
        self.assertEqual(self.run_process("remove", "2"), (0, "removed 2\n", ""))
        self.assertEqual(self.run_process("add", "c"), (0, "added 3\n", ""))

    def test_removing_every_item_keeps_counter(self):
        self.run_process("add", "a")
        self.run_process("add", "b")
        self.run_process("remove", "1")
        self.run_process("remove", "2")
        self.assertEqual(self.ids(), [])
        self.assertEqual(self.run_process("add", "c"), (0, "added 3\n", ""))

    def test_legacy_file_loads_and_highest_removal_is_not_reused(self):
        self.write_raw([{"id": 1, "text": "a"}, {"id": 2, "text": "b"}])
        self.assertEqual(self.ids(), [1, 2])
        self.assertEqual(self.run_cli("remove", "2"), (0, "removed 2\n", ""))
        self.assertEqual(self.run_cli("add", "c"), (0, "added 3\n", ""))

    def test_legacy_file_remove_final_item_keeps_counter(self):
        self.write_raw([{"id": 5, "text": "only"}])
        self.run_cli("remove", "5")
        self.assertEqual(self.run_cli("add", "next"), (0, "added 6\n", ""))

    def test_missing_file_starts_at_one(self):
        self.assertEqual(todo.load(), [])
        self.assertEqual(self.run_cli("add", "x"), (0, "added 1\n", ""))

    def test_remove_on_missing_file_is_unknown(self):
        self.assertEqual(self.run_cli("remove", "1"), (1, "", "no item 1\n"))
        self.assertFalse(os.path.exists(self.file))

    def test_saved_file_is_envelope(self):
        self.run_cli("add", "a")
        self.run_cli("remove", "1")
        self.assertEqual(json.loads(self.read_raw()), {"items": [], "next_id": 2})

    def test_other_fields_preserved(self):
        self.write_raw({"items": [{"id": 1, "text": "a", "done": True},
                                  {"id": 2, "text": "b"}], "next_id": 7})
        self.run_cli("remove", "2")
        self.assertEqual(json.loads(self.read_raw()),
                         {"items": [{"id": 1, "text": "a", "done": True}], "next_id": 7})

    def test_unknown_id_errors_without_writing(self):
        self.run_cli("add", "a")
        before = self.read_raw()
        for arg in ("9", "0", "-1"):
            self.assertEqual(self.run_cli("remove", arg), (1, "", f"no item {arg}\n"))
        self.assertEqual(self.read_raw(), before)

    def test_bad_usage_exits_2_without_writing(self):
        self.run_cli("add", "a")
        before = self.read_raw()
        for argv in (["remove"], ["remove", "x"], ["remove", "1", "2"], ["remove", "1.5"]):
            code, out, err = self.run_cli(*argv)
            self.assertEqual((code, out), (2, ""), argv)
            self.assertTrue(err.startswith("usage:"), argv)
        self.assertEqual(self.read_raw(), before)


if __name__ == "__main__":
    unittest.main()
