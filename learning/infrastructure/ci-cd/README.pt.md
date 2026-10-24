---
title: CI/CD
description: "Construa, teste e entregue cada mudança por um pipeline e seja dono dele: workflows, feedback rápido, artefatos, secrets, deployments, rollback e segurança da cadeia de suprimentos"
type: topic
---

# Aprendizado: CI/CD

Leve qualquer serviço de uma mudança mergeada até a execução em produção por um pipeline que é seu: prove em minutos que cada mudança compila e passa nos testes, produza um único artefato versionado e promova esse mesmo artefato pelos ambientes, dê ao pipeline o acesso de que ele precisa sem chaves de longa duração, faça o deploy com uma estratégia que limite o estrago de um release ruim e faça rollback quando um escapar. Termine capaz de revisar o pipeline de outra pessoa nomeando o que vai falhar, ficar lento ou vazar primeiro, de mudar um workflow do qual outros times dependem sem quebrar os merges deles e de dizer quando a resposta de sempre sobre entrega é a errada.

**Última lição:** [30. Quando a resposta de sempre está errada](lessons/0030-when-the-usual-answer-is-wrong.md)

## O sucesso se parece com isto

- Explicar o que integração contínua, entrega contínua e deployment contínuo prometem cada um, e o que um time precisa praticar para que a promessa se sustente.
- Escrever um pipeline como código: gatilhos e eventos, jobs, steps e runners, actions, expressões, contextos e outputs.
- Rodar etapas de build e de teste que falham primeiro no problema mais barato, em uma matriz, com cache, sem confiar em um teste flaky e rápidas o bastante para que as pessoas esperem pelo resultado.
- Produzir artefatos com uma versão rastreável até um commit, construí-los uma única vez e construir, publicar e referenciar uma imagem de contêiner pelo digest.
- Dar a um pipeline secrets e acesso à nuvem com privilégio mínimo: permissões do `GITHUB_TOKEN` restritas, OIDC em vez de chaves de longa duração e nenhum caminho para que entrada não confiável alcance qualquer um dos dois.
- Controlar deployments com environments e aprovações, e promover um único artefato de staging para produção.
- Fazer deploy com as estratégias rolling, blue-green e canary, fazer rollback ou roll forward, ordenar migrations de banco de dados em torno de um deploy e escolher entre um deploy por push e GitOps.
- Proteger a cadeia de suprimentos: fixar o que o pipeline executa, e produzir e verificar proveniência e SBOMs.
- Escalar pipelines entre repositórios e monorepos com reusable workflows, composite actions e filtros de caminho, e depurar um pipeline que falha só no runner.
- Revisar o pipeline de outra pessoa, mudar um workflow compartilhado ou um check obrigatório sem quebrar os times que dependem dele, dizer quando a resposta de sempre está errada e resolver um comportamento em disputa pela referência de sintaxe de workflow.

## Restrições

- Pressupõe familiaridade com Git, um shell e com compilar e testar um projeto em uma linguagem. Não exige conhecimento prévio de CI/CD. A lição 13 pressupõe a [trilha de contêineres](../containers/README.md) ou equivalente, e as lições 19 e 22 pressupõem o básico da [trilha de Kubernetes](../kubernetes/README.md).
- Ensina as tarefas que um pipeline executa e as executa com GitHub Actions, do mesmo jeito que `programming/java` ensina o ciclo de vida do build com Maven. Jenkins e GitLab CI aparecem só onde o modelo deles realmente difere.
- Toda prática roda em um repositório público descartável em uma conta gratuita do GitHub, onde os runners hospedados pelo GitHub não custam nada. As práticas de deployment fazem deploy em um cluster kind criado dentro do job, então nenhuma conta de nuvem é necessária. Onde uma lição depende de um provedor de nuvem, como uma política de confiança OIDC, ela mostra a parte que só o GitHub consegue mostrar e marca o resto como opcional.

## Fora do escopo

- Compilar e testar o código de uma linguagem. As trilhas de linguagem são donas dos comandos que um step do pipeline executa, por exemplo [Java: testes e build](../../programming/java/reference/testing-and-build.md), [Go: comandos da toolchain](../../programming/golang/reference/toolchain-commands.md), [Python: projeto e empacotamento](../../programming/python/reference/project-and-packaging.md) e [C#: testes e build](../../programming/csharp/reference/testing-and-build.md). Esta trilha executa esses steps em um pipeline.
- Escrever um Dockerfile e construir uma imagem à mão. Isso é a [trilha de contêineres](../containers/README.md), cuja folha de [Dockerfile](../containers/reference/dockerfile.md) é o que a lição 13 constrói em um pipeline.
- Executar a carga de trabalho depois de entregue: probes, rollouts como recurso do cluster, empacotamento de manifestos. Isso é a [trilha de Kubernetes](../kubernetes/README.md), cuja folha de [Empacotamento](../kubernetes/reference/packaging.md) cobre os manifestos que um job de deploy aplica. Esta trilha entrega a mudança a ele, e ensina GitOps apenas o suficiente para escolhê-lo.
- Escrever uma migration que não trave uma tabela. Isso é [SQL](../../programming/sql/README.md), cuja folha de [Operação](../../programming/sql/reference/operating.md) traz a tabela de segurança de migrations. Esta trilha ordena migrations dentro de um deploy.
- Instalar e administrar um servidor de CI, escrever actions em JavaScript ou em contêiner Docker e publicar apps móveis em lojas.

## O arco

Dez etapas, do que CI e CD prometem até o julgamento para revisar o pipeline de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Para que servem CI e CD | 0001 a 0002 | Integração, entrega e deployment como promessas, trabalho trunk-based, pipelines como código, os equivalentes em Jenkins e GitLab | Consegue dizer o que um pipeline garante e ler qualquer arquivo de workflow como código |
| 2. Anatomia de um workflow | 0003 a 0005 | Eventos e filtros, jobs, steps, runners, `needs`, actions, expressões, contextos e outputs | Consegue escrever um workflow que roda quando deveria e passa dados entre jobs |
| 3. Feedback rápido e confiável | 0006 a 0010 | Ordem das etapas, service containers, matrizes, cache, testes flaky, o caminho crítico, concorrência e timeouts | Consegue rodar um pipeline em que as pessoas confiam e pelo qual esperam |
| 4. Artefatos e versionamento | 0011 a 0013 | Artefatos contra caches, identidade do build, build único, construir e publicar uma imagem pelo digest | Consegue produzir um único artefato rastreável e entregar esse mesmo artefato a toda etapa posterior |
| 5. Secrets e confiança | 0014 a 0016 | Secrets, mascaramento, permissões do `GITHUB_TOKEN`, federação OIDC, injeção de script, `pull_request_target` | Consegue dar a um pipeline só o acesso de que ele precisa e manter entrada não confiável longe dele |
| 6. Environments e promoção | 0017 a 0018 | Environments, regras de proteção, secrets de environment, promover um único artefato com configuração por ambiente | Consegue controlar um deploy em produção e promover o que staging testou |
| 7. Deploy e rollback | 0019 a 0022 | Recreate, rolling, blue-green e canary, rollback, roll forward e flags, migrations expand and contract, deploys por push e GitOps | Consegue fazer deploy com uma estratégia que limita o estrago e desfazer um release ruim |
| 8. Cadeia de suprimentos | 0023 a 0024 | Fixar actions e dependências, Dependabot, proveniência SLSA, atestações de artefatos, SBOMs | Consegue dizer o que o pipeline executou e provar de onde um artefato veio |
| 9. Pipelines em escala | 0025 a 0027 | Reusable workflows, composite actions, filtros de caminho e checks obrigatórios em monorepos, logs de depuração, diferenças de runner | Consegue compartilhar lógica de pipeline entre times e descobrir por que uma execução falhou |
| 10. Julgamento | 0028 a 0030 | Revisar um pipeline, mudar um workflow compartilhado ou um check obrigatório, quando a resposta de sempre está errada, resolver isso pela referência de sintaxe de workflow | Tem a confiança para tomar a decisão sobre um pipeline e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-ci-and-cd-promise.md) | O que CI e CD prometem | A integração contínua mantém toda mudança mergeada e provada na main, a entrega contínua mantém a main pronta para release e o deployment contínuo publica toda mudança que passa |
| [0002](lessons/0002-pipelines-as-code.md) | Pipelines como código | Um arquivo de workflow no repositório é versionado, revisado e executado como o código que ele constrói, e Jenkins e GitLab expressam a mesma ideia |
| [0003](lessons/0003-triggers-and-events.md) | Gatilhos e eventos | Iniciar um workflow em um push, um pull request, um agendamento ou à mão, filtrá-lo por branch e caminho e saber contra qual commit cada evento roda |
| [0004](lessons/0004-jobs-steps-and-runners.md) | Jobs, steps e runners | Jobs rodam em paralelo em runners novos a menos que needs os ordene, steps compartilham um único workspace, e runners hospedados e self-hosted trocam custo por controle |
| [0005](lessons/0005-actions-expressions-and-outputs.md) | Actions, expressões e outputs | Reutilizar uma action com uses, decidir com if e expressões sobre contextos e passar valores entre steps e jobs por meio de outputs |
| [0006](lessons/0006-build-and-test-stages.md) | Etapas de build e de teste | Ordenar as etapas de lint, build, testes unitários e de integração para que a falha mais barata venha primeiro, com service containers para os testes que precisam de um banco de dados |
| [0007](lessons/0007-matrix-builds.md) | Builds em matriz | Rodar um job em várias versões e plataformas com uma matriz e controlar o que fail-fast, include e exclude fazem com a execução |
| [0008](lessons/0008-caching.md) | Cache | Basear a chave de um cache no lockfile, recorrer às restore keys como fallback e saber o que nunca se deve confiar a um cache |
| [0009](lessons/0009-flaky-tests.md) | Testes flaky | Um teste que falha sem mudança de código destrói a confiança no pipeline inteiro, então encontre a causa e coloque-o em quarentena em vez de escondê-lo atrás de retries |
| [0010](lessons/0010-making-a-pipeline-fast.md) | Tornando um pipeline rápido | Encurtar o caminho crítico, cancelar execuções superadas com grupos de concorrência e definir timeouts para que um job travado não segure a fila |
| [0011](lessons/0011-artifacts.md) | Artefatos | Passar uma saída de build entre jobs e mantê-la depois da execução com artefatos, e por que um artefato não é um cache |
| [0012](lessons/0012-versioning-a-build.md) | Versionando um build | Dar a todo build uma identidade rastreável até seu commit e construí-lo uma única vez, para que o que foi testado seja o que foi publicado |
| [0013](lessons/0013-building-and-publishing-an-image.md) | Construindo e publicando uma imagem | Construir, taguear e enviar uma imagem de contêiner a partir de um workflow, fazer cache das camadas e entregar o digest às etapas posteriores |
| [0014](lessons/0014-secrets-and-the-github-token.md) | Secrets e o GITHUB_TOKEN | Guardar secrets por repositório e por environment, saber o que o mascaramento deixa passar e reduzir o GITHUB_TOKEN com permissions |
| [0015](lessons/0015-oidc-instead-of-long-lived-keys.md) | OIDC em vez de chaves de longa duração | Deixar uma nuvem confiar em um token de curta duração emitido para uma execução e restringir essa confiança com a claim subject |
| [0016](lessons/0016-untrusted-input.md) | Entrada não confiável | Títulos, nomes de branch e código de fork são entrada do atacante, e pull_request_target com um checkout do fork entrega a eles os seus secrets |
| [0017](lessons/0017-environments-and-approvals.md) | Environments e aprovações | Controlar um deploy com environments, revisores obrigatórios, regras de branch de deployment e secrets de environment |
| [0018](lessons/0018-promotion-between-environments.md) | Promoção entre ambientes | Mover um único artefato construído de staging para produção pelo digest, com a configuração fornecida por ambiente |
| [0019](lessons/0019-deployment-strategies.md) | Estratégias de deployment | Recreate, rolling, blue-green e canary, o que cada uma custa em capacidade e risco, e o que um canary precisa medir para significar alguma coisa |
| [0020](lessons/0020-rollback-and-roll-forward.md) | Rollback e roll forward | Fazer rollback reimplantando o último artefato bom, fazer roll forward quando os dados já mudaram e separar deploy de release com flags |
| [0021](lessons/0021-database-migrations-in-a-deploy.md) | Migrations de banco de dados em um deploy | Ordenar mudanças de schema em torno do código com expand and contract, para que toda versão em execução durante um deploy funcione com o schema |
| [0022](lessons/0022-push-deploys-and-gitops.md) | Deploys por push e GitOps | Um pipeline que faz push para um cluster contra um agente no cluster que faz pull do Git, e o que cada um faz com credenciais e drift |
| [0023](lessons/0023-pinning-what-the-pipeline-runs.md) | Fixando o que o pipeline executa | Fixar actions de terceiros em um SHA de commit completo, travar dependências e manter as fixações atualizadas com o Dependabot |
| [0024](lessons/0024-provenance-and-sboms.md) | Proveniência e SBOMs | Atestar onde e a partir de quê um artefato foi construído, listar o que há dentro dele e verificar os dois antes que ele rode |
| [0025](lessons/0025-reusable-workflows-and-composite-actions.md) | Reusable workflows e composite actions | Compartilhar lógica de pipeline entre repositórios com um workflow chamado ou uma composite action, e escolher pelo que cada um pode conter |
| [0026](lessons/0026-monorepos-and-path-filters.md) | Monorepos e filtros de caminho | Rodar só o que uma mudança toca com filtros de caminho, e por que um check obrigatório ignorado pode bloquear todo merge |
| [0027](lessons/0027-debugging-a-pipeline.md) | Depurando um pipeline | Ler o log, reexecutar com log de depuração e encontrar o que difere entre o runner e a sua máquina quando passa localmente |
| [0028](lessons/0028-reviewing-a-pipeline.md) | Revisando um pipeline | Revisar o workflow de outra pessoa nomeando o que vai falhar, ficar lento ou vazar primeiro |
| [0029](lessons/0029-changing-a-shared-workflow.md) | Mudando um workflow compartilhado | Mudar um reusable workflow ou um check obrigatório do qual outros times dependem sem quebrar os merges deles |
| [0030](lessons/0030-when-the-usual-answer-is-wrong.md) | Quando a resposta de sempre está errada | Dizer quando o deployment contínuo, um canary ou um padrão do pipeline é a decisão errada, e resolver um comportamento em disputa pela referência de sintaxe de workflow |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Sintaxe de workflow](reference/workflow-syntax.md): gatilhos, jobs, steps, expressões, contextos e outputs, com os equivalentes em Jenkins e GitLab, das etapas 1 e 2
- [Feedback rápido](reference/fast-feedback.md): ordem das etapas, matrizes, chaves de cache, tratamento de testes flaky, concorrência e timeouts, da etapa 3
- [Artefatos e versionamento](reference/artifacts-and-versioning.md): artefatos contra caches, esquemas de versão, build único, tags e digests de imagem, da etapa 4
- [Segurança de pipeline](reference/pipeline-security.md): secrets, permissões de token, OIDC, entrada não confiável, fixação e proveniência, das etapas 5 e 8
- [Deployments](reference/deployments.md): environments, promoção, as quatro estratégias, rollback, ordem das migrations e GitOps, das etapas 6 e 7
- [Pipelines em escala](reference/pipelines-at-scale.md): reusable workflows contra composite actions, filtros de caminho, checks obrigatórios e depuração de uma execução, da etapa 9
- [Checklist de revisão de pipeline](reference/pipeline-review-checklist.md): as perguntas a fazer sobre o pipeline de outra pessoa, e quando a resposta de sempre está errada, da etapa 10

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
