---
title: 29. Your First Test
description: Where tests live, what the runner actually does, and the version scheme every write-up gets wrong
type: lesson
---

# Lesson 29. Your First Test

**Mission link:** A Java service you own is a service you can change without dread, and that confidence comes from tests that run automatically and fail loudly, so this lesson sets up the one piece of machinery everything else in this stage builds on.
**Primary source:** [JUnit User Guide](https://docs.junit.org/current/user-guide/)
**Prerequisites:** [Lesson 7](0007-classes-and-objects.md), [Lesson 3](0003-equals-and-hashcode.md)

## Warm-up

1. ▢ A class declares no `equals` at all. Two separate objects hold identical field values. What does `a.equals(b)` return, and why?

<details markdown="1"><summary>Check</summary>

`false`, unless `a` and `b` are the same object. With no override, a class inherits `Object`'s `equals`, which compares identity, not field values. Nothing about "looks the same" makes two objects equal to Java.

</details>

## Know this

### Where tests live

A Maven project keeps production code under `src/main/java` and test code under a separate root, `src/test/java`, mirroring the same package structure. A class `com.example.Order` in `src/main/java/com/example/Order.java` gets its test at `src/test/java/com/example/OrderTest.java`, declared in the same package, `com.example`.

Same package, different root, is doing real work. Lesson 7 covered four access levels, and the one with no keyword at all, package-private, means visible to any class in the same package regardless of file. Putting the test in the production class's own package means the test can call a package-private constructor, read a package-private field, or invoke a package-private method exactly as another class in the production package could, with no getter written solely to let a test see in. You are not making anything more public than the design already calls for; you are placing the test where the access it needs already exists.

This is also the point where a build tool stops being optional. Lesson 7's single-file source launcher, `java Scratch.java`, runs one file with no separate compile step. That is fine for a lesson's worth of code, but it has no notion of two source roots, and no way to add a testing library to the classpath for one root and not the other. A build tool answers exactly those questions: which files compile together, and which of that only matters for tests. Maven's lifecycle, and what a "phase" actually runs, is lesson 34's subject; for now, treat `mvn test` as the command that compiles both roots and runs whatever it finds under the test one.

### Three layers, because every error message names one of them

JUnit is not one library. It is three, stacked:

- The **JUnit Platform** discovers tests and runs them. It knows nothing about `@Test` or any other specific annotation.
- A **test engine** plugs into the platform and understands one particular way of writing tests. **Jupiter** is the engine for the annotations this lesson teaches. **Vintage** is a separate engine that runs old JUnit 4 tests, so a codebase mid-migration can run both kinds in one build.
- The **Jupiter API** is the set of annotations and assertions you actually write against: `@Test`, `@BeforeEach`, `assertEquals`, and the rest.

That split explains the shape of nearly every failure you will hit in this stage: a missing annotation is an API mistake, a missing engine is a platform-level mistake, and a build tool asking "which provider did you use" is asking about the layer in between.

Here is where the version story usually goes wrong, and where most existing write-ups spend paragraphs on a problem that no longer exists. Under JUnit 5, the three sub-projects published different version numbers: the Platform was on a `1.x` line while Jupiter was on `5.x`, so a Jupiter 5.10 project depended on a Platform in the 1.10s. **JUnit 6 collapsed that into one number.** Platform, Jupiter and Vintage all release as the same version, `6.1.3`, together, every time:

```text
JUnit 6.1.3 = JUnit Platform + JUnit Jupiter + JUnit Vintage
```

That is the exact line the User Guide leads with, and it is worth reading literally: one release train, three modules, no separate numbering to reconcile. What makes the jump from "5" to "6" easy to miss entirely is that **the package names did not change**. `org.junit.jupiter.api`, `org.junit.jupiter.params`, everything you might have written or copied against Jupiter 5 compiles unchanged against Jupiter 6, because the API surface is the same. The version number moved; the import statements did not.

Confirmed by resolving the dependency graph for a project that declares only the aggregate artifact at `6.1.3`:

```text
org.junit.jupiter:junit-jupiter:jar:6.1.3
├─ org.junit.jupiter:junit-jupiter-api:jar:6.1.3
│  └─ org.junit.platform:junit-platform-commons:jar:6.1.3
├─ org.junit.jupiter:junit-jupiter-params:jar:6.1.3
└─ org.junit.jupiter:junit-jupiter-engine:jar:6.1.3
   └─ org.junit.platform:junit-platform-engine:jar:6.1.3
```

Every module resolved, Platform and Jupiter alike, comes out at `6.1.3`. Nothing to reconcile.

### One artifact, or three

The Jupiter group publishes `junit-jupiter-api`, the annotations and assertions you write against, and `junit-jupiter-engine`, the engine that executes what those annotations describe, as two separate artifacts, because a project sometimes needs one without the other; a plugin that only generates test code needs the API but never runs anything itself. It also publishes `junit-jupiter`, an aggregate that pulls in `junit-jupiter-api`, `junit-jupiter-params` and `junit-jupiter-engine` together, so an ordinary project does not have to reason about which of the three it needs. For a project that both writes and runs its own tests, which is nearly every project, the aggregate is the right default: one dependency, on one version, and the split stops being something you have to think about.

A minimal POM for this lesson needs only the aggregate, imported through the JUnit BOM so the version is declared once, plus a compiler and test-runner plugin. Dependency scopes and version mediation, why `<scope>test</scope>` matters and how a BOM actually works, belong to lesson 33; take this POM as given for now:

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.junit</groupId>
      <artifactId>junit-bom</artifactId>
      <version>6.1.3</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### What happens when the engine is missing

The three-layer split is not just trivia; a project that declares `junit-jupiter-api` but never pulls in an engine has a genuine gap, because the API by itself has nothing that can execute a `@Test` method. Declare only the API and run the platform's own `Launcher` directly, bypassing any build tool:

```java
Launcher launcher = LauncherFactory.create();
launcher.execute(request);
```

```text
org.junit.platform.commons.PreconditionViolationException: Cannot create Launcher without at least one TestEngine; consider adding an engine implementation JAR to the classpath
```

That message is the three-layer model made concrete: the Platform refused to even start, because it found an API but no engine willing to run anything written against it.

Here is the surprise, verified by actually declaring only `junit-jupiter-api` in a POM and running `mvn test`: **the build passes anyway.** Maven's Surefire plugin, when it drives the JUnit Platform, notices that the test dependencies mention `junit-jupiter-api` and resolves a matching `junit-jupiter-engine` for you, adding it to the classpath it launches with even though the POM never asked for it. That is a real, deliberate convenience in Surefire, not a mistake in this lesson, and it means Maven is not where you will ever see the exception above; you would need to call the Platform's `Launcher` directly, the way the snippet just did, to see the layer the aggregate artifact and Surefire's auto-detection both exist to paper over. Declare the aggregate anyway: relying on a plugin's auto-detection to cover a missing dependency is not a habit worth building.

### @Test, and how little it asks of you

```java
class PriceCalculatorTest {

    @Test
    void discountAppliesToOrdersOverFifty() {
        assertEquals(45.0, PriceCalculator.applyDiscount(50.0));
    }
}
```

Neither the class nor the method needs `public`. JUnit Jupiter discovers and invokes test classes and methods through reflection, and it works with package-private access on both, which is consistent with the test living in the same package as the code it exercises. A `@Test` method also returns nothing; the way a test signals failure is by throwing, whether that throw comes from a failed assertion or from an unexpected exception escaping the method. There is no return value to check, because there is nothing a return value could usefully report that a thrown exception cannot.

### A fresh instance for every test method

This is the single fact that makes everything else about writing a test safe: **by default, JUnit creates a new instance of the test class before running each test method.** One instance runs exactly one test, and that instance is then discarded. Two test methods in the same class never share an object, and by extension never share whatever state a field on that object might hold, which is what lets you write test methods in any order and get the same result from each.

An instance counter makes this visible rather than asserted:

```java
class InstanceTest {

    static int instancesCreated = 0;
    int seenAtStart;

    InstanceTest() {
        instancesCreated++;
        seenAtStart = 0;
    }

    @Test
    void firstTest() {
        seenAtStart++;
        System.out.println("firstTest: seenAtStart=" + seenAtStart + " instancesCreated=" + instancesCreated);
    }

    @Test
    void secondTest() {
        seenAtStart++;
        System.out.println("secondTest: seenAtStart=" + seenAtStart + " instancesCreated=" + instancesCreated);
    }
}
```

Run under `mvn test`, this printed:

```text
firstTest: seenAtStart=1 instancesCreated=1
secondTest: seenAtStart=1 instancesCreated=2
```

Both tests saw `seenAtStart` at `1`, never `2`, because each ran against its own freshly constructed instance; the static counter, which does belong to the class rather than to any one instance, climbed to `2` because two instances really were built.

Annotate the same class `@TestInstance(Lifecycle.PER_CLASS)` and only that changes:

```text
firstTest: seenAtStart=1 instancesCreated=1
secondTest: seenAtStart=2 instancesCreated=1
```

One instance now backs the entire class. `instancesCreated` never passes `1`, and `seenAtStart` climbs across both tests, `1` then `2`, because the same object's field is doing the accumulating. What `PER_CLASS` gives up is exactly the independence the default mode buys: a field left dirty by one test is now visible to the next, so a test's outcome can depend on what ran before it. What it gives back, beyond letting `@BeforeAll` and `@AfterAll` be ordinary instance methods, is not enough to trade independence away for by default; reach for it deliberately, for the case where every test in a class shares one expensive piece of setup, not as a habit.

### @BeforeEach, @AfterEach, @BeforeAll, @AfterAll

`@BeforeEach` and `@AfterEach` run around every test method, on the instance that method itself runs on, which is exactly what you would expect given a fresh instance per method: setup that a test's constructor cannot conveniently do, and teardown that has to happen whether the test passed or threw, both belong here. `@BeforeAll` and `@AfterAll` run once for the whole class, before the first test and after the last.

Under the default per-method lifecycle, no single instance exists that could sensibly own a `@BeforeAll` method, since a new one is about to be built for every test and none of them is "the" instance the whole class runs against. That is why `@BeforeAll` and `@AfterAll` **must be `static`** under the default lifecycle. Leaving one non-static produces this exactly, captured by running it:

```text
[ERROR] @BeforeAll method 'void com.example.BeforeAllNotStaticTest.setUp()' must be static unless the test class is annotated with @TestInstance(Lifecycle.PER_CLASS).
```

Note what the message itself points to: under `PER_CLASS`, one instance already exists for the whole class before any test runs, so `@BeforeAll` and `@AfterAll` are free to be ordinary instance methods there, and the restriction lifts. That is the trade the previous section described from the other side: less independence, but the lifecycle methods relax.

### assertEquals(expected, actual), in that order

Jupiter's `assertEquals` takes the expected value first and the actual value second, and getting that backwards does not fail to compile, it just produces a failure message that names the values incorrectly. This compares with `equals`, the same method lesson 3 covered, so the same rule applies: two records or two objects with a correct `equals` compare by value, and anything relying on the default, identity-based `equals` compares by reference regardless of what the fields hold.

```java
int expected = 42;
int actual = 41;
assertEquals(actual, expected);   // arguments swapped
```

```text
org.opentest4j.AssertionFailedError: expected: <41> but was: <42>
```

Read that message at face value and you would conclude the test wanted `41` and got `42`. The truth is the opposite: the code computed `41`, and `42` was what the test actually wanted. The arguments were passed in the wrong order, so the message faithfully reports what it was told, and what it was told was backwards. There is no tooling that catches this, since both arguments are `int` and the call compiles either way; the only defence is writing `assertEquals(expected, actual)` in that order as a fixed habit, every time. Whether to reach for `assertEquals` at all versus something like `assertThrows` for an expected exception is lesson 30's territory; this lesson is only about the argument order once you are calling it.

### @DisplayName and @Disabled

```java
@DisplayName("discount of 10% applies once the order passes fifty")
@Test
void discountAppliesToOrdersOverFifty() {
    // ...
}

@Disabled("waiting on ORD-412 to fix the rounding")
@Test
void discountRoundsToTheNearestCent() {
    // ...
}
```

`@DisplayName` replaces the method name with a readable sentence wherever a test's name is shown, in an IDE's test tree or a build's report, without renaming the method itself. `@Disabled` skips a test entirely, and unlike commenting the method out, it still shows up in the results as skipped rather than disappearing, which is the difference between a test deferred and a test nobody remembers existed. The reason string appears in the report too, which is why leaving `@Disabled` bare is the same missing-context mistake as an empty catch block.

### What the runner reports

`mvn test` prints one summary line per test class as it finishes, and a total at the end:

```text
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.031 s -- in com.example.InstanceTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

That total line is the number worth reading first: run, failed, errored (an unexpected exception rather than a failed assertion), and skipped, added up across every class. The detail behind each individual test, including anything printed to standard output, does not appear on the console by default; it lands in `target/surefire-reports`, one text file and one XML file per test class, which is where a failing assertion's full stack trace actually lives. A continuous integration system almost always reads the XML file, not the console log.

## Practice

1. ▢ Predict what changes if you delete the `static` keyword from `instancesCreated` in the counter example, keeping the default per-method lifecycle. Would either printed line change?

<details markdown="1"><summary>Check</summary>

No. `instancesCreated` would become an instance field, so each fresh instance would see its own copy starting at `0`, and the constructor's `instancesCreated++` would take it to `1` every time. The printed `instancesCreated=1 instancesCreated=2` would become `instancesCreated=1 instancesCreated=1`, since there is no longer one shared count for two instances to add to. `seenAtStart` is unaffected either way, since it was never static.

</details>

2. ▢ A test class has one `@Test` method and one `@BeforeEach` method that opens a file and stores the handle in an instance field. A teammate adds a second `@Test` method to the same class, expecting to reuse the handle the first test opened. What actually happens, and why?

<details markdown="1"><summary>Hint</summary>

Ask how many times `@BeforeEach` runs, and against how many instances.

</details>

<details markdown="1"><summary>Check</summary>

The second test does not see the first test's handle. `@BeforeEach` runs before every test method, and under the default lifecycle each test method runs on its own fresh instance, so the second test gets its own new instance, its own `@BeforeEach` call, and its own freshly opened handle, not the first one. Nothing is shared, by design; sharing an open resource across tests through instance state is exactly what the per-method lifecycle exists to prevent.

</details>

3. ▢ This test class fails to build. Say what the error will name, without running it.

   ```java
   class ReportTest {
       @BeforeAll
       void setUp() {
           System.out.println("setUp ran");
       }

       @Test
       void aTest() {
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

The error names `setUp`, and says it must be `static` unless the class is annotated `@TestInstance(Lifecycle.PER_CLASS)`. Under the default per-method lifecycle there is no single instance that could own a `@BeforeAll` method, since a fresh one is built for every test, so Jupiter requires it to be callable without any instance at all, which is what `static` means.

</details>

4. ▢ Predict the exact failure message.

   ```java
   String expected = "gold";
   String actual = "silver";
   assertEquals(actual, expected);
   ```

<details markdown="1"><summary>Hint</summary>

`assertEquals` reports its first argument as "expected" regardless of what the variable holding it is named.

</details>

<details markdown="1"><summary>Check</summary>

```text
org.opentest4j.AssertionFailedError: expected: <silver> but was: <gold>
```

The message calls `"silver"` the expected value and `"gold"` the actual one, which is backwards from what the variable names say, because the call passed `actual` first and `expected` second. The message is honest about the order it was given; the order was wrong.

</details>

5. ▢ A class declares `junit-jupiter-api` as its only test dependency and no engine. Predict what `mvn test` does, then say what would happen instead if the same classpath, with no engine JAR anywhere on it, were handed to `LauncherFactory.create()` directly.

<details markdown="1"><summary>Check</summary>

Under Maven, the build passes. Surefire detects `junit-jupiter-api` on the test classpath and resolves a matching `junit-jupiter-engine` itself, even though the POM never declared one, so the missing dependency never becomes visible. Handed to the bare Platform `Launcher` with no build tool involved, there is no such auto-detection, and `LauncherFactory.create()` throws `PreconditionViolationException: Cannot create Launcher without at least one TestEngine`, which is the failure the three-layer model predicts and the one Maven happens to paper over.

</details>

## Real-world reps

- [ ] Take one existing class you did not write a test for yet, and create its test file under `src/test/java` in the same package, with one `@Test` method that calls one method on it.
- [ ] Find a test in code you already have that declares a `@BeforeAll` method. Check whether it is `static`, and if it is not, check for `@TestInstance(Lifecycle.PER_CLASS)` on the class.
- [ ] Search your own test code for `assertEquals` calls and check the argument order on three of them against the values they actually compare.
- [ ] Open `target/surefire-reports` (or your build tool's equivalent) after a test run you have not looked at before, and find one piece of detail that the console summary did not show you.
- [ ] Tomorrow: write the instance counter from this lesson, or your own version of it, and watch a fresh instance reset the count on the very next test method.

## Going further

- [Test Instance Lifecycle](https://docs.junit.org/6.1.3/writing-tests/test-instance-lifecycle.html): the full trade-off between `PER_METHOD` and `PER_CLASS`, including how to change the project-wide default
- [Annotations](https://docs.junit.org/6.1.3/writing-tests/annotations.html): every annotation Jupiter defines, in one reference list
- [Dependency Metadata](https://docs.junit.org/6.1.3/appendix.html#dependency-metadata): exactly what each Platform, Jupiter and Vintage artifact contains, straight from the project that publishes them
- [Testing and build](../reference/testing-and-build.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
