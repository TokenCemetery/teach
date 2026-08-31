---
title: 2. Moves and Copy
description: Assignment moves ownership unless the type is Copy, which is why the old name stops working
type: lesson
---

# Lesson 2. Moves and Copy

**Mission link:** `use of moved value` is the first error every Rust programmer meets, and reaching for `clone` to silence it is the first bad habit. Both come from not knowing which types move.
**Primary source:** [The Rust Programming Language, What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
**Prerequisites:** [Lesson 1](0001-ownership-and-drop.md)

## Warm-up

1. ▢ When is a value dropped, and in what order within one scope?

<details markdown="1"><summary>Check</summary>

When its owner goes out of scope. Within a scope, in reverse declaration order.

</details>

2. ▢ Which of `let n = 5i32` and `let s = String::from("x")` owns a heap allocation?

<details markdown="1"><summary>Check</summary>

The `String`. The `i32` is entirely stack data of a known size.

</details>

## Know this

Since a value has exactly one owner, assigning it to a second name would create two owners. Rust resolves that by **moving**: the new name becomes the owner and the old one becomes unusable.

```rust
let a = String::from("hi");
let b = a;                  // ownership moves to b
println!("{a}");            // error[E0382]: borrow of moved value: `a`
```

Nothing was copied and nothing was freed. The three words describing the `String` were written into `b`, and the compiler now refuses to let you use `a`, because allowing it would mean two names both responsible for freeing one buffer.

This is a compile-time bookkeeping rule, not a runtime operation. A move compiles to the same machine code as a copy of those three words, and often to nothing at all.

### `Copy` types are duplicated instead

A type that is entirely plain data, with nothing to free, can implement [`Copy`](https://doc.rust-lang.org/std/marker/trait.Copy.html). Assignment then duplicates the value and both names stay usable:

```rust
let a = 5;
let b = a;
println!("{a} {b}");        // fine: i32 is Copy
```

| `Copy` | Not `Copy` |
|---|---|
| all integer, float, `bool`, `char` types | `String`, `Vec<T>`, `Box<T>`, `HashMap` |
| shared references, `&T` | mutable references, `&mut T` |
| tuples and arrays whose elements are all `Copy` | any type with a `Drop` implementation |
| `Option<T>` and `Result<T, E>` where the contents are `Copy` | any struct or enum that does not derive `Copy` |

Two rows deserve attention. **`&T` is `Copy` and `&mut T` is not**, which is why passing a `&mut` to a function appears to move it, and is the reason for a surprising number of stage-3 errors. And **a type with a `Drop` implementation can never be `Copy`**, because duplicating it would mean running the destructor twice.

Your own type gets `Copy` only if you ask, and only if every field allows it:

```rust
#[derive(Copy, Clone, Debug)]
struct Point { x: f64, y: f64 }
```

`Copy` requires `Clone` because `Copy` is the special case: an implicit, bit-for-bit duplication. `Clone` is the general case, an explicit and possibly expensive one.

### Moving into and out of functions

```rust
fn consume(s: String) -> usize { s.len() }      // takes ownership, drops it
fn borrow(s: &String) -> usize { s.len() }      // looks at it

let s = String::from("hello");
consume(s);
// s is gone here
```

Returning a value moves ownership out, which is how a constructor works and why returning a local reference is a different matter entirely, covered in stage 4.

### Partial moves

Moving one field out of a struct invalidates that field, and the struct as a whole:

```rust
struct Config { name: String, retries: u32 }

let c = Config { name: String::from("api"), retries: 3 };
let name = c.name;          // c.name moved out
println!("{}", c.retries);  // fine: u32 is Copy and was not moved
println!("{c:?}");          // error: use of partially moved value
```

The remaining `Copy` field is still readable, and the struct cannot be used as a whole. That precision is deliberate, and it is why the error says *partially* moved.

### The four honest answers to a move error

When the compiler says a value was moved, one of these is the fix, and they are in rough order of preference:

1. **Borrow instead of moving.** Change the signature to `&T`. This is right whenever the callee only needs to read.
2. **Return it back.** Take ownership and return the value, or a value derived from it, when the callee genuinely consumes it.
3. **Restructure so one owner is enough.** Often the move error is a design question wearing a compiler error's clothes.
4. **Clone.** Correct when you genuinely need two independent values, and a real allocation every time.

`clone` is last on that list rather than absent. Written deliberately, it says "two independent values are worth an allocation here". Written reflexively, it hides the question the compiler was asking, and the answer would usually have been number 1.

## Practice

1. ▢ Which of these compile?

   ```rust
   // A
   let a = String::from("x");
   let b = a;
   println!("{b}");

   // B
   let a = String::from("x");
   let b = a;
   println!("{a}");

   // C
   let a = 5;
   let b = a;
   println!("{a} {b}");
   ```

<details markdown="1"><summary>Check</summary>

A and C compile. B does not: `error[E0382]`, because `a` was moved into `b`.

C works because `i32` is `Copy`, so the assignment duplicated the value instead of moving it. The syntax is identical in B and C, and the type decides what it means, which is why knowing the `Copy` list matters.

</details>

2. ▢ Predict whether this compiles, and why.

   ```rust
   fn takes(s: String) {}

   fn main() {
       let s = String::from("hi");
       takes(s);
       takes(s);
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what the first call did to the caller's ownership, and whether the parameter type left any choice about it.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile. The first call moved `s` into `takes`, where it was dropped, so the second call has nothing to move.

Two fixes, and the right one depends on the function. If `takes` only reads, change it to `fn takes(s: &String)` and call it twice with `&s`. If it really consumes, either clone for the second call, or have it return the value so the caller can pass it on.

</details>

3. ▢ Which of these types are `Copy`?

   - a) `[u8; 4]`
   - b) `&mut i32`
   - c) `(bool, char)`
   - d) `Option<String>`

<details markdown="1"><summary>Check</summary>

**a)** and **c)** are `Copy`.

An array of `Copy` elements is `Copy`, and so is a tuple of them. `&mut i32` is deliberately not, because two usable copies of a mutable reference would break the rule in lesson 3. `Option<String>` is not, because `String` is not.

</details>

4. ▢ What exactly does this error mean, and what is the most likely correct fix?

   ```text
   error[E0382]: borrow of moved value: `config`
   ```

<details markdown="1"><summary>Check</summary>

Something took ownership of `config`, and a later line tried to use it. The word `borrow` in the message describes the *later* use, which is often confusing: the borrow is fine, the problem is that there is nothing left to borrow.

The most likely fix is to change whatever took ownership so that it borrows instead. Look for a function call taking `config` rather than `&config`, an assignment to another variable, or a `for` loop over a collection by value where `&collection` was meant.

</details>

5. ▢ A colleague fixes every move error by adding `.clone()` and says the compiler is satisfied so the code is correct. What is right and what is wrong about that?

<details markdown="1"><summary>Check</summary>

Right: the code is memory-safe. `clone` produces an independent value, and nothing about it is undefined or unsound. Rust will not let them be wrong about safety.

Wrong on two counts. First, cost: each clone is an allocation and a copy, in a language chosen partly for not doing that. Second, and more damaging, it discards information. The move error was the compiler asking who should own this value, and cloning answers "both, separately", which is rarely the intended design. Two clones of a config that were meant to be one shared config will diverge the moment either is modified, and that is a logic bug the compiler cannot catch.

The reviewable version: a `clone` should be explainable in a sentence about why two independent values are wanted.

</details>

## Real-world reps

- [ ] Write case B from practice 1 and read the full error, including the notes and the span markers. It names the line that moved the value, which is the part people skip.
- [ ] Take a function that accepts `String` and change it to `&str`. Fix the call sites. Notice how many clones disappear.
- [ ] Tomorrow: write a struct with one `String` field and one `u32` field, move the `String` out, and try to use each field and then the whole struct. Three different errors, all informative.

## Going further

- [What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html): moves, clones and the stack-heap distinction, with diagrams
- [`Copy`](https://doc.rust-lang.org/std/marker/trait.Copy.html): what the trait requires, and why it implies `Clone`
- [E0382](https://doc.rust-lang.org/error_codes/E0382.html): the error code, with a minimal reproduction and the suggested fixes
- [Ownership and borrowing](../reference/ownership-and-borrowing.md): the `Copy` table and the error index, for lookup
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
