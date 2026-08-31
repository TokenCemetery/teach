---
title: Java
description: "Own a Java service: model it in modern Java, then operate what the JVM does with it"
type: topic
---

# Learning: Java

Become the engineer trusted to own a Java service on a team: able to model a domain in modern Java rather than in the inheritance hierarchies the language used to demand, reason about concurrency from the memory model instead of from experiment, read a profile and a garbage-collection log to a decision, and review someone's Java and name concretely what an abstraction is costing them.

**Latest lesson:** _none yet_

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
| 5. Testing and build | JUnit 5, parameterised tests, test doubles and when not to use one, dependency declaration, a reproducible runnable artifact | Someone else can clone, build, test and run it |
| 6. The runtime | Memory areas, object layout and escape analysis, garbage collectors and their trade-offs, reading a GC log, JMH, profiling, allocation reduction | Optimises from a profile and proves the win with a benchmark that is trustworthy |
| 7. Judgment | API design and backwards compatibility, deprecation, review, reading the specification and the JEPs for answers | Trusted to make the call and to explain it to someone else |

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
