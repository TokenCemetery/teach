---
title: Kotlin
description: "在 JVM 上掌控 Kotlin：空安全、协程，以及从零开始写出地道的 Kotlin"
type: topic
---

# 学习：Kotlin

成为团队中值得信任、能掌控 Kotlin 的工程师，无论是在后端服务还是 Android 应用中：能以地道的方式为领域建模，能编写并推理协程和 `Flow`，能交付一个有类型、有测试的 Kotlin 服务或 Android 组件，并能评审别人的 Kotlin 代码，具体说出某个结构正在让他们付出什么代价。

**最新课程：** [44. runTest 之外的协程测试](lessons/0044-testing-coroutines-beyond-runtest.md)

## 成功的标准

- 用 data class、sealed class 和枚举为领域建模，并知道什么时候空安全（而不是异常）才是正确的信号。
- 编写并推理协程和 `Flow`，并把这个模型与 Java 虚拟线程做比较。
- 交付一个有类型、有测试、以地道方式设计的 Kotlin 后端服务或 Android 组件。
- 面对带着某种“只是能编译”习惯写出的 Kotlin（用防御性的空检查代替类型系统，用回调代替协程），说出这个习惯，并用地道的写法重写它。

## 约束

- 不要求有 Kotlin 基础。Java 或另一门 JVM 语言的经验能缩短前面的阶段，但并非必需，而且它会带来 Kotlin 悄悄惩罚的习惯：用防御性的空检查代替类型系统，用 data class 或 sealed 类型能表达得更好的地方用了普通 class。
- 同时涵盖后端（服务端）和 Android 两种背景，在二者出现分歧的地方分别讲到。
- 只需要一个 JDK、Kotlin 工具链和一个终端；只在 Android 专属内容需要时才用到 Android Studio。

## 范围之外

- 超出解释 Kotlin 自身编译后行为所需深度的 JVM 内部机制（完整的垃圾回收器调优、性能剖析、字节码工程）：见 [`programming/java`](../../programming/java/)，需要更深入时链接过去，而不在这里重讲。
- 把其他 JVM 语言（Java、Scala、Clojure、Groovy）本身作为学习对象，不过在有助于说明某个 Kotlin 惯用法的地方会出现对比。
- Kotlin Multiplatform：以 JS、Native 或 Wasm 为目标，在各个源集之间组织 `expect`/`actual` 声明，以及这些目标带来的各平台标准库差异。按照本主题使命自身的定位，整条路线只讲 JVM；这里若要有一课，就需要它自己的 Gradle 配置和它自己的一套惯用法，而不是一节加了多平台脚注的 JVM 课程。`kotlinx.serialization`（第 38 课）是唯一提到多平台覆盖范围的地方，它是作为某个 JVM 侧设计选择的文档化理由出现的，而不是作为多平台内容本身。

## 学习路线

共十一个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 基础 | 0001 至 0006 | 空安全、`val`/`var` 与不可变性、值与引用、基本类型与字符串模板、集合基础（`List`/`Set`/`Map`，可变与只读）、控制流（`when`、区间、`for`） | 不运行代码就能预测可空性和可变性 |
| 2. 建模 | 0007 至 0012 | 类与属性、data class、sealed class 与穷尽的 `when`、枚举、对象声明与伴生对象、带默认方法的接口 | 为领域建模时不会首先想到“一样东西一个类”的层次结构 |
| 3. 惯用法 | 0013 至 0018 | 扩展函数、作用域函数（`let`/`run`/`with`/`apply`/`also`）、高阶函数与 lambda、内联函数与具体化泛型、委托（`by`）、运算符重载 | 写出的 Kotlin 不会被评审者说成是翻译过来的 Java |
| 4. 集合与序列 | 0019 至 0021 | Kotlin 的集合操作符、惰性的 `Sequence` 与及早求值的集合、分组与折叠 | 能在集合流水线和序列之间做出选择，并为各自的代价辩护 |
| 5. 并发 | 0022 至 0027 | 线程与 JVM 内存模型基础、挂起函数与协程构建器、结构化并发、协程上下文与调度器、`Flow`、取消与异常处理 | 在运行之前就能预测一个并发协程程序会做什么，并把这个模型与 Java 虚拟线程做比较 |
| 6. 测试与构建 | 0028 至 0030 | Kotlin 测试框架、模拟、Gradle Kotlin DSL 与依赖管理 | 别人能克隆、构建、测试并运行它 |
| 7. 交付服务 | 0031 至 0033 | 组织一个有类型、有测试的后端服务，在平台出现分歧的地方使用 Android 专属惯用法，泛型与型变（`in`/`out`） | 已经组织好一个有类型、有测试的 Kotlin 后端服务或 Android 组件；第 10 阶段用 HTTP 层、配置、日志和持久化把它补全 |
| 8. 判断力 | 0034 至 0035 | 与 Java 互操作，评审 Kotlin 并准确说出某个结构的代价 | 可以信赖他做出判断，并向别人解释清楚 |
| 9. 进阶惯用法 | 0036 至 0039 | 类型安全的构建器与 DSL、`value class`/`@JvmInline`、`kotlinx.serialization`、`Result` 与错误处理惯用法 | 能以地道的方式写出一个小型类型安全构建器 DSL、一个零开销的包装类型，以及一条基于 `Result` 的错误路径 |
| 10. 补全服务 | 0040 至 0043 | 为第 7 阶段开始组织的 Kotlin 后端服务加上 HTTP 层、配置、日志和持久化 | 交付的 Kotlin 后端服务具备路由好的 HTTP 层、外部化配置、结构化日志和数据库访问，而不只是一个组织好的空壳 |
| 11. runTest 之外的协程测试 | 0044 | 针对永不完成的 flow 使用 Turbine 的 `cancelAndIgnoreRemainingEvents()`，以及在取消是协作式的前提下，取消测试实际必须断言什么 | 测试一个无限 flow 而不会挂起，并依据取消实际的、有文档说明的证据来测试它，而不只是看一个 `Job` 标志 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | 空安全 | 把“这里会不会是 null”从运行时的意外变成编译期的问题，以及 Java 习惯如何让它前功尽弃 |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var 与不可变性 | 为什么 val 是值得坚持的默认选择，它实际保证了什么（以及没有保证什么），以及条件反射般使用 var 的 Java 习惯 |
| [0003](lessons/0003-values-vs-references.md) | 值与引用 | 为什么 == 在 Kotlin 中的含义与 Java 不同，以及按 Java 习惯写 == 会产生的那个具体缺陷 |
| [0004](lessons/0004-basic-types-and-string-templates.md) | 基本类型与字符串模板 | 为什么 Kotlin 在语言层面没有基本类型，以及作为语言特性、而不是带了额外语法的拼接的字符串模板 |
| [0005](lessons/0005-collections-basics.md) | 集合基础 | 通过接口实现只读的 List、Set 和 Map，以及为什么由 val 持有的可变集合仍然是可变的 |
| [0006](lessons/0006-control-flow.md) | 控制流 | 作为能产生值的表达式的 if 和 when，区间实际上是什么，以及不运行代码就预测可空性和可变性的第 1 阶段总结练习 |
| [0007](lessons/0007-classes-and-properties.md) | 类与属性 | 作为 Java getter/setter 样板代码替代品的属性，以及为什么 Kotlin 文档本身就说类应该是最后才考虑的选择 |
| [0008](lessons/0008-data-classes.md) | data class | data class 实际生成了什么，以及只有主构造函数中的属性才参与其中的那条微妙规则 |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | sealed class 与穷尽的 when | 把一个层次结构密封起来，如何让 when 的穷尽性从手工的承诺变成由编译器检查的保证 |
| [0010](lessons/0010-enums.md) | 枚举 | 每个枚举常量都是带有自身状态和行为的真实对象，以及枚举在什么情况下确切地比 sealed class 更合适 |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | 对象声明与伴生对象 | 声明出来而不是手工实现的单例，以及作为 Kotlin 对 Java 静态成员真正替代品的伴生对象 |
| [0012](lessons/0012-interfaces-with-default-methods.md) | 带默认方法的接口 | 为什么 Kotlin 接口能实现行为却永远不能保存状态，以及如何显式地解决菱形冲突 |
| [0013](lessons/0013-extension-functions.md) | 扩展函数 | 不通过继承给类型添加行为，以及第一次碰到时总会让人栽跟头的静态分派陷阱 |
| [0014](lessons/0014-scope-functions.md) | 作用域函数 | 根据每个函数返回什么、如何暴露对象，而不是凭习惯，在 let、run、with、apply 和 also 之间做出选择 |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | 高阶函数与 lambda | 作为真正类型的函数类型，尾随 lambda 语法，以及作用域函数实际所依赖的接收者机制 |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | 内联函数与具体化泛型 | 为什么 inline 是为了消除一项真实的开销而存在的，为什么它使非局部返回成为可能，以及为什么具体化类型参数只因内联才能工作 |
| [0017](lessons/0017-delegation.md) | 委托 | 零样板代码地通过转发给所持有的对象来实现接口，以及通过 by lazy 和自定义委托实现可复用的属性行为 |
| [0018](lessons/0018-operator-overloading.md) | 运算符重载 | 运算符就是带有固定符号映射的普通具名函数，以及只在它的含义与符号本来的含义一致时才实现它的那份自律 |
| [0019](lessons/0019-collection-operators.md) | 集合操作符 | 作为扩展函数、及早地返回新集合的集合操作符，以及会错估一串操作符代价的 Java Stream 习惯 |
| [0020](lessons/0020-sequences-and-laziness.md) | 序列与惰性 | 为什么同一串操作符在 Sequence 上的行为不同，终端操作实际上是做什么用的，以及惰性在什么时候花掉的比省下的还多 |
| [0021](lessons/0021-grouping-and-folding.md) | 分组与折叠 | 用 fold 和 reduce 做聚合，不构建分组就完成分组统计，以及为流水线的代价辩护的第 4 阶段总结练习 |
| [0022](lessons/0022-threads-and-the-memory-model.md) | 线程与内存模型 | 为什么 Kotlin 在 JVM 上没有自己的内存模型，它用注解而不是关键字表达的三个结构，以及 val 不能给你的两项保证 |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | 挂起函数与协程构建器 | suspend 实际改变了函数的什么，三个构建器以及各自返回什么，以及为什么挂起代码读起来仍然是从上到下的 |
| [0024](lessons/0024-structured-concurrency.md) | 结构化并发 | 让取消变得可预测的父子树，为什么你拥有的作用域就是你必须取消的作用域，以及 GlobalScope 实际的代价 |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | 协程上下文与调度器 | 作为用加号组合起来的一组元素的上下文，哪个调度器适合哪类工作，以及会悄悄破坏结构化并发的那一个上下文元素 |
| [0026](lessons/0026-flows.md) | Flow | 作为列表和序列之后第三种异步选择的 flow，“冷”对每个收集者实际上意味着什么，以及 flow 构建器在运行时强制执行的上下文规则 |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | 取消与异常处理 | 为什么取消是协作式的，以及什么会让代码忽略它，为什么 CancellationException 不是失败，以及协程模型与 Java 虚拟线程相比如何 |
| [0028](lessons/0028-test-frameworks.md) | 测试框架 | Kotlin 测试实际所处的各个层次，为什么 runTest 的虚拟时间在调度器边界处止步，以及这对被测代码的设计提出了什么要求 |
| [0029](lessons/0029-mocking.md) | 模拟 | 为什么默认 final 改变了模拟在 Kotlin 中的含义，MockK 为那些不是对象方法的结构做了什么，以及什么时候 final 是在告诉你缺少一个接缝 |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle 与依赖管理 | Kotlin DSL 的类型安全访问器及其不够用的地方，为什么 Gradle 配置不是 Maven 作用域，以及决定哪个版本进入类路径的解析规则 |
| [0031](lessons/0031-structuring-a-service.md) | 组织一个服务 | Kotlin 文件实际该放在哪里、类里面该放什么，以及前面各阶段中决定一个服务是否可测试的四个决策 |
| [0032](lessons/0032-android-divergences.md) | Android 的分歧之处 | Android 代你掌管的作用域，作为被调用方所遵守的契约的主线程安全，以及为什么组合的生命周期不是 lifecycle 的生命周期 |
| [0033](lessons/0033-generics-and-variance.md) | 泛型与型变 | 用声明处型变代替通配符，out 和 in 对类型参数实际做出了什么承诺，以及如何阅读一个带投影的签名 |
| [0034](lessons/0034-java-interop.md) | 与 Java 互操作 | 为什么这条边界是不对称的，平台类型让你付出了什么以及如何偿还，以及你欠 Java 调用方哪些注解 |
| [0035](lessons/0035-reviewing-kotlin.md) | 评审 Kotlin 代码 | 把这条路线变成一件评审工具：每个习惯隐藏的代价，能说出这个代价的评审意见长什么样，以及哪些东西不该评审 |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | 类型安全的构建器与 DSL | 第 15 课讲了让 run 和 apply 能暴露 this 的带接收者的函数类型；类型安全的构建器正是把这同一个机制递归嵌套起来，而 @DslMarker 是唯一一个能防止嵌套构建器悄悄访问到错误接收者的注解 |
| [0037](lessons/0037-value-classes.md) | value class 与 @JvmInline | value class 是对“基本类型偏执”的修正，JVM 通常让你免费获得它，它被表示为自身的底层值，根本没有包装对象，只有在编译器仍然必须装箱的那些具体的、有文档说明的情况下例外 |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | Java 习惯会去找一个在运行时通过反射检查类结构的库；kotlinx.serialization 则通过编译器插件，在编译时生成同样的逻辑，而这正是它能在根本没有运行时反射 API 的 Kotlin 目标上工作的原因 |
| [0039](lessons/0039-result-and-error-handling.md) | Result 与错误处理惯用法 | runCatching 会把任何 Throwable 包进一个 Result，而在协程中这恰恰是个问题，因为第 27 课的协作式取消依赖于 CancellationException 不被捕获地向上传播，而 runCatching 会把它吞成一次普通的失败，除非调用方先显式地重新抛出它 |
| [0040](lessons/0040-http-layer.md) | HTTP 层 | 第 31 课有意把路由留给你所选择的框架；结果 Ktor 自己的 routing 块就是把第 36 课的类型安全构建器 DSL 应用于 HTTP，默认什么都不安装，而请求参数提取会大声失败，而不是悄悄绑定到错误的东西上 |
| [0041](lessons/0041-configuration.md) | 配置 | 服务的实际行为，它的端口、它的数据库 URL、它的密钥，必须能在不同环境之间改变，而不用重新编译任何一行代码，而 Ktor 的配置文件加上一个具体的、容易被忽略的替换惯用法，就能让默认值和环境覆盖只存在于一个地方 |
| [0042](lessons/0042-logging.md) | 日志 | 在把真正的日志后端添加为依赖之前，SLF4J 会悄悄地什么都不做，而在更新日志模式本身来打印它们之前，CallLogging 的每请求 MDC 值也会悄悄地不可见，同一形状的陷阱在同一课中出现了两次 |
| [0043](lessons/0043-persistence.md) | 持久化 | Exposed 的 DSL 是另一个类型安全构建器，而它底层大多是阻塞的，因为它包装的是 JDBC；第 10 阶段的总结练习是正确地调度这些阻塞工作，而不是卡住恰好在处理请求的那个线程，并重新审视第 7 阶段交付的服务一直以来真正需要的是什么 |
| [0044](lessons/0044-testing-coroutines-beyond-runtest.md) | runTest 之外的协程测试 | 第 28 课讲了 Turbine 的 awaitItem，以及在没有东西终止它时引起的挂起；本课讲针对一个永远不会自行终止的 flow 的专用工具，以及在取消是协作式的、调用 cancel() 的那一刻并不会更新一切的前提下，取消测试实际必须断言什么 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [空安全与可变性](reference/null-safety-and-mutability.md)：空安全、`val`/`var`、值与引用、预测可空性和可变性
- [建模](reference/modelling.md)：data class、sealed class 与穷尽的 `when`、对象声明与伴生对象、带默认方法的接口
- [惯用法](reference/idiom.md)：扩展函数、作用域函数（`let`/`run`/`with`/`apply`/`also`）、委托（`by`）、运算符重载
- [集合与序列](reference/collections-and-sequences.md)：Kotlin 的集合操作符、惰性的 `Sequence` 与及早求值的集合、分组与折叠
- [并发](reference/concurrency.md)：挂起函数与协程构建器、结构化并发、协程上下文与调度器、`Flow`、与 Java 虚拟线程的比较
- [测试与构建](reference/testing-and-build.md)：Kotlin 测试框架、模拟、Gradle Kotlin DSL 与依赖管理
- [交付服务](reference/shipping-a-service.md)：组织一个有类型、有测试的后端，Android 专属惯用法，泛型与型变
- [判断力](reference/judgment.md)：与 Java 互操作，评审 Kotlin 并准确说出某个结构的代价

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
