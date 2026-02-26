#!/usr/bin/env python3
"""
Instagram Simple Capture

Opens Instagram, waits 45 seconds for you to navigate to DMs,
then automatically reads and captures messages with priority keywords.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[ERROR] Playwright not installed")
    sys.exit(1)

# Priority keywords
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'lead', 'meeting', 'deadline', 'important', 'critical', 'client']

def sanitize_filename(text: str) -> str:
    """Sanitize text for filename."""
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50].lower()

def contains_priority_keywords(text: str) -> bool:
    """Check if text contains priority keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PRIORITY_KEYWORDS)

def extract_matched_keywords(text: str) -> List[str]:
    """Extract matched keywords."""
    text_lower = text.lower()
    return [keyword for keyword in PRIORITY_KEYWORDS if keyword in text_lower]

def create_inbox_file(message_data: Dict[str, str], vault_path: Path) -> bool:
    """Create inbox file for message."""
    try:
        inbox_path = vault_path / "Needs_Action"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        author_safe = sanitize_filename(message_data['author'])
        content_safe = sanitize_filename(message_data['content'][:30])
        filename = f"IG_{timestamp}_{author_safe}_{content_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(message_data['content'])
        keywords_str = ', '.join(matched_keywords)

        content = f"""---
type: instagram
priority: high
status: pending
timestamp: {message_data['timestamp']}
source: instagram
author: {message_data['author']}
keywords: {keywords_str}
---

# Instagram Priority Message from {message_data['author']}

**From**: {message_data['author']}
**Received**: {message_data['timestamp']}
**Priority**: HIGH
**Keywords Matched**: {keywords_str}

---

## Message Content

{message_data['content']}

---

## Context

This message was flagged as high priority because it contains urgent keywords: **{keywords_str}**

**Author**: {message_data['author']}
**Source**: Instagram DM
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Reply if needed
- [ ] Follow up with author

---

*Captured by Instagram Simple Capture on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create file: {e}")
        return False

def load_processed_messages(vault_path: Path) -> set:
    """Load processed message IDs."""
    processed_file = vault_path / ".instagram_processed.json"
    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        except:
            return set()
    return set()

def save_processed_messages(vault_path: Path, processed: set):
    """Save processed message IDs."""
    processed_file = vault_path / ".instagram_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def capture_messages():
    """Capture Instagram DMs."""

    print("="*60)
    print("Instagram Simple Capture")
    print("="*60)
    print()

    vault_path = Path.cwd().parent if Path.cwd().name == 'watchers' else Path.cwd()
    session_path = vault_path / '.instagram_browser_data'
    processed = load_processed_messages(vault_path)
    stats = {'captured': 0, 'skipped': 0}

    with sync_playwright() as p:
        print("[1/4] Launching browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[2/4] Navigating to Instagram DMs...")
        page.goto('https://www.instagram.com/direct/inbox/', wait_until='domcontentloaded')

        print("[3/4] Waiting for Instagram to load...")
        time.sleep(5)  # Give page time to load
        print("      [OK] Instagram page loaded")

        print()
        print("="*60)
        print("ACTION REQUIRED IN BROWSER")
        print("="*60)
        print()
        print("You have 45 SECONDS to:")
        print("1. Make sure you're logged in")
        print("2. Click on a DM thread to open it")
        print("3. Make sure messages are visible")
        print()
        print("The script will automatically continue after 45 seconds...")
        print()

        # Countdown
        for i in range(45, 0, -5):
            print(f"  {i} seconds remaining...")
            time.sleep(5)

        print()
        print("[4/4] Reading messages from open thread...")
        print()

        messages = []

        try:
            # Get sender name
            author = "Unknown"
            try:
                author_elem = page.query_selector('header a')
                if author_elem:
                    author = author_elem.inner_text()
            except:
                pass

            print(f"  Thread with: {author}")

            # Try multiple selectors for Instagram messages
            selectors = [
                '[role="row"]',  # Standard message rows
                'div[class*="x1n2onr6"]',  # Message containers
                'div[dir="auto"]',  # Text containers
            ]

            message_elements = []
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    message_elements = elements
                    print(f"  Found {len(elements)} message(s) using: {selector}")
                    break

            if not message_elements:
                # Fallback: get all visible text
                print("  Using fallback: reading all visible text")
                try:
                    body_text = page.inner_text('body')
                    if body_text and contains_priority_keywords(body_text):
                        paragraphs = [p.strip() for p in body_text.split('\n') if p.strip()]
                        for para in paragraphs:
                            if contains_priority_keywords(para) and len(para) > 10:
                                msg_id = f"{author}_{para[:50]}_{len(para)}"
                                if msg_id not in processed:
                                    messages.append({
                                        'author': author,
                                        'content': para,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    processed.add(msg_id)
                                    print(f"  [MATCH] Found: {para[:50]}...")
                except Exception as e:
                    print(f"  [ERROR] Fallback failed: {e}")
            else:
                # Process found messages
                for msg_elem in message_elements[-20:]:  # Last 20 messages
                    try:
                        text = msg_elem.inner_text()

                        if text and contains_priority_keywords(text):
                            msg_id = f"{author}_{text[:50]}_{len(text)}"

                            if msg_id not in processed:
                                messages.append({
                                    'author': author,
                                    'content': text,
                                    'timestamp': datetime.now().isoformat()
                                })
                                processed.add(msg_id)
                                print(f"  [MATCH] Found: {text[:50]}...")
                    except:
                        continue

        except Exception as e:
            print(f"  [ERROR] Error reading messages: {e}")

        print()
        print(f"  Total priority messages found: {len(messages)}")
        print()

        # Create inbox files
        if messages:
            print("Creating inbox files...")
            for msg in messages:
                if create_inbox_file(msg, vault_path):
                    stats['captured'] += 1

            save_processed_messages(vault_path, processed)
        else:
            print("[INFO] No new priority messages found")

        print()
        print("Waiting 10 seconds before closing browser...")
        time.sleep(10)

        context.close()

    return stats

def main():
    """Main entry point."""
    stats = capture_messages()

    print()
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"[OK] Captured: {stats['captured']}")
    print(f"[SKIP] Skipped: {stats['skipped']}")
    print("="*60)

    if stats['captured'] > 0:
        print()
        print(f"[INFO] {stats['captured']} message(s) added to /Needs_Action")
        print("[INFO] Check Needs_Action/ folder for captured messages")

if __name__ == "__main__":
    main()
