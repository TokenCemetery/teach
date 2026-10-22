---
title: "30. Avaliando um agente"
description: "Medir o sucesso do agente no nível do resultado contra o nível da trajetória, e por que uma única execução bem-sucedida não significa que o agente é confiável"
type: lesson
---

# Lição 30. Avaliando um agente

**Ligação com a missão:** Diagnosticar um agente que falha a partir da trajetória, nomeando a causa (um loop, contexto envenenado, uma ferramenta mal especificada, uma condição de parada errada) em vez de refazer o prompt ao acaso.
**Fonte principal:** [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
**Pré-requisitos:** [Lição 29](0029-tracing-and-trajectory-replay.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 29: Quando você lê a trajetória de um agente para diagnosticar uma falha, que duas coisas deve procurar primeiro: a decisão que o modelo tomou ou o resultado real que essa decisão produziu?

<details markdown="1"><summary>Verificação</summary>

As duas, mas nesta ordem: primeiro, a decisão que o modelo tomou em cada passo (qual ferramenta escolheu, que argumentos passou). Segundo, o que a ferramenta de fato devolveu. Uma decisão razoável com um resultado errado aponta para um problema na implementação da ferramenta. Uma decisão não razoável com um resultado razoável aponta para uma falha de raciocínio. Misturá-las é onde o diagnóstico trava.

</details>

2. ▢ Da Lição 29: Se uma trajetória mostra o modelo tomando a decisão certa cinco vezes seguidas mas o agente não consegue concluir a tarefa, o que esse padrão sugere estar quebrado?

<details markdown="1"><summary>Verificação</summary>

Sugere que o harness ou as próprias implementações das ferramentas estão quebrados, e não o raciocínio do modelo. O modelo está escolhendo corretamente, mas algo mais no loop não está sendo executado como pretendido. Pode ser uma ferramenta que afirma sucesso mas não executa de fato a ação, um harness que corta o loop cedo demais ou um resultado sendo anexado à transcrição de forma incorreta.

</details>

## Saiba isto

### Resultado contra trajetória

Ao avaliar um agente, você pode medir duas coisas diferentes, e elas não são a mesma.

**Sucesso no resultado** significa: O agente chegou ao estado final correto? O arquivo foi atualizado corretamente. O ticket foi triado na categoria certa. A pergunta do usuário foi respondida com precisão. Você confere o resultado inspecionando o que o usuário vê.

**Correção da trajetória** significa: O agente seguiu a sequência certa de passos para chegar lá? Ele chamou as ferramentas certas na ordem certa com argumentos sensatos, interpretou os resultados com precisão e evitou loops circulares.

Uma tarefa de agente muitas vezes tem muitos caminhos válidos até o mesmo resultado correto. Avaliar contra uma única trajetória de referência costuma estar errado; avaliar o resultado (o arquivo foi de fato atualizado, o ticket foi de fato triado corretamente) costuma estar certo. No entanto, a trajetória ainda importa: é como você diagnostica *por que* algo falhou, que é o que as lições 27 a 29 desta trilha ensinam. O resultado diz se o agente teve sucesso; a trajetória diz por que ele falhou.

### pass^k: confiabilidade em tentativas repetidas

Uma única execução bem-sucedida não diz que o agente é confiável. O mesmo agente na mesma tarefa pode falhar em uma segunda tentativa devido à natureza estocástica dos muitos pontos de decisão de um agente se acumulando ao longo de uma trajetória longa. O pass^k mede a probabilidade de o agente ter sucesso em todas as k tentativas independentes da mesma tarefa. Se um agente passa 8 de 10 vezes em uma tarefa, você sabe mais do que se ele tivesse passado uma vez: tem evidência de que ele é cerca de 80 por cento confiável nessa tarefa. Não confunda isso com acurácia da tarefa; é uma barra de confiabilidade muito mais forte e mais honesta do que uma única execução com passou ou falhou. Para o tratamento completo de como projetar e calcular o pass^k em suas próprias avaliações, veja a lição que vem depois desta.

### O que os papers de benchmark realmente medem

Três papers ancoram as fontes desta etapa, e cada um representa uma escolha diferente de como avaliar agentes:

**tau-bench** (Yao et al., 2024) avalia o uso de ferramentas em vários turnos contra um usuário simulado (um modelo de linguagem agindo como pessoa) e uma política de domínio (regras sobre o que constitui sucesso). Usa medidas de confiabilidade com tentativas repetidas, então você vê pontuações pass^k, e não resultados de uma única tentativa.

**SWE-bench** (Jimenez et al., 2023) avalia agentes em issues reais de repositórios com a suíte de testes do próprio projeto como verificação do resultado. Se os testes passam, o agente resolveu a issue. A trajetória não é restringida nem avaliada; apenas o resultado importa.

**GAIA** (Mialon et al., 2023) propõe perguntas fáceis para uma pessoa e difíceis para um agente, que exigem uso de ferramentas em vários passos para chegar a uma resposta inequívoca. Mede se o agente chega à resposta certa, e não se o raciocínio dele foi elegante.

Os três priorizam o sucesso no resultado em vez da elegância da trajetória, e os três usam avaliação com tentativas repetidas ou vários casos de teste para ir além da sorte de uma única execução.

### A passagem para a profundidade

Esta lição dá o vocabulário: resultado contra trajetória, pass^k, sucesso da tarefa. O tratamento completo de construir uma avaliação de agente está na trilha llm/evals, lição 13, Avaliando agentes e uso de ferramentas. Essa lição cobre métricas, design de juiz, como construir um conjunto de teste reservado, o que significa significância estatística e como evitar avaliar sem querer a coisa errada. O papel desta trilha é apenas garantir que você saiba o que medir logo de início. Leia esta lição para conhecer os conceitos; leia llm/evals lição 13 para a profundidade.

## Prática

1. ▢ Um agente registra com sucesso um ticket no seu rastreador de issues na primeira tentativa. Você o roda de novo em um ticket diferente, e ele falha em silêncio, criando um ticket vazio sem texto. Você o roda uma terceira vez e ele tem sucesso. O agente está pronto para produção com base nesses dados?

<details markdown="1"><summary>Verificação</summary>

Não. Você tem um sucesso, uma falha e outro sucesso. São 2 sucessos em 3 tentativas, sugerindo cerca de 67 por cento de confiabilidade. Você ainda não tem dados suficientes, e 67 por cento é baixo demais para a maior parte dos usos em produção. Você precisa de pelo menos 10 a 20 tentativas em tickets diversos para estabelecer um pass^k confiável. O instinto errado é presumir que a única falha foi um acaso e que o agente está bem; o certo é levar o pass^k a sério.

</details>

2. ▢ Você está diagnosticando um agente que falhou ao atualizar um registro de banco de dados. Você olha a trajetória e vê que o modelo escolheu a ferramenta update_record certa, com o ID de registro correto e os novos valores. A ferramenta devolveu sucesso: "ok, record updated". Mas, quando você confere o banco de dados, o registro não foi de fato atualizado. Em que nível você deve olhar para corrigir isso?

<details markdown="1"><summary>Dica</summary>

A decisão do modelo e a trajetória parecem ambas corretas. O problema não está no raciocínio nem na tomada de decisão.

</details>

<details markdown="1"><summary>Verificação</summary>

Você deve inspecionar a própria implementação da ferramenta. A trajetória mostra que o modelo fez a escolha certa e que a ferramenta afirmou sucesso, mas o resultado está errado. Algo entre o valor de retorno da ferramenta e o estado real do banco de dados está quebrado. Pode ser uma ferramenta que registra sucesso em log mas não executa de fato, um harness que não espera a ferramenta terminar ou um problema de conexão com o banco. O diagnóstico de trajetória aqui significa olhar além das palavras que a ferramenta devolveu e conferir o que de fato aconteceu.

</details>

3. ▢ Você está avaliando agentes com o SWE-bench (issues reais do GitHub, suítes de testes do projeto como verificação do resultado). A trajetória de um agente mostra que ele tomou uma decisão que você acha que não é ótima, gastando chamadas de ferramenta extras em comparação com um caminho mais direto. Mas a suíte de testes da issue passa. Você deve diminuir a pontuação do agente pela trajetória não ótima?

    - a) Sim, porque a trajetória mostra ineficiência
    - b) Não, porque apenas a suíte de testes passar importa no SWE-bench
    - c) Pontuar o resultado como aprovado mas sinalizar a trajetória para otimização futura
    - d) Apenas se o caminho não ótimo gastou mais tokens do que uma baseline

<details markdown="1"><summary>Verificação</summary>

**b)** Não, porque apenas a suíte de testes passar importa no SWE-bench. O SWE-bench foi projetado para avaliar resultados, e não trajetórias. Se os testes passam, o agente resolveu a issue, independentemente de ele ter tomado o caminho mais elegante. O instinto errado é avaliar a elegância da trajetória além do resultado; isso mistura duas avaliações separadas. **a)** o levaria a uma métrica que o SWE-bench não usa. **c)** acrescenta complexidade que o SWE-bench não exige para seu objetivo principal. **d)** introduz uma restrição separada (orçamento de tokens) que não faz parte do design do SWE-bench.

</details>

4. ▢ Você está avaliando um agente em uma tarefa apenas pelo resultado: ou ele chega ao estado final correto, ou não. Você o roda 100 vezes e ele tem sucesso 73 vezes. Você melhora o system prompt e testa de novo. Agora ele tem sucesso 75 vezes em 100. A melhoria é pequena. O que esse padrão sugere que você deve fazer em seguida?

<details markdown="1"><summary>Verificação</summary>

Sugere que melhorias de prompting sozinhas não bastam para tratar as falhas na raiz. O ganho de 73 para 75 por cento é modesto; a maioria das falhas persiste apesar de instruções melhores. Você deve ler as trajetórias das execuções que falharam para identificar o modo de falha real (uma ferramenta mal usada, um erro de lógica, um problema de contexto, um obstáculo que o agente não trata) e então corrigir esse problema específico. Alternativamente, a tarefa pode simplesmente ser difícil demais para o modelo ou o conjunto de ferramentas atuais, e nenhuma mudança de prompt ajudará. O diagnóstico de trajetória diz qual das duas é a verdade.

</details>

## Prática no mundo real

- [ ] Escolha uma tarefa de agente simples e repetível (por exemplo, "buscar uma pessoa em um diretório", "converter um formato de arquivo", "responder a uma pergunta factual usando uma ferramenta"). Rode o agente 10 vezes e registre passou ou falhou a cada vez. Calcule o pass^k empírico e anote o que esse número diz a você que uma única execução não diria.

- [ ] Pegue um paper de benchmark publicado sobre agentes (tau-bench, SWE-bench, GAIA, WebArena ou outro). Leia a seção de avaliação e identifique: qual é a métrica de resultado, a trajetória é restringida ou de forma livre e que medida de confiabilidade ele usa.

- [ ] Amanhã: Encontre a trajetória de um agente de uma fonte pública (documentação, blog, GitHub). Escreva uma rubrica de avaliação que avalia a trajetória apenas pelo resultado (o estado final bateu com o objetivo), e uma rubrica separada que avalia pela trajetória (ela tomou passos sensatos). Aplique as duas rubricas à mesma trajetória e compare as pontuações. Escreva um parágrafo sobre se o resultado ou a trajetória disse mais sobre o agente ter funcionado.

## Para ir além

- [Lição 13: Avaliando agentes e uso de ferramentas](../../evals/lessons/0013-evaluating-agents-and-tool-use.md)
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
