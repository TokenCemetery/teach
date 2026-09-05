---
title: Typing
description: Current spellings, narrowing forms, error codes, and which shape to use at a boundary
type: reference
---

# Typing

Lookup sheet for stage 3. The question it exists to answer: **what do I write here, and why is the checker still unhappy?**

## Spellings

| Write | Not | Since |
|---|---|---|
| `list[int]`, `dict[str, int]`, `set[str]`, `tuple[int, ...]` | `typing.List`, `Dict`, `Set`, `Tuple` | 3.9 |
| `int \| None` | `Optional[int]` | 3.10 |
| `int \| str` | `Union[int, str]` | 3.10 |
| `type Rows = list[str]` | `Rows: TypeAlias = list[str]` | 3.12 |
| `def f[T](x: T) -> T` | module-level `T = TypeVar("T")` | 3.12 |
| `-> Self` | `-> "SameClass"` | 3.11 |
| `Callable[[int, str], bool]` | | |

Annotations are evaluated lazily from Python 3.14 (PEP 649). Before that they ran at definition time, so a forward reference needed quoting or `from __future__ import annotations`.

## Parameter and return types

| Body does | Parameter |
|---|---|
| iterates once | `Iterable[T]` |
| indexes, slices, `len` | `Sequence[T]` |
| looks keys up | `Mapping[K, V]` |
| appends or assigns | `MutableSequence[T]`, or a concrete `list[T]` |

Take the general type, return the concrete one. `list` and `dict` are **invariant**: `list[int]` is not a `list[object]`, because the callee could append. `Sequence` and `Iterable` are covariant and safe.

![Two chains of four steps. On the left, a list[int] seen as list[object] lets the callee append a str, leaving the caller's list[int] holding one. On the right, the same substitution with Sequence, where there is no append to call.](images/why-list-is-invariant.svg)

The rule is the second step, and the reason is the third. Nothing is wrong with calling a `list[int]` a `list[object]` until someone writes to it, which is exactly why the distinction lands on the mutable types and not on the read-only ones. Read the first column of the table above the same way: each row asks what the body does, because that is what decides which substitutions stay safe.

## Narrowing

| Form | Narrows |
|---|---|
| `if x is None: return` | removes `None` from the union below |
| `isinstance(x, C)` | to `C` in the true branch |
| `if not x: return` | also removes `0`, `""`, `[]`: rarely what was meant |
| `assert x is not None` | with a real runtime check |
| `match x: case ...` | per pattern, and can be made exhaustive |
| a function returning `TypeIs[C]` | both branches; needs `C` to be a subtype of the parameter |
| a function returning `TypeGuard[C]` | true branch only; no subtype requirement |
| `assert_never(x)` after the last case | proves exhaustiveness at check time |

`reveal_type(x)` prints what the checker believes. Remove it before committing.

## Error codes

| Code | Means | Fix |
|---|---|---|
| `union-attr` | attribute on a possibly-`None` value | narrow first |
| `arg-type` | wrong argument type | fix the call, or widen the parameter |
| `return-value` | return does not match the annotation | fix whichever lies |
| `assignment` | assigned type does not match the declared one | same |
| `no-untyped-def` | function has no annotations | annotate it |
| `no-any-return` | returning `Any` where a type was promised | narrow at the boundary |
| `attr-defined` | no such attribute on that type | typo, or the type is wrong |
| `typeddict-item` | unknown key, or wrong value type | read the suggestion |
| `unused-ignore` | a suppression that is no longer needed | delete it |
| `narrowed-type-not-subtype` | `TypeIs` target is not a subtype | use the covariant type |

## Escapes, ranked

1. Narrow, so the checker proves it.
2. Propagate the truth: change the annotation and let callers handle it.
3. `assert x is not None`: documents the assumption, checks it at run time.
4. `cast(C, x)`: no runtime check at all.
5. `# type: ignore[code]`: always with the code.
6. bare `# type: ignore`: hides the next error on that line too.

Turn on `warn_unused_ignores` so items 5 and 6 cannot rot.

## Strictness

`strict = true` in `[tool.mypy]` is a bundle. As of mypy 2.3 it enables:

```text
disallow-any-generics, disallow-subclassing-any, disallow-untyped-calls,
disallow-untyped-defs, disallow-incomplete-defs, check-untyped-defs,
disallow-untyped-decorators, warn-redundant-casts, warn-unused-ignores,
warn-return-any, no-implicit-reexport, strict-equality, extra-checks
```

Adoption: `strict = true` globally, then relax **individual flags** per module and delete the overrides one at a time.

```toml
[tool.mypy]
strict = true

[[tool.mypy.overrides]]
module = ["legacy.*"]
disallow_untyped_defs = false
check_untyped_defs = false
```

`strict = false` in a per-module override does nothing. Only individual flags work per module.

## Shapes at a boundary

| Shape | Use when | Runtime effect |
|---|---|---|
| frozen dataclass | the value stays in your program | a real class; construction can validate |
| `TypedDict` | it must remain a dict, for JSON or a library | none: it is a plain dict, `isinstance` raises |
| `Literal["a", "b"]` | a closed set fixed by an external protocol | none |
| `Enum` | a closed set your code owns | real singletons, iterable |
| `NewType("UserId", int)` | two values of the same primitive type must not be confused | none: the call is the identity |
| `Annotated[int, ...]` | attaching metadata a library reads | none by itself |
| `object` | genuinely unknown, and you intend to narrow | none |
| `Any` | nothing; it disables checking and propagates | none |

Convert once, at the edge, in a function that can raise.

## Protocol against abstract base class

| | Protocol | ABC |
|---|---|---|
| conformance | structural | must inherit |
| third-party classes | conform automatically | cannot |
| carries implementation | no | yes |
| `isinstance` | only with `@runtime_checkable`, and it checks **names only** | works |
| use for | a boundary you consume | a family you own |

Check `collections.abc` and `typing` before writing a new protocol: `Iterable`, `Iterator`, `Sequence`, `Mapping`, `Callable`, `SupportsIndex` already exist.

## Missing stubs

1. Install `types-<package>` if it exists.
2. Check for a `py.typed` marker inside the package.
3. Per-module `ignore_missing_imports = true`, never the global flag.

Shipping your own annotations requires a `py.typed` file **inside the built wheel** (PEP 561), or every consumer's checker ignores them.

## Sources

- [`typing`](https://docs.python.org/3/library/typing.html)
- [Static Typing with Python](https://typing.readthedocs.io/en/latest/)
- [mypy error codes](https://mypy.readthedocs.io/en/stable/error_code_list.html)
- [Type narrowing](https://mypy.readthedocs.io/en/stable/type_narrowing.html)
- [PEP 484](https://peps.python.org/pep-0484/), [PEP 544](https://peps.python.org/pep-0544/), [PEP 649](https://peps.python.org/pep-0649/), [PEP 695](https://peps.python.org/pep-0695/), [PEP 742](https://peps.python.org/pep-0742/)
