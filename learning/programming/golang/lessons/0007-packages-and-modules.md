---
title: 7. Packages and Modules
description: A directory is a package, a capital letter is the whole visibility system, and internal is enforced
type: lesson
---

# Lesson 7. Packages and Modules

**Mission link:** Go's unit of encapsulation is the directory, not the type. Getting this wrong produces a repository that fights every import you write, and it is hard to undo later.
**Primary source:** [How to Write Go Code, The Go Authors](https://go.dev/doc/code)
**Prerequisites:** [Lesson 6](0006-methods-and-method-sets.md)

## Warm-up

1. ▢ Which methods are in the method set of `T`, and which in the method set of `*T`?

<details markdown="1"><summary>Check</summary>

`T` has only the value-receiver methods. `*T` has both value- and pointer-receiver methods. The asymmetry is why a value can fail to satisfy an interface its pointer satisfies.

</details>

2. ▢ What does `go vet`'s `copylocks` check protect you from?

<details markdown="1"><summary>Check</summary>

Copying a value that contains a `sync.Mutex` or similar, which silently produces two independent locks where the code assumes one.

</details>

## Know this

**A package is a directory.** Every `.go` file in one directory declares the same package name, and files are otherwise interchangeable: Go has no header files, no ordering between files, and no rule about which type lives where. Splitting a package across five files is a readability choice with no semantic weight.

**A capital letter is the entire visibility system.** An identifier starting with an uppercase letter is exported and visible to importers. Anything else is package-private. There is no `protected`, no `friend`, and no per-symbol export list. The unit of privacy is the package, so two types in the same package can always see each other's unexported fields. That is a feature rather than a leak, and it is why Go packages tend to be larger than Java packages.

### Modules

A **module** is a collection of packages released together, rooted at a `go.mod`:

```text
module github.com/you/svc

go 1.26
```

The module path prefixes every import inside it, so a package in `internal/store/` is imported as `github.com/you/svc/internal/store`. The `go` directive states the minimum language version the module requires. It changes what the compiler accepts, and it is why Go 1.22's loop-variable change could ship without breaking older code.

Since Go 1.26, `go mod init` writes a slightly older version than the toolchain you ran it with, so a new module does not immediately demand the newest release from everyone who builds it.

The commands worth memorising now:

| Command | Does |
|---|---|
| `go run ./cmd/svc` | build and run, no binary left behind |
| `go build ./...` | compile everything, report errors |
| `go test ./...` | run every test in the module |
| `go vet ./...` | static checks the compiler does not make |
| `go mod tidy` | add what is imported, remove what is not |
| `go fmt ./...` | canonical formatting, not negotiable |
| `go fix ./...` | rewrite to modern idioms, rebuilt in Go 1.26 |

`gofmt` output is the only accepted format for Go source. There is no style debate to have, and that is deliberate.

### `internal/` is enforced by the compiler

A directory named `internal` limits imports to code rooted at its parent:

```text
github.com/you/svc/
├── cmd/svc/main.go              # package main
├── internal/store/store.go      # importable only within github.com/you/svc
└── httpapi/server.go            # importable by anyone
```

![The module drawn as a dashed subtree holding cmd/svc, internal/store and httpapi. An import inside the subtree reaches internal/store; another module's import of httpapi crosses the boundary and arrives, while its import of internal/store stops at that boundary.](images/only-from-inside-the-subtree.svg)

Two imports cross the boundary and one of them is turned back. Which one depends only on where the target sits in the tree.

This is not a convention: the toolchain rejects the import. It is the mechanism for having a large package surface inside your own module while publishing a small one, and it is the first tool to reach for when you are unsure whether something should be public. Start everything in `internal/`; move it out when an external caller genuinely needs it. That direction is easy, and the reverse is a breaking change.

### The package name is part of every call site

Callers write `store.New`, not `New`. So the package name and the identifier are read together, and repeating the package in the name stutters:

```go
store.NewStore()   // stutter
store.New()        // idiomatic

http.HTTPServer    // stutter
http.Server        // idiomatic
```

Package names are short, lowercase, one word, no underscores, no plurals: `store`, `httpapi`, `token`. A package named `util`, `common`, `helpers` or `base` has no name because it has no subject, and it becomes the place everything lands. That is the single most reliable predictor of a repository that is hard to work in.

### Two constraints that shape layout

**Import cycles are a compile error.** Go has no forward declarations and no lazy resolution. If `a` imports `b`, then `b` can never import `a`. This is the constraint that most often forces a design change, usually by extracting the shared type into a third package that both import.

**`init()` runs before `main`.** Each package's variables are initialised, then its `init` functions run, and all of that completes before any importer's code runs. It is genuinely useful for registering a driver, and it is a poor place for anything you might want to fail, configure, or test; see [Lesson 23](0023-configuration-and-startup.md). Prefer explicit construction in `main`.

## Practice

1. ▢ You have `internal/store` and want to use it from a second repository. What does the compiler say, and what are your options?

<details markdown="1"><summary>Check</summary>

The build fails: use of internal package not allowed. The rule is that `internal/x` is importable only by code rooted at `internal`'s parent directory.

Options: move the package out of `internal` and accept that it is now public API you have to keep compatible, or extract the shared part into its own module. The error is the design question arriving on time.

</details>

2. ▢ Which name is idiomatic for a package that decodes JWTs?

   - a) `package jwtutils`
   - b) `package JWTDecoder`
   - c) `package jwt_decode`
   - d) `package jwt`

<details markdown="1"><summary>Check</summary>

**d)** `package jwt`.

Call sites read `jwt.Decode(...)`, which says everything. `jwtutils` names a grab bag, `JWTDecoder` is capitalised and repeats what the function will already say, and `jwt_decode` uses an underscore that gofmt will not remove but every reviewer will.

</details>

3. ▢ Package `order` imports `payment`, and now `payment` needs an `order.ID`. Name two ways out.

<details markdown="1"><summary>Check</summary>

Extract `ID` into a small third package both import. That is often the right call, and the reason repositories grow a `types`-shaped package that should still be given a real name.

Or invert the dependency: define the narrow interface `payment` needs *inside* `payment`, and let `order` satisfy it. Go's implicit interfaces make this cheap, and it is usually the better design, per Lesson 11.

Merging the two packages is the third option, and it is right more often than people expect.

</details>

4. ▢ Why does Go not need a `private` keyword?

<details markdown="1"><summary>Check</summary>

Because the case of the first letter carries the information, and the boundary is the package rather than the type. Within a package everything is visible; across the boundary only exported identifiers are.

The consequence to internalise is that a Go package is a bigger unit than a Java class. Splitting a type and its helpers into separate packages to "encapsulate" them buys nothing and costs you an import cycle later.

</details>

5. ▢ Interleaving Lesson 1: your package needs a registry populated at startup. Why prefer building it in `main` over an `init()`?

<details markdown="1"><summary>Check</summary>

Because `init` runs implicitly, cannot return an error, and cannot be skipped by a test. A failure inside it kills the process before `main` gets a chance to report anything useful, and any test that imports the package pays the cost.

Explicit construction in `main` gives you an error to handle, a dependency to substitute in tests, and an order you can read. `init` earns its keep for self-registration, such as a database driver adding itself to `database/sql`, and little else.

</details>

## Real-world reps

- [ ] Create a module with `cmd/svc/main.go` and `internal/store/store.go`. Import the store from main, build it, and then try to import it from a second module to watch the toolchain refuse.
- [ ] Run `go vet ./...` and `go fix ./...` on a scratch package. Read what `go fix` proposes. The Go 1.26 modernizers are a fast way to see which idioms have moved on.
- [ ] Tomorrow: open a repository you work in and list every package whose name does not describe a subject. That list is your refactoring backlog.

## Going further

- [How to Write Go Code](https://go.dev/doc/code)
- [Package names, The Go Blog](https://go.dev/blog/package-names)
- [Organizing a Go module](https://go.dev/doc/modules/layout): the layouts the Go team actually recommends
- [Lesson 14. Designing a Package](0014-designing-a-package.md): the same material as a design skill rather than a mechanism
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
