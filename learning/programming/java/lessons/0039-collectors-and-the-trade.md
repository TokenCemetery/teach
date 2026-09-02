---
title: 39. Collectors and the Trade You Are Making
description: Five collectors, one three-way trade, and why the default is usually the right answer
type: lesson
---

# Lesson 39. Collectors and the Trade You Are Making

**Mission link:** Owning a Java service in production means the collector running underneath it is a decision made once from what the service actually needs, a latency target, a throughput target or a memory budget, rather than a default nobody looked at until a pause shows up in an incident report.
**Primary source:** [HotSpot Virtual Machine Garbage Collection Tuning Guide, Release 25](https://docs.oracle.com/en/java/javase/25/gctuning/index.html)
**Prerequisites:** [Lesson 36](0036-where-memory-goes.md), [Lesson 38](0038-the-allocation-that-never-happened.md)

## Warm-up

Lesson 38 showed a `Point` that never had to be allocated at all: scalar replacement deleted it before it ever became a collector's problem. If every allocation a program made could be eliminated that way, would there be anything left for a garbage collector to do?

<details markdown="1"><summary>Check</summary>

Some, and it would be the residue left on purpose. A collector's job is to find what is still reachable and reclaim or relocate everything else, and removing an allocation removes that object from the job entirely, for good, under every collector at once, because a scalar-replaced object never existed for any of them to trace. What is left is whatever genuinely escapes: a result handed back across a real boundary, an object kept in a cache or a collection, anything with an actual reason to outlive the method that made it. That residue is real, it is unavoidable in any program that does more than arithmetic on scalars, and five collectors on the current release offer five different answers to the trade of handling it. That trade is this lesson.

</details>

## Know this

### The trade you cannot escape

Every garbage collector is answering the same three questions, and no collector answers all three well at the same time. Throughput is how much of the machine's time goes to running the program rather than collecting after it. Pause time is how long any single collection is allowed to stop the program for. Footprint is how much memory the collector needs beyond the objects themselves, the bookkeeping it carries to do its job. These three trade against each other for structural reasons, not because nobody has written a clever enough collector yet. More throughput usually means doing more work in fewer, larger pauses rather than spreading it thin, which costs pause time. A short pause usually means moving work off the stop-the-world path onto concurrent threads, which needs extra bookkeeping to keep a moving program and a moving collector from corrupting each other, and that bookkeeping costs footprint. Minimal footprint usually means simpler, less concurrent machinery, and simple machinery earns its simplicity by stopping the program to work safely, which costs pause time again. There is no collector that maximises all three, because the extra work any collector does to buy one of them has to be paid for out of one of the other two. What you actually choose is not a collector in the abstract, but which two of throughput, pause time and footprint matter for this particular service, and the collector follows from that choice.

| Collector | Optimises for | Pays for it in | Right for |
|---|---|---|---|
| Serial | footprint and simplicity | throughput and pause both scale with heap size, with nothing spent hiding it | a heap small enough, or a machine constrained enough, that the other two never come up |
| Parallel | throughput | pause time, fully stop-the-world, sized to how much garbage accumulated | batch and offline work where nobody is waiting on any specific moment |
| G1 | a balance of all three | the best case in any single one of them, since it is not trying to win any of them outright | the default: a service with no unusual requirement pulling it toward one corner |
| ZGC | pause time, independent of heap size | footprint, for the concurrent bookkeeping that keeps pauses short regardless of how large the heap grows | large heaps under a hard latency ceiling |
| Shenandoah | pause time, independent of heap size | footprint, by a different concurrent mechanism aimed at the same target as ZGC | the same latency requirement as ZGC, chosen after measuring both against the real workload |

All five are present and accepted on the current long-term-support release, and asking for any of them by name is enough to confirm that for yourself: none of the five collector flags produces an error on this release.

### Serial: the collector for when there is barely anything to collect

Serial does exactly what its name says: one thread does all of the collecting, and the program stops completely while it happens. That sounds like a strictly worse deal than every other row in the table, and for most services it is, but "most services" is not every workload. A short-lived command-line tool, a small script that runs for a few seconds and exits, or a process confined to a single processor inside a small container never gets far enough into its own heap for a stop-the-world pause to be a problem, and it never has a second core sitting idle for a concurrent collector to use anyway. Paying for G1's region bookkeeping or ZGC's concurrent machinery there buys nothing, since there is no throughput headroom or pause budget being protected by any of it. Serial is right exactly when the other two corners of the trade are not being fought over, because the workload is too small or too constrained for them to matter.

### Parallel: throughput first, and nobody is watching the clock

Parallel uses every available processor to collect, but it still stops the program completely while doing it, so a collection pause under Parallel scales with how much garbage has piled up and how large the heap has grown. That is a real cost, and Parallel does not hide it or spread it out the way the concurrent collectors do. What it buys in exchange is throughput: every cycle not spent on concurrent bookkeeping is a cycle spent finishing the actual work sooner, and a batch job, a nightly reprocessing pass, or an offline pipeline has no client waiting on any particular millisecond of it. For that shape of workload a longer pause costs nothing that matters, because nothing is measuring the wait, and Parallel converts every part of the machine that a concurrent collector would spend keeping a pause short into work that gets the whole job done faster instead.

### G1: the default, and what `{ergonomic}` actually means

G1 is what an unflagged JVM on a server-class machine runs, and it does not report itself the way a hardcoded value would. Asking the JVM to print its own flags shows this:

```text
bool UseG1GC = true {product} {ergonomic}
```

`{ergonomic}` is a different claim from `{default}`. A `{default}` value is the same number regardless of the machine it runs on. An `{ergonomic}` value is one the JVM worked out at startup by looking at the actual machine underneath it, its processor count and the memory it can see, the same mechanism lesson 36 already showed picking `MaxRAMPercentage` and the heap size limits. Nobody typed `-XX:+UseG1GC` for this to happen; the runtime looked at what it was given and decided G1 fit a machine shaped like that one, which is also why the same unflagged program can end up on a different collector on a genuinely different machine, such as one small enough that the ergonomic choice lands on Serial instead.

G1 earns that ergonomic slot on ordinary hardware for the reason the row above states: it is not trying to win throughput, pause time or footprint outright, it is trying not to be bad at any of them. It collects incrementally, in regions, mostly in short pauses classified as ordinary young collections, rather than in the rare, large, whole-heap pauses a simpler collector eventually needs. For an ordinary request-driven service with no stated latency ceiling below what G1 already delivers, and no memory budget tight enough to notice its bookkeeping, nothing pulls the choice toward any other row, which is exactly the case the ergonomic default is built for. How much of a real run's wall-clock time G1's own collections actually cost is a question a garbage collection log answers precisely, and reading one is lesson 40's job rather than this one's; the fact worth keeping from here is only that the default collector is the one built to make that number small without anyone having to ask it to.

### ZGC and Shenandoah: buying pause time independent of heap size

G1's pauses still grow, a little, with the size of what they have to walk. ZGC and Shenandoah exist to break that relationship entirely: both target pauses on the order of a millisecond or less, and both hold that target whether the heap is a few hundred megabytes or hundreds of gigabytes, by moving almost all of the collection work onto concurrent threads that run alongside the program rather than stopping it. Making that safe, when the program can be mutating an object graph a concurrent thread is simultaneously relocating, needs extra machinery on every access, and that machinery is exactly the footprint the earlier table charges both collectors for. A concurrent collector is not a free upgrade over G1; it is a different point on the same trade, one that has decided pause time is worth paying footprint for.

That makes the choice between them a genuine requirement, not a preference. A service with a hard latency ceiling on a large heap, one where a request stalling for tens of milliseconds during a collection is a failure rather than an inconvenience, is the workload both collectors exist for. A service with no such ceiling gets nothing from either beyond the footprint bill, since G1 already keeps its pauses short enough that nobody downstream notices. Between ZGC and Shenandoah specifically, neither is the ergonomic default anywhere, so reaching for either is already deliberate, and the honest way to choose between the two is to measure both against the real workload rather than pick from reputation, since they reach the same pause-time target by different concurrent mechanisms and the difference between them on any given service is an empirical question this lesson cannot answer in the abstract.

### ZGC has no mode to choose anymore

ZGC used to have two shapes, and older material on it, written for an earlier release, is generally describing a choice that no longer exists. A newer, generational mode was introduced as something you opted into, and for a stretch of releases the flag that turned it on was worth knowing about. As of the current long-term-support release, that opt-in is gone because the choice is gone: generational is the only mode ZGC runs in, following JEP 490, which removed the older non-generational mode outright. Passing the flag that used to enable it does not fail loudly. It does this:

```text
OpenJDK 64-Bit Server VM warning: Ignoring option ZGenerational; support was removed in 24.0
```

and then the program runs anyway, on ZGC's only remaining mode. That is worth sitting with a moment longer than the fact itself deserves, because of what it demonstrates rather than what it says: a flag from a two-year-old article, copied into a startup script without checking it against the release actually in hand, does not stop the process or raise an error a reader would notice in a log they were not watching closely. It is silently ignored, with a warning that only tells you something if you already know to look for it. The lesson underneath the JEP is not really about ZGC. It is that any piece of version-sensitive advice about the runtime, a flag, a tuning number, a claim about what a collector does by default, is a claim about a specific release, and the only way to know whether it still holds is to run it against the release you are actually shipping.

### Choosing from the requirement, not the benchmark

None of the last three sections are a ranking. The right way to pick a collector starts from a sentence about the service, not from a chart someone else published running someone else's workload on someone else's hardware. If the sentence is a latency target, a percentile of request time that must not be blown past, ZGC and Shenandoah are the candidates, and the requirement tells you how to verify the choice: measure the tail latency you actually care about, under the real load shape, on both, before committing. If the sentence is a throughput target with nobody waiting on any single response, Parallel is the candidate, and the measurement is simply how long the whole job takes end to end. If the sentence is a memory budget tight enough that a collector's own bookkeeping competes with the program for space, Serial is worth considering on a small heap, and G1 before either concurrent collector on anything larger. If there is no unusual sentence at all, if nothing pulls the service toward one corner of the trade, the ergonomic default already is the answer, and the case for moving off it has to be made by a stated requirement the default is failing to meet, not by an article that measured a different workload on different hardware. However you would confirm any of this against a real, running instance of the service, a collection log is where that confirmation lives, and reading one is exactly what the next lesson teaches.

### The order of leverage

Three moves are available once a collector is on the table, and they are not the same size. Tuning a single collector's own flags, region sizes, concurrent thread counts, the individual knobs the tuning guide documents one by one, is the smallest of the three: it adjusts how that one collector spends the budget it already has, and it cannot change what the budget is. Changing which collector runs at all is a bigger lever, because Serial, Parallel, G1, ZGC and Shenandoah are not five settings on one machine, they are five different algorithms making five different structural bets about where the cost of collection should land, and moving between them changes what is achievable in a way no flag on any single one of them can. Neither lever is as big as not allocating in the first place. Lesson 38 already measured that at the smallest possible scale: one field store, nothing else about the method changed, took an operation from allocating nothing at all to allocating the full object every time. An allocation removed is removed for every collector at once and forever, where changing collector only changes how whatever garbage still exists gets handled. The honest close: pick the collector from the requirement, tune it only after a measurement says it is actually the bottleneck, and before either, ask what is being allocated that does not need to be, because that question, not a flag or a product name, is usually where the largest win in the whole trade is sitting. Finding that answer is a profiling exercise, and profiling is where this stage goes next rather than where this lesson can take you.

## Practice

1. ▢ A command-line tool starts, reads a small file, does a few seconds of work, and exits, running inside a container capped at one processor and a few hundred megabytes of memory. Predict which collector answers this workload's actual requirement, and name which corner of the trade it is buying.

<details markdown="1"><summary>Check</summary>

Serial. It is buying footprint and simplicity, and it can afford to, because the other two corners were never in contention here: the heap is small enough that even a full stop-the-world pause is short in absolute terms, and there is only one processor available, so paying for G1's regions or a concurrent collector's bookkeeping would spend memory and complexity on a benefit this workload has no second core to realise.

</details>

2. ▢ A nightly job reprocesses a large table for several hours with no client waiting on any single moment of it. Predict which collector, and explain why sacrificing pause time here is not actually a sacrifice.

<details markdown="1"><summary>Check</summary>

Parallel. It buys throughput by using every processor to collect, at the cost of pause time, fully stop-the-world and scaling with the heap. That cost is not felt because nothing is measuring the wait: with no request-response boundary and no percentile anyone tracks, every processor cycle that a concurrent collector would have spent on bookkeeping to keep pauses short is, under Parallel, a cycle spent finishing the job sooner instead, which is the only thing this workload's requirement actually asks for.

</details>

3. ▢ Printing the JVM's own flags on an ordinary multi-core server with nothing set on the command line shows `bool UseG1GC = true {ergonomic}`. A colleague reads this as proof that someone on the team deliberately chose G1 for this service. Are they right, and what would `{default}` instead of `{ergonomic}` have told you that this tag does not?

<details markdown="1"><summary>Check</summary>

No, not as stated: `{ergonomic}` means the JVM examined the machine it found itself running on, its processor count and available memory, and picked G1 itself at startup, the same mechanism lesson 36 showed choosing the heap size limits. Nobody had to type a collector flag for that to happen, so there is no record here of a deliberate decision, only of a machine shape the runtime judged suited to G1. `{default}` would have meant something different and more useful to know before moving hardware: a fixed value the JVM would report the same way regardless of the machine, where `{ergonomic}` warns you the same unflagged command could report something else entirely on a smaller or larger machine.

</details>

4. ▢ Predict what happens when `-XX:+ZGenerational` is passed alongside `-XX:+UseZGC` on the current long-term-support release, then explain why an article's instruction to add that flag should not be followed as written.

<details markdown="1"><summary>Hint</summary>

That flag existed to opt into a mode that, at the time most articles about it were written, was not the only mode ZGC had. Ask what an "opt in" flag is worth once the thing it opts into becomes the only option there is.

</details>

<details markdown="1"><summary>Check</summary>

It prints `OpenJDK 64-Bit Server VM warning: Ignoring option ZGenerational; support was removed in 24.0` and then runs anyway, on ZGC's only remaining mode, generational, because JEP 490 removed the non-generational mode the flag used to select between. The instruction should not be followed as written because it is not wrong so much as obsolete: it was written for a release where generational ZGC was something to opt into, and running it unchanged against a later release does not fail loudly, it gets silently ignored with a warning a reader who is not watching the log closely will never see, which is exactly why version-sensitive advice needs checking against the release actually in hand rather than trusting that it aged as well as the rest of the article.

</details>

5. ▢ A service's own collection log later confirms the collector accounts for a small share of the program's wall-clock time. A teammate proposes spending the next sprint tuning G1's region size and concurrent thread count flags. Using the order of leverage from this lesson, what question comes before agreeing to that sprint, and what is probably the bigger opportunity being skipped?

<details markdown="1"><summary>Check</summary>

The question is whether the collector is even close to being the bottleneck, and the scenario already answers it: a small share of wall-clock time means even a perfect collector could only win back that same small share, so a sprint spent on region sizes and thread counts is the smallest of three levers spent on the part of the program that was never the problem. The bigger opportunity being skipped is almost certainly allocation itself: lesson 38 showed that a single field store can turn a call that allocates nothing into one that allocates the full object every time, and removing an unnecessary allocation shrinks the collector's job for every collector at once, permanently, in a way no flag on any one collector can. Finding which allocations in this program are worth removing is a profiling question rather than a tuning-flag question, and that is the sprint worth proposing instead.

</details>

## Real-world reps

- [ ] Run the flag-printing check from this lesson against a JVM you actually operate, and find whether it reports `UseG1GC`, `UseZGC`, or something else as `{ergonomic}`, then ask whether that choice matches what the service actually needs rather than assuming it does.
- [ ] For one real service you run or maintain, write one sentence each naming which two of throughput, pause time and footprint it actually needs, before opening a tuning guide or changing a single flag.
- [ ] If you have ever seen `-XX:+ZGenerational` in a script, a runbook or an article, try it against a current release and read the exact warning it now produces, rather than trusting whatever told you to add it.
- [ ] Tomorrow: find one collector-tuning recommendation you have seen repeated, a blog post, a forum answer, a colleague's advice, and check whether it names the release it was written for, and whether that release still behaves the way it describes.
- [ ] Before your next conversation about a service's performance, ask whether its collector was ever chosen from a stated requirement, or simply inherited from whatever the JVM defaulted to the first time someone ran it.

## Going further

- [The Garbage Collection Handbook](https://gchandbook.org/): the theory behind the three-way trade this lesson only names and puts to work
- [JEP 490: ZGC, Remove the Non-Generational Mode](https://openjdk.org/jeps/490): the change behind the warning this lesson ran and read
- [HotSpot Virtual Machine Garbage Collection Tuning Guide, Release 25](https://docs.oracle.com/en/java/javase/25/gctuning/index.html): the primary source's own collector-by-collector detail, worth reading in full once a requirement points at one row of the table
- [The runtime](../reference/the-runtime.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
