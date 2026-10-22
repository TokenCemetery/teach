---
title: "4. Índices ANN: HNSW e IVF"
description: "Por que a busca vetorial troca exatidão por velocidade, e como IVF e HNSW expõem cada um esse trade-off como um botão ajustável"
type: lesson
---

# Lição 4. Índices ANN: HNSW e IVF

**Ligação com a missão:** A etapa 3 abre a parte de alvo móvel da missão, montar a busca sobre um corpus real: um índice é o que torna a busca vetorial rápida o bastante para rodar, ao custo de um trade-off entre recall e latência que esta lição nomeia antes de a lição 5 torná-lo concreto no pgvector.
**Fonte principal:** [Artigo científico: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov e Yashunin, 2018](https://arxiv.org/abs/1603.09320)
**Pré-requisitos:** [Lição 3](0003-embedding-dimensionality.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Um corpus tem 2 milhões de chunks. Aproximadamente quanto armazenamento ocupa gerar o embedding dele com 1536 dimensões em float32, em comparação com 256 dimensões?

<details markdown="1"><summary>Verificação</summary>

Cerca de 12,3 GB com 1536 dimensões contra cerca de 2,0 GB com 256 dimensões, já que os bytes por vetor escalam linearmente com a contagem de dimensões (`dimensões × 4 bytes`).

</details>

2. ▢ O que o Matryoshka Representation Learning permite fazer com um vetor de embedding que um modelo de embedding padrão não permite com segurança?

<details markdown="1"><summary>Verificação</summary>

Truncá-lo para menos dimensões depois do treinamento, com um custo de qualidade limitado e previsível, já que os prefixos de um modelo treinado com MRL são, eles mesmos, embeddings significativos. As dimensões de um modelo padrão não são ordenadas por importância, então truncar um deles é imprevisível.

</details>

## Saiba isto

### Por que a busca exata não escala

Encontrar de forma exata os verdadeiros vizinhos mais próximos de uma consulta significa compará-la com cada vetor do corpus. Isso é linear no tamanho do corpus: dobrar o corpus dobra o tempo de busca e, com milhões de chunks, a comparação por força bruta fica lenta demais para rodar na hora da consulta. Um índice de **vizinho mais próximo aproximado (ANN)** aceita uma pequena quantidade controlável de inexatidão, devolvendo vetores que muito provavelmente estão próximos dos verdadeiros vizinhos mais próximos, sem garantia de serem exatamente eles, em troca de tempos de busca que não escalam linearmente com o tamanho do corpus.

### IVF: busque apenas nos clusters próximos

O **IVF (inverted file index)** particiona o espaço vetorial em clusters com antecedência (comumente via k-means), atribuindo cada vetor ao centroide de cluster mais próximo. Na hora da consulta, em vez de varrer cada vetor, o IVF busca apenas nos `nprobe` clusters mais próximos da consulta, em que `nprobe` é uma contagem ajustável. Um `nprobe` baixo (buscar apenas o cluster mais próximo) é rápido, mas corre o risco de perder verdadeiros vizinhos que por acaso estão em um cluster vizinho perto da fronteira. Um `nprobe` alto (buscar muitos ou todos os clusters) se aproxima do recall da busca exata ao custo da busca exata. O IVF também carrega um custo de construção único: a etapa de clusterização precisa de uma amostra representativa dos vetores do corpus para posicionar bem os centroides.

### HNSW: um grafo navegável, percorrido de cima para baixo

O **HNSW (hierarchical navigable small world)** constrói um grafo multicamada em vez de clusters: cada vetor é um nó, conectado a outros vetores próximos por arestas, com camadas mais esparsas no topo permitindo saltos longos pelo espaço vetorial e uma camada inferior densa permitindo busca local precisa. Uma consulta começa na camada esparsa do topo, salta de forma gulosa em direção ao nó conectado mais próximo e desce camada por camada, refinando sua posição até chegar à camada inferior densa. O botão ajustável aqui é o `ef_search`, quantos candidatos a busca acompanha a cada passo: um `ef_search` baixo encontra uma resposta rápido, mas pode se contentar com um nó localmente bom que não é o verdadeiro mais próximo; um `ef_search` alto explora mais candidatos, trocando velocidade por recall, o mesmo formato de trade-off que o `nprobe` faz para o IVF.

![Dois painéis. À esquerda, IVF: quatro clusters de vetores, cada um com um centroide. A consulta fica entre dois clusters próximos, sombreados e pesquisados, enquanto dois clusters mais distantes ficam sem sombreamento e são ignorados, um nprobe baixo pesquisando apenas os próximos. À direita, HNSW: três camadas de grafo empilhadas, esparsas no topo e densas embaixo, com um caminho descendo a partir de um ponto de entrada na camada superior, saltando para nós progressivamente mais próximos a cada camada abaixo, refinando sua posição até alcançar o vizinho mais próximo na camada inferior densa.](images/ivf-vs-hnsw.svg)

### O formato geral: uma curva de recall/latência, não uma única resposta certa

Os dois índices expõem um botão (`nprobe` para o IVF, `ef_search` para o HNSW) que ajusta um ponto específico em uma curva de recall contra latência para um dado corpus e índice. O HNSW geralmente cai em um ponto melhor dessa curva que o IVF, recall mais alto para a mesma latência, ao custo de mais memória (a própria estrutura do grafo) e de uma construção de índice mais lenta. Nenhum dos índices tem uma configuração universalmente correta: o ponto certo depende do orçamento de latência da carga de trabalho e de quanta perda de recall uma etapa posterior, como o reranking, consegue absorver sem que o resultado final sofra, que é exatamente o que as métricas de recuperação da etapa 6 existem para medir em vez de presumir.

## Prática

1. ▢ Por que a busca exata de vizinho mais próximo por força bruta não escala para um corpus de milhões de vetores, e o que um índice ANN abre mão para corrigir isso?

<details markdown="1"><summary>Verificação</summary>

A busca exata compara a consulta com cada vetor, então seu custo cresce linearmente com o tamanho do corpus, ficando lento demais com milhões de vetores. Um índice ANN abre mão da garantia de encontrar de forma exata os verdadeiros vizinhos mais próximos, aceitando uma pequena chance controlável de perder um, em troca de tempos de busca que não escalam do mesmo jeito.

</details>

2. ▢ Para um índice IVF, descreva o que acontece em cada extremo do parâmetro `nprobe`: `nprobe = 1` contra `nprobe` ajustado para buscar todos os clusters.

<details markdown="1"><summary>Verificação</summary>

`nprobe = 1` busca apenas o cluster mais próximo: o mais rápido, mas pode perder um verdadeiro vizinho mais próximo que esteja em um cluster vizinho perto da fronteira, especialmente se a consulta cair perto da borda de um cluster. `nprobe` ajustado para buscar todos os clusters se aproxima da busca exata: o recall mais alto, mas ao custo da busca exata, já que deixa de pular a maior parte do corpus.

</details>

3. ▢ Como o parâmetro `ef_search` do HNSW exerce para o HNSW o mesmo papel que o `nprobe` exerce para o IVF?

<details markdown="1"><summary>Dica</summary>

Pense no que cada parâmetro controla: quanto do índice é examinado antes de devolver uma resposta.

</details>

<details markdown="1"><summary>Verificação</summary>

O `ef_search` controla quantos candidatos a busca no grafo acompanha a cada passo ao descer pelas camadas do HNSW. Um valor baixo explora menos candidatos, encontrando uma resposta rápido mas correndo o risco de se contentar com um nó que não é o verdadeiro mais próximo. Um valor alto explora mais candidatos, trocando velocidade de busca por recall mais alto, o mesmo formato de recall contra latência que o `nprobe` dá ao IVF.

</details>

4. ▢ Qual é o trade-off geral entre escolher HNSW e escolher IVF para um dado corpus?

<details markdown="1"><summary>Verificação</summary>

O HNSW tipicamente atinge um ponto melhor de recall para uma dada latência do que o IVF, mas custa mais memória (as arestas do grafo adicionam sobrecarga real além de apenas armazenar os vetores) e leva mais tempo para construir o índice. O IVF é mais barato de construir e armazenar, mas geralmente precisa buscar em uma fração maior do corpus para igualar o recall do HNSW com a mesma latência.

</details>

5. ▢ Qual afirmação é verdadeira sobre ajustar o parâmetro de tempo de busca de um índice ANN (`nprobe` ou `ef_search`)?

    - a) Existe uma configuração universalmente correta que funciona para qualquer corpus e carga de trabalho
    - b) A configuração certa é um ponto em uma curva de recall/latência que precisa ser escolhido contra o orçamento real de latência da carga de trabalho e sua tolerância à perda de recall
    - c) Ajustar o parâmetro o mais alto possível é sempre a escolha certa, já que a latência não importa depois que um índice existe
    - d) O parâmetro afeta apenas o tempo de construção do índice, não o comportamento em tempo de consulta

<details markdown="1"><summary>Verificação</summary>

**b)** Os dois parâmetros trocam recall por latência em tempo de consulta, e o ponto certo depende do que a carga de trabalho de fato precisa, o que a etapa 6 mede em vez de presumir. (a) é falsa: é exatamente isso que a curva de recall/latência descarta. (c) é falsa: uma configuração mais alta custa mais latência em tempo de consulta, o que importa sempre que há um orçamento de latência a cumprir. (d) é falsa: tanto o `nprobe` quanto o `ef_search` são parâmetros de tempo de busca, não de tempo de construção.

</details>

## Prática no mundo real

- [ ] Descubra o tipo de índice (IVF ou HNSW) que o seu vector store usa ou adota por padrão e localize na documentação dele o parâmetro de recall/latência em tempo de busca.
- [ ] Se puder executar consultas contra um índice, experimente dois valores diferentes de `nprobe` ou `ef_search` e observe a diferença na latência da consulta.
- [ ] Amanhã: leia um parágrafo da descrição da estrutura em camadas no artigo do HNSW e anote, com suas próprias palavras, por que a camada do topo precisa ser esparsa para que os saltos de longo alcance funcionem.

## Para ir além

- [Artigo científico: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov e Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Repositório: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
