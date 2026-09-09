---
title: 3. Timeouts as Failure Detectors
description: Why every practical failure detector is built on a timeout, and the formal vocabulary for the accuracy-versus-speed trade-off that follows from it
type: lesson
---

# Lesson 3. Timeouts as Failure Detectors

**Mission link:** This is stage 2's capstone. Lesson 1 established that a caller can't distinguish a slow node from a dead one and that a timeout is a guess, not a fact; lesson 2 established that physical time can't even give two machines a shared notion of "when." This lesson is what a real system actually builds on top of both facts: a failure detector, and the formal terms for what it can and can't promise.
**Primary source:** [Paper: "Unreliable Failure Detectors for Reliable Distributed Systems", Chandra and Toueg, 1996](https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf)
**Prerequisites:** [Lesson 2](0002-clocks-and-ordering.md), [Timeout](../GLOSSARY.md)

## Warm-up

1. ▢ Why can't a timestamp from one machine be compared to a timestamp from another machine to determine which event happened first?

<details markdown="1"><summary>Check</summary>

Physical clocks on different machines drift apart between synchronizations, and synchronizing them at all depends on the same unpredictable network delay that causes partial failure, so a lower timestamp on one machine doesn't reliably mean its event happened first relative to an event on another machine.

</details>

2. ▢ What does the happens-before relation let you conclude about two events with no message chain connecting them and on different processes?

<details markdown="1"><summary>Check</summary>

That they're concurrent: there is no fact about which "really" happened first, and no clock, logical or physical, can manufacture one where none exists.

</details>

## Know this

### A heartbeat is just a repeated timeout, made systematic

Real systems rarely wait for one single request to time out before declaring a node dead; instead, they run a **heartbeat**: node A pings node B on a fixed interval, and if B misses enough consecutive pings (or one ping past some window), A marks B suspected. This is the same timeout decision from lesson 1, just applied continuously and automatically instead of per-request. It doesn't change the underlying problem: A still cannot distinguish "B is dead" from "B, or the network between A and B, is just slow right now."

### Completeness and accuracy: naming the two ways a detector can be wrong

Chandra and Toueg's paper gives this trade-off precise names. A failure detector has **completeness** if it eventually suspects every process that actually crashes (it doesn't miss real failures forever), and **accuracy** if it doesn't suspect a process that hasn't actually crashed (it doesn't cry wolf). The paper's central, somewhat startling result: you don't need perfect accuracy to solve consensus (stage 4). A failure detector that's allowed to make infinitely many mistakes, as long as it eventually stops suspecting a process that's actually still alive, is still enough to build correct systems on. This is the formal version of "we don't need a perfect answer, we need a good enough one, used correctly."

![A plot with accuracy on the horizontal axis and completeness on the vertical axis. The top-left region, high completeness and low accuracy, is a detector that suspects everyone constantly, catching every real failure but crying wolf. The bottom-right region, high accuracy and low completeness, is a detector that never suspects anyone, never crying wolf but missing real failures. The top-right corner, both high, is the impossible perfect detector. A marked point sits near the top-right but short of the corner, labeled real failure detectors: eventually accurate, where practical systems actually live.](images/completeness-vs-accuracy.svg)

### Fixed timeouts assume a distribution; adaptive ones estimate it

A fixed timeout value (`assume dead after 5 seconds of silence`) is really a bet on the shape of normal network and processing delay: too aggressive for a network with occasional long tails, too lax for one that's normally very fast. **Adaptive failure detectors** (the phi accrual detector, used by Cassandra and Akka, is a well-known example) instead track the recent history of heartbeat arrival times and continuously estimate the probability that "no heartbeat yet" is actually abnormal, rather than committing to one fixed cutoff. This doesn't escape lesson 1's fundamental limit, slow and dead are still indistinguishable in principle, but it does let a system's suspicion threshold track the network's actual, currently-observed behavior instead of a number picked once and left alone.

### Why this closes stage 2 and opens stage 4

Every consistency model (stage 3) and every consensus protocol (stage 4) has to be designed around the fact that failure detection is, at best, eventually accurate, never perfectly accurate in real time. Chandra and Toueg's result is exactly why consensus protocols like Raft don't try to solve "tell me for certain who's alive right now"; they're built to make progress correctly despite never being able to solve that problem, using a failure detector that's allowed to be wrong for a while as one of their building blocks.

## Practice

1. ▢ How does a heartbeat mechanism relate to the single-request timeout described in lesson 1?

<details markdown="1"><summary>Check</summary>

A heartbeat is the same timeout decision, applied repeatedly and automatically at a fixed interval instead of to one specific request; missing enough consecutive heartbeats triggers the same "assume dead" decision lesson 1 described, with the same underlying inability to distinguish slow from dead.

</details>

2. ▢ Define completeness and accuracy for a failure detector, and explain why a detector can have one without the other.

<details markdown="1"><summary>Hint</summary>

Consider a detector that suspects everyone, all the time, versus one that never suspects anyone at all.

</details>

<details markdown="1"><summary>Check</summary>

Completeness means the detector eventually suspects every process that actually crashes; accuracy means it doesn't suspect a process that hasn't crashed. A detector that suspects every process constantly has perfect completeness (it will suspect any real crash) but terrible accuracy (it constantly cries wolf); a detector that never suspects anyone has perfect accuracy but zero completeness (it will never catch a real crash). Real detectors sit somewhere between these extremes.

</details>

3. ▢ What's the surprising part of Chandra and Toueg's result about failure detectors that make infinitely many mistakes?

<details markdown="1"><summary>Check</summary>

That consensus can still be solved with such a detector, as long as it's eventually accurate (it eventually stops suspecting processes that are actually still alive), even though it's allowed to be wrong arbitrarily many times before that point. A failure detector doesn't need to be perfectly accurate, or even accurate for a bounded period, to be a usable building block.

</details>

4. ▢ Contrast a fixed timeout with an adaptive (phi accrual-style) failure detector. Does the adaptive version solve the slow-versus-dead ambiguity from lesson 1?

<details markdown="1"><summary>Check</summary>

A fixed timeout commits to one cutoff value regardless of actual network conditions, a bet on the typical shape of delay. An adaptive detector tracks recent heartbeat arrival history and continuously estimates the probability that the current silence is abnormal, letting its suspicion threshold track observed behavior instead of a static guess. It does not solve the ambiguity: slow and dead remain indistinguishable in principle; it only makes the practical trade-off track real conditions rather than a number chosen once in advance.

</details>

5. ▢ Which claim correctly connects this lesson to stage 4 (consensus)?

    - a) Consensus protocols require a failure detector with perfect accuracy to work correctly
    - b) Consensus protocols are designed to make progress correctly despite relying on failure detectors that are only eventually, not immediately, accurate
    - c) Adaptive failure detectors eliminate the need for consensus protocols entirely
    - d) Completeness and accuracy are the same property described two different ways

<details markdown="1"><summary>Check</summary>

**b)** That's exactly Chandra and Toueg's bridge into consensus: protocols like Raft are built around an eventually-accurate, not perfectly-accurate, failure detector. (a) is false: their result explicitly shows consensus is solvable with a detector allowed infinitely many mistakes. (c) is false: adaptive detectors are a better practical instance of the same imperfect detector, not a replacement for the coordination problem consensus solves. (d) is false: they're independent properties, as the always-suspect and never-suspect extremes in question 2 show.

</details>

## Real-world reps

- [ ] Find a heartbeat or health-check mechanism in a system you have access to (a cluster manager, a service mesh, a database's replica health check). Identify whether its timeout is fixed or adaptive, and if fixed, what value was chosen and whether anyone can say why.
- [ ] For that same mechanism, think through what a false suspicion (declaring a healthy-but-slow node dead) would actually trigger in that system, and how costly that would be compared to a missed real failure.
- [ ] Tomorrow: read the primary source's definitions of completeness and accuracy in full, including the different accuracy variants (strong, weak, eventual) it defines, and note which one seems closest to what a heartbeat-based system in practice actually achieves.

## Going further

- [Paper: "Unreliable Failure Detectors for Reliable Distributed Systems", Chandra and Toueg, 1996](https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf)
- [Paper: "Time, Clocks, and the Ordering of Events in a Distributed System", Leslie Lamport, 1978](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
