#!/usr/bin/env python3
"""
Triage Inbox Script
Processes markdown files in Inbox and Needs_Action folders.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

def parse_frontmatter(content: str) -> tuple[Dict[str, str], str]:
    """Parse frontmatter from markdown content."""
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()

            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

    return frontmatter, body

def update_frontmatter(content: str, updates: Dict[str, str]) -> str:
    """Update frontmatter in markdown content."""
    if not content.startswith('---'):
        # No frontmatter, add it
        fm_lines = ['---']
        for key, value in updates.items():
            fm_lines.append(f'{key}: {value}')
        fm_lines.append('---')
        return '\n'.join(fm_lines) + '\n\n' + content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return content

    fm_text = parts[1].strip()
    body = parts[2]

    # Parse existing frontmatter
    fm_dict = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()

    # Apply updates
    fm_dict.update(updates)

    # Rebuild frontmatter
    fm_lines = ['---']
    for key, value in fm_dict.items():
        fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')

    return '\n'.join(fm_lines) + body

def summarize_content(text: str, max_length: int = 200) -> str:
    """Create a brief summary of content."""
    # Remove markdown formatting
    text = re.sub(r'#+ ', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Clean whitespace
    text = ' '.join(text.split())

    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + '...'

    return text

def triage_file(filepath: Path, folder_name: str) -> bool:
    """Triage a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        # Skip if already processing
        if frontmatter.get('status') == 'processing':
            print(f"  [SKIP] {filepath.name} - already processing")
            return False

        # Extract metadata
        file_type = frontmatter.get('type', 'unknown')
        priority = frontmatter.get('priority', 'medium')
        received = frontmatter.get('received', 'unknown')

        # Create summary
        summary = summarize_content(body)

        # Update status
        updates = {
            'status': 'processing',
            'triaged_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        new_content = update_frontmatter(content, updates)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  [OK] {filepath.name}")
        print(f"       Type: {file_type} | Priority: {priority}")
        print(f"       Summary: {summary}")

        # Move to Needs_Action if in Inbox
        if folder_name == 'Inbox':
            needs_action_path = filepath.parent.parent / 'Needs_Action' / filepath.name
            needs_action_path.parent.mkdir(exist_ok=True)
            filepath.rename(needs_action_path)
            print(f"       Moved to: Needs_Action/")

        return True

    except Exception as e:
        print(f"  [ERROR] {filepath.name}: {e}")
        return False

def main():
    """Main entry point."""
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("="*60)
    print("Triage Inbox")
    print("="*60)
    print(f"Vault: {vault_path.absolute()}")
    print()

    # Check for Company Handbook
    handbook_path = vault_path / 'Company_Handbook.md'
    if handbook_path.exists():
        print("[OK] Company Handbook found")
    else:
        print("[WARN] Company Handbook not found")
    print()

    # Process Inbox
    inbox_path = vault_path / 'Inbox'
    if inbox_path.exists():
        print("Processing Inbox...")
        files = list(inbox_path.glob('*.md'))
        if files:
            for filepath in files:
                triage_file(filepath, 'Inbox')
        else:
            print("  [INFO] No files in Inbox")
        print()

    # Process Needs_Action
    needs_action_path = vault_path / 'Needs_Action'
    if needs_action_path.exists():
        print("Processing Needs_Action...")
        files = list(needs_action_path.glob('*.md'))
        if files:
            for filepath in files:
                triage_file(filepath, 'Needs_Action')
        else:
            print("  [INFO] No files in Needs_Action")
        print()

    print("="*60)
    print("Triage Complete")
    print("="*60)

if __name__ == '__main__':
    main()
