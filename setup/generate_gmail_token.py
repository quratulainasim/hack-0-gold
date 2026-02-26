#!/usr/bin/env python3
"""
Gmail OAuth Token Generator

Generates a refresh token for Gmail API access using localhost redirect.
"""

import json
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Your OAuth credentials
# Get these from: https://console.cloud.google.com/apis/credentials
CLIENT_ID = "YOUR_GMAIL_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_GMAIL_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://localhost:8080"

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Global variable to store authorization code
auth_code = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Google."""

    def do_GET(self):
        """Handle GET request with authorization code."""
        global auth_code

        # Parse the authorization code from URL
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            auth_code = params['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            success_html = """
            <html>
            <head><title>Authorization Successful</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            error_html = """
            <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">✗ Authorization Failed</h1>
                <p>No authorization code received.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def get_authorization_code():
    """Open browser for user authorization and capture code."""
    # Build authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

    print("=" * 70)
    print("Gmail OAuth Token Generator")
    print("=" * 70)
    print()
    print("Step 1: Opening browser for authorization...")
    print()
    print("If browser doesn't open automatically, visit this URL:")
    print(auth_url)
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("Step 2: Waiting for authorization...")
    print("(A local server is running on http://localhost:8080)")
    print()

    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)

    # Wait for one request (the OAuth callback)
    server.handle_request()

    return auth_code


def exchange_code_for_tokens(code):
    """Exchange authorization code for access and refresh tokens."""
    import urllib.request

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    # Encode data
    data_encoded = urlencode(data).encode('utf-8')

    # Make request
    req = urllib.request.Request(token_url, data=data_encoded, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"Error exchanging code for tokens: {e}")
        return None


def main():
    """Main function."""
    # Get authorization code
    code = get_authorization_code()

    if not code:
        print("✗ Failed to get authorization code")
        sys.exit(1)

    print("✓ Authorization code received")
    print()

    # Exchange code for tokens
    print("Step 3: Exchanging code for tokens...")
    tokens = exchange_code_for_tokens(code)

    if not tokens:
        print("✗ Failed to exchange code for tokens")
        sys.exit(1)

    if 'refresh_token' not in tokens:
        print("✗ No refresh token received")
        print("This might happen if you've already authorized this app.")
        print("Try revoking access at: https://myaccount.google.com/permissions")
        sys.exit(1)

    # Display results
    print("✓ Tokens received successfully!")
    print()
    print("=" * 70)
    print("Your Gmail Refresh Token")
    print("=" * 70)
    print()
    print(tokens['refresh_token'])
    print()
    print("=" * 70)
    print()
    print("Copy the refresh token above and update your .claude/mcp_config.json file:")
    print()
    print('  "GMAIL_REFRESH_TOKEN": "' + tokens['refresh_token'] + '"')
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
