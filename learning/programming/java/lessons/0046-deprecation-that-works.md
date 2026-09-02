---
title: 46. Deprecation That Works
description: Marking something deprecated changes nothing unless you say what happens next
type: lesson
---

# Lesson 46. Deprecation That Works

**Mission link:** Owning a Java service in production means you will eventually have to take something away, and deprecation is the only mechanism that lets you do that without breaking someone who had no warning.
**Primary source:** [JEP 277, Enhanced Deprecation](https://openjdk.org/jeps/277)
**Prerequisites:** [Lesson 45](0045-evolving-a-type.md), [Lesson 43](0043-what-counts-as-breaking.md)

## Warm-up

Lesson 45 showed that turning an interface's default method into an abstract one breaks every already-compiled implementor with an `AbstractMethodError`, thrown the moment that implementor's code actually calls the now-abstract method. If you know a method has to go, and you know that error is what waits at the end of the road for anyone who does not keep up, what has to happen between deciding "this has to go" and actually removing it, so that error never lands on code someone had every reason to trust?

<details markdown="1"><summary>Check</summary>

Everyone who might call it needs to be told, given time to move off it, and checked on before it is actually removed. That sequence, announce, wait, verify, remove, is what this lesson means by deprecation. An annotation on its own only does the first part, and only if someone reads it.

</details>

## Know this

### What the annotation actually does

Take a class with two deprecated members, one marked the plain way and one marked for removal:

```java
@Deprecated
public static void soft() { }

@Deprecated(since = "2.0", forRemoval = true)
public static void hard() { }
```

A caller that uses both, compiled with no flags at all, produces this:

```text
Caller.java:5: warning: [removal] hard() in Api has been deprecated and marked for removal
        Api.hard();
           ^
Note: Caller.java uses or overrides a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
1 warning
```

Read that carefully. `hard()` gets a named, specific warning, in its own `[removal]` category, with no flag required to see it. `soft()` gets nothing of its own at all. It is folded into the generic `Note: Caller.java uses or overrides a deprecated API`, which does not name the method, does not name the line, and would say exactly the same thing if there were ten plainly-deprecated calls in the file instead of one. Only asking for more detail changes that:

```text
Caller.java:4: warning: [deprecation] soft() in Api has been deprecated
        Api.soft();
           ^
Caller.java:5: warning: [removal] hard() in Api has been deprecated and marked for removal
        Api.hard();
           ^
2 warnings
```

With `-Xlint:deprecation`, both calls get a named warning, but they still land in two different categories, `[deprecation]` and `[removal]`, and the JEP that introduced this split gives them working names for the difference: an "ordinary deprecation" is a recommendation to migrate away with no promise attached, a "terminal deprecation" is a stated intent to remove the member in a future release. That difference in default visibility is not decoration on top of a shared meaning. It is the entire actionable content of JEP 277. Before it existed, `@Deprecated` meant one thing regardless of intent, and the JEP's own account of the problem this caused is blunt: "Everybody was confused about what deprecation actually meant, and nobody took it seriously. This in turn has made it difficult ever to remove anything from the Java SE API." `forRemoval` is not a stronger adjective bolted onto the same annotation. It is a second, distinct signal, with its own default warning behaviour, added specifically because the first signal alone had stopped meaning anything.

The two categories stay separate on the way back out, too, which matters the day you have a deliberate reason to keep calling something. `@SuppressWarnings("deprecation")` silences the ordinary kind and `@SuppressWarnings("removal")` silences the terminal kind, and neither key silences the other: the strings match the `-Xlint` category names, not the annotation. So suppressing the noise from a migration you have already scheduled does not also blind you to a member that has just been marked for removal. Reach for either only with a comment saying why, because a suppression with no reason is how a terminal deprecation gets to the removal release unnoticed.

### The three parts of a usable deprecation

The annotation is one part of a usable deprecation, not the whole of it. A deprecation that actually helps the people depending on the code needs all three:

- **The annotation itself**, with `since` recording the release the deprecation started in, and `forRemoval = true` only when removal is genuinely intended, never by habit and never left as the default because nobody thought about it.
- **A Javadoc `@deprecated` tag that names the replacement.** A warning that only says "this is deprecated" tells a caller there is a problem without telling them how to fix it, which turns one warning into an investigation. JEP 277 itself treats the annotation and the tag as a pair that should always travel together, going as far as giving `javac` a lint flag, `-Xlint:dep-ann`, specifically to catch a `@deprecated` tag that showed up without the matching annotation.
- **A stated removal release.** "Deprecated" with no date attached is not a step on the way to removal, it is a resting state, and the platform's own record, below, shows exactly how comfortable Java has become resting there.

Skip any one of the three and the deprecation stops doing useful work. Skip the annotation and tooling cannot find it. Skip the Javadoc tag and a caller who wants to comply has nowhere to go. Skip the date and "deprecated" just means "still here, indefinitely".

### What the platform's own record looks like

`jdeprscan --list --release N` prints the full set of APIs Java SE itself considers deprecated as of release `N`. Across the four most recent long-term-support releases:

| Release | Deprecated items | Of those, for removal |
|---|---|---|
| 11 | 583 | 25 |
| 17 | 656 | 76 |
| 21 | 679 | 103 |
| 25 | 720 | 132 |

Two things are worth reading off that table before moving on. The total only ever climbs, from 583 to 720 across four releases, and essentially nothing that was already deprecated by release 11 has actually gone away by release 25, which is the platform's own proof that deprecating something and removing it are two separate decisions with two separate timelines, not one event with a delay attached. But look at the second column, and a different story appears: the for-removal count grew from 25 to 132, more than five times over, considerably faster than the total did. As a share of everything deprecated, that is a rise from about four per cent to about eighteen per cent. So the platform is still only willing to commit to removing a small minority of what it deprecates, but it has become far more willing to make that commitment than it used to be, and that shift in willingness is the real story the raw growth in the total, taken alone, would hide.

One more shape is worth naming, because it explains where most of that pile comes from. Of the 720 deprecated items in release 25, 135 carry `since="9"`, the release that shipped the module system and reorganised large parts of the platform's internals. Everything else trails off in a long, thin tail after that one release, with 26 more arriving in release 25 itself. Most of what looks like a permanent backlog is really one historical event, with a slow drip since.

### The example that corrects the assumption

Here is where the assumption that "deprecated eventually means removed" runs straight into the platform's own most visible counterexample. `java.lang.Integer(int)`, the boxing constructor behind `new Integer(3)`, and its sibling constructors on the other boxed primitive types, were all marked `@Deprecated` in release 9, in 2017, explicitly without `forRemoval`. Checking the constructor directly in the class file confirms it, straight from the annotation the compiler actually reads:

```text
  public java.lang.Integer(int);
    ...
    Deprecated: true
    RuntimeVisibleAnnotations:
      0: #357(#358=s#359)
        java.lang.Deprecated(
          since="9"
        )
```

No `forRemoval` element at all. Scanning code that calls `new Integer(3)` with `jdeprscan --for-removal` therefore reports nothing, which looks broken the first time you see it, until you remember what the annotation actually says. Deprecated since Java 9, nine years ago as of this release, and still not scheduled for removal. If the platform will not commit to a removal date for its single most famous deprecation across nearly a decade, an application's own "deprecated" with no date attached is not going anywhere either, and pretending otherwise is wishful thinking dressed up as an annotation.

The story has one more turn worth knowing, because it undercuts the assumption from the opposite direction too. `jdeprscan --list` against the deprecation sets bundled for releases 17 and 21 both report `java.lang.Integer(int)` as `@Deprecated(since="9", forRemoval=true)`, a real, formal commitment to remove it. By release 25 that commitment is gone, back to plain `@Deprecated(since="9")`, exactly matching the class file quoted above. Somewhere between 21 and 25, the platform did not just fail to act on a removal promise, it withdrew one it had already made. Deprecation is not only slower than people assume. A stated intent to remove something is not irreversible either, which is one more reason a bare annotation with no accompanying process is not a schedule anyone can plan around, even when it briefly looks like one.

### Using jdeprscan

`jdeprscan` takes a directory of class files, a jar, or a class name, so `jdeprscan target/classes` and `jdeprscan legacy.jar` are both valid, and so is naming a single class such as `jdeprscan Legacy`. Point it at a class that calls `new Integer(3)` and it reports:

```text
class Legacy uses deprecated method java/lang/Integer::<init>(I)V
```

Two things are worth knowing before reaching for this tool on real code. First, if the class you scan depends on classes that are not on the boot classpath, you need `--class-path` pointed at wherever those dependencies live, typically the same classpath the application itself runs with, or `jdeprscan` prints `error: cannot find class ...` for each one it cannot resolve rather than a clean report. Second, and more important, `jdeprscan` is scoped on purpose, and the scope is narrower than "deprecated". JEP 277 says it plainly: "By default, the deprecated APIs will be the deprecations from Java SE itself." Scanning a class that calls a `@Deprecated` method from your own library, or from a third-party dependency, produces no report at all, even with a perfectly correct classpath, because the tool is only checking usage against Java SE's own list, not against whatever your own codebase happens to have marked. `jdeprscan` answers "is this code still leaning on platform APIs that are on their way out". It does not answer "did anyone on my team ignore a deprecation warning last quarter", and reaching for it expecting that second answer is the trap, not any particular combination of command-line flags.

The form that earns this tool its place in a real upgrade is `--release N`, which scans against another release's deprecation set instead of the one the tool itself ships with. `jdeprscan --release 21 target/classes` tells you, before you touch a single line, whether anything your service already calls was on release 21's deprecated list, its for-removal list, or neither, which is the direct answer to "will this code survive the upgrade" rather than a guess based on a changelog.

### Running a deprecation as a library author

Put the three parts together and a deprecation you own becomes a short, bounded project rather than an open-ended annotation. Announce it with the replacement named and a removal release attached, in both the annotation and the Javadoc. Keep the old path working exactly as it did, because a deprecation that already behaves differently is a breaking change wearing a warning label, not a deprecation. Give callers a way to find out whether they are still exposed, whether that is `jdeprscan` against your own release notes, a search across your own call sites, or usage telemetry if the API is public enough that you cannot see every caller directly. Then remove it on the release you named, not earlier and, just as importantly, not quietly later either, because a removal date that slips without comment teaches everyone watching that your dates do not mean anything, which is the exact failure mode this whole lesson is about avoiding. If a change to a public method's binary signature is part of that removal, lesson 43's distinction between source and binary compatibility is exactly what tells you whether recompiling is enough for your callers or whether their existing binaries will fail outright, and a tool such as `japicmp-maven-plugin` can fail your own build automatically the moment a change crosses that line, which is worth knowing exists even though wiring it up is its own separate task.

The reader-facing half of this is simpler and belongs on the other side of the same warning. When a deprecation warning appears in code you maintain, the first thing to check is not the annotation, it is the Javadoc: does it name a replacement. If it does, the work is scoped and mechanical, however tedious. If a removal release is attached and it is close, treat that the way you would treat any other deadline with an external owner, because the platform's own record above shows plenty of deprecations that stayed put for a decade, but it also shows 132 that did not, and you do not get to choose in advance which kind yours is. If there is no removal release at all, note it, fix it when it is convenient, and stop worrying that it is about to break under you, because a Java SE deprecation with no removal attached has, so far, meant exactly that: noted, not urgent, possibly permanent.

## Practice

1. ▢ A method is annotated `@Deprecated(since = "3.0")` with no `forRemoval` element written at all. A caller in another file calls it, and the project is compiled with no extra flags. Predict what appears in the build output, and name the single default value that decides it.

<details markdown="1"><summary>Check</summary>

Nothing specific to that call appears. The build produces the same generic pair of `Note:` lines this lesson's own example produced for `soft()`, naming neither the method nor the line, because `forRemoval` defaults to `false` when it is left out entirely. Only `forRemoval = true` produces a warning that is loud, named, and visible by default; leaving it out, deliberately or by habit, is indistinguishable to the compiler from writing it as `false`.

</details>

2. ▢ A teammate runs `jdeprscan --for-removal` over a service's compiled classes, gets no output, and tells the team "we have no removal risk from the boxing constructors we still call." Predict whether that conclusion is safe, given only what `new Integer(3)` scans as under the release currently in use.

<details markdown="1"><summary>Hint</summary>

Check what the same constructor scanned as under `--release 17` or `--release 21`, and ask what changed between then and now.

</details>

<details markdown="1"><summary>Check</summary>

It is safe for right now, since `java.lang.Integer(int)` on this release genuinely carries no `forRemoval` element, confirmed directly in the class file's own annotation. But "no removal risk" overstates it, because that same constructor scanned as `forRemoval=true` against the deprecation sets for releases 17 and 21, a formal removal commitment the platform later withdrew. "No output today" only means "not scheduled as of this scan", not "will never be scheduled", and the honest version of the teammate's claim needs that qualifier attached.

</details>

3. ▢ Looking only at the raw totals in the platform's deprecation table, 583 rising to 720 across four releases, predict what conclusion that column alone would support, and say what the for-removal column adds that changes it.

<details markdown="1"><summary>Check</summary>

The raw totals alone support "deprecation only ever accumulates, so it effectively means nothing ever really leaves", and taken in isolation that is a fair reading. The for-removal column complicates it: the count of items actually committed to removal grew from 25 to 132, more than five times over, considerably faster than the total did, even though it still covers only about eighteen per cent of everything deprecated by release 25. The platform has become substantially more willing to promise removal for something it deprecates, without yet promising it for most of the list.

</details>

4. ▢ You deprecate a method with `@Deprecated(since = "2.0", forRemoval = true)` and nothing else, no Javadoc changes at all. Predict what a caller who reads only the compiler's warning can and cannot do next, and name the one missing piece that would fix it.

<details markdown="1"><summary>Check</summary>

The caller can tell the method is going away and roughly when the clock started, since `since` and the `[removal]` category are both visible in the warning itself. They cannot tell what to call instead, because the compiler's warning names the deprecated member, never a replacement. The missing piece is the Javadoc `@deprecated` tag naming what to use, and without it the warning turns into an investigation rather than a fix, exactly the same shape of failure as a deprecation with no removal date, just aimed at a different one of the three required parts.

</details>

5. ▢ A team plans to move a service from release 21 to release 25 next quarter, and wants to know before starting whether that move will expose any new for-removal risk. Predict which `jdeprscan` invocation answers that, and say what changes about the answer if it is run against the built jar instead of against the source tree.

<details markdown="1"><summary>Check</summary>

`jdeprscan --for-removal --release 25` run against the compiled classes or jar answers it, because `--release` scans against another release's deprecation set rather than reporting what is deprecated in the abstract, which is exactly "will this code survive the upgrade" rather than a guess from a changelog. Running it against the built jar rather than the source tree matters because `jdeprscan` reads class files, not source text, so scanning the jar catches deprecated calls sitting inside anything bundled or shaded into that artefact, including a dependency's own code, which scanning only the team's own source tree would miss entirely.

</details>

## Real-world reps

- [ ] Pick one `@Deprecated` annotation in a project you maintain, or in a dependency whose source you can read, and check whether it has all three parts: the annotation with `since`, a Javadoc tag naming a replacement, and a stated removal release.
- [ ] Run `jdeprscan` against a build you own, read whether it reports anything at all, and work out for yourself why the tool's own default scope makes a clean report a weak signal about your own team's deprecated methods specifically.
- [ ] Find one place in a codebase you touch where something has stayed "deprecated" with no removal date longer than anyone remembers, and decide what removal-release commitment you would attach today if it were your call.
- [ ] Deprecate one real method properly: add `since`, set `forRemoval` deliberately rather than by habit, write the `@deprecated` Javadoc tag naming the replacement, and open the follow-up ticket that names the release it goes away in.
- [ ] Tomorrow: recompile a project you own with `-Xlint:deprecation` and read every warning it surfaces that a plain build had been quietly folding into a single unnamed note.

## Going further

- [The jdeprscan Command, Release 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jdeprscan.html): the tool's manual, including the third-party scope limit quoted in this lesson
- [The javap Command, Release 25](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javap.html): how to read a class file's own annotations directly, the way this lesson checked `Integer(int)` against the assumption
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
