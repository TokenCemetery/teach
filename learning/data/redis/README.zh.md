---
title: Redis
description: "按 Redis 的本来面目使用它：内存模型、淘汰、持久化，以及那些悄悄误用它的模式"
type: topic
---

# 学习：Redis

能够发现现有系统在哪里悄悄误用了 Redis，比如把缓存当成存储，或者一把其实不算锁的锁，并能从零设计出正确的用法。

**最新课程：** [17. ACL 与保护模式](lessons/0017-acls-and-protected-mode.md)

## 成功的标准

- 给定现有系统对 Redis 的使用，判断它是否把缓存当成了持久存储、锁的实现是否有误、键空间是否无界，并说出因此会出什么问题。
- 为新的用例从零设计正确的 Redis 用法（有界的键空间、合适的淘汰策略、真正的分布式锁）。
- 把 Redis 的持久化保证（RDB/AOF）与 Postgres 基于 WAL 的持久性作比较，并说出什么时候选用 Redis 而不是数据库是正确的决定，什么时候是反模式。
- 在集群引入的折中这一层面上推理 Redis Cluster/Sentinel，而不需要亲自运维它们。

## 约束

- 不要求有 Redis 经验。

## 范围之外

- 运维生产环境的 Postgres 实例：见 [`data/postgres`](../../data/postgres/)，为了比较而链接过去，不再重述。

## 学习路线

共十个阶段，从淘汰到访问控制。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 内存与淘汰 | 0001 | Redis 为什么会淘汰键，以及忘记这一点所导致的反模式 | 能解释淘汰策略对给定工作负载的影响 |
| 2. 持久化 | 0002 至 0003 | RDB 和 AOF，以及它们的持久性与 Postgres 的 WAL 相比如何 | 能说出什么时候选用 Redis 而不是数据库是正确的，什么时候是反模式 |
| 3. 分布式锁 | 0004 至 0005 | 朴素加锁的错误、Redlock、Kleppmann 的批评 | 能设计基于 Redis 的分布式锁，或正确地否决它 |
| 4. 缓存与存储的反模式 | 0006 至 0007 | 旁路缓存、被当作持久存储的缓存、无界的键空间 | 给定现有系统，能识别出误用并说出会出什么问题 |
| 5. 集群 | 0008 | Redis Cluster 和 Sentinel，集群引入的折中 | 能推理集群的权衡，而不需要亲自运维 |
| 6. 数据类型及其成本模型 | 0009 至 0010 | 字符串、哈希、列表、集合、有序集合、位图、HyperLogLog，以及如何在它们之间选择 | 能为给定的用例选择数据结构，并解释它的代价 |
| 7. 消息与过期 | 0011 至 0012 | Pub/Sub 与 stream 的对比、与 Kafka 相比的消费者组、惰性过期与主动过期 | 能为用例选出合适的消息机制，并解释一个键实际上如何离开 Redis |
| 8. 事务与脚本 | 0013 至 0014 | `MULTI`/`EXEC`、用 `WATCH` 做乐观锁、Lua 脚本、Redis Functions | 能构建真正安全的先检查后执行序列，并解释是什么让锁的释放成为原子操作 |
| 9. 性能与运维 | 0015 至 0016 | 往返成本、流水线、连接池、`INFO`/`SLOWLOG`/延迟监控/`MEMORY USAGE`、`SCAN` 与 `KEYS` 的对比 | 能降低频繁交互的客户端的网络成本，并在不冻结实例的情况下诊断它的实际行为 |
| 10. 访问控制 | 0017 | 保护模式、ACL、命令类别、默认用户 | 能分别限制未认证的连接和已认证的用户各自能做什么 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | 内存与淘汰 | Redis 为什么会淘汰键，以及忘记这一点所导致的反模式 |
| [0002](lessons/0002-rdb-snapshotting.md) | RDB 快照 | RDB 快照实际捕获了什么，以及它的保存间隔留下的数据丢失窗口 |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF 及其与 WAL 的比较 | AOF 的 fsync 策略如何决定它的数据丢失窗口，以及为什么即便是 Redis 最强的常用设置，也比 Postgres 的默认设置用更多的持久性换取速度 |
| [0004](lessons/0004-naive-locking-mistakes.md) | 朴素加锁的错误 | 为什么单靠 SET NX PX 不是分布式锁，以及在真实条件下让它失效的两种失败模式 |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock 与 Kleppmann 的批评 | Redlock 实际修复了朴素锁的哪些问题，Kleppmann 的批评表明它仍然没有修复什么，以及如何判断 Redis 锁究竟是不是合适的工具 |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | 旁路缓存与存储反模式 | 正确的旁路缓存用法是什么样的，以及跳过这种模式时，缓存如何悄悄变成记录系统 |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | 无界键空间反模式与发现误用 | 当没人为键空间设置 TTL 或淘汰策略时，它如何无限增长，以及一份用于在现有系统中发现这一问题和存储反模式的检查清单 |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster 与 Sentinel | Redis Cluster 的分片和 Sentinel 的自动故障转移各自引入的折中，无需亲自运维即可推理 |
| [0009](lessons/0009-strings-hashes-and-lists.md) | 字符串、哈希与列表 | Redis 实际存储的三种核心数据结构，以及每一种在读、写和增长上的代价 |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | 集合、有序集合与概率数据结构 | 为用例选择数据结构，从精确的成员判定，到维护成本几乎为零的近似计数 |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | 作为消息机制的 stream 与 Pub/Sub | Redis 在客户端之间传递消息的两种方式，以及为什么只有其中一种可以安全地用来构建队列 |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | 键过期：惰性过期与主动过期 | 为什么键的 TTL 归零并不会自行把它从内存中删除，以及最终完成删除的两种机制 |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC 与用 WATCH 做乐观锁 | 把多条命令排入队列、不被打断地执行，并在你据此行动之前，检测到某个值已在你不知情时被改动 |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Lua 脚本与 Redis Functions | 通过把检查和操作作为一个原子步骤来执行，真正让锁的释放变得安全的机制 |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | 流水线、往返成本与连接池 | 为什么 N 条顺序执行的命令要付出 N 次网络往返，尽管每条命令只需几微秒就能执行完，以及两种相互独立的解决办法 |
| [0016](lessons/0016-operational-visibility.md) | 运维可见性 | 展示 Redis 实例实际在做什么的工具，以及那条几乎比任何其他命令都引发过更多故障的命令 |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACL 与保护模式 | Redis 如何让未认证的实例根本无法被访问，并限定已认证的客户端实际被允许做什么 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [持久化](reference/persistence.md)：RDB 和 AOF 各自承诺了什么，每种 fsync 策略留下的确切丢失窗口，以及 Redis 自己的文档关于达到数据库级持久性是怎么说的
- [分布式锁](reference/distributed-locks.md)：朴素锁及其两个漏洞，Redlock 的算法及有效期的计算，以及决定二者是否为合适工具的那一个问题
- [缓存与存储的反模式](reference/cache-vs-store-anti-patterns.md)：正确的旁路缓存，缓存不再是缓存的两种方式，以及决定你会遇到哪种失败的淘汰设置
- [集群](reference/clustering.md)：Cluster 的槽位拿走了什么，决定降级的集群继续服务还是停止服务的设置，以及为什么 Sentinel 的法定人数并不控制故障转移

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
