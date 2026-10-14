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
        ev = compose.telegram_html("evening", datetime(2026, 10, 14, 23, 0, tzinfo=IST), "x")
        self.assertIn("<b>1. Brain Dump &amp; Letting Go</b>\n- What's spinning in your mind?", ev)
        self.assertIn("Tea &amp; &lt;toast&gt;?", html)
        self.assertIn("11. What would make today deeply satisfying?", html)

    def test_folded_state_has_no_opener(self):
        html = compose.telegram_html("evening", datetime(2026, 10, 14, 23, 0, tzinfo=IST), None, "missed — reply anytime")
        self.assertIn("missed — reply anytime", html)
        self.assertNotIn("<blockquote", html)  # folded = header only


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
        self.assertIn("## Morning journal", body)
        self.assertTrue(info["path"].endswith("2026/10/2026-10-14.md"))
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
        self.assertLess(body.index("second"), body.index("### Rose's annotations"))

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
        self.assertTrue(entries.annotations_pending(path.read_text(), "morning"))
        entries.write_annotations(path, "morning", "- Pattern: sleep")
        body = path.read_text()
        self.assertIn("raw words", entries.raw_entry(body, "morning"))
        self.assertIn("- Pattern: sleep", body)
        self.assertFalse(entries.annotations_pending(body, "morning"))


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
            tick._opener = lambda *a: ("Morning 🌹", "plain:test", [], [])
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
            tick._opener = lambda *a: ("Morning 🌹", "rose", [], [{"id": "1", "question": "How did you sleep?", "as": "Sleep okay?"}])
            try:
                now = datetime(2026, 10, 14, 6, 5, tzinfo=IST)
                tick.send_due(cfg, now, [])
                tick.send_due(cfg, now + timedelta(minutes=5), [])
                self.assertEqual(len(sent), 1)
                p = ledger.find(ledger.snapshot(cfg.ledger_path), "2026-10-14-morning")
                self.assertEqual(p["message_id"], "555")
            finally:
                telegram.send_html, tick._opener = orig_send, orig_opener


class NotesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = make_cfg(Path(self.tmp.name))
        self.now = datetime(2026, 10, 14, 9, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.tmp.cleanup()

    def test_strip_command(self):
        self.assertEqual(capture.strip_command("/j aimless again"), "aimless again")
        self.assertEqual(capture.strip_command("/journal\nline two"), "line two")
        self.assertEqual(capture.strip_command("/j@RoseBot hi"), "hi")
        self.assertIsNone(capture.strip_command("/jump"))
        self.assertIsNone(capture.strip_command("just text"))

    def test_j_notes_append_to_the_days_note(self):
        a = capture.capture_note(self.cfg, "first thought", self.now)
        b = capture.capture_note(self.cfg, "second thought", self.now + timedelta(hours=1))
        self.assertEqual(a["path"], b["path"])
        self.assertTrue(a["path"].endswith("2026-10-14.md"))
        body = Path(a["path"]).read_text()
        self.assertLess(body.index("first thought"), body.index("second thought"))
        self.assertIn("## Notes (/j)", body)

    def test_rose_note_never_touches_raw_or_annotations(self):
        add_prompt(self.cfg, sent=datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc))
        info = capture.capture(self.cfg, self.cfg.chat_id, "100", "my words", self.now)
        path = Path(info["path"])
        capture.add_rose_note(self.cfg, "A connection to the August entry (inference).", self.now, "2026-10-14", "morning")
        entries.write_annotations(path, "morning", "- annotated")
        body = path.read_text()
        self.assertIn("my words", entries.raw_entry(body, "morning"))
        self.assertIn("- annotated", body)
        self.assertIn("### Rose's notes", body)
        self.assertIn("A connection to the August entry", body)
        self.assertLess(body.index("### Rose's annotations"), body.index("### Rose's notes"))
        # a later direct reply still lands in the raw entry, above the notes
        capture.capture(self.cfg, self.cfg.chat_id, "100", "more words", self.now + timedelta(hours=3))
        body = path.read_text()
        self.assertLess(body.index("more words"), body.index("### Rose's annotations"))
        self.assertIn("- annotated", body)

    def test_rose_note_on_empty_day_then_his_reply(self):
        p = capture.add_rose_note(self.cfg, "Worth keeping.", self.now)
        self.assertTrue(p.endswith("2026-10-14.md"))
        info = capture.capture_note(self.cfg, "my own words", self.now + timedelta(hours=1))
        body = Path(info["path"]).read_text()
        self.assertIn("my own words", entries.raw_entry(body, "note"))
        self.assertNotIn(entries.NO_WORDS, body)
        self.assertLess(body.index("### Burooj"), body.index("### Rose's notes"))
        self.assertTrue(entries.annotations_pending(body, "note"))

    def test_bad_note_inputs(self):
        with self.assertRaises(ValueError):
            capture.add_rose_note(self.cfg, "  ", self.now)
        with self.assertRaises(ValueError):
            capture.add_rose_note(self.cfg, "x", self.now, "2026-13-40")


class VerifierTest(unittest.TestCase):
    def test_quotes_beyond_pack_verified_against_journal(self):
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            f = cfg.root / "2026" / "07" / "2026-07-22-morning.md"
            f.parent.mkdir(parents=True)
            f.write_text("## Raw Entry\n\nI want more chapters. Have arcs.\n")
            from rose_journal import context
            verify = context.make_verifier(cfg)
            d = {"opener": "In July you wrote about wanting arcs.",
                 "citations": [{"source": "journal:2026-07-22-morning", "quote": "I want more  chapters."}]}
            self.assertTrue(validate.check("morning", d, "pack without it", verify)[0])
            d["citations"][0]["quote"] = "I want fewer chapters."
            self.assertFalse(validate.check("morning", d, "pack without it", verify)[0])


class PluginDispatchTest(unittest.TestCase):
    """Drive the gateway hooks with fake Telegram events against a temp journal."""

    def setUp(self):
        import importlib.util
        from types import SimpleNamespace
        self.NS = SimpleNamespace
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        conf = t / "journal.json"
        conf.write_text(json.dumps({"root": str(t / "Journal"), "state_dir": str(t / "state"),
                                    "telegram_chat_id": "579876880"}))
        from rose_journal import config as jconfig
        self._orig = jconfig.CONFIG_PATH
        jconfig.CONFIG_PATH = conf
        spec = importlib.util.spec_from_file_location(
            "rj_plugin2", Path(__file__).resolve().parents[1] / "plugin" / "__init__.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.cfg = jconfig.load()

    def tearDown(self):
        from rose_journal import config as jconfig
        jconfig.CONFIG_PATH = self._orig
        self.tmp.cleanup()

    def event(self, text, kind="TEXT", reply_to=None, chat="579876880"):
        return self.NS(text=text, message_type=self.NS(name=kind), message_id="9", reply_to_message_id=reply_to,
                       source=self.NS(platform=self.NS(value="telegram"), chat_id=chat, user_id=chat))

    def test_j_text_saved_and_rewritten(self):
        out = self.mod.on_dispatch(event=self.event("/j can't sleep, thinking about Rishikesh"))
        self.assertEqual(out["action"], "rewrite")
        self.assertTrue(out["text"].startswith("[Journal note"))
        self.assertFalse(out["text"].split("]\n\n", 1)[1].startswith("/"))
        notes = list(self.cfg.root.rglob("2026-*.md"))
        self.assertEqual(len(notes), 1)
        self.assertIn("can't sleep, thinking about Rishikesh", notes[0].read_text())

    def test_plain_chat_untouched(self):
        self.assertIsNone(self.mod.on_dispatch(event=self.event("hey rose")))
        self.assertIsNone(self.mod.on_dispatch(event=self.event("/j hi", chat="123")))

    def test_direct_reply_to_prompt_saved(self):
        add_prompt(self.cfg, sent=datetime.now(timezone.utc) - timedelta(hours=30), message_id="77")
        out = self.mod.on_dispatch(event=self.event("late answer", reply_to="77"))
        self.assertTrue(out["text"].startswith("[Journal reply"))
        self.assertIn("late answer", next(self.cfg.root.rglob("2026-10-14.md")).read_text())

    def test_voice_j_saved_after_transcription(self):
        out = self.mod.on_dispatch(event=self.event("/j", kind="VOICE"))
        note = out["text"]
        self.mod.on_llm_call(user_message='"walked by the lake, felt light"\n\n' + note, platform="telegram")
        body = next(self.cfg.root.rglob("20*.md")).read_text()
        self.assertIn("walked by the lake, felt light", body)
        self.assertIn("voice transcript", body)

    def test_add_note_tool(self):
        res = json.loads(self.mod.journal_add_note({"note": "Pattern worth keeping (inference)."}))
        self.assertTrue(res["success"])
        self.assertIn("### Rose's notes", Path(res["path"]).read_text())


class DailyFileTest(unittest.TestCase):
    def test_rituals_share_one_day_file_in_order(self):
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            base = datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc)
            add_prompt(cfg, "morning", sent=base, message_id="1")
            add_prompt(cfg, "evening", sent=base + timedelta(hours=17), message_id="2")
            capture.capture(cfg, cfg.chat_id, "1", "morning words", base + timedelta(hours=1))
            capture.capture_note(cfg, "a /j thought", base + timedelta(hours=8))
            capture.capture(cfg, cfg.chat_id, "2", "evening words", base + timedelta(hours=18))
            files = list(cfg.root.rglob("*.md"))
            self.assertEqual(len(files), 1)
            body = files[0].read_text()
            self.assertEqual(entries.kinds_in(body), ["morning", "note", "evening"])
            self.assertIn("kinds: [morning, note, evening]", body)
            self.assertEqual(entries.raw_entry(body, "evening").splitlines()[-1], "evening words")
            self.assertIn("> [!question]- Questions", body)


class LocationTest(unittest.TestCase):
    def test_set_location_updates_config_and_history(self):
        from rose_journal import location
        with tempfile.TemporaryDirectory() as t:
            conf = Path(t) / "journal.json"
            conf.write_text(json.dumps({"root": t, "state_dir": str(Path(t) / "state"),
                                        "timezone": "Asia/Kolkata", "location": "Srinagar"}))
            orig = location.geocode
            location.geocode = lambda q: {"name": "Toronto", "admin1": "Ontario", "country": "Canada",
                                          "latitude": 43.7, "longitude": -79.4, "timezone": "America/Toronto"}
            try:
                r = location.set_location("Toronto", path=conf)
            finally:
                location.geocode = orig
            d = json.loads(conf.read_text())
            self.assertEqual(d["timezone"], "America/Toronto")
            self.assertEqual(d["coordinates"]["lat"], 43.7)
            self.assertEqual(r["previous"]["timezone"], "Asia/Kolkata")
            self.assertTrue((Path(t) / "state" / "location-history.jsonl").exists())


class FoldRetryTest(unittest.TestCase):
    def test_failed_fold_retries_then_gives_up(self):
        from rose_journal import telegram, tick
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            sent = datetime.now(timezone.utc) - timedelta(hours=7)
            add_prompt(cfg, sent=sent, message_id="5")
            orig = telegram.edit_html
            telegram.edit_html = lambda *a: (_ for _ in ()).throw(telegram.TelegramError("timeout"))
            try:
                for _ in range(tick.FOLD_ATTEMPTS - 1):
                    tick.fold(cfg, datetime.now(timezone.utc), [])
                    p = ledger.find(ledger.snapshot(cfg.ledger_path), "2026-10-14-morning")
                    self.assertIsNone(p.get("collapsed_at"))
                tick.fold(cfg, datetime.now(timezone.utc), [])
                p = ledger.find(ledger.snapshot(cfg.ledger_path), "2026-10-14-morning")
                self.assertIsNotNone(p.get("collapsed_at"))
            finally:
                telegram.edit_html = orig


class WovenQuestionsTest(unittest.TestCase):
    def test_ids_and_asked_filtering(self):
        from rose_journal.questions import bank_items
        self.assertEqual(bank_items("evening")["9.2"], "What simple joys touched you today?")
        self.assertEqual(bank_items("morning")["11"], "What would make today deeply satisfying?")
        d = {"opener": "x", "asked": [{"id": "9.2", "as": "What was cozy today?"}, {"id": "99", "as": "bogus"}]}
        got = validate.asked("evening", d)
        self.assertEqual([a["id"] for a in got], ["9.2"])
        self.assertEqual(got[0]["as"], "What was cozy today?")

    def test_longer_woven_opener_allowed_but_not_a_pasted_list(self):
        woven = "Evening, Burooj. " + "What was cozy about the rain? " * 20
        self.assertTrue(validate.check("evening", {"opener": woven, "citations": []}, "")[0])
        pasted = "\n".join(f"{i}. q" for i in range(1, 8))
        self.assertFalse(validate.check("evening", {"opener": pasted, "citations": []}, "")[0])

    def test_manual_resend_keeps_old_message_replyable(self):
        from rose_journal import telegram, tick
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            ids = iter(["500", "501"])
            edits = []
            orig_send, orig_edit, orig_opener = telegram.send_html, telegram.edit_html, tick._opener
            telegram.send_html = lambda chat, html: next(ids)
            telegram.edit_html = lambda chat, mid, html: edits.append(mid)
            tick._opener = lambda *a: ("Morning 🌹", "rose", [], [])
            try:
                now = datetime(2026, 10, 14, 9, 0, tzinfo=IST)
                tick.send_due(cfg, now, [], only="morning")
                tick.send_due(cfg, now + timedelta(minutes=10), [], only="morning")
                data = ledger.snapshot(cfg.ledger_path)
                p = ledger.find(data, "2026-10-14-morning")
                self.assertEqual(p["message_id"], "501")
                self.assertEqual(edits, ["500"])  # old one marked "sent again below"
                self.assertIs(ledger.by_message_id(data, cfg.chat_id, "500"), p)
            finally:
                telegram.send_html, telegram.edit_html, tick._opener = orig_send, orig_edit, orig_opener

    def test_entry_records_woven_questions(self):
        with tempfile.TemporaryDirectory() as t:
            cfg = make_cfg(Path(t))
            p = add_prompt(cfg, sent=datetime(2026, 10, 14, 0, 30, tzinfo=timezone.utc))
            with ledger.locked(cfg.ledger_path) as data:
                q = ledger.find(data, p["id"])
                q["sent_at_local"] = "06:00 IST"
                q["asked"] = [{"id": "1", "question": "How did you sleep?", "as": "Sleep okay?"}]
            info = capture.capture(cfg, cfg.chat_id, "100", "fine", datetime(2026, 10, 14, 1, 0, tzinfo=timezone.utc))
            self.assertIn("_Woven in: [1] How did you sleep?_", Path(info["path"]).read_text())


class PluginCommandTest(unittest.TestCase):
    def test_commands_registered_and_spawn_engine(self):
        import importlib.util, subprocess
        spec = importlib.util.spec_from_file_location(
            "rj_plugin3", Path(__file__).resolve().parents[1] / "plugin" / "__init__.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        names, hooks, tools = [], [], []

        class Ctx:
            def register_command(self, name, handler, description=""):
                names.append(name)
            def register_hook(self, name, cb):
                hooks.append(name)
            def register_tool(self, name, **kw):
                tools.append(name)
        mod.register(Ctx())
        self.assertEqual(names, ["j", "morning", "evening", "midweek", "weekly", "morning-journal", "evening-journal"])
        self.assertIn("journal_set_location", tools)
        calls = []
        orig = subprocess.Popen
        subprocess.Popen = lambda args, **kw: calls.append(args)
        try:
            with tempfile.TemporaryDirectory() as t:
                from rose_journal import config as jconfig
                conf = Path(t) / "j.json"
                conf.write_text(json.dumps({"root": t, "state_dir": t}))
                o, jconfig.CONFIG_PATH = jconfig.CONFIG_PATH, conf
                try:
                    msg = mod._trigger("evening")("")
                finally:
                    jconfig.CONFIG_PATH = o
        finally:
            subprocess.Popen = orig
        self.assertIn("on its way", msg)
        self.assertEqual(calls[0][-3:], ["rose_journal.tick", "--send", "evening"])
