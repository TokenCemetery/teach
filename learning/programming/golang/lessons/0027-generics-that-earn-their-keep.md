---
title: 27. Generics That Earn Their Keep
description: Type parameters remove duplication across types, and an interface is still the right answer for behaviour
type: lesson
---

# Lesson 27. Generics That Earn Their Keep

**Mission link:** Generics arrived after most Go idiom was settled, so the judgment about when *not* to use them is the part that distinguishes a senior reviewer.
**Primary source:** [When To Use Generics, The Go Blog](https://go.dev/blog/when-generics)
**Prerequisites:** [Lesson 11](0011-implicit-interfaces.md), [Lesson 26](0026-talking-to-a-database.md)

## Warm-up

1. ▢ Why does an unclosed `sql.Rows` drain the connection pool?

<details markdown="1"><summary>Check</summary>

An open `Rows` holds a pooled connection until closed. Leak enough and the pool is empty while the database itself is idle.

</details>

2. ▢ Why translate `sql.ErrNoRows` at the repository boundary?

<details markdown="1"><summary>Check</summary>

Otherwise `database/sql` becomes part of your package's API and every caller matching on it breaks when the persistence layer changes — with no compile error.

</details>

## Know this

A **type parameter** lets one function work over many types without `any` and without reflection:

```go
func Map[T, U any](s []T, f func(T) U) []U {
    r := make([]U, len(s))
    for i, v := range s {
        r[i] = f(v)
    }
    return r
}

names := Map(users, func(u User) string { return u.Name })   // T and U inferred
```

Inference means call sites rarely name the types. `Map[User, string](...)` is legal and usually noise.

### Constraints

The constraint says what the type parameter is allowed to be:

| Constraint | Permits |
|---|---|
| `any` | any type; you can only move values around |
| `comparable` | types usable with `==` — so, valid map keys |
| an interface with methods | types having those methods |
| an interface with a type union | exactly the listed types |

A type union with `~` matches any type whose *underlying* type is listed, which is what makes it work for named types:

```go
type Number interface {
    ~int | ~int64 | ~float64
}

func Sum[T Number](s []T) T {
    var total T          // zero value of whichever T is
    for _, v := range s {
        total += v
    }
    return total
}
```

Without `~`, `type Celsius float64` would not satisfy `Number`. With it, it does. The standard library exposes `cmp.Ordered` for the common ordered case, so you rarely write this one yourself.

An interface containing a type union can be used **only as a constraint**, never as a variable's type. An interface with just methods can be both.

### When they earn their keep

Three situations, and the Go team's own guidance says roughly this:

- **Container types.** A set, a cache, a linked list, a queue — anything whose logic is identical regardless of element type. This is the clearest case.
- **Functions over slices, maps and channels** where the element type does not matter to the algorithm. The `slices` and `maps` packages exist because of this.
- **Genuinely identical method bodies across types**, where the only difference is the type. If you would copy-paste and change `int` to `float64`, that is the signal.

### When they do not

- **A single concrete type.** Write the function for that type. Generality with one instantiation is cost with no benefit.
- **The behaviour differs per type.** That is what interfaces are for. If `T` needs a method to do the work, take an interface — `io.Writer` is not improved by a type parameter.
- **Reflection would be needed anyway.** Type parameters do not give you field access or tags; `encoding/json` cannot be rewritten with them.
- **It only makes the signature shorter.** `func Handle[T any](x T)` is `func Handle(x any)` with more punctuation.

The honest default: **write the concrete version first.** Make it generic when the second type shows up, because at that point you know which parts actually vary. That is the same argument as "do not declare an interface before you need it" from Lesson 11, and it holds for the same reason — Go makes the change cheap later.

### Recent additions

- **Generic type aliases** (Go 1.24): `type Set[T comparable] = map[T]struct{}` works across packages.
- **Generic methods** (Go 1.27): a method may declare its own type parameters, so a helper can live in a type's namespace instead of the package's. Interface methods still may not declare them, and an interface method cannot be implemented by a generic method — which keeps dynamic dispatch out of the feature.
- **Self-referential constraints** (Go 1.26): `type Adder[A Adder[A]] interface { Add(A) A }` is now legal, which makes fluent and builder-shaped constraints expressible.

On performance: do not assume generics are faster than an interface, or slower. The compiler shares instantiations between types with the same shape, so the result sits between a hand-written concrete version and an interface, and where exactly depends on the code. Stage 5 gives you `benchstat`; use it rather than a story.

## Practice

1. ▢ Would you make this generic?

   ```go
   func SumInts(s []int) int
   ```

<details markdown="1"><summary>Check</summary>

Not until there is a second numeric type that needs it. One instantiation means a type parameter, a constraint and inference rules bought nothing.

When the second arrives, `func Sum[T Number](s []T) T` is a small edit — and you will then know whether the constraint needs `~` and whether floats belong in it, which you cannot know from one caller.

</details>

2. ▢ What does `~int` allow that `int` does not?

<details markdown="1"><summary>Check</summary>

Named types whose underlying type is `int` — `type UserID int`, `type Celsius int`.

Without the tilde, the union matches the exact type only, so every domain type in your codebase is excluded. Since defining named types over primitives is idiomatic Go, a constraint without `~` usually fails on the first real caller.

</details>

3. ▢ Which is the strongest case for a type parameter?

   - a) A cache whose logic is identical for every value type
   - b) A function needing a method the type provides
   - c) A function used with exactly one concrete type
   - d) A function that inspects struct tags via reflection

<details markdown="1"><summary>Check</summary>

**a)** A cache whose logic is identical for every value type.

Container types are the canonical case: the algorithm genuinely does not depend on the element type. Option b is what interfaces are for, c has nothing to generalise over, and d needs reflection, which type parameters do not provide.

</details>

4. ▢ A colleague replaces `func Write(w io.Writer, b []byte) error` with `func Write[T io.Writer](w T, b []byte) error`. What did that buy?

<details markdown="1"><summary>Check</summary>

Essentially nothing, and it cost something. The interface version already accepts every writer; the generic version accepts the same set with a more complex signature.

The one real difference is that the generic form avoids the interface's dynamic dispatch and can be inlined per instantiation — a micro-optimisation worth making only with a benchmark showing it matters. It also loses the ability to store a heterogeneous set of writers in a slice, since each instantiation is a distinct type.

</details>

5. ▢ Interleaving Lesson 1: why does `var total T` work inside a generic function?

<details markdown="1"><summary>Check</summary>

Because every type has a zero value, and `var` gives you it — `0` for a numeric `T`, `""` for a string one.

This is the zero-value rule paying off in the type system: generic code can construct a valid starting value for a type it knows nothing about, with no constructor constraint and no `new`. A language where the default is null would need the constraint to provide one.

</details>

## Real-world reps

- [ ] Write `Map`, `Filter` and `Keys` with type parameters and use each once. Then read the [`slices`](https://pkg.go.dev/slices) package and note how many you just reimplemented.
- [ ] Take a pair of near-identical functions in your own code that differ only by type. Merge them with a type parameter, and judge whether the result reads better.
- [ ] Tomorrow: find one generic function in a library you use and work out which of the three "earns its keep" cases it falls into. If none, that is worth noticing too.

## Going further

- [When To Use Generics, The Go Blog](https://go.dev/blog/when-generics)
- [An Introduction To Generics, The Go Blog](https://go.dev/blog/intro-generics)
- [`slices`](https://pkg.go.dev/slices) and [`maps`](https://pkg.go.dev/maps): the standard library's own answer
- [Go 1.27 generic methods](https://go.dev/doc/go1.27#language)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
