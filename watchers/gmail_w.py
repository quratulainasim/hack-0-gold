#!/usr/bin/env python3
"""
Gmail Sentinel Watcher - Enhanced
Monitors Gmail for unread important messages using Gmail API.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Priority keywords
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'lead', 'meeting', 'deadline', 'important', 'critical', 'client', 'proposal']

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

def create_inbox_file(email_data: Dict[str, str], vault_path: Path) -> bool:
    """Create inbox file for email."""
    try:
        inbox_path = vault_path / "Needs_Action"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        sender_safe = sanitize_filename(email_data['sender'])
        filename = f"GMAIL_{timestamp}_{sender_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(email_data['subject'] + ' ' + email_data['body'])
        keywords_str = ', '.join(matched_keywords) if matched_keywords else 'general'

        content = f"""---
type: email
priority: {email_data.get('priority', 'high')}
status: new
timestamp: {email_data['timestamp']}
source: gmail
sender: {email_data['sender']}
keywords: {keywords_str}
---

# Gmail: {email_data['subject']}

**From**: {email_data['sender']}
**Received**: {email_data['timestamp']}
**Priority**: {email_data.get('priority', 'high').upper()}
**Keywords Matched**: {keywords_str}

---

## Email Content

{email_data['body']}

---

## Context

This email was flagged as {email_data.get('priority', 'high')} priority.

**Sender**: {email_data['sender']}
**Source**: Gmail API
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review email content
- [ ] Determine appropriate response
- [ ] Draft reply if needed
- [ ] Follow up with sender

---

*Captured by Gmail Sentinel on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create file: {e}")
        return False

def load_processed_emails(vault_path: Path) -> set:
    """Load processed email IDs."""
    processed_file = vault_path / ".gmail_processed.json"
    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        except:
            return set()
    return set()

def save_processed_emails(vault_path: Path, processed: set):
    """Save processed email IDs."""
    processed_file = vault_path / ".gmail_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def check_gmail_api(vault_path: Path) -> int:
    """Check Gmail using Gmail API."""
    try:
        # Try to import Gmail API libraries
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        import pickle

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None

        # Load credentials
        token_path = vault_path / 'config' / 'gmail_token.pickle'
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("  [INFO] Gmail credentials not found or invalid")
                return 0

        service = build('gmail', 'v1', credentials=creds)

        # Get unread messages
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return 0

        processed = load_processed_emails(vault_path)
        new_count = 0

        for msg in messages:
            msg_id = msg['id']

            if msg_id in processed:
                continue

            # Get message details
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

            # Get body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break

            # Check if priority
            if contains_priority_keywords(subject + ' ' + body):
                email_data = {
                    'sender': sender,
                    'subject': subject,
                    'body': body[:500],  # Truncate long emails
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'high'
                }

                if create_inbox_file(email_data, vault_path):
                    processed.add(msg_id)
                    new_count += 1

        if new_count > 0:
            save_processed_emails(vault_path, processed)

        return new_count

    except ImportError:
        print("  [INFO] Gmail API libraries not installed")
        return 0
    except Exception as e:
        print(f"  [ERROR] Gmail API error: {e}")
        return 0

def watch_gmail(vault_path: Path, check_interval: int = 300):
    """Watch Gmail for new messages."""
    print("="*60)
    print("Gmail Sentinel Watcher - Enhanced")
    print("="*60)
    print(f"[INFO] Vault: {vault_path.absolute()}")
    print(f"[INFO] Check Interval: {check_interval} seconds")
    print()

    iteration = 0

    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Check #{iteration}")
            print("-"*60)

            new_count = check_gmail_api(vault_path)

            if new_count > 0:
                print(f"  [OK] Found {new_count} new priority email(s)")
            else:
                print("  [INFO] No new priority emails found")

            print(f"  Next check in {check_interval} seconds...")
            print()
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print()
        print("[INFO] Gmail watcher stopped by user")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"[ERROR] Error in Gmail watcher: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    vault_path = Path.cwd()
    check_interval = int(os.environ.get('GMAIL_CHECK_INTERVAL', 300))
    watch_gmail(vault_path, check_interval)

if __name__ == "__main__":
    main()
