---
title: 9. What Consensus Costs
description: Why every write pays a round trip to a majority, why a minority partition loses availability rather than consistency, and how to weigh that cost against what consensus buys
type: lesson
---

# Lesson 9. What Consensus Costs

**Mission link:** This is stage 4's capstone. Lessons 7 and 8 covered what consensus is for and how Raft provides it; this lesson is the actual cost, in latency and availability, and closes the mission's third success criterion: explaining what a consensus protocol buys and what it costs, without needing to prove its correctness from first principles.
**Primary source:** [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
**Prerequisites:** [Lesson 8](0008-raft-leader-election-and-log-replication.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ Why does Raft require only a majority, not unanimity, to elect a leader or commit a log entry?

<details markdown="1"><summary>Check</summary>

Requiring unanimity would let a single unreachable or crashed server block the entire cluster from making progress. A majority requirement lets the cluster keep working as long as more than half its servers can communicate, tolerating the rest being slow, partitioned, or down.

</details>

2. ▢ What specifically stops a stale, partitioned-away leader from causing a conflicting write once it reconnects?

<details markdown="1"><summary>Check</summary>

The term number: any message from the stale leader carries its old, lower term, and any follower or server that has already moved on to a higher term rejects it. The stale leader discovers a higher term as soon as it communicates with anyone from the new one and steps down.

</details>

## Know this

### The latency cost: every write waits for a majority round trip

A client write isn't committed, and can't be safely reported as successful, until the leader confirms a majority of the cluster has durably stored it (lesson 8). This means every write pays at least one network round trip to enough other servers to form a majority, even when nothing is failing: consensus trades raw write latency for the safety guarantee that a committed write survives the crash of any minority of servers. A single-node system, with no such requirement, is always faster for a plain write; that speed is exactly what consensus gives up to get its guarantee.

### The availability cost: a minority partition can't make progress, on purpose

If a network partition splits the cluster such that no side has a majority, the side without one cannot elect a leader, and the side that does have one keeps working normally. This isn't a bug to be fixed; it's the direct, intended consequence of the safety property from lesson 8: allowing the minority side to also elect its own leader and keep accepting writes would let both sides commit conflicting entries, exactly the split-brain the majority requirement exists to prevent. A minority partition loses availability specifically so the majority side's guarantee stays intact.

![A five-node cluster is split by a network partition into a group of three nodes and a group of two nodes. The group of three is a majority of the original five, so it can still elect a leader and commit writes normally. The group of two is not a majority, so it cannot elect a leader or commit anything at all, and correctly stays unavailable rather than risk a conflicting decision with the other side.](images/majority-partition-availability.svg)

### This is CAP's trade-off, concretely mechanized

Lesson 4 described CAP's conditional choice: during an actual partition, a system prioritizing consistency refuses to answer rather than risk a stale or conflicting response. Consensus is the concrete mechanism that makes this real: the minority side of a partition isn't merely "choosing" unavailability in the abstract, it structurally cannot elect a leader or commit anything, because it cannot assemble a majority. What CAP describes as a trade-off, Raft (and any majority-based consensus protocol) enforces as a hard mechanical consequence of its safety requirement.

### Weighing the cost: what justifies paying it

Consensus is worth its latency and availability cost specifically when a system needs the guarantee lesson 8 provides, a single agreed order that survives the crash of a minority of servers, the same guarantee a linearizable system (lesson 5) needs underneath it. A leader-election mechanism for a cluster manager, a configuration store multiple services must agree on, or a lock service where two conflicting grants would be a real correctness failure are all worth this cost. A system that only needs eventual consistency (lesson 6), where a temporarily stale or diverging answer is tolerable, doesn't need consensus's cost at all: paying for a majority round trip on every write to protect an invariant nothing actually depends on is waste, not safety.

## Practice

1. ▢ Why does every committed write in a consensus-based system pay at least one network round trip, even when nothing is failing?

<details markdown="1"><summary>Check</summary>

Because a write can't be safely reported as committed until the leader has confirmed that a majority of the cluster has durably stored it, which requires sending the entry out and waiting for enough acknowledgments to form a majority, regardless of whether every server happens to be healthy at that moment.

</details>

2. ▢ A five-node Raft cluster is split by a partition into a group of two and a group of three. Which group, if either, can keep electing a leader and committing writes, and why?

<details markdown="1"><summary>Hint</summary>

Consider which group, if either, can assemble a majority of the original five-node cluster.

</details>

<details markdown="1"><summary>Check</summary>

The group of three can keep working: three out of five is a majority, so it can elect a leader and commit entries normally. The group of two cannot: two out of five is not a majority, so it structurally cannot elect a leader or commit anything, and correctly stays unavailable rather than risk a conflicting decision.

</details>

3. ▢ Why is a minority partition's loss of availability described as intended rather than a bug?

<details markdown="1"><summary>Check</summary>

Because allowing the minority side to also elect a leader and accept writes would let two sides of the same cluster commit conflicting entries, exactly the split-brain scenario the majority requirement exists to prevent. Losing availability on the minority side is the direct, necessary price of keeping the safety guarantee intact everywhere.

</details>

4. ▢ How does consensus turn CAP's abstract consistency-versus-availability trade-off (lesson 4) into something mechanically enforced rather than a policy choice?

<details markdown="1"><summary>Check</summary>

A system relying on majority-based consensus doesn't merely choose to refuse requests during a partition as a policy; the minority side structurally cannot assemble the majority required to elect a leader or commit an entry at all. The unavailability isn't a decision made under pressure, it's a direct, mechanical consequence of the safety property requiring majority agreement.

</details>

5. ▢ Which claim correctly weighs when consensus's cost is worth paying?

    - a) Consensus should be used for every piece of data a system stores, since stronger guarantees are always better
    - b) Consensus is worth its latency and availability cost specifically when a system needs a single agreed order that survives a minority of crashed servers; data that only needs eventual consistency doesn't need it
    - c) Consensus has no latency cost as long as the cluster has no failures
    - d) A minority partition's unavailability is a design flaw that better consensus protocols eventually eliminate

<details markdown="1"><summary>Check</summary>

**b)** That's the actual decision this lesson (and the mission) asks for: match the guarantee's cost to the data's actual need. (a) is false: paying consensus's round-trip cost for data that tolerates eventual consistency is waste, not safety. (c) is false: every committed write pays the majority round trip regardless of whether anything is currently failing. (d) is false: minority unavailability is a structural consequence of the safety property, not a solvable inefficiency; any protocol providing the same safety guarantee under partition has the same consequence.

</details>

## Real-world reps

- [ ] For a consensus-backed system you know of (or the one from lesson 7's or 8's rep), estimate how many extra network round trips its majority-commit requirement adds to a single write, compared to a hypothetical single-node version of the same system.
- [ ] For that same system, identify what would actually break if it were replaced with an eventually-consistent alternative instead, to test whether its use of consensus is actually justified by this lesson's standard.
- [ ] Tomorrow: read the primary source's evaluation section in full, and note what latency numbers (or throughput trade-offs) the authors report for Raft under normal operation versus during a leader election.

## Going further

- [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
