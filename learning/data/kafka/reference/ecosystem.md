---
title: Ecosystem
description: "The seven compatibility types with who upgrades first, and what Kafka Connect adds around the log, including the guarantee that is off by default"
type: reference
---

# The Surrounding Ecosystem: Schema Registry and Kafka Connect

Stage 5 compressed for lookup. [Lesson 8](../lessons/0008-schema-registry.md) covers schemas as an enforced contract and [lesson 9](../lessons/0009-kafka-connect-basics.md) covers Connect's shape; this sheet is the settings and the tables, for when you are choosing a compatibility mode or standing up a worker.

## Schema Registry

A separate service, not part of the brokers. A producer registers a schema and puts only the **schema ID** in each message; a consumer resolves the ID to deserialise. The important part happens before any of that: a registration is **checked against the subject's compatibility type and rejected if it would break it**, which moves a breaking change from consume time to produce time.

### The compatibility types, and who upgrades first

This is the operational half, and it follows from the type rather than from preference.

| Type | Guarantee | Upgrade order |
|---|---|---|
| `BACKWARD` | A consumer on the new schema reads data from the new schema **and the one before it** | **Consumers first**, before anything produces the new schema |
| `BACKWARD_TRANSITIVE` | The same, against **all** registered versions | Consumers first |
| `FORWARD` | A consumer on the **old** schema reads data written with the new one | **Producers first**, then make sure older-schema data is no longer reaching consumers, then upgrade consumers |
| `FORWARD_TRANSITIVE` | The same, against all registered versions | Producers first |
| `FULL` | Both directions, against the previous version | Either order, independently |
| `FULL_TRANSITIVE` | Both directions, against all versions | Either order, independently |
| `NONE` | Checks disabled | Entirely on you |

**The default is `BACKWARD`, not `BACKWARD_TRANSITIVE`,** and the difference matters more than the names suggest. With three versions `X-2`, `X-1`, `X`, plain `BACKWARD` guarantees a consumer on `X` can read data written with `X` or `X-1`. It says nothing about `X-2`. A topic with retention long enough to still hold `X-2` data, and a consumer that replays from the beginning, is outside the guarantee. If replay from the start has to work, the type is `BACKWARD_TRANSITIVE`.

For **Kafka Streams**, only `FULL`, transitive, and `BACKWARD` are supported.

### What each type actually lets you change

For Avro and Protobuf. This is why `FULL` is a real constraint rather than a free upgrade in safety.

| Change | Backward | Forward | Full |
|---|---|---|---|
| Add an optional field | yes | yes | yes |
| Remove an optional field | yes | yes | yes |
| Add a required field | no | yes | no |
| Remove a required field | yes | no | no |
| Add a union or `oneof` variant | yes | no | no |
| Remove a union or `oneof` variant | no | yes | no |

Deleting a field and staying compatible depends on how the field was **originally** defined: it has to have been optional or carried a default in the earlier version. A field that was required from the start cannot be removed later without breaking the mode. Today's schema decides which changes are available next year.

JSON Schema behaves differently again, depending on both the compatibility policy and whether the content model is open or closed.

## Kafka Connect

| | Standalone | Distributed |
|---|---|---|
| Processes | One | Several workers sharing a `group.id` |
| Configuration lives in | Local files | Kafka topics |
| On process death | Everything stops | Tasks are reassigned to surviving workers |
| Use for | Development | Production |

Distributed mode coordinates through Kafka itself, exactly as a consumer group does. Its state sits in three internal topics:

| Config | Holds |
|---|---|
| `config.storage.topic` | Connector configurations |
| `offset.storage.topic` | Source connector offsets |
| `status.storage.topic` | Connector and task status |

A sink connector's tasks are a consumer group underneath, so everything on [Consumer Groups and Rebalancing](consumer-groups-and-rebalancing.md) applies to them, including the partition-count ceiling on useful parallelism.

### Converters are where the two halves meet

`key.converter` and `value.converter` translate between Connect's internal format and the bytes on the wire. They are configured **independently of the connector**, which is what lets any connector work with any serialization format, and it is where a Schema Registry serialiser is plugged in.

### The guarantee that is off by default

Lesson 9's claim that Connect invents no new rules is right about the machinery and can leave the wrong impression that there is nothing to switch on. There is.

`exactly.once.source.support` gives source connectors exactly-once delivery by writing source records **and their source offsets** in one transaction, and by fencing out old task generations before starting new ones. It is the transaction mechanism from [Delivery Guarantees](delivery-guarantees.md), wired up for you rather than reinvented.

Its default is **`disabled`**. Enabling it on an existing cluster is two steps, both of which can be rolling:

1. Set it to `preparing` on **every** worker.
2. Set it to `enabled`.

Sink connectors get no such switch. A sink inherits whatever the topic and its consumer configuration already provide, which means `isolation.level` and commit ordering are still yours to get right.

## What Connect adds, and what it does not

| | Added by Connect |
|---|---|
| Parallelism | No. Tasks map onto the same partition ceiling |
| Fault tolerance | Yes, in distributed mode, by the same rebalancing idea |
| Ordering guarantees | No. Whatever the topic and key choice already gave |
| Sink delivery semantics | No. Inherited from the consumer configuration |
| Source delivery semantics | Yes, optionally, through `exactly.once.source.support` |
| Schema handling | Indirectly, through the converters you configure |

## Before relying on either

- The compatibility type is chosen from the upgrade order you can actually run, not from which word sounds safest.
- If consumers ever replay from the beginning of a retained topic, the type is transitive.
- New fields are optional or carry defaults, because that is what keeps them removable later.
- Somebody has confirmed the registry is actually in the path, rather than schemas being agreed informally while the service sits unused.
- Connect runs distributed in production, and its three internal topics exist with sensible replication.
- If a source connector needs exactly-once, `exactly.once.source.support` has been enabled deliberately, in two steps, rather than assumed.

## Sources

- [Docs: "Schema Registry", Confluent](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Docs: "Schema Evolution and Compatibility", Confluent](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- [Docs: "Kafka Connect", Apache Kafka](https://kafka.apache.org/documentation/#connect)
- [Docs: "Connect Configs", Apache Kafka](https://kafka.apache.org/documentation/#connectconfigs)
- [Consumer Groups and Rebalancing](consumer-groups-and-rebalancing.md)
- [Delivery Guarantees](delivery-guarantees.md)
- [Resources](../RESOURCES.md)
