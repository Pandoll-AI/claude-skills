# Insecure File Upload Testing Guide

> File upload vulnerabilities can lead to remote code execution, stored XSS, denial of service, and data breaches. The impact depends on how uploaded files are processed and served.

## Scope

- Profile picture/avatar uploads
- Document uploads (PDF, Office)
- Bulk import functionality
- API file endpoints
- Content management systems

## Methodology

1. Identify all file upload endpoints
2. Determine allowed file types and validation
3. Test extension and content-type bypasses
4. Check where files are stored and served
5. Test for path traversal in filenames

## Extension Bypass Techniques

### Double Extensions
- `file.php.jpg`
- `file.jpg.php`
- `file.php.png`

### Case Variations
- `file.PHP`
- `file.pHp`
- `file.PhP`

### Alternative Extensions
- PHP: `.php3`, `.php4`, `.php5`, `.phtml`, `.phar`
- ASP: `.asp`, `.aspx`, `.asa`, `.cer`
- JSP: `.jsp`, `.jspx`, `.jsw`, `.jsv`

### Null Byte (Legacy)
- `file.php%00.jpg`
- `file.php\x00.jpg`

### Special Characters
- `file.php.`
- `file.php::$DATA` (Windows ADS)
- `file.php....`

## Content-Type Bypass

### Manipulation
- Change `Content-Type` header to allowed type
- Mismatch extension and content-type
- Use generic types: `application/octet-stream`

### Magic Bytes
- Add valid image header before malicious content
- GIF: `GIF89a`
- PNG: `\x89PNG\r\n\x1a\n`
- JPEG: `\xFF\xD8\xFF`

## Path Traversal

### Filename Manipulation
- `../../../var/www/html/shell.php`
- `....//....//shell.php`
- URL-encoded: `%2e%2e%2f`

### Directory Creation
- `newdir/shell.php`
- Check if directories are created

## Dangerous File Types

### Executable Code
- Web shells (PHP, ASP, JSP)
- Server-side scripts
- CGI scripts

### Client-Side
- HTML/SVG with JavaScript (XSS)
- Office documents with macros
- PDF with JavaScript

### Configuration
- `.htaccess` (Apache config)
- `web.config` (IIS config)
- `.user.ini` (PHP config)

## Storage Location Testing

### Same Origin
- Can uploaded files be accessed directly?
- Are they served with executable content-types?

### CDN/External Storage
- Files served from different domain?
- Content-Disposition headers set?
- X-Content-Type-Options: nosniff?

## Post-Upload Processing

### Image Processing
- ImageMagick vulnerabilities
- Metadata extraction issues
- Resize/convert with user input

### Document Processing
- Office macro execution
- PDF JavaScript execution
- XXE in document parsers

## Validation Requirements

1. Successfully upload restricted file type
2. Demonstrate code execution or XSS
3. Show the bypass technique used
4. Document the impact

## False Positives

- Strict allowlist validation on server-side
- Content verification (magic bytes check)
- Files served with Content-Disposition: attachment
- Separate domain for user content
- Re-encoding/sanitization of uploads

## Impact

- Remote code execution
- Stored cross-site scripting
- Denial of service (large files, zip bombs)
- Malware distribution
- Data exfiltration

## Pro Tips

1. Test every upload endpoint independently
2. Check client-side AND server-side validation
3. Try multiple bypass techniques in combination
4. Test file serving location and headers
5. Check for processing vulnerabilities
6. Test maximum file size limits
7. Look for race conditions in upload/process flow
8. Test filename length limits and special characters
