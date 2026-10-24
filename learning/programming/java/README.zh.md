---
title: Java
description: "掌控一个 Java 服务：用现代 Java 为它建模，再运维 JVM 对它所做的一切"
type: topic
---

# 学习：Java

成为团队中值得信任、能掌控一个 Java 服务的工程师：能用现代 Java 为领域建模，而不是用这门语言过去所要求的继承层次，能从内存模型出发而不是靠实验来推理并发，能读懂性能剖析结果和垃圾回收日志并据此做出决定，并能评审别人的 Java 代码，具体说出某个抽象正在让他们付出什么代价。

**从这里开始：** [0001. 引用就是值](lessons/0001-references-are-values.md)
**最新课程：** [0052. 反射与注解](lessons/0052-reflection-and-annotations.md)

## 成功的标准

- 在运行代码之前，预测引用相等、错误的 `hashCode` 以及共享的可变字段会做出什么。
- 用 record、sealed 接口和枚举为领域建模，并说出为什么继承层次会更糟。
- 用 Java 内存模型的词汇，说出 `synchronized`、`volatile` 和并发集合各自保证了什么。
- 在虚拟线程能带来收益的地方使用它，并说出仍然会阻塞载体线程的东西。
- 读懂垃圾回收日志和性能剖析结果，然后依据这些证据而不是默认值来确定堆的大小。
- 交付一个别人能运行的构建：声明好的依赖、一套测试、一个可运行的制品。
- 评审一个拉取请求，准确说出为什么在那里类层次、受检异常或者 stream 链是错误的工具。
- 依据语言规范和引入该特性的 JEP 来裁定一场关于语言的争论。

## 约束

- 不要求有 Java 基础。另一门语言的经验能缩短前面的阶段，但并非必需，而且它会带来 Java 悄悄惩罚的习惯：给每个字段都写 getter，只有一个实现的接口，用 record 能表达得更好的地方用了 class。
- 基线是当前的长期支持版本。每个语言特性都会注明它是在哪个版本引入的，因为 Java 代码会在许多版本之间被阅读，而“现代 Java”也会过时。
- 只需要一个 JDK 和任意受支持操作系统上的终端。IDE 有帮助但从不是必需的，路线中也没有任何内容需要付费工具或云账号。
- 大多数练习都是一次就能完成的小程序。第 6 阶段是例外：做性能剖析需要一个运行时间足够长、值得剖析的程序。
- 对版本敏感的说法，依据语言规范、API 文档和 JEP 索引来核对，而不是依据某本书，因为每六个月一次的发布节奏超过了所列出的每一本书。

## 范围之外

- 把框架本身作为学习对象：Spring、Jakarta EE、Quarkus、Hibernate。判断一个框架是否值得引入是一项评审技能，属于第 7 阶段。
- 其他 JVM 语言：Kotlin、Scala、Clojure、Groovy。
- Android，以及一般的移动端目标。
- 构建工具之间的比较。路线讲授构建必须完成的任务，并用一个工具来完成它们，而不去争论该用哪个。
- 超出预测程序行为所需深度的 JVM 内部机制：JIT 的实现、字节码工程、编写垃圾回收器。
- 超出单个服务运行所需的 Kubernetes 和基础设施。把可运行的制品放进容器镜像，以及运行、加固和调试这个容器，见 [`infrastructure/containers`](../../infrastructure/containers/)。在集群上运行它，见 [`infrastructure/kubernetes`](../../infrastructure/kubernetes/)。

## 学习路线

共七个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 基础 | 0001 至 0006 | 基本类型与引用、`null`、字符串及其常量池、数组、集合框架、`equals` 与 `hashCode`、`Comparable` | 不运行代码就能预测同一性与相等性，以及别名问题 |
| 2. 建模 | 0007 至 0014 | 类与接口、record、sealed 类型、枚举、泛型与类型擦除、模式匹配、以不可变为默认 | 为领域建模时不会首先想到继承 |
| 3. 惯用法与标准库 | 0015 至 0021 | 异常以及如何处理受检异常、`Optional`、stream 与收集器、迭代、文件与 IO、时间 API、文本块 | 写出的 Java 不会被评审者说成不地道 |
| 4. 并发 | 0022 至 0028 | 线程、内存模型、`synchronized` 与 `volatile`、`java.util.concurrent`、执行器、虚拟线程、结构化并发、常见陷阱 | 能说出一个出错的并发程序违反了哪项保证 |
| 5. 测试与构建 | 0029 至 0035 | JUnit 6、参数化测试、测试替身以及何时不该用它、依赖声明、可复现的可运行制品 | 别人能克隆、构建、测试并运行它 |
| 6. 运行时 | 0036 至 0042 | 内存区域、对象布局与逃逸分析、垃圾回收器及其权衡、阅读 GC 日志、JMH、性能剖析、减少分配 | 依据剖析结果做优化，并用可信的基准测试证明收益 |
| 7. 判断力 | 0043 至 0049 | API 设计与向后兼容、弃用、代码评审、从语言规范和 JEP 中寻找答案 | 可以信赖他做出判断，并向别人解释清楚；第 8 阶段补上其机制，即每个被评判的框架实际所依赖的反射与注解 |
| 8. 模块与反射 | 0050 至 0052 | 模块系统、`module-info.java`、`requires` 与 `exports`、强封装、`jlink` 与 `jpackage` 运行时镜像、反射与注解 | 有意识地声明模块边界，交付基于它构建的运行时镜像，并在判断一个框架是否值得引入之前，看清它的反射实际触及了什么 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | 引用就是值 | 变量保存的是一个基本类型值或一个引用，每次赋值和传参复制的都是它 |
| [0002](lessons/0002-identity-and-equality.md) | 同一性与相等性 | == 比较的是引用，所以对字符串和装箱数字来说，它回答的是另一个问题 |
| [0003](lessons/0003-equals-and-hashcode.md) | equals 与 hashCode 契约 | 破坏这个契约，哈希集合就会弄丢你的对象，而且不报任何错 |
| [0004](lessons/0004-null.md) | null 及其来源 | null 是一个什么都不指向的引用，解决办法是在边界上拒绝它 |
| [0005](lessons/0005-arrays-and-collections.md) | 数组与集合 | 数组是协变且长度固定的，而三个列表工厂方法之间的差异被它们的名字掩盖了 |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable 与 Comparator | 有序集合依据排序而不是 equals，所以不一致的比较器会丢失数据 |
| [0007](lessons/0007-classes-and-objects.md) | 类与对象 | 类是状态和行为的模板，每个字段都从一个你没有写下的默认值开始 |
| [0008](lessons/0008-records.md) | record | 不可变数据的透明载体，其构造器、访问器、equals、hashCode 和 toString 都由头部推导而来 |
| [0009](lessons/0009-interfaces.md) | 接口 | 没有状态的契约，以及让接口得以扩展而不破坏每个实现者的默认方法 |
| [0010](lessons/0010-inheritance-and-composition.md) | 继承与组合 | extends 实际给了你什么，以及为什么答案通常是一个字段而不是一个超类 |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | sealed 类型与模式匹配 | 一组封闭的备选项，以及一个检查你是否处理了所有备选项的编译器 |
| [0012](lessons/0012-enums.md) | 枚举 | 由语言保证的一组固定实例，每个实例都可以有自己的状态和行为 |
| [0013](lessons/0013-generics-and-erasure.md) | 泛型与类型擦除 | 编译器检查、运行时遗忘的类型参数，以及让它们变得可用的通配符 |
| [0014](lessons/0014-immutability-as-a-default.md) | 以不可变为默认 | 让对象无法被改变，大多数难题就不再会被提出 |
| [0015](lessons/0015-exceptions.md) | 异常 | 哪些失败属于方法签名，哪些属于堆栈跟踪，以及在两种情况下都能执行的清理 |
| [0016](lessons/0016-optional.md) | Optional | 一种让“缺失”成为契约一部分的返回类型，以及它不该出现的四个地方 |
| [0017](lessons/0017-streams.md) | stream | 一条描述工作的流水线，在被要求之前什么都不做，而且只能被要求一次 |
| [0018](lessons/0018-collectors.md) | 收集器 | 把流水线变回一个容器，以及在你意想不到的地方抛出异常的三个收集器 |
| [0019](lessons/0019-files-and-paths.md) | 文件与路径 | 不是字符串的路径，必须关闭的流，以及终于成为一个值得拥有的默认值的字符集 |
| [0020](lessons/0020-dates-and-times.md) | 日期与时间 | 六种时间类型中你真正指的是哪一种，以及其中不表示时间点的那三种 |
| [0021](lessons/0021-strings-and-text.md) | 字符串与文本 | 文本块，应该使用的格式化方式，以及为什么长度不等于字符数 |
| [0022](lessons/0022-threads.md) | 线程 | 线程是一个被调度的调用栈，而这个阶段的几乎每个错误，都始于把它当作是免费的 |
| [0023](lessons/0023-the-memory-model.md) | 内存模型 | 为什么一个线程写入的值可能永远不会被另一个线程看到，以及解决它的那条确切规则 |
| [0024](lessons/0024-mutual-exclusion.md) | 互斥 | 一次只允许一个线程，表达它的两种方式，以及能在发生之前就找出来的死锁 |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | 并发集合与原子类 | 能承受并发访问的集合，以及让它们每一个都失效的“先检查后执行” |
| [0026](lessons/0026-executors-and-futures.md) | 执行器与 Future | 提交工作而不是创建线程，并找出被 submit 吞掉的异常 |
| [0027](lessons/0027-virtual-threads.md) | 虚拟线程 | 廉价到可以阻塞的线程，以及你现在必须改掉的池化习惯 |
| [0028](lessons/0028-choosing-a-model.md) | 选择并发模型 | 一个问题就能选定模型，而你眼前的失败会说出它破坏了哪项保证 |
| [0029](lessons/0029-your-first-test.md) | 你的第一个测试 | 测试放在哪里，运行器实际做了什么，以及每篇文章都会写错的版本号规则 |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | 能说出失败原因的断言 | 失败的测试就是一份缺陷报告，而你选择的断言决定了这份报告有多好 |
| [0031](lessons/0031-parameterised-tests.md) | 参数化测试 | 一个测试方法、许多用例，以及测试内部的循环在哪里开始变得不够用 |
| [0032](lessons/0032-test-doubles.md) | 测试替身 | 五种替身，真实对象何时胜过它们全部，以及 mock 悄悄地不再测试的东西 |
| [0033](lessons/0033-declaring-dependencies.md) | 声明依赖 | 坐标、作用域和传递依赖图，以及没人要求却自己出现的那个版本 |
| [0034](lessons/0034-the-build-lifecycle.md) | 构建生命周期 | 用阶段和目标代替死记硬背的命令，以及让构建在任何地方都一样的包装器 |
| [0035](lessons/0035-a-runnable-artifact.md) | 可运行的制品 | 把你构建的东西打包，让只有 JDK 的人也能运行它 |
| [0036](lessons/0036-where-memory-goes.md) | 内存去了哪里 | JVM 存放内存的五个地方，以及哪种 OutOfMemoryError 对应哪一个 |
| [0037](lessons/0037-the-shape-of-an-object.md) | 对象的形状 | 一个小对象大部分是对象头，而能缩小它的那个选项默认是关闭的 |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | 从未发生的分配 | 逃逸分析可以完全删除一次分配，而一次字段存储就会把它带回来 |
| [0039](lessons/0039-collectors-and-the-trade.md) | 垃圾回收器与你正在做的权衡 | 五种回收器、一个三方权衡，以及为什么默认选项通常就是正确答案 |
| [0040](lessons/0040-reading-a-gc-log.md) | 阅读垃圾回收日志 | 一行日志说明了回收了多少、花了多长时间，以及是否需要在意 |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | 可信的基准测试 | 为什么显而易见的计时循环会说谎，以及悄悄地什么都没测到的测试框架配置 |
| [0042](lessons/0042-from-profile-to-proof.md) | 从剖析到证明 | 记录运行过程，看清时间花在了哪里，只改动一处，然后证明收益 |
| [0043](lessons/0043-what-counts-as-breaking.md) | 什么算破坏性改动 | 三种兼容性，以及对编译来说安全、对运行来说致命的那种改动 |
| [0044](lessons/0044-designing-a-signature.md) | 设计方法签名 | 参数类型和返回类型决定了调用方能做什么，而大部分损害都发生在边界上 |
| [0045](lessons/0045-evolving-a-type.md) | 在不破坏的前提下演进类型 | 在别人已经依赖之后，如何给接口、record、枚举和 sealed 层次添加内容 |
| [0046](lessons/0046-deprecation-that-works.md) | 真正起作用的弃用 | 把某样东西标记为弃用不会改变任何事，除非你说明接下来会发生什么 |
| [0047](lessons/0047-settling-it-from-the-source.md) | 依据一手资料裁定 | 当争论的是 Java 到底做了什么时该去哪里查，以及哪份文档回答哪个问题 |
| [0048](lessons/0048-reviewing-java.md) | 评审 Java 代码 | 说出一个抽象的代价，而不是说它感觉不对 |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | 这个框架值得引入吗 | 第 7 阶段的最后一个判断，依据服务的约束而不是框架的承诺做出 |
| [0050](lessons/0050-the-module-system.md) | 模块系统 | module-info.java 取代 JAR，成为编译器和运行时都认可的边界，requires 和 exports 决定什么能跨越它，而强封装意味着未导出包中的 public 类在其所属模块之外是不可见的 |
| [0051](lessons/0051-runtime-images.md) | 运行时镜像 | jlink 只用它被告知的起始模块的传递闭包来组装运行时镜像，但只能用显式模块，一个应用哪怕只依赖一个自动模块，也完全无法被链接 |
| [0052](lessons/0052-reflection-and-annotations.md) | 反射与注解 | 这是第 8 阶段的总结练习，反射在运行时而不是编译时读取并调用类自身的结构，注解在被反射读取之前只是惰性的数据，而本路线中每个范围之外的框架，都恰恰是由这两种机制构建的 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [相等性、哈希与排序](reference/equality-hashing-and-ordering.md)：三个契约，以及该写哪种比较
- [建模](reference/modelling.md)：该选用哪种结构，每种结构让你承诺了什么，以及容易记错的规则
- [惯用法与标准库](reference/idiom-and-library.md)：评审者会注意到的标准库选择，以及在没人注意的地方抛出异常的陷阱
- [并发](reference/concurrency.md)：每种结构提供哪项保证，哪种模型适合当前工作负载，以及你眼前的症状意味着什么
- [测试与构建](reference/testing-and-build.md)：每条命令实际执行的构建任务，该选用哪种替身，以及意味着制品有问题的那种失败
- [运行时](reference/the-runtime.md)：内存去了哪里，哪种回收器满足哪种需求，以及能支撑一个结论的度量
- [判断力](reference/judgment.md)：哪些改动会破坏什么，如何让一个 API 退役，以及如何依据一手资料论证判断
- [模块系统](reference/the-module-system.md)：第 8 阶段的速查表，包括跨模块访问的三个条件、每条指令的作用，以及一个 jar 的代码最终落在哪里

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
