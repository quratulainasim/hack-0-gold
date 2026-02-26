---
name: executor
description: Execute approved plans from /Approved folder using MCP tools (Gmail, LinkedIn). Reads Plan.md, executes the proposed action via appropriate MCP tool, logs results, and moves completed items to /Done. Use this skill when the user asks to execute approved plans, run approved actions, process approved queue, send approved emails/posts, or execute pending items.
---

# Executor

This skill executes approved plans using MCP tools, completing the workflow automation cycle.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Executor Script

Execute the executor script:

```bash
python scripts/executor.py [vault_path]
```

- If `vault_path` is provided, process that vault location
- If omitted, process vault in current working directory

The script will:
- Scan `/Approved` folder for items ready for execution
- Read Plan.md to understand the action
- Identify required MCP tools
- Execute the action (send email, post to LinkedIn, etc.)
- Capture execution results and confirmations
- Create execution summary
- Move completed item to `/Done`
- Update Dashboard with execution metrics

### 2. Execution Process

For each approved item, the script follows this process:

**Step 1: Validate**
- Verify Plan.md exists and is readable
- Check required MCP tools are available
- Validate all necessary information is present
- Confirm item hasn't already been executed

**Step 2: Prepare**
- Extract draft content from Plan.md
- Identify target (email address, LinkedIn profile, etc.)
- Prepare any attachments or media
- Set up MCP tool connection

**Step 3: Execute**
- Use appropriate MCP tool (Gmail or LinkedIn)
- Send email or post content
- Capture confirmation (message ID, post URL, etc.)
- Handle any errors or failures

**Step 4: Verify**
- Confirm action completed successfully
- Capture any response or feedback
- Log execution details
- Take screenshots if applicable

**Step 5: Archive**
- Create execution summary document
- Move item folder to `/Done/[YYYY-MM-DD]/`
- Preserve all files (Plan.md, original item, execution log)
- Update item status to 'completed'

**Step 6: Report**
- Update Dashboard.md with execution results
- Log success/failure metrics
- Flag any issues for review

### 3. MCP Tool Integration

The executor uses these MCP tools:

**Gmail MCP**
```python
# Send email via Gmail MCP
gmail_mcp.send_email(
    to="recipient@example.com",
    subject="Re: Subject",
    body="Email content",
    attachments=[]
)
```

**LinkedIn MCP**
```python
# Post to LinkedIn via LinkedIn MCP
linkedin_mcp.create_post(
    content="Post content",
    visibility="public"
)

# Comment on LinkedIn post
linkedin_mcp.create_comment(
    post_url="https://linkedin.com/posts/...",
    comment="Comment content"
)

# Send LinkedIn message
linkedin_mcp.send_message(
    recipient="profile-url",
    message="Message content"
)
```

### 4. Execution Summary Format

After execution, the script creates an execution summary:

```markdown
# Execution Summary

**Executed**: 2026-02-09 16:30:00
**Status**: ✅ Success
**Executor**: Operational Executor (automated)

---

## Action Details

**Type**: Email Response
**Tool Used**: Gmail MCP
**Target**: jennifer@acmecorp.com

---

## Execution Log

16:30:00 - Started execution
16:30:01 - Connected to Gmail MCP
16:30:02 - Composed email
16:30:03 - Sent email
16:30:04 - Received confirmation

**Confirmation**: Message ID: <abc123@gmail.com>

---

## Content Sent

Subject: Re: Project Timeline Discussion

Dear Jennifer,

[Full email content that was sent]

---

## Results

✅ Email sent successfully
✅ Delivery confirmed
✅ No errors encountered

---

## Success Criteria Check

- [x] Email sent successfully without errors
- [x] All points from original email are addressed
- [x] Professional tone and formatting maintained

---

## Next Steps

- Monitor for recipient response
- Track engagement metrics
- Follow up if no response within 48 hours

---

*Execution completed by executor skill on 2026-02-09 16:30:04*
```

### 5. Error Handling

If execution fails, the script:

**Captures Error:**
- Log error message and stack trace
- Note timestamp and context
- Preserve all data for debugging

**Creates Error Report:**
```markdown
# Execution Error Report

**Attempted**: 2026-02-09 16:30:00
**Status**: ❌ Failed
**Error**: Connection timeout to Gmail MCP

---

## Error Details

Error Type: ConnectionError
Error Message: Failed to connect to Gmail MCP server
Timestamp: 2026-02-09 16:30:05

---

## Attempted Action

Type: Email Response
Target: jennifer@acmecorp.com
Tool: Gmail MCP

---

## Troubleshooting Steps

1. Verify Gmail MCP is running
2. Check network connectivity
3. Verify authentication credentials
4. Check MCP configuration

---

## Recommended Action

- Keep item in /Approved folder
- Fix MCP connection issue
- Retry execution
- If persistent, escalate to human

---

*Error logged by executor skill on 2026-02-09 16:30:05*
```

**Handles Gracefully:**
- Keeps item in /Approved (doesn't move to Done)
- Adds ERROR.md file to item folder
- Flags in Dashboard for attention
- Sends alert if configured
- Allows manual retry

### 6. Execution Modes

The executor supports different modes:

**Automatic Mode (Default):**
- Processes all items in /Approved automatically
- Executes immediately when items appear
- Suitable for trusted, well-tested workflows

**Dry Run Mode:**
```bash
python scripts/executor.py --dry-run
```
- Simulates execution without actually sending
- Shows what would be executed
- Useful for testing and validation

**Single Item Mode:**
```bash
python scripts/executor.py --item [folder-name]
```
- Executes only specified item
- Useful for manual control
- Allows selective execution

**Batch Mode:**
```bash
python scripts/executor.py --batch
```
- Processes all items in one batch
- Generates combined report
- Efficient for multiple items

### 7. Safety Features

**Pre-execution Checks:**
- Verify item is in /Approved (not /Pending_Approval)
- Confirm Plan.md has been reviewed
- Check for APPROVED.md marker file
- Validate MCP tools are configured

**Content Validation:**
- Check for placeholder text (e.g., "[Your Name]")
- Verify email addresses are valid
- Ensure URLs are properly formatted
- Confirm no sensitive data is exposed

**Rate Limiting:**
- Respect MCP tool rate limits
- Delay between executions if needed
- Prevent spam or abuse
- Track daily execution counts

**Rollback Capability:**
- For certain actions, support undo
- Log all actions for audit trail
- Preserve original state
- Allow manual intervention

### 8. Execution Metrics

The executor tracks:

**Success Metrics:**
- Total executions today
- Success rate (%)
- Average execution time
- Tool usage breakdown

**Failure Metrics:**
- Failed executions
- Error types and frequency
- Retry attempts
- Resolution time

**Performance Metrics:**
- Queue processing time
- MCP tool response time
- End-to-end completion time
- Throughput (items/hour)

### 9. Integration with Dashboard

After each execution, the executor updates Dashboard.md:

```markdown
## Recent Executions (Last 5)

1. [16:30] ✅ Email sent to jennifer@acmecorp.com - Client inquiry response
2. [15:45] ✅ LinkedIn post published - Industry insights
3. [14:20] ✅ LinkedIn comment posted - Engagement with lead
4. [13:10] ❌ Email failed - Connection timeout (retrying)
5. [12:00] ✅ Email sent to david@techpartners.io - Partnership response

## Execution Metrics (Today)

- Total Executions: 12
- Successful: 11 (92%)
- Failed: 1 (8%)
- Average Time: 3.2 seconds
- Items in Queue: 2
```

### 10. Archive Structure

Completed items are organized in /Done:

```
Done/
├── 2026-02-09/
│   ├── client-project-inquiry/
│   │   ├── Plan.md
│   │   ├── original-item.md
│   │   ├── EXECUTION_SUMMARY.md
│   │   └── APPROVED.md
│   ├── linkedin-lead-engagement/
│   │   ├── Plan.md
│   │   ├── original-item.md
│   │   └── EXECUTION_SUMMARY.md
│   └── meeting-confirmation/
│       ├── Plan.md
│       ├── original-item.md
│       └── EXECUTION_SUMMARY.md
└── 2026-02-08/
    └── [previous day's items]
```

## Important Notes

- **Requires MCP tools**: Gmail and LinkedIn MCP must be configured
- **Irreversible actions**: Emails sent and posts published cannot be undone
- **Human approval required**: Only executes items in /Approved folder
- **Audit trail**: All executions logged for compliance
- **Error recovery**: Failed items remain in /Approved for retry

## Integration with Workflow

This skill completes the automation cycle:

```
1. Capture (Multi-Watchers)
2. Ingest (gmail-ingest, linkedin-ingest)
3. Triage (triage-inbox)
4. Plan (strategic-planner)
5. Approve (approval-monitor + human decision)
6. Execute (executor) ← THIS SKILL
7. Archive (/Done)
```

## Security & Compliance

**Authentication:**
- MCP tools use OAuth2 for secure authentication
- Credentials stored securely
- No passwords in code or logs

**Data Privacy:**
- Email content encrypted in transit
- Sensitive data redacted in logs
- Compliance with GDPR/privacy laws

**Audit Trail:**
- All executions logged with timestamps
- User actions tracked
- Execution summaries preserved
- Searchable archive maintained

## Example Usage

```bash
# Execute all approved items
python scripts/executor.py

# Dry run (test without executing)
python scripts/executor.py --dry-run

# Execute specific item
python scripts/executor.py --item 2026-02-09_client-inquiry

# Execute in specific vault
python scripts/executor.py /path/to/vault

# Batch mode with reporting
python scripts/executor.py --batch --report
```

## Best Practices

1. **Monitor execution logs** - Review daily for errors
2. **Test with dry-run** - Validate before live execution
3. **Check MCP status** - Ensure tools are operational
4. **Review failed items** - Investigate and resolve errors
5. **Archive regularly** - Clean up old items in /Done
6. **Track metrics** - Monitor success rates and performance
7. **Maintain MCP tools** - Keep credentials current

## Troubleshooting

**Issue: Executions failing**
- Check MCP tool configuration
- Verify authentication credentials
- Test MCP connection manually
- Review error logs

**Issue: Items not being processed**
- Verify items are in /Approved (not /Pending_Approval)
- Check folder permissions
- Ensure Plan.md exists
- Look for ERROR.md files

**Issue: Slow execution**
- Check network connectivity
- Review MCP tool performance
- Consider rate limiting
- Optimize batch processing

## Customization

To customize execution:

**Add new MCP tools:**
Edit `execute_with_mcp()` function to support additional tools

**Change archive structure:**
Edit `archive_completed_item()` function

**Modify execution summary:**
Edit `create_execution_summary()` function

**Add custom validations:**
Edit `validate_before_execution()` function

The executor is the final automation step, turning approved plans into real-world actions.
