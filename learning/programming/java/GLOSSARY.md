---
title: Glossary
description: Canonical terms for Java
type: glossary
---

# Java Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words are used loosely in ways that would make later lessons ambiguous, and each one hides a mistake that compiles cleanly, so all three are pinned from the start:

**Reference**:
A value that refers to an object, held in a variable, a field, or an array slot. Everything in Java is passed by value, and for objects the value passed is the reference, which is why a method can mutate what it was given and can never rebind the caller's variable.
_Avoid_: pointer, handle, alias

**Final**:
A promise that a variable, field or parameter will not be reassigned. It says nothing about the object on the other end, so a `final` list can still be cleared.
_Avoid_: immutable, constant, read-only

**Thread-safe**:
A property of a class relative to a stated contract: correct behaviour when accessed concurrently, with the contract saying what "correct" means. It is not a synonym for using `synchronized`, and a class built entirely from thread-safe parts is not automatically one.
_Avoid_: synchronised, atomic, concurrent

## Terms

**Aliasing**:
The situation where two or more variables hold references to one object, which is what assignment always produces. Mutating through either is observable through both.
_Avoid_: sharing, pointing, double reference

**Autoboxing**:
The implicit conversion between a primitive and its wrapper type, performed by calls the source code does not show. `Integer.valueOf` caches `-128` to `127`, which is why `==` on boxed values is correct for small numbers and wrong for large ones.
_Avoid_: casting, wrapping, promotion

**Automatic module**:
A plain jar with no `module-info.class`, which the module system still admits under a name taken from its `Automatic-Module-Name` manifest attribute or, failing that, derived from its filename. A library that does not set the attribute therefore publishes a name that changes when somebody renames the file.
_Avoid_: module, unnamed module, modular jar

**Behavioural compatibility**:
Whether code that still compiles and still links produces the same result as before. It is independent of the other two compatibilities, so the most dangerous release is one that is source-compatible and binary-compatible and quietly answers differently.
_Avoid_: semantic versioning, bug fix, backwards compatible

**Bill of materials**:
A `pom`-packaged artifact that exists only to declare versions, imported into `dependencyManagement` with `import` scope. One line then fixes the versions of a whole family of artifacts, which is why a dependency taken from a BOM is declared with no version of its own.
_Avoid_: parent pom, dependency list, manifest

**Binary compatibility**:
Whether already-compiled class files still link and run against a new version with no recompilation. Its test is running the old class files, never rebuilding them, because a successful rebuild proves source compatibility and says nothing about this.
_Avoid_: source compatibility, ABI stability, drop-in replacement

**Blackhole**:
A sink a benchmark passes a result to so that the value is unambiguously consumed and cannot be treated as unused. JMH can also detect a compiler-supported blackhole mode and use it without any change to the benchmark, and results taken under different modes are not comparable.
_Avoid_: void return, discarding, no-op

**Canonical constructor**:
The constructor whose parameters are exactly a record's components, in declaration order. It is generated unless you declare it, and every other constructor on the record has to delegate to it, which is why validation placed there cannot be bypassed.
_Avoid_: default constructor, primary constructor, main constructor

**Carrier thread**:
The platform thread a virtual thread is currently mounted on and running against. A virtual thread unmounts from its carrier while it is blocked, which is what makes blocking cheap, and failing to unmount is what pinning means.
_Avoid_: host thread, worker, OS thread

**Checked exception**:
A `Throwable` outside `RuntimeException` and `Error`, which the compiler forces every caller to catch or declare. It earns its place only when a reasonable caller can act on the failure, because a caller who can only give up will wrap it or swallow it instead.
_Avoid_: compile-time exception, declared error, fatal exception

**Closeable stream**:
A `Stream` backed by an open operating-system handle, which is what `Files.lines`, `Files.walk` and `Files.find` return. Unlike a stream over a collection it must be closed, and skipping that usually appears to work, because unreachable ones are cleaned up eventually and the descriptors run out only under load.
_Avoid_: file stream, lazy stream, resource

**Committed heap**:
The heap the collector currently holds from the operating system, which is what a garbage collection line reports in parentheses. It is neither the occupancy before or after the collection nor the `-Xmx` ceiling it may still grow towards.
_Avoid_: max heap, used heap, allocated memory

**Compact constructor**:
A canonical constructor written with no parameter list, whose body runs before the components are assigned to the fields. Assigning to the parameter is what reaches the field, and assigning to `this.field` there is a compile error rather than a redundancy.
_Avoid_: compact form, short constructor, implicit constructor

**Compile-time constant**:
A `static final` field of a primitive or `String` type with a constant initialiser, whose value the compiler folds into every caller's class file. Changing it has no effect on a caller that does not recompile, because no reference to the field survives in the caller at all.
_Avoid_: final field, immutable value, static field

**Compressed ordinary object pointers**:
The JVM's default encoding of a reference as a 32-bit heap offset rather than a full-width address, used while the heap is small enough for every object to be reachable that way. It halves the cost of every reference field and every reference-typed array slot, and the JVM decides it ergonomically rather than the programmer choosing it.
_Avoid_: pointer compression, small heap mode, 32-bit mode

**Covariance (of arrays)**:
The rule that `String[]` is usable as an `Object[]`, which lets a type error survive compilation and surface as `ArrayStoreException`. Generics are invariant precisely to close this hole.
_Avoid_: polymorphism, subtyping, generics compatibility

**Critical section**:
The region of code that runs while a lock is held. Its extent is a design decision rather than an accident: it should be exactly the span over which the invariant the lock protects is temporarily untrue, which is usually smaller than the method it sits in.
_Avoid_: locked block, synchronised region, atomic section

**Daemon thread**:
A thread the JVM does not wait for once the last non-daemon thread finishes, so the process exits with that work unfinished and nothing reported. The status is inherited from the creating thread and can only be set before `start`.
_Avoid_: background thread, worker thread, service thread

**Data race**:
Two accesses to one variable from different threads, at least one of them a write, with no happens-before edge between them. Its presence withdraws the guarantee of sequentially consistent behaviour from the entire execution rather than only from that variable, which is stronger than "sometimes wrong".
_Avoid_: race condition, concurrency bug, contention

**Deadlock**:
A cycle of threads each waiting for a lock the next one in the cycle holds, so none proceeds and none of the locks is ever released. One consistent acquisition order across the program prevents it, and the JVM will name the cycle from inside the running process.
_Avoid_: hang, freeze, lock contention

**Decorator (of unified logging)**:
One of the context fields `-Xlog` prepends to each line, such as the wall-clock time, the uptime, the level or the tags. Choosing them is what makes a log analysable later, because the fields absent from a line cannot be recovered from it.
_Avoid_: decorator pattern, prefix, formatter

**Defensive copy**:
A copy taken so that a reference cannot be used to change an object from outside it: on the way in so a caller's later mutation cannot reach a field, and on the way out so a returned reference cannot either. The second half is the half that gets forgotten.
_Avoid_: deep copy, clone, snapshot

**Dependency mediation**:
The rule by which a build picks one version when the graph asks for several: the declaration nearest the project wins, and a tie at equal depth is broken by whichever was declared first. It is not "newest wins", which is the common assumption and the reason adding one dependency can silently downgrade another.
_Avoid_: version resolution, conflict resolution, upgrade

**Dependency scope**:
A declaration of which classpaths a dependency belongs on and whether it reaches a consumer. `test` and `provided` do not propagate at all, which is the mechanism behind most failures that appear only once something is packaged or reused.
_Avoid_: visibility, dependency type, phase

**Downstream collector**:
A collector handed to another one, such as `groupingBy`, `partitioningBy` or `teeing`, which runs against each group or branch rather than against the whole stream. It is what turns a grouping into counts, sums or a nested map without a second pass.
_Avoid_: nested collector, sub-collector, inner reduction

**Dummy**:
A test double passed only to satisfy a signature and never actually called. If it is called the test should fail, which is why throwing from every method is a sound implementation of one.
_Avoid_: stub, mock, null object

**Encounter order**:
The order in which a stream's elements arrive, where the source has one. `findFirst`, sort stability and the order of a collected `List` are all defined against it, and a source such as a `HashSet` gives them nothing to be defined against.
_Avoid_: sort order, iteration order, sequence

**Erasure**:
The compiler's discarding of type arguments, which leaves `List<String>` and `List<Integer>` as one class at run time. Every restriction on generics follows from it, and so does a `ClassCastException` on a line that contains no cast.
_Avoid_: type deletion, unboxing, runtime generics

**Ergonomics**:
The JVM's practice of computing a flag's value at startup from the machine it finds, reported as `{ergonomic}` rather than `{default}`. An ergonomic value is not a constant and changes with the machine or the container limit, silently and with no flag touched.
_Avoid_: default, tuning, autoconfiguration

**Escape analysis**:
The compiler's proof that an object cannot be observed outside the method that created it, which permits it not to be created at all. It is an optimisation with nothing in the specification promising it, so it can stop applying when unrelated code changes what gets inlined.
_Avoid_: garbage collection, stack allocation, optimisation pass

**Exhaustive switch**:
A `switch` whose labels the compiler can prove cover every possible value, which is what permits omitting `default`. Omitting it is the point rather than an oversight, because adding an alternative then fails compilation at every place that has to decide again.
_Avoid_: complete switch, total switch, default-free switch

**Fake**:
A working implementation of an interface, simplified enough to use in a test, such as a map standing in for a repository. It encodes behaviour rather than an expected sequence of calls, so it survives a refactor that would break a mock with ordered expectations.
_Avoid_: mock, stub, in-memory copy

**Final field freeze**:
The guarantee that a thread obtaining a reference only after construction has finished sees that object's `final` fields correctly initialised. It holds even when the reference itself was published through a data race, which is why a properly built immutable object can be shared with no synchronisation at all.
_Avoid_: immutability guarantee, constructor barrier, safe init

**Fork (of a benchmark)**:
A separate JVM process a harness starts so that one benchmark's compilation and profiling history cannot influence another's measurement. Running a single fork is the commonest reason two benchmarks appear to differ when they do not, or appear identical when they differ.
_Avoid_: thread, iteration, process fork

**Fragile base class problem**:
The coupling inheritance creates in both directions: a superclass author breaks subclasses by changing behaviour that looked internal, and a subclass author breaks by depending on more than the superclass promised. It is why every `protected` member is published API.
_Avoid_: tight coupling, bad inheritance, base class rot

**Functional interface**:
An interface with exactly one abstract method, which is what lets a lambda or a method reference stand in for an instance of it. The `@FunctionalInterface` annotation states and enforces the intent, and is never required for the lambda to work.
_Avoid_: lambda interface, callback, SAM type

**Goal**:
A single unit of work a build plugin can perform, named as `plugin:goal`. Goals are what actually run, and a phase only names the point at which one has been bound to run, so "what does this command do" is always answered by listing goals.
_Avoid_: task, phase, command

**Happens-before**:
The ordering relation that makes one action's effects visible to, and ordered before, another's. It is the only thing that makes a concurrent read and write pair safe, so every synchronisation construct is worth precisely the edges it creates and nothing more.
_Avoid_: before, ordering, synchronisation

**Hiding**:
A subclass declaring a `static` method or a field with the same name as one in the superclass. It resolves on the declared type of the reference rather than the runtime type of the object, which is the opposite of overriding and looks identical in the source.
_Avoid_: overriding, shadowing, masking

**Humongous allocation**:
In G1, an object at least half a region in size, which is allocated directly into contiguous regions rather than through the ordinary young path. It appears in a garbage collection log by name, and a stream of them is a sizing problem rather than a collector problem.
_Avoid_: large object, big allocation, old generation allocation

**Interning**:
Placing a value in a shared pool so that identical values are one object. String literals and compile-time constants are interned, which makes `==` on strings appear to work until a value is built at run time.
_Avoid_: caching, deduplication, pooling

**Invariance (of generics)**:
The rule that `List<String>` is not a `List<Object>`, whatever the relationship between the type arguments. It is the deliberate opposite of array covariance, and it is what moves the error from run time to compile time.
_Avoid_: strictness, missing polymorphism, type mismatch

**Lifecycle phase**:
A named point in a build's ordered sequence, such as `compile`, `test` or `package`. Naming one runs every phase before it as well, which is the single rule that predicts what any build command will do.
_Avoid_: goal, step, target

**Local (of a date or time)**:
A value naming a reading on a calendar or a wall clock with no zone attached, which is what `LocalDate`, `LocalTime` and `LocalDateTime` are. None of them is a point on the universal timeline, so none converts to an `Instant` without being told a zone, and using one as a timestamp is the most common mistake in the time API.
_Avoid_: naive time, zoneless, floating time

**Metaspace**:
The off-heap area holding the metadata of loaded classes, meaning their bytecode, constant pools and field layouts. It is bounded separately from the heap and is unbounded by default, so a classloader leak exhausts native memory rather than heap.
_Avoid_: permgen, heap, class cache

**Method descriptor**:
The encoding of a method's parameter and return types which, with its name, is the method's identity inside a class file. Two methods differing only in return type are one method in the source language and two unrelated methods here, which is why narrowing a return type breaks callers that do not recompile.
_Avoid_: signature, prototype, type erasure

**Mock**:
A test double carrying expectations about how it is called, which are checked and can fail the test on their own. It tests the implementation's choice of interactions rather than its promise, which is why it is the double most likely to fail on a change that broke no behaviour.
_Avoid_: stub, fake, double

**Monitor**:
The intrinsic lock and wait set that every object carries, entered by a `synchronized` method or block and released on exit or on a call to `wait`. Locking on an object anyone else can reach publishes its monitor, and then anyone else can hold it.
_Avoid_: lock object, mutex, semaphore

**Natural ordering**:
The ordering a type defines for itself by implementing `Comparable`. A sorted collection uses it instead of `equals`, so two elements that compare as zero are one element as far as a `TreeSet` is concerned.
_Avoid_: default sort, comparison, ranking

**Object header**:
The fixed block of JVM bookkeeping in front of every instance's fields, invisible from the source and counted in every allocation. On a small object it is most of the object, which is why a record of two `int` fields costs three times what its fields do.
_Avoid_: record header, metadata, object overhead

**Overload resolution**:
The compiler's choice, made from the static types of the arguments, of which same-named method a call binds to. It happens once at compile time and never again, so a caller holding a value under a more general type gets a different overload than its runtime class would suggest.
_Avoid_: dynamic dispatch, overriding, polymorphism

**PECS**:
Producer extends, consumer super: `? extends T` for a structure you only read from, `? super T` for one you only write to. A parameter that must do both takes a plain `T` and gives up the flexibility, which is the trade rather than a defect.
_Avoid_: wildcards, variance, bounded generics

**Pinning**:
A virtual thread blocking without being able to unmount, so it keeps its carrier thread occupied and removes it from service for the duration. What causes pinning has changed across releases, so it is established by measuring on the release being deployed rather than from anything written about an earlier one.
_Avoid_: blocking, sticking, thread affinity

**Platform thread**:
A thread backed one to one by an operating-system thread and its stack, which is what `new Thread` has always produced. The stack is why they are counted in thousands rather than millions, and why pools exist at all.
_Avoid_: real thread, native thread, kernel thread

**Probe effect**:
The change in a concurrent program's behaviour caused by observing it, such as a log line shifting the scheduling enough to hide the very race it was added to catch. It is the reason a concurrency bug is made to reproduce reliably before anything is changed.
_Avoid_: heisenbug, observer effect, timing issue

**Raw type**:
A generic type used with no type argument, such as `List` in place of `List<String>`. It switches off checking for every member whose signature mentions the parameter, which is how a wrong element gets in silently and surfaces as a cast failure somewhere else entirely.
_Avoid_: untyped collection, legacy generic, unparameterised type

**Reproducible build**:
A build that turns the same source into byte-identical output. Archive entry timestamps defeat it by default, so it has to be asked for explicitly, and until it is, two builds of one commit cannot be shown to have produced the same artifact.
_Avoid_: deterministic build, repeatable build, clean build

**Resident memory**:
The total memory the operating system charges to the JVM process, which is the heap plus metaspace plus thread stacks plus the code cache plus native and direct buffers. It is what a container limit is enforced against, and `-Xmx` bounds only the first term of it.
_Avoid_: heap usage, virtual memory, max heap

**Scalar replacement**:
The optimisation that follows escape analysis, holding a non-escaping object's fields in registers or on the stack instead of allocating the object. The allocation then does not appear in a measurement of bytes per operation at all, because it never happened.
_Avoid_: inlining, stack allocation, elision

**Sealed hierarchy**:
A supertype whose permitted direct subtypes are fixed at compile time, so the set of alternatives is closed and the compiler can enumerate it. That is what makes a `switch` over it exhaustive with no `default`.
_Avoid_: closed class, final hierarchy, restricted inheritance

**Short-circuiting operation**:
A stream operation that can finish without pulling every element through the pipeline, such as `findFirst`, `anyMatch` or `limit`. It is what makes an infinite source usable, and it is what an operation such as `sorted` takes away, since sorting has to see everything first.
_Avoid_: early exit, lazy operation, break

**Source compatibility**:
Whether code that compiled against the old version still compiles against the new one, unchanged. Its test is a recompile, and passing it says nothing about whether already-compiled callers will still run.
_Avoid_: binary compatibility, API stability, non-breaking change

**Spy**:
A test double that records how it was called so the test can inspect it afterwards, or a wrapper that delegates to a real object while recording. It moves the check to after the call instead of declaring it in advance, which is what separates it from a mock.
_Avoid_: mock, stub, listener

**Stub**:
A test double that returns canned answers and checks nothing about how it was used. It supplies input rather than expectations, so a test built only on stubs is asserting on results.
_Avoid_: mock, fake, dummy

**Suppressed exception**:
An exception attached to another rather than replacing it, which is what try-with-resources does when a resource fails to close while an exception from the body is already propagating. A hand-written `finally` loses the original instead, with no trace that it happened.
_Avoid_: secondary exception, ignored exception, nested exception

**Terminal deprecation**:
Deprecation with `forRemoval = true`, which the platform treats as a different signal rather than a stronger adjective: the compiler warns about it by default, in its own `removal` category, where ordinary deprecation is silent without `-Xlint:deprecation`. It is a stated intention and not a guarantee, since the platform has withdrawn one.
_Avoid_: deprecated, obsolete, scheduled for deletion

**Terminal operation**:
The stream operation that makes the pipeline run and consumes it, such as `forEach`, `collect` or `count`. Nothing before it executes, and nothing after it is possible on that stream, because a second terminal call throws.
_Avoid_: final operation, sink, evaluation

**Test double**:
Any stand-in for a real collaborator in a test: a dummy, a stub, a spy, a mock or a fake. The general word is worth keeping because those five differ in what they let a test conclude, and treating them as synonyms is what produces a suite that passes while proving nothing.
_Avoid_: mock, fake, stub

**Test engine**:
A plug-in that teaches the test platform one way of writing tests, such as Jupiter for current tests or Vintage for JUnit 4 ones. Nothing runs without one present, and a build tool that supplies one automatically will hide its absence from the project's own declarations.
_Avoid_: runner, framework, platform

**Test instance lifecycle**:
The rule deciding how many instances of a test class get created: one per test method by default, or one for the whole class. The default is what makes a field written by one test invisible to the next, so changing it trades isolation for shared setup.
_Avoid_: scope, fixture, lifecycle

**Thread stack**:
The per-thread reservation holding that thread's call frames, sized by `-Xss` and unaffected by `-Xmx`. Exhausting one raises `StackOverflowError` in that thread alone, which is a different kind of failure from a shared pool running out.
_Avoid_: heap, call stack trace, stack trace

**Thread-local allocation buffer**:
The slice of the heap handed to one thread so that its ordinary allocations are a pointer bump needing no coordination with other threads. It is why allocation itself is cheap, and it says nothing about the later cost of tracing or copying what was allocated.
_Avoid_: free allocation, thread-local variable, buffer pool

**Total order**:
A comparator or natural ordering under which no two distinct elements compare as zero. Sorted collections need one, and a chain of keys provides it only if the last key is unique per element.
_Avoid_: full sort, strict ordering, complete comparator

**Transitive dependency**:
A dependency you never declared, present because something you did declare needs it. Most of a project's classpath arrives this way, at versions chosen by mediation rather than by anyone, which is why relying on one you did not ask for breaks on somebody else's upgrade.
_Avoid_: indirect import, sub-dependency, nested library

**Uber jar**:
A single jar holding the project's own classes together with the unpacked contents of all its dependencies, so it runs with nothing else on the classpath. The convenience costs a far larger artifact and flattens every dependency's identity, including its licence information, into one file.
_Avoid_: fat jar, shaded jar, bundle

**View**:
A collection that reads through to another one rather than holding its own contents, which is what `Collections.unmodifiableList` and `Map.values` return. It refuses writes through itself and still shows every change made to the collection behind it.
_Avoid_: copy, snapshot, wrapper

**Wither method**:
A method returning a new instance that differs in one component, conventionally named `withX`. It is the immutable replacement for a setter, and it makes the cost visible, since every call allocates.
_Avoid_: setter, mutator, copy method
