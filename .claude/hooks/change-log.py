#!/usr/bin/env python3
"""
PostToolUse hook: runs after Write, Edit, or Bash.
Appends an audit entry to .claude/changes.log.
Exit 0 always — this is observe-only, never blocks.
"""
import json
import sys
import os
from datetime import datetime

data = json.load(sys.stdin)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Build a short description of what happened
if tool_name in ("Write", "Edit"):
    target = tool_input.get("file_path", "unknown")
    entry = f"{tool_name:<6} {target}"
elif tool_name == "Bash":
    cmd = tool_input.get("command", "")[:80]  # truncate long commands
    entry = f"Bash   {cmd}"
else:
    sys.exit(0)

log_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "changes.log"
)

with open(log_path, "a") as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {entry}\n")
