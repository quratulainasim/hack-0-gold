# MCP Integration Guide

This reference documents how to integrate with various MCP servers.

## MCP Server Overview

MCP (Model Context Protocol) servers provide standardized interfaces to external services. The orchestrator communicates with these servers to execute actions.

## Supported MCP Servers

### Gmail MCP Server

**Actions:**
- `send_email` - Send an email
- `read_inbox` - Read inbox messages
- `search_emails` - Search emails
- `add_label` - Add label to email
- `delete_email` - Delete an email

**Example:**
```yaml
- id: send_email
  mcp_server: gmail
  action: send_email
  params:
    to: "recipient@example.com"
    subject: "Hello"
    body: "Email body content"
    cc: ["cc@example.com"]
    bcc: ["bcc@example.com"]
    attachments:
      - path: "/path/to/file.pdf"
        name: "document.pdf"
```

### LinkedIn MCP Server

**Actions:**
- `create_post` - Create a LinkedIn post
- `send_message` - Send direct message
- `connect_with_user` - Send connection request
- `get_profile` - Get user profile
- `search_people` - Search for people

**Example:**
```yaml
- id: post_update
  mcp_server: linkedin
  action: create_post
  params:
    text: "Excited to announce our new product!"
    visibility: "public"  # public, connections, private
    media:
      - url: "https://example.com/image.jpg"
        type: "image"
```

### Slack MCP Server

**Actions:**
- `send_message` - Send message to channel/user
- `create_channel` - Create new channel
- `invite_to_channel` - Invite users to channel
- `upload_file` - Upload file
- `get_channel_history` - Get message history

**Example:**
```yaml
- id: notify_team
  mcp_server: slack
  action: send_message
  params:
    channel: "#general"
    text: "Deployment completed successfully"
    blocks:
      - type: "section"
        text:
          type: "mrkdwn"
          text: "*Deployment Status*\nEnvironment: Production\nStatus: ✅ Success"
```

### GitHub MCP Server

**Actions:**
- `create_issue` - Create GitHub issue
- `create_pr` - Create pull request
- `merge_pr` - Merge pull request
- `add_comment` - Add comment to issue/PR
- `create_release` - Create release

**Example:**
```yaml
- id: create_issue
  mcp_server: github
  action: create_issue
  params:
    repo: "owner/repository"
    title: "Bug: Login not working"
    body: "Description of the issue..."
    labels: ["bug", "high-priority"]
    assignees: ["username"]
```

### Calendar MCP Server

**Actions:**
- `create_event` - Create calendar event
- `update_event` - Update event
- `delete_event` - Delete event
- `check_availability` - Check availability
- `list_events` - List events

**Example:**
```yaml
- id: schedule_meeting
  mcp_server: calendar
  action: create_event
  params:
    title: "Team Standup"
    start: "2026-02-20T09:00:00Z"
    end: "2026-02-20T09:30:00Z"
    attendees:
      - "team@company.com"
    location: "Zoom"
    description: "Daily standup meeting"
```

### Database MCP Server

**Actions:**
- `query` - Execute SELECT query
- `insert` - Insert records
- `update` - Update records
- `delete` - Delete records
- `execute` - Execute arbitrary SQL

**Example:**
```yaml
- id: get_users
  mcp_server: database
  action: query
  params:
    connection: "production"
    query: "SELECT * FROM users WHERE active = true"
    timeout: 30

- id: insert_user
  mcp_server: database
  action: insert
  params:
    connection: "production"
    table: "users"
    data:
      name: "John Doe"
      email: "john@example.com"
      active: true
```

### HTTP MCP Server

**Actions:**
- `get` - HTTP GET request
- `post` - HTTP POST request
- `put` - HTTP PUT request
- `delete` - HTTP DELETE request
- `patch` - HTTP PATCH request

**Example:**
```yaml
- id: api_call
  mcp_server: http
  action: post
  params:
    url: "https://api.example.com/v1/users"
    headers:
      Authorization: "Bearer {{api_token}}"
      Content-Type: "application/json"
    body:
      name: "John Doe"
      email: "john@example.com"
    timeout: 30
```

### File System MCP Server

**Actions:**
- `read_file` - Read file contents
- `write_file` - Write to file
- `delete_file` - Delete file
- `list_directory` - List directory contents
- `move_file` - Move/rename file

**Example:**
```yaml
- id: read_config
  mcp_server: filesystem
  action: read_file
  params:
    path: "/etc/app/config.json"
    encoding: "utf-8"

- id: write_log
  mcp_server: filesystem
  action: write_file
  params:
    path: "/var/log/app.log"
    content: "{{log_message}}"
    mode: "append"
```

## Authentication

### Environment Variables

Store credentials in environment variables:

```yaml
steps:
  - id: send_email
    mcp_server: gmail
    action: send_email
    params:
      to: "{{recipient}}"
      # Authentication handled by MCP server using env vars:
      # GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
```

### Configuration File

Or use a configuration file:

```yaml
# mcp_config.yaml
servers:
  gmail:
    type: gmail
    auth:
      client_id: "{{env.GMAIL_CLIENT_ID}}"
      client_secret: "{{env.GMAIL_CLIENT_SECRET}}"
      refresh_token: "{{env.GMAIL_REFRESH_TOKEN}}"

  slack:
    type: slack
    auth:
      token: "{{env.SLACK_BOT_TOKEN}}"

  github:
    type: github
    auth:
      token: "{{env.GITHUB_TOKEN}}"
```

## Error Handling

### MCP Server Errors

Handle MCP-specific errors:

```yaml
steps:
  - id: send_email
    mcp_server: gmail
    action: send_email
    params:
      to: "{{recipient}}"
    on_error: retry
    retry_count: 3
    error_handlers:
      - error_type: "RateLimitError"
        action: wait
        duration: 60
      - error_type: "AuthenticationError"
        action: fail
        notify: "admin@company.com"
```

### Timeout Handling

Set appropriate timeouts:

```yaml
steps:
  - id: slow_operation
    mcp_server: database
    action: query
    params:
      query: "SELECT * FROM large_table"
    timeout: 300  # 5 minutes
    on_timeout: fail
```

## Rate Limiting

Respect API rate limits:

```yaml
steps:
  - id: bulk_operation
    mcp_server: gmail
    action: send_email
    for_each: "{{recipients}}"
    params:
      to: "{{item}}"
    rate_limit:
      max_per_second: 10
      max_per_minute: 100
```

## Batching

Batch operations when supported:

```yaml
steps:
  - id: bulk_insert
    mcp_server: database
    action: batch_insert
    params:
      table: "users"
      records: "{{user_list}}"
      batch_size: 100
```

## Webhooks

Trigger workflows via webhooks:

```yaml
name: "Webhook Handler"
trigger:
  type: webhook
  path: "/webhooks/github"
  method: POST
  auth:
    type: signature
    secret: "{{env.WEBHOOK_SECRET}}"

steps:
  - id: process_webhook
    action: parse_github_webhook
    params:
      payload: "{{trigger.payload}}"
```

## Custom MCP Servers

Create custom MCP server integration:

```python
# custom_mcp_server.py
class CustomMCPServer:
    def __init__(self, config):
        self.config = config

    def execute_action(self, action, params):
        if action == "custom_action":
            return self.custom_action(params)
        else:
            raise ValueError(f"Unknown action: {action}")

    def custom_action(self, params):
        # Implementation
        return {"success": True}
```

Register in orchestrator:

```yaml
mcp_servers:
  custom:
    type: custom
    module: "custom_mcp_server"
    class: "CustomMCPServer"
    config:
      api_key: "{{env.CUSTOM_API_KEY}}"
```

## Testing MCP Integrations

### Mock MCP Server

Use mock server for testing:

```yaml
# test_workflow.yaml
mcp_servers:
  gmail:
    type: mock
    responses:
      send_email:
        message_id: "test_msg_123"
        status: "sent"

steps:
  - id: test_email
    mcp_server: gmail
    action: send_email
    params:
      to: "test@example.com"
```

### Dry Run Mode

Test without actual API calls:

```bash
python orchestrator.py --workflow workflow.yaml --dry-run
```

## Best Practices

1. **Use environment variables** for credentials
2. **Set appropriate timeouts** for all external calls
3. **Implement retry logic** for transient failures
4. **Respect rate limits** to avoid throttling
5. **Log all MCP calls** for debugging
6. **Handle errors gracefully** with fallbacks
7. **Test with mock servers** before production
8. **Monitor MCP server health** and availability
9. **Use batching** for bulk operations
10. **Implement circuit breakers** for unreliable services

## Monitoring

Track MCP server performance:

```yaml
monitoring:
  enabled: true
  metrics:
    - mcp_call_duration
    - mcp_call_success_rate
    - mcp_call_error_rate
    - mcp_rate_limit_hits
  alerts:
    - condition: "error_rate > 0.1"
      notify: "ops@company.com"
```

## Security

1. **Never hardcode credentials** in workflows
2. **Use encrypted secrets** for sensitive data
3. **Implement least-privilege access** for MCP servers
4. **Audit all MCP calls** for compliance
5. **Rotate credentials regularly**
6. **Use HTTPS only** for API calls
7. **Validate all inputs** before sending to MCP servers
8. **Sanitize outputs** from MCP servers
