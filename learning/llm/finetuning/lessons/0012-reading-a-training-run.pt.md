---
title: "12. Lendo uma execução de treinamento"
description: "Diagnosticar pelo formato da curva, e o que a loss não enxerga"
type: lesson
---

# Lição 12. Lendo uma execução de treinamento

**Ligação com a missão:** "Diagnosticar uma execução que falhou e nomear a causa" está na lista de sucesso. A maioria das pessoas lê uma curva de loss e chuta.
**Fonte principal:** [Artigo: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
**Pré-requisitos:** [Lição 11](0011-your-first-adapter.md)

## Aquecimento

1. ▢ Nomeie as quatro verificações a executar antes de se importar com a curva de loss.

<details markdown="1"><summary>Verificação</summary>

Confirmar que o adapter se acoplou; decodificar um exemplo de treinamento real e contar as posições pontuadas; confirmar que a loss se move; confirmar que o pipeline consegue fazer overfitting em dois exemplos.

</details>

2. ▢ Por que registrar a revisão do base model ao lado do adapter?

<details markdown="1"><summary>Verificação</summary>

Um adapter é um diff contra pesos específicos. Sem o base exato ele é inutilizável, e um base quase igual degrada a qualidade em silêncio.

</details>

3. ▢ Bytes por parâmetro congelado versus por parâmetro treinável?

<details markdown="1"><summary>Verificação</summary>

Dois versus dezesseis.

</details>

## Saiba isto

### A loss de treinamento sozinha não diz quase nada

A loss de treinamento caindo significa que o modelo está se ajustando aos dados que consegue ver. Isso é compatível tanto com um modelo que está aprendendo a tarefa quanto com um que está memorizando o conjunto de treinamento. **Você precisa de uma divisão held-out para distingui-los, e não há substituto.**

Reserve uma antes de começar:

```python
split = dataset.train_test_split(test_size=0.05, seed=0)
args = SFTConfig(..., eval_strategy="steps", eval_steps=50)
trainer = SFTTrainer(..., train_dataset=split["train"], eval_dataset=split["test"])
```

### Os formatos e o que significam

| Loss de treinamento | Loss held-out | Diagnóstico | Ação |
|---|---|---|---|
| Cai | Cai | Aprendendo | Continue |
| Cai | Se achata e depois sobe | Overfitting a partir da virada | Pare no mínimo; mais dados ou menos capacidade |
| Cai a ~0 rápido | Sobe de imediato | Memorizando | Dataset pequeno demais para esta capacidade |
| Se achata em valor alto | Se achata em valor alto | Underfitting | Mais rank, mais target modules, learning rate maior |
| Plana desde o passo 1 | Plana | Pipeline quebrado | As quatro verificações da Lição 11 |
| Dá picos, ou `NaN` | irrelevante | Instabilidade | Learning rate menor; confira overflow em fp16; adicione warm-up |

O **mínimo da held-out** é o checkpoint útil, e não o passo final. Salve checkpoints periodicamente e guarde o melhor; uma execução que termina no passo 1000 quando a loss held-out chegou ao fundo no passo 400 treinou 600 passos de dano.

### Diagnosticando pelo formato, com mais cuidado

**Um piso de loss que mais treinamento não reduz** é um teto de capacidade. O adapter não consegue expressar a atualização de que a tarefa precisa. Somar epochs não resolve; somar rank ou target modules resolve.

**Loss que dá um pico e se recupera** costuma ser um batch contendo algo incomum: um exemplo de comprimento outlier, texto corrompido, um bloco duplicado. Encontre-o. Um único exemplo patológico pode mover uma execução com dataset pequeno.

**Loss que vira `NaN`** é overflow. Em fp16 isso é comum e é o que o loss scaling existe para evitar; em bf16 costuma indicar algo pior, como uma divisão por zero no pipeline de dados ou um learning rate alto o bastante para mandar pesos ao infinito.

**Loss que cai em uma escada limpa**, com degraus nas fronteiras de epoch, significa que o modelo está reconhecendo exemplos que já viu. É a memorização aparecendo diretamente na curva.

### O que a loss não enxerga de jeito nenhum

Esta é a parte importante da lição.

A entropia cruzada pontua a previsão de próximo token na distribuição dos seus dados. Ela é muda sobre:

- **Se as gerações são utilizáveis.** Um modelo pode pontuar bem e produzir uma saída que nunca para, ou que ignora o formato pedido.
- **Se mais alguma coisa quebrou.** O [esquecimento catastrófico](../GLOSSARY.md), a degradação de habilidades não relacionadas à sua tarefa, não aparece na loss da sua tarefa. A sua loss held-out pode melhorar de forma monotônica enquanto o modelo fica pior em todo o resto que sabia fazer.
- **Se a melhora é real ou contaminação.** Se os seus exemplos held-out são quase duplicatas de exemplos de treinamento, a loss held-out está medindo memorização e chamando de generalização.

Então: **gere, todas as vezes.** Fixe um pequeno conjunto de prompts antes do treinamento. Passe-os pelo base model e salve as saídas. Passe-os pelo modelo adaptado com as mesmas configurações de amostragem e compare. Dez minutos lendo gerações reais pegam coisas que nenhuma métrica da sua curva pega.

```python
PROBES = [
    "<a representative task prompt>",
    "<an edge case you care about>",
    "<something unrelated to the task, to check for forgetting>",
]
```

Essa terceira categoria é a que as pessoas deixam de fora, e é assim que o esquecimento é entregue.

### Reprodutibilidade

Registre o bastante para poder executar de novo: base model e revisão, dataset e a sua divisão exata, seed, todo hiperparâmetro e versões das bibliotecas. O fine-tuning com adapters tem uma superfície de configuração grande o bastante para que "acho que era rank 32" não seja um registro.

Comparar duas execuções só faz sentido quando exatamente uma coisa difere entre elas. Mude o rank *ou* o learning rate, não os dois, e mantenha a seed e os dados fixos. Isso parece óbvio e é violado rotineiramente, em geral porque uma execução demorou o bastante para tornar a paciência cara.

## Prática

1. ▢ A loss de treinamento é 0.2 e está caindo. A loss held-out chegou ao fundo em 0.9 há duzentos passos e agora está em 1.1. O que está acontecendo, e qual checkpoint você entrega?

<details markdown="1"><summary>Verificação</summary>

Overfitting. O modelo agora está se ajustando a ruído específico do conjunto de treinamento.

Entregue o checkpoint do mínimo da held-out, aproximadamente duzentos passos atrás. Depois reduza a capacidade, adicione dados ou pare mais cedo da próxima vez.

</details>

2. ▢ As duas losses se achatam em um nível alto demais para ser útil. Rank 8, targets só de atenção. O que você muda, e o que não muda?

<details markdown="1"><summary>Verificação</summary>

Mude a capacidade: estenda os targets a todas as camadas lineares e aumente o rank. Considere se o learning rate está baixo demais.

Não adicione epochs. Um teto de capacidade não se move com mais passadas pelos mesmos dados. Essa é a definição do diagnóstico.

</details>

3. ▢ A loss held-out melhora o tempo todo. Você entrega. Usuários relatam que o modelo ficou pior em coisas que antes fazia. O que você deixou de medir?

<details markdown="1"><summary>Verificação</summary>

Esquecimento catastrófico. Seu conjunto held-out é tirado da distribuição da sua tarefa, então não consegue ver a degradação em capacidades fora dessa distribuição.

A correção é um conjunto de regressão cobrindo habilidades que você não está treinando: seguimento geral de instruções, comportamento de recusa, outros formatos. Essa é a Lição 24, e essa falha é o motivo de ela existir.

</details>

4. ▢ Qual observação indica com mais força um pipeline quebrado, e não hiperparâmetros ruins?

    - a) A curva de loss estaciona em um valor bem acima de zero
    - b) A loss fica exatamente inalterada ao longo dos cinquenta passos
    - c) A loss held-out sobe enquanto a loss de treinamento cai
    - d) A loss dá um pico para cima em um passo e depois se recupera

<details markdown="1"><summary>Verificação</summary>

**b)** A loss fica exatamente inalterada ao longo dos cinquenta passos.

Um platô é underfitting, um par divergente é overfitting e um pico costuma ser um batch ruim, e todos são comportamentos reais de treinamento. Loss que *não se move nada* significa que nenhum gradiente está chegando a nenhum parâmetro, o que é uma falha de ligação.

</details>

5. ▢ Por que pelo menos uma das suas sondas de geração precisa ser não relacionada à tarefa?

<details markdown="1"><summary>Verificação</summary>

Porque é a única forma barata de perceber o esquecimento durante uma execução. As sondas relacionadas à tarefa e a loss held-out relacionada à tarefa melhoram ambas enquanto as habilidades não relacionadas decaem, então nada do que você já mede vai avisar.

</details>

6. ▢ A loss cai em escada, com quedas em cada fronteira de epoch. Diagnostique.

<details markdown="1"><summary>Verificação</summary>

O modelo está reconhecendo exemplos que já viu. Isso é memorização, visível diretamente na curva. Cada novo epoch produz um degrau para baixo porque os dados já não são novidade.

Confira a loss held-out, que provavelmente está plana ou subindo, e reduza os epochs ou a capacidade.

</details>

## Prática no mundo real

- [ ] Adicione uma divisão held-out e avaliação periódica à sua execução da Lição 11. Encontre o mínimo da held-out.
- [ ] Escreva três sondas de geração, uma delas não relacionada à sua tarefa. Salve as saídas do base model antes do treinamento.
- [ ] Faça overfitting de propósito: treine um adapter de rank generoso em 50 exemplos por muitos epochs e veja as duas curvas se separarem. Guarde o gráfico.
- [ ] Amanhã: escreva um registro de uma página de uma execução real: base model, revisão, dados, divisão, seed, todo hiperparâmetro, versões das bibliotecas.

## Para ir além

- [Artigo: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Modos de falha](../reference/failure-modes.md)
- [Lição 24. O conjunto de regressão](0024-the-regression-suite.md): onde a sonda não relacionada vira um sistema de verdade

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
