---
title: 62. Reading the Source and the RFCs
description: Answering a question the documentation does not, from the standard library, the tracking issues and the RFCs
type: lesson
---

# Lesson 62. Reading the Source and the RFCs

**Mission link:** Sooner or later a reviewer meets a question the crate's own documentation does not answer, and the only way through is the same source and history the documentation was written from, read in an order that says which one to believe when two disagree.
**Primary source:** [The Rust RFC Book](https://rust-lang.github.io/rfcs/)
**Prerequisites:** [Lesson 19](0019-documentation-that-compiles.md), [Lesson 49](0049-checking-with-miri.md)

## Warm-up

1. ▢ Lesson 19 showed that a fenced block under `# Examples` is compiled and run by `cargo test`, not just read. Name one thing about a public item that a passing doctest can never tell you, however many times it runs.

<details markdown="1"><summary>Check</summary>

Which release added the item, or whether it still sits behind a feature gate. A doctest exercises behaviour; it says nothing about the item's own history, and history is what a `#[stable(since = ...)]` attribute or a tracking issue records instead.

</details>

2. ▢ Lesson 49 showed that when a stable run and a Miri run disagree, Miri wins, since it checks a property an ordinary run cannot. Given the arc's rule that a run wins over something written, name two kinds of written source this lesson still expects a run on your own toolchain to outrank.

<details markdown="1"><summary>Check</summary>

A stability badge, and an old blog post or RFC describing a feature as it stood before it shipped. Both describe some toolchain's behaviour at some past moment; only compiling the lines in front of you proves what your own compiler does today.

</details>

## Know this

### 1. The source link, and what three attributes tell you

Every page on `doc.rust-lang.org` carries a badge and a `Source` link beside each item, both generated from the same attributes sitting in the standard library's own source. `Option::unwrap`'s entry in [core/option.rs](https://doc.rust-lang.org/src/core/option.rs.html#1011) carries this stack above its signature:

```rust
#[inline(always)]
#[track_caller]
#[stable(feature = "rust1", since = "1.0.0")]
#[rustc_diagnostic_item = "option_unwrap"]
#[rustc_allow_const_fn_unstable(const_precise_live_drops)]
#[rustc_const_stable(feature = "const_option", since = "1.83.0")]
```

`#[stable(feature = "rust1", since = "1.0.0")]` is a guarantee: the item has behaved this way since Rust 1.0.0, and narrowing it is a breaking change, the same promise lesson 18 attached to anything made public. `#[inline(always)]` promises nothing: a hint to the optimiser, addable or removable between releases without a changelog entry, since it changes speed rather than behaviour. `#[track_caller]` changes visible behaviour, which line a panic blames, so it is worth reading before wrapping a function. Hunting for a badge that disagreed with its own source's `since`, to make the sharpest possible case for this lesson, turned up none: `unwrap`'s badge reads "1.0.0 (const: 1.83.0)", matching its two `since` attributes exactly, since the badge is drawn from nothing else. What no prose states is what `#[track_caller]` does to a wrapper:

```rust
fn first<T>(v: &[T]) -> &T {
    v.first().unwrap()
}

fn first_twice_removed<T>(v: &[T]) -> &T {
    first(v)
}

fn main() {
    let empty: Vec<i32> = Vec::new();
    first_twice_removed(&empty);
}
```

This panics at `src/main.rs:2:15`, inside `first`, however many more functions sit between it and `main`, because `first` itself carries no `#[track_caller]` and the location stops climbing right there; adding the attribute to `first` and rerunning moves the blame to wherever `first` is called instead. The source's own attribute, and five lines, answer what the documentation does not.

### 2. The order of authority when sources disagree

State the rule once: the source and the release notes outrank a rendered badge, the Reference outranks a blog post, a tracking issue outranks a stale RFC, and a run on your own toolchain outranks all four. Each has a reason. A badge is generated from the same attribute you can open directly, so it can only be a rendering of it, never a second fact beside it; when the two seem to differ, the rendering broke. A blog post announces a release once, for a wide audience, and simplifies on purpose; the [Rust Reference](https://doc.rust-lang.org/reference/) is maintained continuously and gets corrected when wrong, unlike an old post. A stale RFC records a design at the moment a team agreed to try it; a tracking issue keeps recording what the implementation became through every amendment after, so it is the RFC's own conversation still being updated. A run on your own toolchain beats every document above, since each describes some toolchain, and only your own compiler says what yours does with what you just wrote.

### 3. Tracking issues, and following a stabilisation trail

Whether an item is stable is one glance: read its badge, or grep the source for `#[stable(` against `#[unstable(`. [Stability attributes](https://rustc-dev-guide.rust-lang.org/stability.html) explains what sits behind that glance: an `#[unstable(feature = "foo", issue = "1234", ...)]` attribute requires a matching `#![feature(foo)]`, and the required `issue` field ties every unstable item to a numbered tracking issue. [`Mutex::clear_poison`](https://doc.rust-lang.org/std/sync/struct.Mutex.html#method.clear_poison) shows the whole trail. Its badge reads 1.77.0, and its [source](https://doc.rust-lang.org/src/std/sync/poison/mutex.rs.html#610-612) agrees:

```rust
#[inline]
#[stable(feature = "mutex_unpoison", since = "1.77.0")]
#[rustc_should_not_be_called_on_const_items]
pub fn clear_poison(&self) {
    self.poison.clear();
}
```

[Tracking Issue for mutex_unpoison](https://github.com/rust-lang/rust/issues/96469) records the feature reaching a disposition to merge, and [Stabilize mutex_unpoison feature](https://github.com/rust-lang/rust/pull/119804) is the pull request that closed it, merged with a milestone of 1.77.0, matching the badge. Here the release notes were not even silent: [Announcing Rust 1.77.0](https://blog.rust-lang.org/2024/03/21/Rust-1.77.0/) lists `Mutex::clear_poison` by name. But that post also hedges its own completeness, pointing to the "detailed release notes for 1.77.0" for the fuller list, an admission that its own highlights are a curated subset. A change can be real and stable without a line in the post announcing its release, which is why a merged pull request's milestone, not a paragraph's presence, settles whether something shipped.

### 4. The RFC book, for the question the Reference will not answer

An RFC is not a description of current behaviour; it is a design record of alternatives and objections raised when a decision was made, which is why it explains why the language refused something rather than what it currently does. Lesson 15 met `#[non_exhaustive]`; the Reference's [Type system](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute) chapter states its mechanics, including that within the defining crate it has no effect, confirmed by building the same literal both inside and outside its own crate:

```rust
#[non_exhaustive]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

pub fn make_point() -> Point {
    Point { x: 1, y: 2 }
}
```

That compiles inside its own crate. A dependent crate writing the identical literal gets `error[E0639]: cannot create non-exhaustive struct using struct expression`. What the Reference never says is why an attribute won over the alternatives, and [2008-non-exhaustive](https://rust-lang.github.io/rfcs/2008-non-exhaustive.html) is where that argument happened. Its Alternatives reads:

```text
- Provide a dedicated syntax instead of an attribute. This would likely be done by adding a `...` variant or field, as proposed by the original extensible enums RFC.
- Allow creating private enum variants and/or private fields for enum variants, giving a less-hacky way to create a hidden variant/field.
- Document the `#[doc(hidden)]` hack and make it more well-known.
```

Anyone who wondered why the standard library did not just keep using `#[doc(hidden)]` fields now has the answer: rejected as a hack worth replacing, not documenting. The Reference only records what shipped; the RFC is where the road not taken is written down at all.

### 5. When to stop reading and run something instead

The arc's habit throughout has been that a short program settles a question faster than a document trail, and this lesson names that habit. A recurring one: does a closure implement `Copy`. No page states the rule in one sentence, but five lines do:

```rust
fn assert_copy<T: Copy>(_: T) {}

fn main() {
    let x = 5i32;
    let c = move || x + 1;
    assert_copy(c);
}
```

This compiles, because the closure's only capture, `x`, is `Copy`. Swap the capture for a `String`, and `assert_copy(c)` instead fails:

```text
error[E0277]: the trait bound `String: Copy` is not satisfied
```

Neither run needed a chapter on closures or a search through the glossary's auto traits entry; each took less time than reading the first paragraph of a chapter, with the compiler's own confirmation attached for free.

## Practice

1. ▢ Predict what happens if `first_twice_removed` above is wrapped in a third function, still with no `#[track_caller]` anywhere, before adding it and running.

<details markdown="1"><summary>Hint</summary>

Ask which function, counting from the panic, is the first one lacking the attribute.

</details>

<details markdown="1"><summary>Check</summary>

Nothing changes: the reported line still names `v.first().unwrap()` inside `first`, since that is still the first function without `#[track_caller]`, and the attribute must sit on every layer between the panic and wherever the blame should land. Extra wrapping without it is invisible to this mechanism.

</details>

2. ▢ Predict whether `assert_copy` above still compiles if the closure captures a `String` by move and only prints it, then write the five lines and run them to check.

<details markdown="1"><summary>Check</summary>

It fails, with `error[E0277]` naming the trait bound `String: Copy`, since a closure's `Copy` status depends on every value it captures, and `String` is not `Copy`. The same five-line shape answers the question either way.

</details>

3. ▢ An old forum post claims a lint is allow-by-default; the Reference still agrees, but the lint warns on your own build anyway. Using the order of authority, say what settles this, and why the Reference agreeing with the post does not.

<details markdown="1"><summary>Hint</summary>

The order ends with a run on your own toolchain for a reason.

</details>

<details markdown="1"><summary>Check</summary>

The build you just ran settles it, since a run outranks every written source. Two sources agreeing does not rule out both being stale, most likely because the lint's default changed in a release neither has caught up with; the warning is the toolchain answering directly.

</details>

4. ▢ Set up a tiny library crate defining `#[non_exhaustive] pub struct Point { pub x: i32, pub y: i32 }` plus a function inside it building one with a literal, and a second crate depending on it that tries the same literal. Predict which one fails before running both.

<details markdown="1"><summary>Hint</summary>

The Reference's own sentence about this names one specific place the attribute has no effect.

</details>

<details markdown="1"><summary>Check</summary>

The library crate's own function compiles, since `non_exhaustive` has no effect inside the crate defining the type. The dependent crate's identical literal fails with `error[E0639]: cannot create non-exhaustive struct using struct expression`, because the restriction only protects callers outside the defining crate from a field added later.

</details>

5. ▢ You find a claim, older than `Mutex::clear_poison`'s stabilisation, that `into_inner` is the only way to recover from a poisoned mutex. Name the fastest check that the claim is out of date, without opening either GitHub link this lesson used.

<details markdown="1"><summary>Check</summary>

Compiling `Mutex::new(0).clear_poison();` on your own toolchain: if it compiles, the claim is out of date, and no tracking issue or blog post needs reading to reach that conclusion. Those explain when and why it changed, not whether it did.

</details>

## Real-world reps

- [ ] Find one question about your `logsum` project that its own doc comments do not answer, settle it using this lesson's order of authority, and write down which source actually settled it and how many sources you opened before it did.
- [ ] Take one claim about the standard library you have carried since an early stage without checking it, and verify it against the item's own source and its `#[stable]` attribute rather than against memory, noting whether it held up.
- [ ] Tomorrow: list every public item in `logsum` whose doc comment states something you have not personally verified against its own tests or source, and fix whichever of the claim and the code turns out to be wrong.

## Going further

- [2008-non-exhaustive](https://rust-lang.github.io/rfcs/2008-non-exhaustive.html): the accepted RFC this lesson reads for the alternatives the Reference never mentions
- [Stability attributes](https://rustc-dev-guide.rust-lang.org/stability.html): the compiler team's own account of what `#[stable]` and `#[unstable]` require and record
- [The Rust Reference](https://doc.rust-lang.org/reference/): the durable statement of the language's rules that outranks a blog post
- [Tracking Issue for mutex_unpoison](https://github.com/rust-lang/rust/issues/96469): the issue this lesson follows from a stability badge to a stabilisation pull request's milestone
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
