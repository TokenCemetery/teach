---
title: 54. Defending an Unsafe Boundary
description: The argument you have to be able to make before an unsafe block ships, and the measurement that has to come with it
type: lesson
---

# Lesson 54. Defending an Unsafe Boundary

**Mission link:** A reviewer who cannot answer five specific questions about an `unsafe` block should not approve it, and a speed claim without a ratio, a workload and a kept safe comparison should not survive review either: the same discipline, applied to the two reasons `unsafe` code ships.
**Primary source:** [Working with Unsafe](https://doc.rust-lang.org/nomicon/working-with-unsafe.html)
**Prerequisites:** [Lesson 50](0050-encapsulating-an-invariant.md), [Lesson 53](0053-allocation-and-copying-costs.md)

## Warm-up

1. ▢ Lesson 51's message-passing example read the published value in five of five release runs. What did the thirty-seed Miri sweep find that those runs could not?

<details markdown="1"><summary>Check</summary>

Fourteen of the thirty seeds under `-Zmiri-many-seeds=0..30` read the stale zero a `Relaxed` store allows. Ordinary runs, even ordinary Miri runs, only exercise one schedule; the sweep turns "it worked" into a count of how often it does not.

</details>

2. ▢ Lesson 52 forbids ever publishing a duration for a performance claim. What must the ratio be stated together with instead, and why does a bare duration fail to travel?

<details markdown="1"><summary>Check</summary>

What it is a ratio of, plus the fact that it came from one machine and one workload. A duration alone is somebody's clock speed and cache sizes wearing a number, meaningless elsewhere; a ratio on a stated workload at least says how much one choice cost relative to the other, wherever it is reproduced.

</details>

## Know this

### 1. The five questions, asked in order

Lesson 46 named what `unsafe` is: a promise to the compiler that a property it can no longer check still holds, not a switch turning the property off. Reviewing a block reconstructs that promise by hand, in five questions: what invariant makes this sound, who guarantees it, can a safe caller break it, what happens if the code inside panics, and what the measurement says it bought. A block failing any of the first four never reaches the fifth; no ratio buys back an invariant that was never true. Lesson 48's aliasing example fails at question one:

```rust
let mut x = 0u32;
let p: *mut u32 = &mut x;
// SAFETY: none. There is no invariant to write here, which is the point.
unsafe {
    let r1 = &mut *p;
    let r2 = &mut *p;
    *r1 += 1;
    *r2 += 1;
}
```

There is no invariant to state: the rule this block should uphold, one live `&mut` per location, is what its own two lines break. Question three's answer is worse than yes: no safe caller is even needed, since the block manufactures both aliases itself. Miri agrees:

```text
error: Undefined Behavior: attempting a read access using <588> at alloc219[0x0], but that tag does not exist in the borrow stack for this location
 --> src/main.rs:7:9
  |
7 |         *r1 += 1;
  |         ^^^^^^^^ this error occurs as part of an access at alloc219[0x0..0x4]
  |
  = help: this indicates a potential bug in the program: it performed an invalid operation, but the Stacked Borrows rules it violated are still experimental
  = help: see https://github.com/rust-lang/unsafe-code-guidelines/blob/master/wip/stacked-borrows.md for further information
help: <588> was created by a Unique retag at offsets [0x0..0x4]
 --> src/main.rs:5:18
  |
5 |         let r1 = &mut *p;
  |                  ^^^^^^^
help: <588> was later invalidated at offsets [0x0..0x4] by a Unique retag
 --> src/main.rs:6:18
  |
6 |         let r2 = &mut *p;
  |                  ^^^^^^^
```

Question two is what a passing block still owes: who guarantees the invariant question one named. Lesson 48's data race answers it the hard way: two threads incrementing a shared `*mut u32` a thousand times each printed the right total in six of six stable runs, and nothing guaranteed exclusive access, which a clean run cannot reveal and Miri's detector can. Lesson 50's encapsulation answers it the easy way: a private field plus one constructor moves the guarantee inside the type, not into every caller's memory. Question four, what a panic does to the invariant, earns its own worked failure below.

### 2. The measurement requirement, with teeth

An `unsafe` block justified by speed needs a before-and-after ratio, a described workload, and the safe version kept in the crate, the discipline lessons 52 and 53 used with `criterion`. The project's per-line parser is the worked case; the safe version splits on a general pattern:

```rust
let mut parts = line.split(' ');
let path = parts.next().ok_or(ParseErr::Malformed)?;
let status: u16 = parts.next().ok_or(ParseErr::Malformed)?.parse().map_err(|_| ParseErr::BadNumber)?;
```

The unsafe version scans for the same two spaces itself:

```rust
// SAFETY: every index handed to `get_unchecked` is bounded by `i < len` in
// the loop that produced it, so it never reaches or passes `len`. Every
// split point is the byte offset of an ASCII space, and slicing a valid
// UTF-8 str at a single-byte ASCII boundary always leaves both halves
// valid UTF-8, so `from_utf8_unchecked` reconstructs a real str rather
// than an arbitrary byte range.
let mut i = 0;
while i < len && unsafe { *bytes.get_unchecked(i) } != b' ' { i += 1; }
let path = unsafe { std::str::from_utf8_unchecked(bytes.get_unchecked(0..i)) };
```

Before that, the honest middle step is a safe rewrite with `split_once`, the third of the next section's four alternatives answered early. Measured three times on one machine, over a two-thousand-line workload split evenly between request lines, notes and blank lines, original version kept for comparison: `split_once` alone was about 1.1 to 1.4 times faster (1.14, 1.37, 1.23), and the unsafe scan a further, more consistent 1.36 to 1.42 times faster on top (1.38, 1.36, 1.42). Multiplied through, unsafe was about 1.6 to 1.9 times faster than the start (1.57, 1.86, 1.74). No duration appears here, only ratios and the workload behind them.

### 3. A review that catches a panic-shaped hole

Question four rarely shows up in the block itself; it shows up in what the block promised before a wrapped call could fail. A fixed-capacity buffer whose invariant is "the first `len` slots hold initialised values" breaks that promise from a single reordering:

```rust
pub fn push_bad<F: FnOnce() -> u8>(&mut self, f: F) {
    assert!(self.len < N, "buffer full");
    self.len += 1;
    let slot = &mut self.data[self.len - 1];
    slot.write(f());
}
```

Reviewer: "what happens if `f` panics?" Author: "`len` only grows once a slot is pushed." Reviewer: "it grows before the write; what does `len` count if `f` panics there?" That is the hole: a slot the invariant claims is initialised, and is not. Run directly it can look fine, since reading uninitialised memory as a plain integer often reads whatever garbage byte the stack held: one real push, then a panicking, caught second push, printed a plausible total in five of five stable runs, another clean run proving nothing. Under Miri, trimmed to the lines carrying the teaching:

```text
error: Undefined Behavior: constructing invalid value of type u8: encountered uninitialized memory, but expected an integer
   --> src/lib.rs:145:31
    |
145 |             total += unsafe { self.data[i].assume_init() } as u32;
    |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
    |
    = help: this indicates a bug in the program: it performed an invalid operation, and caused Undefined Behavior
    = help: see https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html for further information
```

The fix moves the increment after the write, so a panic in `f` leaves `len` exactly where it was before the call:

```rust
pub fn push_good<F: FnOnce() -> u8>(&mut self, f: F) {
    assert!(self.len < N, "buffer full");
    let value = f();
    let slot = &mut self.data[self.len];
    slot.write(value);
    self.len += 1;
}
```

Nothing about the invariant changed, only the order of two already-correct-looking lines, exactly "the fundamental problem of safety" the primary source opens with: indexing a slice with `<= arr.len()` instead of `< arr.len()` turns a sound `get_unchecked` unsound without touching the `unsafe` block, because soundness depends on state ordinary safe code established elsewhere.

### 4. When unsafe is the wrong answer

Four alternatives earn a try first: a different data structure avoiding the problem, a crate that already encapsulated the same unsafety behind a safe API, a safe standard-library method nobody had looked for, or accepting the cost once a measurement says it does not matter. The parser above used the third: `split_once` was there the whole time. The second was also available, and probably better: `memchr` does exactly this byte scan behind a safe function, tuned harder than a first attempt. A 2023 study manually inspecting 5946 `unsafe` blocks across 140 popular libraries reported: "The study unveils hundreds of instances of unnecessary unsafe Rust code". That is not quite the tidier claim that most application `unsafe` gets deleted rather than fixed, and this will not repeat a number it cannot show fetched and matched, but it argues the same point: asking these four questions first removes most candidates before they exist.

### 5. What to write down, and what the project needed

Four things earn their place next to an `unsafe` block: the `SAFETY:` comment stating the invariant, a module-level note when it spans more than one function, a test exercising ordinary and would-be-violating conditions, and a Miri run in continuous integration checking all of it on every change. The comment is the one people write, since review habitually asks for it; the Miri run in CI is the one people skip, since it is slow and nothing invites it back the way a missing comment does. Lesson 49 already showed the cost: a stable run and a Miri run can disagree, and only one checks the property that matters. This stage's closing claim is that `unsafe` and performance are one subject, since the commonest reason `unsafe` shows up in application code is speed nobody measured. The project's own answer, now measured, is a genuine faster path: `split_once` ships regardless, and the further unsafe scan earned its place by clearing all four questions first, backed by a Miri run over the same cases and the safe version kept for the next comparison.

## Practice

1. ▢ Predict which of the five questions the aliasing example above fails first, before rereading the answer.

<details markdown="1"><summary>Check</summary>

Question one: there is no invariant it upholds, since its own two lines create the very violation the aliasing rule exists to prevent. Everything after that question is academic once the first has no answer.

</details>

2. ▢ `push_bad` looked correct to its author. Predict what five stable runs print for one successful push then one panicking one, then say what Miri adds.

<details markdown="1"><summary>Hint</summary>

Ask what "uninitialised" means on stable versus under Miri.

</details>

<details markdown="1"><summary>Check</summary>

Stable prints a plausible total each time, since the uninitialised byte often reads as something small rather than crashing. Miri reports `constructing invalid value of type u8: encountered uninitialized memory, but expected an integer`, which five clean runs never surface.

</details>

3. ▢ A colleague argues `split_once` already captured the whole win, so the unsafe scan on top is not worth keeping. Using this lesson's ratios, is that correct?

<details markdown="1"><summary>Check</summary>

No. `split_once` was about 1.1 to 1.4 times faster than the original, but the unsafe scan added a further, more consistent 1.36 to 1.42 times on top, about 1.6 to 1.9 times over the start. The safe rewrite captured real gain, not all of it.

</details>

4. ▢ Loosen the scan's `while i < len` to `while i <= len`, the primary source's own `<=` mistake. Predict whether an ordinary line still looks fine, then what a spaceless line does on a debug build.

<details markdown="1"><summary>Hint</summary>

The loop only reaches `i == len` when the byte it wants never appears.

</details>

<details markdown="1"><summary>Check</summary>

An ordinary line never needs `i` to reach `len`, so nothing looks wrong. A spaceless line does, and `get_unchecked(len)` there is one past the end: a debug build panics with `unsafe precondition(s) violated: slice::get_unchecked requires that the index is within the slice`, since stable now checks that itself; release has no such guard and is genuinely undefined.

</details>

5. ▢ A block indexes with `get_unchecked` guarded by a bounds check three functions away, invisible in the reviewed diff. Which question does this fail, and what does the primary source call the property behind it?

<details markdown="1"><summary>Check</summary>

Question three: a guard three functions away is the non-local dependency the source describes, soundness resting on state that unrelated, ordinary-looking safe code established.

</details>

## Real-world reps

- [ ] Apply the five questions out loud to every `unsafe` block your project has added since lesson 46, deleting any that fails question one, two or three rather than patching it.
- [ ] Benchmark your project's per-line parsing against a safe rewrite and, if worth trying, a small unsafe variant, over a workload described in words; write the ratios beside a decision either way, as this lesson's project note does.
- [ ] Tomorrow: add your project's Miri run to whatever runs before a change counts as finished, so it survives past today.

## Going further

- [Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html): the Reference's list of what soundness rules out
- [criterion](https://docs.rs/criterion/0.8.2/criterion/): the benchmarking crate behind every ratio in this stage
- [Miri](https://github.com/rust-lang/miri): the interpreter behind the review walkthrough's UB report
- [On the Dual Nature of Necessity in Use of Rust Unsafe Code](https://dl.acm.org/doi/10.1145/3611643.3613878): the study behind this lesson's statistic on unnecessary unsafe
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
