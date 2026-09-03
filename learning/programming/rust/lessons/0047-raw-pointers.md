---
title: 47. Raw Pointers
description: What a raw pointer is not, what it costs you in guarantees, and how to make one that is actually valid
type: lesson
---

# Lesson 47. Raw Pointers

**Mission link:** A `*mut T` shows up the moment code talks to a C library, builds its own collection, or reaches into a struct nobody could hand you a reference to, and every guarantee a reference quietly checked becomes a promise you keep by hand.
**Primary source:** [std::ptr](https://doc.rust-lang.org/std/ptr/index.html)
**Prerequisites:** [Lesson 46](0046-what-unsafe-promises.md), [Lesson 4](0004-slices-string-and-str.md)

## Warm-up

1. ▢ Lesson 46 said `unsafe` is a promise made by the author, not a switch that disables the borrow checker. If a block promises something untrue, what enforces the promise?

<details markdown="1"><summary>Check</summary>

Nothing does: the compiler stopped checking once the block was written, so a broken promise produces undefined behaviour rather than a caught error, which is why this lesson focuses on making the promise true, not merely written.

</details>

2. ▢ Lesson 4 described a slice as a pointer paired with a length, borrowed rather than owned. If you already had a pointer and a length in two separate variables, what would be missing that a real slice has?

<details markdown="1"><summary>Check</summary>

The guarantee that the pointer is non-null, aligned, points to `len` live and initialised values, and is not mutated meanwhile; a bare pointer and number carry none of that, which is what a slice's pointer half gives up once raw.

</details>

## Know this

### `*const T`, `*mut T`, and the line unsafe actually draws

A raw pointer is `*const T` or `*mut T`; the asterisk is part of the type's name, not a dereference. Both are made from a reference or a bare address, and none of that, nor copying, needs `unsafe`:

```rust
let x = 5i32;
let p: *const i32 = &x as *const i32;        // from a reference
let addr: *const i32 = 0x1000 as *const i32; // from a bare address
let q = p;                                   // copying a raw pointer
```

Reading through one is a different story:

```rust
println!("{}", *p);
```

```text
error[E0133]: dereference of raw pointer is unsafe and requires unsafe block
 --> src/main.rs:4:20
  |
4 |     println!("{}", *p);
  |                    ^^ dereference of raw pointer
  |
  = note: raw pointers may be null, dangling or unaligned; they can violate aliasing rules and cause data races: all of these are undefined behavior
```

Wrapping the read compiles cleanly:

```rust
println!("{}", unsafe {
    // SAFETY: sound -- p was made from &x above, and x is still in scope
    // and unmoved, so p is still valid, aligned and non-null.
    *p
});
```

The note already named what it did not check: null, dangling, unaligned, aliasing.

### What you gave up

A reference is never dangling (**validity**), meets its alignment (**alignment**), is never null (**non-nullness**), and never overlaps a conflicting access (**aliasing**). A raw pointer keeps none of the four, uncaught by the compiler at the point it is made.

Validity: a pointer to memory already freed.

```rust
fn make_ptr() -> *const i32 {
    let boxed = Box::new(42);
    let raw = Box::into_raw(boxed);
    unsafe {
        // SAFETY: sound -- raw came from Box::into_raw on the line above and
        // has not been freed or aliased since, so from_raw's requirements hold.
        drop(Box::from_raw(raw));
    } // the allocation is freed here
    raw as *const i32 // the address is still around; nothing backs it now
}

fn clobber() {
    let buf = vec![7u8; 4];
    std::hint::black_box(&buf);
}

fn main() {
    let p = make_ptr();
    clobber();
    println!("{}", unsafe {
        // SAFETY: not sound -- p points into the allocation freed by the
        // drop above, which is exactly the validity rule this section names.
        *p
    });
}
```

Run five times, this printed `3`, never `42`; `make_ptr` compiled without a warning, since `raw`'s type says nothing about the allocation being gone.

Alignment: a pointer one byte off from where its type needs to start.

```rust
let bytes = [0u8, 1, 2, 3, 4, 5, 6, 7];
let misaligned = unsafe {
    // SAFETY: sound -- add(1) moves one byte forward, still inside
    // bytes's 8-byte allocation; alignment only matters on dereference.
    bytes.as_ptr().add(1) as *const u32
};
println!("{}", unsafe {
    // SAFETY: not sound -- misaligned is not a multiple of align_of::<u32>()
    // (4), which is exactly the alignment rule this section names.
    *misaligned
});
```

Debug panics before printing: `misaligned pointer dereference: address must be a multiple of 0x4 but is 0x16dbf1e35`, a runtime guard the library inserts, not something the compiler proved; release skips it and quietly returns `67305985`.

Non-nullness: the address zero itself.

```rust
let p: *const i32 = std::ptr::null();
println!("{}", unsafe {
    // SAFETY: not sound -- p is null, and a null pointer is never valid
    // for reads, which is exactly the non-nullness rule this section names.
    *p
});
```

Debug panics with `null pointer dereference occurred`; release printed `1` and exited normally, no crash or warning.

Aliasing: two live `&mut` borrows made from the same `*mut T`.

```rust
let mut x = 10u32;
let p: *mut u32 = &mut x;
unsafe {
    // SAFETY: not sound -- a and b alias the same &mut, which is exactly
    // what the pointer aliasing rule forbids.
    let a = &mut *p;
    let b = &mut *p;
    *a += 1;
    *b += 1;
    println!("{}", *a);
}
```

On stable this printed `12` every run, an ordinary answer for two increments on `10`. Nothing checks that `a` and `b` overlap; the borrow checker watched `x`, and both came from `p`, untracked. Miri, in lesson 49, names the exact moment one borrow invalidated the other.

Across all four, the compiler's job ends at "you must write `unsafe` before touching memory through this"; whether it is there, aligned, non-null, or unborrowed goes unchecked, and a debug-only guard catches two of the four, gone once optimised.

### Validity is a property of the whole access, not the pointer

`std::ptr` says this outright, with its curly quotation marks flattened here and below to keep this page plain text: "it makes no sense to ask 'is this pointer valid'; one has to ask 'is this pointer valid for a given access'." The same bit pattern is good at one moment and dangling the next, since the memory's ownership changed, not the pointer. `make_ptr` above drew no warning; a plainer route does:

```rust
fn dangling() -> *const i32 {
    let x = 42;
    let addr = &x as *const i32 as usize; // route through an integer; still recognised below
    addr as *const i32
}

fn clobber(n: usize) {
    let buf = vec![7u8; n];
    std::hint::black_box(&buf);
}

fn main() {
    let mut ok = 0;
    let mut bad = 0;
    for n in 0..30 {
        let p = dangling();
        clobber(n * 8 + 1);
        // SAFETY: not sound -- p points at x's old stack slot, which ended
        // when dangling() returned; this is the validity rule broken, and
        // clobber's call is what makes the break visible or not.
        if unsafe { *p } == 42 { ok += 1 } else { bad += 1 }
    }
    println!("{ok} of 30 read back 42, {bad} did not");
}
```

Compiling `dangling` alone draws a warning, `function returns a dangling pointer to dropped local variable 'x'`, with `a dangling pointer is safe, but dereferencing one is undefined behavior`; the lint is narrow, catching only a function handing back a local's address, and `Box::into_raw` above walked past it. As a release binary, the loop read back `42` all thirty times; as an unoptimised debug binary, it read back something else all thirty times. Only how the compiler arranged the freed stack space changed. A clean, repeatable run is not evidence the target is still there, only evidence about the compiler's mood; lesson 49 covers Miri, the tool that checks each access against its claimed allocation regardless of what printed.

### Making a valid pointer deliberately

`NonNull<T>` wraps a `*mut T` that promises never to be null, checked once at construction rather than discovered on read:

```rust
let mut n = 7i32;
let nn = std::ptr::NonNull::new(&mut n as *mut i32).expect("non-null");
println!("{}", unsafe {
    // SAFETY: sound -- nn was built from &mut n above, and n is still
    // in scope and unmoved, so nn is valid, aligned and non-null.
    *nn.as_ptr()
});
```

`NonNull::new_unchecked` skips that check, and its documentation is a one-line promise: "`ptr` must be non-null." `ptr::null_mut` makes the deliberately-absent pointer, meant to be checked with `is_null` before it is dereferenced:

```rust
let p: *mut i32 = std::ptr::null_mut();
assert!(p.is_null());
```

A `str` hands out `as_ptr` for reading and `as_mut_ptr` for writing, the `&`/`&mut` split lesson 4 covered, both compiling without `unsafe`:

```rust
let s: &str = "hi";
let read_ptr = s.as_ptr();
let mut owned = String::from("hi");
let write_ptr = owned.as_mut_ptr();
```

The obligation moves to whoever writes through them; `as_ptr`'s documentation is explicit: "The caller must ensure that the returned pointer is never written to."

The last tool points at a place without ever forming a reference, for when forming one would already be wrong: `addr_of!` and `addr_of_mut!`, in their own example:

```rust
#[repr(packed)]
struct Packed { f1: u8, f2: u16 }

let packed = Packed { f1: 1, f2: 2 };
let raw_f2 = std::ptr::addr_of!(packed.f2);
println!("{}", unsafe {
    // SAFETY: sound -- raw_f2 points at packed.f2, live and initialised,
    // and read_unaligned is the one read that drops the alignment
    // requirement a plain dereference would otherwise need.
    raw_f2.read_unaligned()
});
```

Their documentation says why: "Creating a reference with `&`/`&mut` is only allowed if the pointer is properly aligned and points to initialized data. ... `&mut expr as *mut _` creates a reference before casting it to a raw pointer, and that reference is subject to the same rules as all other references." That is why `&mut x as *mut _` is sometimes wrong before the cast runs: the left side of `as` is a full reference, built under the rules a reference must satisfy; if `x` was never fit to be referenced, the damage happened there.

### Alignment and size

`std::mem::size_of::<T>()` and `std::mem::align_of::<T>()` are the two numbers every guarantee above is measured against:

```rust
println!("{}", std::mem::size_of::<u32>());  // 4
println!("{}", std::mem::align_of::<u32>()); // 4
```

`align_of`'s documentation states the requirement plainly: "Every reference to a value of the type `T` must be a multiple of this number." An unaligned access is a read or write whose address is not a multiple of that number, shown above as one debug panic and one silent wrong answer in release.

`#[repr(packed)]` can force a field's alignment below what its type demands: `align_of::<Packed>()` is `1`, `align_of::<u16>()` is `2`, so `f2` in `Packed { f1: u8, f2: u16 }` gets no two-byte boundary, and an ordinary reference to it is refused outright:

```rust
#[repr(packed)]
struct Packed { f1: u8, f2: u16 }

let packed = Packed { f1: 1, f2: 2 };
let r = &packed.f2;
```

```text
error[E0793]: reference to field of packed struct is unaligned
 --> src/main.rs:9:13
  |
9 |     let r = &packed.f2;
  |             ^^^^^^^^^^
  |
  = note: this struct is 1-byte aligned, but the type of this field may require higher alignment
  = note: creating a misaligned reference is undefined behavior (even if that reference is never dereferenced)
  = help: copy the field contents to a local variable, or replace the reference with a raw pointer and use `read_unaligned`/`write_unaligned` (loads and stores via `*p` must be properly aligned even when using raw pointers)
```

The `help` line names the fix already used above: a raw pointer plus `read_unaligned`, exactly what `addr_of!` did in the previous section.

### Offsets and slices

`add` moves a pointer forward by whole elements, `count * size_of::<T>()` bytes; it and `offset` share one safety rule, from `offset`'s documentation: "If any of the following conditions are violated, the result is Undefined Behavior: ... If the computed offset is non-zero, then `self` must be derived from a pointer to some allocation, and the entire memory range between `self` and `result` ... must be in bounds of that allocation." One element past the last is allowed, letting a loop know where to stop: `offset_from`'s documentation calls this the "end" of a "start" and "end" pair, "one past the end" of the array.

```rust
let v = vec![10i32, 20, 30, 40];
let start = v.as_ptr();
let end = unsafe {
    // SAFETY: sound -- v.len() is exactly v's element count, so this lands
    // one past the end, which add's contract allows to construct, not read.
    start.add(v.len())
};
let mut p = start;
while p != end {
    print!("{} ", unsafe {
        // SAFETY: sound -- the while guard above just confirmed p != end,
        // so p is strictly inside [start, end) and points at a live i32.
        *p
    });
    p = unsafe {
        // SAFETY: sound -- p < end here (same guard), so p.add(1) lands
        // at most at end, still in bounds per the one-past-the-end rule.
        p.add(1)
    };
}
```

Rebuilding a slice from a pointer and a length goes through `slice::from_raw_parts`, whose conditions are what a slice was quietly checking on your behalf:

```rust
let rebuilt: &[i32] = unsafe {
    // SAFETY: sound -- start and v.len() come from v, still alive and
    // unmutated here, so from_raw_parts's documented requirements hold.
    std::slice::from_raw_parts(start, v.len())
};
```

Character for character: "`data` must be non-null, valid for reads for `len * size_of::<T>()` many bytes, and it must be properly aligned. ... `data` must point to `len` consecutive properly initialized values of type `T`. ... The total size `len * size_of::<T>()` of the slice must be no larger than `isize::MAX`, and adding that size to `data` must not 'wrap around' the address space." Every clause names a guarantee a real slice enforces once, asked for here by hand.

## Practice

1. ▢ Predict whether `println!("{}", *p)` compiles for a `*const i32` named `p`, with no `unsafe` block nearby, then try it.

<details markdown="1"><summary>Check</summary>

It does not compile: `error[E0133]: dereference of raw pointer is unsafe and requires unsafe block`, since reading through one is the one operation the compiler always stops at, however it was made.

</details>

2. ▢ Predict what dereferencing `std::ptr::null::<i32>()` does in a debug build versus `cargo build --release`, then try both.

<details markdown="1"><summary>Hint</summary>

A runtime guard the standard library inserted may or may not survive optimisation.

</details>

<details markdown="1"><summary>Check</summary>

Debug panics with `null pointer dereference occurred`; release prints a number and exits, since the check is gone, and the compiler objected to neither.

</details>

3. ▢ Predict whether `&packed.f2` compiles for `#[repr(packed)] struct Packed { f1: u8, f2: u16 }`, then try it.

<details markdown="1"><summary>Hint</summary>

`align_of::<Packed>()` and `align_of::<u16>()` differ.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile: `error[E0793]: reference to field of packed struct is unaligned`, since a reference must be aligned the moment it is created, and packed layout cannot promise that for `f2`; the `help` line points at a raw pointer plus `read_unaligned`.

</details>

4. ▢ Predict whether a use-after-free through a raw pointer looks more obviously wrong in debug or release, then run the same source both ways several times.

<details markdown="1"><summary>Hint</summary>

Debug leaves freed stack space alone more often than an optimiser does.

</details>

<details markdown="1"><summary>Check</summary>

The opposite of the usual expectation: debug reliably reads back the wrong value, while release reads back the original every time, since the optimiser reused the freed slot leaving old bytes there. Neither outcome says anything about whether the pointer was actually valid.

</details>

5. ▢ A judgement call, not a compile check: for each pointer below, say which of validity, alignment, non-nullness or aliasing it violates.

   - a) A `*const Row` from a `Vec<Row>` since resized to hold three times as many rows.
   - b) A `*mut u8` built by adding 3 to a pointer from `&x as *const u32 as *mut u8`.
   - c) A `*mut Config` a failing C function returns, by convention, as unusable.
   - d) Two `*mut Counter` from the same `&mut Counter`, each turned into a `&mut` and incremented in the same expression.

<details markdown="1"><summary>Check</summary>

a) Validity: resizing a `Vec` can reallocate its buffer, so a pointer taken before may point at freed memory after, the freed-`Box` shape again. b) Alignment: `u32` is four-byte aligned and three bytes lands off it. c) Non-nullness: a "failed" C pointer is null far more often than any other sentinel. d) Aliasing: two live `&mut` to the same `Counter` at once, however many pointers produced them.

</details>

## Real-world reps

- [ ] In your summariser, rewrite the split of a request line into path, status and byte count using raw pointers: walk `bytes.as_ptr()` with `add` to find the separator, rebuild both halves with `slice::from_raw_parts` and `str::from_utf8_unchecked`, a `SAFETY:` comment on every `unsafe` block; confirm it matches what it replaced.
- [ ] Delete that version and keep the original. In two sentences, say what it guaranteed silently, that you had to spell out as `SAFETY:` comments.
- [ ] Tomorrow: find one raw pointer in a dependency, or the standard library's source, and decide from its doc comment which of the four guarantees it is most careful about.

## Going further

- [pointer](https://doc.rust-lang.org/std/primitive.pointer.html): the primitive type page carrying `add`, `offset` and the rest of the methods above
- [NonNull](https://doc.rust-lang.org/std/ptr/struct.NonNull.html): the wrapper used above to build a pointer deliberately
- [from_raw_parts](https://doc.rust-lang.org/std/slice/fn.from_raw_parts.html): the function whose safety section this lesson quoted in full
- [Working with Unsafe](https://doc.rust-lang.org/nomicon/working-with-unsafe.html): the Rustonomicon chapter on the boundary a pointer sits behind
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
