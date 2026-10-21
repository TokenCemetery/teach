---
title: "10. A loss do DPO e o que ela deixa de fora em relação ao PPO"
description: "Uma loss, dois modelos, nenhum loop de amostragem e o mesmo beta que uma penalidade de KL teria usado"
type: lesson
---

# Lição 10. A loss do DPO e o que ela deixa de fora em relação ao PPO

**Ligação com a missão:** "Derivar a recompensa implícita do DPO a partir dos mesmos dados de preferência que o RLHF usa e dizer o que ele abre mão ao remover o loop de RL" é o quarto item de O sucesso se parece com isto. A lição 9 cobriu a derivação; esta lição cobre a loss resultante e diz com clareza o que ela deixa de fora em relação ao PPO.
**Fonte principal:** [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Pré-requisitos:** [Lição 9](0009-dpos-implicit-reward-why-the-partition-function-cancels.md)

## Aquecimento

1. ▢ Por que a função de partição `Z(x)` se cancela ao calcular uma diferença de duas recompensas para o mesmo prompt?

<details markdown="1"><summary>Verificação</summary>

`Z(x)` depende apenas do prompt, e não de qual completion está sendo pontuada, então é exatamente o mesmo termo aditivo nas duas recompensas que estão sendo subtraídas, e se cancela por completo na diferença.

</details>

2. ▢ O que significa "recompensa implícita", no sentido em que a lição 9 a deriva?

<details markdown="1"><summary>Verificação</summary>

A função de recompensa que uma policy define matematicamente, em relação a uma policy de referência fixa, puramente como consequência da relação de policy ótima que o objetivo do RLHF já implica, sem nunca treinar um reward model separado.

</details>

## Saiba isto

### Substituindo a recompensa implícita na loss de Bradley-Terry

A loss de Bradley-Terry da lição 4 treinava um reward model separado para fazer a pontuação de uma completion preferida superar a de uma rejeitada. O DPO usa exatamente essa mesma ideia, com uma substituição: em todo lugar onde a loss de Bradley-Terry usaria a saída de um reward model treinado, o DPO substitui pela recompensa implícita da lição 9, `β · log(π(y|x) / π_ref(y|x))`, calculada diretamente a partir da policy sendo treinada e do modelo de referência congelado. A loss resultante, exatamente como Rafailov et al. a apresentam, compara a completion preferida `y_w` e a rejeitada `y_l` para o mesmo prompt:

```text
loss = -log( sigmoid( β · [ (log π(y_w|x) - log π_ref(y_w|x)) - (log π(y_l|x) - log π_ref(y_l|x)) ] ) )
```

Essa é a loss de Bradley-Terry da lição 4, com as duas pontuações do reward model substituídas pelos dois valores da recompensa implícita, um para a completion preferida e outro para a rejeitada. Nada na forma da loss mudou; o que mudou é o que está no lugar de uma recompensa.

### O que essa loss exige e o que ela não exige mais

Calcular essa loss exige exatamente dois modelos: a policy sendo treinada e uma cópia congelada do modelo de referência (normalmente o modelo SFT), cada um avaliado nas mesmas completions preferida e rejeitada para obter quatro log-probabilidades no total. Compare com a configuração de PPO da etapa 4 (lição 8): nenhum reward model separado é treinado, já que a recompensa implícita é calculada diretamente a partir da policy e do modelo de referência. Nenhuma função de valor é necessária, já que não há vantagem a estimar; o DPO não faz reinforcement learning no sentido de amostrar ações e estimar retornos. Também não há corte do PPO (lição 7), já que não há atualização de policy gradient cujo tamanho de passo precise ser limitado; essa loss é otimizada diretamente, do mesmo modo que qualquer loss supervisionada comum, com um passo de gradiente por batch de pares de preferência, sem nenhum loop de amostragem entre os passos.

### O mesmo beta, fazendo o mesmo trabalho

O `β` na loss do DPO não é um hiperparâmetro novo inventado para este método; é a mesma força de penalidade de KL do objetivo do RLHF da lição 6, agora embutida diretamente na recompensa implícita em vez de aparecer como um termo de penalidade separado somado à pontuação de um reward model. Um `β` maior ainda significa ficar mais perto do modelo de referência; um `β` menor ainda significa ter mais liberdade para se afastar dele, exatamente a troca da lição 6, só que expressa dentro de uma única loss em vez de dois termos separados.

### O que de fato se abre mão

O DPO não remove as trocas que a penalidade de KL do PPO gerenciava; ele remove a maquinaria. O método de Rafailov et al. é uma reformulação matematicamente exata da mesma relação de policy ótima em que o RLHF já se apoia, e não uma aproximação dela, então nada no objetivo subjacente de satisfazer as preferências é enfraquecido. O que de fato se perde é um reward model independente e a flexibilidade que vem de treinar um separadamente: um reward model pode, em princípio, ser reutilizado para pontuar saídas nas quais nunca treinou diretamente a policy, ser inspecionado por si só ou ser combinado com sinais adicionais além dos dados de preferência originais. A recompensa implícita do DPO existe apenas atrelada a um par específico de policy e modelo de referência; não sobra nenhuma função de pontuação independente quando o treinamento termina, só a própria policy treinada.

## Prática

1. ▢ O cálculo da loss do DPO para um par de preferência precisa de quatro log-probabilidades. Diga de que cada uma das quatro é a log-probabilidade.

<details markdown="1"><summary>Verificação</summary>

A log-probabilidade da completion preferida sob a policy, a log-probabilidade da completion preferida sob o modelo de referência, a log-probabilidade da completion rejeitada sob a policy e a log-probabilidade da completion rejeitada sob o modelo de referência.

</details>

2. ▢ De quais componentes do PPO (reward model, função de valor, penalidade de KL, atualização cortada) a loss do DPO não tem nenhuma necessidade?

    - a) Apenas da atualização cortada
    - b) Do reward model e da função de valor; a troca da penalidade de KL ainda está presente, só que embutida na recompensa implícita em vez de em um termo separado
    - c) Dos quatro, já que o DPO não usa penalidade de KL de nenhum tipo
    - d) Apenas do reward model; o DPO ainda treina uma função de valor separada

<details markdown="1"><summary>Verificação</summary>

**b)** é o relato correto: o DPO não precisa de reward model separado nem de função de valor, e não tem atualização cortada por passo, já que não há loop de amostragem de RL, mas a mesma troca controlada pelo beta que a lição 6 descreveu continua presente, incorporada diretamente ao termo da recompensa implícita. As alternativas (a), (c) e (d) declaram errado quais peças sobrevivem.

</details>

3. ▢ Uma equipe quer reutilizar o seu reward model treinado para pontuar um batch de completions que nunca fizeram parte do treinamento de nenhuma policy, puramente para fins de monitoramento. Uma equipe que usa DPO em vez de PPO poderia fazer a mesma coisa com facilidade equivalente?

<details markdown="1"><summary>Verificação</summary>

Não de forma tão direta. O DPO nunca produz um reward model independente; a sua recompensa implícita é definida apenas em termos de uma policy treinada específica e do seu modelo de referência. Pontuar completions arbitrárias assim é exatamente o tipo de reutilização que um reward model independente suporta e que a abordagem do DPO não produz como subproduto.

</details>

4. ▢ O `β` significa algo diferente na loss do DPO do que significava no objetivo do RLHF da lição 6?

<details markdown="1"><summary>Verificação</summary>

Não. É a mesma força de penalidade de KL, controlando a mesma troca entre ficar perto do modelo de referência e avançar em direção ao que os dados de preferência recompensam; o DPO simplesmente a embute diretamente no termo da recompensa implícita em vez de mantê-la como uma penalidade visualmente separada somada à pontuação de um reward model.

</details>

## Prática no mundo real

- [ ] Encontre uma implementação de DPO em uma biblioteca a que você tenha acesso (o TRL da Hugging Face é uma comum) e confirme que ela calcula as mesmas quatro log-probabilidades que esta lição nomeia, por par de preferência.
- [ ] Usando um pequeno exemplo hipotético (invente valores plausíveis de log-probabilidade para uma completion preferida e uma rejeitada sob uma policy e um modelo de referência), calcule a loss do DPO à mão para dois valores diferentes de `β` e descreva como a loss muda conforme `β` cresce.
- [ ] Amanhã: para um projeto em que você poderia querer alinhar um modelo, decida se recorreria primeiro ao PPO ou ao DPO e escreva uma frase dizendo qual das trocas desta lição (custo de engenharia, reutilização de um reward model independente, infraestrutura de RL) motivou a sua resposta.

## Para ir além

- [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Documentação: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Recursos](../RESOURCES.md)

---

A etapa 5 cobriu um jeito de chegar a um resultado semelhante ao do RLHF sem um reward model separado nem um loop de RL. A etapa 6 cobre uma partida diferente do PPO: manter o loop de RL, mas para tarefas em que a recompensa não é questão de preferência humana, e sim algo diretamente verificável.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
