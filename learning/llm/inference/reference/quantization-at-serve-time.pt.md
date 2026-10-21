---
title: "Quantização no Serving"
description: "Quantização de pesos int8/int4/GPTQ/AWQ, por que memória, velocidade e acurácia não se movem juntas e um framework de decisão para escolher um esquema"
type: reference
---

# Quantização no Serving

A quantização de pesos como alavanca de serving, independente da precisão do [KV cache](kv-cache.md). Feito para consulta ao escolher ou defender um esquema.

## Esquemas

| Esquema | Largura de bits | Mecanismo | Acurácia nessa largura |
|---|---|---|---|
| int8 | 8 | Arredondamento para o mais próximo | Em geral boa, mesmo de forma ingênua |
| int4, ingênuo | 4 | Arredondamento para o mais próximo | Degrada de forma acentuada: só 16 valores representáveis por peso, contra 256 do int8 |
| GPTQ | 3-4 | Quantiza uma coluna por vez; depois de cada coluna, ajusta os pesos restantes, ainda não quantizados, daquela camada para compensar, usando informação de sensibilidade de segunda ordem | Corrige o erro depois do fato, coluna por coluna |
| AWQ | 3-4 | Uma passada de calibração encontra os canais de pesos que veem as maiores magnitudes de ativação; escala esses canais para protegê-los antes de quantizar qualquer coisa | Protege antes do fato os pesos provavelmente sensíveis |

GPTQ e AWQ miram o mesmo resultado, um modelo acurado com pesos de 4 bits, com momentos opostos: o GPTQ compensa o erro já introduzido; o AWQ o previne nos canais que a calibração sinaliza como sensíveis.

## A memória é o eixo previsível; velocidade e acurácia não são

```text
memory ≈ fp16 footprint / (16 / bit_width)      # int8 halves it, int4 quarters it
```

**Exemplo resolvido**, um modelo de 14 GB em fp16: o int8 fica em cerca de 7 GB, o int4 em cerca de 3.5 GB. Essa razão vale independentemente de qual esquema (ingênuo, GPTQ, AWQ) produziu os pesos quantizados, e independentemente da largura de bits além disso.

A velocidade **não** segue a razão de memória:

- Um peso quantizado muitas vezes precisa ser **dequantizado** de volta para uma precisão maior imediatamente antes de a multiplicação de matrizes rodar, já que o hardware de multiplicação espera essa precisão. Se esse passo de dequantização custa tempo, o ganho de velocidade em tempo real fica aquém da razão de memória, a menos que o kernel da stack de serving opere diretamente sobre o formato quantizado.
- O decode (limitado pela largura de banda de memória) é onde uma pegada de pesos menor compensa: menos a ler, menos tempo lendo. O prefill (limitado por compute) gasta o seu tempo no próprio matmul, e não em ler pesos repetidamente, então a mesma quantização rende ao prefill muito menos ganho, às vezes quase nenhum.

A acurácia precisa de um número medido, e não de uma impressão a partir de saídas de exemplo: a **perplexidade** (quão bem o modelo prevê texto held-out; maior é pior) contra o modelo não quantizado, ou a variação da pontuação em um benchmark específico da tarefa. Saída fluente não é evidência de que a acurácia se manteve.

| Passo | Memória | Velocidade | Acurácia |
|---|---|---|---|
| fp16 para int8 | Cai pela metade | Acompanha razoavelmente bem a memória | Custo pequeno, em geral tolerável |
| int8 para int4 | Cai pela metade de novo | Depende do overhead de dequantização e do suporte do kernel | Cresce desproporcionalmente mais do que no passo para int8, e é por isso que GPTQ/AWQ existem |

Nenhum dos três eixos se move em sincronia com os outros, e é por isso que uma escolha defensável precisa de um número para cada um.

<a id="picking-a-scheme-name-the-binding-constraint-first"></a>

## Escolhendo um esquema: nomeie primeiro a restrição limitante

A quantização é uma correção para uma restrição que o fp16 não cumpre, e não um passo padrão. Se o fp16 já cabe no orçamento de memória e cumpre o orçamento de latência, quantizar não compra nada necessário a um custo real de acurácia.

| Restrição limitante | O que fazer |
|---|---|
| Memória: os pesos mais a [capacidade de KV cache](kv-cache.md#capacity-budget) exigida não cabem | Quantize o suficiente para caber: int8 primeiro (menor custo de acurácia), int4 com GPTQ ou AWQ só se o int8 sozinho ainda não deixar espaço |
| Latência: o modelo cabe, mas o decode estoura o orçamento | int8 ou int4 podem ajudar, já que o decode é limitado pela largura de banda de memória, mas meça o ganho de velocidade real em vez de presumi-lo a partir da largura de bits |
| Acurácia: um teto de benchmark ou de perplexidade não pode ser cruzado | Não descarta a quantização, mas descarta escolher um esquema só por memória ou velocidade: meça GPTQ vs AWQ para este modelo específico, já que eles se saem de forma diferente de modelo para modelo |

**Exemplo resolvido**: os pesos em fp16 de um modelo ocupam 70 GB em uma GPU de 80 GB, deixando 10 GB para cache e overhead, pouco demais para uma concorrência significativa. Isso é uma restrição de memória. Quantizar para int8 reduz os pesos a ~35 GB, liberando ~45 GB para cache, o que eleva substancialmente o [teto de capacidade](kv-cache.md#capacity-budget). Se o int8 sozinho já satisfaz as metas de capacidade e de latência, descer ainda mais para o int4 compra memória de que ninguém precisa a um custo real e medido de acurácia: quantizar além da restrição limitante é o mesmo erro de quantizar quando o fp16 já cabia.

<a id="defending-the-choice-means-citing-three-numbers"></a>

## Defender a escolha significa citar três números

1. **O número de memória** que tornou a quantização necessária, ou o que mostra que não era.
2. **O número de acurácia** medido para o esquema escolhido na largura de bits escolhida: uma variação de perplexidade ou uma mudança de pontuação em benchmark em relação ao modelo não quantizado.
3. **O número de velocidade** realmente medido para a fase que o orçamento cobre (o decode, na maioria dos casos limitados por latência), já que o ganho em tempo real não segue a razão de memória automaticamente.

Uma escolha defendida por apenas um desses ("int4 com AWQ dá a melhor economia de memória") não está defendida: ela deixa sem exame os outros dois eixos, e se essa largura de bits sequer era necessária.

## Relacionado

- [Lição 7](../lessons/0007-quantization-schemes.md), [Lição 8](../lessons/0008-accuracy-speed-memory-tradeoffs.md), [Lição 9](../lessons/0009-picking-a-quantization-scheme.md)
- [KV cache](kv-cache.md): o teto de capacidade contra o qual uma decisão de quantização limitada por memória é medida
