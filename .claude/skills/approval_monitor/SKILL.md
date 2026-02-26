---
name: approval_monitor
description: Monitor and display all items in /Pending_Approval for CEO review. Acts as gatekeeper - lists pending plans with summaries, tracks approval status, and confirms when items are moved to /Approved folder for execution. Use this skill when the user asks to review pending approvals, check approval queue, list items awaiting approval, monitor approval status, or act as HITL (Human-in-the-Loop) gatekeeper.
license: MIT
---

# Approval Monitor

This skill acts as a Human-in-the-Loop (HITL) gatekeeper, monitoring items that require approval before execution.

## Quick Start

Check pending approvals:

```bash
python scripts/approval_monitor.py --vault-path /path/to/vault
```

Interactive approval mode:

```bash
python scripts/approval_monitor.py --vault-path /path/to/vault --interactive
```

## Workflow

1. **Scan /Pending_Approval**: Find all items awaiting approval
2. **Display summaries**: Show key details for each item
3. **Track status**: Monitor approval state (pending, approved, rejected)
4. **Facilitate decisions**: Present information for human review
5. **Confirm actions**: Verify when items move to /Approved or /Rejected

## Folder Structure

The approval monitor works with this vault structure:

```
vault/
├── Pending_Approval/     # Items awaiting approval
│   ├── Plan_001.md
│   ├── Plan_002.md
│   └── Email_Draft_003.md
├── Approved/             # Approved items ready for execution
│   └── Plan_004.md
└── Rejected/             # Rejected items (archived)
    └── Plan_005.md
```

## Approval Item Format

Items in /Pending_Approval should include approval metadata:

```markdown
---
type: plan
title: "Q1 Marketing Campaign"
submitted_by: "strategic-planner"
submitted_date: 2026-02-19T10:30:00Z
approval_status: pending
priority: high
estimated_cost: 50000
estimated_time: "4 weeks"
---

# Q1 Marketing Campaign Plan

## Objective
Launch comprehensive marketing campaign for Q1 product release...

## Required Resources
- Budget: $50,000
- Team: 3 marketers, 1 designer
- Timeline: 4 weeks

## Risks
- Tight timeline may require overtime
- Budget is at upper limit of approval threshold
```

## Display Modes

### Summary View (Default)

```
╔════════════════════════════════════════════════════════════════╗
║                    PENDING APPROVALS (3)                       ║
╚════════════════════════════════════════════════════════════════╝

[1] Plan_001.md - Q1 Marketing Campaign
    Type: plan | Priority: high | Cost: $50,000
    Submitted: 2026-02-19 by strategic-planner
    Summary: Launch comprehensive marketing campaign...

[2] Plan_002.md - Website Redesign
    Type: plan | Priority: medium | Cost: $75,000
    Submitted: 2026-02-18 by strategic-planner
    Summary: Redesign company website to improve UX...

[3] Email_Draft_003.md - Client Proposal
    Type: email | Priority: high | Cost: $0
    Submitted: 2026-02-19 by strategic-planner
    Summary: Proposal for enterprise client engagement...

╔════════════════════════════════════════════════════════════════╗
║ Commands: [v]iew details | [a]pprove | [r]eject | [q]uit      ║
╚════════════════════════════════════════════════════════════════╝
```

### Detailed View

```
╔════════════════════════════════════════════════════════════════╗
║                  APPROVAL ITEM DETAILS                         ║
╚════════════════════════════════════════════════════════════════╝

File: Plan_001.md
Title: Q1 Marketing Campaign
Type: plan
Priority: high
Status: pending

Submitted: 2026-02-19 10:30:00
Submitted by: strategic-planner

Estimated Cost: $50,000
Estimated Time: 4 weeks

Objective:
Launch comprehensive marketing campaign for Q1 product release
targeting 10,000 pre-orders and 50,000 website visits.

Key Tasks:
- Campaign strategy and planning
- Creative asset development
- Landing page development
- Email campaign setup
- Social media campaign
- PR and media outreach
- Paid advertising
- Launch day execution

Risks:
- Tight timeline may require overtime
- Budget is at upper limit of approval threshold

[Full content available in file]

╔════════════════════════════════════════════════════════════════╗
║ Actions: [a]pprove | [r]eject | [b]ack                        ║
╚════════════════════════════════════════════════════════════════╝
```

## Interactive Mode

In interactive mode, the monitor provides a menu-driven interface:

```bash
python scripts/approval_monitor.py --vault-path ./vault --interactive
```

**Features:**
- Browse pending items with arrow keys
- View detailed information
- Approve or reject with confirmation
- Add approval notes/comments
- Batch operations
- Filter by priority, type, or date

## Approval Actions

### Approve Item

```bash
python scripts/approval_monitor.py --vault-path ./vault --approve Plan_001.md --note "Approved for Q1 execution"
```

**What happens:**
1. Item moved from /Pending_Approval to /Approved
2. Approval metadata updated (status, approver, date, notes)
3. Notification logged
4. Item ready for execution by executor skill

### Reject Item

```bash
python scripts/approval_monitor.py --vault-path ./vault --reject Plan_002.md --reason "Budget exceeds Q1 allocation"
```

**What happens:**
1. Item moved from /Pending_Approval to /Rejected
2. Rejection metadata added (reason, date)
3. Notification logged
4. Item archived for reference

### Request Changes

```bash
python scripts/approval_monitor.py --vault-path ./vault --request-changes Plan_003.md --feedback "Please reduce budget to $40k"
```

**What happens:**
1. Item stays in /Pending_Approval
2. Feedback added to metadata
3. Status changed to "changes_requested"
4. Notification sent to submitter

## Approval Metadata

After approval/rejection, items are updated with:

```markdown
---
type: plan
title: "Q1 Marketing Campaign"
submitted_by: "strategic-planner"
submitted_date: 2026-02-19T10:30:00Z
approval_status: approved
approved_by: "CEO"
approved_date: 2026-02-19T14:30:00Z
approval_notes: "Approved for Q1 execution. Monitor budget closely."
priority: high
---
```

## Filtering and Sorting

### Filter by Priority

```bash
python scripts/approval_monitor.py --vault-path ./vault --filter priority=high
```

### Filter by Type

```bash
python scripts/approval_monitor.py --vault-path ./vault --filter type=plan
```

### Sort by Date

```bash
python scripts/approval_monitor.py --vault-path ./vault --sort date
```

### Sort by Cost

```bash
python scripts/approval_monitor.py --vault-path ./vault --sort cost
```

## Notifications

The monitor can send notifications for:

- New items in approval queue
- Items pending for >24 hours
- High-priority items
- Items approaching deadline

```bash
python scripts/approval_monitor.py --vault-path ./vault --notify-pending
```

## Dashboard Generation

Generate approval dashboard:

```bash
python scripts/approval_monitor.py --vault-path ./vault --generate-dashboard
```

Creates `Approval_Dashboard.md`:

```markdown
# Approval Dashboard

**Generated**: 2026-02-19 14:30:00

## Summary

- **Pending**: 3 items
- **Approved (today)**: 2 items
- **Rejected (today)**: 1 item
- **Awaiting changes**: 1 item

## Pending Items (3)

### High Priority (2)
1. Plan_001.md - Q1 Marketing Campaign ($50k, 4 weeks)
2. Email_Draft_003.md - Client Proposal

### Medium Priority (1)
1. Plan_002.md - Website Redesign ($75k, 12 weeks)

## Recently Approved (2)

1. Plan_004.md - Infrastructure Migration (approved 2h ago)
2. Email_Draft_005.md - Partnership Proposal (approved 5h ago)

## Action Required

⚠️ 2 high-priority items need review
⚠️ 1 item pending for >24 hours
```

## Approval Policies

Define approval policies in `approval_policies.yaml`:

```yaml
policies:
  auto_approve:
    - type: email
      cost: 0
      priority: low

  require_approval:
    - type: plan
      cost: ">10000"
    - type: email
      priority: high

  escalate:
    - cost: ">100000"
      escalate_to: "Board"

thresholds:
  budget:
    low: 10000
    medium: 50000
    high: 100000

  time:
    short: "1 week"
    medium: "1 month"
    long: "3 months"
```

## Integration with Other Skills

Works seamlessly with:

- **strategic-planner**: Receives plans for approval
- **executor**: Sends approved items for execution
- **metric-auditor**: Tracks approval metrics
- **update-dashboard**: Displays approval status

## Approval Workflow Example

```
1. strategic-planner creates Plan.md
   ↓
2. Plan.md moved to /Pending_Approval
   ↓
3. approval_monitor detects new item
   ↓
4. Human reviews via approval_monitor
   ↓
5. Decision: Approve/Reject/Request Changes
   ↓
6. If approved: Move to /Approved
   ↓
7. executor picks up from /Approved
   ↓
8. After execution: Move to /Done
```

## Audit Trail

All approval actions are logged:

```json
{
  "timestamp": "2026-02-19T14:30:00Z",
  "action": "approved",
  "item": "Plan_001.md",
  "approver": "CEO",
  "notes": "Approved for Q1 execution",
  "previous_status": "pending",
  "new_status": "approved"
}
```

## Best Practices

1. **Review daily**: Check pending approvals at least once per day
2. **Prioritize high-priority items**: Address urgent items first
3. **Provide clear feedback**: When requesting changes, be specific
4. **Document decisions**: Add notes explaining approval/rejection rationale
5. **Set thresholds**: Define clear approval criteria
6. **Monitor metrics**: Track approval times and bottlenecks
7. **Delegate when appropriate**: Use escalation for high-value decisions

## Security Considerations

- Only authorized users should approve items
- Approval actions are logged for audit
- Sensitive items should be encrypted
- Access controls on /Pending_Approval folder
- Approval history is immutable

## Metrics Tracked

- Average approval time
- Approval rate (approved vs rejected)
- Items pending by priority
- Bottlenecks and delays
- Approver activity
