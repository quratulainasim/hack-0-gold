#!/usr/bin/env python3
"""
LinkedIn OAuth Setup Script

Generates LinkedIn access token using OAuth 2.0 flow.
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import json
from pathlib import Path

# CONFIGURATION - Update these with your LinkedIn app credentials
# Get these from: https://www.linkedin.com/developers/apps
CLIENT_ID = "YOUR_LINKEDIN_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_LINKEDIN_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://localhost:8080/callback"

# OAuth URLs
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Scopes - what permissions we're requesting
SCOPES = "openid profile email w_member_social"

class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP server to receive OAuth callback."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle OAuth callback."""
        print(f"\n[DEBUG] Received callback: {self.path}")

        query = urlparse(self.path).query
        params = parse_qs(query)

        print(f"[DEBUG] Query string: {query}")
        print(f"[DEBUG] Parsed params: {params}")

        # Check for errors first
        if 'error' in params:
            error = params['error'][0]
            error_desc = params.get('error_description', ['No description'])[0]
            print(f"\n[ERROR] LinkedIn returned an error:")
            print(f"  Error: {error}")
            print(f"  Description: {error_desc}")

            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: #DC143C;">OAuth Error</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_desc}</p>
                    <p>Please check your LinkedIn app configuration.</p>
                </body>
                </html>
            """.encode())
            return

        if 'code' in params:
            code = params['code'][0]
            print("\n[OK] Authorization code received")
            print("[INFO] Exchanging code for access token...")

            # Exchange code for token
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }

            try:
                response = requests.post(TOKEN_URL, data=token_data)
                token_info = response.json()

                if 'access_token' in token_info:
                    print("\n" + "="*60)
                    print("SUCCESS! LinkedIn Access Token Generated")
                    print("="*60)
                    print(f"\nAccess Token: {token_info['access_token']}")
                    print(f"Expires In: {token_info.get('expires_in', 'N/A')} seconds")
                    print(f"           ({token_info.get('expires_in', 0) // 86400} days)")
                    print("\n" + "="*60)

                    # Save to config file
                    self.save_token(token_info['access_token'])

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"""
                        <html>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1 style="color: #0077B5;">Success!</h1>
                            <p>LinkedIn access token generated successfully.</p>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                        </html>
                    """)
                else:
                    print(f"\n[ERROR] Failed to get access token: {token_info}")
                    self.send_response(400)
                    self.end_headers()

            except Exception as e:
                print(f"\n[ERROR] Exception during token exchange: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            print("\n[ERROR] No authorization code received")
            self.send_response(400)
            self.end_headers()

    def save_token(self, access_token):
        """Save access token to mcp_config.json."""
        try:
            config_path = Path('.claude/mcp_config.json')

            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}

            # Add LinkedIn configuration
            config['mcpServers']['linkedin'] = {
                "command": "python",
                "args": [".claude/skills/executor/linkedin_api.py"],
                "env": {
                    "LINKEDIN_ACCESS_TOKEN": access_token,
                    "LINKEDIN_CLIENT_ID": CLIENT_ID,
                    "LINKEDIN_CLIENT_SECRET": CLIENT_SECRET
                },
                "description": "LinkedIn API for posting and messaging"
            }

            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"\n[OK] Token saved to {config_path}")
            print("[INFO] LinkedIn integration is now configured!")

        except Exception as e:
            print(f"\n[WARN] Could not save token to config: {e}")
            print("[INFO] Please manually add the token to .claude/mcp_config.json")


def main():
    """Main entry point."""
    print("="*60)
    print("LinkedIn OAuth Setup")
    print("="*60)
    print()

    # Check if credentials are configured
    if CLIENT_ID == "your-linkedin-client-id-here":
        print("[ERROR] LinkedIn credentials not configured!")
        print()
        print("Please follow these steps:")
        print()
        print("1. Go to https://www.linkedin.com/developers/")
        print("2. Click 'Create App'")
        print("3. Fill in app details:")
        print("   - App name: Multi-Agent Workflow System")
        print("   - LinkedIn Page: Your company page")
        print("   - App logo: Upload a logo")
        print()
        print("4. In the 'Auth' tab, add redirect URL:")
        print("   http://localhost:8080/callback")
        print()
        print("5. Copy your Client ID and Client Secret")
        print()
        print("6. Edit this script (linkedin_oauth_setup.py):")
        print("   - Update CLIENT_ID with your Client ID")
        print("   - Update CLIENT_SECRET with your Client Secret")
        print()
        print("7. Run this script again")
        print()
        return

    # Build authorization URL
    auth_params = f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    auth_url = f"{AUTH_URL}?{auth_params}"

    print("[INFO] Opening browser for LinkedIn authorization...")
    print()
    print("If browser doesn't open automatically, visit:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("[INFO] Starting local server on http://localhost:8080")
    print("[INFO] Waiting for authorization callback...")
    print()

    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server.handle_request()

    print()
    print("[INFO] OAuth flow complete!")
    print()


if __name__ == "__main__":
    main()
