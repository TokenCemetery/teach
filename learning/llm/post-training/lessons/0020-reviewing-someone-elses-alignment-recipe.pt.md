---
title: "20. Revisando a receita de alinhamento de outra pessoa"
description: "Percorra o pipeline por todas as etapas que esta trilha cobriu, em ordem, e resolva uma alegação contestada a partir da fonte, e não de uma reafirmação confiante"
type: lesson
---

# Lição 20. Revisando a receita de alinhamento de outra pessoa

**Ligação com a missão:** Esta lição encerra o arco. Cada etapa anterior produziu uma coisa a checar no pipeline de pós-treinamento de outra pessoa; esta lição é o checklist, mais a disciplina de resolver uma confusão específica e genuinamente comum a partir da fonte primária, e não de uma reafirmação secundária e confiante.
**Fonte principal:** [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Pré-requisitos:** todas as lições anteriores desta trilha, já que esta é a síntese.

## Aquecimento

1. ▢ Uma equipe tem dados de preferência e nenhuma necessidade específica de reutilizar um reward model fora do treinamento. Qual entre DPO e PPO é o padrão mais defensável, e por quê?

<details markdown="1"><summary>Verificação</summary>

O DPO. Ele chega a um resultado semelhante, treinado com preferências, a um custo próximo ao do próprio SFT, precisando apenas da policy e de um modelo de referência congelado, sem reward model separado nem loop de RL a justificar, a menos que algo específico exija um.

</details>

2. ▢ O que "defender a escolha contra a rejeitada" exige, além de declarar os benefícios do método escolhido?

<details markdown="1"><summary>Verificação</summary>

Nomear qual método mais barato foi considerado primeiro e por que ele ficou especificamente aquém para a tarefa, e não apenas afirmar por que o método escolhido é bom.

</details>

## Saiba isto

### O checklist de revisão: as etapas em ordem

Ao revisar um pipeline de pós-treinamento proposto ou existente, percorra-o pelas etapas desta trilha em ordem, fazendo a mesma pergunta em cada uma: esta escolha é declarada e justificada, ou apenas pressuposta?

**Etapa 1, o panorama.** O pipeline declara em qual parte do panorama de SFT/RLHF/DPO/GRPO ele está construindo, e isso corresponde ao comportamento-alvo descrito, ou "pós-treinamos o modelo" fica sem especificar qual deles foi realmente usado?

**Etapa 2, SFT.** O loss masking em tokens que não são do assistente é de fato aplicado (lição 3), e o chat template usado no treinamento está documentado com clareza suficiente para que o serving o reproduza exatamente (lição 2)? Um pipeline vago sobre qualquer um dos dois está exposto a um modo de falha real e já documentado, e não hipotético.

**Etapa 3, modelagem de recompensa.** Se um reward model é treinado, os dados de preferência são coletados como rankings decompostos em pares, conforme o método da lição 4, ou como comparações isoladas que correm o risco do overfitting que Ouyang et al. encontraram? O reward hacking (lição 5) é checado, idealmente com algo como um modelo de preferência held-out, em vez de dado como inexistente?

**Etapa 4, RLHF-PPO, se usado.** O coeficiente da penalidade de KL é declarado e a sua troca (lição 6) é reconhecida? O pipeline nomeia os modelos que roda simultaneamente e os seus tamanhos (lição 8), dado o quanto a escala do reward model e da função de valor afetou diretamente a própria estabilidade de Ouyang et al.?

**Etapa 5, DPO, se usado.** O modelo de referência está claramente identificado, e o papel do beta (a mesma troca de força de KL do PPO, conforme a lição 10) é declarado em vez de deixado como um hiperparâmetro sem explicação?

**Etapa 6, GRPO, se usado.** A recompensa por saída é a pontuação de um modelo treinado ou uma checagem verificável? Essa distinção importa o bastante para merecer uma checagem própria, coberta diretamente abaixo.

**Etapa 7, treinamento de raciocínio, se usado.** O comportamento de raciocínio estendido é atribuído ao que de fato o produziu (RL contra uma recompensa, verificável ou não), em vez de descrito como algo explicitamente programado?

**Etapa 8, ajuste de segurança, se usado.** O pipeline declara se o feedback de inofensividade veio de humanos ou de um modelo (lição 15) e, se o desempenho é comparado com um baseline de feedback humano, essa comparação é de fato relatada, conforme o precedente do próprio Bai et al., em vez de presumida como favorável?

**Etapa 9, avaliação.** O alignment tax é medido por benchmark, e não como um único número condensado (lição 17), e há uma checagem de recusa excessiva ou de viés do juiz ao lado de qualquer pontuação de destaque de segurança ou de preferência que seja relatada (lição 18)?

Um pipeline que responde a todas essas perguntas com uma escolha declarada e defensável é um pipeline que fez o trabalho que esta trilha descreve. Um pipeline que responde a várias delas com silêncio não fez, não importa como pareçam os seus números finais de benchmark.

### Resolvendo uma alegação contestada a partir da fonte, e não de um post de blog

Vale a pena percorrer diretamente uma confusão específica e fácil de cometer, porque é fácil repeti-la sem conferir. Às vezes se afirma, casualmente, que "o GRPO treina com recompensas verificáveis", como se os dois fossem inseparáveis. Conferir o próprio artigo de Shao et al., o que introduz o GRPO, refuta isso diretamente como enunciado: o GRPO do DeepSeekMath treina contra uma recompensa produzida por `r_φ`, um reward model explicitamente treinado, inicializado e treinado do mesmo jeito que a lição 4 descreve. As únicas recompensas baseadas em regras do artigo, que pontuam uma resposta pelo acerto da sua resposta final, aparecem na comparação com outros métodos (RFT e Online RFT), não no seu treinamento com GRPO. O pareamento do GRPO com recompensas verificáveis e baseadas em regras é real e bem documentado, mas pertence ao DeepSeek-R1 (lição 13), um artigo diferente, que aplica o mecanismo relativo ao grupo do GRPO a um tipo de recompensa diferente daquele com que o GRPO foi introduzido. Uma fonte secundária que declara "o GRPO usa recompensas verificáveis" como um fato geral sobre o algoritmo está fundindo silenciosamente as contribuições de dois artigos separados em uma só; voltar à própria seção de método do DeepSeekMath, em vez de confiar na alegação fundida e confiante, é o que a pega. O mecanismo (vantagem relativa ao grupo) e a origem da recompensa (checagem verificável contra modelo treinado) são duas escolhas independentes, e não um pacote inseparável, e um pipeline que acerta essa distinção é um pipeline cujo autor de fato leu as fontes em vez de repetir o que "todo mundo sabe" sobre o GRPO.

## Prática

1. ▢ Um pipeline proposto afirma "usamos GRPO com recompensas verificáveis para a nossa tarefa de benchmark de matemática" e cita o artigo do DeepSeekMath como única fonte. Essa citação é fiel ao que o próprio método do DeepSeekMath de fato descreve?

<details markdown="1"><summary>Verificação</summary>

Não totalmente. O GRPO do próprio DeepSeekMath treina contra uma recompensa vinda de um reward model treinado, e não de uma checagem verificável baseada em regras. O pareamento de recompensa verificável com o GRPO é contribuição do DeepSeek-R1, um artigo diferente. O método real do pipeline (GRPO com uma recompensa verificável) pode muito bem ser razoável, mas citar apenas o DeepSeekMath como fonte atribui erroneamente de onde vem essa combinação específica.

</details>

2. ▢ Um documento de pipeline diz apenas "aplicamos RLHF", sem mais detalhes. Usando o checklist desta lição, cite duas coisas específicas que essa afirmação deixa sem declarar e sobre as quais um revisor deveria perguntar.

<details markdown="1"><summary>Verificação</summary>

Quaisquer duas entre: o coeficiente da penalidade de KL e se a sua troca foi considerada; os tamanhos dos modelos envolvidos (policy, referência, reward model, função de valor) e se a escala do reward model foi escolhida deliberadamente; como os dados de preferência foram coletados e se o reward hacking foi checado; se o alignment tax resultante foi medido, e contra quais benchmarks.

</details>

3. ▢ Um pipeline relata uma pontuação alta de segurança vinda de uma avaliação com LLM-as-judge, sem nenhum outro detalhe. Segundo a lição 18 e a checagem da etapa 9 desta lição, o que um revisor deveria pedir antes de confiar nessa pontuação?

<details markdown="1"><summary>Verificação</summary>

Se o juiz foi checado quanto à calibração contra vieses conhecidos (de posição, de verbosidade) e se existe uma checagem de recusa excessiva ao lado da pontuação de segurança, para que uma pontuação alta reflita segurança genuína e não recusa generalizada ou um juiz explorável.

</details>

## Prática no mundo real

- [ ] Encontre um relatório técnico de pós-treinamento real e publicado e passe-o pelo checklist desta lição, etapa por etapa, anotando quais itens são declarados explicitamente e quais ficam em silêncio.
- [ ] Encontre uma alegação sobre métodos de pós-treinamento (DPO, PPO, GRPO ou RLAIF) declarada com confiança em um post de blog, tutorial ou resposta de fórum e confira-a contra o artigo primário a que ela deveria remontar. Anote se ela se sustenta, é uma simplificação ou é uma confusão genuína como o exemplo do GRPO desta lição.
- [ ] Amanhã: escreva uma revisão curta, de três a cinco frases, de um pipeline de pós-treinamento real ou hipotético, nomeando pelo menos uma escolha específica que você questionaria e o que você pediria que a pessoa que a defende justificasse.

## Para ir além

- [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
