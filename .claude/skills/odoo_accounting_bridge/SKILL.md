---
name: odoo_accounting_bridge
description: Sync vault data with Odoo accounting ledger using JSON-RPC API. Use this skill when the user asks to sync accounting data to Odoo, create Odoo invoices, post journal entries to Odoo, sync financial records, integrate with Odoo ERP, or bridge vault transactions to Odoo accounting system.
license: MIT
---

# Odoo Accounting Bridge

This skill syncs vault data with your Odoo accounting ledger using the JSON-RPC API.

## Quick Start

Sync vault data to Odoo:

```bash
python scripts/odoo_sync.py --config config.json --vault-path /path/to/vault
```

## Setup

### 1. Configure Odoo Connection

Create a `config.json` file:

```json
{
  "url": "https://your-odoo-instance.com",
  "database": "your_database",
  "username": "your_username",
  "api_key": "your_api_key",
  "company_id": 1
}
```

**Getting your API key:**
1. Log into Odoo
2. Go to Settings → Users & Companies → Users
3. Select your user
4. Click "API Keys" tab
5. Generate new API key

### 2. Prepare Vault Data

Vault items should include accounting metadata in frontmatter:

```markdown
---
type: invoice
customer: "Acme Corp"
amount: 1500.00
currency: USD
date: 2026-02-19
account_code: "400000"
status: done
---

# Invoice for Acme Corp

Services rendered for Q1 2026...
```

## Workflow

1. **Scan vault**: Read items from specified vault folders (default: /Done)
2. **Parse metadata**: Extract accounting information from frontmatter
3. **Authenticate**: Connect to Odoo via JSON-RPC
4. **Sync records**: Create/update invoices, journal entries, or payments
5. **Update status**: Mark synced items with `odoo_synced: true` in frontmatter
6. **Log results**: Generate sync report with successes and errors

## Supported Operations

### Create Customer Invoice

```bash
python scripts/odoo_sync.py --operation invoice --vault-path ./vault/Done
```

Creates customer invoices in Odoo from vault items with `type: invoice`.

### Create Vendor Bill

```bash
python scripts/odoo_sync.py --operation bill --vault-path ./vault/Done
```

Creates vendor bills from vault items with `type: bill` or `type: expense`.

### Post Journal Entry

```bash
python scripts/odoo_sync.py --operation journal --vault-path ./vault/Done
```

Posts manual journal entries from vault items with `type: journal_entry`.

### Record Payment

```bash
python scripts/odoo_sync.py --operation payment --vault-path ./vault/Done
```

Records payments from vault items with `type: payment`.

## Vault Data Format

### Invoice Format

```markdown
---
type: invoice
customer: "Customer Name"
customer_id: 123  # Optional: Odoo partner ID
amount: 1500.00
currency: USD
date: 2026-02-19
due_date: 2026-03-19
invoice_lines:
  - product: "Consulting Services"
    quantity: 10
    price_unit: 150.00
    account_code: "400000"
account_code: "400000"  # Default account
status: done
odoo_synced: false
---

# Invoice Description

Detailed description of services...
```

### Journal Entry Format

```markdown
---
type: journal_entry
date: 2026-02-19
journal: "General Journal"
reference: "ADJ-2026-001"
lines:
  - account_code: "100000"
    debit: 1000.00
    credit: 0
    label: "Cash"
  - account_code: "400000"
    debit: 0
    credit: 1000.00
    label: "Revenue"
status: done
odoo_synced: false
---

# Adjustment Entry

Description of adjustment...
```

### Payment Format

```markdown
---
type: payment
payment_type: "inbound"  # or "outbound"
partner: "Customer Name"
amount: 1500.00
currency: USD
date: 2026-02-19
payment_method: "bank"
journal: "Bank"
invoice_ref: "INV/2026/0001"
status: done
odoo_synced: false
---

# Payment Received

Payment details...
```

## Advanced Usage

### Dry Run (Preview Only)

```bash
python scripts/odoo_sync.py --config config.json --vault-path ./vault --dry-run
```

Shows what would be synced without making changes.

### Sync Specific Date Range

```bash
python scripts/odoo_sync.py --config config.json --vault-path ./vault --start-date 2026-02-01 --end-date 2026-02-28
```

### Force Re-sync

```bash
python scripts/odoo_sync.py --config config.json --vault-path ./vault --force
```

Re-syncs items even if already marked as synced.

### Custom Folder

```bash
python scripts/odoo_sync.py --config config.json --vault-path ./vault --folder Accounting
```

Sync from specific vault folder instead of /Done.

## Odoo API Reference

For detailed Odoo model documentation, see [references/odoo-models.md](references/odoo-models.md).

For API authentication and common patterns, see [references/odoo-api.md](references/odoo-api.md).

## Error Handling

The script handles common errors:

- **Authentication failures**: Check credentials in config.json
- **Missing accounts**: Verify account codes exist in Odoo chart of accounts
- **Missing partners**: Script can auto-create partners or fail with warning
- **Duplicate entries**: Checks for existing records by reference number
- **Validation errors**: Reports field validation issues from Odoo

## Sync Report

After each sync, a report is generated:

```markdown
# Odoo Sync Report - 2026-02-19 14:30:00

## Summary
- Total items processed: 15
- Successfully synced: 12
- Errors: 3
- Skipped (already synced): 5

## Synced Items
✓ Invoice INV-2026-001 → Odoo ID: 1234
✓ Payment PAY-2026-005 → Odoo ID: 5678
✓ Journal Entry ADJ-2026-002 → Odoo ID: 9012

## Errors
✗ Invoice INV-2026-003: Account code '999999' not found
✗ Payment PAY-2026-007: Partner 'Unknown Corp' not found
✗ Journal Entry ADJ-2026-004: Debit/Credit imbalance

## Recommendations
- Create missing account: 999999
- Add partner: Unknown Corp
- Review journal entry ADJ-2026-004 for balance
```

## Integration with Other Skills

Works well with:
- **metric-auditor**: Track accounting sync metrics
- **update-dashboard**: Display sync status on dashboard
- **triage-inbox**: Process accounting items before sync

## Security Notes

- Store API keys securely (use environment variables or encrypted config)
- Never commit config.json with credentials to version control
- Use read-only API keys for dry-run operations
- Regularly rotate API keys
- Audit sync logs for unauthorized access
