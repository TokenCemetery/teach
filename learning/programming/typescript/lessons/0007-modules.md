---
title: 7. Modules
description: Imports are hoisted and bound live, and a file with no import or export is not a module
type: lesson
---

# Lesson 7. Modules

**Mission link:** Module resolution is where TypeScript's model, the runtime's model, and the bundler's model have to agree, and where they disagree the failure is a build error nobody can read. Understanding the runtime's rules first makes stage 3 tractable.
**Primary source:** [Node.js, Modules: ECMAScript modules](https://nodejs.org/api/esm.html)
**Prerequisites:** [Lesson 5](0005-scope-and-closures.md), [Lesson 6](0006-event-loop-and-promises.md)

## Warm-up

1. ▢ In what order does this print: `console.log("a")`, `setTimeout(cb, 0)`, `Promise.resolve().then(cb2)`?

<details markdown="1"><summary>Check</summary>

Synchronous first, then the promise reaction as a microtask, then the timer as a task.

</details>

2. ▢ Why does `items.forEach(async (i) => await f(i))` not wait?

<details markdown="1"><summary>Check</summary>

`forEach` discards the promise each callback returns, so nothing awaits them and rejections float.

</details>

## Know this

A module is a file with its own scope. Names declared in it are private unless exported, and it is evaluated **once** per program, however many times it is imported.

```ts
export const NAME = "svc";              // named export
export function run() {}
export default class Service {}         // default export, at most one

import Service, { NAME, run } from "./service.js";
import * as service from "./service.js";
import type { Config } from "./types.js";   // erased at compile time
```

### Two facts that change how you write them

**Imports are hoisted and evaluated first.** All of a module's imports are resolved and evaluated before any of its own top-level code runs, regardless of where the `import` appears in the file. So this does not work:

```ts
if (process.env.MODE === "dev") {
  import { debug } from "./debug.js";     // syntax error: not allowed here
}
const mod = await import("./debug.js");  // dynamic import: a promise, allowed anywhere
```

Dynamic `import()` is the conditional form, and it returns a promise, which is why lesson 6 came first.

**Bindings are live, not copied.** An imported name refers to the exporting module's binding:

```ts
// counter.ts
export let count = 0;
export function bump() { count++; }

// main.ts
import { count, bump } from "./counter.js";
console.log(count);     // 0
bump();
console.log(count);     // 1, the binding is shared
count = 5;              // compile error: imports are read-only
```

That is different from CommonJS, where `const { count } = require("./counter")` copies the value at that moment and never sees the increment. It is the single most common cause of "my counter is stuck at zero" in a mixed codebase.

### Modules are strict, and always deferred

Every module is in strict mode automatically, so `this` at the top level is `undefined` rather than the global object, and undeclared assignment throws. Module code is also always deferred: it never blocks parsing the way a classic script does.

### CommonJS against ES modules

| | CommonJS | ES modules |
|---|---|---|
| syntax | `require`, `module.exports` | `import`, `export` |
| resolution | synchronous, at call time | asynchronous, before evaluation |
| bindings | value copied at `require` | live binding |
| conditional loading | `require` anywhere | `import()` only |
| cyclic imports | partially initialised object | hoisted bindings, may be in the dead zone |

Cycles are legal in both and behave badly in both. In ES modules the imported binding exists but may be uninitialised when a cycle is entered, giving a `ReferenceError` from the temporal dead zone, which is lesson 5's rule appearing in a new place. Treat a cycle as a design defect rather than something to work around.

### Three TypeScript-specific points

**A file with no top-level `import` or `export` is not a module.** It is a script, and its declarations go into the global scope, which is how two unrelated files end up in conflict. Adding `export {}` makes such a file a module deliberately.

**`import type` is erased.** It states that only the types are needed, so no run-time import is emitted and no module side effect is triggered. `verbatimModuleSyntax` makes what is emitted predictable, which matters when a module's import has side effects you either need or must avoid.

**Extensions in the specifier are the runtime's business, not the compiler's.** Node's ES module resolution requires the file extension in a relative specifier, and TypeScript source files are written as `.ts` while the emitted specifier must resolve at run time. That is the entire reason `"module"` and `"moduleResolution"` exist as separate settings, and stage 3 spends a lesson on them.

## Practice

1. ▢ Predict the output.

   ```ts
   // counter.ts
   export let count = 0;
   export function bump() { count++; }

   // main.ts
   import { count, bump } from "./counter.js";
   bump();
   bump();
   console.log(count);
   ```

<details markdown="1"><summary>Check</summary>

`2`.

The import is a live binding to the exporting module's `count`, so both increments are visible. Written with CommonJS destructuring it would print `0`.

</details>

2. ▢ Which of these is legal at the top of a module?

   - a) `if (dev) { import { x } from "./a.js"; }`
   - b) `const { x } = await import("./a.js");`
   - c) `import { x } from dev ? "./a.js" : "./b.js";`
   - d) `for (const m of mods) import(m);`

<details markdown="1"><summary>Check</summary>

**b)** and **d)** are legal, since both use dynamic `import()`, which is a function-like expression.

Options a and c are syntax errors. A static `import` cannot be conditional and its specifier must be a literal string, because the whole graph is resolved before evaluation begins.

Note that d starts every import and awaits none, which makes it a floating-promise problem from lesson 6.

</details>

3. ▢ Two files in a project both declare `interface Options` at the top level, with no imports or exports anywhere in either. The compiler reports a duplicate identifier. Why, and what is the one-line fix?

<details markdown="1"><summary>Hint</summary>

Ask what makes a file a module in the first place.

</details>

<details markdown="1"><summary>Check</summary>

Neither file is a module. Without a top-level `import` or `export` a file is a script, and its top-level declarations are global, so the two `Options` collide.

The fix is `export {}` at the top of the file, which makes it a module with no exports and gives its declarations their own scope.

</details>

4. ▢ What is the difference between these two lines, and when does it matter?

   ```ts
   import { Config } from "./config.js";
   import type { Config } from "./config.js";
   ```

<details markdown="1"><summary>Check</summary>

The first may emit a run-time import of `./config.js`. The second never does: it declares that only the type is needed and is erased.

It matters in three situations. When the module has side effects at import time, the first triggers them and the second does not. When the import would create a cycle, the type-only form removes it entirely. And when the emitted output is inspected by a bundler deciding what to include, the difference changes the bundle.

`verbatimModuleSyntax` is the setting that makes the emitted form exactly match what you wrote, so this stops being something to reason about.

</details>

5. ▢ A module imports another, which imports the first. Both use `export const` and each reads the other's value at top level. Predict the failure and say what you would do about it.

<details markdown="1"><summary>Check</summary>

Whichever module is evaluated second finds the first one's binding uninitialised and throws `ReferenceError: Cannot access '...' before initialization`. That is the temporal dead zone from lesson 5, reached through the module graph: the binding exists because imports are hoisted, and it has no value yet.

The fix is not a trick. Move the shared value into a third module both import, or defer the read into a function that runs after both modules have finished evaluating. A cycle that only works because of evaluation order is a defect waiting for someone to reorder an import.

</details>

## Real-world reps

- [ ] Build the live-binding example with ES modules, then again with `require` and destructuring, and compare the two outputs.
- [ ] Take a file with no imports or exports, declare a top-level type in it, and watch what happens when a second file declares the same name. Then add `export {}`.
- [ ] Tomorrow: check whether the codebase you work in uses ES modules, CommonJS, or both, and find out what `"module"` is set to in its `tsconfig.json`. Stage 3 will make that setting make sense.

## Going further

- [Modules: ECMAScript modules](https://nodejs.org/api/esm.html): the runtime's resolution rules, including extensions and `package.json` fields
- [Modules: CommonJS modules](https://nodejs.org/api/modules.html): the older model, and how the two interoperate
- [TSConfig reference](https://www.typescriptlang.org/tsconfig/): `module`, `moduleResolution` and `verbatimModuleSyntax`, which stage 3 takes apart
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
