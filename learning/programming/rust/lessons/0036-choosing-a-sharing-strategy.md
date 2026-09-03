---
title: 36. Choosing a Sharing Strategy
description: The failures that follow from choosing by habit, and the questions that pick the strategy from the data instead
type: lesson
---

# Lesson 36. Choosing a Sharing Strategy

**Mission link:** This closes the stage: a sharing strategy chosen from what the data needs, not from whichever type came to hand first.
**Primary source:** [std::sync](https://doc.rust-lang.org/std/sync/index.html)
**Prerequisites:** [Lesson 33](0033-mutex-rwlock-and-poisoning.md), [Lesson 35](0035-channels.md)

## Warm-up

1. ▢ A thread panics while holding a `Mutex` guard. What does the next `lock()` return, and what does `clear_poison` change about that?

<details markdown="1"><summary>Check</summary>

`lock()` returns an `Err` whose `Display` is `poisoned lock: another task failed inside`, though the data is still reachable via that error's `into_inner`. `clear_poison` clears the flag, so the next `lock()` succeeds.

</details>

2. ▢ `std::sync::mpsc` gives every channel exactly one receiver. What has to change to let two threads each consume their own share of the messages?

<details markdown="1"><summary>Check</summary>

Std's channel cannot: a second `Receiver` for the same channel needs a multi-consumer implementation, and `std::sync::mpmc` for that is still unstable. A separate crate is the only route today.

</details>

## Know this

### The lost update, and how wrong it actually is

Two threads, twenty thousand iterations each, read-then-write against a shared `Arc<Mutex<usize>>` as **separate** lock acquisitions:

```rust
for _ in 0..n {
    let seen = *total.lock().unwrap();
    *total.lock().unwrap() = seen + 1;
}
```

That compiles and completes every time, which is the trap. Across a hundred runs, expecting forty thousand: **wrong in one hundred of one hundred**, the first wrong run reading 32009, the worst reading 22437, a loss of nearly half the increments. A separate set of fifty runs of the same code, on the same release build, disagreed in the one way that matters: **wrong in forty-seven of fifty**, so three runs came out exactly right, with a worst total of 13915. Both sets are the lesson. The loss ranges from a handful of increments to two thirds of them, and the failure rate itself moves, so a "close enough" test gambles on a number nobody controls, and a suite that happens to catch the passing runs reports success.

The bug is the gap between the two acquisitions: nothing stops the other thread reading the same `seen` and writing the same `seen + 1` while this guard is dropped and reacquired. Two fixes close it. Hold one guard across the read and write:

```rust
let mut guard = total.lock().unwrap();
*guard += 1;
```

Zero of a hundred wrong. Or replace `Mutex<usize>` with an `AtomicUsize` and a single `fetch_add`:

```rust
total.fetch_add(1, Ordering::SeqCst);
```

Also zero of a hundred wrong. `fetch_add` is what I would ship: one call, so a later edit cannot split it back into two, whereas the held guard still relies on nobody adding a second `lock()` beside it.

### The deadlock, observed as a hang

Two mutexes, `a` and `b`, locked in opposite order by two scoped threads, each sleeping fifty milliseconds between its acquisitions:

```rust
s.spawn(|| {
    let _ga = a.lock().unwrap();
    thread::sleep(Duration::from_millis(50));
    let _gb = b.lock().unwrap();
});
s.spawn(|| {
    let _gb = b.lock().unwrap();
    thread::sleep(Duration::from_millis(50));
    let _ga = a.lock().unwrap();
});
```

Under a six-second watchdog: **hung in three of three attempts**, no output, no panic, no exit code. A deadlock is silence, not an error the runtime reports, and timing the run out is the only way to see it.

The sleep is not padding: it widens the window where each thread holds one lock while reaching for the other, so the cycle forms every time. The same code without it, ten attempts under a three-second watchdog: **zero of ten hung**, since each thread usually clears both locks before the other takes the first. That is why the bug survives testing: the same mistake passes a suite with no contention, and only shows itself once two call sites are slow or busy enough to overlap. Two honest fixes: a global lock order, always `a` before `b` everywhere, or never holding two locks at once, copying data out first if needed. The second is easier to enforce in review, visible inside one function, where a global order needs checking against every other call site touching the same locks.

### Atomics as the answer to a shared counter

`AtomicUsize` with `fetch_add`, `load` and `store` answers the case above: one number, updated from more than one thread, no `Mutex` needed. `Ordering::SeqCst`, the strictest ordering, is the only one used here; which ordering is correct is a real question with real performance consequences, settled in stage 7. The design point is narrower than "atomics are faster": **an atomic replaces a lock only for a single value**. Once two numbers must change together, or the shared state is a structure rather than a scalar, an atomic no longer applies, and two atomics instead of one lock only trades a lost update for two fields disagreeing at different instants.

### One-time initialisation

Read-only state built once, lazily, before first use needs no lock once built, only a guarantee it is built exactly once. `LazyLock` in a `static` builds its value from a closure on first access:

```rust
static SETTINGS: LazyLock<Vec<&'static str>> = LazyLock::new(|| {
    println!("initialising once");
    vec!["alpha", "beta"]
});
```

Verified: the closure's `println!` appears exactly once though `SETTINGS` is read twice. `OnceLock` gives the same guarantee without the closure, for a value not known until a runtime event supplies it:

```rust
static NAME: OnceLock<String> = OnceLock::new();
NAME.set(String::from("first"));   // Ok
NAME.set(String::from("second"));  // Err, first value kept
```

Verified: the first `set` returns `Ok`, the second `Err`, and `get` yields `"first"`. This replaces a `Mutex<Option<T>>` checked and filled by hand, taking a lock on every read forever after just to check a flag that never changes again.

### The decision, as questions rather than a table

Five questions, asked in order, turn the stage's eight lessons into one procedure:

- **Does the work finish inside this function?** If so, `thread::scope` needs none of the machinery below: no `Arc`, no lock, no lifetime, since the borrowed data outlives the scope ([Lesson 30](0030-scoped-threads.md)).
- **Does the data change after start-up?** If not, `Arc` shares ownership of it ([Lesson 31](0031-shared-ownership.md)), or `OnceLock`/`LazyLock` build it lazily as above. If it does change, a lock or an atomic is the honest tool.
- **Is it one value, or a structure?** A single value only ever updated is what an atomic is for. A structure, or a value read and acted on before being written, needs a `Mutex` or `RwLock` ([Lesson 33](0033-mutex-rwlock-and-poisoning.md)) so the step happens under one guard.
- **Is the read-to-write ratio lopsided?** Mostly reads, rare writes, is what `RwLock` is for; even reads and writes gain nothing over a plain `Mutex`.
- **Does ownership need to move rather than be shared?** A value produced by one thread and consumed by exactly one other is what a channel ([Lesson 35](0035-channels.md)) says honestly; a `Mutex` around the same handoff still compiles but hides it as shared state.

Interior mutability ([Lesson 32](0032-interior-mutability.md)) and `Send`/`Sync` ([Lesson 34](0034-send-and-sync.md)) sit underneath these answers rather than being a sixth question: they explain why the compiler accepts or rejects the tool each answer points to, not which tool to pick.

### Three crates, named once

**`rayon`**, version 1.12.0, over half a billion downloads on crates.io, checked rather than run since no dependency belongs in this stage. It turns `.iter()` into `.par_iter()` and would do this stage's multi-file summarise in about three lines, exactly why it is not taught first: hiding the decision is only safe once it has been made by hand.

**`crossbeam-channel`**, version 0.5.16, well over half a billion downloads. Its algorithm became `std::sync::mpsc`'s implementation, but the crate still offers what std's channel does not: more than one `Receiver` on one channel, filling the gap `std::sync::mpmc` leaves while unstable.

**`parking_lot`**, version 0.12.5, over a billion downloads. It offers a `Mutex` and `RwLock` that never poison, for when a panicked lock should keep working rather than carry a flag forward. Std's poisoning comes first because that convenience is a good trade only once its cost is understood well enough to call it unwanted.

## Practice

1. ▢ Two threads update a shared total with `let seen = *total.lock().unwrap(); *total.lock().unwrap() = seen + 1;` in a loop. Predict: does this ever land on the right total, and would a test asserting the total is merely close pass?

<details markdown="1"><summary>Check</summary>

It compiles and runs every time, and could land on the right total by chance, but across a hundred runs it was wrong in all one hundred, by an amount ranging from small to nearly half the total. A "close enough" assertion would pass or fail depending on how much was lost that run; asserting the exact total fails reliably instead, which is the test worth having.

</details>

2. ▢ Two threads both lock mutex `x` and then mutex `y`, in that same order, never the reverse. Will this deadlock the way the lesson's example did?

<details markdown="1"><summary>Hint</summary>

The deadlock in this lesson needed a cycle: each thread waiting on a lock the other one held.

</details>

<details markdown="1"><summary>Check</summary>

No. A consistent order cannot cycle: whichever thread reaches `x` first proceeds to `y` uncontended, and the second thread simply waits its turn. The opposite-order case deadlocked because each thread held what the other wanted.

</details>

3. ▢ Predict the three results of calling `NAME.set(String::from("first"))`, then `NAME.set(String::from("second"))`, then `NAME.get()`, on a fresh `static NAME: OnceLock<String>`.

<details markdown="1"><summary>Check</summary>

The first `set` returns `Ok(())`, the second returns `Err` carrying the rejected value back, and `get` returns `Some("first")`. `OnceLock` accepts exactly one write and keeps it.

</details>

4. ▢ A summariser spawns one thread per input file and needs combined counts once every thread finishes. Using the five questions, decide whether it needs an `Arc<Mutex<_>>` around a shared totals structure at all.

<details markdown="1"><summary>Hint</summary>

Ask the first question before the rest: does each thread's work finish before the totals are needed?

</details>

<details markdown="1"><summary>Check</summary>

It does not. Each file's work finishes inside its own thread, so the first question already answers this: use `thread::scope`, return each thread's own partial summary from `join`, and combine the partials afterwards in the calling thread. Nothing is shared while mutable, so nothing can be lost or deadlocked.

</details>

5. ▢ A reviewer sees `Arc<Mutex<Config>>` around a configuration struct built once at start-up and never written again. What should they ask, and what would you suggest instead?

<details markdown="1"><summary>Check</summary>

Whether `Config` changes after start-up. If not, the `Mutex` buys nothing but a lock every reader takes for no reason: `Arc<Config>` alone shares ownership without it, and if the value must be built lazily, `OnceLock` or `LazyLock` gives that without a lock surviving into every later read.

</details>

## Real-world reps

- [ ] Reproduce the lost update and the deadlock yourself, with your own run counts, and note anywhere your numbers differ from this lesson's.
- [ ] Give `logsum` a mode that summarises several files at once and combines the partial summaries, choosing the strategy with the five questions rather than the first type that compiles, and write the chosen strategy down next to the question that decided it.
- [ ] Tomorrow: find one `Arc<Mutex<_>>` or `Arc<RwLock<_>>` in code you can read and run the five questions against it. Write down whether it survives, or should be something simpler.

## Going further

- [std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/index.html): every atomic type and operation beyond `fetch_add`
- [OnceLock](https://doc.rust-lang.org/std/sync/struct.OnceLock.html): one-time initialisation without a closure
- [LazyLock](https://doc.rust-lang.org/std/sync/struct.LazyLock.html): the closure-based counterpart used above
- [Fearless Concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html): the chapter this stage compresses, worth reading whole now its pieces are in place
- [Sharing and threads](../reference/sharing-and-threads.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
