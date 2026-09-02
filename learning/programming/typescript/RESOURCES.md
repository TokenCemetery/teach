---
title: Resources
description: Trusted sources for TypeScript, each annotated with what it covers
type: resources
---

# TypeScript Resources

## Knowledge

- [Docs: "The TypeScript Handbook", Microsoft, typescriptlang.org](https://www.typescriptlang.org/docs/handbook/intro.html)
  The official description of the type system, written by the team that implements it. Use for: stages 2 to 4, and as the first answer on any type-system question.

- [Docs: "TSConfig Reference", Microsoft, typescriptlang.org](https://www.typescriptlang.org/tsconfig/)
  Every compiler option with what it changes and what it costs. Use for: stage 3, and for justifying a configuration rather than copying one.

- [Docs: "Handbook: Modules", Microsoft, typescriptlang.org](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
  The compiler's own model of what an import means, separated into the theory, the reference and the guides. Use for: stage 3 module resolution, and as the only source that states the model rather than one tool's approximation of it.

- [Docs: "Modules: Packages", OpenJS Foundation, nodejs.org](https://nodejs.org/api/packages.html)
  How `package.json` decides a file's module system, including `type` and `exports`. Use for: stage 3, since the compiler reads these same fields and a resolution verdict often turns on one of them. Note this URL serves the current release rather than the long-term-support line.

- [Docs: "Declaration Files", Microsoft, typescriptlang.org](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)
  Writing, publishing and consuming type declarations, including for untyped libraries. Use for: stage 5, and for making a package usable by others.

- [Docs: "TypeScript Release Notes", Microsoft, typescriptlang.org](https://www.typescriptlang.org/docs/handbook/release-notes/overview.html)
  What each release added, with examples of what was impossible before it. Use for: checking any version-sensitive claim before teaching it.

- [Tool: "TypeScript Playground", Microsoft, typescriptlang.org](https://www.typescriptlang.org/play)
  Compiles in the browser and shows the emitted JavaScript, the inferred types and the errors side by side. Use for: reps about what erases, and for isolating a type question from a project.

- [Docs: "TypeScript Design Goals", Microsoft, github.com/microsoft/TypeScript wiki](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
  The stated non-goals, including soundness, which explains most of the type system's deliberate holes. Use for: stage 7, and for why an unsound assignment is allowed on purpose.

- [Docs: "Performance", Microsoft, github.com/microsoft/TypeScript wiki](https://github.com/microsoft/TypeScript/wiki/Performance)
  What makes type checking slow, and how to find out which types are responsible. Use for: stage 6, when a clever type has made a project unpleasant to work in.

- [Spec: "ECMAScript Language Specification", Ecma International, tc39.es](https://tc39.es/ecma262/)
  The definitive statement of what JavaScript does, including coercion and the job queue. Use for: stage 1, settling runtime behaviour that TypeScript has no opinion about.

- [Docs: "JavaScript", MDN Web Docs contributors, developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  The readable reference for the language and its standard library, one level above the specification. Use for: stage 1, when the specification is precise and unhelpful.

- [Docs: "Node.js API Documentation", OpenJS Foundation, nodejs.org](https://nodejs.org/docs/latest/api/)
  The runtime's own modules, and the module resolution rules the compiler has to match. Use for: stage 3 module resolution, and anything running outside a browser.

- [Book: "Effective TypeScript", Dan Vanderkam, O'Reilly](https://effectivetypescript.com/)
  Numbered items on using the type system well, each with the failure it prevents. Use for: stages 2 to 5, and for review vocabulary.

- [Course: "Total TypeScript", Matt Pocock, totaltypescript.com](https://www.totaltypescript.com/)
  Exercise-driven material on generics, inference and type-level tools, with free tutorials and articles alongside the paid course. Use for: stage 6, where reading alone does not build the skill.

- [Book: "TypeScript Deep Dive", Basarat Ali Syed, basarat.gitbook.io](https://basarat.gitbook.io/typescript/)
  Free, thorough, and strong on compiler behaviour and the reasons behind error messages. Use for: an alternative explanation when the handbook's is too brief.

- [Book: "You Don't Know JS Yet", Kyle Simpson, github.com/getify](https://github.com/getify/You-Dont-Know-JS)
  Free book series on scope, closures, coercion and `this`, in depth. Use for: stage 1 when a mental model is missing rather than a fact.

- [Practice: "Type Challenges", Anthony Fu and contributors, github.com/type-challenges](https://github.com/type-challenges/type-challenges)
  Graded type-level puzzles with community solutions. Use for: stage 6 reps, treated as exercise rather than as a model for production types.

- [Docs: "Zod", Colin McDonnell and contributors, zod.dev](https://zod.dev/)
  Schema validation whose inferred types match what it validates at runtime. Use for: stage 5, closing the gap between a declared type and an actual value. This is the arc's chosen validation library, decided on reach, release health and the fact that one declaration yields both the check and the type. The stage teaches the boundary rather than the library, so the technique transfers to any schema validator with inference.

## Wisdom (Communities)

- [Archive: "TypeScript Issues", Microsoft, github.com/microsoft/TypeScript](https://github.com/microsoft/TypeScript/issues)
  Fifteen years of design discussion, searchable without an account, and frequently the only place a behaviour is explained at all. Use for: why the compiler does something the handbook does not mention.

## Gaps

- **TypeScript has no specification.** An early one was abandoned, and the compiler is now the definition. Any claim about assignability that the handbook does not state has to be checked against the compiler itself, in the playground.
- Module resolution is the messiest area here. The handbook and the config reference describe the compiler's model, which bundlers and runtimes then approximate differently; no source reconciles them.
- Type-level programming has no authoritative reference. Type Challenges is practice and Total TypeScript is a course, so stage 6 has to supply its own judgment about when a type has gone too far.
- Runtime validation still has no standard, and the gap is narrower than it was. Zod is now the arc's choice and the reasoning is in `NOTES.md`, but it is a choice among live alternatives rather than a settled ecosystem default, and a reader will meet others. Stage 5 therefore teaches the boundary and uses Zod to make it concrete, so nothing in the stage depends on the library beyond the shape of `parse`, `safeParse` and inference from a schema.
