#!/usr/bin/env python3
"""
Ralph Wiggum Manager - Gold Tier Autonomous Loop
Orchestrates the complete 8-agent workflow continuously.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(cmd: str, description: str) -> tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {description}...")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1, str(e)

def count_items(folder: Path) -> int:
    """Count markdown files or folders in a directory."""
    if not folder.exists():
        return 0

    if folder.name == 'Pending_Approval' or folder.name == 'Approved':
        # Count folders
        return len([f for f in folder.iterdir() if f.is_dir()])
    else:
        # Count .md files
        return len(list(folder.glob('*.md')))

def check_pm2_health(vault_path: Path) -> bool:
    """Check if all PM2 processes are online."""
    try:
        result = subprocess.run(
            'pm2 jlist',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return False

        import json
        processes = json.loads(result.stdout)

        # Check if all processes are online
        all_online = all(p['pm2_env']['status'] == 'online' for p in processes)

        if not all_online:
            print("  [WARN] Some PM2 processes are not online")
            # Restart failed processes
            subprocess.run('pm2 restart all', shell=True, capture_output=True)

        return all_online

    except Exception as e:
        print(f"  [ERROR] PM2 health check failed: {e}")
        return False

def autonomous_loop(vault_path: Path, max_iterations: int = 0):
    """Run the autonomous workflow loop."""

    print("="*60)
    print("GOLD TIER AUTONOMOUS BUSINESS LOOP")
    print("Ralph Wiggum Manager - 'I'm helping!'")
    print("="*60)
    print(f"Vault: {vault_path.absolute()}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    iteration = 0

    try:
        while True:
            iteration += 1

            if max_iterations > 0 and iteration > max_iterations:
                print()
                print(f"[INFO] Reached max iterations ({max_iterations})")
                break

            print("="*60)
            print(f"CYCLE #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            print()

            # Step 0: Check PM2 Sentinel Health
            print("[STEP 0] Checking PM2 Sentinel Health...")
            if not check_pm2_health(vault_path):
                print("  [WARN] PM2 health check issues detected")
            else:
                print("  [OK] All 6 sentinels online")
            print()

            # Count items in each folder
            inbox_count = count_items(vault_path / 'Inbox')
            needs_action_count = count_items(vault_path / 'Needs_Action')
            pending_approval_count = count_items(vault_path / 'Pending_Approval')
            approved_count = count_items(vault_path / 'Approved')

            print(f"Current State:")
            print(f"  Inbox: {inbox_count} items")
            print(f"  Needs_Action: {needs_action_count} items")
            print(f"  Pending_Approval: {pending_approval_count} items")
            print(f"  Approved: {approved_count} items")
            print()

            # Step 1: Triage Inbox
            if inbox_count > 0:
                print("[STEP 1] Triaging Inbox...")
                code, output = run_command(
                    f'python scripts/triage_inbox.py "{vault_path}"',
                    "Running triage"
                )
                if code == 0:
                    print("  [OK] Triage complete")
                else:
                    print("  [ERROR] Triage failed")
                print()
            else:
                print("[STEP 1] Inbox empty - skipping triage")
                print()

            # Step 2: Strategic Planning
            needs_action_count = count_items(vault_path / 'Needs_Action')
            if needs_action_count > 0:
                print("[STEP 2] Creating Strategic Plans...")
                code, output = run_command(
                    f'python scripts/strategic_planner.py "{vault_path}"',
                    "Running strategic planner"
                )
                if code == 0:
                    print("  [OK] Plans created")
                else:
                    print("  [ERROR] Planning failed")
                print()
            else:
                print("[STEP 2] Needs_Action empty - skipping planning")
                print()

            # Step 3: Display Pending Approvals
            pending_approval_count = count_items(vault_path / 'Pending_Approval')
            if pending_approval_count > 0:
                print("[STEP 3] Pending Approvals Status...")
                print(f"  [INFO] {pending_approval_count} item(s) awaiting approval")
                print("  [INFO] Items will remain here until manually approved")
                print()
            else:
                print("[STEP 3] No items pending approval")
                print()

            # Step 4: Execute Approved Items
            approved_count = count_items(vault_path / 'Approved')
            if approved_count > 0:
                print("[STEP 4] Executing Approved Items...")
                print(f"  [INFO] {approved_count} item(s) ready for execution")
                print("  [INFO] Executor skill would process these items")
                # In production: run_command('python scripts/executor.py', "Executing approved items")
                print()
            else:
                print("[STEP 4] No approved items to execute")
                print()

            # Step 5: Update Dashboard
            print("[STEP 5] Updating Dashboard...")
            code, output = run_command(
                f'python scripts/update_dashboard.py "{vault_path}"',
                "Updating dashboard"
            )
            if code == 0:
                print("  [OK] Dashboard updated")
            else:
                print("  [ERROR] Dashboard update failed")
            print()

            # Check completion criteria
            inbox_count = count_items(vault_path / 'Inbox')
            needs_action_count = count_items(vault_path / 'Needs_Action')
            approved_count = count_items(vault_path / 'Approved')

            if inbox_count == 0 and needs_action_count == 0 and approved_count == 0:
                if pending_approval_count == 0:
                    print("="*60)
                    print("TASK_COMPLETE")
                    print("="*60)
                    print("All queues are empty. Loop complete.")
                    print()
                    break
                else:
                    print(f"[INFO] {pending_approval_count} item(s) awaiting approval")
                    print("[INFO] Loop will continue monitoring...")

            # Wait before next cycle
            wait_time = 60  # 1 minute between cycles
            print(f"[INFO] Next cycle in {wait_time} seconds...")
            print()
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print()
        print("="*60)
        print("Loop stopped by user")
        print("="*60)
        print(f"Completed {iteration} cycle(s)")
        print()
        sys.exit(0)
    except Exception as e:
        print()
        print(f"[ERROR] Loop error: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    vault_path = Path.cwd()

    # Get max iterations from environment or command line
    max_iterations = int(os.environ.get('MAX_ITERATIONS', 0))
    if len(sys.argv) > 1:
        max_iterations = int(sys.argv[1])

    autonomous_loop(vault_path, max_iterations)

if __name__ == '__main__':
    main()
