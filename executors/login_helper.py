#!/usr/bin/env python3
"""
Login Helper - Re-authenticate browser sessions for Instagram, Twitter, and WhatsApp
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import shutil

class LoginHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.session_dirs = {
            'instagram': self.project_root / '.instagram_browser_data',
            'twitter': self.project_root / '.x_browser_data',
            'whatsapp': self.project_root / '.whatsapp_browser_data'
        }

    def clear_session(self, platform: str):
        """Clear existing browser session for a platform"""
        session_path = self.session_dirs.get(platform)
        if session_path and session_path.exists():
            print(f"[DELETE] Clearing old {platform} session from: {session_path}")
            shutil.rmtree(session_path)
            print(f"[OK] Cleared {platform} session")
        else:
            print(f"[INFO] No existing {platform} session found")

    def login_instagram(self):
        """Guide user to login to Instagram"""
        print("\n" + "="*60)
        print("INSTAGRAM LOGIN")
        print("="*60)

        self.clear_session('instagram')

        print("\nOpening Instagram in browser...")
        print("Please login manually:")
        print("   1. Enter your username and password")
        print("   2. Complete any 2FA if required")
        print("   3. Once logged in, press ENTER in this terminal")
        print("\nWaiting for you to login...")

        with sync_playwright() as p:
            session_path = self.session_dirs['instagram']
            session_path.mkdir(parents=True, exist_ok=True)

            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )

            page = browser.new_page()
            page.goto('https://www.instagram.com/direct/inbox/')

            # Wait for user to login (5 minutes timeout)
            print("\n[INFO] Browser will stay open for 5 minutes for you to login...")
            print("[INFO] The session will be saved automatically when you close this window")
            print("[INFO] Or press Ctrl+C in this terminal when done")

            try:
                time.sleep(300)  # Wait 5 minutes
            except KeyboardInterrupt:
                print("\n[INFO] Login session saved")

            # Verify login by checking if we're on the inbox page
            try:
                current_url = page.url
                if 'instagram.com' in current_url and 'login' not in current_url:
                    print("[OK] Instagram login successful!")
                    print(f"[URL] Current URL: {current_url}")
                else:
                    print("[WARNING] You might not be logged in properly")
                    print(f"[URL] Current URL: {current_url}")
            except:
                print("[INFO] Browser was closed by user")

            try:
                browser.close()
            except:
                pass

    def login_twitter(self):
        """Guide user to login to Twitter/X"""
        print("\n" + "="*60)
        print("TWITTER/X LOGIN")
        print("="*60)

        self.clear_session('twitter')

        print("\nOpening Twitter/X in browser...")
        print("IMPORTANT: Do NOT use 'Sign in with Google'")
        print("Please login manually:")
        print("   1. Use your Twitter username/email and password")
        print("   2. Complete any 2FA if required")
        print("   3. Wait for the browser to stay open (5 minutes)")
        print("\nWaiting for you to login...")

        with sync_playwright() as p:
            session_path = self.session_dirs['twitter']
            session_path.mkdir(parents=True, exist_ok=True)

            # Launch with flags to bypass automation detection
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800},
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

            page = browser.new_page()
            page.goto('https://twitter.com/messages')

            # Wait for user to login (5 minutes timeout)
            print("\n[INFO] Browser will stay open for 5 minutes for you to login...")
            print("[INFO] The session will be saved automatically when you close this window")
            print("[INFO] Or press Ctrl+C in this terminal when done")

            try:
                time.sleep(300)  # Wait 5 minutes
            except KeyboardInterrupt:
                print("\n[INFO] Login session saved")

            # Verify login
            try:
                current_url = page.url
                if 'twitter.com' in current_url and 'login' not in current_url:
                    print("[OK] Twitter/X login successful!")
                    print(f"[URL] Current URL: {current_url}")
                else:
                    print("[WARNING] You might not be logged in properly")
                    print(f"[URL] Current URL: {current_url}")
            except:
                print("[INFO] Browser was closed by user")

            try:
                browser.close()
            except:
                pass

    def login_whatsapp(self):
        """Guide user to login to WhatsApp Web"""
        print("\n" + "="*60)
        print("WHATSAPP WEB LOGIN")
        print("="*60)

        self.clear_session('whatsapp')

        print("\nOpening WhatsApp Web in browser...")
        print("Please login manually:")
        print("   1. Scan the QR code with your phone")
        print("   2. Wait for WhatsApp to load completely")
        print("   3. Once you see your chats, press ENTER in this terminal")
        print("\nWaiting for you to login...")

        with sync_playwright() as p:
            session_path = self.session_dirs['whatsapp']
            session_path.mkdir(parents=True, exist_ok=True)

            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )

            page = browser.new_page()
            page.goto('https://web.whatsapp.com/')

            # Wait for user to login (5 minutes timeout)
            print("\n[INFO] Browser will stay open for 5 minutes for you to login...")
            print("[INFO] Scan the QR code with your phone")
            print("[INFO] The session will be saved automatically when you close this window")
            print("[INFO] Or press Ctrl+C in this terminal when done")

            try:
                time.sleep(300)  # Wait 5 minutes
            except KeyboardInterrupt:
                print("\n[INFO] Login session saved")

            # Verify login
            try:
                current_url = page.url
                if 'web.whatsapp.com' in current_url:
                    print("[OK] WhatsApp Web login successful!")
                    print(f"[URL] Current URL: {current_url}")
                else:
                    print("[WARNING] You might not be logged in properly")
                    print(f"[URL] Current URL: {current_url}")
            except:
                print("[INFO] Browser was closed by user")

            try:
                browser.close()
            except:
                pass

    def run_all(self):
        """Run login process for all platforms"""
        print("\n" + "="*60)
        print("MULTI-PLATFORM LOGIN HELPER")
        print("="*60)
        print("\nThis will guide you through logging into:")
        print("  1. Instagram")
        print("  2. Twitter/X")
        print("  3. WhatsApp Web")
        print("\n" + "="*60)

        try:
            # Instagram
            self.login_instagram()

            # Twitter
            self.login_twitter()

            # WhatsApp
            self.login_whatsapp()

            print("\n" + "="*60)
            print("[OK] ALL LOGINS COMPLETE!")
            print("="*60)
            print("\nYou can now run the orchestrator to test autonomous execution:")
            print("   python executors/master_orchestrator.py")

        except KeyboardInterrupt:
            print("\n\n[WARNING] Login process interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n[ERROR] Error during login: {e}")
            sys.exit(1)

def main():
    helper = LoginHelper()

    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform == 'instagram':
            helper.login_instagram()
        elif platform == 'twitter' or platform == 'x':
            helper.login_twitter()
        elif platform == 'whatsapp':
            helper.login_whatsapp()
        else:
            print(f"❌ Unknown platform: {platform}")
            print("Usage: python login_helper.py [instagram|twitter|whatsapp]")
            sys.exit(1)
    else:
        # Run all logins
        helper.run_all()

if __name__ == '__main__':
    main()
