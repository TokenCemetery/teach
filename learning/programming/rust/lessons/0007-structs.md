---
title: 7. Structs and Their Methods
description: A struct owns its fields, so what you put in one decides who has to keep it alive
type: lesson
---

# Lesson 7. Structs and Their Methods

**Mission link:** Every type you will design from here on is a struct, and the fields you choose for it decide, on the spot, whether the struct owns what it holds or merely borrows a look at someone else's data.
**Primary source:** [The Rust Programming Language, Using Structs to Structure Related Data](https://doc.rust-lang.org/book/ch05-00-structs.html)
**Prerequisites:** [Lesson 1](0001-ownership-and-drop.md), [Lesson 3](0003-borrowing.md)

## Warm-up

1. ▢ In one sentence, what happens to a value when its one owner goes out of scope?

<details markdown="1"><summary>Check</summary>

It is dropped: its destructor runs and whatever it owns is released. A struct's fields are no exception, which is this lesson's subject.

</details>

2. ▢ State the borrow rule from lesson 3 in one sentence.

<details markdown="1"><summary>Check</summary>

Any number of shared borrows or exactly one mutable borrow, never both, and a borrow must stay valid for as long as it is used. It is the rule that decides what a `&self` method may do and what a struct built from borrowed fields is allowed to outlive.

</details>

## Know this

From this lesson on, the stage's reps build one small project a piece at a time: a command-line log summariser called `logsum`, which reads request lines, notes and blank lines from a text stream and reports how many of each it saw. The full brief lives in the project reference sheet; this lesson's reps start it, and the named-field struct below is close to the record type it will need.

### The three shapes a struct can take

A named-field struct is the ordinary case: each field has a name, and that name is how you read and write it.

```rust
struct Request {
    path: String,
    status: u16,
    bytes: u64,
}

fn main() {
    let path = String::from("/index");
    let status = 200;
    let bytes = 1200;
    let r = Request { path, status, bytes }; // field init shorthand
    println!("{} {} {}", r.path, r.status, r.bytes);
}
```

That program compiles and prints `/index 200 1200`. `Request { path, status, bytes }` is field init shorthand: when a local binding has the same name as the field, you do not repeat it as `path: path`.

A tuple struct is for a small, unnamed grouping where position is the only structure worth having, such as a pair of coordinates: `struct Point(f64, f64);`, read back with `.0` and `.1`. A unit struct carries no data at all, `struct Marker;`, and exists purely as a distinct type, for example to mark that some other piece of code has already run. All three compile side by side with no conflict between them.

### Ownership is a decision you make per field

This is the real subject of the lesson, and the reason it opens the stage. A struct does not have its own ownership rule; it inherits whatever rule its fields have, one field at a time. Give `Request` a `String` field and the struct owns that text, drops it when the struct is dropped, and needs nothing else from you: that is lesson 1's one-owner rule, now applied to a field instead of a bare binding. The version above already does this.

The other option is to store a borrow instead of an owned value:

```rust
struct Request {
    path: &str,
    status: u16,
    bytes: u64,
}
```

That alone does not compile:

```
error[E0106]: missing lifetime specifier
 --> src/bin/l7_borrowed.rs:2:11
  |
2 |     path: &str,
  |           ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
```

A borrowed field means the struct only points at text someone else owns, so the compiler needs a promise about how long that text outlives the struct, and it will not guess one. Writing that promise is a lifetime annotation on the struct itself, `struct Request<'a> { path: &'a str, ... }`, and that belongs to stage 4, not this one. The project's own stage table names exactly where: stage 4 is where the project stops owning a copy of every field and starts borrowing the line instead.

For stage 2, the rule is: **own your fields.** A `String` costs an allocation a `&str` would not, but it removes the question "how long does this struct live" from every use site. Reach for a borrowed field once you have a reason tied to a measured cost, and once lesson 4's stage has given you the tool to write it correctly.

### `impl` blocks: what each receiver lets you do

Methods live in an `impl` block, and the first parameter says what kind of access the method gets to the value it is called on.

```rust
struct Request {
    path: String,
    status: u16,
    bytes: u64,
}

impl Request {
    fn new(path: String, status: u16, bytes: u64) -> Self {
        Self { path, status, bytes }
    }

    fn is_success(&self) -> bool {
        self.status < 400
    }

    fn mark_seen(&mut self) {
        self.status = 0;
    }

    fn into_path(self) -> String {
        self.path
    }
}
```

`new` takes no `self` at all, so it is an associated function rather than a method, called as `Request::new(..)`. `Self` in its return type is an alias for `Request`; writing it out avoids repeating the type name and keeps a rename to one place. `is_success` takes `&self`: it reads the value and cannot change it. `mark_seen` takes `&mut self`: it may read and write. `into_path` takes `self` outright, so the call consumes the value.

The receiver is not a suggestion. Change `mark_seen` to take `&self` while it still assigns to `self.status` and the compiler refuses it:

```
error[E0594]: cannot assign to `self.status`, which is behind a `&` reference
  --> src/bin/l7_immut_fail.rs:13:9
   |
13 |         self.status = 0;
   |         ^^^^^^^^^^^^^^^ `self` is a `&` reference, so it cannot be written to
   |
help: consider changing this to be a mutable reference
```

And calling a `self`-consuming method a second time is rejected too, because the first call moved the value away:

```
error[E0382]: use of moved value: `r`
  --> src/bin/l7_consume_fail.rs:16:14
   |
15 |     let p1 = r.into_path();
   |                ----------- `r` moved due to this method call
16 |     let p2 = r.into_path();
   |              ^ value used here after move
```

Both diagnostics are lesson 2's move rule and lesson 3's borrow rule showing up again, now enforced through a method call instead of a bare assignment. Choose `&self` for anything that only reads, `&mut self` for anything that updates in place, and `self` only when the method's whole purpose is to consume the value and hand back something built from its pieces, as `into_path` does.

### Deriving what you need

Four traits cover almost everything a plain data struct needs, and all four can be asked for with `#[derive(...)]` instead of written by hand.

```rust
#[derive(Debug, Clone, PartialEq, Default)]
struct Request {
    path: String,
    status: u16,
    bytes: u64,
}
```

`Debug` is what `{:?}` needs to print a value; without it, printing fails to compile rather than at run time:

```
error[E0277]: `Request` doesn't implement `Debug`
 --> src/bin/l7_derive_fail.rs:8:15
  |
8 |     println!("{r:?}");
  |               ^^^^^ `Request` cannot be formatted using `{:?}` because it doesn't implement `Debug`
  |
help: consider annotating `Request` with `#[derive(Debug)]`
```

With the derive in place, `println!("{r:?}")` prints `Request { path: "/index", status: 200, bytes: 1200 }`. `Clone` gives you `.clone()`, which for this struct means allocating a fresh `String` and copying the bytes into it: real work, proportional to the size of `path`, not free the way copying an `i32` is. `PartialEq` gives you `==`; comparing `r` to `r.clone()` gives `true`. `Default` gives you `Request::default()`, which builds `Request { path: String::new(), status: 0, bytes: 0 }` using each field's own default, printed as `Request { path: "", status: 0, bytes: 0 }`.

### Update syntax moves what it copies from

Struct update syntax builds a new value from an old one, naming only the fields that differ:

```rust
#[derive(Debug)]
struct Summary {
    path: String,
    requests: u32,
}

let old = Summary { path: String::from("/index"), requests: 2 };
let new = Summary { requests: 4, ..old };
```

`..old` fills `path` in from `old`. If `path` were `Copy`, `old` would still be usable afterwards, the way lesson 2 describes for plain data. `String` is not `Copy`, so `path` is moved out of `old` into `new`, and using `old` afterwards fails:

```
error[E0382]: borrow of partially moved value: `old`
  --> src/bin/l7_update_move.rs:11:16
   |
 9 |     let new = Summary { requests: 4, ..old };
   |               ------------------------------ value partially moved here
11 |     println!("{old:?}");
   |                ^^^ value borrowed here after partial move
   |
   = note: partial move occurs because `old.path` has type `String`, which does not implement the `Copy` trait
```

This is lesson 2's move rule again, applied field by field: `..old` moves only the fields it reads, and any that are not `Copy` take `old` down with them. If you need both values afterwards, clone the field you are reusing rather than the whole struct.

### Layout: what `size_of` promises and what it does not

`std::mem::size_of::<Request>()` reports 40 on this target, for the three-field struct above. That number is the whole struct, `String` included, and it is specific to this machine's pointer width; nothing here is a promise about another target.

What the type does not promise is that fields sit in memory in declaration order. A struct with an `u8`, then a `u64`, then another `u8` reports a size of 16 on this target, and `std::mem::offset_of!` shows why: the `u64` field sits at offset 0 and the two `u8` fields land at offsets 8 and 9, even though the `u64` was declared second. The compiler is free to reorder fields to reduce padding; the [Rust Reference](https://doc.rust-lang.org/reference/type-layout.html) guarantees only that a field's offset is a multiple of its alignment and that fields do not overlap, never declaration order. A representation attribute such as `#[repr(C)]` would fix the order, but nothing here needs one.

## Practice

1. ▢ Which of these compile?

   ```rust
   // A
   struct Point(f64, f64);
   let p = Point(1.0, 2.0);
   println!("{} {}", p.0, p.1);

   // B
   struct Marker;
   let _m = Marker;

   // C
   struct Pair { left: &str, right: &str }
   ```

<details markdown="1"><summary>Check</summary>

A and B compile: a tuple struct read back by position, and a unit struct with no data at all. C does not: `error[E0106]`, a missing lifetime specifier on `left`, for the same reason the borrowed-field example in this lesson fails.

</details>

2. ▢ Predict whether this compiles, then say which line the error points at.

   ```rust
   struct Request { path: String, status: u16 }

   impl Request {
       fn mark_seen(&self) {
           self.status = 0;
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Look at the receiver, not at the field.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile. `error[E0594]`, pointing at `self.status = 0`, because `&self` grants read access only. Changing the receiver to `&mut self` is the fix, and nothing else about the method needs to change.

</details>

3. ▢ Predict what happens, and name the error code.

   ```rust
   struct Request { path: String }

   impl Request {
       fn into_path(self) -> String { self.path }
   }

   let r = Request { path: String::from("/index") };
   let a = r.into_path();
   let b = r.into_path();
   ```

<details markdown="1"><summary>Check</summary>

It does not compile. The first call to `into_path` moves `r` away, since the method takes `self` rather than `&self`. The second call is `error[E0382]`, use of a moved value. A `self`-consuming method can only be called once per value.

</details>

4. ▢ Predict the error, then predict the printed output once it is fixed.

   ```rust
   struct Request { path: String, status: u16 }

   let r = Request { path: String::from("/index"), status: 200 };
   println!("{r:?}");
   ```

<details markdown="1"><summary>Check</summary>

`error[E0277]`: `Request` does not implement `Debug`, so `{:?}` has nothing to call. Adding `#[derive(Debug)]` above the struct fixes it, and the printed line is `Request { path: "/index", status: 200 }`.

</details>

5. ▢ Predict whether both `println!` calls succeed, and if not, which one fails and why.

   ```rust
   #[derive(Debug)]
   struct Summary { path: String, requests: u32 }

   let old = Summary { path: String::from("/index"), requests: 2 };
   let new = Summary { requests: 4, ..old };
   println!("{new:?}");
   println!("{old:?}");
   ```

<details markdown="1"><summary>Hint</summary>

Ask which field `..old` has to move, and whether that field is `Copy`.

</details>

<details markdown="1"><summary>Check</summary>

The first `println!` succeeds. The second fails with `error[E0382]`, a partially moved value: `..old` moved `old.path` into `new` because `String` is not `Copy`, so `old` as a whole is no longer usable, even though `old.requests` on its own would still have been fine.

</details>

## Real-world reps

- [ ] Create the `logsum` crate with `cargo new logsum`, then define a `Request` struct with owned fields for a path, a status and a byte count, matching the project's request-line format. Give it a constructor named `new` that takes ownership of its arguments and returns `Self`, and derive `Debug` so you can build one and print it with `{:?}`.
- [ ] Reproduce the field-reordering example with a struct of your own, mixing a couple of small fields with one larger one, and check with `size_of` and `offset_of!` whether the compiler reordered them the way you expected.
- [ ] Tomorrow: from memory, write one sentence each for what `&self`, `&mut self` and `self` permit, then check all three against this lesson.

## Going further

- [Methods](https://doc.rust-lang.org/book/ch05-03-method-syntax.html): `impl` blocks, the three receivers, and associated functions
- [Default](https://doc.rust-lang.org/std/default/trait.Default.html): the trait `#[derive(Default)]` implements, and how to write it by hand
- [Type layout](https://doc.rust-lang.org/reference/type-layout.html): what the default representation guarantees about field order and padding, and what it does not
- [E0382](https://doc.rust-lang.org/error_codes/E0382.html): the use-after-move error, with a minimal reproduction
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
