import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rose_journal import capture, compose, entries, guard, ledger, schedule, validate  # noqa: E402
from rose_journal.config import Config, load  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")


def make_cfg(tmp: Path) -> Config:
    return Config(root=tmp / "Journal", state_dir=tmp / "state")


def add_prompt(cfg, kind="morning", local_date="2026-10-14", sent=None, message_id="100"):
    sent = sent or datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc)
    p = {"id": ledger.prompt_id(kind, local_date), "kind": kind, "local_date": local_date,
         "chat_id": cfg.chat_id, "message_id": message_id, "sent_at": sent.isoformat(),
         "opener": "Morning 🌹", "opener_source": "rose", "plain_text": "Morning journal\n\n1. How did you sleep?"}
    with ledger.locked(cfg.ledger_path) as data:
        data["prompts"].append(p)
    return p


class ConfigTest(unittest.TestCase):
    def test_load_defaults_and_overrides(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "journal.json"
            p.write_text(json.dumps({"version": 1, "root": t, "timezone": "America/Toronto",
                                     "schedule": {"morning": {"time": "07:30"}}}))
            cfg = load(p)
            self.assertEqual(cfg.schedule["morning"]["time"], "07:30")
            self.assertEqual(cfg.schedule["evening"]["time"], "23:00")
            self.assertEqual(str(cfg.tz), "America/Toronto")


class ScheduleTest(unittest.TestCase):
    def setUp(self):
        self.cfg = Config(root=Path("/tmp/x"))

    def test_morning_due_in_local_time_once(self):
        now = datetime(2026, 10, 14, 6, 3, tzinfo=IST)
        self.assertEqual([k for k, _ in schedule.due(self.cfg, now, set())], ["morning"])
        self.assertEqual(schedule.due(self.cfg, now, {"2026-10-14-morning"}), [])

    def test_outside_grace_not_due(self):
        self.assertEqual(schedule.due(self.cfg, datetime(2026, 10, 14, 8, 30, tzinfo=IST), set()), [])

    def test_weekly_only_on_sunday(self):
        sun = datetime(2026, 10, 18, 20, 5, tzinfo=IST)
        mon = datetime(2026, 10, 19, 20, 5, tzinfo=IST)
        self.assertIn("weekly", [k for k, _ in schedule.due(self.cfg, sun, set())])
        self.assertNotIn("weekly", [k for k, _ in schedule.due(self.cfg, mon, set())])


class ComposeTest(unittest.TestCase):
    def test_bank_folded_and_escaped(self):
        html = compose.telegram_html("morning", datetime(2026, 10, 14, 6, 0, tzinfo=IST), "Tea & <toast>?")
        self.assertIn("<blockquote expandable>1. How did you sleep?", html)
        self.assertIn("Tea &amp; &lt;toast&gt;?", html)
        self.assertIn("11. What would make today deeply satisfying?", html)

    def test_folded_state_has_no_opener(self):
        html = compose.telegram_html("evening", datetime(2026, 10, 14, 23, 0, tzinfo=IST), None, "missed — reply anytime")
        self.assertIn("missed — reply anytime", html)
        self.assertIn("<blockquote expandable>", html)


class ValidateTest(unittest.TestCase):
    pack = "### journal:2026-08-25-morning\nI want to call Amir bhaiya about the shop"

    def test_plain_opener_ok(self):
        self.assertTrue(validate.check("morning", {"opener": "Morning 🌹 What's alive today?", "citations": []}, self.pack)[0])

    def test_uncited_claim_rejected(self):
        ok, why = validate.check("morning", {"opener": "Bus run today. Yesterday you mentioned feeling scattered.",
                                             "citations": []}, self.pack)
        self.assertFalse(ok)
        self.assertEqual(why, "claim without citation")

    def test_fabricated_quote_rejected(self):
        d = {"opener": "You mentioned the shop.", "citations": [{"source": "journal:2026-08-25-morning",
                                                                    "quote": "I hate being good"}]}
        self.assertFalse(validate.check("morning", d, self.pack)[0])

    def test_real_quote_accepted(self):
        d = {"opener": "In August you wrote about calling Amir bhaiya — did that happen?",
             "citations": [{"source": "journal:2026-08-25-morning", "quote": "call Amir bhaiya about the shop"}]}
        self.assertTrue(validate.check("morning", d, self.pack)[0])

    def test_parse_tolerates_wrapping(self):
        self.assertEqual(validate.parse('```json\n{"opener": "hi", "citations": []}\n```')["opener"], "hi")


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = make_cfg(Path(self.tmp.name))
        self.sent = datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc)
        add_prompt(self.cfg, sent=self.sent)

    def tearDown(self):
        self.tmp.cleanup()

    def test_next_message_inside_window_captured_once(self):
        now = self.sent + timedelta(hours=2)
        info = capture.capture(self.cfg, self.cfg.chat_id, None, "Slept badly.\nStill in Kashmir.", now)
        self.assertEqual(info["rule"], "next-message")
        body = Path(info["path"]).read_text()
        self.assertIn("Slept badly.\nStill in Kashmir.", body)
        self.assertIn("status: captured", body)
        self.assertTrue(info["path"].endswith("2026/10/2026-10-14-morning.md"))
        self.assertIsNone(capture.capture(self.cfg, self.cfg.chat_id, None, "ok thanks", now + timedelta(minutes=2)))

    def test_after_window_only_direct_reply(self):
        late = self.sent + timedelta(hours=14)
        self.assertIsNone(capture.capture(self.cfg, self.cfg.chat_id, None, "random chat", late))
        info = capture.capture(self.cfg, self.cfg.chat_id, "100", "late answer", late)
        self.assertEqual(info["rule"], "direct-reply")

    def test_direct_replies_append(self):
        capture.capture(self.cfg, self.cfg.chat_id, "100", "first", self.sent + timedelta(hours=1))
        info = capture.capture(self.cfg, self.cfg.chat_id, "100", "second", self.sent + timedelta(hours=20))
        body = Path(info["path"]).read_text()
        self.assertLess(body.index("first"), body.index("second"))
        self.assertLess(body.index("second"), body.index("## Rose's Annotations"))

    def test_other_chat_and_commands_ignored(self):
        now = self.sent + timedelta(hours=1)
        self.assertIsNone(capture.capture(self.cfg, "999", None, "hi", now))
        self.assertIsNone(capture.capture(self.cfg, self.cfg.chat_id, None, "/new", now))

    def test_most_recent_visible_prompt_wins(self):
        add_prompt(self.cfg, kind="evening", local_date="2026-10-14",
                   sent=self.sent + timedelta(hours=3), message_id="200")
        info = capture.capture(self.cfg, self.cfg.chat_id, None, "evening thoughts", self.sent + timedelta(hours=4))
        self.assertEqual(info["prompt"]["kind"], "evening")

    def test_annotations_written_without_touching_raw(self):
        info = capture.capture(self.cfg, self.cfg.chat_id, None, "raw words", self.sent + timedelta(hours=1))
        path = Path(info["path"])
        self.assertTrue(entries.annotations_pending(path.read_text()))
        entries.write_annotations(path, "- Pattern: sleep")
        body = path.read_text()
        self.assertIn("raw words", entries.raw_entry(body))
        self.assertIn("status: complete", body)
        self.assertFalse(entries.annotations_pending(body))


class GuardTest(unittest.TestCase):
    def blocked(self, tool, args):
        return guard.check(tool, args) is not None

    def test_blocks_hermes_settings(self):
        self.assertTrue(self.blocked("terminal", {"command": "hermes config set model.default x"}))
        self.assertTrue(self.blocked("terminal", {"command": "cd /tmp && hermes -p rose cron edit abc --prompt x"}))
        self.assertTrue(self.blocked("patch", {"path": "/home/admin/.hermes/config.yaml"}))
        self.assertTrue(self.blocked("write_file", {"path": "/home/admin/.hermes/profiles/rose/config.yaml"}))
        self.assertTrue(self.blocked("write_file", {"path": "/mnt/server-ssd/BJsWorkspace/Brain/Journal/2026/10/x.md"}))
        self.assertTrue(self.blocked("terminal", {"command": "sed -i s/a/b/ ~/.hermes/config.yaml"}))
        self.assertTrue(self.blocked("terminal", {"command": "systemctl --user restart hermes-gateway"}))
        self.assertTrue(self.blocked("skill_manage", {"action": "edit", "name": "morning-journal"}))
        self.assertTrue(self.blocked("cronjob_manage", {"action": "create"}))
        self.assertTrue(self.blocked("execute_code", {"code": "print(1)"}))

    def test_allows_reading_and_otto(self):
        self.assertFalse(self.blocked("terminal", {"command": "hermes -p otto chat --oneshot --query-file /tmp/q -Q"}))
        self.assertFalse(self.blocked("terminal", {"command": "hermes -p rose cron list"}))
        self.assertFalse(self.blocked("terminal", {"command": "cat ~/.hermes/profiles/rose/config.yaml 2>/dev/null"}))
        self.assertFalse(self.blocked("terminal", {"command": "chat-scrobbler search 'dharma' --json"}))
        self.assertFalse(self.blocked("write_file", {"path": "/mnt/server-ssd/BJsWorkspace/Brain/Notes/idea.md"}))
        self.assertFalse(self.blocked("write_file", {"path": "/home/admin/.hermes/profiles/rose/cache/scratch/h.txt"}))
        self.assertFalse(self.blocked("read_file", {"path": "/home/admin/.hermes/config.yaml"}))
        self.assertFalse(self.blocked("skill_manage", {"action": "view", "name": "journal-system"}))


class PluginTranscriptTest(unittest.TestCase):
    def test_strips_note_reply_prefix_and_quotes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "rj_plugin", Path(__file__).resolve().parents[1] / "plugin" / "__init__.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        note = "[Journal reply — saved …]\n\n"
        msg = '[Replying to: "Morning"]\n\n"I slept okay, the cousins were loud."\n\n' + note
        self.assertEqual(mod._transcript(msg, {"note": note, "caption": ""}), "I slept okay, the cousins were loud.")


if __name__ == "__main__":
    unittest.main()


class TickSendTest(unittest.TestCase):
    def test_failed_sends_retry_then_alert(self):
        from rose_journal import telegram, tick
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            orig_send, orig_opener = telegram.send_html, tick._opener

            def boom(*a, **k):
                raise telegram.TelegramError("Bad Gateway")
            telegram.send_html = boom
            tick._opener = lambda *a: ("Morning 🌹", "plain:test", [])
            try:
                now = datetime(2026, 10, 14, 6, 5, tzinfo=IST)
                for attempt in (1, 2):
                    log = []
                    tick.send_due(cfg, now, log)
                    self.assertIn(f"attempt {attempt}/3", log[-1])
                with self.assertRaises(tick.SendFailed):
                    tick.send_due(cfg, now, [])
                log = []
                tick.send_due(cfg, now, log)  # exhausted: no more attempts
                self.assertEqual(log, [])
            finally:
                telegram.send_html, tick._opener = orig_send, orig_opener

    def test_successful_send_recorded_once(self):
        from rose_journal import telegram, tick
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            orig_send, orig_opener = telegram.send_html, tick._opener
            sent = []
            telegram.send_html = lambda chat, html: sent.append(html) or "555"
            tick._opener = lambda *a: ("Morning 🌹", "rose", [])
            try:
                now = datetime(2026, 10, 14, 6, 5, tzinfo=IST)
                tick.send_due(cfg, now, [])
                tick.send_due(cfg, now + timedelta(minutes=5), [])
                self.assertEqual(len(sent), 1)
                p = ledger.find(ledger.snapshot(cfg.ledger_path), "2026-10-14-morning")
                self.assertEqual(p["message_id"], "555")
            finally:
                telegram.send_html, tick._opener = orig_send, orig_opener
