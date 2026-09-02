---
title: Data and control
description: The modelling decisions, the Option and Result APIs, the pattern rules, and which collection to reach for
type: reference
---

# Data and control

Lookup sheet for stage 2. The question it exists to answer: **what shape should this value have, and how do I get at it without an `unwrap`?**

## Struct or enum

| Question | Reach for |
|---|---|
| The value is one shape, made of parts that are always present together | Struct |
| The value is exactly one of several distinct shapes, never a mix | Enum |

The one-line test: if a struct's fields would need a comment saying which combinations are meaningful, the illegal combinations are constructible and an enum removes them; if every field is always present, an enum buys nothing but an extra `::Variant` at every construction site and every match.

## Ownership of a field or a payload

A struct's field and an enum variant's payload are owned identically: dropping the container drops what it holds, and moving a payload out of a `match` arm is the same move rule as moving a field out by value.

| Choice | What it costs | What it removes |
|---|---|---|
| Owned field (`String`, `Vec<T>`, ...) | An allocation the borrowed form would not need | The question "how long does this struct live", from every use site |
| Borrowed field (`&'a str`, ...) | A lifetime parameter on the struct itself, `struct S<'a> { .. }` | Nothing, until a measured cost justifies the annotation |

Stage 2 owns its fields: a lifetime-carrying struct needs a lifetime annotation, which is stage 4's tool, not this one. A borrowed field with no lifetime parameter fails with `E0106`, missing lifetime specifier.

## The `Option` API

| Method | Question it answers | Returns |
|---|---|---|
| `map` | If it's there, what do I want instead? | `Some(f(x))` or `None` unchanged |
| `and_then` | Given the value, what's the next lookup, and can that fail too? | Whatever the closure returns, no `Option<Option<T>>` |
| `unwrap_or(v)` | If absent, what plain default? | `T`, argument built regardless |
| `unwrap_or_else(f)` | If absent, what computed default? | `T`, closure runs only when needed |
| `unwrap_or_default()` | If absent, what's the type's own default? | `T::default()` |
| `ok_or(e)` | Turn absence into a reason | `Ok(x)` or `Err(e)` |
| `filter(p)` | Keep it only if a predicate holds | `Some(x)` or `None` |
| `as_ref` | Look without moving | `Option<&T>` |
| `take` | Empty the slot and hand back what was there | `Option<T>`, leaves `None` behind |
| `replace(v)` | Swap in a new value, hand back the old | `Option<T>`, leaves `Some(v)` behind |
| `is_some` | Yes or no, without touching the value | `bool` |

`as_ref` fixes a real error: an `Option<String>` field read twice with `if let Some(p) = rec.path` fails `E0382` on the second read, since the first already moved the `String` out; `.as_ref()` borrows an `Option<&String>` instead. `take` and `replace` are the fix when only a `&mut` to a struct is in hand and a value must be handed to the caller: the compiler suggests `.clone()` there, which is the wrong fix, since `take` satisfies the rule for free.

## The `Result` API

| Method | Question it answers | Returns |
|---|---|---|
| `map` | If it succeeded, what do I want instead? | `Ok(f(x))` or `Err` unchanged |
| `map_err` | If it failed, what do I want instead, on the error side? | `Ok` unchanged or `Err(f(e))` |
| `and_then` | Given success, what's the next step, and can it also fail? | Whatever the closure returns |
| `unwrap_or(v)` | If it failed, what plain default? | `T` |
| `unwrap_or_else(f)` | If it failed, what computed default, maybe from the error? | `T` |
| `ok` | Keep only the success side | `Option<T>` |
| `err` | Keep only the failure side | `Option<E>` |
| `is_ok` | Yes or no, without consuming anything | `bool` |

`?` is the `match` that returns `Err(e)` early and unwraps `Ok(x)`, compressed to one character. It needs the function's error type reachable from the expression's error type through `From`; without that conversion the call fails with `E0277`, "`?` couldn't convert the error", and inside this stage the stopgap is `.map_err` at the call site, since an error type's own `From` implementations are stage 3's subject. `Result` carries `#[must_use]`, so dropping one unread produces a warning rather than a compile error, and the program keeps running past the unnoticed failure. `?` also short-circuits on `Option`, with no `Err` payload to carry; `main` may return `Result<(), E>` whenever `E: Debug`, printing `Error: {the Err value's Debug form}` on standard error and exiting with status 1.

**Panic against error, one line:** a `Result` is for a failure the caller could plan for and recover from; a panic is for a broken invariant in your own code that should never happen if the program is correct.

## The pattern rules

| Pattern kind | Answers |
|---|---|
| Literal | Is it exactly this value? |
| Range, `a..=b` | Is it within this inclusive range? |
| Alternation, `a \| b` | Is it one of several values sharing an arm? |
| Struct destructuring, `{ x, y, .. }` | Which fields do I need, ignoring the rest? |
| Tuple or tuple struct, by position | What are the positional parts? |
| Nested pattern | What does a value made of several parts look like all at once? |
| `@` binding | Does it match this shape, and what was the value? |
| Guard, `pat if cond` | Does the shape match, and does an arbitrary condition also hold? |

**Binding modes, and the 2024 edition change.** Matching a non-reference pattern against a reference borrows the contents instead of moving them: `match &line { Line::Note(text) => .. }` binds `text` as `&String`, threading a `ref` binding through automatically, so `line` stays whole afterwards. Matching `line` by value instead moves the payload out on the same rule lesson 2 established for plain assignment. **Since the 2024 edition, an explicit `&` pattern may no longer mix with an implicit borrow**: `(_, &b)` matched against a reference to a tuple compiles and prints on edition 2021, and fails on edition 2024 with `error: cannot explicitly dereference within an implicitly-borrowing pattern`, labelled `reference pattern not allowed when implicitly borrowing`. The fix is either an explicit `&` at every level, `&(_, &b)`, or no inner `&` at all, `(_, b) => *b`.

| Refutability | Allowed in |
|---|---|
| Irrefutable (matches every value of the type) | `let`, a function parameter, a `for` loop's binding |
| Refutable (some value could fail to match) | `if let`, `while let`, `let ... else`, a `match` arm |

A refutable pattern in an irrefutable position fails with `E0005`, refutable pattern in local binding.

## Diagnostics of the stage

| Code / message | Cause | Honest fix |
|---|---|---|
| `E0106`, missing lifetime specifier | A struct field is a bare reference, `&str` with no lifetime | Own the field (`String`), or add the lifetime parameter once stage 4 gives you the tool |
| `E0061`, wrong number of arguments to a tuple variant | Trying to hand one variant the data two separate fields used to hold | There is no fix inside the call: the illegal combination has nowhere to fit, which is the point |
| `E0382`, use / partial move of a moved value | Matching or passing an enum or struct by value moved a non-`Copy` field or payload out | Match or pass a reference instead, or return the value back if the move was real |
| `E0594`, cannot assign to a field behind a `&` reference | A method takes `&self` but writes to a field | Change the receiver to `&mut self` |
| `E0277`, trait not implemented | `{:?}` with no `Debug` derive; `?` with no `From<E>` for the target error; indexing a `String` or `str` by an integer | Derive `Debug`; write or stub the `From` conversion (stage 3) or `.map_err` at the call site; use `.chars().nth(i)` or a byte-range slice instead of `s[i]` |
| `E0004`, non-exhaustive patterns | A `match` over an enum is missing a variant | Add the missing arm; reach for `_` only when the rest is genuinely uninteresting, never `unreachable!()` on an enum you own |
| `E0005`, refutable pattern in local binding | A refutable pattern, such as `Some(x)`, used in a `let` | Use `if let`, `while let`, or `let ... else` |
| `E0507`, cannot move out of a value behind a `&mut` reference | Returning a field by value through only a `&mut` to its container | `Option::take`, not `.clone()`, when the field is an `Option` |
| `error`, let chains are only allowed in Rust 2024 or later | `if let ... && let ... { }` compiled under edition 2021 | Move to edition 2024, or nest the `if let`s |
| `error`, cannot explicitly dereference within an implicitly-borrowing pattern | An explicit `&` pattern nested inside an implicit borrow, under edition 2024 | `&(_, &b)` throughout, or drop the inner `&` and deref at use, `(_, b) => *b` |

## Iterators

| Kind | Method | Question it answers |
|---|---|---|
| Adapter | `map` | What do I want instead of each element? |
| Adapter | `filter` | Which elements do I keep? |
| Adapter | `filter_map` | Keep only what a closure turns into `Some` |
| Adapter | `enumerate` | Pair each element with its index |
| Adapter | `zip` | Pair two sequences in step, stopping at the shorter |
| Adapter | `take` / `skip` | Keep or drop from the front |
| Adapter | `chain` | Join a second iterator onto the first's end |
| Adapter | `flat_map` | Map and flatten in one step |
| Adapter | `rev` | Give the back first |
| Adapter | `peekable` | What's next, without taking it |
| Consumer | `collect` | Gather into a named type |
| Consumer | `sum` / `count` | Reduce to one number |
| Consumer | `fold` | Run a computation from a seed, no early exit |
| Consumer | `any` / `all` | Yes or no, stopping once settled |
| Consumer | `find` / `position` | First match as a value, or as an index |
| Consumer | `min_by_key` / `max_by_key` | The extreme by a derived key |
| Consumer | `for_each` | Run a closure on every element, keep nothing |

**Laziness, one line:** building a chain does no work; only a consumer calling `next` runs anything inside it, which a dropped, unconsumed chain proves by leaving a side-effecting closure's log empty. Collecting an iterator of `Result<T, E>` into `Result<Vec<T>, E>` stops at the first `Err`; collecting into `Vec<Result<T, E>>` keeps every attempt.

| Trait | Permits |
|---|---|
| `Fn` | Only reads what it captured; callable any number of times |
| `FnMut` | Mutates a capture; needs a `mut` binding, callable any number of times |
| `FnOnce` | Moves a captured value out; callable exactly once |

`FnOnce` is the floor every closure meets. `move` decides what is captured (by value, not by reference), not which trait results. Since edition 2021, a closure captures only the fields it names, so a closure touching `p.left` leaves `p.right` readable while it is alive.

## Collections

| Access pattern | Reach for |
|---|---|
| Ordered list, indexed or walked from the start | `Vec<T>` |
| Look up by key, order does not matter | `HashMap<K, V>` |
| Look up by key, need them in order or by range | `BTreeMap<K, V>` |
| Is this value present, order does not matter | `HashSet<T>` |
| Is this value present, need them in order | `BTreeSet<T>` |
| Add or remove from either end | `VecDeque<T>` |
| Always hand me the largest (or smallest) next | `BinaryHeap<T>` |

`Vec` and `HashMap` cover most programs; the entry API, `*map.entry(k).or_insert(0) += 1`, writes to a slot whether or not it was occupied and never resets one already there. **A `HashMap` has no iteration order you may rely on, and that is a correctness matter, not a style preference**: any output a person or a test depends on has to be sorted first, where a `BTreeMap` built from the same pairs needs no such step. Indexing a `Vec` out of range panics; `.get(i)` returns `Option<&T>` instead, the same absence-as-a-value choice `Option` makes everywhere else in this stage. `dedup` only ever compares adjacent elements; sort first if every duplicate, not just adjacent runs, needs to go.

## Sizes, on this target

| Type | Size (bytes) |
|---|---|
| `Option<&u8>`, `&u8` | 8, 8 |
| `Option<Box<u8>>`, `Box<u8>` | 8, 8 |
| `Option<&str>`, `&str` | 16, 16 |
| `Option<u8>` | 2 |
| `Option<u32>` | 8 |
| A three-variant enum with payloads up to two `f64`s | 24 |
| A three-field struct of `String`, `u16`, `u64` | 40 |

Only the reference and `Box` niche cases are a documented promise of the standard library; every other number here is this target's measurement, not a language guarantee. An enum's size is its largest variant plus a discriminant, rounded up to alignment; the discriminant often hides for free in existing padding, which is why a struct and the enum built from the same fields can measure the same.

## Where the project should be

The stage 2 slice of the arc's rep project, `logsum`, is a line parsed into an enum with payloads, a `Result` returned on a malformed line, and a whole input summarised with a map: counts per kind, bytes per path, and a rejected-line count. See [the project](the-project.md) for the full brief and the state expected at the end of every stage.
