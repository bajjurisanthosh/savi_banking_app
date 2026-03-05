#!/usr/bin/env python3
"""
PreToolUse hook: runs before Read.
Blocks Claude from reading .env files to prevent secrets leaking into context.
Exit 2 = block the tool call and show the message to Claude.
"""
import json
import sys

data = json.load(sys.stdin)

tool_name = data.get("tool_name", "")
file_path = data.get("tool_input", {}).get("file_path", "")

if tool_name != "Read":
    sys.exit(0)

# Block reads of .env files (but allow .env.example)
if file_path.endswith(".env") and not file_path.endswith(".env.example"):
    print(f"[security] Blocked read of {file_path} — .env files contain secrets.")
    print("Use os.environ.get() in code instead of reading .env directly.")
    sys.exit(2)
