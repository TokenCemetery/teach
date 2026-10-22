---
title: "5. pgvector 详解"
description: "在 Postgres 中搭建向量搜索，并把第 4 课的索引概念对应到 pgvector 实际的运算符和参数上"
type: lesson
---

# 第 5 课：pgvector 详解

**使命关联:** 这是第 3 阶段的收尾：第 4 课的 IVF 和 HNSW 概念，在这里变成了真实的表结构、真实的距离运算符和真实的调节参数，所用的正是本工作区统一采用的向量存储。
**主要来源:** [仓库：pgvector，pgvector](https://github.com/pgvector/pgvector)
**前置知识:** [第 4 课](0004-ann-indexes.md)、[文本块](../GLOSSARY.md)

## 热身

1. ▢ IVF 的 `nprobe` 参数和 HNSW 的 `ef_search` 参数，各自控制什么？

<details markdown="1"><summary>检查</summary>

`nprobe` 设定查询时搜索 IVF 的多少个簇；`ef_search` 设定 HNSW 的图搜索在每一步跟踪多少个候选。两者都是拿召回率换延迟：值越高，搜索得越多，以延迟为代价提升召回率。

</details>

2. ▢ 为什么只有当嵌入向量被归一化为单位长度时，余弦相似度和点积才会产生相同的排名？

<details markdown="1"><summary>检查</summary>

点积就是按两个向量的长度缩放之后的余弦相似度。当两者都固定为单位长度时，这个缩放因子对每一对都相同，所以排名一致；当长度不一时，点积会偏爱更大的向量。

</details>

## 要点

### 一个向量列和一个距离运算符

pgvector 给 Postgres 添加了 `vector(N)` 列类型，大小与第 3 课确定的嵌入维度一致：

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

相似度用三个运算符之一来计算：`<->`（欧氏距离 / L2 距离）、`<#>`（负内积）和 `<=>`（余弦距离）。运算符必须与嵌入模型训练时针对的度量相匹配（第 2 课）：对一个按原始点积训练的模型使用 `<=>`，或者反过来，正是第 2 课警告过会降低排序质量的那种不匹配，只不过现在表现为一个具体的 SQL 选择，而不是抽象的选择。注意 `<#>` 的符号：它特意取负内积，是为了和另外两个运算符一样，越小越相似，使三者的 `ORDER BY` 升序保持一致。

### 索引必须针对某一个特定的距离函数来建

创建索引，就是选择一个与预期距离函数相匹配的运算符类：

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`、`vector_l2_ops` 和 `vector_ip_ops` 各自为某一个特定的运算符构建索引。用 `vector_l2_ops` 建的索引，无法加速按 `<=>`（余弦距离）排序的查询；运算符类和查询的运算符必须一致，否则索引不会被用上，查询会悄悄退回到全表顺序扫描，这就完全违背了建索引的初衷。

### pgvector 的参数名，就是第 4 课的那些参数，只是名字不同

HNSW 的索引构建参数 `m`（每个节点的最大连接数）和 `ef_construction`（构建时的搜索深度），正是第 4 课中 HNSW 的调节旋钮，在 `CREATE INDEX` 时设置。它的查询时召回率与延迟旋钮是一个会话设置：`SET hnsw.ef_search = 100;`，也就是换了个名字的第 4 课的 `ef_search`。IVFFlat 的构建参数是 `lists`（第 4 课提到的簇数量），同样在创建索引时设置，它的查询时旋钮是 `SET ivfflat.probes = 10;`，也就是第 4 课的 `nprobe`。

### IVFFlat 要先有数据才能建好，HNSW 不需要

IVFFlat 的聚类步骤需要表中实际向量的代表性样本，才能把簇中心放好，这意味着在空表或几乎没有数据的表上建 IVFFlat 索引，会得到质量很差的簇，无法反映语料库真实的向量分布。实际的结论是：先加载数据，再建 IVFFlat 索引。HNSW 的图结构是随着向量的插入逐步构建的，不要求表中事先已有数据，这是对于预计会不断增长的表，HNSW 常被优先选用的原因之一，此外还有第 4 课已经讲过的召回率与延迟方面的优势。

## 练习

1. ▢ 某个嵌入模型的训练目标，是让余弦相似度反映语义上的接近程度。查询及其索引应该使用哪个 pgvector 运算符和运算符类？

<details markdown="1"><summary>检查</summary>

查询用 `<=>` 运算符（余弦距离），索引用 `vector_cosine_ops`。如果使用的运算符或运算符类对应的距离函数与模型训练时的不同，就会重新引入第 2 课的度量不匹配问题，只不过现在是具体的 SQL 不匹配。

</details>

2. ▢ 某团队用 `vector_l2_ops` 建了一个 HNSW 索引，但查询用 `<=>` 运算符（余弦距离）对结果排序。会发生什么？为什么这个问题不只是“答案不对”？

<details markdown="1"><summary>提示</summary>

想一想，当查询的运算符与索引创建时用的运算符类不一致时，这个索引还能不能被用上。

</details>

<details markdown="1"><summary>检查</summary>

为 `vector_l2_ops` 建的索引无法加速使用 `<=>` 的查询，因为索引是针对某一个特定的距离函数构建的。查询会退回到对整张表的顺序扫描，在任何真实规模的语料库上都很慢；这不只是有答案不对的风险，而是丢掉了索引本该提供的全部性能收益。

</details>

3. ▢ 某张表有一个 `lists = 1000` 的 IVFFlat 索引，但查询时设置 `ivfflat.probes` 保持默认值 1。用第 4 课的 `nprobe` 来说，这对召回率与延迟的权衡意味着什么？

<details markdown="1"><summary>检查</summary>

`ivfflat.probes = 1` 就是 `nprobe = 1`：1000 个簇中只搜索最近的那一个。这是第 4 课权衡中最快、召回率最低的一端；靠近簇边界的查询，可能漏掉位于相邻簇中的真正最近邻。调高 `probes` 会搜索更多的簇，用查询延迟换取更高的召回率。

</details>

4. ▢ 为什么构建顺序对 IVFFlat 索引很重要（先加载数据，再建索引），对 HNSW 却不重要？

<details markdown="1"><summary>检查</summary>

IVFFlat 的聚类步骤需要表中真实向量的代表性样本，才能把簇中心放好；在空表或数据稀少的表上构建，会得到质量很差的簇，无法反映实际的数据分布。HNSW 的图是随着向量的插入逐步构建的，不要求表中事先已有一份有代表性的样本。

</details>

5. ▢ 关于 pgvector 的运算符类（`vector_cosine_ops`、`vector_l2_ops`、`vector_ip_ops`），下列哪项说法正确？

    - a) 任何运算符类都能配合任何查询运算符使用，因为 pgvector 会自动在距离函数之间转换
    - b) 索引的运算符类必须与查询的距离运算符一致，否则该查询不会使用这个索引
    - c) 运算符类只影响 HNSW 索引，不影响 IVFFlat
    - d) `vector_ip_ops` 不能用于已归一化的嵌入向量

<details markdown="1"><summary>检查</summary>

**b)** 运算符类和查询的运算符必须一致，否则查询会退回到顺序扫描，而不是使用索引。（a）错误：距离函数之间不存在自动转换。（c）错误：两种索引类型都要求运算符类与距离函数相匹配。（d）错误：已归一化的向量恰恰是内积与余弦距离一致的情形，第 2 课讲过。

</details>

## 实战练习

- [ ] 创建一张小的 pgvector 表，`vector(N)` 列的大小对应你用的某个嵌入模型，并用与该模型训练时的相似度度量相匹配的运算符类建一个索引。
- [ ] 对你的表运行一次相似度查询的 `EXPLAIN`，确认索引确实被用上了，而不是退回到顺序扫描。
- [ ] 明天：对同一个查询，试两个不同的 `ivfflat.probes` 或 `hnsw.ef_search` 值，比较返回的结果和查询延迟。

## 延伸阅读

- [仓库：pgvector，pgvector](https://github.com/pgvector/pgvector)
- [论文：“Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs”，Malkov 和 Yashunin，2018](https://arxiv.org/abs/1603.09320)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
