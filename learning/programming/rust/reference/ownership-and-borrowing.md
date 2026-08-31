---
title: Ownership and Borrowing
description: The rules, the Copy list, the error codes, and the honest fix for each
type: reference
---

# Ownership and Borrowing

Lookup sheet for stage 1. The question it exists to answer: **why was this rejected, and what is the fix that is not a clone?**

## The rules

1. Every value has exactly one **owner**.
2. When the owner goes out of scope, the value is **dropped**.
3. At any point, a value has either any number of shared borrows (`&T`) or exactly one mutable borrow (`&mut T`), never both.
4. Every borrow must be valid for as long as it is used.

A borrow ends at its **last use**, not at the end of the scope.

## Move or copy

| Assignment or argument passing | Result |
|---|---|
| type is `Copy` | value duplicated, both names usable |
| type is not `Copy` | ownership moved, old name unusable |
| `&T` passed | copied, since `&T` is `Copy` |
| `&mut T` passed to a function | implicitly reborrowed, original usable after the call |
| `&mut T` stored in a struct | genuinely moved; use `&mut *r` to reborrow explicitly |

### `Copy` or not

| `Copy` | Not `Copy` |
|---|---|
| `i8` to `i128`, `u8` to `u128`, `usize`, `isize` | `String`, `Vec<T>`, `Box<T>`, `HashMap` |
| `f32`, `f64`, `bool`, `char` | `&mut T` |
| `&T` | anything implementing `Drop` |
| tuples and arrays of `Copy` types | any struct or enum without `#[derive(Copy)]` |
| `Option<T>`, `Result<T, E>` with `Copy` contents | closures capturing by move |

`Copy` requires `Clone`. A type with a `Drop` implementation can never be `Copy`.

## Owned against borrowed

| Owned | Borrowed | Take this in a signature |
|---|---|---|
| `String` | `&str` | `&str` |
| `Vec<T>` | `&[T]` | `&[T]` |
| `[T; N]` | `&[T]` | `&[T]` |
| `PathBuf` | `&Path` | `&Path` |
| `Box<T>` | `&T` | `&T` |

Rule of thumb: **take the borrowed form, return the owned form.** Deref coercion means a caller holding the owned type passes it with `&` and keeps it.

## Error codes

| Code | Headline | Honest fix |
|---|---|---|
| `E0382` | use of moved value | change the signature to borrow, or return the value back |
| `E0499` | two mutable borrows | end one sooner, or split the data |
| `E0502` | mutable while shared | move the last use of the shared borrow earlier, or copy the value out |
| `E0505` | move out while borrowed | end the borrow before the move |
| `E0596` | cannot borrow as mutable | add `mut` to the binding |
| `E0106` | missing lifetime specifier | stage 4: say how long the reference is valid |
| `E0515` | returns a reference to local data | return an owned value instead |

`rustc --explain E0502` prints the page offline.

## Reading the message

Three spans matter, and the third is the useful one:

1. where the first borrow began,
2. where the conflicting borrow or move is,
3. **where the first borrow is still used**, which is what keeps it alive.

If span 3 can move above span 2, the error disappears with no restructuring.

## The four honest fixes

1. **End the borrow sooner.** Move the last use up, or wrap it in a block.
2. **Copy the value out.** `let x = v[0];` for a `Copy` element retains no borrow.
3. **Borrow in the signature.** `&str` instead of `String`, `&[T]` instead of `Vec<T>`.
4. **Restructure.** Split a struct, or compute before mutating instead of interleaving.

## The four workarounds

| Workaround | Legitimate when | Cost otherwise |
|---|---|---|
| `.clone()` | two independent values are wanted | allocation, and values that silently diverge |
| `Rc<RefCell<T>>` | shared ownership is the real design | compile-time check becomes a run-time panic; not thread-safe |
| indices instead of references | traversing while mutating | no bounds guarantee; stale indices |
| `unsafe` | not at this stage | undefined behaviour, and the rules still apply |

## Disjoint fields

The compiler borrows **fields** separately:

```rust
let name = &self.config.name;      // borrows self.config
self.cache.insert(name);           // mutates self.cache: fine
```

A method call taking `&self` borrows **all** of `self`, which loses that precision:

```rust
let name = self.name();            // borrows all of self
self.cache.insert(name);           // E0502
```

Fixes: read the field directly, return an owned value from the method, or split the struct.

## Drop order

- Within a scope: **reverse declaration order**.
- A struct: its own `Drop::drop` first, then its fields in declaration order.
- Early release: `drop(value)`, an ordinary function that takes ownership.

## Sources

- [What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
- [References and Borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
- [The Slice Type](https://doc.rust-lang.org/book/ch04-03-slices.html)
- [Destructors](https://doc.rust-lang.org/reference/destructors.html)
- [Rust Compiler Error Index](https://doc.rust-lang.org/error_codes/error-index.html)
- [Aliasing, The Rustonomicon](https://doc.rust-lang.org/nightly/nomicon/aliasing.html)
