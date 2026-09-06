---
title: Glossary
description: "Canonical terms for Redis"
type: glossary
---

# Redis Glossary

Canonical terms for using Redis for what it actually is: an in-memory store with a bounded, evictable keyspace.

## Terms

**Eviction policy**:
The rule Redis follows to decide which keys to delete once `maxmemory` is reached, ranging from deleting nothing and rejecting writes (`noeviction`) to deleting any key (`allkeys-*`) or only keys with a TTL (`volatile-*`).
_Avoid_: cache policy (too vague; name the specific policy)

**maxmemory**:
The configured memory ceiling for a Redis instance's dataset. What happens once it's reached is determined entirely by the eviction policy in force.
_Avoid_: memory limit (use the exact setting name once it's been introduced)
