---
title: Java
description: "Own a Java service: model it in modern Java, then operate what the JVM does with it"
type: topic
---

# Learning: Java

Become the engineer trusted to own a Java service on a team: able to model a domain in modern Java rather than in the inheritance hierarchies the language used to demand, reason about concurrency from the memory model instead of from experiment, read a profile and a garbage-collection log to a decision, and review someone's Java and name concretely what an abstraction is costing them.

**Start here:** [0001. References Are Values](lessons/0001-references-are-values.md)
**Latest lesson:** [0049. Does This Framework Earn Its Place](lessons/0049-does-this-framework-earn-its-place.md), which closes the arc

## Success looks like

- Predict what reference equality, a broken `hashCode`, and a shared mutable field do, before running the code.
- Model a domain with records, sealed interfaces and enums, and say why an inheritance hierarchy would have been worse.
- State what `synchronized`, `volatile` and a concurrent collection each guarantee, in the vocabulary of the Java memory model.
- Use virtual threads where they pay, and name what still blocks a carrier thread.
- Read a garbage-collection log and a profile, then size a heap from that evidence rather than from a default.
- Ship a build someone else can run: declared dependencies, a test suite, a runnable artifact.
- Review a pull request and say precisely why a class hierarchy, a checked exception, or a stream chain is the wrong tool there.
- Settle a language argument from the specification and the JEP that introduced the feature.

## Constraints

- Assumes no prior Java. Experience in another language shortens the early stages but is not required, and it brings habits Java punishes quietly: a getter for every field, an interface with one implementation, a class where a record would say it better.
- The baseline is the current long-term-support release. Every language feature is introduced with the release it arrived in, because Java code is read across many versions and "modern Java" ages.
- Needs only a JDK and a terminal on any supported OS. An IDE helps and is never required, and nothing in the arc requires paid tooling or a cloud account.
- Most reps are small programs that fit one sitting. Stage 6 is the exception: a profile needs a program that runs long enough to profile.
- Version-sensitive claims are checked against the specification, the API documentation and the JEP index rather than against a book, because the six-month release cadence outpaces every book listed.

## Out of scope

- Frameworks as subjects in their own right: Spring, Jakarta EE, Quarkus, Hibernate. Judging whether a framework earns its place is a review skill and belongs in stage 7.
- Other JVM languages: Kotlin, Scala, Clojure, Groovy.
- Android, and mobile targets generally.
- Build-tool comparison. The arc teaches the tasks a build has to perform and uses one tool to do them, rather than arguing about which.
- JVM internals past the point where they stop predicting program behaviour: JIT implementation, bytecode engineering, writing a garbage collector.
- Kubernetes and infrastructure beyond what one service needs to run.

## The arc

Seven stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Foundations | Primitives and references, `null`, strings and their pool, arrays, the collections framework, `equals` and `hashCode`, `Comparable` | Can predict identity versus equality and aliasing without running the code |
| 2. Modelling | Classes and interfaces, records, sealed types, enums, generics and erasure, pattern matching, immutability as a default | Models a domain without reaching for inheritance first |
| 3. Idiom and the library | Exceptions and what to do with checked ones, `Optional`, streams and collectors, iteration, files and IO, the time API, text blocks | Writes Java a reviewer would not describe as unidiomatic |
| 4. Concurrency | Threads, the memory model, `synchronized` and `volatile`, `java.util.concurrent`, executors, virtual threads, structured concurrency, the traps | Can name the guarantee a broken concurrent program violated |
| 5. Testing and build | JUnit 6, parameterised tests, test doubles and when not to use one, dependency declaration, a reproducible runnable artifact | Someone else can clone, build, test and run it |
| 6. The runtime | Memory areas, object layout and escape analysis, garbage collectors and their trade-offs, reading a GC log, JMH, profiling, allocation reduction | Optimises from a profile and proves the win with a benchmark that is trustworthy |
| 7. Judgment | API design and backwards compatibility, deprecation, review, reading the specification and the JEPs for answers | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | References Are Values | A variable holds a primitive or a reference, and every assignment and argument copies that |
| [0002](lessons/0002-identity-and-equality.md) | Identity and Equality | == compares references, so it answers a different question for strings and boxed numbers |
| [0003](lessons/0003-equals-and-hashcode.md) | The equals and hashCode Contract | Break the contract and a hash collection loses your object without raising anything |
| [0004](lessons/0004-null.md) | null and Where It Comes From | null is a reference that refers to nothing, and the fix is to reject it at the boundary |
| [0005](lessons/0005-arrays-and-collections.md) | Arrays and Collections | Arrays are covariant and fixed, and three list factories differ in ways their names hide |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable and Comparator | A sorted collection uses ordering rather than equals, so an inconsistent comparator loses data |
| [0007](lessons/0007-classes-and-objects.md) | Classes and Objects | A class is a template for state and behaviour, and every field starts at a default you did not write |
| [0008](lessons/0008-records.md) | Records | A transparent carrier for immutable data, with the constructor, accessors, equals, hashCode and toString derived from the header |
| [0009](lessons/0009-interfaces.md) | Interfaces | A contract with no state, plus the default methods that let one grow without breaking every implementor |
| [0010](lessons/0010-inheritance-and-composition.md) | Inheritance and Composition | What extends actually gives you, and why the answer is usually a field instead of a superclass |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | Sealed Types and Pattern Matching | A closed set of alternatives, and a compiler that checks you handled all of them |
| [0012](lessons/0012-enums.md) | Enums | A fixed set of instances the language guarantees, with room for state and behaviour on each one |
| [0013](lessons/0013-generics-and-erasure.md) | Generics and Erasure | Type parameters the compiler checks and the runtime forgets, and the wildcards that make them usable |
| [0014](lessons/0014-immutability-as-a-default.md) | Immutability as a Default | Make the object impossible to change and most of the hard questions stop being asked |
| [0015](lessons/0015-exceptions.md) | Exceptions | Which failures belong in a signature, which belong in a stack trace, and cleanup that survives both |
| [0016](lessons/0016-optional.md) | Optional | A return type that makes absence part of the contract, and the four places it does not belong |
| [0017](lessons/0017-streams.md) | Streams | A pipeline that describes work, does none of it until asked, and can only be asked once |
| [0018](lessons/0018-collectors.md) | Collectors | Turning a pipeline back into a container, and the three collectors that throw where you do not expect it |
| [0019](lessons/0019-files-and-paths.md) | Files and Paths | Paths that are not strings, streams that must be closed, and a charset that is finally a default worth having |
| [0020](lessons/0020-dates-and-times.md) | Dates and Times | Which of the six time types you actually meant, and the three that are not a point in time |
| [0021](lessons/0021-strings-and-text.md) | Strings and Text | Text blocks, the formatting you should use, and why length is not the number of characters |
| [0022](lessons/0022-threads.md) | Threads | A thread is a scheduled call stack, and almost every mistake in this stage starts with treating one as free |
| [0023](lessons/0023-the-memory-model.md) | The Memory Model | Why a value written by one thread may never be seen by another, and the exact rule that fixes it |
| [0024](lessons/0024-mutual-exclusion.md) | Mutual Exclusion | One thread at a time, the two ways to say it, and the deadlock you can find before it happens |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | Concurrent Collections and Atomics | The collections that survive concurrent access, and the check-then-act that defeats every one of them |
| [0026](lessons/0026-executors-and-futures.md) | Executors and Futures | Submit work instead of creating threads, and find the exception that submit swallowed |
| [0027](lessons/0027-virtual-threads.md) | Virtual Threads | Threads cheap enough to block, and the pooling habit you now have to unlearn |
| [0028](lessons/0028-choosing-a-model.md) | Choosing a Model | One question picks the model, and the failure you are looking at names the guarantee it broke |
| [0029](lessons/0029-your-first-test.md) | Your First Test | Where tests live, what the runner actually does, and the version scheme every write-up gets wrong |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | Assertions That Name the Failure | A failing test is a bug report, and the assertion you chose decides how good a report it is |
| [0031](lessons/0031-parameterised-tests.md) | Parameterised Tests | One test method, many cases, and the line where a loop inside a test stops being good enough |
| [0032](lessons/0032-test-doubles.md) | Test Doubles | Five kinds of stand-in, when a real object beats all of them, and what a mock quietly stops testing |
| [0033](lessons/0033-declaring-dependencies.md) | Declaring Dependencies | Coordinates, scopes and the transitive graph, plus the version that arrives without being asked for |
| [0034](lessons/0034-the-build-lifecycle.md) | The Build Lifecycle | Phases and goals instead of memorised commands, and the wrapper that makes the build the same everywhere |
| [0035](lessons/0035-a-runnable-artifact.md) | A Runnable Artifact | Packaging what you built so that someone with nothing but a JDK can run it |
| [0036](lessons/0036-where-memory-goes.md) | Where Memory Goes | The five places the JVM puts memory, and which OutOfMemoryError names which one |
| [0037](lessons/0037-the-shape-of-an-object.md) | The Shape of an Object | A small object is mostly header, and the flag that shrinks it is off by default |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | The Allocation That Never Happened | Escape analysis can delete an allocation entirely, and one field store puts it back |
| [0039](lessons/0039-collectors-and-the-trade.md) | Collectors and the Trade You Are Making | Five collectors, one three-way trade, and why the default is usually the right answer |
| [0040](lessons/0040-reading-a-gc-log.md) | Reading a Garbage Collection Log | One line of log says how much was collected, how long it took, and whether to care |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | A Benchmark You Can Trust | Why the obvious timing loop lies, and the harness setup that silently measures nothing |
| [0042](lessons/0042-from-profile-to-proof.md) | From Profile to Proof | Record the run, read where the time went, change one thing, and prove the win |
| [0043](lessons/0043-what-counts-as-breaking.md) | What Counts as Breaking | Three kinds of compatibility, and the change that is safe to compile against and fatal to run against |
| [0044](lessons/0044-designing-a-signature.md) | Designing a Signature | The parameter and return types decide what callers can do, and most of the damage is done at the boundary |
| [0045](lessons/0045-evolving-a-type.md) | Evolving a Type Without Breaking It | How to add to an interface, a record, an enum and a sealed hierarchy after people depend on them |
| [0046](lessons/0046-deprecation-that-works.md) | Deprecation That Works | Marking something deprecated changes nothing unless you say what happens next |
| [0047](lessons/0047-settling-it-from-the-source.md) | Settling It From the Source | Where to look when the argument is about what Java does, and which document answers which question |
| [0048](lessons/0048-reviewing-java.md) | Reviewing Java | Naming what an abstraction costs, instead of saying it feels wrong |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | Does This Framework Earn Its Place | The last judgment in the arc, made from the service's constraints rather than the framework's promises |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Equality, hashing and ordering](reference/equality-hashing-and-ordering.md): the three contracts, and which comparison to write
- [Modelling](reference/modelling.md): which construct to reach for, what each one commits you to, and the rules that are easy to misremember
- [Idiom and the library](reference/idiom-and-library.md): the library decisions a reviewer notices, and the traps that throw where nobody looks
- [Concurrency](reference/concurrency.md): which guarantee each construct gives, which model fits the workload, and what the symptom in front of you means
- [Testing and build](reference/testing-and-build.md): the build task each command actually performs, the double to reach for, and the failure that means the artifact is wrong
- [The runtime](reference/the-runtime.md): where the memory goes, which collector answers which requirement, and the measurement that supports a claim
- [Judgment](reference/judgment.md): which changes break what, how to retire an API, and how to argue the call from the source

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
