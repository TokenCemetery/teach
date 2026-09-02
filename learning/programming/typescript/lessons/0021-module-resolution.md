---
title: 21. Module Resolution
description: The same compiler options give opposite verdicts depending on one field in package.json
type: lesson
---

# Lesson 21. Module Resolution

**Mission link:** Owning a codebase means predicting whether an import will compile and then run, before either the compiler or the runtime tells you, which rests on keeping two separate questions straight rather than treating module configuration as one setting.
**Primary source:** [Handbook, Modules, Theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
**Prerequisites:** [Lesson 19](0019-reading-a-tsconfig.md), [Lesson 7](0007-modules.md)

## Warm-up

1. ▢ Lesson 7 said extensions in an import specifier are the runtime's business, not the compiler's, and that this is why `module` and `moduleResolution` exist as two separate settings. In one sentence each, what does `module` control and what does `moduleResolution` control?

<details markdown="1"><summary>Check</summary>

`module` decides what import and export syntax the compiler *emits*, `import`/`export` against `require`/`module.exports`. `moduleResolution` decides something earlier: given the text `"./dep"` in an import, which file on disk it points to, and whether the specifier may even omit an extension.

</details>

## Know this

This lesson stays inside two models: what the compiler decides about a program it will never run, and what Node.js, on its active long-term-support line, does with the files that compiler produces.

### The two questions

A `tsconfig.json` has two settings that sound like one, and conflating them is the single most common way this material goes wrong. `module` decides the shape of the emitted code, `import`/`export` against `require`/`module.exports`. `moduleResolution` decides something earlier: given the text `"./dep"` in an import, which file that points to, and whether an extension is even optional. `nodenext` sets both together to follow Node's own rules, which is why choosing it sets `moduleResolution` along with it unless overridden. The configuration `tsc --init` writes for a brand new project already sets `module` to `nodenext`, so the compiler's own default assumption is already this runtime's model.

### The fact that decides everything

Here is the fact this lesson rests on. One project, one `tsconfig.json` with `module: nodenext` and `strict` on, `src/main.ts` importing `src/dep.ts`. Nothing in the compiler options changes between the rows below, only `package.json` does, and identical import text gets opposite verdicts.

| `package.json` | Import in `main.ts` | Result |
|---|---|---|
| `{"type": "module"}` | `from "./dep"` | `TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'.` |
| `{"type": "module"}` | `from "./dep.js"` | compiles, even though the file on disk is `dep.ts` |
| `{"type": "module"}` | `from "./dep.ts"` | `TS5097: An import path can only end with a '.ts' extension when 'allowImportingTsExtensions' is enabled.` |
| `{}` | `from "./dep"` | compiles |

The only thing that moved is one field the compiler options never mention. `package.json`'s `type` field tells Node whether a plain file in that package is an ES module or a CommonJS module, and once `module` is `nodenext` the compiler reads exactly the same field, for exactly the same reason: it must decide which module system a file belongs to before saying anything about how its imports resolve. `{"type": "module"}` puts the package under ES module rules, which require a relative specifier to carry the extension the file will actually have at run time. Leave the field out and the package falls back to CommonJS rules, where an extension has always been optional. The compiler is not consulting its options in isolation, it is doing what Node would do with the same two files.

### The extension you write is the extension that will exist

The middle two rows look backwards until the compiler's actual job is placed correctly. `from "./dep.js"` compiles even though nothing named `dep.js` exists, only `dep.ts`. `from "./dep.ts"` fails, even though that exact file is right there. The compiler is type-checking the program that will exist after emit, and after emit `dep.ts` becomes `dep.js`, so the import that will run has to say `.js`. Writing `.ts` claims a file that will never exist once the project is built, and `TS5097` refuses exactly that claim. This is lesson 2's erasure fact wearing different clothes: a `readonly` marker disappears at run time and the compiler checks the marked version rather than the erased one, and here the source extension disappears at run time and the compiler checks the specifier against the emitted file. `allowImportingTsExtensions` relaxes this, but only alongside `noEmit`, `emitDeclarationOnly`, or `rewriteRelativeImportExtensions`, refused otherwise with `TS5096`, because the option only suits a project that never emits the files whose extensions it relaxes.

### How a file's module system is decided

Every file belongs to exactly one module system, decided in a fixed order rather than guessed from context. First, the extension: `.mts` is always an ES module and `.cts` is always CommonJS, whatever the package says. Second, for a plain `.ts` or `.js` file, the nearest `package.json` above it answers through its `type` field. Third, with nothing above the file, the default is CommonJS. Verified both ways: an `.mts` file in a package with no `type` field still needs the extension, and a `.cts` file in a package marked `{"type": "module"}` compiles the extensionless form, because the extension overrules the package either way. So two files in one repository, even a few directories apart, can sit in different module systems, and identical text such as `from "./dep"` can be legal in one and refused in the other.

### verbatimModuleSyntax: what you see is what ships

Ordinarily the compiler may drop an import from the emitted file when nothing in the file uses the imported name as a value: import a name that turns out to be a type only, and the compiler infers you meant `import type` and erases it without telling you. `verbatimModuleSyntax` stops that inference and insists you say what you mean. `import { v, T } from "./dep.js"`, where `T` is a type-only export, fails with `TS1484: 'T' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.`, and `import { v, type T } from "./dep.js"` compiles. The flag buys emitted imports that are exactly the ones written, never a set the compiler edited, which is why lesson 7's warnings about live bindings and side-effecting imports matter here: an import kept only for its side effect must never be silently elided, and a binding you rely on staying live has to still be there in the emitted file.

### When the compiler and the runtime disagree

Everything above is the compiler's model. Node resolves and runs a program it never type-checked, following each `import` through its own algorithm and either finding a file or throwing. The compiler checks a program it will never run, predicting what emit will produce. `nodenext` arranges agreement between the two on purpose, it does not guarantee it. When an import fails, ask first which side failed. A `TS2835` or `TS5097` comes from `tsc`, fixed in the source or the configuration. A `MODULE_NOT_FOUND` from `node`, against files `tsc` accepted without complaint, is a mismatch between what was emitted and what the runtime was told to load. Bundlers add a third resolver again, each approximating this model differently, which is why this lesson does not survey them.

### One documentation trap

One habit worth keeping when a claim depends on the version: the unversioned address for Node's module documentation always serves whichever release happens to be current, so when a claim depends on the version, link a path that names the release line explicitly rather than the address that will quietly change under a link that already exists.

## Practice

1. ▢ A project has `module: nodenext` and `package.json` is `{"type": "module"}`. Predict the result for each import in `main.ts`, where `dep.ts` exists and `dep.js` does not: `from "./dep"`, `from "./dep.js"`, `from "./dep.ts"`.

<details markdown="1"><summary>Check</summary>

`from "./dep"` fails with `TS2835`: an extensionless relative specifier is not allowed under ES module resolution. `from "./dep.js"` compiles: that is the extension the file will have once emitted, even though no `dep.js` exists yet. `from "./dep.ts"` fails with `TS5097`: `.ts` is never the extension of a file that will exist at run time unless `allowImportingTsExtensions` is on.

</details>

2. ▢ Same project and files, except `package.json` becomes `{}`. Predict the result for `from "./dep"` now, and say why the verdict flipped without any compiler option changing.

<details markdown="1"><summary>Check</summary>

It compiles. With no `type` field the package falls back to CommonJS rules, where an extension has always been optional, so the same text that failed under `{"type": "module"}` is legal here. Nothing in the compiler options moved, only which module system Node, and therefore the compiler, considers the file to be in.

</details>

3. ▢ A file named `worker.mts` sits in a package whose `package.json` is `{}`. It imports a sibling with `from "./util"`, where `util.ts` exists. Predict whether the extension is required, and say what decided the answer.

<details markdown="1"><summary>Hint</summary>

Ordering matters: the file's own extension is checked before anyone looks at `package.json`.

</details>

<details markdown="1"><summary>Check</summary>

The extension is required, and the extensionless form fails with `TS2835`. `.mts` is always an ES module regardless of what `package.json` says, so its `type` field is never even consulted for this file.

</details>

4. ▢ `verbatimModuleSyntax` is on. `helpers.ts` exports a function `run` and an interface `Options`, used only as a type annotation. `main.ts` writes `import { run, Options } from "./helpers.js";`. Predict the diagnostic, then write the line that compiles.

<details markdown="1"><summary>Check</summary>

`TS1484: 'Options' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.` The fix is `import { run, type Options } from "./helpers.js";`, which states that `Options` contributes nothing to the emitted import.

</details>

5. ▢ A project sets `allowImportingTsExtensions: true` but does not set `noEmit`, `emitDeclarationOnly`, or `rewriteRelativeImportExtensions`. Predict what happens when you run `tsc`, before it even reaches any source file.

<details markdown="1"><summary>Hint</summary>

The failure here is about the configuration itself, not about anything an import specifier says.

</details>

<details markdown="1"><summary>Check</summary>

`tsc` refuses the configuration with `TS5096: Option 'allowImportingTsExtensions' can only be used when one of 'noEmit', 'emitDeclarationOnly', or 'rewriteRelativeImportExtensions' is set.` The compiler enforces that precondition before looking at any import.

</details>

## Real-world reps

- [ ] Build the four-row table yourself: one `tsconfig.json` with `module: nodenext`, two versions of `package.json`, and watch the same specifier pass and fail as you switch between them.
- [ ] Turn `verbatimModuleSyntax` on in a small project importing both a type and a value from one file, and fix every import the compiler flags until it is silent.
- [ ] Tomorrow: check a project's `package.json` for its `type` field, then pick one relative import there and decide, before running anything, whether it may omit its extension.

## Going further

- [Handbook, Modules, Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html): every `module` and `moduleResolution` value
- [Node, Packages](https://nodejs.org/api/packages.html): the `type` field and how Node decides a file's module system
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
