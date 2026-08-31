---
title: 30. Benchmarks You Can Trust
description: b.Loop, repeated runs and benchstat, because one number from one run is not a measurement
type: lesson
---

# Lesson 30. Benchmarks You Can Trust

**Mission link:** "Optimises from a profile and proves the win with benchstat" is the stage 5 exit criterion. This is the proving half, and most benchmarks people write do not prove anything.
**Primary source:** [`testing` package — Benchmarks](https://pkg.go.dev/testing#hdr-Benchmarks)
**Prerequisites:** [Lesson 28](0028-table-driven-tests.md)

## Warm-up

1. ▢ Where does a fuzz failure get written, and why commit it?

<details markdown="1"><summary>Check</summary>

`testdata/fuzz/FuzzName/`. Committed, it joins the seed corpus, so every plain `go test` replays it — the finding becomes a regression test for free.

</details>

2. ▢ What does `t.Helper()` change about a failure?

<details markdown="1"><summary>Check</summary>

The reported line points at the caller rather than at the line inside the helper, so the output names the test that actually failed.

</details>

## Know this

A benchmark lives beside the tests and runs on demand:

```go
func BenchmarkParse(b *testing.B) {
    for b.Loop() {
        Parse("1h30m")
    }
}
```

```bash
go test -bench=BenchmarkParse -benchmem ./...
```

`b.Loop()` arrived in [Go 1.24](https://go.dev/doc/go1.24#testing) and is now the form to write. It replaces `for i := 0; i < b.N; i++`, and it fixes two long-standing problems:

- **Setup and cleanup run once per `-count`,** not once per timing iteration, so expensive fixtures no longer need `b.ResetTimer` gymnastics.
- **Parameters and results are kept alive,** so the compiler cannot delete the call as dead code.

That second point is why so many old benchmarks report impossible numbers. With `b.N` and a result nobody uses, the optimiser is entitled to remove the work entirely and you measure an empty loop. The traditional defence was assigning to a package-level sink variable; `b.Loop` makes it unnecessary.

### The output

```text
BenchmarkParse-10    	 8123456	       147.2 ns/op	      32 B/op	       1 allocs/op
```

`-10` is `GOMAXPROCS`. Then iterations, nanoseconds per operation, and — with `-benchmem` — bytes and allocations per operation. **Allocations per operation is usually the number that matters**, because it is stable across machines and it is what you can actually act on. Nanoseconds move with the CPU, the thermal state and whatever else is running.

### One run is not a measurement

A single number tells you nothing about variance. Run it repeatedly and compare with `benchstat`:

```bash
go test -bench=. -benchmem -count=10 ./... > old.txt
# make the change
go test -bench=. -benchmem -count=10 ./... > new.txt
benchstat old.txt new.txt
```

`benchstat` — from `golang.org/x/perf/cmd/benchstat` — reports the difference with a confidence interval and tells you when the change is statistically indistinguishable from noise. That verdict is the deliverable. "It went from 147ns to 141ns" is not a result; it is one sample from a noisy distribution.

Reduce the noise you control: close other applications, disable turbo or plug in the laptop, and never benchmark inside a container sharing a busy host. A quiet machine and `-count=10` beats a clever methodology on a busy one.

### Sub-benchmarks

`b.Run` mirrors `t.Run`, which is how you measure across input sizes:

```go
for _, n := range []int{10, 1000, 100000} {
    b.Run(strconv.Itoa(n), func(b *testing.B) {
        data := makeData(n)          // once per -count, thanks to b.Loop
        for b.Loop() {
            Process(data)
        }
    })
}
```

Scaling behaviour is more informative than any single point. A function that is fine at 10 and quadratic at 100,000 is the bug you are looking for, and one benchmark size cannot show it.

### What benchmarks cannot tell you

A microbenchmark measures one function on warm caches with no contention, no GC pressure from the rest of the program, and no network. Real gains and real regressions frequently live in the parts it excludes.

So the order is: **profile the whole system to find where the time goes, benchmark the specific function to prove the fix.** Reversing it produces a heavily optimised function that was never the problem — the most common way engineering time gets spent on nothing.

## Practice

1. ▢ Why might `for i := 0; i < b.N; i++ { Parse("3h") }` report a suspiciously small number?

<details markdown="1"><summary>Check</summary>

The result is unused, so the compiler may eliminate the call entirely and you time an empty loop.

`b.Loop()` keeps the call's parameters and results alive, which is the reason to switch. On an older toolchain, assign the result to a package-level variable so it cannot be proven dead.

</details>

2. ▢ You changed a function and the benchmark went from 147 ns/op to 141 ns/op. What have you shown?

<details markdown="1"><summary>Check</summary>

Nothing yet. That is a 4% difference from single runs, well inside the noise of most machines.

Run both with `-count=10` and let `benchstat` decide. It will report the change with a confidence interval, and often the answer is that the two are indistinguishable — which is a real and useful result.

</details>

3. ▢ Which metric is most stable across different machines?

   - a) Nanoseconds per operation for the call
   - b) Total iterations the benchmark completed
   - c) Allocations per operation from `-benchmem`
   - d) Wall-clock seconds the benchmark ran

<details markdown="1"><summary>Check</summary>

**c)** Allocations per operation from `-benchmem`.

Allocation count is a property of the code, not of the CPU, so it reproduces on a colleague's laptop and in CI. Timing moves with clock speed, thermal state and neighbours; iteration count and wall-clock are just the framework hitting its time budget.

It is also the number you can act on directly — Lesson 32 is about removing allocations.

</details>

4. ▢ Why profile before benchmarking rather than the other way round?

<details markdown="1"><summary>Check</summary>

A benchmark measures the function you already suspect. A profile tells you which function to suspect — and intuition about where time goes is wrong often enough that the profile regularly points somewhere nobody proposed.

Optimising a correctly-benchmarked function that accounts for 2% of runtime is a real outcome of skipping this order, and the work is unrecoverable once done.

</details>

5. ▢ Interleaving Lesson 19: you benchmark a `RWMutex` change and it looks slightly better. What is missing?

<details markdown="1"><summary>Check</summary>

Concurrency. A lock benchmarked from one goroutine measures the uncontended path, which is exactly where `RWMutex`'s extra bookkeeping shows up as pure cost and its benefit cannot appear.

Use `b.RunParallel` — or a benchmark that starts a realistic number of goroutines — so contention exists at all. Lock changes justified by single-goroutine benchmarks are a recurring way to make a service slower with evidence.

</details>

## Real-world reps

- [ ] Write a benchmark with `b.Loop`, run it with `-benchmem -count=10`, and put the output through `benchstat` against itself. Seeing the noise floor of your own machine is worth doing once.
- [ ] Take a function that concatenates strings in a loop, benchmark it, switch to `strings.Builder`, and prove the win with `benchstat`. The allocation count will move more than the time.
- [ ] Tomorrow: install `benchstat` (`go install golang.org/x/perf/cmd/benchstat@latest`) if you have not, so it is there when you need it.

## Going further

- [`testing` package — Benchmarks](https://pkg.go.dev/testing#hdr-Benchmarks)
- [`benchstat`](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat)
- [Go 1.24 `testing.B.Loop`](https://go.dev/doc/go1.24#testing)
- [Toolchain Commands](../reference/toolchain-commands.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
