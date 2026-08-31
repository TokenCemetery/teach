---
title: 15. Annotations Are Claims
description: The interpreter stores them and never checks them, which is what makes them worth writing
type: lesson
---

# Lesson 15. Annotations Are Claims

**Mission link:** A type hint is a claim a separate tool can prove or refute. Understanding that the interpreter has no opinion about it is what stops annotations from being decoration and starts them being verification.
**Primary source:** [The Python Standard Library, typing](https://docs.python.org/3/library/typing.html)
**Prerequisites:** [Lesson 6](0006-functions-and-arguments.md), [Lesson 12](0012-dataclasses.md)

## Warm-up

1. ▢ Lesson 12: what does `@dataclass` do with the annotation in `amount: float`?

<details markdown="1"><summary>Check</summary>

It uses it to decide that `amount` is a field, and then ignores what it says. `Order(1, "lots")` builds without complaint.

</details>

2. ▢ What do you expect this to do?

   ```python
   def double(n: int) -> int:
       return n * 2

   print(double("ab"))
   ```

<details markdown="1"><summary>Check</summary>

Prints `abab`. Nothing checks the annotation, and `str` supports `* 2`.

</details>

## Know this

An annotation is **syntax that records a claim**. The interpreter stores it and enforces nothing:

```python
def double(n: int) -> int:
    return n * 2

double("ab")                     # runs, returns "abab"
```

That is not a flaw, it is the design. Python's type system is **gradual**: annotations are written where they pay, checked by a separate tool, and absent everywhere else. Nothing about the language changes when you add them.

What they buy, in order of value:

1. A checker rejects programs that were going to fail, before they run.
2. An editor knows what a name is, so completion and rename work.
3. The signature documents itself, and the documentation cannot drift, because the checker fails when it does.

### The current spellings

```python
def summarise(
    orders: list[Order],                 # not List, since 3.9
    country: str | None = None,          # not Optional[str], since 3.10
    limits: dict[str, int] | None = None,
) -> tuple[int, float]:
    ...
```

| Write | Not | Since |
|---|---|---|
| `list[int]`, `dict[str, int]`, `tuple[int, ...]`, `set[str]` | `typing.List`, `Dict`, `Tuple`, `Set` | 3.9 |
| `int \| None` | `Optional[int]` | 3.10 |
| `int \| str` | `Union[int, str]` | 3.10 |
| `type Rows = list[dict[str, str]]` | `Rows: TypeAlias = ...` | 3.12 |
| `def first[T](xs: list[T]) -> T` | a module-level `TypeVar` | 3.12 |

The old spellings still work and still appear everywhere in existing code. Read them, write the new ones.

### When the annotation is evaluated

This is the one part with a real version boundary, and it changed recently.

```python
class Node:
    def child(self) -> Node:             # refers to Node inside its own body
        ...
```

From Python 3.14, annotations are **evaluated lazily** (PEP 649). The line above is fine, and a `NameError` for a genuinely missing name surfaces only when something reads the annotation.

Before 3.14, annotations were evaluated at definition time, so that code raised `NameError`, and the two workarounds were quoting the name, `-> "Node"`, or putting `from __future__ import annotations` at the top of the file, which turned every annotation in the module into a string. Both are still valid, both are still all over real codebases, and a library supporting older versions still needs one of them.

Practical consequence: annotations are for a checker, and a checker never evaluates them. Anything that reads them at run time, such as a dataclass-like decorator or a validation library, does the evaluation itself, which is why those libraries care about this and ordinary code does not.

### `Any` is a hole, not a type

```python
def parse(raw: str) -> Any:
    ...

user = parse(payload)
user.nmae                            # no error, from any checker, ever
```

`Any` means "stop checking here", and it propagates: everything derived from an `Any` is also unchecked. An unannotated function is an implicit `Any` in both directions, which is why a codebase can be half-annotated and get almost none of the benefit, and why stage-3 tooling has a flag for exactly that.

When the type is genuinely unknown, `object` is usually the honest answer. `object` accepts anything and permits almost nothing without narrowing, so the checker keeps working.

### What to annotate, and what not to

Annotate:

- every parameter and return of a public function, `-> None` included
- dataclass fields and class attributes
- a container whose element type is not obvious from one line away
- anything the checker gets wrong, or wrong enough that you had to think

Do not annotate:

- local variables the checker can infer: `count = 0` needs nothing
- `self` and `cls`
- a private one-line helper, unless the checker asks

`-> None` deserves its own line. A function with no annotations at all is invisible to a default checker configuration, so the single most valuable annotation in a codebase is often the return type on a procedure that returns nothing.

### Take the general type, return the specific one

```python
def total(orders: Iterable[Order]) -> float:      # accepts list, tuple, generator
    return sum(o.amount for o in orders)

def recent(orders: Iterable[Order]) -> list[Order]:   # callers get a real list
    ...
```

`Iterable`, `Sequence`, `Mapping` and `Collection` in parameters accept more callers, which lesson 8 already argued for on other grounds. Concrete `list` and `dict` in return types tell callers what they can do with the result. Declaring `-> Iterable[Order]` promises less, and is right when the function is a generator whose laziness is the point.

### Two annotations that state intent

```python
from typing import Final, ClassVar

MAX_RETRIES: Final = 3               # rebinding is an error a checker reports

class Session:
    registry: ClassVar[dict[str, "Session"]] = {}   # on the class, not per instance
    token: str
```

`Final` catches the accidental reassignment of a constant. `ClassVar` is the one that prevents a real bug: a dataclass would otherwise treat `registry` as a field with a shared mutable default, and lesson 12 covered what that costs.

## Practice

1. ▢ Rewrite with current spellings.

   ```python
   from typing import Dict, List, Optional, Union

   def group(rows: List[Dict[str, str]], key: Optional[str] = None) -> Dict[str, List[Union[int, str]]]:
       ...
   ```

<details markdown="1"><summary>Check</summary>

```python
def group(rows: list[dict[str, str]], key: str | None = None) -> dict[str, list[int | str]]:
    ...
```

The `typing` import disappears entirely, which is the usual outcome.

</details>

2. ▢ This passes a strict checker. Explain why that is worthless.

   ```python
   def load_config(path: str) -> Any:
       return json.loads(Path(path).read_text(encoding="utf-8"))

   config = load_config("app.json")
   timeout = config["timout"]["seconds"] * "3"
   ```

<details markdown="1"><summary>Hint</summary>

What type does the checker think `config` has, and what does it think `config["timout"]` has?

</details>

<details markdown="1"><summary>Check</summary>

`Any` disables checking, and everything derived from it is also `Any`. The misspelled key, the nested lookup and multiplying a number by a string all pass, because the checker has been told to stop reasoning.

`json.loads` genuinely returns `Any`, so this is where the honest work is: narrow it at the boundary. Lesson 18 covers the shapes for that. The minimum improvement is to return `dict[str, object]`, which makes the multiplication an error immediately.

</details>

3. ▢ Which of these annotations is wrong or misleading?

   - a) `def send(self, msg: str) -> None:` on a method that returns nothing
   - b) `def parse(raw: bytes) -> dict:`
   - c) `def total(orders: list[Order]) -> float:` called with a generator
   - d) `def find(id: int) -> Order:` on a function that returns `None` when absent
   - e) `count: int = 0` as a local variable

<details markdown="1"><summary>Check</summary>

- a) Correct, and the most valuable kind: without it the function is unchecked.
- b) Misleading. A bare `dict` says nothing about keys or values, so every lookup is `Any`. Write `dict[str, object]` at least.
- c) Wrong for the caller, who now gets an error passing a generator. `Iterable[Order]` is the right parameter type.
- d) **A lie, and the worst kind.** The checker will let callers write `find(1).amount` with no complaint, and it fails in production. `Order | None` is the truth, and the callers it breaks were already broken.
- e) Harmless and redundant. The checker infers `int`.

</details>

4. ▢ Why does this fail before Python 3.14, and give the two fixes that work on any version.

   ```python
   class Tree:
       def leftmost(self) -> Tree:
           ...
   ```

<details markdown="1"><summary>Check</summary>

Before 3.14, the annotation is evaluated when the `def` executes, which happens while the class body is still running, so the name `Tree` does not exist yet: `NameError`.

Fixes: quote it, `-> "Tree"`, or add `from __future__ import annotations` at the top of the file. From 3.14 onward, annotations are evaluated lazily and the original code is correct as written.

A third answer is better still when the return is genuinely "the same class as `self`": `typing.Self`, since 3.11, which is also correct for subclasses where `Tree` is not.

</details>

5. ▢ A colleague adds annotations to one module and reports the checker found nothing. The module has forty functions, of which two are annotated. Explain.

<details markdown="1"><summary>Check</summary>

A checker's default configuration does not check the bodies of unannotated functions, and treats calls into them as `Any`. Two annotated functions surrounded by thirty-eight unannotated ones therefore produce almost no findings, because every value crossing a boundary loses its type.

This is what the strictness flags in lesson 16 are for, and it is also why annotating a codebase pays off non-linearly: the value arrives when a whole module or package is covered, not per function.

</details>

6. ▢ What bug does `ClassVar` prevent here?

   ```python
   @dataclass
   class Session:
       registry: dict[str, "Session"] = field(default_factory=dict)
   ```

<details markdown="1"><summary>Check</summary>

None as written, which is the point: `field(default_factory=dict)` correctly gives each instance its own dict. But the intent looks like a shared registry, and the version people write when they mean that is `registry: dict = {}`, which raises `ValueError` from lesson 12, or a plain class attribute, which a dataclass silently turns into a field.

`registry: ClassVar[dict[str, "Session"]] = {}` says "this lives on the class", the dataclass then excludes it from `__init__` and from equality, and the checker holds you to it.

</details>

## Real-world reps

- [ ] Annotate one complete module, not one function. Every public signature, `-> None` included, and nothing else. That is the unit at which a checker starts finding things.
- [ ] Grep for `-> Any` and `: Any` in code you own. For each, decide whether the honest type is `object`, a `TypedDict`, or a real class.
- [ ] Find a function annotated `-> X` that can return `None`, and fix the annotation rather than the function. Then look at what the checker says about its callers.
- [ ] Search for `List[`, `Dict[` and `Optional[` and modernise one file. Note how many `typing` imports disappear.
- [ ] Tomorrow: add `Final` to one module-level constant and `ClassVar` to one class attribute, and read what the checker says.

## Going further

- [`typing`](https://docs.python.org/3/library/typing.html): the current spellings, and which older ones are deprecated
- [Static Typing with Python](https://typing.readthedocs.io/en/latest/): the specification and the practical guides, maintained with the type system
- [PEP 484, Type Hints](https://peps.python.org/pep-0484/): the original design, and the explicit decision that annotations do not affect runtime behaviour
- [PEP 585](https://peps.python.org/pep-0585/) and [PEP 604](https://peps.python.org/pep-0604/): `list[int]` and `int | None`
- [PEP 649, Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/): what changed in Python 3.14, and why the old workarounds existed
- [`annotationlib`](https://docs.python.org/3/library/annotationlib.html): reading annotations at run time, for the libraries that must
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
