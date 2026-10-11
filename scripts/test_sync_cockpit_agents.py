"""Linker checks use disposable skill roots and a CLI-help stub, never live installs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class CutoverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        (self.repo / 'scripts').mkdir(parents=True)
        self.script = self.repo / 'scripts/sync-cockpit-agents.py'
        shutil.copyfile(Path(__file__).with_name('sync-cockpit-agents.py'), self.script)
        (self.repo / 'cockpit-agents').mkdir()
        (self.repo / 'cockpit-agents/SKILL.md').write_text('fixture')
        (self.repo / 't3-code/scripts').mkdir(parents=True)
        self.helper = self.repo / 't3-code/scripts/t3ctl.mjs'
        self.helper.write_text('unchanged compatibility helper')
        self.roots = [self.base / name for name in ('codex', 'claude', 'agents')]
        for root in self.roots:
            root.mkdir()
            (root / 't3-code').symlink_to(self.repo / 't3-code')
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        self.cli = self.bin / 'cockpit'
        self.cli.write_text('#!/bin/sh\necho "{projects,models,threads,show,create,send,sessions,resume,receipt}"\n')
        self.cli.chmod(0o755)
        self.backup = self.base / 'before.json'

    def run_linker(self, *args):
        roots = [flag for root in self.roots for flag in ('--root', str(root))]
        return subprocess.run([sys.executable, str(self.script), *roots, *args],
                              capture_output=True, text=True,
                              env={**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH']})

    def assert_untouched(self):
        for root in self.roots:
            self.assertFalse((root / 'cockpit-agents').exists())
            self.assertTrue((root / 't3-code').is_symlink())
        self.assertFalse(self.backup.exists())

    def test_preview_apply_backup_and_idempotent_check(self):
        self.assertEqual(self.run_linker('--check').returncode, 1)
        self.assert_untouched()
        applied = self.run_linker('--apply', '--backup', str(self.backup))
        self.assertEqual(applied.returncode, 0, applied.stderr)
        for root in self.roots:
            self.assertEqual((root / 'cockpit-agents').resolve(), self.repo / 'cockpit-agents')
            self.assertFalse((root / 't3-code').is_symlink())
        self.assertEqual(len(json.loads(self.backup.read_text())['changes']), 6)
        self.assertEqual(self.helper.read_text(), 'unchanged compatibility helper')
        self.assertEqual(self.run_linker('--check').returncode, 0)

    def test_install_with_no_legacy_links(self):
        for root in self.roots:
            (root / 't3-code').unlink()
        applied = self.run_linker('--apply', '--backup', str(self.backup))
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(len(json.loads(self.backup.read_text())['changes']), 3)
        self.assertEqual(self.run_linker('--check').returncode, 0)

    def test_foreign_link_in_last_root_prevents_all_writes(self):
        link = self.roots[-1] / 't3-code'
        link.unlink()
        link.symlink_to(self.base / 'foreign')
        result = self.run_linker('--apply', '--backup', str(self.backup))
        self.assertEqual(result.returncode, 2)
        self.assert_untouched()
        self.assertEqual(os.readlink(link), str(self.base / 'foreign'))

    def test_ordinary_directory_collision_prevents_all_writes(self):
        (self.roots[-1] / 'cockpit-agents').mkdir()
        result = self.run_linker('--apply', '--backup', str(self.backup))
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.roots[0] / 'cockpit-agents').exists())
        self.assertTrue((self.roots[0] / 't3-code').is_symlink())
        self.assertFalse(self.backup.exists())

    def test_missing_cli_parity_prevents_all_writes(self):
        self.cli.write_text('#!/bin/sh\necho "{sessions,send,options,receipt}"\n')
        self.assertEqual(self.run_linker('--apply', '--backup', str(self.backup)).returncode, 2)
        self.assert_untouched()

    def test_apply_requires_new_backup(self):
        self.assertEqual(self.run_linker('--apply').returncode, 2)
        self.assert_untouched()
        self.backup.write_text('preserve')
        self.assertNotEqual(self.run_linker('--apply', '--backup', str(self.backup)).returncode, 0)
        self.assertEqual(self.backup.read_text(), 'preserve')
        for root in self.roots:
            self.assertFalse((root / 'cockpit-agents').exists())
            self.assertTrue((root / 't3-code').is_symlink())


if __name__ == '__main__':
    unittest.main()
