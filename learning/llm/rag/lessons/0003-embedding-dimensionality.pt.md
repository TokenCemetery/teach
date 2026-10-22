---
title: "3. Trade-offs de dimensionalidade de embeddings"
description: "Por que um vetor de embedding maior não é de graça, e quando é seguro truncá-lo em vez de escolher um modelo menor"
type: lesson
---

# Lição 3. Trade-offs de dimensionalidade de embeddings

**Ligação com a missão:** Esta é a lição final da etapa 2: escolher um modelo de embedding (lição 2) não termina até que o tamanho de sua saída seja pesado contra o que o orçamento de armazenamento e de latência de um corpus de fato comporta.
**Fonte principal:** [Artigo científico: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
**Pré-requisitos:** [Lição 2](0002-embedding-models-and-similarity.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que um bi-encoder gera o embedding de uma consulta e de uma passagem separadamente em vez de em conjunto?

<details markdown="1"><summary>Verificação</summary>

Para que cada passagem possa ter o embedding gerado uma vez, com antecedência, e ser armazenada; só a consulta precisa de embedding na hora da busca, permitindo compará-la de forma barata com vetores de passagem pré-calculados. Gerar em conjunto (um cross-encoder) exige rodar o modelo sobre cada par, o que não escala para um corpus grande.

</details>

2. ▢ Por que a similaridade de cosseno e o produto escalar produzem o mesmo ranking apenas quando os vetores são normalizados para comprimento unitário?

<details markdown="1"><summary>Verificação</summary>

O produto escalar é a similaridade de cosseno escalada pelas magnitudes dos dois vetores. Quando ambas são fixadas em comprimento unitário, esse fator de escala é idêntico em todo par, então as duas métricas ranqueiam de forma idêntica; quando as magnitudes variam, o produto escalar recompensa implicitamente os vetores maiores.

</details>

## Saiba isto

### Dimensionalidade é um custo, não um botão gratuito de qualidade

Um embedding de dimensão mais alta pode codificar mais nuance, mas cada uma de suas dimensões custa algo concreto: o armazenamento escala linearmente com a dimensão (um vetor de 1536 dimensões em float32 ocupa `1536 × 4 bytes = 6,144 bytes`, cerca de 6 KB, contra `256 × 4 = 1,024 bytes` de um vetor de 256 dimensões, cerca de 1 KB, seis vezes menos), e tanto a memória do índice quanto o cálculo de distância por candidato escalam do mesmo modo. Em um milhão de chunks, essa diferença é de 6 GB contra 1 GB só para os próprios vetores, antes da sobrecarga do próprio índice. Um embedding maior não é automaticamente a melhor escolha; é uma escolha que precisa ser justificada contra o que custa, do mesmo modo que um KV cache maior ou um tamanho de batch maior tinha de ser justificado contra o orçamento real de uma carga de trabalho em outros contextos de serving.

### Matryoshka Representation Learning: o truncamento como recurso projetado, não um hack

Normalmente, truncar um vetor de embedding para menos dimensões não é seguro: nada na forma como um modelo de embedding padrão foi treinado ordena suas dimensões por importância, então cortar um vetor normal de 768 dimensões para 256 poderia descartar informação de forma imprevisível e degradar a qualidade muito mais do que a contagem de dimensões sozinha sugeriria. O **Matryoshka Representation Learning (MRL)** treina um modelo de outra forma: sua loss otimiza explicitamente prefixos do vetor completo (as primeiras 256 dimensões de um embedding de 1536 dimensões, por exemplo) para que eles mesmos sejam embeddings utilizáveis e significativos, aninhados dentro do completo como as bonecas menores dentro de uma boneca matryoshka. Isso significa que um modelo treinado com MRL pode ser truncado depois, com um custo de qualidade limitado e previsível, permitindo trocar dimensionalidade por armazenamento e latência sem retreinar nem gerar novamente os embeddings do corpus inteiro em outro tamanho. Isso só vale para modelos de fato treinados dessa maneira; truncar um modelo que não foi volta ao caso inseguro e imprevisível.

![Um único vetor de 1536 dimensões desenhado como uma barra, com linhas tracejadas marcando onde terminam suas primeiras 256 dimensões e suas primeiras 768 dimensões. Três intervalos entre colchetes acima da barra, todos começando na dimensão 0, mostram que parar em 256, em 768 ou ler as 1536 dimensões completas resulta, em cada caso, em um embedding utilizável e significativo, porque o Matryoshka Representation Learning treinou cada prefixo do vetor para funcionar por conta própria, ao contrário de um modelo de embedding padrão, em que só o vetor completo é significativo.](images/matryoshka-prefix-embeddings.svg)

### Decidir a dimensionalidade certa significa medir, não presumir

A dimensionalidade certa para um dado corpus não é um número para chutar; é um número para medir. Usando um modelo MRL (ou comparando vários tamanhos candidatos de modelo), a qualidade da recuperação, da forma mais direta o recall@k contra um conjunto de consultas rotulado ou sintético (assunto da etapa 6), pode ser medida em cada dimensionalidade candidata sobre o corpus e o padrão de consultas em questão. A dimensionalidade que vale entregar é a menor que ainda atinge o nível de qualidade que a carga de trabalho exige, não a maior disponível, e não um padrão escolhido sem verificar o que ele custa contra o que ele traz.

## Prática

1. ▢ Um corpus tem 2 milhões de chunks. Calcule a diferença de armazenamento, em gigabytes, entre gerar o embedding dele com 1536 dimensões e com 256 dimensões, ambos em float32.

<details markdown="1"><summary>Dica</summary>

Os bytes por vetor são `dimensões × 4 bytes`. Multiplique por 2 milhões e depois converta para gigabytes.

</details>

<details markdown="1"><summary>Verificação</summary>

1536 dimensões: `1536 × 4 = 6,144 bytes` por vetor, `× 2,000,000 ≈ 12.3 GB`. 256 dimensões: `256 × 4 = 1,024 bytes` por vetor, `× 2,000,000 ≈ 2.0 GB`. A diferença é de aproximadamente 10,3 GB, cerca de seis vezes menos armazenamento com 256 dimensões.

</details>

2. ▢ Uma equipe trunca os vetores de um modelo de embedding padrão (não MRL) de 768 dimensões para 256 dimensões para economizar armazenamento, e a qualidade da recuperação desaba muito mais do que a redução de dimensões sozinha sugeriria. Qual é o provável erro?

<details markdown="1"><summary>Verificação</summary>

O modelo não foi treinado com Matryoshka Representation Learning, então nada ordenou suas dimensões por importância nem fez de qualquer prefixo do vetor um embedding significativo por conta própria. Truncá-lo descarta informação de forma imprevisível, e não do modo limitado e projetado que seria o truncamento de um modelo treinado com MRL.

</details>

3. ▢ O que um modelo de embedding treinado com MRL permite a uma equipe fazer que um modelo de embedding padrão não permite?

<details markdown="1"><summary>Verificação</summary>

Truncar o vetor de embedding completo para uma dimensionalidade menor depois, com um custo de qualidade limitado e previsível, trocando armazenamento e latência por qualidade sem retreinar o modelo nem gerar novamente os embeddings do corpus em outro tamanho fixo.

</details>

4. ▢ Como uma equipe deve decidir qual dimensionalidade de embedding de fato usar para o seu corpus, em vez de adotar por padrão o tamanho de saída completo do modelo?

<details markdown="1"><summary>Verificação</summary>

Medir a qualidade da recuperação, da forma mais direta algo como recall@k contra um conjunto de consultas rotulado ou sintético, representativo do corpus e do padrão de consultas reais, em várias dimensionalidades candidatas, e escolher a menor que ainda atinge o nível de qualidade que a carga de trabalho exige, em vez de presumir que a maior dimensionalidade disponível é necessária ou que uma menor é automaticamente "boa o bastante".

</details>

5. ▢ Qual afirmação é verdadeira sobre a dimensionalidade de embeddings?

    - a) Uma dimensionalidade de embedding maior sempre melhora a qualidade da recuperação o bastante para justificar seu custo
    - b) Truncar os vetores de qualquer modelo de embedding é igualmente seguro, independentemente de como o modelo foi treinado
    - c) A dimensionalidade é um custo (armazenamento, memória do índice, cálculo por candidato) que deve ser dimensionado para o menor valor que atinja um nível de qualidade medido
    - d) Modelos treinados com MRL não podem ser truncados; eles oferecem apenas um único tamanho de saída fixo

<details markdown="1"><summary>Verificação</summary>

**c)** Os custos de armazenamento e de cálculo escalam com a dimensionalidade, então o tamanho certo é o menor valor de que um nível de qualidade medido de fato precisa. (a) é falsa: o custo precisa ser pesado contra o benefício medido, não presumido. (b) é falsa: truncar um modelo não MRL é imprevisível e pode destruir muito mais sinal do que a contagem de dimensões implica. (d) é falsa: esse truncamento flexível é exatamente o que o treinamento MRL foi construído para permitir.

</details>

## Prática no mundo real

- [ ] Verifique se o modelo de embedding que você usa (ou pretende usar) foi treinado com Matryoshka Representation Learning e, se foi, para quais dimensionalidades ele suporta o truncamento.
- [ ] Calcule o custo de armazenamento, em bytes por vetor e para o tamanho real do seu corpus, na dimensionalidade completa do seu modelo e em um tamanho candidato menor.
- [ ] Amanhã: se você tiver um conjunto de consultas rotulado ou sintético, meça o recall em duas dimensionalidades de embedding diferentes e compare a diferença de qualidade com a diferença de armazenamento.

## Para ir além

- [Artigo científico: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
- [Artigo científico: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers e Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
