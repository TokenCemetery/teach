---
title: "13. 合并、保存与发布适配器"
description: "合并是精确的；适配器是需要基础模型才有意义的差分"
type: lesson
---

# 第 13 课：合并、保存与发布适配器

**使命关联:** 一个只存在于训练脚本里的适配器，并没有发布。这一课为第 3 阶段收尾。
**主要来源:** [文档：LoRA merging，Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**前置知识:** [第 8 课](0008-the-low-rank-idea.md)、[第 12 课](0012-reading-a-training-run.md)

## 热身

1. ▢ 从一次过拟合的运行里，你发布哪个检查点？

<details markdown="1"><summary>检查</summary>

留出集损失最小值处的那个，而不是最后一步。

</details>

2. ▢ 损失曲线永远无法让你看到什么？

<details markdown="1"><summary>检查</summary>

生成的结果是否可用，以及你任务分布之外的能力是否退化了。两者都需要针对固定的探针做实际的生成。

</details>

3. ▢ 写出 LoRA 的更新，带缩放。

<details markdown="1"><summary>检查</summary>

`ΔW = (α/r) · BA`，加到冻结的 `W₀` 上。

</details>

## 要点

### 目录里有什么

保存下来的适配器，大致包含：

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

很小，常常只有几十兆字节。而且**按设计就是不完整的**：它是一个差分，没有它配置里所指明的那个确切的基础模型，就毫无意义。丢了基础模型，或者弄不清是它的哪个版本，适配器就成了垃圾。

### 两种发布方式

**不合并。** 加载基础模型，在加载时应用适配器。

```text
base := load_model("<base model>", dtype: "bfloat16")
model := load_adapter(base, "runs/first-adapter/final")
```

**合并。** 把更新折叠进权重，丢弃适配器的结构。

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

把分词器也一并保存。缺少分词器的模型目录，是一张等着被提出的支持工单。

### 在两者之间选择

| | 不合并 | 合并 |
|---|---|---|
| 磁盘 | 基础模型只存一份，适配器以兆字节计 | 每个任务一份完整的模型副本 |
| 推理速度 | 每个被适配的层多出两次小的矩阵乘法 | 与基础模型相同 |
| 多个任务 | 一个基础模型，多个适配器，可切换 | 各自一个完整的模型 |
| 部署 | 部署栈必须支持适配器 | 任何能加载模型的栈 |
| 可组合性 | 适配器可以在运行时替换或加权 | 在合并时就固定了 |

![部署三个任务。合并时，三个完整的模型，每个都在一份差分旁边持有自己那份基础权重的副本。不合并时，一份基础权重位于同样的三份差分之上。](images/how-many-copies-of-the-base.svg)

两边的三份差分是同样的三份。成倍增加的是带阴影的那部分，它也恰恰是大的那部分。

经验法则：**单一用途的部署就合并，用一个基础模型服务多个任务时就保持不合并。** 第 25 课会正式讲多适配器部署。

### 合并是精确的，有两个例外

因为更新是加性的、线性的，合并在算术上是精确的。`W₀ + (α/r)BA` 与不合并的模型计算的是同一个函数。没有近似，也没有质量损失。

除了两种情形，二者都值得了解：

**合并进量化的基础模型是有损的。** 如果基础模型是 4 位的，加上一个 bf16 的更新，就需要先反量化、相加、再重新量化，而重新量化这一步会丢信息。正确的顺序是：针对量化的基础模型训练，然后合并进*全精度*的基础模型，如果需要，再把合并的结果量化。直接合并进量化权重，会无缘无故地降低质量。第 4 阶段会回到这一点。

**dropout 会改变有效的尺度。** `lora_dropout` 在训练时生效，在推理时不生效。这是标准的 dropout 行为，通常无害，但它意味着合并后的权重反映的是没有 dropout 的那条路径，而那才是正确的。

### 验证合并

永远不要想当然。比较输出：

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

关键就在贪心解码：开着采样，你分不清合并的缺陷和普通的随机性。微小的数值差异仍可能导致长生成的后段出现分歧，所以只比较适量的 token，并去调查*早期*的分歧，而不是后期的。

### 一个基础模型上的多个适配器

PEFT 可以持有多个适配器并在它们之间切换，还可以带权重地把它们组合起来：

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

加权组合是一个确实有用的工具，但它不是魔法：针对不同任务各自独立训练出来的两个适配器，并不能可靠地组合成一个两样都会的适配器。值得一试，而且需要度量，而不是想当然。对任何关于适配器算术的说法，都要当作需要在你自己的任务上验证的东西。

### 要记录什么

之后用于复现和调试所需要的一切：

- 基础模型的标识符**以及版本**
- 适配器配置，原样保存
- 数据集的身份和确切的划分
- 随机种子、有效批大小、学习率、调度、步数
- 你选了哪个检查点以及原因，也就是为它提供依据的那个留出集数字
- 库的版本
- 评测结果，包括回归探针

这不是为流程而流程。半年后，“为什么旧的适配器比新的好”这个问题，只有凭这样的记录才回答得了。

## 练习

1. ▢ 为什么一个 40 MB 的适配器文件，单独拿着毫无用处？

<details markdown="1"><summary>检查</summary>

它只包含 `A` 和 `B` 矩阵：针对一组特定基础权重的差分。没有那个确切的基础模型和版本，它就无法应用，而应用到差一点的基础模型上，会悄悄地变差。

</details>

2. ▢ 你要部署同一个基础模型的五个微调变体。合并还是不合并？

<details markdown="1"><summary>检查</summary>

不合并。不合并意味着内存里一份基础模型，加上五个小适配器，可按请求切换。合并则意味着五份完整的模型副本。

代价是每个被适配的层多出两次小的矩阵乘法，以及需要一个支持适配器的部署栈。

</details>

3. ▢ 你针对一个 4 位量化的基础模型训练。描述正确的合并流程。

<details markdown="1"><summary>检查</summary>

以全精度加载基础模型，应用适配器，在那里合并，如果需要量化的产物，再把合并后的模型量化。

直接合并进量化权重，需要反量化、相加、再重新量化，而重新量化会丢信息，毫无好处。

</details>

4. ▢ 你合并之后，用温度 0.8 的采样比较生成结果。输出不同。你学到了什么？

<details markdown="1"><summary>检查</summary>

什么也没学到。开着采样，不管合并是否正确，输出不同都是意料之中的。

用贪心解码来比较，那时任何分歧都可以归因于权重。然后去调查早期的分歧；只在很多 token 之后才出现的差异，可能只是普通的数值漂移。

</details>

5. ▢ 关于合并未量化的 LoRA，下列哪项是正确的？

    - a) 它是精确的，在推理时不花任何代价
    - b) 它损失一点质量，但能加速推理
    - c) 它是精确的，但推理时需要更多内存
    - d) 它是有损的，生产环境中应当避免

<details markdown="1"><summary>检查</summary>

**a)** 它是精确的，在推理时不花任何代价。

更新是加性的、线性的，所以它折叠成一个普通的权重矩阵，函数相同，内存相同，也没有额外的矩阵乘法。这个性质，正是 LoRA 与之前的适配层方法的区别所在。

</details>

6. ▢ 你用 `add_weighted_adapter` 把一个格式适配器和一个领域知识适配器组合起来，结果比两者单独用都差。这令人意外吗？

<details markdown="1"><summary>检查</summary>

不意外。独立训练出来的低秩更新，占据的是互不相关的子空间，它们的加权和并不保证对其中任何一个任务是好的更新，更不用说对两个任务都好。

它有时效果很好，值得一试。但永远不要想当然；要拿它与每个适配器单独的结果对比度量。

</details>

## 实战练习

- [ ] 合并你的适配器，并在你的固定探针上用贪心解码验证。确认输出一致。
- [ ] 比较目录大小：单独的适配器与合并后的模型。记下比值。
- [ ] 针对一次真实的运行，完整写出上面所说的运行记录。
- [ ] 明天：在一个基础模型上加载两个适配器，对同一个提示词在它们之间切换。观察差别。

## 延伸阅读

- [文档：LoRA merging，Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [文档：Model merging，Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [第 25 课：部署适配器](0025-serving-adapters.md)
- [失败模式](../reference/failure-modes.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
