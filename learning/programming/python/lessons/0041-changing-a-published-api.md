---
title: 41. Changing a Published API
description: Deprecation that users actually see, and what counts as a breaking change
type: lesson
---

# Lesson 41. Changing a Published API

**Mission link:** A published API can be evolved without breaking dependants, and the mechanism has one part everybody gets wrong: a deprecation warning that nobody sees is not a deprecation, it is a surprise scheduled for later.
**Primary source:** [The Python Standard Library, warnings](https://docs.python.org/3/library/warnings.html)
**Prerequisites:** [Lesson 20](0020-building-a-package.md), [Lesson 40](0040-designing-an-api.md)

## Warm-up

1. ▢ Lesson 20: what happens to a version number once it is published?

<details markdown="1"><summary>Check</summary>

It is spent. It can be yanked but never replaced, so the artefact for that version is final.

</details>

2. ▢ Lesson 40 listed things callers depend on that are not in the signature. Name three.

<details markdown="1"><summary>Check</summary>

Exception types, error message wording, the order of a returned list, private attributes, timing, the concrete return type, and the `repr`.

</details>

## Know this

### What counts as breaking

| Breaking | Not breaking |
|---|---|
| removing or renaming anything public | adding a keyword-only parameter with a default |
| changing a parameter from keyword to positional, or reordering | adding a new function or class |
| narrowing an accepted type | widening an accepted type |
| widening a return type | narrowing a return type |
| changing the exception raised | adding a subclass of an exception you already raise |
| changing the order of a returned sequence | adding a field to a returned dataclass, usually |
| raising the minimum Python version | raising a dependency's minimum, usually |

The two type rows are worth reading twice, because they are asymmetric and people get them backwards. Accepting **more** is safe; accepting **less** breaks callers. Returning **less** is safe; returning **more**, such as `Order | None` where you returned `Order`, breaks every caller who did not narrow.

Under semantic versioning, breaking goes in a major release, new features in a minor, fixes in a patch. Python packaging does not enforce this, and many projects do not follow it, which is exactly why your own policy should be stated in the readme.

### Deprecation that users see

This is the part that goes wrong. `DeprecationWarning` is **hidden by default** unless it is attributed to `__main__`. Verified, with two functions in a library called from a script:

```python
def no_stacklevel(x):
    warnings.warn("deprecated", DeprecationWarning)            # default stacklevel=1

def with_stacklevel(x):
    warnings.warn("deprecated", DeprecationWarning, stacklevel=2)
```

```text
-- after no_stacklevel --                       nothing printed
/private/tmp/dw/app2.py:4: DeprecationWarning: deprecated
  with_stacklevel(1)
-- after with_stacklevel --
```

The first warning was silently dropped. The default filter is:

```python
('default', None, DeprecationWarning, '__main__', 0)
('ignore',  None, DeprecationWarning, None, 0)
```

Shown when attributed to `__main__`, ignored otherwise. `stacklevel=2` attributes it to **your caller** rather than to your own module, which is both more useful, because it names the line to change, and the reason it is visible at all.

So: **always pass `stacklevel=2`** from a public function, `3` from a function one level in. Without it the deprecation is invisible for the entire notice period, and the removal arrives as a broken build.

Since Python 3.13 there is a decorator that gets this right and is also read by type checkers:

```python
from warnings import deprecated

@deprecated("use new_name instead; old_name is removed in 3.0")
def old_name(x): ...
```

```text
category: DeprecationWarning | message: use new_name instead
```

A checker flags call sites at check time, which reaches users who never run with warnings enabled. Note it lives in `warnings`, not in `typing`, on current versions.

### The message is a migration instruction

```python
warnings.warn(
    "Order.total is deprecated and will be removed in shopkit 3.0; "
    "use Order.total_amount, which returns a Decimal rather than a float.",
    DeprecationWarning,
    stacklevel=2,
)
```

Four things, all necessary: what is deprecated, when it goes, what to use instead, and what differs about the replacement. A message saying only "deprecated" makes every user open your source.

### The timeline

1. **Release N**: the new API exists, the old one works and warns.
2. **The notice period**: at least one minor release, and long enough that a user upgrading twice a year sees the warning before the removal. Announce it in the changelog, not only in the warning.
3. **Release N+M, a major version**: the old API is removed.

Shortcuts that are sometimes right: for a security fix, break immediately and say so. For a pre-1.0 library, the version number already says stability is not promised, and abusing that for a widely used package is a choice with consequences.

### Shims

```python
def total_amount(self) -> Decimal: ...

@property
@deprecated("use total_amount; total returns a float and will be removed in 3.0")
def total(self) -> float:
    return float(self.total_amount())
```

A property is the cheapest shim for a renamed attribute, per lesson 23, and needs no change at any call site. For a renamed module, re-export from the old path. For a changed parameter, accept both and warn:

```python
def send(message, *, timeout=5.0, timeout_seconds=None):
    if timeout_seconds is not None:
        warnings.warn("timeout_seconds is deprecated; use timeout",
                      DeprecationWarning, stacklevel=2)
        timeout = timeout_seconds
```

Every shim has a removal date and a line in the changelog, or it is permanent.

### Testing the deprecation

```python
def test_total_warns():
    with pytest.warns(DeprecationWarning, match="use total_amount"):
        order.total
```

Two reasons this test matters. It fails if the warning is removed by accident, and it fails if someone breaks the `stacklevel` in a refactor. Add `-W error::DeprecationWarning` to your own test configuration so **your** code cannot use its own deprecated API, which is the usual way a shim outlives its notice period.

### For the maintainer's own dependencies

The same rules pointed the other way. Run your test suite with deprecation warnings enabled:

```bash
python -W error::DeprecationWarning -m pytest
```

Every failure is a call you will have to change eventually, discovered now rather than during an urgent upgrade. This single flag is the cheapest maintenance habit in the arc.

## Practice

1. ▢ Why does a user of this library never see the warning?

   ```python
   # shopkit/orders.py
   def get_total(order):
       warnings.warn("get_total is deprecated", DeprecationWarning)
       return order.total_amount
   ```

<details markdown="1"><summary>Hint</summary>

Which module does the warning get attributed to, and what does the default filter do with that?

</details>

<details markdown="1"><summary>Check</summary>

`stacklevel` defaults to 1, so the warning is attributed to `shopkit/orders.py`. The default filter shows `DeprecationWarning` only when attributed to `__main__` and ignores it everywhere else, so the user sees nothing at all.

```python
warnings.warn(
    "get_total is deprecated and is removed in shopkit 3.0; use order.total_amount",
    DeprecationWarning,
    stacklevel=2,
)
```

Now it is attributed to the caller's line, which is both visible and actionable. Or use `@deprecated`, which also reaches users through their type checker.

</details>

2. ▢ Breaking or not?

   - a) `def parse(text: str)` becomes `def parse(text: str | bytes)`
   - b) `def find(id) -> Order` becomes `-> Order | None`
   - c) Adding `ItemMissing(StoreError)` and raising it where `StoreError` was raised
   - d) `requires-python = ">=3.10"` becomes `">=3.12"`
   - e) A returned list becomes sorted

<details markdown="1"><summary>Check</summary>

- a) Not breaking. Accepting more is safe.
- b) **Breaking.** Every caller doing `find(x).amount` now type-checks against `None` and can fail at run time. Returning more is a break.
- c) Not breaking, provided callers catch the base class. It is why lesson 10 wanted one base per package.
- d) Breaking for users on 3.10 and 3.11, who can no longer install it. Major release, and a changelog entry.
- e) Formally not breaking, in practice yes: callers' tests assert the old order, per Hyrum's law. Announce it.

</details>

3. ▢ Write the deprecation for renaming `Order.total`, a float, to `Order.amount`, a `Decimal`.

<details markdown="1"><summary>Check</summary>

```python
@dataclass(frozen=True)
class Order:
    amount: Decimal

    @property
    @deprecated(
        "Order.total is deprecated and will be removed in shopkit 3.0; "
        "use Order.amount, which is a Decimal rather than a float."
    )
    def total(self) -> float:
        return float(self.amount)
```

Plus: a changelog entry naming the removal version, a test asserting the warning fires with that message, and `-W error::DeprecationWarning` in the project's own test run so internal code cannot keep using it.

The type change is the part to state loudly. A caller who mechanically renames `total` to `amount` now gets a `Decimal`, and `Decimal` plus `float` raises `TypeError`, so the message has to warn about more than the name.

</details>

4. ▢ A library at 0.9 has 4,000 dependants and wants to remove three functions. Argue both ways.

<details markdown="1"><summary>Check</summary>

For removing now: the version says pre-1.0, semantic versioning explicitly does not promise stability below 1.0, and anyone depending on a 0.x release without an upper bound accepted that risk. Carrying shims into 1.0 makes the first stable release worse.

Against: 4,000 dependants is a stable API regardless of the number, and the number is not what users read. Breaking them costs goodwill that a version string does not buy back, and many of those dependants are themselves libraries, so the break propagates.

The defensible middle: deprecate in 0.9, with visible warnings and `@deprecated` so checkers flag it, release 1.0 with the shims still present, and remove in 2.0. The version number then means what it says, and the removal is at a boundary users expect.

</details>

5. ▢ What does `-W error::DeprecationWarning` in your test configuration find?

<details markdown="1"><summary>Check</summary>

Two categories, both valuable.

Your own code calling your own deprecated API, which is how a shim survives past its removal date: the removal fails a test somewhere internal, and the deadline slips.

And your code calling **your dependencies'** deprecated APIs, which is the upgrade work you would otherwise discover in a hurry when a major version lands. Every failure is a change you now make on your own schedule.

The cost is noise from dependencies you cannot fix, which is handled with a targeted `filterwarnings` entry per module rather than by turning the flag off.

</details>

6. ▢ A team never deprecates: they change the API and bump the major version. What do they gain and lose?

<details markdown="1"><summary>Check</summary>

Gain: no shim code, no dual code paths, no removal schedule to track, and a clean codebase. For an internal service with one consumer that upgrades in lockstep, this is correct and the whole deprecation machinery is waste.

Lose: users cannot migrate incrementally. A major bump with five simultaneous breaks forces a single large change, so users postpone it, stay on the old version, and stop receiving fixes. That is how a library ends up maintaining two branches.

The distinguishing question is whether consumers upgrade on your schedule or on theirs. Inside one repository, break freely. Published to an index, a deprecation period is the cost of having users.

</details>

## Real-world reps

- [ ] Add `-W error::DeprecationWarning` to your test run and count the failures. Each is future work discovered cheaply.
- [ ] Grep your codebase for `warnings.warn` without `stacklevel`, and fix each one. Those deprecations were invisible.
- [ ] Take one deprecated function you maintain and check whether its message names the replacement and the removal version.
- [ ] Write a `pytest.warns` test for one deprecation, so removing the warning by accident fails the build.
- [ ] Tomorrow: read the changelog of a dependency you rely on and see how much notice you actually got for its last removal.

## Going further

- [`warnings`](https://docs.python.org/3/library/warnings.html): the filter defaults, `stacklevel`, and `catch_warnings`
- [PEP 702, Marking deprecations using the type system](https://peps.python.org/pep-0702/): the `@deprecated` decorator and what checkers do with it
- [PEP 387, Backwards Compatibility Policy](https://peps.python.org/pep-0387/): how CPython itself decides what may break, and over what period
- [Semantic Versioning](https://semver.org/): the convention, and its limits
- [`pytest.warns`](https://docs.pytest.org/en/stable/how-to/capture-warnings.html): asserting a warning fires, and turning warnings into errors
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
