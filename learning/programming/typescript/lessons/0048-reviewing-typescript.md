---
title: 48. Reviewing TypeScript
description: Naming what a type costs, instead of saying it looks complicated
type: lesson
---

# Lesson 48. Reviewing TypeScript

**Mission link:** This lesson carries the mission's review clause directly: say precisely why a conditional type, an assertion, or an `enum` is the wrong tool in a pull request, rather than asking for a rewrite on taste.
**Primary source:** [Effective TypeScript, Dan Vanderkam](https://effectivetypescript.com/)
**Prerequisites:** [Lesson 41](0041-inference-for-library-apis.md), [Lesson 18](0018-an-assertion-is-not-a-check.md)

## Warm-up

1. ▢ Lesson 41 gave a two-part standard for judging a signature: what the caller has to write, and what they see when they get it wrong. A reviewer writes only "this looks complicated, please simplify" on a pull request. Say what that comment is missing that the two-part standard would have supplied.

<details markdown="1"><summary>Check</summary>

It names no cost and no payer. Lesson 41's standard forces a look at what the caller writes and what a wrong call shows them, both facts about the code, not feelings about reading it. "Looks complicated" reports the reviewer's own reading speed and gives the author nothing to fix or argue with, since there is no claim in it. This lesson turns that missing half into a method you can apply on purpose.

</details>

## Know this

### The method: cost, payer, alternative

"This looks complicated" fails as a review comment because it cannot be checked and cannot be argued with. It names a reaction, not a fact, so the author's only honest response is to guess what would make the reviewer comfortable. A usable comment names three things instead: what the construct costs, stated as a fact about the code rather than a feeling about reading it; who pays that cost, since some land on every caller and some land only on whoever edits the file next; and what the alternative looks like, concretely, so "wrong tool" arrives with "right tool" attached rather than left as a demand. A reviewer who cannot fill in those three blanks has not earned the right to ask for a rewrite, since the request then asks someone to rewrite working code to satisfy a preference nobody can name. What follows applies that method to the three constructs stage 6 armed you to judge, then more briefly to the review's other usual suspects.

### Case one, the conditional type

Lesson 37 admitted plainly that a conditional type's honest case is narrow: a caller gets back a precise type with nothing to assert and nothing to narrow. Lesson 41 gave the test that decides it, in two halves: what the caller has to write, and what they see when they get it wrong. Lesson 42 supplied the missing half of the price tag: the real cost is not build time, it is the error message the day someone gets it wrong. Put the three together on a signature that keeps only a `T`'s number-valued keys.

```ts
type KeysMatching<T, V> = { [K in keyof T]: T[K] extends V ? K : never }[keyof T];

function pickNumberKeys<T>(obj: T, keys: KeysMatching<T, number>[]): Pick<T, KeysMatching<T, number>> {
  const result = {} as Pick<T, KeysMatching<T, number>>;
  for (const k of keys) result[k] = obj[k];
  return result;
}

const order = { id: "o1", quantity: 4, price: 19.99 };
pickNumberKeys(order, ["total"]);
```

```text
error TS2322: Type '"total"' is not assignable to type 'KeysMatching<{ id: string; quantity: number; price: number; }, number>'.
```

`order` has two number-valued keys, `quantity` and `price`, and the diagnostic names neither: it names the alias itself, unresolved, which tells a caller nothing they did not already know from reading the parameter's declared type. Here is the plain generic doing the smaller, honest job, on the same object and the same typo.

```ts
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const k of keys) result[k] = obj[k];
  return result;
}
pick(order, ["total"]);
```

```text
error TS2322: Type '"total"' is not assignable to type '"id" | "price" | "quantity"'.
```

Same mistake, same caller, and this diagnostic names all three real properties, exactly what someone fixing a typo needs. The review comment writes itself: "`KeysMatching` reports its own name back instead of the properties it is choosing between; the plain generic gives the same guarantee and names every real key. Replace it unless a caller specifically benefits from the number-only constraint being enforced at the call site rather than at first use." That clause matters: lesson 37's own honest case, a `parse` function returning `number` or `string` from a boolean flag, is exactly the shape where the caller writes no assertion and gets a type the plain alternative could not give. A conditional type is the wrong tool when a plainer generic buys the same guarantee with a legible error; it is right when a caller is measurably better off for having written nothing and having nothing left to narrow.

### Case two, the assertion

Lesson 18 named an assertion for what it is: a claim nothing checks, most often used to silence a check that was right, the null check `strictNullChecks` runs or the excess-property check lesson 11 taught. In review terms that becomes three questions: what is the assertion claiming, what establishes that claim, and if nothing does, what would. Here is the shape that shows up in almost every codebase.

```ts
interface Config {
  host: string;
  port: number;
}
const raw = JSON.parse("{}");
const config = raw as Config;
console.log(config.host.toUpperCase());
```

This compiles clean, no diagnostic, because `raw` is `any` straight out of `JSON.parse` and `as Config` only asks the compiler to believe the shape rather than check it. Run it and the claim comes due: `TypeError: Cannot read properties of undefined (reading 'toUpperCase')`, since `JSON.parse("{}")` has no `host`. The review sentence: "This line claims `raw` has the shape `Config`; nothing between the parse and this line establishes that, so the assertion stands in for a check that never ran. Either parse `raw` against `Config`'s shape, lesson 31's way, or say what upstream guarantees the shape and why the compiler cannot see it." That second branch is not a formality: the standard held since lesson 18 is that a defensible assertion carries a comment stating what the author knows and the compiler cannot, the kind lesson 18 modelled: `` `arr[0]!  // arr is populated by the loop above and never empty here` ``. Here is the same shape without one.

The rule that generalises from it: an assertion earns a pass when its comment states a fact a reader can check against the surrounding lines. One with no comment, or a comment that only restates the assertion, is one of lesson 18's two failures wearing new clothes, and the review should say which.

### Case three, the `enum`

Lesson 46 supplied the evidence, and review terms borrow it rather than re-deriving it: an `enum` emits a mutable object with a reverse mapping nobody asked for, and `erasableSyntaxOnly` states the compiler's own reason to refuse it, that this is a runtime construct which is not part of ECMAScript. That makes the review comment citable rather than felt: "`enum Status { Pending, Done }` compiles to an object carrying both `Status.Pending` and the reverse lookup `Status[0]`, and nothing in this diff reads either direction. Replace it with the union of literals lesson 10 gave you, `type Status = "Pending" | "Done";`, which erases completely and checks the same two values." That names a real cost, an object nobody uses, rather than a preference about how the declaration reads.

Fairness matters here as much as for the conditional type. A union gives up two things an `enum` provides free: iterating the members, since there is no `Object.values` for a type, and the reverse lookup from value to name. If a caller genuinely needs either, do not just repeat "avoid `enum`"; lesson 46 already gave the fallback, an object marked `as const` with a derived type, which keeps `Object.keys` working without a reverse mapping nobody asked for. The reviewable line is never "`enum` is banned"; it is what object this line built and what the code does with it.

### What else a review should catch, and how to receive one

The three cases above are the mission's material; the same cost, payer, alternative questions reach a short list of other usual suspects. An `any` with no comment removes checking from every expression built on it, silently, so ask which of lesson 17's two defensible reasons applies. A predicate whose body does not test what its `is` clause claims is trusted at every call site, lesson 32's finding. A value crossing a boundary unparsed needs the schema check lessons 30 and 31 gave `unknown`, not an assertion standing in for one. A published signature that is hard to change is lesson 43's: tightening a loose return type or renaming an exported alias breaks builds you will never see.

Receiving a review well is the other half. The author's job is to make the cost visible, by comment or by taking the simpler alternative, and "it compiles" is never a response to a cost, since every construct above compiles cleanly while doing exactly the damage described.

## Practice

1. ▢ `pickNumberKeys` from Know this is called on `{ id: "o1", quantity: 4, price: 19.99 }` with `["total"]`, and separately the plain `pick` is called on the same object with the same argument. Predict both diagnostics, and say which one a reviewer would cite as the sharper cost.

<details markdown="1"><summary>Check</summary>

`pickNumberKeys` gives `error TS2322: Type '"total"' is not assignable to type 'KeysMatching<{ id: string; quantity: number; price: number; }, number>'.`, naming the alias itself, both real number keys unmentioned. `pick` gives `error TS2322: Type '"total"' is not assignable to type '"id" | "price" | "quantity"'.`, naming all three. The first is the sharper cost: a type name to go and read, not the answer already sitting in the plain version.

</details>

2. ▢ A pull request adds this, with no comment on the `!`. Predict whether it compiles, what happens when it runs, and write the one-sentence review comment this earns.

   ```ts
   function lastPrice(prices: number[]): number {
     return prices[prices.length - 1]!;
   }
   console.log(lastPrice([]).toFixed(2));
   ```

<details markdown="1"><summary>Check</summary>

Compiles clean, no diagnostic. At run time: `TypeError: Cannot read properties of undefined (reading 'toFixed')`, since an empty array's last index is `undefined` and `!` told the compiler otherwise. The review comment: this `!` claims the array is never empty here, nothing establishes that, so either handle the empty case or add a comment saying why the caller can never pass one.

</details>

3. ▢ A pull request uses `enum Weekday { Mon, Tue, Wed, Thu, Fri, Sat, Sun }` and, elsewhere in the same file, calls `Object.values(Weekday).filter(v => typeof v === "number")` to iterate every day. Say whether the review comment from Know this applies unchanged, and why or why not.

<details markdown="1"><summary>Check</summary>

It does not apply unchanged. The Know this comment argued for a union because nothing there read either direction of the mapping; here the code iterates the members, which a union cannot do without a second, hand-written list. Name the trade instead: this caller genuinely needs the runtime object, so ask whether lesson 46's `as const` object would serve the same iteration more predictably, not whether the `enum` should simply go.

</details>

4. ▢ `function isTicket(x: unknown): x is Ticket { return typeof x === "object" && x !== null; }`, where `Ticket` has a required `priority: number`, is called as `if (isTicket(x)) { console.log(x.priority.toFixed(0)); }` with `x` equal to `{ id: "t1" }`. Predict whether it compiles, what happens when it runs, and which teaching point in this lesson it belongs to.

<details markdown="1"><summary>Hint</summary>

Compare what the body actually tests against what the `is` clause promises.

</details>

<details markdown="1"><summary>Check</summary>

Compiles clean, no diagnostic. At run time: `TypeError: Cannot read properties of undefined (reading 'toFixed')`, since `{ id: "t1" }` passes the body's bare non-null-object test while `priority` is missing. Lesson 32's material from the "what else" list: a predicate whose body does not establish its claim, trusted at every call site the way an assertion is trusted at one.

</details>

5. ▢ A review comment reads: "This `as Config` needs either a parse or a comment saying what guarantees the shape." The author replies: "It compiles, so it's fine." Say precisely what is wrong with that reply.

<details markdown="1"><summary>Check</summary>

"It compiles" answers a question nobody asked. An assertion compiles clean whether its claim is true or false, so compiling says nothing about whether `raw` actually has the shape `Config` requires. The reply needed to name what establishes the claim, either an existing check or the parse the comment asked for; restating that the code compiles concedes the reviewer's point rather than answering it.

</details>

## Real-world reps

- [ ] Find one review comment you have written or received that says a type "looks complicated" or "seems overkill", and rewrite it using the three-part method: what it costs, who pays, and what the alternative would be.
- [ ] Pick one assertion in a codebase you can see and ask, in writing, what establishes the claim it makes; if nothing does and no comment says why, flag it the way this lesson's case two did.
- [ ] Tomorrow: the next time you review a pull request containing a conditional type, an assertion, or an `enum`, write the review comment before you approve or reject, and check that it names a cost rather than a preference.

## Going further

- [TypeScript Handbook, Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html): the mechanics case one's review comment is built on
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): the non-goals that explain why the language leaves an escape hatch like `as` in place at all
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
