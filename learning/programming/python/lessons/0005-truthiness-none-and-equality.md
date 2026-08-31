---
title: 5. Truthiness, None and Equality
description: Empty is falsy but not None, so the wrong default idiom rejects zero and the empty string
type: lesson
---

# Lesson 5. Truthiness, None and Equality

**Mission link:** Two idioms that read as "if this has a value" behave differently on `0`, `""` and `[]`. Choosing between them by feel produces bugs that only appear on valid input.
**Primary source:** [The Python Standard Library, Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
**Prerequisites:** [Lesson 1](0001-names-are-bindings.md), [Lesson 4](0004-dicts-and-sets.md)

## Warm-up

1. ▢ You need to know whether an optional setting was provided at all, as opposed to reading it with a fallback. Which dictionary idiom says that?

<details markdown="1"><summary>Check</summary>

`if "key" in config:`. Both `get` spellings answer a different question, because they cannot distinguish absent from present.

</details>

2. ▢ What is the difference between `a is b` and `a == b`?

<details markdown="1"><summary>Check</summary>

`is` asks whether they are the same object. `==` asks whether they are equal, as the type defines equality.

</details>

## Know this

Every object in Python can be used in a boolean context, and each type decides for itself what that means ([truth value testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)).

**Falsy:** `False`, `None`, zero of any numeric type (`0`, `0.0`, `0j`), and every empty container (`""`, `()`, `[]`, `{}`, `set()`, `range(0)`).
**Truthy:** everything else, including `"0"`, `"False"`, `[0]`, `{}` with anything in it, and any object of a class that does not say otherwise.

The two strings in that list of truthy values are worth a second look. `"0"` is a non-empty string, so it is true.

### `if x:` and `if x is not None:` are different questions

```python
def apply(retries=None):
    if retries:                 # WRONG when retries == 0
        ...
    if retries is not None:     # asks whether an argument was given
        ...
```

Pass `retries=0` and the first branch is skipped, even though `0` was a deliberate, valid choice. The same trap applies to `""` as a deliberate empty prefix, and to `[]` as a deliberate empty list.

Use `if x:` when you mean "is there anything here", which is the right question for a container you are about to iterate. Use `if x is not None:` when you mean "was a value supplied", which is the right question for an optional parameter.

`None` is a singleton, so `is` is the correct operator for it and `== None` is discouraged: a class can define `__eq__` to claim equality with anything, and `is None` cannot be lied to.

### The `or` default trap

```python
def connect(timeout=None):
    timeout = timeout or 30     # rejects 0
```

`or` returns its first truthy operand, so `0 or 30` is `30`. The caller asked for no timeout and got thirty seconds. This idiom is fine when zero and empty are genuinely not valid inputs, and a bug the moment they are. The safe spelling is explicit:

```python
timeout = 30 if timeout is None else timeout
```

`and` and `or` return one of their operands rather than a boolean, and both short-circuit: the right side is not evaluated if the left settles the answer. That is what makes `if data and data[0]` safe on an empty list.

### Equality is defined by the type

```python
1 == 1.0            # True, numeric types compare across types
True == 1           # True, bool is a subclass of int
"1" == 1            # False, no implicit conversion between str and int
[1, 2] == [1, 2]    # True, sequences compare element by element
```

Python does not coerce strings and numbers for comparison, so `"1" == 1` is simply false rather than an error or a surprise.

Comparisons chain, and they mean what mathematical notation means:

```python
0 <= x < 10         # one expression, x evaluated once
```

Ordering comparisons between unrelated types raise `TypeError`, which is deliberate: `1 < "a"` is a bug, not a question.

## Practice

1. ▢ Which of these are falsy?

   ```python
   0, "0", [], [[]], "", " ", {}, {0: 0}, None, False, 0.0, "False"
   ```

<details markdown="1"><summary>Check</summary>

Falsy: `0`, `[]`, `""`, `{}`, `None`, `False`, `0.0`.

Truthy: `"0"`, `[[]]` (a list holding one item), `" "` (a space is a character), `{0: 0}`, `"False"`.

The pair to internalise is `""` against `" "`, and `[]` against `[[]]`: emptiness is about the container, not about what the contents look like.

</details>

2. ▢ Predict what this prints for each call: `apply()`, `apply(0)`, `apply(5)`.

   ```python
   def apply(retries=None):
       if retries:
           print("using", retries)
       else:
           print("using default")
   ```

<details markdown="1"><summary>Hint</summary>

Two of the three calls take the same branch. Ask which values are falsy, not which values are `None`.

</details>

<details markdown="1"><summary>Check</summary>

`apply()` prints `using default`. `apply(0)` prints `using default`. `apply(5)` prints `using 5`.

The middle one is the bug: the caller explicitly asked for zero retries and was overruled. The condition should be `if retries is not None:`.

</details>

3. ▢ Fix this line so that a caller can ask for no timeout at all, and say why the original fails.

   ```python
   timeout = timeout or 30
   ```

<details markdown="1"><summary>Check</summary>

`timeout = 30 if timeout is None else timeout`.

The original fails because `or` tests truthiness, and `0` is falsy, so `0 or 30` evaluates to `30`. The replacement tests the only thing that actually means "not supplied".

</details>

4. ▢ Which comparison is correct for detecting that an optional argument was omitted?

   - a) `if value == None:`
   - b) `if value is None:`
   - c) `if not value:`
   - d) `if value != True:`

<details markdown="1"><summary>Check</summary>

**b)** `if value is None:`.

Option a asks the object for its opinion via `__eq__`, which a class can answer dishonestly. Option c is truthiness and rejects `0` and `""`. Option d asks an unrelated question and is true for almost every value.

</details>

5. ▢ Both lines below are common in real code. For each, say what input makes it wrong.

   ```python
   if len(items) > 0:
       ...
   if items != []:
       ...
   ```

<details markdown="1"><summary>Check</summary>

Neither is wrong for a list, and both are worse than `if items:`.

`len(items) > 0` fails on anything that has no length, such as a generator, where `if items:` is also misleading and the correct answer is to try to consume it. `items != []` compares against a specific type, so it is true for `()` and for `{}`, which are also empty. It also builds a throwaway list on every call.

Write `if items:` for "is there anything here". The point of the exercise is that the two verbose forms are not more precise, only longer.

</details>

## Real-world reps

- [ ] Write the `apply` function from practice 2 and call it with no argument, with `0`, and with `5`. Then change the condition to `is not None` and call all three again.
- [ ] Search code you know for `or ` used to supply a default. For each hit, decide whether zero or an empty string is a legal input. Every yes is a live bug.
- [ ] Tomorrow: pick a function with an optional parameter and write down, in words, whether it distinguishes "not supplied" from "supplied as empty". If the function cannot, decide whether it should.

## Going further

- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing): the full rule, including how a class opts out
- [Comparisons](https://docs.python.org/3/reference/expressions.html#comparisons): chaining, identity, and what raises
- [Boolean operations](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not): why `and` and `or` return an operand rather than a boolean
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
