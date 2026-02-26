#!/usr/bin/env python3
"""
LinkedIn OAuth Setup
Regenerate LinkedIn access token with correct permissions for posting
"""
import os
import webbrowser
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

# LinkedIn OAuth credentials from .env
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/callback'

# Required scopes for posting
SCOPES = 'r_liteprofile w_member_social'

class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    
    def do_GET(self):
        """Handle the OAuth callback"""
        if self.path.startswith('/callback'):
            # Parse authorization code
            query = self.path.split('?')[1] if '?' in self.path else ''
            params = parse_qs(query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                
                # Exchange code for access token
                token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
                token_data = {
                    'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': REDIRECT_URI,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                }
                
                response = requests.post(token_url, data=token_data)
                
                if response.status_code == 200:
                    token_info = response.json()
                    access_token = token_info['access_token']
                    expires_in = token_info.get('expires_in', 5184000)  # 60 days default
                    
                    # Save to .env file
                    env_path = '.env'
                    set_key(env_path, 'LINKEDIN_ACCESS_TOKEN', access_token)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = f"""
                    <html>
                    <head><title>LinkedIn OAuth Success</title></head>
                    <body style="font-family: Arial; padding: 50px; text-align: center;">
                        <h1 style="color: green;">✓ LinkedIn Authentication Successful!</h1>
                        <p>Access token has been saved to .env file</p>
                        <p>Token expires in: {expires_in // 86400} days</p>
                        <p><strong>You can close this window and return to the terminal.</strong></p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    
                    print("\n" + "="*60)
                    print("✓ SUCCESS! LinkedIn access token saved to .env")
                    print(f"Token expires in: {expires_in // 86400} days")
                    print("="*60)
                    print("\nYou can now run: python executors/master_orchestrator.py --process-all")
                    
                else:
                    self.send_error(500, f"Token exchange failed: {response.text}")
            else:
                self.send_error(400, "No authorization code received")
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    """Main OAuth flow"""
    print("="*60)
    print("LinkedIn OAuth Setup")
    print("="*60)
    print(f"Client ID: {CLIENT_ID}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scopes: {SCOPES}")
    print("="*60)
    
    # Build authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    
    print("\nStep 1: Opening LinkedIn authorization page in your browser...")
    print("Step 2: Log in and authorize the application")
    print("Step 3: You'll be redirected back automatically")
    print("\nStarting local server on http://localhost:8080...")
    
    # Start local server
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("\nWaiting for authorization...")
    print("(The browser will open automatically)")
    
    # Handle one request (the callback)
    server.handle_request()
    
    print("\nServer stopped.")

if __name__ == "__main__":
    main()
