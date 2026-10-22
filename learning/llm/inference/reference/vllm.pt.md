---
title: "vLLM"
description: "Colocar o vLLM no ar, as flags que carregam os conceitos das etapas 1-3, a block table do PagedAttention e um procedimento de decisão do sintoma ao parâmetro"
type: reference
---

# vLLM

A stack de serving em GPU. Feito para consulta ao colocar no ar ou ajustar um servidor.

## Colocando um servidor no ar

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

Inicia um servidor HTTP compatível com a OpenAI na porta 8000. Uma requisição se parece com qualquer chamada de chat completion da OpenAI:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

O campo `"model"` da requisição precisa coincidir com o modelo com que o servidor foi iniciado.

## Flags que carregam a aritmética das etapas 1-3

| Flag | Carrega |
|---|---|
| `--max-num-seqs` | O teto de batch size [defendido contra um orçamento de latência](batching.md#defending-a-configuration) |
| `--kv-cache-dtype` | A [precisão do cache](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights), por exemplo `fp8`, independente da precisão dos pesos do próprio modelo |
| `--quantization` | O esquema (`gptq`, `awq`, ...) [escolhido e defendido](quantization-at-serve-time.md) para um checkpoint já quantizado |

O continuous batching e o chunked prefill estão ligados por padrão; não há flag para desligar o mecanismo básico, só para ajustar em torno dele (como o tamanho do chunk). Omitir `--quantization` serve o checkpoint na precisão em que ele foi salvo, mais comumente fp16 ou bf16; nada é quantizado no carregamento.

<a id="pagedattention"></a>

## PagedAttention

O cache de cada sequência é dividido em **blocos** de tamanho fixo (16 tokens por padrão); uma **block table** por sequência mapeia as posições lógicas de token para localizações físicas de bloco, a mesma ideia de uma page table de SO.

**O tamanho do bloco é um trade-off:**

| Tamanho do bloco | Espaço desperdiçado no último bloco, parcialmente preenchido | Contabilidade da block table |
|---|---|---|
| Maior | Mais | Menos |
| Menor | Menos | Mais |

**Exemplo resolvido**: uma sequência de 40 tokens com blocos de 16 tokens usa `ceil(40/16) = 3` blocos; o terceiro guarda 8 tokens e desperdiça os outros 8 espaços.

**Compartilhamento de blocos**: as block tables de duas sequências podem apontar para o mesmo bloco físico quando o conteúdo é idêntico, mais comumente um prefixo de prompt compartilhado. A amostragem paralela e o beam search são os casos mais claros: a tabela de cada amostra aponta para os mesmos blocos do prompt até que o token gerado por uma amostra divirja, e nesse ponto um **copy-on-write** dá só a essa amostra uma cópia privada do bloco que está sendo modificado.

**Exemplo resolvido**, 10 amostras paralelas do mesmo prompt de 200 tokens, blocos de 16 tokens: uma cópia precisa de `ceil(200/16) = 13` blocos. Sem compartilhamento: `13 × 10 = 130` blocos. Com compartilhamento: 13 blocos, até que alguma amostra comece a divergir.

## Mais dois parâmetros de ajuste

| Flag | O que controla | Trade-off |
|---|---|---|
| `--gpu-memory-utilization` | Fração da memória de uma GPU que o vLLM pode usar para pesos, cache e o seu próprio overhead (padrão ~0.9) | Subi-la em direção a 1.0 aumenta o teto de capacidade do cache, mas deixa menos folga para qualquer outra coisa que divida a GPU |
| `--tensor-parallel-size` | Divide os pesos e o compute de um modelo entre várias GPUs | Espalha o modelo em vez de encolhê-lo (sem custo de acurácia, ao contrário da quantização); combinável com a quantização quando nenhuma das duas sozinha basta |

`--gpu-memory-utilization` muda o que "memória total" significa na [fórmula do teto de capacidade](kv-cache.md#capacity-budget): em uma GPU de 80 GB com o padrão de ~0.9, só ~72 GB, e não 80 GB, é o que a fórmula deveria usar.

## Do sintoma ao parâmetro

| Sintoma | Verifique |
|---|---|
| Não inicia, ou relata pouca memória para o cache | `--gpu-memory-utilization` primeiro; se ainda não couber em 100%, esse é o [caso limitado por memória](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first): quantize, adicione `--tensor-parallel-size` ou os dois |
| Decode mais lento do que o orçamento de latência | `--max-num-seqs` contra o [batch size defendido](batching.md#the-throughputlatency-trade-off) e depois se quantizar os pesos ou `--kv-cache-dtype` se justifica pelos números medidos |
| Uma requisição trava os tokens de todas as outras sequências | [Head-of-line blocking](batching.md#admission-order-and-head-of-line-blocking): verifique o tamanho do chunk do chunked prefill, e não o batch size |
| A memória parece desperdiçada entre amostras paralelas do mesmo prompt | O compartilhamento de blocos acima: verifique se ele está de fato acontecendo antes de mexer no batch size ou na utilização de memória |

## Relacionado

- [Lição 10](../lessons/0010-standing-up-vllm.md), [Lição 11](../lessons/0011-pagedattention.md), [Lição 12](../lessons/0012-vllm-tuning-knobs.md)
- [KV cache](kv-cache.md), [Batching](batching.md), [Quantização no Serving](quantization-at-serve-time.md): os conceitos que essas flags carregam
