---
title: 51. Memory Orderings
description: What an ordering actually constrains, why you cannot test one by running it, and how to check the one you chose
type: lesson
---

# Lesson 51. Memory Orderings

**Mission link:** A hand-rolled atomic protocol that has run clean a hundred times is exactly what a reviewer should distrust, and the only honest answer to "why this ordering" rests on what it promises and a tool that can check it, not on how many times the program happened to work.
**Primary source:** [std::sync::atomic::Ordering](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)
**Prerequisites:** [Lesson 36](0036-choosing-a-sharing-strategy.md), [Lesson 49](0049-checking-with-miri.md)

## Warm-up

1. ▢ Lesson 36 built a shared counter with `total.fetch_add(1, Ordering::SeqCst)`, calling `SeqCst` the strictest ordering without saying what a weaker one would cost. Does the ordering change whether an increment can be lost?

<details markdown="1"><summary>Check</summary>

No. `fetch_add` is a single indivisible read-modify-write regardless of ordering, so every increment lands; atomicity, not ordering, prevents a lost update. An ordering changes what other memory a thread is guaranteed to see around it, this lesson's subject, never lesson 36's.

</details>

2. ▢ Lesson 49 showed a genuine data race printing the correct total in six clean runs, then reported by Miri as undefined behaviour. What did that establish about what a clean run is evidence of?

<details markdown="1"><summary>Check</summary>

Nothing. A clean run, however often repeated, proves the output was right that time, not that the access pattern was sound; only Miri's report told the truth. This lesson's centrepiece is the same shape, with an ordering instead of a missing one.

</details>

## Know this

### What an ordering constrains, and why it waited

Lesson 36 shipped its counter with one ordering and deferred the choice: a wrong ordering fails silently, on some interleavings and not others, since a race between an atomic operation and its ordering is undefined behaviour, the same fault as lessons 47 and 48's raw-pointer races. An ordering is not a speed knob; any timing claim belongs to lessons 52 and 53, once measured. It constrains which other reads and writes may be observed as happening before or after it. The standard library states each of the five this way. `Relaxed`: "No ordering constraints, only atomic operations." `Release`, on a store: "When coupled with a store, all previous operations become ordered before any load of this value with `Acquire` (or stronger) ordering." `Acquire`, on a load: "When coupled with a load, if the loaded value was written by a store operation with `Release` (or stronger) ordering, then all subsequent operations become ordered after that store." `AcqRel`: "Has the effects of both `Acquire` and `Release` together: For loads it uses `Acquire` ordering. For stores it uses the `Release` ordering." `SeqCst`: "Like `Acquire`/`Release`/`AcqRel` (for load, store, and load-with-store operations, respectively) with the additional guarantee that all threads see all sequentially consistent operations in the same order."

### The failed experiment

The obvious attempt is the textbook store-load buffering test: two static counters, two hundred thousand rounds, a freshly spawned pair of threads that each store `1` into their own flag and load the other's.

```rust
static X: AtomicUsize = AtomicUsize::new(0);
static Y: AtomicUsize = AtomicUsize::new(0);
const ORDER: Ordering = Ordering::Relaxed; // or Ordering::SeqCst

let mut both_zero = 0;
for _ in 0..200_000 {
    X.store(0, Ordering::SeqCst);
    Y.store(0, Ordering::SeqCst);
    let (seen_y, seen_x) = (AtomicUsize::new(9), AtomicUsize::new(9));
    thread::scope(|s| {
        s.spawn(|| { X.store(1, ORDER); seen_y.store(Y.load(ORDER), Ordering::SeqCst); });
        s.spawn(|| { Y.store(1, ORDER); seen_x.store(X.load(ORDER), Ordering::SeqCst); });
    });
    if seen_x.load(Ordering::SeqCst) == 0 && seen_y.load(Ordering::SeqCst) == 0 {
        both_zero += 1;
    }
}
```

Both threads reading the other's flag as still zero is the reordering `Relaxed` permits and `SeqCst` forbids. With `Relaxed`, four runs of two hundred thousand rounds gave 35, 74, 109 and 131 such rounds, under a tenth of a percent, moving threefold between identical runs. With `SeqCst`, three runs gave zero every time. Read quickly that looks like proof; read honestly it is not: a signal this small and unstable is easy to miss in one run, or dismiss as noise, since no run's count predicts the next. The reason is structural: spawning and joining threads every round is itself synchronisation, leaving the pattern almost no window even when the ordering permits it. **A test built to distinguish orderings by running the program can fail to distinguish them for a reason that has nothing to do with which ordering is correct**, and that is the honest lesson: you cannot demonstrate an ordering bug by running it on one machine, especially a strongly ordered one, and a reader who sees nothing will wrongly conclude the ordering does not matter.

### The check that works

What discriminates is exploring the executions the memory model allows, not running the program differently. A publisher writes a value then a flag; a reader spins on the flag then reads the value:

```rust
static DATA: AtomicUsize = AtomicUsize::new(0);
static READY: AtomicBool = AtomicBool::new(false);

let reader = thread::spawn(|| {
    while !READY.load(Ordering::Relaxed) {}
    DATA.load(Ordering::Relaxed)
});
DATA.store(42, Ordering::Relaxed);
READY.store(true, Ordering::Relaxed);
let seen = reader.join().unwrap();
```

Both operations on `READY` are `Relaxed`, too weak: nothing stops the reader's load of `DATA` reordering ahead of its load of `READY` seeing `true`. Stable release: `saw 42`, five runs running, a shipped bug until it is not. Under `MIRIFLAGS="-Zmiri-many-seeds=0..30" cargo +nightly miri run`: fifteen of thirty seeds printed `saw 42`, fifteen the stale `saw 0`. The fix changes two words: `READY`'s store becomes `Release`, its load `Acquire`; `DATA` stays `Relaxed`, the flag's ordering doing the work. Same sweep, all thirty printed `saw 42`. Neither version crashed or printed a wrong number normally; only lesson 49's instrument, trying executions a weak processor may produce, told them apart.

### The release-acquire pattern, and what SeqCst adds

The fixed publisher is the pattern to keep, not a special case: **everything a thread writes before a `Release` store is guaranteed visible to any thread that observes that store with an `Acquire` load**. The flag carries the guarantee; the payload beneath it can stay `Relaxed`, since the flag's ordering alone establishes the happens-before edge the payload rides on. `SeqCst` adds one guarantee on top: a single total order every thread agrees on for every `SeqCst` operation, not just the publishing pair. That matters once three or more threads each run their own handoff and correctness needs them to agree on the order between handoffs; a two-thread publish never needs it. Honestly, `SeqCst` is reached for more often than programs need that guarantee, since it requires no argument; the argument for anything weaker is the rest of this lesson.

### `compare_exchange` and its two orderings

A compare-and-swap retry loop is the first place a reader names two orderings on one call, since success and failure are different operations:

```rust
fn bump_even(counter: &AtomicUsize) -> usize {
    let mut current = counter.load(Ordering::Relaxed);
    loop {
        let next = current + 2;
        match counter.compare_exchange_weak(current, next, Ordering::AcqRel, Ordering::Relaxed) {
            Ok(prev) => return prev,
            Err(actual) => current = actual,
        }
    }
}
```

The first `Ordering` covers the read-modify-write on success; the second covers the plain load on failure, so it can never be stronger than a load supports. `compare_exchange_weak` is deliberate here: the documentation says it "is allowed to spuriously fail even when the comparison succeeds, which can result in more efficient code on some platforms," and inside a loop that already retries on any `Err`, that costs one extra iteration. `compare_exchange`, the strong form, never fails spuriously, and is the one to reach for outside a retry loop, where a false negative would be a real bug. Compiled and run, five calls to `bump_even` left the counter at `10`.

### The rule for a reader who is not writing a lock-free structure

Almost nobody should be choosing among these five day to day. Use `SeqCst` until a measured bottleneck justifies something weaker, and reach for a `Mutex` or a channel before a hand-rolled atomic protocol: a lock's failure mode is a hang a watchdog catches, a wrong ordering's is what this lesson just proved cannot be seen by running the program. Lesson 36's five questions already decide whether the shared state is a single value at all, the only case an ordering choice is on the table; cite that procedure rather than repeat it. A faster ordering is not worth defending without a benchmark, lessons 52 and 53's job.

## Practice

1. ▢ Predict whether the store-load buffering test, run with `Ordering::SeqCst` throughout, ever counts a round where both threads saw the other's flag as zero, then run it several times.

<details markdown="1"><summary>Check</summary>

It does not, ever: `SeqCst`'s total order rules out that interleaving. `Ordering::Relaxed` does occasionally, under a tenth of a percent and several-fold different between runs, why one clean `SeqCst` run proves far less than the contrast against several `Relaxed` runs.

</details>

2. ▢ Predict what fraction of thirty Miri seeds read the stale value from a publisher whose flag store and load are both `Ordering::Relaxed`, then run `MIRIFLAGS="-Zmiri-many-seeds=0..30" cargo +nightly miri run` to check.

<details markdown="1"><summary>Hint</summary>

A normal release run is not the right baseline; it only ever runs one interleaving.

</details>

<details markdown="1"><summary>Check</summary>

A substantial minority: fifteen of thirty seeds, while ordinary release runs beforehand printed the published value every time. The sweep forces interleavings a normal run's scheduler happens not to pick.

</details>

3. ▢ Predict whether changing the flag's store to `Ordering::Release` and load to `Ordering::Acquire`, leaving the data `Ordering::Relaxed`, closes the gap above, then rerun the sweep.

<details markdown="1"><summary>Check</summary>

Completely: every seed reads the published value, none stale. The data needs no strong ordering of its own, since the flag's `Release`/`Acquire` pair creates the happens-before edge the data's write rides on.

</details>

4. ▢ In the `compare_exchange_weak` loop above, predict whether swapping in `compare_exchange` changes the final counter value after five calls, then make the change and run it.

<details markdown="1"><summary>Hint</summary>

The loop already retries on any `Err`; what does a spurious failure cost a loop that was retrying anyway?

</details>

<details markdown="1"><summary>Check</summary>

The final value is identical either way, `10`. The weak form can fail even when `current` matched, costing one extra iteration on the rare occasion; the strong form never pays that cost, but neither changes what the loop returns.

</details>

5. ▢ A reviewer sees a hand-rolled spin lock built from an `AtomicBool`, every operation `Ordering::Relaxed`, defended as "faster, and it passed a thousand-iteration stress test." Using this lesson's rule, what should the reviewer ask for?

<details markdown="1"><summary>Check</summary>

A benchmark showing the weaker ordering matters, since a passing stress test is the clean-run evidence this lesson showed proves nothing, plus a reason it needs a hand-rolled lock rather than `std::sync::Mutex`, whose failure mode is a hang a watchdog catches, not a silent stale read. Absent both, the ordering should be `SeqCst` and the type probably `Mutex`.

</details>

## Real-world reps

- [ ] In your multi-source summariser, find the atomic counter tracking finished sources, note which `Ordering` it needs and why, then confirm it under `MIRIFLAGS="-Zmiri-many-seeds=0..30" cargo +nightly miri run`.
- [ ] If nothing reads a worker's data because it saw a particular count, note `Ordering::Relaxed` is correct and a stronger one buys nothing; if something does rely on the count first, fix that handoff to `Release`/`Acquire`.
- [ ] Tomorrow: reproduce the store-load buffering attempt with your own run counts, and note whether they looked more or less conclusive, since that instability is the point.

## Going further

- [std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/index.html): the module overview, noting Rust's orderings match C++20's
- [AtomicUsize](https://doc.rust-lang.org/std/sync/atomic/type.AtomicUsize.html): `compare_exchange` and `compare_exchange_weak` in full, on the type this lesson used
- [Atomics](https://doc.rust-lang.org/nomicon/atomics.html): the Rustonomicon chapter behind the release-acquire idiom
- [Testing multiple different executions](https://github.com/rust-lang/miri#testing-multiple-different-executions): the Miri section defining the seed-sweep flag used above
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
