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

_Added as lessons establish them._
