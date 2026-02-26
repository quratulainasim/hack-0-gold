#!/usr/bin/env python3
"""
Twitter/X Simple Capture

Opens Twitter/X, waits 45 seconds for you to navigate to notifications,
then automatically reads and captures mentions with priority keywords.
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

def create_inbox_file(tweet_data: Dict[str, str], vault_path: Path) -> bool:
    """Create inbox file for tweet."""
    try:
        inbox_path = vault_path / "Needs_Action"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        author_safe = sanitize_filename(tweet_data['author'])
        content_safe = sanitize_filename(tweet_data['content'][:30])
        filename = f"X_{timestamp}_{author_safe}_{content_safe}.md"
        filepath = inbox_path / filename

        matched_keywords = extract_matched_keywords(tweet_data['content'])
        keywords_str = ', '.join(matched_keywords)

        content = f"""---
type: twitter
priority: high
status: pending
timestamp: {tweet_data['timestamp']}
source: twitter
author: {tweet_data['author']}
handle: {tweet_data.get('handle', 'unknown')}
keywords: {keywords_str}
---

# Twitter/X Priority Mention from {tweet_data['author']}

**From**: {tweet_data['author']} (@{tweet_data.get('handle', 'unknown')})
**Received**: {tweet_data['timestamp']}
**Priority**: HIGH
**Keywords Matched**: {keywords_str}

---

## Tweet Content

{tweet_data['content']}

---

## Context

This tweet was flagged as high priority because it contains urgent keywords: **{keywords_str}**

**Author**: {tweet_data['author']}
**Source**: Twitter/X
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review tweet content
- [ ] Determine appropriate response
- [ ] Reply or quote tweet if needed
- [ ] Follow up with author

---

*Captured by Twitter/X Simple Capture on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create file: {e}")
        return False

def load_processed_tweets(vault_path: Path) -> set:
    """Load processed tweet IDs."""
    processed_file = vault_path / ".x_processed.json"
    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed', []))
        except:
            return set()
    return set()

def save_processed_tweets(vault_path: Path, processed: set):
    """Save processed tweet IDs."""
    processed_file = vault_path / ".x_processed.json"
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump({'processed': list(processed)}, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save: {e}")

def capture_tweets():
    """Capture Twitter/X mentions."""

    print("="*60)
    print("Twitter/X Simple Capture")
    print("="*60)
    print()

    vault_path = Path.cwd().parent if Path.cwd().name == 'watchers' else Path.cwd()
    session_path = vault_path / '.x_browser_data'
    processed = load_processed_tweets(vault_path)
    stats = {'captured': 0, 'skipped': 0}

    with sync_playwright() as p:
        print("[1/4] Launching browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[2/4] Navigating to Twitter/X notifications...")
        page.goto('https://twitter.com/notifications', wait_until='domcontentloaded')

        print("[3/4] Waiting for Twitter/X to load...")
        time.sleep(5)  # Give page time to load
        print("      [OK] Twitter/X page loaded")

        print()
        print("="*60)
        print("ACTION REQUIRED IN BROWSER")
        print("="*60)
        print()
        print("You have 45 SECONDS to:")
        print("1. Make sure you're logged in")
        print("2. Scroll through notifications if needed")
        print("3. The script will automatically capture priority mentions")
        print()
        print("The script will automatically continue after 45 seconds...")
        print()

        # Countdown
        for i in range(45, 0, -5):
            print(f"  {i} seconds remaining...")
            time.sleep(5)

        print()
        print("[4/4] Reading mentions...")
        print()

        tweets = []

        try:
            # Try multiple selectors for Twitter content
            selectors = [
                'article',  # Standard tweets
                '[data-testid="tweet"]',  # Tweet containers
                '[role="article"]',  # Alternative
            ]

            articles = []
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    articles = elements
                    print(f"  Found {len(elements)} tweet(s) using: {selector}")
                    break

            if not articles:
                # Fallback: get all visible text
                print("  Using fallback: reading all visible text")
                try:
                    body_text = page.inner_text('body')
                    if body_text and contains_priority_keywords(body_text):
                        paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]
                        for para in paragraphs:
                            if contains_priority_keywords(para) and len(para) > 20:
                                lines = para.split('\n')
                                author = lines[0] if lines else 'Twitter User'

                                tweet_id = f"{author}_{para[:50]}_{len(para)}"
                                if tweet_id not in processed:
                                    tweets.append({
                                        'author': author,
                                        'handle': 'unknown',
                                        'content': para,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    processed.add(tweet_id)
                                    print(f"  [MATCH] Found: {para[:50]}...")
                except Exception as e:
                    print(f"  [ERROR] Fallback failed: {e}")
            else:
                # Process found articles
                for article in articles[:20]:  # Check first 20 tweets
                    try:
                        # Try to get tweet text
                        text = None
                        text_elem = article.query_selector('[data-testid="tweetText"]')
                        if text_elem:
                            text = text_elem.inner_text()
                        else:
                            # Fallback: get all text from article
                            text = article.inner_text()

                        if text and contains_priority_keywords(text):
                            # Get author name and handle
                            author = "Unknown"
                            handle = "unknown"
                            try:
                                author_elem = article.query_selector('[data-testid="User-Name"]')
                                if author_elem:
                                    author_text = author_elem.inner_text()
                                    parts = author_text.split('\n')
                                    if len(parts) >= 2:
                                        author = parts[0]
                                        handle = parts[1].replace('@', '')
                            except:
                                pass

                            tweet_id = f"{author}_{text[:50]}_{len(text)}"

                            if tweet_id not in processed:
                                tweets.append({
                                    'author': author,
                                    'handle': handle,
                                    'content': text,
                                    'timestamp': datetime.now().isoformat()
                                })
                                processed.add(tweet_id)
                                print(f"  [MATCH] Found: {text[:50]}...")
                    except:
                        continue

        except Exception as e:
            print(f"  [ERROR] Error reading tweets: {e}")

        print()
        print(f"  Total priority mentions found: {len(tweets)}")
        print()

        # Create inbox files
        if tweets:
            print("Creating inbox files...")
            for tweet in tweets:
                if create_inbox_file(tweet, vault_path):
                    stats['captured'] += 1

            save_processed_tweets(vault_path, processed)
        else:
            print("[INFO] No new priority mentions found")

        print()
        print("Waiting 10 seconds before closing browser...")
        time.sleep(10)

        context.close()

    return stats

def main():
    """Main entry point."""
    stats = capture_tweets()

    print()
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"[OK] Captured: {stats['captured']}")
    print(f"[SKIP] Skipped: {stats['skipped']}")
    print("="*60)

    if stats['captured'] > 0:
        print()
        print(f"[INFO] {stats['captured']} mention(s) added to /Needs_Action")
        print("[INFO] Check Needs_Action/ folder for captured mentions")

if __name__ == "__main__":
    main()
