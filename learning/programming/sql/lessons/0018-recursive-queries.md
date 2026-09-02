---
title: 18. Recursive Queries
description: A recursive CTE feeds its own output back in until nothing new comes out, which is how a hierarchy gets walked
type: lesson
---

# Lesson 18. Recursive Queries

**Mission link:** An org chart, a bill of materials, a category tree: each is a table with a column pointing at its own kind, and no fixed number of joins answers "everything under this node" when the depth is not known in advance. A recursive query walks a structure like this without knowing how deep it goes.
**Primary source:** [PostgreSQL, 7.8.2 Recursive Queries](https://www.postgresql.org/docs/current/queries-with.html)
**Prerequisites:** [Lesson 12](0012-common-table-expressions.md), [Lesson 13](0013-set-operations.md)

## Warm-up

1. ▢ Lesson 13 established that `UNION` discards a row that duplicates one already produced, while `UNION ALL` keeps every row exactly as many times as it was produced. Which of the two could, on its own, bring an otherwise endless repetition to a stop, and why?

<details markdown="1"><summary>Check</summary>

`UNION`. If the values a repeating step produces eventually come back around to one already seen, `UNION` throws that repeat away, and once a step produces nothing new there is nothing left to feed the next step, so it ends. `UNION ALL` keeps every row regardless, so the same repeating step never runs out of rows to add on its own; something else has to stop it.

</details>

## Know this

### The shape: an anchor, a UNION, and a term that names itself

A recursive `WITH` has three parts in a fixed order: a non-recursive term that fixes the starting rows, `UNION` or `UNION ALL`, and a recursive term, the only one allowed to mention the CTE's own name. Lesson 12 already named the whole construct `WITH RECURSIVE`; this lesson calls the first part the anchor term, since that is what it does.

```sql
WITH RECURSIVE countdown(n) AS (
    SELECT 5
    UNION ALL
    SELECT n - 1 FROM countdown WHERE n > 1
)
SELECT n FROM countdown;
```

```
n
-
5
4
3
2
1
```

The manual describes the evaluation as a working table. The anchor term runs once; its rows go into the result and seed that table. Then, as long as the working table holds anything, the recursive term runs again, not against everything produced so far, only against the rows the previous round produced. Whatever it returns replaces the working table for the next round and joins the result. The moment a round produces no rows, the table is empty and the whole thing stops. `countdown` ran the recursive term five times: `n = 5` produced `4`, `4` produced `3`, and so on until the round working from `n = 1` found `n > 1` false and produced nothing, which is why the query stopped rather than being told to.

### Termination is your job, not the engine's

Nothing in PostgreSQL checks that a recursive term will eventually stop. Write one with no condition that ever fails and it produces rows forever, and running that without a limit is not something to try to see what happens.

```sql
WITH RECURSIVE counter(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM counter
)
SELECT n FROM counter LIMIT 5;
```

```
n
-
1
2
3
4
5
```

It returns, and it is worth knowing precisely why. PostgreSQL evaluates a `WITH RECURSIVE` query lazily, producing one round only as the outer query asks for more, so `LIMIT 5` stops asking once five rows exist and the recursion never reaches a sixth round. That is a way to inspect a query you are not yet sure of, not a substitute for a real stopping condition: sort the same query, or join its result to another table, and the outer query typically has to pull everything first, so the `LIMIT` stops helping.

Two things actually make a recursive term stop on its own. The first is a condition on a column that changes every round, most often a depth counter carried alongside the real data: `WHERE depth < 5` guarantees at most five rounds however the data is shaped. The second is deduplication itself: `UNION` discards a row that repeats one already produced, and if the values a step can produce are drawn from a finite set, the recursion eventually has nothing new left to offer.

```sql
WITH RECURSIVE dedup(n) AS (
    SELECT 1
    UNION
    SELECT (n + 1) % 3 FROM dedup
)
SELECT n FROM dedup;
```

```
n
-
1
2
0
```

Three rows, one each of `0`, `1` and `2`, in an order the query does not fix. `1` produces `2`, `2` produces `0`, `0` produces `1` again, and that `1` is a repeat `UNION` throws away, so the next round produces nothing. The same query with `UNION ALL` never stops, since keeping every repeat is the whole difference `UNION ALL` makes, and here that difference is all that stands between a query and an infinite one.

### Walking a hierarchy

This is the reason the feature exists, and the three tables in this workspace's dataset have no hierarchy in any of them, so a small table earns its place here:

```sql
CREATE TABLE parts (
    id     bigint PRIMARY KEY,
    name   text NOT NULL,
    parent bigint REFERENCES parts (id)
);

INSERT INTO parts (id, name, parent) VALUES
    (1, 'bike',  NULL),
    (2, 'wheel', 1),
    (3, 'frame', 1),
    (4, 'spoke', 2),
    (5, 'tube',  2),
    (6, 'valve', 5);
```

Walking down from the root, joining the recursive term's `parts` to the previous round's rows on `parent`, and tracking a depth as we go:

```sql
WITH RECURSIVE descend(id, name, depth) AS (
    SELECT id, name, 1
    FROM parts
    WHERE parent IS NULL
    UNION ALL
    SELECT p.id, p.name, d.depth + 1
    FROM parts p
    JOIN descend d ON p.parent = d.id
)
SELECT id, name, depth FROM descend ORDER BY depth, id;
```

```
id | name  | depth
---+-------+------
1  | bike  | 1
2  | wheel | 2
3  | frame | 2
4  | spoke | 3
5  | tube  | 3
6  | valve | 4
```

Walking up from a leaf reverses which side of `parent` the join uses:

```sql
WITH RECURSIVE ascend(id, name, parent) AS (
    SELECT id, name, parent FROM parts WHERE id = 6
    UNION ALL
    SELECT p.id, p.name, p.parent
    FROM parts p
    JOIN ascend a ON p.id = a.parent
)
SELECT id, name FROM ascend;
```

```
id | name
---+------
6  | valve
5  | tube
2  | wheel
1  | bike
```

A path column earns its keep the same way, built by concatenating the current row's name onto the previous round's path as the recursion descends:

```sql
WITH RECURSIVE descend(id, name, path) AS (
    SELECT id, name, name FROM parts WHERE parent IS NULL
    UNION ALL
    SELECT p.id, p.name, d.path || ' > ' || p.name
    FROM parts p
    JOIN descend d ON p.parent = d.id
)
SELECT id, path FROM descend ORDER BY id;
```

```
id | path
---+----------------------------
1  | bike
2  | bike > wheel
3  | bike > frame
4  | bike > wheel > spoke
5  | bike > wheel > tube
6  | bike > wheel > tube > valve
```

A path is worth carrying for two reasons: it makes the route from the root to a row visible without a second query, and it is the raw material a cycle check needs, since a cycle is exactly a row appearing on its own path.

### Cycles, and what PostgreSQL gives you

Add two rows that point at each other and the plain query above would walk back and forth forever, since a parent-child join has no way to notice it has been here before. Bounding it with a `LIMIT` makes the loop visible instead of merely theoretical:

```sql
INSERT INTO parts (id, name, parent) VALUES (7, 'left-bracket', 8), (8, 'right-bracket', 7);
```

```sql
WITH RECURSIVE descend(id, name, path) AS (
    SELECT id, name, name FROM parts WHERE id = 7
    UNION ALL
    SELECT p.id, p.name, d.path || ' > ' || p.name
    FROM parts p
    JOIN descend d ON p.parent = d.id
)
SELECT id, path FROM descend LIMIT 4;
```

```
id | path
---+---------------------------------------------
7  | left-bracket
8  | left-bracket > right-bracket
7  | left-bracket > right-bracket > left-bracket
8  | left-bracket > right-bracket > left-bracket > right-bracket
```

The `CYCLE` clause replaces the guesswork with a real stop:

```sql
WITH RECURSIVE descend(id, name, path) AS (
    SELECT id, name, name FROM parts WHERE id = 7
    UNION ALL
    SELECT p.id, p.name, d.path || ' > ' || p.name
    FROM parts p
    JOIN descend d ON p.parent = d.id
)
CYCLE id SET is_cycle USING visited
SELECT id, name, path, is_cycle FROM descend;
```

```
id | name          | path                                        | is_cycle
---+---------------+---------------------------------------------+---------
7  | left-bracket  | left-bracket                                | f
8  | right-bracket | left-bracket > right-bracket                | f
7  | left-bracket  | left-bracket > right-bracket > left-bracket | t
```

`CYCLE id` names the column that identifies a row, `SET is_cycle` names the boolean the clause adds, and `USING visited` names the array it keeps behind the scenes to remember every `id` seen; `visited` is not part of the output unless also listed in the `SELECT`. The moment a row's `id` repeats one already in `visited`, that row is still returned, marked `is_cycle = true`, and the recursion stops there. PostgreSQL has had `CYCLE`, and the matching `SEARCH` clause for ordering, since release 14, whose release notes list "the SQL-standard `SEARCH` and `CYCLE` options for common table expressions". Before that release, the same protection was hand-written as an array column carried alongside the data and a `WHERE NOT id = ANY(visited)` test in the recursive term, excluding the repeat rather than returning it flagged.

### What belongs in the anchor, and what belongs in the recursive term

A condition in the anchor term decides which rows the walk starts from; a condition in the recursive term decides which rows the walk is allowed to add at every round after that. Confusing the two changes the answer, not just the style. Starting from `wheel` alone and walking down without restriction:

```sql
WITH RECURSIVE descend(id, name) AS (
    SELECT id, name FROM parts WHERE id = 2
    UNION ALL
    SELECT p.id, p.name FROM parts p JOIN descend d ON p.parent = d.id
)
SELECT id, name FROM descend ORDER BY id;
```

returns 4 rows: `wheel`, `spoke`, `tube`, `valve`. Starting from the real root instead, but testing `p.id = 2` inside the recursive term:

```sql
WITH RECURSIVE descend(id, name) AS (
    SELECT id, name FROM parts WHERE parent IS NULL
    UNION ALL
    SELECT p.id, p.name FROM parts p JOIN descend d ON p.parent = d.id WHERE p.id = 2
)
SELECT id, name FROM descend ORDER BY id;
```

returns only 2 rows, `bike` and `wheel`: the anchor walks from the top, but the recursive term admits a child only when that child's own `id` is `2`, so `bike`'s other child `frame` is refused outright, and once `wheel` is admitted its own children fail the same test. The same condition, tested in two different places, answers two different questions.

### It travels: SQLite has this too

SQLite supports `WITH RECURSIVE` with the same anchor, `UNION` or `UNION ALL`, recursive term shape, and its own documentation's "Recursive Common Table Expressions" section works through a hierarchy example much like this lesson's. The parts table and the descent query above run there unchanged:

```
1|bike|1
2|wheel|2
3|frame|2
4|spoke|3
5|tube|3
6|valve|4
```

SQLite has no `CYCLE` clause, so a graph that might loop needs the hand-written array check there regardless of version.

## Practice

1. ▢ Predict the rows returned by the query below.

   ```sql
   WITH RECURSIVE up(n) AS (
       SELECT 1
       UNION ALL
       SELECT n + 1 FROM up WHERE n < 4
   )
   SELECT n FROM up;
   ```

<details markdown="1"><summary>Check</summary>

`1, 2, 3, 4`. Each round adds one to the previous round's single row until a round works from `n = 4`, finds `n < 4` false, and produces nothing.

</details>

2. ▢ Predict what `WITH RECURSIVE t(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM t) SELECT n FROM t LIMIT 3` returns, given that the recursive term carries no condition that could ever stop it.

<details markdown="1"><summary>Hint</summary>

The recursive term never stops itself here; something else is doing the stopping, and it is not a safeguard to rely on outside a quick check like this one.

</details>

<details markdown="1"><summary>Check</summary>

`1, 2, 3`. The recursion runs lazily, one round per row the outer query still needs, so `LIMIT 3` stops asking after the third and a fourth round never runs. Sort the result or join it elsewhere and this stops helping, since both usually pull every row first.

</details>

3. ▢ Using the `parts` table from Know this, predict the rows returned by descending from the root with `WHERE d.depth < 2` added to the recursive term's join condition, everything else unchanged from the depth-tracking query.

   ```sql
   WITH RECURSIVE descend(id, name, depth) AS (
       SELECT id, name, 1 FROM parts WHERE parent IS NULL
       UNION ALL
       SELECT p.id, p.name, d.depth + 1
       FROM parts p JOIN descend d ON p.parent = d.id
       WHERE d.depth < 2
   )
   SELECT id, name, depth FROM descend ORDER BY depth, id;
   ```

<details markdown="1"><summary>Check</summary>

Three rows: `bike` at depth 1, `wheel` and `frame` at depth 2. The recursive term only fires again while the previous round's `depth` is under 2, so the round that would have produced `spoke` and `tube` at depth 3 never runs.

</details>

4. ▢ Predict the row count if the anchor term of the same query is changed to `WHERE id = 3` instead of `WHERE parent IS NULL`, with no other change.

<details markdown="1"><summary>Hint</summary>

Check which rows in `parts` have `parent = 3` before predicting how many rounds follow the first.

</details>

<details markdown="1"><summary>Check</summary>

One row, `frame` at depth 1. `frame` has no children, so the first recursive round finds nothing to join against and the walk never gets past the anchor.

</details>

5. ▢ `parts` also holds two rows pointing at each other, `left-bracket` (parent `right-bracket`) and `right-bracket` (parent `left-bracket`). Predict the output of walking down from `left-bracket` with a `path` column and `CYCLE id SET is_cycle USING visited`.

<details markdown="1"><summary>Check</summary>

Three rows: `left-bracket` false, `right-bracket` false, then `left-bracket` again with `is_cycle` true and path `left-bracket > right-bracket > left-bracket`. The third round would repeat `left-bracket`, `CYCLE` recognises it, returns that row flagged, and stops rather than producing a fourth.

</details>

6. ▢ The hand-written equivalent to `CYCLE` carries an array and tests `WHERE NOT id = ANY(visited)` in the recursive term. Predict what a `LIMIT 5` query over the same two cycling rows returns if that `WHERE` test is left out entirely.

<details markdown="1"><summary>Check</summary>

`left-bracket`, `right-bracket`, `left-bracket`, `right-bracket`, `left-bracket`, alternating forever with no test to refuse the repeat, and the query only stops because `LIMIT 5` stops asking for more rounds, not because the recursion found nothing left to produce.

</details>

## Real-world reps

- [ ] Find a table at work with a self-referencing column, a category tree, an org chart, a comment thread, and write a recursive query that walks it in the direction the business question actually needs, up or down.
- [ ] Take a hierarchy query someone hand-rolled with a fixed number of joins for "up to three levels deep" and replace it with a recursive `WITH` that has no depth limit built into its shape.
- [ ] Tomorrow: pick one hierarchical report you maintain and add a path column to it, then use that path to spot whether the underlying data actually contains a cycle nobody had noticed.

## Going further

- [7.8.2. Recursive Queries](https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-RECURSIVE): the working-table evaluation model, the `SEARCH` clause for ordering, and the full `CYCLE` syntax
- [PostgreSQL 14 Release Notes](https://www.postgresql.org/docs/release/14.0/): the release that added the SQL-standard `SEARCH` and `CYCLE` clauses
- [The WITH Clause](https://www.sqlite.org/lang_with.html): SQLite's own reference, with worked hierarchy and graph examples under "Recursive Common Table Expressions"
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
