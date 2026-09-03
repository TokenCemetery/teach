---
title: 37. What a Future Is
description: A state machine with one method, driven by whoever polls it, and what that means for code that looks sequential
type: lesson
---

# Lesson 37. What a Future Is

**Mission link:** Async code reads like sequential code with `.await` scattered through it, and an engineer who cannot say what happens at each of those points will misdiagnose the first stall this stage's project meets: waiting on something real, spinning uselessly, and never being asked to run all look identical from outside.
**Primary source:** [std::future::Future](https://doc.rust-lang.org/std/future/trait.Future.html)
**Prerequisites:** [Lesson 8](0008-enums.md), [Lesson 29](0029-threads-joining-and-panics.md)

## Warm-up

1. ▢ Lesson 8 built a `Line` enum whose `Request` variant carries three named fields, and matching on it has to handle every variant lesson 8 declared. The type this lesson is built around, `Poll<T>`, is declared as `enum Poll<T> { Ready(T), Pending }`. Given that shape, what must a `match` on a `Poll<u32>` value handle, and what can each arm do with what it carries?

<details markdown="1"><summary>Check</summary>

Exactly two arms: one for `Ready(value)`, binding the payload as a plain `u32`, and one for `Pending`, carrying nothing, the same exhaustive treatment lesson 8 gave `Line`'s three variants. `Poll` is nothing special, an enum with one payload-bearing variant and one empty one, read exactly as lesson 8 taught.

</details>

2. ▢ Lesson 29's `thread::spawn` starts its closure running the moment it is called, whether or not the caller ever calls `join`; `join` only reports what the thread already did. Given that, what would you expect an ordinary function containing a loop to do if you call it and never touch what it returns?

<details markdown="1"><summary>Check</summary>

The loop has already run to completion by the time the call finishes: a plain function's body executes eagerly the moment it is called, exactly as a spawned closure starts running the moment `spawn` is called. Discarding the return value only discards the answer, not the work. This lesson introduces a function shape where that assumption stops holding.

</details>

## Know this

### The trait is one method, and Poll is an enum you already know

The standard library states the whole contract in a few lines:

```rust
pub trait Future {
    type Output;

    // Required method
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

One method, one associated type. `poll` is the only thing anyone may do with a future beyond building it, and it returns another ordinary enum: `pub enum Poll<T> { Ready(T), Pending, }`. Lesson 8 already gives the vocabulary: `Ready` carries a finished value the way `Line::Note` carries a `String`, and `Pending` carries nothing the way `Line::Blank` does. The documentation states each plainly: "Poll::Pending if the future is not ready yet" and "Poll::Ready(val) with the result val of this future if it finished successfully." A future is not asynchronous by magic; it is a value with one method, and that method either hands back an answer or says not yet.

### A hand-written future, and the executor that drives it

A type implementing `Future` needs nothing beyond that method, so building one by hand is direct:

```rust
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};

struct CountToReady {
    polls_remaining: u32,
}

impl Future for CountToReady {
    type Output = &'static str;

    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        if self.polls_remaining == 0 {
            Poll::Ready("done")
        } else {
            self.polls_remaining -= 1;
            println!("poll: not ready yet");
            Poll::Pending
        }
    }
}
```

Each call decrements a counter and reports `Pending` twice, printing on the way, before reporting `Ready("done")` on the third poll. Driving it needs an executor, and the standard library alone is enough to build one:

```rust
fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}
```

Four ingredients: `Waker::noop`, a `Waker` that does nothing when woken, standing in for lesson 38's machinery; `Context::from_waker`, wrapping that waker into the parameter `poll` demands; `Box::pin`, giving the future a fixed address behind a pointer `poll`'s signature accepts; and a loop calling `poll` again while the result is `Pending`. Running `block_on(CountToReady { polls_remaining: 2 })` prints, in order:

```text
poll: not ready yet
poll: not ready yet
block_on returned: done
```

`Waker::noop` stabilised in release 1.85.0, confirmed against that release's stabilised APIs and against the standard library's own `#[stable(feature = "noop_waker", since = "1.85.0")]` attribute on the method. About a dozen lines, no dependency, no runtime: this is the whole model underneath the rest of this stage.

### What async fn actually produces

An `async fn` looks like an ordinary function with an extra keyword, and that appearance is the trap: calling one does not run its body, it builds a value implementing `Future`, and nothing happens until that value is polled.

```rust
async fn greet() -> String {
    println!("greet: running");
    String::from("hello")
}

fn main() {
    greet();
    println!("main: finished");
}
```

This compiles, but "greet: running" never prints, only "main: finished":

```text
warning: unused implementer of `Future` that must be used
 --> src/main.rs:7:5
  |
7 |     greet();
  |     ^^^^^^^
  |
  = note: futures do nothing unless you `.await` or poll them
  = note: `#[warn(unused_must_use)]` (part of `#[warn(unused)]`) on by default
```

"futures do nothing unless you `.await` or poll them" is the whole lesson in one line. The same fact appears from the other side when the call's result is asked to do something a `Future` cannot do:

```rust
async fn compute() -> i32 {
    21
}

fn main() {
    let x = compute();
    println!("{x}");
}
```

```text
error[E0277]: `impl Future<Output = i32>` doesn't implement `std::fmt::Display`
 --> src/main.rs:7:15
  |
7 |     println!("{x}");
  |               ^^^ `impl Future<Output = i32>` cannot be formatted with the default formatter
  |
  = help: the trait `std::fmt::Display` is not implemented for `impl Future<Output = i32>`
  = note: in format strings you may be able to use `{:?}` (or {:#?} for pretty-print) instead
```

`x`'s type is stated right there, `impl Future<Output = i32>`, not `i32`: calling `compute` never ran the body that produces 21, it built a state machine that will, once something polls it. The same `block_on` from the previous section can drive an `async fn`'s body directly, and `.await` is what connects the two:

```rust
async fn run() -> &'static str {
    let value = CountToReady { polls_remaining: 2 }.await;
    println!("run: saw {value}");
    value
}

fn main() {
    let value = block_on(run());
    println!("block_on returned: {value}");
}
```

```text
poll: not ready yet
poll: not ready yet
run: saw done
block_on returned: done
```

Nothing new is running this loop; it is the same `block_on`, polling the same `CountToReady`. `run`'s compiler-generated state machine holds `CountToReady` inside itself, and each time something polls `run`, it polls that inner future in turn, forwarding `Pending` upward and only moving past the `.await` once the inner future reports `Ready`. `.await` is not a call and runs nothing by itself; it marks where `run`'s own `poll` should resume next time something, here `block_on`'s loop, asks it to make progress.

### The busy-spin, named honestly

`block_on`'s loop calls `poll` again the instant `Pending` comes back, with nothing between attempts: no sleep, no signal, no yielding to anything else. Against `CountToReady` this finishes almost instantly, since the work behind each `Pending` is trivial. Against a future that never becomes `Ready`, the loop still finishes each poll instantly and starts the next one immediately, spending the processor on nothing, forever: under a three second watchdog, a future whose `poll` always returned `Pending` was killed in three of three attempts, each run printing only its startup line before being killed. This works, in that `CountToReady`'s result is correct regardless of how eagerly it is polled. It works badly, because a real wait, a socket with nothing to read yet or a timer that has not elapsed, gives `block_on` nothing to do except ask again immediately. What is missing is the future telling the executor when trying again is worth it, and that piece is a real waker, lesson 38's subject. This executor never calls one, deliberately: seeing the spin first is what makes a waker look like a fix rather than ceremony.

### Why poll takes Pin<&mut Self>

`poll`'s receiver is `Pin<&mut Self>`, not the plain `&mut self` used elsewhere in this arc, because an `async` block's compiler-generated state can hold a borrow into one of its own fields, a self-reference that only exists once polling starts, and moving that state afterwards would leave the borrow pointing at the wrong place. `Pin` is the standard library's promise that a value has stopped moving, enforced structurally rather than trusted to callers, which is why calling `poll` on an unpinned value does not compile:

```rust
use std::future::{self, Future};
use std::task::{Context, Waker};

fn main() {
    let mut ready = future::ready(21);
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);
    let _ = ready.poll(&mut cx);
}
```

```text
error[E0599]: no method named `poll` found for struct `std::future::Ready<T>` in the current scope
 --> src/main.rs:8:19
  |
8 |     let _ = ready.poll(&mut cx);
  |                   ^^^^ method not found in `std::future::Ready<{integer}>`
  |
help: consider pinning the expression
  |
8 ~     let mut pinned = std::pin::pin!(ready);
9 ~     let _ = pinned.as_mut().poll(&mut cx);
  |
```

`future::ready`'s value implements `Future` like any other; `poll` still takes a pinned receiver, and nothing here pins it. Lesson 44 covers what `Pin` restricts and how a value gets pinned; here, treat the refusal as proof that pinning is load-bearing, not ceremony.

## Practice

1. ▢ Predict what changing `CountToReady { polls_remaining: 2 }` to `CountToReady { polls_remaining: 0 }` does to the output shown above, then run it to check.

<details markdown="1"><summary>Check</summary>

Only `block_on returned: done` prints, with no "poll: not ready yet" lines: the first call to `poll` already sees `polls_remaining` at zero and reports `Ready` immediately, so the `Pending` branch never runs.

</details>

2. ▢ Predict whether `let x = compute();` followed by `println!("{x}")` compiles, for `async fn compute() -> i32 { 21 }`, then compile it and read what the message says `x`'s type actually is.

<details markdown="1"><summary>Hint</summary>

Calling an `async fn` never runs its body. Ask what the call expression's value is instead.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `E0277`, "`impl Future<Output = i32>` doesn't implement `std::fmt::Display`". `x` is a value implementing `Future`, not the `i32` the function eventually produces, and formatting only works on the type a value actually has.

</details>

3. ▢ A future's `poll` always returns `Poll::Pending`. Predict what calling `block_on` on it does to processor usage, then run it under a timeout you set and confirm nothing is left running.

<details markdown="1"><summary>Check</summary>

It spins forever, calling `poll` again immediately with no delay and no way to stop on its own; under a three second watchdog it was killed in three of three attempts. Nothing about `Poll::Pending` tells `block_on` to wait before trying again, so it does not.

</details>

4. ▢ Write an `async fn` whose body awaits two separate `CountToReady` values in sequence, each printing its own label when polled. Predict whether the two futures' `Pending` lines interleave or whether the first finishes before the second is polled at all, then run it.

<details markdown="1"><summary>Hint</summary>

`.await` is a resume point inside one sequential function body, not a second thread starting alongside the first.

</details>

<details markdown="1"><summary>Check</summary>

The first future's `Pending` lines all print, then it completes, then the second future starts: the two do not interleave, because `run`'s state machine only reaches the second `.await` after the first one resolves. Nothing here runs concurrently; it reads top to bottom like the ordinary function it resembles.

</details>

5. ▢ An `async fn` with no `.await` inside it still has to be polled once to run. Does wrapping ordinary, already-synchronous code in `async fn` change when or how it executes, given it all happens inside one `poll` call with no pause?

<details markdown="1"><summary>Check</summary>

No: with no `.await` inside it, the generated state machine has exactly one state, and the whole body runs to completion the first time anything polls it, the same as if `async` were never there. `async` only matters once a body needs to give control back at an `.await` point; without one, it is a synchronous function wearing an extra keyword.

</details>

## Real-world reps

- [ ] Give your project's line parser a hand-written `Future` whose `poll` parses the line it holds and returns `Poll::Ready` straight away, and drive it, one raw line at a time, with your own `block_on`; write one line saying this is the version a runtime replaces once a line genuinely has to wait, and that nothing about the parsing changed.
- [ ] Keep the previous stage's version of the summariser alongside this one, and confirm both reject the same malformed lines from `reference/the-project.md`'s sample input the same way.
- [ ] Tomorrow: without rereading this lesson, write from memory the four standard-library pieces `block_on` needed and what each was for.

## Going further

- [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/): the model, built without reference to any one runtime
- [std::task::Poll](https://doc.rust-lang.org/std/task/enum.Poll.html): the two-variant enum every `poll` call returns
- [std::task::Waker](https://doc.rust-lang.org/std/task/struct.Waker.html): the handle a real executor uses to be told when to try again, including `noop`
- [Announcing Rust 1.85.0 and Rust 2024](https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/): the release that stabilised `Waker::noop`
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
