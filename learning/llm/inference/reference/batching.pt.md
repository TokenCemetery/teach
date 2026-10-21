---
title: "Batching"
description: "Batching estático versus contínuo, scheduling de requisições e o trade-off entre throughput e latência que uma configuração precisa defender"
type: reference
---

# Batching

Como um servidor transforma a capacidade de [KV cache](kv-cache.md) em throughput servido. Feito para consulta ao ajustar ou defender uma configuração de batching.

<a id="static-batching-wastes-capacity-on-uneven-finish-times"></a>

## O batching estático desperdiça capacidade com términos desiguais

O tráfego de memória de um passo de decode (ler os pesos e o cache de toda sequência residente) quase não muda se ele calcula o próximo token de uma sequência ou de várias ao mesmo tempo, então agrupar passos de decode é throughput quase de graça. O **batching estático** agrupa um conjunto fixo de requisições e roda passos de decode até a mais longa terminar; toda sequência que termina cedo continua ocupando um slot, sem fazer nada, até o grupo inteiro acabar.

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**Exemplo resolvido**, quatro requisições que precisam de 10, 20, 30 e 100 tokens de saída:

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

O desperdício cresce com a dispersão entre os comprimentos das requisições, que é o caso normal.

## O continuous batching remove a fronteira do batch

O **continuous batching** (scheduling em nível de iteração) faz o scheduling no nível de um único passo de decode em vez de um grupo fixo: no instante em que uma sequência termina, o seu slot é liberado e uma requisição em espera é admitida já no passo seguinte. O batch size, e não o tempo de vida de uma requisição qualquer, é o que permanece aproximadamente constante. O ganho não é uma computação por passo mais rápida; é menos slot-steps gastos em sequências que não tinham mais nada a fazer.

<a id="admission-order-and-head-of-line-blocking"></a>

## Ordem de admissão e head-of-line blocking

A política de admissão padrão é o **first-come, first-served (FCFS)**: simples, e justa no sentido de que nenhuma requisição espera atrás de uma que chegou depois. Mas toda sequência que compartilha um passo de batch avança junto, então admitir o trabalho de prefill de uma nova requisição no passo seguinte é bom quando o prompt é curto e prejudicial quando é longo: um prefill grande incorporado a um passo domina a latência desse passo, e todas as outras sequências, mesmo as que só precisavam de um passo de decode rápido, esperam por ele. Isso é o **head-of-line blocking**: a fila está bem, mas o que está rodando agora não está. O FCFS sozinho não causa nem corrige isso; ele só decide quem é admitido, e não quanto do prefill delas cai em um único passo.

O **chunked prefill** divide o prefill de um prompt grande em pedaços intercalados com os passos de decode em andamento do batch, de modo que cada passo admita apenas uma quantidade limitada de novo trabalho de prefill. O prefill da própria nova requisição leva mais passos para terminar; nenhuma outra sequência do batch trava esperando por ele. O tamanho final do cache de um prompt totalmente processado não muda, só como o trabalho para chegar lá se espalha no tempo.

<a id="the-throughputlatency-trade-off"></a>

## O trade-off entre throughput e latência

Acrescentar mais uma sequência a um batch aumenta o throughput (mais tokens produzidos por segundo, agregados no batch) e aumenta a latência por token (toda sequência de um passo avança junto, então um passo maior demora mais). Os dois se movem juntos, e não contra um ao outro de forma independente.

| Regime | Gargalo | Efeito de acrescentar mais uma sequência |
|---|---|---|
| Batch pequeno | Limitado pela largura de banda de memória, como no decode simples | O throughput sobe de forma aproximadamente linear; a latência mal se move |
| Batch grande | Limitado por compute | A latência sobe visivelmente; cada sequência acrescentada compra menos throughput que a anterior |

**Exemplo resolvido**, uma stack medida em quatro batch sizes:

| Batch size | Latência por token |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

<a id="defending-a-configuration"></a>

## Defendendo uma configuração

O batch size defendido é o maior que satisfaz as duas restrições independentes, a que limitar mais:

- **Um orçamento de latência**: um teto declarado para a latência entre tokens.
- **O teto de capacidade**: [o máximo derivado de memória do KV cache](kv-cache.md#capacity-budget), que não diz nada sobre latência.

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**Exemplo resolvido**, orçamento de 30 ms/token, usando a tabela acima:

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

Um batch size escolhido bem abaixo das duas restrições (digamos, 8 quando 32 ainda cumpriria o orçamento) não está errado, mas deixa na mesa um throughput que o orçamento poderia ter pagado.

## Relacionado

- [Lição 4](../lessons/0004-static-vs-continuous-batching.md), [Lição 5](../lessons/0005-request-scheduling.md), [Lição 6](../lessons/0006-throughput-latency-tradeoff.md)
- [KV cache](kv-cache.md): o teto de capacidade de que a fórmula de configuração defendida desta folha depende
