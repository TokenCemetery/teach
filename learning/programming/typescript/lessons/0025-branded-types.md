---
title: 25. Branded Types
description: Nominal typing on top of a structural system, and the single assertion it costs
type: lesson
---

# Lesson 25. Branded Types

**Mission link:** Owning a codebase means a user identifier and an order identifier, both just a string underneath, will eventually get swapped, and a brand is how the compiler catches that swap for one honest assertion, paid once.
**Primary source:** [Object Types, intersection types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/objects.html#intersection-types)
**Prerequisites:** [Lesson 24](0024-illegal-states.md), [Lesson 11](0011-structural-assignability.md)

## Warm-up

1. ▢ Lesson 11 showed that assignability compares shapes, not names, so two aliases for the same shape are the same type wherever the compiler looks. Given `type UserId = string` and `type OrderId = string`, what does that rule say about passing a value declared `OrderId` to a parameter typed `UserId`?

<details markdown="1"><summary>Check</summary>

It compiles, with no diagnostic. Both are just names for `string`, and the compiler checks the shape, not the alias written down, so it sees two identical types where a reader sees two different identifiers.

</details>

## Know this

### Two strings are one type

The warm-up is the whole problem, worth seeing run rather than only stated.

```ts
type UserId = string;
type OrderId = string;

const users = new Map<UserId, string>([["u1", "Ada"]]);

function findUser(id: UserId): string | undefined {
  return users.get(id);
}

function placeOrder(orderId: OrderId) {
  return findUser(orderId);
}

console.log(placeOrder("o-987"));
```

This compiles cleanly, and running it prints `undefined`, since `"o-987"` is not a key in `users` and nothing along the way distinguished an order identifier from a user identifier. That is lesson 11's rule working exactly as designed, and also a real defect: the checker rejected nothing, because by its own rule there was nothing to reject.

### Intersecting with a property no value actually has

The fix leaves assignability alone and changes the shape instead.

```ts
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };
```

Each alias is now an intersection: everything a `string` is, plus one property, `__brand`, pinned to a single literal. A `UserId` and an `OrderId` no longer share a shape, so lesson 11's rule now works for the technique instead of against it. Four results follow, each run rather than assumed.

A plain string is refused:

```ts
function needsUser(id: UserId) {}
needsUser("plain");
```

```text
error TS2345: Argument of type 'string' is not assignable to parameter of type 'UserId'.
  Type 'string' is not assignable to type '{ readonly __brand: "UserId"; }'.
```

The bug from the previous section is now caught, since a `UserId` and an `OrderId` are distinct shapes:

```ts
declare const orderId: OrderId;
needsUser(orderId);
```

```text
error TS2345: Argument of type 'OrderId' is not assignable to parameter of type 'UserId'.
  Type 'OrderId' is not assignable to type '{ readonly __brand: "UserId"; }'.
    Types of property '__brand' are incompatible.
      Type '"OrderId"' is not assignable to type '"UserId"'.
```

Both failures report `TS2345`, because both are the same failure: something without the required `__brand` met a position that demands it. And the branded value still behaves like the primitive it wraps:

```ts
declare const userId: UserId;
const plain: string = userId;
console.log(userId.toUpperCase());
```

Both lines compile. A `UserId` is still everything a `string` is, so any position that only asks for a `string` accepts it, and every `string` method is still there to call: the brand costs nothing at the point where a value is used, only at the point where one arrives.

### An asymmetry, and it is the point

Put those results together and a direction appears. A `UserId` flows out to `string` for free, in an assignment or a method call, but a `string` cannot flow in to a `UserId` position, and neither can an `OrderId`. Lesson 11 called this system structural throughout; here is a narrow, deliberate exception, built without touching that rule. It works because an intersection with a property no runtime value carries is a shape nothing satisfies by accident: no string literal or method result ever arrives with a `__brand` attached, so the only way in is to be told it is there. That is nominal typing, identity deciding acceptance instead of shape, for exactly the one property this technique invents and nowhere else.

### The one assertion, and where it has to live

Being told is the only honest description of what has to happen, since nothing ever constructs a `__brand` for real:

```ts
const userId = "plain" as UserId;
```

This compiles. Lesson 18 already covered what an assertion is: a claim that changes what the compiler believes without checking anything, and here there is no other way in, since no value in a running program ever carries a `__brand` to check against. That makes the technique only as trustworthy as the discipline around this one line, written exactly once, inside a function that owns the invariant:

```ts
function makeUserId(raw: string): UserId {
  return raw as UserId;
}

const userId = makeUserId("u-123");
console.log(userId.toUpperCase());
```

Everywhere else, a `UserId` is obtained by calling `makeUserId`, never by writing `as UserId` again. That function is where a real check belongs, stage 5's material once a value can be validated rather than merely asserted, but even before that stage the one assertion site can be audited: read `makeUserId` and you know everything ever allowed to become a `UserId`. A brand asserted at fifty call sites is worse than no brand at all: it looks like a guarantee everywhere it appears while being fifty unchecked claims, and nothing distinguishes the careful nine from the careless one.

### Gone by the time the program runs

The `__brand` property is missing not just from `"u-123"` but from every value that has ever existed while the program ran, because lesson 2's erasure applies here exactly as it applies to `readonly`, and lesson 18's assertion never converts anything. `typeof userId` reports `"string"`, `JSON.stringify(userId)` writes `"u-123"` with no trace of a brand, and no property called `__brand` is ever set on anything, since the type only ever existed for the compiler. So a brand cannot be checked at run time, there is nothing there to check: a `UserId` in a running program is not a value guaranteed valid, it is a value the compiler was once told to believe was valid. The brand is a record that a check happened at `makeUserId`, not a check repeated wherever the value travels afterwards.

### Where the cost is worth paying

A brand earns its ceremony where two values of the same primitive type are interchangeable to the compiler and not to the program: identifiers for different entities sharing a representation, units where a bare number could be metres or seconds, and a string only meaningful once it has passed a format check, an email address or a slug. It is not worth it for one identifier type alone in a small program with nothing nearby to confuse it with, since the ceremony would buy protection against a mistake the program is not close enough to make.

## Practice

1. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   type Meters = number & { readonly __brand: "Meters" };
   type Seconds = number & { readonly __brand: "Seconds" };
   function wait(duration: Seconds) {}
   declare const distance: Meters;
   wait(distance);
   ```

<details markdown="1"><summary>Check</summary>

`error TS2345: Argument of type 'Meters' is not assignable to parameter of type 'Seconds'.`, with a nested line naming the incompatible `__brand` literals. Same failure as `UserId` against `OrderId`, applied to units instead of identifiers.

</details>

2. ▢ Predict whether this compiles.

   ```ts
   type Meters = number & { readonly __brand: "Meters" };
   function toMeters(n: number): Meters {
     return n as Meters;
   }
   const m = toMeters(10);
   const total: number = m + 5;
   ```

<details markdown="1"><summary>Check</summary>

Compiles. `+` only needs its operands to behave as `number`, which `m` still does, and the result widens to plain `number`, which `total`'s annotation accepts. Nothing strips the brand on purpose; it is only ever consulted where a position specifically asks for it.

</details>

3. ▢ Predict this one, and say why the `TS` number differs from item 1 even though the underlying mistake is the same shape mismatch.

   ```ts
   type Meters = number & { readonly __brand: "Meters" };
   const m: Meters = 10;
   ```

<details markdown="1"><summary>Hint</summary>

Nothing here is a function call. Ask what kind of statement is being checked.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'number' is not assignable to type 'Meters'.` `TS2322` is the general assignability diagnostic, for a variable initialiser; `TS2345` is specifically for a call argument. The reason is identical either way, a plain `number` lacks the `__brand`, but the number tracks the kind of position, not the kind of failure.

</details>

4. ▢ A pull request brands `UserId` and then writes `const id = req.params.userId as UserId;` at eleven different route handlers, each reading from a different part of the request. What is wrong with this, specifically, and what should replace it?

<details markdown="1"><summary>Check</summary>

Each `as UserId` is an unchecked claim, exactly what lesson 18 says an assertion always is, so there are eleven places that could be wrong, with no way to tell the validated ones from the rest by looking at the brand. The fix is a single `makeUserId` function every call site uses, giving one place to audit and, later, one place for the real check stage 5 covers.

</details>

5. ▢ Someone, worried that assertions are unchecked, writes this guard and calls it before trusting a value as a `UserId`. Predict what `isUserId("anything")` returns, and say what that reveals about brands at run time.

   ```ts
   type UserId = string & { readonly __brand: "UserId" };
   function isUserId(x: unknown): x is UserId {
     return typeof x === "string" && (x as { __brand?: string }).__brand === "UserId";
   }
   ```

<details markdown="1"><summary>Check</summary>

`false`, for every string, since no string in a running program has a `__brand` property to find; `typeof x === "string"` can pass, but `.__brand === "UserId"` never does. The guard cannot recover at run time something that only ever existed for the compiler, so it checks a property already erased, not a substitute for the factory function.

</details>

## Real-world reps

- [ ] Find two differently named identifiers of the same primitive type in code you work on, and check whether the compiler would currently accept either one where the other belongs.
- [ ] Write a branded type for one of them, with a single factory function that produces it, and route its construction sites through that function instead of an inline `as`.
- [ ] Tomorrow: search that codebase for `as` immediately followed by a domain identifier's type name, and count how many places assert the same brand; treat any count above one as a finding to raise.

## Going further

- [Object Types, intersection types](https://www.typescriptlang.org/docs/handbook/2/objects.html#intersection-types): the handbook section this lesson rests on
- [TypeScript issue archive](https://github.com/microsoft/TypeScript/issues): search "branded" for the community discussion behind why this stays a pattern rather than a language feature
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
