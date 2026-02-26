# Approval Workflow Patterns

This reference documents common approval workflow patterns and best practices.

## Pattern 1: Single Approver (CEO/Manager)

**Structure:**
```
Item → Pending_Approval → [CEO Review] → Approved/Rejected
```

**When to use:**
- Small organizations
- Clear decision authority
- Fast decision-making needed
- Low-risk items

**Example:**
```yaml
workflow:
  approver: "CEO"
  threshold: "all items"
  sla: "24 hours"
```

**Pros:**
- Fast decisions
- Clear accountability
- Simple process

**Cons:**
- Single point of failure
- Can become bottleneck
- No checks and balances

---

## Pattern 2: Tiered Approval (By Value)

**Structure:**
```
Item → Check Value → Route to Appropriate Approver
  - <$10k → Manager
  - $10k-$50k → Director
  - >$50k → CEO
```

**When to use:**
- Different risk levels
- Delegation needed
- Scale operations
- Clear value thresholds

**Example:**
```yaml
tiers:
  - threshold: 10000
    approver: "Manager"
    sla: "4 hours"

  - threshold: 50000
    approver: "Director"
    sla: "24 hours"

  - threshold: 999999999
    approver: "CEO"
    sla: "48 hours"
```

**Pros:**
- Scales well
- Appropriate oversight
- Empowers managers

**Cons:**
- More complex
- Requires clear thresholds
- Potential for gaming

---

## Pattern 3: Sequential Approval Chain

**Structure:**
```
Item → Manager → Director → VP → CEO
```

**When to use:**
- High-risk decisions
- Regulatory requirements
- Multiple stakeholders
- Consensus needed

**Example:**
```yaml
chain:
  - role: "Manager"
    can_reject: true
  - role: "Director"
    can_reject: true
  - role: "VP"
    can_reject: true
  - role: "CEO"
    final: true
```

**Pros:**
- Multiple reviews
- Shared responsibility
- Thorough vetting

**Cons:**
- Slow process
- Can be bureaucratic
- Any level can block

---

## Pattern 4: Parallel Approval (Consensus)

**Structure:**
```
Item → [Legal, Finance, Operations] → All Must Approve
```

**When to use:**
- Cross-functional impact
- Multiple domains affected
- Risk mitigation
- Compliance requirements

**Example:**
```yaml
parallel:
  approvers:
    - "Legal"
    - "Finance"
    - "Operations"
  requirement: "all"  # or "majority"
```

**Pros:**
- Comprehensive review
- Multiple perspectives
- Risk reduction

**Cons:**
- Slowest process
- Coordination overhead
- Potential deadlock

---

## Pattern 5: Conditional Routing

**Structure:**
```
Item → Check Type/Category → Route to Specialist
  - Legal matters → Legal team
  - Financial → CFO
  - Technical → CTO
  - Marketing → CMO
```

**When to use:**
- Specialized expertise needed
- Different approval authorities
- Domain-specific decisions

**Example:**
```yaml
routing:
  - type: "legal"
    approver: "Legal Team"

  - type: "financial"
    approver: "CFO"

  - type: "technical"
    approver: "CTO"

  - type: "marketing"
    approver: "CMO"
```

**Pros:**
- Expert review
- Appropriate authority
- Efficient routing

**Cons:**
- Requires categorization
- Multiple approval paths
- Coordination needed

---

## Pattern 6: Escalation on Timeout

**Structure:**
```
Item → Primary Approver (24h) → If No Response → Escalate to Manager
```

**When to use:**
- Prevent bottlenecks
- Ensure timely decisions
- Handle absences
- Maintain SLAs

**Example:**
```yaml
escalation:
  primary: "Manager"
  timeout: "24 hours"
  escalate_to: "Director"
  final_timeout: "48 hours"
  final_escalate_to: "CEO"
```

**Pros:**
- Prevents delays
- Handles absences
- Maintains flow

**Cons:**
- Can bypass intended approver
- Requires monitoring
- May rush decisions

---

## Pattern 7: Auto-Approve with Audit

**Structure:**
```
Item → Check Criteria → If Meets Rules → Auto-Approve → Log for Audit
```

**When to use:**
- Low-risk items
- Routine decisions
- Clear criteria
- High volume

**Example:**
```yaml
auto_approve:
  rules:
    - type: "email"
      cost: 0
      priority: "low"

    - type: "expense"
      cost: "<100"
      category: "office_supplies"

  audit: true
  review_frequency: "monthly"
```

**Pros:**
- Fast processing
- Reduces workload
- Consistent decisions

**Cons:**
- Less oversight
- Requires good rules
- Audit burden

---

## Pattern 8: Peer Review

**Structure:**
```
Item → Random Peer(s) → Approve/Reject → Log Decision
```

**When to use:**
- Distributed teams
- Shared responsibility
- Knowledge sharing
- Quality control

**Example:**
```yaml
peer_review:
  pool: ["Dev1", "Dev2", "Dev3", "Dev4"]
  required_approvals: 2
  exclude_submitter: true
```

**Pros:**
- Distributed authority
- Knowledge sharing
- Team involvement

**Cons:**
- Variable quality
- Coordination overhead
- Potential bias

---

## Best Practices

### 1. Define Clear Criteria

**Good:**
```yaml
approval_criteria:
  budget:
    low: "<$10,000"
    medium: "$10,000-$50,000"
    high: ">$50,000"

  risk:
    low: "Reversible, no customer impact"
    medium: "Some customer impact, reversible"
    high: "Irreversible or major customer impact"
```

**Bad:**
```yaml
approval_criteria:
  budget: "depends"
  risk: "use judgment"
```

### 2. Set SLAs

```yaml
slas:
  high_priority: "4 hours"
  medium_priority: "24 hours"
  low_priority: "72 hours"

  escalation_after: "2x SLA"
```

### 3. Document Decisions

```markdown
## Approval Decision

**Approved by**: CEO
**Date**: 2026-02-19
**Rationale**: Aligns with Q1 strategy, budget approved, low risk

**Conditions**:
- Must complete by end of Q1
- Weekly progress reports required
- Budget cap at $50k
```

### 4. Track Metrics

```yaml
metrics:
  - approval_time_avg
  - approval_rate
  - rejection_rate
  - escalation_rate
  - bottleneck_analysis
  - approver_workload
```

### 5. Handle Exceptions

```yaml
exceptions:
  urgent:
    sla: "1 hour"
    notify: ["CEO", "COO"]
    escalate_immediately: true

  high_value:
    require_board_approval: true
    minimum_notice: "7 days"
```

---

## Common Pitfalls

### 1. Too Many Approvers
**Problem**: Slows everything down
**Solution**: Use tiered or conditional routing

### 2. Unclear Criteria
**Problem**: Inconsistent decisions
**Solution**: Document clear thresholds and examples

### 3. No Escalation Path
**Problem**: Items stuck indefinitely
**Solution**: Implement timeout-based escalation

### 4. No Audit Trail
**Problem**: Can't review decisions
**Solution**: Log all actions with rationale

### 5. Rigid Process
**Problem**: Can't handle exceptions
**Solution**: Build in flexibility for urgent items

---

## Approval Checklist

Before approving, verify:

- [ ] Objective is clear and aligned with strategy
- [ ] Budget is within approved limits
- [ ] Resources are available
- [ ] Timeline is realistic
- [ ] Risks are identified and acceptable
- [ ] Success criteria are defined
- [ ] Stakeholders are informed
- [ ] Compliance requirements met
- [ ] Rollback plan exists (if applicable)
- [ ] Monitoring plan in place

---

## Rejection Guidelines

When rejecting, provide:

1. **Clear reason**: Specific issue that led to rejection
2. **Actionable feedback**: What needs to change
3. **Alternative suggestions**: Other approaches to consider
4. **Resubmission process**: How to address and resubmit

**Good rejection:**
```
Rejected: Budget exceeds Q1 allocation by $25k

Feedback:
- Reduce scope to fit $50k budget, OR
- Defer to Q2 when more budget available, OR
- Identify cost savings in other areas

To resubmit: Update budget section and resubmit to Pending_Approval
```

**Bad rejection:**
```
Rejected: Too expensive
```

---

## Integration Patterns

### With Strategic Planning
```
strategic-planner → Creates Plan.md → Pending_Approval → approval_monitor
```

### With Execution
```
approval_monitor → Approves → Moves to /Approved → executor → Executes
```

### With Metrics
```
approval_monitor → Logs decisions → metric-auditor → Tracks approval metrics
```

### With Dashboard
```
approval_monitor → Status updates → update-dashboard → Displays approval queue
```
