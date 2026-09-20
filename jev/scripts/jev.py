#!/usr/bin/env python3
"""Host credentials for upstream jevon; arguments and output remain upstream's."""

import json
import os
from pathlib import Path
import sys

VERSION = "0.8.0"
OPENROUTER_BASE = "https://openrouter.ai/api"
OPENROUTER_MODEL = "typesafe/jev-1.13"


def cli_environment(arguments, inherited, credential_path):
    environment = dict(inherited)
    # Never let provider debug logging expose workflow state or credentials.
    environment["TYPESAFE_LOG_LEVEL"] = "off"
    inspection = {"-h", "--help", "-V", "--version", "--schema", "--llms", "--llms-full"}
    invocation = bool(arguments) and (
        arguments[0] in {"ask", "classify", "eval", "doctor", "models"}
        or "--mcp" in arguments
    )
    if not invocation or inspection.intersection(arguments):
        return environment
    if environment.get("TYPESAFE_API_KEY", "").strip():
        return environment

    # An explicit endpoint/model belongs to its caller. Do not borrow a host
    # credential for an unrelated endpoint or a direct TypeSafe model.
    base = environment.get("TYPESAFE_BASE_URL", "").strip()
    model = environment.get("TYPESAFE_DEFAULT_MODEL", "").strip()
    if base and base.rstrip("/") != OPENROUTER_BASE:
        return environment
    if model and not model.startswith("typesafe/"):
        return environment

    key = environment.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        try:
            config = json.loads(credential_path.read_text())
            candidate = config["providers"]["openrouter"]["apiKey"]
            if isinstance(candidate, str):
                key = candidate.strip()
        except (OSError, UnicodeError, ValueError, KeyError, TypeError):
            pass  # Upstream reports the missing credential through its contract.
    if key:
        environment["TYPESAFE_API_KEY"] = key
        environment["TYPESAFE_BASE_URL"] = OPENROUTER_BASE
        environment["TYPESAFE_DEFAULT_MODEL"] = model or OPENROUTER_MODEL
    return environment


def main():
    arguments = sys.argv[1:]
    binary = Path.home() / ".local" / "share" / "jevon" / VERSION / "bin" / "jev"
    if not binary.is_file():
        print(f"jev: upstream jevon {VERSION} is missing at {binary}", file=sys.stderr)
        return 127
    environment = cli_environment(
        arguments, os.environ, Path.home() / ".opencodex" / "config.json"
    )
    os.execve(binary, [str(binary), *arguments], environment)


if __name__ == "__main__":
    sys.exit(main())
