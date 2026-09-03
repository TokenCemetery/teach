---
title: 32. Interior Mutability
description: Moving the borrow rule from compile time to run time, what that buys, and what it costs when you get it wrong
type: lesson
---

# Lesson 32. Interior Mutability

**Mission link:** A memo table inside a parser that only exposes `&self`, or a counter shared between two owners of the same value, wants to mutate through a reference the borrow checker classifies as read-only, and widening every caller's signature to `&mut self` for one internal field breaks the API for everyone who only needed to read. Interior mutability keeps the `&self` methods and pays for the exception at run time instead.
**Primary source:** [std::cell](https://doc.rust-lang.org/std/cell/index.html)
**Prerequisites:** [Lesson 3](0003-borrowing.md), [Lesson 31](0031-shared-ownership.md)

## Warm-up

1. ▢ Lesson 3's borrow rule says any number of shared borrows or exactly one mutable borrow, never both, checked before the program runs. Given `let r = &record;` with nothing else touching `record`, what does the compiler assume about whether `record`'s fields might change while `r` is alive?

<details markdown="1"><summary>Check</summary>

It assumes they cannot change at all: a live shared reference promises its target is frozen for the reference's lifetime, enforced by refusing any `&mut` access nearby rather than by checking whether the code would actually have mutated anything.

</details>

2. ▢ Lesson 31 gave `Rc<T>` a `clone` that increments a reference count rather than duplicating the value, so every clone points at the same allocation. If every one of those clones only ever hands out `&T`, never `&mut T`, what capability does having a hundred owners of the same `Rc<Vec<i32>>` still not give any of them?

<details markdown="1"><summary>Check</summary>

The ability to mutate the vector. `Rc<T>`'s `Deref` only ever produces `&T`, so cloning it as many times as you like multiplies the number of readers, not the number of writers, which is exactly the gap the types in this lesson exist to fill.

</details>

## Know this

### The check moves from compile time to run time

Interior mutability does not repeal lesson 3's rule; it relocates the check from the compiler reading your source to a counter consulted while the program runs, turning a compile error that names two spans into a panic that names a message. An ordinary struct still cannot be mutated through a shared reference:

```rust
struct Counter {
    count: i32,
}

impl Counter {
    fn increment(&self) {
        self.count += 1;
    }
}
```

```text
error[E0594]: cannot assign to `self.count`, which is behind a `&` reference
 --> src/main.rs:7:9
  |
7 |         self.count += 1;
  |         ^^^^^^^^^^^^^^^ `self` is a `&` reference, so it cannot be written to
  |
help: consider changing this to be a mutable reference
  |
6 |     fn increment(&mut self) {
  |                   +++
```

Taking that help is not always possible: a trait method fixed at `&self`, or a field a hundred call sites already borrow immutably, cannot always be widened to `&mut self` without breaking those callers. Wrapping the field in `Cell` instead keeps `increment` at `&self` and moves the check to run time:

```rust
use std::cell::Cell;

struct Counter {
    count: Cell<i32>,
}

impl Counter {
    fn increment(&self) {
        self.count.set(self.count.get() + 1);
    }
}

fn main() {
    let c = Counter { count: Cell::new(0) };
    c.increment();
    c.increment();
    println!("{}", c.count.get());
}
```

This compiles and prints `2`. Nothing about the borrow rule changed; `increment` still only has a shared reference to `c`. What changed is which value that reference exposes: `count` itself, through `Cell`'s narrow interface, rather than the whole struct.

### Cell: get and set by value

`Cell<T>` never hands out a reference into the value it holds: `get` copies the value out, which is why it needs `T: Copy`, `set` moves a new value in overwriting the old one, and `replace` and `take` do the same by-value swap for non-`Copy` types. No method on `Cell` ever produces a `&T` or `&mut T` into the interior, so there is never a live borrow to conflict with. This is also why `Cell` cannot panic: every operation is one complete move in or out, with nothing outstanding to check.

### RefCell: borrow, borrow_mut, and the panic

`RefCell<T>` earns the flexibility `Cell` lacks, at a cost `Cell` does not pay. `borrow` returns a `Ref<T>` and `borrow_mut` a `RefMut<T>`, both behaving like the reference they wrap through `Deref`, and both running lesson 3's rule against a counter inside the `RefCell` rather than against the compiler. Two `borrow_mut` calls alive at once trip that counter:

```rust
use std::cell::RefCell;

fn main() {
    let cell = RefCell::new(vec![1, 2, 3]);
    let a = cell.borrow_mut();
    let b = cell.borrow_mut();
    println!("{:?} {:?}", a, b);
}
```

```text
thread 'main' panicked at src/main.rs:6:18:
RefCell already borrowed
```

The panic header also carries a numeric thread identifier that changes each run, trimmed above as process noise. Compare this with lesson 3's `E0499` for the compiler-checked version of the same mistake, two overlapping `&mut` borrows of a plain `i32`: the compiler there points at both borrow sites before the program runs. Here there is no compiler diagnostic at all, since to the type system `a` and `b` are both just shared borrows of the `RefCell`; the violation lives one layer down, visible only to `RefCell` itself, at the moment `borrow_mut` is called. That panic is a choice, not a law of the type: `try_borrow_mut` runs the identical check and returns the failure as a value.

```rust
use std::cell::RefCell;

fn main() {
    let cell = RefCell::new(vec![1, 2, 3]);
    let _a = cell.borrow_mut();
    match cell.try_borrow_mut() {
        Ok(_) => println!("got it"),
        Err(e) => println!("{e}"),
    }
}
```

This prints `RefCell already borrowed`, the same text the panic carried, but as an `Err` to match on, log or recover from, instead of a message that ends the program.

### Where the panic actually bites: a guard held across a call

Two `borrow_mut` calls back to back are rare and easy to spot in review; the version that bites is a guard still alive when execution leaves the function that took it, usually held across a call to another method that also borrows:

```rust
use std::cell::RefCell;

struct Log {
    entries: RefCell<Vec<String>>,
}

impl Log {
    fn record(&self, line: &str) {
        let mut entries = self.entries.borrow_mut();
        entries.push(line.to_string());
        self.report();
    }

    fn report(&self) {
        let entries = self.entries.borrow();
        println!("{} entries so far", entries.len());
    }
}

fn main() {
    let log = Log { entries: RefCell::new(Vec::new()) };
    log.record("first line");
}
```

```text
thread 'main' panicked at src/main.rs:15:36:
RefCell already mutably borrowed
```

`record` never releases its `RefMut` before calling `self.report`, which tries to `borrow` the same cell while that guard is still alive; nothing about the call site looks dangerous, since `report` only takes `&self`, and the problem is invisible until it runs. The fix is lesson 3's rule again, applied to when a value drops rather than when it is declared: end the mutable borrow before the next one starts, in a block of its own.

```rust
impl Log {
    fn record(&self, line: &str) {
        {
            let mut entries = self.entries.borrow_mut();
            entries.push(line.to_string());
        }
        self.report();
    }

    fn report(&self) {
        let entries = self.entries.borrow();
        println!("{} entries so far", entries.len());
    }
}
```

With the block in place, `entries` drops at its closing brace, `report`'s `borrow` starts cleanly afterwards, and calling `record` twice prints `1 entries so far` then `2 entries so far`. Nothing about the type changed; only how long the guard stayed alive did.

### `Rc<RefCell<T>>`: shared ownership that can still mutate

`Rc<T>`, from lesson 31, gives many owners of one value but only ever `&T` through any of them. Wrapping the interior in a `RefCell` gives every one of those owners a way to ask for `&mut T` when it actually needs it:

```rust
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let counts = Rc::new(RefCell::new(Vec::<i32>::new()));

    let writer = Rc::clone(&counts);
    writer.borrow_mut().push(10);

    let reader = Rc::clone(&counts);
    reader.borrow_mut().push(20);

    println!("{:?}", counts.borrow());
}
```

This prints `[10, 20]`: three `Rc`s, one `Vec`, every mutation visible through every clone since they share one `RefCell`. The combination earns its keep when a value has more than one long-term owner that may need to mutate it, which is lesson 31's cycle: a back edge, where the node pointed at must be updated after the node pointing at it already exists, needs both shared ownership and the ability to mutate through it. It is also, honestly, the standard workaround for a design with one real owner that was never built that way. Before reaching for it, check whether one piece of code could own the value outright and hand out plain borrows or an updated copy instead, since `Rc<RefCell<T>>` trades that question for a panic that surfaces only once two of its borrows collide.

### Why none of this crosses a thread

`RefCell`'s runtime check assumes only one thread asks it questions at a time; the standard library says so by not implementing `Sync` for it. `Arc<T>`, unlike `Rc<T>`, is safe to send across threads, but wrapping a `RefCell` inside one does not make the `RefCell` itself safe to touch from two threads, and the compiler rejects it before the program runs:

```rust
use std::cell::RefCell;
use std::sync::Arc;
use std::thread;

fn main() {
    let shared = Arc::new(RefCell::new(0));
    let handle = {
        let shared = Arc::clone(&shared);
        thread::spawn(move || {
            *shared.borrow_mut() += 1;
        })
    };
    handle.join().unwrap();
    println!("{}", shared.borrow());
}
```

```text
error[E0277]: `RefCell<i32>` cannot be shared between threads safely
   --> src/main.rs:9:23
    |
  9 |           thread::spawn(move || {
    | _________-------------_^
    | |         |
    | |         required by a bound introduced by this call
 10 | |             *shared.borrow_mut() += 1;
 11 | |         })
    | |_________^ `RefCell<i32>` cannot be shared between threads safely
    |
    = help: the trait `Sync` is not implemented for `RefCell<i32>`
    = note: if you want to do aliasing and mutation between multiple threads, use `std::sync::RwLock` instead
    = note: required for `Arc<RefCell<i32>>` to implement `Send`
note: required because it's used within this closure
   --> src/main.rs:9:23
    |
  9 |         thread::spawn(move || {
    |                       ^^^^^^^
note: required by a bound in `spawn`
```

The diagnostic continues with a `note` pointing at the standard library's own source by an absolute path, naming the `Send + 'static` bound `spawn` declares; that line is cut above since it names a location on this machine, not anything portable. The reason given is `Sync`, not the borrow rule: an `&RefCell<T>` reachable from two threads at once is exactly what `Sync` rules out, and lesson 34 names that trait, and `Send` alongside it, properly. The type that does `RefCell`'s job across threads is lesson 33's, paying for the crossing with an actual lock rather than a borrow counter.

## Practice

1. ▢ Predict the error code before compiling this.

   ```rust
   use std::cell::Cell;

   fn main() {
       let cell: Cell<String> = Cell::new(String::from("hi"));
       let v = cell.get();
       println!("{v}");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`Cell::get` only exists under one trait bound on `T`; check whether `String` satisfies it.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0599`: `get` exists for `Cell<String>` but `String: Copy` does not hold. `Cell<T>::get` only exists when `T: Copy`; reach for `take` or `replace` on a non-`Copy` type instead, or use `RefCell` if the value must be read without being moved out.

</details>

2. ▢ Predict what happens when this runs; the order of the two borrows is reversed from the double `borrow_mut` example above.

   ```rust
   use std::cell::RefCell;

   fn main() {
       let cell = RefCell::new(5);
       let r = cell.borrow();
       let m = cell.borrow_mut();
       println!("{r} {m}");
   }
   ```

<details markdown="1"><summary>Check</summary>

It panics with `RefCell already borrowed`, the same message two `borrow_mut` calls produced: it does not care whether the existing borrow was shared or exclusive, only that one is outstanding, so a live `Ref` blocks a `RefMut` just as a live `RefMut` blocks another.

</details>

3. ▢ Predict what this prints.

   ```rust
   use std::cell::RefCell;

   fn main() {
       let cell = RefCell::new(5);
       let _m = cell.borrow_mut();
       match cell.try_borrow() {
           Ok(v) => println!("got {v}"),
           Err(e) => println!("{e}"),
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

It prints `RefCell already mutably borrowed`. `try_borrow` runs the same check `borrow` would; since the `borrow_mut` guard is still alive, it returns `Err` instead of panicking, worded from the opposite direction of the earlier `try_borrow_mut` message.

</details>

4. ▢ Predict whether this panics, and if so, with which message.

   ```rust
   struct Nested {
       depth: std::cell::RefCell<u32>,
   }

   impl Nested {
       fn go(&self) {
           let mut d = self.depth.borrow_mut();
           *d += 1;
           if *d < 2 {
               self.go();
           }
       }
   }

   fn main() {
       Nested { depth: std::cell::RefCell::new(0) }.go();
   }
   ```

<details markdown="1"><summary>Hint</summary>

`go` calls itself while its own `borrow_mut` guard, `d`, is still in scope; a call does not have to reach a different function to count.

</details>

<details markdown="1"><summary>Check</summary>

It panics with `RefCell already borrowed`. The recursive call to `self.go()` happens while `d` is still alive, so the inner `borrow_mut` finds the outer one outstanding; calling back into the same method reproduces this lesson's guard-across-a-call panic without needing two named methods.

</details>

5. ▢ Predict whether this compiles, given that the wrapper is `Rc` rather than the `Arc` this lesson used.

   ```rust
   use std::cell::RefCell;
   use std::rc::Rc;
   use std::thread;

   fn main() {
       let shared = Rc::new(RefCell::new(0));
       let handle = thread::spawn(move || {
           *shared.borrow_mut() += 1;
       });
       handle.join().unwrap();
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what changes about which type fails to be `Send` once `Arc` is replaced with `Rc`.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile: `E0277`, `Rc<RefCell<i32>>` cannot be sent between threads safely, since it does not implement `Send`. This differs from the `Arc` version: `Rc` is never `Send`, regardless of what it wraps, so the program fails before `RefCell`'s missing `Sync` even matters; `Arc` fixes this half, `RefCell` remains the other.

</details>

## Real-world reps

- [ ] Add a `RefCell<HashMap<String, u32>>` to your project's parser that counts how many times `parse` has seen each path, updating the count from inside `parse` without changing its signature away from `&self`.
- [ ] Beside the new field, write down whether its `borrow_mut` could ever overlap with another: whether `parse` calls itself or calls back into the parser, and that no second thread can reach it yet, since none is wired in before lesson 33.
- [ ] Tomorrow: search your project for a `clone` that exists only to end an argument about ownership rather than because two owners genuinely need the value, and note whether `Rc<RefCell<T>>` would remove it honestly or just relocate the same argument into a run-time panic.

## Going further

- [`RefCell<T>` and the Interior Mutability Pattern](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html): the Book's example of `RefCell` satisfying a trait fixed at `&self`
- [E0594](https://doc.rust-lang.org/error_codes/E0594.html): the diagnostic for assigning through a shared reference
- [E0277](https://doc.rust-lang.org/error_codes/E0277.html): the diagnostic this stage keeps returning to for a missing trait bound, here `Sync`
- [std::cell::RefCell](https://doc.rust-lang.org/std/cell/struct.RefCell.html): the type's own page, with `try_borrow`, `try_borrow_mut` and the guard API
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
