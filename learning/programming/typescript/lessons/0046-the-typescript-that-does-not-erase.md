---
title: 46. The TypeScript That Does Not Erase
description: Four features that emit code you did not ask for, and the flag that names them
type: lesson
---

# Lesson 46. The TypeScript That Does Not Erase

**Mission link:** Reviewing someone else's pull request means judging `enum`, `namespace`, a decorator and a parameter property by what they actually compile to, not by how comfortable they look on the page.
**Primary source:** [TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
**Prerequisites:** [Lesson 29](0029-nothing-survives-to-run-time.md), [Lesson 3](0003-prototypes-and-classes.md)

## Warm-up

1. ▢ Lesson 29 showed that an interface, a generic argument, a brand and an assertion all vanish once compiled, while a class survives because `instanceof` needs its constructor to exist at run time. In one sentence, why was the class the exception rather than a hole in the rule?

<details markdown="1"><summary>Check</summary>

Because a class was never purely a type in the first place. The same declaration that gives the compiler a type also gives the runtime the constructor function `new` calls, so what survives is the value half of the declaration, not a type that somehow escaped erasure.

</details>

## Know this

### The frame: `erasableSyntaxOnly`

Twenty-nine lessons ago the workspace put down a premise worth restating precisely: interfaces, type aliases, generic arguments, brands and assertions all vanish once the compiler finishes, and a class survives only because its constructor was always a value as well as a type. That premise held everywhere in stages 1 to 6. It does not hold for four constructs still in daily use, and the compiler now names them directly rather than leaving the judgment to house style. Ask it what `--erasableSyntaxOnly` is for, and it answers in one line: "Do not allow runtime constructs that are not part of ECMAScript." Read that carefully. The flag is not a taste preference about `enum` looking old-fashioned; it is the compiler drawing a boundary around its own output and refusing to cross it. A construct is erasable when compiling it produces nothing beyond the plain JavaScript expression underneath, exactly what lesson 29 measured for everything else. A construct fails the flag when compiling it has to invent JavaScript that was not in the source: an object built at run time, a wrapped module, an assignment a constructor never wrote. Once a codebase turns this flag on, writing one of the four is a build failure rather than a style note, which is a far stronger footing to review from than "I would not have written it that way."

### The banned four, verified

Compile each of these on its own with `--erasableSyntaxOnly`, and every one reports the same code.

```ts
enum Colour { Red, Green }
```

```ts
const enum Direction { Up = 1 }
```

```ts
namespace Utils {
  export const version = 1;
}
```

```ts
class Box {
  constructor(private size: number) {}
}
```

```text
error TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.
```

One code, four constructs, and the repetition is the point: the compiler is not ranking them by severity, it is applying one rule, "does this need JavaScript beyond what ECMAScript itself defines", and all four answer yes. `const enum` might look safer, since the handbook advertises it as inlined at every use site with no object left behind, but the flag carves out no exception for it, so treat it as no safer than a plain `enum` for this purpose.

### What an `enum` actually emits

Compile the exported version of the plain `enum` above without the flag, with `--outDir`, and read the file `tsc` actually writes.

```text
export var Colour;
(function (Colour) {
    Colour[Colour["Red"] = 0] = "Red";
    Colour[Colour["Green"] = 1] = "Green";
})(Colour || (Colour = {}));
```

That is not a constant lookup table; it is a mutable `var`, an immediately invoked function, and two statements that write both directions of a mapping onto it, `Colour.Red` to `0` and `Colour[0]` back to `"Red"`. Nothing in the source asked for a reverse mapping. Writing `enum Colour { Red, Green }` reads like a declaration of a closed set of values, the same job a type does everywhere else in this workspace, and it quietly hands back a runtime object with behaviour nobody wrote by hand.

Lesson 10 already gave you the tool that says the same thing without the surprise: a union of string literal types.

```ts
type Colour = "Red" | "Green";
```

That line erases completely, exactly as lesson 29 found for every other type-level construct, so there is nothing at run time to inspect, no reverse mapping, and no way to iterate the members without writing a separate list of them yourself. If the reverse mapping or the iteration is genuinely needed, `as const` on a plain object keeps a real value without inventing one behind your back.

```ts
const Colour = { Red: "Red", Green: "Green" } as const;
type Colour = (typeof Colour)[keyof typeof Colour];
```

This keeps `Object.keys(Colour)` and `Colour.Red` working, since it is an ordinary object that happens to survive compilation as a value, but it still does not give you the numeric reverse mapping an `enum` built for free, and the type has to be derived from the object with `keyof` and `typeof` rather than declared up front. Choose between the two literal-type styles on what the caller actually needs to do at run time, not on which one looks closest to the `enum` it replaces.

### Decorators, and the distinction that matters

Compile a standard decorator, the kind written as `@logged` above a class method, with the same `--erasableSyntaxOnly` flag used against all four banned constructs above, and it is silent: no diagnostic, a clean pass. That is not an oversight in the flag. A standard decorator is itself an ECMAScript feature now, defined by the same process that defines classes and modules, so the code it produces is JavaScript's own semantics for wrapping a method, not a TypeScript invention layered on top of it. The flag's own line was "not part of ECMAScript", and a standard decorator simply is part of it, so it never belonged in the same bucket as `enum`, `namespace` and a parameter property. A review comment that treats "it is a decorator" as automatically suspicious, on the same grounds as those three, is wrong about where the line actually sits.

The trap runs the other way. Compile the same decorator with `--experimentalDecorators`, the older flag that predates the ECMAScript proposal, and it fails.

```text
error TS1241: Unable to resolve signature of method decorator when called as an expression.
```

The legacy flag expects a decorator function written to the old calling convention, and a standard decorator is written to the new one, so the two are not compatible dialects of the same idea, they are different features that happen to share the `@` syntax. The practical review question is therefore not "should this codebase use decorators" but "which decorator proposal is this codebase actually on". If `experimentalDecorators` is still set in the `tsconfig.json`, that setting is the liability to raise, and the fix is migrating the flag off rather than removing the decorators it was written for.

### What a reviewer should actually write

Judgment means writing something more specific than "avoid this" for each of the four, and the evidence above supports four different verdicts. A parameter property is the smallest of the four trades: `constructor(private size: number) {}` is genuinely shorter to read than the assignment written out by hand, but lesson 29 already showed what a constructor parameter costs once compiled, an explicit assignment that TypeScript writes for you rather than one the author wrote themselves, so under `erasableSyntaxOnly` it is refused for the same reason as `enum`, not because it is dangerous but because it is one more line of generated code hiding behind a shorthand. A `namespace` in code written today is almost always a module from lesson 7 dressed in older syntax, from before the language had one; say so plainly and ask why the file is not just using `import` and `export`. An `enum` is a value pretending to be a type, and the fix is not "avoid it" as a slogan but naming the reverse mapping it quietly relies on and offering the union or the `as const` object that covers what the code actually does with it. A standard decorator earns no free pass just because it compiles clean under the flag: it is legitimate ECMAScript, but it is still indirection wrapping a method, and it needs the same justification you would ask of any other layer between a caller and the code that runs, a reason grounded in what it does rather than in which era it was written.

## Practice

1. ▢ A file contains only `namespace Utils { export const version = 1; }`, compiled with `--erasableSyntaxOnly`. Predict the diagnostic, with its `TS` number.

<details markdown="1"><summary>Check</summary>

`TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.` The same code the plain `enum`, the `const enum` and the parameter property all get, because a `namespace` also needs runtime JavaScript beyond what ECMAScript's own module syntax defines.

</details>

2. ▢ Given `enum Colour { Red, Green }`, compiled with default settings, predict what `Colour[0]` evaluates to at run time.

<details markdown="1"><summary>Check</summary>

`"Red"`. The compiled function writes the mapping in both directions, `Colour.Red` to `0` and `Colour[0]` back to `"Red"`, so indexing the object numerically recovers the member's name even though nothing in the source asked for that reverse lookup.

</details>

3. ▢ `class Box { constructor(private size: number) {} }` is compiled twice, once with default settings and once with `--erasableSyntaxOnly`. Predict both outcomes.

<details markdown="1"><summary>Check</summary>

With default settings it compiles cleanly, and the emitted constructor writes `this.size = size;` for you, the assignment lesson 29 showed a constructor parameter produces. With `--erasableSyntaxOnly` it fails with `TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.`, because that generated assignment is exactly the runtime code the flag refuses to allow from a parameter property.

</details>

4. ▢ A class method carries a standard decorator, `@logged`. Predict the outcome of compiling it with `--erasableSyntaxOnly`, and separately with `--experimentalDecorators`.

<details markdown="1"><summary>Hint</summary>

One flag asks whether the syntax is part of ECMAScript. The other asks whether the decorator function matches an older calling convention that predates the ECMAScript proposal.

</details>

<details markdown="1"><summary>Check</summary>

Under `--erasableSyntaxOnly` it compiles cleanly, because a standard decorator is itself an ECMAScript feature, not a TypeScript invention. Under `--experimentalDecorators` it fails with `TS1241: Unable to resolve signature of method decorator when called as an expression.`, because that legacy flag expects the old calling convention and a standard decorator is written to the new one.

</details>

5. ▢ A pull request adds `enum Status { Pending, Done }`, used only to compare a variable against the two known values, with no iteration over the members and no reverse lookup anywhere. What would you write in the review, and what would you ask for instead?

<details markdown="1"><summary>Check</summary>

Point out that the `enum` builds a mutable runtime object with a reverse mapping nobody uses, the exact shape shown earlier in this lesson. Since nothing in the code iterates the members or looks a name up from a value, a union of string literals covers everything actually used: `type Status = "Pending" | "Done";`. It erases completely, so nothing is left at run time, and it matches what the code does rather than what an `enum` happens to provide for free.

</details>

## Real-world reps

- [ ] Search a codebase you can see for `enum` and for `namespace`, and for each hit, decide whether it is closer to "a closed set of literal values" or "a module written the old way".
- [ ] Compile a file with a constructor parameter property using `--outDir`, read the assignment TypeScript wrote for you, and decide whether the shorthand is worth that line for the code you looked at.
- [ ] Tomorrow: find a `tsconfig.json` you have access to and check whether `experimentalDecorators` is set; if it is, find out whether any decorator in that codebase was actually written for the standard proposal rather than the legacy one.

## Going further

- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/), the page this lesson quotes from, for every other flag not covered here
- [TypeScript Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/overview.html), for when standard decorators and `erasableSyntaxOnly` itself landed
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
