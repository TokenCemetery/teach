---
title: 1. Values and Coercion
description: Seven primitives, two empties, and an equality operator that converts before comparing
type: lesson
---

# Lesson 1. Values and Coercion

**Mission link:** TypeScript describes values it cannot see at run time. Every serious bug in a typed codebase is a value behaving as JavaScript specifies while the type said otherwise, so the runtime comes first.
**Primary source:** [ECMAScript Language Specification, ECMAScript Language Types](https://tc39.es/ecma262/#sec-ecmascript-language-types)
**Prerequisites:** none, this is the first lesson.

## Know this

JavaScript has seven primitive types and one everything-else. The primitives are `undefined`, `null`, `boolean`, `number`, `bigint`, `string` and `symbol`. Everything not in that list is an object, including arrays and functions.

Primitives are immutable and compared by value. Objects are compared by identity, which is lesson 2.

### Two kinds of nothing

```ts
let a;                  // undefined: no value was ever assigned
const b = null;         // null: a value meaning "deliberately empty"
```

`undefined` is what the language produces: an unassigned variable, a missing property, a parameter that was not passed, a function with no `return`. `null` is what a programmer writes. The distinction is a convention rather than a rule, so a codebase should pick one for "absent" and be consistent, and TypeScript's `strictNullChecks` is what makes that choice enforceable.

One historical wart to memorise, since no reasoning will get you there:

```ts
typeof null           // "object"
typeof undefined      // "undefined"
typeof (() => {})     // "function", though functions are objects
Array.isArray([])     // true; typeof [] is "object"
```

### Numbers are doubles, and `NaN` is not equal to itself

```ts
0.1 + 0.2 === 0.3     // false
0.1 + 0.2             // 0.30000000000000004
Number.MAX_SAFE_INTEGER + 2 === Number.MAX_SAFE_INTEGER + 3   // true

NaN === NaN           // false
Number.isNaN(NaN)     // true, and the only reliable test
[1, 2, 3].indexOf(NaN)        // -1, because indexOf uses ===
[1, 2, NaN].includes(NaN)     // true, because includes uses SameValueZero
```

`number` is a 64-bit float, so integers above 2 to the 53rd lose precision and `bigint` exists for that case. `NaN` failing its own equality test is required by the specification, which is why `Number.isNaN` and `Object.is` exist.

### `==` converts, `===` does not

`===` compares type and value with no conversion. `==` applies the loose-equality algorithm ([spec](https://tc39.es/ecma262/#sec-islooselyequal)), which converts operands until they share a type:

```ts
"1" == 1              // true
0 == ""               // true
0 == "0"              // true
"" == "0"             // false
[] == false           // true
null == undefined     // true
null == 0             // false
```

Read those in pairs and the reason for the rule becomes obvious: `==` is not transitive, so `0 == ""` and `0 == "0"` are both true while `"" == "0"` is false. An operator that cannot be reasoned about transitively has no place in ordinary code.

**Use `===` always, with exactly one idiomatic exception:** `x == null` is true for both `null` and `undefined`, which is a genuinely useful test and is why linters allow it specifically.

### Truthiness, and where it costs you

Falsy: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. Everything else is truthy, including `"0"`, `"false"`, `[]` and `{}`.

The empty array being truthy is the one that surprises people, and the falsy numbers and strings are the ones that cause bugs:

```ts
function connect(timeout?: number) {
  const t = timeout || 30;        // 0 becomes 30
  const u = timeout ?? 30;        // 0 stays 0
}
```

`||` tests truthiness. `??` tests only `null` and `undefined`, which is almost always the question you meant. The same pair applies to member access: `a?.b` short-circuits on `null` and `undefined` only.

## Practice

1. ▢ Predict all six.

   ```ts
   console.log(typeof null);
   console.log(typeof []);
   console.log(0.1 + 0.2 === 0.3);
   console.log(NaN === NaN);
   console.log("" == 0);
   console.log("" === 0);
   ```

<details markdown="1"><summary>Check</summary>

`"object"`, `"object"`, `false`, `false`, `true`, `false`.

The first two are why `typeof` is a poor tool for distinguishing shapes, and why `Array.isArray` exists. The third is binary floating point, not a JavaScript defect. The fourth is required by the specification. The last pair is the whole argument for `===`.

</details>

2. ▢ These three lines cannot all be consistent. Predict them and say what property is violated.

   ```ts
   console.log(0 == "");
   console.log(0 == "0");
   console.log("" == "0");
   ```

<details markdown="1"><summary>Hint</summary>

Ask what each operand is converted to before the comparison happens. The two string comparisons convert differently.

</details>

<details markdown="1"><summary>Check</summary>

`true`, `true`, `false`.

Transitivity is violated: `a == b` and `a == c` hold while `b == c` does not. When one operand is a number, the string is converted to a number, so `""` becomes `0` and `"0"` becomes `0`. When both are strings, no conversion happens and the characters differ.

</details>

3. ▢ Which expression correctly treats `0` as a supplied value?

   - a) `timeout || 30`
   - b) `timeout ?? 30`
   - c) `timeout ? timeout : 30`
   - d) `Boolean(timeout) ? timeout : 30`

<details markdown="1"><summary>Check</summary>

**b)** `timeout ?? 30`.

The other three all test truthiness, and `0` is falsy, so all three replace a deliberate zero with the default. `??` tests only `null` and `undefined`.

</details>

4. ▢ A function receives `value: unknown` and must decide whether it is a real array. Write the check, and say why two obvious alternatives fail.

<details markdown="1"><summary>Check</summary>

`Array.isArray(value)`.

`typeof value === "object"` is true for `null` and for every plain object, so it neither excludes nor identifies arrays. `value instanceof Array` is nearly right and fails across execution contexts, such as a value arriving from another frame or from a worker, because that context has a different `Array` constructor.

`Array.isArray` is specified to answer the question directly, which is why it exists as a static method rather than as an operator.

</details>

5. ▢ Why does an empty array test as truthy, and what should you write instead when you mean "has items"?

<details markdown="1"><summary>Check</summary>

Because truthiness for objects is not defined by their contents. An array is an object, and every object is truthy, so `[]` and `{}` are both true.

Write `items.length > 0`, or `items.length` when a numeric truthiness test is idiomatic in the codebase. The habit worth building is asking what the falsy values of the *type* are before writing a truthiness test at all.

</details>

## Real-world reps

- [ ] Open the [playground](https://www.typescriptlang.org/play) and run the six expressions from practice 1. Then hover each one to see what type TypeScript infers, and note that the inferred type says nothing about the coercion.
- [ ] Write the `connect` function with `||` and call it with `0`. Then switch to `??` and call it again.
- [ ] Tomorrow: search code you know for `||` used to supply a default. Every hit where `0`, `""` or `false` is a legal value is a live bug.

## Going further

- [ECMAScript Language Types](https://tc39.es/ecma262/#sec-ecmascript-language-types): the seven primitives, defined
- [IsLooselyEqual](https://tc39.es/ecma262/#sec-islooselyequal): the loose-equality algorithm, step by step
- [You Don't Know JS Yet: Types & Grammar, chapter 1](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/types-grammar/ch1.md): primitive values in depth
- [You Don't Know JS Yet: Types & Grammar, chapter 4](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/types-grammar/ch4.md): coercion, argued rather than listed
- [Coercion and equality](../reference/coercion-and-equality.md): the tables, for lookup
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
