---
title: Rust
description: "掌握 Rust：用所有权来设计，而不是与借用检查器较劲，然后发布 crate"
type: topic
---

# 学习：Rust

成为团队中值得信赖、可以负责 Rust 的工程师：能用所有权来设计，而不是与借用检查器讨价还价；能塑造错误和 API，让类型承载不变量；只在一个说得清理由的边界之后才动用 `unsafe`；并发布一个别人依赖、也能顺利升级的 crate。

**从这里开始：** [0001. 所有权与 Drop](lessons/0001-ownership-and-drop.md)
**最新课程：** [0067. 基于属性的测试与快照测试](lessons/0067-property-based-and-snapshot-testing.md)

## 成功的标准

- 在编译之前，预测编译器会拒绝哪一个借用，以及原因。
- 根据数据实际需要存活多久，在拥有、借用、引用计数和内部可变性之间做出选择。
- 设计调用方能够处理的错误类型，并说出什么时候 panic 反而是正确的选择。
- 用 trait 和泛型消除重复，同时不让签名变得难以阅读，并知道什么时候动态分发是更好的答案。
- 编写不会卡住的异步代码，并解释跨 `await` 点持有锁会造成什么后果。
- 用每个 `unsafe` 块所维护的不变量来为它辩护，把它放在安全接口之后，并用工具而不是靠阅读来检查它。
- 发布一个带有文档、测试，以及一套可以演进而不破坏依赖方的公共 API 的 crate。
- 评审 Rust 代码，并准确指出某个生命周期标注、某次 `clone` 或某个共享互斥锁为什么是在掩盖设计问题。

## 约束

- 不要求事先了解 Rust，也不要求有系统编程背景。栈、堆和内存布局都在学习路线中讲授，因为离开它们就无法讲清所有权。
- 只需要稳定版工具链和任一受支持操作系统上的终端。学习路线中没有任何内容需要付费工具、云账号或 nightly 版 Rust。
- **练习本来就预期会编译失败。** 这是反馈循环，而不是挫折：先预测编译器会说什么，再去验证，把两者的差异当作这一课的内容。
- 练习都是一次就能完成的小程序。把它们分散到多天去做是机制本身，而不是麻烦。
- edition 和版本发布在这里很重要。凡是课程依赖某个 edition 或某项已稳定的特性，都会说明是哪一个；与版本相关的说法会对照发布说明核实，而不是凭记忆。

## 范围之外

- 作为独立主题的嵌入式目标和 `no_std`。
- WebAssembly、图形界面和游戏引擎。
- 作为主题的 Web 框架。异步需要示例，而这些示例只保持在概念允许的最小规模。
- 编写过程宏。声明宏只在需要读懂标准库自身对它们的使用时出现。
- 超出 `unsafe` 边界内容所需的外部函数接口。封装一个真实的 C 库是另一项独立的工作。
- 超出“能预测编译器会接受什么”这一程度的编译器和借用检查器内部机制。

## 学习路线

共八个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 所有权 | 0001 至 0006 | 值、栈与堆、移动、`Copy`、借用及其规则、切片、`String` 与 `&str` 的对比、遮蔽 | 能在编译器报错之前预测移动或借用错误 |
| 2. 数据与控制流 | 0007 至 0013 | 结构体、枚举、`Option` 与 `Result`、模式匹配与穷尽性、迭代器、闭包、值得了解的集合类型 | 用枚举建模，处理缺失值时不依赖 `unwrap` |
| 3. 错误与 API 形态 | 0014 至 0020 | 用 `?` 传播错误、自定义错误类型、`From` 转换、panic 与错误的对比、模块与可见性、编写能编译的文档 | 能写出一个调用方真正能处理其失败的库 |
| 4. trait、泛型与生命周期 | 0021 至 0028 | trait 约束、关联类型、泛型与动态分发的对比、孤儿规则、生命周期标注与省略、为什么生命周期不是一段时长 | 把生命周期错误当作信息而不是障碍来读 |
| 5. 共享与线程 | 0029 至 0036 | `Box`、`Rc` 与 `Arc`、`RefCell` 与 `Mutex`、`Send` 与 `Sync`、线程、通道、死锁与中毒 | 根据数据而不是习惯选择共享策略 |
| 6. 异步 | 0037 至 0045 | future 与执行器、任务与取消、为什么异步中的阻塞调用是 bug、跨 `await` 持有锁、pinning 的用途 | 能写出不会卡住的异步代码，并能说明它会在哪里卡住 |
| 7. unsafe 与性能 | 0046 至 0054 | `unsafe` 实际承诺了什么、未定义行为、封装不变量、用 Miri 检查、基准测试、分配与复制的成本 | 能为 `unsafe` 边界辩护，并用测量来证明性能上的说法 |
| 8. 判断力 | 0055 至 0063 | 发布、公共 API 的语义化版本、API 指南、评审、从标准库和 RFC 中寻找答案 | 可以信赖他做出判断，并向别人解释清楚；第 9 阶段补全了发布流程自身的第一步，即测试套件通过，而编写这个套件的方法在本路线中此前尚未讲授 |
| 9. 测试 | 0064 至 0067 | `#[test]` 与 `cargo test`、单元测试与集成测试的对比、为库组织测试、基于属性的测试与快照测试 | 像标准库本身那样编写和组织测试套件，而不只是文档测试和基准测试 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-ownership-and-drop.md) | 所有权与 Drop | 每个值都恰好有一个所有者，当所有者离开作用域时，编译器会释放它 |
| [0002](lessons/0002-moves-and-copy.md) | 移动与 Copy | 除非类型是 Copy，否则赋值会转移所有权，这就是旧名字不再可用的原因 |
| [0003](lessons/0003-borrowing.md) | 借用 | 要么多个共享借用，要么一个可变借用，二者绝不同时存在，而借用在最后一次使用处结束 |
| [0004](lessons/0004-slices-string-and-str.md) | 切片、String 与 str | 切片是带长度的借用视图，在 API 中接收 &str 不会给调用方带来任何成本 |
| [0005](lessons/0005-bindings-and-mutability.md) | 绑定与可变性 | 默认不可变，mut 针对单个绑定，而遮蔽是一个新的绑定，而不是一次修改 |
| [0006](lessons/0006-reading-a-borrow-error.md) | 读懂借用错误 | 五个错误码覆盖了第 1 阶段的大部分情况，每一个都有一个正当的修复和一个权宜之计 |
| [0007](lessons/0007-structs.md) | 结构体及其方法 | 结构体拥有自己的字段，所以你往里放什么，决定了谁必须让它保持存活 |
| [0008](lessons/0008-enums.md) | 携带数据的枚举 | 枚举表明一个值恰好是这几种形态之一，这是本阶段其余内容所依赖的建模工具 |
| [0009](lessons/0009-option.md) | Option 与缺失值的处理 | 缺失是另一种类型的值，所以编译器会迫使你说明它出现时该怎么办 |
| [0010](lessons/0010-result.md) | Result 与作为值的失败 | 失败是一个返回值而不是一个事件，所以在你读函数体之前，签名就已经说明了可能出什么错 |
| [0011](lessons/0011-pattern-matching.md) | 模式匹配 | match 必须覆盖所有情况，而模式决定了你是借用了这个值还是移动了它 |
| [0012](lessons/0012-iterators-and-closures.md) | 迭代器与闭包 | 迭代器在被消费之前什么也不做，而闭包恰好捕获它所用到的东西 |
| [0013](lessons/0013-collections.md) | 值得了解的集合类型 | Vec 和 HashMap 覆盖了大部分需求，而 entry API 是唯一值得认真学好的东西 |
| [0014](lessons/0014-propagating-errors.md) | 传播错误 | 问号运算符在返回的同时进行转换，所以签名中的错误类型决定了它会接受什么 |
| [0015](lessons/0015-designing-an-error-type.md) | 设计错误类型 | 调用方只能处理你的错误让他们区分得开的情况，所以错误的形态是一个 API 决策 |
| [0016](lessons/0016-conversions-and-boundaries.md) | 转换与边界 | From 实现是一层的失败变成另一层失败的地方，而 derive 会替你写出那些你已经理解了的实现 |
| [0017](lessons/0017-panic-or-error.md) | panic 还是错误 | panic 表示程序坏了，错误表示输入坏了，而库很少有资格判定前一种情况 |
| [0018](lessons/0018-modules-and-visibility.md) | 模块与可见性 | 你公开了什么，就是承诺了要保留什么，所以模块树首先是 API 决策，其次才是组织结构决策 |
| [0019](lessons/0019-documentation-that-compiles.md) | 能编译的文档 | 文档注释中的示例就是测试，所以会腐烂的文档，正是没人运行过的文档 |
| [0020](lessons/0020-a-library-callers-can-handle.md) | 调用方能处理的库 | 拆分 crate，为失败命名，并决定哪些事由二进制程序来做而库绝不能做 |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | 作为共享行为的 trait | trait 如何为多个类型都能提供的行为命名，以及为什么必须先把 trait 引入作用域才能使用它 |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | trait 约束与泛型函数 | 约束向函数体承诺了什么、向调用方要求了什么，以及编译器用它做了什么 |
| [0023](lessons/0023-associated-types.md) | 关联类型 | 为什么 Iterator 把它的 Item 定义为关联类型而不是参数，以及这为每个实现者决定了什么 |
| [0024](lessons/0024-generics-or-dyn-trait.md) | 泛型还是 dyn Trait | 两种分发策略、各自的代价，以及真正决定二者取舍的那个问题 |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | 为不属于你的 trait 提供实现 | 一致性、newtype 模式，以及为什么 blanket 实现是一项承诺而不是一种便利 |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | 生命周期不是时长 | 生命周期参数说明了借用之间的什么关系，以及省略规则一直以来在替你做什么 |
| [0027](lessons/0027-types-that-borrow.md) | 带借用的类型 | 给结构体加上生命周期参数，并判断这个类型是否应该改为拥有它的数据 |
| [0028](lessons/0028-reading-a-lifetime-error.md) | 读懂生命周期错误 | 生命周期错误的几种形态，每一种都有正当的修复，以及它诱惑你采用的权宜之计 |
| [0029](lessons/0029-threads-joining-and-panics.md) | 线程、join 与 panic | 创建线程对你交给它的数据实际提出了什么要求，以及单独 panic 的线程会怎样 |
| [0030](lessons/0030-scoped-threads.md) | 作用域线程 | 为什么不能比其作用域活得更久的线程可以借用，以及为什么这应该是首选而不是最后的手段 |
| [0031](lessons/0031-shared-ownership.md) | 用 Rc 和 Arc 实现共享所有权 | 一个值什么时候需要多个所有者而不是一个，计数的代价是什么，以及循环引用如何造成泄漏 |
| [0032](lessons/0032-interior-mutability.md) | 内部可变性 | 把借用规则从编译期移到运行期，这带来了什么，以及用错时要付出什么代价 |
| [0033](lessons/0033-mutex-rwlock-and-poisoning.md) | Mutex、RwLock 与中毒 | 锁实际保护的是什么，为什么守卫的作用域才是设计决策，以及持有锁时 panic 会留下什么 |
| [0034](lessons/0034-send-and-sync.md) | Send 与 Sync | 两个没人手写的 trait，它们决定了什么可以跨越线程边界，以及如何读懂它们引发的错误 |
| [0035](lessons/0035-channels.md) | 通道 | 在线程之间发送值而不是共享值，以及当另一端消失时通道的两端会怎样 |
| [0036](lessons/0036-choosing-a-sharing-strategy.md) | 选择共享策略 | 凭习惯选择所导致的失败，以及能根据数据选出策略的那些问题 |
| [0037](lessons/0037-what-a-future-is.md) | future 是什么 | 一个只有一个方法、由轮询它的一方驱动的状态机，以及这对看起来是顺序执行的代码意味着什么 |
| [0038](lessons/0038-wakers-executors-and-runtimes.md) | waker、执行器与运行时 | future 如何表明自己可以再次被轮询，以及运行时除了轮询之外还做什么 |
| [0039](lessons/0039-tasks-and-the-send-bound.md) | 任务与 Send 约束 | 创建异步任务对你交给它的 future 提出了什么要求，以及为什么异步 trait 方法满足不了它 |
| [0040](lessons/0040-blocking-is-a-bug.md) | 阻塞就是 bug | 为什么异步任务中的一次阻塞调用会卡住与它毫不相干的工作，以及对无法避免的调用该怎么办 |
| [0041](lessons/0041-shared-state-across-an-await.md) | 跨 await 的共享状态 | 为什么跨 await 点持有的锁守卫会被拒绝，以及如何在两种互斥锁之间做出选择 |
| [0042](lessons/0042-cancellation.md) | 取消 | 停止一个 future 就是丢弃它，这就是为什么不会有任何通知，工作只是停在了原处 |
| [0043](lessons/0043-cancellation-safety.md) | 取消安全 | future 能否在执行中途被丢弃而不丢失它已经拿到的东西，以及这个问题在哪里得到回答 |
| [0044](lessons/0044-pinning.md) | Pinning | 为什么 future 的内存一旦被轮询就不能再移动，以及 Pin 对此做了什么 |
| [0045](lessons/0045-reading-an-async-failure.md) | 读懂异步失败 | 异步代码在没有错误信息的情况下失败的五种方式，以及如何分辨你看到的是哪一种 |
| [0046](lessons/0046-what-unsafe-promises.md) | unsafe 承诺了什么 | unsafe 块允许你做的五件事，以及写下它时你所承担的义务 |
| [0047](lessons/0047-raw-pointers.md) | 裸指针 | 裸指针不是什么，它让你在保证上付出什么代价，以及如何造出一个真正有效的裸指针 |
| [0048](lessons/0048-undefined-behaviour.md) | 未定义行为 | 编译器被允许假定什么，为什么能运行的程序仍然可能是错的，以及值得牢记的那份清单 |
| [0049](lessons/0049-checking-with-miri.md) | 用 Miri 检查 | 把看不见的健全性 bug 变成报告的工具，它能抓到什么，又抓不到什么 |
| [0050](lessons/0050-encapsulating-an-invariant.md) | 封装不变量 | 把 unsafe 代码包装在安全接口中，以及这个接口要名副其实必须满足什么条件 |
| [0051](lessons/0051-memory-orderings.md) | 内存顺序 | 内存顺序实际约束的是什么，为什么无法靠运行来测试它，以及如何检查你选定的那一种 |
| [0052](lessons/0052-measuring-before-optimising.md) | 先测量再优化 | 如何得到一个站得住脚的数字，编译器会对什么也没测到的基准测试做什么，以及测量无法告诉你什么 |
| [0053](lessons/0053-allocation-and-copying-costs.md) | 分配与复制的成本 | Rust 程序实际把时间花在了哪里，以及哪些显而易见的修复确实物有所值 |
| [0054](lessons/0054-defending-an-unsafe-boundary.md) | 为 unsafe 边界辩护 | 在 unsafe 块发布之前你必须能够给出的论证，以及必须随之提供的测量 |
| [0055](lessons/0055-variance.md) | 型变 | 哪些生命周期可以替代哪些，为什么由你自己的类型决定，以及这让你承诺了什么 |
| [0056](lessons/0056-higher-ranked-bounds.md) | 高阶约束 | 写出编译器一直打印给你看的那个量词，以及需要它的 API 形态 |
| [0057](lessons/0057-what-breaks-a-caller.md) | 什么会破坏调用方 | 需要升主版本号的改动、只是看起来安全的改动，以及告诉你哪个是哪个的工具 |
| [0058](lessons/0058-designing-for-change.md) | 为变化而设计 | 为你日后留出调整空间的决策，以及悄悄承诺了超出你本意的决策 |
| [0059](lessons/0059-features-and-the-minimum-version.md) | feature 与最低版本 | 为什么 feature 只能做加法，特性统一对你的假设做了什么，以及声明最低版本实际承诺了什么 |
| [0060](lessons/0060-workspaces-and-release.md) | 工作区与发布 | 把 crate 推进到发布只需一条命令的程度，以及这条命令实际做了什么 |
| [0061](lessons/0061-the-api-guidelines.md) | API 指南 | 生态已经达成共识的检查清单，其中哪些条目最重要，以及如何使用它而不盲目照搬 |
| [0062](lessons/0062-reading-the-source-and-the-rfcs.md) | 阅读源码与 RFC | 从标准库、跟踪 issue 和 RFC 中回答文档没有回答的问题 |
| [0063](lessons/0063-reviewing-rust.md) | 评审 Rust 代码 | 在别人的 Rust 代码中该看什么、按什么顺序看，以及哪些评论值得提出 |
| [0064](lessons/0064-the-test-attribute-and-cargo-test.md) | test 属性与 cargo test | 文档测试位于文档注释中，运行的是一个示例；#[test] 函数位于 crate 自身的源码中，是几乎所有 Rust 测试实际采用的普通形态，而 cargo test 用同一条命令运行二者，但它们并不是同一种机制 |
| [0065](lessons/0065-unit-versus-integration-tests.md) | 单元测试与集成测试 | #[test] 函数放在哪里，决定了它能看到什么：与代码放在同一个文件的 #[cfg(test)] 之下，可以访问每一个私有项；或者放在单独的 tests/ 目录中，只能看到你真正公开了的东西 |
| [0066](lessons/0066-organising-tests-for-a-library.md) | 为库组织测试 | 集成测试套件的形态由你已经设为 pub 的内容决定，共享的准备代码要专门放在 tests/common/mod.rs 中，而没有 lib.rs 的二进制程序根本无法做集成测试 |
| [0067](lessons/0067-property-based-and-snapshot-testing.md) | 基于属性的测试与快照测试 | 这是第 9 阶段的收尾课：proptest 生成成百上千个输入，并把失败收缩到仍能破坏该属性的最小输入，而快照测试则把某个选定输入的输出与一份已经由人审核过的基线进行比较 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [所有权与借用](reference/ownership-and-borrowing.md)：规则、Copy 类型清单、错误码，以及每一个错误的正当修复
- [项目](reference/the-project.md)：练习在整条学习路线中构建的 crate，以及它在每个阶段结束时应处于的状态
- [数据与控制流](reference/data-and-control.md)：第 2 阶段的速查表，包括枚举、Option 和 Result 的决策、模式规则以及集合类型
- [错误与 API 形态](reference/errors-and-api-shape.md)：第 3 阶段的速查表，包括错误类型的决策、转换规则，以及公共 API 所承诺的内容
- [trait 与生命周期](reference/traits-and-lifetimes.md)：第 4 阶段的速查表，包括分发方式的决策、一致性规则以及生命周期错误表
- [共享与线程](reference/sharing-and-threads.md)：第 5 阶段的速查表，包括选择策略的流程、每种共享类型的代价以及失败表
- [异步](reference/async.md)：第 6 阶段的速查表，包括轮询模型、各项约束、失败表，以及取消安全在何处有文档说明
- [unsafe 与性能](reference/unsafe-and-performance.md)：第 7 阶段的速查表，包括未定义行为表、每种工具能抓到什么，以及测量的纪律
- [判断力](reference/judgment.md)：第 8 阶段的速查表，包括型变规则、破坏性改动表、发布检查清单以及权威来源的优先顺序

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
