import contextlib
import io
import os
import tempfile
import unittest

import todo


class TodoTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        os.environ["TODO_FILE"] = os.path.join(self.dir.name, "todo.json")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = todo.main(list(argv))
        return code, out.getvalue()

    def test_add_then_list(self):
        self.assertEqual(self.run_cli("add", "buy", "milk"), (0, "added 1\n"))
        self.run_cli("add", "call mom")
        self.assertEqual(self.run_cli("list"), (0, "1. buy milk\n2. call mom\n"))

    def test_unknown_command_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(todo.main(["nope"]), 2)


if __name__ == "__main__":
    unittest.main()
