---
title: 5. Bindings and Mutability
description: Immutable by default, mut is per binding, and shadowing is a new binding rather than a change
type: lesson
---

# Lesson 5. Bindings and Mutability

**Mission link:** Where `mut` goes, and what shadowing does, decide whether a function reads as a sequence of transformations or as a mutable blob. This is also where the borrow rule from lesson 3 gets its precondition: you cannot take `&mut` of something that is not `mut`.
**Primary source:** [The Rust Programming Language, Variables and Mutability](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html)
**Prerequisites:** [Lesson 3](0003-borrowing.md), [Lesson 4](0004-slices-string-and-str.md)

## Warm-up

1. ▢ Why does taking `&str` rather than `String` in a signature cost callers nothing?

<details markdown="1"><summary>Check</summary>

Deref coercion converts `&String` to `&str` automatically, and a literal is already a `&str`, so both kinds of caller work without allocating.

</details>

2. ▢ Why is `s[0]` refused on a `String`?

<details markdown="1"><summary>Check</summary>

A byte is not a character in UTF-8, so there is no `Index<usize>`. Range slicing exists and panics on a non-boundary.

</details>

## Know this

`let` creates a **binding**, and bindings are immutable by default:

```rust
let x = 5;
x = 6;                  // error: cannot assign twice to immutable variable

let mut y = 5;
y = 6;                  // fine
```

`mut` is a property of the binding, not of the type. There is no `mut i32`; there is a `mut` binding holding an `i32`. That is why lesson 3's rule needs it: `&mut v` requires `v` to be a `mut` binding, because a mutable borrow is permission to change what the binding owns.

### Shadowing is a new binding, not a mutation

```rust
let spaces = "   ";
let spaces = spaces.len();      // a NEW binding, and a different type
```

The second `let` creates a new binding with the same name. The first still exists and is simply unreachable. Two things follow: the type may change, and no `mut` is needed.

That makes shadowing the idiomatic way to write a pipeline of transformations without inventing `input_raw`, `input_trimmed`, `input_parsed`:

```rust
let input = read_line();                 // String
let input = input.trim();                // &str
let input: u32 = input.parse()?;         // u32
```

Compare with `mut`, which cannot change the type and keeps one value changing under one name:

| | `mut` | shadowing |
|---|---|---|
| same value changes | yes | no, a new value each time |
| type may change | no | yes |
| needed for `&mut` | yes | no |
| reads as | a thing being modified | a sequence of steps |

Use `mut` when a value genuinely changes over time, such as an accumulator or a buffer being filled. Use shadowing when you are converting rather than modifying. Both are ordinary Rust and neither is a trick.

### Blocks are expressions

```rust
let category = {
    let score = compute();
    if score > 90 { "high" } else { "low" }
};
```

A block evaluates to its last expression, when that expression has no semicolon. The pattern above keeps `score` out of the surrounding scope, which is worth doing whenever a temporary exists only to compute one value.

The same rule explains why a missing semicolon changes a function's meaning: `x + 1` returns, and `x + 1;` evaluates and discards, leaving the function returning `()`.

### `const` and `static`

```rust
const MAX_RETRIES: u32 = 5;             // inlined at each use site
static GREETING: &str = "hello";        // one fixed memory location
```

Both require an explicit type and a value computable at compile time. `const` is what you want almost always. `static` matters when the identity of the memory matters, and a `static mut` is unsafe to touch, which stage 7 explains.

Neither is a `let` with extra letters: they live for the whole program and have no owner in lesson 1's sense.

### One aside worth knowing now: integer overflow

```rust
let x: u8 = 255;
let y = x + 1;          // debug: panics. release: wraps to 0
```

Overflow panics in a debug build and wraps in a release build by default. That difference is deliberate, documented, and not undefined behaviour, unlike the equivalent in some other languages. When wrapping is the intent, say so with `wrapping_add`; when it must never happen, use `checked_add` and handle the `Option`.

It is mentioned here because it is the one place where "it worked in testing" has a language-level explanation rather than a logic one.

## Practice

1. ▢ Which of these compile?

   ```rust
   // A
   let x = 5;
   let x = x + 1;

   // B
   let x = 5;
   x = x + 1;

   // C
   let mut x = 5;
   x = x + 1;

   // D
   let mut x = 5;
   x = "five";
   ```

<details markdown="1"><summary>Check</summary>

A and C compile. B fails, because `x` is not `mut` and this is an assignment rather than a new binding. D fails, because `mut` allows a new value and not a new type.

A and C produce the same value by different means, which is the distinction the lesson turns on: A made a second binding, C changed one.

</details>

2. ▢ Predict the two prints.

   ```rust
   let value = 10;
   {
       let value = value * 2;
       println!("{value}");
   }
   println!("{value}");
   ```

<details markdown="1"><summary>Hint</summary>

The inner `let` does not modify anything. Ask what happens to it when its block ends.

</details>

<details markdown="1"><summary>Check</summary>

`20`, then `10`.

The inner binding shadows the outer one for the rest of that block. When the block ends, the shadow ends with it and the outer binding is reachable again, unchanged, because it was never modified.

</details>

3. ▢ Which is better for this task, and why?

   ```rust
   // A
   let mut input = read_line();
   input = input.trim().to_string();

   // B
   let input = read_line();
   let input = input.trim();
   ```

<details markdown="1"><summary>Check</summary>

**B**, and the reason is not only style: A allocates.

`trim` returns a `&str` borrowed from the original, so A has to call `to_string` to get something assignable to a `String` binding, which copies the bytes. B binds the `&str` directly and copies nothing. The original `String` stays alive to be borrowed from, which is exactly what shadowing allows and reassignment does not.

</details>

4. ▢ Where does `mut` belong here, and what does each `mut` permit?

   ```rust
   fn fill(buffer: ??? Vec<u8>, count: usize) {
       for i in 0..count {
           buffer.push(i as u8);
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

```rust
fn fill(buffer: &mut Vec<u8>, count: usize) {
```

The parameter is a mutable borrow: the caller keeps ownership and the function may modify the vector. The caller's binding must itself be `mut` to hand out a `&mut`.

The alternatives say different things. `mut buffer: Vec<u8>` takes ownership and lets the function rebind, so the caller loses the vector. `buffer: Vec<u8>` takes ownership without allowing rebinding, but still allows mutation through methods, because ownership includes the right to mutate. The one to reach for here is `&mut`, because the function's job is to fill the caller's buffer.

</details>

5. ▢ A test passes in a debug build and produces a wrong number in release. The code adds two `u32` values from user input. Explain.

<details markdown="1"><summary>Check</summary>

The addition overflowed. In a debug build overflow panics, so the test failed loudly or the value never got that far; in a release build it wraps around, so the program continues with a small number and no signal.

The behaviour is defined and documented, and the fix is to say which one is intended: `checked_add` returns `Option` for the case where overflow is a real possibility to handle, `saturating_add` clamps, and `wrapping_add` states that wrapping is the intent. Reaching for a larger type is sometimes right and only moves the boundary.

</details>

## Real-world reps

- [ ] Write case D from practice 1 and read the error. It says the types differ, which is the clearest statement of what `mut` does and does not permit.
- [ ] Write the trim pipeline both ways and use a tool or your own reasoning to identify which one allocates.
- [ ] Tomorrow: overflow a `u8` deliberately, run it once with `cargo run` and once with `cargo run --release`, and see both behaviours.

## Going further

- [Variables and Mutability](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html): bindings, `const`, and shadowing with worked examples
- [Data Types](https://doc.rust-lang.org/book/ch03-02-data-types.html): the integer types, and the overflow paragraph
- [Block expressions](https://doc.rust-lang.org/reference/expressions/block-expr.html): why the last expression is the value
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
