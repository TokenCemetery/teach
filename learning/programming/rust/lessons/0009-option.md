---
title: 9. Option, and Handling Absence
description: Absence is a value of a different type, so the compiler makes you say what happens when it arrives
type: lesson
---

# Lesson 9. Option, and Handling Absence

**Mission link:** A value that might be missing has a different type from one that is not, so the compiler will not let a caller forget the missing case, which turns a defect that waits for production into one the compiler catches now.
**Primary source:** [std::option](https://doc.rust-lang.org/std/option/index.html)
**Prerequisites:** [Lesson 8](0008-enums.md), [Lesson 4](0004-slices-string-and-str.md)

## Warm-up

1. ▢ Lesson 8 showed that an enum can carry a different payload per variant. `Option<T>` is defined as `enum Option<T> { None, Some(T) }`. Does the compiler treat it specially, or is it exactly the enum lesson 8 already taught you to read?

<details markdown="1"><summary>Check</summary>

Nothing special. `Option<T>` is an ordinary enum from the standard library, not a keyword or a built-in feature, so it gets exhaustiveness checking and pattern matching for free, the same as any enum from lesson 8. Only how often it turns up makes it feel different.

</details>

2. ▢ Lesson 4 said a `&str` is a borrowed view into string data: a pointer and a length, owning nothing. Is there a value of that type that means "no string"?

<details markdown="1"><summary>Check</summary>

No. An empty `&str` is a string of length zero, not an absent one, and there is no null pointer to smuggle absence in through. When there might be no string at all, the type that says so is `Option<&str>`, never `&str` on its own.

</details>

## Know this

### Absence is a different type, not a special value

Rust has no null. There is no value of type `i32` that means "no `i32`", and no value of type `&str` that means "no string" either, as the warm-up just established. When a value might be missing, that possibility gets its own type, `Option<T>`, an ordinary enum with two variants: `None` for absent and `Some(T)` for present, holding a `T`. Because `Option<T>` and `T` are different types, the compiler enforces the distinction wherever the two might get confused.

```rust
fn takes_i32(n: i32) {
    println!("{n}");
}

fn main() {
    let maybe: Option<i32> = Some(5);
    takes_i32(maybe);
}
```

```text
error[E0308]: mismatched types
 --> src/main.rs:7:15
  |
7 |     takes_i32(maybe);
  |     --------- ^^^^^ expected `i32`, found `Option<i32>`
  |     |
  |     arguments to this function are incorrect
  |
  = note: expected type `i32`
             found enum `Option<i32>`
```

Trimmed of a `help` suggestion and the "for more information" line; the rest is what the compiler printed. This buys visibility: a signature reading `fn takes_i32(n: i32)` tells you, without reading its body, that `n` is never missing, and one reading `Option<i32>` is where you know the opposite. Nothing can quietly hand a caller an absent value where a present one was promised, because the two are different types and doing so is exactly the error above.

### Reaching for the value: `if let` and `let ... else`

A `match` can take an `Option` apart with full exhaustiveness checking and guards, and lesson 11 owns it properly. Most of the time reaching for the value needs less, and this lesson keeps to the two forms it owns, plus the combinators next.

`if let` handles the one case you care about, with a plain `else` for the rest:

```rust
let name: Option<&str> = Some("ferris");
if let Some(n) = name {
    println!("hello, {n}");
}
```

That prints `hello, ferris`; with `name` bound to `None` and an `else` branch added, it prints whatever the `else` branch says instead.

`let ... else` is for the early-return shape: when the rest of a function only makes sense with the value present, `let ... else` pulls the value into the surrounding scope and diverges in the `else` block, rather than nesting everything else inside an `if let`.

```rust
fn first_word(s: &str) -> &str {
    let Some(word) = s.split_whitespace().next() else {
        return "";
    };
    word
}
```

`first_word("hello there")` returns `"hello"`; `first_word("   ")` finds no word and returns `""` from the `else` block before `word` is ever bound. `let ... else` stabilised in Rust 1.65.0, announced 3 November 2022: "This introduces a new type of `let` statement with a refutable pattern and a diverging `else` block that executes when that pattern doesn't match." Material predating that release reaches for `match` or a nested `if let` here instead, a sign of the toolchain it assumes rather than a better style.

### The combinators worth knowing

Each answers one question about an `Option` without unwrapping it by hand.

`map` transforms the value that is there and leaves `None` alone: `Some(1200u32).map(|b| b * 2)` gives `Some(2400)`.

`and_then` chains another lookup that may itself come back empty, rather than nesting an `Option<Option<T>>`:

```rust
fn parse_status(s: &str) -> Option<u32> {
    s.parse().ok()
}
let status: Option<&str> = Some("200");
println!("{:?}", status.and_then(parse_status));
```

That prints `Some(200)`; starting from `Some("oops")` it prints `None`, since `and_then` never gets a value to hand the closure once the chain has already produced a `None`.

`unwrap_or`, `unwrap_or_else` and `unwrap_or_default` all supply a fallback for `None`, differing only in how eager the fallback is: `unwrap_or(0)` builds its argument regardless, `unwrap_or_else(|| 7 * 6)` only runs the closure when needed, and `unwrap_or_default()` reaches for the type's `Default`. On a `None: Option<u32>` they print `0`, `42` and `0` in turn.

`ok_or` turns an absence into an error value, the bridge lesson 10 uses to reach `?`: `None.ok_or("missing byte count")` gives `Err("missing byte count")`, and a `Some` gives `Ok` of the inner value.

`filter` keeps a `Some` only if a predicate holds on the value inside, and turns it into `None` otherwise: on `Some(5)`, filtering by `|&x| x > 3` keeps `Some(5)`, and by `|&x| x > 10` gives `None`.

`is_some` and `is_none` ask the question without touching the value: on `Some(5)` they give `true` and `false`. Reaching for `map` or `filter` first is usually the better habit, since they act on the value in the same step instead of asking and then unwrapping separately.

`as_ref` looks inside an `Option<T>` without moving the `T` out, and earns its place as the fix for a real error rather than a habit to sprinkle everywhere. A struct field of type `Option<String>` can only be moved out of once:

```rust
struct Record {
    path: Option<String>,
}

fn main() {
    let rec = Record { path: Some(String::from("/index")) };
    if let Some(p) = rec.path {
        println!("path: {p}");
    }
    if let Some(p) = rec.path {
        println!("path again: {p}");
    }
}
```

```text
error[E0382]: use of moved value
  --> src/main.rs:10:17
   |
 7 |     if let Some(p) = rec.path {
   |                 - value moved here
...
10 |     if let Some(p) = rec.path {
   |                 ^ value used here after move
   |
   = note: move occurs because value has type `String`, which does not implement the `Copy` trait
```

The first `if let` moved the `String` out of `rec.path`, so the second has nothing left to read. Replacing both occurrences with `rec.path.as_ref()` fixes it: each call produces a borrowed `Option<&String>` rather than a moved `Option<String>`, so `path: /index` prints twice with `rec` still intact.

### `take` and `replace`

This is the one method here that looks surprising until it is motivated. A struct field holds an `Option<String>`, and a function with only a `&mut` to the struct has to hand that value to its caller:

```rust
struct Buffer {
    data: Option<String>,
}

fn drain(buf: &mut Buffer) -> Option<String> {
    buf.data
}
```

```text
error[E0507]: cannot move out of `buf.data` which is behind a mutable reference
 --> src/main.rs:6:5
  |
6 |     buf.data
  |     ^^^^^^^^ move occurs because `buf.data` has type `Option<String>`, which does not implement the `Copy` trait
```

The compiler suggests `.clone()`, which compiles and is the wrong fix: an allocation spent on a rule `take` satisfies for free. `Option::take` replaces the field with `None` and hands back what was there:

```rust
fn drain(buf: &mut Buffer) -> Option<String> {
    buf.data.take()
}
```

Calling that on a `Buffer` whose `data` is `Some("payload")` returns `Some("payload")` and leaves `buf.data` as `None`; nothing was cloned, and the field ends up in a valid state because `None` is always a valid `Option<String>`. `replace` is `take`'s sibling: `slot.replace(2)` on a `slot` holding `Some(1)` returns `Some(1)`, the old value, leaving `slot` as `Some(2)` rather than `None`.

### When `unwrap` and `expect` are defensible

`unwrap` and `expect` are not banned, and a rule a reader breaks silently the first time a deadline is tight is worse than a rule with a stated exception, so here are the three cases honestly. A value the surrounding code has just proved present, such as `.first()` on a `Vec` checked non-empty a line earlier, where the `Option` is real but the answer is already known. A program whose only correct response to absence is to stop, typically at start-up, where a missing configuration key has no fallback worth computing and no caller worth returning an error to. And a test, which has already failed if it got `None`, so a loud panic is exactly the behaviour it wants.

Outside those three, the discipline is this: `expect` takes a message describing what the surrounding code believed, not what went wrong, since the panic already says that; write it as the answer to "why did I think this was safe", such as `.expect("port was validated at start-up")`. A bare `unwrap` is fine in a quick example or a test; it has no place in library code a caller cannot see inside of, because its panic names only the type, never the reasoning. The two look different in a log:

```text
thread 'main' (12345) panicked at src/main.rs:3:24:
request line must have a byte count by this point
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

```text
thread 'main' (12345) panicked at src/main.rs:3:24:
called `Option::unwrap()` on a `None` value
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

The number in parentheses is a thread identifier and differs on every run, so read the file, line and message rather than it. The first message names the invariant that broke; the second names only that something was empty. Recognising the shape of each is the point: one gives a future reader of the log something to act on, the other sends them back to the source to find out what failed.

### `Option` in a signature

Taking `Option<T>` as a parameter when the caller almost always has a value pushes the "what if it is missing" question onto every call site, which usually cannot answer it any better than the function could:

```rust
fn greet_avoid(name: Option<&str>) {
    let name = name.unwrap_or("stranger");
    println!("hello, {name}");
}
```

Every caller with a real name now has to wrap it in `Some` for no benefit. Taking `&str` plainly, and letting the caller decide what "no name" means before calling, is usually the better shape:

```rust
fn greet(name: &str) {
    println!("hello, {name}");
}
```

Returning `Option<T>` is usually right in the other direction, when absence is normal rather than exceptional, such as a field a line of input may or may not carry:

```rust
fn find_referrer(line: &str) -> Option<String> {
    line.split_whitespace().nth(3).map(str::to_string)
}
```

On a line with a fourth field this gives `Some` of it, and on one without it gives `None`, which a call site can turn into a fallback with `unwrap_or_else` rather than a reason to fail. When absence is exceptional instead, with no reasonable fallback and a right response of saying why, that is lesson 10's `Result` rather than this lesson's `Option`.

## Practice

1. ▢ Predict whether this compiles, and if not, which error code you expect, then compile it.

   ```rust
   fn main() {
       let n: i32 = Some(5);
       println!("{n}");
   }
   ```

<details markdown="1"><summary>Check</summary>

Does not compile: `E0308`, "expected `i32`, found `Option<{integer}>`". `Some(5)` and an `i32` are different types no matter how obviously "there" the `5` is; the compiler never narrows `Option<T>` to `T` just because a literal sits inside it.

</details>

2. ▢ Predict what each of these two calls prints, then compile and run it.

   ```rust
   fn stock_message(stock: Option<u32>) -> String {
       let Some(n) = stock else {
           return String::from("out of stock");
       };
       format!("{n} left")
   }

   fn main() {
       println!("{}", stock_message(Some(3)));
       println!("{}", stock_message(None));
   }
   ```

<details markdown="1"><summary>Check</summary>

`3 left`, then `out of stock`. The second call never reaches `n`: the pattern fails to match `None`, so the `else` block runs and returns before `format!` is reached.

</details>

3. ▢ Predict what this prints for `vec![]` and for `vec![9]`, then compile and run it.

   ```rust
   fn main() {
       let empty: Vec<i32> = vec![];
       let one = vec![9];
       println!("{}", empty.first().map(|x| x + 1).unwrap_or(0));
       println!("{}", one.first().map(|x| x + 1).unwrap_or(0));
   }
   ```

<details markdown="1"><summary>Hint</summary>

`first()` already returns an `Option`; work out what `map` does to each of `None` and `Some(&9)` before the `unwrap_or` ever runs.

</details>

<details markdown="1"><summary>Check</summary>

`0`, then `10`. `empty.first()` is `None`, and `map` leaves it alone, so `unwrap_or(0)` supplies the `0`. `one.first()` is `Some(&9)`, `map` produces `Some(10)`, and `unwrap_or(0)` has nothing to do.

</details>

4. ▢ Predict whether this compiles; if not, name the error code, then fix it with `as_ref` without changing the struct.

   ```rust
   struct Record {
       path: Option<String>,
   }

   fn main() {
       let rec = Record { path: Some(String::from("/index")) };
       if let Some(p) = rec.path {
           println!("{p}");
       }
       if let Some(p) = rec.path {
           println!("{p}");
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

The first block already took something out of `rec.path`. What does the second block have left to read?

</details>

<details markdown="1"><summary>Check</summary>

Does not compile: `E0382`, use of a moved value, since the first `if let` moved the `String` out of `rec.path` and the second has nothing left. Changing both occurrences to `rec.path.as_ref()` fixes it: each block borrows an `Option<&String>` instead of moving an `Option<String>`, and both print `/index`.

</details>

5. ▢ This one is a judgement call, not a compile check. For each line, say whether this lesson's three exceptions justify the `unwrap` or `expect`, or whether it should return `Option` and let the caller decide instead.

   - a) `let first = names.first().unwrap();`, immediately after `if names.is_empty() { return; }`
   - b) `let port: u16 = std::env::var("PORT").ok().unwrap().parse().unwrap();`, in a web server's start-up code, with no check beforehand
   - c) `let parsed: u32 = "42".parse().unwrap();`, inside a `#[test]` function

<details markdown="1"><summary>Check</summary>

a) Defensible: the emptiness was just ruled out above, so the surrounding code has proved the value present, the first exception.

b) Not defensible as written: nothing before it proves `PORT` is set or parses, and a bare `unwrap` only logs that something was `None`, not which variable was missing. The second exception could apply, since a server that cannot read its port has no way to continue, but it needs `.expect("PORT must be set to a valid u16")` at minimum, so the message names the actual problem.

c) Defensible: a test, the third exception, on a literal known to parse.

</details>

## Real-world reps

- [ ] In your `logsum` project, pick a field that is genuinely optional on a line, such as a trailing referrer, and write a function returning `Option<String>` for it. At the call site, handle the `None` with `unwrap_or_else` or `filter` rather than `unwrap`, and check that a line with the field and one without both produce sensible output.
- [ ] Reproduce this lesson's `as_ref` error against a struct of your own: an `Option<String>` field read with `if let Some(p) = rec.path` in two places in one function. Fix it with `as_ref` and confirm both reads compile.
- [ ] Tomorrow: without looking back, list the three cases where `unwrap` or `expect` are defensible, then check your list against the lesson.

## Going further

- [The Option Enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum): why Option replaces null, from the enums chapter
- [Announcing Rust 1.65.0](https://blog.rust-lang.org/2022/11/03/Rust-1.65.0.html): the release that stabilised `let ... else`
- [E0308](https://doc.rust-lang.org/error_codes/E0308.html): the mismatched-types code, with minimal reproductions
- [Option](https://doc.rust-lang.org/std/option/enum.Option.html): the enum itself, with every combinator's exact signature
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
