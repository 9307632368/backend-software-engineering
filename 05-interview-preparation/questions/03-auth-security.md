# Authentication and backend security questions

### Q1. Password hashing versus encryption?
Passwords should be stored using a password hashing scheme designed for passwords (such as Argon2 or bcrypt) with unique salts. Encryption is reversible and not the right default for stored passwords.

### Q2. How does JWT differ from server-side session state?
A signed JWT carries claims the server can verify without a database lookup, but revocation and rotation need additional design. A server-side session stores session state on the server and normally sends an opaque cookie identifier.

### Q3. Does a valid JWT automatically authorise access?
No. Check expiry, audience, issuer, signature/algorithm and then authorisation for the specific resource. A user can still be denied access to another user's data.

### Q4. Where should secrets be stored?
Use environment variables or an appropriate secrets manager. Never commit tokens, passwords, real webhook secrets or `.env` files to GitHub.

### Q5. Why compare HMAC signatures with `compare_digest`?
Regular string equality may leak timing information about where two strings differ. Constant-time comparison reduces that class of timing leak.

### Q6. What is replay protection for webhooks?
A malicious party or an accidental provider retry may send the same valid event again. A timestamp window plus durable processed-event IDs helps handle replays and legitimate retries.

### Q7. What is rate limiting defending against?
It reduces abuse and protects capacity. It is not a replacement for authentication, validation, account lockout policies, or upstream network protection.

### Q8. Why are parameterised SQL queries important?
They separate input data from query structure, preventing attacker-controlled values from becoming executable SQL.

### Practical follow-up
Change the webhook payload by one byte while reusing the original signature. Explain why the signature should fail, even though the event still looks like valid JSON.
