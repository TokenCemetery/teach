---
title: 6. Sequential and Eventual Consistency
description: Two models weaker than linearizability, what each still guarantees, and how to choose among all three for a stated design
type: lesson
---

# Lesson 6. Sequential and Eventual Consistency

**Mission link:** This is stage 3's capstone. Lesson 5 established linearizability's guarantee and its cost; this lesson covers the two weaker models teams reach for specifically to avoid that cost, and closes the stage with the actual decision the mission's success criterion asks for: choosing and defending a consistency model for a stated design.
**Primary source:** [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
**Prerequisites:** [Lesson 5](0005-linearizability.md), [Partial failure](../GLOSSARY.md)

## Warm-up

1. ▢ State linearizability's guarantee, precisely.

<details markdown="1"><summary>Check</summary>

Every operation appears to take effect atomically at some single instant between its invocation and completion, and all operations across all clients agree on one single order that's consistent with real, wall-clock time; once a write completes, no subsequent read anywhere can see an earlier value.

</details>

2. ▢ Why does maintaining linearizability during a partition force a system to refuse some requests?

<details markdown="1"><summary>Check</summary>

Because it can't confirm, while partitioned, whether a write already succeeded elsewhere that would make its own answer stale relative to the required real-time order; refusing to answer is how it avoids ever giving an order-violating response.

</details>

## Know this

### Sequential consistency: agreement on order, without the real-time requirement

**Sequential consistency** drops linearizability's one demanding piece: it still requires that all operations appear to execute in *some* single, total order that every client agrees on, and that each client's own operations appear in that order in the sequence that client issued them, but that single agreed order no longer has to match real, wall-clock time. Two operations from different clients that overlapped in real time can be ordered either way in the agreed sequence, as long as the ordering is consistent for everyone observing it. This is weaker than linearizability specifically because it drops the real-time constraint, the part that made linearizability expensive to provide across a partition.

### Why sequential consistency is still not free

Even without the real-time requirement, sequential consistency still requires every client to agree on the *same* single order, which still requires enough coordination that a partition can prevent that single agreed order from being knowable everywhere. It's a genuinely weaker, cheaper guarantee than linearizability, not a free one: it still rules out different clients seeing operations in genuinely different, contradictory sequences.

### Eventual consistency: the guarantee shrinks to "you'll get there"

**Eventual consistency** drops the "single agreed order" requirement entirely. Its guarantee is much smaller: if no new writes occur, all replicas will *eventually* converge to the same value, given enough time for updates to propagate. In between, different clients reading different replicas can observe different values, in different orders, with no promise about how long "eventually" takes. This is what makes eventual consistency available even during a partition (each side just keeps answering with whatever it locally has), at the cost of every client potentially seeing a temporarily different, possibly stale picture of the data.

### Choosing a model is choosing what an application is allowed to observe

The actual design decision isn't "which model is best," it's "what does this specific piece of data need other clients to never be able to observe going wrong." A distributed lock or a bank balance right after a debit needs linearizability, since a single stale or reordered read is a correctness failure (lesson 5). A collaborative document's operation log, or a replicated counter used only for a rough dashboard estimate, can tolerate sequential consistency or even eventual consistency, since a client seeing a slightly different, eventually-converging order isn't a correctness failure for that use case, just a temporary inconvenience. The mission's actual success criterion is this: given a stated design, name which of these three models the data genuinely needs, not which one sounds the strongest.

## Practice

1. ▢ What single requirement does sequential consistency drop relative to linearizability, and what does it keep?

<details markdown="1"><summary>Check</summary>

It drops the requirement that the single agreed order match real, wall-clock time; it keeps the requirement that all clients agree on some single total order, and that each client's own operations appear in that order in the sequence it issued them.

</details>

2. ▢ Two clients issue operations that overlap in real time. Under sequential consistency, is it possible for the system to place client B's operation before client A's in the agreed order, even though A's finished first in real time? Is this still true under linearizability?

<details markdown="1"><summary>Hint</summary>

Consider exactly which guarantee each model actually promises about real time.

</details>

<details markdown="1"><summary>Check</summary>

Under sequential consistency, yes: since the agreed order doesn't have to match real time, B could legitimately be placed before A as long as every client agrees on that same ordering. Under linearizability, no: since A finished completely before B started, linearizability requires A to precede B in the single agreed order; placing B first would violate its real-time-consistency guarantee.

</details>

3. ▢ What is eventual consistency's actual guarantee, and what does it explicitly not promise?

<details markdown="1"><summary>Check</summary>

It guarantees that if no new writes occur, all replicas will eventually converge to the same value once updates finish propagating. It does not promise a single agreed order across clients, nor any bound on how long convergence takes; different clients can see different values, in different orders, in the meantime.

</details>

4. ▢ A team is building a replicated "like count" shown on a social media post, where being off by a small amount for a few seconds is invisible to users, versus a separate feature tracking account balances for a payments product. Which consistency model fits each, and why?

<details markdown="1"><summary>Check</summary>

The like count is a good fit for eventual consistency: a temporarily stale or inconsistent count across replicas isn't a correctness failure for that feature, it's an invisible, self-correcting inconvenience. The account balance needs linearizability: any read observing a balance from before a completed debit or credit, even briefly, is a genuine correctness failure a user or the business could act on incorrectly (like an overdraft).

</details>

5. ▢ Which claim correctly ranks the three models by what they guarantee?

   - a) Eventual consistency is strictly stronger than sequential consistency, since it always converges
   - b) Linearizability implies sequential consistency (it's a strictly stronger guarantee), and sequential consistency is strictly stronger than eventual consistency
   - c) All three models are equivalent once a system has no active partition
   - d) Sequential consistency requires real-time ordering, making it as strong as linearizability

<details markdown="1"><summary>Check</summary>

**b)** Linearizability adds the real-time requirement on top of sequential consistency's single-agreed-order requirement, and sequential consistency requires a single total order that eventual consistency doesn't require at all, so the strength ordering is linearizability > sequential consistency > eventual consistency. (a) is false: convergence eventually is a much weaker promise than a single agreed order at all times. (c) is false: even without a partition, these models differ in what latency and coordination they demand, and a system's implementation choice doesn't just vanish when things are calm. (d) is false: dropping the real-time requirement is exactly what distinguishes sequential consistency from linearizability.

</details>

## Real-world reps

- [ ] For a system you know of, list two pieces of data it stores with genuinely different consistency needs (something that must never be stale even briefly, versus something where staleness is invisible or harmless). Name which of the three models each one actually needs.
- [ ] Check whether the system's actual implementation matches that need, over-provisioning (paying linearizability's cost where eventual consistency would do) or under-provisioning (risking a correctness failure where linearizability was actually required).
- [ ] Tomorrow: read the primary source's formal definitions of sequential and eventual consistency in full, including any additional intermediate models it defines (such as causal consistency), and note where each would sit relative to the three covered in this lesson.

## Going further

- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
