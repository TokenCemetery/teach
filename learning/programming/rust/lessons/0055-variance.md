---
title: 55. Variance
description: Which lifetimes may stand in for which, why your own type decides, and what that commits you to
type: lesson
---

# Lesson 55. Variance

**Mission link:** Once your own type carries a lifetime parameter, a caller will try substituting a longer-lived borrow for a shorter one, and whether that compiles is decided by your fields, not by anything you intended.
**Primary source:** [Subtyping and Variance](https://doc.rust-lang.org/nomicon/subtyping.html)
**Prerequisites:** [Lesson 27](0027-types-that-borrow.md), [Lesson 28](0028-reading-a-lifetime-error.md)

## Warm-up

1. ▢ Lesson 27's `Record<'a>` promised its `path` field's `str` stays valid for at least `'a`, refusing a `Record` whose `path` outlived that string. Given `struct Reader<'a>(&'a str)`, would a `Reader<'static>` be usable anywhere a `Reader<'short>` is expected, for some shorter `'short`?

<details markdown="1"><summary>Check</summary>

Yes, in the direction lesson 27's own checks already assumed: `'static` outlives every other lifetime, so whatever a `Reader<'short>` promises, a `Reader<'static>` satisfies too. Why that holds for `Reader` specifically, rather than every type with a lifetime parameter, is what this lesson answers.

</details>

2. ▢ Lesson 28 showed a `&mut &'a str` slot refusing a shorter borrow, reported as an ordinary `E0597`, "borrowed value does not live long enough", with no mention of variance. Was that diagnostic incomplete, or nothing more to say at the time?

<details markdown="1"><summary>Check</summary>

Nothing more to say: the slot was a bare `&mut &'a str`, not a type you had defined, so the compiler read the whole answer off that one reference, and scope talk covered it. The same fact returns here as invariance, once a type's own fields, not one reference the compiler sees straight through, decide the answer.

</details>

## Know this

### 1. What stage 4 left unnamed, and subtyping stated precisely

Every lifetime error lessons 26 to 28 produced was explained purely in terms of scopes, a borrow not living long enough, or an annotation pinning a lifetime too early, and fixing either needed only reading which scope ended first. None used the word variance, because the only lifetime-carrying shape a stage 4 reader had written was a bare `&'a str` field, where the compiler could read the whole answer off the reference itself. The vocabulary becomes necessary once your type's lifetime parameter sits behind something else, a `Cell`, a function pointer, another layer of indirection, and you must say on purpose whether a caller may substitute a longer-lived borrow for a shorter one, using the term the compiler's own `help` line already points to, the Rustonomicon's [Subtyping and Variance](https://doc.rust-lang.org/nomicon/subtyping.html) chapter.

Two lifetimes relate by subtyping the way two scopes do: `'long` is a subtype of a shorter `'short`, written `'long: 'short`, when the region `'long` names completely contains the region `'short` names, so a borrow lasting `'long` satisfies any requirement written for `'short`, and a `&'long str` stands in wherever a `&'short str` is expected. Whether that survives once the lifetime is buried inside a type you defined is separate, answered here with no error at all:

```rust
struct Reader<'a>(&'a str);

fn shorten<'short, 'long: 'short>(r: Reader<'long>) -> Reader<'short> {
    r
}
```

This compiles. A `Reader<'long>` converts to a `Reader<'short>` exactly as the bare `&'long str` inside it would, since `Reader` adds nothing that could make the substitution unsound. `Reader` is covariant over `'a`, the baseline every other case in this lesson departs from.

### 2. The three variances, each demonstrated by compiling

A type's variance over a lifetime parameter answers one question: given `'long: 'short`, does `Type<'long>` convert to `Type<'short>`, the reverse, or neither. `Reader` above answered yes, covariance. Wrapping the same reference in a `Cell` answers no in both directions at once:

```rust
use std::cell::Cell;

pub struct Slot<'a>(pub Cell<&'a str>);

pub fn shorten<'short, 'long: 'short>(s: Slot<'long>) -> Slot<'short> {
    s
}
```

```text
error: lifetime may not live long enough
 --> src/lib.rs:6:5
  |
5 | pub fn shorten<'short, 'long: 'short>(s: Slot<'long>) -> Slot<'short> {
  |                ------  ----- lifetime `'long` defined here
  |                |
  |                lifetime `'short` defined here
6 |     s
  |     ^ function was supposed to return data with lifetime `'long` but it is returning data with lifetime `'short`
  |
  = help: consider adding the following bound: `'short: 'long`
  = note: requirement occurs because of the type `Slot<'_>`, which makes the generic argument `'_` invariant
  = note: the struct `Slot<'a>` is invariant over the parameter `'a`
  = help: see <https://doc.rust-lang.org/nomicon/subtyping.html> for more information about variance

error: aborting due to 1 previous error
```

The two `note` lines carry the whole teaching, quoted exactly as the compiler wrote them: `Slot` is refused not because anything looks wrong at the call site, but because the type itself is invariant over `'a`, the second of three answers, refusing both directions. The third, refusing what `Reader` allowed while accepting its reverse, needs a field variance has little everyday use for: a function pointer.

```rust
use std::marker::PhantomData;

pub struct Callback<'a>(pub PhantomData<fn(&'a str)>);

pub fn lengthen<'short, 'long: 'short>(c: Callback<'short>) -> Callback<'long> {
    c
}
```

This compiles, going from the shorter lifetime to the longer one. Asking for the conversion `Reader` allowed, longer to shorter, is refused:

```text
error: lifetime may not live long enough
 --> src/lib.rs:8:5
  |
7 | pub fn shorten<'short, 'long: 'short>(c: Callback<'long>) -> Callback<'short> {
  |                ------  ----- lifetime `'long` defined here
  |                |
  |                lifetime `'short` defined here
8 |     c
  |     ^ function was supposed to return data with lifetime `'long` but it is returning data with lifetime `'short`
  |
  = help: consider adding the following bound: `'short: 'long`

error: aborting due to 1 previous error
```

`Callback` is contravariant over `'a`. This diagnostic carries no `invariant` note, the same shape as `Slot`'s with the teaching half removed, since only one direction fails. A field like this is rare in ordinary code, showing up mostly where a type stores a callback it will invoke later with a borrow of its own choosing; elsewhere, covariance or invariance is what you will meet.

### 3. Why each rule is what it is

`&'a T` is covariant because reading through a shorter-lived borrow is harmless: `Reader` never cares how long `'a` is, only that it lasts as long as the borrow, and a longer-lived borrow meets that by definition. A function taking `&'a T` is contravariant for the mirror reason: one accepting any `&'short str` already accepts every `&'long str` too, so the shorter bound substitutes in wherever a caller wanted the longer one. `&'a mut T` is invariant in `T` because a caller could otherwise write a shorter-lived value into a slot the compiler believes lives longer, then read it back once that value is gone. Building the case rather than asserting it:

```rust
pub fn overwrite<'a>(slot: &mut &'a str, value: &'a str) {
    *slot = value;
}

pub fn call_it() {
    let mut outer: &'static str = "outer";
    let inner = String::from("inner");
    overwrite(&mut outer, &inner);
}
```

```text
error[E0597]: `inner` does not live long enough
 --> src/lib.rs:8:27
  |
6 |     let mut outer: &'static str = "outer";
  |                    ------------ type annotation requires that `inner` is borrowed for `'static`
7 |     let inner = String::from("inner");
  |         ----- binding `inner` declared here
8 |     overwrite(&mut outer, &inner);
  |                           ^^^^^^ borrowed value does not live long enough
9 | }
  | - `inner` dropped here while still borrowed
```

`overwrite` unifies both parameters against one `'a`, and `&mut outer` is `&mut &'static str`; because `&mut` is invariant, coercing it to `&mut &'a str` for a shorter `'a` is not allowed, so `'a` is pinned to `'static` and `inner` is judged against that instead of the scope it needs. Refuse the coercion at that reborrow, and the rest is ordinary scope talk, exactly the shape lesson 28 already showed without naming the cause.

### 4. How a type's variance is computed

A struct's variance over a parameter comes from how its fields use it: if every field is covariant, so is the struct; if every field is contravariant, so is the struct; if any two disagree, or one field is itself invariant, the whole struct is invariant, since invariance in one place is a promise the type can never take back elsewhere. That holds even when nothing about the parameter's own type changes, only which field it sits behind:

```rust
pub struct Reader<'a> {
    pub head: &'a str,
    pub tail: &'a str,
}

pub fn shorten<'short, 'long: 'short>(r: Reader<'long>) -> Reader<'short> {
    r
}

use std::cell::Cell;

pub struct ReaderWithCache<'a> {
    pub head: &'a str,
    pub cached_tail: Cell<&'a str>,
}

pub fn shorten2<'short, 'long: 'short>(r: ReaderWithCache<'long>) -> ReaderWithCache<'short> {
    r
}
```

`shorten` compiles without complaint, two plain borrows behaving exactly as one did. `shorten2` does not:

```text
error: lifetime may not live long enough
  --> src/lib.rs:18:5
   |
17 | pub fn shorten2<'short, 'long: 'short>(r: ReaderWithCache<'long>) -> ReaderWithCache<'short> {
   |                 ------  ----- lifetime `'long` defined here
   |                 |
   |                 lifetime `'short` defined here
18 |     r
   |     ^ function was supposed to return data with lifetime `'long` but it is returning data with lifetime `'short`
   |
   = help: consider adding the following bound: `'short: 'long`
   = note: requirement occurs because of the type `ReaderWithCache<'_>`, which makes the generic argument `'_` invariant
   = note: the struct `ReaderWithCache<'a>` is invariant over the parameter `'a`
   = help: see <https://doc.rust-lang.org/nomicon/subtyping.html> for more information about variance
```

Nothing about `head` changed; one added field, `cached_tail: Cell<&'a str>`, took the struct from covariant to invariant, and the same happens for a `RefCell`, a `Mutex`, or an `fn` pointer field anywhere in the type: variance is a property of the whole struct, set by whichever field asks for the strictest answer.

### 5. PhantomData as the tool for saying what you mean

A generic parameter appearing nowhere in a struct's real fields is rejected outright, so a type needing only to promise a relationship to `'a` or `T` reaches for `PhantomData` to say which relationship it means. `PhantomData<T>` declares that the struct owns a `T`, in every sense that matters for variance, as though such a field were really there. `PhantomData<&'a T>` declares a borrow instead, covariant exactly as `&'a T` itself is:

```rust
use std::marker::PhantomData;

pub struct Borrowed<'a, T>(pub PhantomData<&'a T>);

pub fn shorten<'short, 'long: 'short, T>(b: Borrowed<'long, T>) -> Borrowed<'short, T> {
    b
}
```

This compiles, the same verdict as a real `&'a T` field. `PhantomData<fn(T)>` declares a callback taking `T`, contravariant for the reason section 3 argued, the shape `Callback` already used. `PhantomData<*mut T>` declares a raw pointer, invariant over `T` regardless of what `T` would otherwise allow, since a raw pointer carries none of the compiler's aliasing guarantees:

```rust
use std::marker::PhantomData;

pub struct RawSlot<'a>(pub PhantomData<*mut &'a str>);

pub fn shorten<'short, 'long: 'short>(s: RawSlot<'long>) -> RawSlot<'short> {
    s
}
```

```text
error: lifetime may not live long enough
 --> src/lib.rs:6:5
  |
5 | pub fn shorten<'short, 'long: 'short>(s: RawSlot<'long>) -> RawSlot<'short> {
  |                ------  ----- lifetime `'long` defined here
  |                |
  |                lifetime `'short` defined here
6 |     s
  |     ^ function was supposed to return data with lifetime `'long` but it is returning data with lifetime `'short`
  |
  = help: consider adding the following bound: `'short: 'long`
  = note: requirement occurs because of the type `RawSlot<'_>`, which makes the generic argument `'_` invariant
  = note: the struct `RawSlot<'a>` is invariant over the parameter `'a`
  = help: see <https://doc.rust-lang.org/nomicon/subtyping.html> for more information about variance
```

Four shapes, four claims, and picking the wrong one either blocks a substitution a caller should be able to make, or permits one that is not sound.

### 6. Why this is an API decision, not a curiosity

None of this stays inside your crate. A type's variance is part of its public contract exactly as its method signatures are: a caller who shortens your `Record<'a>` to fit a shorter scope relies on covariance holding, whether or not they could name it. Changing one private field from `&'a T` to `Cell<&'a T>`, to add a cache nobody outside sees, flips it from covariant to invariant with no change to a public signature and nothing a documentation diff would show. The caller's code simply stops compiling, far from your change, with the same diagnostic section 2 produced. Deciding what your lifetime parameters may do is made once, at first release, and lesson 0057 picks up from here: what a change like that one breaks, and how to see it coming before a caller does.

## Practice

1. ▢ Predict whether `Lines<'a>(Vec<&'a str>)` shortens the same way `Reader` did, then compile the same `shorten` function against it.

<details markdown="1"><summary>Hint</summary>

`Vec` adds storage and growth, but ask whether it adds any interior mutability of its own.

</details>

<details markdown="1"><summary>Check</summary>

It compiles. `Vec<T>` is covariant over `T` for the same reason `Reader` is covariant over `'a`: nothing about a `Vec` lets you mutate an element through a shared reference, so a `Vec` of longer-lived borrows satisfies every use a shorter-lived one would.

</details>

2. ▢ Change `Slot`'s field from `Cell<&'a str>` to `RefCell<&'a str>`, name it `Cache`, and predict whether `shorten` still fails.

<details markdown="1"><summary>Check</summary>

It fails the same way, naming `Cache` in place of `Slot`:

```text
= note: requirement occurs because of the type `Cache<'_>`, which makes the generic argument `'_` invariant
= note: the struct `Cache<'a>` is invariant over the parameter `'a`
```

`RefCell` grants interior mutability through a shared reference exactly as `Cell` does, and that is what forces invariance, not which type is used.

</details>

3. ▢ `Sink<'a>(fn(&'a str))` stores a real function pointer rather than a `PhantomData` marker. Predict which of `shorten` (long to short) and `lengthen` (short to long) compiles.

<details markdown="1"><summary>Hint</summary>

A bare `fn` field carries the same contravariance as `PhantomData<fn(&'a str)>` did; wrapping it in `PhantomData` never changed the rule, only whether the field was real.

</details>

<details markdown="1"><summary>Check</summary>

`lengthen` compiles and `shorten` fails with the same message `Callback` produced, carrying no invariant note, since `Sink` is contravariant rather than invariant, for the same reason section 3 gave: it already handles every shorter borrow than the one asked for.

</details>

4. ▢ In `overwrite`'s example, predict the error if `inner`'s borrow is never read again after the call, no later `println!` at all.

<details markdown="1"><summary>Hint</summary>

Ask what `'a` unifies to the moment `&mut outer` is passed in, before either argument is used further.

</details>

<details markdown="1"><summary>Check</summary>

The error is `E0597` again, unchanged, since the failure happens at the call itself: `&mut outer` forces `'a` to `'static` before `value` is even considered, so `inner` is measured against `'static` regardless of what follows, the same shape lesson 28 showed for a `Vec<&'static str>` pinned by its own annotation.

</details>

5. ▢ `Combo<'a> { a: &'a str, b: Cell<&'a str> }` mixes a covariant field with an invariant one. Predict the struct's overall variance before compiling the usual `shorten` function against it.

<details markdown="1"><summary>Check</summary>

`Combo` is invariant over `'a`, reporting the same two notes as `Slot`, naming `Combo` instead. One invariant field decides the whole struct regardless of how many others agree, since a caller holding a `Combo` could still reach that field.

</details>

## Real-world reps

- [ ] Audit every public type your summariser exposes with a lifetime parameter, most likely `Record<'a>`: decide covariant or invariant, and name the field that decided it.
- [ ] Then find the one change to a private field, a `Cell` added for a cache nobody outside sees, that flips that type's variance without touching a public signature, and write what caller code would stop compiling.
- [ ] Tomorrow: find a struct with an unused type or lifetime parameter, or one worked around with an extra clone just to keep the compiler quiet, and decide which of section 5's four `PhantomData` shapes says what you meant.

## Going further

- [std::marker::PhantomData](https://doc.rust-lang.org/std/marker/struct.PhantomData.html): the standard library's account of what a `PhantomData<T>` field tells the compiler
- [Subtyping and variance](https://doc.rust-lang.org/reference/subtyping.html): the Reference's formal definitions, plus the higher-ranked cases lesson 0056 owns
- [PhantomData](https://doc.rust-lang.org/nomicon/phantom-data.html): the Nomicon's worked case for why an unused lifetime needs a marker
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
