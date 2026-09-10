---
title: 14. Lua Scripting and Redis Functions
description: The mechanism that actually makes a lock's release safe, by running a check and an action as one atomic step
type: lesson
---

# Lesson 14. Lua Scripting and Redis Functions

**Mission link:** This is stage 8's capstone. Lesson 13 covered `WATCH`'s narrower optimistic-concurrency guarantee; this lesson is the mechanism strong enough to make lesson 4 and 5's lock actually safe to release, a server-side script that runs as a single, uninterruptible unit no matter how many separate operations it contains.
**Primary source:** [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
**Prerequisites:** [Lesson 13](0013-multi-exec-and-optimistic-locking-with-watch.md), [Eviction policy](../GLOSSARY.md)

## Warm-up

1. ▢ Why doesn't `MULTI`/`EXEC` roll back the rest of a queued transaction when one queued command fails at execution time?

<details markdown="1"><summary>Check</summary>

`MULTI`/`EXEC` guarantees nothing interleaves between queued commands, not all-or-nothing rollback on a runtime failure; only an error caught before `EXEC` starts (an unknown command, for instance) aborts the whole batch. A runtime failure in one queued command still lets the rest run.

</details>

2. ▢ Why is `WATCH`/`MULTI`/`EXEC` described as optimistic, in contrast to a lock, which is pessimistic?

<details markdown="1"><summary>Check</summary>

A lock blocks other clients from touching a resource while one client holds it. `WATCH` lets every client proceed without blocking, only checking at commit time whether the watched key actually changed, retrying if it did, assuming a conflict is uncommon enough to detect-and-retry rather than block upfront.

</details>

## Know this

### `EVAL`: a script that runs as one atomic step, not a sequence of round trips

`EVAL script numkeys key [key ...] arg [arg ...]` sends a Lua script to Redis, which runs it in full, atomically, as a single operation: no other client's command can execute in the middle of it, the same non-interleaving guarantee `MULTI`/`EXEC` gives a queued batch, except the whole check-then-act logic lives in one round trip instead of a `WATCH`, a client-side read, and a separate `EXEC`. `EVALSHA` runs a script Redis has already cached by its SHA1 hash, avoiding re-sending the script text on every call. `KEYS[1]`, `KEYS[2]`, and `ARGV[1]`, `ARGV[2]` inside the script refer to the keys and arguments passed positionally; keys have to be declared explicitly this way, not inferred by parsing the script's own logic, specifically so Redis Cluster can verify every key a script touches hashes to the same slot before running it at all (lesson 8's cross-slot constraint, applied here to a script instead of a multi-key command).

### Why this is what actually makes releasing a lock safe

Releasing lesson 4's lock correctly means "delete this key only if its value still matches the token I set when I acquired it," since deleting it unconditionally risks deleting a *different* client's lock if the original one already expired and got reacquired in between. Doing this as two separate round trips, `GET` to check, then `DEL` to release, leaves exactly the same kind of gap this entire mission has been naming since lesson 1: between the `GET` and the `DEL`, the lock could expire and another client could acquire it, and the original client's `DEL` would then delete that *other* client's lock instead of its own. A Lua script closes this gap entirely, since `if redis.call("GET", KEYS[1]) == ARGV[1] then return redis.call("DEL", KEYS[1]) end` runs as one atomic unit; no other client's command can run between the check and the delete, because nothing runs concurrently with the script at all. This is the actual mechanism the Redis documentation's own reference implementation of lock release uses, and precisely what makes lessons 4 and 5's lock buildable correctly rather than just described.

![Two panels showing a client releasing a lock it believes it holds. On the left, client-side: the client runs GET to check the lock's value matches its own token, then, separately, runs DEL. Between those two round trips, the lock could expire and be re-acquired by another client, whose lock this DEL would then incorrectly delete. On the right, a Lua script: the check and the delete happen inside one EVAL call, run atomically inside Redis with no other command able to interleave between the check and the delete, closing that window entirely.](images/lua-atomic-unlock.svg)

### Redis Functions: the same atomicity, with a real library instead of a pile of cached scripts

**Redis Functions** (`FUNCTION LOAD`, then `FCALL`) register a named, versioned server-side function once, rather than relying on `EVALSHA` and hoping the right script is still cached; a function library persists with the server itself (surviving a restart the way a plain cached `EVAL` script's SHA cache doesn't) and groups related functions together the way a real code library does. The atomicity guarantee is identical to `EVAL`, a function still runs as one uninterruptible unit; what changes is the operational story, a function is a deliberately deployed, named piece of server-side logic instead of an ad hoc script a client happens to send.

### Where the atomicity guarantee actually comes from, and its real cost

A script or function runs to completion before Redis processes anything else, because Redis itself is single-threaded for command execution; there's no separate thread for another client's command to interleave with a running script even if it wanted to. This buys real atomicity for free, but it also means a slow script (an expensive loop over a large collection, say) blocks every other client on that Redis instance for its entire duration, the same trade-off any single-threaded system makes between simplicity and the cost of one long-running operation blocking everything else.

## Practice

1. ▢ A client releases a lock with two separate commands: `GET lock`, checked client-side against its own token, then `DEL lock` if it matches. Describe the specific race this leaves open.

<details markdown="1"><summary>Hint</summary>

Consider what could happen to the lock in the gap between the `GET` and the `DEL`.

</details>

<details markdown="1"><summary>Check</summary>

Between the `GET` and the `DEL`, the lock's TTL could expire and a different client could acquire it (setting a new value). The original client's `DEL`, having already confirmed a match against the *old* value before this happened, would then delete the new client's lock, since `DEL` unconditionally removes whatever value is there now, not the value that was there when `GET` checked it.

</details>

2. ▢ Rewrite the release logic above as a single Lua script call, and explain why it closes the race the two-round-trip version has.

<details markdown="1"><summary>Check</summary>

`EVAL "if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('DEL', KEYS[1]) end" 1 lock <token>`. It closes the race because the check and the delete run as one atomic unit inside Redis; nothing else can run between them, so there's no window for the lock to expire and be reacquired between the moment it's checked and the moment it's (conditionally) deleted.

</details>

3. ▢ Why must a Lua script declare its keys via `KEYS[]` rather than embedding them directly in the script's own logic?

<details markdown="1"><summary>Check</summary>

Redis Cluster needs to know, before running a script, which keys it touches, so it can verify they all hash to the same slot (and therefore live on the same node) before allowing the script to run at all. Keys embedded inside the script's own string logic aren't visible to Redis without actually executing the script, defeating that upfront check; declaring them positionally via `KEYS[]` makes them inspectable in advance.

</details>

4. ▢ What does Redis Functions change compared to a plain `EVAL`/`EVALSHA` script, and what stays the same?

<details markdown="1"><summary>Check</summary>

What changes: a function is loaded once as a named, versioned part of a persistent library (surviving a restart, unlike a cached script's SHA), giving server-side logic a real deployment story instead of an ad hoc cached script. What stays the same: the atomicity guarantee itself, a function runs as one uninterruptible unit exactly like an `EVAL` script does.

</details>

5. ▢ Which claim correctly explains why a Lua script (or a Redis function) can safely check-then-act where two separate client commands can't?

    - a) Lua scripts run faster than two separate commands, which is why they're safer
    - b) Redis executes commands single-threaded, and a script runs to completion as one unit before anything else executes, so nothing can interleave between the check and the action inside it, unlike two separate round trips from a client
    - c) `EVAL` automatically retries if another client interferes, the same way `WATCH` does
    - d) Only `MULTI`/`EXEC`, not `EVAL`, provides this atomicity guarantee

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism: single-threaded execution plus a script running as one indivisible unit. (a) is false: speed isn't the safety property; atomicity is. (c) is false: `EVAL` doesn't retry anything; it simply never has a client-visible window where something else could interleave in the first place, so there's nothing to detect or retry. (d) is false: `EVAL` and Redis Functions provide the same non-interleaving atomicity `MULTI`/`EXEC` does, just for arbitrary script logic rather than a queued list of commands.

</details>

## Real-world reps

- [ ] Find (or recall) a lock-release implementation you have access to. Check whether it releases with a single atomic script or with separate `GET`-then-`DEL` round trips, and whether that gap has ever actually caused an incident.
- [ ] Write (on paper or for real) a Lua script implementing a simple "increment, but only if the result stays under a limit" check-and-act, and confirm it needs no `WATCH` at all, since the whole thing runs atomically.
- [ ] Tomorrow: read the primary source's reference implementation for lock release in full, and confirm it uses exactly the check-and-delete Lua pattern this lesson describes.

## Going further

- [Docs: "Distributed locks with Redis", Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
