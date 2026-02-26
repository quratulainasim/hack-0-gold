#!/usr/bin/env python3
"""
Facebook Simple Capture

Opens Facebook, waits 45 seconds for you to navigate to notifications,
then automatically reads and captures notifications with priority keywords.
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

def create_inbox_file(notification_data: Dict[str, str], vault_path: Path) -> bool:
    """Create inbox file for notification."""
    try:
        inbox_path = vault_path / "Needs_Action"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        author_safe = sanitize_filename(notification_data['author'])
        content_safe = sanitize_filename(notification_data['content'][:30])
        filename = f"FB_{timestamp}_{author_safe}_{content_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(notification_data['content'])
        keywords_str = ', '.join(matched_keywords)

        content = f"""---
type: facebook
priority: high
status: pending
timestamp: {notification_data['timestamp']}
source: facebook
author: {notification_data['author']}
keywords: {keywords_str}
---

# Facebook Priority Notification from {notification_data['author']}

**Received**: {notification_data['timestamp']}
**Priority**: HIGH
**Keywords Matched**: {keywords_str}

---

## Notification Content

{notification_data['content']}

---

## Context

This notification was flagged as high priority because it contains urgent keywords: **{keywords_str}**

**Author**: {notification_data['author']}
**Source**: Facebook
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review notification content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Follow up with author

---

*Captured by Facebook Simple Capture on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create file: {e}")
        return False

def load_processed_notifications(vault_path: Path) -> set:
    """Load processed notification IDs."""
    processed_file = vault_path / ".facebook_processed.json"
    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        except:
            return set()
    return set()

def save_processed_notifications(vault_path: Path, processed: set):
    """Save processed notification IDs."""
    processed_file = vault_path / ".facebook_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def capture_notifications():
    """Capture Facebook notifications."""

    print("="*60)
    print("Facebook Simple Capture")
    print("="*60)
    print()

    vault_path = Path.cwd().parent if Path.cwd().name == 'watchers' else Path.cwd()
    session_path = vault_path / '.fb_browser_data'
    processed = load_processed_notifications(vault_path)
    stats = {'captured': 0, 'skipped': 0}

    with sync_playwright() as p:
        print("[1/4] Launching browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[2/4] Navigating to Facebook Messenger...")
        page.goto('https://www.facebook.com/messages', wait_until='domcontentloaded')

        print("[3/4] Waiting for Messenger to load...")
        time.sleep(5)  # Give page time to load
        print("      [OK] Messenger page loaded")

        print()
        print("="*60)
        print("ACTION REQUIRED IN BROWSER")
        print("="*60)
        print()
        print("You have 45 SECONDS to:")
        print("1. Make sure you're logged in")
        print("2. Click on a conversation to open it")
        print("3. The script will automatically capture messages with keywords")
        print()
        print("The script will automatically continue after 45 seconds...")
        print()

        # Countdown
        for i in range(45, 0, -5):
            print(f"  {i} seconds remaining...")
            time.sleep(5)

        print()
        print("[4/4] Reading messenger messages...")
        print()

        notifications = []

        try:
            # Try multiple selectors for Facebook Messenger messages
            selectors = [
                'div[role="row"]',  # Message rows
                'div[data-scope="messages_table"]',  # Message container
                'div.x1n2onr6',  # Message bubbles
                'div[dir="auto"]',  # Text containers
            ]

            message_elements = []
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    message_elements = elements
                    print(f"  Found {len(elements)} message element(s) using: {selector}")
                    break

            if not message_elements:
                # Fallback: get all visible text from the conversation
                print("  Using fallback: reading all visible text from conversation")
                try:
                    # Try to get the main conversation area
                    conversation_area = page.query_selector('[role="main"]')
                    if conversation_area:
                        body_text = conversation_area.inner_text()
                    else:
                        body_text = page.inner_text('body')

                    if body_text and contains_priority_keywords(body_text):
                        # Split into lines and look for messages
                        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
                        for line in lines:
                            if contains_priority_keywords(line) and len(line) > 10:
                                # Try to identify sender (usually first word or phrase)
                                author = 'Facebook User'

                                notif_id = f"{author}_{line[:50]}_{len(line)}"
                                if notif_id not in processed:
                                    notifications.append({
                                        'author': author,
                                        'content': line,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    processed.add(notif_id)
                                    print(f"  [MATCH] Found: {line[:50]}...")
                except Exception as e:
                    print(f"  [ERROR] Fallback failed: {e}")
            else:
                # Process found message elements
                for msg_elem in message_elements[-20:]:  # Last 20 messages
                    try:
                        text = msg_elem.inner_text()

                        if text and contains_priority_keywords(text):
                            # Try to extract sender name
                            lines = text.split('\n')
                            author = lines[0] if lines and len(lines[0]) < 50 else 'Facebook User'

                            notif_id = f"{author}_{text[:50]}_{len(text)}"

                            if notif_id not in processed:
                                notifications.append({
                                    'author': author,
                                    'content': text,
                                    'timestamp': datetime.now().isoformat()
                                })
                                processed.add(notif_id)
                                print(f"  [MATCH] Found: {text[:50]}...")
                    except:
                        continue

        except Exception as e:
            print(f"  [ERROR] Error reading messages: {e}")

        print()
        print(f"  Total priority notifications found: {len(notifications)}")
        print()

        # Create inbox files
        if notifications:
            print("Creating inbox files...")
            for notif in notifications:
                if create_inbox_file(notif, vault_path):
                    stats['captured'] += 1

            save_processed_notifications(vault_path, processed)
        else:
            print("[INFO] No new priority notifications found")

        print()
        print("Waiting 10 seconds before closing browser...")
        time.sleep(10)

        context.close()

    return stats

def main():
    """Main entry point."""
    stats = capture_notifications()

    print()
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"[OK] Captured: {stats['captured']}")
    print(f"[SKIP] Skipped: {stats['skipped']}")
    print("="*60)

    if stats['captured'] > 0:
        print()
        print(f"[INFO] {stats['captured']} notification(s) added to /Needs_Action")
        print("[INFO] Check Needs_Action/ folder for captured notifications")

if __name__ == "__main__":
    main()
