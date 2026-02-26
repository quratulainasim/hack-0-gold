#!/usr/bin/env python3
"""
Social Media Sentiment Analysis Script
Aggregates mentions from X/Twitter, Facebook, and Instagram into sentiment reports.
"""

import argparse
import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import csv


class SentimentAnalyzer:
    """Analyze sentiment of social media mentions"""

    POSITIVE_KEYWORDS = [
        'love', 'great', 'awesome', 'excellent', 'amazing', 'fantastic', 'wonderful',
        'perfect', 'best', 'thank', 'thanks', 'appreciate', 'brilliant', 'outstanding',
        'superb', 'incredible', 'impressed', 'happy', 'delighted', 'satisfied'
    ]

    NEGATIVE_KEYWORDS = [
        'hate', 'terrible', 'awful', 'horrible', 'worst', 'disappointed', 'frustrat',
        'angry', 'upset', 'broken', 'useless', 'waste', 'poor', 'bad', 'sucks',
        'annoying', 'pathetic', 'ridiculous', 'unacceptable', 'disgust'
    ]

    POSITIVE_EMOJIS = ['😊', '😃', '😄', '❤️', '💕', '👍', '🎉', '⭐', '✨', '🙌', '👏', '💯']
    NEGATIVE_EMOJIS = ['😠', '😡', '👎', '😢', '😞', '😤', '💔', '😩', '🤬', '😭']

    POSITIVE_PATTERNS = [
        r'highly recommend',
        r'best ever',
        r'so happy',
        r'love it',
        r'works great',
        r'exceeded expectations',
        r'can\'t wait',
        r'looking forward'
    ]

    NEGATIVE_PATTERNS = [
        r'doesn\'t work',
        r'does not work',
        r'waste of money',
        r'never again',
        r'not worth',
        r'stay away',
        r'avoid',
        r'regret'
    ]

    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of text
        Returns: (sentiment, confidence_score)
        sentiment: 'positive', 'negative', or 'neutral'
        confidence_score: 0.0 to 1.0
        """
        text_lower = text.lower()

        # Count indicators
        positive_score = 0
        negative_score = 0

        # Check keywords
        for keyword in self.POSITIVE_KEYWORDS:
            positive_score += text_lower.count(keyword)

        for keyword in self.NEGATIVE_KEYWORDS:
            negative_score += text_lower.count(keyword)

        # Check emojis
        for emoji in self.POSITIVE_EMOJIS:
            positive_score += text.count(emoji) * 2  # Emojis weighted higher

        for emoji in self.NEGATIVE_EMOJIS:
            negative_score += text.count(emoji) * 2

        # Check patterns
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, text_lower):
                positive_score += 3  # Patterns weighted highest

        for pattern in self.NEGATIVE_PATTERNS:
            if re.search(pattern, text_lower):
                negative_score += 3

        # Determine sentiment
        if positive_score > negative_score:
            confidence = min(positive_score / (positive_score + negative_score + 1), 1.0)
            return 'positive', confidence
        elif negative_score > positive_score:
            confidence = min(negative_score / (positive_score + negative_score + 1), 1.0)
            return 'negative', confidence
        else:
            return 'neutral', 0.5


class MentionProcessor:
    """Process social media mentions and generate reports"""

    def __init__(self):
        self.analyzer = SentimentAnalyzer()
        self.mentions = []

    def load_markdown_file(self, filepath: str) -> Optional[Dict]:
        """Load mention from Markdown file with frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Extract platform
            channel = metadata.get('channel', metadata.get('type', 'unknown')).lower()
            if 'twitter' in channel or channel == 'twitter':
                platform = 'twitter'
            elif 'facebook' in channel or channel == 'facebook':
                platform = 'facebook'
            elif 'instagram' in channel or channel == 'instagram':
                platform = 'instagram'
            else:
                return None  # Not a supported platform

            return {
                'platform': platform,
                'sender': metadata.get('sender', 'Unknown'),
                'sender_id': metadata.get('sender_id', ''),
                'received': metadata.get('received', ''),
                'content': body,
                'source_file': filepath
            }
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None

    def load_json_file(self, filepath: str) -> Optional[Dict]:
        """Load mention from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Detect platform from data structure
            if 'screen_name' in str(data) or 'tweet' in str(data):
                platform = 'twitter'
                content = data.get('text', data.get('full_text', ''))
                sender = data.get('user', {}).get('name', 'Unknown')
                sender_id = data.get('user', {}).get('screen_name', '')
            elif 'sender_name' in data or 'thread_path' in data:
                platform = 'facebook'
                content = data.get('message', data.get('text', ''))
                sender = data.get('sender_name', 'Unknown')
                sender_id = data.get('sender_id', '')
            elif 'username' in str(data) and 'post_url' in str(data):
                platform = 'instagram'
                content = data.get('text', data.get('message', ''))
                sender = data.get('sender', {}).get('username', 'Unknown')
                sender_id = sender
            else:
                return None

            return {
                'platform': platform,
                'sender': sender,
                'sender_id': sender_id,
                'received': data.get('timestamp', data.get('created_at', data.get('date', ''))),
                'content': content,
                'source_file': filepath
            }
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None

    def load_mentions(self, directory: str, platform_filter: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Load all mentions from directory"""
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)

            if not os.path.isfile(filepath):
                continue

            mention = None
            if filename.endswith('.md'):
                mention = self.load_markdown_file(filepath)
            elif filename.endswith('.json'):
                mention = self.load_json_file(filepath)

            if mention:
                # Apply filters
                if platform_filter and mention['platform'] != platform_filter:
                    continue

                # Analyze sentiment
                sentiment, confidence = self.analyzer.analyze(mention['content'])
                mention['sentiment'] = sentiment
                mention['confidence'] = confidence

                self.mentions.append(mention)

        print(f"Loaded {len(self.mentions)} mentions")

    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total = len(self.mentions)
        if total == 0:
            return {}

        sentiment_counts = Counter(m['sentiment'] for m in self.mentions)
        platform_counts = Counter(m['platform'] for m in self.mentions)

        # Calculate sentiment score (-1 to 1)
        sentiment_score = (sentiment_counts['positive'] - sentiment_counts['negative']) / total

        # Platform breakdown
        by_platform = {}
        for platform in ['twitter', 'facebook', 'instagram']:
            platform_mentions = [m for m in self.mentions if m['platform'] == platform]
            if platform_mentions:
                platform_sentiment = Counter(m['sentiment'] for m in platform_mentions)
                by_platform[platform] = {
                    'total': len(platform_mentions),
                    'positive': platform_sentiment['positive'],
                    'negative': platform_sentiment['negative'],
                    'neutral': platform_sentiment['neutral']
                }

        return {
            'total_mentions': total,
            'positive': sentiment_counts['positive'],
            'negative': sentiment_counts['negative'],
            'neutral': sentiment_counts['neutral'],
            'sentiment_score': round(sentiment_score, 3),
            'by_platform': by_platform
        }

    def get_notable_mentions(self, sentiment: str, limit: int = 5) -> List[Dict]:
        """Get top mentions by sentiment"""
        filtered = [m for m in self.mentions if m['sentiment'] == sentiment]
        sorted_mentions = sorted(filtered, key=lambda x: x['confidence'], reverse=True)
        return sorted_mentions[:limit]

    def extract_themes(self) -> List[Tuple[str, int]]:
        """Extract common themes/keywords from mentions"""
        # Simple word frequency analysis
        words = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'was', 'are', 'been', 'be', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'}

        for mention in self.mentions:
            content_words = re.findall(r'\b[a-z]{4,}\b', mention['content'].lower())
            words.extend([w for w in content_words if w not in stop_words])

        return Counter(words).most_common(10)

    def generate_markdown_report(self, output_file: str):
        """Generate Markdown format report"""
        summary = self.generate_summary()

        if not summary:
            print("No mentions to report")
            return

        report = f"""# Social Media Sentiment Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Total mentions analyzed: **{summary['total_mentions']}**

Sentiment Score: **{summary['sentiment_score']:.2f}** (Range: -1.0 to 1.0)

### Overall Sentiment Distribution

- 😊 Positive: **{summary['positive']}** ({summary['positive']/summary['total_mentions']*100:.1f}%)
- 😐 Neutral: **{summary['neutral']}** ({summary['neutral']/summary['total_mentions']*100:.1f}%)
- 😠 Negative: **{summary['negative']}** ({summary['negative']/summary['total_mentions']*100:.1f}%)

## Platform Breakdown

"""

        for platform, data in summary['by_platform'].items():
            platform_name = platform.title()
            if platform == 'twitter':
                platform_name = 'X (Twitter)'

            report += f"""### {platform_name}

Total: {data['total']} mentions
- Positive: {data['positive']} ({data['positive']/data['total']*100:.1f}%)
- Neutral: {data['neutral']} ({data['neutral']/data['total']*100:.1f}%)
- Negative: {data['negative']} ({data['negative']/data['total']*100:.1f}%)

"""

        # Key themes
        themes = self.extract_themes()
        report += "## Key Themes\n\n"
        for word, count in themes:
            report += f"- **{word}**: {count} mentions\n"

        # Notable positive mentions
        report += "\n## Notable Positive Mentions\n\n"
        positive_mentions = self.get_notable_mentions('positive', 3)
        for i, mention in enumerate(positive_mentions, 1):
            report += f"{i}. **{mention['sender']}** ({mention['platform'].title()})\n"
            report += f"   > {mention['content'][:150]}...\n\n"

        # Notable negative mentions
        report += "## Notable Negative Mentions\n\n"
        negative_mentions = self.get_notable_mentions('negative', 3)
        for i, mention in enumerate(negative_mentions, 1):
            report += f"{i}. **{mention['sender']}** ({mention['platform'].title()})\n"
            report += f"   > {mention['content'][:150]}...\n\n"

        # Recommendations
        report += "## Recommendations\n\n"

        if summary['sentiment_score'] > 0.3:
            report += "- ✅ Overall sentiment is positive. Continue current engagement strategies.\n"
        elif summary['sentiment_score'] < -0.3:
            report += "- ⚠️ Overall sentiment is negative. Immediate attention required.\n"
        else:
            report += "- ℹ️ Sentiment is mixed. Monitor closely for trends.\n"

        if summary['negative'] > 0:
            report += f"- 🔍 Address {summary['negative']} negative mentions promptly.\n"

        if summary['positive'] > summary['negative'] * 2:
            report += "- 📢 Amplify positive mentions through sharing and engagement.\n"

        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved to: {output_file}")

    def generate_json_report(self, output_file: str):
        """Generate JSON format report"""
        summary = self.generate_summary()
        themes = self.extract_themes()

        report_data = {
            'generated': datetime.now().isoformat(),
            'summary': summary,
            'themes': [{'word': word, 'count': count} for word, count in themes],
            'top_positive': [
                {
                    'sender': m['sender'],
                    'platform': m['platform'],
                    'content': m['content'],
                    'confidence': m['confidence']
                }
                for m in self.get_notable_mentions('positive', 5)
            ],
            'top_negative': [
                {
                    'sender': m['sender'],
                    'platform': m['platform'],
                    'content': m['content'],
                    'confidence': m['confidence']
                }
                for m in self.get_notable_mentions('negative', 5)
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"JSON report saved to: {output_file}")

    def generate_csv_report(self, output_file: str):
        """Generate CSV format report"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Platform', 'Sender', 'Sentiment', 'Confidence', 'Content', 'Received'])

            for mention in self.mentions:
                writer.writerow([
                    mention['platform'],
                    mention['sender'],
                    mention['sentiment'],
                    f"{mention['confidence']:.2f}",
                    mention['content'][:200],
                    mention['received']
                ])

        print(f"CSV report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze social media sentiment')
    parser.add_argument('input_dir', help='Directory containing social media files')
    parser.add_argument('--output', '-o', default='sentiment_report.md', help='Output file')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'csv'], default='markdown',
                       help='Output format')
    parser.add_argument('--platform', '-p', choices=['twitter', 'facebook', 'instagram'],
                       help='Filter by platform')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--keywords', help='Track specific keywords (comma-separated)')

    args = parser.parse_args()

    processor = MentionProcessor()
    processor.load_mentions(args.input_dir, args.platform, args.start, args.end)

    if args.format == 'markdown':
        processor.generate_markdown_report(args.output)
    elif args.format == 'json':
        processor.generate_json_report(args.output)
    elif args.format == 'csv':
        processor.generate_csv_report(args.output)


if __name__ == '__main__':
    main()
