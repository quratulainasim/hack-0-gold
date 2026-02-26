#!/usr/bin/env python3
"""
Inbox Triage Script

This script triages markdown files in /Inbox and /Needs_Action folders by:
1. Scanning for new .md files
2. Parsing frontmatter (type, priority, received date)
3. Summarizing content and updating status to 'processing'
4. For /Needs_Action files, proposing a 1-step plan based on Company_Handbook.md

Usage:
    python triage_inbox.py [vault_path]

    If vault_path is not provided, uses current working directory.
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    # Check if content starts with frontmatter delimiter
    if not content.startswith('---'):
        return None, content

    # Find the closing delimiter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    # Parse frontmatter as simple key-value pairs
    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def update_frontmatter(content: str, updates: Dict) -> str:
    """
    Update frontmatter fields in markdown content.

    Args:
        content: Original markdown content
        updates: Dictionary of fields to update

    Returns:
        Updated markdown content
    """
    frontmatter, body = parse_frontmatter(content)

    if frontmatter is None:
        # No frontmatter exists, create it
        frontmatter = updates
    else:
        # Update existing frontmatter
        frontmatter.update(updates)

    # Rebuild the content
    frontmatter_lines = ['---']
    for key, value in frontmatter.items():
        frontmatter_lines.append(f'{key}: {value}')
    frontmatter_lines.append('---')

    return '\n'.join(frontmatter_lines) + '\n\n' + body


def summarize_content(body: str, max_length: int = 200) -> str:
    """
    Create a brief summary of the content.

    Args:
        body: The markdown body content
        max_length: Maximum length of summary

    Returns:
        Summary string
    """
    # Remove markdown formatting for summary
    clean_text = re.sub(r'[#*`\[\]()]', '', body)
    clean_text = ' '.join(clean_text.split())

    if len(clean_text) <= max_length:
        return clean_text

    return clean_text[:max_length].rsplit(' ', 1)[0] + '...'


def read_company_handbook(vault_path: Path) -> Optional[str]:
    """
    Read the Company_Handbook.md file.

    Returns:
        Handbook content or None if not found
    """
    handbook_path = vault_path / 'Company_Handbook.md'

    if not handbook_path.exists():
        return None

    try:
        with open(handbook_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Company_Handbook.md: {e}")
        return None


def triage_inbox(vault_path: Optional[str] = None) -> Dict:
    """
    Triage markdown files in Inbox and Needs_Action folders.

    Args:
        vault_path: Path to vault directory (defaults to current directory)

    Returns:
        Dictionary with triage results
    """
    # Use current directory if no path provided
    if vault_path is None:
        vault_path = Path.cwd()
    else:
        vault_path = Path(vault_path).resolve()

    print(f"Triaging inbox at: {vault_path}")
    print()

    # Define folders to scan
    folders_to_scan = ['Inbox', 'Needs_Action']

    results = {
        'success': True,
        'files_processed': [],
        'files_skipped': [],
        'errors': [],
        'handbook_loaded': False,
        'handbook_content': None
    }

    # Read Company Handbook
    print("Loading Company_Handbook.md...")
    handbook_content = read_company_handbook(vault_path)

    if handbook_content:
        results['handbook_loaded'] = True
        results['handbook_content'] = handbook_content
        print(f"  [OK] Loaded Company_Handbook.md ({len(handbook_content)} characters)")
    else:
        print("  [WARNING] Company_Handbook.md not found - plans will be generic")

    print()

    # Scan each folder
    for folder_name in folders_to_scan:
        folder_path = vault_path / folder_name

        if not folder_path.exists():
            print(f"[SKIP] {folder_name}/ does not exist")
            continue

        print(f"Scanning {folder_name}/...")
        print("-" * 60)

        # Find all .md files
        md_files = list(folder_path.glob('*.md'))

        if not md_files:
            print(f"  No .md files found in {folder_name}/")
            print()
            continue

        for md_file in md_files:
            try:
                # Read file content
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter
                frontmatter, body = parse_frontmatter(content)

                # Check if already processed
                if frontmatter and frontmatter.get('status') == 'processing':
                    print(f"  [SKIP] {md_file.name} - already processing")
                    results['files_skipped'].append(str(md_file))
                    continue

                # Extract metadata
                file_type = frontmatter.get('type', 'unknown') if frontmatter else 'unknown'
                priority = frontmatter.get('priority', 'normal') if frontmatter else 'normal'
                received_date = frontmatter.get('received', 'unknown') if frontmatter else 'unknown'

                # Summarize content
                summary = summarize_content(body)

                print(f"\n  File: {md_file.name}")
                print(f"    Type: {file_type}")
                print(f"    Priority: {priority}")
                print(f"    Received: {received_date}")
                print(f"    Summary: {summary}")

                # Update status to 'processing'
                updates = {
                    'status': 'processing',
                    'triaged_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                updated_content = update_frontmatter(content, updates)

                # Write updated content back
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                print(f"    [UPDATED] Status set to 'processing'")

                # If in Needs_Action, propose a plan
                if folder_name == 'Needs_Action':
                    print(f"\n    [NEEDS ACTION] Proposing 1-step plan...")

                    if handbook_content:
                        print(f"    Based on Company_Handbook.md guidelines:")
                        print(f"    Plan: Review the {file_type} item (priority: {priority})")
                        print(f"          and take action according to handbook procedures.")
                    else:
                        print(f"    Plan: Review and process this {file_type} item")
                        print(f"          with priority: {priority}")

                results['files_processed'].append({
                    'file': str(md_file),
                    'type': file_type,
                    'priority': priority,
                    'received': received_date,
                    'summary': summary,
                    'folder': folder_name
                })

            except Exception as e:
                error_msg = f"Error processing {md_file.name}: {e}"
                print(f"  [ERROR] {error_msg}")
                results['errors'].append(error_msg)
                results['success'] = False

        print()

    # Summary
    print("=" * 60)
    print("TRIAGE SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(results['files_processed'])}")
    print(f"Files skipped: {len(results['files_skipped'])}")

    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

    print()

    if results['files_processed']:
        print("Processed files:")
        for file_info in results['files_processed']:
            print(f"  - {Path(file_info['file']).name} ({file_info['type']}, {file_info['priority']})")

    print()

    if results['success'] and results['files_processed']:
        print("[SUCCESS] Triage complete!")
    elif not results['files_processed']:
        print("[INFO] No files to triage")
    else:
        print("[PARTIAL] Triage completed with errors")

    return results


def main():
    """Main entry point for the script."""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else None

    results = triage_inbox(vault_path)

    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
