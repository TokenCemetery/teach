---
title: Resources
description: Trusted sources for Java, each annotated with what it covers
type: resources
---

# Java Resources

## Knowledge

- [Docs: "Java SE Specifications", Oracle, docs.oracle.com](https://docs.oracle.com/javase/specs/index.html)
  The index of every language and virtual-machine specification, by release. Use for: reaching the right version of the specification instead of the one a search engine remembered.

- [Spec: "The Java Language Specification, Java SE 25", Gosling, Joy, Steele, Bracha, Buckley, Smith, Bierman, Oracle](https://docs.oracle.com/javase/specs/jls/se25/html/index.html)
  The definitive statement of what the language means, including overload resolution and generics. Use for: settling an argument no tutorial can settle.

- [Spec: "Threads and Locks", chapter 17 of the Java Language Specification, Oracle](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)
  The Java memory model: happens-before, `volatile`, final field semantics, what a data race is permitted to produce. Use for: stage 4, reasoning about concurrency rather than testing for it.

- [Spec: "The Java Virtual Machine Specification, Java SE 25", Lindholm, Yellin, Bracha, Buckley, Smith, Oracle](https://docs.oracle.com/javase/specs/jvms/se25/html/index.html)
  Class file format, linking, and the execution model the language compiles to. Use for: stage 6, when behaviour only makes sense one level down.

- [Docs: "Java SE 25 API Documentation", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/docs/api/index.html)
  The library, with the contracts each interface actually requires of an implementation. Use for: what a method promises, especially in collections and concurrency.

- [Docs: "JDK 25 Documentation", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/)
  Tool guides, virtual-machine options, troubleshooting and migration in one place. Use for: command-line flags and the guides behind them.

- [Docs: "HotSpot Virtual Machine Garbage Collection Tuning Guide, Release 25", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/gctuning/index.html)
  The collectors, what each is built for, and the ergonomics that pick one for you, versioned to the release. Use for: stage 6, and as the primary source for any tuning claim, because this is the source that gets reissued when the answer changes.

- [Docs: "The java Command", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)
  Every launcher option, including the whole of unified logging behind `-Xlog` and the heap sizing flags. Use for: stage 6, and whenever a flag found in a blog post needs checking against the release in hand.

- [Docs: "The jfr Command", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jfr.html)
  The command-line reader for a Flight Recorder file: `summary`, `print` and event filtering. Use for: stage 6, reading a recording without installing a graphical tool.

- [Docs: "Flight Recorder API Programmer's Guide, Release 25", Oracle, docs.oracle.com](https://docs.oracle.com/en/java/javase/25/jfapi/index.html)
  What the recorder records, which events exist and what each one costs to collect. Use for: stage 6, deciding what to switch on before recording rather than after.

- [Docs: "Learn Java", Oracle, dev.java](https://dev.java/learn/)
  The official tutorials, maintained for current releases rather than left at Java 8. Use for: stages 1 to 3, and for a worked introduction to a feature.

- [Docs: "JEP 0: JEP Index", OpenJDK, openjdk.org](https://openjdk.org/jeps/0)
  Every proposal with its status and target release, each one arguing for its own feature. Use for: which release introduced something, and why it was designed that way.

- [Docs: "JDK 25", OpenJDK, openjdk.org](https://openjdk.org/projects/jdk/25/)
  The feature list and schedule for the release, linked to its JEPs. Use for: checking what is actually in a release before teaching it.

- [Docs: "Oracle Java SE Support Roadmap", Oracle, oracle.com](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)
  Which releases are long-term-support and how long each is maintained. Use for: choosing the version the arc assumes.

- [Book: "Java Concurrency in Practice", Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea, Addison-Wesley](https://jcip.net/)
  Publication, visibility and safe construction built up from the memory model, with the failure modes named. Use for: stage 4 when a mental model is missing rather than a fact.

- [Book: "Effective Java", Joshua Bloch, Addison-Wesley](https://openlibrary.org/isbn/9780134685991)
  Seventy-eight numbered items on API and class design, each with the reasoning kept. Use for: stages 2, 3 and 7, and for review vocabulary.

- [Book: "The Garbage Collection Handbook", Jones, Hosking, Moss, Chapman and Hall](https://gchandbook.org/)
  How collectors are built, from mark-sweep to concurrent and generational designs, with the trade-offs derived rather than asserted. Use for: stage 6 when the question is why a collector behaves as it does, which is the part that does not go stale.

- [Blog: "Inside Java", Oracle Java Platform Group, inside.java](https://inside.java/)
  Design rationale, release changes and deep dives from the engineers who make the decisions. Use for: why the platform refused a feature, and what changed in a release.

- [Blog: Aleksey Shipilëv, shipilev.net](https://shipilev.net/)
  Rigorous posts on the memory model, benchmarking methodology, object layout and garbage collection, by a JVM engineer. Use for: stage 6, and for why a benchmark is lying.

- [Tool: "JMH", OpenJDK, github.com/openjdk/jmh](https://github.com/openjdk/jmh)
  The harness that handles warmup, dead-code elimination and statistics for JVM benchmarks. Use for: measuring anything on a JIT-compiled runtime without fooling yourself.

- [Code: "JMH Samples", OpenJDK, github.com/openjdk/jmh](https://github.com/openjdk/jmh/tree/master/jmh-samples/src/main/java/org/openjdk/jmh/samples)
  Numbered, commented benchmarks, each demonstrating one way a measurement goes wrong. Use for: stage 6, as the authoritative worked examples. Note that they teach the mechanism rather than guarantee the outcome: two of the effects they demonstrate did not reproduce on JDK 25 when this stage was written, which is the reason to run them rather than quote them.

- [Tool: "async-profiler", github.com/async-profiler/async-profiler](https://github.com/async-profiler/async-profiler)
  Sampling profiler for processor time, allocation and native frames, with flame-graph output. Use for: stage 6 when Flight Recorder's resolution is not enough, or when the frames you need are below the Java stack.

- [Tool: "JDK Mission Control", Oracle, oracle.com](https://www.oracle.com/java/technologies/jdk-mission-control.html)
  The graphical reader for Flight Recorder files, with the automated analysis rules. Use for: stage 6 when a recording is too large to read with the command-line tool. It is a separate download, so nothing in the arc requires it.

- [Docs: "JUnit User Guide", JUnit Team, docs.junit.org](https://docs.junit.org/current/user-guide/)
  The programming and extension model, including parameterised and nested tests. Use for: stage 5 mechanics. Note the host: the material now lives at `docs.junit.org` rather than under the `junit5` path most search results still point at, and since JUnit 6 the Platform, Jupiter and Vintage share one version number.

- [Docs: "JUnit Release Notes", JUnit Team, docs.junit.org](https://docs.junit.org/current/release-notes/)
  What each release changed, added and removed, including the breaking changes. Use for: whether the advice you just read still applies.

- [Docs: "Maven Guides", Apache Software Foundation, maven.apache.org](https://maven.apache.org/guides/index.html)
  The build lifecycle, dependency mediation and scopes, from the project itself. Use for: what a build is actually doing, whichever tool runs it.

- [Docs: "Maven POM Reference", Apache Software Foundation, maven.apache.org](https://maven.apache.org/pom.html)
  Every element a project descriptor accepts, with inheritance and interpolation spelled out. Use for: settling what a POM element means rather than copying one that works.

- [Docs: "Mockito", javadoc.io](https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/Mockito.html)
  The API and, unusually for reference documentation, an argued position on what not to mock. Use for: stage 5, and for the reasoning to quote in a review.

- [Style guide: "Google Java Style Guide", Google](https://google.github.io/styleguide/javaguide.html)
  Opinionated, complete and widely adopted, with the rationale attached. Use for: decisions the specification leaves open.

## Wisdom (Communities)

- [Archive: "OpenJDK Mailing Lists", OpenJDK, mail.openjdk.org](https://mail.openjdk.org/)
  The public archive where platform changes are proposed, argued and rejected, readable without subscribing. Use for: the reasoning behind a decision that no document records.

## Gaps

- The memory model has no gentle authoritative source. Chapter 17 is formal and "Java Concurrency in Practice" predates virtual threads, `VarHandle` and structured concurrency, so stage 4 uses the book for the model and the current specification and JEPs for the API. That split worked, with one caveat found while writing the stage: **a JEP describes the release it shipped in and is not revised when a later JEP changes the behaviour.** JEP 444 still states that `synchronized` pins a carrier thread, which JEP 491 changed. Read a JEP for intent and design rationale, and confirm current behaviour by running it.
- Closed, and it turned out to be two gaps rather than one. **How collectors work** does have a book-length source, now listed: "The Garbage Collection Handbook". **How to tune a particular collector on a particular release** does not, and should not: tuning advice ages faster than books ship, so the primary source is the HotSpot garbage-collection tuning guide for the release in hand, which is versioned and is now listed for JDK 25. Do not go looking for a tuning book again.
- Two of the JIT effects the JMH samples demonstrate, dead-code elimination and constant folding, did not reproduce on JDK 25 while stage 6 was being written. This is not a defect in the samples: they demonstrate the mechanism, and whether it fires depends on the compiler, the platform and the shape of the code. It is a standing reason to run a sample rather than cite it, and stage 6 teaches the principle instead of the anecdote.
- The six-month release cadence outpaces every book here. Version-sensitive claims go to the specification, the API documentation or the JEP index, and any lesson naming a release says which one.
- Frameworks have no source by design. When stage 7 judges whether a framework earns its place, that judgment needs a source and this list does not yet have one.
