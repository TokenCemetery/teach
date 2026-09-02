---
title: 20. A Library a Caller Can Handle
description: Split the crate, name the failures, and decide what the binary does that the library must not
type: lesson
---

# Lesson 20. A Library a Caller Can Handle

**Mission link:** A caller who depends on your crate never sees the source, only the type you handed back, so the question this lesson closes is whether that type still lets them act, or whether your binary's own habits, printing, arguments, exit codes, leaked into it along the way.
**Primary source:** [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
**Prerequisites:** [Lesson 16](0016-conversions-and-boundaries.md), [Lesson 18](0018-modules-and-visibility.md)

## Warm-up

1. ▢ Lesson 16 closed by calling a `From` implementation on a public error type a promise rather than a private convenience. Once `YourError` is public, what does adding `impl From<SomeLibError> for YourError` commit you to?

<details markdown="1"><summary>Check</summary>

It commits you to `SomeLibError` now being reachable inside `YourError`, visible to any caller who inspects it or walks its `source` chain. Nothing about the function signature changed, but a dependency you previously kept invisible is now something a caller could depend on you continuing to wrap.

</details>

2. ▢ Lesson 18 gave a checklist for deciding what a crate's public API actually is: not everything you wrote, only what is `pub` and reachable from the crate root. Applied to a crate holding both a library and a binary, what does that checklist say the binary side contributes to the API a caller depends on?

<details markdown="1"><summary>Check</summary>

Nothing. A binary crate is compiled and run, never depended on by another crate, so nothing in `src/main.rs` is reachable from anywhere a caller could write a `use` statement. Only the library's `pub` items, reachable from its own crate root, count.

</details>

## Know this

### The split, performed rather than described

Cargo already expects this: a package with both `lib.rs` and `main.rs` in `src` builds a library and a binary of the same name, linked automatically. Split this way, a small parser's library top level is four items:

```rust
// src/lib.rs
pub struct Record { pub path: String, pub status: u16, pub bytes: u64 }

pub enum LineError {
    MissingField { field: &'static str },
    BadNumber { field: &'static str, source: std::num::ParseIntError },
}

fn split_fields(line: &str) -> Result<(&str, &str, &str), LineError> { /* ... */ }

pub fn parse_line(line: &str) -> Result<Record, LineError> { /* ... */ }
```

`Record` and `LineError` are lesson 15's design, `parse_line` does the parsing, and `split_fields` carries no visibility keyword, which already keeps it out of reach outside this crate. Nothing here reads an argument, opens a file, or calls `println!`; the binary is the part that does:

```rust
// src/main.rs
use std::env;
use std::fs;

use anyhow::{Context, Result};
use callers_can_handle::parse_line;

fn main() -> Result<()> {
    let path = env::args().nth(1).context("usage: reporter <path>")?;
    let text = fs::read_to_string(&path).with_context(|| format!("failed to read {path}"))?;

    let mut bytes_total: u64 = 0;
    for (i, line) in text.lines().enumerate() {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let record = parse_line(line)
            .with_context(|| format!("line {} is not a valid request", i + 1))?;
        bytes_total += record.bytes;
    }
    println!("total bytes: {bytes_total}");
    Ok(())
}
```

Running it against four good lines prints `total bytes: 2090` and exits `0`; with no argument it prints `Error: usage: reporter <path>` and exits `1`, a message rather than a panic. The rule the split enforces: the library must be usable by a caller who has no terminal at all, someone calling `parse_line` from inside a web server or a test, so anything that reads arguments, reads a stream, or prints belongs to the binary.

### `anyhow` on the binary side, and why not on the library side

`main` returns `anyhow::Result<()>`, an alias for `Result<(), anyhow::Error>`. `parse_line` returns `Result<Record, LineError>`, and `.with_context(...)?` compiles with no `From<LineError>` written anywhere, since `anyhow::Error` blanket-converts any `std::error::Error`, and `?` finds it like any other. `.context` and `.with_context` attach a message ahead of the error, the second computing it lazily so success never pays for building a `String` it will not use. Running the binary against an unparseable line shows what a caller sees:

```text
Error: line 2 is not a valid request

Caused by:
    0: field bytes is not a number
    1: invalid digit found in string
```

Three layers appear: the context `main` attached, `LineError`'s own `Display`, and the `ParseIntError` beneath it, walked automatically the way lesson 15's loop walked one by hand. A chain with only one layer beneath the context drops the numbering, printing a single unnumbered `Caused by:` line instead. The rule and its reason: a library returns a typed error since a caller may want to match on it; a binary can afford an opaque one, since nothing above `main` branches on it, only a human reading standard error. `anyhow` sits at about 203 million recent downloads and about 922 million all time on crates.io, read at the time of writing, evidence a reader will meet this shape of code, not an endorsement of it inside a library. It replaces what lesson 16 named: `Box<dyn std::error::Error>` at a binary's edge plus a hand-formatted `.map_err` string bolted on for context, since `.context` does that bolting-on once instead of at every call site.

### The stage's decisions, checked against the finished library

Four questions, each from an earlier lesson, run against the finished library. What can a caller distinguish: `LineError::MissingField` from `LineError::BadNumber`, exactly the two failures lesson 15 argued this parser's real callers need told apart, no more. What `From` implementations has the type committed to: none; a `From<std::num::ParseIntError>` was available and deliberately left unwritten, since it could not say which field failed, the context loss lesson 15 warned a generic conversion causes, so `map_err` keeps the field name instead. What is `pub` and what is not: `Record`'s fields and `LineError`'s variants are public because the types are, `parse_line` is the one function a caller calls, and `split_fields` carries no visibility keyword, reachable only inside this crate as lesson 18's checklist asks a helper to be. Whether every public item has a documented example: `parse_line` uses `?` rather than `.unwrap()`, matching C-QUESTION-MARK, with an `# Errors` section matching C-FAILURE; `LineError` has its own example; `Record` needs none, since C-EXAMPLE allows one item's example to stand in for a type that only ever appears through it, which `Record` does. Nothing carries a `# Panics` section, because nothing panics: every value that could be missing or malformed came from outside, lesson 17's first question, and got a `Result` instead.

### What a caller can do now that they could not before

A second, smaller consumer of the same library shows what the split bought, matching on the two variants and doing something different for each rather than treating both as one opaque failure:

```rust
// src/bin/triage.rs
use callers_can_handle::{parse_line, LineError};

fn main() {
    let lines = ["/index 200 1200", "/login 200", "/login 200 not-a-number"];
    let mut missing = 0;
    let mut bad_number = 0;

    for line in lines {
        match parse_line(line) {
            Ok(record) => println!("kept {} bytes for {}", record.bytes, record.path),
            Err(LineError::MissingField { field }) => {
                missing += 1;
                println!("skipping, {field} was never supplied");
            }
            Err(LineError::BadNumber { field, source }) => {
                bad_number += 1;
                println!("skipping, {field} could not be parsed: {source}");
            }
        }
    }

    println!("missing: {missing}, unparseable: {bad_number}");
}
```

Running it prints `kept 1200 bytes for /index`, then two different skip messages, then `missing: 1, unparseable: 1`. No wildcard arm is needed to match `LineError` exhaustively, here or from any dependent crate, since nothing marked it `#[non_exhaustive]`; `Box<dyn std::error::Error>` in `parse_line`'s place would have made this `match` impossible without a guess and a `downcast_ref`. A caller who wants to count rejections by reason, retry one kind and give up on another, or report each differently now can, which is the stage's promise made concrete rather than stated.

### What stage 3 bought

Lesson 14 gave `?` the job of converting an error through `From` on its way out of a function, not merely unwrapping it. Lesson 15 gave an error type's shape the job of deciding what a caller can tell apart, no more than a real caller needs. Lesson 16 gave a `From` implementation the weight of a promise: once it is on a public type, the error it accepts is part of that type's API. Lesson 17 gave a panic exactly one honest occasion, an invariant of your own code that broke, never a value a caller supplied. Lesson 18 gave the module tree the job of deciding what a crate's public API is, everything else staying out of reach by default. Lesson 19 gave an example the weight of a test, since `cargo test` runs it and a rotten example fails the build rather than quietly misleading the next reader. The stage's promise, from this arc's own table, was that you would write a library whose failures a caller can actually handle; the six lessons before this one are what met it, and this one only assembled them into a crate a caller could actually depend on. Stage 4, Traits, generics and lifetimes, is next.

## Practice

1. ▢ Predict whether this compiles, given that `LineError` implements `std::error::Error` and no `From<LineError>` is written anywhere. Then compile it.

   ```rust
   fn run(line: &str) -> anyhow::Result<()> {
       let record = callers_can_handle::parse_line(line)?;
       println!("{record:?}");
       Ok(())
   }
   ```

<details markdown="1"><summary>Check</summary>

It compiles. `anyhow::Error` implements a blanket `From<E>` for any `E: std::error::Error + Send + Sync + 'static`, so `?` finds a conversion with none written for `LineError` specifically, unlike a plain `Result<(), LineError>` return type.

</details>

2. ▢ Two runs of the same reporting binary hit different depths of failure: one line fails to parse with no further cause, one line's context wraps a `LineError` that itself wraps a `ParseIntError`. Predict whether both print `Caused by:` the same way, then run both.

<details markdown="1"><summary>Hint</summary>

Count how many lines would appear underneath `Caused by:` in each case, and ask whether a list of one item needs the same numbering a list of two does.

</details>

<details markdown="1"><summary>Check</summary>

They differ. One layer beneath the top message prints a single unnumbered `Caused by:` line; two or more print them numbered from `0`, one per line. The walk is identical either way; only the rendering changes with the count.

</details>

3. ▢ A second crate depends on this library and calls `callers_can_handle::split_fields("x")` directly. Predict whether it compiles, then compile it.

<details markdown="1"><summary>Check</summary>

It fails with `E0603`, naming `split_fields` a private function, trimmed here of a note pointing at the dependency's own source line. Carrying no visibility keyword already keeps a function out of another crate's reach, the same restriction `pub(crate)` would give it here, since this library has only one module.

</details>

4. ▢ `LineError` carries no `#[non_exhaustive]`. Predict whether a `match` on it, written in a different crate that depends on this one, needs a wildcard arm to cover both variants. Then write that `match` in a fresh crate and compile it.

<details markdown="1"><summary>Hint</summary>

Lesson 15's `FetchError` only needed a wildcard from outside its crate once the attribute was added. Is it added here?

</details>

<details markdown="1"><summary>Check</summary>

No wildcard is needed. `#[non_exhaustive]` is what forces one from outside a defining crate, and this enum does not carry it, so an external `match` naming both `MissingField` and `BadNumber` compiles exactly as it would from inside.

</details>

5. ▢ A caller, instead of relying on `?`'s automatic conversion, tries to write `impl From<LineError> for anyhow::Error` by hand in their own crate. Predict the diagnostic's code, then compile it.

<details markdown="1"><summary>Check</summary>

It fails with `E0117`, the orphan rule from lesson 16: neither `LineError` nor `anyhow::Error` is defined in the caller's crate, so a foreign trait between two foreign types is refused regardless of intent, and it was never needed anyway, since `anyhow`'s own blanket implementation already gives `?` the conversion.

</details>

## Real-world reps

- [ ] Split your `logsum` project into a library holding `Record`, your error type and every parsing function, and a thin binary holding argument handling, input and reporting, with `main` returning `anyhow::Result<()>` and `.context` at each fallible call.
- [ ] Write a second, smaller consumer of that library, either a test or a second binary, that matches on your error type and does something different for at least two variants, such as counting rejections by reason instead of as one total.
- [ ] Tomorrow: run this lesson's four questions against your own library: what your error type lets a caller distinguish, which foreign errors it wraps or converts and why, what is `pub` against what is left without a visibility keyword, and whether every public item carries a rustdoc example.

## Going further

- [Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html): the full checklist this lesson only samples
- [Package Layout](https://doc.rust-lang.org/cargo/guide/project-layout.html): the convention behind one crate holding both `src/lib.rs` and `src/main.rs`
- [anyhow](https://docs.rs/anyhow/latest/anyhow/): the crate's own documentation, including `Context` and what a failing `main` prints
- [How to write documentation](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html): the rustdoc book's chapter behind `# Examples`, `# Errors` and `# Panics`
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
