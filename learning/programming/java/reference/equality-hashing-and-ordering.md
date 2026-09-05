---
title: Equality, Hashing and Ordering
description: The three contracts, what breaks when each is violated, and which comparison to write
type: reference
---

# Equality, Hashing and Ordering

Lookup sheet for stage 1. The question it exists to answer: **which comparison do I write, and what breaks if I get it wrong?**

## Which comparison to write

| Situation | Write | Not |
|---|---|---|
| two primitives | `a == b` | |
| two `double` values, in a comparator | `Double.compare(a, b)` | `a - b`, `a == b` |
| two references, either may be null | `Objects.equals(a, b)` | `a.equals(b)` |
| a value against a constant | `"active".equals(status)` | `status.equals("active")` |
| two enum constants | `a == b` | `a.equals(b)` |
| checking for null | `a == null` | `a.equals(null)` |
| deliberate identity check | `a == b`, with a comment | |
| two `String` or boxed values | `Objects.equals(a, b)` | `a == b` |

`==` on boxed types is correct for `-128` to `127`, because `valueOf` caches that range, and wrong above it. That is why it survives tests.

## The `equals` contract

| Property | Requirement |
|---|---|
| reflexive | `x.equals(x)` is true |
| symmetric | `x.equals(y)` and `y.equals(x)` agree |
| transitive | equality chains |
| consistent | same answer while nothing relevant changes |
| null-rejecting | `x.equals(null)` is false, never throws |

**Tied to it:** `x.equals(y)` implies `x.hashCode() == y.hashCode()`. The reverse is not required.

| Violation | Symptom |
|---|---|
| `equals` without `hashCode` | `HashMap.get` returns null for a key the map contains; `HashSet` holds duplicates |
| constant `hashCode` | correct but every lookup degrades to a scan of one bucket |
| non-final field in `equals` | entry stranded in the old bucket after a change |
| `instanceof` plus a subclass with extra state | symmetry broken, collections disagree with themselves |
| `equals` reads a null field without a guard | `NullPointerException` from a comparison |

Nothing in this table throws at the point of the mistake. That is what makes it a contract rather than a rule.

![Two bucket arrays, with a.equals(b) true in both. Where hashCode is overridden, a and b select the same bucket and the entry is found. Where hashCode is left at identity, a is stored in bucket 1 while the lookup for b reads bucket 3, finds it empty, and returns null without calling equals.](images/hashcode-picks-the-bucket.svg)

`hashCode` chooses the bucket and `equals` only compares what is already in it, so a wrong `hashCode` sends the lookup to a bucket the entry was never in. The comparison that would have said "yes" is never reached. That is why the first row of the table above fails silently: the map is not disagreeing with your `equals`, it is never asking it.

## Keys

A hash key must be **effectively immutable in every field `equals` and `hashCode` read.**

| Candidate | Safe as a key |
|---|---|
| `record Id(long value) {}` | yes |
| `String`, boxed numbers, `enum`, `LocalDate` | yes |
| `record Tags(List<String> names) {}` | no, the component is mutable |
| any class with a non-final field in `equals` | no |
| `List`, `Set`, `Map` | legal, and a mistake |
| a class that overrides neither | identity-keyed, rarely intended |

## The ordering contract

For `Comparable.compareTo` and `Comparator.compare`, only the sign matters.

| Property | Requirement |
|---|---|
| antisymmetric in sign | `sgn(compare(x, y)) == -sgn(compare(y, x))` |
| transitive | `x > y` and `y > z` implies `x > z` |
| consistent on ties | if `compare(x, y) == 0`, both compare alike against every `z` |
| consistent with `equals` | recommended, not required, and see below |

| Violation | Symptom |
|---|---|
| ties between non-equal elements | `TreeSet` and `TreeMap` silently drop them as duplicates |
| subtraction instead of `compare` | overflow reverses the result and breaks transitivity |
| `.reversed()` at the end of a composed chain | reverses every key, not the last one |
| non-transitive comparator | `IllegalArgumentException: Comparison method violates its general contract!` |
| sorting by one comparator, searching with another | `binarySearch` returns nonsense, no exception |

**Total order test:** does the chain end in something unique per element? If not, a sorted collection loses data.

## Composing comparators

```java
Comparator.comparing(Order::customer)                     // by one key
          .thenComparing(Order::createdAt)                // tie-break
          .reversed();                                    // reverses BOTH keys

Comparator.comparing(Order::customer)
          .thenComparing(Order::createdAt,
                         Comparator.nullsLast(Comparator.reverseOrder()));
```

The two-argument `thenComparing` is how a reversal or a null policy applies to one key only.

Use `comparingInt`, `comparingLong` and `comparingDouble` to avoid boxing the extracted key.

## Stability

| Sorting | Stable |
|---|---|
| `List.sort`, `Collections.sort` | yes |
| `Arrays.sort` on an object array | yes |
| `Arrays.sort` on a primitive array | no, and unobservable |

## Deciding in review

1. Does the class override `equals`? Then it must override `hashCode`, and both must read only final fields.
2. Could it be a record? Then it probably should be, and the question becomes whether all components belong in equality.
3. Is any instance of it used as a map key or a set member? Then apply the key table above.
4. Does a comparator exist for it? Then check for a unique tie-breaker and for subtraction.
5. Is anything sorted, then searched? Then check both operations use the same ordering.

## Sources

- [`Object`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
- [`Objects`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Objects.html)
- [`Comparator`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html)
- [`Comparable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Comparable.html)
- [JLS 15.21.3, Reference Equality Operators](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.3)
