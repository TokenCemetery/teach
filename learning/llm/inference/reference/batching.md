---
title: Batching
description: Static versus continuous batching, request scheduling, and the throughput/latency trade-off a configuration has to defend
type: reference
---

# Batching

How a server turns [KV cache](kv-cache.md) capacity into served throughput. Built for lookup when tuning or defending a batching configuration.

## Static batching wastes capacity on uneven finish times

A decode step's memory traffic (reading the weights and every resident sequence's cache) barely changes whether it computes one sequence's next token or several at once, so batching decode steps together is close to free throughput. **Static batching** groups a fixed set of requests and runs decode steps until the longest one finishes; every sequence that finishes early still occupies a slot, doing nothing, until the whole group ends.

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**Worked example**, four requests needing 10, 20, 30, and 100 output tokens:

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

Waste grows with the spread between requests' lengths, which is the normal case.

## Continuous batching removes the batch boundary

**Continuous batching** (iteration-level scheduling) schedules at the level of a single decode step instead of a fixed group: the instant a sequence finishes, its slot is freed and a waiting request is admitted on the very next step. Batch size, not any one request's lifetime, is what stays roughly constant. The gain is not faster per-step computation; it is fewer slot-steps spent on sequences that had nothing left to do.

## Admission order and head-of-line blocking

The default admission policy is **first-come, first-served (FCFS)**: simple, and fair in the sense that no request waits behind one that arrived later. But every sequence sharing a batch step advances together, so admitting a new request's prefill work into the next step is fine when the prompt is short and damaging when it is long: a large prefill folded into one step dominates that step's latency, and every other sequence, even ones only needing a fast decode step, waits for it. That is **head-of-line blocking**: the queue is fine, but what's running now is not. FCFS alone does not cause or fix this; it only decides who gets admitted, not how much of their prefill lands in one step.

**Chunked prefill** splits a large prompt's prefill into pieces interleaved with the batch's ongoing decode steps, so each step admits only a bounded amount of new prefill work. The new request's own prefill takes more steps to finish; no other sequence in the batch stalls waiting for it. The final cache size for a fully processed prompt is unchanged, only how the work to get there is spread over time.

## The throughput/latency trade-off

Adding another sequence to a batch increases throughput (more tokens produced per second, aggregated across the batch) and increases per-token latency (every sequence in a step advances together, so a bigger step takes longer). They move together, not against each other independently.

| Regime | Bottleneck | Effect of adding another sequence |
|---|---|---|
| Small batch | Memory-bandwidth bound, same as plain decode | Throughput rises roughly linearly; latency barely moves |
| Large batch | Compute bound | Latency climbs noticeably; each added sequence buys less throughput than the last |

**Worked example**, a stack benchmarked at four batch sizes:

| Batch size | Per-token latency |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

## Defending a configuration

The defended batch size is the largest one satisfying both independent constraints, whichever binds tighter:

- **A latency budget**: a stated ceiling on inter-token latency.
- **The capacity ceiling**: [the KV cache's memory-derived maximum](kv-cache.md#capacity-budget), which says nothing about latency.

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**Worked example**, 30 ms/token budget, using the table above:

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

A batch size picked well under both constraints (say, 8 when 32 would still meet the budget) is not wrong, but it leaves throughput on the table the budget could have afforded.

## Related

- [Lesson 4](../lessons/0004-static-vs-continuous-batching.md), [Lesson 5](../lessons/0005-request-scheduling.md), [Lesson 6](../lessons/0006-throughput-latency-tradeoff.md)
- [KV cache](kv-cache.md): the capacity ceiling this sheet's defended-configuration formula depends on
