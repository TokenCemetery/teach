---
title: Resources
description: "Trusted sources for Redis"
type: resources
---

# Redis Resources

## Knowledge

- [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
  Official overview of Redis's in-memory data structures and how they shape what Redis is actually good at storing and manipulating. Use for: the memory-model foundation everything else in this workspace assumes.
- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
  Official reference for eviction policies (`noeviction`, the `allkeys-*` and `volatile-*` families) and exactly when Redis starts evicting keys under a memory limit. Use for: choosing and defending an eviction policy, and recognizing when a system is silently relying on the wrong one.
- [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
  Official docs on RDB snapshotting and AOF logging: what each guarantees on a crash, what each costs, and how they can be combined. Use for: comparing what Redis actually guarantees against Postgres's WAL-backed durability.
- [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
  Official docs describing the Redlock algorithm for a distributed lock built on Redis. Use for: what a "real" distributed lock attempt looks like, before reading the critique below.
- [Article: "How to do distributed locking", Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
  A widely-cited critique of Redlock's safety guarantees under process pauses and clock drift, from the author of *Designing Data-Intensive Applications*. Use for: the specific failure modes behind "a lock that is not one", and why a naive Redis-based lock is a correctness risk, not just a performance one.
- [Docs: "Scaling with Redis Cluster", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)
  Official docs on how Redis Cluster shards keys and what a client and an operator each have to account for as a result. Use for: reasoning about Cluster's compromises without needing to operate one.
- [Docs: "High availability with Redis Sentinel", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
  Official docs on Sentinel's failure-detection and automatic-failover model for a Redis primary/replica setup. Use for: reasoning about Sentinel's compromises, the same way as Cluster above.

## Gaps

- No source yet with a concrete, worked example of "a cache treated as a store" failing in production (a real incident write-up), as opposed to the abstract pattern description in this mission; worth closing once lesson design reaches that specific anti-pattern.
