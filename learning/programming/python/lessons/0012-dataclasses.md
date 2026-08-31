---
title: 12. Dataclasses
description: Generated init, repr and equality, and choosing the right shape for a bundle of data
type: lesson
---

# Lesson 12. Dataclasses

**Mission link:** Most classes in real Python hold data and nothing else, and hand-writing their `__init__`, `__repr__` and `__eq__` is where the typos live. Deciding which shape a bundle of data deserves is a judgment call reviewers make constantly.
**Primary source:** [The Python Standard Library, dataclasses](https://docs.python.org/3/library/dataclasses.html)
**Prerequisites:** [Lesson 2](0002-mutability-and-copying.md), [Lesson 4](0004-dicts-and-sets.md), [Lesson 6](0006-functions-and-arguments.md)

## Warm-up

1. ▢ Lesson 6: why is `def f(items=[])` a trap, and what is the fix?

<details markdown="1"><summary>Check</summary>

The default is evaluated once at definition, so every call without an argument shares one list. The fix is `items=None` and `items = [] if items is None else items` inside.

</details>

2. ▢ Lesson 4: what does a class need before its instances can be dict keys or set members?

<details markdown="1"><summary>Check</summary>

To be hashable: a `__hash__` that never changes for the object's lifetime, consistent with `__eq__`. Objects that compare equal must hash equal.

</details>

## Know this

```python
from dataclasses import dataclass

@dataclass
class Order:
    id: int
    amount: float
    country: str = "GB"
```

That generates `__init__`, `__repr__` and `__eq__`:

```python
o = Order(1, 25.0)
print(o)                        # Order(id=1, amount=25.0, country='GB')
print(o == Order(1, 25.0))      # True
```

The `__eq__` compares field by field, in order, and only against the same class. The `__repr__` is the one that changes daily life, because a log line or a failing test now says which order.

The annotations are **required** by the decorator: a name without one is not a field, and it becomes an ordinary class attribute. They are not enforced at runtime. `Order("one", "lots")` builds happily. A dataclass is code generation, not validation, and stage 3 brings the checker that reads those annotations.

### Mutable defaults are rejected, not shared

```python
@dataclass
class Cart:
    items: list = []             # ValueError at class definition
```

Python refuses this outright, which is the one place the language protects you from the lesson-6 trap. The replacement says what to call per instance:

```python
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list = field(default_factory=list)
```

`default_factory` runs once per instance. Use it for every list, dict, set and any object that must not be shared.

### The options worth knowing

```python
@dataclass(frozen=True, slots=True, kw_only=True, order=True)
```

**`frozen=True`** blocks attribute assignment, raising `FrozenInstanceError`, and generates a `__hash__`, so instances can be dict keys and set members. This is the default worth reaching for: a frozen dataclass is a value, and lesson 4's mutable-key bug becomes impossible.

Without `frozen`, a dataclass with the generated `__eq__` sets `__hash__ = None`, so it is deliberately **unhashable**. That is not an oversight, it is the language refusing to let a mutable object be a key.

**`slots=True`**, from Python 3.10, generates `__slots__`: instances get no `__dict__`, which costs less memory and makes attribute access slightly faster, and assigning an undeclared attribute becomes an `AttributeError` instead of silently adding one. One caveat: it works by returning a **new** class object rather than modifying the original, so anything holding a reference to the original, such as a registry populated by a decorator applied below it, ends up pointing at a different class. Passing parameters to a base class `__init_subclass__` is documented as raising `TypeError` for the same reason.

**`kw_only=True`**, from Python 3.10, makes every field keyword-only. It reads better at four fields and up, it removes the entire class of bugs where two same-typed positional arguments get swapped, and it fixes inheritance: a base class with a default no longer forbids a subclass field without one.

**`order=True`** generates `<`, `<=`, `>` and `>=` comparing the field tuple in declaration order. Useful for sorting, and a commitment: field order is now part of your API.

### Per-field control

```python
@dataclass
class User:
    name: str
    email: str = field(repr=False)              # keep it out of logs
    id: int = field(default=0, compare=False)   # not part of equality
    _cache: dict = field(default_factory=dict, init=False)
```

`repr=False` for secrets and noise, `compare=False` for fields that are not part of identity, `init=False` for anything derived or internal.

### `__post_init__`

Runs after the generated `__init__`, and is where derived fields and validation go:

```python
@dataclass
class Range:
    low: int
    high: int

    def __post_init__(self):
        if self.low > self.high:
            raise ValueError(f"low {self.low} exceeds high {self.high}")
```

On a frozen dataclass, assigning in `__post_init__` needs `object.__setattr__(self, "name", value)`, which is a signal to compute the value in the caller instead.

### The three functions to remember

```python
from dataclasses import asdict, replace, fields

replace(order, amount=30.0)     # a new instance, one field changed
asdict(order)                   # nested dicts, recursively
[f.name for f in fields(Order)] # introspection, for generic code
```

`replace` is what makes frozen instances pleasant to work with: "change" becomes "derive".

### Choosing the shape

| Shape | Reach for it when | Cost |
|---|---|---|
| `dict` | keys are data, and vary at runtime | no field names in a traceback, no attribute access, typos are silent |
| tuple | two or three values, positional, local | positions are unreadable three months later |
| `NamedTuple` | a tuple that must stay a tuple, for unpacking or an existing API | it is still a tuple, so it compares equal to one |
| `@dataclass(frozen=True)` | a value with named fields, the usual answer | none worth listing |
| `@dataclass` | it genuinely has to change in place | unhashable, and every holder sees the change |
| `TypedDict` | JSON crossing a boundary, checked statically, stays a dict | nothing at runtime, checker only |
| plain class | behaviour dominates, and the data is incidental | write the dunders you need, or find you needed a dataclass |

Two libraries live past the edge of this table and are worth naming: `attrs`, which does what dataclasses do with more control and predates them, and `pydantic`, which validates and converts at runtime, which is a different job. Reach for `pydantic` at a boundary where data arrives untrusted, not as a default class.

## Practice

1. ▢ Predict what happens at each line.

   ```python
   @dataclass
   class Point:
       x: int
       y: int

   p = Point(1, 2)
   print(p == Point(1, 2))
   {p: "origin-ish"}
   ```

<details markdown="1"><summary>Check</summary>

`True`, then `TypeError: unhashable type: 'Point'`.

The generated `__eq__` sets `__hash__ = None`, because a mutable object whose equality depends on its fields cannot safely be a key. `@dataclass(frozen=True)` gives both.

</details>

2. ▢ This is in review. Name every problem.

   ```python
   @dataclass
   class Session:
       user: str
       tags: list = []
       token: str = "unset"
   ```

<details markdown="1"><summary>Hint</summary>

One of these three lines stops the module from importing at all.

</details>

<details markdown="1"><summary>Check</summary>

- `tags: list = []` raises `ValueError` at class definition, so the module does not import. Use `field(default_factory=list)`.
- `token` defaults to a sentinel string, so a missing token is indistinguishable from a real one and only fails later, at use. Make it required, or `str | None = None`.
- `token` will appear in every `repr`, so it lands in logs and tracebacks. `field(repr=False)`.
- `tags: list` says nothing about the contents. Stage 3 makes `list[str]` matter; write it now anyway.

</details>

3. ▢ Which of these can be a `set` member? For each `no`, give the one-word fix.

   - a) `@dataclass class A: x: int`
   - b) `@dataclass(frozen=True) class B: x: int`
   - c) `@dataclass(frozen=True) class C: xs: list`
   - d) `@dataclass(eq=False) class D: x: int`

<details markdown="1"><summary>Check</summary>

- a) No. `frozen=True`.
- b) Yes.
- c) It is hashable, and hashing one raises `TypeError: unhashable type: 'list'`, because the generated hash hashes the field tuple. Frozen freezes the attribute, not the list inside it, which is lesson 2 exactly. Fix: `tuple`.
- d) Yes, unexpectedly. With `eq=False` no `__eq__` is generated, so the class keeps `object`'s identity-based `__eq__` and `__hash__`. Two `D(1)` instances are then different set members, which is rarely what the author wanted.

</details>

4. ▢ Rewrite this class as a dataclass, keeping the behaviour identical.

   ```python
   class Invoice:
       def __init__(self, number, total, paid=False):
           self.number = number
           self.total = total
           self.paid = paid

       def __repr__(self):
           return f"Invoice({self.number!r}, {self.total!r}, {self.paid!r})"

       def __eq__(self, other):
           if not isinstance(other, Invoice):
               return NotImplemented
           return (self.number, self.total, self.paid) == (other.number, other.total, other.paid)
   ```

<details markdown="1"><summary>Check</summary>

```python
@dataclass
class Invoice:
    number: str
    total: float
    paid: bool = False
```

Two differences worth noticing. The generated `__repr__` uses `field=value` rather than positional, so it is not character-identical. And the original class, having defined `__eq__` without `__hash__`, was already unhashable, so that behaviour is preserved rather than changed.

</details>

5. ▢ A function takes `config: dict` and reads `config["retries"]`, `config["timeout"]` and `config["base_url"]`. Argue for changing the parameter to a frozen dataclass, and name the one case where the dict is right.

<details markdown="1"><summary>Check</summary>

For the dataclass: a misspelled key is a `KeyError` at run time in one branch, and an `AttributeError` a checker catches before the branch runs. The fields are documented by existing. A default lives in one place instead of at every `get`. And nothing downstream can add a key.

The dict is right when the keys are genuinely data: a mapping of feature names to values, read from a file, whose keys are not known when the code is written. The test is whether you could write the field names down. If you can, they belong in a class.

</details>

6. ▢ Why does the second call fail, and which flag fixes it?

   ```python
   @dataclass
   class Base:
       created: str = "now"

   @dataclass
   class Event(Base):
       name: str
   ```

<details markdown="1"><summary>Check</summary>

`TypeError: non-default argument 'name' follows default argument 'created'`, raised when `Event` is defined. Fields are collected base-first, so the generated `__init__` would be `(created="now", name)`, which is not valid Python.

`@dataclass(kw_only=True)` on both fixes it, because keyword-only parameters have no ordering constraint. The alternatives are giving `name` a default, which lies, or not putting the default in the base class.

</details>

## Real-world reps

- [ ] Find a class in code you own whose body is only `__init__` with assignments. Convert it to a dataclass and count the lines removed.
- [ ] Find a function that passes a dict of three or more known keys between two layers. Replace it with a frozen dataclass and see how many `get` calls and defaults disappear.
- [ ] Take one dataclass you already have and try `frozen=True`. Every failure is a place something mutates it. Decide whether each one wanted `replace` instead.
- [ ] Tomorrow: put `field(repr=False)` on one field that should never reach a log, and grep your logs for it to be sure it was reaching them.

## Going further

- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html): every parameter, `field`, `__post_init__`, `replace` and the frozen rules
- [PEP 557, Data Classes](https://peps.python.org/pep-0557/): the rationale, and the explicit decision not to validate
- [`typing.NamedTuple` and `TypedDict`](https://docs.python.org/3/library/typing.html): the two shapes in the table that a checker treats specially
- [`attrs`](https://www.attrs.org/en/stable/): the library dataclasses came from, for the cases the standard library caps
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
