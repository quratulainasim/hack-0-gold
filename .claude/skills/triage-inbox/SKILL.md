---
name: triage-inbox
description: Triage and process markdown files in vault Inbox and Needs_Action folders. Use this skill when the user asks to triage inbox, process new items, scan inbox/needs_action folders, review pending items, or check for new files requiring attention. The skill parses frontmatter metadata (type, priority, received date), summarizes content, updates status to 'processing', and for Needs_Action items, proposes action plans based on Company_Handbook.md guidelines.
---

# Triage Inbox

This skill automates the triage process for markdown files in vault Inbox and Needs_Action folders, parsing metadata, summarizing content, and proposing action plans.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Triage Script

Execute the inbox triage script:

```bash
python scripts/triage_inbox.py [vault_path]
```

- If `vault_path` is provided, triage that vault location
- If omitted, triage vault in current working directory

The script will:
- Load `Company_Handbook.md` to understand operational guidelines
- Scan `/Inbox` and `/Needs_Action` folders for `.md` files
- Parse frontmatter from each file (type, priority, received date, status)
- Skip files already marked as 'processing'
- Summarize file content (first ~200 characters, cleaned)
- Update file status to 'processing' with timestamp
- For `/Needs_Action` files, propose a 1-step action plan

### 2. Review Triage Results

The script outputs detailed information for each file:
- **File name** and location (Inbox or Needs_Action)
- **Type**: The category/type from frontmatter
- **Priority**: Priority level (high, normal, low, etc.)
- **Received date**: When the item was received
- **Summary**: Brief content summary
- **Status update**: Confirmation that status was set to 'processing'
- **Action plan** (for Needs_Action items): Proposed next step based on handbook

### 3. Handle Files Requiring Action

For files in `/Needs_Action`, the script proposes a 1-step plan. Review these proposals and:

**If Company_Handbook.md is available:**
- The plan will reference handbook guidelines and procedures
- Follow the proposed action according to handbook rules
- Consider the file type and priority when executing

**If Company_Handbook.md is not available:**
- The plan will be generic (review and process the item)
- Ask the user for guidance on how to proceed
- Consider initializing the vault first with the initialize-vault skill

### 4. Process According to Priority

After triage, address files based on priority:
- **High priority**: Handle immediately
- **Normal priority**: Process in order received
- **Low priority**: Handle when time permits

The triage summary shows all processed files with their priorities for easy planning.

## Frontmatter Fields

The script expects and updates these frontmatter fields:

**Expected fields:**
- `type`: Category or type of item (e.g., "request", "document", "task")
- `priority`: Priority level (e.g., "high", "normal", "low")
- `received`: Date received (any format)

**Updated fields:**
- `status`: Set to "processing" during triage
- `triaged_at`: Timestamp when triage occurred

**Example frontmatter:**
```yaml
---
type: request
priority: high
received: 2026-02-01
status: processing
triaged_at: 2026-02-01 10:30:00
---
```

## Important Notes

- Files already marked with `status: processing` are skipped to avoid re-processing
- The script reads but does not modify `Company_Handbook.md`
- Content summaries are cleaned of markdown formatting for readability
- All file modifications preserve the original content, only updating frontmatter
- If folders don't exist, they are skipped (not created)
- The script handles missing frontmatter by treating fields as 'unknown'

## Integration with Other Skills

**Works well with:**
- `initialize-vault`: Run first to ensure vault structure exists
- File processing skills: Use after triage to act on Needs_Action items
- Dashboard skills: Update Dashboard.md with triage results

## Error Handling

The script continues processing even if individual files fail, reporting all errors at the end. Common issues:
- **File encoding errors**: Ensure all .md files are UTF-8 encoded
- **Malformed frontmatter**: Script handles missing or invalid frontmatter gracefully
- **Permission errors**: Ensure write access to vault folders
