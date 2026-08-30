---
title: 2 — Value Semantics and Pointers
description: Every assignment and every argument is a copy, and a pointer is how you opt out
type: lesson
---

# Lesson 2 — Value Semantics and Pointers

**Mission link:** Almost every "why didn't my change stick" bug in early Go is a copy the author did not see. Seeing copies is the prerequisite for reading slices, maps and method sets correctly.
**Primary source:** [Effective Go — Data, allocation with `new` and `make`](https://go.dev/doc/effective_go#allocation_new)
**Prerequisites:** [Lesson 1](0001-values-and-the-zero-value.md)

## Warm-up

1. ▢ `var m map[string]int`. Which works: reading `m["a"]`, or writing `m["a"] = 1`?

<details markdown="1"><summary>Check</summary>

Reading works and returns `0`. Writing panics, because there is no hash table to write into and Go will not allocate one implicitly.

</details>

2. ▢ Name two standard-library types whose zero value is ready to use with no constructor.

<details markdown="1"><summary>Check</summary>

`sync.Mutex`, `bytes.Buffer`, `sync.WaitGroup`, `strings.Builder`, `time.Time` — any two. "Make the zero value useful" is the design rule they all follow.

</details>

## Know this

**Go has one evaluation rule: assignment copies the value.** Passing an argument, returning a result, assigning a variable, appending a struct to a slice, storing into a map — all of them copy. There is no hidden reference, and there is no `Object` that is secretly a pointer.

This is the single largest difference from Java, where a variable of class type is always a reference to an object somewhere else. In Go, a struct variable *is* the struct — the bytes live where the variable lives.

```go
type User struct{ Name string }

func rename(u User) { u.Name = "changed" }

u := User{Name: "original"}
rename(u)
fmt.Println(u.Name) // original — rename mutated its own copy
```

Nothing about that is a bug in `rename`. The function was handed a copy, and it changed the copy.

### A pointer is how you opt out

A pointer is the address of a value. `&x` takes it, `*p` dereferences it, and `p.Field` dereferences implicitly so you almost never write `(*p).Field`.

```go
func rename(u *User) { u.Name = "changed" }

u := User{Name: "original"}
rename(&u)
fmt.Println(u.Name) // changed
```

Go has no pointer arithmetic. A pointer either points at a valid value or is `nil`; it cannot drift off the end of an array. That is what lets the garbage collector be exact, and it is why a Go pointer is much closer to a Java reference than to a C pointer.

Three ways to get one:

```go
p := &User{Name: "a"}    // composite literal, addressed — the common form
q := new(User)           // zero-valued User, returns *User
n := new(len(s))         // Go 1.26: new takes an expression, so this is a *int holding len(s)
```

`new(expr)` is new in [Go 1.26](https://go.dev/doc/go1.26#language) and mostly earns its place filling optional pointer fields in JSON structs. `&User{...}` remains the everyday form.

### Which types already carry a reference inside

Copying is always shallow, and four built-in types are small headers that point at storage they do not own:

| Type | What the copy duplicates | What both copies share |
|---|---|---|
| slice | pointer, length, capacity | the backing array |
| map | one pointer | the whole hash table |
| channel | one pointer | the channel |
| pointer | the address | the pointed-at value |

So `func add(m map[string]int)` can insert entries the caller sees, even though `m` was copied — the copy points at the same table. A map argument is a copied header, not a reference parameter, and the distinction shows up the moment you assign to `m` itself rather than into it.

Everything else — structs, arrays, strings, numbers — is copied in full. `[1000]int` passed to a function copies eight kilobytes.

### When to use a pointer

Reach for one when any of these is true:

- **The callee must mutate the caller's value.** This is the main reason.
- **The type must not be copied.** Anything containing a `sync.Mutex`, or a struct the standard library documents as "must not be copied after first use".
- **The value is large and copied often.** Measure before believing this one; a copy of a few words is cheaper than the indirection that replaces it.
- **`nil` is a meaningful state** that the zero value cannot express — a field that is genuinely absent rather than empty.

Otherwise prefer values. They cannot be nil, they cannot be aliased by accident, and they are easier to reason about — the same reasons a reviewer will ask you to justify a pointer, not a value.

## Practice

1. ▢ Predict the output.

   ```go
   type Config struct{ Retries int }

   func bump(c Config) { c.Retries++ }

   c := Config{Retries: 1}
   bump(c)
   fmt.Println(c.Retries)
   ```

<details markdown="1"><summary>Check</summary>

`1`. `bump` incremented a copy that was discarded when it returned.

To make it stick, the parameter must be `*Config` and the call `bump(&c)`. The wrong instinct is to assume that "objects are passed by reference", which is true in Java and false in Go — Go passes everything by value, including pointers.

</details>

2. ▢ This function does modify the caller's map. Explain why, given that `m` is a copy.

   ```go
   func add(m map[string]int) { m["k"] = 1 }
   ```

<details markdown="1"><summary>Check</summary>

The copy is of the map header — one pointer. Both the caller's variable and the parameter point at the same hash table, so writing through either is visible in both.

The line that would *not* be visible is `m = make(map[string]int)` inside `add`: that reassigns the local copy of the header, leaving the caller pointed at the original table. Same for `s = append(s, x)` on a slice parameter, which is Lesson 3.

</details>

3. ▢ Which of these is the weakest reason to take a pointer receiver?

   - a) The method has to mutate the receiver's fields
   - b) The struct embeds a mutex that resists copying
   - c) The struct is a hundred bytes of plain fields
   - d) The method must record that no value exists

<details markdown="1"><summary>Check</summary>

**c)** The struct is a hundred bytes of plain fields.

A hundred bytes is a cheap copy — often cheaper than the pointer chase and the extra pressure it can put on the heap. Size is a real reason only with evidence from a benchmark, which is stage 5. Mutation, copy-hostile fields, and a meaningful `nil` are all reasons that hold before you measure anything.

</details>

4. ▢ `arr := [3]int{1, 2, 3}` and `sl := []int{1, 2, 3}`. You pass each to a function that assigns `9` to element zero. Which caller sees `9`?

<details markdown="1"><summary>Check</summary>

The slice caller. `[3]int` is an array — a value type, copied element by element — so the function writes into its own copy. A slice copies a three-word header that still points at the caller's backing array, so the write lands in shared storage.

This is the clearest demonstration that arrays and slices are different types rather than two spellings of one idea, and it is why arrays are rare in Go outside fixed-size buffers and map keys.

</details>

5. ▢ A colleague writes `func (c Counter) Inc() { c.n++ }` where `Counter` has an `n int` field. The code compiles and the count never rises. What is the fix, and why did the compiler not object?

<details markdown="1"><summary>Check</summary>

The receiver must be `*Counter`. With a value receiver the method operates on a copy of the counter made at call time, increments it, and drops it.

The compiler stays silent because nothing is ill-typed — incrementing a field of a local copy is a legal thing to want. This is the shape of the whole category: Go's value semantics make wrong code compile cleanly, which is exactly why the habit of asking "what was copied here?" has to be deliberate. Method sets, in [Lesson 6](0006-methods-and-method-sets.md), are the formal version of this question.

</details>

## Real-world reps

- [ ] Write the `rename` example both ways in a scratch file, run it, and confirm the output before you read the code again. Predicting first is the whole exercise.
- [ ] Take a struct from a project you work on. Write down, for each method, whether it should have a value or pointer receiver and why. Consistency within a type matters more than any single call.
- [ ] Tomorrow: find one place in your own code where you pass a large struct by value in a loop. Do not change it — just note whether you can articulate a cost, or only a suspicion. Stage 5 turns the suspicion into a number.

## Going further

- [Effective Go — allocation with `new` and `make`](https://go.dev/doc/effective_go#allocation_new)
- [Go FAQ — should I define methods on values or pointers?](https://go.dev/doc/faq#methods_on_values_or_pointers)
- [Lesson 3 — Slices and the Backing Array](0003-slices-and-the-backing-array.md) — the copy rule applied to the type that surprises people most
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
