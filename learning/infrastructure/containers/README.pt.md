---
title: Contêineres
description: "Empacote um serviço como imagem de contêiner e seja dono dela: primitivas do kernel, Dockerfiles, executar, proteger e depurar um contêiner"
type: topic
---

# Aprendizado: Contêineres

Empacote qualquer serviço como imagem de contêiner e seja dono do que acontece com ele em um host: saiba o que o kernel está fazendo quando um contêiner roda, escreva um Dockerfile que construa uma imagem pequena e reproduzível, execute-o de modo que ele encerre de forma limpa e fique dentro dos seus limites, endureça-o e depure-o quando ele não iniciar. Termine capaz de revisar o Dockerfile e a imagem de outra pessoa nomeando o que cada escolha custa.

**Última lição:** [24. Quando a resposta de sempre está errada](lessons/0024-when-the-usual-answer-is-wrong.md)

## O sucesso se parece com isto

- Explicar o que é um contêiner em termos de kernel (namespaces, cgroups e um sistema de arquivos raiz em camadas) e como isso difere de uma máquina virtual.
- Ler uma imagem: seu manifest, sua config e suas camadas, a diferença entre uma tag e um digest, e fazer pull exatamente da imagem que foi testada.
- Escrever um Dockerfile que construa uma imagem pequena, amigável ao cache e reproduzível, usando um build multi-stage.
- Executar um contêiner que encerra de forma limpa ao receber um sinal, reporta sua saúde e fica dentro de limites de memória e CPU que o runtime dentro dele respeita.
- Conectar contêineres em um host: rede, portas publicadas, volumes para estado e Compose para desenvolvimento local.
- Endurecer uma imagem: um usuário não root, o mínimo de privilégios, uma base mínima, um scan de vulnerabilidades triado, secrets mantidos fora das camadas, e uma assinatura e uma proveniência para verificar.
- Depurar um contêiner que não inicia ou se comporta mal, do código de saída até dentro dos namespaces dele, incluindo um sem shell.
- Revisar o Dockerfile e a imagem de outra pessoa, propagar uma mudança de imagem base pelos serviços que dependem dela e dizer quando a resposta de sempre é a errada.

## Restrições

- Pressupõe familiaridade com a linha de comando do Linux e já ter construído e executado um serviço em alguma linguagem. Não exige conhecimento prévio de contêineres.
- Usa a CLI do Docker com BuildKit, porque é o que a maior parte da documentação e a maioria dos times usam. Onde um comportamento pertence às especificações OCI e não ao Docker, a lição diz isso, e os mesmos comandos em geral funcionam no Podman.
- As práticas da etapa 1 precisam de um shell Linux com root, como uma máquina Linux ou uma máquina virtual. Em um laptop com Docker Desktop, os próprios contêineres rodam dentro de uma máquina virtual Linux que o Docker Desktop gerencia.

## Fora do escopo

- Construir o artefato executável de uma linguagem. As trilhas de linguagem são donas disso, e esta trilha coloca a saída delas em uma imagem: [Go: comandos da toolchain](../../programming/golang/reference/toolchain-commands.md) para binários estáticos, [Java: testes e build](../../programming/java/reference/testing-and-build.md) e [O sistema de módulos](../../programming/java/reference/the-module-system.md) para artefatos executáveis e `jlink`, [C#: entregando o serviço](../../programming/csharp/reference/shipping-the-service.md) e [Python: projeto e empacotamento](../../programming/python/reference/project-and-packaging.md) para wheels.
- Orquestrar contêineres em um cluster: agendamento, services, rollouts, probes como recurso do cluster. Isso é a [trilha de Kubernetes](../kubernetes/README.md). Esta trilha para em um contêiner, ou em alguns poucos, em um host.
- Construir e publicar imagens em um pipeline. Isso é a [trilha de CI/CD](../ci-cd/README.md), cuja folha de [Artefatos e versionamento](../ci-cd/reference/artifacts-and-versioning.md) cobre tags e publicação por digest. Esta trilha constrói imagens à mão para que o que um pipeline automatiza seja entendido primeiro.
- Contêineres Windows, e escrever um runtime de contêiner.

## O arco

Oito etapas, do que é um contêiner até o julgamento para revisar a imagem de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O que é um contêiner | 0001 a 0003 | Um contêiner como processo, namespaces, cgroups, a diferença em relação a uma máquina virtual | Consegue montar à mão o isolamento de um contêiner e dizer o que cada peça esconde ou limita |
| 2. Imagens | 0004 a 0006 | Manifest, config e camadas, overlayfs, a pilha de runtime e o ciclo de vida, registries, tags e digests | Consegue ler uma imagem e fazer pull exatamente da que foi testada |
| 3. Construindo imagens | 0007 a 0010 | Instruções do Dockerfile e o build context, o cache de build, builds multi-stage e imagens base, reprodutibilidade | Consegue escrever um Dockerfile que constrói uma imagem pequena, amigável ao cache e reproduzível |
| 4. Executando um contêiner | 0011 a 0013 | PID 1 e sinais, health checks e políticas de reinício, limites de memória e CPU | Consegue executar um contêiner que para de forma limpa, reporta sua saúde e respeita seus limites |
| 5. Rede, armazenamento e Compose | 0014 a 0016 | Redes bridge e portas publicadas, volumes e bind mounts, Compose para desenvolvimento local | Consegue executar um serviço e suas dependências juntos em um host com estado que sobrevive |
| 6. Segurança | 0017 a 0019 | Não root, capabilities e privilégio, bases mínimas e scan, secrets de build, assinatura e proveniência | Consegue endurecer uma imagem e verificar de onde uma imagem veio |
| 7. Depuração | 0020 a 0021 | Códigos de saída, logs e inspect, sobrescrever o entrypoint, entrar nos namespaces de um contêiner | Consegue descobrir por que um contêiner não inicia ou se comporta mal, mesmo sem shell |
| 8. Julgamento | 0022 a 0024 | Revisar um Dockerfile, mudar uma imagem base da qual outros dependem, quando a resposta de sempre está errada, resolver isso pela especificação | Tem a confiança para tomar a decisão sobre uma imagem e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | Um contêiner é um processo | Um contêiner é um processo Linux comum ao qual o kernel mostra uma visão restrita da máquina, e não uma pequena máquina virtual |
| [0002](lessons/0002-namespaces.md) | Namespaces | Cada tipo de namespace esconde um tipo de recurso global, e o unshare monta a visão de um contêiner um namespace por vez |
| [0003](lessons/0003-cgroups.md) | Cgroups | Control groups limitam e contabilizam a memória, a CPU e os PIDs de uma árvore de processos, e o que o kernel faz quando um limite é atingido |
| [0004](lessons/0004-images-and-layers.md) | Imagens e camadas | Uma imagem OCI é um manifest, uma config e uma pilha de tarballs de camadas que o overlayfs mescla em um único sistema de arquivos raiz |
| [0005](lessons/0005-from-image-to-running-container.md) | Da imagem ao contêiner em execução | O que o docker run faz entre a imagem e o processo: a pilha de runtime, a camada gravável e o ciclo de vida |
| [0006](lessons/0006-registries-tags-and-digests.md) | Registries, tags e digests | Uma tag é um nome móvel e um digest é o hash do conteúdo, então faça pull pelo digest para executar exatamente o que foi testado |
| [0007](lessons/0007-your-first-dockerfile.md) | Seu primeiro Dockerfile | As instruções que constroem uma imagem, o build context e o que o .dockerignore mantém fora dele |
| [0008](lessons/0008-the-build-cache.md) | O cache de build | Quando uma camada em cache é reutilizada, o que a invalida junto com toda camada depois dela e como a ordem das instruções decide o tempo de rebuild |
| [0009](lessons/0009-multi-stage-builds.md) | Builds multi-stage | Construir em uma etapa, copiar só o artefato para uma etapa final mínima e o que cada escolha de imagem base custa |
| [0010](lessons/0010-reproducible-builds.md) | Builds reproduzíveis | O que faz dois builds do mesmo Dockerfile diferirem, e fixar bases, pacotes e timestamps para que não difiram |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 e sinais | Por que um contêiner ignora SIGTERM quando seu processo é o PID 1 ou está embrulhado em um shell, e como encerrar de forma graciosa |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | Health checks e políticas de reinício | Reportar se o processo lá dentro está realmente funcionando e decidir o que o runtime faz quando ele para |
| [0013](lessons/0013-resource-limits-in-practice.md) | Limites de recursos na prática | Definir limites de memória e CPU, interpretar um OOM kill e o throttling de CPU e verificar se o runtime lá dentro enxerga o limite |
| [0014](lessons/0014-container-networking.md) | Rede de contêineres | Namespaces de rede, pares veth e uma bridge conectam contêineres, e publicar uma porta adiciona uma regra de NAT no host |
| [0015](lessons/0015-volumes-and-state.md) | Volumes e estado | Onde os dados sobrevivem a um contêiner em volumes nomeados, bind mounts e tmpfs, e a armadilha de propriedade de arquivos entre host e contêiner |
| [0016](lessons/0016-compose-for-local-development.md) | Compose para desenvolvimento local | Descrever um serviço e suas dependências em um único arquivo Compose e esperar que uma dependência esteja saudável, e não apenas iniciada |
| [0017](lessons/0017-least-privilege.md) | Privilégio mínimo | Rodar como usuário não root, remover capabilities, manter o sistema de arquivos raiz somente leitura e saber o que o modo privilegiado e o socket do Docker entregam |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | Bases mínimas e scan | Reduzir o que uma imagem contém, ler um scan de vulnerabilidades e triar os achados em vez de perseguir uma contagem zero |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | Secrets, assinatura e proveniência | Manter secrets fora das camadas, assinar uma imagem pelo digest e verificar onde ela foi construída antes de executá-la |
| [0020](lessons/0020-a-container-that-will-not-start.md) | Um contêiner que não inicia | Ler o código de saída, os logs e a saída do inspect, e então sobrescrever o entrypoint para descobrir por que ele parou |
| [0021](lessons/0021-debugging-a-running-container.md) | Depurando um contêiner em execução | Entrar em um contêiner que não tem shell juntando-se aos namespaces dele a partir de um contêiner de debug ou do host |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | Revisando um Dockerfile | Revisar o Dockerfile e a imagem de outra pessoa nomeando o que cada escolha custa em tamanho, tempo de rebuild, segurança e confiabilidade |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | Mudando uma imagem base da qual outros dependem | Avançar uma imagem base compartilhada sem quebrar os serviços construídos sobre ela, usando tags, digests, rebuilds e depreciação |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | Quando a resposta de sempre está errada | Reconhecer quando Alpine, distroless, um digest fixado ou até um contêiner é a decisão errada, e resolver isso pela especificação |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Primitivas de contêiner](reference/container-primitives.md): namespaces, cgroups, o layout da imagem e tags contra digests, das etapas 1 e 2
- [Dockerfile](reference/dockerfile.md): instruções, regras de cache, padrões multi-stage, imagens base e reprodutibilidade, da etapa 3
- [Executando contêineres](reference/running-containers.md): sinais, health checks, limites, rede, volumes e Compose, das etapas 4 e 5
- [Segurança de contêineres](reference/container-security.md): privilégios, bases mínimas, triagem de scan, secrets de build, assinatura e proveniência, da etapa 6
- [Depurando contêineres](reference/debugging-containers.md): códigos de saída, os comandos a executar em ordem e como entrar em um contêiner sem shell, da etapa 7
- [Checklist de revisão de Dockerfile](reference/dockerfile-review-checklist.md): as perguntas a fazer sobre o Dockerfile e a imagem de outra pessoa, e quando a resposta de sempre está errada, da etapa 8

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
