# Subdomain Takeover Testing Guide

> Subdomain takeover occurs when a subdomain points to an external service that has been removed or is unclaimed. Attackers can claim the service and serve content on the victim's subdomain.

## Scope

- DNS CNAME records pointing to external services
- Orphaned cloud resources
- Decommissioned services
- Expired external services

## Methodology

1. Enumerate all subdomains
2. Identify CNAME records
3. Check if target service is claimable
4. Verify takeover possibility
5. Document the vulnerable configuration

## Subdomain Enumeration

### Passive Techniques
- Certificate Transparency logs
- DNS aggregators (SecurityTrails, DNSdumpster)
- Search engine dorking
- Historical DNS data

### Active Techniques
- DNS brute forcing
- Zone transfers (if allowed)
- Virtual host enumeration

### Tools
- subfinder, amass, sublist3r
- crt.sh queries
- DNS recon tools

## Vulnerable Services

### Cloud Platforms
- AWS S3 buckets
- Azure websites
- Google Cloud Storage
- Heroku apps
- GitHub Pages

### SaaS Services
- Shopify stores
- Zendesk portals
- Freshdesk instances
- Campaign Monitor
- Unbounce pages

### CDN/Hosting
- Fastly
- CloudFront
- Netlify
- Surge.sh
- Ghost.io

## Detection Indicators

### Error Messages
- "There isn't a GitHub Pages site here"
- "NoSuchBucket" (AWS S3)
- "No such app" (Heroku)
- "Domain not configured" (various)

### DNS Responses
- NXDOMAIN for target
- CNAME chain ends in error
- Service-specific error pages

## Verification Process

1. **Identify CNAME**: `dig subdomain.target.com CNAME`
2. **Check Target**: Visit the CNAME target
3. **Verify Claimable**: Check if service allows claiming
4. **Test Takeover**: Create account and claim (if authorized)

## Service-Specific Checks

### AWS S3
- Error: "The specified bucket does not exist"
- Takeover: Create bucket with same name in same region

### GitHub Pages
- Error: "There isn't a GitHub Pages site here"
- Takeover: Create repo with matching name

### Heroku
- Error: "No such app"
- Takeover: Create app with matching name

### Azure
- Error: Various 404 patterns
- Takeover: Register the subdomain in Azure

### Shopify
- Error: "Sorry, this shop is currently unavailable"
- Takeover: Register store with matching domain

## Advanced Scenarios

### NS Delegation
- Subdomain delegated to external NS
- If NS is takeable, full subdomain control
- Higher impact than CNAME takeover

### Wildcards
- Wildcard CNAME to vulnerable service
- Any subdomain under target is vulnerable

### Second-Order
- CNAME chain through multiple services
- Any link in chain being takeable

## Responsible Testing

### Do
- Document the vulnerability
- Report to asset owner
- Provide remediation steps

### Don't
- Actually take over without permission
- Serve malicious content
- Use for phishing

## Validation Requirements

1. Show the vulnerable DNS configuration
2. Demonstrate the service is claimable
3. Provide evidence (error messages, DNS records)
4. Document the potential impact

## False Positives

- Intentionally parked domains
- Active services with error pages
- Internal-only subdomains
- Services requiring verification

## Impact

- Phishing with legitimate subdomain
- Cookie theft (same-origin)
- Credential harvesting
- Malware distribution
- Brand reputation damage
- Email spoofing (if MX affected)

## Pro Tips

1. Automate subdomain monitoring
2. Check historical DNS for orphaned records
3. Focus on large organizations (more subdomains)
4. Test error messages for service identification
5. Check for NS delegation takeovers
6. Monitor certificate transparency for new subdomains
7. Verify service claimability before reporting
8. Consider second-order takeover chains
