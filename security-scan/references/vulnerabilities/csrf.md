# Cross-Site Request Forgery (CSRF) Testing Guide

> CSRF exploits the trust a web application has in the user's browser. Modern defenses include SameSite cookies, CSRF tokens, and origin validation, but gaps remain in complex architectures.

## Scope

- State-changing requests (POST, PUT, DELETE, PATCH)
- Form submissions and API calls
- Cookie-based authentication systems
- Cross-origin request handling

## Methodology

1. Identify state-changing endpoints that rely on cookie-based authentication
2. Check for CSRF token implementation and validation
3. Analyze SameSite cookie attributes
4. Test origin/referer header validation
5. Attempt cross-origin requests with various techniques

## Common Attack Vectors

### Form-Based CSRF
- Auto-submitting forms via JavaScript
- Hidden forms triggered by user interaction
- GET-based state changes (anti-pattern)

### API-Based CSRF
- XMLHttpRequest with credentials
- Fetch API with credentials: 'include'
- WebSocket connections from malicious origins

## Defense Analysis

### CSRF Tokens
- Check token presence in forms and AJAX requests
- Verify token is tied to user session
- Test token reuse across sessions
- Check for token in URL (bad practice)

### SameSite Cookies
- **Strict**: Cookie not sent on cross-origin requests
- **Lax**: Cookie sent on top-level navigation GET requests
- **None**: Cookie sent on all requests (requires Secure)

### Origin/Referer Validation
- Test with missing Origin header
- Test with null Origin
- Test with spoofed Referer (limited by browsers)

## Bypass Techniques

### Token Bypass
- Check if token validation is optional
- Test empty token value
- Test token from different session
- Check for predictable tokens

### SameSite Bypass
- Top-level navigation for Lax mode
- Window.open() with user interaction
- Meta refresh redirects
- Client-side redirects

### Origin Validation Bypass
- Subdomain confusion (sub.attacker.com vs sub.target.com)
- Port variations
- Protocol downgrade
- Null origin (sandboxed iframes)

## High-Value Targets

- Password/email change
- Account deletion
- Financial transactions
- Permission/role changes
- API key generation/revocation
- OAuth application authorization

## Validation Requirements

1. Demonstrate unauthorized state change from attacker-controlled page
2. Show the action executes with victim's privileges
3. Prove token/origin validation is missing or bypassable
4. Document the impact of the unauthorized action

## False Positives

- Endpoints with proper CSRF token validation
- SameSite=Strict cookies for sensitive operations
- Proper origin validation with no bypasses
- Re-authentication required for sensitive actions

## Impact

- Account takeover via email/password change
- Financial loss via unauthorized transactions
- Privilege escalation via role changes
- Data loss via deletion operations

## Pro Tips

1. Test all state-changing endpoints, not just obvious ones
2. Check if CSRF protection differs between web and API
3. Test mobile API endpoints which often lack CSRF protection
4. Look for JSON endpoints accepting form-encoded data
5. Test CORS configuration alongside CSRF
