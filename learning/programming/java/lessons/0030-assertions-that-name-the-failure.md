---
title: 30. Assertions That Name the Failure
description: A failing test is a bug report, and the assertion you chose decides how good a report it is
type: lesson
---

# Lesson 30. Assertions That Name the Failure

**Mission link:** Owning a service means a failing test is the incident report you get before a user does, and the assertion you picked decides whether it says what broke.
**Primary source:** [`Assertions`, JUnit 6.1.3 API](https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html)
**Prerequisites:** [Lesson 29](0029-your-first-test.md), [Lesson 2](0002-identity-and-equality.md)

## Warm-up

1. ▢ `mvn test` finishes and prints a line like `Tests run: 4, Failures: 1, Errors: 0, Skipped: 0`. What is the difference between a test counted as a Failure and one counted as an Error?

<details markdown="1"><summary>Check</summary>

A Failure means an assertion ran and reported that its expectation did not hold, an `AssertionError` thrown on purpose by an `assert*` method. An Error means the test method threw something else entirely, an exception nobody wrote an assertion for, propagating uncaught. Both fail the test, but they are counted separately, and that split reappears later in a place that looks like it shouldn't matter and does.

</details>

2. ▢ Two `Point` objects hold the same `x` and `y`, `Point` overrides `equals`, and they are two separate objects. What does `a == b` give, and what does `a.equals(b)` give?

<details markdown="1"><summary>Check</summary>

`a == b` is `false`, since `==` between references compares identity and these are two distinct objects. `a.equals(b)` is `true`, since `Point` defines equality by content. This lesson has an assertion for each question, and picking the wrong one is a bug a test can pass while hiding.

</details>

## Know this

### `assertTrue(x.equals(y))` versus `assertEquals(x, y)`: the same bug, two different bug reports

Both of these fail on the same mismatch. Here is the code for each, and the exact text each one printed:

```java
record Point(int x, int y) {}

Point expected = new Point(1, 2);
Point actual = new Point(1, 3);

assertTrue(expected.equals(actual));
```

```text
org.opentest4j.AssertionFailedError: expected: <true> but was: <false>
	at org.junit.jupiter.api.Assertions.assertTrue(Assertions.java:190)
	at demo.EqualsVsEqualsTest.withAssertTrue(EqualsVsEqualsTest.java:16)
```

```java
assertEquals(expected, actual);
```

```text
org.opentest4j.AssertionFailedError: expected: <Point[x=1, y=2]> but was: <Point[x=1, y=3]>
	at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:1199)
	at demo.EqualsVsEqualsTest.withAssertEquals(EqualsVsEqualsTest.java:23)
```

Both are genuinely correct assertions on the same two objects: `expected.equals(actual)` really is `false`, so `assertTrue` on it really does fail. But the first message can only say a `boolean` was not `true`, since the two `Point`s are already collapsed into one bit and thrown away by the time `assertTrue` runs. The second shows what the records actually were, since `assertEquals` still has both operands, and the record's own `toString` (lesson 8) renders them for free: `Point[x=1, y=3]`.

That is this lesson's whole argument in miniature: the assertion you choose decides what the next reader gets to see. `assertTrue` on a boolean-returning expression compiles fine and reports almost nothing useful. Whenever a comparison is smuggled into a `boolean`, treat it as a smell: `assertTrue(a.equals(b))` should almost always be `assertEquals(b, a)`.

### `assertThrows`: it returns the exception, so you keep asserting

`assertThrows` does not just detect that something was thrown, it captures it and hands it back, which matters for lesson 15's exception chaining: message, type and cause are separate facts, and only the returned exception lets you check all three.

```java
static void placeOrder() {
    throw new IllegalStateException("bad state", new RuntimeException("root cause"));
}

IllegalStateException ex = assertThrows(IllegalStateException.class, AssertThrowsTest::placeOrder);
assertEquals("bad state", ex.getMessage());
assertInstanceOf(RuntimeException.class, ex.getCause());
assertEquals("root cause", ex.getCause().getMessage());
```

That passes cleanly, `Tests run: 1, Failures: 0`. Two failure shapes read very differently.

Nothing thrown:

```text
org.opentest4j.AssertionFailedError: Expected java.lang.IllegalArgumentException to be thrown, but nothing was thrown.
	at org.junit.jupiter.api.Assertions.assertThrows(Assertions.java:3234)
	at demo.AssertThrowsTest.nothingThrown(AssertThrowsTest.java:20)
```

The wrong type thrown, the code under test throwing `IllegalStateException` while the assertion expects `IllegalArgumentException`:

```text
org.opentest4j.AssertionFailedError: Unexpected exception type thrown, expected: <java.lang.IllegalArgumentException> but was: <java.lang.IllegalStateException>
	at org.junit.jupiter.api.Assertions.assertThrows(Assertions.java:3234)
	at demo.AssertThrowsTest.wrongTypeThrown(AssertThrowsTest.java:25)
Caused by: java.lang.IllegalStateException: bad state
	at demo.AssertThrowsTest.throwsIllegalState(AssertThrowsTest.java:15)
```

That `Caused by:` line does exactly the job lesson 15 described: the exception that actually happened is attached as the cause rather than discarded, so a reader scrolling past the first line still sees what was really thrown. That is the opposite of the dropped-cause mistake that lesson warned about, done correctly by default on every call to `assertThrows`.

### `assertDoesNotThrow`: rarely necessary, and the one place it earns its keep

An uncaught exception already fails a test, so `assertDoesNotThrow(() -> parse(input))` looks like ceremony around something the JVM does for free. Running both side by side shows the difference is real but narrow:

```java
@Test void wrapped()   { assertDoesNotThrow(() -> { throw new IllegalStateException("boom"); }); }
@Test void unwrapped()  { throw new IllegalStateException("boom"); }
```

```text
[ERROR] demo.DoesNotThrowTest.unwrapped -- Time elapsed: 0.025 s <<< ERROR!
java.lang.IllegalStateException: boom
	at demo.DoesNotThrowTest.unwrapped(DoesNotThrowTest.java:18)

[ERROR] demo.DoesNotThrowTest.wrapped -- Time elapsed: 0.020 s <<< FAILURE!
org.opentest4j.AssertionFailedError: Unexpected exception thrown: java.lang.IllegalStateException: boom
	at org.junit.jupiter.api.Assertions.assertDoesNotThrow(Assertions.java:3366)
	at demo.DoesNotThrowTest.wrapped(DoesNotThrowTest.java:11)
Caused by: java.lang.IllegalStateException: boom
```

Both fail, and the underlying exception is visible either way. The measured difference is the one the warm-up flagged: the `Tests run` summary counts `unwrapped` as an **Error** and `wrapped` as a **Failure**, and the wrapped message says in words what happened rather than leaving the reader to infer it from a bare trace, neither a strong reason to reach for `assertDoesNotThrow` everywhere.

The genuine reason is a different overload: it also accepts a `ThrowingSupplier<T>` and returns the value produced, so one line both asserts "this must not throw" and hands you the result: `int parsed = assertDoesNotThrow(() -> Integer.parseInt("42"));` passed, with `parsed` ready for `assertEquals(42, parsed)` next. Write it for the returned value; skip it otherwise, since an uncaught exception already fails the test.

### `assertAll`: not a `try`/`catch`, and it collects more than assertion failures

The instinct to reach for `try`/`catch` here is wrong in a specific way: a `catch` block stops the moment one thing throws, exactly the behaviour a grouped check should not have. `assertAll` runs every executable to completion regardless of what earlier ones did, then reports everything that went wrong in one object.

```java
record Point(int x, int y) {}
Point actual = new Point(9, 9);

assertAll(
    () -> assertEquals(1, actual.x(), "x mismatch"),
    () -> assertEquals(2, actual.y(), "y mismatch")
);
```

```text
org.opentest4j.MultipleFailuresError:
Multiple Failures (2 failures)
	org.opentest4j.AssertionFailedError: x mismatch ==> expected: <1> but was: <9>
	org.opentest4j.AssertionFailedError: y mismatch ==> expected: <2> but was: <9>
	at org.junit.jupiter.api.Assertions.assertAll(Assertions.java:3048)
	at demo.AssertAllTest.groupedAssertions(AssertAllTest.java:15)
	Suppressed: org.opentest4j.AssertionFailedError: x mismatch ==> expected: <1> but was: <9>
		... 2 more
	Suppressed: org.opentest4j.AssertionFailedError: y mismatch ==> expected: <2> but was: <9>
		... 2 more
```

Both mismatches are named, in one report, from one run. Sequential `assertEquals` calls on the same object would stop at the first failure, hiding the second until the first is fixed and rerun, one edit-rerun cycle per field. Separate test methods instead would fragment one conceptual check, "is this `Point` correct", into several rows in the summary, and a reviewer sees several red lines rather than one that already names which fields are wrong.

Worth verifying: `assertAll` catches anything any executable throws, not only its own `AssertionFailedError`s. Replacing one lambda above with a method that throws a raw `IllegalStateException` still produces `Multiple Failures (2 failures)`, listing it alongside the assertion failure, both collected. So wrapping a call in `assertDoesNotThrow` purely so `assertAll` "keeps going" is unnecessary: it already does, for any `Throwable`.

### Message suppliers: the lazy form exists because building a message can cost something

`assertEquals` has an overload taking a `String` and one taking a `Supplier<String>`. They read almost identically at the call site and behave completely differently when the assertion passes.

```java
static int calls = 0;
static String sideEffect(String label) { calls++; return label + " message built"; }

calls = 0;
assertEquals(1, 1, sideEffect("eager"));            // String argument
System.out.println("eager calls: " + calls);

calls = 0;
assertEquals(1, 1, () -> sideEffect("lazy"));       // Supplier<String> argument
System.out.println("lazy calls: " + calls);
```

```text
eager calls after a passing assertion: 1
lazy calls after a passing assertion:  0
```

Observed on a passing assertion: the eager form always evaluates its argument, since Java evaluates arguments before the call happens. The lazy form evaluates nothing unless the assertion fails, since the supplier is only invoked from the failure path. For a literal this is invisible; for a message built from formatting a large collection, the eager form pays that cost on every passing test forever, and the lazy form pays it only when something is already wrong. Reach for `() -> expensive()` once building the message costs more than a concatenation.

### `assertEquals` on floating point, and why exact comparison is the wrong question

Lesson 2 already established that `0.1 + 0.2 == 0.3` is `false`, because binary floating point cannot represent `0.1` or `0.2` exactly. The same fact reappears here as a test failure:

```java
double result = 0.1 + 0.2;
assertEquals(0.3, result);
```

```text
org.opentest4j.AssertionFailedError: expected: <0.3> but was: <0.30000000000000004>
	at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:935)
```

The assertion is not lying and the arithmetic is not broken: `0.30000000000000004` really is what that addition produces, bit for bit. The mistake is the question: "are these bit-identical" is almost never what a test needs to know, "is this close enough" is, and that is what the three-argument overload asks instead: `assertEquals(0.3, result, 0.0001)` passed cleanly. `delta` is the largest difference the two values may have and still count as equal. Pick a delta meaningful for the quantity measured, a cent for money held as a `double` (`BigDecimal` is the better fix there), not an arbitrarily tiny number chosen just to make the assertion pass.

### `assertSame` versus `assertEquals`: the warm-up's question, as an assertion

`assertSame` is `==` wearing a test framework's clothes: identity, the same object, not equal content. `assertEquals` calls `.equals`. The warm-up's two `Point`s land here directly.

```java
Point a = new Point(1, 2);
Point b = new Point(1, 2);
assertSame(a, b);
```

```text
org.opentest4j.AssertionFailedError: expected: demo.AssertSameTest$Point@19e7a160<Point[x=1, y=2]> but was: demo.AssertSameTest$Point@16b2bb0c<Point[x=1, y=2]>
	at org.junit.jupiter.api.Assertions.assertSame(Assertions.java:2962)
```

The message prints both the identity hash, `@19e7a160` against `@16b2bb0c`, proof these are two objects, and the content, `Point[x=1, y=2]`, identical in both: same content, different objects, and the message says exactly that. Writing `assertSame` here would be a mistake in the test's intent, the same way lesson 2 flagged `==` on freshly constructed strings as a bug rather than a style choice. It belongs where identity is genuinely the question, a cache that must return the exact instance it stored, a builder that must return `this` for chaining. For comparing values by content, `assertEquals` is the correct tool.

### `assertArrayEquals`, `assertIterableEquals`, `assertLinesMatch`: three different shapes of "compare these collections"

`assertArrayEquals` compares arrays element by element, recursing into nested arrays, naming the first diverging index:

```java
int[] expected = {1, 2, 3};
int[] actual = {1, 9, 3};
assertArrayEquals(expected, actual);
```

```text
org.opentest4j.AssertionFailedError: array contents differ at index [1], expected: <2> but was: <9>
```

`assertIterableEquals` does the same for anything implementing `Iterable`, comparing elements pairwise in order, staying legible on records because it delegates per-element printing to their `toString`:

```java
List<Point> expected = List.of(new Point(1,1), new Point(2,2), new Point(3,3));
List<Point> actual   = List.of(new Point(1,1), new Point(2,9), new Point(3,3));
assertIterableEquals(expected, actual);
```

```text
org.opentest4j.AssertionFailedError: iterable contents differ at index [1], expected: <Point[x=2, y=2]> but was: <Point[x=2, y=9]>
```

`assertLinesMatch` compares two lists of `String` as lines of text, and beyond plain equality it understands fast-forward markers for skipping variable lines and lets each expected line be a regular expression, fitting rendered output where a timestamp or an id varies between runs:

```java
List<String> expected = List.of("first", "second", "third");
List<String> actual   = List.of("first", "SECOND", "third");
assertLinesMatch(expected, actual);
```

```text
org.opentest4j.AssertionFailedError:
expected line #2 doesn't match actual line #2
	expected: `second`
	  actual: `SECOND`
```

### `assertTimeout` versus `assertTimeoutPreemptively`: same budget, different thread

Both take a `Duration` and fail if the callback overruns it. The API documentation states the difference directly, worth demonstrating rather than trusting: `assertTimeoutPreemptively` "execute[s] the provided callback in a different thread than that of the calling code", while `assertTimeout` runs it on the calling thread and just measures how long it took. Printing the thread name from inside each confirms it:

```java
@Test void withAssertTimeout() {
    assertTimeout(Duration.ofSeconds(1), () ->
        System.out.println("body on: " + Thread.currentThread()));
}

@Test void withAssertTimeoutPreemptively() {
    assertTimeoutPreemptively(Duration.ofSeconds(1), () ->
        System.out.println("body on: " + Thread.currentThread()));
}
```

```text
test method running on:      Thread[#3,main,5,main]
assertTimeout body on:       Thread[#3,main,5,main]

test method running on:      Thread[#3,main,5,main]
assertTimeoutPreemptively on: Thread[#29,junit-timeout-thread-1,5,main]
```

`assertTimeout`'s body ran on `Thread[#3,main]`, the same thread as the test method. `assertTimeoutPreemptively`'s body ran on `Thread[#29,junit-timeout-thread-1]`, a thread JUnit created purely for that callback. This is exactly what stage 4 spent a lesson on: anything thread-confined, a `ThreadLocal`, a resource contractually touched from one thread only, misbehaves under `assertTimeoutPreemptively` in ways it never would under `assertTimeout`. The documentation names the case: a framework binding transaction state via a `ThreadLocal` will not roll back correctly when the code ran on JUnit's timeout thread instead. Prefer `assertTimeout` by default; reach for `assertTimeoutPreemptively` only when the test must not wait past the deadline and the code does not depend on thread identity.

### `fail()`: for the branch that should be unreachable

`fail()` and `fail(String)` unconditionally fail the test with the given message.

```text
org.opentest4j.AssertionFailedError: not implemented yet
	at org.junit.jupiter.api.Assertions.fail(Assertions.java:142)
```

Its legitimate uses are narrow: marking a test body not yet written, so the gap is a named failure rather than an accidental green test, and the line after a manual `try`/`catch` where reaching it means an expected exception never came. Outside those shapes, `fail()` usually stands in for an assertion that would have said more.

### AssertJ, briefly: what a fluent library actually buys

`org.assertj:assertj-core:3.27.7` is the current stable release; `4.0.0-M1`, published after it, is a milestone, not a stable line, so pin `3.27.7`. AssertJ replaces the differently-named `assertX` calls with one entry point, `assertThat`, that adapts to the value's type and chains further checks fluently:

```java
List<Integer> actual = List.of(1, 2, 4);
assertThat(actual).containsExactly(1, 2, 3);
```

```text
org.opentest4j.AssertionFailedError:

Expecting actual:
  [1, 2, 4]
to contain exactly (and in same order):
  [1, 2, 3]
but some elements were not found:
  [3]
and others were not expected:
  [4]
```

That message names both the missing and the unexpected element, more than `assertIterableEquals`'s single differing index gives when more than one position is wrong. The other gain is fewer names to remember: instead of choosing among `assertEquals`, `assertArrayEquals`, `assertIterableEquals` and `assertSame` by the shape of the data, `assertThat` is the one call, and shape-specific behaviour lives in the chained method. Better messages on collections, one starting point instead of several: that is the whole case for it. Whether the extra dependency is worth it is a call this lesson leaves to you.

## Practice

1. ▢ Predict the failure text for `assertTrue(order.status().equals(Status.SHIPPED))` when the status is actually `Status.CANCELLED`. Then predict it for `assertEquals(Status.SHIPPED, order.status())`.

<details markdown="1"><summary>Check</summary>

`assertTrue` reports `expected: <true> but was: <false>` and nothing else, since the comparison was already collapsed to a boolean before the assertion saw it. `assertEquals` reports the two constants by name, `expected: <SHIPPED> but was: <CANCELLED>`, since it still has both operands. Same mismatch, and only one message says which status came back.

</details>

2. ▢ An `assertAll` block groups three checks on one `Invoice`, and two of the three fail. Predict how many failures the header reports, and whether the passing check appears anywhere in the output.

<details markdown="1"><summary>Check</summary>

`Multiple Failures (2 failures)`, listing only the two that failed. The passing check still runs, but a passing assertion has nothing to report, so it leaves no trace in the output.

</details>

3. ▢ A test calls `assertThrows(IllegalArgumentException.class, () -> repository.save(order))`, and `save` actually throws `NullPointerException` because a required field was `null`. Predict what the failure message shows about the `NullPointerException`, without running it.

<details markdown="1"><summary>Check</summary>

`Unexpected exception type thrown, expected: <java.lang.IllegalArgumentException> but was: <java.lang.NullPointerException>`, with the `NullPointerException` itself attached as the cause, `Caused by: java.lang.NullPointerException: ...`. Nothing about the real exception is lost; it is just not the one that was asked for.

</details>

4. ▢ `assertEquals(1, 1, buildDiagnosticReport())` and `assertEquals(1, 1, () -> buildDiagnosticReport())` sit in a test where `buildDiagnosticReport()` is expensive and the assertion always passes. Predict whether `buildDiagnosticReport()` runs, for each form.

<details markdown="1"><summary>Check</summary>

The plain `String` form always calls `buildDiagnosticReport()`, since Java evaluates arguments before the call regardless of whether the message is needed. The `Supplier<String>` form calls it zero times, since it is only invoked from the failure path. Measured earlier: one call for the eager form, none for the lazy one, on a passing assertion.

</details>

5. ▢ `ConnectionPool.borrow()` is documented to return the exact same `Connection` instance on a second call if the first was never returned. Which assertion verifies that, `assertEquals` or `assertSame`, and why would the other one pass even if the contract were broken by returning an equal-but-different `Connection`?

<details markdown="1"><summary>Check</summary>

`assertSame`. The contract is about identity, not content, so `assertEquals` would happily pass on two distinct but equal `Connection` objects, the exact bug this test exists to catch. The warm-up's question again: `assertEquals` calls `.equals`, `assertSame` checks `==`, and picking the wrong one means the test cannot fail even when the pool is broken.

</details>

6. ▢ A test bounds a database call to two seconds, and the call's transaction state is bound to the calling thread via a `ThreadLocal`. Which timeout assertion is safe, and what goes wrong with the other one?

<details markdown="1"><summary>Check</summary>

`assertTimeout` is safe, since it runs the call on the same thread the test runs on, keeping the `ThreadLocal` transaction state bound to the thread that set it up. `assertTimeoutPreemptively` runs the call on a separate thread, so the lookup sees nothing, or the wrong thing, and the transaction does not roll back as expected. This is the documented Spring testing example, and exactly why stage 4's thread-confinement material matters here.

</details>

## Real-world reps

- [ ] Find an `assertTrue(x.equals(y))` or `assertTrue(x == y)`, rewrite it as `assertEquals` or `assertSame`, break the value on purpose, and compare the two failure messages.
- [ ] Find a test with several sequential assertions on one object, rewrite it as a single `assertAll`, then break two checks at once and read the `MultipleFailuresError`.
- [ ] Find an `assertThrows` call that only checks the exception's type and add an assertion on its message, using the value the call already returns.
- [ ] Search for an `assertEquals` on two `double` or `float` values with no `delta`, and decide whether it passes because the values are exact or because nobody has changed the calculation yet.
- [ ] Tomorrow: before fixing the next test you break, read its failure message first and ask whether it already told you what went wrong.

## Going further

- [`Assertions`, JUnit 6.1.3 API](https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html): every assertion method and overload, including ones this lesson had no room for
- [`MultipleFailuresError`, opentest4j 1.3.0](https://ota4j-team.github.io/opentest4j/docs/1.3.0/api/org/opentest4j/MultipleFailuresError.html): what `assertAll` actually throws, and how suppressed exceptions attach
- [AssertJ Core assertions guide](https://assertj.github.io/doc/#assertj-core-assertions-guide): the fluent style at more length than this lesson's one subsection
- [Testing and build](../reference/testing-and-build.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
