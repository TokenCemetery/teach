---
title: 45. The Consumer's Settings Are Not Yours
description: A strict consumer inherits a loose author's claims and has no way to notice
type: lesson
---

# Lesson 45. The Consumer's Settings Are Not Yours

**Mission link:** Publishing a package means publishing the compiler settings that produced its types along with the code, and reviewing a dependency means knowing that your own strictness cannot repair a claim someone else already made.
**Primary source:** [TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
**Prerequisites:** [Lesson 44](0044-publishing-a-type-surface.md), [Lesson 35](0035-when-the-declaration-lies.md)

## Warm-up

1. ▢ Lesson 34 established that a generated declaration cannot disagree with the implementation that produced it, which is exactly why lesson 44 recommended generating one rather than writing it by hand, and lesson 35 then showed that a hand-written declaration can lie about a value's type with nothing left at run time to notice it. Given that a generated declaration cannot disagree with its own implementation, can it still lie to a caller who imports it?

<details markdown="1"><summary>Check</summary>

Yes, and this lesson is that gap built end to end. Agreement with the implementation is a narrower guarantee than truth about what a value can be at run time: a generated declaration faithfully reports whatever the implementation's own author told the compiler the types were, and if the author's compiler settings let an unsound claim through in the first place, the generated declaration repeats that claim exactly, with the same confidence it would carry if the claim were sound.

</details>

## Know this

### The demonstration

Here is a small library, authored with `strict` turned off:

```ts
// misc-lib/src/index.ts
const store: Record<string, string> = { a: "apple" };

export function find(k: string): string {
  if (k in store) {
    return store[k];
  }
  return null;
}

export function pick(xs: string[], i: number): string {
  return xs[i];
}
```

```json
// misc-lib/tsconfig.json
{
  "compilerOptions": {
    "strict": false,
    "declaration": true,
    "outDir": "dist",
    "rootDir": "src"
  }
}
```

With `strict` off, `strictNullChecks` is off with it, as lesson 15 covered, so `null` is assignable to `string` and `find`'s `return null;` passes without complaint; separately, indexing without `noUncheckedIndexedAccess`, one of the checks lesson 16 named as excluded from `strict`, types the result `string` rather than `string | undefined`, so `pick`'s `return xs[i];` passes too. Building this project emits a declaration generated from that implementation, exactly as lesson 34 promised, and the declaration is exactly as false as the implementation allowed it to be:

```ts
// misc-lib/dist/index.d.ts
export declare function find(k: string): string;
export declare function pick(xs: string[], i: number): string;
```

Both lines are wrong. `find` can return `null`, not only `string`, and `pick` indexes an array at a caller-supplied position with no bound placed on it, so it can return `undefined`. Now consume this package from an application whose own configuration is strict in exactly the way this stage has been teaching:

```json
// app/tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```

```ts
// app/src/main.ts
import { find, pick } from "misc-lib";

const a: string = find("missing");
const b: string = pick(["x", "y"], 5);

console.log(a.toUpperCase());
console.log(b.toUpperCase());
```

Compile this project and it reports nothing, verified: zero diagnostics, with both `strict` and `noUncheckedIndexedAccess` on, and both assignments to `string` accepted without complaint. Run the emitted JavaScript and the paper stops mattering, the same way it stopped mattering in lesson 35:

```text
TypeError: Cannot read properties of null (reading 'toUpperCase')
```

`find("missing")` really does return `null`, because the key is not in the store, and `a.toUpperCase()` calls a method `null` does not have. Isolate the second call the same way and the failure mode repeats with the second false claim: `pick(["x", "y"], 5)` returns `undefined`, because the array has two elements and the call asks for the sixth, and `b.toUpperCase()` fails with `Cannot read properties of undefined (reading 'toUpperCase')`. Two functions, two false claims, one clean compile, two crashes.

### Why the consumer's strictness cannot help

The instinct is to blame the flags, since turning on `strict` and `noUncheckedIndexedAccess` in the consumer's own project was meant to catch exactly this shape of mistake, so it is worth being precise about what those flags actually govern. `noUncheckedIndexedAccess` changes how the compiler types an index expression that appears in code it is currently checking: a line such as `const y: string = xs[9];`, written directly in the consumer's own file with `xs` a `string[]`, fails to compile under that flag, with `TS2322`, because the compiler sees the index expression and knows an array index has no guaranteed bound. But `pick(["x", "y"], 5)` contains no index expression the consumer's compiler ever sees. The indexing happened inside `misc-lib`, at a moment the library's own compiler already decided how to type it, and what crosses the boundary is not an expression to retype but an already settled return type, `string`, written into a `.d.ts` file the consumer's compiler treats as ground truth. A flag that governs how an expression is typed has nothing to act on when there is no expression, only an inherited claim. That is the whole mechanism: a consumer's configuration governs the code the consumer writes, and an imported declaration is not code the consumer wrote.

### The rule for an author

State the demonstration as a rule and it reads harder than it feels while you are only thinking about your own code: your compiler settings are part of what you publish, exactly as much as the function names and the parameter types are. A library built without `strictNullChecks` publishes a declaration that is wrong in a way no consumer, however strict their own project is, can detect or defend against, because the wrongness was baked in before the declaration ever reached them. The nuance worth holding onto is that turning `strict` on in the library would not have been enough by itself: verified directly, `strict` alone catches `find`'s `return null;` as `TS2322`, since `null` is not assignable to `string`, but says nothing about `pick`, because `noUncheckedIndexedAccess` sits outside the `strict` family, exactly as lesson 16 catalogued, and has to be turned on separately even by an author who is otherwise fully strict. So the rule is not "turn strict on" but "know which flags you have not turned on, because every one of them is a claim your consumers cannot check for themselves". A `tsconfig.json` is usually treated as private, an implementation detail nobody outside the project reads; for a published package it is closer to an interface decision, deciding which claims in your declaration are backed by a check and which are backed by nothing at all.

### What a consumer can actually do

None of this is a reason to give up on a dependency's types, and a lesson that only assigns blame to authors leaves the reader with nowhere to go next time, so here is the honest order of preference. First, treat the dependency's output the way lesson 31 taught: as an edge, where a value earns its type by being checked rather than declared, so the check and the type come from the same place instead of an unaudited claim. That is the only response here that actually verifies anything; the rest reduce exposure without eliminating it. Second, where a full parse is more than the call site needs, narrow what you consume rather than trusting the declaration's whole shape, since believing that `pick` returns a `string` you then check for emptiness is a smaller promise than believing the declaration in full. Third, and only when neither is practical, patch the declaration itself, adding the `| undefined` or `| null` the author left out, with a comment naming the version checked, so the patch is visibly owed a recheck at the next upgrade rather than trusted forever. What will not work, verified again here the way lesson 35 verified it for a hand-written declaration, is `skipLibCheck`: turning it on or off around this project changes nothing, because the flag governs whether a `.d.ts` file is internally consistent with itself, not whether it matches the implementation it was generated from, and a generated declaration that is internally consistent and still false is precisely today's demonstration.

## Practice

1. ▢ A library authored with `strict: false` publishes `export declare function first(xs: number[]): number;`, whose implementation is `return xs[0];`. A consumer, compiling under `strict` and `noUncheckedIndexedAccess`, writes `const n: number = first([]); console.log(n.toFixed(1));`. Predict whether the consumer's project compiles, and predict what happens when it runs.

<details markdown="1"><summary>Check</summary>

Compiles with zero errors, for the same reason as this lesson's demonstration: `first`'s declared return type is `number`, the consumer's flags cannot retype a function they did not write, and the assignment is accepted on the declaration's word. At run time, `xs[0]` on an empty array is `undefined`, so `n` is `undefined` rather than a `number`, and `n.toFixed(1)` throws `Cannot read properties of undefined (reading 'toFixed')`.

</details>

2. ▢ Suppose `misc-lib`'s author, before publishing, turns `strict` on in the library's own `tsconfig.json` but changes nothing else. Predict which of `find` and `pick` now fails to compile inside the library, and which still compiles and still gets published with a false return type.

<details markdown="1"><summary>Hint</summary>

Ask which of the two false claims depends on `strictNullChecks`, part of the `strict` family lesson 15 covered, and which depends on `noUncheckedIndexedAccess`, the flag lesson 16 named as one `strict` leaves out.

</details>

<details markdown="1"><summary>Check</summary>

`find` now fails inside the library: `return null;` against a declared return type of `string` is `TS2322`, caught by `strictNullChecks`, which `strict` turns on. `pick` still compiles, and is still published claiming `string`, because indexing an array without `noUncheckedIndexedAccess` types the result `string`, not `string | undefined`, regardless of whether `strict` is on, since that flag is not part of the `strict` family. Turning `strict` on in the library fixes one false claim and leaves the other exactly as false as it was.

</details>

3. ▢ A teammate proposes adding `"skipLibCheck": true` to the consumer's `tsconfig.json`, specifically to catch declarations like `misc-lib`'s before they reach production. Predict what happens to this lesson's exact project, and say what the flag would actually have caught.

<details markdown="1"><summary>Check</summary>

Nothing changes: the project still reports zero errors, `skipLibCheck` true or false, verified both ways. The flag decides whether a `.d.ts` file is checked for internal consistency with itself, not whether it matches the implementation that generated it, and `misc-lib`'s declaration is internally consistent, just false. This is lesson 35's finding again, extended from a hand-written declaration to a generated one.

</details>

4. ▢ You depend on a function whose declaration claims it returns an object with five fields, and your code only ever reads two of them. A full parse at the call site is more setup than the two fields justify. Per this lesson's order of preference, what is the next best response, and why does it beat trusting the declaration's full five-field shape?

<details markdown="1"><summary>Check</summary>

Narrow to the two fields you actually use. Trusting all five means standing behind three claims your code never exercises and so has never had a reason to catch if they are wrong, exactly the position `misc-lib`'s consumer was in before running the program; narrowing to what you read shrinks the promise to what you can actually see used correctly, which is weaker evidence than a parse but stronger than believing a shape you never touch in full.

</details>

5. ▢ A colleague argues that a library's `tsconfig.json` is a private build detail with no bearing on consumers, since consumers set their own strictness. Using this lesson's rule for authors, say in one or two sentences what is wrong with that argument.

<details markdown="1"><summary>Check</summary>

A library's compiler settings decide which claims in its published declaration are backed by a check and which are not, and a consumer's own strictness governs only the code the consumer writes, not a return type already settled inside someone else's build; a `tsconfig.json` behind a published package is therefore part of the interface, not a private detail, whether or not anyone downstream ever reads it.

</details>

## Real-world reps

- [ ] Pick one dependency whose source you can read, and check whether its own `tsconfig.json` turns on `strict` and `noUncheckedIndexedAccess`, treating an absent or unreadable config as evidence rather than as nothing.
- [ ] For one function you call from that dependency, compare its declared return type against what its own implementation can actually produce, the way this lesson compared `find` and `pick` against their declarations.
- [ ] Tomorrow: pick one import in code you own that you have never checked this way, and either parse its result at the boundary the way lesson 31 taught or narrow what you read from it to only the fields your code actually uses.

## Going further

- [Handbook, Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html): what a `.d.ts` promises and whose job it is to keep the promise true
- [Node, Modules, Packages](https://nodejs.org/api/packages.html): how a package's `types` field routes a consumer to the exact declaration this lesson depended on
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
