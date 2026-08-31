---
title: 37. Reading the Standard Library
description: The source is on your machine, it settles arguments the docs cannot, and it is the style reference
type: lesson
---

# Lesson 37. Reading the Standard Library

**Mission link:** The last skill in the arc is self-sufficiency: when the documentation is ambiguous and the blog posts disagree, you read the source and settle it.
**Primary source:** [`io.Copy` source — go.dev](https://go.dev/src/io/io.go)
**Prerequisites:** [Lesson 36](0036-reviewing-go.md)

## Warm-up

1. ▢ Which review finding should a tool catch rather than a human?

<details markdown="1"><summary>Check</summary>

A value receiver copying a mutex — `go vet`'s `copylocks`. Design judgments like a misplaced interface are what human review is for.

</details>

2. ▢ What makes a review comment actionable?

<details markdown="1"><summary>Check</summary>

Naming the concrete consequence and the mechanism, then offering the alternative. "Not idiomatic" is not reviewable.

</details>

## Know this

The standard library source is already on your machine, and it is meant to be read.

```bash
go env GOROOT              # where it lives
go doc net/http Server     # the docs for one type
go doc -src sync.Once Do   # the source of one method, in the terminal
go doc -all strings        # everything a package exports
```

`pkg.go.dev` links every declaration to its source, and your editor's "go to definition" walks straight into it. There is no barrier to reading it except the habit of not trying.

### When to read it

- **The doc comment is ambiguous** about an edge case — does it retain the slice, is it safe for concurrent use, what happens on an empty input.
- **Behaviour surprised you** and you want the mechanism rather than a guess.
- **You want a style reference.** The standard library is where the idioms in this workspace are demonstrated at scale.
- **You are choosing between two approaches** and want to know what the people who designed the language did.

### How to read it

Start at the exported function, not at the top of the file. Follow it down one level at a time, and **skip the fast paths on the first pass** — most standard library functions have a general implementation and several optimisations, and the general one is what you came for.

Then read the tests. `_test.go` files show intended usage and, more usefully, every edge case the authors thought of. When the doc does not say what happens on empty input, the test usually does.

### A worked example: `io.Copy`

`io.Copy(dst, src)` is four lines of documentation and one of the most instructive functions in the library. Reading it:

```go
func Copy(dst Writer, src Reader) (written int64, err error) {
    return copyBuffer(dst, src, nil)
}
```

and inside `copyBuffer`, before any copying happens:

```go
if wt, ok := src.(WriterTo); ok {
    return wt.WriteTo(dst)
}
if rf, ok := dst.(ReaderFrom); ok {
    return rf.ReadFrom(src)
}
// otherwise: allocate a buffer and loop over Read/Write
```

Three things fall out of five lines.

**Why copying a file to a socket is fast.** `*os.File` implements `ReadFrom`, so the copy can become a `sendfile` syscall with no bytes passing through your program. Nothing in the signature says so, and nothing needed to.

**How to extend an interface without breaking anyone.** `Copy` takes `Reader` and `Writer` — the one-method interfaces from Lesson 11 — and *asks* whether the value also satisfies a richer one. This is exactly the mechanism from [Lesson 34](0034-api-design-and-compatibility.md) for growing an interface, demonstrated in the library that invented it.

**Why your own type might be slow through it.** A wrapper that forwards `Read` but not `WriteTo` silently defeats the optimisation. That is a real performance bug in middleware, and it is invisible unless you have read this function.

The lesson generalises: the mechanism was documented nowhere, cost five minutes to find, and changes how you design your own APIs.

### Reading with judgment

The standard library is not uniformly exemplary. Some packages predate modern idiom, some are constrained by the Go 1 compatibility promise from [Lesson 34](0034-api-design-and-compatibility.md) and cannot be fixed, and the runtime is full of `unsafe` and assembly that is not a style model for anything.

Read `net/http`, `io`, `sync`, `errors`, `strings`, `context`, `log/slog` for idiom. Read `runtime` and `reflect` only for mechanism, never for style.

### This is the exit criterion

The mission asked to be trusted to make the call and explain it to someone else. That means answering "how does this actually work?" from the source, and "why is this design right?" from the reasoning — not from memory of a blog post. Both are now available to you.

## Practice

1. ▢ How do you read the implementation of `sync.Once.Do` without leaving the terminal?

<details markdown="1"><summary>Check</summary>

`go doc -src sync.Once Do`.

`go doc` without `-src` gives the documentation; with it, the source. Worth knowing because it works offline, on the exact version you are building with — which is not necessarily the version pkg.go.dev is showing you.

</details>

2. ▢ Why is copying a file to a network connection with `io.Copy` faster than the buffer loop suggests?

<details markdown="1"><summary>Check</summary>

`copyBuffer` first checks whether `src` implements `WriterTo` or `dst` implements `ReaderFrom`, and delegates if so. For a file and a socket that path can become a single `sendfile` syscall, with no bytes entering your program's memory.

The general buffered loop only runs when neither interface is satisfied. This is why wrapping a connection in a type that forwards only `Read` and `Write` can make throughput drop for no visible reason.

</details>

3. ▢ Which standard library package is the best style model?

   - a) `runtime`, where the scheduler is implemented
   - b) `net/http`, where the server is implemented
   - c) `reflect`, where type inspection is implemented
   - d) `syscall`, where the kernel calls are declared

<details markdown="1"><summary>Check</summary>

**b)** `net/http`, where the server is implemented.

It is ordinary Go solving an ordinary problem — interfaces, error handling, concurrency, an API kept compatible for over a decade. The other three are full of `unsafe`, assembly and generated code: excellent for mechanism, actively misleading as style.

</details>

4. ▢ The doc for a function does not say whether it retains the slice you pass it. How do you find out?

<details markdown="1"><summary>Check</summary>

Read the source and see whether the slice is stored anywhere that outlives the call. Then read the tests, which often assert exactly this.

If it does retain it and the doc does not say so, that is a documentation bug worth filing — and until it is fixed, your code should copy, because undocumented behaviour is free to change in the next release.

</details>

5. ▢ Interleaving Lesson 11: what does `io.Copy`'s interface upgrade say about interface size?

<details markdown="1"><summary>Check</summary>

That the smallest possible interface in the signature costs nothing in capability. `Copy` accepts the one-method `Reader` and `Writer`, so *everything* satisfies it — and it still gets the fast path when the value happens to offer more, by asking at runtime.

This is the strongest available argument for "the bigger the interface, the weaker the abstraction". Demanding `ReadWriteSeeker` up front would have excluded most callers to serve an optimisation that a type assertion provides for free.

</details>

## Real-world reps

- [ ] Read `io.Copy` and `copyBuffer` in full. It is under fifty lines and it will change how you write function signatures.
- [ ] Pick one standard library function you use weekly and read its implementation and its tests. Write down one thing you did not know.
- [ ] Tomorrow: next time a doc comment is ambiguous, open the source before searching the web. Time both approaches once and see which was faster.

## Going further

- [`io` package source](https://go.dev/src/io/io.go)
- [Effective Go](https://go.dev/doc/effective_go) — the idioms, with the library as the worked example
- [The Go Blog](https://go.dev/blog/) — design rationale from the people who made the decisions
- [Review Checklist](../reference/review-checklist.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
