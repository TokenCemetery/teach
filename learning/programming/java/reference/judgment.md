---
title: Judgment
description: Which changes break what, how to retire an API, and how to argue the call from the source
type: reference
---

# Judgment

## The three compatibilities

"Breaking" names three independent facts about a change, not one, and each has its own test, checked by a different mechanism. See [lesson 43](../lessons/0043-what-counts-as-breaking.md).

| Compatibility | One-line definition | The test |
|---|---|---|
| Source | Code that used to compile against the old version still compiles, unchanged, against the new one | Recompile the caller's `.java` files against the new version and see whether it succeeds |
| Binary | Code already compiled against the old version still links and runs against the new one, with no recompilation at all | Leave the caller's `.class` files untouched and run them against the new jar |
| Behavioural | Code that compiles and links successfully still does the same thing it did before | Run it and compare the output |

Knowing one of the three holds tells you nothing about the other two: the same edit to `Config` in lesson 43 was source-incompatible for one member, binary-incompatible for another, and left a third silently correct on the surface while inlining stale data underneath it. What decides which of the three actually matters for a given piece of code is the caller, not the code: does everyone who depends on this rebuild before running it, or could an already-compiled caller run against the new version unchanged. A module always rebuilt from a clean checkout has no binary-compatibility risk, since nothing of its own ever runs unrecompiled against itself; a published library or anything else consumed as a jar rather than as rebuilt source has all three live, and binary compatibility is the dangerous one precisely because it fails later, in someone else's production, rather than in a build that would have stopped it. See [lesson 43](../lessons/0043-what-counts-as-breaking.md) and [lesson 45](../lessons/0045-evolving-a-type.md).

## Change to compatibility cost

One row per kind of change, drawn from what lessons 43 and 45 actually ran. The right-hand column names which compatibilities the change costs; "Silent" in the last column marks a failure that produces no compile error, no link error and no exception anywhere, which is what makes it the dangerous kind.

| Change | Costs | Silent? |
|---|---|---|
| Change a `public static final` primitive or `String` constant's value | Behavioural: the old value keeps reporting forever for callers who never recompile | Yes, permanently: the value was inlined at the caller's own compile time |
| Change an ordinary (non-constant) method's behaviour | Behavioural, immediately, for every caller regardless of rebuild | No, the expected case |
| Narrow a method's return type (`List` to `ArrayList`) | Source-compatible on recompile; binary-incompatible without it | No, loud: `NoSuchMethodError` naming the old descriptor |
| Widen a method's return type back | Binary-incompatible the same way; source-incompatible too if a caller relied on a method only the narrower type offered | No, loud: `NoSuchMethodError` |
| Remove a member entirely | Both source and binary | No, loud on both: a compile error, and separately `NoSuchMethodError` |
| Add a brand new method with no name clash | Nothing, except a rare overload-resolution ambiguity for an existing call | No |
| Add an abstract method to an interface | Source on rebuild; binary and behavioural for anyone who never rebuilds | No, loud both ways: a compile error, or `AbstractMethodError` at the call |
| Add a default method to an interface | Nothing | No |
| Remove a default method, or turn it abstract | Binary and behavioural, for already-compiled implementors | Delayed: loads and runs until the missing method is actually called, then `AbstractMethodError` |
| Add a component to a record | Source and binary, since the canonical constructor's descriptor changes | No, loud: a compile error, or `NoSuchMethodError` unrecompiled |
| Reorder a record's existing components | Behavioural only | Yes, completely: descriptor unchanged, accessors return values with no error, just the wrong ones |
| Add a static factory, a derived method, or compact-constructor validation to a record | Nothing | No |
| Add a constant to an enum | Behavioural, for any unrebuilt exhaustive `switch` | Effectively yes, until a value of the new constant reaches the old switch, then `MatchException` |
| Widen `permits` on a sealed type | The same `switch` failure as an enum constant | Effectively yes, until that path runs, then `MatchException` |
| Narrow `permits` on a sealed type | Binary, for any already-compiled permitted subclass | No, loud and immediate: `IncompatibleClassChangeError` at class load |
| Add a field or method, or widen access, on an ordinary class | Nothing | No |
| Add a constructor overload with a parameter type unrelated to an existing one | Source, for `null` call sites now ambiguous | No, loud: a compile error |
| Change a method from non-`final` to `final` | Source, for overriding subclasses that rebuild | Silent until a subclass rebuilds, then loud |

See [lesson 43](../lessons/0043-what-counts-as-breaking.md) and [lesson 45](../lessons/0045-evolving-a-type.md). A build plugin such as `japicmp-maven-plugin` or `revapi-maven-plugin` can fail a build automatically on a binary-incompatible change, mechanising this table rather than replacing the judgment behind it.

## Failure to cause

Each of these is a symptom this stage actually produced by running code, plus the two failures that produce no symptom at all.

| Failure | What actually caused it |
|---|---|
| `NoSuchMethodError` | An already-compiled caller's bytecode names a method by name and descriptor that the new version no longer has, most often from a changed return or parameter type |
| `AbstractMethodError` | An already-compiled class implements an interface that lost a default body, or gained a new abstract method, after that class was compiled; it loads and runs until the missing method is actually called |
| `MatchException` | A `switch` was proven exhaustive against the enum constants or sealed permitted types visible at compile time, and a value from a constant or subtype added afterwards reaches that same unrecompiled switch |
| `IncompatibleClassChangeError` (permitted subclass check) | A sealed type's `permits` list was narrowed, and the class loader itself, not only the compiler, refuses to load a class already compiled against the wider list |
| Silent: a stale value that never updates | A `public static final` primitive or `String` field was inlined at the caller's own compile time; there is no field access left in its bytecode for a new value to answer |
| Silent: a record's values look swapped | The components were reordered without changing arity or types, so the descriptor is unchanged, the call still resolves, and the values come back bound to the wrong names |

See [lesson 43](../lessons/0043-what-counts-as-breaking.md), [lesson 45](../lessons/0045-evolving-a-type.md) and [lesson 47](../lessons/0047-settling-it-from-the-source.md).

## Compile-time constants

A compile-time constant, in the sense the specification gives the phrase, is a `static final` field of a primitive type or `String`, initialised with an expression the compiler can evaluate on the spot. `javac` inlines every one of these into each caller's class file at the caller's own compile time, so the value stops being something your class hands out at run time and becomes something copied into other people's binaries the moment they compile against you.

| Declaration | Compile-time constant | Consequence for callers |
|---|---|---|
| `public static final int MAX = 10;` | Yes | Folded straight into the caller's constant pool; changing it later is invisible until that caller recompiles |
| `public static final String NAME = "v1";` | Yes | Same folding, often concatenated straight into a literal string operand |
| `public static int MAX = 10;` (no `final`) | No | Read with a genuine `getstatic`, resolved against whatever is on the classpath at run time |
| `public static final List<String> ITEMS = List.of("a");` | No | Reference types other than `String` are never compile-time constants, whatever value they hold |

If a value must ever be correctable after the fact, without waiting for every caller to rebuild, it cannot be a `public static final` primitive or `String` field. Expose it through an ordinary static method instead, `public static int max() { return MAX; }`, since a method call is never inlined: it resolves at run time by name and descriptor against whichever class is on the classpath, the same mechanism that let an ordinary method's new behaviour arrive for free in lesson 43's own experiment. See [lesson 43](../lessons/0043-what-counts-as-breaking.md).

## Parameters against return types

A parameter type is a demand on the caller; a return type is a promise to the caller. Loosening a demand later costs nobody who already satisfied the stricter version, while loosening or narrowing a promise later can break every caller who relied on the version shipped first, exactly the failure lesson 43 measured for `Config.items()`.

| | Parameter type | Return type |
|---|---|---|
| What it is | A minimum demanded of the caller | A maximum promised to the caller |
| Safe direction to move later | Generalise; every existing caller still satisfies a weaker demand | Neither narrowing nor widening is safe; both are binary-incompatible |
| The test to apply | Find the weakest type that still declares every call the body makes | Ask whether every caller can rely on the guarantee, not what today's implementation happens to offer |
| What it should never be | Stricter than the body needs, purely by habit | A concrete implementation class (`ArrayList`, `HashMap`), which names an implementation, not a contract |

Generalising is not free of judgment: a parameter type is documentation too, and demanding `Collection` when the contract genuinely depends on order makes the signature lie about what it needs, not more flexible. See [lesson 44](../lessons/0044-designing-a-signature.md).

## Overloading and overload resolution

Overload resolution picks which same-named method a call invokes once, at compile time, from the declared static type of each argument; it has nothing to do with the runtime object, the opposite of overriding and the mismatch that makes overloading surprising.

| Rule | Detail |
|---|---|
| Resolved statically | By the declared type of each argument, never the runtime class; `var` changes nothing, since it infers the same declared type the explicit form would carry |
| Safe to overload | Genuinely the same operation over convertible argument types, the way `StringBuilder.append(String)`, `append(int)` and `append(char)` never disagree |
| Use a different name instead | When two same-named methods answer different questions rather than one operation over convertible inputs |
| A new overload beside an existing one | Safe for an existing `null` call site only when its parameter type is a strict supertype of an already-applicable one; an unrelated reference type makes the call site ambiguous |

The specification resolves an ambiguous-looking call in stages rather than by instinct: given `m(long x)` and `m(Integer x)` called with a plain `int`, the widening conversion to `long` is found in the phase that excludes boxing entirely, so `Integer` is never even considered. Which signature to write so this ordering never matters to a caller is a design question lesson 44 owns; which method a given pair of overloads resolves to is a descriptive fact lesson 47 settles from the specification.

| Phase (JLS 15.12.2) | What it considers |
|---|---|
| 1, strict invocation | Widening conversions only, no boxing or unboxing |
| 2, loose invocation | Boxing and unboxing, only if phase 1 found nothing |
| 3, variable arity | Varargs methods, only if phases 1 and 2 both found nothing, kept for compatibility with code written before generics |

See [lesson 44](../lessons/0044-designing-a-signature.md) and [lesson 47](../lessons/0047-settling-it-from-the-source.md).

## Varargs costs

A trailing `T... name` parameter is sugar for `T[]`, and that desugaring carries two costs a signature's author should decide about deliberately rather than by accident.

| Trap | What actually happens |
|---|---|
| An allocation per call, invisible at the call site | Passing an existing array of the exact type costs nothing extra, since the compiler hands it over unchanged; passing a literal list of values allocates a fresh array to hold them, once per call |
| An empty call compiles by default | A varargs parameter accepts zero arguments unless the signature says otherwise, since an empty array is a completely ordinary array; correct for an operation like summing, where zero terms honestly sum to zero, and a silent wrong answer for an operation like `max`, which has no honest answer for the empty case |
| The fix for the second trap | Pull a mandatory value out of the varargs: `max(int first, int... rest)` turns `max()` into a compile error, "actual and formal argument lists differ in length", instead of a silently wrong runtime answer |

See [lesson 44](../lessons/0044-designing-a-signature.md).

## What not to return

Three shapes of return value, plus the general case they are examples of, cause damage out of proportion to how easy they are to write.

| Return shape | Why it is a problem |
|---|---|
| `null` for absence | Type-checks identically to a value that means something; the only defence is remembering to check every time, forever, which is exactly what `Optional` as a return type exists to replace |
| An array where a collection is meant | Fixed length with no resize protection, and covariant in a way that can throw `ArrayStoreException` at the element-type boundary a `List` would have caught earlier or not at all |
| A mutable internal collection, returned by reference | Hands the caller a key to the object's own internals rather than an answer; `List.copyOf` or an equivalent unmodifiable view returns data instead of exposing state, and the return type alone gives a caller no way to tell which one they are holding |
| A concrete implementation type as the contract | Names what today's implementation happens to be, not a guarantee any caller can rely on, and is exactly what lesson 43 measured the cost of walking back |

See [lesson 44](../lessons/0044-designing-a-signature.md).

## Evolving each construct

No construct has a change that is free in both directions; the table below groups lesson 45's findings by what each construct can absorb without cost against what always asks something of somebody.

| Construct | Safe, additive | Not safe |
|---|---|---|
| Interface | A default method: every existing implementor inherits it with no rebuild needed | An abstract method (source break on rebuild, `AbstractMethodError` for anyone who never rebuilds); removing a default, or turning it abstract (binary and behavioural break for existing implementors) |
| Record | A static factory, a derived method, or compact-constructor validation, none of which touch the canonical constructor's descriptor or the accessor set | Adding, removing or reordering a component: adding fails a build, reordering silently corrupts data with no error at all |
| Enum | Nothing is entirely free: a new constant costs no compile or link error but is behaviourally live for any unrebuilt exhaustive `switch` with no `default` | The same case, seen from the consumer's side: `MatchException` the moment a value of the new constant reaches an old switch |
| Sealed hierarchy | Nothing is free either way, since the closed set is the entire point of sealing | Widening `permits` risks the same `MatchException` as an enum constant; narrowing it risks `IncompatibleClassChangeError` for an already-compiled permitted subclass, checked at class load |
| Class | Adding a field or method, or widening access from `private` to `protected` or `public` | A constructor overload unrelated to an existing one (ambiguous for existing `null` call sites); a method changed from non-`final` to `final` (breaks an overriding subclass on its next rebuild) |

A default method buys compatibility, not correctness: a body that does nothing, or the wrong thing, lets every implementor keep compiling while silently inheriting behaviour nobody asked for, which is worse than a compile error because it is invisible until the exact path that needed the real behaviour finally runs. See [lesson 45](../lessons/0045-evolving-a-type.md).

## Deprecation defaults

`@Deprecated` alone and `@Deprecated(forRemoval = true)` are two distinct signals with two distinct default behaviours in the compiler, not one adjective made stronger.

| | Ordinary deprecation | Terminal deprecation |
|---|---|---|
| Written as | `@Deprecated` | `@Deprecated(since = "...", forRemoval = true)` |
| Meaning | A recommendation to migrate away, with no promise about removal | A stated intent to remove the member in a future release |
| Default compiler output, no flags | Folded into one generic, unnamed note per file: "uses or overrides a deprecated API" | A named warning of its own, category `[removal]`, visible with no flag required |
| Output with `-Xlint:deprecation` | A named warning, category `[deprecation]` | The same named warning, still category `[removal]` |

Before JEP 277 introduced this split, `@Deprecated` meant one thing regardless of intent, and its own account of the problem is blunt: nobody took a bare deprecation seriously, which made it difficult ever to remove anything from the platform's own API. See [lesson 46](../lessons/0046-deprecation-that-works.md).

## The three parts of a usable deprecation

An annotation on its own only announces; it does not help anyone comply.

| Part | What it must do | What is lost if it is missing |
|---|---|---|
| The annotation, with `since` and `forRemoval` set deliberately | Records the release the deprecation started in and states, truthfully, whether removal is genuinely intended | Tooling such as `jdeprscan` and the compiler's own warning categories have nothing to find |
| A Javadoc `@deprecated` tag naming the replacement | Tells a caller who wants to comply what to call instead | A warning turns into an investigation; `javac`'s `-Xlint:dep-ann` exists specifically to catch a `@deprecated` tag with no matching annotation, and the reverse gap is just as costly |
| A stated removal release | Turns "deprecated" into a bounded project rather than a resting state | Without it, "deprecated" has, on the platform's own record, sometimes meant exactly that: noted, not urgent, possibly permanent for a decade or more |

See [lesson 46](../lessons/0046-deprecation-that-works.md).

## Suppressing deprecation warnings

`@SuppressWarnings` uses the same category strings `-Xlint:deprecation` reports, and the two categories are independent, checked by compiling code that triggers both: suppressing one leaves the other visible.

| `@SuppressWarnings` key | Suppresses |
|---|---|
| `"deprecation"` | Ordinary `@Deprecated` members only, category `[deprecation]` |
| `"removal"` | Members marked `@Deprecated(forRemoval = true)` only, category `[removal]` |
| `{"deprecation", "removal"}` | Both categories at once |

Suppressing only `"deprecation"` on code calling both a plainly-deprecated and a for-removal member still surfaces the `[removal]` warning, and the reverse holds too, so the combined form is only safe once both categories are actually meant to be silenced.

## Using jdeprscan

`jdeprscan` takes a directory of class files, a jar, or a single class name.

| Invocation | What it does |
|---|---|
| `jdeprscan target/classes` | Scans a directory of compiled classes for calls to Java SE's own deprecated API |
| `jdeprscan legacy.jar` | Scans a jar the same way |
| `jdeprscan Legacy` | Scans a single named class |
| `jdeprscan --for-removal ...` | Reports only members marked `forRemoval = true` |
| `jdeprscan --release N ...` | Scans against release `N`'s deprecation set instead of the one bundled with the tool itself, which answers "will this code survive the upgrade" rather than a guess from a changelog |
| `jdeprscan --class-path ... ` | Required whenever the scanned classes reference anything outside the platform, or the tool fails with `error: cannot find class` for each one it cannot resolve |

The limitation that matters most is scope, not syntax. `jdeprscan` reports only uses of Java SE's own deprecated API, never a project's own deprecated members and never a third party's, verified both ways: a class calling a `@Deprecated` method declared in the same project produces no output at all even with a correct classpath, while a class calling `new Integer(3)` is reported by name.

| Question | Right tool |
|---|---|
| Will the platform's own deprecated or for-removal API break this code on the next upgrade | `jdeprscan`, with `--release` set to the target release |
| Is anyone on the team still calling something we ourselves deprecated | The compiler's `-Xlint:deprecation`, not `jdeprscan` |

`java.lang.Integer(int)` shows why a bare scan result needs the annotation checked, not trusted: on release 25 it is `@Deprecated(since="9")` with no `forRemoval`, so `jdeprscan --for-removal` correctly reports nothing, even though the identical scan reported `forRemoval=true` against releases 17 and 21. A removal commitment can be postponed indefinitely, and it can be withdrawn outright after being made. See [lesson 46](../lessons/0046-deprecation-that-works.md).

## Which document answers which question

Reaching for the wrong document wastes the most time once an argument needs a citation, because each one is organised for a different purpose and does not answer a question it was not written to settle.

| Question | Document | What it is uniquely good for |
|---|---|---|
| What does the language mean: overload resolution, generics, exhaustiveness | The Java Language Specification | The rules the compiler actually applies, stated as rules rather than examples |
| What is a descriptor, how does linking work, what does a class file contain | The Java Virtual Machine Specification | The level below the language, where `NoSuchMethodError` or `AbstractMethodError` actually comes from |
| What does this method promise | The API documentation | A contract that binds even when no specification mentions the method at all |
| Why does a feature exist, what was it arguing against | The JEP that introduced it, via the JEP index | The intent and rejected alternatives, which no other document records |
| Which releases are still maintained | The Oracle Java SE Support Roadmap | A schedule, the only one of these that goes stale on its own |

A question about whether a change breaks callers splits along this line: the Java Language Specification for the source-compatible half, the Java Virtual Machine Specification for the binary-compatible half, the split lesson 43 built its argument on without naming the two documents behind it. See [lesson 47](../lessons/0047-settling-it-from-the-source.md).

## Specification navigation

The specification is organised by construct, not by task, so the working move is translating a question into the construct it is really about before opening anything.

| Chapter | Covers | Worth opening for |
|---|---|---|
| JLS chapter 8, Classes | Class declarations, sealed `permits`, `final` methods, constructor overload resolution | Whether a change to an ordinary or sealed class is safe |
| JLS chapter 13, Binary Compatibility | What a compiled class file is entitled to assume about everything around it | The specification's own account of source against binary compatibility |
| JLS chapter 14, Blocks, Statements and Patterns | `switch` exhaustiveness, section 14.11.1.1 | Why an exhaustive switch is a compile-time proof about the hierarchy as it stood then, not a permanent guarantee |
| JLS chapter 15, Expressions | Evaluation order (15.7), overload resolution (15.12.2) | Whether precedence and evaluation order really are the same question, and how a call between overloads is actually decided |
| JLS chapter 17, Threads and Locks | The memory model | Where stage 4 already sent you for `synchronized` and `volatile`; not new territory in this stage |

See [lesson 47](../lessons/0047-settling-it-from-the-source.md) and [lesson 45](../lessons/0045-evolving-a-type.md).

## Reading a JEP

A specification states what is true; a JEP states why someone decided it should be true and which alternatives were rejected, the one thing no specification ever records. The trap is that a JEP describes the release it shipped in and is never revised, even when a later JEP changes the very behaviour its own prose describes.

| What the header table tells you | What it does not tell you |
|---|---|
| Status and target release, how to tell a delivered feature from a withdrawn proposal at a glance | Whether a sibling JEP has since overtaken a specific claim buried in the prose beneath it |
| A "Relates to" line naming a cross-linked JEP, added as bookkeeping after the fact | Whether that cross-link is a correction; it lives in the metadata, not the body, so a reader of the prose alone gets no signal anything changed |

JEP 444, Virtual Threads, delivered in Java 21, still states that a `synchronized` block pins a virtual thread's carrier, and only speculates that a later release "may" remove it. JEP 491, delivered in Java 24, is that release: running a virtual thread that blocks inside `synchronized` with pinning diagnostics on produces no pinning trace at all. The rule: read a JEP for intent and the rejected alternatives, since nothing else records either, and confirm current behaviour by running the code, since a JEP is a historical record of an argument, not a reference manual that keeps itself current. See [lesson 47](../lessons/0047-settling-it-from-the-source.md).

## Review checklist

A review comment that works names a cost, who pays it, and what the alternative is; "this feels wrong" is a mood, not a defect, because the author cannot investigate a feeling.

| Construct | Right tool when | The cost to name when it is wrong |
|---|---|---|
| `extends` | The "is-a" relationship is real in the domain, the author controls every subclass, or it is sealed, or a skeletal implementation the interface's own author also writes | Coupling to an undocumented detail of the superclass (the fragile base class problem); a hierarchy commits every future subclass to the same shape |
| Checked exception | A reasonable caller of this exact method has a real next step: retry, fall back, ask for different input | Ceremony propagated up the call stack with no differing response anywhere; breaks any functional interface, such as `Function`, that declared no exception to receive it |
| Stream chain | One source, a short run of stateless intermediate operations, one terminal operation, nothing ambiguous | Undebuggable step-through; a side effect a short-circuiting operation such as `limit` can silently skip; a collector such as `toMap` throwing with a trace naming its own internals, not the data; a loop's structure hidden behind `peek` |

Two catches beyond the three named cases, brief because each is a fact a lesson already established rather than a fresh judgment call.

| Look for | Lesson that already taught it |
|---|---|
| An `equals` and `hashCode` pair not overridden together, or one that breaks symmetry or transitivity | 3 |
| `Optional` used as a field, a constructor parameter, or a method parameter | 16 |
| A mutable collection handed back from an accessor with no defensive copy | 14 |
| A shared mutable field read or written from more than one thread with no `synchronized`, `volatile`, or higher-level guarantee | 23, 24 |
| A public signature that is hard to change later for the reasons a binary or source compatibility break makes true | 43 |

When a diff is correct and the design underneath it is the real issue, say so in two separated comments: approve what is correct and can go in now, then open the design conversation separately, addressed to the code rather than the author, so a shippable change is never held hostage to a larger conversation it did not create. See [lesson 48](../lessons/0048-reviewing-java.md).

## The dependency and framework rubric

An ordered list, meant to be asked in this order, because an early "no" usually closes the case before the later questions matter.

1. **What problem does this solve that the service actually has right now, without a hypothetical?** A requirement nobody has yet, a scale not reached, or a backend that might get swapped one day is speculative generality, not a present need.
2. **What is the smallest thing that would work, and what specifically does it fail to do?** The exact gap, not a feeling of robustness, decides whether closing it by hand is cheaper than the framework and its costs.
3. **How much of the organisation's limited appetite for novelty does this spend, and what else was it earmarked for?** Spending it on what makes the product different is usually a good trade; spending it on plumbing every competitor already buys is usually not.
4. **What does the transitive graph actually contain, once it has been read rather than guessed?** A dependency-tree command answers this in minutes, before anyone has an opinion about the framework itself.
5. **What would it cost to remove this today, before it has had time to spread?** The cheapest estimate of the exit cost is available now; it only grows from here.
6. **What would have to be true to change the decision?** If nothing would, this is a commitment wearing the shape of an engineering decision, not an actual one.

For a framework already in place, sunk cost, the years already spent, is irrelevant going forward, since none of it can be spent again; migration cost, what leaving now would take, is the opposite of sunk and has to be priced against the cost of continuing, not against never having adopted it. A decision recorded with its constraint and its reversing fact can be revisited when the constraint changes; one recorded only as a preference cannot be checked against anything. See [lesson 49](../lessons/0049-does-this-framework-earn-its-place.md).

## Symptom to cause

| Symptom | What it actually means |
|---|---|
| `NoSuchMethodError` naming a method that "should" exist | The caller's bytecode wants a descriptor the new version no longer has, usually from a changed return or parameter type |
| `AbstractMethodError` partway through a program that otherwise ran fine | An interface method the caller's compiled class never got a body for: a default was removed, or turned abstract, after that class was compiled |
| `MatchException` on a `switch` that was proven exhaustive | The proof was true of the hierarchy at compile time; a constant or permitted subtype added since has reached an unrecompiled switch |
| `IncompatibleClassChangeError` naming a permitted subclass check | A sealed type's `permits` list was narrowed, and the class loader refused to load a class no longer on it |
| A constant's old value keeps printing after a new jar shipped | It was a compile-time constant, inlined at the caller's own compile time; no field access is left in its bytecode to answer a change |
| A record's fields read back in the wrong places, with no error anywhere | Components were reordered; the descriptor is unchanged, so nothing catches it and the data is simply wrong |
| An unchanged `null` call site suddenly fails to compile as "ambiguous" | A new overload was added with a parameter type unrelated to an existing one, rather than a supertype of it |
| `jdeprscan` reports nothing for a method your own team calls that you know is deprecated | It only reports Java SE's own deprecated API by default; use `-Xlint:deprecation` for your own or a dependency's members |
| `jdeprscan --for-removal` reports nothing for a call everyone assumes is scheduled for removal | The annotation genuinely carries no `forRemoval` element on the release scanned, and that element can be added or later withdrawn |
| A JEP's prose describes behaviour the current release does not have | JEPs are never revised after they ship; check for a later JEP on the same behaviour and confirm by running the code |
| A review comment gets relitigated every time it is raised | It named a feeling rather than a cost, a payer and an alternative |
| A framework decision cannot be revisited when the situation changes | It was recorded as a preference, not tied to a constraint and a fact that would reverse it |

See [lesson 43](../lessons/0043-what-counts-as-breaking.md), [lesson 45](../lessons/0045-evolving-a-type.md), [lesson 46](../lessons/0046-deprecation-that-works.md), [lesson 47](../lessons/0047-settling-it-from-the-source.md), [lesson 48](../lessons/0048-reviewing-java.md) and [lesson 49](../lessons/0049-does-this-framework-earn-its-place.md).

## Sources

- [Kinds of Compatibility, OpenJDK Compatibility and Specification Review](https://wiki.openjdk.org/display/csr/Kinds+of+Compatibility)
- [The Java Language Specification, Java SE 25, chapter 13, Binary Compatibility](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html)
- [The Java Language Specification, Java SE 25, chapter 15, Expressions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html)
- [The Java Language Specification, Java SE 25, chapter 8, Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html)
- [The Java Language Specification, Java SE 25, index](https://docs.oracle.com/javase/specs/jls/se25/html/index.html)
- [JEP 277, Enhanced Deprecation](https://openjdk.org/jeps/277)
- [The jdeprscan Command, Release 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jdeprscan.html)
- [The javap Command, Release 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javap.html)
- [JEP 0, the JEP Index](https://openjdk.org/jeps/0)
- [JEP 444, Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 491, Synchronize Virtual Threads without Pinning](https://openjdk.org/jeps/491)
- [Effective Java, Joshua Bloch](https://openlibrary.org/isbn/9780134685991)
- [Choose Boring Technology, Dan McKinley](https://boringtechnology.club/)
- [Yagni, Martin Fowler](https://martinfowler.com/bliki/Yagni.html)
- [Oracle Java SE Support Roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)
