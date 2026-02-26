---
name: update-dashboard
description: Update Dashboard.md with real-time vault metrics and executive summary. Use this skill when the user asks to update dashboard, refresh dashboard, generate dashboard report, check vault status, create executive summary, or review vault metrics. The skill counts items in Needs_Action, extracts the last 5 completed items from Done folder, and rewrites Dashboard.md with a scannable, CEO-friendly layout including status indicators and quick actions.
---

# Update Dashboard

This skill generates an executive dashboard with real-time vault metrics, designed for quick scanning by busy executives.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Dashboard Update Script

Execute the dashboard update script:

```bash
python scripts/update_dashboard.py [vault_path]
```

- If `vault_path` is provided, update dashboard at that location
- If omitted, update dashboard in current working directory

The script will:
- Count all `.md` files in `/Needs_Action` folder
- Extract the last 5 completed items from `/Done` folder (sorted by modification time)
- Generate a new Dashboard.md with real-time summary
- Include visual indicators for workload status
- Maintain CEO-friendly, scannable layout

### 2. Review the Generated Dashboard

The script creates a Dashboard.md with these sections:

**Real-time Summary:**
- Current count of items requiring action
- Visual workload indicator:
  - ✅ 0 items: All clear
  - 🟢 1-3 items: Low volume, manageable
  - 🟡 4-10 items: Moderate volume, monitor closely
  - 🔴 11+ items: High volume, prioritization needed

**Recently Completed:**
- Last 5 completed items with priority indicators
- Item type and completion timestamp
- Truncated titles for quick scanning

**Quick Actions:**
- Suggested next steps for vault management

**Vault Health:**
- Summary metrics at a glance
- System operational status

### 3. Present Dashboard to User

After updating, inform the user:
- How many items require action
- How many recently completed items were found
- The workload status indicator (green/yellow/red)
- Location of the updated Dashboard.md

If the user is a CEO or executive, emphasize:
- The visual status indicators for quick assessment
- Priority-coded completed items
- Actionable next steps

### 4. Handle Missing Folders

If `/Needs_Action` or `/Done` folders don't exist:
- The script handles this gracefully (returns 0 or empty list)
- Suggest running the `initialize-vault` skill first
- Dashboard will still be created with available data

## Dashboard Layout Design

The dashboard is optimized for executive readability:

**Visual Hierarchy:**
- Clear section headers with emoji icons
- Bold numbers for key metrics
- Status indicators using colors/emojis
- Whitespace for easy scanning

**Information Density:**
- Most critical info at the top (Real-time Summary)
- Supporting details below (Recently Completed)
- Action items clearly separated
- No overwhelming detail

**Scannable Format:**
- Can be read in under 30 seconds
- Key metrics visible without scrolling
- Priority indicators at a glance
- Timestamps for context

## Priority Indicators

Completed items show priority with visual markers:
- 🔴 High priority
- 🟡 Medium priority
- ⚪ Normal priority
- 🔵 Low priority

This allows executives to quickly assess what types of work are being completed.

## File Metadata Used

The script extracts these frontmatter fields from files:

**From all files:**
- `type`: Category of item
- `priority`: Priority level
- `status`: Current status

**From Done files:**
- `completed_at`: Completion timestamp (preferred)
- Falls back to file modification time if not present

**For display:**
- First line of content (after frontmatter) as title
- Truncated to 80 characters for readability

## Integration with Other Skills

**Works well with:**
- `initialize-vault`: Run first to create vault structure
- `triage-inbox`: Triage items before updating dashboard
- File completion skills: Mark items as done, then update dashboard

**Typical workflow:**
1. Initialize vault (one-time)
2. Triage inbox items
3. Process Needs_Action items
4. Update dashboard to reflect current state
5. Review dashboard for executive summary

## Important Notes

- Dashboard.md is completely rewritten each time (not appended)
- The script preserves no previous dashboard content
- Timestamps use the format: `YYYY-MM-DD HH:MM:SS`
- File modification times are used if `completed_at` frontmatter is missing
- The script handles missing folders gracefully (shows 0 counts)
- All markdown files are assumed to be UTF-8 encoded

## Customization Considerations

If the user requests dashboard customization:

**Layout changes:**
- Modify the `generate_dashboard_content()` function
- Adjust section order or add new sections
- Change emoji indicators or formatting

**Metric changes:**
- Adjust the count of completed items (default: 5)
- Add new metrics (inbox count, overdue items, etc.)
- Modify workload thresholds (currently 0/3/10)

**Visual changes:**
- Change priority indicators
- Adjust status emoji
- Modify section headers

## Error Handling

The script continues execution even if individual operations fail:
- Missing folders: Returns 0 or empty list
- Unreadable files: Logs error, continues with other files
- Missing frontmatter: Uses defaults (unknown, normal, etc.)
- All errors reported in summary

This ensures the dashboard is always updated with whatever data is available.
