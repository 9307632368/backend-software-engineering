# Backend Software Engineering

This repository contains my backend development practice using **Python and FastAPI**. I made it to keep my learning in one place, from writing basic API endpoints to working on projects with authentication, databases, background jobs, and more realistic backend problems.

I have tried to focus more on implementation than just writing notes. Most topics include an `app.py` file, a short explanation, sample HTTP requests, and tests. I have also added a few bigger projects where different backend concepts work together.

The folders are arranged from fundamentals to advanced topics, so it is easier to follow them in order.

## What's inside?

| Folder | What I worked on |
| --- | --- |
| [01-fundamentals](01-fundamentals/) | HTTP, routing, validation, CRUD, SQLite, authentication, file uploads, logging and API testing |
| [02-intermediate-concepts](02-intermediate-concepts/) | Dependencies, database transactions, async operations, idempotency, webhooks and pagination |
| [03-advanced-concepts](03-advanced-concepts/) | Retries, circuit breakers, optimistic locking, outbox pattern, rate limiting, job queues and observability |
| [04-projects](04-projects/) | Three larger backend projects based on common business workflows |
| [05-interview-preparation](05-interview-preparation/) | Backend questions, hands-on problems, system design and mock interview exercises |
| [06-real-world-case-studies](06-real-world-case-studies/) | Local simulations of overselling, payment webhook retries and API traffic spikes |
| [07-resources](07-resources/) | Notes, checklists, diagrams, reusable scripts and a FastAPI starter template |

## Tech stack

- **Language:** Python (the examples mainly target Python 3.11)
- **API framework:** FastAPI, Pydantic, Uvicorn
- **Databases:** SQLite, SQLAlchemy
- **Authentication and security:** JWT, API keys, password hashing, HMAC signatures
- **Caching:** Redis in a local practice example
- **Testing:** pytest, httpx, Python `unittest`
- **Other tools:** Docker, Docker Compose, Git, VS Code REST Client

Not every project uses all of these tools. I kept most examples small enough to run locally.

## 01 - Fundamentals

I started with the things an API needs before moving to bigger projects: accepting requests, checking input, saving data, and returning useful errors.

The [tutorials](01-fundamentals/tutorials/) cover HTTP routing, request validation, error handling, in-memory CRUD, SQLite persistence, dependencies, pagination, and API-key permissions.

The [practical examples](01-fundamentals/examples/) include user registration and login, file uploads, database relationships, JWT authentication, email notification simulation, Redis caching, logging, and API testing/documentation.

Each tutorial and example has its own README and sample requests, so I can run them individually and see how they work.

## 02 - Intermediate concepts

In this section, I moved on to problems that come up when an API starts handling more than simple CRUD.

- **Tutorials:** Dependencies and settings, database transactions, async I/O, and request/response contracts.
- **Practical examples:** Idempotent checkout, webhook signature verification, and keyset pagination.
- **Mini-projects:** Support Ticket API and Inventory Order Workflow.

I also included tests for cases such as repeating a request, invalid input, and making sure updates happen safely.

[Explore intermediate implementations](02-intermediate-concepts/)

## 03 - Advanced concepts

Here I focused on what happens when backend services fail, receive duplicate work, or need to handle concurrent requests.

| Implementation | Main concept |
| --- | --- |
| [Circuit breaker and retry](03-advanced-concepts/tutorials/01-circuit-breaker-retry/) | Handling a failing dependency |
| [Optimistic locking](03-advanced-concepts/tutorials/02-optimistic-locking/) | Avoiding lost database updates |
| [Transactional outbox](03-advanced-concepts/tutorials/03-transactional-outbox/) | Recording events with database changes |
| [URL shortener](03-advanced-concepts/system-design/04-url-shortener/) | Short links, redirects and statistics |
| [Multi-tenant reporting](03-advanced-concepts/system-design/05-multi-tenant-reporting/) | Keeping different tenants' data separate |
| [Token bucket rate limiter](03-advanced-concepts/implementations/06-token-bucket-rate-limiter/) | Controlling request bursts |
| [Leased job queue](03-advanced-concepts/implementations/07-leased-job-queue/) | Worker leases, retries and failed jobs |
| [API observability](03-advanced-concepts/implementations/08-api-observability/) | Request IDs, structured logs and metrics |

These are small implementations to understand the design and trade-offs, not full distributed production systems.

## 04 - Backend projects

I wanted to build something beyond separate tutorial endpoints, so this section has three applications with multiple features and business rules.

### 1. [E-Commerce Order Service](04-projects/01-ecommerce-order-service/)

An order-management API with customer login, admin product management, stock updates, checkout, order history, cancellation and staff fulfillment.

The main part I worked on was **keeping stock and orders consistent**, especially when someone submits checkout twice. It uses database transactions, conditional stock updates and an idempotency key.

### 2. [Support Ticketing Platform](04-projects/02-support-ticketing-platform/)

A ticket-management API where customers can create and track tickets, and support staff can assign them, change their status, and add replies.

I added role and ownership checks, so customers cannot read somebody else's tickets. Internal staff notes are kept separate from public replies.

### 3. [Appointment Booking Service](04-projects/03-appointment-booking-service/)

A booking API where admins can create services and time slots, and customers can book or cancel appointments.

The main challenge here was **preventing two customers from booking the same slot**. The implementation uses a conditional database update, transactions and retry protection.

All three projects include their own application code, tests, API request examples, Dockerfile, Compose configuration and documentation. They can be run separately.

## 05 - Interview preparation

I added this folder to practise explaining backend concepts as well as writing the code.

It includes:

- Questions on HTTP, APIs, databases, authentication and related backend topics.
- Hands-on coding exercises for idempotent payments, rate limiting, stock concurrency, pagination, signed webhooks and retryable jobs.
- System-design exercises and mock interview prompts.

[Open interview preparation](05-interview-preparation/)

## 06 - Case studies

These are **simulated problems that I can reproduce locally**, not real incidents from a company.

| Case study | What I tested |
| --- | --- |
| [Flash sale overselling](06-real-world-case-studies/01-flash-sale-overselling/) | Multiple customers trying to buy limited stock at once |
| [Payment webhook retries](06-real-world-case-studies/02-payment-webhook-retries/) | Duplicate, delayed and out-of-order webhook events |
| [API traffic spike](06-real-world-case-studies/03-api-traffic-spike/) | Rate limiting and handling a sudden burst of traffic |

Each case includes code, tests and notes about design decisions and limitations.

## 07 - Resources

The [resources folder](07-resources/) has the notes and tools I use while working through the repository: HTTP and SQL cheat sheets, architecture diagrams, testing and security checklists, small utility scripts, and a [FastAPI starter template](07-resources/templates/fastapi-starter/).

## How to run the code

I mainly use **Windows PowerShell**. The examples below assume Python 3.11 is installed. Run the commands from the specified folder rather than from the repository root.

### Start with a basic API

Open PowerShell in the repository folder:

```powershell
cd 01-fundamentals/tutorials/01-http-and-routing
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi==0.115.6 uvicorn==0.32.1
python -m uvicorn app:app --reload
```

Open **http://127.0.0.1:8000/docs** to try the endpoints through Swagger UI. This tutorial also contains `requests.http` if you use the VS Code REST Client extension.

### Run a larger project

From a new PowerShell terminal at the repository root:

```powershell
cd 04-projects/01-ecommerce-order-service
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m uvicorn app.main:app --reload
```

For admin-only actions, first create an admin through the included bootstrap command:

```powershell
python -m app.bootstrap_admin
```

You can follow the same setup steps for the other two projects. Check each project's README for its workflow, environment variables and example requests.

### Run the tests

Different sections have separate test setups. After installing that section's dependencies, you can use these commands **inside the relevant folder**:

| Section | Command |
| --- | --- |
| `02-intermediate-concepts` | `python check_all.py` |
| `03-advanced-concepts` | `python check_all.py` |
| `04-projects` | `python run_checks.py` |
| `05-interview-preparation` | `python -m pytest -q` |
| `06-real-world-case-studies` | `python -m pytest -q` |
| `07-resources` | `python -m unittest discover -s tests -v` |

**Small issue to fix in the uploaded fundamentals section:** `01-fundamentals/tests/conftest.py` repeats `01-fundamentals` in the paths used to load tutorial and example apps. Change those paths to `Path(__file__).resolve().parents[1] / "tutorials"` and `Path(__file__).resolve().parents[1] / "examples"` before running its tests.

## What I want to improve next

There are still things I would like to add or improve, especially PostgreSQL migrations, better authentication flows, CI integration, proper monitoring, and load testing. Some of these topics are already demonstrated in smaller examples, but the bigger projects would need more work before they could be used in a real environment.

For now, this repository is mainly for **learning backend engineering by building and testing things myself**. The payment, email and traffic examples use local/demo data and do not connect to real customer systems.

*Note: The 2024 labels used inside some sections refer to the technology versions chosen for this learning collection, not to historical Git commit dates.*
