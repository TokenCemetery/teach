---
title: 30. unknown at the Edge
description: Find every place a value arrives from outside, and give each one the only honest type
type: lesson
---

# Lesson 30. unknown at the Edge

**Mission link:** Owning a codebase means being able to name, for any value inside it, the exact point where it entered from outside, and to say honestly what has been checked about it since.
**Primary source:** [The TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
**Prerequisites:** [Lesson 29](0029-nothing-survives-to-run-time.md), [Lesson 17](0017-unknown-instead-of-any.md)

## Warm-up

1. ▢ Lesson 17 established that a `catch` variable is typed `unknown`, because a `throw` can hand you anything and the language refuses to pretend otherwise. `JSON.parse` also hands you a value the compiler never checked. Predict its declared return type from that same suspicion, and say whether it matches the choice made for `catch`.

<details markdown="1"><summary>Check</summary>

It does not match. `JSON.parse` is declared to return `any`, not `unknown`. A `catch` variable gets the honest type because the language enforces that choice; `JSON.parse` is an ordinary library function, and its authors chose the type that asks nothing further of you. This lesson finds every place that same choice was made on your behalf, and undoes it.

</details>

## Know this

### Where a boundary actually is

A boundary is any point where a value enters your program from somewhere the compiler did not check: bytes from a network, a variable set by whoever launched the process, a command-line argument, an exception thrown by code you did not write. Inside the boundary, a type is an argument the compiler has verified. Outside it, a type is a hope, because nothing forced the outside world to agree with your declaration before handing the value over. Lesson 29 already gave the reason this matters: none of this checking survives into the running program, so the moment a value crosses a boundary unchecked, the guarantee becomes an assumption nobody stated out loud. What follows is a survey of where those points actually are, and what each one lies about by default.

### The inventory of edges

Every one of these is a place a value arrives from outside your own code, and each one is worth knowing by name because a codebase that has never listed them tends to trust all of them by accident.

- **`JSON.parse`**: declared to return `any`. Covered below in full.
- **A network response body**, such as the `json()` method on a fetch response: declared `Promise<any>`, the same lie as `JSON.parse`, one layer further from the call site.
- **Reading a file**: declared to return a `string` or a `Buffer`, and it genuinely is one. The lie is not in the type, it is in the content: nothing there says the string holds valid JSON or a well-formed configuration.
- **Environment variables**: covered below, and the surprising case in this stage.
- **Command-line arguments**: an array of strings. Reading an element by a fixed index types as a plain `string`, present or not, the same family as ordinary array indexing, one of the checks `strict` leaves out per lesson 16.
- **A `catch` variable**: `unknown`, exactly as lesson 17 established.
- **A callback invoked by a third party**: typed however you or the library declared its parameters, and nothing forces the invoker to actually pass that shape. The declaration is a request, not an inspection.
- **A database or message-queue payload**: typically typed by a generic parameter you supply yourself, such as a row type. The compiler trusts the parameter; it cannot ask the database whether a column was dropped in the last migration.

### `JSON.parse`, the centrepiece

Every reader has already crossed this edge carelessly, because nothing warns you when you do:

```ts
const raw = '{"a":1}';
const parsed = JSON.parse(raw);
console.log(parsed.b.toUpperCase());
```

`tsc --strict --noEmit` on this reports nothing, exit code `0`. `parsed` is `any`, so `parsed.b` is `any`, so calling `.toUpperCase()` on it is a use the compiler accepts from any value whatsoever. Run it and the truth arrives late:

```text
TypeError: Cannot read properties of undefined (reading 'toUpperCase')
```

There is no `b` in `{"a":1}`, so `parsed.b` is `undefined`, and calling a method on `undefined` throws. `any` is not a description of what `JSON.parse` returns, it is an instruction to stop checking from that point on.

The fix is to refuse the type on the way in:

```ts
function parseConfig(raw: string): unknown {
  return JSON.parse(raw);
}
const config = parseConfig('{"port":3000}');
console.log(config.port);
```

That last line fails to compile: `error TS18046: 'config' is of type 'unknown'.` The function's own return type overrides what `JSON.parse` claims, so the property read is refused exactly as one was in lesson 17, before assignability even comes into it. You are not allowed to proceed until something narrows it:

```ts
if (
  typeof config === "object" &&
  config !== null &&
  "port" in config &&
  typeof config.port === "number"
) {
  console.log(config.port.toFixed(0));
}
```

This compiles clean, using nothing beyond the narrowing operators lesson 12 already gave you: `typeof`, a null check, and `in`. Writing that chain by hand every time is the tedium that motivates lesson 31, which owns the shorter way to say it. What this lesson owns comes first: the return type has to be `unknown`, or the property read from the first example slips straight through.

### Environment variables, told straight

The expectation is usually that an environment variable is declared a plain `string`, so the missing case has to be caught by hand. Running this against a project with the standard Node type declarations installed says otherwise:

```ts
const port: string = process.env.PORT;
```

```text
error TS2322: Type 'string | undefined' is not assignable to type 'string'.
  Type 'undefined' is not assignable to type 'string'.
```

`NodeJS.ProcessEnv` is telling the truth: every property on it is declared `string | undefined`, because its authors modelled it as a dictionary indexed by an arbitrary key that is not guaranteed to have been set. Unlike `JSON.parse`, this edge is not lying: the compiler already refuses the assignment, correctly, for a value that may genuinely be absent.

Where the lie creeps back in is self-inflicted, through an assertion that silences the honest declaration on command:

```ts
const apiKey = process.env.API_KEY as string;
console.log(apiKey.toUpperCase());
```

This compiles. Run it with `API_KEY` unset and you get the same failure as the `JSON.parse` example: `TypeError: Cannot read properties of undefined (reading 'toUpperCase')`. Lesson 18 already told you what `as` does: it switches off checking rather than converting anything, and here it switches off a check the declaration gave for free. The honest version keeps that check:

```ts
const port = process.env.PORT;
if (typeof port === "string") {
  console.log(port.toUpperCase());
} else {
  throw new Error("PORT is not set");
}
```

The lesson here is not that environment variables need `unknown`; it is that a boundary can already be declared honestly, and the discipline is still the same: do not spend an assertion undoing a check somebody already gave you.

### Why `any` is the wrong instrument here

Lesson 17 already drew this line, and it is worth restating where it bites hardest. `any` at a boundary does not mark the boundary, it removes it: every expression built on top of an `any` value is itself unchecked, silently, with no diagnostic pointing at the region that stopped being verified. `unknown` marks the boundary instead, accepting the value on the way in exactly as `any` would, then refusing every operation on it until something narrows it, producing `TS18046` right where checking would otherwise have stopped. It does not perform the check for you, that is lesson 31's subject, but it guarantees the check has to happen somewhere, rather than never.

### The discipline to leave with

List your program's edges once, on paper: every `JSON.parse`, response body, file read, environment variable, command-line argument, third-party callback, and payload read out of a database or a queue. Give each one the type `unknown` at the point it enters, even where, as with `process.env`, the declaration already happens to be honest, because writing the boundary down is what stops the next person reaching past it with an assertion. Most codebases have never written that list down, which is why an unchecked `any` sits quietly at one of these points until the day the shape it assumed turns out to be wrong.

## Practice

1. ▢ Predict whether this compiles, and if it does not, quote the diagnostic with its `TS` number.

   ```ts
   const raw = '{"name":"Ada"}';
   const settings = JSON.parse(raw);
   console.log(settings.theme.length);
   ```

<details markdown="1"><summary>Check</summary>

It compiles, exit code `0`, no diagnostic. `JSON.parse` returns `any`, so `settings` and `settings.theme` are both `any`, which lets `.length` through regardless of whether `theme` exists. Run it and `settings.theme` is `undefined`, so reading `.length` off it throws `TypeError: Cannot read properties of undefined (reading 'length')` at run time.

</details>

2. ▢ Predict whether this compiles.

   ```ts
   function parseConfig(raw: string): unknown {
     return JSON.parse(raw);
   }
   const config = parseConfig('{"port":3000}');
   if (typeof config === "object" && config !== null && "port" in config) {
     console.log(config.port.toFixed(0));
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what type `in` gives `config.port` once `typeof` and the null check have already run, then ask whether calling `.toFixed` on that is any different from calling it on an unnarrowed `unknown` value.

</details>

<details markdown="1"><summary>Check</summary>

No. `error TS18046: 'config.port' is of type 'unknown'.` `in` narrows `config` to an object known to have a `port` key, but not what type that key holds, so `config.port` is itself `unknown` and refuses `.toFixed`, the same refusal an unnarrowed `unknown` value gave a method call in lesson 17. The fix in Know this adds one more check, `typeof config.port === "number"`, to narrow that last `unknown` too.

</details>

3. ▢ Predict the diagnostic, with its `TS` number, for this line in a project with the standard Node type declarations installed.

   ```ts
   const port: string = process.env.PORT;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string | undefined' is not assignable to type 'string'.` `process.env` is declared a dictionary of `string | undefined`, so every read off it carries the possibility of being unset, and the assignment is refused before the value is used. This is the one edge in the inventory whose declaration is already honest.

</details>

4. ▢ Predict whether this compiles, and if it does, predict what running it prints when only two arguments were passed on the command line.

   ```ts
   const third: string = process.argv[5];
   console.log(third.toUpperCase());
   ```

<details markdown="1"><summary>Check</summary>

It compiles, exit code `0`. `process.argv` is declared `string[]`, and a fixed index off an array types as a plain `string`, present or not, the array-indexing gap lesson 16 already named. Nothing is printed; the program throws instead, `TypeError: Cannot read properties of undefined (reading 'toUpperCase')`, because `process.argv[5]` is `undefined` at run time.

</details>

5. ▢ Predict whether this compiles.

   ```ts
   async function loadTheme(url: string) {
     const res = await fetch(url);
     const body = await res.json();
     return body.toUpperCase();
   }
   ```

<details markdown="1"><summary>Check</summary>

Yes, cleanly. `res.json()` is declared `Promise<any>`, the same declaration `JSON.parse` carries, so `body` is `any` and `.toUpperCase()` compiles whether or not the response body is ever a string. A network response body belongs on the same list as `JSON.parse`, and needs the same `unknown` return type and the same narrowing before use.

</details>

## Real-world reps

- [ ] Find every `JSON.parse` call in a project you can see. For each, check whether the result is used before anything narrows it, and note which calls are one malformed response away from a failure the compiler would have caught had the return been typed `unknown`.
- [ ] Find every `process.env.SOMETHING` your code reads directly, and check whether it is read with an assertion, a default, or an actual check for `undefined`. Note which would fail silently the day someone forgets to set that variable.
- [ ] Tomorrow: write the list Know this asked for, every boundary in one real program you maintain, and mark which already carry `unknown` at the point of entry and which still carry `any` or a bare assertion instead.

## Going further

- [TypeScript Handbook, More on Functions, `unknown`](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown), for the type this whole lesson depends on
- [Node.js documentation, `process.env`](https://nodejs.org/api/process.html#processenv), for the runtime behaviour behind the declaration this lesson tested
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
