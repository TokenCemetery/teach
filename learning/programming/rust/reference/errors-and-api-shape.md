---
title: Errors and API shape
description: The error-type decisions, the conversion rules, the visibility levels, and what a public API commits to
type: reference
---

# Errors and API shape

Lookup sheet for stage 3. The question it exists to answer: **what does this error type let a caller do, and what have I promised by making it public?**

## `?`

| On | Does | Requires | Cannot go in | Fix |
|---|---|---|---|---|
| `Ok(v)` | Unwraps to `v`, execution continues | Nothing | A closure passed to `map` returning a plain `i32` rather than `Result`/`Option` | Make the closure return `Result`/`Option` and collect the chain, `.map(\|s\| s.parse::<i32>().map(\|n\| n * 2))` |
| `Err(e)` | Returns early as `Err(From::from(e))` | The function's error type implements `From<E>` for the error's type, or one of `map_err`, a `From` impl, or `Box<dyn Error>` is used first | A function returning `()`, including a `#[test]` with no return type | Give the function `-> Result<(), Box<dyn std::error::Error>>` and end with `Ok(())` |
| `Some(v)` | Unwraps to `v`, no conversion | The function returns `Option` | `Option`'s `?` inside a function returning `Result` | `.ok_or(e)?` or `.ok_or_else(\|\| e)?`, converting first |

Without a matching `From`, the diagnostic is `E0277`, "`?` couldn't convert the error", naming the missing `From<SourceError>` implementation directly.

## Choosing the error shape

| Shape | A caller can | Costs |
|---|---|---|
| Enum, one variant per failure | `match` on the variant itself | Adding a named field to a variant breaks a caller who destructured it exhaustively, `E0027` |
| Struct with a `kind()` enum plus private fields | `match` on `kind()`, same as above | Adding a private field never breaks a caller; only a new `kind` variant does |
| `Box<dyn Error>` | Print with `{}`, nothing else without guessing | The signature stops naming what can go wrong; branching needs `downcast_ref` and a guessed concrete type, `None` for a wrong guess is indistinguishable from `None` for absence |

`#[non_exhaustive]` on an enum has no effect inside its own defining crate, where a `match` may still list every variant with no catch-all; from any other crate the same `match` needs a wildcard arm or fails `E0004`. It buys room to add a variant later without that counting as a breaking change, at the cost of every external caller needing a catch-all up front.

## The two implementations an error type needs

| Implementation | Holds | Rule |
|---|---|---|
| `Display` | One `match` arm per variant, in words, naming what this layer knows | Must not repeat what the wrapped error's own `Display` will say when a caller walks the chain |
| `std::error::Error::source` | `Some(&wrapped)` for a variant carrying a foreign error, `None` otherwise | The only method worth overriding; the default already returns `None` |

Breaking the rule is visible immediately: a `BadNumber` whose `Display` reads `"field bytes is not a number: {source}"` and a `report` function that also walks `source()` together print `invalid digit found in string` twice, once from each layer. The fix is to let `Display` say only what this layer adds and trust the walk to print the rest.

## Convert against wrap

| Choice | Keeps | A caller can still |
|---|---|---|
| Wrap (`source` returns `Some(&foreign)`) | The original value | Match on it, downcast it, walk to it through the chain |
| Convert (`From` formats a message and discards the value) | Only the formatted text | Read the message; nothing to downcast, `source()` returns `None` |

Both compile and report the same fact through `Display`; the difference shows only in what `source()` can still return. Wrap when a caller or a log needs the specific cause to match or count by kind; convert when the cause is an implementation detail that must not become part of the public type. Whichever type gets wrapped becomes visible in the public error the moment it is wrapped: a caller who finds `std::num::ParseIntError` inside can now depend on that exact type never changing. A `From` implementation on a public error type is not a private convenience; once it exists, the type it accepts is part of that error's API.

`From` can only be implemented where the source or target type is defined in the implementing crate (`E0117` otherwise, the orphan rule), which bites even inside one workspace: an error type living in a library crate cannot gain a `From` written from a thin binary crate that depends on it, since the binary owns neither type. The workaround inside this stage is a local wrapper type in the crate that needs the conversion.

## What `thiserror` and `anyhow` each replace

| Crate | Replaces | Stays hand-written |
|---|---|---|
| `thiserror` | `Display` (one `#[error("...")]` per variant), `Error::source` (`#[source]` on a field), and `From` for a wrapping variant with no other fields (`#[from]`) | The enum's variants and fields themselves |
| `anyhow` | `Box<dyn Error>` at a binary's edge, plus a hand-formatted `.map_err` string bolted on for context at every call site | Nothing; it is an opaque error type end to end |

The rule: a library returns a typed error a caller can match on, so `thiserror` belongs there; a binary can afford an opaque one, since nothing above `main` branches on it, only a human reading standard error, so `anyhow` belongs there and not in a library's public signature. `#[from]` only generates a conversion when the variant's other fields, besides the source and an optional backtrace, are empty; a variant that also carries a `field` name is refused with a compile error naming that requirement. On crates.io, read at the time of writing rather than as a stable figure: `thiserror` 2.0.20 has about 343 million recent downloads and 1.4 billion all time; `anyhow` 1.0.104 about 203 million recent and 922 million all time. Evidence a reader will meet both shapes often, not an endorsement of either.

## The visibility levels

| Level | Answers | From outside |
|---|---|---|
| Private (default) | Is there any reason for this to exist outside the module that wrote it? | `E0603` |
| `pub(super)` | Can the parent, and anything it can already reach, use this? | `E0603` from a sibling or anywhere further than the parent |
| `pub(crate)` | Can any module in this crate reach it, while a dependant crate cannot? | `E0603` from a dependant crate |
| `pub` | Can anything reach this, even a different crate? | Reachable |

Every one of these diagnoses `E0603` when it fails: to the compiler, private-by-default and a narrower visibility that does not reach the caller are the same fact. `use` never grants access; it only shortens a path already reachable, so `use`-ing a private item fails with the identical `E0603` a bare call would.

A struct's visibility and its fields' visibility are separate decisions: a `pub` struct with a private field blocks the struct literal from outside (`E0451`), which is the mechanism behind the constructor pattern, `pub fn new(...) -> Self`, that lets a type enforce an invariant no caller can bypass by naming every field. `pub use` re-exports an item at a shorter path than where it lives, so a library can hide its internal layout while keeping a caller's path stable; the old long path then fails with `E0603` once the module it passed through loses its own `pub`.

A `pub fn` returning a private type compiles with a warning, `private_interfaces`, on by default, rather than a hard error: `type 'X' is more private than the item`, noting the function is reachable at a wider visibility than the type it returns. This replaced a hard error, `private_in_public`, as of Rust 1.74.0. A caller outside the defining module who tries to call such a function anyway still fails, with `type 'X' is private` and no code.

## What the public API is

A caller can reach:
- Every `pub` item reachable from the crate root, directly or through a `pub use` re-export.
- Every field of every `pub` struct that is itself marked `pub`.
- Every variant of a `pub` enum, and every named field on a variant that lacks `#[non_exhaustive]`.
- Every trait implementation on a public type.
- The error type named in every public signature, including its own public surface by the same rules.

Anything without a visibility keyword, or narrower than `pub`, is not part of it, however far it is called from inside the crate.

## The documentation conventions

| Heading | Says |
|---|---|
| `# Examples` | A runnable demonstration; the only section `cargo test` executes |
| `# Errors` | Which `Err` variant shows up under which condition, named rather than left as "this can fail" |
| `# Panics` | Every way the function can panic, plainly enough that a caller can decide whether to call it |
| `# Safety` | The invariants a caller must uphold for an `unsafe fn` call to be sound |

None of the four is compiler-enforced the way a missing `match` arm is; `#![warn(missing_docs)]` only checks that a doc comment exists, not that it says anything, so a one-word comment satisfies it as fully as a complete write-up. What makes an example a test: a fenced ` ```rust ` block inside a `///` comment, compiled and run by `cargo test` under a `running 1 test` heading separate from the crate's unit tests, and failing the build the same way a wrong assertion anywhere else would. A line starting with `#` inside the block compiles but never renders; ending an example that uses `?` with `# Ok::<(), YourErrorType>(())` gives the hidden `fn main` rustdoc generates the return type `?` needs, since without it the example fails `E0277` for the same reason any plain function using `?` with no compatible return type would.

## Panic or error

Four questions, in order:

1. Did the failing value come from outside this function, or is it a state this code already ruled out itself? Outside, continue; already ruled out, skip to 4.
2. Is there a plausible way forward other than stopping, a fallback, a retry, rejecting one input and continuing? Yes, `Result`; genuinely not, continue.
3. Can the caller see inside this function, or are you both its author and only caller? A caller who cannot see inside gets `Result`; your own top-level code with no other caller, continue.
4. Can you write, in one sentence, the invariant of your own code that broke? Yes, panic. If the sentence really describes input that merely surprised you, return `Result` instead.

Four ways a library panics without a `panic!` in sight: indexing a slice past its length, `unwrap` on `None`, integer division by zero, and arithmetic overflow, the last of which panics in a normal build but silently wraps in `--release`, since `overflow-checks` defaults to `true` for `dev` and `false` for `release`. A constant expression such as `250_u8 + 10_u8` is caught at compile time instead, `#[deny(arithmetic_overflow)]`, since the compiler evaluates it itself.

## Diagnostics of the stage

| Code / message | Cause | Honest fix |
|---|---|---|
| `E0277`, `?` couldn't convert the error | The function's error type has no `From` for the expression's error type | Write the `From` impl, `map_err` at the call site, or widen the signature to `Box<dyn Error>` |
| `E0277`, the `?` operator can only be used on `Result`s, not `Option`s | `?` on an `Option` inside a function returning `Result` | `.ok_or(e)?` or `.ok_or_else(\|\| e)?` first |
| `E0277`, `?` used in a function returning `()` or with no return type | A plain function, or a `#[test]`, with no `Result`/`Option` return type | Give it `-> Result<(), Box<dyn std::error::Error>>` and end with `Ok(())` |
| `E0277`, same, inside a doctest | A `# Examples` block calls `?` with no hidden line giving the generated `fn main` a compatible return type | Add `# Ok::<(), YourErrorType>(())` as the block's last line |
| `E0117`, only traits defined in the current crate can be implemented for types defined outside of it | A `From` (or any trait) between two foreign types, including a library type and a dependent binary's local type | A local wrapper type owned by the crate that needs the conversion |
| `E0027`, pattern does not mention field | An enum variant gained a named field a caller's exhaustive destructuring did not expect | Add the field to the pattern, or move to a struct-with-a-kind shape if callers should not need to |
| `E0004`, non-exhaustive patterns | A `match` on a `#[non_exhaustive]` enum, from outside its defining crate, with no wildcard arm | Add `_ => ...` |
| `E0603`, item is private | Any of the four visibility levels not reaching the caller | Widen the visibility, or reach it through a `pub` constructor or re-export instead |
| `E0451`, field of struct is private | A struct literal outside the defining module names a private field | Use the type's constructor instead of a literal |
| `warning: private_interfaces`, type is more private than the item | A `pub fn` returns a type that is not itself `pub` | Make the type `pub`, since a caller cannot hold a value of a type they cannot name; this replaced a hard error, `private_in_public`, before Rust 1.74.0 |
| `warning: missing documentation`, from `#![warn(missing_docs)]` | A `pub` item with no `///` comment at all | Add one; the lint checks presence, not usefulness |
| `warning: unresolved link`, from `broken_intra_doc_links` | An intra-doc link, `` [`Name`] ``, to an item that does not exist | Fix the name; the build still finishes, since this warns rather than fails |
| Doctest `FAILED`, wrong `left`/`right` | An assertion inside a `# Examples` block no longer holds | Fix the example or the code; the failure names the exact line in the doc comment |
| Panic, `index out of bounds` | Indexing a slice or `Vec` past its length | `.get(i)` and handle `None`, or prove the index in range first |
| Panic, `called Option::unwrap() on a None value` | `unwrap`/`expect` on an absent value that was not already proven present | Propagate with `?` after `ok_or`, or prove presence first |
| Panic, `attempt to divide by zero` / `attempt to add with overflow` | Division or arithmetic on a runtime value with no check | `checked_div`, `checked_add`, and convert `None` to an error |
| Panic, `internal error: entered unreachable code` | `unreachable!()` reached, meaning the code's own reasoning about possible branches was wrong | Add the missing match arm; never reach for `unreachable!()` on an enum you do not own |

## Where the project should be

The stage 3 slice of the arc's rep project, `logsum`, splits into a library plus a thin binary, with an error type a caller can match on, `?` propagation throughout, module boundaries chosen deliberately, and documentation examples that compile. See [the project](the-project.md) for the full brief and the state expected at the end of every stage.
