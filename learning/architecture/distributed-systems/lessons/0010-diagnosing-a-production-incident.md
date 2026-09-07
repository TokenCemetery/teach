---
title: 10. Diagnosing a Production Incident
description: Applying partial failure, failure detection, consistency models, and consensus to name the mechanism behind a real incident, instead of reasoning about "the network" or "consistency" in the abstract
type: lesson
---

# Lesson 10. Diagnosing a Production Incident

**Mission link:** This is the final lesson of the arc. Every prior lesson named one mechanism in isolation; a real incident is usually one or two of them colliding. This lesson is the mission's second success criterion made concrete: given an incident caused by partial failure, name the mechanism responsible, using the vocabulary this workspace built rather than reasoning about "the network" as one vague thing.
**Primary source:** [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
**Prerequisites:** [Lesson 9](0009-what-consensus-costs.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ Why does every committed write in a consensus-based system pay at least one network round trip, even when nothing is failing?

<details markdown="1"><summary>Check</summary>

Because a write can't be safely reported as committed until the leader confirms a majority of the cluster has durably stored it, which requires sending the entry out and waiting for enough acknowledgments to form a majority, regardless of whether every server happens to be healthy at that moment.

</details>

2. ▢ Why is a minority partition's loss of availability in a consensus-based system described as intended rather than a bug?

<details markdown="1"><summary>Check</summary>

Because allowing the minority side to also elect a leader and accept writes would let two sides of the same cluster commit conflicting entries, exactly the split-brain the majority requirement exists to prevent. Losing availability on the minority side is the direct price of keeping the safety guarantee intact.

</details>

## Know this

### A diagnostic checklist, built from nine lessons instead of a hunch

Given an incident, the vocabulary this workspace built resolves into four questions, in order: (1) Was there partial failure involved, silence that got misread as success, failure, or vice versa (lesson 1)? (2) Did anything depend on comparing timestamps or events across machines in a way physical clocks can't support (lesson 2), or did a timeout or heartbeat make a wrong slow-versus-dead call (lesson 3)? (3) Did the incident involve two clients or replicas disagreeing about the order or currency of a value, and if so, which consistency model did the system actually need versus actually have (lessons 4 to 6)? (4) Did the incident involve a leader, a lock, or an agreed value, and if so, was consensus actually being used correctly, or was a step of it (majority confirmation, term checking) skipped or assumed (lessons 7 to 9)? Most real incidents answer "yes" to one or two of these, not all four; naming which one is the actual diagnosis.

### Reading a real incident: what to look for in an actual report

A concrete incident report (a postmortem, or one of the Jepsen analyses in the primary source) typically describes: what the system was supposed to guarantee, what a client actually observed that violated that guarantee, and, once investigated, which specific mechanism failed to hold up its end. The diagnostic work is connecting the observed symptom ("we saw duplicate data," "two nodes both thought they were primary," "a write we confirmed came back stale") to one of the checklist's four questions, rather than stopping at a description of the symptom itself. "The database lost data during a network issue" is a symptom; "the system allowed a minority partition to keep accepting writes because its failover logic didn't actually check for a majority" is a diagnosis, because it names the specific mechanism (lesson 8's majority requirement, skipped or misimplemented) that failed.

### A worked example: split-brain from a failover that skipped consensus

A common pattern in real incidents (and several Jepsen analyses): a system provides automatic failover, promoting a replica to primary when the old primary seems unreachable, but implements the promotion with a simple heartbeat-and-timeout mechanism (lesson 3) rather than an actual majority-based consensus protocol (lessons 7 to 8). During a partition, both the old primary (still reachable to some clients) and the newly promoted replica (reachable to others) can end up believing they're the sole primary at the same time, each accepting writes independently. The diagnosis: this isn't "the network failed," it's that the failover mechanism never actually enforced lesson 8's majority-commit requirement, so nothing prevented two leaders from coexisting the way term numbers and majority votes are specifically designed to prevent.

### What this closes: reasoning about incidents instead of vibes

The mission opened by observing that six language workspaces can't teach what happens when the other machine doesn't answer. This lesson is the payoff: given an unfamiliar incident, the four-question checklist gives a concrete place to start, and the vocabulary from lessons 1 through 9 (partial failure, logical clocks, failure detectors, CAP, linearizability, sequential and eventual consistency, replicated state machines, majority quorums) gives precise, checkable names for what actually went wrong, instead of a vague appeal to "the network" or "consistency" as one undifferentiated thing.

## Practice

1. ▢ State the four diagnostic questions this lesson's checklist asks about an incident, in order.

<details markdown="1"><summary>Check</summary>

(1) Was partial failure involved, silence misread as success or failure? (2) Did the incident involve trusting cross-machine timestamps, or a timeout/heartbeat making a wrong slow-versus-dead call? (3) Did it involve disagreement about order or currency of a value, and which consistency model was actually needed versus provided? (4) Did it involve a leader, lock, or agreed value where a step of consensus (majority confirmation, term checking) was skipped or assumed?

</details>

2. ▢ Why is "the database lost data during a network issue" a symptom rather than a diagnosis?

<details markdown="1"><summary>Hint</summary>

Consider what additional, specific information a real diagnosis has to supply that this sentence doesn't.

</details>

<details markdown="1"><summary>Check</summary>

It describes what was observed without naming which specific mechanism from the checklist actually failed, a timeout misfiring, a missing majority check, a consistency model weaker than what the data needed. A real diagnosis names the specific failed mechanism, for example that a failover skipped an actual majority-based consensus check, which is what makes the incident understandable and preventable rather than just described.

</details>

3. ▢ In the worked split-brain example, why does implementing failover with a heartbeat-and-timeout mechanism instead of majority-based consensus create the risk of two simultaneous primaries?

<details markdown="1"><summary>Check</summary>

A heartbeat-and-timeout mechanism only answers "have I heard from the primary recently," which different clients partitioned differently can answer differently at the same time; nothing in that mechanism enforces that only one side of a partition can ever believe it has permission to act, the way a majority-quorum requirement does. Without that enforcement, both an old primary still reachable to some clients and a newly promoted replica reachable to others can each conclude they're the sole primary simultaneously.

</details>

4. ▢ A team reports: "Two of our service instances both grabbed the same job from the queue at the same time during a brief network blip." Using the checklist, what's the first question to ask, and what's a plausible next step?

<details markdown="1"><summary>Check</summary>

The first question is whether partial failure and a timeout-based failure detector were involved (checklist question 2): did one instance's health check briefly and wrongly conclude the job's original owner was dead? A plausible next step is checking whether "grabbing" a job is protected by an actual distributed lock with real exclusivity guarantees (data/redis lessons 4-5, or a consensus-backed lock, lesson 8) or by a weaker heartbeat-based ownership check that two instances could both pass at once.

</details>

5. ▢ Which claim best describes the point of this lesson's diagnostic approach?

   - a) Every incident should be attributed to "the network" without further investigation, since partial failure explains all distributed failures equally
   - b) A real diagnosis names the specific mechanism (a timeout, a consistency model mismatch, a skipped consensus step) that failed, using the precise vocabulary this workspace built, rather than stopping at a description of the observed symptom
   - c) Consensus protocols make diagnosing incidents unnecessary, since they eliminate all four checklist categories
   - d) Incidents caused by consistency model mismatches can only be diagnosed by reading the Raft paper

<details markdown="1"><summary>Check</summary>

**b)** That's the mission's actual payoff: precise, checkable names for what went wrong instead of a vague appeal to "the network." (a) is false: the whole point of the checklist is distinguishing which specific mechanism was actually responsible, not treating all failures as interchangeable. (c) is false: consensus-based systems can still have incidents, for instance if a component bypasses consensus entirely, as the worked example shows. (d) is false: a consistency-model mismatch is diagnosed using lessons 4-6's vocabulary, not the Raft paper specifically.

</details>

## Real-world reps

- [ ] Read one Jepsen analysis from the primary source in full. Identify which of this lesson's four checklist questions the analysis's root cause actually falls under, and write the diagnosis in one sentence using this workspace's vocabulary.
- [ ] Find (or recall) one incident from a system you've worked on that involved more than one machine. Run the four-question checklist against it and see how far you get toward a precise diagnosis versus a vague "the network was flaky" description.
- [ ] Tomorrow: pick one system you use professionally that makes a consistency or availability claim (a database, a queue, a cache), and write down, in this workspace's vocabulary, exactly what guarantee it claims and what mechanism provides it.

## Going further

- [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
