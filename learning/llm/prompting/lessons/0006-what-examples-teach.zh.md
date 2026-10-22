---
title: "6. 少样本示例教给模型什么"
description: 演示示例主要教给模型的是格式、标签空间和输入分布，这会改变你挑选示例的方式
type: lesson
---

# 第 6 课：少样本示例教给模型什么

**使命关联:** 要挑好少样本示例，先要知道模型从中拿走了什么，而证据表明，它拿走的与其说是答案，不如说是任务的形状。
**主要来源:** [论文：“Rethinking the Role of Demonstrations”，Min 等，2022](https://arxiv.org/abs/2202.12837)
**前置知识:** [第 5 课](0005-format-sensitivity.md)、[少样本提示词](../GLOSSARY.md)、[零样本提示词](../GLOSSARY.md)

## 热身

1. ▢ 第 4 课用标签把指令和数据分开。说出少样本提示词中应当放在自己标签里的一样东西，并说明原因。

<details markdown="1"><summary>检查</summary>

示例，把它们包在一起（比如放进一个 examples 标签，每个示例再用一个标签），这样模型才能分清演示示例、指令和真正的输入。没有标签的话，示例可能被当成指令，真正的输入也可能被当成又一个示例。

</details>

2. ▢ 第 5 课说过，一处没有含义的格式改动也能让准确率波动。对于两个示例完全相同、只是一个写 `Label:` 而另一个写 `Answer:` 的少样本提示词，这意味着什么？

<details markdown="1"><summary>检查</summary>

意味着它们的准确率可能不同，所以在两者都测试之前，不知道哪个更好。这处改动不改变任何含义，却改变了模型所续写的 token 序列，这正是第 5 课的要点。

</details>

## 要点

### 出人意料的结果

**少样本提示词**会在真正的输入之前，先给模型看输入和输出的配对。一个顺理成章的猜测是，模型从中学到了输入到输出的映射，就像分类器从带标签的数据中学习一样。Min 等人检验了这个猜测，把演示示例中的标签换成随机的。在包括 GPT-3 在内的 12 个模型上，性能几乎没有下降：几乎所有模型下降 0 到 5%（绝对值），分类任务平均下降 2.6%，多项选择任务平均下降 1.7%。

如果有帮助的并不是正确的标签，那么演示示例里一定还有别的东西在起作用。论文指出了三样东西，并通过逐一移除来检验：

| 演示示例提供的东西 | 移除后会怎样 |
|---|---|
| 标签空间：模型可以给出的答案集合 | 把标签换成随机英文单词，使直接模型下降 5 到 16%（绝对值） |
| 输入分布：看起来像真实输入的文本 | 把输入换成随机语料文本，使大多数被测模型下降 3 到 16%（绝对值） |
| 格式：先输入后标签，反复出现 | 去掉配对后，性能接近甚至差于没有演示示例 |

### 这并不意味着什么

有三点限制，使它不会变成“标签不重要”。

被测的模型从 GPT-2 Large 到 GPT-3（7.74 亿到 1750 亿参数），任务是分类和多项选择。论文没有测试当前的聊天模型是否也是同样的表现，所以把它当作一个强先验，然后在你自己的模型上测试。

随机标签仍然有代价，而且代价并不均匀：在分类任务上，有一个模型在每个标签都错的情况下下降了近 10%。“几乎没有伤害”是在被测模型和任务上取的平均值。

作者还指出，如果模型尚未掌握某项任务的输入与标签之间的对应关系，上下文学习可能对这项任务不起作用。演示示例是帮模型定位一项它大体上已经会做的任务，用它来教模型一个从未见过的映射，效果要弱一些。

### 这如何改变示例的选择

如果模型从示例中读出的是格式、标签空间和输入分布，那么这三样就是要做对的东西。

- **采用目标格式**：每个示例都应当和真实的输入以及你想要的输出一模一样，连大小写和标点都要一致。第 5 课解释了为什么细小的差异并非无关紧要。
- **覆盖标签空间**：把模型可能输出的每个标签都展示出来，这样就没有哪个是意外。
- **贴近真实输入**：使用来自真实分布的文本，而不是整齐的编造句子。

Anthropic 的最佳实践指南用实践者的话说了同样的意思：示例要相关（反映实际用例）、多样（覆盖边缘情况，并且变化足够大，以免模型学到非预期的模式）、有结构（包在标签里），并建议用 3 到 5 个示例。这是一家厂商文档里的建议，不是测量得出的结果。

这些都不是给你放行错误标签的理由。正确的标签不花任何代价，还能避开论文里的最坏情况。

## 练习

1. ▢ 先预测，再运行。把下面这个提示词粘贴到聊天窗口里。三个示例上的标签是故意写错的。预测模型对最后一条评论会输出什么，然后运行。

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>提示</summary>

想一想，即使标签是错的，这些示例仍然教了什么：格式、两个允许使用的词，以及评论是什么样子。

</details>

<details markdown="1"><summary>检查</summary>

Min 等人预测，模型会从允许的两个词里给出一个单词的答案，对于一条含义明确的评论，最可能给出正确的那个（Negative），因为模型自己对任务的理解在标签错误时依然保留。如果有模型反而照搬了被调换的映射，那是关于该模型的一个发现，不是论文的错误。无论哪种情况，输出格式（`Label:` 之后一个单词）都应当保持不变，因为格式是示例稳定地教给模型的东西。

</details>

2. ▢ 对一个可用的少样本提示词做下面哪种改动，论文预测伤害最大？

    - a) 调换标签，使部分示例带有错误答案
    - b) 把示例的输入换成语料库中的随机句子
    - c) 重新排列同样的示例，同时保持每个标签正确
    - d) 再加一个符合现有格式的示例

<details markdown="1"><summary>检查</summary>

**b)** 把输入换成分布外的文本，使大多数被测模型下降 3 到 16%（绝对值），比错误的标签（几乎所有模型 0 到 5%）更严重。(a) 是论文的核心结论：代价很小。(c) 这篇论文没有测试；顺序是第 7 课的主题，而且它并非无害。(d) 增加了一个格式正确的演示示例，论文说一旦有了 8 个左右，再增加对结果影响不大。

</details>

3. ▢ 这个提示词是用来给支持工单打标签的。指出它的示例在哪些方面没能教会格式、标签空间或输入分布，并说明你会怎么改。

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>提示</summary>

逐行比较这三个示例。它们的版式是否一致？标签的拼写和标点是否一致？数一数标签。

</details>

<details markdown="1"><summary>检查</summary>

格式：第二个示例去掉了 `Ticket:` 和 `Tag:`，还加了一句评论，所以模式被破坏了一次。标签空间：`billing`、`bug` 和 `Account.` 的大小写和标点各不相同，所以任务里本来只有三个确切的标签，模型却看到了三种标签拼写。带句号的标签 `Account.` 会教给模型一个信息：标点是答案的一部分。输入分布：每个工单都只有短短一行，可能不像真实的工单（真实的更长也更杂乱）。修改办法：每个示例用同一种版式，每次都用确切的标签拼写，工单用真实工单粘贴过来。

</details>

4. ▢ 一个分类器必须输出 Billing、Bug、Account 之一。从下面这个池子里挑出你会用的三个示例，并说明为什么舍弃其余的。

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>检查</summary>

一种合理的选择是 A、C 和 E：每个标签一个示例，覆盖了标签空间，它们的版式一致，而且口语化、像真实内容的措辞符合输入分布。B 几乎是 A 的重复，没有增加多样性。D 是打磨过的行文，不像工单（输入分布不匹配），而且被标成 Bug 的理由也不对。F 本身没问题，但在其他标签出现之前就放第二个 Billing 示例，有第 7 课所讲的偏差风险。只要覆盖三个标签并且避开 D，其他选择也说得通。

</details>

## 实战练习

- [ ] 拿一个你已经在用的少样本提示词。列出每个示例体现了格式、标签空间和输入分布中的哪几样，并标出哪些示例一样都没体现。
- [ ] 把一个提示词运行两次，一次用真实示例，一次用随机重新标注的同样示例，在五个输入上进行。记下有多少个答案发生了变化。
- [ ] 明天：重写一个少样本提示词，让每个示例都采用同一种版式和确切的标签拼写，然后在同样的五个输入上运行并比较。

## 延伸阅读

- [少样本与推理](../reference/few-shot-and-reasoning.md)
- [论文：“Rethinking the Role of Demonstrations”，Min 等，2022](https://arxiv.org/abs/2202.12837)
- [文档：“Prompting best practices”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
