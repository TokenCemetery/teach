---
title: "Busca Híbrida"
description: "A pontuação por estatísticas de termos do BM25, por que ele ainda importa ao lado da busca vetorial e a reciprocal rank fusion como forma independente de escala de combiná-los"
type: reference
---

# Busca Híbrida

Combinando rankings lexicais e vetoriais. Feito para consulta ao montar ou ajustar uma mistura híbrida.

## O BM25 pontua a sobreposição de termos, não o significado

Uma função de ranking puramente lexical, sem embedding, sem noção de significado. Três ingredientes:

| Ingrediente | O que faz |
|---|---|
| Frequência inversa de documento (IDF) | Pondera um termo da consulta pela raridade no corpus; uma palavra comum como "the" contribui quase nada |
| Frequência de termo, com saturação | Mais ocorrências de um termo elevam a pontuação, mas com retornos decrescentes, de modo que a repetição sozinha (keyword stuffing) não consegue dominar |
| Normalização de tamanho | Desconta a vantagem bruta de frequência de termo que um documento ganha simplesmente por ser mais longo |

## O BM25 e a busca vetorial têm pontos cegos opostos

| Formato da consulta | BM25 | Busca vetorial |
|---|---|---|
| Identificador exato ("error code E502") | Encontra: a string literal aparece | Pode deixar passar: o modelo de embedding foi treinado para similaridade semântica, não para correspondência de identificador exato |
| Formulação sinônima, sem palavras em comum ("broken pipe" / "leaking conduit") | Pontua perto de zero: nenhuma sobreposição de termos | Encontra: as duas frases significam a mesma coisa |

Cada abordagem pega o que a outra deixa passar, e essa é toda a base para combiná-las.

## Reciprocal rank fusion (RRF): use a posição, não a pontuação

A pontuação do BM25 é ilimitada e depende do corpus; a similaridade de cosseno é limitada a [-1, 1]. Tirar a média das duas diretamente significa inventar uma normalização frágil e específica do corpus. A **RRF** contorna o problema de escala usando apenas a posição de ranking de cada documento dentro de cada ranking:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

O `k` amortece a influência das posições mais altas (um padrão comum é `k = 60`; um `k` menor faz as diferenças de posição perto do topo importarem mais, um `k` maior as amortece). A posição no ranking é uma moeda comum a qualquer método de ranking, então nenhuma normalização é necessária entre o BM25 e a busca vetorial.

**Exemplo resolvido**, `k = 1`, o BM25 ranqueia A em 1º / B em 4º / C em 2º, a busca vetorial ranqueia A em 4º / B em 1º / C em 2º:

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A e B empatam em primeiro, cada um se destacando em um método e indo mal no outro; C, apenas medíocre nos dois, perde para ambos. A RRF recompensa um documento em que qualquer um dos métodos acredita fortemente, e não apenas aquele em que os dois métodos concordam de leve.

## Ajustando a mistura

A RRF se estende com um peso por ranking, `sum of w_r / (k + rank_r(d))`, permitindo que a busca vetorial conte mais ou menos que o BM25. O peso e o `k` certos não são chutados: meça a qualidade da recuperação (recall@k, MRR) contra um conjunto de consultas rotulado ou sintético, representativo do tráfego real do corpus, em várias ponderações candidatas, e entregue a mistura que de fato recupera os documentos certos com mais frequência para este corpus, e não uma divisão padrão de 50/50.

## Relacionado

- [Lição 6](../lessons/0006-bm25-and-lexical-search.md), [Lição 7](../lessons/0007-reciprocal-rank-fusion.md)
- [Busca Vetorial e Indexação](vector-search-and-indexing.md): a metade vetorial do ranking da fusão
