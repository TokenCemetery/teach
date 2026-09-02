---
title: 31. Parsing Instead of Asserting
description: One declaration that produces both the runtime check and the static type
type: lesson
---

# Lesson 31. Parsing Instead of Asserting

**Mission link:** Owning a codebase means the check that runs against a value and the type the rest of the program trusts have to be the same fact rather than two people's promises to keep two files in step, and a schema is what makes that structural instead of a matter of discipline.
**Primary source:** [Zod documentation](https://zod.dev/)
**Prerequisites:** [Lesson 30](0030-unknown-at-the-edge.md), [Lesson 18](0018-an-assertion-is-not-a-check.md)

## Warm-up

1. ▢ Lesson 30 left you with a list of every edge in a program and an `unknown` sitting at each one. Given a payload arriving at one such edge as `unknown`, and a hand-written type describing the shape you expect it to have, what exactly has to happen before the program may treat the value as that type, and what does an assertion buy you if you skip that step?

<details markdown="1"><summary>Check</summary>

Something has to test the value against the shape the type describes, field by field, before anything narrows it to that type; lesson 18 already covered this ground and nothing here moves it. An assertion buys nothing at that boundary except silence: it tells the compiler the value is that shape without anyone having looked, so `unknown` ends up exactly as unverified as it was before, only now with no diagnostic left to warn about it.

</details>

## Know this

### The trouble with two declarations

Before reaching for a library, look at what happens without one. Write a type for the shape you expect and write a check for it by hand, separately, and nothing keeps the two in step, because a type is a compile-time claim, gone by the time the program runs, and a check is ordinary code that happens to test some of what the type promises:

```ts
type User = { id: string; age: number; email: string };

function checkUser(x: unknown): boolean {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  return typeof o.id === "string" && typeof o.age === "number";
}

const raw: unknown = { id: "u1", age: 30 };

if (checkUser(raw)) {
  const user = raw as User;
  console.log(user.email.toUpperCase());
}
```

This compiles with no diagnostic. `checkUser` tests `id` and `age` only; nothing tests `email`, and nothing forces it to, since `User` and `checkUser` are two separate pieces of text that happen to describe overlapping ground. Run it and the gap shows up where lesson 18 said an assertion's cost always shows up, later and somewhere else:

```text
TypeError: Cannot read properties of undefined (reading 'toUpperCase')
```

`raw` never had an `email` field, `checkUser` never looked for one, and `as User` told the compiler to believe it anyway. Add a field to `User` next month, or take one away, and `checkUser` still compiles and still says nothing, because the compiler has no way to know the two declarations are supposed to agree.

### One declaration, not two

A schema closes that gap by making the check and the type read off the same value rather than two independent pieces of text:

```ts
import { z } from "zod";

const User = z.object({ id: z.string(), age: z.number().int().min(0) });
type User = z.infer<typeof User>;
```

`User` on the left is a schema, a runtime value that knows how to validate an object against the shape it describes. `type User = z.infer<typeof User>` reads the static type back off that same value rather than restating the shape a second time; nobody writes `{ id: string; age: number }` anywhere else, so there is nothing left that could fall out of step. Read a field the schema never validated and the identical mistake from above is caught before the program runs, rather than at run time:

```ts
const raw: unknown = { id: "u1", age: 30 };
const user = User.parse(raw);
console.log(user.email.toUpperCase());
```

```text
error TS2339: Property 'email' does not exist on type '{ id: string; age: number; }'.
```

Add `email: z.email()` to `User`'s definition and the error above disappears everywhere `user.email` is read, with no second file to update and no name to remember to keep in sync; the same edit adds `email: string` to `User` the type, in the same place, for free. That is the actual argument for a schema over a hand-written pair, not that the syntax reads shorter but that drift becomes impossible by construction, since there is only one declaration left for anything to drift from. `z.string().email()` still compiles under this release and behaves identically; `z.email()` is the current idiom and the form to reach for.

### `parse` against `safeParse`

Every schema carries both methods and both run the same check underneath; they differ only in how a failure reaches you. `.parse` returns the parsed, typed value or throws. `.safeParse` never throws; it returns a discriminated union keyed on `success`, exactly the shape lesson 22 taught, one literal property that tells you which arm you are holding:

```ts
const good = User.safeParse({ id: "u1", age: 30, email: "u1@example.com" });
console.log(good.success); // true

const bad = User.safeParse({ id: "u1", age: -1, email: "u1@example.com" });
console.log(bad.success); // false
```

Both calls ran; the first schema accepted the value and the second refused it, and `success` is a plain boolean you can branch on with the same `if` lesson 22 used on a `kind` field, no exception handling required. Which of the two to prefer, and what to do with a failure once you have one, is lesson 33's material.

### The structured failure

`safeParse`'s failing side is not a string; it is a structured object. Reading the first issue off the failed call above gives, verified verbatim:

```text
{"origin":"number","code":"too_small","minimum":0,"inclusive":true,"path":["age"],"message":"Too small: expected number to be >=0"}
```

`path` matters most here: it names, as an array of keys, exactly which field of the input failed, `age` in this case. A boundary that only knows the input was invalid cannot tell whoever sent it what to fix; one that knows the failure sits at `path: ["age"]` can turn that straight into a message next to the right field, which is why a boundary failure needs to be a structured value rather than a thrown string.

### A schema describes two types, not one

Everything so far has read one type off a schema. A schema with a `.default()` on one of its fields reads two, and the two are not the same:

```ts
const S = z.object({
  a: z.string(),
  b: z.number().optional(),
  c: z.array(z.string()).default([]),
});

type SOut = z.infer<typeof S>;
type SIn = z.input<typeof S>;
```

`SOut`, from `z.infer`, is `{ a: string; b?: number | undefined; c: string[] }`: `c` is required, because by the time a value has come out of `.parse` the default has already run and filled it in. `SIn`, from `z.input`, is `{ a: string; b?: number | undefined; c?: string[] | undefined }`: `c` is optional, because on the way in, before `.parse` runs, leaving it out is exactly what the default exists to allow. Both types accept real values the other refuses:

```ts
const out: SOut = { a: "x", c: ["y"] };
const inp: SIn = { a: "x" };
```

The gap between them is not academic. A function whose job is to receive a value on its way to being validated wants `SIn`. Annotate it with `SOut` instead and every caller who legitimately omits `c`, trusting the default to supply it, is refused:

```ts
function send(payload: SOut) {
  console.log(payload);
}
send({ a: "x" });
```

```text
error TS2741: Property 'c' is missing in type '{ a: string; }' but required in type '{ a: string; b?: number | undefined; c: string[]; }'.
```

That diagnostic looks safe, a compile error rather than a crash, but the fix people reach for under it is the real bug: hand-fill `c` at the call site, `send({ a: "x", c: [] })`, and the default now lives in two places, the schema's `.default([])` and whatever the caller guessed, with nothing keeping them equal if the schema's own default ever changes. Using `z.infer` for the type of something you are about to hand in is a real bug, and the workaround for it type-checks cleanly; the mistake stops being a diagnostic you get once that workaround is in place. `z.infer` for what a schema hands back, `z.input` for what you are allowed to hand it, is the rule that avoids this.

### Where the parse belongs

Lesson 30 named the edges: every point where a value arrives from outside the program. The parse belongs at exactly those points, once, and nowhere else. Call `.parse` where the payload first arrives and the value that comes back is fully typed and already checked, so every function it passes to afterwards receives, in one sentence, what lesson 25's brand was built for: a value whose type carries a promise that a specific check has already run, without repeating the check. If a `.parse` or `.safeParse` call turns up in the middle of a program, away from any boundary, that is a sign the boundary was drawn in the wrong place, not a reason to add another schema there; the fix is moving the validation back to where the value actually entered, and letting the typed value travel inward unassisted.

### The honest limits

A schema checks shape and whatever constraints you wrote into it, `min(0)`, a pattern `z.email()` expects, nothing more. It cannot tell you that an `id` of `"u1"` names a row that actually exists, or that an `age` of `30` is the sender's real age rather than a plausible-looking number in the wrong field; that is truth about the world, and no schema reaches it from a value's shape alone. The check also costs something real at run time: `.parse` walks the whole value, every field, every call, the price of the boundary being an actual check rather than a claim the compiler took on faith. Paying that price once, at the edge, rather than skipping it and asserting instead, is the whole difference this lesson has argued for.

## Practice

1. ▢ Predict what this prints.

   ```ts
   const User = z.object({ id: z.string(), age: z.number().int().min(0) });
   const raw: unknown = { id: "u1", age: -5 };
   const result = User.safeParse(raw);
   console.log(result.success);
   ```

<details markdown="1"><summary>Check</summary>

`false`. `age` fails `.min(0)` at `-5`, so `safeParse` returns the failing arm of the union, `{ success: false, error: ... }`, and `result.success` is that arm's literal.

</details>

2. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   const Point = z.object({ x: z.number(), y: z.number() });
   type Point = z.infer<typeof Point>;
   const p = Point.parse({ x: 1, y: 2 });
   console.log(p.z);
   ```

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'z' does not exist on type '{ x: number; y: number; }'.` `Point` only ever had two fields, on the schema and on the type read off it, so there was never a `z` to read, caught before the program runs rather than at run time.

</details>

3. ▢ Predict whether both lines compile, and say which one is legal only because of the `.default()` on `c`.

   ```ts
   const S = z.object({ a: z.string(), c: z.array(z.string()).default([]) });
   type SOut = z.infer<typeof S>;
   type SIn = z.input<typeof S>;
   const x: SOut = { a: "hi", c: [] };
   const y: SIn = { a: "hi" };
   ```

<details markdown="1"><summary>Hint</summary>

Ask which of the two types, `SOut` or `SIn`, makes `c` optional, and why a default is exactly the reason it can be.

</details>

<details markdown="1"><summary>Check</summary>

Both compile. `x` supplies `c` explicitly, which either type accepts. `y` omits `c`, legal only under `SIn`, since before `.parse` runs the default has not filled `c` in yet; `SOut` would refuse `{ a: "hi" }` with `TS2741`, as `send` did.

</details>

4. ▢ Predict whether this compiles, and if it does, predict what happens when it runs.

   ```ts
   type Account = { id: string; balance: number; currency: string };

   function checkAccount(x: unknown): boolean {
     if (typeof x !== "object" || x === null) return false;
     const o = x as Record<string, unknown>;
     return typeof o.id === "string" && typeof o.balance === "number";
   }

   const raw: unknown = { id: "a1", balance: 100 };

   if (checkAccount(raw)) {
     const acc = raw as Account;
     console.log(acc.currency.toUpperCase());
   }
   ```

<details markdown="1"><summary>Check</summary>

Compiles with no diagnostic. Fails at run time with `TypeError: Cannot read properties of undefined (reading 'toUpperCase')`: `checkAccount` never tests `currency`, `raw` never had one, and `as Account` told the compiler to believe it did anyway, the same two-declarations problem from the start of the lesson.

</details>

5. ▢ A function receives a payload on its way to being validated against the schema below. Predict the diagnostic, with its `TS` number, produced by the call beneath it.

   ```ts
   const Config = z.object({
     name: z.string(),
     retries: z.number().default(3),
   });
   type ConfigOut = z.infer<typeof Config>;

   function submit(payload: ConfigOut) {
     Config.parse(payload);
   }
   submit({ name: "job" });
   ```

<details markdown="1"><summary>Check</summary>

`error TS2741: Property 'retries' is missing in type '{ name: string; }' but required in type '{ name: string; retries: number; }'.` `submit` receives data before it has been parsed, so its parameter should have been `z.input<typeof Config>`, which leaves `retries` optional on account of the default; `ConfigOut` is the post-default type and demands a field the caller has no reason to supply yet.

</details>

## Real-world reps

- [ ] Find a boundary in your own code where a hand-written type and a hand-written check both describe the same external value, and confirm whether every field the type promises is one the check actually tests.
- [ ] Take one payload your code currently trusts through an assertion rather than a check, write a schema for its shape, and run `.safeParse` against a real sample, reading the `path` on any failure it produces.
- [ ] Tomorrow: find a schema with a `.default()` on any field in a codebase you touch, and check every place that names its type with `z.infer` for whether that place is receiving a value on its way in or reading one already validated.

## Going further

- [Basic usage, Zod documentation](https://zod.dev/basics): the primary source's own walkthrough of defining a schema, then parsing and inferring a type from it
- [Defining schemas, Zod documentation](https://zod.dev/api): the fuller schema-building API this lesson only samples, including `.default()` and the rest of the object method
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
