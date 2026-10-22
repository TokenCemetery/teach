---
title: "5. Leis de escala: o que Kaplan previu"
description: "Uma lei de potência empírica permite prever a loss de uma execução de treinamento antes de pagar por ela, e o que isso previa sobre como gastar um orçamento de compute"
type: lesson
---

# Lição 5. Leis de escala: o que Kaplan previu

**Ligação com a missão:** "Dados uma contagem de parâmetros e um orçamento de compute, calcular a contagem de tokens compute-optimal e defendê-la contra uma alternativa subtreinada no estilo de Kaplan" é o terceiro item em O sucesso se parece com isto. Esta lição cobre o que Kaplan et al. encontraram e recomendaram; a Lição 6 cobre a correção que mudou a recomendação.
**Fonte principal:** [Artigo científico: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
**Pré-requisitos:** [Lição 4](0004-sentencepiece-and-the-vocabulary-size-tradeoff.md)

## Aquecimento

1. ▢ Nomeie um eixo em que um vocabulário de tokenizer maior é pior do que um menor.

<details markdown="1"><summary>Verificação</summary>

Um vocabulário maior significa uma tabela de embeddings e de projeção de saída maior (puro número de parâmetros) e espalha o sinal de treinamento de forma mais rarefeita por mais tokens distintos, então qualquer token específico é visto com menos frequência por passada pelo mesmo corpus.

</details>

## Saiba isto

### O que uma lei de escala realmente é

Uma **lei de escala**, neste contexto, é uma relação empírica de lei de potência: a loss held-out de um modelo cai suavemente em função do tamanho do modelo, do tamanho do dataset ou do compute de treinamento, em uma faixa ampla o bastante para ser útil na previsão. Kaplan et al. ajustaram exatamente isso, constatando que a loss escala como uma lei de potência com cada uma dessas três quantidades individualmente, valendo em tendências que cobrem mais de sete ordens de magnitude de escala. Outras escolhas de arquitetura, como a forma de dividir um orçamento fixo de parâmetros entre largura e profundidade, mostraram importar comparativamente pouco dentro de uma faixa ampla, uma vez levado em conta o próprio tamanho do modelo.

O valor prático de uma lei de escala é a previsão: se a loss segue uma curva suave e ajustada em relação ao tamanho do modelo, ao tamanho do dataset e ao compute, uma equipe pode prever aproximadamente o desempenho de uma execução de treinamento de determinado tamanho e orçamento antes de gastar o compute para rodá-la, em vez de descobrir só depois do fato.

### Modelos maiores aprendem mais por token

Uma das constatações centrais de Kaplan et al. é que modelos maiores são significativamente mais eficientes em amostras: para alcançar uma dada loss, um modelo maior precisa ver menos dados do que um modelo menor precisaria para alcançar a mesma loss. Combinada com as relações ajustadas entre loss, compute e as duas coisas que o compute compra (um modelo maior ou mais dados para treiná-lo), isso implica uma resposta específica sobre como gastar um orçamento fixo de compute: o treinamento ótimo em eficiência de compute significa treinar um modelo muito grande com uma quantidade comparativamente modesta de dados e parar bem antes de convergir nesses dados, em vez de treinar um modelo menor até a convergência em mais dados.

### Como essa recomendação se parecia na prática

Essa constatação moldou a forma como uma geração de modelos grandes foi realmente treinada: escalar a contagem de parâmetros de forma agressiva e manter a contagem de tokens comparativamente fixa ou apenas modestamente aumentada. O GPT-3, por exemplo, treinou um modelo de 175 bilhões de parâmetros com 300 bilhões de tokens. Esta lição deixa esse número aqui sem mais comentários; a Lição 6 volta a ele diretamente quando houver uma segunda lei de escala para compará-lo.

## Prática

1. ▢ O que significa, precisamente, a loss "escalar como uma lei de potência" com o tamanho do modelo, no sentido em que Kaplan et al. usam isso?

    - a) A loss diminui exatamente pela mesma quantidade fixa para cada aumento fixo no tamanho do modelo
    - b) A loss cai suavemente seguindo uma curva ajustada, valendo em uma faixa ampla de tamanhos de modelo, e é isso que torna possível a previsão
    - c) A loss se torna zero quando o modelo é grande o bastante
    - d) A loss depende apenas do tamanho do modelo e nada da quantidade de dados de treinamento

<details markdown="1"><summary>Verificação</summary>

**b)** Um ajuste de lei de potência suave o bastante, e validado em ordens de magnitude suficientes, para prever a partir dele. (a) descreve uma relação linear, e não uma lei de potência. (c) não é afirmado em lugar nenhum do artigo. (d) contradiz a constatação separada do próprio artigo de uma lei de escala com o tamanho do dataset.

</details>

2. ▢ Segundo Kaplan et al., qual alcança uma loss-alvo fixa usando menos dados de treinamento: um modelo maior ou um menor?

<details markdown="1"><summary>Verificação</summary>

Um modelo maior. Modelos maiores são mais eficientes em amostras, o que significa que precisam de menos dados para alcançar a mesma loss que um modelo menor precisaria de mais dados para alcançar.

</details>

3. ▢ Dado um orçamento fixo de compute e as constatações de Kaplan et al., qual alocação a análise deles recomenda: um modelo muito grande treinado com comparativamente poucos dados e interrompido bem antes da convergência, ou um modelo menor treinado até a convergência com tantos dados quanto o orçamento permitir?

<details markdown="1"><summary>Dica</summary>

Isso decorre diretamente de combinar "modelos maiores são mais eficientes em amostras" com um orçamento fixo de compute: o compute gasto em dados é compute não gasto em tamanho de modelo, e o artigo constatou que um desses dois usos do compute compensava mais do que o outro.

</details>

<details markdown="1"><summary>Verificação</summary>

O modelo muito grande treinado com comparativamente poucos dados, interrompido antes da convergência. Essa é a recomendação declarada do próprio Kaplan et al. para um treinamento ótimo em eficiência de compute sob um orçamento fixo.

</details>

## Prática no mundo real

- [ ] Encontre a contagem de parâmetros e a contagem de tokens de treinamento relatada de dois ou três modelos conhecidos lançados até um ou dois anos depois do artigo de Kaplan (de 2020 a cerca de 2022). Anote se as suas contagens de tokens ficaram mais ou menos fixas enquanto as contagens de parâmetros cresceram, que é o que seguir a recomendação desta lição pareceria.
- [ ] Releia o resumo do artigo de Kaplan (linkado acima) e, em uma frase, diga o que "parar significativamente antes da convergência" significa para uma execução de treinamento: o que continuar treinando de fato compraria e que esta recomendação diz não valer o seu compute?
- [ ] Amanhã: sem olhar a Lição 6, escreva uma previsão de uma frase: dado que a construção de datasets (etapa 1 desta trilha) é cara e lenta de escalar, e que a pura contagem de parâmetros é comparativamente fácil de escalar adicionando mais aceleradores, que pressão prática pode ter empurrado as execuções de treinamento reais em direção à recomendação de Kaplan com ainda mais força do que as curvas de loss sozinhas justificariam?

## Para ir além

- [Artigo científico: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
