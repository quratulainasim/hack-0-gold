# Metrics Guide

This reference documents all metrics tracked by the business audit system.

## Financial Metrics

### Revenue
**Definition**: Total income from all sources during the reporting period.

**Calculation**: Sum of all items with `type: invoice`, `type: sale`, `type: revenue`, or `type: payment_received`.

**Sources**:
- Customer invoices
- Subscription payments
- Service fees
- Product sales

**Targets**:
- Weekly: $125,000
- Monthly: $500,000
- Quarterly: $1,500,000

**Thresholds**:
- 🟢 Green: ≥100% of target
- 🟡 Yellow: 90-99% of target
- 🔴 Red: <90% of target

---

### Expenses
**Definition**: Total costs and expenditures during the reporting period.

**Calculation**: Sum of all items with `type: expense`, `type: bill`, `type: payment`, or `type: cost`.

**Categories**:
- Payroll (40-50% of revenue)
- Marketing (10-15% of revenue)
- Infrastructure (5-10% of revenue)
- Operations (10-15% of revenue)
- Other (5-10% of revenue)

**Budget**:
- Weekly: $45,000
- Monthly: $200,000
- Quarterly: $600,000

**Thresholds**:
- 🟢 Green: ≤90% of budget
- 🟡 Yellow: 91-95% of budget
- 🔴 Red: >95% of budget

---

### Profit
**Definition**: Revenue minus expenses.

**Calculation**: `profit = revenue - expenses`

**Target Margin**: 60-70%

**Interpretation**:
- >70%: Excellent, consider reinvestment
- 60-70%: Healthy, sustainable
- 50-60%: Acceptable, monitor closely
- <50%: Concerning, review costs

---

### Cash Flow
**Definition**: Net change in cash position.

**Components**:
- Operating cash flow
- Investing cash flow
- Financing cash flow

**Runway**: Months of operation at current burn rate.

**Calculation**: `runway = cash_balance / monthly_expenses`

**Thresholds**:
- 🟢 Green: >12 months
- 🟡 Yellow: 6-12 months
- 🔴 Red: <6 months

---

## Operational Metrics

### Task Completion Rate
**Definition**: Percentage of tasks completed vs. total tasks.

**Calculation**: `completion_rate = completed_tasks / total_tasks`

**Target**: 65%

**Interpretation**:
- >80%: Excellent productivity
- 65-80%: Good, on target
- 50-65%: Below target, investigate
- <50%: Poor, immediate action needed

---

### Task Backlog
**Definition**: Number of tasks in Needs_Action folder.

**Target**: <10 items

**Thresholds**:
- 🟢 Green: 0-5 items
- 🟡 Yellow: 6-10 items
- 🔴 Red: >10 items

**Action Required**:
- >20 items: Emergency triage needed
- >15 items: Prioritize and delegate
- >10 items: Review and clear backlog

---

### Approval Backlog
**Definition**: Number of items in Pending_Approval folder.

**Target**: <5 items

**SLA**: Items should be approved within 48 hours.

**Thresholds**:
- 🟢 Green: 0-3 items
- 🟡 Yellow: 4-5 items
- 🔴 Red: >5 items

---

### Response Time
**Definition**: Average time to respond to customer inquiries.

**Target**: <4 hours

**Measurement**: Time from inquiry received to first response.

**Thresholds**:
- 🟢 Green: <2 hours
- 🟡 Yellow: 2-4 hours
- 🔴 Red: >4 hours

---

## Customer Metrics

### Customer Acquisition
**Definition**: Number of new customers acquired during period.

**Target**: 3-5 per week

**Cost per Acquisition (CPA)**: Total marketing spend / new customers

**Target CPA**: <$5,000

---

### Customer Churn
**Definition**: Number of customers lost during period.

**Calculation**: `churn_rate = churned_customers / total_customers`

**Target**: <5% monthly

**Thresholds**:
- 🟢 Green: <3%
- 🟡 Yellow: 3-5%
- 🔴 Red: >5%

---

### Net Customer Growth
**Definition**: New customers minus churned customers.

**Calculation**: `net_growth = new_customers - churned_customers`

**Target**: Positive growth (>0)

---

### Customer Lifetime Value (CLV)
**Definition**: Total revenue expected from a customer over their lifetime.

**Calculation**: `CLV = avg_revenue_per_customer * avg_customer_lifespan`

**Target**: >$50,000

**Ratio**: CLV should be >3x CPA

---

### Customer Satisfaction Score
**Definition**: Average satisfaction rating from customer surveys.

**Scale**: 0-100

**Target**: >90

**Thresholds**:
- 🟢 Green: >90
- 🟡 Yellow: 80-90
- 🔴 Red: <80

---

## Team Metrics

### Team Size
**Definition**: Number of active team members.

**Tracking**: Full-time equivalents (FTE)

**Growth Rate**: Target 10-20% quarterly

---

### Team Utilization
**Definition**: Percentage of available time spent on productive work.

**Calculation**: `utilization = productive_hours / total_available_hours`

**Target**: 80-90%

**Interpretation**:
- >95%: Overworked, risk of burnout
- 80-95%: Healthy utilization
- 70-80%: Acceptable, some slack
- <70%: Underutilized, investigate

---

### Overtime Hours
**Definition**: Hours worked beyond standard schedule.

**Target**: <10% of total hours

**Monitoring**: Track for burnout risk

---

## Activity Metrics

### Emails Sent
**Definition**: Number of emails sent during period.

**Tracking**: From vault items with `type: email`

**Typical Range**: 30-50 per week

---

### LinkedIn Posts
**Definition**: Number of LinkedIn posts published.

**Target**: 5-10 per week

**Engagement**: Track likes, comments, shares

---

### Meetings Held
**Definition**: Number of meetings conducted.

**Target**: 10-15 per week

**Efficiency**: Track meeting duration and outcomes

---

## Trend Metrics

### Week-over-Week (WoW) Change
**Definition**: Percentage change from previous week.

**Calculation**: `wow_change = (current - previous) / previous * 100`

**Interpretation**:
- >10%: Significant change, investigate
- 5-10%: Notable change
- 0-5%: Normal variation
- <0%: Decline, monitor

---

### Month-to-Date (MTD) Performance
**Definition**: Cumulative performance for current month.

**Tracking**: Compare to monthly targets

**Projection**: Estimate month-end based on current pace

---

### Quarter-to-Date (QTD) Performance
**Definition**: Cumulative performance for current quarter.

**Tracking**: Compare to quarterly targets

**Planning**: Adjust Q2 plans based on Q1 performance

---

## Calculated Metrics

### Revenue per Employee
**Calculation**: `revenue / team_size`

**Target**: >$40,000 per month

**Benchmark**: Industry standard varies by sector

---

### Profit per Employee
**Calculation**: `profit / team_size`

**Target**: >$25,000 per month

---

### Customer Acquisition Cost (CAC)
**Calculation**: `marketing_spend / new_customers`

**Target**: <$5,000

**Payback Period**: Target <6 months

---

### Customer Acquisition Cost Ratio
**Calculation**: `CLV / CAC`

**Target**: >3:1

**Interpretation**:
- >5:1: Excellent, scale marketing
- 3-5:1: Healthy, sustainable
- 2-3:1: Acceptable, optimize
- <2:1: Unprofitable, fix immediately

---

## Health Indicators

### Overall Business Health
**Composite Score**: Weighted average of key metrics

**Components**:
- Revenue vs. target (30%)
- Profit margin (20%)
- Customer growth (20%)
- Task completion (15%)
- Cash runway (15%)

**Score**:
- 90-100: 🟢 Excellent
- 75-89: 🟢 Good
- 60-74: 🟡 Fair
- <60: 🔴 Poor

---

## Custom Metrics

### Industry-Specific Metrics
Define custom metrics for your industry:

**SaaS**:
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Churn rate
- Net Revenue Retention (NRR)

**E-commerce**:
- Average Order Value (AOV)
- Conversion rate
- Cart abandonment rate
- Return rate

**Services**:
- Billable hours
- Utilization rate
- Project margin
- Client retention

---

## Metric Collection

### Data Sources
1. **Vault folders**: Primary source for task and project data
2. **Frontmatter metadata**: Financial amounts, dates, priorities
3. **External systems**: Accounting, CRM, analytics tools
4. **Manual entry**: Survey results, qualitative data

### Data Quality
- **Completeness**: All items have required metadata
- **Accuracy**: Amounts and dates are correct
- **Timeliness**: Data is up-to-date
- **Consistency**: Formatting is standardized

### Best Practices
1. **Standardize metadata**: Use consistent field names
2. **Validate inputs**: Check for errors and outliers
3. **Regular audits**: Review data quality monthly
4. **Document changes**: Track metric definition changes
5. **Automate collection**: Reduce manual entry errors

---

## Reporting Frequency

### Daily
- Cash balance
- Critical issues
- High-priority tasks

### Weekly
- Revenue and expenses
- Task completion
- Customer metrics
- Team activity

### Monthly
- Comprehensive financial review
- Customer analysis
- Team performance
- Strategic planning

### Quarterly
- Business review
- Goal assessment
- Strategic adjustments
- Board reporting

---

## Benchmarking

### Internal Benchmarks
Compare current performance to:
- Previous periods
- Historical averages
- Best performance

### External Benchmarks
Compare to:
- Industry averages
- Competitors (if available)
- Best-in-class companies

### Setting Targets
1. **Baseline**: Establish current performance
2. **Aspirational**: Set stretch goals
3. **Realistic**: Balance ambition with achievability
4. **Time-bound**: Define achievement timeline
5. **Review**: Adjust targets quarterly
