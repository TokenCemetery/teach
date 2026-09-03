---
title: Glossary
description: Canonical terms for Rust
type: glossary
---

# Rust Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Four words carry a meaning from other languages that Rust does not share, and each mistranslation is one of the reasons the borrow checker feels arbitrary, so all four are pinned from the start:

**Ownership**:
The property that exactly one binding is responsible for a value and for releasing it, transferred by assignment or by passing it on. It is a compile-time rule about responsibility, enforced with no runtime bookkeeping.
_Avoid_: reference counting, garbage collection, scope

**Borrow**:
A temporary access to a value that someone else still owns, created with `&` or `&mut`. Shared borrows may coexist, a mutable borrow may not coexist with any other, and both are checked at compile time.
_Avoid_: pointer, alias, reference (in the C++ sense), view

**Lifetime**:
A region of code over which a borrow must remain valid, and a constraint the compiler checks rather than a duration it measures. Annotating one relates the lifetimes of inputs and outputs; it never makes a value live longer.
_Avoid_: scope, duration, retention, allocation

**Unsafe**:
A promise from the author that the compiler's usual proof obligations are met by hand, in a block or function where a few extra operations become available. It disables specific checks and never disables the borrow checker or the rules about undefined behaviour.
_Avoid_: unchecked, dangerous, raw, escape hatch

## Terms

**Associated type**:
A type placeholder a trait declares and each implementing type fills in exactly once, named in a bound as `Iterator<Item = u32>` and, where two traits in scope declare the same name, as the fully qualified `<Type as Trait>::Item`. Declare one where a type has a single sensible choice, and take a generic parameter where several are sensible.
_Avoid_: generic parameter, type argument, `Trait<Type>` as though the placeholder were positional

**Auto trait**:
A trait the compiler implements for a type structurally, from what the type contains, rather than from any written `impl`. `Send` and `Sync` are the two that matter here, and because nobody writes them, a type loses one because of something several layers inside it.
_Avoid_: derived trait in the attribute sense, marker trait as a synonym, a trait you can add by hand

**Backpressure**:
A bounded channel's `send` blocking once the queue is full, so a fast producer is paced by its consumer rather than allowed to grow an unbounded queue. It is a design tool, chosen with the bound.
_Avoid_: a limitation, a bug, a full buffer being an error, throttling as a synonym

**Binding mode**:
The implicit `ref`, `ref mut` or move state a sub-pattern inherits when a non-reference pattern is matched against a reference, which is why matching `&record` gives you borrowed fields without writing `&` anywhere. From the 2024 edition an explicit `&` pattern may not be layered on top of an implicit borrow.
_Avoid_: dereference, ref keyword as the only way, move, coercion

**Breaking change**:
A released version that fails to compile for some caller of the previous public API, judged by what compiles rather than by what you intended. Adding a public field, an enum variant or a trait method without a default all qualify, and a tool can check the shape while only your tests can check the behaviour.
_Avoid_: any refactor, anything that feels large, only a removal, something the version number decides after the fact

**Busy-spin**:
An executor that answers `Poll::Pending` by polling again immediately, so it makes progress without a waker at the cost of occupying a processor for nothing. It is what a hand-written first executor does, and it is the reason the waker contract exists.
_Avoid_: polling as a synonym, blocking, a tight loop being merely inefficient

**Cancel safety**:
The property that dropping a future before it completes loses nothing that cannot be retried. It is a statement about that future's own state rather than about the code around it, and it is documented method by method rather than derived.
_Avoid_: every use of `select!` being unsafe, cancellation being prevented, a synonym for cancellation

**Cancellation**:
Dropping a future or task before it completes. Nothing is notified and no error is delivered: the state machine stops at the await point it was suspended at, and only `Drop` runs.
_Avoid_: a signal, an exception, an interrupt, anything the cancelled code can observe

**Channel**:
A queue with a sending half and a receiving half that moves ownership of each value between threads, so no two threads hold the same value and there is nothing to lock. Each half fails once the other is dropped, which is how a pipeline ends.
_Avoid_: a shared buffer, a lock with extra steps, a queue both ends may read

**Closure**:
An anonymous function that captures what its body uses from the enclosing scope, by shared borrow, mutable borrow or move, whichever is the least it needs. Which of `Fn`, `FnMut` and `FnOnce` it satisfies follows from what it does with the capture rather than from how it is written.
_Avoid_: lambda as a synonym for its type, function pointer, block, thunk

**Combinator**:
A method on `Option` or `Result` that transforms or inspects the value inside without unwrapping it, such as `map`, `and_then` or `ok_or`. Each answers one question, and a chain of them is the alternative to a `match` rather than a replacement for thinking about the absent case.
_Avoid_: helper, functor, adapter, which is an iterator's word, chaining as a style

**Confidence interval**:
The range a benchmarking harness reports in place of a single figure, which is what makes a measurement quotable: it says how much of the difference you are seeing is the change and how much is noise.
_Avoid_: the centre value alone, a guarantee, precision that came free

**Copy**:
A marker trait for types that are duplicated rather than moved on assignment, because they are plain data with nothing to free. It requires `Clone` and is incompatible with `Drop`, and `&T` has it while `&mut T` deliberately does not.
_Avoid_: value type, primitive, cheap type

**Data race**:
Two threads accessing the same location without synchronisation where at least one writes, which is undefined behaviour rather than merely a wrong answer. It is not the same as a lost update, which is a wrong answer produced by correctly synchronised code.
_Avoid_: a lost update, any concurrency bug, something a correct-looking run rules out

**Deadlock**:
Two or more threads each holding a lock the other needs, so none can proceed. It presents as a hang with no panic, no message and no exit code, and it survives testing because low contention usually lets both threads through.
_Avoid_: a slow program, a livelock, an error the compiler could catch

**Deref coercion**:
The compiler's automatic conversion from a reference to an owning type into a reference to what it derefs to, such as `&String` into `&str`. It is why taking the borrowed type in a signature costs callers nothing.
_Avoid_: implicit cast, auto-conversion, upcasting

**Discriminant**:
The value an enum stores to say which variant it holds. It costs space unless the compiler can hide it in a bit pattern the payload cannot use, so an enum is generally its largest variant plus the discriminant, rounded to the alignment its fields demand.
_Avoid_: tag as a synonym for the whole value, index, type id, variant

**Disjoint capture**:
A closure capturing individual fields of a struct rather than the whole struct, from the 2021 edition onward, so touching one field leaves the others usable. It removes a `clone` the older whole-struct rule used to force.
_Avoid_: partial move, field borrow as a general rule, split borrow of a slice, move

**Doctest**:
A fenced code block inside a doc comment, which `cargo test` compiles and runs as a test. It is the mechanism that stops an example rotting, and a line beginning with `#` inside the fence is compiled without being shown, which is how an example uses `?` without teaching a bad habit.
_Avoid_: example, unit test, snippet, comment

**Downcast**:
Recovering a concrete type from a trait object such as `Box<dyn Error>`, by naming the type you expect and asking. A `None` answer means the guess was wrong or the value was never that type, and the two are indistinguishable, which is the cost of erasing the type in the first place.
_Avoid_: cast, conversion, coercion, pattern match

**Drop**:
The point at which a value's owner goes out of scope and its destructor runs, releasing whatever it owns. It happens in reverse declaration order within a scope, which makes it the defined moment a lock is released or a file is closed.
_Avoid_: free, garbage collection, finalisation

**Dyn compatibility**:
The property a trait needs before the compiler can build a vtable for it and let it stand behind a trait object, lost by an associated function with no receiver or by a generic method, and recoverable one method at a time with a `where Self: Sized` bound. Sources written before the compiler's diagnostics were renamed in release 1.83 call the same property object safety.
_Avoid_: object safety as the current term, sealed trait, interface

**Elision**:
The rules by which the compiler supplies a lifetime the signature left unwritten: each elided input position gets its own, a single input lends its lifetime to the output, and a method with a receiver lends the receiver's. It is a stated rule with a resolvable answer rather than a guess, so a signature it cannot resolve is rejected instead of assumed.
_Avoid_: inference, omission, the compiler guessing, defaulting to `'static`

**Error source**:
The underlying cause a wrapping error returns from `Error::source`, which is what lets a caller or a log print the whole chain. A layer's own `Display` message says what that layer knows and leaves the cause to the source, or the printed chain repeats itself.
_Avoid_: cause as a synonym for the message, backtrace, context, inner error as an opaque field

**Executor**:
The loop that owns a future, calls `poll` and supplies the waker. It is the smaller half of a runtime, which adds a timer and a source of readiness on top of it.
_Avoid_: runtime as a synonym, scheduler, thread pool, something the standard library ships

**Exhaustiveness**:
The compiler's requirement that a `match` account for every possible value, which is what makes adding an enum variant a compile error rather than a silent gap. Satisfying it with a catch-all on an enum you own gives the guarantee away.
_Avoid_: completeness, default case, total function, coverage in the testing sense

**Feature**:
A named, additive switch declared in the manifest that turns on code or an optional dependency, with `default` being an ordinary feature that happens to be enabled. It may only add: a feature that changes or removes behaviour is a design error, because a build gets the union of everything anyone asked for.
_Avoid_: a configuration option, a build profile, a way to offer two behaviours, something only your crate sees

**Feature unification**:
Cargo resolving one set of features per package per build, so if two dependants ask for different features everybody in that build gets both. It is the reason a feature that subtracts breaks somebody you never hear from.
_Avoid_: per-dependant features, isolation between consumers, something a lock file prevents

**Future**:
A value implementing one method, `poll`, which either yields a result or says not yet. Constructing one runs nothing, and an `async fn` returns one, so something has to poll it before any of its body executes.
_Avoid_: a promise, a thread, a running computation, a callback

**Guard**:
The value a borrow or a lock hands back, whose `Drop` ends the access it granted, as with `RefMut` from a `RefCell` or `MutexGuard` from a `Mutex`. Its scope, not the call that produced it, decides how long the access lasts.
_Avoid_: a handle you may keep, a reference, a token to pass around

**Happens-before**:
The relation a `Release` store and a matching `Acquire` load establish between two threads, which is what makes everything written before the store visible after the load.
_Avoid_: wall-clock order, any two operations on the same atomic, something a stronger ordering makes faster

**Higher-ranked bound**:
A trait bound quantified over every lifetime rather than one particular lifetime, which is what a closure bound such as `Fn(&str) -> usize` already means. Offering a closure fixed to one lifetime against such a bound is what the compiler reports as an implementation not being general enough, contrasting a lifetime it needs for any against one the closure provides for some.
_Avoid_: lifetime parameter, generic lifetime, a `'static` bound

**Interior mutability**:
Mutating a value through a shared reference, using a type that enforces the borrow rule itself instead of leaving it to the compiler. `Cell` and `RefCell` do it in one thread and `Mutex` and `RwLock` across threads, and the check moves from compile time to run time.
_Avoid_: a hole in the borrow rule, `unsafe` by another name, mutability you get for free

**Intra-doc link**:
A bracketed item path in a doc comment that rustdoc resolves against the crate's own items, so a rename moves the link with it. A broken one is reported by a lint rather than shipping as dead text.
_Avoid_: markdown link, external URL, reference, anchor

**Invariant**:
A property your own code guarantees at a given point, whose violation is a bug in that code rather than bad input. That distinction is what decides between a panic and a `Result`, since a caller cannot fix your broken invariant and can often handle bad input.
_Avoid_: precondition on the caller, validation, assertion, contract with the user, and the variance sense of the word, where a type being invariant over a lifetime means the lifetime cannot be substituted at all

**Iterator**:
A type with a `next` method returning `Option<Item>`, which is where absence and iteration meet. Adapters build a new iterator and do nothing until a consumer asks for items, so a chain with no consumer runs no code at all.
_Avoid_: loop, generator, stream, which is async, collection

**Lost update**:
An increment or write silently overwritten because two threads read the same value before either wrote, which is what separate lock acquisitions for a read and a write allow. Its size is not predictable and neither is its rate, so an approximate assertion can pass while the code is wrong.
_Avoid_: a small drift, rounding, something a retry fixes, a bug that always shows up

**Memory ordering**:
The constraint an atomic operation places on which other operations may be observed around it. It is about visibility and ordering rather than speed, and a stronger ordering does not make a write propagate sooner.
_Avoid_: a delay, a flush, a speed setting, something testable by running it once

**Microbenchmark**:
A measurement of one function or loop in isolation. Its ratio is evidence about that function and nothing else, so it cannot tell you whether the code path matters in a real run.
_Avoid_: a profile, proof that a change matters, a number that generalises to another machine

**Monomorphisation**:
The compiler's generation of one fully concrete copy of a generic item for each set of type arguments it is used with, which is why a generic call is a direct call that can be inlined, and why a widely instantiated generic costs compile time and binary size rather than nothing.
_Avoid_: erasure, dynamic dispatch, specialisation, inlining as a synonym

**Move**:
The transfer of ownership that assignment or argument passing performs on a non-**Copy** type, after which the source binding is unusable. It is compile-time bookkeeping rather than a runtime operation.
_Avoid_: transfer, copy, reassignment

**MSRV**:
The minimum supported Rust version a crate declares with `rust-version` in its `[package]` table, which cargo enforces by refusing to build on an older toolchain. Raising it is treated as a minor incompatibility, so it is a promise with a cost rather than a note.
_Avoid_: the version you happen to use, the newest release, something only documentation records

**Must-use attribute**:
An attribute on a function, or on a type returned by one, that makes the compiler warn when the result is discarded. It is a warning rather than an error, and it applies to any type worth not ignoring rather than only to `Result`.
_Avoid_: a compile error, something only `Result` needs, a guarantee the value is handled

**Newtype**:
A local tuple struct wrapping a single value, used to implement a foreign trait the orphan rule would otherwise forbid, or to keep a foreign type's API from becoming your public API. Nothing forwards automatically, which is both its cost and the point.
_Avoid_: a type alias, a zero-cost synonym, something whose methods you inherit

**Niche optimisation**:
The compiler's use of an impossible bit pattern in a payload to store an enum's discriminant, which is why `Option<&T>` and `Option<Box<T>>` are the same size as the pointer they wrap. The standard library documents that guarantee for those cases; other sizes are not promised.
_Avoid_: compression, packing, null pointer as a value, alignment

**Non-exhaustive**:
The attribute that forces a downstream crate's `match` on a type to include a catch-all arm, so a variant can be added later without breaking them. It has no effect inside the crate that defines the type, which is why demonstrating it needs two crates.
_Avoid_: unfinished, unstable, sealed, private

**Non-lexical lifetimes**:
The analysis under which a borrow ends at its last use rather than at the end of its enclosing scope. It is why many borrow errors are fixed by moving one line instead of restructuring.
_Avoid_: scope-based borrows, lexical scoping

**Option**:
The standard library's enum for a value that may be absent, `Some(T)` or `None`, which replaces null by making absence a different type from presence. A signature therefore says where absence can arrive, and the compiler will not let one stand in for the other.
_Avoid_: null, nullable, default value, error

**Orphan rule**:
The coherence rule that a trait implementation needs the crate to own either the trait or the type, which is why a conversion between two foreign types will not compile. It is what stops two crates providing conflicting implementations for the same pair.
_Avoid_: visibility, privacy, ownership in the borrow sense, a package-level rule

**Panic**:
The failure path for a broken invariant in your own code, which unwinds the thread with a message, a file and a line rather than returning anything. It is not the same event as an `Err`, which returns normally and prints nothing on its own.
_Avoid_: exception, error, crash, abort

**Pin**:
A wrapper around a pointer promising that its target will not move again, which is why `poll` takes a pinned receiver: a generated future can hold borrows into its own state, so relocating it once polling has begun would leave them dangling.
_Avoid_: immutability, a lock, a borrow, pinning a value to a thread

**Poisoning**:
A lock marking itself unusable after a thread panicked while holding its guard, because it cannot know whether the data's invariant survived. Later locks return an `Err` that still carries the guard, so the data and any partial mutation remain reachable, and `clear_poison` clears the mark once it has been checked.
_Avoid_: the data being lost, a corrupted lock, an error you must `unwrap` past

**Poll**:
The two-variant enum a future's `poll` returns, either pending or ready. Pending is a promise to wake the caller later rather than a request to be asked again.
_Avoid_: input and output polling, a busy loop, a status code

**Provenance**:
The information a pointer carries beyond its address, recording which allocation it came from and what it may reach. A round trip through an integer can lose it, leaving an address that is numerically right and not usable.
_Avoid_: the address, a type, something a cast preserves automatically

**Re-export**:
A `pub use` that presents an item at a shorter public path than the one its file layout gives it, so a library can move code without breaking the paths callers type. The path a caller writes is part of the public API, which is what makes this a design tool rather than a tidying one.
_Avoid_: import, alias, copy, module declaration

**Reborrow**:
Producing a new borrow from an existing one, which the compiler inserts implicitly when a `&mut T` is passed to a function so the original stays usable. Where it does not fire, such as storing a `&mut` in a struct, the move is real.
_Avoid_: copy, pass-through, nested borrow

**Reference cycle**:
Two or more counted pointers holding each other alive, so no count reaches zero and the values are never dropped. It compiles, runs, and leaks, and it is broken by making one direction a weak pointer.
_Avoid_: a borrow error, something the compiler catches, a double free, an infinite loop

**Refutable pattern**:
A pattern that may fail to match some value of its type, which is why it is allowed in `if let`, `while let` and `let ... else` and rejected in a plain `let` or a function parameter. An irrefutable pattern always matches, and the distinction decides which construct will accept it.
_Avoid_: invalid pattern, optional match, guard, wildcard

**Result**:
The standard library's enum for an operation that may fail, `Ok(T)` or `Err(E)`, used when the caller could reasonably do something about the failure. The `?` operator returns early on `Err`, which is what makes propagating one cheap enough to do everywhere.
_Avoid_: exception, panic, Option, status code

**Runtime**:
An executor plus what real work needs around it: a timer, a source of input and output readiness, and a scheduler with worker threads. Rust ships none, so a program chooses one, and the flavour it chooses decides where a future runs.
_Avoid_: executor as a synonym, a virtual machine, a garbage collector, part of the language

**SAFETY comment**:
The comment attached to an `unsafe` block naming the invariant that makes it sound, and which line or caller guarantees that invariant. It is written for the next reader rather than for the compiler, and it is what makes the block reviewable.
_Avoid_: a note expressing confidence, a description of what the code does, decoration

**Scoped thread**:
A thread spawned inside a `thread::scope` block, which may borrow non-`'static` data because the scope guarantees every one of its threads is joined before it returns.
_Avoid_: any thread spawned inside a scope, a lightweight thread, a thread you need not join

**Sealed trait**:
A public trait that no other crate can implement, achieved by giving it a supertrait that is public in name only and unreachable outside your crate. It keeps the right to add methods later, at the cost of forbidding implementations you did not write.
_Avoid_: a private trait, `#[non_exhaustive]`, a trait nobody may call

**Send**:
A marker meaning a value may be moved to another thread. It says nothing about sharing, so a type can be `Send` and still be unusable behind a shared reference from two threads.
_Avoid_: thread-safe as a general claim, `Sync`, safe to share

**Shadowing**:
Declaring a new binding with the name of an existing one, so the earlier binding becomes unreachable. It is not mutation: the type may change, and no `mut` is required.
_Avoid_: reassignment, overwriting, redeclaration

**Slice**:
A borrowed view into a contiguous sequence, carrying a pointer and a length and owning nothing. `&str` and `&[T]` are the two that appear constantly, and both are what a signature should ask for.
_Avoid_: array, view, range, substring

**Soundness**:
The property that no safe caller, however careless, can cause undefined behaviour through your interface. It is a much stronger claim than the code working, and tests cannot establish it.
_Avoid_: well tested, safe as a synonym, it compiled and ran

**Stacked Borrows**:
Miri's default model for checking which references may be used when, by tracking a stack of borrows per location. Its own documentation calls it experimental, so a program it accepts is not thereby proved sound.
_Avoid_: the language's definition, a proof of soundness, the borrow checker

**Strong count**:
The number of owning handles to a counted value that are currently alive, reported by `Rc::strong_count` and `Arc::strong_count`. The value is dropped when it reaches zero, and weak handles are counted separately and do not keep it alive.
_Avoid_: the weak count, a borrow count, the number of references in the program

**Sync**:
A marker meaning `&T` may be shared with another thread, which is exactly what makes `&T` itself `Send`. A type may have this without `Send` or `Send` without this, and the two errors name different traits.
_Avoid_: `Send`, thread-safe as a general claim, synchronised access

**Task**:
A future handed to a runtime to own and drive, which starts running without being awaited and must be `Send` and `'static` because the runtime may move it between workers.
_Avoid_: a thread, a green thread the language provides, a future that runs by itself

**Tracking issue**:
The issue an `#[unstable]` attribute points at, where a feature's amendments and eventual stabilisation are recorded. It is the live record, so it outranks an accepted proposal that describes an earlier design.
_Avoid_: the RFC, a fixed specification, something that stops changing once written

**Trait bound**:
A constraint on a generic parameter naming a trait the type must implement, written after a colon, joined with `+`, moved into a `where` clause, or sugared as `impl Trait` in an argument position. It faces two ways at once: a promise to the body about what it may call, and a requirement on every caller.
_Avoid_: runtime check, interface, constraint on the value rather than the type

**Trait object**:
A value reached through a two-pointer handle, a data pointer beside a vtable pointer, whose concrete type is no longer in the type system, which is what `&dyn Trait` and `Box<dyn Trait>` produce and what lets one collection hold several types at once.
_Avoid_: interface, abstract class, boxed value, a cost claim nobody measured

**Turbofish**:
The `::<Type>` syntax that names a generic argument explicitly at a use site, for where inference has nothing to work from. A parameter written as `impl Trait` declares no name to give it, so the turbofish is not available against one.
_Avoid_: cast, type annotation, generic declaration

**Undefined behaviour**:
An operation whose premise the compiler was entitled to assume never happens, so once it does, the optimisations licensed by that assumption can misbehave anywhere in the program. It is a broken premise rather than an unpredictable result.
_Avoid_: unpredictable output, a runtime error, a crash, something a passing run rules out

**Unpin**:
An auto trait meaning a type does not care whether it is pinned, which almost every ordinary type implements. Generated futures do not, which is why the pinning ceremony appears exactly where it is load-bearing.
_Avoid_: something to implement by hand, unpinning a pinned value, the opposite of a pinned pointer

**Unwind**:
The default panic behaviour, running each value's `Drop` up the call stack as the panic propagates, as opposed to `abort`, which ends the process immediately. A project can choose either, so code must not rely on unwinding happening.
_Avoid_: exception handling, catch, stack trace, rollback

**Variance**:
Which lifetimes and types may stand in for the ones a generic type was written with. A type is covariant where a longer lifetime may substitute for a shorter one, as `&'a T` is, invariant where no substitution is allowed, as anything behind `&mut` or inside a `Cell` is, and contravariant where the substitution runs the other way, as a function's parameter position does. It is computed from the fields, so one field decides it for the whole type, and it is part of a public API whether or not the signature changes.
_Avoid_: mutability, the invariant sense of the same word, something you declare rather than compute

**Variant**:
One of the shapes an enum's value may take, which may carry no data, a tuple payload or named fields. A payload is owned by the value the way a struct's field is, so constructing a variant moves what you put in it.
_Avoid_: case as a synonym for the enum, subclass, tag, member

**Waker**:
The handle a future receives through its context and must arrange to have called once progress is possible. Returning pending without arranging that is how a future is never polled again.
_Avoid_: a callback the executor invokes on its own, a thread signal, something a future may ignore

**Weak pointer**:
A non-owning handle to a counted value, made with `Rc::downgrade` or `Arc::downgrade`, which must be upgraded before use and yields `None` once the value is gone. It is how a cycle is broken and how a back-reference is expressed.
_Avoid_: a raw pointer, a borrow, a handle that keeps the value alive, an `upgrade` that always succeeds

**Workspace**:
A root manifest carrying `[workspace]` members rather than a package of its own, optionally sharing dependency versions and package fields the members inherit. Its members are published separately, in dependency order.
_Avoid_: one package with two targets, a monorepo as such, something that publishes as a unit

**Yank**:
Marking a published version so that new resolution will not pick it, without deleting the code or disturbing anyone whose lock file already names it. It withdraws a recommendation rather than a release.
_Avoid_: deletion, a fix for a leaked secret, something that unbreaks existing builds
