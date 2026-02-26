# Company Handbook - Rules of Engagement

## Purpose
This handbook defines the operational guidelines for the Digital FTE vault management system.

## Folder Structure

### /Inbox
- **Purpose**: Temporary holding area for new items created by Watcher scripts
- **Retention**: Items should be triaged and moved within 24 hours
- **Status**: All items start with `status: new`

### /Needs_Action
- **Purpose**: Items requiring review, decision, or action
- **Priority Levels**: high, medium, low
- **Status Flow**: new → processing → completed

### /Done
- **Purpose**: Archive for completed items
- **Retention**: Keep last 30 days for dashboard reporting
- **Status**: All items marked as `status: completed`

## File Naming Conventions
- Use descriptive names with underscores: `task_description_YYYYMMDD.md`
- Include date stamps for time-sensitive items
- Keep names under 50 characters when possible

## Frontmatter Requirements
All markdown files must include:
```yaml
---
type: [notification|task|alert|report]
priority: [high|medium|low]
status: [new|processing|completed]
received: YYYY-MM-DD
---
```

## Processing Guidelines

### Notifications
- Simple informational items
- Move directly to /Done after review
- Update status to `completed`

### Tasks
- Require action or decision
- Create action plan in /Needs_Action
- Update status to `processing` while working
- Move to /Done when completed

### Alerts
- Time-sensitive items requiring immediate attention
- Always mark as `priority: high`
- Process before other items

## Dashboard Updates
- Run after each triage session
- Include counts from all folders
- Show last 5 completed items
- Timestamp all updates
