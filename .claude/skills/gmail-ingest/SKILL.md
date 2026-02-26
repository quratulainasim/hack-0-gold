---
name: gmail-ingest
description: Monitor /Inbox for files tagged 'source: gmail', extract email metadata (From, Subject, Body), and format into standardized Task Templates. Use this skill when the user asks to process Gmail items, ingest email data, convert emails to tasks, or format Gmail inbox items into task templates.
---

# Gmail Ingest

This skill processes Gmail-sourced files in the /Inbox folder, extracting email metadata and formatting them into standardized Task Templates for action planning.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Gmail Ingest Script

Execute the Gmail ingest script:

```bash
python scripts/gmail_ingest.py [vault_path]
```

- If `vault_path` is provided, process that vault location
- If omitted, process vault in current working directory

The script will:
- Scan `/Inbox` folder for `.md` files with `source: gmail` in frontmatter
- Extract email metadata: From (name and email), Subject, Body
- Load Task Template format from `Company_Handbook.md` (if available)
- Generate standardized Task Template for each email
- Save formatted task to `/Needs_Action` folder
- Update original file status to 'ingested'

### 2. Review Ingested Tasks

The script outputs information for each processed email:
- **Original file**: Path to the Gmail inbox item
- **From**: Sender name and email address
- **Subject**: Email subject line
- **Task created**: Path to the generated task file
- **Status**: Confirmation of successful ingestion

### 3. Task Template Format

The generated task follows this standardized format:

```markdown
---
source: gmail
type: email_task
priority: [extracted from original or default to normal]
received: [original received date]
status: pending
created_from: [original filename]
from_email: [sender email]
from_name: [sender name]
subject: [email subject]
---

# Task: [Email Subject]

## Source Information
- **From**: [Name] <[email@example.com]>
- **Received**: [Date/Time]
- **Original Email**: [Link to original file]

## Email Content

[Full email body content]

## Proposed Actions

Based on the email content, consider these actions:

- [ ] Review and respond to sender
- [ ] [Additional context-specific actions]

## Response Draft

[Placeholder for response content]

## Notes

[Space for additional notes and context]
```

### 4. Company Handbook Integration

**If Company_Handbook.md exists:**
- The script loads the Task Template format from the handbook
- Tasks are formatted according to company standards
- Action proposals follow handbook guidelines

**If Company_Handbook.md is not available:**
- The script uses the default Task Template format shown above
- Consider creating Company_Handbook.md to define custom templates
- The default format can be customized by editing the script

### 5. Processing Rules

**Files to Process:**
- Must be in `/Inbox` folder
- Must have `source: gmail` in frontmatter
- Must have `status: new` or no status field
- Must be `.md` files

**Files to Skip:**
- Already processed (status: ingested, processing, or completed)
- Missing required fields (from_email, subject)
- Non-Gmail sources
- Files outside /Inbox

### 6. Metadata Extraction

The script extracts these fields from Gmail inbox files:

**Required fields:**
- `from_email`: Sender's email address
- `from_name`: Sender's name
- `subject`: Email subject line
- Email body content (from markdown body)

**Optional fields:**
- `priority`: Inherited from original file
- `received`: Timestamp when email was received
- `has_attachments`: Whether email has attachments
- `thread_id`: Gmail thread identifier

### 7. Output Location

Generated tasks are saved to `/Needs_Action` with this naming convention:

```
[YYYY-MM-DD]_task_[sanitized-subject].md
```

Example: `2026-02-09_task_project-timeline-discussion.md`

## Integration with Workflow

This skill fits into the larger workflow:

1. **Gmail Multi-Watcher** → Captures emails to `/Inbox`
2. **Gmail Ingest** (this skill) → Converts to tasks in `/Needs_Action`
3. **Triage Inbox** → Processes and prioritizes tasks
4. **Senior Business Strategist** → Creates action plans
5. **Human Approval** → Reviews and approves
6. **Operational Executor** → Executes approved actions

## Error Handling

The script continues processing even if individual files fail:
- **Missing fields**: Logs warning and skips file
- **Malformed frontmatter**: Attempts to parse, uses defaults if needed
- **File access errors**: Reports error and continues
- **Invalid email format**: Logs error with file details

All errors are reported at the end of execution.

## Important Notes

- Original Gmail files are preserved in `/Inbox` with updated status
- Generated tasks are new files in `/Needs_Action`
- The script is idempotent - running multiple times won't create duplicates
- Task templates can be customized via Company_Handbook.md
- Attachments are referenced but not copied (handled separately)

## Integration with Other Skills

**Works well with:**
- `triage-inbox`: Run after gmail-ingest to process generated tasks
- `initialize-vault`: Run first to ensure folder structure exists
- `update-dashboard`: Update metrics after ingestion

## Example Usage

```bash
# Process Gmail items in current vault
python scripts/gmail_ingest.py

# Process Gmail items in specific vault
python scripts/gmail_ingest.py /path/to/vault

# Typical workflow
python scripts/gmail_ingest.py && python scripts/triage_inbox.py
```
