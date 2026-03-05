#!/usr/bin/env python3
"""
PostToolUse hook: runs after Write or Edit.
If the file is a .py file, compiles it to catch syntax errors immediately.
Exit 2 = show error to Claude so it fixes it right away.
"""
import json
import sys
import subprocess

data = json.load(sys.stdin)

tool_name = data.get("tool_name", "")
file_path = data.get("tool_input", {}).get("file_path", "")

# Only check Python files edited by Write or Edit
if tool_name not in ("Write", "Edit") or not file_path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    ["python3", "-m", "py_compile", file_path],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(f"[syntax-check] Syntax error in {file_path}:")
    print(result.stderr)
    sys.exit(2)  # Exit 2 = Claude sees this and fixes it
