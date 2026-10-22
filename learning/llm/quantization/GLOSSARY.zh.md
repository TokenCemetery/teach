---
title: "术语表"
description: "LLM 量化的规范术语"
type: glossary
---

# 量化术语表

涉及数值格式、量化方法、它们所运行的硬件，以及如何度量它们的开销时使用的规范术语。在本工作区中，“量化”始终指降低已训练模型中数值的精度，绝不指对输入做离散化。

## 术语

**绝对值最大量化（Absmax quantization）**:
对称量化的一种，其截断范围取共用同一个缩放因子的那些值中绝对值最大的一个，所以不会有任何值被截断，缩放因子就是这个值除以最大的整数档位。
_避免使用_: 最大值缩放（max scaling）、朴素量化（naive quantization）

**按激活排序（Act-order）**:
GPTQ 的一个选项：按激活值从大到小的顺序来量化一层的各列，排序依据是海森矩阵的对角线。它记录在作者的代码里，论文中没有。
_避免使用_: 未经介绍就直接写 desc_act、重排技巧（reorder trick，AWQ 论文对 GPTQ 一个变体的叫法）

**激活值（Activation）**:
在前向传播中算出的张量，例如线性层的输入，与存储下来的权重相对。它的取值取决于输入，所以范围只能在运行时才知道，或者由校准集估计。
_避免使用_: 隐藏状态（hidden state，专指残差流时可以用）、特征图（feature map）

**仿射量化（Affine quantization）**:
同时带有缩放因子和零点的量化，所以整数网格可以相对于零不对称地摆放，覆盖 [-0.2, 1.5] 这样的范围而不浪费档位。
_避免使用_: 非对称量化（asymmetric quantization，可接受的别名，但只用一个术语）、均匀量化（uniform quantization，对称量化同样成立）

**算术强度（Arithmetic intensity）**:
一次计算每从内存搬运一个字节所执行的算术运算次数，它决定了这次计算在某块芯片上是受内存带宽限制还是受算力限制。
_避免使用_: 运算强度（operational intensity）、FLOP 与字节之比（FLOP-to-byte ratio，出现在公式里可以接受）

**位宽（Bit width）**:
存储一个量化值所用的位数，不含花在它的缩放因子和零点上的位数。总量见每个权重的有效位数。
_避免使用_: 精度（precision，与尾数位有歧义）、位深（bit depth）

**块缩放格式（Block-scaled format）**:
一小块值（例如 32 个）共用一个与它们存放在一起的缩放因子的格式，因此元素类型可以非常窄。MXFP4 和 NVFP4 是例子，GGUF 的块类型也是。
_避免使用_: 微缩放（microscaling，那只是其中一个家族，即 OCP 的 MX）、分组格式（grouped format）

**校准集（Calibration set）**:
一小批有代表性的输入，让模型跑一遍以收集激活值的统计量，训练后方法用它来选择范围或给舍入误差加权。它不是训练数据，训练后量化也绝不会对它做反向传播。
_避免使用_: 训练集（training set）、校准数据集（calibration dataset，可以用，但统计量本身不要叫“校准数据”）

**截断误差（Clipping error）**:
截断范围之外的值被钳制到范围两端所产生的误差。
_避免使用_: 饱和误差（saturation error）、溢出（overflow）

**截断范围（Clipping range）**:
量化器映射到它的整数网格上的那段实数区间；区间之外的值被钳制到最近的一端。选择它，是在截断误差与舍入误差之间做权衡。
_避免使用_: 动态范围（dynamic range，那是格式的属性）、量化范围（quantization range）

**受算力限制（Compute-bound）**:
速度由算术吞吐量而不是字节搬运所限制的负载，预填充和大批量解码都是典型。只量化权重不能让它变快，甚至可能让它变慢。
_避免使用_: 受 FLOP 限制（FLOP-bound，可以用，但只用一个术语）

**反量化（Dequantization）**:
用缩放因子和零点把量化后的整数映射回近似的实数值，目的是以更高精度来计算，或者检查误差。
_避免使用_: 去量化（unquantization）、解压缩（decompression）

**动态量化（Dynamic quantization）**:
在运行时根据实际出现的值来计算激活值的缩放因子，而不是事先由校准集固定下来。与静态量化相对。
_避免使用_: 即时量化（on-the-fly quantization）、运行时量化（runtime quantization）

**每个权重的有效位数（Effective bits per weight）**:
把缩放因子、零点和其他任何按组存放的元数据都算进来之后，每个权重的平均存储量，例如 4 位权重、每 32 个一组配一个 16 位缩放因子，约为 4.5。
_避免使用_: 未经定义就写 bpw、位宽（bit width，它不含元数据）

**指数位（Exponent bits）**:
浮点格式中决定一个值按 2 的几次幂缩放的那些位，因此也决定它的动态范围。
_避免使用_: 范围位（range bits）

**伪量化（Fake quantization）**:
在前向传播中对一个张量先量化、紧接着反量化，使训练能看到舍入和钳制带来的误差，而算术仍然以浮点进行。
_避免使用_: 模拟量化（simulated quantization，可接受的别名，但只用一个术语）、量化噪声注入（quantization noise injection）

**翻转（Flip）**:
在同一个问题上，基线模型与它的量化版本之间，答案从正确变成错误，或者从错误变成正确。两个方向的翻转在准确率的平均值里会互相抵消，所以要分开计数。
_避免使用_: 答案变化（answer change，错误变成另一个错误也算在内）、退化（regression，只指一个方向）

**GGUF**:
llama.cpp 的单文件模型格式，它存储张量（常常采用它自己的块量化类型），并连同分词器和模型元数据一起存放。
_避免使用_: GGML（那是库名，也是一种更早的格式）、llama 格式（llama format）

**GPTQ**:
一种训练后权重量化方法：一次量化一层权重中的一列，并利用校准激活值带来的二阶信息，更新尚未量化的权重，来补偿每一次舍入误差。
_避免使用_: GPT 量化（GPT quantization）、泛指任何 4 位检查点

**量化粒度（Granularity）**:
有多少个值共用一个缩放因子和零点：整个张量（逐张量）、一个输出通道（逐通道）、一个 token（逐 token），或者通道内固定大小的一组（逐组）。
_避免使用_: 分辨率（resolution）、量化档位（quantization level）

**分组大小（Group size）**:
逐组量化中共用一个缩放因子的连续值的个数，例如 32 或 128。
_避免使用_: 块大小（block size，某种格式本身就这样叫的时候可以接受，例如 MX 或 GGUF）

**海森矩阵（Hessian）**:
在 GPTQ 中，由一层的校准输入构造出的矩阵 `H = 2 X X^T`，每个输入特征对应一行一列。它记录哪些特征会一起变化，并且由这一层权重的每一行共用。
_避免使用_: 曲率矩阵（curvature matrix）、协方差矩阵（covariance matrix，很接近，但不是同一个对象）

**重要性矩阵（Importance matrix）**:
在 llama.cpp 中，根据一段校准文本上的激活值估计出的逐权重重要性，选择每个块的缩放因子时用它给舍入误差加权。
_避免使用_: 未经介绍就在正文中写 imatrix

**内核（Kernel）**:
执行某一种运算的 GPU 例程，例如某种量化方案下的矩阵乘法。一种方案只有在硬件上存在对应的内核时才跑得快。
_避免使用_: 算子（operator，范围更广）、实现（implementation）

**KL 散度（KL divergence）**:
量化模型的下一个 token 分布与基线模型的分布相差多远，在数据集的各个 token 上取平均。两者完全一致时为 0，并且不需要带标签的答案。
_避免使用_: 未经定义就写 KLD、距离（distance，有歧义）

**KV 缓存量化（KV-cache quantization）**:
用更少的位数存储缓存的注意力键和值，以减少随上下文长度和批大小增长的内存。
_避免使用_: 缓存压缩（cache compression，也包括驱逐）、对权重做的 KV 量化（KV quantization of weights）

**损失缩放（Loss scaling）**:
在反向传播之前把损失乘以一个常数，使小梯度在 fp16 这类范围窄的格式中仍能表示出来，然后在更新权重之前再把这个常数除掉。
_避免使用_: 梯度缩放（gradient scaling，与梯度裁剪有歧义）

**机器精度（Machine epsilon）**:
浮点格式中，1 与比它大的下一个可表示值之间的间隔，等于 2 的负尾数位数次方。
_避免使用_: 单位舍入误差（unit roundoff，就近舍入下是它的一半）、精度（precision）

**尾数位（Mantissa bits）**:
浮点格式中决定一个 2 的幂之内各值的间隔有多细的那些位，因此也决定它的精度。
_避免使用_: 有效数字（significand，正确，但只用一个术语）、小数位（fraction bits）

**巨大激活值（Massive activation）**:
LLM 中某一个比其余激活值大好几个数量级的激活值，出现在固定的维度上，以及特定的 token（例如第一个）上。
_避免使用_: 离群特征（outlier feature，相关但不同的模式）、尖峰（spike）

**受内存带宽限制（Memory-bound）**:
速度由字节从内存搬运的快慢而不是算术所限制的负载，小批量解码是典型，每生成一个 token，每个权重都要被读取一次。
_避免使用_: 受带宽限制（bandwidth-bound，可以用，但只用一个术语）、受 IO 限制（IO-bound）

**混合精度分解（Mixed-precision decomposition）**:
拆分一次矩阵乘法，使少数离群特征维度用 16 位计算，其余用 int8 计算，这是 LLM.int8() 的核心。
_避免使用_: 离群值拆分（outlier splitting）、混合精度（mixed precision，范围更广）

**原生格式（Native format）**:
芯片的矩阵单元可以直接用来做乘法的数值格式，与只用于存储的格式相对，后者必须先转换成原生格式才能做乘法。
_避免使用_: 支持的格式（supported format，在存储和计算之间有歧义）

**噪声底限（Noise floor）**:
一个分数在多次运行之间和抽样造成的波动，基线模型与量化模型之间的差异只要低于它，就无法与偶然区分开。
_避免使用_: 误差范围（margin of error，区间只是报告噪声底限的方式）、容差（tolerance）

**离群特征（Outlier feature）**:
隐藏状态中的一个维度，Transformer 的激活值在其中，跨越大多数 token 和各层，始终比在其他维度中大得多。
_避免使用_: 离群通道（outlier channel，对应的权重通道可以这样叫）、不带“离群”一词的涌现特征（emergent feature）

**困惑度（Perplexity）**:
模型赋予一段文本的平均负对数似然的指数，用来快速代表一项改动伤害了模型多少。
_避免使用_: 未经介绍就在正文中写 PPL、准确率（accuracy）

**训练后量化（Post-training quantization）**:
不再做任何训练，最多只用一个小校准集，就把一个已经训练好的模型量化。
_避免使用_: 未经介绍就在正文中写 PTQ、一次性量化（one-shot quantization）

**量化（Quantization）**:
用更少的位数，把模型中的实数值表示在一个更小的档位集合上，代价是一个有界的近似误差。
_避免使用_: 压缩（compression，范围更广）、离散化（discretisation）

**量化配置（Quantization config）**:
模型 `config.json` 中的 `quantization_config` 条目，其中的 `quant_method` 和其他键告诉加载器，存储的张量用了哪种方法、什么位宽和什么分组大小。
_避免使用_: quantize config（某些工具写出的另一个文件）、元数据（metadata）

**量化感知训练（Quantization-aware training）**:
在前向传播中加入伪量化来训练或微调模型，使权重适应它们将要面对的舍入。
_避免使用_: 未经介绍就在正文中写 QAT、量化训练（quantized training，那是以低精度来计算）

**脊点（Ridge point）**:
芯片的峰值算术速率与它的内存带宽所需时间相同时的算术强度，低于它，计算受内存带宽限制，高于它，则受算力限制。
_避免使用_: 屋顶线拐点（roofline knee）、交叉点（crossover）

**旋转（Rotation）**:
把一层的激活值和权重分别乘以一个正交矩阵及其转置，这样不会改变该层的输出，却能把离群值分散到许多通道上，使它们更容易量化。
_避免使用_: 哈达玛变换（Hadamard transform，旋转的一种选择）、非相干处理（incoherence processing，更一般的思路）

**就近舍入（Round-to-nearest）**:
把每个值独立地量化到离它最近的网格档位，不用数据，也不做误差补偿。这是其他一切训练后方法所对照的基线。
_避免使用_: 未经介绍就在正文中写 RTN、朴素量化（naive quantization）

**舍入误差（Rounding error）**:
截断范围之内的值被移到最近的网格档位所产生的误差；就近舍入下最多为半个步长。
_避免使用_: 量化噪声（quantization noise，可以用来指合并后的误差）、精度损失（precision loss）

**Safetensors**:
一种张量文件格式，依次是 8 字节的头部长度、一个包含张量名称、dtype、形状和偏移量的 JSON 头部，然后是原始数据。它只存储张量，所以量化方案要在量化配置中说明。
_避免使用_: 检查点（checkpoint，指整套文件）、权重文件（weights file）

**显著通道（Salient channel）**:
权重矩阵中量化误差影响最大的输入通道，AWQ 是根据它所遇到的激活值的大小，而不是它自身权重的大小来找出它。
_避免使用_: 重要权重（important weight，正文里可以用）、离群通道（outlier channel，是离群特征在权重一侧的名字）

**缩放因子（Scale）**:
量化器中相邻整数档位之间的实数步长，所以一个实数值近似等于缩放因子乘以它的整数。
_避免使用_: 步长（step，公式里可以用）、乘数（multiplier）

**静态量化（Static quantization）**:
事先由校准集固定下激活值的缩放因子，所以运行时不用计算任何统计量。与动态量化相对。
_避免使用_: 离线量化（offline quantization）

**直通估计器（Straight-through estimator）**:
在反向传播中把舍入这一步当作恒等函数，使梯度能够穿过一个真实导数几乎处处为零的运算。
_避免使用_: 未经介绍就在正文中写 STE、代理梯度（surrogate gradient，范围更广）

**超级块（Super-block）**:
在 GGUF 的 k-quant 中，由 256 个权重组成的一组，分成若干子块，每个子块各有自己的缩放因子，这些缩放因子再以一个 16 位的超级块缩放因子为基准做量化。
_避免使用_: 块（block，旧类型中 32 个权重的单位）

**对称量化（Symmetric quantization）**:
零点固定为零的量化，所以网格以零为中心，只需存储缩放因子。
_避免使用_: 只有缩放因子的量化（scale-only quantization）

**仅权重量化（Weight-only quantization）**:
以低精度存储权重，并在内核内部做反量化，而激活值和算术仍保持 16 位。写作 WxA16，例如 W4A16。
_避免使用_: 混合精度量化（mixed-precision quantization，范围更广）

**WxAy 记法（WxAy notation）**:
对一种方案的权重位宽和激活值位宽的简写，例如 W8A8 表示 8 位权重和 8 位激活值，有时再加上 KVz 表示 KV 缓存。
_避免使用_: 激活值并非同样是 int4 时却写 int4

**零点（Zero point）**:
在仿射量化中表示实数零的那个整数，选它是为了让零可以被精确表示。
_避免使用_: 偏移（offset）、偏置（bias）
