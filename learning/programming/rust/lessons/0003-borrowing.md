---
title: 3. Borrowing
description: Many shared borrows or one mutable borrow, never both, and a borrow ends at its last use
type: lesson
---

# Lesson 3. Borrowing

**Mission link:** The borrow rule is one sentence and it is the sentence the compiler is enforcing every time it rejects your program. Being able to state it, and to see where a borrow ends, is what turns the borrow checker from an obstacle into a design tool.
**Primary source:** [The Rust Programming Language, References and Borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
**Prerequisites:** [Lesson 2](0002-moves-and-copy.md)

## Warm-up

1. ▢ Why does `let b = a;` make `a` unusable when `a` is a `String`, and not when `a` is an `i32`?

<details markdown="1"><summary>Check</summary>

`String` is not `Copy`, so the assignment moves ownership. `i32` is `Copy`, so the value is duplicated and both names remain valid.

</details>

2. ▢ Which is `Copy`: `&T` or `&mut T`?

<details markdown="1"><summary>Check</summary>

`&T`. A mutable reference is deliberately not `Copy`, because two usable copies would break this lesson's rule.

</details>

## Know this

Borrowing is access to a value someone else still owns. There are two kinds, and one rule:

```rust
let s = String::from("hi");
let r1 = &s;            // shared borrow: read only
let mut t = String::from("hi");
let r2 = &mut t;        // mutable borrow: read and write
```

**At any point in a program, for any given value, you may have either any number of shared borrows or exactly one mutable borrow, never both.** And every borrow must be valid for as long as it is used.

That is the whole rule. It is worth saying out loud until it is automatic, because every borrow error is one of its two halves.

### Why the rule exists

It is not about preventing crashes in the abstract. The rule outlaws **aliasing plus mutation**: two paths to one value where at least one can change it. That combination is what makes iterator invalidation, use-after-free and data races possible ([aliasing](https://doc.rust-lang.org/nightly/nomicon/aliasing.html)).

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];      // shared borrow of an element
v.push(4);              // error[E0502]: needs a mutable borrow of v
println!("{first}");
```

`push` may reallocate the vector's buffer, which would leave `first` pointing at freed memory. In a language without this rule that program compiles and is a use-after-free. Here it is a compile error, and the error is the language doing the job it was designed for.

### A borrow ends at its last use

This is the part that makes the rule livable, and the part older material gets wrong. A borrow lasts until its **last use**, not until the end of the enclosing scope:

```rust
let mut s = String::from("hi");

let r = &s;
println!("{r}");        // last use of r; the shared borrow ends here

s.push_str(" there");   // fine: no live borrow
```

That analysis is called non-lexical lifetimes, and it has been how the compiler works since the 2018 edition. So a borrow error is often fixed by moving a line, not by restructuring: if the last use of the shared borrow can happen before the mutation, the conflict disappears.

### The three errors this produces, and what each means

```rust
let mut v = vec![1];

let a = &mut v;
let b = &mut v;         // E0499: cannot borrow `v` as mutable more than once
```

```rust
let r = &v;
v.push(2);              // E0502: cannot borrow as mutable while borrowed as immutable
```

```rust
let r = &v;
let owned = v;          // E0505: cannot move out of `v` because it is borrowed
```

All three are the same rule seen from three sides: two mutable paths, a mutable path alongside a shared one, and the owner disappearing while a borrow is live.

### Reborrowing, and passing `&mut` around

Since `&mut T` is not `Copy`, passing one to a function looks like it should move it. In practice the compiler inserts an implicit **reborrow**, so the original is usable again after the call returns:

```rust
fn extend(v: &mut Vec<i32>) { v.push(1); }

let mut v = vec![];
let r = &mut v;
extend(r);              // implicit reborrow: &mut *r
extend(r);              // still fine
```

Knowing the mechanism matters when it does not fire, for example when storing a `&mut` in a struct, where the move is real and the fix is an explicit `&mut *r`.

### Shared borrows are not read-only in the type, they are read-only in the access

`&T` gives you read access. It does not promise the value never changes, only that it will not change through any path while your borrow is live. Interior mutability, meaning `Cell` and `RefCell`, moves that check to run time and is stage 5's material. Until then, treat `&T` as a promise the compiler is keeping for you.

## Practice

1. ▢ Which of these compile?

   ```rust
   // A
   let mut v = vec![1, 2];
   let a = &v;
   let b = &v;
   println!("{a:?} {b:?}");

   // B
   let mut v = vec![1, 2];
   let a = &mut v;
   let b = &mut v;
   println!("{a:?} {b:?}");

   // C
   let mut v = vec![1, 2];
   let a = &mut v;
   a.push(3);
   println!("{v:?}");
   ```

<details markdown="1"><summary>Check</summary>

A and C compile. B does not: `error[E0499]`, two mutable borrows alive at once.

C is the interesting one. The mutable borrow `a` is last used on the `push` line, so it is dead by the time `v` is printed, and printing `v` needs only a shared borrow. Under the old lexical rules this would have been rejected.

</details>

2. ▢ Explain the error, then fix it without changing what the program does.

   ```rust
   let mut v = vec![1, 2, 3];
   let first = &v[0];
   v.push(4);
   println!("{first}");
   ```

<details markdown="1"><summary>Hint</summary>

The fix is not a different data structure. Ask what `first` is for, and whether it needs to be a reference at all.

</details>

<details markdown="1"><summary>Check</summary>

`push` needs a mutable borrow of `v`, and the shared borrow held by `first` is still live because `first` is used on the last line. `E0502`.

The clean fix is to copy the value out, since it is an `i32`:

```rust
let first = v[0];       // i32 is Copy, no borrow is retained
v.push(4);
println!("{first}");
```

The alternative is to move the `println!` above the `push`, which ends the borrow earlier. Both are better than cloning the vector, and much better than the instinct to reach for `Rc<RefCell<Vec<i32>>>`, which would make a compile-time question into a run-time one.

</details>

3. ▢ Which rule does each error correspond to?

   - a) `E0499: cannot borrow as mutable more than once`
   - b) `E0502: cannot borrow as mutable while also borrowed as immutable`
   - c) `E0505: cannot move out because it is borrowed`

<details markdown="1"><summary>Check</summary>

All three are the one rule, seen from three sides.

a is two mutable paths to one value. b is a mutable path alongside a shared one. c is the owner being taken away while a borrow is still live, which would leave the borrow dangling.

Being able to map an error code back to the rule is the skill; lesson 6 makes it systematic.

</details>

4. ▢ Predict whether this compiles, and explain your reasoning in terms of where borrows end.

   ```rust
   let mut s = String::from("a");
   let r = &s;
   s.push('b');
   println!("{r}");
   ```

<details markdown="1"><summary>Check</summary>

It does not compile. `r` is used on the last line, so the shared borrow is live across the `push`, which needs a mutable borrow. `E0502`.

Move the `println!("{r}")` above the `push` and it compiles, because the borrow's last use is then before the mutation. The lines are the same; only their order changed, and the rule is about liveness rather than about text.

</details>

5. ▢ A colleague says the borrow checker is "about preventing null pointers". Give a more accurate one-sentence description, and one thing it does not prevent.

<details markdown="1"><summary>Check</summary>

It prevents aliasing and mutation at the same time: two paths to a value where at least one can change it. Null is a separate matter, handled by not having null at all and using `Option<T>` instead.

What it does not prevent: logic errors, deadlocks, memory leaks, and integer overflow in release builds. `Rc<RefCell<T>>` and `Mutex` both satisfy the borrow checker and can deadlock or panic at run time, which is precisely why they are stage 5 rather than a way around this lesson.

</details>

## Real-world reps

- [ ] Write case B from practice 1 and read the error, including the two span labels showing where each borrow starts. Then write case C and confirm it compiles.
- [ ] Take the iterator-invalidation example and try to fix it four ways: copy the value, move the print, clone the vector, use an index. Rank them.
- [ ] Tomorrow: state the borrow rule from memory, in one sentence, without looking. Then check it against the primary source.

## Going further

- [References and Borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html): the rule, with dangling-reference examples
- [Aliasing](https://doc.rust-lang.org/nightly/nomicon/aliasing.html): why the rule is what it is, from the optimiser's point of view
- [E0499](https://doc.rust-lang.org/error_codes/E0499.html) and [E0502](https://doc.rust-lang.org/error_codes/E0502.html): both codes with minimal reproductions
- [Ownership and borrowing](../reference/ownership-and-borrowing.md): the rule, the codes, and the honest fixes
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
