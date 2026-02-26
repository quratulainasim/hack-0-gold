#!/usr/bin/env python3
"""
Odoo Finance Sentinel Watcher - Enhanced
Monitors Odoo for financial transactions, invoices, and alerts using Odoo XML-RPC API.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def sanitize_filename(text: str) -> str:
    """Sanitize text for filename."""
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50].lower()

def create_inbox_file(transaction_data: Dict[str, str], vault_path: Path) -> bool:
    """Create inbox file for Odoo transaction."""
    try:
        inbox_path = vault_path / "Needs_Action"
        inbox_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        trans_type = sanitize_filename(transaction_data.get('type', 'transaction'))
        filename = f"ODOO_{timestamp}_{trans_type}.md"
        filepath = inbox_path / filename

        content = f"""---
source: odoo
type: {transaction_data.get('type', 'transaction')}
priority: {transaction_data.get('priority', 'high')}
timestamp: {transaction_data.get('timestamp', datetime.now().isoformat())}
status: new
amount: {transaction_data.get('amount', '0.00')}
currency: {transaction_data.get('currency', 'USD')}
---

# Odoo Finance: {transaction_data.get('title', 'Transaction')}

**Type**: {transaction_data.get('type', 'Transaction').title()}
**Amount**: {transaction_data.get('currency', 'USD')} {transaction_data.get('amount', '0.00')}
**Date**: {transaction_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}
**Priority**: {transaction_data.get('priority', 'high').upper()}

---

## Transaction Details

{transaction_data.get('details', '[No details]')}

---

## Context

This financial transaction was flagged as {transaction_data.get('priority', 'high')} priority.

**Source**: Odoo ERP System
**Captured**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Recommended Actions

- [ ] Review transaction details
- [ ] Verify amounts and accounts
- [ ] Approve or flag for review
- [ ] Update accounting records
- [ ] Follow up if needed

---

*Captured by Odoo Finance Sentinel on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Created: {filename}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to create file: {e}")
        return False

def check_odoo_api(vault_path: Path) -> int:
    """Check Odoo using XML-RPC API."""
    try:
        # Check for Odoo credentials
        odoo_url = os.environ.get('ODOO_URL')
        odoo_db = os.environ.get('ODOO_DB')
        odoo_username = os.environ.get('ODOO_USERNAME')
        odoo_password = os.environ.get('ODOO_PASSWORD')

        if not all([odoo_url, odoo_db, odoo_username, odoo_password]):
            print("  [INFO] Odoo credentials not fully configured")
            return 0

        print("  [INFO] Checking Odoo ERP system...")

        # Import xmlrpc.client
        import xmlrpc.client

        # Authenticate with Odoo
        common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
        uid = common.authenticate(odoo_db, odoo_username, odoo_password, {})

        if not uid:
            print("  [ERROR] Odoo authentication failed")
            return 0

        # Connect to models API
        models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')

        # Load processed transactions
        processed_file = vault_path / '.odoo_processed.json'
        processed_ids = set()
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                processed_ids = set(json.load(f))

        new_count = 0

        # Check for draft invoices (need approval)
        try:
            invoices = models.execute_kw(odoo_db, uid, odoo_password,
                'account.move', 'search_read',
                [[['state', '=', 'draft'], ['move_type', 'in', ['out_invoice', 'in_invoice']]]],
                {'fields': ['name', 'amount_total', 'partner_id', 'invoice_date', 'move_type'], 'limit': 10})

            for invoice in invoices:
                invoice_id = str(invoice['id'])

                # Skip if already processed
                if invoice_id in processed_ids:
                    continue

                # Get partner name
                partner_name = invoice['partner_id'][1] if invoice['partner_id'] else 'Unknown'

                # Determine invoice type
                inv_type = 'Customer Invoice' if invoice['move_type'] == 'out_invoice' else 'Vendor Bill'

                # Get invoice date (might be string or date object)
                invoice_date = invoice.get('invoice_date')
                if invoice_date:
                    # If it's already a string, use it; if it's a date object, convert it
                    timestamp = invoice_date if isinstance(invoice_date, str) else invoice_date.isoformat()
                else:
                    timestamp = datetime.now().isoformat()

                # Create transaction data
                transaction_data = {
                    'type': 'invoice',
                    'priority': 'high',
                    'timestamp': timestamp,
                    'amount': f"{invoice['amount_total']:.2f}",
                    'currency': 'USD',
                    'title': f"{inv_type}: {invoice['name']}",
                    'details': f"""**Invoice Number**: {invoice['name']}
**Type**: {inv_type}
**Partner**: {partner_name}
**Amount**: ${invoice['amount_total']:.2f}
**Status**: Draft (Awaiting Approval)
**Date**: {invoice.get('invoice_date', 'Not set')}

This invoice is in draft state and requires approval before posting."""
                }

                # Create inbox file
                if create_inbox_file(transaction_data, vault_path):
                    new_count += 1
                    processed_ids.add(invoice_id)

        except Exception as e:
            print(f"  [WARNING] Could not fetch invoices: {e}")

        # Check for payments (posted today)
        try:
            from datetime import date
            today = date.today().isoformat()

            payments = models.execute_kw(odoo_db, uid, odoo_password,
                'account.payment', 'search_read',
                [[['date', '=', today], ['state', '=', 'posted']]],
                {'fields': ['name', 'amount', 'partner_id', 'date', 'payment_type'], 'limit': 10})

            for payment in payments:
                payment_id = str(payment['id'])

                # Skip if already processed
                if payment_id in processed_ids:
                    continue

                # Get partner name
                partner_name = payment['partner_id'][1] if payment['partner_id'] else 'Unknown'

                # Determine payment type
                pay_type = 'Received' if payment['payment_type'] == 'inbound' else 'Sent'

                # Create transaction data
                transaction_data = {
                    'type': 'payment',
                    'priority': 'medium',
                    'timestamp': payment.get('date', datetime.now().date()).isoformat() if payment.get('date') else datetime.now().isoformat(),
                    'amount': f"{payment['amount']:.2f}",
                    'currency': 'USD',
                    'title': f"Payment {pay_type}: {payment['name']}",
                    'details': f"""**Payment Reference**: {payment['name']}
**Type**: Payment {pay_type}
**Partner**: {partner_name}
**Amount**: ${payment['amount']:.2f}
**Status**: Posted
**Date**: {payment.get('date', 'Not set')}

This payment has been posted to the accounting system."""
                }

                # Create inbox file
                if create_inbox_file(transaction_data, vault_path):
                    new_count += 1
                    processed_ids.add(payment_id)

        except Exception as e:
            print(f"  [WARNING] Could not fetch payments: {e}")

        # Save processed IDs
        with open(processed_file, 'w') as f:
            json.dump(list(processed_ids), f)

        return new_count

    except Exception as e:
        print(f"  [ERROR] Odoo API error: {e}")
        return 0

def watch_odoo(vault_path: Path, check_interval: int = 1800):
    """Watch Odoo for financial activity."""
    print("="*60)
    print("Odoo Finance Sentinel Watcher - Enhanced")
    print("="*60)
    print(f"[INFO] Vault: {vault_path.absolute()}")
    print(f"[INFO] Check Interval: {check_interval} seconds")
    print()

    iteration = 0

    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Check #{iteration}")
            print("-"*60)

            new_count = check_odoo_api(vault_path)

            if new_count > 0:
                print(f"  [OK] Found {new_count} new transaction(s)")
            else:
                print("  [INFO] No new transactions found")

            print(f"  Next check in {check_interval} seconds...")
            print()
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print()
        print("[INFO] Odoo watcher stopped by user")
        sys.exit(0)

def main():
    vault_path = Path.cwd()
    check_interval = int(os.environ.get('ODOO_CHECK_INTERVAL', 1800))
    watch_odoo(vault_path, check_interval)

if __name__ == "__main__":
    main()
