---
title: Kubernetes
description: "Rode serviços em um cluster Kubernetes e seja dono deles: o loop de reconciliação, workloads, rede, configuração, confiabilidade, segurança, empacotamento e depuração"
type: topic
---

# Aprendizado: Kubernetes

Rode qualquer serviço conteinerizado em um cluster Kubernetes e seja dono do que acontece com ele lá: descreva-o em manifestos que o cluster reconcilia, exponha-o, configure-o, mantenha-o saudável ao longo de rollouts, falhas de nó e carga, restrinja-o, empacote-o para vários ambientes e descubra por que ele está quebrado quando estiver. Termine capaz de revisar os manifestos de outra pessoa nomeando o que cada escolha custa, de atualizar o que outros times usam sem quebrá-los e de dizer quando um serviço nem precisa de Kubernetes.

**Última lição:** [28. Quando o Kubernetes é a resposta errada](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## O sucesso se parece com isto

- Explicar o modelo declarativo: o estado desejado armazenado por meio do API server, controllers reconciliando o cluster em direção a ele, e o que isso significa quando um pod é excluído ou um nó morre.
- Ler e escrever manifestos: os campos que todo objeto tem, labels e selectors, namespaces e a aplicação de mudanças com `kubectl apply`.
- Rodar um serviço stateless com um Deployment, fazer o rollout de uma nova versão e o rollback dela, e rodar trabalho em lote e agentes por nó com Jobs, CronJobs e DaemonSets.
- Expor um serviço dentro do cluster com um Service e o DNS do cluster, e fora dele com Ingress ou com a Gateway API.
- Configurar um workload com ConfigMaps e Secrets, e dizer o que um Secret protege e o que não protege.
- Manter um workload saudável: probes que respondem à pergunta certa, um encerramento limpo, e requests e limits que definem sua classe de QoS.
- Rodar workloads stateful em armazenamento persistente, posicionar pods com restrições de agendamento, escalá-los automaticamente e impedir que disrupções voluntárias derrubem um serviço.
- Restringir um workload com RBAC, service accounts, network policy e pod security.
- Empacotar manifestos para vários ambientes com Kustomize ou Helm, e escolher entre eles pelo que cada um custa.
- Observar um workload e depurar um que esteja Pending, quebrando ou inacessível, dos eventos e logs até um contêiner de debug.
- Revisar os manifestos de outra pessoa, atualizar um cluster ou um chart compartilhado do qual outros times dependem, dizer quando o Kubernetes ou um dos seus padrões habituais é a resposta errada e resolver uma questão em disputa pela referência da API.

## Restrições

- Pressupõe a [trilha de contêineres](../containers/README.md) ou equivalente: construir uma imagem, executar um contêiner, sinais, health checks e limites em um host. Não exige conhecimento prévio de Kubernetes.
- Toda prática roda em um cluster local criado com kind, que precisa de Docker ou Podman e de alguns gigabytes de memória, além do `kubectl`. Nenhuma conta de nuvem é necessária. Onde o comportamento de uma lição depende de um provedor de nuvem (um Service `LoadBalancer`, um autoscaler de nós, uma storage class de nuvem), ela diz isso e ensina a parte que o kind consegue mostrar.
- Usa o Kubernetes upstream e a documentação dele. As ofertas gerenciadas (EKS, GKE, AKS) diferem em padrões e add-ons, e as lições só nomeiam uma diferença onde ela muda a resposta.

## Fora do escopo

- Construir e executar um contêiner. Isso é a [trilha de contêineres](../containers/README.md), cuja folha de [Executando contêineres](../containers/reference/running-containers.md) é a versão em um único host da etapa 5 daqui.
- Tornar um serviço observável e interrompível de dentro do próprio código: endpoints de saúde, tratamento de sinais, encerramento gracioso. As trilhas de linguagem são donas disso, por exemplo [Encerramento gracioso](../../programming/golang/lessons/0025-graceful-shutdown.md) em Go e [Logging e health checks](../../programming/csharp/lessons/0039-logging-and-health-checks.md) em C#. Esta trilha ensina o que o cluster faz com esses sinais.
- Consenso e falha parcial como teoria. Isso é [Sistemas Distribuídos](../../architecture/distributed-systems/README.md), cuja folha de [Consenso](../../architecture/distributed-systems/reference/consensus.md) explica o que o etcd está fazendo por baixo. Esta trilha ensina o que reconciliação e etcd significam para quem roda workloads.
- Entregar uma mudança ao cluster a partir de um pipeline, e ferramentas de GitOps. Isso é a [trilha de CI/CD](../ci-cd/README.md), cuja folha de [Deployments](../ci-cd/reference/deployments.md) cobre estratégias de deployment, rollback e a escolha entre um deploy por push e GitOps.
- Instalar e operar o próprio control plane (backups do etcd, rotação de certificados, construir um cluster do zero), escrever controllers ou operators, e service meshes.

## O arco

Dez etapas, do loop de reconciliação até o julgamento para revisar os manifestos de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O modelo declarativo | 0001 a 0003 | Cluster, control plane e nós, o API server, etcd e controllers, o loop de reconciliação, campos de objeto, labels, namespaces, `kubectl apply` | Consegue prever o que o cluster faz depois de uma mudança no estado desejado e escrever um manifesto que ele aceita |
| 2. Workloads | 0004 a 0007 | Pods, Deployments e ReplicaSets, rolling updates e rollbacks, Jobs, CronJobs e DaemonSets | Consegue rodar um serviço stateless, avançá-lo e voltá-lo, e escolher o controller para um trabalho que não é um serviço |
| 3. Rede | 0008 a 0010 | Services e EndpointSlices, kube-proxy, DNS do cluster, Ingress e a Gateway API | Consegue tornar um workload acessível dentro e fora do cluster e dizer qual salto falhou quando ele não está |
| 4. Configuração | 0011 a 0012 | ConfigMaps como ambiente e arquivos, Secrets, criptografia em repouso, manter secrets fora do Git | Consegue configurar um workload por ambiente e dizer o que protege seus secrets |
| 5. Rodando com confiabilidade | 0013 a 0015 | Probes de liveness, readiness e startup, encerramento e a corrida dos endpoints, requests, limits e classes de QoS | Consegue rodar um workload que só recebe tráfego quando está pronto, é drenado de forma limpa e não é o primeiro a ser despejado |
| 6. Estado, agendamento e escala | 0016 a 0019 | PersistentVolumes e claims, StatefulSets, affinity, taints e topology spread, autoscaling, PodDisruptionBudgets | Consegue rodar um workload stateful, posicionar pods de propósito, e escalar e drenar sem indisponibilidade |
| 7. Segurança | 0020 a 0021 | RBAC, service accounts, NetworkPolicy, security contexts, Pod Security Standards | Consegue conceder privilégio mínimo a pessoas e pods e restringir o que um pod pode alcançar e fazer |
| 8. Empacotamento | 0022 a 0023 | Bases e overlays do Kustomize, charts, values e releases do Helm, a escolha entre eles | Consegue entregar um conjunto de manifestos a vários ambientes e defender a ferramenta escolhida |
| 9. Observabilidade e depuração | 0024 a 0025 | Métricas de recursos, eventos, logs, kube-state-metrics, os estados de falha e os comandos que os explicam, contêineres de debug | Consegue descobrir por que um workload está Pending, quebrando ou inacessível |
| 10. Julgamento | 0026 a 0028 | Revisar manifestos, atualizar um cluster ou um chart compartilhado do qual outros dependem, quando o Kubernetes ou um padrão está errado, resolver isso pela referência da API | Tem a confiança para tomar a decisão sobre um workload e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | Para que serve o Kubernetes | Um cluster transforma muitas máquinas em um único lugar para rodar contêineres, e o control plane e os nós dividem o trabalho |
| [0002](lessons/0002-the-reconciliation-loop.md) | O loop de reconciliação | Você declara o estado desejado por meio do API server, e os controllers continuam observando e agindo até que o cluster corresponda a ele |
| [0003](lessons/0003-objects-and-manifests.md) | Objetos e manifestos | Todo objeto tem apiVersion, kind, metadata, spec e status, e labels, selectors, namespaces e kubectl apply trabalham todos sobre esses campos |
| [0004](lessons/0004-pods.md) | Pods | Um pod é a unidade que o cluster agenda, contêineres que compartilham um namespace de rede e volumes, e por que você raramente cria um diretamente |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployments e ReplicaSets | Um Deployment é dono de ReplicaSets que são donos de pods, então um pod excluído é substituído e um template alterado vira um novo ReplicaSet |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | Rollouts e rollbacks | Fazer o rollout de uma nova versão com maxSurge e maxUnavailable, acompanhá-lo, pausá-lo e fazer rollback para uma revisão conhecida |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Jobs, CronJobs e DaemonSets | Rodar trabalho que termina, trabalho agendado e um pod por nó, e o modo de falha que cada um tem |
| [0008](lessons/0008-services.md) | Services | Um Service dá a um conjunto variável de pods um único IP virtual estável, e EndpointSlices e kube-proxy roteiam para os que estão prontos |
| [0009](lessons/0009-cluster-dns.md) | DNS do cluster | Como um pod encontra um Service pelo nome, o que o search path e o ndots fazem com cada consulta e o que um Service headless devolve |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress e a Gateway API | Trazer tráfego HTTP de fora para dentro do cluster por meio de um controller, e por que a Gateway API divide o trabalho por papel |
| [0011](lessons/0011-configmaps.md) | ConfigMaps | Injetar configuração como variáveis de ambiente ou arquivos, e saber qual dos dois enxerga uma mudança sem reinício |
| [0012](lessons/0012-secrets.md) | Secrets | Um Secret é base64, não criptografia, então o que o protege é o RBAC, a criptografia em repouso e mantê-lo fora do Git |
| [0013](lessons/0013-probes.md) | Probes | Probes de liveness, readiness e startup respondem a perguntas diferentes, e a probe de liveness errada causa a indisponibilidade que deveria impedir |
| [0014](lessons/0014-pod-termination.md) | Encerramento de pods | O que acontece entre uma exclusão e o SIGKILL, e por que um pod ainda recebe tráfego depois do SIGTERM a menos que você planeje para isso |
| [0015](lessons/0015-requests-limits-and-qos.md) | Requests, limits e QoS | Requests guiam o agendamento e limits guiam a imposição, e juntos definem a classe de QoS que decide quem é despejado primeiro |
| [0016](lessons/0016-persistent-storage.md) | Armazenamento persistente | Reivindicar armazenamento com um PersistentVolumeClaim, deixar uma StorageClass provisioná-lo e saber o que access modes e reclaim policies prometem |
| [0017](lessons/0017-statefulsets.md) | StatefulSets | Nomes estáveis, inicialização ordenada e um volume por réplica, e por que um StatefulSet sozinho não torna seguro rodar um banco de dados |
| [0018](lessons/0018-scheduling.md) | Agendamento | Direcionar pods com node selectors, affinity, topology spread, taints e tolerations, e entender por que um pod continua Pending |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | Autoscaling e disrupções | Escalar pods com o HorizontalPodAutoscaler e nós com um autoscaler de nós, e impedir com um PodDisruptionBudget que um drain derrube pods demais |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC e service accounts | Conceder a uma pessoa ou a um pod exatamente os verbos de que ela precisa com Roles e bindings, e verificar isso com kubectl auth can-i |
| [0021](lessons/0021-network-policy-and-pod-security.md) | Network policy e pod security | Negar por padrão o tráfego entre pods e então restringir o que um pod pode fazer no seu nó com security contexts e Pod Security Standards |
| [0022](lessons/0022-kustomize.md) | Kustomize | Manter uma base de manifestos simples e aplicar patches por ambiente com overlays, sem uma linguagem de template |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm contra Kustomize | Instalar e escrever um chart Helm, e escolher entre um chart e um overlay do Kustomize pelo que cada um custa |
| [0024](lessons/0024-observability.md) | Observabilidade | Ler métricas de recursos, eventos, logs de contêiner e métricas de estado de objetos, e saber a qual pergunta cada um responde |
| [0025](lessons/0025-debugging-a-workload.md) | Depurando um workload | Ir de Pending, ImagePullBackOff, CrashLoopBackOff e OOMKilled até a causa com describe, eventos, logs e kubectl debug |
| [0026](lessons/0026-reviewing-manifests.md) | Revisando manifestos | Revisar os manifestos de outra pessoa nomeando o que cada escolha custa em disponibilidade, segurança e operabilidade |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | Atualizando o que outros usam | Levar um cluster ou um chart compartilhado além de uma versão de API removida sem quebrar os times cujos workloads dependem dele |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | Quando o Kubernetes é a resposta errada | Dizer quando um serviço não precisa de Kubernetes ou quando um padrão habitual está errado, e resolver uma questão em disputa pela referência da API |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [kubectl](reference/kubectl.md): os comandos por tarefa, da inspeção de objetos a rollouts, depuração e verificação de permissões, ao longo do arco
- [Workloads](reference/workloads.md): campos de objeto, labels e selectors, pods, Deployments, rollouts, Jobs, CronJobs e DaemonSets, das etapas 1 e 2
- [Rede](reference/networking.md): tipos de Service, EndpointSlices, nomes DNS e ndots, recursos de Ingress e da Gateway API, da etapa 3
- [Configuração](reference/configuration.md): ConfigMaps e Secrets como ambiente e arquivos, comportamento de atualização e o que protege um Secret, da etapa 4
- [Rodando com confiabilidade](reference/running-reliably.md): as três probes, a sequência de encerramento, requests, limits e classes de QoS, da etapa 5
- [Estado, agendamento e escala](reference/state-scheduling-and-scale.md): armazenamento, StatefulSets, restrições de posicionamento, autoscalers e disruption budgets, da etapa 6
- [Segurança do cluster](reference/cluster-security.md): objetos de RBAC, tokens de service account, padrões de NetworkPolicy e Pod Security Standards, da etapa 7
- [Empacotamento](reference/packaging.md): Kustomize e Helm lado a lado, e quando cada um se encaixa, da etapa 8
- [Depurando workloads](reference/debugging-workloads.md): cada estado de falha, o que o causa e os comandos a executar em ordem, da etapa 9
- [Checklist de revisão de manifestos](reference/manifest-review-checklist.md): as perguntas a fazer sobre os manifestos de outra pessoa, e quando a resposta de sempre está errada, da etapa 10

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
