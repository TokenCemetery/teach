---
title: "Orçamento de memória"
description: "A contabilidade de bytes e o que tentar quando uma execução não cabe"
type: reference
---

# Orçamento de memória

Contabilidade de bytes para fine-tuning com adapters. Feito para consulta durante uma execução.

## Bytes por parâmetro

| Formato | Bytes | Bits |
|---|---|---|
| fp32 | 4 | 32 |
| bf16 / fp16 | 2 | 16 |
| int8 | 1 | 8 |
| 4 bits, bruto | 0.5 | 4 |
| 4 bits + escalas fp32, bloco de 64 | 0.5625 | 4.5 |
| 4 bits + dupla quantização | ~0.516 | ~4.13 |

**Reflexo:** gigabytes em bf16 ≈ 2 × parâmetros em bilhões.

## Custo de treinamento por parâmetro

| Categoria | fp32 | Precisão mista |
|---|---|---|
| Pesos | 4 | 2 bf16 + 4 fp32 master |
| Gradientes | 4 | 2 |
| Momento 1 do AdamW | 4 | 4 |
| Momento 2 do AdamW | 4 | 4 |
| **Total treinável** | **16** | **16** |
| **Total congelado** | **4** | **2** |

A precisão mista não reduz o total. Ela compra throughput aritmético.

| Variante do otimizador | Bytes/parâmetro |
|---|---|
| AdamW, momentos em fp32 | 16 |
| AdamW, momentos em 8 bits | 10 |
| SGD com momentum | 12 |

## Contagem de parâmetros

```text
attention/layer = 2·d² + 2·d·d_kv          # q,o full; k,v narrowed by GQA
mlp/layer       = 3·d·d_ff                  # gate, up, down
model           ≈ n_layers·(attn + mlp) + vocab·d·(1 if tied else 2)
```

O MLP costuma ser de 75 a 80% de um bloco.

## Contagem de parâmetros de um adapter

```text
adapter = Σ over targeted layers:  r · (d_in + d_out)
```

Dominada pela dimensão **maior**, então o estreitamento do GQA quase não encolhe um adapter.

| Base | Targets | Rank | Adapter | % do base |
|---|---|---|---|---|
| ~1.1B, d=2048 | atenção | 8 | 2.5M | 0.22% |
| ~7B, d=4096 | q,v | 16 | 6.8M | 0.10% |
| ~7B, d=4096 | all-linear | 64 | ~160M | ~2.3% |

## Ativações

```text
activations ≈ n_layers · batch · seq_len · d · ~20 bytes
```

A constante é um ponto de partida para medir contra, não uma lei. Linear no batch e no comprimento da sequência; o termo quadrático dos scores de atenção é removido por um kernel de atenção eficiente em memória.

| Configuração | Estimativa |
|---|---|
| 24 camadas, d=2048, batch 4, seq 2048 | ~8 GB |
| 32 camadas, d=4096, batch 2, seq 4096 | ~21 GB |

O gradient checkpointing reduz isso em aproximadamente uma ordem de grandeza, por ~20 a 40% a mais de tempo por passo.

**Em uma execução com adapter, as ativações costumam dominar.** Isso inverte o perfil do full fine-tuning.

![Duas barras empilhadas na mesma escala, em gigabytes. Um fine-tune completo de 7B com AdamW tem 112 GB fixos mais 21 GB de ativações, então as ativações são 16% do total. Uma execução de QLoRA sobre um base de 7B em NF4 com um adapter de 20M tem 3.9 GB fixos mais os mesmos 21 GB, então as ativações são 84% do total.](images/activations-dominate.svg)

As duas barras tiram a memória fixa da tabela abaixo e as ativações da linha de 32 camadas, d=4096, batch 2, seq 4096 acima, sem gradient checkpointing. O bloco de ativações tem o mesmo tamanho nas duas, porque depende do formato do forward pass e não de quantos parâmetros são treináveis. Só a memória ao redor dele desaba, e é por isso que o que se deve cortar raramente é o adapter.

## Totais calculados, sem contar as ativações

| Configuração | Memória fixa |
|---|---|
| Full FT, 1.5B, AdamW | 24 GB |
| Full FT, 7B, AdamW | 112 GB |
| Full FT, 70B, AdamW | 1120 GB |
| base de 7B em bf16 + adapter de 20M | 14.3 GB |
| base de 7B em NF4 + adapter de 20M | ~3.9 GB |
| base de 13B em NF4 + adapter de 30M | ~7.2 GB |

## Quando uma execução não cabe

Na ordem do que você abre mão:

1. **Gradient checkpointing**, custa só tempo
2. **Batch size menor, mais gradient accumulation**, estatisticamente equivalente
3. **Comprimento de sequência menor**, mas confira antes a distribuição de comprimento em tokens; isso muda a tarefa
4. **Quantizar o base**, custa alguma qualidade
5. **Rank menor**, economiza o menos e custa capacidade

O rank é o instinto e quase a pior opção. Reduzir o rank pela metade em um adapter de 4M economiza ~32 MB.

## Batch size efetivo

```text
effective = per_device_batch × grad_accumulation × num_devices
```

Sempre reporte o número efetivo.

## Relacionado

- [Lição 5](../lessons/0005-counting-parameters-and-bytes.md), [Lição 6](../lessons/0006-gradients-and-optimizer-state.md), [Lição 7](../lessons/0007-activations-and-checkpointing.md), [Lição 15](../lessons/0015-nf4-and-double-quantisation.md)
