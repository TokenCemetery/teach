---
title: C#
description: "掌控一个 C# 服务：类型系统、async，以及 CLR 如何处理你写下的代码，从零开始"
type: topic
---

# 学习：C\#

成为团队中值得信任、能掌控一个 C# 服务的工程师：能为领域建模，并在 struct、class 和 record 之间做出正确选择，能编写并推理 `async`/`await` 代码，能用 LINQ 流畅地查询和转换数据，能交付一个有类型、有测试的 ASP.NET Core 后端，并能解释 CLR 如何处理你写下的代码。

**最新课程：** [45. NuGet 打包与版本管理](lessons/0045-nuget-packaging-and-versioning.md)

## 成功的标准

- 为领域建模时在 struct、class 和 record 之间做出正确选择，并依据 CLR 的实际行为为这个选择辩护。
- 编写 `async`/`await` 代码，并解释方法的执行在每个 `await` 处发生了什么。
- 用 LINQ 流畅地查询和转换数据。
- 交付一个有类型、有测试、按 C# 惯用方式设计的 ASP.NET Core 后端服务。
- 面对带着某种“只是能编译”习惯写出的 C#（该用 struct 的地方用了 class，该用 `async`/`await` 的地方用了回调），说出这个习惯，并用惯用写法重写它。

## 约束

- 不要求有 C# 基础。另一门面向对象语言（Java、Kotlin）的经验能缩短前面的阶段，但并非必需，而且它会带来 C# 悄悄惩罚的习惯：该用 struct 或 record 的地方用了 class，`async`/`await` 读起来更好的地方用了回调。
- 以 ASP.NET Core 和后端服务为背景；不讲没有这个侧重点的通用 .NET。

## 范围之外

- Unity 和用 C# 做游戏开发：背景差异足够大，这里不涉及。
- JIT 的内部机制，以及编写或手工调优垃圾回收器：第 8 阶段讲分代堆、GC 模式和性能剖析，深度以服务负责人能度量并为某个选择辩护为准，而不是实现一个 GC 的深度。
- 容器镜像：把发布出来的服务放进镜像，以及运行、加固和调试这个容器，见 [`infrastructure/containers`](../../infrastructure/containers/)。
- 在集群上运行服务，包括 Kubernetes 如何处理它的存活检查和就绪检查，见 [`infrastructure/kubernetes`](../../infrastructure/kubernetes/)。

## 学习路线

共十一个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 基础 | 0001 至 0006 | 值类型与引用类型（struct 与 class）、可空值类型、基本类型与字符串插值、集合（`List`、`Dictionary`、`IEnumerable`）、控制流、异常 | 不运行代码就能预测是复制还是引用的行为 |
| 2. 建模 | 0007 至 0011 | 属性、`record` 类型、模式匹配与 switch 表达式、带默认实现的接口、泛型 | 为领域建模时选择合适的类型，而不是什么都用 class |
| 3. 惯用法 | 0012 至 0016 | 扩展方法、LINQ 查询语法与方法语法、委托与事件、可空引用类型、表达式主体成员 | 写出的 C# 不会被评审者说成是翻译过来的 Java |
| 4. 异步 | 0017 至 0021 | `Task` 模型、`async`/`await` 的机制、`Task` 组合、取消令牌、`IAsyncEnumerable` | 能解释 `await` 对方法的执行做了什么，并预测异步程序的行为 |
| 5. 测试与构建 | 0022 至 0024 | xUnit/NUnit、模拟、`dotnet` CLI 以及项目与包管理 | 别人能克隆、构建、测试并运行它 |
| 6. 交付服务 | 0025 至 0029 | ASP.NET Core 路由与中间件、依赖注入、配置、Entity Framework Core 基础、组织一个有类型、有测试的后端 | 交付一个有类型、有测试的 ASP.NET Core 服务 |
| 7. 判断力 | 0030 至 0031 | 把 `async`/`await` 与 Java 虚拟线程、LINQ 与 Stream API 做比较，评审 C# 中只是能编译的习惯 | 可以信赖他做出判断，并向别人解释清楚 |
| 8. CLR 运行时与性能 | 0032 至 0037 | 托管堆的分代设计、GC 模式、`Span<T>`/`Memory<T>`、`stackalloc`/`ArrayPool<T>`、用 BenchmarkDotNet 度量 struct 与 class，以及性能剖析 | 依据剖析结果做优化，并用可信的基准测试为收益辩护，且能对应到 CLR 实际的分代和分配行为 |
| 9. 资源生命周期 | 0038 | 实现 `IDisposable` 和 `IAsyncDisposable`：dispose 模式、`disposing` 参数、终结器，以及 `DisposeAsyncCore` | 能实现正确且幂等的 dispose 模式，而不只是通过 `using` 使用它 |
| 10. 运维与加固服务 | 0039 至 0042 | 用 `ILogger` 做结构化日志、存活与就绪健康检查、OpenTelemetry、身份验证与授权，以及 `System.Text.Json` 序列化 | 交付的服务不只是能构建，还可观测、可做健康检查、安全，并能正确序列化 |
| 11. API 演进与打包 | 0043 至 0045 | 二进制兼容、源码兼容与行为兼容、`[Obsolete]` 与弃用、NuGet 打包与语义化版本 | 能准确判定一次改动对兼容性的影响，并在不让调用方猝不及防的前提下演进已发布的 API |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | struct 与 class | Java 从未给过你的类型系统选择，以及 CLR 实际如何处理二者 |
| [0002](lessons/0002-nullable-value-types.md) | 可空值类型 | 为什么 int? 仍然是值类型，让两个方向的比较都为 false 的规则，以及装箱对这个包装做了什么 |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | 基本类型与字符串插值 | 作为 .NET 类型别名的关键字，为什么 decimal 是内置类型而不是一个类，以及插值占位的宽度、格式和副作用规则 |
| [0004](lessons/0004-collections.md) | 集合 | 作为整个路线所依赖的抽象的 IEnumerable，以及在 Java 的 map 返回 null 的地方会抛异常的字典查找 |
| [0005](lessons/0005-control-flow.md) | 控制流 | 控制流无法从 Java 照搬的三个地方：foreach 的鸭子类型枚举器、没有贯穿的 switch，以及作为合法跳转的 goto |
| [0006](lessons/0006-exceptions.md) | 异常 | 异常筛选器和被“捕获后重新抛出”破坏的堆栈跟踪，用于确定性清理的 using，以及第 1 阶段的总结练习 |
| [0007](lessons/0007-properties.md) | 属性 | 作为语言特性的访问器，required、init 和非空类型这三个相互独立的承诺，以及没有后备字段的计算属性 |
| [0008](lessons/0008-record-types.md) | record 类型 | record 修饰符实际生成了什么，为什么相等性取决于运行时类型，以及 with 表达式解决不了的浅层不可变性 |
| [0009](lessons/0009-pattern-matching.md) | 模式匹配 | 模式的词汇，switch 表达式的穷尽性及其唯一一个无声的缺口，以及为什么分支顺序是一个编译期问题 |
| [0010](lessons/0010-interfaces.md) | 接口 | 接口能携带实现之后可以包含什么，那个看似是自动属性其实不是的写法，以及只能通过接口调用的成员 |
| [0011](lessons/0011-generics.md) | 泛型 | 作为描述类型参数必须满足什么的词汇的约束，作为关于位置的规则的变体，以及选择合适类型的第 2 阶段总结练习 |
| [0012](lessons/0012-extension-methods.md) | 扩展方法 | 编译成同一段 IL 的两种语法，阻止扩展方法覆盖任何东西的绑定规则，以及它在调用处的代价 |
| [0013](lessons/0013-linq.md) | LINQ | 一种查询语言、两种语法、没有语义差别，为什么不迭代就什么都不会执行，以及让同一个查询能到达数据库的表达式树 |
| [0014](lessons/0014-delegates-and-events.md) | 委托与事件 | 作为一种类型、签名包含返回类型的委托，一个处理程序抛异常就会让其余的停下的调用列表，以及 event 关键字从调用方手里拿走了什么 |
| [0015](lessons/0015-nullable-reference-types.md) | 可空引用类型 | 是注解而不是类型，编译器沿着你的控制流追踪的空状态，以及唯一一个会把你的注解变成运行时行为的库 |
| [0016](lessons/0016-expression-bodied-members.md) | 表达式主体成员 | 箭头符号的第二个用途，void 成员的语句表达式规则，以及重写翻译式 Java 的第 3 阶段总结练习 |
| [0017](lessons/0017-the-task-model.md) | Task 模型 | 作为异步操作而不是线程的 task，它产生的四种方式，以及会让你以为已经结束的进程终止的 AggregateException |
| [0018](lessons/0018-async-and-await.md) | async 与 await | await 对外层方法做了什么，禁止使用它的三个地方，以及为什么 async void 破坏了调用方唯一拥有的机制 |
| [0019](lessons/0019-task-composition.md) | Task 组合 | 先启动工作再 await 它，让 LINQ 构建的 task 列表真正跑起来的 ToArray，以及 WhenAny 所需的两次 await |
| [0020](lessons/0020-cancellation-tokens.md) | 取消令牌 | 一个请求方、多个监听方的协作式取消，为什么提前返回报告的是成功，以及决定一个 task 是否声称自己被取消的令牌比较 |
| [0021](lessons/0021-async-streams.md) | 异步流 | await foreach 背后的三个接口，让消费方的令牌到达异步迭代器主体的特性，以及预测异步程序的第 4 阶段总结练习 |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit 与 NUnit | 让 xUnit 无需任何 setup 特性的“每个测试一个实例”规则，theory 这个词的两种不同含义，以及共享 fixture 悄悄付出的并行代价 |
| [0023](lessons/0023-mocking.md) | 模拟 | 每个替身库背后的运行时代理，决定它能替换什么的 C# 默认规则，以及调用根本没发生也能通过的模拟断言 |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | dotnet CLI 与包 | 新克隆的仓库需要的那一条命令，为什么包版本是下限而不是固定值，重排了命令的那次 SDK 发布，以及第 5 阶段总结练习 |
| [0025](lessons/0025-routing-and-middleware.md) | 路由与中间件 | 共用一个 Program.cs 的两套系统，一套由你书写的顺序决定，一套由模板优先级决定，以及决定中间件能知道什么、会不会运行的两个位置 |
| [0026](lessons/0026-dependency-injection.md) | 依赖注入 | 三种生命周期，是容器只在它看得见的地方才强制执行的声明，悄悄提升短生命周期服务的长生命周期服务，以及为什么没人去释放容器创建的东西 |
| [0027](lessons/0027-configuration.md) | 配置 | 一个由字符串组成、最后一个提供程序胜出的扁平字典，按生命周期而不是按喜好区分的三个选项接口，以及除非你要求，否则要等到第一个请求才执行的校验 |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | 记住你查询过什么、让一次赋值变成一次更新的上下文，查询唯一允许回退到客户端执行的地方，以及为什么第 4 阶段那种重叠执行工作的习惯会破坏它 |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | 组织一个有类型、有测试的后端 | 作为测试替换注册项的接缝的容器，在单元测试和集成测试之间做选择的文档化规则，以及四个都能编译的缺陷组成的第 6 阶段总结练习 |
| [0030](lessons/0030-two-comparisons-with-java.md) | 与 Java 的两个比较 | 同一个等待问题在两个不同层面上的解法，为什么 Java 的答案是去掉 C# 所要求的写法而不是采纳它，以及在 Stream 中没有对应物的表达式树 |
| [0031](lessons/0031-reviewing-csharp.md) | 评审 C# 代码库 | 风格意见与能说出具体代价之间的区别，按编译器永远不会告诉你的内容排序的评审流程，以及本路线从第 1 课起一直在收集的那些习惯 |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | 托管堆与分代 | 第 1 课说过 class 实例存放在托管堆上；本课揭开它在那里经历了什么，为什么堆被分成三代，以及为什么大多数对象注定在最年轻的一代中死去，从不被提升 |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | GC 模式与权衡 | 第 32 课建立了分代堆；本课讲一次回收实际上如何在其上运行，用一个专用线程还是每个核一个线程，阻塞所有托管线程还是让其中大多数继续运行，以及即使是非阻塞模式也仍然必须让一切停下的那一刻 |
| [0034](lessons/0034-span-and-memory.md) | Span 与 Memory | 一个对现有内存的零分配视图，它完全不进入第 32 课的分代系统，让它安全地只存在于栈上的编译器限制，以及专为它唯一做不到的事（跨越 await）而构建、可放在堆上的对应类型 |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc 与 ArrayPool | 第 34 课让 Span<T> 查看 stackalloc 分配的内存；本课讲 stackalloc 实际分配了什么，为什么与 ref struct 搭配才让它安全，它真正的风险（栈溢出，而不是垃圾回收），以及作为对栈来说太大或存活太久的缓冲区的后备方案的 ArrayPool<T> |
| [0036](lessons/0036-struct-vs-class-measured.md) | 实测 struct 与 class | 第 1 课论证过 struct 能避免同样形状的 class 所需的一次堆分配；本课就是把这个论证从推理变成度量的地方，以及为什么最显而易见的度量方式得出的数字毫无意义 |
| [0037](lessons/0037-profiling-a-csharp-service.md) | 剖析 C# 服务 | dotnet-counters 捕捉症状，dotnet-trace 找出其背后的热点调用栈，只在预热之后剖析以免度量到的是 JIT，以及把剖析结果送回本阶段某个手段的第 8 阶段总结练习 |
| [0038](lessons/0038-idisposable-and-iasyncdisposable.md) | IDisposable 与 IAsyncDisposable | 第 6 课从使用方的角度教了 using，第 26 课教了容器会释放它创建的东西；本课讲另一面，真正实现 IDisposable 和 IAsyncDisposable，以及让类型可以安全地多次释放、安全地终结、安全地 await 的模式 |
| [0039](lessons/0039-logging-and-health-checks.md) | 日志与健康检查 | 一个没人能观测、也没人能问一句“你还正常吗”的有类型、有测试的后端，还不算交付完成；本课把 ILogger 的结构化日志以及存活与就绪的区分接入 Program.cs，方式与第 25 课接入路由、第 26 课接入容器相同 |
| [0040](lessons/0040-opentelemetry.md) | OpenTelemetry | 第 39 课的 ILogger 已经是 OpenTelemetry 三大支柱之一；本课通过框架已内置的 API 加上另外两个支柱，指标和追踪，并用第 25、26 和 39 课已经教过的同一种 AddX 模式把三者接入服务 |
| [0041](lessons/0041-authentication-and-authorization.md) | 身份验证与授权 | 身份验证回答你是谁，授权回答你被允许做什么，文档把二者作为独立的关注点，尽管一个依赖另一个，本课用第 25 课的中间件顺序规则把它们接入，并加上第 39 课的健康检查真正需要的 AllowAnonymous 例外 |
| [0042](lessons/0042-system-text-json.md) | System.Text.Json | 序列化器本身的默认值（PascalCase、区分大小写）并不是 ASP.NET Core 在 HTTP 边界上实际使用的设置（camelCase、不区分大小写），这是一个真实的分歧，值得在它产生令人困惑的测试结果之前点明，另外还有作为反射的编译期替代方案的源生成 |
| [0043](lessons/0043-api-compatibility.md) | API 兼容性 | 一次能干净地重新编译的改动，仍可能让每个不重新编译的调用方失败，一次无法编译的改动，对已经拥有可用二进制的调用方可能完全没问题，而两者都不是的改动，仍可能悄悄地做出不同的行为，而这恰恰是语义化版本存在的意义所要警示调用方的那一种 |
| [0044](lessons/0044-obsolete-and-deprecation.md) | Obsolete 与弃用 | 第 43 课说明了什么算破坏性改动；ObsoleteAttribute 是已发布的 API 预告破坏性改动即将到来的方式，在同一个成员上从可抑制的警告逐步升级为真正的编译错误，并配上自定义诊断 ID，使某一项弃用的警告可以被单独屏蔽，而不必屏蔽项目中所有其他警告 |
| [0045](lessons/0045-nuget-packaging-and-versioning.md) | NuGet 打包与版本管理 | 本路线的最后一课把第 11 阶段串起来：第 43 课的兼容性类别真正能支撑的版本号，NuGet 除了称其为预发布之外不做任何强制的预发布后缀，违背直觉的上限建议，以及重新构建后可能让你测到的陈旧包 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [值类型与引用类型](reference/value-vs-reference-types.md)：struct 与 class、可空值类型、预测是复制还是引用的行为
- [建模](reference/modelling.md)：`record` 类型、模式匹配与 switch 表达式、带默认实现的接口、泛型
- [惯用法](reference/idiom.md)：扩展方法、LINQ、委托与事件、可空引用类型
- [异步](reference/async.md)：`Task` 模型、`async`/`await` 的机制、取消令牌、`IAsyncEnumerable`
- [测试与构建](reference/testing-and-build.md)：xUnit/NUnit、模拟、`dotnet` CLI 以及项目与包管理
- [交付服务](reference/shipping-the-service.md)：ASP.NET Core 路由与中间件、依赖注入、配置、Entity Framework Core 基础
- [判断力](reference/judgment.md)：`async`/`await` 与 Java 虚拟线程、LINQ 与 Stream API、评审 C# 中只是能编译的习惯

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
