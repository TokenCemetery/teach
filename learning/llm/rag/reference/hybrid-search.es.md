---
title: "Búsqueda híbrida"
description: "La puntuación por estadística de términos de BM25, por qué sigue importando junto a la búsqueda vectorial y reciprocal rank fusion como forma independiente de la escala de combinarlas"
type: reference
---

# Búsqueda híbrida

Combinar rankings léxicos y vectoriales. Pensado para consultar al montar o ajustar una mezcla híbrida.

## BM25 puntúa la coincidencia de términos, no el significado

Una función de ranking puramente léxica, sin embedding y sin noción de significado. Tres ingredientes:

| Ingrediente | Qué hace |
|---|---|
| Frecuencia inversa de documentos (IDF) | Pondera un término de la consulta según su rareza en el corpus; una palabra común como "the" aporta casi nada |
| Frecuencia de términos, con saturación | Más apariciones de un término elevan la puntuación, pero con rendimientos decrecientes, de modo que la sola repetición (relleno de palabras clave) no puede dominar |
| Normalización por longitud | Descuenta la ventaja bruta de frecuencia de términos que obtiene un documento por el simple hecho de ser más largo |

## BM25 y la búsqueda vectorial tienen puntos ciegos opuestos

| Forma de la consulta | BM25 | Búsqueda vectorial |
|---|---|---|
| Identificador exacto ("error code E502") | Coincide: la cadena literal aparece | Puede fallar: el modelo de embeddings se entrenó para la similitud semántica, no para la coincidencia exacta de identificadores |
| Formulación sinónima, sin palabras en común ("broken pipe" / "leaking conduit") | Puntúa casi cero: no hay ninguna coincidencia de términos | Coincide: las dos frases significan lo mismo |

Cada enfoque detecta lo que el otro pasa por alto, que es la base completa para combinarlos.

## Reciprocal rank fusion (RRF): usar la posición, no la puntuación

La puntuación de BM25 no tiene cota y depende del corpus; la similitud coseno está acotada a [-1, 1]. Promediar las dos directamente implica inventar una normalización frágil y específica del corpus. **RRF** esquiva el problema de la escala usando solo la posición de cada documento dentro de cada ranking:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` amortigua la influencia de las primeras posiciones (un valor por defecto común es `k = 60`; un `k` menor hace que las diferencias de posición cerca de la cabeza importen más, un `k` mayor las amortigua). La posición en el ranking es una moneda común para cualquier método de ranking, así que no hace falta normalización entre BM25 y la búsqueda vectorial.

**Ejemplo resuelto**, `k = 1`, BM25 coloca a A 1.º / B 4.º / C 2.º, la búsqueda vectorial coloca a A 4.º / B 1.º / C 2.º:

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A y B empatan en el primer lugar, y cada uno sobresale con un método y rinde mal con el otro; C, apenas mediocre con ambos, pierde frente a los dos. RRF premia a un documento en el que cualquiera de los métodos confía con fuerza, no solo a uno en el que ambos coinciden de forma moderada.

## Ajustar la mezcla

RRF se amplía con un peso por ranking, `sum of w_r / (k + rank_r(d))`, que permite que la búsqueda vectorial cuente más o menos que BM25. El peso correcto y el `k` correcto no se adivinan: mide la calidad de la recuperación (recall@k, MRR) frente a un conjunto de consultas etiquetado o sintético representativo del tráfico real del corpus, con varias ponderaciones candidatas, y lleva a producción la mezcla que realmente recupera los documentos correctos con más frecuencia para este corpus, no una división 50/50 por defecto.

## Relacionado

- [Lección 6](../lessons/0006-bm25-and-lexical-search.md), [Lección 7](../lessons/0007-reciprocal-rank-fusion.md)
- [Búsqueda vectorial e indexación](vector-search-and-indexing.md): la mitad vectorial del ranking que se fusiona
