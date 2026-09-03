---
title: 29. Threads, Joining and Panics
description: What spawning actually demands of the data you hand it, and what happens to a thread that panics alone
type: lesson
---

# Lesson 29. Threads, Joining and Panics

**Mission link:** Handing a spawned thread the wrong kind of ownership either fails to compile with a complaint that looks unrelated to threading, or compiles and quietly takes data away from a caller who still wanted it, and a summariser that reads several files at once needs that trade settled honestly before it needs speed.
**Primary source:** [std::thread](https://doc.rust-lang.org/std/thread/index.html)
**Prerequisites:** [Lesson 12](0012-iterators-and-closures.md), [Lesson 27](0027-types-that-borrow.md)

## Warm-up

1. ▢ Lesson 12 distinguished `Fn`, `FnMut` and `FnOnce` by what a closure does with what it captures, separately from the `move` keyword, which decides whether a captured variable is owned by the closure or borrowed from its enclosing scope. If a closure only reads a captured `Vec<i32>` by calling `.len()` on it, does adding `move` change which of the three closure traits it implements?

<details markdown="1"><summary>Check</summary>

No: `move` only changes where the captured data lives, not what the closure does with it once captured. A closure that only reads through `.len()` still implements `Fn` whether or not `move` is present; the body's usage decides which trait applies, and `move` decides ownership.

</details>

2. ▢ Lesson 27 distinguished `&'static T`, a reference valid for the whole program, from `T: 'static`, a bound saying `T` carries no borrow shorter than that. Given that distinction, does a `String` built and dropped after three lines satisfy `T: 'static`?

<details markdown="1"><summary>Check</summary>

Yes: `T: 'static` says nothing about how long any one value lives, only that `T`'s own type carries no lifetime parameter shorter than `'static`. A `String` owns its data outright, so it satisfies the bound unconditionally, even though the particular value is created and dropped within a handful of lines.

</details>

## Know this

### Spawning a thread and waiting for it

`thread::spawn` takes a closure, starts it running on a new operating system thread, and hands back a `JoinHandle<T>` immediately, without waiting for that closure to finish. Its signature is `pub fn spawn<F, T>(f: F) -> JoinHandle<T> where F: FnOnce() -> T + Send + 'static, T: Send + 'static`; the `Send` bounds are lesson 34's subject, so treat them for now as a requirement the standard library imposes on anything crossing a thread boundary. The `JoinHandle` is the only way to learn what the thread returned or whether it panicked, through `pub fn join(self) -> Result<T>`, where that `Result` is `Result<T, Box<dyn Any + Send + 'static>>`: `Ok` of the closure's value, or `Err` of whatever a panic handed it.

```rust
use std::thread;

fn main() {
    let first = thread::spawn(|| {
        let mut total = 0;
        for n in 1..=5 {
            total += n;
        }
        total
    });

    let second = thread::spawn(|| {
        let mut total = 0;
        for n in 1..=10 {
            total += n;
        }
        total
    });

    let first_result = first.join();
    let second_result = second.join();

    println!("{first_result:?}");
    println!("{second_result:?}");
}
```

This prints `Ok(15)` and then `Ok(55)`. Both threads run concurrently from the moment each `spawn` call returns; calling `join` on `first` before spawning `second` would only change when the calling thread waits, not whether the two spawned threads overlap, since a `JoinHandle` blocks the caller, not the thread it names.

### The `'static` demand, and what satisfying it costs

That `'static` is the one lesson 27 defined: the closure's type must carry no borrow shorter than the whole program, because the spawned thread might genuinely outlive the function that spawned it, and nothing stops the caller from never calling `join` at all. A closure that borrows a local instead of owning it cannot make that promise:

```rust
use std::thread;

fn main() {
    let lines = vec![String::from("/index 200 1200"), String::from("/login 500 90")];

    let handle = thread::spawn(|| {
        println!("{}", lines.len());
    });

    handle.join().unwrap();
}
```

```text
error[E0373]: closure may outlive the current function, but it borrows `lines`, which is owned by the current function
 --> src/main.rs:6:32
  |
6 |     let handle = thread::spawn(|| {
  |                                ^^ may outlive borrowed value `lines`
7 |         println!("{}", lines.len());
  |                        ----- `lines` is borrowed here
  |
note: function requires argument type to outlive `'static`
 --> src/main.rs:6:18
  |
6 |       let handle = thread::spawn(|| {
  |  __________________^
7 | |         println!("{}", lines.len());
8 | |     });
  | |______^
help: to force the closure to take ownership of `lines` (and any other referenced variables), use the `move` keyword
  |
6 |     let handle = thread::spawn(move || {
  |                                ++++
```

Taking that `help` is not free. Adding `move` makes the closure own `lines` outright, which satisfies `'static` because there is no borrow left to outlive anything, but it also means `lines` is gone from `main` once the closure is built:

```rust
use std::thread;

fn main() {
    let lines = vec![String::from("/index 200 1200"), String::from("/login 500 90")];

    let handle = thread::spawn(move || {
        println!("{}", lines.len());
    });

    handle.join().unwrap();
    println!("{}", lines.len());
}
```

```text
error[E0382]: borrow of moved value: `lines`
  --> src/main.rs:11:20
   |
 4 |     let lines = vec![String::from("/index 200 1200"), String::from("/login 500 90")];
   |         ----- move occurs because `lines` has type `Vec<String>`, which does not implement the `Copy` trait
 6 |     let handle = thread::spawn(move || {
   |                                ------- value moved into closure here
 7 |         println!("{}", lines.len());
   |                        ----- variable moved due to use in closure
...
11 |     println!("{}", lines.len());
   |                    ^^^^^ value borrowed here after move
```

The compiler's own `help` after this, trimmed here, suggests cloning `lines` before the move so both the closure and `main` get a copy; that removes the error but is the workaround, not the fix, since it pays an allocation the data's actual lifetime never demanded. That is the trade this lesson exists to name: `move` buys `'static` by handing over ownership, and the caller pays by losing `lines` for good, even though the thread finishes and is joined well before `main` ends, and the borrow would have been sound the whole time. Lesson 30 removes this demand for exactly this shape of program; nothing here shows how.

### `move` closures capture places, not always whole bindings

Lesson 12's disjoint capture lets a closure capture only the fields it actually uses rather than a whole struct, and that still applies across a thread boundary, but it does not relax the `'static` bound itself. A closure that only reads one field, without `move`, is still borrowing, and the diagnostic now names the field rather than the struct:

```rust
use std::thread;

struct Data {
    first: Vec<i32>,
    second: Vec<i32>,
}

fn main() {
    let data = Data { first: vec![1, 2, 3], second: vec![4, 5, 6] };

    let handle = thread::spawn(|| {
        println!("{:?}", data.first);
    });

    handle.join().unwrap();
    println!("{:?}", data.second);
}
```

```text
error[E0373]: closure may outlive the current function, but it borrows `data.first`, which is owned by the current function
  --> src/main.rs:11:32
   |
11 |     let handle = thread::spawn(|| {
   |                                ^^ may outlive borrowed value `data.first`
12 |         println!("{:?}", data.first);
   |                          ---------- `data.first` is borrowed here
   |
note: function requires argument type to outlive `'static`
  --> src/main.rs:11:18
   |
11 |       let handle = thread::spawn(|| {
   |  __________________^
12 | |         println!("{:?}", data.first);
13 | |     });
   | |______^
help: to force the closure to take ownership of `data.first` (and any other referenced variables), use the `move` keyword
  |
11 |     let handle = thread::spawn(move || {
   |                                ++++
```

The message proves disjoint capture is at work, since it names `data.first` rather than `data`, but a narrower borrow is still a borrow: `'static` does not care how much is borrowed, only whether anything is. `move` remains the only way past it, and it moves just the field the closure touches, which the practice section below is worth working through by hand.

### A panicking thread does not take down its caller

A spawned thread that panics unwinds its own stack, running its own destructors, and then stops; that unwinding does not cross into the thread that spawned it, or into any other thread that happens to be running. What the caller sees is an `Err` from `join`, carrying whatever value was given to `panic!`:

```rust
use std::thread;

fn main() {
    let steady = thread::spawn(|| {
        thread::sleep(std::time::Duration::from_millis(50));
        "steady thread finished"
    });

    let doomed = thread::spawn(|| {
        panic!("could not parse byte count");
    });

    let doomed_result = doomed.join();
    let steady_result = steady.join();

    match doomed_result {
        Ok(value) => println!("doomed returned {value:?}"),
        Err(payload) => {
            if let Some(message) = payload.downcast_ref::<&str>() {
                println!("doomed panicked with: {message}");
            } else {
                println!("doomed panicked with a non-string payload");
            }
        }
    }

    println!("steady returned {steady_result:?}");
}
```

Every run printed the same shape:

```text
thread '<unnamed>' panicked at src/main.rs:10:9:
could not parse byte count
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
doomed panicked with: could not parse byte count
steady returned Ok("steady thread finished")
```

The numeric identifier the runtime prints after the thread's name changes on every run, so it is trimmed above. `doomed`'s panic reached `main` only because `main` chose to call `join` and inspect the `Result`; `steady` was never touched by it, and its own `join` came back `Ok` exactly as if the other thread did not exist. The process kept running and exited normally, since nothing in `main` re-panicked on seeing the `Err`; only an unhandled panic in the main thread itself takes the program down. Lesson 17 already established that `panic = "abort"` skips `Drop` entirely; the narrower point here holds even under the default unwinding strategy, that unwinding simply stops at the boundary of the thread it started in.

### What a thread actually costs

A value returned by `thread::spawn` is a genuine operating system thread with its own stack, not a lightweight thread multiplexed onto fewer real ones; the standard library pools nothing, so every call asks the operating system for one more thread, and a `JoinHandle` dropped without being joined leaves its thread running detached rather than cancelling it. That makes "one thread per unit of work" a decision to justify rather than a default to reach for, since threads beyond what the machine can run at once buy nothing but the overhead of switching between them. `thread::available_parallelism` exists to give a program something to divide work by:

```rust
use std::thread;

fn main() {
    let parallelism = thread::available_parallelism();
    println!("available_parallelism returned Ok: {}", parallelism.is_ok());
}
```

This printed `available_parallelism returned Ok: true`. What it returns on the inside is not printed or quoted here, deliberately: that number belongs to whatever machine runs the code, not to a lesson. Treat the function as a way to ask "how many" before deciding whether a thread per file, per line, or per some other unit is a decision that pays for itself.

## Practice

1. ▢ Predict the error code, then compile this.

   ```rust
   use std::thread;

   fn main() {
       let counts = vec![1u8, 2, 3];
       let handle = thread::spawn(|| counts.iter().sum::<u8>());
       println!("{:?}", handle.join());
   }
   ```

<details markdown="1"><summary>Check</summary>

It is `E0373`, naming `counts` as the borrowed value and pointing at the same `'static` requirement as the lesson's `lines` example; the `help` suggests adding `move`.

</details>

2. ▢ Add `move` to the closure above so it compiles, then spawn a second thread the same way, reusing `counts` in its closure too. Predict what happens before compiling.

<details markdown="1"><summary>Hint</summary>

`move` gave the first closure ownership of `counts`; ask what is left of `counts` by the time the second `thread::spawn` call tries to capture it.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0382`, use of a moved value: the first `move` closure already took `counts` for itself, so the second closure has nothing left to capture. The compiler's own suggestion is to clone `counts` before the first move, which works but is the workaround, not the fix; nothing about this program needs two threads to touch the same `Vec`, it needs two `Vec`s.

</details>

3. ▢ Predict whether this compiles, given that each closure only touches one field of `data`.

   ```rust
   use std::thread;

   struct Data {
       first: Vec<i32>,
       second: Vec<i32>,
   }

   fn main() {
       let data = Data { first: vec![1, 2, 3], second: vec![4, 5, 6] };
       let first_handle = thread::spawn(move || data.first.len());
       let second_handle = thread::spawn(move || data.second.len());
       println!("{:?}", first_handle.join());
       println!("{:?}", second_handle.join());
   }
   ```

<details markdown="1"><summary>Hint</summary>

The know-this section's diagnostic already showed the compiler tracking `data.first` as its own place, separate from `data.second`.

</details>

<details markdown="1"><summary>Check</summary>

It compiles and prints `Ok(3)` twice: disjoint capture lets the first closure move only `data.first` and the second move only `data.second`, so the two `move` closures do not fight over the same data, they each take a different, non-overlapping piece of it.

</details>

4. ▢ This closure panics with a formatted message rather than a string literal. Predict which type `downcast_ref` needs before compiling and running.

   ```rust
   use std::thread;

   fn main() {
       let handle = thread::spawn(|| {
           let bad_count = -1i32;
           panic!("byte count cannot be negative: {bad_count}");
       });

       match handle.join() {
           Ok(()) => println!("no panic"),
           Err(payload) => match payload.downcast_ref::<&str>() {
               Some(message) => println!("recovered: {message}"),
               None => println!("payload was not a &str"),
           },
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

A bare string literal in `panic!` is a `&'static str`; a `panic!` with formatting arguments has to build the message at runtime.

</details>

<details markdown="1"><summary>Check</summary>

`downcast_ref::<&str>()` returns `None` here and prints `payload was not a &str`: a formatted `panic!` call builds its message with `format!` internally, so the payload is a `String`, not a `&str`. Changing the call to `downcast_ref::<String>()` recovers `byte count cannot be negative: -1`.

</details>

5. ▢ Suppose your own machine reports that it can run four things in parallel. If your summariser reads a hundred small files, is spawning a hundred threads, one per file, obviously the fastest option?

<details markdown="1"><summary>Check</summary>

No: once more threads are runnable than the machine can actually run at the same time, the extra ones only add scheduling overhead and the memory cost of a full operating system stack each, without adding real parallelism. `thread::available_parallelism` exists so a program can ask what to divide work by; the right number of threads for a hundred files follows from that answer, it is not automatically one thread per file.

</details>

## Real-world reps

- [ ] Give your project's summariser a small handful of input files instead of one, spawn one `thread::spawn` per file that reads and parses that file into its own partial summary, and join every handle before combining the partial summaries in the main thread.
- [ ] Next to wherever you satisfied `thread::spawn`'s `'static` bound, write a comment saying plainly whether you moved each file's own data into its thread or cloned something the caller still needed, and why that choice feels like a workaround rather than a design.
- [ ] Tomorrow: call `thread::available_parallelism` once in your project without printing or logging what it returns, and compare that count, by eye, against how many files you actually spawned a thread for.

## Going further

- [Using Threads to Run Code Simultaneously](https://doc.rust-lang.org/book/ch16-01-threads.html): the Book's introduction to spawning threads and waiting on their handles
- [E0373](https://doc.rust-lang.org/error_codes/E0373.html): the diagnostic for a closure that may outlive data it only borrows
- [E0382](https://doc.rust-lang.org/error_codes/E0382.html): the diagnostic for using a value after it has already been moved
- [std::thread::JoinHandle](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html): the handle a spawned thread returns, and what its `join` method hands back
- [std::thread::available_parallelism](https://doc.rust-lang.org/std/thread/fn.available_parallelism.html): what a program can ask in order to decide how many threads a task deserves
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
