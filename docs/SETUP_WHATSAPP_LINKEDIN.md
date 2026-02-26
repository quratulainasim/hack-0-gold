# WhatsApp & LinkedIn Integration Setup Guide

This guide will help you set up WhatsApp Web automation and LinkedIn API integration for your Multi-Agent Workflow System.

---

## WhatsApp Web Setup

### Prerequisites

1. **Install Playwright**
```bash
pip install playwright
playwright install chromium
```

2. **Verify Installation**
```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully')"
```

### Initial Setup (One-Time)

1. **Run WhatsApp Watcher for First Time**
```bash
python whatsapp_watcher.py
```

2. **Scan QR Code**
   - A browser window will open showing WhatsApp Web
   - Open WhatsApp on your phone
   - Go to Settings > Linked Devices > Link a Device
   - Scan the QR code displayed in the browser
   - Wait for WhatsApp Web to load completely

3. **Session Persistence**
   - Your session is saved in `.whatsapp_browser_data/` folder
   - You won't need to scan QR code again unless you log out
   - The browser profile persists across restarts

### Running WhatsApp Watcher

**Manual Mode (with visible browser):**
```bash
python whatsapp_watcher.py
```

**Background Mode (headless):**
Edit `whatsapp_watcher.py` line 368:
```python
headless=True,  # Change from False to True
```

Then run:
```bash
python whatsapp_watcher.py
```

### How It Works

1. **Monitoring**: Scans WhatsApp Web every 60 seconds for unread messages
2. **Priority Detection**: Identifies messages with keywords: urgent, asap, payment, lead, meeting
3. **Inbox Creation**: Creates structured markdown files in `/Inbox` folder
4. **Deduplication**: Tracks processed messages in `.whatsapp_processed.json`

### Configuration

**Change Check Interval:**
Edit `whatsapp_watcher.py` line 455:
```python
monitor_whatsapp(vault_path, user_data_dir, check_interval=300)  # 5 minutes
```

**Add Priority Keywords:**
Edit `whatsapp_watcher.py` lines 63-67:
```python
high_priority_keywords = [
    'urgent', 'asap', 'payment', 'lead', 'meeting',
    'deadline', 'important', 'critical', 'client',
    'proposal', 'contract', 'emergency',
    'your-custom-keyword'  # Add your keywords here
]
```

### Testing WhatsApp Integration

1. Send yourself a test message on WhatsApp containing "urgent test"
2. Run the watcher: `python whatsapp_watcher.py`
3. Check `/Inbox` folder for new markdown file
4. Verify the file contains your message with high priority

---

## LinkedIn Integration Setup

LinkedIn integration requires LinkedIn API access. There are two approaches:

### Option 1: LinkedIn Official API (Recommended for Production)

**Step 1: Create LinkedIn App**

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click "Create App"
3. Fill in app details:
   - App name: "Multi-Agent Workflow System"
   - LinkedIn Page: Your company page
   - App logo: Upload a logo
   - Legal agreement: Accept terms

4. Note your credentials:
   - Client ID
   - Client Secret

**Step 2: Configure OAuth 2.0**

1. In your app settings, go to "Auth" tab
2. Add Redirect URLs:
   ```
   http://localhost:8080/callback
   ```

3. Request API access for these scopes:
   - `r_liteprofile` - Read basic profile
   - `r_emailaddress` - Read email
   - `w_member_social` - Post on behalf of user
   - `r_organization_social` - Read organization posts

**Step 3: Generate Access Token**

Create `linkedin_oauth_setup.py`:

```python
#!/usr/bin/env python3
"""LinkedIn OAuth Setup - Generate Access Token"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

CLIENT_ID = "your-client-id-here"
CLIENT_SECRET = "your-client-secret-here"
REDIRECT_URI = "http://localhost:8080/callback"

# OAuth URLs
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Scopes
SCOPES = "r_liteprofile r_emailaddress w_member_social r_organization_social"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            code = params['code'][0]

            # Exchange code for token
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }

            response = requests.post(TOKEN_URL, data=token_data)
            token_info = response.json()

            if 'access_token' in token_info:
                print("\n" + "="*60)
                print("SUCCESS! LinkedIn Access Token:")
                print("="*60)
                print(f"Access Token: {token_info['access_token']}")
                print(f"Expires In: {token_info.get('expires_in', 'N/A')} seconds")
                print("="*60)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>Success! You can close this window.</h1>")
            else:
                print(f"Error: {token_info}")
                self.send_response(400)
                self.end_headers()

def main():
    # Build authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES
    }

    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}"

    print("Opening browser for LinkedIn authorization...")
    print(f"If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)

    # Start local server to receive callback
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    print("Waiting for authorization callback...")
    server.handle_request()

if __name__ == "__main__":
    main()
```

**Step 4: Update Configuration**

Add to `.claude/mcp_config.json`:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "python",
      "args": [".claude/skills/executor/linkedin_api.py"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your-access-token-here",
        "LINKEDIN_CLIENT_ID": "your-client-id-here",
        "LINKEDIN_CLIENT_SECRET": "your-client-secret-here"
      },
      "description": "LinkedIn API for posting and messaging"
    }
  }
}
```

### Option 2: Browser Automation (Quick Start)

For testing or if you don't have API access, use Playwright automation:

**Step 1: Install Dependencies**
```bash
pip install playwright
playwright install chromium
```

**Step 2: Run LinkedIn Watcher**
```bash
python linkedin_watcher.py
```

**Step 3: Manual Login**
- Browser opens to LinkedIn
- Log in manually (one-time)
- Session persists in browser profile

**Note**: Browser automation is less reliable than official API and may violate LinkedIn's Terms of Service. Use only for testing.

---

## LinkedIn API Implementation

Create `linkedin_api.py` for direct API integration:

```python
#!/usr/bin/env python3
"""LinkedIn API Integration"""

import os
import requests
from typing import Dict, Optional

class LinkedInAPI:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.environ.get('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def get_profile(self) -> Dict:
        """Get user profile information."""
        url = f"{self.base_url}/me"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_post(self, text: str, visibility: str = "PUBLIC") -> Dict:
        """
        Create a LinkedIn post.

        Args:
            text: Post content
            visibility: PUBLIC or CONNECTIONS

        Returns:
            Response with post ID
        """
        profile = self.get_profile()
        person_urn = f"urn:li:person:{profile['id']}"

        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        url = f"{self.base_url}/ugcPosts"
        response = requests.post(url, headers=self.headers, json=post_data)
        return response.json()

    def send_message(self, recipient_urn: str, message: str) -> Dict:
        """
        Send a LinkedIn message.

        Args:
            recipient_urn: LinkedIn URN of recipient
            message: Message content

        Returns:
            Response with message ID
        """
        # Note: Requires messaging API access
        url = f"{self.base_url}/messages"
        message_data = {
            "recipients": [recipient_urn],
            "subject": "Message",
            "body": message
        }

        response = requests.post(url, headers=self.headers, json=message_data)
        return response.json()

def create_post(text: str, visibility: str = "PUBLIC") -> Dict:
    """Helper function to create LinkedIn post."""
    api = LinkedInAPI()
    return api.create_post(text, visibility)

def send_message(recipient_urn: str, message: str) -> Dict:
    """Helper function to send LinkedIn message."""
    api = LinkedInAPI()
    return api.send_message(recipient_urn, message)
```

---

## Testing Your Setup

### Test WhatsApp Integration

```bash
# Terminal 1: Start WhatsApp watcher
python whatsapp_watcher.py

# Terminal 2: Send test message to yourself
# Message should contain: "urgent test message"

# Check Inbox folder
ls -la Inbox/WA_*
```

### Test LinkedIn Integration

```bash
# Test LinkedIn API connection
python -c "from linkedin_api import LinkedInAPI; api = LinkedInAPI(); print(api.get_profile())"

# Test LinkedIn watcher
python linkedin_watcher.py
```

---

## Troubleshooting

### WhatsApp Issues

**Problem**: QR code doesn't appear
- Solution: Check if Chromium is installed: `playwright install chromium`

**Problem**: Session expires frequently
- Solution: Don't log out from WhatsApp Web manually
- Keep `.whatsapp_browser_data/` folder intact

**Problem**: Messages not detected
- Solution: Check priority keywords match your messages
- Verify unread badge is visible in WhatsApp Web

### LinkedIn Issues

**Problem**: Access token expired
- Solution: LinkedIn tokens expire after 60 days
- Re-run OAuth setup to get new token

**Problem**: API rate limits
- Solution: LinkedIn has rate limits (varies by endpoint)
- Implement exponential backoff in API calls

**Problem**: Missing API permissions
- Solution: Request additional scopes in LinkedIn app settings
- May require LinkedIn review for certain permissions

---

## Production Deployment

### Running as Background Services

**WhatsApp Watcher (Linux/Mac):**
```bash
# Create systemd service
sudo nano /etc/systemd/system/whatsapp-watcher.service
```

```ini
[Unit]
Description=WhatsApp Watcher Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Silver-Tier
ExecStart=/usr/bin/python3 whatsapp_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable whatsapp-watcher
sudo systemctl start whatsapp-watcher
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `D:\Hackathon-0\Silver-Tier\whatsapp_watcher.py`

---

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate access tokens** regularly
4. **Monitor API usage** to detect anomalies
5. **Keep browser sessions** secure (don't share `.whatsapp_browser_data/`)

---

## Next Steps

1. ✅ Set up WhatsApp Web automation
2. ✅ Configure LinkedIn API credentials
3. ✅ Test both integrations
4. ✅ Run watchers in background
5. ✅ Monitor Dashboard for incoming items
6. ✅ Process items through workflow

Your Multi-Agent Workflow System is now ready for continuous operation!
