---
title: 27. satisfies
description: Check a value against a type without letting the type replace what you wrote
type: lesson
---

# Lesson 27. satisfies

**Mission link:** Owning a codebase means writing configuration objects and constants the compiler checks without throwing away the exact information the rest of the code reads back out of them.
**Primary source:** [TypeScript 4.9 Release Notes, Microsoft](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
**Prerequisites:** [Lesson 18](0018-an-assertion-is-not-a-check.md), [Lesson 14](0014-what-inference-already-knows.md)

## Warm-up

1. ▢ Lesson 14 showed `const kind: string = "a"` throwing away the literal type `"a"` inference would have kept, and lesson 18 closed by naming a form that checks a value against a type without doing that. Guess: what would such a form give up compared with an annotation, and what would it keep?

<details markdown="1"><summary>Check</summary>

Nothing about the checking: it still rejects a value that does not match the type, exactly as an annotation does. It gives up the annotation's side effect of replacing the expression's own type with the annotated type; it keeps whatever type the value would have inferred alone, narrower than the annotation whenever the annotation names something wider, a union say. That form is `satisfies`.

</details>

## Know this

### Two questions, not one

A type near a value answers up to two separate questions, and keeping them separate is what makes the rest of this lesson easy. First: does the compiler check the value against the type? Second: does the value keep the type inference would have given it, rather than take on the written type instead? An annotation answers yes, then no: `const c: Cfg = { host: "a", port: 1 }` checks the literal, then makes `c`'s type `Cfg` itself. An assertion answers no to the first question, since lesson 18 showed `as` compiling even when a value is missing members the type claims. `satisfies` is the missing combination: yes, yes.

### The same value, three ways

Take one type and one value and run it through all three forms.

```ts
type Cfg = Record<string, string | number>;
```

| Form | Checked against `Cfg`? | Inferred type kept? | Evidence |
|---|---|---|---|
| `const c: Cfg = { host: "a", port: 1 }` | yes | no | `const p: number = c.port` fails |
| `const c = { host: "a", port: 1 } satisfies Cfg` | yes | yes | the same line compiles |
| `const c = { host: "a", extra: 1 } as Cfg` | no | n/a | compiles, though `extra` is not in `Cfg` |

The first row's failure is exact:

```ts
const c: Cfg = { host: "a", port: 1 };
const p: number = c.port;
```

```text
error TS2322: Type 'string | number' is not assignable to type 'number'.
```

The annotation checked the literal against `Cfg` correctly, then threw the result away: `c`'s type is `Cfg` itself, so every property reads back as the whole union regardless of which member it actually holds. Swap the annotation for `satisfies` and change nothing else:

```ts
const c = { host: "a", port: 1 } satisfies Cfg;
const p: number = c.port;
```

This compiles. `c` is checked against `Cfg` exactly as before, so a misspelt key or a `boolean` still fails; what changed is `c`'s type afterwards, not `Cfg` but whatever the literal infers alone, `{ host: string; port: number }`. `port` is `number`, what the literal is, not the widest thing `Cfg` allows.

The `as` row is lesson 18's territory: it does not check at all, so `extra` slips through even though `Cfg` says nothing about one.

### Still a check, not a softer one

"Keeps the narrower type" does not mean "checks less strictly"; both cases below refuse `satisfies` exactly as they would refuse an annotation.

```ts
const bad = { host: "a", flag: true } satisfies Cfg;
```

```text
error TS2322: Type 'boolean' is not assignable to type 'string | number'.
```

It also runs lesson 11's excess property check, the one `as` is known to silence, on a type closed enough to have one:

```ts
interface Cfg2 {
  host: string;
  port: number;
}
const bad2 = { host: "a", extra: 1 } satisfies Cfg2;
```

```text
error TS2353: Object literal may only specify known properties, and 'extra' does not exist in type 'Cfg2'.
```

That second diagnostic is the sharpest reason to prefer `satisfies` over `as`. The two read almost the same in a diff, a value on the left, a type on the right, but one is a check a stray member fires against, the other a promise nobody verified.

One case buys nothing: a value already typed `any` stays `any` on the other side of `satisfies`, since `any` is compatible with everything and has no narrower type to keep. `raw satisfies Config` on `JSON.parse` output compiles and lets any member read back unchecked, exactly like the `as` it replaced; a value that arrived as `any` needs validating, stage 5's problem, not a different keyword in front of it.

### Where it earns its keep

**Deriving a union from the keys you actually wrote.** `Record<string, string | number>` says nothing about which keys exist, so an annotated `c: Cfg` gives `keyof typeof c` the useless type `string`. `satisfies` keeps the literal's own keys:

```ts
const c = { host: "a", port: 1 } satisfies Cfg;
type Key = keyof typeof c;   // "host" | "port"
const k: Key = "host";       // compiles
const bad: Key = "anything"; // error TS2322
```

**A lookup table whose value types stay precise per key**, not widened to the union every value is allowed to be:

```ts
type IconName = "circle" | "square" | "triangle";
const styles = {
  primary: "circle",
  secondary: "square",
} satisfies Record<string, IconName>;
const p: "circle" = styles.primary; // compiles
```

Annotate the same object `: Record<string, IconName>` instead and `styles.primary` becomes the full `IconName` union, so `const p: "circle" = styles.primary` fails with `TS2322: Type 'IconName' is not assignable to type 'circle'.`, since `"square"` is also possible as far as the annotation is concerned.

**A constant checked against a plain interface without losing what it actually holds.** Not a `Record` trick; this works against any named type with a union-typed member.

```ts
interface Ticket {
  status: "open" | "closed" | "pending";
  owner: string;
}
const ticket = { status: "open", owner: "alice" } satisfies Ticket;
const s: "open" = ticket.status; // compiles
```

Annotate `ticket: Ticket` instead and the same line fails with `TS2322: Type '"closed" | "open" | "pending"' is not assignable to type '"open"'.`, because the annotation makes `ticket.status` the full union. Lesson 10's widening material is why a literal type is worth keeping: the difference between "this string" and "some string", which an unnecessarily wide annotation erases.

### Where it does not reach

`satisfies` checks an expression, `expr satisfies T`, and cannot appear anywhere an annotation goes. In place of a parameter's type:

```ts
function f(x satisfies Cfg) {}
```

```text
error TS1005: ',' expected.
```

In place of a return type:

```ts
function makeTicket(): satisfies Ticket {
  return { status: "open", owner: "alice" };
}
```

```text
error TS1144: '{' or ';' expected.
```

A parameter and an exported return type are the boundaries lesson 14 named, where the declared type is what the rest of the program should see. `satisfies` is for the values flowing through those boundaries, never the boundaries themselves.

### The rule to leave with

Annotate when you want the value to become the wider, written type, right at a parameter or an exported return type, where callers depending on the boundary matter more than what one call site passes. Reach for `satisfies` when you want the value checked and still want to keep what it actually is: a configuration object, a lookup table, any constant you would otherwise annotate and regret. Fall back to `as` only once you hold information the compiler genuinely cannot get from the code, which lesson 18 already argued should be rare and commented.

## Practice

1. ▢ Predict whether this compiles, and if it does, what `t`'s value is checked against.

   ```ts
   type Limits = Record<string, number | boolean>;
   const limits = { timeout: 5000, retry: true } satisfies Limits;
   const t: number = limits.timeout;
   ```

<details markdown="1"><summary>Check</summary>

Compiles. `limits` was checked against `Limits`, and `satisfies` kept the literal's own inferred type, `{ timeout: number; retry: boolean }`, so `limits.timeout` is `number` rather than `number | boolean`.

</details>

2. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   type Limits = Record<string, number | boolean>;
   const limits = { timeout: "5s", retry: true } satisfies Limits;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string' is not assignable to type 'number | boolean'.` `satisfies` rejects it exactly as an annotation would; switching forms did not weaken the check.

</details>

3. ▢ A teammate writes `const routes: Record<string, Route> = { home: {...}, settings: {...} }` and wants `keyof typeof routes` to be `"home" | "settings"`. Predict what it actually is with the annotation left as written, and say what single change fixes it.

<details markdown="1"><summary>Hint</summary>

Ask what `keyof` sees when the declared type has an index signature, versus when it sees the object literal's own shape.

</details>

<details markdown="1"><summary>Check</summary>

`keyof typeof routes` is `string`, because `keyof Record<string, Route>` is `string` regardless of which keys the literal has; the annotation replaced the literal's type before `keyof` ever ran. Changing `: Record<string, Route> =` to `satisfies Record<string, Route>` fixes it: the object keeps its own shape, `{ home: Route; settings: Route }`, and `keyof typeof routes` becomes `"home" | "settings"`.

</details>

4. ▢ Predict whether this compiles, and if it does not, name the diagnostic.

   ```ts
   interface Ticket {
     status: "open" | "closed" | "pending";
     owner: string;
   }
   function assign(t satisfies Ticket, owner: string) {}
   ```

<details markdown="1"><summary>Check</summary>

Does not compile: `error TS1005: ',' expected.` `satisfies` checks an expression, and a parameter has no expression to check, only a name and a type position; the fix is an ordinary annotation, `t: Ticket`.

</details>

5. ▢ A pull request reads `const config = JSON.parse(text) satisfies Config;` with no further check. The author says `satisfies` was chosen over `as` to keep the check `as` would have silenced. Is that correct?

<details markdown="1"><summary>Check</summary>

Wrong. `JSON.parse` returns `any`, and `satisfies` against an `any` expression passes trivially, since `any` is compatible with every type and has no narrower inferred type to keep. `config` is still `any` afterwards, exactly as with `as Config`, and every member read off it is unchecked. `satisfies` only does work when the expression has a real inferred type to compare and keep; a value that crossed a boundary as `any` needs validating against `Config`'s shape, stage 5's material, not a different assertion-shaped keyword in front of it.

</details>

## Real-world reps

- [ ] Find a `const x: T = { ... }` where `T` is a `Record` or has a union-typed member, switch it to `satisfies T`, and check whether a later read of `x` narrows more than before.
- [ ] Find an `as T` on an object literal and try `satisfies T` in its place; if it still compiles, `as` was only ever hiding the excess property check for nothing.
- [ ] Tomorrow: find a lookup table or configuration object annotated with its container type directly, and ask whether `keyof typeof` on it gives the keys you wrote or only `string`.

## Going further

- [TypeScript 4.9 Release Notes, the satisfies operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html): the release that introduced it, with the colour-palette example the keyword was built for
- [Handbook, Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html): the excess property check `satisfies` still runs, covered in full where lesson 11 first taught it
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
