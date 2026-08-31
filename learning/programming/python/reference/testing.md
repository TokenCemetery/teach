---
title: Testing
description: Fixture scopes, parametrisation forms, which double to reach for, and reading a coverage report
type: reference
---

# Testing

Lookup sheet for stage 5. The question it exists to answer: **what should this test do, and why is the suite not telling me the truth?**

## Anatomy

```python
def test_rejects_negative_discount():          # name states the behaviour
    order = an_order(amount=Decimal("100"))    # arrange

    with pytest.raises(ValueError, match="must not be negative"):
        order.apply_discount(Decimal("-5"))    # act and assert
```

- One behaviour per test, not one assertion.
- No `if` and no loop in the body: that is a second implementation of the code under test.
- Expected values as literals, even when repetitive.
- `pytest.raises` always narrowed, with `match=` or an assertion on `exc_info.value`.
- A message argument on `assert` **replaces** the introspection. Omit it.

## Command lines

| Command | Does |
|---|---|
| `pytest -q` | one line per file |
| `pytest -vv` | full diffs, no truncation |
| `pytest -k discount` | tests whose name matches |
| `pytest -x` | stop at the first failure |
| `pytest --lf` | only what failed last time |
| `pytest --durations=10` | the ten slowest tests |
| `pytest "f.py::test_x[case-id]"` | one parametrised case |

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
xfail_strict = true
pythonpath = ["src"]        # or install the package editable instead
```

`-ra` surfaces skips and xfails. `--strict-markers` makes a misspelled marker an error. `xfail_strict` makes an unexpected pass a failure, which is what stops stale marks accumulating.

## Fixtures

```python
@pytest.fixture
def temp_table(connection):          # composes by requesting another fixture
    connection.execute("CREATE TEMP TABLE orders (id bigint)")
    yield "orders"                   # teardown runs however the test ends
    connection.execute("DROP TABLE orders")
```

| Scope | Created once per | Safe if |
|---|---|---|
| `function` (default) | test | always |
| `class` | test class | nothing mutates it |
| `module` | file | nothing mutates it |
| `package` | directory | nothing mutates it |
| `session` | run | immutable, or reset by a narrower fixture |

**A test that passes alone and fails in the suite is shared mutable state.** Check fixture scopes first, then module-level globals.

| Built-in | Gives |
|---|---|
| `tmp_path` | a fresh directory, named after the test |
| `monkeypatch` | `setattr`, `setitem`, `setenv`, `chdir`, all undone automatically |
| `capsys` | captured stdout and stderr |
| `caplog` | captured log records |
| `request` | metadata, for `request.param` |

Factory fixture, the highest-value pattern:

```python
@pytest.fixture
def make_order():
    def _make(**kwargs):
        return Order(**({"id": 1, "amount": Decimal("100"), "country": "GB"} | kwargs))
    return _make
```

`conftest.py` fixtures are available without import, nearest directory wins. Put nothing else in it. Use `autouse` only for global state, frozen time, or warning capture.

## Parametrisation

```python
@pytest.mark.parametrize("country, expected", [
    pytest.param("GB", 0.20, id="united-kingdom"),
    pytest.param("ZZ", 0.0, id="not-implemented",
                 marks=pytest.mark.xfail(strict=True, reason="rate table incomplete")),
])
def test_vat_rate(country, expected): ...
```

- Each case is a separate test: named, individually re-runnable, and a failure does not stop the others.
- The failure output prints the arguments above the body.
- Ids come from the values; containers get useless ids like `value3`, so name those with `pytest.param`.
- Stacking decorators produces the cartesian product. Two lists of five is 25 tests.
- `ids=lambda c: c.name` with a frozen dataclass per case beats a tuple of six fields.
- `list(SomeEnum)` as the parameter list makes a new member fail the suite.

Worth parametrising: lookup tables, boundaries, the falsy set, formats that must all parse, inputs that must all be rejected, every enum member.

Not worth it: a parameter that changes which behaviour is tested. If the body needs `if expected_error:`, it is two tests.

## Test doubles

| Kind | Is |
|---|---|
| dummy | passed to satisfy a signature, never used |
| stub | returns canned answers |
| fake | a real, simplified, working implementation |
| spy | records calls and still does the real thing |
| mock | records calls, and the test asserts on them |

**Patch where the name is used, not where it is defined.** Verified:

```python
# report_from.py did:  from pkg.clock import now
patch("pkg.clock.now", ...)          # no effect on report_from
patch("pkg.report_from.now", ...)    # works

# report_mod.py did:   from pkg import clock
patch("pkg.clock.now", ...)          # works
```

Importing the module rather than the name makes the target stable.

**Use `autospec`.** A bare `Mock` accepts any attribute, any arity, any arguments:

```python
gateway = create_autospec(Gateway, instance=True)
gateway.charge(10)                # TypeError: missing a required argument: 'currency'
gateway.chrage(10, "GBP")         # AttributeError: Mock object has no attribute 'chrage'
gateway.charge(10, "GBP", "x")    # TypeError: too many positional arguments
```

| Replace | Leave alone |
|---|---|
| network, payment and email providers | pure functions |
| the clock, randomness, generated ids | dicts, lists, dataclasses |
| slow or rate-limited third-party services | your own domain logic |
| the filesystem, when `tmp_path` will not do | anything already fast and deterministic |

Do not mock what you do not own: wrap it in an interface you own, and fake that. More than two patches in a unit test is a statement about the design, not the test.

## Properties

```python
@given(st.text(), st.integers(min_value=0, max_value=50))
def test_truncate_respects_limit(s, n):
    assert len(truncate(s, n)) <= n
```

| Shape | Assertion |
|---|---|
| round trip | `decode(encode(x)) == x` |
| idempotence | `f(f(x)) == f(x)` |
| invariant | a bound that must always hold |
| oracle | fast implementation agrees with the obvious slow one |
| metamorphic | a relation between two calls |

- Put preconditions in the strategy (`min_size=1`), not in `assume`; heavy filtering raises `FailedHealthCheck`.
- `@example(...)` pins a counterexample the search found, permanently.
- `st.from_type(Order)` works on an annotated dataclass, so a typed domain needs almost no strategy code.
- Defaults are hostile on purpose: `st.text()` yields empty and non-Latin strings, `st.floats()` yields `nan` and `-0.0`.
- Failing examples are cached in `.hypothesis/`, so a local failure reproduces and a fresh CI container may not.
- Keep examples too: properties find bugs, examples document intent.

## Coverage

```text
Name                  Stmts   Miss Branch BrPart  Cover   Missing
src/shop/pricing.py      12      5      6      1    56%   8-11, 14
```

```toml
[tool.coverage.run]
branch = true
source = ["src"]
```

`branch = true` or the number is misleading: an `if` with no `else` counts as covered from one path. `source` or a module no test imports is absent from the report entirely.

**100 per cent proves nothing.** Verified: three parametrised tests calling a function with no assertion reach 100 per cent statements and branches while the function returns double what it should.

| The number is good for | Not for |
|---|---|
| the `Missing` column: what never ran | proving correctness |
| coverage of the lines a change touched | a CI target, which produces assertion-free tests |
| finding dead code | comparing teams or projects |
| a ratchet that forbids going down | a percentage in a report |

To find out whether tests detect anything: change an operator and see what fails; write the regression test before the fix; or run mutation testing on one module.

## Flaky tests, in diagnostic order

1. Run it alone, repeatedly. Passes alone, fails together: shared state, so check fixture scopes.
2. Randomise test order. Order-dependent confirms it.
3. Look for real time: `sleep`, timeouts, `now()`, cache expiry.
4. Look for unordered data compared as ordered: sets, queries without `ORDER BY`, directory listings.
5. Look for concurrency in the code under test. Then the code has a race and the test found it.

## Layers

| Layer | Answers | Should be |
|---|---|---|
| unit | does this function behave? | nearly all, milliseconds each |
| integration | do the pieces talk to a real database or service correctly? | few, and genuinely real |
| end to end | does the system do the user's task? | very few |

An integration test whose collaborators are all mocks is a unit test of the wiring. Name it as one.

## Sources

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)
- [`unittest.mock`, Where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch)
- [Coverage.py](https://coverage.readthedocs.io/en/latest/)
