---
title: "30. Gradle and Dependency Management"
description: "The Kotlin DSL's type-safe accessors and where they run out, why a Gradle configuration is not a Maven scope, and the resolution rule that decides which version reaches the classpath"
type: lesson
---

# Lesson 30. Gradle and Dependency Management

**Mission link:** Stage 6 closes on someone else being able to clone, build, test and run your work. That is a property of the build file, and the capstone asks you to name what makes it true.
**Primary source:** [Docs: "Gradle Kotlin DSL Primer", Gradle](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
**Prerequisites:** [Lesson 29](0029-mocking.md), [Lesson 28](0028-test-frameworks.md), [Lesson 15](0015-higher-order-functions-and-lambdas.md)

## Warm-up

1. ▢ Kotlin classes and their members are final by default. What does that imply about mocking, and what is the better move than adding `open`?

<details markdown="1"><summary>Check</summary>

Any technique based on generating a subclass and overriding methods has nothing to work with, which is why a Kotlin-first library exists rather than a wrapper over a Java one. Marking a production class `open` changes its inheritance contract permanently to suit one test; introducing an interface, or writing a fake, puts the seam in the type system instead.

</details>

2. ▢ A Turbine test does not fail, it hangs. What is the usual cause?

<details markdown="1"><summary>Check</summary>

A flow that never terminates, collected through `testIn`, which cannot clean up its own coroutine. Either pass `runTest`'s `backgroundScope`, or end each turbine explicitly with `cancel()`, `awaitComplete()` or `awaitError()` before the scope ends. A hang rather than a red assertion means an outstanding coroutine nobody cancelled.

</details>

3. ▢ In a lambda with receiver, what is `this` inside the body, and what does that let the body call unqualified?

<details markdown="1"><summary>Check</summary>

`this` is the receiver, so the body can call that type's members and any extension on it without qualification. That is the mechanism behind the scope functions, behind `launch` resolving inside a `CoroutineScope` block, and, as of this lesson, behind every `dependencies { }` and `plugins { }` block in a Kotlin build script.

</details>

## Know this

**A Kotlin build script is Kotlin, which is the point and the price.** `build.gradle.kts` is compiled and type-checked, so the editor can complete it and a typo is an error rather than a mystery at task-execution time. What you get in exchange for the compilation is **type-safe model accessors**: `implementation` and `runtimeOnly` as configurations, `testImplementation` and `mavenCentral` inside their containers, `sourceSets`, and elements of `tasks` and `configurations` such as `compileJava` and `test`, all contributed by the plugins you applied ([Kotlin DSL Primer](https://docs.gradle.org/current/userguide/kotlin_dsl.html)). Every one of those blocks is a lambda with receiver, which is warm-up 3 turning up in a file you did not think of as Kotlin.

Accessors are not always there, and the documentation's own example shows the fallback: a script that applies a plugin with `apply(plugin = "java-library")` configures the same model with `configure<SourceSetContainer> { ... }` and `configure<JavaPluginExtension> { ... }` instead, with `the<T>()` available when a reference is all you need. Two ways to find out what exists rather than guessing: read the applied plugin's documentation, or run `./gradlew kotlinDslAccessorsReport`, which prints the Kotlin code for the model elements those plugins contribute, names and types together.

**A configuration is not a Maven scope, and this is where a Java background misleads.** Maven's scopes answer two questions, compile classpath and runtime classpath, and the [Java workspace's testing and build sheet](../../java/reference/testing-and-build.md) has that table along with how Maven reads a dependency graph. Gradle splits the idea by **role** instead, and a configuration is meant for one role only ([Creating Dependency Configurations](https://docs.gradle.org/current/userguide/declaring_configurations.html)):

|Role|What it is for|With the Java plugins|
|---|---|---|
|Declarable|Where you put dependencies|`api` (with `java-library` only), `implementation`, `compileOnly`, `runtimeOnly`, and the test variants|
|Resolvable|What you resolve to get jars and directories|`compileClasspath`, `runtimeClasspath`, and their test equivalents|
|Consumable|What Gradle publishes so other projects can depend on you|`apiElements` (with `java-library`) and `runtimeElements`|

**`api` against `implementation` is a design decision, not a formality.** The `java-library` plugin introduces the idea of an API exposed to consumers: dependencies declared in `api` are transitively exposed and appear on the **compile classpath of consumers**, while dependencies in `implementation` are not exposed and do not leak into a consumer's compile classpath ([Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html)). So `api` is a promise about your library's surface. Declare something `api` that you only use internally and every consumer can now compile against it, which means you can no longer replace it without breaking them. `implementation` is the right default, and `api` is what you write deliberately for a type that genuinely appears in your own signatures.

**Version catalogs put the versions in one place.** `gradle/libs.versions.toml` is imported automatically as `libs`, and each alias becomes a type-safe accessor with dashes mapped to dots, so `ktor-client-core` is reachable as `libs.ktor.client.core` while a single-segment alias such as `junit` stays flat as `libs.junit` ([Version Catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html)). Further catalogs are registered in the settings script with `from(files(...))`, and each generates its own extension. One limitation worth knowing before you hit it: within a catalog, `from` may be called only once, so a catalog cannot be assembled from two files.

**The resolution rule, which is the sharpest difference of all.** When two components depend on the same module at different versions, Gradle considers all requested versions across the graph and, **by default, selects the highest** ([Graph Resolution](https://docs.gradle.org/current/userguide/graph_resolution.html)). Its own example: your project depends directly on `guava:20.0`, and `guice:4.2.2` brings `guava:25.1-android`, so Gradle resolves 25.1-android.

Maven answers the same question differently, and the Java sheet records it as verified there: **nearest wins, not newest**, with ties broken by whichever was declared first in the POM. Two consequences for anyone crossing over. A Maven habit of declaring a coordinate directly to pin an older version does not work in Gradle, where depth buys nothing and a constraint or a `strictly` declaration is the tool; note that a `strictly` version lower than the highest requested makes resolution fail rather than quietly winning. And "highest" is not purely numeric: Gradle prefers versions without qualifiers, comparing base versions first, so `1.0.0` is treated as higher than `1.0.0-beta`.

Gradle also handles a second kind of conflict, where two modules provide the same capability rather than different versions of one module. That one is resolved during variant selection and is beyond this lesson.

## Practice

1. ▢ A build script does `apply(plugin = "java-library")` and then `sourceSets { ... }`, which does not compile. Why, and what does the documentation do instead?

<details markdown="1"><summary>Check</summary>

Type-safe accessors are generated from the plugins the script's model knows about, and applying one this way leaves them unavailable, so `sourceSets` is not in scope as an accessor. The documented fallback is to configure the model by type: `configure<SourceSetContainer> { named("main") { ... } }`, and `configure<JavaPluginExtension> { ... }` for the extension. `the<T>()` is the lighter form when you only need a reference. If you do not know what a plugin contributes, `./gradlew kotlinDslAccessorsReport` prints it rather than leaving you to guess.

</details>

2. ▢ A library declares `api("com.fasterxml.jackson.core:jackson-databind:2.17.0")` but uses Jackson only inside its own implementation, with no Jackson type in any public signature. What does that cost?

<details markdown="1"><summary>Check</summary>

Jackson is now transitively exposed to every consumer and lands on their compile classpath, so consumers can compile against it, and some will. That makes an internal choice part of your library's surface: swapping Jackson out, or moving to a version with an incompatible API, becomes a breaking change for people who never asked for it. `implementation` gives the same runtime behaviour without the exposure, which is why it is the default and `api` is a deliberate statement about types that appear in your own signatures.

</details>

3. ▢ Your project depends directly on `guava:20.0`. It also depends on `guice:4.2.2`, which depends on `guava:25.1-android`. Predict which version of Guava ends up on the classpath under Gradle, and under Maven.

<details markdown="1"><summary>Hint</summary>

One tool asks how far away each candidate is. The other asks how high each candidate is.

</details>

<details markdown="1"><summary>Check</summary>

Gradle resolves `25.1-android`: it considers every requested version in the graph and by default selects the highest, regardless of where in the graph it was requested. Maven resolves `20.0`: nearest wins, and a direct dependency sits at depth zero, so the transitive 25.1-android is omitted for conflict. Same graph, two answers. The practical trap is a Maven-trained reflex, that declaring the version you want directly is how you pin it, which in Gradle changes nothing about who wins. There you state it as a constraint, and a `strictly` declaration below the highest requested version fails the build rather than silently winning.

</details>

4. ▢ A catalog declares `ktor-client-core`, `ktor-client-cio` and `junit`. Write the accessor for each, and say what the dashes did.

<details markdown="1"><summary>Check</summary>

`libs.ktor.client.core`, `libs.ktor.client.cio`, and `libs.junit`. Each dash in an alias becomes a dot in the generated accessor, which creates nested groups an IDE can complete, so related libraries cluster under a shared prefix. A single-segment alias stays flat. The naming of aliases is therefore a small API design exercise: `ktor-client-core` reads well as a group, whereas an alias with no dashes puts everything at the top level.

</details>

5. ▢ Which claim about a Gradle configuration is correct?

    - a) A Gradle configuration is a Maven scope with a different name and syntax
    - b) A Gradle configuration has one role: declarable, resolvable, or consumable, not several
    - c) A Gradle configuration is resolved eagerly, so declaring one downloads its dependencies
    - d) A Gradle configuration called api exists in any project applying the java plugin

<details markdown="1"><summary>Check</summary>

**b)** Configurations are intended for a single role, and the Java plugins give you a set of each: declarable ones you put dependencies into, resolvable ones that produce a classpath, consumable ones Gradle publishes for other projects. (a) is the assumption this lesson exists to correct: Maven's scopes answer compile-and-runtime questions, while Gradle splits by role. (c) confuses declaring with resolving, which are two different phases and two different kinds of configuration. (d) gets the plugin wrong: `api` arrives with `java-library`, not with `java`.

</details>

6. ▢ **Stage capstone.** The stage closes on someone else being able to clone your project and build, test and run it. Name what the build has to get right for that to be true, and for each item say what breaks when it is missing.

<details markdown="1"><summary>Check</summary>

A defensible list, with the failure attached to each:

**A pinned build tool.** The checked-in Gradle wrapper is what makes `./gradlew build` mean the same thing on your machine and theirs; without it the build depends on whatever Gradle the newcomer happened to install.

**Versions declared in one place.** A version catalog at `gradle/libs.versions.toml`, imported automatically as `libs`, so the same coordinate cannot appear at two versions in two modules. Without it, versions drift per module and the answer to "which version are we on" becomes a grep.

**Declared, not inherited, dependencies.** Anything you import should be something you declared, not something that arrived transitively. When it is inherited, an upgrade elsewhere in the graph removes it from your classpath and the failure appears in code that nobody touched.

**The right configuration for each dependency.** `implementation` by default, `api` only for types in your own signatures, `testImplementation` for test-only tooling. Get this wrong towards `api` and your internals become other people's compile-time contract; wrong towards `compileOnly` and it compiles for you and fails at runtime for them.

**A resolution outcome you can predict and inspect.** Knowing that Gradle takes the highest requested version, so that when the classpath holds something you did not choose, you know to look for who requested it rather than assuming a bug.

**Tests that run without your machine.** From lesson 28: no hardcoded dispatcher that a test cannot replace, and nothing that depends on real time, real network, or a path only you have.

An answer listing only "commit the wrapper" has the right first item and none of the reasoning. The point of the stage is that "it works on my machine" is a statement about a build file, and every item above is a way that file can quietly be about your machine instead.

</details>

## Real-world reps

- [ ] Open a Kotlin project's `build.gradle.kts` and classify every dependency by configuration. For each `api`, check whether the library actually appears in a public signature.
- [ ] Run your build's dependency report and find one library at a version nobody declared. Identify who requested it, and whether the highest-wins rule is what put it there.
- [ ] Tomorrow: take a project without a version catalog and write the `libs.versions.toml` it would have. Note every coordinate that turns out to be declared at two different versions.

## Going further

- [Docs: "Gradle Kotlin DSL Primer", Gradle](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
- [Docs: "Version Catalogs", Gradle](https://docs.gradle.org/current/userguide/version_catalogs.html)
- [Docs: "Graph Resolution", Gradle](https://docs.gradle.org/current/userguide/graph_resolution.html)
- [Testing and build sheet, Java workspace](../../java/reference/testing-and-build.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
