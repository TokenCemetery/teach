---
title: "18. A lacuna de imitação"
description: "Por que imitar um modelo mais forte copia o seu estilo muito mais rápido do que a sua capacidade"
type: lesson
---

# Lição 18. A lacuna de imitação

**Ligação com a missão:** A missão pede que você preveja o que um aluno vai e o que não vai absorver, e que revise uma alegação de "se iguala ao professor", o que significa saber como um aluno pode se parecer com o seu professor sem ter o que o professor sabe.
**Fonte principal:** [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), seções 1 e 4
**Pré-requisitos:** [Lição 10](0010-distilling-from-generated-data.md), [Lição 17](0017-fidelity-and-generalization.md), [Lacuna de imitação](../GLOSSARY.md), [Dados sintéticos](../GLOSSARY.md), [Fidelidade](../GLOSSARY.md)

## Aquecimento

1. ▢ O Alpaca e o Self-Instruct constroem um conjunto de treinamento de que maneira, e o que o aluno recebe do professor?

<details markdown="1"><summary>Verificação</summary>

Um modelo professor gera instruções e respostas, e o aluno passa por fine-tuning nesse texto. Ele recebe apenas o texto decodificado do professor, sem logits.

</details>

2. ▢ A lição 17 diz que a acurácia na tarefa não pode substituir a concordância com o professor. Qual é o risco inverso: um aluno pode concordar com o professor nas saídas e ainda assim não ter a sua capacidade?

<details markdown="1"><summary>Verificação</summary>

A concordância é medida nas entradas que você testa, então só fala por essas entradas. Um aluno pode igualar a redação do professor em pedidos comuns e falhar em tarefas que os dados de treinamento mal cobriram, que é o caso que esta lição examina.

</details>

3. ▢ A lição 12 diz que volume não corrige exemplos ruins. Cite uma coisa que mais dados gerados pelo professor não conseguem fornecer a um aluno.

<details markdown="1"><summary>Verificação</summary>

Conhecimento que o próprio pré-treinamento do aluno não lhe deu. Mais exemplos podem ensinar formato e comportamento, mas não conseguem compensar de forma barata o que o base model nunca aprendeu. Essa afirmação é o núcleo desta lição.

</details>

## Saiba isto

### O cenário

Gudibande et al. estudam a "imitação de modelos": coletar um dataset de saídas de um modelo proprietário por meio da sua API e fazer fine-tuning de um modelo aberto nele. Eles imitam o ChatGPT com modelos de 1,5B a 13B de parâmetros (GPT-2 1.5B, LLaMA 7B e 13B) e dados de imitação de 0,3M a 150M de tokens. O aluno vê apenas texto, então isso é destilação em nível de sequência sem logits.

Dois tipos de imitação importam para o argumento:

| Tipo | O que imita | Os dados deles |
|---|---|---|
| Imitação local | Uma tarefa ou domínio | NQ-synthetic: 6.000 pares de pergunta e resposta gerados pelo ChatGPT a partir de uma semente de 10 pares, no estilo do Natural Questions |
| Imitação ampla | Toda a gama de comportamento | ShareGPT-Mix: cerca de 50K diálogos deduplicados do ShareGPT, mais cerca de 27K respostas do ChatGPT do HC3 e 10K exemplos de bots de ChatGPT do Discord |

### O que os avaliadores humanos viram

Crowd workers fizeram comparações pareadas cegas de cada modelo de imitação contra o ChatGPT, com cerca de 70 trabalhadores em 255 prompts held-out. Cerca de 70% das saídas dos modelos de imitação foram avaliadas como iguais ou melhores do que as do ChatGPT (legenda da Figura 1). O GPT-4 como juiz mostrou as mesmas tendências. Segundo essas avaliações, os modelos de imitação pareciam próximos do modelo que copiavam.

As avaliações também saturaram: mais dados de imitação deixaram de elevá-las (seção 4.2).

### O que os benchmarks viram

Os autores então executaram avaliações automáticas direcionadas: MMLU (5-shot), Natural Questions (3-shot) e HumanEval (0-shot). Eles relatam que, em todos os benchmarks medidos, os modelos de imitação ampla não melhoraram em relação aos seus base models, ou pioraram, mesmo com o crescimento dos dados de imitação (seção 4.3, Figura 4).

O caso específico de tarefa é onde funcionou. Acurácia no Natural Questions, da Tabela 1:

| Modelo | Sem imitação | Treinado no ShareGPT-Mix (amplo) | Treinado no NQ-synthetic (local) | ChatGPT |
|---|---|---|---|---|
| LLaMA 7B | 17 | 10 | 22 | 31 |
| LLaMA 13B | 20 | 15 | 27 | 31 |

A imitação ampla reduziu a acurácia e a imitação local a elevou, fechando uma grande parte da distância na única tarefa que ela visava. A conclusão dos autores é que destilar um comportamento específico é muito mais viável do que igualar amplamente as capacidades do ChatGPT. Eles também constataram que treinar com mais dados do ShareGPT-Mix prejudicou algumas avaliações em relação ao base model, o que atribuem a uma mudança de distribuição entre os dados conversacionais de fine-tuning e os benchmarks, e sinalizam como não resolvido se regularização ou misturar dados de pré-treinamento resolveria isso.

### Por que as avaliações e os benchmarks discordam

A resposta do artigo é que os modelos de imitação aprendem estilo, não conteúdo. A Tabela 2 compara saídas de modelos de imitação treinados em 20M, 80M e 150M de tokens com o LLaMA base e com uma segunda amostra do ChatGPT:

| Métrica | LLaMA base | 20M | 150M | Segunda amostra do ChatGPT |
|---|---|---|---|---|
| Se o ChatGPT produz uma lista, o modelo produz? | 13% | 50% | 81% | 83% |
| Saídas em tom autoritário, segundo o GPT-4 | 57% | 99% | 98% | 98% |
| Correlação de Pearson do comprimento com a saída do ChatGPT | -0,11 | 0,51 | 0,62 | 0,67 |

A tabela do artigo também tem uma coluna de 80M, omitida aqui. Nessas medidas de estilo, os modelos de imitação se aproximam do que uma segunda resposta do ChatGPT pontua. Em factualidade, eles continuam fracos. A Figura 2 do artigo mostra uma resposta de imitação que tem a estrutura do ChatGPT e está completamente errada, em tom confiante.

A explicação dos autores para por que os avaliadores deixaram passar: crowd workers sem conhecimento de domínio ou tempo significativo podem ser enganados por respostas confiantes e bem estruturadas. Eles tiram duas lições para a avaliação. Use especialistas de domínio ou prompts difíceis, e note que o GPT-4 como juiz mostrou o mesmo viés.

### O que a escala traz e o que não traz

Esta é a afirmação a acertar exatamente. Os autores dizem que a lacuna, com os métodos atuais, só pode ser superada por uma quantidade pouco prática de dados de imitação ou por um base model mais capaz. A evidência deles para a segunda metade: aumentar o tamanho do base model melhorou os benchmarks automáticos de forma constante, enquanto aumentar os dados de imitação deu pouca melhora ou regressões (Figura 4). A conclusão deles é que a ação de maior alavancagem é um base model melhor.

Duas qualificações importam. A parte da "quantidade pouco prática de dados de imitação" é um argumento: eles dizem que igualar o ChatGPT amplamente exigiria um dataset mais próximo da escala do pré-treinamento e observam que não está claro se vale a pena fazer isso. Eles não o executaram. E o tamanho do base model é um proxy da qualidade do base model, ponto que a própria nota de rodapé deles faz. O cenário também é de base models LLaMA e GPT-2 de 2023 imitando o ChatGPT, então não trate os tamanhos como atuais.

### O que se transfere

O artigo também relata o que um aluno absorve. Os modelos de imitação ficaram menos tóxicos no RealToxicityPrompts conforme os dados de imitação cresceram, o que os autores leem como o modelo aprendendo a se abster do jeito que o ChatGPT faz (Figura 5). Eles concluem que a imitação é eficaz quando você tem um base model forte e quer evitar anotar dados de fine-tuning. Um aluno herda comportamentos que o professor foi treinado para mostrar, incluindo padrões de recusa, de forma muito mais barata do que herda conhecimento.

### Ressalvas que os autores enunciam

Eles nomeiam três: as pontuações de avaliação do ChatGPT podem estar infladas por contaminação em um conjunto de pré-treinamento desconhecido, eles usaram apenas imitação supervisionada e não RLHF ou métodos constitucionais, e usaram uma coleta de dados simples. Uma cautela a mais é minha: a avaliação usou 255 prompts depois de filtrar os de código e os que não estavam em inglês, então o resultado das avaliações é mais estreito do que "qualidade do ChatGPT".

## Prática

1. ▢ Usando a Tabela 1, que parte da distância até o ChatGPT no Natural Questions a imitação local fecha para o LLaMA 13B e para o LLaMA 7B, e o que a imitação ampla fez?

<details markdown="1"><summary>Verificação</summary>

Para o 13B a distância é 31 menos 20, que dá 11, e o NQ-synthetic soma 7 pontos, cerca de 64% dela. Para o 7B a distância é 14 e ele soma 5, cerca de 36%. A imitação ampla do ShareGPT-Mix reduziu a acurácia nos dois, em 7 pontos para o 7B e 5 para o 13B. São números do NQ em um benchmark, não uma afirmação sobre todas as tarefas.

</details>

2. ▢ Por que os crowd workers avaliaram os modelos de imitação como próximos do ChatGPT enquanto os benchmarks mostraram pouco ganho?

    - a) Os avaliadores sabiam a identidade de cada modelo
    - b) Os avaliadores verificaram cada afirmação de forma independente
    - c) Os avaliadores favoreceram o puro tamanho da resposta
    - d) Os avaliadores recompensaram um estilo confiante e polido

<details markdown="1"><summary>Verificação</summary>

**d)** O artigo diz que os modelos de imitação copiam o estilo do ChatGPT, e avaliadores sem conhecimento de domínio ou tempo para checar fatos podem ser enganados por ele. (b) é o oposto do que aconteceu. (c) não é a explicação do artigo, embora o tamanho da saída dos modelos tenha de fato se correlacionado com o do ChatGPT. (a) está errada: a comparação era cega.

</details>

3. ▢ Uma equipe faz fine-tuning de um modelo de 7B em mais 200K diálogos ao estilo do ChatGPT e relata um ganho a partir de avaliações de crowd workers. Que duas coisas você pede antes de acreditar que o modelo se iguala ao professor?

<details markdown="1"><summary>Dica</summary>

Pense em qual tipo de medição o artigo encontrou divergindo das avaliações, e no que faltava nas tarefas.

</details>

<details markdown="1"><summary>Verificação</summary>

Peça benchmarks automáticos direcionados em tarefas que os dados de treinamento não cobrem muito, como conhecimento factual, código ou raciocínio, contra o base model antes do fine-tuning. Peça para saber quem eram os avaliadores e se algum tinha conhecimento de domínio ou tempo para checar fatos. O achado do artigo é que as avaliações podem subir enquanto os benchmarks ficam parados ou caem. As avaliações sozinhas provam apenas que o estilo se transferiu.

</details>

4. ▢ Você pode gastar um orçamento fixo em mais um milhão de exemplos amplos escritos pelo professor ou em passar para um base model com o dobro do tamanho. O que a evidência do artigo sugere, e o que ela não mostra?

<details markdown="1"><summary>Verificação</summary>

Nos experimentos dele, escalar o base model melhorou os benchmarks de forma constante enquanto escalar os dados de imitação deu pouca mudança ou negativa, o que sugere o base model. Ela não mostra que nenhuma quantidade de dados de imitação ampla ajudaria, já que eles não testaram dados próximos da escala de pré-treinamento, e não cobre um caso específico de tarefa, em que a imitação local deles funcionou bem. Para uma tarefa estreita, os dados podem ser o melhor gasto.

</details>

5. ▢ A lição 13 perguntou o que os termos de um provedor permitem. O artigo lista razões para a imitação, de benignas a ilegais, incluindo empresas lançando serviços que concorrem com o sistema proprietário. Por que isso importa para um dataset ao estilo do ShareGPT?

<details markdown="1"><summary>Verificação</summary>

Porque um dataset de saídas de outro provedor só é utilizável se os termos dele o permitirem. Por exemplo, os Terms of Use da OpenAI listam, entre as coisas que um usuário não pode fazer, usar a saída para desenvolver modelos que concorram com a OpenAI (termos do resto do mundo, em vigor desde 1º de janeiro de 2026). Confira o texto atual do provedor que você usou. Não encontrei uma análise de se algum dataset específico era permitido nas seções do artigo que li.

</details>

## Prática no mundo real

- [ ] Abra a Figura 1 e a Figura 4 do artigo de Gudibande e escreva uma frase sobre como cada uma apoia a afirmação de que um base model melhor ajuda mais do que mais dados de imitação.
- [ ] Pegue qualquer modelo destilado que você usa e procure o seu model card. Anote quais tipos de evidência ele dá para "se iguala ao professor": avaliações humanas, pontuações de um modelo juiz ou benchmarks direcionados.
- [ ] Amanhã: sem consultar anotações, escreva a diferença entre imitação local e ampla, o resultado do Natural Questions e por que as avaliações de crowd workers enganaram.

## Para ir além

- [O Que o Aluno Herda](../reference/what-the-student-inherits.md)
- [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
