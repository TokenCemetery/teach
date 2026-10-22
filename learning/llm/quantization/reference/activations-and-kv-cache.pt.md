---
title: "Ativações e o KV Cache"
description: "Somente pesos contra pesos e ativações, SmoothQuant, rotações e quantização do KV cache, para consulta"
type: reference
---

# Ativações e o KV Cache: Quantizando Além dos Pesos

A etapa 5 comprimida para consulta. A [lição 13](../lessons/0013-weights-activations-or-both.md) cobre somente pesos contra pesos e ativações, a [lição 14](../lessons/0014-smoothquant.md) o SmoothQuant, a [lição 15](../lessons/0015-rotations.md) as rotações e a [lição 16](../lessons/0016-kv-cache-quantization.md) a quantização do KV cache.

## Pesos, ativações ou ambos

| Esquema | Armazenado pequeno | O matmul roda em | Oferece | Serve para |
|---|---|---|---|---|
| W4A16, W8A16 (somente pesos) | Pesos | 16 bits, após dequantizar no kernel | Memória, bytes lidos por token | Limitado pela largura de banda de memória: decode com batch pequeno |
| W8A8 int8 ou fp8 | Pesos e ativações | 8 bits | Vazão aritmética, mais memória | Limitado por compute: prefill, batches grandes |
| W4A4 com rotações | Pesos, ativações, muitas vezes o KV | 4 bits | Memória e aritmética | Só onde existe um kernel de 4 bits, veja a lição 20 |

Kurtic et al. (família Llama 3.1, mais de 500.000 avaliações): fp8 W8A8 efetivamente sem perdas, int8 W8A8 bem ajustado com 1 a 3% de degradação, W4A16 int rivaliza com o de 8 bits. Conselho: W4A16 para serving síncrono, W8A8 para continuous batching.

## Por que as ativações são mais difíceis

| Propriedade | Pesos | Ativações |
|---|---|---|
| Faixa conhecida | Após o treinamento, fixa | Só em tempo de execução |
| Outliers | Planos, fáceis de quantizar | Cerca de 100 vezes a maioria dos valores, em canais fixos em todos os tokens (SmoothQuant) |
| Granularidade de scale que um GEMM em int8 permite | Por canal de saída | Apenas por tensor ou por token |

O GEMM em int8: `Y = diag(s_X) · (X_int8 @ W_int8) · diag(s_W)`. As scales ficam apenas nas dimensões externas; uma scale por canal de entrada ficaria dentro da soma.

| Scale da ativação | Calculada | Custo | Risco |
|---|---|---|---|
| Estática | Offline, a partir de um calibration set | Nenhum por requisição | Calibration set diferente do tráfego real |
| Dinâmica | Em tempo de execução, a partir do tensor | Uma redução antes de cada matmul | Pouco; adapta-se a cada entrada |

## SmoothQuant

```text
X @ W = (X @ diag(s)^-1) @ (diag(s) @ W)
s_j   = max(|X_j|)^α / max(|W_j|)^(1 - α)
```

| `α` | Efeito |
|---|---|
| 0 | Ativações inalteradas |
| 0.5 | O padrão equilibrado do artigo, ponto ideal para OPT e BLOOM |
| Maior, em direção a 1 | Mais dificuldade para os pesos; para modelos com outliers mais pesados, como o GLM-130B |
| 1 | Todo canal de ativação tem o mesmo máximo; os pesos carregam todos os outliers |

- `max(|X_j|)` vem de um calibration set.
- O fator é fundido offline na camada que produz `X`: nenhum custo em tempo de execução.
- Um método de 8 bits: até 1.56x de aceleração e 2x de redução de memória no artigo.

## Rotações

```text
X @ W = (X @ Q) @ (Q.T @ W)      where Q @ Q.T = I
```

| Ponto | Detalhe |
|---|---|
| O que faz | Espalha um outlier por todos os canais; o máximo fica próximo do RMS |
| `Q` usual | Hadamard aleatorizada: entradas ±1/sqrt(n), custo `n log n` |
| Fundida offline | Rotação do residual stream, nos pesos |
| Online | Antes da projeção de descida da FFN; head a head em queries e keys, após o RoPE |
| QuaRot | Todos os pesos, ativações e o KV cache em 4 bits; Llama 2 70B a 0.47 de perplexity no WikiText-2, 99% do zero-shot |
| SpinQuant | Rotações aleatórias diferem em até 13 pontos de zero-shot; rotações aprendidas reduzem a diferença a 2.9 pontos no Llama 2 7B W4A4KV4 |

Pergunta de revisão para qualquer alegação de W4A4: qual rotação, e ela foi escolhida ou aprendida para este modelo?

## Quantização do KV cache

```text
KV bytes per token = 2 x layers x kv_heads x head_dim x bytes_per_value
```

Llama 3 8B (32 camadas, 8 KV heads, dimensão 128) em bf16: 128 KiB por token, 4 GiB por sequência de 32.768 tokens.

| Tensor | Quantizar ao longo de | Por quê |
|---|---|---|
| Keys | Por canal, antes do RoPE quando possível | Alguns canais outliers fixos (KIVI); o RoPE mistura pares de canais (KVQuant) |
| Values | Por token | Sem padrão por canal; quase 15 vezes menos erro na saída da atenção do que por canal (KIVI) |

| Método ou opção | Bits | Resultado reportado |
|---|---|---|
| KIVI | 2 | Qualidade quase igual, 2.6x menos memória de pico, até 4x de batch, 2.35 a 3.47x de throughput |
| KVQuant | 3 | Menos de 0.1 de degradação de perplexity; LLaMA-7B com 1M de contexto em uma única A100 de 80 GB |
| KV cache em fp8 do vLLM | 8 | Scales por tensor ou por head; scales padrão 1.0 sem calibração, calibração recomendada |

O KIVI mantém os tokens mais novos (128 nos seus experimentos) em precisão total até que um grupo per-channel de keys esteja completo.
