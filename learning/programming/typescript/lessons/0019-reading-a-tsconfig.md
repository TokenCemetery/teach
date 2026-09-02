---
title: 19. Reading a tsconfig
description: Which files the compiler looks at, where the settings come from, and why the generated file says what it says
type: lesson
---

# Lesson 19. Reading a tsconfig

**Mission link:** Owning a codebase means being able to point at any checked file or fired flag and say exactly why, and a `tsconfig.json` is where every one of those answers lives.
**Primary source:** [TSConfig Reference, typescriptlang.org](https://www.typescriptlang.org/tsconfig/)
**Prerequisites:** [Lesson 16](0016-the-checks-strict-leaves-out.md), [Lesson 15](0015-what-strict-turns-on.md)

## Warm-up

1. ▢ Lesson 16 showed that some flags are refused outright rather than merely reported as a code problem. Predict what `tsc` does with a `tsconfig.json` that sets `"strictNullChecks": false` and `"strictPropertyInitialization": true` together, and where the diagnostic points.

<details markdown="1"><summary>Check</summary>

`error TS5052: Option 'strictPropertyInitialization' cannot be specified without specifying option 'strictNullChecks'.`, and it points at the `tsconfig.json` file itself, at the line and column of the offending option, not at any `.ts` file. The configuration was rejected before a single line of code was read.

</details>

## Know this

### Two jobs in one file

A `tsconfig.json` does two things, and the second causes the confusing failures. It names the compiler options, which lessons 15 and 16 covered. It also defines the project: the exact set of files the compiler treats as part of the program. Ignoring the second half means "why did the compiler check a file I never mentioned" has nowhere to look for an answer. A bare `tsc` in a directory with no `include`, `exclude` or `files` checks every `.ts` file below the configuration file, in every subdirectory, except `node_modules` and whatever `outDir` names. That default is already a policy: everything counts unless something says otherwise.

### Include, exclude, files, and where intuition goes wrong

`include` is a list of glob patterns, resolved relative to the configuration file, that seeds the set of files the compiler looks at. `exclude` narrows that seed set. `files` is a separate allow list of exact paths, no globs, and every path in it must exist. The trap is assuming `exclude` vetoes the whole program. It does not: it only removes matches from what `include` found, and cannot stop a file entering the program by another route.

```json
{
  "compilerOptions": { "strict": true, "noEmit": true },
  "include": ["src"],
  "exclude": ["src/other.ts"]
}
```

```ts
// lib/helper.ts, outside include
export function helper(): number { return "not a number"; }

// src/other.ts, matched by include, then named in exclude
export function other(): number { return "nope"; }

// src/main.ts
import { helper } from "../lib/helper";
import { other } from "./other";
helper();
other();
```

Running `tsc` reports both:

```text
lib/helper.ts(2,3): error TS2322: Type 'string' is not assignable to type 'number'.
src/other.ts(2,3): error TS2322: Type 'string' is not assignable to type 'number'.
```

`helper.ts` was never matched by `include`, and `other.ts` was matched and then explicitly excluded, yet both are checked, because `main.ts` imports them and an import outranks a glob pattern. Delete the `import { other }` line and its call, and its error disappears: `exclude` only works once nothing else pulls the file back in. `tsc --showConfig` on the original three files prints `"files": ["./src/main.ts"]`, the seed set after `include` and `exclude` ran, not the program actually built. `files` sits outside this entirely: a path listed there compiles even if `exclude` also names it.

### extends: a base plus overrides, and where its paths resolve

`extends` names another configuration file to start from, and the extending file's own settings merge on top of it, key by key, inside `compilerOptions`. Where both set the same key, the extending file wins.

```json
// base/tsconfig.base.json
{ "compilerOptions": { "strict": true, "outDir": "./dist" } }
```

```json
// project/tsconfig.json
{
  "extends": "../base/tsconfig.base.json",
  "compilerOptions": { "strict": false, "rootDir": "./src" },
  "include": ["src"]
}
```

`tsc --showConfig` from inside `project` prints `"strict": false`, the override, and `"outDir": "../base/dist"` for a setting the project file never mentioned. That second line is the part people get wrong: a relative path written in the base file resolves against the base file's own location, not the file that extends it, so `"./dist"` in `base/tsconfig.base.json` means the `dist` folder next to the base file. Building confirms it: the output lands at `base/dist/main.js`, not anywhere under `project`. A base configuration shared by several projects can only use relative paths it is happy to see resolved next to itself.

### tsc --showConfig: where a setting actually came from

Once a project is extended and merged, "why is this flag on" is answered fastest by running one command rather than reading files. `tsc --showConfig` prints the fully merged configuration exactly as the compiler will use it, including options nobody wrote down because another option implied them. Set only `"composite": true` and nothing else, and `--showConfig` prints `"declaration": true` and `"incremental": true` alongside it, both implied rather than written. Before changing a flag you did not expect to be on, run `--showConfig` first; tracing an `extends` chain by eye can miss an implied setting entirely.

### The command line against the file

TypeScript 7 treats a bare list of files on the command line, next to a `tsconfig.json`, as a mistake rather than an instruction. Running `tsc main.ts --noEmit` where a `tsconfig.json` exists reports `error TS5112: tsconfig.json is present but will not be loaded if files are specified on commandline. Use '--ignoreConfig' to skip this error.`, and the compiler stops rather than compiling. Earlier releases compiled anyway, silently, using only the command line's flags and none of the project's settings, no `strict`, no `paths`, nothing, so a command that looked like it respected the project quietly did not. `--ignoreConfig` still gives that old behaviour when genuinely wanted, but now by name rather than by accident.

### Reading what tsc --init writes

`tsc --init` writes a real configuration in three kinds of line. The checking flags, `strict` plus `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`, are lessons 15 and 16's territory. The module and emit settings, `module`, `target`, `verbatimModuleSyntax`, `isolatedModules`, `noUncheckedSideEffectImports`, `moduleDetection`, and the source map and declaration options, belong to lessons 20 and 21. Two lines are this lesson's to settle now.

`skipLibCheck: true` skips checking every `.d.ts` file, including ones you did not write and cannot fix, and duplicate copies of the same package's types pulled in by different dependencies. Off, a declaration file with a genuine mistake reports `TS2322` like any other file; on, that file compiles clean, silently, buying speed and peace from other people's mistakes at the cost of a real incompatibility between two versions of the same types package going unseen.

`types: []` states, rather than changes, the current default: since TypeScript 6.0 the compiler no longer pulls in every `@types` package under `node_modules` automatically, so a global declared only in an ambient `.d.ts` and never imported reports `TS2304: Cannot find name`, unless its package is named in `types`, or the old behaviour is restored wholesale with `types: ["*"]`. It buys a global scope nothing pollutes by accident, at the cost that a globals-only package must be named or its globals vanish.

### Reviewing someone else's configuration

Start from `tsc --showConfig`, since it is the truth and the files on disk are only history. Follow the `extends` chain first, since a setting that looks wrong in the leaf file might override a worse default. Two findings deserve a question before anything else: a check turned off with no comment explaining why, and a setting nobody on the project can explain. Both usually mean the configuration was copied rather than decided. Project references and build mode split a large codebase into independently built pieces, a scaling concern for later, not a stage 3 skill.

## Practice

1. ▢ A configuration sets `"include": ["src"]` and `"exclude": ["src/generated"]`. A file in `src/generated` is never imported by anything under `src`. Is it checked?

<details markdown="1"><summary>Check</summary>

No. `exclude` only removes matches from what `include` found, and with nothing importing the file, nothing pulls it back in. Add one import from a file under `src` and the answer flips, since an import reaches it regardless of `exclude`.

</details>

2. ▢ A base configuration sets `"outDir": "../build"`, and a project two directories deeper extends it with no `outDir` of its own. Where does the output land, relative to which file?

<details markdown="1"><summary>Hint</summary>

The path is written in the base file, and `extends` merges values, it does not move where they resolve from.

</details>

<details markdown="1"><summary>Check</summary>

Relative to the base file's own location, one directory above wherever the base file sits, not relative to the project that extends it. A relative path in a base configuration always resolves against that base file.

</details>

3. ▢ A configuration sets only `"strict": true`. Predict whether `tsc --showConfig` prints `"noImplicitAny": true` anywhere in its output.

<details markdown="1"><summary>Check</summary>

No. `--showConfig` prints written and implied options, but `strict` is not expanded into its member flags there, it stays a single line. Contrast `"composite": true`, which does cause `--showConfig` to print `"declaration": true`, because `composite` genuinely implies it.

</details>

4. ▢ A directory has a `tsconfig.json` in it. Predict the result, including its `TS` number, of running `tsc app.ts --noEmit`.

<details markdown="1"><summary>Check</summary>

`error TS5112: tsconfig.json is present but will not be loaded if files are specified on commandline. Use '--ignoreConfig' to skip this error.` The command does not fall back to compiling `app.ts` with only the flags given; it refuses.

</details>

5. ▢ A `node_modules/@types/mylib` package declares one global. A project's `tsconfig.json` has no `types` field at all. A file references that global with no import anywhere. Does it compile?

<details markdown="1"><summary>Hint</summary>

This is not the pre-6.0 default, and the generated `tsc --init` file is written the way it is for a reason.

</details>

<details markdown="1"><summary>Check</summary>

No, `error TS2304: Cannot find name`. Since TypeScript 6.0 the default value of `types` is already an empty list, so a globals-only package must be named explicitly in `types`, or restored wholesale with `types: ["*"]`.

</details>

## Real-world reps

- [ ] Run `tsc --showConfig` on a real project and find one option in the output that appears in no file on disk, then trace which written option implied it.
- [ ] Find a real `exclude` entry and check whether anything still imports the file it names. If something does, the entry is not doing what its author thinks.
- [ ] Tomorrow: open a `tsconfig.json` you did not write and find one flag off with no comment, or one setting nobody nearby can explain, and ask about it.

## Going further

- [TSConfig Reference, `exclude`](https://www.typescriptlang.org/tsconfig/#exclude): the exact wording on why exclude only narrows include and cannot stop an import
- [TSConfig Reference, `extends`](https://www.typescriptlang.org/tsconfig/#extends): the merge and path resolution rules this lesson verified
- [TypeScript Release Notes, TypeScript 6.0](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html): the change to `types` defaulting to an empty list
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
