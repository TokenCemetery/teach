---
title: 1. Partial Failure
description: The one problem every later topic in this workspace is a response to
type: lesson
---

# Lesson 1. Partial Failure

**Mission link:** "What a network can do to you" starts with the single failure mode a single process never has to handle. Consistency models and consensus protocols both exist because of this one problem.
**Primary source:** [Article: "Fallacies of distributed computing", Wikipedia](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
**Prerequisites:** none

## Know this

### The failure mode a single process doesn't have

Call a function in the same process, and there are really only two outcomes: it returns (with a result or an error), or the process crashes and nothing further happens. Either way, once you're back in control of the program, you know which one occurred.

Call across a network, and a third outcome becomes possible: **no response arrives, and you cannot tell why.** The request might never have reached the other machine. It might have arrived and been processed, with only the reply lost on the way back. Or the other machine might simply be slow, still working on it, about to reply any moment. From where the caller stands, all three look identical: silence. This is **partial failure**, and it is the foundational problem this entire workspace is a response to.

### The fallacy behind it

The Wikipedia article's list of "fallacies of distributed computing" catalogs assumptions that hold true on one machine and quietly stop holding once a network is involved: that the network is reliable, that latency is zero, that bandwidth is infinite, and several more. The first one, **"the network is reliable,"** is the one this lesson is about. Code that implicitly assumes a request will always get a response, the way a local function call always returns, is code that has not confronted partial failure yet. It will confront it in production instead, usually at the worst possible time.

### You cannot distinguish "slow" from "dead"

The sharpest version of this problem: **a caller cannot, in general, tell a slow node from a dead one.** Both look exactly like "no response yet." This isn't a solvable engineering gap waiting for a clever enough client library; it's a structural fact about communicating over a network with no upper bound on message delay.

Because of this, every system that waits for a response has to make a decision under uncertainty: **how long do we wait before assuming the other side has failed?** That decision is a **timeout**, and a timeout is a guess, not a fact:

- **Too short**, and a node that is merely slow (garbage collection pause, a momentary CPU spike, a slow disk) gets declared dead. Acting on that false declaration, failing over to a backup, retrying a request that's actually still in flight, can itself cause problems, including two nodes both believing they're in charge at once.
- **Too long**, and a node that has actually failed keeps being treated as "maybe still there, just slow," delaying the recovery that users are waiting on.

There is no timeout value that eliminates this trade-off; there is only choosing where on it a given system needs to sit.

### Why this is the root of everything else in this mission

If nodes could always tell instantly and accurately whether another node had failed, most of what makes distributed systems hard would evaporate: agreeing on state across machines would be nearly trivial, because everyone would always know exactly who's still participating. Consensus protocols are elaborate specifically because they have to produce correct agreement **without** ever being able to fully resolve the slow-versus-dead ambiguity. Every later lesson in this mission, consistency models, consensus, is really a different answer to the same question this lesson raises: given that you can't be sure who's still there, what can you still guarantee?

## Practice

1. ▢ In one sentence, what makes "partial failure" a genuinely different problem from a single process crashing?

<details markdown="1"><summary>Check</summary>

A crashed process's caller finds out immediately and unambiguously; a partial failure produces silence that could mean the request was lost, the reply was lost, or the other side is merely slow, and the caller cannot tell which from where it stands.

</details>

2. ▢ Service A calls Service B and gets no response for 30 seconds. Name the three explanations still on the table, and explain why Service A genuinely cannot distinguish between them just by waiting longer.

<details markdown="1"><summary>Check</summary>

(1) The request never reached Service B. (2) The request arrived and was processed, but the reply was lost on the way back. (3) Service B is still working on the request and hasn't replied yet (it's slow, not dead). All three produce identical observable behavior from Service A's side: no response. Waiting longer doesn't resolve the ambiguity; it only shifts where on the too-short/too-long trade-off Service A is sitting.

</details>

3. ▢ An operator sets an aggressive, very short health-check timeout to "fail fast" and recover quickly from real outages. What risk does this introduce, and why?

<details markdown="1"><summary>Hint</summary>

What happens to a node that is healthy but momentarily slow (a GC pause, a CPU spike) under a timeout tuned for speed rather than accuracy?

</details>

<details markdown="1"><summary>Check</summary>

A merely slow, but healthy, node can get falsely declared dead. If the system reacts to that false declaration (failing over to a backup, promoting another node to take over its role), it risks two nodes believing they're active at once, or unnecessary churn from repeatedly "recovering" from failures that never happened. Fast failure detection and accurate failure detection are in tension, not the same goal.

</details>

4. ▢ Why can't a caller reliably distinguish a slow node from a dead one?

   - a) Because most network protocols don't support health checks
   - b) Because there is no upper bound on message delay over a network, so silence is consistent with both "still coming" and "never coming"
   - c) Because dead nodes always return a specific error code that gets lost in transit
   - d) Because this is solvable, but most client libraries haven't implemented it yet

<details markdown="1"><summary>Check</summary>

**b)** There is no upper bound on message delay over a network, so from the caller's side, silence is consistent with both "the reply is still coming" and "it will never come." (a), (c), and (d) all describe this as an engineering gap rather than the structural fact it actually is.

</details>

## Real-world reps

- [ ] Find a timeout value configured in a real system you have access to (an HTTP client timeout, a health-check interval, a lock lease). Write down what you think it's trading off, too-short-risk versus too-long-risk, and whether you think it's tuned toward "fail fast" or "avoid false positives."
- [ ] Read the full Wikipedia list of fallacies, and for each one, write one sentence on what code would look like if it silently assumed that fallacy were true.
- [ ] Tomorrow: find one incident report (your own team's, or a public postmortem) that was caused by a system mistaking a slow node for a dead one, or vice versa. Name which direction the mistake went.

## Going further

- [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
