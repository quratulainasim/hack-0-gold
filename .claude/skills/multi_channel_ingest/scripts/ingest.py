#!/usr/bin/env python3
"""
Multi-Channel Communication Ingest Script
Converts communications from various channels into standardized Markdown format.
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import html


class ChannelIngestor:
    """Base class for channel-specific ingestors"""

    PRIORITY_HIGH_KEYWORDS = ['urgent', 'asap', 'important', 'critical', 'emergency', 'immediately']
    PRIORITY_MEDIUM_KEYWORDS = ['?', 'please', 'could you', 'would you', 'follow up', 'reminder']

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or './Inbox'
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def detect_priority(self, content: str, subject: str = '') -> str:
        """Detect message priority based on content"""
        text = (content + ' ' + subject).lower()

        if any(keyword in text for keyword in self.PRIORITY_HIGH_KEYWORDS):
            return 'high'
        elif any(keyword in text for keyword in self.PRIORITY_MEDIUM_KEYWORDS):
            return 'medium'
        else:
            return 'low'

    def html_to_markdown(self, html_content: str) -> str:
        """Basic HTML to Markdown conversion"""
        # Remove HTML tags but preserve structure
        text = html.unescape(html_content)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text)
        text = re.sub(r'<b>(.*?)</b>', r'**\1**', text)
        text = re.sub(r'<em>(.*?)</em>', r'*\1*', text)
        text = re.sub(r'<i>(.*?)</i>', r'*\1*', text)
        text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def generate_markdown(self, data: Dict) -> str:
        """Generate standardized Markdown output"""
        frontmatter = f"""---
type: {data['type']}
channel: {data['channel']}
sender: {data['sender']}
sender_id: {data['sender_id']}
received: {data['received']}
priority: {data['priority']}
status: new
---

# {data['subject']}

{data['content']}
"""

        if data.get('metadata'):
            frontmatter += "\n## Metadata\n"
            for key, value in data['metadata'].items():
                frontmatter += f"- **{key}**: {value}\n"

        return frontmatter

    def save_markdown(self, markdown: str, filename: str):
        """Save Markdown to output directory"""
        filepath = Path(self.output_dir) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Saved: {filepath}")


class GmailIngestor(ChannelIngestor):
    """Process Gmail messages"""

    def process(self, input_file: str):
        """Process Gmail JSON export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both single message and array
        messages = data if isinstance(data, list) else [data]

        for msg in messages:
            content = self.html_to_markdown(msg.get('body', msg.get('snippet', '')))
            subject = msg.get('subject', 'No Subject')

            markdown_data = {
                'type': 'email',
                'channel': 'Gmail',
                'sender': msg.get('from', {}).get('name', msg.get('from', 'Unknown')),
                'sender_id': msg.get('from', {}).get('email', ''),
                'received': msg.get('date', datetime.now().isoformat()),
                'priority': self.detect_priority(content, subject),
                'subject': subject,
                'content': content,
                'metadata': {
                    'Thread ID': msg.get('threadId', 'N/A'),
                    'Message ID': msg.get('id', 'N/A'),
                    'Attachments': ', '.join([a.get('filename', '') for a in msg.get('attachments', [])])
                }
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"email_{timestamp}_{msg.get('id', 'unknown')[:8]}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


class LinkedInIngestor(ChannelIngestor):
    """Process LinkedIn messages and notifications"""

    def process(self, input_file: str):
        """Process LinkedIn JSON export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = data if isinstance(data, list) else [data]

        for msg in messages:
            msg_type = msg.get('type', 'message')
            content = msg.get('content', msg.get('text', ''))

            markdown_data = {
                'type': 'linkedin',
                'channel': f"LinkedIn {msg_type.title()}",
                'sender': msg.get('sender', {}).get('name', msg.get('from', 'Unknown')),
                'sender_id': msg.get('sender', {}).get('profileUrl', ''),
                'received': msg.get('timestamp', datetime.now().isoformat()),
                'priority': self.detect_priority(content),
                'subject': msg.get('subject', f"LinkedIn {msg_type}"),
                'content': content,
                'metadata': {
                    'Profile URL': msg.get('sender', {}).get('profileUrl', 'N/A'),
                    'Company': msg.get('sender', {}).get('company', 'N/A'),
                    'Conversation ID': msg.get('conversationId', 'N/A')
                }
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"linkedin_{timestamp}_{msg.get('id', 'unknown')[:8]}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


class TwitterIngestor(ChannelIngestor):
    """Process Twitter/X messages and tweets"""

    def process(self, input_file: str):
        """Process Twitter JSON export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tweets = data if isinstance(data, list) else [data]

        for tweet in tweets:
            content = tweet.get('text', tweet.get('full_text', ''))

            markdown_data = {
                'type': 'twitter',
                'channel': 'Twitter/X',
                'sender': tweet.get('user', {}).get('name', tweet.get('author', 'Unknown')),
                'sender_id': f"@{tweet.get('user', {}).get('screen_name', '')}",
                'received': tweet.get('created_at', datetime.now().isoformat()),
                'priority': self.detect_priority(content),
                'subject': f"Tweet from @{tweet.get('user', {}).get('screen_name', 'unknown')}",
                'content': content,
                'metadata': {
                    'Tweet ID': tweet.get('id_str', 'N/A'),
                    'Retweets': tweet.get('retweet_count', 0),
                    'Likes': tweet.get('favorite_count', 0),
                    'Media': ', '.join([m.get('media_url', '') for m in tweet.get('entities', {}).get('media', [])])
                }
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"twitter_{timestamp}_{tweet.get('id_str', 'unknown')[:8]}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


class FacebookIngestor(ChannelIngestor):
    """Process Facebook messages and posts"""

    def process(self, input_file: str):
        """Process Facebook JSON export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = data if isinstance(data, list) else [data]

        for msg in messages:
            content = msg.get('message', msg.get('text', ''))

            markdown_data = {
                'type': 'facebook',
                'channel': 'Facebook',
                'sender': msg.get('sender_name', msg.get('from', 'Unknown')),
                'sender_id': msg.get('sender_id', ''),
                'received': msg.get('timestamp_ms', datetime.now().timestamp() * 1000),
                'priority': self.detect_priority(content),
                'subject': f"Facebook message from {msg.get('sender_name', 'Unknown')}",
                'content': content,
                'metadata': {
                    'Thread': msg.get('thread_path', 'N/A'),
                    'Reactions': ', '.join([r.get('reaction', '') for r in msg.get('reactions', [])])
                }
            }

            # Convert timestamp
            if isinstance(markdown_data['received'], (int, float)):
                markdown_data['received'] = datetime.fromtimestamp(
                    markdown_data['received'] / 1000
                ).isoformat()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"facebook_{timestamp}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


class WhatsAppIngestor(ChannelIngestor):
    """Process WhatsApp chat exports"""

    def process(self, input_file: str):
        """Process WhatsApp text export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse WhatsApp export format: [date, time] sender: message
        pattern = r'\[?(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s+[AP]M)?)\]?\s+-?\s+([^:]+):\s+(.+?)(?=\n\[?\d{1,2}/\d{1,2}/|\Z)'
        messages = re.findall(pattern, content, re.DOTALL)

        for timestamp_str, sender, message in messages:
            markdown_data = {
                'type': 'whatsapp',
                'channel': 'WhatsApp',
                'sender': sender.strip(),
                'sender_id': sender.strip(),
                'received': timestamp_str,
                'priority': self.detect_priority(message),
                'subject': f"WhatsApp from {sender.strip()}",
                'content': message.strip(),
                'metadata': {}
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"whatsapp_{timestamp}_{sender.strip().replace(' ', '_')[:20]}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


class InstagramIngestor(ChannelIngestor):
    """Process Instagram messages and comments"""

    def process(self, input_file: str):
        """Process Instagram JSON export"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = data if isinstance(data, list) else [data]

        for msg in messages:
            content = msg.get('text', msg.get('message', ''))

            markdown_data = {
                'type': 'instagram',
                'channel': 'Instagram',
                'sender': msg.get('sender', {}).get('username', msg.get('from', 'Unknown')),
                'sender_id': f"@{msg.get('sender', {}).get('username', '')}",
                'received': msg.get('timestamp', datetime.now().isoformat()),
                'priority': self.detect_priority(content),
                'subject': f"Instagram from @{msg.get('sender', {}).get('username', 'unknown')}",
                'content': content,
                'metadata': {
                    'Post Reference': msg.get('post_url', 'N/A'),
                    'Media Type': msg.get('media_type', 'N/A')
                }
            }

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"instagram_{timestamp}.md"
            self.save_markdown(self.generate_markdown(markdown_data), filename)


def detect_channel(input_file: str) -> Optional[str]:
    """Auto-detect channel type from file content or name"""
    filename = os.path.basename(input_file).lower()

    # Check filename
    if 'gmail' in filename or 'email' in filename:
        return 'gmail'
    elif 'linkedin' in filename:
        return 'linkedin'
    elif 'twitter' in filename or 'tweet' in filename:
        return 'twitter'
    elif 'facebook' in filename:
        return 'facebook'
    elif 'whatsapp' in filename:
        return 'whatsapp'
    elif 'instagram' in filename:
        return 'instagram'

    # Check file content for JSON files
    if filename.endswith('.json'):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if 'threadId' in data or 'labelIds' in data:
                        return 'gmail'
                    elif 'conversationId' in data or 'profileUrl' in data:
                        return 'linkedin'
                    elif 'tweet' in data or 'screen_name' in data:
                        return 'twitter'
                    elif 'sender_name' in data or 'thread_path' in data:
                        return 'facebook'
        except:
            pass

    # Check for WhatsApp text format
    if filename.endswith('.txt'):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                first_lines = f.read(500)
                if re.search(r'\[\d{1,2}/\d{1,2}/\d{2,4}', first_lines):
                    return 'whatsapp'
        except:
            pass

    return None


def main():
    parser = argparse.ArgumentParser(description='Ingest multi-channel communications to Markdown')
    parser.add_argument('input_file', nargs='?', help='Input file to process')
    parser.add_argument('--output', '-o', default='./Inbox', help='Output directory (default: ./Inbox)')
    parser.add_argument('--channel', '-c', choices=['gmail', 'linkedin', 'twitter', 'facebook', 'whatsapp', 'instagram'],
                       help='Force specific channel type')
    parser.add_argument('--batch', '-b', help='Process all files in directory')

    args = parser.parse_args()

    ingestors = {
        'gmail': GmailIngestor,
        'linkedin': LinkedInIngestor,
        'twitter': TwitterIngestor,
        'facebook': FacebookIngestor,
        'whatsapp': WhatsAppIngestor,
        'instagram': InstagramIngestor
    }

    if args.batch:
        # Batch processing
        for filename in os.listdir(args.batch):
            filepath = os.path.join(args.batch, filename)
            if os.path.isfile(filepath):
                channel = args.channel or detect_channel(filepath)
                if channel and channel in ingestors:
                    print(f"Processing {filename} as {channel}...")
                    ingestor = ingestors[channel](args.output)
                    try:
                        ingestor.process(filepath)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
    elif args.input_file:
        # Single file processing
        channel = args.channel or detect_channel(args.input_file)

        if not channel:
            print("Could not detect channel type. Use --channel to specify.")
            return

        if channel not in ingestors:
            print(f"Unsupported channel: {channel}")
            return

        print(f"Processing as {channel}...")
        ingestor = ingestors[channel](args.output)
        ingestor.process(args.input_file)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
