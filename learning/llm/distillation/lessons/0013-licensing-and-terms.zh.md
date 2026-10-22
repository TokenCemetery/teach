---
title: "13. 许可与条款"
description: "服务商的条款和开源模型的许可，允许你对它的输出做什么"
type: lesson
---

# 第 13 课：许可与条款

**使命关联:** 本使命要求你核查一份蒸馏数据集的使用是被允许的，这意味着在从教师那里生成数据之前，先阅读约束这个教师的文件，并把你的发现记录下来。
**主要来源:** [条款：“Terms of Use”，OpenAI](https://openai.com/policies/row-terms-of-use/)
**前置知识:** [第 12 课](0012-filtering-synthetic-data.md)、[第 10 课](0010-distilling-from-generated-data.md)、[合成数据](../GLOSSARY.md)、[教师模型](../GLOSSARY.md)

本课不构成法律意见。它阅读两份文件，引用其中所说的话，并给出一份该看什么的清单。它不对一份文件对你的情形意味着什么、某个条款是否可以强制执行，或者哪份文件约束你作出任何断言。条款和许可的变动没有课程可以固定的版本号，所以下面的引文都带有阅读它们的日期，而在依赖其中任何一条之前，你应该阅读当前的文本。要做真正的决定，请去问律师。

## 热身

1. ▢ phi-1 的作者用 n-gram、嵌入和 AST 匹配，对照 HumanEval 对他们的习题做了剪枝。他们为什么没有止步于 n-gram 重叠？

<details markdown="1"><summary>检查</summary>

13-gram 检查只标出了四道题，全是误报，而且对找出相似的代码来说太粗糙，所以他们加入了嵌入和 AST 的比较（第 12 课）。

</details>

2. ▢ Alpaca 的数据来自 text-davinci-003，它的模型是从 LLaMA 7B 微调而来的。所以它依赖于别人拥有或控制的哪两样东西？

<details markdown="1"><summary>检查</summary>

生成数据的教师（OpenAI 的 text-davinci-003，受 OpenAI 的条款约束）和基础模型（LLaMA，受它的许可约束）。二者都是学生的输入，各自都带着自己的条件（第 10 课）。

</details>

3. ▢ 说出按规则对照标准答案检查生成答案的那种过滤器，以及它判断不了的一样东西。

<details markdown="1"><summary>检查</summary>

带检查器的拒绝采样，只保留通过检查的样本。它判断不了开放式的答案或风格，那里没有可供核对的东西（第 12 课）。

</details>

## 要点

### 三份文件，三个问题

当你从教师那里生成数据时，你最多可能受到三种不同文件的约束，各自回答不同的问题。

| 文件 | 它回答的问题 |
|---|---|
| 托管模型的服务商使用条款 | 我对从这项服务得到的输出，可以做什么？ |
| 开放权重的许可 | 我对这个模型，以及它的产出，可以做什么？ |
| 提示词和种子数据的许可或条款 | 我对输入给它的内容，以及用这些内容构建的数据，可以做什么？ |

每一份都是单独的文本，有自己的日期和适用范围。读了其中一份，并不能告诉你另一份说了什么。

### 托管服务商的条款说了什么

OpenAI 面向世界其他地区的使用条款，自 2026 年 1 月 1 日起生效，列出了用户不能做的事情。其中有这样一行，是在编写本系列时、即 2026 年 10 月读到的。该网站会阻止脚本化读取，所以请在浏览器里重新核对这个页面：

> "Use Output to develop models that compete with OpenAI."

要注意三点，不多不少。这句话位于禁止用途的那一节。它说的是开发与 OpenAI 竞争的模型，这比开发任何模型要窄。而且它只是一份文件：你的使用可能适用另一个版本，或者适用 API 或企业服务的单独协议，而本课没有读过那些。

### 开放权重的许可说了什么

Meta 的 Llama 3.1 社区许可协议，在第 1.b.i 条（再分发与使用）里说，如下是 2026 年 10 月 17 日从仓库文本读到的：

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

同一段还要求，如果你分发 Llama Materials，或者包含它们的产品或服务（包括另一个 AI 模型），你必须提供一份该协议的副本，并在相关的网站、用户界面、博客文章、关于页面或产品文档上显著地展示“Built with Llama”。另外，许可说明，使用 Llama Materials 必须遵守适用的法律，以及它通过引用并入的可接受使用政策。

当以这种方式使用输出、而且最终得到的模型被分发或被公开提供时，文本给它附加了一个关于模型名称的条件。本课对文字之外的东西不作任何断言。其他的 Llama 版本和其他开源模型有各自的许可，有些说的是不同的内容。

### 一个项目是怎么处理的

Alpaca 的作者声明，他们的模型仅用于学术研究，禁止任何商业使用，并给出三个因素：LLaMA 的许可是非商业的，所以他们继承了它；指令数据来自 text-davinci-003，他们说它的使用条款禁止开发与 OpenAI 竞争的模型；而且他们没有建立起足够的安全措施。他们还写道，他们的演示被限制在非商业用途，以及符合 LLaMA 许可的用途（Alpaca 博客文章，“Overview”和“Release decision”）。请注意他们做了什么：他们点出了每一个限制的来源，并把发布与之挂钩。无论你自己的文件怎么说，这都是值得照搬的习惯。

### 生成之前：一份清单

按这个顺序阅读并记录：

1. **教师的条款**。找到适用于你访问该模型的方式的确切文件。记下它的名称、URL、日期或版本，以及关于用输出训练其他模型的句子。
2. **权重的许可，如果教师是开放的**。记下版本、任何关于在输出上训练的条款、任何关于命名或署名的要求，以及它并入的任何使用政策。
3. **提示词和种子数据**。你输入给教师的任何东西的许可，比如种子任务、文档或抓取的文本，约束的是这些输入。请把它与教师分开检查。
4. **命名与署名**。如果某份文件要求模型名称带前缀或署名行，现在就决定，趁模型还没有名字的时候。
5. **学生将如何被使用和共享**。许多条款取决于模型是被分发、被公开提供，还是被出售，以及它与什么相竞争。写下你打算的用途。
6. **日期**。记录你阅读每份文件的时间，以及你生成每一批数据的时间，因为生成时有效的条款，可能与今天的条款不同。

把这份记录放在数据集旁边，每个来源一行，这样“这是从哪里来的？”这个问题，在一年之后仍然有答案。在每个样本上加一个来源字段，写明教师、版本和生成日期，几乎不花什么成本。

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

`<...>` 这些条目，是要针对你自己的项目去填写的字段。

### 本课无法告诉你的

它无法说明某个项目是否违反了某个条款。这取决于完整的文本、事实、司法辖区，以及服务商和许可持有人会怎么做，而这些都不在一句引文里。这个练习的要点要窄得多：确保你读过这些文件，知道它们字面上说了什么，并留有一份带日期的记录。

## 练习

1. ▢ 一个团队在 Llama 3.1 的输出上微调了一个模型，并且会公开提供它。根据引用的许可文本，新模型的名称必须满足什么条件？

    - a) 必须以“Llama”这个词结尾
    - b) 不得提及 Llama
    - c) 必须以“Llama”这个词开头
    - d) 必须向许可方注册

<details markdown="1"><summary>检查</summary>

**c)** 引用的句子说的是，对被分发或被公开提供的模型，AI 模型名称的开头要有 “Llama”。(a) 把位置弄反了。(b) 与它所说的相反。(d) 不在引用的文本里。

</details>

2. ▢ 引用的 OpenAI 那一行，说的是使用输出“to develop models that compete with OpenAI”。一位同事把它概括为“OpenAI 禁止在它的输出上训练”。这个概括错在哪里？

<details markdown="1"><summary>检查</summary>

那一行比这个概括要窄：它涉及的是开发与 OpenAI 竞争的模型，而不是所有的模型开发。它还只是一份文件，是条款的一个版本，在某一个日期。请引用那句话和它的日期，而不是转述，并检查适用于你的访问途径的是什么。你的项目是否构成竞争，是本课不回答的法律问题。

</details>

3. ▢ 你在三月从一个托管模型生成了 200,000 个样本。十月，服务商修改了它的条款。你首先做什么？

<details markdown="1"><summary>检查</summary>

阅读新的条款，以及你生成数据时有效的条款，两者都从服务商自己的页面获取，并看看你的记录里写着你读的是哪个版本。你之所以把日期写下来，正是为了这个。接下来的问题，是关于哪些条款适用于已经生成的数据，这是法律问题，所以要交给有资质的人，而不是靠猜。

</details>

4. ▢ Alpaca 的作者为仅供研究的发布给出了三个因素。哪一个取决于对教师的选择，哪一个取决于对学生基础模型的选择？

<details markdown="1"><summary>检查</summary>

教师因素是，数据来自 text-davinci-003，它的条款禁止开发与 OpenAI 竞争的模型。基础模型因素是，LLaMA 的许可是非商业的，所以 Alpaca 继承了它。第三个，缺少安全措施，与二者都无关。

</details>

5. ▢ 你的种子提示词来自一个公开数据集，你的教师是一个采用宽松许可的开源模型。说出在你发布学生之前，仍然需要阅读的两份文件。

<details markdown="1"><summary>检查</summary>

种子数据集的许可，因为它约束的是输入，以及开源模型自己的许可，看其中关于在它的输出上训练、命名、署名或使用政策的任何条款。还要检查学生起点所用的任何基础模型的许可。某一个来源上的宽松许可，并不会延伸到其他来源。

</details>

## 实战练习

- [ ] 打开 OpenAI 使用条款和 Llama 3.1 许可，找到上面引用的那些确切的句子。把各自的生效日期抄进笔记里。
- [ ] 在你使用的某个平台上，挑一个公开的合成数据集。找出它说自己是由哪个教师生成的，并写下数据集页面上所述的那个教师的条款或许可。
- [ ] 明天：针对一个你选定教师的假想数据集，填写上面的清单记录，并标出每一个你无法从一手文件中填写的字段。

## 延伸阅读

- [序列与合成数据](../reference/sequence-and-synthetic-data.md)
- [条款：“Terms of Use”，OpenAI](https://openai.com/policies/row-terms-of-use/)
- [许可：“Llama 3.1 Community License Agreement”，Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [文章：“Alpaca: A Strong, Replicable Instruction-Following Model”，Stanford CRFM，2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
