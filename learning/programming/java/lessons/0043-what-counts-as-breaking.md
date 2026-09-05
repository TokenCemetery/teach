---
title: 43. What Counts as Breaking
description: Three kinds of compatibility, and the change that is safe to compile against and fatal to run against
type: lesson
---

# Lesson 43. What Counts as Breaking

**Mission link:** Owning a Java service in production means other people's already-compiled code keeps running against yours long after you shipped it, and "did I break anything" turns out to be three separate questions with three separate tests, not one vague worry.
**Primary source:** [Kinds of Compatibility, OpenJDK Compatibility and Specification Review](https://wiki.openjdk.org/display/csr/Kinds+of+Compatibility)
**Prerequisites:** [Lesson 42](0042-from-profile-to-proof.md), [Lesson 33](0033-declaring-dependencies.md)

## Warm-up

Lesson 33 showed that bumping a dependency's version is one line in a `pom.xml`, and that mediation then decides which jar actually lands on the classpath, sometimes without anyone directly choosing it. Suppose that one-line bump leaves your own project compiling cleanly, no errors and no warnings. Does that clean recompile tell you that code already running in production, compiled last month against the old jar and never touched since, is safe to keep running unchanged once the new jar is deployed underneath it?

<details markdown="1"><summary>Check</summary>

No. A clean recompile answers exactly one question: does your source still compile against the new version. It says nothing about whether a `.class` file compiled last month, sitting untouched on a server, will still link and run against the new jar without being recompiled, and it says nothing about whether the answer that code computes is still the same answer it used to compute. Those are two further, independent questions, and this lesson gives each of the three its own name and its own test.

</details>

## Know this

### Three questions, not one

"Breaking" is usually said as though it names a single property a change either has or does not have. It names three, and each one has its own test, checked in a different way by a different tool.

- **Source compatibility.** Does code that used to compile against the old version still compile, unchanged, against the new one. The test is a recompile: take the caller's `.java` files exactly as they are, point the compiler at the new version, and see whether it succeeds.
- **Binary compatibility.** Does code that was already compiled against the old version still link and run against the new one, with no recompilation at all. The test is to leave the caller's `.class` files exactly as they are and run them against the new jar, changing nothing on the caller's side.
- **Behavioural compatibility.** Does code that compiles and links successfully, whether freshly recompiled or already compiled, still do the same thing it did before. The test is to run it and compare what comes out, which makes this the one of the three that depends on what the code is actually for rather than on anything a compiler or a class loader can check for you mechanically.

These are three independent facts about the same change, not three names for the same fact. A single change to a single class can be any combination of the three, true or false in either direction, and knowing that one of them holds tells you nothing about the other two. The assumption this lesson exists to remove is the one that treats source compatibility, the thing your own build already checks on every commit, as if it implied the other two. It does not, and the fastest way to see why is to watch one small change produce three different verdicts at once.

### One library, two versions, three outcomes

Here is a library with three public members, version 1:

```java
package lib;
import java.util.List;
public class Config {
    public static final int MAX = 10;
    public static String name() { return "v1"; }
    public static List<String> items() { return List.of("a"); }
}
```

Version 2 changes all three members at once: the constant's value, the string the method returns, and the return type of the third method, narrowed from `List` to `ArrayList`:

```java
package lib;
import java.util.ArrayList;
public class Config {
    public static final int MAX = 20;
    public static String name() { return "v2"; }
    public static ArrayList<String> items() { ArrayList<String> l = new ArrayList<>(); l.add("a"); return l; }
}
```

An application compiled once, against version 1, reads all three:

```java
import lib.Config;
import java.util.List;
public class App {
    public static void main(String[] args) {
        System.out.println("MAX      = " + Config.MAX);
        System.out.println("name()   = " + Config.name());
        List<String> items = Config.items();
        System.out.println("items()  = " + items);
    }
}
```

Compiled against version 1 and run against version 1, it prints exactly what you would expect: `MAX      = 10`, `name()   = v1`, `items()  = [a]`, verified by running it. Now take those exact `.class` files, the ones the compiler produced against version 1, and point the same run at version 2's jar instead, recompiling nothing at all. This is the whole experiment, and the output is worth reading slowly, verified by running it:

```text
MAX      = 10
name()   = v2
Exception in thread "main" java.lang.NoSuchMethodError: 'java.util.List lib.Config.items()'
	at App.main(App.java:7)
```

Three changes, made at the same time, to the same class, and three different results. `MAX` still reports the old value, ten, even though the new jar on the classpath defines it as twenty. `name()` reports the new value, `v2`, immediately, with no recompilation at all. `items()` does not report anything: the program crashes before it gets there, with an error naming a method that, as far as the loaded classes are concerned, no longer exists. Each of those three outcomes is a different one of the compatibilities from the previous section, and each is worth taking apart on its own.

![Three rows. For MAX the class file holds the literal ten and nothing crosses to version 2, which still defines twenty. For name the call crosses and finds a match. For items the call crosses and is stopped, because version 2 provides a different return type.](images/three-members-three-answers.svg)

The `MAX` row has an empty gap on purpose: nothing crosses, because nothing is looked up. The other two rows both cross, and only the descriptor decides whether what they find counts as the same method.

### The constant that was never a read

`MAX` reporting ten is not a stale cache and not a delayed update. It is the compiler, back when `App.java` was compiled against version 1, deciding there was nothing left to look up at run time. Disassembling the application's class file confirms it directly:

```text
$ javap -c -p App.class
Compiled from "App.java"
public class App {
  public App();
    Code:
       0: aload_0
       1: invokespecial #1    // Method java/lang/Object."<init>":()V
       4: return

  public static void main(java.lang.String[]);
    Code:
       0: getstatic     #7    // Field java/lang/System.out:Ljava/io/PrintStream;
       3: ldc           #15   // String MAX      = 10
       5: invokevirtual #17   // Method java/io/PrintStream.println:(Ljava/lang/String;)V
       8: getstatic     #7    // Field java/lang/System.out:Ljava/io/PrintStream;
      11: invokestatic  #23   // Method lib/Config.name:()Ljava/lang/String;
      14: invokedynamic #27,0 // InvokeDynamic #0:makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;
      19: invokevirtual #17   // Method java/io/PrintStream.println:(Ljava/lang/String;)V
      22: invokestatic  #31   // Method lib/Config.items:()Ljava/util/List;
      25: astore_1
      26: getstatic     #7    // Field java/lang/System.out:Ljava/io/PrintStream;
      29: aload_1
      30: invokestatic  #35   // Method java/lang/String.valueOf:(Ljava/lang/Object;)Ljava/lang/String;
      33: invokedynamic #41,0 // InvokeDynamic #1:makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;
      38: invokevirtual #17   // Method java/io/PrintStream.println:(Ljava/lang/String;)V
      41: return
}
```

That `ldc #15` is the entire cost of the line `System.out.println("MAX      = " + Config.MAX);`. There is no `getstatic` fetching `lib.Config.MAX`, because there is no field access left in the bytecode at all: the compiler evaluated `"MAX      = " + Config.MAX` itself, at compile time, and wrote the finished string, `MAX      = 10`, straight into the constant pool as a single literal. `ldc` loads that literal. Nothing about running the program against a different `Config` class can change what that instruction loads, because the instruction never mentions `Config` in the first place. Compare that to line 11, `invokestatic #23 // Method lib/Config.name:()Ljava/lang/String;`: that one really is a call, resolved by name and descriptor against whatever `Config` happens to be on the classpath at run time, which is exactly why `name()` reported the new value with no recompilation at all.

This happens because `MAX` is a **compile-time constant** in the sense the language specification gives that phrase: a `static final` field of a primitive type or `String`, initialised with an expression the compiler can evaluate on the spot. Every one of those is a candidate for inlining, and `javac` takes the candidacy every time. The consequence for anyone publishing a library is a hard one: a `public static final` primitive or `String` field is not really a value your class hands out at run time, it is a value your callers' compilers copy into their own class files the moment they compile against you, and once it is copied it belongs to them, not to you. You can ship a new jar with a corrected value every day, and every caller who has not recompiled will go on reading the old one, silently and forever, because there is no read left anywhere in their bytecode for your new value to answer. If a value must ever be correctable after the fact, from your side, without waiting for every caller to rebuild, it cannot be a `public static final` primitive or `String`. It has to be exposed through an ordinary static method instead, a plain accessor with a body, `public static int max() { return MAX; }`, because an ordinary method call is not a constant expression and is never inlined: it is resolved at run time by name and descriptor against whichever class is actually on the classpath, which is exactly what let `name()` report `v2` with no recompilation at all.

### The descriptor is the method's real name

`items()` is the opposite failure, and the surprising part is which direction it fails in. Recompile the unchanged `App.java`, the same source, against version 2's `Config`, and it succeeds with no error at all, verified by running it: `List<String> items = Config.items();` still type-checks, because an `ArrayList<String>` is assignable to a variable of type `List<String>`, and nothing about that assignment cares which of the two types the method actually declares. By the source-compatibility test from the first section, narrowing the return type from `List` to `ArrayList` is a compatible change. Nobody who rebuilds notices anything happened.

Nobody who does not rebuild gets that lucky. Run the original, already-compiled `App.class` against the new jar, and it fails with the `NoSuchMethodError` shown above, and the error message is precise about why: it names `'java.util.List lib.Config.items()'`, the exact method the caller's bytecode is looking for. That string is not a decoration. Inside a class file, a method is not identified by its name alone: it is identified by its name together with its **descriptor**, a compact encoding of every parameter type and the return type, and `()Ljava/util/List;` is a different descriptor from `()Ljava/util/ArrayList;`. As far as the class file format is concerned, these are not the same method with a different return type. They are two unrelated methods that happen to share a name, and version 2 defines one of them while the caller's bytecode asks for the other, which simply is not there to be found. `javap` on the original `App.class` shows exactly what got baked in at compile time: `invokestatic #31 // Method lib/Config.items:()Ljava/util/List;`, a reference to a descriptor, not to a return type in any looser sense.

This is the pair most people find hardest to hold in their head at once, because it runs against the instinct that "compiles fine" and "runs fine" are the same fact checked at two different times. They are not. Narrowing a return type is source-compatible, because the compiler only ever checks whether the result can be used the way it is being used. It is binary-incompatible, because the class file only ever checks whether the exact descriptor it recorded still exists. A change can be perfectly safe for every caller who rebuilds and simultaneously fatal for every caller who does not, from the very same edit, and nothing about a green build tells you which of those two worlds you are shipping into.

### Deciding which one you actually need

None of this is a reason to test all three compatibilities on every change you ever make. It is a reason to ask one question before you ship, and the question is about your callers, not about your code: will everyone who calls this recompile against the new version before they run it, or could an already-compiled caller run against it unchanged?

If the answer is that everyone rebuilds together, because the code in question is a module inside one repository that is always built and released as a whole, then binary compatibility is not a real risk for that code: nobody's `.class` files sit around waiting to be run against a jar they were never compiled for, since a full rebuild retires every old class file before anything runs. Source compatibility and behavioural compatibility are still worth checking, because "does it still compile" and "does it still do the same thing" are both real questions inside a single repository too, but the third test, the one this lesson spent most of its time on, has nothing to bite on there.

If the answer is that you do not control when your callers rebuild, because the code is a published library, an internal artefact consumed by other teams' own release schedules, or anything else that reaches its users as a jar rather than as source someone recompiles alongside yours, then all three compatibilities are live, and binary compatibility is the dangerous one precisely because of where it fails: not in your own build, where a red build stops you before anything ships, but later, in someone else's production, the moment they upgrade a transitive dependency the way lesson 33 described and end up running old class files against your new jar without ever touching a line of their own source. That failure mode is the one worth designing against deliberately, because by the time you see it, if you ever see it at all, it is somebody else's incident.

This check can be mechanised rather than done by hand every time: `japicmp-maven-plugin`, at 0.26.1, and `revapi-maven-plugin`, at 0.15.1, both compare a built jar against a previous release and can fail the build outright when a binary-incompatible change slips in. Either is worth wiring into a published library's build once you know, from the question above, that binary compatibility is one of the things that library actually has to answer for.

## Practice

1. ▢ A further version of `Config` widens `items()` back the other way, from `ArrayList<String>` as in version 2 to `List<String>`, while every existing caller was compiled against version 2 and calls an `ArrayList`-only method on the result, such as `ensureCapacity`. Predict the source-compatibility and binary-compatibility verdicts for that caller.

<details markdown="1"><summary>Hint</summary>

The descriptor changed again, in the other direction this time, and the caller's own code now expects a type the new method no longer promises.

</details>

<details markdown="1"><summary>Check</summary>

Both fail. Binary compatibility fails for the same structural reason as the lesson's own example: `()Ljava/util/ArrayList;` is a different descriptor from `()Ljava/util/List;`, so an already-compiled caller still gets `NoSuchMethodError` naming the descriptor it was built against, regardless of which direction the change went. Source compatibility fails too this time, unlike the lesson's example, because recompiling the caller now hits a real compile error: `List` has no `ensureCapacity` method, so the line that called it no longer type-checks. Changing a return type is not binary-compatible in either direction, and whether it stays source-compatible depends entirely on what the caller does with the result.

</details>

2. ▢ Suppose `MAX` had been declared `public static int MAX = 10;`, with no `final`, everything else about the experiment unchanged. Predict what the second run, against version 2's jar with no recompilation, would print for that line.

<details markdown="1"><summary>Check</summary>

It would print `MAX      = 20`, the new value, immediately. Without `final`, the field is not a compile-time constant, so `javac` cannot fold it into a literal and has no choice but to compile a genuine `getstatic` instruction, resolved against whatever class is actually on the classpath at run time. Inlining is specific to `static final` primitives and `String` fields with a constant initialiser; remove either the `static`, the `final`, or the constant initialiser, and the field is read exactly the way an ordinary field is, with no caller ever frozen at compile time.

</details>

3. ▢ Version 3 of `Config` keeps every existing member exactly as version 1 had them, and adds a brand new method, `public static boolean ready() { return true; }`. Predict the source and binary compatibility verdicts for every caller that already exists, and say what, if anything, could make that prediction wrong.

<details markdown="1"><summary>Check</summary>

Both compatible, for every caller that exists today: nothing already compiled or already written refers to `ready()`, so there is no descriptor for anything to fail to find and no line of existing source that could stop compiling because of a method it never called. The one way this could go wrong is overload resolution: if some existing caller already has its own method or import that becomes ambiguous against the new `ready()` in a way the compiler cannot resolve, recompiling that specific caller could fail. That is a real edge case in a full overload-resolution rule set, but it does not touch any caller that never mentions the new name, which is every caller in this experiment.

</details>

4. ▢ Version 4 removes `name()` entirely, with `MAX` and `items()` left exactly as they were in version 1. Predict what happens to a caller's already-compiled `.class` files run against version 4, and separately what happens when that same caller's unchanged source is recompiled against version 4.

<details markdown="1"><summary>Check</summary>

Both fail, for the same underlying reason from two different angles. The already-compiled caller throws `NoSuchMethodError` naming `name()`'s descriptor the instant it reaches the call, exactly like `items()` in the lesson's own experiment, because linking looks for a name-and-descriptor pair that is no longer there. Recompiling the same unchanged source also fails, with a compile error such as "cannot find symbol", because the method the source calls by name genuinely does not exist in version 4 at all. Removing a member outright is the one kind of change that fails both tests at once, unlike narrowing a return type, which the lesson showed passes one and fails the other.

</details>

5. ▢ A two-person team owns a single Maven module, built and deployed as one artefact by one pipeline that always compiles every source file from a clean checkout before it runs anything. They are deciding whether to add `japicmp-maven-plugin` to that module's build. Predict whether that decision is well justified, and name the one fact about their callers that the decision actually turns on.

<details markdown="1"><summary>Check</summary>

Not well justified, on the facts given. `japicmp-maven-plugin` exists to catch binary-incompatible changes, and binary incompatibility only bites a caller whose already-compiled class files run against a new version without being recompiled first. A module that is always rebuilt from a clean checkout by its own pipeline has no such caller: every consumer of its own code is, by construction, the next full build, which recompiles everything. The fact the decision turns on is not the size of the team or the module, it is whether anything outside that one pipeline's control could ever run old class files against the new build, and nothing in the scenario says that it can.

</details>

## Real-world reps

- [ ] Pick a public class you maintain and list every `public static final` field on it whose type is a primitive or `String`; for each one, decide whether any caller outside your own build might be relying on a value you could later want to change.
- [ ] Run `javap -c` on one of your own compiled classes that reads a `public static final` constant defined in a different class, and check whether the instruction at that line is an `ldc` of a folded literal or a genuine field access.
- [ ] Find a published library your project depends on, look at its changelog between two versions you have both used, and classify one signature change from it as source-compatible, binary-compatible, both, or neither.
- [ ] Pick one public method you own whose return type could plausibly need to change one day, and work out whether any caller outside your own build could be running compiled class files against it without ever recompiling.
- [ ] Tomorrow: before you next bump a dependency's version in a `pom.xml`, ask out loud whether every one of that dependency's own callers recompiles against the new jar before running it, or whether some of them run already-compiled class files against it unchanged.

## Going further

- [The Java Language Specification, Java SE 25, chapter 13, Binary Compatibility](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html): the specification's own account of exactly what a compiled class file is entitled to assume about everything around it
- [The javap Command, Release 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javap.html): the tool used in this lesson to read what a compiler actually decided to write into a class file
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
