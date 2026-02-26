---
name: multi_mcp_orchestrator
description: Orchestrate multiple external actions across MCP servers (Gmail, LinkedIn, Slack, etc.) in a single session. Use this skill when the user asks to execute complex workflows spanning multiple services, coordinate actions across platforms, run multi-step automation, orchestrate MCP tools, or execute batch operations across different external systems.
license: MIT
---

# Multi-MCP Orchestrator

This skill orchestrates complex workflows across multiple MCP (Model Context Protocol) servers, enabling coordinated actions across Gmail, LinkedIn, Slack, and other external services in a single session.

## Quick Start

Execute a workflow:

```bash
python scripts/orchestrator.py --workflow workflow.yaml
```

Interactive workflow builder:

```bash
python scripts/orchestrator.py --interactive
```

## Supported MCP Servers

- **Gmail**: Send emails, read inbox, manage labels
- **LinkedIn**: Post updates, send messages, manage connections
- **Slack**: Send messages, create channels, manage users
- **GitHub**: Create issues, PRs, manage repositories
- **Calendar**: Create events, check availability
- **Database**: Query, insert, update records
- **File System**: Read, write, move files
- **HTTP**: Make API calls to external services

## Workflow Structure

Workflows are defined in YAML or JSON:

```yaml
name: "Customer Onboarding Workflow"
description: "Automated customer onboarding process"
version: "1.0"

variables:
  customer_name: "Acme Corp"
  customer_email: "contact@acme.com"
  account_manager: "john@company.com"

steps:
  - id: send_welcome_email
    name: "Send welcome email"
    mcp_server: gmail
    action: send_email
    params:
      to: "{{customer_email}}"
      subject: "Welcome to our platform!"
      body: "Dear {{customer_name}}, welcome aboard..."
    on_error: retry
    retry_count: 3

  - id: create_slack_channel
    name: "Create customer Slack channel"
    mcp_server: slack
    action: create_channel
    params:
      name: "customer-{{customer_name | slugify}}"
      is_private: false
    depends_on: [send_welcome_email]

  - id: notify_team
    name: "Notify team in Slack"
    mcp_server: slack
    action: send_message
    params:
      channel: "{{steps.create_slack_channel.channel_id}}"
      text: "New customer onboarded: {{customer_name}}"
    depends_on: [create_slack_channel]

  - id: linkedin_announcement
    name: "Post LinkedIn announcement"
    mcp_server: linkedin
    action: create_post
    params:
      text: "Excited to welcome {{customer_name}} to our platform!"
      visibility: "public"
    depends_on: [send_welcome_email]
    optional: true  # Don't fail workflow if this fails
```

## Workflow Features

### Sequential Execution

Steps execute in order:

```yaml
steps:
  - id: step1
    action: ...

  - id: step2
    action: ...
    depends_on: [step1]

  - id: step3
    action: ...
    depends_on: [step2]
```

### Parallel Execution

Steps without dependencies run in parallel:

```yaml
steps:
  - id: send_email
    action: ...

  - id: post_linkedin
    action: ...
    # No depends_on, runs parallel with send_email

  - id: post_slack
    action: ...
    # No depends_on, runs parallel with above
```

### Conditional Execution

Execute steps based on conditions:

```yaml
steps:
  - id: check_status
    action: ...

  - id: send_success_email
    action: ...
    condition: "{{steps.check_status.result == 'success'}}"

  - id: send_failure_email
    action: ...
    condition: "{{steps.check_status.result == 'failure'}}"
```

### Error Handling

Handle errors gracefully:

```yaml
steps:
  - id: risky_operation
    action: ...
    on_error: retry  # Options: retry, continue, fail, rollback
    retry_count: 3
    retry_delay: 5  # seconds

  - id: fallback_operation
    action: ...
    run_on_error: [risky_operation]  # Only runs if risky_operation fails
```

### Variable Substitution

Use variables and step outputs:

```yaml
variables:
  customer_name: "Acme Corp"

steps:
  - id: get_customer_id
    action: database_query
    params:
      query: "SELECT id FROM customers WHERE name = '{{customer_name}}'"

  - id: send_email
    action: send_email
    params:
      to: "customer@example.com"
      body: "Your customer ID is {{steps.get_customer_id.result.id}}"
```

### Loops and Iteration

Iterate over lists:

```yaml
variables:
  recipients:
    - "user1@example.com"
    - "user2@example.com"
    - "user3@example.com"

steps:
  - id: send_bulk_emails
    action: send_email
    for_each: "{{recipients}}"
    params:
      to: "{{item}}"
      subject: "Bulk notification"
      body: "Hello {{item}}"
```

## Execution Modes

### Dry Run

Preview workflow without executing:

```bash
python scripts/orchestrator.py --workflow workflow.yaml --dry-run
```

Shows what would be executed without making actual API calls.

### Step-by-Step

Execute with confirmation at each step:

```bash
python scripts/orchestrator.py --workflow workflow.yaml --step-by-step
```

Prompts for confirmation before each action.

### Resume from Checkpoint

Resume failed workflow from last successful step:

```bash
python scripts/orchestrator.py --workflow workflow.yaml --resume checkpoint.json
```

### Parallel Execution

Control parallelism:

```bash
python scripts/orchestrator.py --workflow workflow.yaml --max-parallel 5
```

Limits concurrent step execution.

## Advanced Features

### Rollback on Failure

Define rollback actions:

```yaml
steps:
  - id: create_resource
    action: create_database_record
    params:
      table: "customers"
      data: {...}
    rollback:
      action: delete_database_record
      params:
        table: "customers"
        id: "{{steps.create_resource.result.id}}"

  - id: send_notification
    action: send_email
    params: {...}
    rollback:
      action: send_email
      params:
        to: "admin@company.com"
        subject: "Rollback notification"
```

### Approval Gates

Require human approval:

```yaml
steps:
  - id: prepare_campaign
    action: ...

  - id: approval_gate
    type: approval
    message: "Review campaign before sending to 10,000 customers"
    timeout: 3600  # 1 hour
    on_timeout: fail

  - id: send_campaign
    action: ...
    depends_on: [approval_gate]
```

### Webhooks and Callbacks

Trigger external webhooks:

```yaml
steps:
  - id: process_order
    action: ...

  - id: notify_webhook
    action: http_post
    params:
      url: "https://external-system.com/webhook"
      body:
        event: "order_processed"
        order_id: "{{steps.process_order.result.id}}"
```

### State Persistence

Save workflow state:

```yaml
workflow:
  name: "Long Running Process"
  checkpoint_interval: 5  # Save state every 5 steps
  checkpoint_file: "workflow_state.json"
```

## Workflow Templates

### Email Campaign

```yaml
name: "Email Campaign"
steps:
  - id: get_recipients
    action: database_query
    params:
      query: "SELECT email FROM subscribers WHERE active = true"

  - id: send_emails
    action: send_email
    for_each: "{{steps.get_recipients.result}}"
    params:
      to: "{{item.email}}"
      subject: "Monthly Newsletter"
      body: "..."
    max_parallel: 10
```

### Social Media Cross-Post

```yaml
name: "Cross-Platform Post"
variables:
  message: "Exciting product launch today!"

steps:
  - id: post_linkedin
    mcp_server: linkedin
    action: create_post
    params:
      text: "{{message}}"

  - id: post_twitter
    mcp_server: twitter
    action: create_tweet
    params:
      text: "{{message}}"

  - id: post_slack
    mcp_server: slack
    action: send_message
    params:
      channel: "#announcements"
      text: "{{message}}"
```

### Customer Onboarding

```yaml
name: "Customer Onboarding"
steps:
  - id: create_account
    action: database_insert
    params:
      table: "customers"
      data:
        name: "{{customer_name}}"
        email: "{{customer_email}}"

  - id: send_welcome_email
    action: send_email
    params:
      to: "{{customer_email}}"
      subject: "Welcome!"

  - id: create_slack_channel
    action: create_slack_channel
    params:
      name: "customer-{{customer_name | slugify}}"

  - id: assign_account_manager
    action: send_email
    params:
      to: "{{account_manager}}"
      subject: "New customer assigned"
```

## Error Handling Strategies

### Retry with Exponential Backoff

```yaml
steps:
  - id: api_call
    action: http_get
    params:
      url: "https://api.example.com/data"
    on_error: retry
    retry_count: 5
    retry_strategy: exponential  # 1s, 2s, 4s, 8s, 16s
    retry_max_delay: 60
```

### Circuit Breaker

```yaml
steps:
  - id: external_service
    action: http_post
    params:
      url: "https://unreliable-service.com/api"
    circuit_breaker:
      failure_threshold: 5
      timeout: 30
      reset_timeout: 300
```

### Fallback Actions

```yaml
steps:
  - id: primary_action
    action: send_via_primary_service
    on_error: continue

  - id: fallback_action
    action: send_via_backup_service
    run_on_error: [primary_action]
```

## Monitoring and Logging

### Execution Log

```json
{
  "workflow_id": "wf_12345",
  "name": "Customer Onboarding",
  "status": "completed",
  "started_at": "2026-02-19T10:00:00Z",
  "completed_at": "2026-02-19T10:05:23Z",
  "duration_seconds": 323,
  "steps_executed": 8,
  "steps_failed": 0,
  "steps_skipped": 1,
  "steps": [
    {
      "id": "send_welcome_email",
      "status": "success",
      "started_at": "2026-02-19T10:00:00Z",
      "completed_at": "2026-02-19T10:00:02Z",
      "duration_seconds": 2,
      "result": {
        "message_id": "msg_abc123"
      }
    }
  ]
}
```

### Real-time Progress

```bash
python scripts/orchestrator.py --workflow workflow.yaml --progress
```

Shows live progress:

```
Executing: Customer Onboarding Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60% 6/10 steps

✓ send_welcome_email (2s)
✓ create_slack_channel (3s)
✓ notify_team (1s)
⏳ linkedin_announcement (in progress...)
⏸ assign_account_manager (waiting)
⏸ send_confirmation (waiting)
```

## Integration with Vault

When used with a vault system:

1. Read approved plans from `/Approved`
2. Extract action items from Plan.md
3. Generate workflow from plan
4. Execute workflow with orchestrator
5. Log results to `/Done`

## Best Practices

1. **Idempotency**: Design steps to be safely retryable
2. **Timeouts**: Set appropriate timeouts for all external calls
3. **Error handling**: Always define error handling strategy
4. **Logging**: Log all actions for audit trail
5. **Testing**: Test workflows in dry-run mode first
6. **Checkpoints**: Use checkpoints for long-running workflows
7. **Monitoring**: Monitor execution and set up alerts
8. **Documentation**: Document workflow purpose and dependencies

## Security Considerations

- Store credentials securely (environment variables, secrets manager)
- Validate all inputs before execution
- Implement rate limiting for external APIs
- Log all actions for audit
- Use least-privilege access for MCP servers
- Encrypt sensitive data in workflow definitions
- Review workflows before execution

## Performance Optimization

- Use parallel execution where possible
- Implement caching for repeated operations
- Batch operations when supported by MCP servers
- Set appropriate timeouts
- Use connection pooling
- Monitor and optimize slow steps

For detailed workflow patterns, see [references/workflow-patterns.md](references/workflow-patterns.md).

For MCP server integration guide, see [references/mcp-integration.md](references/mcp-integration.md).
