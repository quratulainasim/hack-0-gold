#!/usr/bin/env python3
"""
Odoo Accounting Bridge - Sync Script
Syncs vault data with Odoo accounting ledger using JSON-RPC API.
"""

import argparse
import json
import os
import re
import xmlrpc.client
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class OdooClient:
    """Odoo JSON-RPC client for accounting operations"""

    def __init__(self, url: str, database: str, username: str, api_key: str):
        self.url = url
        self.database = database
        self.username = username
        self.api_key = api_key
        self.uid = None

        # Setup XML-RPC endpoints
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def authenticate(self) -> bool:
        """Authenticate with Odoo"""
        try:
            self.uid = self.common.authenticate(
                self.database, self.username, self.api_key, {}
            )
            if self.uid:
                print(f"✓ Authenticated as user ID: {self.uid}")
                return True
            else:
                print("✗ Authentication failed")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo model method"""
        return self.models.execute_kw(
            self.database, self.uid, self.api_key,
            model, method, args, kwargs
        )

    def search(self, model: str, domain: List, limit: int = None) -> List[int]:
        """Search for records"""
        kwargs = {}
        if limit:
            kwargs['limit'] = limit
        return self.execute(model, 'search', domain, **kwargs)

    def read(self, model: str, ids: List[int], fields: List[str] = None) -> List[Dict]:
        """Read record data"""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        return self.execute(model, 'read', ids, **kwargs)

    def create(self, model: str, values: Dict) -> int:
        """Create new record"""
        return self.execute(model, 'create', values)

    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update existing records"""
        return self.execute(model, 'write', ids, values)

    def get_partner_id(self, partner_name: str, create_if_missing: bool = False) -> Optional[int]:
        """Get partner ID by name, optionally create if missing"""
        partner_ids = self.search('res.partner', [('name', '=', partner_name)], limit=1)

        if partner_ids:
            return partner_ids[0]
        elif create_if_missing:
            print(f"  Creating new partner: {partner_name}")
            return self.create('res.partner', {'name': partner_name})
        else:
            return None

    def get_account_id(self, account_code: str) -> Optional[int]:
        """Get account ID by code"""
        account_ids = self.search('account.account', [('code', '=', account_code)], limit=1)
        return account_ids[0] if account_ids else None

    def get_journal_id(self, journal_name: str) -> Optional[int]:
        """Get journal ID by name"""
        journal_ids = self.search('account.journal', [('name', '=', journal_name)], limit=1)
        return journal_ids[0] if journal_ids else None

    def create_invoice(self, invoice_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Create customer invoice in Odoo"""
        try:
            # Get partner
            partner_id = invoice_data.get('customer_id')
            if not partner_id:
                partner_id = self.get_partner_id(invoice_data['customer'], create_if_missing=True)

            if not partner_id:
                return False, f"Partner '{invoice_data['customer']}' not found", None

            # Prepare invoice values
            invoice_vals = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'invoice_date': invoice_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'invoice_date_due': invoice_data.get('due_date'),
                'ref': invoice_data.get('reference', ''),
                'invoice_line_ids': []
            }

            # Add invoice lines
            if 'invoice_lines' in invoice_data:
                for line in invoice_data['invoice_lines']:
                    account_id = self.get_account_id(line.get('account_code', invoice_data.get('account_code')))
                    if not account_id:
                        return False, f"Account code '{line.get('account_code')}' not found", None

                    line_vals = (0, 0, {
                        'name': line.get('product', line.get('description', 'Service')),
                        'quantity': line.get('quantity', 1),
                        'price_unit': line.get('price_unit', invoice_data.get('amount', 0)),
                        'account_id': account_id
                    })
                    invoice_vals['invoice_line_ids'].append(line_vals)
            else:
                # Single line invoice
                account_id = self.get_account_id(invoice_data.get('account_code', '400000'))
                if not account_id:
                    return False, f"Account code '{invoice_data.get('account_code')}' not found", None

                line_vals = (0, 0, {
                    'name': invoice_data.get('description', 'Service'),
                    'quantity': 1,
                    'price_unit': invoice_data.get('amount', 0),
                    'account_id': account_id
                })
                invoice_vals['invoice_line_ids'].append(line_vals)

            # Create invoice
            invoice_id = self.create('account.move', invoice_vals)

            # Post invoice if requested
            if invoice_data.get('post', False):
                self.execute('account.move', 'action_post', [invoice_id])

            return True, f"Invoice created with ID: {invoice_id}", invoice_id

        except Exception as e:
            return False, f"Error creating invoice: {str(e)}", None

    def create_bill(self, bill_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Create vendor bill in Odoo"""
        try:
            # Get partner
            partner_id = bill_data.get('vendor_id')
            if not partner_id:
                partner_id = self.get_partner_id(bill_data['vendor'], create_if_missing=True)

            if not partner_id:
                return False, f"Vendor '{bill_data['vendor']}' not found", None

            # Prepare bill values
            bill_vals = {
                'partner_id': partner_id,
                'move_type': 'in_invoice',
                'invoice_date': bill_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'invoice_date_due': bill_data.get('due_date'),
                'ref': bill_data.get('reference', ''),
                'invoice_line_ids': []
            }

            # Add bill lines
            account_id = self.get_account_id(bill_data.get('account_code', '600000'))
            if not account_id:
                return False, f"Account code '{bill_data.get('account_code')}' not found", None

            line_vals = (0, 0, {
                'name': bill_data.get('description', 'Expense'),
                'quantity': 1,
                'price_unit': bill_data.get('amount', 0),
                'account_id': account_id
            })
            bill_vals['invoice_line_ids'].append(line_vals)

            # Create bill
            bill_id = self.create('account.move', bill_vals)

            return True, f"Bill created with ID: {bill_id}", bill_id

        except Exception as e:
            return False, f"Error creating bill: {str(e)}", None

    def create_journal_entry(self, entry_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Create journal entry in Odoo"""
        try:
            # Get journal
            journal_id = self.get_journal_id(entry_data.get('journal', 'Miscellaneous Operations'))
            if not journal_id:
                return False, f"Journal '{entry_data.get('journal')}' not found", None

            # Prepare entry values
            entry_vals = {
                'move_type': 'entry',
                'date': entry_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'journal_id': journal_id,
                'ref': entry_data.get('reference', ''),
                'line_ids': []
            }

            # Add journal lines
            total_debit = 0
            total_credit = 0

            for line in entry_data.get('lines', []):
                account_id = self.get_account_id(line['account_code'])
                if not account_id:
                    return False, f"Account code '{line['account_code']}' not found", None

                debit = float(line.get('debit', 0))
                credit = float(line.get('credit', 0))
                total_debit += debit
                total_credit += credit

                line_vals = (0, 0, {
                    'name': line.get('label', 'Journal Entry Line'),
                    'account_id': account_id,
                    'debit': debit,
                    'credit': credit
                })
                entry_vals['line_ids'].append(line_vals)

            # Validate balance
            if abs(total_debit - total_credit) > 0.01:
                return False, f"Entry not balanced: Debit {total_debit} != Credit {total_credit}", None

            # Create entry
            entry_id = self.create('account.move', entry_vals)

            return True, f"Journal entry created with ID: {entry_id}", entry_id

        except Exception as e:
            return False, f"Error creating journal entry: {str(e)}", None

    def create_payment(self, payment_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Create payment in Odoo"""
        try:
            # Get partner
            partner_id = self.get_partner_id(payment_data['partner'], create_if_missing=False)
            if not partner_id:
                return False, f"Partner '{payment_data['partner']}' not found", None

            # Get journal
            journal_id = self.get_journal_id(payment_data.get('journal', 'Bank'))
            if not journal_id:
                return False, f"Journal '{payment_data.get('journal')}' not found", None

            # Prepare payment values
            payment_vals = {
                'payment_type': payment_data.get('payment_type', 'inbound'),
                'partner_type': 'customer' if payment_data.get('payment_type') == 'inbound' else 'supplier',
                'partner_id': partner_id,
                'amount': payment_data.get('amount', 0),
                'date': payment_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'journal_id': journal_id,
                'ref': payment_data.get('reference', '')
            }

            # Create payment
            payment_id = self.create('account.payment', payment_vals)

            # Post payment
            self.execute('account.payment', 'action_post', [payment_id])

            return True, f"Payment created with ID: {payment_id}", payment_id

        except Exception as e:
            return False, f"Error creating payment: {str(e)}", None


class VaultSyncer:
    """Sync vault data with Odoo"""

    def __init__(self, odoo_client: OdooClient, vault_path: str, dry_run: bool = False):
        self.odoo = odoo_client
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.results = {
            'processed': 0,
            'synced': 0,
            'errors': 0,
            'skipped': 0,
            'details': []
        }

    def parse_markdown_file(self, filepath: str) -> Optional[Dict]:
        """Parse markdown file with frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            metadata = {}
            current_key = None
            current_list = None

            for line in frontmatter.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith('- ') and current_list is not None:
                    # List item
                    item_text = line[2:].strip()
                    if ':' in item_text:
                        # Dict item in list
                        item_dict = {}
                        for pair in item_text.split(','):
                            if ':' in pair:
                                k, v = pair.split(':', 1)
                                item_dict[k.strip()] = v.strip().strip('"\'')
                        current_list.append(item_dict)
                    else:
                        current_list.append(item_text)
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    if value == '' or value == '[]':
                        # Start of list
                        current_list = []
                        metadata[key] = current_list
                        current_key = key
                    else:
                        metadata[key] = value
                        current_list = None

            metadata['_body'] = body
            metadata['_filepath'] = filepath

            return metadata

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def update_file_sync_status(self, filepath: str, odoo_id: int):
        """Update markdown file with sync status"""
        if self.dry_run:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update frontmatter
            if 'odoo_synced: false' in content:
                content = content.replace('odoo_synced: false', 'odoo_synced: true')
            elif 'odoo_synced:' not in content:
                # Add sync status
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    parts[1] += f"\nodoo_synced: true\nodoo_id: {odoo_id}\nodoo_synced_date: {datetime.now().isoformat()}"
                    content = '---'.join(parts)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(f"Error updating {filepath}: {e}")

    def sync_file(self, filepath: str):
        """Sync single file to Odoo"""
        self.results['processed'] += 1

        data = self.parse_markdown_file(filepath)
        if not data:
            return

        # Check if already synced
        if data.get('odoo_synced') == 'true' and not self.dry_run:
            self.results['skipped'] += 1
            return

        item_type = data.get('type', '').lower()
        filename = os.path.basename(filepath)

        if self.dry_run:
            print(f"[DRY RUN] Would sync: {filename} (type: {item_type})")
            self.results['synced'] += 1
            return

        success = False
        message = ""
        odoo_id = None

        # Route to appropriate handler
        if item_type == 'invoice':
            success, message, odoo_id = self.odoo.create_invoice(data)
        elif item_type in ['bill', 'expense']:
            success, message, odoo_id = self.odoo.create_bill(data)
        elif item_type == 'journal_entry':
            success, message, odoo_id = self.odoo.create_journal_entry(data)
        elif item_type == 'payment':
            success, message, odoo_id = self.odoo.create_payment(data)
        else:
            message = f"Unsupported type: {item_type}"

        if success:
            print(f"✓ {filename}: {message}")
            self.results['synced'] += 1
            self.results['details'].append({
                'file': filename,
                'status': 'success',
                'message': message,
                'odoo_id': odoo_id
            })
            self.update_file_sync_status(filepath, odoo_id)
        else:
            print(f"✗ {filename}: {message}")
            self.results['errors'] += 1
            self.results['details'].append({
                'file': filename,
                'status': 'error',
                'message': message
            })

    def sync_vault(self, folder: str = 'Done'):
        """Sync all files in vault folder"""
        vault_folder = os.path.join(self.vault_path, folder)

        if not os.path.exists(vault_folder):
            print(f"Vault folder not found: {vault_folder}")
            return

        print(f"Scanning: {vault_folder}")

        for filename in os.listdir(vault_folder):
            if filename.endswith('.md'):
                filepath = os.path.join(vault_folder, filename)
                self.sync_file(filepath)

    def generate_report(self, output_file: str = None):
        """Generate sync report"""
        report = f"""# Odoo Sync Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total items processed: {self.results['processed']}
- Successfully synced: {self.results['synced']}
- Errors: {self.results['errors']}
- Skipped (already synced): {self.results['skipped']}

"""

        if self.results['details']:
            # Successes
            successes = [d for d in self.results['details'] if d['status'] == 'success']
            if successes:
                report += "## Synced Items\n"
                for detail in successes:
                    report += f"✓ {detail['file']} → {detail['message']}\n"
                report += "\n"

            # Errors
            errors = [d for d in self.results['details'] if d['status'] == 'error']
            if errors:
                report += "## Errors\n"
                for detail in errors:
                    report += f"✗ {detail['file']}: {detail['message']}\n"
                report += "\n"

        print("\n" + report)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Sync vault data to Odoo accounting')
    parser.add_argument('--config', '-c', required=True, help='Config file (JSON)')
    parser.add_argument('--vault-path', '-v', required=True, help='Path to vault')
    parser.add_argument('--folder', '-f', default='Done', help='Vault folder to sync (default: Done)')
    parser.add_argument('--operation', '-o', choices=['invoice', 'bill', 'journal', 'payment', 'all'],
                       default='all', help='Operation type')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Preview without syncing')
    parser.add_argument('--report', '-r', help='Output report file')

    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Initialize Odoo client
    odoo = OdooClient(
        url=config['url'],
        database=config['database'],
        username=config['username'],
        api_key=config['api_key']
    )

    # Authenticate
    if not args.dry_run:
        if not odoo.authenticate():
            print("Authentication failed. Exiting.")
            return

    # Sync vault
    syncer = VaultSyncer(odoo, args.vault_path, args.dry_run)
    syncer.sync_vault(args.folder)

    # Generate report
    syncer.generate_report(args.report)


if __name__ == '__main__':
    main()
