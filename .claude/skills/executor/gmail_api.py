#!/usr/bin/env python3
"""
Gmail API Integration Module

Direct Gmail API integration using OAuth credentials.
Provides email sending functionality for the executor.
"""

import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import urllib.request
import urllib.parse


class GmailAPI:
    """Gmail API client using OAuth 2.0."""

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        """
        Initialize Gmail API client.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            refresh_token: OAuth refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None

    def get_access_token(self) -> str:
        """
        Get a fresh access token using the refresh token.

        Returns:
            Access token string
        """
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(token_url, data=data_encoded, method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.access_token = result['access_token']
                return self.access_token
        except Exception as e:
            raise Exception(f"Failed to get access token: {e}")

    def create_message(self, to: str, subject: str, body: str,
                      cc: Optional[str] = None,
                      bcc: Optional[str] = None) -> Dict:
        """
        Create an email message.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Message dictionary ready for sending
        """
        message = MIMEMultipart('alternative')
        message['To'] = to
        message['Subject'] = subject

        if cc:
            message['Cc'] = cc
        if bcc:
            message['Bcc'] = bcc

        # Add plain text part
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        return {'raw': raw_message}

    def send_message(self, to: str, subject: str, body: str,
                    cc: Optional[str] = None,
                    bcc: Optional[str] = None) -> Dict:
        """
        Send an email message.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Response dictionary with message ID and status
        """
        # Get fresh access token
        if not self.access_token:
            self.get_access_token()

        # Create message
        message = self.create_message(to, subject, body, cc, bcc)

        # Send via Gmail API
        send_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(send_url, data=data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return {
                    'success': True,
                    'message_id': result.get('id'),
                    'thread_id': result.get('threadId'),
                    'label_ids': result.get('labelIds', [])
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {
                'success': False,
                'error': f"HTTP {e.code}: {error_body}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def load_gmail_credentials(config_path: Path) -> Dict[str, str]:
    """
    Load Gmail credentials from MCP config file.

    Args:
        config_path: Path to mcp_config.json

    Returns:
        Dictionary with client_id, client_secret, refresh_token
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    gmail_config = config['mcpServers']['gmail']['env']

    return {
        'client_id': gmail_config['GMAIL_CLIENT_ID'],
        'client_secret': gmail_config['GMAIL_CLIENT_SECRET'],
        'refresh_token': gmail_config['GMAIL_REFRESH_TOKEN']
    }


def send_email(to: str, subject: str, body: str,
               cc: Optional[str] = None,
               bcc: Optional[str] = None,
               config_path: Optional[Path] = None) -> Dict:
    """
    Send an email using Gmail API.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        config_path: Path to mcp_config.json (optional)

    Returns:
        Response dictionary with success status and details
    """
    # Default config path
    if not config_path:
        config_path = Path(__file__).parent.parent.parent / 'mcp_config.json'

    # Load credentials
    try:
        creds = load_gmail_credentials(config_path)
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to load credentials: {e}"
        }

    # Create Gmail API client
    gmail = GmailAPI(
        client_id=creds['client_id'],
        client_secret=creds['client_secret'],
        refresh_token=creds['refresh_token']
    )

    # Send email
    return gmail.send_message(to, subject, body, cc, bcc)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python gmail_api.py <to> <subject> <body>")
        sys.exit(1)

    to_addr = sys.argv[1]
    subject_text = sys.argv[2]
    body_text = sys.argv[3]

    print(f"Sending email to: {to_addr}")
    print(f"Subject: {subject_text}")
    print()

    result = send_email(to_addr, subject_text, body_text)

    if result['success']:
        print(f"[OK] Email sent successfully!")
        print(f"Message ID: {result['message_id']}")
    else:
        print(f"[ERROR] Failed to send email:")
        print(f"{result['error']}")
        sys.exit(1)
