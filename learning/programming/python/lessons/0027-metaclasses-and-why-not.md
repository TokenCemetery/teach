---
title: 27. Metaclasses, and Why Not
description: What a class statement actually does, and the four hooks that replace almost every metaclass
type: lesson
---

# Lesson 27. Metaclasses, and Why Not

**Mission link:** The mission asks you to name precisely why someone's metaclass is the wrong tool. That requires knowing what a metaclass does, what the cheaper hooks do, and the small set of cases where nothing else works.
**Primary source:** [The Python Language Reference, Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses)
**Prerequisites:** [Lesson 25](0025-construction.md), [Lesson 26](0026-inheritance-and-mro.md)

## Warm-up

1. ▢ Lesson 25 gave a hook that runs once per subclass at class-creation time. Which, and what did it replace?

<details markdown="1"><summary>Check</summary>

`__init_subclass__`, which covers registration and subclass validation without a metaclass.

</details>

2. ▢ What is `type(Order)`, for an ordinary class `Order`?

<details markdown="1"><summary>Check</summary>

`type`. A class is an object, and its type is its metaclass. That is the whole idea this lesson is about.

</details>

## Know this

A `class` statement is not a declaration; it is code that runs. Roughly:

```python
class Order:
    currency = "GBP"
    def total(self): ...
```

is:

```python
namespace = {}                        # execute the body into a dict
exec(class_body, globals(), namespace)
Order = type("Order", (), namespace)  # call the metaclass to build the class
```

`type` is the default metaclass. Calling it with three arguments, name, bases and namespace, builds a class, which is why `type(Order)` is `type` and why classes can be created at run time.

A **metaclass** replaces that call:

```python
class Meta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls

class Order(metaclass=Meta): ...
```

Now `type(Order)` is `Meta`, and `Meta` gets to inspect or alter every class that uses it, including subclasses.

### The four hooks that come first

Almost every real use of a metaclass is one of these, and each has a cheaper answer:

| Goal | Hook | Lesson |
|---|---|---|
| register every subclass | `__init_subclass__` | 25 |
| require subclasses to define something | `__init_subclass__` | 25 |
| tell a class attribute its own name | `__set_name__` | 23 |
| refuse instantiation until a method exists | `abc.ABC` with `@abstractmethod` | 26 |
| generate `__init__`, `__eq__`, `__repr__` | `@dataclass`, or a class decorator | 12 |
| add or wrap methods after class creation | a class decorator | this lesson |

A class decorator is the one to reach for when the change happens after the class exists:

```python
def slots_checked(cls):
    if not hasattr(cls, "__slots__"):
        raise TypeError(f"{cls.__name__} must define __slots__")
    return cls

@slots_checked
class Point:
    __slots__ = ("x", "y")
```

It runs once, it is visible directly above the class, it composes by stacking, and it does not change the class's type. Compared with a metaclass it gives up exactly one thing: it does not apply automatically to subclasses.

That single difference is the honest decision rule. **If subclasses must be affected without opting in, you need `__init_subclass__` or a metaclass. Otherwise a decorator does it.**

### What only a metaclass can do

Four things, and they are recognisable:

1. **Control the class body's namespace before it executes**, via `__prepare__`. This is how a framework makes a class body record declaration order in something other than a dict, or rejects duplicate names.
2. **Change what `isinstance` and `issubclass` answer**, via `__instancecheck__` and `__subclasshook__` on the metaclass. `abc` itself is built this way.
3. **Customise the class object's own behaviour**: attributes on the class rather than on instances, a `__repr__` for the class, a `__call__` that changes what `Order(...)` does before `__new__` is reached, or `__getattr__` for class-level attribute access.
4. **Apply behaviour to a whole hierarchy the base class did not anticipate**, because a metaclass is inherited and `__init_subclass__` requires the base to have been written with the hook.

These are framework problems. `abc`, `enum`, and ORMs use metaclasses correctly, and they all exist to make ordinary code not need one.

### The costs, concretely

- **Type conflicts.** Two bases with different metaclasses cannot be combined: `TypeError: metaclass conflict`. This shows up as a library being uncombinable with another library, and there is no fix on the user's side.
- **Invisible action at a distance.** A reader of the subclass sees no indication that anything happens; the behaviour lives in a class they may not know exists.
- **Tooling.** Checkers, editors and refactoring tools reason poorly about attributes a metaclass creates, so a codebase built this way loses the stage-3 benefits.
- **Debuggability.** The stack trace at class-creation time is at import time, and the failure often surfaces as a missing attribute much later.

### Reading one

You will meet metaclasses in other people's code, so recognise the shape:

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return {}                            # the namespace the body executes into

    def __new__(mcls, name, bases, namespace, **kwargs):
        return super().__new__(mcls, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):      # runs when the class is called
        return super().__call__(*args, **kwargs)
```

`__prepare__`, then the body executes, then `__new__`, then `__init__`. The `cls` in the last two methods is the class being built, and `mcls` is the metaclass. `__call__` is the one that surprises people: it intercepts instance creation before `__new__` from lesson 25 is reached, which is where singleton metaclasses live.

Two lines answer most questions about unfamiliar code: `type(SomeClass)` names the metaclass, and `SomeClass.__mro__` shows what it inherited.

### The rule, stated once

Write a metaclass when you are building a framework whose users must not have to opt in, and you have checked that `__init_subclass__`, `__set_name__`, `abc` and a class decorator cannot do it. Otherwise the metaclass is a cost paid by every future reader for a feature that had a simpler spelling.

## Practice

1. ▢ Rewrite without a metaclass.

   ```python
   class RegistryMeta(type):
       registry = {}
       def __new__(mcls, name, bases, ns, **kw):
           cls = super().__new__(mcls, name, bases, ns)
           if bases:
               RegistryMeta.registry[name.lower()] = cls
           return cls

   class Handler(metaclass=RegistryMeta): ...
   class CsvHandler(Handler): ...
   ```

<details markdown="1"><summary>Check</summary>

```python
class Handler:
    registry: ClassVar[dict[str, type["Handler"]]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        Handler.registry[cls.__name__.lower()] = cls

class CsvHandler(Handler): ...
```

Identical behaviour, fewer concepts, `type(Handler)` is still `type`, and the registry lives in the class a reader already has open. The `if bases` guard disappears too, because `__init_subclass__` does not run for the class that defines it.

</details>

2. ▢ Decorator or `__init_subclass__`?

   - a) Validate that a class defines `__slots__`, applied to twelve specific classes
   - b) Ensure every subclass of `Model` in the codebase, present and future, registers its table
   - c) Add `__repr__` to a handful of legacy classes
   - d) Require every subclass written by another team to implement `handle`

<details markdown="1"><summary>Check</summary>

- a) Decorator. Twelve explicit opt-ins are a feature, not a limitation.
- b) `__init_subclass__`. "Future subclasses without opting in" is exactly the line where a decorator stops working.
- c) Decorator, or write the method. The set is closed and small.
- d) `__init_subclass__`, or `abc.ABC` with `@abstractmethod` if the check should happen at instantiation instead of at class creation. The other team cannot forget to apply a hook they never see.

</details>

3. ▢ Two libraries each provide a base class, and combining them fails. What does the error say, and what can a user do?

<details markdown="1"><summary>Hint</summary>

What has to be true of the type of the new class, with respect to the types of both bases?

</details>

<details markdown="1"><summary>Check</summary>

```text
TypeError: metaclass conflict: the metaclass of a derived class must be a
(non-strict) subclass of the metaclasses of all its bases
```

The user's options are all bad: write a third metaclass inheriting from both, if they happen to be compatible, which requires understanding two libraries' internals; drop one of the two bases and reimplement its behaviour by composition; or open an issue and wait.

This is the concrete cost of a metaclass in a published library, and it is why frameworks that can use `__init_subclass__` should.

</details>

4. ▢ Which of these genuinely needs a metaclass?

   - a) A singleton, so `Connection()` always returns the same object
   - b) A class body that must record the order in which fields were declared
   - c) Changing what `isinstance(x, Shape)` answers for classes that merely have the right methods
   - d) Generating `__init__` from annotations

<details markdown="1"><summary>Check</summary>

- a) No. A module-level factory with `functools.cache`, or explicit lifetime management by the caller, and lesson 25 gave the bug a singleton `__new__` produces.
- b) No longer. Class bodies have executed into an ordered dict since Python 3.7, so `__init_subclass__` or a decorator can read the order. `__prepare__` is needed only for a namespace that is not a plain dict, such as one rejecting duplicates.
- c) **Yes.** `__instancecheck__` and `__subclasshook__` live on the metaclass, which is how `abc` and `Protocol` do it. Prefer using `abc` or `Protocol` rather than writing your own.
- d) No. `@dataclass` is a decorator, and that is the proof it does not need one.

</details>

5. ▢ You inherit a codebase and a class behaves in a way its body does not explain. Give the two lines you run first.

<details markdown="1"><summary>Check</summary>

```python
type(SomeClass)          # names the metaclass, if any
SomeClass.__mro__        # names every base, in lookup order
```

The first says whether class creation was intercepted. The second says which base a surprising attribute or method actually came from. After those, `SomeClass.__dict__` versus the same on each base separates what this class defines from what it inherited, and `inspect.getsource(type(SomeClass))` shows the metaclass itself.

</details>

6. ▢ A colleague proposes a metaclass so that all models automatically validate their fields on assignment. Give a fuller answer than "no".

<details markdown="1"><summary>Check</summary>

Name what the requirement actually is, then price the options.

Validation on assignment is a descriptor's job, from lesson 23: one `Field` descriptor with `__set__`, declared per attribute. If the objection is that every model must get it without writing the descriptors out, `__init_subclass__` can walk the annotations and install descriptors, which needs no metaclass because the models all inherit a base you control.

If the models should be immutable instead, a frozen dataclass validating in `__post_init__` removes the whole problem, since there is no assignment to intercept.

The metaclass wins only if the models must not inherit from a common base, which for a codebase's own models is rarely a real constraint. And it costs the metaclass conflict from question 3 the first time a model also needs a base from another library.

</details>

## Real-world reps

- [ ] Run `type(cls)` over the classes in one dependency you use heavily. The ones that are not `type` are where the framework's magic lives.
- [ ] Find a metaclass in any codebase and decide which of the four legitimate capabilities it uses. Most use none.
- [ ] Take one metaclass, if you have one, and try rewriting it as `__init_subclass__` plus a class decorator. Keep whichever version a new reader would understand faster.
- [ ] Read the first thirty lines of `enum.py` or `abc.py` in the standard library. Both are metaclasses done for a reason, and both exist so your code does not need one.
- [ ] Tomorrow: write a class decorator that adds one thing, and stack two of them, to see how composition works where inheritance of metaclasses does not.

## Going further

- [Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses): `__prepare__`, the creation sequence, and the conflict rule
- [PEP 487, Simpler customisation of class creation](https://peps.python.org/pep-0487/): the explicit argument for the hooks over metaclasses
- [`abc`](https://docs.python.org/3/library/abc.html): a correct metaclass, and `__subclasshook__`
- [`type`](https://docs.python.org/3/library/functions.html#type): the three-argument form that builds a class
- [`inspect`](https://docs.python.org/3/library/inspect.html): reading the source of whatever is doing the magic
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
