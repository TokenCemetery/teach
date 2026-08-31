---
title: 2. Mutability and Copying
description: Mutability belongs to the object, so an immutable container can still hold something that changes
type: lesson
---

# Lesson 2. Mutability and Copying

**Mission link:** Deciding what to copy, and how deeply, is a design decision made dozens of times in any real program. Made by instinct, it produces either shared state nobody expected or copies nobody needed.
**Primary source:** [The Python Standard Library, `copy`](https://docs.python.org/3/library/copy.html)
**Prerequisites:** [Lesson 1](0001-names-are-bindings.md)

## Warm-up

1. ▢ `a = [1]; b = a; b.append(2)`. What does `a` print, and why?

<details markdown="1"><summary>Check</summary>

`[1, 2]`. Assignment bound a second name to the same list, and `append` mutated that one list.

</details>

2. ▢ When is `is` the right operator to reach for?

<details markdown="1"><summary>Check</summary>

For `None`, and for deliberate identity checks. Everywhere else `==` is the question you actually mean.

</details>

## Know this

**Mutability is a property of the object, not of the name.** Lesson 1 established that a name is only a binding; this lesson is about what you can do to the thing on the other end.

| Type | Mutable | Notes |
|---|---|---|
| `int`, `float`, `bool`, `complex` | no | arithmetic builds new objects |
| `str`, `bytes` | no | every "modification" is a new object |
| `tuple`, `frozenset` | no | the container is fixed, its contents may not be |
| `list`, `dict`, `set`, `bytearray` | yes | methods change them in place |
| most of your own classes | yes | unless you deliberately prevent it |

The rows to read twice are `str` and `tuple`.

### Immutable does not mean deeply immutable

A tuple fixes which objects it holds. It says nothing about those objects:

```python
row = ([1, 2], "fixed")
row[0].append(3)        # fine, the list is mutable
print(row)              # ([1, 2, 3], 'fixed')
row[0] = []             # TypeError: 'tuple' object does not support item assignment
```

You cannot change which objects the tuple holds, and you can change those objects freely. The tuple's immutability is one level deep, and that is the whole story of most surprises here.

This is why hashability follows mutability. A `dict` key must be hashable, and a tuple is hashable only if everything inside it is:

```python
{("a", 1): "ok"}        # fine
{("a", [1]): "boom"}    # TypeError: unhashable type: 'list'
```

### Strings do not change

```python
s = "hello"
s.upper()               # returns a new string
print(s)                # hello, unchanged
s = s.upper()           # rebinding is how you "modify" a string
```

Every string method returns a new string. Reading a string method call and expecting the original to change is the same mistake as expecting `a + [1]` to change `a`.

### Three depths of copy

For a flat list of immutable items, all three of these are equivalent in effect:

```python
import copy

original = [1, 2, 3]
alias      = original                 # not a copy at all
shallow    = original[:]              # or list(original), or copy.copy(original)
deep       = copy.deepcopy(original)
```

For anything nested they are three different things:

```python
original = [[1], [2]]
alias   = original
shallow = original[:]
deep    = copy.deepcopy(original)

original[0].append("x")
print(alias)     # [[1, 'x'], [2]]   same object
print(shallow)   # [[1, 'x'], [2]]   new outer list, same inner lists
print(deep)      # [[1], [2]]        new all the way down
```

A **shallow copy** builds a new outer container holding the same objects. A **deep copy** recursively copies what it finds. Shallow is what every convenient syntax gives you: `[:]`, `list()`, `dict()`, `set()`, `copy.copy`.

Reach for `deepcopy` when you genuinely need an independent tree, and know that it is slow, that it has to handle cycles, and that it will happily copy things you did not intend to duplicate. Most of the time the better answer is not to share the mutable thing in the first place.

## Practice

1. ▢ Predict the output.

   ```python
   config = {"tags": ["a"], "name": "svc"}
   backup = dict(config)
   config["tags"].append("b")
   config["name"] = "other"
   print(backup)
   ```

<details markdown="1"><summary>Hint</summary>

`dict(config)` gives you a new dictionary. Ask separately, for each of the two keys, whether the value it holds was copied.

</details>

<details markdown="1"><summary>Check</summary>

`{'tags': ['a', 'b'], 'name': 'svc'}`.

`dict(config)` is a shallow copy: a new mapping holding the same value objects. Rebinding `config["name"]` changed only which object `config` maps that key to, so `backup` still has `"svc"`. The `append` mutated the single list both dictionaries point at, so `backup` sees it.

This exact shape, a "backup" that was never independent, is one of the most common bugs in configuration handling.

</details>

2. ▢ Is this tuple hashable? Answer for each of the two.

   ```python
   a = (1, "x", (2, 3))
   b = (1, "x", {2: 3})
   ```

<details markdown="1"><summary>Check</summary>

`a` is hashable. `b` is not, so it cannot be a `dict` key or a `set` member, and trying raises `TypeError: unhashable type: 'dict'`.

A tuple's hash is computed from the hashes of its contents, so one unhashable item anywhere inside disqualifies the whole thing.

</details>

3. ▢ Which line raises, and what does it tell you about the object?

   ```python
   point = (1, [2])
   point[1].append(3)
   point[1] = [4]
   ```

<details markdown="1"><summary>Check</summary>

The third line raises `TypeError`. The second is legal.

The tuple controls its own slots and nothing beyond them. It refuses the rebinding of slot 1, and has no say in what happens to the list that slot 1 refers to.

</details>

4. ▢ Which one produces an object that is fully independent of `data`?

   ```python
   data = {"a": [1]}
   ```

   - a) `data.copy()`
   - b) `dict(data)`
   - c) `{**data}`
   - d) `copy.deepcopy(data)`

<details markdown="1"><summary>Check</summary>

**d)** `copy.deepcopy(data)`.

The first three are three spellings of the same shallow copy: a new dictionary holding the same list. Only the deep copy also copies the list.

</details>

5. ▢ A function receives a list and needs a version it can sort without affecting the caller. Give the line you would write, and say why you would not reach for `deepcopy`.

<details markdown="1"><summary>Check</summary>

`items = sorted(items)`, or `items = list(items)` followed by `items.sort()`.

`sorted` returns a new list and never touches the argument, which is exactly the guarantee needed. A shallow copy is enough because sorting rearranges which objects the new list refers to and does not modify any of them, so copying them would be wasted work.

`deepcopy` would be both slower and misleading, since it implies the elements themselves need protecting.

</details>

## Real-world reps

- [ ] Build the nested `original`, `alias`, `shallow`, `deep` example yourself and mutate at both levels: the outer list and an inner one. Predict each of the six results before printing.
- [ ] Find a place in code you know where a dict or list is copied, decide whether the copy needed to be deep, and check whether it is. One of the two is usually wrong.
- [ ] Tomorrow: write down which of the types you use most often are mutable, from memory, then check against the table above. The gaps are what to watch for in review.

## Going further

- [`copy`](https://docs.python.org/3/library/copy.html): the module, including why `deepcopy` needs to handle recursive structures
- [Mutable sequence types](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types): the operations that mutate, listed in one table
- [Mutability and copying](../reference/mutability-and-copying.md): the reference sheet for this, built for lookup
- [Glossary](../GLOSSARY.md): `Mutability` is pinned there
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
