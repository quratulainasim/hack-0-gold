# WhatsApp Ingest

This skill monitors WhatsApp Web for priority messages containing urgent keywords and creates structured markdown files in /Inbox for processing by the workflow system.

## Workflow

When this skill is invoked, follow these steps:

### 1. Run the WhatsApp Ingest Script

Execute the WhatsApp ingestion script:

```bash
python scripts/whatsapp_ingest.py [vault_path]
```

- If `vault_path` is provided, process that vault location
- If omitted, process vault in current working directory

The script will:
- Launch Playwright browser with persistent session
- Navigate to WhatsApp Web (web.whatsapp.com)
- Scan unread messages for priority keywords
- Extract messages containing: 'urgent', 'asap', 'invoice', 'payment', 'help'
- Create structured markdown files in /Inbox
- Track processed messages to avoid duplicates

### 2. Priority Keywords

The skill searches for these high-priority keywords:

- **urgent** - Immediate attention required
- **asap** - As soon as possible requests
- **invoice** - Billing and invoice matters
- **payment** - Payment-related communications
- **help** - Assistance requests

Messages containing any of these keywords are automatically flagged as high priority.

### 3. Session Management

The script uses Playwright's persistent browser context:

**Session Path**:
- Default: `[vault]/.whatsapp_session/`
- Environment variable: `WHATSAPP_SESSION_PATH`

**Benefits**:
- No need to scan QR code every time
- Session persists across script runs
- Faster startup after initial setup

**First-Time Setup**:
1. Script launches browser (non-headless)
2. WhatsApp Web displays QR code
3. Scan QR code with your phone
4. Session is saved for future use
5. Subsequent runs use saved session

### 4. Message Extraction Process

For each unread chat, the script:

**Step 1: Identify Unread Chats**
- Scans chat list for unread message indicators
- Prioritizes most recent conversations
- Limits to 20 most recent chats for efficiency

**Step 2: Open and Scan Chat**
- Clicks on chat to open conversation
- Extracts sender name and chat type (individual/group)
- Retrieves recent unread messages

**Step 3: Keyword Matching**
- Checks each message for priority keywords
- Case-insensitive matching
- Identifies all matched keywords

**Step 4: Create Inbox File**
- Generates unique message ID
- Checks if already processed (deduplication)
- Creates structured markdown file in /Inbox
- Marks message as processed

### 5. Inbox File Format

Each captured message creates a file with this structure:

```markdown
---
type: whatsapp
priority: high
status: pending
timestamp: 2026-02-10T15:30:00
source: whatsapp
sender: John Smith
keywords: urgent, payment
chat_type: individual
---

# WhatsApp Priority Message from John Smith

**Received**: 2026-02-10T15:30:00
**Priority**: HIGH
**Keywords Matched**: urgent, payment
**Chat Type**: Individual

---

## Message Content

[Full message text extracted from WhatsApp]

---

## Context

This message was flagged as high priority because it contains urgent keywords: **urgent, payment**

**Sender**: John Smith
**Source**: WhatsApp Web
**Captured**: 2026-02-10 15:30:45

---

## Recommended Actions

- [ ] Review payment/invoice details
- [ ] Verify transaction information
- [ ] Process payment or send invoice
- [ ] Confirm with sender

---

*Captured by whatsapp-ingest skill on 2026-02-10 15:30:45*
```

### 6. Deduplication

The script prevents duplicate processing:

**Tracking File**: `.whatsapp_processed.json`
- Stores message IDs of processed messages
- Persists across script runs
- Prevents re-processing same message

**Message ID Format**:
```
{sender}_{message_preview}_{message_length}
```

### 7. Keyword-Specific Actions

The script generates context-aware action items:

**Payment/Invoice Keywords**:
- Review payment/invoice details
- Verify transaction information
- Process payment or send invoice
- Confirm with sender

**Urgent/ASAP Keywords**:
- Assess urgency level
- Respond immediately
- Take necessary action
- Follow up to confirm resolution

**Help Keywords**:
- Understand the help request
- Provide assistance or guidance
- Escalate if necessary
- Confirm issue resolved

### 8. Integration with Workflow

This skill is the first step in the WhatsApp workflow:

```
1. WhatsApp Ingest (this skill) → /Inbox
2. Strategic Planner → /Needs_Action → /Pending_Approval
3. Human Approval → /Approved
4. Executor → /Done
```

## Requirements

### Python Dependencies

```bash
pip install playwright
playwright install chromium
```

### System Requirements

- Python 3.8+
- Chromium browser (installed via Playwright)
- Active WhatsApp account
- Internet connection

### WhatsApp Setup

1. Have WhatsApp installed on your phone
2. Phone must be connected to internet
3. Ability to scan QR code for WhatsApp Web

## Configuration

### Session Path

Set custom session path via environment variable:

```bash
export WHATSAPP_SESSION_PATH="/secure/path/session"
python scripts/whatsapp_ingest.py
```

Or use default: `[vault]/.whatsapp_session/`

### Headless Mode

For background/daemon operation, edit script:

```python
# Change this line in whatsapp_ingest.py
headless=False,  # Set to True for background operation
```

### Priority Keywords

To customize keywords, edit the script:

```python
# Modify this list in whatsapp_ingest.py
PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help']
```

## Usage Examples

### Basic Usage

```bash
# Run in current vault
python scripts/whatsapp_ingest.py

# Run in specific vault
python scripts/whatsapp_ingest.py /path/to/vault
```

### Scheduled Execution

Run periodically to capture messages:

```bash
# Every 5 minutes during business hours (9 AM - 6 PM)
*/5 9-18 * * * cd /path/to/vault && python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py

# Every 15 minutes (less frequent)
*/15 * * * * cd /path/to/vault && python .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py
```

### With Custom Session Path

```bash
export WHATSAPP_SESSION_PATH="/secure/whatsapp/session"
python scripts/whatsapp_ingest.py
```

## Error Handling

The script handles common errors:

**Browser Connection Issues**:
- Retries connection
- Logs error details
- Continues operation

**WhatsApp Web Not Loaded**:
- Timeout after 15 seconds
- Prompts to check login status
- Preserves session for retry

**Message Extraction Errors**:
- Skips problematic messages
- Logs warnings
- Continues processing other messages

**File Creation Errors**:
- Logs error details
- Increments error counter
- Continues with next message

## Security Considerations

### Session Security

- Session data stored locally
- Contains WhatsApp Web authentication
- Protect session directory with appropriate permissions

```bash
chmod 700 .whatsapp_session/
```

### Message Privacy

- Messages stored in plain text in /Inbox
- Ensure vault directory has proper access controls
- Consider encryption for sensitive vaults

### Browser Automation

- Uses Playwright (legitimate automation tool)
- Respects WhatsApp's terms of service
- No API abuse or rate limit violations

## Performance

### Efficiency Optimizations

- Limits to 20 most recent unread chats
- Processes only unread messages
- Deduplication prevents reprocessing
- Persistent session eliminates QR scanning

### Resource Usage

- Browser runs in foreground (default) or headless mode
- Memory: ~200-300 MB (Chromium browser)
- CPU: Low (only during active scanning)
- Network: Minimal (only WhatsApp Web traffic)

## Troubleshooting

### Issue: QR Code Appears Every Time

**Solution**: Ensure session path is writable and persistent
```bash
ls -la .whatsapp_session/
# Should contain browser profile data
```

### Issue: No Messages Captured

**Possible Causes**:
1. No unread messages containing keywords
2. Already processed (check `.whatsapp_processed.json`)
3. WhatsApp Web not fully loaded

**Solution**:
- Check for unread messages in WhatsApp
- Delete `.whatsapp_processed.json` to reprocess
- Increase timeout in script

### Issue: Browser Doesn't Launch

**Solution**: Reinstall Playwright browsers
```bash
playwright install chromium
```

### Issue: "Not Logged In" Error

**Solution**:
1. Delete session directory
2. Run script again
3. Scan QR code when prompted

## Integration with Other Skills

**Run after:**
- WhatsApp messages arrive (triggered by watcher or schedule)

**Run before:**
- `strategic-planner` - Creates plans for captured messages

**Works well with:**
- `gmail-ingest` - Parallel message capture from multiple sources
- `linkedin-ingest` - Complete communication monitoring

## Best Practices

1. **Regular Execution**: Run every 5-15 minutes during business hours
2. **Monitor Logs**: Check for errors and adjust as needed
3. **Secure Session**: Protect session directory with proper permissions
4. **Test Keywords**: Verify keywords match your business needs
5. **Backup Session**: Keep backup of session directory
6. **Review Captures**: Periodically check /Inbox for accuracy

## Daemon Mode

For continuous background operation:

1. Set `headless=True` in script
2. Use process manager (systemd, supervisor, pm2)
3. Redirect output to log file
4. Monitor process health

Example systemd service:

```ini
[Unit]
Description=WhatsApp Ingest Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/vault
Environment="WHATSAPP_SESSION_PATH=/secure/path/session"
ExecStart=/usr/bin/python3 .claude/skills/whatsapp-ingest/scripts/whatsapp_ingest.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

## Limitations

- Requires active WhatsApp Web session
- Phone must be online and connected
- Cannot access archived chats
- Limited to text messages (no media extraction)
- Processes only unread messages

## Future Enhancements

Potential improvements:
- Media file extraction (images, documents)
- Group message filtering
- Sender whitelist/blacklist
- Custom keyword rules per sender
- Message threading and context
- Automated responses for common queries

This skill provides the critical "sensory organ" for urgent WhatsApp communications, ensuring no high-priority message goes unnoticed.
