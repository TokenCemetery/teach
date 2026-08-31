---
title: 23. Properties and Descriptors
description: Turning an attribute into code without changing a single caller
type: lesson
---

# Lesson 23. Properties and Descriptors

**Mission link:** A property is the reason Python code does not need getters and setters, and a descriptor is the mechanism underneath properties, methods, `classmethod` and `staticmethod`. Knowing the one protocol explains all four and removes the temptation to write accessors defensively.
**Primary source:** [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)
**Prerequisites:** [Lesson 22](0022-attribute-lookup.md)

## Warm-up

1. ▢ Lesson 22: which step of the lookup order does a `property` occupy, and what does that let it do?

<details markdown="1"><summary>Check</summary>

Step 1, as a data descriptor, so it beats the instance dict. That is what lets assignment run a setter rather than creating an attribute.

</details>

2. ▢ Why does Python code not usually have `get_amount()` and `set_amount()`?

<details markdown="1"><summary>Check</summary>

Because a plain attribute can become a property later without changing any caller. This lesson is how.

</details>

## Know this

Start with the plain attribute. It is the right first version:

```python
class Order:
    def __init__(self, amount: float) -> None:
        self.amount = amount
```

When it later needs behaviour, a property adds it with no change at any call site:

```python
class Order:
    def __init__(self, amount: float) -> None:
        self.amount = amount            # goes through the setter below

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"amount must not be negative, got {value}")
        self._amount = value
```

`order.amount` and `order.amount = 5` are unchanged for every caller, and the validation now cannot be bypassed. This is why writing accessors upfront is not caution in Python: it is a cost paid for a migration the language does not require.

Three good reasons for a property:

1. **Validation** on assignment, as above.
2. **A computed value** that reads like data: `order.total`, derived from lines and tax.
3. **A compatibility shim**: an attribute that moved or was renamed, kept working with a `DeprecationWarning`.

And two signals it is the wrong tool. If the body is slow or hits the network, a method named `fetch_total()` is honest, because `order.total` looks free and will be called in a loop. If there is no getter logic and no validation, delete it and use the attribute.

```python
from functools import cached_property

class Report:
    @cached_property
    def rows(self) -> list[Row]:
        return expensive_query()          # runs once per instance
```

`cached_property` stores the result in the instance dict under the same name, so later reads never reach the descriptor at all, which is lesson 22's step 2 doing the work. It needs a `__dict__`, so it does not combine with `__slots__`, and nothing invalidates it except `del instance.rows`.

### The descriptor protocol

A descriptor is any object implementing at least one of these, placed as a **class** attribute:

```python
class Field:
    def __set_name__(self, owner, name):     # called at class creation
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                      # accessed on the class
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
```

| Defines | Called | Kind |
|---|---|---|
| `__get__` only | on read | non-data descriptor: instance dict wins |
| `__get__` and `__set__` | on read and write | data descriptor: wins over instance dict |
| `__delete__` | on `del obj.attr` | |
| `__set_name__` | once, when the class body finishes | tells the descriptor its own name |

`__set_name__` is what makes reusable descriptors practical: the descriptor learns the attribute name it was assigned to, without the name being passed in twice.

```python
class Model:
    title = Field()          # __set_name__ receives ("title")
```

### Everything is a descriptor

This is the part that pays off:

| Construct | Actually is |
|---|---|
| a plain method | a function, which is a non-data descriptor; `__get__` returns a bound method |
| `@property` | a data descriptor written in C |
| `@classmethod`, `@staticmethod` | descriptors that bind differently, or not at all |
| `@cached_property` | a non-data descriptor that writes into the instance dict |
| `__slots__` entries | data descriptors, one per slot |

So `obj.method` is not a lookup that finds a function; it is a lookup that finds a descriptor and calls its `__get__`, which returns a new bound method with `self` attached. That single fact explains why methods can be shadowed by instance attributes, why `Class.method` gives a plain function while `obj.method` gives a bound one, and why a property cannot be shadowed at all.

### When to write your own

Almost never, and the exception is worth knowing: **the same non-trivial attribute behaviour on many attributes or many classes.** Five fields that all need range validation is a descriptor; one field is a property.

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name[1:]} must not be negative")
        setattr(obj, self.name, value)

class Invoice:
    amount = Positive()
    tax = Positive()
    shipping = Positive()
```

Before writing one, check the alternatives: a dataclass with `__post_init__` validates once at construction, which is enough when the object is frozen; `pydantic` does this generatively; and a plain property repeated three times is more readable than a descriptor nobody on the team has seen before.

## Practice

1. ▢ What breaks, and why?

   ```python
   class Order:
       @property
       def amount(self):
           return self.amount
   ```

<details markdown="1"><summary>Check</summary>

`RecursionError`. The getter reads `self.amount`, which is the property, which calls the getter.

A property must store the value somewhere else, conventionally an underscore-prefixed instance attribute: `return self._amount`, set by the setter or by `__init__`.

</details>

2. ▢ A colleague adds getters and setters to every field of a new class, "so we can add validation later". Answer them.

<details markdown="1"><summary>Hint</summary>

What has to change at the call sites when a plain attribute becomes a property?

</details>

<details markdown="1"><summary>Check</summary>

Nothing has to change. `obj.amount` keeps working when `amount` becomes a property, so the migration the accessors were protecting against does not exist in Python.

The cost of writing them now is real: three lines per field instead of zero, a `_name` for every public name, and readers who have to check whether each accessor does anything. Add the property on the day a field needs behaviour.

</details>

3. ▢ For each, say whether it is a data descriptor, a non-data descriptor, or neither.

   - a) `def method(self): ...` in a class body
   - b) `@property`
   - c) `@cached_property`
   - d) `size = 10` in a class body
   - e) `@staticmethod`

<details markdown="1"><summary>Check</summary>

- a) Non-data. A function has `__get__` only, which is why `obj.method = other` shadows it.
- b) Data. It has `__set__`, which is why assignment runs the setter.
- c) Non-data, deliberately: after the first read it writes into the instance dict, and every later read stops at step 2 without calling the descriptor.
- d) Neither: a plain class attribute at step 3.
- e) A descriptor whose `__get__` returns the underlying function unchanged, with no binding.

</details>

4. ▢ Why does this cache never expire, and what would you do about a stale value?

   ```python
   class Report:
       @cached_property
       def rows(self):
           return query_database()
   ```

<details markdown="1"><summary>Check</summary>

The first read stores the result in `self.__dict__["rows"]`, and every later read finds it at lookup step 2 without touching the descriptor. There is no invalidation hook and no time limit.

The available answers: `del report.rows` removes the instance-dict entry so the next read recomputes; create a new `Report` for a new point in time, which is usually the honest design; or use a real cache with a TTL if the lifetime matters. Note also that `cached_property` needs `__dict__`, so it is incompatible with `__slots__`.

</details>

5. ▢ Rewrite these three properties as one descriptor, and then argue whether you should.

   ```python
   class Config:
       @property
       def retries(self): return self._retries
       @retries.setter
       def retries(self, v):
           if not 0 <= v <= 10: raise ValueError("retries out of range")
           self._retries = v
       # ... the same twelve lines for timeout and workers
   ```

<details markdown="1"><summary>Check</summary>

```python
class InRange:
    def __init__(self, low: int, high: int) -> None:
        self.low, self.high = low, high

    def __set_name__(self, owner, name):
        self.attr = f"_{name}"

    def __get__(self, obj, objtype=None):
        return self if obj is None else getattr(obj, self.attr)

    def __set__(self, obj, value):
        if not self.low <= value <= self.high:
            raise ValueError(f"{self.attr[1:]} must be between {self.low} and {self.high}")
        setattr(obj, self.attr, value)

class Config:
    retries = InRange(0, 10)
    timeout = InRange(1, 300)
    workers = InRange(1, 64)
```

Should you: at three fields, yes, and the win grows with the fourth. Against it: a frozen dataclass validating everything in `__post_init__` is fewer concepts and is enough when the object never changes after construction. Choose the descriptor when values are assigned repeatedly over an object's life.

</details>

6. ▢ Why is `order.total` a bad name for something that queries a database, even though it works?

<details markdown="1"><summary>Check</summary>

Because attribute syntax communicates that reading is free. Callers put it inside loops, inside f-strings, inside log lines that are usually disabled, and inside comparisons, because nothing at the call site suggests otherwise. A property that takes 40 milliseconds becomes 40 seconds in a report over a thousand orders, and the code that caused it looks like it is reading data.

`order.fetch_total()` costs one pair of parentheses and tells the truth. `cached_property` is the middle answer when the value is stable for the object's lifetime.

</details>

## Real-world reps

- [ ] Find a getter and setter pair in code you own that do nothing but read and write. Replace them with a plain attribute and fix the callers, then note how few there were.
- [ ] Find a property whose body does real work, and time it. If it is not free, rename it to a method or wrap it in `cached_property`.
- [ ] Print `type(SomeClass.__dict__["method"])` and `type(SomeClass.__dict__["some_property"])` and confirm which is which kind of descriptor.
- [ ] Look for the same validation repeated across three or more attributes. That is the one case where writing a descriptor is the smaller change.
- [ ] Tomorrow: add a deprecation shim as a property, so a renamed attribute keeps working while warning.

## Going further

- [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html): builds properties, methods and `classmethod` from the protocol, and is the best page in the documentation on this
- [Implementing Descriptors](https://docs.python.org/3/reference/datamodel.html#implementing-descriptors): the reference statement, including `__set_name__`
- [`property`](https://docs.python.org/3/library/functions.html#property): the getter, setter and deleter forms
- [`functools.cached_property`](https://docs.python.org/3/library/functools.html#functools.cached_property): the caching semantics and the `__slots__` restriction
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
