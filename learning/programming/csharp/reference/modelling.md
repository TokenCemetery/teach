---
title: Modelling
description: Properties' three promises, what record generates and how its equality works, the pattern vocabulary, interfaces with default implementations, and generic constraints and variance
type: reference
---

# Modelling

Lookup sheet for stage 2: choosing the right type, not a class for everything. Five constructs, and what each commits you to.

## Choosing the construct

| Requirement | Reach for | Because |
|---|---|---|
| Small value, compared by contents, passed around constantly | `readonly record struct` | Value type: no allocation, copy semantics; `record` for compiler-synthesized value equality; `readonly` because a positional `record struct` otherwise gets read-write properties |
| Identity that matters, mutated over a lifetime | `class` | Reference equality is what identity (and a change tracker like EF Core) needs; records are not appropriate as EF Core entity types |
| Read-only data downstream code pattern-matches on | Positional `record` | Value equality suits it; the positional form generates `Deconstruct`, which is what makes positional patterns work |
| A contract several unrelated types implement, extensible later | `interface` | A method can be added later as a default implementation without breaking existing implementers |
| The same behaviour regardless of the concrete type it operates on | Generic type or method | Reusability and type safety without erasure |

## Properties: three promises, easy to confuse

| Modifier | Promises | Does **not** promise |
|---|---|---|
| `required` | Every construction expression must initialise the member | The value is non-null; setting it to `null` or `default` is valid |
| `init` | Assignable only during construction (constructor or object initializer), never after | That it will be assigned at all |
| A non-nullable type | The value should not be null (flow analysis) | That it must be set, or that it can't change later |

Assigning `null` to a required, non-nullable property compiles with a **nullability warning**; omitting the member entirely is error **CS9035**. Different mechanisms, different diagnostics: `required` polices whether you said something, nullability polices what you said.

An expression-bodied property (`public string Name => $"{First} {Last}";`) has **no backing field**; it computes on every access, so it cannot go stale, at the cost of redoing the work on every read.

## What `record` generates from positional parameters

| Generated | Detail |
|---|---|
| One auto-property per positional parameter | Init-only for `record class` and `readonly record struct`; **read-write** for plain `record struct` |
| A primary constructor | Parameters matching the positional ones |
| A parameterless constructor | Only for `record struct`, setting each field to default |
| `Deconstruct` | One `out` per positional parameter; **ignores** any property declared with ordinary syntax |
| `ToString` | Type name plus each public property/field as name and value |

`record` is a modifier, not a third kind of type: `record class` (or just `record`) is a reference type, `record struct` is a value type. Both use `struct`-style equality (same type, same values), but **compiler-synthesized** from declared members rather than `ValueType.Equals`'s reflection.

**Equality follows the runtime type, not the declared one** (for `record class`): a `Person`-typed `Teacher` and a `Person`-typed `Student` with identical values compare unequal, via a synthesized `EqualityContract`. A `Person`-typed and a `Student`-typed variable holding the same `Student` values compare equal.

**`with` copies, then changes.** `original with { }` (no changes) compares equal to `original`, since equality is about values, not identity.

**Shallow immutability is the trap.** Init-only freezes a value-type property's value or a reference-type property's *reference*, not what that reference points at: `person.PhoneNumbers[0] = "555-6789"` succeeds on an init-only `string[]` property. `with` makes it worse, not better: it copies the reference, so the original and the copy then share one mutable array. Fix is at the type level (an immutable collection type), not at the property level.

**Records are the wrong choice for EF Core entities.** EF Core depends on reference equality for one instance per conceptual entity, and doesn't support updating immutable entity types either.

## Pattern vocabulary

One vocabulary, usable in `is`, `switch` statements, and `switch` expressions:

| Pattern | Example | Matches when |
|---|---|---|
| Declaration and type | `o is string s` | Non-null and runtime type satisfies the check |
| Constant | `x is 0`, `x is null` | Equals the constant |
| Relational | `x is > 15.0` | Comparison holds |
| Logical | `not`, `and`, `or` | Combining the above |
| Property | `date is { Year: 2020 }` | Non-null and every nested pattern matches the named member |
| Positional | `point is (0, 0)` | `Deconstruct` succeeds and each nested pattern matches |
| List | `numbers is [1, 2, 3]` | Each nested pattern matches the corresponding element; `..` (slice) matches any number of elements |
| `var` / discard | `[var first, _, _]` | Always; binds or ignores |

`input is not null` and `somethingPossiblyNull is { } bound` both test non-null; only the second binds a variable in the same step. A positional pattern calls the generated `Deconstruct`, so it only exists for **positional** records (a record mixing positional and ordinary-syntax properties supports patterns over the positional half only).

**Switch-expression exhaustiveness has one hole.** An unmatched arm throws (`SwitchExpressionException` / `InvalidOperationException`) at runtime; the compiler usually warns when arms don't cover every input, **except for list patterns**, which produce no such warning. Add a discard (`_`) arm deliberately whenever the arms are list patterns.

**Arm order is a compile-time question.** An arm already covered by an earlier one is error **CS8510** (unreachable pattern), not silent dead code, unlike the equivalent `if`/`else if` chain, which has the identical ordering hazard with no diagnostic at all.

## Interfaces with default implementations

An interface member may carry a **default implementation** (since C# 8) so a new member can be added to a published interface without breaking existing implementers. Put the logic in a `protected static` helper so an implementer can extend rather than replace it; parameterize a default implementation with **private static** fields (instance fields are not allowed).

**The auto-property trap**: `public string Name { get; set; }` means an auto-implemented property with a compiler-generated field in a class or struct, but in an **interface** it declares a property with **no default implementation** that every implementer must provide (instance auto-properties would need a hidden field, which an interface can't hold). Identical syntax, opposite meaning, no diagnostic.

**A default member isn't automatically on the class's own surface.** If it isn't overridden as a public method or an explicit interface implementation, it still lives on the interface: calls reach it only through an interface-typed reference, unlike a Java default method, which arrives as an inherited method on the implementing type.

**Explicit interface implementation** (`void IControl.Paint()`) is callable **only through that interface type**; it leaves the class's own public surface entirely, resolving a same-signature clash between two implemented interfaces at that cost.

## Generic constraints and variance

Type arguments are **not erased**: `typeof(T)` works at runtime, `List<int>` genuinely stores integers, no `reified` or `Class<T>` workaround needed.

| Constraint | Meaning |
|---|---|
| `where T : struct` | Non-nullable value type; **implies** `new()`, can't combine with it |
| `where T : class` | Reference type; non-nullable in a nullable context |
| `where T : class?` | Reference type, nullable or not |
| `where T : notnull` | Any non-nullable type, reference or value |
| `where T : new()` | Accessible parameterless constructor |
| `where T : SomeBase` / `ISomeInterface` | That base class (or derived) / that interface |

Ordering: at most one of `struct`/`class`/`class?`/`notnull`/`unmanaged` may appear, and it must be **first**; `new()`, if present, must be **last**.

**Variance is a rule about positions.** `out T` (covariant) may appear only in output positions (e.g. `IEnumerable<out T>`, so `IEnumerable<Dog>` flows into `IEnumerable<Animal>`); `in T` (contravariant) only in input positions (e.g. `Action<in T>`, so `Action<Animal>` flows into a `Action<Dog>` parameter). A type with both a getter and a setter/`Add` in `T`'s position (`IList<T>`) is invariant.

**`static abstract`/`static virtual` members have no runtime dispatch**; the compiler resolves them at compile time from type information, so they appear almost exclusively in generic interfaces that self-constrain their type parameter (`interface INumber<TSelf> where TSelf : INumber<TSelf>`), letting the interface declare operators in terms of `T` rather than the interface itself.

## Related

- [Lesson 7](../lessons/0007-properties.md), [Lesson 8](../lessons/0008-record-types.md), [Lesson 9](../lessons/0009-pattern-matching.md), [Lesson 10](../lessons/0010-interfaces.md), [Lesson 11](../lessons/0011-generics.md)
- [Value vs Reference Types](value-vs-reference-types.md): the struct/class distinction this sheet's construct choices build on
