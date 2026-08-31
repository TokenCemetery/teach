---
title: Glossary
description: Canonical terms for SQL
type: glossary
---

# SQL Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Unqualified "SQL" means standard SQL where the standard covers the point, and PostgreSQL where an example has to run. Any lesson relying on engine-specific behaviour says which engine.

Three terms are used loosely in ways that would make later lessons ambiguous, and each one carries a mistake that runs without complaint, so all three are pinned from the start:

**NULL**:
A marker for the absence of a value, not a value. Comparing anything to it yields unknown rather than true or false, which is why a row can fail both `= 5` and `<> 5`.
_Avoid_: empty, blank, zero, missing value

**Index**:
A redundant, ordered structure that the planner may choose to use, and part of the physical design rather than the logical one. It can change how long a query takes and can never change which rows it returns.
_Avoid_: key, constraint, hint

**Isolation level**:
A bound on which anomalies concurrent transactions are permitted to observe. It is a statement about what may not happen, not a promise that transactions run one at a time, and two engines can implement the same named level differently.
_Avoid_: locking mode, consistency level, transaction mode

## Terms

**Bag**:
A collection that allows duplicates, which is what a SQL table actually is. Two identical rows are two rows and no query can tell them apart, so only a constraint makes rows distinguishable.
_Avoid_: set, list, relation

**Candidate key**:
A set of columns that is both `UNIQUE` and `NOT NULL`, and therefore identifies every row. Uniqueness alone is not enough, because a nullable unique column permits any number of NULLs.
_Avoid_: unique index, identifier, natural key

**Collation**:
The rules that decide how text compares and sorts, including case and accent handling. It is configuration rather than part of SQL, so the same query on two databases can legitimately return rows in a different order.
_Avoid_: character set, encoding, locale

**Evaluation order**:
The order in which a `SELECT`'s clauses actually run, which is `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`. It differs from the written order, and it is what determines which names a clause can see.
_Avoid_: execution plan, clause order, precedence

**Surrogate key**:
An identifier invented for the purpose of identifying a row, carrying no meaning of its own. It is chosen over a natural key for stability, since data that means something tends to change.
_Avoid_: auto-increment, primary key, technical key

**Three-valued logic**:
The system in which a condition evaluates to true, false or unknown, with any comparison involving `NULL` producing unknown. `WHERE` keeps only true, which is why unknown behaves like false and why a filter and its negation do not partition a table.
_Avoid_: null handling, boolean logic, tri-state

**Unknown**:
The third truth value, produced by comparing anything with `NULL`. It is not the same as false: `NOT unknown` is still unknown, and `false AND unknown` is false while `unknown AND unknown` is not.
_Avoid_: null, false, undefined
