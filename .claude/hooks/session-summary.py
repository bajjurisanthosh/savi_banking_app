#!/usr/bin/env python3
"""
Stop hook: runs when the Claude Code session ends.
Reads changes.log and prints a summary of everything that happened.
Also appends the summary to session-history.log for long-term record.
"""
import json
import sys
import os
from datetime import datetime
from collections import Counter

data = json.load(sys.stdin)

hooks_dir  = os.path.dirname(os.path.abspath(__file__))
claude_dir = os.path.dirname(hooks_dir)
log_path   = os.path.join(claude_dir, "changes.log")

if not os.path.exists(log_path):
    print("[session] No changes recorded this session.")
    sys.exit(0)

with open(log_path) as f:
    lines = [l.strip() for l in f if l.strip()]

if not lines:
    print("[session] No changes recorded this session.")
    sys.exit(0)

# Count operations by type
ops = Counter()
files_touched = set()
for line in lines:
    parts = line.split(None, 2)
    if len(parts) >= 3:
        _, op, target = parts
        ops[op.strip()] += 1
        if not target.startswith("python") and not target.startswith("git"):
            files_touched.add(target.strip())

summary_lines = [
    f"\n{'='*55}",
    f"  Session summary — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    f"{'='*55}",
    f"  Total operations : {len(lines)}",
]
for op, count in ops.most_common():
    summary_lines.append(f"  {op:<8}: {count}")
if files_touched:
    summary_lines.append(f"\n  Files touched ({len(files_touched)}):")
    for f in sorted(files_touched):
        summary_lines.append(f"    {f}")
summary_lines.append(f"{'='*55}\n")

summary = "\n".join(summary_lines)
print(summary)

# Archive to session-history.log and reset changes.log
history_path = os.path.join(claude_dir, "session-history.log")
with open(history_path, "a") as f:
    f.write(summary)

# Clear the per-session log for the next session
open(log_path, "w").close()
