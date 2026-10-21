---
title: "llama.cpp"
description: "O formato do GGUF e a sua nomenclatura de quantização, a abstração de backends do ggml e o que muda quando o serving sai da GPU"
type: reference
---

# llama.cpp

A stack de serving para CPU/edge. Feito para consulta ao colocar no ar ou raciocinar sobre um deployment com llama.cpp.

## GGUF

Um único arquivo binário que reúne pesos, tokenizer e metadados de arquitetura, no lugar dos vários arquivos separados (`config.json`, tokenizer, pesos) com que um checkpoint do Hugging Face é entregue. A reunião importa mais para o deployment em edge: enviar um arquivo para rodar com um binário pequeno e com poucas dependências, sem Python nem ecossistema Hugging Face instalado para remontar as peças.

Como o GGUF organiza os pesos em um formato que o SO consegue ler diretamente, o llama.cpp pode **mapear o arquivo em memória** (`mmap`) em vez de lê-lo ansiosamente para a RAM e desserializá-lo. As páginas são lidas do disco só conforme algo as toca, e o próprio page cache do SO gerencia o que fica residente. Isso importa mais onde a RAM é o recurso mais apertado, em hardware de CPU e edge, e menos em um servidor de GPU com RAM de sistema de sobra.

### Nomenclatura de quantização

O GGUF carrega a família de quantização própria do llama.cpp, separada de GPTQ e AWQ, orientados a GPU. Decodificando um nome como `Q4_K_M`:

| Parte | Significado |
|---|---|
| `Q4` | Largura de bits: aproximadamente 4 bits por peso (também `Q5`, `Q8` e outros) |
| `K` | Um tipo **k-quant**: uma largura de bits por tensor, com super-blocos de 256 pesos cujos sub-blocos carregam, cada um, a sua própria escala |
| `M` | A receita que mistura tipos entre tensores, dando a alguns tensores um tipo de mais bits: `S` (small), `M` (medium), `L` (large). Veja a [folha Measuring and Storing da trilha de quantização](../../quantization/reference/measuring-and-storing.md) |

## ggml: uma base de código, vários backends

O llama.cpp é construído sobre o **ggml**, uma biblioteca de tensores em C sem dependências (nenhuma BLAS externa exigida). Uma passada forward é um grafo de computação estático, construído uma vez e depois executado, em vez da execução eager, operação por operação, do PyTorch. Essa separação entre "o que calcular" e "o que executa" é o que permite ao mesmo grafo mirar vários **backends**, CPU (AVX2/NEON), CUDA, Metal, Vulkan, a partir de uma base de código, sem runtime de Python, em hardwares que vão da CPU ARM de um celular à GPU Metal de um Mac e a um Raspberry Pi. O design do vLLM, em contraste, é específico do CUDA e não consegue rodar sem uma GPU NVIDIA.

## Threads substituem o batching em GPU

| | Espalha | Limitado por |
|---|---|---|
| Batching em GPU (`--max-num-seqs`) | O custo de largura de banda de memória entre sequências concorrentes | A capacidade do cache e o orçamento de latência |
| Threads de CPU (`--threads`) | As multiplicações de matrizes de uma única sequência entre cores | A contagem de cores físicos da CPU |

O threading acelera o compute de uma única sequência; ele não tem o equivalente do "já estou pagando pela leitura de memória de qualquer jeito" para amortizar entre as requisições de estranhos como o batching em GPU tem.

## Colocando o servidor no ar

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

O mesmo formato de requisição compatível com a OpenAI do [vLLM](vllm.md); o que muda é tudo o que está por baixo.

## O que muda fora da GPU

| Mecanismo | Em uma GPU (vLLM) | Em escala de CPU/edge (llama.cpp) |
|---|---|---|
| Concorrência | O [continuous batching](batching.md) amortiza a largura de banda de memória entre as requisições de centenas de estranhos concorrentes | Um punhado de slots em paralelo (de um dígito a algumas dezenas); uma carga de trabalho típica em edge, um dispositivo servindo o seu próprio usuário, raramente tem centenas de requisições concorrentes para agrupar |
| Gerenciamento de cache | O [PagedAttention](vllm.md#pagedattention) gerencia um pool compartilhado grande e em constante mudança | Um cache contíguo e mais simples por sequência é adequado; o problema que o PagedAttention resolve raramente chega à escala em que a sua complexidade se paga |
| Momento da quantização | Uma flag de tempo de serving (`--quantization`), escolhida no lançamento | Já travada quando um nível específico de quantização GGUF foi escolhido ou produzido; mudá-la significa usar outro arquivo, e não uma flag |

Os trade-offs em si ([memória, velocidade e acurácia](quantization-at-serve-time.md)) não mudam; só muda quando cada decisão é tomada e em que concorrência ela compensa.

## Relacionado

- [Lição 13](../lessons/0013-gguf.md), [Lição 14](../lessons/0014-llamacpp-architecture.md), [Lição 15](../lessons/0015-what-changes-off-gpu.md)
- [vLLM](vllm.md), [Batching](batching.md), [Quantização no Serving](quantization-at-serve-time.md): os mecanismos do lado da GPU com que esta folha contrasta
