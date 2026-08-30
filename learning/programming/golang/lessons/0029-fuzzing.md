---
title: 29 — Fuzzing
description: State a property that must always hold, then let the toolchain search for the input that breaks it
type: lesson
---

# Lesson 29 — Fuzzing

**Mission link:** Table tests check the cases you thought of. Fuzzing finds the ones you did not, which is exactly the category that reaches production.
**Primary source:** [Tutorial: Getting started with fuzzing — The Go Authors](https://go.dev/doc/tutorial/fuzz)
**Prerequisites:** [Lesson 28](0028-table-driven-tests.md)

## Warm-up

1. ▢ Why does `t.Cleanup` beat `defer` in a helper used by a parallel subtest?

<details markdown="1"><summary>Check</summary>

`defer` fires when the helper returns, and a parent's `defer` fires while parallel subtests are still running. `t.Cleanup` runs when that specific test finishes.

</details>

2. ▢ What is the `got, want` convention for a failure message?

<details markdown="1"><summary>Check</summary>

`t.Errorf("Parse(%q) = %v, want %v", in, got, want)` — the call, the result, the expectation, on one line, so the failure is readable without opening the file.

</details>

## Know this

A fuzz test states a **property** and lets the toolchain generate inputs looking for a counterexample:

```go
func FuzzRoundTrip(f *testing.F) {
    f.Add("3h")           // seed corpus — known-interesting inputs
    f.Add("")
    f.Add("1h30m")

    f.Fuzz(func(t *testing.T, s string) {
        d, err := Parse(s)
        if err != nil {
            return        // rejecting bad input is correct behaviour, not a failure
        }
        got, err := Parse(Format(d))
        if err != nil {
            t.Fatalf("Format produced unparseable output %q: %v", Format(d), err)
        }
        if got != d {
            t.Errorf("round trip: Parse(Format(%v)) = %v", d, got)
        }
    })
}
```

Two commands:

```bash
go test ./...                    # runs the seed corpus only, as an ordinary test
go test -fuzz=FuzzRoundTrip      # generates inputs until it finds a failure or you stop it
```

That split matters. Fuzz targets run as normal tests in CI over their corpus, and the open-ended search is something you run deliberately — for minutes or hours — when working on the code.

When a failing input is found it is **minimised and written to `testdata/fuzz/FuzzRoundTrip/`**. Commit that file: from then on it is part of the seed corpus and every `go test` run checks it. A fuzz finding becomes a regression test with no work.

### What makes a good property

The hard part is not the mechanics, it is finding an assertion that holds for every input. Four that usually exist:

| Property | Shape |
|---|---|
| Round trip | `Decode(Encode(x)) == x` |
| Invariant | output is always sorted, or always valid UTF-8, or length is preserved |
| Differential | your fast implementation agrees with the obvious slow one |
| Never panics | the function returns an error rather than crashing on any input |

"Never panics" is the weakest and still worth having for anything parsing untrusted input — which is every request body, every header, every filename. It is the whole reason fuzzing was invented.

Reject invalid input by returning early, not by failing. A parser rejecting garbage is correct; the fuzzer will move on and try something else.

### Limits worth knowing

The fuzzing engine supports a fixed set of parameter types: `[]byte`, `string`, the integer types, `float32`/`float64`, `bool`, and `rune`. To fuzz a struct, take a `[]byte` and build the struct from it deterministically.

The search is coverage-guided but not exhaustive. A clean overnight run is evidence, not proof — the same caveat as the race detector in Lesson 20, for the same reason: both observe what actually executed.

Fuzzing is slow relative to unit tests, so keep the body fast. A target that touches a database will find almost nothing, because the engine gets a few hundred executions a second instead of a few hundred thousand.

## Practice

1. ▢ Your parser returns an error on random bytes. Is that a fuzz failure?

<details markdown="1"><summary>Check</summary>

No — it is the parser working. Return early from the fuzz function when the input is legitimately invalid.

Failing on any error would make the fuzzer report noise immediately and constantly, and the real property — that valid input round-trips, and that nothing panics — would never get exercised.

</details>

2. ▢ The fuzzer finds a crashing input. What do you do with it?

<details markdown="1"><summary>Check</summary>

Commit the file it wrote under `testdata/fuzz/`. It becomes part of the seed corpus, so every subsequent `go test` — with no `-fuzz` flag — replays it.

That turns each finding into a permanent regression test at zero cost, which is the part of Go's fuzzing design that makes it worth adopting rather than just trying.

</details>

3. ▢ Which is the strongest property to fuzz for a JSON encoder?

   - a) That the output never contains a null byte
   - b) That decoding the encoded value returns it
   - c) That the output is shorter than the input
   - d) That the function completes within one second

<details markdown="1"><summary>Check</summary>

**b)** That decoding the encoded value returns it.

A round trip constrains the whole encoding rather than one surface detail, so it catches quoting, escaping and Unicode bugs together. Option a is a narrow invariant, c is not even true, and d tests the machine more than the code.

</details>

4. ▢ You want to fuzz a function taking a `Config` struct. The engine only accepts primitives. What do you do?

<details markdown="1"><summary>Check</summary>

Take a `[]byte` and construct the `Config` from it deterministically — slice fields out of the bytes, or feed it through a decoder you already trust.

Deterministic matters: the engine minimises a failing input by shrinking the bytes and re-running, so the same bytes must always produce the same `Config`. Anything random in the construction makes the reported failure unreproducible.

</details>

5. ▢ Interleaving Lesson 5: why is a UTF-8-handling function a good fuzz target?

<details markdown="1"><summary>Check</summary>

Because the input space is enormous and the interesting cases are exactly the ones nobody writes by hand: truncated multi-byte sequences, overlong encodings, lone surrogates, combining marks.

Lesson 5's rule — `len` is bytes, indexing is bytes, only `range` decodes — is violated by code that slices a string at an arbitrary index. A fuzzer finds that in seconds by producing a string where the boundary lands mid-rune, which is the same bug that mangles a real user's name in production.

</details>

## Real-world reps

- [ ] Write a `Format`/`Parse` pair and fuzz the round trip. Run it for two minutes and see whether it finds anything.
- [ ] Deliberately introduce a bug — slice a string at a byte index — and watch the fuzzer produce the multi-byte input that breaks it. Commit the corpus file it writes.
- [ ] Tomorrow: find one function in a service you own that parses untrusted input. Write the "never panics" fuzz target for it, even if you write nothing else.

## Going further

- [Tutorial: Getting started with fuzzing](https://go.dev/doc/tutorial/fuzz)
- [Go Fuzzing documentation](https://go.dev/security/fuzz/) — supported types, corpus layout, and how minimisation works
- [Toolchain Commands](../reference/toolchain-commands.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
