import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rose_journal import capture, entries, ledger, notebook  # noqa: E402
from rose_journal.config import Config  # noqa: E402
from test_engine import add_prompt, make_cfg  # noqa: E402


class PerEntryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = make_cfg(Path(self.tmp.name))
        self.base = datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc)

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_ritual_and_each_j_is_its_own_flat_file(self):
        add_prompt(self.cfg, "morning", sent=self.base, message_id="1")
        add_prompt(self.cfg, "evening", sent=self.base + timedelta(hours=17), message_id="2")
        capture.capture(self.cfg, self.cfg.chat_id, "1", "morning words", self.base + timedelta(hours=1))
        capture.capture_note(self.cfg, "first thought", self.base + timedelta(hours=8))
        capture.capture_note(self.cfg, "second thought", self.base + timedelta(hours=9))
        capture.capture(self.cfg, self.cfg.chat_id, "2", "evening words", self.base + timedelta(hours=18))
        names = sorted(p.name for p in self.cfg.root.glob("*.md"))
        self.assertEqual(names, ["2026-10-14-evening.md", "2026-10-14-j-2.md", "2026-10-14-j.md",
                                 "2026-10-14-morning.md"])
        self.assertEqual(entries.raw_entry((self.cfg.root / "2026-10-14-j-2.md").read_text()).splitlines()[-1],
                         "second thought")
        self.assertIn("kind: evening", (self.cfg.root / "2026-10-14-evening.md").read_text())

    def test_rose_note_never_touches_his_words_or_annotations(self):
        add_prompt(self.cfg, sent=self.base)
        info = capture.capture(self.cfg, self.cfg.chat_id, "100", "my words", self.base + timedelta(hours=1))
        path = Path(info["path"])
        capture.add_rose_note(self.cfg, "Links to an August entry (inference).", self.base + timedelta(hours=2),
                              "2026-10-14", "morning")
        entries.write_annotations(path, "- annotated")
        capture.capture(self.cfg, self.cfg.chat_id, "100", "more words", self.base + timedelta(hours=3))
        body = path.read_text()
        self.assertIn("my words", entries.raw_entry(body))
        self.assertLess(body.index("more words"), body.index("## Rose's annotations"))
        self.assertLess(body.index("## Rose's annotations"), body.index("## Rose's notes"))
        self.assertIn("- annotated", body)

    def test_rose_note_on_empty_day_starts_a_note_entry(self):
        p = capture.add_rose_note(self.cfg, "Worth keeping.", self.base)
        self.assertTrue(p.endswith("2026-10-14-note.md"))
        body = Path(p).read_text()
        self.assertIn("## Rose's notes", body)
        self.assertNotIn("## Burooj", body)

    def test_voice_audio_embedded(self):
        add_prompt(self.cfg, sent=self.base)
        with ledger.locked(self.cfg.ledger_path) as data:
            prompt = ledger.find(data, "2026-10-14-morning")
            info = capture.record(self.cfg, prompt, "direct-reply", "slept okay", self.base + timedelta(hours=1),
                                  "voice", "9", "2026-10-14-morning-063000.ogg")
        body = Path(info["path"]).read_text()
        self.assertIn("· voice transcript\n\n![[2026-10-14-morning-063000.ogg]]\n\nslept okay", body)


class NotebookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = make_cfg(Path(self.tmp.name))
        self.cfg.state_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_render_resolve_archive(self):
        now = datetime(2026, 10, 14, 9, 0, tzinfo=timezone.utc)
        a = notebook.add(self.cfg, "Ask how the Amir talk went", "2026-10-13-evening", now=now)
        notebook.add(self.cfg, "Check in on the return-route decision", bring_up_after="2026-10-14", now=now)
        block = notebook.render(self.cfg, "2026-10-14")
        self.assertIn("Ask how the Amir talk went", block)
        self.assertLess(block.index("return-route"), block.index("Amir"))  # due item first
        notebook.resolve(self.cfg, a["id"], "came up; went well", now=now)
        self.assertEqual(len(notebook.open_items(self.cfg)), 1)
        arch = (self.cfg.state_dir / "notebook-archive.jsonl").read_text()
        self.assertIn("went well", arch)
        self.assertNotIn("prompts", json.loads((self.cfg.state_dir / "notebook.json").read_text()))

    def test_stale_items_archived_not_deleted(self):
        old = datetime(2026, 9, 1, tzinfo=timezone.utc)
        notebook.add(self.cfg, "old thread", now=old)
        n = notebook.sweep(self.cfg, datetime(2026, 10, 14, tzinfo=timezone.utc))
        self.assertEqual(n, 1)
        self.assertEqual(notebook.open_items(self.cfg), [])
        self.assertIn('"status": "stale"', (self.cfg.state_dir / "notebook-archive.jsonl").read_text())

    def test_followups_split_from_annotations(self):
        text, follow = notebook.split_followups("- He felt tired.\n- FOLLOW-UP: ask what 'lazy' meant\nFOLLOW-UP: sleep?")
        self.assertEqual(text, "- He felt tired.")
        self.assertEqual(follow, ["ask what 'lazy' meant", "sleep?"])


if __name__ == "__main__":
    unittest.main()
