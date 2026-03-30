# Information Disclosure Testing Guide

> Information disclosure vulnerabilities reveal sensitive data that can aid further attacks. While often low severity alone, they frequently enable or amplify other vulnerabilities.

## Scope

- Error messages and stack traces
- Debug information in responses
- Sensitive data in URLs
- Metadata and comments
- Backup and configuration files
- Directory listings

## Methodology

1. Trigger error conditions
2. Analyze response headers
3. Check for debug endpoints
4. Look for exposed files
5. Examine client-side code

## Error Messages

### Verbose Errors
- Stack traces revealing code paths
- Database error messages
- Framework/library versions
- Internal IP addresses
- File system paths

### Triggering Errors
- Invalid input types
- Missing parameters
- Malformed requests
- Out-of-range values
- Special characters

## Response Headers

### Sensitive Headers
- `Server`: Web server version
- `X-Powered-By`: Framework information
- `X-AspNet-Version`: ASP.NET version
- `X-Debug-Token`: Debug information
- Custom headers with internal data

### Missing Security Headers
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Strict-Transport-Security`
- `Content-Security-Policy`

## Debug Endpoints

### Common Paths
- `/debug`, `/debug/pprof`
- `/actuator` (Spring Boot)
- `/elmah.axd` (ASP.NET)
- `/_profiler` (Symfony)
- `/trace`, `/health`, `/metrics`

### Development Tools
- GraphQL Playground/GraphiQL
- Swagger UI with sensitive data
- phpMyAdmin, Adminer
- Redis Commander, Mongo Express

## Exposed Files

### Configuration Files
- `.env`, `.env.local`, `.env.production`
- `web.config`, `config.php`
- `database.yml`, `settings.py`
- `application.properties`

### Backup Files
- `*.bak`, `*.backup`, `*.old`
- `*.sql`, `*.dump`
- `*~`, `*.swp`
- `#*#` (Emacs)

### Version Control
- `.git/config`, `.git/HEAD`
- `.svn/entries`
- `.hg/`

### Development Files
- `package.json` (dependencies)
- `composer.json`
- `requirements.txt`
- `Gemfile`

## Client-Side Disclosure

### JavaScript Files
- API keys and secrets
- Internal API endpoints
- Business logic
- Hidden features

### HTML Comments
- Developer notes
- TODO comments
- Disabled code
- Internal references

### Source Maps
- `.map` files exposing source code
- Unminified JavaScript
- Original TypeScript/JSX

## Directory Listings

### Enabled Listings
- Apache DirectoryIndex
- Nginx autoindex
- IIS directory browsing

### Exposed Directories
- `/uploads/`, `/backup/`
- `/tmp/`, `/logs/`
- `/admin/`, `/internal/`

## Metadata Disclosure

### Document Metadata
- PDF author information
- Office document properties
- Image EXIF data
- Creation/modification dates

### API Responses
- Internal IDs exposed
- Database field names
- Timestamps revealing activity
- User enumeration via responses

## Validation Requirements

1. Document the sensitive information found
2. Explain how it aids further attacks
3. Show the disclosure source
4. Assess the severity in context

## False Positives

- Intentionally public information
- Generic error messages
- Non-sensitive metadata
- Properly sanitized debug output

## Impact

- Credential discovery
- Attack surface mapping
- Vulnerability identification
- Business intelligence exposure
- Privacy violations
- Compliance failures (GDPR, etc.)

## Pro Tips

1. Always check robots.txt for hidden paths
2. Try common backup file extensions
3. Look for version control directories
4. Analyze JavaScript for secrets
5. Check error responses thoroughly
6. Test different Accept headers
7. Look for environment-specific configs
8. Monitor response differences between environments
