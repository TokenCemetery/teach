---
title: 5. Redlock and Kleppmann's Critique
description: What Redlock actually fixes about the naive lock, what Kleppmann's critique shows it still doesn't, and how to decide whether a Redis lock is the right tool at all
type: lesson
---

# Lesson 5. Redlock and Kleppmann's Critique

**Mission link:** This is stage 3's capstone: lesson 4 showed the naive lock's two failure modes; Redlock is Redis's own answer to one of them, and Kleppmann's critique is the specific reason the mission treats "a lock that is not one" as a real anti-pattern rather than a solved problem.
**Primary source:** [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
**Prerequisites:** [Lesson 4](0004-naive-locking-mistakes.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ Name the two failure modes of the naive single-instance Redis lock from lesson 4.

<details markdown="1"><summary>Check</summary>

A client stalling (GC pause, slow disk, descheduling) past the lock's TTL, so a second client acquires the "same" lock while the first still believes it holds it; and the single instance itself failing after granting a lock but before asynchronous replication copies it, so a promoted replica has no record the lock existed.

</details>

2. ▢ Why doesn't raising the TTL fix the stall-based failure mode?

<details markdown="1"><summary>Check</summary>

It only raises the bar for how long a pause has to be before triggering the same problem; it doesn't bound pause time, which is the actual assumption the lock's correctness depends on.

</details>

## Know this

### Redlock's fix targets the single-point-of-failure mode specifically

**Redlock** addresses lesson 4's second failure mode by running the lock against N independent Redis instances (Redis recommends 5) instead of one. A client attempts to acquire the same lock key on every instance, using the same short network timeout for each attempt, and considers the lock acquired only if it got a majority (at least N/2 + 1) within roughly the lock's validity time. Because a majority of independent instances would all have to fail, or be network-partitioned from the client, in the same window for this to go wrong, Redlock removes any single instance as a single point of failure the way the naive lock had one.

### What Redlock does not touch: the pause-based failure mode

Redlock says nothing new about lesson 4's first failure mode. A client that acquires the lock across a majority of instances can still stall past the lock's validity time before finishing its critical section, for exactly the same reasons as before (GC pause, slow disk, descheduling, a slow network call). Multiplying the number of instances a lock lives on doesn't bound how long a client's own pause can be; it only makes losing the lock to instance failure harder, a different problem than the one a stalled client causes.

### Kleppmann's critique: the fencing token gap

Kleppmann's critique targets exactly this gap. His argument: a distributed lock used to protect a shared resource (a file, a database row, a downstream API call) is only actually safe if the *protected resource itself* can detect and reject a stale client, one whose lock has already expired. The standard fix for this is a **fencing token**, a monotonically increasing number handed out with each lock grant that the protected resource checks and rejects if it's lower than one already seen. Kleppmann's point isn't that Redlock's algorithm has a bug; it's that Redlock, as commonly used, protects access to the lock itself without also requiring the fencing token that would make the *protected resource* correct under a pause, and that Redlock's timing assumptions (bounded clock drift, bounded network delay) are difficult to guarantee in practice, which is where its safety margin actually comes from.

### The actual decision, not "Redlock is broken"

This isn't a reason to treat Redlock, or Redis-based locks generally, as unusable. It's a reason to ask a sharper question before reaching for one: does the protected resource enforce a fencing token, making a stale client's action harmless even if it acts after its lock expired? If yes, a Redis-based lock (naive or Redlock) is a reasonable efficiency mechanism, since fencing is the actual safety net. If the protected resource *can't* enforce a fencing token, whether because it's a legacy system, an external API, or a physical action with no way to reject a stale caller, a Redis lock alone is not a correctness guarantee, no matter how many instances it runs on. This is the concrete shape of "a lock that is not one": not that the code is wrong, but that it's being asked to guarantee something it structurally can't guarantee alone.

## Practice

1. ▢ What specific failure mode does running Redlock across 5 independent instances fix, and how does it fix it?

<details markdown="1"><summary>Check</summary>

It fixes the single-point-of-failure mode: since acquiring the lock requires a majority (3 of 5) of independent instances to agree, a single instance crashing or losing a lock key to an unreplicated failover no longer breaks the lock, because the other instances still hold it.

</details>

2. ▢ Does Redlock fix the pause-based failure mode from lesson 4 (a client stalling past the lock's validity time)? Justify the answer.

<details markdown="1"><summary>Hint</summary>

Consider what "acquiring the lock on a majority of instances" does and doesn't say about the client's own execution time afterward.

</details>

<details markdown="1"><summary>Check</summary>

No. Redlock only changes how many instances have to agree the lock is held; it says nothing about how long the client's critical section is allowed to take. A client can still stall (GC pause, slow disk, descheduling) past the lock's validity time after acquiring it across a majority of instances, and a second client can then acquire the same lock while the first still believes it holds it, the exact same shape of failure as the naive single-instance case.

</details>

3. ▢ What is a fencing token, and what problem does Kleppmann argue it solves that Redlock alone doesn't?

<details markdown="1"><summary>Check</summary>

A fencing token is a monotonically increasing number handed out with each lock grant, which the *protected resource* (not the lock itself) checks and rejects if it's lower than one already seen. It solves the problem of a client acting on a shared resource *after* its lock has already expired: without a fencing check at the resource itself, the resource has no way to know the caller's lock is stale and rejects the action, so the lock alone can't guarantee exclusivity once a client has paused past its validity time.

</details>

4. ▢ A team protects writes to a legacy on-premises system with a Redlock-based lock. The legacy system has no way to reject a request based on a fencing token or any other staleness marker. Is this a defensible use of Redlock? Why or why not?

<details markdown="1"><summary>Check</summary>

Not on its own. Since the protected resource can't reject a stale, paused client's write, Redlock's guarantee that a majority of instances agree on who holds the lock doesn't prevent a stalled client from writing after another client has already acquired the "same" lock. This is exactly the anti-pattern Kleppmann's critique targets: the lock alone is being asked to guarantee correctness that only the protected resource, via fencing, can actually provide.

</details>

5. ▢ Which claim best summarizes Kleppmann's critique of Redlock?

    - a) Redlock's majority-quorum algorithm is implemented incorrectly and doesn't actually tolerate instance failure
    - b) Redlock fixes the single-instance failure mode, but without a fencing token enforced at the protected resource, a paused client can still act after its lock has expired
    - c) Distributed locks built on Redis should never be used under any circumstances
    - d) Kleppmann's critique only applies to Redis and has no equivalent in other distributed lock designs

<details markdown="1"><summary>Check</summary>

**b)** That's the precise gap: Redlock genuinely fixes the instance-failure mode, but the pause-based mode requires a fencing token enforced where the resource is actually accessed, not just agreement among lock-holding instances. (a) is false: the quorum algorithm itself works as designed for instance failure. (c) is false: a Redlock-protected resource that also enforces fencing is a defensible design. (d) is false: the fencing-token requirement is a general property of any lock protecting a resource under possible client pauses, not Redis-specific.

</details>

## Real-world reps

- [ ] For the Redis-based lock you identified in lesson 4's rep, check whether the resource it protects can reject a stale (already-expired) caller in any way. If it can't, that's the concrete gap this lesson describes.
- [ ] Sketch, for that same resource, what a fencing token check would need to look like (a monotonically increasing value the resource stores and compares against).
- [ ] Tomorrow: read the primary source's section on Redlock's algorithm and its stated assumptions (clock drift, network delay bounds) in full, then read Kleppmann's article for the counter-argument in the author's own words.

## Going further

- [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Article: "How to do distributed locking", Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
