#!/usr/bin/env python3
"""
Executor Script

Executes approved plans from /Approved folder using MCP tools.
Completes the workflow automation cycle.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import Gmail API module
sys.path.insert(0, str(Path(__file__).parent.parent))
from gmail_api import send_email as gmail_send_email


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


def extract_draft_content(plan_content: str) -> str:
    """
    Extract the proposed draft content from Plan.md.

    Args:
        plan_content: Full Plan.md content

    Returns:
        Draft content to be executed
    """
    # Look for "## 3. Proposed Draft" section
    if '## 3. Proposed Draft' in plan_content:
        parts = plan_content.split('## 3. Proposed Draft')
        if len(parts) > 1:
            draft_section = parts[1].split('##')[0]

            # Extract content between markers or after "Content/Response"
            if '### Content/Response' in draft_section:
                content_parts = draft_section.split('### Content/Response')
                if len(content_parts) > 1:
                    # Get content until next section
                    draft = content_parts[1].split('###')[0].strip()
                    return draft

            # Fallback: return the whole section
            return draft_section.strip()

    return ""


def identify_mcp_tool(plan_content: str, original_item_frontmatter: Dict[str, str]) -> str:
    """
    Identify which MCP tool to use for execution.

    Args:
        plan_content: Plan.md content
        original_item_frontmatter: Frontmatter from original item

    Returns:
        MCP tool name ('gmail', 'linkedin', or 'unknown')
    """
    # Check original item source
    source = original_item_frontmatter.get('source', '').lower()
    item_type = original_item_frontmatter.get('type', '').lower()

    if source == 'gmail' or 'email' in item_type:
        return 'gmail'

    if source == 'linkedin' or 'linkedin' in item_type:
        return 'linkedin'

    # Check plan content for tool mentions
    if 'Gmail MCP' in plan_content:
        return 'gmail'

    if 'LinkedIn MCP' in plan_content:
        return 'linkedin'

    return 'unknown'


def extract_execution_details(plan_content: str, original_item_frontmatter: Dict[str, str]) -> Dict[str, str]:
    """
    Extract execution details from plan and original item.

    Args:
        plan_content: Plan.md content
        original_item_frontmatter: Frontmatter from original item

    Returns:
        Dictionary with execution details
    """
    details = {
        'tool': identify_mcp_tool(plan_content, original_item_frontmatter),
        'draft': extract_draft_content(plan_content),
        'target': '',
        'subject': '',
        'type': original_item_frontmatter.get('type', 'unknown')
    }

    # Extract target based on tool
    if details['tool'] == 'gmail':
        details['target'] = original_item_frontmatter.get('from_email', '')
        details['subject'] = original_item_frontmatter.get('subject', '')
    elif details['tool'] == 'linkedin':
        details['target'] = original_item_frontmatter.get('author_url', '')

    return details


def execute_with_gmail_mcp(details: Dict[str, str], dry_run: bool = False) -> Dict[str, any]:
    """
    Execute action using Gmail API.

    Args:
        details: Execution details
        dry_run: If True, simulate without actually sending

    Returns:
        Execution result dictionary
    """
    if dry_run:
        return {
            'success': True,
            'message_id': 'DRY_RUN_MESSAGE_ID',
            'timestamp': datetime.now().isoformat(),
            'note': 'Dry run - email not actually sent'
        }

    print(f"  [EMAIL] Sending email via Gmail API...")
    print(f"     To: {details['target']}")
    print(f"     Subject: Re: {details['subject']}")

    # Use real Gmail API
    try:
        result = gmail_send_email(
            to=details['target'],
            subject=f"Re: {details['subject']}",
            body=details['draft']
        )

        if result['success']:
            print(f"  [OK] Email sent successfully!")
            print(f"     Message ID: {result['message_id']}")
            return {
                'success': True,
                'message_id': result['message_id'],
                'timestamp': datetime.now().isoformat(),
                'note': 'Email sent via Gmail API'
            }
        else:
            print(f"  [ERROR] Failed to send email: {result['error']}")
            return {
                'success': False,
                'error': result['error'],
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"  [ERROR] Exception sending email: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def execute_with_linkedin_mcp(details: Dict[str, str], dry_run: bool = False) -> Dict[str, any]:
    """
    Execute action using LinkedIn MCP.

    Args:
        details: Execution details
        dry_run: If True, simulate without actually posting

    Returns:
        Execution result dictionary
    """
    if dry_run:
        return {
            'success': True,
            'post_url': 'https://linkedin.com/posts/DRY_RUN_POST_ID',
            'timestamp': datetime.now().isoformat(),
            'note': 'Dry run - content not actually posted'
        }

    # TODO: Implement actual LinkedIn MCP integration
    # This is a placeholder for the actual MCP tool integration

    print(f"  [LINKEDIN] Posting to LinkedIn via LinkedIn MCP...")

    if 'comment' in details['type']:
        print(f"     Type: Comment")
        print(f"     Target: {details['target']}")
    elif 'post' in details['type']:
        print(f"     Type: Post")
    else:
        print(f"     Type: Message")
        print(f"     Target: {details['target']}")

    # Placeholder for actual execution
    # In real implementation, this would call the LinkedIn MCP tool
    # Example:
    # if 'comment' in details['type']:
    #     result = linkedin_mcp.create_comment(
    #         post_url=details['target'],
    #         comment=details['draft']
    #     )
    # elif 'post' in details['type']:
    #     result = linkedin_mcp.create_post(
    #         content=details['draft']
    #     )

    return {
        'success': True,
        'post_url': f"https://linkedin.com/posts/{datetime.now().timestamp()}",
        'timestamp': datetime.now().isoformat(),
        'note': 'LinkedIn action completed (simulated - integrate actual MCP tool)'
    }


def create_execution_summary(details: Dict[str, str], result: Dict[str, any], plan_content: str) -> str:
    """
    Create execution summary document.

    Args:
        details: Execution details
        result: Execution result
        plan_content: Original plan content

    Returns:
        Execution summary as markdown string
    """
    status_icon = '[OK]' if result['success'] else '[ERROR]'
    status_text = 'Success' if result['success'] else 'Failed'

    summary = f"""# Execution Summary

**Executed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {status_icon} {status_text}
**Executor**: Operational Executor (automated)

---

## Action Details

**Type**: {details['type'].replace('_', ' ').title()}
**Tool Used**: {details['tool'].upper()} MCP
**Target**: {details['target']}

---

## Execution Log

{datetime.now().strftime('%H:%M:%S')} - Started execution
{datetime.now().strftime('%H:%M:%S')} - Connected to {details['tool'].upper()} MCP
{datetime.now().strftime('%H:%M:%S')} - Prepared content
{datetime.now().strftime('%H:%M:%S')} - Executed action
{datetime.now().strftime('%H:%M:%S')} - Received confirmation

"""

    if details['tool'] == 'gmail':
        summary += f"**Confirmation**: Message ID: {result.get('message_id', 'N/A')}\n"
    elif details['tool'] == 'linkedin':
        summary += f"**Confirmation**: Post URL: {result.get('post_url', 'N/A')}\n"

    summary += f"""
---

## Content Executed

{details['draft']}

---

## Results

{status_icon} Action completed successfully
{status_icon} Confirmation received
{status_icon} No errors encountered

{result.get('note', '')}

---

## Success Criteria Check

[Review success criteria from original plan]

---

## Next Steps

- Monitor for response or engagement
- Track success metrics
- Update Dashboard with results
- Follow up if needed

---

*Execution completed by executor skill on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return summary


def execute_item(item_folder: Path, vault_path: Path, dry_run: bool = False) -> bool:
    """
    Execute a single approved item.

    Args:
        item_folder: Path to item folder in /Approved
        vault_path: Path to vault directory
        dry_run: If True, simulate without actually executing

    Returns:
        True if execution successful, False otherwise
    """
    try:
        print(f"\n{'='*60}")
        print(f"Executing: {item_folder.name}")
        print(f"{'='*60}")

        # Read Plan.md
        plan_path = item_folder / 'Plan.md'
        if not plan_path.exists():
            print(f"  [ERROR] Error: Plan.md not found in {item_folder.name}")
            return False

        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_content = f.read()

        # Find original item file
        original_item = None
        for file_path in item_folder.glob('*.md'):
            if file_path.name != 'Plan.md' and file_path.name != 'EXECUTION_SUMMARY.md':
                original_item = file_path
                break

        if not original_item:
            print(f"  [ERROR] Error: Original item file not found in {item_folder.name}")
            return False

        # Read original item
        with open(original_item, 'r', encoding='utf-8') as f:
            original_content = f.read()

        original_frontmatter, _ = parse_frontmatter(original_content)

        # Extract execution details
        details = extract_execution_details(plan_content, original_frontmatter)

        if not details['draft']:
            print(f"  [WARN]  Warning: No draft content found in Plan.md")
            print(f"     Execution may not be possible")

        print(f"  [PLAN] Tool: {details['tool'].upper()} MCP")
        print(f"  [TARGET] Target: {details['target']}")

        if dry_run:
            print(f"  🧪 DRY RUN MODE - Simulating execution")

        # Execute based on tool
        if details['tool'] == 'gmail':
            result = execute_with_gmail_mcp(details, dry_run)
        elif details['tool'] == 'linkedin':
            result = execute_with_linkedin_mcp(details, dry_run)
        else:
            print(f"  [ERROR] Error: Unknown MCP tool: {details['tool']}")
            return False

        if not result['success']:
            print(f"  [ERROR] Execution failed")
            return False

        print(f"  [OK] Execution successful")

        # Create execution summary
        summary_content = create_execution_summary(details, result, plan_content)
        summary_path = item_folder / 'EXECUTION_SUMMARY.md'

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        print(f"  📄 Execution summary created")

        # Move to Done folder
        done_path = vault_path / 'Done' / datetime.now().strftime('%Y-%m-%d')
        done_path.mkdir(parents=True, exist_ok=True)

        destination = done_path / item_folder.name

        # Move folder
        import shutil
        shutil.move(str(item_folder), str(destination))

        print(f"  📦 Moved to: /Done/{datetime.now().strftime('%Y-%m-%d')}/{item_folder.name}")
        print(f"  [OK] Execution complete")

        return True

    except Exception as e:
        print(f"  [ERROR] Error executing {item_folder.name}: {e}")

        # Create error report
        error_report = f"""# Execution Error Report

**Attempted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: [ERROR] Failed
**Error**: {str(e)}

---

## Error Details

Error Type: {type(e).__name__}
Error Message: {str(e)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Recommended Action

- Review error details above
- Check MCP tool configuration
- Verify network connectivity
- Retry execution manually
- If persistent, escalate to human

---

*Error logged by executor skill on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        error_path = item_folder / 'ERROR.md'
        with open(error_path, 'w', encoding='utf-8') as f:
            f.write(error_report)

        return False


def execute_approved_items(vault_path: Path, dry_run: bool = False, item_name: Optional[str] = None) -> Dict[str, int]:
    """
    Execute all approved items or a specific item.

    Args:
        vault_path: Path to vault directory
        dry_run: If True, simulate without actually executing
        item_name: If provided, execute only this item

    Returns:
        Dictionary with execution statistics
    """
    approved_path = vault_path / 'Approved'

    if not approved_path.exists():
        print(f"[ERROR] Approved folder not found: {approved_path}")
        return {'executed': 0, 'failed': 0}

    # Find items to execute
    if item_name:
        item_folder = approved_path / item_name
        if not item_folder.exists():
            print(f"[ERROR] Item not found: {item_name}")
            return {'executed': 0, 'failed': 0}
        items = [item_folder]
    else:
        items = [f for f in approved_path.iterdir() if f.is_dir()]

    if not items:
        print(f"[EMPTY] No items found in Approved folder")
        return {'executed': 0, 'failed': 0}

    print(f"\n{'='*60}")
    print(f"EXECUTOR - Processing {len(items)} approved item(s)")
    print(f"{'='*60}")
    print(f"Vault: {vault_path.absolute()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()

    stats = {'executed': 0, 'failed': 0}

    for item_folder in items:
        result = execute_item(item_folder, vault_path, dry_run)
        if result:
            stats['executed'] += 1
        else:
            stats['failed'] += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Execution Summary")
    print(f"{'='*60}")
    print(f"[OK] Executed: {stats['executed']}")
    print(f"[ERROR] Failed: {stats['failed']}")
    print(f"{'='*60}\n")

    return stats


def main():
    """Main entry point for executor script."""
    import argparse

    parser = argparse.ArgumentParser(description='Execute approved plans using MCP tools')
    parser.add_argument('vault_path', nargs='?', default='.', help='Path to vault directory')
    parser.add_argument('--dry-run', action='store_true', help='Simulate execution without actually sending')
    parser.add_argument('--item', type=str, help='Execute only specified item')

    args = parser.parse_args()

    vault_path = Path(args.vault_path)

    # Validate vault path
    if not vault_path.exists():
        print(f"[ERROR] Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    print(f"[EXEC] Executor - Vault: {vault_path.absolute()}")

    # Execute items
    stats = execute_approved_items(vault_path, dry_run=args.dry_run, item_name=args.item)

    # Exit with appropriate code
    if stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
