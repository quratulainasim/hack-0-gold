#!/usr/bin/env python3
"""
LinkedIn Simple Capture

Opens LinkedIn feed, waits 45 seconds for you to scroll through posts,
then automatically reads and captures posts with priority keywords.
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

# Priority keywords for LinkedIn
PRIORITY_KEYWORDS = ['urgent', 'asap', 'opportunity', 'partnership', 'collaboration', 'lead', 'meeting', 'project', 'interested', 'discuss']

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
    """Create inbox file for LinkedIn notification."""
    try:
        inbox_path = vault_path / "Inbox"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        author_safe = sanitize_filename(notification_data['author'])
        notif_type = sanitize_filename(notification_data['type'])
        filename = f"LI_{timestamp}_{notif_type}_{author_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(notification_data['content'])
        keywords_str = ', '.join(matched_keywords) if matched_keywords else 'general'

        content = f"""---
source: linkedin
type: {notification_data['type']}
priority: {notification_data['priority']}
timestamp: {notification_data['timestamp']}
status: pending
author: {notification_data['author']}
keywords: {keywords_str}
---

# LinkedIn {notification_data['type'].title()}: {notification_data['author']}

**Received**: {notification_data['timestamp']}
**Priority**: {notification_data['priority'].upper()}
**Keywords Matched**: {keywords_str}

---

## Notification Content

{notification_data['content']}

---

## Context

This LinkedIn notification was flagged as {notification_data['priority']} priority.

**From**: {notification_data['author']}
**Source**: LinkedIn
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review notification details
- [ ] Check sender's LinkedIn profile
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Follow up if needed

---

*Captured by LinkedIn Simple Capture on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
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
    processed_file = vault_path / ".linkedin_processed.json"
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
    processed_file = vault_path / ".linkedin_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def capture_notifications():
    """Capture LinkedIn notifications."""

    print("="*60)
    print("LinkedIn Simple Capture")
    print("="*60)
    print()

    vault_path = Path.cwd()
    session_path = vault_path / '.linkedin_browser_data'
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

        print("[2/4] Navigating to LinkedIn Feed...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')

        print("[3/4] Waiting for LinkedIn to load...")
        time.sleep(5)  # Give page time to load
        print("      [OK] LinkedIn page loaded")

        print()
        print("="*60)
        print("ACTION REQUIRED IN BROWSER")
        print("="*60)
        print()
        print("You have 45 SECONDS to:")
        print("1. Log in to LinkedIn (if not already logged in)")
        print("2. Scroll through your feed to load posts")
        print("3. Make sure posts are visible on the page")
        print()
        print("The script will automatically continue after 45 seconds...")
        print()

        # Countdown
        for i in range(45, 0, -5):
            print(f"  {i} seconds remaining...")
            time.sleep(5)

        print()
        print("[4/4] Reading posts from feed...")
        print()

        notifications = []

        try:
            # Try multiple post selectors for LinkedIn feed
            post_selectors = [
                'div[class*="feed-shared-update-v2"]',  # Main post container
                'div[data-id]',  # Posts with data-id
                'article',  # Article posts
                'div[class*="feed-shared-update"]',  # Alternative post container
            ]

            post_elements = []
            for selector in post_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if len(elements) > 0:
                        post_elements = elements
                        print(f"  Found {len(elements)} posts using: {selector}")
                        break
                except:
                    continue

            if not post_elements:
                print("  [INFO] No posts found with standard selectors")
                print("  [INFO] Trying alternative approach - reading all visible text...")

                # Fallback: get all visible text from feed
                try:
                    # Try to get the main feed area
                    feed_area = page.query_selector('main')
                    if feed_area:
                        body_text = feed_area.inner_text()
                    else:
                        body_text = page.inner_text('body')

                    if body_text:
                        # Split into paragraphs and look for content with keywords
                        paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]
                        for para in paragraphs:
                            if contains_priority_keywords(para) and len(para) > 20:
                                # Extract first line as potential author
                                lines = para.split('\n')
                                author = lines[0][:50] if lines else 'LinkedIn User'

                                post_id = f"linkedin_{para[:50]}_{len(para)}"
                                if post_id not in processed:
                                    notifications.append({
                                        'author': author,
                                        'type': 'post',
                                        'content': para,
                                        'timestamp': datetime.now().isoformat(),
                                        'priority': 'high',
                                        'notification_id': post_id
                                    })
                                    processed.add(post_id)
                                    print(f"  [MATCH] Found post: {para[:50]}...")
                except Exception as e:
                    print(f"  [ERROR] Alternative approach failed: {e}")

            else:
                # Process found posts
                recent = post_elements[-20:] if len(post_elements) > 20 else post_elements

                for post_elem in recent:
                    try:
                        # Get post text
                        text = post_elem.inner_text()

                        if text and len(text) > 20:
                            # Try to extract author from post
                            author = "LinkedIn User"
                            author_selectors = [
                                'span[class*="update-components-actor__name"]',
                                'span[class*="actor-name"]',
                                'a[class*="app-aware-link"] span[aria-hidden="true"]',
                                'strong',
                            ]

                            for auth_sel in author_selectors:
                                try:
                                    auth_elem = post_elem.query_selector(auth_sel)
                                    if auth_elem:
                                        author_text = auth_elem.inner_text()
                                        if author_text and len(author_text) > 0 and len(author_text) < 100:
                                            author = author_text.strip()
                                            break
                                except:
                                    continue

                            # Check if post contains priority keywords
                            if contains_priority_keywords(text):
                                priority = 'high'

                                post_id = f"{author}_{text[:50]}_{len(text)}"
                                if post_id not in processed:
                                    notifications.append({
                                        'author': author,
                                        'type': 'post',
                                        'content': text,
                                        'timestamp': datetime.now().isoformat(),
                                        'priority': priority,
                                        'notification_id': post_id
                                    })
                                    processed.add(post_id)
                                    print(f"  [MATCH] POST: {author}")
                    except:
                        continue

        except Exception as e:
            print(f"  [ERROR] Error reading posts: {e}")

        print()
        print(f"  Total posts with keywords found: {len(notifications)}")
        print()

        # Create inbox files
        if notifications:
            print("Creating inbox files...")
            for notif in notifications:
                if create_inbox_file(notif, vault_path):
                    stats['captured'] += 1

            save_processed_notifications(vault_path, processed)
        else:
            print("[INFO] No new notifications found")

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
        print(f"[INFO] {stats['captured']} notification(s) added to /Inbox")
        print("[INFO] Check Inbox/ folder for captured notifications")

if __name__ == "__main__":
    main()
