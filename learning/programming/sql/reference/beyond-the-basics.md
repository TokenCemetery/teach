---
title: Beyond the basics
description: The window functions, the frame modes, and which tool answers which question
type: reference
---

# Beyond the basics

Lookup sheet for stage 3. The question it exists to answer: **which window function, frame or tool answers this question, and does it obey the frame?**

All counts below are against the small fixture: eight customers, twelve orders, eight countries, described in [The Dataset](the-dataset.md). The JSON table adds the four `events` rows from the same page.

## The window function vocabulary

Every function this stage taught, and the column a reader comes back for: whether it reads the frame or ignores it.

| Function | Returns | Obeys the frame |
|---|---|---|
| `sum`, `avg`, `count` as window calls | the aggregate over the current frame | yes |
| `row_number()` | 1, 2, 3... within the partition, ties broken arbitrarily | no, only the partition's `ORDER BY` decides it |
| `rank()` | ordinal position; ties share a number, the next distinct value skips ahead | no |
| `dense_rank()` | ordinal position; ties share a number, nothing is skipped | no |
| `ntile(n)` | which of `n` roughly equal buckets the row falls into | no |
| `percent_rank()` | fraction from 0 to 1, 0 on the first row | no |
| `cume_dist()` | fraction of rows at or before this one, never 0 | no |
| `lag(expr [, offset [, default]])` | a value from a row earlier in the partition | no, walks the partition by position |
| `lead(expr [, offset [, default]])` | a value from a row later in the partition | no, walks the partition by position |
| `first_value(expr)` | the value of the frame's first row | yes |
| `last_value(expr)` | the value of the frame's last row | yes |
| `nth_value(expr, n)` | the value of the frame's `n`th row | yes |

Verified on the fixture: `lag(amount, 2, '0')` gives customer 1's three orders `0, 0, 120.00`. `last_value(amount) OVER (PARTITION BY customer_id ORDER BY amount)` gives each row its own amount, not the partition's largest, because the default frame ends at the current row; widening the frame to the whole partition makes it 120.00 for customer 1 and 999.99 for customer 4. Ordered by `amount`, `percent_rank` and `cume_dist` give the first four rows `0.000, 0.000, 0.182, 0.273` and `0.167, 0.167, 0.250, 0.333`.

## The three frame modes

A frame is the subset of the partition a frame-sensitive function actually reads for the current row.

| Mode | Counts | The default (an `ORDER BY`, no explicit frame) | Runs without an `ORDER BY` |
|---|---|---|---|
| `ROWS` | physical position: exactly this many rows before or after, tied or not | never the default | yes, walks whatever physical order the partition holds |
| `RANGE` | every row whose ordering value falls inside the bound, so tied rows are always framed together | **yes**: `RANGE UNBOUNDED PRECEDING AND CURRENT ROW` | only if the bound is `UNBOUNDED`; an offset bound needs an `ORDER BY` |
| `GROUPS` | peer groups, rows sharing one ordering value counted as a single step | never the default | only if the bound is `UNBOUNDED`; an offset bound needs an `ORDER BY` |

Two restrictions a reader will hit, both re-run directly. First, a `RANGE` offset bound needs exactly one `ORDER BY` column: `sum(amount) OVER (ORDER BY amount, id RANGE BETWEEN 1 PRECEDING AND CURRENT ROW)` fails with `ERROR: RANGE with offset PRECEDING/FOLLOWING requires exactly one ORDER BY column`, SQLSTATE `42P20`, since the offset does arithmetic on the ordering value, which only means something with one subtractable column. `GROUPS` has no such limit, verified: the identical query with `GROUPS` in place of `RANGE` runs against two `ORDER BY` columns, since counting peer groups only needs equality on the whole tuple, not subtraction. Second, the tied-row behaviour: with the fixture's two `10.00` orders, the plain default gives both `20.00`, since `RANGE` frames every peer together; naming `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` instead splits them into `10.00` and `20.00`, in whichever order the tie lands. A running total with no explicit frame is a running total over peers, not over rows, and the two agree only when the ordering column never ties.

## Where a window function may run, and where it may not

Tied to [Evaluation order](select-evaluation-order.md): a window is computed after `FROM`, `WHERE`, `GROUP BY` and `HAVING` have all finished, in the same phase that builds the `SELECT` list.

| Position | Allowed |
|---|---|
| `SELECT` list | yes |
| `ORDER BY` of the same query | yes |
| `WHERE` | no, `ERROR: window functions are not allowed in WHERE`, `42P20` |
| `GROUP BY` | no, `ERROR: window functions are not allowed in GROUP BY`, `42P20` |
| `HAVING` | no, `ERROR: window functions are not allowed in HAVING`, `42P20` |
| inside another window function's own argument | no, `ERROR: window function calls cannot be nested`, `42P20` |

All four share one SQLSTATE for one reason: at the point each clause runs, the window has not been computed yet, so there is nothing for it to filter, group or nest on. Filtering on one means computing it a layer down, in a derived table or a CTE, and testing the alias from the query wrapped around it.

## LATERAL

`LATERAL` lets a subquery in `FROM` see a column from a table already named earlier in the same `FROM` clause, which an ordinary derived table cannot do. `ON true` is the idiom that goes with it: the correlation already happened inside the lateral subquery's own `WHERE`, so the join itself has nothing left to check and `ON true` just accepts whatever came back, once per outer row.

| Form | A row with nothing to join to |
|---|---|
| `JOIN LATERAL (...) ON true` | dropped, like any inner join; verified 7 rows for the largest order per customer |
| `LEFT JOIN LATERAL (...) ON true` | kept, with `NULL`s; verified 8 rows, customer 6 included |
| `CROSS JOIN LATERAL (...)` | never lost, when the subquery is an aggregate, since an aggregate always returns one row per group including a group of zero |

Order in `FROM` carries meaning here: a lateral item sees only what is already to its left, so writing it before the table it needs fails with `ERROR: missing FROM-clause entry for table "c"`, `42P01`, no `HINT`, since `c` has not been reached yet. Omitting `LATERAL` entirely fails differently: `ERROR: invalid reference to FROM-clause entry for table "c"`, `DETAIL: There is an entry for table "c", but it cannot be referenced from this part of the query.`, `HINT: To reference that table, you must mark this subquery with LATERAL.`, `42P01`.

## Recursive WITH

A recursive `WITH` has three parts, in a fixed order: an anchor term that runs once and fixes the starting rows, `UNION` or `UNION ALL`, and a recursive term, the only one of the three allowed to mention the CTE's own name.

| Part | Runs | May reference the CTE's own name |
|---|---|---|
| Anchor term | once | no |
| `UNION` / `UNION ALL` | combines every round produced so far | not applicable |
| Recursive term | once per round, as long as the previous round produced at least one row | yes, and only here |

Termination is the query's job, not the engine's: nothing checks that a recursive term will eventually stop, and one with no failing condition produces rows forever. Two things actually stop it. A condition on a column that changes every round, typically a depth counter, guarantees a bounded number of rounds: `WHERE depth < 5` at most five. Deduplication is the other: `UNION` discards a row that repeats one already produced, and if the recursive term can only ever produce values from a finite set, the round eventually has nothing new to add, verified with `WITH RECURSIVE dedup(n) AS (SELECT 1 UNION SELECT (n + 1) % 3 FROM dedup) SELECT n FROM dedup`, which returns `1, 2, 0` and stops. `LIMIT` on the outer query looks like a third way, and it does return, since PostgreSQL evaluates rounds lazily, but it only stops asking for more; sorting the result or joining it elsewhere still tends to pull every round first, so it inspects a query under construction rather than substituting for a real stopping condition. `CYCLE id SET is_cycle USING path` catches a cycle a stopping condition would miss: the moment a row's `id` repeats one already seen, that row is returned once, marked `is_cycle` true, and the recursion stops there rather than looping. PostgreSQL has had `CYCLE` since release 14; earlier, or on an engine without it, the same guard is hand-written as an array column and a `WHERE NOT id = ANY(seen)` test.

## JSON

| Operator or function | Returns |
|---|---|
| `->` | `jsonb` |
| `->>` | `text` |
| `@>` | boolean, whole fragment contained |
| `?` | boolean, key present regardless of its value |
| `jsonb_array_length(...)` | integer |
| `jsonb_array_elements(...)` | one row per array element, `jsonb`, used with `LATERAL` |
| `jsonb_path_query(doc, path)` | one row per value the path matches |
| `jsonb_path_query_array(doc, path)` | one array per document, `[]` rather than `NULL` when nothing matches |
| `jsonb_path_exists(doc, path)` | boolean |
| `JSON_TABLE(doc, path COLUMNS (...))` | one row per match, columns already typed as declared |

The one-line rule: `->` returns `jsonb` so it chains, each step handing another document to the next `->`; `->>` returns `text`, which has nothing left to descend into, so it only ever ends a chain. Verified: `pg_typeof(payload -> 'channel')` is `jsonb`, `pg_typeof(payload ->> 'channel')` is `text`; `payload -> 'items' -> 0 ->> 'sku'` gives `A1` for events 1 and 2 and `NULL` for events 3 and 4, since a missing key or an out-of-range index returns `NULL` rather than an error. `@>` matches events 1 and 4 on `{"channel": "web"}`; `?` matches event 2 alone on `coupon`.

## Which tool answers which question

The stage's centrepiece: three questions, each with two or three correct spellings, verified against the fixture.

| Question | Correct spellings | Reason to pick this one |
|---|---|---|
| Top-N per group | `row_number() OVER (PARTITION BY ... ORDER BY ...)` filtered to `rn <= n` in an outer query or CTE | keeps the rank itself, useful the moment a caller needs to know a row came second rather than first; travels to any engine with window functions |
| | `JOIN LATERAL (... ORDER BY ... LIMIT n) ON true` | stops as soon as its own `LIMIT` is satisfied rather than ranking every row in the table; extends from top-1 to top-3 by raising `LIMIT` alone; needs `LEFT JOIN LATERAL` to keep a group with nothing in it |
| Running total | `sum(amount) OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` | the only spelling that answers "the last N rows, whatever their value"; write `ROWS` explicitly the moment the ordering column can tie, since the bare default is `RANGE` and sums every peer together |
| Deduplication (one row per key) | `row_number() OVER (PARTITION BY key ORDER BY ...) ... WHERE rn = 1` | travels to any engine; hands back a rank a later step can also use |
| | `DISTINCT ON (key) ... ORDER BY key, ...` | shortest to write; PostgreSQL only; needs the `DISTINCT ON` expression to lead the `ORDER BY` or it fails with `ERROR: SELECT DISTINCT ON expressions must match initial ORDER BY expressions`, `42P10` |
| | `JOIN LATERAL (... ORDER BY ... LIMIT 1) ON true` | the one to reach for when picking the row is not just a sort, since the lateral subquery can compute or aggregate before choosing |

Verified: all three spellings of "newest order per customer" return the identical seven ids, 102, 104, 105, 107, 109, 111, 112, once the ordering breaks ties correctly with `shipped_at DESC NULLS LAST, id DESC`. Dropping `NULLS LAST` lets an unshipped order win the "newest" seat, since PostgreSQL's default for `DESC` is `NULLS FIRST`. Reading the same ranked query backwards, `rn > 1` instead of `rn = 1`, gives the five rows to delete rather than the seven to keep, and the two sets never overlap.

## The diagnostics of the stage

Every error a lesson quoted, re-run and confirmed, plus the two frame errors this sheet needed and verified directly.

| Error | SQLSTATE | Cause |
|---|---|---|
| `window functions are not allowed in WHERE` | `42P20` | `WHERE` finishes before a window is computed |
| `window functions are not allowed in HAVING` | `42P20` | `HAVING` finishes before a window is computed, the same reason |
| `window functions are not allowed in GROUP BY` | `42P20` | `GROUP BY` also finishes first |
| `window function calls cannot be nested` | `42P20` | a window consumes a frame and produces one value per row; there is no frame left for an outer window to read |
| `GROUPS mode requires an ORDER BY clause` | `42P20` | `GROUPS` needs an ordering to form peer groups from; `ROWS` alone tolerates none |
| `RANGE with offset PRECEDING/FOLLOWING requires exactly one ORDER BY column` | `42P20` | a `RANGE` offset does arithmetic on the ordering value, which needs a single, subtractable column |
| `function round(double precision, integer) does not exist` | `42883` | `percent_rank` and `cume_dist` return `double precision`; cast to `numeric` before rounding |
| `invalid reference to FROM-clause entry for table "c"` (with a `HINT` naming `LATERAL`) | `42P01` | a correlated subquery in `FROM` cannot see a sibling table without `LATERAL` |
| `missing FROM-clause entry for table "c"` | `42P01` | `LATERAL` only grants permission to look left; a lateral item written before the table it needs still cannot see it |
| `SELECT DISTINCT ON expressions must match initial ORDER BY expressions` | `42P10` | `DISTINCT ON` must be the leading term of its own `ORDER BY`, since that is how it decides which rows are peers |
| `invalid input syntax for type integer: "web"` | `22P02` | `->>` always returns text; casting a non-numeric value fails loudly rather than silently |
| `function sum(text) does not exist` | `42883` | a `JSON_TABLE` column typed `text` in its `COLUMNS` clause stays text; nothing converts it back |

## PostgreSQL and SQLite

What travels unchanged, verified directly: every ranking and aggregate window function, the `ROWS` and `RANGE` frame modes and the tie behaviour that splits them, `lag`, `lead`, `first_value`, `last_value`, `nth_value`, `ntile`, `percent_rank`, `cume_dist`, the `WINDOW` clause, `->`, `->>` and `json_extract`, and `WITH RECURSIVE` with the same anchor-union-recursive shape.

| Feature | What happens on SQLite 3.51 |
|---|---|
| `LATERAL` | not a keyword; syntax error |
| `JSON_TABLE` | function does not exist; `json_each` plays the same part in `FROM` |
| `DISTINCT ON` | not implemented; syntax error at `ON` |
| `CYCLE ... SET ... USING ...` | no such clause; a cycle needs the hand-written array guard on every release |
