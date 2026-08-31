---
title: 2. Objects Are References
description: const stops rebinding, spread copies one level, and readonly disappears at run time
type: lesson
---

# Lesson 2. Objects Are References

**Mission link:** `readonly` and `const` are the two things people believe make data safe, and neither one stops a mutation. Knowing what actually does is the difference between a defensive copy and a false sense of one.
**Primary source:** [You Don't Know JS Yet: Objects & Classes, chapter 1](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch1.md)
**Prerequisites:** [Lesson 1](0001-values-and-coercion.md)

## Warm-up

1. ▢ Why is `timeout || 30` wrong when `0` is a legal timeout, and what replaces it?

<details markdown="1"><summary>Check</summary>

`||` tests truthiness and `0` is falsy, so the default wins. `??` tests only `null` and `undefined`.

</details>

2. ▢ What does `typeof null` return, and what should you use to identify an array?

<details markdown="1"><summary>Check</summary>

`"object"`, a historical wart. Use `Array.isArray(value)`.

</details>

## Know this

A variable holding an object holds a **reference**. Assignment copies the reference, so two variables can name one object:

```ts
const a = { count: 1 };
const b = a;
b.count = 2;
console.log(a.count);       // 2
```

Objects are compared by identity, never by contents:

```ts
console.log({ a: 1 } === { a: 1 });     // false, two objects
console.log([1] === [1]);               // false
```

There is no built-in structural equality. Comparing by `JSON.stringify` is the common shortcut and it is wrong in ways that matter: key order changes the result, `undefined` values disappear, `Date` becomes a string, and `NaN` becomes `null`.

### `const` is about the binding

```ts
const config = { retries: 3 };
config.retries = 5;         // fine
config = { retries: 5 };    // TypeError: Assignment to constant variable
```

`const` prevents rebinding the name. It says nothing about the object. That is the same distinction as lesson 1's primitives against objects, seen from the declaration side.

To freeze the object itself, `Object.freeze` exists and is shallow:

```ts
const frozen = Object.freeze({ tags: ["a"] });
frozen.tags.push("b");      // works, the array was never frozen
```

### Spread copies one level

```ts
const original = { name: "svc", tags: ["a"] };
const copy = { ...original };
copy.name = "other";            // original.name unchanged
copy.tags.push("b");            // original.tags IS changed
```

Every convenient copy syntax is shallow: object spread, array spread, `Object.assign`, `Array.prototype.slice`, `Array.from`. For a genuinely independent tree use `structuredClone(value)`, which is built in, handles cycles, and copies `Map`, `Set`, `Date` and typed arrays. It refuses functions and class instances lose their prototype, so it is a data-copying tool rather than an object-copying one.

### `readonly` is a compile-time claim

```ts
interface Config { readonly tags: readonly string[] }

function handle(c: Config) {
  c.tags.push("x");         // compile error
}
```

The error is real and the guarantee is not. `readonly` is erased, so a caller in plain JavaScript, or a value arriving from `JSON.parse`, or an `as` assertion anywhere in the chain, can all mutate it at run time with nothing to stop them. Stage 5 is about exactly this boundary.

So there are two separate questions to keep apart, and each has its own tool:

| Question | Tool |
|---|---|
| can this name be reassigned | `const` |
| does the compiler reject writes | `readonly` |
| can the object be changed at run time | `Object.freeze`, or not sharing it |
| is this copy independent | `structuredClone`, or a hand-written deep copy |

## Practice

1. ▢ Predict the output.

   ```ts
   const original = { name: "svc", tags: ["a"] };
   const copy = { ...original };
   copy.name = "other";
   copy.tags.push("b");
   console.log(original);
   ```

<details markdown="1"><summary>Hint</summary>

Ask separately for each of the two properties whether the spread copied the value or the reference.

</details>

<details markdown="1"><summary>Check</summary>

`{ name: 'svc', tags: [ 'a', 'b' ] }`.

`name` held a string, which is a primitive, so the copy got its own. `tags` held a reference, so both objects point at one array and the `push` is visible through both.

</details>

2. ▢ Which of these mutations succeed?

   ```ts
   const c = Object.freeze({ n: 1, inner: { m: 2 }, list: [1] });
   c.n = 9;
   c.inner.m = 9;
   c.list.push(2);
   ```

<details markdown="1"><summary>Check</summary>

The first fails, silently in sloppy mode and with a `TypeError` in strict mode, which includes every module. The second and third succeed.

`Object.freeze` freezes the object's own properties. It does not reach the objects those properties refer to, which is the same one-level rule as spread.

</details>

3. ▢ You need to compare two objects by contents. Which is acceptable?

   - a) `a === b`
   - b) `JSON.stringify(a) === JSON.stringify(b)`
   - c) A hand-written comparison of the fields you care about
   - d) `Object.keys(a).length === Object.keys(b).length`

<details markdown="1"><summary>Check</summary>

**c)** is the honest answer for application code.

Option a compares identity. Option b works often enough to be tempting and fails on key order, `undefined` values, `Date`, `NaN` and anything with a cycle. Option d compares nothing but shape size.

A library that implements deep equality is the other reasonable answer. The point of the exercise is that the language provides none, so a comparison is a decision you make rather than a syntax you reach for.

</details>

4. ▢ This function is meant to leave the caller's data alone. Name the defect and fix it.

   ```ts
   function withDefault(config: { tags: string[] }) {
     const next = { ...config };
     next.tags.push("default");
     return next;
   }
   ```

<details markdown="1"><summary>Check</summary>

The spread copied the reference to `tags`, so the `push` mutates the caller's array.

```ts
function withDefault(config: { tags: string[] }) {
  return { ...config, tags: [...config.tags, "default"] };
}
```

Copying the one nested value that gets modified is usually better than `structuredClone` here: it is cheaper, it states which part of the shape matters, and it does not silently copy things the function has no business duplicating.

</details>

5. ▢ A reviewer says a parameter typed `readonly string[]` makes the function safe to call with shared state. What is right about that, and what is wrong?

<details markdown="1"><summary>Check</summary>

Right: within a type-checked codebase, the compiler rejects `push`, `sort`, index assignment and everything else that mutates, so the function's own author cannot mutate it by accident. That is real value, and it costs nothing.

Wrong: it is not a run-time guarantee. `readonly` is erased at compile time, so an untyped caller, a value from `JSON.parse`, or one `as string[]` anywhere in the chain removes the protection with no diagnostic. If the function must not mutate shared state under any circumstances, the answer is to copy on entry or to freeze the array at the boundary.

</details>

## Real-world reps

- [ ] Run the spread example and the `Object.freeze` example. Then run the freeze example again in a module, where strict mode makes the failed assignment throw instead of doing nothing.
- [ ] Try `structuredClone` on an object containing a `Date`, a `Map`, and a function. Note which survives and which throws.
- [ ] Tomorrow: find a function in code you know that spreads an argument and then modifies something nested. That is the bug from practice 4, in the wild.

## Going further

- [You Don't Know JS Yet: Objects & Classes, chapter 1](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch1.md): object fundamentals, property definitions and descriptors
- [Ordinary object internal methods](https://tc39.es/ecma262/#sec-ordinary-object-internal-methods-and-internal-slots): what a property access actually performs
- [Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html): how the type system describes these values, including `readonly`
- [Glossary](../GLOSSARY.md): `Type` is pinned there, and this lesson is the first place the compile-time boundary bites
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
