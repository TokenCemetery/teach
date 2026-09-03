---
title: 58. Designing for Change
description: The decisions that leave you room to move later, and the ones that quietly promise more than you meant
type: lesson
---

# Lesson 58. Designing for Change

**Mission link:** A caller who builds your struct with a literal, matches your enum exhaustively, or implements your trait has frozen your next release around whatever shape you shipped first; the four tools here keep the parts you have not settled yet, at a real, stated cost to today's convenience.
**Primary source:** [Future proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html)
**Prerequisites:** [Lesson 25](0025-implementing-traits-you-do-not-own.md), [Lesson 57](0057-what-breaks-a-caller.md)

## Warm-up

1. ▢ Lesson 57 named `constructible_struct_adds_field` for a new public field and `enum_variant_added` for a new variant on a plain enum. What do both checks have in common about who is allowed to trigger them?

<details markdown="1"><summary>Check</summary>

Both fire only because the type let a caller reach in directly: a public-field struct can be built with a literal a new field breaks, and a plain enum can be matched exhaustively in a way a new variant breaks. Neither check exists for a type that never gave the caller that access.

</details>

2. ▢ Lesson 25 established coherence: a program has at most one implementation of a trait for a type. What did the orphan rule require before a crate could implement a trait it did not define?

<details markdown="1"><summary>Check</summary>

That the type is local, since the trait itself is foreign. A local wrapper, the newtype pattern, was the escape that did not require owning the trait.

</details>

## Know this

### 1. Two shapes `#[non_exhaustive]` changes

Lesson 57 catalogued what breaks; this lesson decides before a caller can trigger it. `#[non_exhaustive]` marks a struct, enum or variant as still growing, with no effect inside the defining crate. From outside, a struct with public fields loses the literal:

```rust
#[non_exhaustive]
pub struct Viewport {
    pub width: u16,
    pub height: u16,
}
```

```text
error[E0639]: cannot create non-exhaustive struct using struct expression
 --> src/main.rs:4:13
  |
4 |     let c = Viewport { width: 10, height: 20 };
  |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Destructuring is restricted too, more gently: `let Viewport { width, height } = base;` from a dependent crate needs a trailing `..`, since the pattern would otherwise claim nothing is left to ignore. An enum keeps its existing variants constructible; only an exhaustive `match` with no catch-all is forbidden:

```rust
#[non_exhaustive]
pub enum Shape {
    Circle(f64),
    Square(f64),
}
```

```text
error[E0004]: non-exhaustive patterns: `&_` not covered
  --> src/main.rs:4:11
   |
 4 |     match s {
   |           ^ pattern `&_` not covered
   |
   = note: the matched value is of type `&Shape`
   = note: `Shape` is marked as non-exhaustive, so a wildcard `_` is necessary to match exhaustively
help: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
   |
 6 ~         Shape::Square(_) => "square",
 7 ~         &_ => todo!(),
   |
```

A note naming the library's file by its full path is cut here. The room bought is a future variant with no major release; the cost falls on every exhaustive `match`, now carrying an arm it may never need. Adding the attribute later is itself a major change: cargo's own semver reference files "adding `non_exhaustive` to an existing enum, variant, or struct with no private fields" as one, since it revokes literals and matches a caller already relied on. It earns its keep only shipped with the type's first release.

### 2. A constructor, and a sealed trait

A private field paired with a constructor buys a smaller, similar room: the field can be validated or renamed internally, because lesson 18's mechanism means no caller ever named it in a literal.

```rust
pub struct Threshold {
    limit: u32,
}

impl Threshold {
    pub fn new(limit: u32) -> Result<Self, &'static str> {
        if limit == 0 { Err("limit must be positive") } else { Ok(Threshold { limit }) }
    }

    pub fn limit(&self) -> u32 {
        self.limit
    }
}
```

```text
error[E0451]: field `limit` of struct `Threshold` is private
 --> src/main.rs:4:25
  |
4 |     let t = Threshold { limit: 5 };
  |                         ^^^^^ private field
```

The cost is the literal and any functional-update shorthand; the room is a second precondition added later without asking every caller to re-check it. A sealed trait buys room over a different axis: who may implement it at all. A private supertrait no other crate can name closes that door without touching the trait's own methods:

```rust
mod private {
    pub trait Sealed {}
    impl Sealed for Meters {}
}

pub trait Unit: private::Sealed {
    fn to_base(&self) -> f64;
}

pub struct Meters(pub f64);

impl Unit for Meters {
    fn to_base(&self) -> f64 {
        self.0
    }
}
```

A dependent type cannot satisfy a bound it cannot name:

```text
error[E0277]: the trait bound `Feet: unitlib::private::Sealed` is not satisfied
 --> src/main.rs:5:15
  |
5 | impl Unit for Feet {
  |               ^^^^ unsatisfied trait bound
  |
help: the trait `unitlib::private::Sealed` is not implemented for `Feet`
 --> src/main.rs:3:1
  |
3 | struct Feet(f64);
  | ^^^^^^^^^^^
  = note: `Unit` is a "sealed trait", because to implement it you also need to implement `unitlib::private::Sealed`, which is not accessible; this is usually done to force you to use one of the provided types that already implement it
  = help: the following type implements the trait:
            unitlib::Meters
```

Two further notes naming the library's file by its full path are cut here. The compiler names the pattern itself; the cost is that `Unit` can gain a method or a new required item in a minor release with no external `impl` to break, because none exists.

### 3. A newtype around a foreign type

Lesson 25's newtype escaped the orphan rule; the same wrapper buys room when the thing inside is a choice you might reverse. A `HashMap` holds byte totals per path today; exposing it directly means a caller can call `.iter()` on exactly that map type forever.

```rust
pub struct ByteCounts(HashMap<String, u64>);

impl ByteCounts {
    pub fn add(&mut self, path: &str, n: u64) {
        *self.0.entry(path.to_string()).or_insert(0) += n;
    }

    pub fn get(&self, path: &str) -> u64 {
        *self.0.get(path).unwrap_or(&0)
    }
}
```

```text
error[E0599]: no method named `len` found for struct `ByteCounts` in the current scope
 --> src/main.rs:6:22
  |
6 |     println!("{}", b.len());
  |                      ^^^ method not found in `ByteCounts`
```

That failure is the whole cost: every method the wrapped type had is gone unless forwarded on purpose. The room is that swapping the map for something else later changes nothing a caller wrote, since they were never calling `HashMap`'s own methods.

### 4. What public actually commits you to

A public field pins a representation; a public type in a signature must stay nameable, the warning lesson 18 produced for a private return type. An implemented standard trait is a promise too, since removing it is one of lesson 57's breaks. The one nobody expects is an auto trait a type happens to satisfy, never written by hand. A struct built only from `Send` fields is `Send`, though your signature never says so:

```rust
pub struct Job {
    pub name: String,
}
```

```rust
fn print_job(job: Job) {
    println!("{}", job.name);
}

fn main() {
    let j = Job::new("build");
    let handle = std::thread::spawn(move || {
        print_job(j);
    });
    handle.join().unwrap();
}
```

That compiles and runs. Lesson 57 showed the tool catching a private field silently dropping `Send`; here is the other half, what that does to a dependant who changed nothing. Adding one private field nobody reads changes nothing above, yet the same closure now fails to build:

```text
error[E0277]: `*const ()` cannot be sent between threads safely
   --> src/main.rs:9:37
    |
  9 |       let handle = std::thread::spawn(move || {
    |                    ------------------ ^------
    |  __________________|__________________within this `{closure@src/main.rs:9:37: 9:44}`
    | |                  |
    | |                  required by a bound introduced by this call
 10 | |         print_job(j);
 11 | |     });
    | |_____^ `*const ()` cannot be sent between threads safely
    |
    = help: within `{closure@src/main.rs:9:37: 9:44}`, the trait `Send` is not implemented for `*const ()`
note: required because it appears within the type `Job`
```

Two further notes naming the standard library's own source, by full path, are cut here too. Nothing in `Job`'s public surface named `Send`; the field that removed it is not even `pub`. This is the auto trait already named in the glossary: nobody writes it, so a type loses it from something several layers inside, discovered the day a dependant crosses a thread boundary.

### 5. `#[doc(hidden)]` and the honest truth about it

`#[doc(hidden)]` removes an item from generated documentation and nothing else. A hidden function stays exactly as public as the keyword says:

```rust
#[doc(hidden)]
pub fn internal_helper() -> u32 {
    21
}
```

Called from a dependent crate, by its full path or via `use`, it compiles and runs, printing `21`; generated docs carry the page for the ordinary public function beside it but no page for this one, since rustdoc's manual says a hidden item is omitted from the documentation, not from the crate. That gap between what a caller can read and call is a workaround, not a design: legitimate for an item rustdoc must generate for a macro but nobody should call directly, wrong wherever it dodges deciding something should be public.

### 6. Designing an error type for change, and the trade itself

Lesson 15 built an error enum from its callers; lesson 16 chose between wrapping a foreign error and converting it. Stage 8 adds one question to both. An error enum wants `#[non_exhaustive]` from its first release, for the same reason as any other enum: a new variant is nearly guaranteed as a library grows. Exposing a dependency's error type directly in a variant hands a caller its whole API, not just its message:

```rust
pub enum LeakyError {
    Upstream(serde_json::Error),
    Malformed { field: &'static str },
}
```

A caller matching `Upstream` can call `serde_json::Error`'s own methods, such as `e.classify()`, printing `classify: Syntax` today; that dependency's next release can now change what the call does. Converting instead keeps only what your own type needs:

```rust
#[non_exhaustive]
pub enum SummaryError {
    Parse(String),
    Malformed { field: &'static str },
}

impl From<serde_json::Error> for SummaryError {
    fn from(e: serde_json::Error) -> Self {
        SummaryError::Parse(e.to_string())
    }
}
```

```text
bytes: 1200
error: missing field bytes
error: could not parse record: expected ident at line 1 column 2
```

`SummaryError` never names `serde_json` in its own shape, so that dependency's next major version stays a private decision. Every tool here trades convenience for room, and how much to spend depends on how many dependants you expect and how settled the design is. A `Point { x: f64, y: f64 }` passed around one process, with no invariant beyond two numbers, is more useful with public fields than behind a constructor, since there is nothing to protect. A byte-count map still being redesigned wants the newtype today, before a caller depends on `HashMap` specifically. A trait meant for one implementation while the design still moves wants sealing, only for as long as that stays true. Running cargo-semver-checks against a library's previous commit, after applying the three tools touching existing items, confirmed the shape meant: the non-exhaustive enum, the hidden field, and the sealed trait each produced a named failure, five in total against `196 checks: 191 pass, 5 fail`. A fourth change, a newtype-returning iterator method added beside the map, produced none, since nothing already public changed shape.

## Practice

1. ▢ Using `Viewport` above, predict whether `Viewport { width: 1, height: 1 }` compiles inside the defining crate, then whether `let Viewport { width, height } = base;` compiles from a dependent crate, with no `..`.

<details markdown="1"><summary>Check</summary>

The literal compiles inside the defining crate, since `#[non_exhaustive]` is only checked at the crate boundary. The destructuring pattern fails from a dependent crate with `E0638`, `..` required with struct marked as non-exhaustive, since a pattern naming every field would otherwise claim there is nothing left to add.

</details>

2. ▢ Predict the error code a dependent crate gets for `impl Unit for Feet`, and the one term the compiler's own note uses for the pattern `Unit` follows.

<details markdown="1"><summary>Hint</summary>

The note does not say "private trait"; it reaches for the term this lesson's heading uses.

</details>

<details markdown="1"><summary>Check</summary>

`E0277`, the unsatisfied `Sealed` bound, and the note calls `Unit` a "sealed trait" by name.

</details>

3. ▢ `Job` gains the private `tag: std::marker::PhantomData<*const ()>` field. Predict whether `std::thread::spawn(move || { println!("{}", j.name); })`, touching only `j.name` and never passing `j` itself anywhere, still compiles.

<details markdown="1"><summary>Hint</summary>

Ask which fields of `j` the closure actually captures, under the 2021 edition's field-by-field capture rule.

</details>

<details markdown="1"><summary>Check</summary>

It still compiles. The closure captures only `j.name`, a `String`, not the whole `Job`, so the non-`Send` `tag` field never crosses the boundary; only passing the whole `Job`, as to `print_job`, requires `Job: Send` and fails.

</details>

4. ▢ Predict whether bringing `internal_helper` into scope with `use` and calling it bare behaves any differently from calling it by its full path.

<details markdown="1"><summary>Check</summary>

No differently at all: it compiles and prints `21` either way, since `#[doc(hidden)]` changes nothing about privacy or `use`, only what rustdoc renders.

</details>

5. ▢ A project sealed a trait, hid a field behind a constructor, marked an error enum non-exhaustive, and added a newtype-returning iterator method. Predict how many of cargo-semver-checks' failures the fourth change caused.

<details markdown="1"><summary>Check</summary>

None. The other three each cost at least one named failure, and hiding the field cost two, for five in total, but the new iterator method was purely additive: nothing already public changed shape.

</details>

## Real-world reps

- [ ] Apply this lesson's four tools to your summariser's public API only where a real dependant would be hurt without them, the error type, the byte-count map, and any trait a caller could implement, one line per decision saying what it bought and what it took away.
- [ ] Run cargo-semver-checks against your previous commit and confirm every failure is one you meant; where it names one you did not expect, decide on the spot whether to keep the change or take it back.
- [ ] Tomorrow: run `cargo publish --dry-run` on your summariser and read what the manifest is missing, so publishing it for real is one command away.

## Going further

- [SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html): cargo's own list of what counts as major, minor, or merely possible
- [Send in std::marker](https://doc.rust-lang.org/std/marker/trait.Send.html): the auto trait behind this lesson's `Job` example
- [hidden](https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html#hidden): what the attribute does and does not do
- [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks): the tool behind every named failure here
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
