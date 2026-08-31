---
title: 44. Judgment
description: When to break the rules from the earlier stages, and how to defend the call
type: lesson
---

# Lesson 44. Judgment

**Mission link:** This is the last lesson, and the mission's real ending: trusted to make the call and to explain it to someone else. Every rule in this arc has a case where it is wrong, and knowing which case is the difference between competence and seniority.
**Primary source:** [PEP 20, The Zen of Python](https://peps.python.org/pep-0020/)
**Prerequisites:** the whole arc, and in particular [Lesson 39](0039-measuring-before-optimising.md), [Lesson 40](0040-designing-an-api.md) and [Lesson 42](0042-reviewing-python.md)

## Warm-up

1. ▢ Lesson 27 gave a decision rule for metaclasses. What made it a rule rather than a prohibition?

<details markdown="1"><summary>Check</summary>

It named the condition under which a metaclass is the right answer: subclasses must be affected without opting in. A prohibition would have had no condition.

</details>

2. ▢ Which of the arc's rules have you already seen an exception to?

<details markdown="1"><summary>Check</summary>

Several, stated in the lessons themselves: a wide `except` in a per-item loop, a mutable class attribute as a deliberate registry, a metaclass for `__instancecheck__`, `assert` for an internal invariant, `threading.local` for a request id. This lesson is about how to recognise the next one.

</details>

## Know this

### Every rule in this arc has a shape

A rule worth following states a cost, not a taboo. That is what makes its exception findable: when the cost does not apply, neither does the rule.

| Rule | The cost it avoids | Exception when |
|---|---|---|
| never catch broadly | hiding an unexpected failure | a per-item loop that logs the exception and continues |
| never mutate a class attribute | accidental sharing between instances | a deliberate registry, marked `ClassVar` |
| no metaclasses | invisible action, and metaclass conflicts | subclasses must be affected without opting in |
| take `Iterable`, return `list` | restricting callers | the function genuinely mutates the argument |
| always annotate | unverified claims | a private three-line helper the checker infers |
| never `assert` for validation | it vanishes under `-O` | an internal invariant, not caller-caused |
| no shared mutable state | races | immutable, or guarded, or per-worker |
| frozen dataclasses by default | aliasing bugs | the object's identity is its mutation over time |
| always use a lock | corruption | there is nothing shared, which is the better fix |
| measure before optimising | wasted effort and worse code | the change also makes the code simpler |
| deprecate before removing | breaking users | one consumer, upgraded in lockstep |
| small public surface | permanent commitments | a library whose whole purpose is the surface |

Read that table as a method rather than a list. For any rule, ask what it protects against; then ask whether that thing can happen here. If it cannot, the rule is not binding, and saying so out loud is what a review needs.

### Deciding without enough information

Most real decisions are made with less than you want. Four questions, in this order, get most of them right:

**1. What is reversible?** A choice that can be changed in one commit needs a fraction of the deliberation of one that cannot. From lesson 40 and 41: a public signature, an exception type, a returned order, and a version number are effectively permanent; an internal structure is not. Spend the thinking where the mistake is expensive.

**2. What is the cost of being wrong, times how likely?** A wrong choice about a hot loop costs latency; a wrong choice about money arithmetic costs money. `Decimal` for the second is not caution, it is arithmetic on the expected cost.

**3. What does the code make impossible?** Better than "is this correct" is "can this be used incorrectly". A frozen dataclass, a `Literal`, an `Enum`, a keyword-only parameter and an exhaustive `match` all remove states rather than checking them, which is the highest-value form of design available in this language.

**4. Who has to understand it, and when?** Code read at three in the morning by someone who did not write it has a different clarity budget from a script run once. Both are legitimate; pretending they are the same is how a one-off script grows a plugin architecture.

### The cost of abstraction, stated honestly

Every abstraction is a bet that a change will come. When it does, the abstraction pays for itself many times. When it does not, you have paid indirection forever for nothing.

| Abstraction | Costs | Earns its place at |
|---|---|---|
| a `Protocol` | one more file to open when reading | the second implementer, or the first test double |
| a generic | harder signatures | the second type parameter |
| a base class | every base attribute becomes public API | shared implementation you own |
| a plugin registry | the class name is no longer greppable | plugins written outside your repository |
| a configuration option | a code path that will be untested | a user who genuinely needs both |
| a wrapper around a dependency | one indirection | the second call site, or the first test |

The asymmetry worth internalising: **removing an abstraction nobody needed is easy, and adding one later is also easy. Removing one people already depend on is not.** So the default is the concrete version, and the trigger is the second case, not the anticipated one.

### Explaining the call

A decision that cannot be explained is indistinguishable from a preference, and this is the mission's actual last clause. Three sentences, in this order:

1. **What you chose**, plainly.
2. **What it costs**, named specifically.
3. **What would change your mind.**

> We are using processes rather than subinterpreters for the transform. Subinterpreters start three times faster and would save about 60 milliseconds per job, but two of our C extensions have no statement about multiple-interpreter support and the failure mode is a crash rather than an error. If we get that statement, or if job start-up becomes a measurable share of the runtime, it is worth redoing.

The third sentence is the one that marks the decision as reasoning rather than taste, and it is the one that gets left out. It also does something practical: it records the condition under which the next person should revisit, which is otherwise lost.

Write it where it will be found: a commit message for a small call, a comment above the code for something that looks wrong without it, a short document for anything a whole team will live with. A decision recorded nowhere gets re-argued every six months.

### What seniority looks like here

Not knowing more rules. Four things, all visible in behaviour:

- **Reaching for the boring option** unless there is a reason, and being able to state the reason.
- **Changing your mind on evidence**, including a measurement that contradicts something you taught someone last month.
- **Saying "I do not know, here is how we could find out"**, which lesson 43 made concrete.
- **Making the decision the team can maintain**, not the one that demonstrates the most Python.

The last one is the hardest, because this arc has taught you constructs that are genuinely powerful, and the temptation to use them is strongest right after learning them. Descriptors, metaclasses, generics, `asyncio` and structural typing are all correct answers to specific problems and expensive answers to problems nobody had.

### Where to go from here

The arc is finished, and the mission's success criteria are the checklist to test yourself against. What is deliberately not here, from the `README`: web frameworks, the scientific stack, CPython internals past the point where they predict behaviour. Each is a separate arc, and each is easier now.

The habit that keeps this current is smaller than a curriculum: read What's New for each release, run your test suite with `-W error::DeprecationWarning`, and check a version-sensitive belief before teaching it. Three claims in this arc changed under exactly that check.

## Practice

1. ▢ For each, argue that the rule does not apply.

   - a) A `try/except Exception` around each item in a nightly import of 200,000 rows
   - b) A mutable class attribute on a `Plugin` base class
   - c) A `float` rather than a `Decimal`
   - d) No annotations on a 30-line script

<details markdown="1"><summary>Check</summary>

- a) The rule avoids hiding unexpected failures. Here the handler logs the exception with its traceback and records the row id, so nothing is hidden, and the alternative is one bad row aborting 199,999 good ones. Legitimate, provided the log is actually read and the failure count is reported.
- b) The rule avoids accidental sharing. A registry is deliberate sharing, and `ClassVar` from lesson 15 says so to a checker. Lesson 25's `__init_subclass__` populates it. Legitimate.
- c) The rule is about money and exact decimal arithmetic. For a physical measurement, a coordinate, or a machine-learning feature, `float` is correct and `Decimal` is slower and no more accurate. The rule was never about all numbers.
- d) The rule buys verification, which pays at module scale, per lesson 15. For a 30-line script with no callers, the checker has almost nothing to prove. Annotate the one function whose types you had to think about.

</details>

2. ▢ Rank by how much deliberation each deserves.

   - a) The name of a public function in a library with 400 dependants
   - b) Whether an internal helper takes two arguments or a dataclass
   - c) The exception type a published function raises
   - d) Whether to use a comprehension or a loop
   - e) The database column type for a money amount

<details markdown="1"><summary>Hint</summary>

Sort by reversibility first, then by the cost of being wrong.

</details>

<details markdown="1"><summary>Check</summary>

**e**, **a**, **c**, then **b**, then **d**.

- e) A migration on a large table, plus every stored value already wrong if the type is. Least reversible and most expensive.
- a) Permanent once released; changing it means a deprecation cycle, per lesson 41.
- c) Equally permanent and more often overlooked, since nobody thinks of it as the API.
- b) One commit, no external impact. Decide quickly and move on.
- d) Reversible in one line. Pick the one that reads better and stop.

The general shape: deliberation should track irreversibility, and most arguments in code review are about the bottom of this list.

</details>

3. ▢ A change adds a `Protocol`, a generic and a plugin registry, for one implementation. Write the review comment.

<details markdown="1"><summary>Check</summary>

> All three of these are bets that a second implementation is coming. If it is, say so in the description and I will approve as is. If it is not, each costs something now: the protocol adds a file to open when reading, the generic makes the signatures harder, and the registry means the class name cannot be found by searching. The concrete version is a smaller change and stays easy to abstract later, whereas the registry is the one that gets hard to remove once anything depends on it. What is the second case?

The final question is the point. If there is a second case, the abstractions are right; if there is not, the author usually notices while answering.

</details>

4. ▢ You told a colleague last month that binding a method to a local speeds up a loop. Lesson 39 measured no difference. What do you do?

<details markdown="1"><summary>Check</summary>

Tell them, with the measurement. Two sentences: the advice was from an older interpreter, here are the numbers on the one we run, so the loop can be written the readable way.

That is not a minor courtesy. Advice propagates, so a wrong performance claim spreads into code reviews and into other people's habits, and the person who taught it is the cheapest one to retract it. It also demonstrates the thing this lesson is actually about: the willingness to be publicly wrong on evidence is what makes your other claims worth believing.

</details>

5. ▢ Write the three-sentence explanation for choosing a frozen dataclass over a `TypedDict` for a configuration object.

<details markdown="1"><summary>Check</summary>

> We are parsing configuration into a frozen dataclass rather than a `TypedDict`. It costs a conversion step at the boundary and means the value is no longer a dict, so anything passing it to a library expecting one needs `asdict`. If we find we are calling `asdict` at more than one or two call sites, the `TypedDict` was the right shape and we should switch.

What makes it work: it names the real cost rather than only the benefit, and the revisit condition is observable rather than a feeling. Someone reading it in a year knows both what was traded and what to look for.

</details>

6. ▢ A team asks you to write their Python conventions. What do you include, and what do you refuse to?

<details markdown="1"><summary>Check</summary>

Include, because each has a cost that generalises: the formatter and the linter selection, so style is never discussed; strict type checking with a per-module ratchet, per lesson 16; one base exception per package; frozen dataclasses as the default shape; boundary conversion for external data; keyword-only parameters past the first one or two; `stacklevel=2` on every warning; and `-W error::DeprecationWarning` in the test run.

Refuse: anything a tool can enforce, which belongs in the tool's configuration and not in a document nobody reads; anything phrased as a prohibition without its cost, since it will be either cargo-culted or ignored; and anything about how much abstraction is correct, because that is the judgment this lesson exists for and a document cannot make it.

The most valuable thing to add is not a rule at all: for each convention, one sentence on what it protects against, so the next person can tell when it does not apply.

</details>

## Real-world reps

- [ ] Take the exception table above and find, in your own codebase, one place where a rule from this arc is being followed where it does not apply. Remove the ceremony.
- [ ] Write the three-sentence explanation for the largest technical decision you made recently, including the revisit condition. Put it where it will be found.
- [ ] Find an abstraction in your code with one implementation and decide, out loud, whether the second case is real.
- [ ] Retract one piece of advice you have given that you have not verified on your current interpreter.
- [ ] Test yourself against the eight success criteria in the workspace `README`, and pick the weakest one to work on next.
- [ ] Tomorrow: read What's New for the release you are on, end to end. It is the cheapest way to stay current, and it is once a year.

## Going further

- [PEP 20, The Zen of Python](https://peps.python.org/pep-0020/): shared vocabulary, and a set of trade-offs rather than rules
- [PEP 8, A Foolish Consistency](https://peps.python.org/pep-0008/): the style guide's own instructions for when to ignore it
- [PEP 387, Backwards Compatibility Policy](https://peps.python.org/pep-0387/): how the language itself weighs breaking against improving
- [What's New in Python](https://docs.python.org/3/whatsnew/index.html): the habit that keeps everything above current
- [Python Developer's Guide](https://devguide.python.org/): where the decisions in this arc are actually made
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
