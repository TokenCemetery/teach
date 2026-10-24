---
title: Postgres
description: "运维 Postgres：WAL、vacuum 与膨胀、复制，以及维护一个索引的代价"
type: topic
---

# 学习：Postgres

能够运维一个正在运行的 Postgres 实例（自建或托管），诊断膨胀、复制延迟或恢复缓慢的故障转移，而不是靠猜去修，并能从一开始就为新部署设计存储、复制和索引维护。

**最新课程：** [18. 分区与 TOAST](lessons/0018-partitioning-and-toast.md)

## 成功的标准

- 面对膨胀的表或滞后的副本，从 WAL、autovacuum 和复制的机制出发诊断原因，而不是反复试错。
- 为新部署设计存储、复制拓扑和索引维护，并为每个选择辩护。
- 解释托管服务（RDS 一类）能替你挡住什么、挡不住什么，并与自己运行实例对比。
- 说清向量索引（pgvector）给数据库带来的维护成本，与 `llm/rag` 选用 pgvector 作为存储的决定相衔接。

## 约束

- 假定具备基本的 SQL 知识（语言本身见 `programming/sql`）；不要求有数据库管理经验。
- 同时覆盖自建运维，以及在托管服务下会有哪些变化。

## 范围之外

- 查询、查询计划、schema 设计和隔离语义：见 [`programming/sql`](../../programming/sql/)，只链接过去，不再重述。本主题负责运行中的实例，而不是语言。

## 学习路线

共十二个阶段，从持久性到大规模的表级维护。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 预写日志 | 0001 | 本主题中其他一切所依赖的持久性机制 | 能解释 WAL 如何让崩溃变得可恢复 |
| 2. vacuum 与膨胀 | 0002 至 0003 | autovacuum 的内部机制、MVCC 与死元组、膨胀的诊断与调优 | 能从 vacuum 和 WAL 的机制出发诊断膨胀的表 |
| 3. 复制 | 0004 至 0006 | 流复制、复制槽、故障转移、延迟诊断 | 能诊断滞后的副本并设计复制拓扑 |
| 4. 索引及其维护成本 | 0007 至 0008 | B-tree/GiST/GIN 的维护成本、维护一个 pgvector 索引的代价 | 能设计索引维护计划，并说清 pgvector 的成本 |
| 5. 托管与自建 | 0009 至 0010 | RDS 一类托管服务能替你挡住什么、挡不住什么 | 能解释托管服务的边界，并为运维选择辩护 |
| 6. 备份与时间点恢复 | 0011 | 基础备份、持续 WAL 归档、`recovery_target_time`，以及为什么未经测试的恢复不算经过验证的备份 | 能设计一套经测试确实能重建出可用数据库的备份策略，并为之辩护 |
| 7. 配置与内存调优 | 0012 | `shared_buffers`、`work_mem`、`maintenance_work_mem`、检查点调优 | 能依据实际的并发来设定这些参数，而不是依据孤立的单查询测试 |
| 8. 监控 | 0013 | `pg_stat_activity`、等待事件、`pg_stat_statements`、服务器日志 | 能为给定的症状选出合适的监控入口（实时后端状态、聚合的查询成本，或一条日志事件） |
| 9. 连接管理 | 0014 | `max_connections`、每个连接一个进程的代价、PgBouncer 的会话/事务/语句池化模式 | 能选出与应用实际依赖相匹配的池化模式，而不是默认选最高效的那个 |
| 10. 逻辑复制与大版本升级 | 0015 至 0016 | 发布与订阅、逻辑复制对 DDL 的限制、`pg_upgrade` 的传输模式、低停机时间的逻辑复制升级路径 | 能在给定的停机预算下选择升级路径（原地 `pg_upgrade` 或逻辑复制切换）并为之辩护 |
| 11. 角色、权限与行级安全 | 0017 | 角色与其他系统中用户/组的划分、成员关系的 INHERIT/SET 选项、表级 GRANT、行级安全及其默认对属主放行 | 能设计角色和 RLS 策略的布局，并说出为什么仅仅启用 RLS 并不能限制表的属主 |
| 12. 分区与 TOAST | 0018 | 范围/列表/哈希分区、分区裁剪、无膨胀的批量删除、TOAST 及其四种存储策略 | 能为无膨胀的生命周期管理设计分区布局，并说清大字段的存储策略 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | 预写日志 | 本主题中其他一切所依赖的持久性机制 |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC 与死元组 | 为什么 UPDATE 或 DELETE 从不立即删除任何东西，以及为什么这会留下等待 vacuum 清理的死元组 |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | 膨胀诊断与 autovacuum 调优 | 如何度量膨胀，为什么 autovacuum 会落后，以及找到真正原因而不是靠猜的排查顺序 |
| [0004](lessons/0004-streaming-replication-and-slots.md) | 流复制与复制槽 | 备库实际上如何连接并追上主库，以及复制槽能保证什么是普通流复制保证不了的 |
| [0005](lessons/0005-failover-mechanics.md) | 故障转移的机制 | 备库被提升时会发生什么，为什么原来的主库不能直接重新加入，以及同步复制所限定的数据丢失权衡 |
| [0006](lessons/0006-diagnosing-replication-lag.md) | 诊断复制延迟 | 为什么接收延迟和应用延迟是不同的度量，以及找出实际发生的是哪一种的排查顺序 |
| [0007](lessons/0007-index-maintenance-cost.md) | B-Tree、GiST 与 GIN 的维护成本 | 为什么每个索引都会让写入更昂贵，以及 B-tree、GiST 和 GIN 各自如何以不同的方式付出这笔成本 |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | 维护一个 pgvector 索引的代价 | 向量索引在其所索引的原始向量之外，额外带来的磁盘、构建时间和常驻内存成本 |
| [0009](lessons/0009-what-managed-shields-you-from.md) | 托管服务能替你挡住什么 | RDS 一类的自动化实际去掉了什么，以及为什么前面各课的内容在它底下仍然需要理解 |
| [0010](lessons/0010-defending-an-operating-choice.md) | 为运维选择辩护 | 一个完整的部署设计实例，引用每个阶段的具体决策和成本，而不是假定一个默认答案 |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | 备份与时间点恢复 | 基础备份加上持续的 WAL 归档，让你能重建备份之后的任意时刻，而不只是备份本身所在的那一刻，而未经测试的恢复不算经过验证的备份 |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | 配置与内存调优 | shared_buffers、work_mem 和 maintenance_work_mem 各自回答一个不同的内存问题，而最常被调错的，正是那个会悄悄乘以实际同时运行的操作数的参数 |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | 监控：活动、语句与日志 | 每个后端此刻在做什么的实时视图，长期来看什么最耗服务器资源的聚合视图，以及准确说出一个卡住的查询被谁阻塞的日志，这是三个不同的问题 |
| [0014](lessons/0014-connection-management-and-pgbouncer.md) | 连接管理与 PgBouncer | 每个 Postgres 连接都是一个完整的操作系统进程，这就是为什么通常需要连接池，而 PgBouncer 的三种池化模式各自以不同方式用会话级的正确性换取复用效率 |
| [0015](lessons/0015-logical-replication-publications-and-subscriptions.md) | 逻辑复制、发布与订阅 | 流复制传输原始 WAL，构建一份完全相同的整集群副本；逻辑复制把同样的变更解码成行级事件，订阅方可以有选择地、跨大版本地应用，代价是它本身从不复制 DDL |
| [0016](lessons/0016-major-version-upgrades-and-pg-upgrade.md) | 大版本升级与 pg_upgrade | pg_upgrade 最快的传输模式以放弃简单回退的能力换取速度，而逻辑复制提供了一种真正不同的权衡：近乎零停机，代价是在整个迁移过程中手工处理 DDL |
| [0017](lessons/0017-roles-privileges-and-row-level-security.md) | 角色、权限与行级安全 | 表级 GRANT 和行级安全是两个独立的授权层，而启用 RLS 并不会限制表的属主，除非你明确要求它这样做 |
| [0018](lessons/0018-partitioning-and-toast.md) | 分区与 TOAST | 分区把全表扫描变成只扫描相关分区，并让批量删除不产生膨胀，而 TOAST 是单行能够容纳远大于 8kB 页面的值的原因 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [vacuum 与膨胀](reference/vacuum-and-bloat.md)：什么会触发 autovacuum、阈值是多少，什么会阻碍它回收空间，以及按什么顺序检查哪些视图
- [复制](reference/replication.md)：复制槽保证什么、带来什么风险，五个同步级别以及其中三个何时毫无作用，以及两种延迟和区分它们的列
- [索引维护](reference/index-maintenance.md)：每种索引类型每次写入的开销以及什么会让它退化，以及 pgvector 索引带来的参数和内存悬崖
- [托管与自建](reference/managed-vs-self-hosted.md)：托管服务自动化了什么、只是转移了什么，三种不可互换的高可用形态，以及一个经过论证的设计必须说明的决策

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
