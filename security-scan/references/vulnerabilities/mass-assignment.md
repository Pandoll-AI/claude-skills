# Mass Assignment Vulnerability Testing Guide

> Mass assignment occurs when an application automatically binds user input to object properties without proper filtering, allowing attackers to modify fields they shouldn't have access to.

## Scope

- API endpoints accepting JSON/form data
- Object-relational mapping (ORM) frameworks
- Form builders with automatic binding
- GraphQL mutations

## Methodology

1. Identify endpoints that create or update objects
2. Analyze the object model (what fields exist)
3. Add unexpected fields to requests
4. Check if sensitive fields can be modified
5. Test both creation and update operations

## Common Vulnerable Fields

### User/Account
- `role`, `is_admin`, `admin`, `permissions`
- `verified`, `email_verified`, `active`
- `balance`, `credits`, `subscription_level`
- `password`, `password_hash`

### Ownership
- `user_id`, `owner_id`, `created_by`
- `organization_id`, `tenant_id`
- `parent_id`, `account_id`

### Timestamps
- `created_at`, `updated_at`
- `verified_at`, `approved_at`
- `expires_at`, `valid_until`

### Status/State
- `status`, `state`, `approved`
- `published`, `public`, `visible`
- `deleted`, `archived`

## Discovery Techniques

### Field Enumeration
- Check API documentation
- Analyze response objects for field names
- Review client-side JavaScript
- Check error messages for field hints
- Examine GraphQL schema

### Testing Approach
1. Capture normal request
2. Add suspected sensitive field
3. Check if field was modified
4. Verify change in subsequent requests

## Framework-Specific

### Ruby on Rails
- Mass assignment protection via `strong_params`
- Test `attr_accessible` restrictions
- Check for `permit!` usage

### Django
- Check `ModelForm` field restrictions
- Test serializer field definitions
- Look for `exclude` vs `fields`

### Laravel
- Check `$fillable` and `$guarded`
- Test form request validation
- Look for unguarded models

### Node.js/Express
- Check for spread operator usage
- Test mongoose schema restrictions
- Verify input validation

### Spring
- Check `@ModelAttribute` binding
- Test `DataBinder` configurations
- Verify `@JsonIgnore` usage

## GraphQL Considerations

### Mutation Testing
- Test all mutation inputs
- Check for nested object modification
- Verify input type restrictions

### Schema Analysis
- Review input types vs output types
- Check for sensitive fields in inputs
- Test relationship modifications

## Exploitation Examples

### Privilege Escalation
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "role": "admin"
}
```

### Account Takeover
```json
{
  "id": 123,
  "email": "attacker@evil.com",
  "user_id": 456
}
```

### Balance Manipulation
```json
{
  "product_id": 1,
  "quantity": 1,
  "price": 0
}
```

## Validation Requirements

1. Demonstrate modification of restricted field
2. Show the before/after state
3. Prove the impact (privilege change, data modification)
4. Document the exact payload used

## False Positives

- Fields intentionally modifiable by users
- Server-side filtering working correctly
- Read-only fields properly enforced
- Input validation rejecting extra fields

## Impact

- Privilege escalation to admin
- Account takeover via ownership change
- Financial manipulation
- Data integrity compromise
- Bypass of approval workflows

## Pro Tips

1. Always test registration and profile update endpoints
2. Check both POST (create) and PUT/PATCH (update)
3. Compare regular user vs admin response objects
4. Look for price, quantity, and discount fields
5. Test nested object modifications
6. Check array parameters for injection
7. Review API documentation for object schemas
8. Test with both JSON and form-encoded data
