---
title: 6. The Event Loop, Promises and await
description: Microtasks drain before the next timer, and two awaits in a row are sequential
type: lesson
---

# Lesson 6. The Event Loop, Promises and await

**Mission link:** Almost all real TypeScript is asynchronous, and two of its costs are invisible in the source: the ordering of callbacks, and the difference between awaiting two things in sequence and awaiting them together.
**Primary source:** [The Node.js Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
**Prerequisites:** [Lesson 5](0005-scope-and-closures.md)

## Warm-up

1. ▢ Why does a `let` loop variable make each closure see its own value?

<details markdown="1"><summary>Check</summary>

Because the specification creates a fresh binding per iteration, and a closure captures the binding rather than a value.

</details>

2. ▢ What keeps a callback's local variables alive after the enclosing function returned?

<details markdown="1"><summary>Check</summary>

The closure. The function still refers to that scope, so the scope stays reachable.

</details>

## Know this

JavaScript runs your code on one thread. Anything that waits, a timer, a request, a file read, is handed to the runtime, and your function returns. When the work finishes, a callback is queued, and the **event loop** runs it when the current code has finished.

The consequence to internalise: **no callback ever interrupts running code.** There is no pre-emption, so there are no data races on ordinary variables, and a synchronous loop that takes a second blocks every timer and every response for that second.

### Two queues, and one of them has priority

Queued work is either a **task** (a timer, an I/O callback) or a **microtask** (a promise reaction, `queueMicrotask`). After the current script or task finishes, the loop **drains the entire microtask queue** before taking the next task.

```ts
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
console.log("4");
// 1 4 3 2
```

Synchronous code first, then all microtasks, then the timer. A microtask that queues another microtask is still processed in the same drain, which is why an endless chain of promises can starve timers completely.

In Node, `process.nextTick` runs before promise microtasks, which is a Node-specific extra queue rather than part of the language.

### `await` is a microtask boundary

```ts
async function f() {
  console.log("a");
  await null;              // suspends here, even though nothing is pending
  console.log("b");
}
f();
console.log("c");
// a c b
```

An `async` function runs synchronously until its first `await`, then returns a promise. Everything after the `await` is a continuation queued as a microtask. So `await` on an already-resolved value still yields, which is exactly why the ordering above surprises people.

### Sequential against concurrent

```ts
// two round trips, one after the other
const user = await getUser();
const orders = await getOrders();

// both started immediately, both awaited together
const [user2, orders2] = await Promise.all([getUser(), getOrders()]);
```

Both versions are correct. The first takes the sum of the two latencies and the second takes the maximum, and nothing in the syntax marks the difference. Use sequential `await` when the second call needs the first result, and `Promise.all` when it does not.

Three neighbours worth knowing:

| Combinator | Settles when | On failure |
|---|---|---|
| `Promise.all` | all fulfil | rejects on the first rejection |
| `Promise.allSettled` | all settle | never rejects; each result reports status |
| `Promise.race` | the first settles | adopts that outcome, fulfil or reject |

`Promise.all` rejecting early does **not** cancel the others. They keep running, and if a second one rejects with nobody listening you get an unhandled rejection. `allSettled` is the honest choice when you need every outcome.

### Floating promises

```ts
saveUser(user);              // not awaited: errors vanish, order is unknown
await saveUser(user);        // errors propagate, order is guaranteed
```

An un-awaited promise is a fire-and-forget operation whose rejection becomes an unhandled rejection, which in Node terminates the process by default. TypeScript does not flag this by itself; the lint rule `no-floating-promises` exists precisely because the compiler will not.

For error handling, `try`/`catch` around `await` behaves as you would expect, with one caveat: a rejection inside a callback passed to a synchronous function, such as `forEach`, escapes the surrounding `try` entirely. `for...of` with `await` inside works; `array.forEach(async ...)` does not.

## Practice

1. ▢ Predict the exact output order.

   ```ts
   console.log("1");
   setTimeout(() => console.log("2"), 0);
   Promise.resolve().then(() => console.log("3"));
   queueMicrotask(() => console.log("4"));
   console.log("5");
   ```

<details markdown="1"><summary>Hint</summary>

Sort the five into three groups first: synchronous, microtask, task.

</details>

<details markdown="1"><summary>Check</summary>

`1 5 3 4 2`.

`1` and `5` are synchronous. `3` and `4` are microtasks, drained in the order they were queued once the script finishes. `2` is a task, and tasks wait until the microtask queue is empty.

</details>

2. ▢ Predict the output.

   ```ts
   async function f() {
     console.log("a");
     await null;
     console.log("b");
   }
   console.log("start");
   f();
   console.log("end");
   ```

<details markdown="1"><summary>Check</summary>

`start a end b`.

The call runs synchronously to the `await`, so `a` prints before `end`. `await null` still suspends and queues the continuation as a microtask, so `b` runs after the synchronous code finishes.

</details>

3. ▢ Each request takes 100 milliseconds. How long does each version take?

   ```ts
   // A
   const x = await getA();
   const y = await getB();

   // B
   const [x2, y2] = await Promise.all([getA(), getB()]);
   ```

<details markdown="1"><summary>Check</summary>

A takes about 200 milliseconds, B about 100.

In A the second call is not made until the first has resolved. In B both are started before either is awaited. Nothing in the shape of the code signals this, which is why it is worth checking every pair of consecutive `await`s for a dependency that may not exist.

</details>

4. ▢ Which one reports every failure without letting an unhandled rejection escape?

   - a) `await Promise.all(tasks)`
   - b) `await Promise.allSettled(tasks)`
   - c) `await Promise.race(tasks)`
   - d) `tasks.forEach(async (t) => await t)`

<details markdown="1"><summary>Check</summary>

**b)** `Promise.allSettled(tasks)`.

Option a rejects on the first failure and leaves the rest running, so a later rejection has no handler. Option c reports one outcome and ignores the rest. Option d is the trap: `forEach` ignores the returned promises entirely, so the surrounding function does not wait and every rejection floats.

</details>

5. ▢ This loop is meant to process items one at a time and stop on the first error. It does neither. Explain and fix it.

   ```ts
   items.forEach(async (item) => {
     await process(item);
   });
   console.log("done");
   ```

<details markdown="1"><summary>Check</summary>

`forEach` calls the callback and discards its return value, so all the async callbacks start immediately and nothing waits for them. `done` prints before any item finishes, and a rejection in `process` becomes an unhandled rejection rather than something the caller can catch.

```ts
for (const item of items) {
  await process(item);
}
console.log("done");
```

If concurrency was actually wanted, be explicit and keep the errors:

```ts
await Promise.all(items.map((item) => process(item)));
```

The general rule: `await` inside a callback only helps if something is awaiting the callback's promise, and the array methods do not.

</details>

## Real-world reps

- [ ] Run practice 1 and get the order right from prediction, not from the output. Then add a `process.nextTick` if you are on Node and see where it lands.
- [ ] Write two versions of a function that fetches two independent things, one sequential and one with `Promise.all`, and time both.
- [ ] Tomorrow: search code you know for `forEach(async` and for calls to async functions with no `await` and no `.catch`. Both are usually bugs, and neither is a compile error.

## Going further

- [The Node.js Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick): the phases, and where `nextTick` and promises sit
- [Jobs and Host Operations to Enqueue Jobs](https://tc39.es/ecma262/#sec-jobs): the specification's model of the microtask queue
- [You Don't Know JS Yet: Sync & Async, chapter 1](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/sync-async/ch1.md): the single-threaded model argued from first principles
- [Event loop and promises](../reference/event-loop-and-promises.md): the ordering rules and the combinator table, for lookup
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
