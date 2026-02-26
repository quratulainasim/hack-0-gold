# AI Content Generator Skill

## Purpose
Autonomously generate high-quality, platform-specific content for social media posts, email responses, and business communications using AI. Transforms captured communications into draft responses ready for human approval.

## Capabilities

### Content Generation
- **Instagram**: Engaging captions with hashtags, visual descriptions, emoji usage
- **Facebook**: Community-focused posts with calls-to-action
- **LinkedIn**: Professional updates with industry insights
- **Twitter/X**: Concise tweets with trending hashtags (280 chars)
- **Gmail**: Professional email responses with proper formatting
- **WhatsApp**: Conversational replies maintaining tone
- **Odoo**: Invoice and order drafts with proper formatting

### AI-Powered Features
- **Context Analysis**: Understands the original message intent
- **Tone Matching**: Adapts tone to platform and audience
- **Brand Voice**: Maintains consistent brand personality
- **Hashtag Generation**: Creates relevant, trending hashtags
- **Call-to-Action**: Includes appropriate CTAs
- **Personalization**: Tailors content to recipient

### Platform-Specific Logic

#### Social Media (Instagram, Facebook, LinkedIn, Twitter/X)
- Engaging captions optimized for platform
- Relevant hashtags (3-5 for Instagram, 1-2 for LinkedIn)
- Emoji usage appropriate to platform culture
- Visual descriptions for image posts
- Character limits respected (Twitter: 280, LinkedIn: 3000)

#### Email & Messaging (Gmail, WhatsApp)
- Professional or conversational tone based on context
- Proper email formatting (greeting, body, signature)
- Clear subject lines
- Action items highlighted
- Professional closings

#### Business (Odoo)
- Invoice drafts with line items
- Order confirmations with details
- Payment reminders with terms
- Professional business formatting

## Usage

### Invoke via Claude Code
```
Use the ai-content-generator skill to:
- Generate responses for items in Needs_Action
- Create platform-specific content
- Draft social media posts
- Write email responses
```

### Manual Execution
```bash
python .claude/skills/ai-content-generator/scripts/generate_content.py
```

### Process Specific Item
```bash
python .claude/skills/ai-content-generator/scripts/generate_content.py --file "Needs_Action/GMAIL_2026-02-24_item.md"
```

## Input

### Source Files
Reads from `Needs_Action/` folder:
- Gmail emails requiring responses
- LinkedIn posts needing engagement
- Twitter mentions requiring replies
- Facebook messages needing responses
- Instagram DMs requiring replies
- WhatsApp messages needing responses
- Odoo invoices/orders requiring drafts

### Required Metadata
Source files must have YAML frontmatter:
```yaml
---
source: gmail
type: email
priority: high
timestamp: 2026-02-24T10:30:00
author: John Doe
keywords: invoice, payment
---
```

## Output

### Generated Files
Creates files in `Pending_Approval/` folder with format:
```markdown
---
source: linkedin
platform: linkedin
type: post
priority: high
scheduled_time: 2026-02-24T14:00:00
content_type: engagement_post
status: pending
original_item: Needs_Action/LI_2026-02-24_item.md
ai_generated: true
requires_approval: true
---

# LinkedIn Post Response

## Generated Content

[AI-generated post content here]

## Hashtags
#BusinessGrowth #Innovation #Leadership

## Original Context
[Summary of original post/message]

## Approval Checklist
- [ ] Content tone is appropriate
- [ ] Hashtags are relevant
- [ ] No sensitive information disclosed
- [ ] Brand voice maintained
- [ ] Call-to-action is clear
```

### Platform-Specific Examples

#### Instagram Post
```markdown
---
platform: instagram
content_type: story_post
status: pending
---

# Instagram Story Response

🎉 Exciting news! We're thrilled to announce...

[Engaging caption with emojis]

#Innovation #TechStartup #Growth #Entrepreneurship #Success

📸 Visual: [Description of image/video needed]
```

#### Gmail Response
```markdown
---
platform: gmail
content_type: email_response
status: pending
to: john.doe@example.com
subject: Re: Invoice Payment Inquiry
---

# Email Response

**To**: john.doe@example.com
**Subject**: Re: Invoice Payment Inquiry

Dear John,

Thank you for reaching out regarding invoice #12345...

[Professional email body]

Best regards,
[Your Name]
```

#### Odoo Invoice Draft
```markdown
---
platform: odoo
content_type: invoice_draft
status: pending
amount: 5000.00
currency: USD
---

# Invoice Draft

**Customer**: ABC Corporation
**Invoice Date**: 2026-02-24
**Due Date**: 2026-03-24
**Amount**: $5,000.00

## Line Items
1. Consulting Services - $3,000.00
2. Software License - $2,000.00

**Total**: $5,000.00

## Payment Terms
Net 30 days
```

## Configuration

### Environment Variables
```bash
# Claude API for content generation
ANTHROPIC_API_KEY=your_api_key_here

# Content generation settings
AI_MODEL=claude-sonnet-4-6
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# Brand voice settings
BRAND_TONE=professional_friendly
BRAND_VOICE=innovative_approachable
```

### Brand Voice Configuration
Edit `.claude/skills/ai-content-generator/references/brand_voice.md`:
- Company values
- Tone guidelines
- Prohibited words/phrases
- Preferred terminology
- Example posts

## AI Prompts

### Social Media Generation
```
Generate an engaging [platform] post responding to:
[Original content]

Requirements:
- Tone: [professional/casual/enthusiastic]
- Include 3-5 relevant hashtags
- Keep under [character limit]
- Include call-to-action
- Match brand voice: [description]
```

### Email Generation
```
Generate a professional email response to:
[Original email]

Requirements:
- Professional tone
- Clear subject line
- Proper greeting and closing
- Address all points raised
- Include next steps
```

### Invoice Generation
```
Generate an invoice draft for:
[Order details]

Requirements:
- Professional formatting
- Clear line items
- Accurate calculations
- Payment terms included
- Company branding
```

## Integration

### With Other Skills
- **triage-inbox**: Identifies items needing responses
- **approval_monitor**: Presents generated content for review
- **executor**: Sends approved content to platforms
- **metric-auditor**: Tracks generation success rates

### With Workflow
```
Needs_Action → AI Content Generator → Pending_Approval → Human Review → Approved → Executor → Done
```

## Quality Assurance

### Content Checks
- Grammar and spelling verification
- Brand voice consistency
- Platform guidelines compliance
- Character/word limits respected
- No sensitive information leaked

### Safety Filters
- No offensive language
- No controversial topics (unless approved)
- No false claims
- No copyright violations
- No personal data exposure

## Performance

### Generation Speed
- Social media posts: ~5 seconds
- Email responses: ~10 seconds
- Invoice drafts: ~8 seconds
- Batch processing: ~30 items/minute

### Quality Metrics
- AI confidence score
- Brand voice match score
- Engagement prediction
- Approval rate tracking

## Error Handling

### Automatic Fallbacks
- API failures: Retry with exponential backoff
- Low confidence: Flag for manual review
- Content policy violations: Skip and alert
- Missing context: Request additional info

### Logging
All operations logged to `logs/content-generator.log`:
- Generation requests
- AI responses
- Approval status
- Error details

## Security

- API keys stored in `.env` (gitignored)
- No sensitive data in generated content
- Content sanitization before generation
- Audit trail for all generated content

## Monitoring

### Metrics Tracked
- Items processed per day
- Generation success rate
- Approval rate by platform
- Average generation time
- AI confidence scores

### Alerts
- Low approval rates (<70%)
- High rejection rates (>30%)
- API failures
- Content policy violations

## Future Enhancements

- [ ] Multi-language support
- [ ] A/B testing for content variations
- [ ] Engagement prediction models
- [ ] Automated scheduling optimization
- [ ] Image generation integration
- [ ] Video script generation
- [ ] Voice message transcription and response
