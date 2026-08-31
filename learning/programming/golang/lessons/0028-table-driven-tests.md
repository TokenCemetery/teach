---
title: 28. Table-Driven Tests
description: One test function, a slice of cases, subtests that name themselves and fail independently
type: lesson
---

# Lesson 28. Table-Driven Tests

**Mission link:** Go's testing package has no assertions and no framework, and the tests are better for it. The table is the idiom that makes that work at scale.
**Primary source:** [Using Subtests and Sub-benchmarks, The Go Blog](https://go.dev/blog/subtests)
**Prerequisites:** [Lesson 27](0027-generics-that-earn-their-keep.md)

## Warm-up

1. ▢ When is a type parameter the wrong tool?

<details markdown="1"><summary>Check</summary>

When the behaviour differs per type, which is what an interface is for, or when there is one concrete type, or when reflection would be needed anyway.

</details>

2. ▢ What does `~int` allow in a constraint that `int` does not?

<details markdown="1"><summary>Check</summary>

Named types with `int` as their underlying type, such as `type UserID int`. Without the tilde, a constraint fails on the first domain type.

</details>

## Know this

A test is a function taking `*testing.T` in a `_test.go` file. There are no assertions: you compare and call `t.Errorf`. That is deliberate: the failure message is written by the person who knows what the test means.

```go
func TestParse(t *testing.T) {
    got, err := Parse("3h")
    if err != nil {
        t.Fatalf("Parse(%q) returned error: %v", "3h", err)
    }
    if want := 3 * time.Hour; got != want {
        t.Errorf("Parse(%q) = %v, want %v", "3h", got, want)
    }
}
```

`t.Errorf` records a failure and continues; `t.Fatalf` stops this test. Use `Fatalf` when continuing would produce noise, such as a nil pointer to dereference, and `Errorf` when you want to see every failure at once.

The message convention is `functionCall = got, want expected`. It looks terse and it means a failing test tells you the input, the result and the expectation on one line, without opening the file.

### The table

When there are more than two cases, a table beats copy-paste:

```go
func TestParse(t *testing.T) {
    tests := []struct {
        name    string
        in      string
        want    time.Duration
        wantErr bool
    }{
        {name: "hours", in: "3h", want: 3 * time.Hour},
        {name: "minutes", in: "45m", want: 45 * time.Minute},
        {name: "empty", in: "", wantErr: true},
        {name: "garbage", in: "banana", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Parse(tt.in)
            if (err != nil) != tt.wantErr {
                t.Fatalf("Parse(%q) error = %v, wantErr %v", tt.in, err, tt.wantErr)
            }
            if err != nil {
                return
            }
            if got != tt.want {
                t.Errorf("Parse(%q) = %v, want %v", tt.in, got, tt.want)
            }
        })
    }
}
```

`t.Run` creates a **subtest**: it gets its own name, fails independently, and can be selected from the command line.

```bash
go test -run 'TestParse/empty' ./...
```

Adding a case is one line, which is the property that makes people actually add them. Note that the zero value does useful work again: omitted fields mean "no error expected" and "empty input", and the struct literal stays readable.

### Parallel subtests

```go
t.Run(tt.name, func(t *testing.T) {
    t.Parallel()
    ...
})
```

Parallel subtests pause until the parent test function returns, then run together. Two things to know: since Go 1.22 the loop variable is per-iteration, so the old `tt := tt` line is no longer needed, and you will still see it everywhere. And parallel tests sharing state is exactly the situation `-race` was built for.

### Helpers and cleanup

```go
func newTestStore(t *testing.T) *Store {
    t.Helper()                        // failures point at the caller, not here
    db := openTestDB(t)
    t.Cleanup(func() { db.Close() })  // runs at the end of this test, even on failure
    return New(db)
}
```

`t.Helper()` keeps the reported line number useful. `t.Cleanup` is `defer` for tests, and it works correctly with subtests and parallel tests where a plain `defer` in the parent would fire too early.

### Golden files

For output too large to inline, such as rendered templates, formatted reports or JSON, keep the expected result in `testdata/` and compare against it. The directory name is special: the Go tool ignores it when building.

The convention is a `-update` flag that rewrites the golden files, so regenerating is deliberate and the diff is reviewed like any other change:

```go
var update = flag.Bool("update", false, "update golden files")
```

### What not to reach for

You do not need an assertion library. `testify` is widely used and adds a dependency, a second vocabulary, and failure messages nobody wrote for this test. `google/go-cmp` is the one worth adopting, because comparing structs and slices by hand is genuinely awkward. `cmp.Diff(want, got)` prints a readable diff, and it handles unexported fields explicitly rather than by accident.

Run tests with `-race` in CI, and with `-count=1` when you want to defeat the test cache.

## Practice

1. ▢ Why `t.Run` rather than one test function per case?

<details markdown="1"><summary>Check</summary>

Each subtest reports independently, so one failure does not hide the next; each gets a name that appears in the output; and `-run 'TestX/case'` selects one.

The deeper reason is cost: adding a case to a table is one line, so cases get added. A new function per case is enough friction that edge cases quietly do not get tested.

</details>

2. ▢ What is the difference between `t.Errorf` and `t.Fatalf`?

<details markdown="1"><summary>Check</summary>

`Errorf` marks the test failed and continues. `Fatalf` marks it failed and stops that test function immediately.

Use `Fatalf` when continuing is pointless or unsafe, as with an error where you expected a value, so the next line would dereference nil. Use `Errorf` when independent checks can all report, which gives you the whole picture from one run.

</details>

3. ▢ Which line stops being necessary in Go 1.22 and later?

   - a) `t.Parallel()` at the top of the subtest
   - b) `tt := tt` before the subtest closure
   - c) `t.Helper()` inside a test helper
   - d) `t.Cleanup(...)` for resource teardown

<details markdown="1"><summary>Check</summary>

**b)** `tt := tt` before the subtest closure.

Loop variables are per-iteration from Go 1.22, so the shadow copy is redundant, subject to the `go` directive in `go.mod`. The other three do jobs the language change did not touch.

</details>

4. ▢ Why does `t.Cleanup` beat `defer` in a helper that a parallel subtest calls?

<details markdown="1"><summary>Check</summary>

A `defer` in the helper fires when the *helper* returns, which is before the test has used the resource. Moving it to the calling test does not work either, once the subtest is parallel: the parent function returns while the parallel subtests are still running, so its defers fire too early.

`t.Cleanup` is registered against the specific `*testing.T` and runs when *that* test finishes, which is the semantics you wanted in both cases.

</details>

5. ▢ Interleaving Lesson 11: your service type takes a `UserStore` interface. How do you fake it in a test?

<details markdown="1"><summary>Check</summary>

Write a struct in the test file with the one or two methods the interface requires, returning whatever the case needs. Ten lines, no dependency, no code generation.

```go
type fakeStore struct{ user *User; err error }
func (f fakeStore) GetUser(context.Context, string) (*User, error) { return f.user, f.err }
```

This is the payoff for declaring the interface in the consumer and keeping it small. A mocking framework is what you need when the interface has fourteen methods, so the framework is treating the symptom.

</details>

## Real-world reps

- [ ] Convert one existing test with repeated blocks into a table with `t.Run`. Run `go test -v` and read the subtest names.
- [ ] Add a deliberately failing case and read the message. If it does not tell you the input and both values, rewrite it until it does.
- [ ] Tomorrow: add `-race` to the test command in your CI if it is not there, and run the suite locally with it once to see what falls out.

## Going further

- [Using Subtests and Sub-benchmarks, The Go Blog](https://go.dev/blog/subtests)
- [`testing` package](https://pkg.go.dev/testing)
- [`google/go-cmp`](https://pkg.go.dev/github.com/google/go-cmp/cmp): `cmp.Diff` for struct and slice comparison
- [Toolchain Commands](../reference/toolchain-commands.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
