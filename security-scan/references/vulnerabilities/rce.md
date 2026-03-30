# Remote Code Execution (RCE) Testing Guide

> RCE vulnerabilities allow attackers to execute arbitrary code on the server. This is the highest severity vulnerability class, often leading to complete system compromise.

## Sources

### Command Injection
- User input passed to system commands
- Shell metacharacters not sanitized
- Unsafe functions processing user input

### Deserialization
- Untrusted data passed to deserialize functions
- Gadget chains enabling code execution
- Library-specific vulnerabilities

### Template Injection
- User input evaluated in template engines
- Server-side expression evaluation
- Missing sandbox restrictions

### File Upload
- Executable files uploaded and accessed
- Web shells placed in accessible directories
- Bypassing file type restrictions

### Expression Languages
- User input in expression evaluation
- Framework-specific expression injection
- Missing input validation

## Command Injection Testing

### Identifying Injection Points
- Parameters passed to system utilities
- File operations with user-controlled names
- Network operations (ping, traceroute)
- Document processing (convert, export)

### Testing Approach
1. Identify user input reaching system commands
2. Test with benign commands (sleep, ping)
3. Use time-based detection for blind injection
4. Verify command output if visible

### Common Parameters
- Filenames, paths, IP addresses
- URLs for processing
- Format conversion options
- Report generation parameters

## Deserialization Testing

### Identifying Vulnerable Functions
- Review code for deserialize calls
- Check for serialized data in requests
- Look for known serialization formats

### Format Indicators
- Java: Base64 starting with rO0
- PHP: Serialized object strings
- Python: Pickle format
- .NET: ViewState, binary data

### Testing Approach
1. Identify serialization format
2. Research known gadget chains
3. Generate payload with appropriate tools
4. Test for execution indicators

## Template Injection Testing

### Detection
- Inject mathematical expressions
- Look for expression evaluation
- Test template syntax variations

### Framework Identification
- Error messages reveal engine
- Documentation patterns
- Response characteristics

### Testing Approach
1. Identify template engine
2. Test basic expression evaluation
3. Research engine-specific payloads
4. Verify code execution

## Validation Requirements

1. Demonstrate arbitrary code execution
2. Show the attack vector and payload
3. Prove server-side execution
4. Document the execution context

## False Positives

- Input sanitization blocking special characters
- Sandboxed execution environments
- Type-safe deserialization
- Parameterized commands

## Impact

- Complete server compromise
- Data exfiltration
- Lateral movement
- Persistent access
- Cryptocurrency mining
- Ransomware deployment

## Pro Tips

1. Test both visible and blind execution
2. Use time delays for confirmation
3. Check for outbound network access
4. Identify the execution user context
5. Review code for unsafe patterns
6. Test file upload functionality thoroughly
7. Check for known CVEs in dependencies
8. Monitor for partial execution indicators
