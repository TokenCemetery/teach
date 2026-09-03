---
title: 40. Blocking Is a Bug
description: Why one blocking call in an async task stalls work that has nothing to do with it, and what to do with the calls you cannot avoid
type: lesson
---

# Lesson 40. Blocking Is a Bug

**Mission link:** A production async service with an unexplained latency spike is often logically correct: one handler called something ordinary that happens to block, and every other request queued on that worker paid for it. Knowing what counts as blocking, and what to do about each kind, finds that before a user reports it.
**Primary source:** [tokio::task::spawn_blocking](https://docs.rs/tokio/1.53.1/tokio/task/fn.spawn_blocking.html)
**Prerequisites:** [Lesson 39](0039-tasks-and-the-send-bound.md), [Lesson 38](0038-wakers-executors-and-runtimes.md)

## Warm-up

1. ▢ Lesson 39 spawned each unit of work as its own task, polled independently by whichever worker thread was free. A runtime has a fixed number of worker threads and more tasks than that are spawned at once. How many can be actively polled at the same instant, and what happens to the rest?

<details markdown="1"><summary>Check</summary>

At most one task per worker thread; the remainder sit in the runtime's queue until a worker is free to poll them. A task waiting its turn is ordinary and expected; it only becomes a problem if a worker never becomes free.

</details>

2. ▢ Lesson 38 built an executor that polls a future and then does nothing further for it until its waker fires. In one sentence: what actually gives a task more of the worker thread's attention once it has returned `Poll::Pending`?

<details markdown="1"><summary>Check</summary>

Nothing does, until its waker wakes it and the executor schedules it again. A future's own code only runs while the executor is actively calling `poll` on it, never in the gap between one poll and the next.

</details>

## Know this

### A task only yields at an await point

An executor gives a task the worker thread's attention until that task's `poll` call returns, either `Ready` or `Pending`. Returning `Pending` happens at an await point, where whatever is awaited says it is not ready yet; that is the only place a well-behaved task hands the thread back. A statement between two awaits that does not return control, an ordinary blocking call or a computation that simply keeps computing, holds the worker for as long as it takes, and every other task assigned to that worker waits with it, not just the one that made the call.

```rust
async fn ticker() {
    for i in 0..3 {
        tokio::time::sleep(std::time::Duration::from_millis(20)).await;
        println!("tick {i}");
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let blocker = async {
        std::thread::sleep(std::time::Duration::from_millis(100)); // an ordinary blocking call
        println!("blocking work done");
    };
    tokio::join!(blocker, ticker());
}
```

Across three runs, this printed `blocking work done` followed by all three `tick` lines, in that order every time, even though `ticker` has nothing to do with the blocker's work. Nothing about the runtime can distinguish legitimate slow work from a task that has planted itself on the worker; both look identical from inside `poll`. That is why this is a bug rather than a slowdown: no error, no log line, nothing a reviewer can point at beyond how long the code happens to run.

### The cost, as a ratio, on a single worker

The clearest way to see the cost: give a runtime with one worker four tasks that each wait the same length of time, once the honest way and once the blocking way.

```rust
let mut set = Vec::new();
for _ in 0..4 { set.push(tokio::spawn(async { tokio::time::sleep(Duration::from_millis(200)).await; })); }
for h in set { h.await.unwrap(); }
// ...versus, timed the same way:
let mut set = Vec::new();
for _ in 0..4 { set.push(tokio::spawn(async { std::thread::sleep(Duration::from_millis(200)); })); }
for h in set { h.await.unwrap(); }
```

On a `current_thread` runtime, timing each block with `Instant` and printing `blocking.as_secs_f64() / async_sleep.as_secs_f64()` gave a ratio of 4.1, the same to one decimal place across three runs: the blocking version's total wall time over the async version's. The asynchronous sleeps overlap almost completely, since the worker only checks each when its timer fires, while the blocking sleeps queue one after another, each holding the only worker there is until it returns; four tasks that should finish together instead finish in series.

### The same measurement with several workers, honestly reported

A single worker makes the bug obvious; a runtime built with two worker threads, given the same eight tasks, is worth reporting because it is not.

```rust
let rt = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(2)
    .enable_time()
    .build()
    .unwrap();
```

Run through the same comparison inside `rt.block_on`, this printed a ratio of 2.1, the same across three runs. Two workers let two of the four blocking tasks run at once instead of none, so the blocking version takes about twice as long rather than four times, and a ratio of two reads as scheduling overhead rather than a stalled worker, which is why this survives review on multi-worker services when the single-worker case above would not.

### Three kinds of blocking, and each needs a different fix

Not every blocking call is the same problem. The first kind waits on something outside the program, such as a socket, a timer, or a file, and already has an asynchronous equivalent; the fix is to use it, which is what turned the ratio above from 4.1 back to 1. The second kind also waits on the world but has no asynchronous equivalent, commonly a synchronous library with no async client; the honest fix is a dedicated thread, `tokio::task::spawn_blocking`, returning a value through an ordinary `JoinHandle`.

```rust
fn no_async_equivalent(input: u32) -> u32 {
    std::thread::sleep(Duration::from_millis(50)); // stands in for a blocking-only API
    input * 2
}

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let handle: tokio::task::JoinHandle<u32> = tokio::task::spawn_blocking(|| no_async_equivalent(21));
    let value = handle.await.unwrap();
    println!("spawn_blocking returned {value}");
}
```

This printed `spawn_blocking returned 42` on three separate runs, the value coming back through the `JoinHandle` rather than being lost to the closure. The third kind is a computation that simply takes a long time with nothing external involved; there is no I/O to make asynchronous and no thread pool worth paying for, so the fix is giving the executor a chance to poll other tasks partway through, with `tokio::task::yield_now`.

```rust
async fn cpu_bound_with_yield() {
    let mut total: u64 = 0;
    for i in 0..2_000_000_000u64 {
        total = total.wrapping_add(i);
        if i % 100_000_000 == 0 { tokio::task::yield_now().await; }
    }
    println!("cpu (yielding) done, total {total}");
}
```

Joined with the same `ticker`, all three ticks printed before this finished, on three of three runs; with the `yield_now` call removed, the loop's own line printed first, before any tick, also on three of three runs. Its documentation says exactly this: the task is re-added at the back of the queue and other pending tasks are scheduled, with no other waking needed.

### What spawn_blocking actually costs

`spawn_blocking` is not free, and treating it as a reflex hides that. Its signature, `pub fn spawn_blocking<F, R>(f: F) -> JoinHandle<R> where F: FnOnce() -> R + Send + 'static, R: Send + 'static`, carries the same `Send + 'static` shape lesson 39 required of every spawned future. That thread comes from a separate pool, sized independently of the runtime's own workers: "Tokio will spawn more blocking threads when they are requested through this function until the upper limit configured on the `Builder` is reached. After reaching the upper limit, the tasks are put in a queue." The default limit is 512, generous for ordinary I/O, though a flood of long-lived or CPU-bound work can still queue behind it. Moving the call off the runtime's own worker also does not make it interruptible: "tasks spawned using `spawn_blocking` cannot be aborted because they are not async. If you call `abort` on a `spawn_blocking` task, then this will not have any effect, and the task will continue running normally. The exception is if the task has not started running yet; in that case, calling `abort` may prevent the task from starting." Lesson 42 covers cancellation properly; the fact belongs here because `spawn_blocking` solves stalling, not stopping. `tokio::task::block_in_place` is narrower than it looks: multi-thread runtime only, panicking on a `current_thread` one.

### The habit to break

The reflex to watch for is reaching for `spawn_blocking` on anything that merely feels slow, including calls with a good asynchronous equivalent. Wrapping `std::fs::read_to_string` in `spawn_blocking` "fixes" the stall, but spends a thread from a separate pool for work `tokio::fs::read_to_string` already does correctly without that cost. Name the honest fix first: is there an asynchronous version of this operation. Only once the answer is no does `spawn_blocking` become right, and only once the work is pure computation with nothing to await does `yield_now`.

## Practice

1. ▢ Predict what this prints and in what order, then run it.

   ```rust
   #[tokio::main(flavor = "current_thread")]
   async fn main() {
       let a = async { std::thread::sleep(std::time::Duration::from_millis(50)); println!("a done"); };
       let b = async { tokio::time::sleep(std::time::Duration::from_millis(10)).await; println!("b done"); };
       tokio::join!(a, b);
   }
   ```

<details markdown="1"><summary>Check</summary>

It prints `a done` then `b done`, even though `b`'s wait is shorter: `a` never awaits, so it holds the single worker until it returns, before `b` gets polled at all.

</details>

2. ▢ Predict whether joining a tight, non-yielding loop with an async `ticker` on a `current_thread` runtime prints any tick before the loop finishes, then run it and check across a few runs.

<details markdown="1"><summary>Hint</summary>

What would have to happen for the executor to poll `ticker` while the loop is still running?

</details>

<details markdown="1"><summary>Check</summary>

No: the loop never returns `Pending`, so the worker never polls `ticker` until the loop's own future finishes. This held on three of three runs.

</details>

3. ▢ For each of the following, name which of the three kinds of blocking it is and the honest fix.

   - a) An async handler calls a synchronous database driver with no async client available.
   - b) An async handler calls `std::fs::read_to_string` to load a template file.
   - c) An async handler hashes several megabytes of data with no I/O involved.

<details markdown="1"><summary>Check</summary>

a) No async equivalent, so `spawn_blocking`. b) An async equivalent exists, `tokio::fs::read_to_string`, so use it rather than `spawn_blocking`. c) A long computation with nothing to await, so `tokio::task::yield_now` between chunks, or `spawn_blocking` if it is long enough to be worth a dedicated thread.

</details>

4. ▢ `let handle: tokio::task::JoinHandle<u32> = tokio::task::spawn_blocking(|| 6 * 7);` compiles. Predict what `handle.await` produces and its type, then run it.

<details markdown="1"><summary>Hint</summary>

`JoinHandle<R>`'s `Future` implementation has an `Output` that accounts for the closure panicking as well as succeeding.

</details>

<details markdown="1"><summary>Check</summary>

`handle.await` produces `Result<u32, JoinError>`, `Ok(42)` here; `.unwrap()` gives the plain `u32`, `42`, which is what a run prints.

</details>

5. ▢ A `spawn_blocking` task is partway through a long call with no async equivalent when its `JoinHandle` is aborted. Predict what happens to the call, then check against this lesson's quotation.

<details markdown="1"><summary>Check</summary>

Nothing: `abort` has no effect once a `spawn_blocking` task has started, and the closure runs to completion regardless. It only has a chance of working before the task starts.

</details>

## Real-world reps

- [ ] In your project's async version, find the call that reads a source's contents; if it is an ordinary, thread-blocking read, replace it with `tokio::fs`'s equivalent rather than wrapping it in `spawn_blocking`, and confirm the summary produced is unchanged.
- [ ] Put a thread-blocking read back into one source's task while the others read from sources that make them wait, run it, and write one line saying how you would have noticed this in a program you had not just broken on purpose.
- [ ] Tomorrow: find one call in recent code that runs inside an `async fn` and ask, honestly, which of this lesson's three kinds it is.

## Going further

- [Blocking and Yielding](https://docs.rs/tokio/1.53.1/tokio/task/index.html#blocking-and-yielding): tokio's own explanation of the problem and its blocking APIs
- [tokio::task::yield_now](https://docs.rs/tokio/1.53.1/tokio/task/fn.yield_now.html): the cooperative-yield function used above
- [tokio::runtime::Builder::max_blocking_threads](https://docs.rs/tokio/1.53.1/tokio/runtime/struct.Builder.html#method.max_blocking_threads): the blocking pool's default size and how to change it
- [tokio::task::JoinHandle::abort](https://docs.rs/tokio/1.53.1/tokio/task/struct.JoinHandle.html#method.abort): the method this lesson's cancellation quotation describes
- [Bridging with sync code](https://tokio.rs/tokio/topics/bridging): the tutorial's page on the same boundary, crossed the other way
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
