---
title: "Mapeamento para o código real"
description: "Onde cada peça derivada vive no transformers ou no llama.cpp, os três desvios padrão em relação ao artigo original, o byte-pair encoding e onde um adapter de baixo rank se acopla"
type: reference
---

# Mapeamento para o código real

A etapa 5 comprimida para consulta. A [lição 12](../lessons/0012-reading-real-model-code.md) cobre traduzir as derivações deste workspace para a nomenclatura do `transformers` da Hugging Face e do llama.cpp; a [lição 13](../lessons/0013-tokenizers-and-low-rank-adapters.md) cobre derivar o byte-pair encoding e onde um adapter de baixo rank se acopla a uma matriz de pesos. Esta folha traz o mapeamento de nomes, os desvios padrão e as duas derivações, lado a lado.

## Nomenclatura no `transformers` da Hugging Face

| Nome no código real | Derivado em | O que é |
|---|---|---|
| `GPT2Attention` (ou similar) | Lições 1-2 | Scaled dot-product attention, muitas vezes por meio de uma camada linear QKV fundida e separada depois, um detalhe de eficiência de batched-matmul, e não uma operação diferente |
| Um buffer de máscara triangular inferior registrado | Lição 3 | Máscara causal, pré-calculada uma vez, já que a máscara depende apenas do comprimento da sequência, e não dos valores da entrada, e reutilizada ou fatiada a cada chamada |
| `wte` (word token embedding) | Lição 8 | A tabela de embeddings de entrada |
| `wpe` (word position embedding) | Lição 4 | Codificação posicional, aqui em geral uma tabela aprendida e não a fórmula sinusoidal |
| Uma `ModuleList` de blocos, percorrida em um loop for | Lição 7 | Blocos transformer empilhados |
| `lm_head`, amarrado aos pesos de `wte` | Lição 8 | A projeção de saída, via weight tying |
| O script de treinamento ou o `Trainer`, e não a classe do modelo | Lições 9-11 | Loss de cross-entropy, `.backward()`, o passo do otimizador; a classe do modelo apenas define o forward pass até os logits |

## Três desvios padrão em relação ao artigo original

| Peça | Artigo original | Comum em modelos de produção | Ainda é a mesma lição de fundo |
|---|---|---|---|
| Embedding de posição | Fórmula sinusoidal | Uma tabela aprendida, ou rotary embeddings | A alternativa aprendida da lição 4, ou uma variante adicional |
| Função de ativação | ReLU | GELU (ou SwiGLU) | O formato de expandir e depois contrair da lição 6, uma não linearidade diferente |
| Posição da norma | Post-norm | Pre-norm | A alternativa pre-norm da lição 5 |

Nenhum deles muda a arquitetura que este workspace derivou; são variações padrão encontradas em quase toda implementação real, e não um design diferente.

## A mesma matemática, uma base de código diferente: llama.cpp

O llama.cpp (C, por meio da biblioteca de tensores `ggml`) constrói um grafo de computação explícito por chamadas de função, e não por classes `nn.Module` com um método `forward`. Ele calcula os mesmos objetos matemáticos: atenção, codificação posicional (em geral rotary), normalização (em geral RMSNorm, uma variante simplificada da layer norm) e um bloco feed-forward (em geral SwiGLU). A diferença está inteiramente em como o grafo de computação é construído e executado, e não no que ele calcula.

## Derivando o tokenizer: byte-pair encoding (BPE)

1. Representar o texto de treinamento como uma sequência de bytes brutos ou caracteres, cada um uma entrada própria do vocabulário.
2. Contar todo par adjacente de símbolos no corpus.
3. Mesclar o único par mais frequente em um novo símbolo, adicionado ao vocabulário.
4. Repetir até que o vocabulário atinja um tamanho-alvo escolhido.

Exemplo resolvido, corpus `"low low lower"`: o par `l, o` é frequente e é mesclado em `lo`; a rodada seguinte encontra `lo, w` e mescla em `low`. Palavras frequentes se comprimem em direção a um único token; palavras raras recorrem a pedaços menores e mais frequentes.

`vocab_size` é quantos símbolos iniciais mais etapas de mesclagem o treinamento do tokenizer executou, fixado quando o treinamento termina; é exatamente o que dimensiona a tabela de embeddings de entrada e a camada de saída da lição 8.

## Onde um adapter de baixo rank se acopla

O mecanismo de adapter de `llm/finetuning`, `ΔW = BA` com `A` projetando para baixo até o rank `r` e `B` projetando de volta para cima, se acopla a uma matriz de pesos concreta que este workspace derivou, por exemplo a projeção de query por head da lição 2:

```text
Q_i = X (W_Q^i + (alpha / r) B_i A_i)
```

| Matriz | Congelada? | Recebe gradientes durante o treinamento do adapter? |
|---|---|---|
| `W_Q^i` | Sim, exatamente como pré-treinada | Não |
| `A_i`, `B_i` | Não, recém-adicionadas, dimensionadas pelo rank `r` | Sim |

Como a atualização é aditiva e linear, exatamente como a projeção original, `W_Q^i + (alpha/r) B_i A_i` colapsa em uma única matriz comum depois do treinamento. Nada no forward pass muda para servir o resultado mesclado, já que ele se encaixa em `Q_i = X W_Q^i` como uma matriz de projeção comum, com zero computação adicional na inferência.

## Antes de ler ou acoplar algo ao código de um modelo real

- [ ] Uma camada linear QKV fundida que é separada depois é reconhecida como um detalhe de eficiência, e não como uma operação diferente das projeções por head.
- [ ] O buffer de máscara, se pré-calculado, é entendido como dependente apenas do comprimento da sequência, sem mudar o próprio mecanismo de mascaramento.
- [ ] As escolhas de embedding de posição, ativação e posição da norma são conferidas contra os três desvios padrão antes de serem tratadas como uma arquitetura diferente.
- [ ] O ponto de acoplamento de um adapter de baixo rank é nomeado como uma matriz de pesos específica (qual projeção, em qual camada), e não apenas "o modelo".

## Fontes

- [Repositório: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repositório: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Artigo científico: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow e Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md): o termo canônico de `llm/finetuning` para o padrão de base congelada mais pequenos pesos treináveis
- [Recursos](../RESOURCES.md)
