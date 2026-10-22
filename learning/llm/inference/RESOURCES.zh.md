---
title: "资源"
description: "推理服务的可信资料来源"
type: resources
---

# 推理服务资源

## 知识

- [文档：vLLM Documentation，vLLM Project](https://docs.vllm.ai/en/latest/)
  本工作区最先搭起来的 GPU 服务栈的官方文档：安装、启动服务，以及引擎的批处理和内存设置。用途：如何运行和配置 vLLM 本身。
- [论文：“Efficient Memory Management for Large Language Model Serving with PagedAttention”，Kwon 等，SOSP 2023](https://arxiv.org/abs/2309.06180)
  PagedAttention 论文：为什么 KV 缓存会让普通的内存分配器产生碎片，分页如何解决这个问题，以及推动 vLLM 设计的吞吐量数据。用途：理解 KV 缓存的代价，以及 vLLM 的内存管理器为什么存在。
- [仓库：llama.cpp，ggml-org](https://github.com/ggml-org/llama.cpp)
  本工作区其次搭起来的 CPU/边缘服务栈的官方仓库：构建说明、支持的量化格式（GGUF），以及服务器二进制文件的参数。用途：如何运行和配置 llama.cpp 本身。
- [拉取请求：“k-quants”，ikawrakow，llama.cpp，2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  引入了 k-quant 类型、它们的超级块布局，以及在各个张量之间混用不同类型的 `S`、`M` 和 `L` 配方。用途：像 `Q4_K_M` 这样的 GGUF 名称实际存的是什么。
- [论文：“GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers”，Frantar 等，2023](https://arxiv.org/abs/2210.17323)
  一次性的训练后权重量化，可压到 3 到 4 位，并给出实测的精度代价。用途：为服务而量化一个模型，实际要拿什么去换，以及这种权衡是如何度量的。
  如果这里的线性代数是卡住你的地方，请先读下面的 [transformers 指南](https://huggingface.co/docs/transformers/main/en/llm_optims)。
- [文档：“Optimizing inference”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  面向从业者的讲解，涵盖 KV 缓存、静态与动态批处理以及量化后端，不要求先具备论文里的数学。用途：在读上面的一手来源之前，先建立一个可用的心智模型。
- [文章：“Transformer Inference Arithmetic”，Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  推导一次前向计算背后真实的 FLOP 与内存带宽算术，包括 KV 缓存的内存开销从何而来。用途：从第一性原理出发计算延迟或内存预算，而不是引用某个基准测试。
- [文章：“How continuous batching enables 23x throughput in LLM inference while reducing p50 latency”，Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  由早期把连续批处理做进服务引擎的工程师撰写；解释了静态批处理为什么会在长度参差不齐的请求流上浪费 GPU 时间，以及连续批处理如何解决这个问题。用途：本工作区所要辩护的延迟与吞吐量权衡中，关于批处理的那一半。

- [论文：“Fast Inference from Transformers via Speculative Decoding”，Leviathan 等，2022](https://arxiv.org/abs/2211.17192)
  提出了推测解码：小模型起草若干 token，大模型在一次并行计算中全部验证，并用一种采样方法保证输出分布与单独运行大模型时完全相同。用途：为什么这是一个纯粹的延迟杠杆，而不是质量上的取舍，以及并行验证几乎免费背后的内存带宽论证。
- [论文：“Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads”，Cai 等，2024](https://arxiv.org/abs/2401.10774)
  用直接加在目标模型上的额外解码头，取代推测解码中单独的草稿模型。用途：既解决了维护第二个模型的运维负担，又保持同样的验证并纠正的保证。
- [论文：“EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty”，Li 等，2024](https://arxiv.org/abs/2401.15077)
  在模型内部特征的层面而不是原始 token 上起草，并通过引入提前一步的 token 序列，化解特征层面预测的不确定性。用途：相对于 Medusa 的进一步改进，据报告加速比更大，同时仍然保持目标模型的输出分布。
- [论文：“Efficient Guided Generation for Large Language Models”（Outlines），Willard 和 Louf，2023](https://arxiv.org/abs/2307.09702)
  把约束生成重新表述为有限状态机各状态之间的转移，使得每个语法只需预先计算一次词表索引，之后作为快速的逐 token 查找反复使用。用途：为什么基于语法或 schema 的约束解码每个 token 增加的开销很小，并且是靠构造而不是靠碰运气来保证输出结构。
- [文档：“Automatic Prefix Caching”，vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  vLLM 自己的文档，讲如何在原本互不相关的请求之间复用共享前缀的 KV 缓存、它点名的两种示例工作负载（长文档问答、多轮对话），以及它声明的局限（只加快预填充，从不加快解码）。用途：把前缀缓存看作 PagedAttention 的块共享机制扩展到了请求之间。
- [论文：“Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism”，Shoeybi 等，2019](https://arxiv.org/abs/1909.08053)
  张量并行的经典论文：一种层内模型并行方案，把 Transformer 层的矩阵乘法切分到多个 GPU 上，只需要少量通信操作，并且明确与流水线并行正交且互补。用途：`--tensor-parallel-size`（第 12 课）在一层内部究竟做了什么。
- [论文：“GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism”，Huang 等，2018](https://arxiv.org/abs/1811.06965)
  流水线并行的经典论文：把任何能表示为层序列的网络划分成连续的组，分别放在不同的加速器上，并引入微批处理来缩小（而不是消除）由此产生的流水线气泡。用途：与张量并行相对的另一种切分方式，以及它为什么能容忍更慢的设备间链路。
- [文档：“Welcome to production-stack” and use-case guides，vLLM Production Stack](https://docs.vllm.ai/projects/production-stack)
  vLLM 的参考实现、原生运行在 Kubernetes 上的集群部署的官方文档：KV 缓存感知的请求路由，以及基于 `vllm:num_requests_waiting` 这类队列深度指标、由 KEDA 驱动的自动扩缩容。用途：在单台服务器之外，路由和自动扩缩容在集群规模上究竟如何运作。
- [论文：“ServerlessLLM: Low-Latency Serverless Inference for Large Language Models”，Fu 等，OSDI 2024](https://arxiv.org/abs/2401.14351)
  度量了 LLM 冷启动为什么严重（检查点加载时间远超单个 token 的生成时间，在生产追踪中长达几十秒），并用多层的、靠近 GPU 的检查点加载来解决。用途：为什么给集群增加一个副本不是瞬间完成的，以及究竟是什么限制了它多快才能派上用场。
- [文档：“Metrics”，vLLM Project](https://docs.vllm.ai/en/stable/design/metrics/)
  vLLM 自己导出的 Prometheus 指标清单：TTFT、token 间延迟、端到端延迟，以及分开的预填充和解码时间直方图。用途：生产环境的服务器实际会持续导出什么，而不是一次性的基准测试。
- [Google SRE Workbook：“Implementing SLOs”](https://sre.google/workbook/implementing-slos/)
  SRE 对 SLI、SLO 和错误预算的经典表述：一个与用户相关的比率，对它设定的目标，以及直接由 SLO 推出的、对未达标的容忍度。用途：把一个原始的导出指标变成可以据以行动的生产目标。
- [论文：“YaRN: Efficient Context Window Extension of Large Language Models”，Peng 等，ICLR 2024](https://arxiv.org/abs/2309.00071)
  通过对 RoPE 的频率维度做非均匀的重新缩放，把模型可用的上下文长度扩展到训练长度之外，而微调成本只是先前方法的一小部分。用途：为什么 RoPE 缩放改变了最大上下文长度，却丝毫不触及 KV 缓存自身的增长。
- [论文：“Mistral 7B”，Jiang 等，2023](https://arxiv.org/abs/2310.06825)
  引入了滑动窗口注意力及与之配套的滚动缓冲区缓存：每个 token 最多只关注前面固定窗口内的 token，无论序列多长，缓存大小都有上限。用途：把第 2 课的线性缓存增长变成常数的那套机制。
- [论文：“Efficient Streaming Language Models with Attention Sinks”，Xiao 等，ICLR 2024](https://arxiv.org/abs/2309.17453)
  指出了注意力汇聚点现象，它解释了为什么普通的滑动窗口注意力一旦丢掉旧 token 就会崩溃，并通过永久保留最初几个 token 的 KV 条目来修复。用途：为什么一个有界的缓存仍然能够为实际上无界的流提供服务。

## 空白

- 目前还没有专门讲 llama.cpp 的 GGUF 格式的、面向服务的量化来源（相对于面向 GPU 服务栈的 GPTQ/AWQ）；等课程设计推进到那个阶段，使命还需要一份针对 CPU/边缘的量化对比。
