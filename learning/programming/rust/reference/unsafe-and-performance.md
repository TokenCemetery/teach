---
title: Unsafe and performance
description: The stage 7 reference sheet: what unsafe promises, the undefined-behaviour list, how each claim gets checked, and the measurement discipline
type: reference
---

# Unsafe and performance

Lookup sheet for stage 7. The question it exists to answer: **does this `unsafe` block have a sound argument, and does this speed claim have a measurement?**

## What `unsafe` grants, and the obligation it creates

| Ability | What it lets you do | Where |
|---|---|---|
| Dereference a raw pointer | Read or write through `*const T` or `*mut T`, none of which the compiler tracked for validity, alignment, non-nullness or aliasing | Lesson 47 |
| Call an unsafe function or method | Invoke an operation whose caller must uphold documented preconditions the signature cannot express | Lesson 46 |
| Implement an unsafe trait | Promise the trait's own extra invariant holds, such as `unsafe impl Send` | Lesson 46 |
| Read or write a mutable or unsafe external static | Touch global state with no compiler-enforced exclusivity | Lesson 46 |
| Access a union field, other than to assign to it | Read a field the type cannot track as the active one | Lesson 46 |

`unsafe` grants exactly these five abilities and nothing else: it does not disable the borrow checker or type checking, and a block that uses none of the five compiles to the same thing without it, plus a compiler warning that it was unnecessary. The obligation it creates in exchange is a `SAFETY:` comment naming the invariant that makes each use sound, addressed to the next reader rather than to the compiler, which stopped checking the moment the block was written.

## The undefined-behaviour list, as a checkable table

Not exhaustive, but these are the entries this stage checks by name.

| Category | What it is | How you check it |
|---|---|---|
| Dangling or misaligned access | Reading or writing through a pointer that is not backed by a live allocation, or not at an address its type may start from | Miri: `accessing memory based on pointer with alignment N, but alignment M is required`, or a dangling-reference report; a debug-build panic on the same access is a coincidence of an unrelated runtime guard, not this check |
| Pointer aliasing violation | Two overlapping accesses reach the same memory where at least one is a unique (`&mut`) borrow, however both were obtained | Miri's borrow-stack report: `attempting a read access using <tag> ..., but that tag does not exist in the borrow stack for this location`, naming the retag that created and the retag that invalidated the tag |
| Data race | Two threads touch the same memory with no lock and no atomic, and at least one access is a write | Miri: `Data race detected between (1) ... and (2) ...`; never reliably visible from a clean run in either build profile |
| Invalid value | A bit pattern the type cannot legally hold, such as a `bool` that is not `0` or `1` | Miri: `constructing invalid value of type T: encountered 0xNN, but expected a boolean` (or similar) |
| Uninitialised read | Reading `MaybeUninit` bytes, or anything built from them, before they were written | Miri: `constructing invalid value of type T: encountered uninitialized memory` |
| Broken provenance | Reinterpreting a pointer's bytes as a plain integer and back, discarding the extra information a pointer carries beyond its address | Rejected outright in a const context (`unable to turn pointer into integer`); undefined at runtime otherwise, with nothing to catch it there |
| Wrong call ABI | Calling a function through a transmuted, mismatched signature | Named on the list; not separately demonstrated in these lessons |

## What each tool actually catches

| Tool | Catches | Misses |
|---|---|---|
| The compiler, stable | Type errors, borrow errors (unchanged inside `unsafe`), and the syntactic gate on the five abilities (`E0133`, `E0499`, `E0502`, `E0793` among them) | Whether a raw pointer's target is actually valid, aligned, non-null or unaliased at the moment it is used |
| A debug build, by accident | Misalignment and null dereferences (a library-inserted panic, not a compiler proof); integer overflow; a documented `debug_assert`-style precondition on a method such as `get_unchecked` | Aliasing, data races, uninitialised reads, invalid values and provenance breaks, none of which trip a debug-only guard; a debug panic that does fire can be catching a different symptom by a different mechanism than the real bug |
| Miri | Every category on the list above, but only on the paths and interleavings a run actually takes, one execution or one seed at a time | Anything on a path a run never exercises; foreign function calls; and, by its own documentation, general soundness, since a clean Miri run is evidence about the run it made, not a proof |
| Nothing | A number that looks right | A clean run in any build profile, however many times repeated, is never evidence of soundness; a green test suite describes the inputs it contains, not the function |

## The SAFETY comment: five questions a boundary must answer

A block failing any of the first four never reaches the fifth: no ratio buys back an invariant that was never true.

| # | Question | A passing answer | A failing answer |
|---|---|---|---|
| 1 | What invariant makes this sound? | A fact about the surrounding code or its inputs that, if true, rules out the violation, statable in one sentence | "This is fine", or no fact at all, such as two lines that manufacture the very aliasing violation the block should avoid |
| 2 | Who guarantees it? | A private field plus one checked constructor, or a check that runs immediately before the operation | Nothing; the property held only by luck across however many clean runs were tried |
| 3 | Can a safe caller break it? | Every input's type plus a runtime check together rule out every bad value reaching the unsafe code | A guard enforced three functions away, invisible in the reviewed diff |
| 4 | What does a panic inside do to it? | State the invariant depends on changes only after the fallible call returns | A counter incremented before the value it is meant to count was actually written |
| 5 | What did the measurement say it bought? | A before-and-after ratio, a described workload, and the safe version kept in the crate for comparison | A speed claim with no ratio, or a ratio from a workload nobody recognises |

A comment that can only be honestly written as a paragraph of exceptions is a hope, not an invariant: keep looking for the safe version instead of writing it down.

## Memory orderings

| Ordering | Guarantees | Reach for it when |
|---|---|---|
| `Relaxed` | Atomicity only; no constraint on any other memory | The value publishes nothing else that another thread depends on |
| `Release` (store) | Everything written before this store becomes visible to any thread that `Acquire`-loads the same value | Publishing a payload behind a flag |
| `Acquire` (load) | If the value read was written by a `Release` (or stronger) store, everything before that store is now visible here | Consuming the flag above |
| `AcqRel` | `Acquire` on the load half, `Release` on the store half of one read-modify-write | A `compare_exchange` that both consumes and republishes state |
| `SeqCst` | Everything `Release`/`Acquire`/`AcqRel` give, plus one total order every thread agrees on for every `SeqCst` operation | The default; the extra guarantee matters only once three or more threads must agree on the relative order between independent handoffs |

**The idiom to keep**: pair a `Release` store on a flag with an `Acquire` load on the same flag; the data underneath can stay `Relaxed`, since the flag's ordering alone creates the happens-before edge the data rides on. Everyone else should default to `SeqCst` until a measured bottleneck justifies something weaker, and reach for a `Mutex` or a channel before a hand-rolled atomic protocol at all.

**Orderings are checked by exploring executions, not by running the program.** A store-load buffering test spawning fresh threads every round barely distinguished `Relaxed` from `SeqCst`: reproduced here, `SeqCst` gave zero forbidden outcomes across three runs of two hundred thousand rounds each, and `Relaxed` gave a small, unstable count in the tens per two hundred thousand rounds on one run, because spawning and joining threads is itself synchronisation and leaves little room for the difference to show. What actually discriminates is Miri's seed sweep against a publish-and-consume pair with no such per-round synchronisation: a `Relaxed` flag read the stale value on a substantial minority of seeds under `-Zmiri-many-seeds=0..30`, and switching the flag alone to `Release`/`Acquire` brought that to zero across the same thirty seeds. A clean run, of any kind, answers nothing here; a seed sweep against the right shape of program does.

## The measurement discipline

- **`std::hint::black_box`** treats its argument as unknown going in and observed coming out, which stops the optimiser from proving a benchmark's result is unused and deleting the work behind it. A loop whose accumulator nothing reads reports the same time as an empty closure, at any iteration count, with or without `black_box` around the arithmetic; the difference only shows once the input and the output are both wrapped.
- **A ratio, never a duration.** State what is being divided by what, the workload that produced it, and the fact that it came from one machine. A duration by itself is somebody else's clock speed and cache sizes; a ratio on a named workload is a claim another machine can attempt to reproduce, even if the exact number moves.
- **criterion 0.8.2**: a dev-dependency, `harness = false` on its `[[bench]]` target, reporting a three-figure confidence interval per benchmark, lower bound, best estimate, upper bound, rather than one number, because no two samples agree exactly. A wide interval means noise, and a ratio built on one deserves less trust than one built on a narrow interval.

**Four ways a microbenchmark lies even when built carefully:**

| Way | What happens |
|---|---|
| Unrealistic input | The workload measured is not one a real caller produces, such as querying one key a million times when real traffic varies |
| Warm cache | Repeating the same access lets an implementation serve every later call from whatever it cached, hiding the cost a cold caller actually pays |
| Constant-folded away | The optimiser proves a value never changes and removes the work regardless of intent, `black_box` included, if it is not placed on every value that must stay live |
| Local win, global loss | A change that speeds up the measured path while costing the rest of the program something it needed, such as trading time for memory the caller cannot spare |

## Allocation and copying costs

| Comparison | Ratio | Workload | Note |
|---|---|---|---|
| Heap allocation vs a plain copy | About 29 times | An eight-byte `Vec<u8>` against the same eight bytes as an array | The order of magnitude that matters most: count allocations before counting characters |
| Cloning a borrowed `&str` into an owned `String` vs borrowing it | About 66 times | A thousand calls against a roughly sixty-byte string | Own only once the field must outlive the source that borrowing cannot |
| A fresh `.collect()` per pass vs extending a `Vec` declared outside the loop | About 4.8 times | Two hundred passes, sixty-four-element chunks | The reused buffer allocates once; the fresh collect allocates every pass |
| `push_str` into a pre-sized `String` vs `format!` | About 2.1 times | Two hundred passes, five pieces | Both allocate exactly once; the gap is that `format!` compiles to one opaque call the optimiser cannot see inside, not an extra allocation |
| A sorted `Vec` with `binary_search_by_key` vs `HashMap::get` | About 3 times, the vector faster | Eight entries, built once, queried often | **Where the obvious optimisation does not pay**: hashing a key costs more than a few integer comparisons over data already sitting together at this size, though the gap narrows and can reverse well before ten thousand entries |
| An indexed loop vs an iterator's `.sum()` | Within half a percent | Ten thousand `u64` values | Not a performance decision; the iterator is not a slower abstraction here |
| Passing a small two-field struct by value vs by `&reference` | Within half a percent | A hundred thousand calls | Reaching for a reference "to avoid a copy" buys nothing once the value fits in registers, and adds indirection instead |
| An owning field vs a borrowing field in a parsed record | About 35 times | A thousand parses of a six-byte path | Lines up with the raw allocation ratio above; an owned field is an allocation paid once per value |
| `Cow` (allocates only on the rare path) vs always owning | About 4.5 times faster | Eight paths, one of eight needing a change | `Cow` earns its place exactly when the rare case is genuinely rare in the traffic the function sees |

Every ratio above came from one run, one machine, one named workload; a different input shape or machine can move the number without moving which side of the table it lands on.

## Deliberately not here

| Topic | Where it went |
|---|---|
| `divan`, `dhat` | Named once each, in lessons 52 and 53, for benchmarking and heap profiling respectively; neither is taught |
| Whether Tree Borrows and Stacked Borrows agree in general | Lesson 49 tested both against its own two examples and found no divergence there; that is not a claim the two models agree everywhere, only that this stage did not turn up a split |
| A profiler's view of a whole running program | A ratio answers "is X faster than Y on this workload", never "where does this program actually spend its time"; that is a profiler's question, not a benchmark's |
| FFI and calling into C | Named as a reason a raw pointer exists at all (lesson 47's mission); never demonstrated, since Miri cannot see across that boundary either |
| Manual `Pin` projection, writing a `Future` by hand for a self-referential type, and building a `Waker` from a raw pointer and a vtable | Named as stage 7 material by the async reference sheet; none of this stage's nine lessons builds one, so the thread is still open rather than closed here |
