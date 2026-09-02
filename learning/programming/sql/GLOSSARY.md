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

**Anchor term**:
The non-recursive first part of a recursive `WITH`, which fixes the rows the walk starts from. A condition belongs here when it chooses the starting point and in the recursive term when it must hold at every round, and putting it in the wrong one answers a different question rather than merely reading differently.
_Avoid_: base case, seed query, first row, initial condition

**Anti-join**:
A query that keeps the rows of one table having no match in another, written as an outer join filtered on the joined side being `NULL`, as `NOT EXISTS`, or as `EXCEPT`. Only the nullness test itself is safe after an outer join, since any other condition on the joined side discards the very rows the question is about.
_Avoid_: exclusion join, negative join, filter, `NOT IN`

**Bag**:
A collection that allows duplicates, which is what a SQL table actually is. Two identical rows are two rows and no query can tell them apart, so only a constraint makes rows distinguishable.
_Avoid_: set, list, relation

**Candidate key**:
A set of columns that is both `UNIQUE` and `NOT NULL`, and therefore identifies every row. Uniqueness alone is not enough, because a nullable unique column permits any number of NULLs.
_Avoid_: unique index, identifier, natural key

**Collation**:
The rules that decide how text compares and sorts, including case and accent handling. It is configuration rather than part of SQL, so the same query on two databases can legitimately return rows in a different order.
_Avoid_: character set, encoding, locale

**Common table expression**:
A named subquery written before the query that uses it, so a long query reads in the order its steps happen. Naming a step is what it buys; on a current PostgreSQL a single-use one is inlined, so it is not an optimisation fence unless `MATERIALIZED` asks for one.
_Avoid_: temporary table, view, optimisation fence, subquery

**Cross product**:
Every row of one table paired with every row of another, with no condition to remove a pair, which `CROSS JOIN` produces and which is also what a join is before its condition applies. Also called a Cartesian product.
_Avoid_: cross join as a mistake, full join, cartesian explosion, join

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

**Lateral subquery**:
A subquery in `FROM` marked `LATERAL`, which may reference columns of the items to its left and is evaluated once per row of them. Order in `FROM` therefore matters, since it can only see what is already to its left.
_Avoid_: derived table, correlated subquery, join, inline view

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

**Peer**:
A row that ties with another on a window's `ORDER BY` columns. `RANGE` and `GROUPS` treat peers as one unit and `ROWS` does not, which is why one running total gives tied rows the same value and the other splits them.
_Avoid_: duplicate, tie as a synonym, equal row, neighbour

**Referential action**:
The `ON DELETE` or `ON UPDATE` behaviour a foreign key applies when the referenced row goes or changes: `NO ACTION`, `RESTRICT`, `CASCADE`, `SET NULL` or `SET DEFAULT`. Writing none of them does not mean no policy, it means `NO ACTION`, and `RESTRICT` differs from it only in when the check happens and in the error it raises.
_Avoid_: cascade as a synonym for all of them, trigger, constraint, default

**Referential integrity**:
The property a foreign key maintains, that every referencing value names a row that exists. It promises existence and nothing else: the row it names can still be the wrong one for the domain.
_Avoid_: correctness, consistency, cascade, constraint

**Scalar subquery**:
A subquery returning exactly one row and one column, usable wherever a single value belongs. Nothing checks the promise at parse time, so a second row makes it fail at run time, on data rather than on syntax.
_Avoid_: correlated subquery, single-row query, aggregate, expression

**Self-join**:
A table joined to itself so two of its own rows can be compared, which needs a condition to stop a row pairing with itself and another to stop each genuine pair appearing twice.
_Avoid_: recursive query, cross join, duplicate join, hierarchy query

**Semi-join**:
A test of whether a matching row exists, as `IN` and `EXISTS` perform, which returns each outer row at most once however many inner rows match. That is the difference from a join, which repeats the outer row per match and needs a `DISTINCT` or a grouping to imitate this.
_Avoid_: join, subquery, filter, inner join

**Surrogate key**:
An identifier invented for the purpose of identifying a row, carrying no meaning of its own. It is chosen over a natural key for stability, since data that means something tends to change.
_Avoid_: auto-increment, primary key, technical key

**Three-valued logic**:
The system in which a condition evaluates to true, false or unknown, with any comparison involving `NULL` producing unknown. `WHERE` keeps only true, which is why unknown behaves like false and why a filter and its negation do not partition a table.
_Avoid_: null handling, boolean logic, tri-state

**Transitive dependency**:
A non-key column that depends on the key only through another non-key column, which third normal form forbids. The tell is that one fact can be updated in one row and left stale in another that shares it.
_Avoid_: partial dependency, indirect join, chained foreign key, derived column

**Unknown**:
The third truth value, produced by comparing anything with `NULL`. It is not the same as false: `NOT unknown` is still unknown, and `false AND unknown` is false while `unknown AND unknown` is not.
_Avoid_: null, false, undefined

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
