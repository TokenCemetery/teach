---
title: 1. Ownership and Drop
description: Every value has exactly one owner, and the compiler frees it when that owner goes out of scope
type: lesson
---

# Lesson 1. Ownership and Drop

**Mission link:** Ownership is the rule the rest of the language is built on. Read it as a restriction and everything after it feels arbitrary; read it as a claim about who is responsible for a value and the borrow checker stops being an opponent.
**Primary source:** [The Rust Programming Language, What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
**Prerequisites:** none, this is the first lesson.

## Know this

**Every value in Rust has exactly one owner. When the owner goes out of scope, the value is dropped.**

That is the whole mechanism. There is no garbage collector, no reference counting by default, and no `free` for you to call or forget.

```rust
{
    let s = String::from("hello");   // s owns the String
    println!("{s}");
}                                    // scope ends: s is dropped, the heap buffer is freed
```

The compiler inserts the cleanup. It knows where to put it because it knows who the owner is, and it knows that because there is only ever one.

### Stack and heap, and why the distinction shows up here

A local variable lives on the **stack**: fixed size, known at compile time, freed when the frame ends. Values whose size is not known at compile time, or which need to outlive the expression that made them, live on the **heap**, and something on the stack has to point at them.

```rust
let n: i64 = 7;                      // 8 bytes on the stack, that is all of it
let s = String::from("hello");       // 3 words on the stack, 5 bytes on the heap
```

A `String` is three machine words: a pointer to the heap buffer, a length, and a capacity. The name `s` owns all of it, and dropping `s` frees the buffer.

That is why ownership matters for a `String` and is invisible for an `i64`. There is no separate allocation to free, so nothing needs an owner to be responsible for it. Lesson 2 turns that observation into the `Copy` trait.

### Drop order is defined, not incidental

Values are dropped in **reverse declaration order** within a scope, and a struct's fields are dropped after the struct's own `Drop::drop` runs, in declaration order ([destructors](https://doc.rust-lang.org/reference/destructors.html)).

```rust
struct Noisy(&'static str);

impl Drop for Noisy {
    fn drop(&mut self) {
        println!("dropping {}", self.0);
    }
}

fn main() {
    let _a = Noisy("a");
    let _b = Noisy("b");
}                       // prints: dropping b, then dropping a
```

Reverse order is the only order that can work: `_b` may hold something borrowed from `_a`, and never the other way round, because `_a` existed first.

You will rarely implement `Drop` yourself. Knowing when it runs matters anyway, because it is exactly when a lock is released, a file is closed and a buffer is flushed. Those three things happening at a defined point, rather than whenever a collector gets round to it, is one of the concrete benefits of this design.

### Ownership can be transferred, and dropping can be deferred

```rust
fn consume(s: String) {              // takes ownership
    println!("{s}");
}                                    // dropped here, at the end of consume

fn main() {
    let s = String::from("hi");
    consume(s);                      // ownership moves into consume
                                     // s is no longer usable: lesson 2
}
```

Passing a value to a function can hand over ownership, and then the value is dropped inside that function rather than in the caller. Returning a value hands ownership back. That is why the signature of a Rust function tells you more than a signature in most languages: it says who will be responsible for the value afterwards.

You can also drop early on purpose with `drop(value)`, which is an ordinary function that takes ownership and does nothing. It is the idiomatic way to release a lock before the end of a long scope.

## Practice

1. ▢ How many heap allocations do these three lines make, and what does each variable own?

   ```rust
   let a = 5i32;
   let b = String::from("five");
   let c = "five";
   ```

<details markdown="1"><summary>Check</summary>

One allocation, made by `String::from`.

`a` owns four bytes on the stack. `b` owns three words on the stack plus a four-byte heap buffer. `c` owns nothing that needs freeing: it is a `&'static str`, a pointer and a length referring to bytes compiled into the binary, which is why it needs no allocation and no owner to clean it up.

The third case is worth noticing early. Lesson 4 is entirely about the difference between `b` and `c`.

</details>

2. ▢ Predict the output.

   ```rust
   struct Noisy(&'static str);
   impl Drop for Noisy {
       fn drop(&mut self) { println!("{}", self.0); }
   }

   fn main() {
       let _first = Noisy("first");
       {
           let _inner = Noisy("inner");
       }
       let _last = Noisy("last");
   }
   ```

<details markdown="1"><summary>Hint</summary>

Handle the inner scope on its own, then apply reverse declaration order to what is left in `main`.

</details>

<details markdown="1"><summary>Check</summary>

`inner`, then `last`, then `first`.

The inner scope ends first, so `_inner` drops there. At the end of `main`, the remaining two drop in reverse declaration order, so `_last` before `_first`.

</details>

3. ▢ Where is the `String` dropped in each case?

   ```rust
   fn a(s: String) { println!("{s}"); }
   fn b(s: &String) { println!("{s}"); }

   fn main() {
       let s1 = String::from("x");
       a(s1);
       let s2 = String::from("y");
       b(&s2);
   }
   ```

<details markdown="1"><summary>Check</summary>

`s1`'s `String` is dropped at the end of `a`, because ownership moved there. `s2`'s is dropped at the end of `main`, because `b` only borrowed it.

That difference is visible in the signatures alone, which is the point: `String` means "I will take responsibility for this", and `&String` means "let me look at yours".

</details>

4. ▢ Which of these values needs an owner to be responsible for freeing something?

   - a) `let x: u64 = 9;`
   - b) `let v: Vec<u8> = vec![1, 2];`
   - c) `let t: (i32, bool) = (1, true);`
   - d) `let f: f64 = 1.5;`

<details markdown="1"><summary>Check</summary>

**b)** only.

`Vec` owns a heap allocation, so something has to free it. The other three are entirely stack data of a size known at compile time, so the frame ending is all the cleanup they need.

That split is exactly the line lesson 2 formalises: the values in a, c and d are `Copy`, and the `Vec` is not.

</details>

5. ▢ A lock guard is held for a long function and the lock needs releasing halfway through. Give the idiomatic answer, and say why it works.

<details markdown="1"><summary>Check</summary>

Call `drop(guard)` at the point the lock should be released, or put the guard in a smaller block so its scope ends there.

It works because releasing the lock *is* the guard's `Drop`, and `drop` is an ordinary function that takes its argument by value. Taking ownership and returning immediately runs the destructor at that point, which is the whole trick.

The block form is often better style, because the indentation shows a reader the region where the lock is held rather than relying on them noticing one line.

</details>

## Real-world reps

- [ ] Write the `Noisy` struct and experiment with drop order: two values in one scope, a nested block, a value moved into a function. Predict each ordering before running it.
- [ ] Write a function that takes a `String` by value and try to use the variable afterwards in `main`. Read the error carefully; lesson 2 is about that exact message.
- [ ] Tomorrow: for one function in any language you know that opens a file, write down where the file is closed. Then say who is responsible if the function returns early.

## Going further

- [What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html): the same ground, at more length, with the stack and heap diagrams
- [Destructors](https://doc.rust-lang.org/reference/destructors.html): the exact drop order, including struct fields and temporaries
- [Ownership and borrowing](../reference/ownership-and-borrowing.md): the rules and the error codes, for lookup
- [Glossary](../GLOSSARY.md): `Ownership` is pinned there, because reading it as garbage collection or as scoping is what makes the rest feel arbitrary
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
