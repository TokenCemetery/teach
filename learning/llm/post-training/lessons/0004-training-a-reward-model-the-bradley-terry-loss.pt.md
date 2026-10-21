---
title: "4. Treinando um reward model: a loss de Bradley-Terry"
description: "Um reward model nunca vê uma pontuação absoluta no treinamento, apenas qual de duas completions um humano preferiu"
type: lesson
---

# Lição 4. Treinando um reward model: a loss de Bradley-Terry

**Ligação com a missão:** "Treinar um reward model em pares de preferência usando a loss de Bradley-Terry e identificar uma completion com reward hacking vinda de uma policy treinada contra ele" é o segundo item de O sucesso se parece com isto. Esta lição cobre o treinamento do reward model; a lição 5 cobre o que pode dar errado quando uma policy é otimizada contra ele.
**Fonte principal:** [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Pré-requisitos:** [Lição 3](0003-loss-masking-on-non-assistant-tokens.md)

## Aquecimento

1. ▢ O que o loss masking em tokens que não são do assistente faz, mecanicamente, durante o treinamento de SFT?

<details markdown="1"><summary>Verificação</summary>

Ele dá à posição de cada token de prompt ou de turno que não é do assistente um rótulo que a função de loss é instruída a ignorar, de modo que só as posições do assistente (da resposta) contribuem com gradiente, ainda que os tokens do prompt continuem presentes como entrada em que o modelo se condiciona.

</details>

2. ▢ O que quebra no treinamento de SFT se esse mascaramento for pulado?

<details markdown="1"><summary>Verificação</summary>

O sinal de gradiente é gasto, ou diluído, em aprender a prever os próprios tokens do prompt, que não é a habilidade que o SFT deve ensinar, em vez de ficar concentrado inteiramente nos tokens da resposta que o modelo deveria de fato aprender a produzir.

</details>

## Saiba isto

### Coletando dados de preferência

Um reward model precisa de dados que digam qual de duas saídas do modelo é melhor, e não qual deveria ter sido a melhor saída palavra por palavra. Ouyang et al. coletam isso apresentando aos rotuladores várias saídas (eles usam entre 4 e 9) para o mesmo prompt e pedindo que ranqueiem o conjunto inteiro, em vez de sempre comparar apenas duas por vez. Um ranking de `K` saídas produz todas as comparações pareadas dentro dele, `K` tomados 2 a 2, de modo que uma única tarefa de ranking rende muitos pares de treinamento de uma vez.

### De onde vem o reward model

Um reward model não é treinado a partir do zero. Ouyang et al. descrevem partir do próprio modelo SFT, com a sua camada final de unembedding, a parte que transforma um estado oculto em probabilidades do próximo token, removida e substituída por uma camada que produz um único escalar. O reward model reaproveita tudo o que o modelo SFT já aprendeu sobre linguagem e sobre o comportamento-alvo, redirecionado para produzir um número, uma pontuação, para um dado prompt e uma dada completion, em vez de uma distribuição sobre o próximo token.

### A loss de Bradley-Terry

Dada uma completion preferida `y_w` ("vencedora") e uma completion rejeitada `y_l` ("perdedora") para o mesmo prompt `x`, e as saídas escalares `r(x, y_w)` e `r(x, y_l)` do reward model para cada uma, Ouyang et al. treinam o reward model com esta loss:

```text
loss(θ) = -E[log(σ(r_θ(x, y_w) - r_θ(x, y_l)))]
```

onde `σ` é a função sigmoide logística. Essa é a **loss de Bradley-Terry**: ela trata a probabilidade de um humano preferir `y_w` a `y_l` como a sigmoide da diferença entre as duas pontuações e treina o reward model para fazer essa probabilidade prevista coincidir com o que o rotulador humano de fato escolheu. Empurrar essa loss para baixo significa empurrar `r(x, y_w) - r(x, y_l)` para cima: o modelo é treinado para fazer a pontuação da completion preferida ficar acima da rejeitada, por uma margem proporcional à confiança com que a sigmoide precisa favorecê-la.

### Por que a escala absoluta da recompensa não tem significado por si só

Note que a loss depende apenas da *diferença* entre as duas pontuações, nunca de qualquer uma delas isoladamente. Somar a mesma constante a toda recompensa que o modelo produzir deixaria todas as diferenças, e portanto a loss inteira, completamente inalteradas. Isso significa que nada no treinamento força as pontuações do reward model a uma escala absoluta específica; só a ordenação relativa (e o tamanho das diferenças) entre completions preferidas e rejeitadas é restringida. Ouyang et al. tratam isso diretamente: como a loss é invariante a um deslocamento, eles normalizam o reward model com um viés de modo que as demonstrações dos rotuladores tenham pontuação média 0, antes de usá-lo em reinforcement learning, dando à escala de outro modo arbitrária uma âncora fixa contra a qual ser medida.

### Por que as comparações de um mesmo ranking ficam juntas

Tratar cada uma das `K` tomadas 2 a 2 comparações de uma única tarefa de ranking como um exemplo de treinamento independente, embaralhado separadamente, causa um problema específico: como o mesmo pequeno conjunto de completions reaparece em muitas dessas comparações, uma única passada sobre dados construídos assim tende a sofrer overfitting, já que cada completion acaba sendo reutilizada em `K - 1` comparações correlacionadas. A correção de Ouyang et al. é tratar todas as comparações de uma tarefa de ranking como um único elemento de batch durante o treinamento, em vez de embaralhá-las independentemente no conjunto de dados mais amplo, o que, segundo eles, melhorou a acurácia e a loss de validação em comparação com tratar cada comparação pareada como totalmente independente.

## Prática

1. ▢ Um reward model produz `r(x, y_w) = 2.0` e `r(x, y_l) = 1.0` para um par, e `r(x, y_w) = 12.0` e `r(x, y_l) = 11.0` para um segundo par, de um prompt diferente. A loss de Bradley-Terry trata esses dois pares de forma diferente?

<details markdown="1"><summary>Dica</summary>

A loss é uma função de `r(x, y_w) - r(x, y_l)`, e não de qualquer um dos valores isoladamente.

</details>

<details markdown="1"><summary>Verificação</summary>

Não. Os dois pares têm a mesma diferença, `1.0`, e a loss depende apenas dessa diferença, e não das pontuações absolutas. É exatamente por isso que a escala absoluta do reward model não tem significado sem uma âncora externa.

</details>

2. ▢ De onde vêm de fato os pesos iniciais de um reward model, segundo Ouyang et al.?

<details markdown="1"><summary>Verificação</summary>

Do modelo SFT, com a sua camada final de unembedding removida e substituída por uma camada que produz um único escalar, e não de um modelo novo, inicializado aleatoriamente.

</details>

3. ▢ Um rotulador ranqueia 4 completions (`K = 4`) para um único prompt. Quantas comparações pareadas essa única tarefa de ranking produz para o treinamento?

<details markdown="1"><summary>Verificação</summary>

6 (`4` tomados 2 a 2, que é `(4 × 3) / 2 = 6`).

</details>

4. ▢ Por que Ouyang et al. mantêm todas as comparações de uma tarefa de ranking juntas como um único elemento de batch, em vez de embaralhar cada comparação pareada independentemente no conjunto de treinamento?

    - a) Faz o reward model treinar mais rápido sem efeito na acurácia
    - b) Embaralhá-las independentemente causa overfitting, já que o mesmo pequeno conjunto de completions é reutilizado em muitas comparações correlacionadas dentro de uma tarefa de ranking
    - c) A loss de Bradley-Terry não pode ser calculada a menos que as comparações sejam agrupadas assim
    - d) É necessário para que as pontuações do reward model caiam em uma faixa numérica fixa

<details markdown="1"><summary>Verificação</summary>

**b)** é a razão que Ouyang et al. dão diretamente: completions correlacionadas e reutilizadas nas comparações de uma tarefa de ranking fazem uma única passada sofrer overfitting se forem embaralhadas independentemente. As alternativas (a), (c) e (d) não descrevem o problema real nem a sua correção.

</details>

## Prática no mundo real

- [ ] Encontre um dataset público de preferências (muitos são publicados para treinar reward models) e verifique quantas completions são ranqueadas por prompt, e se o formato divulgado já reflete comparações pareadas ou um ranking completo.
- [ ] Calcule, à mão, o termo da sigmoide da loss de Bradley-Terry para uma diferença de recompensa de `0` (nenhum sinal de preferência) e para uma diferença positiva grande, e descreva em uma frase como a loss se comporta em cada extremo.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 5: se um reward model só é treinado para ranquear as completions que humanos de fato lhe mostraram, o que pode dar errado quando uma policy está livre para gerar qualquer completion, buscando o que quer que pontue mais alto?

## Para ir além

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
