---
title: 14. What Inference Already Knows
description: Where inference reaches, so that writing an annotation means something when you do
type: lesson
---

# Lesson 14. What Inference Already Knows

**Mission link:** A codebase where every local is annotated is a codebase where nobody can tell which annotation was load-bearing, which is the opposite of what an annotation is for.
**Primary source:** [Effective TypeScript, Dan Vanderkam](https://effectivetypescript.com/)
**Prerequisites:** [Lesson 13](0013-function-types.md), [Lesson 10](0010-unions-and-literal-types.md)

## Warm-up

1. ▢ Lesson 10 showed `let s = "hello"; const t: "hello" = s;` failing, and `const s = "hello"; const t: "hello" = s;` compiling. What changed between them?

<details markdown="1"><summary>Check</summary>

`let` widens its initialiser to the primitive type, `string`, because it might be reassigned. `const` cannot be reassigned, so the compiler keeps the literal type, `"hello"`.

</details>

## Know this

Every lesson since 8 has been about reading a type once written down. This one is about when writing one down is worth it, since inference already covers most of a program.

### Five things inference already gets right

```ts
const a = [1, "x"];        // (string | number)[]

const b = [];
b.push(1);                  // fine, evolves to number[]

const o = { n: 1, s: "x" };
o.n = 5;                     // fine: widens and stays mutable, like lesson 10's `let`

function f(x: boolean) {
  return x ? 1 : "x";        // inferred: string | number, a union across branches
}

declare function each(xs: string[], cb: (x: string) => void): void;
each(["a"], x => {
  const n: number = x;       // error TS2322: Type 'string' is not assignable to type 'number'
});
```

The last error is the proof: `x` carries no annotation, yet the compiler knew it was `string`, from `each`'s declared parameter. This is **contextual typing**, the mechanism lesson 13 relied on for a callback needing no type of its own.

### The cost of annotating what inference already has

**It goes stale.** An annotation is a claim made once. The initialiser can change under it while the annotation sits there, unchanged and now wrong; an inferred type is recomputed on every check.

**It can be wider than the inferred type, and wider throws information away.**

```ts
const inferred = [1, "x"];
inferred.push(true);         // error TS2345: Argument of type 'boolean' is not assignable to parameter of type 'string | number'

const annotated: any[] = [1, "x"];
annotated.push(true);        // compiles: the mistake is invisible
```

Nobody writes `any[]` and means it, but `const kind: string = "a"` from lesson 10 is the same mistake in a shape people write constantly: the literal type `"a"`, exactly what a caller expecting `"a" | "b"` needs, is destroyed by an annotation that looks harmless. Inference would have kept `"a"`; the annotation threw it away.

**It hides the annotation that matters.** If every local carries a type, the load-bearing one cannot stand out from the decorative ones.

### Where inference genuinely cannot reach

Inference works from an initialiser, a return statement, or a calling context. Take those away and it has nothing to work from.

**Parameters have no initialiser.** A parameter is a promise to every future caller, which is why lesson 8's `TS7006` fires under `strict` the moment one is left bare:

```ts
function greet(name) {          // error TS7006: Parameter 'name' implicitly has an 'any' type
  return "hi " + name;
}
```

**An empty collection you intend to fill with something specific.** The evolving-array trick above only works while the compiler watches every push in the same scope. Once that is not true, an annotation states the intent instead of hoping the pushes agree.

**A value whose inferred type is not the one you mean to publish**, wider or narrower. `const kind: string = "a"` above is the wider case; the narrower case is deliberate, annotating `number | undefined` when the current initialiser only ever produces `number`, because the published contract will widen later.

**A return type you want checked against your intent, rather than derived from your implementation.** A judgement call, turning on whether the function's body is the thing you trust or the thing you are verifying.

```ts
function parse(s: string): number {
  const n = Number(s);
  if (Number.isNaN(n)) return undefined;   // error TS2322: Type 'undefined' is not assignable to type 'number'
  return n;
}
```

Without `: number`, this compiles: the inferred return type would simply be `number | undefined`, matching the body. With it, the annotation states the promise and the compiler catches the branch that breaks it. Annotate when the signature is a contract other code depends on; leave it inferred when the body is obviously right.

### The rule to leave with

**Annotate boundaries, let bodies infer.** A parameter is a boundary, since nothing upstream tells the compiler what it will be. An exported signature is a boundary, since everything downstream depends on it holding after the implementation changes. A local, almost always, is not: it has an initialiser right next to it, and the compiler reads that as well as you can.

### Closing stage 2, and one hole before stage 3

Lessons 8 to 13 gave vocabulary: read a type, predict an assignability verdict, narrow a union, tell a helpful annotation from a decorative one. This lesson is the payoff: "inference already has this" is checkable, not a guess, only once that vocabulary is in place.

One hole to carry forward. `noUncheckedIndexedAccess` is not part of `strict`, so indexing an array gives the element type with no `undefined` mixed in, in bounds or not:

```ts
const a: string[] = ["x"];
const s: string = a[0];      // compiles
const s2: string = a[99];    // also compiles, and is undefined at runtime
```

Inference is only as sound as the checks that are on, and `strict` is only the subset judged safe to default to. Stage 3 stops treating that default as fixed and configures the rest, starting here.

## Practice

1. ▢ Predict whether this compiles, and what type `a` is inferred as.

   ```ts
   const a = [1, 2, "x", true];
   ```

<details markdown="1"><summary>Check</summary>

Compiles, as `(string | number | boolean)[]`, the union of every element's type.

</details>

2. ▢ Predict the diagnostic, including its `TS` number.

   ```ts
   const rows: any[] = [1, 2, 3];
   rows.push("oops");
   const total: number = rows.reduce((a, b) => a + b, 0);
   ```

<details markdown="1"><summary>Hint</summary>

Ask what the annotation `any[]` gave up compared with letting `[1, 2, 3]` infer its own type.

</details>

<details markdown="1"><summary>Check</summary>

No diagnostic, which is the problem: `any[]` disabled checking on every element, so pushing a string and reducing as `number` both slip past. Without the annotation, `rows` would have inferred `number[]`, and `push("oops")` would have failed with `TS2345`.

</details>

3. ▢ A function parameter is written `(cb) => cb()` with no annotation anywhere in sight and no error. Why does that compile under `strict`, given that lesson 8 said an unannotated parameter is `TS7006`?

<details markdown="1"><summary>Check</summary>

Only if `cb` is contextually typed, meaning this arrow is being passed somewhere that declares its parameter's type, the same mechanism as `each`'s callback above. A bare top-level `function f(cb) { cb() }` would still be `TS7006`.

</details>

4. ▢ Which of these two versions would you annotate, and why?

   ```ts
   // a
   function double(n: number) { return n * 2; }

   // b
   export function fetchUser(id: string) { /* ... */ }
   ```

<details markdown="1"><summary>Check</summary>

`fetchUser`, the exported one. Its signature is a boundary other modules depend on, so its return type should be a contract checked against the implementation, not a fact the implementation happens to produce. `double` is a local helper small enough to trust, and a return type there would only restate what `n * 2` already tells the compiler.

</details>

5. ▢ Predict the outcome of each line.

   ```ts
   const items: string[] = ["a", "b"];
   const first: string = items[0];
   const tenth: string = items[9];
   ```

<details markdown="1"><summary>Check</summary>

Both compile under plain `strict`. `items[9]` is out of bounds and `undefined` at runtime, but its type is still `string`, because `noUncheckedIndexedAccess` is not one of the checks `strict` turns on. That hole is stage 3's to close.

</details>

## Real-world reps

- [ ] Find one local variable already annotated with exactly what its initialiser would infer on its own. Delete the annotation and confirm nothing changes.
- [ ] Find one exported function with no return type written down. Add one, and see whether the compiler still agrees, or whether the annotation surfaces a branch that breaks the promise.
- [ ] Tomorrow: pick one array index read in real code and ask whether it checked the length first, or is trusting a type that `noUncheckedIndexedAccess` would have refused to give it.

## Going further

- [TypeScript Handbook, Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html): the handbook's own account of inference against annotation
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/#noUncheckedIndexedAccess): `noUncheckedIndexedAccess`, the hole this lesson names and stage 3 closes
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
