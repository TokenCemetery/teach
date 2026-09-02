---
title: 23. Exhaustiveness With never
description: Adding a member to a union should break every switch that ignored it, and one line makes it so
type: lesson
---

# Lesson 23. Exhaustiveness With never

**Mission link:** Owning a codebase means that when someone adds a member to a union six months from now, every `switch` that ignored it should fail to compile instead of quietly doing the wrong thing at runtime.
**Primary source:** [Narrowing, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
**Prerequisites:** [Lesson 22](0022-discriminated-unions.md), [Lesson 12](0012-narrowing.md)

## Warm-up

1. ▢ Lesson 22 gave you a `Shape` union with a `kind` field, narrowed inside a `switch` so that each case saw only the members that arm actually has. Predict what happens if, inside `case "circle":`, you write `s.side` instead of `s.radius`.

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'side' does not exist on type '{ kind: "circle"; radius: number; }'.` Narrowing on `kind` gave that branch exactly the members a circle has, and `side` is not one of them, the same restriction lesson 22 built, seen here from the branch that lost a member.

</details>

## Know this

### `never`: the type with no values

`never` is the type that no value has. Every other type describes some set of values, however large; `never` describes the empty set, so nothing is assignable to it except a value already narrowed all the way down to nothing. Writing `const x: never = someValue` is therefore a claim, checked by the compiler, that `someValue`'s type has narrowed to nothing left. This lesson uses exactly that property; `never` also shows up as the return type of a function that never returns and inside type-level machinery, both for a later stage.

### The technique: handle every case, then check the claim

Take the `Shape` union from lesson 22.

```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius * s.radius;
    case "square":
      return s.side * s.side;
    default:
      const _e: never = s;
      return _e;
  }
}
```

This compiles. Inside `default`, the compiler has already ruled out `"circle"` and `"square"` via the two `case` labels above, so whatever `s` still has at that point is nothing: `never`. Assigning `s` to `_e: never` is the compiler checking that belief out loud, and the same idea works on a plain literal union with no object shape at all. Now add a `triangle` member to `Shape` and leave the switch above unchanged.

```text
error TS2322: Type '{ kind: "triangle"; base: number; height: number; }' is not assignable to type 'never'.
```

`default` used to see `never`; now it sees the leftover `triangle` shape, the one member the two `case` labels do not exclude. Run the same experiment on a bare literal union such as `"a" | "b"` with a third member `"c"` added, and the message shrinks to `error TS2322: Type '"c"' is not assignable to type 'never'.`, no object shape, just the literal. Same mechanism either way; a discriminated union just has more to print.

### Why this is the good failure

That diagnostic does not say "something is wrong with this switch." It names the value left over, `"c"` or the `triangle` shape, at the exact `switch` that failed to handle it. Without the guard, a new member is a silent change: every switch that used to be exhaustive keeps compiling and does the wrong thing for the case nobody told it about, discovered from a bug report rather than a build. With the guard, a new member becomes a list of compile errors, one at every site not yet updated, each naming the member responsible. This is the mechanism behind stage 4's completion criterion, illegal states unrepresentable and the compiler proving it: lesson 22 shaped the type so a bad combination cannot be constructed, and this guard makes the compiler enforce that every consumer kept up. Without the guard, a discriminated union is a convenience; with it, a guarantee.

### What you get without it

It is worth seeing the weaker version so the two are easy to tell apart. Drop the `default` clause and rely on the declared return type to catch a missed case.

```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number }
  | { kind: "triangle"; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius * s.radius;
    case "square":
      return s.side * s.side;
  }
}
```

```text
error TS2366: Function lacks ending return statement and return type does not include 'undefined'.
```

That is a real error, and it catches the missing case here, but read what it says: a return statement is missing, not which case is missing. With several unhandled members you would have to work that out yourself, and there is a case where this signal does not fire at all: a function that returns `void`.

```ts
function log(s: Shape): void {
  switch (s.kind) {
    case "circle":
      console.log("circle", s.radius);
      return;
    case "square":
      console.log("square", s.side);
      return;
  }
}
```

Run that through the compiler and nothing happens: no error, despite `triangle` never being mentioned. A `void` function need not return anything on any path, so falling off the end after an unhandled `case` breaks no rule the return type imposes. This is where a reader who trusts the return-type signal is not covered and does not know it, exactly what the `never` guard closes, since it checks the union directly rather than the return type.

### Where to put the guard

The `default` clause is where it goes in a `switch`, as above. A final `else` of an `if`/`else if` chain plays the same role: `else { const _e: never = s; }` checks whatever is left once every named branch is excluded. Most codebases factor this into a standalone helper rather than repeating `const _e: never = s;` at every site.

```ts
function assertNever(x: never): never {
  throw new Error(`unhandled case: ${JSON.stringify(x)}`);
}

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius * s.radius;
    case "square":
      return s.side * s.side;
    case "triangle":
      return 0.5 * s.base * s.height;
    default:
      return assertNever(s);
  }
}
```

`assertNever` takes a parameter typed `never`, so calling it with anything else is the same check, phrased as a call; leave a member unhandled and the diagnostic moves to the call site: `error TS2345: Argument of type '"c"' is not assignable to parameter of type 'never'.` The body throws rather than returns, and that matters: if every case is handled and the types are honest, `assertNever` is unreachable, dead by construction, and throwing costs nothing. If it does run, a value crossed in from somewhere the compiler could not see, typically a boundary with the outside world, and throwing turns that surprise into an immediate failure at the point it was found rather than a wrong answer computed from a value nobody checked; validating a value at that boundary is a problem the next stage owns.

### The limits, honestly

Everything here is a compile-time check. It proves the code you wrote handles every member the union currently has, and proves it again, automatically, next time the union changes. It proves nothing about a value entering the program from outside, a network response, a parsed file, a database row, since the compiler only ever sees the declared type, not the value; that gap belongs to stage 5. It is also a habit rather than a setting: nothing forces a `never` guard, so it only protects the switches where someone actually wrote one.

## Practice

1. ▢ `type Weather = "sunny" | "rainy"`. A function returns a string for each case, and the `default` clause assigns `const _e: never = w;` before returning `_e`. Does it compile?

<details markdown="1"><summary>Check</summary>

Yes. Both members are excluded by the two `case` labels, so `w` is `never` in `default` and the assignment checks out.

</details>

2. ▢ `"cloudy"` is added to `Weather`, and the function from item 1 is left unchanged. Predict the diagnostic, with its `TS` number.

<details markdown="1"><summary>Check</summary>

`error TS2322: Type '"cloudy"' is not assignable to type 'never'.` `default` no longer sees `never`, since `"cloudy"` is not excluded by either `case`, and that is the one value left over.

</details>

3. ▢ Take the same unhandled-`"cloudy"` function from item 2, but change its return type to `void` and have each handled case end with a bare `return;` instead of a value, with no `default` clause at all. Does it still fail to compile?

<details markdown="1"><summary>Hint</summary>

Ask what a `void` return type actually requires on a path that falls off the end of the function, not what a `number` or `string` return type would require.

</details>

<details markdown="1"><summary>Check</summary>

No, it compiles cleanly. A `void` function is never required to return a value on any path, so falling off the end after the unhandled `"cloudy"` case breaks no rule the compiler checks, and there is no `default` clause to catch it another way. This is the silent gap: a return-type check says nothing here, because the missing case was never the return type's job.

</details>

4. ▢ Using the `assertNever` helper from Know this, `Weather` includes `"cloudy"` and the switch's `default` calls `return assertNever(w);` without handling `"cloudy"`. Predict the diagnostic, with its `TS` number, and say why it differs from item 2's.

<details markdown="1"><summary>Check</summary>

`error TS2345: Argument of type '"cloudy"' is not assignable to parameter of type 'never'.` It is `TS2345` rather than item 2's `TS2322` because the leftover value is now a function argument, checked against `assertNever`'s parameter type, rather than assigned to a `const`. The underlying reason is identical: something wider than `never` met a position that only accepts it.

</details>

5. ▢ Go back to the `Shape` union with `circle`, `square` and `triangle`, and a `switch` whose `default` assigns `const _e: never = s;`, but the `square` case is missing entirely. Predict what the diagnostic names: just the word `"square"`, or something larger, and why.

<details markdown="1"><summary>Check</summary>

Something larger: `error TS2322: Type '{ kind: "square"; side: number; }' is not assignable to type 'never'.` `Shape`'s members are object types, not bare literals, so what is left over in `default` is the whole object shape, not just its discriminant, same mechanism as the clean literal case with a bigger printout.

</details>

## Real-world reps

- [ ] Find a `switch` in your own code, or write one, over a union with three or more members, and add a `default` clause that assigns the selector to `const _e: never`.
- [ ] Add a member to that union on purpose and count how many places light up with `TS2322` or `TS2345` before fixing any of them; that count is what the guard just saved you from finding out in production.
- [ ] Tomorrow: find one function in a real project that returns `void` and switches over a union with no `default`, and check by hand whether every member is handled, since the compiler will not tell you either way.

## Going further

- [TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html), for the union and literal types this lesson's switches close over
- [Effective TypeScript](https://effectivetypescript.com/), for exhaustiveness checks framed as a habit worth building rather than a one-off trick
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
