---
title: 42. Cancellation
description: Stopping a future means dropping it, which is why nothing gets told and why the work simply stops where it was
type: lesson
---

# Lesson 42. Cancellation

**Mission link:** A slow request eventually gets cancelled by something: a client giving up, a load balancer's own timeout, an operator restarting the process, and the only mechanism a future has for that is being dropped mid-poll, with no chance to run one more line or log one more message. Code that assumes it will always reach its own cleanup line is code that has never met a real deadline.
**Primary source:** [tokio::time::timeout](https://docs.rs/tokio/1.53.1/tokio/time/fn.timeout.html)
**Prerequisites:** [Lesson 1](0001-ownership-and-drop.md), [Lesson 39](0039-tasks-and-the-send-bound.md)

## Warm-up

1. ▢ Lesson 1 fixed the rule that a scope's locals drop in reverse declaration order once the scope ends, whether by returning normally or by a panic unwinding through it. An `async fn`'s body is ordinary code with `.await` points scattered through it. Guess: if the task running that body stops partway, rather than returning, what happens to a local variable alive at that point?

<details markdown="1"><summary>Check</summary>

It is still dropped, in the order lesson 1 already fixed. Stopping a future partway is not a special case; it runs the same destructors any other scope exit would, wherever execution happened to be paused.

</details>

2. ▢ Lesson 39 established that `tokio::spawn` hands a future to the runtime, which starts running it as its own independent unit, and that this is exactly why the future must satisfy the `Send` bound: the runtime is free to move it between worker threads. If you spawn a task and let its `JoinHandle` fall out of scope without awaiting or aborting it, guess what happens to the task.

<details markdown="1"><summary>Check</summary>

It keeps running. Spawning already handed the future to the runtime; the handle only observes or affects it afterwards, so losing the handle does not undo that hand-off.

</details>

## Know this

### Cancelling a future is dropping it, and nothing else

tokio gives cancellation no dedicated syntax, no exception type and no message a future can inspect. A cancelled future is a dropped future, in lesson 1's sense: its destructor runs, and that is the whole event. `timeout`'s documentation says so directly: "Cancelling a timeout is done by dropping the future. No additional cleanup or other work is required."

```rust
use tokio::time::{sleep, timeout, Duration};

struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) {
        println!("dropped {}", self.0);
    }
}

async fn half_finished() {
    let _guard = Noisy("work in progress");
    println!("started");
    sleep(Duration::from_millis(500)).await;
    println!("finished, never reached");
}

#[tokio::main]
async fn main() {
    let outcome = timeout(Duration::from_millis(50), half_finished()).await;
    println!("{outcome:?}");
}
```

Five of five runs printed the same three lines, in order: `started`, then `dropped work in progress`, then `Err(Elapsed(()))`. `finished, never reached` never printed: the `sleep` inside `half_finished` never returned, because `timeout` dropped the future once its deadline passed, taking `Noisy`'s destructor with it.

### What that means for the code inside

A future compiles to a state machine suspended only at an `.await`, never at an arbitrary instruction. Dropping it while suspended runs the destructors of whatever locals that state holds, in lesson 1's reverse declaration order, and nothing else executes: code between the last completed `.await` and the next one simply never runs, not skipped, just never reached. `Noisy`'s destructor ran above because `_guard` was declared before the cancelled `.await`; declared after it, there would be no value yet to drop. A `MutexGuard` held across a cancelled `.await` is released the same way, as an ordinary local; lesson 41 covers whether it should have been alive there at all.

### select! cancels the losers, every time it runs

`tokio::select!`'s description says it directly: "Waits on multiple concurrent branches, returning when the first branch completes, cancelling the remaining branches." Cancelling here is the drop above, applied to whichever futures did not win.

```rust
use tokio::time::{sleep, Duration};

struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) {
        println!("dropped {}", self.0);
    }
}

#[tokio::main]
async fn main() {
    let fast = async {
        sleep(Duration::from_millis(20)).await;
        "fast"
    };
    let slow = async {
        let _guard = Noisy("loser's local");
        sleep(Duration::from_millis(300)).await;
        "slow"
    };
    let winner = tokio::select! {
        r = fast => r,
        r = slow => r,
    };
    println!("winner: {winner}");
}
```

Five of five runs printed `dropped loser's local` before `winner: fast`: the losing branch's destructor ran as part of `select!` dropping it, before the surrounding code even saw the winner's value. This repeats on every iteration of a `select!` loop, dropping whichever branches did not complete that round, the fact lesson 43 is entirely about. Nothing here says whether dropping a given branch mid-flight is safe.

### The three ways a future gets cancelled in practice

Only three events do this to code you write: a `timeout` elapsing, shown above; a `select!` branch losing, also shown above; and a spawned task's `JoinHandle::abort`, which asks the runtime to drop the task's future instead:

```rust
use tokio::time::{sleep, Duration};

struct Noisy;
impl Drop for Noisy {
    fn drop(&mut self) {
        println!("dropped noisy local inside aborted task");
    }
}

#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        let _guard = Noisy;
        println!("task started");
        sleep(Duration::from_millis(500)).await;
        println!("task finished, never reached");
    });

    sleep(Duration::from_millis(20)).await;
    handle.abort();

    let outcome = handle.await;
    println!("outcome is_err: {}", outcome.is_err());
    if let Err(join_err) = outcome {
        println!("join_err.is_cancelled(): {}", join_err.is_cancelled());
    }
}
```

Five of five runs printed `task started`, then `dropped noisy local inside aborted task`, then `outcome is_err: true`, then `join_err.is_cancelled(): true`. `abort` does not force the drop instantly; the module documentation says exactly when: "the task is signalled to shut down next time it yields at an .await point", and "When tasks are shut down, it will stop running at whichever .await it has yielded at. All local variables are destroyed by running their destructor." A task blocked inside `spawn_blocking` cannot be reached this way, lesson 40's uninterruptible case by name: "Be aware that tasks spawned using spawn_blocking cannot be aborted because they are not async. If you call abort on a spawn_blocking task, then this will not have any effect, and the task will continue running normally."

### Dropping a JoinHandle does not cancel the task

Throwing away the handle looks like a fourth way to cancel, and is exactly the case that is not. `JoinHandle`'s documentation is direct: "A JoinHandle detaches the associated task when it is dropped, which means that there is no longer any handle to the task, and no way to join on it." Separately: "If a JoinHandle is dropped, then the task continues running in the background and its return value is lost." The task keeps going; only the ability to observe or stop it later is gone.

```rust
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let ticks = Arc::new(AtomicUsize::new(0));
    let ticks_task = Arc::clone(&ticks);

    let handle = tokio::spawn(async move {
        for _ in 0..5 {
            sleep(Duration::from_millis(20)).await;
            ticks_task.fetch_add(1, Ordering::SeqCst);
        }
    });

    drop(handle);
    println!("handle dropped, task not awaited or aborted");

    sleep(Duration::from_millis(150)).await;
    println!("ticks after dropping the handle: {}", ticks.load(Ordering::SeqCst));
}
```

Five of five runs printed `handle dropped, task not awaited or aborted` followed by `ticks after dropping the handle: 5`: the task ran to completion on its own, unaffected by the handle's drop. A bare future the runtime has never seen behaves nothing like this; constructing an `async` block and dropping it again without awaiting, spawning or polling it runs none of its body:

```rust
struct Noisy;
impl Drop for Noisy {
    fn drop(&mut self) {
        println!("dropped noisy local");
    }
}

#[tokio::main]
async fn main() {
    let fut = async {
        let _guard = Noisy;
        println!("this line never runs, because the future is never polled");
    };
    println!("created the future, about to drop it unpolled");
    drop(fut);
    println!("dropped the unpolled future; nothing above printed the guard's destructor");
}
```

Five of five runs printed only the two `println!`s either side of the `drop`; `_guard` never appeared, because it was never created. A future does nothing until something polls it, so dropping one before that first poll loses nothing, in sharp contrast to the spawned task above, already running the moment `tokio::spawn` returned.

### What to do about it

None of this is fixed by writing more careful code at the one line that gets cancelled: any `.await` is a candidate, and cancellation is neither rare nor announced. The design that survives treats being stopped between two `.await` points as a resumable state, not a failure to guard against at one site. Concretely: put nothing irreversible, a write that cannot be undone, a count that cannot be taken back, between two `.await` points, so whichever one a drop lands on leaves nothing half-done. Where an invariant needs restoring regardless, a guard is the tool: a value whose only job is a `Drop` that puts things back, which works because dropping is the one event cancellation always triggers. tokio_util's `CancellationToken` is the usual next step once a single future cannot signal a cooperative wind-down across several tasks, but that crate is not part of this stage.

## Practice

1. ▢ Predict what this prints, then compile and run it.

   ```rust
   use tokio::time::{sleep, timeout, Duration};

   struct Noisy;
   impl Drop for Noisy {
       fn drop(&mut self) {
           println!("dropped");
       }
   }

   async fn work() {
       println!("before the await");
       sleep(Duration::from_millis(200)).await;
       let _guard = Noisy;
       println!("after the await, never reached");
   }

   #[tokio::main]
   async fn main() {
       let outcome = timeout(Duration::from_millis(30), work()).await;
       println!("{outcome:?}");
   }
   ```

<details markdown="1"><summary>Check</summary>

Five of five runs printed `before the await`, then `Err(Elapsed(()))`, with no `dropped` line: `_guard` is declared after the cancelled `.await`, so the future drops before that line runs and no `Noisy` value exists yet.

</details>

2. ▢ Predict what this prints, then compile and run it.

   ```rust
   use tokio::time::{sleep, timeout, Duration};

   async fn steps() {
       println!("step 0");
       sleep(Duration::from_millis(20)).await;
       println!("step 1");
       sleep(Duration::from_millis(20)).await;
       println!("step 2");
       sleep(Duration::from_millis(20)).await;
       println!("step 3, never reached");
   }

   #[tokio::main]
   async fn main() {
       let outcome = timeout(Duration::from_millis(45), steps()).await;
       println!("{outcome:?}");
   }
   ```

<details markdown="1"><summary>Check</summary>

Five of five runs printed `step 0`, `step 1`, `step 2`, then `Err(Elapsed(()))`: the first two sleeps finish inside the budget, but the third is still in progress when the timeout elapses, dropping the future there before `step 3` prints.

</details>

3. ▢ A task sleeps ten milliseconds then returns `"done"`. The caller sleeps a hundred milliseconds before calling `abort` and awaiting the handle. Predict the result, then run it.

<details markdown="1"><summary>Check</summary>

Five of five runs printed `outcome: Ok("done")`: the task had already finished well before `abort` was called, so there is nothing left to shut down, and the documentation is explicit that aborting does not guarantee a cancelled error if the task already completed.

</details>

4. ▢ A task increments an atomic counter five times, twenty milliseconds apart. The caller spawns it, drops the `JoinHandle` immediately, and reads the counter on the next line before `main` returns. Predict what it reads, then run it.

<details markdown="1"><summary>Check</summary>

Five of five runs printed `0`: the task has had no time for even one iteration, and `main` returning at once then drops the whole runtime, which the module documentation says immediately cancels all tasks on it, unlike the earlier example where `main` stayed alive long enough for the task to finish.

</details>

5. ▢ A judgement call, not a compile check: for each function, say whether it is already safe to cancel as written, or needs a guard restoring an invariant on drop.

   - a) Increments a counter, awaits a network call, then decrements the counter to mark it finished.
   - b) Reads a whole buffer with one non-blocking call and has no other `.await` in the function.
   - c) Writes a "job started" record, awaits the job, writes "job finished" once it returns, and a report assumes every started job also finished.

<details markdown="1"><summary>Check</summary>

a) Needs a guard: cancellation between increment and decrement leaves the counter too high, so the decrement belongs in a value created right after the increment, its `Drop` running it regardless of how the function ends. b) Already safe: no `.await` sits between starting and finishing the read, so a cancellation either never starts the work or has nothing left to interrupt. c) Needs a guard too: the "started" write sits before an `.await`, leaving an entry the "finished" write will never balance, exactly what this lesson's design rule warns against.

</details>

## Real-world reps

- [ ] Give each source in your project's async summariser a `tokio::time::timeout`, run it with one source made deliberately slow, and write down what the cancelled read left behind: what was collected, what was lost, and whether anything recorded the cut-off.
- [ ] Find one `.await` in code you have already written with a `Drop` value alive on one side of it, and write one sentence on what state its owner would be left in if the future were dropped at that exact point.
- [ ] Tomorrow: pick one function you wrote today that does something irreversible, and check whether an `.await` sits close enough beside it that a cancellation there leaves the irreversible part done with nothing else.

## Going further

- [tokio::task::JoinHandle](https://docs.rs/tokio/1.53.1/tokio/task/struct.JoinHandle.html): `abort` in full, and what dropping the handle leaves behind
- [tokio::select!](https://docs.rs/tokio/1.53.1/tokio/macro.select.html): the macro's complete lifecycle and fairness rules
- [tokio::task](https://docs.rs/tokio/1.53.1/tokio/task/index.html): the module's cancellation section, covering abort and spawn_blocking together
- [Select](https://tokio.rs/tokio/tutorial/select): the tutorial chapter that builds a select! loop end to end
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
