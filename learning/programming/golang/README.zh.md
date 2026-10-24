---
title: Go
description: "在团队中对 Go 负责：设计、发布并运维一个生产服务"
type: topic
---

# 学习：Go

成为团队中值得信任、对 Go 负责的工程师：能够设计、发布并运维一个生产级的 Go 服务，评审别人的 Go 代码并具体指出某个设计错在哪里，并识别出一个从其他语言照搬来的设计什么时候是在和 Go 对着干，而不是在用好它。

**最新课程：** [0041. 针对真实数据库的测试](lessons/0041-testing-against-a-real-database.md)

## 成功的标准

- 设计并发布一个生产服务：配置、结构化日志、优雅关闭、健康检查、数据库访问。
- 在不是你写的代码中，用 `-race` 和 `pprof` 调试数据竞争和 goroutine 泄漏。
- 评审同事的 PR，准确说出为什么在那里接口、指针接收者或通道是错误的工具。
- 在运行之前，依据调度器和内存模型而不是实验，预测一个并发程序会做什么。
- 依据 `pprof` 和 `benchstat` 的证据而不是靠猜来减少内存分配。
- 设计一个能保持向后兼容的包 API，并知道什么时候*不该*动用 goroutine。

## 约束

- 不要求有 Go 基础。其他语言的经验能缩短前面几个阶段，但并非必需，而且它会带来一些会被 Go 悄悄惩罚的习惯，因为在这里，错误的直觉照样能通过编译。
- 只需要任意受支持操作系统上的标准工具链。到第 5 阶段为止，都不需要付费工具、云账号或第二台机器。
- 练习都是一次坐下来就能完成的小程序。把它们分散到不同的日子里，正是学习机制本身，而不是一种不便。
- 与版本相关的内容过时得很快。关于当前版本的说法，要对照发布说明来核实，而不是对照书本。

## 范围之外

- 把其他语言作为独立的主题。只有当比较能防止某个习惯被带进 Go 时，才会出现比较。
- 把第三方框架作为独立的主题：路由器、ORM、依赖注入容器、CLI 工具包。标准库直接涵盖了路由、结构化日志和数据库访问，所以课程以它为基础；当团队已经选定了某个框架时，判断它是否值得存在是一项评审技能，属于第 6 阶段。
- 前端、WASM 和移动端目标。
- 超出一个 Go 服务运行所需的 Kubernetes 和基础设施内容。把二进制文件放进容器镜像，以及运行、加固和调试这个容器，属于 [`infrastructure/containers`](../../infrastructure/containers/)。在集群上运行它，包括集群如何处理它的健康检查和关闭信号，属于 [`infrastructure/kubernetes`](../../infrastructure/kubernetes/)。
- 超出能预测程序行为那个程度的编译器和运行时内部机制。

## 学习路线

共七个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 基础 | 0001 至 0007 | 类型、零值、值语义与指针语义、切片和 map 的机制（包括别名）、字符串与 rune 与字节、包的基础 | 不运行代码就能预测别名和复制行为 |
| 2. 惯用写法 | 0008 至 0014 | 作为值的错误、用 `%w` 包装、`errors.Is`/`As`、隐式的接口实现、小接口、结构体嵌入、包的布局与命名 | 写出的 Go 不会被评审者说成“用 Go 语法写的 Java” |
| 3. 并发 | 0015 至 0021 | goroutine、通道、`select`、`sync` 原语、`context` 取消、`errgroup`、竞争检测器、内存模型、泄漏模式 | 能在陌生代码中找出泄漏和竞争，并解释被违反的是哪项保证 |
| 4. 生产 | 0022 至 0027 | HTTP 服务、配置、`slog`、优雅关闭、健康检查、数据库访问、真正有价值时使用泛型 | 搭建过一个经得起运维的服务；第 7 阶段用指标、追踪，以及围绕处理器和数据库（而不只是围绕函数）的测试把它补全 |
| 5. 性能与工具 | 0028 至 0033 | 表驱动测试、模糊测试、基准测试、`pprof`、逃逸分析、减少内存分配、模块与版本、发布构建 | 依据性能剖析做优化，并用 `benchstat` 证明收益 |
| 6. 判断力 | 0034 至 0037 | API 设计与兼容性、什么时候*不该*使用 goroutine、评审、通过阅读标准库源码寻找答案 | 值得信任去做出判断，并向别人解释清楚 |
| 7. 生产可观测性与测试 | 0038 至 0041 | 中间件与请求作用域的值、指标与追踪（RED/USE、OpenTelemetry）、测试 HTTP 处理器、针对真实数据库的集成测试 | 发布的服务具备第 4 阶段没有做到的第三和第四种信号：指标、追踪，以及围绕处理器和数据库（而不只是围绕函数）的测试 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | 值与零值 | 每个已声明的变量都已经可以使用，而 nil 是一个值，而不是“不存在” |
| [0002](lessons/0002-value-semantics-and-pointers.md) | 值语义与指针 | 每次赋值和每个参数都是一份副本，而指针是你选择不复制的方式 |
| [0003](lessons/0003-slices-and-the-backing-array.md) | 切片与底层数组 | 切片是一个三字长的头部，指向一个别人可能也持有的数组 |
| [0004](lessons/0004-maps-and-their-rules.md) | map 及其规则 | comma-ok、不可取址的元素、随机化的迭代顺序，以及共享 map 抛出的致命错误 |
| [0005](lessons/0005-strings-bytes-and-runes.md) | 字符串、字节与 rune | 字符串是不可变的 UTF-8 字节，所以 len 不是字符数，下标取到的也不是字符 |
| [0006](lessons/0006-methods-and-method-sets.md) | 方法与方法集 | 你选择哪种接收者，决定的是哪些类型实现了某个接口，而不只是谁能修改值 |
| [0007](lessons/0007-packages-and-modules.md) | 包与模块 | 一个目录就是一个包，首字母大写就是全部的可见性系统，而 internal 是强制执行的 |
| [0008](lessons/0008-errors-are-values.md) | 错误即值 | error 是一个普通的接口，所以失败是你要处理的数据，而不是逃逸出去的控制流 |
| [0009](lessons/0009-wrapping-is-and-as.md) | 包装、Is 与 As | %w 构建出一条链，Is 和 As 在链上搜索，而包装是一项 API 承诺 |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer、panic 与 recover | 参数在 defer 语句处就被固定，而 panic 用于 bug，而不是用于失败 |
| [0011](lessons/0011-implicit-interfaces.md) | 接口是隐式实现的 | 由使用方声明接口，实现方从不提及它，而小正是关键所在 |
| [0012](lessons/0012-the-nil-interface-trap.md) | nil 接口陷阱 | 接口持有一个类型和一个值，所以装着 nil 指针的接口并不是 nil 接口 |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | 嵌入不是继承 | 提升看起来像子类化，直到某个被嵌入的方法拒绝调用你的覆盖实现 |
| [0014](lessons/0014-designing-a-package.md) | 设计一个包 | 文档注释、小的导出面，以及只朝一个方向的依赖箭头 |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | goroutine 及其代价 | 便宜到可以启动成千上万个，却从来不至于免费到可以不带停止计划地启动 |
| [0016](lessons/0016-channels.md) | 通道 | 无缓冲意味着会合，关闭是一次广播，而且只有发送方可以关闭 |
| [0017](lessons/0017-select-and-timeouts.md) | select 与超时 | 同时等待多个通道，在已就绪的通道中随机选择，并用 nil 禁用某个分支 |
| [0018](lessons/0018-context-cancellation.md) | context 与取消 | 一个值，把截止时间和停止信号沿着它经过的每次调用传递下去 |
| [0019](lessons/0019-sync-primitives.md) | sync 与 errgroup | 什么时候共享内存胜过传递内存，以及几乎涵盖一切的四种原语 |
| [0020](lessons/0020-memory-model-and-races.md) | 内存模型与竞争 | 数据竞争是未定义行为，而不是抛硬币，而检测器只能看到实际运行到的代码 |
| [0021](lessons/0021-goroutine-leaks.md) | goroutine 泄漏 | 永远阻塞的 goroutine 永远不会被回收，它持有的一切也不会 |
| [0022](lessons/0022-an-http-server.md) | 值得运维的 HTTP 服务器 | 处理器、路由模式，以及默认服务器没有设置的四个超时 |
| [0023](lessons/0023-configuration-and-startup.md) | 配置与启动 | 只负责组装的 main、返回 error 的 run 函数，以及在第一个请求之前完成的校验 |
| [0024](lessons/0024-structured-logging-with-slog.md) | 用 slog 做结构化日志 | 键值属性、作为依赖传入的单个 logger，以及无需部署就能调整的级别 |
| [0025](lessons/0025-graceful-shutdown.md) | 优雅关闭与健康检查 | 捕获信号，停止接收新请求，排空进行中的工作，然后按顺序关闭依赖 |
| [0026](lessons/0026-talking-to-a-database.md) | 与数据库对话 | sql.DB 是一个连接池，每次调用都接收一个 context，而没有关闭的 Rows 会占住一个连接 |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | 真正有价值的泛型 | 类型参数消除跨类型的重复，而对于行为，接口仍然是正确的答案 |
| [0028](lessons/0028-table-driven-tests.md) | 表驱动测试 | 一个测试函数、一个用例切片，以及能自己命名、各自独立失败的子测试 |
| [0029](lessons/0029-fuzzing.md) | 模糊测试 | 声明一个必须始终成立的性质，然后让工具链去搜索打破它的输入 |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | 可信的基准测试 | b.Loop、重复运行和 benchstat，因为一次运行得出的一个数字算不上测量 |
| [0031](lessons/0031-reading-a-pprof-profile.md) | 读懂 pprof 剖析结果 | 在改动任何一行代码之前，先找出时间和内存实际花在了哪里 |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | 逃逸分析与内存分配 | 一个值为什么会落到堆上，如何向编译器询问，以及哪些修复真正有回报 |
| [0033](lessons/0033-modules-and-release-builds.md) | 模块与发布构建 | 最小版本选择、v2 路径规则，以及让二进制文件可复现的构建标志 |
| [0034](lessons/0034-api-design-and-compatibility.md) | API 设计与兼容性 | 哪些东西可以添加而不破坏调用方，以及总会破坏调用方的三种改动 |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | 什么时候不该使用 goroutine | 并发是一种结构，而不是一种加速手段，而顺序执行的版本往往才是正确答案 |
| [0036](lessons/0036-reviewing-go.md) | 评审 Go 代码 | 让工具去发现风格问题，把你的注意力花在生命周期、边界以及编译器检查不了的东西上 |
| [0037](lessons/0037-reading-the-standard-library.md) | 阅读标准库 | 源码就在你的机器上，它能平息文档平息不了的争论，而且它就是风格的参照 |
| [0038](lessons/0038-middleware-and-request-scoped-values.md) | 中间件与请求作用域的值 | 第 22 课展示了中间件把一个值写入 context；本课是另一半，即安全地把它读出来，以及那个例子从未需要的机制：一个决定根本不调用下一个处理器的中间件 |
| [0039](lessons/0039-metrics-and-tracing.md) | 指标与追踪 | pprof 在本地剖析单个进程自身的 CPU 和内存；指标和追踪则是两种生产信号，回答的是另一组问题：服务此刻的整体状况如何，以及这一个请求在它经过的每个服务中发生了什么 |
| [0040](lessons/0040-testing-an-http-handler.md) | 测试 HTTP 处理器 | 第 22 课顺带提到，ResponseRecorder 让处理器无需网络就能测试；本课把这个说法落到实处，说明为什么接口这道接缝让它成为可能，以及用于测试客户端而非处理器的另一个容易混淆的工具 |
| [0041](lessons/0041-testing-against-a-real-database.md) | 针对真实数据库的测试 | 这是第 7 阶段的收官之作：testing.Short() 把慢速的数据库测试挡在快速的本地循环之外，一个开启后从不提交的事务为每个测试提供干净、隔离的起点，而一个集成测试终于把中间件、处理器和真实数据库放在一起检验 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [切片与 map](reference/slice-and-map-mechanics.md)：别名、容量，以及会引发 panic 的操作
- [错误处理](reference/error-handling.md)：包装动词、匹配函数，以及能通过编译的陷阱
- [并发模式](reference/concurrency-patterns.md)：通道规则、context 构造函数、泄漏检查清单
- [工具链命令](reference/toolchain-commands.md)：测试、基准测试、性能剖析和发布构建的标志
- [评审清单](reference/review-checklist.md)：工具能发现什么，以及你必须自己发现什么

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
