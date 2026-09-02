---
title: 24. Making Illegal States Unrepresentable
description: Count the states your type permits, then remove the ones your domain does not have
type: lesson
---

# Lesson 24. Making Illegal States Unrepresentable

**Mission link:** Owning a codebase means being able to say which states a type permits and which the domain actually produces, and closing that gap before a bug does it for you instead.
**Primary source:** [Effective TypeScript, Dan Vanderkam](https://effectivetypescript.com/)
**Prerequisites:** [Lesson 23](0023-exhaustiveness-with-never.md), [Lesson 22](0022-discriminated-unions.md)

## Warm-up

1. ▢ Lesson 22 showed that `type Bad = { a?: number; b?: string }` accepts `{ a: 1, b: "both" }` without complaint. Precisely how many states does `Bad` permit, counting presence and absence of each field separately, and how many did the domain that motivated the example actually need?

<details markdown="1"><summary>Check</summary>

Four: `a` present or absent, times `b` present or absent. The domain needed two, one thing or the other, never both, never neither. That gap of two states is the whole subject of this lesson: a type permitting more than the domain produces lets a bug through the front door without a diagnostic.

</details>

## Know this

### Count first, redesign second

The method is arithmetic before it is a redesign. A plain `boolean` permits two states; optional, it permits three, since absence is a third possibility, not one of the original two. Two independent optional booleans permit nine combined, `3 x 3`, since independent fields multiply. Making any field optional multiplies the count by two, because presence is its own axis regardless of how many values the field's type has: that is why counting works on `string` and object fields, where the value space is far too large to enumerate, as long as you count presence rather than values. A union permits exactly the sum of its arms' states, so three fully determined object arms permit exactly three. The procedure follows: count what the type permits, count what the domain produces, and if the first number is larger, name the difference and remove it, almost always by turning optional or independent fields into a union of the domain's actual states, the shape lesson 22 taught you to write and narrow.

### Optional fields that are really alternatives

The warm-up's `Bad` is lesson 22's shape. Here is the same shape in a different domain, deliberately, because recognising it is most of the skill: a stored document whose contents are either held inline or kept elsewhere behind a URL.

```ts
type StoredBad = { inlineText?: string; blobUrl?: string };
const bad: StoredBad = { inlineText: "hello", blobUrl: "https://example.invalid/a" };
```

Compiles: four states against a domain of two, held inline or held remotely, never both, never neither. Counting is what exposes it, and the union names the two states directly.

```ts
type Stored =
  | { kind: "inline"; inlineText: string }
  | { kind: "remote"; blobUrl: string };

const bad: Stored = { kind: "inline", inlineText: "hello", blobUrl: "https://example.invalid/a" };
```

```text
error TS2353: Object literal may only specify known properties, and 'blobUrl' does not exist in type '{ kind: "inline"; inlineText: string; }'.
```

Two states in, two states out, enforced on both ends.

### A flag beside the data it governs

This is the shape most codebases have, grown one field at a time on a request handler.

```ts
type FetchState = { loading: boolean; data?: string; error?: string };

function describe(s: FetchState): string {
  if (s.loading) {
    return "loading, but here is an error anyway: " + s.error;
  }
  return "data: " + s.data + ", error: " + s.error;
}

const bad: FetchState = { loading: true, data: "x", error: "oops" };
```

Compiles clean, and `bad` is loading, holding a result, and holding an error simultaneously, three things that cannot all be true of one request at once. Counting presence and absence, `loading`, `data` and `error` each give two, eight states from a domain that only ever produces three: loading, succeeded with data, or failed with a message. The union says exactly that.

```ts
type FetchState =
  | { status: "loading" }
  | { status: "success"; data: string }
  | { status: "error"; error: string };

function describe(s: FetchState): string {
  switch (s.status) {
    case "loading":
      return "loading";
    case "success":
      return "data: " + s.data;
    case "error":
      return "error: " + s.error;
  }
}

const bad: FetchState = { status: "loading", error: "oops" };
```

```text
error TS2353: Object literal may only specify known properties, and 'error' does not exist in type '{ status: "loading"; }'.
```

Eight states down to three, and the call site changed shape along with the type: `describe` used to read `s.data` and `s.error` straight off a struct that happened to have both, and now it must ask which of the three arms it holds before reading anything member-specific.

### A field whose meaning depends on another

This shape has no optionality, so the count above will not flag it; the tell is a comment doing a type's work.

```ts
type Shipping = {
  method: "pickup" | "delivery";
  // address is required when method is "delivery", ignored when method is "pickup"
  address: string;
};

const s: Shipping = { method: "pickup", address: "no one reads this" };
```

Compiles. `address` is a member of every `Shipping` value regardless of `method`, so a pickup order carries an address nobody reads, and only the comment says the combination is pointless. Moving `address` into the arm that needs it removes the member from the other arm entirely.

```ts
type Shipping =
  | { method: "pickup" }
  | { method: "delivery"; address: string };

const s: Shipping = { method: "pickup", address: "no one reads this" };
```

```text
error TS2353: Object literal may only specify known properties, and 'address' does not exist in type '{ method: "pickup"; }'.
```

A pickup order can no longer be given an address to ignore, since the arm that represents it has no such member.

### What narrowing costs, and why that is the point

Every redesign above made the type shorter and the code reading it longer: a struct read with `s.data` everywhere becomes a `switch` or an `if` chain on the discriminant first. That is not a side effect to minimise, it is the mechanism: skip the check and `s.data` written outside `FetchState`'s `"success"` case gives `error TS2339: Property 'data' does not exist on type 'FetchState'.` The extra code at each call site is where the compiler forces the decision, and lesson 23's exhaustiveness guard turns an unhandled state into a compile error rather than a silent gap. Fewer states is almost always more verbose to consume, worth trading when the states removed have actually produced a bug, not on principle everywhere; a type with one optional field that genuinely means "not yet known" does not need a union.

### Where the method stops

Counting states only finds problems about which combination of fields exists. It says nothing about constraints inside a single state.

```ts
type Ticket = { price: number; discountPercent: number };
const t: Ticket = { price: -10, discountPercent: 150 };
```

Compiles. `price` and `discountPercent` are each exactly one state, a `number`, so there is no combination to remove; the problem is that `number` admits values the domain does not, negative prices and percentages over a hundred. The same is true of two fields whose values must sum to a third, or a string that must look like an identifier: no rearrangement into a union changes what a single `number` or `string` accepts. Two things cover that, and neither is a rearrangement. A value arriving from outside your own code has to be checked at that boundary, which is stage 5's material and the honest answer for a range. And where the check has already happened and you want the type to remember it, lesson 25's pattern applies: a single constructing function, and a type nothing else can produce. Lesson 25 demonstrates that pattern on identifiers rather than on ranges, so treat the range case as the pattern applied rather than as something already shown. This lesson's method finds the states a shape should not have; those two cover what a shape cannot express at all.

## Practice

1. ▢ `type Card = { discount?: number; giftCode?: string };` Count the states this permits, then predict whether `{ discount: 10, giftCode: "SUMMER" }` compiles.

<details markdown="1"><summary>Check</summary>

Four states, discount present or absent times gift code present or absent. Compiles with no diagnostic, so a card can carry both at once, exactly the kind of combination that needs a domain answer before deciding whether it is illegal.

</details>

2. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   type Contact =
     | { kind: "email"; email: string }
     | { kind: "phone"; phone: string };

   const bad: Contact = { kind: "email" };
   ```

<details markdown="1"><summary>Hint</summary>

This is a missing member, not an excess one, so it is not the `TS2353` you saw above.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type '{ kind: "email"; }' is not assignable to type 'Contact'.`, detailed as `Property 'email' is missing in type '{ kind: "email"; }' but required in type '{ kind: "email"; email: string; }'.` The chosen arm is a complete object type, so leaving out its other member is an ordinary missing-property error against it.

</details>

3. ▢ `type UploadState = { uploading: boolean; result?: string; error?: string };` Name the domain states this should have, count the states the type permits, and predict whether `{ uploading: false, result: "ok", error: "also this" }` compiles.

<details markdown="1"><summary>Check</summary>

Uploading, succeeded with a result, or failed with a message, three domain states. The type permits `2 x 2 x 2`, eight. Compiles with no diagnostic, holding a result and an error while claiming not to be uploading, the same illegal combination `FetchState` had before its redesign.

</details>

4. ▢ Predict whether this compiles, and say in one sentence what is doing the work a type should be doing instead.

   ```ts
   type Discount = {
     kind: "percentage" | "fixed";
     // amount is 0 to 100 when kind is "percentage", a currency amount in cents when kind is "fixed"
     amount: number;
   };

   const weird: Discount = { kind: "percentage", amount: 5000 };
   ```

<details markdown="1"><summary>Check</summary>

Compiles, no diagnostic, and `weird` claims a percentage of five thousand. The comment alone tells a reader which range applies for which `kind`, and nothing checks the value against it; splitting `amount` into each arm would not even fix this, since both would still take a bare `number`, the boundary the next section names.

</details>

5. ▢ `type Ticket = { price: number; discountPercent: number };` and the domain rule is that `price` must never be negative and `discountPercent` must stay between 0 and 100. Predict whether turning this into a union removes the illegal states, and say what would.

<details markdown="1"><summary>Hint</summary>

Ask how many states `price` alone has as a type, regardless of what values you consider legal.

</details>

<details markdown="1"><summary>Check</summary>

No. `price` and `discountPercent` are each a single state as a type, a `number`, so there are no field combinations to remove; `-10` and `150` are illegal values inside a state that already exists, not an extra state. This is the last section's boundary: validation at the edge checks a value arriving from outside, lesson 25's pattern lets a type remember that a check happened, and no rearrangement of `Ticket`'s fields does either job.

</details>

## Real-world reps

- [ ] Find a type with two or more optional fields, count the states it permits against what the domain produces, and write down what the difference represents.
- [ ] Find a boolean flag beside optional data it governs, a loading flag, an `isValid` flag, a `hasError` flag, and check whether the illegal combination it permits has ever shown up in a bug report or a log line.
- [ ] Tomorrow: redesign one of the types above as a union of its actual domain states, and find every place that reads the old shape to see how each call site changes.

## Going further

- [Handbook, Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html): optional members and how they combine
- [Handbook, Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html): the discriminated union material this lesson builds on
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
