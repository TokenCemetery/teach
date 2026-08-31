---
title: 19. Files and Paths
description: Paths that are not strings, streams that must be closed, and a charset that is finally a default worth having
type: lesson
---

# Lesson 19. Files and Paths

**Mission link:** A service that reads its own configuration and writes its own output meets this API on every run, and the two ways it corrupts data all by itself, a half-written file left behind by a crash and a stream nobody closed, are cured by the same two disciplines this lesson teaches: atomic replacement and try-with-resources.
**Primary source:** [`Files`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html)
**Prerequisites:** [Lesson 15](0015-exceptions.md), [Lesson 17](0017-streams.md)

## Warm-up

1. ▢ Two resources, `a` then `b`, are declared in that order in one try-with-resources statement. In which order does the statement close them, and why does that order matter?

<details markdown="1"><summary>Check</summary>

In reverse: `b` closes before `a`. Closing in the opposite order from acquisition means a resource that depends on another, such as a writer wrapping a channel, is always closed while the thing underneath it is still open, never after it.

</details>

2. ▢ A terminal operation has already run on a `Stream<Integer>`. What happens if a second terminal operation runs on that same stream instance?

<details markdown="1"><summary>Check</summary>

It throws `IllegalStateException: stream has already been operated upon or closed`. A stream describes one pipeline that runs once; nothing about calling a terminal operation resets it, which is why a stream already used gets discarded rather than reused.

</details>

## Know this

### `Path` and `Files`, not `File`

`Path` and `Files` are the current API for anything filesystem-shaped: `Path` represents a location, and `Files` is the class holding the static operations that act on one. `java.io.File` predates both, and its design shows the age: most of its methods report failure by returning a `boolean`, so a caller has to remember to check the result to notice anything went wrong, and even then the `boolean` says nothing about why. Calling delete on a file that never existed makes the difference concrete.

```java
File ghost = new File("no-such-file.txt");
System.out.println(ghost.delete());                        // false, no explanation

Files.delete(Path.of("no-such-file.txt"));
// java.nio.file.NoSuchFileException: no-such-file.txt
```

`File.delete()` on a missing file returned `false` and stopped there; `Files.delete` on the identical path threw `NoSuchFileException`, naming the file and the reason in one line. Write new code against `Path` and `Files`; recognise `File` when an older library insists on it, and convert between the two with `File.toPath()` and `Path.toFile()` rather than rewriting the library.

### Building and resolving a path

```java
Path base = Path.of("/home/user/project");
System.out.println(base.resolve("config.txt"));            // /home/user/project/config.txt
System.out.println(base.resolve(Path.of("/etc/passwd")));   // /etc/passwd
```

`resolve` treats its argument as relative to the receiver, unless the argument is itself absolute, in which case the argument comes back unchanged and the receiver is discarded entirely. That is a real source of bugs: code that builds `base` to keep every read and write underneath one directory, then resolves a value that arrived from configuration or from a request, silently steps outside that directory the moment the value happens to be absolute, because `resolve` did exactly what it documents and nothing checked which kind of argument had arrived.

```java
Path withDots = Path.of("/home/user/./project/../shared/file.txt");
System.out.println(withDots.normalize());                  // /home/user/shared/file.txt
```

`normalize`, `relativize` and `toAbsolutePath` never look at the filesystem; they are string manipulation over a path's components, which is why `normalize` collapsed the `.` and `..` segments above into a clean path with no directory named `project` or `shared` needing to exist. `relativize` runs in one direction only: `Path.of("/home/user/project").relativize(Path.of("/home/user/project/reports/2025"))` gives `reports/2025`, and calling it the other way round gives `../..`, the walk back up rather than down.

### Reading and writing

`Files.readString` and `Files.readAllLines` read the whole file eagerly, into a `String` or a `List<String>`; `Files.newBufferedReader` gives a reader for reading incrementally without loading everything at once. `Files.lines` looks like one more convenience but is not: it returns a `Stream<String>` that reads the file lazily, line by line, backed by an open file handle, and the documentation is explicit that it must be closed, unlike the others, which return once the read is done and hold nothing open afterwards.

```java
System.out.println(Charset.defaultCharset());               // UTF-8
```

Since JEP 400 (Java 18) the platform default charset is UTF-8 everywhere the JVM runs, rather than the locale-dependent default of earlier releases; code that used to depend on the platform default, an `InputStreamReader` or a `FileWriter` built with no charset argument, changed behaviour on any platform whose native default was not already UTF-8 when it moved to Java 18 or later. Naming a charset explicitly still beats relying on any default, but the default is now one worth having.

Opening tens of thousands of `Files.lines` streams without closing them, and keeping every one of them reachable so nothing could be garbage-collected in the meantime, does eventually exhaust the process's file descriptors: after roughly sixty thousand unclosed, held-open streams the next open failed with `java.nio.file.FileSystemException: leaktest.txt: Too many open files`. The "held reachable" qualifier matters: running the identical loop without keeping a reference to each stream produced no failure at all, even past a hundred thousand iterations, because a stream that becomes unreachable gets its underlying channel closed by the JDK's own cleaner regardless. That is not permission to skip try-with-resources; it explains why skipping it usually gets away with it anyway, right up until something keeps a `Files.lines` stream reachable for long enough, or opens enough of them fast enough, that the cleaner cannot keep up.

### Walking a tree, and deleting one

`Files.walk` and `Files.find` are closeable streams for exactly the same reason `Files.lines` is: both read a directory tree lazily and hold a directory handle open until the stream is closed. `Files.find` is `walk` with a filter built in, taking a maximum depth and a `BiPredicate<Path, BasicFileAttributes>` in place of a separate filtering stage, which saves fetching attributes twice when the filter needs them.

```java
Files.delete(dir);   // dir contains a file and a subdirectory
// java.nio.file.DirectoryNotEmptyException: tree
```

`Files.delete` refuses outright to remove a non-empty directory. Deleting a tree means walking it and removing the deepest entries first:

```java
try (Stream<Path> walk = Files.walk(dir)) {
    walk.sorted(Comparator.reverseOrder())
        .forEach(p -> {
            try {
                Files.delete(p);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
}
```

Sorting the walked paths in reverse of their natural ordering puts every entry after its parent, so a directory's contents are always gone before the directory itself is deleted; run against a two-level tree, the loop finished with nothing thrown and `Files.exists(dir)` reported `false` afterwards.

### Creating directories

`Files.createDirectory` makes exactly one directory and is strict about it: called on a directory that already exists it threw `FileAlreadyExistsException: tree/sub`, and called where the parent is missing it threw `NoSuchFileException: a/b/c`. `Files.createDirectories` makes every missing intermediate directory and raises nothing when the target is already there, verified by calling it twice on the same path with no exception either time. Reach for `createDirectories` by default; `createDirectory`'s stricter contract earns its keep only when the caller specifically wants to be told the directory already existed.

### `exists`, and the race it invites

`Files.exists` answers a question about a single instant, and the filesystem is free to change before the code that follows gets to act on the answer: another process can delete the file between the check and the read, or create the directory between the check and the `createDirectory` call. An existence check cannot be a lock, so nothing about calling it first closes that window. The sturdier shape is to skip the check and let the real operation fail when there is nothing there, then catch the specific exception it throws, the same preference for a self-describing failure over a bare test that [Lesson 15](0015-exceptions.md) makes for exceptions generally.

### Atomic move, and writing a file safely

Writing new content directly into a target file, incrementally, leaves a window in which a reader opening that file partway through the write sees a half-written result, and a crash mid-write leaves the corruption behind permanently. The fix is to write the new content to a temporary file and move it into place as one step:

```java
Path tmp = Files.createTempFile(target.getParent(), "config", ".tmp");
Files.writeString(tmp, newContent);
Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
```

Run end to end, `Files.readString(target)` afterwards read back only the new content, never the old content and never a mixture. `ATOMIC_MOVE` makes the switch a single filesystem operation, so any reader that opens `target` sees either the complete old file or the complete new one. The temporary file has to sit in the same directory as the target, because an atomic move is only guaranteed within one filesystem; across filesystems it typically falls back to a copy followed by a delete, which is precisely the non-atomic sequence this exists to avoid.

`Files.copy` takes the same kind of option: copying onto an existing target with no option threw `FileAlreadyExistsException`, and adding `StandardCopyOption.REPLACE_EXISTING` made the identical call succeed. `COPY_ATTRIBUTES` is the third standard option, carrying over timestamps and whatever other attributes the filesystem supports rather than giving the copy fresh ones.

### A `Path` says nothing about existence

Building a `Path`, resolving it, or normalising it never touches the disk, so a `Path` can legally name something that does not exist yet, existed once and is now gone, or will exist only once this code creates it; nothing about the type distinguishes those cases from each other. Assuming otherwise fails at the exact point the assumption gets used: `toRealPath()`, which does touch the disk to resolve symbolic links and requires the target to be real, threw `NoSuchFileException` naming the path when run against directories that were never created, and `Files.readString` threw the same exception type against a path that was never written. Treat a `Path` as a name and every operation that needs the thing behind the name to be real as one that can fail for exactly that reason.

## Practice

1. ▢ Predict the output, and explain it.

   ```java
   Path base = Path.of("/var/app/data");
   Path input = Path.of("/etc/shadow");
   System.out.println(base.resolve(input));
   ```

<details markdown="1"><summary>Check</summary>

`/etc/shadow`. `resolve` returns an absolute argument unchanged and discards the receiver entirely; `base` never appears in the result. This is the exact shape of the bug the lesson warns about: a value assumed to be a filename arrives as an absolute path instead, and the sandbox `base` was meant to enforce disappears with no error raised anywhere.

</details>

2. ▢ Find the bug.

   ```java
   List<String> lines = new ArrayList<>();
   Files.lines(path).forEach(lines::add);
   ```

<details markdown="1"><summary>Check</summary>

The stream `Files.lines` opens is never closed. Unlike `readAllLines`, this one holds a file handle open for as long as it stays reachable and unclosed, and nothing here closes it. Either wrap it in try-with-resources, `try (Stream<String> s = Files.lines(path)) { s.forEach(lines::add); }`, or, since a `List` was wanted all along, call `Files.readAllLines(path)` directly and skip the stream entirely.

</details>

3. ▢ A program needs to scan a many-gigabyte log file once, checking each line against a pattern. Which of `readString`, `readAllLines`, `newBufferedReader` or `Files.lines` fits, and which two would be a mistake here?

<details markdown="1"><summary>Hint</summary>

Ask what each option holds in memory at once before the first line is even checked.

</details>

<details markdown="1"><summary>Check</summary>

`Files.lines` fits, opened in try-with-resources, because it reads and hands over one line at a time and can be short-circuited without reading the rest of the file. `readString` and `readAllLines` would be a mistake, since both load the entire file into memory as one `String` or one `List<String>` before any line is checked, which is exactly the cost this file is too large to pay. `newBufferedReader` would also work, read in a loop, but gives up the stream operations `Files.lines` offers for the same lazy, line-at-a-time reading.

</details>

4. ▢ Predict what happens.

   ```java
   Files.createDirectory(Path.of("a/b"));   // "a" does not exist yet
   ```

<details markdown="1"><summary>Check</summary>

`NoSuchFileException: a/b`. `createDirectory` requires the parent to already exist and creates exactly one level; it will not create `a` on the way to creating `b`. `Files.createDirectories(Path.of("a/b"))` would create both and raise nothing.

</details>

5. ▢ A configuration file is rewritten by calling `Files.writeString(target, newContent)` directly, in place, every time it changes. Name the failure mode this invites and the fix.

<details markdown="1"><summary>Check</summary>

A reader that opens `target` while the write is in progress can see a partial file, part old content and part new, and a crash during the write leaves that partial file behind for good, since nothing rolls it back. The fix is to write the new content to a temporary file in the same directory and then `Files.move` it onto `target` with `ATOMIC_MOVE` and `REPLACE_EXISTING`, so the switch from old content to new is one filesystem operation and every reader sees a whole file, either the old one or the new one, never a partial one.

</details>

## Real-world reps

- [ ] Write a small program that reads a short file with `Files.readString` and a larger one with `Files.lines` inside try-with-resources, and check that the second still closes when an early `takeWhile` stops before the end of the file.
- [ ] Reproduce `DirectoryNotEmptyException` by creating a directory with one file inside it and calling `Files.delete` on the directory, then fix the delete with the walk-and-delete-deepest-first sequence from this lesson.
- [ ] Replace one place in code you already have that writes a file directly with a temp-file-then-atomic-move sequence.
- [ ] Tomorrow: find a file-reading call in code you already have, and check whether it calls `Files.exists` first or simply attempts the read and catches the exception if there is nothing there.

## Going further

- [`Files`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html): every static operation, and which ones return a stream that must be closed
- [`Path`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Path.html): building, resolving, comparing and iterating over a path's components
- [JEP 400: UTF-8 by Default](https://openjdk.org/jeps/400): the platform default that changed in Java 18, and why
- [Idiom and the library](../reference/idiom-and-library.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
