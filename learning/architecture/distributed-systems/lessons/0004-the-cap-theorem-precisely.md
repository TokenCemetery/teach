---
title: 4. The CAP Theorem, Precisely
description: What CAP actually proves, why partition tolerance was never optional, and the specific misreadings that make "pick two" the wrong way to state it
type: lesson
---

# Lesson 4. The CAP Theorem, Precisely

**Mission link:** Stage 3 opens consistency models, and CAP is the theorem everyone half-remembers and almost everyone half-misremembers. This lesson pins down exactly what it proves, since lessons 5 and 6 (linearizability, sequential and eventual consistency) only make sense once CAP's actual trade-off is stated correctly.
**Primary source:** [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
**Prerequisites:** [Lesson 3](0003-timeouts-as-failure-detectors.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ Define completeness and accuracy for a failure detector.

<details markdown="1"><summary>Check</summary>

Completeness means the detector eventually suspects every process that actually crashes. Accuracy means it doesn't suspect a process that hasn't actually crashed. A detector can have one without the other, for instance one that suspects everyone constantly (complete, inaccurate) or one that never suspects anyone (accurate, incomplete).

</details>

2. ▢ What is a heartbeat, and how does it relate to the single-request timeout from lesson 1?

<details markdown="1"><summary>Check</summary>

A heartbeat is a periodic ping used to detect whether a remote node is still responsive; it's the same timeout decision from lesson 1 (how long to wait before assuming failure), just applied continuously and automatically instead of to one specific request.

</details>

## Know this

### What CAP actually names: three properties, only one real choice

**CAP** names three properties of a distributed data system: **Consistency** (every read receives the most recent write, or an error), **Availability** (every request to a non-failed node receives a response, though not necessarily the most recent write), and **Partition tolerance** (the system continues operating despite network partitions, arbitrary message loss or delay between nodes). The theorem states you cannot have all three simultaneously in the presence of an actual partition.

### Partition tolerance isn't the third option, it's the given

The most common misreading treats CAP as "pick any two of three," as if partition tolerance were a design choice a team could decline. It isn't: partial failure (lesson 1) is a structural fact about networks, not a preference, and any distributed system spanning more than one node has to survive the possibility of a partition whether or not its designers accounted for it. Brewer's retrospective is explicit about this: the real choice CAP describes only exists *once a partition is actually happening*, and it's between C and A, not among all three: during a partition, a node that keeps responding despite being unable to confirm it has the latest data is choosing availability over consistency, and a node that refuses to respond (or returns an error) rather than risk a stale answer is choosing consistency over availability.

### Outside a partition, the trade-off doesn't apply

CAP's constraint is conditional: while the network is behaving normally, a well-designed system can be fully consistent and fully available at the same time, since there's no partition forcing the choice. This is a large part of why "CAP says you can only have two of three" oversimplifies things: it's not a permanent, always-in-effect two-out-of-three menu, it's a specific trade-off that only bites during an actual partition, and only for the specific requests affected by it.

### What CAP does not say

CAP says nothing about latency, nothing about the many consistency models more precise than the binary "consistent or not" it uses (lessons 5 and 6 cover several), and nothing about failures other than partitions. Brewer's own later work (PACELC, outside this lesson's scope) extends the idea specifically because CAP alone doesn't capture the latency-versus-consistency trade-off systems face even when no partition is happening. Treating CAP as a complete theory of distributed system trade-offs, rather than a precise statement about one specific scenario, is the second common misreading this lesson corrects.

## Practice

1. ▢ Why is "pick two of three" a misleading way to state CAP?

<details markdown="1"><summary>Check</summary>

It implies partition tolerance is an optional design choice on equal footing with consistency and availability, when it's actually a structural fact about networks that every real distributed system has to survive. The genuine choice CAP describes is only between consistency and availability, and only during an actual partition.

</details>

2. ▢ A system that isn't currently experiencing a network partition claims to be both fully consistent and fully available. Does this contradict CAP?

<details markdown="1"><summary>Hint</summary>

Consider exactly when CAP's constraint applies.

</details>

<details markdown="1"><summary>Check</summary>

No. CAP's trade-off only applies during an actual partition; outside of one, there's nothing forcing a choice between consistency and availability, so being fully consistent and fully available simultaneously is entirely possible and doesn't contradict the theorem.

</details>

3. ▢ During a network partition, one replica keeps answering reads even though it can't confirm it has the latest write, while another replica returns an error rather than risk answering with stale data. Name which property each replica is prioritizing.

<details markdown="1"><summary>Check</summary>

The first replica is prioritizing availability over consistency (it answers, possibly with stale data). The second is prioritizing consistency over availability (it refuses to answer rather than risk being wrong).

</details>

4. ▢ Name two things CAP does not address, according to this lesson.

<details markdown="1"><summary>Check</summary>

Latency (the trade-off between consistency and response time that exists even without a partition, which PACELC was later proposed to address) and the finer-grained consistency models (linearizability, sequential consistency, eventual consistency) more precise than CAP's simple "consistent or not" framing.

</details>

5. ▢ Which claim correctly states what CAP proves?

    - a) A distributed system must permanently sacrifice either consistency or availability at all times
    - b) During an actual network partition, a system must choose between consistency and availability for the requests affected by that partition; outside a partition, no such forced choice exists
    - c) Partition tolerance is one of three equally optional properties a system can choose to support
    - d) CAP fully describes every trade-off a distributed system faces, including latency

<details markdown="1"><summary>Check</summary>

**b)** That's the theorem's actual, conditional scope. (a) is false: the trade-off is conditional on an actual partition occurring, not a permanent state. (c) is false: partition tolerance isn't optional, since partial failure is a structural network fact, not a design preference. (d) is false: CAP says nothing about latency or about consistency models finer than its binary framing, which is exactly why PACELC and more precise consistency definitions (lessons 5 and 6) exist.

</details>

## Real-world reps

- [ ] For a distributed data system you know of (a database, a cache cluster, a coordination service), find its documented behavior during a network partition. Determine whether it prioritizes consistency or availability for reads during that scenario.
- [ ] For the same system, check whether its designers describe this as a fixed, unconditional choice or as something that only applies during an actual partition, matching (or not) the precise version of CAP from this lesson.
- [ ] Tomorrow: read the primary source's full retrospective in full, including Brewer's own listed list of common CAP misreadings, and note any not covered in this lesson.

## Going further

- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
