---
title: 48. Reviewing Java
description: Naming what an abstraction costs, instead of saying it feels wrong
type: lesson
---

# Lesson 48. Reviewing Java

**Mission link:** This workspace's stated goal for this stage is to review a pull request and say precisely why a class hierarchy, a checked exception, or a stream chain is the wrong tool there, and precisely is the difficulty: you already have the opinion, from six stages of building these things, and this lesson turns it into a sentence the author can act on.
**Primary source:** [Effective Java, Addison-Wesley](https://openlibrary.org/isbn/9780134685991)
**Prerequisites:** [Lesson 44](0044-designing-a-signature.md), [Lesson 10](0010-inheritance-and-composition.md)

## Warm-up

1. ▢ Lesson 10 gave `extends` exactly two things. Name them, and name the cost bundled with the second one, whether the reviewer asks for it or not.

<details markdown="1"><summary>Check</summary>

Inheriting the superclass's non-private members, and being usable anywhere the superclass type is expected. The second one, the "is-a" relationship, is what a caller relies on, but getting it also couples the subclass to the superclass's actual implementation, not just its documented contract, which is why a superclass change that looks internal can break a subclass that never touched the changed line.

</details>

## Know this

### Why "it feels wrong" loses the argument

"This feels wrong" is not a review comment, it is a mood, and moods are not falsifiable. The author cannot investigate a feeling or measure it, so the honest options left are to comply out of politeness or to turn the review into a standoff about whose taste wins. Either way the review produced no information.

A comment that works has three parts, in order: what the construct costs, who pays that cost, and what the alternative is. "This subclass is coupled to `HashSet`'s undocumented `addAll` implementation, which double-counts through this override; a held field with the two methods forwarded avoids it" names a cost, a payer, and a fix, checkable clause by clause. A reviewer who cannot fill in all three has not located a defect yet, only a discomfort, and asking for a rewrite on discomfort is a fight the reviewer either loses on the merits or wins by seniority, which teaches the team that reviews are about rank rather than evidence.

The rest of this lesson applies that shape to `extends`, a checked exception, and a stream chain, three tools that are all correct somewhere in this curriculum but wrong in a specific diff, for a reason specific to that diff.

### Case one: the class hierarchy

Lesson 10 priced `extends` once already; a review comment just spends that price back at the author, in terms specific to the change in front of you.

**The costs, in review terms.**

- **Implementation coupling.** The subclass depends on how the superclass is written, not only on what it promises. `HashSet.addAll` happens to be implemented by calling `add` once per element, which is undocumented, so a subclass that counts in both methods double-counts every bulk insert:

  ```java
  class AuditedTagSet extends HashSet<String> {
      private int added = 0;

      @Override
      public boolean add(String s) {
          added++;
          return super.add(s);
      }

      @Override
      public boolean addAll(Collection<? extends String> c) {
          added += c.size();
          return super.addAll(c);
      }

      int added() { return added; }
  }

  AuditedTagSet tags = new AuditedTagSet();
  tags.addAll(List.of("urgent", "billing", "eu"));
  ```

  Running this prints `size=3 added=6`: `addAll` counts 3 up front, then calls `super.addAll`, `AbstractCollection`'s implementation, which calls the overridden `add` once per element, adding 3 more. Nothing about `HashSet`'s contract changed; the bug is entirely a consequence of extending a class whose internals were never part of the deal.

- **The fragile base class problem.** A `protected` member, and every overridable method a subclass calls into, is a contract with subclasses the superclass author cannot see, so a change that looks purely internal can break every subclass silently, with no compiler error anywhere. This runs both directions: the superclass author breaks subclasses by refactoring, and a subclass author breaks by depending on more of the superclass's behaviour than its documentation promised.

- **A hierarchy commits every future subclass to the same shape.** Once `Sub1` and `Sub2` extend `Base`, a third subclass either fits the shape `Base` already assumes, or the hierarchy gets reshaped under two existing users. Composition never demands this: a class holding a field can be handed a different implementation of that field's type at any time, and nothing about existing holders changes.

**The review sentence.** Name the concrete coupling, not the abstract worry: "This subclass double-counts through `addAll` because `HashSet` implements it by calling the overridden `add`, an implementation detail the `Set` contract never promised; a held `Set` field with `add` and `addAll` forwarded explicitly avoids this, because the delegate's internal calls stay internal." Every clause is a fact about the code, not a preference, which is why the sentence survives an argument.

**Where a hierarchy is right.** This is not a blanket prohibition, and a reviewer who treats every `extends` as a defect is as unhelpful as one who never questions any of them. A hierarchy earns its place when the "is-a" relationship is real in the domain's own terms, when the author controls every subclass that will ever exist, and when the state being shared is worth sharing. Bloch's own skeletal implementation pattern, an `AbstractX` class supplying the boilerplate behind an interface so each concrete subclass fills in a handful of primitive operations, is exactly this case: the interface's author also writes the abstract class, so the coupling a reviewer would otherwise flag is coupling to code the same team already owns. A sealed hierarchy from lesson 11 is the other clean case, because closing off which types may extend the base removes the "every future subclass" cost entirely: there is no future subclass, by design.

### Case two: the checked exception

Lesson 15 gave the actual criterion, which review turns into a question about a specific `throws` clause rather than a rule of thumb: can a reasonable caller of this exact method do something other than give up right here?

**The cost, named precisely.** A checked exception in a signature is a demand on every caller, transitively, up the call stack to whoever first catches it or lets the program stop. Each intermediate caller either declares the same exception, propagating the demand further, or catches it with no actual response, usually by wrapping it as unchecked and rethrowing, which quiets the compiler while adding nothing.

The propagation gets sharper once a checked exception meets an interface that had no opinion about it. `Function<T, R>`, the interface behind every `.map()` lambda, declares no exception on `apply`, because it was written for the general case:

```java
List<String> paths = List.of("a.txt", "b.txt");
List<String> contents = paths.stream()
        .map(p -> Files.readString(Path.of(p)))
        .collect(Collectors.toList());
```

This fails to compile:

```text
error: unreported exception IOException; must be caught or declared to be thrown
                .map(p -> Files.readString(Path.of(p)))
                                          ^
```

`Files.readString` throws a checked `IOException`, `Function.apply` has no `throws` clause to receive it, and there is no signature anywhere in this expression for the exception to land on. The lambda has to catch it on the spot, at the point in the code with the least context about what the caller of the whole pipeline could do about a missing file. A checked exception does not stay a private detail of the method that throws it; it becomes a design problem for every interface the failure passes through, whether or not that interface had an opinion about failure at all.

**The test.** Ask it about the caller of the specific method under review: does this caller have a real next step, retry, fall back to a default, ask for different input, or only "log this and stop"? `IOException` from opening a configuration file earns checked status when the caller can fall back to a default; the same exception three layers up inside a pipeline with no fallback available there is not earning anything.

**The review sentence.** "This `throws ConfigException` is caught at every one of its four call sites by wrapping it in a `RuntimeException` and rethrowing, so none of those callers has a different response available; making `ConfigException` unchecked removes four blocks of ceremony and loses nothing."

**Where a checked exception is right.** When the test comes back yes. A method opening a network connection, reading a file, or parsing user input usually fails for a reason outside the program, and a caller commonly has a next step: retry with backoff, open a different resource, show the user which field was invalid. Lesson 15's `IOException` is the standing example, and the checked status forces every caller to decide rather than letting the failure surface as a bug report from someone who never knew a decision point existed.

### Case three: the stream chain

This is the case reviewers get wrong most often, because the temptation is to object that a chain feels less direct than a loop, a mood wearing a technical costume. Lessons 17 and 18 gave the real vocabulary; the review's job is to point at one of four concrete costs, not at a general dislike of the syntax.

**Cost one: a chain that cannot be stepped through.** A `for` loop gives a debugger one statement per line to stop on, with local variables visible at each one. A chain of five or six intermediate operations gives far fewer places to land, and inspecting a value at any stage means stream-specific debugger tooling or breaking the chain apart just to see inside it. Worth naming once a pipeline is complex enough that someone will need to debug it; not worth naming for a three-stage `filter().map().toList()` nobody will ever need to step through.

**Cost two: an intermediate operation with a side effect.** A lambda passed to `map`, `filter`, or any intermediate operation is documented to be non-interfering and stateless, and a pipeline is free to skip calling it for elements it does not end up needing:

```java
List<String> orders = List.of("A1", "A2", "B1", "A3", "B2");
int[] seen = {0};
List<String> firstTwo = orders.stream()
        .map(o -> { seen[0]++; return o; })
        .limit(2)
        .toList();
```

Running this gives `firstTwo = [A1, A2]` and `seen = 2`, not `5`. `limit(2)` needed only two elements, so the pipeline never pulled the rest through `map`, and a counter meant to record how many orders were processed silently reports less than the truth: a mismatch between what the side effect assumes, that it runs once per element, and what the pipeline actually promises. `peek` carries the identical risk under a more misleading name, since its own documentation calls it a debugging aid the implementation may skip calling, which lesson 17 already covers.

**Cost three: a collector that throws where nobody looks.** `Collectors.toMap` refuses a `null` value by calling `Map.merge` internally, and the resulting `NullPointerException` names neither the key nor the value:

```java
record Order(String customerId, String note) {}

List<Order> orders = List.of(
        new Order("c1", "first order"),
        new Order("c2", null));
Map<String, String> notesByCustomer = orders.stream()
        .collect(Collectors.toMap(Order::customerId, Order::note));
```

```text
Exception in thread "main" java.lang.NullPointerException
	at java.base/java.util.Objects.requireNonNull(Objects.java:220)
	at java.base/java.util.stream.Collectors.lambda$uniqKeysMapAccumulator$0(Collectors.java:180)
	...
	at CollectorThrows.main(CollectorThrows.java:13)
```

The trace names `Collectors` internals, not `Order.note` or the customer with the missing note, so whoever is on call reconstructs the cause from the stack alone. A `for` loop doing the equivalent `put` accepts the `null` without complaint, so the failure here is a property of choosing `toMap`, not of the data being genuinely unrepresentable.

**Cost four: a loop written to look clever.** A pipeline that reaches for `peek` to keep a count the result depends on is not more idiomatic than the loop it replaces, it is the loop with its structure hidden:

```java
int[] paidCount = {0};
int paidTotal = orders.stream()
        .filter(o -> o.status().equals("PAID"))
        .peek(o -> paidCount[0]++)
        .mapToInt(Order::total)
        .sum();

int loopTotal = 0;
int loopCount = 0;
for (Order o : orders) {
    if (o.status().equals("PAID")) {
        loopTotal += o.total();
        loopCount++;
    }
}
```

Both give the same two numbers on the data used to check them, but that is the trap: the chain only works because nothing here short-circuits before `peek` runs, which `peek` never guarantees, only an accident of this chain having no `limit` in it yet. The loop states both facts as two independent statements and needs no such accident to stay correct. Lesson 17 already named the honest test: does the stream version read faster than the loop it replaces? Here it does not, and using `peek` to smuggle a second answer out of a pipeline built to produce one is the sign it was time to write the loop.

**What is not a legitimate objection.** "I would just use a loop here", with no cost named, aimed at a plain `filter` feeding `map` feeding `toList`, is taste dressed as a standard, and should not survive this lesson's question: what does it cost, who pays it, what is the alternative? If the answer is "nothing, nobody, none," the chain stays.

**Where the chain is right.** Lesson 17's best case: one source, a short run of stateless intermediate operations, one terminal operation, nothing ambiguous at any stage. `words.stream().filter(w -> w.length() > 3).map(String::toUpperCase).toList()` says what it does in the order it does it, and a loop would only add lines, not clarity.

### What else a Java review should catch

Brief, because this stage is about judgement rather than a checklist, but each of these is a defect worth naming on sight, with the lesson that already taught the underlying fact:

| Look for | Lesson |
|---|---|
| an `equals` and `hashCode` pair not overridden together, or one that breaks symmetry or transitivity | 3 |
| `Optional` used as a field or a constructor or method parameter | 16 |
| a mutable collection handed back from an accessor with no defensive copy | 14 |
| a shared mutable field read or written from more than one thread with no `synchronized`, `volatile`, or higher-level guarantee behind it | 23, 24 |
| a public signature that is hard to change later for the reasons a binary or source compatibility break makes true | 43 |

None of these needs the three-part comment spelled out every time, because the cost is already established by the lesson that taught it; naming the fact and pointing at the line is enough. A signature is reviewed differently, since getting it right the first time is what lesson 44 is for; a reviewer's job on a signature is to notice it is public and therefore permanent, not to redesign it in the comment thread.

### Reviewing the design, not the diff

The hardest comment to write well says the diff itself is fine, correctly implements what it set out to do, passes every test that matters, and the design underneath is the actual problem. It is hard because the author asked for feedback on ten changed lines and the honest answer is about the two hundred lines around them the diff did not touch, and because "approve this, but" reads to an anxious author as "reject this."

Say it in two separated parts, so the author can act on the first without waiting on the second: state plainly the change is correct and can go in, then open the design conversation separately, addressed to the design rather than the person, with the concrete cost this lesson has asked for throughout. "This correctly adds a fourth field to the growing `switch` in `PricingEngine`; it is now eleven cases long, and every new rule means a matching case here and in three other switches over the same enum elsewhere in the module, exactly the shape lesson 11's sealed types close off. Worth a follow-up ticket, not a blocker on this change." The author ships today and has a specific starting point for tomorrow, which is why two comments beat one that tries to be both.

### Receiving a review

The author's job here is symmetrical: make the cost visible, or accept it explicitly. If a named cost turns out not to apply, say why with the same specificity the comment used: "this cache is read-only after construction, so the shared field is not actually racing anything" is a complete answer. If the cost applies, fix it or accept it out loud in the pull request, where the decision is recorded, not in a private message that leaves no trace: "taking this on purpose, tracked in TICKET-4021" is one a future reader can find. "It works" is not a response to a named cost: a hierarchy that double-counts, a checked exception nobody can act on, and a collector that throws in production all worked, right up until they did not.

## Practice

1. ▢ A teammate submits `AuditedTagSet extends HashSet<String>` from this lesson's own example. Write the review comment.

<details markdown="1"><summary>Check</summary>

> This double-counts through `addAll`: `HashSet` inherits it from `AbstractCollection`, implemented by calling the overridden `add` once per element, so a bulk insert of 3 elements records `added=6` instead of `added=3`. That is an implementation detail of `HashSet`, not part of the `Set` contract, so it could change again on a future release. A field of type `Set<String>` with `add` and `addAll` forwarded explicitly, incrementing the counter in each, does not have this problem, because the delegate's internal calls never reach back into the wrapper.

</details>

2. ▢ This compiles and every existing test passes.

   ```java
   interface Notifier {
       void send(String message) throws NotificationException;
   }

   // every one of the four call sites in the codebase:
   try {
       notifier.send(message);
   } catch (NotificationException e) {
       throw new RuntimeException(e);
   }
   ```

   Write the review comment.

<details markdown="1"><summary>Hint</summary>

Apply lesson 15's test to `NotificationException` specifically, at the call sites shown, not to checked exceptions in general.

</details>

<details markdown="1"><summary>Check</summary>

> Every call site catches `NotificationException` only to wrap it in a `RuntimeException` and rethrow, so none of the four has a different response available; the checked status is producing four blocks of ceremony that all do the same thing. Making `NotificationException` extend `RuntimeException` removes all four `catch` blocks and loses nothing, because nothing downstream was ever going to act differently on catching it. If a future caller genuinely gets a retry path, that is the point to reconsider, not now.

</details>

3. ▢ Predict what this prints, then write the review comment.

   ```java
   List<String> orders = List.of("A1", "A2", "B1", "A3", "B2");
   int[] seen = {0};
   List<String> firstTwo = orders.stream()
           .map(o -> { seen[0]++; return o; })
           .limit(2)
           .toList();
   System.out.println("firstTwo=" + firstTwo + " seen=" + seen[0]);
   ```

<details markdown="1"><summary>Hint</summary>

`limit` is short-circuiting. How many elements does the pipeline actually have to pull through `map` to satisfy it?

</details>

<details markdown="1"><summary>Check</summary>

`firstTwo=[A1, A2] seen=2`, not `5`. The comment: "`seen` is meant to count how many orders were processed, but `limit(2)` stops the pipeline once it has two results, so `map`'s side effect only runs for elements pulled through before that, an accident of where `limit` sits rather than a property of the data. Counting has to be its own pass, `orders.stream().count()` or a plain loop, not a side effect riding on an operation free to skip elements."

</details>

4. ▢ For each, say whether it is a genuine defect worth the comment this lesson builds, or a case where the construct is the right tool. Justify each in one sentence.

   - a) A sealed interface with three permitted records, one method implemented identically in all three, pulled up into a shared abstract class the sealed hierarchy's author also owns.
   - b) A public `parseInput(String)` throws a checked `MalformedInputException`, and its only two callers, a CLI entry point and a batch importer, both catch it to show the user which line was wrong.
   - c) `orders.stream().filter(Order::isPaid).map(Order::total).reduce(0, Integer::sum)`, used once, on one line, with no further processing.
   - d) A `Cache<K, V>` class extends `LinkedHashMap<K, V>` purely to reuse its `removeEldestEntry` hook for an LRU eviction policy, and never exposes `Cache` where a `Map` is expected.

<details markdown="1"><summary>Check</summary>

a) Right tool. The hierarchy is sealed, no fourth subclass can appear, and the base class's author and every subtype's author are the same person, Bloch's skeletal implementation case.

b) Right tool. Both callers have a real, different next step, so the checked status forces a decision both actually use.

c) Right tool. One source, one stateless chain, one terminal operation, nothing a debugger needs to step through and nothing a loop would say more clearly.

d) Worth a narrow comment: `LinkedHashMap` exposes `put`, `remove`, and every other `Map` method publicly, so even though `Cache` is never handed out as a `Map` today, those methods are callable by any code in the same package or subclass, bypassing whatever eviction discipline `Cache` thinks it owns. "This only needed one hook, `removeEldestEntry`; a held `LinkedHashMap` field with `get` and `put` forwarded keeps that hook without exposing the rest of `Map`."

</details>

5. ▢ A change adds a twelfth `case` to a `switch` over an `enum` that already had eleven, each `case` computing one pricing rule, and the same `enum` is switched over in three other files in the module with the same shape. The new case is correct and every test passes. What do you write?

<details markdown="1"><summary>Check</summary>

Two separate comments. First, approve the change on its own terms: correct, tested, should not wait on anything else. Second, open the design conversation separately: "Unrelated to this change, which is fine as is: this `enum` is switched over in four places with the same case list, and every new rule means editing all four in step, exactly what a sealed interface with one implementation per case would remove, since the compiler would refuse to compile any of the four switches until the new case was handled everywhere. Worth a follow-up, not a blocker here." Separating the two keeps the correct, shippable change from being held hostage to a real but larger conversation.

</details>

## Real-world reps

- [ ] Find a class that extends a JDK collection or utility class and check whether it overrides one method of a pair where the other calls back into it, the way `add` and `addAll` do here. Write the three-part comment even if you never send it.
- [ ] Find a checked exception in your own code and apply lesson 15's test at each of its actual call sites. Note which sites have a real next step and which only wrap and rethrow.
- [ ] Take a stream pipeline from a past review and check it against this lesson's four costs: debuggability, a side-effecting intermediate operation, a collector that can throw unexpectedly, and a loop wearing a chain's clothes.
- [ ] Practice the two-comment split on a real diff: approve what is correct, and write the design comment separately, addressed to the code rather than the author.
- [ ] Tomorrow: take the last review comment you sent that said something felt wrong, and rewrite it with the cost, the payer, and the alternative named, even if the review already closed.

## Going further

- [JLS Chapter 8, Classes, Java SE 25](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html): the rules a subclass and an override are actually bound by, worth having open when a review argument about `extends` needs settling on the specification rather than on memory
- [`Function`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/function/Function.html): the interface behind `.map()`, and a look at how little opinion a functional interface has about what a lambda might throw
- [`Collectors`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html): `toMap`'s exact null and duplicate-key behaviour, worth rereading before flagging a collector in review
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
