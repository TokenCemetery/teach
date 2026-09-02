---
title: 35. When the Declaration Lies
description: The compiler believes the declaration and the runtime has never heard of it
type: lesson
---

# Lesson 35. When the Declaration Lies

**Mission link:** A declaration you did not write is a promise you inherit, and owning a codebase means knowing exactly how much that promise is worth before a caller pays for it at run time.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 34](0034-declaration-files.md), [Lesson 11](0011-structural-assignability.md)

## Warm-up

1. ▢ Lesson 34 called a declaration file a promise the compiler cannot audit against the implementation it describes. If that promise names the wrong type, what, precisely, checks it before the program runs?

<details markdown="1"><summary>Check</summary>

Nothing. The compiler takes the declaration's word for the shape of a value it never inspects against the implementation, and by run time nothing remains, as lesson 29 established, to notice the mismatch either. This lesson shows exactly what that costs and where the belief that some flag might catch it goes wrong.

</details>

## Know this

### The demonstration

A tiny untyped library ships as plain JavaScript:

```js
// node_modules/legacy-thing/index.js
exports.shout = function shout(s) { return s.toUpperCase(); };
```

Someone writes a declaration for it by hand and gets one detail wrong:

```ts
// legacy-thing.d.ts
declare module "legacy-thing" {
  export function shout(s: string): number;
}
```

The implementation returns a shouted string. The declaration claims a number. A caller trusts the declaration, because trusting it is the entire point of writing one:

```ts
// main.ts
import { shout } from "legacy-thing";

const n: number = shout("hi");
console.log(n.toFixed(2));
```

Run `tsc --noEmit` under `strict` and this project reports zero errors, verified. `n` is typed `number`, `shout` returns `number` as far as the compiler can see, and `n.toFixed(2)` is a method every `number` has, so the chain checks out on paper. Compile it for real and run the output, and the paper stops mattering:

```text
TypeError: n.toFixed is not a function
```

That is the exact message, verified against the emitted JavaScript. Look at what actually shipped:

```js
const n = (0, legacy_thing_1.shout)("hi");
console.log(n.toFixed(2));
```

No trace of `number` survives, since lesson 29 already established that types are gone by run time. What runs is a call returning a shouted string, assigned to a variable, then asked for a method strings do not have. The compiler signed off on a program that no longer exists by the time anything goes wrong.

### The same fact the arc has been circling since lesson 2

This is not a new failure mode. It is the oldest one in the arc, arriving somewhere it can finally hurt. Lesson 2 showed that a type is a claim checked at compile time and gone by run time. Lesson 29 established that nothing survives to notice a broken claim once running starts. Lesson 11 named the reason the compiler let this one through: TypeScript declares soundness a non-goal, trading proof for productivity. A declaration is that same claim, written once, in a file the compiler treats as ground truth rather than as something to verify. The difference is blast radius: an ordinary bug is wrong about one function's own body, caught where that body and its callers are both in view, while a declaration is trusted at every call site that imports the module it describes, so one wrong line in one `.d.ts` file is one lie told to every caller at once.

### skipLibCheck does not help, and most people believe it does

The obvious reflex, hearing that a `.d.ts` file can be wrong, is to reach for the flag lesson 19 introduced: `skipLibCheck`. Verified directly: with the lying declaration above in place, this project reports zero errors with the flag `false`, and zero with it `true`. Nothing changes, because the flag never answered the question it sounds like it answers. `skipLibCheck` controls whether the compiler type-checks the *inside* of declaration files, meaning whether a `.d.ts` is internally consistent with itself. It says nothing about whether a declaration's claim matches the JavaScript it describes, because the implementation is untyped by definition, which is the entire reason a declaration exists. Reaching for this flag expecting it to audit truth rather than internal consistency is a common and expensive misunderstanding: it has never been in the business of checking whether a declaration tells the truth.

### How to distrust a declaration in practice

Since nothing built into the compiler will do this for you, distrust has to be a habit, and it starts with recognising the signals worth acting on.

- A dependency whose `@types` package versions independently of the library itself, since that declaration is written and updated by someone other than the library's author.
- A declaration checked against a different major version than the one actually installed, which has had every chance to drift since, particularly across a major bump.
- An `any` inside a declaration you rely on, which is a place the type system has already, silently, stopped checking on your behalf.
- A runtime failure whose type said it could not happen, this lesson's exact shape, which is evidence that some declaration between you and that value was wrong.

None of these prove a declaration is false; they are reasons to check rather than to rewrite. Three responses exist, in order of preference. First, treat the dependency's output the way lesson 31 taught: as an edge, parsed there, so the check and the type come from one place rather than an unaudited claim. Second, if a full parse is more than the call site needs, narrow what you consume rather than trusting the whole declared shape; two fields read off a return value is a smaller promise than trusting all five the declaration claims. Only when neither is practical, patch the declaration itself, with a comment saying why and which version it was checked against, so the next reader knows the patch is owed a recheck rather than assumed permanent.

### The rule that ties the stage together

Line them up: a declaration, a hand-written assertion, a type predicate whose body lesson 32 showed is never checked against its own claim, and a cast written with `as`, are one category wearing four syntaxes, claims the compiler records and nothing afterwards verifies. A parse is the only thing this stage taught that is not in that category, because a parse is a runtime check that produces the type, rather than a type standing in for one. That gives the stage one boundary: wherever a claim is the last thing standing between your program and a value, put a check there instead. The discipline is a habit rather than a rule to recite, since the mistake looks the same whether it is a lying declaration, an unearned assertion, or a predicate that always returns `true`.

### Closing stage 5

Lessons 29 to 34 built one capability in six pieces, and this lesson's demonstration is where all six meet at once. Lesson 29 explained erasure, the reason the declaration above was believed instead of tested. Lesson 30 inventoried where a program meets the outside world. Lesson 31 showed how to parse at each edge so the check and the type come from one declaration. Lessons 32 and 33 gave you a way to tell a real check from a claim dressed as one, and a way to put a failure where a caller cannot ignore it. Lesson 34, and this lesson closing it, gave you a declaration file for what it is: sometimes reliable, sometimes exactly the claim this lesson just watched fail, worth exactly as much as the evidence behind it and no more. The stage's completion criterion is met: no value enters your program unvalidated, and no assertion in it is load-bearing. Stage 6 turns from defending the program against what arrives to designing types that serve the callers who use what you export.

## Practice

1. ▢ A declaration claims `function parseCount(s: string): number`, and the implementation is `function parseCount(s) { return s.length > 0 ? s : undefined; }`. A caller writes `const c: number = parseCount(""); console.log(c + 1);`. Predict whether the project compiles, and predict the value logged, if any.

<details markdown="1"><summary>Check</summary>

Compiles with zero errors, for the same reason as this lesson's demonstration: the declaration is believed rather than checked. At run time `parseCount("")` returns `undefined`, since the empty string fails the length check, and `undefined + 1` evaluates to `NaN`, so `console.log` prints `NaN`. No `TypeError` this time, which is the sharper lesson: a lying declaration does not always crash loudly, and a silent `NaN` is worse, since nothing points back at where it started.

</details>

2. ▢ Someone on your team adds `"skipLibCheck": true` to `tsconfig.json` specifically to catch declarations like the one in this lesson before they ship. Predict what happens to the compile of this lesson's exact three files, and say what the flag actually would catch.

<details markdown="1"><summary>Check</summary>

No change: the project still reports zero errors, verified both ways earlier in this lesson. `skipLibCheck` checks a declaration file's own internal consistency, not whether it matches the implementation it has no access to. The plan does not work, and the fix is not a flag but one of the three responses this lesson gave: parse the dependency's output, narrow what is consumed, or patch the declaration with a comment.

</details>

3. ▢ A dependency's `@types` package is at major version 3 while the library itself just released major version 5. A colleague argues this is fine because the code compiles with no errors. What is wrong with that argument?

<details markdown="1"><summary>Hint</summary>

Ask what "compiles with no errors" was actually able to check, given what this lesson showed the compiler has access to.

</details>

<details markdown="1"><summary>Check</summary>

A clean compile is exactly what this lesson's demonstration also produced, and it proved nothing about whether the declaration matches the library. An `@types` package two majors behind is a strong signal the declaration was written against an API that has since changed: renamed exports, changed return types, functions removed that the old declaration still claims exist. Zero compiler errors is the one piece of evidence this lesson showed cannot distinguish a true declaration from a false one.

</details>

4. ▢ A declaration for a dependency claims a function returns `{ id: string; name: string; email: string; role: string; permissions: string[] }`, but your code only ever reads `id` and `name` off the result. Per this lesson, which is the safer response: trusting the whole declared shape, or narrowing to the two fields you actually use?

<details markdown="1"><summary>Check</summary>

Narrowing to `id` and `name`. Trusting the full five-field shape means standing behind three claims your code never exercises and so never has a reason to have noticed are wrong; narrowing shrinks the promise to the two fields you can see used correctly. A full parse is stronger still, but where that is more than the call site needs, narrowing is the cheaper correct move, ahead of patching the declaration.

</details>

5. ▢ Name the one thing in this stage that is not in the same category as a declaration, an assertion, and a type predicate, and say what makes it different.

<details markdown="1"><summary>Check</summary>

A parse. A declaration, an assertion, and a type predicate are all claims the compiler records and nothing afterwards verifies, which is why a wrong one compiles clean, as this lesson showed for a declaration and lesson 18 showed for an assertion. A parse is a runtime check that produces the type from the check's own result, so the type and the verification come from the same place.

</details>

## Real-world reps

- [ ] Find one `.d.ts` file, hand-written or from an `@types` package, that a project you work in depends on, and check whether its version tracks the library's or moves on its own schedule.
- [ ] Pick one dependency call your code trusts without a parse, list every field the declaration claims against every field your code actually reads, and note how much smaller the second list is.
- [ ] Tomorrow: reread this stage's completion criterion, no value enters your program unvalidated and no assertion is load-bearing, against one file you own, and write down the one edge that still fails it.

## Going further

- [Handbook, Declaration Files, introduction](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html): what a declaration promises and who is expected to keep that promise true
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/): the exact scope of `skipLibCheck` and every other flag this stage has touched
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
