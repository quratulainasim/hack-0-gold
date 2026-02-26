# Report Templates

This reference shows example report outputs for different scenarios.

## Standard Sentiment Report

```markdown
# Social Media Sentiment Report

**Generated**: 2026-02-19 14:30:00

## Executive Summary

Total mentions analyzed: **247**

Sentiment Score: **0.42** (Range: -1.0 to 1.0)

### Overall Sentiment Distribution

- 😊 Positive: **145** (58.7%)
- 😐 Neutral: **67** (27.1%)
- 😠 Negative: **35** (14.2%)

## Platform Breakdown

### X (Twitter)

Total: 120 mentions
- Positive: 68 (56.7%)
- Neutral: 35 (29.2%)
- Negative: 17 (14.2%)

### Facebook

Total: 82 mentions
- Positive: 52 (63.4%)
- Neutral: 20 (24.4%)
- Negative: 10 (12.2%)

### Instagram

Total: 45 mentions
- Positive: 25 (55.6%)
- Neutral: 12 (26.7%)
- Negative: 8 (17.8%)

## Key Themes

- **product**: 89 mentions
- **launch**: 67 mentions
- **feature**: 54 mentions
- **update**: 42 mentions
- **support**: 38 mentions
- **design**: 31 mentions
- **quality**: 28 mentions
- **price**: 24 mentions
- **service**: 22 mentions
- **experience**: 19 mentions

## Notable Positive Mentions

1. **Sarah Johnson** (Twitter)
   > Just tried the new product and I'm absolutely blown away! The design is incredible and it works flawlessly. Highly recommend to everyone! 🎉

2. **Mike Chen** (Facebook)
   > Best purchase I've made this year. The customer support team was amazing and helped me set everything up. Five stars! ⭐⭐⭐⭐⭐

3. **designstudio** (Instagram)
   > Love the attention to detail in this product. You can tell the team really cares about quality. Can't wait to see what's next! 💯

## Notable Negative Mentions

1. **TechReviewer99** (Twitter)
   > Disappointed with the latest update. Several features are broken and support hasn't responded to my ticket in 3 days. Not acceptable.

2. **Jane Smith** (Facebook)
   > The product doesn't work as advertised. I've tried everything and it still crashes. Waste of money. Very frustrated.

3. **user_12345** (Instagram)
   > Poor quality for the price. Expected much better based on the marketing. Would not recommend.

## Recommendations

- ✅ Overall sentiment is positive. Continue current engagement strategies.
- 🔍 Address 35 negative mentions promptly.
- 📢 Amplify positive mentions through sharing and engagement.
```

## Crisis Alert Report (Negative Sentiment)

```markdown
# Social Media Sentiment Report - ALERT

**Generated**: 2026-02-19 14:30:00

⚠️ **ATTENTION REQUIRED**: Negative sentiment detected

## Executive Summary

Total mentions analyzed: **156**

Sentiment Score: **-0.38** (Range: -1.0 to 1.0)

### Overall Sentiment Distribution

- 😊 Positive: **32** (20.5%)
- 😐 Neutral: **45** (28.8%)
- 😠 Negative: **79** (50.6%)

## Platform Breakdown

### X (Twitter)

Total: 95 mentions
- Positive: 15 (15.8%)
- Neutral: 25 (26.3%)
- Negative: 55 (57.9%)

### Facebook

Total: 41 mentions
- Positive: 10 (24.4%)
- Neutral: 12 (29.3%)
- Negative: 19 (46.3%)

### Instagram

Total: 20 mentions
- Positive: 7 (35.0%)
- Neutral: 8 (40.0%)
- Negative: 5 (25.0%)

## Key Themes

- **broken**: 45 mentions
- **issue**: 38 mentions
- **problem**: 34 mentions
- **support**: 31 mentions
- **bug**: 28 mentions
- **crash**: 22 mentions
- **refund**: 18 mentions
- **disappointed**: 16 mentions
- **terrible**: 14 mentions
- **worst**: 12 mentions

## Notable Negative Mentions

1. **AngryCustomer** (Twitter)
   > This is the worst product I've ever bought. It's completely broken and customer support is ignoring me. Absolutely unacceptable! 😡

2. **FrustratedUser** (Facebook)
   > Three weeks and still no response from support. The product crashes every time I try to use it. This is ridiculous. I want a refund!

3. **tech_reviewer** (Instagram)
   > Major quality issues. Multiple bugs, poor performance, and zero communication from the company. Stay away from this product.

## Recommendations

- ⚠️ Overall sentiment is negative. Immediate attention required.
- 🚨 URGENT: Address 79 negative mentions promptly.
- 📞 Prioritize customer support response times.
- 🔧 Investigate reported technical issues immediately.
- 💬 Issue public statement acknowledging concerns.
- 📊 Schedule daily sentiment monitoring until resolved.
```

## Platform-Specific Report (Twitter Only)

```markdown
# X (Twitter) Sentiment Report

**Generated**: 2026-02-19 14:30:00

## Executive Summary

Total mentions analyzed: **120**

Sentiment Score: **0.35** (Range: -1.0 to 1.0)

### Sentiment Distribution

- 😊 Positive: **68** (56.7%)
- 😐 Neutral: **35** (29.2%)
- 😠 Negative: **17** (14.2%)

## Engagement Metrics

- Total reach: ~45,000 followers
- High-engagement accounts: 12
- Retweets: 234
- Likes: 1,567

## Top Influencers

1. **@TechInfluencer** (125K followers) - Positive mention
2. **@IndustryExpert** (89K followers) - Positive mention
3. **@ProductReviewer** (67K followers) - Neutral mention

## Key Themes

- **launch**: 34 mentions
- **feature**: 28 mentions
- **update**: 22 mentions
- **design**: 18 mentions
- **performance**: 15 mentions

## Notable Mentions

### Positive
1. **@TechInfluencer**
   > Just tested the new product and wow! This is a game-changer. The team nailed it. 🚀

### Negative
1. **@CriticalUser**
   > Not impressed with the latest update. Several bugs and performance issues. Hope they fix this soon.

## Recommendations

- ✅ Overall Twitter sentiment is positive.
- 🎯 Engage with high-influence positive mentions.
- 🔄 Retweet and amplify positive feedback.
- 📞 Respond to negative mentions within 24 hours.
```

## JSON Output Example

```json
{
  "generated": "2026-02-19T14:30:00Z",
  "summary": {
    "total_mentions": 247,
    "positive": 145,
    "negative": 35,
    "neutral": 67,
    "sentiment_score": 0.42,
    "by_platform": {
      "twitter": {
        "total": 120,
        "positive": 68,
        "negative": 17,
        "neutral": 35
      },
      "facebook": {
        "total": 82,
        "positive": 52,
        "negative": 10,
        "neutral": 20
      },
      "instagram": {
        "total": 45,
        "positive": 25,
        "negative": 8,
        "neutral": 12
      }
    }
  },
  "themes": [
    {"word": "product", "count": 89},
    {"word": "launch", "count": 67},
    {"word": "feature", "count": 54}
  ],
  "top_positive": [
    {
      "sender": "Sarah Johnson",
      "platform": "twitter",
      "content": "Just tried the new product and I'm absolutely blown away!",
      "confidence": 0.92
    }
  ],
  "top_negative": [
    {
      "sender": "TechReviewer99",
      "platform": "twitter",
      "content": "Disappointed with the latest update. Several features are broken.",
      "confidence": 0.87
    }
  ]
}
```

## CSV Output Example

```csv
Platform,Sender,Sentiment,Confidence,Content,Received
twitter,Sarah Johnson,positive,0.92,"Just tried the new product and I'm absolutely blown away! The design is incredible and it works flawlessly.",2026-02-19T10:30:00Z
facebook,Mike Chen,positive,0.88,"Best purchase I've made this year. The customer support team was amazing.",2026-02-19T11:15:00Z
instagram,designstudio,positive,0.85,"Love the attention to detail in this product. You can tell the team really cares about quality.",2026-02-19T12:00:00Z
twitter,TechReviewer99,negative,0.87,"Disappointed with the latest update. Several features are broken and support hasn't responded.",2026-02-19T13:20:00Z
facebook,Jane Smith,negative,0.91,"The product doesn't work as advertised. I've tried everything and it still crashes.",2026-02-19T14:05:00Z
```
