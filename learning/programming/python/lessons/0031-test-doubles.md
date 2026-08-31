---
title: 31. Test Doubles
description: What to replace, what to leave alone, and why patch takes the path where the name is used
type: lesson
---

# Lesson 31. Test Doubles

**Mission link:** The mission asks what deserves a mock and what does not. Most of the pain in a slow, brittle suite comes from mocking the wrong layer, and most of the confusion comes from one rule about where `patch` points.
**Primary source:** [The Python Standard Library, unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
**Prerequisites:** [Lesson 13](0013-modules-and-packages.md), [Lesson 29](0029-fixtures.md)

## Warm-up

1. ▢ Lesson 13: after `from settings import TIMEOUT`, why does setting `settings.TIMEOUT = 30` not change what the importing module sees?

<details markdown="1"><summary>Check</summary>

The `from` import bound a second, independent name to the same object. Rebinding one does not touch the other. This lesson is that fact with consequences.

</details>

2. ▢ What is the difference between replacing a payment gateway and replacing a dict?

<details markdown="1"><summary>Check</summary>

One is a boundary you do not control and cannot call in a test; the other is fast, deterministic and already correct. Only the first is a candidate.

</details>

## Know this

### The five kinds, and the two worth using

| Name | Is |
|---|---|
| **dummy** | a value passed to satisfy a signature and never used |
| **stub** | returns canned answers, asserts nothing |
| **fake** | a real, working, simplified implementation |
| **spy** | records how it was called, and still does the real thing |
| **mock** | records calls, and the test asserts on them |

In practice: **fakes for boundaries you own the interface to, stubs for values you need to control, and mocks only when the call itself is the behaviour under test.** A test asserting "the email was sent" needs a mock, because sending is the outcome. A test asserting "the total is 90" needs neither.

### `patch` points at the name that is used

This is the rule that costs people the most time, and lesson 13 already explained why.

```python
# pkg/clock.py
def now(): return "real"

# pkg/report_from.py
from pkg.clock import now
def stamp(): return f"at {now()}"

# pkg/report_mod.py
from pkg import clock
def stamp(): return f"at {clock.now()}"
```

```python
with patch("pkg.clock.now", return_value="fake"):
    report_from.stamp()      # 'at real'   <- patch had no effect
    report_mod.stamp()       # 'at fake'

with patch("pkg.report_from.now", return_value="fake"):
    report_from.stamp()      # 'at fake'
```

Patching where the function is **defined** does nothing to a module that did `from ... import`, because that module holds its own binding. Two consequences:

1. The patch target is `where.it.is.used`, not `where.it.is.defined`.
2. Importing modules rather than names, `from pkg import clock` then `clock.now()`, makes the patch target stable and the code easier to test. That is a design argument for the `import module` style, not just a testing trick.

`monkeypatch.setattr("pkg.report_from.now", fake)` from lesson 29 does the same job with automatic undo, and is the pytest-native spelling.

### `Mock` believes everything

```python
m = Mock()
m.chrage(1, 2, 3, 4, nonsense=True)     # <Mock name='mock.chrage()'>
m.whatever.deeply.nested                # <Mock name='mock.whatever.deeply.nested'>
```

A bare `Mock` accepts any attribute, any call, any arguments, and returns another `Mock`. So a test using one keeps passing after you rename the method, change its signature, or delete it. The suite is green and the code is broken, which is the worst outcome available.

`create_autospec`, or `patch(..., autospec=True)`, builds the double from the real object's signature:

```python
gateway = create_autospec(Gateway, instance=True)

gateway.charge(10, "GBP")               # fine
gateway.charge(10)                      # TypeError: missing a required argument: 'currency'
gateway.chrage(10, "GBP")               # AttributeError: Mock object has no attribute 'chrage'
gateway.charge(10, "GBP", "extra")      # TypeError: too many positional arguments
```

**Use `autospec` by default.** Without it, the double drifts away from the thing it stands for and nothing tells you.

Then assert on the interaction only when the interaction is the point:

```python
gateway.charge.assert_called_once_with(10, "GBP")
```

### Do not mock what you do not own

The rule has a reason: a mock of a third-party client encodes your belief about that library's API, and a mock cannot be wrong about it. When the library changes, or when your belief was mistaken from the start, the test still passes.

The alternative is a thin layer you own:

```python
class PaymentGateway(Protocol):          # your interface, from lesson 17
    def charge(self, amount: Decimal, currency: str) -> str: ...

class StripeGateway:                     # the only code that touches the library
    def charge(self, amount, currency): ...

class FakeGateway:                       # for tests: real, simple, in memory
    def __init__(self): self.charges = []
    def charge(self, amount, currency):
        self.charges.append((amount, currency))
        return "ch_test_1"
```

Now the tests use `FakeGateway`, which is a working implementation you can assert against, and exactly one class needs an integration test against the real service. The library's shape is checked in one place instead of asserted in forty.

### What to replace, and what to leave

| Replace | Leave alone |
|---|---|
| network calls | pure functions |
| a payment or email provider | dicts, lists, dataclasses |
| the current time and time zone | your own domain logic |
| randomness and generated ids | a fast in-memory database |
| the filesystem, sometimes: `tmp_path` is usually better | another module in the same package |
| a slow or rate-limited third-party service | anything already deterministic and fast |

Mocking inside your own package is the smell that matters. If a unit test needs four patches to run, it is not the test that is wrong: the code under test is calling out to four collaborators it should have been handed. Passing dependencies in as arguments removes the patches.

### Time and randomness

```python
def total_due(order, *, today: date) -> Decimal:       # injected
    ...
```

Injecting the clock is better than patching it, because the function becomes deterministic for every caller rather than only for tests. When injection is not practical, patch the one place that reads the clock:

```python
def test_overdue(monkeypatch):
    monkeypatch.setattr("shop.billing.today", lambda: date(2026, 1, 31))
```

The same applies to `uuid4` and `random`. `freezegun` and `time-machine` exist for the cases where time is read from many places, and needing one is a signal about the code.

### Asserting on calls, carefully

```python
gateway.charge.assert_called_once_with(10, "GBP")   # exact, positional matters
gateway.charge.assert_any_call(10, "GBP")           # among several
assert gateway.charge.call_count == 2
assert gateway.charge.call_args.kwargs["currency"] == "GBP"
```

Two failure modes. `assert_called_once_with` pins the exact argument form, so switching a caller from positional to keyword breaks a test that cares about neither. And `assert_called_with` on a mock that was never configured with `autospec` will happily accept a method name that no longer exists, which is the drift above.

Also: `mock.assert_called_once()` exists, and misspelling it as `assert_called_once` on a bare `Mock`, or inventing `assert_called_twice`, silently creates a new attribute and asserts nothing. `autospec` and `Mock(spec=...)` prevent that too.

## Practice

1. ▢ The patch has no effect. Why, and give both fixes.

   ```python
   # shop/billing.py
   from shop.clock import today
   def is_overdue(order): return today() > order.due_date

   # tests
   with patch("shop.clock.today", return_value=date(2026, 1, 31)):
       assert is_overdue(order)
   ```

<details markdown="1"><summary>Hint</summary>

How many names refer to the function, and which one did the patch replace?

</details>

<details markdown="1"><summary>Check</summary>

`shop.billing` holds its own binding, created by the `from` import at import time. Patching `shop.clock.today` replaces the name in `shop.clock` and leaves `shop.billing.today` pointing at the original.

Fix one, in the test: `patch("shop.billing.today", ...)`, the name where it is used.

Fix two, in the code: `from shop import clock` and call `clock.today()`, so there is only one binding and the patch target is stable. That version is also easier to read, because the call says where the function comes from.

</details>

2. ▢ This test passes after `charge` is renamed to `capture`. Explain, and fix it.

   ```python
   def test_charges_the_card():
       gateway = Mock()
       checkout(order, gateway)
       gateway.charge.assert_called_once_with(Decimal("90"), "GBP")
   ```

<details markdown="1"><summary>Check</summary>

It does not pass, and that is the point worth being precise about: `assert_called_once_with` fails because the renamed code calls `capture`, so `charge` was never called. What silently passes is the reverse direction, and every call **into** the mock:

```python
gateway.chrage(...)          # typo in the code under test: accepted, returns a Mock
gateway.charge(1, 2, 3, 4)   # wrong signature: accepted
```

So the mock hides defects in the code it stands for, and the assertion only catches the specific rename it names.

```python
gateway = create_autospec(PaymentGateway, instance=True)
```

Now a call with the wrong name raises `AttributeError` and a call with the wrong arity raises `TypeError`, at the moment the code under test makes it.

</details>

3. ▢ Fake, stub, or nothing at all?

   - a) An HTTP client for a third-party address-lookup service
   - b) A function computing VAT from a country code
   - c) `datetime.now()`, in a function that decides whether an invoice is overdue
   - d) A `Repository` class that talks to a real database, in a unit test of pricing logic
   - e) A `dict` of feature flags

<details markdown="1"><summary>Check</summary>

- a) Fake, behind an interface you own. Do not mock the library directly.
- b) Nothing. It is pure, fast and deterministic, and replacing it would test the replacement.
- c) Inject the date as a parameter. Failing that, a stub via `monkeypatch` on the one place that reads it.
- d) Fake, or restructure so the pricing function takes the data rather than the repository. If the pricing logic needs a repository at all, that is the finding.
- e) Nothing. Construct the dict the test wants.

</details>

4. ▢ A unit test needs four `patch` decorators. What does that tell you, and what is the fix?

<details markdown="1"><summary>Check</summary>

That the function under test reaches out to four collaborators it looks up itself, usually via module-level imports or global singletons. The patches are compensating for the design.

The fix is dependency injection: the function takes its collaborators as parameters, and the test passes fakes directly with no patching at all. That also makes the function's dependencies visible in its signature, which a checker can then verify.

Where the collaborators genuinely belong at module level, such as a logger, they do not need patching in the first place.

</details>

5. ▢ Why is a fake usually better than a mock for a repository?

<details markdown="1"><summary>Check</summary>

A fake is a working implementation, so it enforces the interface's semantics: an object saved can be read back, an id that does not exist raises, and two saves of the same id behave the way the real one does. Tests then assert on outcomes, `assert repo.get(1).amount == 90`, which is what the caller actually cares about.

A mock asserts on calls, `repo.save.assert_called_once_with(order)`, which couples the test to how the code is written rather than to what it achieves. Refactoring two saves into one breaks the test without changing behaviour, and the test passes when `save` is called with an object that the real repository would reject.

The cost of a fake is that it is code, and it can drift from the real implementation. A shared contract test, parametrised over the fake and the real one from lesson 30, is what keeps them honest.

</details>

6. ▢ A colleague says "we mock the database so unit tests are fast; the integration suite covers the real thing". What is right and what is missing?

<details markdown="1"><summary>Check</summary>

Right: fast, isolated tests for logic are worth having, and something has to stand in for the database.

Missing: three things. The mock encodes assumptions about the driver's behaviour that only the integration suite can check, so those assumptions need to be exercised somewhere and usually are not. An in-memory database, or a real one in a container, is often fast enough that the trade was unnecessary. And most importantly, if the pricing logic needs a database mock at all, the logic and the persistence are entangled; separating them removes the question rather than answering it.

</details>

## Real-world reps

- [ ] Grep your tests for `patch(` and `Mock(` and add `autospec=True` or `create_autospec` to each. Anything that starts failing was a drifted double.
- [ ] Find a patch target that points at where a function is defined rather than where it is used, and check whether the test was ever effective.
- [ ] Take one unit test with more than two patches and rewrite the function under test to accept its dependencies.
- [ ] Replace one mocked repository with a small in-memory fake, and see how many assertions become statements about outcomes instead of calls.
- [ ] Tomorrow: find every place your code reads the current time, and count them. That number is why time is hard to test.

## Going further

- [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html): `Mock`, `patch`, `create_autospec` and the assertion methods
- [Where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch): the documentation's own statement of the rule in this lesson
- [Autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing): what it checks, and its limitations
- [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html): the pytest-native patching with automatic undo
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
