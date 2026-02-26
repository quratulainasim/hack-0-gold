# Workflow Patterns

This reference documents common workflow patterns for multi-MCP orchestration.

## Pattern 1: Sequential Pipeline

**Use case:** Each step depends on the previous step's output

```yaml
name: "Data Processing Pipeline"
steps:
  - id: fetch_data
    action: database_query
    params:
      query: "SELECT * FROM raw_data"

  - id: transform_data
    action: process_data
    params:
      input: "{{steps.fetch_data.result}}"
    depends_on: [fetch_data]

  - id: validate_data
    action: validate
    params:
      data: "{{steps.transform_data.result}}"
    depends_on: [transform_data]

  - id: save_data
    action: database_insert
    params:
      data: "{{steps.validate_data.result}}"
    depends_on: [validate_data]
```

## Pattern 2: Fan-Out Parallel Execution

**Use case:** Execute multiple independent actions simultaneously

```yaml
name: "Multi-Channel Notification"
variables:
  message: "System maintenance scheduled"

steps:
  - id: send_email
    mcp_server: gmail
    action: send_email
    params:
      to: "team@company.com"
      subject: "Maintenance Alert"
      body: "{{message}}"

  - id: post_slack
    mcp_server: slack
    action: send_message
    params:
      channel: "#general"
      text: "{{message}}"

  - id: post_linkedin
    mcp_server: linkedin
    action: create_post
    params:
      text: "{{message}}"

  - id: update_status_page
    action: http_post
    params:
      url: "https://status.company.com/api/incidents"
      body:
        message: "{{message}}"
```

## Pattern 3: Conditional Branching

**Use case:** Different actions based on conditions

```yaml
name: "Order Processing"
steps:
  - id: check_inventory
    action: database_query
    params:
      query: "SELECT stock FROM inventory WHERE product_id = {{product_id}}"

  - id: process_order
    action: create_order
    params:
      product_id: "{{product_id}}"
    condition: "{{steps.check_inventory.result.stock > 0}}"
    depends_on: [check_inventory]

  - id: notify_success
    action: send_email
    params:
      to: "{{customer_email}}"
      subject: "Order Confirmed"
    condition: "{{steps.process_order.status == 'success'}}"
    depends_on: [process_order]

  - id: notify_out_of_stock
    action: send_email
    params:
      to: "{{customer_email}}"
      subject: "Out of Stock"
    condition: "{{steps.check_inventory.result.stock == 0}}"
    depends_on: [check_inventory]
```

## Pattern 4: Retry with Fallback

**Use case:** Try primary service, fall back to secondary if it fails

```yaml
name: "Resilient Email Sending"
steps:
  - id: send_via_primary
    mcp_server: gmail
    action: send_email
    params:
      to: "{{recipient}}"
      subject: "{{subject}}"
      body: "{{body}}"
    on_error: continue
    retry_count: 3

  - id: send_via_backup
    mcp_server: sendgrid
    action: send_email
    params:
      to: "{{recipient}}"
      subject: "{{subject}}"
      body: "{{body}}"
    condition: "{{steps.send_via_primary.status == 'failed'}}"
    depends_on: [send_via_primary]
```

## Pattern 5: Approval Gate

**Use case:** Require human approval before proceeding

```yaml
name: "Campaign Launch with Approval"
steps:
  - id: prepare_campaign
    action: generate_campaign
    params:
      template: "{{template_id}}"

  - id: approval_gate
    type: approval
    message: "Review campaign before sending to 10,000 customers"
    timeout: 3600
    depends_on: [prepare_campaign]

  - id: send_campaign
    action: send_bulk_email
    params:
      campaign_id: "{{steps.prepare_campaign.result.id}}"
    depends_on: [approval_gate]
```

## Pattern 6: Batch Processing with Loop

**Use case:** Process multiple items with the same action

```yaml
name: "Bulk User Onboarding"
variables:
  new_users:
    - email: "user1@example.com"
      name: "Alice"
    - email: "user2@example.com"
      name: "Bob"
    - email: "user3@example.com"
      name: "Charlie"

steps:
  - id: send_welcome_emails
    action: send_email
    for_each: "{{new_users}}"
    params:
      to: "{{item.email}}"
      subject: "Welcome {{item.name}}!"
      body: "Hello {{item.name}}, welcome to our platform!"
    max_parallel: 5
```

## Pattern 7: Aggregation Pattern

**Use case:** Collect results from multiple sources and combine

```yaml
name: "Multi-Source Data Aggregation"
steps:
  - id: fetch_from_db
    action: database_query
    params:
      query: "SELECT * FROM users"

  - id: fetch_from_api
    action: http_get
    params:
      url: "https://api.example.com/users"

  - id: fetch_from_file
    action: read_file
    params:
      path: "/data/users.json"

  - id: aggregate_data
    action: merge_data
    params:
      sources:
        - "{{steps.fetch_from_db.result}}"
        - "{{steps.fetch_from_api.result}}"
        - "{{steps.fetch_from_file.result}}"
    depends_on: [fetch_from_db, fetch_from_api, fetch_from_file]
```

## Pattern 8: Error Recovery with Rollback

**Use case:** Undo changes if workflow fails

```yaml
name: "Database Migration with Rollback"
steps:
  - id: backup_database
    action: create_backup
    params:
      database: "production"

  - id: run_migration
    action: execute_sql
    params:
      script: "migration_v2.sql"
    depends_on: [backup_database]
    rollback:
      action: restore_backup
      params:
        backup_id: "{{steps.backup_database.result.id}}"

  - id: verify_migration
    action: run_tests
    params:
      test_suite: "migration_tests"
    depends_on: [run_migration]
    rollback:
      action: restore_backup
      params:
        backup_id: "{{steps.backup_database.result.id}}"
```

## Pattern 9: Scheduled Workflow

**Use case:** Run workflow on a schedule

```yaml
name: "Daily Report Generation"
schedule:
  cron: "0 9 * * *"  # Every day at 9 AM
  timezone: "America/New_York"

steps:
  - id: generate_report
    action: create_report
    params:
      type: "daily_summary"
      date: "{{today}}"

  - id: send_report
    action: send_email
    params:
      to: "management@company.com"
      subject: "Daily Report - {{today}}"
      attachments:
        - "{{steps.generate_report.result.file_path}}"
    depends_on: [generate_report]
```

## Pattern 10: Event-Driven Workflow

**Use case:** Trigger workflow based on external event

```yaml
name: "New Customer Onboarding"
trigger:
  type: webhook
  path: "/webhooks/new-customer"

steps:
  - id: extract_customer_data
    action: parse_webhook
    params:
      payload: "{{trigger.payload}}"

  - id: create_account
    action: database_insert
    params:
      table: "customers"
      data: "{{steps.extract_customer_data.result}}"

  - id: send_welcome_email
    action: send_email
    params:
      to: "{{steps.extract_customer_data.result.email}}"
      subject: "Welcome!"
    depends_on: [create_account]

  - id: notify_sales_team
    action: send_slack_message
    params:
      channel: "#sales"
      text: "New customer: {{steps.extract_customer_data.result.name}}"
    depends_on: [create_account]
```

## Pattern 11: Saga Pattern (Distributed Transaction)

**Use case:** Coordinate transactions across multiple services

```yaml
name: "Order Fulfillment Saga"
steps:
  - id: reserve_inventory
    action: inventory_reserve
    params:
      product_id: "{{product_id}}"
      quantity: "{{quantity}}"
    rollback:
      action: inventory_release
      params:
        reservation_id: "{{steps.reserve_inventory.result.id}}"

  - id: charge_payment
    action: payment_charge
    params:
      customer_id: "{{customer_id}}"
      amount: "{{amount}}"
    depends_on: [reserve_inventory]
    rollback:
      action: payment_refund
      params:
        charge_id: "{{steps.charge_payment.result.id}}"

  - id: create_shipment
    action: shipping_create
    params:
      order_id: "{{order_id}}"
      address: "{{shipping_address}}"
    depends_on: [charge_payment]
    rollback:
      action: shipping_cancel
      params:
        shipment_id: "{{steps.create_shipment.result.id}}"

  - id: send_confirmation
    action: send_email
    params:
      to: "{{customer_email}}"
      subject: "Order Confirmed"
    depends_on: [create_shipment]
```

## Pattern 12: Circuit Breaker

**Use case:** Prevent cascading failures

```yaml
name: "API Call with Circuit Breaker"
steps:
  - id: call_external_api
    action: http_get
    params:
      url: "https://external-api.com/data"
    circuit_breaker:
      failure_threshold: 5
      timeout: 30
      reset_timeout: 300
    on_error: continue

  - id: use_cached_data
    action: get_from_cache
    params:
      key: "api_data"
    condition: "{{steps.call_external_api.status == 'failed'}}"
    depends_on: [call_external_api]
```

## Best Practices

### 1. Idempotency

Design steps to be safely retryable:

```yaml
steps:
  - id: create_user
    action: upsert_user  # Use upsert instead of insert
    params:
      email: "{{email}}"
      name: "{{name}}"
```

### 2. Timeouts

Always set appropriate timeouts:

```yaml
steps:
  - id: external_api_call
    action: http_get
    params:
      url: "{{api_url}}"
    timeout: 30  # 30 seconds
```

### 3. Error Handling

Define clear error handling strategy:

```yaml
steps:
  - id: risky_operation
    action: complex_task
    on_error: retry
    retry_count: 3
    retry_delay: 5
```

### 4. Logging

Log important information:

```yaml
steps:
  - id: process_payment
    action: charge_card
    params:
      amount: "{{amount}}"
    log_level: info
    log_fields:
      - customer_id
      - amount
      - transaction_id
```

### 5. Monitoring

Add health checks:

```yaml
steps:
  - id: health_check
    action: ping_service
    params:
      service: "payment_gateway"
    timeout: 5
```

## Anti-Patterns to Avoid

### 1. Tight Coupling

**Bad:**
```yaml
steps:
  - id: step1
    params:
      hardcoded_value: "specific_value"
```

**Good:**
```yaml
variables:
  config_value: "specific_value"

steps:
  - id: step1
    params:
      value: "{{config_value}}"
```

### 2. No Error Handling

**Bad:**
```yaml
steps:
  - id: critical_step
    action: important_operation
    # No error handling!
```

**Good:**
```yaml
steps:
  - id: critical_step
    action: important_operation
    on_error: retry
    retry_count: 3
```

### 3. Blocking Operations

**Bad:**
```yaml
steps:
  - id: long_running
    action: process_large_file
    timeout: 3600  # 1 hour!
```

**Good:**
```yaml
steps:
  - id: queue_job
    action: enqueue_processing
    params:
      file: "{{file_path}}"

  - id: poll_status
    action: check_job_status
    params:
      job_id: "{{steps.queue_job.result.id}}"
    retry_count: 60
    retry_delay: 60
```

### 4. Missing Dependencies

**Bad:**
```yaml
steps:
  - id: step2
    params:
      data: "{{steps.step1.result}}"
    # Missing depends_on!
```

**Good:**
```yaml
steps:
  - id: step2
    params:
      data: "{{steps.step1.result}}"
    depends_on: [step1]
```
