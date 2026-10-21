---
title: "19. Revisando um relatório de eval"
description: "Nomeie especificamente o que tornaria pouco confiável o número de um relatório de eval (contaminação, um juiz não calibrado, uma execução única sem estimativa de variância, uma posição em leaderboard fazendo o papel de uma decisão específica da tarefa), em vez de dizer que ele parece fraco"
type: lesson
---

# Lição 19. Revisando um relatório de eval

**Ligação com a missão:** Toda habilidade deste arco leva a uma coisa: um número que você possa defender pessoalmente. Esta lição é a habilidade complementar: revisar o número de outra pessoa e dizer, de forma específica e a partir do material, o que o tornaria pouco confiável, em vez de apenas sentir que está incompleto. Uma suíte de evals, depois de construída, é infraestrutura compartilhada: outras equipes condicionam lançamentos ao número dela, e trocar um juiz, um limiar ou uma métrica invalida em silêncio decisões já tomadas. Revisar e manter uma com honestidade é um julgamento de nível sênior.
**Fonte principal:** [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Pré-requisitos:** [Lição 6](0006-judge-bias-and-human-agreement.md), [Lição 9](0009-statistical-significance-vs-noise.md), [Lição 10](0010-defending-the-go-no-go-call.md), [Lição 18](0018-public-benchmarks.md)

## Aquecimento

1. ▢ O que significa um juiz estar calibrado, e que falha específica a lição 5 descreve como compressão da pontuação?

<details markdown="1"><summary>Verificação</summary>

As pontuações de um juiz calibrado acompanham a qualidade real de forma consistente entre os exemplos. A compressão da pontuação em direção ao teto é uma falha em que o juiz avalia quase tudo com notas altas, independentemente das diferenças reais de qualidade, apagando as distinções que um eval existe para pegar.

</details>

2. ▢ Qual é a conclusão honesta quando uma diferença de pontuação de eval cai dentro do ruído estimado, e quais são duas formas de obter uma resposta mais clara?

<details markdown="1"><summary>Verificação</summary>

A conclusão honesta não é "nenhuma diferença", e sim "ainda não há evidência suficiente para dizer". Duas formas de esclarecer: executar o eval em mais exemplos (encolhendo o erro padrão) ou executar um teste de significância pareado adequado sobre os exemplos específicos em que as variantes discordam.

</details>

3. ▢ Uma posição em leaderboard agrega preferências sobre quais três coisas que podem não corresponder à sua tarefa real?

<details markdown="1"><summary>Verificação</summary>

Usuários, tarefas e casos de uso que não são os seus. Uma posição em leaderboard pode ser um primeiro filtro razoável para saber quais modelos avaliar mais a fundo, mas falha no teste do OEC que a lição 15 estabeleceu porque não é causalmente ligada à sua decisão específica.

</details>

## Saiba isto

### O checklist de revisão: o que torna um número pouco confiável

Quando alguém apresenta um relatório de eval ou o design de um harness, percorra estas perguntas em ordem. Onde o relatório não tem resposta, você encontrou a lacuna que torna o número pouco confiável, de forma específica e nomeada.

**Etapas 1-2: O conjunto held-out é de fato held-out?**

Pergunte: que evidência existe de que os dados do eval são held-out? A equipe verificou a contaminação com as técnicas que a lição 2 ensinou (canary strings, testes de adivinhar o resto da instância, ou ambos)? Se o relatório diz "os dados vêm de um benchmark público", ele também deveria informar se a saturação (desempenho no teto sem melhoria real) ou a contaminação desse benchmark já está documentada por aí. Se nem a verificação de contaminação nem evidência de saturação são reportadas, o número pode estar inflado porque o modelo simplesmente viu as perguntas antes no treinamento ou memorizou um benchmark muito ajustado em vez de aprender a habilidade de fundo.

**Etapa 2: A métrica de fato se encaixa na tarefa?**

Pergunte: por que esta métrica está sendo usada para esta tarefa? Se o relatório diz "acurácia", essa é a métrica certa (a lição 3 cobre os modos de falha de cada métrica), ou o F1, o BLEU, a execução de código ou outra coisa mediria de fato o que importa? Se uma métrica customizada foi construída, qual é a evidência de que ela se correlaciona com o resultado real (por exemplo, preferência humana, sucesso na tarefa)? Um relatório que não justifica sua escolha de métrica fez um palpite disfarçado de decisão.

**Etapas 3 e 6: Se um juiz LLM é usado, ele é de fato confiável?**

Pergunte três coisas:

- **Design:** qual é o prompt do juiz, e o que a equipe fez para calibrá-lo antes de executá-lo em escala? O prompt dá ao juiz uma resposta de referência quando há uma disponível? A lição 5 ensina a calibração; se o relatório não a menciona, o juiz pode estar sofrendo de compressão da pontuação ou de outros modos de falha de descalibração.
- **Verificações de viés:** o juiz foi verificado quanto ao viés de posição (a mesma comparação pairwise se inverte se você trocar a ordem)? O viés de verbosidade foi verificado (o juiz prefere o comprimento independentemente da correção)? A lição 6 cobre esses vieses; se o relatório não menciona tê-los verificado, eles podem estar inflando ou desinflando os números em silêncio.
- **Concordância humana:** qual é a taxa de concordância do juiz com avaliadores humanos em uma amostra, e qual é a concordância humano-humano na mesma amostra? Um juiz com 82% de concordância soa fraco até você saber que os avaliadores humanos concordam 80% entre si, caso em que o juiz está se saindo mais ou menos tão bem quanto outro humano se sairia. Um relatório que alega um juiz LLM sem medi-lo contra o julgamento humano está alegando um atalho sem evidência de que funciona.

**Etapas 5 e 9-10: O número é sustentado por variância, ou é uma execução só?**

Pergunte: quantas vezes o eval foi executado, e qual foi a dispersão? Se é um número de uma execução com temperatura diferente de zero, o ruído nesse número (o erro padrão da lição 9) é invisível. A equipe mediu um erro padrão ou executou um teste de significância para confirmar que a diferença observada é claramente maior que o ruído? Se uma melhoria é reportada sem estimativa de significância, não há como saber se é uma vitória real ou uma coincidência estatística. Verifique também se o limiar foi definido antes de o eval rodar ou depois, e se ele respeita o piso de ruído: a lição 10 ensina que um limiar mais apertado do que o eval consegue de fato resolver é um cara ou coroa disfarçado de decisão.

**Etapa 11: Ele leva em conta custo e latência?**

Pergunte: a melhoria reportada é ponderada contra o que custa servi-la? Custo por requisição e custo por token para modelos com divisão diferente entre entrada e saída: isso é mencionado, e o ganho de qualidade de fato vale esse multiplicador? Se a latência foi medida, foi a latência de cauda (p95/p99) ou só uma média? A lição 17 ensina por que uma média inalterada pode esconder uma cauda sensivelmente pior. Se o relatório diz "a qualidade melhorou" sem custo nem latência, falta metade da decisão de go/no-go.

**Etapa 12: Ele se apoia em um leaderboard em vez de um número específico da tarefa?**

Pergunte: o relatório diz "este modelo está na posição X no MMLU" ou "este modelo pontua X no nosso eval específico da tarefa"? Se ele se apoia em um benchmark público ou em uma posição de leaderboard como evidência, a lição 18 estabelece que uma posição em leaderboard falha no teste de que um OEC de verdade precisa: ela não é causalmente ligada à sua decisão específica e carrega vetores de manipulação documentados (divulgação seletiva, viés de estilo). Uma decisão de go/no-go específica da tarefa não substitui uma checagem de leaderboard, mas uma posição em leaderboard também não substitui um número específico da tarefa.

### A habilidade específica: resolver se um juiz LLM pode substituir uma decisão de go/no-go específica da tarefa

Este workspace apresentou dois relatos críveis sobre juízes LLM. As lições 5 e 6 ensinaram como construir e calibrar um, considerando-os úteis para tarefas abertas quando construídos com cuidado. Mas uma pergunta legítima paira sobre toda a ideia: um juiz LLM é alguma vez confiável o bastante para substituir um eval específico da tarefa, ou fica fundamentalmente limitado à triagem prévia ou à verificação de correlação?

O artigo de Zheng et al. de 2023, "Judging LLM-as-a-Judge", estabelece que juízes LLM conseguem medir bem as preferências humanas em tarefas abertas (no Chatbot Arena, a preferência pairwise de um juiz coincide com as preferências humanas cerca de 80% das vezes), e que isso é bom o bastante para uso prático, mas *só* quando você verifica e corrige os vieses conhecidos (posição, verbosidade, autopreferência) e só quando mede o juiz contra a concordância humana, e não contra um padrão perfeito imaginado.

Eis o movimento que um revisor precisa fazer quando essa pergunta aparece em uma conversa real. Duas pessoas, ambas citando fontes plausíveis, discordam:

**O engenheiro A diz:** "Zheng et al. mostraram que os juízes funcionam; podemos usar um juiz LLM para a nossa decisão de go/no-go."

**O engenheiro B diz:** "Sim, mas Zheng também mostrou que os juízes têm vieses; uma métrica específica da tarefa seria mais honesta."

Os dois citam o mesmo artigo. A diferença está no que cada um extrai dele.

O movimento certo não é escolher um lado por impressão, nem dividir a diferença de modo vago ("às vezes os juízes funcionam, use seu julgamento"). O movimento certo é voltar ao artigo e verificar se as condições em que os achados de Zheng valem correspondem à sua situação real:

**As condições de Zheng:** os juízes se saíram melhor em comparações de preferência pairwise para tarefas abertas (escrita, raciocínio, criatividade). A comparação foi pairwise, e não pontual (não uma avaliação em escala de 1 a 10). Os avaliadores humanos na mesma tarefa estavam eles mesmos em cerca de 80% de concordância entre si. O juiz foi verificado quanto a vários vieses e correções foram aplicadas. O veredito foi usado como filtro ou sinal, e não como uma decisão final de go/no-go sem revisão.

**Agora, a sua situação:** sua tarefa é aberta, ou tem uma resposta certa nítida? Você está avaliando em pairwise ou em escala numérica? Você mediu a concordância humana nesta tarefa e, se sim, qual é ela? Você verificou o juiz quanto a viés de posição, de verbosidade e de autopreferência, e tem um plano para corrigi-los se encontrados? A saída desse juiz é revisada por um humano antes de conduzir uma decisão, ou fica sozinha?

Se a sua situação corresponde de perto às condições de Zheng, o achado de que "os juízes funcionam quando construídos com cuidado" se aplica de modo mais direto. Se a sua tarefa é nítida, ou se você não mediu a concordância humana nela, ou se a saída do juiz conduz a decisão sem revisão, o peso da evidência muda. A habilidade não é "lembrar o que Zheng diz", e sim "verificar se as condições que tornaram aquele achado verdadeiro se aplicam ao que você está construindo".

### Como soa um bom julgamento ao revisar um relatório de eval

> "O relatório alega uma melhoria de 5 pontos no eval específico da tarefa deles com um juiz LLM, mas não diz quantas execuções foram feitas nem qual é o erro padrão em um conjunto de 100 exemplos com baseline de 70%; isso provavelmente é 4 a 5 pontos de ruído, o que significa que essa diferença pode ser real ou pode não ser. Eles também não mencionaram ter verificado o juiz quanto a viés de posição ou de verbosidade, e não citam a concordância humana nas mesmas amostras. Antes de lançarmos com base nesse número, precisamos do erro padrão calculado, de uma verificação de viés no juiz e da medição contra a concordância humana em uma amostra da tarefa. Ou, se a tarefa for nítida o bastante, eles deveriam ter usado uma métrica específica da tarefa em vez de um juiz logo de início."

Nada disso é um fato que você consultou. É o formato do ceticismo para o qual este workspace existiu.

### Mantendo uma suíte de evals de que outros dependem

Depois que você construiu um eval, e outras equipes condicionam lançamentos ao número dele, o eval vira infraestrutura compartilhada. Mudar o juiz, a métrica, o limiar ou o formato do dataset invalida em silêncio decisões já tomadas sobre a versão antiga. Uma equipe que lançou com base em "a versão 1.0 do eval mostrou melhoria de 3 pontos" tomou uma decisão ligada a esse eval específico. Se você trocar o juiz e executar a versão 2.0 do eval, uma melhoria de 2 pontos não é comparável: a equipe se apoiou no número da versão 1.0, e não da 2.0.

Quando você precisar mudar uma suíte de evals:

**Opção 1: Execute o antigo e o novo lado a lado.** Antes de fazer a troca, meça uma amostra razoável de mudanças recentes de modelo contra o juiz/métrica/versão antigos e contra os novos. Isso dá às outras equipes um fator de conversão e mostra o impacto. Um relatório dizendo "trocar de juiz muda a pontuação em cerca de 2 pontos em média entre estes modelos" é honesto e acionável; trocar em silêncio é uma mudança que quebra compatibilidade.

**Opção 2: Versione o eval formalmente.** Se você está lançando o eval 2.0 com um juiz, uma métrica ou um limiar diferente, versione-o com clareza. As outras equipes podem continuar executando a 1.0 até estarem prontas para migrar. Documente o que mudou e por quê. É assim que as ferramentas estáveis fazem.

**Opção 3: Não mude aquilo de que outros dependem sem comunicação.** Se uma mudança é necessária (o juiz antigo está comprovadamente quebrado, uma métrica deixou de ser apropriada), anuncie-a. Dê tempo às equipes para reavaliar suas últimas decisões de lançamento sob as duas versões. Uma mudança surpresa no que um eval significa é como se perde a confiança nos evals por completo.

## Prática

1. ▢ Uma equipe reporta que um modelo melhorou 6 pontos no eval dela, com um juiz LLM pontuando comparações pairwise. O relatório não menciona quantos exemplos há no eval nem se o juiz foi conferido contra a concordância humana. O que você deve perguntar?

<details markdown="1"><summary>Verificação</summary>

Em que tamanho de conjunto de eval? O erro padrão em um conjunto de 100 exemplos com uma baseline típica é de 4 a 5 pontos; uma diferença de 6 pontos pode ser real ou pode ser ruído. Vocês mediram a concordância do juiz com avaliadores humanos em uma amostra da sua tarefa? Sem saber a concordância humano-humano, você não consegue dizer se uma concordância juiz-humano de 80% é boa ou medíocre. Além disso: o juiz foi verificado quanto a viés de posição (ordem trocada) e viés de verbosidade? Sem essas verificações, a melhoria pode ser um artefato de como o juiz foi instruído.

</details>

2. ▢ Uma equipe diz "usamos um juiz LLM porque Zheng et al. mostraram que os juízes funcionam". Mas ela não mediu a concordância humana na própria tarefa e está usando pontuação pontual (escala de 1 a 10), e não pairwise. O achado de Zheng se aplica diretamente à situação dela?

<details markdown="1"><summary>Verificação</summary>

Não diretamente. Os achados de Zheng valeram para comparações de preferência pairwise em tarefas abertas em que os próprios avaliadores humanos estavam em 80% de concordância. A pontuação pontual é outro modo (mais sujeito a problemas de interpretação de escala), e sem medir a concordância humana nesta tarefa específica, você não sabe que baseline esperar do juiz. A equipe deveria medir a concordância humana na tarefa e comparar o juiz contra ela, ou trocar para uma métrica específica da tarefa se a tarefa permitir uma.

</details>

3. ▢ Sua suíte de evals roda há seis meses, e outras equipes condicionam lançamentos a ela. Você quer trocar para um juiz diferente e mais bem calibrado porque o atual tem compressão da pontuação. O que fazer antes de fazer a mudança?

<details markdown="1"><summary>Verificação</summary>

Execute o juiz antigo e o novo lado a lado em uma amostra de mudanças recentes de modelo. Mostre às outras equipes o que a troca de juiz faz com as pontuações em que elas vêm se apoiando. Se for um deslocamento de 2 pontos em média, elas podem recalibrar; se for um deslocamento de 10 pontos, precisam reavaliar decisões recentes. Anuncie a mudança com clareza e considere versionar o eval (eval 1.0 com o juiz antigo, eval 2.0 com o novo) para que as outras equipes migrem no próprio ritmo em vez de serem surpreendidas por uma mudança que quebra compatibilidade.

</details>

4. ▢ Um engenheiro revisando um relatório de eval diz: "O relatório alega uma melhoria de 4 pontos sem nenhum teste de significância reportado. O conjunto de eval tem 50 exemplos, e a baseline é 68%. Devemos confiar nesse número?" Qual é a sua análise?

<details markdown="1"><summary>Verificação</summary>

Não sem mais informação. Com N=50 e p=0,68, o erro padrão é de aproximadamente `sqrt(0.68 × 0.32 / 50) ≈ 0.066`, ou cerca de 6,6 pontos percentuais. Uma diferença de 4 pontos está bem dentro do ruído; não é claramente maior do que a amostragem sozinha poderia produzir. A equipe deveria executar mais exemplos (encolhendo o erro padrão) ou executar um teste de significância pareado nos exemplos específicos em que há discordância, e não apenas reportar a diferença bruta e esperar que ela pareça convincente.

</details>

5. ▢ Qual situação o deixaria mais cético quanto a um relatório de eval que alega uma melhoria?

    - a) O eval usa uma métrica específica da tarefa, executou 500 exemplos e reporta uma melhoria de 3 pontos com um teste de significância pareado mostrando p < 0,05
    - b) O eval usa um juiz LLM, executou 100 exemplos, reporta uma melhoria de 4 pontos, mas não menciona se o juiz foi verificado quanto a viés de posição nem se a concordância humana foi medida
    - c) O eval reporta uma posição de ranking no MMLU como principal evidência de melhoria
    - d) O eval incluiu custo e latência junto com a qualidade na decisão de go/no-go

<details markdown="1"><summary>Verificação</summary>

**b)** e **c)** são sinais de alerta. (b) está incompleta: sem verificações de viés nem medição de concordância humana, não dá para saber se o juiz é confiável. (c) é uma falha em medir o que importa: uma posição em leaderboard não é um sinal de go/no-go específico da tarefa. (a) acerta todas as notas: uma métrica específica da tarefa, amostra grande, teste de significância. (d) é boa prática, e não motivo para ceticismo. O sinal de alerta mais cético é um relatório que não responde às perguntas que esta lição ensina a fazer.

</details>

## Prática no mundo real

- [ ] Encontre um relatório de eval do seu próprio trabalho ou de um colega. Execute contra ele o checklist de revisão desta lição. Anote quais itens do checklist o relatório trata com clareza e quais deixa em silêncio. Compartilhe a lista com o autor do relatório.
- [ ] Sobre a pergunta "um juiz LLM pode substituir um eval específico da tarefa", releia você mesmo o artigo de Zheng et al. e identifique as condições específicas em que os achados deles valeram. Anote: que características de tarefa, tamanhos de amostra e práticas de medição eles usaram? Como você testaria se essas condições se aplicam a uma nova situação?
- [ ] Amanhã: proponha uma mudança em uma suíte de evals que você mantém ou conhece. Anote como você comunicaria essa mudança às outras equipes que condicionam lançamentos a ela, e se você executaria o antigo e o novo lado a lado, versionaria formalmente, ou os dois.

## Para ir além

- [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Lição 6: Viés do juiz e concordância com humanos](0006-judge-bias-and-human-agreement.md), para os vieses a verificar
- [Lição 10: Defendendo a decisão de go/no-go](0010-defending-the-go-no-go-call.md), para o que uma defesa completa precisa citar
- [Lição 18: Benchmarks públicos](0018-public-benchmarks.md), para saber por que uma posição em leaderboard não substitui uma decisão específica da tarefa
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
