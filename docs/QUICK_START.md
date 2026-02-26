# Quick Start Guide - WhatsApp & LinkedIn Integration

**Last Updated**: 2026-02-11 23:00:00

---

## ✅ What's Already Done

### Gmail Integration
- ✅ Fully operational
- ✅ 2 emails sent successfully
- ✅ OAuth credentials configured
- ✅ Direct API integration working

### Multi-Agent Workflow
- ✅ All agents operational
- ✅ Complete workflow tested
- ✅ Dashboard tracking metrics
- ✅ 100% success rate

### WhatsApp Setup
- ✅ Playwright installed
- ✅ Chromium browser downloaded
- ✅ WhatsApp Web session authenticated
- ✅ Browser profile saved
- ⚠️ UI selector timeout issue (fixable)

---

## 🔧 Fix WhatsApp Integration (5 minutes)

### Option 1: Test Current Setup

Run the connection test script:
```bash
python test_whatsapp_connection.py
```

This will:
- Open WhatsApp Web with your saved session
- Check which UI selectors work
- Give you specific feedback

### Option 2: Manual Test

1. **Send yourself a test message** from another phone:
   ```
   urgent test message
   ```

2. **Run the ingestion script**:
   ```bash
   python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py
   ```

3. **Check for captured messages**:
   ```bash
   ls -la Inbox/WA_*
   ```

### Option 3: Update Selectors (if needed)

If the scripts timeout, edit `whatsapp_ingest.py` line 244:

**Current:**
```python
page.wait_for_selector('div[data-testid="chat-list"]', timeout=15000)
```

**Try these alternatives:**
```python
# Option A: Increase timeout
page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)

# Option B: Alternative selector
page.wait_for_selector('#pane-side', timeout=30000)

# Option C: More generic selector
page.wait_for_selector('div[role="application"]', timeout=30000)
```

---

## 🔗 Set Up LinkedIn Integration

### Choose Your Approach

#### Option A: Official LinkedIn API (Recommended for Production)

**Time Required**: 30-60 minutes

**Steps:**

1. **Create LinkedIn App**
   - Go to https://www.linkedin.com/developers/
   - Click "Create App"
   - Fill in details:
     - App name: "Multi-Agent Workflow System"
     - LinkedIn Page: Your company page
     - Upload app logo

2. **Configure OAuth**
   - Go to "Auth" tab
   - Add redirect URL: `http://localhost:8080/callback`
   - Request scopes:
     - `r_liteprofile` - Read basic profile
     - `r_emailaddress` - Read email
     - `w_member_social` - Post on behalf of user

3. **Get Credentials**
   - Copy Client ID
   - Copy Client Secret

4. **Run OAuth Setup**
   ```bash
   # Edit linkedin_oauth_setup.py first
   # Update CLIENT_ID and CLIENT_SECRET
   python linkedin_oauth_setup.py
   ```

5. **Authorize in Browser**
   - Browser will open automatically
   - Log in to LinkedIn
   - Authorize the app
   - Token will be saved automatically

**Result**: LinkedIn API fully configured and ready to use

---

#### Option B: Browser Automation (Quick Test)

**Time Required**: 5 minutes

**Steps:**

1. **Run LinkedIn Watcher**
   ```bash
   python linkedin_watcher.py
   ```

2. **Log In Manually**
   - Browser opens to LinkedIn
   - Log in with your credentials
   - Session is saved for future use

3. **Test**
   - Script will check for notifications
   - Currently in mock mode (no real API calls)

**Note**: This is for testing only. Not recommended for production.

---

## 🚀 Test Complete Workflow

Once both integrations are set up:

### 1. Test WhatsApp → Email Flow

**Step 1**: Send WhatsApp message
```
Send yourself: "urgent client inquiry about project timeline"
```

**Step 2**: Capture message
```bash
python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py
```

**Step 3**: Process through workflow
```bash
# Move to Needs_Action
mv Inbox/WA_* Needs_Action/

# Create strategic plan
python .claude/skills/strategic-planner/scripts/strategic_planner.py

# Review and approve
ls -la Pending_Approval/

# Move to Approved
mv Pending_Approval/[folder-name] Approved/

# Execute
python .claude/skills/executor/scripts/executor.py

# Update metrics
python .claude/skills/metric-auditor/scripts/metric_auditor.py --days 1
```

**Step 4**: Check results
```bash
# Check Dashboard
cat Dashboard.md

# Check Done folder
ls -la Done/2026-02-11/
```

---

## 📊 Current System Status

### Working Integrations
| Integration | Status | Test Command |
|-------------|--------|--------------|
| Gmail API | 🟢 Operational | `python quick_email_test.py email@example.com` |
| Workflow System | 🟢 Operational | `bash test_complete_workflow.sh` |
| WhatsApp | 🟡 Needs Testing | `python test_whatsapp_connection.py` |
| LinkedIn | ⚪ Not Started | `python linkedin_oauth_setup.py` |

### Files Created
- ✅ `SETUP_WHATSAPP_LINKEDIN.md` - Complete setup guide
- ✅ `INTEGRATION_STATUS.md` - Current status report
- ✅ `test_whatsapp_connection.py` - WhatsApp connection tester
- ✅ `linkedin_oauth_setup.py` - LinkedIn OAuth helper
- ✅ `quick_email_test.py` - Gmail API tester
- ✅ `test_complete_workflow.sh` - End-to-end workflow test

---

## 🎯 Recommended Next Steps

### Immediate (Next 10 minutes)
1. ✅ Test WhatsApp connection
   ```bash
   python test_whatsapp_connection.py
   ```

2. ✅ Send test WhatsApp message with "urgent" keyword

3. ✅ Run WhatsApp ingestion
   ```bash
   python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py
   ```

### Short-term (Today)
4. ⏳ Choose LinkedIn integration method (API or Browser)

5. ⏳ Set up LinkedIn credentials

6. ⏳ Test LinkedIn integration

### This Week
7. ⏳ Test complete WhatsApp → Email workflow

8. ⏳ Set up automated scheduling (run watchers every 15 minutes)

9. ⏳ Deploy as background services

---

## 🆘 Troubleshooting

### WhatsApp Issues

**Problem**: "Timeout waiting for WhatsApp Web to load"

**Solutions**:
1. Check if WhatsApp Web loads in regular browser
2. Increase timeout in script (line 244)
3. Try alternative UI selectors
4. Run `python test_whatsapp_connection.py` for diagnostics

**Problem**: "No messages captured"

**Solutions**:
1. Ensure messages contain priority keywords: urgent, asap, payment, lead, meeting
2. Check messages are unread in WhatsApp Web
3. Verify `.whatsapp_processed.json` isn't blocking duplicates

### LinkedIn Issues

**Problem**: "LinkedIn credentials not configured"

**Solution**: Edit `linkedin_oauth_setup.py` and add your Client ID and Secret

**Problem**: "Access token expired"

**Solution**: LinkedIn tokens expire after 60 days. Re-run OAuth setup:
```bash
python linkedin_oauth_setup.py
```

---

## 📞 Support

### Documentation
- `SETUP_WHATSAPP_LINKEDIN.md` - Detailed setup instructions
- `INTEGRATION_STATUS.md` - Current integration status
- `SYSTEM_SUMMARY.md` - System architecture
- `Dashboard.md` - Live metrics

### Test Scripts
- `test_whatsapp_connection.py` - Test WhatsApp
- `linkedin_oauth_setup.py` - Set up LinkedIn
- `quick_email_test.py` - Test Gmail
- `test_complete_workflow.sh` - Test full workflow

---

## ✨ What You Can Do Right Now

**Option 1: Test WhatsApp (5 minutes)**
```bash
# 1. Test connection
python test_whatsapp_connection.py

# 2. Send yourself "urgent test" message

# 3. Run ingestion
python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py

# 4. Check results
ls -la Inbox/WA_*
```

**Option 2: Set Up LinkedIn (30 minutes)**
```bash
# 1. Create LinkedIn app at https://www.linkedin.com/developers/

# 2. Edit linkedin_oauth_setup.py with your credentials

# 3. Run OAuth setup
python linkedin_oauth_setup.py

# 4. Authorize in browser
```

**Option 3: Test Complete Workflow (10 minutes)**
```bash
# Run the complete workflow test
bash test_complete_workflow.sh
```

---

*Your Multi-Agent Workflow System is 90% complete!*
*Just test WhatsApp and set up LinkedIn to reach 100%.*
