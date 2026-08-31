---
title: 8. The Iteration Protocol
description: Why for works on anything, and why some of those things can only be looped over once
type: lesson
---

# Lesson 8. The Iteration Protocol

**Mission link:** A large share of the confusing bugs in data-handling code are one iterator that was already consumed. The protocol is four lines long, and knowing it turns those bugs into predictions.
**Primary source:** [The Python Standard Library, Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types)
**Prerequisites:** [Lesson 3](0003-lists-and-slicing.md), [Lesson 4](0004-dicts-and-sets.md), [Lesson 7](0007-comprehensions.md)

## Warm-up

1. ▢ Lesson 4 said `d.keys()` is a live view rather than a snapshot. What happens if you add a key while looping over it?

<details markdown="1"><summary>Check</summary>

`RuntimeError: dictionary changed size during iteration`. The view sees the change, and iteration refuses to continue over a container whose size moved. Loop over `list(d)` when the body needs to mutate `d`.

</details>

2. ▢ Lesson 7 called `(n * n for n in range(3))` a generator expression rather than a tuple. Guess what the second `sum` prints.

   ```python
   g = (n * n for n in range(3))
   print(sum(g))
   print(sum(g))
   ```

<details markdown="1"><summary>Check</summary>

`5`, then `0`. This lesson is about why the second one is not an error.

</details>

## Know this

`for` is sugar. This is what it does, exactly:

```python
it = iter(items)                 # 1. ask the object for an iterator
while True:
    try:
        item = next(it)          # 2. ask the iterator for a value
    except StopIteration:        # 3. it says it has none left
        break
    ...                          # 4. the loop body
```

That gives two distinct roles, and the difference between them is the whole lesson.

An **iterable** can produce an iterator. It implements `__iter__`.

An **iterator** produces values one at a time and remembers where it stopped. It implements `__next__`, and its `__iter__` returns itself.

| Object | Iterable | Iterator |
|---|---|---|
| `[1, 2, 3]`, `"abc"`, `(1, 2)`, `{1, 2}` | yes | no |
| `range(3)` | yes | no |
| `d.keys()`, `d.values()`, `d.items()` | yes | no |
| `iter([1, 2, 3])` | yes | yes |
| result of `zip`, `map`, `filter`, `enumerate`, `reversed` | yes | yes |
| a generator expression, or a call to a generator function | yes | yes |
| an open file object | yes | yes |

Every iterator is also an iterable, because its `__iter__` hands back itself. That is why `for` accepts either one without caring. The reverse is not true, and that asymmetry produces every bug below.

### An iterator is consumed once, and says nothing about it

```python
pairs = zip([1, 2], "ab")
print(list(pairs))               # [(1, 'a'), (2, 'b')]
print(list(pairs))               # []
```

Nothing raised. The second `list` asked for a value, was told there were none, and built an empty list. That silence is the danger: the code looks like it processed the data twice and it processed it once.

A list survives repeated iteration because each `for` calls `iter` and gets a **fresh** iterator with its own position. `zip` is already the iterator, so there is nothing fresh to get.

The rule that prevents this: **if a value has to be traversed twice, it must be a container, not an iterator.** Materialise it once, deliberately.

```python
pairs = list(zip([1, 2], "ab"))  # now re-iterable
```

### A file is its own iterator

```python
with open(path) as f:
    line_count = sum(1 for _ in f)
    first = next(f, None)        # None: the file is at its end
```

There is no second pass without `f.seek(0)`. A function that takes "the lines" and loops over them twice works when it is handed a list and quietly returns nothing on the second pass when it is handed a file. This is the most common form of the bug in real code, because the two callers look identical at the call site.

### `next` with a default, and the sentinel form of `iter`

`next(it)` raises `StopIteration` when exhausted. `next(it, default)` returns the default instead, which is the readable way to say "the first one, if there is one".

```python
with open(path) as f:
    next(f, None)                # discard the header line
    for line in f:               # continues from line 2
        ...
```

Partially consuming an iterator and then continuing is not a trick, it is the point of holding one. `itertools.islice` does the same job for a range of positions.

`iter` also has a two-argument form that calls something until it returns a sentinel:

```python
for chunk in iter(lambda: stream.read(4096), b""):
    ...
```

### Making your own type iterable

Almost always: return an iterator built from something that already is one.

```python
class Deck:
    def __init__(self, cards):
        self._cards = list(cards)

    def __iter__(self):
        return iter(self._cards)
```

`Deck` is now iterable, re-iterable, and works with `for`, `list`, `sum`, `in`, and comprehensions. Two loops over one deck do not interfere, because each gets its own iterator.

Defining `__next__` **on `Deck` itself** would make the deck its own iterator, and then two loops over one deck would fight over a single shared position. That is what the file object does, and it is a deliberate choice for a stream, not a default to copy.

One legacy path is worth recognising in old code: a class with `__getitem__` taking integers from zero is iterable without `__iter__`, because `iter` falls back to calling `obj[0]`, `obj[1]` and so on until `IndexError`.

### When you genuinely need two passes

Three honest options, in order of preference:

1. **Store it**: `items = list(source)`. Costs memory, and it is usually the right answer.
2. **Recompute it**: call the function that produced the iterator again. Right when the source is cheap or huge.
3. **`itertools.tee`**: buffers whatever one branch has seen and the other has not. Right for two passes that advance roughly together, wrong as a way to avoid deciding.

## Practice

1. ▢ Predict both lines.

   ```python
   nums = map(int, ["1", "2", "3"])
   print(max(nums))
   print(sum(nums))
   ```

<details markdown="1"><summary>Check</summary>

`3`, then `0`.

`max` consumed the map object. `sum` of an exhausted iterator is the empty sum, which is zero. No exception is raised at any point, and a report built this way would show a maximum with a total of zero.

</details>

2. ▢ This function is called twice: once with a list of lines, once with an open file. Describe both outcomes.

   ```python
   def summarise(lines):
       total = sum(len(line) for line in lines)
       longest = max((line for line in lines), key=len)
       return total, longest
   ```

<details markdown="1"><summary>Hint</summary>

Which argument survives being iterated twice, and what does `max` receive on the second pass?

</details>

<details markdown="1"><summary>Check</summary>

With a list it works. With a file it raises `ValueError: max() iterable argument is empty`, because `sum` already consumed the file and `max` has no default.

The fix is to decide inside the function: `lines = list(lines)` at the top, and the signature then honestly accepts any iterable.

</details>

3. ▢ Which of these can be looped over twice with the same result? For each `no`, say what it is instead.

   - a) `sorted(nums)`
   - b) `reversed(nums)`
   - c) `nums.keys()` for a dict `nums`
   - d) `(n for n in nums)`
   - e) `range(len(nums))`

<details markdown="1"><summary>Check</summary>

Twice: **a**, **c**, **e**. Once: **b**, **d**.

- a) `sorted` returns a new list.
- b) `reversed` returns an iterator.
- c) A dict view is an iterable, and a fresh iterator comes from each loop.
- d) A generator expression is an iterator.
- e) `range` is a lazy sequence, not an iterator: it is re-iterable, supports `len` and indexing, and stores only its endpoints.

`range` is the useful case to have straight. Laziness and single-use are different properties, and `range` has the first without the second.

</details>

4. ▢ Write `first_matching(items, predicate)`, returning the first item that satisfies `predicate` or `None`. Do it without a `for` statement, and make it stop at the first match.

<details markdown="1"><summary>Check</summary>

```python
def first_matching(items, predicate):
    return next((item for item in items if predicate(item)), None)
```

The generator expression is lazy, so `next` pulls exactly as many items as it takes to find one. Building a list first, as in `[i for i in items if predicate(i)]`, would evaluate the predicate against everything and then throw the rest away.

</details>

5. ▢ Why does the second loop print nothing, and what are the two ways to fix it?

   ```python
   evens = filter(lambda n: n % 2 == 0, range(10))
   for n in evens:
       print(n)
   for n in evens:
       print("again", n)
   ```

<details markdown="1"><summary>Check</summary>

`filter` returns an iterator, exhausted by the first loop.

Fix one, if the values are needed twice: `evens = list(filter(...))`. Fix two, if the source is cheap: build the filter again before the second loop. Choosing between them is a memory-against-recomputation decision, and it should be made rather than discovered.

</details>

6. ▢ A colleague makes their `Playlist` class its own iterator, so `__next__` lives on `Playlist` and tracks a `self._position`. Name a specific way this breaks.

<details markdown="1"><summary>Check</summary>

Any of these:

- Two loops over one playlist share a position, so a nested loop finishes the outer one.
- `if track in playlist` consumes the playlist, because `in` iterates.
- Looping twice silently yields nothing the second time, exactly like the file case.
- `len(list(playlist))` returns zero after anything else has iterated it.

The fix is one line: delete `__next__` and let `__iter__` return `iter(self._tracks)`.

</details>

## Real-world reps

- [ ] Grep code you know for `zip(`, `map(`, `filter(` and `enumerate(`. For each one, ask whether the result is traversed once. Anything traversed twice is either already a bug or one edit away from being one.
- [ ] Take a function that accepts "a list of things" and loops over the argument twice. Hand it a generator expression and watch what it returns. Then fix it, and decide whether the fix belongs in the function or in its documented signature.
- [ ] Add `__iter__` to a class you own that currently exposes a `.items` list, and remove the callers reaching into that attribute.
- [ ] Tomorrow: read a header line off a file with `next(f, None)` and process the rest with a plain `for`, instead of an index check inside the loop.

## Going further

- [Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types): the protocol stated in full, including the requirement that `__iter__` returns self
- [Glossary: iterable, iterator, sequence](https://docs.python.org/3/glossary.html): the canonical one-line definitions
- [`itertools`](https://docs.python.org/3/library/itertools.html): `islice`, `tee`, `chain` and the rest, all of which take and return iterators
- [The `for` statement](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement): the exact desugaring, including what `break` does to the iterator
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
