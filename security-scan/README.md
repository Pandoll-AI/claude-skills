# Strix Penetration Testing Skill

**Version:** v0.1.0
**License:** Apache-2.0
**Original Project:** [usestrix/strix](https://github.com/usestrix/strix)

A Claude Code skill for AI-powered penetration testing and security assessments. This skill adapts the Strix multi-agent penetration testing framework for use with Claude Code's native capabilities.

## Overview

This skill enables Claude to perform comprehensive web application security testing by providing:

- **Browser Automation** - Playwright-based scripts for navigation, interaction, and JavaScript execution
- **HTTP Proxy Tools** - Request crafting and batch fuzzing capabilities
- **Reconnaissance** - Subdomain enumeration, technology detection, and web crawling
- **Vulnerability References** - Testing guides for OWASP Top 10 and common vulnerability classes
- **Reporting** - Structured vulnerability report generation

## Structure

```
strix-claude-skills/
├── SKILL.md              # Skill definition and methodology
├── README.md             # This file
├── scripts/
│   ├── setup.sh          # Dependency installation
│   ├── browser/          # Browser automation (5 scripts)
│   ├── proxy/            # HTTP request tools (2 scripts)
│   ├── recon/            # Reconnaissance (3 scripts)
│   └── reporting/        # Report generation (1 script)
└── references/
    ├── methodology/      # Core testing methodology
    └── vulnerabilities/  # 16 vulnerability testing guides
```

## Installation

### Project Skill (Current Location)
```bash
# Already installed at .claude/skills/strix-claude-skills/
```

### User Skill (Global)
```bash
cp -r .claude/skills/strix-claude-skills ~/.claude/skills/
```

### Dependencies
```bash
# Run the setup script
bash .claude/skills/strix/scripts/setup.sh
```

Required dependencies:
- Python 3.10+
- Playwright (`pip install playwright && playwright install chromium`)
- httpx (`pip install httpx`)
- BeautifulSoup4 (`pip install beautifulsoup4`)

## Usage

Once installed, Claude Code will automatically use this skill for penetration testing tasks. Example prompts:

```
"Perform a security assessment of https://example.com"
"Test this login form for SQL injection"
"Crawl the target and identify the attack surface"
"Check for IDOR vulnerabilities in the API"
```

## Key Differences from Original Strix

| Feature | Original Strix | This Skill |
|---------|---------------|------------|
| LLM Backend | LiteLLM (external) | Claude Code (native) |
| Execution | Docker sandbox | Local Bash tool |
| Multi-agent | Custom orchestration | Claude's reasoning |
| Browser | Playwright via agent | Standalone scripts |
| Proxy | Caido integration | httpx-based scripts |

## Vulnerability Coverage

- SQL Injection
- Cross-Site Scripting (XSS)*
- Cross-Site Request Forgery (CSRF)
- Server-Side Request Forgery (SSRF)
- XML External Entity (XXE)
- Insecure Direct Object Reference (IDOR)
- Broken Function Level Authorization (BFLA)
- Authentication & JWT Flaws
- Business Logic Vulnerabilities
- File Upload Vulnerabilities
- Mass Assignment
- Open Redirect
- Path Traversal (LFI/RFI)
- Race Conditions
- Subdomain Takeover
- Information Disclosure
- Remote Code Execution (RCE)

*XSS reference guide pending due to content restrictions

## State Management

Scripts store temporary state in:
- `/tmp/strix_browser/` - Browser session data
- `/tmp/strix_reports/` - Generated reports

## Ethical Use

This skill is intended for:
- Authorized penetration testing
- Bug bounty programs
- Security research
- Educational purposes

Always obtain proper authorization before testing any system.

## Credits

This skill is derived from [Strix](https://github.com/usestrix/strix), an open-source AI penetration testing framework by [usestrix](https://usestrix.com).

## Changelog

### v0.1.0 (2024-12-01)
- Initial release
- Converted Strix to Claude Code skill format
- 12 automation scripts (browser, proxy, recon, reporting)
- 16 vulnerability reference guides
- Core methodology documentation
