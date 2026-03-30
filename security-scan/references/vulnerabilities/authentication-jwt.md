# Authentication & JWT Testing Guide

> Authentication vulnerabilities enable account takeover, privilege escalation, and unauthorized access. JWT implementation flaws are particularly common in modern APIs.

## Scope

- Session management
- Password policies and reset flows
- JWT implementation and validation
- OAuth/OIDC flows
- Multi-factor authentication
- Remember-me functionality

## JWT Vulnerabilities

### Algorithm Confusion
- Change `alg` to `none` (no signature)
- Change RS256 to HS256 (use public key as HMAC secret)
- Test with empty signature

### Weak Secrets
- Brute force HS256 secrets with common passwords
- Tools: jwt_tool, hashcat, john

### Key Confusion
- `kid` parameter injection (path traversal, SQL injection)
- `jku`/`x5u` pointing to attacker-controlled keys
- `jwk` embedding attacker's key

### Claim Manipulation
- Change `sub` (subject) to another user
- Modify `role`, `admin`, `permissions` claims
- Extend `exp` (expiration) timestamp
- Change `iss` (issuer) if not validated

### Signature Issues
- Missing signature validation
- Signature not checked for specific algorithms
- Accepting unsigned tokens

## Session Management

### Session Fixation
- Session ID not regenerated after login
- Session ID in URL parameters
- Accepting attacker-provided session

### Session Hijacking
- Session transmitted over HTTP
- Lack of Secure/HttpOnly flags
- Cross-site scripting leading to cookie theft

### Insufficient Expiration
- Long-lived sessions
- No idle timeout
- Session valid after password change
- Session valid after logout

## Password Reset Flaws

### Token Issues
- Predictable reset tokens
- Token not invalidated after use
- Token valid for too long
- Token not tied to specific user

### Flow Bypass
- Host header injection in reset email
- Rate limiting bypass
- Account enumeration via reset flow

### Logic Flaws
- Reset without current password
- Reset via security questions (weak)
- Email change without re-authentication

## OAuth/OIDC Vulnerabilities

### Authorization Code Flow
- CSRF in authorization request (missing state)
- Open redirect in redirect_uri
- Authorization code reuse
- Token leakage via referrer

### Implicit Flow
- Token in URL fragment exposed to JavaScript
- No state parameter validation

### Client Vulnerabilities
- Client secret exposure
- Insecure storage of tokens
- Missing PKCE in public clients

## Brute Force & Enumeration

### Login Brute Force
- No rate limiting
- No account lockout
- CAPTCHA bypass
- IP rotation bypass

### Account Enumeration
- Different responses for valid/invalid users
- Timing differences in authentication
- Password reset reveals existence
- Registration reveals existence

## Validation Requirements

1. Demonstrate unauthorized access to another user's account
2. Show privilege escalation or permission bypass
3. Prove JWT manipulation leads to unauthorized access
4. Document the complete attack flow

## False Positives

- Proper JWT validation with strong secrets
- Short-lived tokens with refresh rotation
- Multi-factor authentication enforced
- Proper session invalidation on sensitive changes

## Impact

- Account takeover
- Privilege escalation
- Data breach via unauthorized access
- Financial fraud
- Identity theft

## Pro Tips

1. Always test JWT with jwt_tool for comprehensive checks
2. Check token behavior after password/email change
3. Test OAuth flows for state parameter and redirect_uri validation
4. Look for timing differences in authentication responses
5. Test password reset from attacker-controlled email
6. Check if logout actually invalidates the session
7. Test concurrent sessions and session limits
8. Verify MFA cannot be bypassed via API
