---
title: 46. Portability, and What It Costs
description: Most of this arc travels between engines, and the parts that do not are the parts worth depending on deliberately
type: lesson
---

# Lesson 46. Portability, and What It Costs

**Mission link:** A team that says "this is just SQL" when every statement it has run has run on one engine is asserting something nobody has checked, and the day that gets tested is a migration already underway, not a calm afternoon of research.
**Primary source:** [Modern SQL](https://modern-sql.com/)
**Prerequisites:** [Lesson 1](0001-tables-rows-and-types.md), [Lesson 19](0019-json-columns.md)

## Warm-up

1. ▢ Lesson 1 had you insert the text `'abc'` into a column declared `INTEGER` on SQLite; it succeeded, stored as text, since SQLite applies affinity rather than enforcement. Predict what a column declared `NUMERIC(12,2)` does with the value `10.005`.

<details markdown="1"><summary>Check</summary>

It keeps `10.005` exactly, unrounded. SQLite has no type with a precision and a scale, so it reads the word `NUMERIC`, ignores `(12,2)` entirely, and applies the numeric affinity, which converts to an integer or a real when it can and otherwise leaves the value as given. There was never a scale to round to.

</details>

## Know this

### The debt this lesson pays

This arc has taught PostgreSQL and, in places, called it SQL. That was a simplification, corrected here. Some of what earlier lessons taught is standard behaviour any engine implements the same way; some is a PostgreSQL feature with no equivalent elsewhere; and the only honest way to tell which, for any feature, is to run it rather than guess. There is no free canonical copy of the standard to settle it by citation, since ISO sells it by the page. [Modern SQL](https://modern-sql.com/) is the best available secondary source for what the standard says and which engines implement it, built by someone who reads it so the rest of us do not buy it, and it is named here as exactly that: secondary, not the standard itself. Everything below was run on SQLite 3.51 for this lesson, not recalled from an earlier one.

### What travels

Six kinds of query were rerun here rather than taken on trust.

| Feature | Query shape | Result |
|---|---|---|
| Window function with a frame | `sum(amt) OVER (PARTITION BY grp ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)` | Ran; the bounded frame gave a different total from an unbounded sum beside it |
| `->`, `->>`, `json_extract` | `payload -> 'channel'`, `->> 'channel'`, `json_extract(payload, '$.channel')` | Ran, `->` keeping JSON quoting and the other two stripping it |
| `FULL JOIN`, `RIGHT JOIN` | `t FULL JOIN t2 ON t.id = t2.tid`, and the same with `RIGHT` | Ran, padding the unmatched side with `NULL` |
| `WITH RECURSIVE` | `WITH RECURSIVE nums(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM nums WHERE n < 5) SELECT * FROM nums` | Ran, walking 1 to 5 |
| `FILTER` | `count(*) FILTER (WHERE amt > 10)` | Ran, counting only the filtered rows per group |
| Ordinary joins, aggregation, set operations | `t JOIN t2 ON ...`, `GROUP BY` with `sum`, plain `UNION` | Ran without anything to remark on |

That last row is the point: most of stages 2, 3 and 5 are portable, and what follows is a short exception list, not a reason to distrust the rest.

### What does not travel

The same run, against what PostgreSQL taught with nothing to match it elsewhere.

| Feature | On SQLite | Rewrite that travels |
|---|---|---|
| `GROUPING SETS`, `ROLLUP` | Syntax error at `SETS` or `WITH` | One `GROUP BY` per grouping, `UNION`ed |
| `LATERAL` | Syntax error at the correlated subquery | A window function, lesson 20's `row_number()` top-N equivalence |
| `JSON_TABLE` | Not a recognised function | None; SQLite's `json_each` is a different function, not a rewrite of this one |
| `DISTINCT ON` | Syntax error at `ON` | `row_number()` filtered to `1`, the same equivalence |
| `UNIQUE NULLS NOT DISTINCT` | Syntax error at `NULLS` | A unique index on `COALESCE(column, sentinel)` |
| Domain | Not a recognised statement | The same `CHECK` written directly on every column that would have used it |
| Exclusion constraint | Syntax error at `USING` | None; a trigger or an application lock approximates it without the same guarantee |
| Materialised view | Not a recognised statement | An ordinary table plus `CREATE TABLE ... AS SELECT`, refreshed by rerunning it |
| Identity column | Not a recognised syntax | Nothing itself portable; every engine has its own idiom, `INTEGER PRIMARY KEY` here |
| Multi-table `DROP TABLE` | Syntax error at the comma | One `DROP TABLE` statement per table |

Every row in both tables matched what this arc already expected; nothing here disagreed with it.

### The typing difference, which changes designs rather than queries

The warm-up's fact is the one difference here that is not about whether a clause parses. `numeric(12,2)` is a promise PostgreSQL enforces on every write; SQLite's affinity typing is a preference the column states and rarely enforces, so a numeric value passes through unrounded and text lands in an integer column as given. `STRICT` changes that, but less than it looks: it rejects the text-into-integer insert, with `cannot store TEXT value in INTEGER column`, but only for six base names, `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB` and `ANY`, and a `NUMERIC(12,2)` column inside a `STRICT` table fails at `CREATE TABLE` time with `unknown datatype`, since a precision and a scale are not a shape it understands. Stage 4 built its guarantees, a candidate key, a domain, a validated constraint, on the premise that the schema itself refuses bad data, and that premise is only as strong as the engine enforcing it: `numeric(12,2)` unenforced is a comment about intent, not a constraint, though `CHECK`, `NOT NULL` and `UNIQUE` held throughout, enforced separately from a column's declared type.

### Deciding to depend on something that will not travel

A compatibility list answers what happens if a statement runs elsewhere; it does not answer whether to write that statement at all, and that is a judgement. Three questions decide it: what the portable rewrite costs, in code maintained and in work the database stops doing; how likely a move to another engine genuinely is, rather than as a slogan; and what the migration would actually involve. This arc's own PostgreSQL-only features answer in opposite directions. `DISTINCT ON` costs almost nothing to make portable: the `row_number()` rewrite is one more layer round the same `ORDER BY`, the equivalence lesson 20 proved, and it runs identically either way, so the likelihood of a move stops mattering and the portable form is the sensible default regardless. An exclusion constraint answers differently: its rewrite is not a different clause but a different design, a lock or a trigger reimplementing "reject a row conflicting with any existing row under an operator" in procedural code, carrying the exact anomaly stage 4 built the constraint to remove. A team committed to PostgreSQL for its transactional guarantees is not plausibly one release from leaving over one constraint kind, and the constraint would be one of many things to reimplement if it did, not the one deciding whether the move is worth it. Here the rewrite is expensive, the move unlikely, and the migration would have bigger problems than this line, so the constraint is worth depending on deliberately.

### The dialects this arc leaves out

Three further engines are common enough to name and out of scope to teach. MySQL's own manual blocks automated fetching, so this is verified instead on MariaDB, the same family and the same grammar: its `JOIN` clause offers `INNER`, `CROSS`, `STRAIGHT_JOIN`, `LEFT OUTER` and `RIGHT OUTER`, and no `FULL` option, so a full outer join there is a `LEFT JOIN` and a `RIGHT JOIN` combined with `UNION`. SQL Server has no `LATERAL`; its documentation describes `CROSS APPLY` and `OUTER APPLY` as the operator for a table-valued expression reading columns from the table to its left, the same job under another name. Oracle's data type reference lists character, numeric, datetime, rowid and large object types and no boolean among them, so a flag column there is conventionally a `NUMBER(1)` or `CHAR(1)` with a `CHECK`, the workaround stage 1 named for any engine without one. None gets a lesson here, since each has idioms deep enough to be its own arc. What an ORM emits on top of any of these is a related, separate question, and it is next.

## Practice

1. ▢ Predict what `SELECT DISTINCT ON (grp) grp, amt FROM t ORDER BY grp, amt DESC;` does when run on SQLite.

<details markdown="1"><summary>Check</summary>

A syntax error at `ON`. `DISTINCT ON` is not part of SQLite's grammar, confirmed by running it rather than assumed from the name.

</details>

2. ▢ The same query rewritten as `row_number() OVER (PARTITION BY grp ORDER BY amt DESC)`, filtered to rank `1`. Predict whether it returns the same rows on SQLite, and say why in one sentence.

<details markdown="1"><summary>Check</summary>

Yes. Window functions travel, and this is lesson 20's equivalence for `DISTINCT ON`, so it is the same answer computed differently, not a workaround with different behaviour.

</details>

3. ▢ Predict what `CREATE TABLE t (id INTEGER PRIMARY KEY, price NUMERIC(12,2)) STRICT;` does on SQLite.

<details markdown="1"><summary>Hint</summary>

`STRICT` recognises a short list of type names. Is `NUMERIC(12,2)` on it?

</details>

<details markdown="1"><summary>Check</summary>

An error, `unknown datatype for t.price: "NUMERIC(12,2)"`, at `CREATE TABLE` time rather than `INSERT` time. `STRICT` only accepts `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB` and `ANY`, and a precision and scale are not a shape it understands, so the table is never created.

</details>

4. ▢ A team has no concrete plan to leave PostgreSQL. Say, in one sentence, whether you would rewrite an exclusion constraint into an application-enforced lock purely for engine independence.

<details markdown="1"><summary>Check</summary>

No: the rewrite reimplements in procedural code the anomaly the constraint exists to prevent, and a migration remote enough to have no plan is not a reason to pay that cost today.

</details>

5. ▢ Say, in one sentence, whether you would write `DISTINCT ON` or its `row_number()` rewrite by default, for a query with no particular reason to expect a migration.

<details markdown="1"><summary>Check</summary>

The rewrite, because it costs nothing extra and runs identically either way, which removes how likely a migration is from the decision entirely.

</details>

6. ▢ A colleague says "Modern SQL lists window functions as standard, so they must behave identically on every engine that has them." What is wrong with that, in one sentence?

<details markdown="1"><summary>Hint</summary>

What does Modern SQL actually document: the standard's text, or every engine's exact behaviour?

</details>

<details markdown="1"><summary>Check</summary>

Modern SQL documents what the standard says and which engines implement a feature at all, not that every implementation agrees on every detail; only running the query confirms behaviour, which is why this lesson reran everything on SQLite rather than citing the claim.

</details>

## Real-world reps

- [ ] Take one query in a codebase you maintain that uses `DISTINCT ON`, `LATERAL` or an exclusion constraint, and write down what the portable rewrite would cost in code and in database work.
- [ ] Pick one of lesson 19's document queries and run it against SQLite, checking whether `->` and `->>` behave the way this lesson found.
- [ ] Tomorrow: for one PostgreSQL-only feature your own schema depends on, answer this lesson's three questions and write down the verdict, not just the compatibility fact.

## Going further

- [Datatypes In SQLite](https://www.sqlite.org/datatype3.html): affinity typing in full
- [STRICT Tables](https://www.sqlite.org/stricttables.html): the opt-in that makes SQLite enforce a column's declared type
- [JOIN Syntax](https://mariadb.com/kb/en/join-syntax/): MariaDB's join grammar, and the `FULL` option it lacks, checked here since MySQL's own manual refuses automated fetches
- [FROM clause plus JOIN, APPLY, PIVOT (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/queries/from-transact-sql?view=sql-server-ver16): SQL Server's `APPLY`, used where this arc used `LATERAL`
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
