---
title: "llama.cpp"
description: "GGUF 的格式与量化命名、ggml 的后端抽象，以及服务离开 GPU 之后有什么变化"
type: reference
---

# llama.cpp

CPU/边缘服务栈。为在搭起或思考 llama.cpp 部署时查阅而做。

## GGUF

一个把权重、分词器和架构元数据打包在一起的单一二进制文件，取代 Hugging Face 检查点所带的好几个独立文件（`config.json`、分词器、权重）。这种打包对边缘部署最重要：只需发布一个文件，配上一个小而依赖很少的二进制程序就能运行，不需要安装 Python 或 Hugging Face 生态来把这些零件重新组装起来。

由于 GGUF 把权重排布成操作系统可以直接读取的格式，llama.cpp 可以对文件做**内存映射**（`mmap`），而不是急切地把它读进内存并反序列化。页面只有在被访问到时才从磁盘读入，哪些页面保持驻留则由操作系统自己的页缓存来管理。这在内存最紧张的 CPU 和边缘硬件上最要紧，在系统内存充裕的 GPU 服务器上则没那么重要。

### 量化命名

GGUF 承载的是 llama.cpp 自己的量化家族，与面向 GPU 的 GPTQ 和 AWQ 是分开的。解读 `Q4_K_M` 这样的名称：

| 部分 | 含义 |
|---|---|
| `Q4` | 位宽：每个权重大约 4 位（还有 `Q5`、`Q8` 等） |
| `K` | 一种 **k-quant** 类型：每个张量一个位宽，由 256 个权重组成的超级块，其中每个子块各自带一个缩放因子 |
| `M` | 在各个张量之间混用不同类型的配方，给某些张量用更高位的类型：`S`（小）、`M`（中）、`L`（大）。参见量化系列的[“度量与存储”参考表](../../quantization/reference/measuring-and-storing.md) |

## ggml：一套代码，多个后端

llama.cpp 建立在 **ggml** 之上，这是一个无依赖的 C 语言张量库（不需要外部 BLAS）。一次前向计算是一张静态计算图，构建一次然后执行，而不是 PyTorch 那样一个操作接一个操作的即时执行。这种“算什么”与“由什么来跑”的分离，使得同一张图可以面向多个**后端**，包括 CPU（AVX2/NEON）、CUDA、Metal、Vulkan，一套代码，没有 Python 运行时，硬件上从手机的 ARM CPU，到 Mac 的 Metal GPU，再到树莓派。相比之下，vLLM 的设计是针对 CUDA 的，没有 NVIDIA GPU 就无法运行。

## 线程取代了 GPU 批处理

| | 摊开的是 | 受什么限制 |
|---|---|---|
| GPU 批处理（`--max-num-seqs`） | 在并发序列之间分摊内存带宽开销 | 缓存容量和延迟预算 |
| CPU 线程（`--threads`） | 把单个序列自己的矩阵乘法分到各个核上 | CPU 的物理核数 |

线程加快的是单个序列自己的计算；它没有“反正内存读取的钱已经花了”这种东西，可以像 GPU 批处理那样在素不相识的请求之间分摊。

## 搭起服务器

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

请求的形状与 [vLLM](vllm.md) 一样，同样兼容 OpenAI；变的是它下面的一切。

## 离开 GPU 之后有什么变化

| 机制 | 在 GPU 上（vLLM） | 在 CPU/边缘规模上（llama.cpp） |
|---|---|---|
| 并发 | [连续批处理](batching.md)在数百个素不相识的并发请求之间分摊内存带宽 | 少量并行槽位（个位数到二十几个）；典型的边缘工作负载是一台设备服务它自己的用户，很少有数百个并发请求可以批在一起 |
| 缓存管理 | [PagedAttention](vllm.md#pagedattention) 管理一个庞大的、不断变化的共享池 | 一个更简单的、每个序列连续存放的缓存就足够了；PagedAttention 所要解决的问题，很少达到它的复杂度值得付出的规模 |
| 量化时机 | 一个服务时的参数（`--quantization`），在启动时选定 | 在挑选或生成某个具体的 GGUF 量化级别时就已锁定；要改它，就得换一个文件，而不是改一个参数 |

权衡本身（[内存、速度和精度](quantization-at-serve-time.md)）没有变；不同的只是每个决策在何时做出，以及在多大的并发下才划算。

## 相关内容

- [第 13 课](../lessons/0013-gguf.md)、[第 14 课](../lessons/0014-llamacpp-architecture.md)、[第 15 课](../lessons/0015-what-changes-off-gpu.md)
- [vLLM](vllm.md)、[批处理](batching.md)、[服务时量化](quantization-at-serve-time.md)：本表用来做对照的 GPU 一侧的机制
