---
title: 4. Naive Locking Mistakes
description: Why SET NX PX alone is not a distributed lock, and the two failure modes that break it under real conditions
type: lesson
---

# Lesson 4. Naive Locking Mistakes

**Mission link:** Stage 3 opens distributed locks, one of the mission's named misuse patterns ("a lock that is not one"). This lesson is the naive first attempt and exactly where it breaks; lesson 5 covers Redlock's answer and Kleppmann's critique of that answer.
**Primary source:** [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
**Prerequisites:** [Lesson 3](0003-aof-and-wal-comparison.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ What does `appendfsync everysec` actually bound, and what does it not bound?

<details markdown="1"><summary>Check</summary>

It bounds AOF's data-loss window to roughly one second of writes on a crash. It does not bound RDB's separate save-interval loss window, and it says nothing about lock behavior at all: persistence and locking are unrelated guarantees.

</details>

2. ▢ Why does AOF need periodic rewriting?

<details markdown="1"><summary>Check</summary>

Because it logs every write command, so the file grows unbounded over time even for keys whose value has long since changed again; rewriting replaces the full history with the minimal commands needed to reconstruct the current dataset.

</details>

## Know this

### The naive lock: one command, one obvious hole

A distributed lock's job is to let only one client at a time hold a named resource. The naive Redis approach uses a single atomic command: `SET lock_key unique_value NX PX 30000`, which sets the key only if it doesn't already exist (`NX`), with a 30-second expiry (`PX`), so a crashed client's lock releases itself instead of blocking everyone forever. Releasing is a check-then-delete script that only deletes if `unique_value` still matches, so a client can't accidentally release a lock some other client now holds. On a *single* Redis instance, with no crashes, this is genuinely correct.

### Failure mode 1: the client stalls past the lock's expiry

The lock's TTL is a guess at "how long the critical section could possibly take," not a guarantee about it. If a client pauses for longer than that guess (a garbage-collection pause, a slow disk write, being descheduled by the OS, a slow network call it's waiting on) the lock expires while the client is still working. A second client then acquires the same lock and starts its own critical section, and now two clients believe they each hold exclusive access at the same time. The lock's *code* was correct: the assumption that "30 seconds is always enough" was not, and nothing in the design detects the violation when it happens.

### Failure mode 2: the single instance itself is the single point of failure

A lock held on exactly one Redis instance is only as available, and as correct, as that one instance. If it crashes after granting a lock but before that lock's key has been replicated to a replica, and a replica is then promoted to take over, the new primary has no record the lock was ever granted: a second client can acquire "the same" lock on the new primary while the first client still believes it holds it. Running the lock on a single instance was never actually distributed; it just looked that way until the instance failed at the wrong moment.

### Why the fix isn't "just use a bigger TTL" or "just add a replica"

A bigger TTL doesn't remove the possibility of a pause longer than the TTL, it only raises the bar; the failure mode is structural, not a tuning problem. A naive replica doesn't help either: Redis replication is asynchronous, so a lock key can be lost in exactly the crash-before-replication window described above, no matter how many replicas exist. Both failure modes come from the same root cause: a lock's correctness depends on an assumption (bounded pause time, or synchronous replication) that a single naive implementation doesn't actually enforce. Lesson 5 covers Redlock, the multi-instance algorithm designed to address the single-point-of-failure case, and Kleppmann's critique of whether it actually closes the pause-based failure mode too.

## Practice

1. ▢ A client acquires a lock with `SET lock_key val NX PX 30000`, then experiences a 45-second garbage-collection pause before finishing its critical section. What goes wrong, and whose "fault" is it: the lock code, or something else?

<details markdown="1"><summary>Check</summary>

The lock expires automatically at 30 seconds while the client is still paused, so a second client can acquire it and start its own critical section, and both clients now believe they exclusively hold the lock. The lock's code is correct; the failure is the assumption that 30 seconds was always long enough for the critical section, an assumption a GC pause (or any other unbounded stall) violates.

</details>

2. ▢ Why doesn't running the lock on a Redis primary with an asynchronous replica protect against losing a granted lock?

<details markdown="1"><summary>Hint</summary>

Consider exactly when the primary could crash relative to when the lock key gets copied to the replica.

</details>

<details markdown="1"><summary>Check</summary>

Asynchronous replication means the primary can acknowledge the lock to the client before the replica has received it. If the primary crashes in that window and the replica is promoted, the new primary has no record the lock was ever granted, so a second client can acquire what looks like "the same" lock on the new primary while the first client still believes it holds it.

</details>

3. ▢ Why doesn't simply raising the lock's TTL (say, from 30 seconds to 5 minutes) fix failure mode 1?

<details markdown="1"><summary>Check</summary>

It only raises the bar for how long a pause has to be before it causes the same problem; it doesn't remove the possibility of a pause exceeding whatever TTL is chosen. The failure mode is structural: the lock's correctness depends on bounding pause time, and no fixed TTL actually bounds it.

</details>

4. ▢ Name the two distinct root-cause assumptions the two failure modes each violate.

<details markdown="1"><summary>Check</summary>

Failure mode 1 violates the assumption that the critical section always finishes within the lock's TTL (bounded pause time). Failure mode 2 violates the assumption that a granted lock is durable across a primary failure (which requires synchronous, not asynchronous, replication of the lock key).

</details>

5. ▢ Which claim is true of the naive single-instance Redis lock?

    - a) It is safe as long as the TTL is set high enough
    - b) It is correct on a single instance with no crashes and no pauses exceeding the TTL, but neither condition is guaranteed in practice
    - c) Adding an asynchronous replica makes it safe against primary failure
    - d) The check-then-delete release script is unnecessary if the TTL is short

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, narrow scope in which the naive lock actually works, and exactly what's not guaranteed once it's deployed. (a) is false: a longer TTL only raises the bar for how long a pause has to be, it doesn't bound it. (c) is false: asynchronous replication can still lose a just-granted lock on failover. (d) is false: without the check, a client could delete a lock some other client now legitimately holds, once its own lock has expired.

</details>

## Real-world reps

- [ ] Find a place in a codebase you know of that uses Redis for mutual exclusion (a "lock", a "mutex", a "leader election" key). Identify whether it's the naive single-instance pattern from this lesson, and if so, which of the two failure modes it's actually exposed to.
- [ ] For that same lock, estimate a realistic worst-case pause (GC, network retry, disk stall) for the client process, and compare it against the TTL currently configured.
- [ ] Tomorrow: read the primary source's section describing the single-instance lock implementation in full, including its release script, before reading about Redlock in lesson 5.

## Going further

- [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Article: "How to do distributed locking", Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
