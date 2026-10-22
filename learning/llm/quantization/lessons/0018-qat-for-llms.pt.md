---
title: "18. QAT para LLMs"
description: "O que o treinamento ciente de quantização custa em um LLM, o que ele recupera e quando a PTQ basta"
type: lesson
---

# Lição 18. QAT para LLMs

**Ligação com a missão:** A missão pede que você diga quando o treinamento ciente de quantização compensa o seu custo em relação à quantização pós-treinamento, o que exige a etiqueta de preço, o ganho medido e os casos em que o ganho é zero.
**Fonte principal:** [Artigo científico: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
**Pré-requisitos:** [Lição 17](0017-fake-quantization-and-the-ste.md), [Treinamento ciente de quantização](../GLOSSARY.md), [Quantização pós-treinamento](../GLOSSARY.md), [Quantização somente de pesos](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 9 comparou o round-to-nearest em 8 bits e em 4 ou menos. Em qual dos dois ele se sustenta, e por que escorrega no outro?

<details markdown="1"><summary>Verificação</summary>

Ele se sustenta em 8 bits, onde a grade tem 256 níveis e o [erro de arredondamento](../GLOSSARY.md) por peso é pequeno. Em 4 bits há 16 níveis, cada peso pode errar em até meio passo muito maior, e o arredondamento simples não tem nada que compense os erros. Essa diferença é o espaço em que GPTQ, AWQ e QAT competem.

</details>

2. ▢ Por que um loop de treinamento não pode simplesmente diferenciar através de `round`, e o que a quantização fake faz a respeito?

<details markdown="1"><summary>Verificação</summary>

A derivada de round é zero quase em toda parte, então nenhum gradiente chega aos pesos. A quantização fake mantém uma cópia master em float, aplica quantizar e dequantizar no forward pass e usa o [straight-through estimator](../GLOSSARY.md) para passar o gradiente pela etapa de arredondamento no backward pass, com gradiente zero para os valores que o clamp cortou.

</details>

## Saiba isto

### O que o QAT custa em um LLM

O QAT é treinamento comum com quantização fake inserida, então herda os custos do treinamento. Nagel et al. os listam: treinamento mais longo, a necessidade de dados e busca de hiperparâmetros ([white paper](https://arxiv.org/abs/2106.08295), seção 4). Duas medições específicas de LLMs tornam isso concreto.

A equipe do PyTorch o mediu com o fluxo de QAT do torchao no Llama3-8B, usando ativações dinâmicas int8 per-token com pesos agrupados int4. Cada uma das 225 camadas lineares recebe pelo menos uma operação de fake quantize. Nos microbenchmarks deles, o fine-tuning com QAT foi cerca de 34% mais lento que o full fine-tuning comum, e com activation checkpointing o uso de memória subiu cerca de 2.35 GB por GPU ([blog do PyTorch](https://pytorch.org/blog/quantization-aware-training/)). Um fine-tune de 20 horas passa a levar cerca de 27 horas. Esses são os números deles no setup deles, então trate-os como uma ordem de grandeza.

O segundo custo são os dados. Liu et al. observam que os dados de treinamento originais de um LLM muitas vezes não estão disponíveis, e que os modelos muitas vezes são treinados em vários estágios (instruction tuning, reinforcement learning) que seriam difíceis de replicar durante o QAT. A resposta deles é o treinamento **data-free**: o modelo de precisão total gera o texto sozinho, com os primeiros tokens escolhidos de forma gulosa e o resto amostrado, e o modelo quantizado é treinado para igualar o modelo de precisão total como seu professor. Eles relatam destilar os modelos quantizados a partir de apenas um pequeno conjunto de 100.000 sequências amostradas, em um único nó de 8 GPUs. As sequências foram limitadas a 1.024 tokens, então o conjunto inteiro tem no máximo cerca de 100 milhões de tokens, um número que decorre dos dois números deles e não um que eles afirmem.

### O que ele recupera

O LLM-QAT quantiza pesos, ativações e o KV cache, escritos como W-A-KV em bits. A Tabela 1 deles relata a acurácia zero-shot média em sete tarefas de senso comum. Para o LLaMA-7B, a média em precisão total é 66.2.

| Configuração (W-A-KV) | RTN | SmoothQuant | LLM-QAT |
|---|---|---|---|
| 8-8-8 | 65.6 | 66.3 | 66.0 |
| 4-16-16 (somente pesos de 4 bits) | 63.0 | não reportado | 64.4 |
| 4-8-4 | 41.2 | 43.2 | 60.7 |

Em 8 bits, todo método fica a um ponto da precisão total. O somente pesos de 4 bits já se sustenta com o RTN, e o QAT ganha 1.4 ponto. A configuração de ativações e KV cache de 4 bits é onde os métodos de PTQ colapsam e o QAT fica a 5.5 pontos. No LLaMA-30B, a média em precisão total é 71.4: o 4-8-4 dá 42.5 com o RTN e 40.7 com o SmoothQuant contra 69.9 do LLM-QAT, mas somente pesos de 4 bits dá 70.1 com o RTN, 70.3 com o GPTQ e 70.1 com o LLM-QAT. O próprio resumo do artigo concorda: todos os métodos vão bem em 8 bits, e quando pesos, ativações ou KV cache caem abaixo de 8 bits os métodos de PTQ perdem acurácia enquanto o LLM-QAT se sustenta muito melhor. Os baselines de PTQ aqui são RTN, GPTQ e SmoothQuant. Os métodos de rotação da lição 15 vieram depois e não estão nesta comparação.

O blog do torchao relata o mesmo padrão pelo lado do treinamento. No Llama3-8B com o esquema 8da4w, o QAT recuperou 96% da degradação de acurácia normalizada no hellaswag em comparação com a PTQ, e 68% da degradação de perplexity por palavra no wikitext. Com pesos de 2 bits, a perplexity por palavra no wikitext do modelo PTQ era 603.336. Pular as 3 primeiras e as 2 últimas camadas a levou para 6.766, e acrescentar QAT a isso a levou para 30. Sem pular essas camadas, o QAT foi muito menos eficaz, então o QAT não resgatou os 2 bits sozinho.

### O QLoRA é o vizinho, não é QAT

O [QLoRA](https://arxiv.org/abs/2305.14314) também treina um modelo quantizado, mas faz backpropagation por um base congelado de 4 bits até adapters de baixo rank. Os pesos do base nunca mudam, então o modelo não está aprendendo a sobreviver ao próprio arredondamento: a quantização está ali para fazer o fine-tune caber na memória. Esta trilha não o ensina. A trilha de finetuning o ensina, e a sua folha de [orçamento de memória](../../finetuning/reference/memory-budget.md) conta os bytes.

### Quando a PTQ basta e quando o QAT compensa

| Situação | Evidência | Padrão |
|---|---|---|
| Pesos e ativações de 8 bits | Tabela 1 acima; [Kurtic et al.](https://arxiv.org/abs/2411.02355) relatam o FP8 efetivamente sem perdas entre os tamanhos do Llama 3.1 e o INT8 bem ajustado com 1 a 3% de degradação | PTQ |
| Somente pesos de 4 bits, modelo grande | Linha do LLaMA-30B acima; Kurtic et al. descobrem que o INT4 somente de pesos rivaliza com o de 8 bits | PTQ, depois meça |
| Somente pesos de 4 bits, modelo pequeno | LLaMA-7B: o RTN perde 3.2 pontos, o QAT 1.8 | Tente a PTQ, QAT se a diferença importar |
| Ativações ou KV cache de 4 bits | LLaMA-30B 4-8-4: RTN 42.5, LLM-QAT 69.9 | QAT, ou as rotações da lição 15, testadas |
| 3 bits ou menos | Experimentos de 2 e 3 bits do torchao | QAT mais manter as camadas sensíveis |
| Modelo treinado com uma grande quantidade de dados | [Kumar et al.](https://arxiv.org/abs/2411.04330) descobrem que a degradação da PTQ cresce conforme um modelo vê mais dados | Teste a PTQ cedo, espere uma diferença maior |

O resultado de Kumar vem de modelos de até 1.7B de parâmetros treinados com até 26B de tokens, então diz onde olhar, não o tamanho da diferença para um modelo grande. Cada linha é um padrão a testar contra o seu próprio baseline, não uma regra.

## Prática

1. ▢ A partir dos números do LLM-QAT acima para o LLaMA-30B (precisão total 71.4), quantos pontos o RTN perde com somente pesos de 4 bits, e quantos com 4-8-4? O QAT compensa o seu custo em cada caso?

<details markdown="1"><summary>Verificação</summary>

O RTN perde 1.3 ponto com somente pesos de 4 bits (70.1) e 28.9 pontos em 4-8-4 (42.5). Com somente pesos, o LLM-QAT também marca 70.1, então não compra nada aqui e a PTQ basta. Em 4-8-4, o LLM-QAT marca 69.9, 1.5 ponto abaixo da precisão total, então o custo do treinamento compra quase toda a acurácia perdida. O QAT compensa quando ativações ou o KV cache vão para 4 bits, não quando só os pesos vão.

</details>

2. ▢ Um full fine-tune do seu modelo leva 20 horas. Usando o microbenchmark do torchao, quanto tempo levaria aproximadamente a mesma execução com QAT, e o que mais cresce?

<details markdown="1"><summary>Verificação</summary>

Cerca de 27 horas (20 vezes 1.34 dá 26.8). A memória também cresce, em cerca de 2.35 GB por GPU com activation checkpointing ligado, porque os pesos precisam ser clonados antes de a quantização fake ser aplicada. Esse é um setup medido no Llama3-8B, então a sua execução pode diferir.

</details>

3. ▢ Qual destes descreve o QLoRA?

    - a) Treinar adapters através de um modelo base congelado de 4 bits
    - b) Atualizar todos os pesos atrás de uma etapa de arredondamento straight-through
    - c) Destilar o modelo em texto que ele mesmo gerou
    - d) Quantizar o KV cache enquanto se faz fine-tuning do modelo

<details markdown="1"><summary>Verificação</summary>

**a)** O QLoRA mantém o base quantizado congelado e treina pequenos adapters através dele. (b) descreve o QAT em geral: os pesos mudam para sobreviver ao arredondamento. (c) é a destilação data-free do LLM-QAT. (d) é algo que o LLM-QAT também faz, e o QLoRA não.

</details>

4. ▢ No experimento de 2 bits do torchao, o QAT levou a perplexity por palavra no wikitext de 6.766 para 30. Isso mostra que o QAT sozinho faz pesos de 2 bits funcionarem?

<details markdown="1"><summary>Dica</summary>

Olhe o que já tinha sido feito ao modelo antes de o QAT ser acrescentado, e o que aconteceu sem ele.

</details>

<details markdown="1"><summary>Verificação</summary>

Não. Esse modelo já tinha as suas 3 primeiras e 2 últimas camadas deixadas sem quantizar, uma etapa que custou tamanho de modelo e que tinha levado a perplexity de 603.336 para 6.766. Sem pular essas camadas, o QAT foi muito menos eficaz. Em bits muito baixos, o QAT é um ingrediente ao lado de manter as camadas sensíveis em precisão maior, o que é uma decisão sobre o que quantizar além de como.

</details>

5. ▢ O modelo int4 de PTQ da sua equipe está bom, mas o próximo modelo que vocês treinam é treinado com três vezes mais dados e a sua versão int4 marca notavelmente pior. O que a literatura desta lição sugere, e o que você não deve concluir?

<details markdown="1"><summary>Verificação</summary>

Kumar et al. relatam que a degradação da PTQ cresce conforme um modelo é treinado com mais dados, então uma diferença maior depois de um treinamento mais longo é o que a evidência das leis de escala prevê. Opções a testar são uma largura em bits maior, um método de PTQ mais forte ou o QAT. Não conclua que é inevitável nem dê o seu tamanho: a evidência deles é para modelos de até 1.7B de parâmetros e 26B de tokens, então execute a comparação no seu próprio modelo contra o baseline de precisão total.

</details>

## Prática no mundo real

- [ ] Abra o blog de QAT do PyTorch e encontre a frase sobre o que a etapa de convert produz em comparação com o fluxo de PTQ. Anote o que isso implica para implantar um modelo de QAT nos mesmos kernels que um de PTQ.
- [ ] Escolha um modelo aberto quantizado que você poderia implantar e leia o seu model card: ele diz se os pesos vieram de PTQ ou de QAT, e quais dados de calibração ou de treinamento foram usados?
- [ ] Amanhã: sem consultar anotações, escreva três custos do QAT, as situações em que a PTQ basta e a situação em que o QAT compensa.

## Para ir além

- [QAT e Hardware](../reference/qat-and-hardware.md)
- [Blog: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch, 2024](https://pytorch.org/blog/quantization-aware-training/)
- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- [Fine-tuning: Orçamento de memória](../../finetuning/reference/memory-budget.md)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
