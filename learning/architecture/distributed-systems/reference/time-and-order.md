---
title: Time and Order
description: "What happens-before can and cannot decide, what a Lamport clock refuses to tell you, and the failure-detector vocabulary a timeout is an instance of"
type: reference
---

# Time and Order: Clocks, Causality, and Failure Detection

Stage 2 compressed for lookup. [Lesson 2](../lessons/0002-clocks-and-ordering.md) covers why physical timestamps cannot order events and [lesson 3](../lessons/0003-timeouts-as-failure-detectors.md) covers timeouts as failure detectors; this sheet is the vocabulary and the exact guarantees, for when you are deciding what a system may conclude.

## Happens-before

Written `a -> b`. Defined without reference to physical time at all, by three rules:

| Rule | Reads |
|---|---|
| Program order | `a` and `b` are in the same process and `a` comes first |
| Message order | `a` is the sending of a message and `b` is its receipt |
| Transitivity | `a -> b` and `b -> c` gives `a -> c` |

Two events related by none of these are **concurrent**. That is not ignorance about the order; it is the absence of one. No clock, physical or logical, can supply an answer, because there is nothing to supply.

## Lamport clocks

Each process keeps a counter `C`. Lamport's two implementation rules:

| Rule | What it says |
|---|---|
| IR1 | A process increments its counter between any two successive events |
| IR2 | A sent message carries a timestamp equal to the sender's counter at send; on receipt a process sets its counter greater than both its current value and the received timestamp |

These satisfy the **Clock Condition**: if `a -> b` then `C(a) < C(b)`.

**The converse does not hold, and the paper says so.** Lamport writes that we cannot expect it, "since that would imply that any two concurrent events must occur at the same time". So:

| Question | A Lamport clock answers |
|---|---|
| Did `a` happen before `b`? | No. `C(a) < C(b)` is consistent with `a -> b` **and** with `a` and `b` being concurrent |
| Could `b` have influenced `a`? | Yes, by contrapositive: if `C(a) < C(b)` then `b -> a` is impossible |
| Are `a` and `b` concurrent? | No. Concurrency is exactly what it cannot see |

Reading `C(a) < C(b)` as "a caused b" is the most common way this mechanism is misused, and the counter offers no signal that the reading was wrong.

### When you need the converse, you need vector clocks

| | Lamport clock | Vector clock |
|---|---|---|
| Shape | One integer per process | One integer per process, per process |
| Guarantee | `a -> b` implies `C(a) < C(b)` | `a -> b` **if and only if** `V(a) < V(b)` |
| Detects concurrency | No | Yes: neither vector dominates the other |
| Cost | Constant | Grows with the number of processes, in every message |

Vector clocks are not in Lamport's paper. They arrive later, with Mattern's virtual time among the standard references, and the extra cost is exactly the price of the direction Lamport declined to promise.

### Total order, and what it is worth

A total order can be manufactured by breaking ties on process identifier: order by `C`, then by process. It is consistent with happens-before and it is **arbitrary** wherever the events were concurrent. That is fine for a system that needs *some* agreed order, such as a replicated log, and it is not evidence of causality. Do not report it as one.

## Physical clocks

| Claim | Status |
|---|---|
| Two machines' clocks read the same instant | Never exactly, whatever NTP does |
| Synchronisation can be made exact | No. It runs over the same network whose delay is unbounded |
| A later timestamp means a later event | No, across machines |
| The failure is loud | No. Nothing crashes. An occasional inverted order surfaces only downstream |

## Failure detection

A heartbeat is a timeout applied continuously rather than per request. It does not change what a timeout can know.

### The two ways a detector can be wrong

Chandra and Toueg name them. **Completeness** is about not missing real crashes; **accuracy** is about not crying wolf.

| Property | Definition |
|---|---|
| Strong completeness | Eventually every crashed process is permanently suspected by **every** correct process |
| Weak completeness | Eventually every crashed process is permanently suspected by **some** correct process |
| Strong accuracy | No process is suspected before it crashes |
| Weak accuracy | Some correct process is never suspected |
| Eventual strong accuracy | There is a time after which no correct process is suspected by any correct process |
| Eventual weak accuracy | There is a time after which some correct process is never suspected by any correct process |

**Completeness alone is worthless.** A detector that permanently suspects everything satisfies strong completeness and tells you nothing. Accuracy is what makes a detector informative, and accuracy is the property a real network denies you.

### The eight classes

Two completeness properties by four accuracy properties.

| | Strong accuracy | Weak accuracy | Eventual strong | Eventual weak |
|---|---|---|---|---|
| **Strong completeness** | Perfect, `P` | Strong, `S` | Eventually Perfect, `<>P` | Eventually Strong, `<>S` |
| **Weak completeness** | `Q` | Weak, `W` | `<>Q` | Eventually Weak, `<>W` |

`<>W` is the weakest of the eight, and consensus is still solvable with it. A detector in `<>W` may make an infinite number of mistakes, repeatedly adding and removing correct processes from its suspect list, as long as eventually some correct process stops being suspected.

### The result that reaches into stage 4

Consensus using `S` tolerates **any number** of failures. Consensus using `<>S` requires a **majority of correct processes**, and that requirement is necessary, not an artefact of one algorithm.

That is where stage 4's "every write pays a round trip to a majority" comes from. The majority is not a design preference; it is the price of building on a failure detector that is only eventually accurate, which is the only kind a real network permits.

One more consequence worth carrying: if an application assumes `<>W` and its detector misbehaves continuously, the application may lose **liveness** but not **safety**. Processes may fail to decide; they never decide differently.

### Why detectors exist at all

Consensus is impossible in an asynchronous system with even one faulty process, if the algorithm must always terminate. Failure detectors are the standard way of adding exactly enough assumption to escape that result without pretending the network is synchronous.

## Fixed versus adaptive timeouts

| | Fixed timeout | Accrual detector |
|---|---|---|
| Output | Boolean: trusted or suspected | A **suspicion level on a continuous scale** |
| Threshold | Chosen once, by a human | Chosen by each application, against a scale the detector adjusts to observed conditions |
| Adapts to network | No | Yes |
| Escapes the slow-versus-dead problem | No | No |

The design insight in the accrual approach is the decoupling: the detector reports how abnormal the silence is, and each application decides separately what level justifies acting. A cautious consumer and an aggressive one can then read the same detector.

## What a system may conclude

- From `C(a) < C(b)`: that `b` did not influence `a`. Nothing more.
- From equal or incomparable clocks: that the events are concurrent, and any order you impose is yours, not theirs.
- From a timeout: that a node is **suspected**. Never that it is dead, and never that it is not still processing the request you gave it.
- From a detector that has been silent for a long time: that the probability of abnormality is high, if the detector is accrual, and only that a threshold was crossed otherwise.
- From "the clocks are synchronised to within a few milliseconds": nothing about the order of two events milliseconds apart on different machines.

## Sources

- [Paper: "Time, Clocks, and the Ordering of Events in a Distributed System", Leslie Lamport, 1978](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Paper: "Virtual Time and Global States of Distributed Systems", Friedemann Mattern, 1988](https://www.vs.inf.ethz.ch/publ/papers/VirtTimeGlobStates.pdf)
- [Paper: "Unreliable Failure Detectors for Reliable Distributed Systems", Chandra and Toueg, 1996](https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf)
- [Paper: "Impossibility of Distributed Consensus with One Faulty Process", Fischer, Lynch and Paterson, 1985](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
- [Paper: "The Accrual Failure Detector", Hayashibara, Defago, Yared and Katayama, 2004](https://dspace.jaist.ac.jp/dspace/bitstream/10119/4784/1/IS-RR-2004-010.pdf)
- [Resources](../RESOURCES.md)
