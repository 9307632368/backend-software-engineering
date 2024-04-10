# 02 — Request Validation: Enrollment Preview

I wanted to see what happens when a client sends JSON that an API isn't expecting. Here, Pydantic checks the input *before* the endpoint runs.

## Implementation notes

`EnrollmentRequest` defines the shape of the incoming body: a name, course code, semester number, learning mode and credit count. For example, `semester=12` is invalid because the allowed range is **1–8**. A wrong mode is also rejected because `mode` only accepts `online` or `offline`.

The validator converts `course_code` to uppercase. `str_strip_whitespace=True` strips spaces around the student name. `extra="forbid"` makes accidentally supplied fields visible as errors instead of silently ignoring them.

The response is a **preview**, not a saved record. Its ID is not unique and must not be treated as a real enrollment identifier.

## Run

```powershell
python -m uvicorn app:app --reload
$body = @{ student_name='Ananya'; course_code='cse401'; semester=4; mode='online'; credits=4 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/enrollments/preview -ContentType application/json -Body $body
```

Try an invalid `semester` in `/docs` and inspect the **422** validation details.

## Exercises

1. Restrict `course_code` to a pattern such as three letters followed by three digits.
2. Add an optional `contact_email` field and validate its format.
3. Compare missing fields, wrong data types, and extra fields. Which produces **422**?
