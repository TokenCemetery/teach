---
title: 39. Measuring Before Optimising
description: Where the time actually goes, and why the micro-optimisations you were taught are gone
type: lesson
---

# Lesson 39. Measuring Before Optimising

**Mission link:** The mission asks you to find the slow part with a profiler and prove the fix with a measurement. Both halves matter: intuition about Python performance is unreliable, and it has become more unreliable as the interpreter has improved.
**Primary source:** [The Python Standard Library, The Python Profilers](https://docs.python.org/3/library/profile.html)
**Prerequisites:** [Lesson 3](0003-lists-and-slicing.md), [Lesson 4](0004-dicts-and-sets.md), [Lesson 34](0034-the-gil-precisely.md)

## Warm-up

1. ▢ Lesson 4 said a `set` gives constant-time membership. How much does that matter, in numbers?

<details markdown="1"><summary>Check</summary>

Measured below at 89.8 microseconds against 20 nanoseconds for 10,000 items, which is over four thousand fold. Hold that number: it dwarfs everything else in this lesson.

</details>

2. ▢ You have heard that binding `math.sqrt` to a local name inside a hot loop makes it faster. Does it, on a current interpreter?

<details markdown="1"><summary>Check</summary>

No. Measured below at 36.8 against 37.8 microseconds, which is within noise. This lesson is partly about folklore that expired.

</details>

## Know this

### Rule one: measure, and measure the right thing

```bash
python -m timeit -s "xs = list(range(10000))" "9999 in xs"
python -m timeit -s "xs = set(range(10000))" "9999 in xs"
```

```text
5000 loops, best of 5: 89.8 usec per loop
10000000 loops, best of 5: 20 nsec per loop
```

`timeit` answers "how long does this expression take", runs it enough times to be meaningful, and reports the **best** rather than the mean, because the best is the least polluted by whatever else the machine was doing.

For a program rather than an expression, profile it:

```bash
python -m cProfile -s cumulative myscript.py
```

```text
         100126 function calls (100122 primitive calls) in 0.030 seconds

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.009    0.009    0.030    0.030 prof_demo.py:5(slow_count)
    20000    0.005    0.000    0.019    0.000 re/__init__.py:270(findall)
    20000    0.008    0.000    0.008    0.000 {method 'findall' of 're.Pattern' objects}
    20000    0.005    0.000    0.007    0.000 re/__init__.py:330(_compile)
    20018    0.002    0.000    0.002    0.000 {built-in method builtins.isinstance}
```

Two columns matter and they answer different questions:

- **`tottime`** is time in that function excluding calls it made. High `tottime` means the code there is the problem.
- **`cumtime`** includes everything it called. High `cumtime` with low `tottime` means the problem is further down.

Read that profile: `re.findall` accounts for two thirds of the total, and `_compile` is being called 20,000 times because the pattern is recompiled on every call. That is the finding, and it is not visible by reading the source.

| Tool | Use |
|---|---|
| `timeit` | one expression, precise |
| `cProfile` | which functions, in a run you can start |
| `pstats` | sorting and filtering a saved profile |
| `py-spy`, `pyinstrument` | a running process, or a wall-clock view including waiting |
| `tracemalloc` | where memory is allocated |
| `memray` | memory in depth |

`cProfile` measures function calls, so it understates code that is slow inside one long function and adds overhead to code that makes many small calls. A sampling profiler such as `py-spy` distorts less and can attach to a process already running in production, which is often the only option.

### Rule two: the algorithm dominates

The membership measurement above is the whole argument. Before considering anything else:

| Look for | Replace with |
|---|---|
| `x in some_list` inside a loop | a `set` or `dict` |
| a nested loop over two collections | a dict keyed by the join field |
| repeated sorting inside a loop | sort once outside |
| a query per row | one query with a join, or one batched query |
| recompiling a regex per call | compile once at module level |
| repeated `list.pop(0)` | `collections.deque` |
| string concatenation in a loop | `"".join(parts)` |
| re-reading a file per lookup | read once into a dict |

Every row is a change in complexity class, and each is worth more than every micro-optimisation combined.

Measured on the word-counting example from the profile above, after replacing the recompiled regex and the manual counting with `str.split` and a `Counter`:

```text
slow_count   14.4 msec per loop
fast_count    6.08 msec per loop
```

Two and a half fold, from a change that also made the function shorter.

### Rule three: most micro-optimisations no longer exist

CPython's specialising interpreter changed which folklore is true. Measured on 3.14:

```text
for i in range(1000): math.sqrt(i)        36.8 usec      attribute lookup per call
for i in range(1000): sqrt(i)            37.8 usec      pre-imported local
out = []; for ...: out.append(i*2)       28.6 usec
out = [i*2 for i in range(1000)]         25.4 usec
```

Binding the function to a local: **no gain**. The comprehension against the append loop: 12 per cent, not the two-fold that gets repeated. Neither is worth restructuring code for, and the comprehension is worth writing anyway because it reads better, which is lesson 7's argument, not a performance one.

The general point is stronger than these two numbers: **do not trade readability for a performance claim you have not measured on your interpreter.** Advice from 2015 about attribute lookups, local variables and loop unrolling was measured against an interpreter that no longer exists.

What still costs, measurably:

| Real cost | Why |
|---|---|
| creating many objects | allocation and reference counting |
| deep call chains in a hot loop | frame setup per call |
| pure-Python loops over large data | the interpreter, which is the thing to leave |
| copying large containers | lesson 2, and it is often accidental |
| serialisation across a process boundary | lesson 36 |

### Rule four: leave the interpreter, do not fight it

For numeric or columnar work over large data, the answer is not faster Python. It is NumPy, Polars, or the database, all of which run the loop in C and release the interpreter lock while doing it.

For the remaining hot spot, in order: check whether the standard library has it in C already; check whether a library exists; then consider Cython, a Rust extension, or `ctypes` around something that exists. Each of those adds a build step, a platform matrix, and a debugging story, so it needs a measurement to justify it, and the measurement should be of the whole program rather than the function.

### Rule five: prove the fix

```bash
python -m timeit -s "from mod import old, DATA" "old(DATA)"
python -m timeit -s "from mod import new, DATA" "new(DATA)"
```

An optimisation without a before-and-after number is a guess that also made the code harder to read. Write both numbers in the commit message, because the next person will otherwise revert the ugly version for good reasons.

Then check the whole program. A function made ten times faster that accounted for 3 per cent of runtime bought 2.7 per cent, which is usually not worth what it cost in clarity. That arithmetic is the discipline this entire lesson exists to enforce.

## Practice

1. ▢ A profile shows `cumtime` of 8 seconds in `handle_request` and `tottime` of 0.02. Where is the time?

<details markdown="1"><summary>Check</summary>

Not in `handle_request`. Its own code takes 20 milliseconds; the other 7.98 seconds are in what it called.

Read down the profile for the function with high `tottime`, which is where the work happens. If the highest `tottime` is a socket read or a driver call, the program is waiting, which sends you to lesson 38 rather than to an optimisation.

</details>

2. ▢ Fix the actual problem.

   ```python
   def annotate(orders, flagged_ids):        # flagged_ids is a list of 50,000
       for order in orders:                  # orders is 200,000
           order.flagged = order.id in flagged_ids
   ```

<details markdown="1"><summary>Hint</summary>

Count the comparisons, then look at the type of `flagged_ids`.

</details>

<details markdown="1"><summary>Check</summary>

`in` on a list is a linear scan, so this is 200,000 times up to 50,000 comparisons: ten billion in the worst case.

```python
def annotate(orders, flagged_ids):
    flagged = set(flagged_ids)               # once
    for order in orders:
        order.flagged = order.id in flagged
```

One line, and the complexity goes from quadratic to linear. By the measurement above, each membership test drops from about 90 microseconds to 20 nanoseconds at 10,000 items, and the gap widens with size.

Note what is not the fix: threads, processes, a faster loop body, or rewriting it in C. Any of those applied to the original would still be quadratic.

</details>

3. ▢ Which of these is worth doing for performance on a current interpreter?

   - a) Hoisting `self.config.timeout` out of a loop that reads it 1,000 times
   - b) Replacing a `for` loop that appends with a list comprehension
   - c) Compiling a regex once at module level instead of per call
   - d) Replacing `dict.get(k)` with a `try/except KeyError`
   - e) Replacing 200,000 `list.pop(0)` calls with a `deque`

<details markdown="1"><summary>Check</summary>

- a) Marginal. Attribute lookup is specialised now, and the measurement above found no gain from the equivalent trick. Do it if it reads better.
- b) Twelve per cent, measured. Do it for readability, not for speed.
- c) Yes. The profile above showed `_compile` called 20,000 times, and the fix was a real fraction of the runtime.
- d) No, and it can be slower. Choose between them by intention, from lesson 10, not by speed.
- e) Yes, decisively. `pop(0)` shifts every remaining element, so this is quadratic and `deque.popleft` is constant.

The pattern: **c** and **e** change how much work happens; **a**, **b** and **d** change how the same work is spelled.

</details>

4. ▢ A colleague optimises a function from 40 milliseconds to 4. The request takes 1.2 seconds. What do you say?

<details markdown="1"><summary>Check</summary>

That they bought 3 per cent, and the question is what it cost. If the code is now unreadable, it is a bad trade; if it also got simpler, keep it.

Then redirect: 1.2 seconds with 40 milliseconds in that function means 1.16 seconds is somewhere else. Profile the request, find the largest `tottime`, and check first whether it is waiting rather than computing, because those have completely different fixes.

The arithmetic worth stating explicitly: the ceiling on any local optimisation is the fraction of total time it occupies. A function that is 3 per cent of runtime cannot give more than 3 per cent no matter how fast it becomes.

</details>

5. ▢ A nightly job processes 50 million rows in pure Python and takes six hours. Give the order of things to try.

<details markdown="1"><summary>Check</summary>

1. **Profile it**, on a sample, to find whether the time is parsing, computing, or writing.
2. **Do less work.** Filter earlier, avoid loading columns nobody uses, and check for a per-row query or a quadratic lookup.
3. **Push it into the database**, if the data is already there. A `GROUP BY` beats 50 million Python iterations by orders of magnitude and moves no data.
4. **Move the loop into a library**: Polars or NumPy over columns rather than Python over rows.
5. **Split across processes**, per lesson 36, with each worker reading its own byte range.
6. **Rewrite the hot kernel** in Cython or Rust, last, with a measurement.

Steps 3 and 4 are usually where the two orders of magnitude are, and step 5 gives at most the number of cores. Doing 5 before 3 is the common mistake, because it feels like engineering.

</details>

6. ▢ Why report `timeit`'s best rather than its average?

<details markdown="1"><summary>Check</summary>

Because the distribution is one-sided. Noise from other processes, the scheduler, cache eviction and frequency scaling can only make a run slower, never faster than the code actually is. The minimum is therefore the best estimate of the code's cost, and the mean measures the machine as much as the code.

The caveat worth knowing: this makes `timeit` good at comparing two implementations and bad at predicting production latency, where the tail is what users experience. For that, measure the real system and look at the high percentiles.

</details>

## Real-world reps

- [ ] Profile something you own with `cProfile -s cumulative` and read the top ten lines. The finding is usually a call count, not a slow function.
- [ ] Run the two `timeit` commands from this lesson yourself. The membership number is worth having in your own hands.
- [ ] Grep for `in ` against a list or tuple inside a loop, and for a regex compiled per call.
- [ ] Take one micro-optimisation in your codebase, revert it, and measure. Keep the revert if the difference is noise.
- [ ] Attach `py-spy` to a running process and compare its picture with `cProfile`'s. The wall-clock view shows waiting, which `cProfile` hides.
- [ ] Tomorrow: put a before-and-after number in the next performance commit message you write.

## Going further

- [The Python Profilers](https://docs.python.org/3/library/profile.html): `cProfile`, `pstats`, and what the columns mean
- [`timeit`](https://docs.python.org/3/library/timeit.html): the command-line form, and why it reports the minimum
- [`tracemalloc`](https://docs.python.org/3/library/tracemalloc.html): allocation sites and snapshots
- [What's New in Python](https://docs.python.org/3/whatsnew/index.html): the interpreter changes that expire performance folklore
- [py-spy](https://github.com/benfred/py-spy): sampling profiler for a process already running
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
