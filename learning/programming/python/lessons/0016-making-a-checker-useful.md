---
title: 16. Making a Checker Useful
description: Configuring strictness, reading the error codes, and narrowing instead of silencing
type: lesson
---

# Lesson 16. Making a Checker Useful

**Mission link:** A checker on default settings finds almost nothing and creates the impression the code is typed. The difference between decoration and verification is configuration plus the habit of fixing what it reports.
**Primary source:** [mypy documentation](https://mypy.readthedocs.io/en/stable/)
**Prerequisites:** [Lesson 15](0015-annotations-are-claims.md)

## Warm-up

1. ▢ Lesson 15: why does annotating two functions in a forty-function module find nothing?

<details markdown="1"><summary>Check</summary>

Unannotated functions are not checked inside and are treated as `Any` from outside, so types are lost at every boundary between the two annotated ones.

</details>

2. ▢ What is the honest annotation for a function that returns an order or nothing?

<details markdown="1"><summary>Check</summary>

`-> Order | None`. Annotating it `-> Order` makes the checker approve `find(1).amount`.

</details>

## Know this

Take this file, which contains four defects:

```python
@dataclass
class Order:
    id: int
    amount: float

def find(order_id: int) -> Order | None:
    return None

def show(order_id: int) -> str:
    order = find(order_id)
    return f"{order.amount:.2f}"      # 1

def untyped(x):
    return x.whatever() + 1           # 2

def wrong_arg() -> None:
    find("not-an-int")                # 3

def bad_return(order: Order) -> int:
    return order.amount               # 4
```

On default settings a checker reports three of them:

```text
sample.py:13: error: Item "None" of "Order | None" has no attribute "amount"  [union-attr]
sample.py:19: error: Argument 1 to "find" has incompatible type "str"; expected "int"  [arg-type]
sample.py:22: error: Incompatible return value type (got "float", expected "int")  [return-value]
```

Defect 2 is invisible, because `untyped` has no annotations. Under `--strict` it appears as `[no-untyped-def]`, and that is the whole argument for strictness: the default reports what it can prove, and it can prove little about code that made no claims.

### The error code is the useful part

Every message ends in a bracketed code. Learn these seven and most output becomes readable at a glance:

| Code | Means | Usual fix |
|---|---|---|
| `union-attr` | attribute used on a value that might be `None` | narrow first |
| `arg-type` | wrong type passed | fix the call, or widen the parameter |
| `return-value` | returned type does not match the annotation | fix whichever one is lying |
| `assignment` | assigned type does not match the declared one | same |
| `no-untyped-def` | function has no annotations | annotate it |
| `no-any-return` | returning `Any` from a function that promises a type | narrow at the boundary |
| `attr-defined` | attribute does not exist on that type | a typo, or the type is wrong |

`no-any-return` is the one worth watching, because it marks the exact place where checking silently stopped:

```python
def load(raw: str) -> dict[str, int]:
    return json.loads(raw)
```

```text
error: Returning Any from function declared to return "dict[str, int]"  [no-any-return]
```

The annotation is a promise nothing verified. Lesson 18 is about honouring it.

### Narrowing is the answer, not silencing

The checker follows control flow. Give it a test and it updates what it knows:

```python
def show(order_id: int) -> str:
    order = find(order_id)
    if order is None:
        return "missing"
    return f"{order.amount:.2f}"      # here, order is Order
```

| Narrowing form | Use |
|---|---|
| `if x is None: return` | the everyday one; put it first and keep the body flat |
| `isinstance(x, Order)` | a union of classes |
| `if not x: return` | careful: also excludes `0`, `""` and `[]`, from lesson 5 |
| `assert x is not None` | when it truly cannot be `None`, and you accept the runtime check |
| `match` with `case` | several shapes, and it can be made exhaustive |

`reveal_type(x)` is the debugging tool. Drop it in, run the checker, and it prints what the checker believes:

```text
narrow.py:11: note: Revealed type is "str"
```

No import is needed for the checker to understand it; remove the line afterwards, since the interpreter needs `typing.reveal_type` for it to run.

### Escapes, and how to keep them honest

```python
return v.upper()    # type: ignore[union-attr]
```

Always with the code in brackets. A bare `# type: ignore` suppresses everything on that line forever, including the unrelated error introduced next year.

Then turn on `--warn-unused-ignores`, which reports the ignores that are no longer needed:

```text
narrow.py:19: error: Unused "type: ignore" comment  [unused-ignore]
```

That flag is what stops a codebase accumulating suppressions for problems that were fixed years ago.

`cast(Order, value)` is the stronger escape: it tells the checker to believe you and generates no runtime check whatsoever. It is right when you know something the checker cannot, and it is a lie the same way a wrong annotation is.

### Exhaustiveness

```python
def describe(s: State) -> str:
    match s:
        case State.A:
            return "a"
    assert_never(s)
```

```text
error: Argument 1 to "assert_never" has incompatible type "Literal[State.B]"; expected "Never"  [arg-type]
```

The checker names the case you forgot. Adding a third member to the enum breaks the build rather than falling through at run time, which is the single highest-value pattern in this lesson. `assert_never` is in `typing` since Python 3.11.

### Configuration, and adopting it gradually

```toml
[tool.mypy]
strict = true

[[tool.mypy.overrides]]
module = ["legacy.*"]
disallow_untyped_defs = false
check_untyped_defs = false
```

`strict` is a bundle. In mypy 2.3 it enables thirteen flags, including `disallow-untyped-defs`, `disallow-untyped-calls`, `check-untyped-defs`, `warn-return-any`, `warn-unused-ignores` and `strict-equality`. Turning it on for a large existing codebase produces thousands of errors, so the working approach is the ratchet: `strict = true` globally, then relax **individual flags** for the modules that are not ready, and delete those overrides one module at a time.

One trap, worth verifying rather than assuming: `strict = false` inside a per-module override does **nothing**. It is not rejected, and the module stays strict. Only the individual flags work per module.

### Missing stubs

A dependency without type information makes everything from it `Any`. Three answers:

1. Install the stubs, if they exist, usually `types-<package>`.
2. Check whether the package ships its own, which is what a `py.typed` marker file inside it means.
3. Silence that import specifically, and accept that anything it touches is unchecked:

```toml
[[tool.mypy.overrides]]
module = ["untyped_dependency.*"]
ignore_missing_imports = true
```

Global `--ignore-missing-imports` is the version to avoid: it turns every future missing dependency into a silent hole.

### Which checker

mypy is the reference implementation and the one the specification tracks. pyright is faster, stricter by default about `None`, and what most editors run for completion. They disagree at the edges, and disagreement is a signal the code is genuinely ambiguous. Pick one for the build, and know your editor may be running the other.

## Practice

1. ▢ Which of the four defects in the file above does a default configuration miss, and what makes it invisible?

<details markdown="1"><summary>Check</summary>

Defect 2, inside `untyped`. Without annotations, the body is not checked and calls into it produce `Any`. It appears under `--strict` as `[no-untyped-def]`.

</details>

2. ▢ Fix this without `assert`, `cast`, or an ignore comment.

   ```python
   def label(order_id: int) -> str:
       order = find(order_id)
       return order.country.upper()
   ```

<details markdown="1"><summary>Hint</summary>

Two things can be `None` here if `country` is optional. Handle the outer one first, and read the error again.

</details>

<details markdown="1"><summary>Check</summary>

```python
def label(order_id: int) -> str:
    order = find(order_id)
    if order is None:
        return "UNKNOWN"
    if order.country is None:
        return "UNKNOWN"
    return order.country.upper()
```

Early returns keep the body flat and give the checker two narrowings. If both branches produce the same fallback, `order.country or "unknown"` reads better, with the lesson-5 caveat that it also replaces an empty string.

</details>

3. ▢ Rank these four ways of dealing with a `union-attr` error, best first.

   - a) `assert order is not None`
   - b) `if order is None: return None` and change the return type to `str | None`
   - c) `order = cast(Order, find(order_id))`
   - d) `return order.amount  # type: ignore`

<details markdown="1"><summary>Check</summary>

**b**, **a**, **c**, **d**.

- b) Propagates the truth. The caller now knows, and the checker holds them to it.
- a) Honest about the cost: it documents the assumption and fails loudly at run time if wrong. Acceptable where absence really is a bug.
- c) Silences the checker with no runtime check at all. If the value is `None`, an `AttributeError` appears far away.
- d) All of c's problems, plus it has no error code, so it also hides whatever error appears on that line later.

</details>

4. ▢ A team sets `strict = true`, gets 4,000 errors, and reverts. Design the adoption they should have done.

<details markdown="1"><summary>Check</summary>

Keep `strict = true` globally, then add per-module overrides relaxing the individual flags for every package that fails, so the build is green on day one. New code is strict automatically, because new modules have no override. Then delete one override per pull request.

Two details matter. Relax **flags**, not `strict`, since `strict = false` per module has no effect. And put the error budget where it belongs: a module still under an override is a known debt with a name, not an unknown.

</details>

5. ▢ Why is this worse than it looks, and what is the narrower fix?

   ```toml
   [tool.mypy]
   ignore_missing_imports = true
   ```

<details markdown="1"><summary>Check</summary>

It applies to every import that lacks type information, present and future. A dependency added next month, or a typo in a module name inside your own project, becomes `Any` rather than an error, and everything derived from it is unchecked.

The fix is a per-module override for each dependency that genuinely has no stubs, so the list is visible in the file and shrinks as the ecosystem improves.

</details>

6. ▢ An enum gains a third member and nothing breaks in the build, but a request starts returning `None`. What was missing?

<details markdown="1"><summary>Check</summary>

An exhaustiveness check. A `match` or `if/elif` chain over the members with no final `assert_never` falls off the end and returns `None` implicitly, and the annotation `-> str` was never verified for that path.

Adding `assert_never(s)` after the last case makes the checker report the unhandled member by name, at the moment the member is added.

</details>

## Real-world reps

- [ ] Run a checker on one module you own with default settings, then with `--strict`. Compare the counts. The difference is what your annotations were not buying.
- [ ] Add a `[tool.mypy]` block with `strict = true` and per-module relaxations until the run is green. Commit that as the baseline, then remove one relaxation.
- [ ] Find every bare `# type: ignore` in code you own, add the specific code to each, and switch on `warn_unused_ignores`. Delete whatever it reports.
- [ ] Put `reveal_type` on a variable whose type you would have guessed wrong, and read what the checker actually believes.
- [ ] Tomorrow: add `assert_never` to one `match` over an enum or a `Literal`, then add a member and watch the build fail in the right place.

## Going further

- [mypy documentation](https://mypy.readthedocs.io/en/stable/): what each flag turns on, and how inference proceeds
- [mypy error codes](https://mypy.readthedocs.io/en/stable/error_code_list.html): the full list, with an example of each
- [Type narrowing](https://mypy.readthedocs.io/en/stable/type_narrowing.html): every form the checker understands, including `TypeGuard`
- [Static Typing with Python: guides](https://typing.readthedocs.io/en/latest/guides/index.html): adoption strategies, and writing stubs
- [pyright](https://microsoft.github.io/pyright/): the other implementation, and its stricter defaults
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
