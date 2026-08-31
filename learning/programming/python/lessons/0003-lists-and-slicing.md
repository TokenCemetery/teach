---
title: 3. Lists and Slicing
description: A slice copies, in-place methods return None, and += mutates what + would rebuild
type: lesson
---

# Lesson 3. Lists and Slicing

**Mission link:** The list is the default container in Python, and three of its behaviours produce silent bugs rather than errors. Those three are the whole lesson.
**Primary source:** [The Python Tutorial, More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
**Prerequisites:** [Lesson 2](0002-mutability-and-copying.md)

## Warm-up

1. ▢ `row = (1, [2]); row[1].append(3)`. Legal or not, and why?

<details markdown="1"><summary>Check</summary>

Legal. The tuple fixes which objects it holds, and the list it holds is still mutable.

</details>

2. ▢ What kind of copy is `list(original)`, and when is that not enough?

<details markdown="1"><summary>Check</summary>

A shallow copy: a new list holding the same objects. Not enough when the elements themselves are mutable and have to be independent.

</details>

## Know this

A list is a mutable, ordered sequence. Three of its behaviours are worth more than all its methods put together.

### A slice builds a new list

```python
items = [0, 1, 2, 3, 4]
part  = items[1:3]      # [1, 2], a new list
part.append(99)
print(items)            # [0, 1, 2, 3, 4], untouched
```

`items[start:stop:step]`, with `stop` excluded. Every index is optional, so `items[:]` is the idiomatic shallow copy of a whole list. Slicing never fails on out-of-range bounds: `items[2:99]` gives you what is there, while `items[99]` raises `IndexError`. Negative indices count from the end.

The one to remember: **a slice of a list is a copy, and indexing a list is not.** `items[1]` hands you the object itself.

### In-place methods return `None`

```python
items = [3, 1, 2]
items.sort()                    # returns None, sorts items
print(items)                    # [1, 2, 3]

result = [3, 1, 2].sort()
print(result)                   # None
```

This is a deliberate convention across the language: a method that mutates the object returns `None` so that nothing looks like it produced a value. `append`, `extend`, `insert`, `remove`, `reverse`, `sort` and `clear` all return `None`.

Every one has a non-mutating counterpart when you need a new object instead:

| In place, returns `None` | Builds a new object |
|---|---|
| `items.sort()` | `sorted(items)` |
| `items.reverse()` | `reversed(items)`, or `items[::-1]` |
| `items.append(x)` | `items + [x]` |
| `items.extend(other)` | `items + other` |

The bug this convention prevents is `items = items.sort()`, which discards the list and leaves you with `None`. The bug it causes is writing that line anyway and being confused by the error two functions later.

### `+=` mutates a list, `+` does not

```python
a = [1]
b = a
a += [2]                # in place: calls list.__iadd__, extends the list
print(b)                # [1, 2], b sees it

a = [1]
b = a
a = a + [2]             # new list, then rebinding
print(b)                # [1], b did not move
```

For a list, `+=` is `extend`, followed by rebinding the name to the same object it already referred to. Every other name for that list observes the change.

For an immutable object there is no in-place option, so `+=` can only build a new object and rebind:

```python
s = "a"
s += "b"                # new string, s rebound; nothing else could observe it
```

So `+=` means "mutate if you can, otherwise rebuild". Whether other names see the result depends entirely on the type on the left, which is why lesson 1 called this the most common reason people think Python is inconsistent.

### Multiplication shares, it does not duplicate

```python
grid = [[0] * 3] * 2        # two names for ONE inner list
grid[0][0] = 9
print(grid)                 # [[9, 0, 0], [9, 0, 0]]
```

`* 2` repeats the reference twice. The fix is a comprehension, which evaluates its expression once per item:

```python
grid = [[0] * 3 for _ in range(2)]
```

`[0] * 3` is fine, because `0` is immutable and sharing it is unobservable.

## Practice

1. ▢ Predict the output.

   ```python
   names = ["a", "b", "c"]
   first_two = names[:2]
   first_two[0] = "z"
   print(names, first_two)
   ```

<details markdown="1"><summary>Check</summary>

`['a', 'b', 'c'] ['z', 'b']`.

The slice built a new list. Assigning into `first_two` rebinds one of its slots, and `names` has no idea.

</details>

2. ▢ Predict both prints. They are not the same.

   ```python
   a = [1]
   b = a
   a += [2]
   print(b)
   a = a + [3]
   print(b)
   ```

<details markdown="1"><summary>Hint</summary>

One of these two operations gives the list a chance to change itself. The other has to build something new before the assignment happens.

</details>

<details markdown="1"><summary>Check</summary>

`[1, 2]`, then `[1, 2]`.

`+=` extended the shared list in place, so `b` saw the `2`. Then `a + [3]` built a new list and rebound `a` to it, leaving `b` on the old object, which still ends at `2`.

</details>

3. ▢ What does this print, and what did the author intend to write?

   ```python
   scores = [5, 2, 9]
   scores = scores.sort()
   print(scores)
   ```

<details markdown="1"><summary>Check</summary>

`None`.

`sort` mutates in place and returns `None` by convention, and the assignment threw the list away. The author wanted either `scores.sort()` with no assignment, or `scores = sorted(scores)`.

</details>

4. ▢ Which line makes a grid where the rows are independent?

   - a) `grid = [[0] * 3] * 2`
   - b) `grid = [[0] for _ in "ab"] * 2`
   - c) `grid = [[0] * 3 for _ in "ab"]`
   - d) `grid = list([[0] * 3] * 2)`

<details markdown="1"><summary>Check</summary>

**c)** `grid = [[0] * 3 for _ in "ab"]`.

The comprehension evaluates `[0] * 3` once per iteration, so each row is a separate list. Option a repeats one reference. Option b builds two independent rows and then repeats both references, giving four entries and two distinct lists. Option d is a shallow copy of the broken structure from option a, so the rows are still shared.

</details>

5. ▢ You are reviewing a function that takes `items: list` and starts with `items = items[:]`. What is the author protecting against, and what are they not protecting against?

<details markdown="1"><summary>Check</summary>

They are protecting the caller from any mutation of the list itself: appends, removals, sorting, slot assignment. After that line, the function's name refers to a different list, so the caller's list cannot be changed.

They are not protecting the caller from mutation of the elements. If the list holds dictionaries and the function modifies one, the caller sees it, because the shallow copy holds the same dictionaries.

</details>

## Real-world reps

- [ ] Run the `+=` and `+` pair from the lesson, and check `id(a)` before and after each. The identity is the evidence, and it makes the difference impossible to forget.
- [ ] Build `[[0] * 3] * 2`, mutate one cell, and look at the result. Then fix it with a comprehension.
- [ ] Tomorrow: search code you know for `= .*\.sort\(\)` or `= .*\.append\(`. Any hit is a bug or about to be one.

## Going further

- [More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists): every method, with the return value stated
- [Sorting Techniques](https://docs.python.org/3/howto/sorting.html): `key`, stability, and why `cmp` is gone
- [Mutability and copying](../reference/mutability-and-copying.md): the copy and aliasing rules in one table
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
