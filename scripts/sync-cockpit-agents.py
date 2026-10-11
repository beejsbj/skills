#!/usr/bin/env python3
"""Retire only this checkout's t3-code links and expose cockpit-agents."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only check (default).')
    mode.add_argument('--apply', action='store_true', help='Apply after CLI deployment confirmation.')
    parser.add_argument('--root', action='append', type=Path, help='Skill root; repeatable.')
    parser.add_argument('--backup', type=Path, help='New JSON file recording links before apply.')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    target = repo / 'cockpit-agents'
    if not (target / 'SKILL.md').is_file():
        parser.error(f'missing skill: {target}')
    roots = args.root or [Path.home() / p / 'skills' for p in ('.claude', '.agents', '.codex')]
    roots = list(dict.fromkeys(p.expanduser().resolve() for p in roots))
    changes = []
    for root in roots:
        if root.exists() and not root.is_dir():
            parser.error(f'not a directory: {root}')
        for name in ('cockpit-agents', 't3-code'):
            path = root / name
            expected = repo / name
            old = None
            if path.is_symlink():
                old = os.readlink(path)
                if path.resolve() != expected.resolve():
                    parser.error(f'foreign link, left untouched: {path}')
            elif path.exists():
                parser.error(f'non-symlink collision, left untouched: {path}')
            desired = str(target) if name == 'cockpit-agents' else None
            if (old is None) == (desired is None):
                continue
            changes.append({'path': str(path), 'before': old, 'after': desired})
    try:
        result = subprocess.run(['cockpit', 'agents', '--help'], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as error:
        parser.error(f'cannot verify deployed cockpit agents: {type(error).__name__}')
    required = ('projects', 'models', 'threads', 'show', 'create', 'send', 'sessions', 'resume', 'receipt')
    missing = [name for name in required if name not in result.stdout.replace(',', ' ').replace('{', ' ').replace('}', ' ').split()]
    if result.returncode or missing:
        parser.error('CLI cutover is not ready; missing commands: ' + ', '.join(missing))
    if not changes:
        print('All selected roots expose cockpit-agents; legacy skill links are absent.')
        return 0
    for change in changes:
        print(('link ' if change['after'] else 'unlink ') + change['path'])
    if not args.apply:
        print('Pending changes; re-run with --apply --backup FILE after deployment confirmation.')
        return 1
    if not args.backup:
        parser.error('--apply requires --backup FILE (a new file)')
    # Preflight every root before mutation; refuse changed state on the apply pass.
    with args.backup.expanduser().open('x', encoding='utf-8') as stream:
        json.dump({'repo': str(repo), 'changes': changes}, stream, indent=2)
        stream.write('\n')
    for change in changes:
        path = Path(change['path'])
        if change['before'] is None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(change['after'])
        else:
            if not path.is_symlink() or os.readlink(path) != change['before']:
                raise RuntimeError(f'link changed during cutover: {path}; inspect backup')
            path.unlink()
    print(f'Applied. Prior link targets: {args.backup}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
