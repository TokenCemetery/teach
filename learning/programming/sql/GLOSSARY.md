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

**Exclusion constraint**:
A generalisation of `UNIQUE` to any operator, which rejects a row whose values conflict with an existing row under that operator, most usefully `&&` on a range. It compares one row against the table, so it catches an overlap that no per-row `CHECK` could see.
_Avoid_: unique constraint, check constraint, index, trigger

**Fan-out**:
The row multiplication a join causes when one row on one side matches several on the other, so every additive aggregate computed afterwards is multiplied with it. A query that fans out runs without error and reports a wrong total, which is why it has to be recognised rather than debugged.
_Avoid_: cartesian product, duplicate rows, cross join, bad join

**Functional dependency**:
The relationship that lets one column's value determine another's, which a primary key has with every other column of its row. It is why grouping by a table's key permits selecting its other columns ungrouped, and why grouping by a merely unique-looking column does not.
_Avoid_: correlation, constraint, uniqueness, foreign key

**Generated column**:
A column whose value the database computes from other columns of the same row, and which nothing else may write. It is the one redundant column that cannot drift, and it cannot see another row, so a count of children is not expressible as one.
_Avoid_: default value, computed column as a synonym for a trigger, view column, cached column

**Grouping set**:
One of several groupings computed in a single pass, as `GROUPING SETS`, `ROLLUP` and `CUBE` request. A total row's grouping column is `NULL`, indistinguishable in the output from a real group of `NULL`s, and `grouping()` is what tells them apart.
_Avoid_: subtotal, pivot, rollup as a synonym, aggregate

**Index**:
A redundant, ordered structure that the planner may choose to use, and part of the physical design rather than the logical one. It can change how long a query takes and can never change which rows it returns.
_Avoid_: key, constraint, hint

**Isolation level**:
A bound on which anomalies concurrent transactions are permitted to observe. It is a statement about what may not happen, not a promise that transactions run one at a time, and two engines can implement the same named level differently.
_Avoid_: locking mode, consistency level, transaction mode

## Terms

**Aborted transaction**:
The state a transaction enters after any statement in it fails, in which every later statement is refused with `25P02` until a `ROLLBACK` or a rollback to a savepoint. Catching the error in application code does not clear it.
_Avoid_: failed statement, rolled-back transaction, deadlock, error

**Advisory lock**:
A lock taken on a number the application chooses rather than on a row or a table, held for the transaction or the session. It is the tool for serialising work that has no row to lock yet, such as deciding which of two workers creates a thing.
_Avoid_: row lock, table lock, mutex, semaphore

**Anchor term**:
The non-recursive first part of a recursive `WITH`, which fixes the rows the walk starts from. A condition belongs here when it chooses the starting point and in the recursive term when it must hold at every round, and putting it in the wrong one answers a different question rather than merely reading differently.
_Avoid_: base case, seed query, first row, initial condition

**Anti-join**:
A query that keeps the rows of one table having no match in another, written as an outer join filtered on the joined side being `NULL`, as `NOT EXISTS`, or as `EXCEPT`. Only the nullness test itself is safe after an outer join, since any other condition on the joined side discards the very rows the question is about.
_Avoid_: exclusion join, negative join, filter, `NOT IN`

**Atomicity**:
The promise that a transaction takes effect completely or not at all, so there is no half-applied state to clean up or to retry into. It says nothing about what another transaction may see while it runs.
_Avoid_: isolation, durability, consistency, locking

**Bag**:
A collection that allows duplicates, which is what a SQL table actually is. Two identical rows are two rows and no query can tell them apart, so only a constraint makes rows distinguishable.
_Avoid_: set, list, relation

**Bitmap heap scan**:
A scan that collects matching row locations from an index, sorts them by page, then visits each heap page once. It is what the planner chooses when many scattered rows match, between the extremes of one index lookup and a full sequential scan.
_Avoid_: index scan, sequential scan, index-only scan, bitmap index

**Bloat**:
Space a table or index holds that no live row occupies, left by updated and deleted row versions. A plain vacuum makes it reusable without returning it, so a table can stop growing in rows and keep growing on disk.
_Avoid_: fragmentation, table size, dead rows, disk usage

**Candidate key**:
A set of columns that is both `UNIQUE` and `NOT NULL`, and therefore identifies every row. Uniqueness alone is not enough, because a nullable unique column permits any number of NULLs.
_Avoid_: unique index, identifier, natural key

**Cardinality**:
The number of rows a step produces, which is what a selectivity fraction works out to against a given table. Not the number of distinct values in a column, which is a different quantity the planner stores separately.
_Avoid_: selectivity, distinct values, row count of the table, uniqueness

**Collation**:
The rules that decide how text compares and sorts, including case and accent handling. It is configuration rather than part of SQL, so the same query on two databases can legitimately return rows in a different order.
_Avoid_: character set, encoding, locale

**Common table expression**:
A named subquery written before the query that uses it, so a long query reads in the order its steps happen. Naming a step is what it buys; on a current PostgreSQL a single-use one is inlined, so it is not an optimisation fence unless `MATERIALIZED` asks for one.
_Avoid_: temporary table, view, optimisation fence, subquery

**Covering index**:
An index holding every column a query needs, so the query is answered without reading the table, which a plan reports as an index-only scan. Columns added with `INCLUDE` are stored in the leaves and cannot be searched or ordered by.
_Avoid_: wide index, composite key, unique index, partial index

**Cross product**:
Every row of one table paired with every row of another, with no condition to remove a pair, which `CROSS JOIN` produces and which is also what a join is before its condition applies. Also called a Cartesian product.
_Avoid_: cross join as a mistake, full join, cartesian explosion, join

**Dead row version**:
A row version left behind by an `UPDATE` or a `DELETE` once no snapshot can still need it. It occupies space until vacuum removes it, which is why a table can grow while its row count does not.
_Avoid_: duplicate row, orphaned row, deleted row, garbage

**Deadlock**:
A cycle of transactions each waiting on a lock another holds, which no amount of waiting resolves. The server detects the cycle after `deadlock_timeout` and cancels one transaction with `40P01`, and which one it picks is not something to rely on.
_Avoid_: lock wait, contention, serialization failure, timeout

**Deferred constraint check**:
A constraint whose check is postponed from the end of the statement to the end of the transaction, which `DEFERRABLE INITIALLY DEFERRED` requests and `SET CONSTRAINTS` can switch on. It is what lets two rows that reference each other be inserted at all, at the cost of a window inside the transaction where the promise does not hold.
_Avoid_: disabled constraint, `NOT VALID`, deferred trigger, `RESTRICT`

**Denormalisation**:
Keeping a second copy of a fact on purpose, for the sake of the reads that want it in one place. The question it always raises is who keeps the copies equal, and the answers range from the database itself, for a generated column, to nobody, for a plain duplicated column that needs an audit query to catch drift.
_Avoid_: optimisation, caching, redundancy as a synonym for a mistake, wide table

**Derived table**:
A subquery in `FROM`, queried like any other table, which is how a result gets grouped or filtered before the outer query sees it. It takes an alias, which every codebase writes even where a recent PostgreSQL no longer demands one.
_Avoid_: subquery, inline view, temporary table, CTE

**Evaluation order**:
The order in which a `SELECT`'s clauses actually run, which is `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`. It differs from the written order, and it is what determines which names a clause can see.
_Avoid_: execution plan, clause order, precedence

**Hash batch**:
One pass a hash join makes over its build and probe sides. More than one batch means the build side did not fit in `work_mem`, so the join wrote partitions to temporary files, which the plan shows as `Batches` above 1 with temp reads and writes.
_Avoid_: partition, chunk, bucket, spill as a synonym

**Idempotency key**:
A caller-supplied identifier sent unchanged on every retry of one logical request, stored in a unique column so a repeat is refused by the constraint rather than by a check the application forgot.
_Avoid_: primary key, request id, trace id, nonce

**Idempotent operation**:
An operation that can be run more than once without changing anything beyond its first successful run. It is a property of the caller's design, not of the database's atomicity, and it is what makes at-least-once delivery survivable.
_Avoid_: atomic, safe, retryable, transactional

**Join strategy**:
The algorithm the planner picks to combine two row sets, being a nested loop, a hash join or a merge join. It is chosen from estimated row counts rather than written in the query, which is why a wrong estimate shows up as the wrong strategy.
_Avoid_: join type, join order, inner join, plan

**Keyset pagination**:
Fetching the next page by asking for rows after the last key seen, rather than by counting rows to skip. Every page costs the same, and the key has to be unique or the order is not stable enough to page through.
_Avoid_: offset pagination, cursor, page number, seek

**Lateral subquery**:
A subquery in `FROM` marked `LATERAL`, which may reference columns of the items to its left and is evaluated once per row of them. Order in `FROM` therefore matters, since it can only see what is already to its left.
_Avoid_: derived table, correlated subquery, join, inline view

**Leftmost-prefix rule**:
A multicolumn index can only be searched from its first column inward, so an index on two columns serves a query on the first, or on both, and not one on the second alone. Skip scan relaxes this only when the leading column has few distinct values.
_Avoid_: column order as a preference, covering index, partial index, index-only scan

**Lost update**:
Two transactions read a value, each computes a new one from it, and the second write silently replaces the first. Neither transaction gets an error at Read Committed, which is what makes it the most expensive anomaly to find.
_Avoid_: non-repeatable read, write skew, deadlock, overwrite

**MVCC**:
Multiversion concurrency control: an `UPDATE` writes a new row version and marks the old one as ending rather than changing it in place, so a reader sees whichever version its snapshot admits and never waits for a writer.
_Avoid_: locking, isolation level, snapshot, versioning

**Natural join**:
A join whose condition the engine infers from every column name the two tables share. The condition is invisible in the query text and changes on its own when either table gains or loses a matching name, so it is unsafe in code that outlives the schema.
_Avoid_: inner join, `USING` join, implicit join, equijoin

**Natural key**:
A key made of data the domain already has, such as a country code or an email address, so it carries meaning and enforces uniqueness of the real thing. It moves when the domain changes its mind, and every child row referencing it moves with it.
_Avoid_: primary key, unique column, business key as a synonym for stable, composite key

**Outer join**:
A join that keeps rows from one or both sides that matched nothing, filling the absent side's columns with `NULL`. Those `NULL`s were invented by the join rather than stored, and any later condition on them behaves exactly as three-valued logic says.
_Avoid_: left join as a synonym for all three, full join, join, optional join

**Partial dependency**:
A non-key column that depends on part of a composite key rather than on the whole of it, which second normal form forbids. It cannot arise in a table whose key is a single column.
_Avoid_: transitive dependency, redundancy, denormalisation, join dependency

**Partial index**:
An index built over the subset of rows a `WHERE` clause selects, which is smaller than the full index and serves only queries whose own condition implies that clause.
_Avoid_: expression index, filtered query, covering index, unique index

**Peer**:
A row that ties with another on a window's `ORDER BY` columns. `RANGE` and `GROUPS` treat peers as one unit and `ROWS` does not, which is why one running total gives tied rows the same value and the other splits them.
_Avoid_: duplicate, tie as a synonym, equal row, neighbour

**Phantom**:
A row that appears in, or vanishes from, the result of the same predicate run twice in one transaction, because another transaction inserted or removed a matching row. The defence has to cover the predicate rather than any particular row.
_Avoid_: non-repeatable read, read skew, dirty read, ghost row

**Plan node**:
One step in the tree `EXPLAIN` prints, with its children indented beneath it and execution running from the leaves upward. Each node reports what it produced, and the line worth reading differs by node type.
_Avoid_: query, statement, operator as a synonym for a scan, buffer

**Planner cost**:
The estimate `EXPLAIN` prints in arbitrary units, comparable only between plans for the same query on the same settings. It is not a time, not a byte count, and not comparable across queries.
_Avoid_: execution time, milliseconds, buffers, price

**Read skew**:
Two different rows read once each in one transaction, each read correct on its own, and jointly describing a state that never existed, such as both sides of a transfer read either side of it.
_Avoid_: non-repeatable read, write skew, phantom, inconsistency

**Referential action**:
The `ON DELETE` or `ON UPDATE` behaviour a foreign key applies when the referenced row goes or changes: `NO ACTION`, `RESTRICT`, `CASCADE`, `SET NULL` or `SET DEFAULT`. Writing none of them does not mean no policy, it means `NO ACTION`, and `RESTRICT` differs from it only in when the check happens and in the error it raises.
_Avoid_: cascade as a synonym for all of them, trigger, constraint, default

**Referential integrity**:
The property a foreign key maintains, that every referencing value names a row that exists. It promises existence and nothing else: the row it names can still be the wrong one for the domain.
_Avoid_: correctness, consistency, cascade, constraint

**Savepoint**:
A named point inside a transaction that `ROLLBACK TO SAVEPOINT` returns to, discarding the work after it and keeping the work before it. It is not a nested transaction: nothing it did is durable until the outer transaction commits.
_Avoid_: nested transaction, checkpoint, commit, rollback

**Scalar subquery**:
A subquery returning exactly one row and one column, usable wherever a single value belongs. Nothing checks the promise at parse time, so a second row makes it fail at run time, on data rather than on syntax.
_Avoid_: correlated subquery, single-row query, aggregate, expression

**Selectivity**:
The fraction of a table's rows a condition keeps, which is what decides every choice the planner makes. It is a fraction rather than a count; the count it implies is the cardinality.
_Avoid_: cardinality, distinct values, index usefulness, filter

**Self-join**:
A table joined to itself so two of its own rows can be compared, which needs a condition to stop a row pairing with itself and another to stop each genuine pair appearing twice.
_Avoid_: recursive query, cross join, duplicate join, hierarchy query

**Semi-join**:
A test of whether a matching row exists, as `IN` and `EXISTS` perform, which returns each outer row at most once however many inner rows match. That is the difference from a join, which repeats the outer row per match and needs a `DISTINCT` or a grouping to imitate this.
_Avoid_: join, subquery, filter, inner join

**Skip scan**:
A planner strategy, added in PostgreSQL 18, that uses a multicolumn index for a query constrained only on a later column by restarting the search once per distinct leading value. The plan shows it as more than one index search on a single-row result.
_Avoid_: index scan, full index scan, leftmost-prefix rule as broken, bitmap scan

**Snapshot**:
A statement of which transactions had committed at one moment, which decides what a query sees. An isolation level is a rule about when a snapshot is taken and how long it is kept.
_Avoid_: isolation level, backup, transaction, lock

**Surrogate key**:
An identifier invented for the purpose of identifying a row, carrying no meaning of its own. It is chosen over a natural key for stability, since data that means something tends to change.
_Avoid_: auto-increment, primary key, technical key

**Three-valued logic**:
The system in which a condition evaluates to true, false or unknown, with any comparison involving `NULL` producing unknown. `WHERE` keeps only true, which is why unknown behaves like false and why a filter and its negation do not partition a table.
_Avoid_: null handling, boolean logic, tri-state

**Transaction**:
A unit of work the database applies completely or not at all, opened with `BEGIN` and closed with `COMMIT` or `ROLLBACK`. A statement sent outside one is still a transaction, of exactly one statement.
_Avoid_: session, connection, statement, batch

**Transitive dependency**:
A non-key column that depends on the key only through another non-key column, which third normal form forbids. The tell is that one fact can be updated in one row and left stale in another that shares it.
_Avoid_: partial dependency, indirect join, chained foreign key, derived column

**Unknown**:
The third truth value, produced by comparing anything with `NULL`. It is not the same as false: `NOT unknown` is still unknown, and `false AND unknown` is false while `unknown AND unknown` is not.
_Avoid_: null, false, undefined

**Visibility map**:
A per-table bitmap recording which pages hold only rows every transaction can see. It is what allows an index-only scan to skip the table entirely, so a non-zero `Heap Fetches` means some page was not yet marked.
_Avoid_: index-only scan, MVCC, vacuum, cache

**Window frame**:
The subset of the partition a window function actually reads for the current row, which is the whole partition when the window has no `ORDER BY` and `RANGE UNBOUNDED PRECEDING AND CURRENT ROW` when it has one. Every value function is only as wide as its frame.
_Avoid_: partition, window, range, subset

**Window function**:
A function computed over rows related to the current row, called with `OVER`, which leaves every row in place instead of collapsing them. It is computed after `WHERE`, `GROUP BY` and `HAVING` have finished, which is why its result cannot be filtered in the same query.
_Avoid_: aggregate, analytic function as a synonym for one, grouping, subquery

**Window partition**:
The division of rows a window's `PARTITION BY` makes, which groups them for the calculation and keeps every row in the output. It is unrelated to a table partition, which is a storage arrangement.
_Avoid_: table partition, group, shard, frame

**Working table**:
The rows the previous round of a recursive query produced, which is what the recursive term runs against. It is not the accumulated result, so a term that expects to see everything produced so far is wrong about what it is joining to.
_Avoid_: result set, accumulated rows, temporary table, CTE

**Write skew**:
Two transactions each read overlapping rows, each write a different row, and together break a rule that spans both, which no per-row constraint can see. Repeatable Read permits it; Serializable turns it into `40001`.
_Avoid_: lost update, read skew, phantom, race condition
