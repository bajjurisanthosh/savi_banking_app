#!/usr/bin/env python3
"""
PostToolUse hook: runs after Write or Edit.
Auto-formats Python files with black so code style is always consistent.
Exit 0 always — formatting is silent, never blocks Claude.
"""
import json
import sys
import subprocess

data = json.load(sys.stdin)

tool_name = data.get("tool_name", "")
file_path = data.get("tool_input", {}).get("file_path", "")

if tool_name not in ("Write", "Edit") or not file_path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    ["python3", "-m", "black", "--quiet", "--line-length", "100", file_path],
    capture_output=True,
    text=True,
)

# Always exit 0 — formatting is a silent background action
# If black fails (e.g. syntax error), syntax-check.py will catch it
sys.exit(0)
