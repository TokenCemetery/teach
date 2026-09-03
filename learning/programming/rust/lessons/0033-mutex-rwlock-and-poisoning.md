---
title: 33. Mutex, RwLock and Poisoning
description: What a lock actually protects, why the guard's scope is the design decision, and what a panic while holding one leaves behind
type: lesson
---

# Lesson 33. Mutex, RwLock and Poisoning

**Mission link:** Lesson 32 closed by pointing here: the type that does `RefCell`'s job across threads pays for the crossing with an actual lock. Knowing what that lock buys is what separates a program that serialises only what must be serialised from one that serialises everything, and the difference is a single decision about how long a guard stays alive.
**Primary source:** [std::sync::Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
**Prerequisites:** [Lesson 32](0032-interior-mutability.md), [Lesson 31](0031-shared-ownership.md)

## Warm-up

1. ▢ Lesson 32 closed by saying `RefCell`'s borrow counter is not built for two threads at once, and that the type doing its job across threads uses a lock instead. `RefCell` catches a conflict by panicking. What should a lock do differently when a second thread wants access while a first still holds it?

<details markdown="1"><summary>Check</summary>

Wait rather than refuse. Overlapping `RefCell` borrows is always a bug, so panicking is correct; two threads wanting a lock is ordinary, so the second should get its turn once the first is done. Waiting, not a panic, is what a lock adds beyond a borrow counter.

</details>

2. ▢ Lesson 31 charged `Arc` an atomic increment per `clone`, but its `Deref` only ever hands out `&T`. If two threads each hold an `Arc<Vec<i32>>` and both want to push onto it, what has `Arc` made safe, and what has it left unaddressed?

<details markdown="1"><summary>Check</summary>

Only the sharing: the count guarantees the vector is freed exactly once. Mutating through the handle is untouched, since `&Vec<i32>` never yields `&mut Vec<i32>`, so neither thread can push yet, safely or otherwise. Coordinating a write between threads is the gap this lesson closes.

</details>

## Know this

### The data lives inside the lock

Elsewhere, a mutex often stands beside the data it guards, so nothing stops code touching the data and forgetting the lock. Rust's `Mutex<T>` stores the `T` inside itself: "the data can only be accessed through the RAII guards returned from `lock` and `try_lock`, which guarantees that the data is only ever accessed when the mutex is locked," in the standard library's words. `lock` returns `Result<MutexGuard<'_, T>, ...>`, the `Err` case being poisoning, covered below; the guard `Deref`s to `&T` and `&mut T`, and dropping it unlocks.

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0u32));
    thread::scope(|s| {
        for _ in 0..4 {
            let counter = Arc::clone(&counter);
            s.spawn(move || {
                for _ in 0..1000 {
                    *counter.lock().unwrap() += 1;
                }
            });
        }
    });
    println!("{}", *counter.lock().unwrap());
}
```

Four scoped threads add one thousand times each; all ten runs printed `4000`. Each iteration takes the lock once for the whole read-modify-write, leaving nothing for two threads to interleave badly.

### The guard's scope is the whole design decision

A guard held past its mutation makes everything else done while holding it something every other thread waits for. Two threads increment a counter; thread A sleeps, standing in for unrelated work, before dropping its guard:

```rust
fn held_too_long(counter: &Mutex<u32>) {
    thread::scope(|s| {
        s.spawn(|| {
            let mut guard = counter.lock().unwrap();
            *guard += 1;
            thread::sleep(Duration::from_millis(200));
            println!("A: work done, dropping guard");
        });
        thread::sleep(Duration::from_millis(20));
        s.spawn(|| {
            let mut guard = counter.lock().unwrap();
            *guard += 1;
            println!("B: acquired the lock");
        });
    });
}
```

Across three runs, `B: acquired the lock` printed only after `A: work done`, every time. Dropping A's guard before the sleep instead:

```rust
s.spawn(|| {
    { let mut guard = counter.lock().unwrap(); *guard += 1; }
    thread::sleep(Duration::from_millis(200));
    println!("A: work done");
});
```

Across three more runs, `B: acquired the lock` printed before `A: work done`, every time: B now only waits for the increment, and its own unrelated work overlaps A's. Both versions leave the same final count; a guard's scope is the boundary of what the rest of the program queues for, not a style choice.

### Not reentrant: locking twice hangs, it does not error

`lock`'s documentation refuses to commit to one behaviour: "the exact behavior on locking a mutex in the thread which already holds the lock is left unspecified. However, this function will not return on the second call (it might panic or deadlock, for example)." A `Mutex` has no notion of "this thread already owns me," so a second `lock` on the same thread queues as if a stranger asked.

```rust
fn main() {
    let m = Mutex::new(0u32);
    let _outer = m.lock().unwrap();
    println!("locked once, about to lock again on the same thread");
    let _inner = m.lock().unwrap(); // never returns
}
```

Under a six-second watchdog, this hung in three of three attempts: one line printed, then nothing, until the watchdog killed it. The same happens one call away, a guard alive when a method it calls locks the same value again:

```rust
impl Store {
    fn total(&self) -> u32 {
        self.values.lock().unwrap().iter().sum() // &self, looks harmless
    }

    fn push_and_report(&self, value: u32) {
        let mut guard = self.values.lock().unwrap();
        guard.push(value);
        let total = self.total(); // hangs: guard above is still held
        println!("should not get here: {total}");
    }
}
```

`push_and_report` also hung in three of three attempts. `total`'s `&self` signature hides the danger. The fix is always ending the outer borrow before a call that might lock the same value again; std's `Mutex` has no reentrant mode to fall back on.

### RwLock: many readers or one writer, decided by the workload

`RwLock<T>` relaxes `Mutex`'s all-or-nothing exclusion where most access reads: "this type of lock allows a number of readers or at most one writer at any point in time," through separate `read` and `write` methods.

```rust
fn main() {
    let data = RwLock::new(vec![1, 2, 3]);
    thread::scope(|s| {
        for i in 0..3 {
            let data = &data;
            s.spawn(move || {
                let guard = data.read().unwrap();
                println!("reader {i}: sees {:?}", *guard);
                thread::sleep(Duration::from_millis(100));
                println!("reader {i}: releasing");
            });
        }
        thread::sleep(Duration::from_millis(20));
        s.spawn(|| {
            let mut guard = data.write().unwrap();
            guard.push(4);
            println!("writer: wrote {:?}", *guard);
        });
    });
}
```

Across three runs, all three "sees" lines always printed before any "releasing" line, confirming concurrent holding rather than turns, and the writer's line always printed last, after every reader released. `RwLock` is not automatically faster for allowing concurrent readers: every access pays reader-count bookkeeping `Mutex` does not need, and a write-heavy workload gets none of that benefit while still paying the cost, which can leave `RwLock` slower than a plain `Mutex`. The decision comes from the actual read-to-write ratio, not the name.

### Poisoning: what a panic while holding a guard leaves behind

A `Mutex` cannot know whether a panicking thread left its data's invariant intact, so it stops guessing: the moment a thread panics while holding a guard, the mutex is poisoned, and every later `lock` returns `Err`.

```rust
fn main() {
    let mutex = Arc::new(Mutex::new(vec![1, 2, 3]));
    let c_mutex = Arc::clone(&mutex);
    let _ = thread::spawn(move || {
        let mut guard = c_mutex.lock().unwrap();
        guard.push(4);
        panic!("worker invariant broken");
    }).join();

    println!("is_poisoned: {}", mutex.is_poisoned());
    match mutex.lock() {
        Err(err) => println!("lock() Display: {err}"),
        Ok(_) => unreachable!(),
    }
}
```

Across three runs this printed `is_poisoned: true` and `lock() Display: poisoned lock: another task failed inside`, exact wording every time. Poisoning is only advisory: `PoisonError::into_inner` hands back what `lock` would have returned, the guard itself, not a bare copy, so the mutation is visible through it, `[1, 2, 3, 4]` in this run. That guard still holds the lock; keeping it alive and calling `lock` again reproduces the previous section's hang. Once the data is checked, `clear_poison` marks the mutex sound again, `is_poisoned` back to `false`, and the next `lock` succeeds, still seeing `[1, 2, 3, 4]`. `Mutex::clear_poison` and `RwLock::clear_poison` both stabilised in release 1.77.0, confirmed against that release's notes.

### Breaking the `.lock().unwrap()` habit

That `unwrap` asserts something specific: not that this call is fine, but that no thread anywhere in the program's run has ever panicked holding this mutex, a claim about the whole program's history, not something the call site can verify. Lesson 17's question one is instructive: the failure came from another part of the same program, closer to "your own code" than a stranger's bad input, yet this site cannot state the invariant question four asks for, since it does not know what the other thread was doing. A short-lived tool or test, where any panic should end the run, lesson 9's second exception generalised, makes a bare `unwrap` defensible. A long-running server does not get that for free: matching the `Result` and propagating lesson 15's own error type, recovering with `into_inner` when the invariant plainly survives a panic, or calling `clear_poison` after checking, are more honest. Lesson 35 avoids this judgement, giving each piece of data to one worker at a time.

## Practice

1. ▢ Predict what this prints, then compile and run it.

   ```rust
   use std::sync::{Arc, Mutex};
   use std::thread;

   fn main() {
       let total = Arc::new(Mutex::new(0i32));
       thread::scope(|s| {
           for _ in 0..2 {
               let total = Arc::clone(&total);
               s.spawn(move || {
                   for _ in 0..500 {
                       *total.lock().unwrap() += 1;
                   }
               });
           }
       });
       println!("{}", *total.lock().unwrap());
   }
   ```

<details markdown="1"><summary>Check</summary>

It prints `1000`. Each iteration locks, adds one, and drops the guard in the same statement, so the two threads' increments cannot overlap.

</details>

2. ▢ In this lesson's guard-scope example, predict whether `B: acquired the lock` can print before `A: work done` in the held-too-long version, then run both several times to check.

<details markdown="1"><summary>Hint</summary>

Ask what thread B is actually waiting on in each version: the guard's lifetime, or the sleep's.

</details>

<details markdown="1"><summary>Check</summary>

No, not in the held-too-long version: A keeps its guard through the sleep, so B's `lock` cannot return first. In the narrowed version A drops its guard before the sleep starts, so B's line consistently comes first.

</details>

3. ▢ Predict whether this panics immediately, returns an `Err`, or hangs, then run it under a timeout you set yourself.

   ```rust
   use std::sync::Mutex;

   fn main() {
       let m = Mutex::new(0);
       let _first = m.lock().unwrap();
       println!("locked once");
       let _second = m.lock().unwrap();
       println!("locked twice");
   }
   ```

<details markdown="1"><summary>Check</summary>

It hangs: `Mutex` is not reentrant, and the standard library documents the second call as unspecified. On this toolchain it deadlocks, printing `locked once` and then nothing.

</details>

4. ▢ After a panic poisons a `Mutex<Vec<i32>>`, `let recovered = mutex.lock().unwrap_err().into_inner();` runs without panicking. Predict `recovered`'s type, then predict what happens if the next line calls `mutex.lock()` again while `recovered` is still in scope.

<details markdown="1"><summary>Hint</summary>

`Mutex::lock` returns `Result<MutexGuard<'_, T>, PoisonError<MutexGuard<'_, T>>>`. What does `into_inner` hand back from that `Err`?

</details>

<details markdown="1"><summary>Check</summary>

`recovered` is a `MutexGuard`, not a bare `Vec<i32>`, since `into_inner` gives back exactly what a successful `lock` would have. It still holds the mutex, so a second `lock` while it is alive hangs, the same as two ordinary guards from one thread.

</details>

5. ▢ This one is a judgement call, not a compile check. For each `.lock().unwrap()` site, say whether it is defensible as written or should propagate the poisoning instead.

   - a) A one-shot script that counts things behind a shared `Mutex`, prints the result and exits.
   - b) A server's shared request counter, where one bad request should not stop other workers.
   - c) A test that locks a shared fixture set up on another thread.

<details markdown="1"><summary>Check</summary>

a) Defensible: a short tool where any panic is an acceptable reason to stop, lesson 9's second exception, generalised. b) Not defensible: one bad request should not poison a counter every worker needs, so match and recover with `into_inner`. c) Defensible: a test already treats any panic as a failure, lesson 9's third exception.

</details>

## Real-world reps

- [ ] Give your project's file-summarising threads a single `Arc<Mutex<Summary>>` that every worker locks per update, instead of the partial summary each already builds; run it, confirm the totals still match, then put lesson 30's design back, each worker returning its own partial summary with no lock, and write one comment saying which version you would ship and why.
- [ ] For every `.lock().unwrap()` the shared-accumulator version needed, decide with this lesson's procedure whether it was defensible or needed a `match` or a propagated error instead, and keep that note beside the comment above.
- [ ] Tomorrow: pick one guard in code you touched today and check it is dropped before the next line that might lock the same value again.

## Going further

- [std::sync::RwLock](https://doc.rust-lang.org/std/sync/struct.RwLock.html): the reader-writer lock's full API
- [std::sync::PoisonError](https://doc.rust-lang.org/std/sync/struct.PoisonError.html): the error type `lock` returns once poisoned, with `into_inner` and its guard-shaped payload
- [Shared-State Concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html): the Book's chapter introducing `Mutex<T>`
- [Announcing Rust 1.77.0](https://blog.rust-lang.org/2024/03/21/Rust-1.77.0/): the release that stabilised `clear_poison`
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
