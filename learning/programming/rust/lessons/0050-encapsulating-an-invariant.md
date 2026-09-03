---
title: 50. Encapsulating an Invariant
description: Wrapping unsafe code in a safe interface, and what has to be true for that interface to deserve the name
type: lesson
---

# Lesson 50. Encapsulating an Invariant

**Mission link:** Lesson 49 gave you a tool that can say a program has undefined behaviour but never that it does not; this lesson gives you the discipline that makes an `unsafe` block worth shipping, which is the one thing Miri cannot check for you.
**Primary source:** [Working with Unsafe](https://doc.rust-lang.org/nomicon/working-with-unsafe.html)
**Prerequisites:** [Lesson 49](0049-checking-with-miri.md), [Lesson 25](0025-implementing-traits-you-do-not-own.md)

## Warm-up

1. ▢ Lesson 49's data race printed the correct total in six release runs out of six before Miri was asked, and Miri still called it undefined behaviour. If a hand-written `unsafe` function passes every test in its suite ten times over, what has that proven about whether it is sound?

<details markdown="1"><summary>Check</summary>

Nothing on its own. A passing run shows only that the inputs you tried did not trigger the failure you have; it says nothing about inputs you did not try or checks you never ran. Soundness is a claim about every caller, not the ones you happened to write.

</details>

2. ▢ Lesson 25 explained why the orphan rule stops you implementing a foreign trait for a foreign type from outside its crate. What is that rule protecting?

<details markdown="1"><summary>Check</summary>

It stops an impl the type's own author never accounted for from appearing behind their back, one that could contradict an invariant the rest of their crate relies on. This lesson leans on the same idea the other way round: keeping a struct's fields private is what lets its author guarantee something no outside caller can violate.

</details>

## Know this

### The contract, stated precisely

Split a mutable slice into two halves using only what earlier stages taught, and the borrow checker refuses:

```text
error[E0499]: cannot borrow `*r` as mutable more than once at a time
 --> examples/naive.rs:5:18
  |
4 |     let a = &mut r[..3];
  |                  - first mutable borrow occurs here
5 |     let b = &mut r[3..];
  |                  ^ second mutable borrow occurs here
  |
  = help: use `.split_at_mut(position)` to obtain two mutable non-overlapping sub-slices
```

The two halves never overlap, so the rejection is a limit of the checker's reasoning, not a real hazard, and rustc's own `help` names the escape hatch: a safe function with `unsafe` code inside it. The Rustonomicon states what such a function has to promise: "we say that such a correct unsafely implemented function is sound, meaning that safe code cannot cause Undefined Behavior through it (which, remember, is the single fundamental property of Safe Rust)". That is stronger than "it works": no caller, however careless, can reach undefined behaviour through the safe signature exposed, and that alone is what makes an `unsafe` block acceptable in code other people call without reading its body.

### Building `split_at_mut`, with its invariant named

The safe signature promises nothing unusual: `pub fn split_at_mut<T>(slice: &mut [T], mid: usize) -> (&mut [T], &mut [T])`. Nothing about it says `unsafe`, and any slice and any `usize` gets back two ordinary mutable slices or a panic, never undefined behaviour. A single check before the pointer work makes that promise keepable:

```rust
pub fn split_at_mut<T>(slice: &mut [T], mid: usize) -> (&mut [T], &mut [T]) {
    let len = slice.len();
    assert!(mid <= len, "mid out of bounds");
    let ptr = slice.as_mut_ptr();
    // SAFETY: `mid <= len` was just checked, so both `ptr` (for `mid`
    // elements) and `ptr.add(mid)` (for `len - mid` elements) stay within
    // the single allocation backing `slice`. The ranges [0, mid) and
    // [mid, len) do not overlap, so the two `&mut [T]` this produces never
    // alias each other, and neither aliases anything else because `slice`
    // was borrowed uniquely for the whole function.
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

The `SAFETY:` comment names the fact that makes the two `from_raw_parts_mut` calls sound: the ranges are disjoint. Boundaries are what a reader should not have to take on faith, so the tests cover `mid` of zero, `mid` equal to the slice's own length, an empty slice, and that both halves are independently writable.

```text
running 6 tests
test tests::both_halves_are_independently_writable ... ok
test tests::empty_slice_mid_zero ... ok
test tests::mid_at_len_gives_an_empty_right_half ... ok
test tests::mid_past_len_panics - should panic ... ok
test tests::mid_zero_gives_an_empty_left_half ... ok
test tests::splits_in_the_middle ... ok

test result: ok. 6 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

`cargo +nightly miri test` on the same six is where the claim earns its name rather than just sounding plausible: all six still say `ok`, and Miri raised nothing.

### Then break it, on purpose

Delete the one line that does the checking:

```rust
pub fn split_at_mut_unchecked<T>(slice: &mut [T], mid: usize) -> (&mut [T], &mut [T]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    // SAFETY: not sound -- with the assertion deleted, nothing guarantees `mid <= len`,
    // so a caller passing a larger `mid` gets a slice over memory this one never owned.
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

The same five non-panicking tests still all say `ok`: deleting the check breaks nothing a valid caller was doing, because none of those tests ever pass a `mid` greater than the length. That is the trap in one sentence: "the tests still pass" describes the inputs the tests chose, not the function. Calling it with a `mid` past the end looks fine too, at first. A debug build's overflow check gets there first, panicking with `attempt to subtract with overflow` on `len - mid`, three times out of three, before the unsafe code runs, a different mechanism catching a different symptom, not evidence of soundness. A release build has that check compiled out, and that is the fair test: five runs out of five, `len` five and `mid` seven, printed
```text
a.len() = 7, first = 1
b.len() = 18446744073709551614
```
without crashing or warning. Only then does Miri speak:
```text
error: Undefined Behavior: constructing invalid value of type &mut [i32]: encountered a dangling reference (going beyond the bounds of its allocation)
  --> src/lib.rs:30:13
   |
30 |             std::slice::from_raw_parts_mut(ptr, mid),
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
   |
   = help: this indicates a bug in the program: it performed an invalid operation, and caused Undefined Behavior
```
Five clean release runs, zero warnings, one Miri run, one diagnosis, at the very first line of pointer work.

### What a sound boundary needs

Five things, applied to `split_at_mut` rather than left abstract. Every input validated or documented as a requirement: `mid` is checked by the `assert!`, and `slice` already carries its own validity as an ordinary `&mut [T]`, leaving nothing else to check. No way for a safe caller to violate the invariant: the signature accepts only a slice and a `usize`, and every `usize` either passes the check or panics, so nothing reaches the unsafe code with `mid > len`. The invariant written down: the `SAFETY:` comment above, naming disjointness rather than gesturing at "this is fine". Panics considered: the `assert!` runs before either raw pointer is touched, so it unwinds a function with nothing yet for a destructor to see, leaving the original slice untouched. The type's own destructor considered: `split_at_mut` never takes ownership of `T` and never drops anything, it only reborrows, so there is no destructor interaction here, and saying so is part of the argument rather than a step to skip.

### The types that exist because of this

Four standard-library types exist so a reader encapsulating an invariant is not starting from raw pointers alone. `UnsafeCell<T>` is described as "the core primitive for interior mutability in Rust": the compiler optimises through a shared reference on the assumption that nothing behind it changes, and `UnsafeCell` is the single legal way to opt out of that assumption, which is what every `Cell`, `RefCell`, `Mutex` and atomic type is built from underneath. `NonNull<T>` guarantees its pointer is never null, and a compiled check confirms that buys something concrete:

```rust
assert_eq!(
    std::mem::size_of::<NonNull<u8>>(),
    std::mem::size_of::<Option<NonNull<u8>>>()
);
```

That holds because the niche the null value would otherwise occupy is free for `Option` to use, so a pointer promising never to be null costs nothing over the raw one. `MaybeUninit<T>` guarantees the compiler will not assume the bits inside it are a valid `T` until told otherwise, and its size matches `T` exactly, confirmed the same way: a permission slip, not extra storage. `ManuallyDrop<T>` guarantees the same layout as `T` while switching off its destructor, verified the same way again, the building block behind handing a value's ownership to unseen code, a raw allocator or a foreign function, without it being dropped twice. Each of these already carries a soundness argument a reader would otherwise write from nothing.

### When to stop

Most `unsafe` in application code should be deleted, not encapsulated. A slice that needs splitting almost never needs a hand-written `unsafe fn`, because the standard library, or a well-used crate, has usually already done this lesson's work with more scrutiny than one afternoon affords. Before writing a `SAFETY:` comment, apply one test: can the invariant it names be stated in a single sentence? `split_at_mut`'s is "the two ranges never overlap". If the honest answer runs to a paragraph, with exceptions, that is a hope, not an invariant, and the fix is to keep looking for the safe version rather than keep writing the comment.

## Practice

1. ▢ Predict whether the two-borrow attempt at the top of this lesson compiles, then try it.

<details markdown="1"><summary>Hint</summary>

The checker sees one slice borrowed twice; it cannot see that `[..3]` and `[3..]` never touch the same element.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile: `E0499`, "cannot borrow `*r` as mutable more than once at a time", and rustc's own `help` names `split_at_mut`, the function this lesson just built by hand.

</details>

2. ▢ Predict what `cargo +nightly miri test` reports for the six tests against the checked `split_at_mut`, then run it.

<details markdown="1"><summary>Check</summary>

All six report `ok`, same as plain `cargo test`, because the `assert!` rules out the one input that would make the pointer arithmetic invalid, leaving Miri nothing to object to.

</details>

3. ▢ Delete the `assert!` line, rerun the five tests that never pass an out-of-range `mid`, and predict whether any of them notice.

<details markdown="1"><summary>Hint</summary>

None of those five tests were written to catch this particular deletion.

</details>

<details markdown="1"><summary>Check</summary>

All five still say `ok`. Deleting the bounds check breaks nothing those tests exercise, which is exactly the trap: a green suite tells you about the inputs it contains, not about the function.

</details>

4. ▢ Call the unchecked version with a slice of length five and `mid` of seven, predict whether a `--release` build crashes, then run it under `cargo +nightly miri run` and compare.

<details markdown="1"><summary>Check</summary>

A `--release` build does not crash: it prints a plausible length for one half and an enormous wrapped length for the other, five times out of five. Miri refuses at the first `from_raw_parts_mut` call, with "constructing invalid value of type `&mut [i32]`: encountered a dangling reference (going beyond the bounds of its allocation)", before the second half's arithmetic even runs.

</details>

5. ▢ A judgement call, not a compile check: a colleague's `unsafe fn` bounds-checks every argument, has a `SAFETY:` comment naming its invariant, and takes ownership of a `Vec<T>` internally without saying what happens to it. Which checklist item is missing?

<details markdown="1"><summary>Check</summary>

The destructor was not considered. Validation and the invariant's own statement are both present, but owning a `Vec<T>` means something must happen to it, dropped, forgotten or handed elsewhere, and the checklist asks for that to be an explicit decision, not a silent default.

</details>

## Real-world reps

- [ ] In your project's summariser, wherever a buffer of lines is split across worker threads (see `../reference/the-project.md`), replace any manual index arithmetic with the standard library's own `split_at_mut`, and write beside the call, as a comment, the invariant it enforces on your behalf: the two halves never overlap, so both threads can hold one at once without a lock.
- [ ] Take `split_at_mut` from this lesson, or any small `unsafe` function you already wrote, and run its tests twice, once with its bounds check intact and once with it deleted, under both a normal build and `cargo +nightly miri test`; note which single combination actually tells the two apart.
- [ ] Tomorrow: pick one `unsafe` block already in your own code, or one you were tempted to write, and apply this lesson's test by writing its invariant in one sentence; if you cannot, lesson 54 is where you learn to say so out loud in review.

## Going further

- [Working with Unsafe](https://doc.rust-lang.org/nomicon/working-with-unsafe.html): this lesson's soundness contract, quoted above
- [std::cell::UnsafeCell](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html): the primitive every interior-mutability type is built on
- [std::ptr::NonNull](https://doc.rust-lang.org/std/ptr/struct.NonNull.html): the non-null, covariant pointer used throughout the standard library's own unsafe code
- [std::mem::MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html): uninitialised memory made explicit instead of implicit
- [std::mem::ManuallyDrop](https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html): suppressing a destructor without changing layout
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
