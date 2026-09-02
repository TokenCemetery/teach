---
title: 11. Pattern Matching
description: A match must cover every case, and the pattern decides whether you borrowed the value or moved it
type: lesson
---

# Lesson 11. Pattern Matching

**Mission link:** A `match` that silently ignores a variant either panics later or keeps running on a case nobody planned for; a `match` that moves a value you meant to keep forces a `clone` you did not need. Both are avoidable once exhaustiveness and binding modes are things you reason about rather than guess at.
**Primary source:** [The Rust Reference, Patterns](https://doc.rust-lang.org/reference/patterns.html)
**Prerequisites:** [Lesson 8](0008-enums.md), [Lesson 2](0002-moves-and-copy.md)

## Warm-up

1. ▢ In lesson 8, matching `Line::Note(text)` on `line` by value moved the `String` out, so `line` could not be printed afterwards, but matching on `&line` instead left `line` intact and printable. What changed between the two matches?

<details markdown="1"><summary>Check</summary>

Matching `line` by value hands the arms the enum itself, so binding `text` inside `Note` moves that payload out, the same as moving any owned value out of a container. Matching `&line` gives the arms only a reference, so there is nothing to move; `text` borrows the payload instead. This lesson's binding-modes section names that difference and shows exactly how the compiler decides which one you get.

</details>

2. ▢ When `a` is a `String` and you write `let b = a;`, why can you no longer use `a`?

<details markdown="1"><summary>Check</summary>

Assignment moves ownership for a type that is not `Copy`, so `a` is left with nothing once `b` owns the value. That is the whole rule the binding-modes section turns on: whether a pattern moves a value out or only borrows it is this exact rule, applied inside a `match` arm instead of a plain `let`.

</details>

## Know this

### Exhaustiveness is the compiler's promise

A `match` needs an arm for every value the scrutinee's type can hold. Drop a variant and the compiler refuses to compile, rather than let the missing case surface as a bug in production:

```rust
enum State {
    Draft,
    Published,
    Archived,
}

fn label(s: &State) -> &'static str {
    match s {
        State::Draft => "draft",
        State::Published => "published",
    }
}
```

```text
error[E0004]: non-exhaustive patterns: `&State::Archived` not covered
  --> src/main.rs:9:11
   |
 9 |     match s {
   |           ^ pattern `&State::Archived` not covered
   |
note: `State` defined here
  --> src/main.rs:2:6
   |
 2 | enum State {
   |      ^^^^^
...
 5 |     Archived,
   |     -------- not covered
   = note: the matched value is of type `&State`
help: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
   |
11 ~         State::Published => "published",
12 ~         &State::Archived => todo!(),
   |
```

The note points straight at the variant the enum's definition promises and the arm never delivered, and the help even offers `todo!()`: you can defer the decision, but you cannot skip acknowledging it.

There are two honest ways to satisfy this promise, and one way that throws it away. Cover every variant by name, which is what you want whenever each case needs different handling. Reach for `_` when the rest is genuinely uninteresting, such as counting only the `Archived` case; `_` said on purpose, next to a comment saying why, is a design choice. What is not honest is writing `_ => unreachable!()` on an enum you own, on the theory that every variant is already listed. Adding an eleventh variant next year should be a compile error at every `match` that needs updating, not a panic discovered by whoever hits the new case first. Say that plainly: exhaustiveness on your own enum is where this earns its keep, and trading it for a shorter `match` is a bad deal.

### The patterns worth knowing

Each of these answers a specific question a `match` arm needs to ask.

Is it exactly this value? A literal pattern:

```rust
match 2 {
    1 => println!("one"),
    2 => println!("two"),
    _ => println!("other"),
}
```

prints `two`.

Is it within a range? `..=` is inclusive on both ends:

```rust
match 'k' {
    'a'..='j' => println!("early"),
    'k'..='z' => println!("late"),
    _ => println!("not lowercase"),
}
```

prints `late`.

Is it one of several values that all deserve the same arm? `|` alternatives:

```rust
match 5 {
    1 | 3 | 5 | 7 | 9 => println!("odd digit"),
    _ => println!("other"),
}
```

prints `odd digit`.

Which fields do I need, and can I ignore the rest? Struct destructuring, named and with `..`:

```rust
struct Point { x: i32, y: i32, z: i32 }
let p = Point { x: 1, y: 2, z: 3 };
let Point { x, y, .. } = p;
println!("{x} {y}");
```

prints `1 2`; naming `z` was never needed, and `..` says so instead of a throwaway binding.

What are the positional parts? Tuples and tuple structs, by position:

```rust
struct Wrapper(i32, i32);
let (a, b) = (10, 20);
let Wrapper(w0, w1) = Wrapper(7, 8);
println!("{a} {b} {w0} {w1}");
```

prints `10 20 7 8`; a tuple struct is destructured exactly like a tuple, just naming the type first.

What does a value made of several parts look like all at once? Patterns nest:

```rust
let pair = (Some(3), None::<i32>);
match pair {
    (Some(x), None) => println!("first {x}, second absent"),
    _ => println!("other"),
}
```

prints `first 3, second absent`, checking the shape of both tuple slots and the `Option` inside each in one arm.

Can I match a range and still keep the whole value? `@` bindings:

```rust
match 15 {
    n @ 13..=19 => println!("teen {n}"),
    _ => println!("not a teen"),
}
```

prints `teen 15`; without `@`, matching the range would tell you it matched but not what the value was.

Is the shape not enough, and I need to compare two of its parts? A guard:

```rust
match (4, 4) {
    (x, y) if x == y => println!("equal {x}"),
    (x, y) => println!("different {x} {y}"),
}
```

prints `equal 4`. A guard runs arbitrary code after the shape matches, which a pattern alone cannot express.

### Binding modes, and what changed in 2024

Every pattern above bound a name by value, since the scrutinee was owned. Matching a reference triggers a second rule: a non-reference pattern matched against a reference borrows the contents instead of moving them.

```rust
#[derive(Debug)]
enum Record {
    Note(String),
    Blank,
}

let record = Record::Note(String::from("deploy started"));
match &record {
    Record::Note(text) => println!("{text}"),
    Record::Blank => {}
}
println!("still have it: {record:?}");
```

This compiles and prints `deploy started` followed by `still have it: Note("deploy started")`, because `&record` is a `&Record`, the arm pattern `Record::Note(text)` is not a reference pattern, and the compiler responds by binding `text` as `&String` rather than moving the `String` out. Nothing was moved, so `record` is still whole afterwards. This is the difference the warm-up asked about, now with a name: the compiler threads a `ref` binding through the match on your behalf, the same thing the older syntax below used to say explicitly.

The 2024 edition tightened one corner of this: an explicit `&` pattern may no longer mix with that implicit borrowing. Take a tuple whose second slot already holds a reference:

```rust
let x = 3;
let pair = (1, &x);
let r = &pair;
match r {
    (_, &b) => println!("{b}"),
}
```

Edition 2021 compiles this and prints `3`: the outer tuple pattern implicitly borrows through `r`, and `&b` dereferences the already-borrowed second slot. Edition 2024 rejects the identical code:

```text
error: cannot explicitly dereference within an implicitly-borrowing pattern
 --> src/main.rs:6:13
  |
6 |         (_, &b) => println!("{b}"),
  |             ^ reference pattern not allowed when implicitly borrowing
  |
  = note: for more information, see <https://doc.rust-lang.org/reference/patterns.html#binding-modes>
note: matching on a reference type with a non-reference pattern implicitly borrows the contents
 --> src/main.rs:6:9
  |
6 |         (_, &b) => println!("{b}"),
  |         ^^^^^^^ this non-reference pattern matches on a reference type `&_`
help: match on the reference with a reference pattern to avoid implicitly borrowing
  |
6 |         &(_, &b) => println!("{b}"),
  |         +
```

Two spellings still compile on 2024, both printing `3`: take the help's suggestion and add the outer `&` so every level is an explicit reference pattern, `&(_, &b)`, or drop the inner `&` and dereference at the point of use instead, `(_, b) => *b`. Verified on rustc 1.98.0, edition 2024 against edition 2021, using the workspace's two edition-comparison crates: the mixed pattern is accepted on the 2021 crate and rejected on the 2024 crate with the message just quoted. A pattern copied from an older tutorial that mixes an explicit `&` with an implicit borrow is the single most likely thing here to stop compiling after an edition upgrade.

### `ref` and `ref mut`

Before binding modes existed, `ref` and `ref mut` were how you said "borrow this, do not move it" inside a pattern, and they still work:

```rust
let record = Some(String::from("deploy started"));
match record {
    Some(ref text) => println!("{text}"),
    None => {}
}
println!("{record:?}");
```

prints the note followed by `Some("deploy started")`, because `ref text` borrows the payload out of an owned `Option<String>` rather than moving it, leaving `record` usable afterwards. Worth reading, since existing code uses it constantly, but rarely what you write today: matching a reference to begin with, `match &record`, gets the same borrow through binding modes with no extra keyword. `ref mut` is the same idea for a mutable borrow.

### Where else a pattern appears

A `let` binding is itself a pattern, which is why `let (a, b) = pair;` destructures a tuple in one line: the left-hand side of every `let` is a pattern, ordinarily just a single irrefutable name. A function parameter is a pattern too:

```rust
fn add((a, b): (i32, i32)) -> i32 {
    a + b
}
```

compiles and `add((3, 4))` gives `7`, destructuring the tuple argument before the body even starts.

The rule deciding which construct accepts which pattern is refutability: irrefutable means the pattern matches every value of its type, refutable means some value could fail to match. `let`, a function parameter and a `for` loop's binding all require an irrefutable pattern, because there is nothing sensible left to do if the match fails. Try it anyway:

```rust
let n: Option<i32> = Some(5);
let Some(x) = n;
```

```text
error[E0005]: refutable pattern in local binding
 --> src/main.rs:7:9
  |
7 |     let Some(x) = n;
  |         ^^^^^^^ pattern `None` not covered
  |
  = note: `let` bindings require an "irrefutable pattern", like a `struct` or an `enum` with only one variant
  = note: for more information, visit https://doc.rust-lang.org/book/ch19-02-refutability.html
  = note: the matched value is of type `Option<i32>`
help: you might want to use `let...else` to handle the variant that isn't matched
  |
7 |     let Some(x) = n else { todo!() };
  |                     ++++++++++++++++
```

`if let` and `while let` exist precisely because they accept a refutable pattern: `if let Some(x) = n { ... }` runs the block only on a match and otherwise does nothing, and `while let Some(top) = stack.pop() { ... }` keeps popping until the pattern fails. `let ... else`, from lesson 9, is the third refutable construct, forcing the failure branch to diverge rather than letting it fall through silently.

### Let chains, and `matches!`

A let chain joins several `let` patterns and plain boolean conditions with `&&` in one `if` or `while`, which used to need nested `if let` blocks:

```rust
let a: Option<i32> = Some(3);
let b: Option<i32> = Some(5);
if let Some(x) = a && let Some(y) = b && x < y {
    println!("{x} < {y}");
}
```

This compiles and prints `3 < 5` on edition 2024. The same line on edition 2021 fails outright:

```text
error: let chains are only allowed in Rust 2024 or later
 --> src/main.rs:4:8
  |
4 |     if let Some(x) = a && let Some(y) = b && x < y {
  |        ^^^^^^^^^^^^^^^
```

with a second, identical error pointing at the second `let`. The 1.88.0 release announcement names let chains as stabilised there, with edition 2024 a requirement rather than a recommendation, because the feature depends on a temporary-scope change only that edition made. Before this, the same condition needed nesting: `if let Some(x) = a { if let Some(y) = b { if x < y { ... } } }`, three levels deep for three conditions instead of one line.

`matches!` is for the times a full `match` is overkill and a plain `bool` is all you want:

```rust
let n: Option<i32> = Some(7);
println!("{}", matches!(n, Some(x) if x > 5));
println!("{}", matches!(n, None));
```

prints `true` then `false`; it takes a pattern, an optional guard, and gives back whether the value matched, without writing out every other arm.

## Practice

1. ▢ Predict whether this compiles, and if not, which variant the compiler names.

   ```rust
   enum Shape {
       Circle(f64),
       Square(f64),
       Triangle(f64, f64, f64),
   }

   fn area(s: &Shape) -> f64 {
       match s {
           Shape::Circle(r) => std::f64::consts::PI * r * r,
           Shape::Square(side) => side * side,
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

It does not compile: `error[E0004]: non-exhaustive patterns: `&Shape::Triangle(_, _, _)` not covered`, with a note pointing at `Triangle`'s definition. Adding the third arm, rather than a `_`, is the honest fix: a triangle's area needs its own formula, and a wildcard would hide that rather than handle it.

</details>

2. ▢ Predict what each line prints, then compile and check.

   ```rust
   let point = (5, -3);
   match point {
       (0, 0) => println!("origin"),
       (x, 0) => println!("on the x axis at {x}"),
       (0, y) => println!("on the y axis at {y}"),
       (x, y) if x == y => println!("on the diagonal"),
       (x, y) => println!("elsewhere: {x}, {y}"),
   }
   ```

<details markdown="1"><summary>Check</summary>

`elsewhere: 5, -3`. Neither coordinate is zero and they are not equal, so the first four arms fail and the catch-all fires. Order matters here: a specific arm has to come before the general one it would otherwise make unreachable.

</details>

3. ▢ This binds a `String` payload while matching by value, then tries to use the enum again. Predict the error code, then compile it.

   ```rust
   enum Job { Queued(String), Done }

   fn main() {
       let job = Job::Queued(String::from("build"));
       match job {
           Job::Queued(name) => println!("{name}"),
           Job::Done => {}
       }
       println!("{job:?}");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`Job` needs `#[derive(Debug)]` before this compiles even that far; add it, then think about what matching `job` by value does to the binding named `job`.

</details>

<details markdown="1"><summary>Check</summary>

`error[E0382]: borrow of partially moved value: `job``. Matching `job` by value moves the enum into the match, and binding `name` moves the `String` payload out of it, so nothing is left to print. Matching `&job` instead, so `name` binds a `&String`, fixes it without cloning.

</details>

4. ▢ Predict whether this compiles on edition 2024, then on edition 2021, and why they differ.

   ```rust
   let items: Vec<i32> = vec![1, 2, 3];
   let first = items.first();
   if let Some(&n) = first && n > 0 {
       println!("{n}");
   }
   ```

<details markdown="1"><summary>Check</summary>

It compiles on edition 2024, printing `1`, and fails on edition 2021 with `error: let chains are only allowed in Rust 2024 or later`. The `&n` pattern itself is fine on both editions; what 2021 rejects is chaining a `let` with `&&` inside the `if` condition at all.

</details>

5. ▢ Write `matches!` in place of this `match`, predict that both give the same answer, then compile both.

   ```rust
   let code = 404;
   let is_client_error = match code {
       400..=499 => true,
       _ => false,
   };
   ```

<details markdown="1"><summary>Hint</summary>

`matches!` takes the value first and the pattern second, and a range pattern needs no guard here.

</details>

<details markdown="1"><summary>Check</summary>

```rust
let is_client_error = matches!(code, 400..=499);
```

Both give `true` for `404`. The `match` version spells out the two outcomes by hand; `matches!` says directly that the only thing being asked is whether the shape matches.

</details>

## Real-world reps

- [ ] In your `logsum` crate, replace the summariser's if-else chain that decides what a line is with a single `match` over your `Line` enum, one arm per variant and no `_`. A non-exhaustive error the day you add a variant is this lesson working as intended.
- [ ] In that same match, check whether each binding is a `&String` or a moved `String`, and change the match style if the ownership was not what you meant.
- [ ] Tomorrow: write a three-variant enum from memory, write a `match` over it that compiles, then delete one arm and read the exhaustiveness error before running anything through an editor's linter.

## Going further

- [Refutability: Whether a Pattern Might Fail to Match](https://doc.rust-lang.org/book/ch19-02-refutability.html): the rule behind which construct accepts which pattern
- [E0004](https://doc.rust-lang.org/error_codes/E0004.html): the non-exhaustive-match code, with a minimal reproduction
- [E0005](https://doc.rust-lang.org/error_codes/E0005.html): the refutable-pattern-in-`let` code
- [Announcing Rust 1.88.0](https://blog.rust-lang.org/2025/06/26/Rust-1.88.0/): the release that stabilised let chains
- [matches in std](https://doc.rust-lang.org/std/macro.matches.html): the macro's exact signature and guard support
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
