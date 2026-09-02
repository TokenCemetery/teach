---
title: 35. A Runnable Artifact
description: Packaging what you built so that someone with nothing but a JDK can run it
type: lesson
---

# Lesson 35. A Runnable Artifact

**Mission link:** Owning a Java service means someone else, a teammate, a deployment pipeline, or you on a different machine in six months, has to be able to get it running from nothing but the repository, and that is a property of the artifact, not of the test suite.
**Primary source:** [The jar Command, Oracle](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jar.html)
**Prerequisites:** [Lesson 34](0034-the-build-lifecycle.md), [Lesson 33](0033-declaring-dependencies.md)

## Warm-up

`mvn package` runs the default lifecycle up to and including the `package` phase. Which phases have already run by the time `package` starts, and what would have to be true for `package` to run at all?

<details markdown="1"><summary>Check</summary>

By the time `package` runs, `validate`, `compile` and `test` have already succeeded, along with the phases around them that generate and process sources and resources. For `package` to run at all, every test that Surefire executed in the `test` phase has to have passed, because a failing test stops the build before `package` is reached. That means `package`'s only job is to collect what `compile` already produced, the `.class` files under `target/classes`, into one distributable file. It does not compile anything and it does not run anything. This is the phase this lesson is about, and it does less than most people assume.

</details>

## Know this

### A jar is a zip with a manifest

Run `mvn package` on a small project, a single `Greeting` class with one dependency-free method, and look at what came out.

```text
target/greeting-1.0.jar: Zip archive data, at least v1.0 to extract, compression method=store
```

That is `file` talking about a `.jar`, and it is telling the truth: a jar is a zip archive, nothing more exotic. `unzip -l` on it shows the same thing a zip tool would show for any archive:

```text
Archive:  target/greeting-1.0.jar
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2026-01-01 00:00   META-INF/
      208  2026-01-01 00:00   META-INF/MANIFEST.MF
        0  2026-01-01 00:00   com/
        0  2026-01-01 00:00   com/example/
        0  2026-01-01 00:00   com/example/greeting/
        0  2026-01-01 00:00   META-INF/maven/
      782  2026-01-01 00:00   com/example/greeting/Greeting.class
     3900  2026-01-01 00:00   META-INF/maven/com.example/greeting/pom.xml
       45  2026-01-01 00:00   META-INF/maven/com.example/greeting/pom.properties
```

The one entry that makes a jar different from an arbitrary zip is `META-INF/MANIFEST.MF`, a small text file of key-value pairs that the `jar` command and the `java` launcher both read. Maven writes one automatically, and by default it says almost nothing:

```text
Manifest-Version: 1.0
Created-By: Maven JAR Plugin 3.5.0
Java-Version: 25
Build-Jdk-Spec: 25
```

No mention of which class to run. That absence is the whole story of the next section.

### A plain jar will not run itself

Try running the jar you just built, the ordinary way:

```text
$ java -jar target/greeting-1.0.jar Ada
no main manifest attribute, in target/greeting-1.0.jar
```

The `java` launcher opened the archive, found the manifest, looked for a `Main-Class` attribute to know where to start, and found nothing. `mvn package` finished with `BUILD SUCCESS`, every test passed, and the thing it produced still cannot be run. This is not a bug in Maven, it is the default: the `maven-jar-plugin` packages what compiled and stops there, because it has no way to guess which class, if any, is meant to be an entry point.

The fix is to tell the plugin explicitly, by configuring its `archive` element:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-jar-plugin</artifactId>
  <version>3.5.1</version>
  <configuration>
    <archive>
      <manifest>
        <mainClass>com.example.greeting.Greeting</mainClass>
      </manifest>
    </archive>
  </configuration>
</plugin>
```

Rebuild, and the manifest now carries the attribute the launcher was looking for:

```text
Manifest-Version: 1.0
Created-By: Maven JAR Plugin 3.5.1
Java-Version: 25
Build-Jdk-Spec: 25
Main-Class: com.example.greeting.Greeting
```

```text
$ java -jar target/greeting-1.0.jar Ada
Hello, Ada!
```

That is the fix, and for a project with no dependencies beyond the JDK itself, that is the whole lesson. Almost nothing you will ship has no dependencies beyond the JDK.

### The dependency cliff

Add one dependency, [Lesson 33](0033-declaring-dependencies.md)'s subject, and have `Greeting` actually use it:

```java
package com.example.greeting;

import org.apache.commons.lang3.StringUtils;

public class Greeting {

    public String greet(String name) {
        return "Hello, " + StringUtils.capitalize(name) + "!";
    }

    public static void main(String[] args) {
        String name = args.length > 0 ? args[0] : "world";
        System.out.println(new Greeting().greet(name));
    }
}
```

```xml
<dependency>
  <groupId>org.apache.commons</groupId>
  <artifactId>commons-lang3</artifactId>
  <version>3.20.0</version>
</dependency>
```

Run the build. It succeeds, and the test suite passes:

```text
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.031 s -- in com.example.greeting.GreetingTest
[INFO] BUILD SUCCESS
```

A green build, on a project that now depends on a library. Run the artifact it just produced, the same command that worked a moment ago:

```text
$ java -jar target/greeting-1.0.jar Ada
Exception in thread "main" java.lang.NoClassDefFoundError: org/apache/commons/lang3/StringUtils
	at com.example.greeting.Greeting.greet(Greeting.java:8)
	at com.example.greeting.Greeting.main(Greeting.java:13)
Caused by: java.lang.ClassNotFoundException: org.apache.commons.lang3.StringUtils
```

The build was green and the artifact is dead on arrival. Nothing about this is a mistake in the build: `mvn test` runs Surefire with the full dependency classpath that Maven resolved, so `StringUtils` was right there for the test, and the test told the truth about the code. `mvn package`, by contrast, packages exactly one thing into the jar, the project's own compiled classes:

```text
com/example/greeting/Greeting.class
```

Nothing from `commons-lang3` is in there, because the `maven-jar-plugin`'s job has never been "package everything on the classpath", it is "package what this module compiled". `java -jar` runs with the classpath fixed to that one jar, so the moment `Greeting.greet` reaches the bytecode that references `StringUtils`, the JVM asks its classloader for a class that exists nowhere it is allowed to look, and throws `NoClassDefFoundError`. `NoClassDefFoundError` specifically means the compiler saw the class and was happy, and the *runtime* classpath is what came up short, which is exactly this situation: correct code, wrong shipping. This is the single most common way a "finished" Java project turns out not to be shippable, and it passes every test along the way.

### Three ways off the cliff

**1. A `Class-Path` manifest entry, with the jars shipped alongside.** Tell `maven-jar-plugin` to add a classpath, and use `maven-dependency-plugin`'s `copy-dependencies` goal to actually put the dependency jars where that classpath points:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-jar-plugin</artifactId>
  <version>3.5.1</version>
  <configuration>
    <archive>
      <manifest>
        <mainClass>com.example.greeting.Greeting</mainClass>
        <addClasspath>true</addClasspath>
        <classpathPrefix>lib/</classpathPrefix>
      </manifest>
    </archive>
  </configuration>
</plugin>
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-dependency-plugin</artifactId>
  <version>3.11.0</version>
  <executions>
    <execution>
      <id>copy-dependencies</id>
      <phase>package</phase>
      <goals><goal>copy-dependencies</goal></goals>
      <configuration>
        <outputDirectory>${project.build.directory}/lib</outputDirectory>
        <includeScope>runtime</includeScope>
      </configuration>
    </execution>
  </executions>
</plugin>
```

This writes `Class-Path: lib/commons-lang3-3.20.0.jar` into the manifest, and `copy-dependencies` drops that exact file into `target/lib`. `java -jar` resolves a `Class-Path` entry relative to the jar's own location, not the working directory, so running from `target/` now works:

```text
$ java -jar target/greeting-1.0.jar Ada
Hello, Ada!
```

The honest cost: `lib/` has to travel with the jar. Copy the jar alone anywhere and it is back on the cliff.

**2. An uber jar via `maven-shade-plugin`.** One file that runs anywhere, because the dependencies' classes are unpacked and repacked inside it:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-shade-plugin</artifactId>
  <version>3.6.2</version>
  <executions>
    <execution>
      <phase>package</phase>
      <goals><goal>shade</goal></goals>
      <configuration>
        <shadedArtifactAttached>true</shadedArtifactAttached>
        <shadedClassifierName>shaded</shadedClassifierName>
        <transformers>
          <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
            <mainClass>com.example.greeting.Greeting</mainClass>
          </transformer>
          <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer" />
        </transformers>
      </configuration>
    </execution>
  </executions>
</plugin>
```

Copied to an empty directory with nothing else next to it, this runs:

```text
$ java -jar greeting-1.0-shaded.jar Ada
Hello, Ada!
```

Two things the plugin had to solve to get there, and both show up in the configuration above. First, two dependencies can each contain a file at the same path, most commonly `META-INF/MANIFEST.MF` itself or a `META-INF/services/` entry used by `ServiceLoader`; a naive merge would let the last one packaged silently win and drop the other's registration. The `ManifestResourceTransformer` writes one deliberate manifest instead of concatenating candidates, and the `ServicesResourceTransformer` concatenates same-named `META-INF/services` files line by line instead of overwriting, so a provider registered by one dependency does not vanish because another dependency shipped a file at the identical path. Second, when two dependencies pull in different, incompatible versions of some third library, `relocation` renames a dependency's packages wholesale, `com.thing` to `shaded.com.thing`, so two copies can coexist in one jar without colliding on the classloader. This project needed neither, having exactly one dependency, so the configuration above only carries the two transformers most projects end up needing anyway.

The honest costs: measured on this project, one small class plus `commons-lang3` 3.20.0, the plain jar is 3.19 KB and the shaded jar is 699.0 KB, a ratio of about 220 to 1, on one small dependency graph, and it grows with every dependency added. The other cost is less visible: the original per-library `META-INF` metadata, licence files, `NOTICE` files, module descriptors, is flattened into one artifact, so provenance that used to be one jar per statement becomes archaeology.

**3. `jlink` and `jpackage`, named and not taught here.** `jlink` assembles a custom, minimal Java runtime image containing only the modules a modular application needs, so the target machine needs no separately installed JDK at all. `jpackage` goes one step further and wraps an application, its dependencies and a runtime image into a platform-specific installer or native executable. Both solve a real problem, shipping to a machine that has no JDK, and both assume a modular application as a starting point, which is a bigger step than this lesson takes.

### What the module system sees

Even a jar with no `module-info.class` is visible to the module system, as an automatic module, and `jar --describe-module` shows you exactly what gets derived:

```text
$ jar --describe-module --file target/greeting-1.0.jar
No module descriptor found. Derived automatic module.

greeting@1.0 automatic
requires java.base mandated
contains com.example.greeting
main-class com.example.greeting.Greeting
```

Read that module name again: `greeting`, derived from the jar's own file name, `greeting-1.0.jar`, with the version-looking suffix stripped. The code inside is packaged as `com.example.greeting`. Those two do not match, and nothing about the build complains, because nothing is wrong yet: an automatic module's derived name is purely a function of the file name at the moment something puts it on a module path, which is a fact about the file, not about the code. Set an `Automatic-Module-Name` attribute in the manifest and the derived guess is replaced by something the library author actually chose:

```xml
<manifestEntries>
  <Automatic-Module-Name>com.example.greeting</Automatic-Module-Name>
</manifestEntries>
```

```text
$ jar --describe-module --file target/greeting-1.0.jar
No module descriptor found. Derived automatic module.

com.example.greeting@1.0 automatic
requires java.base mandated
contains com.example.greeting
main-class com.example.greeting.Greeting
```

Copy that exact jar to a deliberately odd file name and check again, and the point sharpens further:

```text
$ jar --describe-module --file greeting-renamed-oddly-99.jar
com.example.greeting@99 automatic
```

The name held, `com.example.greeting`, but the version did not: it is still parsed from whatever numeric-looking suffix trails the file name, `99` here, regardless of the manifest. `Automatic-Module-Name` fixes the one thing that matters for another module's `requires` clause to keep working when the jar gets renamed or repackaged. This is why a library should set it even while shipping ordinary, non-modular code: nothing about writing `Automatic-Module-Name` requires a `module-info.class`, and it is the only part of "what does the module system call this jar" that the author gets to decide rather than have derived from a file name a repackaging tool might change.

### Reproducible builds

Two builds from identical, unmodified source do not normally produce identical bytes. Building the project above twice in a row and hashing the jar each time:

```text
$ shasum -a 256 target/greeting-1.0.jar    # build 1
999dd8926c859f6cd7f432cc4abe9bf61c221053a298729ece6a840e3e14b299
$ shasum -a 256 target/greeting-1.0.jar    # build 2, same source, moments later
1228c435e4f7b7711dc5989a09601bdb0d2bb6659b771b45fad9f295f837ca8d
```

Different hashes, confirmed byte-different with `cmp`, from a project that did not change between the two runs. The cause is timestamps: every entry in a zip carries a modification time, and Maven stamps each entry with the time the build ran, so two builds a few seconds apart write different bytes even though every `.class` file inside is identical. Setting one property fixes it:

```xml
<properties>
  <project.build.outputTimestamp>2026-01-01T00:00:00Z</project.build.outputTimestamp>
</properties>
```

Rebuilding twice with that property in place, and it holds exactly as advertised:

```text
$ shasum -a 256 target/greeting-1.0.jar    # build 1, outputTimestamp set
23d886018c1c74302756fb9f76b41b01b26293fef4efa867615151b2341822bc
$ shasum -a 256 target/greeting-1.0.jar    # build 2, outputTimestamp set
23d886018c1c74302756fb9f76b41b01b26293fef4efa867615151b2341822bc
```

Identical hashes, confirmed byte-identical with `cmp`. This one worked exactly as the property's documentation claims: one timestamp, applied consistently to every archive entry, is enough to make `mvn package` deterministic for this project. It is worth checking on a project with more moving parts than a single-class demo, since other plugins that touch archive entries can reintroduce non-determinism of their own, but for the plugins used in this lesson, the property alone closed the gap.

### What belongs in the repository for the handover to succeed

Three things, and all three already exist by this point in the arc: the wrapper scripts from [Lesson 34](0034-the-build-lifecycle.md), so a clone needs no pre-installed Maven at all; a `pom.xml` with every plugin and dependency pinned to an exact version, [Lesson 33](0033-declaring-dependencies.md)'s subject, so the build run six months from now uses the same inputs as the build run today; and a short README with the two commands that matter, how to build and test, and how to run what came out. Nothing more elaborate than that is required, and nothing less is enough.

### The handover test

This is the procedure that makes the stage's promise literally true. Perform it yourself, on the project you have been building through this lesson, before trusting that someone else can do it.

1. Copy the whole project, wrapper scripts and all, to a clean directory, one that has never had a build run in it. A different machine is a better test than a different directory on the same one, but a directory with no `target/` and no warm dependency cache still catches most of what matters.
2. From that clean copy, with nothing but a JDK on the path, no separately installed Maven, run the wrapper: `./mvnw clean verify`. Confirm it downloads its own Maven distribution the first time, then compiles, then runs the test suite, then reports `BUILD SUCCESS`.
3. Run the artifact the build produced, with `java -jar`, and confirm it does what it is supposed to do.

Run on the demo project from this lesson, with the system `mvn` deliberately removed from the path so only the wrapper and the JDK were available:

```text
$ which mvn
mvn not found
$ ./mvnw clean verify
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
$ java -jar target/greeting-1.0.jar Ada
Hello, Ada!
```

Clean copy, no pre-installed Maven, wrapper downloads its own, tests pass, artifact runs. That is the stage's done-when criterion, performed rather than asserted.

## Practice

1. ▢ Predict what `java -jar` prints when the manifest has a `Main-Class` attribute that names a class not actually present in the jar, then build a jar like that and run it.

<details markdown="1"><summary>Check</summary>

`java.lang.NoClassDefFoundError`, naming the missing main class, because the launcher reads `Main-Class` from the manifest and then asks the classloader for that class before anything else runs. It is the same exception family as the dependency cliff, for the same underlying reason: the manifest promised a class the archive does not actually contain.

</details>

2. ▢ A colleague's "fix" for the dependency cliff is to run the application with `java -cp target/classes:$(find ~/.m2 -name '*.jar' | tr '\n' ':') com.example.greeting.Greeting` instead of `java -jar`. Predict whether this works, and name the property of a "runnable artifact" it gives up even if it does.

<details markdown="1"><summary>Hint</summary>

Ask what has to be true about the machine running that command for the classpath expression to resolve to anything at all.

</details>

<details markdown="1"><summary>Check</summary>

It works, on the machine that has that exact local repository populated, which is the whole problem: it is not an artifact, it is a command that only means something on a machine with the right `~/.m2` already warmed. A runnable artifact travels; this does not.

</details>

3. ▢ Build the shaded jar for a project with two dependencies that each ship a `META-INF/services/java.nio.file.spi.FileSystemProvider` entry naming a different provider. Predict what happens without the `ServicesResourceTransformer`, then check by removing it.

<details markdown="1"><summary>Check</summary>

Without the transformer, the plugin's default merge takes one file and one wins, so only one provider ends up registered, silently, with no build error to flag it. The other dependency's `ServiceLoader` registration is simply gone from the shaded jar. Adding the transformer back concatenates the two files so both providers register.

</details>

4. ▢ Two teammates each run `mvn package` on the same commit, on different machines, with `project.build.outputTimestamp` set. Predict whether the resulting jars are byte-identical, then say what would break the guarantee even with the property set.

<details markdown="1"><summary>Check</summary>

They should be byte-identical, since the property fixes the one source of non-determinism this lesson demonstrated, timestamps on archive entries. It would break if the two machines resolved different dependency versions, for instance because one had a stale local cache or a version range in the POM rather than a pin, which is exactly why Lesson 33's advice to pin every version is not a separate concern from this one.

</details>

5. ▢ Rename a jar that has no `Automatic-Module-Name` set from `payments-2.3.jar` to `payments-core.jar`, and predict what `jar --describe-module` reports for it before and after.

<details markdown="1"><summary>Check</summary>

Before, the derived module is `payments` at version `2.3`, both parsed from the file name. After the rename to `payments-core.jar`, with no digits left for the parser to treat as a version, the derived module becomes `payments.core` with no version at all. Nothing about the code changed, only the file name did, and the module system's idea of what to call the module changed with it.

</details>

## Real-world reps

- [ ] Run the handover test, as written above, on a personal or work project that already has tests and a `pom.xml`. Note the first thing that fails, if anything does.
- [ ] Take a project that currently ships with a README instructing the reader to install a specific Maven version by hand, and replace that instruction with the wrapper from Lesson 34.
- [ ] Find a project on a shared team repository that produces a plain jar today, and check by hand whether `java -jar` on that artifact, run outside the build's own working directory, actually starts.
- [ ] Pick a dependency-bearing project and decide, deliberately rather than by copying a template, which of the three ways off the cliff fits its deployment target, and write the one sentence that justifies it.
- [ ] Tomorrow: run `jar --describe-module --file` against the plain jar your own current project already produces, and read what name and version it derived.

## Going further

- [Guide to Uber JAR](https://maven.apache.org/plugins/maven-shade-plugin/index.html): the shade plugin's own goals, transformers and relocation reference
- [Introduction to the Dependency Mechanism](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html): how Maven resolves the classpath that Surefire sees but `package` does not copy
- [Configuring for Reproducible Builds](https://maven.apache.org/guides/mini/guide-reproducible-builds.html): the `outputTimestamp` property and the wider practice it belongs to
- [Testing and build](../reference/testing-and-build.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
