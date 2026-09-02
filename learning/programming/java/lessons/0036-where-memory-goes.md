---
title: 36. Where Memory Goes
description: The five places the JVM puts memory, and which OutOfMemoryError names which one
type: lesson
---

# Lesson 36. Where Memory Goes

**Mission link:** Owning a Java service in production means being the person a pager wakes up when a container is killed with no Java stack trace at all, and that starts with knowing that `-Xmx` describes one room in the process, not the whole house.
**Primary source:** [HotSpot Virtual Machine Garbage Collection Tuning Guide, Release 25, Oracle](https://docs.oracle.com/en/java/javase/25/gctuning/index.html)
**Prerequisites:** [Lesson 35](0035-a-runnable-artifact.md), [Lesson 23](0023-the-memory-model.md)

## Warm-up

Lesson 22 described a thread as a scheduled call stack: each method call pushes a frame holding its local variables and where to return to when the call finishes. That stack has to live somewhere in memory. Where, and is it the same place `new` puts the objects your code creates?

<details markdown="1"><summary>Check</summary>

A thread's call stack lives in its own thread stack, one per thread, reserved when the thread starts and released when it ends. It is not the same place as `new`, which allocates on the heap, a pool shared by every thread in the process and managed on a completely different lifetime, one object at a time, by the garbage collector rather than by a single thread finishing a single call. That separation, one pool per thread for call frames and one shared pool for objects, is the first crack in the idea that "the JVM's memory" means "the heap", and this lesson widens it.

</details>

## Know this

### Five rooms, one process

A running JVM is one operating-system process, and that process's memory is not one undifferentiated pool. It is at least five separate areas, each with its own owner, its own way of filling up, and its own way of being bounded:

| Area | Holds | Allocated by | Freed by | Typically bounded by |
|---|---|---|---|---|
| Heap | Objects your code creates | Application code, via `new` and everything that compiles down to it | The garbage collector | `-Xmx` |
| Metaspace | Loaded classes' metadata | The class loading machinery, as classes load | Unloading the classloader that defined them | `-XX:MaxMetaspaceSize` |
| Thread stacks | Call frames, one stack per thread | The JVM, when a thread starts | The JVM, when the thread ends | `-Xss`, times the number of live threads |
| JIT code cache | Compiled native machine code | The just-in-time compiler, as methods get hot | Code cache sweeping, when compiled code goes cold | `-XX:ReservedCodeCacheSize` |
| Native and direct memory | Direct buffers, JNI, memory-mapped files, the collector's own bookkeeping | Library and platform code outside the heap's ledger | Whatever freed the native resource, often a cleaner rather than the garbage collector | `-XX:MaxDirectMemorySize`, and otherwise nothing you set |

The rest of this lesson walks through each row, then shows why the JVM's own vocabulary for running out, the `OutOfMemoryError` message, is precise about which row ran dry.

### The heap, and what actually bounds it

The heap is the one area every Java programmer already has some picture of: it is where objects live, and it is what the garbage collector is collecting. `-Xmx` sets its maximum size and `-Xms` sets its initial size. On a server-class machine with no flags at all, the default collector is G1, reported by the JVM itself as `{ergonomic}` rather than as a default anyone chose. What G1 or any other collector actually does, and how the five collectors compare, is not this lesson's subject; the point here is narrower and more load-bearing than any collector's algorithm: the heap is one room, `-Xmx` is the size of that room, and nothing about `-Xmx` says anything at all about the other four rooms in the table above.

### Metaspace, the class data that is not on the heap

Before JDK 8 this area had a different name and a different, notoriously awkward flag; since then it is metaspace, and it holds the metadata for every class the JVM has loaded, the constant pool, the method bytecode, the layout of fields, everything the class loading machinery produced when it parsed a `.class` file and made a `Class` object usable. It is not object data and it is not on the heap. Asking for its bound with `-XX:+PrintFlagsFinal -version` shows why an ordinary program rarely thinks about it at all:

```text
size_t MaxMetaspaceSize = 18446744073709551615 {product} {default}
```

That number is not a generous cap someone chose; it is `size_t`'s own maximum value, which is the JVM's way of saying "unbounded, unless you say otherwise". Metaspace fills up in a way ordinary garbage collection cannot touch: individual objects are freed one at a time as they become unreachable, but a class's metadata is only freed when the classloader that defined that class becomes unreachable, and every class it loaded is discarded together, as one unit. A program that loads a bounded, fixed set of classes at startup will barely notice metaspace exists. A program that keeps defining new classes at runtime, whether that is a hot-reloading development server, a framework that generates proxy classes per request, or a scripting or expression engine compiling fresh classes on the fly, can fill this area steadily in a way that looks nothing like an ordinary memory leak, because the leaked objects are entire classes, not instances.

### Thread stacks, one per thread

Lesson 22 already named the shape of this one: a call stack per thread. What that stack costs is a fixed reservation, made once when the thread starts, sized by `-Xss`. Reading the JVM's own reported default:

```text
intx ThreadStackSize = 2048 {pd product} {default}
```

Two thousand and forty eight kibibytes, two mebibytes, reserved for every platform thread's stack by default before that thread has called a single method of your own code. That number multiplies: a thousand platform threads is on the order of two gibibytes of stack reservation before any of them does anything, which is exactly the arithmetic that made "one thread per request" an expensive habit and made lesson 27's virtual threads worth learning, since a virtual thread's stack does not carry that same fixed native reservation per unit of concurrency. Nothing about that comparison is retaught here; it is named only to show that this row of the table is not a rounding error, it is the reason thread-per-request designs run out of something before they run out of heap.

### The JIT code cache

Bytecode does not run as bytecode forever. As a method gets called often enough, the just-in-time compiler translates it into native machine code, and that compiled code has to live somewhere the processor can execute it directly: the code cache. Measured on the same command:

```text
uintx ReservedCodeCacheSize = 251674624 {pd product} {ergonomic}
```

About two hundred and forty mebibytes, reported `{ergonomic}` because the JVM computed it rather than reading a fixed constant, the same tag `InitialHeapSize` and `MaxHeapSize` carry below. When the code cache fills, the compiler stops compiling new methods and everything keeps running, just more slowly, in bytecode; a full code cache is a performance cliff, not a crash, which is the one row in this table that degrades gracefully instead of throwing. How the JIT decides what to compile, and what escapes it can prove along the way, is lesson 38's subject, not this one; here it is enough to know the compiled code has to be stored somewhere, and that somewhere is neither the heap nor metaspace.

### Native and direct memory

This is the area with no single clean boundary, because it is defined by what it is not: not the heap, not metaspace, not a thread stack, not the code cache. It holds memory-mapped files, JNI allocations from native libraries, the garbage collector's own internal bookkeeping structures, and, most visibly to application code, direct buffers created with `ByteBuffer.allocateDirect`. A direct buffer keeps only a small handle object on the heap; the actual bytes it wraps live here, outside the heap entirely, which is precisely why they need their own bound, `-XX:MaxDirectMemorySize`. Left unset, it is reported as:

```text
uint64_t MaxDirectMemorySize = 0 {product} {default}
```

Zero is not "zero bytes allowed"; it is the flag's way of saying "not set", and the JVM falls back to treating the maximum heap size as the effective ceiling for direct memory too. Setting the flag explicitly gives this pool its own bound instead of quietly sharing one sized for a different purpose. Provoking that ceiling on a throwaway program, with a small heap and a small explicit direct memory limit, produces this, in full:

```text
Exception in thread "main" java.lang.OutOfMemoryError: Cannot reserve 1000000 bytes of direct buffer memory (allocated: 16000000, limit: 16777216)
	at java.base/java.nio.Bits.reserveMemory(Bits.java:178)
	at java.base/java.nio.DirectByteBuffer.<init>(DirectByteBuffer.java:108)
	at java.base/java.nio.ByteBuffer.allocateDirect(ByteBuffer.java:367)
```

Notice what that message reports and what it does not: allocated bytes and a limit, both in this pool, with no mention of the heap at all, because the heap in that same run was nowhere near full.

### Resident memory is the sum, and `-Xmx` only bounds one line item

Put the five rows back together and the practical consequence is immediate: the memory the operating system actually charges to a Java process, its resident memory, is the heap plus metaspace plus every thread's stack plus the code cache plus whatever native and direct memory the process has reserved. `-Xmx` bounds exactly one of those five numbers. A container started with a memory limit of, say, five hundred and twelve mebibytes, and a JVM inside it launched with `-Xmx512m` and nothing else, has been told "the heap may use all five hundred and twelve mebibytes", which leaves precisely zero headroom for metaspace, stacks, the code cache, or anything native. That process's resident memory crosses the container's ceiling the moment the other four rooms need any space at all, which they always do, and the container's own out-of-memory killer, a mechanism completely outside the JVM, terminates the process. There is no `OutOfMemoryError` in that failure, no stack trace, no log line the application wrote, because the JVM was never asked to throw anything: it was simply killed from outside, mid-sentence, by a supervisor that only ever saw one number, total resident memory, cross one other number, the limit. The fix has one shape regardless of which container platform is involved: leave headroom below the container's limit for everything that is not the heap, and set the ceilings that matter, `-Xmx`, and where they apply, `-XX:MaxMetaspaceSize`, `-Xss` times the thread count you actually expect, `-XX:MaxDirectMemorySize`, deliberately, rather than trusting that the default for each one happens to add up to something safe.

### Ergonomics: computed defaults, not chosen ones

`-XX:+PrintFlagsFinal -version`, run with no other flags, is how the previous sections' numbers were read, and it is worth reading its own labels carefully, because two different tags mean two different things:

```text
size_t InitialHeapSize  = 268435456                                 {product} {ergonomic}
size_t MaxHeapSize      = 4294967296                                {product} {ergonomic}
double MaxRAMPercentage = 25.000000                                 {product} {default}
```

`MaxRAMPercentage` is tagged `{default}`: twenty five per cent is a literal constant, hard-coded into the JVM, the same on every machine. `InitialHeapSize` and `MaxHeapSize` are tagged `{ergonomic}`: those two numbers are not constants at all, they are the result of a calculation the JVM performed at startup, taking whatever it believed the available memory to be and applying that twenty five per cent to it. On the machine that produced the numbers above, four gibibytes is a quarter of sixteen. Change the machine's memory and those two ergonomic numbers change with it, silently, without a single flag being touched. Inside a container, that calculation is only as good as what the JVM believes "available memory" to mean. A JVM that correctly reads the container's own memory limit sizes its heap as a quarter of that limit, which is usually a reasonable, conservative default. A JVM that, for whatever reason, ends up reading the host machine's total memory instead of the container's limit, an older container runtime, an unusual cgroup configuration, a limit that was never actually set on the container, sizes its heap as a quarter of a number that has nothing to do with what the container will actually let the process use, and every scenario in the previous section follows from there. The fix is the same one, restated: say what you mean. Set `-Xmx` (or `-XX:MaxRAMPercentage` at a value you have checked against the container's real limit and the other four rows' needs) explicitly, rather than trusting an ergonomic calculation to have seen the same ceiling the container will actually enforce.

### `OutOfMemoryError` as a diagnostic index

Once the five rooms are separate in your head, `OutOfMemoryError`'s message text stops being a generic "ran out of memory" and becomes an index into the table above, naming which room, which narrows what to check next:

| Message names | The area that ran out | What to look for |
|---|---|---|
| `Java heap space` | The heap | Too many live objects, or `-Xmx` set too low for the workload |
| `Metaspace` | Metaspace | Classes being defined and never unloaded, often a classloader leak or runtime class generation |
| `unable to create native thread` | Thread stacks, and the operating system's own thread limit | Too many platform threads created, often one-thread-per-request under load |
| `Direct buffer memory` | Native and direct memory | Direct buffers allocated and never released, or `-XX:MaxDirectMemorySize` set too low |
| `GC overhead limit exceeded` | The heap, specifically | The collector running almost continuously and reclaiming almost nothing, which usually means the heap is undersized for what is actually live, not merely full of garbage |
| `Requested array size exceeds VM limit` | The heap, at the point of a single allocation | One array whose requested length is larger than the JVM will ever attempt to satisfy, often an overflowed or miscalculated size rather than a true capacity need |

Provoking the first and the last of these on a throwaway program shows the message text exactly as the JVM writes it, with nothing added:

```text
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
	at HeapFill.main(HeapFill.java:8)
```

```text
Exception in thread "main" java.lang.OutOfMemoryError: Requested array size exceeds VM limit
	at ArraySize.main(ArraySize.java:3)
```

Loading a steady stream of freshly defined classes with a small metaspace ceiling names the second row exactly as the table predicts:

```text
Exception in thread "main" java.lang.OutOfMemoryError: Metaspace
	at java.base/java.lang.ClassLoader.defineClass1(Native Method)
```

`unable to create native thread` and `GC overhead limit exceeded` are not reproduced with a captured trace in this lesson, because the first depends on an operating system's own thread ceiling, which varies by platform and by how a machine is configured, and the second depends on a garbage collector policy decision that is not this stage's subject to demonstrate. Both names are exact and stable regardless: the first always means the JVM asked the operating system for a new native thread and was refused, which is a thread-stack and operating-system-limit problem no matter how large the heap is; the second always means the collector itself gave up on a heap it judged unrecoverable by ordinary means, which is a heap-sizing problem dressed up as a collector complaint. Every row in that table earns its place the same way: it turns "OutOfMemoryError" from a shrug into a pointer at one specific room.

### `StackOverflowError` is a different kind of failure

`StackOverflowError` is not a member of the table above, and treating it as one is the single most common misreading of these two error names. `OutOfMemoryError` means some shared pool, checked from outside the code that happened to trigger it, has nothing left to give any thread that asks. `StackOverflowError` means one specific thread's own stack, a resource that thread alone was using, ran out because that thread's call depth exceeded what was reserved for it; it is thrown by that thread checking its own bound on a call, not by some central arbiter running out of a pool everyone shares. A recursive method with no base case, run and caught rather than left to print a wall of frames, shows exactly that:

```text
StackOverflowError after depth = 32696
```

That depth is one run on one machine, and it is not a constant worth remembering: it moves with the stack size, with how large each frame is, and even between runs of the same program. What matters is that the number exists at all and that it has nothing to do with the heap. Raising `-Xmx` to any number does nothing for that program, because `-Xmx` bounds the heap, and this failure never touched the heap at all; the pool that ran out was the thread's own stack, measured earlier in this lesson at two mebibytes by default. Raising `-Xss` instead buys more call depth before the identical error fires, and it is worth naming the honest cost of reaching for that fix: a stack deep enough that the default limit is genuinely too small for legitimate, bounded recursion is real and occasionally correct to raise, but a stack that only needed to be larger because a base case was missing is not fixed by a bigger stack, it is delayed by one, and every other thread the process creates from then on reserves that same larger amount whether it needs it or not.

## Practice

1. ▢ A container is started with a memory limit of 512 MiB, and the JVM inside it is launched with `-Xmx512m` and no other memory flag. Predict what eventually happens to a service that runs steadily for hours under normal load, and name what actually kills it.

<details markdown="1"><summary>Check</summary>

Sooner or later, metaspace, thread stacks, the code cache, and whatever native or direct memory the service uses add on top of the 512 MiB heap, and the process's total resident memory crosses the container's 512 MiB ceiling even though the heap itself never fills. What kills the process is the container's own out-of-memory mechanism, acting from outside the JVM entirely, not an `OutOfMemoryError`. There is no Java stack trace and no log line the application wrote, because the JVM was never asked to throw anything; it was simply terminated.

</details>

2. ▢ A service adds a `ByteBuffer.allocateDirect` call to a hot path that talks to native code, and never releases the buffers it allocates. Predict which `OutOfMemoryError` variant eventually fires, and say why the heap can look nearly empty on a monitoring dashboard at the same moment it happens.

<details markdown="1"><summary>Hint</summary>

Ask which of the five areas the actual bytes behind `ByteBuffer.allocateDirect` live in, as opposed to the small handle object the calling code holds a reference to.

</details>

<details markdown="1"><summary>Check</summary>

`Direct buffer memory`. The handle object returned by `allocateDirect` is small and lives on the heap, but the bytes it wraps live in native memory, a pool this lesson showed is bounded separately by `-XX:MaxDirectMemorySize`, or by the heap ceiling if that flag is left unset. A dashboard watching heap usage never sees that pool at all, so it can report a heap comfortably under its limit at the exact moment the process is about to throw, because the thing actually running out is not the heap.

</details>

3. ▢ A framework that supports hot reloading recompiles and reloads a class on every request during development, and after a few thousand requests the process throws an `OutOfMemoryError` naming an area that is not the heap. Name it, and say what property of a class, rather than of an ordinary object, makes this area fill up in a way ordinary garbage collection cannot fix by itself.

<details markdown="1"><summary>Check</summary>

`Metaspace`. Each reload defines a brand-new `Class` object with its own metadata, and this lesson showed that metaspace is freed by unloading an entire classloader and everything it defined, not by collecting individual objects one at a time the way the heap is. If anything, a live instance of the old class, a reference to its classloader, or a static field still pointing at it, keeps that classloader reachable, none of that generation's metadata is ever eligible for unloading, and the pool only grows with every reload.

</details>

4. ▢ A method recurses with no base case. Predict whether raising `-Xmx` to a much larger value changes what happens when it runs, then say what does change it and what the honest cost of that change is.

<details markdown="1"><summary>Check</summary>

Raising `-Xmx` changes nothing, because `-Xmx` bounds the heap, and a runaway recursion's failure is on the stack, a separate pool measured in this lesson at two mebibytes per thread by default. Raising `-Xss` does change the outcome, buying more call depth before the identical `StackOverflowError` fires, but at a cost that is easy to miss: that larger reservation applies to every thread the process creates afterwards, not only the one that needed it, so fixing one runaway method this way quietly makes every other thread in the service more expensive to start.

</details>

5. ▢ A service starts a new platform `Thread` for every incoming request instead of using an executor, and a sudden burst sends it ten thousand concurrent requests at once. Predict what fails, name the `OutOfMemoryError` variant, and say what about lesson 27's fix removes this failure as a category rather than merely postponing it.

<details markdown="1"><summary>Check</summary>

Ten thousand platform threads, each reserving this lesson's own measured default of two mebibytes of stack, is already on the order of twenty gibibytes reserved before any of them does a single unit of work, and the operating system also caps how many native threads one process may create; past whichever ceiling is hit first, a request to create another native thread is refused and the JVM reports `OutOfMemoryError: unable to create native thread`. Lesson 27's virtual threads remove the category rather than tuning it, because a virtual thread does not carry that same fixed native stack reservation per unit of concurrency, so ten thousand of them is an unremarkable number rather than a crisis waiting for the next burst.

</details>

## Real-world reps

- [ ] Run `-XX:+PrintFlagsFinal -version` on a machine you administer and read off `InitialHeapSize`, `MaxHeapSize`, `MaxRAMPercentage`, `ThreadStackSize` and `ReservedCodeCacheSize`, noting which are tagged `{ergonomic}` and which are tagged `{default}`.
- [ ] Find a container manifest or deployment configuration for a Java service you run, and check whether the heap flag it passes leaves any headroom below the container's memory limit for metaspace, stacks, the code cache and direct memory.
- [ ] Provoke a `Java heap space` `OutOfMemoryError` yourself on a throwaway program with a deliberately tiny `-Xmx`, and read the exact message and stack trace it prints.
- [ ] Search a service you maintain for `ByteBuffer.allocateDirect` or a native library binding, and check whether `-XX:MaxDirectMemorySize` is set explicitly anywhere in its deployment configuration.
- [ ] Tomorrow: pick one `OutOfMemoryError` variant from this lesson's table that you have never personally seen fire, and write down, before you need it, which area it names and what you would check first.

## Going further

- [The `java` command reference, Oracle](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html): every flag named in this lesson, `-Xmx`, `-Xss`, `-XX:MaxMetaspaceSize`, `-XX:MaxDirectMemorySize`, documented in one place
- [`OutOfMemoryError`, Java SE 25 API documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/OutOfMemoryError.html)
- [`StackOverflowError`, Java SE 25 API documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/StackOverflowError.html)
- [The runtime](../reference/the-runtime.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
