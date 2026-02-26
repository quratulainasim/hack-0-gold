---
name: business_handover_audit
description: Generate comprehensive weekly financial and performance review reports for business handover. Use this skill when the user asks to create weekly audit reports, generate business performance reviews, prepare handover documentation, create executive summaries, audit vault metrics, or compile weekly business status reports.
license: MIT
---

# Business Handover Audit

This skill generates comprehensive weekly financial and performance review reports, ideal for business handovers, executive reviews, and stakeholder updates.

## Quick Start

Generate weekly audit report:

```bash
python scripts/audit.py --vault-path /path/to/vault --output Weekly_Audit.md
```

Generate with specific date range:

```bash
python scripts/audit.py --vault-path /path/to/vault --start-date 2026-02-12 --end-date 2026-02-19 --output Weekly_Audit.md
```

## Workflow

1. **Scan vault folders**: Analyze /Done, /Needs_Action, /Pending_Approval, /Approved
2. **Extract metrics**: Count completed items, pending items, financial data
3. **Calculate KPIs**: Revenue, expenses, task completion rate, approval rate
4. **Identify trends**: Week-over-week changes, patterns, anomalies
5. **Generate insights**: Key wins, concerns, recommendations
6. **Create report**: Formatted executive summary with actionable insights

## Report Structure

Generated reports follow this comprehensive format:

```markdown
# Weekly Business Audit Report
**Week of**: February 12-19, 2026
**Generated**: 2026-02-19 17:00:00
**Reporting Period**: 7 days

---

## Executive Summary

**Overall Status**: 🟢 Healthy

This week showed strong performance with 15 completed tasks, $125K in revenue, and 3 new customer acquisitions. All critical items are on track. One medium-priority concern requires attention regarding Q1 budget utilization.

**Key Highlights**:
- ✅ Revenue target exceeded by 12%
- ✅ Customer satisfaction at 94%
- ⚠️ Q1 budget 78% utilized with 6 weeks remaining

---

## Financial Performance

### Revenue
- **This Week**: $125,000
- **Last Week**: $112,000
- **Change**: +$13,000 (+11.6%)
- **MTD**: $487,000
- **Target**: $500,000 (97.4% achieved)

### Expenses
- **This Week**: $45,000
- **Last Week**: $42,000
- **Change**: +$3,000 (+7.1%)
- **MTD**: $178,000
- **Budget**: $200,000 (89% utilized)

### Profit
- **This Week**: $80,000
- **Last Week**: $70,000
- **Margin**: 64%
- **MTD**: $309,000

### Cash Flow
- **Opening Balance**: $450,000
- **Closing Balance**: $530,000
- **Net Change**: +$80,000
- **Runway**: 11.8 months

---

## Operational Metrics

### Task Completion
- **Completed**: 15 tasks
- **In Progress**: 8 tasks
- **Pending**: 5 tasks
- **Completion Rate**: 65%

### Customer Metrics
- **New Customers**: 3
- **Churned Customers**: 1
- **Net Growth**: +2
- **Total Active**: 127
- **Satisfaction Score**: 94%

### Team Performance
- **Emails Sent**: 47
- **LinkedIn Posts**: 8
- **Meetings Held**: 12
- **Response Time**: 2.3 hours avg

---

## Completed Work (15 items)

### High Priority (5)
1. ✅ **Q1 Marketing Campaign** - Launched successfully, 10K pre-orders achieved
2. ✅ **Client Proposal - Enterprise Corp** - Approved, $50K contract signed
3. ✅ **Infrastructure Migration** - Completed with zero downtime
4. ✅ **Product Feature Release** - Deployed to production
5. ✅ **Security Audit** - Passed with no critical findings

### Medium Priority (7)
1. ✅ Website redesign mockups approved
2. ✅ Q1 budget review completed
3. ✅ Team training session delivered
4. ✅ Customer onboarding automation implemented
5. ✅ API documentation updated
6. ✅ Monthly newsletter sent (5K subscribers)
7. ✅ Vendor contract renewal negotiated

### Low Priority (3)
1. ✅ Office supplies restocked
2. ✅ Team social event organized
3. ✅ Internal wiki updated

---

## Pending Items

### Needs Action (5 items)
1. 🔴 **High**: Q2 Strategic Planning - Due in 3 days
2. 🔴 **High**: Client escalation - Response overdue
3. 🟡 **Medium**: Hiring pipeline review
4. 🟡 **Medium**: Expense report submission
5. 🟢 **Low**: Team feedback survey

### Pending Approval (3 items)
1. 🔴 **High**: $75K marketing budget request
2. 🟡 **Medium**: New hire offer letter
3. 🟡 **Medium**: Vendor contract amendment

### In Progress (8 items)
1. Website redesign implementation (60% complete)
2. Q2 product roadmap (40% complete)
3. Customer success playbook (75% complete)
4. Sales pipeline optimization (30% complete)
5. Security compliance certification (50% complete)
6. Team expansion planning (25% complete)
7. Partnership negotiations (80% complete)
8. Process documentation (45% complete)

---

## Key Wins 🎉

1. **Revenue Growth**: Exceeded weekly target by 12%, driven by 3 new customer acquisitions
2. **Product Launch**: Successfully deployed major feature with positive customer feedback
3. **Infrastructure**: Completed cloud migration with zero downtime and 30% cost reduction
4. **Marketing**: Q1 campaign achieved 10K pre-orders, exceeding goal by 25%
5. **Team**: Hired 2 new team members, expanding capacity by 20%

---

## Concerns & Risks ⚠️

### High Priority
- **Q1 Budget Utilization**: 78% spent with 6 weeks remaining - may need reallocation
- **Client Escalation**: Response overdue by 2 days - requires immediate attention

### Medium Priority
- **Hiring Pipeline**: Only 3 candidates in pipeline for 5 open positions
- **Q2 Planning**: Behind schedule, needs acceleration to meet deadline

### Low Priority
- **Documentation**: Some processes still undocumented
- **Team Feedback**: Survey response rate at 60%, target is 80%

---

## Trends & Insights

### Week-over-Week Trends
- Revenue: ↗️ +11.6% (3-week upward trend)
- Task completion: ↗️ +20% (improved efficiency)
- Customer acquisition: ↗️ +50% (2 vs 3 new customers)
- Response time: ↘️ -15% (faster responses)

### Month-to-Date Performance
- Revenue: 97.4% of target (on track)
- Expenses: 89% of budget (under budget)
- Customer growth: 8% (exceeding 5% target)
- Task completion: 68% avg (above 65% target)

### Notable Patterns
- Marketing campaigns driving consistent customer acquisition
- Infrastructure investments yielding cost savings
- Team productivity improving with new tools
- Customer satisfaction stable at 94%

---

## Recommendations

### Immediate Actions (This Week)
1. **Address client escalation** - Assign senior team member, respond within 24 hours
2. **Review Q1 budget** - Reallocate remaining funds to high-priority initiatives
3. **Accelerate Q2 planning** - Schedule focused planning sessions

### Short-term Actions (Next 2 Weeks)
1. **Boost hiring pipeline** - Increase recruiting efforts, engage headhunter
2. **Approve pending items** - Clear approval backlog to unblock team
3. **Document key processes** - Prioritize critical workflows

### Strategic Recommendations
1. **Maintain marketing momentum** - Continue successful campaign strategies
2. **Invest in automation** - Customer onboarding success suggests broader opportunities
3. **Scale team strategically** - Hire ahead of Q2 growth projections
4. **Optimize budget allocation** - Shift funds from under-utilized areas to high-ROI initiatives

---

## Action Items for Next Week

### Critical
- [ ] Resolve client escalation
- [ ] Complete Q2 strategic planning
- [ ] Review and reallocate Q1 budget

### Important
- [ ] Approve pending budget request
- [ ] Accelerate hiring pipeline
- [ ] Clear approval backlog

### Routine
- [ ] Continue website redesign
- [ ] Progress Q2 roadmap
- [ ] Submit expense reports

---

## Appendix

### Detailed Metrics
- Total vault items: 156
- Items in Done: 89
- Items in Needs_Action: 5
- Items in Pending_Approval: 3
- Items in Approved: 12
- Items in Progress: 8

### Financial Details
- Largest revenue source: Enterprise contracts ($75K)
- Largest expense: Payroll ($28K)
- Outstanding invoices: $45K
- Accounts receivable: 18 days avg

### Team Metrics
- Team size: 12
- Utilization rate: 87%
- Overtime hours: 15
- PTO taken: 8 days

---

**Report prepared by**: Business Audit System
**Next review**: February 26, 2026
**Questions**: Contact finance@company.com
```

## Data Sources

The audit pulls data from:

### Vault Folders
- **/Done**: Completed tasks and deliverables
- **/Needs_Action**: Items requiring attention
- **/Pending_Approval**: Items awaiting approval
- **/Approved**: Approved items ready for execution
- **/In_Progress**: Active work items

### Metadata Extraction
From frontmatter in markdown files:
- `type`: Task type (plan, email, expense, etc.)
- `priority`: Priority level (high, medium, low)
- `amount`: Financial amounts
- `status`: Current status
- `completed_date`: Completion timestamp
- `customer`: Customer information
- `revenue`: Revenue data
- `cost`: Cost/expense data

### Calculated Metrics
- Revenue totals and trends
- Expense totals and trends
- Task completion rates
- Customer acquisition/churn
- Response times
- Budget utilization

## Configuration

Configure audit parameters in `audit_config.yaml`:

```yaml
reporting:
  period: "weekly"  # daily, weekly, monthly
  start_day: "monday"
  include_weekends: false

metrics:
  revenue_target: 500000  # Monthly target
  expense_budget: 200000  # Monthly budget
  task_completion_target: 0.65  # 65%
  customer_growth_target: 0.05  # 5%
  response_time_target: 4  # hours

thresholds:
  revenue_warning: 0.90  # Warn if below 90% of target
  expense_warning: 0.95  # Warn if above 95% of budget
  task_backlog_warning: 10  # Warn if >10 pending tasks
  approval_backlog_warning: 5  # Warn if >5 pending approvals

categories:
  revenue_sources:
    - "Enterprise Contracts"
    - "SMB Subscriptions"
    - "Professional Services"
    - "Other"

  expense_categories:
    - "Payroll"
    - "Marketing"
    - "Infrastructure"
    - "Operations"
    - "Other"

alerts:
  enabled: true
  email_recipients:
    - "ceo@company.com"
    - "cfo@company.com"
  conditions:
    - metric: "revenue"
      threshold: 0.90
      message: "Revenue below 90% of target"
    - metric: "expenses"
      threshold: 0.95
      message: "Expenses above 95% of budget"
```

## Advanced Features

### Trend Analysis

Compare multiple periods:

```bash
python scripts/audit.py --vault-path ./vault --compare-periods 4 --output Trend_Report.md
```

Shows 4-week trend analysis with charts.

### Custom Metrics

Define custom metrics:

```yaml
custom_metrics:
  - name: "Customer Lifetime Value"
    formula: "total_revenue / total_customers"
    target: 50000

  - name: "Team Efficiency"
    formula: "completed_tasks / team_size"
    target: 1.5
```

### Export Formats

Export to different formats:

```bash
# Markdown (default)
python scripts/audit.py --vault-path ./vault --output report.md

# JSON for dashboards
python scripts/audit.py --vault-path ./vault --format json --output report.json

# CSV for spreadsheets
python scripts/audit.py --vault-path ./vault --format csv --output report.csv

# PDF for distribution
python scripts/audit.py --vault-path ./vault --format pdf --output report.pdf
```

### Automated Scheduling

Schedule weekly audits:

```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/vault && python scripts/audit.py --vault-path . --output Weekly_Audit_$(date +\%Y\%m\%d).md
```

## Integration with Other Skills

Works seamlessly with:

- **metric-auditor**: Provides detailed metrics for audit
- **update-dashboard**: Displays audit summary on dashboard
- **approval-monitor**: Tracks approval metrics
- **strategic-planner**: Reviews plan execution
- **executor**: Monitors execution progress

## Best Practices

1. **Run weekly**: Consistent timing for trend analysis
2. **Review thoroughly**: Don't just generate, actually review
3. **Act on insights**: Use recommendations to drive decisions
4. **Track trends**: Compare week-over-week for patterns
5. **Share widely**: Distribute to stakeholders
6. **Archive reports**: Keep historical record
7. **Update targets**: Adjust targets based on performance
8. **Customize metrics**: Track what matters to your business

## Use Cases

### Weekly Executive Review
Generate comprehensive report for CEO/leadership team review.

### Board Meeting Preparation
Compile performance data for board presentations.

### Investor Updates
Create investor-ready performance summaries.

### Business Handover
Document current state for transition/handover.

### Performance Tracking
Monitor KPIs and progress toward goals.

### Budget Management
Track financial performance against budget.

For detailed metric definitions, see [references/metrics-guide.md](references/metrics-guide.md).

For report customization, see [references/report-templates.md](references/report-templates.md).
