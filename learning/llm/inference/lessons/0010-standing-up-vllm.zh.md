---
title: "10. 搭起 vLLM"
description: "安装 vLLM、启动它的服务器，并找出承载已学概念的参数"
type: lesson
---

# 第 10 课：搭起 vLLM

**使命关联:** 第 1 到 3 阶段的每一个公式，包括缓存占用、批大小、量化方案，在本课里都变成了一条真实命令上的真实参数；算术就是在这里变成一台响应请求的服务器的。
**主要来源:** [文档：vLLM Documentation，vLLM Project](https://docs.vllm.ai/en/latest/)
**前置知识:** [第 9 课](0009-picking-a-quantization-scheme.md)、[KV 缓存](../GLOSSARY.md)

## 热身

1. ▢ 一台服务器在当前批大小下超出了延迟预算。按第 6 课的推理，第一个该检查的参数是哪个？

<details markdown="1"><summary>检查</summary>

最大批大小的设置：第 6 课所辩护的，就是仍然满足延迟预算的最大批大小，所以这是直接控制它的那个旋钮。

</details>

2. ▢ 为什么在服务时选择对 KV 缓存使用 fp8，而不是模型自身的权重精度，会是合理的（第 3 课）？

<details markdown="1"><summary>检查</summary>

缓存精度是独立于模型自身权重精度的杠杆。把缓存的 `bytes_per_value` 减半，就直接把它的占用减半，模型本身不变，换回容量的方式就像换了一个更小的模型一样。

</details>

## 要点

### 安装 vLLM

vLLM 以 Python 包的形式安装，`pip install vllm`，并且需要一块支持 CUDA 的 GPU；它是本工作区使命中 GPU 的那一半，CPU 和边缘则留给后面一个阶段的 llama.cpp。对于常见的配置，安装会自动拉取匹配的 PyTorch 和 CUDA 工具链，在假定安装失败是别的原因之前，值得先对照已安装的 CUDA 驱动版本检查一下。

### 启动服务器

`vllm serve <model>` 为指定的模型（本地路径或 Hugging Face Hub 上的标识符）启动一个兼容 OpenAI 的 HTTP 服务器，默认监听 8000 端口：

```text
vllm serve meta-llama/Llama-2-7b-hf
```

这一条命令完成了下载（如果需要）、权重加载和服务器启动，而第 1 到 3 阶段的一切，推理的都是这些步骤在内存和延迟上的后果。

### 发送请求

由于服务器采用的是 OpenAI API 的形状，请求看起来就像任何 OpenAI 聊天补全调用，只是瞄准了本地服务器：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### 已学的概念在哪里表现为参数

命令行就是第 1 到 3 阶段不再是算术、而变成配置的地方：

- `--max-num-seqs`：第 6 课教你如何对照延迟预算来辩护的批大小上限。
- `--kv-cache-dtype`：第 3 课介绍的缓存精度，作为独立于模型自身权重的杠杆（例如 `fp8`）。
- `--quantization`：在为一个已经量化好的检查点提供服务时，指明方案，比如 `gptq` 或 `awq`，也就是第 7 到 9 课教你如何选择并辩护的那个方案。
- 连续批处理和分块预填充（第 4 和第 5 课）默认开启；没有参数可以关掉这个基本机制，只有围绕它做调节的参数，比如块大小。

## 练习

1. ▢ 一个团队运行 `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8`。按第 6 和第 3 课，这两个参数各自实际控制什么？

<details markdown="1"><summary>检查</summary>

`--max-num-seqs 32` 把批大小上限设为 32，也就是第 6 课会对照规定的延迟预算和第 2 课的容量上限来辩护的那个数字。`--kv-cache-dtype fp8` 用 fp8 而不是默认值来存 KV 缓存，把它每个 token 的占用减半，与模型自身的权重精度无关，恰好就是第 3 课描述的那个杠杆。

</details>

2. ▢ 一个团队用 `vllm serve some-model` 启动服务器，完全没有指定 `--quantization` 参数。服务器以什么精度提供这个模型的服务，为什么？

<details markdown="1"><summary>检查</summary>

以检查点自身保存时的精度，最常见的是 fp16 或 bf16，因为没有要求任何量化方案。`--quantization` 只有在为一个事先量化好的检查点提供服务，或者参数告诉 vLLM 在加载时量化时才适用；省略它，就意味着不做任何量化。

</details>

3. ▢ 在检查之前先预测：`vllm serve` 成功运行之后，本课“要点”一节里的 curl 请求中，哪一项信息必须与服务器实际启动时用的某个东西一致，否则请求会失败？

<details markdown="1"><summary>提示</summary>

看 curl 命令里的 `"model"` 字段。

</details>

<details markdown="1"><summary>检查</summary>

请求体里的 `"model"` 字段必须与服务器启动时使用的模型名（或路径）一致。服务器一次只服务一个模型；在请求里指明另一个模型，最常导致一次本来格式正确的调用出错。

</details>

4. ▢ 在没有给出批处理或缓存参数时，关于 vLLM 的默认行为，哪种说法是对的？

    - a) 在设置 `--max-num-seqs` 之前，它退回到静态批处理
    - b) 连续批处理和分块预填充默认运行；参数只是进一步调节它们
    - c) 在明确选定 KV 缓存的数据类型之前，它拒绝启动
    - d) 默认以硬件支持的最低精度提供服务

<details markdown="1"><summary>检查</summary>

**b)** 连续批处理和分块预填充是默认的机制，不是靠某个参数打开的；可用的参数调节的是围绕它们的各个参数，比如最大批大小或块大小。(a) 是错的：没有退回静态批处理这回事。(c) 是错的：没有指定时，会使用默认的缓存数据类型。(d) 是错的：默认是检查点自身保存的精度，而不是硬件支持的最低精度。

</details>

## 实战练习

- [ ] 在一台带有支持 CUDA 的 GPU 的机器上安装 vLLM（`pip install vllm`），用一个你下载得起的小模型运行 `vllm serve`。
- [ ] 对你运行中的服务器发送本课的 curl 请求，确认你拿回来的是一个真正的补全结果，而不是错误。
- [ ] 明天：把服务器重启，分别把 `--max-num-seqs` 设成一个小数（比如 2）和一个大数，看看你能不能观察到它在几个并发请求下的行为有什么差别。

## 延伸阅读

- [文档：vLLM Documentation，vLLM Project](https://docs.vllm.ai/en/latest/)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
