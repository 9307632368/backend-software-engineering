# Software architecture and tradeoffs

### Q1. Monolith or microservices?
A well-structured monolith is often faster to build and maintain at first. Split services when boundaries, scaling needs and team ownership justify network and operational complexity.

### Q2. How would you make a backend easier to test?
Separate HTTP handlers from business rules, pass dependencies as parameters, avoid global shared state in tests and use deterministic fixtures.

### Q3. When would you introduce a message broker?
When operations need async buffering, retry policies, decoupled consumers or independently scaled workers. It adds delivery, ordering and monitoring challenges.

### Q4. Horizontal versus vertical scaling?
Vertical scaling gives one node more resources. Horizontal scaling adds instances; shared state, load balancing and consistency become more important.

### Q5. What is eventual consistency?
Different replicas or services might briefly disagree, but converge if updates propagate and the system remains healthy. Show users appropriate pending states when consistency is not immediate.

### Q6. What is the outbox pattern?
Write a business change and an outgoing event into the same database transaction. A separate publisher sends events from the outbox. It reduces the risk of committing data without publishing the corresponding event.

### Q7. What are SLOs and SLIs?
An SLI measures service performance, e.g. request success rate. An SLO sets an explicit target, e.g. 99.9% of requests succeed over a period. Both should reflect real user experience.

### Q8. What is the right amount of abstraction?
Enough to make changes safe and code understandable, without building a large framework for an uncertain future. Explain the immediate reason you introduced each module, service or interface.

### Practical follow-up
Choose one of the six hands-on apps. Draw what changes when it must serve three API replicas and ten thousand concurrent clients. Name which existing components no longer work as-is.
