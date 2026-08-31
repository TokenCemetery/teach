---
title: 17. Generics and Protocols
description: Keeping the element type through a function, and typing a shape instead of a class
type: lesson
---

# Lesson 17. Generics and Protocols

**Mission link:** Python's own libraries are typed structurally, so a function that asks for a class when it only needs a method is narrower than the language. Generics and protocols are how a signature stays honest without being restrictive.
**Primary source:** [Static Typing with Python, Generics](https://typing.readthedocs.io/en/latest/reference/generics.html)
**Prerequisites:** [Lesson 15](0015-annotations-are-claims.md), [Lesson 16](0016-making-a-checker-useful.md)

## Warm-up

1. ▢ Lesson 15 said to take `Iterable` in parameters. What does a checker lose if a parameter is annotated `list` with no element type?

<details markdown="1"><summary>Check</summary>

The element type. Every item read out of it is `Any`, so nothing about the contents is checked.

</details>

2. ▢ What should this return?

   ```python
   def first(xs: list) -> ?:
       return xs[0]
   ```

<details markdown="1"><summary>Check</summary>

Whatever the list contains, which no fixed annotation can express. That is what a generic is for.

</details>

## Know this

A **generic** relates one type in a signature to another. Since Python 3.12 the parameter is declared in brackets on the definition:

```python
def first[T](xs: Sequence[T]) -> T:
    return xs[0]
```

```text
reveal_type(first([1, 2]))       # Revealed type is "int"
reveal_type(first(["a", "b"]))   # Revealed type is "str"
```

`T` is not a type; it is a name for "whatever type the caller used", and using it twice is the claim that both are the same. Older code declares it separately, and the two forms mean the same thing:

```python
T = TypeVar("T")                 # before 3.12, still everywhere
def first(xs: Sequence[T]) -> T: ...
```

Generic classes and aliases use the same brackets:

```python
class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

type Pair[T] = tuple[T, T]
```

### Bounds and constraints

```python
def largest[T: (int, float)](a: T, b: T) -> T:      # constrained: one of these two
    return a if a > b else b

def describe[T: Order](item: T) -> str:              # bound: Order or a subclass
    ...
```

A **constraint list** allows exactly the listed types. A **bound** allows the type and anything below it. Reach for a bound when the function needs a capability, and the next section is usually a better way to say that.

### Invariance, and why `Sequence` is the parameter type

```python
def widen(xs: list[object]) -> None: ...

def caller(nums: list[int]) -> None:
    widen(nums)
```

```text
error: Argument 1 to "widen" has incompatible type "list[int]"; expected "list[object]"  [arg-type]
note: "list" is invariant -- see ... #variance
note: Consider using "Sequence" instead, which is covariant
```

This looks like pedantry and is not. `widen` could legally do `xs.append("hello")`, and then the caller's `list[int]` contains a string. **A mutable container cannot be substituted for a container of a wider type.** Languages that allow it, such as Java with its arrays, pay for the substitution with a run-time failure at the moment of the write instead of an error at the call.

`Sequence[object]` is read-only, so it is safe, and the fix is to ask for the narrower capability:

| Parameter | Accepts | Allows the function to |
|---|---|---|
| `list[int]` | only a `list[int]` | mutate it, and the caller sees that |
| `Sequence[int]` | list, tuple, str-like sequences | index, slice, iterate, `len` |
| `Iterable[int]` | all of those plus generators | iterate once |
| `MutableSequence[int]` | list and similar | mutate, stated openly |

Choose from what the body does. Most functions iterate, so most parameters want `Iterable`.

### Protocols: typing the shape

```python
from typing import Protocol

class Closable(Protocol):
    def close(self) -> None: ...

def shutdown(resource: Closable) -> None:
    resource.close()
```

Any class with a matching `close` satisfies this, with **no inheritance and no registration**:

```python
class File:
    def close(self) -> None: ...

shutdown(File())            # accepted
shutdown(NotClosable())     # error: incompatible type "NotClosable"; expected "Closable"
```

This is **structural typing**, and it is how Python already worked before anyone annotated it. A function that took "something with a `read` method" was never taking a class, and a `Protocol` is how to say that to a checker. It also works on classes you do not own, which nominal inheritance cannot do.

`Protocol` against `ABC`, decided by one question: **do you own the implementations?**

| | Protocol | Abstract base class |
|---|---|---|
| conformance | structural: shape matches | nominal: must inherit |
| third-party classes | conform automatically | cannot, without a wrapper |
| shared implementation | none, it is a signature | can provide real methods |
| discoverability | grep for the protocol | `issubclass` works, and the base documents itself |
| use when | typing a boundary you consume | building a family you own |

The standard library's own vocabulary is already protocols: `Iterable`, `Iterator`, `Sequence`, `Mapping`, `Callable`, `SupportsIndex`, `SupportsFloat`. Prefer one of those over a new protocol with the same shape.

```python
def apply(f: Callable[[int, str], bool], n: int, s: str) -> bool:
    return f(n, s)
```

### `runtime_checkable`, and what it does not check

```python
@runtime_checkable
class Sized2(Protocol):
    def size(self) -> int: ...

class Liar:
    def size(self, extra: str) -> int: ...

isinstance(Liar(), Sized2)      # True
Liar().size()                   # TypeError: missing 1 required positional argument
```

`isinstance` against a runtime-checkable protocol checks that the **attribute names exist**. It does not check signatures, parameter counts, or return types. Treat it as a coarse guard, and rely on the checker for the real conformance.

### `Self`

```python
class QueryBuilder:
    def where(self, clause: str) -> Self:
        ...
        return self
```

`Self`, since Python 3.11, means "the type of the actual instance", so a subclass's `where` returns the subclass. Annotating `-> QueryBuilder` loses that, and chaining then reports the wrong type for every subclass.

### When not to reach for either

A generic with one call site is indirection. A protocol with one implementer that you own is an interface nobody needed. Both earn their place at the second caller, and the honest first version is a concrete type.

## Practice

1. ▢ Make this generic, so the checker knows the element type of the result.

   ```python
   def dedupe(items: list) -> list:
       seen = set()
       out = []
       for item in items:
           if item not in seen:
               seen.add(item)
               out.append(item)
       return out
   ```

<details markdown="1"><summary>Check</summary>

```python
def dedupe[T](items: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    out: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
```

`Iterable` in the parameter, since the body only iterates, and a concrete `list[T]` in the return, since callers will want to index it. The two local annotations are needed because an empty `set()` and `[]` give the checker nothing to infer from.

Strictly, `T` should be bounded to hashable types, and in practice the checker's handling of that is awkward enough that most code leaves it.

</details>

2. ▢ Why is the second call an error, and which one line fixes both the error and the design?

   ```python
   def log_all(items: list[object]) -> None:
       for item in items:
           print(item)

   log_all(["a", "b"])
   log_all([1, 2])
   ```

<details markdown="1"><summary>Hint</summary>

Both calls are errors, and the note in the checker's output names the replacement.

</details>

<details markdown="1"><summary>Check</summary>

`list` is invariant, so neither `list[str]` nor `list[int]` is a `list[object]`. The reason is that `log_all` is permitted to append to the list.

```python
def log_all(items: Iterable[object]) -> None:
```

The body only iterates, so `Iterable` states the real requirement, accepts every caller, and now cannot mutate anything.

</details>

3. ▢ Protocol or abstract base class?

   - a) Typing a parameter that needs `read` and `close`, called with file objects and with objects from two libraries
   - b) A family of payment providers, all written in this codebase, sharing retry logic
   - c) Accepting "anything with a `to_json` method" from plugin code you do not control
   - d) A base class that provides four concrete methods and requires one

<details markdown="1"><summary>Check</summary>

- a) Protocol. You do not own the implementations, and `IO[str]` from `typing` may already fit.
- b) Abstract base class. You own them all, and the shared retry logic has to live somewhere.
- c) Protocol. Nominal typing cannot reach plugin classes.
- d) Abstract base class. A protocol carries no implementation.

</details>

4. ▢ What does this `isinstance` guarantee, and what does the code below it still assume?

   ```python
   @runtime_checkable
   class Serialisable(Protocol):
       def to_json(self) -> str: ...

   def dump(obj: object) -> str:
       if isinstance(obj, Serialisable):
           return obj.to_json()
       return json.dumps(obj)
   ```

<details markdown="1"><summary>Check</summary>

It guarantees only that the object has an attribute called `to_json`. It does not check that it is callable with no arguments, or that it returns a string.

So the code assumes the signature. A class whose `to_json(self, indent)` requires an argument passes the check and raises `TypeError` on the call, and one returning a `dict` passes and returns the wrong type. The check is a name lookup, not a conformance proof.

</details>

5. ▢ Fix the chaining.

   ```python
   class Query:
       def where(self, clause: str) -> "Query":
           return self

   class AuditedQuery(Query):
       def by(self, user: str) -> "AuditedQuery":
           return self

   AuditedQuery().where("x").by("bob")
   ```

<details markdown="1"><summary>Check</summary>

The last line fails to check: `where` is annotated as returning `Query`, which has no `by`.

```python
from typing import Self

class Query:
    def where(self, clause: str) -> Self:
        return self
```

`Self` means the runtime type, so `AuditedQuery().where(...)` is an `AuditedQuery`. Before 3.11 this needed a bound `TypeVar` on the method, which is why old code has `T = TypeVar("T", bound="Query")`.

</details>

6. ▢ A colleague introduces a generic `Repository[T]` with one subclass, `UserRepository`, and a `Protocol` with one implementer. Argue both ways in two sentences each.

<details markdown="1"><summary>Check</summary>

Against: both are indirection bought before it was needed, they double the number of places a change lands, and the concrete `UserRepository` would have read better and been easier to follow.

For: a repository is a shape that predictably recurs, the protocol is what lets tests substitute a fake without inheritance, and the second implementer usually arrives.

The honest resolution is that the protocol earns its place if a test already substitutes something, and the generic does not earn its place until the second type parameter exists.

</details>

## Real-world reps

- [ ] Find a function annotated with a concrete `list[X]` parameter whose body only iterates. Change it to `Iterable[X]` and see whether any caller was working around the restriction.
- [ ] Take one function that accepts an object and calls two methods on it. Write the `Protocol` for exactly those two methods, then check whether `typing` already has it.
- [ ] Find a `-> "SameClass"` annotation on a method that returns `self`, and switch it to `Self`. If the class has subclasses, look at what the checker says about them now.
- [ ] Write a generic function with `reveal_type` at three call sites, and confirm the checker specialises it as you expected.
- [ ] Tomorrow: look for an abstract base class in your codebase whose subclasses share no implementation. That is a protocol wearing inheritance.

## Going further

- [Generics](https://typing.readthedocs.io/en/latest/reference/generics.html): type parameters, bounds, constraints and variance
- [PEP 695, Type Parameter Syntax](https://peps.python.org/pep-0695/): the bracket syntax, and what it replaced
- [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol) and [PEP 544](https://peps.python.org/pep-0544/): structural subtyping, and the limits of `runtime_checkable`
- [Variance, in the mypy documentation](https://mypy.readthedocs.io/en/stable/common_issues.html#variance): why `list` is invariant and `Sequence` is not
- [`collections.abc`](https://docs.python.org/3/library/collections.abc.html): the protocol vocabulary that already exists
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
