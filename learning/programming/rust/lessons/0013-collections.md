---
title: 13. The Collections Worth Knowing
description: Vec and HashMap cover most of it, and the entry API is the one thing worth learning properly
type: lesson
---

# Lesson 13. The Collections Worth Knowing

**Mission link:** Almost every program holds a growing list or looks something up by key, and reaching for the wrong collection, or a hand-rolled loop where the standard library already has the right method, is the kind of thing a reviewer flags in every language you touch after this one.
**Primary source:** [std::collections](https://doc.rust-lang.org/std/collections/index.html)
**Prerequisites:** [Lesson 12](0012-iterators-and-closures.md), [Lesson 9](0009-option.md)

## Warm-up

1. ▢ Lesson 12 said an iterator does nothing until something consumes it, and that `.iter()` and `.into_iter()` differ in whether they hand out borrowed or owned items. Writing `for x in &v`, which of those is running, and does `v` still exist once the loop ends?

<details markdown="1"><summary>Check</summary>

`&v`'s iterator borrows: each `x` is a reference, `v` is never moved, and it is still there after the loop. Writing `for x in v`, or calling `v.into_iter()` directly, consumes `v`, gone once the loop starts.

</details>

2. ▢ Lesson 9 established that a value which might be missing gets a type of its own, `Option<T>`, rather than a special value borrowed from `T`. Every lookup in this lesson comes back as an `Option`. What does `HashMap::get` returning `Option<&V>` rather than `&V` buy the caller?

<details markdown="1"><summary>Check</summary>

It forces the missing case to be handled at compile time rather than discovered at run time. A plain `&V` would promise the key is there; `Option<&V>` admits it might not be, so nothing has to guess, and nothing can silently read past a key that was never inserted.

</details>

## Know this

### `Vec`, properly

`push` appends to the end, the method most `Vec` code reaches for first:

```rust
let mut v: Vec<i32> = Vec::new();
v.push(3);
v.push(1);
v.push(2);
```

Reaching an element by position is where lesson 9's argument shows most clearly. Indexing with `v[i]` and calling `v.get(i)` ask the same question two different ways:

```rust
let v = vec![10, 20, 30];
println!("{:?}", v.get(5));
println!("{}", v[5]);
```

The first line prints `None`. The second panics:

```text
thread 'main' panicked at src/main.rs:4:21:
index out of bounds: the len is 3 but the index is 5
```

Same out-of-range position, two different answers: `[]` treats "not there" as a broken invariant and stops the program; `get` treats it as normal and hands the absence back as a value. Reach for `get` when the index might be out of range, and `[]` only once you can say why it never will be.

Iterating with `for x in &v` borrows, as the warm-up described, so `v` stays usable afterwards, and it is the form nearly all code wants. `retain` keeps only the elements a predicate accepts:

```rust
let mut v = vec![1, 2, 3, 4, 5, 6];
v.retain(|&x| x % 2 == 0);
```

`v` ends as `[2, 4, 6]`. `sort` puts a `Vec` of `Ord` values into ascending order; `sort_by_key` sorts by whatever a closure extracts instead, useful when the order you want is not the type's own:

```rust
let mut words = vec!["ccc", "a", "bb"];
words.sort_by_key(|s| s.len());
```

That gives `["a", "bb", "ccc"]`, shortest first, not the alphabetical order plain `sort` gives. `dedup` removes duplicates, but only where they are already adjacent, worth stating plainly since it is the one method here that looks like it does more than it does:

```rust
let mut v = vec![1, 1, 2, 2, 3, 1];
v.dedup();
```

`v` ends as `[1, 2, 3, 1]`. The last `1` survives because it is not next to the earlier run of `1`s; `dedup` only ever compares neighbours, never the whole `Vec`. Sort first if you want every duplicate gone regardless of position.

`len` and `capacity` answer different questions: `len` is how many elements are actually there, `capacity` is how much space is reserved before the next `push` needs to ask the allocator for more. `Vec::with_capacity(10)` followed by two pushes gives `len() == 2` and `capacity() == 10`; nothing about capacity shows up in what the `Vec` holds, only in how soon it grows.

### `String` as a collection

A `String` owns a buffer of UTF-8 bytes, and `push_str` and `push` are its two ways of growing that buffer: `push_str` appends a `&str`, `push` appends one `char`.

```rust
let mut s = String::from("hi");
s.push_str(" there");
s.push('!');
```

`s` ends as `hi there!`. Indexing it by an integer position, `s[0]`, does not compile:

```text
error[E0277]: the type `str` cannot be indexed by `{integer}`
   --> src/main.rs:3:15
    |
  3 |     let c = s[0];
    |               ^ string indices are ranges of `usize`
    |
    = note: you can use `.chars().nth()` or `.bytes().nth()`
```

Trimmed of a `help` line and a pointer; the rest is what the compiler printed. Byte position and character position stop agreeing as soon as text is not plain ASCII, and a position landing mid-character has no sensible answer, so the compiler refuses the question rather than letting it panic later. `chars` walks Unicode scalar values and `bytes` walks the raw `u8`s underneath: on text whose accented letter is a base letter plus a combining mark, `chars().count()` gives `5` where `bytes().count()` gives `6`. Reaching a character has two honest forms, `s.chars().nth(i)` for an `Option<char>` found by walking, and `&s[a..b]` for a byte-range slice that panics if either end misses a boundary. Neither is indexing by position, which is the point.

### `HashMap`, and the entry API

A `HashMap` answers "what value did I store under this key", and the entry API is worth learning properly because the alternative shows exactly why it exists. The version a reader reaches for first, `get` then `insert`:

```rust
let mut counts: HashMap<&str, i32> = HashMap::new();
for w in ["a", "b", "a", "c", "a"] {
    let count = match counts.get(&w) {
        Some(&c) => c,
        None => 0,
    };
    counts.insert(w, count + 1);
}
```

That works, and it is three lines doing one job: look up, decide a default, write back. `entry` collapses it to one:

```rust
let mut counts: HashMap<&str, i32> = HashMap::new();
for w in ["a", "b", "a", "c", "a"] {
    *counts.entry(w).or_insert(0) += 1;
}
```

Both give the same map: `a` maps to `3`, `b` to `1`, `c` to `1`. `entry` looks up the key once and hands back a place to write, whether or not it was occupied; `or_insert(0)` fills that place only if nothing was there, and leaves an existing value untouched, so on a map where `a` already maps to `5`, `*counts.entry("a").or_insert(0) += 1` gives `6`, not a reset to `1`. `get` returns `Option<&V>`: `counts.get("a")` gives `Some(&3)`, and `counts.get("z")` gives `None` for a key never inserted, the same shape the warm-up asked about. `insert` returns whatever was there before, also an `Option`: `Some` of the old value over an existing key, `None` over a new one. `remove` works the same way in reverse, `Some` the first time and `None` once there is nothing left to remove. Iterating with `for (k, v) in &counts` borrows every pair without taking the map apart, the borrowing form lesson 12 named.

### Iteration order is a correctness matter

A `HashMap` has no iteration order you are entitled to rely on: printing `counts.iter()` directly prints whatever order its internals happen to produce, which is not part of its contract, so any output a person or a test depends on has to be sorted first:

```rust
let mut pairs: Vec<_> = counts.iter().collect();
pairs.sort();
```

A `BTreeMap` built from the same pairs needs no such step, because it keeps its keys in order as a matter of what it is:

```rust
use std::collections::BTreeMap;
let btree: BTreeMap<&str, i32> = counts.into_iter().collect();
```

Iterating `btree` gives `[("a", ...), ("b", ...), ("c", ...)]`, in key order, every time. Choosing between the two follows the same access-pattern rule as the rest of this lesson: `HashMap` by default, `BTreeMap` the moment you need the keys in order or a range of them.

### The rest, one question each

`HashSet` and `BTreeSet` answer "have I seen this value before", the same relationship as the two maps above: `HashSet` for membership with no order guarantee, `BTreeSet` when the members need to come out sorted or by range. `VecDeque` answers "add or remove from either end", what a queue or a sliding window needs and a plain `Vec`, built around one end, does not. `BinaryHeap` answers "give me the largest item next", the shape a priority queue needs; it gets only that name and that question here, no tour.

### Which collection to reach for

| Collection | The question it answers |
|---|---|
| `Vec<T>` | An ordered list I will index or walk from the start |
| `HashMap<K, V>` | Look up by key; I do not care what order they come back in |
| `BTreeMap<K, V>` | Look up by key, and I need them in order or by range |
| `HashSet<T>` | Is this value already present; order does not matter |
| `BTreeSet<T>` | Is this value already present, and I need them in order |
| `VecDeque<T>` | Add or remove from either end |
| `BinaryHeap<T>` | Always hand me the largest (or smallest) item next |

`Vec` and `HashMap` cover most programs on their own; reaching for anything else here should follow from an access pattern you can name, not a feeling that the plain two are too ordinary.

### What the stage bought

Lesson 7 gave a struct a way to say what it owns, field by field. Lesson 8 gave an enum that makes the combination the domain never meant impossible to construct. Lesson 9 gave absence its own type, so it is never mistaken for a value that is genuinely there. Lesson 10 gave failure a type too, one a caller has to look at rather than an exception that skips past unnoticed. Lesson 11 gave a pattern that decides, on the spot, whether the value underneath it was borrowed or moved. Lesson 12 gave an iterator that does nothing until something consumes it, and a closure that captures exactly what it touches. The stage's promise, from this workspace's own arc table, was that you would model with enums and handle absence without reaching for `unwrap`; the six lessons before this one are what met it, and this lesson only adds where the results get counted and stored. Stage 3, Errors and API shape, is where `logsum` stops being a binary that panics or prints and hopes, and becomes a library whose failures a caller can actually handle.

## Practice

1. ▢ Predict what each line prints or does, in order, then compile it.

   ```rust
   fn main() {
       let v = vec![10, 20, 30];
       println!("{:?}", v.get(5));
       println!("{}", v[5]);
   }
   ```

<details markdown="1"><summary>Check</summary>

The first line prints `None`, since `5` is out of range and `get` says so as a value. The second never finishes: it panics with `index out of bounds: the len is 3 but the index is 5`, exit status 101. Same fact, answered twice: once as data, once as a crash.

</details>

2. ▢ Predict whether this compiles, and if not, name the error code, then compile it.

   ```rust
   fn main() {
       let s = String::from("rust");
       println!("{}", s[0]);
   }
   ```

<details markdown="1"><summary>Hint</summary>

This is not a run-time question. Ask what type `s[0]` would even have to be, and whether the compiler can decide that from an integer alone.

</details>

<details markdown="1"><summary>Check</summary>

Does not compile: `error[E0277]`, "the type `str` cannot be indexed by `{integer}`", noting "string indices are ranges of `usize`". Nothing runs, since the indexing is refused before the program starts.

</details>

3. ▢ Predict what this prints, then compile and run it.

   ```rust
   use std::collections::HashMap;

   fn main() {
       let mut m: HashMap<&str, i32> = HashMap::new();
       m.insert("x", 5);
       *m.entry("x").or_insert(0) += 1;
       println!("{:?}", m.get("x"));
   }
   ```

<details markdown="1"><summary>Hint</summary>

`or_insert` only ever runs for a key that is not there yet. Is `"x"` one of those?

</details>

<details markdown="1"><summary>Check</summary>

`Some(6)`. `"x"` already mapped to `5`, so `or_insert(0)` never fires; `entry` hands back the existing slot, and `+= 1` takes it to `6`. A common misreading is that `or_insert` resets the value; it only ever fills an empty one.

</details>

4. ▢ Predict this `Vec`'s contents after `dedup`, then compile and check.

   ```rust
   fn main() {
       let mut v = vec![1, 2, 1, 1, 3, 3, 2];
       v.dedup();
       println!("{v:?}");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`dedup` only ever compares an element to its immediate neighbour. Which pairs in this list are actually adjacent and equal?

</details>

<details markdown="1"><summary>Check</summary>

`[1, 2, 1, 3, 2]`. Only the adjacent `1, 1` and `3, 3` collapse; the earlier `1` and the later `2` are duplicates of values seen before, but neither sits next to its match, so both survive.

</details>

5. ▢ This one is a judgement call rather than a compile check. For each, name the collection you would reach for first, and the question that makes it the right one.

   - a) Counting how many times each status code appears while summarising a log.
   - b) Printing the busiest paths in ascending order, every time, without sorting by hand at every print site.
   - c) A job queue where new work is added at the back and taken from the front.

<details markdown="1"><summary>Check</summary>

a) `HashMap`, with the entry API: the question is "how many so far for this key", and nothing about status codes needs an order.

b) `BTreeMap`: the question is "give me these in order", repeatedly, with no sort step needed anywhere.

c) `VecDeque`: the question is "add or remove from either end", which is the one thing it is built to answer and a plain `Vec` is not shaped for.

</details>

## Real-world reps

- [ ] In `logsum`, replace any hand-rolled `get`-then-`insert` counting with the entry API: counts per line kind, and bytes per path, both belong in a `HashMap` built this way.
- [ ] Add the rejected-line count to your summary's output, printing it alongside the per-kind counts and the bytes-per-path totals, sorted by path before you print them.
- [ ] Tomorrow: without looking back, write the entry-API line for counting occurrences of a key from memory, then check it against this lesson.

## Going further

- [Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html): the full API, including `retain`, `dedup` and `capacity`
- [Storing Keys with Associated Values in Hash Maps](https://doc.rust-lang.org/book/ch08-03-hash-maps.html): the entry API introduced in prose, from the Book
- [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html): the ordered map, and what it takes to query a range of keys
- [Storing UTF-8 Encoded Text with Strings](https://doc.rust-lang.org/book/ch08-02-strings.html): why indexing a `String` by byte position is not allowed
- [E0277](https://doc.rust-lang.org/error_codes/E0277.html): the trait-not-implemented code behind indexing a `String` directly
- [Data and control](../reference/data-and-control.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
