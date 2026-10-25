---
title: Stream Processing
description: "用 Kafka Streams 在流上做计算：拓扑、状态、窗口与连接，以及一个拓扑在进入生产环境之前的代价"
type: topic
---

# 学习：流处理

能够构建、测试并运行一个 Kafka Streams 应用，在记录迟到、乱序或重复到达时仍给出正确答案，并能在它进入生产环境之前，从它的拓扑说出它会带来哪些内部 topic、多少状态和多长的恢复时间。

**最新课程：** [20. 修改别人依赖的拓扑](lessons/0020-changing-a-topology-others-depend-on.md)

## 成功的标准

- 从流表二元性出发，解释 topic、changelog 和 KTable 之间的关系，并预测一个拓扑对给定的输入会输出什么。
- 用 DSL 构建拓扑，读懂 `describe()` 的输出，并说出它创建的每个内部 topic 及其原因。
- 为有状态操作选择状态存储，并说明持有它的实例宕掉后，其状态如何重建。
- 为一个与时间相关的问题选择窗口和宽限期，并说明它会丢弃哪些迟到的记录、何时输出结果。
- 为两个输入选择连接方式，使它们共分区，或说明为什么 GlobalKTable 可以免去这一要求，并预测连接的输出。
- 说出 `exactly_once_v2` 保证了什么、没有覆盖什么，并为给定的恢复时间确定应用的任务、线程、实例和备用副本的规模。
- 用 `TopologyTestDriver` 测试拓扑，并依据指标、状态和异常处理器运维正在运行的应用。
- 为一个工作负载在 Kafka Streams、普通消费者、Flink 和 ksqlDB 之间做出选择，评审别人的拓扑，并在不破坏其状态和下游消费者的前提下修改正在运行的拓扑。

## 约束

- 要求具备可用的 Java 能力，并掌握 [`data/kafka`](../../data/kafka/) 所讲的日志：分区、消费者组、投递保证、保留与压缩。这些课程会链接回那里，不再重新推导。
- 只讲 Kafka Streams 这一个引擎。示例使用 Apache Kafka 4.3 的 Java DSL 和 Processor API。
- 默认值和协议会随版本变化。课程引用其中某个值时，会注明它出自哪个文档页面或 KIP，读者应到该页面核对当前值。

## 范围之外

- 日志本身：分区、消费者组、投递语义、事务的代价、保留与压缩、Kafka Connect 和 Schema Registry。见 [`data/kafka`](../../data/kafka/)，本主题建立在它之上。
- 作为理论的部分失败与一致性：见 [`architecture/distributed-systems`](../../architecture/distributed-systems/)。本主题只讲状态存储的恢复和再均衡对 Streams 应用意味着什么。
- 作为独立主题的 Apache Flink、Spark Structured Streaming 和 ksqlDB。第 8 阶段把它们作为某个工作负载的候选方案与 Kafka Streams 比较，但不讲如何运行它们。
- Java 语言：见 [`programming/java`](../../programming/java/)。
- 把流加载进分析型数据仓库：见 [`data/warehouses`](../../data/warehouses/)。

## 学习路线

共八个阶段，从流表二元性到判断力。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 流与表 | 0001 至 0002 | 流表二元性、作为表的压缩 topic、Streams 应用运行什么以及在哪里运行 | 能说出一个 topic 是作为流还是作为表来读，以及 Streams 应用在消费者之上增加了什么 |
| 2. 拓扑 | 0003 至 0004 | DSL，源、处理器和汇，`describe()`，Serdes，无状态操作，键变更与重分区 topic | 能读懂一个拓扑，并说出它创建的每个内部 topic |
| 3. 状态 | 0005 至 0007 | 状态存储、changelog topic、聚合、KTable 更新、记录缓存、Processor API 与 punctuator | 能为有状态的步骤选择存储，并说明实例宕掉后其状态如何保住 |
| 4. 时间与窗口 | 0008 至 0010 | 事件时间、处理时间与流时间，时间戳提取器，滚动、跳跃、滑动和会话窗口，宽限期，抑制 | 能为一个问题选择窗口和宽限期，并说出它会丢弃哪些记录 |
| 5. 连接 | 0011 至 0012 | 流表连接与 GlobalKTable 连接、共分区、带窗口的流流连接、表表连接与外键连接 | 能为两个输入选择连接方式，并预测它输出什么 |
| 6. 保证与扩展 | 0013 至 0015 | `exactly_once_v2`，任务、线程与实例，再均衡，状态恢复，备用副本与预热副本，streams 再均衡协议 | 能说出恰好一次覆盖了什么，并为给定的恢复时间确定应用的规模 |
| 7. 测试与运维 | 0016 至 0017 | `TopologyTestDriver`、指标、客户端与线程状态、异常处理器、交互式查询、运维工具 | 能在没有 broker 的情况下测试拓扑，并从指标判断正在运行的应用是否健康 |
| 8. 判断力 | 0018 至 0020 | Streams 与普通消费者、Flink 和 ksqlDB 的对比，评审拓扑，修改别人依赖的拓扑，依据一手资料裁定争议 | 可以信赖他做出判断，并向别人解释清楚 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | 流与表 | 为什么变更的流和当前值的表是同一份数据的两种视图，以及一个 topic 如何承载其中任意一种 |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | Streams 应用是一个库 | Kafka Streams 应用启动时运行的是什么：在你自己的进程里运行的消费者、生产者和本地状态，没有它自己的集群 |
| [0003](lessons/0003-the-dsl-and-topologies.md) | DSL 与拓扑 | DSL 调用如何构建由源、处理器和汇组成的拓扑，以及如何从 `describe()` 读懂它 |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | 无状态操作与重分区 | 哪些操作一次只转换一条记录，以及哪种键变更会让下一个有状态步骤写入重分区 topic |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | 状态存储与 changelog topic | 有状态操作把状态保存在哪里，以及压缩的 changelog topic 如何让另一个实例重建它 |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | 聚合、KTable 与记录缓存 | 为什么 KTable 输出的是更新流而不是最终答案，以及记录缓存和提交间隔如何决定输出多少条 |
| [0007](lessons/0007-the-processor-api.md) | Processor API | 什么时候要从 DSL 下沉到带有自己的存储和 punctuator 的自定义处理器，以及那时你要负责什么 |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | 事件时间、处理时间与流时间 | Streams 操作遵循哪个时钟，记录的时间戳从哪里来，以及为什么流时间只会向前走 |
| [0009](lessons/0009-windowed-aggregations.md) | 窗口聚合 | 滚动、跳跃、滑动和会话窗口如何按时间对记录分组，以及每种窗口回答什么问题 |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | 迟到数据、宽限期与抑制 | 窗口接受乱序记录的时间有多长，之后到达的记录会怎样，以及如何只输出最终结果 |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | 流表连接与共分区 | 流如何用表中的数据丰富每条记录，为什么两边必须共分区，以及什么时候 GlobalKTable 可以免去这一要求 |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | 流流连接与表表连接 | 带窗口的连接如何把两个流中的事件配对，以及表连接（包括外键连接）如何让结果保持最新 |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | Kafka Streams 中的恰好一次 | `exactly_once_v2` 让读取、状态和写入中的什么成为原子操作，以及它无法覆盖哪些副作用 |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | 任务、线程与横向扩展 | 分区如何变成任务，任务如何分布到线程和实例上，以及什么限制了应用的并行度 |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | 再均衡、恢复与备用副本 | 任务迁移时状态会怎样，以及备用副本和预热副本如何缩短状态不可用的时间 |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | 用 TopologyTestDriver 测试 | 如何在没有 broker 的单元测试中测试拓扑的输出、状态和时间行为 |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | 运维和监控 Streams 应用 | 哪些指标、状态和异常处理器能告诉你正在运行的应用是否健康，以及不健康时该怎么办 |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | 什么时候 Kafka Streams 是错误的工具 | 什么时候普通消费者、Flink 或 ksqlDB 比 Streams 应用更适合某个工作负载，以及如何为这个选择辩护 |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | 评审别人的拓扑 | 如何评审一个 Streams 拓扑，并说出每个选择在内部 topic、状态和正确性上的代价 |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | 修改别人依赖的拓扑 | 如何在不损坏状态、不破坏下游消费者的前提下修改正在运行的应用的拓扑，以及如何依据一手资料裁定有争议的说法 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [DSL 操作](reference/dsl-operations.md)：按输入和输出类型列出每个 DSL 操作，以及它是否保存状态、是否重分区
- [状态存储](reference/state-stores.md)：存储类型、changelog 设置、记录缓存，以及状态如何恢复
- [时间与窗口](reference/time-and-windows.md)：三种时钟、四种窗口类型、宽限期，以及每种窗口何时输出
- [连接](reference/joins.md)：连接矩阵，包括窗口、共分区以及每种连接输出什么
- [配置](reference/configuration.md)：决定保证、延迟、并行度和恢复的设置及其默认值
- [运维](reference/operations.md)：需要关注的指标、客户端与线程状态、异常处理器和运维工具
- [拓扑评审](reference/topology-review.md)：评审拓扑的检查清单、工具选择，以及安全与不安全的拓扑修改

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
