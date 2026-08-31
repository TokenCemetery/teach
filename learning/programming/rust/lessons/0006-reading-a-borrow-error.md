---
title: 6. Reading a Borrow Error
description: Five error codes cover most of stage 1, and each one has an honest fix and a workaround
type: lesson
---

# Lesson 6. Reading a Borrow Error

**Mission link:** This closes the stage. Its success criterion is predicting a move or borrow error before the compiler reports it, and the way there is a small vocabulary of error codes plus the habit of asking what the compiler was actually asking.
**Primary source:** [Rust Compiler Error Index](https://doc.rust-lang.org/error_codes/error-index.html)
**Prerequisites:** [Lesson 2](0002-moves-and-copy.md), [Lesson 3](0003-borrowing.md), [Lesson 5](0005-bindings-and-mutability.md)

## Warm-up

1. ▢ What is the difference between `mut x` and `&mut x`?

<details markdown="1"><summary>Check</summary>

`mut x` is a binding that may be reassigned or mutated. `&mut x` is a mutable borrow of what `x` owns, and it requires `x` to be a `mut` binding.

</details>

2. ▢ Which of these ends a shared borrow: the end of the enclosing scope, or its last use?

<details markdown="1"><summary>Check</summary>

Its last use.

</details>

## Know this

An error message from `rustc` has four parts, and people read one of them:

```text
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
 --> src/main.rs:4:5
  |
3 |     let first = &v[0];
  |                  - immutable borrow occurs here
4 |     v.push(4);
  |     ^^^^^^^^^ mutable borrow occurs later here
5 |     println!("{first}");
  |               ------- immutable borrow later used here
```

The headline names the conflict. The spans name **three** lines: where the first borrow began, where the conflicting one is, and where the first borrow is still used. That third span is the one that matters, because it tells you what is keeping the borrow alive, which is usually the line you can move.

`rustc --explain E0502` prints the error code's page with a minimal reproduction, offline.

### The five codes that cover stage 1

| Code | Says | Usually means |
|---|---|---|
| `E0382` | use of moved value | a function took ownership where it should have borrowed |
| `E0499` | two mutable borrows | one of them can end sooner, or the data should be split |
| `E0502` | mutable while shared | a shared borrow is still used after the mutation |
| `E0505` | move out while borrowed | a borrow outlives the value's owner |
| `E0596` | cannot borrow as mutable | the binding is missing `mut` |

Two more arrive in stage 4, and they are the boundary of this stage rather than part of it: `E0106`, a missing lifetime specifier, and `E0597`, a value that does not live long enough. Both mean the compiler cannot work out how long a reference is meant to be valid, which is a question this stage never asks.

### The four honest fixes

Given a borrow or move error, one of these is right:

1. **End the borrow sooner.** Move the last use above the conflicting line, or wrap it in a block. Costs nothing, and works surprisingly often because borrows end at their last use.
2. **Copy the value out instead of borrowing.** For a `Copy` type, `let x = v[0];` retains no borrow at all.
3. **Change the signature to borrow.** `fn f(s: &str)` instead of `fn f(s: String)`. This is the fix for most `E0382`.
4. **Restructure so one owner is enough.** Split a struct so the two fields being borrowed separately are separate, or compute one value before mutating rather than interleaving.

### The four workarounds, and what each costs

These also compile. Each is correct in a narrow case and a mistake as a reflex:

| Workaround | Legitimate when | Cost when it is not |
|---|---|---|
| `.clone()` | two independent values are genuinely wanted | an allocation, and two values that silently diverge |
| `Rc<RefCell<T>>` | shared ownership with runtime-checked mutation is the real design | a compile-time check becomes a run-time panic |
| indices instead of references | the collection is mutated while being traversed | no bounds guarantee from the type; stale indices |
| `unsafe` | never, at this stage | undefined behaviour, and the borrow rules still apply |

The distinction is not moral, it is about information. The error was a question about who owns the value and for how long. Fixes 1 to 4 answer it; the workarounds change the subject.

### A worked triage

```rust
struct Server { config: Config, cache: Cache }

impl Server {
    fn refresh(&mut self) {
        let name = &self.config.name;          // shared borrow of self.config
        self.cache.insert(name);               // needs &mut self.cache
    }
}
```

That compiles, and the reason is worth knowing: the compiler tracks borrows of **disjoint fields** separately, so borrowing `self.config` and mutating `self.cache` do not conflict.

Now make it fail:

```rust
    fn refresh(&mut self) {
        let name = self.name();                // &self: borrows ALL of self
        self.cache.insert(name);               // E0502
    }
```

Calling a method that takes `&self` borrows the whole struct, so the disjointness is lost. The honest fixes, in order: have `name()` return an owned `String` when it is cheap; or read the field directly rather than through a method; or split the struct so the two parts can be borrowed independently. Cloning `self.config` would also compile and answers a question nobody asked.

### The habit

Before running the compiler on code you are unsure about, ask three questions in order:

1. Does anything take ownership here, and does it need to?
2. Which borrows are live at this line, and where is each one last used?
3. Are the two things being borrowed actually the same value, or two fields the compiler will treat separately?

Predicting the error is the skill. The compiler is a very fast way to check the prediction, and using it as the first step rather than the second is how people spend a year fighting it.

## Practice

1. ▢ Name the error code and the honest fix.

   ```rust
   let s = String::from("hi");
   let t = s;
   println!("{s}");
   ```

<details markdown="1"><summary>Check</summary>

`E0382`, use of moved value.

The honest fix depends on the intent. If both names should refer to one value, borrow: `let t = &s;`. If two independent values are wanted, `let t = s.clone();` and say why. If `t` was meant to replace `s`, delete the `println!`.

</details>

2. ▢ Name the code, then fix it without cloning and without changing what the program prints.

   ```rust
   let mut v = vec![1, 2, 3];
   let last = &v[v.len() - 1];
   v.push(4);
   println!("{last}");
   ```

<details markdown="1"><summary>Hint</summary>

Two of the four honest fixes apply here. One of them is a single-character change.

</details>

<details markdown="1"><summary>Check</summary>

`E0502`.

Fix by copying the value out, since `i32` is `Copy`: `let last = v[v.len() - 1];`, dropping the `&`. No borrow is retained, so the `push` is fine.

The other honest fix is to move the `println!` above the `push`, which ends the borrow earlier. Both cost nothing. Cloning the vector to keep a reference into the old copy would compile and would be absurd.

</details>

3. ▢ Which code does each situation produce?

   - a) A `for` loop over a `Vec` by value, then using the `Vec` afterwards
   - b) Calling `push` on a binding declared without `mut`
   - c) Two `&mut` to the same value alive at once
   - d) Returning a reference to a local variable

<details markdown="1"><summary>Check</summary>

a is `E0382`: `for x in v` takes ownership of `v`, and `for x in &v` is almost always what was meant. b is `E0596`. c is `E0499`. d is `E0106` or `E0515` depending on the shape, and it is the stage 4 material: the reference would outlive what it points at.

</details>

4. ▢ Why does the first method compile and the second not?

   ```rust
   fn a(&mut self) {
       let name = &self.config.name;
       self.cache.insert(name);
   }

   fn b(&mut self) {
       let name = self.name();     // fn name(&self) -> &str
       self.cache.insert(name);
   }
   ```

<details markdown="1"><summary>Check</summary>

The first borrows two disjoint fields, `self.config` and `self.cache`, and the compiler tracks field borrows separately, so there is no conflict.

The second calls a method taking `&self`, which borrows the whole struct including `cache`. The subsequent mutable borrow of `self.cache` then conflicts with a live shared borrow of all of `self`, giving `E0502`.

This is the single most common surprise when moving from free functions to methods, and the usual fixes are to access the field directly, to have the method return an owned value, or to split the struct.

</details>

5. ▢ A reviewer sees `Rc<RefCell<Config>>` in a pull request that was previously a plain `Config`. What should they ask?

<details markdown="1"><summary>Check</summary>

Whether more than one owner is genuinely required, and if so, why.

`Rc<RefCell<T>>` is the right tool for a real graph of shared, mutable state, and it is frequently the wrong tool introduced to silence a borrow error. It has three costs worth naming: the borrow rule is now checked at run time, so a double mutable borrow panics instead of failing to compile; `Rc` is not thread-safe, so the type cannot cross a thread boundary and will need to become `Arc<Mutex<T>>` later; and every access is a method call with a runtime check.

The useful review question is not "is this allowed" but "what is the second owner". If nobody can name it, the error being silenced had a structural answer.

</details>

## Real-world reps

- [ ] Take each of the five error codes and write the smallest program that triggers it. Then run `rustc --explain` on each and compare your reproduction with the official one.
- [ ] Write the disjoint-fields example both ways, confirm which compiles, then fix the failing one three different ways and pick the one you would defend.
- [ ] Tomorrow: before compiling anything new, predict out loud whether it will be rejected and with which code. Keep score for a week. That score going up is the stage being finished.

## Going further

- [Rust Compiler Error Index](https://doc.rust-lang.org/error_codes/error-index.html): every code with a minimal reproduction
- [E0382](https://doc.rust-lang.org/error_codes/E0382.html), [E0499](https://doc.rust-lang.org/error_codes/E0499.html), [E0502](https://doc.rust-lang.org/error_codes/E0502.html), [E0505](https://doc.rust-lang.org/error_codes/E0505.html): the four this stage produces most
- [Ownership and borrowing](../reference/ownership-and-borrowing.md): the rules, the codes, and the fix-against-workaround table
- [Learn Rust With Entirely Too Many Linked Lists](https://rust-unofficial.github.io/too-many-lists/): what happens when the structure genuinely fights ownership, which is stage 5
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
