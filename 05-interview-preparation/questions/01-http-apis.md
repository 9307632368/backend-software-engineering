# HTTP and REST API questions

Use these as **speaking prompts**. Try answering before reading the notes.

### Q1. What is the difference between GET, POST, PUT, PATCH and DELETE?
GET reads a resource and should not change server state. POST usually creates or triggers processing. PUT replaces a resource and is designed to be idempotent; PATCH applies a partial change and may or may not be idempotent. DELETE removes a resource and is normally idempotent in intended effect, even if response status changes on later calls.

### Q2. Is POST always non-idempotent?
No. POST has no default idempotency guarantee, but an application can implement one. The `idempotent_payments.py` example uses a client-supplied key to return the same stored result after a retry.

### Q3. When should I return 400, 401, 403, 404, 409, 422 or 429?
400: invalid request syntax or custom contract violation; 401: missing/invalid authentication; 403: authenticated but not authorised; 404: no matching resource; 409: state conflict; 422: request data fails semantic validation (common with FastAPI); 429: too many requests.

### Q4. Why is a request ID helpful?
It allows logs across a request path to be correlated. In practice, propagate a header like `X-Request-ID` through your services and return it to the client. Do not use it as a secret or authentication token.

### Q5. What makes pagination safe?
Bound `size`, validate `page`, sort deterministically, and use parameterised SQL. OFFSET is easy but becomes slower on large data. Cursor pagination is often preferable for large append-only feeds.

### Q6. Why should an API have a version?
A version helps clients adapt to breaking changes. Avoid unnecessary versions for every minor release. Document a clear deprecation plan for old endpoints.

### Q7. What is the difference between authentication and authorisation?
Authentication answers “who is this?”. Authorisation answers “can this identity perform this operation?”. A valid login is not permission to read another customer's orders.

### Q8. What should be included in an API error response?
A stable error code, safe message, and optionally a request ID or field-level errors. Avoid exposing database stack traces or sensitive internal paths.

### Small practical task
Explain why `POST /payments` may need an idempotency key. Run the first test and change the amount while reusing the same key. Predict the result before checking.
