#!/usr/bin/env python3
"""
LinkedIn API Wrapper

Provides functions to interact with LinkedIn API:
- Fetch notifications
- Post updates
- Send messages
- Comment on posts
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# LinkedIn API endpoints
API_BASE = "https://api.linkedin.com/v2"
NOTIFICATIONS_ENDPOINT = f"{API_BASE}/notifications"
POSTS_ENDPOINT = f"{API_BASE}/ugcPosts"
SHARES_ENDPOINT = f"{API_BASE}/shares"
MESSAGES_ENDPOINT = f"{API_BASE}/messages"

class LinkedInAPI:
    """LinkedIn API client."""

    def __init__(self, access_token: str):
        """
        Initialize LinkedIn API client.

        Args:
            access_token: LinkedIn OAuth access token
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def get_profile(self) -> Dict:
        """
        Get current user's profile using OpenID Connect.

        Returns:
            Profile data dictionary
        """
        try:
            # Use OpenID Connect userinfo endpoint
            url = "https://api.linkedin.com/v2/userinfo"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get profile: {e}")
            return {}

    def post_update(self, text: str) -> Dict:
        """
        Post a text update to LinkedIn.

        Args:
            text: Text content to post

        Returns:
            Response data dictionary
        """
        try:
            # Get user profile ID (using OpenID Connect 'sub' field)
            profile = self.get_profile()
            person_id = profile.get('sub', '')

            if not person_id:
                return {'success': False, 'error': 'Could not get user profile'}

            # Create post payload
            payload = {
                "author": f"urn:li:person:{person_id}",
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
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(POSTS_ENDPOINT, headers=self.headers, json=payload)

            if response.status_code == 201:
                post_id = response.headers.get('x-restli-id', '')
                return {
                    'success': True,
                    'post_id': post_id,
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'{response.status_code} {response.reason}: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def comment_on_post(self, post_urn: str, comment_text: str) -> Dict:
        """
        Comment on a LinkedIn post.

        Args:
            post_urn: URN of the post to comment on
            comment_text: Comment text

        Returns:
            Response data dictionary
        """
        try:
            # Get user profile ID (using OpenID Connect 'sub' field)
            profile = self.get_profile()
            person_id = profile.get('sub', '')

            if not person_id:
                return {'error': 'Could not get user profile'}

            # Create comment payload
            payload = {
                "actor": f"urn:li:person:{person_id}",
                "object": post_urn,
                "message": {
                    "text": comment_text
                }
            }

            url = f"{API_BASE}/socialActions/{post_urn}/comments"
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            return {
                'success': True,
                'comment_id': response.headers.get('X-RestLi-Id', ''),
                'response': response.json()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_message(self, recipient_urn: str, message_text: str) -> Dict:
        """
        Send a direct message on LinkedIn.

        Args:
            recipient_urn: URN of the recipient
            message_text: Message text

        Returns:
            Response data dictionary
        """
        try:
            # Get user profile ID (using OpenID Connect 'sub' field)
            profile = self.get_profile()
            person_id = profile.get('sub', '')

            if not person_id:
                return {'error': 'Could not get user profile'}

            # Create message payload
            payload = {
                "recipients": [recipient_urn],
                "subject": "Message",
                "body": message_text
            }

            response = requests.post(MESSAGES_ENDPOINT, headers=self.headers, json=payload)
            response.raise_for_status()

            return {
                'success': True,
                'message_id': response.headers.get('X-RestLi-Id', ''),
                'response': response.json()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_notifications(self, count: int = 20) -> List[Dict]:
        """
        Get recent LinkedIn notifications.

        Args:
            count: Number of notifications to fetch

        Returns:
            List of notification dictionaries
        """
        try:
            url = f"{NOTIFICATIONS_ENDPOINT}?count={count}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data.get('elements', [])

        except Exception as e:
            print(f"[ERROR] Failed to get notifications: {e}")
            return []


def main():
    """Main entry point for testing."""
    access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')

    if not access_token:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN environment variable not set")
        sys.exit(1)

    api = LinkedInAPI(access_token)

    # Test connection
    print("Testing LinkedIn API connection...")
    profile = api.get_profile()

    if profile:
        print(f"[OK] Connected as: {profile.get('localizedFirstName', 'Unknown')} {profile.get('localizedLastName', '')}")
    else:
        print("[ERROR] Failed to connect to LinkedIn API")
        sys.exit(1)

    # Get notifications
    print("\nFetching notifications...")
    notifications = api.get_notifications()
    print(f"[OK] Found {len(notifications)} notifications")


if __name__ == '__main__':
    main()
