---
title: "18. 提示词的回归集"
description: 建立一小组提示词改动不得破坏的用例，从真实出现过的失败入手
type: lesson
---

# 第 18 课：提示词的回归集

**使命关联:** 提示词的每次改动都是一个主张，而回归集能让这个主张在几秒钟内得到检验，而不是靠你碰巧读到的那三条输出来判断。
**主要来源:** [文章：“Your AI Product Needs Evals”，Hamel Husain](https://hamel.dev/blog/posts/evals/)
**前置知识:** [第 17 课](0017-prompt-caching-and-layout.md)、[回归集](../GLOSSARY.md)

## 热身

1. ▢ 第 11 课要求输出结构化内容，然后对其做校验。为什么有效性检查很自然地会成为回归集里的第一个断言？

<details markdown="1"><summary>检查</summary>

要求某种格式并不是保证，输出仍然可能无法解析。解析或 schema 检查成本低，不需要主观判断，并且能对每个用例运行，所以这是一个容易写出来的断言。

</details>

2. ▢ 第 5 课说明了，一处没有含义的格式改动也能改变准确率。这意味着，仅靠阅读少量输出，你能判断出提示词改动的多大一部分？

<details markdown="1"><summary>检查</summary>

非常少。一处小改动可能让结果发生偏移，而少数几条输出看不出来，所以必须让这个改动在一组固定的用例上运行并计数。

</details>

## 要点

### 从你已经见过的失败开始

**回归集**是一组固定的输入，每个输入都配有对输出的检查，提示词的改动不得破坏它们。最好的最初用例是真实的用例。Hamel Husain 讲述了为一个房地产助手构建评测的经历，他说，当你想不出断言时，就批判性地审视 trace 和失败模式，而且团队的数百个单元测试，都是根据数据里观察到的新失败持续更新的。trace 就是被记录下来的对话，所以要记录它们、阅读它们，并把每次失败变成一个用例：触发它的输入，加上本来能抓住它的检查。

Anthropic 的评测构建指南在目标上与此一致：设计能反映真实任务分布的测试，包含边缘情况，并尽可能自动评分。开始时不需要生产流量。Hamel 指出，你可以先写下有根据的猜测，或者让模型生成输入，再让早期用户来完善它们。

### 每个属性一个断言

Hamel 把这些检查描述为断言，就像你在 pytest 里写的那样，要快而且便宜，这样才能在每次改动时运行。每个用例都列出它的输出必须具备的属性。

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` 会渲染第 15 课的模板，调用第 16 课中固定的模型，并返回它的文本。Hamel 自己的例子是一个类似的检查：输出绝不能暴露内部 UUID。如果某个属性无法写成字符串或正则测试，可以让模型来评分，至于何时可以信任这个评分器，评测系列里有专门讲解。

### 小、会增长，而且不是非全过不可

从眼前那几个失败开始，每出现一个新失败就添加一个用例。这个集合应当能代表你在意的失败，而不是为了大而大：Anthropic 的指南主张数量优先于人工评分的质量，Hamel 的团队也积累到了数百个测试，所以小只是起点，不是目标。Hamel 提醒了两点：好的集合包含模型吃力的用例；而且与普通单元测试不同，你不一定需要 100% 的通过率，因为通过率是一个产品决策，决定你容忍哪些失败。按提示词版本来跟踪结果，这样你就能看出自己有没有在进步。

## 练习

1. ▢ 一位用户反馈，摘要器把退款请求称作“complaint”。把这个反馈变成一个用例：输入里放什么，输出需要哪些断言？

<details markdown="1"><summary>检查</summary>

输入是用户的真实工单文本，或者与它相近的一条。断言是 `must_contain` 包含 refund 一词，并且 `must_not_contain` 不含 complaint 一词，就像上面的 `refund-not-complaint` 用例那样。这个用例现在在旧提示词上会失败，在修复之后会通过。

</details>

2. ▢ 当模型输出 `Account 3f2b8c1e is locked.` 时，预测 `no-uuid` 用例的 `run_case` 结果。

<details markdown="1"><summary>提示</summary>

把输出与唯一的那个 `must_not_contain` 字符串比较。

</details>

<details markdown="1"><summary>检查</summary>

它返回 `False`。`must_contain` 为空，所以 `has_all` 为真，但输出里包含 `3f2b8c1e`，所以 `has_none` 为假，用例失败。这个提示词泄露了 ID 的一部分。

</details>

3. ▢ 一位队友想等到有 500 个生产质量的用例之后，再建立回归集。结合本课的资料，这样做错在哪里？

<details markdown="1"><summary>检查</summary>

在那之前什么都不会运行，所以这期间的改动只能凭感觉来判断。资料描述的集合都是从观察到的失败中逐步增长起来的，Hamel 还说可以从有根据的猜测开始。从你手头有的失败开始，随着新失败的出现再添加用例。

</details>

4. ▢ 一个回归集在当前提示词上通过了 20 个用例中的 18 个，团队坚持任何发布之前都必须 20 个全过。哪种看法与 Hamel 的文章一致？

    - a) 通过率是一个关于容忍哪些失败的产品决策，所以不要求 100%
    - b) 每个用例都必须通过，否则这个集合作为上线前的关卡就毫无价值
    - c) 应当删掉那两个失败的用例，让集合反映当前提示词的状况
    - d) 通过率没有用例数量重要，而用例数量应当始终尽量压低

<details markdown="1"><summary>检查</summary>

**a)** Hamel 说你不一定需要 100% 的通过率，这取决于你愿意容忍哪些失败。(b) 是他拿来对比的普通单元测试的习惯。(c) 删掉了这个集合本来就是为了记住的那些失败。(d) 说反了：集合只是在起步时才小。

</details>

## 实战练习

- [ ] 从日志、缺陷报告或你自己的测试中，找出五个你在运行的提示词的真实或贴近真实的失败，把每个都写成一个输入加一个断言。
- [ ] 把这五个用例放进仓库中紧挨着提示词的一个文件里，对当前的提示词运行它们，并记下哪些通过。
- [ ] 明天：下一次提示词给出糟糕的输出时，在修复提示词之前先把它添加为一个用例，并确认它一开始是失败的。

## 延伸阅读

- [文章：“Your AI Product Needs Evals”，Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [文档：“Define success criteria and build evaluations”，Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [生产环境中的提示词](../reference/prompts-in-production.md)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
