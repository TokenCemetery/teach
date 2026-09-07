# Postgres Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Interview recorded in #36. Every either/or came back as both: diagnosing an existing instance's problems and designing storage, replication and index upkeep from scratch, across both self-hosted operation and a managed service.
- pgvector was kept in rather than declared out of scope, specifically for what a vector index costs the database, connecting to `llm/rag`'s choice of it. That connection was the learner's, not an editorial guess.
- This workspace opened the `data/` domain, so it also set the boundary that the SQL language itself stays with `programming/sql`.

## On the arc

The five stages and their ten lessons are public, in `README.md`. What belongs here is the caveat on them: the arc was written upfront across successive runs, not one lesson per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early lesson and check whether the level is right, rather than assuming the written arc landed.
- The pgvector material is the most version-sensitive in the workspace: update and delete behaviour on an HNSW index has genuinely changed across releases, so lesson 0008 tells the reader to check current release notes rather than trusting a fixed answer. That lesson will need rechecking sooner than the rest of the arc.
