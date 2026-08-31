---
title: 34. The GIL, Precisely
description: What it serialises, what it does not protect, and what changes without it
type: lesson
---

# Lesson 34. The GIL, Precisely

**Mission link:** The mission asks you to state what the GIL does and does not prevent. Almost every wrong concurrency decision in Python traces to one of two errors: believing threads are useless, or believing the GIL makes code thread-safe.
**Primary source:** [PEP 703, Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/)
**Prerequisites:** [Lesson 13](0013-modules-and-packages.md), [Lesson 22](0022-attribute-lookup.md)

## Warm-up

1. ▢ Lesson 1: what does `counter += 1` do to the name `counter`?

<details markdown="1"><summary>Check</summary>

Reads the object it is bound to, computes a new one, and rebinds the name. Three steps, which matters here.

</details>

2. ▢ True or false: because of the GIL, two threads cannot corrupt shared data.

<details markdown="1"><summary>Check</summary>

False. It is the most expensive misunderstanding in this stage, and the measurements below show why.

</details>

## Know this

The global interpreter lock is a mutex inside CPython that allows **one thread at a time to execute Python bytecode**. It exists to protect the interpreter's own internal state, above all reference counts, from concurrent modification.

Two consequences, and they point in opposite directions.

### CPU-bound work does not scale with threads

Measured, on one machine, four calls to a pure-Python arithmetic loop:

```text
CPU sequential x4                  1.01s
CPU 4 threads                      1.02s
CPU 4 processes                    0.38s
CPU 4 subinterpreters              0.30s
```

Threads bought nothing, because only one of them ran bytecode at any moment. Processes and subinterpreters did, because each has its own interpreter state and its own lock.

### Input and output does scale, completely

```text
IO sequential x8 (0.2s each)       1.66s
IO 8 threads                       0.21s
```

Eight-fold, from the same threads. The lock is **released** around blocking operations: reading a socket, waiting on a file, `time.sleep`, and inside C extensions that opt to release it, which includes much of NumPy and most database drivers.

That is the whole practical rule. **The GIL serialises the interpreter, not the waiting.** A thread waiting for a response is not holding it.

### What it does not do

It does not make your code thread-safe, and the demonstration matters more than the assertion. Eight threads running this on one key:

```python
def get_or_create(key):
    if key not in cache:              # check
        time.sleep(0.001)             # any real yield: I/O, a lock, a network call
        cache[key] = object()         # act
        created.append(key)
    return cache[key]
```

```text
check-then-act with a real yield: objects created for one key: 8
with a lock: 1
```

Eight objects for one key. The dictionary was never corrupted, so the GIL did its job; the **invariant across two statements** was destroyed, which was never its job. Every check-then-act, read-modify-write, and multi-field update has this shape.

The same applies to an object with two fields that must agree:

```python
def add(self, n):
    self.total += n
    time.sleep(0.0005)           # stands in for anything that yields
    self.entries += 1
```

A reader thread sampling both fields saw them disagree 873 times in one short run. The final totals were correct; every intermediate observation was not.

### The honest complication

This claim is often taught with `counter += 1` across threads losing updates. On CPython 3.14, that did **not** reproduce: four threads incrementing a global 300,000 times each produced exactly the expected total, on every attempt, including with the thread switch interval lowered from the default 5 milliseconds to 1 microsecond.

That is not reassurance, it is the danger stated precisely. The race is real, since the operation is a load, an add and a store. Whether it is ever **observed** depends on where the interpreter chooses to switch threads, which is an implementation detail that varies by version, by build, and by what else the code does. Code that is correct only because a switch never happened to land in the wrong place is code that breaks on an upgrade, on another machine, or on a free-threaded build.

The rule that follows: **do not reason about atomicity from bytecode.** Guard the invariant with a lock, or do not share the state.

### Free-threaded Python

CPython can now be built without the lock. The state, as of 3.14:

```python
import sysconfig, sys
sysconfig.get_config_var("Py_GIL_DISABLED")     # 1 on a free-threaded build
sys._is_gil_enabled()                            # False when it is off
```

On a standard build both report the lock present. On a free-threaded build, threads execute bytecode in parallel, CPU-bound threading works, and every race above becomes far easier to hit. Single-threaded performance is somewhat lower, memory use is higher, and C extensions must declare support.

What this means for a lesson written today: the free-threaded build is a real, supported option and not yet the default, so **write code that is correct either way.** That is the same code: locks around invariants, or no shared mutable state.

### What to do with this

| Workload | Threads help |
|---|---|
| network requests, database queries | yes, fully |
| reading and writing files | yes |
| pure-Python computation | no, on a standard build |
| NumPy, Pillow, compression, hashing | yes, where the extension releases the lock |
| waiting on a subprocess | yes |

The next three lessons are the tools: threads for waiting, processes and subinterpreters for computing, and `asyncio` for waiting on thousands of things at once.

## Practice

1. ▢ For each, say whether four threads will be roughly four times faster.

   - a) Downloading 200 URLs
   - b) Computing SHA-256 of 200 files with `hashlib`
   - c) Parsing 200 JSON documents already in memory with `json.loads`
   - d) Running 200 SQL queries against a database
   - e) Resizing 200 images with Pillow

<details markdown="1"><summary>Check</summary>

- a) Yes. Nearly all the time is waiting on sockets.
- b) Yes, mostly. `hashlib` releases the lock for larger inputs, and the file reading waits anyway.
- c) No. `json.loads` is C code that does not release the lock, and the work is CPU-bound.
- d) Yes. The driver waits on a socket, and the database does the work.
- e) Yes, largely. Pillow releases the lock around its own processing.

The pattern: ask what the thread is doing while it is slow. Waiting scales; interpreting does not.

</details>

2. ▢ This runs on a standard build and produces the right answer every time. Is it correct?

   ```python
   total = 0
   def add_all(items):
       global total
       for item in items:
           total += item
   ```

<details markdown="1"><summary>Hint</summary>

Separate "produces the right answer today" from "is guaranteed to".

</details>

<details markdown="1"><summary>Check</summary>

No. It is a load, an add and a store on shared state with no lock, and nothing in the language guarantees those three happen together.

It passes today because the interpreter happens not to switch threads between the load and the store. That is timing, not a guarantee, and it changes with a version upgrade, a free-threaded build, a different machine, or the addition of any call inside the loop that yields.

Correct versions: a lock around the update, or each thread returning its own subtotal and one thread summing them. The second is better, because it removes the sharing rather than guarding it.

</details>

3. ▢ Fix the cache, and explain what the lock protects.

   ```python
   cache: dict[str, Connection] = {}

   def get(key):
       if key not in cache:
           cache[key] = connect(key)       # connect() does I/O
       return cache[key]
   ```

<details markdown="1"><summary>Check</summary>

```python
lock = threading.Lock()

def get(key):
    with lock:
        if key not in cache:
            cache[key] = connect(key)
        return cache[key]
```

The lock protects the **invariant** "at most one connection per key", which spans the check and the assignment. The dict itself was never at risk.

Note the cost: `connect` does I/O while holding the lock, so callers for other keys wait. The usual refinement is per-key locking, or accepting an occasional duplicate and closing the loser. Both are decisions; the unguarded version is not.

Simplest of all, when the key set is small and the value is cheap to build: `functools.cache` from lesson 14 on the factory function, which has the same race under the same conditions and is at least documented.

</details>

4. ▢ Why does lowering `sys.setswitchinterval` not reliably expose a race?

<details markdown="1"><summary>Check</summary>

Because the switch interval only sets how long a thread may hold the lock before being asked to yield; it does not force a switch at any particular bytecode. The interpreter also has fast paths where no check happens, and a tight loop over integers may complete without ever offering to yield.

So a small interval makes some races more likely and cannot make them certain. Which is why a race is diagnosed by reading the code for unguarded invariants, not by trying to reproduce it.

</details>

5. ▢ A colleague proposes moving to a free-threaded build to speed up a request handler that spends 90 per cent of its time waiting on a database. What do you say?

<details markdown="1"><summary>Check</summary>

That the lock is not the bottleneck. Waiting releases it, so those threads already run concurrently: the measured input-output case above scaled eight-fold on a standard build.

What a free-threaded build would change: slightly lower single-threaded performance, higher memory use, a dependency check across every C extension in use, and every latent race in the codebase becoming reachable. All cost, no benefit, for this workload.

What to say next: measure where the 90 per cent goes. Connection pool exhaustion, a missing index, and one query per row are the usual causes, and none of them are about the GIL.

</details>

6. ▢ Two threads append to the same list, and it works. Two threads update the same dictionary counter, and it does not. Explain the difference in one paragraph.

<details markdown="1"><summary>Check</summary>

`list.append` is a single call into C that completes without releasing the lock, so it either happened or did not, and no other thread can observe a half-appended list. That makes it usable as a thread-safe collector, and 200,000 appends from four threads produced exactly 200,000 items.

`counts[key] += 1` is a read of the current value, an addition, and a write back, expressed as separate bytecodes with an interpreter that may switch threads between them, and the same shape as the check-then-act above. The safe versions are a lock, a `Counter` merged per thread, or a `queue.Queue` feeding one consumer.

The general lesson is not the list-versus-dict distinction, which is an implementation detail. It is that "one call into C" and "several statements in Python" are different, and only the second needs guarding.

</details>

## Real-world reps

- [ ] Run the measurement yourself: a pure-Python loop four times, sequentially and in four threads, then in four processes. The numbers make the argument better than the explanation does.
- [ ] Take the slowest job you have and answer one question: while it is slow, is it waiting or computing? That answer chooses the tool for the next three lessons.
- [ ] Grep code you own for check-then-act on shared state: `if key not in`, `if not os.path.exists`, `if x is None:` followed by an assignment to a shared object. Each one is this lesson.
- [ ] Print `sys._is_gil_enabled()` and `sysconfig.get_config_var("Py_GIL_DISABLED")` on every interpreter you deploy on, so you know which build you are reasoning about.
- [ ] Tomorrow: find one shared mutable global in a threaded program and try to remove the sharing rather than adding a lock.

## Going further

- [PEP 703](https://peps.python.org/pep-0703/): the clearest statement of what the lock protects and what removing it costs
- [Python support for free threading](https://docs.python.org/3/howto/free-threading-python.html): how to identify such a build, its thread-safety guarantees, and its known limitations
- [`threading`](https://docs.python.org/3/library/threading.html): the note on which operations are atomic, and why not to rely on it
- [`sys.setswitchinterval`](https://docs.python.org/3/library/sys.html#sys.setswitchinterval): what the interval actually controls
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
