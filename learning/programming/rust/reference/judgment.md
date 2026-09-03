---
title: Judgment
description: The stage 8 reference sheet: what a public API commits to, what breaks a caller, the release procedure, and where to look when nothing is written down
type: reference
---

# Judgment

Lookup sheet for stage 8. The question it exists to answer: **does this change need a major version, and where do you look when the documentation does not say?**

## Variance: what makes a lifetime parameter covariant, invariant or contravariant

A type's variance over a lifetime parameter answers one question: given `'long: 'short`, does `Type<'long>` convert to `Type<'short>`, the reverse, or neither. It is computed from the fields, not declared: if every field agrees, the struct gets that answer; if any two disagree, or one field is itself invariant, the whole struct is invariant, since invariance in one place can never be taken back elsewhere.

| Shape | Variance | Why |
|---|---|---|
| `&'a T`, or a struct holding only plain `&'a T` fields | Covariant | reading through a shorter-lived borrow is harmless, so a longer-lived borrow satisfies everything a shorter one would |
| A function parameter of type `&'a T`, or `PhantomData<fn(T)>` | Contravariant | a function that accepts any short-lived borrow already accepts every longer-lived one, so the substitution runs the other way |
| `&'a mut T`, in `T` | Invariant | a caller could otherwise write a shorter-lived value into a slot the compiler believes lives longer, then read it back once that value is gone |
| `Cell<&'a T>`, `RefCell<&'a T>`, `Mutex`, `RwLock`, or any interior-mutability wrapper, anywhere in the type | Invariant | the same hazard as `&mut`, since interior mutability grants a write path through what looks like a shared reference |
| `PhantomData<*mut T>` | Invariant | a raw pointer carries none of the compiler's aliasing guarantees, regardless of what `T` would otherwise allow |
| `PhantomData<T>` | Whatever `T` itself is | declares an owned `T` for variance purposes, as though the field were really there |
| `PhantomData<&'a T>` | Covariant | declares a borrow, exactly as a real `&'a T` field would |
| A struct mixing covariant and invariant fields | Invariant overall | one field asking for the strictest answer decides the whole type |

The compiler names this for you once a type is your own: `` = note: the struct `Name<'a>` is invariant over the parameter `'a` ``, with a help line pointing at the Nomicon's subtyping chapter. A type's variance is part of its public contract exactly as its signatures are: adding a `Cell` to a private field for an internal cache flips a type from covariant to invariant with no change to any public signature, and a caller's code simply stops compiling with that same note, far from the change that caused it.

## Where `for<'a>` is required rather than optional

| Situation | Sugar covers it? |
|---|---|
| A bound with one borrowed parameter and no borrowed return, `Fn(&str) -> usize` | Yes, every elided-lifetime closure bound already carries an implicit `for<'a>` |
| A bound whose return also borrows from the argument, `Fn(&'a str, &'a str) -> &'a str` | No: there is no elided form for "the same lifetime, for every lifetime"; write `for<'a>` by hand |
| A function that must hand the closure a borrow it created itself, after the caller's own lifetime was already fixed | No: a single named lifetime is fixed before the body runs and cannot reach back to cover a value born later; only a bound satisfied afresh at every call, `for<'a>`, works |
| A trait you define whose method takes its own lifetime-parameterised borrow, used the same way | No, for the same reason; write it on the bound or as a supertrait |
| Quantifying over a type parameter instead of a lifetime, `for<T>` | Not available on stable (`E0658`); move the type parameter onto the method instead, as an ordinary generic |

The diagnostic to recognise either way is `` implementation of `Fn` is not general enough ``, or, comparing two named function types directly, `` one type is more general than the other ``: both mean a bound asked for every lifetime and got a closure or function pinned to one specific lifetime instead.

## The breaking-change table

The change, whether `cargo-semver-checks` 0.50.0 catches it, and what to do instead.

| Change | Tool catches it | What to do instead |
|---|---|---|
| New field on a plain `pub` struct buildable with a literal | Yes, `constructible_struct_adds_field` | `#[non_exhaustive]` plus a constructor, from the first release |
| New variant on a plain `pub` enum | Yes, `enum_variant_added` | `#[non_exhaustive]` on the enum, from the first release |
| New field on a struct-like variant, when only the enum carries `#[non_exhaustive]` | Yes, `enum_struct_variant_field_added` | mark the struct-like variant `#[non_exhaustive]` too; the enum-level attribute protects only the set of variants, not the fields inside one that is itself struct-like |
| A non-sealed public trait gains a method with no default body | Yes, `trait_method_added` | give it a default body, or seal the trait first so no external `impl` exists to break |
| A field quietly drops an auto trait such as `Send` or `Sync` | Yes, `auto_trait_impl_removed` | keep every field's own type `Send`/`Sync`, or treat the loss as deliberate and take the major version |
| A blanket `impl` added where a dependant already implemented the trait by hand | No; the conflict is `E0119` in the dependant, outside a single crate's own surface | check for a plausible downstream `impl` before adding a blanket one; the tool has nothing to say here |
| Narrowing an accepted type, `impl Into<String>` to `String` | No | keep the wider bound once shipped; narrowing is the breaking direction even on a clean report |
| A function's behaviour changes with no signature change, such as `unwrap_or(0)` becoming `unwrap()` | No | tests catch behaviour a signature cannot express; document panics so the promise is written down somewhere |
| Adding `#[non_exhaustive]` to a type that shipped without it | Yes, cargo's own semver reference names this a breaking addition | ship it with the type's first release; adding it later revokes literals and matches a caller already relied on |
| A private field changes a public lifetime parameter's variance, for example adding a `Cell` for a cache | No dedicated lint; surfaces as an ordinary compile failure in the dependant | decide covariance or invariance at first release, and treat later interior mutability as a variance-changing, hence breaking, decision |

Four of the shapes above need only the tool against one crate; the blanket-impl and narrowed-parameter rows need a second, dependent crate compiled against the change, since a coherence conflict or a tightened bound is invisible from inside the crate that made it.

## The future-proofing tools, and what each costs a caller

| Tool | What it buys | What it costs today |
|---|---|---|
| `#[non_exhaustive]` on a struct or enum (and on a struct-like variant, separately) | A future field or variant costs no major version | the literal constructor is gone entirely (`E0639`) from outside the crate, functional update included, and an exhaustive `match` needs a wildcard arm it may never use |
| A private field behind a constructor | The field can be validated, renamed or defaulted later with no caller-visible change | the literal and any functional-update shorthand are gone; every caller goes through the constructor |
| A sealed trait (a private supertrait no other crate can name) | A method can be added in a minor release, since no external `impl` exists to break | only types the crate itself provides may ever implement it |
| A newtype around a foreign or unsettled type | The wrapped type can change later, or the crate can start owning a foreign trait's `impl`, with nothing a caller wrote depending on it | every method the inner type had is gone unless forwarded on purpose |
| `#[doc(hidden)]` | Hides an item from generated documentation | nothing else: the item is exactly as callable and exactly as public as before; a workaround for a macro's own generated items, not a substitute for deciding something should be private |

None of these are free in general; each is worth its cost only where a real dependant would be hurt without it; a type with nothing left to protect, such as two public `f64` fields and no invariant, is more useful left plain.

## Features: the additive rule and unification

A feature must only add. Cargo's own reference states it plainly: enabling a feature should never disable functionality, and it should usually be safe to enable any combination of features at once.

| Fact | Consequence |
|---|---|
| Features are unique to the package that defines them | enabling one on your own crate does not enable a same-named feature anywhere else |
| Cargo builds one copy of a shared dependency per build, unioning every feature any package in that build asked for | a package that never touched a feature can still receive its effects, if another package sharing the same dependency asked for it |
| `optional = true` on a dependency defines an implicit feature of the same name | writing `dep:name` inside another feature's list turns that implicit name off, available since Rust 1.60 |
| `#[cfg(feature = "...")]` on a `pub` item removes it from the build entirely when the feature is off | calling it without the feature is a compile error, `E0425`, "configured out", never a runtime surprise |
| `rust-version` in `[package]` is enforced, not merely advisory | the wrong toolchain fails outright with a named requirement; placed after `[dependencies]` by mistake, cargo instead searches crates.io for a package called `rust-version` and reports it missing |

What a feature cannot fix: a signature or an error type that should differ between callers. Every feature in one build is on or off for everyone sharing that dependency, and unification means "everyone" is not a set any one caller controls; the honest alternatives are a major version, a new type, or a function under a new name.

## The release procedure, ending in a dry run

1. The test suite passes.
2. `cargo semver-checks check-release` runs clean against the version actually on the registry (`--baseline-version` in continuous integration; `--baseline-rev HEAD` against a git commit day to day).
3. `cargo doc` builds with no broken intra-doc-link warnings.
4. `cargo package --list` is read by eyes at least once, since a narrowed `include` can look plausible and still be missing a file `cargo package` itself would catch by compiling the packaged copy.
5. The manifest carries `description` and `license` or `license-file`, both required in practice by crates.io, plus `repository`, `documentation` and `readme` where they exist.
6. In a workspace, a library is published before any sibling that path-depends on it; a dependant's own dry run fails first with "failed to prepare local package for uploading" if the registry has never seen the library it needs restated as a registry dependency.
7. The version number follows the change actually being shipped: below `1.0.0` a change the tool calls major lands on the minor position instead; at or above `1.0.0` it is a true major bump; reaching `1.0.0` itself is a judgement that the API is settled, never a count of `#[non_exhaustive]` attributes added.
8. `cargo publish --dry-run` packages, verifies by compiling the packaged copy, and ends with "warning: aborting upload due to dry run".
9. Only after all of the above, publish for real, which is one command this arc's reps never run.

A published version is never modified once uploaded; a mistake is yanked instead (`cargo yank --version`), which blocks any new dependency on that version while every lock file already naming it keeps working. A yank deletes no code.

## API Guidelines items worth citing by identifier

Citing an identifier names a sentence someone else already argued through in public, rather than a feeling. None of these are enforced by any tool.

| Identifier | What it says | Why it earns a citation |
|---|---|---|
| `C-CONV` | `as_`, `to_` and `into_` prefixes carry a cost and an ownership shape | fixes an argument about naming with a table instead of taste |
| `C-GETTER` | the `get_` prefix is not used for a getter, barring a single obvious thing to fetch | the exception is narrow and named, not "whatever is already common in the file" |
| `C-ITER` | a collection's `iter`, `iter_mut` and `into_iter` follow one fixed shape | lets a caller reach for an ownership mode by a name already known from `Vec` |
| `C-CASE` | acronyms count as one word inside `UpperCamelCase` (`Uuid`, not `UUID`) | a convention, not a soundness question; costs only a reader's eye |
| `C-COMMON-TRAITS` | a crate defining a new type should eagerly implement `Copy`, `Clone`, `Eq`, `PartialEq`, `Ord`, `PartialOrd`, `Hash`, `Debug`, `Display`, `Default` | the orphan rule means a missing one can never be patched in from outside |
| `C-CONV-TRAITS` | never implement `Into` or `TryInto` directly; implement `From` or `TryFrom` instead | the blanket impl already gives you the other direction for free |
| `C-GENERIC` | fewer assumptions on an input make a function more widely usable | cuts both ways: every extra generic parameter is more surface for the breaking-change table above |
| `C-STRUCT-PRIVATE` | making a field public pins a representation and gives up all validation | the argument for a constructor over a public field, stated as a cost rather than a taste |
| `C-GOOD-ERR` | an error type should be `Send` and `Sync` | catches a type that compiles fine until somebody returns it from a spawned thread |
| `C-FAILURE` | function docs state error, panic and safety considerations | the checklist's own name for writing down what lesson 0057 shows the tool cannot see |

`#[must_use]` is not on this checklist at all; it is sourced from the Reference's own attribute documentation instead, and belongs on anything whose only job is producing a value the caller is expected to act on.

## The order of authority when sources disagree

Stated once, in rank order, highest first.

| Rank | Source | Loses to the one above because |
|---|---|---|
| 1 | A run on your own toolchain | every document below describes some toolchain; only your own compiler says what yours does with what you just wrote |
| 2 | The item's own source and its release notes | a rendered stability badge is generated from the same attributes you can open directly, so it can only be a rendering of them, never a second fact beside them |
| 3 | The Reference | maintained continuously and corrected when wrong, unlike a blog post that announces a release once and simplifies on purpose |
| 4 | A tracking issue | keeps recording what an implementation became through every amendment after a design was agreed, so it is a stale RFC's own conversation still being updated |
| 5 | An RFC | a design record of alternatives and objections at the moment of a decision, not a description of current behaviour |

## The review order

Seven levels, hardest to undo first; the argument is reversibility, not severity.

| Order | Level | What to check |
|---|---|---|
| 1 | The public API's commitments | does this need to be `pub` at all; for a struct or enum, what happens the day it needs one more field or variant, including a field added inside a struct-like variant |
| 2 | What the types make impossible | could a caller already construct or exhaustively match today's shape |
| 3 | Error and panic behaviour | does it panic on caller-supplied input when a `Result` was available, and does the documentation say so |
| 4 | Sharing and concurrency | which sharing strategy picked this `Mutex`, atomic or channel, and does the code still answer the question that chose it |
| 5 | `unsafe` | the five questions a boundary must answer; failing any of the first four skips the fifth |
| 6 | A performance claim | is there a ratio, a stated workload and the safe version kept for comparison, or only an assertion |
| 7 | Naming and style | would a formatter or a five-second rename have settled this without a comment |

What separates a comment worth making from one that only looks like feedback is what it costs to ignore, not its politeness: a missing `#[non_exhaustive]` on a struct-like variant costs a major version if ignored; an unmeasured "this clone will be slow" costs nothing to ignore and states an opinion the arc's own measurement discipline already rules out.

## What this arc deliberately never taught, and where to go next

Not taught anywhere in this arc: embedded targets and `no_std`, foreign function interfaces, macros beyond deriving, or any particular framework. Where a specific gap needs filling, the Cargo Book's future-proofing and semver pages, the API Guidelines themselves, and the Rust RFC book are the sources this stage read from directly rather than summarised in full; go to them once a question is narrower than this sheet, and to the [Resources](../RESOURCES.md) page for everything general the arc pointed at along the way.
