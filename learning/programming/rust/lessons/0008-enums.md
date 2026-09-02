---
title: 8. Enums That Carry Data
description: An enum says a value is exactly one of these shapes, which is the modelling tool the rest of the stage rests on
type: lesson
---

# Lesson 8. Enums That Carry Data

**Mission link:** A struct with several optional fields cannot say which combinations are meaningful, so every call site has to be read to find out; an enum makes the meaningless combinations impossible to construct, turning a bug a reviewer might miss into one the compiler catches.
**Primary source:** [The Rust Programming Language, Enums and Pattern Matching](https://doc.rust-lang.org/book/ch06-00-enums.html)
**Prerequisites:** [Lesson 2](0002-moves-and-copy.md), [Lesson 7](0007-structs.md)

## Warm-up

1. ▢ A `Request` struct with a `path: String` field goes out of scope. What happens to the `String`, and why does nobody have to call anything for it to happen?

<details markdown="1"><summary>Check</summary>

A struct owns each of its fields, so dropping the struct drops every field along with it, the `String` included. That is ownership doing the cleanup with no runtime bookkeeping, the same rule lesson 7 established for a struct's own fields.

</details>

2. ▢ When `a` is a `String` and you write `let b = a;`, why can you no longer use `a`? Would the same be true if `a` were a `u16`?

<details markdown="1"><summary>Check</summary>

Assignment moves ownership for a type that is not `Copy`, so `a` is moved into `b` and the old binding is gone. A `u16` is `Copy`, so the value is duplicated instead and both names stay usable. A variant's payload sits inside an enum exactly the way a field sits inside a struct, so it follows this same rule, which is what today's lesson checks.

</details>

## Know this

### What an enum is

In many languages an enum is a list of names with numbers behind them: a `Status` that is `PENDING`, `ACTIVE` or `DONE`, and nothing more can be true about it. Rust's enum is a different tool. A value of an enum type is exactly one of several named variants, and each variant is free to carry its own data in its own shape. Here is the shape the project needs, with all three kinds of variant in one type:

```rust
#[derive(Debug)]
enum Line {
    Blank,
    Note(String),
    Request { path: String, status: u16, bytes: u64 },
}
```

`Blank` carries nothing. `Note` carries one value reached by position, the way a tuple is. `Request` carries three named fields reached by name, the way a struct is, built from exactly the fields lesson 7 gave `Request`. Constructing one of each and printing them:

```rust
let a = Line::Blank;
let b = Line::Note(String::from("deploy started"));
let c = Line::Request { path: String::from("/index"), status: 200, bytes: 1200 };
println!("{a:?}\n{b:?}\n{c:?}");
```

prints:

```text
Blank
Note("deploy started")
Request { path: "/index", status: 200, bytes: 1200 }
```

Three shapes, one type, and the compiler always knows which one a given `Line` is.

### Making illegal states impossible

This is the argument for reaching for an enum instead of a struct with more fields. Take a type that tracks how someone is paying, with two optional fields:

```rust
struct OldPayment {
    card: Option<String>,
    paypal: Option<String>,
}
```

`OldPayment` permits four combinations: neither field set, only `card`, only `paypal`, or both set. The domain only ever means one of two things by "how is this person paying": by card, or by PayPal, never both and never neither, but nothing in the struct's definition says so; it compiles equally happily with both fields `Some`. An enum can only ever be one variant, so it says the same thing without a comment:

```rust
enum Payment {
    Card(String),
    PayPal(String),
}
```

Try to hand a single `Payment` both pieces of data, the way `OldPayment` let you:

```rust
let payment = Payment::Card(String::from("4111"), String::from("a@b.com"));
```

```text
error[E0061]: this enum variant takes 1 argument but 2 arguments were supplied
  --> src/main.rs:12:19
   |
12 |     let payment = Payment::Card(String::from("4111"), String::from("a@b.com"));
   |                   ^^^^^^^^^^^^^                       ----------------------- unexpected argument #2 of type `String`
```

(help and note trimmed). There is no longer any syntax for "both": a `Payment::Card` has room for the one string a card payment needs and nothing else. The illegal state has nowhere left to fit, which is a stronger guarantee than a comment or a runtime check could give.

### A variant's payload is owned like a struct field

A variant's payload is a value living inside the enum, owned the same way a field is owned inside a struct, and it moves the same way too. Construct a `Line::Note` and match on the enum by value:

```rust
let line = Line::Note(String::from("deploy started"));

match line {
    Line::Note(text) => println!("{text}"),
    _ => {}
}

println!("{line:?}");
```

```text
error[E0382]: borrow of partially moved value: `line`
  --> src/main.rs:16:16
   |
12 |         Line::Note(text) => println!("{text}"),
   |                    ---- value partially moved here
...
16 |     println!("{line:?}");
   |                ^^^^ value borrowed here after partial move
```

(note and help trimmed). Binding `text` inside the `Note` arm moves the `String` out of `line`, the same as moving a struct field out by value would, so `line` cannot be printed afterwards. Match on a reference instead and the payload is only borrowed:

```rust
match &line {
    Line::Note(text) => println!("{text}"),
    _ => {}
}

println!("{line:?}");
```

```text
deploy started
Note("deploy started")
```

Nothing here is a rule about `match` itself, which lesson 11 covers in full; it is the ownership rule you already know, applied to a value that happens to be sitting inside an enum's variant rather than inside a struct's field.

### What an enum costs

An enum's size is its largest variant's size plus a discriminant to say which variant this value is, rounded up to the type's alignment. Take a small enum built to make the arithmetic visible:

```rust
enum Reading {
    Missing,
    One(f64),
    Two(f64, f64),
}

println!("{}", std::mem::size_of::<Reading>());
```

```text
24
```

The largest variant, `Two`, carries sixteen bytes of payload; the discriminant adds a little more, rounded up to the eight-byte alignment its `f64` fields demand, landing on twenty-four rather than seventeen. Measuring the project's own `Line` gives a real number too:

```rust
println!("{}", std::mem::size_of::<Line>());
```

```text
40
```

which is exactly the size of a bare struct holding `Request`'s three fields with no enum wrapped around them: the compiler had six bytes of padding after `u16` to keep the trailing `u64` aligned, and tucked the discriminant into that gap for free. These are this target's numbers, not a promise the language makes about every enum.

One case is a documented promise rather than a target's coincidence: `Option<&T>` and `Option<Box<T>>` are exactly the size of the pointer they wrap.

```rust
println!("{} {}", std::mem::size_of::<Option<&u8>>(), std::mem::size_of::<&u8>());
println!("{} {}", std::mem::size_of::<Option<Box<u8>>>(), std::mem::size_of::<Box<u8>>());
println!("{}", std::mem::size_of::<Option<u8>>());
```

```text
8 8
8 8
2
```

A reference or a `Box` can never be a null pointer, so the standard library documents that the compiler may use that impossible all-zero pattern as `None`'s tag, at no extra cost. A plain `u8` has no such gap, so wrapping it in `Option` costs a byte: two rather than one. A recursive variant, one holding another value of its own enum, needs indirection through `Box` to have a size at all; that tool is stage 5's, so it waits until then.

### Methods on an enum

An `impl` block works on an enum exactly as it does on a struct, which is what keeps an enum a type with behaviour rather than a tagged blob a caller has to pick apart by hand:

```rust
impl Line {
    fn kind(&self) -> &'static str {
        match self {
            Line::Blank => "blank",
            Line::Note(_) => "note",
            Line::Request { .. } => "request",
        }
    }
}

let lines = [
    Line::Blank,
    Line::Note(String::from("deploy started")),
    Line::Request { path: String::from("/index"), status: 200, bytes: 1200 },
];
for line in &lines {
    println!("{}", line.kind());
}
```

```text
blank
note
request
```

`kind` takes `&self`, so calling it borrows the line rather than consuming it; the match inside is the smallest one that answers the question, and lesson 11 teaches `match` itself.

### Option and Result are enums too, and when a struct is simpler

Nothing about the standard library's two best-known types is special. They are ordinary enums, defined with the same keyword and the same variant shapes just covered, generic over the type or types they carry:

```rust
// both are ordinary enums, generic over the type or types they carry
enum Option<T> { None, Some(T) }
enum Result<T, E> { Ok(T), Err(E) }
```

`Option` pairs a payload-less variant with a one-payload variant; `Result` pairs two one-payload variants. Lesson 9 covers `Option`'s methods and lesson 10 covers `Result`'s methods and `?`; today's job was only the shape underneath them. None of this argues for an enum everywhere. If every field of a type is always present, a single-variant enum buys nothing: it is a struct with an extra `::Variant` at every construction site and every match, and no illegal state was ever on offer to rule out. Reach for an enum when a value is only ever one of several distinct shapes, and for a struct when it is one shape made of parts.

## Practice

1. ▢ Predict `std::mem::size_of::<Option<&str>>()` and `std::mem::size_of::<&str>()` before compiling, then check both.

<details markdown="1"><summary>Check</summary>

Both are sixteen, not eight. `&str` is a fat pointer, a data pointer plus a length, and the niche optimisation is not limited to thin pointers: the compiler still finds an impossible bit pattern to use as `None`'s tag, so wrapping it in `Option` costs nothing beyond what `&str` already costs.

</details>

2. ▢ Predict whether this compiles, then compile it and read the message.

   ```rust
   #[derive(Debug)]
   enum Shape {
       Blank,
       Note(String),
   }

   fn describe(s: Shape) -> String {
       match s {
           Shape::Note(text) => text,
           Shape::Blank => String::new(),
       }
   }

   fn main() {
       let s = Shape::Note(String::from("hi"));
       let text = describe(s);
       println!("{text}");
       println!("{s:?}");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`s` is passed to `describe` by value, the same as passing an owned struct would be. Ask what that does to the binding named `s` in `main`.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile:

```text
error[E0382]: borrow of moved value: `s`
```

The whole `Shape` moved into `describe`, not just the `String` inside it, so `main`'s own `s` is gone by the time the last line tries to print it. Passing `&s` and matching the reference instead would leave `main`'s binding usable.

</details>

3. ▢ A `Session` struct has two fields, `token: Option<String>` and `guest_name: Option<String>`; the domain rule is that a session is either signed in with a token or browsing as a guest with a name, never both and never neither. Rewrite `Session` as a two-variant enum, then say how many states each version actually permits.

<details markdown="1"><summary>Hint</summary>

List every combination the two `Option` fields can hold before you count how many of them the domain allows.

</details>

<details markdown="1"><summary>Check</summary>

The struct permits four states: neither field set, `token` only, `guest_name` only, or both set. The domain needs exactly two. An enum with `SignedIn(String)` and `Guest(String)` variants permits exactly those two; there is no combination left to construct for "both" or "neither".

</details>

4. ▢ Add a `label` method to the `Payment` enum from Know this, returning `"card"` or `"paypal"`. Predict the output of printing both labels, then compile and check.

<details markdown="1"><summary>Check</summary>

`card paypal`. The method takes `&self` and matches on the variant to pick the string, without needing to read either payload.

</details>

5. ▢ A colleague models a traffic light with a struct of three fields, `is_red: bool`, `is_yellow: bool`, `is_green: bool`. Give a one-sentence enum rewrite, and name one illegal state the struct allowed that the enum removes.

<details markdown="1"><summary>Check</summary>

`enum TrafficLight { Red, Yellow, Green }`, three payload-less variants, since the colour alone is the whole state. The struct allowed all eight boolean combinations, including all three lights on at once or all three off; the enum permits only the three the domain actually has.

</details>

## Real-world reps

- [ ] In your `logsum` crate, turn the `Request` struct from lesson 7 into a `Line` enum with three variants: `Blank`, `Note(String)` for a line starting with `#`, and `Request` carrying the same three named fields. Add a `kind(&self) -> &'static str` method returning `"blank"`, `"note"` or `"request"`.
- [ ] Take a type with two fields only ever meaningful together, or write a small one like the payment example, and rewrite it as an enum; try to construct the illegal combination and read what the compiler says.
- [ ] Tomorrow: without looking at this lesson, write from memory the three shapes an enum variant can carry, and state the compile-time cost of an enum in one sentence.

## Going further

- [Defining an Enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html): the three variant shapes, from the primary source's own book
- [std::option](https://doc.rust-lang.org/std/option/index.html): the "Representation" section, which documents which types get the null pointer optimisation
- [E0061](https://doc.rust-lang.org/error_codes/E0061.html): the "wrong number of arguments" code behind this lesson's illegal-state example
- [E0382](https://doc.rust-lang.org/error_codes/E0382.html): the "moved value" code behind this lesson's payload-ownership example
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
