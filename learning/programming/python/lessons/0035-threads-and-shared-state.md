---
title: 35. Threads and Shared State
description: A pool instead of raw threads, a queue instead of a lock, and the exception nobody saw
type: lesson
---

# Lesson 35. Threads and Shared State

**Mission link:** Threads are the right tool for waiting, which is most of what a service does. The failures are not exotic: an exception nobody looked at, a lock held too long, and shared state that did not need to be shared.
**Primary source:** [The Python Standard Library, concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
**Prerequisites:** [Lesson 34](0034-the-gil-precisely.md)

## Warm-up

1. ▢ Lesson 34: eight threads ran a check-then-act on one cache key. How many objects did they create?

<details markdown="1"><summary>Check</summary>

Eight, where one was intended. The dict was fine; the invariant across two statements was not.

</details>

2. ▢ What is a thread doing, in a program where threads help?

<details markdown="1"><summary>Check</summary>

Waiting. On a socket, a file, a lock, or a subprocess. Waiting releases the interpreter lock.

</details>

## Know this

### Start with a pool, not a thread

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, urls))
```

`ThreadPoolExecutor` bounds the concurrency, reuses threads, propagates return values, and joins everything on exit. Raw `threading.Thread` is for the long-lived background worker that a pool does not model: a scheduler loop, a log flusher, a signal handler.

Sizing: for waiting work, more workers than cores is correct, and the right number is set by the thing you are waiting on. Eight database connections in the pool means eight workers, not fifty, and exceeding the remote service's limits turns concurrency into rate-limit errors.

### The exception nobody saw

This is the failure that ships:

```python
with ThreadPoolExecutor(3) as pool:
    futures = [pool.submit(process, item) for item in items]
```

```text
submitted and pool closed, no exception raised yet
```

The block exits cleanly, the process continues, and one item raised `ValueError` that nobody will ever see. A future holds its exception until someone asks:

```python
for future in futures:
    future.result()          # re-raises here, in this thread
```

`pool.map` is safer, because iterating the result raises, but only when you actually iterate it and only up to the first failure. When every item matters, use `as_completed` and handle each one:

```python
from concurrent.futures import as_completed

for future in as_completed(futures):
    try:
        handle(future.result())
    except SomeError:
        log.exception("item failed")
```

**Rule: every `submit` needs a matching `result()` somewhere, or you have written `except Exception: pass` by accident.**

### Do not share; hand over

The best fix for shared mutable state is not a lock, it is a queue.

```python
import queue

q: queue.Queue[Item | None] = queue.Queue()

def worker():
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        results.append(transform(item))     # append is safe; see lesson 34
        q.task_done()
```

`queue.Queue` is thread-safe by design and is the channel between producers and consumers. Verified: three workers draining 100 items produced exactly 100 results, with no lock in the code.

The other way to remove sharing is to return instead of accumulate. Each worker computes its own subtotal, the caller sums them. No lock, no queue, no ordering question.

### Locks, when the invariant is genuinely shared

```python
lock = threading.Lock()

with lock:
    if key not in cache:
        cache[key] = build(key)
```

| Primitive | For |
|---|---|
| `Lock` | one holder; a second acquire from the **same** thread deadlocks |
| `RLock` | reentrant: the same thread may acquire it repeatedly, and must release as often |
| `Event` | one-way signal: "start", "shut down" |
| `Condition` | wait until a predicate holds, with a lock attached |
| `Semaphore` | at most n holders: rate limiting, connection caps |
| `Barrier` | all n threads wait for each other |

Verified: a plain `Lock` acquired twice from one thread reported `True` then `False` with a timeout, and without a timeout the second acquire waits forever. An `RLock` nested inside itself is fine. That is the whole difference, and it matters when a locked method calls another locked method of the same object.

Four rules that prevent nearly all lock bugs:

1. **Hold it for as little as possible.** Never across I/O if it can be avoided; compute outside, assign inside.
2. **Always use `with`.** A `finally` you wrote by hand will eventually be skipped by an early return.
3. **One order, everywhere.** Deadlock needs two locks taken in opposite orders by two threads. Pick a global order and document it.
4. **Guard the invariant, not the object.** The lock exists for the rule that spans statements.

`lock.acquire(timeout=...)` turns a deadlock into a detectable failure, which is worth it in a long-running service.

### Thread-local state

```python
data = threading.local()
data.request_id = generate()        # each thread has its own
```

Legitimate for per-thread context: a request id, a database connection, a transaction. Verified: five threads each kept their own value across a sleep. It is still global state, so it makes functions depend on invisible context and makes tests order-dependent; prefer passing the value explicitly, and use `contextvars` instead when `asyncio` is involved, since a thread-local is shared by every task on one event-loop thread.

### Daemon threads and shutdown

```python
t = threading.Thread(target=flush_loop, daemon=True)
```

A daemon thread does not keep the process alive, so the interpreter exits without waiting for it, and its `finally` blocks may not run. That makes it wrong for anything that must finish, such as flushing a buffer. The alternative is an `Event`:

```python
stop = threading.Event()

def flush_loop():
    while not stop.wait(timeout=5.0):
        flush()

stop.set(); t.join(timeout=10)
```

`Event.wait` with a timeout is the correct idiom for a periodic loop: it sleeps and is interruptible, where `time.sleep` in a loop delays shutdown by up to one interval.

## Practice

1. ▢ Find the defect.

   ```python
   with ThreadPoolExecutor(8) as pool:
       for order in orders:
           pool.submit(charge, order)
   log.info("charged %d orders", len(orders))
   ```

<details markdown="1"><summary>Hint</summary>

What happens to the return value, and what happens to an exception?

</details>

<details markdown="1"><summary>Check</summary>

Nothing collects the futures, so an exception inside `charge` is stored in a future that is immediately discarded. Every failed charge is silent, and the log line claims success for all of them.

```python
with ThreadPoolExecutor(8) as pool:
    futures = {pool.submit(charge, o): o for o in orders}

failed = []
for future in as_completed(futures):
    try:
        future.result()
    except ChargeError:
        log.exception("charge failed for %s", futures[future].id)
        failed.append(futures[future])
log.info("charged %d orders, %d failed", len(orders) - len(failed), len(failed))
```

The dict mapping future to input is the standard trick for knowing **which** item failed, since `as_completed` yields in completion order.

</details>

2. ▢ Rewrite without a lock.

   ```python
   totals = {}
   lock = threading.Lock()

   def process(chunk):
       for row in chunk:
           with lock:
               totals[row.country] = totals.get(row.country, 0) + row.amount
   ```

<details markdown="1"><summary>Check</summary>

```python
from collections import Counter

def process(chunk) -> Counter[str]:
    local = Counter()
    for row in chunk:
        local[row.country] += row.amount
    return local

with ThreadPoolExecutor(8) as pool:
    totals = sum(pool.map(process, chunks), Counter())
```

Each worker accumulates privately and returns; the caller merges. No lock is taken per row, the workers do not contend, and the shared state exists only in the thread that assembles the answer.

That is the general move: **turn shared accumulation into returned values.** It is faster as well as safer, because the original acquires a lock once per row.

</details>

3. ▢ Match the primitive.

   - a) At most five concurrent calls to a rate-limited API
   - b) Tell four worker threads to shut down
   - c) A method holding a lock that calls another method of the same object which also locks
   - d) A consumer that should sleep until there is work
   - e) A per-request correlation id available to every function in the call stack

<details markdown="1"><summary>Check</summary>

- a) `Semaphore(5)`, or a pool with `max_workers=5`, which is usually simpler.
- b) `Event`: one `set()` observed by all of them.
- c) `RLock`. Or better, restructure so the locking happens at one level and the inner method assumes the lock is held.
- d) `queue.Queue`, whose `get` already blocks. `Condition` when the wait is on a predicate rather than an item.
- e) `threading.local`, or `contextvars.ContextVar` if `asyncio` is in play. Passing it as an argument is better than either where the call chain allows it.

</details>

4. ▢ Why is this dangerous, and what does the fix cost?

   ```python
   with lock:
       response = http.get(url)          # network call, inside the lock
       cache[url] = response.json()
   ```

<details markdown="1"><summary>Check</summary>

The lock is held for the duration of a network call, so every other thread wanting **any** key waits on this one request. Under load the pool serialises completely, and a slow remote turns into a stalled service. A timeout on the request is essential and does not fix the contention.

The fix, and its cost:

```python
data = http.get(url).json()          # outside
with lock:
    cache.setdefault(url, data)      # inside, and cheap
```

Now two threads may fetch the same URL simultaneously, and one result is discarded. That is the trade: a duplicated request instead of a serialised pool, and for an idempotent read it is almost always the better side. When duplication is unacceptable, use a per-key lock so only the threads wanting that key wait.

</details>

5. ▢ A background thread writes metrics every five seconds and is created with `daemon=True`. On shutdown, up to five seconds of metrics are lost. Fix it.

<details markdown="1"><summary>Check</summary>

```python
stop = threading.Event()

def metrics_loop():
    try:
        while not stop.wait(5.0):
            flush()
    finally:
        flush()                      # the last one

t = threading.Thread(target=metrics_loop)    # not a daemon
t.start()
...
stop.set()
t.join(timeout=10)
```

Three changes matter. Not a daemon, so the interpreter waits for it. `Event.wait` rather than `time.sleep`, so `stop.set()` interrupts the sleep immediately instead of after up to five seconds. And a `finally` that flushes once more, which only runs because the thread is no longer a daemon.

</details>

6. ▢ A service uses 200 threads and gets slower than with 20. Give three explanations.

<details markdown="1"><summary>Check</summary>

- **The bottleneck is downstream.** A database with a 20-connection pool serves 20 at a time; the other 180 threads queue, and the queueing adds latency and timeouts without adding throughput.
- **Contention.** If the handlers share a lock, more threads mean more waiting on it, and the lock becomes the serialisation point that the GIL was blamed for.
- **Memory and scheduling.** Each thread has a stack, and 200 of them add allocation, context switching, and cache pressure. If any part of the work is CPU-bound, those parts now interleave badly with no parallelism gained, per lesson 34.

The diagnostic is to find out what the threads are waiting on, and the fix is usually to bound the pool to whatever the scarcest downstream resource allows.

</details>

## Real-world reps

- [ ] Grep for `pool.submit` and `executor.submit` in code you own and check that every one has a `result()` reached on some path. Each that does not is a silent failure.
- [ ] Find a lock in your code and measure how long it is held. If a network or database call happens inside it, move the call out and decide what duplication costs.
- [ ] Replace one lock-protected shared accumulator with per-worker results merged by the caller.
- [ ] Find every `daemon=True` thread and ask what it loses if the process exits mid-iteration.
- [ ] Tomorrow: set your pool size from the downstream limit rather than from the number of items, and see whether throughput changes.

## Going further

- [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html): executors, futures, `as_completed`, and the exception semantics
- [`threading`](https://docs.python.org/3/library/threading.html): every primitive, and the notes on daemon threads and shutdown
- [`queue`](https://docs.python.org/3/library/queue.html): the thread-safe channel, including `task_done` and `join`
- [`contextvars`](https://docs.python.org/3/library/contextvars.html): the per-task alternative to thread-local state
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
