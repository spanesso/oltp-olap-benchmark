#!/usr/bin/env python3
"""PreToolUse hook for Bash: blocks bulk `git add` and lints before `git commit`.

Claude Code passes the tool call as JSON on stdin. Exit code 2 blocks the call
and feeds stderr back to the agent; exit code 0 lets it through.
"""

import json
import os
import re
import subprocess
import sys

BULK_ADD = re.compile(r"\bgit\s+add\s+(.*\s)?(\.|-A|--all)(\s|$|;|&)")
COMMIT = re.compile(r"\bgit\s+commit\b")
LINT_DIRS = ("src", "tests")


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0

    if BULK_ADD.search(command):
        print(
            "Bloqueado: no uses `git add .` / `git add -A`. "
            "Agrega archivos explícitamente para mantener commits atómicos.",
            file=sys.stderr,
        )
        return 2

    if COMMIT.search(command):
        root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        targets = [d for d in LINT_DIRS if os.path.isdir(os.path.join(root, d))]
        if not targets:
            return 0
        for args in (
            ["ruff", "check", *targets],
            ["ruff", "format", "--check", *targets],
        ):
            result = subprocess.run(args, cwd=root, capture_output=True, text=True)
            if result.returncode != 0:
                print(
                    f"Commit bloqueado: `{' '.join(args)}` falló.\n"
                    f"{result.stdout}{result.stderr}",
                    file=sys.stderr,
                )
                return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
