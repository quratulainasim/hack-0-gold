#!/usr/bin/env python3
"""
Dashboard Update Script

This script updates Dashboard.md with real-time vault metrics:
1. Counts files in /Needs_Action
2. Extracts last 5 entries from /Done folder
3. Rewrites Dashboard.md with a 'Real-time Summary' section
4. Maintains CEO-friendly, scannable layout

Usage:
    python update_dashboard.py [vault_path]

    If vault_path is not provided, uses current working directory.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def get_file_summary(file_path: Path) -> Dict:
    """
    Extract summary information from a markdown file.

    Returns:
        Dictionary with file metadata and summary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        # Extract first line of body as title/summary
        first_line = body.split('\n')[0].strip() if body else ''
        # Remove markdown heading markers
        first_line = first_line.lstrip('#').strip()

        return {
            'filename': file_path.name,
            'type': frontmatter.get('type', 'unknown') if frontmatter else 'unknown',
            'priority': frontmatter.get('priority', 'normal') if frontmatter else 'normal',
            'status': frontmatter.get('status', 'unknown') if frontmatter else 'unknown',
            'completed_at': frontmatter.get('completed_at', '') if frontmatter else '',
            'triaged_at': frontmatter.get('triaged_at', '') if frontmatter else '',
            'title': first_line[:80] if first_line else file_path.stem,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
        }
    except Exception as e:
        return {
            'filename': file_path.name,
            'type': 'error',
            'priority': 'unknown',
            'status': 'error',
            'completed_at': '',
            'triaged_at': '',
            'title': f'Error reading file: {e}',
            'modified': datetime.now()
        }


def count_needs_action(vault_path: Path) -> int:
    """Count markdown files in /Needs_Action folder."""
    needs_action_path = vault_path / 'Needs_Action'

    if not needs_action_path.exists():
        return 0

    md_files = list(needs_action_path.glob('*.md'))
    return len(md_files)


def get_last_done_items(vault_path: Path, count: int = 5) -> List[Dict]:
    """
    Get the last N completed items from /Done folder.

    Returns:
        List of file summaries, sorted by modification time (newest first)
    """
    done_path = vault_path / 'Done'

    if not done_path.exists():
        return []

    md_files = list(done_path.glob('*.md'))

    if not md_files:
        return []

    # Get summaries for all files
    file_summaries = [get_file_summary(f) for f in md_files]

    # Sort by modified time, newest first
    file_summaries.sort(key=lambda x: x['modified'], reverse=True)

    # Return last N items
    return file_summaries[:count]


def generate_dashboard_content(vault_path: Path, needs_action_count: int, done_items: List[Dict]) -> str:
    """
    Generate the complete Dashboard.md content with real-time summary.

    Returns:
        Formatted markdown content
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Build the dashboard content
    lines = [
        '# Executive Dashboard',
        '',
        f'*Last updated: {now}*',
        '',
        '---',
        '',
        '## 📊 Real-time Summary',
        '',
        '### Current Status',
        '',
        f'**Items Requiring Action:** {needs_action_count}',
        '',
    ]

    # Add urgency indicator
    if needs_action_count == 0:
        lines.append('✅ All clear - no pending actions')
    elif needs_action_count <= 3:
        lines.append('🟢 Low volume - manageable workload')
    elif needs_action_count <= 10:
        lines.append('🟡 Moderate volume - monitor closely')
    else:
        lines.append('🔴 High volume - prioritization needed')

    lines.extend([
        '',
        '### Recently Completed',
        '',
    ])

    if done_items:
        lines.append(f'*Last {len(done_items)} completed items:*')
        lines.append('')

        for i, item in enumerate(done_items, 1):
            # Format completion time
            completed_time = item.get('completed_at', '')
            if not completed_time:
                completed_time = item['modified'].strftime('%Y-%m-%d %H:%M')

            # Priority indicator
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'normal': '⚪',
                'low': '🔵'
            }.get(item['priority'].lower(), '⚪')

            # Format the item
            lines.append(f"{i}. {priority_icon} **{item['title']}**")
            lines.append(f"   - Type: {item['type']} | Completed: {completed_time}")
            lines.append('')
    else:
        lines.append('*No completed items yet*')
        lines.append('')

    lines.extend([
        '---',
        '',
        '## 📋 Quick Actions',
        '',
        '- Review items in `/Needs_Action`',
        '- Triage new items in `/Inbox`',
        '- Archive old items from `/Done`',
        '',
        '---',
        '',
        '## 📈 Vault Health',
        '',
        f'- **Needs Action:** {needs_action_count} items',
        f'- **Recently Completed:** {len(done_items)} items',
        f'- **System Status:** ✅ Operational',
        '',
    ])

    return '\n'.join(lines)


def update_dashboard(vault_path: Optional[str] = None) -> Dict:
    """
    Update Dashboard.md with real-time metrics.

    Args:
        vault_path: Path to vault directory (defaults to current directory)

    Returns:
        Dictionary with update results
    """
    # Use current directory if no path provided
    if vault_path is None:
        vault_path = Path.cwd()
    else:
        vault_path = Path(vault_path).resolve()

    print(f"Updating dashboard at: {vault_path}")
    print()

    results = {
        'success': True,
        'needs_action_count': 0,
        'done_items_count': 0,
        'dashboard_updated': False,
        'errors': []
    }

    # Step 1: Count files in Needs_Action
    print("Step 1: Counting items in /Needs_Action...")
    try:
        needs_action_count = count_needs_action(vault_path)
        results['needs_action_count'] = needs_action_count
        print(f"  [OK] Found {needs_action_count} items requiring action")
    except Exception as e:
        error_msg = f"Error counting Needs_Action items: {e}"
        print(f"  [ERROR] {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        needs_action_count = 0

    print()

    # Step 2: Get last 5 done items
    print("Step 2: Extracting last 5 completed items from /Done...")
    try:
        done_items = get_last_done_items(vault_path, count=5)
        results['done_items_count'] = len(done_items)
        print(f"  [OK] Found {len(done_items)} completed items")

        if done_items:
            print("  Recent completions:")
            for item in done_items[:3]:  # Show first 3
                print(f"    - {item['title'][:60]}")
    except Exception as e:
        error_msg = f"Error extracting Done items: {e}"
        print(f"  [ERROR] {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False
        done_items = []

    print()

    # Step 3: Generate and write Dashboard.md
    print("Step 3: Updating Dashboard.md...")
    try:
        dashboard_content = generate_dashboard_content(vault_path, needs_action_count, done_items)
        dashboard_path = vault_path / 'Dashboard.md'

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

        results['dashboard_updated'] = True
        print(f"  [OK] Dashboard.md updated successfully")
        print(f"  Location: {dashboard_path}")
    except Exception as e:
        error_msg = f"Error writing Dashboard.md: {e}"
        print(f"  [ERROR] {error_msg}")
        results['errors'].append(error_msg)
        results['success'] = False

    print()

    # Summary
    print("=" * 60)
    print("DASHBOARD UPDATE SUMMARY")
    print("=" * 60)
    print(f"Items requiring action: {results['needs_action_count']}")
    print(f"Recently completed: {results['done_items_count']}")
    print(f"Dashboard updated: {'Yes' if results['dashboard_updated'] else 'No'}")

    if results['errors']:
        print()
        print("ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")

    print()

    if results['success']:
        print("[SUCCESS] Dashboard update complete!")
    else:
        print("[FAILED] Dashboard update incomplete - see errors above")

    return results


def main():
    """Main entry point for the script."""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else None

    results = update_dashboard(vault_path)

    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
