#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

v = Path.cwd()

print("\n=== WORKFLOW START ===\n")

# Step 1: Inbox to Needs_Action
print("[1] Inbox -> Needs_Action")
for f in (v / "Inbox").glob("*.md"):
    dest = v / "Needs_Action" / f.name
    f.rename(dest)
    print(f"    OK {f.name}")

# Step 2: Run Strategic Planner
print("\n[2] Creating Plans...")
subprocess.call([sys.executable, ".claude/skills/strategic-planner/scripts/strategic_planner.py"])

# Step 3: Auto-approve
print("\n[3] Pending_Approval -> Approved")
for p in (v / "Pending_Approval").glob("*/"):
    dest = v / "Approved" / p.name
    p.rename(dest)
    print(f"    OK {p.name}")

# Step 4: Execute
print("\n[4] Executing Approved Items...")
subprocess.call([sys.executable, ".claude/skills/executor/scripts/executor.py"])

print("\n=== WORKFLOW COMPLETE ===\n")
