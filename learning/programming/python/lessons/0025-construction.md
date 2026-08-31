---
title: 25. Construction
description: What __init__ does not control, when __new__ is required, and naming your constructors
type: lesson
---

# Lesson 25. Construction

**Mission link:** Most classes need only `__init__`, and the ones that need `__new__` need it for a specific, recognisable reason. Knowing which is which prevents both the copied `__new__` nobody can explain and the constructor that takes eleven arguments because nobody named the alternatives.
**Primary source:** [The Python Language Reference, Basic customization](https://docs.python.org/3/reference/datamodel.html#basic-customization)
**Prerequisites:** [Lesson 12](0012-dataclasses.md), [Lesson 22](0022-attribute-lookup.md)

## Warm-up

1. ▢ Lesson 12: where does validation go in a dataclass?

<details markdown="1"><summary>Check</summary>

`__post_init__`, which runs after the generated `__init__`.

</details>

2. ▢ What does `Order(10)` do, in two steps?

<details markdown="1"><summary>Check</summary>

Creates the object, then initialises it. Those are two different methods, which is the subject of this lesson.

</details>

## Know this

`Order(10)` calls the class, and the class's type runs two methods:

```python
obj = Order.__new__(Order, 10)       # allocate and return an instance
if isinstance(obj, Order):
    obj.__init__(10)                 # initialise it, return None
```

`__new__` **creates**, `__init__` **configures**. `__new__` receives the class and returns an instance; `__init__` receives the instance and returns `None`. If `__new__` returns something that is not an instance of the class, `__init__` is skipped entirely, which is a real source of confusion in code that returns a cached object.

For ordinary classes, only `__init__` is needed. The default `__new__` does the right thing and there is no reason to touch it.

### Three cases where `__new__` is required

**Subclassing an immutable type.** By the time `__init__` runs, the value already exists and cannot be changed:

```python
class Upper(str):
    def __new__(cls, value: str):
        return super().__new__(cls, value.upper())

Upper("abc")        # 'ABC'
```

The same applies to `int`, `float`, `tuple`, `bytes` and `frozenset`. Doing this in `__init__` has no effect, because `self` is already the finished string.

**Returning an existing instance**, such as a cache or a singleton. Note the consequence: `__init__` still runs on the cached instance unless you guard it, which quietly reinitialises shared state.

**Controlling allocation**, which in practice means `__slots__` interacting with immutable bases, `copy` and `pickle` protocols, and metaclass-adjacent machinery. If you are not doing one of those, you do not need it.

Everything else that looks like a reason usually is not. "Validate before creating" is `__init__` raising, which is equivalent from the caller's side. "Return a subclass depending on the arguments" is a classmethod or a module-level function, which is both clearer and inspectable.

### Named constructors beat argument soup

```python
@dataclass(frozen=True)
class Order:
    id: int
    amount: Decimal
    country: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Order":
        return cls(id=row["id"], amount=Decimal(row["amount"]), country=row["country"])

    @classmethod
    def from_json(cls, payload: dict[str, object]) -> "Order":
        ...
```

`__init__` takes the canonical fields, and every other way of building the object gets a name. Three properties make this better than one flexible constructor: the name says which source the data came from, each one can validate what only it can validate, and `cls` rather than `Order` means subclasses get working constructors for free.

This is the standard library's own pattern: `dict.fromkeys`, `datetime.fromisoformat`, `Decimal.from_float`, `Path.cwd`, `int.from_bytes`.

### `__init_subclass__`, the hook that replaces most metaclasses

```python
class Plugin:
    registry: ClassVar[dict[str, type["Plugin"]]] = {}

    def __init_subclass__(cls, /, name: str, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        Plugin.registry[name] = cls

class CsvPlugin(Plugin, name="csv"): ...
class JsonPlugin(Plugin, name="json"): ...

Plugin.registry        # {'csv': <class 'CsvPlugin'>, 'json': <class 'JsonPlugin'>}
```

It runs once per subclass, at class-creation time, and receives keyword arguments passed in the class header. Registration, subclass validation, and "every subclass must define `handles`" all live here, and none of them need a metaclass. Lesson 27 makes that argument fully.

`__set_name__`, from lesson 23, is the same idea for descriptors: a class-creation hook instead of a metaclass.

### `__del__` is not a destructor

```python
def __del__(self):
    self.file.close()          # do not rely on this
```

`__del__` runs when the object is collected, which is unspecified in timing, may be at interpreter shutdown when module globals are already gone, and never happens at all for objects in a reference cycle in some situations. Exceptions raised inside it are printed and swallowed.

Release resources with a context manager from lesson 11. `__del__` is acceptable as a last-resort warning that something was not closed, and unacceptable as the mechanism that closes it.

## Practice

1. ▢ Why does this print `abc` rather than `ABC`?

   ```python
   class Upper(str):
       def __init__(self, value):
           self = value.upper()

   print(Upper("abc"))
   ```

<details markdown="1"><summary>Check</summary>

Two independent reasons, and both are worth seeing.

`str` is immutable, so by the time `__init__` runs the string already exists with the original characters. And assigning to `self` rebinds a local name, which is lesson 1: it cannot change what the caller received.

The fix is `__new__`, because creation is the only moment an immutable value can be chosen.

</details>

2. ▢ Find the bug.

   ```python
   class Connection:
       _instance = None

       def __new__(cls, dsn):
           if cls._instance is None:
               cls._instance = super().__new__(cls)
           return cls._instance

       def __init__(self, dsn):
           self.dsn = dsn
           self.pool = []
   ```

<details markdown="1"><summary>Hint</summary>

Create two connections with different arguments, then look at the first one.

</details>

<details markdown="1"><summary>Check</summary>

`__init__` runs on **every** call, including the ones that returned the cached instance. So `Connection("db2")` reassigns `dsn` on the single shared object and replaces `pool` with an empty list, silently discarding whatever the first caller was using.

Guards exist (`if hasattr(self, "dsn"): return`), and they make a confusing class more confusing. The better answers: a module-level function returning a memoised connection, `functools.cache` on a factory function, or dependency injection so the object's lifetime is the caller's decision.

</details>

3. ▢ Which of these need `__new__`?

   - a) A `Celsius` class that rejects values below absolute zero
   - b) A `Duration` subclass of `int` that stores seconds and clamps negatives to zero
   - c) A `Colour` class returning a shared instance for each named colour
   - d) A `Config` class assembled from three different file formats

<details markdown="1"><summary>Check</summary>

- a) No. Raise in `__init__`, or use `__post_init__` in a dataclass.
- b) Yes. `int` is immutable, so the value must be chosen at creation.
- c) Yes, technically, and consider not doing it: a module-level `by_name` dict or a cached factory function achieves the same interning without hiding it in the constructor.
- d) No. Three classmethods, `from_toml`, `from_json`, `from_env`, each with a name.

</details>

4. ▢ Replace this with named constructors, and say what improves.

   ```python
   class Order:
       def __init__(self, row=None, payload=None, id=None, amount=None):
           if row is not None:
               self.id, self.amount = row["id"], Decimal(row["amount"])
           elif payload is not None:
               self.id, self.amount = payload["id"], Decimal(str(payload["amount"]))
           else:
               self.id, self.amount = id, amount
   ```

<details markdown="1"><summary>Check</summary>

```python
@dataclass(frozen=True)
class Order:
    id: int
    amount: Decimal

    @classmethod
    def from_row(cls, row) -> "Order":
        return cls(id=row["id"], amount=Decimal(row["amount"]))

    @classmethod
    def from_payload(cls, payload) -> "Order":
        return cls(id=payload["id"], amount=Decimal(str(payload["amount"])))
```

What improves: every parameter is now required and typed, so a checker can verify the call; `Order()` with no arguments is no longer legal; the three code paths cannot be reached by accident; and each converter can raise a message naming its own source. The `if/elif` chain also had a fourth reachable state, all arguments `None`, which produced an object with `id=None`.

</details>

5. ▢ What replaces a metaclass here, and why is it better?

   Requirement: every subclass of `Handler` must define a `route` attribute, and must register itself in a lookup table.

<details markdown="1"><summary>Check</summary>

```python
class Handler:
    registry: ClassVar[dict[str, type["Handler"]]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "route", None):
            raise TypeError(f"{cls.__name__} must define a route")
        Handler.registry[cls.route] = cls
```

Better because it is ordinary code in the ordinary place: readers find it in the class they already have open, it does not change the class's type, it composes with other base classes without metaclass conflicts, and both the check and the registration run at import time where the error is easy to attribute.

</details>

6. ▢ A colleague closes a file in `__del__` "as a safety net". What do you tell them?

<details markdown="1"><summary>Check</summary>

That it is not a net. Its timing is unspecified, so the file can stay open long past the last use; at interpreter shutdown the module globals it needs may already be `None`; an object in a reference cycle may never reach it; and any exception it raises is printed and discarded, so a failure to flush is invisible.

The mechanism is a context manager, which runs on every path out of the block. `__del__` is defensible only as a warning: log that something was not closed, so the missing `with` gets fixed.

</details>

## Real-world reps

- [ ] Search code you own for `__new__` and, for each, decide which of the three legitimate reasons applies. Any that match none can become `__init__`.
- [ ] Find a constructor with mutually exclusive optional parameters and split it into named classmethods. Count how many arguments each one needs.
- [ ] Find a class with a registry populated by a decorator or a metaclass and try `__init_subclass__` instead.
- [ ] Look for `__del__` in any codebase and check what it releases. If it is a resource, find out whether callers use a `with`.
- [ ] Tomorrow: subclass `str` or `int` for a domain value and confirm that only `__new__` can shape it.

## Going further

- [Basic customization](https://docs.python.org/3/reference/datamodel.html#basic-customization): `__new__`, `__init__`, `__del__` and their contracts
- [`__init_subclass__`](https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__): the class-creation hook, and how keyword arguments reach it
- [PEP 487, Simpler customisation of class creation](https://peps.python.org/pep-0487/): the case for `__init_subclass__` and `__set_name__` over metaclasses
- [`object.__del__`](https://docs.python.org/3/reference/datamodel.html#object.__del__): the documented warnings about timing and shutdown
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
