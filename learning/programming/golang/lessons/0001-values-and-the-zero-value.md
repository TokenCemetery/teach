---
title: 1. Values and the Zero Value
description: Every declared variable is already usable, and nil is a value rather than an absence
type: lesson
---

# Lesson 1. Values and the Zero Value

**Mission link:** Go's defaults are load-bearing. Code that defends against uninitialised state is fighting the language before it has expressed any logic.
**Primary source:** [Effective Go, The Go Authors](https://go.dev/doc/effective_go)
**Prerequisites:** none, this is the first lesson.

## Know this

Go removes a whole category of bug with one rule: **a declared variable always holds a value.** There is no uninitialised memory, no `undefined`, and no moment between declaration and first assignment where reading is a mistake. `var n int` is `0`. `var s string` is `""`. `var p *User` is `nil`. A struct is the zero value of every field, applied recursively.

That value is called the **zero value**, and it is specified by the language rather than left to the compiler ([spec](https://go.dev/ref/spec#The_zero_value)).

Three ways to declare:

```go
var count int           // explicit type, zero value 0
var name = "gopher"     // type inferred from the value
total := 42             // short form, functions only, and at least one new name on the left
```

The short form is why idiomatic Go writes types out far less often than its reputation suggests.

The compiler also enforces that you meant it. An unused local variable and an unused import are **compile errors**, not warnings. This is deliberate: it is cheaper to delete dead code than to grow used to ignoring warnings.

### The zero value is meant to be usable

| Type | Zero value | Usable as-is? |
|---|---|---|
| numeric | `0` | yes |
| `string` | `""` | yes |
| `bool` | `false` | yes |
| slice | `nil` | yes, `len`, `cap`, `range` and `append` all work |
| map | `nil` | reads work, writes panic |
| pointer, func, chan, interface | `nil` | no, dereferencing or calling panics |
| struct | each field at its own zero value | as usable as its fields are |

The standard library is designed around this. All three of these are ready to work with no constructor:

```go
var mu sync.Mutex     // ready to Lock
var buf bytes.Buffer  // ready to WriteString
var wg sync.WaitGroup // ready to Add
```

That is the idiom to copy: **make the zero value useful**, and supply a constructor only when it cannot be. In Java, `new StringBuilder()` is unavoidable because the field would otherwise be `null`. In Go, requiring `NewBuffer()` before a `Buffer` works would be a design smell.

### `nil` is a value, not an absence

`nil` is not `null`. It is the zero value for six kinds of type, and it carries a type with it. Two of those kinds are genuinely usable while nil.

A nil slice is a perfectly good empty slice:

```go
var ids []int
fmt.Println(len(ids)) // 0
ids = append(ids, 7)  // fine, append allocates the backing array
```

A nil map reads but does not write:

```go
var m map[string]int
fmt.Println(m["missing"]) // 0, reads from a nil map return the zero value
m["k"] = 1                // panic: assignment to entry in nil map
```

The asymmetry is deliberate. Reading needs no storage; writing does, and Go will not quietly allocate a map you never asked for. So a nil slice needs no guard, and a nil map does.

## Practice

1. ▢ You declare `var tags []string` and never assign to it. Name three operations that are safe on `tags`, and one that is not.

<details markdown="1"><summary>Check</summary>

Safe: `len(tags)`, `range tags` (zero iterations), `append(tags, "x")`. Also `cap(tags)` and comparing `tags == nil`.

Not safe: indexing, `tags[0]`, which panics with an index-out-of-range error, the same as it would on any empty slice.

The wrong instinct, imported from a language with `null`, is to write `if tags != nil` before ranging. It is dead code: ranging a nil slice runs zero times, which is exactly what you wanted.

</details>

2. ▢ Predict the output, then explain the difference between the two lines.

   ```go
   var counts map[string]int
   fmt.Println(counts["a"])
   counts["a"]++
   ```

<details markdown="1"><summary>Check</summary>

It prints `0`, then panics: `assignment to entry in nil map`.

A read only has to return the zero value, and it can do that without any storage. A write needs somewhere to put the entry, and the nil map has no hash table behind it. Go refuses to allocate one implicitly, so the map must be made first: `counts := make(map[string]int)`.

Note that `counts["a"]++` is a write, even though it looks like an increment of something that already exists.

</details>

3. ▢ Which one panics the first time it is used as intended?

   - a) `var mu sync.Mutex`, then `mu.Lock()`
   - b) `var b bytes.Buffer`, then `b.WriteString("x")`
   - c) `var m map[string]int`, then `m["a"] = 1`
   - d) `var s []int`, then `s = append(s, 1)`

<details markdown="1"><summary>Check</summary>

**c)** `var m map[string]int`, then `m["a"] = 1`.

A `Mutex` and a `Buffer` are both designed so their zero value is ready to use, and a nil slice accepts `append`. Only the map write needs storage that has not been allocated.

</details>

4. ▢ Why does idiomatic Go have far fewer constructor functions than the equivalent Java or TypeScript code?

<details markdown="1"><summary>Check</summary>

Because the zero value is usually already the correct starting state, so there is nothing for a constructor to do. A constructor earns its place only when a field's zero value is invalid: an unset timeout that must default to 30 seconds, a required dependency, a validated invariant.

The habit worth breaking is writing `NewThing()` reflexively. If it only sets fields to their zero values, delete it; if it exists so callers cannot forget one required field, keep it.

</details>

5. ▢ Is this type usable without a constructor, and what would you still warn a reviewer about?

   ```go
   type Counter struct {
       mu sync.Mutex
       n  int
   }
   ```

<details markdown="1"><summary>Check</summary>

Yes. `var c Counter` is ready to use, because both fields are usable at their zero values.

The warning is about copying rather than construction: once a `sync.Mutex` has been used, copying the struct that contains it copies lock state, and the copy is no longer coordinated with the original. Pass `*Counter`, not `Counter`. `go vet` catches this; it is what the `copylocks` check exists for, and Lesson 2 is about the copy semantics underneath it.

</details>

## Real-world reps

- [ ] Write the `Counter` above with an `Inc()` method and use it from `main` with no constructor. Then deliberately pass it by value to a function and run `go vet ./...` to see the `copylocks` diagnostic.
- [ ] Declare a variable you never use and try to build. Read the exact error text. You will see it often, and it means less than it looks like it means.
- [ ] Tomorrow: take one class from a Java or TypeScript project you know well. List which fields would need a constructor in Go, and which would be fine at their zero value. Most will be fine.

## Going further

- [Effective Go](https://go.dev/doc/effective_go): the sections on allocation and on `new` versus `make`
- [The zero value, in the language spec](https://go.dev/ref/spec#The_zero_value)
- [Glossary](../GLOSSARY.md): `zero value` is pinned there because carrying `null` across from another language is the failure this lesson prevents
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
