# Business Logic Vulnerability Testing Guide

> Business logic flaws exploit the intended functionality of an application in unintended ways. These vulnerabilities cannot be detected by automated scanners and require understanding of the application's business rules.

## Scope

- Workflow bypass and manipulation
- Price and quantity manipulation
- Coupon and discount abuse
- Account and privilege manipulation
- Feature abuse and misuse

## Methodology

1. Understand the business workflow thoroughly
2. Identify trust boundaries and assumptions
3. Test each step can be skipped or reordered
4. Look for race conditions in critical operations
5. Test boundary conditions and limits

## Common Vulnerability Patterns

### Workflow Bypass
- Skip verification/approval steps
- Access final step directly
- Reorder multi-step processes
- Replay completed transactions

### Price Manipulation
- Modify prices in client-side requests
- Negative quantities resulting in credits
- Currency confusion (cents vs dollars)
- Discount stacking beyond limits

### Quantity & Limit Abuse
- Integer overflow in quantities
- Bypass purchase limits
- Negative values where unexpected
- Floating point precision issues

### Coupon & Discount
- Apply expired coupons
- Stack non-stackable discounts
- Use single-use codes multiple times
- Transfer non-transferable credits

## Financial Logic

### Payment Flow
- Pay less than required amount
- Complete order without payment
- Refund more than paid
- Double-spend credits/points

### Account Balance
- Transfer to self for bonus
- Negative balance exploitation
- Race condition in withdrawals
- Currency conversion arbitrage

### Subscription
- Downgrade keeping premium features
- Cancel but maintain access
- Trial period manipulation
- Billing cycle exploitation

## Access Control Logic

### Role Manipulation
- Self-assign higher roles
- Invite with elevated privileges
- Transfer ownership without authorization
- Bypass organization boundaries

### Feature Flags
- Enable premium features
- Access beta/unreleased features
- Bypass geographic restrictions
- Unlock disabled functionality

## Race Conditions

### Time-of-Check Time-of-Use (TOCTOU)
- Double-spend in transfers
- Exceed limits with parallel requests
- Redeem single-use items multiple times

### Testing Approach
- Send parallel requests
- Use multiple sessions simultaneously
- Test during state transitions

## Validation Requirements

1. Document the intended business rule
2. Demonstrate the bypass or manipulation
3. Show the unintended outcome
4. Prove financial or security impact

## False Positives

- Edge cases handled by design
- Intentional flexibility in rules
- Low-impact cosmetic issues
- Already rate-limited or monitored

## Impact

- Financial loss to business
- Unfair advantage to attacker
- Regulatory compliance violation
- Reputation damage
- Resource exhaustion

## Pro Tips

1. Think like a fraudster - what would save money or gain advantage?
2. Test all numerical inputs for negative/zero/max values
3. Look for client-side validation only
4. Test multi-step processes out of order
5. Check if coupons/discounts validate server-side
6. Test limits with concurrent requests
7. Examine the complete user journey for shortcuts
8. Review refund and cancellation flows carefully
9. Test privilege changes during active sessions
10. Look for assumptions in documentation and comments
