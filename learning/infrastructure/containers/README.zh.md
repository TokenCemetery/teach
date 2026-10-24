---
title: 容器
description: "把服务打包成容器镜像并对它负责：内核原语、Dockerfile，以及运行、加固和调试单个容器"
type: topic
---

# 学习：容器

把任何服务打包成容器镜像，并对它在单台主机上的遭遇负责：清楚容器运行时内核在做什么，写出能构建小巧、可复现镜像的 Dockerfile，让容器运行时能干净地关闭并守住资源限制，加固它，并在它无法启动时调试它。学完后，你能评审别人的 Dockerfile 和镜像，说出每个选择的代价。

**最新课程：** [24. 当惯常答案出错时](lessons/0024-when-the-usual-answer-is-wrong.md)

## 成功的标准

- 用内核的术语（命名空间、cgroup 和分层的根文件系统）解释容器是什么，以及它与虚拟机有何不同。
- 读懂一个镜像：它的清单、配置和层，标签与摘要的区别，并准确拉取经过测试的那个镜像。
- 用多阶段构建写出能构建小巧、对缓存友好且可复现镜像的 Dockerfile。
- 运行一个收到信号时能干净关闭、能报告自身健康状况、并守在内存和 CPU 限制之内的容器，而且容器内的运行时也遵守这些限制。
- 在单台主机上连接容器：网络、发布的端口、用于保存状态的卷，以及用于本地开发的 Compose。
- 加固镜像：非 root 用户、最少的权限、最小化的基础镜像、经过分诊的漏洞扫描、不进入镜像层的密钥，以及可供验证的签名和来源证明（provenance）。
- 调试无法启动或行为异常的容器，从它的退出码一直深入到它的命名空间内部，包括没有 shell 的容器。
- 评审别人的 Dockerfile 和镜像，把基础镜像的变更逐步推广到依赖它的各个服务，并说出什么时候惯常答案是错的。

## 约束

- 假定你熟悉 Linux 命令行，并用某种语言构建和运行过服务。不要求具备容器的知识。
- 使用带 BuildKit 的 Docker CLI，因为大多数文档和大多数团队用的都是它。当某个行为属于 OCI 规范而不是 Docker 时，课程会明确指出，而且同样的命令在 Podman 中大多也能用。
- 第 1 阶段的练习需要一个有 root 权限的 Linux shell，例如一台 Linux 机器或虚拟机。在运行 Docker Desktop 的笔记本上，容器本身运行在由 Docker Desktop 管理的 Linux 虚拟机中。

## 范围之外

- 为某一种语言构建可运行的制品。这归各语言系列负责，本系列把它们的产出放进镜像：静态二进制文件见 [Go：工具链命令](../../programming/golang/reference/toolchain-commands.md)，可运行制品和 `jlink` 见 [Java：测试与构建](../../programming/java/reference/testing-and-build.md) 和[模块系统](../../programming/java/reference/the-module-system.md)，另见 [C#：交付服务](../../programming/csharp/reference/shipping-the-service.md)，wheel 见 [Python：项目与打包](../../programming/python/reference/project-and-packaging.md)。
- 跨集群编排容器：调度、服务、滚动发布、作为集群功能的探针。那属于 [Kubernetes 系列](../kubernetes/README.md)。本系列止步于单台主机上的一个或少数几个容器。
- 在流水线中构建和发布镜像。那属于 [CI/CD 系列](../ci-cd/README.md)，其中的[制品与版本](../ci-cd/reference/artifacts-and-versioning.md)速查表涵盖打标签和按摘要发布。本系列手动构建镜像，好让你先理解流水线自动化的是什么。
- Windows 容器，以及编写容器运行时。

## 学习路线

共八个阶段，从容器是什么，到评审别人镜像的判断力。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 容器是什么 | 0001 至 0003 | 作为进程的容器、命名空间、cgroup、与虚拟机的区别 | 能手动搭建容器的隔离，并说出每个部分隐藏或限制了什么 |
| 2. 镜像 | 0004 至 0006 | 清单、配置与层，overlayfs，运行时栈与生命周期，镜像仓库、标签与摘要 | 能读懂一个镜像，并准确拉取经过测试的那一个 |
| 3. 构建镜像 | 0007 至 0010 | Dockerfile 指令与构建上下文、构建缓存、多阶段构建与基础镜像、可复现性 | 能写出构建小巧、对缓存友好、可复现镜像的 Dockerfile |
| 4. 运行单个容器 | 0011 至 0013 | PID 1 与信号、健康检查与重启策略、内存与 CPU 限制 | 能运行一个干净停止、报告健康状况并遵守限制的容器 |
| 5. 网络、存储与 Compose | 0014 至 0016 | 桥接网络与发布的端口、卷与绑定挂载、用于本地开发的 Compose | 能在单台主机上把服务及其依赖一起运行，且状态得以保留 |
| 6. 安全 | 0017 至 0019 | 非 root、capability 与特权、最小化基础镜像与扫描、构建密钥、签名与来源证明 | 能加固镜像，并验证一个镜像从何而来 |
| 7. 调试 | 0020 至 0021 | 退出码、日志与 inspect、覆盖入口点、加入容器的命名空间 | 即使没有 shell，也能查明容器为什么无法启动或行为异常 |
| 8. 判断力 | 0022 至 0024 | 评审 Dockerfile、修改别人依赖的基础镜像、惯常答案何时出错、依据规范做出裁定 | 值得信任去对镜像做出决定，并向别人解释清楚 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | 容器就是进程 | 容器是一个普通的 Linux 进程，内核只向它展示机器的受限视图，而不是一台小型虚拟机 |
| [0002](lessons/0002-namespaces.md) | 命名空间 | 每种命名空间隐藏一类全局资源，而 unshare 一次一个命名空间地搭建出容器的视图 |
| [0003](lessons/0003-cgroups.md) | cgroup | 控制组为进程树的内存、CPU 和 PID 设置上限并进行计量，以及达到限制时内核会做什么 |
| [0004](lessons/0004-images-and-layers.md) | 镜像与层 | OCI 镜像由一个清单、一个配置和一叠层 tar 包组成，overlayfs 把它们合并成一个根文件系统 |
| [0005](lessons/0005-from-image-to-running-container.md) | 从镜像到运行中的容器 | docker run 在镜像与进程之间做了什么：运行时栈、可写层和生命周期 |
| [0006](lessons/0006-registries-tags-and-digests.md) | 镜像仓库、标签与摘要 | 标签是可移动的名称，摘要是内容的哈希，所以要按摘要拉取，才能准确运行经过测试的内容 |
| [0007](lessons/0007-your-first-dockerfile.md) | 你的第一个 Dockerfile | 构建镜像的指令、构建上下文，以及 .dockerignore 把什么挡在它之外 |
| [0008](lessons/0008-the-build-cache.md) | 构建缓存 | 缓存的层何时会被复用，什么会让它及其后的每一层失效，以及指令顺序如何决定重新构建的时间 |
| [0009](lessons/0009-multi-stage-builds.md) | 多阶段构建 | 在一个阶段中构建，只把制品复制到最小化的最终阶段，以及每种基础镜像选择的代价 |
| [0010](lessons/0010-reproducible-builds.md) | 可复现构建 | 是什么让同一个 Dockerfile 的两次构建产生差异，以及如何固定基础镜像、软件包和时间戳来消除差异 |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 与信号 | 为什么当进程是 PID 1 或被 shell 包裹时容器会忽略 SIGTERM，以及如何优雅地关闭 |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | 健康检查与重启策略 | 报告容器内的进程是否真的在正常工作，并决定它停止时运行时该做什么 |
| [0013](lessons/0013-resource-limits-in-practice.md) | 资源限制实践 | 设置内存和 CPU 限制，读懂 OOM kill 和 CPU 节流，并检查容器内的运行时是否看到了限制 |
| [0014](lessons/0014-container-networking.md) | 容器网络 | 网络命名空间、veth 对和网桥把容器连接起来，而发布端口会在主机上添加一条 NAT 规则 |
| [0015](lessons/0015-volumes-and-state.md) | 卷与状态 | 数据在命名卷、绑定挂载和 tmpfs 中的什么地方比容器活得更久，以及主机与容器之间的文件所有权陷阱 |
| [0016](lessons/0016-compose-for-local-development.md) | 用于本地开发的 Compose | 在一个 Compose 文件中描述服务及其依赖，并等待依赖变为健康，而不只是已启动 |
| [0017](lessons/0017-least-privilege.md) | 最小权限 | 以非 root 用户运行，丢弃 capability，保持根文件系统只读，并清楚特权模式和 Docker 套接字会交出什么 |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | 最小化基础镜像与扫描 | 缩减镜像包含的内容，读懂漏洞扫描结果，并对发现的问题做分诊，而不是追求零漏洞数 |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | 密钥、签名与来源证明 | 让密钥远离镜像层，按摘要为镜像签名，并在运行之前验证它在哪里构建 |
| [0020](lessons/0020-a-container-that-will-not-start.md) | 无法启动的容器 | 阅读退出码、日志和 inspect 的输出，然后覆盖入口点，查明它为什么停止 |
| [0021](lessons/0021-debugging-a-running-container.md) | 调试运行中的容器 | 从调试容器或主机加入其命名空间，进入一个没有 shell 的容器 |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | 评审 Dockerfile | 评审别人的 Dockerfile 和镜像，说出每个选择在大小、重新构建时间、安全性和可靠性上的代价 |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | 修改别人依赖的基础镜像 | 借助标签、摘要、重新构建和弃用，把共享的基础镜像向前推进，而不破坏基于它构建的服务 |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | 当惯常答案出错时 | 识别 Alpine、distroless、固定的摘要，乃至使用容器本身，什么时候是错误的选择，并依据规范做出裁定 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [容器原语](reference/container-primitives.md)：命名空间、cgroup、镜像布局，以及标签与摘要的对比，来自第 1 和第 2 阶段
- [Dockerfile](reference/dockerfile.md)：指令、缓存规则、多阶段模式、基础镜像与可复现性，来自第 3 阶段
- [运行容器](reference/running-containers.md)：信号、健康检查、限制、网络、卷与 Compose，来自第 4 和第 5 阶段
- [容器安全](reference/container-security.md)：权限、最小化基础镜像、扫描分诊、构建密钥、签名与来源证明，来自第 6 阶段
- [调试容器](reference/debugging-containers.md)：退出码、按顺序要运行的命令，以及如何进入没有 shell 的容器，来自第 7 阶段
- [Dockerfile 评审清单](reference/dockerfile-review-checklist.md)：评审别人的 Dockerfile 和镜像时要问的问题，以及惯常答案何时出错，来自第 8 阶段

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
