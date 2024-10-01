# Mock interview 03 — explaining a backend project

**Goal:** Explain one project accurately in 3–5 minutes. Don't claim features that have not been implemented or deployment traffic that you haven't measured.

## A simple structure

1. **Problem:** What practical issue does this project solve?
2. **My contribution:** Which part did I personally implement or modify?
3. **Architecture:** API routes, services, database, background tasks.
4. **Difficult part:** A bug or design tradeoff (e.g. retries, concurrency).
5. **Testing:** Name one test that demonstrates correctness.
6. **Limitations:** What is missing before a real production deployment?

## Example based on the practice stock service

> “This is a small FastAPI order service I used to learn transaction safety. I wanted to check what happens when several users try to order the last item. Instead of reading the count first and updating it later, I used a conditional SQL UPDATE inside a transaction. I wrote a test that sends several orders concurrently and checks that only one succeeds when one unit is available. It runs locally with SQLite. I would still need authentication, migrations, monitoring and production-database load tests before deploying it for customers.”

Only use this answer if it genuinely describes what you've built, run and understood. Change the wording to your own experience.

## Questions an interviewer may ask next

- Why FastAPI instead of another framework?
- Why did you choose SQLite for a demo?
- Where can your service fail under load?
- How would you migrate this to PostgreSQL?
- How would you add logging without exposing personal information?
- What would you do differently if you had another week?

## Personal notes to fill after practice

| Question | My answer / evidence |
|---|---|
| What I changed in the starter code | |
| Test command and result | |
| Failure case I reproduced | |
| Feature I would build next | |
| Documentation or issue I used | |
