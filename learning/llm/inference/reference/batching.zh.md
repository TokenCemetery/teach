---
title: "批处理"
description: "静态批处理与连续批处理、请求调度，以及一套配置必须为之辩护的吞吐量与延迟的权衡"
type: reference
---

# 批处理

服务器如何把 [KV 缓存](kv-cache.md)容量变成实际提供的吞吐量。为在调优或辩护批处理配置时查阅而做。

<a id="static-batching-wastes-capacity-on-uneven-finish-times"></a>

## 静态批处理会因完成时间参差不齐而浪费容量

一个解码步的内存流量（读取权重和每个驻留序列的缓存），无论是只算一个序列的下一个 token，还是同时算好几个，几乎都不变，所以把解码步批在一起，几乎是白得的吞吐量。**静态批处理**把一组固定的请求编在一起，一直运行解码步，直到最长的那个完成；提前完成的序列仍然占着一个槽位什么也不做，直到整组结束。

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**算例**，四个请求分别需要 10、20、30 和 100 个输出 token：

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

浪费随请求长度之间的差距而增大，而这正是常态。

## 连续批处理去掉了批次的边界

**连续批处理**（迭代级调度）以单个解码步而不是固定的一组为单位来调度：一个序列一完成，它的槽位就被释放，等待中的请求在紧接着的下一步被接纳。保持大致恒定的是批大小，而不是任何一个请求的生命周期。它的收益不是每步计算变快了，而是更少的槽位步数花在已经无事可做的序列上。

<a id="admission-order-and-head-of-line-blocking"></a>

## 接纳顺序与队首阻塞

默认的接纳策略是**先到先服务（FCFS）**：简单，而且公平，因为没有请求需要排在后到的请求后面。但是共用一个批次步的每个序列是一起前进的，所以把新请求的预填充工作接纳进下一步，在提示词短的时候没问题，在提示词长的时候就有害：一个大的预填充并进一步里，会主导这一步的延迟，批次里其他所有序列，即使只需要一个很快的解码步，也要等着它。这就是**队首阻塞**：队列没问题，有问题的是当前正在运行的东西。FCFS 本身既不造成也不解决这个问题；它只决定谁被接纳，不决定他们的预填充有多少落在一步里。

**分块预填充**把一个大提示词的预填充拆成若干块，与批次中正在进行的解码步交错执行，使每一步只接纳有限量的新预填充工作。新请求自己的预填充需要更多的步数才能完成；批次里其他序列都不会因为等它而停滞。一个提示词处理完之后最终的缓存大小不变，变的只是抵达那里的工作在时间上如何摊开。

<a id="the-throughputlatency-trade-off"></a>

## 吞吐量与延迟的权衡

给批次增加一个序列，会提高吞吐量（每秒产出的 token 更多，是整个批次汇总的），也会提高每 token 延迟（一步中的每个序列一起前进，所以更大的一步要花更长时间）。二者是一起变化的，而不是各自独立地互相对立。

| 状态 | 瓶颈 | 再增加一个序列的效果 |
|---|---|---|
| 小批次 | 受内存带宽限制，与普通解码相同 | 吞吐量大致线性上升；延迟几乎不动 |
| 大批次 | 受算力限制 | 延迟明显攀升；每多加一个序列换来的吞吐量，比上一个更少 |

**算例**，一套服务栈在四个批大小下做了基准测试：

| 批大小 | 每 token 延迟 |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

<a id="defending-a-configuration"></a>

## 为一套配置辩护

要辩护的批大小，是同时满足两个独立约束的最大值，哪个约束更紧就由哪个决定：

- **延迟预算**：对 token 间延迟规定的上限。
- **容量上限**：[由内存推出的 KV 缓存最大值](kv-cache.md#capacity-budget)，它对延迟只字不提。

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**算例**，30 ms/token 的预算，使用上面的表：

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

选的批大小远低于两个约束（比如 32 仍然满足预算，却选了 8），并不算错，但它把预算本来承受得起的吞吐量留在了桌上。

## 相关内容

- [第 4 课](../lessons/0004-static-vs-continuous-batching.md)、[第 5 课](../lessons/0005-request-scheduling.md)、[第 6 课](../lessons/0006-throughput-latency-tradeoff.md)
- [KV 缓存](kv-cache.md)：本表中被辩护配置的公式所依赖的容量上限
