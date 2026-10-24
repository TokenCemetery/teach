---
title: Kubernetes
description: "在 Kubernetes 集群上运行服务并对它们负责：协调循环、工作负载、网络、配置、可靠性、安全、打包与调试"
type: topic
---

# 学习：Kubernetes

在 Kubernetes 集群上运行任何容器化服务，并对它在那里的遭遇负责：用集群会去协调的清单描述它，把它暴露出去，配置它，让它在滚动发布、节点故障和负载之下保持健康，锁定它的权限，为多个环境打包它，并在它出问题时查明原因。学完后，你能评审别人的清单，说出每个选择的代价，升级其他团队依赖的东西而不破坏他们，并说出什么时候一个服务根本不需要 Kubernetes。

**最新课程：** [28. 当 Kubernetes 是错误答案时](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## 成功的标准

- 解释声明式模型：通过 API server 存储期望状态，控制器让集群朝它协调，以及当一个 pod 被删除或一个节点宕机时这意味着什么。
- 阅读和编写清单：每个对象都有的字段、标签与选择器、命名空间，以及用 `kubectl apply` 应用变更。
- 用 Deployment 运行无状态服务，滚动发布新版本并回滚，并用 Job、CronJob 和 DaemonSet 运行批处理工作和每节点一个的代理。
- 用 Service 和集群 DNS 在集群内部暴露服务，并用 Ingress 或 Gateway API 在集群外部暴露服务。
- 用 ConfigMap 和 Secret 配置工作负载，并说出 Secret 能保护什么、不能保护什么。
- 让工作负载保持健康：回答正确问题的探针、干净的终止，以及决定其 QoS 类别的 request 和 limit。
- 在持久存储上运行有状态的工作负载，用调度约束安排 pod 的位置，自动扩缩容，并防止自愿中断让服务宕掉。
- 用 RBAC、服务账号、网络策略和 pod 安全锁定工作负载。
- 用 Kustomize 或 Helm 为多个环境打包清单，并根据各自的代价在二者之间做出选择。
- 观测工作负载，并调试处于 Pending、崩溃或无法访问状态的工作负载，从事件和日志一直到调试容器。
- 评审别人的清单，升级其他团队依赖的集群或共享 chart，说出什么时候 Kubernetes 或它的某项惯常默认设置是错误的答案，并依据 API 参考裁定有争议的问题。

## 约束

- 假定你学过[容器系列](../containers/README.md)或具备同等基础：构建镜像，在单台主机上运行单个容器、处理信号、健康检查和资源限制。不要求具备 Kubernetes 的知识。
- 每个练习都在用 kind 创建的本地集群上运行，这需要 Docker 或 Podman、几 GB 内存，以及 `kubectl`。不需要云账号。当某节课的行为依赖云服务商（`LoadBalancer` 类型的 Service、节点自动扩缩器、云存储类）时，课程会明确指出，并讲授 kind 能展示的部分。
- 使用上游 Kubernetes 及其文档。托管服务（EKS、GKE、AKS）在默认设置和附加组件上有所不同，课程只在差异会改变答案的地方指出它。

## 范围之外

- 构建和运行单个容器。那属于[容器系列](../containers/README.md)，其中的[运行容器](../containers/reference/running-containers.md)速查表就是本系列第 5 阶段的单主机版本。
- 在服务自己的代码内部让它可观测、可停止：健康端点、信号处理、优雅关闭。这归各语言系列负责，例如 Go 的[优雅关闭](../../programming/golang/lessons/0025-graceful-shutdown.md)和 C# 的[日志与健康检查](../../programming/csharp/lessons/0039-logging-and-health-checks.md)。本系列讲授集群如何处理这些信号。
- 作为理论的共识和部分失败。那属于[分布式系统](../../architecture/distributed-systems/README.md)，其中的[共识](../../architecture/distributed-systems/reference/consensus.md)速查表解释了 etcd 在底层做什么。本系列讲授协调和 etcd 对运行工作负载的人意味着什么。
- 从流水线向集群交付变更，以及 GitOps 工具。那属于 [CI/CD 系列](../ci-cd/README.md)，其中的[部署](../ci-cd/reference/deployments.md)速查表涵盖部署策略、回滚，以及在推送式部署与 GitOps 之间做出选择。
- 安装和运维控制平面本身（etcd 备份、证书轮换、从零搭建集群）、编写控制器或 operator，以及服务网格。

## 学习路线

共十个阶段，从协调循环，到评审别人清单的判断力。一个阶段包含若干课程，边界并不严格；一个阶段是否完成，取决于能力，而不是课程数量。

| 阶段 | 课程 | 内容 | 完成的标志 |
|---|---|---|---|
| 1. 声明式模型 | 0001 至 0003 | 集群、控制平面与节点，API server、etcd 与控制器，协调循环，对象字段，标签，命名空间，`kubectl apply` | 能预测期望状态改变后集群会做什么，并写出它接受的清单 |
| 2. 工作负载 | 0004 至 0007 | Pod、Deployment 与 ReplicaSet，滚动更新与回滚，Job、CronJob 与 DaemonSet | 能运行无状态服务，向前推进和回退它，并为不是服务的工作挑选合适的控制器 |
| 3. 网络 | 0008 至 0010 | Service 与 EndpointSlice、kube-proxy、集群 DNS、Ingress 与 Gateway API | 能让工作负载在集群内外都可访问，并在访问失败时说出是哪一跳出了问题 |
| 4. 配置 | 0011 至 0012 | 作为环境变量和文件的 ConfigMap、Secret、静态加密、让密钥远离 Git | 能按环境配置工作负载，并说出是什么在保护它的密钥 |
| 5. 可靠地运行 | 0013 至 0015 | 存活、就绪和启动探针，终止与端点竞态，request、limit 与 QoS 类别 | 能运行只在就绪时才接收流量、能干净排空、且不会第一个被驱逐的工作负载 |
| 6. 状态、调度与扩缩 | 0016 至 0019 | PersistentVolume 与声明、StatefulSet、亲和性、污点与拓扑分布、自动扩缩、PodDisruptionBudget | 能运行有状态的工作负载，有意识地安排 pod 的位置，并在不中断服务的情况下扩缩和排空 |
| 7. 安全 | 0020 至 0021 | RBAC、服务账号、NetworkPolicy、安全上下文、Pod Security Standards | 能为人和 pod 授予最小权限，并限制 pod 能访问什么、能做什么 |
| 8. 打包 | 0022 至 0023 | Kustomize 的 base 与 overlay，Helm chart、values 与 release，在二者之间做选择 | 能把一套清单交付到多个环境，并为所选的工具辩护 |
| 9. 可观测性与调试 | 0024 至 0025 | 资源指标、事件、日志、kube-state-metrics、各种失败状态及解释它们的命令、调试容器 | 能查明工作负载为什么处于 Pending、崩溃或无法访问 |
| 10. 判断力 | 0026 至 0028 | 评审清单、升级别人依赖的集群或共享 chart、Kubernetes 或某项默认设置何时出错、依据 API 参考做出裁定 | 值得信任去对工作负载做出决定，并向别人解释清楚 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | Kubernetes 的用途 | 集群把许多台机器变成一个运行容器的地方，控制平面和节点分担其中的工作 |
| [0002](lessons/0002-the-reconciliation-loop.md) | 协调循环 | 你通过 API server 声明期望状态，控制器持续监视并采取行动，直到集群与之相符 |
| [0003](lessons/0003-objects-and-manifests.md) | 对象与清单 | 每个对象都有 apiVersion、kind、metadata、spec 和 status，标签、选择器、命名空间和 kubectl apply 都作用于这些字段 |
| [0004](lessons/0004-pods.md) | Pod | pod 是集群调度的单位，是共享一个网络命名空间和卷的若干容器，以及为什么你很少亲自创建它 |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployment 与 ReplicaSet | Deployment 拥有 ReplicaSet，ReplicaSet 拥有 pod，所以被删除的 pod 会被替换，而改动过的模板会变成一个新的 ReplicaSet |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | 滚动发布与回滚 | 用 maxSurge 和 maxUnavailable 滚动发布新版本，观察它、暂停它，并把它回滚到一个已知的修订版本 |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Job、CronJob 与 DaemonSet | 运行会结束的工作、按计划执行的工作，以及每个节点一个 pod，以及它们各自的失败模式 |
| [0008](lessons/0008-services.md) | Service | Service 为一组不断变化的 pod 提供一个稳定的虚拟 IP，EndpointSlice 和 kube-proxy 把流量路由到已就绪的 pod |
| [0009](lessons/0009-cluster-dns.md) | 集群 DNS | pod 如何按名称找到 Service，搜索路径和 ndots 对每次查询有什么影响，以及 headless Service 返回什么 |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress 与 Gateway API | 通过控制器把外部 HTTP 流量引入集群，以及为什么 Gateway API 按角色拆分这项工作 |
| [0011](lessons/0011-configmaps.md) | ConfigMap | 以环境变量或文件的形式注入配置，并清楚二者中哪一种无需重启就能看到变更 |
| [0012](lessons/0012-secrets.md) | Secret | Secret 只是 base64，而不是加密，所以保护它的是 RBAC、静态加密，以及让它远离 Git |
| [0013](lessons/0013-probes.md) | 探针 | 存活、就绪和启动探针回答的是不同的问题，而错误的存活探针会引发它本想阻止的故障 |
| [0014](lessons/0014-pod-termination.md) | Pod 终止 | 从删除到 SIGKILL 之间发生了什么，以及为什么除非你事先规划，pod 在收到 SIGTERM 后仍会收到流量 |
| [0015](lessons/0015-requests-limits-and-qos.md) | request、limit 与 QoS | request 驱动调度，limit 驱动强制执行，二者共同决定 QoS 类别，而 QoS 类别决定谁最先被驱逐 |
| [0016](lessons/0016-persistent-storage.md) | 持久存储 | 用 PersistentVolumeClaim 申请存储，让 StorageClass 去供给它，并清楚访问模式和回收策略承诺了什么 |
| [0017](lessons/0017-statefulsets.md) | StatefulSet | 稳定的名称、有序的启动和每个副本一个卷，以及为什么光有 StatefulSet 并不能让运行数据库变得安全 |
| [0018](lessons/0018-scheduling.md) | 调度 | 用节点选择器、亲和性、拓扑分布、污点和容忍度引导 pod 的位置，并读懂 pod 为什么一直处于 Pending |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | 自动扩缩与中断 | 用 HorizontalPodAutoscaler 扩缩 pod，用节点自动扩缩器扩缩节点，并用 PodDisruptionBudget 防止一次排空拿下太多 pod |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC 与服务账号 | 用 Role 和绑定给一个人或一个 pod 恰好授予它需要的操作，并用 kubectl auth can-i 检查 |
| [0021](lessons/0021-network-policy-and-pod-security.md) | 网络策略与 Pod 安全 | 默认拒绝 pod 之间的流量，然后用安全上下文和 Pod Security Standards 限制 pod 在其节点上能做什么 |
| [0022](lessons/0022-kustomize.md) | Kustomize | 保留一份由普通清单组成的 base，并用 overlay 按环境为它打补丁，无需模板语言 |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm 与 Kustomize 的对比 | 安装并编写 Helm chart，并根据各自的代价在 chart 与 Kustomize overlay 之间做出选择 |
| [0024](lessons/0024-observability.md) | 可观测性 | 阅读资源指标、事件、容器日志和对象状态指标，并清楚每一种回答的是什么问题 |
| [0025](lessons/0025-debugging-a-workload.md) | 调试工作负载 | 借助 describe、事件、日志和 kubectl debug，从 Pending、ImagePullBackOff、CrashLoopBackOff 和 OOMKilled 一路追查到原因 |
| [0026](lessons/0026-reviewing-manifests.md) | 评审清单 | 评审别人的清单，说出每个选择在可用性、安全性和可运维性上的代价 |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | 升级别人依赖的东西 | 让集群或共享 chart 越过一个已被移除的 API 版本，而不破坏其工作负载依赖它的团队 |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | 当 Kubernetes 是错误答案时 | 说出什么时候一个服务不需要 Kubernetes，或某项惯常默认设置是错的，并依据 API 参考裁定有争议的问题 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源，每一项都注明了它涵盖的内容
- [kubectl](reference/kubectl.md)：按任务组织的命令，从检查对象到滚动发布、调试和权限检查，贯穿整个学习路线
- [工作负载](reference/workloads.md)：对象字段、标签与选择器、pod、Deployment、滚动发布、Job、CronJob 与 DaemonSet，来自第 1 和第 2 阶段
- [网络](reference/networking.md)：Service 类型、EndpointSlice、DNS 名称与 ndots、Ingress 与 Gateway API 资源，来自第 3 阶段
- [配置](reference/configuration.md)：作为环境变量和文件的 ConfigMap 与 Secret、更新行为，以及是什么在保护 Secret，来自第 4 阶段
- [可靠地运行](reference/running-reliably.md)：三种探针、终止顺序、request、limit 与 QoS 类别，来自第 5 阶段
- [状态、调度与扩缩](reference/state-scheduling-and-scale.md)：存储、StatefulSet、位置约束、自动扩缩器与中断预算，来自第 6 阶段
- [集群安全](reference/cluster-security.md)：RBAC 对象、服务账号令牌、NetworkPolicy 模式与 Pod Security Standards，来自第 7 阶段
- [打包](reference/packaging.md)：Kustomize 与 Helm 的并列对比，以及各自适用的场合，来自第 8 阶段
- [调试工作负载](reference/debugging-workloads.md)：每种失败状态、它的成因，以及按顺序要运行的命令，来自第 9 阶段
- [清单评审清单](reference/manifest-review-checklist.md)：评审别人的清单时要问的问题，以及惯常答案何时出错，来自第 10 阶段

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
