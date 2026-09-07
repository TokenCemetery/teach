---
title: 10. Enums
description: Each enum constant as a real object with its own state and behavior, and precisely where an enum fits over a sealed class
type: lesson
---

# Lesson 10. Enums

**Mission link:** Lesson 9 drew the line between sealed classes (variants that can each carry different data) and enums (typically data-less constants) without covering enums themselves. This lesson is that coverage, and the precise criterion for choosing between the two.
**Primary source:** [Docs: "Enum classes", Kotlin](https://kotlinlang.org/docs/enum-classes.html)
**Prerequisites:** [Lesson 9](0009-sealed-classes-and-exhaustive-when.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What does sealing a class or interface guarantee about its subclasses, compared to an ordinary open class?

<details markdown="1"><summary>Check</summary>

Every direct subclass must be declared within the same module and package as the sealed declaration, so the compiler knows the complete, closed set of subclasses at compile time, unlike an ordinary open class where any code anywhere could add a new subclass.

</details>

2. ▢ Why can a `when` expression over a sealed type skip the `else` branch and still compile as exhaustive?

<details markdown="1"><summary>Check</summary>

Because the compiler knows the sealed type's complete, closed set of subclasses, it can check whether the `when`'s branches cover every one of them directly, without needing a catch-all for cases it can't otherwise account for.

</details>

## Know this

### Each enum constant is a real object, not a bare label

`enum class Direction { NORTH, SOUTH, WEST, EAST }` declares four constants, each an actual object, an instance of `Direction`, not merely a named integer the way some languages' enums work. This is why an enum constant can carry its own constructor arguments (`enum class Color(val rgb: Int) { RED(0xFF0000), GREEN(0x00FF00), BLUE(0x0000FF) }`), giving each constant real, distinct state beyond just being a distinguishable name.

### A constant can override behavior in its own anonymous class body

An enum class can declare abstract members, and each constant can provide its own implementation in an anonymous class body: `enum class ProtocolState { WAITING { override fun signal() = TALKING }, TALKING { override fun signal() = WAITING }; abstract fun signal(): ProtocolState }`. This lets different constants of the same enum behave differently for the same method call, not just hold different data. An enum class can also implement interfaces, either with one shared implementation across all constants or per-constant overrides the same way.

### Every enum gets `entries`, `valueOf()`, `name`, and `ordinal` for free

Kotlin generates, for every enum class, an `entries` property (a specialized, read-only `List` of all constants, in declaration order), a `valueOf(name: String)` function (looking up a constant by its declared name, throwing `IllegalArgumentException` if no match exists), and, on each constant, a `name` property (its declared identifier as a string) and an `ordinal` property (its zero-based position in declaration order). All enum classes also implement `Comparable` by default, ordered by declaration order (their `ordinal`), which is why comparing two enum constants with `<` or sorting a list of them works without writing any comparison logic by hand.

### Choosing between an enum and a sealed class is a real, checkable decision

An enum fits a fixed set of constants that are fundamentally the same *kind* of thing, differing only in which specific value or behavior they represent (a day of the week, a traffic light color, a fixed set of named strategies), where every constant is a singleton, exactly one instance ever exists per constant. A sealed class fits when different variants need to carry genuinely different *shapes* of data, not just different values of the same shape (a network result that's `Loading` with no payload, `Success(data: T)` carrying a typed payload, or `Failure(error: Throwable)` carrying an exception, three structurally different cases, not three instances of the same structure). Reaching for an enum with awkward, only-relevant-to-some-constants extra fields is usually the signal that a sealed class actually fits the data better.

## Practice

1. ▢ Why can `enum class Color(val rgb: Int) { RED(0xFF0000), GREEN(0x00FF00), BLUE(0x0000FF) }` give each constant its own distinct `rgb` value, when a simpler language's enum is just a named integer?

<details markdown="1"><summary>Check</summary>

Because each Kotlin enum constant is a real object, an actual instance of the enum class, it can be constructed with its own constructor arguments the same way any class instance can, giving each constant genuine state beyond just being a distinguishable name.

</details>

2. ▢ In the `ProtocolState` example, `WAITING` and `TALKING` each override `signal()` differently. What does this demonstrate that a plain "list of named constants" enum couldn't do?

<details markdown="1"><summary>Hint</summary>

Consider whether every constant needs to behave the same way for a given method, or can genuinely differ.

</details>

<details markdown="1"><summary>Check</summary>

It demonstrates that individual constants can have their own distinct behavior for the same method, not just distinct data; `WAITING.signal()` and `TALKING.signal()` return different results because each constant provides its own anonymous-class override of the abstract `signal()` method, something a bare list of named values with no behavior couldn't express at all.

</details>

3. ▢ What does `RGB.entries` return, and how does it differ from the older `values()` function it replaced?

<details markdown="1"><summary>Check</summary>

`entries` returns a specialized, read-only `List` of all the enum's constants in declaration order. The `values()` function it replaced (prior to Kotlin 1.9.0) returned an array instead; `entries` is the current, preferred way to list an enum's constants.

</details>

4. ▢ A team models a payment result with an enum: `enum class PaymentResult { SUCCESS, INSUFFICIENT_FUNDS, CARD_DECLINED }`, but `INSUFFICIENT_FUNDS` needs to carry the shortfall amount and `CARD_DECLINED` needs to carry a decline reason code, neither of which applies to `SUCCESS`. What does this signal, and what's the better fit?

<details markdown="1"><summary>Check</summary>

This signals that the variants aren't really the same *shape* of thing; they need genuinely different data attached to different cases, exactly what an enum (fundamentally the same kind of thing, differing only in value) doesn't fit well. A sealed class fits better: `sealed class PaymentResult { object Success : PaymentResult(); data class InsufficientFunds(val shortfall: Int) : PaymentResult(); data class CardDeclined(val reasonCode: String) : PaymentResult() }`, letting each case carry exactly the data it needs.

</details>

5. ▢ Which claim correctly describes choosing between an enum and a sealed class?

   - a) Enums and sealed classes are interchangeable; the choice is purely stylistic
   - b) An enum fits a fixed set of same-shape constants (each a singleton instance), while a sealed class fits variants needing genuinely different data shapes per case; awkward, sparsely-relevant fields on some enum constants signal a sealed class fits better
   - c) An enum constant can never override behavior; only sealed class subclasses can do that
   - d) `entries`, `valueOf()`, `name`, and `ordinal` need to be written by hand for each enum class

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, checkable distinction this lesson (and lesson 9) draws. (a) is false: the shape of the data each variant needs is a real, checkable criterion, not a stylistic preference. (c) is false: enum constants can override abstract members in their own anonymous class body, exactly as the `ProtocolState` example shows. (d) is false: Kotlin generates all four automatically for every enum class, with no manual implementation needed.

</details>

## Real-world reps

- [ ] Find an enum in a codebase you've written or have access to. Check whether any of its constants have fields that don't apply to every other constant, or where the enum's behavior differs oddly by constant, either of which might signal a sealed class fits better.
- [ ] Find a place using `entries` (or the older `values()`) to iterate an enum's constants, or `valueOf()` to look one up by name. Confirm you understand what each returns and what `valueOf()` does when given a name that doesn't match any constant.
- [ ] Tomorrow: read the primary source's section on enum classes implementing interfaces in full, and sketch one small example where different constants provide different implementations of the same interface method.

## Going further

- [Docs: "Enum classes", Kotlin](https://kotlinlang.org/docs/enum-classes.html)
- [Docs: "Sealed classes and interfaces", Kotlin](https://kotlinlang.org/docs/sealed-classes.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
