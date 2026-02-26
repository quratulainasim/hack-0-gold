# Channel Input/Output Examples

This reference shows expected input formats and resulting Markdown output for each supported channel.

## Gmail

**Input (JSON):**
```json
{
  "id": "18d4f2a1b3c5e6f7",
  "threadId": "18d4f2a1b3c5e6f7",
  "from": {
    "name": "John Smith",
    "email": "john.smith@example.com"
  },
  "subject": "Q1 Budget Review",
  "date": "2026-02-19T10:30:00Z",
  "body": "<p>Hi team,</p><p>Please review the attached Q1 budget.</p>",
  "attachments": [
    {"filename": "Q1_Budget.xlsx"}
  ]
}
```

**Output (Markdown):**
```markdown
---
type: email
channel: Gmail
sender: John Smith
sender_id: john.smith@example.com
received: 2026-02-19T10:30:00Z
priority: medium
status: new
---

# Q1 Budget Review

Hi team,

Please review the attached Q1 budget.

## Metadata
- **Thread ID**: 18d4f2a1b3c5e6f7
- **Message ID**: 18d4f2a1b3c5e6f7
- **Attachments**: Q1_Budget.xlsx
```

## LinkedIn

**Input (JSON):**
```json
{
  "id": "msg_abc123",
  "type": "message",
  "conversationId": "conv_xyz789",
  "sender": {
    "name": "Sarah Johnson",
    "profileUrl": "https://linkedin.com/in/sarahjohnson",
    "company": "Tech Corp"
  },
  "content": "I'd love to discuss potential collaboration opportunities.",
  "timestamp": "2026-02-19T14:20:00Z"
}
```

**Output (Markdown):**
```markdown
---
type: linkedin
channel: LinkedIn Message
sender: Sarah Johnson
sender_id: https://linkedin.com/in/sarahjohnson
received: 2026-02-19T14:20:00Z
priority: medium
status: new
---

# LinkedIn message

I'd love to discuss potential collaboration opportunities.

## Metadata
- **Profile URL**: https://linkedin.com/in/sarahjohnson
- **Company**: Tech Corp
- **Conversation ID**: conv_xyz789
```

## Twitter/X

**Input (JSON):**
```json
{
  "id_str": "1234567890",
  "created_at": "2026-02-19T16:45:00Z",
  "user": {
    "name": "Tech News Daily",
    "screen_name": "technewsdaily"
  },
  "full_text": "Breaking: New AI model released today. Check it out!",
  "retweet_count": 42,
  "favorite_count": 156
}
```

**Output (Markdown):**
```markdown
---
type: twitter
channel: Twitter/X
sender: Tech News Daily
sender_id: @technewsdaily
received: 2026-02-19T16:45:00Z
priority: low
status: new
---

# Tweet from @technewsdaily

Breaking: New AI model released today. Check it out!

## Metadata
- **Tweet ID**: 1234567890
- **Retweets**: 42
- **Likes**: 156
- **Media**:
```

## Facebook

**Input (JSON):**
```json
{
  "sender_name": "Mike Chen",
  "sender_id": "100012345678",
  "timestamp_ms": 1708358400000,
  "message": "Hey! Are you free for coffee next week?",
  "thread_path": "inbox/mikechenconversation",
  "reactions": [
    {"reaction": "👍", "actor": "You"}
  ]
}
```

**Output (Markdown):**
```markdown
---
type: facebook
channel: Facebook
sender: Mike Chen
sender_id: 100012345678
received: 2026-02-19T12:00:00Z
priority: medium
status: new
---

# Facebook message from Mike Chen

Hey! Are you free for coffee next week?

## Metadata
- **Thread**: inbox/mikechenconversation
- **Reactions**: 👍
```

## WhatsApp

**Input (Text export):**
```
[2/19/26, 9:15 AM] Alice Brown: Can you send me the project files?
[2/19/26, 9:16 AM] Alice Brown: I need them for the presentation
[2/19/26, 9:20 AM] You: Sure, sending now
```

**Output (Markdown for first message):**
```markdown
---
type: whatsapp
channel: WhatsApp
sender: Alice Brown
sender_id: Alice Brown
received: 2/19/26, 9:15 AM
priority: medium
status: new
---

# WhatsApp from Alice Brown

Can you send me the project files?

## Metadata
```

## Instagram

**Input (JSON):**
```json
{
  "sender": {
    "username": "designstudio"
  },
  "text": "Love your recent work! Would you be interested in collaborating?",
  "timestamp": "2026-02-19T11:30:00Z",
  "post_url": "https://instagram.com/p/abc123",
  "media_type": "photo"
}
```

**Output (Markdown):**
```markdown
---
type: instagram
channel: Instagram
sender: designstudio
sender_id: @designstudio
received: 2026-02-19T11:30:00Z
priority: medium
status: new
---

# Instagram from @designstudio

Love your recent work! Would you be interested in collaborating?

## Metadata
- **Post Reference**: https://instagram.com/p/abc123
- **Media Type**: photo
```

## Priority Detection Examples

**High Priority:**
- "URGENT: Server is down"
- "ASAP - Need approval"
- "IMPORTANT: Client meeting moved"

**Medium Priority:**
- "Can you review this?"
- "Please send the files"
- "Follow up on our discussion"

**Low Priority:**
- "Just checking in"
- "FYI - New blog post"
- "Newsletter: Weekly updates"
