---
title: 28. What a Test Asserts
description: One behaviour per test, a failure message that needs no debugger, and plain assert
type: lesson
---

# Lesson 28. What a Test Asserts

**Mission link:** The mission asks for tests that fail informatively. That is a property of how a test is written, not of the framework, and it is the difference between a red build you can read and one you have to reproduce locally.
**Primary source:** [pytest documentation, Get Started](https://docs.pytest.org/en/stable/getting-started.html)
**Prerequisites:** [Lesson 10](0010-exceptions.md), [Lesson 13](0013-modules-and-packages.md)

## Warm-up

1. ▢ Lesson 10: why is `assert amount > 0` the wrong way to validate user input?

<details markdown="1"><summary>Check</summary>

Assertions are stripped under `-O`, so the check disappears in exactly the deployment that needed it. In a **test** that is not a concern, because tests never run optimised.

</details>

2. ▢ What is the single most useful thing a failing test can tell you?

<details markdown="1"><summary>Check</summary>

The actual value alongside the expected one, and which input produced it. This lesson is about getting that for free.

</details>

## Know this

A test is a function whose name starts with `test_`, in a file named `test_*.py`, and it asserts with the plain `assert` statement:

```python
def total(items):
    return sum(i["amount"] for i in items)

def test_totals_two_items():
    items = [{"amount": 10}, {"amount": 2}]
    assert total(items) == 13
```

```text
    def test_totals_two_items():
        items = [{"amount": 10}, {"amount": 2}]
>       assert total(items) == 13
E       AssertionError: assert 12 == 13
E        +  where 12 = total([{'amount': 10}, {'amount': 2}])
```

No `assertEqual`, no message argument. pytest rewrites the assertion at import time to report both sides and how each was computed, and it does the same for containers:

```text
E       assert [1, 2, 3] == [1, 2, 4]
E         At index 2 diff: 3 != 4

E       AssertionError: assert {'a': 1, 'b': 2} == {'a': 1, 'b': 3}
E         Omitting 1 identical items, use -vv to show
E         Differing items:
E         {'b': 2} != {'b': 3}

E       AssertionError: assert 'hello world' == 'hello werld'
E         - hello werld
E         ?        ^
E         + hello world
E         ?        ^
```

This is the practical reason for `__repr__` from lesson 24: every one of those messages is repr output. A class without one turns the third message into two object addresses.

### The shape of a test

```python
def test_rejects_negative_amount():
    order = Order(id=1, amount=Decimal("10.00"))     # arrange

    with pytest.raises(ValueError, match="negative"):
        order.apply_discount(Decimal("-5.00"))       # act, and assert
```

Three properties, in order of how much they matter.

**One behaviour per test.** Not one assertion, which is a rule people cite and which forces awkward tests: several assertions about one behaviour are fine. What is not fine is a test that exercises three behaviours, because when it fails you learn only that one of the three broke.

**A name that states the behaviour.** `test_rejects_negative_amount` tells you what broke from the summary line alone. `test_order_2` requires opening the file, and `test_apply_discount` names the method rather than the claim.

**No logic.** A test with an `if`, a loop, or a computed expected value has a second implementation of the thing under test inside it, and now two things can be wrong. Write the expected value as a literal, even when that means repetition. Parametrisation, in lesson 30, is how to avoid the loop.

### The assertions worth knowing

```python
assert result == expected                    # the default, and usually enough
assert result is None                        # identity, from lesson 5
assert 0.1 + 0.2 == pytest.approx(0.3)       # floats, from lesson 14
assert "negative" in str(exc.value)          # part of a message

with pytest.raises(ValueError, match="negative"):
    ...                                      # match is a regex against str(exc)

with pytest.raises(ValueError) as exc_info:
    ...
assert exc_info.value.field == "amount"      # inspect the exception object
```

`pytest.raises` without an argument to narrow it is a weak test: it passes when the code raises the right exception for the wrong reason, and it passes when a typo raises `NameError`. Pass `match=`, or assert on the exception object.

### Running and selecting

```bash
pytest                          # discover and run everything
pytest tests/test_orders.py     # one file
pytest -k "discount"            # tests whose name matches
pytest -x                       # stop at the first failure
pytest --lf                     # only what failed last time
pytest -q                       # one line per file instead of per test
pytest -vv                      # full diffs, no truncation
```

`--lf` and `-x` together are the debugging loop. `-vv` is the answer to "use `-v` to get more diff" in the output above.

### Where tests live

```text
shop/
├── src/shop/orders.py
└── tests/
    ├── conftest.py             # shared fixtures, lesson 29
    └── test_orders.py
```

Tests outside the package, importing it as an installed package, which is lesson 19's editable install. That way the tests exercise what users get, and `tests/` is not shipped in the wheel.

Two mechanical notes that cause most first-day confusion. Test files need unique names when there is no `__init__.py` in `tests/`, because otherwise two `test_utils.py` collide as modules. And a test that needs the package importable needs the package installed, or `pythonpath = ["src"]` in the pytest configuration, which is the shortcut.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
```

`-ra` prints a summary of everything that was not a plain pass, which is how skipped and expected-failure tests stop being invisible. `--strict-markers` turns a misspelled marker into an error rather than a silently ignored one.

### What deserves a test

The mission's answer, in one sentence: **anything whose failure you would want to hear about from a machine rather than a user.**

| Deserves a test | Rarely worth one |
|---|---|
| a bug you just fixed | a getter that returns an attribute |
| a branch a reader would get wrong | a `__repr__` |
| boundary values: empty, one, zero, negative, maximum | code that only calls a library and does nothing else |
| the contract of a public function | a private helper covered through its caller |
| anything involving money, dates or time zones | a constant |

The regression test is the highest-value test there is, and it has an unfair advantage: you know it fails before you fix anything. Write it first, watch it fail, then fix.

## Practice

1. ▢ This test passes. Explain why it is nearly worthless.

   ```python
   def test_apply_discount():
       order = Order(id=1, amount=Decimal("100"))
       with pytest.raises(Exception):
           order.apply_discount(Decimal("-5"))
   ```

<details markdown="1"><summary>Hint</summary>

What else, besides the intended rejection, would make this pass?

</details>

<details markdown="1"><summary>Check</summary>

`Exception` catches nearly everything. The test passes if `apply_discount` is misspelled inside the method and raises `AttributeError`, if `Decimal` is not imported and it raises `NameError`, if the argument order is wrong and it raises `TypeError`, and if the discount logic is entirely absent but something unrelated fails first.

```python
with pytest.raises(ValueError, match="must not be negative"):
    order.apply_discount(Decimal("-5"))
```

Name the type, and pin the message with `match`. The name also should say what the test claims: `test_rejects_negative_discount`.

</details>

2. ▢ Split this into the right number of tests, and name them.

   ```python
   def test_order():
       order = Order(id=1, amount=Decimal("100"), country="GB")
       assert order.amount == Decimal("100")
       order.apply_discount(Decimal("10"))
       assert order.amount == Decimal("90")
       assert order.vat() == Decimal("18")
       with pytest.raises(ValueError):
           order.apply_discount(Decimal("-1"))
   ```

<details markdown="1"><summary>Check</summary>

Four behaviours, so four tests:

```python
def test_stores_the_amount_it_was_given(): ...
def test_discount_reduces_the_amount(): ...
def test_vat_is_twenty_percent_for_gb(): ...
def test_rejects_a_negative_discount(): ...
```

The reason is what the failure tells you. In the original, a broken `vat` and a broken `apply_discount` produce the same line in the summary: `FAILED test_order`. Worse, the `raises` at the end is never reached when an earlier assertion fails, so a second defect stays hidden until the first is fixed.

</details>

3. ▢ Which of these tests has logic in it, and why does that matter?

   - a) `assert total([{"amount": 10}, {"amount": 2}]) == 12`
   - b) `assert total(items) == sum(i["amount"] for i in items)`
   - c) `for n in (0, 1, 5): assert double(n) == n * 2`
   - d) `assert format_money(Decimal("1234.5")) == "1,234.50"`

<details markdown="1"><summary>Check</summary>

**b** and **c** have logic.

- b) reimplements the function under test, so the test passes whenever both copies are wrong the same way. It tests nothing about correctness.
- c) computes the expected value and loops, so a failure reports one line for three cases and does not say which `n` failed. Parametrisation in lesson 30 fixes exactly this.
- a) and d) state literals. They repeat themselves, and that repetition is what makes the failure readable.

</details>

4. ▢ Why does `assert result == expected` beat `assert result == expected, "totals should match"`?

<details markdown="1"><summary>Check</summary>

The message **replaces** the introspection. With no message, pytest prints both values and how each was computed. With one, you get your sentence and lose the numbers, so a failing test says "totals should match" and nothing about what they were.

Add a message only when it carries information the values do not, such as which of several fixtures was in play.

</details>

5. ▢ A test suite has 400 tests, all passing, and a production bug ships in a function with three branches. Where do you look first?

<details markdown="1"><summary>Check</summary>

At what the 400 tests assert, not at how many there are. The likely finds:

- Only the happy path of those three branches is covered, and coverage would say so, which is lesson 33.
- The test exercises the function through four layers, so the branch is reached with one fixed input.
- The assertions are weak: `pytest.raises(Exception)`, or `assert result is not None`.

Then write the regression test for the actual bug, watch it fail, and fix. That test is worth more than most of the 400, because it is the only one that has been proven to detect something.

</details>

6. ▢ Your `Order` class has no `__repr__` and a test comparing two orders fails. What does the output look like, and what is the one-line fix?

<details markdown="1"><summary>Check</summary>

Object addresses, with only the constructor calls to identify them:

```text
>       assert Order(1) == Order(2)
E       assert <shop.orders.Order object at 0x1094757f0> == <shop.orders.Order object at 0x1094982d0>
E        +  where <shop.orders.Order object at 0x1094757f0> = Order(1)
E        +  and   <shop.orders.Order object at 0x1094982d0> = Order(2)
```

The rewriting still shows how each side was produced, which helps when the values are built inline and not at all when they come from a fixture three files away.

The fix is `@dataclass` on the class, which generates both `__repr__` and `__eq__`, and turns that line into a field-by-field diff. Writing `__repr__` by hand does the same for a class that cannot be a dataclass. This is lesson 24's argument arriving as a concrete cost.

</details>

## Real-world reps

- [ ] Take the last bug you fixed and write the test after the fact. Then revert the fix, confirm the test fails, and reapply it. That loop is the only proof a test detects anything.
- [ ] Find a test in your suite named after a method rather than a behaviour, and rename it. Read the summary line afterwards.
- [ ] Grep for `pytest.raises(Exception)` and `raises(Exception)` and narrow each one, adding `match=`.
- [ ] Find a test with a loop or an `if` and convert it to literals. Note whether it was reimplementing the code under test.
- [ ] Tomorrow: add `-ra --strict-markers` to your pytest configuration and read the summary. Skipped tests you had forgotten about are the usual discovery.

## Going further

- [Get Started](https://docs.pytest.org/en/stable/getting-started.html): installation, discovery rules, and the first assertion
- [How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html): the rewriting, `pytest.raises`, and `approx`
- [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html): where tests live, and why the `src` layout matters here
- [Configuration](https://docs.pytest.org/en/stable/reference/customize.html): the `[tool.pytest.ini_options]` table
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
