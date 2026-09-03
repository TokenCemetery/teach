---
title: 63. Reviewing Rust
description: What to look for in somebody else's Rust, in what order, and which comments are worth making
type: lesson
---

# Lesson 63. Reviewing Rust

**Mission link:** A reviewer who reads top to bottom spends an hour on a variable name before approving a function that cannot grow without breaking every dependant; the fix is an order, expensive first.
**Primary source:** [Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html)
**Prerequisites:** [Lesson 61](0061-the-api-guidelines.md), [Lesson 54](0054-defending-an-unsafe-boundary.md)

## Warm-up

1. ▢ A struct's public fields and an enum's missing `#[non_exhaustive]` once turned two ordinary edits into a major version each. What made the identical edits free instead?

<details markdown="1"><summary>Check</summary>

`#[non_exhaustive]` plus a constructor, so nothing outside the crate ever built one from a literal: neither addition then changes what an existing pattern or literal has to name.

</details>

2. ▢ Lesson 54's five questions for an `unsafe` block are asked in order, and failing one of the first four skips the fifth. Which question, if it fails, means no measurement can rescue the block?

<details markdown="1"><summary>Check</summary>

Question one: whether an invariant exists at all. With nothing to guarantee, the rest are moot, and a fast, well-measured block on no invariant is still unsound.

</details>

## Know this

### 1. The order, argued

Seven levels, hardest to undo first: the public API's commitments, then what the types make impossible, then error and panic behaviour, then sharing and concurrency, then `unsafe`, then a performance claim, then naming and style. The argument is reversibility, not severity. A public function's shape ships into every dependant's compiled output the moment they build against it; undoing it needs a major version, [Lesson 57](0057-what-breaks-a-caller.md)'s subject. What the types allow to be constructed is nearly as fixed, since a caller may already match today's shape. Error and panic behaviour is a contract too, but behavioural: a caller notices only once their input walks the changed path, so a wrong panic ships, is found, and is fixed as a bug rather than a break. Sharing and concurrency move the cost elsewhere: [Lesson 36](0036-choosing-a-sharing-strategy.md)'s lost update compiled and ran wrong without touching a signature, so nothing here is a semver question, only an uptime one, deferred rather than removed. `unsafe` is invisible outside the crate: [Lesson 54](0054-defending-an-unsafe-boundary.md)'s fix for a panic-shaped hole moved two lines and changed no signature, so review repairs it for free, proportional in cost only to how long it ran undetected. A performance claim binds nobody's code, so an unmeasured ratio is embarrassing, not breaking. Naming and style rank last: a private name or formatting choice was never a promise to anyone outside the file, why a reviewer reaches for them first out of habit and should last.

### 2. Public API and types

Two questions: does this need to be `pub` at all, when `pub(crate)` says the same to every caller that matters ([Lesson 18](0018-modules-and-visibility.md)); and, for a struct or enum, what happens the day it needs one more field or variant. This project's `Line` carried a struct-like variant without its own attribute:

```rust
#[non_exhaustive]
pub enum Line<'a> {
    Request { path: &'a str, status: u16, bytes: u64 },
    Note(&'a str),
    Blank,
}
```

Adding a field compiles inside the crate, but cargo-semver-checks, run against the unchanged version, disagreed:

```text
--- failure enum_struct_variant_field_added: pub enum struct variant field added ---

Description:
An enum's exhaustive struct variant has a new field, which has to be included when constructing or matching on this variant.

Failed in:
  field method of variant Line::Request in src/lib.rs:21

     Summary semver requires new major version: 1 major and 0 minor checks failed
```

The report is trimmed to the lines carrying the teaching; the path was absolute, cut above to the file and line. The enum's own `#[non_exhaustive]` only promises a caller cannot exhaustively match the *variants*, saying nothing about fields inside a struct-like one, so `Request` needed the attribute a second time, on itself. Moved onto the variant, the identical addition reports every check passing. The checklist explains why the plainer alternative, public fields with no attribute, costs more: "Making a field public is a strong commitment: it pins down a representation choice, and prevents the type from providing any validation or maintaining any invariants on the contents of the field, since clients can mutate it arbitrarily" (C-STRUCT-PRIVATE). `Summary` takes the other route, private fields behind a constructor and accessors.

### 3. Behaviour, sharing and unsafe

Three more questions, one per level, each pointing at the lesson that owns it. Errors and panics: does this function panic on input a caller supplied, when a `Result` was available ([Lesson 17](0017-panic-or-error.md)), and does the documentation say so, since the checklist expects "Function docs include error, panic, and safety considerations" (C-FAILURE) as an Errors or a Panics section. Sharing and concurrency: which of [Lesson 36](0036-choosing-a-sharing-strategy.md)'s five questions picked this `Mutex`, atomic or channel, and does the code still answer them, since a lost update or a deadlock passes a low-contention test and says nothing until it does not. `unsafe`: cite rather than repeat [Lesson 54](0054-defending-an-unsafe-boundary.md)'s five questions; failing any of the first four rejects the block before its measurement is read.

### 4. Performance, naming and noise

Performance: is there a ratio, a stated workload and the safe version kept for comparison, or only an assertion, per [Lesson 52](0052-measuring-before-optimising.md). Naming and style: would a formatter or a five-second rename have settled this without a comment. What separates a comment worth leaving from one that only looks like feedback is what it costs to ignore, not its politeness. Three, on this project's code. Worth making, since ignoring it ships a break: "This `Request` variant needs its own `#[non_exhaustive]`: the next field you add here is a major version, and a constructor plus the attribute makes it free, the way `Summary` already is." Worth making as a question, since the author may know something a reviewer does not: "`record` counts a status of 500 or above as a server error; is that a caller's actual definition of failure, or a placeholder?" Not worth making at all: "`path.to_owned()` in `record` allocates on every request line; a `Cow` would avoid it." That fails on its own terms: an unmeasured performance opinion is exactly what Lesson 52 rules out, indistinguishable from a style preference the formatter already settled.

### 5. What only the author knows

A reviewer sees the diff, not the invariant never written down, the caller the author already fielded a bug report from, or the measurement sitting in a terminal nobody screenshotted. Ask for these rather than assume their absence: what has to stay true here, who else already calls it, and what number, if any, justified the choice. Most Rust is never reviewed by a second person, which is where the arc's own habit pays off: [the project](../reference/the-project.md) keeps a copy per stage precisely so the diff between two versions of your own crate becomes the artefact a colleague would have produced. Reading the rendered public API, a documentation page rather than the source, is the other half: it shows exactly what a stranger sees, the only honest way to judge whether a signature explains itself.

### 6. Closing the arc

At lesson one, a moved value and a borrowed one looked the same. By here: predicting a borrow or lifetime error before the compiler reports it, modelling with enums, `Option` and `Result` instead of `unwrap`, designing an error type a caller can act on, choosing a sharing strategy from the data rather than habit, defending an `unsafe` boundary with an invariant and a measurement, and shaping a public API that can grow without breaking anyone using it. Not taught: embedded targets and `no_std`, foreign function interfaces, macros beyond deriving, or any particular framework.

## Practice

1. ▢ `Line::Request` gains a `method: &'a str` field while its own attribute is still missing. Predict what cargo-semver-checks reports against the unchanged version as baseline, then run it.

<details markdown="1"><summary>Hint</summary>

Ask whether the enum's `#[non_exhaustive]` reaches inside a struct-like variant, or only across the variants.

</details>

<details markdown="1"><summary>Check</summary>

A failing check, `enum_struct_variant_field_added`, and a required major version: the enum-level attribute only protects the set of variants, not the fields inside a struct-like one.

</details>

2. ▢ `Summary`'s `requests` field is private, read only through a method. Predict whether making it `pub` is breaking today, and what it forecloses tomorrow.

<details markdown="1"><summary>Check</summary>

Not breaking today: widening a field from private to public only adds capability. What it forecloses is C-STRUCT-PRIVATE's point: a public field can never again be validated, since any caller may now write to it directly.

</details>

3. ▢ A diff changes a public function's signature, renames a helper's local variables, and swaps a `Mutex` for an atomic inside it. Which do you read first, and can the rename ever outrank the `Mutex` change?

<details markdown="1"><summary>Check</summary>

The signature first, always: nothing outranks a level a dependant already compiled against. The `Mutex`-to-atomic swap is next, a runtime guarantee change though no signature moved. The rename outranks neither, since nothing outside the file depends on a local name.

</details>

4. ▢ Sort these into worth making, worth making as a question, and not worth making: "this clone is unnecessary and will be slow", "should this really panic on a timeout, or is that caller-recoverable", "prefer `iter().map()` over this `for` loop, it reads better".

<details markdown="1"><summary>Hint</summary>

Ask what each one costs to ignore, not how confidently it is phrased.

</details>

<details markdown="1"><summary>Check</summary>

The clone comment is not worth making: an unmeasured slowdown claim is exactly what Lesson 52 rules out. The panic question is worth making, as a question: the author may already know the caller has no recovery path. The loop comment is not worth making: a style preference a formatter or team convention already settles.

</details>

5. ▢ Two commits of your own project exist, one per stage, as [the project](../reference/the-project.md) recommends keeping. With nobody to review the later one, what do you read first, and why does it beat rereading the whole file?

<details markdown="1"><summary>Check</summary>

The diff, read for its effect on the public surface first: it shows what changed and what a dependant can see, this lesson's order applied to your own work, where rereading the whole file only re-exposes code you already believed correct.

</details>

## Real-world reps

- [ ] Apply this lesson's order to your own project's public API, level by level, writing down the first thing each level finds before fixing anything.
- [ ] Give your project one honest pass at stage 8: `#[non_exhaustive]` where it protects a real future change, a constructor beside every struct that needs one, a doc example on every public item, and a clean `cargo publish --dry-run`; do not run the real publish.
- [ ] Tomorrow: pick one piece of Rust you did not write, apply this lesson's order out loud, and write down the three most valuable comments, marking which is a question rather than an instruction.

## Going further

- [Future proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html): sealed traits and hidden newtypes, C-STRUCT-PRIVATE's chapter
- [Documentation](https://rust-lang.github.io/api-guidelines/documentation.html): what an Errors section and a Panics section are expected to say
- [SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html): cargo's catalogue of breaking changes, owned by Lesson 57
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
