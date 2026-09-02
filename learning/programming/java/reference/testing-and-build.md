---
title: Testing and build
description: The build task each command actually performs, the double to reach for, and the failure that means the artifact is wrong
type: reference
---

# Testing and Build

## Which test to write

Parameterising earns its keep when cases differ only in data: same setup, same call, same assertion, different numbers. It stops earning its keep once cases differ in what they assert. See [lesson 31](../lessons/0031-parameterised-tests.md).

| Situation | Construct | Reason |
|---|---|---|
| One behaviour, one input, one assertion | `@Test` | nothing varies |
| Same setup and assertion, different data | `@ParameterizedTest` | each declared case is its own test, so one bad case never hides another the way a `for` loop inside a `@Test` does |
| Cases differ in what they assert, not just what they feed in | separate `@Test` methods, one per behaviour | parameterising would hide a conditional inside the body that decides which assertion applies to which row |
| Case list only known at run time | `@TestFactory` returning `Stream<DynamicTest>` | a `@ParameterizedTest` source is fixed at discovery time; a factory is ordinary code |
| Input genuinely varies per run, or hunting flakiness | `@RepeatedTest` | repeating a deterministic assertion against fixed inputs proves nothing a single run did not |
| Several scenarios share one fixture | `@Nested` | groups tests around shared context without repeating it per method |

## JUnit versions and artifacts

The part of the ecosystem most likely to have drifted. See [lesson 29](../lessons/0029-your-first-test.md).

| Layer | Artifact | Purpose |
|---|---|---|
| Platform | `junit-platform-commons`, `-engine`, `-launcher` | discovers and runs tests; knows nothing about `@Test` |
| Engine | `junit-jupiter-engine` (Jupiter), `junit-vintage-engine` (old JUnit 4, for mid-migration) | plugs into the platform, understands one way of writing tests |
| API | `junit-jupiter-api`, `junit-jupiter-params` | the annotations and assertions you write against |
| Aggregate | `junit-jupiter` | pulls in API, params and engine; the right default for a project that both writes and runs its own tests |

**One version number.** Under JUnit 5, Platform was `1.x` while Jupiter was `5.x`. **JUnit 6 collapsed this**: Platform, Jupiter and Vintage all release as `6.1.3`, together, every time. Resolving the graph for a project declaring only `junit-jupiter` shows every module, Platform included, at `6.1.3`. Package names did not change (`org.junit.jupiter.api`), which is what makes the jump easy to miss.

- **Java 17+ at runtime**; can still test code compiled for older releases.
- **Removed in 6.0.0**: `junit-platform-runner`, `junit-platform-jfr` (JFR moved into `junit-platform-launcher`).
- Nullability uses JSpecify; `org.jspecify:jspecify` appears transitively on the test classpath.
- `@CsvSource`/`@CsvFileSource` switched to FastCSV in 6.0.0; a regression made `#` unchangeable, fixed in 6.1 with a `commentCharacter` attribute.
- `@Nested` classes run in deterministic order; `@TestMethodOrder` on the enclosing class is inherited by nested classes.

**The engine you never declared.** Declare only `junit-jupiter-api` and hand the classpath to the Platform's own `Launcher`: it throws `PreconditionViolationException: Cannot create Launcher without at least one TestEngine`. Run the identical POM under `mvn test` and **the build passes anyway**: Surefire notices `junit-jupiter-api` and silently resolves and injects a matching `junit-jupiter-engine`, even though the POM never asked for one. Maven is therefore not where you will ever see that exception. Declare the aggregate anyway (lesson 29).

## Lifecycle annotations

See [lesson 29](../lessons/0029-your-first-test.md). The default is a fresh test instance per method.

| Annotation | When it runs | Must be `static`? |
|---|---|---|
| `@BeforeAll` | once, before the first test | yes, under the default lifecycle; not under `PER_CLASS` |
| `@BeforeEach` | before every test, on that test's own instance | no |
| `@AfterEach` | after every test, pass or fail | no |
| `@AfterAll` | once, after the last test | yes, under the default lifecycle; not under `PER_CLASS` |

**`@TestInstance(Lifecycle.PER_CLASS)`** backs the whole class with one instance instead of one per method. It buys instance-method `@BeforeAll`/`@AfterAll` and a non-static `@MethodSource` factory. It costs independence: a field left dirty by one test is visible to the next. Reach for it deliberately, for one expensive shared fixture, not as a habit.

## Choosing an assertion

The assertion decides what the next reader sees on failure, not just whether the bug is caught. See [lesson 30](../lessons/0030-assertions-that-name-the-failure.md); compare `equals` versus `==` in [equality, hashing and ordering](equality-hashing-and-ordering.md).

| Checking | Assertion | On failure |
|---|---|---|
| Equal by value | `assertEquals(expected, actual)` | both operands printed via `toString`, e.g. `expected: <Point[x=1, y=2]> but was: <Point[x=1, y=3]>` |
| Equal by identity | `assertSame` | both operands' identity hash and content |
| A boolean condition, last resort | `assertTrue`/`assertFalse` | only `expected: <true> but was: <false>`; the operands are already collapsed and gone |
| An exception is expected | `assertThrows(Type.class, exec)` | "nothing was thrown", or the wrong type with the real exception attached as `Caused by:`; returns the caught exception for further asserts |
| Code must not throw (rare) | `assertDoesNotThrow` | a **Failure** naming the exception, versus an **Error** if left uncaught; its real use is the `ThrowingSupplier` overload, which also returns the value |
| Several checks on one object | `assertAll(execs...)` | `MultipleFailuresError` listing every failure, not just the first; catches any `Throwable`, not only assertion errors |
| `float`/`double` | `assertEquals(expected, actual, delta)` | exact comparison shows full precision, e.g. `<0.30000000000000004>`; fix with a `delta` |
| Arrays | `assertArrayEquals` | "array contents differ at index [n]" |
| Any `Iterable` | `assertIterableEquals` | "iterable contents differ at index [n]" |
| Text lines, allowing regex/fast-forward | `assertLinesMatch` | "expected line #n doesn't match actual line #n" |
| Time budget, thread-confined code | `assertTimeout` | runs on the calling thread; safe for `ThreadLocal`-bound code |
| Time budget that must not be overrun | `assertTimeoutPreemptively` | runs on a separate thread; breaks thread-confined code, see [concurrency](concurrency.md) |
| A branch that should be unreachable | `fail(message)` | unconditional failure with your message |

**Failure versus Error, together because the split recurs everywhere.** A **Failure** is an assertion that ran and disagreed. An **Error** is anything else: an uncaught exception in the body, or (lesson 31) a parameterised argument that failed to convert before the body ran. `Tests run: N, Failures: X, Errors: Y` separates the two.

## Parameterised test sources

Every source value starts as a `String`, implicitly converted to the parameter's type; a failed conversion is an **Error**, not a Failure. See [lesson 31](../lessons/0031-parameterised-tests.md).

| Source | Supplies | Gotcha |
|---|---|---|
| `@ValueSource` | one array of a primitive or `String`, one parameter | no `null`/empty case, no multiple parameters |
| `@NullSource`/`@EmptySource`/`@NullAndEmptySource` | one case each for `null`/`""`, stacking with `@ValueSource` | `@NullAndEmptySource` is shorthand for both |
| `@EnumSource` | one case per enum constant, or a filtered subset | case set comes from the enum's own declared constants |
| `@CsvSource` | rows become cases, columns become parameters | `commentCharacter` (`#` default) applies only to the `textBlock` form; a `#` row there is dropped silently, case count the only evidence; the same leading `#` inside the array form is **not** a comment |
| `@MethodSource` | a static factory returning a `Stream` (`Stream<Arguments>` or domain objects) | a local factory must be `static` unless `@TestInstance(PER_CLASS)`; an external factory must always be `static` |

Display names matter as much as the source: the default is positional (`method(int, int)[3]`); a `name` template with `{index}`/`{0}`/`{1}` substitutes the raw pre-conversion value, quotes included.

## Test doubles

Meszaros's five names, precisely, so "mock" stops being a catch-all. See [lesson 32](../lessons/0032-test-doubles.md).

| Kind | One-line test | Reach for the real thing (or a fake) instead when |
|---|---|---|
| Dummy | passed only to satisfy a signature, never used | it starts being used for an answer; then it is a stub |
| Stub | returns canned answers, nothing more | the collaborator's behaviour across several calls matters; a fake fits better |
| Spy | a stub that also records what happened | the recorded interaction is not actually part of the contract; then it is ceremony |
| Mock | a stub with expectations the test checks via `verify` | the point is a return value or resulting state; use `assert` first |
| Fake | a real, simplified working implementation (an in-memory map) | almost never; it survives a behaviour-preserving refactor by answering actual behaviour, not a pinned call sequence |

**The default-return trap.** An unstubbed mock returns `null`, `0`, or `false`, and does nothing for `void`. When that default matches what the test expected, the test passes without the mock ever answering the real question, indistinguishable from a broken implementation hardcoding the same value. Adding `verify(mock).theMethod(...)` exposes the gap: it fails with "zero interactions with this mock" against the broken version.

**`verify` versus asserting on state.** Asserting checks what the code produced, the promise to its caller. Verifying checks which calls the current implementation happened to make. Reach for `assert` first: a mock test pinning call order with `InOrder` fails on a refactor that changes order but not outcome; a fake-backed test asserting only final state survives it. Do not mock a type you do not own; wrap it, or use a real stand-in the library ships, such as `Clock.fixed(...)`.

## Dependency scopes

A scope answers two questions: compile classpath, and runtime classpath. See [lesson 33](../lessons/0033-declaring-dependencies.md).

| Scope | Compile | Runtime | Transitive to a consumer? |
|---|---|---|---|
| `compile` (default) | yes | yes | yes |
| `provided` | yes | no | **no** |
| `runtime` | no | yes | yes |
| `test` | yes, test sources only | yes, test execution only | **no** |
| `system` | yes | no | no; resolved from `<systemPath>`, effectively deprecated |
| `import` | n/a | n/a | valid only on a `<type>pom</type>` entry in `dependencyManagement` |

`provided` and `test` scoped dependencies of a library **do not propagate**: verified, a `test`-scoped and a `provided`-scoped dependency of `lib-a` are both absent from `consumer-b`'s tree even though `consumer-b` depends on `lib-a` at the default scope. `test` scope is literal: importing a `test`-scoped type from `src/main/java` fails `mvn compile` itself, before `mvn test` is reached.

## Reading the dependency graph

**Mediation: nearest wins, not newest.** Maven picks the version nearest the root; if two candidates sit at equal depth, **the one declared first in the POM wins**, with no reference to recency. See [lesson 33](../lessons/0033-declaring-dependencies.md): a newer Guava, pulled in one hop below a direct dependency, was **omitted for conflict** purely because another direct dependency at the same depth was declared earlier.

| Tool | Shows |
|---|---|
| `mvn dependency:tree` | the resolved graph as it stands |
| `mvn dependency:tree -Dverbose` | also every version considered and discarded, marked "omitted for conflict with `<version that won>`" |
| `mvn dependency:analyze` | **used, undeclared**: a class you import that resolves only transitively; **declared, unused**: a dependency nothing in your code references |

Three ways to force a version: declare the coordinate directly in your own `<dependencies>` (depth zero beats anything transitive); manage it in `<dependencyManagement>` with no matching `<dependencies>` entry, so it still arrives only transitively but at the managed version; or import a BOM (a `<type>pom</type>` artifact whose only content is `dependencyManagement`) with `<scope>import</scope>`, to manage many coordinates at once.

One tooling trap: `maven-dependency-plugin` 3.7.0 fails to read JDK 25 class files, `Unsupported class file major version 69`; 3.11.0 or later reads them correctly.

## Lifecycle phases and what runs

Naming a phase runs every phase up to and including it, in order, executing whatever is bound along the way. See [lesson 34](../lessons/0034-the-build-lifecycle.md). Maven ships three lifecycles (`clean`, `default`, `site`); `default` builds, tests and ships.

| Phase | What runs under `jar` packaging |
|---|---|
| `validate` | nothing bound by default |
| `compile` | `maven-compiler-plugin`'s `compile` goal: compiles `src/main/java` |
| `test-compile` | the compiler plugin compiles `src/test/java` |
| `test` | `maven-surefire-plugin`'s `test` goal: **a failing test stops the build here**, before `package` |
| `package` | `maven-jar-plugin`'s `jar` goal: collects `target/classes` into a jar; nothing compiled or run |
| `verify` | `maven-failsafe-plugin`'s `verify` goal, if configured: checks Failsafe's recorded results, fails the build if any failed |
| `install` | copies the artifact into the local repository |
| `deploy` | publishes it outward |

| Command | What it actually runs |
|---|---|
| `mvn compile` | `validate` through `compile` |
| `mvn package` | `validate` through `package`; a failing test means `package` is never reached |
| `mvn clean test` | `clean`'s `clean` phase, then `default` through `test`, in one invocation |
| `mvn integration-test` | `default` through `integration-test`; Failsafe records `*IT` results but **does not fail the build here** |
| `mvn verify` | `default` through `verify`; `post-integration-test` tears down what the integration tests started, then Failsafe fails the build if any recorded failure exists |
| `mvn install` | `default` through `install` |
| `./mvnw ...` | any of the above, through the exact Maven version pinned in `.mvn/wrapper/maven-wrapper.properties`, regardless of what is installed system-wide |

**The Surefire/Failsafe asymmetry silently passes a broken build.** Surefire fails the build the instant a unit test fails, in `test`. Failsafe does not fail at `integration-test`, because `post-integration-test` must tear down whatever the tests started whether they passed or not; only `verify` reports the failure. A pipeline stopping at `mvn integration-test` has silently disabled its own integration tests.

**Inspecting instead of guessing.** `mvn help:effective-pom` shows a plugin's real, project-specific version and binding. `mvn help:describe -Dcmd=test` reports **Maven's generic default plugin version for the packaging**, not what the project pins: verified, `describe` reported Surefire `3.5.4` for a project whose POM, build log and effective POM all agreed on `3.5.6`. Trust `effective-pom` or the log, not `describe`.

**`-DskipTests` versus `-Dmaven.test.skip=true`.** Both skip running tests; `-DskipTests` still runs `test-compile`, catching a test file that no longer compiles, while `-Dmaven.test.skip=true` skips `test-compile` entirely.

## Packaging strategies

An unconfigured `jar`-packaged build produces a manifest with no `Main-Class`; `java -jar` fails with "no main manifest attribute". Setting `mainClass` fixes that only for a project with no dependencies beyond the JDK. See [lesson 35](../lessons/0035-a-runnable-artifact.md).

| Strategy | Produces | Needs at run time | Cost |
|---|---|---|---|
| Plain jar, `Main-Class` set | the project's own classes plus a manifest | dependency classes on the classpath by some other means | a green build can be dead on arrival: `NoClassDefFoundError`, because Surefire tested against the full resolved classpath while `package` only ever collects the project's own classes |
| Manifest `Class-Path` + `copy-dependencies` | a thin jar plus a `lib/` directory of the actual dependency jars | `lib/`, alongside the jar, resolved relative to the jar's own location | `lib/` must travel with the jar; copy the jar alone and it is back on the cliff |
| Uber jar (`maven-shade-plugin`) | one self-contained jar, dependencies unpacked and repacked inside | nothing else | measured on one dependency: plain jar 3.19 KB versus shaded 699.0 KB, about 220 to 1, growing with each dependency; flattens each library's `META-INF`/licence provenance; needs a `ServicesResourceTransformer` so same-path `META-INF/services` entries concatenate rather than one overwriting another, and `relocation` for colliding transitive versions |
| `jlink`/`jpackage` (named, not taught) | a custom runtime image, or a platform installer | no separately installed JDK on the target | both assume a modular application, a bigger step than this stage takes |

Orthogonal facts: an automatic module's derived name and version come from the jar's file name when it hits a module path, and change if the file is renamed; `Automatic-Module-Name` fixes the name half. Identical source does not build byte-identical output by default, purely from zip entry timestamps; `project.build.outputTimestamp` made two builds hash identically, verified with `shasum`/`cmp`.

## Symptom to cause

Populated only from failures the lessons actually reproduced.

| Symptom | What it actually means |
|---|---|
| `NoClassDefFoundError` at `java -jar`, after a green build with passing tests | the plain jar packages only the project's own classes; Surefire ran with the full resolved classpath, `package` never copies dependency jars in (lesson 35) |
| `Cannot create Launcher without at least one TestEngine` | only reachable by calling the Platform `Launcher` directly; under Maven, Surefire silently resolves and injects an engine even for a bare `junit-jupiter-api` classpath, so the same gap passes `mvn test` (lesson 29) |
| A test passes while asserting nothing real happened | an unstubbed mock returned its type's default and the assertion happened to match it; a broken implementation that never consults the collaborator produces the identical pass (lesson 32) |
| `BUILD SUCCESS` at `mvn integration-test` despite a failing `*IT` | Failsafe defers failing the build to `verify`, after `post-integration-test` teardown; check `verify`, never `integration-test` alone (lesson 34) |
| An unexpected transitive dependency version | nearest-wins mediation picked the shallowest candidate; an equal-depth tie went to whichever was declared earlier in the POM, never the newest one (lesson 33) |
| A mock-based test breaks on a refactor that changed no observable behaviour | the test verified an interaction rather than asserting on resulting state; the interaction was never part of the contract (lesson 32) |
| `@BeforeAll method ... must be static` | the default per-method lifecycle builds a fresh instance per test, so no single instance exists yet to own a non-static `@BeforeAll` (lesson 29) |
| A `@MethodSource` factory errors before the test body runs | a local factory must be `static` unless `@TestInstance(PER_CLASS)`; an external factory must always be `static` (lesson 31) |
| A parameterised case is reported as an **Error**, not a Failure | JUnit could not convert the raw `String` to the declared parameter type before the body ran, distinct from an assertion mismatch (Failure) or an uncaught exception (also an Error) (lessons 30, 31) |
| A `@CsvSource` case count is smaller than the declared rows | the default `#` comment character dropped a row silently, in the `textBlock` form only; the array form never treats a leading `#` as a comment (lesson 31) |

## Handover checklist

The stage's done-when criterion as a list. See [lesson 35](../lessons/0035-a-runnable-artifact.md) for the full procedure.

- [ ] `mvnw`, `mvnw.cmd` and `.mvn/wrapper/maven-wrapper.properties` are committed, so a clone needs no pre-installed Maven (lesson 34).
- [ ] Every plugin and dependency in `pom.xml` is pinned to an exact version, not a range or unpinned "latest" (lesson 33).
- [ ] The README states the two commands that matter: build and test, and run what came out (lesson 35).
- [ ] From a clean copy, with nothing but a JDK on the path, `./mvnw clean verify` reports `BUILD SUCCESS` (lesson 35).
- [ ] The produced artifact runs with `java -jar`, from outside the build's own working directory (lesson 35).
- [ ] If the artifact has runtime dependencies, one of the three packaging strategies was chosen deliberately, not left as an unrunnable plain jar (lesson 35).

## Version table

Stable at the time of writing, distinct from a plugin's "latest" tag, which several of these publish as a beta or milestone. Pin the version actually tested. See [lesson 33](../lessons/0033-declaring-dependencies.md).

| Artifact | Stable, at time of writing | Latest published |
|---|---|---|
| `org.junit:junit-bom` | 6.1.3 | 6.1.3 |
| `maven-compiler-plugin` | 3.15.0 | 4.0.0-beta-5 |
| `maven-surefire-plugin` | 3.5.6 | 3.6.0-M1 |
| `maven-failsafe-plugin` | 3.5.6 | 3.6.0-M1 |
| `maven-jar-plugin` | 3.5.1 | 4.0.0-beta-1 |
| `maven-shade-plugin` | 3.6.2 | 3.6.2 |
| `maven-enforcer-plugin` | 3.6.3 | 3.6.3 |
| `maven-wrapper-plugin` | 3.3.4 | 3.3.4 |
| `org.mockito:mockito-core` | 5.23.0 | 5.23.0 |
| `org.assertj:assertj-core` | 3.27.7 | 4.0.0-M1 |

Baseline: JDK 25, the current long-term-support release; Maven 3.9 or later (Maven 4 is only a release candidate at time of writing); `maven-dependency-plugin` 3.11.0 or later, since 3.7.0 cannot read JDK 25 class files.

## Sources

- [JUnit User Guide](https://docs.junit.org/current/user-guide/): the primary source for the JUnit versions and lifecycle-annotations sections
- [JUnit API](https://docs.junit.org/current/api/): exact assertion overloads and annotation semantics
- [JUnit 6.1.3 release notes](https://docs.junit.org/6.1.3/release-notes/): the version collapse, removed artifacts, and the `commentCharacter` fix
- [Mockito API](https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/Mockito.html): `mock`, `when`, `verify`, `ArgumentCaptor`, the inline mock maker's agent notice
- [Maven guides index](https://maven.apache.org/guides/index.html): the entry point for every Maven guide used here
- [Introduction to the Build Lifecycle](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html): phases, goals, bindings and the three lifecycles
- [Maven POM Reference](https://maven.apache.org/pom.html): coordinates, scopes, `dependencyManagement`, `exclusions`, `optional`
- [Introduction to the Dependency Mechanism](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html): transitivity and mediation
- [Maven Surefire Plugin](https://maven.apache.org/surefire/maven-surefire-plugin/): the unit test runner and its phase binding
- [Maven Failsafe Plugin](https://maven.apache.org/surefire/maven-failsafe-plugin/): the integration test runner and `verify` behaviour
- [Maven Wrapper Plugin](https://maven.apache.org/tools/wrapper/maven-wrapper-plugin/): `wrapper:wrapper` and the files it generates
- [Guide to Uber JAR (Shade Plugin)](https://maven.apache.org/plugins/maven-shade-plugin/index.html): transformers and relocation
- [Configuring for Reproducible Builds](https://maven.apache.org/guides/mini/guide-reproducible-builds.html): `project.build.outputTimestamp`
- [Enforcer Plugin rule catalogue](https://maven.apache.org/enforcer/enforcer-rules/index.html): `banDynamicVersions`, `requireReleaseDeps`
- [`dependency:analyze`](https://maven.apache.org/plugins/maven-dependency-plugin/analyze-mojo.html): what "used undeclared" and "declared unused" check
- [The jar Command, Oracle](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jar.html): the manifest, `Main-Class`, `Class-Path`, module descriptors
- [Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html): the link shape used for JDK class documentation
