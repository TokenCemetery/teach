---
title: 46. What Unsafe Promises
description: The five things an unsafe block lets you do, and the obligation you take on by writing one
type: lesson
---

# Lesson 46. What Unsafe Promises

**Mission link:** Every senior review of an `unsafe` block asks what it actually buys, and what the author checked by hand to earn it. Answering that needs the five things `unsafe` grants held exactly, not as a vague sense of "raw pointer stuff", and needs the borrow checker's continued presence proven rather than assumed, since the most common misuse of `unsafe` in the wild is reaching for it past an error nobody understood.
**Primary source:** [Unsafety](https://doc.rust-lang.org/reference/unsafety.html)
**Prerequisites:** [Lesson 6](0006-reading-a-borrow-error.md), [Lesson 36](0036-choosing-a-sharing-strategy.md)

## Warm-up

1. ▢ Lesson 6 showed a method taking `&self` borrowing the whole struct, so a shared borrow of `self.config.name` was still alive when `self.cache.insert` tried to borrow `self.cache` mutably, giving `E0502`. If that exact code is wrapped in an `unsafe` block with nothing else changed, does `E0502` still fire?

<details markdown="1"><summary>Check</summary>

Yes. `unsafe` adds five specific abilities; it does not remove any existing check, and the borrow checker runs on `unsafe` code exactly as it runs on everything else. Know this proves it by compiling the same shape.

</details>

2. ▢ Lesson 36 fixed a lost update by replacing two separate `Mutex` acquisitions with one `fetch_add` on an `AtomicUsize`, using no `unsafe` anywhere. If a reviewer instead saw a shared `*mut usize`, incremented directly from two threads with a raw pointer, what would that buy over the atomic?

<details markdown="1"><summary>Check</summary>

Nothing. It gives up exactly the guarantee the atomic exists to provide, in exchange for nothing measurable, which is this lesson's closing point: `unsafe` is worth reaching for only once the safe design has actually been asked for and found wanting.

</details>

## Know this

### What `unsafe` does not do

`unsafe` does not disable the borrow checker, does not turn off type checking, and is not a way past an error you did not understand. It grants five specific abilities, listed below, and nothing else changes. Proof beats assertion here, so take the warm-up's shape and compile it inside an `unsafe` block:

```rust
fn borrow_error_inside_unsafe() {
    let mut v = vec![1, 2, 3];
    unsafe {
        let first = &v[0];
        v.push(4);
        println!("{first}");
    }
}
```

```text
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
 --> src/main.rs:5:9
  |
4 |         let first = &v[0];
  |                      - immutable borrow occurs here
5 |         v.push(4);
  |         ^^^^^^^^^ mutable borrow occurs here
6 |         println!("{first}");
  |                    ----- immutable borrow later used here
```

`E0502` fires exactly as without the `unsafe`, because nothing inside this block uses any of the five abilities: the compiler additionally warns `unnecessary unsafe block`. The block did not make the code faster, safer or more permissive; it made it longer.

### The five abilities, from the Reference

The Reference defines the class: "Unsafe operations are those that can potentially violate the memory-safety guarantees of Rust's static semantics", then lists the ones this lesson covers: "Dereferencing a raw pointer.", "Calling an unsafe function.", "Implementing an unsafe trait.", "Reading or writing a mutable or unsafe external static variable.", and "Accessing a field of a union, other than to assign to it." Those are the five: a raw pointer dereference, an unsafe function or method call, an unsafe trait implementation, a mutable static access, and a union field access. Two, compiling:

```rust
unsafe fn double(x: i32) -> i32 {
    x * 2
}

fn main() {
    let n = 21;
    let p: *const i32 = &n;

    // SAFETY: `p` was just taken from a live local `n`, so it is aligned,
    // non-null and points at a valid `i32` for the length of this call.
    let value = unsafe { *p };

    // SAFETY: `double` has no preconditions beyond its argument type.
    let doubled = unsafe { double(value) };

    println!("{value} {doubled}");
}
```

This prints `21 42`. The raw pointer dereference and the unsafe function call are the two most common of the five in ordinary code; the union field, the mutable static and the unsafe trait are rarer and are named rather than demonstrated, since raw pointer mechanics are lesson 47's subject and the other two need nothing this lesson has not already said about the obligation they carry.

### The direction of the obligation

`unsafe` is not permission to skip a proof; it is a promise that you performed the proof the compiler cannot. The direction matters because `unsafe fn` and an `unsafe` block promise different things to different people. Marking a function `unsafe fn` promises nothing about its own body: it restricts who may call it, requiring the caller to write `unsafe` and take on the burden of having read its documented preconditions. An `unsafe` block inside a function's body is the author's own promise about one specific operation, addressed to whoever reads the surrounding code next. Edition 2024 sharpened this distinction: an unsafe operation written directly inside an `unsafe fn`'s body, with no inner `unsafe` block, now warns:

```rust
unsafe fn read_raw(p: *const i32) -> i32 {
    *p
}
```

```text
warning[E0133]: dereference of raw pointer is unsafe and requires unsafe block
 --> src/main.rs:2:5
  |
2 |     *p
  |     ^^ dereference of raw pointer
  |
  = note: raw pointers may be null, dangling or unaligned; they can violate aliasing rules and cause data races: all of these are undefined behavior
note: an unsafe function restricts its caller, but its body is safe by default
 --> src/main.rs:1:1
  |
1 | unsafe fn read_raw(p: *const i32) -> i32 {
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  = note: `#[warn(unsafe_op_in_unsafe_fn)]` (part of `#[warn(rust_2024_compatibility)]`) on by default
```

The note carries the whole idea in one line, "an unsafe function restricts its caller, but its body is safe by default". Before this lint, `unsafe fn` did double duty, gating callers and pre-authorising every unsafe operation inside it, so an operation added deep in a long function inherited the first one's blanket cover, with no separate `SAFETY:` comment forced at the new site. Edition 2024 splits the two roles: being inside an `unsafe fn` no longer excuses an operation from its own `unsafe { }` block and its own comment, the version this lesson and the ones after it assume.

### `unsafe(...)` on attributes

The same edition made a second, unrelated tightening: an attribute whose correctness the compiler cannot check on its own must now be written `unsafe(...)`, and leaving the wrapper off is a hard error:

```rust
#[no_mangle]
pub fn example() {}
```

```text
error: unsafe attribute used without unsafe
 --> src/main.rs:1:3
  |
1 | #[no_mangle]
  |   ^^^^^^^^^ usage of unsafe attribute
  |
help: wrap the attribute in `unsafe(...)`
  |
1 | #[unsafe(no_mangle)]
  |   +++++++         +
```

The edition guide states plainly: "Starting with the 2024 Edition, it is now required to mark these attributes as unsafe." That covers `no_mangle`, `export_name` and `link_section`, all of which affect linker symbol names in ways the compiler cannot verify are collision-free. Wrapped and compiling, with the comment the help text asked for:

```rust
// SAFETY: this binary defines `example` exactly once, so there is no other
// global symbol of this name to collide with.
#[unsafe(no_mangle)]
pub fn example() {}
```

### The `SAFETY:` comment is the deliverable

A `SAFETY:` comment is not decoration on an `unsafe` block; it is the actual product of writing one. It must state the invariant that makes the operation sound: a fact about the surrounding code or its inputs that, if true, guarantees the operation cannot misbehave, and that the compiler had no way to check itself. The two comments above earn their keep: `p` was just taken from a live local, so the dereference is over a valid, aligned, non-null pointer; `example` is the crate's only definition of that symbol, so `no_mangle` cannot collide. Compare a comment that says nothing:

```rust
unsafe {
    // SAFETY: this is fine
    *p
}
```

"This is fine" names no fact, checks nothing and gives a reviewer nothing to verify against; it is a comment about the author's confidence, not about the pointer. The difference between the two is whether a reader who trusts nothing but the comment could independently convince themselves the operation is sound. Every `unsafe` block in this lesson carries one for exactly that reason.

### When the answer is not `unsafe` at all

Two shapes recur, both already solved without `unsafe` in earlier stages. First, a borrow error whose honest fix is a design change: lesson 6's method taking `&self` borrowed the whole struct and broke a call mutating a different field, and the fix was to read the field directly or split the struct, not to wrap the conflict in `unsafe` and lose the check that caught it. Second, a shared-mutability problem the sharing stage already answered: lesson 36's lost update, two threads updating one number, was fixed with a held `Mutex` guard or an atomic `fetch_add`, both keeping every guarantee the compiler and runtime can give about that access. A raw pointer shared the same way keeps neither, for nothing the atomic did not already provide. `unsafe` earns its place only once a safe design has been tried against the requirement and found insufficient, which lesson 50 returns to when it builds an abstraction hiding an `unsafe` block behind a safe interface.

## Practice

1. ▢ Predict whether adding `unsafe { }` around lesson 6's `E0502` example changes the compiler's answer, then wrap it and run it.

<details markdown="1"><summary>Check</summary>

No change: `E0502` fires with the same three spans as without the `unsafe`, and the compiler additionally warns that the block is unnecessary, since nothing inside it uses any of the five abilities.

</details>

2. ▢ Match each snippet to one of the five abilities: `let v = unsafe { *p };`, `unsafe impl Send for Handle {}`, `unsafe { GLOBAL += 1 };` where `GLOBAL` is a `static mut`.

<details markdown="1"><summary>Check</summary>

The first dereferences a raw pointer. The second implements an unsafe trait. The third reads and writes a mutable static, one operation doing both.

</details>

3. ▢ Predict what happens when `#[no_mangle]` appears with no wrapper on edition 2024, then try it.

   ```rust
   #[no_mangle]
   pub fn example() {}
   ```

<details markdown="1"><summary>Hint</summary>

This is not the `unsafe_op_in_unsafe_fn` warning from Know this; it is a separate lint on attributes, and edition 2024 changed its severity.

</details>

<details markdown="1"><summary>Check</summary>

It refuses to compile with `error: unsafe attribute used without unsafe`, and a help line asking for the same wrapper Know this showed. Wrapping it as `#[unsafe(no_mangle)]` compiles.

</details>

4. ▢ A pull request adds `unsafe { *ptr }` with the comment `// SAFETY: unsafe block, be careful`. Is this ready to merge?

<details markdown="1"><summary>Check</summary>

No. The comment names no invariant: it does not say why `ptr` is valid, aligned or non-null at this point, so a reviewer has nothing to check it against. A comment stating what guarantees the pointer's validity, and where that guarantee comes from, is what the rule actually asks for.

</details>

5. ▢ A judgement call: a function borrows `self.a` immutably to compute a value, then needs to mutate `self.b`, and the compiler rejects it. A teammate suggests wrapping the whole function body in `unsafe` to make it compile. Using lesson 6, what would you suggest instead?

<details markdown="1"><summary>Check</summary>

Wrapping it in `unsafe` would not even compile, since `E0502` is not one of the five things `unsafe` waives, and if it somehow did, it would throw away the exact check that caught a real bug. The honest fix from lesson 6 is to borrow the two fields separately, read the field directly instead of through a `&self` method, or split the struct so the two parts can be borrowed independently.

</details>

## Real-world reps

- [ ] Go through your project's summariser and list every place a reader might reach for `unsafe`: skipping bounds checks against a `Vec`, a raw pointer instead of an index, a lifetime or borrow error that tempted a shortcut. For each, write down the safe design and why it is enough, citing the lesson that supplies it.
- [ ] Confirm your list contains no `unsafe`. If one entry seems to genuinely need it, write down what safe alternative you tried first and why it did not fit, since that is the argument lesson 54 asks you to make properly.
- [ ] Tomorrow: find one `unsafe` block in code you can read, yours or a dependency's, and check whether its `SAFETY:` comment survives this lesson's test: does it name a fact a reviewer could check, or does it just express confidence.

## Going further

- [Unsafe Rust](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html): the Book's chapter naming the same five abilities as "unsafe superpowers", worked through with more examples
- [Unsafe attributes](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html): the edition guide page behind the `unsafe(...)` wrapper shown above
- [unsafe_op_in_unsafe_fn warning](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html): the edition guide page behind the note quoted above
- [Error code E0133](https://doc.rust-lang.org/error_codes/E0133.html): the code behind the raw-pointer-dereference warning
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
