---
name: linkedin-ingest
description: Process incoming LinkedIn notification files. For 'Lead' or 'Comment' notifications, create high-priority tasks in /Inbox with draft user profile summaries. Use this skill when the user asks to process LinkedIn notifications, ingest LinkedIn data, convert LinkedIn items to tasks, or handle LinkedIn leads and comments.
---

# LinkedIn Ingest

This skill processes LinkedIn notification files, creating high-priority tasks for Leads and Comments with user profile summaries.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the LinkedIn Ingest Script

Execute the LinkedIn ingest script:

```bash
python scripts/linkedin_ingest.py [vault_path]
```

- If `vault_path` is provided, process that vault location
- If omitted, process vault in current working directory

The script will:
- Scan `/Inbox` folder for `.md` files with `source: linkedin` in frontmatter
- Filter for notification types: Lead, Comment, DM, Mention, Connection Request
- Extract user profile information and notification context
- Generate high-priority tasks with profile summaries
- Save tasks to `/Inbox` folder
- Update original file status to 'ingested'

### 2. Notification Types Processed

The script processes these LinkedIn notification types:

**High Priority (Always Processed):**
- **Lead** - Potential business opportunities
- **Comment** - Engagement on your content
- **DM** - Direct messages
- **Mention** - You've been mentioned in posts
- **Connection Request** - New connection requests

**Skipped:**
- General notifications
- Automated updates
- Already processed items

### 3. Task Template Format

Generated tasks follow this high-priority format:

```markdown
---
source: linkedin
type: linkedin_lead | linkedin_comment | linkedin_dm
priority: high
received: [timestamp]
status: pending
author: [LinkedIn user name]
author_url: [LinkedIn profile URL]
connection_level: [1st/2nd/3rd degree]
---

# 🔴 High Priority - LinkedIn [Type]: [Author]

## Profile Summary

- **Name**: [Author name]
- **LinkedIn**: [Profile URL]
- **Connection**: [Connection level]
- **Context**: [Extracted profile insights]

**Quick Assessment**: [Strategic context for engagement]

## Notification Details

- Type, author, profile link, context URL
- Received timestamp
- Link to original notification file

## Content

[Full notification content]

## Recommended Actions

- [ ] Review profile in detail
- [ ] Assess engagement opportunity
- [ ] Draft response strategy
- [ ] Determine urgency
- [ ] Check previous interactions

## Response Strategy

**Tone**: [Professional/Friendly/Consultative]
**Approach**: [Direct response/Schedule call/Share resource]

### Draft Response

[Placeholder for response]

## Profile Research Notes

[Space for background research]

## Follow-up Actions

- [ ] Connect on LinkedIn
- [ ] Review recent activity
- [ ] Check mutual connections
- [ ] Research company/role
```

### 4. Profile Summary Generation

The script automatically generates profile summaries by:

**Extracting from frontmatter:**
- Author name
- LinkedIn profile URL
- Connection level (1st, 2nd, 3rd degree)

**Analyzing content for:**
- Leadership roles (CEO, Founder, etc.)
- Experience indicators
- Company affiliations
- Industry context

**Providing quick assessment:**
- Connection relationship
- Engagement context
- Strategic value indicators

### 5. Priority Flagging

All processed LinkedIn notifications receive:

- **Priority**: HIGH (automatically set)
- **Status**: Pending (awaiting review)
- **Visual indicator**: 🔴 in task title
- **Urgency note**: Prompt review recommended

### 6. Processing Rules

**Files to Process:**
- Must be in `/Inbox` folder
- Must have `source: linkedin` in frontmatter
- Must have `type: lead`, `comment`, `dm`, `mention`, or `connection_request`
- Must have `status: new` or no status field
- Must be `.md` files

**Files to Skip:**
- Already processed (status: ingested, processing, completed)
- Missing required fields (author)
- Non-LinkedIn sources
- Notification types not configured for processing

### 7. Metadata Extraction

The script extracts these fields:

**Required:**
- `author`: LinkedIn user name
- `type`: Notification type

**Optional:**
- `author_url`: LinkedIn profile URL
- `connection_level`: 1st/2nd/3rd degree
- `context_url`: URL to post/comment/message
- `received`: Timestamp
- `priority`: Priority level (defaults to high)

### 8. Output Location

Generated tasks are saved to `/Inbox` with this naming convention:

```
[YYYY-MM-DD]_linkedin_[type]_[author-name].md
```

Examples:
- `2026-02-09_linkedin_lead_sarah-johnson.md`
- `2026-02-09_linkedin_comment_michael-chen.md`
- `2026-02-09_linkedin_dm_david-kim.md`

## Integration with Workflow

This skill fits into the workflow:

1. **LinkedIn Multi-Watcher** → Captures notifications to `/Inbox`
2. **LinkedIn Ingest** (this skill) → Creates high-priority tasks in `/Inbox`
3. **Triage Inbox** → Processes and prioritizes all inbox items
4. **Senior Business Strategist** → Creates engagement plans
5. **Human Approval** → Reviews and approves responses
6. **Operational Executor** → Posts responses via LinkedIn MCP

## Strategic Value

LinkedIn Leads and Comments represent:

- **Business opportunities** - Potential clients or partners
- **Engagement opportunities** - Build relationships and authority
- **Network expansion** - Grow professional connections
- **Brand visibility** - Respond to maintain reputation
- **Sales pipeline** - Convert engagement to business

High-priority flagging ensures these opportunities are addressed promptly.

## Error Handling

The script continues processing even if individual files fail:
- **Missing author**: Logs warning and skips
- **Invalid type**: Skips with notification
- **Malformed frontmatter**: Attempts to parse, uses defaults
- **File access errors**: Reports error and continues

All errors are reported at the end of execution.

## Important Notes

- Original LinkedIn notification files are preserved with updated status
- Generated tasks are new files in `/Inbox`
- Script is idempotent - safe to run multiple times
- Profile summaries are generated automatically but can be enhanced manually
- All tasks default to HIGH priority for prompt attention

## Integration with Other Skills

**Works well with:**
- `triage-inbox`: Run after linkedin-ingest to process tasks
- `gmail-ingest`: Process both email and LinkedIn in sequence
- `update-dashboard`: Update metrics after ingestion

## Example Usage

```bash
# Process LinkedIn notifications in current vault
python scripts/linkedin_ingest.py

# Process LinkedIn notifications in specific vault
python scripts/linkedin_ingest.py /path/to/vault

# Typical workflow - process both Gmail and LinkedIn
python scripts/gmail_ingest.py && python scripts/linkedin_ingest.py
```

## Customization

To customize notification processing:

**Add notification types:**
Edit `should_process_notification()` function to include additional types

**Modify profile summary:**
Edit `extract_profile_summary()` function to extract more details

**Change priority logic:**
Modify priority assignment based on notification type or author

**Enhance task template:**
Edit `generate_task_from_linkedin()` to customize task format

## Best Practices

1. **Review promptly** - High-priority tasks should be reviewed within 24 hours
2. **Research profiles** - Use provided profile summary as starting point
3. **Personalize responses** - Avoid generic replies to leads and comments
4. **Track engagement** - Monitor which types of engagement convert best
5. **Maintain quality** - Better to respond thoughtfully than quickly

LinkedIn engagement quality directly impacts professional reputation and business opportunities.
