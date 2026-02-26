---
name: metric-auditor
description: Perform daily audit of /Done folder to count Emails Sent, LinkedIn Posts Made, and Resolved Tasks. Rewrites Dashboard.md with comprehensive metrics and CEO Summary of recent wins. Use this skill when the user asks to audit metrics, generate daily report, count completed items, review wins, or update dashboard with audit results.
---

# Metric Auditor

This skill audits completed items in /Done folder and generates comprehensive metrics with CEO-friendly summaries.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the Metric Auditor Script

Execute the metric auditor script:

```bash
python scripts/metric_auditor.py [vault_path] [--days N]
```

- If `vault_path` is provided, audit that vault location
- If omitted, audit vault in current working directory
- `--days N` specifies how many days to audit (default: 7)

The script will:
- Scan `/Done` folder for completed items
- Analyze execution summaries and original items
- Count emails sent, LinkedIn posts made, and resolved tasks
- Identify recent wins and notable achievements
- Calculate success rates and performance metrics
- Generate CEO Summary with key highlights
- Rewrite Dashboard.md with updated metrics

### 2. Metrics Collected

The auditor tracks these key metrics:

**Email Metrics:**
- Total emails sent
- Email response rate (if trackable)
- High-priority emails handled
- Average response time
- Client vs. internal emails

**LinkedIn Metrics:**
- Total posts published
- Comments posted
- Messages sent
- Lead engagements
- Engagement rate (if trackable)

**Task Metrics:**
- Total tasks resolved
- Tasks by priority (high/medium/low)
- Tasks by source (Gmail/LinkedIn/other)
- Average completion time
- Success rate

**Performance Metrics:**
- Overall success rate
- Items processed per day
- Average time from capture to completion
- Approval rate
- Execution efficiency

### 3. Audit Process

For each item in /Done, the script:

**Step 1: Identify Item Type**
- Read EXECUTION_SUMMARY.md to determine action type
- Check original item frontmatter for source and type
- Classify as email, LinkedIn post, comment, message, etc.

**Step 2: Extract Metrics**
- Count successful executions
- Note priority level
- Calculate time metrics
- Identify target audience (client, lead, internal)

**Step 3: Identify Wins**
- High-priority items completed successfully
- Client communications handled
- Lead engagements executed
- Complex tasks resolved
- Quick turnaround times

**Step 4: Aggregate Data**
- Sum totals by category
- Calculate averages and rates
- Identify trends
- Compare to previous periods

### 4. CEO Summary Generation

The script generates an executive summary highlighting:

**Recent Wins:**
- "Responded to 3 high-priority client inquiries within 24 hours"
- "Engaged with 5 LinkedIn leads, 3 responded positively"
- "Published 2 thought leadership posts with strong engagement"
- "Maintained 95% success rate on all executions"

**Key Achievements:**
- Milestone completions (e.g., "100th task completed")
- Perfect execution days
- Rapid response times
- High-value client interactions

**Trends:**
- "Email volume up 20% from last week"
- "LinkedIn engagement improving"
- "Average response time decreased to 18 hours"

**Areas of Focus:**
- Items requiring follow-up
- Opportunities identified
- Process improvements

### 5. Dashboard Update Format

The script rewrites Dashboard.md with this structure:

```markdown
# Workflow System Dashboard

**Last Updated**: 2026-02-09 17:00:00
**System Status**: 🟢 Operational
**Audit Period**: Last 7 Days

---

## 🎯 CEO Summary

### Recent Wins (This Week)

✅ **Client Success**: Responded to 8 client inquiries with 100% success rate
✅ **Lead Generation**: Engaged with 12 LinkedIn leads, 7 conversations ongoing
✅ **Thought Leadership**: Published 3 industry insights posts, 450+ views
✅ **Efficiency**: Average response time reduced to 16 hours (target: 24h)

### Key Achievements

- 🏆 Maintained 95% execution success rate
- 🚀 Processed 45 items end-to-end
- ⚡ 15 high-priority items handled within SLA
- 💼 3 new partnership opportunities identified

### This Week's Highlights

**Monday**: Closed partnership discussion with TechVenture (LinkedIn lead)
**Wednesday**: Client project timeline successfully renegotiated
**Friday**: Published viral post on industry trends (200+ engagements)

---

## 📊 Metrics Dashboard

### Execution Summary (Last 7 Days)

| Metric | Count | Success Rate |
|--------|-------|--------------|
| **Emails Sent** | 28 | 96% |
| **LinkedIn Posts** | 5 | 100% |
| **LinkedIn Comments** | 8 | 100% |
| **LinkedIn Messages** | 9 | 89% |
| **Total Tasks Resolved** | 50 | 94% |

### Breakdown by Priority

- 🔴 **High Priority**: 15 items (30%)
- 🟡 **Medium Priority**: 25 items (50%)
- 🟢 **Low Priority**: 10 items (20%)

### Breakdown by Source

- 📧 **Gmail**: 28 items (56%)
- 💼 **LinkedIn**: 22 items (44%)

### Performance Metrics

- **Average Completion Time**: 18.5 hours
- **Fastest Completion**: 2.3 hours (meeting confirmation)
- **Success Rate**: 94%
- **Items Pending**: 3
- **Backlog**: 0

---

## 📈 Trends & Insights

### Week-over-Week Comparison

- Email volume: ↑ 15%
- LinkedIn engagement: ↑ 25%
- Response time: ↓ 20% (improved)
- Success rate: → 94% (stable)

### Top Performers

1. **Client Communications**: 100% success, avg 12h response
2. **LinkedIn Lead Engagement**: 89% response rate
3. **Thought Leadership Posts**: 450+ total views

### Areas for Improvement

- LinkedIn message response rate (89% → target 95%)
- Reduce backlog in Pending_Approval (currently 3 items)

---

## 🎯 Current Status

### Today's Activity
- **New Items**: 5 items received
- **Processed**: 7 items triaged
- **Approved**: 4 items approved
- **Executed**: 6 items completed

### Pipeline Status
- 📥 **Inbox**: 2 items awaiting triage
- 📋 **Needs_Action**: 4 items awaiting planning
- ⏳ **Pending Approval**: 3 items awaiting review
- ✅ **Approved**: 2 items ready for execution

---

## 🏆 Recent Completions (Last 5)

1. **[17:00]** ✅ LinkedIn post published - Industry insights
2. **[16:30]** ✅ Email sent to client - Project update
3. **[15:45]** ✅ LinkedIn comment posted - Lead engagement
4. **[14:20]** ✅ Email sent to partner - Collaboration proposal
5. **[13:10]** ✅ LinkedIn message sent - Follow-up with lead

---

## 📅 This Week's Wins

### Monday, Feb 3
- Responded to urgent client inquiry within 3 hours
- Engaged with 2 high-value LinkedIn leads

### Tuesday, Feb 4
- Published thought leadership post (150+ views)
- Closed partnership discussion initiated via LinkedIn

### Wednesday, Feb 5
- Successfully renegotiated client timeline
- 100% execution success rate (8/8 items)

### Thursday, Feb 6
- Engaged with 4 LinkedIn leads
- Maintained sub-24h response time on all emails

### Friday, Feb 7
- Published viral industry trends post (200+ engagements)
- Completed 12 tasks (personal record)

---

## 🔔 Alerts & Action Items

### Immediate Attention
- [ ] 3 items in Pending_Approval > 24 hours (review needed)
- [ ] Follow up with TechVenture lead (3 days since last contact)

### This Week
- [ ] Review and optimize LinkedIn posting schedule
- [ ] Analyze email response patterns for improvement

---

## 📊 Historical Performance

### Last 30 Days
- Total Items Processed: 180
- Success Rate: 93%
- Average Daily Volume: 6 items
- Peak Day: 15 items (Feb 7)

### All-Time Stats
- Total Items Completed: 450+
- System Uptime: 99.5%
- Client Satisfaction: High
- ROI: Significant time savings

---

*Dashboard updated by metric-auditor skill on 2026-02-09 17:00:00*
```

### 6. Audit Frequency

**Recommended Schedule:**

- **Daily**: Run at end of business day for daily summary
- **Weekly**: Run Monday morning for weekly review
- **Monthly**: Run first of month for monthly report

**Automated Scheduling:**
```bash
# Daily audit at 6 PM
0 18 * * * python scripts/metric_auditor.py

# Weekly audit Monday at 8 AM
0 8 * * 1 python scripts/metric_auditor.py --days 7

# Monthly audit first of month
0 8 1 * * python scripts/metric_auditor.py --days 30
```

### 7. Win Identification Criteria

The script identifies "wins" based on:

**High-Value Items:**
- High-priority items completed successfully
- Client communications handled
- Lead engagements with positive outcomes
- Partnership opportunities

**Performance Excellence:**
- Items completed under target time
- Perfect execution days (100% success)
- Rapid response times
- Complex tasks resolved

**Business Impact:**
- Revenue opportunities identified
- Client relationships strengthened
- Brand visibility increased
- Efficiency improvements

**Engagement Success:**
- LinkedIn posts with high engagement
- Email responses received
- Leads converted to conversations
- Positive feedback received

### 8. Time Period Analysis

The auditor can analyze different time periods:

**Daily (--days 1):**
- Today's completions
- Current day metrics
- Immediate wins

**Weekly (--days 7):**
- Week-over-week trends
- Weekly achievements
- Performance patterns

**Monthly (--days 30):**
- Monthly summary
- Long-term trends
- Strategic insights

**Custom Period:**
```bash
# Last 14 days
python scripts/metric_auditor.py --days 14

# Last 90 days (quarterly)
python scripts/metric_auditor.py --days 90
```

### 9. Data Sources

The auditor extracts data from:

**EXECUTION_SUMMARY.md:**
- Action type (email, post, comment)
- Execution timestamp
- Success/failure status
- Confirmation details
- Tool used

**Original Item Files:**
- Priority level
- Source (Gmail, LinkedIn)
- Target audience
- Subject/context
- Received timestamp

**Plan.md:**
- Objective
- Success criteria
- Risk assessment
- Strategic context

**Folder Structure:**
- Date organized (/Done/YYYY-MM-DD/)
- Item naming conventions
- Completion timestamps

### 10. CEO Summary Best Practices

**Keep it Scannable:**
- Use bullet points and icons
- Highlight key numbers
- Focus on outcomes, not process
- Lead with wins

**Tell the Story:**
- Connect metrics to business impact
- Highlight client successes
- Show progress and trends
- Celebrate achievements

**Be Actionable:**
- Flag items needing attention
- Suggest improvements
- Identify opportunities
- Set clear priorities

**Maintain Context:**
- Compare to targets/goals
- Show week-over-week trends
- Provide historical perspective
- Explain anomalies

## Important Notes

- **Non-destructive**: Only reads /Done folder, doesn't modify completed items
- **Dashboard rewrite**: Completely rewrites Dashboard.md with fresh data
- **Backup recommended**: Consider backing up Dashboard.md before audit
- **Customizable**: Metrics and summary format can be customized
- **Scalable**: Handles large volumes of completed items efficiently

## Integration with Workflow

This skill provides visibility and accountability:

```
Complete Workflow Cycle
         ↓
    /Done folder
         ↓
  Metric Auditor (this skill)
         ↓
  Dashboard.md (updated)
         ↓
  CEO Review & Insights
```

## Error Handling

The script handles:
- **Missing files**: Skips items with incomplete data
- **Malformed data**: Uses defaults for missing fields
- **Empty folders**: Reports zero metrics gracefully
- **Date parsing errors**: Falls back to folder timestamps

## Security & Privacy

**Data Handling:**
- Aggregates metrics without exposing sensitive content
- CEO Summary uses general descriptions, not specific details
- Email addresses and names not included in public metrics
- Maintains confidentiality of client communications

## Example Usage

```bash
# Daily audit (last 24 hours)
python scripts/metric_auditor.py --days 1

# Weekly audit (last 7 days)
python scripts/metric_auditor.py --days 7

# Monthly audit (last 30 days)
python scripts/metric_auditor.py --days 30

# Audit specific vault
python scripts/metric_auditor.py /path/to/vault --days 7

# Audit with verbose output
python scripts/metric_auditor.py --days 7 --verbose
```

## Integration with Other Skills

**Run after:**
- `executor` - After items are completed and moved to /Done

**Run before:**
- CEO review sessions
- Weekly planning meetings
- Monthly business reviews

**Works well with:**
- `update-dashboard` - Complementary dashboard updates
- `approval-monitor` - Complete workflow visibility

## Customization

To customize the auditor:

**Add new metrics:**
Edit `collect_metrics()` function to track additional data points

**Modify CEO Summary:**
Edit `generate_ceo_summary()` function to change format and content

**Change win criteria:**
Edit `identify_wins()` function to adjust what counts as a win

**Customize dashboard format:**
Edit `generate_dashboard()` function to change layout and sections

## Best Practices

1. **Run daily** - Keep metrics current and relevant
2. **Review trends** - Look for patterns and improvements
3. **Celebrate wins** - Acknowledge successes and achievements
4. **Act on insights** - Use data to drive improvements
5. **Share results** - Communicate metrics to stakeholders
6. **Archive reports** - Keep historical dashboards for comparison

The metric auditor transforms raw execution data into strategic business intelligence.
