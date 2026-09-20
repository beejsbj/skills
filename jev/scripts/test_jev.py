import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("jev.py")
SPEC = importlib.util.spec_from_file_location("jev_launcher", SCRIPT)
jev = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(jev)


class CredentialBoundaryTests(unittest.TestCase):
    def credential_file(self, contents):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        with handle:
            json.dump(contents, handle)
        return Path(handle.name)

    def env(self, **values):
        inherited = {"PATH": "/usr/bin", **values}
        result = jev.cli_environment(["ask", "question"], inherited, self.store)
        return inherited, result

    def setUp(self):
        self.store = self.credential_file(
            {"providers": {"openrouter": {"apiKey": "store-key"}}}
        )

    def test_inspection_commands_do_not_read_credential_file(self):
        with mock.patch.object(Path, "read_text", side_effect=AssertionError("read")):
            for arguments in (["--help"], ["ask", "--help"], ["classify", "--schema"]):
                result = jev.cli_environment(arguments, {}, self.store)
                self.assertEqual(result, {"TYPESAFE_LOG_LEVEL": "off"})

    def test_explicit_typesafe_key_wins_and_does_not_read_store(self):
        with mock.patch.object(Path, "read_text", side_effect=AssertionError("read")):
            inherited, result = self.env(TYPESAFE_API_KEY="direct-key")
        self.assertEqual(result["TYPESAFE_API_KEY"], "direct-key")
        self.assertEqual(result["TYPESAFE_LOG_LEVEL"], "off")
        self.assertEqual(inherited, {"PATH": "/usr/bin", "TYPESAFE_API_KEY": "direct-key"})

    def test_environment_openrouter_key_wins_over_store(self):
        with mock.patch.object(Path, "read_text", side_effect=AssertionError("read")):
            _, result = self.env(OPENROUTER_API_KEY="environment-key")
        self.assertEqual(result["TYPESAFE_API_KEY"], "environment-key")

    def test_store_key_selects_openrouter_compatibility_route(self):
        _, result = self.env()
        self.assertEqual(result["TYPESAFE_API_KEY"], "store-key")
        self.assertEqual(result["TYPESAFE_BASE_URL"], "https://openrouter.ai/api")
        self.assertEqual(result["TYPESAFE_DEFAULT_MODEL"], "typesafe/jev-1.13")

    def test_missing_or_malformed_store_is_safe(self):
        cases = [self.store.parent / "does-not-exist.json"]
        for contents in ("{broken", "[]", '{"providers": {}}'):
            path = self.credential_file({})
            path.write_text(contents, encoding="utf-8")
            cases.append(path)
        for path in cases:
            result = jev.cli_environment(["ask", "question"], {}, path)
            self.assertNotIn("TYPESAFE_API_KEY", result)

    def test_unrelated_endpoint_does_not_borrow_openrouter_key(self):
        result = jev.cli_environment(
            ["ask", "question"],
            {"TYPESAFE_BASE_URL": "https://api.typesafe.ai", "OPENROUTER_API_KEY": "router"},
            self.store,
        )
        self.assertNotIn("TYPESAFE_API_KEY", result)

    def test_direct_model_does_not_borrow_openrouter_key(self):
        result = jev.cli_environment(
            ["ask", "question"],
            {"TYPESAFE_DEFAULT_MODEL": "jev-latest", "OPENROUTER_API_KEY": "router"},
            self.store,
        )
        self.assertNotIn("TYPESAFE_API_KEY", result)

    def test_inherited_environment_is_not_mutated(self):
        inherited = {"OPENROUTER_API_KEY": "router", "PATH": "/bin"}
        original = inherited.copy()
        jev.cli_environment(["ask", "question"], inherited, self.store)
        self.assertEqual(inherited, original)

    def test_command_is_forwarded_with_key_only_in_environment(self):
        arguments = ["ask", "-", "--noul", "Does this request a refund?"]
        with mock.patch.object(jev.sys, "argv", ["jev", *arguments]), \
             mock.patch.dict(jev.os.environ, {"OPENROUTER_API_KEY": "test-secret"}, clear=True), \
             mock.patch.object(Path, "is_file", return_value=True), \
             mock.patch.object(jev.os, "execve") as execute:
            jev.main()
        binary, argv, environment = execute.call_args.args
        self.assertEqual(argv, [str(binary), *arguments])
        self.assertNotIn("test-secret", " ".join(argv))
        self.assertEqual(environment["TYPESAFE_API_KEY"], "test-secret")

    def test_logging_is_forced_off(self):
        result = jev.cli_environment([], {"TYPESAFE_LOG_LEVEL": "debug"}, self.store)
        self.assertEqual(result["TYPESAFE_LOG_LEVEL"], "off")


if __name__ == "__main__":
    unittest.main()
