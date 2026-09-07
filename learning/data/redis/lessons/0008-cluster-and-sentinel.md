---
title: 8. Redis Cluster and Sentinel
description: The compromises Redis Cluster's sharding and Sentinel's automatic failover each introduce, reasoned about without needing to operate either
type: lesson
---

# Lesson 8. Redis Cluster and Sentinel

**Mission link:** This is the final lesson of the arc. Every prior stage assumed a single Redis instance; this lesson is what changes, and what it costs, once a real deployment needs to scale past one instance (Cluster) or survive one failing (Sentinel), closing the mission's last success criterion.
**Primary source:** [Docs: "Scaling with Redis Cluster", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)
**Prerequisites:** [Lesson 7](0007-unbounded-keyspace-and-spotting-misuse.md), [Eviction policy](../GLOSSARY.md)

## Warm-up

1. ▢ State the "named owner" test for whether a Redis key is safely bounded.

<details markdown="1"><summary>Check</summary>

Every key should have an answer to what removes it eventually and when: a TTL set at write time, an explicit `DEL` at a known application event, or a deliberate, capacity-planned decision that it lives forever. A key with none of these is an instance of the unbounded-keyspace anti-pattern.

</details>

2. ▢ What two questions does the stage-4 spotting checklist ask about a given key?

<details markdown="1"><summary>Check</summary>

Whether a miss or eviction of the key has a durable system of record to fall back to (the store anti-pattern check), and whether the key has a named removal mechanism, a TTL, explicit deletion, or deliberate permanence (the unbounded-keyspace check).

</details>

## Know this

### Cluster's job: more data and throughput than one instance can hold

**Redis Cluster** shards the keyspace across multiple primary nodes using hash slots: every key is hashed into one of 16,384 fixed slots, and each slot is owned by exactly one primary node at a time. A client can send a command to any node; if that node doesn't own the relevant slot, it redirects the client to the node that does. This is how Cluster scales past a single instance's memory and CPU ceiling, the same problem that eventually forces the eviction and unbounded-keyspace questions from lessons 1 and 7 onto a single node.

### What Cluster costs: multi-key operations and cross-slot limits

Sharding isn't free. A command touching multiple keys (a multi-key `MGET`, a transaction, a Lua script) only works atomically if every key involved hashes to the *same* slot, since Redis has no cross-node transaction mechanism; Cluster supports **hash tags** (`{user:123}:cart` and `{user:123}:profile` both hash on `user:123`) specifically so a developer can force related keys onto the same slot when an operation needs them together. Get the key design wrong, and a query that was one command on a single instance becomes an application-level fan-out across nodes, or an outright unsupported operation.

### Cluster's failover reuses the same eviction-adjacent trade-off

Each hash slot's primary can have replicas, and Cluster promotes a replica to primary automatically if the original primary is unreachable long enough for the cluster to agree it has failed. Because Redis replication is asynchronous (lesson 4's second failure mode, restated at cluster scale), a write acknowledged by the old primary just before it failed can be lost if it never reached the replica that gets promoted. Cluster gets you through a node failure without an outage, not without any possible data loss on that node's slots.

### Sentinel: the same failover problem for a non-sharded deployment

**Redis Sentinel** solves a narrower, different problem: automatic failover for a single primary/replica setup that isn't sharded at all, monitoring the primary's health and promoting a replica if it goes down, without Cluster's slot-sharding machinery or its multi-key constraints. A team that needs high availability but not more capacity than one instance provides reaches for Sentinel; a team that needs both capacity beyond one instance and availability reaches for Cluster (which has its own built-in replica-promotion, making a separate Sentinel layer unnecessary). Sentinel doesn't remove the asynchronous-replication data-loss window either: it only automates detecting a failure and cutting over faster than a human would.

### The actual trade-off clustering asks a team to accept

Neither Cluster nor Sentinel makes Redis's persistence or replication guarantees stronger; they make an instance failure survivable *for availability* while leaving the same asynchronous-replication loss window from lesson 4 in place for *data*. The decision this closes the mission on is: does this workload need to scale past one instance's capacity (Cluster, accepting its cross-slot constraints), does it need to survive one instance failing without sharding (Sentinel), or does it need neither, in which case a single instance with the persistence configuration from lessons 2 and 3 is the simpler, correct choice.

## Practice

1. ▢ How does Redis Cluster decide which node owns a given key, and how many total slots are there?

<details markdown="1"><summary>Check</summary>

Every key is hashed into one of 16,384 fixed hash slots, and each slot is owned by exactly one primary node at a time. A client can query any node and gets redirected to the node owning the relevant slot if it asked the wrong one.

</details>

2. ▢ Why does a multi-key operation only work atomically in Cluster if a hash tag forces the keys onto the same slot?

<details markdown="1"><summary>Hint</summary>

Consider what Cluster does and doesn't provide across two different nodes.

</details>

<details markdown="1"><summary>Check</summary>

Redis Cluster has no cross-node transaction mechanism, so a multi-key command, transaction, or script can only be atomic if every key it touches lives on the same node, meaning the same hash slot. A hash tag like `{user:123}` forces related keys to hash identically so they land on the same slot and the operation stays possible; without it, keys that happen to land on different nodes make the operation unsupported.

</details>

3. ▢ Does Redis Cluster's automatic failover eliminate the possibility of losing a write during a primary failure? Why or why not?

<details markdown="1"><summary>Check</summary>

No. Cluster's replication between a slot's primary and its replicas is asynchronous, the same as any Redis replica setup, so a write the old primary acknowledged just before failing can be lost if it never reached the replica that gets promoted. Cluster makes the failover automatic and keeps the cluster available, but it doesn't add a stronger replication guarantee.

</details>

4. ▢ A team runs a single, un-sharded Redis instance well within capacity but wants automatic failover if it goes down. Should they reach for Cluster or Sentinel, and why?

<details markdown="1"><summary>Check</summary>

Sentinel: their workload doesn't need Cluster's sharding, only the failover behavior, so Sentinel gives them that without Cluster's cross-slot constraints on multi-key operations or the operational complexity of managing hash slots they don't need.

</details>

5. ▢ Which claim correctly describes what Cluster and Sentinel each provide?

    - a) Both eliminate the asynchronous-replication data-loss window that lesson 4 described
    - b) Cluster provides sharded capacity plus built-in failover; Sentinel provides failover alone for a non-sharded deployment; neither strengthens the underlying replication guarantee
    - c) Sentinel is required in addition to Cluster for any highly-available deployment
    - d) Cluster's hash-tag mechanism removes the need to think about which keys are accessed together

<details markdown="1"><summary>Check</summary>

**b)** That's the precise scope of what each solves and what neither changes. (a) is false: both still rely on asynchronous replication for promoting a replica, so the same loss window from lesson 4 still applies. (c) is false: Cluster already has its own replica-promotion, making a separate Sentinel layer redundant for a Cluster deployment. (d) is false: hash tags require deliberately thinking about which keys need to be co-located; they don't remove the constraint, they're the tool for satisfying it.

</details>

## Real-world reps

- [ ] For a Redis deployment you know of (or a hypothetical one matching a real workload), decide whether it actually needs Cluster's sharding, Sentinel's failover alone, or neither, using the closing trade-off from this lesson.
- [ ] If that deployment used Cluster, identify one multi-key operation in its actual usage that would need a hash tag to stay atomic, and check whether the current key design already accounts for it.
- [ ] Tomorrow: read the primary source's section on cluster resharding (moving slots between nodes while live) in full, and note what a client has to handle differently during a resharding operation versus normal operation.

## Going further

- [Docs: "Scaling with Redis Cluster", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)
- [Docs: "High availability with Redis Sentinel", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
