---
title: 38. Wakers, Executors and Runtimes
description: How a future says it is ready to be polled again, and what a runtime does besides poll it
type: lesson
---

# Lesson 38. Wakers, Executors and Runtimes

**Mission link:** Lesson 37's `block_on` proved a future can run with no runtime at all, but its loop polled the same pending future again immediately, with nothing telling it when to try again. A future that returns `Pending` without wiring up its waker is invisible in a diff and silent in a test, and either burns a core for nothing or is never polled again.
**Primary source:** [tokio::runtime](https://docs.rs/tokio/1.53.1/tokio/runtime/index.html)
**Prerequisites:** [Lesson 37](0037-what-a-future-is.md), [Lesson 35](0035-channels.md)

## Warm-up

1. ▢ Lesson 37 built a `block_on` that loops, calling `poll` again immediately whenever the future returns `Poll::Pending`. What is that loop doing between the moments the future can actually progress, and what would have to be true of it to stop?

<details markdown="1"><summary>Check</summary>

It calls `poll` on a future that has not changed and cannot yet answer differently, which is pure waste. For the loop to stop, it would need to be told when trying again is worth doing, rather than guessing by trying constantly; that "telling" is this lesson's subject.

</details>

2. ▢ Lesson 35's `Receiver::recv` blocks the calling thread until a value arrives or every sender is dropped, with no loop checking in. What does that give the thread that a `try_recv` loop on a timer would not?

<details markdown="1"><summary>Check</summary>

Blocking hands the thread's idle time back to the operating system, which reschedules it only once a value exists, whereas a `try_recv` loop spends CPU on every failed check. The same shape reappears here: sleeping instead of spinning hands idle time back the same way, rather than guessing on a timer.

</details>

## Know this

### The waker contract, stated exactly

A future returning `Pending` tells its caller nothing about when to try again; lesson 37's loop could only guess, which is what made it spin. The standard library's own description of `Waker` states the contract in one place: "The typical life of a `Waker` is that it is constructed by an executor, wrapped in a `Context`, then passed to `Future::poll()`. Then, if the future chooses to return `Poll::Pending`, it must also store the waker somehow and call `Waker::wake()` when the future should be polled again." Returning `Pending` is only half the job; the other half is arranging, by whatever means the future needs, for that waker to be called once progress is possible. Skipping it breaks the one promise an executor is entitled to rely on, shown next.

### An executor that sleeps instead of spins

Building a `Waker` from a raw pointer and a vtable is `unsafe`; the standard library's safe route is the `Wake` trait, implemented for any `Arc<W>` and convertible with `Waker::from`. An executor that sleeps rather than spins can hand out a waker that unparks its own thread, then park whenever a poll returns `Pending`:

```rust
use std::future::Future;
use std::pin::{pin, Pin};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use std::time::Duration;

struct DelayedReady {
    started: bool,
    ready: Arc<AtomicBool>,
}

impl Future for DelayedReady {
    type Output = &'static str;
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        if self.ready.load(Ordering::Acquire) {
            return Poll::Ready("done");
        }
        if !self.started {
            self.started = true;
            let waker = cx.waker().clone();
            let ready = Arc::clone(&self.ready);
            thread::spawn(move || {
                thread::sleep(Duration::from_millis(50));
                ready.store(true, Ordering::Release);
                waker.wake();
            });
        }
        Poll::Pending
    }
}

struct ThreadWaker(Thread);

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
    fn wake_by_ref(self: &Arc<Self>) {
        self.0.unpark();
    }
}

fn block_on_parking<F: Future>(future: F) -> (F::Output, usize) {
    let mut future = pin!(future);
    let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
    let mut cx = Context::from_waker(&waker);
    let mut polls = 0usize;
    loop {
        polls += 1;
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return (value, polls),
            Poll::Pending => thread::park(),
        }
    }
}
```

Every part of this is standard library only: `Wake` is "a memory-safe and ergonomic alternative to constructing a `RawWaker`". Against a future that spawns a helper thread, sets a flag and calls `wake()` fifty milliseconds later, this executor polled exactly twice in three of three runs: once to find `Pending`, once more once `wake()` unparked it and the flag was set. The same future through lesson 37's spinning loop, using `Waker::noop()` (stable since release 1.85) with no parking, polled 2254746, 2060114 and 4217134 times across three runs to wait out the same fifty milliseconds. Only the poll count shows which one burns a core to get there.

### The future that never wakes

The contract cuts both ways: nothing forces a future to honour it, and one that returns `Pending` without arranging a wake leaves its caller with no recourse.

```rust
struct NeverWakes;

impl Future for NeverWakes {
    type Output = ();
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        println!("polled once");
        Poll::Pending
    }
}
```

Run through `block_on_parking` under a three-second watchdog, this stalled in three of three attempts: `polled once` printed once, then the watchdog killed the process, since nothing was ever going to call `wake()`. A future can be well-typed, compile cleanly, and still hang the task awaiting it forever, with no panic and no error to grep for. Lesson 45's triage starts from exactly this shape.

### Tokio: the executor nobody should write themselves

Both are toys; a real program reads sockets, timers and files, and rebuilding a waker-aware reactor for each would dwarf the program itself. Tokio 1.53.1 is that reactor, timer and scheduler already built, at about 213 million recent downloads read from crates.io. Its runtime module states what it bundles beyond polling: "the following runtime services are necessary: An I/O event loop, called the driver, which drives I/O resources and dispatches I/O events to tasks that depend on them. A scheduler to execute tasks that use these I/O resources. A timer for scheduling work to run after a set period of time." The same `DelayedReady` future needs no change to run under it:

```rust
#[tokio::main]
async fn main() {
    let value = DelayedReady { started: false, ready: Default::default() }.await;
    println!("value={value}");
}
```

This printed `value=done` in three of three runs: the future is unchanged, and what changed is who owns the waker and does the parking, now tokio rather than a hand-rolled loop.

### Two flavours, chosen rather than inherited

`#[tokio::main]` accepts a `flavor`. The default is the multi-thread scheduler: "the multi-threaded runtime requires the rt-multi-thread feature flag, and is selected by default". `#[tokio::main(flavor = "current_thread")]` selects "a single-threaded future executor" where "all tasks will be created and executed on the current thread." The runtime module names the consequence: "A multi-threaded runtime is always running because it spawns its own worker threads", while "a current-thread runtime does not spawn any worker threads, so it can only execute tasks when you provide a thread by calling `Runtime::block_on`." The `DelayedReady` example printed `value=done` in three of three runs under each flavour. What differs is the cost of a stall: one thread on a current-thread runtime does all the polling, so a block there blocks every task; a multi-thread runtime's other workers keep tasks moving, hiding the same stall. A current-thread runtime therefore makes a stall obvious, which is why lesson 40 measures it there.

### `block_on` is the boundary, not a tool for both sides

`Runtime::block_on` is how synchronous code, such as a plain `fn main`, hands control to the asynchronous world and gets a value back; `#[tokio::main]` expands to exactly this call. It is not a tool for asynchronous code to call on itself:

```rust
#[tokio::main]
async fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        println!("inner block_on ran");
    });
}
```

Calling `block_on` on a fresh runtime from inside an `async fn main` that `#[tokio::main]` is already driving panics:

```text
Cannot start a runtime from within a runtime. This happens because a function (like `block_on`) attempted to block the current thread while the thread is being used to drive asynchronous tasks.
```

The line above the message, an absolute path inside tokio's own source in the crate registry, is trimmed here. This panicked in three of three runs with identical wording: the thread driving one runtime's tasks cannot also block waiting on another. `block_on` belongs at the one seam between ordinary and asynchronous code, called once, not sprinkled through async functions to "just get the value".

## Practice

1. ▢ Take the parking `block_on_parking` above and swap only its waker, from `Waker::from(Arc::new(ThreadWaker(thread::current())))` to `Waker::noop()`, keeping `thread::park()` in the `Pending` arm. Predict what happens against `DelayedReady`, then run it under a watchdog.

   ```rust
   fn block_on_parking_noop<F: Future>(future: F) -> F::Output {
       let mut future = pin!(future);
       let waker = Waker::noop();
       let mut cx = Context::from_waker(waker);
       loop {
           match future.as_mut().poll(&mut cx) {
               Poll::Ready(value) => return value,
               Poll::Pending => thread::park(),
           }
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

The helper thread still calls `wake()` on the clone `cx.waker()` gave it. Does that call reach anything if the `Context` was built from a no-op waker?

</details>

<details markdown="1"><summary>Check</summary>

It hangs. Under a three-second watchdog this stalled in three of three attempts. `thread::park()` still runs, but the cloned waker is itself a no-op, so `wake()` does nothing and the thread never unparks, even though the flag is genuinely set fifty milliseconds later. Parking without a waker that can reach back is `NeverWakes`'s failure from the other direction.

</details>

2. ▢ `Waker` is documented as implementing `Clone`, `Send` and `Sync`. Predict whether a clone of this lesson's parking waker, moved into a new `thread::spawn` closure separate from the future's own helper thread, can `wake()` the parked executor from there.

<details markdown="1"><summary>Check</summary>

Yes. The standard library states this directly: "a waker may be invoked from any thread, including ones not in any way managed by the executor." Calling `wake()` on a clone from an unrelated spawned thread unparked the original thread in three of three runs, since `unpark` does not care who calls it.

</details>

3. ▢ Predict whether `DelayedReady` prints the same value under `#[tokio::main]` and under `#[tokio::main(flavor = "current_thread")]`, then run both to check.

<details markdown="1"><summary>Check</summary>

Yes, both printed `value=done` in three of three runs each. The flavour decides how many worker threads exist, not whether a correctly implemented future eventually completes.

</details>

4. ▢ The `block_on`-inside-async panic in this lesson is not a compile error; the code that triggers it type-checks cleanly. Predict what kind of rule it is actually enforcing, then read the panic message again with that question in mind.

<details markdown="1"><summary>Hint</summary>

Ask what the thread calling the inner `block_on` was already doing at the moment it tried to block.

</details>

<details markdown="1"><summary>Check</summary>

A runtime behaviour rule, not a syntax or type rule: the thread driving the outer runtime's tasks cannot also sit blocked on an inner one, since nothing would be left to drive the outer tasks meanwhile. The panic names this directly, since nothing about the types says which thread is doing what.

</details>

5. ▢ A judgement call: for each program, say whether current-thread or multi-thread is the more honest default flavour.

   - a) A command-line tool that reads one file, with nothing else running while it does.
   - b) A tool reading several independent sources at once, where one being slow must not stall the others.
   - c) A test that wants a single, deterministic thread to reason about ordering.

<details markdown="1"><summary>Check</summary>

a) Current-thread: nothing here benefits from more than one worker, so extra threads would sit idle. b) Multi-thread: with only one thread, a stall on one source stalls every source, with no second worker to keep the others moving. c) Current-thread: reasoning about task order is far simpler with one thread scheduling everything than with several workers that may pick tasks up in any order.

</details>

## Real-world reps

- [ ] Wrap your project's `main` in `#[tokio::main]` for the first time, choosing `current_thread` or the default multi-thread flavour deliberately, and confirm the sample input's summary matches stage 5's.
- [ ] Add a comment above `main` saying which flavour you chose and what would make the other flavour the right one instead.
- [ ] Tomorrow: pick one blocking call still inside your project's `main` and note, without changing it, its cost to the rest of the program on a current-thread runtime.

## Going further

- [tokio::main](https://docs.rs/tokio/1.53.1/tokio/attr.main.html): the attribute macro's flavour parameter and its default
- [std::task::Wake](https://doc.rust-lang.org/std/task/trait.Wake.html): the safe trait for building a waker without `unsafe`, with its own worked `block_on` example
- [std::task::Waker](https://doc.rust-lang.org/std/task/struct.Waker.html): the handle itself, its contract, and its `Send` and `Sync` guarantee
- [std::thread::park](https://doc.rust-lang.org/std/thread/fn.park.html): the blocking primitive this lesson's executor sleeps on, and its spurious-wake caveat
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
