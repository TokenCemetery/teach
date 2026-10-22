---
title: "1. O que o pós-treinamento oferece"
description: "Um modelo alinhado 100 vezes menor superou um base model bruto em fazer o que os usuários de fato queriam"
type: lesson
---

# Lição 1. O que o pós-treinamento oferece

**Ligação com a missão:** "Dados os dados, o orçamento e o comportamento-alvo de uma equipe, escolher entre SFT sozinho, DPO, RLHF-PPO e GRPO, e defender a escolha" é a decisão central da missão, e ela começa por saber que problema o pós-treinamento resolve e o pré-treinamento sozinho não.
**Fonte principal:** [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Pré-requisitos:** nenhum

## Saiba isto

### Um base model não é automaticamente um bom assistente

Um base model pré-treinado, o produto de todo o arco de `llm/pretraining`, é treinado para prever os próximos tokens mais prováveis, dada a distribuição de texto que ele viu. Isso não é a mesma habilidade que seguir as instruções reais de um usuário, e tornar um base model maior não fecha essa lacuna por si só. Ouyang et al. dizem isso sem rodeios: "tornar os modelos de linguagem maiores não os torna, por si só, melhores em seguir a intenção do usuário." Um base model grande pode produzir saídas inverídicas, inúteis ou simplesmente diferentes do que foi pedido, não por faltar capacidade, mas porque nada no pré-treinamento o treinou especificamente para usar essa capacidade do jeito que o usuário quer.

### O resultado de destaque

O resultado central de Ouyang et al. torna concreto o tamanho dessa lacuna: em avaliações humanas, as saídas do seu modelo **InstructGPT** de 1,3 bilhão de parâmetros foram preferidas às do modelo GPT-3 de 175 bilhões de parâmetros do qual ele partiu, apesar de ter cerca de 100 vezes menos parâmetros. O pós-treinamento não tornou o modelo maior nem mais inteligente em nenhum sentido bruto; ele mudou para onde a capacidade já existente do modelo estava apontada, e essa direção importou mais para os avaliadores humanos do que mais duas ordens de grandeza de escala.

### O pipeline de três passos

A receita de Ouyang et al., ainda hoje o formato de referência contra o qual a maior parte do trabalho posterior de RLHF é descrita, tem três passos:

1. **Coletar demonstrações e treinar uma policy supervisionada.** Rotuladores humanos escrevem exemplos do comportamento desejado para uma variedade de prompts; o base model passa por fine-tuning com eles, por meio de aprendizado supervisionado comum. Esse passo é o **SFT** (supervised fine-tuning), tema da etapa 2.
2. **Coletar comparações e treinar um reward model.** Os rotuladores ranqueiam várias saídas do modelo SFT para o mesmo prompt; um modelo separado, o **reward model**, é treinado para prever qual saída um humano preferiria. Esse é o tema da etapa 3.
3. **Otimizar a policy contra o reward model com PPO.** O modelo SFT passa por mais fine-tuning usando reinforcement learning, tratando a pontuação do reward model como o sinal de recompensa a maximizar. Esse é o tema da etapa 4, e os passos 2 e 3 podem ser repetidos, coletando mais comparações sobre a melhor policy atual para treinar, por sua vez, um novo reward model e uma nova policy.

### Alignment tax, apresentado

O pós-treinamento não é isento de custo nem quando funciona. Ouyang et al. descobriram que os seus modelos alinhados tiveram desempenho ligeiramente pior em alguns benchmarks públicos de PLN (um benchmark de compreensão de leitura, um de raciocínio discreto, um de senso comum e um de tradução, entre outros) do que o base model original. Eles chamam isso de **alignment tax**: um custo real e medido para certas capacidades, pago em troca de um comportamento que os humanos preferiram no geral. Eles também encontraram uma correção parcial: misturar as atualizações do PPO com atualizações que aumentam a verossimilhança dos dados originais de pré-treinamento (que eles chamam de **PPO-ptx**) recuperou boa parte do desempenho perdido sem abrir mão dos ganhos de preferência que o pós-treinamento foi feito para produzir. O imposto não é fixo nem inevitável; é uma troca medida que técnicas posteriores podem pagar parcialmente.

### O panorama pela frente

O SFT sozinho (etapa 2) é o passo mais barato e já muda muito do comportamento. A modelagem de recompensa e o RLHF via PPO (etapas 3 e 4) acrescentam por cima dele uma segunda fase, de reinforcement learning, com custo e complexidade adicionais reais. O Direct Preference Optimization (etapa 5) busca depois um resultado semelhante sem um reward model separado nem qualquer loop de RL. O GRPO (etapa 6) adapta a abordagem de RL a tarefas com uma resposta verificável e checável, como matemática ou código, em vez de um julgamento de preferência humana. O ajuste específico de segurança (etapa 8) aplica a mesma família de técnicas a um alvo diferente. Cada uma delas é uma resposta distinta à mesma pergunta de fundo que esta lição abriu: como a capacidade já existente de um modelo é apontada para o que uma pessoa realmente quer, e a que custo.

## Prática

1. ▢ O modelo InstructGPT de 1,3 bilhão de parâmetros foi preferido ao modelo GPT-3 de 175 bilhões de parâmetros em avaliações humanas. O que esse resultado sugere sobre a relação entre a contagem bruta de parâmetros e ser bom em seguir a intenção do usuário?

<details markdown="1"><summary>Verificação</summary>

Que elas não são a mesma coisa. Um modelo muito menor, apontado para a tarefa por meio do pós-treinamento, superou um modelo muito maior que não passou por isso. A escala sozinha não produziu o comportamento que os humanos preferiram; o que produziu foi como a capacidade do modelo foi direcionada.

</details>

2. ▢ Coloque em ordem estes três passos do pipeline de Ouyang et al.: (a) treinar um reward model com comparações humanas de saídas do modelo, (b) fazer fine-tuning da policy contra o reward model usando PPO, (c) fazer fine-tuning de um base model com demonstrações escritas por humanos.

<details markdown="1"><summary>Verificação</summary>

c, a, b: primeiro coletar demonstrações e treinar uma policy supervisionada (SFT), depois coletar comparações e treinar um reward model, e então otimizar a policy contra esse reward model com PPO.

</details>

3. ▢ O que é um alignment tax, segundo a própria descoberta de Ouyang et al., e o que eles descobriram que poderia compensá-lo parcialmente?

<details markdown="1"><summary>Verificação</summary>

Uma queda medida de desempenho em certos benchmarks públicos de PLN que veio junto com os ganhos de alinhamento do pós-treinamento, mesmo com os avaliadores humanos preferindo o modelo alinhado no geral. Misturar as atualizações do PPO com atualizações que aumentam a verossimilhança dos dados originais de pré-treinamento (PPO-ptx) recuperou boa parte desse desempenho perdido sem abrir mão dos ganhos de preferência.

</details>

4. ▢ Qual destas descreve melhor o que o SFT, a modelagem de recompensa e o RLHF-PPO fazem, cada um, no pipeline de Ouyang et al.?

    - a) O SFT imita diretamente demonstrações escritas por humanos; a modelagem de recompensa aprende a prever a preferência humana entre saídas; o RLHF-PPO otimiza a policy contra esse sinal de preferência aprendido
    - b) Os três passos treinam o reward model, em escala crescente
    - c) O SFT e o RLHF-PPO são o mesmo passo, executado duas vezes por estabilidade
    - d) A modelagem de recompensa substitui por completo o base model antes de o PPO começar

<details markdown="1"><summary>Verificação</summary>

**a)** é a divisão real de trabalho entre os três passos. As alternativas (b), (c) e (d) fundem passos que fazem coisas genuinamente diferentes: imitar demonstrações, aprender um sinal de preferência e otimizar contra esse sinal são três passos separados, e não um só repetido.

</details>

## Prática no mundo real

- [ ] Encontre um model card ou relatório técnico de um modelo aberto "instruct" ou "chat" e anote quais dos três passos de Ouyang et al. ele diz explicitamente ter usado (SFT, um reward model e/ou RL) e quais, se houver, ele substitui por um método diferente.
- [ ] Leia o resumo do artigo do InstructGPT (linkado acima) e escreva, em uma frase, que danos específicos (além de simplesmente "inútil") Ouyang et al. citam como motivação para a necessidade de alinhamento.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a etapa 2: dado que o SFT é descrito como imitação direta de demonstrações escritas por humanos, que tipo de erro você esperaria que uma implementação ingênua de SFT cometesse se treinasse em todos os tokens de um exemplo de treinamento, incluindo o próprio prompt?

## Para ir além

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
