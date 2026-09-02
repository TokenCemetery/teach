---
title: 22. Discriminated Unions
description: One shared literal property, and a union the compiler can take apart
type: lesson
---

# Lesson 22. Discriminated Unions

**Mission link:** Owning a codebase means recognising the union types that are really a set of named states, and arranging each one so the compiler refuses the states that should not exist.
**Primary source:** [Narrowing, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
**Prerequisites:** [Lesson 12](0012-narrowing.md), [Lesson 10](0010-unions-and-literal-types.md)

## Warm-up

1. ▢ Lesson 12 narrowed a union with `x === "a"`, an equality check against a literal. Given `type A = { kind: "a"; a: number }; type B = { kind: "b"; b: string };` and `function g(x: A | B) { console.log(x.a); }`, predict whether `g` compiles.

<details markdown="1"><summary>Check</summary>

It does not. `error TS2339: Property 'a' does not exist on type 'A | B'.` with a second line naming `B` as the member that lacks `a`. `x` stays typed `A | B` for the whole of `g`, and nothing narrows it before `x.a` is read, so the compiler offers only what every member has in common. Reaching `a` needs the same equality check lesson 12 taught, aimed at `kind` rather than at `x` itself, which is this lesson.

</details>

## Know this

### The shape

A discriminated union is a union of object types that all carry one property in common, with a literal type and a different literal in every arm. The Handbook calls that shared property the discriminant. In the warm-up's `A | B`, `kind` is the discriminant: every arm declares it, every arm gives it its own literal, and no arm's `kind` overlaps another's. `a` and `b` are the members each arm carries alone, what the shape exists to protect. Once you can name the discriminant in a type someone else wrote, you can predict how it narrows without reading the rest of the file. It recurs constantly: API responses, event objects, anything with a `type` or `status` field.

### Why the compiler can take it apart

Nothing new happens in the type system here. `x.kind === "a"` is the same equality narrowing lesson 12 taught: compare a value against a literal, and keep only the union members whose type admits it. What is new is arrangement, not mechanism. `A` declares `kind: "a"` and no other arm can be `"a"`; `B` declares `kind: "b"` and no other arm can be `"b"`, so one comparison eliminates every member but one.

```ts
type A = { kind: "a"; a: number };
type B = { kind: "b"; b: string };

function f(x: A | B) {
  if (x.kind === "a") {
    console.log(x.a);
  } else {
    console.log(x.b);
  }
}
```

This compiles, and each branch sees only its own member: inside the `if`, `x` is `A`; inside the `else`, `x` is `B`. Neither branch can reach the other arm's property, and that restriction is the reason to reach for this shape: it turns the warm-up's `TS2339` from an obstacle into a signal, forcing every piece of code touching the union to check which arm it has. Calling this a trick undersells it; it is a technique, arranging types so a check you already had lets ordinary narrowing do work it could not do before.

### The failure that motivates it

Here is the case a discriminated union replaces. A payment is either paid by card, which needs a card number, or paid by wallet, which needs a wallet ID. Written carelessly, both fields end up optional on one type:

```ts
type Bad = { cardNumber?: string; walletId?: string };
const t: Bad = { cardNumber: "4111 1111", walletId: "w-8842" };
```

This compiles. Two optional properties describe four states: neither present, only `cardNumber`, only `walletId`, or both, and the assignment above is the fourth state compiling without complaint. The domain has two legal states, paid by card or paid by wallet, and the compiler cannot object to the other two, because the type told it all four were fine. That gap is not a corner case; it is the type admitting more than the domain does, leaving every function that receives a `Bad` to decide by hand what "both" or "neither" should mean.

A discriminated union closes the gap, because a single property now decides which other properties are legal:

```ts
type Good = { kind: "card"; cardNumber: string } | { kind: "wallet"; walletId: string };
const paid: Good = { kind: "card", cardNumber: "4111 1111" };
const bad: Good = { kind: "card", cardNumber: "4111 1111", walletId: "w-8842" };
```

`paid` compiles. `bad` does not: `error TS2353: Object literal may only specify known properties, and 'walletId' does not exist in type '{ kind: "card"; cardNumber: string; }'.` The `kind: "card"` tag tells the checker which arm to match against, and `walletId` belongs to the other arm, so it is rejected at construction rather than discovered later by a function that had to guess. `Good` has exactly two states, one per arm, matching the domain. That is the argument for this shape: not that it looks tidier, but that the illegal states become unrepresentable rather than merely discouraged.

### Where the discriminant comes from

In practice the discriminant is rarely invented; it is a field already in the domain: a `status` from a database row, a `type` tag on an event, a field in an API response. What matters is that its type is a literal, not the general `string`, which reaches straight back to lesson 10's widening: a returned object literal widens an unannotated discriminant exactly as lesson 10 widened `kind`, and the fix is the same `as const` or annotated return type.

A sharper failure is specific to discriminated unions, not lesson 10 again: declaring the discriminant itself as `string` in the type, rather than letting a value merely widen into one.

```ts
type Loading = { status: string };
type Done = { status: string; data: string };
type State = Loading | Done;

function f(x: State) {
  if (x.status === "done") {
    console.log(x.data);
  }
}
```

`x.status === "done"` is the same equality check as before, but it eliminates nothing, since both arms admit any string, so neither is ruled out. `x.data` still fails: `error TS2339: Property 'data' does not exist on type 'State'.`, followed by `Property 'data' does not exist on type 'Loading'.` The check ran and told the compiler nothing, the cost of a discriminant that was never a literal.

### Choosing a name and values

Any property name works as a discriminant; `kind`, `type`, `status` and `tag` all appear in real code, with no compiler preference among them. What matters more than the name is consistency across a codebase, so a reader who looks for `kind` on one type is not made to relearn the convention on the next. A boolean also works, since `true` and `false` are literal types too:

```ts
type Circle = { isSquare: false; radius: number };
type Square = { isSquare: true; side: number };
type Shape = Circle | Square;

function area(s: Shape) {
  if (!s.isSquare) {
    return Math.PI * s.radius * s.radius;
  }
  return s.side * s.side;
}
```

This compiles; `!s.isSquare` narrows just as well as the positive check would. A boolean discriminant is limited to exactly two arms, since there is no third value to give a third one, and `isSquare` reads worse at every call site than a named tag such as `kind: "circle" | "square"`, since the reader has to remember what `false` means rather than reading it off the value.

## Practice

1. ▢ Predict the output of both calls.

   ```ts
   type A = { kind: "a"; a: number };
   type B = { kind: "b"; b: string };

   function describe(x: A | B): string {
     if (x.kind === "a") {
       return `a: ${x.a}`;
     }
     return `b: ${x.b}`;
   }
   console.log(describe({ kind: "a", a: 5 }));
   console.log(describe({ kind: "b", b: "hi" }));
   ```

<details markdown="1"><summary>Check</summary>

`a: 5` then `b: hi`. The `kind` check narrows `x` to `A` in the first branch and, since every other path returns, to `B` on the final line, so each `return` reaches the member it names.

</details>

2. ▢ Predict the diagnostic, with its `TS` number.

   ```ts
   type A = { kind: "a"; a: number };
   type B = { kind: "b"; b: string };

   function f(x: A | B) {
     if (x.kind === "a") {
       console.log(x.a);
     }
     console.log(x.b);
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'b' does not exist on type 'A | B'.`, followed by `Property 'b' does not exist on type 'A'.` The `if` narrows `x` only inside its own block; once it ends without an `else` or a `return`, `x` reverts to `A | B`, and `b` is missing from `A`.

</details>

3. ▢ Predict whether this compiles.

   ```ts
   type Success = { kind: "success"; value: number };
   type Failure = { kind: "failure"; message: string };
   type Result = Success | Failure;

   const r: Result = { kind: "success", value: 1, message: "oops" };
   ```

<details markdown="1"><summary>Check</summary>

It does not. `error TS2353: Object literal may only specify known properties, and 'message' does not exist in type 'Success'.` The `kind: "success"` tag picks `Success` as the arm to check against, and `message` belongs to `Failure`, so it is rejected rather than silently accepted.

</details>

4. ▢ Predict the diagnostic, with its `TS` number.

   ```ts
   type Red = { color: "red" };
   type Green = { color: "green" };
   type Light = Red | Green;

   function makeLight() {
     return { color: "green" };
   }

   function show(l: Light) {}
   show(makeLight());
   ```

<details markdown="1"><summary>Hint</summary>

Ask what `makeLight`'s return type is inferred as, with no annotation and no `as const` in sight.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2345: Argument of type '{ color: string; }' is not assignable to parameter of type 'Light'.`, ending in `Type 'string' is not assignable to type '"red"'.` `color` widens to `string` in the returned object, the widening lesson 10 covered, and neither arm of `Light` accepts a plain `string` for its discriminant.

</details>

5. ▢ Does this compile?

   ```ts
   type Circle = { isSquare: false; radius: number };
   type Square = { isSquare: true; side: number };
   type Shape = Circle | Square;

   function area(s: Shape) {
     if (!s.isSquare) {
       return Math.PI * s.radius * s.radius;
     }
     return s.side * s.side;
   }
   ```

<details markdown="1"><summary>Check</summary>

Yes. `!s.isSquare` narrows `s` to `Circle` inside the `if`, just as `s.isSquare === false` would, so `s.radius` is available there, and `s` narrows to `Square` for the final `return`, where `s.side` is available.

</details>

## Real-world reps

- [ ] Find a type in your own code with two or more optional properties that are never legitimately all present or all absent together, and count how many states it admits against how many the domain actually has.
- [ ] Take a value your code reads from outside the program, such as a response body or a stored record, and check whether the field you are branching on is typed as a literal or has widened to `string` before you rely on it.
- [ ] Tomorrow: search a real project for a type with a `type`, `kind` or `status` field, delete the narrowing check at one call site, and read the diagnostic naming exactly which member is missing the property you tried to use.

## Going further

- [TypeScript Handbook: Narrowing, Discriminated unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions), the section this lesson compresses
- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html), for how the object types inside each arm are built
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
