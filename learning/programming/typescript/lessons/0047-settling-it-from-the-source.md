---
title: 47. Settling It From the Source
description: Which document answers a question about the compiler, and how to read the declarations it ships
type: lesson
---

# Lesson 47. Settling It From the Source

**Mission link:** Owning a TypeScript codebase means having somewhere real to go the moment the Handbook stops answering a question, whether that turns out to be the release notes, the compiler's own shipped declarations, or an old argument in the issue archive.
**Primary source:** [TypeScript Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/overview.html)
**Prerequisites:** [Lesson 34](0034-declaration-files.md), [Lesson 19](0019-reading-a-tsconfig.md)

## Warm-up

1. ▢ Lesson 34 taught you to read a `.d.ts` file: no implementation, just the types, taken on trust if hand-written and guaranteed to agree with its source if generated. The compiler ships its own `.d.ts` files too, the `lib` files lesson 20 named when it explained what `target` and `lib` choose between. What changes about how you read one of those, compared with a `.d.ts` a library published for you to consume?

<details markdown="1"><summary>Check</summary>

Nothing about the reading changes: still signatures and type aliases with no implementation to check them against, read exactly as lesson 34 taught. What changes is the author. A published `.d.ts` is one team's claim about their own library, checked by nobody but them. The `lib` files are the compiler's own account of what it makes available, written by the people who also write the checker that enforces every use of it, about as close to an authoritative claim as this language has to offer.

</details>

## Know this

Every lesson in this arc that hit a question the Handbook did not answer did the same thing: wrote a small file, ran `tsc` against it, and trusted the diagnostic over any description of what it ought to say. This lesson names why that was always right, and adds three places to look first: the release notes, for whether something changed and when, the compiler's own shipped declarations, for what a construct actually does, and the issue archive, for why, on the rare occasion a run and a read still leave the question open.

### No specification, and the consequence

Say this plainly, because it reframes everything that follows: TypeScript has no specification. An early attempt at one existed and was abandoned years ago, and nothing replaced it. ECMAScript itself, which stage 1 pointed you at directly, has a normative document, so a runtime that disagrees with it is, by definition, wrong. TypeScript has no equivalent to be wrong against. The compiler is the definition: whatever `tsc` accepts is accepted, whatever it rejects is rejected, and there is no higher authority when either surprises you. The Handbook is not that authority. It is a description, written by the same team, aimed at teaching rather than at exhaustively stating every rule, and a description can lag what it describes, particularly around a feature added after the page was last revised. The release notes are a different job again: they say what became true on a given date, not what is true today. So when an assignability question has no answer in the Handbook, and this arc has hit several, from a method parameter checked bivariantly in lesson 13 to soundness being a declared non-goal in lesson 11, there is one way to settle it: write the two lines of code and run them. Not a shortcut taken because reading the source is hard; the actual answer, because the compiler's behaviour is the fact and everything else, Handbook included, is commentary on the fact.

### The release notes: did this change?

The release notes answer a narrower question than "what is true": they answer "did this change, and when". Lesson 46 sent you to exactly this page to find out when `erasableSyntaxOnly` and standard decorators landed, and it is worth actually doing that rather than filing it under things to check later. Search for `erasableSyntaxOnly` and the answer is TypeScript 5.8: the notes for that release say plainly that TypeScript 5.8 introduces the `--erasableSyntaxOnly` flag, and that with it enabled, the compiler errors on most TypeScript-specific constructs that have runtime behaviour. The same page explains why: Node.js had recently unflagged experimental support for running TypeScript files directly, on condition that a file contain nothing a stripper cannot cleanly erase, and before that release, the only way to discover your `enum` or parameter property broke that assumption was to run the stripped file and watch it fail. That is the shape of what the notes are for: not merely that a flag exists, but what was impossible, or undiscoverable except by trial, before the release that added it. For any feature this arc taught you as though it had always existed, `satisfies`, template literal types, a `const` type parameter, the notes will name the version before which writing that code meant something else or nothing at all, and finding that version from the notes themselves rather than from memory is the research move this section is teaching.

### Reading what the compiler ships

The most under-used source available is not a document at all. It is the declarations the compiler ships alongside itself, the `lib` files lesson 20 named. Lesson 36 already assigned opening one of these for `Partial` or `Pick`; this section does the same for `ReturnType`, and every one of these utility types is defined in the same handful of lines every install carries. These are ordinary `.d.ts` files, so lesson 34 already gave you what you need to read one: no runtime behaviour to check them against, just a type alias to read literally. Open the file carrying the general-purpose utility types and `ReturnType` reads like this, comment and all:

```ts
/**
 * Obtain the return type of a function type
 */
type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any;
```

That is the entire implementation. Nothing in it is unfamiliar: a constraint from lesson 26 restricting `T` to something callable, a conditional type from lesson 37 asking whether `T` matches a callable shape, and `infer` from lesson 38 pulling the return position out and naming it `R`. There is no larger machine hiding behind the name. `Exclude`, defined a little earlier in the same file, is just as short, `type Exclude<T, U> = T extends U ? never : T;`, doing exactly what its own comment says, "exclude from T those types that are assignable to U", and `Omit` a few lines further down is built directly on top of it, `Pick<T, Exclude<keyof T, K>>`, so reading one definition often hands you the next one for free. None of this is a teaching example simplified for the occasion; it is the real text the checker runs against every call site that uses `ReturnType`. A question about exactly what it does with an unusual input has an answer sitting in those three lines rather than in anything this lesson could tell you about them, and reading the actual definition settles it faster and more reliably than guessing from the name.

### The issue archive: intent, not current behaviour

`RESOURCES.md` already flags where this fits: the issue archive is, in its own words, frequently the only place a behaviour is explained at all, after fifteen years of a team arguing in public about exactly the kind of thing a Handbook page never mentions. Search it and you will regularly find the reasoning behind a choice that otherwise reads as arbitrary: why a narrowing does not survive being read from a closure, why `const enum` gets no exemption from `erasableSyntaxOnly` even though the Handbook advertises it as inlined away, why an unsound assignment stayed unsound on purpose rather than by oversight. That is what the archive is for: explaining why the compiler does something the Handbook does not mention, in the words of the people who decided it, often with the alternative they rejected alongside. It is not, and this is the discipline worth holding onto, a statement of what the compiler does today. An issue records a moment, sometimes about a version several releases behind the one you are running, sometimes closed and fixed, sometimes closed and rejected outright, sometimes gone quiet without either. Nothing stops a comment from years ago being exactly right and completely superseded since, and the thread will not tell you which. So treat an issue the way this lesson has treated everything else with a date attached to it: it explains intent, and only a run against the compiler you actually have establishes what happens now.

## Practice

1. ▢ A colleague says the Handbook does not mention whether an assignment through a getter-only accessor is checked at the point of assignment, and asks you to confirm before merging. Per this lesson, what actually settles the question, and what does not?

<details markdown="1"><summary>Check</summary>

A small file and a run of `tsc`, because the compiler's behaviour is the definition and the Handbook's silence is not evidence of what it does. What does not settle it: guessing from a similar-looking case elsewhere, or trusting a description that predates the release you are running, since the Handbook is known to lag the compiler.

</details>

2. ▢ Lesson 46 pointed you at the release notes to find out when `erasableSyntaxOnly` and standard decorators landed, without saying the version itself. Predict which release the notes credit with introducing `erasableSyntaxOnly`, and predict, in one sentence, what the notes say was true before that release that stopped being true after it.

<details markdown="1"><summary>Check</summary>

TypeScript 5.8. Before that release there was no flag that turned an unerasable construct into a compile error, so the only way to discover that an `enum`, a `namespace` or a parameter property broke Node's type-stripping mode was to try running the stripped file and watch it fail at run time; after 5.8, the same mistake is a compile-time diagnostic instead.

</details>

3. ▢ You need to know exactly what `Awaited<T>` does with a "thenable" that is not a real `Promise`, and the Handbook's own description is a paragraph of prose rather than a worked case. Where do you go, and what should you expect to find there?

<details markdown="1"><summary>Hint</summary>

The same kind of file that carried `ReturnType` in this lesson carries `Awaited` too, and lessons 37 and 38 already gave you every piece the definition is built from.

</details>

<details markdown="1"><summary>Check</summary>

The compiler's own shipped declarations. Searching the file that defines `ReturnType` for `type Awaited` turns up the whole thing in a handful of lines: a conditional type checking whether `T` has a callable `then`, `infer` extracting what its first argument would receive, and `Awaited` calling itself again on that extracted type, bottoming out once nothing thenable is left. Nothing beyond conditional types, `infer` and self-reference, just applied to itself once per layer of wrapping.

</details>

4. ▢ A GitHub issue from several years ago, still open, has a maintainer stating that a particular unsound assignment is "intentional, not a bug." Predict whether that comment, on its own, tells you what the compiler you are running today actually does with that assignment, and say what would tell you.

<details markdown="1"><summary>Check</summary>

No, not on its own. An issue records a decision made at a point in time, and neither an unresolved comment nor an open thread guarantees the decision still holds in the release you are running; it explains why someone chose the behaviour, not that the behaviour is current. What tells you what happens today is the same move as everywhere else in this lesson: write the assignment and run the compiler you actually have.

</details>

5. ▢ During review, a comment cites a Handbook page to justify a claim about assignability, but running the exact case under the project's own compiler gives the opposite answer, with a diagnostic to show it. Which one wins, and what do you write in the review?

<details markdown="1"><summary>Check</summary>

The compiler wins, because it is the definition and the Handbook is a description that can lag it. Write the diagnostic itself in the review comment, not a paraphrase of the Handbook page, since the diagnostic is the fact everyone has to agree with and the citation was never more than someone's summary of that fact.

</details>

## Real-world reps

- [ ] Pick one utility type your code relies on and find its definition in the `lib` files your compiler ships, rather than in a blog post about it.
- [ ] Take one review comment that cited "the docs" without a link, and find the release note or issue that actually backs it, or discover that none does.
- [ ] Tomorrow: the next time the Handbook and your compiler disagree about anything, write down which one you trusted and why, before deciding the disagreement does not matter.

## Going further

- [Handbook, Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html), for the writing side of a `.d.ts`, since this lesson only reads one
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals), the closest thing to a constitution this language has, and still not a specification
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
