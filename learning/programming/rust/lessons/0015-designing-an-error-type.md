---
title: 15. Designing an Error Type
description: A caller can only handle what your error lets them distinguish, so the shape of it is an API decision
type: lesson
---

# Lesson 15. Designing an Error Type

**Mission link:** A caller decides what to do next by matching on what your error type exposes, so a plain `String` or a single catch-all variant quietly removes their ability to retry a timeout differently from rejecting bad input. Shaping the type from your actual callers, not your function's internals, is the difference between an API a caller can build retry logic against and one that forces a grep through a message.
**Primary source:** [std::error::Error](https://doc.rust-lang.org/std/error/trait.Error.html)
**Prerequisites:** [Lesson 8](0008-enums.md), [Lesson 14](0014-propagating-errors.md)

## Warm-up

1. ▢ Lesson 8 established that a variant's payload is owned the way a struct's field is, and that two variants of one enum can carry different shapes of data. An error enum with one variant carrying `field: &'static str` and another carrying that plus a nested `std::num::ParseIntError` is exactly that. What does constructing either variant do to the values you put in it?

<details markdown="1"><summary>Check</summary>

It moves them in, the same as building a struct: the `&'static str` is copied since it is a reference, and the `ParseIntError` is moved and no longer usable from where it came. A variant carrying an error is a payload like any other.

</details>

2. ▢ Lesson 14 had you write `From` conversions so `?` could turn a foreign error into your own error type without a `.map_err` at every call site. What does a second kind of foreign error force you to add to your own error type, at minimum?

<details markdown="1"><summary>Check</summary>

A new variant, plus a `From` implementation converting into it, since `?` only compiles when the target is reachable through `From`. A type's variant count tends to grow with the failures it propagates, which is why deciding the variants is worth doing on purpose rather than leaving it to `?`.

</details>

## Know this

### Start from the caller

The only question that decides an error type's shape is what a caller might reasonably do differently for one failure than another, not how the code's internals are structured. Take a project's line parser, splitting a log line into a path and a byte count, and three callers. The summariser's main loop only decides whether to count a line as a request or bump a rejected-lines counter, so any `Result` satisfies it and says nothing about shape. A reporting mode bucketing rejections, such as "3 lines missing a field, 1 with a bad byte count", needs to distinguish which kind of failure happened, but not which field or what the parse error said. A mode for cleaning up a broken log source needs the field's name and the underlying error's message. Those two callers, not the parser's structure, justify this shape:

```rust
#[derive(Debug)]
enum ParseError {
    MissingField { field: &'static str },
    BadNumber { field: &'static str, source: std::num::ParseIntError },
}
```

Two variants for the second caller, a `field` name for the third, and a nested `source` on the variant wrapping a foreign error, again for the third. The first caller does not appear here at all, since "an error occurred" needs no distinguishing; a caller you cannot name is not a reason to add anything.

### The enum, and the two implementations that make it an error

An enum becomes an error with two implementations, both by hand here since the derive that generates them is next lesson's subject. `Display` is one `match` arm per variant, saying in words what went wrong:

```rust
use std::fmt;

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::MissingField { field } => write!(f, "missing field {field}"),
            ParseError::BadNumber { field, .. } => write!(f, "field {field} is not a number"),
        }
    }
}
```

`std::error::Error` adds one method worth writing deliberately: `source`, returning the wrapped error for the variant that has one and `None` otherwise.

```rust
impl std::error::Error for ParseError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            ParseError::MissingField { .. } => None,
            ParseError::BadNumber { source, .. } => Some(source),
        }
    }
}
```

Compiling and running both confirms what each variant reports:

```rust
let bad_number = parse("/index x").unwrap_err();
println!("display: {bad_number}");
println!("source: {:?}", bad_number.source().map(|s| s.to_string()));

let missing = parse("/index").unwrap_err();
println!("display: {missing}");
println!("source: {:?}", missing.source().map(|s| s.to_string()));
```

```text
display: field bytes is not a number
source: Some("invalid digit found in string")
display: missing field bytes
source: None
```

`MissingField` reports itself; `BadNumber` reports its own message and hands back the `ParseIntError` it wrapped, exactly what the third caller needed.

### Walking the chain, and what a message should not repeat

`source` lets a caller walk backwards through however many layers wrapped the failure, one `while let` away from a full report:

```rust
fn report(err: &dyn std::error::Error) {
    println!("error: {err}");
    let mut src = err.source();
    while let Some(s) = src {
        println!("caused by: {s}");
        src = s.source();
    }
}
```

Run against the `BadNumber` case above:

```text
error: field bytes is not a number
caused by: invalid digit found in string
```

That output is useful because each line says something the other does not. The rule: `Display` says what this layer knows and does not repeat what the source will say, since the caller printing the chain prints both. Break it on purpose and the evidence shows up immediately. Here `BadNumber`'s `Display` includes the source's own text instead of just naming the field:

```rust
use std::fmt;

#[derive(Debug)]
struct BadNumber(std::num::ParseIntError);

impl fmt::Display for BadNumber {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "field bytes is not a number: {}", self.0)
    }
}
```

```text
error: field bytes is not a number: invalid digit found in string
caused by: invalid digit found in string
```

"invalid digit found in string" now appears twice, once because this layer quoted it and once because `report` walked to the source and printed it again. The fix is not to stop wrapping the source; it is to let `Display` say only what this layer adds, and trust the chain-walking to print the rest.

### What each field is for

Every field on a variant should be there because a caller needs it to act, not because it was sitting in scope when you wrote the constructor. A `&'static str` naming which field failed, a `String` holding the offending text, and the inner error as `source` are all fine, each answering a question a caller was shown to have. Usually not fine: the whole input line, convenient but almost always already held by whoever called the parser. The shape leaving a caller with the least is a message string as the only payload:

```rust
use std::fmt;

#[derive(Debug)]
struct FetchError(String);

impl fmt::Display for FetchError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl std::error::Error for FetchError {}
```

```text
failed: timed out while fetching example.com
```

A caller holding this `FetchError` has exactly one thing: `to_string()`. Acting differently on a timeout than a lookup failure means searching that sentence for a substring you hope the author never rewords.

### A struct with a kind, and `#[non_exhaustive]`

An enum is right when a caller matches on the variant itself. `io::Error` picks a different shape: a struct holding an enum `kind` plus whatever context it needs, fields private, `kind()` the only way in. That shape is right when every failure carries roughly the same context and you want to add a field without touching a caller's match. The two shapes fail differently when they grow. Add a field to an enum variant's named fields and a caller who destructured it exhaustively breaks:

```rust
enum FetchError {
    Timeout { host: String, after_ms: u64, retries: u32 },
    NotFound { host: String },
}

fn handle(e: &FetchError) {
    match e {
        FetchError::Timeout { host, after_ms } => println!("{host} timed out after {after_ms}ms"),
        FetchError::NotFound { host } => println!("{host} not found"),
    }
}
```

```text
error[E0027]: pattern does not mention field `retries`
 --> src/main.rs:8:9
  |
8 |         FetchError::Timeout { host, after_ms } => println!("{host} timed out after {after_ms}ms"),
  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ missing field `retries`
```

Add a private field to a struct-with-a-kind instead, and a caller who only matched on `kind()` never sees it: `match e.kind() { FetchErrorKind::Timeout => ..., FetchErrorKind::NotFound => ... }` compiles unchanged before and after the struct gains a new `attempt: u32` field.

Adding a whole new variant is a different problem, and `#[non_exhaustive]` targets that one. Placed on an enum it has no effect inside the defining crate, confirmed by the Rust Reference: a `match` there may still list every variant with no catch-all. Used from another crate, the same `match` needs one:

```rust
#[non_exhaustive]
#[derive(Debug)]
pub enum FetchError {
    Timeout,
    NotFound,
}
```

```rust
match e {
    FetchError::Timeout => println!("retry"),
    FetchError::NotFound => println!("give up"),
}
```

```text
error[E0004]: non-exhaustive patterns: `&_` not covered
 --> src/main.rs:4:11
  |
4 |     match e {
  |           ^ pattern `&_` not covered
  |
  = note: `FetchError` is marked as non-exhaustive, so a wildcard `_` is necessary to match exhaustively
```

Adding `_ => println!("unknown failure"),` compiles and runs, printing `retry` for `Timeout` exactly as before. What `#[non_exhaustive]` buys is freedom: a variant can be added later without breaking every downstream `match`, and without that counting as the breaking change that forces a major version. Whether that trade is worth making is a question stage 8's eighth lesson answers, not this one.

### What not to do

A single `Error(String)` variant is the fields section's shape again: nothing to match on but the text. An error type per function looks disciplined but is not, since it multiplies types without giving a caller a new distinction: calling two of your functions now means writing two unrelated `match` expressions for what is often the same short list of failures. `Box<dyn Error>` in a public signature compiles and prints fine with `{}`, but stops the signature naming what can go wrong; a caller who wants to branch has to guess a concrete type and call `downcast_ref`, asking rather than being told. Lesson 16 brings `Box<dyn Error>` back as a conversion target, a different use from putting it in your own signature.

## Practice

1. ▢ `parse("")` is called on the line parser from this lesson. Predict its `Display` and its `source`, then run it.

<details markdown="1"><summary>Check</summary>

`Display` gives `missing field path`, since an empty line has no first token, and `source` is `None`, because `MissingField` never wraps another error. The variant and its field say exactly what went wrong without a nested error to consult.

</details>

2. ▢ Predict what `report` prints for the doubled-message `BadNumber` from this lesson, then say in one sentence what is wrong with rewriting `Display` to include the source's text.

<details markdown="1"><summary>Hint</summary>

`report` prints this layer's `Display` first, then walks `source()` and prints whatever it finds there too, regardless of what the first line already said.

</details>

<details markdown="1"><summary>Check</summary>

It prints `error: field bytes is not a number: invalid digit found in string` then `caused by: invalid digit found in string`, so the same sentence appears twice. `Display` duplicated work `source` was always going to do.

</details>

3. ▢ From your own crate, match a dependency's `#[non_exhaustive]` enum with one arm per current variant and no catch-all. Predict the error code before compiling.

<details markdown="1"><summary>Check</summary>

The error is `E0004`, non-exhaustive patterns: the attribute has no effect only inside its defining crate, so from any other crate a wildcard arm is required regardless of how many variants currently exist.

</details>

4. ▢ Two libraries model the same failure, one as an enum with a `Timeout { host, after_ms }` variant and one as a struct with a `kind()` accessor and private fields. Both need to record a retry count. Predict which one's callers keep compiling, and which error code the other's callers hit.

<details markdown="1"><summary>Hint</summary>

The question is whether the retry count becomes part of what a caller's `match` has to mention, or stays behind an accessor no `match` touches.

</details>

<details markdown="1"><summary>Check</summary>

The struct-with-a-kind's callers keep compiling, since the new field is private and never appeared in a `match`; the enum's callers who destructured `Timeout`'s fields hit `E0027`, missing field, since the pattern no longer accounts for every field.

</details>

5. ▢ A colleague's crate exposes `struct FetchError(String)` as its only error type. Given this lesson's three callers, adapted to a fetch instead of a parse, name one this shape cannot serve, and sketch the enum that would.

<details markdown="1"><summary>Check</summary>

A caller retrying a timeout but giving up on a not-found cannot be served, since both arrive as the same `String`. An enum with `Timeout` and `NotFound` variants gives that caller the distinction `FetchError(String)` withheld.

</details>

## Real-world reps

- [ ] In your `logsum` project, replace the hand-rolled error enum from lesson 10's rep with one designed from actual callers, such as the counting loop and a reporting mode that buckets rejections by reason, and hand-write `Display` and `std::error::Error` for it as in this lesson, with no derive yet.
- [ ] Add a `report` function using the `while let Some(s) = src` loop, call it wherever a rejected line's reason is printed, and check that no layer's `Display` repeats text the next layer down will already print.
- [ ] Tomorrow: pick one variant of your error type and ask what a caller could do differently because of it; if you cannot name anything, fold it into a neighbour.

## Going further

- [The non_exhaustive attribute](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute): what changes inside the defining crate against outside it
- [E0004](https://doc.rust-lang.org/error_codes/E0004.html): the non-exhaustive-match code, here from the attribute rather than a missing variant
- [E0027](https://doc.rust-lang.org/error_codes/E0027.html): the missing-field code behind a variant gaining a field a pattern did not expect
- [Error in std::io](https://doc.rust-lang.org/std/io/struct.Error.html): the standard library's own struct-with-a-kind error type
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
