# Kafka Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Interview recorded in #37. The outcome was not narrowed: both designing topic and partition layouts and diagnosing lag or rebalancing problems.
- **Apache Kafka only, asked for explicitly.** No Redpanda, no managed-service variants. This is the one place the interview cut scope rather than pulling it in, so do not widen the arc to alternatives for balance.
- The surrounding ecosystem, meaning Schema Registry and Kafka Connect, was kept in rather than declared out of scope, on the grounds that the log's guarantees alone do not explain how a real pipeline is built. A later session should not drop those lessons to shorten the arc.

## On the arc

The five stages and their nine lessons are public, in `README.md`. What belongs here is the caveat on them: the arc was written upfront across successive runs, not one lesson per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early lesson and check whether the level is right, rather than assuming the written arc landed.
- No lesson has been checked against a running cluster. The arc teaches partitions, consumer groups and delivery guarantees from the documentation, and a real broker is what would confirm the practice items are answerable.
