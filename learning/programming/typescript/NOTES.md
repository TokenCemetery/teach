# TypeScript Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior TypeScript and no more JavaScript than the arc teaches. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting. Many are type experiments rather than programs, and the playground is enough for those.

## State

Stages 1 and 2 are written: lessons 0001 to 0014, plus three reference sheets, `coercion-and-equality.md`, `event-loop-and-promises.md` and `types-over-values.md`. Stages 3 to 7 are unwritten.

Stage 2 is seven lessons and is the first stage in the arc that teaches the type system at all. Its order is deliberate and worth keeping: the vocabulary first (0008), then the two features that look like guarantees and are not (0009), then unions and literals (0010), then the assignability rule that explains every verdict (0011), then narrowing (0012), then functions where assignability stops being intuitive (0013), and only then inference (0014). Inference comes last because the stage's done-when criterion is restraint, and a reader cannot be told to stop annotating before they know what an annotation does.

Lesson 0012 is the one to protect. Its narrowing-loss rules were checked by running every case rather than repeating the received wisdom, and two of them come out the opposite way round from how they are usually stated. If it is ever revised, re-run the cases rather than trusting the prose.

Stage 1 is JavaScript, as the arc says, and it stayed that way in the writing: no lesson in it teaches a type-system feature. Types appear only where the runtime behaviour explains why a type is a claim rather than a guarantee, which happens three times, in lessons 2, 3 and 7. That is deliberate groundwork for stage 5.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added eight terms alongside the three pinned ones, and stage 2 added thirteen, for twenty-four in total. Two candidates were refused, on the same grounds the Java workspace refuses coined phrases: "boundary", in the annotate-boundaries sense lesson 0014 argues for, is this workspace's wording rather than the language's, and "contravariant" was left out because lesson 0013 deliberately teaches the direction as an intuition rather than as vocabulary, so the reader has not earned the word. Keep doing this per stage, and do not add a term the lessons have not earned.

## What execution changed

Every behavioural claim in stage 2 was run on TypeScript 7.0.2 rather than recalled, and the stage found more drift than any other opening stage in this repository, because the compiler had been rewritten since almost everything written about it.

- **The headline is in the version policy above: TypeScript 7 type-checks strictly with no configuration.** It is repeated here because it is the fact most likely to be undone by a reviser working from older material.
- **Passing files on the command line while a `tsconfig.json` is present is now an error**, `TS5112`, suggesting `--ignoreConfig`. Earlier releases silently ignored the config file. This bit immediately when setting up the verification harness, and any script that checks a single file needs the flag.
- **Property narrowing survives an arbitrary function call.** Narrow `b.v` to `string`, call an unrelated function, use `b.v`, and it compiles. The widely repeated claim that any intervening call invalidates a narrowed property is wrong on this compiler. What does lose it is capturing the property in a closure, which errors with `TS2322`, because the closure may run later.
- **Local narrowing is about reassignment, not about `let` against `const`.** A narrowed `let` survives being captured in a closure so long as the variable is never reassigned anywhere afterwards. One reassignment later in the function loses the narrowing, for a direct use and for a closure use alike.
- **A tuple's fixed length is enforced on reads and not on `push`.** `t[5]` and destructuring a third element both give `TS2493` naming the length, while `t.push(3)` compiles, because a tuple is an array at run time and `push` belongs to the array type.
- **`readonly` is not part of assignability for object types.** A `{ readonly a: number }` value is assignable to `{ a: number }` with no diagnostic, so a readonly object can be handed straight to something that mutates it. Enforced where you use it, forgotten where you pass it.
- **A parameter written with method syntax is checked bivariantly and the same parameter written as a function-typed property is checked contravariantly.** The identical narrower callback is rejected in one declaration style and accepted in the other. This is a deliberate exemption rather than a bug, and it decides whether the compiler is helping on a given line.
- **`noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` are not in `strict`**, verified, so `a[99]` on a `string[]` types as `string`. `tsc --init` turns both on anyway, which is the clearest available evidence of what the team now considers sane and is stage 3's material.

- **The readonly hole is specific to object properties and does not generalise.** A readonly array or readonly tuple assigned to a mutable one is caught, `TS4104: The type 'readonly number[]' is 'readonly' and cannot be assigned to the mutable type 'number[]'`, while the object-property case compiles silently. So `readonly` is part of assignability for arrays and tuples and is not part of it for object properties. This was found by the sheet writer, which noticed that lesson 0009 discusses both side by side and had only stated the hole, leaving a reader free to over-generalise it. The lesson now carries both facts.

Two that behaved exactly as expected and are worth recording because a reader will doubt them: excess property checking fires on a fresh object literal with `TS2353` and does not fire when the identical object arrives through a variable; and `const f: () => void = () => 42` compiles, because a `void` return type promises only that the caller ignores the result.

## On the arc

- Stage 1 is JavaScript, and that is the decision most likely to be questioned. It stays because every hard TypeScript bug is a runtime behaviour the types described wrongly, and a reader who cannot predict the runtime cannot tell which of the two is lying.
- Stage 5 is the load-bearing stage for the mission. If the arc has to be cut short, stages 1 to 5 are the part that makes someone dangerous to leave alone with a codebase; stage 6 mostly prevents self-inflicted damage.
- Stage 6 has a failure mode built into it: type-level puzzles are enjoyable and mostly do not pay. Every lesson there needs a caller who benefits, or it does not get written.

## Version policy

The arc names no TypeScript version. Where a lesson must assume one, it states which and checks the release notes rather than recalling the feature. Inference and narrowing improve in ordinary releases, so a claim that something "cannot be expressed" dates faster than anything else here.

**Settled for stage 2, and it is bigger than a version bump.** The recheck before stage 2 found that the current release is **TypeScript 7.0.2**, published 2026-07-08. That is the native compiler rewrite, not another point release on the 5.x line: 5.9.3 was the last 5.x, the 6.0.x line was the short-lived bridge, and 7 is now `latest` on the registry. Two consequences the arc has to live with.

The first is that **TypeScript 7 type-checks strictly out of the box.** Verified by running it: bare `tsc`, with no flags and no configuration file, reports `TS7006: Parameter 'x' implicitly has an 'any' type` and `TS2322: Type 'null' is not assignable to type 'string'`. `tsc --all` states the mechanism, that `noImplicitAny`, `noImplicitThis`, `strictBindCallApply`, `strictBuiltinIteratorReturn` and `strictFunctionTypes` now default to `true` unless `strict` is explicitly `false`, and passing `--strict false` does disable them. Every piece of writing about TypeScript that predates this describes the opposite default, which is the drift most likely to reach a lesson unnoticed. Stage 2 is therefore written assuming strictness rather than promising it later, and **the arc's stage 3 row needed rewording**: its done-when used to be turning the strict flags on, and the honest version is keeping them on and knowing which strict-shaped flags `strict` still does not include. That row is updated in `README.md`.

The second is that a rewritten compiler means **no behavioural claim carried over from 5.x-era writing is trustworthy without a run**. Stage 2 was written against 7.0.2 with every claim executed; see "What execution changed". When stage 3 is written, recheck the version again rather than assuming 7.0.2 still holds, and note that `tsc --init` now emits a configuration that goes beyond `strict`, adding `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` along with `verbatimModuleSyntax`, `isolatedModules`, `noUncheckedSideEffectImports`, `moduleDetection: force` and `skipLibCheck`. That generated file is stage 3's material and is the best single piece of evidence about what the team now considers a sane default.

No version is named in a lesson unless the lesson's claim depends on it, which is the existing policy and still the right one. Where stage 2 states a version it states 7.0.2 and says the behaviour was run.

## Open threads

- No decision yet on which runtime the reps use. The playground covers stages 2, 4 and 6 entirely; stages 1, 3 and 5 need a real runtime, and the module-resolution material depends on which one.
- Runtime validation needs one library to teach with. Zod is in `RESOURCES.md` for its inference, which is not the same as a decision, and the lesson should teach the boundary rather than the library.
- Module resolution is under-sourced and over-complicated in practice. Expect this to be the hardest stage 3 lesson to write honestly, and keep it to the compiler's model plus one runtime.
- `enum`, namespaces and decorators are legacy-shaped features that still appear in real codebases. Currently unplaced: they belong somewhere in stage 7 as review material rather than being taught as tools.
