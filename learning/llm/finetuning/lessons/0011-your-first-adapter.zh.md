---
title: "11. 你的第一个适配器"
description: "一次运行，先证明流水线是通的，其他一切都排在后面"
type: lesson
---

# 第 11 课：你的第一个适配器

**使命关联:** “把它跑起来”写在使命里。在此之前的都是阅读，这一课才是运行。
**主要来源:** [文档：SFTTrainer，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**前置知识:** [第 3 课](0003-tokenizers-and-chat-templates.md)、[第 9 课](0009-rank-alpha-and-initialisation.md)、[第 10 课](0010-choosing-target-modules.md)

## 热身

1. ▢ 目标模块的现代默认做法是什么，为什么现在负担得起？

<details markdown="1"><summary>检查</summary>

所有线性层，秩给得宽裕。适配器参数相对于激活内存可以忽略，所以限制它们已经省不了多少了。

</details>

2. ▢ 哪一行代码能抓住什么也没匹配上的目标模块名？

<details markdown="1"><summary>检查</summary>

`model.print_trainable_parameters()`。数量接近零，意味着适配器什么也没挂上。

</details>

3. ▢ 训练还是推理：`add_generation_prompt=True` 属于哪一个？

<details markdown="1"><summary>检查</summary>

推理。在训练中助手这一轮已经在文本里了，再加上这个提示就会让标记重复。

</details>

## 要点

### 选一个最小的、失败时能提供信息的东西

你第一次运行的目的**不是**得到一个好模型，而是证明流水线接得正确。所以要让它便宜到出了错只损失几分钟：

- 0.5B 到 3B 级别的基础模型。小模型训练得快，暴露数据缺陷的能力并不比大模型差。
- 几百个样本。足以看到损失在动。
- `max_steps` 大约 20 到 50，而不是用 epoch。你想让它很快跑完。

在流水线得到验证之前优化任何东西，都是白费力气，而且会掩盖是哪项改动造成了哪种效果。

### 一次最小的运行

```text
dataset := load_dataset("<a small instruction dataset>", split: "train[:500]")

adapter_config := {
    rank: 16,
    alpha: 32,
    dropout: 0.05,
    adapt_bias: false,
    target_modules: "all-linear",
}

run_config := {
    output_dir: "runs/first-adapter",
    max_steps: 50,
    per_device_batch_size: 1,
    gradient_accumulation_steps: 8,      # effective batch size 8
    learning_rate: 2e-4,
    warmup_steps: 5,
    lr_schedule: "cosine",
    logging_steps: 1,                    # every step, for the first run
    max_length: 1024,
    gradient_checkpointing: true,
    precision: "bf16",
}

trainer := new_trainer(
    model: "<a small base model>",
    train_dataset: dataset,
    adapter_config: adapter_config,
    run_config: run_config,
)

trainer.train()
trainer.save("runs/first-adapter/final")
```

关于这个 API 接口，有两点说明。`SFTTrainer` 接受模型的*字符串*，并会替你加载它。序列长度是 `SFTConfig` 上的 `max_length`。这两点在不同版本之间都变过，所以**请阅读所安装版本的文档，而不要相信这段代码或你的记忆。** 这条指示不是套话，它是整个工作区里最可靠的、浪费整个下午的来源。

### 精度、硬件，以及真正会变的是什么

`bf16=True` 需要硬件支持 bfloat16，这在现代加速器上很普遍，但并非处处如此。在较老的设备上，你可能需要带损失缩放的 fp16，在某些后端上，则只有完整的 fp32 可选。第 5 课的原理不变，变的只是可用的格式。

同样，这个脚本背后具体用的是哪种加速器，不是方法的一部分。概念、算术和失败模式，在 CUDA、ROCm、Intel、Apple Silicon 和 CPU 上是一样的。不同的是哪些内核经过了优化、支持哪些精度，以及每一步要多久。凡是某个后端确实限制了方法的地方，本工作区都会明确说明；见[第 16 课](0016-training-through-a-quantized-base.md)。

### 四项检查，按顺序

在你关心损失曲线之前，先做这些检查。

**1. 适配器存在吗？**

```python
trainer.model.print_trainable_parameters()
```

与你第 8 课的算术比较。数量为零，或者差距超出舍入误差，意味着停下来修。

**2. 数据是你以为的那样吗？**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

解码一个真实的训练样本，把它读一遍。这一项检查，能抓住模板不匹配、缺少回合结束 token、屏蔽的缺陷，以及答案中途被截断：糟糕微调最常见的五个原因里的四个。**不要跳过它。** 它是整个过程里最值的十秒钟。

**3. 损失在动吗？**

在 `logging_steps=1` 下的 50 步里，损失应当明显下降。从第一步起就一动不动，意味着适配器没挂上、学习率低得离谱，或者什么也没被打分。

**4. 它能对两个样本过拟合吗？**

这是现有最强的冒烟测试。在两个样本上训练一百步。损失应当趋近于零。如果它连两个样本都记不住，说明流水线坏了，而你两分钟就知道了，而不是等到跑完六小时之后。

### 保存下复现所需要的东西

适配器目录很小，通常是个位数到几百兆字节，只包含适配器权重，以及一份记录基础模型、秩、alpha 和目标模块的配置。没有那个确切的基础模型，它就毫无用处，所以要把基础模型的标识符及其版本一并记录下来。

还要记录库的版本。六个月前训练顺利的配置，未必还能以同样的方式加载，而“这是哪个版本”事后是无法恢复的。

## 练习

1. ▢ 你有 50,000 个样本和一个很大的基础模型可用。为什么这是错误的第一次运行？

<details markdown="1"><summary>检查</summary>

因为第一次运行的任务是证明流水线是通的，而一次漫长而昂贵的运行，给出的信息和一次短而便宜的运行一样，只是晚得多、代价高得多。

更糟的是，如果哪里有问题，你要过了几个小时才发现，而不是几分钟，而且你无法分辨几项改动中哪一项起了作用。

</details>

2. ▢ 损失从第一步起就完全平坦。按你检查的顺序，说出三个原因。

<details markdown="1"><summary>检查</summary>

1. 适配器什么也没挂上；检查 `print_trainable_parameters()`。
2. 每个标签都是 `-100`，所以什么也没被打分；在一个真实样本上检查标签数量。
3. 学习率低了几个数量级；检查它在 `1e-4` 左右，而不是 `1e-5` 或更低。

这三项各只需一行就能排除，所以它们排在任何微妙的问题之前。

</details>

3. ▢ 为什么要解码一个训练样本，而不是相信数据集？

<details markdown="1"><summary>检查</summary>

因为真正要紧的失败，在数据集里看不见，在解码后的文本里却看得见：错误的聊天模板、缺少回合结束 token、本该屏蔽却没屏蔽的提示词 token、被 `max_length` 在句子中间截断的答案。

这些都不会抛出错误。每一个产生的，都是一次看上去没问题的运行，和一个有问题的模型。

</details>

4. ▢ 你的适配器在一百步里，无法在两个样本上把损失推到接近零。这说明了什么？

<details markdown="1"><summary>检查</summary>

说明流水线坏了，而不是任务难。任何正常工作的适配器，都能轻而易举地记住两个样本。

去找：没挂上的适配器、被完全屏蔽的标签、接近零的学习率，或者数据整理器产出的东西与你预期的不同。

</details>

5. ▢ 你只有适配器目录，别的什么都没有。你能用它吗？

<details markdown="1"><summary>检查</summary>

只有当你能识别出它是针对哪个确切的基础模型训练的才行，适配器配置里按名字记录了这一点。应用到不同的基础模型上，即使是同一系列的另一个检查点，结果往好了说是退化，往坏了说是胡言乱语。

记录基础模型的标识符、版本，以及你的库版本。适配器就是一个差分（diff），而差分需要它的基底。

</details>

6. ▢ 在 4 台设备上，`per_device_train_batch_size=2`、`gradient_accumulation_steps=8`，有效批大小是多少？

<details markdown="1"><summary>检查</summary>

2 × 8 × 4 = 64。

报告这个数字，而不是每设备的那个。用每设备的批大小来比较运行，是得出错误结论的可靠办法。

</details>

## 实战练习

- [ ] 在做任何真正的训练之前，先运行两个样本的过拟合测试。确认损失趋近于零。
- [ ] 完整地解码并阅读一个训练样本。数一数有多少位置被打分，有多少被屏蔽。
- [ ] 从头到尾完成一次 50 步的运行，并保存适配器。记下它在磁盘上的大小。
- [ ] 明天：把基础模型的标识符、版本和每个库的版本，写进适配器旁边的一个文件里。

## 延伸阅读

- [文档：SFTTrainer，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [文档：LoRA，Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [失败模式](../reference/failure-modes.md)：运行期间把它开着
- [第 12 课：解读训练运行](0012-reading-a-training-run.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
