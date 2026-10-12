# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PostToolUse hook: when the Bash command that just ran contains a
`git commit`, leave Claude a message that asks for the changelog skill.

Same script as exercise 4. APM installs skills unprefixed (.claude/skills/
changelog), so the message names the bare skill. APM rewrites the path in
the hook command per harness at install time; this script does not need to
know where it landed."""

import json
import re
import sys

data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")

parts = re.split(r"&&|\|\||;", command)
if any(part.strip().startswith("git commit") for part in parts):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "A git commit was just made. Invoke the "
                "changelog skill (/changelog) now, in this same turn. "
                "Do not ask the user for permission first."
            )
        }
    }))
