# LinkedIn Comment & Message Guide

## 1. Comment on a LinkedIn Post

### Command:
```bash
export LINKEDIN_ACCESS_TOKEN="AQU9IuhoR74ioNPX3WmRSZhZtL1fEp2PmQjND_XX6mwfzt6cpqQYaTR8RjarQAk4FDt_Whr9a-_TNaXStIYorrHeq1Tqul4431PNclXq2lS6HWFNXp-hbeMcITQTI_npgtobtvAnmMO66AfbZuxXHUuovnW9ZcrLMApc3r_ZhfddOzU5AxmQpIkuqavGM7w-a3JEuAFDS4Ay8HirRgBPKm90MyAagsNX6vGWOcCG4xqMdBV3J2RbWDZk6LEpoL5QWNl1qOLAI7Khta1oPVFicUQmHDenaQ2kmzibkkYcnkn6x8zTBz0NImyRLCtlzmGZXhmokdq7FAZoMnFpKwsx6pt9yGED7w"

python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.claude/skills/executor')))
from linkedin_api import LinkedInAPI

api = LinkedInAPI('$LINKEDIN_ACCESS_TOKEN')

# Comment on a post
post_urn = 'urn:li:share:7427784673352806400'  # Your post URN
comment_text = 'Great insights! Thanks for sharing this.'

result = api.comment_on_post(post_urn, comment_text)

if result.get('success'):
    print('SUCCESS! Comment posted')
    print(f'Comment ID: {result.get(\"comment_id\")}')
else:
    print(f'ERROR: {result.get(\"error\")}')
"
```

### How to Get Post URN:
1. Go to the LinkedIn post you want to comment on
2. The URL looks like: `https://www.linkedin.com/feed/update/urn:li:share:7427784673352806400/`
3. Copy the URN: `urn:li:share:7427784673352806400`

---

## 2. Send LinkedIn Direct Message

### Command:
```bash
export LINKEDIN_ACCESS_TOKEN="AQU9IuhoR74ioNPX3WmRSZhZtL1fEp2PmQjND_XX6mwfzt6cpqQYaTR8RjarQAk4FDt_Whr9a-_TNaXStIYorrHeq1Tqul4431PNclXq2lS6HWFNXp-hbeMcITQTI_npgtobtvAnmMO66AfbZuxXHUuovnW9ZcrLMApc3r_ZhfddOzU5AxmQpIkuqavGM7w-a3JEuAFDS4Ay8HirRgBPKm90MyAagsNX6vGWOcCG4xqMdBV3J2RbWDZk6LEpoL5QWNl1qOLAI7Khta1oPVFicUQmHDenaQ2kmzibkkYcnkn6x8zTBz0NImyRLCtlzmGZXhmokdq7FAZoMnFpKwsx6pt9yGED7w"

python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.claude/skills/executor')))
from linkedin_api import LinkedInAPI

api = LinkedInAPI('$LINKEDIN_ACCESS_TOKEN')

# Send message
recipient_urn = 'urn:li:person:RECIPIENT_ID'  # Replace with recipient's URN
message_text = 'Hi! I wanted to reach out about our collaboration opportunity.'

result = api.send_message(recipient_urn, message_text)

if result.get('success'):
    print('SUCCESS! Message sent')
    print(f'Message ID: {result.get(\"message_id\")}')
else:
    print(f'ERROR: {result.get(\"error\")}')
"
```

### How to Get Recipient URN:
1. Go to the person's LinkedIn profile
2. The URL looks like: `https://www.linkedin.com/in/username/`
3. You need their person ID (not easily visible in URL)
4. Alternative: Use LinkedIn API to search for connections

---

## Quick Test Commands

### Test Comment on Your Own Post:
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.claude/skills/executor')))
from linkedin_api import LinkedInAPI

api = LinkedInAPI('AQU9IuhoR74ioNPX3WmRSZhZtL1fEp2PmQjND_XX6mwfzt6cpqQYaTR8RjarQAk4FDt_Whr9a-_TNaXStIYorrHeq1Tqul4431PNclXq2lS6HWFNXp-hbeMcITQTI_npgtobtvAnmMO66AfbZuxXHUuovnW9ZcrLMApc3r_ZhfddOzU5AxmQpIkuqavGM7w-a3JEuAFDS4Ay8HirRgBPKm90MyAagsNX6vGWOcCG4xqMdBV3J2RbWDZk6LEpoL5QWNl1qOLAI7Khta1oPVFicUQmHDenaQ2kmzibkkYcnkn6x8zTBz0NImyRLCtlzmGZXhmokdq7FAZoMnFpKwsx6pt9yGED7w')

# Comment on your test post
result = api.comment_on_post(
    'urn:li:share:7427784673352806400',
    'Testing comment functionality - Multi-Agent Workflow System'
)

print('Comment result:', result)
"
```

---

## Notes

- **Post URN**: Easy to get from post URL
- **Person URN**: Harder to get, requires API lookup or profile inspection
- **Messaging**: May require additional LinkedIn API permissions
- **Rate Limits**: LinkedIn has rate limits on API calls

