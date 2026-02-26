#!/usr/bin/env python3
"""
LinkedIn Ingest Script

Processes incoming LinkedIn notification files, creating high-priority tasks
for Leads and Comments with user profile summaries.
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


def extract_profile_summary(body: str, frontmatter: Dict[str, str]) -> str:
    """
    Extract and format user profile summary from LinkedIn notification.

    Args:
        body: Notification body content
        frontmatter: Parsed frontmatter with profile data

    Returns:
        Formatted profile summary
    """
    author = frontmatter.get('author', 'Unknown User')
    author_url = frontmatter.get('author_url', '')
    connection_level = frontmatter.get('connection_level', 'Unknown')

    # Try to extract profile information from body
    profile_info = []

    # Look for common profile patterns in the body
    if 'CEO' in body or 'Founder' in body:
        profile_info.append('Leadership role')
    if 'years' in body.lower() and 'experience' in body.lower():
        profile_info.append('Experienced professional')
    if 'startup' in body.lower() or 'company' in body.lower():
        profile_info.append('Company affiliation')

    summary = f"""**Profile Summary**

- **Name**: {author}
- **LinkedIn**: {author_url if author_url else 'Not provided'}
- **Connection**: {connection_level}
- **Context**: {', '.join(profile_info) if profile_info else 'See full content below'}

**Quick Assessment**: This is a {connection_level} connection who has engaged with your content. Review their profile and the context of their engagement to determine the best response strategy.
"""

    return summary


def extract_linkedin_data(frontmatter: Dict[str, str], body: str) -> Dict[str, str]:
    """
    Extract LinkedIn notification metadata.

    Args:
        frontmatter: Parsed frontmatter dictionary
        body: Notification body content

    Returns:
        Dictionary with extracted LinkedIn data
    """
    notification_type = frontmatter.get('type', 'unknown')

    linkedin_data = {
        'type': notification_type,
        'author': frontmatter.get('author', 'Unknown'),
        'author_url': frontmatter.get('author_url', ''),
        'connection_level': frontmatter.get('connection_level', 'Unknown'),
        'context_url': frontmatter.get('context_url', ''),
        'received': frontmatter.get('received', datetime.now().strftime('%Y-%m-%d %H:%M')),
        'priority': frontmatter.get('priority', 'high'),  # Default to high for leads/comments
        'body': body
    }

    return linkedin_data


def should_process_notification(notification_type: str) -> bool:
    """
    Determine if notification type should be processed.

    Args:
        notification_type: Type of LinkedIn notification

    Returns:
        True if should create task, False otherwise
    """
    # Process these notification types
    process_types = ['lead', 'comment', 'dm', 'mention', 'connection_request']

    return notification_type.lower() in process_types


def generate_task_from_linkedin(linkedin_data: Dict[str, str], original_file: str, body: str, frontmatter: Dict[str, str]) -> str:
    """
    Generate high-priority task from LinkedIn notification.

    Args:
        linkedin_data: Extracted LinkedIn metadata
        original_file: Path to original notification file
        body: Original notification body
        frontmatter: Original frontmatter

    Returns:
        Formatted task as markdown string
    """
    notification_type = linkedin_data['type'].title()
    author = linkedin_data['author']

    # Generate profile summary
    profile_summary = extract_profile_summary(body, frontmatter)

    # Determine task title based on type
    if linkedin_data['type'].lower() == 'lead':
        task_title = f"LinkedIn Lead: {author}"
        action_context = "This is a potential business opportunity. Review the lead's profile and context to determine the best engagement strategy."
    elif linkedin_data['type'].lower() == 'comment':
        task_title = f"LinkedIn Comment: {author}"
        action_context = "This user has commented on your content. Review the comment and their profile to craft an appropriate response."
    elif linkedin_data['type'].lower() == 'dm':
        task_title = f"LinkedIn DM: {author}"
        action_context = "Direct message requiring response. Review the message and sender's profile."
    elif linkedin_data['type'].lower() == 'mention':
        task_title = f"LinkedIn Mention: {author}"
        action_context = "You've been mentioned in a post or comment. Review and decide if response is needed."
    else:
        task_title = f"LinkedIn {notification_type}: {author}"
        action_context = "Review this LinkedIn notification and determine appropriate action."

    template = f"""---
source: linkedin
type: linkedin_{linkedin_data['type'].lower()}
priority: high
received: {linkedin_data['received']}
status: pending
created_from: {original_file}
author: {linkedin_data['author']}
author_url: {linkedin_data['author_url']}
connection_level: {linkedin_data['connection_level']}
context_url: {linkedin_data['context_url']}
---

# {task_title}

## 🔴 High Priority - LinkedIn Engagement

{action_context}

{profile_summary}

## Notification Details

- **Type**: {notification_type}
- **From**: {linkedin_data['author']}
- **Profile**: {linkedin_data['author_url'] if linkedin_data['author_url'] else 'Not provided'}
- **Connection Level**: {linkedin_data['connection_level']}
- **Context**: {linkedin_data['context_url'] if linkedin_data['context_url'] else 'Not provided'}
- **Received**: {linkedin_data['received']}
- **Original File**: [{original_file}](./../Inbox/{original_file})

## Content

{linkedin_data['body']}

## Recommended Actions

Based on the notification type and profile:

- [ ] Review {author}'s LinkedIn profile in detail
- [ ] Assess engagement opportunity and potential value
- [ ] Draft appropriate response or engagement strategy
- [ ] Determine if this requires immediate action or can be scheduled
- [ ] Check for any relevant context from previous interactions

## Response Strategy

**Tone**: [Professional / Friendly / Consultative]
**Approach**: [Direct response / Schedule call / Share resource / Other]

### Draft Response

[Placeholder for response content - to be filled during planning phase]

## Profile Research Notes

[Space for notes about the user's background, company, interests, and potential synergies]

## Follow-up Actions

- [ ] Connect on LinkedIn (if not already connected)
- [ ] Review their recent posts and activity
- [ ] Check for mutual connections
- [ ] Research their company/role
- [ ] Prepare personalized response

---

*Task generated from LinkedIn notification on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return template


def process_linkedin_file(file_path: Path, vault_path: Path) -> bool:
    """
    Process a single LinkedIn notification file.

    Args:
        file_path: Path to LinkedIn notification file
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
            print(f"  ⏭️  Skipping (already processed): {file_path.name}")
            return False

        # Verify it's a LinkedIn source
        if frontmatter.get('source') != 'linkedin':
            print(f"  ⏭️  Skipping (not LinkedIn source): {file_path.name}")
            return False

        # Get notification type
        notification_type = frontmatter.get('type', 'unknown')

        # Check if this type should be processed
        if not should_process_notification(notification_type):
            print(f"  ⏭️  Skipping (type '{notification_type}' not configured for processing): {file_path.name}")
            return False

        # Extract LinkedIn data
        linkedin_data = extract_linkedin_data(frontmatter, body)

        # Validate required fields
        if not linkedin_data['author']:
            print(f"  ⚠️  Skipping (missing author): {file_path.name}")
            return False

        # Generate task
        task_content = generate_task_from_linkedin(linkedin_data, file_path.name, body, frontmatter)

        # Create task filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        type_slug = sanitize_filename(notification_type)
        author_slug = sanitize_filename(linkedin_data['author'])
        task_filename = f"{date_str}_linkedin_{type_slug}_{author_slug}.md"

        # Ensure Inbox folder exists
        inbox_path = vault_path / 'Inbox'
        inbox_path.mkdir(exist_ok=True)

        # Save task file
        task_path = inbox_path / task_filename
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
        print(f"  ✅ Processed: {file_path.name}")
        print(f"     Type: {notification_type.title()}")
        print(f"     From: {linkedin_data['author']}")
        print(f"     Priority: HIGH")
        print(f"     Task created: {task_filename}")

        return True

    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")
        return False


def ingest_linkedin_notifications(vault_path: Path, source_folder: str = 'Inbox') -> Dict[str, int]:
    """
    Process all LinkedIn notification files.

    Args:
        vault_path: Path to vault directory
        source_folder: Folder to scan for LinkedIn notifications

    Returns:
        Dictionary with processing statistics
    """
    source_path = vault_path / source_folder

    if not source_path.exists():
        print(f"❌ Source folder not found: {source_path}")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    # Find all markdown files
    md_files = list(source_path.glob('*.md'))

    if not md_files:
        print(f"📭 No markdown files found in {source_folder}")
        return {'processed': 0, 'skipped': 0, 'errors': 0}

    print(f"\n📥 LinkedIn Ingest - Processing {len(md_files)} files from {source_folder}\n")

    stats = {'processed': 0, 'skipped': 0, 'errors': 0}

    for file_path in md_files:
        result = process_linkedin_file(file_path, vault_path)
        if result:
            stats['processed'] += 1
        else:
            stats['skipped'] += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"LinkedIn Ingest Summary")
    print(f"{'='*60}")
    print(f"✅ Processed: {stats['processed']} (High-priority tasks created)")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"❌ Errors: {stats['errors']}")
    print(f"{'='*60}\n")

    if stats['processed'] > 0:
        print(f"🔴 {stats['processed']} high-priority LinkedIn tasks created in /Inbox")
        print(f"   Review these tasks promptly for engagement opportunities.\n")

    return stats


def main():
    """Main entry point for LinkedIn ingest script."""
    # Get vault path from command line or use current directory
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    # Validate vault path
    if not vault_path.exists():
        print(f"❌ Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    print(f"🔍 LinkedIn Ingest - Vault: {vault_path.absolute()}")

    # Process LinkedIn notifications
    stats = ingest_linkedin_notifications(vault_path)

    # Exit with appropriate code
    if stats['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
