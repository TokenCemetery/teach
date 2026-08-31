---
title: 42. Reviewing Python
description: What to look for, in what order, and how to separate a defect from a preference
type: lesson
---

# Lesson 42. Reviewing Python

**Mission link:** The mission's last success criterion is naming precisely why someone's clever use of Python is going to hurt them. That requires an order to look in, and the discipline to say which findings are defects and which are taste.
**Primary source:** [PEP 8, A Foolish Consistency](https://peps.python.org/pep-0008/)
**Prerequisites:** every earlier lesson, since this one is the arc pointed at other people's code. The two it leans on hardest are [Lesson 21](0021-lint-and-format.md), for what a tool should report instead, and [Lesson 40](0040-designing-an-api.md), for what cannot be fixed later

## Warm-up

1. ▢ Which findings should a human reviewer never spend time on?

<details markdown="1"><summary>Check</summary>

Anything a formatter or linter reports, from lesson 21. If a review comment could be a rule, it should be one.

</details>

2. ▢ Name one defect from this arc that neither a linter nor a type checker can see.

<details markdown="1"><summary>Check</summary>

Several: a shared mutable class attribute, a check-then-act race, an `await` in a loop, a session-scoped fixture that gets mutated, a discarded future, a lock held across I/O.

</details>

## Know this

### The order

Look in this order, because a finding at level one makes findings at level four irrelevant.

**1. Does it do what the change says?** Read the description, then the tests, then the code. If the tests do not describe the behaviour claimed, that is the first comment.

**2. Is there a test that would fail if the code were wrong?** Lesson 33's question. A change with tests that assert nothing is unreviewed by construction.

**3. Correctness, in Python's specific failure modes.** The list below.

**4. Interface.** Anything public, per lesson 40, is permanent. This is the level where a review is most valuable, because it is the only level where the cost of being wrong cannot be paid later.

**5. Clarity.** Naming, structure, and whether the next reader will understand it.

**6. Everything else.** Which is either automated or preference.

### The Python-specific checklist

Ordered by how much damage each does, and every one is a lesson in this arc.

| Look for | Lesson |
|---|---|
| a mutable default argument, or a mutable class attribute | 6, 22 |
| an iterator consumed twice, silently returning nothing | 8 |
| `except Exception: pass`, or a bare `except` | 10 |
| a `try` block whose second statement should not be protected | 10 |
| resource cleanup without a context manager | 11 |
| `from x import y` for something that gets patched in tests | 13, 31 |
| a naive `datetime`, or `bool(os.environ.get(...))` | 14, 18 |
| `-> X` on a function that can return `None` | 15 |
| `Any` at a boundary, and everything downstream unchecked | 16, 18 |
| a concrete `list[X]` parameter in a function that only iterates | 17 |
| `dict` passed between layers with keys the code already knows | 12, 18 |
| a `pytest.raises(Exception)` or an assertion-free test | 28, 33 |
| a fixture with a scope wider than one test that gets mutated | 29 |
| a bare `Mock` where the collaborator's shape matters | 31 |
| a discarded future from `submit` | 35 |
| a lock held across I/O | 35 |
| check-then-act on shared state, or across an `await` | 34, 37 |
| a blocking call inside `async def` | 37 |
| `await` inside a `for` loop over independent work | 37 |
| `warnings.warn` without `stacklevel` | 41 |
| a module-level client, connection or config object | 40 |
| an optimisation with no measurement | 39 |

That table is the arc's review value, and it is worth having open for the first few reviews.

### Defect, risk, or preference

Say which one, every time. It changes how the author reads the comment.

- **Defect**: it is wrong. "This returns `None` when the list is empty, and the caller indexes the result." Blocking.
- **Risk**: it is correct now and will break. "This fixture is session-scoped and the test mutates it, so the suite becomes order-dependent." Usually blocking.
- **Preference**: it would read better another way. "I would use a comprehension here." Never blocking, and worth saying only if it is genuinely clearer.

Mixing them is what makes reviews slow and resented. Ten preferences and one defect read as eleven complaints, and the defect gets lost.

### Comments that work

Say what is wrong, why it matters, and what you would do. The last part is what turns a comment into a decision.

> This holds `self._lock` across the HTTP call, so every other caller waits on this request. Moving the fetch above the `with` allows a duplicate request for the same key, which for an idempotent read is the better trade.

Not:

> Don't hold locks during I/O.

The second is correct and gives the author nothing to act on: they do not know whether you considered the duplicate fetch, so the conversation takes three rounds.

Ask when you do not know. "What happens if two requests arrive for the same key?" costs one sentence and is often how the author finds the bug themselves.

Praise the specific thing, not the change. "This boundary function is the reason the rest of the diff has no `isinstance`" tells the author what to keep doing.

### On cleverness

The mission's phrasing is "name precisely why someone's clever use of Python's dynamism is going to hurt them". Precisely is the operative word, and it means naming a consequence rather than a feeling.

| Clever thing | The precise cost |
|---|---|
| a metaclass | cannot be combined with another library's base; invisible to the reader of the subclass; tooling cannot see generated attributes |
| `__getattr__` forwarding | typos become silent; a checker cannot verify any attribute; `hasattr` lies |
| `exec` or `eval` on constructed strings | no checker, no linter, no debugger, and an injection surface |
| generating classes at import time | `grep` for the class name finds nothing |
| monkeypatching a dependency | breaks on the dependency's next release, at a distance |
| a decorator without `functools.wraps` | tracebacks and help output name the wrapper |
| deep inheritance for reuse | every base attribute is public API, per lesson 26 |

Notice that none of those costs is "it is hard to read". That is a matter of opinion and invites an argument about the reader's skill. "The class name cannot be found by searching" is a fact, and it ends the discussion.

The counter-discipline matters too: sometimes the clever thing is right, and a reviewer who reflexively objects to every metaclass is as unhelpful as one who approves every one. Lesson 27 gave the four cases where a metaclass is required. If the change is one of them, say so and approve it.

### Reviewing your own code

The same list, with one addition: read the diff as a stranger before sending it. Most of the findings above are visible in a diff read cold, and the cheapest review is the one that never had to be a conversation.

## Practice

1. ▢ Review this. Name each finding and label it defect, risk, or preference.

   ```python
   class Report:
       rows = []

       def add(self, row):
           self.rows.append(row)

       def totals(self, rows=None):
           rows = rows or self.rows
           return sum(r.amount for r in rows)
   ```

<details markdown="1"><summary>Check</summary>

- **Defect**: `rows = []` is a class attribute, so every `Report` shares one list, per lesson 22. `append` mutates it, so the second report includes the first's rows.
- **Defect**: `rows or self.rows` treats an explicitly passed empty list as absent, per lesson 5, so `totals([])` returns the total of everything. `rows if rows is not None else self.rows`.
- **Risk**: `totals` accepts an `Iterable` that might be a generator, and `sum` consumes it, which is fine here and breaks if a second pass is added later, per lesson 8.
- **Preference**: `rows` as both a parameter name and an attribute name makes the body harder to follow.
- **Missing**: no annotations, so a checker sees nothing, per lesson 15.

</details>

2. ▢ Review this async handler.

   ```python
   async def handle(order_ids):
       results = []
       for order_id in order_ids:
           order = await db.fetch(order_id)
           results.append(await enrich(order))
       return results
   ```

<details markdown="1"><summary>Hint</summary>

How many fetches are in flight at once, and is that necessary?

</details>

<details markdown="1"><summary>Check</summary>

- **Defect, in the performance sense**: `await` in a loop over independent work, per lesson 37, so the total is the sum rather than the maximum. A `TaskGroup` makes them concurrent.
- **Risk**: no bound on concurrency once it is fixed. A thousand order ids becomes a thousand concurrent fetches, which the database will reject; `asyncio.Semaphore` or chunking is needed.
- **Risk**: no timeout. One slow fetch hangs the handler; `asyncio.timeout` bounds it.
- **Missing**: annotations, and a decision about what happens when one fetch fails, which is the choice between `TaskGroup` and `gather(return_exceptions=True)` from lesson 37.

The comment worth writing states the trade: making these concurrent turns a sum into a maximum, and it needs a semaphore sized to the connection pool, or it moves the failure from slow to refused.

</details>

3. ▢ Which of these belong in a human review?

   - a) A line is 130 characters
   - b) A public function returns `Order | None` but is annotated `-> Order`
   - c) Imports are not sorted
   - d) A new public parameter is positional
   - e) A variable is named `l`
   - f) A `submit` result is discarded

<details markdown="1"><summary>Check</summary>

Human: **b**, **d**, **f**.

- b) A defect a checker would catch if run, and worth saying because the fix is a design decision about the signature.
- d) An interface decision that cannot be undone after release, per lesson 40. This is the highest-value comment on the list.
- f) A silently swallowed exception, per lesson 35, invisible to any tool.

Automated: **a**, **c**, **e**. All three are lint rules, and any of them appearing in a review means the project's tooling is not configured, which is one comment to make once rather than in every review.

</details>

4. ▢ An author submits a metaclass that registers subclasses. Write the review comment.

<details markdown="1"><summary>Check</summary>

> `__init_subclass__` on the base class does this in four lines and keeps `type(Handler)` as `type`, which matters because a metaclass cannot be combined with a base from another library: `TypeError: metaclass conflict`. It also puts the registration in the class a reader already has open. Lesson 27's four cases for a metaclass are `__prepare__`, custom `isinstance`, customising the class object itself, and reaching a hierarchy whose base has no hook; this is none of them. Happy to be wrong if there is a case here I have missed.

What makes it work: it names the concrete cost rather than calling the approach wrong, offers the specific alternative, and leaves room for the author to know something you do not.

</details>

5. ▢ You find eleven things in one change: one defect, two risks, eight preferences. What do you send?

<details markdown="1"><summary>Check</summary>

The defect and the two risks, labelled. Perhaps one or two of the preferences, if they are genuinely clearer and cheap, marked as non-blocking.

Not all eleven. A review of eleven comments reads as a rejection of the change rather than three specific problems, the author defends rather than fixes, and the defect is discussed last. If the eight preferences share a theme worth addressing, that is a separate conversation about conventions, or a linter rule, which is where it belongs permanently.

</details>

6. ▢ A colleague's reviews are technically correct and the team dreads them. Diagnose it.

<details markdown="1"><summary>Check</summary>

The usual causes, all fixable and none about correctness:

- Defects and preferences are not distinguished, so everything reads as blocking.
- Comments state a rule rather than a consequence, so the author cannot tell whether their case is an exception.
- Findings a tool should report appear in the review, which feels like being marked rather than helped.
- No comment ever says what to do instead, so each round is a guess.
- Nothing is ever acknowledged as good, so the review has no signal about what to repeat.

The single highest-leverage change is labelling. "Defect, blocking" and "preference, non-blocking" on each comment costs three words and changes how the whole review reads.

</details>

## Real-world reps

- [ ] Take the checklist table and use it on the next three changes you review. Note which rows actually fire in your codebase; those are the lessons your team needs.
- [ ] Read one of your own past changes cold and label every finding defect, risk, or preference.
- [ ] Find a review comment you made that stated a rule, and rewrite it as a consequence plus an alternative.
- [ ] Move one recurring preference out of your reviews and into a linter rule.
- [ ] Tomorrow: in the next review, write one specific piece of praise about something you want repeated.

## Going further

- [PEP 8, A Foolish Consistency](https://peps.python.org/pep-0008/): the section on when to break the style guide, which is the part reviewers forget
- [PEP 20, The Zen of Python](https://peps.python.org/pep-0020/): short, and useful as shared vocabulary rather than as an argument
- [Ruff rules](https://docs.astral.sh/ruff/rules/): a catalogue of the findings that should never be a human comment
- [`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps): the one-line fix for the decorator finding above
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
