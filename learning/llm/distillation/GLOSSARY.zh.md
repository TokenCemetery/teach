---
title: "术语表"
description: "LLM 知识蒸馏的规范术语"
type: glossary
---

# 蒸馏术语表

用较大模型的输出训练较小模型时使用的规范术语，涵盖承载信号的损失与数据，以及如何评判结果。在本工作区里，“蒸馏”始终指从教师模型到学生模型的知识蒸馏，绝不指数据集蒸馏，也不指蒸馏提示词。

## 术语

**束搜索（Beam search）**:
一种解码方法，每一步只保留得分最高的几条部分序列，最后返回其中最好的完整序列，以此近似概率最大的序列。
_避免使用_: 贪心搜索（greedy search，那是束宽为 1 的情形）、最佳优先解码（best-first decoding）

**容量差距（Capacity gap）**:
教师模型比学生模型大得多时，学生质量可能出现的下降：更强的教师反而训练出比较弱的教师更差的学生。
_避免使用_: 教师太聪明（teacher too smart）、规模不匹配（size mismatch）

**组合损失（Combined loss）**:
一种蒸馏损失，把针对硬标签的交叉熵，与相对于教师软目标的散度相加，并由一个混合系数加权。
_避免使用_: 混合损失（hybrid loss）、双重损失（dual loss）

**跨分词器蒸馏（Cross-tokenizer distillation）**:
在词表不同的教师与学生之间做的 logit 蒸馏，不依赖共享的 token 索引，而是通过对齐或比较二者的分布来完成。
_避免使用_: 无分词器蒸馏（tokenizer-free distillation）、词表迁移（vocabulary transfer）

**去污染（Decontamination）**:
把训练数据中与评测集相同或高度相似的样本移除，让基准测试的分数不再是在度量被记住的题目。
_避免使用_: 清洗（cleaning，过于宽泛）、去重（deduplication，那是移除训练集内部的重复）

**蒸馏（Distillation）**:
训练学生模型去复现教师模型的行为，以教师的输出分布或生成的文本作为训练信号。
_避免使用_: 压缩（compression，过于宽泛）、模型复制（model copying）

**蒸馏缩放定律（Distillation scaling law）**:
Busbridge 等人拟合出的一种关系，根据学生的规模、蒸馏所用的 token 数量和教师的交叉熵，预测学生的交叉熵。
_避免使用_: 蒸馏定律（distillation law）、KD 缩放（KD scaling）

**暴露偏差（Exposure bias）**:
训练时用的是别人写的前缀，生成时用的却是模型自己写的前缀，二者之间的不匹配，使模型早期自己犯的错误把它带入从未训练过的状态。
_避免使用_: 训练与测试不匹配（train-test mismatch，过于宽泛）、漂移（drift）

**保真度（Fidelity）**:
在相同输入上，学生的预测与教师的预测有多接近，而不是二者各自在任务上做得有多好。
_避免使用_: 准确率（accuracy）、忠实性（faithfulness）

**前向 KL（Forward KL）**:
散度 KL(teacher ‖ student)，在教师的分布下取平均。教师给了很高概率的地方，学生若给得很低就会受罚，因此它推动学生覆盖每一个模式。
_避免使用_: 不点明方向的“覆盖模式的 KL”（mode-covering KL）、单说 KL（plain KL）

**广义知识蒸馏（Generalized knowledge distillation）**:
Agarwal 等人提出的在策略方法，用固定序列与学生自己生成的序列混合来训练学生，并用选定的散度逐 token 对照教师打分。缩写为 GKD。
_避免使用_: generalised KD、通用蒸馏（generic distillation）

**硬标签（Hard label）**:
被用作训练目标的那一个正确类别或 token，全部概率都集中在一个答案上。
_避免使用_: 真实值（ground truth，它可能是教师的 argmax）、没有上下文的 one-hot 目标（one-hot target）

**模仿差距（Imitation gap）**:
学生听起来有多像教师，与它实际拥有多少教师能力之间的距离。在有限预算下的模仿，在风格上缩小这个差距的速度，远快于在能力上。
_避免使用_: false promise（那是论文标题，不是术语）、风格迁移（style transfer）

**KL 散度（KL divergence）**:
对同一组 token 上的两个分布 P 和 Q，按 token 求和 P log(P / Q)：衡量 Q 偏离 P 有多远的一个度量，它不具有对称性。在蒸馏中它的两个方向是前向 KL 和反向 KL。
_避免使用_: KL 距离（KL distance）、未引入该术语就直接说相对熵（relative entropy）

**logit**:
模型对某个类别或 token 给出的原始、未归一化的分数，softmax 把这些分数转换成概率之前的那个值。
_避免使用_: 分数（score，有歧义）、对数概率（log-probability，那是 softmax 之后的值）

**logit 蒸馏（Logit distillation）**:
训练信号是教师在每个位置上的完整输出分布的蒸馏，需要能访问教师的 logit，并且师生共用同一个词表。
_避免使用_: 白盒蒸馏（white-box distillation，可接受的别名，但只用一个术语）、软蒸馏（soft distillation）

**离策略蒸馏（Off-policy distillation）**:
在学生并未生成的序列上做的蒸馏：人类数据，或教师自己的输出，在训练之前就已固定。
_避免使用_: 离线蒸馏（offline distillation）、监督蒸馏（supervised distillation）

**在策略蒸馏（On-policy distillation）**:
在学生于训练期间生成的序列上做的蒸馏，由教师给学生选出的每个 token 打分，所以学生是在自己的错误上训练。
_避免使用_: 在线蒸馏（online distillation，也用来指与学生一同训练的教师）、自蒸馏（self-distillation）

**推理依据（Rationale）**:
教师在给出答案之前或同时写出的中间推理，用作额外的训练目标，让学生学到答案是如何得出的。
_避免使用_: 解释（explanation，正文里可以用，但不作为术语）、思维链（chain of thought，那是产生它的提示词技术）

**拒绝采样（Rejection sampling）**:
对每个提示词从模型中抽取若干候选输出，只保留通过检查的那些，例如最终答案正确的。
_避免使用_: 过滤（filtering，过于宽泛）、best-of-n（那是只留下一个胜者，而不是按检查来丢弃）

**反向 KL（Reverse KL）**:
散度 KL(student ‖ teacher)，在学生的分布下取平均。教师给了很低概率的地方，学生若给了概率就会受罚，因此它推动学生专注于一个模式。
_避免使用_: 不点明方向的“寻找模式的 KL”（mode-seeking KL）、后向 KL（backward KL）

**序列级蒸馏（Sequence-level distillation）**:
用普通的交叉熵，在教师解码出的整条序列上训练学生，而不是在教师的逐 token 分布上训练的蒸馏。
_避免使用_: 硬蒸馏（hard distillation）、黑盒蒸馏（black-box distillation，它同样涵盖生成数据的蒸馏）

**软目标（Soft targets）**:
教师在各个类别或 token 上的完整概率分布，用来取代硬标签，或与硬标签一起作为训练目标。
_避免使用_: 软标签（soft labels，可接受的别名，但只用一个术语）、暗知识（dark knowledge，那是软目标所携带的信息，不是目标本身）

**学生模型（Student）**:
蒸馏中被训练的那个模型，通常比教师更小，或运行成本更低。
_避免使用_: 训练完成之前就称为蒸馏模型（distilled model）、子模型（child model）

**潜意识学习（Subliminal learning）**:
学生从语义上与某种特质无关的数据中，习得了教师的这种特质。Cloud 等人在二者共用同一个基础模型时观察到了这一现象。
_避免使用_: 隐蔽蒸馏（hidden distillation）、数据投毒（data poisoning，那是蓄意的）

**监督基线（Supervised baseline）**:
与学生同样大小、不经蒸馏、用相同的数据或相同的算力训练出来的模型，用作对照，以显示某个结果是不是蒸馏造成的。
_避免使用_: 对照模型（control model，过于宽泛）、普通模型（plain model）

**合成数据（Synthetic data）**:
由模型而不是由人写出的训练样本。在本工作区里，它指教师为学生生成的数据。
_避免使用_: 假数据（fake data）、增强数据（augmented data，增强是对已有样本做变换）

**教师模型（Teacher）**:
蒸馏中以其输出作为训练信号的那个模型。它在训练期间保持固定，通常比学生更大或能力更强。
_避免使用_: 神谕（oracle）、父模型（parent model）

**助教模型（Teacher assistant）**:
一个中等规模的模型，先从教师蒸馏得到，再充当更小学生的教师，用来弥合容量差距。
_避免使用_: 未引入该术语就直接说中间教师（intermediate teacher）、TA 模型（TA model）

**教师强制（Teacher forcing）**:
给模型输入一个固定的前缀，而不是它自己先前的输出，这样一次前向传播就能在序列的每个位置上得到一个下一个 token 的分布。
_避免使用_: 教师强制解码（teacher-forced decoding）、自由运行（free running，那是相反的做法）

**温度（Temperature）**:
在 softmax 之前作用于 logit 的除数 T。T 大于 1 会让分布变平，抬高不太可能的答案的概率，使学生能从中学到东西。那是分类器时代的默认做法；而本工作区各来源中的 LLM 蒸馏实验发现，T 取 1 最好。
_避免使用_: 采样温度（sampling temperature，同一种运算，用途不同）、柔和度（softness）

**token 级蒸馏（Token-level distillation）**:
在序列的每个位置上施加的 logit 蒸馏，最小化教师与学生的下一个 token 分布之间的散度。
_避免使用_: 词级蒸馏（word-level distillation，原始论文里的叫法）、逐 token KD（per-token KD）

**top-1 一致率（Top-1 agreement）**:
学生概率最高的答案与教师的相同的输入所占的比例，是 Stanton 等人提出的两个保真度指标之一。
_避免使用_: 准确率（accuracy，那是对照正确答案而言）、匹配率（match rate）

**top-k logits**:
教师在某个位置的输出分布中最大的 k 项，连同它们的 token 索引一起保留，取代完整的词表行，以减少存储。
_避免使用_: 稀疏 logits（sparse logits）、没有说明被丢弃的概率质量如何处理的截断 softmax（truncated softmax）
