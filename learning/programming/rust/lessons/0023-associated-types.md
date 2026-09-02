---
title: 23. Associated Types
description: Why Iterator names its Item as an associated type rather than a parameter, and what that decides for anyone implementing it
type: lesson
---

# Lesson 23. Associated Types

**Mission link:** A trait whose method needs a placeholder type forces a choice about who fills it in, the implementer once or the caller every call, and getting it backwards either boxes every implementer into one type or makes every call site repeat itself, the choice `Iterator` settles by declaring `Item` an associated type rather than a parameter.
**Primary source:** [Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html)
**Prerequisites:** [Lesson 12](0012-iterators-and-closures.md), [Lesson 22](0022-trait-bounds-and-generic-functions.md)

## Warm-up

1. ▢ Lesson 12 said an iterator is any type implementing `Iterator`, which asks for exactly one method, `fn next(&mut self) -> Option<Self::Item>`. Without looking ahead, say what `Self::Item` stands in for, and why the signature is not `fn next<T>(&mut self) -> Option<T>`.

<details markdown="1"><summary>Check</summary>

`Self::Item` names the one type this implementer's iterator produces, fixed when `Iterator` is implemented rather than supplied by whoever calls `next`. A generic `T` would let the same call site ask for a different type each call, which is not what an iterator does: the same value always yields the same kind of thing.

</details>

2. ▢ Lesson 22 showed that a generic function bounded by a trait, called with two concrete types, produces two separate copies in the compiled binary, while the same function taking `&dyn Trait` compiles once and dispatches at runtime. Name the compiler technique behind the generic version's duplication.

<details markdown="1"><summary>Check</summary>

Monomorphisation: the compiler generates one specialised copy per concrete type the generic function is called with, rather than one shared copy that decides at runtime. The `&dyn Trait` version is the other side of that trade, a single compiled copy that pays with a vtable lookup.

</details>

## Know this

### One choice per type, not one choice per call

An associated type is a placeholder a trait declares once, filled in exactly once by each implementer, and it is easy to reach for a generic parameter instead since both look like a slot for a concrete type. `Iterator` declares `type Item;` rather than `trait Iterator<Item>`: a generic parameter lets the same type implement a trait many times, once per value a caller supplies, while an associated type is chosen once by the implementer and every caller sees the same answer. Writing `Iterator<u32>` as though `Item` were a parameter does not compile:

```text
error[E0107]: trait takes 0 generic arguments but 1 generic argument was supplied
  --> src/bin/e0107.rs:1:18
   |
 1 | fn takes_iter<I: Iterator<u32>>(_it: I) {}
   |                  ^^^^^^^^ expected 0 generic arguments
   |
help: turn the generic argument into an associated item binding
   |
 1 | fn takes_iter<I: Iterator<Item = u32>>(_it: I) {}
   |                           ++++++
```

A `note` line normally follows, quoting the trait's declaration by pointing at the standard library's own source file with a full path into the installed toolchain; it is trimmed here, since that path names one machine's toolchain install and tells a reader nothing. The `help` is the whole story: `Iterator` takes zero generic arguments, and what looked like one is an associated item waiting for a `Name = Type` binding instead.

Going the other way, a trait object that never says what `Item` is fails just as directly, because `&dyn Iterator` needs one concrete shape for its vtable:

```text
error[E0191]: the value of the associated type `Item` in `Iterator` must be specified
 --> src/bin/e0191.rs:1:22
  |
1 | fn describe(it: &dyn Iterator) {
  |                      ^^^^^^^^
  |
help: specify the associated type
  |
1 | fn describe(it: &dyn Iterator<Item = /* Type */>) {
  |                              +++++++++++++++++++
```

The `help` inserts the missing binding. Both errors are one fact seen twice: `Item` is not a knob a caller turns per call, it is a decision the implementer already made, and the compiler needs it settled first.

### Implementing Iterator for your own type

The project's parsing step hands back one parsed line at a time out of a loop; turning that into an `Iterator` means writing the one method the trait asks for and choosing `Item` once, after which the rest of the iterator vocabulary follows unasked. `Records` below wraps whatever already yields owned lines and owns every `String` it reads, deliberately: teaching it to borrow the line instead is lesson 27's job, not this one's.

```rust
struct Record {
    path: String,
    status: u16,
    bytes: u64,
}

struct Records {
    lines: std::vec::IntoIter<String>,
}

fn parse_record(line: &str) -> Option<Result<Record, String>> {
    if line.is_empty() || line.starts_with('#') {
        return None;
    }
    let mut parts = line.split_whitespace();
    let (Some(path), Some(status), Some(bytes)) = (parts.next(), parts.next(), parts.next())
    else {
        return Some(Err(format!("missing field in {line:?}")));
    };
    let (Ok(status), Ok(bytes)) = (status.parse(), bytes.parse()) else {
        return Some(Err(format!("{line:?} is not a number")));
    };
    Some(Ok(Record { path: path.to_string(), status, bytes }))
}

impl Iterator for Records {
    type Item = Result<Record, String>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let line = self.lines.next()?;
            if let Some(result) = parse_record(&line) {
                return Some(result);
            }
        }
    }
}
```

`next` returns `Option<Self::Item>`, and here `Item` is `Result<Record, String>`: a blank line or a comment is skipped without producing anything, a request line that parses becomes `Ok`, and a request-shaped line that fails to parse becomes `Err` rather than being silently dropped. Choosing `Item` to be a `Result` rather than a bare `Record` is still one choice made once for every consumer; nothing in `Iterator`'s declaration stops an associated type from being a compound type like this one.

Nothing else about `Records` needed writing. Over the project's seven-line sample input, three requests, a comment, a blank line and two malformed lines, `.count()` walks the chain once and returns `5`, one entry per line that was neither blank nor a comment. Calling `.filter_map(Result::ok).map(|r| r.bytes).sum::<u64>()` on the same input keeps only the successes and totals their bytes, `2090`. Neither `count`, `filter_map` nor `sum` is written anywhere in `Records`: they are default methods declared once on `Iterator` itself, defined in terms of `next`, and every type that supplies `next` inherits all of them for free. That is the trade a hand-written loop never offered: write one honest method and the whole vocabulary lesson 12 covered, `map`, `filter_map`, `sum`, `count` and the rest, works on the new type with no further code.

### Naming the associated type in a bound

A function generic over something that implements `Iterator` usually needs to say what item it produces, using the same `Name = Type` binding the `E0107` help suggested:

```rust
fn sum_of<I: Iterator<Item = u32>>(it: I) -> u32 {
    it.sum()
}
```

calling `sum_of(vec![1u32, 2, 3].into_iter())` gives `6`. The same binding names what an `impl Trait` return type produces, without naming the concrete iterator type underneath it:

```rust
fn paths(records: Vec<Record>) -> impl Iterator<Item = String> {
    records.into_iter().map(|r| r.path)
}
```

collecting it into a `Vec<String>` gives `["/index", "/index", "/login"]` for the three parsed requests above; the caller learns only that it yields owned `String`s, not that the real type is a `Map` over `std::vec::IntoIter`.

Most of the time `I::Item` is all a signature needs, but that shorthand breaks once a type is bound by two traits that each declare an associated type of the same name:

```rust
trait Labelled {
    type Item;
}

fn describe<I: Iterator + Labelled>(_first: I::Item) {}
```

```text
error[E0221]: ambiguous associated type `Item` in bounds of `I`
 --> src/bin/e0221.rs:5:45
  |
2 |     type Item;
  |     --------- ambiguous `Item` from `Labelled`
...
5 | fn describe<I: Iterator + Labelled>(_first: I::Item) {}
  |                                             ^^^^^^^ ambiguous associated type `Item`
  |
  = note: associated type `Item` could derive from `Iterator`
help: use fully-qualified syntax to disambiguate
  |
5 - fn describe<I: Iterator + Labelled>(_first: I::Item) {}
5 + fn describe<I: Iterator + Labelled>(_first: <I as Labelled>::Item) {}
  |
```

Naming `Iterator`'s `Item` specifically needs the fully qualified form the `help` is built from: `<I as Iterator>::Item`. Writing `fn describe<I: Iterator + Labelled>(_first: <I as Iterator>::Item) {}` compiles cleanly, since `<Type as Trait>::Item` says which trait's associated type is meant, instead of leaving the compiler to guess.

### IntoIterator, and looping over a reference

A `for` loop does not call `Iterator::next` directly; lesson 12's desugaring called `.into_iter()` first, a method belonging to a different trait, `IntoIterator`, which every `Iterator` gets for free through a blanket implementation that hands back itself. A type that already implements `Iterator`, such as `Records`, needs nothing more for a `for` loop, but a type that owns a collection and is not itself an iterator has to say what looping over it means, and can do that for a reference to itself so the original value survives the loop:

```rust
struct Playlist {
    tracks: Vec<String>,
}

impl IntoIterator for &Playlist {
    type Item = String;
    type IntoIter = std::vec::IntoIter<String>;

    fn into_iter(self) -> Self::IntoIter {
        self.tracks.clone().into_iter()
    }
}
```

```rust
let list = Playlist { tracks: vec!["a".to_string(), "b".to_string()] };
for track in &list {
    println!("track = {track}");
}
println!("tracks still owned = {:?}", list.tracks);
```

prints `track = a`, `track = b`, then `tracks still owned = ["a", "b"]`: the loop borrowed `list` rather than consuming it, so `list.tracks` is still readable afterwards. Returning a truly borrowed `Item`, `&String` rather than owned `String`, would need a lifetime connecting the borrow to the iterator built from it, exactly what lessons 26 to 28 introduce; for now `into_iter` clones each track on the way out, an honest trade since a lifetime is not on offer yet. `IntoIterator` is the trait a `for` loop asks for, `Iterator` is what makes a type iterable, and implementing `IntoIterator` by hand for `&Playlist` is what a type reaches for when the thing worth looping over is a view onto it, not the type itself.

### One sensible choice, or several

The choice between an associated type and a generic parameter has a plain rule: use an associated type when an implementation has exactly one sensible answer, and a generic parameter when several are legitimate and the caller should say which. `Iterator` is the associated-type case seen throughout this lesson: a `Records` value produces one kind of item, decided once when `Iterator` is implemented, and `next` never asks which kind this time. The standard library's generic-parameter case sits next to it: `Add` is declared `trait Add<Rhs = Self>`, and its documentation implements `Add` for `Point` with the default `Rhs = Self`, then separately implements `Add<Meters> for Millimeters`, choosing a different, equally sensible right-hand side for the same left-hand type. A single type could not implement `Iterator` twice for two different `Item`s the way `Millimeters` implements `Add` twice for two different `Rhs`s; the trait's declaration decides which shape is available before an implementer writes a line. `Deref`, declared `type Target: ?Sized;`, is another associated-type case: a smart pointer dereferences to exactly one target type, never a caller's choice.

## Practice

1. ▢ Predict which error code this fails with, then compile it.

   ```rust
   fn double_all<I: Iterator<i64>>(_it: I) {}

   fn main() {
       double_all(vec![1i64, 2, 3].into_iter());
   }
   ```

<details markdown="1"><summary>Check</summary>

It fails with `E0107`, the lesson's opening mistake again: `i64` needs to be written as `Iterator<Item = i64>`.

</details>

2. ▢ Predict whether this compiles, and which error code it gives if not.

   ```rust
   struct Boxed {
       it: Box<dyn Iterator>,
   }
   ```

<details markdown="1"><summary>Hint</summary>

A struct field's type is checked the same way a function parameter's is; ask what a `dyn Iterator` needs before it has a fixed shape.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `E0191`: a trait object needs its associated type specified, so the field must read `Box<dyn Iterator<Item = /* Type */>>` with a concrete type filled in.

</details>

3. ▢ Implement `Iterator` for `struct Countdown(u8);` so `next` decrements towards zero and yields the value before each decrement. Predict `Countdown(3).collect::<Vec<u8>>()`, then compile and check.

<details markdown="1"><summary>Check</summary>

It produces `[3, 2, 1]`: each call returns `Some` of the value still held, then decrements, until the field reaches `0` and `next` returns `None`.

</details>

4. ▢ Predict what happens when `head` is compiled as written, then fix it so the returned item is `Iterator`'s, not `Tagged`'s.

   ```rust
   trait Tagged {
       type Item;
   }

   fn head<I: Iterator + Tagged>(mut it: I) -> Option<I::Item> {
       it.next()
   }
   ```

<details markdown="1"><summary>Hint</summary>

Two traits in the same bound both declare an `Item`; `I::Item` alone cannot say which one is meant.

</details>

<details markdown="1"><summary>Check</summary>

As written it fails with `E0221`, ambiguous between `Iterator`'s `Item` and `Tagged`'s; writing the return type as `Option<<I as Iterator>::Item>` names `Iterator`'s explicitly and compiles.

</details>

5. ▢ Judgement call, not a compile check. `Vec<i32>` implements both `Extend<i32>` and `Extend<&'a i32>`, one collection absorbing two different kinds of item depending on which `impl` a caller's iterator matches. Would `Extend`'s `A` fit better as an associated type or as the generic parameter it already is?

<details markdown="1"><summary>Check</summary>

A generic parameter fits, which is why `Extend<A>` is declared that way: one type absorbing more than one kind of item, one `impl` per kind, is the several-sensible-choices case this lesson's design rule describes, the same shape as `Add<Rhs>` rather than `Iterator`'s single `Item`.

</details>

## Real-world reps

- [ ] Replace the loop in your `logsum` project that turns lines into records with a `Records` type implementing `Iterator`, choosing `type Item` and writing one `next`, so summarising becomes a chain over records rather than a loop over lines.
- [ ] Call two methods on your new `Records` value that you never wrote, one used before this lesson and one not, and note in a comment which default `Iterator` method each is.
- [ ] Tomorrow: without looking back, write `Iterator`'s two required pieces from memory, then check them against this lesson.

## Going further

- [Advanced Traits](https://doc.rust-lang.org/book/ch20-02-advanced-traits.html): associated types versus generic parameters, through `Iterator` and `Add`, plus fully qualified syntax
- [IntoIterator](https://doc.rust-lang.org/std/iter/trait.IntoIterator.html): the trait a `for` loop actually calls, and its blanket implementation for every `Iterator`
- [E0221](https://doc.rust-lang.org/error_codes/E0221.html): the diagnostic for an associated type that could come from more than one trait
- [Associated items](https://doc.rust-lang.org/reference/items/associated-items.html): the Reference's rule for how an associated type is declared and fulfilled
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
