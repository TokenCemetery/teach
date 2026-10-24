---
title: TypeScript
description: "掌握 TypeScript 代码库：让编译器拒绝那些本不该存在的状态"
type: topic
---

# 学习：TypeScript

成为团队中值得信赖、可以负责 TypeScript 代码库的工程师：能为领域建模，让编译器拒绝那些本不该存在的状态；让类型断言远离承担关键职责的代码；验证跨越运行时边界的数据，而不是假定类型依然成立；并能评审别人的类型，具体说出某个巧妙的泛型为什么代价大于收益。

**从这里开始：** [0001. 值与强制类型转换](lessons/0001-values-and-coercion.md)
**最新课程：** [0049. 值得信赖去做决定](lessons/0049-trusted-to-make-the-call.md)，它为整条学习路线收尾

## 成功的标准

- 在运行代码之前、不借助类型系统，预测 JavaScript 在强制类型转换、闭包、`this` 和事件循环上会做什么。
- 把一组非法状态变成编译器会拒绝的类型，并用 `never` 证明穷尽性。
- 把泛型的错误信息一路读到它的根因，而不是伸手去用 `as`。
- 准确说出哪些东西会保留到编译之后、哪些会被擦除，并验证从程序外部进入的每一个值。
- 有意图地配置编译器：说出每个严格性标志带来了什么，以及模块和 target 设置为什么是现在这样。
- 编写类型推断能够生效的泛型函数，让调用方什么都不用标注。
- 发布一个类型对使用者可用的包，包括声明文件的输出及其所宣告的导出。
- 评审一个拉取请求，并准确说出为什么在那里条件类型、断言或 `enum` 是错误的工具。

## 约束

- 不要求事先了解 TypeScript，所需的 JavaScript 知识也不超出本学习路线所讲的内容。TypeScript 是建立在 JavaScript 之上的类型系统，所以凡是 JavaScript 语义能解释类型解释不了的行为之处，都会讲授它。
- 编译期与运行时的边界自始至终被当作一条硬性界线，因为几乎每一个严重的 TypeScript 错误，都是一个只有编译器检查过的、关于运行时的断言。
- 只需要一个 JavaScript 运行时和任一受支持操作系统上的终端；当练习只需要看一个类型时，在线 playground 可以同时代替二者。不需要付费工具、云账号或框架。
- 练习都是一次就能完成的小程序和小型类型实验。
- TypeScript 每隔几个月发布一次新版本，类型系统在这些版本中获得了实实在在的表达能力。与版本相关的说法会对照发布说明核实，任何依赖某个版本的课程都会说明是哪一个。

## 范围之外

- 作为独立主题的框架和 UI 库：React、Angular、Vue、Svelte、Next.js。
- 作为主题的打包工具和 monorepo 工具：webpack、Vite、esbuild、Turborepo。模块解析依据编译器自身的模型来讲，而这正是那些工具必须与之保持一致的模型。
- 作为主题的其他运行时：Deno、Bun、浏览器平台。它们只在行为确实不同的地方出现。
- 作为独立平台的 Node.js：流、集群、原生扩展。
- 作为竞技运动的类型层面编程。映射类型和条件类型只讲到能为调用方服务的程度，第 6 阶段会明确说明这个程度在哪里。

## 学习路线

共七个阶段，从零基础到资深。这不是课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 底层的 JavaScript | 0001 至 0007 | 值与强制类型转换、对象与原型、闭包、`this`、模块、事件循环、promise 与 async | 在不涉及任何类型的情况下，能预测程序在运行时会做什么 |
| 2. 值之上的类型 | 0008 至 0014 | 原始类型、数组与元组、联合类型、字面量类型、结构化可赋值性、类型收窄、函数类型、`readonly`、类型推断已经知道什么 | 只在类型推断够不到的地方添加标注 |
| 3. 严格性与编译器 | 0015 至 0021 | 逐个讲解 `strict` 系列标志、`strict` 仍然遗漏的那些同类严格标志、`unknown` 与 `any` 的对比、断言与声明的对比、`tsconfig`、模块解析、`target` 与 `lib` | 保持严格模式开启，修复它报告的问题而不是压制它们，并打开 `strict` 遗漏的那些检查 |
| 4. 建模 | 0022 至 0028 | 可辨识联合、用 `never` 实现穷尽性检查、品牌类型、泛型与约束、`satisfies`、interface 与类型别名的对比 | 非法状态无法被表示，而证明这一点的正是编译器 |
| 5. 运行时边界 | 0029 至 0035 | 哪些会被擦除、声明文件、在边缘验证输入、作为值的错误、使用没有类型或类型错误的依赖 | 没有任何值未经验证就进入程序，也没有任何断言在承担关键职责 |
| 6. 类型层面的工具 | 0036 至 0042 | 映射类型与条件类型、`infer`、模板字面量类型、型变与可赋值性、库 API 的类型推断、编译器性能 | 写出类型为调用方服务的 API，并在过度炫技之前停下 |
| 7. 判断力 | 0043 至 0049 | 发布公共类型接口、什么算作类型上的破坏性改动、评审、阅读发布说明和编译器自带的声明 | 可以信赖他做出判断，并向别人解释清楚 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-values-and-coercion.md) | 值与强制类型转换 | 七种原始类型、两种空值，以及一个在比较之前先做转换的相等运算符 |
| [0002](lessons/0002-objects-are-references.md) | 对象是引用 | const 阻止的是重新绑定，展开运算只复制一层，而 readonly 在运行时会消失 |
| [0003](lessons/0003-prototypes-and-classes.md) | 原型与类 | 属性查找沿着一条链进行，而 class 语法是构建这条链的一种方式 |
| [0004](lessons/0004-this-and-the-call-site.md) | this 由调用方式决定 | this 来自函数被调用的方式，所以把方法单独取出来就会丢掉它 |
| [0005](lessons/0005-scope-and-closures.md) | 作用域与闭包 | 闭包捕获的是绑定而不是值，而 let 会在每次迭代中创建一个新绑定 |
| [0006](lessons/0006-event-loop-and-promises.md) | 事件循环、promise 与 await | 微任务会在下一个定时器之前清空，而连续的两个 await 是顺序执行的 |
| [0007](lessons/0007-modules.md) | 模块 | import 会被提升并以活绑定的方式连接，而没有任何 import 或 export 的文件不是模块 |
| [0008](lessons/0008-the-types-you-write.md) | 你写下的类型 | 类型标注的词汇，以及一个在你配置它之前就已经会提出异议的编译器 |
| [0009](lessons/0009-tuples-and-readonly.md) | 元组与 readonly | 编译器在读取时强制执行、在 push 时却忘掉的固定长度 |
| [0010](lessons/0010-unions-and-literal-types.md) | 联合类型与字面量类型 | 一个可能有不止一种类型的值，以及把其中有意义的那一种丢掉的类型拓宽 |
| [0011](lessons/0011-structural-assignability.md) | 结构化可赋值性 | 形状决定了什么能放到哪里，只有一项检查例外，它只在新鲜的对象字面量上触发 |
| [0012](lessons/0012-narrowing.md) | 类型收窄 | 控制流告诉编译器联合类型已经变成了什么，而恰好有两种情况会让这一结论失效 |
| [0013](lessons/0013-function-types.md) | 函数类型 | 参数会按你预期的方向接受检查，除非你写的是一个方法 |
| [0014](lessons/0014-what-inference-already-knows.md) | 类型推断已经知道什么 | 类型推断能够到达哪里，这样当你写下标注时，它才有意义 |
| [0015](lessons/0015-what-strict-turns-on.md) | strict 打开了什么 | 一个标志背后的七项检查，每一项都有它专门要捕捉的失败 |
| [0016](lessons/0016-the-checks-strict-leaves-out.md) | strict 遗漏的检查 | 另外六项值得启用的检查、一项编译器拒绝启用的检查，以及一项完全不起作用的检查 |
| [0017](lessons/0017-unknown-instead-of-any.md) | 用 unknown 代替 any | 一种类型接受一切却什么也不让你做，另一种接受一切却什么也不检查 |
| [0018](lessons/0018-an-assertion-is-not-a-check.md) | 断言不是检查 | 让编译器停止检查的每一种方式，以及当断言出错时每一种的代价 |
| [0019](lessons/0019-reading-a-tsconfig.md) | 读懂 tsconfig | 编译器会查看哪些文件、设置从哪里来，以及生成的文件为什么写的是那些内容 |
| [0020](lessons/0020-target-and-lib.md) | target 与 lib | 一个设置改变输出什么，另一个改变存在什么，而一旦指定后者，默认值就被丢弃了 |
| [0021](lessons/0021-module-resolution.md) | 模块解析 | 同样的编译器选项会因 package.json 中的一个字段而给出截然相反的结论 |
| [0022](lessons/0022-discriminated-unions.md) | 可辨识联合 | 一个共享的字面量属性，以及一个编译器能够拆解开的联合类型 |
| [0023](lessons/0023-exhaustiveness-with-never.md) | 用 never 实现穷尽性检查 | 给联合类型新增一个成员，应当让每一个忽略了它的 switch 报错，而一行代码就能做到 |
| [0024](lessons/0024-illegal-states.md) | 让非法状态无法被表示 | 数一数你的类型允许多少种状态，然后去掉你的领域中并不存在的那些 |
| [0025](lessons/0025-branded-types.md) | 品牌类型 | 在结构化类型系统之上实现名义类型，以及它所需要付出的唯一一次断言 |
| [0026](lessons/0026-generics-and-constraints.md) | 泛型与约束 | 类型参数是对调用方的一项承诺，而约束是让你能够兑现它的东西 |
| [0027](lessons/0027-satisfies.md) | satisfies | 用一个类型检查某个值，同时不让这个类型取代你写下的内容 |
| [0028](lessons/0028-interface-or-type.md) | interface 还是 type | 一个在你写下冲突成员的地方报告它，另一个则在别处报告 |
| [0029](lessons/0029-nothing-survives-to-run-time.md) | 没有什么能保留到运行时 | 每一个类型都是关于某个程序的断言，而当这个断言真正要紧时，那个程序已经不存在了 |
| [0030](lessons/0030-unknown-at-the-edge.md) | 边缘处的 unknown | 找出每一个值从外部进入的地方，并给每一处唯一诚实的类型 |
| [0031](lessons/0031-parsing-instead-of-asserting.md) | 用解析代替断言 | 一份声明，同时产出运行时检查和静态类型 |
| [0032](lessons/0032-type-predicates-and-assertion-functions.md) | 类型谓词与断言函数 | 一个承诺会做检查的签名，以及一个没有任何东西去核对它的函数体 |
| [0033](lessons/0033-errors-as-values.md) | 作为值的错误 | 出现在返回类型中的失败，是编译器能够强制你去处理的失败 |
| [0034](lessons/0034-declaration-files.md) | 声明文件 | 为编译器从未见过的代码提供类型，以及这项承诺值多少 |
| [0035](lessons/0035-when-the-declaration-lies.md) | 当声明撒谎时 | 编译器相信声明，而运行时对它一无所知 |
| [0036](lessons/0036-mapped-types.md) | 映射类型 | 一次性转换一个类型的所有属性，并去掉你不想要的那些 |
| [0037](lessons/0037-conditional-types.md) | 条件类型 | 一个会分支的类型，以及它事先悄悄拆开的联合类型 |
| [0038](lessons/0038-infer.md) | infer | 从某个位置中提取出一个类型，而不是要求调用方说出它的名字 |
| [0039](lessons/0039-template-literal-types.md) | 模板字面量类型 | 编译器会检查的字符串模式，以及它能构造出的键名 |
| [0040](lessons/0040-variance-and-assignability.md) | 型变与可赋值性 | 一个类型可以朝哪个方向传递，以及故意把它弄错的数组 |
| [0041](lessons/0041-inference-for-library-apis.md) | 库 API 的类型推断 | 设计签名，让调用方什么都不用标注 |
| [0042](lessons/0042-knowing-when-to-stop.md) | 知道何时停下 | 衡量一个巧妙的类型的代价，然后向维护它的人证明它值得 |
| [0043](lessons/0043-what-counts-as-a-breaking-change.md) | 什么算作破坏性改动 | 对已发布类型的哪些修改会破坏使用者，以及每一种修改必须朝哪个方向进行 |
| [0044](lessons/0044-publishing-a-type-surface.md) | 发布类型接口 | 使用者导入你的包时实际解析到的是什么，以及如何在他们之前检查它 |
| [0045](lessons/0045-the-consumers-settings-are-not-yours.md) | 使用者的设置不是你的设置 | 严格的使用者会继承宽松作者的断言，而且无从察觉 |
| [0046](lessons/0046-the-typescript-that-does-not-erase.md) | 不会被擦除的 TypeScript | 四项会输出你并未要求的代码的特性，以及点名它们的那个标志 |
| [0047](lessons/0047-settling-it-from-the-source.md) | 从源头裁定 | 哪份文档能回答关于编译器的问题，以及如何阅读它自带的声明 |
| [0048](lessons/0048-reviewing-typescript.md) | 评审 TypeScript 代码 | 说出一个类型的代价，而不是说它看起来很复杂 |
| [0049](lessons/0049-trusted-to-make-the-call.md) | 值得信赖去做决定 | 本学习路线的最后一次判断，以及编译器永远不会替你做的事 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [强制类型转换与相等性](reference/coercion-and-equality.md)：假值、`==` 会转换什么、默认应该写哪个运算符
- [事件循环与 promise](reference/event-loop-and-promises.md)：队列顺序、组合器，以及没有任何编译器会报告的异步错误
- [值之上的类型](reference/types-over-values.md)：每种标注带来了什么、类型推断能够到达哪里，以及编译器有意留下的漏洞
- [严格性与编译器](reference/strictness-and-the-compiler.md)：哪个标志捕捉哪种失败、一项设置从哪里来，以及一个 import 如何被解析
- [建模](reference/modelling.md)：哪种形状能消除非法状态，以及哪种声明能在你犯错的地方捕捉到错误
- [运行时边界](reference/the-runtime-boundary.md)：值从哪里进入、由什么来检查它们，以及哪些断言根本没有任何东西去检查
- [类型层面的工具](reference/type-level-tools.md)：哪种构造计算出哪种类型，以及一个巧妙的类型必须通过的检验
- [判断力](reference/judgment.md)：哪些修改会破坏使用者、哪些不会被擦除，以及如何依据源头论证你的决定

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
