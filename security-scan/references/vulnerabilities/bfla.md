# Broken Function Level Authorization (BFLA) Testing Guide

> BFLA occurs when an application fails to properly verify that a user is authorized to access specific functions or endpoints. Unlike IDOR which focuses on objects, BFLA focuses on actions and API endpoints.

## Scope

- Administrative endpoints accessible to regular users
- Privileged functions without role validation
- API endpoints with inconsistent authorization
- Hidden endpoints discoverable through enumeration

## Methodology

1. Map all available endpoints for different user roles
2. Identify admin/privileged endpoints
3. Test access to privileged endpoints with lower-privilege tokens
4. Check for hidden endpoints via enumeration
5. Test HTTP method variations

## Common Vulnerable Patterns

### Admin Endpoints
- `/api/admin/*` accessible to regular users
- `/api/users/delete` without role check
- `/api/settings/global` modifiable by anyone

### Role-Based Functions
- User can access manager-only reports
- Regular API key can access admin functions
- Staff functions accessible to customers

### Hidden Endpoints
- Undocumented API endpoints
- Debug/development endpoints in production
- Legacy endpoints without updated authorization

## Discovery Techniques

### Endpoint Enumeration
- Analyze JavaScript bundles for API routes
- Check OpenAPI/Swagger documentation
- Fuzz common admin paths: `/admin`, `/manage`, `/internal`
- Review mobile app API calls

### Parameter Discovery
- Add `admin=true`, `role=admin` parameters
- Change `user_type`, `account_type` values
- Test with elevated permission flags

### HTTP Method Testing
- Try POST when only GET is documented
- Test PUT/PATCH/DELETE on read-only endpoints
- Check OPTIONS for allowed methods

## Exploitation Patterns

### Vertical Privilege Escalation
- Regular user accessing admin functions
- Customer accessing staff endpoints
- Read-only user performing write operations

### Function Bypass
- Skip workflow steps (approval, verification)
- Direct access to final action endpoints
- Bypass rate limits via admin endpoints

### Mass Operations
- Bulk delete without authorization
- Export all data via admin export
- Modify system-wide settings

## API-Specific Checks

### REST APIs
- Test all CRUD operations per endpoint
- Check collection vs item permissions
- Verify nested resource authorization

### GraphQL
- Check mutation authorization
- Test admin-only queries
- Verify directive-based authorization

### gRPC
- Test service-level authorization
- Verify method-level permissions

## Validation Requirements

1. Demonstrate access to privileged function as lower-privilege user
2. Show the function executes successfully
3. Prove this differs from expected behavior
4. Document the role/permission mismatch

## False Positives

- Intentionally public endpoints
- Functions with proper role validation
- Rate-limited or monitored but not blocked
- Feature flags controlling access

## Impact

- Unauthorized administrative actions
- Data modification or deletion
- System configuration changes
- User management (create/delete/modify)
- Financial operations

## Pro Tips

1. Map all endpoints for each user role
2. Test the same endpoint with different tokens
3. Check API documentation for undocumented endpoints
4. Look for admin endpoints in client-side code
5. Test HTTP method override headers
6. Check for authorization on sub-resources
7. Test batch/bulk endpoints separately
8. Verify webhook endpoints require authentication
