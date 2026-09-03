---
title: 48. Undefined Behaviour
description: What the compiler is allowed to assume, why a program that works can still be wrong, and the list worth knowing by heart
type: lesson
---

# Lesson 48. Undefined Behaviour

**Mission link:** Lesson 47 showed how to build a raw pointer without a compiler complaint. This lesson is the list of everything it can still get wrong, because a clean compile and a correct-looking run are not evidence that either is sound.
**Primary source:** [Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)
**Prerequisites:** [Lesson 47](0047-raw-pointers.md), [Lesson 34](0034-send-and-sync.md)

## Warm-up

1. ▢ Lesson 47 showed a raw pointer dereferences with no complaint from the borrow checker, whatever it points at. If that pointer's target has already been freed, does dereferencing it produce an error, or does the result depend on what occupies that memory now?

<details markdown="1"><summary>Check</summary>

Nothing forces an error; the memory might hold the old bytes, something else, or a different allocation, so the result is whatever the hardware hands back, not a guaranteed failure, which is why a sensible-looking number is not a correct one.

</details>

2. ▢ Lesson 34 showed a raw pointer is not `Send` by default, so moving one to another thread needs an explicit unsafe promise. If a program casts a `*mut u32` to a `usize`, hands it to two threads, and casts it back to a pointer in each, has it satisfied the promise `Send` protects, or only got past the compiler?

<details markdown="1"><summary>Check</summary>

Only got past the compiler: the round trip is `Send` because integers always are, but nothing proves the two threads' accesses are synchronised, so the property `Send` stands for is assumed, not shown, and this lesson's data race demonstration is that assumption failing.

</details>

## Know this

### A broken premise, not a random result

Undefined behaviour is not a vague warning that a result is unpredictable; the Reference says exactly what it is: "Rust code is incorrect if it exhibits any of the behaviors in the following list." This applies inside `unsafe` too; it only moves the proof onto the author. The optimiser assumes none of this list ever happens, so once it does, every transformation performed under that false assumption stays correct relative to it, and the effect can surface anywhere the optimiser touched. The Reference names what this protects: "if unsafe code can be misused by safe code to exhibit undefined behavior, it is unsound."

### The list, from the page

The page warns this list "is not exhaustive", but seven entries are worth holding by name, two of them bundled into one bullet: "Accessing (loading from or storing to) a place that is dangling or based on a misaligned pointer", dangling meaning the bytes are not part of any live allocation, misaligned meaning they are, just not at an address that type may start from. A third and fourth are "Breaking the pointer aliasing rules" and "Data races", covered below. A fifth is "Producing an invalid value", such as a `bool` that is not `false` or `true`. A sixth is provenance, a pointer's extra information beyond its address, broken by "transmuting or otherwise reinterpreting a pointer ... into a non-pointer type ... is undefined behavior if the pointer had provenance", whose page example refuses to compile:

```rust
const _: usize = {
    let ptr = &0;
    // SAFETY: not sound -- reinterpreting a pointer's bytes as an integer
    // discards provenance, which is exactly the rule this violates.
    unsafe { (&raw const ptr as *const usize).read() }
};
```

```text
error[E0080]: unable to turn pointer into integer
  = help: the absolute address of a pointer is not known at compile-time, so such operations are not supported
```

A seventh is "Calling a function with the wrong call ABI", including a transmuted function pointer called through the wrong signature. Safe Rust never allows two `&mut` to one value; aliasing fails the same way through a raw pointer:

```rust
let mut x: u32 = 10;
let p: *mut u32 = &mut x;
unsafe {
    // SAFETY: not sound -- r1 and r2 alias the same &mut, which is exactly
    // what the pointer aliasing rule forbids.
    let r1 = &mut *p;
    let r2 = &mut *p;
    *r1 += 1;
    *r2 += 1;
    println!("x = {}", x);
}
```

Stable printed the arithmetically correct `x = 12` in five of five runs. Miri:

```text
error: Undefined Behavior: attempting a read access using <588> at alloc219[0x0], but that tag does not exist in the borrow stack for this location
help: <588> was created by a Unique retag at offsets [0x0..0x4]
help: <588> was later invalidated at offsets [0x0..0x4] by a Unique retag
```

Miri calls the rule it checked "still experimental"; the violation is real regardless.

### The data race that never failed

The clearest entry on this list is a data race, because here a correct answer is the expected outcome, not a lucky one. Stage 5's safe design for a shared counter is `Arc<Mutex<u32>>` or a channel; this routes around both. Two scoped threads, sharing an address cast through a `usize` as the warm-up described, increment a `u32` a thousand times each, no lock or atomic:

```rust
let mut counter: u32 = 0;
let p: *mut u32 = &mut counter;
let shared = p as usize;
std::thread::scope(|s| {
    for _ in 0..2 {
        s.spawn(move || {
            let p = shared as *mut u32;
            for _ in 0..1000 {
                // SAFETY: not sound -- two threads write and read this
                // location with no lock and no atomic, which is a data race.
                unsafe { *p += 1; }
            }
        });
    }
});
println!("counter = {counter}");
```

The correct total is 2000. Release printed it in ten of ten runs; debug printed it in only one of ten, the rest landing between 1090 and 1935, each a lost increment. Miri:

```text
error: Undefined Behavior: Data race detected between (1) non-atomic write on thread `unnamed-2` and (2) non-atomic read on thread `unnamed-1` at alloc219
help: and (1) occurred earlier here
```

Ten of ten clean release runs is the whole point: a passing run, however many times it passes, says nothing about soundness. Miri (lesson 49's subject) answered on the first attempt.

### An invalid value: a bool that is neither

Safe Rust can only ever produce `false` or `true`. `transmute` copies bits without checking what they mean at the destination, so transmuting the byte `3` into a `bool` builds a value the safe side of the language cannot:

```rust
// SAFETY: not sound -- 3 is not a valid bit pattern for bool, which
// requires 0 or 1.
let bad: bool = unsafe { std::mem::transmute::<u8, bool>(3) };
println!("bad = {bad}");
if bad { println!("branched: true arm"); } else { println!("branched: false arm"); }
```

Run eleven times across debug and release, this printed `bad = true` and took the true arm every time. That is not a well-formed `true`: the compiler is free to compile its assumption that a bool is one of two bit patterns however it likes. Miri:

```text
error: Undefined Behavior: constructing invalid value of type bool: encountered 0x03, but expected a boolean
```

The Reference states the rule directly: "A bool value must be false (0) or true (1)." An enum with an invalid discriminant fails the same way, with a payload attached: not a wrong answer, but a shape the type system never gave a meaning to.

### transmute and MaybeUninit: the two doors into an invalid value

`transmute` and `MaybeUninit` build most accidental invalid values. `transmute`'s contract: "Both the argument and the result must be valid at their given type. Violating this condition leads to undefined behavior." Nothing checks that; `3u8` satisfied it for `u8`, not `bool`. `MaybeUninit<T>` holds bytes the compiler will not assume are valid, and its docs warn this matters even for an integer: "It is a common mistake to assume that this function is safe to call on integers because they can hold all bit patterns." Safe Rust will not compile a read before assignment; `MaybeUninit` opts out, and reading too early is undefined regardless of type:

```rust
use std::mem::MaybeUninit;
let slot: MaybeUninit<u8> = MaybeUninit::uninit();
// SAFETY: not sound -- slot was never written, so this reads
// uninitialised memory, which is invalid regardless of the type.
let value = unsafe { slot.assume_init() };
println!("value = {value}");
```

This printed `value = 0` in six of six runs, which looks like proof the byte is zero, not that the read was sound. Miri:

```text
error: Undefined Behavior: constructing invalid value of type u8: encountered uninitialized memory, but expected an integer
```

matching the scalar rule: "An integer (i*/u*), floating point value (f*), or raw pointer must be initialized, i.e., must not be obtained from uninitialized memory." Every bit pattern a `u8` can hold is otherwise legal; reading one before writing it is illegal because uninitialised memory behaves like no value at all.

### Release against debug, and what neither proves

The data race already answered this section's question: release and debug disagreed about the same program, and neither answer was honest. Release's faster loop let the two threads finish before their windows for a lost update lined up; debug's slower code gave far more chances to interleave mid-increment. Debug adds overflow and bounds checks, not a check for a torn read-modify-write, so debug exposing more bugs here is a side effect of being slower, not more careful. The transmuted bool agrees from the other side, printing the identical wrong answer in both profiles, since no profile inserts a validity check on a bare `transmute`; a hand-written `debug_assert!` catches a value its own code produced, not a byte-for-byte reinterpretation. A clean run, in either build, is not the tool for this job.

## Practice

1. ▢ Predict what the aliasing example prints on stable, run it several times, then run it under Miri.

<details markdown="1"><summary>Check</summary>

It prints `x = 12` every time on stable; Miri still rejects it with the tag error above, because a correct-looking number is not what Miri checks.

</details>

2. ▢ Predict what the invalid-bool example prints, and which branch it takes, in debug and in release.

<details markdown="1"><summary>Check</summary>

Both print `bad = true` and take the true arm; no build's debug checks catch a bad transmute, so agreement between profiles is not evidence of correctness.

</details>

3. ▢ Predict whether the data race example's clean release runs would survive a switch to a debug build, then run both several times.

<details markdown="1"><summary>Hint</summary>

Debug is slower and unoptimised, which changes how often two threads overlap mid-instruction; slower is not safer here.

</details>

<details markdown="1"><summary>Check</summary>

No: debug loses data in most attempts, nine of ten in one run, while release stayed clean in all ten; the bug is identical, only the odds of seeing it changed.

</details>

4. ▢ Ordinary access is always aligned; a raw pointer skips that check. Predict whether reading a `u32` through a pointer offset one byte into an eight-byte buffer compiles and runs cleanly on stable, then run it, then under Miri.

   ```rust
   let buf: [u8; 8] = [1, 2, 3, 4, 5, 6, 7, 8];
   let base = buf.as_ptr();
   unsafe {
       let misaligned = base.add(1) as *const u32;
       // SAFETY: not sound -- misaligned has alignment 1, but u32 needs 4.
       let value = misaligned.read();
       println!("value = {value}");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`.read()` does not check the alignment its type requires; only `read_unaligned` says so honestly.

</details>

<details markdown="1"><summary>Check</summary>

It compiles, runs, and prints `value = 84148994`, the little-endian reading of bytes two through five, exactly what a correct-but-misaligned read should give; Miri's first line is `error: Undefined Behavior: accessing memory based on pointer with alignment 2, but alignment 4 is required`.

</details>

5. ▢ A judgement call, not a compile check: for each of these, name which entry on this lesson's list it risks.

   - a) A `Box<T>` is dropped, then a raw pointer copied from it beforehand is dereferenced.
   - b) A `fn(i32) -> i32` is transmuted to `fn(i64) -> i64` and called.
   - c) Two threads, one writing and one reading, touch the same `u32` through a raw pointer, no lock, no atomic.

<details markdown="1"><summary>Check</summary>

a) is a dangling access. b) is calling a function with the wrong call ABI. c) is a data race, the demonstration above.

</details>

## Real-world reps

- [ ] In your project's parser, take the hottest parse function and, for each entry on this lesson's list, write one sentence saying whether the safe code could violate it and which guarantee rules it out; a sentence that will not finish is worth flagging.
- [ ] Write an `unsafe` block that dereferences a raw pointer one element past the end of a `Vec`'s allocation, run it under `cargo +nightly miri run`, and note whether it errors.
- [ ] Tomorrow: before the next `unsafe` block you write anywhere, write its `SAFETY:` comment first, as "this is sound because ...", and if the sentence will not finish, do not write the block.

## Going further

- [Transmutes](https://doc.rust-lang.org/nomicon/transmutes.html): the Rustonomicon on the operation behind the bool above
- [Uninitialized Memory](https://doc.rust-lang.org/nomicon/uninitialized.html): the Rustonomicon on why a partial value is dangerous
- [std::mem::MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html): the type behind the uninitialised read above
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
