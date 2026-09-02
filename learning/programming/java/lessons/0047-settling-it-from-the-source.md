---
title: 47. Settling It From the Source
description: Where to look when the argument is about what Java does, and which document answers which question
type: lesson
---

# Lesson 47. Settling It From the Source

**Mission link:** When an argument about what Java actually does reaches your production service, whether a signature really broke callers or a `synchronized` block really still pins a carrier, the fastest way to end it is to open the document that settles it and run the code that confirms it, rather than trusting the search result that merely sounds confident.
**Primary source:** [The Java Language Specification, Java SE 25](https://docs.oracle.com/javase/specs/jls/se25/html/index.html)
**Prerequisites:** [Lesson 43](0043-what-counts-as-breaking.md), [Lesson 13](0013-generics-and-erasure.md)

## Warm-up

Lesson 43 ran an application's unchanged class files against a new library version and watched `Config.items()` fail with `NoSuchMethodError: 'java.util.List lib.Config.items()'`, naming a method descriptor that no longer existed. Which document defines what a descriptor actually is and how a class loader resolves one at link time: the Java Language Specification, or a different specification entirely?

<details markdown="1"><summary>Check</summary>

A different one. The Java Language Specification tells you what the source code meant, including why narrowing `Config.items()`'s return type was source-compatible. The descriptor, the class file format, and the linking process that turned that possibility into an actual thrown exception belong to the Java Virtual Machine Specification. Confusing the two wastes real time, because each document answers questions the other one does not even ask, and that gap is the whole subject of this lesson.

</details>

## Know this

Settling an argument about Java from a source rather than from opinion is a skill with its own technique, not a matter of knowing where the JLS lives as a bookmark. The technique has three parts: knowing which document answers which kind of question, knowing how to find the right place inside a document organised by construct rather than by task, and knowing that a JEP is a historical record rather than a live reference, so its claims need confirming by execution before you repeat them.

### Which document answers which question

Five documents come up again and again once an argument gets specific enough to need a citation, and each one is authoritative for a different kind of question. Reaching for the wrong one is the single biggest waste of time in this kind of research, because each document is organised for its own purpose and simply does not contain the answer to a question it was not written to settle.

| Question | Document | What it is uniquely good for |
|---|---|---|
| What does the language mean: overload resolution, generics, definite assignment, exhaustiveness | The Java Language Specification | The rules the compiler actually applies, stated as rules rather than as examples |
| What is a descriptor, how does linking work, what does a class file contain | The Java Virtual Machine Specification | The one level down from the language, which is where a `NoSuchMethodError` or an `AbstractMethodError` actually comes from |
| What does this method promise | The API documentation | A contract that binds even when nothing in a specification mentions the method at all |
| Why does a feature exist, what was it arguing against | The JEP that introduced it, found through [JEP 0](https://openjdk.org/jeps/0), the JEP index | The intent and the rejected alternatives, which no other document records |
| Which releases are still maintained | The [Oracle Java SE Support Roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html) | A schedule, not a technical claim, and the only one of the five that goes stale on its own without anyone changing the language |

A question about whether a change breaks callers is the case where the routing needs stating carefully, because both documents have something to say and lesson 45 cites the one you might not expect. The Java Language Specification's chapter 13 is titled Binary Compatibility, and it is the right source for **which changes preserve it**: it enumerates, change by change, what you may do to a type without invalidating already-compiled code, which is why lesson 45 rests on it. The Java Virtual Machine Specification is the right source for **why a break happens at all**: descriptors, resolution and linking, which is where the `NoSuchMethodError` in lesson 43 actually came from. So the rule is not "source questions to one and binary questions to the other". It is that the language specification tells you the rule and the virtual machine specification tells you the mechanism, and you want the second only when the first has not settled it. A question about why virtual threads exist at all, rather than what they currently do, goes to a JEP and nowhere else, because the reasoning that led to a design is not the kind of fact a specification records.

### Turning a question into a construct

The specification's table of contents is organised by language construct: classes in one chapter, expressions in another, threads and locks in a third. It is not organised by the task a working programmer actually has, which is why searching the specification for "is my change safe" fails outright and searching it for "binary compatibility" lands on chapter 13 immediately. The move that makes the specification usable is to translate the question into the construct it is really about before opening anything.

"Does narrowing a return type break an unrecompiled caller" is really a question about binary compatibility, so it goes to chapter 13. "Which of two overloaded methods gets picked" is really a question about a method invocation expression, so it goes to chapter 15, specifically section 15.12. "Does `happens-before` guarantee what I think it guarantees" is really a question about the memory model, so it goes to chapter 17, Threads and Locks, exactly where stage 4 already sent you for `synchronized` and `volatile`. Chapter 8 covers classes, chapter 13 covers binary compatibility, chapter 15 covers expressions including evaluation order and overload resolution, and chapter 17 covers threads and locks. None of those four chapters has a section called "is this safe" or "which one wins", because the specification answers questions about constructs, and turning your question into the right construct first is the actual research skill.

### Worked lookup 1: evaluation order against operator precedence

Here is a question where intuition is unreliable. Given `a() + b() * c()`, each call printing its own name, does `*`'s higher precedence mean `b()` and `c()` run before `a()`, since multiplication is "done first"?

Precedence decides how an expression's operators group into a tree, nothing about when each piece of that tree actually runs. [The Java Language Specification, chapter 15, section 15.7](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.7) states the actual rule plainly: "the Java programming language guarantees that the operands of operators appear to be evaluated in a specific evaluation order, namely, from left to right", and section 15.7.1 sharpens it further: "The left-hand operand of a binary operator appears to be fully evaluated before any part of the right-hand operand is evaluated." Running the code confirms it rather than merely restating it:

```java
public class Eval {
    static int a() { System.out.println("a"); return 1; }
    static int b() { System.out.println("b"); return 2; }
    static int c() { System.out.println("c"); return 3; }
    public static void main(String[] args) {
        int r = a() + b() * c();
        System.out.println("result = " + r);
    }
}
```

This printed `a`, `b`, `c`, then `result = 7`, in that order, every time. The multiplication still happens before the addition, since precedence decided that `b() * c()` is one subexpression that the addition then consumes, but the calls that build the operands of `+` run left to right regardless: `a()` first as the left operand of `+`, then `b()` and `c()` as the two calls needed to build the right operand. Precedence answers "what operates on what"; evaluation order answers "what runs when", and they are two different questions the specification keeps carefully separate.

### Worked lookup 2: what an exhaustive switch compiles to, and why an unrecompiled one can fail

Lesson 11 taught that a `switch` over a sealed hierarchy can omit `default` because the compiler can enumerate every permitted subtype and prove the switch covers them all. The reasonable guess from there is that an exhaustive switch, once compiled, is exhaustive forever: the compiler proved it, so there is nothing left to check at run time. Lesson 45 has already shown you that this guess is wrong and what the failure looks like, so take the failure as given here. What that lesson did not do, and what this one is for, is show where the specification says so and what the compiler emitted to make it true.

[The Java Language Specification, section 14.11.1.1](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.11.1) defines exhaustiveness as a property the compiler checks against the hierarchy it can see at compile time: "The switch block of a switch expression or switch statement is exhaustive for a selector expression `e` if... the set containing all the `case` constants and `case` patterns... covers the type of the selector expression `e`." That proof belongs to one compilation, against the hierarchy as it existed then, and section 14.11.1.1 lives in chapter 14, Blocks, Statements, and Patterns, not chapter 15, even though a switch expression is unmistakably an expression, which is another case of the specification organising by the shared construct, a switch block, rather than by the kind of question you actually have.

Compiling a switch with two cases over a sealed interface with two permitted types and inspecting it with `javap -c` shows exactly what the compiler leaves behind for the case its own proof did not anticipate:

```text
9: aload_1
10: iload_2
11: invokedynamic #13,  0    // InvokeDynamic #0:typeSwitch:(Lapi/Shape;I)I
16: lookupswitch  { // 2
               0: 54
               1: 64
         default: 44
    }
44: new           #17         // class java/lang/MatchException
47: dup
48: aconst_null
49: aconst_null
50: invokespecial #19         // Method java/lang/MatchException."<init>":(Ljava/lang/String;Ljava/lang/Throwable;)V
53: athrow
```

The compiler always generates a `default` arm that throws `MatchException`, even for a switch it proved exhaustive, because the proof is a compile-time fact about the hierarchy as it stood then and the class file has to survive a hierarchy that might not stand still. Recompiling `Shape` with a third permitted type added, without recompiling the class holding the switch, and then passing an instance of that third type into the old, unrecompiled switch, threw exactly that:

```text
Exception in thread "main" java.lang.MatchException
	at Describe.describe(Describe.java:4)
	at Main2.main(Main2.java:4)
```

This is the switch expression's version of lesson 43's `NoSuchMethodError` and `AbstractMethodError`: a change that is perfectly safe for anyone who rebuilds, adding a permitted subtype to an already-shipped sealed hierarchy, and fatal for a compiled switch that never got the chance to prove exhaustiveness against the new shape. The exhaustiveness the compiler promised was true, and it was true about a hierarchy that stopped matching reality.

### Worked lookup 3: how overload resolution picks between two applicable methods

Given `static void m(long x)` and `static void m(Integer x)`, and a call `m(n)` where `n` is a plain `int` variable, which one runs? A common guess reaches for `Integer`, on the theory that boxing an `int` into its own wrapper type is the "natural" match and a `long` is a different type altogether.

[The Java Language Specification, section 15.12.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.2) settles it by describing the search as a staged one: "There may be more than one such method, in which case the most specific one is chosen", and the process of finding an applicable method at all "continues in three phases" to preserve compatibility with code older than generics. Section 15.12.2.2 names the first of those phases "Identify Matching Arity Methods Applicable by Strict Invocation", and strict invocation excludes boxing and unboxing entirely; only if phase 1 finds nothing does section 15.12.2.3's phase 2, "Identify Matching Arity Methods Applicable by Loose Invocation", even consider a boxing conversion. Widening `int` to `long` is a conversion strict invocation already allows, so `m(long)` is found and chosen in phase 1, before boxing to `Integer` is ever considered:

```java
public class Pick {
    static void m(long x) { System.out.println("long: " + x); }
    static void m(Integer x) { System.out.println("Integer: " + x); }
    public static void main(String[] args) {
        int n = 5;
        m(n);
    }
}
```

Running it printed `long: 5`. That is the specification's phase ordering doing exactly what section 15.12.2.2 and 15.12.2.3 describe, and it is worth stopping there: which signature to write so that this ordering never matters to a caller is a design question, and lesson 44 owns that argument. What is settled here is narrower and purely descriptive: given two already-written overloads, this is the rule the compiler actually follows, not a rule of thumb about which type "feels" more specific.

### The JEP: what it is uniquely good for, and the trap it sets

A specification states what is true. A JEP states why someone decided it should be true, which arguments were rejected along the way, and what the feature was designed to fix, none of which survives into the specification's finished, argument-free prose. That makes a JEP the only document that answers "why is it like this" convincingly, and no specification, however carefully read, will ever answer that question as well as the proposal that made the case.

The trap is that a JEP describes the release it shipped in and is never revised afterwards, even when a later JEP changes the very behaviour it described. [JEP 444, Virtual Threads](https://openjdk.org/jeps/444), delivered in Java 21, still states in its body text that pinning happens "when it executes code inside a synchronized block or method", and its section on future work says only that "in a future release we may be able to remove the first limitation above, namely pinning inside `synchronized`", written as an open possibility rather than a fact already settled. [JEP 491, Synchronize Virtual Threads without Pinning](https://openjdk.org/jeps/491), delivered in Java 24, is that future release: its summary states the goal plainly, to "eliminate nearly all cases of virtual threads being pinned to platform threads" for `synchronized` methods and statements. Both JEPs' header tables now carry a "Relates to" line pointing at each other, added as bookkeeping after the fact, but that cross-reference lives in the metadata table, not in JEP 444's prose, so a reader of the body text alone gets the older, now incomplete picture with no signal inside the paragraph itself that anything changed.

Running the check settles which one describes today's JDK 25. Starting a virtual thread that blocks inside a `synchronized` block, with pinning diagnostics switched on:

```java
public class Pin {
    static final Object LOCK = new Object();
    public static void main(String[] args) throws Exception {
        Thread vt = Thread.ofVirtual().start(() -> {
            synchronized (LOCK) {
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {}
            }
        });
        vt.join();
        System.out.println("done");
    }
}
```

Run with `-Djdk.tracePinnedThreads=full`, this printed only `done`, with no pinning trace at all. If JEP 444's body text were still the last word, that run should have reported the virtual thread pinned to its carrier for the whole 200 milliseconds; it did not, because JEP 491 already changed the behaviour the older JEP described. A JEP's own header table does carry its status and target release, Closed and Delivered at release 21 for JEP 444, Closed and Delivered at release 24 for JEP 491, which is how you tell a delivered feature from a withdrawn proposal at a glance, but that table cannot tell you that a sibling JEP has since overtaken a specific claim buried in the prose beneath it. The rule this earns: read a JEP for intent and for the alternatives it rejected, since nothing else records either, and confirm current behaviour by running it, since a JEP is a historical record of an argument and not a reference manual that keeps itself current.

### How to close an argument in practice

Closing an argument about what Java does has two parts, and they are not the same claim. Cite the document and the exact section: "chapter 15, section 15.12.2, phase 1" is a claim about what the specification says. Separately, state what you observed by compiling and running the code: "printed `long: 5`" is a claim about what actually happened on the release in hand. Most of the time these agree, and citing both is simply thorough. When they disagree, as JEP 444's prose and JEP 491's delivered behaviour do on pinning, that disagreement is itself the finding worth writing down and sharing, not a puzzle to quietly resolve before anyone else sees it, because the next person to hit that JEP will hit the same stale claim you just found.

## Practice

1. ▢ Predict the print order and the final value of `int total = p() - q() / r();`, where `p`, `q` and `r` each print their own name before returning `9`, `3` and `1` in that order.

<details markdown="1"><summary>Check</summary>

`p`, `q`, `r` print in that order, left to right, regardless of the fact that `/` groups `q()` and `r()` together before the subtraction runs. `total` is `9 - (3 / 1)`, which is `6`. Section 15.7 guarantees the print order; ordinary integer division rules, not evaluation order, decide the value.

</details>

2. ▢ A sealed interface `Vehicle` permits `Car` and `Bike`, shipped in a jar. A switch expression over `Vehicle` with cases for `Car` and `Bike`, no `default`, is compiled against that jar in a separate application and shipped on its own. The jar is later redeployed with a third permitted type, `Truck`, added to `Vehicle`, and the application is not recompiled. A `Truck` instance reaches the switch at run time. What happens, and where does the answer come from in the switch's own compiled code?

<details markdown="1"><summary>Hint</summary>

The compiler proved the switch exhaustive against two permitted types. Ask what it generated for the case its proof never considered.

</details>

<details markdown="1"><summary>Check</summary>

It throws `java.lang.MatchException`. `javap -c` on the compiled switch shows a synthetic `default` arm, generated by the compiler even though the switch was proven exhaustive, that constructs and throws `MatchException` when the selector matches none of the compiled `case` labels. The exhaustiveness proof in section 14.11.1.1 was true of the two-permits hierarchy at compile time and stays compiled into the class file; it says nothing about a hierarchy that grows a third permitted type afterwards.

</details>

3. ▢ Two overloads exist, `print(Object o)` and `print(String s)`. A caller writes `print(null)`. Which one runs, and why does the other not win instead?

<details markdown="1"><summary>Check</summary>

`print(String s)` runs, printing `String: null`. `null` is assignable to both parameter types, so both overloads are applicable, but `String` is more specific than `Object`, and section 15.12.2's most-specific-method step prefers the most specific of the applicable methods rather than leaving the choice ambiguous. `print(Object o)` loses precisely because being more general is the property that loses a tie between two otherwise applicable methods.

</details>

4. ▢ A teammate claims `ArrayList` is thread-safe "because the Javadoc doesn't say otherwise." Which document actually settles a claim like this, and what does it say for `ArrayList` specifically?

<details markdown="1"><summary>Check</summary>

The API documentation settles it, since a class's thread-safety is a contract question, not a language-rules question, and the Java Language Specification has nothing to say about any particular class. `ArrayList`'s own documentation states plainly: "Note that this implementation is not synchronized." Silence would not have been a promise either way, but this is not silence: the contract is explicit, and the teammate's reasoning has the API documentation's default backwards.

</details>

5. ▢ You want to know whether a `synchronized` block still pins a virtual thread's carrier on the release you are running. Which document should you read first for why that behaviour existed and what changed about it, and which single check actually settles the question for your release?

<details markdown="1"><summary>Check</summary>

Read JEP 444 for why pinning existed in the first place and JEP 491 for the design that removed most of it, since between them they record the argument that no specification bothers to keep. Neither JEP's prose is guaranteed current, since JEP 444's body still describes the old behaviour without update. The check that settles it for your actual release is running a virtual thread that blocks inside a `synchronized` block with `-Djdk.tracePinnedThreads=full` and reading whether a pinning trace appears at all.

</details>

## Real-world reps

- [ ] Take an argument your team had recently about what Java does, and write down which of the five documents in this lesson's table should have settled it, before searching for anything.
- [ ] Find one method call in code you maintain where an overload could plausibly be ambiguous, and work out from section 15.12.2 which phase actually resolves it.
- [ ] Pick a JEP for a feature you use regularly, read its Motivation section for the alternative it argued against, and check whether a later JEP has touched the same behaviour since.
- [ ] Run the pinning check from this lesson against a `synchronized` block you actually use in a service, and record what you observed rather than assuming it matches either JEP.
- [ ] Tomorrow: the next time someone states a fact about Java in a review or a chat, ask them which document it came from before agreeing or disagreeing with it.

## Going further

- [The Java Virtual Machine Specification, Java SE 25](https://docs.oracle.com/javase/specs/jvms/se25/html/index.html): the document one level down, for a descriptor, a class file or a linking failure that the language specification does not cover
- [Java SE 25 API Documentation](https://docs.oracle.com/en/java/javase/25/docs/api/index.html): where a method's contract lives, including the `ArrayList` synchronisation note quoted above, which no specification states
- [Kinds of Compatibility, OpenJDK Compatibility and Specification Review](https://wiki.openjdk.org/display/csr/Kinds+of+Compatibility): the platform's own working vocabulary for source, binary and behavioural compatibility, used to review every change to the JDK itself
- [JEP 0, the JEP Index](https://openjdk.org/jeps/0): every proposal with its status and target release, the starting point for finding the JEP that argues for a feature you are relying on
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
