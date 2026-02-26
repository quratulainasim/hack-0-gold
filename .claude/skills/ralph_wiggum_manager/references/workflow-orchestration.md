# Workflow Orchestration Patterns

This reference documents workflow orchestration patterns for the Ralph Wiggum Manager.

## Overview

The manager orchestrates a complete workflow cycle through five stages:

1. **Inbox → Triage** - Process incoming items
2. **Needs_Action → Planning** - Create strategic plans
3. **Pending_Approval → Approval** - Human review gate
4. **Approved → Execution** - Execute approved actions
5. **Done → Audit** - Generate metrics and reports

---

## Pattern 1: Sequential Processing

**Description**: Process stages one at a time in order.

**When to Use**:
- Simple workflows
- Limited resources
- Dependencies between stages
- Single-threaded execution

**Implementation**:

```python
def run_sequential_cycle(self):
    stages = [
        self._process_inbox,
        self._process_needs_action,
        self._process_pending_approval,
        self._process_approved,
        self._process_done
    ]

    for stage in stages:
        if not stage():
            self.logger.warning(f"Stage {stage.__name__} failed")
            # Continue to next stage
```

**Benefits**:
- Simple to understand
- Predictable execution order
- Easy to debug
- No race conditions

**Drawbacks**:
- Slower overall throughput
- Idle resources during sequential execution

---

## Pattern 2: Parallel Processing

**Description**: Process multiple stages simultaneously.

**When to Use**:
- Independent stages
- High throughput requirements
- Multiple CPU cores available
- No shared state between stages

**Implementation**:

```python
from concurrent.futures import ThreadPoolExecutor

def run_parallel_cycle(self):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(self._process_inbox): 'inbox',
            executor.submit(self._process_needs_action): 'needs_action',
            executor.submit(self._process_approved): 'approved'
        }

        for future in as_completed(futures):
            stage_name = futures[future]
            try:
                result = future.result()
                self.logger.info(f"Stage {stage_name} completed: {result}")
            except Exception as e:
                self.logger.error(f"Stage {stage_name} failed: {e}")
```

**Benefits**:
- Higher throughput
- Better resource utilization
- Faster overall cycle time

**Drawbacks**:
- More complex
- Potential race conditions
- Harder to debug

---

## Pattern 3: Priority-Based Processing

**Description**: Process high-priority items first.

**When to Use**:
- Items have different urgency levels
- SLA requirements
- Critical items need fast processing
- Resource constraints

**Implementation**:

```python
def get_items_by_priority(self, folder_path):
    items = []
    for file_path in folder_path.glob('*.md'):
        with open(file_path, 'r') as f:
            content = f.read()
            # Extract priority from frontmatter
            priority = self._extract_priority(content)
            items.append((priority, file_path))

    # Sort by priority (1=highest)
    items.sort(key=lambda x: x[0])
    return [item[1] for item in items]

def _process_inbox_with_priority(self):
    items = self.get_items_by_priority(self.folders['Inbox'].path)

    for item in items:
        self._process_item(item)
```

**Benefits**:
- Critical items processed first
- Better SLA compliance
- Flexible prioritization

**Drawbacks**:
- Low-priority items may starve
- More complex logic
- Priority management overhead

---

## Pattern 4: Batch Processing

**Description**: Process multiple items together.

**When to Use**:
- High volume of items
- Efficiency gains from batching
- API rate limits
- Reduce overhead

**Implementation**:

```python
def process_batch(self, items, batch_size=10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]

        try:
            self._process_item_batch(batch)
            self.logger.info(f"Processed batch of {len(batch)} items")
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            # Process individually as fallback
            for item in batch:
                try:
                    self._process_item(item)
                except Exception as item_error:
                    self.logger.error(f"Item {item} failed: {item_error}")
```

**Benefits**:
- Higher throughput
- Reduced overhead
- Better API utilization
- Efficient resource usage

**Drawbacks**:
- All-or-nothing failures
- More complex error handling
- Delayed feedback

---

## Pattern 5: Conditional Execution

**Description**: Execute stages based on conditions.

**When to Use**:
- Dynamic workflows
- Resource optimization
- Conditional logic
- Skip unnecessary work

**Implementation**:

```python
def run_conditional_cycle(self):
    # Always check inbox
    self._process_inbox()

    # Only plan if items need action
    if self.folders['Needs_Action'].item_count > 5:
        self._process_needs_action()

    # Only check approvals during business hours
    if self._is_business_hours():
        self._process_pending_approval()

    # Execute if approved items exist
    if self.folders['Approved'].item_count > 0:
        self._process_approved()

    # Audit once per day
    if self._should_run_daily_audit():
        self._process_done()
```

**Benefits**:
- Efficient resource usage
- Skip unnecessary work
- Flexible execution
- Context-aware processing

**Drawbacks**:
- More complex logic
- Harder to predict behavior
- Testing complexity

---

## Pattern 6: Event-Driven Processing

**Description**: React to events rather than polling.

**When to Use**:
- Real-time requirements
- Reduce polling overhead
- Event-based architecture
- Immediate response needed

**Implementation**:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class VaultEventHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_created(self, event):
        if event.is_directory:
            return

        # Determine which folder changed
        folder = Path(event.src_path).parent.name

        if folder == 'Inbox':
            self.manager._process_inbox()
        elif folder == 'Approved':
            self.manager._process_approved()

def run_event_driven(self):
    event_handler = VaultEventHandler(self)
    observer = Observer()
    observer.schedule(event_handler, self.vault_path, recursive=True)
    observer.start()

    try:
        while self.running:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
```

**Benefits**:
- Immediate response
- No polling overhead
- Real-time processing
- Efficient resource usage

**Drawbacks**:
- More complex setup
- Event handling overhead
- Potential event storms
- Platform-specific behavior

---

## Pattern 7: State Machine Orchestration

**Description**: Manage workflow as explicit state machine.

**When to Use**:
- Complex workflows
- Clear state transitions
- Error recovery
- Audit requirements

**Implementation**:

```python
class WorkflowState(Enum):
    IDLE = "idle"
    TRIAGING = "triaging"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    AUDITING = "auditing"
    ERROR = "error"

def transition_state(self, new_state: WorkflowState):
    old_state = self.state
    self.state = new_state

    self.logger.info(f"State transition: {old_state.value} → {new_state.value}")

    # Trigger state-specific actions
    if new_state == WorkflowState.ERROR:
        self._handle_error_state()
    elif new_state == WorkflowState.IDLE:
        self._handle_idle_state()

def run_state_machine(self):
    while self.running:
        if self.state == WorkflowState.IDLE:
            self.transition_state(WorkflowState.TRIAGING)

        elif self.state == WorkflowState.TRIAGING:
            if self._process_inbox():
                self.transition_state(WorkflowState.PLANNING)
            else:
                self.transition_state(WorkflowState.ERROR)

        # ... handle other states
```

**Benefits**:
- Clear state management
- Easy to reason about
- Good for auditing
- Error recovery support

**Drawbacks**:
- More boilerplate
- State explosion risk
- Rigid structure

---

## Pattern 8: Retry with Backoff

**Description**: Retry failed operations with increasing delays.

**When to Use**:
- Transient failures
- External dependencies
- Network operations
- Rate limiting

**Implementation**:

```python
def execute_with_retry(self, operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = 2 ** attempt  # Exponential backoff
            self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            time.sleep(delay)
```

**Benefits**:
- Handles transient failures
- Prevents overwhelming services
- Industry standard approach

**Drawbacks**:
- Increased latency
- May mask real issues
- Resource consumption

---

## Pattern 9: Circuit Breaker

**Description**: Fail fast when service is unhealthy.

**When to Use**:
- Protect downstream services
- Prevent cascading failures
- Fast failure detection
- Resource protection

**Implementation**:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, operation):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise CircuitBreakerOpenError()

        try:
            result = operation()
            self.failures = 0
            self.state = 'closed'
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = 'open'

            raise
```

**Benefits**:
- Fast failure
- Protects services
- Prevents cascading failures

**Drawbacks**:
- May reject valid requests
- Requires tuning
- State management complexity

---

## Pattern 10: Graceful Degradation

**Description**: Continue with reduced functionality on failure.

**When to Use**:
- Optional features
- High availability requirements
- User experience priority
- Non-critical failures

**Implementation**:

```python
def run_cycle_with_degradation(self):
    # Critical operations
    self._process_inbox()
    self._process_approved()

    # Optional operations - continue on failure
    try:
        self._process_needs_action()
    except Exception as e:
        self.logger.warning(f"Planning failed, continuing: {e}")

    try:
        self._process_done()
    except Exception as e:
        self.logger.warning(f"Audit failed, continuing: {e}")
```

**Benefits**:
- High availability
- Better user experience
- Partial functionality maintained

**Drawbacks**:
- Incomplete operations
- May hide issues
- Complex error handling

---

## Combining Patterns

### Sequential + Retry

```python
def run_resilient_sequential(self):
    stages = [
        self._process_inbox,
        self._process_needs_action,
        self._process_approved
    ]

    for stage in stages:
        self.execute_with_retry(stage, max_retries=3)
```

### Parallel + Circuit Breaker

```python
def run_protected_parallel(self):
    breakers = {
        'inbox': CircuitBreaker(),
        'needs_action': CircuitBreaker(),
        'approved': CircuitBreaker()
    }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(breakers['inbox'].call, self._process_inbox): 'inbox',
            executor.submit(breakers['needs_action'].call, self._process_needs_action): 'needs_action',
            executor.submit(breakers['approved'].call, self._process_approved): 'approved'
        }
```

### Priority + Batch

```python
def run_priority_batch(self):
    items = self.get_items_by_priority(self.folders['Inbox'].path)

    # Process high-priority items individually
    high_priority = [item for item in items if self._get_priority(item) == 1]
    for item in high_priority:
        self._process_item(item)

    # Batch process normal priority
    normal_priority = [item for item in items if self._get_priority(item) > 1]
    self.process_batch(normal_priority, batch_size=10)
```

---

## Best Practices

1. **Start Simple**: Begin with sequential processing, add complexity as needed
2. **Monitor Performance**: Track cycle times and throughput
3. **Handle Errors Gracefully**: Don't let one failure stop the entire workflow
4. **Log State Transitions**: Make debugging easier
5. **Test Each Pattern**: Verify behavior under load
6. **Document Decisions**: Explain why you chose each pattern
7. **Measure Impact**: Quantify improvements from each pattern
8. **Plan for Failure**: Design for resilience from the start
9. **Keep It Maintainable**: Complexity should be justified
10. **Review Regularly**: Patterns may need adjustment over time
