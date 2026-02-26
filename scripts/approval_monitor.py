#!/usr/bin/env python3
"""
Approval Monitor Script
Displays pending items for CEO review and tracks approval status.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse frontmatter from markdown content."""
    frontmatter = {}

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()

            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter

def extract_plan_summary(plan_content: str) -> Dict[str, str]:
    """Extract key information from Plan.md."""
    summary = {
        'objective': 'Not specified',
        'tools': 'Not specified',
        'success_criteria': 'Not specified',
        'risk_level': 'UNKNOWN'
    }

    # Extract objective
    if '## 1. Objective' in plan_content:
        obj_section = plan_content.split('## 1. Objective')[1].split('##')[0]
        lines = [l.strip() for l in obj_section.split('\n') if l.strip() and not l.startswith('#')]
        if lines:
            summary['objective'] = lines[0][:200]

    # Extract tools
    if '## 2. Required MCP Tools' in plan_content:
        tools_section = plan_content.split('## 2. Required MCP Tools')[1].split('##')[0]
        tools = [l.strip('- *').strip() for l in tools_section.split('\n') if l.strip().startswith('-')]
        if tools:
            summary['tools'] = ', '.join(tools[:3])

    # Extract success criteria
    if '## 4. Success Criteria' in plan_content:
        success_section = plan_content.split('## 4. Success Criteria')[1].split('##')[0]
        criteria = [l.strip('- []').strip() for l in success_section.split('\n') if '[ ]' in l]
        if criteria:
            summary['success_criteria'] = '; '.join(criteria[:3])

    # Extract risk level
    if 'Risk Level: LOW' in plan_content or 'risk level: low' in plan_content.lower():
        summary['risk_level'] = 'LOW'
    elif 'Risk Level: MEDIUM' in plan_content or 'risk level: medium' in plan_content.lower():
        summary['risk_level'] = 'MEDIUM'
    elif 'Risk Level: HIGH' in plan_content or 'risk level: high' in plan_content.lower():
        summary['risk_level'] = 'HIGH'

    return summary

def display_pending_items(vault_path: Path):
    """Display all pending approval items."""
    pending_path = vault_path / 'Pending_Approval'

    if not pending_path.exists():
        print("[INFO] No Pending_Approval folder found")
        return

    folders = [f for f in pending_path.iterdir() if f.is_dir()]

    if not folders:
        print("[INFO] No items pending approval")
        return

    print("="*60)
    print("PENDING ITEMS")
    print("="*60)
    print()

    for idx, folder in enumerate(sorted(folders), 1):
        plan_file = folder / 'Plan.md'

        if not plan_file.exists():
            print(f"[{idx}] [WARNING] {folder.name}")
            print(f"     No Plan.md found")
            print()
            continue

        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_content = f.read()

            frontmatter = parse_frontmatter(plan_content)
            summary = extract_plan_summary(plan_content)

            priority = frontmatter.get('priority', 'medium').upper()
            created = frontmatter.get('created', 'Unknown')
            original_file = frontmatter.get('original_file', 'Unknown')

            # Priority indicator
            if priority == 'HIGH':
                indicator = '[HIGH PRIORITY]'
            elif priority == 'MEDIUM':
                indicator = '[MEDIUM PRIORITY]'
            else:
                indicator = '[LOW PRIORITY]'

            # Extract title from plan
            title_match = plan_content.split('\n')[0] if plan_content else folder.name
            if title_match.startswith('#'):
                title = title_match.strip('# ').strip()
            else:
                title = folder.name

            print(f"[{idx}] {indicator} - {title}")
            print(f"    Folder: {folder.name}")
            print(f"    Created: {created}")
            print(f"    Original: {original_file}")
            print()
            print(f"    Objective: {summary['objective']}")
            print(f"    MCP Tools: {summary['tools']}")
            print()
            print(f"    Success Criteria:")
            print(f"    {summary['success_criteria']}")
            print()
            print(f"    Risk Level: {summary['risk_level']}")
            print()
            print(f"    [APPROVE] Move to /Approved/{folder.name}/")
            print(f"    [MODIFY] Edit Plan.md and keep in /Pending_Approval/")
            print(f"    [REJECT] Move to /Rejected/ with reason")
            print()
            print("-"*60)
            print()

        except Exception as e:
            print(f"[{idx}] [ERROR] {folder.name}")
            print(f"     Could not read plan: {e}")
            print()

def display_approved_items(vault_path: Path):
    """Display approved items ready for execution."""
    approved_path = vault_path / 'Approved'

    if not approved_path.exists():
        return

    folders = [f for f in approved_path.iterdir() if f.is_dir()]

    if not folders:
        return

    print("="*60)
    print("APPROVED ITEMS (Ready for Execution)")
    print("="*60)
    print()

    for idx, folder in enumerate(sorted(folders), 1):
        print(f"[A{idx}] {folder.name}")
        print(f"     Status: [AWAITING EXECUTION]")
        print()

def main():
    """Main entry point."""
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("="*60)
    print("APPROVAL MONITOR - Items Awaiting Review")
    print("="*60)
    print(f"Vault: {vault_path.absolute()}")
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Count items
    pending_path = vault_path / 'Pending_Approval'
    approved_path = vault_path / 'Approved'

    pending_count = len([f for f in pending_path.iterdir() if f.is_dir()]) if pending_path.exists() else 0
    approved_count = len([f for f in approved_path.iterdir() if f.is_dir()]) if approved_path.exists() else 0

    print(f"PENDING APPROVAL: {pending_count} item(s)")
    print(f"APPROVED (Ready for Execution): {approved_count} item(s)")
    print()

    # Display pending items
    display_pending_items(vault_path)

    # Display approved items
    display_approved_items(vault_path)

    # Display instructions
    print("="*60)
    print("APPROVAL INSTRUCTIONS")
    print("="*60)
    print()
    print("To APPROVE an item:")
    print("  Move the entire folder to /Approved/")
    print()
    print("To MODIFY an item:")
    print("  Edit the Plan.md file in the folder")
    print("  Keep the folder in /Pending_Approval/")
    print()
    print("To REJECT an item:")
    print("  Create REJECTION_REASON.md in the folder")
    print("  Move the folder to /Rejected/")
    print()
    print("="*60)
    print("NEXT STEPS")
    print("="*60)
    print()
    print("1. Review each pending item above")
    print("2. Read full Plan.md for items requiring approval")
    print("3. Make approval decisions")
    print("4. Move approved items to /Approved/ folder")
    print("5. Operational Executor will process items in /Approved/")
    print()
    print("="*60)

if __name__ == '__main__':
    main()
