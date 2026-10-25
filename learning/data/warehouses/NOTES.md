# Analytical Warehouses Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- No interview yet. The mission was written from the scope in issue #141, which named the arc's material (columnar storage, storage and compute separation, partitioning and clustering, dimensional modelling, loading, cost, and a judgment stage) but not the learner's reason for wanting it. The first interactive session should ask that reason and narrow the mission if the answer is narrower than "own a warehouse on any of the three platforms".
- The three-platform framing (BigQuery, Snowflake, Redshift) came from the issue, not from a learner. If the learner works on one platform only, keep the mechanism-first lessons as they are and weight practice toward that platform rather than dropping the others.

## On the arc

The eight stages and twenty lessons are public, in `README.md`. The caveat on them belongs here: the whole arc was written upfront in one change, not one lesson per interactive session, and `learning-records/` is empty. Nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- No lesson has been checked against a running warehouse. The practice items are answerable from the documentation each lesson cites, and a sandbox project on any of the three platforms (or DuckDB over a Parquet file for stages 1 and 2) is what would confirm the predict-then-run reps produce the numbers the lessons expect.
- Prices and quotas were read from each vendor's pricing page in October 2026 and quoted only as shapes (what is billed, in what unit), never as amounts a later reader would rely on. Recheck the shapes before reusing a lesson's arithmetic.
