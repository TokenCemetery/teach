---
title: 16. Conversions and Boundaries
description: A From implementation is where one layer's failure becomes another's, and a derive writes the ones you already understand
type: lesson
---

# Lesson 16. Conversions and Boundaries

**Mission link:** A library that exposes a dependency's exact error type has promised never to change that dependency without breaking callers, and a `From` implementation is the one line that decides whether a foreign failure crosses the boundary on purpose or by accident.
**Primary source:** [std::convert::From](https://doc.rust-lang.org/std/convert/trait.From.html)
**Prerequisites:** [Lesson 14](0014-propagating-errors.md), [Lesson 15](0015-designing-an-error-type.md)

## Warm-up

1. ▢ Lesson 14 established that `expr?`, inside a function returning `Result<T, E>`, converts the expression's error into `E` before returning it. Which trait performs that conversion, and what happens when `E` has no implementation of it for that error?

<details markdown="1"><summary>Check</summary>

`From` performs it: `?` calls the target type's `from` on the `Err` value. Without a matching implementation the code does not compile, and the diagnostic names the missing conversion directly, the same failure lesson 10 first showed.

</details>

2. ▢ Lesson 15's hand-written `Display` for the project's error type gives two messages, one for a missing field and one for a field that will not parse as a number, and neither repeats what the failed parse itself would say. What is left out, and where does it go instead?

<details markdown="1"><summary>Check</summary>

The message names what is wrong with the input and leaves out the underlying parse failure's own text entirely. That text is not lost: it is reachable through `source`, a separate method for a separate question, and a caller who wants both calls both.

</details>

## Know this

### `From` is what makes `?` work across a boundary

Converting a foreign error by hand at every call site works, but it means writing the same `map_err` wherever that error can occur:

```rust
fn bytes(s: &str) -> Result<u64, ParseError> {
    s.parse().map_err(|source| ParseError { field: "bytes", source })
}
```

Implement `From` for the target error type once, and every `?` on that source error type finds it without being told:

```rust
impl From<std::num::ParseIntError> for ParseError {
    fn from(source: std::num::ParseIntError) -> Self {
        ParseError { field: "bytes", source }
    }
}

fn bytes(s: &str) -> Result<u64, ParseError> {
    Ok(s.parse()?)
}
```

Both versions give the identical value for the same input. The second has lost its `map_err` entirely and kept only the `?`: the conversion moved out of every call site and into one place, the trade lesson 14 made available and lesson 15's error type is built to receive. A `From` implementation is the boundary between "the caller converts" and "the caller just asks," and the rest of this lesson is about what that boundary should and should not do.

### Converting against wrapping

There are two honest ways to bring a foreign error across that boundary, and they keep different amounts of the original. Wrapping stores it and lets a caller reach it through `source`:

```rust
struct WrapError(std::num::ParseIntError);

impl std::error::Error for WrapError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        Some(&self.0)
    }
}
```

Walking the chain with the same loop lesson 15 used prints both layers:

```text
error: bytes is not a number
caused by: invalid digit found in string
```

Converting keeps only what it needs, usually a formatted message, and throws the original value away:

```rust
struct ConvertError(String);

impl From<std::num::ParseIntError> for ConvertError {
    fn from(e: std::num::ParseIntError) -> Self {
        ConvertError(format!("bytes is not a number: {e}"))
    }
}
```

`ConvertError`'s `Error` implementation takes the default `source`, which returns `None`, so walking its chain stops after one line:

```text
error: bytes is not a number: invalid digit found in string
```

Both compile and report the same fact; the difference is what a caller or a log can still ask for afterwards. Wrap when a caller or a log will want the specific cause, to match on or count by kind; convert when the cause is an implementation detail the caller must not depend on. That second case matters because whichever type you wrap becomes visible in your public error the moment you wrap it: a caller who finds `std::num::ParseIntError` inside can now depend on you always parsing with that exact type, pinning a choice you may want to change later. A `From` implementation is not a private convenience; once it is in your public error, it is part of your API.

### The blanket rule that bites

`From` can only be implemented where at least one of the source or target types is defined in the implementing crate. A conversion between two types neither of which you own does not compile:

```text
error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
 --> src/main.rs:1:1
  |
1 | impl From<std::num::ParseIntError> for std::fmt::Error {
  | ^^^^^-----------------------------^^^^^---------------
  |      |                                 |
  |      |                                 `std::fmt::Error` is not defined in the current crate
  |      `ParseIntError` is not defined in the current crate
```

This is the orphan rule, and it applies inside your own project too: once an error type lives in a library crate and you write code in a thin binary crate that only depends on it, the binary owns neither type, so it cannot add a `From` between them either. Stage 4 owns this rule properly; for now the workaround is a wrapper type of your own, local to the crate that needs the conversion:

```rust
struct BinError(ParseError);

impl From<ParseError> for BinError {
    fn from(e: ParseError) -> Self {
        BinError(e)
    }
}
```

`?` finds this `From` exactly as it finds any other.

### `Box<dyn Error>` as a conversion target

The standard library ships one `From` that takes any error: anything implementing `std::error::Error` converts into `Box<dyn std::error::Error>`. A function can use `?` on two unrelated concrete error types through the same signature:

```rust
fn run(which: &str) -> Result<(), Box<dyn std::error::Error>> {
    if which == "parse" {
        errprobe::parse("/index x")?;
    } else {
        "x".parse::<i32>()?;
    }
    Ok(())
}
```

Both branches compile and print through `{}` the same way a concrete error would. What is gone is the type: a caller cannot match on which failure happened without guessing, using `downcast_ref` with a type named explicitly:

```rust
let boxed = run("parse").unwrap_err();
boxed.downcast_ref::<errprobe::ParseError>(); // Some(..)
boxed.downcast_ref::<std::num::ParseIntError>(); // None, wrong guess
```

A wrong guess is not an error, it is `None`, indistinguishable from a value that was simply absent. That is the trade: `Box<dyn std::error::Error>` is fine at the top of an application, where the last thing done with an error is printing it. It is wrong in a library's public signature, because it throws away the one thing lesson 15's design bought, a caller who can match on what went wrong. An application binary that just wants to report a failure and stop reaches for `anyhow` instead; that tool, and the library-versus-application split behind it, is lesson 20's.

### Then the derive

Every piece written by hand above, `Display`, `source`, `From`, is mechanical enough that `thiserror` writes it from attributes on the same enum:

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum ParseError {
    #[error("missing field {field}")]
    MissingField { field: &'static str },
    #[error("field {field} is not a number")]
    BadNumber {
        field: &'static str,
        #[source]
        source: std::num::ParseIntError,
    },
}
```

`#[error("...")]` per variant replaces the whole `match` inside `Display::fmt`, with the same field interpolation `write!` used by hand. `#[source]` on a field replaces the `source` method's `match`, telling the derive which field a variant's `source` should return. Where a field exists only to feed a conversion, `#[from]` also generates the `impl From` from the opening section:

```rust
#[derive(Debug, Error)]
enum BytesError {
    #[error("bytes is not a number")]
    Bytes(#[from] std::num::ParseIntError),
}
```

That `From<std::num::ParseIntError> for BytesError` is real: `?` finds it with no hand-written impl anywhere in the file. `#[from]` cannot do this for `ParseError::BadNumber` above, because that variant carries a `field` the source value cannot supply; the derive only generates a conversion when the variant's other fields, besides the source and an optional backtrace, are empty, and asking it to try produces a compile error naming that requirement.

The derived `ParseError`, with no `Display` or `Error` written by hand, gives back the identical values: the same `to_string` text, and `source` returning the wrapped parse failure for one variant and `None` for the other. Three things follow. First, it replaces everything lessons 15 and 16 wrote by hand, not a simplified version of it. Second, it stays a library-side tool: the enum it produces is still a real type a caller can match on, unlike the boxed error above. Third, it is not a niche convenience: `thiserror` sits at about 343 million recent downloads and 1.4 billion all time on crates.io, read at the time of writing rather than as a stable figure, evidence that a reader will meet this shape of code often, not an endorsement of it.

### The boundary as an API decision

Every `From` implementation added to a public error type is a promise that the foreign error it accepts can now appear inside that type, visible to any caller who inspects it or walks its `source` chain. Adding one changes no function's name or argument, so it is easy to add without noticing it as a change, but it is one: a dependency you previously kept invisible is now something a caller could depend on you continuing to wrap. Wrapping and converting is this same decision seen from the other side: wrapping commits you to exposing the foreign type, converting is how you decline to.

## Practice

1. ▢ Predict whether this compiles, and if not, which trait the diagnostic says is missing. Then compile it.

   ```rust
   #[derive(Debug)]
   struct ConfigError(String);

   fn read_port(s: &str) -> Result<u32, ConfigError> {
       let port = s.parse::<u32>()?;
       Ok(port)
   }
   ```

<details markdown="1"><summary>Check</summary>

It fails with `E0277`: `?` cannot convert the error to `ConfigError` because `From<ParseIntError>` is not implemented for it, the same shape lesson 10 introduced.

</details>

2. ▢ Add a `Display`, an `Error` implementation and a `From<std::num::ParseIntError>` for `ConfigError` that keeps only a formatted message, discarding the parse error itself. Predict what `source` returns on the result, then compile and check.

<details markdown="1"><summary>Hint</summary>

Not overriding `source` in an `Error` implementation leaves the default, and the default returns nothing.

</details>

<details markdown="1"><summary>Check</summary>

`source` returns `None`. This is the converting choice: the message survives because `From` formats it in, but nothing is kept that a caller could downcast or match against, since the `ParseIntError` was never stored.

</details>

3. ▢ Predict what happens when you try this, where neither type is yours, and name the error code before compiling.

   ```rust
   impl From<std::num::ParseIntError> for std::fmt::Error {
       fn from(_e: std::num::ParseIntError) -> Self {
           std::fmt::Error
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

It is `E0117`, the orphan rule: both `ParseIntError` and `fmt::Error` are foreign to this crate, and owning neither is exactly what the rule blocks.

</details>

4. ▢ This boxes a `ParseIntError` behind `Box<dyn std::error::Error>` and then guesses twice. Predict each guess's result before running it.

   ```rust
   fn run() -> Result<(), Box<dyn std::error::Error>> {
       "x".parse::<i32>()?;
       Ok(())
   }

   fn main() {
       let boxed = run().unwrap_err();
       println!("{:?}", boxed.downcast_ref::<std::num::ParseIntError>());
   }
   ```

   Now change the type argument to a type that was never boxed here, and predict how the second run differs.

<details markdown="1"><summary>Check</summary>

The first guess is correct and prints `Some(ParseIntError { kind: InvalidDigit })`. Guessing a type that was never boxed gives `None`, with nothing to say the guess was wrong rather than the value merely absent, the cost of a signature that stopped naming its error type.

</details>

5. ▢ Predict whether `thiserror` accepts `#[from]` on this field, given that the variant also carries `field`, and what the message says if not.

   ```rust
   #[derive(Debug, Error)]
   enum BadDerive {
       #[error("field {field} is not a number")]
       Bytes {
           field: &'static str,
           #[from]
           source: std::num::ParseIntError,
       },
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what value the generated `From::from` would have to invent for `field`, given that it only ever receives a `ParseIntError`.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile: the derive reports that deriving `From` requires no fields other than the source and a backtrace, since it has nothing to put in `field` when the only argument to `from` is the `ParseIntError` itself.

</details>

## Real-world reps

- [ ] Add the `From` implementations your project's error type needs for every foreign error your parser converts by hand with `map_err`, then delete each `map_err` in favour of `?`.
- [ ] For each foreign error you now convert, decide whether it should wrap or convert, note that decision above the `From` implementation, and confirm a `source` walk agrees with it.
- [ ] Tomorrow: rewrite your project's error type with `thiserror`, keep the hand-written version alongside it, and assert both give the same `to_string` and `source` for every input your tests already cover.

## Going further

- [Boxing errors](https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/boxing_errors.html): converting any error into `Box<dyn Error>` so `?` works across unrelated error types
- [Error in std::error](https://doc.rust-lang.org/std/error/trait.Error.html): the `source` method and the `downcast_ref` that recovers a concrete type from a trait object
- [Orphan rules](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules): the coherence rule behind `E0117`, which stage 4 covers properly
- [E0117](https://doc.rust-lang.org/error_codes/E0117.html): the diagnostic for implementing a foreign trait for a foreign type
- [thiserror](https://docs.rs/thiserror/latest/thiserror/): the derive that generates `Display`, `Error::source` and `From` from attributes
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
