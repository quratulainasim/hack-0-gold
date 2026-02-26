#!/usr/bin/env python3
"""
AI Content Generator (Free Version)
Uses Google Gemini API - completely FREE!
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed")
    print("Run: pip install google-generativeai")
    sys.exit(1)


class FreeAIContentGenerator:
    """Generates AI-powered content using free Google Gemini API"""

    def __init__(self):
        # Script is at: .claude/skills/ai-content-generator/scripts/
        # Need to go up 5 levels to reach project root
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.needs_action_dir = self.project_root / "Needs_Action"
        self.pending_approval_dir = self.project_root / "Pending_Approval"
        self.logs_dir = self.project_root / "logs"

        # Ensure directories exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("ERROR: GEMINI_API_KEY not found in .env file")
            print("\nTo get a FREE API key:")
            print("1. Go to: https://makersuite.google.com/app/apikey")
            print("2. Click 'Create API Key'")
            print("3. Add to .env file: GEMINI_API_KEY=your_key_here")
            sys.exit(1)

        genai.configure(api_key=api_key)
        # Use the latest free Gemini Flash model
        self.model = genai.GenerativeModel('gemini-flash-latest')

        # Platform configurations
        self.platform_configs = {
            'instagram': {
                'char_limit': 2200,
                'hashtag_count': 5,
                'tone': 'engaging_visual',
                'emoji': True
            },
            'facebook': {
                'char_limit': 5000,
                'hashtag_count': 3,
                'tone': 'community_friendly',
                'emoji': True
            },
            'linkedin': {
                'char_limit': 3000,
                'hashtag_count': 3,
                'tone': 'professional_insightful',
                'emoji': False
            },
            'twitter': {
                'char_limit': 280,
                'hashtag_count': 2,
                'tone': 'concise_engaging',
                'emoji': True
            },
            'gmail': {
                'char_limit': None,
                'tone': 'professional_clear',
                'format': 'email'
            },
            'whatsapp': {
                'char_limit': 1000,
                'tone': 'conversational_friendly',
                'emoji': True
            },
            'odoo': {
                'tone': 'business_formal',
                'format': 'invoice'
            }
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        log_file = self.logs_dir / "content-generator.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown file"""
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        frontmatter_text = parts[1].strip()
        body = parts[2].strip()

        # Simple YAML parser
        metadata = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        return metadata, body

    def detect_platform(self, filename: str, metadata: Dict) -> str:
        """Detect platform from filename or metadata"""
        if 'source' in metadata:
            source = metadata['source'].lower()
            if source in self.platform_configs:
                return source

        filename_lower = filename.lower()
        if filename_lower.startswith('gmail_'):
            return 'gmail'
        elif filename_lower.startswith('li_'):
            return 'linkedin'
        elif filename_lower.startswith('x_'):
            return 'twitter'
        elif filename_lower.startswith('fb_'):
            return 'facebook'
        elif filename_lower.startswith('ig_'):
            return 'instagram'
        elif filename_lower.startswith('wa_'):
            return 'whatsapp'
        elif filename_lower.startswith('odoo_'):
            return 'odoo'

        return 'unknown'

    def build_generation_prompt(self, platform: str, metadata: Dict, content: str) -> str:
        """Build platform-specific prompt for Gemini"""
        config = self.platform_configs.get(platform, {})

        base_prompt = f"""You are a professional content creator. Generate a {platform} response to this communication.

ORIGINAL MESSAGE:
{content}

REQUIREMENTS:
"""

        if platform == 'instagram':
            base_prompt += """- Create an engaging Instagram caption
- Include 5 relevant hashtags
- Use emojis appropriately
- Keep under 2200 characters
- Include a call-to-action"""

        elif platform == 'facebook':
            base_prompt += """- Create a community-friendly Facebook post
- Include 3 relevant hashtags
- Use emojis to enhance engagement
- Keep under 5000 characters
- Encourage comments"""

        elif platform == 'linkedin':
            base_prompt += """- Create a professional LinkedIn post
- Include 3 relevant hashtags
- Professional tone, minimal emojis
- Keep under 3000 characters
- Add industry insights"""

        elif platform == 'twitter':
            base_prompt += """- Create a concise tweet
- Maximum 280 characters
- Include 1-2 hashtags
- Engaging and shareable"""

        elif platform == 'gmail':
            base_prompt += """- Create a professional email response
- Include proper greeting and closing
- Clear subject line
- Address all points
- Professional tone"""

        elif platform == 'whatsapp':
            base_prompt += """- Create a conversational WhatsApp reply
- Friendly tone
- Keep under 1000 characters
- Use emojis if appropriate"""

        elif platform == 'odoo':
            base_prompt += """- Create a professional invoice or order draft
- Include all line items
- Clear pricing
- Payment terms"""

        base_prompt += "\n\nGenerate ONLY the content, no explanations or meta-commentary."

        return base_prompt

    def generate_content(self, platform: str, metadata: Dict, content: str) -> Optional[str]:
        """Generate content using Google Gemini"""
        try:
            prompt = self.build_generation_prompt(platform, metadata, content)

            self.log(f"Generating {platform} content with Gemini...")

            response = self.model.generate_content(prompt)
            generated_content = response.text.strip()

            self.log(f"  [OK] Generated {len(generated_content)} characters")

            return generated_content

        except Exception as e:
            self.log(f"  [ERROR] Error generating content: {e}", "ERROR")
            return None

    def create_approval_file(self, platform: str, metadata: Dict, original_file: Path, generated_content: str):
        """Create file in Pending_Approval folder"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{platform.upper()}_{timestamp}_generated.md"
        filepath = self.pending_approval_dir / filename

        scheduled_time = (datetime.now() + timedelta(hours=1)).isoformat()

        frontmatter = f"""---
source: {metadata.get('source', platform)}
platform: {platform}
type: {metadata.get('type', 'response')}
priority: {metadata.get('priority', 'medium')}
scheduled_time: {scheduled_time}
content_type: ai_generated_response
status: pending
original_item: {original_file.relative_to(self.project_root)}
ai_generated: true
ai_model: gemini-pro
requires_approval: true
generated_at: {datetime.now().isoformat()}
---

"""

        if platform == 'gmail':
            content_body = f"""# Email Response

## Generated Content

{generated_content}

## Original Context
**From**: {metadata.get('author', 'Unknown')}
**Keywords**: {metadata.get('keywords', 'None')}

## Approval Checklist
- [ ] Content tone is appropriate
- [ ] All points addressed
- [ ] No sensitive information disclosed
- [ ] Professional language maintained
"""

        elif platform in ['instagram', 'facebook', 'linkedin', 'twitter']:
            content_body = f"""# {platform.title()} Post Response

## Generated Content

{generated_content}

## Original Context
**Author**: {metadata.get('author', 'Unknown')}
**Keywords**: {metadata.get('keywords', 'None')}

## Approval Checklist
- [ ] Content tone is appropriate
- [ ] Hashtags are relevant
- [ ] No sensitive information disclosed
- [ ] Brand voice maintained
- [ ] Call-to-action is clear
"""

        elif platform == 'whatsapp':
            content_body = f"""# WhatsApp Response

## Generated Content

{generated_content}

## Original Context
**From**: {metadata.get('author', 'Unknown')}
**Keywords**: {metadata.get('keywords', 'None')}

## Approval Checklist
- [ ] Tone is conversational
- [ ] Message is clear
- [ ] No sensitive information disclosed
"""

        elif platform == 'odoo':
            content_body = f"""# Odoo Invoice/Order Draft

## Generated Content

{generated_content}

## Original Context
**Type**: {metadata.get('type', 'Unknown')}
**Amount**: {metadata.get('amount', 'Unknown')}

## Approval Checklist
- [ ] All line items correct
- [ ] Pricing is accurate
- [ ] Payment terms included
- [ ] Customer details verified
"""

        else:
            content_body = f"""# Generated Response

## Content

{generated_content}

## Original Context
{metadata}

## Approval Checklist
- [ ] Content reviewed
- [ ] Ready to send
"""

        full_content = frontmatter + content_body

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        self.log(f"  [OK] Created: {filename}")
        return filepath

    def process_file(self, filepath: Path) -> bool:
        """Process a single file from Needs_Action"""
        try:
            self.log(f"Processing: {filepath.name}")

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata, body = self.parse_frontmatter(content)
            platform = self.detect_platform(filepath.name, metadata)

            if platform == 'unknown':
                self.log(f"  [WARNING] Unknown platform, skipping", "WARNING")
                return False

            self.log(f"  Platform: {platform}")

            generated_content = self.generate_content(platform, metadata, body)
            if not generated_content:
                return False

            self.create_approval_file(platform, metadata, filepath, generated_content)

            return True

        except Exception as e:
            self.log(f"  [ERROR] Error processing file: {e}", "ERROR")
            return False

    def process_all(self) -> Dict:
        """Process all files in Needs_Action folder"""
        self.log("="*60)
        self.log("FREE AI Content Generator (Google Gemini)")
        self.log("="*60)

        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0
        }

        files = list(self.needs_action_dir.glob("*.md"))

        if not files:
            self.log("No files found in Needs_Action folder")
            return results

        self.log(f"Found {len(files)} files to process")

        for filepath in files:
            results['processed'] += 1

            if self.process_file(filepath):
                results['successful'] += 1
            else:
                results['failed'] += 1

        self.log("="*60)
        self.log("Generation Summary")
        self.log("="*60)
        self.log(f"Processed: {results['processed']}")
        self.log(f"Successful: {results['successful']}")
        self.log(f"Failed: {results['failed']}")
        self.log("="*60)

        return results


def main():
    """Main entry point"""
    generator = FreeAIContentGenerator()

    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Usage: python generate_content_free.py --file <filepath>")
            sys.exit(1)

        filepath = Path(sys.argv[2])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        success = generator.process_file(filepath)
        sys.exit(0 if success else 1)

    results = generator.process_all()

    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
