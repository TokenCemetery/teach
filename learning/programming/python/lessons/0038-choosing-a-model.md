---
title: 38. Choosing a Model
description: One question decides it, and the measurement that settles the rest
type: lesson
---

# Lesson 38. Choosing a Model

**Mission link:** The mission asks you to choose between threads, processes and `asyncio` from the shape of the workload. There is one question that decides most cases, and a second that decides the rest, and neither is answered by preference.
**Primary source:** [The Python Standard Library, concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
**Prerequisites:** [Lesson 34](0034-the-gil-precisely.md), [Lesson 35](0035-threads-and-shared-state.md), [Lesson 36](0036-processes-and-interpreters.md), [Lesson 37](0037-asyncio.md)

## Warm-up

1. ▢ Name the two numbers from lesson 34 that decide almost everything.

<details markdown="1"><summary>Check</summary>

Four threads on CPU-bound work: no speedup. Eight threads on waiting: eight-fold. Waiting scales with threads, interpreting does not.

</details>

2. ▢ What does adding concurrency to a program that is already fast enough buy?

<details markdown="1"><summary>Check</summary>

New failure modes. That is the honest answer and the first thing this lesson checks.

</details>

## Know this

### The decision, in order

**Question zero: is it too slow, measured?** If not, stop. Concurrency adds races, partial failures, harder debugging, and a shutdown path. That cost is paid whether or not the speedup was needed.

**Question one: while it is slow, is it waiting or computing?** Everything follows from the answer.

| Waiting on | Computing in |
|---|---|
| sockets, HTTP, database queries | pure Python loops |
| files, disks | `json.loads`, regex, string building |
| subprocesses | pickling, serialisation |
| locks, queues | C extensions that hold the lock |

The two are distinguished by measurement, not intuition: a profile that shows most time inside a `recv` or a driver call is waiting; one that shows it spread across your own functions is computing. Lesson 39 is that measurement.

**Question two, if waiting: how many at once?**

| Concurrent waits | Reach for |
|---|---|
| up to a few hundred | `ThreadPoolExecutor` |
| thousands, or long-lived connections | `asyncio` |
| a handful, and simple code matters more | sequential, honestly |

**Question three, if computing: can the work be split into independent pieces?**

| | Reach for |
|---|---|
| independent chunks, plain data | `ProcessPoolExecutor` |
| independent chunks, and the dependencies allow it | `InterpreterPoolExecutor` |
| the loop can move into a library | NumPy, Polars, the database |
| it cannot be split | make the algorithm cheaper; concurrency will not help |

### The table, in full

| Model | Parallel CPU | Scales waits to | Shares memory | Failure isolation | Costs |
|---|---|---|---|---|---|
| sequential | no | one | trivially | total | none |
| threads | no, on a standard build | hundreds | yes, and that is the risk | none | locks, races |
| subinterpreters | yes | hundreds | no | partial | new; extension support |
| processes | yes | hundreds | no | full | start-up, serialisation |
| `asyncio` | no | tens of thousands | yes, at `await` points | none | colours the codebase |

Two rows deserve emphasis. Threads and `asyncio` both share memory, so both need the discipline from lesson 34; `asyncio` makes the switch points visible, which is a genuine review advantage, not a safety guarantee. And nothing in the table makes CPU-bound Python faster except processes, subinterpreters, and doing less work.

### Combining them

Real systems mix models, and the sane combinations are few:

- **`asyncio` plus a thread pool**, via `asyncio.to_thread`, for the one synchronous library you cannot replace.
- **`asyncio` plus a process pool**, via `run_in_executor`, for the CPU-bound step inside an otherwise waiting service.
- **Threads plus a process pool**, where threads fan out requests and processes do the heavy transform.
- **Processes each running their own event loop**, which is what a production async server does: one process per core, each handling thousands of connections.

The combination to avoid is threads and `asyncio` sharing mutable state, where the review has to reason about both thread switches and `await` points at once.

### What concurrency does not fix

Four cases where the answer is not a concurrency model:

| Symptom | Actual cause |
|---|---|
| a query per row | the query pattern; batch or join it |
| latency dominated by one remote call | that service, or a cache |
| adding workers makes it slower | a downstream limit: pool size, rate limit, disk |
| memory grows with worker count | each worker holds its own copy of the data |

The third is the one that catches teams repeatedly, and lesson 35's practice question covers it: bound the pool by the scarcest downstream resource, not by the number of items or the number of cores.

### Getting out cleanly

Whatever the model, a service needs a shutdown path, and it is part of the choice:

| Model | Shutdown |
|---|---|
| threads | an `Event`, not `daemon=True`, then `join` with a timeout |
| pools | the context manager, or `shutdown(wait=True, cancel_futures=...)` |
| processes | the same, plus a signal handler so children are not orphaned |
| `asyncio` | cancel the tasks, `await` them, and never swallow `CancelledError` |

A program that cannot stop cleanly loses in-flight work, and the loss shows up as data that is written but not acknowledged.

## Practice

1. ▢ Choose a model for each, and say why.

   - a) A report joining data from six HTTP APIs
   - b) Resampling 40,000 audio files
   - c) A chat server with 30,000 open connections
   - d) A nightly job parsing 200 GB of logs, CPU-bound in the parse
   - e) A command-line tool that makes three API calls

<details markdown="1"><summary>Check</summary>

- a) Threads, a pool of six. Waiting, and the concurrency is tiny.
- b) Processes. CPU-bound, trivially splittable, and workers can read their own files so the boundary carries only paths.
- c) `asyncio`. Thirty thousand mostly-idle connections is exactly the workload one thread per connection cannot serve.
- d) Processes, with each worker reading its own byte range. Also worth checking first whether the parse can move into a library or a different format.
- e) Sequential. Three calls do not justify anything, unless they are slow and independent, in which case a thread pool of three is still simpler than making the tool async.

</details>

2. ▢ A service handles 200 requests per second, each spending 90 per cent of its time on one database query. The team proposes `asyncio`. What do you check first?

<details markdown="1"><summary>Hint</summary>

What limits the number of queries in flight, regardless of the concurrency model?

</details>

<details markdown="1"><summary>Check</summary>

The connection pool. If the database allows 20 connections, then 20 queries run at a time whatever the calling code does, and adding concurrency above that just moves the queue from the database into your process.

Then: whether the query itself is slow, since a missing index makes every model equally slow; and whether it is one query or one per row.

Only after those does the model matter, and at this scale a thread pool sized to the connection pool is both simpler and equivalent. `asyncio` earns its place when the number of concurrent waits exceeds what threads can hold, which is tens of thousands, not 200.

</details>

3. ▢ A CPU-bound job takes 60 seconds. Rank these by expected improvement.

   - a) Eight threads
   - b) Eight processes
   - c) Rewriting the inner loop with NumPy
   - d) Replacing an O(n squared) scan with a dict lookup
   - e) Converting the code to `asyncio`

<details markdown="1"><summary>Check</summary>

**d**, then **c**, then **b**, then **a** and **e** tied at nothing.

- d) Algorithmic. Lesson 39 measures a membership test at 89.8 microseconds against 20 nanoseconds, which is over four thousand fold. Nothing else on this list competes.
- c) Moves the loop into C, which typically gives one to two orders of magnitude, and releases the lock as a bonus.
- b) Up to eight-fold, minus start-up and transfer.
- a) Nothing, on a standard build.
- e) Nothing, and it makes the code harder.

The order matters because the effort is roughly the reverse: the largest win is usually the smallest change.

</details>

4. ▢ Adding workers made throughput worse. Give the diagnostic sequence.

<details markdown="1"><summary>Check</summary>

1. Find what the workers wait on. A downstream pool, a rate limit, a disk, or a lock in your own code.
2. Check whether any part of the work is CPU-bound. If so, threads are now interleaving without parallelism and adding overhead.
3. Check per-worker memory. If each worker loads the same dataset, eight workers is eight copies, and the machine may be swapping.
4. Check the task size against the boundary cost, for a process pool: many small tasks pay pickling more than they gain.
5. Only then look at the concurrency library.

The general shape: throughput is set by the scarcest resource, and concurrency above that point adds queueing latency without adding work done.

</details>

5. ▢ An async service needs to hash uploaded files, which is CPU-bound and takes 400 milliseconds. What do you do, and what is wrong with the two obvious answers?

<details markdown="1"><summary>Check</summary>

```python
digest = await loop.run_in_executor(process_pool, hash_file, path)
```

A process pool, awaited, so the event loop stays free.

The two obvious answers and their defects. Calling `hash_file` directly stalls the single event-loop thread for 400 milliseconds, adding that to every concurrent request's latency, per lesson 37. And `asyncio.to_thread` does not help for pure-Python CPU work, per lesson 34, though it does help here if `hashlib` releases the lock for large inputs, which it does, making the thread version defensible for this specific case and wrong as a general habit.

The real first question is whether the hashing belongs in the request at all. A queue and a worker process removes it from the latency path entirely, which is the answer that scales.

</details>

6. ▢ A colleague says "we should use `asyncio` everywhere; it is the modern way". Give the case for and against.

<details markdown="1"><summary>Check</summary>

For: it is the only model that scales to tens of thousands of concurrent waits; `TaskGroup` and `timeout` give structured concurrency and cancellation that threads have no equivalent of; suspension points are visible in the source, which makes review of shared state tractable; and the ecosystem for network services has moved that way, so the libraries are there.

Against: it colours every function in the call path, so partial adoption means duplicated interfaces; one blocking call anywhere stalls everything, and finding those is ongoing work; it gives nothing for CPU-bound code; and for the common case of a few dozen concurrent waits, a thread pool is fewer concepts and the same speed.

The resolution is not a compromise but a criterion: choose it when the concurrency count is large or the protocol is long-lived. "Modern" is not a workload.

</details>

## Real-world reps

- [ ] For the slowest thing you own, write down one sentence: while it is slow, it is waiting on X, or computing Y. If you cannot, that is lesson 39's job first.
- [ ] Find a pool in your code and check what set its size. If it was a round number rather than a downstream limit, measure both.
- [ ] Find the place where two concurrency models meet in your codebase and check what state crosses the boundary.
- [ ] Write the shutdown path for one concurrent component you own, and test it by interrupting the process mid-work.
- [ ] Tomorrow: take the concurrency you added most recently and ask whether the sequential version was actually too slow.

## Going further

- [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html): the one interface behind threads, processes and interpreters
- [`asyncio`, Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html): the documented list of what does not belong in an event loop
- [PEP 703](https://peps.python.org/pep-0703/): what changes about this table without the interpreter lock
- [PEP 734](https://peps.python.org/pep-0734/): what a subinterpreter isolates, and what it does not
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
