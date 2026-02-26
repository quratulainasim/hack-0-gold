#!/usr/bin/env python3
"""
Update Dashboard Script - Generate executive dashboard with real-time metrics
Part of Multi-Agent Workflow System - Silver Tier
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    frontmatter = {}

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter


def get_title_from_content(content):
    """Extract title from markdown content"""
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]

    # Find first heading or first line
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            return title[:80] if len(title) > 80 else title
        elif line and not line.startswith('**'):
            return line[:80] if len(line) > 80 else line

    return "Untitled"


def count_needs_action(vault_path):
    """Count markdown files in /Needs_Action folder"""
    needs_action_path = vault_path / 'Needs_Action'

    if not needs_action_path.exists():
        return 0

    count = 0
    for item in needs_action_path.iterdir():
        if item.is_file() and item.suffix == '.md' and item.name != '.gitkeep':
            count += 1

    return count


def get_completed_items(vault_path, limit=5):
    """Get last N completed items from /Done folder"""
    done_path = vault_path / 'Done'

    if not done_path.exists():
        return []

    items = []

    # Scan all date folders in Done/
    for date_folder in done_path.iterdir():
        if not date_folder.is_dir() or date_folder.name.startswith('.'):
            continue

        # Scan items in date folder
        for item_folder in date_folder.iterdir():
            if not item_folder.is_dir():
                continue

            # Look for markdown files
            for md_file in item_folder.glob('*.md'):
                if md_file.name in ['Plan.md', 'EXECUTION_SUMMARY.md', 'ERROR.md']:
                    continue

                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter = parse_frontmatter(content)
                    title = get_title_from_content(content)

                    item_type = frontmatter.get('type', 'unknown')
                    priority = frontmatter.get('priority', 'normal')
                    completed_at = frontmatter.get('completed_at', '')

                    # Use file modification time if no completed_at
                    if not completed_at:
                        mtime = md_file.stat().st_mtime
                        completed_at = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

                    items.append({
                        'title': title,
                        'type': item_type,
                        'priority': priority,
                        'completed_at': completed_at,
                        'folder': item_folder.name
                    })

                except Exception as e:
                    print(f"[WARN] Failed to read {md_file}: {e}")
                    continue

    # Sort by completion time (most recent first)
    items.sort(key=lambda x: x['completed_at'], reverse=True)

    return items[:limit]


def get_priority_indicator(priority):
    """Get visual indicator for priority level"""
    priority_lower = priority.lower()

    if priority_lower in ['high', 'urgent', 'critical']:
        return 'HIGH'
    elif priority_lower in ['medium', 'moderate']:
        return 'MED'
    elif priority_lower in ['low']:
        return 'LOW'
    else:
        return 'NORM'


def get_workload_status(count):
    """Get workload status indicator"""
    if count == 0:
        return "OK All clear", "green"
    elif count <= 3:
        return "OK Low volume, manageable", "green"
    elif count <= 10:
        return "WARN Moderate volume, monitor closely", "yellow"
    else:
        return "ALERT High volume, prioritization needed", "red"


def generate_dashboard_content(vault_path):
    """Generate dashboard markdown content"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get metrics
    needs_action_count = count_needs_action(vault_path)
    completed_items = get_completed_items(vault_path, limit=5)

    # Get workload status
    status_text, status_color = get_workload_status(needs_action_count)

    # Build dashboard content
    content = f"""# Multi-Agent Workflow Dashboard

**Last Updated**: {timestamp}
**System Status**: Operational

---

## Real-time Summary

**Items Requiring Action**: {needs_action_count}

**Workload Status**: [{status_text}]

---

## Recently Completed (Last 5)

"""

    if completed_items:
        for item in completed_items:
            priority_indicator = get_priority_indicator(item['priority'])
            content += f"- [{priority_indicator}] {item['title']}\n"
            content += f"  - Type: {item['type']}\n"
            content += f"  - Completed: {item['completed_at']}\n\n"
    else:
        content += "No completed items found.\n\n"

    content += """---

## Quick Actions

- Review items in /Needs_Action folder
- Process pending approvals in /Pending_Approval
- Execute approved items in /Approved
- Monitor /Inbox for new incoming tasks

---

## Vault Health

**Folders**:
- Inbox: Ready for triage
- Needs_Action: Awaiting planning
- Pending_Approval: Awaiting human review
- Approved: Ready for execution
- Done: Archived by date

**Integrations**:
- Gmail: Operational
- LinkedIn: Operational
- WhatsApp: Operational

---

*Dashboard generated by update-dashboard skill*
*Multi-Agent Workflow System - Silver Tier*
"""

    return content


def main():
    """Main dashboard update function"""
    # Determine vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    print(f"\n{'='*60}")
    print("UPDATE DASHBOARD - Multi-Agent Workflow System")
    print('='*60)
    print(f"Vault: {vault_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)

    # Generate dashboard content
    print("\n[INFO] Scanning vault folders...")
    needs_action_count = count_needs_action(vault_path)
    print(f"[INFO] Found {needs_action_count} item(s) in /Needs_Action")

    completed_items = get_completed_items(vault_path, limit=5)
    print(f"[INFO] Found {len(completed_items)} completed item(s)")

    # Generate and write dashboard
    print("\n[INFO] Generating dashboard content...")
    dashboard_content = generate_dashboard_content(vault_path)

    dashboard_path = vault_path / 'Dashboard.md'
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_content)

    print(f"[OK] Dashboard updated: {dashboard_path}")

    # Show summary
    status_text, status_color = get_workload_status(needs_action_count)
    print(f"\n{'='*60}")
    print("DASHBOARD SUMMARY")
    print('='*60)
    print(f"Items Requiring Action: {needs_action_count}")
    print(f"Workload Status: [{status_text}]")
    print(f"Recently Completed: {len(completed_items)} items")
    print('='*60)
    print("\nDashboard update complete")


if __name__ == '__main__':
    main()
