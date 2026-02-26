# Retry Strategies Guide

This reference documents different retry strategies and when to use them.

## Strategy Comparison

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| Fixed Delay | Simple operations, predictable load | Simple, predictable | Can overwhelm service |
| Linear Backoff | Moderate load, gradual recovery | Balanced approach | May be too slow |
| Exponential Backoff | High load, distributed systems | Prevents overload | Can be too aggressive |
| Jittered Exponential | Multiple clients, prevent thundering herd | Best for distributed | More complex |

---

## Fixed Delay Strategy

**Pattern**: Wait same amount of time between each retry.

```python
@retry_fixed(max_retries=3, delay=5)
def operation():
    pass
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 5s delay
- Attempt 3: 5s delay
- Attempt 4: 5s delay

**When to Use**:
- Simple operations
- Low traffic scenarios
- Known recovery time
- Testing/development

**Avoid When**:
- High traffic
- Shared resources
- Multiple clients
- Unknown failure cause

---

## Linear Backoff Strategy

**Pattern**: Increase delay linearly with each retry.

```python
@retry_linear(max_retries=5, base_delay=2)
def operation():
    pass
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 2s delay
- Attempt 3: 4s delay
- Attempt 4: 6s delay
- Attempt 5: 8s delay
- Attempt 6: 10s delay

**When to Use**:
- Moderate traffic
- Gradual service recovery
- Database operations
- File system operations

**Formula**: `delay = base_delay * attempt`

---

## Exponential Backoff Strategy

**Pattern**: Double delay with each retry.

```python
@retry_with_backoff(
    max_retries=5,
    base_delay=1,
    exponential_base=2
)
def operation():
    pass
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 1s delay
- Attempt 3: 2s delay
- Attempt 4: 4s delay
- Attempt 5: 8s delay
- Attempt 6: 16s delay

**When to Use**:
- API calls
- Network operations
- Distributed systems
- High traffic scenarios
- Rate-limited services

**Formula**: `delay = base_delay * (exponential_base ^ attempt)`

**Advantages**:
- Quickly backs off under load
- Prevents overwhelming services
- Industry standard for APIs
- Works well with rate limits

---

## Exponential Backoff with Jitter

**Pattern**: Add randomness to exponential backoff.

```python
@retry_with_backoff(
    max_retries=5,
    base_delay=1,
    exponential_base=2,
    jitter=True
)
def operation():
    pass
```

**Retry Schedule** (with jitter):
- Attempt 1: Immediate
- Attempt 2: 0.5-1.5s delay (random)
- Attempt 3: 1-3s delay (random)
- Attempt 4: 2-6s delay (random)
- Attempt 5: 4-12s delay (random)
- Attempt 6: 8-24s delay (random)

**When to Use**:
- Multiple clients
- Prevent thundering herd
- Distributed systems
- Cloud services
- Microservices

**Formula**: `delay = (base_delay * exponential_base ^ attempt) * random(0.5, 1.5)`

**Why Jitter Matters**:
- Prevents synchronized retries
- Distributes load over time
- Reduces peak traffic
- Improves overall success rate

---

## Capped Exponential Backoff

**Pattern**: Exponential backoff with maximum delay.

```python
@retry_with_backoff(
    max_retries=10,
    base_delay=1,
    max_delay=60,
    exponential_base=2
)
def operation():
    pass
```

**Retry Schedule**:
- Attempts 1-6: As exponential (1s, 2s, 4s, 8s, 16s, 32s)
- Attempts 7+: Capped at 60s

**When to Use**:
- Long-running operations
- Many retry attempts
- Prevent excessive delays
- Balance persistence with responsiveness

---

## Adaptive Retry Strategy

**Pattern**: Adjust strategy based on error type.

```python
class AdaptiveRetryStrategy(RetryStrategy):
    def get_delay(self, attempt, exception):
        if isinstance(exception, RateLimitError):
            # Longer delay for rate limits
            return 60
        elif isinstance(exception, TimeoutError):
            # Exponential for timeouts
            return 2 ** attempt
        else:
            # Fixed for others
            return 5
```

**When to Use**:
- Multiple error types
- Different failure modes
- Complex systems
- Fine-tuned control

---

## Retry Budget Strategy

**Pattern**: Limit total retry time or attempts across all operations.

```python
class RetryBudget:
    def __init__(self, max_retries_per_minute=100):
        self.max_retries = max_retries_per_minute
        self.current_retries = 0
        self.window_start = time.time()

    def can_retry(self):
        # Reset window if needed
        if time.time() - self.window_start > 60:
            self.current_retries = 0
            self.window_start = time.time()

        if self.current_retries < self.max_retries:
            self.current_retries += 1
            return True
        return False
```

**When to Use**:
- Prevent retry storms
- Protect system resources
- SLA compliance
- Cost control

---

## Choosing the Right Strategy

### Decision Tree

```
Is this a distributed system with multiple clients?
├─ Yes → Use Exponential Backoff with Jitter
└─ No
   ├─ Is the service rate-limited?
   │  ├─ Yes → Use Exponential Backoff (capped)
   │  └─ No
   │     ├─ Is recovery time predictable?
   │     │  ├─ Yes → Use Fixed Delay
   │     │  └─ No → Use Linear Backoff
```

### By Service Type

**External APIs**:
- Strategy: Exponential with jitter
- Max retries: 5-7
- Base delay: 1-2s
- Max delay: 60-120s

**Databases**:
- Strategy: Exponential (no jitter)
- Max retries: 3-5
- Base delay: 0.5-1s
- Max delay: 10-30s

**File Operations**:
- Strategy: Fixed or Linear
- Max retries: 3
- Delay: 0.5-1s

**Microservices**:
- Strategy: Exponential with jitter
- Max retries: 3-5
- Base delay: 0.5-1s
- Max delay: 10-30s

**Message Queues**:
- Strategy: Exponential
- Max retries: 5-10
- Base delay: 1s
- Max delay: 300s

---

## Advanced Patterns

### Retry with Timeout

```python
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

@retry_with_backoff(max_retries=3)
def operation_with_timeout():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    try:
        result = slow_operation()
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError:
        signal.alarm(0)
        raise
```

### Retry with Circuit Breaker

```python
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker
@retry_with_backoff(max_retries=3)
def operation():
    return external_service.call()
```

### Conditional Retry

```python
def should_retry(exception):
    # Only retry on specific errors
    return isinstance(exception, (TimeoutError, ConnectionError))

@retry_with_backoff(
    max_retries=3,
    exceptions=(TimeoutError, ConnectionError)
)
def operation():
    pass
```

### Retry with Fallback

```python
@retry_with_backoff(max_retries=3)
def primary_operation():
    return primary_service.call()

def operation_with_fallback():
    try:
        return primary_operation()
    except Exception:
        logger.warning("Primary failed, using fallback")
        return fallback_service.call()
```

---

## Best Practices

### 1. Set Appropriate Limits

```python
# Good: Reasonable limits
@retry_with_backoff(
    max_retries=5,
    max_delay=60
)

# Bad: Unlimited retries
@retry_with_backoff(
    max_retries=999,
    max_delay=3600
)
```

### 2. Use Jitter in Distributed Systems

```python
# Good: Prevents thundering herd
@retry_with_backoff(jitter=True)

# Bad: Synchronized retries
@retry_with_backoff(jitter=False)
```

### 3. Log Retry Attempts

```python
@retry_with_backoff(
    max_retries=3,
    on_retry=lambda e, attempt, delay:
        logger.warning(f"Retry {attempt}: {e}, waiting {delay}s")
)
```

### 4. Classify Errors

```python
# Retry transient errors only
@retry_with_backoff(
    exceptions=(TimeoutError, ConnectionError)
)
def operation():
    pass
```

### 5. Monitor Retry Metrics

```python
metrics = RetryMetrics()

@retry_with_backoff(max_retries=3, metrics=metrics)
def operation():
    pass

# Check metrics
if metrics.average_retries > 2:
    alert("High retry rate detected")
```

---

## Anti-Patterns

### ❌ Retry Everything

```python
# Bad: Retries even on permanent errors
@retry_with_backoff(exceptions=(Exception,))
def operation():
    validate_input()  # Should fail fast
```

### ❌ No Maximum Delay

```python
# Bad: Delays can grow unbounded
@retry_with_backoff(
    max_retries=10,
    base_delay=1,
    max_delay=None  # No cap!
)
```

### ❌ Retry Without Logging

```python
# Bad: Silent retries
@retry_with_backoff(max_retries=5)
def operation():
    pass  # No logging!
```

### ❌ Nested Retries

```python
# Bad: Exponential retry explosion
@retry_with_backoff(max_retries=3)
def outer():
    @retry_with_backoff(max_retries=3)
    def inner():
        pass
    return inner()  # 3 * 3 = 9 total attempts!
```

---

## Testing Retry Logic

### Simulate Failures

```python
class FlakyService:
    def __init__(self, fail_count=2):
        self.fail_count = fail_count
        self.attempts = 0

    def call(self):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise ConnectionError("Simulated failure")
        return "Success"

# Test
service = FlakyService(fail_count=2)

@retry_with_backoff(max_retries=3)
def test_operation():
    return service.call()

result = test_operation()
assert result == "Success"
assert service.attempts == 3
```

### Test Retry Limits

```python
def test_max_retries():
    attempts = 0

    @retry_with_backoff(max_retries=3)
    def always_fails():
        nonlocal attempts
        attempts += 1
        raise Exception("Always fails")

    with pytest.raises(Exception):
        always_fails()

    assert attempts == 4  # Initial + 3 retries
```

---

## Performance Considerations

### Total Retry Time

Calculate maximum time spent retrying:

**Exponential (base=2, max_delay=60)**:
- 3 retries: ~7 seconds
- 5 retries: ~31 seconds
- 7 retries: ~60+ seconds (capped)

**Linear (base_delay=2)**:
- 3 retries: ~12 seconds
- 5 retries: ~30 seconds

**Fixed (delay=5)**:
- 3 retries: ~15 seconds
- 5 retries: ~25 seconds

### Resource Usage

- Each retry consumes resources
- Consider connection pools
- Monitor memory usage
- Set appropriate timeouts
- Use circuit breakers for protection
