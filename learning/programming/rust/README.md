---
title: Rust
description: "Own Rust: design with ownership instead of fighting the borrow checker, then ship the crate"
type: topic
---

# Learning: Rust

Become the engineer trusted to own Rust on a team: able to design with ownership rather than negotiating with the borrow checker, shape errors and APIs so the types carry the invariants, reach for `unsafe` only behind a boundary that can be justified, and ship a crate other people depend on and can upgrade.

**Latest lesson:** _none yet_

## Success looks like

- Predict which borrow the compiler will reject, and why, before compiling.
- Choose between owning, borrowing, reference counting and interior mutability from how long the data actually has to live.
- Design an error type callers can handle, and say when panicking is the correct choice instead.
- Remove duplication with traits and generics without making the signatures unreadable, and know when dynamic dispatch is the better answer.
- Write async code that does not stall, and explain what holding a lock across an `await` point does.
- Justify every `unsafe` block by the invariant it upholds, keep it behind a safe interface, and check it with a tool rather than by reading.
- Publish a crate with documentation, tests, and a public API you can evolve without breaking dependants.
- Review Rust and name precisely why a lifetime annotation, a `clone`, or a shared mutex is covering for a design problem.

## Constraints

- Assumes no prior Rust and no systems-programming background. The stack, the heap and memory layout are taught inside the arc, because ownership is unteachable without them.
- Needs only the stable toolchain and a terminal on any supported OS. Nothing in the arc requires paid tooling, a cloud account, or nightly Rust.
- **Reps are expected to fail to compile.** That is the feedback loop, not a setback: predict what the compiler will say, then find out, and treat the difference as the lesson.
- Reps are small programs that fit one sitting. Spacing them across days is the mechanism, not an inconvenience.
- Editions and releases matter here. Where a lesson depends on an edition or a stabilised feature, it says which, and version-sensitive claims are checked against the release notes rather than recalled.

## Out of scope

- Embedded targets and `no_std` as subjects in their own right.
- WebAssembly, graphical interfaces, and game engines.
- Web frameworks as subjects. Async needs examples, and they stay as small as the concept allows.
- Procedural macro authoring. Declarative macros appear where the standard library's own use of them has to be read.
- Foreign function interfaces past what the `unsafe` boundary material needs. Wrapping a real C library is a separate undertaking.
- Compiler and borrow-checker internals past the point where they stop predicting what the compiler will accept.

## The arc

Eight stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Ownership | Values, stack and heap, moves, `Copy`, borrows and their rules, slices, `String` versus `&str`, shadowing | Can predict a move or borrow error before the compiler reports it |
| 2. Data and control | Structs, enums, `Option` and `Result`, pattern matching and exhaustiveness, iterators, closures, the collections worth knowing | Models with enums, and handles absence without reaching for `unwrap` |
| 3. Errors and API shape | Propagation with `?`, custom error types, `From` conversions, panic versus error, modules and visibility, writing documentation that compiles | Writes a library whose failures a caller can actually handle |
| 4. Traits, generics and lifetimes | Trait bounds, associated types, generics versus dynamic dispatch, the orphan rule, lifetime annotations and elision, why a lifetime is not a duration | Reads a lifetime error as information rather than as an obstacle |
| 5. Sharing and threads | `Box`, `Rc` and `Arc`, `RefCell` and `Mutex`, `Send` and `Sync`, threads, channels, deadlock and poisoning | Chooses a sharing strategy from the data rather than from habit |
| 6. Async | Futures and executors, tasks and cancellation, why a blocking call in async is a bug, locks across `await`, what pinning is for | Writes async code that does not stall, and can explain where it would |
| 7. Unsafe and performance | What `unsafe` actually promises, undefined behaviour, encapsulating an invariant, checking with Miri, benchmarking, allocation and copying costs | Can defend an `unsafe` boundary, and proves a performance claim with a measurement |
| 8. Judgment | Publishing, semantic versioning of a public API, the API guidelines, review, reading the standard library and the RFCs for answers | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
