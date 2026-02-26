# Odoo API Reference

This reference covers authentication and common API patterns for Odoo JSON-RPC.

## Authentication

### XML-RPC Endpoints

Odoo uses two XML-RPC endpoints:

- `/xmlrpc/2/common` - Authentication and version info
- `/xmlrpc/2/object` - Model operations (CRUD)

### Authentication Flow

```python
import xmlrpc.client

# Connect to common endpoint
common = xmlrpc.client.ServerProxy('https://your-odoo.com/xmlrpc/2/common')

# Get version info (no auth required)
version = common.version()

# Authenticate
uid = common.authenticate(
    'database_name',
    'username',
    'api_key_or_password',
    {}
)
```

### API Key vs Password

**API Keys (Recommended):**
- More secure than passwords
- Can be revoked without changing password
- Generated per user in Odoo settings

**Passwords:**
- Less secure
- Should only be used for development/testing

## CRUD Operations

### Search

Find records matching criteria:

```python
# Search for partners named "Acme"
partner_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('name', '=', 'Acme Corp')]]
)

# With limit
partner_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('name', 'ilike', 'Acme')]],
    {'limit': 5}
)
```

**Domain operators:**
- `=` - equals
- `!=` - not equals
- `>`, `>=`, `<`, `<=` - comparisons
- `like`, `ilike` - pattern matching (ilike is case-insensitive)
- `in`, `not in` - list membership
- `&`, `|`, `!` - logical operators

### Read

Retrieve field values:

```python
# Read all fields
records = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'read',
    [partner_ids]
)

# Read specific fields only
records = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'read',
    [partner_ids],
    {'fields': ['name', 'email', 'phone']}
)
```

### Search and Read (Combined)

More efficient than separate search + read:

```python
records = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search_read',
    [[('is_company', '=', True)]],
    {'fields': ['name', 'email'], 'limit': 10}
)
```

### Create

Create new records:

```python
# Single record
partner_id = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'create',
    [{
        'name': 'New Partner',
        'email': 'partner@example.com',
        'is_company': True
    }]
)

# Multiple records
partner_ids = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'create',
    [
        {'name': 'Partner 1', 'email': 'p1@example.com'},
        {'name': 'Partner 2', 'email': 'p2@example.com'}
    ]
)
```

### Update (Write)

Update existing records:

```python
success = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'write',
    [[partner_id], {'email': 'newemail@example.com'}]
)
```

### Delete (Unlink)

Delete records:

```python
success = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'unlink',
    [[partner_id]]
)
```

## One2Many and Many2Many Fields

### Creating Records with Related Records

Use special command tuples:

```python
# Create invoice with lines
invoice_id = models.execute_kw(
    db, uid, api_key,
    'account.move', 'create',
    [{
        'partner_id': partner_id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [
            (0, 0, {  # (0, 0, values) = create new record
                'name': 'Product A',
                'quantity': 2,
                'price_unit': 100.0,
                'account_id': account_id
            }),
            (0, 0, {
                'name': 'Product B',
                'quantity': 1,
                'price_unit': 50.0,
                'account_id': account_id
            })
        ]
    }]
)
```

**Command tuple formats:**
- `(0, 0, values)` - Create new record with values
- `(1, id, values)` - Update existing record with id
- `(2, id)` - Delete record with id
- `(3, id)` - Unlink record with id (remove relation but don't delete)
- `(4, id)` - Link existing record with id
- `(5,)` - Unlink all records
- `(6, 0, [ids])` - Replace all links with ids list

## Calling Model Methods

### Action Methods

Many Odoo models have action methods:

```python
# Post an invoice
models.execute_kw(
    db, uid, api_key,
    'account.move', 'action_post',
    [[invoice_id]]
)

# Confirm a sale order
models.execute_kw(
    db, uid, api_key,
    'sale.order', 'action_confirm',
    [[order_id]]
)
```

### Custom Methods

Call any model method:

```python
# Get invoice's payment state
result = models.execute_kw(
    db, uid, api_key,
    'account.move', 'my_custom_method',
    [[invoice_id]],
    {'param1': 'value1'}
)
```

## Error Handling

### Common Errors

**Authentication Error:**
```python
try:
    uid = common.authenticate(db, username, api_key, {})
    if not uid:
        print("Invalid credentials")
except Exception as e:
    print(f"Connection error: {e}")
```

**Access Rights Error:**
```python
try:
    models.execute_kw(db, uid, api_key, 'account.move', 'create', [values])
except xmlrpc.client.Fault as e:
    if 'AccessError' in str(e):
        print("Insufficient permissions")
    else:
        print(f"Error: {e}")
```

**Validation Error:**
```python
try:
    models.execute_kw(db, uid, api_key, 'res.partner', 'create', [values])
except xmlrpc.client.Fault as e:
    if 'ValidationError' in str(e):
        print("Invalid field values")
    else:
        print(f"Error: {e}")
```

## Best Practices

### 1. Batch Operations

Instead of creating records one by one:

```python
# Bad - Multiple API calls
for item in items:
    models.execute_kw(db, uid, api_key, 'res.partner', 'create', [item])

# Good - Single API call
models.execute_kw(db, uid, api_key, 'res.partner', 'create', items)
```

### 2. Field Selection

Only read fields you need:

```python
# Bad - Reads all fields (slow)
records = models.execute_kw(db, uid, api_key, 'res.partner', 'read', [ids])

# Good - Only needed fields
records = models.execute_kw(
    db, uid, api_key, 'res.partner', 'read',
    [ids], {'fields': ['name', 'email']}
)
```

### 3. Search Limits

Always use limits for large datasets:

```python
# Bad - Could return thousands of records
ids = models.execute_kw(db, uid, api_key, 'res.partner', 'search', [[]])

# Good - Paginated
ids = models.execute_kw(
    db, uid, api_key, 'res.partner', 'search',
    [[]], {'limit': 100, 'offset': 0}
)
```

### 4. Check Before Create

Avoid duplicates:

```python
# Check if partner exists
existing = models.execute_kw(
    db, uid, api_key,
    'res.partner', 'search',
    [[('email', '=', 'test@example.com')]], {'limit': 1}
)

if not existing:
    # Create only if doesn't exist
    partner_id = models.execute_kw(
        db, uid, api_key,
        'res.partner', 'create',
        [{'name': 'Test', 'email': 'test@example.com'}]
    )
```

### 5. Transaction Safety

Odoo handles transactions automatically, but be aware:

- Each `execute_kw` call is a separate transaction
- If you need atomicity, use a custom server-side method
- Failed operations are automatically rolled back

## Performance Tips

1. **Use search_read instead of search + read**
2. **Batch create/write operations**
3. **Limit fields in read operations**
4. **Use appropriate search limits**
5. **Cache frequently accessed data (accounts, journals, partners)**
6. **Avoid nested loops with API calls**

## Security Considerations

1. **Never hardcode credentials** - Use environment variables or config files
2. **Use API keys instead of passwords**
3. **Implement rate limiting** for public-facing integrations
4. **Validate all input data** before sending to Odoo
5. **Log all operations** for audit trails
6. **Use HTTPS only** - Never plain HTTP
7. **Rotate API keys regularly**
8. **Limit API key permissions** to minimum required
