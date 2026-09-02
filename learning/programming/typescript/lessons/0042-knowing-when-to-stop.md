---
title: 42. Knowing When to Stop
description: Measure what a clever type costs, then justify it to whoever maintains it
type: lesson
---

# Lesson 42. Knowing When to Stop

**Mission link:** Owning a codebase means being able to say, with a number rather than a feeling, whether a clever type is worth what it costs the person who touches it next.
**Primary source:** [TypeScript wiki, Performance](https://github.com/microsoft/TypeScript/wiki/Performance)
**Prerequisites:** [Lesson 41](0041-inference-for-library-apis.md), [Lesson 19](0019-reading-a-tsconfig.md)

## Warm-up

1. ▢ Lesson 26 said a type parameter earns its place only when the caller learns something from it. In one sentence, what does a caller learn from a type that only its author can read?

<details markdown="1"><summary>Check</summary>

Nothing beyond what a plain comment would have told them, and they pay for it twice: once when the error message that type produces is harder to read than a plainer type's would be, and again if they are ever the one who has to change it. This lesson is about measuring that trade instead of assuming it.

</details>

## Know this

Lessons 36 to 41 gave you the mechanics: mapped types, conditional types, `infer`, template literal types, variance, and a signature designed for its callers. This lesson gives you a way to decide when to stop using them, and the decision rests on a number you produce yourself rather than a rule of thumb.

### How to measure, concretely

The compiler will tell you what a type costs to check, if you ask it. `tsc --diagnostics` prints a short summary after a build: how many types the checker created, how many instantiations it performed, and how long checking took. `tsc --extendedDiagnostics` prints the same summary in more detail. `tsc --generateTrace <dir>` writes a trace for a viewer, for the rare case where the summary numbers say something is expensive but not which type is responsible.

Here is real output, from a project built for this lesson, running a single file with a recursive type in it:

```text
Files:               64
Lines:            56152
Identifiers:      48106
Symbols:         897589
Types:           443629
Instantiations:  440786
Memory used:    317488K
Memory allocs:  1056967
Parse time:      0.017s
Bind time:       0.007s
Check time:      0.448s
Emit time:       0.000s
Total time:      0.473s
```

`--extendedDiagnostics` on this single small file printed the same fields; the extra breakdown it adds shows up on a multi-file project, so save it for a real one rather than a scratch file. `--generateTrace trace` wrote four files: `trace.json`, `legend.json`, and, in this version of the compiler, several `types_N.json` files rather than one, a consequence of the checker working in parallel. Load `trace.json` in a trace viewer once `--diagnostics` has already told you something is worth chasing; it names the type responsible.

### The number that used to end the argument

Here is the type that produced the summary above, a tail-recursive type that builds a tuple one element at a time:

```ts
type BuildTuple<L extends number, T extends unknown[] = []> =
  T['length'] extends L ? T : BuildTuple<L, [...T, unknown]>;

type Target = BuildTuple<900>;
```

That is 900 levels of recursion, and the summary above is what checking it actually costs: 443629 types, 440786 instantiations, checked in 0.448 seconds. A prior measurement of the same type reported 443626 types, 439881 instantiations, and a check time of 0.479 seconds; the two runs agree closely, and the small difference is exactly what you would expect between machines rather than evidence that either number is wrong.

Read what that says. Nearly half a million instantiations, checked in under half a second. The old argument against clever types, that they make the build crawl, does not carry the weight it used to on this compiler. If your instinct is to reject a conditional or mapped type because "it will slow the build down", that instinct is now a claim, and a claim needs a number behind it. Two things follow. First, instantiations is the number to watch: it grows without bound as recursion or union size grows, while check time, on a fast compiler, can stay small for a while even as instantiations climb. Second, "this type is slow" is a sentence you back with a `--diagnostics` run or do not say. A reader who finishes this lesson and repeats the old folklore unmeasured has not actually read it.

### The ceiling is exact

Speed is not unlimited, and the compiler still refuses recursion past a fixed depth. The same `BuildTuple` type, run at a target length of 999, compiles cleanly. Run at a target length of 1000, it fails:

```text
error TS2589: Type instantiation is excessively deep and possibly infinite.
```

That boundary held at 1500 too, which rules out a fluke at exactly 1000. So the ceiling is not a vague sense that "deep recursion is risky"; it is a specific number, and a type that walks up to it is one recursive step away from breaking for a caller who passes a slightly larger input. Knowing the number precisely tells you how much margin a recursive type has left, rather than just that some margin exists.

### What actually costs you

With the speed argument weakened, the argument that was always the stronger one is left standing on its own: maintenance. A type nobody on the team can read costs something every time the code near it changes, because a change has to be understood before it can be made safely, whether or not the build itself is fast.

The error messages make the cost visible. Here is a small, ordinary mismatch against a named interface:

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

Here is a mismatch against a `BuildTuple<40>`, the same recursive type at a smaller size, assigned to `string`:

```text
error TS2322: Type '[unknown, unknown, unknown, unknown, unknown, unknown, unknown,
unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown,
unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown,
unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown, unknown,
unknown, unknown, u...' is not assignable to type 'string'.
```

The compiler truncated that second message, and it was still too long to read at a glance. That is the honest cost of a clever type: not that the build is slow, but that the day-to-day feedback it gives back is worse, on every mismatch, for as long as the type stays in the codebase. Lesson 40 raised variance annotations as a way to lower checking cost without changing what a type expresses; that trade belongs there, and instantiation count and readability, not raw speed, are what you are actually managing here.

Before you keep a clever type, apply one concrete test: cover its definition, look only at where it is used, and try to say what it evaluates to for a new input. If you cannot do that in under a minute for your own type, written five minutes ago, the person who inherits it in a year will not manage it either, and the long error above is a preview of their first encounter with it.

### Who is better off

Name the caller plainly, because that is the point of the whole stage. It is your colleague reviewing the pull request, and it is you in six months, having forgotten the trick that felt obvious today. The benefit of stopping before the clever version is a type someone else can change without asking you first. Most of that benefit will not show up in a measurement; it shows up as a review that goes faster and a bug fix that does not need you personally. One part of it does measure directly: a simpler type produces a shorter, more specific error, as the two messages above showed, and a shorter error is one a reader can act on without scrolling.

### Stage 6, closed

Look back across lessons 36 to 41 and name what changed. You can compute a type from another type, with a mapped type. You can branch on a type, with a conditional type. You can extract a type from a position inside another type, with `infer`. You can describe a shape of string, with a template literal type. You can read an assignability error and tell which direction it complains about, which is what a variance annotation documents. And you can design a signature that serves its callers rather than its author, lesson 41's job. The stage's completion criterion is met: you write an API whose types serve its callers, and you now decide, by measurement rather than taste, when to stop reaching for more type than the job needs.

Stage 7 is judgment: publishing a type surface to people you do not work with directly, deciding what counts as a breaking change when the change is only to a type, and reviewing someone else's types with the same rigour you would want applied to your own. This lesson does not touch that ground. It only makes sure you arrive at it able to weigh a clever type honestly instead of by reputation.

## Practice

1. ▢ A teammate says a conditional type "will slow the build down" and offers no numbers. What is the one command you would ask them to run before agreeing, and what two figures in its output actually matter?

<details markdown="1"><summary>Check</summary>

`tsc --diagnostics` (or `--extendedDiagnostics`) on a file that exercises the type. The instantiation count matters most, since it is the figure that grows without bound as recursion or a union gets bigger; check time matters too, but a fast check time today does not guarantee a fast one after the type grows further, so instantiations is the earlier warning.

</details>

2. ▢ `BuildTuple<L, T>` from this lesson is asked to build a tuple of length 950. Predict: does it compile?

<details markdown="1"><summary>Check</summary>

Yes. The verified ceiling for this recursive type is a target length of 999 compiling and 1000 failing with `TS2589`, so 950 is comfortably inside the limit.

</details>

3. ▢ The same type is asked to build a tuple of length 1000. Predict the exact error code, and name one length you could try to confirm the failure is a real ceiling rather than a fluke at exactly 1000.

<details markdown="1"><summary>Hint</summary>

The ceiling was checked again well past 1000 to rule out a coincidence at that particular number.

</details>

<details markdown="1"><summary>Check</summary>

`TS2589: Type instantiation is excessively deep and possibly infinite.` Trying a much larger length, such as 1500, still fails the same way, which confirms the compiler is enforcing a real depth limit rather than tripping on something specific to 1000.

</details>

4. ▢ Two mismatches produce these errors: `Type 'string' is not assignable to type 'number'.` and a several-line error listing dozens of `unknown` entries in a tuple before being cut off. Which type is more expensive to maintain, and is that expense about compile speed?

<details markdown="1"><summary>Check</summary>

The tuple type is more expensive to maintain, and the expense is about readability, not speed. Both types can check in well under a second; the difference is that every future mismatch against the tuple type hands the next reader an error they have to squint at, while the plain type's error is immediately actionable.

</details>

5. ▢ You are reviewing a pull request that adds a recursive conditional type with no comment. Name the one-minute test from this lesson you would apply before approving it, and what result would make you ask for a rewrite.

<details markdown="1"><summary>Check</summary>

Cover the type's definition, look only at where it is called, and try to state what it evaluates to for a new input. If you cannot do that within a minute for a type someone just wrote, ask for a rewrite or a comment, because the person who touches this code in a year, possibly the author themselves, will fail the same test with less context than you have right now.

</details>

## Real-world reps

- [ ] Find a type in a codebase you maintain that took you more than a few seconds to read, write a minimal file that exercises it, and run `tsc --diagnostics` against it; note the instantiation count.
- [ ] Take one error message your own types currently produce and check whether it is short enough to act on without scrolling; if it is not, decide whether the type is worth that cost.
- [ ] Tomorrow: the next time you review a pull request touching a generic, conditional, or mapped type, apply the one-minute readability test from this lesson before you approve it.

## Going further

- [TypeScript wiki, Performance](https://github.com/microsoft/TypeScript/wiki/Performance), the full page beyond the flags this lesson used
- [Type Challenges](https://github.com/type-challenges/type-challenges), useful for practising the mechanics from lessons 36 to 39, not as a model for a type you would commit to a shared codebase
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
