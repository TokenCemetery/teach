---
title: 1. Names Are Bindings, Not Boxes
description: Assignment binds a name to an object and never copies it, so two names can mean one thing
type: lesson
---

# Lesson 1. Names Are Bindings, Not Boxes

**Mission link:** Every aliasing bug in Python starts with reading assignment as copying. Getting this right in the first lesson removes a whole class of bug from every lesson after it.
**Primary source:** [The Python Language Reference, Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
**Prerequisites:** none, this is the first lesson.

## Know this

In Python, **assignment binds a name to an object.** It does not copy the object, and it does not put a value into a box called `x`.

Every object has three things: an identity, a type, and a value ([data model](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)). The identity never changes for the life of the object. The type never changes. Whether the value can change is a property of the object, and that is the next lesson.

A name is separate from all of that. It lives in a namespace and refers to an object:

```python
a = [1, 2, 3]
b = a           # a second name for the same list, not a second list
b.append(4)
print(a)        # [1, 2, 3, 4]
```

Nothing was copied on line 2. There is one list, and two names for it. That is called **aliasing**, and it is not a special case: it is what assignment always does.

### Rebinding is not mutating

Two operations look similar in code and have nothing in common:

```python
a = [1, 2]
b = a

a.append(3)     # mutation: changes the object both names refer to
print(b)        # [1, 2, 3]

a = a + [4]     # rebinding: builds a new list, points a at it
print(b)        # [1, 2, 3], b never moved
```

Mutation reaches through the name to the object. Rebinding changes only which object the name refers to, and every other name is untouched.

The test to apply when reading code: **is the name on the left of an `=`?** If yes, that name is being rebound and nothing else can observe it. If no, and a method is being called, the object is being changed and every name for it observes the change.

### Identity, and the operator that tests it

`is` compares identity, meaning "the same object". `==` compares value, meaning "equal as far as the type is concerned".

```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True, equal values
print(a is b)   # False, two distinct lists
```

`id()` returns the identity as a number, which is useful while learning and rarely in real code.

CPython sometimes reuses objects for small integers and short strings, so `a = 256; b = 256; a is b` may be `True`. That is an implementation detail, not a language guarantee, and code that depends on it is broken. Use `is` for `None` and for genuine identity questions, `==` for everything else. Lesson 5 comes back to this.

### `del` removes a name

```python
a = [1, 2]
b = a
del a           # the name a is gone
print(b)        # [1, 2], the list is very much alive
```

`del` unbinds a name. The object survives as long as something still refers to it, which is why the list here is fine. Nothing in Python deletes objects directly.

## Practice

1. ▢ Predict both outputs.

   ```python
   x = ["a"]
   y = x
   y.append("b")
   print(x)
   y = ["c"]
   print(x)
   ```

<details markdown="1"><summary>Check</summary>

`['a', 'b']`, then `['a', 'b']`.

The `append` mutated the one list both names referred to, so `x` sees it. The last assignment rebound `y` to a brand new list and left `x` alone.

</details>

2. ▢ Which of these four lines can change what another name sees? Answer for each.

   ```python
   items.append(1)
   items = items + [1]
   items += [1]
   items = [1]
   ```

<details markdown="1"><summary>Hint</summary>

Three of them have `items` on the left of an `=`. That is not the whole story for one of them, and that one is worth being unsure about for now.

</details>

<details markdown="1"><summary>Check</summary>

- `items.append(1)`: yes. A method call on the object, so every name for it observes the change.
- `items = items + [1]`: no. `+` builds a new list, and the assignment rebinds only this name.
- `items += [1]`: yes, and this is the surprise. For a list, `+=` mutates in place and then rebinds the same object to the same name. Lesson 3 takes this apart properly.
- `items = [1]`: no. A plain rebinding.

If you got the third one wrong, you are in the majority. It is the single most common reason people believe Python's rules are inconsistent.

</details>

3. ▢ Both comparisons below print something. Predict them, and say which comparison you should be writing in real code.

   ```python
   a = "hello world"
   b = "hello world"
   print(a == b)
   print(a is b)
   ```

<details markdown="1"><summary>Check</summary>

`True`, then either `True` or `False` depending on the interpreter, the version, and how the strings were produced.

That is the point: the second comparison asks a question you almost never mean. Write `==` when you are asking whether two things are equal, and reserve `is` for `None` and for deliberate identity checks.

</details>

4. ▢ How many list objects exist after these three lines, and how many names refer to each?

   ```python
   a = [0]
   b = a
   c = [0]
   ```

<details markdown="1"><summary>Check</summary>

Two list objects. The first has two names, `a` and `b`. The second has one name, `c`.

`c` compares equal to the others with `==` and is a different object, so mutating `c` is invisible to `a` and `b`, and mutating `a` is visible through `b`.

</details>

5. ▢ A colleague says "Python passes small values by value and big values by reference, like other languages". Give the accurate version in one sentence.

<details markdown="1"><summary>Check</summary>

Python passes references to objects, always, with no exception for size or type: what varies is whether the object you received can be mutated at all.

An `int` behaves as if copied because you cannot mutate an `int`, not because Python treated it differently. Lesson 2 makes this precise, and lesson 6 applies it to function arguments, where the belief does real damage.

</details>

## Real-world reps

- [ ] Open an interactive interpreter. Bind two names to one list, mutate through one, and print the other. Then rebind one and print again. Watch `id()` for both names at each step, since it is the only direct evidence of what happened.
- [ ] Take a function in code you know that receives a list or a dict and modifies it. Decide whether the caller can see the change, then check by reading, not by running.
- [ ] Tomorrow: explain aliasing out loud to someone, or write it down in three sentences, without using the words "pointer" or "reference variable". If it will not go into words, the model is not there yet.

## Going further

- [Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding): the precise rules, including what counts as a binding operation
- [Objects, values and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types): identity, type and value in the language's own words
- [Glossary](../GLOSSARY.md): `Name` is pinned there, because carrying the word "variable" across from another language is exactly the failure this lesson prevents
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
