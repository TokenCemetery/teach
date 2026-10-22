---
title: "12. Lendo código real de modelos"
description: "Onde cada peça derivada vive em uma biblioteca de modelos de produção, e os pequenos desvios comuns em relação ao artigo original que vale reconhecer em vez de se confundir com eles"
type: lesson
---

# Lição 12. Lendo código real de modelos

**Ligação com a missão:** A etapa 5 passa da derivação ao código real: tudo o que foi derivado a partir de tensores brutos nas etapas 1 a 4 existe dentro de código real, de produção, com nomes diferentes e com um punhado de pequenos desvios padrão em relação ao artigo original, e esta lição é como traduzir entre o que foi construído aqui e o que de fato roda na prática.
**Fonte principal:** [Repositório: transformers, Hugging Face](https://github.com/huggingface/transformers)
**Pré-requisitos:** [Lição 11](0011-adamw-optimizer.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ O que dá errado ao embutir o weight decay no gradiente no Adam original e o que o AdamW faz de diferente?

<details markdown="1"><summary>Verificação</summary>

Embutido no gradiente, o weight decay é dividido pelo termo de escalonamento adaptativo junto com todo o resto, então o seu encolhimento efetivo varia por parâmetro em vez de se aplicar de modo uniforme. O AdamW aplica o weight decay diretamente aos pesos, somado à atualização separadamente do termo baseado em gradiente.

</details>

2. ▢ Os pesos de um bloco transformer são os mesmos de outro bloco da pilha? O que isso custa e o que compra?

<details markdown="1"><summary>Verificação</summary>

Não, cada bloco tem os seus próprios parâmetros, aprendidos de forma independente, o que custa contagem de parâmetros de forma aproximadamente linear com a profundidade, mas permite que blocos diferentes se especializem de modo diferente, em vez de serem forçados a calcular uma transformação idêntica em todas as profundidades.

</details>

## Saiba isto

### As mesmas peças, com nomes diferentes

Um modelo estilo GPT-2 na biblioteca `transformers` da Hugging Face implementa tudo o que este workspace derivou, apenas com as suas próprias convenções de nomes. A atenção vive em uma classe como `GPT2Attention`, que calcula a mesma operação de scaled dot-product da lição 1, muitas vezes por meio de uma camada linear fundida que produz Q, K e V concatenados e depois separados, um detalhe de eficiência de batched-matmul, e não uma operação diferente das projeções separadas por head da lição 2. A máscara causal (lição 3) aparece como um buffer registrado e pré-calculado que guarda uma máscara triangular inferior, aplicada aos scores de atenção antes do softmax exatamente como derivado, em vez de ser reconstruída do zero a cada chamada de forward: como a máscara depende apenas do comprimento da sequência, e não dos valores reais da entrada, calculá-la uma vez e reutilizá-la (ou fatiá-la) é uma escolha puramente de eficiência, sem mudança no mecanismo em si. Os embeddings de token e de posição aparecem como as tabelas `wte` (word token embedding) e `wpe` (word position embedding) (lições 4 e 8); os blocos empilhados vivem em uma `ModuleList` percorrida por um loop for no método forward do modelo, correspondendo diretamente à lição 7; e a projeção de saída é uma camada linear, comumente chamada de `lm_head`, amarrada aos pesos de `wte` por uma atribuição explícita ou por uma chamada a `tie_weights()`, exatamente o weight tying da lição 8.

![Um mapeamento em duas colunas. À esquerda, cinco peças derivadas neste workspace: a atenção das lições 1 e 2, a máscara causal da lição 3, a codificação posicional da lição 4, os blocos empilhados da lição 7 e o embedding e o weight tying da lição 8. À direita, o nome correspondente que cada uma assume na biblioteca transformers da Hugging Face: GPT2Attention com uma projeção fundida de query, key e value, um buffer triangular inferior registrado, uma tabela de posições wpe aprendida, uma ModuleList de blocos percorrida em um loop for e wte amarrada ao lm_head. Uma linha liga cada conceito da esquerda ao seu nome em código real, à direita.](images/workspace-to-real-code-mapping.svg)

### Três pequenos desvios padrão em relação ao artigo original

Quase todo modelo de produção moderno se afasta do artigo original dos mesmos poucos modos pequenos, e reconhecê-los como implementações de conceitos já cobertos, e não como algo novo, é o objetivo desta lição. **Embedding de posição**: muitos modelos usam uma tabela de posições aprendida (a alternativa da lição 4 à codificação sinusoidal) ou rotary embeddings, em vez da fórmula sinusoidal do artigo original. **Função de ativação**: o bloco feed-forward (lição 6) costuma usar GELU em vez da ReLU do artigo original, o mesmo formato de expandir e depois contrair, uma não linearidade diferente. **Posição da norma**: a maioria dos modelos atuais usa pre-norm (a alternativa da lição 5), colocando a layer norm antes de cada subcamada dentro do ramo residual, em vez da post-norm do artigo original. Nenhum deles muda a arquitetura de fundo que este workspace derivou; são as variações padrão encontradas em quase toda implementação real.

### O código de treinamento vive fora da classe do modelo

As peças da etapa 4, a chamada da loss de cross-entropy, `loss.backward()` e o passo do otimizador, não fazem parte da classe do próprio modelo; elas vivem no script de treinamento ou em um utilitário de treinamento (como o `Trainer` da Hugging Face, ou um loop customizado como o do nanoGPT). A classe do modelo define o forward pass que produz logits; tudo sobre transformar esses logits em um modelo treinado vive uma camada acima, no código que chama o modelo repetidamente e aplica ao redor dele o mecanismo da etapa 4.

### Uma base de código diferente, os mesmos objetos matemáticos

O llama.cpp, construído em C em vez de Python e PyTorch, expressa as mesmas operações, atenção, codificação posicional (em geral rotary), normalização (em geral RMSNorm, uma variante simplificada da layer norm da lição 5) e um bloco feed-forward (em geral com uma ativação SwiGLU), não como classes `nn.Module` com um método `forward`, mas como chamadas explícitas que constroem um grafo de computação no `ggml`, a biblioteca de tensores por baixo dele. As chamadas de construção de grafo e o estilo de classe com método forward não se parecem em nada na página, mas calculam os mesmos objetos matemáticos que este workspace derivou a partir de tensores brutos; a diferença está inteiramente em como o grafo de computação é construído e executado, e não no que ele calcula.

## Prática

1. ▢ Associe cada um destes nomes de código real à lição que derivou o conceito que ele implementa: `wte`, `wpe`, um buffer de máscara triangular inferior registrado, `lm_head` amarrado aos pesos de `wte`, uma `ModuleList` de blocos.

<details markdown="1"><summary>Verificação</summary>

`wte` (word token embedding): o embedding de entrada da lição 8. `wpe` (word position embedding): a codificação posicional da lição 4 (aqui, uma tabela aprendida e não sinusoidal). O buffer de máscara registrado: a máscara causal da lição 3. `lm_head` amarrado a `wte`: o weight tying da lição 8. A `ModuleList` de blocos: o empilhamento da lição 7.

</details>

2. ▢ Nomeie os três pequenos desvios comuns em relação ao artigo original encontrados na maioria das implementações reais modernas e a que alternativa de qual lição cada um corresponde.

<details markdown="1"><summary>Verificação</summary>

Embeddings de posição aprendidos ou rotary em vez de sinusoidais (a alternativa aprendida da lição 4, ou uma variante adicional como a rotary). GELU em vez de ReLU no bloco feed-forward (a não linearidade da lição 6, trocada por uma função diferente, o mesmo formato de expandir e depois contrair). Pre-norm em vez da posição post-norm (a alternativa pre-norm da lição 5 à escolha do artigo original).

</details>

3. ▢ Por que a máscara causal aparece no código real como um buffer registrado e pré-calculado, em vez de ser reconstruída a cada chamada de forward?

<details markdown="1"><summary>Dica</summary>

Considere do que a máscara de fato depende.

</details>

<details markdown="1"><summary>Verificação</summary>

A máscara depende apenas do comprimento da sequência, nunca dos valores reais da entrada, então pode ser calculada uma vez (em geral no comprimento máximo de sequência que o modelo suporta) e reutilizada ou fatiada a cada chamada de forward, em vez de reconstruída do zero a cada vez. Essa é uma escolha puramente de eficiência; o mecanismo de mascaramento em si, somado aos scores antes do softmax, é inalterado em relação à lição 3.

</details>

4. ▢ Como a abordagem do llama.cpp para calcular a atenção e o bloco feed-forward difere mecanicamente do forward pass de um `nn.Module` do PyTorch, ainda calculando as mesmas operações matemáticas de fundo?

<details markdown="1"><summary>Verificação</summary>

O llama.cpp constrói um grafo de computação explícito no `ggml` por meio de chamadas de função em C, em vez de definir uma classe com um método `forward` que o PyTorch rastreia automaticamente enquanto roda. O estilo de construção de grafo parece inteiramente diferente na página, mas as operações que ele constrói, atenção, codificação posicional, normalização, o bloco feed-forward, são os mesmos objetos matemáticos que este workspace derivou a partir de tensores brutos.

</details>

5. ▢ Qual afirmação é verdadeira sobre ler o código de um modelo real depois de derivar a arquitetura do zero?

    - a) Os modelos reais de produção implementam uma arquitetura inteiramente diferente da que o artigo original e este workspace derivam
    - b) As mesmas peças aparecem com nomes diferentes, com um punhado de pequenos desvios padrão (esquema de embedding de posição, função de ativação, posição da norma) que vale reconhecer em vez de tratar como novos
    - c) O código de treinamento (loss, backward pass, otimizador) é sempre parte da definição da classe do próprio modelo
    - d) O llama.cpp calcula operações matemáticas fundamentalmente diferentes das de uma implementação em PyTorch, já que é escrito em C

<details markdown="1"><summary>Verificação</summary>

**b)** É exatamente a tradução que esta lição ensina. (a) é falsa: a arquitetura de fundo é a mesma, apenas nomeada e configurada de modo diferente. (c) é falsa: o código de treinamento vive em um script ou utilitário de treinamento separado, e não dentro da própria classe do modelo. (d) é falsa: as operações são matematicamente idênticas; só difere como o grafo de computação é construído e expresso.

</details>

## Prática no mundo real

- [ ] Abra a implementação de um modelo estilo GPT-2 na biblioteca `transformers` e encontre a sua classe de atenção, a sua máscara causal e a sua nomenclatura `wte`/`wpe`/`lm_head`, associando cada uma à lição que a derivou.
- [ ] Confira se esse mesmo modelo usa pre-norm ou post-norm, e GELU ou ReLU, e anote qual é qual em relação à lista de desvios comuns desta lição.
- [ ] Amanhã: encontre o script de treinamento (ou o uso do `Trainer`) de um modelo a que você tenha acesso e localize o seu cálculo da loss, a chamada `.backward()` e o passo do otimizador.

## Para ir além

- [Repositório: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repositório: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
