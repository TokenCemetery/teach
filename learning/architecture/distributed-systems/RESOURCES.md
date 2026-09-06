---
title: Resources
description: "Trusted sources for distributed systems"
type: resources
---

# Distributed Systems Resources

## Knowledge

- [Article: "Fallacies of distributed computing", Wikipedia](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
  The canonical list (originated by Peter Deutsch, extended by James Gosling) of assumptions that hold on one machine and quietly stop holding once a network sits between two of them. Use for: the vocabulary for what a network can do to you, before reasoning about any specific failure.
- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
  An interactive, precisely-defined map of consistency models (linearizability, serializability, causal consistency, and more), with the guarantees and violations that distinguish each. Use for: pinning down exactly which consistency model a system is buying, rather than reasoning about "consistency" as one vague thing.
- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
  CAP's own author revisiting and correcting common misreadings of the theorem, including that partition tolerance isn't optional and that the real trade-off is more nuanced than "pick two". Use for: using CAP correctly instead of the oversimplified version most engineers repeat.
- [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
  The Raft paper, written explicitly to make a consensus protocol's mechanism and cost understandable without requiring a from-scratch proof of correctness. Use for: the primary source on what a consensus protocol actually does and what it costs to run.
- [Site: "The Raft Consensus Algorithm", raft.github.io](https://raft.github.io/)
  Interactive visualization of Raft's leader election and log replication, letting you watch the protocol handle a simulated node failure or partition. Use for: building intuition for Raft's mechanics before or alongside reading the paper.
- [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
  Real distributed databases and coordination systems tested under actual network partitions and process pauses, with the specific consistency violations each analysis found. Use for: concrete, real-system evidence of what partial failure actually does to a system that assumed the network was reliable.

## Gaps

- No source yet specifically distinguishing a slow node from a dead one in a real incident (the detection and timeout mechanics behind that specific failure mode), as opposed to the general partial-failure vocabulary in the sources above; worth closing once lesson design reaches failure detection.
