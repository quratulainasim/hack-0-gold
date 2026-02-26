# Odoo Accounting Models

This reference documents the key Odoo accounting models used by the bridge.

## account.move (Invoices, Bills, Journal Entries)

The `account.move` model represents all accounting entries in Odoo.

### Move Types

- `out_invoice` - Customer Invoice
- `in_invoice` - Vendor Bill
- `out_refund` - Customer Credit Note
- `in_refund` - Vendor Credit Note
- `entry` - Journal Entry

### Key Fields

**Header Fields:**
- `move_type` (string) - Type of move (required)
- `partner_id` (many2one: res.partner) - Customer/Vendor
- `date` (date) - Accounting date
- `invoice_date` (date) - Invoice date (for invoices)
- `invoice_date_due` (date) - Due date (for invoices)
- `ref` (string) - Reference/memo
- `journal_id` (many2one: account.journal) - Journal
- `currency_id` (many2one: res.currency) - Currency
- `state` (selection) - Status: draft, posted, cancel
- `amount_total` (float) - Total amount (computed)
- `amount_residual` (float) - Amount due (computed)

**Line Fields (invoice_line_ids / line_ids):**
- `name` (string) - Description (required)
- `account_id` (many2one: account.account) - Account (required)
- `quantity` (float) - Quantity
- `price_unit` (float) - Unit price
- `debit` (float) - Debit amount (for journal entries)
- `credit` (float) - Credit amount (for journal entries)
- `tax_ids` (many2many: account.tax) - Taxes

### Example: Customer Invoice

```python
invoice_vals = {
    'move_type': 'out_invoice',
    'partner_id': 123,
    'invoice_date': '2026-02-19',
    'invoice_date_due': '2026-03-19',
    'ref': 'INV-2026-001',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Consulting Services',
            'quantity': 10,
            'price_unit': 150.0,
            'account_id': 456  # Revenue account
        })
    ]
}

invoice_id = models.execute_kw(
    db, uid, api_key,
    'account.move', 'create',
    [invoice_vals]
)

# Post the invoice
models.execute_kw(
    db, uid, api_key,
    'account.move', 'action_post',
    [[invoice_id]]
)
```

### Example: Vendor Bill

```python
bill_vals = {
    'move_type': 'in_invoice',
    'partner_id': 789,
    'invoice_date': '2026-02-19',
    'ref': 'BILL-2026-001',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Office Supplies',
            'quantity': 1,
            'price_unit': 250.0,
            'account_id': 321  # Expense account
        })
    ]
}

bill_id = models.execute_kw(
    db, uid, api_key,
    'account.move', 'create',
    [bill_vals]
)
```

### Example: Journal Entry

```python
entry_vals = {
    'move_type': 'entry',
    'date': '2026-02-19',
    'journal_id': 1,  # General Journal
    'ref': 'ADJ-2026-001',
    'line_ids': [
        (0, 0, {
            'name': 'Adjustment - Debit',
            'account_id': 100,  # Asset account
            'debit': 1000.0,
            'credit': 0.0
        }),
        (0, 0, {
            'name': 'Adjustment - Credit',
            'account_id': 200,  # Liability account
            'debit': 0.0,
            'credit': 1000.0
        })
    ]
}

entry_id = models.execute_kw(
    db, uid, api_key,
    'account.move', 'create',
    [entry_vals]
)
```

### Important Methods

- `action_post()` - Post/validate the move
- `button_draft()` - Reset to draft
- `button_cancel()` - Cancel the move
- `action_invoice_sent()` - Mark as sent
- `action_register_payment()` - Register payment

## account.payment (Payments)

The `account.payment` model handles payments and receipts.

### Key Fields

- `payment_type` (selection) - inbound, outbound, transfer
- `partner_type` (selection) - customer, supplier
- `partner_id` (many2one: res.partner) - Customer/Vendor
- `amount` (float) - Payment amount (required)
- `date` (date) - Payment date
- `journal_id` (many2one: account.journal) - Payment journal (required)
- `payment_method_id` (many2one: account.payment.method) - Payment method
- `ref` (string) - Reference/memo
- `state` (selection) - draft, posted, sent, reconciled, cancelled

### Example: Customer Payment

```python
payment_vals = {
    'payment_type': 'inbound',
    'partner_type': 'customer',
    'partner_id': 123,
    'amount': 1500.0,
    'date': '2026-02-19',
    'journal_id': 5,  # Bank journal
    'ref': 'Payment for INV-2026-001'
}

payment_id = models.execute_kw(
    db, uid, api_key,
    'account.payment', 'create',
    [payment_vals]
)

# Post the payment
models.execute_kw(
    db, uid, api_key,
    'account.payment', 'action_post',
    [[payment_id]]
)
```

### Example: Vendor Payment

```python
payment_vals = {
    'payment_type': 'outbound',
    'partner_type': 'supplier',
    'partner_id': 789,
    'amount': 250.0,
    'date': '2026-02-19',
    'journal_id': 5,  # Bank journal
    'ref': 'Payment for BILL-2026-001'
}

payment_id = models.execute_kw(
    db, uid, api_key,
    'account.payment', 'create',
    [payment_vals]
)
```

## res.partner (Customers/Vendors)

The `res.partner` model represents contacts, customers, and vendors.

### Key Fields

- `name` (string) - Name (required)
- `email` (string) - Email address
- `phone` (string) - Phone number
- `mobile` (string) - Mobile number
- `street` (string) - Street address
- `city` (string) - City
- `zip` (string) - ZIP/Postal code
- `country_id` (many2one: res.country) - Country
- `is_company` (boolean) - Is a company
- `customer_rank` (integer) - Customer rank (>0 = customer)
- `supplier_rank` (integer) - Supplier rank (>0 = supplier)
- `vat` (string) - Tax ID

### Example: Create Partner

```python
partner_vals = {
    'name': 'Acme Corporation',
    'email': 'contact@acme.com',
    'phone': '+1-555-0100',
    'street': '123 Main St',
    'city': 'New York',
    'zip': '10001',
    'is_company': True,
    'customer_rank': 1  # Mark as customer
}

partner_id = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'create',
    [partner_vals]
)
```

### Search Partners

```python
# Find by name
partner_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('name', '=', 'Acme Corporation')]]
)

# Find by email
partner_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('email', '=', 'contact@acme.com')]]
)

# Find all customers
customer_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('customer_rank', '>', 0)]]
)
```

## account.account (Chart of Accounts)

The `account.account` model represents accounts in the chart of accounts.

### Key Fields

- `code` (string) - Account code (required, unique)
- `name` (string) - Account name (required)
- `user_type_id` (many2one: account.account.type) - Account type
- `reconcile` (boolean) - Allow reconciliation
- `deprecated` (boolean) - Deprecated account
- `currency_id` (many2one: res.currency) - Currency

### Common Account Types

- **Assets**: 100000-199999
- **Liabilities**: 200000-299999
- **Equity**: 300000-399999
- **Revenue**: 400000-499999
- **Expenses**: 600000-699999

### Example: Find Account

```python
# Find by code
account_ids = models.execute_kw(
    db, uid, api_key,
    'account.account', 'search',
    [[('code', '=', '400000')]]
)

# Find revenue accounts
revenue_ids = models.execute_kw(
    db, uid, api_key,
    'account.account', 'search',
    [[('code', '>=', '400000'), ('code', '<', '500000')]]
)
```

## account.journal (Journals)

The `account.journal` model represents accounting journals.

### Key Fields

- `name` (string) - Journal name (required)
- `code` (string) - Journal code (required)
- `type` (selection) - sale, purchase, cash, bank, general
- `currency_id` (many2one: res.currency) - Currency
- `default_account_id` (many2one: account.account) - Default account

### Common Journals

- **Sales Journal** - Customer invoices
- **Purchase Journal** - Vendor bills
- **Bank Journal** - Bank transactions
- **Cash Journal** - Cash transactions
- **General Journal** - Manual entries

### Example: Find Journal

```python
# Find by name
journal_ids = models.execute_kw(
    db, uid, api_key,
    'account.journal', 'search',
    [[('name', '=', 'Bank')]]
)

# Find by type
bank_journals = models.execute_kw(
    db, uid, api_key,
    'account.journal', 'search',
    [[('type', '=', 'bank')]]
)
```

## account.tax (Taxes)

The `account.tax` model represents tax rates.

### Key Fields

- `name` (string) - Tax name (required)
- `amount` (float) - Tax rate percentage
- `amount_type` (selection) - percent, fixed, division
- `type_tax_use` (selection) - sale, purchase, none
- `price_include` (boolean) - Tax included in price

### Example: Apply Tax to Invoice Line

```python
# Find tax
tax_ids = models.execute_kw(
    db, uid, api_key,
    'account.tax', 'search',
    [[('name', '=', 'Sales Tax 10%')]]
)

# Create invoice with tax
invoice_vals = {
    'move_type': 'out_invoice',
    'partner_id': 123,
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product',
            'quantity': 1,
            'price_unit': 100.0,
            'account_id': 456,
            'tax_ids': [(6, 0, tax_ids)]  # Link taxes
        })
    ]
}
```

## Field Validation Rules

### Required Fields by Model

**account.move (Invoice):**
- `move_type`
- `partner_id` (for invoices/bills)
- `invoice_line_ids` (at least one line)
- Each line needs: `name`, `account_id`

**account.payment:**
- `payment_type`
- `partner_type`
- `partner_id`
- `amount`
- `journal_id`

**res.partner:**
- `name`

**account.account:**
- `code`
- `name`
- `user_type_id`

### Common Validation Errors

1. **Unbalanced Journal Entry**: Debit != Credit
2. **Missing Account**: Account code doesn't exist
3. **Missing Partner**: Partner not found
4. **Invalid Date**: Date format incorrect
5. **Negative Amount**: Amount must be positive
6. **Duplicate Code**: Account/journal code already exists
7. **Missing Lines**: Invoice without lines
8. **Wrong Move Type**: Invalid move_type value

## Performance Considerations

### Caching Strategy

Cache these frequently accessed records:

```python
# Cache accounts
accounts = models.execute_kw(
    db, uid, api_key,
    'account.account', 'search_read',
    [[]],
    {'fields': ['code', 'name', 'id']}
)
account_cache = {a['code']: a['id'] for a in accounts}

# Cache journals
journals = models.execute_kw(
    db, uid, api_key,
    'account.journal', 'search_read',
    [[]],
    {'fields': ['name', 'id']}
)
journal_cache = {j['name']: j['id'] for j in journals}

# Cache partners
partners = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search_read',
    [[('customer_rank', '>', 0)]],
    {'fields': ['name', 'id']}
)
partner_cache = {p['name']: p['id'] for p in partners}
```

### Batch Operations

Create multiple invoices at once:

```python
invoice_list = [
    {
        'move_type': 'out_invoice',
        'partner_id': 123,
        'invoice_line_ids': [(0, 0, {...})]
    },
    {
        'move_type': 'out_invoice',
        'partner_id': 456,
        'invoice_line_ids': [(0, 0, {...})]
    }
]

invoice_ids = models.execute_kw(
    db, uid, api_key,
    'account.move', 'create',
    invoice_list
)
```
