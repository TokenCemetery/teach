---
title: Async
description: The stage 6 reference sheet: the poll model, what a runtime adds, the failures that arrive without an error, and where cancel safety is documented
type: reference
---

# Async

Lookup sheet for stage 6. The question it exists to answer: **which of the ways this stalls or loses data am I looking at, and what is the honest fix?**

## The poll model, in the fewest true words

| Term | What it is |
|---|---|
| Future | A state machine with one method, `poll`, driven by whoever holds it; nothing runs until something polls it |
| `Poll<T>` | `enum Poll<T> { Ready(T), Pending }`, matched exhaustively like any other two-variant enum |
| `.await` | Not a call: the point where a generated state machine suspends and resumes, forwarding `Pending` upward and moving on only once the awaited future reports `Ready` |
| The waker contract | Returning `Pending` obliges the future to arrange, by whatever means it needs, for the `Waker` it was given to be called once progress is possible; skipping that half of the contract is what leaves a future polled once and never again |
| Busy-spin | An executor that polls again immediately after `Pending`, with nothing telling it to wait; correct, since a future's own answer never depends on how eagerly it is asked, and wasteful, since it spends a processor on nothing between real changes |

`Waker::noop`, stable since release 1.85, builds an executor loop with no waker at all, which is the busy-spin made concrete rather than a tool to reach for outside a demonstration.

## What a runtime adds, and the flavour decision

Beyond a bare poll loop, a runtime bundles an I/O driver that turns socket, file and timer readiness into a wake, and a scheduler that places tasks on worker threads and requeues a woken one.

| Flavour | Worker threads | Choose when |
|---|---|---|
| `current_thread` | None of its own; runs only inside the call to `Runtime::block_on` or the thread `#[tokio::main]` starts on | A single source, a test wanting deterministic ordering, or diagnosing a suspected stall |
| `multi_thread` (the default) | Spawns its own pool | More than one independent unit of work that should genuinely overlap |

Running suspect code under `current_thread` is the cheapest diagnostic this stage has: with one worker, a blocking call or a non-yielding loop stalls everything sharing it, visibly, where a spare worker under `multi_thread` can keep the rest of the program moving and hide the same bug behind a thread that happened to be free.

## Bounds: what each spawn demands

| Call | Bound | Why |
|---|---|---|
| `thread::spawn` | `F: FnOnce() -> T + Send + 'static`, `T: Send + 'static` | The closure and its result may end up owned by a thread with no relation to the caller's own stack frame |
| `Scope::spawn` | `F: Send + 'scope`, `T: Send + 'scope` | The scope guarantees every thread it spawns is joined before the scope itself returns, so a borrow only needs to outlive the scope, never `'static` |
| `tokio::spawn` | `F: Future + Send + 'static`, `F::Output: Send + 'static` | The task may be moved to a different worker thread than the one that spawned it, and it keeps running whether or not anything ever awaits its `JoinHandle`, so it may still be alive after the function that spawned it returns |

There is no scoped spawn for tasks. `thread::scope` can let a borrowed local cross into a thread because the scope itself guarantees the join happens first; tokio's task module offers only `spawn`, with no equivalent guarantee, because a spawned future is registered with the runtime immediately and may still be running long after the code that called `spawn` has moved on. A future that would have borrowed a local under the scoped-thread design has to move an owned value in instead, or share it behind an `Arc`.

## The failure table

Five ways async code stalls or loses data without an error message, and how to tell which is which from outside the process.

| Failure | Presents as | Idle or busy | Would a test catch it | Honest fix |
|---|---|---|---|---|
| The never-woken future | One poll, then nothing further: no more output, no measurable CPU | Idle | No, unless the test itself runs under a timeout that expects to see completion | Store the waker somewhere real and call it once progress is possible, or hand the future to a runtime that already does |
| The blocking stall | Everything sharing the worker queues up behind the blocking call, reported as a ratio of the blocking run's time over the honest one's, never as a duration | Busy: CPU time tracks wall time on the thread making the call | No, unless the test measures overlap between tasks rather than only the final answer | An asynchronous equivalent where one exists; `spawn_blocking` only once none does; `yield_now` between chunks of pure computation |
| The not-`Send` future | Refused before anything runs: a compile error naming the value or type still alive across an `.await` | Neither; it never builds | Yes, trivially, since it fails to compile | Narrow the value's scope so it does not survive the `.await`, or choose a type that genuinely is `Send` |
| Cancel-unsafe work lost | A final total that does not add up; no panic, no log line, nothing to grep for | Neither, or idle between laps; the loss itself is silent | No, unless the assertion checks the exact expected value on every run rather than a plausible-looking one | Move whatever state must survive a lost race outside the loop, so a fresh attempt resumes instead of restarting from nothing |
| The self-inflicted deadlock | A hang with no panic, indistinguishable from the never-woken future without checking CPU use | Idle if the cycle is a lock awaited across a spawned task; busy if it is a non-yielding loop competing with the task that would clear its flag | No, unless run under a watchdog | Never await something whose completion depends on a guard your own code is still holding; release the guard first |

## Shared state across an await

| | `std::sync::Mutex` | `tokio::sync::Mutex` |
|---|---|---|
| `lock` | An ordinary call, blocking the thread only as long as the almost always uncontended lock is actually held | An `async fn`, itself a suspension point |
| Its guard | Not `Send`; alive across an `.await` it makes the whole future not `Send`, refused at `tokio::spawn` | `Send`; may cross an `.await` and still be spawned |
| What it costs | Nothing beyond the lock itself | A suspension point on every call, and no poisoning to report a panic that happened mid-guard |
| Reach for it when | The critical section holds no `.await`, which is most shared data | The critical section must itself contain an `.await`, such as a write that has to finish before the next task's write may start |

The honest default is ending the critical section before the `.await` rather than changing the mutex's type: most diagnostics naming a guard that is not `Send` are fixed by narrowing where the guard lives, and reaching for the asynchronous mutex first only buys a suspension point nothing needed.

## Cancellation and cancel safety

Cancelling a future is dropping it: no notification, no dedicated error, just the destructors of whatever locals were alive at the suspended point, in the same reverse order any other scope exit uses. Three events do this to code you write: a `timeout` elapsing, a `select!` branch losing, and `JoinHandle::abort`. Dropping a `JoinHandle` is not a fourth: the task it named keeps running regardless.

Cancel safety is a narrower, separate question: can this future be dropped and recreated from scratch with nothing lost. The test is exact: a future that has not yet completed must be a no-op to drop and recreate. The answer is never a general rule; it is documented once per method, so look up the specific method before it goes into a `select!` branch. One trait's documentation page carries every verdict side by side.

| Method | Verdict |
|---|---|
| `AsyncReadExt::read` | Cancel safe: guaranteed that no data was read if another branch completes first |
| `mpsc::Receiver::recv` | Cancel safe: guaranteed that no message was received on the channel if another branch completes first |
| `tokio::sync::Mutex::lock` | A caveat, neither of the other two: losing the race loses your place in the queue, which is a fairness cost, not data loss or corruption |

None of these three verdicts generalise to a method the page has not covered; a state built up across more than one call, such as a partial batch held in a loop's own local, is not covered by any one call's cancel safety and has to be moved outside the racing branch instead.

## Pinning

`Pin` promises that its target has stopped moving in memory until its own drop runs. `Future::poll` takes `Pin<&mut Self>` rather than a plain `&mut Self` because a compiler-generated state machine can hold a field that borrows another field of the same generated struct, and an ordinary move copies bytes with no per-field fix-up, which would leave that borrow pointing at the wrong place. `Unpin` is an auto trait implemented for almost every type, which is why wrapping something in `Pin` is usually a formality; the compiler infers the opposite, `!Unpin`, only for a generated future that borrows across one of its own `.await` points, and a reader meets the consequence in three places: calling `poll` directly on a bare future, which needs `std::pin::pin!` or `Box::pin` first; collecting futures produced by more than one distinct `async fn` into one collection, which needs boxing behind `Pin<Box<dyn Future<Output = T>>>` because boxing is what erases the otherwise-mismatched compiler-generated types; and awaiting `&mut some_future` again and again inside a loop, which needs the future pinned first, since `&mut F` implements `Future` only when `F: Unpin`.

## Deliberately not in this stage

| Topic | Where it went |
|---|---|
| `Stream` | The standard library has not settled the trait; not taught in this arc |
| `futures`, `tokio-stream`, `async-std`, `smol` | Not taught; tokio is this stage's only runtime crate |
| `async-trait` | Named once, for the `Send`-on-a-trait-method gap it papers over; not taught as a general tool |
| Manual `Pin` projection, and writing `Future` by hand for a type with genuine internal pointers | Stage 7 |
| Comparing memory orderings | Stage 7, as already settled for threads in stage 5 |
| Building a `Waker` from a raw pointer and a vtable | Stage 7; this stage's own hand-built executors use the safe `Wake` trait instead |
| `tokio_util::CancellationToken` | Named once, for cooperative shutdown across several tasks; not taught |
| `tokio::sync::RwLock`, `Semaphore`, `Notify`, `oneshot` | Named so a reader recognises each on sight; their APIs are not worked through here |

## Where the project should be

The stage 6 slice of the arc's rep project, `logsum`, reads from sources that wait, without stalling the whole run on the slowest one. See [the project](the-project.md) for the full brief and the state expected at the end of every stage.
