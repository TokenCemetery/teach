---
title: "Métodos de PTQ de Pesos"
description: "Round-to-nearest, GPTQ e AWQ lado a lado, e o que o calibration set faz"
type: reference
---

# Métodos de PTQ de Pesos: Round-to-Nearest, GPTQ e AWQ Comparados

A etapa 4 comprimida para consulta. A [lição 9](../lessons/0009-round-to-nearest.md) cobre o round-to-nearest (RTN), a [lição 10](../lessons/0010-gptq.md) o GPTQ, a [lição 11](../lessons/0011-awq.md) o AWQ e a [lição 12](../lessons/0012-the-calibration-set.md) o calibration set.

## Os três métodos lado a lado

| | Round-to-nearest | GPTQ | AWQ |
|---|---|---|---|
| Ideia | Arredondar cada peso para o seu nível mais próximo | Arredondar as colunas em ordem, empurrando cada erro para as colunas ainda não arredondadas | Aumentar a scale dos canais de entrada salientes antes do arredondamento, dividindo a ativação pela mesma scale |
| Lê dos dados | Nada | Entradas da camada, somadas em `H = 2 X X^T` | Magnitude média da ativação por canal, mais as saídas da camada para pontuar cada `alpha` |
| Muda os valores dos pesos | Não | Sim, todas as colunas seguintes após cada arredondamento | Sim, pela scale por canal `s = s_X^alpha`, e então arredonda para o mais próximo |
| Objetivo | O erro de cada peso em si | `argmin \|\| W X - Ŵ X \|\|^2` por camada | O mesmo erro na saída da camada, buscado ao longo de `alpha` em [0, 1] |
| Backpropagation | Nenhuma | Nenhuma | Nenhuma |
| Custo | Desprezível | Cerca de 4 horas de GPU para 175B de parâmetros (artigo) | Uma grade de 20 valores de `alpha` por camada (artigo) |
| Grade | Uma scale por linha ou por grupo | Fixada antes do loop; scale por grupo definida quando o loop chega ao grupo | Per-group, 128 no artigo |
| Principal risco | Colapsa em 3 bits com scales por linha | Overfit em um calibration set pequeno ou incompatível | Escalar demais prejudica os canais não salientes |

## O que cada um faz com os números

| Perplexity no WikiText-2 | 16 bits | RTN | GPTQ | AWQ |
|---|---|---|---|---|
| OPT-175B, 4 bits, grade por linha | 8.34 | 10.54 | 8.37 | não reportado ali |
| OPT-175B, 3 bits, grade por linha | 8.34 | 7.300 | 8.68 | não reportado ali |
| Llama-2 7B, 4 bits, grupos de 128 | 5.47 | 5.73 | 5.69 | 5.60 |
| Llama-2 7B, 3 bits, grupos de 128 | 5.47 | 6.66 | 6.43 | 6.24 |

As duas primeiras linhas vêm do artigo do GPTQ e as duas últimas do artigo do AWQ. As grades e os modelos diferem, então compare dentro de uma linha e a forma entre as linhas, não os números entre elas. Cada artigo avalia o seu próprio método contra o outro, então leia as diferenças como execuções dos autores.

## Por que o erro se comporta assim

| Fato | Consequência |
|---|---|
| Cada bit removido aproximadamente dobra o passo | O erro do round-to-nearest aproximadamente dobra por bit |
| No exemplo simplificado da lição 9, as razões de erro igualam as razões de passo: 127 / 7 = 18.1 de 8 para 4 bits, 7 / 3 = 2.3 de 4 para 3 | Os últimos bits são os caros |
| O round-to-nearest minimiza o erro de cada peso, não o erro da saída da camada | 919 de 2000 arredondamentos aleatórios o superam em uma camada simplificada com entradas correlacionadas |
| O ganho do GPTQ vem de entradas correlacionadas | Com entradas independentes ele quase desaparece (0.2680 contra 0.2595 no exemplo simplificado) |
| Um peso saliente é escolhido pela sua ativação, não pelo seu tamanho | No OPT-6.7B em 3 bits, 1% escolhido pela ativação dá 11.39, pelo tamanho do peso 22.37, round-to-nearest simples 23.54 |
| Escalar um canal por `s` reduz o seu erro relativo em cerca de `1 / s` | Um `s` grande demais aumenta o passo dos outros canais do grupo |

## As três mudanças de escala do GPTQ e o act-order

| Mudança | O que corrige |
|---|---|
| Mesma ordem de colunas para toda linha | Uma atualização da inversa por coluna serve a todas as linhas |
| Atualizações lazy em batch, 128 colunas por vez | A atualização é limitada pela largura de banda de memória, então fazê-la em batch aproveita a GPU |
| Dampening de 1% da diagonal média, mais um fator de Cholesky | Erro numérico que pode tornar a inversa indefinida |
| Act-order (código dos autores, não o artigo): colunas ordenadas pela diagonal de `H`, a maior primeiro | Corrige resultados ruins como o OPT-66B em 3 bits (14.16 para 9.95); pode exigir mudanças na inferência, a menos que se usem static groups |

## O que o calibration set faz

| | GPTQ | AWQ |
|---|---|---|
| Tamanho típico | Artigo: 128 segmentos de 2048 tokens, do C4 | O AWQ com 16 sequências supera o GPTQ com 192 no OPT-6.7B, 3 bits (execução dos autores) |
| llm-compressor | 128 a 512 amostras é o típico, comece com 128 a 256 | Mesmo conselho; o seu exemplo usa 256 |
| Precisa de mais dados porque | Estima uma matriz inteira de co-variação das features | Estima uma média por canal |
| Penalidade por incompatibilidade, OPT-6.7B, 3 bits (artigo do AWQ) | 2.3 a 4.9 de perplexity pior | 0.5 a 0.6 pior |

- O round-to-nearest não usa dados. O GPTQ e o AWQ precisam de um calibration set. Nenhum dos dois faz backpropagation por ele.
- Um calibration set não são dados de treinamento, e o seu domínio aparece no resultado.
- Case o conjunto com o uso-alvo: texto geral para um modelo geral, dados de instrução para um modelo de instrução, código para um modelo de código (llm-compressor).
- Avalie em texto held-out do domínio de calibração e em texto dos outros domínios que você atende. Um ganho em um e uma perda no outro é uma incompatibilidade.
- Uma perplexity medida no texto de que o conjunto foi extraído sai favorecida. O artigo do GPTQ diz que os seus resultados no C4 não são totalmente zero-shot por esse motivo.
- No exemplo simplificado da lição 12, amostras de menos (64 para 128 features) deixaram o GPTQ pior que o round-to-nearest mesmo dentro do domínio.

## Antes de confiar em um checkpoint de PTQ de pesos

- Qual método, qual largura em bits e qual tamanho de grupo ou grade.
- Qual calibration set, quantas amostras e de que comprimento. Se o model card não diz, isso é uma lacuna.
- Se a perplexity citada é no domínio de calibração.
- Se um baseline sem dados na mesma grade foi medido na mesma avaliação.
- No GPTQ com act-order e grupos, se ele exige mudanças na inferência que podem custar velocidade ou se foi feito com static groups.
