---
title: 35. Channels
description: Sending values between threads instead of sharing them, and what the ends of a channel do when the other end goes away
type: lesson
---

# Lesson 35. Channels

**Mission link:** A channel is the right tool exactly where lesson 33's shared state is the wrong one, a pipeline where each item is owned by one worker at a time, and misreading the two ends' failure modes is how a review finds a program that quietly drops work or hangs on a message nobody will send.
**Primary source:** [std::sync::mpsc](https://doc.rust-lang.org/std/sync/mpsc/index.html)
**Prerequisites:** [Lesson 29](0029-threads-joining-and-panics.md), [Lesson 33](0033-mutex-rwlock-and-poisoning.md)

## Warm-up

1. ▢ Lesson 29 established that a value moved into a `thread::spawn` closure must satisfy `'static` because the closure might outlive its caller. If a thread needs to hand an owned `String` to another thread once done with it, what does the sending side give up to make that happen?

<details markdown="1"><summary>Check</summary>

It moves the value in and stops using it: the closure is bound by `F: Send + 'static`, so it takes ownership rather than borrowing, and cannot touch the value again afterwards. Handing a value off and keeping a usable copy are not both available at once.

</details>

2. ▢ Lesson 33 showed that a `Mutex<T>` guards one shared copy every thread locks before touching, and a thread panicking while holding the lock poisons it for every thread after. What would have to be true of a design for two threads to never contend for the same lock, rather than just surviving the poisoning if they do?

<details markdown="1"><summary>Check</summary>

The threads cannot share the same value: each needs its own copy, or a value handed off so exactly one thread owns it at a time. That handoff, rather than shared access guarded by a lock, is the shape this lesson's tool is built for.

</details>

## Know this

### Moving ownership instead of sharing access

`mpsc::channel` returns a `(Sender<T>, Receiver<T>)` pair connected to one queue. `send` moves a `T` in and `recv` moves it back out, so at every moment a value has exactly one owner: the sender, the queue, or the receiver. Nothing is locked, because no two threads ever touch the same value at once. A `Sender` clones so several threads can produce into the same queue, the "multi-producer" half; a `Receiver` cannot clone, the "single-consumer" half, covered later. Iterating a `Receiver` in a `for` loop calls `recv` repeatedly until nothing is left to receive and nothing left could send more.

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    for id in 0..4 {
        let tx = tx.clone();
        thread::spawn(move || {
            tx.send(id * 10).unwrap();
        });
    }
    drop(tx);

    let mut received: Vec<i32> = Vec::new();
    for value in rx {
        received.push(value);
    }
    println!("{:?}", received);
}
```

All twenty runs produced the same four values, but the arrival order varied: twelve of twenty printed `[0, 10, 20, 30]`, matching spawn order, and eight printed a different order such as `[0, 20, 10, 30]`, since nothing promises which producer's message the queue hands out first when more than one is ready. Code that depends on producer order needs to attach an index and sort or match on it afterwards, not assume the schedule. `drop(tx)` matters here; leaving it out is the trap the next section covers. A value crossing a thread boundary must satisfy `Send` (lesson 34), and `Sender<T>` is itself `Send` only when `T: Send`, so a type that cannot cross threads is rejected at the `send` call, not only inside `thread::spawn`.

### What the ends do when the other one goes away

A channel has two ends, and each one's failure is a plain `Result`, not a panic. Sending into a channel whose `Receiver` is already dropped returns an error rather than sending into nothing:

```rust
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::channel::<i32>();
    drop(rx);
    println!("{:?}", tx.send(1));
}
```

This printed `Err(SendError { .. })` in three of three runs; the `Debug` implementation for `SendError` hides the value rather than showing it. Receiving once every `Sender` (the original and every clone) has been dropped fails the same way, in the other direction:

```rust
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::channel::<i32>();
    drop(tx);
    println!("{:?}", rx.recv());
}
```

This printed `Err(RecvError)` in three of three runs. The `Sender` documentation states the rule plainly: "all senders (the original and its clones) need to be dropped for the receiver to stop blocking to receive messages with `Receiver::recv`". A `for` loop over a `Receiver` ends the same way, once every sender is gone:

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        for i in 0..3 {
            tx.send(i).unwrap();
        }
    });

    let mut count = 0;
    for _value in rx {
        count += 1;
    }
    println!("loop ended after {count} values");
}
```

This printed `loop ended after 3 values` in three of three runs: the spawned thread's `tx` is dropped when the closure returns, that was the last sender, and the loop's implicit `recv` calls start failing.

### The trap: a live `Sender` means the loop never ends

The same rule cuts the other way if a clone of the `Sender` stays reachable somewhere the loop cannot see. Cloning `tx` for a worker but keeping the original `tx` alive in the surrounding scope leaves one sender that is never dropped:

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    let worker_tx = tx.clone();
    thread::spawn(move || {
        for i in 0..3 {
            worker_tx.send(i).unwrap();
        }
    });

    let mut count = 0;
    for value in rx {
        println!("got {value}");
        count += 1;
    }
    println!("loop ended after {count} values");
}
```

Under a six-second watchdog, this hung in three of three attempts, always after printing the three values sent and never printing the final line: no panic, no error, nothing more, since the program never reaches a state where `recv` can return `Err`. The fix is dropping the extra sender once it is no longer needed, not sending a sentinel value the receiver has to recognise:

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    let worker_tx = tx.clone();
    thread::spawn(move || {
        for i in 0..3 {
            worker_tx.send(i).unwrap();
        }
    });
    drop(tx);

    let mut count = 0;
    for value in rx {
        println!("got {value}");
        count += 1;
    }
    println!("loop ended after {count} values");
}
```

With that one line added, the same loop completed and printed `loop ended after 3 values` in three of three runs. A sentinel message only works if every consumer agrees to look for it and no ordinary value could collide with it; dropping the sender is a fact the channel itself already checks, for free.

### `sync_channel` and backpressure

`mpsc::channel` is unbounded: `send` never blocks, and a slow consumer lets the queue grow without limit. `mpsc::sync_channel(n)` gives the queue a fixed capacity, and `send` blocks once full until the receiver makes room, a design tool for pacing a fast producer against a slow consumer, not a limitation. To observe the block rather than time it: a channel of capacity one already holds one value, and a second `send` on another thread gets a short sleep's head start to reach its blocking call first, purely to bias scheduling.

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = mpsc::sync_channel(1);
    tx.send(1).unwrap();
    let handle = thread::spawn(move || {
        println!("about to block, channel is full");
        tx.send(2).unwrap();
        println!("unblocked, after the receiver made room");
    });
    thread::sleep(Duration::from_millis(500));
    rx.recv().unwrap();
    handle.join().unwrap();
    rx.recv().unwrap();
}
```

In three of three runs, "unblocked, after the receiver made room" printed only after the main thread's `recv` call, never before: the second `send` cannot return until the buffer has space, and the buffer only gets space when something receives, so that order is guaranteed by the channel, not the sleep. `try_send` and `try_recv` are the non-blocking forms, returning immediately instead of waiting:

```rust
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::sync_channel(1);
    tx.send(1).unwrap();
    println!("{:?}", tx.try_send(2));
    println!("{:?}", rx.try_recv());
    println!("{:?}", rx.try_recv());
}
```

This printed `Err(TrySendError::Full(..))` for the send into a full channel, then `Ok(1)` for a `try_recv` that took the one value waiting, then `Err(Empty)` for a `try_recv` with nothing left and the sender still alive, in three of three runs.

### The one place a crate is genuinely needed

Every type above is single-consumer: `Receiver` has no `clone`, and moving one into two threads is rejected at compile time. The standard library has an `mpmc` module for multiple consumers, but it is not stable:

```text
error[E0658]: use of unstable library feature `mpmc_channel`
 --> src/main.rs:2:22
  |
2 |     let (_tx, _rx) = std::sync::mpmc::channel::<i32>();
  |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: see issue #126840 <https://github.com/rust-lang/rust/issues/126840> for more information
```

So on stable Rust, multiple consumers means one of two things: one consumer reading a single `Receiver` and handing work to others by whatever means fits, or a crate providing a multi-consumer channel outright. Neither is named here; both are lesson 36's territory.

### The honest comparison with a lock

A channel and a `Mutex` solve the same problem by opposite means. A channel moves ownership: a value has one owner at a time, work is serialised through the consumer that reads the queue, and there is nothing to lock because no two threads ever hold the same value at once. A lock keeps one shared copy every thread reaches through the same guard, letting any thread read or write it at any point rather than only the one currently holding it. A pipeline, where each item is produced once, processed once and discarded, fits a channel: the handoff matches the shape of the work. A structure several threads must consult and update in no particular order, such as a running total or a shared cache, fits a lock instead, since forcing that through one consumer would only add a queue between threads that all genuinely need the same value: choose from that shape, not from habit. Release 1.67.0 replaced `std::sync::mpsc`'s own implementation with `crossbeam-channel`'s, unchanged API, so a program written against plain `std` already runs on that design.

## Practice

1. ▢ Predict whether `rx.clone()` compiles for a `Receiver<i32>`, and if not, which error code names the problem.

<details markdown="1"><summary>Check</summary>

It does not compile: `E0599`, no method named `clone` found. `Receiver` deliberately has no `Clone`, since cloning it would let two consumers race for the same messages, exactly the gap `mpmc` fills once stable.

</details>

2. ▢ Predict the error code for moving the same `rx` into two separate `thread::spawn` closures, one after the other.

<details markdown="1"><summary>Hint</summary>

`Receiver` is not `Copy`, and a `move` closure takes ownership of what it captures.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0382`, use of a moved value: the first closure moves `rx` in, and the second's capture uses a binding that no longer owns anything. A single `Receiver` can only ever belong to one place.

</details>

3. ▢ For a channel whose `Sender` is alive but has sent nothing yet, predict which `TryRecvError` variant `try_recv` returns, then predict the variant once every `Sender` is dropped, and compile both to check.

<details markdown="1"><summary>Check</summary>

`Empty` while a sender remains, since a message could still arrive; `Disconnected` once every sender is gone. Running each case confirms `Err(Empty)` and `Err(Disconnected)`.

</details>

4. ▢ Take the "trap" example, keep the clone but comment out `drop(tx)`, and run it under a timeout of your choosing. Predict the last line printed.

<details markdown="1"><summary>Hint</summary>

The loop's `recv` calls only fail once every sender, including the one your surrounding code still holds, is gone.

</details>

<details markdown="1"><summary>Check</summary>

There is no last line: the loop never ends, since `tx` is still alive in scope even though the worker's clone finished sending. It has to be interrupted, not waited out.

</details>

5. ▢ `sync_channel`'s documentation notes that a bound of `0` makes a "rendezvous" channel. Predict whether `tx.send(value)` can return before some thread calls `recv`, then compile a spawned sender against a receiving main thread to check.

<details markdown="1"><summary>Check</summary>

It cannot: with no buffer, a `send` on a bound-`0` channel only returns once a receiver takes the value directly, confirmed by the sender's "returned" message printing only after the receiver's `recv` call.

</details>

## Real-world reps

- [ ] Change your project's summary type so each worker sends its own partial summary down a channel once it finishes a file, instead of returning it from `join` for the main thread to collect afterwards.
- [ ] Fold the partial summaries into one total by iterating the `Receiver` on the main thread, dropping every worker's `Sender` clone once spawned so the loop ends once every file has reported in.
- [ ] Tomorrow: compare this against lesson 33's mutex-based version in two sentences: which you would ship, and what the channel version made easier or harder than locking one shared summary.

## Going further

- [Transfer Data Between Threads with Message Passing](https://doc.rust-lang.org/book/ch16-02-message-passing.html): the Book's introduction to the same model
- [std::sync::mpsc::sync_channel](https://doc.rust-lang.org/std/sync/mpsc/fn.sync_channel.html): the API reference for the bounded flavour, including the bound-0 rendezvous case
- [E0658](https://doc.rust-lang.org/error_codes/E0658.html): the diagnostic for using a library feature the standard library has not yet stabilised
- [Announcing Rust 1.67.0](https://blog.rust-lang.org/2023/01/26/Rust-1.67.0.html): the release that replaced `std::sync::mpsc`'s implementation with `crossbeam-channel`'s
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
