#!/usr/bin/env python3
"""
Generate Gmail token.pickle file from .env credentials
"""

import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

# Load .env
load_dotenv()

# Get credentials from .env
client_id = os.getenv('GMAIL_CLIENT_ID')
client_secret = os.getenv('GMAIL_CLIENT_SECRET')
refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

print("=" * 60)
print("Gmail Token Generator")
print("=" * 60)
print()

if not all([client_id, client_secret, refresh_token]):
    print("[ERROR] Missing Gmail credentials in .env file")
    print()
    print("Required:")
    print("  GMAIL_CLIENT_ID")
    print("  GMAIL_CLIENT_SECRET")
    print("  GMAIL_REFRESH_TOKEN")
    exit(1)

print("[OK] Found Gmail credentials in .env")
print(f"  Client ID: {client_id[:20]}...")
print(f"  Refresh Token: {refresh_token[:20]}...")
print()

# Create credentials object
creds = Credentials(
    token=None,
    refresh_token=refresh_token,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=client_id,
    client_secret=client_secret,
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

# Create config directory if it doesn't exist
config_dir = Path('config')
config_dir.mkdir(exist_ok=True)

# Save token
token_path = config_dir / 'gmail_token.pickle'
with open(token_path, 'wb') as token:
    pickle.dump(creds, token)

print(f"[OK] Created: {token_path}")
print()
print("Gmail watcher can now access your Gmail account!")
print()
print("Next steps:")
print("  1. Restart Gmail watcher: pm2 restart gmail-sentinel")
print("  2. Check logs: pm2 logs gmail-sentinel")
print("  3. Send test email with 'urgent' in subject")
print("  4. Wait 5 minutes for watcher to check")
print()
print("=" * 60)
