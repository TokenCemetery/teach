---
title: 7. Comprehensions
description: One expression that builds a container, with its own scope and a limit worth respecting
type: lesson
---

# Lesson 7. Comprehensions

**Mission link:** Comprehensions are the most idiomatic construct in the language and the easiest to overuse. Knowing where the line is separates Python that reads well from Python that shows off.
**Primary source:** [The Python Tutorial, List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
**Prerequisites:** [Lesson 3](0003-lists-and-slicing.md), [Lesson 4](0004-dicts-and-sets.md), [Lesson 6](0006-functions-and-arguments.md)

## Warm-up

1. ▢ Why does `[[0] * 3] * 2` produce rows that change together, and what fixes it?

<details markdown="1"><summary>Check</summary>

`* 2` repeats one reference to a single inner list. A comprehension fixes it, because it evaluates `[0] * 3` once per iteration.

</details>

2. ▢ `funcs = [lambda: i for i in range(3)]`. What do the three calls return, and why?

<details markdown="1"><summary>Check</summary>

All three return `2`. The lambdas close over the name `i`, looked up when they are called, and the loop has finished by then.

</details>

## Know this

A comprehension builds a container from an iterable in one expression:

```python
squares  = [n * n for n in range(5)]            # list
unique   = {n % 3 for n in range(10)}           # set
by_name  = {u.name: u for u in users}           # dict
lazy     = (n * n for n in range(5))            # generator, not a tuple
```

The last one is the odd member of the family. Parentheses do not build a tuple: they build a **generator expression**, which computes items on demand and can only be consumed once. Use `tuple(n * n for n in range(5))` when a tuple is what you want.

The shape is always the same:

```text
[expression for item in iterable if condition]
```

The `if` filters, and it is optional. A conditional expression may also appear in the *expression* position, which is a different thing:

```python
[n for n in nums if n > 0]              # filters: shorter output
[n if n > 0 else 0 for n in nums]       # transforms: same length, clamped
```

Confusing these two is the most common comprehension mistake. Filtering changes how many items come out. A conditional expression changes what each item is.

### Nesting reads outer to inner

```python
pairs = [(x, y) for x in "ab" for y in (1, 2)]
# [('a', 1), ('a', 2), ('b', 1), ('b', 2)]
```

The clauses run in the order written, exactly like nested `for` statements, and the innermost varies fastest. That surprises people because the *expression* is at the front, and the loops read left to right after it.

Flattening uses the same order:

```python
flat = [item for row in matrix for item in row]
```

### A comprehension has its own scope

```python
i = "untouched"
result = [i for i in range(3)]
print(i)            # untouched
```

The loop variable is local to the comprehension and cannot leak into the surrounding function. A plain `for` statement does leak, which is worth knowing when you convert one into the other.

The consequence to remember from lesson 6: this scope is why a `lambda` inside a comprehension still shows late binding. The lambda outlives the comprehension's scope, and it captured the name.

### Where the line is

A comprehension is the right tool when it reads as one thought. Three signs it has stopped:

- It needs a comment to explain the ordering of its clauses.
- It contains a second `if`, or a conditional expression, plus a filter.
- It wraps onto three lines and the reader has to hunt for the `for`.

The honest alternative is a `for` statement, which can hold a comment, a `try`, and an early `continue`. There is no idiom points system, and a loop that a reader understands the first time beats a comprehension they have to decode.

Two related tools worth knowing before reaching for either: `sum`, `any`, `all`, `min` and `max` take a generator expression directly, so `sum(x.total for x in orders)` needs no intermediate list; and `sorted(items, key=...)` replaces most comprehensions that were only trying to reorder.

## Practice

1. ▢ Predict both outputs, and describe the difference in one sentence each.

   ```python
   nums = [-2, 0, 3]
   print([n for n in nums if n > 0])
   print([n if n > 0 else 0 for n in nums])
   ```

<details markdown="1"><summary>Check</summary>

`[3]`, then `[0, 0, 3]`.

The first filters, so the output is shorter than the input. The second transforms each item, so the output has the same length with the negatives clamped to zero.

</details>

2. ▢ What does this produce?

   ```python
   result = [(x, y) for x in (1, 2) for y in "ab"]
   ```

<details markdown="1"><summary>Hint</summary>

Rewrite it as two nested `for` statements in the order the clauses appear. The rightmost clause is the inner loop.

</details>

<details markdown="1"><summary>Check</summary>

`[(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]`.

The clauses nest left to right, so `x` is the outer loop and `y` varies fastest.

</details>

3. ▢ One of these is not a tuple. Which, and what is it?

   - a) `tuple(n for n in "ab")`
   - b) `(n for n in "ab")`
   - c) `tuple([n for n in "ab"])`
   - d) `(*(n for n in "ab"),)`

<details markdown="1"><summary>Check</summary>

**b)** `(n for n in "ab")` is a generator expression, not a tuple.

There is no tuple comprehension syntax. The other three all produce `('a', 'b')`, and option a is the one to write: it consumes the generator directly without building an intermediate list.

</details>

4. ▢ This is real code from a review. Rewrite it so a reader understands it on the first pass.

   ```python
   result = [transform(v) for k, v in data.items() if k not in skip and v is not None]
   ```

<details markdown="1"><summary>Check</summary>

Any of these is defensible:

```python
result = []
for key, value in data.items():
    if key in skip or value is None:
        continue
    result.append(transform(value))
```

Or split the filtering from the transforming:

```python
wanted = {k: v for k, v in data.items() if k not in skip and v is not None}
result = [transform(v) for v in wanted.values()]
```

The original is not wrong, and it is at the length where a reader has to parse rather than read. The loop version also has somewhere to put a comment about why `skip` exists, which the one-liner does not.

</details>

5. ▢ Replace each of these with a shorter, clearer expression.

   ```python
   total = sum([order.amount for order in orders])
   found = len([u for u in users if u.active]) > 0
   ```

<details markdown="1"><summary>Check</summary>

```python
total = sum(order.amount for order in orders)
found = any(u.active for u in users)
```

The first drops the brackets, so `sum` consumes a generator expression instead of a list that exists only to be added up and discarded.

The second is the bigger win. `any` stops at the first active user, while the original builds a list of every active user, counts it, and compares the count to zero. On a large collection that is the difference between one iteration and all of them, and the intention is now stated in the function's name.

</details>

## Real-world reps

- [ ] Take three `for` loops from code you know that only build a list, and convert each to a comprehension. Then convert one back because it read better as a loop, and be able to say why.
- [ ] Write the nested comprehension for flattening a matrix from memory, then check the clause order by running it. The order is the part people get wrong.
- [ ] Tomorrow: find a `len([... for ...]) > 0` or a `sum([... for ...])` in real code and replace it with `any` or a bare generator expression.

## Going further

- [List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions): including the nested form and the equivalent loops
- [Generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions): the lazy sibling, and why the parenthesised form is not a tuple
- [PEP 8, on comprehensions and line length](https://peps.python.org/pep-0008/): the style rules that decide when to break one up
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
