---
title: 40. Designing an API
description: The signature is the contract, and everything observable becomes one whether you meant it or not
type: lesson
---

# Lesson 40. Designing an API

**Mission link:** Everything in the arc so far was about making code correct. This stage is about the part you cannot change later: what callers can see, what they will depend on, and what you have promised without noticing.
**Primary source:** [PEP 8, Designing for Inheritance and Public Interfaces](https://peps.python.org/pep-0008/)
**Prerequisites:** [Lesson 15](0015-annotations-are-claims.md), [Lesson 20](0020-building-a-package.md), [Lesson 24](0024-dunder-methods.md)

## Warm-up

1. ▢ Lesson 15 gave a rule about parameter and return types. State it.

<details markdown="1"><summary>Check</summary>

Take the general type, return the concrete one: `Iterable` in, `list` out. It widens who can call you and tells callers what they got.

</details>

2. ▢ Lesson 12 asked which shape a bundle of data deserves. Which shape can gain a field without breaking callers?

<details markdown="1"><summary>Check</summary>

A dataclass with keyword arguments. A tuple cannot, because positions are the interface.

</details>

## Know this

### The signature is the contract

```python
def send(
    message: str,
    *,
    retries: int = 3,
    timeout: float = 5.0,
    on_failure: Callable[[Exception], None] | None = None,
) -> Receipt:
```

Five decisions are visible there, and each one is a promise.

**Keyword-only after the first one or two.** `*` in the signature forces the rest to be named at the call site, which makes `send(msg, 3, 5.0)` impossible to write and impossible to misread. It also means you can reorder, rename with a shim, or insert a parameter without breaking anyone. Positional parameters are a promise about order, and order is the hardest thing to change.

**Positional-only where the name is noise.** `def get(self, key, /, default=None)` says the first parameter's name is not part of the API, so you may rename it. Use it for the one or two arguments whose meaning is obvious from position.

**Defaults that are values, not behaviour.** `timeout: float = 5.0` is a documented default. `timeout: float | None = None` meaning "use the global config" is a second code path hidden in a default.

**An annotated return.** `-> Receipt` tells callers what they can do next, and it is verified, which a docstring is not.

**No boolean parameters that select behaviour.** `send(msg, validate=True)` is two functions in one signature; two functions with names are clearer, and the checker can then type each properly.

### Everything observable becomes an interface

The uncomfortable rule, usually attributed to Hyrum Wright: with enough users, every observable behaviour of your system will be depended on by somebody, regardless of what you documented.

Things people depend on that are not in the signature:

| They depend on | You thought it was |
|---|---|
| the exact exception type raised | an implementation detail |
| the wording of an error message | a message |
| the order of a returned list or dict | incidental |
| a `_private` attribute | private |
| timing, and whether a call is fast | not a promise |
| the concrete type, not the protocol | "returns a sequence" |
| the `repr` of an object | debugging output |

You cannot prevent all of it. You can decide deliberately about the top four, because they are cheap to get right and expensive to change:

- **Exceptions are part of the API.** Document what you raise, give your package one base exception from lesson 10, and translate anything from a dependency, or the dependency's exception type becomes yours.
- **Order is part of the API** if you return a list. If it is not meant to be, say so in the docstring, and consider returning a `set` or `frozenset` so the promise is visible in the type.
- **Private means underscore, and means it.** A published attribute without one is public whatever the docs say.
- **A stable `repr`** is worth writing once, per lesson 24, because it lands in other people's logs.

### What to expose

```python
# shop/__init__.py
from shop.orders import Order, OrderError, place_order

__all__ = ["Order", "OrderError", "place_order"]
```

The package's public surface is the smallest set that lets callers do the job. Everything else is an underscore, an internal module, or absent. Two arguments for keeping it small: every public name is a thing you cannot rename, and a small surface is documentable in one screen, which is the difference between a library people use correctly and one they cargo-cult.

`__all__` states the intention for `import *` and for tooling. It is not enforcement, and combined with `no_implicit_reexport` from the strict checker settings in lesson 16, it becomes something a tool can check.

### The shapes that age well

| Instead of | Prefer |
|---|---|
| a class with one method | a function |
| a function with eight parameters | a frozen dataclass of options |
| `**kwargs` forwarded blindly | explicit parameters, or `Unpack[TypedDict]` |
| returning `None` on failure | raising, or returning an explicit result type |
| returning a tuple of four values | a `NamedTuple` or dataclass, so fields have names |
| a boolean flag argument | two named functions |
| inheritance for the caller to extend | a callback, or a `Protocol` they implement |
| a module-level singleton | an object the caller constructs and holds |

The last one is the largest in practice. A module-level client, connection, or config object cannot be configured twice, cannot be replaced in a test without patching, and ties its lifetime to the process. Handing the caller a constructor costs one line and removes all three problems, which is lesson 31's argument arriving as a design rule.

### Documenting the contract

```python
def place_order(items: Sequence[Item], *, customer: CustomerId) -> Order:
    """Create and persist an order.

    Args:
        items: at least one item; quantities must be positive.
        customer: must exist, or CustomerMissing is raised.

    Returns:
        The persisted order, with `id` assigned.

    Raises:
        EmptyOrder: if `items` is empty.
        CustomerMissing: if `customer` does not exist.
    """
```

The types are in the annotations, so the docstring carries what annotations cannot: preconditions, what is raised and when, side effects, and whether the result is ordered. A docstring that repeats the types is maintenance with no benefit.

`doctest` is worth knowing here: an example in a docstring that is actually executed cannot drift, and it doubles as the first test.

## Practice

1. ▢ Rewrite this signature, and name each change.

   ```python
   def export(data, True, "csv", None, 100):
       ...
   # def export(data, headers, format, path, chunk):
   ```

<details markdown="1"><summary>Check</summary>

```python
def export(
    data: Iterable[Row],
    *,
    include_headers: bool = True,
    format: Literal["csv", "json"] = "csv",
    path: Path | None = None,
    chunk_size: int = 100,
) -> int:
```

Changes: keyword-only, so no call site can be misread or broken by reordering; `Iterable` in, so a generator works; `Literal` for the format, so a typo is a checker error rather than a runtime one; `include_headers` renamed so the boolean reads at the call site; `chunk_size` named for its unit; and an annotated return, since a caller wants to know how many rows were written.

`path: Path | None = None` still hides a second behaviour, writing to standard output. Two functions, `export_to_path` and `export_to_stream`, would be honest, and whether that is worth it depends on how different the bodies are.

</details>

2. ▢ Which of these can you change in a patch release without breaking callers?

   - a) The name of the first positional parameter
   - b) Adding a keyword-only parameter with a default
   - c) The exception type raised on invalid input
   - d) The order of a returned list
   - e) Adding a field to a returned frozen dataclass

<details markdown="1"><summary>Hint</summary>

For each, imagine the call site or the assertion that breaks.

</details>

<details markdown="1"><summary>Check</summary>

- a) No, unless it is positional-only with `/`. Someone passes it by name.
- b) Yes. This is why keyword-only with a default is the safe way to extend.
- c) No. `except ValueError` in a caller stops catching, and the failure becomes an unhandled exception in production.
- d) No, in practice. Nothing documents it and everyone's tests assert it. Hyrum's law is about exactly this.
- e) Usually yes for reading, and no if any caller does `astuple`, unpacks it positionally, or compares whole instances in a test.

</details>

3. ▢ Why is a module-level client worse than a constructor?

   ```python
   # shop/api.py
   client = HttpClient(base_url=os.environ["API_URL"], timeout=5)

   def fetch(order_id): return client.get(f"/orders/{order_id}")
   ```

<details markdown="1"><summary>Check</summary>

Four concrete problems, all from lesson 13's "a module runs once".

It reads the environment at **import** time, so importing the module fails without the variable set, including in a test collection run and in a documentation build. It cannot be configured twice, so a caller talking to two environments is stuck. Replacing it in a test requires patching a module attribute, per lesson 31, rather than passing an argument. And its lifetime is the process, so connections are never closed and there is no shutdown path.

```python
class ShopApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def fetch(self, order_id: OrderId) -> Order: ...
```

The caller constructs it, configures it, closes it, and passes a fake in tests with no patching. One extra line at the call site.

</details>

4. ▢ A function returns `None` when the order is not found. Give two better designs and when each applies.

<details markdown="1"><summary>Check</summary>

**Raise.** `get_order(id) -> Order`, raising `OrderMissing`. Right when absence is exceptional and the caller almost always has an order: the type is then honest, and a caller who forgets gets a loud failure rather than an `AttributeError` on `None` three frames later.

**Return an explicit optional.** `find_order(id) -> Order | None`. Right when absence is ordinary, and lesson 16's narrowing then forces every caller to handle it, verified by the checker.

The convention that makes both readable is naming: `get_` raises, `find_` returns optional. Offering both is fine and is what several standard library types do; what is not fine is `-> Order` that can return `None`, which lesson 15 called the worst kind of annotation.

</details>

5. ▢ A library raises `KeyError` from its public function, which internally is a dict lookup. Two years later the storage becomes a database. What breaks, and what should have been done?

<details markdown="1"><summary>Check</summary>

Every caller's `except KeyError`. The database raises something else, so the handlers stop catching and the failure becomes an unhandled exception in production, in code nobody touched.

The exception type was part of the API from the first release, and it leaked the implementation. Lesson 10's pattern is the fix, applied at the boundary from day one:

```python
class StoreError(Exception): ...
class OrderMissing(StoreError): ...

def get_order(order_id):
    try:
        return _orders[order_id]
    except KeyError as exc:
        raise OrderMissing(order_id) from exc
```

Now the storage can change freely, and callers catch a name that belongs to the library rather than to its internals.

</details>

6. ▢ A colleague argues that keyword-only parameters are noise, since the team knows the argument order. Answer them.

<details markdown="1"><summary>Check</summary>

The team is not the only reader, and the future is not the present. Three specifics.

Two same-typed positional parameters can be swapped, silently, and a checker cannot see it: `transfer(source, target)` and `transfer(target, source)` both type-check. Keyword-only makes it a syntax error to omit the names.

Positional order is the part of a signature you can never change. Once released, inserting a parameter or reordering means a new function name, whereas a keyword-only parameter can be added at any time.

And the call site reads better without the reader going to the definition: `send(msg, retries=5)` says what 5 is; `send(msg, 5)` requires a lookup.

The honest concession: for one or two obvious arguments, positional is right, and `/` says so explicitly. The rule is not "everything keyword", it is "everything after the obvious ones".

</details>

## Real-world reps

- [ ] Take the widest signature in code you own and count how many parameters could be keyword-only without breaking a caller. Change those.
- [ ] List every exception your package's public functions can raise, including from dependencies. Anything not one of yours is a leak.
- [ ] Write out your package's public surface from `__all__` and ask whether each name has to be public.
- [ ] Find a module-level client, connection or config object and try turning it into a constructor argument. Note how many tests stop patching.
- [ ] Tomorrow: write the docstring for one public function stating what it raises, and see whether you can answer that question without reading the body.

## Going further

- [PEP 8, Designing for Inheritance and Public Interfaces](https://peps.python.org/pep-0008/): the naming and privacy conventions Python reviewers cite
- [PEP 570, Positional-Only Parameters](https://peps.python.org/pep-0570/): why `/` exists and when to use it
- [PEP 3102, Keyword-Only Arguments](https://peps.python.org/pep-3102/): the rationale for `*` in a signature
- [PEP 257, Docstring Conventions](https://peps.python.org/pep-0257/): the shape of a docstring
- [`doctest`](https://docs.python.org/3/library/doctest.html): examples in a docstring that cannot drift
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
