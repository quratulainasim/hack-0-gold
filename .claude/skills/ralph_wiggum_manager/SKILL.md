---
name: ralph_wiggum_manager
description: Autonomous loop orchestrator that manages the complete workflow from Inbox to Done. Coordinates triage, planning, approval, and execution skills in a continuous loop. Use this skill when the user asks to run the autonomous loop, manage the complete workflow, orchestrate all skills, run continuous processing, or manage tasks from start to completion.
license: MIT
---

# Ralph Wiggum Manager

This skill orchestrates the complete autonomous workflow loop, coordinating all skills from task ingestion through completion. Named after Ralph Wiggum for its simple, reliable, continuous operation - "I'm helping!"

## Quick Start

Start the autonomous loop:

```bash
python scripts/manager.py --vault-path /path/to/vault
```

Run with monitoring:

```bash
python scripts/manager.py --vault-path /path/to/vault --monitor --interval 60
```

## Workflow Overview

The manager orchestrates a complete workflow cycle:

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS LOOP                          │
└─────────────────────────────────────────────────────────────┘

1. INBOX → Triage
   ├─ Scan /Inbox for new items
   ├─ Run triage-inbox skill
   └─ Move to /Needs_Action

2. NEEDS_ACTION → Planning
   ├─ Scan /Needs_Action for items
   ├─ Run strategic-planner skill
   └─ Move to /Pending_Approval

3. PENDING_APPROVAL → Approval
   ├─ Scan /Pending_Approval for items
   ├─ Run approval-monitor skill
   ├─ Wait for human approval
   └─ Move to /Approved or /Rejected

4. APPROVED → Execution
   ├─ Scan /Approved for items
   ├─ Run executor skill
   └─ Move to /Done

5. DONE → Archive
   ├─ Scan /Done for completed items
   ├─ Run metric-auditor skill
   └─ Generate reports

6. REPEAT → Loop back to step 1
```

## Core Features

### Autonomous Operation

Runs continuously without human intervention:

```bash
# Run indefinitely
python scripts/manager.py --vault-path ./vault --loop

# Run for specific duration
python scripts/manager.py --vault-path ./vault --duration 3600  # 1 hour

# Run specific number of cycles
python scripts/manager.py --vault-path ./vault --cycles 10
```

### State Machine

Manages workflow state transitions:

```python
States:
- IDLE: Waiting for work
- TRIAGING: Processing inbox
- PLANNING: Creating plans
- AWAITING_APPROVAL: Waiting for human
- EXECUTING: Running approved tasks
- AUDITING: Generating reports
- ERROR: Handling failures
```

### Skill Coordination

Automatically invokes appropriate skills:

```yaml
workflow:
  - stage: inbox
    skill: triage-inbox
    trigger: "items in /Inbox"

  - stage: needs_action
    skill: strategic-planner
    trigger: "items in /Needs_Action"

  - stage: pending_approval
    skill: approval-monitor
    trigger: "items in /Pending_Approval"

  - stage: approved
    skill: executor
    trigger: "items in /Approved"

  - stage: done
    skill: metric-auditor
    trigger: "items in /Done"
```

### Health Monitoring

Continuous health checks:

```bash
# Monitor mode with health checks
python scripts/manager.py --vault-path ./vault --monitor --health-check-interval 300
```

**Monitors**:
- Vault folder integrity
- Skill availability
- System resources
- Error rates
- Processing times
- Queue depths

### Error Recovery

Automatic error handling and recovery:

```python
error_handling:
  - retry_failed_skills: true
  - max_retries: 3
  - backoff_strategy: exponential
  - fallback_to_manual: true
  - alert_on_critical: true
```

## Configuration

Configure in `manager_config.yaml`:

```yaml
manager:
  name: "Ralph Wiggum Manager"
  version: "1.0"

loop:
  enabled: true
  interval: 60  # seconds between cycles
  max_cycles: 0  # 0 = infinite
  max_duration: 0  # 0 = infinite

vault:
  path: "./vault"
  folders:
    - Inbox
    - Needs_Action
    - Pending_Approval
    - Approved
    - Rejected
    - Done

skills:
  triage_inbox:
    enabled: true
    trigger: "inbox_not_empty"
    timeout: 300

  strategic_planner:
    enabled: true
    trigger: "needs_action_not_empty"
    timeout: 600

  approval_monitor:
    enabled: true
    trigger: "pending_approval_not_empty"
    mode: "notify"  # notify, interactive, auto

  executor:
    enabled: true
    trigger: "approved_not_empty"
    timeout: 900

  metric_auditor:
    enabled: true
    trigger: "done_updated"
    schedule: "daily"

monitoring:
  enabled: true
  health_check_interval: 300
  metrics_interval: 60
  dashboard_update_interval: 300

  alerts:
    - condition: "error_rate > 0.1"
      severity: warning
      action: notify

    - condition: "queue_depth > 20"
      severity: warning
      action: notify

    - condition: "skill_timeout"
      severity: critical
      action: alert

error_handling:
  retry_enabled: true
  max_retries: 3
  retry_delay: 60
  backoff_multiplier: 2

  on_error:
    - log_error
    - notify_admin
    - attempt_recovery

  critical_errors:
    - vault_corruption
    - skill_unavailable
    - resource_exhaustion

logging:
  level: INFO
  file: "logs/manager.log"
  rotation: "daily"
  retention: 30

  structured: true
  include_context: true
```

## Operation Modes

### Continuous Mode (Default)

Runs indefinitely:

```bash
python scripts/manager.py --vault-path ./vault --continuous
```

### Scheduled Mode

Runs on schedule:

```bash
# Run every hour
python scripts/manager.py --vault-path ./vault --schedule "0 * * * *"

# Run weekdays at 9 AM
python scripts/manager.py --vault-path ./vault --schedule "0 9 * * 1-5"
```

### Single-Cycle Mode

Runs one complete cycle:

```bash
python scripts/manager.py --vault-path ./vault --single-cycle
```

### Interactive Mode

Prompts before each stage:

```bash
python scripts/manager.py --vault-path ./vault --interactive
```

### Dry-Run Mode

Simulates without executing:

```bash
python scripts/manager.py --vault-path ./vault --dry-run
```

## Monitoring Dashboard

Real-time status display:

```
╔════════════════════════════════════════════════════════════╗
║           RALPH WIGGUM MANAGER - STATUS                    ║
╚════════════════════════════════════════════════════════════╝

Status: 🟢 RUNNING
Uptime: 2h 34m 12s
Cycles: 154
Last Cycle: 23s ago

┌─────────────────────────────────────────────────────────┐
│ WORKFLOW STAGES                                         │
├─────────────────────────────────────────────────────────┤
│ Inbox:            3 items  → Triaging                   │
│ Needs_Action:     5 items  → Planning                   │
│ Pending_Approval: 2 items  → Awaiting Human            │
│ Approved:         1 item   → Executing                  │
│ Done:            47 items  → Complete                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SKILL STATUS                                            │
├─────────────────────────────────────────────────────────┤
│ triage-inbox:      ✓ Ready   Last: 45s ago             │
│ strategic-planner: ✓ Ready   Last: 2m ago              │
│ approval-monitor:  ⏸ Waiting Last: 5m ago              │
│ executor:          ⏳ Running Last: 12s ago             │
│ metric-auditor:    ✓ Ready   Last: 1h ago              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ METRICS                                                 │
├─────────────────────────────────────────────────────────┤
│ Items Processed:   154                                  │
│ Success Rate:      96.8%                                │
│ Avg Cycle Time:    58s                                  │
│ Error Rate:        3.2%                                 │
│ Queue Depth:       11 items                             │
└─────────────────────────────────────────────────────────┘

[q]uit | [p]ause | [r]esume | [s]tatus | [h]elp
```

## Advanced Features

### Parallel Processing

Process multiple stages simultaneously:

```yaml
parallel:
  enabled: true
  max_workers: 3
  stages:
    - inbox
    - needs_action
    - approved
```

### Priority Queue

Process high-priority items first:

```yaml
priority:
  enabled: true
  levels:
    - critical: 1
    - high: 2
    - medium: 3
    - low: 4
```

### Conditional Execution

Execute based on conditions:

```yaml
conditions:
  - stage: planning
    condition: "item_count > 5"
    action: batch_process

  - stage: approval
    condition: "priority == 'critical'"
    action: notify_immediately
```

### Workflow Hooks

Custom actions at each stage:

```yaml
hooks:
  pre_triage:
    - validate_inbox_items
    - check_duplicates

  post_execution:
    - update_dashboard
    - send_notifications

  on_error:
    - log_error
    - attempt_recovery
    - notify_admin
```

### State Persistence

Save and resume state:

```bash
# Save state on shutdown
python scripts/manager.py --vault-path ./vault --save-state

# Resume from saved state
python scripts/manager.py --vault-path ./vault --resume
```

## Integration Examples

### With Cron

```bash
# Run every 5 minutes
*/5 * * * * cd /path/to/vault && python scripts/manager.py --single-cycle
```

### With Systemd

```ini
[Unit]
Description=Ralph Wiggum Manager
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/path/to/vault
ExecStart=/usr/bin/python3 scripts/manager.py --vault-path . --continuous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "scripts/manager.py", "--vault-path", "/vault", "--continuous"]
```

### With Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ralph-wiggum-manager
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: manager
        image: ralph-wiggum-manager:latest
        env:
        - name: VAULT_PATH
          value: /vault
        volumeMounts:
        - name: vault
          mountPath: /vault
```

## Troubleshooting

### Manager Won't Start

```bash
# Check vault structure
python scripts/manager.py --vault-path ./vault --validate

# Check skill availability
python scripts/manager.py --vault-path ./vault --check-skills

# Verbose logging
python scripts/manager.py --vault-path ./vault --verbose
```

### Stuck in Loop

```bash
# Check current state
python scripts/manager.py --vault-path ./vault --status

# Force state reset
python scripts/manager.py --vault-path ./vault --reset-state

# Skip problematic stage
python scripts/manager.py --vault-path ./vault --skip-stage approval
```

### High Error Rate

```bash
# View error log
tail -f logs/manager.log | grep ERROR

# Run diagnostics
python scripts/manager.py --vault-path ./vault --diagnose

# Safe mode (skip failing skills)
python scripts/manager.py --vault-path ./vault --safe-mode
```

## Best Practices

1. **Monitor regularly**: Check dashboard and logs
2. **Set appropriate intervals**: Balance responsiveness and resource usage
3. **Configure alerts**: Get notified of issues
4. **Test in dry-run**: Validate before production
5. **Backup vault**: Regular backups of vault data
6. **Review metrics**: Track performance over time
7. **Update skills**: Keep skills up to date
8. **Handle approvals**: Don't let approval queue grow
9. **Archive old items**: Move completed items to archive
10. **Document workflows**: Keep workflow documentation current

## Performance Tuning

### Optimize Cycle Time

```yaml
optimization:
  # Skip empty folders
  skip_empty_folders: true

  # Batch processing
  batch_size: 10

  # Parallel execution
  parallel_stages: true

  # Cache skill results
  cache_enabled: true
  cache_ttl: 300
```

### Resource Management

```yaml
resources:
  # CPU limits
  max_cpu_percent: 80

  # Memory limits
  max_memory_mb: 2048

  # Disk space
  min_disk_space_gb: 10

  # Connection pools
  max_connections: 50
```

## Security

### Access Control

```yaml
security:
  # Require authentication
  auth_required: true

  # API key for remote access
  api_key: "${API_KEY}"

  # Allowed operations
  allowed_operations:
    - read
    - write
    - execute
```

### Audit Logging

```yaml
audit:
  enabled: true
  log_file: "logs/audit.log"

  events:
    - skill_execution
    - state_changes
    - error_occurrences
    - configuration_changes
```

For detailed workflow patterns, see [references/workflow-orchestration.md](references/workflow-orchestration.md).

For troubleshooting guide, see [references/troubleshooting.md](references/troubleshooting.md).

For deployment guide, see [references/deployment.md](references/deployment.md).
