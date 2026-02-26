#!/usr/bin/env python3
"""
Complete Task - Move a single file from Needs_Action to Done
"""

import os
import sys
import shutil

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    needs_action_path = os.path.join(script_dir, 'Needs_Action')
    done_path = os.path.join(script_dir, 'Done')

    # List files in Needs_Action
    files = [f for f in os.listdir(needs_action_path) if f.endswith('.md')]

    if not files:
        print("✅ No tasks in Needs_Action folder")
        return 0

    print(f"\n📋 Tasks in Needs_Action ({len(files)}):\n")
    for i, filename in enumerate(files, 1):
        print(f"  {i}. {filename}")

    # If filename provided as argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename not in files:
            print(f"\n❌ File not found: {filename}")
            return 1
    else:
        # Complete all
        print(f"\n✅ Completing all {len(files)} tasks...\n")
        for filename in files:
            src = os.path.join(needs_action_path, filename)
            dst = os.path.join(done_path, filename)
            shutil.move(src, dst)
            print(f"  ✓ {filename} → Done")
        print(f"\n✅ All tasks completed!")
        return 0

    # Complete specific file
    src = os.path.join(needs_action_path, filename)
    dst = os.path.join(done_path, filename)
    shutil.move(src, dst)
    print(f"\n✅ Completed: {filename}")

    return 0

if __name__ == '__main__':
    exit(main())
