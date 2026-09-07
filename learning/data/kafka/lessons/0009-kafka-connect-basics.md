---
title: 9. Kafka Connect Basics
description: How Connect's tasks and worker modes provide parallelism and fault tolerance, and why Connect grants no guarantee the underlying producer or consumer API didn't already provide
type: lesson
---

# Lesson 9. Kafka Connect Basics

**Mission link:** This is the final lesson of the arc: a real pipeline moves data in and out of Kafka through connectors, not hand-written producers and consumers, and this lesson is how Connect's own parallelism and fault-tolerance model relates to everything this workspace already derived, rather than granting anything new.
**Primary source:** [Docs: "Kafka Connect", Apache Kafka](https://kafka.apache.org/documentation/#connect)
**Prerequisites:** [Lesson 8](0008-schema-registry.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ What does a message carry instead of the full schema when Schema Registry is used, and why does that matter for overhead?

<details markdown="1"><summary>Check</summary>

A compact schema ID, not the full schema definition, which avoids the repeated bandwidth and storage cost of embedding a full schema in every message.

</details>

2. ▢ Contrast backward and forward compatibility. Which supports upgrading consumers first, and which supports upgrading producers first?

<details markdown="1"><summary>Check</summary>

Backward compatibility (a new schema can read data written under the previous schema) supports upgrading consumers first. Forward compatibility (data written with a new schema can still be read using the previous schema) supports upgrading producers first.

</details>

## Know this

### Source and sink connectors move data in opposite directions

**Kafka Connect** is a framework for moving data into and out of Kafka without hand-writing a producer or consumer for every integration. A **source connector** pulls data from an external system, a database, a file, an API, into a Kafka topic. A **sink connector** pushes data from a Kafka topic into an external system. Most common integrations already have existing connector plugins (a JDBC source or sink, an S3 sink, a change-data-capture source like Debezium) that only need configuring, not writing from scratch.

### Tasks are Connect's own unit of parallelism

A connector splits its work across one or more **tasks**. A source connector might split by table or by partition of the external system; a sink connector's tasks map onto a subset of the topic's partitions, the same way a consumer group's members do, since a sink connector's tasks are, under the hood, essentially a consumer group. This is the same parallelism idea lesson 1 introduced for partitions and lesson 2 introduced for consumer group members, now expressed at Connect's own layer: tasks are the unit that determines how much of a connector's work can run concurrently.

### Distributed mode gets its fault tolerance from the same rebalancing idea

**Standalone mode** runs Connect as a single process with its configuration in local files: simple, fine for development, with no fault tolerance if that process dies. **Distributed mode** runs multiple worker processes that coordinate with each other using Kafka itself, storing connector configurations, task assignments, and offsets in internal topics, the same pattern lesson 2's `__consumer_offsets` topic used, reusing Kafka's own log as the coordination substrate. If a worker process dies in distributed mode, its tasks get reassigned to the remaining workers, directly analogous to lesson 2's consumer group rebalancing when a member's heartbeats stop arriving; this is exactly what makes distributed mode the production-appropriate choice over standalone.

### Connect grants no guarantee the underlying API didn't already provide

A sink connector consuming from a topic still inherits whatever delivery guarantee (lessons 4 and 5) and ordering guarantee (lesson 6) that topic and its consumer-side configuration actually provide; Connect doesn't add a new guarantee beyond what the producer and consumer APIs it wraps already give. Exactly-once behavior for a source connector still depends on the same idempotent-producer and transaction machinery lesson 5 derived, not on something Connect invents independently. A source connector's output commonly integrates with Schema Registry directly, converting the external system's native schema into a registered schema automatically, which is where lesson 8's compatibility-mode concerns meet whatever schema evolution the external system does over time. Connect is an operational convenience, not a different set of underlying rules.

## Practice

1. ▢ Distinguish a source connector from a sink connector. Which direction does each move data?

<details markdown="1"><summary>Check</summary>

A source connector pulls data from an external system into a Kafka topic. A sink connector pushes data from a Kafka topic into an external system, the opposite direction.

</details>

2. ▢ Describe how a connector's tasks provide parallelism, and how that's conceptually similar to lesson 1's partition-as-parallelism-unit and lesson 2's consumer group parallelism.

<details markdown="1"><summary>Check</summary>

A connector splits its total work across multiple tasks, each handling a subset (a sink connector's tasks map onto a subset of a topic's partitions, essentially forming a consumer group). This mirrors lesson 1's partition count capping consumer parallelism and lesson 2's rule that only one consumer reads a given partition at a time: task count is Connect's own version of that same parallelism ceiling, expressed at its own layer.

</details>

3. ▢ Contrast standalone and distributed mode. Which provides fault tolerance if a worker process dies, and how does that recovery relate to lesson 2's rebalancing?

<details markdown="1"><summary>Hint</summary>

Consider what happens to a connector's configuration and task assignments if the single standalone process disappears versus if one of several distributed workers does.

</details>

<details markdown="1"><summary>Check</summary>

Distributed mode provides fault tolerance: multiple worker processes coordinate via Kafka's own internal topics, and if one worker dies, its tasks get reassigned to the remaining workers, directly analogous to lesson 2's consumer group rebalancing when a member stops sending heartbeats. Standalone mode has no such recovery; a single process dying takes the whole connector down with it, since its configuration lives only in that process's local files.

</details>

4. ▢ Does using Kafka Connect grant a new delivery guarantee beyond what the underlying producer and consumer APIs already provide? Why or why not?

<details markdown="1"><summary>Check</summary>

No. A sink connector's delivery and ordering guarantees still come from whatever the topic and its consumer-side configuration actually provide, and a source connector's exactly-once behavior still relies on the same idempotent-producer and transaction machinery lesson 5 derived. Connect is a convenient runtime and configuration model for using those existing APIs, not a separate guarantee mechanism layered on top of them.

</details>

5. ▢ Which claim is true of Kafka Connect?

   - a) Connect invents its own delivery guarantees, independent of the idempotent-producer and transaction mechanisms this workspace already covered
   - b) A connector's tasks are its own unit of parallelism, and distributed mode reassigns a dead worker's tasks the same way a consumer group rebalances a dead member's partitions
   - c) Standalone mode is the production-appropriate choice, since it requires no coordination overhead
   - d) A sink connector's tasks have no relationship to the topic's own partitions

<details markdown="1"><summary>Check</summary>

**b)** That direct parallel to lesson 2's rebalancing is exactly how distributed mode's fault tolerance works. (a) is false: Connect relies on the same underlying delivery-guarantee machinery, it doesn't replace it. (c) is false: standalone mode has no fault tolerance, which is why distributed mode is preferred in production. (d) is false: a sink connector's tasks map onto a subset of the topic's partitions, essentially forming a consumer group.

</details>

## Real-world reps

- [ ] Find an existing connector plugin (JDBC, S3, Debezium, or similar) for an integration you have or are considering, and read its configuration options for task count and any delivery-guarantee-related settings.
- [ ] For a Connect deployment you have access to, check whether it's running in standalone or distributed mode, and what that implies for fault tolerance if a worker process fails.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can design a topic, partition, and consumer-group layout for a stated workload, diagnose a lagging or rebalancing consumer, and state what exactly-once actually costs.

## Going further

- [Docs: "Kafka Connect", Apache Kafka](https://kafka.apache.org/documentation/#connect)
- [Docs: "Schema Registry", Confluent](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
