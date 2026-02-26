#!/usr/bin/env python3
"""
Gmail Ingest Script

Monitors /Inbox for files tagged 'source: gmail', extracts email metadata,
and formats them into standardized Task Templates.
"""

import os
import sys
import re
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


def update_frontmatter(content: str, updates: Dict[str, str]) -> str:
    """
    Update frontmatter fields in markdown content.

    Args:
        content: Original markdown content
        updates: Dictionary of fields to update

    Returns:
        Updated markdown content
    """
    frontmatter, body = parse_frontmatter(content)
    frontmatter.update(updates)

    # Rebuild frontmatter
    fm_lines = ['---']
    for key, value in frontmatter.items():
        fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')

    return '\n'.join(fm_lines) + '\n\n' + body


def sanitize_filename(text: str) -> str:
    """
    Sanitize text for use in filename.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Trim hyphens from ends
    text = text.strip('-')
    # Limit length
    return text[:50].lower()


def extract_email_data(frontmatter: Dict[str, str], body: str) -> Dict[str, str]:
    """
    Extract email metadata from Gmail inbox file.

    Args:
        frontmatter: Parsed frontmatter dictionary
        body: Email body content

    Returns:
        Dictionary with extracted email data
    """
    email_data = {
        'from_name': frontmatter.get('from_name', 'Unknown'),
        'from_email': frontmatter.get('from_email', 'unknown@example.com'),
        'subject': frontmatter.get('subject', 'No Subject'),
        'received': frontmatter.get('received', datetime.now().strftime('%Y-%m-%d %H:%M')),
        'priority': frontmatter.get('priority', 'normal'),
        'has_attachments': frontmatter.get('has_attachments', 'no'),
        'thread_id': frontmatter.get('thread_id', ''),
        'body': body
    }

    return email_data


def load_task_template(vault_path: Path) -> Optional[str]:
    """
    Load Task Template format from Company_Handbook.md if available.

    Args:
        vault_path: Path to vault directory

    Returns:
        Task template string or None if not found
    """
    handbook_path = vault_path / 'Company_Handbook.md'

    if handbook_path.exists():
        try:
            with open(handbook_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Look for Task Template section
                if 'Task Template' in content or 'task template' in content:
                    # Extract template section (simplified - could be more sophisticated)
                    return content
        except Exception as e:
            print(f"Warning: Could not load Company_Handbook.md: {e}")

    return None


def generate_task_template(email_data: Dict[str, str], original_file: str) -> str:
    """
    Generate standardized Task Template from email data.

    Args:
        email_data: Extracted email metadata
        original_file: Path to original Gmail file

    Returns:
        Formatted task template as markdown string
    """
    template = f"""---
source: gmail
type: email_task
priority: {email_data['priority']}
received: {email_data['received']}
status: pending
created_from: {original_file}
from_email: {email_data['from_email']}
from_name: {email_data['from_name']}
subject: {email_data['subject']}
has_attachments: {email_data['has_attachments']}
---

# Task: {email_data['subject']}

## Source Information
- **From**: {email_data['from_name']} <{email_data['from_email']}>
- **Received**: {email_data['received']}
- **Original Email**: [{original_file}](./../Inbox/{original_file})
- **Attachments**: {email_data['has_attachments']}

## Email Content

{email_data['body']}

## Proposed Actions

Based on the email content, consider these actions:

- [ ] Review and respond to sender
- [ ] Assess priority and urgency
- [ ] Identify required resources or information
- [ ] Draft response or action plan

## Response Draft

[Placeholder for response content - to be filled during planning phase]

## Notes

[Space for additional notes, context, and considerations]

---

*Task generated from Gmail inbox item on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return template


def process_gmail_file(file_path: Path, vault_path: Path) -> bool:
    """
    Process a single Gmail inbox file.

    Args:
        file_path: Path to Gmail inbox file
        vault_path: Path to vault directory

    Returns:
        True if processed successfully, False otherwise
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        frontmatter, body = parse_frontmatter(content)

        # Check if already processed
        status = frontmatter.get('status', 'new')
        if status in ['ingested', 'processing', 'completed']:
            print(f"  [SKIP] Already processed: {file_path.name}")
            return False

        # Verify it's a Gmail source
        if frontmatter.get('source') != 'gmail':
            print(f"  [SKIP] Not Gmail source: {file_path.name}")
            return False

        # Extract email data
        email_data = extract_email_data(frontmatter, body)

        # Validate required fields
        if not email_data['from_email'] or not email_data['subject']:
            print(f"  [WARN] Skipping (missing required fields): {file_path.name}")
            return False

        # Generate task template
        task_content = generate_task_template(email_data, file_path.name)

        # Create task filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        subject_slug = sanitize_filename(email_data['subject'])
        task_filename = f"{date_str}_task_{subject_slug}.md"

        # Ensure Needs_Action folder exists
        needs_action_path = vault_path / 'Needs_Action'
        needs_action_path.mkdir(exist_ok=True)

        # Save task file
        task_path = needs_action_path / task_filename
        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        # Update original file status
        updated_content = update_frontmatter(content, {
            'status': 'ingested',
            'ingested_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'task_file': task_filename
        })

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Report success
        print(f"  [OK] Processed: {file_path.name}")
        print(f"       From: {email_data['from_name']} <{email_data['from_email']}>")
        print(f"       Subject: {email_data['subject']}")
        print(f"       Task created: {task_filename}")

        return True

    except Exception as e:
        print(f"  [ERROR] Error processing {file_path.name}: {e}")
        return False


def ingest_gmail_items(vault_path: Path) -> Dict[str, int]:
    """
    Process all Gmail items in the Inbox folder.

    Args:
        vault_path: Path to vault directory

    Returns:
        Dictionary with processing statistics
    """
    inbox_path = vault_path / 'Inbox'

    if not inbox_path.exists():
        print(f"[ERROR] Inbox folder not found: {inbox_path}")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    # Find all markdown files
    md_files = list(inbox_path.glob('*.md'))

    if not md_files:
        print(f"[INFO] No markdown files found in Inbox")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    print(f"\n[Gmail Ingest] Processing {len(md_files)} files from Inbox\n")

    stats = {'processed': 0, 'skipped': 0, 'errors': 0}

    for file_path in md_files:
        result = process_gmail_file(file_path, vault_path)
        if result:
            stats['processed'] += 1
        else:
            stats['skipped'] += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Gmail Ingest Summary")
    print(f"{'='*60}")
    print(f"[OK] Processed: {stats['processed']}")
    print(f"[SKIP] Skipped: {stats['skipped']}")
    print(f"[ERROR] Errors: {stats['errors']}")
    print(f"{'='*60}\n")

    return stats


def main():
    """Main entry point for Gmail ingest script."""
    # Get vault path from command line or use current directory
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    # Validate vault path
    if not vault_path.exists():
        print(f"[ERROR] Vault path does not exist: {vault_path}")
        sys.exit(1)

    print(f"[Gmail Ingest] Vault: {vault_path.absolute()}")

    # Process Gmail items
    stats = ingest_gmail_items(vault_path)

    # Exit with appropriate code
    if stats['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
