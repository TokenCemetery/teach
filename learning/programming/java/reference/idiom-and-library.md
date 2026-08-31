---
title: Idiom and the library
description: The library decisions a reviewer notices, and the traps that throw where nobody looks
type: reference
---

# Idiom and the library

Lookup sheet for stage 3. The question it exists to answer: **which library call is the right one, and where does this one throw?**

## Exceptions

| | Checked (`Exception`, not a `RuntimeException`) | Unchecked (`RuntimeException`) |
|---|---|---|
| Compiler | forces every caller to catch it or declare `throws` | never forces anyone to acknowledge it |
| The test | a reasonable caller has a real next step other than giving up, retry, fall back, ask for something different | the caller already made a programming mistake; there was never a next step but fixing the caller |
| Example | `IOException` from a file read | `IllegalArgumentException` from a negative constructor argument |

`Error` sits outside this decision entirely: `OutOfMemoryError` and `StackOverflowError` mean the JVM itself is in a state the program did not cause, and the right response is almost never a catch block, since there is nowhere sane to continue from.

| Clause | Guarantees |
|---|---|
| `try` | nothing on its own; marks the region a `catch` or `finally` can react to |
| `catch` | runs if a thrown exception matches its type; under multi-catch (Java 7) the caught variable is typed as the nearest common supertype the listed types share |
| `finally` | always runs after the `try` and whichever `catch` matched, whether the block completed normally, returned, or threw; an abrupt completion written inside it, `return`, `break`, `continue`, or another `throw`, overrides whatever the `try` or `catch` was already doing |
| try-with-resources (Java 7) | closes every declared `AutoCloseable` resource when the block exits by any means, in reverse of declaration order |

| | try-with-resources | hand-written `finally` |
|---|---|---|
| Several resources | closes in reverse of declaration order | whatever the code writes, easy to get backwards |
| Body throws, and `close` also throws | the body's exception propagates; `close`'s exception attaches to it as a **suppressed exception**, retrievable from `getSuppressed()` | `close`'s exception replaces the body's outright; the original is gone with no trace anywhere |
| Requires | the resource implement `AutoCloseable` | nothing, which is also why it is easy to get wrong |

Never do these, each for the reason stated rather than as a style objection:

| Never | Cost |
|---|---|
| `catch (Throwable t)` | catches `Error` along with everything else, including `OutOfMemoryError` and `StackOverflowError`; the program keeps running against a corrupted or nearly exhausted heap, or a blown stack, instead of failing where the JVM itself gave up |
| Swallowing, `catch (Exception e) {}` | the failure disappears with no log line and no metric; the next person to see it is a confused user |
| Spending an exception on an expected, common condition (end of input, a cache miss, a failed validation) | pays for building a full stack trace for something a returned value or an `Optional` would say more cheaply and more clearly |
| `return`, `break` or `continue` inside `finally` | discards whatever the `try` or `catch` block was already doing, including an exception already in flight, silently; the compiler's own `-Xlint:finally` names the shape, `finally clause cannot complete normally` |
| Dropping the cause when rethrowing, `throw new OrderException("msg")` instead of `throw new OrderException("msg", e)` | the trace loses its `Caused by:` section entirely; whoever is on call reconstructs the failure from a message string alone |

## `Optional`

| Method | Behaviour |
|---|---|
| `Optional.of(value)` | wraps a non-null value; throws `NullPointerException` immediately, no message, if `value` is `null` |
| `Optional.ofNullable(value)` | wraps `value`, or returns `Optional.empty()` if `value` is `null` |
| `Optional.empty()` | the same shared empty instance every call |
| `isPresent()` plus `get()` | a `null` check wearing a costume: still branches on presence, still calls a method that throws if the branch is wrong. Reach for this pair only when every alternative below genuinely fails to fit |
| `ifPresent(consumer)` | runs the consumer only when a value exists, and never calls `get()` |
| `ifPresentOrElse(consumer, runnable)` | both branches at once, one for presence and one for absence |
| `map(fn)` | transforms the value when present; if `fn` already returns `Optional`, the result is an `Optional` inside an `Optional` |
| `flatMap(fn)` | transforms the value with a function that itself returns `Optional`, without the double wrapping |
| `filter(predicate)` | turns a present `Optional` empty when the predicate fails; never throws on a failed test |
| `or(supplier)` | supplies a fallback `Optional`, evaluated lazily |
| `stream()` | zero or one elements, for folding an absence into a larger pipeline |
| `orElse(value)` | **eager**: evaluates `value` unconditionally, before checking whether the `Optional` holds one |
| `orElseGet(supplier)` | **lazy**: invokes the supplier only when the `Optional` is empty |
| `orElseThrow(supplier)` | throws whatever the supplier builds |
| `orElseThrow()` | throws the fixed `NoSuchElementException: No value present` |

`orElse` against `orElseGet` is the eager-argument trap: passing a literal or an already-computed value to `orElse` costs nothing extra, but passing a call that queries a database, builds a collection, or does anything else with a real cost pays that cost on every invocation, present value or not, unless it is behind `orElseGet` instead.

Four places `Optional` does not belong:

| Place | Why not |
|---|---|
| A field | the field itself can still be `null`, so a field of type `Optional<T>` has three states instead of two, and the type bought nothing |
| A parameter | a caller can hand over a bare `null` instead of `Optional.empty()`, reintroducing the exact `null` check the parameter existed to remove, only now buried inside the method |
| The element type of a collection | a `List<Optional<T>>` makes every consumer handle absence twice, once for the element and once for the list already being able to be empty |
| Anything serialised | `Optional` does not implement `Serializable`; writing one throws `java.io.NotSerializableException: java.util.Optional`, and `instanceof Serializable` against a variable of static type `Optional<T>` does not even compile |

A method whose success case is a collection returns an empty collection for "none found", not `Optional<Collection<T>>`: the collection can already say "zero results" by being empty, and wrapping it forces every caller to unwrap twice.

## Streams

A pipeline has exactly one **source** (a collection, an array, a generator, a range), any number of **intermediate operations**, each returning a new stream, and exactly one **terminal operation**, which produces a result or a side effect instead of another stream. Nothing runs until the terminal operation is called.

| Operation | Kind | Short-circuits |
|---|---|---|
| `limit`, `takeWhile` | intermediate | yes |
| `findFirst`, `findAny`, `anyMatch`, `allMatch`, `noneMatch` | terminal | yes |
| `map`, `filter`, `flatMap`, `distinct`, `dropWhile`, `peek` | intermediate | no, but pass each element downstream without buffering the rest |
| `sorted` | intermediate | no; it must pull the entire upstream through before releasing even the first element, since it cannot know the correct first element until it has seen the last one |
| `forEach`, `toList`, `collect`, `reduce` | terminal | no, must consume everything |
| `count` | terminal | no in general, but skips the whole pipeline body when the stream is unfiltered and its size is already known |

`findFirst` always returns the first element in encounter order; `findAny` returns any matching element and is free to return whichever one it finds fastest. The two behave identically on a plain sequential stream, which is why the difference is easy to miss: `findAny` only diverges under parallel execution or an unordered source, and repeated runs of unchanged sequential code cannot upgrade a permission the contract never granted. Prefer `findFirst` when order matters to the reader, `findAny` when it genuinely does not, as a signal of intent.

A `Stream` runs once. Calling a second terminal operation on the same instance throws:

```text
java.lang.IllegalStateException: stream has already been operated upon or closed
```

If the same elements are needed twice, build the pipeline again from the source, or terminate once into a collection and reuse that.

Reach for a `for` loop instead of a stream once the body needs more than one thing at a time: several independent accumulators, an early exit that compares two elements, a checked exception with no clean path through a lambda, or logic that reads better as a sequence of statements than as a chain of named operations. The test is whether the stream version reads faster than the loop it replaced; if it does not, write the loop.

## Collectors

| Collector | Result | Notes |
|---|---|---|
| `Collectors.toList()` | `ArrayList` (unspecified) | mutable; no promise about the concrete type |
| `Stream.toList()` | unmodifiable list | not a `Collectors` method; final in Java 16 |
| `Collectors.toUnmodifiableList()` | unmodifiable list | Java 10; throws on a `null` element |
| `Collectors.toSet()` | `HashSet` (unspecified) | no iteration-order guarantee |
| `Collectors.toUnmodifiableSet()` | unmodifiable set | Java 10 |
| `Collectors.toMap(keyFn, valFn)` | `HashMap` (unspecified) | throws on a duplicate key or a `null` value |
| `Collectors.toMap(keyFn, valFn, merge)` | `HashMap` | duplicate keys resolved by `merge`; a `null` value still throws, since `merge` never runs for a key that has not collided |
| `Collectors.toMap(keyFn, valFn, merge, factory)` | whatever `factory` builds | e.g. `TreeMap::new` for a sorted result |
| `Collectors.groupingBy(classifier)` | `HashMap` of `ArrayList` (unspecified) | add a downstream collector as a second argument to do more than bucket into a list |
| `Collectors.groupingBy(classifier, factory, downstream)` | whatever `factory` builds | three-argument form, map factory in the middle |
| `Collectors.partitioningBy(predicate)` | always exactly two entries, keyed `true` and `false` | concrete type is an internal class; program against `Map<Boolean, List<T>>` only |
| `Collectors.joining(delim, prefix, suffix)` | `String` | the one-argument form takes only the delimiter |
| `Collectors.counting()`, `summingInt`, `averagingDouble` | a number | mainly useful as a downstream collector, since there is otherwise a primitive-stream equivalent |
| `Collectors.mapping`, `filtering` (Java 9), `flatMapping` (Java 9), `reducing` | downstream collectors | transform, filter, flatten or fold a bucket rather than a whole stream |
| `Collectors.teeing(c1, c2, merge)` | whatever `merge` returns | Java 12; runs two collectors over one stream in a single pass |
| `collect(supplier, accumulator, combiner)` | whatever `supplier` builds | the collector-free escape hatch for a shape no `Collectors` factory matches |

Three places a collector throws where a hand-built `HashMap` would not:

| Where | Exception |
|---|---|
| Two-argument `toMap`, a duplicate key | `IllegalStateException: Duplicate key a (attempted merging values apple and avocado)` |
| `toMap`, a `null` value | `NullPointerException`, no message; the internal `Map.merge` call treats a `null` value as "remove this key" |
| Modifying the list `Stream.toList()` returned | `UnsupportedOperationException` |

| | `Collectors.toList()` | `Stream.toList()` | `Collectors.toUnmodifiableList()` |
|---|---|---|---|
| Mutable | yes | no | no |
| `null` elements | allowed | allowed | throws `NullPointerException`, no message |
| Since | Java 8 | Java 16 | Java 10 |

That asymmetry, an "unmodifiable" name that is null-tolerant sitting next to another that is null-hostile, is the least guessable fact in this table and is only visible by trying it.

## Files

| Never touches the disk | Touches the disk |
|---|---|
| `Path.of`, `resolve`, `normalize`, `relativize`, `toAbsolutePath` | `Files.exists`, `Files.createDirectory`/`createDirectories`, `Files.delete`, `Files.copy`, `Files.move`, `Files.readString`/`readAllLines`, `Files.lines`, `Files.walk`/`find`, `toRealPath()` |

`resolve` returns an absolute argument unchanged and discards the receiver entirely, which is the shape of the bug where a sandbox directory built to hold every read and write quietly stops applying the moment the resolved value happens to be absolute.

`Files.lines`, `Files.walk` and `Files.find` return a `Stream` backed by an open file or directory handle, and the documentation is explicit that it must be closed; the other read methods return once the read is done and hold nothing open afterwards.

The platform default charset is UTF-8 everywhere the JVM runs, since JEP 400 (Java 18); before that release the default was locale-dependent, so code built with no explicit charset argument could change behaviour on any platform whose native default was not already UTF-8.

Safe-write sequence, so a reader never sees a half-written file and a crash mid-write never leaves one behind:

1. `Files.createTempFile(target.getParent(), prefix, suffix)`, in the same directory as the target, since an atomic move is only guaranteed within one filesystem.
2. Write the new content to the temporary file.
3. `Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE)`.

| Exception | Means |
|---|---|
| `NoSuchFileException` | nothing exists at that path, whether the target itself or a required parent directory |
| `FileAlreadyExistsException` | the target already exists and the call did not ask to replace it |
| `DirectoryNotEmptyException` | `Files.delete` on a non-empty directory; walk it and delete the deepest entries first |
| `FileSystemException` | a filesystem-level failure, such as `Too many open files` from a large number of unclosed, still-reachable `Files.lines` or `Files.walk` streams |

A `Path` never confirms that anything real exists behind it; `Files.exists` answers for one instant only, and the filesystem is free to change before the next line runs, so the sturdier shape is to attempt the real operation and catch the specific exception it throws instead of checking first.

## Time

| Type | Answers | Zone or offset attached |
|---|---|---|
| `Instant` | a point on the one universal timeline, no calendar | none |
| `LocalDate` | a calendar date, no time-of-day | none |
| `LocalTime` | a time-of-day, no date | none |
| `LocalDateTime` | a date and a time-of-day, **not an instant**: it has no zero-argument `toInstant()`, and the same reading names a different real moment depending on where it is interpreted | none |
| `ZonedDateTime` | what actually happened in a named region, correct across a daylight-saving transition | a region (`ZoneId`) whose rules can change the offset for a given date |
| `OffsetDateTime` | a timestamp needing a fixed offset for interchange, with no region's rules attached | a fixed `ZoneOffset` |

| | `Duration` | `Period` |
|---|---|---|
| Unit | exact seconds and nanoseconds | years, months, days on a calendar |
| Right for arithmetic on | `Instant`, elapsed machine time | `LocalDate` |
| Crossing a daylight-saving transition | follows the clock; a calendar "day" can be 23 or 25 real hours | follows the calendar; lands on the same wall-clock reading the next day regardless |

| Situation | What `ZonedDateTime.of` does |
|---|---|
| Gap (clocks spring forward; the requested local time never happens) | moves the requested time later by the length of the gap, into the offset that applies after the transition |
| Overlap (clocks fall back; the requested local time happens twice) | picks the earlier of the two valid offsets by default; `withEarlierOffsetAtOverlap()` and `withLaterOffsetAtOverlap()` make the choice explicit instead |

`DateTimeFormatter` supplies predefined constants, `ISO_INSTANT`, `ISO_LOCAL_DATE`, `ISO_DATE_TIME` among them, for the standard forms most interchange already uses; reach for `ofPattern` for a genuinely custom display format, and treat a hand-written pattern anywhere near a service boundary as a sign one of the ISO constants was overlooked.

Storage rule: store an `Instant`, in UTC, for the fact of when something happened, since that is what survives being read back on a different machine in a different zone with the same meaning intact. When the zone is itself part of the business rule, such as a job that must run at a fixed local time forever, store the wall-clock reading and the `ZoneId` separately and recompute the `ZonedDateTime`, and the instant it resolves to, at the moment it is needed, so the daylight-saving rules applied are whichever ones are current then.

## Text

A text block's compiler strips **incidental whitespace**: it finds the smallest leading-whitespace count among every content line and the closing `"""` delimiter's own line, then removes exactly that much from every line, which is why the closing delimiter's column is a decision and not decoration. `\` at the end of a line suppresses the line break there, joining it to the next line with nothing between them. `\s` is a single space that survives stripping even at the end of a line, where a plain trailing space would otherwise be invisible in the source.

| | `trim` | `strip` (Java 11) |
|---|---|---|
| Removes | any leading or trailing character `<= U+0020` | leading or trailing Unicode whitespace, per `Character.isWhitespace` |
| U+2003, em space | left alone, since it sits above `trim`'s cutoff | stripped |
| Default choice | only when the code specifically means "control characters and the ASCII space" | yes |

| | Counts | `"a😀b"` |
|---|---|---|
| `length()` | UTF-16 code units | `4`, the emoji is a surrogate pair |
| `codePointCount(0, length())` | decoded characters | `3` |

Slicing a string by a fixed `length()` offset risks cutting a surrogate pair in half, which produces an unpaired surrogate rather than an exception; use the `codePointCount`, `codePointAt` and `offsetByCodePoints` family where the distinction matters.

`split(regex, limit)` for `"a,b,c,,".split(",", limit)`:

| `limit` | Behaviour | Result |
|---|---|---|
| `0` (the default for one-argument `split`) | trailing empty strings dropped | `[a, b, c]` |
| a positive `n` | at most `n` pieces, the remainder left unsplit in the last one | `[a, b,c,,]` for `n = 2` |
| a negative number | every trailing empty string kept | `[a, b, c, , ]` |

A single expression built with `+`, such as `a + " " + b + " " + n`, already compiles, since JEP 280 (Java 9), to one `invokedynamic` call into `StringConcatFactory`; there is no manual `StringBuilder` to write there. A loop is the case that matters: each `+=` inside it is a separate concatenation, so `n` iterations run the compiler's one-call trick `n` times, each building on a growing string, which is the quadratic behaviour to avoid by declaring a `StringBuilder` before the loop and calling `toString()` once after it.

## Release table

| Feature | Finalised in |
|---|---|
| Multi-catch (`catch (A \| B e)`) | Java 7 |
| try-with-resources | Java 7 |
| `Optional<T>` | Java 8 |
| The Stream API | Java 8 |
| `java.time` | Java 8 |
| `Collectors.toList`, `toSet`, `toMap` | Java 8 |
| `CharSequence.chars()` and `codePoints()` | Java 8 |
| String concatenation via `invokedynamic` (JEP 280) | Java 9 |
| `Stream.iterate(seed, hasNext, next)` | Java 9 |
| `Collectors.filtering`, `Collectors.flatMapping` | Java 9 |
| `Collectors.toUnmodifiableList`, `toUnmodifiableSet`, `toUnmodifiableMap` | Java 10 |
| `String.strip`, `isBlank`, `repeat`, `lines` | Java 11 |
| `String.indent` | Java 12 |
| `Collectors.teeing` | Java 12 |
| Text blocks (JEP 378) | Java 15 |
| `String.formatted` | Java 15 |
| `Stream.toList()` | Java 16 |
| UTF-8 as the platform default charset (JEP 400) | Java 18 |

## Sources

- [JLS Chapter 11, Exceptions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-11.html)
- [JLS 14.20.3, Execution of try-with-resources](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.20.3)
- [`Throwable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Throwable.html)
- [`Optional`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
- [`Stream`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html)
- [`Collectors`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html)
- [`Collector`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collector.html)
- [`Files`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html)
- [`Path`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Path.html)
- [`java.time` package summary](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/package-summary.html)
- [`ZonedDateTime`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/ZonedDateTime.html)
- [`DateTimeFormatter`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/format/DateTimeFormatter.html)
- [`String`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html)
- [JEP 280, Indify String Concatenation](https://openjdk.org/jeps/280)
- [JEP 378, Text Blocks](https://openjdk.org/jeps/378)
- [JEP 400, UTF-8 by Default](https://openjdk.org/jeps/400)
