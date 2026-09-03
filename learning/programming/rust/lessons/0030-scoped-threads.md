---
title: 30. Scoped Threads
description: Why a thread that cannot outlive its scope may borrow, and why this is the first thing to reach for rather than the last
type: lesson
---

# Lesson 30. Scoped Threads

**Mission link:** A pipeline that summarises several files at once needs threads and nothing more once every thread finishes before the function that started them returns, and reaching for shared ownership anyway buys a senior engineer only a habit they will later have to notice and undo.
**Primary source:** [std::thread::scope](https://doc.rust-lang.org/std/thread/fn.scope.html)
**Prerequisites:** [Lesson 3](0003-borrowing.md), [Lesson 29](0029-threads-joining-and-panics.md)

## Warm-up

1. ▢ Lesson 29 showed that a panic inside a spawned thread is reported through `join`, not propagated into the caller by itself. If a program spawns three threads with `thread::spawn` and one panics, what happens to the other two, and how does the caller find out about the first one?

<details markdown="1"><summary>Check</summary>

The other two keep running to completion on their own schedule; a panic in one thread has no automatic effect on any other. The caller finds out only by calling `join` on that thread's own handle and checking whether it returns `Err`.

</details>

2. ▢ Lesson 3 stated the borrow rule as one mutable reference, or any number of immutable ones, to the same data, never both at once. If two closures each need to mutate a different element of one `Vec`, does that rule forbid it, and what changes if they target the same element instead?

<details markdown="1"><summary>Check</summary>

The rule is about the same location, not the same collection, so two mutable borrows into disjoint elements do not alias; the difficulty is only that the compiler has to be shown the split, since indexing the same `Vec` twice looks like two borrows of the whole thing. Targeting the same element is different: one location borrowed mutably twice, which the rule forbids outright.

</details>

## Know this

### Why the borrowing version comes first

A thread that reads a shared file list and a shared configuration, does its work, and is joined before the function that spawned it returns has never needed more than a borrow: nothing about it outlives the call that created it. Reaching for `Arc<Mutex<_>>` for that thread anyway still compiles and runs, and that is the trap: it teaches the habit of sharing ownership before checking whether ownership needed to be shared at all. A reader taught the cloning, locking version first takes it as the default and has to unlearn it later; a reader taught the borrowing version first learns to ask, for every thread, whether it outlives its data, and reaches for shared ownership only once the answer is yes. Scoped threads start that question, because they are the case where the answer is no and no sharing machinery is needed to say so.

### Borrowing under `thread::scope`, and what `thread::spawn` required instead

`thread::scope` takes a closure and passes it a `Scope`, through which threads are spawned with `s.spawn` instead of `thread::spawn`. Two threads, each given a line to measure and a private slot to write into, need no `Arc`, no `clone`, and no lifetime annotation anywhere in the caller's code:

```rust
use std::thread;

fn main() {
    let lines = vec![
        String::from("/index 200 1200"),
        String::from("/login 500 90"),
    ];
    let mut first_len = 0usize;
    let mut second_len = 0usize;

    thread::scope(|s| {
        s.spawn(|| {
            first_len = lines[0].len();
        });
        s.spawn(|| {
            second_len = lines[1].len();
        });
    });

    let lengths = vec![first_len, second_len];
    println!("{:?}", lengths);
    println!("{:?}", lines);
}
```

This prints `[15, 13]` then `["/index 200 1200", "/login 500 90"]`: both threads wrote their length into their own slot, and `lines` is still owned by `main` afterwards. The same borrow under `thread::spawn` does not compile, because `spawn`'s closure is bounded by `'static`:

```rust
use std::thread;

fn main() {
    let lines = vec![
        String::from("/index 200 1200"),
        String::from("/login 500 90"),
    ];
    let mut first_len = 0usize;

    let a = thread::spawn(|| {
        first_len = lines[0].len();
    });
    a.join().unwrap();
}
```

```text
error[E0373]: closure may outlive the current function, but it borrows `lines`, which is owned by the current function
  --> src/main.rs:9:27
   |
 9 |     let a = thread::spawn(|| {
   |                           ^^ may outlive borrowed value `lines`
10 |         first_len = lines[0].len();
   |                     ----- `lines` is borrowed here
   |
note: function requires argument type to outlive `'static`
help: to force the closure to take ownership of `lines` (and any other referenced variables), use the `move` keyword
```

Lesson 29 named this diagnostic; capturing `first_len` produces an identical error, trimmed here as redundant. The `help` moves `lines` into the closure, which compiles, but takes the original from the caller or hands the thread a copy, spending more than the borrow ever needed.

### Why the borrow is sound, and the join nobody asked for

`Scope::spawn` is declared as `fn spawn<F, T>(&'scope self, f: F) -> ScopedJoinHandle<'scope, T> where F: FnOnce() -> T + Send + 'scope, T: Send + 'scope`: the bound is `'scope`, not `'static`. That is not `'static` waived for a special case; it is a shorter region named by `Scope` itself, safe to borrow into because, in the standard library's words, "the scope guarantees all threads will be joined at the end of the scope." The program above never calls `.join()` on either handle, yet `first_len` and `second_len` hold both results the moment `thread::scope` returns: "all threads spawned within the scope that haven't been manually joined will be automatically joined before this function returns," and the printed `[15, 13]` is that promise observed rather than assumed. Because every thread is joined before `thread::scope` can return, no borrow it holds can ever be read after its source is gone, the same soundness rule lesson 27 gave a struct's lifetime parameter, applied here to a region the compiler manages rather than one you write by hand.

### Writing to disjoint parts of one collection

Two threads writing into different elements of the same `Vec` need the split made visible to the compiler; `split_at_mut` returns two mutable slices that borrow disjoint halves:

```rust
use std::thread;

fn main() {
    let lines = vec![
        String::from("/index 200 1200"),
        String::from("/login 500 90"),
    ];
    let mut lengths = vec![0usize; 2];
    let (first_half, second_half) = lengths.split_at_mut(1);

    thread::scope(|s| {
        s.spawn(|| {
            first_half[0] = lines[0].len();
        });
        s.spawn(|| {
            second_half[0] = lines[1].len();
        });
    });

    println!("{:?}", lengths);
}
```

This compiles and prints `[15, 13]`. Skipping the split and letting both closures capture the whole `Vec` mutably is rejected before either thread runs:

```text
error[E0499]: cannot borrow `lengths` as mutable more than once at a time
   --> src/main.rs:14:17
    |
 10 |     thread::scope(|s| {
    |                    - has type `&'1 Scope<'1, '_>`
 11 |         s.spawn(|| {
    |         -       -- first mutable borrow occurs here
    |  _________|
    | |
 12 | |           lengths[0] = lines[0].len();
    | |           ------- first borrow occurs due to use of `lengths` in closure
 13 | |       });
    | |________- argument requires that `lengths` is borrowed for `'1`
 14 |         s.spawn(|| {
    |                 ^^ second mutable borrow occurs here
 15 |             lengths[0] = lines[1].len();
    |             ------- second borrow occurs due to use of `lengths` in closure
```

The note that follows quotes the standard library's own source by absolute path and is trimmed here for that reason. `E0499` is the warm-up's rule again: indexing `lengths` from two closures looks like two mutable borrows of the whole `Vec`, so the split has to be made explicit before two threads can each own a piece of it.

### The `ScopedJoinHandle`: a return value, and a panic

`s.spawn` returns a `ScopedJoinHandle<T>`, and calling `.join()` on it gives back the closure's return value instead of requiring a slot to write into:

```rust
use std::thread;

fn main() {
    let lines = vec![
        String::from("/index 200 1200"),
        String::from("/login 500 90"),
    ];

    let total: usize = thread::scope(|s| {
        let a = s.spawn(|| lines[0].len());
        let b = s.spawn(|| lines[1].len());
        a.join().unwrap() + b.join().unwrap()
    });

    println!("{total}");
}
```

This prints `28`. A `ScopedJoinHandle` also earns its keep when a thread panics: `join`'s own documentation says "if the associated thread panics, `Err` is returned with the panic payload," so joining it explicitly turns the panic into a value you handle. Three threads, one panicking immediately while the other two sleep briefly and then print, gave the same result in three runs each of two shapes tried. Joining the panicking thread's handle before the scope ends: `Err` from that `join` every time, both siblings' prints appeared, and the scope returned normally with no panic reaching `main`, in all three runs. Dropping that handle instead, so it is never joined by hand: the siblings still finished and printed every time, but once every thread was joined internally, `thread::scope` itself panicked with "a scoped thread panicked", and nothing after that call ran, in all three runs, matching the documented rule, which reads "if any of the automatically joined threads panicked, this function will panic". The two siblings' print order was not fixed between runs; neither shape controls which finishes first.

### What scope cannot do

`thread::scope` only works when every thread it spawns can finish before the call to `scope` returns, which rules out a thread, or data it touches, that must survive past the function that created it: a worker stored inside a struct so it keeps running after the constructor returns, a thread handed to code whose lifetime the caller does not control, or a value a thread must still read after its own creating scope has ended. None of that is a limitation to work around here; it is the boundary where borrowing runs out and shared ownership is the honest answer, which is what `Arc` exists for, in the next lesson.

## Practice

1. ▢ Predict whether this compiles, given that neither thread mutates anything.

   ```rust
   use std::thread;

   fn main() {
       let banner = String::from("logsum");
       thread::scope(|s| {
           s.spawn(|| println!("{banner} worker one"));
           s.spawn(|| println!("{banner} worker two"));
       });
   }
   ```

<details markdown="1"><summary>Check</summary>

It compiles and prints both lines, in either order between runs: two immutable borrows of `banner` are not in conflict, and `s.spawn` needs no `'static` bound to allow it.

</details>

2. ▢ Rewrite the first example under "Know this" so both threads use `thread::spawn` instead of `s.spawn`, keeping `.join()` calls on both handles. Predict the error code for each captured variable before compiling.

<details markdown="1"><summary>Hint</summary>

Every non-`'static` variable a `thread::spawn` closure borrows is reported separately, even when two closures borrow the same one.

</details>

<details markdown="1"><summary>Check</summary>

Each closure produces its own `E0373`, one for the local slot it writes and one for `lines`, since neither is `'static`; four diagnostics in total, all the same shape as the one this lesson quoted.

</details>

3. ▢ In the return-value example above, replace the last line of the closure with the one below, adding the two `.join()` calls directly instead of unwrapping first. Predict the error code.

   ```rust
   let total = thread::scope(|s| {
       let a = s.spawn(|| lines[0].len());
       let b = s.spawn(|| lines[1].len());
       a.join() + b.join()
   });
   ```

<details markdown="1"><summary>Check</summary>

It is `E0369`: `Result` has no `Add` implementation, since `join` returns a `Result`, not the value itself, so the panic case has to be handled, with `unwrap` or otherwise, before the two lengths can be combined.

</details>

4. ▢ Predict the error code for two threads that each call `.iter_mut()` on the same `Vec` inside one `thread::scope` block, without splitting it first.

<details markdown="1"><summary>Hint</summary>

`iter_mut` borrows the whole collection mutably for as long as the iterator exists, exactly like indexing it does in this lesson's disjoint-writes example.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0499` again: `iter_mut` borrows the whole `Vec` mutably for as long as it exists, so the borrow checker sees the same conflict as two closures indexing it, and `split_at_mut` or `chunks_mut` is the fix, not a smaller loop.

</details>

5. ▢ Take the panicking-thread example from "Know this" where the panicking thread's handle is dropped rather than joined. Predict whether the two sleeping threads' prints appear before the program ends, and whether any code written after the `thread::scope` call runs. Then compile, run it under a few attempts, and check whether your prediction held every time.

<details markdown="1"><summary>Check</summary>

Both sleeping threads' prints appeared before the program ended in every run tried, because `scope` joins every thread internally before deciding whether to panic itself; the code after the `thread::scope` call never ran in any of those runs, because the panicked thread made `thread::scope` itself panic, unwinding past everything that followed it.

</details>

## Real-world reps

- [ ] Rewrite your project's multi-file rep from lesson 29 to spawn each file's summarising thread inside `thread::scope` instead of `thread::spawn`, letting every thread borrow the shared file list and the shared, read-only configuration rather than cloning or moving them, and add one comment naming which `clone` or `move` the diff removed.
- [ ] Confirm every thread in that rewrite finishes, and its result is folded into the overall summary, before `thread::scope` returns, and note in one comment why that guarantee is what made the borrow legal.
- [ ] Tomorrow: find one place, here or elsewhere, where a value is wrapped for sharing across threads that all finish before the function that spawned them returns, and check whether `thread::scope` compiles in its place.

## Going further

- [std::thread::Scope](https://doc.rust-lang.org/std/thread/struct.Scope.html): the type through which scoped threads are spawned, and its `'scope` and `'env` lifetimes
- [std::thread::ScopedJoinHandle](https://doc.rust-lang.org/std/thread/struct.ScopedJoinHandle.html): the handle returned by a scoped spawn, and what `join` returns on a panic
- [E0373](https://doc.rust-lang.org/error_codes/E0373.html): the diagnostic for a closure that may outlive data it borrows
- [Announcing Rust 1.63.0](https://blog.rust-lang.org/2022/08/11/Rust-1.63.0/): the release notes that introduced scoped threads
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
