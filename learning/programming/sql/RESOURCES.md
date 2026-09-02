---
title: Resources
description: Trusted sources for SQL, each annotated with what it covers
type: resources
---

# SQL Resources

## Knowledge

- [Docs: "PostgreSQL Documentation", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/)
  The reference engine's complete manual, and the most thorough free description of how a real database behaves. Use for: the authoritative answer on anything this workspace teaches.

- [Docs: "Tutorial", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/tutorial.html)
  A guided start covering tables, queries, joins and aggregation. Use for: stage 1, and the first working queries.

- [Docs: "Queries", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/queries.html)
  Join types, grouping, and the order in which the clauses of a `SELECT` are actually evaluated. Use for: stage 2, and for why `WHERE` cannot see an alias from `SELECT`.

- [Docs: "5.5 Constraints", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/ddl-constraints.html)
  Every constraint kind with its syntax and its caveats: `CHECK`, `NOT NULL`, `UNIQUE`, primary and foreign keys with their referential actions, and exclusion constraints. Use for: stage 4, and for the exact wording of a diagnostic.

- [Docs: "Chapter 8 Data Types", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/datatype.html)
  Every type with its range, its storage and the trade it makes, including the numeric, character, date and time families the arc argues about. Use for: stages 1 and 4, whenever a column type is being chosen rather than accepted.

- [Docs: "SELECT", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/sql-select.html)
  The full syntax of one statement, clause by clause, including the grouping and set-operation forms the tutorial pages leave out. Use for: stage 2, when the question is what is legal where rather than what it means.

- [Docs: "Appendix A, Error Codes", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/errcodes-appendix.html)
  Every SQLSTATE the server can raise, grouped by class. Use for: turning a five-character code in a log line into a named condition, from stage 2 onward.

- [Docs: "Release Notes", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/release.html)
  What changed in each release, which is the only place to settle when a behaviour became true. Use for: any claim that depends on a version, and stage 2 needed it twice.

- [Docs: "Window Functions", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/tutorial-window.html)
  Partitions and frames explained with worked examples. Use for: stage 3.

- [Docs: "9.22 Window Functions", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/functions-window.html)
  Every window function with what it returns and, crucially, which of them respect the frame. Use for: stage 3, and the answer to why `last_value` returned the current row.

- [Docs: "7.8 WITH Queries", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/queries-with.html)
  Common table expressions, the recursive form with its evaluation described round by round, and the `SEARCH` and `CYCLE` options. Use for: stages 2 and 3, and for how a recursive query terminates.

- [Docs: "8.14 JSON Types" and "9.16 JSON Functions", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/datatype-json.html)
  `json` against `jsonb`, the operators, the path language and `JSON_TABLE`. Use for: stage 3, and for what a document column does not enforce.

- [Docs: "Window Functions", SQLite contributors, sqlite.org](https://www.sqlite.org/windowfunctions.html)
  The same feature in the no-server engine, including its frame syntax. Use for: checking whether a stage 3 query travels.

- [Docs: "Indexes", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/indexes.html)
  Index types, multicolumn and partial indexes, and when the planner will ignore one. Use for: stage 6, choosing an index rather than adding one.

- [Docs: "Using EXPLAIN", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/using-explain.html)
  How to read a plan, and what the estimated and actual numbers each mean. Use for: stage 6, every time.

- [Docs: "Performance Tips", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/performance-tips.html)
  Statistics, planner cost constants, and how estimation goes wrong. Use for: stage 6, when the plan is bad because the estimate was.

- [Docs: "Concurrency Control", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/mvcc.html)
  Multiversion concurrency control, lock modes and deadlocks, from the implementation. Use for: stage 5, and for what a writer does to a reader.

- [Docs: "Transaction Isolation", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/docs/current/transaction-iso.html)
  Each isolation level with the anomalies it permits and the errors it raises instead. Use for: stage 5, choosing a level on purpose.

- [Docs: "Don't Do This", PostgreSQL contributors, wiki.postgresql.org](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
  A maintained list of choices that look reasonable and are regretted, with the reason for each. Use for: stage 4 type and schema decisions, and for review vocabulary.

- [Docs: "Slow Query Questions", PostgreSQL contributors, wiki.postgresql.org](https://wiki.postgresql.org/wiki/Slow_Query_Questions)
  What information a plan diagnosis actually requires, which doubles as a checklist for doing it yourself. Use for: stage 6, structuring an investigation.

- [Book: "Use The Index, Luke", Markus Winand, use-the-index-luke.com](https://use-the-index-luke.com/)
  Free web edition on indexing and query tuning, covering PostgreSQL, MySQL, Oracle and SQL Server side by side. Use for: stage 6, and for indexing advice that is not engine-specific.

- [Book: "SQL Performance Explained", Markus Winand, sql-performance-explained.com](https://sql-performance-explained.com/)
  The print edition of the same material, organised as a book. Use for: working through indexing systematically rather than by lookup.

- [Site: "Modern SQL", Markus Winand, modern-sql.com](https://modern-sql.com/)
  What standard SQL has gained since SQL-92, feature by feature, with a table of which engines implement each. Use for: writing portable SQL, and for what the standard actually says.

- [Docs: "Query Language Understood by SQLite", SQLite contributors, sqlite.org](https://www.sqlite.org/lang.html)
  The full syntax of the second engine used here, including its deliberate divergences. Use for: reps that should need no server.

- [Docs: "Query Planning", SQLite contributors, sqlite.org](https://www.sqlite.org/queryplanner.html)
  How a deliberately simple planner uses indexes, which makes the mechanism easier to see. Use for: stage 6, before the same ideas get harder in PostgreSQL.

- [Docs: "Appropriate Uses For SQLite", SQLite contributors, sqlite.org](https://www.sqlite.org/whentouse.html)
  A candid statement of what the engine is and is not for, from its author. Use for: stage 7, and for choosing an engine honestly.

- [Book: "Designing Data-Intensive Applications", Martin Kleppmann, O'Reilly](https://dataintensive.net/)
  Chapter 7 derives the isolation anomalies from first principles, independently of any engine. Use for: stage 5 when a mental model is missing rather than a fact.

- [Paper: "A Critique of ANSI SQL Isolation Levels", Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil, Microsoft Research](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)
  Shows that the standard's levels are defined by the anomalies they forbid, and that the definitions are incomplete. Use for: stage 5, and for why two engines can both be right about "repeatable read".

- [Analyses: "Jepsen", Kyle Kingsbury, jepsen.io](https://jepsen.io/analyses)
  Published tests of what real systems actually guarantee under fault, database by database. Use for: stage 5 and stage 7, and for treating a vendor's isolation claim as a hypothesis.

## Wisdom (Communities)

- [Archive: "PostgreSQL Mailing Lists", PostgreSQL Global Development Group, postgresql.org](https://www.postgresql.org/list/)
  Decades of public archives where planner behaviour and design decisions are explained by the people who wrote them, readable without subscribing. Use for: behaviour the manual states without justifying.

## Gaps

- **Normalisation has no PostgreSQL source.** The manual documents constraints and types thoroughly and never teaches the normal forms, so stage 4 states first to third normal form and Boyce-Codd from ordinary relational theory and cites an encyclopaedia for the forms it deliberately does not teach. Any claim about a normal form in this workspace rests on a demonstration against the engine rather than on a citation.
- **The ISO SQL standard is paywalled**, so no lesson can cite it directly. Modern SQL is the substitute for what the standard requires, and it is a secondary source; a lesson that says "the standard says" is leaning on it.
- Cross-engine differences have no single reference. MySQL, Oracle and SQL Server behaviours have to be checked in their own documentation, and stage 7 portability material will need sources this list does not have.
- Zero-downtime migration has no canonical source. It is stage 7's central skill and currently rests on the concurrency and locking documentation plus engine-specific release notes.
- Reading ORM output is unsourced by design, since the arc keeps ORMs out of scope as subjects. The stage 7 lesson will need at least one worked example from a real ORM.
