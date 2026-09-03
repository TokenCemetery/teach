---
title: 45. Reading an Async Failure
description: The five ways async code fails without an error message, and how to tell which one you are looking at
type: lesson
---

# Lesson 45. Reading an Async Failure

**Mission link:** This closes the stage: a stalled async program almost never announces itself, so the skill that ships is recognising which of a few shapes it is from the outside, and reaching for the fix that removes it rather than one that only hides it.
**Primary source:** [tokio::runtime](https://docs.rs/tokio/1.53.1/tokio/runtime/index.html)
**Prerequisites:** [Lesson 40](0040-blocking-is-a-bug.md), [Lesson 43](0043-cancellation-safety.md)

## Warm-up

1. ▢ A spawned future has to satisfy one extra bound that `Future` itself does not require. Which bound, and whose signature actually demands it?

<details markdown="1"><summary>Check</summary>

`Send`, plus `'static`. `Future` says nothing about either; `tokio::spawn`'s signature requires `F: Future + Send + 'static`, so the bound comes from spawning, not the trait.

</details>

2. ▢ In a `select!` loop, why can a branch lose data it had already collected, with nothing reporting an error?

<details markdown="1"><summary>Check</summary>

Losing the race drops that branch's future mid-poll: no unwinding, no notification, just a stop. Anything the branch was still holding in its own local state, rather than outside the branch, disappears with it.

</details>

## Know this

### 1. The idle stall: never polled again

A future is only re-polled because something calls the waker it was given. If a hand-rolled `poll` returns `Pending` without storing that waker anywhere, nothing will ever call it:

```rust
struct Stuck { polled: u32 }

impl Future for Stuck {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        self.polled += 1;
        println!("polled {} time(s)", self.polled);
        Poll::Pending
    }
}
```

Spawned and awaited through a two-second `timeout`: three watchdog runs, three timeouts, `polled 1 time(s)` printed once each time, then nothing. Comparing CPU time against wall-clock time showed none of it spent running: polled once, nothing left for the runtime to do. The same shape follows a `JoinHandle` dropped without ever being awaited while something downstream still needed that await: the task keeps running, but whatever depended on hearing back does not. The tell either way is an idle process: no further output, no CPU spent, no watchdog will see it finish.

### 2. The busy stall: blocking without yielding

A blocking call inside an async task looks like ordinary slowness, which is what makes it dangerous. [Lesson 40](0040-blocking-is-a-bug.md) established the technique: compare tasks doing the same work asynchronously against tasks occupying the one worker thread synchronously instead, reported as a ratio, never a duration. Re-run here with the blocking side made CPU-bound rather than a sleep, so the busy tell is visible too:

```rust
for _ in 0..4 { set.push(tokio::spawn(async { sleep(Duration::from_millis(200)).await; })); }
// ...
for _ in 0..4 { set.push(tokio::spawn(async { spin_ms(200); })); }
```

`ratio blocking/async = 3.9`, measured twice, agreeing to one decimal place: four tasks that could have overlapped queued behind one occupied thread instead. The tell against shape one: CPU time tracks wall-clock time here, because the thread has genuine work, just the wrong task's, while every other queued task waits behind it. Idle means nothing is happening; busy means the wrong thing is, exclusively, on the thread that matters.

### 3. The good case: not Send at compile time

Holding a standard-library lock guard across an `.await` and spawning the future is the one failure here that never runs at all:

```rust
async fn touch(state: Arc<Mutex<u32>>) {
    let mut guard = state.lock().unwrap();
    sleep(Duration::from_millis(10)).await;
    *guard += 1;
}
```

```text
error: future cannot be sent between threads safely
   --> src/main.rs:13:18
    |
 13 |     tokio::spawn(touch(Arc::clone(&state))).await.unwrap();
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^ future returned by `touch` is not `Send`
    |
    = help: within `impl Future<Output = ()>`, the trait `Send` is not implemented for `std::sync::MutexGuard<'_, u32>`
note: future is not `Send` as this value is used across an await
   --> src/main.rs:6:38
    |
  5 |     let mut guard = state.lock().unwrap();
    |         --------- has type `std::sync::MutexGuard<'_, u32>` which is not `Send`
  6 |     sleep(Duration::from_millis(10)).await;
    |                                      ^^^^^ await occurs here, with `mut guard` maybe used later
note: required by a bound in `tokio::spawn`
```

The rest of that last note quotes tokio's own source by path and is trimmed. Two notes appear, and only one locates the problem: "required by a bound in `tokio::spawn`" only explains why `Send` is demanded, but "future is not `Send` as this value is used across an await" names the guard and the await keeping it alive, the line to change. [Lesson 39](0039-tasks-and-the-send-bound.md) covers the bound and [Lesson 41](0041-shared-state-across-an-await.md) covers this recurring cause; neither is repeated here.

### 4. Losing work silently: the cancel-unsafe branch

[Lesson 43](0043-cancellation-safety.md) built a `select!` loop whose partial batch lives inside the branch racing a timer:

```rust
tokio::select! {
    n = collect_two(&mut rx, &mut batch) => { if n == 0 { break; } seen.extend(batch); }
    _ = sleep(Duration::from_millis(30)) => { /* batch, and anything in it, is dropped here */ }
}
```

Fed the values one to five by a slower producer, run ten times: every run lost something, nine kept exactly `[1, 2, 5]` and one kept `[1, 2, 4, 5]`, so what was lost varied but full recovery never happened once. No error, no panic, nothing printed: the only tell is a total that does not add up. This is the opposite of shape three, the same mistake silent instead of refused, because nothing about a dropped `select!` branch need look like a failure.

### 5. The hang that is not a classic deadlock

Two mutexes locked in opposite order was stage 5's deadlock ([Lesson 36](0036-choosing-a-sharing-strategy.md)). Async adds a version that needs only one lock and one task:

```rust
let guard = state.lock().await;                 // tokio::sync::Mutex
let handle = tokio::spawn(async move { *other.lock().await += 1; });
handle.await.unwrap();                            // waits on work only dropping guard could unblock
drop(guard);
```

Three watchdog runs, three stalls at the two-second mark, idle exactly like shape one: awaiting the handle before releasing the lock it needs is a cycle of one task with itself, spread across an await instead of two threads. A second version needs no lock: a tight loop with no `.await`, waiting on a flag a spawned task will set, run on one worker against the same code on two. Three runs each: one worker gave up at the watchdog every time, busy rather than idle, because the loop itself is what is running; two workers finished in a fraction of that window every time, since the spawned task got a thread of its own. Same code, same bug, and worker count alone changed the outcome.

### 6. Confirming which one you have, and the four workarounds

Watchdog anything that might not finish; a clean run proves nothing. Ask, in order: idle or busy, separating shape one and the lock-cycle half of five from shape two and the single-worker half; did it fail to compile, already shape three, located for you; and does it behave differently on a current-thread runtime than a multi-thread one, the question [tokio::runtime](https://docs.rs/tokio/1.53.1/tokio/runtime/index.html) frames as the point of choosing between them. Current-thread hides nothing, since everything runs on the one watched thread; multi-thread can paper over the same bug with a spare worker.

Four tools make each problem go away without answering its question. `spawn_blocking` fixes shape two, but against an existing async version it spends a pool thread on what an `.await` would have done free. A `tokio::sync::Mutex` fixes shape three by making the guard `Send`, verified: swapping it in above compiles and prints `1`; the cost is a guard genuinely held across an await, shape five's cycle waiting to happen. `Box::pin` fixes a future that does not fit where placed, but against a real shape mismatch it hides that behind an allocation instead of a restructure. A longer timeout makes shape four rarer, not gone; moving state outside the branch, as Lesson 43 showed, is what stays fixed under load.

None of this makes anything faster. Async overlaps waiting, it does not shrink work: shape two's ratio got worse, not better, once real computation replaced a sleep. Nor does it remove stage 5's sharing decisions: an `Arc`, `Mutex` or atomic inside a task is still the tool [Lesson 36](0036-choosing-a-sharing-strategy.md)'s five questions would pick. The stage's project rep shows this: four sources read concurrently, one five times slower per line, finished in about the time that slow one alone would take, a ratio near 1.5 against reading them in sequence; the work per line never changed, only the idle time waiting for it did.

## Practice

1. ▢ A hand-rolled future's `poll` always returns `Pending` and never touches its `Context`. Spawned, then awaited through a two-second `timeout`, predict what the process looks like from outside, then run it.

<details markdown="1"><summary>Hint</summary>

Ask whether anything exists that could call this future's waker.

</details>

<details markdown="1"><summary>Check</summary>

Nothing does, so the runtime never revisits the task after its first poll. The process sits idle: no further output, no measurable CPU, until the watchdog gives up. Shape one, and it stalls every time.

</details>

2. ▢ Four tasks sleep asynchronously for an interval; four more spin a CPU-bound loop for the same interval. Predict which group finishes first, and by roughly what ratio.

<details markdown="1"><summary>Check</summary>

The asynchronous group finishes first, since the sleeps overlap on the reactor. The spinning group serialises behind the one worker thread, giving a ratio near four, the same measurement Lesson 40 used.

</details>

3. ▢ Given the notes "required by a bound in `tokio::spawn`" and "future is not `Send` as this value is used across an await", which tells you which line to change?

<details markdown="1"><summary>Check</summary>

The second. It names the guard and the `.await` keeping it alive, what has to move or disappear. The first only explains that `spawn` demands `Send`; it says nothing about where the fix belongs.

</details>

4. ▢ A `select!` loop keeps a partial batch inside the branch racing a timer, fed five values by a slower producer. Predict whether ten runs ever recover all five, and whether a lost run raises an error.

<details markdown="1"><summary>Hint</summary>

Ask where the partial batch lives relative to the branch, not how fast the producer is.

</details>

<details markdown="1"><summary>Check</summary>

None recovers all five, since the batch lives inside the branch dropped whenever the timer wins, and none raises anything: across ten runs, nine kept exactly three values and one kept four, every run losing one silently.

</details>

5. ▢ For `spawn_blocking`, a `tokio::sync::Mutex`, `Box::pin` and a longer timeout, name the shape each honestly answers, and what using it against another shape hides.

<details markdown="1"><summary>Check</summary>

`spawn_blocking` answers shape two's synchronous call; against an existing async version, it hides that an `.await` was free. A `tokio::sync::Mutex` answers a section that must survive an await; against shape three, it hides that the guard should never have crossed it, risking shape five. `Box::pin` answers a future too large to place; against a needed restructure, it hides the mismatch behind an allocation. A longer timeout answers nothing here; against shape four it only makes the loss rarer.

</details>

## Real-world reps

- [ ] Reproduce the idle stall and the busy stall yourself, with your own run counts and idle-versus-busy check, noting any numbers that differ from this lesson's.
- [ ] Give `logsum` a mode reading from several sources that each pause before producing a line, confirm no single slow source stalls the rest, then introduce two of this lesson's shapes and diagnose each from outside before fixing it.
- [ ] Tomorrow: pick one `tokio::spawn` call in code you can read and predict which shape it would fail as, before it ever does.

## Going further

- [Builder](https://docs.rs/tokio/1.53.1/tokio/runtime/struct.Builder.html): `worker_threads` and the two runtime flavours from code
- [JoinHandle](https://docs.rs/tokio/1.53.1/tokio/task/struct.JoinHandle.html): what aborting and dropping a handle each do to the task behind it
- [timeout](https://docs.rs/tokio/1.53.1/tokio/time/fn.timeout.html): the watchdog primitive used throughout this lesson
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
