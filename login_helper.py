from playwright.sync_api import sync_playwright
import time

platform = input("Enter platform to login (instagram/whatsapp/twitter): ")

with sync_playwright() as p:
    session_dir = f'D:/Hackathon-0/Gold-Tier/browser_sessions/{platform}_session'

    if platform == 'instagram':
        url = 'https://www.instagram.com/direct/inbox/'
    elif platform == 'whatsapp':
        url = 'https://web.whatsapp.com/'
    else:
        url = 'https://twitter.com/messages'

    print(f"\n=== Opening {platform} for login ===")
    print("1. The browser will open")
    print("2. Log in manually if needed")
    print("3. Navigate to your messages/inbox")
    print("4. Wait for everything to load")
    print("5. Press Enter here when done\n")

    browser = p.chromium.launch_persistent_context(
        user_data_dir=session_dir,
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    page = browser.pages[0]
    page.goto(url, wait_until='domcontentloaded')

    input("\nPress Enter after you've logged in and see your conversations...")

    print("\n=== Verifying login ===")
    all_text = page.inner_text('body')

    if platform == 'instagram' and 'Log into Instagram' in all_text:
        print("❌ Still on login page - please log in first")
    elif platform == 'whatsapp' and 'WhatsApp Web' in all_text:
        print("✓ WhatsApp loaded")
    elif platform == 'twitter':
        print("✓ Twitter loaded")
    else:
        print("✓ Session appears to be logged in")

    print(f"\nSession saved to: {session_dir}")
    print("You can now close the browser or press Enter to close...")
    input()
