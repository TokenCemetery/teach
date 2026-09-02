---
title: 16. The Checks strict Leaves Out
description: Six more checks worth having, one that the compiler refuses to enable, and one that does nothing at all
type: lesson
---

# Lesson 16. The Checks strict Leaves Out

**Mission link:** The tsconfig you inherit on a real codebase was somebody's judgement call, and telling a deliberate omission from an oversight means knowing exactly which checks `strict` already covers and which ones it does not.
**Primary source:** [TSConfig Reference, TypeScript](https://www.typescriptlang.org/tsconfig/)
**Prerequisites:** [Lesson 15](0015-what-strict-turns-on.md), [Lesson 14](0014-what-inference-already-knows.md)

## Warm-up

1. ▢ Lesson 14 left one hole: indexing a `string[]` gives back `string`, with no `undefined` mixed in, whether or not the index is in bounds. Lesson 15 catalogued the seven flags `strict` turns on. Is the flag that closes that hole one of the seven?

<details markdown="1"><summary>Check</summary>

No. `noUncheckedIndexedAccess` is not among `strict`'s seven flags. It has to be turned on separately, and it is the first of six such flags this lesson covers.

</details>

## Know this

### Why there is a gap at all

`strict` is not simply the checks the TypeScript team judge best; it is also a compatibility promise, because every project that already writes `"strict": true` inherits whatever joins that group with no action of its own, the moment it upgrades the compiler.
A check that would fail across a large fraction of real, working code cannot join `strict` without breaking that promise for everyone who trusted it, however good the check is at catching a genuine bug.
So the set of checks worth turning on is strictly bigger than `strict`, and reading a configuration correctly means knowing the difference rather than trusting one flag to mean "everything sensible is on".

### The six checks strict leaves out

Each of these fires only when its own flag is added, never as a side effect of `strict` alone.

| Flag | Minimal failing code | Diagnostic |
|---|---|---|
| `noUncheckedIndexedAccess` | `const s: string = a[0]` on a `string[]` | `TS2322` |
| `exactOptionalPropertyTypes` | `{ a: undefined }` assigned to `{ a?: number }` | `TS2375` |
| `noImplicitReturns` | a function with a declared return type and one branch that falls out without returning | `TS7030` |
| `noFallthroughCasesInSwitch` | a `case` with statements and no `break` | `TS7029` |
| `noPropertyAccessFromIndexSignature` | `m.anything` on `{ [k: string]: string }` | `TS4111` |
| `noUnusedLocals` | an unused `const` inside a function | `TS6133` |

The bug each one actually catches, in one line apiece: `noUncheckedIndexedAccess` catches trusting an array index that might be past the end; `exactOptionalPropertyTypes` catches writing `undefined` into a property meant to be present-with-a-value or absent, not present-and-empty; `noImplicitReturns` catches a branch that silently returns `undefined` against a declared type; `noFallthroughCasesInSwitch` catches a missing `break` that runs the next case's statements too; `noPropertyAccessFromIndexSignature` catches property-style access on a signature that promised nothing about that name, forcing the honest bracket form; `noUnusedLocals` catches the dead variable a refactor left behind.

### The three tiers of flag interaction

Six flags to consider sounds like six independent decisions, but three of them only make sense in the presence of `strictNullChecks`, and the compiler's response to getting that wrong falls into three distinct tiers worth knowing by name, because the middle one is easy to miss.

**Refused outright.** With `strictNullChecks` off, `strictPropertyInitialization` and `exactOptionalPropertyTypes` are rejected as configuration, before the compiler looks at a single line of code.

```text
error TS5052: Option 'strictPropertyInitialization' cannot be specified without specifying option 'strictNullChecks'.
error TS5052: Option 'exactOptionalPropertyTypes' cannot be specified without specifying option 'strictNullChecks'.
```

Both checks are meaningless without a distinction between present and absent, so the compiler will not let the configuration exist in an incoherent state at all.

**Accepted and silently inert.** `noUncheckedIndexedAccess` is different, and this is the sharpest fact in the lesson: it is *not* refused without `strictNullChecks`, and it also achieves nothing.

```ts
const a: string[] = ["x"];
const s: string = a[0];      // compiles, with --noUncheckedIndexedAccess and no strictNullChecks
```

The flag makes an index access `string | undefined`, and without `strictNullChecks` on, `undefined` is assignable to `string` anyway, so widening the type by adding `undefined` changed nothing that mattered.
The proof is in what a mismatched assignment names.

```ts
const a: string[] = ["x"];
const n: number = a[0];
```

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

The error names `string`, not `string | undefined`. Had the flag done anything, `undefined` would appear in that message, since a real union failing against `number` would say so; it does not appear, because there was nothing there to fail. A flag that is on, spelled correctly, and buying nothing is worse than one that is simply off, because a configuration review reads the line and marks the risk covered when nothing at all is being checked, and an absent flag at least says "not done yet" instead of lying.

**Working.** Once `strictNullChecks` is on, all three do their job: `noUncheckedIndexedAccess` gives `TS2322: Type 'string | undefined' is not assignable to type 'string'`, naming the union honestly this time; `strictPropertyInitialization` gives `TS2564: Property 'a' has no initializer and is not definitely assigned in the constructor.`; `exactOptionalPropertyTypes` gives `TS2375: Type '{ a: undefined; }' is not assignable to type 'P' with 'exactOptionalPropertyTypes: true'.`. Before trusting any flag's silence as evidence the code is fine, check what else the configuration needs for that flag to mean anything.

### What tsc --init writes

Asked to produce a sane starting configuration, the compiler's own `tsc --init` writes `"strict": true` and then reaches for exactly two of the six checks above, `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`, leaving `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature` and `noUnusedLocals` off.
Alongside those two it writes `verbatimModuleSyntax`, `isolatedModules`, `noUncheckedSideEffectImports`, `moduleDetection: force`, `module: nodenext`, `declaration`, `declarationMap` and `sourceMap`, which are module and emit choices lesson 21 owns; `target: esnext`, which lesson 20 owns; and `skipLibCheck` and `types: []`, which lesson 19 owns along with the rest of the file. None of them are checking flags, which is why they are outside this lesson's question.
Read the two it picked as the team's own answer to this lesson's question: both are checks that are meaningless, not merely weaker, without `strictNullChecks`, so writing them into a starter file is also an implicit insistence that `strictNullChecks` is not optional.

### Adopting a check on a codebase that already exists

The practical move is to turn one flag on, run the compiler, and read the resulting count of new diagnostics as a decision, rather than switching all six on together and reverting whichever one produced too much noise to triage before the next release.
`noUnusedLocals` is usually the gentle one on real code: a dead variable is a dead variable, and the fix is almost always deletion, with no design judgement required.
`noUncheckedIndexedAccess` is usually the one that produces the largest count, and honestly the one teams turn on and quietly revert, because every array or object index access becomes a decision between a bounds check, a fallback value, or a narrowing, and a codebase with hundreds of such accesses does not resolve that in an afternoon.

## Practice

1. ▢ Predict the diagnostic, with its `TS` number, for this configuration attempt.

   ```json
   { "compilerOptions": { "strict": false, "exactOptionalPropertyTypes": true } }
   ```

<details markdown="1"><summary>Check</summary>

`error TS5052: Option 'exactOptionalPropertyTypes' cannot be specified without specifying option 'strictNullChecks'.`. The configuration itself is rejected before any file is checked.

</details>

2. ▢ Under `--strict false --noUncheckedIndexedAccess` on `const a: string[] = ["x"]`, predict the outcome of `const s: string = a[0]`, then of `const n: number = a[0]`, and say what the second one's diagnostic proves about the first.

<details markdown="1"><summary>Hint</summary>

Ask what type the second diagnostic names, and whether `undefined` appears in it.

</details>

<details markdown="1"><summary>Check</summary>

The first compiles. The second fails with `TS2322: Type 'string' is not assignable to type 'number'.`, naming `string` rather than `string | undefined`. That proves the flag added nothing: had it worked, the type would have been the union, and the message would have said so.

</details>

3. ▢ Predict the diagnostic, with its `TS` number, for a `case` that runs a statement and has no `break` before the next `case`, under `noFallthroughCasesInSwitch`.

<details markdown="1"><summary>Check</summary>

`TS7029: Fallthrough case in switch.`. Only a `case` that has both statements of its own and no `break` triggers it; an empty case falling through to the next is a common idiom and is exempt.

</details>

4. ▢ `const m: { [k: string]: string } = { x: "y" }; console.log(m.anything);` compiles under plain `strict`. Predict the diagnostic, with its number, once `noPropertyAccessFromIndexSignature` is added, and what you would have to write instead.

<details markdown="1"><summary>Check</summary>

`TS4111: Property 'anything' comes from an index signature, so it must be accessed with ['anything'].`. Writing `m["anything"]` compiles, because the bracket form reads honestly as an unchecked guess about a key, where the dot form disguises it as a declared property.

</details>

5. ▢ A team enables all six checks from this lesson in a single commit against a codebase with no history of any of them, and reverts within the week. Which flag most likely produced the diagnostic count nobody could clear in time, and why is that the same flag people give up on rather than the one that is refused outright or does nothing?

<details markdown="1"><summary>Check</summary>

`noUncheckedIndexedAccess`. Unlike `strictPropertyInitialization` or `exactOptionalPropertyTypes`, it is not refused, and unlike its inert form without `strictNullChecks`, it works exactly as designed once that flag is already on, which most real codebases have had for years. Every array and object index access becomes `T | undefined`, and clearing that means visiting each one, so its diagnostic count is often the largest of the six and the least mechanical to fix.

</details>

## Real-world reps

- [ ] Open a real `tsconfig.json` you have access to and list which of this lesson's six checks are already on, and which of the remaining ones would be refused outright if `strictNullChecks` were ever turned off.
- [ ] Turn on `noUnusedLocals` against one real project's build and read the diagnostic count before deciding whether to keep it committed.
- [ ] Tomorrow: turn on `noUncheckedIndexedAccess` against one real file for five minutes, note the diagnostic count, and check whether `strictNullChecks` was already on there, since that count is the only way to tell whether the flag did anything at all.

## Going further

- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/#noUncheckedIndexedAccess): the option's own entry, with the other five one click away in the same reference
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/#exactOptionalPropertyTypes): worth reading in full once, since one sentence here compresses a longer explanation with more examples
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
