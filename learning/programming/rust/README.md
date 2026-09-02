---
title: Rust
description: "Own Rust: design with ownership instead of fighting the borrow checker, then ship the crate"
type: topic
---

# Learning: Rust

Become the engineer trusted to own Rust on a team: able to design with ownership rather than negotiating with the borrow checker, shape errors and APIs so the types carry the invariants, reach for `unsafe` only behind a boundary that can be justified, and ship a crate other people depend on and can upgrade.

**Start here:** [0001. Ownership and Drop](lessons/0001-ownership-and-drop.md)
**Latest lesson:** [0028. Reading a Lifetime Error](lessons/0028-reading-a-lifetime-error.md)

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
| [0001](lessons/0001-ownership-and-drop.md) | Ownership and Drop | Every value has exactly one owner, and the compiler frees it when that owner goes out of scope |
| [0002](lessons/0002-moves-and-copy.md) | Moves and Copy | Assignment moves ownership unless the type is Copy, which is why the old name stops working |
| [0003](lessons/0003-borrowing.md) | Borrowing | Many shared borrows or one mutable borrow, never both, and a borrow ends at its last use |
| [0004](lessons/0004-slices-string-and-str.md) | Slices, String and str | A slice is a borrowed view with a length, and taking &str in an API costs callers nothing |
| [0005](lessons/0005-bindings-and-mutability.md) | Bindings and Mutability | Immutable by default, mut is per binding, and shadowing is a new binding rather than a change |
| [0006](lessons/0006-reading-a-borrow-error.md) | Reading a Borrow Error | Five error codes cover most of stage 1, and each one has an honest fix and a workaround |
| [0007](lessons/0007-structs.md) | Structs and Their Methods | A struct owns its fields, so what you put in one decides who has to keep it alive |
| [0008](lessons/0008-enums.md) | Enums That Carry Data | An enum says a value is exactly one of these shapes, which is the modelling tool the rest of the stage rests on |
| [0009](lessons/0009-option.md) | Option, and Handling Absence | Absence is a value of a different type, so the compiler makes you say what happens when it arrives |
| [0010](lessons/0010-result.md) | Result, and Failure as a Value | A failure is a return value rather than an event, so the signature says what can go wrong before you read the body |
| [0011](lessons/0011-pattern-matching.md) | Pattern Matching | A match must cover every case, and the pattern decides whether you borrowed the value or moved it |
| [0012](lessons/0012-iterators-and-closures.md) | Iterators and Closures | An iterator does nothing until something consumes it, and a closure captures exactly what it uses |
| [0013](lessons/0013-collections.md) | The Collections Worth Knowing | Vec and HashMap cover most of it, and the entry API is the one thing worth learning properly |
| [0014](lessons/0014-propagating-errors.md) | Propagating Errors | The question mark converts as it returns, so the error type in your signature decides what it will accept |
| [0015](lessons/0015-designing-an-error-type.md) | Designing an Error Type | A caller can only handle what your error lets them distinguish, so the shape of it is an API decision |
| [0016](lessons/0016-conversions-and-boundaries.md) | Conversions and Boundaries | A From implementation is where one layer's failure becomes another's, and a derive writes the ones you already understand |
| [0017](lessons/0017-panic-or-error.md) | Panic or Error | A panic says the program is broken and an error says the input was, and a library rarely gets to decide the first |
| [0018](lessons/0018-modules-and-visibility.md) | Modules and Visibility | What you make public is what you have promised to keep, so the module tree is an API decision before it is an organisation one |
| [0019](lessons/0019-documentation-that-compiles.md) | Documentation That Compiles | An example in a doc comment is a test, so the documentation that rots is the documentation nobody ran |
| [0020](lessons/0020-a-library-callers-can-handle.md) | A Library a Caller Can Handle | Split the crate, name the failures, and decide what the binary does that the library must not |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | Traits as Shared Behaviour | How a trait names behaviour several types can provide, and why the trait has to be in scope before you can use it |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | Trait Bounds and Generic Functions | What a bound promises the body and demands of the caller, and what the compiler does with it |
| [0023](lessons/0023-associated-types.md) | Associated Types | Why Iterator names its Item as an associated type rather than a parameter, and what that decides for anyone implementing it |
| [0024](lessons/0024-generics-or-dyn-trait.md) | Generics or dyn Trait | The two dispatch strategies, what each one costs, and the question that actually decides between them |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | Implementing Traits You Do Not Own | Coherence, the newtype pattern, and why a blanket implementation is a commitment rather than a convenience |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | Lifetimes Are Not Durations | What a lifetime parameter says about the relation between borrows, and what elision had been doing for you all along |
| [0027](lessons/0027-types-that-borrow.md) | Types That Borrow | Putting a lifetime parameter on a struct, and deciding whether the type should own its data instead |
| [0028](lessons/0028-reading-a-lifetime-error.md) | Reading a Lifetime Error | The shapes a lifetime error takes, each with the honest fix and the workaround it tempts you into |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Ownership and borrowing](reference/ownership-and-borrowing.md): the rules, the Copy list, the error codes, and the honest fix for each
- [The project](reference/the-project.md): the crate the reps build across the arc, and what state it should be in at the end of each stage
- [Data and control](reference/data-and-control.md): the stage 2 sheet, with the enum and Option and Result decisions, the pattern rules, and the collections
- [Errors and API shape](reference/errors-and-api-shape.md): the stage 3 sheet, with the error-type decisions, the conversion rules, and what a public API commits to
- [Traits and lifetimes](reference/traits-and-lifetimes.md): the stage 4 sheet, with the dispatch decision, the coherence rules, and the lifetime error table

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
