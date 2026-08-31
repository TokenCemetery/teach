---
title: 29. Fixtures
description: Setup as a dependency the test asks for, with teardown that runs whatever happens
type: lesson
---

# Lesson 29. Fixtures

**Mission link:** The mission asks for fixtures instead of copied test bodies. A fixture is a function a test requests by name, which makes setup composable, scoped, and cleaned up on every path out, and which is the same idea as the context manager from lesson 11.
**Primary source:** [pytest documentation, How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
**Prerequisites:** [Lesson 11](0011-context-managers.md), [Lesson 28](0028-what-a-test-asserts.md)

## Warm-up

1. ▢ Lesson 11: what does a `yield` inside a `@contextmanager` separate?

<details markdown="1"><summary>Check</summary>

Setup from teardown, with the caller's block running at the `yield`. A fixture uses exactly the same shape.

</details>

2. ▢ Three tests need the same five lines of setup. What is wrong with copying them?

<details markdown="1"><summary>Check</summary>

The fourth test copies them slightly differently, and then a change to the setup has to be found in four places. This lesson is the alternative.

</details>

## Know this

A fixture is a function; a test asks for it by naming a parameter:

```python
import pytest

@pytest.fixture
def order():
    return Order(id=1, amount=Decimal("100"), country="GB")

def test_discount_reduces_the_amount(order):
    order.apply_discount(Decimal("10"))
    assert order.amount == Decimal("90")
```

pytest matches the parameter name to a fixture, calls it, and passes the result. Each test gets a **fresh** call, so the mutation above cannot leak into the next test.

### Teardown with `yield`

```python
@pytest.fixture
def temp_table(connection):
    connection.execute("CREATE TEMP TABLE orders (id bigint)")
    yield "orders"
    connection.execute("DROP TABLE orders")
```

Everything before the `yield` is setup, the value yielded is what the test receives, and everything after is teardown, which runs whether the test passed, failed, or raised. Unlike lesson 11, no `try/finally` is needed: pytest guarantees the teardown.

Fixtures compose by requesting each other, as `temp_table` requests `connection`. That is the mechanism that replaces inheritance-based test base classes: a fixture needs three things, so it names three fixtures.

### Scope

```python
@pytest.fixture(scope="session")
def db():
    print("create db")
    yield "db"
    print("drop db")
```

| Scope | Created once per |
|---|---|
| `function` (default) | test |
| `class` | test class |
| `module` | file |
| `package` | package directory |
| `session` | whole run |

Verified ordering, with a session `db`, a function `order` that requests it, and an autouse `clock`:

```text
[session] create db
[autouse] freeze clock
[function] make order
.          [function] clean order
[autouse] freeze clock
[function] make order
.          [function] clean order
...
[session] drop db
```

The expensive thing is built once; the per-test thing is rebuilt each time.

The rule that keeps this safe: **a wider scope must be immutable, or reset by a narrower fixture.** A session-scoped database connection is fine. A session-scoped `Order` that one test mutates makes the suite order-dependent, which shows up as tests that pass alone and fail together, and it is the hardest test failure to diagnose.

### `conftest.py`

Fixtures in `tests/conftest.py` are available to every test under that directory with no import. Nested directories can have their own, and the nearest one wins, which is how a subdirectory of integration tests overrides a fake with a real client.

Nothing else belongs in `conftest.py`. Helper functions go in an ordinary module the tests import, because a `conftest.py` full of utilities is a file nobody can grep for.

### The built-in fixtures worth knowing

| Fixture | Gives |
|---|---|
| `tmp_path` | a fresh `pathlib.Path` directory, named after the test |
| `monkeypatch` | attribute, item and environment patching, undone automatically |
| `capsys` | captured `stdout` and `stderr` |
| `caplog` | captured log records, with levels |
| `request` | metadata about the test asking, used for indirect parametrisation |

`monkeypatch` is the one that removes the most hand-written teardown:

```python
def test_uses_test_mode(monkeypatch):
    monkeypatch.setenv("MODE", "test")
    assert config.mode() == "test"

def test_env_is_clean():
    assert "MODE" not in os.environ        # undone, verified
```

It also has `setattr`, `delattr`, `setitem`, `delitem` and `chdir`, all reverted at the end of the test. Anything patched by hand needs a `try/finally` and will eventually be forgotten.

`tmp_path` replaces every hand-rolled temporary directory, and pytest keeps the last few runs' directories on disk, which is useful when a test fails on file content.

### Factory fixtures

When tests need several objects, or objects with different fields, return a **function**:

```python
@pytest.fixture
def make_order():
    def _make(**kwargs):
        defaults = {"id": 1, "amount": Decimal("100"), "country": "GB"}
        return Order(**(defaults | kwargs))
    return _make

def test_vat_differs_by_country(make_order):
    gb = make_order(country="GB")
    de = make_order(country="DE")
    assert gb.vat() != de.vat()
```

This is the most useful fixture pattern in practice. Each test states only the fields it cares about, so a test about countries does not mention amounts, and adding a required field to `Order` changes one line instead of forty.

### `autouse`, sparingly

```python
@pytest.fixture(autouse=True)
def freeze_clock():
    ...
```

An autouse fixture runs for every test in its scope without being requested. Legitimate uses are narrow: resetting global state the code under test insists on having, freezing time, and failing a test that emits a warning. Everything else makes tests depend on setup that is invisible in their signature, which is the property that makes a suite hard to reason about. A test that requests what it needs can be read alone.

### Fixture or plain function?

If setup has no teardown, no scope, and no composition, a plain helper function called explicitly is clearer:

```python
def test_totals():
    order = an_order(amount=Decimal("100"))     # just a function
```

The fixture earns its place when there is cleanup, when the scope should be wider than one test, when several fixtures compose, or when a built-in like `tmp_path` is involved.

## Practice

1. ▢ Why does the second test fail, and what is the fix?

   ```python
   @pytest.fixture(scope="session")
   def order():
       return Order(id=1, amount=Decimal("100"))

   def test_discount(order):
       order.apply_discount(Decimal("10"))
       assert order.amount == Decimal("90")

   def test_amount_unchanged(order):
       assert order.amount == Decimal("100")
   ```

<details markdown="1"><summary>Hint</summary>

How many `Order` objects exist across the two tests?

</details>

<details markdown="1"><summary>Check</summary>

One. The session scope means both tests share it, so the first test's mutation is visible to the second, which sees `90`.

Worse than the failure is the symptom: `pytest tests/test_x.py::test_amount_unchanged` passes alone, and the same test fails in a full run. Any test that passes alone and fails in company is shared mutable state, and a fixture scope is the first place to look.

Fix: drop the scope, so it defaults to `function`. Session scope is for expensive immutable things.

</details>

2. ▢ Rewrite with `monkeypatch` and say what improves.

   ```python
   def test_reads_mode():
       original = os.environ.get("MODE")
       os.environ["MODE"] = "test"
       try:
           assert config.mode() == "test"
       finally:
           if original is None:
               del os.environ["MODE"]
           else:
               os.environ["MODE"] = original
   ```

<details markdown="1"><summary>Check</summary>

```python
def test_reads_mode(monkeypatch):
    monkeypatch.setenv("MODE", "test")
    assert config.mode() == "test"
```

Nine lines become two, and the restore is no longer something a future edit can break. It also cannot be skipped by an early `return` or a second `assert` above the `try`, which is the failure mode of hand-written teardown.

</details>

3. ▢ Choose the scope.

   - a) A Docker container running a database for the whole suite
   - b) An `Order` object each test mutates
   - c) A parsed configuration file, read-only
   - d) A temporary directory holding files one test writes

<details markdown="1"><summary>Check</summary>

- a) `session`. Expensive, and shared safely if each test uses its own schema or transaction.
- b) `function`. Mutable, so anything wider makes the suite order-dependent.
- c) `session` or `module`, since read-only is the condition that makes a wide scope safe. Prefer returning something immutable, a frozen dataclass from lesson 12, so "read-only" is enforced rather than assumed.
- d) `function`, and use the built-in `tmp_path`, which already is one.

</details>

4. ▢ A `conftest.py` grows to 400 lines with 30 fixtures. Name the specific problems and the fix.

<details markdown="1"><summary>Check</summary>

Problems: a test's signature no longer tells you where its setup comes from, since `conftest.py` requires no import; fixtures that are used by one test look shared; nobody deletes anything, because grep cannot prove a fixture is unused; and if some are autouse, tests depend on setup they never mention.

Fixes, in order: move single-use fixtures into the test file that uses them; move helper functions into an ordinary importable module; split `conftest.py` by directory, so integration fixtures live under `tests/integration/`; and convert autouse fixtures to explicitly requested ones wherever the test genuinely needs them.

</details>

5. ▢ Convert to a factory fixture, then say what a new required `currency` field costs in each version.

   ```python
   @pytest.fixture
   def gb_order():
       return Order(id=1, amount=Decimal("100"), country="GB")

   @pytest.fixture
   def de_order():
       return Order(id=2, amount=Decimal("100"), country="DE")

   @pytest.fixture
   def large_gb_order():
       return Order(id=3, amount=Decimal("10000"), country="GB")
   ```

<details markdown="1"><summary>Check</summary>

```python
@pytest.fixture
def make_order():
    def _make(**kwargs):
        defaults = {"id": 1, "amount": Decimal("100"), "country": "GB"}
        return Order(**(defaults | kwargs))
    return _make
```

Callers become `make_order(country="DE")` and `make_order(amount=Decimal("10000"))`, which state exactly what the test is about.

A new required field costs one line in the factory version, added to `defaults`. In the original it costs three fixtures now, and one more for every fixture added between now and then, and each edit is a chance to make them inconsistent.

</details>

6. ▢ Argue both sides of an autouse fixture that resets a module-level cache before every test.

<details markdown="1"><summary>Check</summary>

For: the cache is global state the code insists on having, every test needs it clean, and requiring 200 tests to request a fixture that says nothing about what they test is noise. Forgetting it in one new test produces a failure that looks unrelated.

Against: the tests now pass because of setup none of them mention, so a reader cannot tell why one works, and running a single test through an editor's runner behaves differently from importing the module by hand.

The resolution is usually to attack the cause: a module-level cache is the thing making tests interdependent, and lesson 13 said as much. If the cache can become an attribute of an object the test constructs, both the autouse fixture and the argument disappear.

</details>

## Real-world reps

- [ ] Find three tests in a suite you know with the same setup lines and extract one factory fixture. Then check whether each test got shorter and clearer, or just shorter.
- [ ] Run your suite with `-p no:randomly` if you use random ordering, then with random ordering. Any test that only passes one way is sharing state.
- [ ] Grep for `os.environ[` and `setattr(` inside tests and convert each to `monkeypatch`.
- [ ] Look at every `scope="session"` and `scope="module"` fixture you have and ask whether anything mutates the value.
- [ ] Tomorrow: run one failing test alone and then in the full suite. If the results differ, the fixture scopes are where to look.

## Going further

- [How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html): requesting, composing, `yield` teardown, and factories
- [Fixture scopes](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session): the five scopes and their instantiation order
- [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html): every patching method, and what each one undoes
- [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html): the temporary directory fixture and its retention policy
- [conftest.py](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files): the discovery rules for nested directories
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
