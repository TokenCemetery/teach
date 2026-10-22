---
title: "3. 清晰的指令"
description: "写出一个能干的新人也能照着执行的指令：上下文、任务、约束，以及完成后是什么样子"
type: lesson
---

# 第 3 课：清晰的指令

**使命关联:** 大多数失败的提示词并不是模型被骗了或被搞糊涂了，而是请求本身说得不够明确，所以对任何提示词来说，成本最低的改进就是把一个能干的陌生人需要知道的信息说清楚。
**主要来源:** [文档：“Prompting best practices”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**前置知识:** [第 2 课](0002-system-prompts-and-roles.md)、[零样本提示词](../GLOSSARY.md)

## 热身

1. ▢ 有一行写着 “Reply in at most three sentences.”。它属于系统提示词还是用户轮次，为什么？

<details markdown="1"><summary>检查</summary>

属于系统提示词，因为它应当对每次请求都成立，而不只是这一次。

</details>

2. ▢ 一段聊天渲染出来的提示词以助手的角色标记结尾。模型从这里开始做什么？

<details markdown="1"><summary>检查</summary>

它从这个位置接着续写 token 序列，回复就是这样写出来的。

</details>

## 要点

### 同事测试

Anthropic 的指南让你把模型想象成一位出色但刚入职的员工，他不了解你们的规范和工作流程。指南里的黄金法则是：把你的提示词拿给一位对这项任务了解极少的同事看，请他照着做。如果他会感到困惑，模型也会。

模型没法问你是什么意思，所以你遗漏的一切，它都会用猜测来补上。指南还说，如果你想要“超出预期”的表现，应当明确提出来，而不是指望模型从一个含糊的提示词里自己推断出来。

### 清晰指令的四个部分

| 部分 | 回答的问题 | 示例 |
|---|---|---|
| 上下文 | 这是给谁的，为什么重要？ | “These summaries go to busy support managers who read on their phones.” |
| 任务 | 具体要做什么？ | “Summarise the ticket below.” |
| 约束 | 有哪些限制？ | “At most 40 words. No customer names.” |
| 完成后的样子 | 怎么知道它起作用了？ | “A manager can decide whether to open the ticket from the summary alone.” |

Anthropic 的指南说，说明指令背后的动机，比如某个行为为什么重要，可以帮助模型给出更有针对性的回答。Google 的提示词设计指南同样把约束和响应格式列为需要明确指定的内容。“完成后的样子”是最常缺失的部分，也是你之后拿回归集测试提示词改动时一定会用到的部分。

### 说清楚该做什么，并给必须按顺序发生的步骤编号

Anthropic 的指南建议告诉模型该做什么，而不是不该做什么：不要写 “Do not use markdown”，而是写 “Your response should be composed of smoothly flowing prose paragraphs.”。当步骤的顺序或完整性很重要时，它还建议使用按顺序编号的步骤。

### 改写前后对比

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

第二个提示词更长，是因为它带着上下文、约束和目的。多出来的长度是信息，不是装饰。

## 练习

1. ▢ 说出本课讲的清晰指令的四个部分，并就提示词 “Write a product description.” 指出缺了哪几个。

<details markdown="1"><summary>检查</summary>

上下文、任务、约束，以及完成后的样子。这个提示词只有任务，而且很含糊。缺少的是：描述是写给谁的、会出现在哪里，长度和语气的限制，以及它必须达到的标准。

</details>

2. ▢ 把 “Don't write long answers.” 改写成告诉模型该做什么的形式。

<details markdown="1"><summary>检查</summary>

例如：“Answer in two or three sentences.” 它点明了期望的行为，并给出可衡量的限制，因此也是可检查的。否定式的指令只说了要避免什么，却让模型自己去猜替代做法。

</details>

3. ▢ 对 “Make this email better” 的几种改写中，哪一种最清晰？

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>检查</summary>

**b)** 它指明了受众、长度限制和顺序要求，所以别人也能检查结果。(a)、(c) 和 (d) 只是用别的词重述了“更好”，并没有说明更好是什么意思。

</details>

4. ▢ 先预测，再运行。选一项你经常做的任务，比如 “Write a short bio.”。用五个词写出提示词并发送。预测回复在你的用途上会出错的三件事，然后用全部四个部分重写提示词，再发送一次。你预测的三件事哪些被修正了，又出现了哪些你没有预料到的问题？

<details markdown="1"><summary>提示</summary>

先把这个五个词的提示词交给一位同事。他会向你提的所有问题，就是模型正在猜的内容。

</details>

<details markdown="1"><summary>检查</summary>

典型的结果是：第一次回复会猜受众、长度和语气。第二次去掉了这些猜测，但可能带来新问题，往往是某条约束和另一条冲突。把两次回复都留下来：它们之间的差异，就是你能拿给别人看的第一组对比，而第 18 课会把这个习惯变成一个回归集。

</details>

## 实战练习

- [ ] 拿一个你本周发出过、回复令人失望的提示词，标出它缺少上下文、任务、约束和完成后的样子中的哪几项。
- [ ] 把你写的一个提示词交给一位毫无背景的同事，问他有哪些地方得靠猜。为每一处猜测补上一行。
- [ ] 明天：把你常用的一个提示词里的某个“不要”换成正面的指令，在同一个输入上比较回复。

## 延伸阅读

- [文档：“Prompt design strategies”，Gemini API，Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)：另一家厂商关于约束和响应格式的指南。
- [提示词的构成](../reference/prompt-anatomy.md)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
