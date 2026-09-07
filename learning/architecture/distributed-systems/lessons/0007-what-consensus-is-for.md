---
title: 7. What Consensus Is For
description: The replicated-state-machine problem consensus protocols solve, and why it's the mechanism underneath a linearizable system's coordination
type: lesson
---

# Lesson 7. What Consensus Is For

**Mission link:** Stage 4 opens consensus. Lesson 5 established that linearizability requires coordination to maintain a single agreed order; this lesson names the actual problem, replicated state machines, that a consensus protocol solves to provide that coordination, before lesson 8 covers Raft's specific mechanism and lesson 9 covers what it costs.
**Primary source:** [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
**Prerequisites:** [Lesson 6](0006-sequential-and-eventual-consistency.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ State sequential consistency's guarantee, and what it drops relative to linearizability.

<details markdown="1"><summary>Check</summary>

Sequential consistency requires all operations to appear in some single, total order that every client agrees on, with each client's own operations appearing in that order in the sequence it issued them, but it drops linearizability's requirement that this order match real, wall-clock time.

</details>

2. ▢ For a distributed lock and a social media "like" count, which consistency model does each actually need, and why?

<details markdown="1"><summary>Check</summary>

A distributed lock needs linearizability: two clients ever observing the lock as free at the same time is a genuine correctness failure. A like count can tolerate eventual consistency: a temporarily stale or differently-ordered count across replicas is invisible and self-correcting, not a correctness failure for that use case.

</details>

## Know this

### The replicated state machine: the actual problem being solved

A **replicated state machine** is a collection of servers that each maintain an identical copy of some data and process the same sequence of commands in the same order, so that as long as they start in the same state, they stay in the same state. This is how a system provides linearizability, or any single-agreed-order guarantee, in the presence of the partial failure and imperfect failure detection from stages 1 and 2: instead of one server holding the only copy (a single point of failure), multiple servers hold copies, and consensus is precisely the mechanism that gets them to agree on the *order* of commands despite crashes, message loss, and the impossibility of perfectly distinguishing a slow server from a dead one.

### Why "just have every server agree" is the hard part

If message delivery were instant and reliable and servers never crashed, replicated state machines would be trivial: broadcast every command to every server in the order it arrived, done. Consensus is hard specifically because none of that holds: messages can be delayed, reordered, or lost; servers can crash and restart; and a server proposing "the next command is X" has to get the others to actually agree on X, even when some servers are unreachable, without ever letting two servers commit *different* commands to the same slot in their sequence. A consensus protocol's job is producing exactly one agreed value per decision, safely, even under all of stage 1 and 2's failure modes, while still making forward progress most of the time.

### Consensus and linearizability: the client-facing promise built on an internal one

A linearizable key-value store, for instance, is typically built by running a replicated state machine underneath it: every write is a command, consensus gets every replica to agree on the order commands are applied in, and the system exposes that agreed, ordered sequence to clients as a single, coherent history. The client-facing guarantee from lesson 5 (a single real-time-consistent order) is implemented by the internal guarantee this lesson names (replicas agreeing on a single order of commands). Consensus is the load-bearing mechanism most systems reach for when they need lesson 5's guarantee and can't get it for free.

### What a consensus protocol has to promise, at minimum

Regardless of the specific protocol (lesson 8 covers Raft specifically), any consensus algorithm has to guarantee **safety** (never two different values decided for the same slot, even under network partitions, message delays, or reordering) and, under reasonable conditions, **liveness** (the system does eventually make progress, deciding new values, once enough of the network is behaving well enough). Safety is absolute, it must hold no matter how badly the network behaves; liveness is conditional, since the FLP impossibility result (not covered here) shows no protocol can guarantee progress under fully arbitrary asynchronous conditions, which is why liveness is stated as "eventually, under reasonable behavior" rather than "always."

## Practice

1. ▢ Define a replicated state machine, and explain what problem it exists to solve.

<details markdown="1"><summary>Check</summary>

A replicated state machine is a set of servers each holding an identical copy of some data, processing the same sequence of commands in the same order so their states stay identical. It solves the single-point-of-failure problem of having only one server hold the authoritative copy, by having multiple servers hold copies that stay in agreement.

</details>

2. ▢ Why would replicated state machines be trivial if messages were instant, reliable, and servers never crashed? What specifically makes them hard in practice?

<details markdown="1"><summary>Hint</summary>

Think about what stage 1 and stage 2 already established about networks and failure detection.

</details>

<details markdown="1"><summary>Check</summary>

Without failure or delay, a single broadcast of each command in order would keep every server in sync trivially. It's hard in practice because messages can be delayed, reordered, or lost (partial failure, lesson 1), servers can crash, and no server can be certain another has actually failed rather than merely being slow (lesson 3), so getting every server to agree on the same order without ever letting two servers commit different values to the same slot requires real coordination machinery.

</details>

3. ▢ How does consensus relate to providing linearizability (lesson 5) in a typical system?

<details markdown="1"><summary>Check</summary>

A linearizable system is typically built on top of a replicated state machine: consensus gets every replica to agree on the order in which write commands are applied, and that internally-agreed order is what the system exposes to clients as a single, real-time-consistent history. Consensus is the internal mechanism; linearizability is the client-facing guarantee it enables.

</details>

4. ▢ Distinguish safety from liveness for a consensus protocol, and explain why one is described as absolute and the other as conditional.

<details markdown="1"><summary>Check</summary>

Safety means the protocol never decides two different values for the same slot, and this must hold unconditionally, no matter how badly the network behaves, since violating it means the replicated state machines have actually diverged. Liveness means the system eventually makes progress, deciding new values, but this is only guaranteed under reasonable conditions (the network isn't behaving in a fully arbitrary, worst-case way forever), which is why it's stated conditionally rather than as an absolute promise.

</details>

5. ▢ Which claim correctly describes what a consensus protocol is for?

   - a) It eliminates the need for replicated state machines by removing the requirement to keep multiple servers in the same state
   - b) It gets multiple servers to agree on the order of commands despite crashes and message loss, providing the internal coordination that a client-facing guarantee like linearizability is built on
   - c) It guarantees the system always makes progress deciding new values, regardless of network conditions
   - d) It only matters for systems that don't need linearizability

<details markdown="1"><summary>Check</summary>

**b)** That's precisely the replicated-state-machine problem consensus solves, and its relationship to linearizability from lesson 5. (a) is false: consensus exists specifically to keep replicated state machines agreeing, not to remove the need for replication. (c) is false: liveness is conditional, not absolute, per the FLP-adjacent reasoning in this lesson. (d) is false: consensus is exactly the mechanism most systems reach for when they do need linearizability or a similarly strong guarantee.

</details>

## Real-world reps

- [ ] Find a system you know of that uses a consensus protocol internally (a coordination service, a distributed database's replication layer, a cluster leader-election mechanism). Identify what specific decision it uses consensus to agree on (a leader, a commit order, a configuration value).
- [ ] For that same system, check whether its documentation frames its guarantee in terms of safety versus liveness, or conflates the two; note which failure it would treat as the more serious one.
- [ ] Tomorrow: read the primary source's introduction and motivation section in full, and note the specific criticism of Paxos (an earlier consensus protocol) that motivated Raft's design toward understandability.

## Going further

- [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
- [Site: "The Raft Consensus Algorithm", raft.github.io](https://raft.github.io/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
