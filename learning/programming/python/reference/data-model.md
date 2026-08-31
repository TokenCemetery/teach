---
title: Data Model
description: Attribute lookup order, the dunder map, the descriptor protocol, and which hook replaces a metaclass
type: reference
---

# Data Model

Lookup sheet for stage 4. The question it exists to answer: **which method does this construct call, and where does the lookup go?**

## Attribute lookup, for `obj.name`

1. A **data descriptor** on the class or its bases: defines `__get__` **and** `__set__`. Wins outright.
2. `obj.__dict__["name"]`.
3. A **non-data descriptor** (`__get__` only) or a plain class attribute, along the MRO.
4. `__getattr__`, if defined, as a last resort.

Assignment `obj.name = v` goes to a data descriptor's `__set__` if one exists, otherwise straight into `obj.__dict__`, shadowing any class attribute.

| Construct | Kind | Consequence |
|---|---|---|
| `@property` | data | assignment runs the setter; cannot be shadowed |
| a method | non-data | `obj.method = f` shadows it |
| `@cached_property` | non-data | writes into the instance dict, so later reads stop at step 2 |
| `@classmethod`, `@staticmethod` | descriptors | bind differently, or not at all |
| `__slots__` entries | data | one descriptor per slot |
| `size = 10` | neither | plain class attribute at step 3 |

`__getattr__` runs only after failure. `__getattribute__` intercepts every access, including `self.x` inside itself, so it recurses unless it calls `object.__getattribute__`.

## Class against instance attributes

```python
class Cart:
    items = []              # one list, shared by every instance
```

- Reading falls through to the class; **writing** creates an instance attribute and stops sharing.
- `a.items.append(x)` mutates the shared one, because nothing was assigned.
- Mutable state belongs in `__init__` or `field(default_factory=...)`.
- Deliberately shared state should be annotated `ClassVar[...]`.

## The descriptor protocol

| Method | Called |
|---|---|
| `__set_name__(self, owner, name)` | once, when the class body finishes |
| `__get__(self, obj, objtype=None)` | on read; `obj` is `None` when accessed on the class |
| `__set__(self, obj, value)` | on write; its presence makes the descriptor a data descriptor |
| `__delete__(self, obj)` | on `del obj.attr` |

Write one when the same non-trivial attribute behaviour is needed on **several** attributes or classes. For one attribute, use a property. For validate-once, use a frozen dataclass with `__post_init__`.

## Dunder map, by what you want

| Want | Implement | Falls back to |
|---|---|---|
| useful printing in logs and tracebacks | `__repr__` | |
| user-facing text | `__str__` | `__repr__` |
| `==`, dict and set membership | `__eq__` **and** `__hash__` | identity |
| `<`, sorting | `__lt__` plus `@total_ordering` | |
| `len(x)` | `__len__` | |
| `bool(x)` | `__bool__` | `__len__`, then always `True` |
| `for`, `list`, `sum` | `__iter__` | `__getitem__` from 0 until `IndexError` |
| `item in x` | `__contains__` | `__iter__` |
| `x[k]`, slicing | `__getitem__` | |
| `with` | `__enter__`, `__exit__` | |
| `async with`, `await` | `__aenter__`, `__aexit__`, `__await__` | |
| `x()` | `__call__` | |
| `+`, `-`, `*` | `__add__`, `__sub__`, `__mul__`, and the `__r*__` forms | |
| `+=` in place | `__iadd__`, returning `self` | `__add__` then rebinding |
| `f"{x:>10.2f}"` | `__format__` | `__str__` |
| attribute fallback | `__getattr__` | |

### Equality contract

1. Equal objects must hash equal.
2. A hash must not change while the object is in a dict or set.
3. Defining `__eq__` sets `__hash__ = None`: instances become unhashable until you define it.
4. Return `NotImplemented`, not `False`, for an unrecognised type, or comparison becomes asymmetric.

`@dataclass(frozen=True)` generates all of this correctly and is the right default.

## Construction

```python
obj = Cls.__new__(Cls, *args)      # creates
if isinstance(obj, Cls):
    obj.__init__(*args)            # configures, returns None
```

`__new__` is required only for:

- subclassing an immutable type (`str`, `int`, `float`, `tuple`, `bytes`, `frozenset`);
- returning an existing instance, remembering that `__init__` still runs on it;
- controlling allocation, `copy` or `pickle` machinery.

Otherwise use `__init__`, and give every alternative way of building the object a name:

```python
@classmethod
def from_row(cls, row): return cls(...)
```

`__del__` has unspecified timing, may run at shutdown with globals gone, may never run for cycles, and swallows exceptions. Use a context manager.

## Inheritance

```python
[k.__name__ for k in D.__mro__]    # the exact lookup order
```

C3 linearisation guarantees: a class precedes its bases, declared base order is kept, each class appears once. When no such order exists:

```text
TypeError: Cannot create a consistent method resolution order (MRO) for bases A, C
```

`super()` means **the next class after this one in the instance's MRO**, not the base class. In a cooperative hierarchy every override must call `super()` exactly once and forward `**kwargs`; one that does not silently truncates the chain.

| Need | Use |
|---|---|
| shape only, classes you do not own | `Protocol` |
| shared implementation, classes you own | `abc.ABC` with `@abstractmethod` |
| behaviour added to specific classes | composition, or a mixin before the base |
| a dict-like or list-like type | hold one, or `collections.UserDict` / `UserList` |

Subclassing `dict`, `list` or `str` does not route their internal operations through your overrides. Verified: with `__setitem__` overridden on a `dict` subclass, `d["a"] = 1` calls it while `update`, `setdefault` and the constructor do not.

## Class creation hooks, in order of preference

| Goal | Hook |
|---|---|
| register or validate every subclass | `__init_subclass__` |
| a class attribute needs to know its name | `__set_name__` |
| refuse instantiation until a method exists | `abc.ABC` and `@abstractmethod` |
| generate methods for specific classes | `@dataclass`, or a class decorator |
| affect subclasses that never opt in | `__init_subclass__`, else a metaclass |

A metaclass is required only for: `__prepare__` (a non-dict class-body namespace), `__instancecheck__` or `__subclasshook__`, customising the class object itself including `__call__`, and reaching a hierarchy whose base was not written with a hook.

Its cost is concrete:

```text
TypeError: metaclass conflict: the metaclass of a derived class must be a
(non-strict) subclass of the metaclasses of all its bases
```

Two bases with different metaclasses cannot be combined, and a user of two libraries cannot fix that.

## Diagnosing unfamiliar magic

```python
type(SomeClass)          # the metaclass, if any
SomeClass.__mro__        # where an inherited name came from
SomeClass.__dict__       # what this class defines, versus inherits
vars(obj)                # the instance dict
```

## Sources

- [Data model](https://docs.python.org/3/reference/datamodel.html)
- [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)
- [The Python 2.3 Method Resolution Order](https://docs.python.org/3/howto/mro.html)
- [`abc`](https://docs.python.org/3/library/abc.html), [`collections.abc`](https://docs.python.org/3/library/collections.abc.html)
- [PEP 487, Simpler customisation of class creation](https://peps.python.org/pep-0487/)
