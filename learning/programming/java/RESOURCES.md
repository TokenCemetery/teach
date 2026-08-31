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

- [Blog: "Inside Java", Oracle Java Platform Group, inside.java](https://inside.java/)
  Design rationale, release changes and deep dives from the engineers who make the decisions. Use for: why the platform refused a feature, and what changed in a release.

- [Blog: Aleksey Shipilëv, shipilev.net](https://shipilev.net/)
  Rigorous posts on the memory model, benchmarking methodology, object layout and garbage collection, by a JVM engineer. Use for: stage 6, and for why a benchmark is lying.

- [Tool: "JMH", OpenJDK, github.com/openjdk/jmh](https://github.com/openjdk/jmh)
  The harness that handles warmup, dead-code elimination and statistics for JVM benchmarks. Use for: measuring anything on a JIT-compiled runtime without fooling yourself.

- [Docs: "JUnit 5 User Guide", JUnit Team, junit.org](https://junit.org/junit5/docs/current/user-guide/)
  The programming and extension model, including parameterised and nested tests. Use for: stage 5 mechanics.

- [Docs: "Maven Guides", Apache Software Foundation, maven.apache.org](https://maven.apache.org/guides/index.html)
  The build lifecycle, dependency mediation and scopes, from the project itself. Use for: what a build is actually doing, whichever tool runs it.

- [Style guide: "Google Java Style Guide", Google](https://google.github.io/styleguide/javaguide.html)
  Opinionated, complete and widely adopted, with the rationale attached. Use for: decisions the specification leaves open.

## Wisdom (Communities)

- [Archive: "OpenJDK Mailing Lists", OpenJDK, mail.openjdk.org](https://mail.openjdk.org/)
  The public archive where platform changes are proposed, argued and rejected, readable without subscribing. Use for: the reasoning behind a decision that no document records.

## Gaps

- The memory model has no gentle authoritative source. Chapter 17 is formal and "Java Concurrency in Practice" predates virtual threads, `VarHandle` and structured concurrency, so stage 4 uses the book for the model and the current specification and JEPs for the API. That split worked, with one caveat found while writing the stage: **a JEP describes the release it shipped in and is not revised when a later JEP changes the behaviour.** JEP 444 still states that `synchronized` pins a carrier thread, which JEP 491 changed. Read a JEP for intent and design rationale, and confirm current behaviour by running it.
- Garbage-collection tuning in depth rests on Shipilëv's posts and the virtual-machine guides. No single book is listed, and one may be needed before stage 6 is written.
- The six-month release cadence outpaces every book here. Version-sensitive claims go to the specification, the API documentation or the JEP index, and any lesson naming a release says which one.
- Frameworks have no source by design. When stage 7 judges whether a framework earns its place, that judgment needs a source and this list does not yet have one.
