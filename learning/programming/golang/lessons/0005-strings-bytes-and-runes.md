---
title: 5. Strings, Bytes and Runes
description: A string is immutable UTF-8 bytes, so len is not a character count and indexing is not a character
type: lesson
---

# Lesson 5. Strings, Bytes and Runes

**Mission link:** Every service parses, slices and logs strings. Treating them as arrays of characters produces output that is fine in tests and mangled the first time a real name arrives.
**Primary source:** [Strings, bytes, runes and characters in Go — The Go Blog](https://go.dev/blog/strings)
**Prerequisites:** [Lesson 3](0003-slices-and-the-backing-array.md)

## Warm-up

1. ▢ Why can you not write `m["a"].N++` when `m` is a `map[string]Stat`?

<details markdown="1"><summary>Check</summary>

Map elements are not addressable, because the table can relocate entries as it grows. Store `*Stat`, or read into a local, mutate, and assign back.

</details>

2. ▢ What is the capacity of a nil slice, and what happens when you append to it?

<details markdown="1"><summary>Check</summary>

Capacity 0. `append` allocates a backing array and returns a header pointing at it — no guard needed.

</details>

## Know this

A Go string is an **immutable, read-only sequence of bytes**. Not characters. The bytes are conventionally UTF-8, and the language guarantees UTF-8 in exactly two places: string literals in source, and the `range` loop.

Two consequences arrive immediately:

```go
s := "héllo"
fmt.Println(len(s))  // 6 — bytes, because é takes two
fmt.Println(s[1])    // 195 — a byte (uint8), not a character
```

`len` is a byte count and `s[i]` is a byte. Neither is wrong; both are answering a lower-level question than the one usually intended.

### `rune` is the character-shaped type

A **rune** is an alias for `int32` holding a Unicode code point. `range` over a string decodes UTF-8 and yields runes, with the *byte* index of each:

```go
for i, r := range "héllo" {
    fmt.Println(i, string(r))
}
// 0 h
// 1 é
// 3 l    <- index jumps from 1 to 3: é occupied two bytes
// 4 l
// 5 o
```

The jump from 1 to 3 is the whole lesson in one line. A `for i := 0; i < len(s); i++` loop over the same string visits six positions and produces two of them that are not valid characters on their own.

To count characters, count runes: `utf8.RuneCountInString(s)` returns 5.

Invalid UTF-8 does not stop the loop. `range` yields `utf8.RuneError` (`U+FFFD`, the replacement character) and advances one byte, so a corrupt input degrades rather than panics.

### Converting costs a copy

```go
b := []byte(s)   // allocates and copies — strings are immutable, byte slices are not
r := []rune(s)   // allocates, decodes, four bytes per code point
back := string(b)
```

Each conversion is an allocation. That is fine once, and it is a real cost inside a hot loop — the kind of thing stage 5 finds in a profile. `[]rune` in particular is heavy: it turns a 6-byte string into a 20-byte slice.

Building strings in a loop with `+=` is quadratic, because each concatenation allocates a new string and copies both sides. Use a builder:

```go
var b strings.Builder
for _, part := range parts {
    b.WriteString(part)
}
return b.String()
```

`strings.Builder` is usable at its zero value, and — like anything holding internal state — must not be copied after first use.

### `strings` and `bytes` are the same package twice

`strings` operates on `string`, `bytes` on `[]byte`, with near-identical APIs: `Contains`, `Split`, `TrimSpace`, `Builder`/`Buffer`. Choose by what you already hold, so you do not pay for a conversion just to call a function.

### The honest caveat

A rune is a code point, and a code point is still not always a "character" as a user sees it. `é` can be one code point or two (`e` plus a combining accent), and a flag emoji is two. Rune counting is correct for indexing and slicing text; for anything user-visible — truncating a display name, counting for a UI limit — grapheme clusters are the right unit, and that needs a library such as [`golang.org/x/text`](https://pkg.go.dev/golang.org/x/text). Knowing which question you are asking matters more than the answer.

## Practice

1. ▢ For `s := "héllo"`, give `len(s)`, `utf8.RuneCountInString(s)`, and the type of `s[0]`.

<details markdown="1"><summary>Check</summary>

`6`, `5`, and `byte` (which is `uint8`).

The wrong instinct is to expect `len` to match what you see. It matches what is stored. Both numbers are correct answers to different questions, and the bug is asking the wrong one.

</details>

2. ▢ Why does this print the wrong thing, and what does it actually print?

   ```go
   s := "héllo"
   fmt.Println(string(s[1]))
   ```

<details markdown="1"><summary>Check</summary>

It prints `Ã` — the replacement of a lone byte. `s[1]` is the first of the two bytes encoding `é`, `195`. Converting a single byte value to a string interprets it as a code point, and code point 195 is `Ã`.

To get the character, range the string, or decode with `utf8.DecodeRuneInString(s[1:])`.

</details>

3. ▢ Which loop safely visits each character of an arbitrary UTF-8 string?

   - a) `for i := 0; i < len(s); i++`
   - b) `for i, r := range s`
   - c) `for i := range len(s)`
   - d) `for _, b := range []byte(s)`

<details markdown="1"><summary>Check</summary>

**b)** `for i, r := range s`.

Ranging a string decodes UTF-8 and yields runes. Options a and c both walk raw bytes by index — c is the Go 1.22 range-over-int form, which changes the spelling and not the problem — and d converts to bytes explicitly, which is right only when bytes are what you want.

</details>

4. ▢ A handler builds a CSV line by appending to a string inside a loop over 50,000 rows. Name the cost and the fix.

<details markdown="1"><summary>Check</summary>

Strings are immutable, so each `+=` allocates a new string and copies everything accumulated so far. The work is quadratic in the number of rows.

Use `strings.Builder`, which keeps a growing byte buffer and converts once at the end. For output that is being written anyway, skip the intermediate string entirely and write into the `io.Writer` — `w` is already there in an HTTP handler.

</details>

5. ▢ Interleaving Lesson 3: `b := []byte(s)`, then `b[0] = 'H'`. Does `s` change? What if you could take a slice of the string directly?

<details markdown="1"><summary>Check</summary>

`s` does not change. `[]byte(s)` allocated a copy precisely because strings are immutable, so `b` has its own backing array — this is one of the few places Go copies rather than aliasing.

Slicing a string, `s[1:3]`, does *not* copy: it produces a new string header over the same bytes, cheaply. That is safe only because neither side can write. Immutability is what buys the sharing.

</details>

## Real-world reps

- [ ] Run the range loop over `"héllo"` and print the byte index with each rune. Then run the indexed byte loop over the same string and compare the two outputs side by side.
- [ ] Write a `Truncate(s string, n int) string` that cuts to `n` characters without splitting a multi-byte one. Test it with an accented string and an emoji, and note which case your implementation still gets wrong.
- [ ] Tomorrow: grep a codebase for `len(` applied to something user-supplied — a name, a description, a password. Decide for each whether bytes or characters was the intended unit.

## Going further

- [Strings, bytes, runes and characters in Go — The Go Blog](https://go.dev/blog/strings)
- [`unicode/utf8` package](https://pkg.go.dev/unicode/utf8) — `RuneCountInString`, `DecodeRuneInString`, `ValidString`
- [`strings.Builder`](https://pkg.go.dev/strings#Builder)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
