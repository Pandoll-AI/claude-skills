---
name: strix
description: Perform penetration testing and security vulnerability assessment. Use when the user asks to "pentest", "security test", "vulnerability scan", "find security vulnerabilities", "test for SQL injection", "check for XSS", "OWASP testing", "web application security assessment", or any security testing related request. Requires authorized access to target systems.
---

# Strix - Penetration Testing Skill

## Purpose

Strix is a penetration testing skill that enables Claude to conduct security assessments directly. Instead of calling external LLMs, Claude performs the security analysis using built-in tools (Bash, Read, Write, WebSearch, WebFetch) and specialized Python scripts.

## When to Use

- Authorized security testing of web applications
- Vulnerability assessment and discovery
- API security testing
- Authentication/authorization testing
- Code review for security vulnerabilities
- OWASP Top 10 vulnerability testing

**IMPORTANT**: Only use this skill when explicit authorization has been confirmed.

## Core Capabilities

### 1. Browser Automation (via Playwright scripts)
- Navigate to URLs and capture screenshots
- Interact with page elements (click, type, scroll)
- Execute JavaScript for DOM manipulation
- Extract page source and links

### 2. HTTP Requests (via httpx scripts)
- Send GET/POST/PUT/DELETE requests with custom headers
- Test API endpoints with various payloads
- Capture and analyze responses

### 3. Reconnaissance
- Subdomain enumeration
- Technology stack detection
- Web crawling and endpoint discovery

### 4. Reporting
- Generate structured vulnerability reports
- Document proof-of-concept (PoC) evidence
- Severity assessment (CVSS-based)

## Testing Methodology

### Phase 1: Reconnaissance & Mapping

**Black-box Testing** (URL/domain only):
1. Enumerate subdomains and related assets
2. Detect technology stack (frameworks, libraries)
3. Crawl and map all endpoints
4. Identify input points and attack surfaces

**White-box Testing** (source code provided):
1. Review code structure and architecture
2. Identify routes, endpoints, and handlers
3. Analyze authentication/authorization logic
4. Review input validation and sanitization

### Phase 2: Vulnerability Testing

Test for these high-impact vulnerabilities (in priority order):

1. **IDOR** - Insecure Direct Object Reference
2. **SQL Injection** - Database compromise
3. **SSRF** - Server-Side Request Forgery
4. **XSS** - Cross-Site Scripting
5. **XXE** - XML External Entity
6. **RCE** - Remote Code Execution
7. **CSRF** - Cross-Site Request Forgery
8. **Authentication Bypass** - JWT/session vulnerabilities
9. **Business Logic Flaws** - Workflow abuse
10. **Race Conditions** - TOCTOU issues

### Phase 3: Validation & Reporting

- Validate findings with concrete PoCs
- Document attack chains and impact
- Generate comprehensive vulnerability reports

## Script Usage

### Browser Scripts

```bash
# Launch browser
python scripts/browser/browser_controller.py --action launch

# Navigate to URL
python scripts/browser/navigate.py --url "https://target.com"

# Interact with page
python scripts/browser/interact.py --action click --coordinate "100,200"
python scripts/browser/interact.py --action type --text "admin"

# Execute JavaScript
python scripts/browser/execute_js.py --code "document.cookie"

# Get page source
python scripts/browser/view_source.py
```

### HTTP Request Scripts

```bash
# Send GET request
python scripts/proxy/send_request.py --method GET --url "https://api.target.com/users"

# Send POST with body
python scripts/proxy/send_request.py --method POST --url "https://api.target.com/login" \
  --body '{"username":"admin","password":"test"}' \
  --header "Content-Type: application/json"

# Test with custom headers
python scripts/proxy/send_request.py --method GET --url "https://target.com/admin" \
  --header "Authorization: Bearer <token>"
```

### Recon Scripts

```bash
# Enumerate subdomains
python scripts/recon/subdomain_enum.py --domain example.com

# Detect technology stack
python scripts/recon/tech_detect.py --url "https://target.com"

# Crawl website
python scripts/recon/crawl.py --url "https://target.com" --depth 3
```

### Reporting Scripts

```bash
# Generate vulnerability report
python scripts/reporting/vulnerability_report.py \
  --title "SQL Injection in Login Form" \
  --severity critical \
  --description "The login form is vulnerable to SQL injection..." \
  --poc "curl -X POST 'https://target.com/login' -d \"username=admin'--&password=x\"" \
  --impact "Full database access, authentication bypass" \
  --remediation "Use parameterized queries"
```

## Workflow Guidelines

1. **Use TodoWrite** to track testing progress and findings
2. **Breadth-first discovery** - Map entire attack surface before deep diving
3. **Parallel testing** where possible - Run independent tests simultaneously
4. **Evidence collection** - Always capture PoCs for validated vulnerabilities
5. **Consult references** - Check `references/vulnerabilities/` for specific techniques

## Vulnerability Reference Files

Detailed testing guides are available in `references/vulnerabilities/`:

| Vulnerability | Reference File |
|--------------|----------------|
| SQL Injection | `sql-injection.md` |
| XSS | `xss.md` |
| CSRF | `csrf.md` |
| IDOR | `idor.md` |
| SSRF | `ssrf.md` |
| XXE | `xxe.md` |
| RCE | `rce.md` |
| Auth/JWT | `authentication-jwt.md` |
| BFLA | `bfla.md` |
| Business Logic | `business-logic.md` |
| File Upload | `file-uploads.md` |
| Mass Assignment | `mass-assignment.md` |
| Open Redirect | `open-redirect.md` |
| Path Traversal | `path-traversal.md` |
| Race Conditions | `race-conditions.md` |
| Subdomain Takeover | `subdomain-takeover.md` |
| Info Disclosure | `information-disclosure.md` |

## Testing Principles

1. **Go deep** - Surface scans find nothing; real vulnerabilities are buried
2. **Be persistent** - Try multiple approaches if one fails
3. **Chain vulnerabilities** - Low-impact issues can combine for high impact
4. **Focus on impact** - One critical vulnerability > 100 informational findings
5. **Document everything** - Evidence is essential for valid reports

## Limitations

- Requires explicit authorization for testing
- Network-dependent operations may timeout
- Some WAFs may block automated testing
- Cannot test systems without network access
- Browser scripts require Playwright installation

## Setup

Before first use, run:
```bash
cd .claude/skills/strix && bash scripts/setup.sh
```

This installs required Python packages and Playwright browsers.
