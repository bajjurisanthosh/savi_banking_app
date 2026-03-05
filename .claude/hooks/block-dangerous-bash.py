#!/usr/bin/env python3
"""
PreToolUse hook: runs before every Bash call.
Blocks commands that could cause irreversible damage to the project.
Exit 2 = block the command and show the reason to Claude.
"""
import json
import sys
import re

data = json.load(sys.stdin)

if data.get("tool_name") != "Bash":
    sys.exit(0)

command = data.get("tool_input", {}).get("command", "")

DANGEROUS_PATTERNS = [
    (r"rm\s+-rf?\s+/",            "rm -rf on root/system paths"),
    (r"rm\s+-rf?\s+\.",           "rm -rf on current directory"),
    (r"git\s+push\s+.*--force",   "force push (use --force-with-lease instead)"),
    (r"git\s+reset\s+--hard",     "git reset --hard (irreversible)"),
    (r"git\s+clean\s+-f",         "git clean -f (deletes untracked files)"),
    (r"git\s+checkout\s+\.",       "git checkout . (discards all changes)"),
    (r"git\s+branch\s+-D",        "git branch -D (force deletes branch)"),
    (r"drop\s+table",             "SQL DROP TABLE"),
    (r"truncate\s+table",         "SQL TRUNCATE TABLE"),
    (r">\s*/dev/null\s+2>&1.*rm",  "silenced rm command"),
]

for pattern, reason in DANGEROUS_PATTERNS:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"[safety] Blocked: {reason}")
        print(f"Command: {command[:120]}")
        print("Ask the user to confirm before running this.")
        sys.exit(2)
