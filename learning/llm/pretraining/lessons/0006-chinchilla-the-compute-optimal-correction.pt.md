---
title: "6. Chinchilla: a correção compute-optimal"
description: "Por que o tamanho do modelo e a contagem de tokens devem escalar juntos e como transformar um orçamento de compute em uma contagem de tokens"
type: lesson
---

# Lição 6. Chinchilla: a correção compute-optimal

**Ligação com a missão:** "Dados uma contagem de parâmetros e um orçamento de compute, calcular a contagem de tokens compute-optimal e defendê-la contra uma alternativa subtreinada no estilo de Kaplan" é o terceiro item em O sucesso se parece com isto. A Lição 5 cobriu a recomendação de Kaplan et al.; esta lição cobre o estudo mais amplo que a derrubou e a aritmética para aplicá-lo.
**Fonte principal:** [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Pré-requisitos:** [Lição 5](0005-scaling-laws-what-kaplan-predicted.md)

## Aquecimento

1. ▢ Segundo Kaplan et al., para um orçamento fixo de compute, o treinamento ótimo em eficiência de compute significa treinar o maior modelo que se pode pagar com comparativamente poucos dados, ou um modelo menor com tantos dados quanto o orçamento permitir?

<details markdown="1"><summary>Verificação</summary>

O maior modelo que se pode pagar, treinado com comparativamente poucos dados e interrompido antes da convergência. O fato de modelos maiores serem mais eficientes em amostras é o que faz dessa a alocação recomendada de um orçamento fixo.

</details>

2. ▢ O GPT-3 treinou um modelo de 175 bilhões de parâmetros com 300 bilhões de tokens. Aproximadamente quantos tokens por parâmetro isso dá?

<details markdown="1"><summary>Verificação</summary>

Cerca de 1.7 token por parâmetro (300 bilhões divididos por 175 bilhões).

</details>

## Saiba isto

### Uma varredura muito maior, uma resposta diferente

Hoffmann et al. conduziram o mesmo tipo de estudo de lei de escala que Kaplan et al., mas muito maior e com controle mais cuidadoso: mais de 400 modelos, de 70 milhões a mais de 16 bilhões de parâmetros, treinados com entre 5 bilhões e 500 bilhões de tokens. Ajustando uma lei de escala a essa varredura, chegaram a uma conclusão prática diferente: para um treinamento compute-optimal, o tamanho do modelo e o número de tokens de treinamento devem ser aumentados **na mesma proporção**. Dobrar o orçamento de compute significa dobrar tanto o tamanho do modelo quanto a contagem de tokens, e não, como a recomendação de Kaplan et al. implicava, gastar quase todo o compute extra em um modelo maior.

### A aproximação que faz a aritmética

Os dois artigos usam a mesma aproximação grosseira para quanto compute uma execução de treinamento custa: `FLOPs(N, D) ≈ 6ND`, em que `N` é a contagem de parâmetros e `D` é o número de tokens de treinamento. Hoffmann et al. conferiram essa aproximação diretamente contra uma contagem de FLOPs mais exata para uma faixa de tamanhos de modelo e constataram que a diferença era pequena o bastante para não afetar as suas conclusões. Isso significa que um orçamento de compute `C`, uma contagem de parâmetros `N` e uma contagem de tokens `D` não são três escolhas independentes: fixar quaisquer duas determina a terceira, por meio de `D ≈ C / (6N)`.

### Chinchilla e os números por trás da manchete

Hoffmann et al. treinaram um modelo, o Chinchilla, com 70 bilhões de parâmetros e 1,4 trilhão de tokens, usando o mesmo compute de treinamento que o Gopher (um modelo de 280 bilhões de parâmetros) tinha usado. Isso dá aproximadamente 20 tokens para cada parâmetro (1,4 trilhão dividido por 70 bilhões). As suas próprias projeções de alocação ótima para outros orçamentos de compute caem em uma faixa parecida, sem cair no mesmo número exato todas as vezes: projeta-se que um modelo compute-optimal de 175 bilhões de parâmetros queira mais de 4,2 trilhões de tokens (cerca de 24 por parâmetro), e um de 280 bilhões de parâmetros, cerca de 6,8 trilhões de tokens (cerca de 24 por parâmetro) em um orçamento maior. A conclusão certa é "aproximadamente 20 a 25 tokens por parâmetro na alocação compute-optimal em toda a faixa que este artigo verificou", e não uma única constante universal.

Ao lado disso, os 175 bilhões de parâmetros do GPT-3 com 300 bilhões de tokens, cerca de 1.7 token por parâmetro, do aquecimento desta lição, estão muito abaixo dessa faixa. Essa distância é exatamente o que o resumo do artigo do Chinchilla quer dizer ao chamar os grandes modelos de linguagem contemporâneos de "significativamente subtreinados": o mesmo compute de treinamento poderia ter ido para um modelo menor treinado até uma loss mais baixa, ou para o modelo do mesmo tamanho treinado com várias vezes mais dados, e qualquer um dos dois teria usado o compute melhor do que o que foi de fato gasto.

### O resultado que fez a correção pegar

Treinado no orçamento de compute do Gopher, mas com um quarto da sua contagem de parâmetros e quatro vezes a sua contagem de tokens, o Chinchilla superou de forma uniforme e significativa o Gopher (280B), o GPT-3 (175B), o Jurassic-1 (178B) e o Megatron-Turing NLG (530B), vários deles várias vezes maiores, em uma ampla gama de avaliações downstream, incluindo 67.5% no MMLU, então o estado da arte, mais de 7 pontos acima do Gopher. Ter um quarto do tamanho do Gopher também tornou o Chinchilla consideravelmente mais barato de rodar na inferência, um benefício separado, de tempo de implantação, que o treinamento compute-optimal traz além do argumento de tempo de treinamento que esta lição faz.

## Prática

1. ▢ Uma equipe está treinando um modelo com 13 bilhões de parâmetros e quer cair na faixa de aproximadamente 20 a 25 tokens por parâmetro do Chinchilla. Aproximadamente quantos tokens de treinamento isso implica?

<details markdown="1"><summary>Verificação</summary>

Aproximadamente 260 a 325 bilhões de tokens (13 bilhões vezes 20 a 25). Qualquer extremo dessa faixa é uma resposta defensável; um número bem fora dela, como a razão de 1.7 por parâmetro do GPT-3, não é.

</details>

2. ▢ Uma equipe tem um orçamento de compute de `1.2 × 10^22` FLOPs e planeja treinar um modelo de 10 bilhões de parâmetros. Usando `FLOPs(N, D) ≈ 6ND`, aproximadamente quantos tokens esse orçamento comporta?

<details markdown="1"><summary>Dica</summary>

Resolva `D ≈ C / (6N)` com `C = 1.2 × 10^22` e `N = 10^10`.

</details>

<details markdown="1"><summary>Verificação</summary>

Cerca de 200 bilhões de tokens: `1.2 × 10^22 / (6 × 10^10) = 2 × 10^11`, que são 200 bilhões, cerca de 20 tokens por parâmetro e bem dentro da faixa que esta lição dá.

</details>

3. ▢ Qual destas caracteriza melhor a diferença prática entre a recomendação de Kaplan et al. e a correção de Hoffmann et al., para um orçamento fixo de compute?

    - a) Kaplan recomenda gastar a maior parte do orçamento em um modelo maior com comparativamente poucos dados; Hoffmann recomenda escalar o tamanho do modelo e a contagem de tokens na mesma proporção
    - b) Os dois artigos chegam a recomendações idênticas, apenas formuladas de modo diferente
    - c) Kaplan diz que o tamanho do modelo é irrelevante para a loss; Hoffmann diz que só o tamanho do modelo importa
    - d) Hoffmann defende que um modelo maior é sempre pior do que um menor com o mesmo compute

<details markdown="1"><summary>Verificação</summary>

**a)** é a diferença real que esta lição e a Lição 5 percorrem. (b) apaga uma discordância real e de consequências práticas entre os dois artigos. (c) e (d) não descrevem as afirmações de nenhum dos artigos.

</details>

4. ▢ O GPT-3 treinou 175 bilhões de parâmetros com 300 bilhões de tokens, cerca de 1.7 token por parâmetro. Segundo a faixa compute-optimal do Chinchilla, de aproximadamente 20 a 25 tokens por parâmetro, o GPT-3 estava mais perto de sobretreinado ou de subtreinado em dados, em relação ao seu tamanho?

<details markdown="1"><summary>Verificação</summary>

Subtreinado. A sua razão está mais de dez vezes abaixo da faixa que os resultados do Chinchilla indicam ser compute-optimal, o que significa que o mesmo compute de treinamento poderia plausivelmente ter ido para um modelo menor treinado até uma loss mais baixa, ou para o mesmo modelo de 175 bilhões de parâmetros treinado com substancialmente mais dados.

</details>

## Prática no mundo real

- [ ] Encontre a contagem de parâmetros e a contagem de tokens de treinamento publicadas de um modelo aberto lançado depois de 2022 (Llama, Mistral ou similares publicam as duas). Calcule a sua razão de tokens por parâmetro e compare-a com a faixa de aproximadamente 20 a 25 desta lição.
- [ ] Usando `FLOPs(N, D) ≈ 6ND`, estime o compute de treinamento (em FLOPs) que a execução de treinamento real do GPT-3 (175 bilhões de parâmetros, 300 bilhões de tokens) usou e, separadamente, estime o compute de que uma execução compute-optimal de 175 bilhões de parâmetros teria precisado com 4,2 trilhões de tokens. Compare os dois números.
- [ ] Amanhã: escolha um orçamento hipotético de compute à sua escolha (qualquer ordem de magnitude) e calcule, no papel, tanto uma alocação no estilo de Kaplan (favorecer um modelo muito maior, manter os tokens comparativamente fixos) quanto uma alocação no estilo do Chinchilla (escalar os dois juntos) para esse mesmo orçamento. Anote os dois pares `(N, D)` resultantes lado a lado.

## Para ir além

- [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

As etapas 1 e 2 decidiram com o que o modelo treina e como ele é tokenizado; esta etapa decidiu quanto disso usar para um dado tamanho. A etapa 4 se volta para como uma execução de treinamento realmente leva tanto compute a mais de um dispositivo ao mesmo tempo.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
