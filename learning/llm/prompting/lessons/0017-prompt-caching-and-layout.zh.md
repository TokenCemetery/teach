---
title: "17. 提示词缓存与布局"
description: 把稳定的部分排在提示词前面，让服务商能够缓存前缀
type: lesson
---

# 第 17 课：提示词缓存与布局

**使命关联:** 提示词模板把稳定的文本放在最前面，服务商就能在每次调用时跳过对它的重复处理，所以布局是在模板里做出的成本和延迟决策，而不是事后补上的东西。
**主要来源:** [文档：“Prompt caching”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**前置知识:** [第 16 课](0016-versioning-prompts.md)、[提示词缓存](../GLOSSARY.md)

## 热身

1. ▢ 第 13 课讲过，在同一个提示词里，长文档和问题各放在哪里。哪个在前？这个顺序与为缓存而把稳定内容放在前面是否一致？

<details markdown="1"><summary>检查</summary>

长文档在前，问题在后。两者一致：跨请求复用的文档是稳定的，而问题每次都在变，所以两个目标指向同一个方向。

</details>

2. ▢ 第 15 课的模板里有固定文本和槽位。两者之中，哪个可以作为缓存前缀的候选，哪个永远不可能？

<details markdown="1"><summary>检查</summary>

固定文本是候选，因为它每次调用都完全相同。每个请求的槽位值会变化，所以任何包含槽位值的内容都不能成为可复用前缀的一部分。

</details>

## 要点

### 被缓存的是前缀

**提示词缓存**会保存提示词前缀处理后的状态，这样之后共享这段完全相同前缀的调用就可以跳过重新计算。Anthropic 的文档描述了它的实现：缓存的前缀按固定顺序覆盖整个请求，先是 `tools`，再是 `system`，最后是 `messages`，一直到并包括标有 `cache_control` 的那个块。缓存条目背后的哈希是累积的，所以改动标记块或它之前的任何块，下一次请求就会得到不同的哈希，条目也就无法匹配。

其他服务商的缓存实现各不相同，所以要查看他们的规则。这里值得带走的原则是：复用一段完全相同的前缀。

### 布局由此而来

把永远不变的放在最前面，把每个请求都会变的放在最后：先是工具定义，然后是系统提示词，再是长文档和少样本示例，最后是每个请求自己的问题。文档建议把静态内容放在开头，并标出可复用部分的结尾。

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

这里 `documents` 在多次调用之间共享，`question` 不共享，所以共享的文本排在前面，二者是各自独立的块，这样标记就可以放在文档之后、问题之前。在 Anthropic 的 API 中，这个标记是文档块上的 `cache_control` 字段，这是这段示例代码里另一处与厂商相关的部分。文档自己给出的错误示例是：一个块里同时放了时间戳和用户消息，并且在这个块上打了缓存标记。前缀哈希包含了时间戳，所以每个请求都会写入一个新条目，却从来读不到。不要把时间戳、请求 ID 或用户名放进稳定的部分。Anthropic 的修复办法是把标记打在跨请求完全相同的最后一个块上。

### 什么会让命中失败，以及各项限制

- 比模型最低要求更短的前缀不会被缓存，而且不会返回错误。文档给出的最低值取决于模型，范围是 512 到 4,096 个 token。如果响应 usage 中的 `cache_creation_input_tokens` 和 `cache_read_input_tokens` 都是 0，说明这个提示词没有被缓存。
- 改动工具定义会使整个缓存失效。文档里的失效表还列出了对 tool-choice 设置、图片以及部分思考和 effort 设置的改动，它们会使 messages 部分失效。
- 默认的有效期是 5 分钟，每次读取该条目时都会刷新。另有 1 小时的选项，需要额外付费。
- 缓存条目只有在第一次响应开始之后才可用，所以并行发出的首批请求不会共享它。关于并发和智能体工作负载，参见[智能体系列第 34 课：提示词缓存与并发](../../agents/lessons/0034-prompt-caching-and-concurrency.md)。

读取比未缓存的输入便宜，写入则更贵：文档列出的 5 分钟写入是基础输入价格的 1.25 倍，读取是 0.1 倍，读取的价格在个别模型上有例外。所以一个永远不会命中的布局，花费会比完全不用缓存略高。

## 练习

1. ▢ 一个模板以 `Current time: {now}` 开头，接着是 3,000 个 token 的风格指南，最后是用户的问题。为什么缓存对它永远没有帮助？怎么修复？

<details markdown="1"><summary>检查</summary>

时间戳是第一个块，所以前缀哈希在每个请求里都会变，后面的任何块都读不到缓存。把风格指南和其他固定文本移到时间戳前面，或者在任务不需要时间戳的情况下把它从提示词里去掉，并让问题保持在最后。

</details>

2. ▢ 第一次请求：`cache_read_input_tokens` 是 0，`cache_creation_input_tokens` 是 2,400，`input_tokens` 是 60。第二次请求，前缀相同，问题有 75 个 token：如果缓存生效，这三个字段分别是多少？总输入是多少？

<details markdown="1"><summary>提示</summary>

文档说，`input_tokens` 只统计最后一个缓存断点之后的内容。

</details>

<details markdown="1"><summary>检查</summary>

`cache_read_input_tokens` 是 2,400，`cache_creation_input_tokens` 是 0，`input_tokens` 是 75。总输入是三者之和，即 2,475 个 token。前缀是从缓存读取的，而不是再次写入，只有新的问题被重新处理。

</details>

3. ▢ 一个团队在最低要求为 1,024 个 token 的模型上加了一个 600 个 token 的系统提示词，标记了缓存，结果两个 usage 计数器都是 0。发生了什么？有什么东西坏了吗？

<details markdown="1"><summary>检查</summary>

这个提示词低于最低要求，所以它在没有缓存的情况下被处理，也没有返回错误。没有任何东西坏了。可以增加更多稳定内容（例如示例）来达到最低要求，或者接受未缓存的调用。

</details>

4. ▢ 对于一个围绕同一份长政策文档回答大量问题的客服机器人，哪种提示词布局最适合缓存？

    - a) 问题，然后是政策文档，再是系统提示词
    - b) 系统提示词，然后是问题，再是政策文档
    - c) 系统提示词，然后是政策文档，再是问题
    - d) 系统提示词，然后是用户姓名，再是政策文档

<details markdown="1"><summary>检查</summary>

**c)** 系统提示词和文档在各个请求之间完全相同，排在前面，问题放在最后。(a) 和 (b) 把变化的问题放在稳定文本之前，所以每次调用的前缀都不同。(d) 把每个用户特有的值放在文档之前，这会让每个不同的用户都破坏共享前缀。

</details>

## 实战练习

- [ ] 拿一个你在运行的提示词，把每个部分标记为稳定、每天变化或每个请求变化，然后检查稳定的部分是否都排在前面。
- [ ] 在一个会报告缓存用量的服务商上，用相同的前缀把同一次调用发两遍，并读取两次调用的计数器。
- [ ] 明天：找出提示词稳定区域里的任何时间戳、ID 或姓名，把它移到末尾。

## 延伸阅读

- [文档：“Prompt caching”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [智能体系列第 34 课：提示词缓存与并发](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [生产环境中的提示词](../reference/prompts-in-production.md)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
