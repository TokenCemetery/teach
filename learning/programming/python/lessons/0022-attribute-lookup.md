---
title: 22. Attribute Lookup
description: Where dot notation actually looks, and why a class attribute is shared by every instance
type: lesson
---

# Lesson 22. Attribute Lookup

**Mission link:** Almost every surprising behaviour in the data model is attribute lookup following a rule you did not know it had. One ordered list explains properties, methods, `__slots__`, and the shared-mutable-default bug at class level.
**Primary source:** [The Python Language Reference, Customizing attribute access](https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access)
**Prerequisites:** [Lesson 1](0001-names-are-bindings.md), [Lesson 12](0012-dataclasses.md)

## Warm-up

1. ▢ Lesson 6 covered the mutable default argument. What is the class-level version of that bug?

<details markdown="1"><summary>Check</summary>

A mutable class attribute, such as `items = []` in a class body. Every instance shares it, because it lives on the class.

</details>

2. ▢ Where does `obj.method` find the function, given that it is not in `obj.__dict__`?

<details markdown="1"><summary>Check</summary>

On the class. This lesson gives the exact order in which the two are consulted.

</details>

## Know this

An object's attributes live in a dict, and its class's attributes live in another:

```python
class Order:
    currency = "GBP"                 # class attribute: one, shared

    def __init__(self, amount):
        self.amount = amount         # instance attribute: one per object

o = Order(10)
o.__dict__                           # {'amount': 10}
Order.__dict__                       # contains 'currency', '__init__', ...
```

Reading `o.currency` finds nothing in the instance and falls back to the class. **Writing** `o.currency = "EUR"` does not touch the class: it creates an instance attribute that shadows it, which is lesson 1's rebinding at one level up.

```python
o.currency = "EUR"       # o.__dict__ now has it
Order.currency           # still "GBP"
del o.currency           # the shadow is gone; o.currency is "GBP" again
```

That asymmetry is the whole class-attribute trap. Reading through the class looks like it works; writing through an instance silently stops sharing.

### The lookup order

For `obj.name`, Python consults, in this order:

1. A **data descriptor** on the class or its bases: something defining `__get__` **and** `__set__`. It wins outright.
2. `obj.__dict__["name"]`.
3. A **non-data descriptor** (only `__get__`) or a plain class attribute, found along the class's method resolution order.
4. `__getattr__`, if the class defines one, as a last resort.

Verifying it is three lines:

```python
c.__dict__["d"] = "instance dict"    # d is a data descriptor
c.d                                  # "data descriptor": the class wins
c.n                                  # "instance dict": n is non-data, the instance wins
```

Two consequences to keep. A `property` is a data descriptor, which is why assigning to a property calls the setter instead of quietly creating an instance attribute. A plain method is a non-data descriptor, which is why `obj.method = something_else` works and shadows it.

### The class-attribute trap

```python
class Cart:
    items = []                       # shared by every Cart ever created

a, b = Cart(), Cart()
a.items.append("book")
b.items                              # ['book']
```

Nothing was assigned, so nothing shadowed: `a.items` read the class's list and mutated it in place. The same code with `a.items = ["book"]` would have behaved as expected, which is what makes this so hard to spot in review.

Mutable state belongs in `__init__`, or in a dataclass field with `default_factory` from lesson 12. A class attribute is correct for constants, and for anything genuinely shared and deliberate, such as a registry, which `ClassVar` from lesson 15 marks for a checker.

### `__getattr__` against `__getattribute__`

```python
class Config:
    debug = False

    def __getattr__(self, name):             # only for lookups that failed
        raise ConfigError(f"unknown setting: {name}")
```

`__getattr__` runs **only when normal lookup raised `AttributeError`**, which makes it cheap and safe for fallbacks, lazy loading, and better error messages.

`__getattribute__` intercepts **every** attribute access, including successful ones and including `self.anything` inside its own body, which recurses instantly unless you route through `object.__getattribute__`. It is the correct tool roughly never; reach for `__getattr__`, a property, or a descriptor.

### `__slots__`

```python
class Point:
    __slots__ = ("x", "y")

p = Point()
p.x = 1
p.z = 2          # AttributeError: 'Point' object has no attribute 'z'
                 #                 and no __dict__ for setting new attributes
hasattr(p, "__dict__")     # False
```

Declaring `__slots__` replaces the instance dict with fixed storage. Three effects: less memory per instance, marginally faster access, and a typo becomes an error instead of a new attribute. Two costs: no attributes beyond the declared ones, and a subclass without its own `__slots__` reintroduces the dict.

Worth it for objects created in large numbers, or where the typo protection matters. `@dataclass(slots=True)` from lesson 12 generates it.

### `hasattr`, `getattr`, `vars`

```python
getattr(obj, "amount", 0)        # like obj.amount, with a default
hasattr(obj, "amount")           # tries the lookup, catches AttributeError
vars(obj)                        # obj.__dict__
```

`hasattr` runs the lookup, so a property that raises makes it return `False` rather than propagating, which hides bugs. When the attribute name is a literal you typed, use the dot.

## Practice

1. ▢ Predict all four lines.

   ```python
   class Order:
       currency = "GBP"

   a, b = Order(), Order()
   a.currency = "EUR"
   print(a.currency, b.currency)
   Order.currency = "USD"
   print(a.currency, b.currency)
   ```

<details markdown="1"><summary>Check</summary>

```text
EUR GBP
EUR USD
```

`a` has its own shadowing instance attribute, so the later class-level change is invisible to it. `b` never assigned, so it still reads through to the class and sees `USD`.

</details>

2. ▢ Find the bug and give two fixes.

   ```python
   class Session:
       history = []

       def record(self, event):
           self.history.append(event)
   ```

<details markdown="1"><summary>Hint</summary>

Count how many lists exist after creating three sessions.

</details>

<details markdown="1"><summary>Check</summary>

One list, shared by every session, because `append` mutates the class attribute rather than assigning to the instance.

```python
class Session:
    def __init__(self):
        self.history: list[str] = []
```

or

```python
@dataclass
class Session:
    history: list[str] = field(default_factory=list)
```

The reason it survives review is that the code reads `self.history`, which looks per-instance and is not.

</details>

3. ▢ For each access, say which step of the lookup order answers it.

   ```python
   class Widget:
       size = 10
       @property
       def area(self): return self.size ** 2
       def draw(self): ...
       def __getattr__(self, name): return None

   w = Widget()
   w.__dict__["size"] = 20
   w.__dict__["area"] = 999
   ```

   - a) `w.size`
   - b) `w.area`
   - c) `w.draw`
   - d) `w.colour`

<details markdown="1"><summary>Check</summary>

- a) `20`, from the instance dict at step 2, because the class attribute is a plain value at step 3.
- b) `400`, from the property at step 1. A `property` is a data descriptor and beats the instance dict, so the `999` is unreachable.
- c) The bound method, at step 3. A function is a non-data descriptor, so an instance-dict entry would have won had one existed.
- d) `None`, from `__getattr__` at step 4, after the first three found nothing.

</details>

4. ▢ Why does this recurse forever, and what should it have been?

   ```python
   class Logged:
       def __getattribute__(self, name):
           print(f"reading {name}")
           return self.__dict__[name]
   ```

<details markdown="1"><summary>Check</summary>

`self.__dict__` is itself an attribute access, so it calls `__getattribute__` again, which accesses `self.__dict__` again.

Correct within `__getattribute__`:

```python
return object.__getattribute__(self, name)
```

But the honest answer is not to write `__getattribute__` at all. For logging missing attributes, `__getattr__` runs only on failure and cannot recurse this way. For one computed attribute, use a property.

</details>

5. ▢ Which of these classes benefits from `__slots__`?

   - a) A `Point` created a few million times while parsing a mesh
   - b) A `Service` object created once at start-up
   - c) A class that a plugin system adds attributes to at run time
   - d) A base class whose subclasses are written by other teams

<details markdown="1"><summary>Check</summary>

- a) Yes, and it is the case `__slots__` exists for.
- b) No measurable gain. The typo protection is a real but small argument.
- c) No: `__slots__` is precisely what forbids that.
- d) Careful. Subclasses without their own `__slots__` get a `__dict__` back, so the memory saving evaporates while the base's restriction remains. Document it or do not do it.

</details>

6. ▢ Why can `hasattr` return `False` for an attribute that exists?

<details markdown="1"><summary>Check</summary>

It performs the access and treats any `AttributeError` as absence. A property whose body raises `AttributeError`, directly or from a bug three calls deep, therefore reports the attribute as missing, and the underlying error is discarded.

That makes `hasattr` unsuitable as a general "does this exist" test on objects with properties. Prefer `getattr(obj, name, default)` when a default is what you want, and a plain access when you typed the name yourself and want the error.

</details>

## Real-world reps

- [ ] Grep class bodies in code you own for `= []`, `= {}` and `= set()`. Every one is shared, and each is either a bug or a deliberate registry that should say so.
- [ ] Print `obj.__dict__` and `type(obj).__dict__` for an object you find confusing. The split between the two usually answers the question.
- [ ] Find a `__getattribute__` in any codebase and work out whether `__getattr__` or a property would have done it.
- [ ] Add `__slots__`, or `@dataclass(slots=True)`, to the class you create the most of, and measure the memory difference rather than assuming it.
- [ ] Tomorrow: assign to a property in a class you own, and confirm the setter runs rather than a new instance attribute appearing.

## Going further

- [Customizing attribute access](https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access): `__getattr__`, `__getattribute__`, `__setattr__`, `__slots__`
- [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html): the lookup order derived from first principles, and why a property beats the instance dict
- [`__slots__`](https://docs.python.org/3/reference/datamodel.html#slots): the exact rules, including subclassing
- [`vars`, `getattr`, `hasattr`](https://docs.python.org/3/library/functions.html): what each one actually does
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
