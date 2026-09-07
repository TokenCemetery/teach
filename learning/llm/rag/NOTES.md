# RAG Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Interview recorded in #34. The outcome was not narrowed: both designing a retrieval pipeline for a given corpus and diagnosing why an existing system returns the wrong context.
- **pgvector, chosen deliberately to connect to `data/postgres`.** The learner picked the store so the two workspaces would meet, so a lesson that generalises away from pgvector loses the point of the choice.
- Generation and prompting were kept partly in rather than declared out of scope: this workspace covers how retrieved context reaches the generation step, without restating prompting as its own topic. That boundary is narrow and easy to drift across in either direction.
- Disclosed background: basic Python and familiarity with what an embedding is, no retrieval-systems experience.

## On the arc

The seven stages and their thirteen lessons are public, in `README.md`. What belongs here is the caveat on them: the arc was written upfront across successive runs, not one lesson per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early lesson and check whether the level is right, rather than assuming the written arc landed.
