---
title: 5. Scope and Closures
description: A closure captures the binding rather than the value, and let makes one per iteration
type: lesson
---

# Lesson 5. Scope and Closures

**Mission link:** Closures are how every callback, handler and async continuation keeps its context, and the loop-variable trap is the one place the mechanism is visible. Async code in lesson 6 is built entirely on this.
**Primary source:** [You Don't Know JS Yet: Scope & Closures, chapter 7](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/scope-closures/ch7.md)
**Prerequisites:** [Lesson 4](0004-this-and-the-call-site.md)

## Warm-up

1. ▢ Why does `setTimeout(svc.describe, 0)` fail while `setTimeout(() => svc.describe(), 0)` works?

<details markdown="1"><summary>Check</summary>

The first hands over a bare function, so there is no receiver at the call. The second calls it with the dot inside the callback, which supplies `this`.

</details>

2. ▢ Should a method be an ordinary function or an arrow, and should a callback inside it be?

<details markdown="1"><summary>Check</summary>

Method ordinary, callback arrow. The method needs `this` from its call site; the callback needs the enclosing one.

</details>

## Know this

A **closure** is a function together with the scope it was created in. The function keeps access to that scope after the enclosing function has returned, and the crucial detail is that it keeps the **binding**, not a copy of the value:

```ts
function counter() {
  let n = 0;
  return () => ++n;
}
const next = counter();
next();     // 1
next();     // 2
```

`n` outlives `counter` because the returned function still refers to it. Two calls to `counter()` produce two independent `n` bindings, which is what makes this a tool for encapsulation rather than a curiosity.

### `var`, `let` and the temporal dead zone

| Declaration | Scope | Before its line | Redeclarable |
|---|---|---|---|
| `var` | nearest function | `undefined` | yes |
| `let` | nearest block | `ReferenceError` | no |
| `const` | nearest block | `ReferenceError` | no |

`var` is hoisted to the top of the function and initialised to `undefined`, so reading it early is legal and useless. `let` and `const` are hoisted too, and reading one before its declaration throws: that gap is the **temporal dead zone**, and it turns a class of silent bug into an error.

Use `const` by default, `let` when a binding genuinely changes, and `var` never.

### The loop-variable trap

```ts
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// 3 3 3

for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// 0 1 2
```

With `var` there is one binding for the whole function, so all three closures share it and see its final value. With `let` the specification creates **a fresh binding per iteration**, and each closure captures its own.

This is worth stating precisely because it is the thing people half-remember: the closure did not capture a value in either case. It captured a binding. `let` changed how many bindings there were.

The same trap appears without a loop wherever one binding is shared by several closures, and it explains a whole family of "why is it always the last one" bugs in handler registration.

### What closures are actually for

Three uses that carry real weight:

```ts
// 1. private state, with no class and no `this`
function makeLimiter(max: number) {
  let used = 0;
  return { take: () => (used < max ? (used++, true) : false) };
}

// 2. partial application: fixing an argument now, calling later
const prefix = (p: string) => (s: string) => p + s;

// 3. keeping context across an asynchronous gap
async function retry<T>(fn: () => Promise<T>, times: number) {
  for (let attempt = 1; attempt <= times; attempt++) {
    try { return await fn(); } catch (e) { if (attempt === times) throw e; }
  }
}
```

The third is why lesson 6 depends on this one: every `await` resumes a function whose local bindings are still there, and that is a closure doing its job.

One cost worth knowing: a closure keeps its whole enclosing scope reachable, so a small callback can hold a large object alive. That is a real memory-leak shape in long-lived programs, and the fix is to close over the field you need rather than the object that contains it.

## Practice

1. ▢ Predict both loops.

   ```ts
   for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 0);
   for (let j = 0; j < 3; j++) setTimeout(() => console.log(j), 0);
   ```

<details markdown="1"><summary>Check</summary>

The first prints `3 3 3`. The second prints `0 1 2`.

`var i` is one function-scoped binding, and by the time any callback runs the loop has finished with `i` at `3`. `let j` gets a fresh binding per iteration, so each callback closed over a different one.

</details>

2. ▢ Predict the output.

   ```ts
   function make() {
     let n = 0;
     return { inc: () => ++n, get: () => n };
   }
   const a = make();
   const b = make();
   a.inc(); a.inc(); b.inc();
   console.log(a.get(), b.get());
   ```

<details markdown="1"><summary>Check</summary>

`2 1`.

Each call to `make` created its own `n`. Within one object, `inc` and `get` close over the same binding, which is what makes the pair coherent.

</details>

3. ▢ What does this print, and what is the name of the rule?

   ```ts
   console.log(a);
   console.log(b);
   var a = 1;
   let b = 2;
   ```

<details markdown="1"><summary>Hint</summary>

Both declarations are hoisted. Only one of them is initialised before its line is reached.

</details>

<details markdown="1"><summary>Check</summary>

`undefined`, then `ReferenceError: Cannot access 'b' before initialization`.

`var a` is hoisted and initialised to `undefined`. `let b` is hoisted and left uninitialised, and the region between the top of the block and the declaration is the temporal dead zone.

</details>

4. ▢ Fix this so each button logs its own index, using two different approaches.

   ```ts
   var handlers = [];
   for (var i = 0; i < 3; i++) {
     handlers.push(() => console.log(i));
   }
   ```

<details markdown="1"><summary>Check</summary>

Change the declaration, which is the answer in modern code:

```ts
const handlers: Array<() => void> = [];
for (let i = 0; i < 3; i++) handlers.push(() => console.log(i));
```

Or create a scope explicitly, which is what people did before `let` and is still what you write when the value is derived rather than the loop variable:

```ts
for (var i = 0; i < 3; i++) {
  ((captured: number) => handlers.push(() => console.log(captured)))(i);
}
```

The second version makes the mechanism visible: passing `i` as an argument copies the value into a new binding, which is exactly what `let` does for you per iteration.

</details>

5. ▢ This handler keeps a large object alive for the life of the program. Explain how, and fix it.

   ```ts
   function register(response: HugeResponse) {
     const id = response.user.id;
     onEvent(() => track(response.user.id));
   }
   ```

<details markdown="1"><summary>Check</summary>

The callback closes over `response`, so the whole response stays reachable as long as the handler is registered, even though only one number is needed.

```ts
function register(response: HugeResponse) {
  const id = response.user.id;
  onEvent(() => track(id));
}
```

Now the closure holds a number. The original code already had `id` in scope and used the long path anyway, which is what makes this shape easy to miss in review: the fix is invisible unless you ask what the closure retains rather than what it computes.

</details>

## Real-world reps

- [ ] Run both loops from practice 1. Then change the second to `var` and watch the output change, so the difference is attributed to the declaration rather than to the timer.
- [ ] Write the `makeLimiter` closure and confirm from the outside that there is no way to read or reset `used`. That is encapsulation with no class involved.
- [ ] Tomorrow: find a `var` in code you know. Decide whether replacing it with `let` or `const` would change behaviour, and whether that change would be a fix.

## Going further

- [You Don't Know JS Yet: Scope & Closures, chapter 7](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/scope-closures/ch7.md): closures, defined carefully and then tested against cases
- [You Don't Know JS Yet: Scope & Closures, chapter 1](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/scope-closures/ch1.md): how scopes are determined before any code runs
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
