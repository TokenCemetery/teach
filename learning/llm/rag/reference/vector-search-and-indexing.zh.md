---
title: "向量搜索与索引"
description: "IVF 和 HNSW 在召回率与延迟之间的权衡，以及 pgvector 的运算符、索引参数和构建顺序上的细节"
type: reference
---

# 向量搜索与索引

近似最近邻搜索及其在 pgvector 中的实现。便于在搭建或调节索引时查阅。

## 为什么精确搜索无法扩展

精确的最近邻搜索要把查询与每个向量比较：与语料库大小成线性关系，到了几百万个文本块就太慢了。**近似最近邻**（ANN）索引接受少量、可控的不精确，换来不随规模线性增长的搜索时间。

## IVF 和 HNSW

| 索引 | 机制 | 搜索时的旋钮 | 构建成本 |
|---|---|---|---|
| IVF（倒排文件） | 提前把向量划分成若干簇（k-means）；只搜索最近的 `nprobe` 个簇 | `nprobe`：低则快，可能漏掉簇边界附近的近邻；高则接近精确搜索 | 需要语料库中有代表性的样本，才能把簇中心放好 |
| HNSW（分层可导航小世界） | 多层图；上面稀疏的层用于长距离跳跃，最底下稠密的一层用于精确的局部搜索，贪心地逐层下降 | `ef_search`：每一步跟踪多少个候选；低则快，但可能满足于局部不错的节点；高则召回率更高 | 比 IVF 内存开销更大（图的边），索引构建也更慢 |

两个旋钮都是针对给定的语料库，在**召回率与延迟曲线**上拨到某个点；没有哪个设置是放之四海而皆准的。HNSW 通常能在这条曲线上达到比 IVF 更好的点（同样延迟下召回率更高），代价是内存和构建时间。合适的点取决于工作负载的延迟预算，以及后面的阶段（重排序）能吸收多少召回损失，这要靠度量，而不是想当然。

## pgvector：列、运算符、索引

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| 运算符 | 距离 | 运算符类（用于建索引） |
|---|---|---|
| `<->` | 欧氏距离 / L2 | `vector_l2_ops` |
| `<#>` | 负内积 | `vector_ip_ops` |
| `<=>` | 余弦 | `vector_cosine_ops` |

`<#>` 特意取 *负* 内积，是为了和另外两个运算符一样，越小越相似，使三者的 `ORDER BY` 升序保持一致。运算符必须与[嵌入模型训练时针对的度量](chunking-and-embeddings.md#similarity-metrics-must-match-training)相匹配：对一个按点积训练的模型使用 `<=>`（或者反过来），就是同样的度量不匹配，只不过现在表现为一个具体的 SQL 选择。

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**索引是针对某一个特定的距离函数构建的。** 按与索引的运算符类不匹配的运算符排序的查询，根本不会使用这个索引：它会悄悄退回到全表顺序扫描，丢掉索引本该提供的全部性能收益。距离函数之间不存在自动转换。

## pgvector 的参数，就是第 4 课的那些参数，只是改了名字

| 概念 | HNSW | IVFFlat |
|---|---|---|
| 构建时参数 | `m`（每个节点的最大连接数）、`ef_construction`（构建时的搜索深度），在 `CREATE INDEX` 时设置 | `lists`（簇数量），在 `CREATE INDEX` 时设置 |
| 查询时的召回率与延迟旋钮 | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;`（这就是 `nprobe`） |

## 构建顺序对 IVFFlat 重要，对 HNSW 不重要

IVFFlat 的聚类步骤需要表中实际向量的代表性样本，才能把簇中心放好：在空表或数据稀少的表上构建，会得到质量很差的簇。先加载数据，再建 IVFFlat 索引。HNSW 的图是随着向量的插入逐步构建的，没有同样的依赖，这是对于预计会不断增长的表，HNSW 常被优先选用的原因之一。

## 相关内容

- [第 4 课](../lessons/0004-ann-indexes.md)、[第 5 课](../lessons/0005-pgvector-specifics.md)
- [分块与嵌入](chunking-and-embeddings.md)：本速查表中的索引必须与之匹配的向量和相似度度量
