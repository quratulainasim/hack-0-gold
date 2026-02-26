#!/usr/bin/env python3
"""
LinkedIn Session Setup
Run this once to log into LinkedIn and save the session
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

project_root = Path(__file__).parent
session_path = project_root / '.linkedin_browser_data'

print("Opening LinkedIn for manual login...")
print("Please log in to your LinkedIn account in the browser window.")
print("After logging in successfully, press Enter here to save the session.")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(session_path),
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    page = context.pages[0]
    page.goto('https://www.linkedin.com/feed/')
    
    input("\nPress Enter after you've logged in successfully...")
    
    print("Session saved! You can now use the master orchestrator.")
    context.close()
