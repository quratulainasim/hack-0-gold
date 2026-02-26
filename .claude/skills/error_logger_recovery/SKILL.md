---
name: error_logger_recovery
description: Implement exponential backoff retry logic and comprehensive error logging for resilient operations. Use this skill when the user asks to add retry logic, implement exponential backoff, add error logging, handle transient failures, implement circuit breakers, or build resilient error recovery systems.
license: MIT
---

# Error Logger & Recovery

This skill provides robust error handling, exponential backoff retry logic, and comprehensive logging for building resilient systems.

## Quick Start

### Basic Retry with Exponential Backoff

```python
from error_recovery import retry_with_backoff, logger

@retry_with_backoff(max_retries=3, base_delay=1, max_delay=60)
def call_external_api():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()

# Automatically retries with exponential backoff on failure
data = call_external_api()
```

### Circuit Breaker Pattern

```python
from error_recovery import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker
def unreliable_service():
    return external_service.call()

# Fails fast after threshold reached
result = unreliable_service()
```

## Features

### 1. Exponential Backoff

Automatically retry failed operations with increasing delays:

```python
@retry_with_backoff(
    max_retries=5,
    base_delay=1,        # Start with 1 second
    max_delay=60,        # Cap at 60 seconds
    exponential_base=2,  # Double each time
    jitter=True          # Add randomness
)
def flaky_operation():
    # Your code here
    pass
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 seconds delay
- Attempt 4: 4 seconds delay
- Attempt 5: 8 seconds delay
- Attempt 6: 16 seconds delay

### 2. Comprehensive Logging

Multi-level logging with structured output:

```python
from error_recovery import logger

logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical failure")

# Structured logging
logger.info("API call", extra={
    'endpoint': '/api/users',
    'method': 'GET',
    'status_code': 200,
    'duration_ms': 145
})
```

### 3. Circuit Breaker

Prevent cascading failures:

```python
breaker = CircuitBreaker(
    failure_threshold=5,    # Open after 5 failures
    timeout=60,             # Stay open for 60 seconds
    expected_exception=RequestException
)

@breaker
def call_service():
    return service.call()
```

**States**:
- **Closed**: Normal operation, requests pass through
- **Open**: Circuit tripped, requests fail fast
- **Half-Open**: Testing if service recovered

### 4. Retry Strategies

Multiple retry strategies available:

```python
# Fixed delay
@retry_fixed(max_retries=3, delay=5)
def operation1():
    pass

# Linear backoff
@retry_linear(max_retries=5, base_delay=2)
def operation2():
    pass

# Exponential backoff
@retry_exponential(max_retries=5, base_delay=1)
def operation3():
    pass

# Custom strategy
@retry_custom(strategy=my_strategy)
def operation4():
    pass
```

### 5. Error Classification

Classify errors for appropriate handling:

```python
from error_recovery import ErrorClassifier

classifier = ErrorClassifier()

# Transient errors - retry
classifier.add_transient(TimeoutError, ConnectionError)

# Permanent errors - don't retry
classifier.add_permanent(ValueError, AuthenticationError)

# Check error type
if classifier.is_transient(error):
    # Retry
    pass
elif classifier.is_permanent(error):
    # Fail immediately
    pass
```

## Usage Patterns

### API Calls with Retry

```python
import requests
from error_recovery import retry_with_backoff, logger

@retry_with_backoff(
    max_retries=3,
    base_delay=1,
    exceptions=(requests.RequestException,)
)
def fetch_user_data(user_id):
    logger.info(f"Fetching user data for {user_id}")

    try:
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
            timeout=10
        )
        response.raise_for_status()

        logger.info(f"Successfully fetched user {user_id}")
        return response.json()

    except requests.RequestException as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise
```

### Database Operations

```python
from error_recovery import retry_with_backoff, logger
import psycopg2

@retry_with_backoff(
    max_retries=5,
    base_delay=2,
    exceptions=(psycopg2.OperationalError,)
)
def execute_query(query, params):
    logger.debug(f"Executing query: {query}")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()

        logger.info(f"Query executed successfully, {len(result)} rows")
        return result

    except psycopg2.OperationalError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()
```

### File Operations

```python
from error_recovery import retry_with_backoff, logger
import os

@retry_with_backoff(
    max_retries=3,
    base_delay=1,
    exceptions=(IOError, OSError)
)
def write_file(filepath, content):
    logger.info(f"Writing to file: {filepath}")

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Successfully wrote {len(content)} bytes to {filepath}")

    except (IOError, OSError) as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        raise
```

### Batch Processing with Error Recovery

```python
from error_recovery import retry_with_backoff, logger

def process_batch(items):
    results = []
    errors = []

    for item in items:
        try:
            result = process_item_with_retry(item)
            results.append(result)
            logger.info(f"Processed item {item['id']}")

        except Exception as e:
            logger.error(f"Failed to process item {item['id']}: {e}")
            errors.append({'item': item, 'error': str(e)})

    logger.info(f"Batch complete: {len(results)} success, {len(errors)} errors")
    return results, errors

@retry_with_backoff(max_retries=3, base_delay=1)
def process_item_with_retry(item):
    # Processing logic
    return process(item)
```

## Configuration

### Logging Configuration

Configure logging in `logging_config.yaml`:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

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
    formatter: detailed
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/errors.log
    maxBytes: 10485760
    backupCount: 10

loggers:
  app:
    level: DEBUG
    handlers: [console, file, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

### Retry Configuration

Configure retry behavior in `retry_config.yaml`:

```yaml
retry:
  default:
    max_retries: 3
    base_delay: 1
    max_delay: 60
    exponential_base: 2
    jitter: true

  api_calls:
    max_retries: 5
    base_delay: 2
    max_delay: 120
    exponential_base: 2
    jitter: true

  database:
    max_retries: 5
    base_delay: 1
    max_delay: 30
    exponential_base: 2
    jitter: false

  file_operations:
    max_retries: 3
    base_delay: 0.5
    max_delay: 10
    exponential_base: 2
    jitter: false

circuit_breaker:
  default:
    failure_threshold: 5
    timeout: 60
    expected_exception: Exception

  external_api:
    failure_threshold: 10
    timeout: 120
    expected_exception: RequestException

error_classification:
  transient:
    - TimeoutError
    - ConnectionError
    - TemporaryFailure
    - ServiceUnavailable

  permanent:
    - ValueError
    - TypeError
    - AuthenticationError
    - PermissionError
```

## Advanced Features

### Custom Retry Strategy

```python
from error_recovery import RetryStrategy

class CustomRetryStrategy(RetryStrategy):
    def get_delay(self, attempt):
        # Custom delay calculation
        if attempt <= 3:
            return attempt * 2
        else:
            return 10

    def should_retry(self, attempt, exception):
        # Custom retry logic
        if attempt >= self.max_retries:
            return False
        if isinstance(exception, CriticalError):
            return False
        return True

@retry_custom(strategy=CustomRetryStrategy(max_retries=5))
def operation():
    pass
```

### Contextual Logging

```python
from error_recovery import LogContext

with LogContext(user_id=123, request_id='abc-123'):
    logger.info("Processing request")
    # All logs in this context include user_id and request_id
    process_request()
```

### Metrics and Monitoring

```python
from error_recovery import RetryMetrics

metrics = RetryMetrics()

@retry_with_backoff(max_retries=3, metrics=metrics)
def operation():
    pass

# Get metrics
print(f"Total attempts: {metrics.total_attempts}")
print(f"Successful: {metrics.successful}")
print(f"Failed: {metrics.failed}")
print(f"Average retries: {metrics.average_retries}")
```

### Async Support

```python
from error_recovery import async_retry_with_backoff
import asyncio

@async_retry_with_backoff(max_retries=3, base_delay=1)
async def async_operation():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com') as response:
            return await response.json()

# Use with asyncio
result = await async_operation()
```

## Best Practices

1. **Choose appropriate retry counts**: Don't retry indefinitely
2. **Use exponential backoff**: Prevents overwhelming services
3. **Add jitter**: Prevents thundering herd problem
4. **Log at appropriate levels**: Debug for details, Error for failures
5. **Classify errors**: Retry transient, fail fast on permanent
6. **Set timeouts**: Prevent hanging operations
7. **Monitor metrics**: Track retry rates and failures
8. **Use circuit breakers**: Protect against cascading failures
9. **Handle partial failures**: In batch operations
10. **Test error paths**: Ensure recovery logic works

## Error Handling Patterns

### Fail Fast

```python
@retry_with_backoff(
    max_retries=0,  # No retries
    exceptions=(ValueError,)
)
def validate_input(data):
    if not data:
        raise ValueError("Data cannot be empty")
    return data
```

### Graceful Degradation

```python
def get_user_data(user_id):
    try:
        return fetch_from_api(user_id)
    except Exception as e:
        logger.warning(f"API failed, using cache: {e}")
        return fetch_from_cache(user_id)
```

### Fallback Chain

```python
def get_data():
    try:
        return primary_source()
    except Exception:
        try:
            return secondary_source()
        except Exception:
            return default_data()
```

## Integration Examples

### With Flask

```python
from flask import Flask
from error_recovery import logger, retry_with_backoff

app = Flask(__name__)

@app.route('/api/users/<user_id>')
def get_user(user_id):
    try:
        user = fetch_user_with_retry(user_id)
        return jsonify(user)
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        return jsonify({'error': 'User not found'}), 404

@retry_with_backoff(max_retries=3)
def fetch_user_with_retry(user_id):
    return database.get_user(user_id)
```

### With Celery

```python
from celery import Celery
from error_recovery import retry_with_backoff, logger

app = Celery('tasks')

@app.task(bind=True)
@retry_with_backoff(max_retries=5, base_delay=2)
def process_task(self, data):
    logger.info(f"Processing task {self.request.id}")
    try:
        result = process(data)
        logger.info(f"Task {self.request.id} completed")
        return result
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {e}")
        raise
```

For detailed retry strategies, see [references/retry-strategies.md](references/retry-strategies.md).

For logging best practices, see [references/logging-guide.md](references/logging-guide.md).

For error handling patterns, see [references/error-patterns.md](references/error-patterns.md).
