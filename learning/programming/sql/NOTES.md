# SQL Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, client tool or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior SQL. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting, with one exception noted below: stage 6 needs a dataset that takes longer to prepare than to query.

## State

Stages 1 and 2 are written: lessons 0001 to 0013, plus four reference sheets, `null-and-three-valued-logic.md`, `select-evaluation-order.md`, `the-dataset.md` and `querying.md`. Stages 3 to 7 are unwritten.

Stage 1's six lessons use one schema, `customers` and `orders`, introduced in lesson 0001. Stage 2 added `countries` beside them and nothing else; see "The dataset, settled". Keep using it. Its nullability is deliberate: `country` is unknown-if-absent and `shipped_at` is not-yet-if-absent, which gives lesson 0003 two genuinely different meanings of `NULL` to work with, and gives later stages a foreign key and a money column to reason about.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added seven terms alongside the three pinned ones. Keep doing this per stage, and do not add a term the lessons have not earned.

## Engine policy

**Baseline, rechecked before stage 2: PostgreSQL 18.6, the current minor of the current major.** The supported majors are 14 to 18 and 13 went out of support, so a claim checked on 18 is a claim about every supported release only if it does not depend on a recent feature. Stage 2 was written and verified on 18.6. SQLite claims were checked on 3.51. Recheck both before the next stage rather than assuming these still hold, and name the version in a lesson only where the claim depends on it.

PostgreSQL is the reference engine and SQLite is the no-server alternative. Both choices are about documentation quality rather than popularity: PostgreSQL documents its planner and its concurrency model in public, and SQLite's planner is simple enough to see through.

The risk is teaching PostgreSQL and calling it SQL. Two defences, and they need applying per lesson rather than once:

- Check Modern SQL before claiming something is standard. The instinct to say "the standard requires" is usually wrong.
- Where behaviour is engine-specific, say which engine in the lesson body, not in a footnote.

## The dataset, settled

**Resolved before stage 2, and published as `reference/the-dataset.md`.** The decision was forced earlier than the original note expected: stage 2 cannot teach joins without a third table to join to, so the dataset had to exist here rather than during stage 4.

What was decided, and why each part was decided that way.

- **Generated, never downloaded**, by SQL the reader can read. A downloaded dataset dates, moves and eventually 404s, and it puts a claim in a lesson that nobody can check.
- **Deterministic, with no `random()` and no seed.** Every generated value is arithmetic on the row's own number. Verified rather than assumed: loading both scripts into an empty database twice produced byte-identical tables, checked as an `md5` over the concatenation of every row of `customers` and of `orders`. Had `setseed` been used instead, determinism would have depended on the planner's parallelism, which is not a promise worth teaching against.
- **Two sizes, one schema.** A small fixture of eight customers and twelve orders, checkable by eye, which every lesson from stage 2 quotes; and a large fixture of 100,000 customers and 1,049,916 orders, for stage 6. The large one is the small one plus generated rows, so an identifier named in a lesson means the same row in both.
- **One new table, `countries`.** Stage 1's `customers` and `orders` are untouched. The lookup table is what makes a join teachable: it holds five countries with no customers, and customer 5's code `NL` is absent from it, so an outer join has something to report and an inner join loses a customer who exists.
- **Every awkward row is deliberate** and listed in the sheet's table: a customer with no orders, two `NULL` countries, four unshipped orders, and two orders with the same amount. A dataset where everything matches teaches nothing about the cases that produce wrong answers.

The size question was settled by measurement rather than by picking a round number. On the large fixture with statistics collected, one customer's orders go from a parallel sequential scan discarding about 350,000 rows per worker to an index-only scan reading 7 rows with no heap fetches, while a predicate matching a third of the table keeps its two sequential scans and its hash join even with that index present. Both halves are the evidence: the first says the dataset is big enough to teach with, the second says it is big enough to teach honestly. Generation takes a few seconds, so it stays inside the one-sitting rule.

Skew is on purpose: about a third of customers are `US`, a sixth `GB`, an eighth each in six others, one percent have no country, and exactly one is `NL`. One column therefore holds a value too common for an index to help and a value rare enough for it to decide the plan.

## What execution changed

Stage 2's findings, all run on PostgreSQL 18.6 against the small fixture, with SQLite checks on 3.51. The harness was a local server the session started for the purpose; the scripts that build the data are published in `reference/the-dataset.md`, so a later stage can rebuild the same conditions from the workspace rather than from this file.

- **My own stage spec was wrong twice, and both were caught by an author running the query.** It told lesson 0009 that `avg(amount)` divides by 8 rather than 12 because of the `NULL`s; `amount` is `NOT NULL` and it divides by 12, so the lesson demonstrates the skipping with a three-row `VALUES` example instead and keeps the true `orders` numbers. And it labelled a set of counts as coming from `customers FULL JOIN countries` when they came from `orders FULL JOIN customers`, so `count(shipped_at)` named a column the labelled join does not have. Neither reached a published file. The lesson for the next stage: a spec fact needs the query beside it, not just the number.
- **The fan-out bug is worth the space it gets.** Joining `customers` to `orders` and then to `countries` on `region = 'Europe'` gives 36 rows and a `sum(amount)` of 7219.47 against a true 2406.49, exactly three times too big. The author also verified that the obvious repair does not work: `sum(DISTINCT amount)` gives 2396.49, wrong in the other direction, because two orders genuinely cost `10.00` and deduplication throws one away. That pair of numbers is the argument.
- **`GROUPING SETS` and `ROLLUP` produce a total row whose grouping column is `NULL`**, printing identically to the real group of customers with no country, so the output holds two blank rows meaning different things and `grouping()` is the only way to separate them. Verified, and it is why the grouping material sits in a lesson rather than in the sheet.
- **The CTE folklore is out of date and the stage says so.** On 18.6 a `WITH` referenced once is inlined and its plan is identical to the same query written as a derived table, with no `CTE` node; `MATERIALIZED` puts the fence back; and a CTE referenced twice is materialised without being asked. Lesson 0012 dates the change to PostgreSQL 12 from that release's notes, which list automatic but overridable inlining of common table expressions.
- **A subquery in `FROM` no longer needs an alias**, since PostgreSQL 16, verified by running it without one. The lessons teach writing the alias and name the version, because a reader on 14 or 15 gets a syntax error and would otherwise read it as their own mistake.
- **An error message echoes the token in the case the author wrote it.** Lesson 0013 quoted `syntax error at or near "union"` under an example written in upper case; the same query gives `"UNION"`. Found by the sheet writer, verified centrally, corrected. Quote a diagnostic from the run of the exact text the lesson prints, not from a variant.
- **`NATURAL JOIN` on this schema is a live demonstration rather than a warning.** `customers NATURAL JOIN orders` returns 0 rows, because the shared column name is `id` and no order's id equals its customer's id, and `orders NATURAL JOIN countries` degrades to a 96-row cross product because the two share no column at all. Lesson 0007's author also checked that the "Don't Do This" wiki page does **not** mention `NATURAL JOIN`, contrary to what a Going-further bullet claimed, and replaced it with the note inside the primary source, which is where the warning actually lives.

**A rendering defect class found here and now caught mechanically.** An answer that opens with the number it is answering, as in `64. Eight countries times eight customers`, is parsed as an ordered list starting at 64 and renders as a list item rather than the sentence it is. Two instances in lesson 0007 and one in lesson 0013 were fixed by writing the number as a word. The checker now flags a collapsible block whose first line opens with a number other than 1 and a full stop, since a deliberate list in an answer starts at 1; that rule found one pre-existing instance in the `finetuning` workspace, fixed with it, and no false positive across the five finished workspaces.

**On the overlap with stage 1.** Lesson 0004 already introduced the four set operations, their `ALL` variants and `EXCEPT` against `NOT EXISTS`, so lesson 0013 deliberately does not re-teach them: it supplies the verified counts on the real dataset, positional column matching, the two diagnostics, the `ORDER BY` placement rules, and the three-way comparison of the anti-join forms. A later reviser should not collapse the two lessons on the grounds that they share a subject.

## Open threads

- Resolved: the dataset. See "The dataset, settled" above, and `reference/the-dataset.md` for what a reader loads.
- Zero-downtime migration is stage 7's central skill and has no canonical source. Likely the first place the session has to do real source-finding work rather than teaching.
- `JSON` columns are placed in stage 3 as a querying feature. They are equally a schema-design decision, and if the material grows it moves to stage 4.
- Stage 7 has to read ORM output without teaching ORMs. Needs one concrete example, from a real ORM, chosen once and reused.
- Isolation-level material is where a reader's prior belief is most likely to be wrong and confidently held. Worth a retrieval prompt before teaching, rather than an explanation.
