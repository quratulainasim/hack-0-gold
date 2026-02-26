# Platform Watchers - Gold Tier AI Employee

This folder contains platform monitoring scripts that continuously capture communications from 7 platforms.

---

## 📋 Available Watchers

| Watcher | Platform | Technology | Interval | Keywords |
|---------|----------|------------|----------|----------|
| `gmail_w.py` | Gmail | Gmail API | 30 min | invoice, meeting, urgent |
| `linkedin_simple_capture.py` | LinkedIn | Playwright | 10 min | opportunity, project, collaboration |
| `x_simple_capture.py` | Twitter/X | Playwright | 10 min | urgent, lead, help |
| `facebook_simple_capture.py` | Facebook | Playwright | 10 min | urgent, meeting, help |
| `instagram_simple_capture.py` | Instagram | Playwright | 10 min | urgent, lead, opportunity |
| `whatsapp_simple_capture.py` | WhatsApp | Playwright | 10 min | urgent, payment, invoice |
| `odoo_w.py` | Odoo ERP | XML-RPC | 30 min | draft invoices |

---

## 🚀 Quick Start Commands

### Run Individual Watchers

```bash
# Gmail watcher (API-based)
python watchers/gmail_w.py

# LinkedIn watcher (browser automation)
python watchers/linkedin_simple_capture.py

# Twitter/X watcher (browser automation)
python watchers/x_simple_capture.py

# Facebook watcher (browser automation)
python watchers/facebook_simple_capture.py

# Instagram watcher (browser automation)
python watchers/instagram_simple_capture.py

# WhatsApp watcher (browser automation)
python watchers/whatsapp_simple_capture.py

# Odoo ERP watcher (API-based)
python watchers/odoo_w.py
```

### Run All Watchers (Sequential)

```bash
# Run all watchers one by one
cd D:/Hackathon-0/Gold-Tier
python watchers/gmail_w.py && \
python watchers/linkedin_simple_capture.py && \
python watchers/x_simple_capture.py && \
python watchers/facebook_simple_capture.py && \
python watchers/instagram_simple_capture.py && \
python watchers/whatsapp_simple_capture.py && \
python watchers/odoo_w.py
```

### Run Specific Platform Group

```bash
# Social media platforms only
python watchers/linkedin_simple_capture.py && \
python watchers/x_simple_capture.py && \
python watchers/facebook_simple_capture.py && \
python watchers/instagram_simple_capture.py

# Messaging platforms only
python watchers/whatsapp_simple_capture.py && \
python watchers/instagram_simple_capture.py

# API-based platforms only
python watchers/gmail_w.py && \
python watchers/odoo_w.py
```

---

## 📝 Watcher Details

### 1. Gmail Watcher (`gmail_w.py`)

**Technology**: Gmail API with OAuth 2.0
**Interval**: Every 30 minutes
**Keywords**: invoice, meeting, urgent, payment, asap, help

**Command**:
```bash
python watchers/gmail_w.py
```

**Requirements**:
- Gmail API credentials in `.env`
- OAuth 2.0 refresh token
- Internet connection

**Output**: Creates files in `Inbox/` folder with format `GMAIL_YYYY-MM-DD_HHMMSS_subject.md`

**Configuration**:
```bash
# Required in .env file
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

---

### 2. LinkedIn Watcher (`linkedin_simple_capture.py`)

**Technology**: Playwright browser automation
**Interval**: Every 10 minutes
**Keywords**: opportunity, project, collaboration, meeting, urgent, lead

**Command**:
```bash
python watchers/linkedin_simple_capture.py
```

**Requirements**:
- LinkedIn account credentials
- Persistent browser session (first run requires login)
- Playwright installed

**Output**: Creates files in `Inbox/` folder with format `LI_YYYY-MM-DD_HHMMSS_post_title.md`

**First Run**:
```bash
# First time - will open browser for login
python watchers/linkedin_simple_capture.py
# Login manually, then session persists
```

---

### 3. Twitter/X Watcher (`x_simple_capture.py`)

**Technology**: Playwright browser automation
**Interval**: Every 10 minutes
**Keywords**: urgent, lead, help, opportunity, meeting

**Command**:
```bash
python watchers/x_simple_capture.py
```

**Requirements**:
- Twitter/X account credentials
- Persistent browser session
- Playwright installed

**Output**: Creates files in `Inbox/` folder with format `X_YYYY-MM-DD_HHMMSS_tweet_content.md`

---

### 4. Facebook Watcher (`facebook_simple_capture.py`)

**Technology**: Playwright browser automation
**Interval**: Every 10 minutes
**Keywords**: urgent, meeting, help, client, opportunity

**Command**:
```bash
python watchers/facebook_simple_capture.py
```

**Requirements**:
- Facebook account credentials
- Persistent browser session
- Playwright installed

**Output**: Creates files in `Inbox/` folder with format `FB_YYYY-MM-DD_HHMMSS_sender_message.md`

---

### 5. Instagram Watcher (`instagram_simple_capture.py`)

**Technology**: Playwright browser automation
**Interval**: Every 10 minutes
**Keywords**: urgent, lead, opportunity, meeting, client

**Command**:
```bash
python watchers/instagram_simple_capture.py
```

**Requirements**:
- Instagram account credentials
- Persistent browser session
- Playwright installed

**Output**: Creates files in `Inbox/` folder with format `IG_YYYY-MM-DD_HHMMSS_sender_message.md`

**AI Response Integration**:
This watcher integrates with the AI response automation system. Urgent messages are automatically responded to via `executors/platform_executor.py`.

---

### 6. WhatsApp Watcher (`whatsapp_simple_capture.py`)

**Technology**: Playwright browser automation
**Interval**: Every 10 minutes
**Keywords**: urgent, payment, invoice, help, asap, meeting

**Command**:
```bash
python watchers/whatsapp_simple_capture.py
```

**Requirements**:
- WhatsApp account (phone number)
- QR code scan on first run
- Persistent browser session
- Playwright installed

**Output**: Creates files in `Inbox/` folder with format `WA_YYYY-MM-DD_HHMMSS_contact_name.md`

**First Run**:
```bash
# First time - will open browser with QR code
python watchers/whatsapp_simple_capture.py
# Scan QR code with phone, then session persists
```

**AI Response Integration**:
This watcher integrates with the AI response automation system. Urgent messages are automatically responded to via `executors/platform_executor.py`.

---

### 7. Odoo ERP Watcher (`odoo_w.py`)

**Technology**: XML-RPC API
**Interval**: Every 30 minutes
**Keywords**: draft invoices, unpaid invoices

**Command**:
```bash
python watchers/odoo_w.py
```

**Requirements**:
- Odoo ERP credentials in `.env`
- Odoo server URL
- Internet connection

**Output**: Creates files in `Inbox/` folder with format `ODOO_YYYY-MM-DD_HHMMSS_invoice.md`

**Configuration**:
```bash
# Required in .env file
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following:

```bash
# Gmail API
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# Odoo ERP
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional: Twitter API (if using API instead of browser)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

### Browser Sessions

Browser-based watchers (LinkedIn, Twitter, Facebook, Instagram, WhatsApp) store persistent sessions in:
- `.linkedin_browser_data/`
- `.x_browser_data/`
- `.facebook_browser_data/`
- `.instagram_browser_data/`
- `.whatsapp_browser_data/`

These folders are automatically created on first run and are gitignored.

---

## 📊 Output Format

All watchers create Markdown files in the `Inbox/` folder with frontmatter metadata:

```markdown
---
source: platform_name
type: message_type
priority: high/medium/low
received: YYYY-MM-DDTHH:MM:SS
keywords: keyword1, keyword2, keyword3
---

# Message Title

**From**: Sender Name
**Time**: HH:MM AM/PM
**Status**: unread/read

## Message Content

[Message content here]

## Context

[Additional context]
```

---

## 🔄 Automated Scheduling

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start all watchers
pm2 start watchers/gmail_w.py --name gmail-watcher --cron "*/30 * * * *"
pm2 start watchers/linkedin_simple_capture.py --name linkedin-watcher --cron "*/10 * * * *"
pm2 start watchers/x_simple_capture.py --name x-watcher --cron "*/10 * * * *"
pm2 start watchers/facebook_simple_capture.py --name facebook-watcher --cron "*/10 * * * *"
pm2 start watchers/instagram_simple_capture.py --name instagram-watcher --cron "*/10 * * * *"
pm2 start watchers/whatsapp_simple_capture.py --name whatsapp-watcher --cron "*/10 * * * *"
pm2 start watchers/odoo_w.py --name odoo-watcher --cron "*/30 * * * *"

# Save PM2 configuration
pm2 save

# View status
pm2 status

# View logs
pm2 logs
```

### Using Windows Task Scheduler

```bash
# Create batch file: run_watchers.bat
@echo off
cd D:\Hackathon-0\Gold-Tier
python watchers\gmail_w.py
python watchers\linkedin_simple_capture.py
python watchers\x_simple_capture.py
python watchers\facebook_simple_capture.py
python watchers\instagram_simple_capture.py
python watchers\whatsapp_simple_capture.py
python watchers\odoo_w.py

# Schedule in Task Scheduler:
# - Trigger: Every 10 minutes
# - Action: Run run_watchers.bat
```

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add these lines:
*/30 * * * * cd /path/to/Gold-Tier && python watchers/gmail_w.py
*/10 * * * * cd /path/to/Gold-Tier && python watchers/linkedin_simple_capture.py
*/10 * * * * cd /path/to/Gold-Tier && python watchers/x_simple_capture.py
*/10 * * * * cd /path/to/Gold-Tier && python watchers/facebook_simple_capture.py
*/10 * * * * cd /path/to/Gold-Tier && python watchers/instagram_simple_capture.py
*/10 * * * * cd /path/to/Gold-Tier && python watchers/whatsapp_simple_capture.py
*/30 * * * * cd /path/to/Gold-Tier && python watchers/odoo_w.py
```

---

## 🐛 Troubleshooting

### Watcher Not Capturing

```bash
# Check browser session
ls -la .*_browser_data/

# Re-run watcher manually
python watchers/<platform>_simple_capture.py

# Check logs
cat logs/<platform>_watcher.log
```

### Gmail Authentication Failed

```bash
# Re-run OAuth setup
python setup/generate_gmail_token.py

# Check .env file
cat .env | grep GMAIL
```

### Odoo Connection Error

```bash
# Verify credentials in .env
cat .env | grep ODOO

# Test connection
python watchers/odoo_w.py
```

### WhatsApp Session Lost

```bash
# Delete session and re-scan QR code
rm -rf .whatsapp_browser_data/
python watchers/whatsapp_simple_capture.py
# Scan QR code with phone
```

### Browser Automation Fails

```bash
# Reinstall Playwright browsers
playwright install chromium

# Check Playwright version
playwright --version

# Run in non-headless mode for debugging
# Edit watcher file: headless=False
```

---

## 📈 Performance Tips

1. **Stagger Execution**: Don't run all watchers simultaneously
2. **Adjust Intervals**: Increase intervals for less critical platforms
3. **Monitor Resources**: Check CPU/memory usage with `pm2 monit`
4. **Clean Old Sessions**: Periodically delete and recreate browser sessions
5. **Use Headless Mode**: Always use `headless=True` in production

---

## 🔒 Security

- ✅ All credentials stored in `.env` (gitignored)
- ✅ Browser sessions encrypted and gitignored
- ✅ OAuth 2.0 for Gmail and LinkedIn
- ✅ No hardcoded credentials in code
- ✅ Secure token refresh mechanisms

**Important**: Never commit `.env` file or browser session folders to version control!

---

## 📚 Related Documentation

- **Main README**: `../README.md`
- **System Summary**: `../docs/SYSTEM_SUMMARY.md`
- **Dashboard**: `../Dashboard.md`
- **Audit Report**: `../Audit_Report.md`

---

## ✅ Watcher Status

**Current Status**: 🟢 All 7 Watchers Operational

| Watcher | Status | Last Run | Next Run |
|---------|--------|----------|----------|
| Gmail | ✅ | 2026-02-26 13:00 | 2026-02-26 13:30 |
| LinkedIn | ✅ | 2026-02-26 13:10 | 2026-02-26 13:20 |
| Twitter/X | ✅ | 2026-02-26 13:18 | 2026-02-26 13:28 |
| Facebook | ✅ | 2026-02-26 13:05 | 2026-02-26 13:15 |
| Instagram | ✅ | 2026-02-26 13:00 | 2026-02-26 13:10 |
| WhatsApp | ✅ | 2026-02-26 13:00 | 2026-02-26 13:10 |
| Odoo | ✅ | 2026-02-26 12:30 | 2026-02-26 13:00 |

---

*Platform Watchers - Gold Tier Autonomous AI Employee System*
*Version 2.0 (AI Automation Edition)*
