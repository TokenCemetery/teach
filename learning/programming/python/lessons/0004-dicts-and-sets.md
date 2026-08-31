---
title: 4. Dicts and Sets
description: Keys must be hashable, lookup has one right idiom per intention, and a view is not a snapshot
type: lesson
---

# Lesson 4. Dicts and Sets

**Mission link:** The dictionary is where most Python programs keep their state, and choosing the wrong lookup idiom is how a program acquires silent defaults it was never meant to have.
**Primary source:** [The Python Tutorial, Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
**Prerequisites:** [Lesson 2](0002-mutability-and-copying.md), [Lesson 3](0003-lists-and-slicing.md)

## Warm-up

1. ▢ `a = [1]; b = a; a += [2]; print(b)`. What prints, and what would `a = a + [2]` have printed instead?

<details markdown="1"><summary>Check</summary>

`[1, 2]`, because `+=` extended the shared list in place. With `a = a + [2]` it would print `[1]`, because that builds a new list and rebinds only `a`.

</details>

2. ▢ Why can a tuple be a dict key while a list cannot?

<details markdown="1"><summary>Check</summary>

Because hashability follows mutability: a key's hash must not change while it is in the dictionary. A tuple of hashable items is hashable, and a list is never hashable.

</details>

## Know this

A `dict` maps keys to values. A `set` holds unique members. Both are built on hashing, which is why both impose the same requirement on what you put in them.

### Keys are hashable, and order is insertion order

```python
counts = {"a": 1, "b": 2}
counts["c"] = 3
print(list(counts))         # ['a', 'b', 'c']
```

Since Python 3.7 the language guarantees that a `dict` preserves insertion order. Sets do not, and never have: a set's iteration order is an artefact of hashing, so any code that depends on it is broken even though it will appear to work.

Assigning to an existing key replaces the value and keeps the key's original position.

### Four ways to read a key, and they mean different things

```python
config = {"retries": 3}

config["timeout"]                  # KeyError, and that is often correct
config.get("timeout")              # None
config.get("timeout", 10)          # 10, and config is unchanged
config.setdefault("timeout", 10)   # 10, and config now HAS the key
```

Pick by intention, not by habit:

| You mean | Write |
|---|---|
| this key must exist, a missing one is a bug | `config["k"]` |
| a missing key is normal, and I have a default | `config.get("k", default)` |
| a missing key is normal, and I want it stored | `config.setdefault("k", default)` |
| I need to know which happened | `if "k" in config:` |

The trap is `get` with a default that hides a real error. If a missing key means a misconfigured program, `KeyError` is a feature: it names the key and stops immediately, which is far better than a `None` that surfaces three functions later.

Never use `config.keys()` for a membership test. `"k" in config` already tests keys, and it is both clearer and faster.

### A mutable default needs care

Counting and grouping is the most common dictionary task, and the naive version reads badly:

```python
groups = {}
for word in words:
    if word[0] not in groups:
        groups[word[0]] = []
    groups[word[0]].append(word)
```

Two better spellings:

```python
from collections import defaultdict

groups = defaultdict(list)
for word in words:
    groups[word[0]].append(word)     # missing keys create a list on access
```

```python
groups = {}
for word in words:
    groups.setdefault(word[0], []).append(word)
```

`defaultdict` is clearer when the whole dictionary works that way. Be aware of its one edge: merely reading a missing key creates it, so a `defaultdict` grows when you only meant to look.

### Views are live, not snapshots

`keys()`, `values()` and `items()` return **views** onto the dictionary:

```python
config = {"a": 1}
keys = config.keys()
config["b"] = 2
print(list(keys))       # ['a', 'b'], the view updated
```

A view is a window, not a copy. It also means you cannot add or remove keys while iterating the dictionary, and Python raises `RuntimeError: dictionary changed size during iteration` rather than producing nonsense. To delete while iterating, iterate a copy of what you need:

```python
for key in list(config):        # list() takes the snapshot
    if config[key] is None:
        del config[key]
```

### Sets, briefly

```python
a = {1, 2, 3}
b = {3, 4}
a | b       # {1, 2, 3, 4}   union
a & b       # {3}            intersection
a - b       # {1, 2}         difference
a ^ b       # {1, 2, 4}      symmetric difference
```

Membership in a set is fast and does not depend on size, which is the reason to build one: turning a list into a set before a loop of `in` tests is the single most common honest optimisation in Python. `{}` is an empty dict, and `set()` is an empty set.

## Practice

1. ▢ Predict each of the four lines, and say whether `config` changed.

   ```python
   config = {"retries": 3}
   print(config.get("timeout"))
   print(config.get("timeout", 10))
   print(config.setdefault("timeout", 10))
   print(config)
   ```

<details markdown="1"><summary>Check</summary>

`None`, `10`, `10`, then `{'retries': 3, 'timeout': 10}`.

Both `get` calls left the dictionary alone. `setdefault` returned the same value and also stored it, which is the difference the name does not advertise.

</details>

2. ▢ This loop is meant to drop empty values. Predict what happens.

   ```python
   data = {"a": 1, "b": None, "c": None}
   for key in data:
       if data[key] is None:
           del data[key]
   ```

<details markdown="1"><summary>Hint</summary>

The loop is iterating the dictionary itself, not a copy of it. Ask what the iterator is doing while the dictionary is changing underneath it.

</details>

<details markdown="1"><summary>Check</summary>

It raises `RuntimeError: dictionary changed size during iteration`, on the iteration after the first deletion.

The fix is to iterate a snapshot: `for key in list(data):`. Python detects the mutation instead of silently skipping entries, which is a deliberate choice in favour of a loud failure.

</details>

3. ▢ Which lookup would you write for each intention? Match the four.

   - Reading a required setting from a parsed config file
   - Reading an optional setting with a sensible fallback
   - Building up a dictionary of lists while grouping records
   - Deciding whether to log "created" or "updated"

<details markdown="1"><summary>Check</summary>

- Required setting: `config["key"]`. A `KeyError` naming the key is the best possible outcome of a broken config.
- Optional with fallback: `config.get("key", default)`. No mutation, no exception.
- Grouping: `defaultdict(list)`, or `setdefault("k", []).append(...)` if the dictionary is not exclusively for grouping.
- Which happened: `if "key" in config:`, because that is the only one of the four that reports the distinction rather than smoothing it over.

</details>

4. ▢ Both of these count words. One has a bug that only appears with certain input. Which, and what input?

   ```python
   # A
   counts = defaultdict(int)
   for w in words:
       counts[w] += 1

   # B
   counts = {}
   for w in words:
       counts[w] = counts[w] + 1
   ```

<details markdown="1"><summary>Check</summary>

B raises `KeyError` on the first occurrence of every word, so it fails on any non-empty input. A is correct: reading `counts[w]` on a `defaultdict(int)` creates a `0`, and `+= 1` stores `1`.

The honest fix for B without `defaultdict` is `counts[w] = counts.get(w, 0) + 1`, and the standard-library answer for this whole task is `collections.Counter`.

</details>

5. ▢ A function takes a list of user IDs and, for each one, checks membership against a list of 50,000 banned IDs. Name the one-line change that matters, and say what makes it correct rather than merely faster.

<details markdown="1"><summary>Check</summary>

Build a set once, before the loop: `banned = set(banned_list)`.

Membership in a list scans it, so the work grows with both inputs. Membership in a set hashes the item and looks in one place. It is correct rather than merely faster because it also states the intention: the collection is being used as a membership test, and a set is the type that means that.

The one thing to check before converting is that the IDs are hashable, which they are if they are strings or integers.

</details>

## Real-world reps

- [ ] Take a counting or grouping loop you have written and rewrite it three ways: with `if key not in`, with `setdefault`, and with `defaultdict`. Decide which you would defend in review, and why.
- [ ] Trigger the `RuntimeError` deliberately, then fix it with `list()`. Getting the error once makes it recognisable forever.
- [ ] Tomorrow: find one `.get(` in code you know where a `KeyError` would have been the better outcome. They are common, and each one is a bug that has been converted into a mystery.

## Going further

- [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries): the tutorial's treatment, including `items()` in loops
- [`collections`](https://docs.python.org/3/library/collections.html): `defaultdict`, `Counter` and the rest, which cover most of what people hand-roll
- [Mapping types](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict): every method, and the view objects in detail
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
