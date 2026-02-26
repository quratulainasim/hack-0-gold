#!/usr/bin/env python3
"""
Check what apps are installed in Odoo and what permissions are available
"""

import os
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Checking Odoo Apps and Permissions")
print("=" * 60)
print()

# Get credentials
odoo_url = os.getenv('ODOO_URL')
odoo_db = os.getenv('ODOO_DB')
odoo_username = os.getenv('ODOO_USERNAME')
odoo_password = os.getenv('ODOO_PASSWORD')

try:
    # Authenticate
    common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_db, odoo_username, odoo_password, {})

    if not uid:
        print("[ERROR] Authentication failed")
        exit(1)

    print(f"[OK] Authenticated! User ID: {uid}")
    print()

    # Connect to models
    models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')

    # Check installed apps/modules
    print("[INFO] Checking installed apps...")
    print()

    try:
        # Search for accounting-related modules
        modules = models.execute_kw(odoo_db, uid, odoo_password,
            'ir.module.module', 'search_read',
            [[['name', 'in', ['account', 'account_accountant', 'account_invoicing', 'sale', 'purchase']]]],
            {'fields': ['name', 'state', 'shortdesc']})

        if modules:
            print("Accounting-related modules:")
            for module in modules:
                status = "✓ INSTALLED" if module['state'] == 'installed' else "✗ NOT INSTALLED"
                print(f"  {status} - {module['shortdesc']} ({module['name']})")
        else:
            print("  No accounting modules found")
        print()

    except Exception as e:
        print(f"  [WARNING] Could not check modules: {e}")
        print()

    # Check user's current groups/permissions
    print("[INFO] Checking your user permissions...")
    print()

    try:
        # Get user info
        user = models.execute_kw(odoo_db, uid, odoo_password,
            'res.users', 'read',
            [uid],
            {'fields': ['name', 'login', 'groups_id']})

        if user:
            user_data = user[0]
            print(f"User: {user_data['name']} ({user_data['login']})")
            print(f"User ID: {uid}")
            print()

            # Get group names
            if user_data.get('groups_id'):
                groups = models.execute_kw(odoo_db, uid, odoo_password,
                    'res.groups', 'read',
                    [user_data['groups_id']],
                    {'fields': ['name', 'category_id']})

                print("Your current permissions/groups:")
                accounting_found = False
                for group in groups:
                    print(f"  - {group['name']}")
                    if 'account' in group['name'].lower() or 'invoice' in group['name'].lower():
                        accounting_found = True

                print()
                if accounting_found:
                    print("[OK] You have some accounting permissions")
                else:
                    print("[INFO] No accounting permissions found")
            else:
                print("No groups assigned to user")

    except Exception as e:
        print(f"  [WARNING] Could not check user permissions: {e}")
        print()

    # Check what we can actually access
    print()
    print("[INFO] Testing what data you can access...")
    print()

    accessible_models = []

    # Test common models
    test_models = {
        'res.partner': 'Contacts/Customers',
        'res.company': 'Companies',
        'res.users': 'Users',
        'sale.order': 'Sales Orders',
        'purchase.order': 'Purchase Orders',
        'account.move': 'Journal Entries/Invoices',
        'account.payment': 'Payments',
        'product.product': 'Products',
        'crm.lead': 'CRM Leads'
    }

    for model, description in test_models.items():
        try:
            count = models.execute_kw(odoo_db, uid, odoo_password,
                model, 'search_count', [[]])
            print(f"  ✓ {description} ({model}): {count} records")
            accessible_models.append(model)
        except Exception as e:
            print(f"  ✗ {description} ({model}): Not accessible")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Accessible models: {len(accessible_models)}/{len(test_models)}")
    print()

    if 'account.move' in accessible_models or 'account.payment' in accessible_models:
        print("[SUCCESS] You have accounting access!")
        print("The Odoo watcher should work for financial monitoring.")
    elif 'sale.order' in accessible_models or 'purchase.order' in accessible_models:
        print("[INFO] You have sales/purchase access but not accounting.")
        print("I can modify the watcher to monitor sales orders instead.")
    elif 'res.partner' in accessible_models:
        print("[INFO] You only have basic access (contacts).")
        print("I can modify the watcher to monitor new customers/contacts.")
    else:
        print("[WARNING] Very limited access.")
        print("You may need administrator to grant more permissions.")

    print()
    print("Recommendations:")
    if 'account.move' not in accessible_models:
        print("  1. Ask Odoo administrator to install Accounting app")
        print("  2. Ask administrator to grant you accounting permissions")
        print("  3. OR: I can modify watcher to use available models")

except Exception as e:
    print(f"[ERROR] Failed: {e}")
    exit(1)

print()
print("=" * 60)
