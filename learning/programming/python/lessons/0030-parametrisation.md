---
title: 30. Parametrisation
description: One test body, many cases, and a failure that names the case that broke
type: lesson
---

# Lesson 30. Parametrisation

**Mission link:** The mission asks for parametrisation instead of copied test bodies. The payoff is not fewer lines: it is that each case is a separate test with its own name, so a failure says which input broke rather than that something in a loop did.
**Primary source:** [pytest documentation, How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html)
**Prerequisites:** [Lesson 28](0028-what-a-test-asserts.md), [Lesson 29](0029-fixtures.md)

## Warm-up

1. ▢ Lesson 28 objected to a loop inside a test. What exactly does the loop cost?

<details markdown="1"><summary>Check</summary>

The failure reports one test and one line, without saying which iteration failed, and the loop stops at the first failure so later cases go unchecked.

</details>

2. ▢ How many tests does one function with three parameter sets produce?

<details markdown="1"><summary>Check</summary>

Three, each collected, named and reported separately. That is the entire point.

</details>

## Know this

```python
@pytest.mark.parametrize("country, expected", [("GB", 0.20), ("DE", 0.19), ("NO", 0.25)])
def test_vat_rate(country, expected):
    assert vat_rate(country) == expected
```

Three tests, with generated names:

```text
test_p.py::test_vat_rate[GB-0.2] PASSED
test_p.py::test_vat_rate[DE-0.19] PASSED
test_p.py::test_vat_rate[NO-0.25] FAILED
```

And the failure names the case, with the arguments printed above the body:

```text
____________________________ test_vat_rate[NO-0.25] ____________________________

country = 'NO', expected = 0.25

>       assert vat_rate(country) == expected
E       AssertionError: assert 0.0 == 0.25
E        +  where 0.0 = vat_rate('NO')
```

Compare the loop version, which would have said `FAILED test_vat_rate` and left you guessing. The other property that matters: `NO` failing does not prevent `FR` from running, because they are separate tests.

Re-running one case is then possible:

```bash
pytest "test_p.py::test_vat_rate[NO-0.25]"
```

### Readable identifiers

pytest builds ids from the values, and for anything that is not a simple scalar it gives up and uses a position:

```text
test_falsy[0]           # 0
test_falsy[]            # the empty string
test_falsy[None]        # None
test_falsy[value3]      # []      no readable id
test_falsy[value4]      # {}      no readable id
```

`value3` in a CI summary tells nobody anything. Name the cases with `pytest.param`:

```python
@pytest.mark.parametrize("country, expected", [
    pytest.param("GB", 0.20, id="united-kingdom"),
    pytest.param("XX", 0.0, id="unknown-country"),
    pytest.param("ZZ", 0.0, id="not-implemented",
                 marks=pytest.mark.xfail(reason="rate table incomplete")),
])
def test_named(country, expected):
    assert vat_rate(country) == expected
```

```text
test_p.py::test_named[united-kingdom] PASSED
test_p.py::test_named[unknown-country] PASSED
test_p.py::test_named[not-implemented] XPASS (rate table incomplete)
```

Two things there. `marks=` attaches a mark to **one case**, which is how a single known-broken input gets an `xfail` without disabling the rest. And `XPASS` is what happens when an expected failure passes: by default it is not an error, so an `xfail` that silently starts working stays in the suite forever. `strict=True` on the mark, or `xfail_strict = true` in the configuration, turns that into a failure, which is what you want.

### Stacking multiplies

```python
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", ["x", "y"])
def test_stacked(a, b): ...
```

```text
test_stacked[x-1]  test_stacked[x-2]  test_stacked[y-1]  test_stacked[y-2]
```

Four tests: the cartesian product. Useful for genuinely independent dimensions, such as three storage backends against four payloads, and a trap when the dimensions are not independent, because you get combinations that cannot occur and have to be excluded case by case. Two stacked decorators with five values each is 25 tests, and a third makes 125.

### What belongs in a parameter list

The good cases are all one behaviour with several inputs:

| Pattern | Example |
|---|---|
| a lookup table | country to VAT rate |
| boundaries | `0`, `1`, `-1`, maximum, one over maximum |
| the falsy set, from lesson 5 | `0`, `""`, `None`, `[]`, `{}` |
| formats that must all parse | ISO, epoch, with and without a zone |
| inputs that must all be rejected | each with its expected message |
| every member of an `Enum` | so a new member fails the suite |

The bad case is a parameter that changes **which behaviour** is being tested. When the body needs `if expected_error:` to decide what to assert, that is two tests wearing one name:

```python
@pytest.mark.parametrize("value, expected, raises", [...])
def test_parse(value, expected, raises):
    if raises:                                  # stop
        with pytest.raises(ValueError):
            parse(value)
    else:
        assert parse(value) == expected
```

Split it: `test_parses_valid_input` with its cases, and `test_rejects_invalid_input` with its own.

### Parametrising a fixture

A fixture can be parametrised instead, and then every test using it runs once per value:

```python
@pytest.fixture(params=["sqlite", "postgres"])
def storage(request):
    return make_storage(request.param)

def test_saves_and_reads_back(storage):        # runs twice
    ...
```

This is how a contract test gets applied to several implementations. It is powerful and easy to overuse: a parametrised fixture in `conftest.py` doubles the runtime of every test that touches it, including those that do not care which backend they got.

### Parametrisation against a table of expectations

Sometimes the cleanest form is a dataclass per case, especially with more than three fields:

```python
@dataclass(frozen=True)
class Case:
    name: str
    payload: dict[str, object]
    expected: Decimal

CASES = [
    Case("no discount", {"amount": "100"}, Decimal("100")),
    Case("percentage discount", {"amount": "100", "discount": "10%"}, Decimal("90")),
]

@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_totals(case):
    assert total(case.payload) == case.expected
```

The `ids=` callable keeps the output readable, and the named fields stop a reader counting positions in a tuple of six.

## Practice

1. ▢ Convert, and say what improves in the output.

   ```python
   def test_falsy_values():
       for value in (0, "", None, [], {}):
           assert not value
   ```

<details markdown="1"><summary>Check</summary>

```python
@pytest.mark.parametrize("value", [0, "", None, [], {}])
def test_falsy(value):
    assert not value
```

Five tests instead of one. A failure names the value, the other four still run, and one case can be re-run alone.

Two of the ids will be `value3` and `value4`, because `[]` and `{}` have no readable representation for an id, so `pytest.param([], id="empty-list")` is worth adding.

</details>

2. ▢ Why is this worse than two separate tests?

   ```python
   @pytest.mark.parametrize("raw, expected, error", [
       ("10", Decimal("10"), None),
       ("abc", None, "not a number"),
       ("", None, "empty"),
   ])
   def test_parse(raw, expected, error):
       if error:
           with pytest.raises(ValueError, match=error):
               parse(raw)
       else:
           assert parse(raw) == expected
   ```

<details markdown="1"><summary>Hint</summary>

Read the body and count how many claims it makes.

</details>

<details markdown="1"><summary>Check</summary>

The body has an `if`, which lesson 28 ruled out, and for the same reason: it is two tests. Each case carries a `None` for the fields it does not use, so a reader has to work out which half of the body applies. And a fourth column would be needed the moment one invalid input should raise a different exception type.

```python
@pytest.mark.parametrize("raw, expected", [("10", Decimal("10")), ("10.5", Decimal("10.5"))])
def test_parses_valid_numbers(raw, expected):
    assert parse(raw) == expected

@pytest.mark.parametrize("raw, message", [("abc", "not a number"), ("", "empty")])
def test_rejects_invalid_numbers(raw, message):
    with pytest.raises(ValueError, match=message):
        parse(raw)
```

</details>

3. ▢ How many tests does this collect, and is that a good idea?

   ```python
   @pytest.mark.parametrize("backend", ["sqlite", "postgres", "mysql"])
   @pytest.mark.parametrize("payload", [P1, P2, P3, P4])
   @pytest.mark.parametrize("mode", ["sync", "async"])
   def test_roundtrip(backend, payload, mode): ...
   ```

<details markdown="1"><summary>Check</summary>

24, the product of three, four and two.

Whether it is a good idea depends on independence. If every combination is meaningful and each is fast, 24 is fine and thorough. If some combinations cannot occur, such as a backend with no async driver, the list needs exclusions and the test grows an `if`, at which point splitting by dimension is clearer.

The other question is runtime. If each case starts a container, 24 cases is minutes, and the honest design is one parametrised backend fixture with the payloads inside a single test.

</details>

4. ▢ An `xfail`-marked case starts passing. What does the suite report, and what should it?

<details markdown="1"><summary>Check</summary>

By default `XPASS`, which is not a failure, so the run stays green and nobody notices the mark is now a lie. The case remains marked as broken indefinitely, and a later regression re-breaks it silently.

With `strict=True` on the mark, or `xfail_strict = true` in `[tool.pytest.ini_options]`, an unexpected pass fails the run, which is what forces someone to delete the mark. Make it the project-wide default.

</details>

5. ▢ Every member of an `Enum` should be handled. Write the test that fails when a member is added.

<details markdown="1"><summary>Check</summary>

```python
@pytest.mark.parametrize("state", list(State), ids=lambda s: s.name)
def test_every_state_has_a_label(state):
    assert label(state)
```

`list(State)` is evaluated at collection time, so adding a member adds a test automatically, and the new one fails until `label` handles it.

This is the runtime companion to `assert_never` from lesson 16: the checker catches an unhandled member in a `match`, and this catches one in a lookup table the checker cannot see into, such as a dict keyed by member.

</details>

6. ▢ A colleague parametrises a `conftest.py` fixture with two database backends. What is the cost, and when is it right?

<details markdown="1"><summary>Check</summary>

Every test that requests the fixture, directly or transitively, now runs twice, including the ones testing pure logic that has nothing to do with storage. The suite roughly doubles in the worst case, and the second run of most tests proves nothing.

It is right when the fixture is requested only by contract tests that must hold for both implementations, which usually means moving it out of the top-level `conftest.py` into `tests/storage/conftest.py`, so its scope is the directory that cares.

</details>

## Real-world reps

- [ ] Find a test with a loop over inputs and parametrise it. Break one input on purpose and read the new failure output.
- [ ] Look for any parametrised test whose body has an `if` on one of its parameters, and split it.
- [ ] Add `xfail_strict = true` to your pytest configuration and see whether anything turns red. Every `XPASS` was a stale mark.
- [ ] Parametrise one test over `list(SomeEnum)` and add a member to confirm the suite fails.
- [ ] Tomorrow: check your CI output for ids like `value3` or `payload1`, and give those cases names.

## Going further

- [How to parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html): the decorator, stacking, and parametrised fixtures
- [`pytest.param`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param): ids and per-case marks
- [Skip and xfail](https://docs.pytest.org/en/stable/how-to/skipping.html): `strict`, `reason`, and conditional skipping
- [Parametrising fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#parametrizing-fixtures): `params` and `request.param`
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
