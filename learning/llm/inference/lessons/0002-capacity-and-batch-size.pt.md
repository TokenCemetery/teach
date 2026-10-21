---
title: "2. Capacidade e batch size"
description: "Como o compartilhamento de heads (GQA/MQA) e o batch size mudam a pegada real do cache"
type: lesson
---

# Lição 2. Capacidade e batch size

**Ligação com a missão:** Um orçamento de latência é defendido em termos de quantas requisições concorrentes um servidor consegue manter, e esse número sai direto da matemática de cache que esta lição estende.
**Fonte principal:** [Artigo: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
**Pré-requisitos:** [Lição 1](0001-the-kv-cache.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Em uma frase, o que o KV cache permite a um servidor pular a cada token gerado depois do primeiro?

<details markdown="1"><summary>Verificação</summary>

Recalcular os vetores de key e value de todos os tokens anteriores da sequência, em cada camada.

</details>

2. ▢ O que havia de errado com uma alocação de cache ingênua, contígua e dimensionada para o comprimento máximo, e o que o PagedAttention mudou nela?

<details markdown="1"><summary>Verificação</summary>

Ela reservava memória para o comprimento máximo que uma sequência poderia alcançar, desperdiçando-a como fragmentação interna e externa. O PagedAttention, em vez disso, aloca o cache em blocos de tamanho fixo e não contíguos, endereçados por uma tabela por sequência.

</details>

## Saiba isto

### A maioria dos modelos não guarda uma key e um value por head

A fórmula da lição 1, `2 × num_layers × d_model × 2 bytes` por token, pressupõe que cada attention head mantém os seus próprios vetores de key e value. Isso é a **multi-head attention (MHA)**. A maioria dos modelos servidos hoje usa **grouped-query attention (GQA)** ou o seu caso extremo, a **multi-query attention (MQA)**: muitas query heads compartilham um número muito menor de key/value heads. O cache só guarda um par K/V por *KV head*, e não por query head, então a fórmula passa a ser:

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

onde `head_dim = d_model / num_heads`, e `num_kv_heads` é o número que importa agora, e não a contagem total de heads. Quando `num_kv_heads = num_heads`, isso se reduz exatamente à fórmula da lição 1 (a MHA é o caso especial da GQA). Quando `num_kv_heads` é bem menor, o cache encolhe nessa mesma proporção, de graça, sem nenhuma mudança no comprimento de contexto nem no batch size.

![Três linhas: a MHA tem 8 query heads, cada uma pareada com a sua própria KV head; a GQA tem grupos de query heads compartilhando uma de 2 KV heads (um quarto do cache); a MQA tem todas as 8 query heads compartilhando uma única KV head (um oitavo do cache). A contagem de query heads nunca aparece na fórmula do cache; só a contagem de KV heads aparece.](images/mha-gqa-mqa-head-sharing.svg)

O Llama-2-70B é um caso concreto: 80 camadas, 64 query heads, mas apenas 8 KV heads, `head_dim` = 128. Em fp16:

```text
per token = 2 × 80 × 8 × 128 × 2 bytes = 327,680 bytes ≈ 320 KB
```

Se ele usasse MHA completa (64 KV heads em vez de 8), as mesmas camadas e o mesmo `head_dim` dão `2 × 80 × 64 × 128 × 2 = 2,621,440 bytes ≈ 2,5 MB` por token, oito vezes mais, exatamente a razão entre `num_heads` e `num_kv_heads`. A GQA é tanto uma decisão de custo de serving quanto uma decisão de modelagem.

### Do custo por token à pegada total de um batch

Um servidor raramente guarda uma única sequência. A pegada total do cache em qualquer momento é o custo por token, multiplicado por quanto cada sequência cresceu, multiplicado por quantas sequências estão residentes juntas:

```text
total cache bytes = bytes per token × context length × batch size
```

Para o Llama-2-70B com contexto de 4096 tokens, uma sequência custa `320 KB × 4096 ≈ 1,25 GB`. Trinta e duas sequências concorrentes nesse mesmo comprimento custam `1,25 GB × 32 = 40 GB`, antes de os pesos do próprio modelo ocuparem qualquer espaço.

### Transformando isso em um orçamento de capacidade

Este é o número de que uma decisão de serving realmente precisa: dado um pool de memória, quantas sequências concorrentes cabem? Subtraia os pesos e o overhead do framework da memória total disponível e depois divida o que sobrou pelo custo de cache por sequência no comprimento de contexto que você pretende suportar:

```text
max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)
```

Tome um pool de 320 GB (quatro GPUs de 80 GB, com paralelismo de tensor) servindo o Llama-2-70B, com pesos e overhead do framework medidos em 160 GB. Sobram 160 GB para o cache. Com os 4096 tokens e 1,25 GB por sequência acima: `160 GB / 1,25 GB ≈ 128` sequências concorrentes. Esse teto, e não o throughput bruto do modelo, é normalmente aquilo contra o qual um scheduler de batching negocia, e é aí que a lição 4 continua.

## Prática

1. ▢ Um modelo usa GQA com `num_kv_heads` igual a um quarto de `num_heads`. Em comparação com o mesmo modelo sob MHA completa, quanto menor é o seu KV cache por token?

<details markdown="1"><summary>Verificação</summary>

Um quarto do tamanho. O cache guarda um par K/V por KV head, e não por query head, então o custo por token escala só com `num_kv_heads`; todo o resto da fórmula permanece igual.

</details>

2. ▢ Um modelo tem 48 camadas, 40 query heads, 8 KV heads, `head_dim` = 128, servido em fp16. Calcule o seu tamanho de KV cache por token.

<details markdown="1"><summary>Dica</summary>

Use `2 × num_layers × num_kv_heads × head_dim × bytes_per_value`. A contagem de query heads não aparece na fórmula.

</details>

<details markdown="1"><summary>Verificação</summary>

`2 × 48 × 8 × 128 × 2 = 196,608 bytes ≈ 192 KB` por token.

</details>

3. ▢ Usando o modelo de 192 KB por token da questão 2, calcule a pegada total do cache para um batch de 16 sequências com contexto de 2048 tokens.

<details markdown="1"><summary>Dica</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

<details markdown="1"><summary>Verificação</summary>

Por sequência: `192 KB × 2048 ≈ 384 MB`. Para 16 sequências: `384 MB × 16 = 6,144 MB ≈ 6 GB`.

</details>

4. ▢ Um servidor tem 96 GB de memória. Pesos e overhead do framework ocupam 40 GB. O cache de cada sequência custa 384 MB no comprimento de contexto que esse servidor suporta. Qual é o número máximo de sequências concorrentes que o orçamento de cache permite?

<details markdown="1"><summary>Verificação</summary>

`(96 GB − 40 GB) / 384 MB = 56 GB / 384 MB ≈ 149` sequências. Na prática, um servidor reserva ainda uma margem de segurança abaixo desse teto, mas a aritmética é essa divisão.

</details>

## Prática no mundo real

- [ ] Procure o campo `num_key_value_heads` (ou equivalente) no arquivo de configuração de um modelo que você pretende servir, ao lado de `num_attention_heads`. Calcule a razão entre eles e o que ela devolve em tamanho de cache.
- [ ] Usando o tamanho de cache por token desse modelo, calcule quantas sequências concorrentes um pool de memória a que você tem acesso (ou a memória de uma GPU publicada) comportaria em um comprimento de contexto que lhe interessa.
- [ ] Amanhã: encontre a flag que a sua stack de serving de escolha (vLLM ou llama.cpp) usa para limitar a memória total de KV cache, e leia o que acontece quando uma requisição ultrapassaria esse limite.

## Para ir além

- [Artigo: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Artigo científico: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
