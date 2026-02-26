---
name: multi_channel_ingest
description: Standardize all communication channels (Gmail, LinkedIn, Facebook, Twitter, WhatsApp, Instagram) into consistent Markdown format with metadata. Use this skill when the user asks to process incoming messages, convert communications to Markdown, ingest social media content, standardize message formats, or prepare communications for vault processing.
license: MIT
---

# Multi-Channel Ingest

This skill converts communications from multiple channels into standardized Markdown files with consistent metadata for downstream processing.

## Supported Channels

- Gmail (email)
- LinkedIn (messages, notifications, posts)
- Facebook (messages, posts, comments)
- Twitter/X (tweets, DMs, mentions)
- WhatsApp (messages)
- Instagram (messages, comments)

## Quick Start

Process a communication file:

```bash
python scripts/ingest.py <input-file> --output <output-directory>
```

The script automatically detects the channel type and converts to standardized Markdown.

## Workflow

1. **Detect channel**: Identify the source channel from file format or metadata
2. **Extract content**: Parse the message content and metadata
3. **Standardize format**: Convert to Markdown with consistent frontmatter
4. **Save output**: Write to specified directory (default: vault /Inbox)

## Output Format

All ingested communications use this structure:

```markdown
---
type: [email|linkedin|facebook|twitter|whatsapp|instagram]
channel: [specific channel name]
sender: [sender name or handle]
sender_id: [email address, profile URL, or user ID]
received: [ISO 8601 timestamp]
priority: [high|medium|low]
status: new
---

# [Subject or first line]

[Message content in Markdown]

## Metadata
- **Platform**: [Channel name]
- **Thread ID**: [if applicable]
- **Attachments**: [list if any]
```

## Channel-Specific Processing

### Gmail
- Extracts: sender, subject, body, timestamp, attachments
- Converts HTML to Markdown
- Preserves thread information

### LinkedIn
- Handles: messages, connection requests, post notifications, comments
- Extracts: sender profile, company, message content
- Includes profile URL for context

### Facebook
- Processes: messages, post comments, reactions
- Extracts: sender name, timestamp, thread context
- Converts reactions to text

### Twitter/X
- Handles: tweets, DMs, mentions, replies
- Extracts: handle, tweet text, media links
- Preserves thread structure

### WhatsApp
- Processes: exported chat messages
- Extracts: sender, timestamp, message content
- Handles media references

### Instagram
- Handles: DMs, post comments, story replies
- Extracts: username, message content, media context
- Includes post/story reference if applicable

## Priority Detection

The script automatically assigns priority based on:
- **High**: Keywords like "urgent", "ASAP", "important", direct mentions
- **Medium**: Questions, requests for action, follow-ups
- **Low**: General updates, notifications, automated messages

## Advanced Usage

Process multiple files:
```bash
python scripts/ingest.py --batch <directory>
```

Specify output location:
```bash
python scripts/ingest.py <input-file> --output /path/to/vault/Inbox
```

Override channel detection:
```bash
python scripts/ingest.py <input-file> --channel gmail
```

## Integration with Vault

When used with a vault system, ingested files are saved to `/Inbox` for triage processing. The standardized format ensures compatibility with downstream skills like `triage-inbox` and `strategic-planner`.
