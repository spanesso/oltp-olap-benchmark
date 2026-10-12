#!/usr/bin/env python3
"""PostToolUse hook for Bash: after a pytest run, remind the agent of the SDD loop.

Plain stdout from a hook is not shown to the model, so the reminder is returned
as `additionalContext` in the hook's JSON output.
"""

import json
import re
import sys

PYTEST = re.compile(r"(^|[\s;&|])(pytest|make\s+test)\b")


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0

    if PYTEST.search(command):
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "Tests ejecutados. Si pasaron, verifica la implementación "
                        "contra el spec con /speckit-analyze antes de commitear."
                    ),
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
