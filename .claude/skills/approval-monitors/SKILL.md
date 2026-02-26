---
name: approval-monitor
description: Monitor and display all items in /Pending_Approval for CEO review. Acts as gatekeeper - lists pending plans with summaries, tracks approval status, and confirms when items are moved to /Approved folder for execution. Use this skill when the user asks to review pending approvals, check approval queue, list items awaiting approval, or monitor approval status.
---

# Approval Monitor

This skill monitors the approval pipeline, displaying pending items for CEO review and tracking approval status.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Approval Monitor Script

Execute the approval monitoring script:

```bash
python scripts/approval_monitor.py [vault_path]
```

- If `vault_path` is provided, monitor that vault location
- If omitted, monitor vault in current working directory

The script will:
- Scan `/Pending_Approval` folder for items awaiting review
- Extract key information from each Plan.md
- Display CEO-friendly summary of all pending items
- Show approval status and priority
- Provide instructions for approval process
- Check `/Approved` folder for recently approved items

### 2. Display Format

The script presents items in this executive-friendly format:

```
============================================================
APPROVAL MONITOR - Items Awaiting Review
============================================================
Vault: /path/to/vault
Last Updated: 2026-02-09 15:30:00

PENDING APPROVAL: 3 items
APPROVED (Ready for Execution): 2 items

============================================================
PENDING ITEMS
============================================================

[1] 🔴 HIGH PRIORITY - Client Project Inquiry
    Folder: 2026-02-09_client-project-inquiry
    Created: 2026-02-09 14:30
    Type: Email Response

    Objective: Respond to client inquiry about Q1 deliverables
    MCP Tools: Gmail MCP

    Quick Summary:
    Client Jennifer Martinez needs to discuss timeline changes.
    Plan proposes scheduling call this week and reviewing requirements.

    Success Criteria:
    - Email sent within 24 hours
    - Meeting scheduled
    - Client relationship maintained

    Risk Level: LOW

    ✅ APPROVE: Move to /Approved/2026-02-09_client-project-inquiry/
    ✏️  MODIFY: Edit Plan.md and keep in /Pending_Approval/
    ❌ REJECT: Move to /Rejected/ with reason

---

[2] 🔴 HIGH PRIORITY - LinkedIn Lead Engagement
    Folder: 2026-02-09_linkedin-lead-sarah-johnson
    Created: 2026-02-09 15:00
    Type: LinkedIn Message

    Objective: Engage with potential partnership lead
    MCP Tools: LinkedIn MCP

    Quick Summary:
    Sarah Johnson (CEO, TechVenture) expressed interest in collaboration.
    Plan proposes personalized outreach with value proposition.

    Success Criteria:
    - Message sent within 24 hours
    - Lead responds positively
    - Conversation progresses

    Risk Level: MEDIUM

    ✅ APPROVE: Move to /Approved/2026-02-09_linkedin-lead-sarah-johnson/
    ✏️  MODIFY: Edit Plan.md and keep in /Pending_Approval/
    ❌ REJECT: Move to /Rejected/ with reason

---

[3] 🟡 MEDIUM PRIORITY - Meeting Confirmation
    Folder: 2026-02-09_meeting-confirmation
    Created: 2026-02-09 15:15
    Type: Email Response

    Objective: Confirm attendance at quarterly review
    MCP Tools: Gmail MCP

    Quick Summary:
    Standard meeting confirmation for Q1 business review.
    Plan proposes accepting invitation and confirming attendance.

    Success Criteria:
    - Calendar invitation accepted
    - Confirmation sent

    Risk Level: LOW

    ✅ APPROVE: Move to /Approved/2026-02-09_meeting-confirmation/
    ✏️  MODIFY: Edit Plan.md and keep in /Pending_Approval/
    ❌ REJECT: Move to /Rejected/ with reason

============================================================
APPROVED ITEMS (Ready for Execution)
============================================================

[A1] Partnership Proposal Response
     Folder: 2026-02-08_partnership-proposal
     Approved: 2026-02-09 10:00
     Status: ⏳ Awaiting Execution

[A2] Customer Success Story Post
     Folder: 2026-02-08_customer-success-post
     Approved: 2026-02-09 11:30
     Status: ⏳ Awaiting Execution

============================================================
APPROVAL INSTRUCTIONS
============================================================

To APPROVE an item:
1. Review the Plan.md file in the folder
2. Verify all details are correct
3. Move the entire folder to /Approved/

   Example:
   mv Pending_Approval/2026-02-09_client-project-inquiry Approved/

To MODIFY an item:
1. Edit the Plan.md file in the folder
2. Make necessary changes
3. Keep the folder in /Pending_Approval/
4. Run approval-monitor again to see updated version

To REJECT an item:
1. Create a REJECTION_REASON.md file in the folder
2. Document why it was rejected
3. Move the folder to /Rejected/

   Example:
   echo "Timing not appropriate" > Pending_Approval/[folder]/REJECTION_REASON.md
   mv Pending_Approval/[folder] Rejected/

============================================================
NEXT STEPS
============================================================

1. Review each pending item above
2. Read full Plan.md for items requiring approval
3. Make approval decisions
4. Move approved items to /Approved/ folder
5. Operational Executor will process items in /Approved/

============================================================
```

### 3. Information Extracted

For each pending item, the script extracts:

**From Folder Name:**
- Date created
- Item identifier

**From Plan.md:**
- Priority level (High/Medium/Low)
- Objective statement
- Required MCP tools
- Quick summary (first few lines)
- Success criteria
- Risk assessment level

**From Original Item:**
- Source (Gmail, LinkedIn, etc.)
- Type (email, post, comment, etc.)
- Context and background

### 4. Priority Indicators

Items are displayed with visual priority indicators:

- 🔴 **HIGH PRIORITY** - Requires immediate attention (within 24 hours)
- 🟡 **MEDIUM PRIORITY** - Standard timeline (48-72 hours)
- 🟢 **LOW PRIORITY** - Can be scheduled flexibly

High-priority items are listed first for immediate visibility.

### 5. Approval Process

The skill provides clear instructions for three actions:

**APPROVE ✅**
```bash
# Move entire folder to /Approved/
mv Pending_Approval/[folder-name] Approved/
```

**MODIFY ✏️**
```bash
# Edit Plan.md in place
nano Pending_Approval/[folder-name]/Plan.md
# Keep in Pending_Approval for re-review
```

**REJECT ❌**
```bash
# Document rejection reason
echo "Reason for rejection" > Pending_Approval/[folder-name]/REJECTION_REASON.md
# Move to Rejected folder
mv Pending_Approval/[folder-name] Rejected/
```

### 6. Gatekeeper Function

The skill acts as a gatekeeper by:

**Monitoring Pending:**
- Lists all items awaiting approval
- Prevents execution until approved
- Tracks how long items have been pending

**Tracking Approved:**
- Shows items in /Approved/ folder
- Indicates they're ready for Operational Executor
- Monitors execution status

**Blocking Execution:**
- Items in /Pending_Approval/ cannot be executed
- Only items in /Approved/ are accessible to Executor
- Clear separation between review and execution

### 7. CEO-Friendly Features

**Scannable Format:**
- Quick summary at top
- Priority-sorted list
- Key information highlighted
- Clear action items

**Risk Awareness:**
- Risk level displayed for each item
- High-risk items flagged
- Mitigation strategies referenced

**Time Sensitivity:**
- Creation timestamps shown
- Priority indicates urgency
- Aging items highlighted

**Decision Support:**
- Objective clearly stated
- Success criteria visible
- Tools required listed
- Quick summary provided

### 8. Monitoring Frequency

**Recommended Usage:**

- **Morning**: Review overnight items
- **Midday**: Check for new items
- **End of Day**: Final review before close

**Automated Monitoring:**
Can be scheduled to run periodically:
```bash
# Run every 2 hours during business hours
*/120 * * * * python scripts/approval_monitor.py
```

### 9. Integration with Workflow

This skill bridges planning and execution:

```
Strategic Planner → /Pending_Approval
                         ↓
                  Approval Monitor (this skill)
                         ↓
                  CEO Review & Decision
                         ↓
                    /Approved/
                         ↓
                Operational Executor
```

### 10. Approval Metrics

The script tracks and displays:

**Current Status:**
- Number of items pending
- Number of items approved
- Oldest pending item age

**Historical Metrics:**
- Average approval time
- Approval rate (approved vs. rejected)
- Items processed today

**Alerts:**
- Items pending > 24 hours
- High-priority items waiting
- Backlog warnings

## Important Notes

- **Non-destructive**: Script only reads and displays, doesn't modify files
- **Read-only**: Approval actions are manual (moving folders)
- **Gatekeeper**: Ensures human review before execution
- **Audit trail**: All approvals tracked by folder movement
- **Flexible**: CEO can approve, modify, or reject at any time

## Integration with Other Skills

**Run after:**
- `strategic-planner` - Creates items to review

**Run before:**
- Operational Executor - Ensures items are approved

**Works well with:**
- `update-dashboard` - Update metrics after approvals

## Error Handling

The script handles:
- **Missing Plan.md**: Flags item as incomplete
- **Malformed plans**: Displays what's available
- **Empty folders**: Skips with warning
- **Permission issues**: Reports access errors

## Security & Compliance

**Approval Authority:**
- Only authorized personnel should move items to /Approved/
- Folder permissions should enforce this

**Audit Trail:**
- Folder timestamps track approval timing
- REJECTION_REASON.md documents rejections
- All movements logged in system

**Quality Control:**
- Human review ensures quality
- Prevents automated errors from executing
- Allows strategic oversight

## Example Usage

```bash
# Check pending approvals
python scripts/approval_monitor.py

# Monitor specific vault
python scripts/approval_monitor.py /path/to/vault

# Approve an item (manual)
mv Pending_Approval/2026-02-09_client-inquiry Approved/

# Check status after approval
python scripts/approval_monitor.py
```

## Best Practices

1. **Review daily** - Check pending items at least once per day
2. **Prioritize high-priority** - Address urgent items first
3. **Read full plans** - Don't rely only on summaries for important items
4. **Document rejections** - Always explain why items are rejected
5. **Batch approvals** - Review multiple items in one session for efficiency
6. **Monitor execution** - Check that approved items are executed promptly

## Customization

To customize the monitor:

**Change display format:**
Edit `format_pending_item()` function

**Adjust priority sorting:**
Edit `sort_pending_items()` function

**Add metrics:**
Edit `calculate_metrics()` function

**Customize alerts:**
Edit `check_alerts()` function

The approval monitor is the critical control point ensuring quality and strategic alignment before execution.
