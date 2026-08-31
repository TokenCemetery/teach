---
title: 32. Escape Analysis and Allocation
description: Why a value lands on the heap, how to ask the compiler, and which fixes actually pay
type: lesson
---

# Lesson 32. Escape Analysis and Allocation

**Mission link:** Cutting allocations with evidence is a stage 5 success criterion. Escape analysis is the mechanism underneath the `allocs/op` number, and the compiler will tell you its reasoning.
**Primary source:** [Go FAQ: Stack or heap?](https://go.dev/doc/faq#stack_or_heap)
**Prerequisites:** [Lesson 31](0031-reading-a-pprof-profile.md), [Lesson 2](0002-value-semantics-and-pointers.md)

## Warm-up

1. ▢ What does a large `cum` with a near-zero `flat` tell you about a function?

<details markdown="1"><summary>Check</summary>

It is a wrapper — the cost is in what it calls. Optimising it does nothing; follow the callees.

</details>

2. ▢ Which heap view do you open for a suspected leak?

<details markdown="1"><summary>Check</summary>

`inuse_space` — memory currently held. `alloc_space` includes everything already collected and is the view for allocation *rate*.

</details>

## Know this

Go has no `new` versus stack distinction in the source. **The compiler decides** where a value lives, using **escape analysis**: if it can prove a value does not outlive the function that created it, the value goes on the stack, which costs nothing to allocate and nothing to collect. If it cannot prove that, the value escapes to the heap.

This is why Lesson 2's advice — take a pointer when you need to mutate — does not carry a hidden performance rule. `&Config{}` inside a function that does not let it escape is a stack allocation.

### Asking the compiler

```bash
go build -gcflags='-m' ./... 2>&1 | grep escapes
```

```text
./main.go:14:9: &User{...} escapes to heap
./main.go:22:2: moved to heap: buf
./main.go:31:12: parameter w does not escape
```

`-m -m` (twice) gives the reasoning chain, which is verbose and occasionally the only way to understand a surprising result. This is the ground truth: not a heuristic you memorise, but a question you ask about a specific line.

### What makes a value escape

| Cause | Why |
|---|---|
| Returning a pointer to a local | it outlives the frame by definition |
| Storing a pointer in something that escapes | a struct field, a global, a slice that escapes |
| Assigning to an interface | the interface holds a pointer, and the callee is unknown |
| Capturing by a closure that escapes | the closure outlives the frame |
| A size the compiler cannot bound | `make([]byte, n)` with a variable `n` above a threshold |
| Passing to a function it cannot see through | an unknown implementation, so it must assume the worst |

The interface row is the one that surprises people. `fmt.Println(x)` boxes `x` into an `any`, and the compiler cannot see what `Println` does with it — so `x` escapes. That is why a debug print inside a hot loop can change a benchmark's allocation count, and why removing a log line sometimes "makes it faster".

### Fixes that actually pay

**Preallocate when you know the size.** This is the highest-value, lowest-risk change there is:

```go
out := make([]Result, 0, len(in))   // one allocation, not log₂(n) of them
for _, v := range in {
    out = append(out, convert(v))
}
```

Growing a slice by `append` reallocates and copies repeatedly. Giving `make` the capacity removes all of it. The same applies to `make(map[K]V, n)` and to `strings.Builder.Grow(n)`.

**Reuse buffers on a hot path.** `sync.Pool` holds temporary objects between uses. It is genuinely effective for large per-request buffers, and it is easy to misuse: pooled objects must be reset before reuse, the pool is cleared by the garbage collector, and pooling small objects usually costs more than it saves. Reach for it with a profile in hand, not before.

**Avoid interface boxing in the hottest loop.** Concrete types where the type is known. This is a real effect and a small one — do not restructure a program for it.

**Do not pass large structs by pointer to avoid the copy without measuring.** The pointer can force a heap allocation that the copy did not need, making it slower. This is the exact case where the intuition from other languages is inverted.

### Keeping it in proportion

Allocation reduction is worth doing where the profile says allocation is the problem — a service where GC is a visible share of CPU, a function called millions of times. It is not worth doing everywhere, and the code it produces is generally less readable.

The order is unchanged: profile ([Lesson 31](0031-reading-a-pprof-profile.md)), then change, then prove with `benchstat` ([Lesson 30](0030-benchmarks-you-can-trust.md)). "Fewer allocations" is not automatically faster — the Go 1.26 garbage collector is significantly cheaper than older ones, and a change that trades clarity for a 2% allocation reduction is a bad trade.

## Practice

1. ▢ Does `p := &User{}` inside a function always allocate on the heap?

<details markdown="1"><summary>Check</summary>

No. If the compiler can prove `p` does not outlive the function, the `User` goes on the stack and the pointer is a stack address.

It escapes when `p` is returned, stored somewhere that escapes, captured by an escaping closure, or passed into a function the compiler cannot see through. `go build -gcflags=-m` answers it for the specific line rather than in general.

</details>

2. ▢ Why can adding `fmt.Println(x)` to a loop change the allocation count?

<details markdown="1"><summary>Check</summary>

`Println` takes `...any`, so `x` is boxed into an interface and the compiler cannot prove what happens to it — `x` escapes to the heap, and so does the `[]any` holding it.

This is worth knowing for two reasons: debug prints distort the benchmark you are reading, and it explains the otherwise magical effect of deleting a log line from a hot path.

</details>

3. ▢ Which change most reliably removes allocations?

   - a) Passing large structs by pointer instead of value
   - b) Preallocating a slice with the known final capacity
   - c) Replacing concrete parameter types with interfaces
   - d) Adding a `sync.Pool` in front of every allocation

<details markdown="1"><summary>Check</summary>

**b)** Preallocating a slice with the known final capacity.

It turns a series of grow-and-copy reallocations into one, it is a one-line change, and it never makes the code harder to read. Option a can force a heap allocation the copy avoided, c adds boxing, and d is a targeted tool that costs more than it saves on small objects.

</details>

4. ▢ How do you find out why a specific variable escaped?

<details markdown="1"><summary>Check</summary>

`go build -gcflags='-m -m'` and read the chain for that line. The doubled flag prints the reasoning, not just the conclusion — which value it flowed into, and why that one escapes.

Guessing from the table of causes is a starting point; the compiler's own explanation is the answer, and it changes between releases as the analysis improves.

</details>

5. ▢ Interleaving Lesson 3: how does slice capacity connect to allocation count?

<details markdown="1"><summary>Check</summary>

`append` beyond capacity allocates a new backing array and copies. Growing from nothing to `n` elements does that repeatedly, so a loop appending 10,000 items performs a series of allocations and copies totalling far more than 10,000 elements of work.

`make([]T, 0, n)` does it once. This is the same header-and-backing-array model from Lesson 3 seen from the performance side — and it is why `allocs/op` often drops by an order of magnitude from one line.

</details>

## Real-world reps

- [ ] Run `go build -gcflags='-m' ./...` on a package you wrote and read every `escapes to heap` line. Pick the one that surprises you most and get the reason with `-m -m`.
- [ ] Benchmark a function that appends 10,000 items with and without a preallocated capacity. Compare `allocs/op` — the difference is the point, not the nanoseconds.
- [ ] Tomorrow: find a hot loop in a service you own and check whether anything in it boxes into an interface. Logging and `fmt` are the usual culprits.

## Going further

- [Go FAQ: stack or heap?](https://go.dev/doc/faq#stack_or_heap)
- [Diagnostics: memory profiling](https://go.dev/doc/diagnostics)
- [`sync.Pool`](https://pkg.go.dev/sync#Pool): read the caveats in the doc before using it
- [Toolchain Commands](../reference/toolchain-commands.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
