---
title: 61. The API Guidelines
description: The checklist the ecosystem already agreed on, which items matter most, and how to use it without cargo-culting it
type: lesson
---

# Lesson 61. The API Guidelines

**Mission link:** "Doesn't feel idiomatic" gives a reviewer nothing to act on; citing C-CONV or C-COMMON-TRAITS points at a sentence both sides can read, and knowing which few items catch real problems is what turns a long list into judgment instead of ritual.
**Primary source:** [Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html)
**Prerequisites:** [Lesson 58](0058-designing-for-change.md), [Lesson 21](0021-traits-as-shared-behaviour.md)

## Warm-up

1. ▢ Lesson 58 used `#[non_exhaustive]` plus a constructor to make a new struct field or enum variant free where `cargo-semver-checks` had called the plain version a major break. What did that change about how a caller builds the value, rather than about the type's attributes?

<details markdown="1"><summary>Check</summary>

It moved construction behind the constructor: `#[non_exhaustive]` stops an external crate writing a literal at all, so the function you control is the only path left, and it can absorb the new field or variant without any existing call site changing shape.

</details>

2. ▢ Lesson 21 distinguished a trait from an inherent method by what it promises a caller who never sees your type's definition. In one sentence, what was that promise?

<details markdown="1"><summary>Check</summary>

Behaviour under a name the caller already knows, so code written against the trait works for any type that implements it, including ones that did not exist when the caller was written.

</details>

## Know this

### 1. A checklist, not a specification

The guidelines are explicit about their own authority: "These are only guidelines, some more firm than others." and "Rust crate authors should consider them as a set of important considerations in the development of idiomatic and interoperable Rust libraries, to use as they see fit." The same page adds that they "should not in any way be considered a mandate that crate authors must follow". Nothing enforces a single item: no compiler lint, no `cargo publish` step, nothing `cargo-semver-checks` reports on. What they buy instead is vocabulary. The checklist groups its items under headings such as Naming, Interoperability and Flexibility, and gives each a short identifier: `C-CONV` for conversion-method naming, `C-COMMON-TRAITS` for the traits in section 3 below. Citing `C-CONV` in review names one specific sentence somebody else already argued through in public, rather than a feeling.

### 2. The naming rules that actually cause arguments

Four naming items generate more review back-and-forth than the rest combined. `C-CONV` gives ad-hoc conversions a cost and an ownership shape by prefix, restated here from its own table:

```text
as_    Free       borrowed -> borrowed
to_    Expensive  borrowed -> borrowed / borrowed -> owned / owned -> owned (Copy)
into_  Variable   owned -> owned (non-Copy)
```

`C-GETTER` is shorter: "With a few exceptions, the `get_` prefix is not used for getters in Rust code." `C-ITER` fixes the method names a homogeneous collection exposes for its three ownership modes:

```rust
fn iter(&self) -> Iter             // Iter implements Iterator<Item = &U>
fn iter_mut(&mut self) -> IterMut  // IterMut implements Iterator<Item = &mut U>
fn into_iter(self) -> IntoIter     // IntoIter implements Iterator<Item = U>
```

And `C-CASE` settles acronyms inside `UpperCamelCase`: "acronyms and contractions of compound words count as one word: use `Uuid` rather than `UUID`, `Usize` rather than `USize` or `Stdin` rather than `StdIn`." One small crate follows all four at once and compiles cleanly under rustc 1.98.0:

```rust
pub struct HttpUrl(String);

impl HttpUrl {
    pub fn as_str(&self) -> &str { &self.0 }                          // as_: free, borrowed -> borrowed
    pub fn to_ascii_lowercase(&self) -> String { self.0.to_ascii_lowercase() } // to_: allocates
    pub fn into_string(self) -> String { self.0 }                     // into_: owned -> owned, consumes self
    pub fn host(&self) -> &str { self.0.split("//").nth(1).unwrap_or(&self.0) } // getter, no get_
}

pub struct UrlList(Vec<HttpUrl>);

impl UrlList {
    pub fn iter(&self) -> std::slice::Iter<'_, HttpUrl> { self.0.iter() }
    pub fn iter_mut(&mut self) -> std::slice::IterMut<'_, HttpUrl> { self.0.iter_mut() }
}

impl IntoIterator for UrlList {
    type Item = HttpUrl;
    type IntoIter = std::vec::IntoIter<HttpUrl>;
    fn into_iter(self) -> Self::IntoIter { self.0.into_iter() }
}
```

`HttpUrl`, not `HttpURL`, tells a reader the crate treats acronyms as ordinary words throughout. `as_str` promises the call is free and the caller keeps its own borrow; `to_ascii_lowercase` promises real work and a fresh allocation; `into_string` promises the same bytes handed over, `self` gone. `host` without a `get_` prefix reads as a property of the value, not a request to fetch one. `UrlList::iter`, `iter_mut` and the `IntoIterator` impl let a caller reach for exactly the ownership mode it needs by a name it already knows from `Vec`.

### 3. The traits worth implementing eagerly

`C-COMMON-TRAITS` grounds its advice in the orphan rule already in the glossary: "Rust's trait system does not allow orphans: roughly, every impl must live either in the crate that defines the trait or the implementing type. Consequently, crates that define new types should eagerly implement all applicable, common traits." Its list is `Copy`, `Clone`, `Eq`, `PartialEq`, `Ord`, `PartialOrd`, `Hash`, `Debug`, `Display`, `Default`. A small enum earns the set and shows which promises are cheap and which are not:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
pub enum Severity {
    #[default]
    Info,
    Warning,
    Error,
}

impl std::fmt::Display for Severity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self { Severity::Info => "info", Severity::Warning => "warning", Severity::Error => "error" })
    }
}

impl std::str::FromStr for Severity {
    type Err = ParseSeverityError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "info" => Ok(Severity::Info),
            "warning" => Ok(Severity::Warning),
            "error" => Ok(Severity::Error),
            other => Err(ParseSeverityError(other.to_owned())),
        }
    }
}

impl From<Severity> for u8 {
    fn from(s: Severity) -> u8 { match s { Severity::Info => 0, Severity::Warning => 1, Severity::Error => 2 } }
}
```

`Debug`, `Clone`, `Hash` and the equality traits are cheap here: derived from field structure, they commit to nothing beyond "prints, copies and compares like data", verified by the derive compiling at all. `PartialOrd` and `Ord` are a real commitment, since deriving them uses declaration order, and that order has to mean something: `Severity::Info < Severity::Warning` holds because the variants were written low to high on purpose. `Display` and `FromStr` are the pair stage 3 already built, and together they commit the crate to a stable text form: parsing and printing must agree, or the round trip lies. The final `impl` follows `C-CONV-TRAITS`, blunt about the other direction: "The following conversion traits should never be implemented: `Into`, `TryInto`. These traits have a blanket impl based on `From` and `TryFrom`. Implement those instead." `From<Severity> for u8` gets `Into<u8>` for free everywhere; the reverse `impl` would compile but give nothing back.

### 4. `#[must_use]`, the annotation nobody adds

The Reference states its purpose in one line: "The `must_use` attribute marks a value that should be used." It may be placed on a struct, enum, union, function or trait, and on a function it fires even when the return type is `()`:

```rust
#[must_use]
fn announce() { println!("hi"); }

fn main() { announce(); }
```

```text
warning: unused return value of `announce` that must be used
 --> examples/must_use_unit.rs:4:13
  |
4 | fn main() { announce(); }
  |             ^^^^^^^^^^
  |
  = note: `#[warn(unused_must_use)]` (part of `#[warn(unused)]`) on by default
```

The same attribute on a type catches every constructor that returns it, which is exactly the shape of a builder nobody finishes:

```rust
#[must_use]
#[derive(Debug, Default)]
pub struct SummaryBuilder { minimum: Severity }
```

```text
warning: unused `SummaryBuilder` that must be used
 --> examples/ignore_must_use.rs:5:5
  |
5 |     SummaryBuilder::default();
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^
```

Neither warning stops a build; both catch a mistake an ordinary struct never would. It belongs on anything whose only job is producing a value the caller is expected to act on: a validator returning `bool`, a builder returning `Self`, a guard whose drop matters.

### 5. Where the checklist argues with itself

Three items are contentious enough to hold the trade, not a verdict. Returning `impl Iterator<Item = Severity>` instead of a named concrete type hides exactly what it sounds like:

```rust
pub fn severities() -> impl Iterator<Item = Severity> {
    [Severity::Info, Severity::Warning, Severity::Error].into_iter()
}
```

The array's `IntoIter` is a `DoubleEndedIterator`, but a caller cannot use that fact:

```text
error[E0599]: no method named `next_back` found for opaque type `impl Iterator<Item = Severity>` in the current scope
```

That is lesson 0057's trade from the other side: an opaque return type lets the crate change the concrete iterator later, because callers were never allowed to depend on more than `Iterator`. Accepting `impl Into<String>` instead of a concrete `String` is the mirror image, on the input side:

```rust
fn set_name_generic(name: impl Into<String>) -> String { name.into() }
fn set_name_concrete(name: String) -> String { name }
```

A caller passing an owned `String` compiles against either; one passing `"c"` only compiles against the generic one, so tightening a shipped `impl Into<String>` down to `String` is the breaking direction:

```text
error[E0308]: mismatched types
6 |     let c = set_name_concrete("c");
  |             ----------------- ^^^ expected `String`, found `&str`
```

The general form is `C-GENERIC`: "The fewer assumptions a function makes about its inputs, the more widely usable it becomes," preferring `fn foo<I: IntoIterator<Item = i64>>(iter: I)` over a concrete `&[i64]`. Lesson 21 already named why this cuts both ways: a trait bound binds the caller as much as the body, and each generic parameter is more surface for lesson 0057's breaking-change catalogue, not less.

### 6. Using the list without reciting it

Two items catch more real damage than the rest of the naming section combined: `C-GOOD-ERR`'s `Send` and `Sync` requirement, since a failing error type quietly compiles until somebody returns it from a spawned thread, and `C-COMMON-TRAITS` itself, since the orphan rule means a missing `Debug` cannot be patched in from outside the owning crate. Beside those, `C-CASE`'s acronym rule and `C-WORD-ORDER` are conventions in the plainer sense: nothing breaks if a crate writes `HTTPUrl`, and the cost is only a reader's eye skipping less smoothly across a boundary. The checklist gives no signal for which kind an item is beyond its own prose, and citing one without being able to say, in your own words, what goes wrong if it is ignored is the cargo-culting the list otherwise prevents.

## Practice

1. ▢ A type implements `Display`, and somebody separately adds an inherent `fn to_string(&self) -> String` with different text. Predict whether this compiles, and which text `value.to_string()` prints.

<details markdown="1"><summary>Check</summary>

It compiles cleanly: an inherent method shadows a blanket trait method of the same name, so `value.to_string()` calls the inherent one, not `Display`'s. `C-CONV`'s promise for a `to_` method is cost and ownership, not which implementation wins, which is why `to_string` should only ever be reached through `Display`.

</details>

2. ▢ `HttpUrl::host` is written as `get_host` instead. Using `C-GETTER`'s own wording, does that pass review?

<details markdown="1"><summary>Check</summary>

No: the exception is for "a single and obvious thing that could reasonably be gotten," with `Cell::get` as its example, and a URL's host is not the only thing anyone would want from it. The rule is about what the type conceptually offers, not how many getters exist so far.

</details>

3. ▢ `#[must_use] fn announce() { .. }` returns `()`. Predict whether calling it as a bare statement warns, then check by compiling it.

<details markdown="1"><summary>Hint</summary>

The Reference's fn-based rule names the function being called, not its return type.

</details>

<details markdown="1"><summary>Check</summary>

It warns: unused return value of `announce` that must be used. The fn-based check fires on any call to a `#[must_use]` function used as a statement regardless of return type.

</details>

4. ▢ A colleague "fixes" a must_use warning on `fn announce() -> u8` by writing `if true { announce() } else { 0 };` instead of `let _ = announce();`. Predict whether this compiles cleanly.

<details markdown="1"><summary>Check</summary>

It does, with no warning: the lint looks through a block to its trailing expression, but the `if` itself is not a call expression, so the fn-based check never applies, and the discard stays invisible in the diff. `let _ = announce();` says the same thing honestly instead.

</details>

5. ▢ A published `pub fn set_name(name: impl Into<String>)` changes to `pub fn set_name(name: String)`. Predict which existing callers this breaks: the ones passing an owned `String`, the ones passing a `&str` literal, or both.

<details markdown="1"><summary>Hint</summary>

Check which of the two signatures a bare `"c"` compiles against.

</details>

<details markdown="1"><summary>Check</summary>

Only the `&str` callers break, with the mismatched-types error shown above. Callers already passing an owned `String` are unaffected, since `String` satisfies both signatures; the generic parameter was only ever widening what the concrete one accepted.

</details>

## Real-world reps

- [ ] Walk your crate's public items against the checklist, one heading at a time, and for every item it misses write one line: fix it, or say why not, since both are a real answer.
- [ ] Pick the type a caller constructs most often and check it against `C-COMMON-TRAITS` by hand: implement or derive whichever of `Debug`, `Clone`, `Default`, `PartialEq`, the ordering traits, `Hash` and `Display` fits, and nothing that does not.
- [ ] Tomorrow: mark whichever function or builder is easiest to call and forget with `#[must_use]`, confirm the warning fires on a throwaway call, then run `cargo publish --dry-run` and treat a clean result as that surface being one command from someone else's dependency.

## Going further

- [Naming](https://rust-lang.github.io/api-guidelines/naming.html): the full `C-CONV`, `C-GETTER`, `C-ITER` and `C-CASE` rules with more standard-library examples than this lesson had room for
- [Interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html): the complete `C-COMMON-TRAITS` and `C-CONV-TRAITS` guidance, plus `C-GOOD-ERR`
- [Flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html): `C-GENERIC`, `C-CALLER-CONTROL` and the rest of the trade-offs behind this lesson's contentious section
- [The must_use attribute](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-must_use-attribute): the Reference's full rules for where the attribute is allowed and when the lint fires
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
