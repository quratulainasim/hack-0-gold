#!/usr/bin/env python3
"""
Approval Monitor Script

Monitors /Pending_Approval folder and displays items awaiting CEO review.
Acts as gatekeeper between planning and execution.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def extract_plan_summary(plan_path: Path) -> Dict[str, str]:
    """
    Extract key information from Plan.md file.

    Args:
        plan_path: Path to Plan.md file

    Returns:
        Dictionary with extracted information
    """
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title
        title = "Unknown"
        for line in content.split('\n'):
            if line.startswith('# Strategic Plan:'):
                title = line.replace('# Strategic Plan:', '').strip()
                break
            elif line.startswith('#'):
                title = line.lstrip('#').strip()
                break

        # Extract priority
        priority = "medium"
        if '**Priority**:' in content:
            for line in content.split('\n'):
                if '**Priority**:' in line:
                    priority = line.split('**Priority**:')[1].strip().lower()
                    break

        # Extract objective
        objective = ""
        if '## 1. Objective' in content:
            parts = content.split('## 1. Objective')
            if len(parts) > 1:
                obj_section = parts[1].split('##')[0]
                # Get first meaningful line
                for line in obj_section.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('**'):
                        objective = line[:200]
                        break

        # Extract MCP tools
        tools = []
        if '## 2. Required MCP Tools' in content:
            parts = content.split('## 2. Required MCP Tools')
            if len(parts) > 1:
                tools_section = parts[1].split('##')[0]
                for line in tools_section.split('\n'):
                    if line.strip().startswith('- **'):
                        tool = line.split('**')[1]
                        tools.append(tool)

        # Extract success criteria count
        success_count = 0
        if '## 4. Success Criteria' in content:
            parts = content.split('## 4. Success Criteria')
            if len(parts) > 1:
                success_section = parts[1].split('##')[0]
                success_count = success_section.count('- [ ]')

        # Extract risk level
        risk_level = "unknown"
        if '## Risk Assessment' in content:
            parts = content.split('## Risk Assessment')
            if len(parts) > 1:
                risk_section = parts[1].split('##')[0]
                risk_count = risk_section.count('**')
                if risk_count <= 2:
                    risk_level = "low"
                elif risk_count <= 4:
                    risk_level = "medium"
                else:
                    risk_level = "high"

        # Extract created timestamp
        created = "Unknown"
        if '**Created**:' in content:
            for line in content.split('\n'):
                if '**Created**:' in line:
                    created = line.split('**Created**:')[1].strip()
                    break

        return {
            'title': title,
            'priority': priority,
            'objective': objective,
            'tools': tools,
            'success_count': success_count,
            'risk_level': risk_level,
            'created': created
        }

    except Exception as e:
        return {
            'title': 'Error reading plan',
            'priority': 'unknown',
            'objective': f'Error: {e}',
            'tools': [],
            'success_count': 0,
            'risk_level': 'unknown',
            'created': 'Unknown'
        }


def get_folder_age(folder_path: Path) -> str:
    """
    Calculate how long ago the folder was created.

    Args:
        folder_path: Path to folder

    Returns:
        Human-readable age string
    """
    try:
        created_time = folder_path.stat().st_ctime
        age_seconds = datetime.now().timestamp() - created_time
        age_hours = age_seconds / 3600

        if age_hours < 1:
            return f"{int(age_seconds / 60)} minutes ago"
        elif age_hours < 24:
            return f"{int(age_hours)} hours ago"
        else:
            return f"{int(age_hours / 24)} days ago"
    except:
        return "Unknown"


def format_pending_item(index: int, folder_path: Path, plan_summary: Dict[str, str]) -> str:
    """
    Format a pending item for display.

    Args:
        index: Item number
        folder_path: Path to item folder
        plan_summary: Extracted plan information

    Returns:
        Formatted string for display
    """
    priority = plan_summary['priority']

    # Priority indicator
    if priority == 'high':
        priority_icon = '🔴 HIGH PRIORITY'
    elif priority == 'low':
        priority_icon = '🟢 LOW PRIORITY'
    else:
        priority_icon = '🟡 MEDIUM PRIORITY'

    # Risk indicator
    risk = plan_summary['risk_level'].upper()

    # Format tools
    tools_str = ', '.join(plan_summary['tools']) if plan_summary['tools'] else 'Not specified'

    # Get folder age
    age = get_folder_age(folder_path)

    output = f"""
[{index}] {priority_icon} - {plan_summary['title']}
    Folder: {folder_path.name}
    Created: {plan_summary['created']} ({age})

    Objective: {plan_summary['objective']}
    MCP Tools: {tools_str}
    Success Criteria: {plan_summary['success_count']} items
    Risk Level: {risk}

    📄 Full Plan: {folder_path}/Plan.md

    ✅ APPROVE: mv Pending_Approval/{folder_path.name} Approved/
    ✏️  MODIFY: Edit {folder_path}/Plan.md
    ❌ REJECT: mv Pending_Approval/{folder_path.name} Rejected/
"""

    return output


def scan_pending_approval(vault_path: Path) -> List[Tuple[Path, Dict[str, str]]]:
    """
    Scan Pending_Approval folder for items.

    Args:
        vault_path: Path to vault directory

    Returns:
        List of tuples (folder_path, plan_summary)
    """
    pending_path = vault_path / 'Pending_Approval'

    if not pending_path.exists():
        return []

    items = []

    # Find all folders in Pending_Approval
    for folder_path in pending_path.iterdir():
        if folder_path.is_dir():
            plan_path = folder_path / 'Plan.md'

            if plan_path.exists():
                plan_summary = extract_plan_summary(plan_path)
                items.append((folder_path, plan_summary))
            else:
                # Folder without Plan.md
                items.append((folder_path, {
                    'title': folder_path.name,
                    'priority': 'unknown',
                    'objective': 'Missing Plan.md file',
                    'tools': [],
                    'success_count': 0,
                    'risk_level': 'unknown',
                    'created': 'Unknown'
                }))

    # Sort by priority (high first) then by creation time
    priority_order = {'high': 0, 'medium': 1, 'low': 2, 'unknown': 3}
    items.sort(key=lambda x: (priority_order.get(x[1]['priority'], 3), x[0].stat().st_ctime))

    return items


def scan_approved(vault_path: Path) -> List[Path]:
    """
    Scan Approved folder for items ready for execution.

    Args:
        vault_path: Path to vault directory

    Returns:
        List of folder paths in Approved
    """
    approved_path = vault_path / 'Approved'

    if not approved_path.exists():
        return []

    items = []

    for folder_path in approved_path.iterdir():
        if folder_path.is_dir():
            items.append(folder_path)

    # Sort by creation time (oldest first)
    items.sort(key=lambda x: x.stat().st_ctime)

    return items


def display_approval_monitor(vault_path: Path):
    """
    Display approval monitor dashboard.

    Args:
        vault_path: Path to vault directory
    """
    print(f"\n{'='*60}")
    print(f"APPROVAL MONITOR - Items Awaiting Review")
    print(f"{'='*60}")
    print(f"Vault: {vault_path.absolute()}")
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Scan folders
    pending_items = scan_pending_approval(vault_path)
    approved_items = scan_approved(vault_path)

    print(f"PENDING APPROVAL: {len(pending_items)} items")
    print(f"APPROVED (Ready for Execution): {len(approved_items)} items")

    # Display pending items
    if pending_items:
        print(f"\n{'='*60}")
        print(f"PENDING ITEMS")
        print(f"{'='*60}")

        for index, (folder_path, plan_summary) in enumerate(pending_items, 1):
            print(format_pending_item(index, folder_path, plan_summary))
            print(f"{'-'*60}")

    else:
        print(f"\n{'='*60}")
        print(f"✅ No items pending approval")
        print(f"{'='*60}\n")

    # Display approved items
    if approved_items:
        print(f"\n{'='*60}")
        print(f"APPROVED ITEMS (Ready for Execution)")
        print(f"{'='*60}\n")

        for index, folder_path in enumerate(approved_items, 1):
            age = get_folder_age(folder_path)
            print(f"[A{index}] {folder_path.name}")
            print(f"     Approved: {age}")
            print(f"     Status: ⏳ Awaiting Execution")
            print()

    # Display instructions
    print(f"{'='*60}")
    print(f"APPROVAL INSTRUCTIONS")
    print(f"{'='*60}\n")

    print("To APPROVE an item:")
    print("  mv Pending_Approval/[folder-name] Approved/\n")

    print("To MODIFY an item:")
    print("  Edit the Plan.md file in Pending_Approval/[folder-name]/")
    print("  Keep the folder in Pending_Approval/\n")

    print("To REJECT an item:")
    print("  echo 'Reason' > Pending_Approval/[folder-name]/REJECTION_REASON.md")
    print("  mv Pending_Approval/[folder-name] Rejected/\n")

    # Alerts
    alerts = []

    # Check for old items
    for folder_path, plan_summary in pending_items:
        age_seconds = datetime.now().timestamp() - folder_path.stat().st_ctime
        age_hours = age_seconds / 3600

        if age_hours > 24:
            alerts.append(f"⚠️  Item pending > 24 hours: {folder_path.name}")

        if plan_summary['priority'] == 'high' and age_hours > 4:
            alerts.append(f"🔴 High-priority item waiting > 4 hours: {folder_path.name}")

    if alerts:
        print(f"{'='*60}")
        print(f"⚠️  ALERTS")
        print(f"{'='*60}\n")
        for alert in alerts:
            print(f"  {alert}")
        print()

    # Next steps
    print(f"{'='*60}")
    print(f"NEXT STEPS")
    print(f"{'='*60}\n")

    if pending_items:
        print("1. Review each pending item above")
        print("2. Read full Plan.md for items requiring approval")
        print("3. Make approval decisions")
        print("4. Move approved items to /Approved/ folder")
        print("5. Operational Executor will process items in /Approved/")
    else:
        print("✅ All items have been reviewed")
        print("   Check back later for new items")

    print(f"\n{'='*60}\n")


def main():
    """Main entry point for approval monitor script."""
    # Get vault path from command line or use current directory
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    # Validate vault path
    if not vault_path.exists():
        print(f"❌ Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Display approval monitor
    display_approval_monitor(vault_path)

    sys.exit(0)


if __name__ == '__main__':
    main()
