import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compose-souls.py"
spec = importlib.util.spec_from_file_location("compose_souls", SCRIPT)
composer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composer)


class ComposerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "souls"
        self.root.mkdir()
        (self.root / "a.md").write_text("  # A\n\n", encoding="utf-8")
        (self.root / "b.md").write_text("B — text\n", encoding="utf-8")
        self.targets = {"prime": {"output": "generated/prime.md", "parts": ["a.md", "b.md"]}}

    def run_composer(self, *args):
        (self.root / "composition.json").write_text(json.dumps({"version": 1, "targets": self.targets}), encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            return composer.main(["--souls-dir", str(self.root), *args])

    def test_deterministic_output_check_and_mode(self):
        self.assertEqual(self.run_composer("--check"), 1)
        self.assertFalse((self.root / "generated").exists())
        self.assertEqual(self.run_composer(), 0)
        output = self.root / "generated/prime.md"
        expected = f"{composer.HEADER}\n\n# A\n\nB — text\n".encode("utf-8")
        self.assertEqual(output.read_bytes(), expected)
        output.chmod(0o640)
        self.assertEqual(self.run_composer(), 0)
        self.assertEqual(output.read_bytes(), expected)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o640)
        self.assertEqual(self.run_composer("--check"), 0)
        output.write_text("stale", encoding="utf-8")
        self.assertEqual(self.run_composer("--check"), 1)
        self.assertEqual(output.read_text(), "stale")

    def test_missing_source_does_not_partially_overwrite(self):
        self.assertEqual(self.run_composer(), 0)
        output = self.root / "generated/prime.md"
        before = output.read_bytes()
        (self.root / "a.md").write_text("changed", encoding="utf-8")
        self.targets["rose"] = {"output": "generated/rose.md", "parts": ["missing.md"]}
        self.assertEqual(self.run_composer(), 1)
        self.assertEqual(output.read_bytes(), before)
        self.assertFalse((self.root / "generated/rose.md").exists())

    def test_escaping_paths_and_symlinks(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        for field, value in [("output", "../escape.md"), ("output", "link/out.md"),
                             ("output", str(outside / "absolute.md")), ("parts", ["../outside/source.md"])]:
            with self.subTest(field=field, value=value):
                self.targets["prime"] = {"output": "generated/prime.md", "parts": ["a.md"]}
                self.targets["prime"][field] = value
                self.assertEqual(self.run_composer(), 1)
        destination = self.root / "out.md"
        destination.symlink_to(outside / "missing.md")
        self.targets["prime"] = {"output": "out.md", "parts": ["a.md"]}
        self.assertEqual(self.run_composer(), 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_collisions_across_targets_and_manifest(self):
        for output in ["a.md", "composition.json", "generated/prime.md"]:
            with self.subTest(output=output):
                self.targets["rose"] = {"output": output, "parts": ["b.md"]}
                self.assertEqual(self.run_composer("--target", "prime"), 1)
        self.assertFalse((self.root / "generated").exists())

    def test_target_selection_and_invalid_data(self):
        self.targets["rose"] = {"output": "generated/rose.md", "parts": ["missing.md"]}
        self.assertEqual(self.run_composer("--target", "prime"), 0)
        self.assertFalse((self.root / "generated/rose.md").exists())
        self.assertEqual(self.run_composer("--target", "unknown"), 1)
        for targets in [{"": {"output": "out.md", "parts": ["a.md"]}},
                        {"prime": {"output": "out.md", "parts": []}}]:
            self.targets = targets
            self.assertEqual(self.run_composer(), 1)
        (self.root / "composition.json").write_text('{"version": true, "targets": {}}')
        with self.assertRaises(ValueError):
            composer.render(self.root)


if __name__ == "__main__":
    unittest.main()
