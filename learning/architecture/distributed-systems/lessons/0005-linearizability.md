---
title: 5. Linearizability
description: What linearizability actually guarantees, why it's the strongest common consistency model, and what it costs to provide during a partition
type: lesson
---

# Lesson 5. Linearizability

**Mission link:** Lesson 4 established that CAP's "consistency" is a loose, binary stand-in for something more precise. Linearizability is that precise thing, the strongest single-object consistency model in common use, and this lesson is what it actually promises and what providing it costs, before lesson 6 covers the weaker models teams choose specifically to avoid that cost.
**Primary source:** [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
**Prerequisites:** [Lesson 4](0004-the-cap-theorem-precisely.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ State CAP's three named properties.

<details markdown="1"><summary>Check</summary>

Consistency (every read gets the most recent write, or an error), Availability (every request to a non-failed node gets a response, not necessarily the most recent write), and Partition tolerance (the system keeps operating despite arbitrary message loss or delay between nodes).

</details>

2. ▢ Why is "pick two of three" a misleading way to state CAP?

<details markdown="1"><summary>Check</summary>

It implies partition tolerance is optional, when partial failure is a structural network fact every distributed system has to survive; the real, conditional trade-off is only between consistency and availability, and only during an actual partition.

</details>

## Know this

### What linearizability actually guarantees

**Linearizability** guarantees that every operation on an object appears to take effect atomically, at some single instant between when it was invoked and when it completed, and that all operations across all clients agree on one single, real-time-consistent order. Concretely: once a write completes, every subsequent read (by any client, anywhere) sees that write or a later one, never an earlier value. This is stronger than merely "reads eventually see writes"; it specifically rules out any read, anywhere in the system, ever observing a value older than one that has already finished being written elsewhere.

### Why "single real-time order" is the demanding part

The demanding part isn't that operations have some order; it's that the order has to be consistent with real, wall-clock time across every client and every replica. If operation A finishes completely before operation B even starts (by real time, from any external observer's perspective), a linearizable system must place A before B in its single agreed order; it cannot ever place B first. This is exactly what makes linearizability expensive to provide across multiple replicas: every replica has to coordinate enough that no client can ever observe an ordering violating real-time precedence, and that coordination requires communication, which costs latency.

### What providing it costs during a partition

Under CAP's real, conditional trade-off (lesson 4), a system trying to remain linearizable during an actual partition has to sacrifice availability for any request whose correct, order-consistent answer it can't currently confirm: rather than risk answering with a value that might already be stale according to a write that succeeded on the other side of the partition, a linearizable system refuses to answer at all until the partition resolves, or until it can otherwise be sure it isn't providing a real-time-order-violating response. This is the concrete, mechanical shape of "choosing consistency over availability" from lesson 4: linearizability is precisely strong enough that maintaining it during a partition forces this refusal.

### Why a team would choose it, given the cost

Linearizability is what makes a distributed system behave, from any client's perspective, indistinguishably from a single, non-distributed copy of the data: no client can ever observe a value that's causally impossible given what any other client already saw succeed. This matters most where two clients' operations genuinely have to agree on a single order because a real invariant depends on it, a bank balance that mustn't be read as higher than it is right after a debit clears, a lock that mustn't be seen as free by two clients simultaneously (Redlock's whole premise, `data/redis` lesson 4-5, depends on some layer providing an order this strong somewhere). Weaker models (lesson 6) trade this guarantee away specifically because most data doesn't actually need it, and paying linearizability's coordination cost everywhere is wasteful when it does.

## Practice

1. ▢ State linearizability's guarantee in terms of what a read is allowed to return relative to a write that has already completed.

<details markdown="1"><summary>Check</summary>

Once a write completes, every subsequent read, by any client anywhere in the system, must see that write or a later one; it can never see a value from before that write.

</details>

2. ▢ Why does linearizability require an order consistent with real, wall-clock time, rather than just "some" order that respects each individual client's own view of things?

<details markdown="1"><summary>Hint</summary>

Consider what would go wrong if the agreed order could place a later real-world operation before an earlier one that had already fully completed.

</details>

<details markdown="1"><summary>Check</summary>

If operation A completes entirely, by real time, before operation B even begins, but the system's agreed order placed B first, some client could observe an effect of B (the later operation) without ever being able to observe A (the earlier, already-finished one) taking priority, an outcome that would be causally nonsensical relative to what actually happened in the world. Linearizability rules this out specifically by tying the single agreed order to real-time precedence.

</details>

3. ▢ During a network partition, why does a linearizable system have to refuse some requests rather than answer them?

<details markdown="1"><summary>Check</summary>

Because it can't confirm, while partitioned, whether a write has already succeeded on the other side that would make its own answer stale and out of the required real-time order. Rather than risk violating the single-order guarantee, it refuses to answer at all until it can be sure, which is the concrete mechanism behind choosing consistency over availability from lesson 4.

</details>

4. ▢ Give a concrete example of data where linearizability's guarantee actually matters, and explain why a weaker consistency model would be a real risk there.

<details markdown="1"><summary>Check</summary>

A distributed lock (as in `data/redis` lessons 4-5): if two clients could observe the lock as "free" at the same time because their reads weren't linearizable with respect to each other's operations, both could believe they hold exclusive access simultaneously, exactly the correctness failure a lock is supposed to prevent. A bank balance right after a debit is another example: a weaker model could let a client observe the pre-debit balance after the debit has already cleared elsewhere, leading to an overdraft that shouldn't have been possible.

</details>

5. ▢ Which claim correctly describes linearizability?

    - a) It only requires that all clients eventually agree on the same final value, regardless of order
    - b) It guarantees a single, real-time-consistent order for all operations, so no client can ever observe a value older than one already confirmed to have completed elsewhere
    - c) It has no cost during a partition, since it only affects how data is stored, not how it's read
    - d) It's the same guarantee as CAP's "Consistency" property, just described with different words

<details markdown="1"><summary>Check</summary>

**b)** That's the precise guarantee: single real-time-consistent order, ruling out any stale read relative to an already-completed write. (a) is false: eventual agreement without order guarantees is closer to the weaker eventual consistency model (lesson 6), not linearizability. (c) is false: maintaining it during a partition forces refusing some requests, exactly the availability cost described in this lesson. (d) is false: CAP's "Consistency" is a loose, binary stand-in; linearizability is the specific, precisely-defined model that gives that stand-in an actual, checkable meaning.

</details>

## Real-world reps

- [ ] Find a component in a system you know of that claims or requires "strong consistency" (a lock service, a leader-election mechanism, a primary database). Check whether its documentation actually specifies linearizability, or a weaker guarantee described loosely as "strong."
- [ ] For that same component, identify what would concretely go wrong (not just "inconsistency" in the abstract) if it only provided a weaker model instead.
- [ ] Tomorrow: read the primary source's formal definition of linearizability in full, including its worked example of a non-linearizable history, and note what specifically makes that example's ordering invalid.

## Going further

- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
