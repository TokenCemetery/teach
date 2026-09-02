---
title: 31. Parameterised Tests
description: One test method, many cases, and the line where a loop inside a test stops being good enough
type: lesson
---

# Lesson 31. Parameterised Tests

**Mission link:** Owning a Java service means owning the report a failing test produces at two in the morning, and a parameterised test is what turns "the suite is red" into "input 3 and input 5 are wrong" without anyone reading a stack trace first.
**Primary source:** [Parameterized Classes and Tests, JUnit User Guide](https://docs.junit.org/current/writing-tests/parameterized-classes-and-tests.html)
**Prerequisites:** [Lesson 30](0030-assertions-that-name-the-failure.md), [Lesson 12](0012-enums.md)

## Warm-up

1. ▢ Lesson 30 argued that `assertEquals(expected, actual)` reports more on failure than `assertTrue(expected == actual)` does. What extra information does the `assertEquals` failure carry that `assertTrue`'s does not?

<details markdown="1"><summary>Check</summary>

`assertEquals` reports both values it compared: what was expected and what actually turned up. `assertTrue` only reports that some boolean expression evaluated to `false`, with no record of what either side of that expression actually was, so the reader has to go back to the source line to find out. The same gap reopens at the level of a whole test method: which one, of several inputs, produced the `false`.

</details>

## Know this

### One test method, five cases, and what a loop throws away

Here is a deliberately buggy method: it triples every integer correctly except two of them.

```java
public class Tripler {
    public static int triple(int n) {
        if (n == 3) return 10;
        if (n == 5) return 16;
        return n * 3;
    }
}
```

The obvious way to check it against several inputs is a `for` loop inside one `@Test` method:

```java
@Test
void tripleOverFiveInputs() {
    int[] inputs = {1, 2, 3, 4, 5};
    int[] expected = {3, 6, 9, 12, 15};
    for (int i = 0; i < inputs.length; i++) {
        assertEquals(expected[i], Tripler.triple(inputs[i]), "input " + inputs[i]);
    }
}
```

Run that under Maven Surefire and this is the whole report:

```text
Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
l0031.LoopTest.tripleOverFiveInputs -- Time elapsed: 0.020 s <<< FAILURE!
org.opentest4j.AssertionFailedError: input 3 ==> expected: <9> but was: <10>
	at l0031.LoopTest.tripleOverFiveInputs(LoopTest.java:12)
```

One test ran. It failed on input 3, and `assertEquals` threw right there, unwinding the loop before it reached input 4 or input 5. Input 5 was also wrong, and the report says nothing about it, because the loop never got there. Fix the input-3 bug, rerun, and the suite goes green with input 5 still broken; the loop only ever shows the earliest failure it happens to reach.

Rewrite the same five cases as a parameterised test instead, one method, one annotation, five declared inputs:

```java
@ParameterizedTest
@CsvSource({
    "1, 3",
    "2, 6",
    "3, 9",
    "4, 12",
    "5, 15"
})
void tripleOverFiveInputs(int input, int expected) {
    assertEquals(expected, Tripler.triple(input));
}
```

Same buggy `Tripler`, same five cases, and the report this time:

```text
Tests run: 5, Failures: 2, Errors: 0, Skipped: 0
l0031.ParamTest.tripleOverFiveInputs(int, int)[3] -- Time elapsed: 0.006 s <<< FAILURE!
org.opentest4j.AssertionFailedError: expected: <9> but was: <10>
l0031.ParamTest.tripleOverFiveInputs(int, int)[5] -- Time elapsed: 0.002 s <<< FAILURE!
org.opentest4j.AssertionFailedError: expected: <15> but was: <16>
```

Five tests ran, not one: each declared case is its own JUnit test with its own pass or fail. Cases 1, 2 and 4 pass, cases 3 and 5 fail, independently, by index, in the same run, and fixing input 3 does not hide input 5. This is the entire case for parameterising: a loop inside a test method is one test with several assertions chained by control flow, so the first thrown exception ends it, while a parameterised test turns each case into its own test, and JUnit's execution model already guarantees that one test's failure does not stop another from running and being reported. Everything else in this lesson is detail on top of that one fact.

### `@ParameterizedTest` replaces `@Test`, it does not join it

A method takes exactly one of the two. `@ParameterizedTest` tells JUnit that the method's parameters come from a source you also declare, and every parameter the method lists has to be satisfiable from that source, in order, or resolution fails before the method body ever runs. There is no annotation that means "run this once as a plain test and also run it several times with arguments"; if you want both, write two methods.

### Sources: what each one is actually for

`@ValueSource` supplies a single array of one primitive type or `String`: the simplest shape a case can take, one value in, nothing else varying, and no more than one parameter.

`@NullSource`, `@EmptySource` and `@NullAndEmptySource` add edge cases a `@ValueSource` array cannot express on its own, since `null` and `""` are not values you can drop into a `String[]` literal as deliberate cases. Stacked alongside a `@ValueSource`, each adds its own case to the count. Verified: `@NullSource`, `@EmptySource` and `@ValueSource(strings = {"a", "bb", "ccc"})` on one method produced `Tests run: 5`, one case each for `null` and `""`, plus the three declared strings. `@NullAndEmptySource` is shorthand for both of the first two at once.

`@CsvSource` supplies a small table inline, each row becoming one case and each column becoming one parameter, which is the shape most real test data actually has: several related values that belong together as one row.

`@EnumSource` runs the test once per constant of a named enum, or a filtered subset by name. Run against `java.time.DayOfWeek` with no filter, it produced `Tests run: 7`, once per day, the source being the enum's own declared set from [Lesson 12](0012-enums.md), rather than a set you had to type out again.

`@MethodSource` is the one that carries real weight, because a static factory method can return anything, not just primitives or CSV rows: a `Stream<Arguments>` of tuples, or a `Stream` of domain objects the test method takes directly. Once a case needs an object graph, a builder result, or several fields that make no sense flattened into CSV columns, `@MethodSource` is the only one of these that can carry it.

### `@MethodSource` needs a static factory, usually

Point `@MethodSource` at a factory method that is not `static`, and the test does not run, it errors before the method body is reached:

```java
class MethodSourceNonStaticTest {
    Stream<String> words() { return Stream.of("a", "b", "c"); }

    @ParameterizedTest
    @MethodSource("words")
    void wordIsNotBlank(String word) { assertTrue(!word.isBlank()); }
}
```

```text
org.junit.platform.commons.PreconditionViolationException: Method 'java.util.stream.Stream<java.lang.String> l0031.MethodSourceNonStaticTest.words()' must be static: local factory methods must be static unless the PER_CLASS @TestInstance lifecycle mode is used; external factory methods must always be static.
```

The message names the escape hatch itself: annotate the test class `@TestInstance(TestInstance.Lifecycle.PER_CLASS)` and the same non-static `words()` resolves and runs, verified at `Tests run: 3, Failures: 0`. `PER_CLASS` makes JUnit construct one test instance for the whole class instead of one per method, so a factory reached through that single instance no longer needs to exist independently of any instance. A factory method in a different class, referenced as `com.example.Words#words`, must always be `static`, `PER_CLASS` or not, since there is no instance of that other class to call it through.

### `@CsvSource`, the FastCSV switch, and a `#` that used to be unchangeable

JUnit 6.0.0 switched `@CsvSource` and `@CsvFileSource` to parse with the FastCSV library. A regression that shipped with that switch made `#` an unchangeable comment character; JUnit 6.1 added a `commentCharacter` attribute to both annotations to fix it. Verified against the current baseline, JUnit 6.1.3, the default still treats `#` as a comment marker in the multi-line `textBlock` form: three rows declared, one of them starting with `#`, produced only two test cases, the commented row silently missing from the count:

```java
@ParameterizedTest
@CsvSource(textBlock = """
    1, one
    #2, two
    3, three
    """)
void countRows(String number, String word) { ... }
```

```text
Tests run: 2, Failures: 2, Errors: 0, Skipped: 0
```

Set `commentCharacter = '~'` on the same annotation and all three rows come back, `Tests run: 3`, with the `#2` row present and its `#` preserved as data. Worth knowing separately: the same leading `#`, tried instead as one full row inside the array form, `@CsvSource({"#1, one", "2, two", "3, three"})`, was **not** treated as a comment; all three rows ran. Comment-line detection here applies to lines inside a `textBlock`, not to array elements that are each already a complete, isolated row. If a value your data legitimately contains starts with `#`, check which form you used and what it actually printed, rather than assuming the row is there.

Two more `@CsvSource` attributes worth knowing: `nullValues` names a placeholder string, such as `"N/A"`, that converts to an actual `null` rather than the literal text, verified to turn `"N/A"` into `null` while leaving `"present"` untouched on the same source. Quoting uses a single quote by default, so `'lemon, lime', 2` is one two-column row, `fruit` equal to the literal string `lemon, lime`, the comma inside the quotes never splitting the column, verified by printing both fields back out.

`useHeadersInDisplayName = true` folds the first declared row, treated as column headers, into the default display name instead of positional indices. With `input, expected` as that header row, the same three-case source reported, verified against the actual runner output:

```text
[1] input = "1", expected = "3"
[2] input = "2", expected = "6"
[3] input = "3", expected = "9"
```

### Implicit argument conversion, and what a bad one reports

Every value out of a source such as `@CsvSource` starts life as a `String`. JUnit converts it implicitly to whatever type the method parameter declares, which is how a CSV column becomes a `LocalDate` from [Lesson 20](0020-dates-and-times.md) or an enum constant from [Lesson 12](0012-enums.md) without a line of conversion code in the test:

```java
@ParameterizedTest
@CsvSource({"2024-01-01, 2024", "not-a-date, 2024"})
void yearOf(LocalDate date, int expectedYear) {
    assertEquals(expectedYear, date.getYear());
}
```

The first row converts cleanly. The second fails before the test body runs, reported as an **error**, not a failure, the tell that the problem is argument resolution rather than a wrong assertion:

```text
Tests run: 4, Failures: 0, Errors: 2, Skipped: 0
org.junit.jupiter.api.extension.ParameterResolutionException: Error converting parameter at index 0: Failed to convert String "not-a-date" to type java.time.LocalDate
Caused by: java.time.format.DateTimeParseException: Text 'not-a-date' could not be parsed at index 0
```

The same shape shows up converting to an enum, with the enum's own lookup failure as the root cause:

```text
org.junit.jupiter.api.extension.ParameterResolutionException: Error converting parameter at index 0: Failed to convert String "FUNDAY" to type java.time.DayOfWeek
Caused by: java.lang.IllegalArgumentException: No enum constant java.time.DayOfWeek.FUNDAY
```

`Tests run: N, Failures: X, Errors: Y` is worth reading precisely for this reason: failures are assertions that ran and disagreed, errors are everything that went wrong before or around one, including a conversion JUnit could not perform.

### Display names are what makes the failure report readable

By default, a parameterised test's display name is positional: `tripleOverFiveInputs(int, int)[3]`. The `name` attribute on `@ParameterizedTest` overrides that, with placeholders including `{index}` for the one-based case number and `{0}`, `{1}` and so on for each declared argument in order. Given `name = "{index}: triple({0}) should be {1}"` on the five-case triple test from the opening example, the actual rendered names JUnit's own runner reported were:

```text
1: triple("1") should be "3"
2: triple("2") should be "6"
3: triple("3") should be "9"
```

Notice the quotes around the numbers: `{0}` and `{1}` substitute the argument as it existed at substitution time, which for a `@CsvSource` case is the raw `String` before implicit conversion runs, not the `int` the method body receives. Design for that rather than being surprised by it, since a template assuming a numeric-looking placeholder can carry quote marks nobody asked for.

This is [Lesson 30](0030-assertions-that-name-the-failure.md)'s argument one level up: an assertion message names what failed inside one test, a display name names which test, out of several sharing one method body, failed at all. `tripleOverFiveInputs(int, int)[3] -- FAILURE!` still tells you a case number; `3: triple("3") should be "9"` tells you what that case claimed, without opening the source to find out.

### `@RepeatedTest` proves less than it looks like

```java
@RepeatedTest(3)
void repeatsThree() { assertEquals(4, 2 + 2); }
```

This runs three times, reported by JUnit's own default names as `repetition 1 of 3`, `repetition 2 of 3`, `repetition 3 of 3`, all three passing, verified. Running a deterministic test three times against the same fixed inputs proves nothing that running it once did not: the JVM does not roll dice on `2 + 2`, and a passing repetition only shows the machine did not corrupt itself between runs. `@RepeatedTest` earns its place when either the input genuinely varies between repetitions, drawn from `RepetitionInfo` or something external such as a clock, or the point is explicitly to hunt for flakiness, a race condition from [Lesson 23](0023-the-memory-model.md) that only shows up on some interleavings. Outside those two reasons, a passing `@RepeatedTest` is decoration, not evidence.

### `@TestFactory` and dynamic tests: the case list decided at run time

`@ParameterizedTest` needs its source declared in the annotation or provided by a method whose return value is known before the test starts; the case count is fixed once discovery finishes. `@TestFactory` instead returns a `Stream`, `Collection` or `Iterable` of `DynamicTest`, generated by ordinary code, and the number and content of the cases can depend on anything available at run time, a directory listing, a database query, or here, a `List` built inline:

```java
@TestFactory
Stream<DynamicTest> dynamicCasesFromRuntimeList() {
    List<Integer> inputs = List.of(1, 2, 3, 4, 5);
    return inputs.stream()
        .map(n -> dynamicTest("triple(" + n + ")", () -> assertEquals(n * 3, Tripler.triple(n))));
}
```

Run alongside the `@RepeatedTest` above in one class, verified `Tests run: 8`, three repetitions plus five dynamic cases, with `triple(3)` and `triple(5)` reported as failures by the exact names given to `dynamicTest`, and the other three passing. What `@TestFactory` buys over `@ParameterizedTest` is that run-time freedom; what it costs is that the case list is one method's worth of ordinary Java rather than a declarative annotation another tool could statically inspect.

### `@Nested` classes for shared context

An inner, non-static class annotated `@Nested` groups tests that share a setup context defined in the enclosing class, letting several related scenarios reuse one fixture without repeating it per test method. JUnit 6 changed two things about how nested classes execute: `@Nested` classes now run in a deterministic order rather than whatever order the JVM happens to report them in, and a `@TestMethodOrder` declared on the enclosing class is now inherited by every `@Nested` class inside it, no longer needing repeating on each one to take effect there too.

### When not to parameterise

Parameterising earns its keep when several cases differ only in their **data**: same setup, same call, same assertion, different numbers in and out, exactly the `Tripler` example throughout this lesson. It stops earning its keep once the cases differ in what they **assert** rather than what they feed in. A test that checks "negative input throws, zero returns the identity, positive input triples it" is three different claims about three different behaviours, and forcing that into one parameterised method means smuggling a conditional into the test body to decide which assertion applies to which row, an `if` that exists only to work around the annotation. Three separate `@Test` methods, each named for the behaviour it checks, read better and fail more specifically than one parameterised method with a branch hidden inside it.

## Practice

1. ▢ Predict `Tests run` and `Failures` for a `@ParameterizedTest` fed by `@ValueSource(ints = {2, 4, 6, 8})` where the method under test doubles the input correctly for every value, then run it.

<details markdown="1"><summary>Check</summary>

`Tests run: 4, Failures: 0`. Every declared value becomes its own passing test; a plain `@Test` calling the method four times in a row could prove the same thing here, since none of the four inputs is expected to fail.

</details>

2. ▢ Predict how many cases `@CsvSource(textBlock = "...")` produces for a three-row block where the second row's first cell is `#skip`, with no `commentCharacter` set, then run it and check against the verified behaviour in this lesson.

<details markdown="1"><summary>Hint</summary>

The default comment character in the `textBlock` form is `#`, and a comment line does not become a case at all, it is simply absent from the count.

</details>

<details markdown="1"><summary>Check</summary>

Two cases, not three. The `#skip` row is silently dropped by the default comment handling, and nothing in the Surefire summary announces a missing row; the case count is just smaller than the source. Setting `commentCharacter` to something other than `#` brings the row back.

</details>

3. ▢ A `@ParameterizedTest` method takes a `java.time.DayOfWeek` parameter fed by a `@CsvSource` whose column contains the literal text `Monday`. Predict whether this test errors, and if so, why, given that `DayOfWeek.MONDAY` is a real constant.

<details markdown="1"><summary>Check</summary>

It errors, with a `ParameterResolutionException` wrapping a `java.lang.IllegalArgumentException: No enum constant java.time.DayOfWeek.Monday`. Implicit conversion to an enum resolves by exact declared constant name, which for `DayOfWeek` is all upper case, `MONDAY`; the mixed-case text does not match, and there is no case-insensitive fallback built into the conversion.

</details>

4. ▢ Two teams each write "the same" test differently. Team A: one `@ParameterizedTest` with a `name` of `"case {index}"` fed by ten CSV rows. Team B: the same ten rows, with a `name` of `"{0} rounds to {1}"`. Both catch the same bug. What is different about the two teams' experience of the failing run, and why?

<details markdown="1"><summary>Check</summary>

Both suites go red on the same case, but team A's report reads `case 7 -- FAILURE!` and team B's reads something like `4.5 rounds to 5 -- FAILURE!`. Team A has to open the source and count down to row seven to find out what was claimed; team B can tell what failed from the report alone. The bug is caught either way, both being genuinely parameterised; the difference is entirely how much the display name tells the reader before they go looking further.

</details>

5. ▢ A test needs to check that a `Discount` calculator returns 0 for a negative percentage, echoes the input back for a percentage between 0 and 100, and caps at 100 for anything above. Would you write this as one `@ParameterizedTest`, or as three plain `@Test` methods, and why?

<details markdown="1"><summary>Check</summary>

Three plain `@Test` methods, one per behaviour: `negativePercentageReturnsZero`, `midRangePercentageIsUnchanged`, `percentageAboveHundredIsCapped`. Each is a different claim about the calculator, not the same claim checked against different data, and parameterising would mean one method branching internally on which assertion applies to which row, the conditional-inside-the-test-body smell this lesson names as the reason not to parameterise here.

</details>

## Real-world reps

- [ ] Find a test in your own code that loops over an array or a list of cases inside one `@Test` method, and check whether an assertion partway through the loop would currently hide every case after it.
- [ ] Take one `@CsvSource` or `@CsvFileSource` in code you maintain and check its `name` attribute, or lack of one, against whether the default positional display name would tell you anything useful if it failed at 2 a.m.
- [ ] Search your test suite for any `@RepeatedTest` and check, for each one, whether its input actually varies between repetitions or whether it is running a deterministic assertion several times for no additional evidence.
- [ ] If any test in your codebase reads CSV-shaped data containing a literal `#`, whether from `@CsvSource` or from a real CSV file elsewhere, check whether that `#` is being silently swallowed as a comment marker.
- [ ] Tomorrow: pick the parameterised test in your suite with the least informative `name`, and give it a `name` template built from its actual arguments instead of the default positional one.

## Going further

- [Repeated Tests, JUnit User Guide](https://docs.junit.org/current/writing-tests/repeated-tests.html): when a repetition is decoration and when it is evidence
- [Dynamic Tests, JUnit User Guide](https://docs.junit.org/current/writing-tests/dynamic-tests.html): generating the case list itself at run time with `@TestFactory`
- [Nested Tests, JUnit User Guide](https://docs.junit.org/current/writing-tests/nested-tests.html): grouping tests that share a fixture
- [JUnit 6.1.3 release notes](https://docs.junit.org/6.1.3/release-notes/): the `commentCharacter` fix and the rest of what changed in 6.1
- [Testing and build](../reference/testing-and-build.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
