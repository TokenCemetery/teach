---
title: 3. Slices and the Backing Array
description: A slice is a three-word header over an array someone else may also be holding
type: lesson
---

# Lesson 3. Slices and the Backing Array

**Mission link:** Slice aliasing is the bug that separates people who read Go from people who write it. It produces corrupted data with no panic, no race, and no stack trace.
**Primary source:** [Go Slices: usage and internals — The Go Blog](https://go.dev/blog/slices-intro)
**Prerequisites:** [Lesson 2](0002-value-semantics-and-pointers.md)

## Warm-up

1. ▢ A function takes a `map[string]int` parameter and inserts a key. Does the caller see it?

<details markdown="1"><summary>Check</summary>

Yes. The map header was copied, but the copy points at the same hash table.

</details>

2. ▢ Name the one reason to take a pointer receiver that needs no benchmark to justify.

<details markdown="1"><summary>Check</summary>

The method has to mutate the receiver. Copy-hostile fields such as a `sync.Mutex`, and a meaningful `nil`, are the other two that stand on their own. Size is the one that needs evidence.

</details>

## Know this

A slice is not a list and not an array. It is a three-word **header**:

| Field | Meaning |
|---|---|
| pointer | where the elements start in the backing array |
| length | how many elements this slice exposes — what `len` returns |
| capacity | how many elements exist from the pointer to the end of the array — what `cap` returns |

The elements live in a **backing array** that the slice does not own and does not exclusively hold. Two slices can point into the same array, and neither knows about the other.

Slicing creates a second header over the same storage:

```go
a := []int{1, 2, 3, 4, 5}
b := a[1:3]
fmt.Println(len(b), cap(b)) // 2 4  — length 2, but capacity runs to the end of a
b[0] = 99
fmt.Println(a)              // [1 99 3 4 5]
```

Nothing was copied. `b[0]` and `a[1]` are the same memory.

### `append` is conditional, and that is the trap

`append` has two behaviours, and which one you get depends on capacity:

- **Capacity is sufficient** → it writes into the existing backing array and returns a header with a longer length. Anyone else pointed at that array sees the write.
- **Capacity is not sufficient** → it allocates a new, larger array, copies the elements, and returns a header pointing at the new one. The old array is now untouched by further appends.

```go
a := []int{1, 2, 3, 4, 5}
b := a[1:3]        // len 2, cap 4 — room to spare
b = append(b, 99)  // writes into a's array at index 3
fmt.Println(a)     // [1 2 3 99 5]  — a was never mentioned
```

The same code with `a := []int{1, 2, 3}` would have hit the second branch, allocated, and left `a` alone. **Whether an append is visible elsewhere depends on capacity**, which is not visible at the call site and not stable across inputs. That is why this bug reaches production: it is data-dependent.

The growth amount is unspecified. Do not build anything on a doubling assumption; it has changed between releases and applies differently to large slices.

### Two habits that defuse it

**Cut the capacity when you hand out a sub-slice.** The three-index form `s[low:high:max]` sets capacity explicitly, so the result has no room and the first `append` is forced to allocate:

```go
b := a[1:3:3]      // len 2, cap 2
b = append(b, 99)  // allocates; a is untouched
```

**Copy when you mean copy.** `copy(dst, src)` moves `min(len(dst), len(src))` elements, or use `slices.Clone` from the [`slices`](https://pkg.go.dev/slices) package added in Go 1.21.

### `append` also copies the header

The other half of Lesson 2 applies here:

```go
func addOne(s []int) { s = append(s, 1) } // caller never sees the new element
```

`s` is a copy of the header. Appending may or may not touch shared storage, but the *new length* only ever lands in the local copy. This is why `append` is written as `s = append(s, x)` everywhere in Go: the return value is the point, and a function that grows a slice must return it.

### nil versus empty

`var s []int` is nil with length 0. `s := []int{}` is non-nil with length 0. `len`, `range`, and `append` treat them identically, so prefer nil — it is the zero value and needs no allocation. The difference is visible in exactly two places: `s == nil`, and JSON, where a nil slice marshals to `null` and an empty one to `[]`.

## Practice

1. ▢ Predict the printed value of `a`.

   ```go
   a := []int{1, 2, 3, 4, 5}
   b := a[:2]
   b = append(b, 30)
   fmt.Println(a)
   ```

<details markdown="1"><summary>Hint</summary>

Work out `len(b)` and `cap(b)` before you predict. Slicing moved where `b` starts and ends; it did not move where the array ends.

</details>

<details markdown="1"><summary>Check</summary>

`[1 2 30 4 5]`.

`b` has length 2 and capacity 5, so `append` had room and wrote into `a`'s backing array at index 2, replacing the `3`. No allocation, no copy, and no hint at the call site that `a` was involved.

</details>

2. ▢ Same code, but `a := []int{1, 2}` and `b := a[:2]`. What does `a` print now, and what changed?

<details markdown="1"><summary>Check</summary>

`[1 2]`. Capacity was 2 and length was 2, so `append` had to allocate a new array and copy into it. `b` now points at storage `a` knows nothing about.

Same source, opposite outcome, decided entirely by the input length. That data dependence is the reason to fix this with the three-index form rather than by reasoning carefully at each call site.

</details>

3. ▢ You are writing a function that returns the first two elements of a caller-supplied slice, and the caller will keep appending to your result. Which return expression is safe?

   - a) `return s[:2]`
   - b) `return s[0:2:2]`
   - c) `return s[:2:cap(s)]`
   - d) `return s[0:2]`

<details markdown="1"><summary>Hint</summary>

Ask of each option: how much room is left past the length you handed back? Three of the four answer the same way.

</details>

<details markdown="1"><summary>Check</summary>

**b)** `return s[0:2:2]`.

It sets capacity to 2, so the caller's first `append` must allocate and cannot reach into your storage. Options a and d are the same expression written two ways, and c explicitly hands over the full capacity — the worst of the four.

`slices.Clone(s[:2])` is the other correct answer: it always copies, at the cost of an allocation you may not need.

</details>

4. ▢ Why is `s = append(s, x)` written with the assignment, when `append` sometimes modifies the array in place anyway?

<details markdown="1"><summary>Check</summary>

Because the length lives in the header, not in the array. Even when `append` writes in place, the caller's header still says the old length, so the new element is outside the slice until the returned header replaces it. When `append` reallocates, the returned header is the only thing pointing at the new array.

Discarding the result is a bug in both branches. `go vet` does not catch it in general, which is why the assignment is a fixed idiom rather than a judgment call.

</details>

5. ▢ Interleaving Lesson 1: a function returns `nil` for "no results", and its caller does `for _, r := range results`. Is a nil check needed first?

<details markdown="1"><summary>Check</summary>

No. Ranging a nil slice runs zero times.

Add the check only if nil and empty mean genuinely different things to the caller — which is rare, and worth a doc comment when it is true. Returning a nil slice for "nothing" is idiomatic; returning `[]int{}` to be defensive is noise.

</details>

## Real-world reps

- [ ] Run the two `append` examples above and print `len` and `cap` at each step. Watching capacity change is what makes the rule stick.
- [ ] Write a function `func Head(s []int) []int` that returns the first two elements and cannot be used to corrupt the caller's data. Then write the test that fails against the unsafe version.
- [ ] Tomorrow: search a codebase you work in for `[:` and check each sub-slice that escapes the function it was made in. You are looking for slices handed to a caller with capacity to spare.

## Going further

- [Go Slices: usage and internals — The Go Blog](https://go.dev/blog/slices-intro)
- [Arrays, slices and strings: the mechanics of `append` — The Go Blog](https://go.dev/blog/slices)
- [`slices` package](https://pkg.go.dev/slices) — `Clone`, `Contains`, `Sort`, `Delete`, added in Go 1.21
- [Slice and Map Mechanics](../reference/slice-and-map-mechanics.md) — the lookup version of this lesson
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
