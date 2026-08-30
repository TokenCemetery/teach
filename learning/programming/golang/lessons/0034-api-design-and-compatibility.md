---
title: 34 — API Design and Compatibility
description: What you can add without breaking callers, and the three changes that always do
type: lesson
---

# Lesson 34 — API Design and Compatibility

**Mission link:** Designing a package API you can keep backwards-compatible is a stated success criterion. The rules are short, and two of them are counterintuitive enough that most people learn them by breaking something.
**Primary source:** [Go 1 and the Future of Go Programs — The Go Authors](https://go.dev/doc/go1compat)
**Prerequisites:** [Lesson 14](0014-designing-a-package.md), [Lesson 33](0033-modules-and-release-builds.md)

## Warm-up

1. ▢ Why must a module at v2 or above carry `/v2` in its path?

<details markdown="1"><summary>Check</summary>

So v1 and v2 are different packages and can coexist in one build. Without the suffix the go tool will not select the new major version at all.

</details>

2. ▢ What does minimal version selection choose?

<details markdown="1"><summary>Check</summary>

The highest of the minimum versions required across the graph — not the newest published. Upgrades happen only when a `go.mod` changes.

</details>

## Know this

Go's own compatibility promise is the model: code that builds with one Go 1 release should build and run with later ones. It is not a slogan — it constrains what the Go team ships, and it is why upgrading a Go toolchain is boring. Aim your own packages at the same bar.

### The three changes that always break

**Removing or renaming an exported identifier.** Obvious, and the only one people reliably remember.

**Changing a function signature.** Adding a parameter, changing a type, changing the number of results. Add a new function instead — `QueryContext` beside `Query` is the standard library doing exactly this.

**Adding a method to an interface.** Every implementation outside your module stops compiling, including test doubles. This is the one that catches people, because adding a method feels additive. It is not — an interface is a contract on implementers, so it can only shrink safely.

If an interface must grow, define a new one and detect it:

```go
type Flusher interface{ Flush() error }

if f, ok := w.(Flusher); ok {
    if err := f.Flush(); err != nil { ... }
}
```

That is how `net/http` grew `Hijacker`, `Flusher` and `Pusher` without breaking a single `ResponseWriter` implementation.

### The subtle one: struct fields

Adding a field to an exported struct is *usually* safe — unless a caller writes an unkeyed composite literal:

```go
p := Point{1, 2}          // breaks the moment Point gains a third field
p := Point{X: 1, Y: 2}    // keeps working
```

You cannot stop callers doing the first. The standard defence is an unexported zero-width field, which makes the unkeyed form a compile error immediately rather than later:

```go
type Options struct {
    Timeout time.Duration
    _       struct{}   // forces keyed literals
}
```

Removing a field, changing its type, or making it unexported is always breaking.

### Designing for change up front

**Return concrete types, accept interfaces.** Adding a method to your struct breaks nobody; adding one to your interface breaks everyone. This is the compatibility argument for the Lesson 11 rule, and it is the stronger one.

**Options struct or functional options** for anything that will grow:

```go
func New(db *sql.DB, opts ...Option) *Store

type Option func(*config)

func WithTimeout(d time.Duration) Option {
    return func(c *config) { c.Timeout = d }
}
```

New options are new functions — purely additive, and the zero configuration stays valid. The cost is one function per setting plus indirection, so for two or three settings an `Options` struct with a documented zero value is simpler and just as extensible. Use functional options when the set will keep growing and the compatibility horizon is long, which is the situation libraries are in and most services are not.

**Document what is not guaranteed.** Error message text, map iteration order, the exact number of goroutines, whether a returned slice is retained. If you do not say, someone will depend on it, and their bug report will be about your change.

### Deprecating

Go has no `@Deprecated` attribute — the convention is a paragraph in the doc comment starting with the exact word:

```go
// Query runs the query without a context.
//
// Deprecated: use QueryContext instead.
func Query(q string) (*Rows, error)
```

Tooling recognises the marker: editors strike it through, and linters report uses. Keep the function working. Deprecation announces an intention; removal is a v2.

### When you genuinely must break

Cut a new major version with a new module path. It is more work than breaking quietly, and that asymmetry is the point — it makes "just change it" cost something.

For behaviour changes that are not type changes, Go itself uses `GODEBUG` settings: the new behaviour is the default, and the old one is recoverable with a documented flag while callers migrate. It is a good pattern to copy for a widely-used internal library.

## Practice

1. ▢ You add a method to an exported interface. Who breaks?

<details markdown="1"><summary>Check</summary>

Every implementation you do not control — including every test double a consumer wrote.

An interface constrains implementers, so growing it is a breaking change even though it looks additive. Define a second interface and type-assert for it, which is how `net/http` added `Flusher` and `Hijacker` without breaking anyone.

</details>

2. ▢ Adding a field to an exported struct broke a consumer. How?

<details markdown="1"><summary>Check</summary>

They used an unkeyed composite literal — `Point{1, 2}` — which requires exactly as many values as fields, in order.

You cannot prevent it after the fact, but an unexported `_ struct{}` field makes unkeyed literals a compile error from the start, so the breakage happens once, early, at your choosing rather than at theirs.

</details>

3. ▢ Which change is safe for existing callers?

   - a) Adding a method to an exported interface type
   - b) Adding a method to an exported struct type
   - c) Adding a parameter to an exported function
   - d) Changing an exported field's declared type

<details markdown="1"><summary>Check</summary>

**b)** Adding a method to an exported struct type.

Nothing implements a struct, so nothing can fail to satisfy it. The other three all break somebody: an interface constrains implementers, a signature change breaks call sites, and a field type change breaks every read and write.

</details>

4. ▢ When are functional options worth their cost over an options struct?

<details markdown="1"><summary>Check</summary>

When the option set will keep growing and you cannot coordinate with callers — a published library with a long compatibility horizon. New options are new functions, so nothing existing changes.

For two or three settings in a service you control, an `Options` struct with a documented zero value is fewer moving parts and equally additive. Functional options for three settings is a pattern applied because it is a pattern.

</details>

5. ▢ Interleaving Lesson 9: how is a sentinel error part of your compatibility surface?

<details markdown="1"><summary>Check</summary>

The moment you document it, callers write `errors.Is(err, pkg.ErrNotFound)` and depend on that specific value being in the chain. Removing it, or ceasing to wrap it, silently breaks their branch — with no compile error anywhere.

So documenting which errors are matchable is a commitment, and it is why Lesson 9 said to translate a driver's errors at the boundary rather than wrap them with `%w`. Every `%w` you publish is API.

</details>

## Real-world reps

- [ ] Take a package you have written and list its exported surface. For each item, decide whether you could remove it tomorrow. Whatever you could not is your real API.
- [ ] Add an unexported `_ struct{}` field to an exported struct and try an unkeyed literal. Read the error — that is what you are buying.
- [ ] Tomorrow: find one function in a library you depend on that is marked `Deprecated:`. Check whether your code still uses it, and whether the replacement is a drop-in.

## Going further

- [Go 1 and the Future of Go Programs](https://go.dev/doc/go1compat)
- [Keeping Your Modules Compatible — The Go Blog](https://go.dev/blog/module-compatibility)
- [Go Doc Comments — deprecation](https://go.dev/doc/comment#deprecated)
- [Review Checklist](../reference/review-checklist.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
