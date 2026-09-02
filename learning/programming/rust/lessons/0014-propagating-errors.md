---
title: 14. Propagating Errors
description: The question mark converts as it returns, so the error type in your signature decides what it will accept
type: lesson
---

# Lesson 14. Propagating Errors

**Mission link:** A function stacking several fallible calls behind hand-written `match` arms is either long enough that a reviewer stops reading closely, or it quietly narrows every error down to one string; `?` collapses that stack to one call each, but only once the signature names an error type that can absorb every failure it meets.
**Primary source:** [Recoverable Errors with Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
**Prerequisites:** [Lesson 10](0010-result.md), [Lesson 9](0009-option.md)

## Warm-up

1. ▢ Lesson 10 wrote `s.parse::<i32>()?` inside a function returning `Result<i32, ParseIntError>`, in place of a four-line `match`. In plain words, what does that one character do on the `Ok` case and on the `Err` case?

<details markdown="1"><summary>Check</summary>

On `Ok(v)` it unwraps to `v` and execution carries on as if you had written the value directly. On `Err(e)` it returns from the enclosing function immediately, handing back the error. Lesson 10 stopped there and called it a shortcut for `match`; this lesson opens up what happens to `e` on the way out, which is the one detail that decides whether `?` compiles at all.

</details>

2. ▢ Lesson 9's `ok_or` turns `None` into `Err(e)` for whatever `e` you supply, and leaves `Some(x)` as `Ok(x)`. If one step of a `Result`-returning function only has an `Option` to work with, what does `ok_or` let you do before you can reach for `?` on that step?

<details markdown="1"><summary>Check</summary>

`ok_or` supplies the missing error value up front, turning the `Option` into a `Result` you can call `?` on directly. `?` only understands `Result` inside a function that returns `Result`; `ok_or`, or `ok_or_else` when computing the error costs something, is the bridge that gets an absence there, which is exactly the mismatch this lesson runs into further down.

</details>

## Know this

### The step `?` hides: unwrap, or convert and return

Lesson 10 used `?` to shorten a `match` but never opened up what it does. On a `Result`, `expr?` behaves like this, written out by hand rather than as a macro:

```rust
// let n = expr?; desugars to roughly:
let n = match expr {
    Ok(v) => v,
    Err(e) => return Err(From::from(e)),
};
```

Two functions built from the two forms give identical results for every input: `s.parse::<i32>()?` and the hand-written `match` above both give `Ok(42)` for `"21"` and `Err(ParseIntError { kind: InvalidDigit })` for `"x"`. The unwrapping half, `Ok(v) => v`, is the part everyone remembers about `?`. The half worth fixing in your head instead is `Err(e) => return Err(From::from(e))`: `?` does not hand the `Err` value back unchanged, it hands back whatever the function's own error type converts it into through `From`. Every consequence in the rest of this lesson follows from that one conversion step, not from the unwrapping.

### The conversion requirement, met head-on

Lesson 10 already showed this once with its own `MyError`, so here is the same mechanism against a fresh function, reading the byte count out of a line with the crate's own `parse`:

```rust
#[derive(Debug)]
struct ReadError(String);

fn read_bytes(line: &str) -> Result<u64, ReadError> {
    let (_path, bytes) = errprobe::parse(line)?;
    Ok(bytes)
}
```

```text
error[E0277]: `?` couldn't convert the error to `ReadError`
 --> src/bin/read.rs:5:47
  |
4 | fn read_bytes(line: &str) -> Result<u64, ReadError> {
  |                              ---------------------- expected `ReadError` because of this
5 |     let (_path, bytes) = errprobe::parse(line)?;
  |                          ---------------------^ the trait `From<ParseError>` is not implemented for `ReadError`
  |                          |
  |                          this can't be annotated with `?` because it has type `Result<_, ParseError>`
  |
note: `ReadError` needs to implement `From<ParseError>`
```

There are exactly three ways past this. The first is a real `From<ParseError>` implementation for `ReadError`, so `?` has a conversion to call; writing one well, for every error a type needs to absorb, is lesson 16's subject, named here rather than built. The second is `map_err` at the call site, needing no `From` at all: `errprobe::parse(line).map_err(|e| ReadError(e.to_string()))?` compiles and gives `Err(ReadError("missing field bytes"))`. The third drops the local error type and widens the signature to `Result<u64, Box<dyn std::error::Error>>`; with that return type the original `errprobe::parse(line)?` compiles unchanged, and a caller prints the boxed value with `{}` to get `missing field bytes` straight out. That third option costs something specific: a caller who wants to branch rather than just print has to guess a concrete type and ask for it back with `downcast_ref`, verified working when the guess matches and giving `None` when it does not. That guessing game is exactly what a library should not hand a caller, so the `From` implementation is what to reach for there; `map_err` is a fine stopgap for one or two call sites, and `Box<dyn Error>` earns its keep at a binary's edge, where nothing downstream needs to match on the failure.

### One function, two kinds of failure

A function that reads a count and then a field fails in two unrelated ways, and `?` needs telling how both convert. Written with `map_err` at each site and no shared error type:

```rust
fn read_record_a(count: &str, line: &str) -> Result<(i32, String), String> {
    let n: i32 = count.parse().map_err(|e| format!("bad count: {e}"))?;
    let (path, _) = errprobe::parse(line).map_err(|e| format!("bad line: {e}"))?;
    Ok((n, path.to_string()))
}
```

This gives `Err("bad count: invalid digit found in string")` and `Err("bad line: missing field bytes")` for the two bad inputs, and it costs nothing to read locally: each line states its own failure in English on the spot. It costs the caller everything: `String` carries no structure, so telling the two failures apart means parsing prose. The alternative gives both calls one error type to convert into:

```rust
#[derive(Debug)]
enum RecordError {
    Count(std::num::ParseIntError),
    Line(errprobe::ParseError),
}

fn read_record_b(count: &str, line: &str) -> Result<(i32, String), RecordError> {
    let n: i32 = count.parse()?;
    let (path, _) = errprobe::parse(line)?;
    Ok((n, path.to_string()))
}
```

With `From<ParseIntError>` and `From<errprobe::ParseError>` written for `RecordError`, this gives `Err(Count(ParseIntError { kind: InvalidDigit }))` and `Err(Line(MissingField { field: "bytes" }))`. It costs two small `From` implementations up front, boilerplate lesson 16 automates, but the signature now names two variants a caller can match on with an ordinary `match`, rather than a sentence they have to parse back apart.

### `?` on `Option`, and where it stops

`?` works the same way in a function returning `Option`, unwrapping `Some` and returning `None` early with nothing to convert: `s.chars().last()?` inside a function returning `Option<char>` gives `Some('h')` for `"teach"` and `None` for `""`. It does not, on its own, cross into a function returning `Result`:

```rust
fn first_char_checked(s: &str) -> Result<char, String> {
    let c = s.chars().next()?;
    Ok(c)
}
```

```text
error[E0277]: the `?` operator can only be used on `Result`s, not `Option`s, in a function that returns `Result`
 --> src/bin/mismatch.rs:2:29
  |
1 | fn first_char_checked(s: &str) -> Result<char, String> {
  | ------------------------------------------------------ this function returns a `Result`
2 |     let c = s.chars().next()?;
  |                             ^ use `.ok_or(...)?` to provide an error compatible with `Result<char, String>`
```

The compiler's own suggestion is the fix from the warm-up: `s.chars().next().ok_or("empty string".to_string())?` compiles and gives `Err("empty string")`. `ok_or_else` takes a closure instead of a value, useful when the error is worth building lazily: `s.chars().next().ok_or_else(|| format!("{s:?} is empty"))?` gives `Err("\"\" is empty")` for the same input.

### `?` in `main`, and which form of the error it prints

Lesson 10 already showed `fn main() -> Result<(), E>` failing with `Error: ` followed by the error's printed form; the part worth adding is which form that is. Printing the same `ParseError` value both ways side by side, `println!("{e}")` gives `missing field bytes`, its `Display`, while `println!("{e:?}")` gives `MissingField { field: "bytes" }`, its `Debug`. Running a `main` whose `?` fails on that same value prints `Error: MissingField { field: "bytes" }` on standard error and exits with status 1: the line after `Error: ` is the `Debug` form, not the friendlier `Display` one. That is worth knowing on its own terms, because it means an error type wants a `Debug` a reader can make sense of, not just a good `Display`; a plain `#[derive(Debug)]` that dumps every field is often enough for that, but it is a decision, not an accident.

### Where `?` cannot go

Three shapes reject `?` with the same diagnostic, each for a different reason. A closure passed to `map` that returns `i32` rather than a `Result` or `Option`, as in `.map(|s| { let n = s.parse::<i32>()?; n * 2 })`, fails because the closure itself must return `Result` or `Option`; the fix is to make it return one and collect the whole chain into a `Result`, `.map(|s| s.parse::<i32>().map(|n| n * 2))`. A function returning `()` fails the same way, needing a `Result` or `Option` return type to hand the early return to; the fix is `Result<(), Box<dyn std::error::Error>>` at a binary's edge, or a named error type in a library. A `#[test]` function, which returns `()` by default, fails identically, and the fix is the same: `fn my_test() -> Result<(), Box<dyn std::error::Error>>`, ending with `Ok(())`. None of these three is a case for reaching past `Result` into `panic!` instead; whether a failure deserves a `Result` or a panic is a separate call, and lesson 17 is where that rule lives.

## Practice

1. ▢ Predict whether this compiles, and if not, predict the diagnostic's code.

   ```rust
   #[derive(Debug)]
   struct LoadError;

   fn load_count(s: &str) -> Result<u32, LoadError> {
       let n = s.parse::<u32>()?;
       Ok(n)
   }
   ```

<details markdown="1"><summary>Check</summary>

It fails with `E0277`, because `?` needs `LoadError: From<ParseIntError>` and `LoadError` implements no such thing. The message is the same shape every time this mistake happens: it names the trait that is missing rather than anything wrong with the parsing itself.

</details>

2. ▢ Fix the previous function with `map_err` instead of a `From` implementation, giving `LoadError` a field to carry the message, then compile and run it against `"12"` and `"x"`.

<details markdown="1"><summary>Hint</summary>

`map_err` goes between the fallible call and the `?`, not after it: `s.parse::<u32>().map_err(|e| LoadError(e.to_string()))?`.

</details>

<details markdown="1"><summary>Check</summary>

```rust
#[derive(Debug)]
struct LoadError(String);

fn load_count(s: &str) -> Result<u32, LoadError> {
    let n = s.parse::<u32>().map_err(|e| LoadError(e.to_string()))?;
    Ok(n)
}
```

This gives `Ok(12)` and `Err(LoadError("invalid digit found in string"))`. Nothing about `?` changed; only the `Result` it now receives already has the right error type.

</details>

3. ▢ Predict what this prints for `"teach"` and for `""`, then compile and run it.

   ```rust
   fn last_char(s: &str) -> Option<char> {
       let c = s.chars().last()?;
       Some(c)
   }
   ```

<details markdown="1"><summary>Check</summary>

`Some('h')` and `None`. `?` on an `Option` inside a function returning `Option` is the unwrap-or-return-early behaviour with nothing to convert, since there is no `Err` payload on either side.

</details>

4. ▢ This test has no return type, so it is `()` by default. Predict the diagnostic, then fix it so the test compiles and passes.

   ```rust
   #[test]
   fn parses_bytes() {
       let n = "1200".parse::<u64>()?;
       assert_eq!(n, 1200);
   }
   ```

<details markdown="1"><summary>Hint</summary>

The fix is the same one the compiler suggests for a plain function: give the test a return type `?` can work with, and end it with `Ok(())`.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `E0277`, because a test with no return type is exactly that: a function returning `()`, and `?` needs a `Result` or `Option` return type to hand its early return to. Giving it `-> Result<(), Box<dyn std::error::Error>>` and a final `Ok(())` fixes it, and the fixed version compiles and passes.

</details>

5. ▢ Two versions of a record reader exist, one with `map_err` at each call and one with a shared `RecordError` enum both calls convert into. A teammate wants to `match` on which of the two calls failed without inspecting a string. Which version does that, and what did the other version's author have to write that this one's did not?

<details markdown="1"><summary>Hint</summary>

Look at what a caller receives from each: a `String` built by `format!`, or an enum with a variant per failure.

</details>

<details markdown="1"><summary>Check</summary>

The shared-`RecordError` version supports that `match`, because its two variants carry the original errors rather than a sentence describing them. Its author had to write, once, a `From` implementation for each error the two calls can produce; the `map_err` version's author wrote no `From` implementation at all, at the cost of a caller who can only compare strings.

</details>

## Real-world reps

- [ ] Replace every hand-written `match` on a `Result` in your summariser's line-parsing and record-reading functions with `?` and one shared error type, then write, in a sentence, what the resulting signature now promises a caller that a bare `match` returning a `String` never did.
- [ ] Make your summariser's `main` return `Result<(), Box<dyn std::error::Error>>`, so a line your parser cannot handle stops the run with a printed error instead of a silently wrong count or a panic.
- [ ] Tomorrow: find one call in your summariser where a callee's error type does not already match its caller's, and note whether you reached for `map_err` or a shared error type to make `?` compile there, and why that was the right stopgap or the right fix.

## Going further

- [E0277](https://doc.rust-lang.org/error_codes/E0277.html): the trait-not-implemented diagnostic behind every failed `?` conversion
- [Option in std::option](https://doc.rust-lang.org/std/option/enum.Option.html#method.ok_or_else): `ok_or` and `ok_or_else`, the two bridges from `Option` to `Result`
- [Result in std::result](https://doc.rust-lang.org/std/result/enum.Result.html#method.map_err): `map_err`, the call-site conversion that needs no `From` implementation
- [Operator expressions](https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-try-propagation-expression): the Reference's rule for what `?` desugars to and what it requires, under the name it now carries
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
