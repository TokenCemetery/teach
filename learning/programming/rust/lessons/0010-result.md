---
title: 10. Result, and Failure as a Value
description: A failure is a return value rather than an event, so the signature says what can go wrong before you read the body
type: lesson
---

# Lesson 10. Result, and Failure as a Value

**Mission link:** A fallible function that returns `Result` cannot fail silently: the compiler makes you look at the `Err` case before the code compiles cleanly, which is the difference between a bug a reviewer catches and one a customer reports.
**Primary source:** [std::result](https://doc.rust-lang.org/std/result/index.html)
**Prerequisites:** [Lesson 9](0009-option.md), [Lesson 8](0008-enums.md)

## Warm-up

1. ▢ `None.ok_or("nothing")` gives `Err("nothing")`. What does that tell you about how `ok_or` treats the two `Option` variants?

<details markdown="1"><summary>Check</summary>

`ok_or` turns `Some(x)` into `Ok(x)` and `None` into `Err(e)`, where `e` is whatever value you supply. It is the crossing point from an absence with no reason attached to a failure with one.

</details>

2. ▢ Lesson 8 established that an enum is data plus a tag, with no exceptions. `Result<T, E>` is such an enum. Name its two variants and what each one holds.

<details markdown="1"><summary>Check</summary>

`Ok(T)` holds the success value, `Err(E)` holds the failure value. Nothing else is special about `Result`; it is defined in the standard library the same way you would define it yourself.

</details>

## Know this

### `Result`, and the warning for ignoring one

`Result<T, E>` is `Ok(T)` or `Err(E)`, an ordinary two-variant enum whose second variant carries the reason for failure. Once a function's return type says `Result<i32, ParseIntError>`, the signature itself tells a caller that this can fail and what the failure looks like, before they read a line of the body. `Option` says "this might be absent"; `Result` says "this might be absent, and here is why."

The standard library will not let a caller quietly drop that value on the floor. `Result` carries the `#[must_use]` attribute, so ignoring one produces a warning:

```rust
fn parse_num(s: &str) -> Result<i32, std::num::ParseIntError> {
    s.parse()
}

fn main() {
    parse_num("abc");
    println!("done");
}
```

```text
warning: unused `Result` that must be used
 --> src/main.rs:6:5
  |
6 |     parse_num("abc");
  |     ^^^^^^^^^^^^^^^^
  |
  = note: this `Result` may be an `Err` variant, which should be handled
  = note: `#[warn(unused_must_use)]` (part of `#[warn(unused)]`) on by default
help: use `let _ = ...` to ignore the resulting value
```

This still compiles and still prints `done`, which is the trap: the program keeps running with a parse failure nobody looked at. A warning nobody reads is exactly how that bug ships.

### `?`, and the constraint it comes with

Writing out the failure path by hand with `match` works, but it is verbose enough that it discourages doing it consistently:

```rust
fn double_match(s: &str) -> Result<i32, std::num::ParseIntError> {
    let n = match s.parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(e),
    };
    Ok(n * 2)
}
```

The `?` operator is that same match, compressed to one character. In a function returning `Result`, `expr?` unwraps an `Ok` and returns early with the `Err` unchanged:

```rust
fn double_q(s: &str) -> Result<i32, std::num::ParseIntError> {
    let n = s.parse::<i32>()?;
    Ok(n * 2)
}
```

Both give `Ok(42)` for `"21"` and `Err(ParseIntError { kind: InvalidDigit })` for `"x"`; the second is one line shorter and the intent is easier to see, and that gap only widens as more fallible calls stack up. This is the reason `?` exists, and the reason `Result`-returning code reads as plainly as code that cannot fail.

`?` has one requirement worth hitting on purpose: the function's error type has to be reachable from the expression's error type through `From`. Without that conversion, this fails to compile:

```rust
#[derive(Debug)]
struct MyError(String);

fn parse_it(s: &str) -> Result<i32, MyError> {
    let n = s.parse::<i32>()?;
    Ok(n)
}
```

```text
error[E0277]: `?` couldn't convert the error to `MyError`
 --> src/main.rs:5:29
  |
4 | fn parse_it(s: &str) -> Result<i32, MyError> {
  |                         -------------------- expected `MyError` because of this
5 |     let n = s.parse::<i32>()?;
  |               --------------^ the trait `From<ParseIntError>` is not implemented for `MyError`
  |               |
  |               this can't be annotated with `?` because it has type `Result<_, ParseIntError>`
  |
note: `MyError` needs to implement `From<ParseIntError>`
```

This is the message to recognise: `?` did not fail because your logic is wrong, it failed because nobody told it how to turn a `ParseIntError` into a `MyError`. Writing that conversion properly, so every fallible call in a program can convert into one error type automatically, is stage 3's subject. For now, two stopgaps get you through this stage without it, and both are exactly that, stopgaps rather than answers: call `.map_err(|e| MyError(e.to_string()))` by hand at the call site, or use a single error type everywhere so there is nothing left to convert. The first does not scale past a couple of calls, and the second only postpones the design question stage 3 exists to answer.

### `?` in `main`

`main` is allowed to return `Result` too, and the type it returns has to implement `Termination`, which `Result<(), E>` does whenever `E` implements `Debug`:

```rust
fn main() -> Result<(), std::num::ParseIntError> {
    let n: i32 = "x".parse()?;
    println!("got {n}");
    Ok(())
}
```

Running it never reaches the `println!`. It prints `Error: ParseIntError { kind: InvalidDigit }` on standard error and the process exits with status 1. Nothing formats that line specially; it is the `Err` value's `Debug` output behind an `Error: ` prefix, which is worth knowing so you recognise it in a log rather than mistake it for a panic.

`?` also works, briefly, in a function returning `Option`: `s.chars().next()?` returns `None` early if the string is empty, and unwraps to the `char` otherwise. Same operator, same shape, no `Err` payload to carry.

### The combinators

Each of these answers one question about a `Result` you already have, without a `match`.

`map` asks: if this succeeded, what do I want instead of the raw value? `parse("3").map(|n| n * 10)` gives `Ok(30)`; on an `Err` it does nothing and passes it through.

`map_err` asks the same question about the failure side: `parse("x").map_err(|e| format!("bad number: {e}"))` gives `Err("bad number: invalid digit found in string")`.

`and_then` asks: given the success value, what is the next step, and can that step also fail? Chaining `parse("4").and_then(half)`, where `half` returns `Ok(n / 2)` for an even number and a genuine parse failure otherwise, gives `Ok(2)`; chaining `parse("3")` into the same function gives `Err(ParseIntError { kind: InvalidDigit })`, because three is odd.

`unwrap_or` and `unwrap_or_else` ask: if this failed, what default do I fall back to? `parse("x").unwrap_or(0)` gives `0`. `unwrap_or_else` takes a closure instead of a plain value, useful when computing the default costs something or needs the error: `parse("x").unwrap_or_else(|_| -1)` gives `-1`.

`ok` and `err` ask: can I have just the side I care about, as an `Option`? `parse("3").ok()` gives `Some(3)` and `parse("x").ok()` gives `None`; `parse("x").err()` gives `Some(ParseIntError { kind: InvalidDigit })` and `parse("3").err()` gives `None`. Either one discards the other side entirely, which is fine once you have decided you no longer need it.

`is_ok` asks the yes-or-no version without consuming anything: `parse("3").is_ok()` is `true`, `parse("x").is_ok()` is `false`.

### Panic against error, decided rather than assumed

A panic and an `Err` look nothing alike once you know what to look for. A plain `panic!("boom")` prints, roughly:

```text
thread 'main' (12345) panicked at src/main.rs:2:5:
boom
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

The number in parentheses is a thread identifier and is different on every run; the file, line and column and the message are what to read. Calling `.unwrap()` on an `Err` produces the same shape with a more specific message:

```text
thread 'main' (12345) panicked at src/main.rs:2:30:
called `Result::unwrap()` on an `Err` value: ParseIntError { kind: InvalidDigit }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

Both terminate the thread and exit with status 101; the difference is entirely in the second line, and `unwrap`'s complaint names the `Err` value's `Debug` form. Neither of these is what an `Err` on its own does: an unhandled `Err` sitting in a `Result` you have not called `unwrap` on does not print anything until something forces it to, which is the whole point of returning it rather than panicking.

The rule for choosing between them: a `Result` is for a failure the caller could reasonably plan for and recover from; a panic is for a broken invariant in your own code, one that should never happen if the program is correct. Reaching for `Result`: a file that might not exist, a network call that might time out, user input that might not parse. Reaching for `panic!` or `unwrap`: an index you have already bounds-checked, a config value your own constructor guarantees is present, a `.lock()` that can only fail if a previous thread already panicked while holding it. Designing an error type that a caller can actually match on, rather than a single opaque struct or a stopgap `String`, is stage 3's job, under "Errors and API shape".

### Collecting failures

Parsing many lines and stopping on the first bad one is usually what you want, and it comes for free: collecting an iterator of `Result<T, E>` into a `Result<Vec<T>, E>` stops at the first `Err` and discards nothing else you might need.

```rust
let ok: Result<Vec<i32>, _> = ["1", "2", "3"].iter().map(|s| s.parse::<i32>()).collect();
let bad: Result<Vec<i32>, _> = ["1", "x", "3"].iter().map(|s| s.parse::<i32>()).collect();
```

`ok` is `Ok([1, 2, 3])`; `bad` is `Err(ParseIntError { kind: InvalidDigit })`, and the `"3"` after the bad entry is never even parsed. The alternative, keeping every good value and separately counting or recording the bad ones instead of stopping the whole run, also exists, and which one is right depends on whether one bad line should sink the batch. That choice belongs to whoever is summarising the input, which is your project's own call to make, not a rule this lesson hands you. Turning that loop into an iterator chain is lesson 12's; here it is one `match` per line, which is control flow you already have:

```rust
let mut rejected = 0;
for s in inputs {
    match s.parse::<i32>() {
        Ok(n) => println!("kept {n}"),
        Err(_) => rejected += 1,
    }
}
```

## Practice

1. ▢ Predict whether this compiles cleanly, and if not, predict the warning it produces. Then compile it.

   ```rust
   fn status_of(line: &str) -> Result<u16, std::num::ParseIntError> {
       line.parse()
   }

   fn main() {
       status_of("200");
   }
   ```

<details markdown="1"><summary>Check</summary>

It compiles, but with a warning that an unused `Result` must be used, the same `#[must_use]` warning `Result` always carries when its value is dropped. The program still runs and prints nothing, which is the point: a parse failure here would pass unnoticed.

</details>

2. ▢ Rewrite this function using `?` instead of `match`, then compile both versions and compare their length.

   ```rust
   fn to_bytes(s: &str) -> Result<u64, std::num::ParseIntError> {
       match s.parse::<u64>() {
           Ok(n) => Ok(n),
           Err(e) => Err(e),
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

`s.parse::<u64>()?` already is the value you want to return; you do not need a `match` or an intermediate binding at all here.

</details>

<details markdown="1"><summary>Check</summary>

```rust
fn to_bytes(s: &str) -> Result<u64, std::num::ParseIntError> {
    Ok(s.parse::<u64>()?)
}
```

Both compile and both give identical results for every input. The `match` version spells out a conversion that changes nothing, `Ok(e)` back to `Ok` and `Err(e)` back to `Err`; `?` says that directly.

</details>

3. ▢ This defines its own error type and tries to use `?` on a `u16::from_str` failure. Predict the error code before compiling.

   ```rust
   struct StatusError;

   fn parse_status(s: &str) -> Result<u16, StatusError> {
       let n = s.parse::<u16>()?;
       Ok(n)
   }
   ```

<details markdown="1"><summary>Check</summary>

`error[E0277]`, because `?` needs `StatusError: From<ParseIntError>` and there is no such implementation. The fix inside this stage's scope is `.map_err(|_| StatusError)` at the call site; the honest fix, an error type that implements `From` for each error it wraps, is stage 3's.

</details>

4. ▢ Predict what this prints and what its exit status is, then run it.

   ```rust
   fn main() -> Result<(), std::num::ParseIntError> {
       let count: u32 = "many".parse()?;
       println!("count is {count}");
       Ok(())
   }
   ```

<details markdown="1"><summary>Hint</summary>

The `println!` never runs. What does `main` do with the `Err` that `?` returns, given that `main`'s own return type is a `Result`?

</details>

<details markdown="1"><summary>Check</summary>

It prints `Error: ParseIntError { kind: InvalidDigit }` to standard error and exits with status 1. The `Err` value's `Debug` form is what appears after `Error: `, which is why a custom error type with a plain `Debug` derive can print something unhelpful here; that is stage 3's problem to solve properly.

</details>

5. ▢ Two log lines below came from the same faulty program, one from a bare `panic!` and one from an `unwrap()` on a `Result`. Which is which, and how do you know without seeing the source?

   ```text
   thread 'main' (9001) panicked at src/main.rs:14:9:
   called `Result::unwrap()` on an `Err` value: StatusError
   ```

   ```text
   thread 'main' (9001) panicked at src/main.rs:22:5:
   status must be a valid HTTP code
   ```

<details markdown="1"><summary>Check</summary>

The first is `unwrap()` on an `Err`: the message names `Result::unwrap()` explicitly and shows the error value's `Debug` form after it. The second is a bare `panic!`: the message is just the string that was passed to the macro, with no mention of `Result` or `unwrap` at all.

</details>

## Real-world reps

- [ ] Change your line parser from returning `Option` to returning `Result`, with a hand-rolled error enum with one variant per way a line can be malformed, such as a missing field and a byte count that will not parse. Use `?` on the numeric parse and `.map_err` to convert its `ParseIntError` into your own variant.
- [ ] Change the summariser so that a rejected line increments a counter instead of stopping the run, and print that count alongside the other totals.
- [ ] Tomorrow: find one `unwrap()` in this project's code and decide, using this lesson's rule, whether it should stay a panic or become a `Result` the caller can handle.

## Going further

- [Recoverable Errors with Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html): `?`, propagation, and `main` returning `Result`
- [E0277](https://doc.rust-lang.org/error_codes/E0277.html): the trait-not-implemented diagnostic behind a failed `?` conversion
- [Termination in std::process](https://doc.rust-lang.org/std/process/trait.Termination.html): what lets `main` return something other than `()`
- [panic in std](https://doc.rust-lang.org/std/macro.panic.html): what the macro does and how `unwrap` uses it
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
