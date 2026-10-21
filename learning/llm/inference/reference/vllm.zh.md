---
title: "vLLM"
description: "搭起 vLLM、承载第 1 到 3 阶段概念的参数、PagedAttention 的块表，以及从症状到调优参数的决策流程"
type: reference
---

# vLLM

GPU 服务栈。为在搭起或调优服务器时查阅而做。

## 搭起一台服务器

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

在 8000 端口启动一个兼容 OpenAI 的 HTTP 服务器。请求看起来和任何 OpenAI 聊天补全调用一样：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

请求中的 `"model"` 字段必须与服务器启动时指定的模型一致。

## 承载第 1 到 3 阶段算术的参数

| 参数 | 承载的内容 |
|---|---|
| `--max-num-seqs` | [对照延迟预算来辩护的](batching.md#defending-a-configuration)批大小上限 |
| `--kv-cache-dtype` | [缓存精度](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights)，例如 `fp8`，与模型自身的权重精度无关 |
| `--quantization` | 对一个已经量化好的检查点，[所选并辩护过的](quantization-at-serve-time.md)方案（`gptq`、`awq` 等） |

连续批处理和分块预填充默认开启；没有参数可以关掉这个基本机制，只有围绕它做调节的参数（比如块大小）。省略 `--quantization`，就会按检查点保存时的精度提供服务，最常见的是 fp16 或 bf16；加载时不会做任何量化。

<a id="pagedattention"></a>

## PagedAttention

每个序列的缓存被切成固定大小的**块**（默认 16 个 token）；每个序列有一张**块表**，把逻辑上的 token 位置映射到物理块的位置，思路与操作系统的页表相同。

**块大小是一个权衡：**

| 块大小 | 最后一个未填满的块里浪费的空间 | 块表的记账开销 |
|---|---|---|
| 更大 | 更多 | 更少 |
| 更小 | 更少 | 更多 |

**算例**：一个 40 个 token 的序列，块大小为 16 个 token，用掉 `ceil(40/16) = 3` 个块；第三个块里放 8 个 token，浪费另外 8 个槽位。

**块共享**：当内容相同（最常见的是共享的提示词前缀）时，两个序列的块表可以指向同一个物理块。并行采样和束搜索是最清楚的情形：每个样本的块表都指向同样的提示词块，直到某个样本自己生成的 token 发生分歧，这时**写时复制**只给那个样本一份正在被修改的块的私有副本。

**算例**，对同一个 200 个 token 的提示词做 10 个并行样本，块为 16 个 token：一份拷贝需要 `ceil(200/16) = 13` 个块。不共享：`13 × 10 = 130` 个块。共享：13 个块，直到有样本开始分歧。

## 另外两个调优参数

| 参数 | 控制什么 | 权衡 |
|---|---|---|
| `--gpu-memory-utilization` | vLLM 可以用于权重、缓存及其自身开销的 GPU 内存比例（默认约 0.9） | 往 1.0 调高会增大缓存的容量上限，但给与它共用这块 GPU 的其他东西留下的余量更少 |
| `--tensor-parallel-size` | 把模型的权重和计算切分到多块 GPU 上 | 是把模型摊开，而不是缩小它（没有精度代价，这点不同于量化）；单靠任何一种都不够时，可以与量化组合使用 |

`--gpu-memory-utilization` 改变了[容量上限公式](kv-cache.md#capacity-budget)中“总内存”的含义：在 80 GB 的 GPU 上，按默认的约 0.9，公式应该使用的只是约 72 GB，而不是 80 GB。

## 从症状到参数

| 症状 | 检查什么 |
|---|---|
| 启动不了，或报告缓存可用的内存太少 | 先看 `--gpu-memory-utilization`；如果调到 100% 仍然放不下，那就是[内存受限的情形](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first)：量化、加上 `--tensor-parallel-size`，或者两者兼用 |
| 解码比延迟预算慢 | 先拿 `--max-num-seqs` 对照[被辩护的批大小](batching.md#the-throughputlatency-trade-off)，再看量化权重或 `--kv-cache-dtype` 是否有实测数字作为依据 |
| 一个请求拖住所有其他序列的 token | [队首阻塞](batching.md#admission-order-and-head-of-line-blocking)：检查分块预填充的块大小，而不是批大小 |
| 同一个提示词的并行样本之间，内存看起来被浪费了 | 上面的块共享：在动批大小或内存利用率之前，先确认它是否真的在发生 |

## 相关内容

- [第 10 课](../lessons/0010-standing-up-vllm.md)、[第 11 课](../lessons/0011-pagedattention.md)、[第 12 课](../lessons/0012-vllm-tuning-knobs.md)
- [KV 缓存](kv-cache.md)、[批处理](batching.md)、[服务时量化](quantization-at-serve-time.md)：这些参数所承载的概念
