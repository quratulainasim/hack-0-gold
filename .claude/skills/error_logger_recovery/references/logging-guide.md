# Logging Best Practices Guide

This reference documents logging best practices for error recovery systems.

## Logging Levels

### DEBUG
**When to use**: Detailed diagnostic information for troubleshooting.

```python
logger.debug("Processing item", item_id=123, status="pending")
logger.debug(f"Query: {query}, Params: {params}")
```

**Examples**:
- Function entry/exit
- Variable values
- Loop iterations
- Detailed state information

**Production**: Usually disabled for performance.

---

### INFO
**When to use**: General informational messages about normal operation.

```python
logger.info("User logged in", user_id=456, ip="192.168.1.1")
logger.info("Task completed successfully", task_id=789, duration_ms=1234)
```

**Examples**:
- Successful operations
- State changes
- Milestones reached
- Configuration loaded

**Production**: Enabled, but not verbose.

---

### WARNING
**When to use**: Something unexpected but recoverable happened.

```python
logger.warning("Retry attempt", attempt=2, max_retries=3, error="Connection timeout")
logger.warning("Cache miss", key="user:123", fallback="database")
```

**Examples**:
- Retry attempts
- Deprecated features used
- Configuration issues
- Performance degradation
- Fallback mechanisms triggered

**Production**: Always enabled.

---

### ERROR
**When to use**: An error occurred that prevented an operation from completing.

```python
logger.error("Failed to process payment",
    order_id=123,
    error=str(e),
    exc_info=True
)
```

**Examples**:
- Operation failures
- Exceptions caught
- Data validation errors
- External service failures

**Production**: Always enabled, often triggers alerts.

---

### CRITICAL
**When to use**: A serious error that may cause system failure.

```python
logger.critical("Database connection lost",
    database="production",
    exc_info=True
)
```

**Examples**:
- System failures
- Data corruption
- Security breaches
- Resource exhaustion

**Production**: Always enabled, triggers immediate alerts.

---

## Structured Logging

### Basic Structure

```python
logger.info("User action",
    user_id=123,
    action="purchase",
    item_id=456,
    amount=99.99,
    timestamp=datetime.now().isoformat()
)
```

### JSON Format

```json
{
  "timestamp": "2026-02-19T14:30:00Z",
  "level": "INFO",
  "message": "User action",
  "user_id": 123,
  "action": "purchase",
  "item_id": 456,
  "amount": 99.99
}
```

### Benefits
- Machine-readable
- Easy to parse
- Searchable
- Aggregatable

---

## Context Logging

### Using Context Managers

```python
with LogContext(request_id="abc-123", user_id=456):
    logger.info("Processing request")
    process_order()
    logger.info("Request completed")

# All logs include request_id and user_id
```

### Thread-Local Context

```python
import threading

class ThreadLocalContext:
    _context = threading.local()

    @classmethod
    def set(cls, **kwargs):
        if not hasattr(cls._context, 'data'):
            cls._context.data = {}
        cls._context.data.update(kwargs)

    @classmethod
    def get(cls):
        if not hasattr(cls._context, 'data'):
            return {}
        return cls._context.data.copy()
```

---

## Performance Logging

### Execution Time

```python
@log_execution_time
def slow_operation():
    time.sleep(2)
    return "Done"

# Logs: "slow_operation completed in 2.003s"
```

### Custom Timing

```python
import time

start = time.time()
try:
    result = operation()
    duration = time.time() - start
    logger.info("Operation succeeded", duration_ms=duration*1000)
except Exception as e:
    duration = time.time() - start
    logger.error("Operation failed", duration_ms=duration*1000, error=str(e))
```

---

## Error Logging

### With Stack Traces

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
    # Includes full stack trace
```

### Without Stack Traces

```python
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    # Just the error message
```

### Custom Error Context

```python
try:
    process_item(item)
except Exception as e:
    logger.error("Failed to process item",
        item_id=item.id,
        item_type=item.type,
        error_type=type(e).__name__,
        error_message=str(e),
        exc_info=True
    )
```

---

## Log Rotation

### File Size Based

```python
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Time Based

```python
handler = logging.handlers.TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=30
)
```

---

## Log Aggregation

### Centralized Logging

```python
import logging
from logging.handlers import SysLogHandler

# Send to syslog
syslog = SysLogHandler(address=('logs.example.com', 514))
logger.addHandler(syslog)
```

### Cloud Logging

```python
# AWS CloudWatch
import watchtower

handler = watchtower.CloudWatchLogHandler(
    log_group='my-app',
    stream_name='production'
)
logger.addHandler(handler)
```

---

## Sensitive Data

### Redacting Secrets

```python
def redact_sensitive(data):
    """Redact sensitive fields"""
    sensitive_fields = ['password', 'api_key', 'token', 'ssn']

    if isinstance(data, dict):
        return {
            k: '***REDACTED***' if k in sensitive_fields else v
            for k, v in data.items()
        }
    return data

logger.info("User data", data=redact_sensitive(user_data))
```

### Masking

```python
def mask_email(email):
    """Mask email address"""
    local, domain = email.split('@')
    return f"{local[0]}***@{domain}"

logger.info("Email sent", to=mask_email(recipient))
```

---

## Sampling

### Rate Limiting Logs

```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def should_log(key, interval=60):
    """Rate limit logs by key"""
    return True

def rate_limited_log(message, **kwargs):
    key = f"{message}:{kwargs.get('error_type')}"
    if should_log(key):
        logger.warning(message, **kwargs)
```

### Sampling High-Volume Logs

```python
import random

def sample_log(message, sample_rate=0.1, **kwargs):
    """Log only a sample of messages"""
    if random.random() < sample_rate:
        logger.debug(message, **kwargs)
```

---

## Correlation IDs

### Request Tracking

```python
import uuid

def process_request(request):
    correlation_id = str(uuid.uuid4())

    with LogContext(correlation_id=correlation_id):
        logger.info("Request started")
        result = handle_request(request)
        logger.info("Request completed")

    return result
```

### Distributed Tracing

```python
def call_service(service_name, correlation_id):
    headers = {'X-Correlation-ID': correlation_id}

    logger.info("Calling service",
        service=service_name,
        correlation_id=correlation_id
    )

    response = requests.get(
        f"https://{service_name}/api",
        headers=headers
    )

    return response
```

---

## Testing Logs

### Capturing Logs in Tests

```python
import logging
from io import StringIO

def test_logging():
    # Capture logs
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger.addHandler(handler)

    # Run code
    my_function()

    # Check logs
    log_output = log_stream.getvalue()
    assert "Expected message" in log_output
```

### Mock Logging

```python
from unittest.mock import patch

def test_error_logging():
    with patch('myapp.logger') as mock_logger:
        my_function()

        # Verify error was logged
        mock_logger.error.assert_called_once()
```

---

## Configuration Examples

### Basic Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Advanced Configuration (YAML)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: json
    filename: logs/app.log
    maxBytes: 10485760
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: logs/errors.log
    maxBytes: 10485760
    backupCount: 10

loggers:
  myapp:
    level: DEBUG
    handlers: [console, file, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console]
```

---

## Best Practices Summary

### ✅ Do

1. **Use appropriate log levels**
2. **Include context** (user_id, request_id, etc.)
3. **Log exceptions with stack traces** (`exc_info=True`)
4. **Use structured logging** for machine parsing
5. **Rotate log files** to prevent disk fill
6. **Redact sensitive data** before logging
7. **Use correlation IDs** for request tracking
8. **Monitor log volume** and sample if needed
9. **Test logging** in unit tests
10. **Centralize logs** in production

### ❌ Don't

1. **Don't log passwords or secrets**
2. **Don't log in tight loops** without sampling
3. **Don't use print()** instead of logger
4. **Don't log at DEBUG level** in production
5. **Don't ignore log rotation**
6. **Don't log PII** without consent
7. **Don't use string formatting** in log calls
8. **Don't catch and log without re-raising**
9. **Don't log the same error** multiple times
10. **Don't forget to configure handlers**

---

## Common Patterns

### Retry Logging

```python
@retry_with_backoff(
    max_retries=3,
    on_retry=lambda e, attempt, delay:
        logger.warning(
            "Retry attempt",
            attempt=attempt,
            max_retries=3,
            delay_seconds=delay,
            error=str(e)
        )
)
def operation():
    pass
```

### Circuit Breaker Logging

```python
class CircuitBreaker:
    def _on_failure(self):
        self.failure_count += 1
        logger.warning(
            "Circuit breaker failure",
            failure_count=self.failure_count,
            threshold=self.failure_threshold
        )

        if self.failure_count >= self.failure_threshold:
            logger.error(
                "Circuit breaker opened",
                failure_count=self.failure_count
            )
            self.state = CircuitState.OPEN
```

### Batch Processing Logging

```python
def process_batch(items):
    logger.info("Batch started", item_count=len(items))

    success_count = 0
    error_count = 0

    for item in items:
        try:
            process_item(item)
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error("Item failed", item_id=item.id, error=str(e))

    logger.info("Batch completed",
        total=len(items),
        success=success_count,
        errors=error_count
    )
```

---

## Monitoring and Alerts

### Log-Based Alerts

```python
# Alert on high error rate
if error_count > 100:
    logger.critical("High error rate detected",
        error_count=error_count,
        threshold=100,
        alert=True
    )
```

### Metrics from Logs

```python
# Track operation duration
logger.info("Operation completed",
    operation="user_login",
    duration_ms=duration,
    status="success"
)

# Can be aggregated to:
# - Average login time
# - Success rate
# - P95/P99 latency
```

---

## Tools and Libraries

### Python Logging Libraries

- **logging**: Built-in, standard library
- **loguru**: Simplified logging with better defaults
- **structlog**: Structured logging
- **python-json-logger**: JSON formatting

### Log Aggregation

- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Splunk**: Enterprise log management
- **Datadog**: Cloud monitoring and logging
- **CloudWatch**: AWS logging service
- **Stackdriver**: Google Cloud logging

### Log Analysis

- **Kibana**: Visualization for Elasticsearch
- **Grafana**: Metrics and logs visualization
- **Papertrail**: Simple log aggregation
- **Loggly**: Cloud-based log management
