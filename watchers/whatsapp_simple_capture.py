#!/usr/bin/env python3
"""
WhatsApp Simple Capture

Opens WhatsApp Web, waits 45 seconds for you to open a chat,
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
        inbox_path = vault_path / "Inbox"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        sender_safe = sanitize_filename(message_data['sender'])
        filename = f"WA_{timestamp}_{sender_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(message_data['message'])
        keywords_str = ', '.join(matched_keywords)

        content = f"""---
type: whatsapp
priority: high
status: pending
timestamp: {message_data['timestamp']}
source: whatsapp
sender: {message_data['sender']}
keywords: {keywords_str}
chat_type: {message_data.get('chat_type', 'individual')}
---

# WhatsApp Priority Message from {message_data['sender']}

**Received**: {message_data['timestamp']}
**Priority**: HIGH
**Keywords Matched**: {keywords_str}
**Chat Type**: {message_data.get('chat_type', 'individual').title()}

---

## Message Content

{message_data['message']}

---

## Context

This message was flagged as high priority because it contains urgent keywords: **{keywords_str}**

**Sender**: {message_data['sender']}
**Source**: WhatsApp Web
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Follow up with sender

---

*Captured by WhatsApp Simple Capture on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
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
    processed_file = vault_path / ".whatsapp_processed.json"
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
    processed_file = vault_path / ".whatsapp_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def capture_messages():
    """Capture WhatsApp messages."""

    print("="*60)
    print("WhatsApp Simple Capture")
    print("="*60)
    print()

    vault_path = Path.cwd()
    session_path = vault_path / '.whatsapp_browser_data'
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

        print("[2/4] Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')

        print("[3/4] Waiting for WhatsApp to load...")
        try:
            page.wait_for_selector('#pane-side', timeout=120000)
            print("      [OK] WhatsApp Web loaded")
        except:
            print("      [ERROR] Timeout")
            context.close()
            return stats

        print()
        print("="*60)
        print("ACTION REQUIRED IN BROWSER")
        print("="*60)
        print()
        print("You have 45 SECONDS to:")
        print("1. Find the chat with your urgent message")
        print("2. Click on it to open the chat")
        print("3. Make sure messages are visible")
        print()
        print("The script will automatically continue after 45 seconds...")
        print()

        # Countdown
        for i in range(45, 0, -5):
            print(f"  {i} seconds remaining...")
            time.sleep(5)

        print()
        print("[4/4] Reading messages from open chat...")
        print()

        messages = []

        try:
            # Get sender name
            sender = "Unknown"
            sender_selectors = [
                'header span[title]',
                'header span[dir="auto"]',
                'header div[role="button"] span',
            ]

            for selector in sender_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        text = elem.inner_text()
                        if text and len(text) > 0:
                            sender = text
                            break
                except:
                    continue

            print(f"  Chat with: {sender}")

            # Try multiple message selectors
            message_selectors = [
                'div[data-testid="msg-container"]',
                'div.message-in',
                'div.message-out',
                'div[class*="message"]',
            ]

            message_elements = []
            for selector in message_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if len(elements) > 0:
                        message_elements = elements
                        print(f"  Found {len(elements)} messages using: {selector}")
                        break
                except:
                    continue

            if not message_elements:
                print("  [ERROR] No messages found with any selector")
                print("  [INFO] Trying alternative approach...")

                # Try to get all text content
                try:
                    all_text = page.query_selector_all('span.selectable-text')
                    print(f"  Found {len(all_text)} text elements")

                    for elem in all_text[-10:]:  # Last 10 text elements
                        try:
                            text = elem.inner_text()
                            if text and contains_priority_keywords(text):
                                message_id = f"{sender}_{text[:50]}_{len(text)}"
                                if message_id not in processed:
                                    messages.append({
                                        'sender': sender,
                                        'message': text,
                                        'timestamp': datetime.now().isoformat(),
                                        'chat_type': 'individual',
                                        'message_id': message_id
                                    })
                                    processed.add(message_id)
                                    print(f"  [MATCH] Found: {text[:50]}...")
                        except:
                            continue
                except Exception as e:
                    print(f"  [ERROR] Alternative approach failed: {e}")

            else:
                # Process messages
                recent = message_elements[-20:] if len(message_elements) > 20 else message_elements

                for msg_elem in recent:
                    try:
                        # Try to get text
                        text = None
                        text_elem = msg_elem.query_selector('span.selectable-text')
                        if text_elem:
                            text = text_elem.inner_text()

                        if not text:
                            text = msg_elem.inner_text()

                        if text and contains_priority_keywords(text):
                            message_id = f"{sender}_{text[:50]}_{len(text)}"
                            if message_id not in processed:
                                messages.append({
                                    'sender': sender,
                                    'message': text,
                                    'timestamp': datetime.now().isoformat(),
                                    'chat_type': 'individual',
                                    'message_id': message_id
                                })
                                processed.add(message_id)
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
        print(f"[INFO] {stats['captured']} message(s) added to /Inbox")
        print("[INFO] Check Inbox/ folder for captured messages")

if __name__ == "__main__":
    main()
