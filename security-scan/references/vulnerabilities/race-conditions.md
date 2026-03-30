# Race Condition Testing Guide

> Race conditions occur when the outcome of operations depends on the timing of events. In security contexts, they can lead to authentication bypass, double-spending, and limit bypass.

## Scope

- Financial transactions
- Coupon/voucher redemption
- Account balance operations
- Limit checks (rate limits, quotas)
- File operations
- Session management

## Methodology

1. Identify critical operations with state changes
2. Understand the check-then-act pattern
3. Send parallel requests to exploit timing window
4. Verify inconsistent state achieved
5. Document the impact

## Common Patterns

### Time-of-Check Time-of-Use (TOCTOU)
```
1. Check: Is balance >= transfer amount?
2. (Race window)
3. Use: Deduct amount from balance
```

### Double-Spending
- Send multiple withdrawal requests simultaneously
- Each checks balance before any deducts
- Result: Multiple successful withdrawals

### Limit Bypass
- Rate limit: Check count < limit
- Multiple requests before count updates
- Result: Exceed intended limit

## Attack Techniques

### Parallel Requests
- Send N identical requests simultaneously
- Use threading/async to maximize timing overlap
- Burp Intruder with parallel threads
- Custom scripts with async HTTP clients

### Single Packet Attack
- HTTP/2 multiplexing
- Multiple requests in single TCP packet
- Minimizes timing variation

### Last-Byte Sync
- Send all requests except final byte
- Release final bytes simultaneously
- Achieves tighter timing

## Target Scenarios

### Financial
- Bank transfers
- Cryptocurrency transactions
- Gift card redemption
- Refund processing
- Payment processing

### E-Commerce
- Coupon application
- Inventory reduction
- Flash sale limits
- Discount stacking

### Account Operations
- Password reset token usage
- Email verification
- Two-factor authentication
- Session invalidation

### Resource Limits
- API rate limiting
- File upload quotas
- Account creation limits
- Download restrictions

## Testing Tools

### Burp Suite
- Turbo Intruder for parallel requests
- Repeater with parallel send
- Custom extensions

### Custom Scripts
```python
import asyncio
import aiohttp

async def race_request(session, url, data):
    async with session.post(url, data=data) as response:
        return await response.text()

async def exploit():
    async with aiohttp.ClientSession() as session:
        tasks = [race_request(session, url, data) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        return results
```

## Detection Indicators

### Success Signs
- Multiple success responses
- Balance lower than expected
- Limit exceeded
- Duplicate records created

### Partial Success
- Some requests succeed, others fail
- Inconsistent error messages
- Database constraint violations

## Validation Requirements

1. Demonstrate the race condition exists
2. Show exploitable outcome (double-spend, limit bypass)
3. Prove the inconsistent state achieved
4. Document timing and technique

## False Positives

- Proper database transactions with locking
- Atomic operations
- Idempotency keys
- Request deduplication
- Distributed locks

## Impact

- Financial loss (double spending)
- Resource exhaustion
- Privilege escalation
- Data integrity compromise
- Denial of service

## Pro Tips

1. Focus on operations with state checks
2. Use HTTP/2 for tighter timing
3. Test with varying concurrency levels
4. Monitor for partial success indicators
5. Check for database constraint errors
6. Test from multiple network locations
7. Consider server-side timing variations
8. Document successful timing windows
