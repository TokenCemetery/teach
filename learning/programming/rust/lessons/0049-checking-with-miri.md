---
title: 49. Checking With Miri
description: The tool that turns an invisible soundness bug into a report, what it catches, and what it cannot
type: lesson
---

# Lesson 49. Checking With Miri

**Mission link:** Lesson 48 showed undefined behaviour is silent on stable Rust: a broken invariant can print a plausible answer and leave no trace. This lesson turns that silence into a report you can read before shipping, so "it printed the right number" and "Miri found nothing" are not the same claim.
**Primary source:** [Miri](https://github.com/rust-lang/miri)
**Prerequisites:** [Lesson 48](0048-undefined-behaviour.md), [Lesson 47](0047-raw-pointers.md)

## Warm-up

1. ▢ Lesson 48 catalogued undefined behaviour: out-of-bounds access, broken aliasing, data races. If a program does one of these and still prints the expected answer, what does that tell you about whether the code is sound?

<details markdown="1"><summary>Check</summary>

Nothing. A plausible answer is one possible outcome of undefined behaviour, not evidence against it: the compiler was free to do anything once the invariant broke, and the answer you hoped for is inside that range. Soundness is a claim about every execution, not the one you watched.

</details>

2. ▢ Lesson 47 covered what a raw pointer does not promise: no validity, no lifetime, no aliasing, all pushed onto the `unsafe` block that dereferences it. Given that, can the pointer's type alone tell you whether a dereference is sound?

<details markdown="1"><summary>Check</summary>

No. Soundness lives in the argument the block's author made, typically as a `SAFETY:` comment, not in the pointer's type, which looks identical whether the invariant holds or not. Checking that argument by eye does not scale, which is the gap this lesson's tool closes.

</details>

## Know this

### An interpreter, not a linter

Miri is not a linter reading your source for suspicious patterns. It executes the compiler's own mid-level intermediate representation, one operation at a time, checking each against the rules a real execution must obey: is this access in bounds, is this value initialised, does this borrow still hold its place. Its own documentation is direct: "Miri is an Undefined Behavior detection tool for Rust. It can run binaries and test suites of cargo projects and detect unsafe code that fails to uphold its safety requirements." Running a program under Miri is running it for real, watched every step, which is why it costs real time instead of being instant like a lint.

That machinery is not on the stable toolchain: **Miri requires a nightly toolchain installed alongside stable**. Install it once:

```
rustup toolchain install nightly --component miri
```

Invoke it with `cargo +nightly miri run` or `cargo +nightly miri test`, leaving your default toolchain on stable. Everything this stage teaches, every `unsafe` block included, still compiles on stable rustc 1.98.0. Verified here on rustc 1.100.0-nightly. Both examples below could be written safely in one line each, a plain `&mut x` for the first and an `Arc<Mutex<u32>>` for the second; they reach for a raw pointer instead, on purpose, so their `unsafe` blocks promise nothing beyond that honesty, existing only to give Miri something real to catch.

### The aliasing violation stable ran happily

Two overlapping `&mut` values, dereferenced from the same raw pointer, break the rule that a unique borrow tolerates no other live access to the same memory:

```rust
let mut x: u32 = 42;
let p: *mut u32 = &mut x;
unsafe {
    // SAFETY: this is deliberately unsound, to see what Miri says about it.
    let a = &mut *p;
    let b = &mut *p;
    *b = 2;
    let v = *a;
    println!("{}", v);
}
```

Run on stable release five times, this printed `2` every time: five of five looked fine. Under `cargo +nightly miri run`, the binary never gets past that print:

```text
error: Undefined Behavior: attempting a read access using <588> at alloc210[0x0], but that tag does not exist in the borrow stack for this location
 --> src/main.rs:9:17
  |
9 |         let v = *a;
  |                 ^^ this error occurs as part of an access at alloc210[0x0..0x4]
  |
  = help: this indicates a potential bug in the program: it performed an invalid operation, but the Stacked Borrows rules it violated are still experimental
  = help: see https://github.com/rust-lang/unsafe-code-guidelines/blob/master/wip/stacked-borrows.md for further information
help: <588> was created by a Unique retag at offsets [0x0..0x4]
 --> src/main.rs:6:17
  |
6 |         let a = &mut *p;
  |                 ^^^^^^^
help: <588> was later invalidated at offsets [0x0..0x4] by a Unique retag
 --> src/main.rs:7:17
  |
7 |         let b = &mut *p;
  |                 ^^^^^^^

error: aborting due to 1 previous error
```

(An absolute path to Miri's runner binary, printed just before this, is trimmed here and below.) `a` gets unique access at line 6, `b` claims the same access at line 7 and invalidates it, and the read through `a` at line 9 is where that dead permission gets used. Stable checks none of this.

### The data race that won six out of six

Two scoped threads each add one to a shared `u32` a thousand times, nothing serialising the two loops:

```rust
#[derive(Clone, Copy)]
struct SendPtr(*mut u32);
// SAFETY: this is deliberately unsound, to see what Miri says about it.
unsafe impl Send for SendPtr {}

fn racy_increment() -> u32 {
    let mut total: u32 = 0;
    let shared = SendPtr(&mut total);
    std::thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(move || {
                let shared = shared;
                let p = shared.0;
                for _ in 0..1000 {
                    // SAFETY: this is deliberately unsound, to see what Miri says about it.
                    unsafe { *p += 1; }
                }
            });
        }
    });
    total
}
```

Six runs of the release binary printed `2000` every time: easy to mistake for proof the racing writes are harmless. Wrapped as a test and run with `cargo +nightly miri test`, the same code never reaches a verdict:

```text
running 1 test
test tests::totals_two_thousand ... error: Undefined Behavior: Data race detected between (1) non-atomic write on thread `unnamed-2` and (2) non-atomic read on thread `unnamed-3` at alloc41867
 --> src/main.rs:21:25
   |
21 |                         *p += 1;
   |                         ^^^^^^^ (2) just happened here
   |
help: and (1) occurred earlier here
 --> src/main.rs:21:25
   |
21 |                         *p += 1;
   |                         ^^^^^^^
   = help: this indicates a bug in the program: it performed an invalid operation, and caused Undefined Behavior
   = help: see https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html for further information

error: aborting due to 1 previous error
```

Access (2) is the read half of an increment on one thread; access (1) is the write half on the other: the same unsynchronised `+= 1` racing itself. Six clean runs said nothing, since a right total is easy to hit by luck when both threads do identical arithmetic.

### What a clean run does not license

A pass under Miri is evidence, not proof. Its own documentation draws the line: "Miri fundamentally cannot ensure that your code is *sound*... Miri can just tell you if *a particular way of interacting with your code* (e.g., a test suite) causes any undefined behavior *in a particular execution*... When Miri finds UB, your code is definitely unsound, but when Miri does not find UB, then you may just have to test more inputs or more possible non-deterministic choices." Four limits follow. It only checks paths a run takes, so an untested `unsafe` branch is never examined: its coverage is your tests'. It is far slower, every operation interpreted rather than compiled: a suite with no `unsafe` at all took `cargo +nightly miri test` roughly three and a half times as long as plain `cargo test`, one machine, one workload, finding nothing new. It cannot see foreign functions, since it runs as a platform-independent interpreter with no access to most platform-specific APIs or FFI. And its aliasing rules are, in its own words, "**Experimental**: Violations of the Stacked Borrows rules governing aliasing for reference types." A clean run says this execution hit no undefined behaviour it knows how to detect, not that the function is sound for every caller.

### Running it usefully

`cargo miri test` matters day to day, since it drives tests you already have rather than throwaway programs written just for Miri. `MIRIFLAGS="-Zmiri-many-seeds=0..N"` reruns a test under several random schedules and allocation layouts, since one run is only one interleaving; against the data race test above, seed 0 alone failed, since a thousand unsynchronised increments per thread leaves little room for the two accesses to never coincide. This is also the flag lesson 51 leans on, for a rarer failure. `-Zmiri-disable-isolation` turns off Miri's default host sandboxing, which otherwise fakes clocks, environment variables and randomness, trading determinism for real host access when a test needs it. Run it on the test suite, not as an occasional command, and put it in continuous integration beside the normal test job, pointed at the crate that actually contains `unsafe` rather than the whole dependency tree: a crate with none of its own gains little, exactly what the run above showed.

### Tree Borrows against Stacked Borrows

Stacked Borrows is Miri's default aliasing model; Tree Borrows is a second, more permissive one, selectable with `-Zmiri-tree-borrows`, called by Miri's own documentation "even more experimental than Stacked Borrows." The two do not always agree, so a program accepted under one is not automatically sound under the other. Tested against this lesson's examples: the overlapping-`&mut` violation is rejected by both, Tree Borrows naming the fault in its own vocabulary, a tag moving to `Disabled`, which forbids the read. The fixed version, borrows no longer overlapping, is accepted by both. Both agreed here; splits exist elsewhere, this lesson just did not turn one up.

## Practice

1. ▢ Predict whether deleting the `// SAFETY:` comment changes what `rustc` or Miri reports about the aliasing example, then delete it and check.

<details markdown="1"><summary>Check</summary>

Nothing changes: the comment is documentation for the reader, not something either tool parses, so removing it removes a promise, not the bug.

</details>

2. ▢ Predict whether moving the read through `a` before `b` is created, so the borrows never overlap, still trips Miri, then edit and rerun.

<details markdown="1"><summary>Hint</summary>

The report names a permission invalidated and then used afterwards; a use strictly before the invalidation was never at issue.

</details>

<details markdown="1"><summary>Check</summary>

Clean, printing the same value stable already printed: `a`'s permission is only invalidated when `b` is created, and by then `a` was already read, so there is no later use of a dead permission to catch.

</details>

3. ▢ Predict whether two threads that only read a shared pointer, never writing, are flagged as a race, then adapt the increment example to read and accumulate, and check under Miri.

<details markdown="1"><summary>Hint</summary>

The original report named two accesses, one write and one read. A race needs at least one of those.

</details>

<details markdown="1"><summary>Check</summary>

Clean: a race needs a conflicting access, and two concurrent reads never conflict, so there is nothing to name.

</details>

4. ▢ Predict whether item 2's fixed example is still accepted under `MIRIFLAGS="-Zmiri-tree-borrows" cargo +nightly miri run`, then check.

<details markdown="1"><summary>Check</summary>

Still accepted, printing the same value: this program has nothing for either model to object to, so the two agree here even though they are free to disagree elsewhere.

</details>

5. ▢ A judgement call, not a compile check: for each claim, say whether a clean `cargo +nightly miri test` run licenses it.

   a) A crate with no `unsafe` runs clean, so the team concludes its dependencies must be sound too.
   b) A function with one `unsafe` block runs clean on its tests, so the team concludes it is sound for every input it could receive.
   c) The same function runs clean across a range of seeds under `-Zmiri-many-seeds`, and the team notes only that those schedules turned up nothing.

<details markdown="1"><summary>Check</summary>

a) Overreach: Miri only interprets the paths the tests take, so a dependency's unsafe code is checked only as far as those tests exercise it, never as a guarantee about the dependency. b) Overreach, for the reason lesson 48 and this lesson both stress: a clean run covers the inputs the tests fed it, not every input the function could see. c) Accurate: this is what a seed sweep supports, breadth of choices tried, not proof no bad schedule exists.

</details>

## Real-world reps

- [ ] Run `cargo +nightly miri test` against your project's test suite at stage 6's end, and record whether it found anything, and roughly how long it took relative to plain `cargo test`, as a ratio.
- [ ] If your stage 5 rep summarises files using threads, rerun that test under `MIRIFLAGS="-Zmiri-many-seeds=0..16" cargo +nightly miri test`, and note whether every seed agreed.
- [ ] Tomorrow: pick a dependency you know contains `unsafe`, and check whether its tests run under Miri in continuous integration; if not, decide what that changes about how much you trust it.

## Going further

- [Toolchains](https://rust-lang.github.io/rustup/concepts/toolchains.html): how rustup keeps nightly alongside stable
- [Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html): the Reference's list of what Miri checks against
- [Stacked Borrows](https://github.com/rust-lang/unsafe-code-guidelines/blob/master/wip/stacked-borrows.md): the model Miri's default report cites
- [Tree Borrows](https://plf.inf.ethz.ch/research/pldi25-tree-borrows.html): the alternative model, from the group that designed it
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
