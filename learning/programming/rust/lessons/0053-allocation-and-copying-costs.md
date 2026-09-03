---
title: 53. Allocation and Copying Costs
description: Where a Rust program actually spends its time, and which of the obvious fixes pay for themselves
type: lesson
---

# Lesson 53. Allocation and Copying Costs

**Mission link:** A reviewer who cannot say whether a `clone` or a fresh `Vec` is the real cost in a hot path either leaves allocation traffic in place or demands a rewrite that buys nothing; the order of magnitude between an allocation and a copy settles which is worth fighting over.
**Primary source:** [The Rust Performance Book](https://nnethercote.github.io/perf-book/title-page.html)
**Prerequisites:** [Lesson 52](0052-measuring-before-optimising.md), [Lesson 13](0013-collections.md)

## Warm-up

1. ▢ Lesson 52 measured reserving a vector's capacity against letting it grow. What did it find about the size of that payoff as the workload grew from eight elements to ten thousand?

<details markdown="1"><summary>Check</summary>

The payoff shrank: about 2.7 times faster at eight elements, about 1.8 times at ten thousand, the opposite of the usual assumption that a fixed cost matters less as more work surrounds it.

</details>

2. ▢ Lesson 13 named `HashMap` the default for "look up by key, order does not matter." Does that hold at every size, or is it a rule of thumb with a size hidden inside it?

<details markdown="1"><summary>Check</summary>

A rule of thumb with a size hidden inside it: lesson 13 never claimed `HashMap` was fastest, only that it answers the right question for most programs. This lesson finds a size where a plainer structure answers it faster, the boundary lesson 13 left unstated.

</details>

## Know this

### The order of magnitude that matters

The Performance Book states the baseline plainly: "Heap allocations are moderately expensive... each allocation (and deallocation) typically involves acquiring a global lock, doing some non-trivial data structure manipulation, and possibly executing a system call." Measured directly, allocating an eight-byte `Vec<u8>` against copying the same eight bytes into an array:

```rust
fn alloc_one(bytes: [u8; 8]) -> Vec<u8> {
    Vec::from(bytes)
}

fn copy_one(bytes: [u8; 8]) -> [u8; 8] {
    bytes
}
```

Benchmarked with criterion, result passed through `black_box` so both actually happen: the allocation took about 29 times longer than the copy, on one machine. That is the order of magnitude this lesson works from: a copy of a few bytes is close to free, so the question worth asking is almost never "is this copy expensive" but "how many times does this allocate."

### Four cases a reader meets constantly

Lesson 52 already measured growing a vector against reserving capacity, cited rather than repeated; the other three follow the same method. Cloning a string against borrowing it, a thousand calls each, forcing a fresh clone every time:

```rust
fn takes_str(s: &str) -> usize { s.len() }
fn takes_string(s: String) -> usize { s.len() }
```

Against a roughly sixty-byte string, the cloned calls took about 66 times longer than the borrowed calls, one machine. Building a `Vec<u32>` from a sixty-four-element chunk two hundred times, once collecting a fresh vector each time and once clearing and extending a vector declared outside the loop:

```rust
let v: Vec<u32> = chunk.iter().map(|x| x * 2).collect();      // fresh each time
buf.clear();
buf.extend(chunk.iter().map(|x| x * 2));                      // same buffer reused
```

The fresh-collect version took about 4.8 times longer, on one machine, for this chunk size. And building a five-piece string two hundred times with `push_str` against `format!`:

```rust
let mut s = String::with_capacity(32);
for p in parts { s.push_str(p); }
```

against

```rust
format!("{}{}{}{}{}", p[0], p[1], p[2], p[3], p[4])
```

`format!` took about 2.1 times longer, on one machine, for this five-piece workload. Section four below explains why that gap is not the one most people expect.

### Where the obvious optimisation does not pay

Lesson 13's default, `HashMap` for "look up by key, order does not matter", measured against a sorted `Vec<(i32, i32)>` searched with `binary_search_by_key`, both built and queried with eight entries:

```rust
map.get(k)
vec.binary_search_by_key(k, |&(key, _)| key)
```

The sorted vector answered all eight lookups about 3 times faster than the `HashMap`, on one machine, not a close call, and not an allocation story: the Performance Book notes `HashSet` and `HashMap` "have a single contiguous heap allocation, holding keys and values, which is reallocated as necessary as the table grows", exactly like a `Vec`, so both pay for one allocation. The gap is what happens after: hashing a key costs more per lookup than a few integer comparisons over data already sitting together, and at eight entries that dominates. This is a small-size result only, with a readability cost too: `binary_search_by_key` is more ceremony than `.get`, and keeping the vector sorted is a rule the type will not enforce. The trade earns its keep for a small table built once and queried often, not one mutating on the request path.

### What the compiler already does for you

Three claims, each checked rather than assumed. First, an indexed loop and an iterator chain summing the same ten thousand `u64` values:

```rust
for i in 0..v.len() { total += v[i]; }
v.iter().sum::<u64>()
```

measured within half a percent: the iterator chain is not a slower, more abstract loop, it compiles to the same work. Second, a small two-field `i64` struct passed by value against by reference, a hundred thousand times, also within half a percent: a copy of two machine words costs nothing extra once passed in registers, so reaching for `&SmallPoint` to "avoid a copy" buys nothing and adds indirection instead. Third, the `format!` gap above: the Performance Book's caveat is that `format!` "produces a `String`, which means it performs an allocation", reading as though the cost is an extra allocation. Disassembling the compiled benchmark found otherwise: `push_str` compiles to one allocator call, inlined pushes, and one deallocation, while `format!` compiles to a single opaque call into `alloc::fmt::format::format_inner` and nothing else visible. Both allocate exactly once; the gap is that call being opaque to the optimiser, unable to simplify anything inside it, where inlined `push_str` calls give it the whole loop to work with. `format!` is worse than it looks, but not for the reason its documentation suggests.

### The allocation-shaped decisions in a type's design

Lesson 27 framed a field that borrows against one that owns as a question of who outlives whom; it is also an allocation decision. Parsing the same six-byte path a thousand times into a field owning a fresh `String` against one borrowing the source line:

```rust
struct OwnedRecord { path: String }
struct BorrowedRecord<'a> { path: &'a str }
```

cost about 35 times more for the owning version, on one machine, lining up with the first section's raw allocation cost: an owned field is not a stylistic preference, it is an allocation paid once per value built. `Cow`, lesson 27's shape for "usually borrowed", sits between the two, decided by a workload measurement: lesson 27's own `normalise` function, against eight paths where seven need no change and one does, against a version that always allocates:

```rust
fn normalise(path: &str) -> Cow<'_, str> { /* lesson 27 */ }
fn normalise_always_owned(path: &str) -> String { path.replace("//", "/") }
```

The `Cow` version ran about 4.5 times faster over that mix, on one machine, because seven of eight calls paid nothing. What matters before reaching for `Cow` is not whether the rare case exists but how rare it is in the traffic the function actually sees.

### The honest summary

Every ratio above came from one run, one machine, one named workload; a different input shape or machine could move the number without moving the lesson. Most programs are slow because of what they do, how many times a loop allocates, not how its lines are phrased, which is why the first section's order of magnitude outlasts this lesson: count allocations before counting characters. Where a measured ratio lands near one, as the iterator-versus-index and by-value-versus-by-reference cases did, that change is a readability decision, not a performance one, made openly rather than defended with a number that is not really there. Have a ratio in hand before touching either kind of code.

## Practice

1. ▢ Predict whether `alloc_one` or `copy_one` is faster, and whether the gap is nearer two times or twenty, then benchmark both with criterion and check.

<details markdown="1"><summary>Check</summary>

`copy_one` is faster, closer to twenty times, in this run about 29: an allocation acquires a lock and does real bookkeeping, where a copy of eight bytes never touches the heap.

</details>

2. ▢ Predict whether a fresh `.collect()` inside a loop, or extending a `Vec` declared outside it, is faster, given both produce the same length every time, then benchmark both and check.

<details markdown="1"><summary>Hint</summary>

Ask what each approach asks the allocator for on the second pass, not the first.

</details>

<details markdown="1"><summary>Check</summary>

Extending the reused buffer is faster, about 4.8 times in this run: the fresh `.collect()` allocates every pass, while the reused buffer, once grown to fit, asks for nothing again.

</details>

3. ▢ This lesson's `HashMap`-versus-sorted-`Vec` lookup was measured at eight entries. Would the vector still win at ten thousand? Say what would settle it.

<details markdown="1"><summary>Check</summary>

Not necessarily: `HashMap::get` stays roughly constant as the table grows, while `binary_search_by_key` costs more comparisons per doubling, so the gap favouring the vector narrows well before ten thousand. Settling it needs the benchmark rerun at that size, not a guess.

</details>

4. ▢ Predict whether passing a small two-field struct by value or by `&reference`, a hundred thousand times, shows a measurable difference, then benchmark both and check.

<details markdown="1"><summary>Check</summary>

No measurable difference: both land within half a percent in this run, since a value that size is passed in registers either way, and the reference only adds indirection.

</details>

5. ▢ A judgement call, not a benchmark: for each field below, say whether it should own its data, borrow it, or be a `Cow`, using lesson 27's outlives-who test and this lesson's ratios.

   - a) A path read once while its source line is still in scope, then discarded.
   - b) A path pushed into a `Vec` kept for the program's lifetime, long after the source line is gone.
   - c) A path almost always clean, occasionally needing one character replaced first.

<details markdown="1"><summary>Hint</summary>

Ask which has a source that disappears before the field is done being read, and which has a rare case that is genuinely rare.

</details>

<details markdown="1"><summary>Check</summary>

a) Borrow: the source outlives the field, so an owned copy pays the allocation cost for nothing. b) Own: the field must survive its source, which a borrow cannot do. c) `Cow`: exactly the workload the measurement above favoured, an allocation only on the rare path.

</details>

## Real-world reps

- [ ] In `logsum`, measure the per-line cost the way lesson 52's rep did, then apply one change from this lesson's catalogue, reserving capacity, borrowing instead of cloning, extending a reused buffer, or `push_str` instead of `format!`, and measure again.
- [ ] Report the ratio. If close to one, keep whichever version reads better and write why the optimisation was not worth it; if not, that sentence justifies the faster path. That note is the deliverable this stage's project row asks for.
- [ ] Tomorrow: pick one field in your project's line record or summary type and decide, using lesson 27's outlives-who test and this lesson's ratios, whether it should own, borrow, or be a `Cow`, and write the justifying sentence.

## Going further

- [Heap Allocations](https://nnethercote.github.io/perf-book/heap-allocations.html): the chapter this lesson's opening claim and its `format!` caveat come from
- [Vec: Allocation behavior](https://doc.rust-lang.org/std/vec/struct.Vec.html#allocation-behavior): what `collect` may assume about preallocating from an iterator's size hint
- [std::borrow::Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html): the type lesson 27 introduced, measured here against always owning
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
