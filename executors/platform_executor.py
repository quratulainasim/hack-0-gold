#!/usr/bin/env python3
"""
Platform Executor
Executes approved content on various platforms using Playwright and APIs
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PlatformExecutor:
    """Executes content on various platforms"""

    def __init__(self, session_dirs: Dict, screenshots_dir: Path, log_func):
        self.session_dirs = session_dirs
        self.screenshots_dir = screenshots_dir
        self.log = log_func

    def take_screenshot(self, page: Page, platform: str, error_msg: str) -> str:
        """Take screenshot on error"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_{timestamp}_error.png"
            filepath = self.screenshots_dir / filename

            page.screenshot(path=str(filepath), full_page=True)
            self.log(f"Screenshot saved: {filename}")

            return str(filepath)
        except Exception as e:
            self.log(f"Failed to take screenshot: {e}", "ERROR")
            return ""

    def execute(self, platform: str, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute content on specified platform"""
        self.log(f"Executing on {platform}...")

        # Route to appropriate executor
        if platform == 'linkedin':
            return self.execute_linkedin(content, metadata)
        elif platform == 'facebook':
            return self.execute_facebook(content, metadata)
        elif platform == 'instagram':
            return self.execute_instagram(content, metadata)
        elif platform in ['twitter', 'x']:
            return self.execute_twitter(content, metadata)
        elif platform == 'gmail':
            return self.execute_gmail(content, metadata)
        elif platform == 'whatsapp':
            return self.execute_whatsapp(content, metadata)
        elif platform == 'odoo':
            return self.execute_odoo(content, metadata)
        else:
            return False, f"Unknown platform: {platform}"

    def execute_linkedin(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute LinkedIn post using Playwright with saved session"""
        try:
            with sync_playwright() as p:
                self.log("Using LinkedIn browser automation with saved session...")

                # Use the saved browser session
                session_path = self.session_dirs.get('linkedin')

                self.log(f"Loading LinkedIn session from: {session_path}")

                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(session_path),
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to LinkedIn
                self.log("Navigating to LinkedIn feed...")
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=30000)
                time.sleep(5)

                # Take screenshot for debugging
                debug_screenshot = self.screenshots_dir / 'linkedin_before_post.png'
                page.screenshot(path=str(debug_screenshot))
                self.log(f"Debug screenshot saved: {debug_screenshot}")

                # Try to find and click the share box
                self.log("Looking for share box...")

                # Try clicking on the "Start a post" area
                try:
                    # Wait for the feed to load
                    page.wait_for_selector('.share-box-feed-entry', timeout=10000)

                    # Click the share box to open composer
                    page.click('.share-box-feed-entry', timeout=5000)
                    self.log("Clicked share box")
                    time.sleep(3)

                except Exception as e:
                    self.log(f"Share box not found, trying alternative: {e}")
                    # Try alternative - click anywhere in the share area
                    page.click('text=Start a post', timeout=5000)
                    time.sleep(3)

                # Find the content editable div and type
                self.log(f"Typing content ({len(content)} chars)...")

                # Wait for editor to appear
                page.wait_for_selector('.ql-editor', timeout=10000)

                # Click and type in the editor
                page.click('.ql-editor')
                time.sleep(1)

                # Type the content
                page.keyboard.type(content, delay=30)

                time.sleep(2)

                # Take screenshot before posting
                before_post_screenshot = self.screenshots_dir / 'linkedin_ready_to_post.png'
                page.screenshot(path=str(before_post_screenshot))
                self.log(f"Ready to post screenshot: {before_post_screenshot}")

                # Click the Post button
                self.log("Clicking Post button...")

                # Try multiple selectors for the Post button
                post_button_clicked = False
                post_selectors = [
                    'button.share-actions__primary-action',
                    'button:has-text("Post")',
                    '[data-test-share-box-post-button]',
                    '.share-actions button[type="submit"]'
                ]

                for selector in post_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000, state='visible')
                        page.click(selector, timeout=5000)
                        post_button_clicked = True
                        self.log(f"Clicked Post button using: {selector}")
                        break
                    except:
                        continue

                if not post_button_clicked:
                    raise Exception("Could not find Post button")

                # Wait for post to complete
                time.sleep(5)

                # Take screenshot after posting
                after_post_screenshot = self.screenshots_dir / 'linkedin_after_post.png'
                page.screenshot(path=str(after_post_screenshot))
                self.log(f"After post screenshot: {after_post_screenshot}")

                context.close()

                return True, "LinkedIn post published successfully via browser automation"

        except Exception as e:
            error_msg = f"LinkedIn execution failed: {str(e)}"
            self.log(error_msg, "ERROR")

            # Try to take error screenshot
            try:
                if 'page' in locals():
                    error_screenshot = self.screenshots_dir / 'linkedin_error.png'
                    page.screenshot(path=str(error_screenshot))
                    self.log(f"Error screenshot saved: {error_screenshot}")
            except:
                pass

            return False, error_msg

    def execute_facebook(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute Facebook post using Playwright"""
        try:
            with sync_playwright() as p:
                self.log("Launching Facebook browser...")

                session_path = self.session_dirs.get('facebook')
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(session_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to Facebook
                self.log("Navigating to Facebook...")
                page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
                time.sleep(3)

                # Click "What's on your mind?" composer
                self.log("Clicking post composer...")
                try:
                    page.click('div[role="button"]:has-text("What\'s on your mind")', timeout=10000)
                except:
                    # Try alternative selector
                    page.click('span:has-text("What\'s on your mind")', timeout=10000)

                time.sleep(2)

                # Type content using keyboard.type
                self.log(f"Typing content ({len(content)} chars)...")
                page.keyboard.type(content, delay=50)

                time.sleep(1)

                # Click Post button
                self.log("Clicking 'Post' button...")
                page.click('div[aria-label="Post"]', timeout=10000)

                time.sleep(3)

                context.close()

                return True, "Facebook post published successfully"

        except Exception as e:
            error_msg = f"Facebook execution failed: {str(e)}"
            self.log(error_msg, "ERROR")

            try:
                if 'page' in locals():
                    self.take_screenshot(page, 'facebook', error_msg)
            except:
                pass

            return False, error_msg

    def execute_instagram(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute Instagram DM using Playwright - simplified for existing conversations"""
        try:
            with sync_playwright() as p:
                self.log("Launching Instagram browser...")

                session_path = self.session_dirs.get('instagram')
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(session_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Get recipient from metadata
                recipient = metadata.get('recipient', metadata.get('to', ''))

                if not recipient:
                    return False, "No recipient specified for Instagram DM"

                # Navigate to Instagram Direct Messages
                self.log("Navigating to Instagram Direct Messages...")
                page.goto('https://www.instagram.com/direct/inbox/', wait_until='domcontentloaded')
                self.log("Waiting for page to fully load...")
                time.sleep(8)  # Increased wait time for full page load

                # Wait for page to be fully interactive
                page.wait_for_load_state('domcontentloaded')
                time.sleep(3)

                # Try to scroll to trigger lazy loading
                self.log("Scrolling to trigger conversation list loading...")
                page.evaluate("window.scrollBy(0, 100)")
                time.sleep(2)

                # Take screenshot for debugging
                debug_screenshot = self.screenshots_dir / 'instagram_dm_inbox.png'
                page.screenshot(path=str(debug_screenshot))
                self.log(f"Debug screenshot saved: {debug_screenshot}")

                # Look for existing conversation with recipient
                self.log(f"Looking for existing conversation with: {recipient}")

                # Try multiple selectors for conversation list
                try:
                    # Try different selectors with longer timeout
                    self.log("Waiting for conversations to appear...")
                    selectors_to_try = [
                        'div[class*="x1n2onr6"]',  # Working selector from inspection
                        'a[href*="/direct/t/"]',
                        'div[role="listitem"]',
                        'div[role="list"] > div'
                    ]

                    found = False
                    for selector in selectors_to_try:
                        try:
                            page.wait_for_selector(selector, timeout=15000)
                            self.log(f"Found conversations using selector: {selector}")
                            found = True
                            break
                        except:
                            self.log(f"Selector {selector} not found, trying next...")
                            continue

                    if not found:
                        return False, "Could not find conversation list on Instagram"

                    time.sleep(3)  # Additional wait for conversations to fully render

                    # Try clicking on conversation containing the recipient username
                    # Use JavaScript to find and click to avoid overlay issues
                    self.log(f"Attempting to click conversation with {recipient}...")

                    click_script = f"""
                    () => {{
                        // Try multiple selectors for Instagram conversations
                        const selectors = ['div[class*="x1n2onr6"]', 'a[href*="/direct/t/"]', 'div[role="listitem"]'];
                        for (let selector of selectors) {{
                            const items = document.querySelectorAll(selector);
                            for (let item of items) {{
                                if (item.textContent.includes('{recipient}')) {{
                                    item.click();
                                    return true;
                                }}
                            }}
                        }}
                        return false;
                    }}
                    """

                    clicked = page.evaluate(click_script)

                    if not clicked:
                        self.log(f"Could not find conversation with {recipient}")
                        return False, f"Conversation with {recipient} not found in inbox"

                    self.log("Clicked on conversation")
                    time.sleep(3)

                except Exception as e:
                    self.log(f"Failed to find conversation: {e}")
                    return False, f"Could not locate conversation with {recipient}"

                # Type message using keyboard (shortened to prevent timeout)
                # Limit to 200 chars for faster processing
                ig_content = content[:200] if len(content) > 200 else content
                self.log(f"Typing message ({len(ig_content)} chars)...")

                # Use keyboard shortcut or find message input
                # Try to focus on message input using Tab or clicking
                try:
                    # Look for the message input textarea
                    page.wait_for_selector('div[contenteditable="true"]', timeout=10000)

                    # Click on it using JavaScript to avoid overlay issues
                    page.evaluate("""
                        const input = document.querySelector('div[contenteditable="true"]');
                        if (input) input.focus();
                    """)

                    time.sleep(1)

                    # Type the message
                    page.keyboard.type(ig_content, delay=30)
                    time.sleep(2)

                except Exception as e:
                    self.log(f"Failed to type message: {e}")
                    return False, "Could not type message in input field"

                # Take screenshot before sending
                before_send_screenshot = self.screenshots_dir / 'instagram_dm_ready_to_send.png'
                page.screenshot(path=str(before_send_screenshot))
                self.log(f"Ready to send screenshot: {before_send_screenshot}")

                # Send message using Enter key instead of clicking button
                self.log("Sending message with Enter key...")
                page.keyboard.press('Enter')
                time.sleep(3)

                # Take screenshot after sending
                after_send_screenshot = self.screenshots_dir / 'instagram_dm_after_send.png'
                page.screenshot(path=str(after_send_screenshot))
                self.log(f"After send screenshot: {after_send_screenshot}")

                context.close()

                return True, f"Instagram DM sent to {recipient}"

        except Exception as e:
            error_msg = f"Instagram execution failed: {str(e)}"
            self.log(error_msg, "ERROR")

            try:
                if 'page' in locals():
                    self.take_screenshot(page, 'instagram', error_msg)
            except:
                pass

            return False, error_msg

    def execute_twitter(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute Twitter/X DM using Playwright - for existing conversations"""
        try:
            with sync_playwright() as p:
                self.log("Launching Twitter/X browser...")

                session_path = self.session_dirs.get('twitter')
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(session_path),
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ],
                    ignore_default_args=['--enable-automation'],
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Get recipient from metadata
                recipient = metadata.get('recipient', metadata.get('to', ''))

                if not recipient:
                    # If no recipient, treat as a tweet (original behavior)
                    self.log("No recipient specified, posting as tweet...")

                    # Navigate to Twitter compose
                    page.goto('https://twitter.com/compose/tweet', wait_until='domcontentloaded')
                    time.sleep(3)

                    # Type content (very short to ensure Post button enables)
                    # Limit to 80 chars to prevent button staying disabled
                    tweet_content = content[:80] if len(content) > 80 else content
                    self.log(f"Typing tweet ({len(tweet_content)} chars)...")

                    # Find tweet composer
                    page.click('div[role="textbox"]', timeout=10000)
                    time.sleep(1)

                    page.keyboard.type(tweet_content, delay=50)
                    self.log("Tweet content typed, waiting for Post button to enable...")
                    time.sleep(3)  # Increased wait time for Twitter to process input

                    # Wait for Post button to become enabled (not disabled)
                    self.log("Waiting for Post button to become enabled...")
                    try:
                        # Wait for button to exist and be enabled
                        page.wait_for_selector('button[data-testid="tweetButtonInline"]:not([disabled])', timeout=10000)
                        self.log("Post button is now enabled")
                    except:
                        self.log("Post button still disabled, trying alternative approach...")
                        # Try waiting a bit more
                        time.sleep(2)

                    # Click Post button
                    self.log("Clicking 'Post' button...")
                    page.click('button[data-testid="tweetButtonInline"]', timeout=10000)
                    time.sleep(3)

                    context.close()
                    return True, "Twitter/X post published successfully"

                # Handle DM to existing conversation
                self.log(f"Sending DM to existing conversation with: {recipient}")

                # Navigate to Twitter Messages
                page.goto('https://twitter.com/messages', wait_until='domcontentloaded')
                self.log("Waiting for messages page to fully load...")
                time.sleep(8)  # Increased wait time for WebSocket connections

                # Take screenshot for debugging
                debug_screenshot = self.screenshots_dir / 'twitter_dm_inbox.png'
                page.screenshot(path=str(debug_screenshot))
                self.log(f"Debug screenshot saved: {debug_screenshot}")

                # Look for existing conversation
                self.log(f"Looking for conversation with {recipient}...")

                try:
                    # Wait longer for conversations to load (increased timeout)
                    self.log("Waiting for conversations to appear...")

                    # Try multiple selectors
                    selectors_to_try = [
                        'div[class*="css-175oi2r"]',  # Generic Twitter container
                        'div[data-testid="conversation"]',
                        'a[href*="/messages/"]',
                        'div[role="link"]'
                    ]

                    found = False
                    working_selector = None
                    for selector in selectors_to_try:
                        try:
                            page.wait_for_selector(selector, timeout=15000)
                            self.log(f"Found elements using selector: {selector}")
                            found = True
                            working_selector = selector
                            break
                        except:
                            self.log(f"Selector {selector} not found, trying next...")
                            continue

                    if not found:
                        return False, "Could not find conversation list on Twitter"

                    time.sleep(3)  # Additional wait for conversations to fully render

                    # Click on conversation using JavaScript
                    click_script = f"""
                    () => {{
                        const elements = document.querySelectorAll('{working_selector}');
                        for (let elem of elements) {{
                            if (elem.textContent.includes('{recipient}')) {{
                                elem.click();
                                return true;
                            }}
                        }}
                        return false;
                    }}
                    """

                    clicked = page.evaluate(click_script)

                    if not clicked:
                        self.log(f"Could not find conversation with {recipient}")
                        return False, f"Conversation with {recipient} not found"

                    self.log("Clicked on conversation")
                    time.sleep(3)

                except Exception as e:
                    self.log(f"Failed to find conversation: {e}")
                    return False, f"Could not locate conversation with {recipient}"

                # Type message (shortened to prevent timeout)
                # Limit to 200 chars for faster processing
                dm_content = content[:200] if len(content) > 200 else content
                self.log(f"Typing message ({len(dm_content)} chars)...")

                try:
                    # Find message input
                    page.wait_for_selector('div[data-testid="dmComposerTextInput"]', timeout=10000)

                    # Focus and type using JavaScript
                    page.evaluate("""
                        const input = document.querySelector('div[data-testid="dmComposerTextInput"]');
                        if (input) input.focus();
                    """)

                    time.sleep(1)
                    page.keyboard.type(dm_content, delay=30)
                    time.sleep(2)

                except Exception as e:
                    self.log(f"Failed to type message: {e}")
                    return False, "Could not type message in input field"

                # Take screenshot before sending
                before_send_screenshot = self.screenshots_dir / 'twitter_dm_ready_to_send.png'
                page.screenshot(path=str(before_send_screenshot))
                self.log(f"Ready to send screenshot: {before_send_screenshot}")

                # Send message using Enter key or button
                self.log("Sending message...")
                try:
                    # Try clicking send button first
                    page.click('button[data-testid="dmComposerSendButton"]', timeout=5000)
                except:
                    # Fallback to Enter key
                    page.keyboard.press('Enter')

                time.sleep(3)

                # Take screenshot after sending
                after_send_screenshot = self.screenshots_dir / 'twitter_dm_after_send.png'
                page.screenshot(path=str(after_send_screenshot))
                self.log(f"After send screenshot: {after_send_screenshot}")

                context.close()

                return True, f"Twitter DM sent to {recipient}"

        except Exception as e:
            error_msg = f"Twitter/X execution failed: {str(e)}"
            self.log(error_msg, "ERROR")

            try:
                if 'page' in locals():
                    self.take_screenshot(page, 'twitter', error_msg)
            except:
                pass

            return False, error_msg

    def execute_gmail(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute Gmail email using API"""
        try:
            self.log("Sending email via Gmail API...")

            # Import Gmail API modules
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from email.mime.text import MIMEText
            import base64

            # Get credentials from environment
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

            if not all([client_id, client_secret, refresh_token]):
                return False, "Gmail credentials not configured"

            # Create credentials
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret
            )

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # Extract email details from metadata
            to_email = metadata.get('to', '')
            subject = metadata.get('subject', 'Message from AI System')

            if not to_email:
                return False, "No recipient email specified"

            # Create message
            message = MIMEText(content)
            message['to'] = to_email
            message['subject'] = subject

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            self.log(f"Email sent successfully (ID: {send_message['id']})")

            return True, f"Email sent to {to_email}"

        except Exception as e:
            error_msg = f"Gmail execution failed: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg

    def execute_whatsapp(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute WhatsApp message using Playwright - for existing conversations"""
        try:
            with sync_playwright() as p:
                self.log("Launching WhatsApp browser...")

                session_path = self.session_dirs.get('whatsapp')
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(session_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to WhatsApp Web
                self.log("Navigating to WhatsApp Web...")
                page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded')
                self.log("Waiting for WhatsApp to fully load...")
                time.sleep(8)  # Increased wait time for full page load

                # Wait for page to be fully interactive
                page.wait_for_load_state('domcontentloaded')
                time.sleep(3)

                # Try to scroll to trigger lazy loading
                self.log("Scrolling to trigger conversation list loading...")
                page.evaluate("window.scrollBy(0, 100)")
                time.sleep(2)

                # Get contact name from metadata
                contact = metadata.get('contact', metadata.get('to', metadata.get('recipient', '')))

                if not contact:
                    return False, "No contact specified"

                # Take screenshot for debugging
                debug_screenshot = self.screenshots_dir / 'whatsapp_inbox.png'
                page.screenshot(path=str(debug_screenshot))
                self.log(f"Debug screenshot saved: {debug_screenshot}")

                # Look for existing conversation
                self.log(f"Looking for conversation with: {contact}")

                try:
                    # Try multiple selectors with longer timeout
                    self.log("Waiting for conversations to appear...")
                    selectors_to_try = [
                        'span[dir="auto"][title]',  # Working selector from inspection
                        'div[class*="_ak8l"]',
                        'div[role="listitem"]',
                        'div[data-testid="cell-frame-container"]'
                    ]

                    found = False
                    for selector in selectors_to_try:
                        try:
                            page.wait_for_selector(selector, timeout=15000)
                            self.log(f"Found conversations using selector: {selector}")
                            found = True
                            break
                        except:
                            self.log(f"Selector {selector} not found, trying next...")
                            continue

                    if not found:
                        return False, "Could not find conversation list on WhatsApp"

                    time.sleep(3)  # Additional wait for conversations to fully render

                    # Click on conversation using JavaScript to avoid overlay issues
                    click_script = f"""
                    () => {{
                        // Try multiple selectors for WhatsApp conversations
                        const selectors = ['span[dir="auto"][title]', 'div[class*="_ak8l"]', 'div[role="listitem"]'];
                        for (let selector of selectors) {{
                            const items = document.querySelectorAll(selector);
                            for (let item of items) {{
                                if (item.textContent.includes('{contact}')) {{
                                    item.click();
                                    return true;
                                }}
                            }}
                        }}
                        return false;
                    }}
                    """

                    clicked = page.evaluate(click_script)

                    if not clicked:
                        self.log(f"Could not find conversation with {contact}")
                        return False, f"Conversation with {contact} not found"

                    self.log("Clicked on conversation")
                    time.sleep(3)

                except Exception as e:
                    self.log(f"Failed to find conversation: {e}")
                    return False, f"Could not locate conversation with {contact}"

                # Type message (shortened to prevent timeout)
                # Limit to 200 chars for faster processing
                wa_content = content[:200] if len(content) > 200 else content
                self.log(f"Typing message ({len(wa_content)} chars)...")

                try:
                    # Find message input field
                    page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=10000)

                    # Focus and type using JavaScript
                    page.evaluate("""
                        const input = document.querySelector('div[contenteditable="true"][data-tab="10"]');
                        if (input) input.focus();
                    """)

                    time.sleep(1)
                    page.keyboard.type(wa_content, delay=30)
                    time.sleep(2)

                except Exception as e:
                    self.log(f"Failed to type message: {e}")
                    return False, "Could not type message in input field"

                # Take screenshot before sending
                before_send_screenshot = self.screenshots_dir / 'whatsapp_ready_to_send.png'
                page.screenshot(path=str(before_send_screenshot))
                self.log(f"Ready to send screenshot: {before_send_screenshot}")

                # Send message using Enter key
                self.log("Sending message with Enter key...")
                page.keyboard.press('Enter')
                time.sleep(3)

                # Take screenshot after sending
                after_send_screenshot = self.screenshots_dir / 'whatsapp_after_send.png'
                page.screenshot(path=str(after_send_screenshot))
                self.log(f"After send screenshot: {after_send_screenshot}")

                context.close()

                return True, f"WhatsApp message sent to {contact}"

        except Exception as e:
            error_msg = f"WhatsApp execution failed: {str(e)}"
            self.log(error_msg, "ERROR")

            try:
                if 'page' in locals():
                    self.take_screenshot(page, 'whatsapp', error_msg)
            except:
                pass

            return False, error_msg

    def execute_odoo(self, content: str, metadata: Dict) -> Tuple[bool, str]:
        """Execute Odoo operation using XML-RPC API"""
        try:
            self.log("Executing Odoo operation via API...")

            import xmlrpc.client

            # Get Odoo credentials
            url = os.getenv('ODOO_URL')
            db = os.getenv('ODOO_DB')
            username = os.getenv('ODOO_USERNAME')
            password = os.getenv('ODOO_PASSWORD')

            if not all([url, db, username, password]):
                return False, "Odoo credentials not configured"

            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})

            if not uid:
                return False, "Odoo authentication failed"

            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

            # Determine operation type from metadata
            operation = metadata.get('content_type', 'invoice_draft')

            if 'invoice' in operation:
                # Create/post invoice
                self.log("Creating invoice in Odoo...")

                # Parse invoice details from content
                # This is simplified - real implementation would parse structured data
                invoice_data = {
                    'partner_id': 1,  # Would be parsed from content
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'move_type': 'out_invoice',
                }

                # Create invoice
                invoice_id = models.execute_kw(
                    db, uid, password,
                    'account.move', 'create',
                    [invoice_data]
                )

                self.log(f"Invoice created (ID: {invoice_id})")

                return True, f"Odoo invoice created (ID: {invoice_id})"

            else:
                return False, f"Unknown Odoo operation: {operation}"

        except Exception as e:
            error_msg = f"Odoo execution failed: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg
