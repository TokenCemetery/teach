---
title: 18. Types at the Boundary
description: Turning Any from JSON, environment and database rows into something a checker can reason about
type: lesson
---

# Lesson 18. Types at the Boundary

**Mission link:** Every annotation inside a program is worthless if the data entering it is `Any`. The boundary is one function wide, and the whole benefit of typing depends on what happens there.
**Primary source:** [Static Typing with Python, TypedDict](https://typing.readthedocs.io/en/latest/spec/typeddict.html)
**Prerequisites:** [Lesson 16](0016-making-a-checker-useful.md), [Lesson 17](0017-generics-and-protocols.md)

## Warm-up

1. ▢ Lesson 16 named the error code that marks where checking silently stopped. Which one, and what triggers it here?

   ```python
   def load(raw: str) -> dict[str, int]:
       return json.loads(raw)
   ```

<details markdown="1"><summary>Check</summary>

`[no-any-return]`. `json.loads` returns `Any`, so the annotation is a promise nothing verified.

</details>

2. ▢ Lesson 12 listed `TypedDict` as one shape for a bundle of data. What is it at run time?

<details markdown="1"><summary>Check</summary>

A plain `dict`. `TypedDict` exists for the checker only, which this lesson makes precise.

</details>

## Know this

Four sources hand a program values a checker knows nothing about:

| Source | What it gives you |
|---|---|
| `json.loads` | `Any` |
| `os.environ` | `str`, always, including `"false"` and `"0"` |
| a database driver | tuples, or dicts of `Any` |
| a web framework's request body | `Any`, or the framework's own model |

The discipline is one sentence: **convert once, at the edge, in a function that can fail.** Everything inside then has real types, and there is exactly one place to look when the outside world changes shape.

### `TypedDict`, for a dict that must stay a dict

```python
from typing import TypedDict, NotRequired

class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]
```

The checker now knows the keys:

```text
error: TypedDict "Config" has no key "hostt"  [typeddict-item]
note: Did you mean "host"?
error: Incompatible types (expression has type "str", TypedDict item "port" has type "int")  [typeddict-item]
```

A misspelled key becomes an error, and the checker even suggests the right one. `NotRequired`, since Python 3.11, marks an optional key; `total=False` on the class makes them all optional.

What it is not: at run time this is a `dict` with no checking whatsoever. `c: Config = {"host": 1}` executes happily, and `isinstance(c, Config)` raises `TypeError: TypedDict does not support instance and class checks`. Reach for `TypedDict` when the value has to remain a dict, because it is going straight back out as JSON or into a library that expects one. When it does not, a frozen dataclass from lesson 12 is stronger, because construction is a real function that can validate.

### `Literal`, for a closed set of values

```python
from typing import Literal

Mode = Literal["read", "write"]

def open_stream(mode: Mode) -> None: ...

open_stream("append")
```

```text
error: Argument 1 to "open_stream" has incompatible type "Literal['append']";
       expected "Literal['read', 'write']"  [arg-type]
```

`Literal` is what makes a stringly-typed API checkable without changing its callers, which is why the standard library's own stubs use it heavily. For a set that your own code owns, an `Enum` from lesson 14 is usually better, because it also exists at run time. `Literal` wins when the values are fixed by an external protocol you do not control.

### `NewType`, for two things that are both `int`

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def load(uid: UserId) -> None: ...

load(n)                 # error: incompatible type "int"; expected "UserId"
load(UserId(n))         # explicit, and free at run time
```

```text
error: Argument 1 to "load" has incompatible type "int"; expected "UserId"  [arg-type]
```

This catches the bug where an order id is passed where a user id belongs, which no amount of `int` annotation can. `UserId(n)` compiles to `n`: there is no wrapper object and no cost.

### Narrowing with a function: `TypeIs`

Sometimes the check is yours to write. A function returning `TypeIs[X]`, since Python 3.13, teaches the checker to narrow on it:

```python
from typing import TypeIs

def all_strings(v: Sequence[object]) -> TypeIs[Sequence[str]]:
    return all(isinstance(x, str) for x in v)

def join(v: Sequence[object]) -> str:
    if all_strings(v):
        reveal_type(v)          # Revealed type is "typing.Sequence[str]"
        return ", ".join(v)
    return ""
```

Two things to know. The narrowed type must be a subtype of the parameter type, so `list[object]` to `TypeIs[list[str]]` is rejected for the invariance reason from lesson 17, and the `Sequence` version above is accepted. And `TypeGuard`, the older form, narrows only in the true branch and does not require the subtype relationship; `TypeIs` narrows both branches and is the better default now.

### `@overload`, when the return depends on the arguments

```python
@overload
def get(key: str) -> str: ...
@overload
def get(key: str, default: int) -> str | int: ...

def get(key: str, default: int | None = None) -> str | int:
    ...
```

```text
reveal_type(get("a"))        # str
reveal_type(get("a", 1))     # str | int
```

The overloads are what the checker reads; the last definition is the only one that runs. Use it where a single signature would force every caller to narrow a union they already know the answer to, `dict.get` being the canonical example.

### The boundary function itself

```python
@dataclass(frozen=True)
class Config:
    host: str
    port: int
    debug: bool = False

def parse_config(raw: object) -> Config:
    if not isinstance(raw, dict):
        raise ConfigError("expected an object at the top level")
    try:
        host = raw["host"]
        port = raw["port"]
    except KeyError as exc:
        raise ConfigError(f"missing key: {exc}") from exc
    if not isinstance(host, str) or not isinstance(port, int):
        raise ConfigError("host must be a string and port an integer")
    return Config(host=host, port=port, debug=bool(raw.get("debug", False)))
```

Verbose, and every line is doing something the rest of the program then never has to. Note `raw: object` rather than `Any`, which is what forces the `isinstance` checks to exist, and `ConfigError` from lesson 10, which gives the caller one exception type to catch.

At three or four fields this is fine. Past that, a validation library earns its place: `pydantic` generates exactly this from the same annotations, and reaching for it here is a considered choice rather than a default class. What does not work is skipping the boundary and annotating hopefully.

Environment variables deserve one explicit warning, because the failure is silent:

```python
DEBUG = bool(os.environ.get("DEBUG", ""))       # "false" is True
DEBUG = os.environ.get("DEBUG", "") == "1"      # a decision, written down
```

## Practice

1. ▢ Fix the annotation, and then fix the function.

   ```python
   def load_settings(path: Path) -> dict[str, int]:
       return json.loads(path.read_text(encoding="utf-8"))
   ```

<details markdown="1"><summary>Hint</summary>

There are two honest fixes and they differ in how much work they move to the caller.

</details>

<details markdown="1"><summary>Check</summary>

Honest but weak: `-> Any`, or `-> object`, which pushes every check to the caller and at least stops the lie.

Honest and useful: return a real type and do the work here.

```python
def load_settings(path: Path) -> Settings:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("expected an object")
    ...
    return Settings(...)
```

The point of the boundary is that this function is the only place `isinstance` appears.

</details>

2. ▢ `TypedDict` or frozen dataclass?

   - a) A row read from a database and passed to three functions
   - b) A payload assembled and handed to a library that expects `dict`
   - c) A parsed configuration file used everywhere in the program
   - d) The `**kwargs` a wrapper forwards to a third-party function

<details markdown="1"><summary>Check</summary>

- a) Dataclass. The row is converted once and nothing downstream needs a dict.
- b) `TypedDict`. It must stay a dict, and the alternative is `asdict` at every call.
- c) Dataclass, frozen. Construction is where the validation goes, and nothing should mutate configuration.
- d) `TypedDict`, which is what it is for: `Unpack[Params]` types `**kwargs` precisely.

</details>

3. ▢ What does each of these catch that a plain `int` does not?

   ```python
   UserId = NewType("UserId", int)
   Port = Literal[80, 443]
   ```

<details markdown="1"><summary>Check</summary>

`UserId` catches passing an id of the wrong kind: an order id, a row count, a length. Both are `int`, and only one is meaningful in that parameter.

`Port` catches a value outside the allowed set at the call site, with no runtime check and no validation function.

Neither costs anything at run time. `UserId(n)` is `n`, and `Literal` is erased entirely.

</details>

4. ▢ Why does the checker reject this, and what is the fix?

   ```python
   def all_ints(v: list[object]) -> TypeIs[list[int]]:
       return all(isinstance(x, int) for x in v)
   ```

<details markdown="1"><summary>Check</summary>

```text
error: Narrowed type "list[int]" is not a subtype of input type "list[object]"
       [narrowed-type-not-subtype]
```

`list` is invariant, so `list[int]` is not a subtype of `list[object]`, and `TypeIs` requires that relationship. The reason is real rather than formal: after narrowing, the checker would let you append an `int` to a list the caller thinks holds `object`s, or the reverse.

Fix: use the covariant read-only type, `def all_ints(v: Sequence[object]) -> TypeIs[Sequence[int]]`.

</details>

5. ▢ Find the bug, and say why no checker reports it.

   ```python
   MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 3))
   VERBOSE = bool(os.environ.get("VERBOSE", False))
   ```

<details markdown="1"><summary>Check</summary>

`VERBOSE` is `True` for every non-empty value, including `"false"`, `"0"` and `"no"`. `bool` of a non-empty string is `True`, which is lesson 5, and every annotation here is correct, so there is nothing for a checker to report. The types are right and the meaning is wrong.

```python
VERBOSE = os.environ.get("VERBOSE", "").lower() in {"1", "true", "yes"}
```

`MAX_RETRIES` is fine as a type and will raise `ValueError` on a non-numeric value, which is the correct behaviour and worth wrapping in the boundary function so the message names the variable.

</details>

6. ▢ A colleague argues that since the API is internal and both sides are typed, the boundary function is ceremony. Answer them.

<details markdown="1"><summary>Check</summary>

Two answers.

The annotation on the other side of a network call or a database is not a guarantee your process can rely on: it describes what the other program believes today, and JSON carries none of it. The deployment where the two disagree is exactly the one the boundary exists for.

And a checker's proof only covers what enters typed. Skipping the boundary makes every downstream annotation an assertion nobody verified, so the codebase reports zero errors and has the same defects it had before anyone annotated it.

Where they have a point: the boundary should be one function, not `isinstance` scattered through the call graph. If it feels like ceremony because it is everywhere, that is a real complaint about placement.

</details>

## Real-world reps

- [ ] Find every `json.loads` in code you own and follow the result. Whichever one flows furthest before being used is where the first boundary function belongs.
- [ ] Turn on `warn_return_any` and count the results. Each one is a place a promise was made and not kept.
- [ ] Take a dict that crosses two layers with known keys, give it a `TypedDict`, and see whether the checker finds a key that was misspelled in one branch.
- [ ] Add a `NewType` for one id in your domain, and follow the errors. Any place a raw `int` was accepted is a place the wrong id could have been passed.
- [ ] Tomorrow: grep for `bool(os.environ` and `os.getenv` used as a flag, and check what each does with the string `"false"`.

## Going further

- [`TypedDict`](https://typing.readthedocs.io/en/latest/spec/typeddict.html): required and optional keys, and the rules for reading and writing
- [`Literal`](https://typing.readthedocs.io/en/latest/spec/literal.html) and [PEP 586](https://peps.python.org/pep-0586/): closed value sets
- [`NewType`](https://typing.readthedocs.io/en/latest/spec/aliases.html#newtype): distinct types with no runtime cost
- [PEP 742, Narrowing types with `TypeIs`](https://peps.python.org/pep-0742/): why it replaced `TypeGuard` as the default
- [`@overload`](https://typing.readthedocs.io/en/latest/spec/overload.html): the rules for how a checker picks a variant
- [pydantic](https://docs.pydantic.dev/latest/): runtime validation generated from the same annotations
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
