---
title: "21. Strings and Text"
description: Text blocks, the formatting you should use, and why length is not the number of characters
type: lesson
---

# Lesson 21. Strings and Text

**Mission link:** A reviewer judges idiomatic Java partly on how a change handles text, since a string looks like the simplest type in the language while quietly hiding the widest gap between what a method appears to do and what its default arguments actually do.
**Primary source:** [`String`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html)
**Prerequisites:** [Lesson 2](0002-identity-and-equality.md), [Lesson 14](0014-immutability-as-a-default.md)

## Warm-up

1. ▢ Two `String` variables are each built from the same literal text but one is built with `new String(...)`. What does `==` report, and what should the code write instead?

<details markdown="1"><summary>Check</summary>

`==` reports `false`, because `new String(...)` forces a distinct object even though the pooled literal already exists with the same content. The code should compare with `equals`, or `Objects.equals` when either side might be `null`.

</details>

2. ▢ Why must a `LocalDateTime` never be used to represent a timestamp?

<details markdown="1"><summary>Check</summary>

It has no time zone or offset, so the same `LocalDateTime` value names a different real moment depending on where it is read, and it cannot be converted to an `Instant` without supplying one. Recording it as a timestamp silently drops the information needed to know when the event actually happened.

</details>

## Know this

`String` is immutable: once constructed, its content never changes, which is what lets the compiler intern literals and lets two references share one object safely (that sharing is [interning](../GLOSSARY.md), covered in lesson 2). Every method that looks like it modifies a string, `strip`, `toUpperCase`, `concat`, in fact returns a new one and leaves the original alone.

### Text blocks

A text block (final in Java 15, [JEP 378](https://openjdk.org/jeps/378)) is a multi-line string literal delimited by `"""`:

```java
String flushClose = """
    line one
    line two
""";

String matchedClose = """
    line one
    line two
    """;
```

Both literals have identical content lines, indented four spaces, and differ only in where the closing `"""` sits. Running them prints:

```text
[flushClose]    line one
    line two
[/flushClose]
[matchedClose]line one
line two
[/matchedClose]
```

The compiler strips **incidental whitespace**: it finds the smallest leading-whitespace count among every content line and the closing delimiter's own line, then removes exactly that much from every line. In `flushClose` the delimiter sits at column zero, so the minimum is zero and nothing is stripped, four spaces survive. In `matchedClose` the delimiter lines up with the content at four spaces, so the minimum is four and every line loses its indent entirely. This is why the closing delimiter's column is a decision, not decoration.

Two escapes exist because stripping and normal line breaks would otherwise fight over the source's formatting. `\` at the end of a line suppresses the line break that would otherwise appear there, joining it to the next line with nothing between them:

```java
String c = """
    no\
    break here""";
// "nobreak here"
```

`\s` is a single space that survives stripping even at the end of a line, since a plain trailing space would otherwise be invisible in the source and easy to lose to an editor's trim-on-save:

```java
String d = """
    trailing space\s
    next line""";
// "trailing space \nnext line"
```

A text block is the wrong choice for a short, single-line string, since three quote characters and a line of stripping rules cost more than they buy there, and for content that itself contains a `"""` sequence, which needs escaping and stops reading as literal text. It is also the wrong choice when the string is built from pieces at run time, since a text block is still a compile-time literal and interpolation is not part of it, `formatted` or concatenation still does that part.

### `formatted`, `String.format`, and the localised case

```java
"%s has %d items".formatted("cart", 3)   // "cart has 3 items"
String.format("%s has %d items", "cart", 3)   // the same string
```

`formatted` (Java 15) is an instance method on the same format string that `String.format` takes as its first argument, so `template.formatted(args)` and `String.format(template, args)` do exactly the same work, chosen for whichever reads better at the call site. Both use the default locale for anything locale-sensitive inside the pattern, such as a decimal separator. `java.text.MessageFormat` exists for the case an application actually needs, a message pattern chosen per user locale with correct pluralisation and number formatting, and is worth knowing by name rather than learning here.

### `strip` against `trim`

`trim` predates Unicode-aware whitespace: it removes any leading or trailing character whose value is `<= U+0020`. `strip` (Java 11) asks `Character.isWhitespace` instead, which recognises whitespace characters above that boundary too, such as U+2003 (em space):

```java
String padded = "\u2003hello\u2003";
padded.trim();    // unchanged, length 7: U+2003 is above trim's cutoff
padded.strip();   // "hello", length 5
```

Prefer `strip` by default. `trim` is only right when the code specifically means "control characters and the ASCII space", which is rare.

### The rest of the convenience methods

`isBlank` (Java 11) is true for a string that is empty or entirely whitespace under the same Unicode-aware rule as `strip`; `isEmpty` only checks length zero, so `"   ".isBlank()` is `true` while `"   ".isEmpty()` is `false`. `repeat(n)` (Java 11) concatenates `n` copies, and `repeat(0)` gives the empty string rather than throwing. `lines()` (Java 11) splits on line terminators and returns a stream with none of them included, `"one\ntwo\nthree".lines()` yields `one`, `two`, `three`. `chars()` and `codePoints()`, both default methods on `CharSequence` since Java 8, stream the string as `int` code units and code points respectively. `indent(n)` (Java 12) adds `n` spaces to the start of every line for a positive argument, removes up to `n` leading whitespace characters per line for a negative one, and guarantees the result ends with a line terminator.

### `split` and `join`

`split(regex, limit)` has a limit argument whose sign changes the behaviour, not just the count:

```java
String csv = "a,b,c,,";
csv.split(",", 0);    // [a, b, c]          trailing empty strings dropped
csv.split(",", 2);    // [a, b,c,,]         at most 2 pieces, the rest left in the second
csv.split(",", -1);   // [a, b, c, , ]      every trailing empty string kept
```

Limit zero, the default when calling `split(regex)` with one argument, discards trailing empty strings, which is almost never what you want from a CSV line where a trailing empty field is meaningful. A negative limit keeps them, and a positive limit caps the piece count while leaving the remainder unsplit in the final piece. `String.join(delimiter, elements)` is the inverse and has no such trap.

### `StringBuilder`, honestly

A single expression built from `+` already compiles to one efficient call, not a chain of intermediate `StringBuilder` objects: `a + " " + b + " " + n` compiles, since [JEP 280](https://openjdk.org/jeps/280) in Java 9, to one `invokedynamic` call into `StringConcatFactory`, which the JIT is free to implement however is fastest. There is no manual `StringBuilder` to write here and no advice to follow beyond writing the expression plainly. The case that matters is a loop: each iteration's `+=` is a separate concatenation, so a loop of `n` iterations does the compiler's one-call trick `n` times, each one building on a growing string, which is the quadratic behaviour worth avoiding. Declare a `StringBuilder` before the loop, `append` inside it, and call `toString()` once after.

### `char`, code units, and code points

A Java `char` is a UTF-16 **code unit**, not a character. Most characters fit in one code unit, but any character outside the Basic Multilingual Plane, most emoji among them, needs a **surrogate pair**, two code units together, to be represented at all:

```java
String s = "a😀b";
s.length();                          // 4
s.codePointCount(0, s.length());     // 3
```

`length()` counts code units, so the grinning-face emoji counts as two, while `codePointCount` walks the string decoding surrogate pairs and counts three actual characters. Any code that slices a string by a fixed `length()` offset risks cutting a surrogate pair in half, which produces an unpaired surrogate rather than an exception. Where the distinction matters, use the `codePointCount`, `codePointAt` and `offsetByCodePoints` family instead of the `char`-indexed one.

### `equalsIgnoreCase` and locale

Case conversion is locale-sensitive because the mapping from lower to upper case is not the same in every language:

```java
"istanbul".toUpperCase(Locale.ROOT);                        // "ISTANBUL"
"istanbul".toUpperCase(Locale.forLanguageTag("tr"));         // "İSTANBUL", dotted capital I
"TITLE".toLowerCase(Locale.forLanguageTag("tr"));            // "tıtle", dotless i
"TITLE".toLowerCase(Locale.ROOT);                            // "title"
```

Calling `toLowerCase()` or `toUpperCase()` with no argument uses the JVM's default locale, whatever that happens to be on the machine the code runs on, which makes a case conversion used for anything other than display, a protocol tag, a file extension, a dictionary key, into a bug that only appears on some machines. Use `Locale.ROOT` for any case conversion that is not about display to a specific user. `equalsIgnoreCase` sidesteps the whole question: it compares through `Character.toUpperCase` and `Character.toLowerCase`, which use a fixed Unicode mapping rather than a locale, so `"i".equalsIgnoreCase("I")` gives the same answer everywhere. Prefer it outright over `a.toLowerCase().equals(b.toLowerCase())`, which both allocates two strings and reopens the locale question.

### `String.valueOf(null)`

```java
String.valueOf((Object) null);   // "null"
Objects.toString(null);          // "null"
String.valueOf(null);            // NullPointerException
```

`String.valueOf` is overloaded, including `valueOf(Object)` and `valueOf(char[])`. A bare `null` argument is applicable to both, and overload resolution picks the most specific applicable one, `char[]`, since every `char[]` is an `Object` but not the reverse. That overload builds a `String` from the array, and a `null` array fails there with a `NullPointerException`, not at the call site and not as a compiler ambiguity error. The safe null-tolerant conversion is `Objects.toString(value)`, or an explicit cast to `Object` if `String.valueOf` must be the method called.

## Practice

1. ▢ Predict what each of these two text blocks prints, then explain the difference from the closing delimiter alone.

   ```java
   String x = """
       first
       second
   """;

   String y = """
       first
       second
       """;
   ```

<details markdown="1"><summary>Check</summary>

`x` keeps four leading spaces on both lines, because its closing `"""` sits at column zero, making zero the minimum indentation across every content line and the delimiter line. `y` strips all four spaces, because its closing `"""` lines up with the content at four spaces, making four the minimum. Nothing about the content lines changed between the two, only where the closing `"""` was placed.

</details>

2. ▢ Predict `s.length()` and `s.codePointCount(0, s.length())` for `String s = "a🎉b"`, and explain why they differ.

<details markdown="1"><summary>Check</summary>

`length()` is `4`, `codePointCount` is `3`. The party-popper emoji sits outside the Basic Multilingual Plane, so it needs a surrogate pair, two `char` code units, to represent one character. `length()` counts code units and sees four; `codePointCount` decodes the pair and counts three real characters.

</details>

3. ▢ Find the bug. This method is meant to be a locale-independent, case-insensitive equality check, and it is not:

   ```java
   static boolean sameKey(String a, String b) {
       return a.toLowerCase().equals(b.toLowerCase());
   }
   ```

<details markdown="1"><summary>Hint</summary>

`toLowerCase()` with no argument does not ask what locale-independent means; it asks the JVM's default locale.

</details>

<details markdown="1"><summary>Check</summary>

`toLowerCase()` uses the default locale, so on a machine whose default locale is Turkish, `"TITLE".toLowerCase()` gives `"tıtle"` with a dotless i rather than `"title"`, and the comparison can fail against a key produced on a different machine. Write `a.equalsIgnoreCase(b)`, which never consults a locale, or `a.toLowerCase(Locale.ROOT).equals(b.toLowerCase(Locale.ROOT))` if the lower-cased value is needed afterwards.

</details>

4. ▢ `"a,b,c,,".split(",", limit)` for `limit` equal to `0`, `2`, and `-1` gives three different results. State all three and explain what the sign and magnitude of `limit` each control.

<details markdown="1"><summary>Check</summary>

`0` gives `[a, b, c]`: trailing empty strings are dropped, and this is also what a one-argument `split(regex)` does. `2` gives `[a, b,c,,]`: the magnitude caps the result at two pieces, so everything after the first comma is left unsplit in the second piece. `-1` gives `[a, b, c, , ]`: any negative limit keeps every trailing empty string, so all five fields survive. Reading a delimited format where a trailing empty field is meaningful needs a negative limit, not the default.

</details>

5. ▢ A colleague builds a report by concatenating ten thousand rows with `+=` inside a loop, and separately writes a one-line log message as `"user " + id + " logged in"`. They ask whether both need a `StringBuilder`. What do you tell them, and why does the answer differ?

<details markdown="1"><summary>Check</summary>

The loop needs an explicit `StringBuilder`, declared once before the loop and appended to inside it, because each `+=` is a separate concatenation and the compiler cannot merge iterations of a loop into one call; ten thousand iterations otherwise do ten thousand growing concatenations. The single log line needs nothing extra: a `+` chain in one expression already compiles to one call that builds the whole string at once, so writing it as a manual `StringBuilder` would add code without changing what runs.

</details>

6. ▢ A teammate guards against a null value by writing `String.valueOf(null)` directly, expecting `"null"` back. Predict what actually happens, and explain why a variable of type `String` or `Object` holding `null` would not have the same problem.

<details markdown="1"><summary>Check</summary>

`String.valueOf(null)` throws `NullPointerException`, not `"null"`. Overload resolution runs on the argument's static type, and the literal `null` is assignable to every reference type, so both `valueOf(Object)` and `valueOf(char[])` are applicable; the compiler picks the more specific one, `char[]`, and building a `String` from a `null` array fails inside the constructor. A variable declared `String` or `Object` never has this ambiguity, since its static type is not assignable to `char[]`, so only `valueOf(Object)` applies and the call safely returns `"null"`. `Objects.toString(value)` is the version that is safe either way, since it has only one overload.

</details>

## Real-world reps

- [ ] Write a text block for a short SQL or JSON fragment you actually have, predict what the stripped indentation will be before running it, then run it and check.
- [ ] Search code you know for a case-insensitive comparison and check whether it uses `equalsIgnoreCase` or a locale-free `toLowerCase(Locale.ROOT)`, rather than a bare `toLowerCase()`.
- [ ] Find a `split` call in code you know and check what its limit argument actually does to trailing empty fields, since the default of zero silently drops them.
- [ ] Tomorrow: find a place in code you have that stores or displays user-supplied text, and check what happens to a length-based check or a substring cut if that text contains an emoji.

## Going further

- [`String`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html): every method this lesson used, in one page
- [JEP 378: Text Blocks](https://openjdk.org/jeps/378): the full indentation and escape rules, including cases this lesson did not cover
- [`Locale`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Locale.html): `ROOT` and the locale-sensitive methods that take one
- [Idiom and the library](../reference/idiom-and-library.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
