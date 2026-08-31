---
title: API and Review
description: Signature decisions, what counts as breaking, the review checklist, and where to find an answer
type: reference
---

# API and Review

Lookup sheet for stage 7. The question it exists to answer: **can I still change this, and what should I have looked at?**

## Signature decisions

```python
def send(
    message: str,
    *,
    retries: int = 3,
    timeout: float = 5.0,
) -> Receipt:
```

| Decision | Why |
|---|---|
| keyword-only (`*`) past the first one or two | order stops being a promise; parameters can be added or renamed |
| positional-only (`/`) where the name is noise | frees you to rename it |
| defaults that are values, not behaviour | `timeout=None` meaning "use the global" is a hidden code path |
| an annotated return | verified, unlike a docstring |
| two named functions instead of a boolean flag | each can be typed and documented properly |
| `Iterable` in, concrete `list` out | accepts more callers, tells them what they got |

## Things callers depend on that are not in the signature

Exception types, error message wording, the order of a returned sequence, `_private` attributes, timing, the concrete return type, and the `repr`. Decide deliberately about the first four: document what you raise, give the package one base exception, say whether order is guaranteed, and mean it when you use an underscore.

## Shapes that age well

| Instead of | Prefer |
|---|---|
| a class with one method | a function |
| eight parameters | a frozen dataclass of options |
| blindly forwarded `**kwargs` | explicit parameters, or `Unpack[TypedDict]` |
| returning `None` on failure | raise (`get_`), or an explicit optional (`find_`) |
| a tuple of four values | a `NamedTuple` or dataclass |
| a boolean flag argument | two named functions |
| a module-level client or config | an object the caller constructs |

## Breaking or not

| Breaking | Not breaking |
|---|---|
| removing or renaming anything public | adding a keyword-only parameter with a default |
| reordering, or keyword to positional | adding a new function or class |
| **narrowing** an accepted type | **widening** an accepted type |
| **widening** a return type (`X` to `X \| None`) | **narrowing** a return type |
| changing the exception raised | adding a subclass of one you already raise |
| changing the order of a returned sequence | adding a field to a returned dataclass, usually |
| raising `requires-python` | raising a dependency minimum, usually |

The two type rows are asymmetric and are commonly stated backwards. Accept more, return less.

## Deprecation

`DeprecationWarning` is **hidden unless attributed to `__main__`**. The default filters:

```python
('default', None, DeprecationWarning, '__main__', 0)
('ignore',  None, DeprecationWarning, None, 0)
```

Verified: the same warning from library code is invisible without `stacklevel`, and visible with `stacklevel=2`, because that attributes it to the caller.

```python
warnings.warn(
    "Order.total is deprecated and will be removed in shopkit 3.0; "
    "use Order.amount, which is a Decimal rather than a float.",
    DeprecationWarning,
    stacklevel=2,          # 3 from one level further in
)
```

```python
from warnings import deprecated       # Python 3.13; in warnings, not typing

@deprecated("use new_name instead; removed in 3.0")
def old_name(x): ...
```

The decorator is also read by type checkers, so it reaches users who never enable warnings.

A message needs four things: what is deprecated, when it goes, what replaces it, and what differs about the replacement.

| Shim | For |
|---|---|
| a `property` with `@deprecated` | a renamed attribute |
| re-export from the old path | a moved module |
| accept both parameters and warn | a renamed parameter |

Test it, and turn warnings into errors for yourself:

```python
with pytest.warns(DeprecationWarning, match="use total_amount"):
    order.total
```

```bash
python -W error::DeprecationWarning -m pytest
```

That flag finds your own code using your own deprecated API, and your code using your dependencies' deprecated APIs, which is the upgrade work you would otherwise meet in a hurry.

## Review, in order

1. Does it do what the description says?
2. Is there a test that would fail if the code were wrong?
3. Correctness, in Python's specific failure modes (below).
4. Interface: anything public is permanent.
5. Clarity.
6. Everything else, which should be automated.

### The checklist

| Look for | Lesson |
|---|---|
| mutable default argument, or mutable class attribute | 6, 22 |
| an iterator consumed twice, silently empty | 8 |
| `except Exception: pass`, or a bare `except` | 10 |
| a `try` whose second statement should be in `else` | 10 |
| cleanup without a context manager | 11 |
| `from x import y` for something patched in tests | 13, 31 |
| naive `datetime`, `bool(os.environ.get(...))` | 14, 18 |
| `-> X` on a function that can return `None` | 15 |
| `Any` at a boundary | 16, 18 |
| concrete `list[X]` parameter in a function that only iterates | 17 |
| a dict passed between layers with known keys | 12, 18 |
| `pytest.raises(Exception)`, or an assertion-free test | 28, 33 |
| a wide fixture scope that gets mutated | 29 |
| a bare `Mock` where shape matters | 31 |
| a discarded `submit` result | 35 |
| a lock held across I/O | 35 |
| check-then-act on shared state, or across an `await` | 34, 37 |
| a blocking call inside `async def` | 37 |
| `await` in a loop over independent work | 37 |
| `warnings.warn` without `stacklevel` | 41 |
| a module-level client, connection or config | 40 |
| an optimisation with no measurement | 39 |

Label every comment **defect**, **risk**, or **preference**. Say what is wrong, why it matters, and what you would do instead.

### Naming the cost of cleverness

| Construct | Precise cost |
|---|---|
| a metaclass | metaclass conflict with another library's base; invisible to the subclass's reader; tooling cannot see generated attributes |
| `__getattr__` forwarding | typos become silent; no attribute is checkable; `hasattr` lies |
| `exec` or `eval` on built strings | no checker, no linter, no debugger, an injection surface |
| classes generated at import | the class name is not greppable |
| monkeypatching a dependency | breaks on its next release, at a distance |
| a decorator without `functools.wraps` | tracebacks and help name the wrapper |
| deep inheritance for reuse | every base attribute is public API |

None of those costs is "hard to read", which is an opinion. Each is a fact, which ends the discussion.

## Where the answer is

| Question | Source |
|---|---|
| what does this do | the library reference |
| what does the language guarantee | the language reference |
| why is it like this | the PEP, then the Discourse thread |
| what does it actually do here | the source, via `inspect.getsource` |
| when did it change | What's New, and the version-status page |
| how fast is it | a measurement |

Reading a PEP: header (status, version), Abstract and Motivation, Rationale and Rejected Ideas, then Specification last. Rejected PEPs are often the most useful, because they explain why the obvious idea fails.

Sizes on CPython 3.14, for the argument that this is afternoon-sized: `contextlib` 814 lines, `functools` 1,165, `pathlib` 1,307, `dataclasses` 1,813.

A leading underscore in the standard library means what it means in your code. `re._compile` can change in a patch release.

## Judgment

Every rule states a cost. When the cost cannot occur, the rule does not bind.

| Rule | Exception when |
|---|---|
| never catch broadly | a per-item loop that logs the traceback and continues |
| never mutate a class attribute | a deliberate registry, marked `ClassVar` |
| no metaclasses | subclasses must be affected without opting in |
| always annotate | a private three-line helper |
| never `assert` for validation | an internal invariant, not caller-caused |
| frozen by default | the object's identity is its mutation over time |
| always lock | there is nothing shared, which is the better fix |
| measure before optimising | the change also makes the code simpler |
| deprecate before removing | one consumer, upgraded in lockstep |

Deciding order: what is reversible; cost of being wrong times likelihood; what does the code make impossible; who reads it and when.

Abstraction earns its place at the **second** case, not the anticipated one. Removing one nobody needed is easy; removing one people depend on is not.

Explaining a call, in three sentences: what you chose, what it costs, what would change your mind. The third is the one that gets omitted and the one that makes it reasoning rather than taste.

## Sources

- [PEP 8](https://peps.python.org/pep-0008/), [PEP 20](https://peps.python.org/pep-0020/), [PEP 257](https://peps.python.org/pep-0257/)
- [PEP 570](https://peps.python.org/pep-0570/), [PEP 3102](https://peps.python.org/pep-3102/)
- [`warnings`](https://docs.python.org/3/library/warnings.html), [PEP 702](https://peps.python.org/pep-0702/), [PEP 387](https://peps.python.org/pep-0387/)
- [Python Developer's Guide](https://devguide.python.org/), [Python HOWTOs](https://docs.python.org/3/howto/index.html)
- [`inspect`](https://docs.python.org/3/library/inspect.html)
