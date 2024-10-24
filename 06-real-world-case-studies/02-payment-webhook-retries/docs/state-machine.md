# Simplified payment state machine

```text
             success event
 pending ----------------------> succeeded
    |                               |
    | failure event                 | late events ignored
    v                               v
  failed                     succeeded (no change)
```

Each accepted new event is recorded once. A matching replay gets the original stored outcome. Unknown payment IDs get `awaiting_payment` and can be retried by reconciliation. An amount mismatch is **rejected** and is never applied automatically.

**Exercise:** Add a payment audit table, then test a provider-specific rule that permits some terminal transitions. Document why it is safe before changing the implementation.
