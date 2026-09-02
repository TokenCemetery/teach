---
title: 48. Trusted With the Database
description: Seven stages end in one habit, which is naming the row, the lock or the plan that makes a call defensible
type: lesson
---

# Lesson 48. Trusted With the Database

**Mission link:** A senior engineer's calls are trusted because they arrive with evidence anyone else can check, and that habit is this lesson's only new subject.
**Primary source:** [SQLite, Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)
**Prerequisites:** [Lesson 44](0044-reviewing-a-query.md), [Lesson 47](0047-reading-orm-output.md)

## Warm-up

1. ▢ Lesson 30 named an anomaly rather than calling a bug odd, lesson 38 named a buffer count rather than calling a query faster, and lesson 43 read `pg_constraint.convalidated` rather than trusting a constraint looked fine. Name the habit shared by all three.

<details markdown="1"><summary>Check</summary>

Each replaced a feeling with one fact someone else could check: an anomaly's name, a plan-derived count, a boolean column's actual value. A colleague who disagrees argues against that fact, not an impression, which is the difference between a defensible call and one that only sounds confident.

</details>

## Know this

### When the database is the wrong tool

Four workloads, four verdicts.

A work queue, several workers each claiming a different pending row without agreeing who gets which, stays in SQL: lesson 32's `SELECT ... FOR UPDATE SKIP LOCKED` is already the mechanism it needs.

A hierarchy or graph walk stays too, with a limit. Lesson 18's recursive `WITH` descends a tree one round per level, stopping once a round produces nothing new: bounded, no fan-out. A graph with many edges per node, or a search for the single cheapest path rather than every reachable row, is a different problem the same query still answers, wrongly.

Document data stays for genuinely variable shape, at a cost worth naming: lesson 19 admitted nothing enforces a document field is the right kind of value, since a foreign key or `NOT NULL` cannot be declared on it, exactly what lesson 21's normal forms buy back: a key, a type, a checked constraint. Move a field out once every row needs that enforced.

A stream read by many independent consumers, each at its own pace, is the one genuine case for leaving. `SKIP LOCKED` removes a claimed row from every other view; a stream needs every consumer to see every event without one's progress deleting it for another, meaning a read position per consumer, nothing deleted until the slowest has passed: a log rebuilt badly, not a queue with an index added. Apache Kafka's introduction names this directly: a topic is multi-producer and multi-subscriber, its events read as often as needed rather than consumed once, a guarantee no table was built to make.

### The four questions that decided every call in this arc

Four questions, in this order, decided nearly everything this arc built.

What rows does this return: lesson 3 explained why `NOT IN` returns nothing once a `NULL` sits in its subquery; lesson 44 made it review's first question, recovering customer 6 only once `NOT EXISTS` replaced it. Stage 1, asked first because a fast wrong answer is worse than a slow right one.

What does the plan say: lesson 35 taught a plan read leaves-up; lesson 44 applied it to `lower(email)` against a plain index on `email`, 834 buffers against 4 once an expression index existed. Stage 6, the question SQL text alone never answers.

What happens when two run at once: lesson 32 let two sessions read and write one balance and still lose a withdrawal, then closed the gap with `FOR UPDATE`. Stage 5, and skipping it is how a solo test passes while production still loses money.

What does it cost at ten times the size: lesson 44's fan-out bug returned 7219.47 against a true 2406.49 on twelve orders, and exactly three times the truth again at a million rows, 3149748 against 1049916. Unchanged shape, only cost, stage 6's discipline of a count over a feeling.

### How to explain a decision so it survives you

State the constraint that decided it, the cost accepted, and what would change your mind: three clauses, each specific enough to check.

Take this arc's `customers.id`, a generated key, over the obvious candidate, `email`. Constraint: email is the fact lesson 21 showed drifting, and the customer owns and can change it, taking every referencing row along. Cost accepted: `id` carries no meaning, so a stray row tells you nothing until joined back, and the generator behind it, lesson 22's subject, decides what else that costs. What would change my mind: a domain with few referencing tables and a key the domain cannot revise, a country's code rather than an email. The weak version, "we used a surrogate key because natural keys are usually a bad idea", names none of the three, and survives only until someone asks a second question.

### The arc, closed

Seven stages, once more by what each left you able to do. Stage 1, the relational model: say why a query returned exactly those rows, `NULL`s included. Stage 2, querying: express a question as one query without trial and error. Stage 3, beyond the basics: solve a ranking or running-total problem in SQL, not application code. Stage 4, schema design: make bad data impossible rather than discouraged. Stage 5, transactions: name the anomaly a concurrency bug depends on, before reproducing it. Stage 6, performance: optimise from a plan and prove the win with a measurement. Stage 7, this one: trusted to make the call and explain it to someone else.

The workspace's mission was to become the engineer a team trusts with its database: express a question as a query answering exactly it, read a plan to see why a query is slow, choose an index from evidence rather than instinct, reason about what concurrent transactions may observe, and design and migrate a schema that keeps bad data out and stays fast as the table grows. That mission is met by the forty-seven lessons before this one, not by this one: every verb in it names a mechanism the other stages built, and this lesson taught almost none of it, only the habit of naming the evidence.

There is no lesson 49. What comes next is not a lesson: a schema you own, a review someone is waiting on, a decision that will sometimes be wrong.

### The failure modes of the newly capable

Four new mistakes the same capability invites, each with the lesson that taught the discipline against it.

Reaching for a window function where a `GROUP BY` was clearer: lesson 20 named this choice; the discipline is asking which spelling the question asked for, not which was learned last.

Adding an index because it might help: lesson 38 concluded the best index is often the one you decide not to build, since every index costs on every write regardless of use; lesson 41 showed the result later, `idx_scan` at zero.

Insisting on Serializable everywhere: lesson 31 built the discipline this skips, naming the anomaly actually at risk before choosing what stops it, since the strongest level costs retries lesson 34 must make safe.

Blocking a migration that was safe: lesson 42's table of which `ALTER TABLE` statements rewrite and which do not is the evidence a reviewer needs, since a nullable column or a constant default takes its lock for a moment and rewrites nothing.

## Practice

1. ▢ Five systems must each read the same audit trail at their own pace, none losing a row until all five have passed it. Keep in SQL, or leave?

<details markdown="1"><summary>Check</summary>

Leave: a multi-consumer stream, not lesson 32's queue. `SKIP LOCKED` gives a row to one worker; here every system must see every row, so no read may remove one.

</details>

2. ▢ A category tree is five levels deep and, by design, can never point back to its own ancestor. Is lesson 18's recursive query the right tool, and what property of the data makes it so?

<details markdown="1"><summary>Check</summary>

Yes. Bounded depth with no cycle is what a recursive `WITH` handles cleanly: each round's working table shrinks toward nothing, and the walk stops once it runs out of children.

</details>

3. ▢ A query returns the right rows, its plan is cheap, and it never runs alongside a conflicting write. Which of this lesson's four questions is still unanswered?

<details markdown="1"><summary>Check</summary>

What it costs at ten times the size. Rows, plan and concurrency are answered; nothing says whether they still hold at ten times this table's current size.

</details>

4. ▢ A payments table stores its currency code inside a `jsonb` payload, and the payload has held three spellings of the same currency this year. Which lesson's promise did this schema give up, and what restores it?

<details markdown="1"><summary>Check</summary>

Lesson 21's promise that a fact stored once, with a key and a checked constraint, cannot drift. Restoring it means pulling `currency` into its own column with a `CHECK` or foreign key.

</details>

5. ▢ A review comment reads: "we chose a surrogate key here because natural keys are usually a bad idea." What is it missing against this lesson's three-part decision shape?

<details markdown="1"><summary>Check</summary>

No constraint this schema has, no cost it pays, nothing that would change the author's mind: a rule of thumb, not a decision anyone could contest.

</details>

6. ▢ A migration adding a nullable column with no default sits blocked in review pending a maintenance window. Which failure mode does this name, and which earlier lesson clears it?

<details markdown="1"><summary>Hint</summary>

Ask what lesson 42's filenode table says a nullable column with no default does to the table underneath it.

</details>

<details markdown="1"><summary>Check</summary>

Blocking a migration that was safe. Lesson 42 already showed a nullable `ADD COLUMN` takes its lock for a moment and rewrites nothing, so treating it like a genuine rewrite spends caution on a statement that never needed it.

</details>

## Real-world reps

- [ ] Take one recurring decision at work and write it in this lesson's three-part shape: constraint, cost accepted, what would change your mind.
- [ ] Check one workload your team runs against a relational database today against this lesson's four candidates: a queue, a hierarchy, a document, or a multi-consumer stream.
- [ ] Tomorrow: reread this workspace's mission statement and check which promises you can already keep on a real database, and which still need practice this arc cannot give you.

## Going further

- [3. Checklist For Choosing The Right Database Engine](https://www.sqlite.org/whentouse.html#checklist_for_choosing_the_right_database_engine): the primary source's checklist
- [Introduction | Apache Kafka](https://kafka.apache.org/intro): the log this lesson's leaving case cites
- [Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This): a catalogue of this lesson's failure modes
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Forty-eight lessons ago this arc started from a table with three columns and a promise that its rows would behave; it ends with you accountable for a call about a table much like it, which was the point all along.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
