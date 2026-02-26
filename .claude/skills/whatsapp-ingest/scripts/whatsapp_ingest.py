#!/usr/bin/env python3
"""
WhatsApp Ingest Script

Uses Playwright to access WhatsApp Web and extract urgent messages
containing priority keywords, creating structured markdown files in /Inbox.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("[ERROR] Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


# Priority keywords to search for
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help']


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


def contains_priority_keywords(text: str) -> bool:
    """
    Check if text contains any priority keywords.

    Args:
        text: Text to check

    Returns:
        True if contains priority keywords, False otherwise
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PRIORITY_KEYWORDS)


def extract_matched_keywords(text: str) -> List[str]:
    """
    Extract which priority keywords are present in text.

    Args:
        text: Text to check

    Returns:
        List of matched keywords
    """
    text_lower = text.lower()
    return [keyword for keyword in PRIORITY_KEYWORDS if keyword in text_lower]


def create_inbox_file(message_data: Dict[str, str], vault_path: Path) -> bool:
    """
    Create a structured markdown file in /Inbox for the WhatsApp message.

    Args:
        message_data: Dictionary containing message metadata
        vault_path: Path to the Obsidian vault

    Returns:
        True if file created successfully, False otherwise
    """
    try:
        inbox_path = vault_path / "Inbox"
        inbox_path.mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        sender_safe = sanitize_filename(message_data['sender'])
        filename = f"WA_{timestamp}_{sender_safe}.md"
        filepath = inbox_path / filename

        # Get matched keywords
        matched_keywords = extract_matched_keywords(message_data['message'])
        keywords_str = ', '.join(matched_keywords)

        # Create markdown content with frontmatter
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

"""

        # Add keyword-specific actions
        if 'payment' in matched_keywords or 'invoice' in matched_keywords:
            content += """- [ ] Review payment/invoice details
- [ ] Verify transaction information
- [ ] Process payment or send invoice
- [ ] Confirm with sender
"""
        elif 'urgent' in matched_keywords or 'asap' in matched_keywords:
            content += """- [ ] Assess urgency level
- [ ] Respond immediately
- [ ] Take necessary action
- [ ] Follow up to confirm resolution
"""
        elif 'help' in matched_keywords:
            content += """- [ ] Understand the help request
- [ ] Provide assistance or guidance
- [ ] Escalate if necessary
- [ ] Confirm issue resolved
"""
        else:
            content += """- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Follow up with sender
"""

        content += f"""
---

*Captured by whatsapp-ingest skill on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create inbox file: {e}")
        return False


def load_processed_messages(vault_path: Path) -> set:
    """
    Load the set of already processed message IDs.

    Args:
        vault_path: Path to the Obsidian vault

    Returns:
        Set of processed message IDs
    """
    processed_file = vault_path / ".whatsapp_processed.json"

    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        except Exception as e:
            print(f"  [WARN] Could not load processed messages: {e}")
            return set()

    return set()


def save_processed_messages(vault_path: Path, processed: set):
    """
    Save the set of processed message IDs.

    Args:
        vault_path: Path to the Obsidian vault
        processed: Set of processed message IDs
    """
    processed_file = vault_path / ".whatsapp_processed.json"

    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save processed messages: {e}")


def extract_priority_messages(page, processed: set) -> List[Dict[str, str]]:
    """
    Extract unread messages containing priority keywords from WhatsApp Web.

    Args:
        page: Playwright page object
        processed: Set of already processed message IDs

    Returns:
        List of message dictionaries
    """
    messages = []

    try:
        # Wait for chat list to load with increased timeout (2 minutes)
        page.wait_for_selector('#pane-side', timeout=120000)
        print("  [INFO] WhatsApp Web loaded successfully")
        print("")
        print("="*60)
        print("MANUAL INTERACTION REQUIRED")
        print("="*60)
        print("")
        print("Please do the following in the WhatsApp Web browser:")
        print("1. Find the chat with your urgent message")
        print("2. Click on it to open the chat")
        print("3. Make sure you can see the messages")
        print("4. Leave the chat open")
        print("")
        print("Press Enter here when ready to continue...")
        input()
        print("")
        print("  [INFO] Continuing with message detection...")

        # Find all chats with unread messages
        unread_chats = page.query_selector_all('div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])')

        print(f"  [INFO] Found {len(unread_chats)} chat(s) with unread messages")

        for idx, chat in enumerate(unread_chats[:20], 1):  # Limit to 20 most recent
            try:
                # Click on the chat to open it
                chat.click()
                page.wait_for_timeout(1500)  # Wait for chat to load

                # Get sender name from header
                sender_elem = page.query_selector('header span[data-testid="conversation-info-header-chat-title"]')
                sender = sender_elem.inner_text() if sender_elem else "Unknown"

                # Get chat type (group or individual)
                is_group = page.query_selector('header span[data-testid="default-group"]') is not None
                chat_type = "group" if is_group else "individual"

                # Get all messages in the chat
                message_elements = page.query_selector_all('div[data-testid="msg-container"]')

                # Get unread count
                unread_badge = chat.query_selector('span[data-testid="icon-unread-count"]')
                unread_count = int(unread_badge.inner_text()) if unread_badge and unread_badge.inner_text().isdigit() else 5

                # Process recent messages (likely unread)
                recent_messages = message_elements[-unread_count:] if len(message_elements) >= unread_count else message_elements

                for msg_elem in recent_messages:
                    try:
                        # Get message text
                        text_elem = msg_elem.query_selector('span.selectable-text')
                        if not text_elem:
                            continue

                        message_text = text_elem.inner_text()

                        # Check if message contains priority keywords
                        if not contains_priority_keywords(message_text):
                            continue

                        # Create unique message ID
                        message_id = f"{sender}_{message_text[:50]}_{len(message_text)}"

                        # Skip if already processed
                        if message_id in processed:
                            continue

                        # Get timestamp
                        timestamp = datetime.now().isoformat()

                        messages.append({
                            'sender': sender,
                            'message': message_text,
                            'timestamp': timestamp,
                            'chat_type': chat_type,
                            'message_id': message_id
                        })

                        processed.add(message_id)
                        print(f"  [MATCH] Found priority message from {sender}")

                    except Exception as e:
                        print(f"  [WARN] Error processing message: {e}")
                        continue

            except Exception as e:
                print(f"  [WARN] Error processing chat {idx}: {e}")
                continue

    except PlaywrightTimeout:
        print("  [ERROR] Timeout waiting for WhatsApp Web to load")
        print("  [ERROR] Please ensure you're logged in to WhatsApp Web")
    except Exception as e:
        print(f"  [ERROR] Error extracting messages: {e}")

    return messages


def ingest_whatsapp_messages(vault_path: Path, session_path: Path) -> Dict[str, int]:
    """
    Ingest priority WhatsApp messages using Playwright.

    Args:
        vault_path: Path to the Obsidian vault
        session_path: Path to persistent browser session

    Returns:
        Dictionary with processing statistics
    """
    print("[INFO] Starting WhatsApp ingestion...")
    print(f"[INFO] Vault: {vault_path}")
    print(f"[INFO] Session: {session_path}")
    print("")

    # Load processed messages
    processed = load_processed_messages(vault_path)
    stats = {'captured': 0, 'skipped': 0, 'errors': 0}

    try:
        with sync_playwright() as p:
            # Launch browser with persistent context
            print("[INFO] Launching browser...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,  # Set to True for background operation
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ]
            )

            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to WhatsApp Web
            print("[INFO] Navigating to WhatsApp Web...")
            page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')

            # Extract priority messages
            messages = extract_priority_messages(page, processed)

            if messages:
                print(f"[INFO] Found {len(messages)} priority message(s)")
                print("")

                # Create inbox files for each message
                for msg in messages:
                    if create_inbox_file(msg, vault_path):
                        stats['captured'] += 1
                    else:
                        stats['errors'] += 1

                # Save processed messages
                save_processed_messages(vault_path, processed)
            else:
                print("[INFO] No new priority messages found")

            # Cleanup
            context.close()

    except Exception as e:
        print(f"[ERROR] Fatal error during ingestion: {e}")
        stats['errors'] += 1

    return stats


def main():
    """Main entry point."""
    # Get vault path from command line or use current directory
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path.cwd()

    # Validate vault path
    if not vault_path.exists():
        print(f"[ERROR] Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Set up session path
    # Use environment variable or default to vault subdirectory
    session_path_str = os.environ.get('WHATSAPP_SESSION_PATH', str(vault_path / '.whatsapp_browser_data'))
    session_path = Path(session_path_str)
    session_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("WhatsApp Ingest - Priority Message Capture")
    print("=" * 60)
    print("")

    # Ingest WhatsApp messages
    stats = ingest_whatsapp_messages(vault_path, session_path)

    # Print summary
    print("")
    print("=" * 60)
    print("WhatsApp Ingest Summary")
    print("=" * 60)
    print(f"[OK] Captured: {stats['captured']}")
    print(f"[SKIP] Skipped: {stats['skipped']}")
    print(f"[ERROR] Errors: {stats['errors']}")
    print("=" * 60)

    if stats['captured'] > 0:
        print("")
        print(f"[INFO] {stats['captured']} priority message(s) added to /Inbox")
        print("[INFO] These messages contain urgent keywords and require attention")


if __name__ == "__main__":
    main()
