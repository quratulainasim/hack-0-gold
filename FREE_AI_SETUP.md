# 🚀 FREE AI Setup Guide
## Google Gemini API (Completely Free!)

---

## Step 1: Get FREE Gemini API Key

### Go to Google AI Studio
1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key (starts with `AIza...`)

**✅ This is 100% FREE for demos and development!**

---

## Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## Step 3: Configure API Key

### Option A: Edit .env file directly
```bash
# Copy the example file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor

# Add your Gemini API key:
GEMINI_API_KEY=AIza...your_key_here
```

### Option B: Quick command
```bash
# Replace YOUR_KEY with your actual key
echo "GEMINI_API_KEY=YOUR_KEY_HERE" >> .env
```

---

## Step 4: Test AI Generation

```bash
# Test if Gemini is working
python -c "import google.generativeai as genai; print('✅ Gemini ready!')"
```

---

## 🎯 Complete Autonomous Workflow

### Full Demo (All Steps)

```bash
# 1. Capture communications from all 7 platforms
bash run_demo.sh

# 2. Generate AI responses (FREE with Gemini!)
python .claude/skills/ai-content-generator/scripts/generate_content_free.py

# 3. Review generated content
ls -la Pending_Approval/

# 4. Approve items (manually move to Approved/)
# Move files you approve from Pending_Approval/ to Approved/

# 5. Execute approved items
python executors/master_orchestrator.py --process-all

# 6. View results
cat Dashboard.md
```

---

## 📊 Quick Commands

### Capture Only
```bash
# Run all watchers
bash run_demo.sh
```

### AI Generation Only
```bash
# Generate responses for items in Needs_Action
python .claude/skills/ai-content-generator/scripts/generate_content_free.py
```

### Execute Only
```bash
# Execute approved items
python executors/master_orchestrator.py --process-all
```

### Continuous Monitoring
```bash
# Monitor and auto-execute approved items
python executors/master_orchestrator.py --monitor
```

---

## 🎬 Demo for Teacher

### Quick Demo (5 minutes)
```bash
# 1. Show platform watchers
bash run_demo.sh

# 2. Show captured data
ls -la Inbox/
ls -la Needs_Action/

# 3. Show AI generation
python .claude/skills/ai-content-generator/scripts/generate_content_free.py

# 4. Show generated responses
ls -la Pending_Approval/
cat Pending_Approval/*.md | head -50

# 5. Show dashboard
cat Dashboard.md
```

### Full Demo (15 minutes)
```bash
# 1. Capture communications
bash run_demo.sh

# 2. Generate AI responses
python .claude/skills/ai-content-generator/scripts/generate_content_free.py

# 3. Show approval workflow
echo "Review files in Pending_Approval/"
ls -la Pending_Approval/

# 4. Approve one item (example)
mv Pending_Approval/LINKEDIN_*.md Approved/

# 5. Execute approved item
python executors/master_orchestrator.py --process-all

# 6. Show completion
ls -la Done/
cat Dashboard.md
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'google.generativeai'"
**Solution:**
```bash
pip install google-generativeai
```

### Issue: "GEMINI_API_KEY not found"
**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Add API key to .env
echo "GEMINI_API_KEY=YOUR_KEY_HERE" >> .env
```

### Issue: "API key invalid"
**Solution:**
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Update .env file with new key

### Issue: "Rate limit exceeded"
**Solution:**
- Gemini free tier: 60 requests per minute
- Wait 1 minute and try again
- For demo, this is more than enough!

---

## 📈 What You Get (FREE!)

### ✅ Included Features
- **7 Platform Monitoring**: Gmail, LinkedIn, Twitter, Facebook, Instagram, WhatsApp, Odoo
- **AI Content Generation**: Powered by Google Gemini (FREE!)
- **Autonomous Workflow**: Inbox → Needs_Action → Pending_Approval → Approved → Done
- **Executive Reports**: CEO briefings, daily audits, financial reports
- **Platform Execution**: Automated posting via Playwright
- **Error Recovery**: Retry logic with screenshots

### 💰 Cost Breakdown
- **Gemini API**: FREE (60 requests/min)
- **Playwright**: FREE (open source)
- **Python Libraries**: FREE (open source)
- **Total Cost**: $0.00 🎉

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GOLD TIER SYSTEM                      │
│              (100% FREE with Gemini API)                │
└─────────────────────────────────────────────────────────┘

1. CAPTURE (Watchers)
   ├── Gmail API
   ├── LinkedIn (Playwright)
   ├── Twitter/X (Playwright)
   ├── Facebook (Playwright)
   ├── Instagram (Playwright)
   ├── WhatsApp (Playwright)
   └── Odoo ERP (XML-RPC)
          ↓
2. AI GENERATION (Gemini - FREE!)
   └── Generate platform-specific responses
          ↓
3. HUMAN APPROVAL
   └── Review in Pending_Approval/
          ↓
4. EXECUTION (Master Orchestrator)
   └── Post to platforms via Playwright
          ↓
5. REPORTING
   └── Dashboard, CEO Report, Audit Report
```

---

## 📝 Example Workflow

### Scenario: LinkedIn Post Response

```bash
# 1. LinkedIn watcher captures a post
# Creates: Needs_Action/LI_2026-02-24_post.md

# 2. AI generates response
python .claude/skills/ai-content-generator/scripts/generate_content_free.py
# Creates: Pending_Approval/LINKEDIN_2026-02-24_generated.md

# 3. You review and approve
cat Pending_Approval/LINKEDIN_2026-02-24_generated.md
mv Pending_Approval/LINKEDIN_2026-02-24_generated.md Approved/

# 4. System executes
python executors/master_orchestrator.py --process-all
# Posts to LinkedIn automatically!

# 5. Check completion
ls -la Done/
# File moved to Done/2026-02-24/LINKEDIN_2026-02-24_generated.md
```

---

## 🎓 For Your Teacher

### Key Points to Highlight

1. **7-Platform Integration**
   - "The system monitors 7 different platforms simultaneously"
   - Show: `bash run_demo.sh`

2. **FREE AI Generation**
   - "Uses Google Gemini API which is completely free"
   - Show: `python .claude/skills/ai-content-generator/scripts/generate_content_free.py`

3. **Autonomous Workflow**
   - "Captures → AI generates → Human approves → System executes"
   - Show: Folder structure (Inbox → Needs_Action → Pending_Approval → Approved → Done)

4. **Executive Reporting**
   - "Generates CEO briefings and financial reports automatically"
   - Show: `cat Dashboard.md` and `cat CEO_Morning_Report.md`

5. **Production Ready**
   - "Complete with error handling, retry logic, and logging"
   - Show: `logs/` folder and screenshot capability

---

## 🚀 Next Steps

### After Demo
1. Push to GitHub (make sure .env is gitignored!)
2. Add README badges
3. Create demo video
4. Document API setup process

### For Production
1. Set up PM2 for continuous monitoring
2. Configure scheduled runs (cron)
3. Add more platforms
4. Implement advanced analytics

---

## 📞 Support

### Getting Help
- Check logs: `cat logs/content-generator.log`
- Check errors: `cat logs/orchestrator.log`
- View screenshots: `ls logs/screenshots/`

### Common Questions

**Q: Is Gemini really free?**
A: Yes! 60 requests per minute, perfect for demos.

**Q: Can I use this in production?**
A: Yes, but consider rate limits for high volume.

**Q: Do I need to pay for anything?**
A: No! Everything is free and open source.

---

**🎉 You're Ready! Run `bash run_demo.sh` to start!**
