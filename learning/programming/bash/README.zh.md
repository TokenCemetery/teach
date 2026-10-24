---
title: Bash
description: "编写能在生产环境中经受考验的 shell：引号、退出状态、失败模式，以及知道何时停手改用真正的编程语言"
type: topic
---

# 学习：Bash

能够为 CI 流水线、部署和运维工具编写并维护 shell 脚本，使它们不会因为一个错误的输入或一个未设置的变量而悄悄出错，并能识别出一个脚本何时已经超出了 shell 的能力范围，应当改用真正的编程语言。

**最新课程：** [17. shellcheck、shfmt 与测试脚本](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## 成功的标准

- 编写一个 CI/部署脚本或运维工具，正确处理引号、退出状态和常见的失败模式，并解释每个选择为什么是必要的。
- 给定一个 shell 脚本，说出它在边界情况下会以哪种具体方式出错（未加引号的展开、未设置的变量、被忽略的命令退出状态）。
- 识别出一个脚本何时已经超出了 shell 那片无需判断的舒适区，并说出为什么这项工作现在应当交给 `programming/python`。

## 约束

- 不要求有 shell 脚本经验。
- 以 POSIX `sh` 的可移植性为准，而不是只适用于 bash 的惯用法，尽管 bash 是本主题的大本营；用到只有 bash 才有的特性时，会明确指出。
- 只在脚本确实需要时才涉及 `awk`/`sed`，不把它们作为独立的话题。

## 范围之外

- 一个脚本本该不再是 shell 之后的一切：这条边界见 [`programming/python`](../../programming/python/)。

## 学习路线

共十一个阶段，从引号到 shellcheck、shfmt 和测试。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 引号 | 0001 | 能防止 shell 脚本在生产环境中最常见出错方式的那一个习惯 | 能正确使用引号，并解释未加引号的展开为什么会出错 |
| 2. 退出状态与错误处理 | 0002 至 0003 | `$?`、非官方严格模式（`set -euo pipefail`）、`trap` | 能编写正确处理退出状态和失败的脚本 |
| 3. 单词拆分与通配的陷阱 | 0004 | Bash Pitfalls 列表，引号之外的常见坑 | 给定一个脚本，能说出它会在哪个具体的边界情况下出错 |
| 4. 可移植性 | 0005 | POSIX `sh` 与只适用于 bash 的惯用法，以及各自何时重要 | 能编写可移植的 `sh`，并明确指出只有 bash 才有的特性 |
| 5. 必要时使用 `awk`/`sed` | 0006 | 只在脚本确实需要时才使用它们 | 能在真正需要时使用 `awk`/`sed`，而不过度使用 |
| 6. 知道何时停手 | 0007 | 识别出 shell 已经超出了它那片无需判断的舒适区 | 能说出为什么某项工作现在应当交给 `programming/python` |
| 7. shell 基础 | 0008 至 0009 | 变量、命令替换、控制流（`if`/`case`/循环）、函数、`local`、返回状态与输出的区别 | 能用变量、命令替换和控制流编写脚本，并把重复的工作组织成作用域正确的函数 |
| 8. 参数展开与数组 | 0010 至 0011 | 对未设置的变量给默认值或报错（`${v:-}`、`${v:?}`）、截取（`${v%%}`）、替换、索引数组与关联数组 | 能就地为值提供默认、校验和转换，并在不把它编码成字符串的情况下保存列表或映射 |
| 9. 重定向与组合 | 0012 至 0013 | 重定向的顺序、文件描述符、here-doc、为什么管道中的 `while` 循环会丢失变量、进程替换 | 能正确重定向各个流，并解释为什么在管道循环中设置的变量在循环结束后不复存在 |
| 10. 参数与作业控制 | 0014 至 0015 | `getopts`、用法/帮助的约定、信号、后台作业、`wait` | 能解析脚本自己的选项和参数，并正确管理后台工作和脚本自身的退出 |
| 11. 安全与工具 | 0016 至 0017 | `mktemp`、`eval`/注入的攻击面、ShellCheck、`shfmt`、用 bats/shunit2 测试 | 能安全地创建临时文件和动态命令，并用静态分析和测试抓住仅靠评审会漏掉的问题 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-quoting.md) | 引号 | 能防止 shell 脚本在生产环境中最常见出错方式的那一个习惯 |
| [0002](lessons/0002-exit-status.md) | 退出状态 | $? 实际报告的是什么，为什么 bash 默认会在命令失败后继续运行，以及脚本在生产环境中第二常见的出错方式 |
| [0003](lessons/0003-strict-mode-and-trap.md) | 严格模式与 trap | set -euo pipefail 中每个选项实际改变了什么、它真正的漏洞，以及在脚本失败时用 trap 可靠地完成清理 |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | 单词拆分与通配的陷阱 | 不只是漏了一个引号的常见坑，在这些情况下仅靠引号并不能完全解决问题 |
| [0005](lessons/0005-portability.md) | 可移植性 | POSIX sh 实际保证了什么，哪些常用的 bash 特性不在其中，以及这种差异何时真正重要 |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | 必要时使用 awk 与 sed | 认出 sed 和 awk 各自适合的任务形态，只在脚本确实需要时才使用其中之一，而不是出于习惯 |
| [0007](lessons/0007-knowing-when-to-stop.md) | 知道何时停手 | 表明一个脚本已经超出 shell 那片无需判断的舒适区的具体信号，以及为什么这项工作现在应当交给真正的编程语言 |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | 变量、命令替换与控制流 | shell 自己用来保存值、捕获命令输出，以及据此分支或循环的词汇 |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | 函数、local，以及返回状态与输出的区别 | 把重复的工作组织成函数，以及 shell 函数与几乎所有其他语言中的函数最显著的不同之处 |
| [0010](lessons/0010-parameter-expansion.md) | 参数展开 | 就地为值提供默认、报错和截取，而无需动用单独的命令 |
| [0011](lessons/0011-arrays.md) | 数组（索引数组与关联数组） | 在不把结构编码进字符串的情况下保存多个值，以及能让每个元素保持完整的那一种引号写法 |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | 重定向、文件描述符与 here-doc | 把命令的输出精确地发送到屏幕之外的地方，并就地为它提供一段输入 |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | 管道、子 shell 与进程替换 | 为什么在管道循环中设置的变量会在管道结束的那一刻消失，以及能保住它的、只有 bash 才有的解决办法 |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | 用 getopts 解析参数与用法约定 | 用与解析其他一切同样严谨的方式，解析脚本自己的选项和参数 |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | 信号、后台作业与 wait | 在一个脚本内并发地运行工作，并确保脚本自身退出时不会让这些工作成为孤儿 |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp、安全的临时文件与 eval/注入的攻击面 | 创建一个无法被预测或劫持的临时文件，以及为什么 eval 会把不可信的输入变成任意代码 |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck、shfmt 与测试脚本 | 能在脚本运行之前就抓住大部分悄无声息的错误的工具，以及如何测试其余部分 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源
- [引号与陷阱](reference/quoting-and-pitfalls.md)：引号规则、它在哪里会坑人，以及即使仔细加了引号仍然存在的 Bash Pitfalls
- [退出状态与错误处理](reference/exit-status-and-error-handling.md)：`$?`、`set -euo pipefail` 的各个选项及其真正的例外情况，以及用于确保清理的 `trap`
- [可移植性](reference/portability.md)：POSIX `sh` 与只有 bash 才有的特性、shebang 诚实原则，以及这种权衡何时值得
- [awk、sed 与知道何时停手](reference/awk-sed-and-when-to-stop.md)：让工具匹配任务的形态，以及表明脚本已经超出 shell 能力范围的具体信号

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
