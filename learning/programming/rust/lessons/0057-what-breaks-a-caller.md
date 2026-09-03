---
title: 57. What Breaks a Caller
description: The changes that need a major version, the ones that only look safe, and the tool that tells you which is which
type: lesson
---

# Lesson 57. What Breaks a Caller

**Mission link:** A crate with users has promised what keeps compiling, and a change that quietly breaks that promise without a major version bump turns a routine release into somebody else's emergency; this lesson catches the break first.
**Primary source:** [SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
**Prerequisites:** [Lesson 16](0016-conversions-and-boundaries.md), [Lesson 18](0018-modules-and-visibility.md)

## Warm-up

1. ▢ Lesson 18 listed a crate's public API as every `pub` item, every field of a `pub` struct, every variant of a `pub` enum, every trait impl on a public type, and the error type in every signature. Which two does this lesson's demonstration change, and why more easily than a renamed function?

<details markdown="1"><summary>Check</summary>

Struct fields and enum variants. Renaming or removing a function fails loudly, the moment a caller's code stops resolving; a new field or variant fails only where a caller wrote an exhaustive literal or `match`, code that compiled right up to the new release, exactly the break nobody notices while writing it.

</details>

2. ▢ Lesson 16 said adding a `From` impl to a public error type changes no function's name or argument, easy to add unnoticed, but real, since a caller can now depend on a foreign error type that used to be invisible. What do this lesson's quiet breaks share with that?

<details markdown="1"><summary>Check</summary>

None touch a function's name or argument list, what a diff makes obvious at a glance. Each adds something inside an existing shape, a field, a variant, a method, an impl, that a caller's already-compiling code can depend on not being there.

</details>

## Know this

### 1. The version contract, checked against the source

A crate's version is three numbers. The primary source calls a change "major" if it can force a major bump and "minor" if it only ever needs a minor one, leaving patch at "only apply bug fixes in patch releases," so every lint below answers major or minor, never patch. Below `1.0.0` the two left-hand positions swap roles (curly quotes flattened to straight ones, per this workspace's plain-ASCII rule):

"This guide uses the terms "major" and "minor" assuming this relates to a "1.0.0" release or later. Initial development releases starting with "0.y.z" can treat changes in "y" as a major release, and "z" as a minor release. [...] This is because Cargo uses the convention that only changes in the left-most non-zero component are considered incompatible."

A crate at `0.1.0` bumps to `0.2.0`, not `1.0.0`, for a change the tool calls major; the tool never makes that translation itself, leaving a maintainer below `1.0.0` to apply the rule by hand.

### 2. Two changes that look like patches

A small library at `0.1.0` exposes a struct callers build with a literal and an enum they match on:

```rust
pub struct Record {
    pub path: String,
    pub status: u16,
}

pub enum ParseError {
    Malformed,
    BadNumber,
}
```

`cargo-semver-checks` compares the working tree against a git commit, so committing this shape as the baseline comes first, then the change:

```text
git init -q && git add -A && git commit -qm baseline
# edit, then:
cargo semver-checks check-release --baseline-rev HEAD
```

The edit adds one field to `Record`, `pub bytes: u64`, and one variant to `ParseError`, `Empty`. Both read as additions, the word a minor release uses for itself, and both compile inside the crate without a warning. The tool disagrees (absolute paths trimmed from the two failure locations below, since a scratch directory belongs in nobody's report):

```text
Checked 196 checks: 194 pass, 2 fail, 0 warn, 58 skip

--- failure constructible_struct_adds_field: struct exhaustively constructible through public API adds field ---

Description:
A pub struct that could be exhaustively constructed with a literal using only public API has a new pub field, breaking existing exhaustive literals.

Failed in:
  field Record.bytes in src/lib.rs:4

--- failure enum_variant_added: enum variant added on exhaustive enum ---

Description:
A publicly-visible enum without #[non_exhaustive] has a new variant.

Failed in:
  variant ParseError:Empty in src/lib.rs:10

Summary semver requires new major version: 2 major and 0 minor checks failed
```

That run's counts matched exactly, nothing to correct. By section 1's rule, "new major version" on a `0.1.0` crate lands on the minor position: the honest next release is `0.2.0`, and calling it a patch would ship a break under a version number that promises none.

### 3. The same two changes, designed for them

Redesign both types first, using lesson 15's `#[non_exhaustive]` and lesson 18's constructor pattern together:

```rust
#[non_exhaustive]
pub struct Record {
    pub path: String,
    pub status: u16,
}

impl Record {
    pub fn new(path: String, status: u16) -> Self {
        Record { path, status }
    }
}

#[non_exhaustive]
pub enum ParseError {
    Malformed,
    BadNumber,
}
```

Commit that as the new baseline, then add the identical field and variant, defaulting the new field inside `new` so the constructor's signature does not change:

```rust
#[non_exhaustive]
pub struct Record {
    pub path: String,
    pub status: u16,
    pub bytes: u64,
}
```

```rust
impl Record {
    pub fn new(path: String, status: u16) -> Self {
        Record { path, status, bytes: 0 }
    }
}
```

```rust
#[non_exhaustive]
pub enum ParseError {
    Malformed,
    BadNumber,
    Empty,
}
```

Running the same check against the same edit:

```text
Checked 196 checks: 196 pass, 58 skip
Summary no semver update required
```

Nothing about the edit changed, only what the types were prepared for. This is lesson 15's `#[non_exhaustive]` paying off three stages later, exactly as it said it would when it deferred whether the trade is worth making: a constructor meant nobody outside the crate wrote `Record { .. }` as a literal, and `#[non_exhaustive]` meant nobody wrote an exhaustive `match` on `ParseError`, so neither addition had anything left to break.

### 4. The catalogue of quiet breaks

Seven shapes break a caller while looking like nothing happened. The first two are sections 2 and 3: a new field on a literal-constructed struct and a new variant on a non-`#[non_exhaustive]` enum, caught by `constructible_struct_adds_field` and `enum_variant_added`. A third, caught the same way, is a trait method added with no default body:

```rust
pub trait Greeter {
    fn greet(&self) -> String;
    fn farewell(&self) -> String;
}
```

```text
Checked 196 checks: 195 pass, 1 fail, 0 warn, 58 skip

--- failure trait_method_added: pub trait method added ---

Description:
A non-sealed public trait added a new method without a default implementation, which breaks downstream implementations of the trait

Failed in:
  trait method traitdemo::Greeter::farewell in file src/lib.rs:3

Summary semver requires new major version: 1 major and 0 minor checks failed
```

A fourth, also tool-caught, is a field that silently drops an auto trait. `Handle` used to be `Send` and `Sync`:

```rust
pub struct Handle {
    id: u64,
    cache: std::rc::Rc<()>,
}
```

```text
Checked 196 checks: 195 pass, 1 fail, 0 warn, 58 skip

--- failure auto_trait_impl_removed: auto trait no longer implemented ---

Description:
A public type has stopped implementing one or more auto traits. This can break downstream code that depends on the traits being implemented.

Failed in:
  type Handle is no longer Send, in src/lib.rs:3
  type Handle is no longer Sync, in src/lib.rs:3

Summary semver requires new major version: 1 major and 0 minor checks failed
```

The last two need a second crate, since the tool inspects one crate's own surface and has no lint for either. A blanket impl, `impl<T: Display> Describe for T` where callers used to implement `Describe` by hand, reports `196 checks: 196 pass`, yet a dependant holding `impl Describe for Local` where `Local: Display` fails with `error[E0119]`, conflicting implementations of trait `Describe` for type `Local`. Narrowing behaves the same way: `pub fn greet(name: impl Into<String>)` narrowed to `pub fn greet(name: String)` also reports clean, and a dependant calling `greet("ferris")` fails with `error[E0308]: mismatched types`, expected `String`, found `&str`. The seventh is variance, verified in full by lesson 0055: shortening a lifetime through an invariant `Slot<'a>(Cell<&'a str>)` fails where the same shortening through a covariant `Reader<'a>(&'a str)` succeeds, and neither signature names variance anywhere.

Four of these seven were verified directly here, two with the tool (trait method, auto trait loss) and two by compiling a dependant (blanket impl, narrowed parameter); the struct field and enum variant were the tool-verified pair from sections 2 and 3, and variance is lesson 0055's own fact, cited rather than repeated.

### 5. What the tool cannot see

A function whose signature never changes can still stop honouring what it used to promise. Take a parser that used to tolerate a bad number:

```rust
pub fn parse_status(code: &str) -> u16 {
    code.parse().unwrap_or(0)
}
```

Replacing `unwrap_or(0)` with `unwrap()` changes no name, argument or return type, and the tool agrees:

```text
Checked 196 checks: 196 pass, 58 skip
Summary no semver update required
```

Calling it on bad input now panics, `called `Result::unwrap()` on an `Err` value: ParseIntError { kind: InvalidDigit }`, where it used to return `0`; nothing in the signature said it would never panic. The same blindness covers an invariant quietly weakened or a promise living only in a doc comment: the tool checks the shape a signature exposes, not the behaviour behind it, and has never read your documentation. Tests catch behaviour a signature cannot express; the tool catches a shape tests might never exercise. Neither replaces the other.

### 6. The habit worth forming

The check belongs in continuous integration, run against the last published release, before a change ships rather than after somebody reports it broken. Day to day, `--baseline-rev` against a git commit needs only the repository already in hand, what every report above used. In CI the comparison that matters is against what callers already depend on, the published crate, needing `--baseline-version` instead: network access and the crate already existing, a cost worth paying once in a job that runs before release rather than never. A crate with no such job learns it broke a caller from the caller, the more expensive way to find out.

## Practice

1. ▢ A change on a crate at `0.1.0` reports `semver requires new major version`. Using section 1's rule, name the actual next version, and what it would be at `1.4.2` instead.

<details markdown="1"><summary>Check</summary>

`0.2.0`: below `1.0.0` the major position stays `0`, so the change lands on the minor position instead. At `1.4.2` the same verdict is a true major bump, to `2.0.0`.

</details>

2. ▢ A `#[non_exhaustive]` struct has two `pub` fields and a derived `Default`. Predict whether `Config { retries: 3, ..Default::default() }` compiles from another crate, then try it.

<details markdown="1"><summary>Hint</summary>

`#[non_exhaustive]` blocks struct-expression syntax itself from outside the crate, not just the fields it lets you skip.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `E0639`, cannot create non-exhaustive struct using struct expression. Public fields are irrelevant: the attribute blocks the literal form entirely from outside its crate, functional update included, which is why section 3's redesign needed a constructor rather than just `pub` fields.

</details>

3. ▢ The same trait from section 4 instead gains `fn farewell(&self) -> String { String::from("bye") }`, a default body rather than none. Predict whether `cargo-semver-checks` reports this the same way, then run both and compare.

<details markdown="1"><summary>Check</summary>

No: it reports `196 checks: 196 pass`, unlike the no-default version's single failure. The reference page still calls a defaulted addition "possibly-breaking" rather than safe, since it can collide with a method a caller's type already had; the tool does not flag that narrower risk, worth knowing before trusting a clean report as the final word.

</details>

4. ▢ A library adds `impl<T: std::fmt::Display> Describe for T`, and the tool reports it clean. Predict what happens to a dependant already holding `impl Describe for Local` where `Local` also implements `Display`, then say why the report missed it.

<details markdown="1"><summary>Hint</summary>

The tool inspects one crate's API surface; a coherence conflict only exists once a second crate's own `impl` is in the picture.

</details>

<details markdown="1"><summary>Check</summary>

The dependant fails to build with `E0119`, conflicting implementations of `Describe` for `Local`. The library's report missed it because nothing about its own surface became inconsistent; the conflict exists only once a second crate's `impl` collides with the new one, outside a single-crate check's view.

</details>

5. ▢ `pub fn greet(name: impl Into<String>) -> String` becomes `pub fn greet(name: String) -> String`. Predict the library's report, then what happens to a dependant calling `greet("ferris")`.

<details markdown="1"><summary>Check</summary>

The library reports clean, `196 checks: 196 pass`: the tool has no lint for narrowing a parameter's type. The dependant fails with `E0308`, mismatched types, expected `String`, found `&str`, since the wider `Into<String>` bound accepted a string literal directly and the narrower one no longer does.

</details>

## Real-world reps

- [ ] Run `cargo semver-checks check-release --baseline-rev` against your project's first commit shipping a public item, then make one change from this lesson's catalogue and read what the tool calls it before you would have guessed.
- [ ] Walk every `pub` struct and enum your project exposes and decide whether each should be `#[non_exhaustive]` with a constructor or fixed forever; where you choose fixed, say in a comment why nothing will ever need adding.
- [ ] Tomorrow: add `cargo semver-checks check-release --baseline-version` to whatever runs before your project counts as ready to publish, then run `cargo publish --dry-run` and confirm it packages cleanly, without publishing anything.

## Going further

- [Semantic Versioning 2.0.0](https://semver.org/): the general specification Cargo's pre-`1.0.0` convention departs from
- [cargo_semver_checks](https://docs.rs/cargo-semver-checks/0.50.0/cargo_semver_checks/): the tool behind every report here, at the release verified
- [The non_exhaustive attribute](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute): the attribute section 3's redesign relies on
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
