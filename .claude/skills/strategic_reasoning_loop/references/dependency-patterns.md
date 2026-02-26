# Dependency Patterns

This reference documents common dependency patterns and when to use them.

## Pattern 1: Sequential Chain

**Structure:**
```
T1 → T2 → T3 → T4
```

**When to use:**
- Each task builds directly on the previous one
- No opportunities for parallelization
- Linear workflow with clear progression

**Example:**
```yaml
tasks:
  - id: T1
    name: "Design database schema"
    dependencies: []

  - id: T2
    name: "Implement database migrations"
    dependencies: [T1]

  - id: T3
    name: "Create data access layer"
    dependencies: [T2]

  - id: T4
    name: "Build API endpoints"
    dependencies: [T3]
```

**Characteristics:**
- Longest critical path
- No parallelization
- Clear dependencies
- Easy to understand

---

## Pattern 2: Parallel Streams

**Structure:**
```
T1 → T2 → T3
T4 → T5 → T6
```

**When to use:**
- Independent workstreams
- Different team members or teams
- No shared dependencies
- Maximize parallelization

**Example:**
```yaml
tasks:
  # Frontend stream
  - id: T1
    name: "Design UI mockups"
    dependencies: []

  - id: T2
    name: "Implement React components"
    dependencies: [T1]

  - id: T3
    name: "Add frontend tests"
    dependencies: [T2]

  # Backend stream
  - id: T4
    name: "Design API specification"
    dependencies: []

  - id: T5
    name: "Implement API endpoints"
    dependencies: [T4]

  - id: T6
    name: "Add API tests"
    dependencies: [T5]
```

**Characteristics:**
- Maximum parallelization
- Independent progress tracking
- Can have different timelines
- Requires coordination at integration points

---

## Pattern 3: Fan-Out (Divergence)

**Structure:**
```
    T1
   ↙ ↓ ↘
  T2 T3 T4
```

**When to use:**
- One task enables multiple parallel tasks
- Common foundation for different features
- Distribute work after setup phase

**Example:**
```yaml
tasks:
  - id: T1
    name: "Setup project infrastructure"
    dependencies: []

  - id: T2
    name: "Implement authentication"
    dependencies: [T1]

  - id: T3
    name: "Implement product catalog"
    dependencies: [T1]

  - id: T4
    name: "Implement payment system"
    dependencies: [T1]
```

**Characteristics:**
- Single bottleneck at start
- High parallelization after initial task
- Good for distributing work
- Common in project kickoffs

---

## Pattern 4: Fan-In (Convergence)

**Structure:**
```
  T1 T2 T3
   ↘ ↓ ↙
     T4
```

**When to use:**
- Multiple tasks must complete before next phase
- Integration or testing phase
- Combining parallel workstreams

**Example:**
```yaml
tasks:
  - id: T1
    name: "Implement user service"
    dependencies: []

  - id: T2
    name: "Implement product service"
    dependencies: []

  - id: T3
    name: "Implement order service"
    dependencies: []

  - id: T4
    name: "Integration testing"
    dependencies: [T1, T2, T3]
```

**Characteristics:**
- Bottleneck at convergence point
- Requires all dependencies complete
- Common for testing/integration phases
- Risk of delays if any dependency slips

---

## Pattern 5: Diamond (Fan-Out + Fan-In)

**Structure:**
```
    T1
   ↙  ↘
  T2   T3
   ↘  ↙
    T4
```

**When to use:**
- Parallel work that must reconverge
- Most common pattern in real projects
- Balance between parallelization and integration

**Example:**
```yaml
tasks:
  - id: T1
    name: "Design system architecture"
    dependencies: []

  - id: T2
    name: "Implement backend API"
    dependencies: [T1]

  - id: T3
    name: "Implement frontend UI"
    dependencies: [T1]

  - id: T4
    name: "End-to-end testing"
    dependencies: [T2, T3]
```

**Characteristics:**
- Very common pattern
- Good balance of parallelization
- Clear integration point
- Manageable complexity

---

## Pattern 6: Layered Dependencies

**Structure:**
```
T1 → T2 → T4
T1 → T3 → T4
```

**When to use:**
- Multiple paths to same goal
- Shared foundation, different implementations
- Redundancy or alternatives

**Example:**
```yaml
tasks:
  - id: T1
    name: "Setup infrastructure"
    dependencies: []

  - id: T2
    name: "Implement REST API"
    dependencies: [T1]

  - id: T3
    name: "Implement GraphQL API"
    dependencies: [T1]

  - id: T4
    name: "Deploy to production"
    dependencies: [T2, T3]
```

**Characteristics:**
- Multiple paths converge
- Flexibility in execution
- Can prioritize one path
- Good for alternatives/options

---

## Pattern 7: Milestone Gates

**Structure:**
```
T1 → T2 → [GATE] → T3 → T4 → [GATE] → T5
```

**When to use:**
- Approval or review required
- Quality gates
- Phase transitions
- Stakeholder checkpoints

**Example:**
```yaml
tasks:
  - id: T1
    name: "Requirements gathering"
    dependencies: []

  - id: T2
    name: "Design document"
    dependencies: [T1]

  - id: GATE1
    name: "Design review and approval"
    dependencies: [T2]

  - id: T3
    name: "Implementation"
    dependencies: [GATE1]

  - id: T4
    name: "Testing"
    dependencies: [T3]

  - id: GATE2
    name: "QA approval"
    dependencies: [T4]

  - id: T5
    name: "Production deployment"
    dependencies: [GATE2]
```

**Characteristics:**
- Explicit approval points
- Prevents premature progression
- Good for governance
- Can introduce delays

---

## Pattern 8: Iterative Cycles

**Structure:**
```
T1 → T2 → T3 → T4
      ↑_______↓
```

**When to use:**
- Agile/iterative development
- Continuous improvement
- Feedback loops
- Refinement cycles

**Example:**
```yaml
tasks:
  - id: T1
    name: "Sprint planning"
    dependencies: []

  - id: T2
    name: "Development sprint"
    dependencies: [T1]

  - id: T3
    name: "Sprint review"
    dependencies: [T2]

  - id: T4
    name: "Sprint retrospective"
    dependencies: [T3]

  # Next iteration
  - id: T5
    name: "Next sprint planning"
    dependencies: [T4]
```

**Characteristics:**
- Cyclical pattern
- Continuous improvement
- Feedback incorporated
- Common in agile methodologies

---

## Pattern 9: Conditional Branches

**Structure:**
```
T1 → T2 → [Decision]
           ↙      ↘
          T3      T4
```

**When to use:**
- Decision points in workflow
- Alternative paths based on outcomes
- Risk mitigation strategies

**Example:**
```yaml
tasks:
  - id: T1
    name: "Evaluate build vs buy"
    dependencies: []

  - id: T2
    name: "Decision: Build or Buy"
    dependencies: [T1]

  # Build path
  - id: T3
    name: "Custom development"
    dependencies: [T2]
    condition: "if build"

  # Buy path
  - id: T4
    name: "Vendor integration"
    dependencies: [T2]
    condition: "if buy"
```

**Characteristics:**
- Mutually exclusive paths
- Decision-driven
- Flexibility in approach
- Requires clear decision criteria

---

## Pattern 10: Dependency Matrix (Complex)

**Structure:**
```
T1 → T3 → T5
T2 → T3 → T6
T2 → T4 → T6
```

**When to use:**
- Complex projects with many interdependencies
- Multiple shared dependencies
- Large-scale initiatives

**Example:**
```yaml
tasks:
  - id: T1
    name: "Backend infrastructure"
    dependencies: []

  - id: T2
    name: "Frontend infrastructure"
    dependencies: []

  - id: T3
    name: "Authentication service"
    dependencies: [T1, T2]

  - id: T4
    name: "UI component library"
    dependencies: [T2]

  - id: T5
    name: "Admin API"
    dependencies: [T1, T3]

  - id: T6
    name: "Admin dashboard"
    dependencies: [T3, T4]
```

**Characteristics:**
- High complexity
- Many interdependencies
- Requires careful coordination
- Common in large projects

---

## Anti-Patterns to Avoid

### 1. Circular Dependencies

**Bad:**
```
T1 → T2 → T3 → T1  ❌
```

**Problem:** Impossible to execute, creates deadlock

**Solution:** Break the cycle by removing or reordering dependencies

---

### 2. Over-Serialization

**Bad:**
```
T1 → T2 → T3 → T4 → T5 → T6  ❌
```

**Problem:** No parallelization, unnecessarily long timeline

**Solution:** Identify tasks that can run in parallel

**Better:**
```
T1 → T2 → T4
T1 → T3 → T5
```

---

### 3. Dependency Overload

**Bad:**
```
T10 depends on: [T1, T2, T3, T4, T5, T6, T7, T8, T9]  ❌
```

**Problem:** Too many dependencies, high risk of delays

**Solution:** Group related tasks or create intermediate milestones

**Better:**
```
T1, T2, T3 → T7 (milestone)
T4, T5, T6 → T8 (milestone)
T7, T8 → T10
```

---

### 4. Orphaned Tasks

**Bad:**
```
T1 → T2 → T3
T4 (no dependencies, nothing depends on it)  ❌
```

**Problem:** Unclear purpose, may be forgotten

**Solution:** Connect to main workflow or remove if unnecessary

---

## Choosing the Right Pattern

### Consider:

1. **Team size**: More parallel streams with larger teams
2. **Risk tolerance**: More gates for risk-averse projects
3. **Complexity**: Simpler patterns for straightforward projects
4. **Timeline**: More parallelization for tight deadlines
5. **Dependencies**: Natural dependencies dictate structure

### Decision Matrix:

| Project Type | Recommended Pattern |
|--------------|-------------------|
| Simple, linear | Sequential Chain |
| Multiple teams | Parallel Streams |
| After setup phase | Fan-Out |
| Before integration | Fan-In |
| Balanced project | Diamond |
| High governance | Milestone Gates |
| Agile development | Iterative Cycles |
| Complex enterprise | Dependency Matrix |

---

## Best Practices

1. **Minimize dependencies**: Only add necessary dependencies
2. **Maximize parallelization**: Find opportunities for concurrent work
3. **Clear milestones**: Use convergence points as milestones
4. **Document rationale**: Explain why dependencies exist
5. **Review regularly**: Dependencies may change as project evolves
6. **Validate logic**: Ensure dependencies make logical sense
7. **Consider resources**: Don't over-parallelize beyond team capacity
8. **Plan for delays**: Critical path tasks need buffer time
