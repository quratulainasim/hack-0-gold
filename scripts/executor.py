#!/usr/bin/env python3
"""
Executor Script - Execute approved plans using MCP tools
Part of Multi-Agent Workflow System - Silver Tier
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add executor skills to path
sys.path.insert(0, str(Path(__file__).parent.parent / '.claude' / 'skills' / 'executor'))

try:
    from gmail_api import send_email
    from linkedin_api import LinkedInAPI
except ImportError as e:
    print(f"[ERROR] Failed to import MCP tools: {e}")
    sys.exit(1)


def scan_approved_folder(vault_path):
    """Scan /Approved folder for items ready for execution"""
    approved_path = vault_path / 'Approved'

    if not approved_path.exists():
        print("[INFO] No /Approved folder found")
        return []

    items = []
    for item in approved_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            plan_file = item / 'Plan.md'
            if plan_file.exists():
                items.append(item)

    return items


def parse_plan(plan_path):
    """Parse Plan.md to extract execution details"""
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract MCP tool
        mcp_tool = 'UNKNOWN'
        if 'LINKEDIN MCP' in content.upper() or 'LinkedIn MCP' in content:
            mcp_tool = 'LINKEDIN'
        elif 'GMAIL MCP' in content.upper() or 'Gmail MCP' in content:
            mcp_tool = 'GMAIL'

        # Extract draft content
        draft_match = re.search(r'\*\*Draft Content\*\*\s*\n\n(.*?)(?:\n\n---|\n\n###|\Z)', content, re.DOTALL)
        draft_content = draft_match.group(1).strip() if draft_match else ''

        # Extract target (email or profile)
        target = ''
        target_match = re.search(r'\*\*To\*\*:\s*(.+)', content)
        if target_match:
            target = target_match.group(1).strip()

        # Extract subject for emails
        subject = ''
        subject_match = re.search(r'\*\*Subject\*\*:\s*(.+)', content)
        if subject_match:
            subject = subject_match.group(1).strip()

        return {
            'mcp_tool': mcp_tool,
            'draft_content': draft_content,
            'target': target,
            'subject': subject
        }

    except Exception as e:
        print(f"[ERROR] Failed to parse plan: {e}")
        return None


def execute_gmail(plan_data, item_path):
    """Execute email via Gmail MCP"""
    print(f"  [EMAIL] Sending email via Gmail API...")
    print(f"     To: {plan_data['target']}")
    print(f"     Subject: {plan_data['subject']}")

    if not plan_data['target']:
        return False, "Recipient address required"

    if not plan_data['draft_content']:
        return False, "Email body is empty"

    try:
        result = send_email(
            to=plan_data['target'],
            subject=plan_data['subject'],
            body=plan_data['draft_content']
        )

        if result and result.get('success'):
            message_id = result.get('message_id', '')
            print(f"  [SUCCESS] Email sent - Message ID: {message_id}")
            return True, f"Message ID: {message_id}"
        else:
            error = result.get('error', 'Unknown error')
            return False, f"Failed to send email: {error}"

    except Exception as e:
        error_msg = str(e)
        print(f"  [ERROR] Failed to send email: {error_msg}")
        return False, error_msg


def execute_linkedin(plan_data, item_path):
    """Execute LinkedIn post via LinkedIn MCP"""
    print(f"  [LINKEDIN] Posting to LinkedIn...")

    if not plan_data['draft_content']:
        return False, "Post content is empty"

    try:
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        if not access_token:
            return False, "LinkedIn access token not found in .env"

        api = LinkedInAPI(access_token)
        result = api.post_update(plan_data['draft_content'])

        if result and result.get('success'):
            post_id = result.get('post_id', '')
            print(f"  [SUCCESS] LinkedIn post published - Post ID: {post_id}")
            return True, f"Post ID: {post_id}"
        else:
            error = result.get('error', 'Unknown error')
            return False, f"Failed to post: {error}"

    except Exception as e:
        error_msg = str(e)
        print(f"  [ERROR] Failed to post to LinkedIn: {error_msg}")
        return False, error_msg


def create_execution_summary(item_path, plan_data, success, result_msg):
    """Create execution summary document"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "SUCCESS" if success else "FAILED"
    status_icon = "OK" if success else "ERROR"

    summary = f"""# Execution Summary

**Executed**: {timestamp}
**Status**: [{status_icon}] {status}
**Executor**: Automated Executor

---

## Action Details

**Type**: {plan_data['mcp_tool']} Action
**Tool Used**: {plan_data['mcp_tool']} MCP
**Target**: {plan_data.get('target', 'N/A')}

---

## Execution Log

{timestamp} - Started execution
{timestamp} - Connected to {plan_data['mcp_tool']} MCP
{timestamp} - {'Completed successfully' if success else 'Failed'}

**Result**: {result_msg}

---

## Content Executed

{plan_data['draft_content']}

---

## Results

{'OK' if success else 'ERROR'} Execution {'completed successfully' if success else 'failed'}

---

*Execution completed by executor script on {timestamp}*
"""

    summary_path = item_path / 'EXECUTION_SUMMARY.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"  [LOG] Execution summary created")


def create_error_report(item_path, plan_data, error_msg):
    """Create error report for failed execution"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    error_report = f"""# Execution Error Report

**Attempted**: {timestamp}
**Status**: [ERROR] Failed
**Error**: {error_msg}

---

## Error Details

Error Type: ExecutionError
Error Message: {error_msg}
Timestamp: {timestamp}

---

## Recommended Action

- Review error details above
- Check MCP tool configuration
- Verify network connectivity
- Retry execution manually
- If persistent, escalate to human

---

*Error logged by executor skill on {timestamp}*
"""

    error_path = item_path / 'ERROR.md'
    with open(error_path, 'w', encoding='utf-8') as f:
        f.write(error_report)

    print(f"  [ERROR] Error report created")


def archive_to_done(item_path, vault_path):
    """Move completed item to /Done folder with date organization"""
    import shutil

    done_path = vault_path / 'Done'
    done_path.mkdir(exist_ok=True)

    # Create date folder
    date_folder = datetime.now().strftime('%Y-%m-%d')
    date_path = done_path / date_folder
    date_path.mkdir(exist_ok=True)

    # Move item
    dest_path = date_path / item_path.name

    try:
        shutil.move(str(item_path), str(dest_path))
        print(f"  [ARCHIVE] Moved to /Done/{date_folder}/{item_path.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to archive: {e}")
        return False


def execute_item(item_path, vault_path):
    """Execute a single approved item"""
    print(f"\n{'='*60}")
    print(f"Executing: {item_path.name}")
    print('='*60)

    # Parse plan
    plan_path = item_path / 'Plan.md'
    plan_data = parse_plan(plan_path)

    if not plan_data:
        print("  [ERROR] Failed to parse Plan.md")
        return False

    # Check for draft content
    if not plan_data['draft_content']:
        print("  [WARN]  Warning: No draft content found in Plan.md")
        print("     Execution may not be possible")

    print(f"  [PLAN] Tool: {plan_data['mcp_tool']} MCP")
    print(f"  [TARGET] Target: {plan_data.get('target', '')}")

    # Execute based on MCP tool
    success = False
    result_msg = ""

    if plan_data['mcp_tool'] == 'GMAIL':
        success, result_msg = execute_gmail(plan_data, item_path)
    elif plan_data['mcp_tool'] == 'LINKEDIN':
        success, result_msg = execute_linkedin(plan_data, item_path)
    else:
        print(f"  [ERROR] Error: Unknown MCP tool: {plan_data['mcp_tool'].lower()}")
        result_msg = f"Unknown MCP tool: {plan_data['mcp_tool']}"

    # Create execution summary or error report
    if success:
        create_execution_summary(item_path, plan_data, success, result_msg)
        archive_to_done(item_path, vault_path)
        print(f"  [COMPLETE] Execution completed successfully")
    else:
        create_error_report(item_path, plan_data, result_msg)
        print(f"  [ERROR] Execution failed")

    return success


def main():
    """Main executor function"""
    # Determine vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    print(f"\n{'='*60}")
    print("EXECUTOR - Multi-Agent Workflow System")
    print('='*60)
    print(f"Vault: {vault_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)

    # Scan for approved items
    items = scan_approved_folder(vault_path)

    if not items:
        print("\n[INFO] No items found in /Approved folder")
        print("\nExecution complete - nothing to process")
        return

    print(f"\n[INFO] Found {len(items)} item(s) ready for execution")

    # Execute each item
    success_count = 0
    fail_count = 0

    for item in items:
        success = execute_item(item, vault_path)
        if success:
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*60}")
    print("EXECUTION SUMMARY")
    print('='*60)
    print(f"Total Items: {len(items)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print('='*60)
    print("\nExecution complete")


if __name__ == '__main__':
    main()
