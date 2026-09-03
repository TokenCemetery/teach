---
title: 52. Measuring Before Optimising
description: How to get a number you can defend, what the compiler does to a benchmark that measures nothing, and what a measurement cannot tell you
type: lesson
---

# Lesson 52. Measuring Before Optimising

**Mission link:** A senior engineer is regularly asked whether a change is worth the risk it adds, and the only honest answer rests on a measured number rather than one guessed from the shape of the code.
**Primary source:** [Getting Started - Criterion.rs Documentation](https://bheisler.github.io/criterion.rs/book/getting_started.html)
**Prerequisites:** [Lesson 22](0022-trait-bounds-and-generic-functions.md), [Lesson 40](0040-blocking-is-a-bug.md)

## Warm-up

1. ▢ Lesson 22 showed a generic function is monomorphised anew in the caller's own crate rather than compiled once elsewhere. A closure written directly in a `benches/` file, versus a plain function called from a separate crate, gives the compiler different amounts of information about whether its result is used. Which is easier to optimise away by accident?

<details markdown="1"><summary>Check</summary>

The closure in the benchmark file: it and its caller compile together, so the compiler sees the result is discarded and removes the work behind it, whereas a call across a crate boundary is opaque and normally survives unused. This is why the loop optimised away below is written inline, not behind a function call.

</details>

2. ▢ Lesson 40 established that a blocking-call stall is noticed by observing behaviour, not confirmed by reading the call. If two people disagree about which of two implementations is faster, and neither has run either one, whose opinion should the codebase trust?

<details markdown="1"><summary>Check</summary>

Neither, until one of them runs both under the same conditions: a claim about speed is as unverifiable by inspection as a claim about a stall, since both are facts about execution, not the source text.

</details>

## Know this

### The benchmark that measures nothing

A loop whose result nothing reads has no reason to run, and an optimising compiler that can see the whole loop will remove it. Written as a criterion benchmark, the mistake looks entirely reasonable:

```rust
fn measures_nothing(c: &mut Criterion) {
    c.bench_function("measures_nothing", |b| {
        b.iter(|| {
            let mut acc: u64 = 0;
            for i in 0..1000u64 {
                acc = acc.wrapping_add(i.wrapping_mul(2654435761));
            }
        });
    });
}
```

Nothing reads `acc`, so the compiler deletes the whole body: the reported time matched an empty closure's, even after raising the bound from a thousand iterations to a million, the tell that nothing is running. `std::hint::black_box` fixes it, treating the input as unknown and the output as observed:

```rust
fn measures_the_loop(c: &mut Criterion) {
    c.bench_function("measures_the_loop", |b| {
        b.iter(|| {
            let mut acc: u64 = 0;
            for i in 0..1000u64 {
                acc = acc.wrapping_add(black_box(i).wrapping_mul(2654435761));
            }
            black_box(acc);
        });
    });
}
```

Measured back to back, `measures_the_loop` reported a per-iteration time roughly a thousand times that of `measures_nothing`: the ratio of the loop's honest cost to a closure with nothing left inside it, and the size of the lie the first version told silently, with no wrong-looking output. `std::hint::black_box` was stabilised in Rust 1.66.0, whose release notes describe adding `core::hint::black_box` for exactly this purpose: a best-effort hint, not a barrier the optimiser must respect.

### Setting up criterion 0.8.2

Criterion is a dev-dependency with its own harness disabled, so criterion's `main` runs instead of the standard one:

```toml
[dev-dependencies]
criterion = "0.8.2"

[[bench]]
name = "measuring"
harness = false
```

`benches/measuring.rs` groups its functions with `criterion_group!`, hands the group to `criterion_main!`, and each benchmark calls `b.iter` with a closure:

```rust
use criterion::{criterion_group, criterion_main, Criterion};
use std::hint::black_box;

criterion_group!(benches, measures_nothing, measures_the_loop);
criterion_main!(benches);
```

Criterion 0.8.2 still exposes its own `black_box` but marks it deprecated in favour of the standard library's, hence the direct import above. `cargo bench` compiles in release mode, samples, and prints each benchmark as three figures rather than one. Criterion's documentation explains them: "This shows a confidence interval over the measured per-iteration time for this benchmark. The left and right values show the lower and upper bounds of the confidence interval respectively, while the center value shows Criterion.rs' best estimate of the time taken for each iteration of the benchmarked routine." No two samples agree exactly, so one figure would claim a precision the measurement lacks; a wide interval means noise, and its ratio deserves less trust than one from a narrow interval.

### The counterintuitive result, reproduced

The usual mental model says reserving a vector's capacity before pushing matters more as the workload grows. Measuring says otherwise:

```rust
fn push_no_reserve(n: usize) -> Vec<u64> {
    let mut v = Vec::new();
    for i in 0..n { v.push(i as u64); }
    v
}

fn push_with_reserve(n: usize) -> Vec<u64> {
    let mut v = Vec::with_capacity(n);
    for i in 0..n { v.push(i as u64); }
    v
}
```

Benchmarked with the input and the returned vector both wrapped in `black_box`, on one machine, reserving ahead of time was about **two and a half times** faster at eight elements and about **one and a half times** faster at ten thousand, each ratio being the no-reserve time divided by the with-reserve time at that size. The first few repeats disagreed by a wide margin before settling, worth noticing on its own: a nanosecond-scale benchmark run once is not enough to trust. The direction held throughout: the relative payoff shrank as the workload grew, the opposite of the intuition that reserving matters more at scale, and nothing about reading the two functions predicted which way it would move.

### What makes a measurement worth quoting

A number is only as useful as the conditions attached to it: a workload precise enough to rebuild, such as "pushing zero to ten thousand `u64` values into a freshly allocated vector" rather than "some pushes"; a comparison rather than a bare absolute, since a ratio survives a change of hardware where a lone number does not; the same machine for both sides; and a stated sense of how much the numbers moved between repeats, since the noise seen above before it settled is exactly what an unrepeated ratio hides. Even done carefully, a microbenchmark still lies in four ways: an unrealistic input, a cache left warm when the real caller would hit it cold, a value the optimiser proves constant and folds away regardless of `black_box`, and a change that helps the benchmark while hurting the program, say by trading time for memory the rest of it needed.

### What a measurement cannot tell you

A benchmark answers exactly the question it was built to ask, and no other. It cannot tell you where time goes inside a larger, real run, since summing isolated per-iteration costs says nothing about how often each function runs in practice or what else the program does meanwhile; that is a profiler's question. It cannot tell you whether the path measured matters at all: a function made three times faster is worth nothing if it is a negligible share of total running time. Two tools answer questions this lesson does not: `divan`, another statistics-driven benchmarking harness, and `dhat`, a heap profiler reporting where allocations happen rather than where time goes. Neither is taught here; a profiler's output is machine-specific in a way a ratio is not.

### The rule

No optimisation lands without a before-and-after ratio and a note saying what workload produced it. A change nobody measured is a guess wearing the confidence of a fact: the unmeasured benchmark above looked like evidence of speed, and the unmeasured intuition about reserving capacity pointed the wrong way as the workload grew. This is why this stage has not quoted a single timing: a duration tells the next reader nothing they can rebuild, while a ratio tied to a described workload is a claim someone else can verify.

## Practice

1. ▢ Predict whether raising the loop bound in `measures_nothing` from a thousand iterations to a million changes the reported time by roughly a thousandfold, then run both and compare.

<details markdown="1"><summary>Check</summary>

It does not change appreciably: the reported time stayed close to an empty closure's at both bounds, since the compiler removes the whole loop either way, having proven the accumulator is never read. A running loop would show a thousandfold rise in reported time to match; its absence is the evidence that nothing runs at all.

</details>

2. ▢ Predict whether the relative payoff of `push_with_reserve` over `push_no_reserve` keeps shrinking, flattens out, or starts growing again at one hundred thousand elements, then add that size and measure it.

<details markdown="1"><summary>Hint</summary>

`Vec` roughly doubles its capacity each time it runs out, so compare how many reallocations happen between eight and ten thousand elements against ten thousand and a hundred thousand.

</details>

<details markdown="1"><summary>Check</summary>

No single prediction is correct here: a trend measured at two sizes does not entitle you to assume a third, and only running the larger size tells you whether this machine's ratio kept shrinking, flattened, or reversed.

</details>

3. ▢ Predict what `cargo bench` does if the `[[bench]]` entry for a criterion benchmark is missing `harness = false`, then try it.

<details markdown="1"><summary>Hint</summary>

The default harness is the same one `cargo test` uses, and looks for functions marked `#[test]` or `#[bench]`, neither of which criterion's macros produce.

</details>

<details markdown="1"><summary>Check</summary>

Nothing errors and nothing benchmarks: the default harness takes over, finds no `#[test]` or `#[bench]` functions, and reports `running 0 tests` followed by `test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out`, silently skipping every benchmark criterion defined. A clean-looking result here proves nothing ran at all.

</details>

4. ▢ A judgement call, not a run: a change makes a five-element input three times faster in a microbenchmark. Does that alone justify merging it?

<details markdown="1"><summary>Check</summary>

No. A ratio only describes the workload measured, and this lesson's reserve example moved by a different amount at two sizes; without knowing whether five-element inputs are common, or whether this path is a meaningful share of running time, the ratio alone cannot justify the change.

</details>

5. ▢ A benchmark for a lookup function runs in a loop that queries the same single key a million times. Which of the four ways a microbenchmark lies does this risk, and why?

<details markdown="1"><summary>Check</summary>

The warm cache: repeating one key means every lookup after the first can be served from whatever the implementation cached along the way, so the benchmark measures the friendliest access pattern and says nothing about a caller whose keys vary or whose cache is cold.

</details>

## Real-world reps

- [ ] In your project, write a criterion benchmark that feeds your line parser a fixed, described input, such as one thousand lines cycling through your format's record kinds, and report its per-line cost as a ratio against one deliberate variation, such as borrowing the line instead of owning it.
- [ ] Pick one change already in your project made "for performance" without a benchmark, add the criterion benchmark it should have shipped with, and record the ratio and workload next to the change.
- [ ] Tomorrow: rerun this lesson's eight-versus-ten-thousand-element comparison on your own machine and check whether the payoff still shrinks with scale there, since the direction need not transfer.

## Going further

- [Command-Line Output - Criterion.rs Documentation](https://bheisler.github.io/criterion.rs/book/user_guide/command_line_output.html): every field criterion prints
- [black_box in std::hint](https://doc.rust-lang.org/std/hint/fn.black_box.html): the function this lesson's fix relies on, and its limits
- [Announcing Rust 1.66.0](https://blog.rust-lang.org/2022/12/15/Rust-1.66.0/): the release notes confirming when `black_box` was stabilised
- [The Rust Performance Book](https://nnethercote.github.io/perf-book/introduction.html): a deeper, ongoing reference than one lesson can cover
- [Unsafe and performance](../reference/unsafe-and-performance.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
