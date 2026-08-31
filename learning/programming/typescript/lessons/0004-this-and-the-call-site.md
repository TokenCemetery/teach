---
title: 4. this Is Decided by the Call
description: this comes from how a function is called, so extracting a method throws it away
type: lesson
---

# Lesson 4. this Is Decided by the Call

**Mission link:** Passing a method as a callback is the most ordinary thing in a codebase, and it is the exact operation that loses `this`. The type system does catch some of it, and only if you know what it is checking.
**Primary source:** [You Don't Know JS Yet: Objects & Classes, chapter 4](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch4.md)
**Prerequisites:** [Lesson 3](0003-prototypes-and-classes.md)

## Warm-up

1. ▢ Where does a class method live, and where does a class field live?

<details markdown="1"><summary>Check</summary>

The method is on the prototype and shared by all instances. The field is an own property, created per instance by the constructor.

</details>

2. ▢ What does `instanceof` actually check?

<details markdown="1"><summary>Check</summary>

Whether the constructor's `prototype` object appears in the value's prototype chain.

</details>

## Know this

`this` is not a variable and it is not lexically scoped. For an ordinary function it is an implicit parameter, and **the call site decides its value.** The same function called four ways gets four different `this`.

The four rules, in precedence order:

1. **`new`**: `new F()` sets `this` to the newly created object.
2. **Explicit**: `f.call(obj)`, `f.apply(obj)`, `f.bind(obj)` set it to `obj`.
3. **Method call**: `obj.f()` sets it to `obj`, because of the dot, not because of where `f` was defined.
4. **Default**: anything else gets `undefined` in strict mode, which includes every module and every class body. In sloppy mode it gets the global object instead, which is how these bugs used to be silent.

Arrow functions are outside this system entirely: they have no `this` of their own and close over the one in scope where they were written.

### The bug this produces

```ts
class Service {
  constructor(private name: string) {}
  describe() { return this.name; }
}

const svc = new Service("api");
svc.describe();                     // "api"

const fn = svc.describe;
fn();                               // TypeError: cannot read 'name' of undefined

[1].map(svc.describe);              // same failure
setTimeout(svc.describe, 0);        // same failure
```

Nothing was mutated and no reference was lost. `svc.describe` evaluates to the function, and the function has no attachment to `svc`. The dot is what supplied `this`, and once you extract the function there is no dot.

TypeScript catches part of this, and only part. With `strictBindCallApply` and `noImplicitThis` on, a function that uses `this` and is called without a receiver can be reported, but a method passed as a callback usually type-checks fine, because its signature says nothing about needing a receiver.

### Three fixes, and when each is right

```ts
setTimeout(() => svc.describe(), 0);            // 1: call it at the call site
setTimeout(svc.describe.bind(svc), 0);          // 2: bind explicitly
class Service { describe = () => this.name; }   // 3: an arrow class field
```

- **Wrapping in an arrow** is the default. It is local, obvious, costs nothing structurally, and keeps the method on the prototype.
- **`bind`** is right when you need the bound function as a value, for example to store it and remove a listener later. Note that `bind` returns a *new* function, so `removeEventListener(el, this.handler.bind(this))` removes nothing.
- **The arrow field** is right when a class exists to be used as a bag of callbacks. It costs one function object per instance and it is not on the prototype, so it cannot be overridden by a subclass in the usual way.

### `this` in an arrow function

```ts
const obj = {
  name: "x",
  ordinary() { return this.name; },       // "x"
  arrow: () => this.name,                 // NOT obj: `this` is the enclosing scope's
};
```

An arrow in an object literal captures whatever `this` was outside the literal, which at module top level is `undefined`. So arrows are correct for callbacks inside a method and wrong for methods themselves. That is the one rule worth memorising: **methods should be ordinary functions, callbacks should be arrows.**

## Practice

1. ▢ Predict each of the four.

   ```ts
   class Counter {
     n = 0;
     inc() { this.n++; return this.n; }
   }
   const c = new Counter();
   console.log(c.inc());
   const f = c.inc;
   console.log(f());
   console.log(f.call(c));
   console.log([0].map(c.inc));
   ```

<details markdown="1"><summary>Hint</summary>

For each call, find what is immediately to the left of the parentheses.

</details>

<details markdown="1"><summary>Check</summary>

`1`, then a `TypeError` from `f()`.

`c.inc()` had the dot, so `this` was `c`. `f()` is a plain call in strict mode, so `this` is `undefined` and reading `this.n` throws. The remaining two lines never run; `f.call(c)` would have returned `2`, and the `map` call would have thrown for the same reason as `f()`.

</details>

2. ▢ Which of these logs `"api"`?

   ```ts
   const svc = new Service("api");
   ```

   - a) `setTimeout(svc.describe, 0)`
   - b) `setTimeout(() => svc.describe(), 0)`
   - c) `setTimeout(svc.describe.bind(svc), 0)`
   - d) `setTimeout(function () { svc.describe(); }, 0)`

<details markdown="1"><summary>Check</summary>

**b)**, **c)** and **d)** all work. Only **a)** fails.

In b and d the call happens with `svc` to the left of the dot, inside the callback. In c, `bind` attached the receiver permanently. In a, the function is handed over with nothing attached, and the timer calls it with no receiver.

Note that d works despite being an ordinary function: what matters is not how the callback was written but how `describe` is called inside it.

</details>

3. ▢ Why does this listener never get removed?

   ```ts
   class Widget {
     handle() { }
     attach(el: HTMLElement) { el.addEventListener("click", this.handle.bind(this)); }
     detach(el: HTMLElement) { el.removeEventListener("click", this.handle.bind(this)); }
   }
   ```

<details markdown="1"><summary>Check</summary>

`bind` returns a new function object every time it is called, so the function passed to `removeEventListener` is not the one that was added, and removal is by identity.

The fix is to bind once and keep the result:

```ts
class Widget {
  private readonly bound = this.handle.bind(this);
  attach(el: HTMLElement) { el.addEventListener("click", this.bound); }
  detach(el: HTMLElement) { el.removeEventListener("click", this.bound); }
  handle() { }
}
```

An arrow class field, `handle = () => {}`, has the same effect: one stable function per instance.

</details>

4. ▢ One of these two is wrong. Which, and why?

   ```ts
   const timer = {
     seconds: 0,
     startA() { setInterval(() => this.seconds++, 1000); },
     startB() { setInterval(function () { this.seconds++; }, 1000); },
   };
   ```

<details markdown="1"><summary>Check</summary>

`startB` is wrong. The ordinary function passed to `setInterval` is called with no receiver, so `this` is not `timer`, and `this.seconds++` either throws or silently writes to something else depending on the environment and mode.

`startA` is correct: the arrow has no `this` of its own, so it uses the one from `startA`, which is `timer` because `startA` was called with the dot.

This is the memorable version of the rule: the method is an ordinary function, and the callback inside it is an arrow.

</details>

5. ▢ A colleague proposes making every class method an arrow field, so `this` can never be lost. Give the strongest argument for and against.

<details markdown="1"><summary>Check</summary>

For: the failure mode disappears completely. Methods survive being passed as callbacks, destructured, or handed to a framework, and nobody has to think about the call site again. In a codebase that mostly wires callbacks, that is a real reduction in a whole class of bug.

Against: it moves every method off the prototype, so each instance carries its own copy of every function, which matters when instances are numerous. Subclass overriding stops working the usual way, since a field on the child shadows rather than overrides and the ordering of field initialisation starts to matter. `super.method()` is no longer available. And the methods vanish from the prototype, so anything reflecting over the class, including some test and serialisation tooling, no longer sees them.

The defensible middle: ordinary methods by default, arrow fields for the specific handful that are genuinely passed as callbacks, and a comment saying which.

</details>

## Real-world reps

- [ ] Run practice 1 line by line and watch exactly which call throws. Then add `"use strict"` reasoning to it: in a module you are already in strict mode, so `this` is `undefined` rather than the global object.
- [ ] Reproduce the `bind` listener bug: attach, detach, then click and see the handler still fire.
- [ ] Tomorrow: search code you know for a method passed directly as a callback, meaning `something(this.method)` or `something(obj.method)` with no wrapper. Each one either already has an arrow field or is a latent bug.

## Going further

- [You Don't Know JS Yet: Objects & Classes, chapter 4](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/objects-classes/ch4.md): the four rules, argued in full
- [TSConfig: `noImplicitThis` and `strictBindCallApply`](https://www.typescriptlang.org/tsconfig/): what the compiler can and cannot catch here
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
