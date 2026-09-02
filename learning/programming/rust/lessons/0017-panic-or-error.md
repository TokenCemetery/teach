---
title: 17. Panic or Error
description: A panic says the program is broken and an error says the input was, and a library rarely gets to decide the first
type: lesson
---

# Lesson 17. Panic or Error

**Mission link:** A `panic!` inside library code is not something a caller can rely on catching, so every panic you leave in is a decision made on their behalf. This lesson turns "panic or return an `Err`" from a feeling into four questions you can run against your own code before shipping it.
**Primary source:** [The Rust Programming Language, To panic! or Not to panic!](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)
**Prerequisites:** [Lesson 10](0010-result.md), [Lesson 15](0015-designing-an-error-type.md)

## Warm-up

1. ▢ Lesson 10 stated the rule for choosing between a panic and a `Result` in one sentence. What was it?

<details markdown="1"><summary>Check</summary>

A `Result` is for a failure the caller could reasonably plan for and recover from; a panic is for a broken invariant in your own code, one that should never happen if the program is correct.

</details>

2. ▢ Lesson 9 named three cases where `unwrap` or `expect` are defensible. Name them.

<details markdown="1"><summary>Check</summary>

A value the surrounding code just proved present, such as `.first()` after checking a `Vec` non-empty. A program whose only correct response to absence is to stop, typically at start-up with no fallback worth computing. And a test, which has already failed if it got `None`.

</details>

## Know this

### Whose mistake, and why it is a library's question

A panic says a rule inside your own code broke and there was nothing the caller could have done differently, since the caller never touched the value that broke it. An error says the input or environment was not what the function requires, and the caller supplied that input or controls that environment, so they may handle it: try a different path, reject one record, keep going. The two answer "whose problem is this" with opposite answers, not two shades of one thing.

That is a library question because of an asymmetry. A function inside your own binary that panics only inconveniences its one caller, you, its author. A function in a library panics on behalf of every caller who depends on it, none of whom agreed to that when they wrote `?` expecting a `Result`. A caller cannot generally catch a panic back in any way worth relying on, so a library that panics has removed a choice from everyone downstream rather than made one. Lesson 15's error type only pays off if the functions around it return it instead of panicking past it.

### What a panic actually does, and the choice behind it

A bare panic prints a fixed shape:

```rust
fn main() {
    panic!("boom");
}
```

```text
thread 'main' (12345) panicked at src/main.rs:2:5:
boom
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

The number in parentheses is a thread identifier, different on every run; the message, file, line and column are what to read, and the process exits with status 101. What happens between the message and the exit is a choice a project makes once, for the whole build, through the `panic` setting in a Cargo profile: `"unwind"`, which "unwind[s] the stack upon panic", or `"abort"`, which "terminate[s] the process upon panic". Both `dev` and `release` default to `"unwind"`, so ordinary code can assume unwinding until a project's `Cargo.toml` says otherwise.

The difference is not cosmetic. Under `"unwind"`, a panic runs every `Drop` up the stack before the process exits: a type that prints on drop still prints. `panic = "abort"` skips that entirely: no destructor runs, and the process aborts rather than exits normally, which most shells report as a distinct, non-101 status since it died to a signal instead of returning one. `"abort"` also leaves `catch_unwind`, met briefly below, nothing to catch.

### Four ways a library panics without meaning to

None of these four say `panic!` in the source, which is why they catch a library author off guard.

Indexing past the end of a slice:

```rust
fn main() {
    let v = vec![1, 2, 3];
    println!("{}", v[5]);
}
```

```text
thread 'main' (12345) panicked at src/main.rs:3:21:
index out of bounds: the len is 3 but the index is 5
```

`unwrap` on a `None`:

```rust
fn main() {
    let x: Option<i32> = None;
    x.unwrap();
}
```

```text
thread 'main' (12345) panicked at src/main.rs:3:7:
called `Option::unwrap()` on a `None` value
```

Integer division by zero:

```rust
fn divide(a: i32, b: i32) -> i32 {
    a / b
}
```

```text
thread 'main' (12345) panicked at src/main.rs:2:5:
attempt to divide by zero
```

Arithmetic overflow, but only sometimes:

```rust
fn add(a: u8, b: u8) -> u8 {
    a + b
}
```

Calling `add(255, 1)` panics in a normal build with `attempt to add with overflow`. Building with `cargo build --release` and running the same call prints `0` instead: the addition wraps rather than panics, because the check is controlled by the `overflow-checks` profile setting, `true` by default for `dev` and `false` for `release`. A reader who tests in a normal build and ships `--release` has changed this behaviour without touching a line of code: the bug does not disappear, it starts returning a wrong number instead of stopping the program.

### `assert!`, `debug_assert!` and `unreachable!`

`assert!` checks its condition and panics if false; the standard library says this "will invoke the panic! macro if the provided expression cannot be evaluated to true", in every profile, with no way to compile it away. It earns its keep for an invariant worth checking even in a shipped binary.

`debug_assert!` is the same macro, compiled in only when `debug-assertions` is on, `true` for `dev` and `false` for `release`, a separate setting from `overflow-checks` following the same pattern. It prints the same panic as `assert!` in a normal build; in `--release` the check and its condition are not evaluated at all, so a side effect inside one stops running too. Reach for it for an invariant you want caught while developing and are willing to ship without, typically because the check costs more than production should pay on every call.

`unreachable!()` panics unconditionally; the standard library names "match arms with guard conditions" among the places "the compiler can't determine that some code is unreachable" even though you can. Reaching it means your own reasoning about which branches are possible was wrong, not that a caller supplied something odd:

```rust
fn main() {
    unreachable!("Kind grew a variant this match does not know about");
}
```

```text
thread 'main' (12345) panicked at src/main.rs:2:5:
internal error: entered unreachable code: Kind grew a variant this match does not know about
```

Its unsafe counterpart, `unreachable_unchecked`, trades the panic for undefined behaviour if you are wrong, the harder meaning "broken invariant" gets in stage 7; `unreachable!` itself only ever panics.

### The decision procedure

Four questions, in order, each answerable from the code in front of you, ending in panic or `Result`.

1. Does the failing value come from outside this function, a caller or the environment, or is it a state your own code already promised to have ruled out? Outside, go to question two; already ruled out, skip to question four.
2. Is there a plausible way forward other than stopping the program, a fallback, a retry, rejecting this one input and continuing? Yes, return `Result`; genuinely not, go to question three.
3. Can the caller see inside this function, or are you both its author and only caller, such as the top of your own binary? A caller who cannot see inside gets `Result`; your own top-level code with no other caller, go to question four.
4. Can you write, in one sentence, the invariant of your own code that broke, the sentence lesson 19's `# Panics` convention asks for? Yes, panic. If that sentence really describes input that merely surprised you, it is not a panic; return `Result` instead.

Five cases, three errors and two panics, from a log summariser and the standard library:

- A byte count field that will not parse: it came from outside the program, and rejecting that line while counting it is the fallback already chosen. `Result`.
- A request line missing a field entirely: same origin, same fallback. `Result`.
- `std::fs::File::open` failing because a path a user typed does not exist: the caller can fix the typo and rerun, and panicking would deny them the message needed to notice it. `Result`, exactly how `File::open` already ships.
- `data.first().unwrap()` reached only after `if data.is_empty() { return; }` two lines above: your own check ruled out the emptiness, not the caller, so nothing is left for them to act on differently. Panic, lesson 9's first exception, earning a `# Panics` line.
- A `match` over an error enum's variants in your own reporting code, with a wildcard arm calling `unreachable!()`: if it ever runs, the fix is a match arm for a variant you forgot, not anything a caller passed in. Panic, and the message should say so.

### One boundary this lesson will not open

`std::panic::catch_unwind` exists and does catch an unwinding panic, turning it into an `Err` the caller can inspect. The standard library is direct about its place: "it is not recommended to use this function for a general try/catch mechanism", naming instead a boundary such as a thread or a call from foreign code that cannot itself unwind. This arc meets that boundary later; here the function is only named so you recognise it.

## Practice

1. ▢ Predict what this prints and its exit status, then run it.

   ```rust
   fn main() {
       let v: Vec<i32> = Vec::new();
       println!("{}", v[0]);
   }
   ```

<details markdown="1"><summary>Check</summary>

It panics with `index out of bounds: the len is 0 but the index is 0` and exits with status 101. An empty `Vec` has no index in range, so `v[0]` fails the same way `v[5]` did above, only with smaller numbers.

</details>

2. ▢ `split(9, 0)` calls this function. Predict whether it panics, then decide with this lesson's procedure whether `split` should panic or return `Result` if `parts` can come from a configuration file a user edits by hand.

   ```rust
   fn split(total: u32, parts: u32) -> u32 {
       total / parts
   }
   ```

<details markdown="1"><summary>Hint</summary>

Question one is about where `parts` came from, not about whether the division machinery can panic.

</details>

<details markdown="1"><summary>Check</summary>

It panics: `attempt to divide by zero`. Since `parts` would come from a file a user edits, questions one and two both point at `Result`: use `checked_div` and turn `None` into an error the caller can report.

</details>

3. ▢ Predict whether this compiles, and if it does not, predict the shape of the diagnostic, then compile it.

   ```rust
   fn main() {
       let count: u8 = 250;
       let extra: u8 = 10;
       println!("{}", count + extra);
   }
   ```

<details markdown="1"><summary>Hint</summary>

Both operands are literals the compiler can work out without running the program at all.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile, in either profile: `error: this arithmetic operation will overflow`, naming `250_u8 + 10_u8`, with `#[deny(arithmetic_overflow)]` on by default. Because both values are constants, the compiler evaluates the addition itself, so it never reaches the profile-dependent behaviour shown above for values that only exist at runtime.

</details>

4. ▢ Predict what this prints in a normal build and in one built with `--release`, then run both.

   ```rust
   fn main() {
       debug_assert!(1 + 1 == 3, "arithmomancy failed");
       println!("still running");
   }
   ```

<details markdown="1"><summary>Check</summary>

A normal build panics with `arithmomancy failed` and never reaches the `println!`. A `--release` build prints `still running`, because `debug_assert!` and its condition are not compiled in at all once `debug-assertions` is off.

</details>

5. ▢ A private helper `combine(a: u8, b: u8) -> u8` is only called from one public function, `checksum`, always with values `checksum` has already validated. A defensive check inside `combine` can fail only if `checksum` itself has a bug. Should that check panic or return `Result`?

<details markdown="1"><summary>Check</summary>

Panic. The failing value never came from outside `combine`'s one caller, code you also wrote, so question one already answers it: this is your own invariant, not the public caller's problem. Returning `Result` would only move the `unwrap` into `checksum`, one line from the bug.

</details>

## Real-world reps

- [ ] Search your project for every `.unwrap()`, `.expect(...)` and bare index expression, and for each one write down which of the four questions answers it and whether the answer is panic or `Result`.
- [ ] Pick one call the search turned up where the value can come from outside the function, such as a field parsed from a log line, and change it from a panic to your project's error type from lesson 15, propagated with `?`.
- [ ] Tomorrow: pick one place you decided should stay a panic, and write the one sentence naming the broken invariant that question four asked for, ready for lesson 19's `# Panics` section.

## Going further

- [Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html): the `panic`, `overflow-checks` and `debug-assertions` settings and their defaults
- [assert in std](https://doc.rust-lang.org/std/macro.assert.html): what `assert!` guarantees and why it cannot be compiled away
- [debug_assert in std](https://doc.rust-lang.org/std/macro.debug_assert.html): the macro this lesson contrasts with `assert!`
- [unreachable in std](https://doc.rust-lang.org/std/macro.unreachable.html): the macro and its unsafe counterpart
- [catch_unwind in std::panic](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html): the boundary function this lesson names but does not teach
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
