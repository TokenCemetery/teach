---
title: "3. Crescimento, prefill, decode e precisão"
description: "Como o cache cresce ao longo do prefill e do decode, e o que reduzir a sua precisão devolve"
type: lesson
---

# Lição 3. Crescimento, prefill, decode e precisão

**Ligação com a missão:** Um orçamento de latência depende de quando a memória do cache é reivindicada durante uma requisição, e não apenas do seu tamanho final, e das outras alavancas que um servidor tem sobre esse tamanho além do batch size e do comprimento de contexto.
**Fonte principal:** [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Pré-requisitos:** [Lição 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Escreva a fórmula da pegada total de KV cache de um batch, em termos de bytes por token, comprimento de contexto e batch size.

<details markdown="1"><summary>Verificação</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

2. ▢ Por que um modelo que usa grouped-query attention tem um KV cache menor do que o mesmo modelo sob multi-head attention completa?

<details markdown="1"><summary>Verificação</summary>

O cache guarda um par key/value por KV head, e não por query head, e a GQA usa menos KV heads do que query heads. O cache escala com `num_kv_heads`, que a MHA completa define igual a `num_heads`.

</details>

## Saiba isto

### O cache não cresce a um ritmo constante

Uma requisição tem duas fases, e elas reivindicam a memória do cache de maneiras muito diferentes.

O **prefill** processa o prompt inteiro em uma única passada forward: os vetores de key e value de todos os tokens do prompt são calculados e colocados em cache juntos, em um só passo. O cache salta de vazio para `bytes per token × prompt length` antes de o modelo gerar um único token de saída. Esta fase é limitada por compute: é uma grande multiplicação de matrizes paralela sobre o prompt todo.

O **decode** então gera um token de saída por vez. Cada passo calcula e coloca em cache exatamente mais um token de keys e values, então o cache cresce `bytes per token` por passo, um fio de água em comparação. Esta fase é limitada pela largura de banda de memória: cada passo precisa ler o cache inteiro de volta para atender sobre ele, por apenas um token de trabalho novo.

Um prompt longo, portanto, reivindica imediatamente, no prefill, a maior parte da pegada final de cache de uma requisição, enquanto o decode acrescenta o resto aos poucos. Um plano de capacidade que só olha para o "comprimento de contexto final" na verdade está perguntando "quão grande isso vai ficar depois do prefill mais quantos passos de decode eu espero", e as duas fases contribuem em cronogramas muito diferentes.

![Um gráfico do tamanho do cache ao longo do tempo: o cache salta quase na vertical durante o único passo de prefill e depois sobe em uma escada lenta e constante durante o decode, conforme cada token de saída acrescenta mais um token de cache. Um prompt de 2048 tokens reivindica cerca de 640 MB no prefill, enquanto 128 passos de decode acrescentam apenas cerca de 40 MB, 6% do total.](images/prefill-decode-cache-growth.svg)

### Uma alavanca independente dos pesos do próprio modelo: a precisão do cache

A fórmula da lição 2 carregava `bytes_per_value` como um termo próprio, separado de `num_layers`, `num_kv_heads` e `head_dim`. Esse termo não precisa coincidir com a precisão em que o modelo calcula. Uma stack de serving pode armazenar o próprio KV cache em uma precisão menor, geralmente fp8, enquanto o modelo continua calculando em bf16 ou fp16. Reduzir `bytes_per_value` de 2 bytes para 1 corta a pegada do cache pela metade de imediato, sem mudança em `num_kv_heads`, sem mudança no comprimento de contexto e sem retreinamento: é uma escolha de tempo de serving, independente da precisão para a qual os pesos foram quantizados.

Isso se soma a tudo o que veio da lição 2. Retome os números do Llama-2-70B (80 camadas, 8 KV heads, `head_dim` = 128): em fp16, o custo por token era 320 KB. Em fp8, é `2 × 80 × 8 × 128 × 1 byte = 163,840 bytes ≈ 160 KB`, exatamente a metade, porque só `bytes_per_value` mudou.

## Prática

1. ▢ Uma requisição tem um prompt de 2048 tokens. Usando o valor de fp16 do Llama-2-70B, de 320 KB por token, quanto cache o prefill sozinho reivindica, antes de qualquer token de saída ser gerado?

<details markdown="1"><summary>Verificação</summary>

`320 KB × 2048 ≈ 640 MB`, reivindicados no único passo de prefill.

</details>

2. ▢ Essa mesma requisição então gera 128 tokens de saída no decode. Quanto cache adicional o decode acrescenta, e que fração do cache final total da requisição isso representa?

<details markdown="1"><summary>Dica</summary>

O decode acrescenta `bytes per token × number of decode steps`. Compare isso com o valor do prefill da questão 1.

</details>

<details markdown="1"><summary>Verificação</summary>

`320 KB × 128 ≈ 40 MB` acrescentados pelo decode. O cache total é `640 MB + 40 MB = 680 MB`, então o decode é só cerca de 6% do total; o prefill reivindicou os outros 94% em um único passo.

</details>

3. ▢ Usando o valor de cache em fp8 do Llama-2-70B, de 160 KB por token, calcule a pegada total do cache para um batch de 64 sequências com contexto de 4096 tokens.

<details markdown="1"><summary>Dica</summary>

`total cache bytes = bytes per token × context length × batch size`, a mesma fórmula do aquecimento.

</details>

<details markdown="1"><summary>Verificação</summary>

`160 KB × 4096 × 64 = 41,943,040 KB ≈ 40 GB`.

</details>

4. ▢ A versão em fp16 desse mesmo batch (questão 3, mas com 320 KB por token) custaria quanto de cache, e o que a comparação mostra sobre empilhar uma mudança de precisão sobre uma mudança de compartilhamento de heads?

<details markdown="1"><summary>Verificação</summary>

`320 KB × 4096 × 64 ≈ 80 GB`, exatamente o dobro. O cache em fp8 reduz a pegada pela metade sobre o que a GQA já devolveu em relação à MHA completa: as duas alavancas são independentes e se multiplicam, em vez de uma substituir a outra.

</details>

## Prática no mundo real

- [ ] Encontre a flag da sua stack de serving para o tipo de dados do KV cache (vLLM: `--kv-cache-dtype`) e leia quais precisões ela suporta e o que ela avisa sobre acurácia.
- [ ] Para um formato de requisição que você realmente espera (comprimento do prompt, comprimento esperado da saída), calcule quanto do cache final o prefill reivindica em comparação com o decode, usando o valor real por token de um modelo.
- [ ] Amanhã: leia um parágrafo da documentação do vLLM sobre chunked prefill e anote, em uma frase, por que dividir o prefill em pedaços muda o cronograma de reivindicação de memória descrito nesta lição.

## Para ir além

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Artigo: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
