# Server-Side Request Forgery (SSRF) Testing Guide

> SSRF allows attackers to make requests from the server, potentially accessing internal services, cloud metadata, and bypassing firewalls. Impact ranges from information disclosure to full system compromise.

## Scope

- URL fetching functionality
- Webhook implementations
- File imports from URLs
- PDF/image generators
- OAuth callbacks
- Cloud metadata services

## Methodology

1. Identify URL input parameters (url, link, src, dest, redirect, uri, path, file)
2. Test basic SSRF with external callback (Burp Collaborator, webhook.site)
3. Probe internal network (localhost, 127.0.0.1, internal IPs)
4. Target cloud metadata endpoints
5. Attempt protocol smuggling

## Internal Targets

### Localhost Variations
- 127.0.0.1, localhost, 127.1, 2130706433 (decimal)
- 0.0.0.0, 0, [::], [::1]
- 127.0.0.1.xip.io, localtest.me

### Internal Networks
- 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
- 169.254.169.254 (cloud metadata)
- Kubernetes: kubernetes.default, *.svc.cluster.local

### Cloud Metadata Endpoints
- **AWS**: http://169.254.169.254/latest/meta-data/
- **GCP**: http://metadata.google.internal/computeMetadata/v1/
- **Azure**: http://169.254.169.254/metadata/instance?api-version=2021-02-01
- **DigitalOcean**: http://169.254.169.254/metadata/v1/

## Bypass Techniques

### URL Parsing Tricks
- URL encoding: %31%32%37%2e%30%2e%30%2e%31
- Double encoding
- IPv6 embedding: http://[::ffff:127.0.0.1]/
- Decimal/octal IP: http://2130706433/, http://0177.0.0.1/

### DNS Rebinding
- Configure DNS to first return allowed IP, then internal IP
- Use services like rebind.network

### Redirect-Based
- Open redirect on allowed domain to internal target
- HTTP 30x redirects to internal resources
- JavaScript redirects (if rendered)

### Protocol Smuggling
- file://, gopher://, dict://, ldap://
- Data URIs for local file access
- CRLF injection for request smuggling

### Filter Bypass
- Add port: http://127.0.0.1:80@attacker.com
- Username in URL: http://attacker.com@127.0.0.1/
- Fragment: http://127.0.0.1#attacker.com
- Whitelist subdomain takeover

## Advanced Techniques

### Partial SSRF
- When only part of URL is controllable
- Path injection, query parameter injection
- Host header injection

### Blind SSRF
- No direct response visible
- Use time-based detection
- DNS-based out-of-band detection
- Error message differences

### SSRF to RCE
- Redis (SLAVEOF, CONFIG SET)
- Memcached (STAT, set commands)
- Elasticsearch (script execution)
- Internal APIs with dangerous endpoints

## Validation Requirements

1. Demonstrate server making request to attacker-controlled endpoint
2. Show access to internal resource not accessible externally
3. Prove cloud metadata or internal service data retrieval
4. Document filter bypasses used

## False Positives

- URL validation with strict allowlist
- No processing of URL response
- Network segmentation preventing internal access
- IMDSv2 on AWS (requires token)

## Impact

- Cloud credential theft (IAM roles, service accounts)
- Internal service enumeration
- Access to internal APIs and databases
- Firewall bypass for internal attacks
- Full system compromise via internal RCE

## Pro Tips

1. Always test cloud metadata endpoints first - highest impact
2. Use multiple localhost representations
3. Check if server follows redirects
4. Test both HTTP and HTTPS
5. Look for partial SSRF in path/query parameters
6. Check error messages for internal information leakage
7. Test webhook endpoints thoroughly - common SSRF source
8. IMDSv2 on AWS requires PUT request for token - test for v1 fallback
