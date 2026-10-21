---
title: "11. GRPO: vantagem relativa ao grupo em vez de uma função de valor"
description: "Amostre várias respostas para a mesma pergunta e deixe a própria dispersão das recompensas do grupo dizer quais foram melhores"
type: lesson
---

# Lição 11. GRPO: vantagem relativa ao grupo em vez de uma função de valor

**Ligação com a missão:** "Explicar a vantagem relativa ao grupo no GRPO e por que uma recompensa verificável (um teste unitário, uma resposta matemática conferida) muda o que o treinamento de RL pode ter como alvo" é o quinto item de O sucesso se parece com isto. Esta lição cobre a vantagem relativa ao grupo em si; a lição 12 cobre as recompensas verificáveis, o par que torna o GRPO especialmente adequado a matemática e código.
**Fonte principal:** [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Pré-requisitos:** [Lição 10](0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md)

## Aquecimento

1. ▢ O que a loss do DPO exige, em termos de modelos, que a configuração do PPO não exige?

<details markdown="1"><summary>Verificação</summary>

Nada a mais; o DPO precisa estritamente de menos modelos do que o PPO. Ele precisa apenas da policy e de um modelo de referência congelado, sem reward model separado e sem função de valor.

</details>

2. ▢ Remover o reward model separado e o loop de RL no DPO também remove a troca da penalidade de KL entre ficar perto do modelo de referência e avançar em direção ao que os dados de preferência recompensam?

<details markdown="1"><summary>Verificação</summary>

Não. A mesma troca, controlada pelo mesmo `β`, continua presente; ela é simplesmente incorporada diretamente ao termo da recompensa implícita em vez de mantida como uma penalidade visualmente separada.

</details>

## Saiba isto

### O custo que a função de valor do PPO acrescenta especificamente

A etapa 4 (lição 8) já estabeleceu que o PPO precisa de uma função de valor ao lado do reward model, inicializada a partir dele, para produzir as estimativas de vantagem de que o seu objetivo cortado depende. Shao et al. nomeiam exatamente por que essa peça específica é cara: a função de valor costuma ser outro modelo de tamanho comparável ao da própria policy, acrescentando custo real de memória e de compute por cima de tudo o mais de que o PPO já precisa. Eles acrescentam um segundo problema específico de modelos de linguagem: nesse cenário, normalmente só o último token de uma completion recebe uma pontuação de recompensa, o que torna mais difícil treinar uma função de valor que seja precisa em todo token anterior dentro dessa completion do que seria em um cenário com feedback de recompensa a cada passo.

### O substituto do GRPO: deixar um grupo de amostras fornecer o seu próprio baseline

O **Group Relative Policy Optimization (GRPO)** remove totalmente a função de valor, substituindo-a por algo que não precisa de nenhum modelo extra: para uma dada pergunta `q`, o GRPO amostra um **grupo** de `G` saídas, `{o_1, o_2, ..., o_G}`, todas da mesma policy (antiga). Um reward model pontua cada uma das `G` saídas, dando `G` recompensas, de `r_1` a `r_G`. Em vez de perguntar a uma função de valor treinada separadamente "esta saída específica foi melhor do que o esperado", o GRPO faz uma pergunta mais simples, que pode ser respondida diretamente a partir do próprio grupo: esta saída foi melhor do que as outras amostradas para a mesma pergunta. A **vantagem relativa ao grupo** da saída `i` é a recompensa normalizada pelo grupo:

```text
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

aplicada uniformemente a todo token dessa saída. Uma saída que pontuou acima da média do grupo recebe uma vantagem positiva; uma que pontuou abaixo recebe uma vantagem negativa; o tamanho da vantagem é escalado pelo quão dispersas as recompensas do grupo por acaso estavam. Nenhuma função de valor é treinada, e o custo de memória e de compute que a lição 8 atribuiu a ela desaparece junto.

### Por que isso combina especialmente bem com reward models

Shao et al. fazem outra observação que vale a pena guardar: essa comparação relativa ao grupo não é apenas um atalho para economizar custo, ela corresponde ao formato dos dados em que um reward model foi treinado desde o início. Um reward model de Bradley-Terry (lição 4) é treinado em comparações entre saídas para a mesma pergunta; pontuar várias saídas para a mesma pergunta e compará-las entre si, em vez de contra um baseline absoluto aprendido separadamente, pede ao reward model o mesmo tipo de julgamento relativo que ele foi de fato treinado para fazer.

### Para onde a penalidade de KL se move

O GRPO também muda onde a penalidade de KL fica, em comparação com o objetivo do RLHF da lição 6. O objetivo de Ouyang et al. somava a penalidade de KL diretamente à recompensa por token, antes de as vantagens serem calculadas a partir dela. Shao et al., em vez disso, somam a divergência KL entre a policy treinada e a policy de referência como um termo separado diretamente na loss, ao lado do objetivo substituto cortado, em vez de misturá-la à recompensa a partir da qual a vantagem é calculada. Isso mantém a parte do cálculo baseada em recompensa (e a vantagem relativa ao grupo construída a partir dela) livre da complicação do termo de KL, aplicando ainda o mesmo tipo de contenção sobre o quanto a policy se afasta da sua referência.

## Prática

1. ▢ Um grupo de 4 saídas amostradas para a mesma pergunta recebe do reward model as recompensas `{2, 4, 6, 8}`. Aproximadamente, qual(is) saída(s) recebe(m) uma vantagem relativa ao grupo positiva e qual(is) recebe(m) uma negativa?

<details markdown="1"><summary>Dica</summary>

Calcule primeiro a média do grupo e depois pergunte quais recompensas ficam acima dela e quais ficam abaixo.

</details>

<details markdown="1"><summary>Verificação</summary>

A média é 5. As saídas com pontuação 6 e 8 ficam acima da média e recebem vantagem positiva; as saídas com pontuação 2 e 4 ficam abaixo dela e recebem vantagem negativa.

</details>

2. ▢ Segundo Shao et al., cite dois problemas específicos da função de valor do PPO que a vantagem relativa ao grupo do GRPO evita.

<details markdown="1"><summary>Verificação</summary>

A função de valor costuma ser outro modelo de tamanho comparável ao da policy, acrescentando custo substancial de memória e de compute, e, no cenário de LLMs, em que normalmente só o último token recebe uma pontuação de recompensa, treinar uma função de valor precisa em todo token anterior é mais difícil do que em cenários com feedback de recompensa a cada passo.

</details>

3. ▢ Por que Shao et al. descrevem a comparação relativa ao grupo como adequada a reward models de forma especial, além de simplesmente ser mais barata do que uma função de valor?

<details markdown="1"><summary>Verificação</summary>

Porque reward models costumam ser treinados, desde o início, em comparações entre saídas para a mesma pergunta (o mesmo formato que a loss de Bradley-Terry da lição 4 usa); pontuar várias saídas para uma pergunta e compará-las entre si pede ao reward model o mesmo tipo de julgamento relativo que ele foi de fato treinado para fazer.

</details>

4. ▢ Onde fica a penalidade de KL do GRPO, em comparação com onde ela fica no objetivo do RLHF de Ouyang et al. (lição 6)?

    - a) No mesmo lugar: somada diretamente à recompensa por token antes de as vantagens serem calculadas
    - b) O GRPO não tem penalidade de KL
    - c) O GRPO soma a divergência KL como um termo separado diretamente na loss, ao lado do objetivo cortado, em vez de misturá-la à recompensa
    - d) O GRPO substitui a penalidade de KL por um segundo reward model

<details markdown="1"><summary>Verificação</summary>

**c)** é a posição real que Shao et al. descrevem. A alternativa (a) descreve a abordagem de Ouyang et al., que o GRPO muda especificamente. As alternativas (b) e (d) declaram errado o que o GRPO faz; o mesmo tipo de contenção continua presente, apenas realocado.

</details>

## Prática no mundo real

- [ ] Encontre uma implementação de GRPO em uma biblioteca a que você tenha acesso e verifique como ela calcula a vantagem normalizada pelo grupo: ela corresponde à fórmula de média e desvio padrão que esta lição apresenta?
- [ ] Leia o parágrafo do artigo do DeepSeekMath (linkado acima) que descreve por que a função de valor é custosa especificamente no cenário de LLMs e escreva uma frase distinguindo o argumento do custo de memória do argumento da precisão por token.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 12: se um reward model pode ser substituído por qualquer coisa que produza uma pontuação confiável para cada saída amostrada, que tipo de tarefa permitiria que essa pontuação viesse de um verificador determinístico em vez de de um modelo treinado?

## Para ir além

- [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
