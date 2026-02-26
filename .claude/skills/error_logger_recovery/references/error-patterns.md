# Error Handling Patterns

This reference documents common error handling patterns for resilient systems.

## Pattern 1: Retry with Exponential Backoff

**Problem**: Transient failures in external services.

**Solution**: Retry with increasing delays.

```python
@retry_with_backoff(max_retries=5, base_delay=1)
def call_external_api():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

**When to Use**:
- Network operations
- API calls
- Database connections
- Temporary service unavailability

**Benefits**:
- Handles transient failures
- Prevents overwhelming services
- Industry-standard approach

---

## Pattern 2: Circuit Breaker

**Problem**: Cascading failures when a service is down.

**Solution**: Fail fast after threshold reached.

```python
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker
def call_unreliable_service():
    return service.call()
```

**States**:
- **Closed**: Normal operation
- **Open**: Failing fast
- **Half-Open**: Testing recovery

**When to Use**:
- Microservices architecture
- External dependencies
- Prevent cascading failures
- Resource protection

---

## Pattern 3: Fallback

**Problem**: Primary operation fails, need alternative.

**Solution**: Provide fallback mechanism.

```python
def get_user_data(user_id):
    try:
        return fetch_from_api(user_id)
    except Exception as e:
        logger.warning(f"API failed, using cache: {e}")
        return fetch_from_cache(user_id)
```

**When to Use**:
- Graceful degradation
- High availability requirements
- Multiple data sources
- User experience priority

---

## Pattern 4: Timeout

**Problem**: Operations hang indefinitely.

**Solution**: Set explicit timeouts.

```python
import requests

def call_api_with_timeout():
    try:
        response = requests.get(
            "https://api.example.com/data",
            timeout=10  # 10 seconds
        )
        return response.json()
    except requests.Timeout:
        logger.error("API call timed out")
        raise
```

**When to Use**:
- All external calls
- Network operations
- Database queries
- File operations

---

## Pattern 5: Bulkhead

**Problem**: One failing component affects entire system.

**Solution**: Isolate resources.

```python
from concurrent.futures import ThreadPoolExecutor

# Separate thread pools for different services
api_pool = ThreadPoolExecutor(max_workers=10)
db_pool = ThreadPoolExecutor(max_workers=5)

def call_api():
    return api_pool.submit(api_operation)

def call_db():
    return db_pool.submit(db_operation)
```

**When to Use**:
- Resource isolation
- Prevent resource exhaustion
- Multiple services
- Fault isolation

---

## Pattern 6: Fail Fast

**Problem**: Wasting resources on operations that will fail.

**Solution**: Validate early and fail immediately.

```python
def process_order(order):
    # Validate first
    if not order.customer_id:
        raise ValueError("Customer ID required")
    if order.amount <= 0:
        raise ValueError("Amount must be positive")

    # Then process
    return process(order)
```

**When to Use**:
- Input validation
- Precondition checks
- Resource availability
- Configuration errors

---

## Pattern 7: Error Classification

**Problem**: Different errors need different handling.

**Solution**: Classify and handle appropriately.

```python
classifier = ErrorClassifier()
classifier.add_transient(TimeoutError, ConnectionError)
classifier.add_permanent(ValueError, AuthenticationError)

try:
    operation()
except Exception as e:
    if classifier.is_transient(e):
        # Retry
        retry_operation()
    elif classifier.is_permanent(e):
        # Fail immediately
        handle_permanent_error(e)
    else:
        # Unknown, log and investigate
        logger.error(f"Unknown error: {e}")
```

**When to Use**:
- Complex error scenarios
- Multiple error types
- Automated error handling
- Retry logic

---

## Pattern 8: Graceful Degradation

**Problem**: Complete failure when optional features fail.

**Solution**: Continue with reduced functionality.

```python
def get_product_page(product_id):
    # Essential data
    product = get_product(product_id)

    # Optional enhancements
    try:
        recommendations = get_recommendations(product_id)
    except Exception as e:
        logger.warning(f"Recommendations failed: {e}")
        recommendations = []

    try:
        reviews = get_reviews(product_id)
    except Exception as e:
        logger.warning(f"Reviews failed: {e}")
        reviews = []

    return {
        'product': product,
        'recommendations': recommendations,
        'reviews': reviews
    }
```

**When to Use**:
- Optional features
- Non-critical functionality
- User experience priority
- High availability needs

---

## Pattern 9: Compensating Transaction

**Problem**: Need to undo operations after failure.

**Solution**: Implement rollback logic.

```python
def process_order(order):
    # Step 1: Reserve inventory
    reservation = reserve_inventory(order.items)

    try:
        # Step 2: Charge payment
        payment = charge_customer(order.customer, order.amount)

        try:
            # Step 3: Create shipment
            shipment = create_shipment(order)
            return shipment

        except Exception as e:
            # Rollback payment
            refund_customer(payment.id)
            raise

    except Exception as e:
        # Rollback inventory
        release_inventory(reservation.id)
        raise
```

**When to Use**:
- Distributed transactions
- Multi-step operations
- Data consistency requirements
- Saga pattern

---

## Pattern 10: Dead Letter Queue

**Problem**: Failed messages lost or block processing.

**Solution**: Move failed items to separate queue.

```python
def process_message(message):
    try:
        handle_message(message)
    except Exception as e:
        if message.retry_count < MAX_RETRIES:
            # Retry
            message.retry_count += 1
            requeue_message(message)
        else:
            # Move to dead letter queue
            logger.error(f"Message failed after {MAX_RETRIES} retries")
            dead_letter_queue.add(message)
```

**When to Use**:
- Message queues
- Batch processing
- Asynchronous operations
- Failure analysis

---

## Pattern 11: Health Check

**Problem**: Don't know if service is healthy.

**Solution**: Implement health endpoints.

```python
def health_check():
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'external_api': check_external_api()
    }

    all_healthy = all(checks.values())

    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks
    }

def check_database():
    try:
        db.execute("SELECT 1")
        return True
    except Exception:
        return False
```

**When to Use**:
- Microservices
- Load balancers
- Monitoring systems
- Auto-scaling

---

## Pattern 12: Idempotency

**Problem**: Retries cause duplicate operations.

**Solution**: Make operations idempotent.

```python
def process_payment(payment_id, amount):
    # Check if already processed
    if payment_exists(payment_id):
        logger.info(f"Payment {payment_id} already processed")
        return get_payment(payment_id)

    # Process payment
    result = charge_customer(amount)

    # Store with idempotency key
    store_payment(payment_id, result)

    return result
```

**When to Use**:
- Payment processing
- API endpoints
- Message processing
- Retry scenarios

---

## Pattern 13: Rate Limiting

**Problem**: Too many requests overwhelm service.

**Solution**: Limit request rate.

```python
from time import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = []

    def allow_request(self):
        now = time()
        # Remove old requests
        self.requests = [r for r in self.requests if r > now - self.window]

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

limiter = RateLimiter(max_requests=100, window_seconds=60)

def api_call():
    if not limiter.allow_request():
        raise RateLimitError("Too many requests")
    return make_request()
```

**When to Use**:
- API protection
- Resource management
- Cost control
- Fair usage

---

## Pattern 14: Saga Pattern

**Problem**: Distributed transactions across services.

**Solution**: Coordinate with compensating actions.

```python
class OrderSaga:
    def execute(self, order):
        steps = [
            (self.reserve_inventory, self.release_inventory),
            (self.charge_payment, self.refund_payment),
            (self.create_shipment, self.cancel_shipment)
        ]

        completed = []

        try:
            for action, compensation in steps:
                result = action(order)
                completed.append((compensation, result))

            return "Success"

        except Exception as e:
            # Rollback completed steps
            for compensation, result in reversed(completed):
                try:
                    compensation(result)
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            raise
```

**When to Use**:
- Microservices
- Distributed systems
- Long-running transactions
- Complex workflows

---

## Pattern 15: Retry Budget

**Problem**: Unlimited retries cause resource exhaustion.

**Solution**: Limit total retry attempts.

```python
class RetryBudget:
    def __init__(self, max_retries_per_minute=100):
        self.max_retries = max_retries_per_minute
        self.current_retries = 0
        self.window_start = time.time()

    def can_retry(self):
        # Reset window
        if time.time() - self.window_start > 60:
            self.current_retries = 0
            self.window_start = time.time()

        if self.current_retries < self.max_retries:
            self.current_retries += 1
            return True

        logger.warning("Retry budget exhausted")
        return False

budget = RetryBudget(max_retries_per_minute=100)

def operation_with_budget():
    if not budget.can_retry():
        raise RetryBudgetExhaustedError()

    return retry_operation()
```

**When to Use**:
- Prevent retry storms
- Resource protection
- Cost control
- SLA compliance

---

## Combining Patterns

### Retry + Circuit Breaker

```python
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker
@retry_with_backoff(max_retries=3)
def resilient_operation():
    return external_service.call()
```

### Retry + Fallback

```python
@retry_with_backoff(max_retries=3)
def primary_operation():
    return primary_service.call()

def operation_with_fallback():
    try:
        return primary_operation()
    except Exception:
        return fallback_service.call()
```

### Circuit Breaker + Fallback

```python
breaker = CircuitBreaker(failure_threshold=5)

@breaker
def primary_with_breaker():
    return primary_service.call()

def operation():
    try:
        return primary_with_breaker()
    except CircuitBreakerOpenError:
        return fallback_service.call()
```

---

## Anti-Patterns

### ❌ Swallowing Exceptions

```python
# Bad
try:
    operation()
except Exception:
    pass  # Silent failure!
```

### ❌ Catching Too Broadly

```python
# Bad
try:
    operation()
except Exception:  # Catches everything!
    retry()
```

### ❌ Retry Without Backoff

```python
# Bad
for i in range(10):
    try:
        operation()
        break
    except:
        pass  # Immediate retry!
```

### ❌ No Timeout

```python
# Bad
response = requests.get(url)  # Can hang forever!
```

### ❌ Nested Retries

```python
# Bad
@retry(max_retries=3)
def outer():
    @retry(max_retries=3)
    def inner():
        pass
    return inner()  # 9 total attempts!
```

---

## Best Practices Summary

1. **Classify errors** - transient vs permanent
2. **Use exponential backoff** for retries
3. **Set timeouts** on all external calls
4. **Implement circuit breakers** for protection
5. **Provide fallbacks** for graceful degradation
6. **Make operations idempotent** for safe retries
7. **Log all errors** with context
8. **Monitor retry rates** and failures
9. **Test error paths** thoroughly
10. **Document error handling** strategy
