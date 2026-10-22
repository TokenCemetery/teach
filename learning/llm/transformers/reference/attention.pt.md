---
title: "Atenção"
description: "Scaled dot-product attention, multi-head attention e máscara causal, com os formatos dos tensores anotados em cada etapa"
type: reference
---

# Atenção: Scaled Dot-Product, Multi-Head e Máscara Causal

A etapa 1 comprimida para consulta. A [lição 1](../lessons/0001-scaled-dot-product-attention.md) cobre a equação central; a [lição 2](../lessons/0002-multi-head-attention.md) cobre rodá-la em subespaços paralelos; a [lição 3](../lessons/0003-causal-masking.md) cobre restringi-la ao passado. Esta folha traz as equações e os formatos, lado a lado.

## Scaled dot-product attention

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| Passo | Formato de entrada | Formato de saída | Observação |
|---|---|---|---|
| `Q`, `K`, `V` dados | n/d | `[n, d_k]`, `[m, d_k]`, `[m, d_v]` | `n` queries, `m` pares key/value; `d_k` é a dimensão de key/query |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | um score de similaridade por par query-key |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | compensa o crescimento da variância com `d_k`, mantém o gradiente do softmax utilizável |
| `softmax(...)` (por linha) | `[n, m]` | `[n, m]` | cada linha agora é uma distribuição de probabilidade somando 1 |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | um vetor de saída por query, uma mistura ponderada dos values |

A self-attention é o caso em que `Q`, `K`, `V` vêm todos da mesma sequência (`n = m`), cada posição atendendo a todas as posições, incluindo ela mesma.

**Por que o escalonamento.** A variância do produto escalar cresce com `d_k`, empurrando o softmax para saídas quase one-hot, em que o seu gradiente é quase plano e o treinamento emperra. O `/ sqrt(d_k)` compensa esse crescimento, não importa quão grande seja `d_k`.

## Multi-head attention

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| Passo | Formato de entrada | Formato de saída | Observação |
|---|---|---|---|
| Entrada `X` | n/d | `[n, d_model]` | |
| Projeção por head (`W_Q^i`, `W_K^i`, `W_V^i`) | `[n, d_model] × [d_model, d_k]` | `[n, d_k]` por head, `d_k = d_model / h` | as projeções de cada head são aprendidas de forma independente |
| `head_i = Attention(Q_i, K_i, V_i)` | `[n, d_k]` cada | `[n, d_k]` | a equação exata acima, executada uma vez por head |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | coloca os heads lado a lado, ainda sem interação entre heads |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | o único passo que permite que a informação de heads diferentes se combine |

**A fórmula de escalonamento usa o `d_k` por head, e não o `d_model`.** Os produtos escalares de cada head são somados sobre a sua própria dimensão, menor, então essa é a variância que o escalonamento precisa compensar, não importa quão grande seja o modelo completo.

**A `W_O` não é opcional.** A concatenação sozinha coloca as saídas lado a lado, sem interação; a `W_O` é o único lugar em que a informação de heads diferentes pode se combinar em uma só representação.

## Máscara causal

Somada aos scores brutos, antes do softmax:

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| Escolha | Por quê |
|---|---|
| Mascarar antes do softmax, e não depois | Zerar um peso depois de o softmax já ter rodado deixa os pesos restantes somando menos que 1, sem formar uma distribuição válida. Mascarar o score permite que a renormalização aconteça automaticamente dentro do mesmo softmax |
| Número negativo grande, e não `0` | `exp(0) = 1`, um valor comum e não desprezível que ainda compete por massa de probabilidade. Só um número negativo suficientemente grande leva `exp(...)` a efetivamente zero |
| A mesma máscara para todo head e todo exemplo de um batch | A restrição (a posição de query `i` pode atender às posições de key `0..i`) é uma propriedade da tarefa, e não de um head em particular |

Na inferência, um modelo gera o token `N` a partir de apenas os tokens `1..N-1`; deixar a posição `i` atender a uma posição posterior `j` durante o treinamento permite que o modelo use uma resposta que ele nunca terá na hora da geração. A loss de treinamento parece boa nesse caso, mas o modelo não aprende nada transferível.

## Antes de confiar em uma implementação de atenção

- [ ] O divisor de escalonamento é o `d_k` por head (`d_model / h`), e não o `d_model` completo.
- [ ] A `W_O` é aplicada depois de concatenar os heads, e não omitida.
- [ ] A máscara causal é somada aos scores brutos antes do softmax, e não aplicada aos pesos depois.
- [ ] O valor da máscara é um número negativo grande (ou `-inf`), e não `0`.
- [ ] O formato da saída é `[n, d_model]` seja qual for a quantidade de heads, já que os heads só mudam a dimensão intermediária por head.

## Fontes

- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Artigo: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Artigo: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Recursos](../RESOURCES.md)
