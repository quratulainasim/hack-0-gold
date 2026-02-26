---
name: social_media_summary
description: Aggregate social media mentions from X/Twitter, Facebook, and Instagram into comprehensive sentiment reports. Use this skill when the user asks to analyze social media sentiment, generate mention reports, track brand sentiment, summarize social media feedback, analyze social engagement, or create sentiment dashboards from social platforms.
license: MIT
---

# Social Media Summary

This skill aggregates mentions from X (Twitter), Facebook, and Instagram and generates sentiment analysis reports.

## Quick Start

Analyze social media mentions:

```bash
python scripts/analyze_sentiment.py <input-directory> --output <report-file>
```

The script processes all social media files in the directory and generates a comprehensive sentiment report.

## Workflow

1. **Collect mentions**: Gather social media files (JSON exports or Markdown from multi_channel_ingest)
2. **Analyze sentiment**: Run sentiment analysis on each mention
3. **Aggregate data**: Group by platform, sentiment, and time period
4. **Generate report**: Create formatted report with insights and visualizations

## Supported Platforms

- **X (Twitter)**: Tweets, mentions, replies, DMs
- **Facebook**: Posts, comments, messages, reactions
- **Instagram**: Posts, comments, DMs, story replies

## Sentiment Classification

The skill classifies mentions into three categories:

- **Positive**: Praise, appreciation, enthusiasm, satisfaction
- **Negative**: Complaints, criticism, frustration, dissatisfaction
- **Neutral**: Questions, informational, factual statements

## Report Structure

Generated reports include:

1. **Executive Summary**: High-level sentiment overview
2. **Platform Breakdown**: Sentiment by platform (X, Facebook, Instagram)
3. **Sentiment Distribution**: Percentage breakdown with counts
4. **Key Themes**: Common topics and patterns
5. **Notable Mentions**: Highlighted positive and negative mentions
6. **Trend Analysis**: Sentiment changes over time
7. **Recommendations**: Actionable insights based on findings

## Usage Examples

**Basic analysis:**
```bash
python scripts/analyze_sentiment.py ./social_mentions --output sentiment_report.md
```

**Specify date range:**
```bash
python scripts/analyze_sentiment.py ./social_mentions --start 2026-02-01 --end 2026-02-19 --output report.md
```

**Platform-specific analysis:**
```bash
python scripts/analyze_sentiment.py ./social_mentions --platform twitter --output twitter_report.md
```

**JSON output for dashboards:**
```bash
python scripts/analyze_sentiment.py ./social_mentions --format json --output sentiment_data.json
```

## Advanced Features

### Keyword Tracking

Track specific keywords or hashtags:
```bash
python scripts/analyze_sentiment.py ./social_mentions --keywords "product,launch,feature" --output keyword_report.md
```

### Influencer Identification

Identify high-engagement accounts:
```bash
python scripts/analyze_sentiment.py ./social_mentions --identify-influencers --output influencer_report.md
```

### Comparative Analysis

Compare sentiment across time periods:
```bash
python scripts/analyze_sentiment.py ./social_mentions --compare-periods weekly --output trend_report.md
```

## Report Templates

For detailed report format examples, see [references/report-templates.md](references/report-templates.md).

## Integration with Other Skills

This skill works well with:
- **multi_channel_ingest**: Standardize social media data before analysis
- **metric-auditor**: Track sentiment metrics over time
- **update-dashboard**: Display sentiment summaries in dashboards

## Sentiment Detection Patterns

The script uses keyword-based and contextual analysis:

**Positive indicators:**
- Keywords: love, great, awesome, excellent, amazing, thank you, perfect
- Emojis: 😊, ❤️, 👍, 🎉, ⭐
- Patterns: "highly recommend", "best ever", "so happy"

**Negative indicators:**
- Keywords: hate, terrible, awful, disappointed, frustrated, broken, worst
- Emojis: 😠, 😡, 👎, 😢
- Patterns: "doesn't work", "waste of money", "never again"

**Neutral indicators:**
- Questions without emotional context
- Factual statements
- Informational requests

## Output Formats

### Markdown Report (default)
Human-readable report with sections, tables, and insights.

### JSON Data
Structured data for integration with dashboards or analytics tools:
```json
{
  "summary": {
    "total_mentions": 150,
    "positive": 85,
    "negative": 20,
    "neutral": 45,
    "sentiment_score": 0.43
  },
  "by_platform": {...},
  "timeline": [...],
  "top_mentions": [...]
}
```

### CSV Export
Tabular data for spreadsheet analysis.

## Best Practices

1. **Regular monitoring**: Run analysis daily or weekly for trend tracking
2. **Respond to negatives**: Prioritize addressing negative sentiment mentions
3. **Amplify positives**: Share and engage with positive mentions
4. **Track keywords**: Monitor product names, campaigns, and brand terms
5. **Compare periods**: Identify sentiment shifts after launches or events
