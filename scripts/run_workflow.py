#!/usr/bin/env python3
"""
Automated Workflow Runner
Simulates the complete workflow: Inbox -> Needs_Action -> Done
"""

import os
import sys
import time
import shutil
import re
from datetime import datetime
from collections import defaultdict

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def get_file_metadata(filepath):
    """Extract type and priority from markdown frontmatter."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            type_match = re.search(r'type:\s*(\w+)', content)
            priority_match = re.search(r'priority:\s*(\w+)', content)

            file_type = type_match.group(1) if type_match else 'unknown'
            priority = priority_match.group(1) if priority_match else 'medium'

            return file_type, priority
    except:
        pass
    return 'unknown', 'medium'

def process_inbox(inbox_path, needs_action_path, done_path, stats):
    """Move files from Inbox to Needs_Action or Done based on priority."""
    files = [f for f in os.listdir(inbox_path) if f.endswith('.md')]

    if not files:
        print("  📭 Inbox is empty")
        return 0

    processed = 0
    for filename in files:
        filepath = os.path.join(inbox_path, filename)
        file_type, priority = get_file_metadata(filepath)

        # High/medium priority -> Needs_Action, low priority -> Done
        if priority in ['high', 'medium']:
            dest = os.path.join(needs_action_path, filename)
            shutil.move(filepath, dest)
            print(f"  ➡️  {filename} → Needs_Action (priority: {priority})")
            stats['to_needs_action'] += 1
            stats['by_type'][file_type] += 1
            stats['by_priority'][priority] += 1
        else:
            dest = os.path.join(done_path, filename)
            shutil.move(filepath, dest)
            print(f"  ✅ {filename} → Done (priority: {priority})")
            stats['to_done_direct'] += 1
            stats['by_type'][file_type] += 1
            stats['by_priority'][priority] += 1

        processed += 1

    return processed

def process_needs_action(needs_action_path, done_path, stats):
    """Move files from Needs_Action to Done."""
    files = [f for f in os.listdir(needs_action_path) if f.endswith('.md')]

    if not files:
        print("  📋 Needs_Action is empty")
        return 0

    processed = 0
    for filename in files:
        filepath = os.path.join(needs_action_path, filename)
        dest = os.path.join(done_path, filename)
        shutil.move(filepath, dest)
        print(f"  ✅ {filename} → Done")
        processed += 1
        stats['completed_tasks'] += 1

    return processed

def show_status(inbox_path, needs_action_path, done_path):
    """Display current status of all folders."""
    inbox_count = len([f for f in os.listdir(inbox_path) if f.endswith('.md')])
    needs_count = len([f for f in os.listdir(needs_action_path) if f.endswith('.md')])
    done_count = len([f for f in os.listdir(done_path) if f.endswith('.md')])

    print(f"\n📊 Status: Inbox({inbox_count}) | Needs_Action({needs_count}) | Done({done_count})")

def print_summary_table(stats, start_time, end_time):
    """Print comprehensive summary table."""
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("📊 WORKFLOW SUMMARY - COMPLETE STATISTICS")
    print("=" * 80)

    # Workflow Overview
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ WORKFLOW OVERVIEW                                                           │")
    print("├─────────────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Files Processed:        {stats['files_created']:>3} files                                   │")
    print(f"│ Execution Time:               {duration:.1f} seconds                                │")
    print(f"│ Cycles Completed:             {stats['cycles']:>3} cycles                                 │")
    print("└─────────────────────────────────────────────────────────────────────────────┘")

    # File Flow Table
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ FILE FLOW BREAKDOWN                                                         │")
    print("├──────────────────────────────────────┬──────────────────────────────────────┤")
    print(f"│ Files Created in Inbox               │ {stats['files_created']:>3} files                         │")
    print(f"│ Files Moved to Needs_Action          │ {stats['to_needs_action']:>3} files                         │")
    print(f"│ Files Moved Directly to Done         │ {stats['to_done_direct']:>3} files                         │")
    print(f"│ Tasks Completed (Needs_Action→Done)  │ {stats['completed_tasks']:>3} files                         │")
    print(f"│ Total Files in Done                  │ {stats['to_done_direct'] + stats['completed_tasks']:>3} files                         │")
    print("└──────────────────────────────────────┴──────────────────────────────────────┘")

    # By Type Table
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ BREAKDOWN BY FILE TYPE                                                      │")
    print("├──────────────────────────────────────┬──────────────────────────────────────┤")
    for file_type, count in sorted(stats['by_type'].items()):
        percentage = (count / stats['files_created'] * 100) if stats['files_created'] > 0 else 0
        print(f"│ {file_type.capitalize():<36} │ {count:>3} files ({percentage:>5.1f}%)              │")
    print("└──────────────────────────────────────┴──────────────────────────────────────┘")

    # By Priority Table
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ BREAKDOWN BY PRIORITY                                                       │")
    print("├──────────────────────────────────────┬──────────────────────────────────────┤")
    for priority, count in sorted(stats['by_priority'].items()):
        percentage = (count / stats['files_created'] * 100) if stats['files_created'] > 0 else 0
        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
        print(f"│ {emoji} {priority.capitalize():<33} │ {count:>3} files ({percentage:>5.1f}%)              │")
    print("└──────────────────────────────────────┴──────────────────────────────────────┘")

    # Workflow Diagram
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ WORKFLOW DIAGRAM                                                            │")
    print("├─────────────────────────────────────────────────────────────────────────────┤")
    print("│                                                                             │")
    print(f"│         📥 INBOX ({stats['files_created']} created)                                            │")
    print("│              │                                                              │")
    print("│              ├─── High/Medium Priority ──→ 📋 NEEDS_ACTION                  │")
    print(f"│              │                              ({stats['to_needs_action']} files)                      │")
    print("│              │                                    │                         │")
    print("│              │                                    ↓                         │")
    print(f"│              │                              ✅ DONE ({stats['completed_tasks']} completed)           │")
    print("│              │                                                              │")
    print(f"│              └─── Low Priority ──────────→ ✅ DONE ({stats['to_done_direct']} direct)              │")
    print("│                                                                             │")
    print(f"│         TOTAL IN DONE: {stats['to_done_direct'] + stats['completed_tasks']} files                                              │")
    print("└─────────────────────────────────────────────────────────────────────────────┘")

    print("\n✅ All tasks completed successfully!")
    print("=" * 80 + "\n")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inbox_path = os.path.join(script_dir, 'Inbox')
    needs_action_path = os.path.join(script_dir, 'Needs_Action')
    done_path = os.path.join(script_dir, 'Done')

    # Verify folders exist
    for path in [inbox_path, needs_action_path, done_path]:
        if not os.path.exists(path):
            print(f"ERROR: Folder not found: {path}")
            return 1

    # Initialize statistics
    stats = {
        'files_created': 0,
        'to_needs_action': 0,
        'to_done_direct': 0,
        'completed_tasks': 0,
        'cycles': 0,
        'by_type': defaultdict(int),
        'by_priority': defaultdict(int)
    }

    start_time = time.time()

    print("=" * 70)
    print("🔄 AUTOMATED WORKFLOW RUNNER")
    print("=" * 70)
    print("\nThis will run 5 cycles:")
    print("  Cycle 1-3: Create files → Process Inbox → Process Needs_Action")
    print("  Cycle 4-5: Process remaining files\n")

    cycles = 5

    for cycle in range(1, cycles + 1):
        print(f"\n{'='*70}")
        print(f"🔄 CYCLE {cycle}/{cycles}")
        print(f"{'='*70}")

        # Create new files in first 3 cycles
        if cycle <= 3:
            print(f"\n📥 Creating new files in Inbox...")
            os.system(f'python "{os.path.join(script_dir, "simulate_watcher.py")}" --count 2 --type mixed')
            stats['files_created'] += 2

        time.sleep(1)

        # Process Inbox
        print(f"\n📋 Processing Inbox...")
        process_inbox(inbox_path, needs_action_path, done_path, stats)

        time.sleep(1)

        # Process Needs_Action
        print(f"\n✅ Processing Needs_Action...")
        process_needs_action(needs_action_path, done_path, stats)

        # Show status
        show_status(inbox_path, needs_action_path, done_path)

        stats['cycles'] += 1

        if cycle < cycles:
            print(f"\n⏳ Waiting 2 seconds before next cycle...")
            time.sleep(2)

    end_time = time.time()

    # Print comprehensive summary table
    print_summary_table(stats, start_time, end_time)

    return 0

if __name__ == '__main__':
    exit(main())
