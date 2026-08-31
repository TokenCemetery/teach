---
title: 9. Generators
description: A function that pauses, keeps its local state, and produces values only when asked
type: lesson
---

# Lesson 9. Generators

**Mission link:** Generators are how Python handles data that does not fit in memory, and how a pipeline gets written without an intermediate list at every step. They are also the construct people avoid longest, because a function that returns nothing when called looks broken.
**Primary source:** [The Python Language Reference, Yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions)
**Prerequisites:** [Lesson 8](0008-the-iteration-protocol.md)

## Warm-up

1. ▢ From lesson 8: what makes a list re-iterable and a `zip` object not?

<details markdown="1"><summary>Check</summary>

Each `for` over a list calls `iter` and gets a fresh iterator with its own position. A `zip` object is already the iterator, so there is nothing fresh to hand out.

</details>

2. ▢ How many times does `print` run here, and when?

   ```python
   def numbers():
       print("starting")
       yield 1
       yield 2

   n = numbers()
   ```

<details markdown="1"><summary>Check</summary>

Never, so far. Calling `numbers()` created a generator and executed none of its body. This lesson is about why.

</details>

## Know this

A `yield` anywhere in a function body changes what calling that function does. It no longer runs the body: it builds a **generator** and returns it immediately.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

c = countdown(3)                 # nothing has run
print(next(c))                   # 3   body runs up to the first yield
print(next(c))                   # 2   resumes after that yield
```

Each `next` runs the body until it reaches a `yield`, hands that value out, and **freezes the frame**: local variables, the position in the loop, the state of any open `with`. The next `next` thaws it and continues on the line after the `yield`. When the body finishes, the generator raises `StopIteration` and is done for good.

That is the whole mechanism. Everything below follows from it.

### Laziness is the reason to use one

```python
def read_records(path):
    with open(path) as f:
        for line in f:
            yield parse(line)
```

This processes a file of any size in constant memory, and the caller can stop early:

```python
for record in read_records(path):
    if record.id == wanted:
        break
```

The `break` leaves the generator suspended forever, at which point Python closes it: the frame is discarded and the `with` block's exit runs, so the file is closed. Compare the eager version, which reads and parses every line before the caller sees the first one.

The trade is fixed and worth stating plainly: a generator gives up random access, `len`, and second passes, and gets constant memory and early exit. Choose from that, not from style.

### A generator is an iterator, with everything that implies

It is single-use. Every warning from lesson 8 applies, and applies harder, because a generator looks like a function call and function calls usually give a fresh answer.

```python
records = read_records(path)
count = sum(1 for _ in records)
first = next(records, None)       # None
```

The generator **function** is reusable. The generator it returns is not. When a caller needs two passes, call the function twice or materialise once.

### `return` in a generator ends it

```python
def take_until_blank(lines):
    for line in lines:
        if not line.strip():
            return                # ends iteration; not a value
        yield line
```

A bare `return` stops the generator. `return value` also stops it, and attaches the value to the `StopIteration` rather than yielding it, which only `yield from` normally reads. Treat a returned value as an advanced feature and the bare form as the everyday one.

One rule worth knowing before it bites: **a `StopIteration` raised inside a generator body becomes a `RuntimeError`**, since Python 3.7. That means a bare `next(it)` inside a generator does not quietly end it, which is the behaviour the change was made to remove. Use `next(it, None)` and check.

### `yield from` delegates

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item
```

`yield from sub` yields every value from `sub` as if it were written inline. The explicit `for item in sub: yield item` does the same thing for plain iteration; `yield from` additionally forwards `send`, `throw` and `close` to the inner generator, and it reads better in recursion.

### Pipelines

Generators compose without intermediate lists, because each stage pulls one value from the stage before it:

```python
lines    = (line.rstrip("\n") for line in open(path))
records  = (parse(line) for line in lines if line)
billable = (r for r in records if r.amount > 0)

total = sum(r.amount for r in billable)
```

Nothing is read until `sum` starts pulling, and only one record exists at a time. `itertools` is the library of ready-made stages: `islice` for a window, `chain` for concatenation, `takewhile` and `dropwhile` for prefixes, `groupby` for runs of equal keys (which requires the input to be sorted by that key already, and surprises people who expect SQL's `GROUP BY`).

### Cleanup is not guaranteed the way `with` is

A `try/finally` or a `with` inside a generator runs its cleanup when the generator is exhausted, explicitly closed, or garbage collected. It does **not** run at the moment the caller stops caring:

```python
def records(path):
    with open(path) as f:         # closed when the generator is closed
        for line in f:
            yield line
```

In CPython, an abandoned generator is usually collected promptly and the file closes right then. That is an implementation detail, not a language promise. When the resource matters, close it deliberately with `contextlib.closing`, or open it in the caller and pass the file in. Lesson 10 makes the `with` side of this precise.

### `send` exists, and is not where to spend attention

A generator can receive values (`value = yield`), which made generator-based coroutines possible before `async` existed. Modern code uses `async def` for that, and it arrives in stage 6. Recognise `send` in old code; do not design with it.

## Practice

1. ▢ Predict the exact output, including the order.

   ```python
   def gen():
       print("a")
       yield 1
       print("b")
       yield 2
       print("c")

   g = gen()
   print("created")
   for x in g:
       print(x)
   ```

<details markdown="1"><summary>Check</summary>

```text
created
a
1
b
2
c
```

`created` comes first because the call ran no code. Then each `next` runs up to the following `yield`, and the final `next` runs `print("c")`, falls off the end, and raises `StopIteration`, which `for` catches.

</details>

2. ▢ Rewrite this so it uses constant memory and lets the caller stop early.

   ```python
   def parse_all(path):
       result = []
       with open(path) as f:
           for line in f:
               result.append(parse(line))
       return result
   ```

<details markdown="1"><summary>Hint</summary>

The `return` of a list becomes a `yield` of one item, and the accumulator disappears.

</details>

<details markdown="1"><summary>Check</summary>

```python
def parse_all(path):
    with open(path) as f:
        for line in f:
            yield parse(line)
```

Note what changed for callers: they can no longer index the result, call `len` on it, or loop over it twice. If any caller does, either they change or the function keeps its list. This is a signature change, not a refactor.

</details>

3. ▢ Which of these is a generator function, and what do the others return?

   - a) `def f(): return (n for n in range(3))`
   - b) `def f(): yield from range(3)`
   - c) `def f(): return [n for n in range(3)]`
   - d) `def f(): print(1); yield`

<details markdown="1"><summary>Check</summary>

Generator functions: **b** and **d**, because their bodies contain `yield`.

- a) An ordinary function returning a generator object. Calling it runs the body, which builds the generator expression. The result is close to b in practice and different in mechanism.
- c) An ordinary function returning a list.
- d) A generator function that yields a single `None`. `yield` with no expression is legal.

</details>

4. ▢ Find the bug.

   ```python
   def first_words(lines):
       for line in lines:
           yield line.split()[0]

   words = first_words(open("notes.txt"))
   print(sum(1 for _ in words), "words")
   print(next(words, "none left"))
   ```

<details markdown="1"><summary>Check</summary>

Two bugs, and only one of them is the exhaustion.

The `sum` consumes the generator, so the `next` prints `none left`. That is the lesson-8 failure and it is silent.

The other is `line.split()[0]` on a blank line, which raises `IndexError` from inside the generator. An exception in a generator body propagates out of the `next` that triggered it, meaning it surfaces at the `sum` line, far from the code that produced the bad input. Guard it: `if not line.strip(): continue`.

</details>

5. ▢ Rewrite the eager version as a pipeline of generator expressions, and say what changes about when the file is read.

   ```python
   lines = open(path).readlines()
   stripped = [line.strip() for line in lines]
   nonblank = [line for line in stripped if line]
   count = len(nonblank)
   ```

<details markdown="1"><summary>Check</summary>

```python
with open(path) as f:
    stripped = (line.strip() for line in f)
    nonblank = (line for line in stripped if line)
    count = sum(1 for _ in nonblank)
```

The eager version builds three lists and holds the whole file plus two derived copies. The pipeline reads one line at a time and never holds more than one.

The `with` is not decoration. The eager version leaked a file object; the pipeline must be consumed inside the block, because `sum` is where the reading happens.

</details>

6. ▢ A colleague says a generator is "just a lazy list". Give two concrete things a list does that a generator cannot.

<details markdown="1"><summary>Check</summary>

Any two of: indexing and slicing, `len`, iterating more than once, `in` without consuming it, sorting in place, appending, being passed to two functions in sequence, printing usefully.

The point is not that generators are worse. It is that `list(gen)` is a decision with a memory cost, and `gen` is a decision with a capability cost, and neither is a default.

</details>

## Real-world reps

- [ ] Take one function you own that builds a list and returns it, convert it to a generator, and run the test suite. Every failure is a caller relying on something a list does. Decide case by case, then keep the version that produced the fewest changes.
- [ ] Write a three-stage generator pipeline over a file you actually have: read, parse, filter. Then insert a `print` in the parse stage and watch the interleaving prove that nothing runs ahead.
- [ ] Read [`itertools`](https://docs.python.org/3/library/itertools.html) end to end once. It is short, and the point is recognition rather than recall.
- [ ] Tomorrow: find code that reads an entire file to count or find one thing, and replace it with `sum(1 for _ in f)` or `next(...)`.

## Going further

- [Yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions): including `yield from`, `send`, `throw` and `close`
- [Generators, in the tutorial](https://docs.python.org/3/tutorial/classes.html#generators): the shortest correct introduction
- [PEP 479, Change StopIteration handling inside generators](https://peps.python.org/pep-0479/): why a `StopIteration` in a generator body is now a `RuntimeError`
- [PEP 380, Syntax for delegating to a subgenerator](https://peps.python.org/pep-0380/): what `yield from` forwards beyond the values
- [`itertools`](https://docs.python.org/3/library/itertools.html): the standard pipeline stages
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
