---
title: 41. Shared State Across an Await
description: Why a lock guard held across an await point is refused, and how to choose between the two kinds of mutex
type: lesson
---

# Lesson 41. Shared State Across an Await

**Mission link:** A guard that is ordinary in a scoped thread becomes a compile error once it survives an await inside a spawned task, and reaching for tokio's own mutex to silence that error is sometimes right and often just slower for no reason. Knowing which is which keeps a shared accumulator fast rather than merely quiet.
**Primary source:** [tokio::sync::Mutex](https://docs.rs/tokio/1.53.1/tokio/sync/struct.Mutex.html)
**Prerequisites:** [Lesson 33](0033-mutex-rwlock-and-poisoning.md), [Lesson 39](0039-tasks-and-the-send-bound.md)

## Warm-up

1. ▢ Lesson 33 made a guard's scope the whole design decision: a guard held past its mutation makes everything else done while holding it something every other thread waits for. What did dropping the guard earlier buy, without changing what it protected?

<details markdown="1"><summary>Check</summary>

Only how long the guard stayed alive changed, not the data. Dropped before the unrelated work started, another thread's `lock` could return once the mutation finished, instead of waiting for that work too. A guard's scope, not the mutex's existence, is the boundary of what gets serialised.

</details>

2. ▢ Lesson 39 said a future handed to `tokio::spawn` must satisfy `Future + Send + 'static`, since the executor may move it to another worker. Lesson 34 named a type that is `Sync` but not `Send`. Which type, and what does that split mean for one sitting inside a future?

<details markdown="1"><summary>Check</summary>

`std::sync::MutexGuard`. `Sync` says a `&MutexGuard` may be shared between threads; `Send` says the guard itself may move to another thread. It has the first without the second, so a future holding one cannot move to a different worker, exactly what `tokio::spawn`'s bound catches.

</details>

## Know this

### The diagnostic: a guard that survives an await cannot be spawned

A task that locks a standard-library `Mutex`, awaits something, and only then finishes with the guard looks harmless:

```rust
use std::sync::{Arc, Mutex};
use tokio::time::{sleep, Duration};

async fn touch(state: Arc<Mutex<u32>>) {
    let mut guard = state.lock().unwrap();
    sleep(Duration::from_millis(10)).await;
    *guard += 1;
}

#[tokio::main]
async fn main() {
    let state = Arc::new(Mutex::new(0));
    tokio::spawn(touch(Arc::clone(&state))).await.unwrap();
    println!("{}", *state.lock().unwrap());
}
```

Handing that future to `tokio::spawn` refuses to compile:

```text
error: future cannot be sent between threads safely
   --> src/bin/lockacross.rs:13:18
    |
 13 |     tokio::spawn(touch(Arc::clone(&state))).await.unwrap();
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^ future returned by `touch` is not `Send`
    |
    = help: within `impl Future<Output = ()>`, the trait `Send` is not implemented for `std::sync::MutexGuard<'_, u32>`
note: future is not `Send` as this value is used across an await
   --> src/bin/lockacross.rs:6:38
    |
  5 |     let mut guard = state.lock().unwrap();
    |         --------- has type `std::sync::MutexGuard<'_, u32>` which is not `Send`
  6 |     sleep(Duration::from_millis(10)).await;
    |                                      ^^^^^ await occurs here, with `mut guard` maybe used later
note: required by a bound in `tokio::spawn`
```

The note went on to quote the exact line and file of tokio's own source inside a registry path on disk; trimmed here, since an absolute path into the runtime's crate is no more portable than one in a home directory. What is left is enough: `async fn touch` compiles to a state machine whose locals become fields, so a `guard` still alive at the `.await` becomes a field, and the whole future inherits whatever traits that field lacks. Lesson 34 established `MutexGuard` as `Sync` but not `Send`; lesson 39's bound on `spawn` demands `Send`. Nothing new is happening, it is stage 5's own rule arriving at a suspension point instead of a thread boundary.

### The fix that is usually right: end the critical section before the await

The guard only needs to exist for the increment, not for the sleep after it, so give it a block of its own:

```rust
async fn touch(state: Arc<Mutex<u32>>) {
    {
        let mut guard = state.lock().unwrap();
        *guard += 1;
    }
    sleep(Duration::from_millis(10)).await;
}
```

Spawning this compiles and printed `1`. The mutex did not change; the guard's scope did, exactly lesson 33's conclusion about a held-too-long guard, now applied to a suspension point rather than unrelated work on another thread. Narrowing where a guard lives removes the problem instead of working around it.

### tokio::sync::Mutex, and what it is actually for

Sometimes the critical section genuinely needs to await something, a write to a shared file handle that must finish before another task writes to it. Tokio's own `Mutex` is for that: its `lock` is `pub async fn lock(&self) -> MutexGuard<'_, T>`, async rather than blocking, returning a `Send` guard. The code that failed above compiles unchanged once both the mutex and the guard are tokio's:

```rust
use tokio::sync::Mutex;

async fn touch(state: Arc<Mutex<u32>>) {
    let mut guard = state.lock().await;
    sleep(Duration::from_millis(10)).await;
    *guard += 1;
}
```

Spawned exactly as before, this compiles and printed `1`. The primary source is direct about when to reach for it over the standard library's: "Contrary to popular belief, it is ok and often preferred to use the ordinary Mutex from the standard library in asynchronous code. The feature that the async mutex offers over the blocking mutex is the ability to keep it locked across an .await point. This makes the async mutex more expensive than the blocking mutex, so the blocking mutex should be preferred in the cases where it can be used. The primary use case for the async mutex is to provide shared mutable access to IO resources such as a database connection. If the value behind the mutex is just data, it's usually appropriate to use a blocking mutex such as the one in the standard library or parking_lot." Justified only when the critical section has to contain an await, rarer than the diagnostic above suggests, since its own fix resolves most cases without this type at all.

### The case where the standard library's lock is not merely acceptable but better

A counter bumped once per incoming line, no await anywhere near the lock, is the "just data" case the quotation above names:

```rust
use std::sync::{Arc, Mutex};

async fn bump(counter: Arc<Mutex<u32>>) {
    let mut guard = counter.lock().unwrap();
    *guard += 1;
}
```

Spawned eight times and joined, this printed `8`, and the same program written against `tokio::sync::Mutex` also printed `8`: both correct. The difference is what each pays. `tokio::sync::Mutex::lock` is async, so every call goes through `.await` and gives the executor a point at which it could suspend the task, even though nothing here has anything to wait for; the standard library's `lock` is an ordinary call that returns once the almost always uncontended lock is free. Reaching for the async mutex here buys a suspension point with no use for it, at the cost the primary source already named.

### RwLock and the other async primitives, named and bounded

Tokio's `sync` module has more than one lock. [`tokio::sync::RwLock`](https://docs.rs/tokio/1.53.1/tokio/sync/struct.RwLock.html) is `Mutex`'s many-readers-or-one-writer counterpart, chosen by the same ratio argument lesson 33 gave, with `read` and `write` as async methods whose guards can likewise cross an await. [`tokio::sync::Semaphore`](https://docs.rs/tokio/1.53.1/tokio/sync/struct.Semaphore.html) hands out a fixed number of permits asynchronously, bounding how many tasks use a resource at once rather than protecting one value. [`tokio::sync::Notify`](https://docs.rs/tokio/1.53.1/tokio/sync/struct.Notify.html) is a bare wake-up signal with no payload, for telling one waiting task something happened. [`tokio::sync::oneshot`](https://docs.rs/tokio/1.53.1/tokio/sync/oneshot/index.html) is a channel sized for exactly one value, from one task to another. None of their APIs belong here; they exist so a reader who meets one elsewhere recognises it.

### What poisoning does here

The standard library's `Mutex::lock` returns `Result<MutexGuard<'_, T>, PoisonError<...>>`, because a panic while holding the guard leaves the data's invariant in doubt. Tokio's `lock` returns `MutexGuard<'_, T>` directly, no `Result`, no `Err` case, because the type has no poisoning to report. A task that pushes onto a shared `Vec` behind a `tokio::sync::Mutex` then panics while still holding the guard confirmed this across three runs: each printed the panic message, and the next `lock().await` succeeded immediately, still showing the pushed value, with no flag that a task had died mid-update. Lesson 33's argument for poisoning was that a bare `.unwrap()` on `lock` asserts something about the whole program's history, not just the call site; that has nothing to attach to here, since there is no `Result` to unwrap. Choosing tokio's mutex is also choosing to give up that signal, silently, one more reason to prefer the standard library's lock wherever the critical section allows it. What a cancelled task holding either guard leaves behind is lesson 42's subject.

## Practice

1. ▢ The diagnostic's `touch` is awaited directly in `main`, not passed to `tokio::spawn`. Predict whether this compiles, then try it.

<details markdown="1"><summary>Hint</summary>

The `Send` bound above belonged to `tokio::spawn`'s signature specifically. Does anything move to another thread if nothing is spawned?

</details>

<details markdown="1"><summary>Check</summary>

It compiles and prints `1`. Awaiting a future in place never asks it to leave the current task, so `Send` is never checked; the bound only bites where something is spawned, which is why the same shape is fine in one line and refused in the next.

</details>

2. ▢ In the diagnostic's spawned version, replace `std::sync::Mutex` with `tokio::sync::Mutex`, keeping the guard held across the same `sleep(...).await`. Predict whether this compiles, then run it.

<details markdown="1"><summary>Check</summary>

It compiles and prints `1`. `tokio::sync::MutexGuard` is `Send`, so a future holding one across an await carries no field the executor cannot move, and `tokio::spawn`'s bound is satisfied.

</details>

3. ▢ Take the eight-task counter from "the standard library's lock is not merely acceptable but better" and change only the mutex to `tokio::sync::Mutex`. Predict what it prints, then run it, then say whether this version is wrong.

<details markdown="1"><summary>Check</summary>

It prints `8`, same as before: correctness is unchanged. Not wrong, only worse than it needs to be, since the critical section has no await and the async mutex adds a suspension point that buys nothing.

</details>

4. ▢ After the panicking task in "what poisoning does here" finishes, predict what type `data.lock().await` produces next, and whether anything needs matching or unwrapping first.

<details markdown="1"><summary>Hint</summary>

Compare `tokio::sync::Mutex::lock`'s signature to `std::sync::Mutex::lock`'s from lesson 33.

</details>

<details markdown="1"><summary>Check</summary>

It produces a `MutexGuard<'_, Vec<i32>>` directly, nothing to match or unwrap, since `tokio::sync::Mutex::lock` returns the guard rather than a `Result`. There is no poisoned state for the panic to have left behind at the type level.

</details>

5. ▢ For each shared value, say which mutex fits and what decided it: a) a request counter bumped once per parsed line, nothing further to await; b) a cache whose refill is an awaited network call, where a second task wanting the same key should wait on that fetch rather than start its own; c) a log handle wrapped so the disk write itself is awaited while the lock is held.

<details markdown="1"><summary>Check</summary>

a) `std::sync::Mutex`: a plain increment, nothing to await inside it. b) `tokio::sync::Mutex`: the critical section's own await, the refill, is why the second task should queue behind the first rather than duplicate the fetch. c) `tokio::sync::Mutex`: the awaited write is inside the critical section by design, so the guard must survive it.

</details>

## Real-world reps

- [ ] Give the async version of your summariser's per-source reading loop a shared category table, counts per line kind, and a shared accumulator, a running total of bytes; implement both, choosing each lock on this lesson's evidence, and confirm the totals match a single-threaded run.
- [ ] Beside that code, write one line per shared value naming which mutex you used and what decided it: an await present or absent in the critical section.
- [ ] Tomorrow: find one `.lock()` call in code you touched today and check whether anything between it and the guard's drop could ever need to await; if not, the standard library's mutex already belongs there.

## Going further

- [tokio::sync::RwLock](https://docs.rs/tokio/1.53.1/tokio/sync/struct.RwLock.html): the async many-readers-or-one-writer lock, with tokio's own fairness policy
- [tokio::sync::Semaphore](https://docs.rs/tokio/1.53.1/tokio/sync/struct.Semaphore.html): asynchronous permit acquisition for bounding concurrent access
- [tokio::sync::Notify](https://docs.rs/tokio/1.53.1/tokio/sync/struct.Notify.html): a payload-free wake-up signal for a single task
- [tokio::sync::oneshot](https://docs.rs/tokio/1.53.1/tokio/sync/oneshot/index.html): a channel sized for exactly one value between two tasks
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
