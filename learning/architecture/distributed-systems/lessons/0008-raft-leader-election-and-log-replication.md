---
title: 8. Raft, Leader Election and Log Replication
description: How Raft elects a single leader and replicates a log through it, the two mechanisms that turn the replicated-state-machine problem into something concrete
type: lesson
---

# Lesson 8. Raft, Leader Election and Log Replication

**Mission link:** Lesson 7 named the replicated-state-machine problem consensus solves. Raft is the specific, deliberately understandable protocol this workspace uses to make that concrete: this lesson covers its two core mechanisms, before lesson 9 covers what running either actually costs.
**Primary source:** [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
**Prerequisites:** [Lesson 7](0007-what-consensus-is-for.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ Define a replicated state machine and the problem it solves.

<details markdown="1"><summary>Check</summary>

A set of servers each holding an identical copy of some data, applying the same sequence of commands in the same order so their states stay identical. It solves the single-point-of-failure problem of one server holding the only authoritative copy.

</details>

2. ▢ Distinguish safety from liveness for a consensus protocol.

<details markdown="1"><summary>Check</summary>

Safety means the protocol never decides two different values for the same slot, an absolute guarantee that must hold no matter how badly the network behaves. Liveness means the system eventually makes progress deciding new values, but only under reasonable conditions, since no protocol can guarantee progress under fully arbitrary asynchronous behavior.

</details>

## Know this

### Raft's first move: reduce consensus to "agree on who's in charge"

Raft's central design choice is **leadership**: at any time, at most one server in the cluster is the leader, and every client write goes through it. This turns the general "how do multiple servers agree on a value" problem into two narrower ones: first, how does the cluster elect a leader and detect when it needs a new one (**leader election**); second, given a leader, how does it get its log of commands replicated correctly to the rest of the cluster (**log replication**). Reducing consensus to these two mechanisms is exactly what the paper's title means by "understandable": each piece is simpler to reason about than a single protocol solving both problems undifferentiated.

### Leader election: a term counter and a majority vote

Every server is a **follower**, a **candidate**, or the **leader**. A follower that stops hearing from a leader within a timeout (lesson 3's failure-detection problem, applied here directly) becomes a candidate, increments a monotonically increasing **term** number, and requests votes from the rest of the cluster. A server votes for at most one candidate per term, on a first-come basis; a candidate that receives votes from a **majority** of the cluster becomes leader for that term. Requiring a majority, not unanimity, is what lets Raft keep working when some servers are unreachable: it only needs more than half the cluster to agree at any moment, not all of it.

### Log replication: the leader is the only source of truth for order

Once elected, the leader accepts client commands, appends each one to its own log, and replicates that log entry to followers via `AppendEntries` messages. A log entry is considered **committed**, safe to apply and report as done, once the leader confirms a majority of servers have stored it. Followers never accept commands directly from clients and never independently decide their own log order; they only ever adopt entries the current leader sends them. This is the mechanism that provides the single agreed order lesson 6 and 7 described: since only one leader proposes order at a time, and a majority must durably store each entry before it's committed, no two conflicting orders can both become committed.

### Why a term number, not just an election, prevents split-brain

A stale leader that hasn't noticed a new election happened (it was partitioned away, then reconnects) could otherwise keep believing it's still in charge. Raft prevents this with the term number: every message carries the sender's term, and a server that sees a higher term than its own immediately steps down (if it was a leader or candidate) and updates its own term. A stale leader's `AppendEntries` messages get rejected by followers who've already voted in, and moved on to, a higher term, so the old leader discovers it's stale as soon as it talks to anyone from the new term and reverts to being a follower.

## Practice

1. ▢ Why does reducing consensus to "elect one leader, then replicate its log" make Raft easier to reason about than a protocol without a designated leader?

<details markdown="1"><summary>Check</summary>

It splits one general, hard problem (getting arbitrary servers to agree on arbitrary values) into two narrower, more tractable ones: who is in charge right now, and how does the one server in charge get its proposed order replicated correctly. Each piece can be understood and verified largely on its own.

</details>

2. ▢ Why does Raft require only a majority vote to elect a leader, rather than a unanimous one?

<details markdown="1"><summary>Hint</summary>

Consider what would happen to the cluster's ability to make progress if it required every single server to agree before proceeding.

</details>

<details markdown="1"><summary>Check</summary>

Requiring unanimity would mean a single unreachable or crashed server could block the entire cluster from ever electing a leader, which is exactly the kind of liveness failure a partition (lesson 1) makes routine. A majority requirement lets the cluster keep making progress as long as more than half its servers can communicate, tolerating the rest being slow, partitioned, or down.

</details>

3. ▢ When is a log entry considered committed, and why does that specific condition matter for safety?

<details markdown="1"><summary>Check</summary>

An entry is committed once the leader confirms a majority of servers have stored it. This matters because any future leader must also be elected by a majority, and any two majorities of the same cluster always overlap by at least one server; that overlapping server is guaranteed to have the committed entry, so no future leader can be elected without seeing it and can't accidentally erase or reorder it.

</details>

4. ▢ A leader gets partitioned away from the rest of the cluster, which elects a new leader in its absence. The old leader later reconnects, still believing it's in charge. What stops it from causing a conflicting write?

<details markdown="1"><summary>Check</summary>

The term number. The new leader was elected in a higher term, and any message the old leader sends carries its own, now-stale term number; any follower that has already moved on to the higher term rejects the old leader's messages, and the old leader discovers a higher term as soon as it communicates with anyone from the new one, at which point it steps down and reverts to being a follower.

</details>

5. ▢ Which claim correctly describes Raft's core mechanisms?

   - a) Followers independently decide log order and reconcile differences after the fact
   - b) A leader is elected by majority vote per term, and only the leader proposes log order, which followers replicate; a majority must store an entry before it's committed
   - c) Raft requires unanimous agreement from every server before committing any log entry
   - d) Term numbers are only used for debugging and have no role in preventing conflicting leaders

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism: majority-elected leader, leader-proposed order, majority-durable commits. (a) is false: followers never independently decide order, only the leader proposes it. (c) is false: Raft explicitly uses majority, not unanimous, agreement, specifically to tolerate some servers being unreachable. (d) is false: term numbers are exactly what lets a stale leader detect it's been superseded and step down, preventing split-brain.

</details>

## Real-world reps

- [ ] Use the primary source's companion visualization (raft.github.io) to watch a simulated leader election and a simulated network partition, and note what happens to the partitioned-away leader when the partition heals.
- [ ] Find a system you know of that uses Raft (or a similar leader-based consensus protocol) for coordination. Identify what decision its leader is elected to make authoritative (a configuration value, a replication order, a lock).
- [ ] Tomorrow: read the primary source's section on log replication and commitment in full, including its argument for why an entry from a previous term can't be considered committed just because a majority stores it under the current leader, without an entry from the current term also being replicated.

## Going further

- [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
- [Site: "The Raft Consensus Algorithm", raft.github.io](https://raft.github.io/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
