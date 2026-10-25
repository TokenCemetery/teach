---
title: Kafka
description: "掌握日志：分区、消费者组、投递保证，以及“恰好一次”实际的代价"
type: topic
---

# 学习：Kafka

能够为真实的工作负载设计 topic 和分区布局，并诊断消费者延迟、再均衡风暴或意外的消息丢失，而不是靠猜去修。

**最新课程：** [16. 运维集群时真正重要的指标](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## 成功的标准

- 为给定的工作负载设计 topic、分区和消费者组的布局，并为背后的投递保证选择辩护。
- 面对持续滞后或反复再均衡的消费者，诊断出是哪项设置或哪种使用模式出了问题。
- 说清“恰好一次”实际的代价，以及什么时候至少一次加幂等处理是更好的权衡。

## 约束

- 不要求有 Kafka 或消息系统的经验。
- 以 Apache Kafka 作为参照实现；不涉及替代品（Redpanda、托管服务）。
- 在仅凭日志的保证无法解释真实流水线如何搭建的地方，简要涉及周边生态（Schema Registry、Kafka Connect 基础）。

## 范围之外

- 投递保证背后的失败模型本身：见 [`architecture/distributed-systems`](../../architecture/distributed-systems/)，只链接过去，不在这里重新推导。
- Kafka Streams 以及基于日志的计算（拓扑、状态、窗口、连接）：见 [`data/stream-processing`](../../data/stream-processing/)，投递语义部分则链接回这里。作为独立主题的 ksqlDB。

## 学习路线

共十个阶段，从日志到在生产环境中运维集群。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 分区与日志 | 0001 | 其他一切（顺序、并行、消费者组）都围绕它构建的那个单元 | 能解释为什么分区是顺序和并行的单元 |
| 2. 消费者组与再均衡 | 0002 至 0003 | 组协调、协作式再均衡、消费者延迟 | 能诊断持续滞后或反复再均衡的消费者 |
| 3. 投递保证 | 0004 至 0005 | 至多一次、至少一次、恰好一次语义，幂等生产者，事务 | 能为投递保证的选择辩护，并说清恰好一次的代价 |
| 4. 设计布局 | 0006 至 0007 | 键的选择、分区数的权衡、顺序保证 | 能为给定的工作负载设计 topic 和分区布局 |
| 5. 周边生态 | 0008 至 0009 | Schema Registry、Kafka Connect 基础 | 能解释它们在真实流水线中如何围绕日志工作 |
| 6. 保留与复制 | 0010 至 0011 | `cleanup.policy`、日志压缩、副本因子、ISR、`acks`、`min.insync.replicas`、非干净领导者选举 | 能为 topic 数据保留多久，以及其复制设置实际保证了怎样的持久性辩护 |
| 7. 负载下的客户端配置 | 0012 | `batch.size`、`linger.ms`、`fetch.min.bytes`、`max.poll.interval.ms` | 能把吞吐量、延迟或无谓再均衡的症状，对应到解决它的具体客户端设置 |
| 8. 集群协调 | 0013 | KRaft、控制器法定人数、`process.roles`、取代 ZooKeeper 的东西 | 能解释控制器法定人数做什么，以及为什么 KRaft 故障转移无需完整地重新拉取元数据 |
| 9. 安全与多租户 | 0014 至 0015 | TLS、SASL、`security.protocol`、ACL、默认拒绝、配额 | 能说出某个安全问题实际涉及哪种机制（加密、认证、授权或资源隔离） |
| 10. 运维集群 | 0016 | `UnderReplicatedPartitions`、`UnderMinIsr`、磁盘余量、请求延迟、请求处理线程饱和 | 能说出某个运维症状属于三类信号中的哪一类，并分辨是单个 broker 的问题还是整个集群的问题 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | 分区与日志 | 本主题中其他一切（顺序、并行、消费者组）都围绕它构建的那个单元 |
| [0002](lessons/0002-consumer-group-coordination.md) | 消费者组协调 | 组协调者和组领导者如何在消费者之间分配分区，以及位移如何跟踪每个组的进度 |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | 协作式再均衡与诊断消费者延迟 | 为什么最初的再均衡协议会引发再均衡风暴，协作式再均衡如何缩小它的影响，以及诊断消费者延迟的排查顺序 |
| [0004](lessons/0004-delivery-semantics.md) | 至多一次、至少一次与恰好一次 | 在生产、broker 和消费这几段路径上，每种投递保证究竟是在哪里得到或失去的 |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | 幂等生产者与事务 | 为什么幂等几乎是免费的，而事务才承担了恰好一次的真正代价 |
| [0006](lessons/0006-partition-key-choice.md) | 分区键的选择与顺序保证 | 选择分区键，就是在同一个决策中同时选定你得到怎样的顺序、放弃多少并行度 |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | 分区数的权衡与设计 topic 布局 | 为什么更多的分区并非没有代价，以及一个经过充分论证的 topic 布局必须说明之前每个阶段的哪些内容 |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | 在生产时就拦截不兼容的 schema 变更，如何取代在下游消费时才悄无声息地出错 |
| [0009](lessons/0009-kafka-connect-basics.md) | Kafka Connect 基础 | Connect 的任务和 worker 模式如何提供并行与容错，以及为什么 Connect 不提供底层生产者或消费者 API 本来没有提供的任何保证 |
| [0010](lessons/0010-retention-and-log-compaction.md) | 保留与日志压缩 | 一条消息在 topic 中实际能存活多久，以及另一种按键保留历史、而不是按时间保留的清理策略 |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | 复制、ISR、acks 与非干净领导者选举 | acks=all 实际在等待什么，防止它悄悄变得比听起来更弱的那条下限，以及所有同步副本都不在时的权衡 |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | 负载下的生产者与消费者配置 | 用延迟换吞吐量的客户端旋钮，以及那个可能让一个从未真正死掉的消费者触发再均衡的旋钮 |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft，以及取代 ZooKeeper 的东西 | 在外部协调服务消失之后，集群如何就自己的元数据达成一致，以及为什么故障转移时完整地重新拉取状态是值得解决的问题 |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS 与 SASL：向集群认证 | 加密通道和认证客户端是两项独立的工作，security.protocol 把它们合并在一个设置里，而混淆二者正是大多数困惑的起点 |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACL 与配额：授权与多租户 | 一个通过认证的主体，在 ACL 允许之前仍然无权做任何事，而一个被允许操作的主体，仍然不能防止它耗尽集群的容量、饿死其他所有租户 |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | 运维集群时真正重要的指标 | 副本不足的分区、磁盘余量和请求延迟是值得关注的三种信号，每一种都指向不同类型的问题 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [消费者组与再均衡](reference/consumer-groups-and-rebalancing.md)：两种再均衡协议、两个相互独立的存活超时，以及诊断消费者延迟的排查顺序和支配每一步的配置
- [投递保证](reference/delivery-guarantees.md)：哪项配置决定路径的哪一段，为什么幂等可能被悄悄关闭，以及 read_committed 消费者实际在等待什么
- [topic 与分区设计](reference/topic-and-partition-design.md)：一条记录实际如何到达某个分区，这能换来什么顺序、换不来什么，以及分区数在两个方向上修改都很昂贵
- [生态](reference/ecosystem.md)：七种兼容性类型以及每种类型下谁必须先升级，以及 Kafka Connect 在日志周围增加了什么，包括那项默认关闭的保证

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
