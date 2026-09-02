---
title: Resources
description: Trusted sources for Rust, each annotated with what it covers
type: resources
---

# Rust Resources

## Knowledge

- [Book: "The Rust Programming Language", Steve Klabnik, Carol Nichols and contributors, doc.rust-lang.org](https://doc.rust-lang.org/book/)
  The official book, free and maintained with the language. Use for: stages 1 to 5, and as the default first source for anything in them.

- [Docs: "Rust by Example", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/rust-by-example/)
  The same ground as the book, but as runnable examples with exercises. Use for: a second pass on a concept the prose did not land.

- [Docs: "The Rust Standard Library", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/std/)
  The library, with the guarantees and complexity of each type stated on it. Use for: choosing a collection or a smart pointer, and reading how the standard library solves it.

- [Reference: "The Rust Reference", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/reference/)
  The closest thing to a specification: syntax, semantics, coercions and behaviour considered undefined. Use for: settling what the language guarantees.

- [Book: "The Rustonomicon", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/nomicon/)
  Unsafe Rust in depth, including what invariants `unsafe` code is obliged to uphold. Use for: stage 7, and nowhere earlier.

- [Docs: "Rust Compiler Error Index", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/error_codes/error-index.html)
  Every error code with a minimal reproduction and an explanation. Use for: turning a rejected borrow into an understood rule.

- [Book: "The Cargo Book", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/cargo/)
  Manifests, features, workspaces, dependency resolution and publishing. Use for: stage 8, and anything about `Cargo.toml`.

- [Book: "The Edition Guide", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/edition-guide/)
  What each edition changed and what migration involves. Use for: stating which edition a lesson assumes.

- [Docs: "The rustdoc Book", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/rustdoc/)
  Documentation attributes, intra-doc links, and doctests that run in the test suite. Use for: stage 3, where documentation becomes part of the API.

- [Docs: "thiserror", David Tolnay, docs.rs](https://docs.rs/thiserror/)
  The derive that generates the `Display` and `Error` implementations a typed library error needs, with the attributes it accepts. Use for: stage 3, after writing one of those implementations by hand.

- [Docs: "anyhow", David Tolnay, docs.rs](https://docs.rs/anyhow/)
  One opaque error type for an application's top level, with context chaining and a report that prints the chain. Use for: stage 3, and only above the library boundary.

- [Style guide: "The Rust Style Guide", The Rust Project, doc.rust-lang.org](https://doc.rust-lang.org/style-guide/)
  The formatting conventions the toolchain enforces, and the reasoning behind them. Use for: settling layout questions without argument.

- [Docs: "Rust API Guidelines", The Rust Project, rust-lang.github.io](https://rust-lang.github.io/api-guidelines/)
  A checklist for public interfaces: naming, traits to implement, what to make future-proof. Use for: stage 8, and for review vocabulary.

- [Docs: "Clippy Lints", The Rust Project, rust-lang.github.io](https://rust-lang.github.io/rust-clippy/master/index.html)
  Every lint with its rationale, which doubles as a catalogue of non-idiomatic Rust. Use for: settling an idiom question with a lint name.

- [Book: "Asynchronous Programming in Rust", The Rust Project, rust-lang.github.io](https://rust-lang.github.io/async-book/)
  Futures, executors and the model itself, independently of any runtime. Use for: stage 6, before any runtime's own documentation.

- [Docs: "Tokio Tutorial", Tokio contributors, tokio.rs](https://tokio.rs/tokio/tutorial)
  A complete worked async application from the most widely used runtime. Use for: stage 6 reps, once the model is understood.

- [Tool: "Miri", The Rust Project, github.com/rust-lang/miri](https://github.com/rust-lang/miri)
  An interpreter that detects undefined behaviour in unsafe code, including aliasing violations. Use for: stage 7, checking an `unsafe` block instead of trusting it.

- [Book: "The Rust Performance Book", Nicholas Nethercote, nnethercote.github.io](https://nnethercote.github.io/perf-book/)
  Profiling, allocation, build configuration and the changes that actually pay. Use for: stage 7, and before optimising anything.

- [Book: "Rust for Rustaceans", Jon Gjengset, No Starch Press](https://rust-for-rustaceans.com/)
  The intermediate-to-advanced material the official book stops short of: variance, trait design, unsafe boundaries, project structure. Use for: stages 4, 7 and 8.

- [Book: "Learn Rust With Entirely Too Many Linked Lists", Aria Beingessner, rust-unofficial.github.io](https://rust-unofficial.github.io/too-many-lists/)
  Builds the one data structure that fights ownership hardest, several times, each attempt teaching why the previous failed. Use for: stage 5, when ownership still feels arbitrary.

- [Docs: "Rust Design Patterns", Rust Unofficial contributors, rust-unofficial.github.io](https://rust-unofficial.github.io/patterns/)
  Idioms and anti-patterns with the trade-off stated for each. Use for: naming a pattern in review.

- [Docs: "The Rust RFC Book", The Rust Project, rust-lang.github.io](https://rust-lang.github.io/rfcs/)
  The accepted proposals, each arguing for its own feature and recording what was rejected. Use for: stage 8, and for why the language refuses something.

- [Blog: "Rust Blog", The Rust Project, blog.rust-lang.org](https://blog.rust-lang.org/)
  Release announcements and project decisions from the teams that make them. Use for: checking any version-sensitive claim before teaching it.

- [Blog: Amos Wenger, fasterthanli.me](https://fasterthanli.me/)
  Long, careful articles that follow one Rust problem all the way down, including several on async and on lifetimes. Use for: going one level below the book into why a rule holds.

## Wisdom (Communities)

- [Forum: "The Rust Programming Language Forum", The Rust Project, users.rust-lang.org](https://users.rust-lang.org/)
  A large searchable archive where borrow-checker and lifetime problems are worked through in full, readable without an account. Use for: a rejected borrow that no document seems to cover.

- [Forum: "Rust Internals", The Rust Project, internals.rust-lang.org](https://internals.rust-lang.org/)
  Where language changes are designed and argued in public. Use for: the reasoning behind a rule, when the RFC records the decision but not the debate.

- [Newsletter: "This Week in Rust", This Week in Rust contributors, this-week-in-rust.org](https://this-week-in-rust.org/)
  A weekly archive of releases, articles and RFC activity going back years. Use for: catching what changed during a gap between sessions.

## Gaps

- The async ecosystem is the least settled area here. The async book covers the model and Tokio covers one runtime, and no source covers cancellation safety well; stage 6 will need care and possibly a source that does not exist yet.
- Rust has no formal specification. The Reference is authoritative in practice and explicitly incomplete, so a claim about undefined behaviour goes to the Rustonomicon and the Reference together, and to Miri for evidence.
- Nothing here covers embedded or `no_std`, by design. If the mission ever moves that way, the sources change entirely.
- Release notes are read from the blog rather than from a book. Any lesson naming a stabilised feature says which release stabilised it.
