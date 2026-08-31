---
title: 3. Prototypes and Classes
description: Property lookup walks a chain, and class syntax is one way to build that chain
type: lesson
---

# Lesson 3. Prototypes and Classes

**Mission link:** Class syntax hides a delegation mechanism that is still there, and it surfaces in three places a typed codebase cares about: what `instanceof` answers, where methods actually live, and why a class instance survives serialisation as a plain object.
**Primary source:** [You Don't Know JS Yet: Objects & Classes, chapter 5](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch5.md)
**Prerequisites:** [Lesson 2](0002-objects-are-references.md)

## Warm-up

1. ▢ `const copy = { ...original }` and then `copy.tags.push("b")`. Does `original` see it?

<details markdown="1"><summary>Check</summary>

Yes. Spread is one level deep, so both objects refer to the same `tags` array.

</details>

2. ▢ What does `const` prevent, and what does it not?

<details markdown="1"><summary>Check</summary>

It prevents rebinding the name. It does not prevent mutation of the object the name refers to.

</details>

## Know this

Every object has a hidden link to another object, its **prototype**. When you read a property the engine looks on the object, then on its prototype, then on that object's prototype, until the chain ends at `null`.

```ts
const base = { greet() { return "hi"; } };
const child = Object.create(base);
child.greet();                      // "hi", found on base
Object.getPrototypeOf(child) === base;   // true
```

Writing is not symmetrical with reading. An assignment creates an **own property** on the object itself and leaves the prototype untouched:

```ts
child.greet = () => "hello";        // own property, shadows the prototype's
delete child.greet;                 // the prototype's is visible again
```

That asymmetry, reads walking the chain and writes staying local, is the whole mechanism. Shared behaviour goes on the prototype; per-object state goes on the object.

### `class` builds that chain for you

```ts
class Service {
  name: string;                     // per-instance
  constructor(name: string) { this.name = name; }
  describe() { return this.name; }   // on Service.prototype, shared
}
```

`describe` lives on `Service.prototype`, so every instance shares one function object. `name` is an own property of each instance. `new Service("a")` creates an object whose prototype is `Service.prototype` and runs the constructor with `this` bound to it.

`extends` links prototypes, `super` calls up the chain, and `static` members live on the constructor function rather than on the prototype.

Two class features that look alike and are not:

```ts
class A {
  method() { return this; }         // on the prototype, shared
  field = () => this;               // an own property per instance
}
```

The arrow field is created once per instance and captures `this` at construction, which is lesson 4's material and the reason it exists. It costs one function object per instance, which is why it is a tool for a specific problem rather than a default style.

### What this means in practice

**`instanceof` walks the chain.** `x instanceof Service` asks whether `Service.prototype` appears in `x`'s prototype chain. It is therefore false across execution contexts, and false for an object that merely has the same shape.

**Serialisation loses the chain.** `JSON.parse(JSON.stringify(instance))` returns a plain object: same own properties, no prototype, so no methods. Anything arriving from a network or a file is a plain object however you typed it, which is exactly why stage 5 exists.

**TypeScript is structural, and the prototype chain is nominal.** The compiler will accept `{ name: "x", describe: () => "x" }` where a `Service` is expected, because the members match. `instanceof` will still say `false`. The two are answering different questions, and mixing them is a common source of confusion.

**Private fields are the one truly private mechanism.** `#field` is enforced at run time by the language. TypeScript's `private` is a compile-time claim that is erased, so it is visible to any untyped caller.

## Practice

1. ▢ Predict all four.

   ```ts
   const base = { kind: "base" };
   const child = Object.create(base);
   console.log(child.kind);
   child.kind = "child";
   console.log(child.kind, base.kind);
   console.log(Object.hasOwn(child, "kind"));
   delete child.kind;
   console.log(child.kind);
   ```

<details markdown="1"><summary>Check</summary>

`"base"`, then `"child" "base"`, then `true`, then `"base"`.

The read walked the chain. The write created an own property that shadows it, leaving `base` alone. Deleting the own property makes the inherited one visible again, which is why `delete` on an inherited property appears to do nothing.

</details>

2. ▢ Where does each of these live, and how many function objects exist for ten instances?

   ```ts
   class Counter {
     n = 0;
     inc() { this.n++; }
     dec = () => { this.n--; };
   }
   ```

<details markdown="1"><summary>Hint</summary>

One of the two is written by the constructor onto each new object. The other is written once, when the class is evaluated.

</details>

<details markdown="1"><summary>Check</summary>

`inc` lives on `Counter.prototype`: one function object, shared by all ten instances. `dec` is a class field, so each instance gets its own: ten function objects. `n` is an own property of each instance.

That is the cost of the arrow-field style, and lesson 4 is about what it buys.

</details>

3. ▢ An object arrives from `JSON.parse` and the code calls a method on it. Predict what happens and say why the compiler did not object.

   ```ts
   class User { constructor(public name: string) {} greet() { return "hi " + this.name; } }
   const raw = JSON.parse('{"name":"ada"}') as User;
   console.log(raw.greet());
   ```

<details markdown="1"><summary>Check</summary>

`TypeError: raw.greet is not a function` at run time.

`JSON.parse` produces a plain object with one own property. Its prototype is `Object.prototype`, so there is no `greet` anywhere in the chain.

The compiler did not object because `as User` is an assertion: it stops checking rather than converting. This is the single most common way a typed codebase acquires a run-time error, and it is what stage 5 replaces with validation.

</details>

4. ▢ Which is true of `x instanceof Service`?

   - a) It compares the shape of `x` against the class
   - b) It looks for `Service.prototype` in the chain
   - c) It calls the constructor to compare results
   - d) It checks the value of `x.constructor.name`

<details markdown="1"><summary>Check</summary>

**b)** It looks for `Service.prototype` in `x`'s prototype chain.

That is why a structurally identical plain object is not an instance, why an object from another execution context is not an instance, and why reassigning `Service.prototype` after construction breaks existing instances' answers.

</details>

5. ▢ You need a field that outside code genuinely cannot read, even from untyped JavaScript. Which do you use, and what is the trade-off?

<details markdown="1"><summary>Check</summary>

`#field`, the ECMAScript private field. It is enforced by the language: access from outside the class body is a syntax error, and there is no reflective way in.

TypeScript's `private` is erased at compile time, so the property is an ordinary own property at run time and any untyped caller can read it.

The trade-offs of `#field` are real: it is not visible in `JSON.stringify` output, it cannot be reached by test code that pokes at internals, and mixing it with structural typing is awkward, since two classes with the same shape are no longer interchangeable if either has one. Use `private` for ordinary encapsulation between colleagues, and `#` when the guarantee has to hold against code you do not control.

</details>

## Real-world reps

- [ ] Build the `Counter` class and check `Object.hasOwn(instance, "inc")` and `Object.hasOwn(instance, "dec")`. The pair of answers makes the prototype distinction concrete.
- [ ] Round-trip a class instance through `JSON.stringify` and `JSON.parse`, then call a method on the result and read the error.
- [ ] Tomorrow: find an `as SomeClass` in code you know where the value came from outside the program. Decide what would happen if a field were missing.

## Going further

- [You Don't Know JS Yet: Objects & Classes, chapter 5](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch5.md): delegation, and the case for using it directly
- [You Don't Know JS Yet: Objects & Classes, chapter 4](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch4.md): how `this` interacts with all of this, which is lesson 4
- [Ordinary object internal methods](https://tc39.es/ecma262/#sec-ordinary-object-internal-methods-and-internal-slots): the specified lookup algorithm
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
