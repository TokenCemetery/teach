---
title: "15. GKD 与 MiniLLM"
description: "从学生那里采样、由教师来打分，以及随之而来的散度与混合方式的选择"
type: lesson
---

# 第 15 课：GKD 与 MiniLLM

**使命关联:** 本使命要求你运行在策略蒸馏并选择它的设置，这需要知道 GKD 的两个旋钮各做什么、MiniLLM 的做法有何不同，以及哪些结果来自哪个任务。
**主要来源:** [论文：“On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes”，Agarwal 等，2023](https://arxiv.org/abs/2306.13649)，第 2 至 4 节
**前置知识:** [第 5 课](0005-forward-and-reverse-kl.md)、[第 14 课](0014-exposure-bias.md)、[广义知识蒸馏](../GLOSSARY.md)、[在策略蒸馏](../GLOSSARY.md)、[反向 KL](../GLOSSARY.md)

## 热身

1. ▢ 在策略蒸馏的一个步骤，在哪些序列上训练？由哪个模型来决定它们？

<details markdown="1"><summary>检查</summary>

训练期间由学生生成的序列，所以由学生来决定。教师只对学生选出的每个 token 打分。在固定序列上训练，不论是人类写的还是教师写的，都是[离策略](../GLOSSARY.md)的。

</details>

2. ▢ 前向 KL 推动学生覆盖教师的每个模式，反向 KL 推动它只认定一个。二者之中，哪一个有可能把概率放在教师认为不太可能的文本上？

<details markdown="1"><summary>检查</summary>

前向 KL，因为它惩罚漏掉教师覆盖的任何区域，所以小的学生会铺开到它建模不好的区域。反向 KL 惩罚在教师概率很低的地方放概率，所以它避免了这一点，代价是多样性。

</details>

3. ▢ 暴露偏差与学生单纯太小之间有什么区别？

<details markdown="1"><summary>检查</summary>

暴露偏差关乎前缀：学生在别人写的前缀上训练，却从自己的前缀上生成。太小的学生，在能表示什么上有容量限制，即使每个前缀都是它自己的，这个限制仍然存在。在策略训练解决的是前者，去除不了后者。

</details>

## 要点

### GKD：一个循环，两个旋钮

广义知识蒸馏（GKD）是一个带两个超参数的算法（Agarwal 等，算法 1）。每一步它抽取一个随机数。以概率 lambda，它针对一批提示词，从学生那里生成序列。否则它从一个由标准答案或教师所写序列构成的固定数据集中取一批。然后它更新学生，以最小化教师与学生 token 分布之间的一个散度，在各位置上取平均，采样过程不带梯度。

lambda 是**学生数据占比**。lambda 为 0 时是普通的监督蒸馏，为 1 时是纯粹的在策略。论文中“混合”的变体用 0.5。训练期间，学生在温度 1 下采样，以保持序列的多样性。

第二个旋钮是散度。GKD 使用广义 Jensen-Shannon 散度 JSD(beta)，它是两个 KL 方向的一种有界混合。按论文的约定，beta 接近 0 时行为像前向 KL，接近 1 时像反向 KL，所以 0.1、0.5 和 0.9 是这条线上的几个点。TRL 的训练器记录了同样的方向：beta 为 0.0 近似前向 KL，beta 为 1.0 近似反向 KL。

### 论文在各个任务上发现了什么

学生是 T5-small（7700 万）、T5-base（2.5 亿）和 T5-large（8 亿）参数的模型，从一个约 30 亿参数、经过微调的 T5-XL 蒸馏而来，所以教师分别比它们大 38 倍、12 倍和 3.8 倍。这些结果是论文自己在 T5 上的结果，不是关于 LLM 的一般事实。

| 任务 | 指标 | 什么有效 | 论文中的出处 |
|---|---|---|---|
| XSum 摘要 | ROUGE-2 | 使用 JSD(0.9) 的在策略 GKD，在贪心和温度采样下都胜过附加基线 ImitKD 和 f-distill。在温度采样下，寻找模式的散度做得更好，而在贪心解码下，散度几乎无关紧要 | 第 4.1 节，图 3 和图 4 |
| WMT14 英语到德语 | BLEU | 广义 JSD 胜过前向 KL 和反向 KL，对较大的学生差距更小。只用学生生成的数据，胜过其他数据混合。图 1 用的是 JSD(0.1) | 第 4.2 节，图 6 |
| 带思维链的 GSM8K | 准确率 | 单用学生生成的思维链，胜过固定数据或混合数据。前向 KL 表现不错，反向 KL 也是。只要至少有 25% 的数据是在策略的，收益就能保持 | 第 4.3 节，图 8 和图 9 |
| FLAN 上的指令微调 | 留出的 MMLU 和 BBH | 使用反向 KL 的在策略 GKD，明显胜过前向 KL | 第 4.4 节，图 10 |

作者的总结是，最佳的散度取决于任务，而在策略数据和混合数据始终胜过固定数据。另外两个结果值得知道。在用 T5-small 做的 XSum 上，在 5% 子样本上做的在策略 GKD，在没有标准摘要的情况下，胜过了在完整数据集上训练的监督 KD 和 ImitKD（第 4.1 节）。对各个学生规模取平均，相对初始学生的性能提升，在摘要上是基线 KD 的 2.1 倍，在翻译上是 1.7 倍，在算术推理上是 1.9 倍（引言）。

对于指令微调，论文正文与它图 10 的说明，在学生是 T5-base 还是 T5-large 上不一致，所以本课不引用该任务的学生规模。教师在 MMLU 上达到 52.4%，在 BBH 上达到 41%。作者假设反向 KL 在那里有效，是因为它寻找模式的特性使模型聚焦于指令的主要意图，他们把这当作假设提出，而不是发现。

### MiniLLM：把反向 KL 当作策略来优化

Gu 等人（MiniLLM）从另一个方向走到在策略训练。他们认为，前向 KL 会使低容量的学生高估教师的低概率区域，转而在整条序列上最小化反向 KL。因为期望是在学生自己的分布下取的，他们用策略梯度定理推导出梯度，并像强化学习那样训练，把教师与学生概率之比的对数，作为每个 token 的信号。

朴素的策略梯度有问题，论文加了三种修复：

| 问题 | 修复 | 细节 |
|---|---|---|
| 方差大 | 单步分解 | 每个 token 的项通过对词表求和来计算，而不是通过采样 |
| 奖励投机：重复短语之类的退化文本，在教师那里得分很高 | 教师混合采样 | 每一步从 alpha 乘教师加 (1 减 alpha) 乘学生的分布中采样，实验中 alpha 取 0.2 |
| 长输出累积的奖励很小，所以学生学会输出非常短甚至空的答案 | 长度归一化 | 用剩余长度对累积的奖励做归一化 |

它还加入了截断，以及在预训练文本上的语言建模损失，以保持通用基准上的性能。训练从一个在任务数据上微调过的学生开始。请注意它与 GKD 的区别：MiniLLM 的样本，通过混合部分来自教师，所以它不是纯粹的在策略，而且它优化的是序列级的目标，而 GKD 平均的是 token 级的散度。

### MiniLLM 的结果

设置是在 15K 条 Dolly 样本上做指令遵循，其中约 12.5K 用于训练，学生来自 GPT-2（120M 到 760M，教师 GPT-2 1.5B）、OPT（1.3B 到 6.7B，教师 OPT 13B）和 LLaMA（7B，教师 LLaMA 13B）。表 1 中的几个单元格，是 DollyEval 上 GPT-4 反馈的平均分：

| 学生 | 仅微调 | 标准 KD | SeqKD | MiniLLM | 教师 |
|---|---|---|---|---|---|
| OPT 1.3B | 52.6 | 52.7 | 51.0 | 60.7 | 70.3 |
| OPT 6.7B | 67.9 | 68.6 | 69.6 | 70.8 | 70.3 |
| LLaMA 7B | 73.0 | 73.7 | 73.6 | 76.4 | 79.0 |

GPT-4 这个指标，是 GPT-4 对模型答案的打分与对参考答案的打分之比，所以它是相对的，不是绝对的。作者还报告说，学生有时在 Rouge-L 上胜过教师，并推测这反映了教师中的暴露偏差。在校准方面，MiniLLM 学生的误差低于前向 KL 基线，但仍高于教师：在 SST2 上，ECE 是 0.099，教师是 0.025，标准 KD 是 0.191（表 2）。

### 你得不出什么结论

每篇论文都是在自己的学生、教师和指标上调整自己的方法，所以上面的数字并没有给 GKD 与 MiniLLM 排名。我在两篇论文里都没有找到直接的正面比较。请比较它们的思路，并在你自己的这一对模型上两个都测一测。

### 一份可以运行的配置

TRL 的 `GKDTrainer` 把两个旋钮暴露为 `GKDConfig` 上的 `lmbda` 和 `beta`。它文档中的默认值各为 0.5，生成时 `temperature` 为 0.9，`max_new_tokens` 为 128，`seq_kd` 关闭。下面文档中的示例，把 Qwen2-1.5B-Instruct 蒸馏进 Qwen2-0.5B-Instruct。我没有运行过它，所以请对照你安装的 TRL 版本检查导入路径，因为当前的文档把 GKD 放在 `trl.experimental` 下。

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

这两个模型共享分词器，因为它们属于同一个家族，而第 6 课解释过，这是 logit 蒸馏所必需的。TRL 页面自己的指导与论文一致：在策略数据（高 `lmbda`）表现更好，而最佳的 `beta` 取决于任务和评估方法。

## 练习

1. ▢ 在 GKD 中，lambda 和散度怎样设置，才能重现按论文定义的 (a) 监督蒸馏和 (b) 在策略 KD？

<details markdown="1"><summary>检查</summary>

两者都用前向 KL。lambda 为 0 得到监督 KD，学生从不生成，lambda 为 1 得到在策略 KD，每条序列都是学生的。中间的值就是混合的变体。散度和数据来源是相互独立的旋钮，这就是为什么同样的前向 KL 会出现在两者之中。

</details>

2. ▢ 在 GKD 对 FLAN 的指令微调实验中，论文发现哪一种搭配，明显优于与它相对应的前向 KL 版本？

    - a) 前向 KL，学生样本
    - b) 反向 KL，学生样本
    - c) 前向 KL，固定序列
    - d) 反向 KL，固定序列

<details markdown="1"><summary>检查</summary>

**b)** 在第 4.4 节里，使用反向 KL 的在策略 GKD，胜过了其他做法。(a) 是论文在 XSum 和使用贪心解码的 GSM8K 上的选择，不是指令微调的选择。(c) 和 (d) 使用的是固定数据，论文发现它始终弱于学生生成的数据。

</details>

3. ▢ 把每一种 MiniLLM 的修复与它所防止的失败配对：(1) 教师混合采样，(2) 长度归一化，(3) 单步分解。失败：A，学生返回非常短或空的答案。B，梯度的方差很大。C，学生找到了教师会给高分的退化文本。

<details markdown="1"><summary>检查</summary>

(1) 对应 C，(2) 对应 A，(3) 对应 B。教师混合采样，通过把教师混入采样分布，来抑制退化的样本。长度归一化，避免长序列因累积的奖励很小而受到惩罚。单步分解，通过对整个词表求和而不是通过采样来计算每个 token 的项，从而降低方差。

</details>

4. ▢ 一个用 MiniLLM 式目标训练的学生，开始输出一个教师给高概率的重复短语。哪种技巧针对的是这个问题？论文用的是什么值？

<details markdown="1"><summary>提示</summary>

教师的打分就是奖励。教师喜欢的退化样本，是在利用这个奖励。

</details>

<details markdown="1"><summary>检查</summary>

教师混合采样，是论文为对付奖励投机而引入的，在它所有的实验中 alpha 都是 0.2（第 3.1 节）。这个值是那篇论文在它的设置上的选择，所以请把它当作起点，而不是常数。

</details>

5. ▢ 用上面的表 1，MiniLLM 对 OPT 1.3B 和 LLaMA 7B，分别弥合了“仅微调的学生”与教师之间差距的多大一部分？从 OPT 6.7B 那一行你得不出什么结论？

<details markdown="1"><summary>检查</summary>

OPT 1.3B：差距是 70.3 减 52.6，即 17.7，MiniLLM 提升了 8.1，约 46%。LLaMA 7B：差距是 6.0，MiniLLM 提升了 3.4，约 57%。在 OPT 6.7B 那一行，MiniLLM 得分 70.8，教师是 70.3，但这并不说明学生更好：这个指标是相对于参考答案的，差异只有半分，而且这只是一对模型。

</details>

6. ▢ 你想在 TRL 里做一次使用反向 KL 的纯在策略运行。要设置哪两个配置值？如果你只有教师的文本，能运行它吗？

<details markdown="1"><summary>检查</summary>

`lmbda=1.0` 和 `beta=1.0`。不能：散度需要教师在学生序列每个位置上的分布，所以你需要教师模型本身，而不是一份存储的文本。只有文本的话，你就回到了序列级（第 8 课）。TRL 的 `seq_kd` 选项并不改变这一点，因为教师仍然要给出针对具体 token 的反馈。

</details>

## 实战练习

- [ ] 阅读 GKD 论文的第 3.1 节。把损失写成一行，然后圈出 lambda 和散度各自在哪里进入。
- [ ] 打开 MiniLLM 论文的表 1，挑一个 MiniLLM 没有在每一列上都胜过教师的学生。写下它在哪个指标上输了，输了多少。
- [ ] 明天：不看笔记，写出 lambda 和 beta 各控制什么，说出 GKD 中反向 KL 获胜的一个任务，并说出 MiniLLM 的三种修复。

## 延伸阅读

- [在策略蒸馏](../reference/on-policy-distillation.md)
- [论文：“On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes”，Agarwal 等，2023](https://arxiv.org/abs/2306.13649)
- [论文：“MiniLLM: On-Policy Distillation of Large Language Models”，Gu 等，2023](https://arxiv.org/abs/2306.08543)
- [文档：“Generalized Knowledge Distillation Trainer”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
