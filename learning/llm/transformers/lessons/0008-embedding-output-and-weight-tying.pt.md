---
title: "8. Camadas de embedding e de saída, weight tying"
description: "Como os tokens entram e saem do espaço vetorial do transformer, e por que as duas camadas que fazem isso podem compartilhar uma só matriz"
type: lesson
---

# Lição 8. Camadas de embedding e de saída, weight tying

**Ligação com a missão:** Esta é a lição de fechamento da etapa 3: os blocos empilhados (lição 7) operam inteiramente em vetores de dimensão `d_model`, então algo precisa converter tokens discretos para esse espaço na entrada e de volta para scores do vocabulário na saída, fechando o ciclo dos IDs brutos de token até um forward pass completo.
**Fonte principal:** [Artigo científico: "Using the Output Embedding to Improve Language Models", Press e Wolf, 2017](https://arxiv.org/abs/1608.05859)
**Pré-requisitos:** [Lição 7](0007-stacking-blocks.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que todo bloco transformer precisa preservar a mesma dimensão de entrada e de saída (`d_model` na entrada, `d_model` na saída)?

<details markdown="1"><summary>Verificação</summary>

Empilhar significa que a saída de um bloco alimenta diretamente a entrada do bloco seguinte; se um bloco mudasse a dimensão, todo bloco posterior e o residual stream precisariam ser construídos para um tamanho diferente, quebrando o empilhamento uniforme que permite que o mesmo formato de bloco se repita qualquer número de vezes.

</details>

2. ▢ Os pesos de um bloco de uma pilha transformer padrão são os mesmos de outro bloco? O que isso custa e o que compra?

<details markdown="1"><summary>Verificação</summary>

Não, cada bloco tem os seus próprios parâmetros, aprendidos de forma independente. Isso custa contagem de parâmetros de forma aproximadamente linear com a profundidade, já que nada é compartilhado, mas permite que blocos diferentes se especializem de modo diferente em profundidades diferentes, em vez de todos calcularem a transformação idêntica.

</details>

## Saiba isto

### O embedding de entrada: uma busca do ID do token até o vetor

Um tokenizer (mencionado de passagem aqui; território de `llm/finetuning` para derivar mais a fundo) produz uma sequência de IDs inteiros de token, cada um um índice em um vocabulário fixo. A **camada de embedding de entrada** é uma matriz aprendida de formato `vocab_size × d_model`: a linha `i` é a representação vetorial densa do token `i`. Buscar o embedding de um token é simplesmente ler a sua linha. É aqui que tokens discretos e simbólicos entram no espaço vetorial contínuo sobre o qual todas as peças posteriores, a atenção, o bloco feed-forward, a codificação posicional, de fato operam.

### A camada de saída: projetando de volta para scores do vocabulário

Depois que o último bloco empilhado produz a sua saída, ainda de dimensão `d_model` por posição, o modelo precisa de mais uma etapa para transformar esse vetor de volta em uma previsão sobre o vocabulário. A **camada de saída** é uma projeção linear de formato `d_model × vocab_size`, que produz um score bruto, chamado de **logit**, por token do vocabulário em cada posição. Esses logits (transformados em uma distribuição de probabilidade pela loss de cross-entropy da próxima lição) são o que "prever o próximo token" de fato significa numericamente: um vetor de scores do tamanho do vocabulário, um por token possível.

### Os formatos das duas camadas são transpostos um do outro

A matriz de embedding de entrada é `vocab_size × d_model`; a projeção de saída é `d_model × vocab_size`, exatamente o formato transposto. O **weight tying** aproveita isso diretamente: em vez de aprender uma matriz de saída totalmente separada, o modelo reutiliza a mesma matriz de embedding, transposta, para calcular os logits de saída (`logits = h @ W_embedding^T`). Isso não é uma mera coincidência explorada por conveniência; as duas camadas relacionam um token com essencialmente a mesma pergunta de fundo, o embedding de entrada responde "que vetor representa o token X" e a camada de saída responde "qual a probabilidade do token X", e o tying trata essas duas como compartilhando uma só representação, em vez de aprender duas separadas e sem relação.

![Dois diagramas lado a lado. À esquerda, um id de token busca a sua linha na matriz de embedding, de formato vocab_size por d_model, produzindo um vetor de embedding. À direita, um vetor oculto é projetado pela mesma matriz, transposta para d_model por vocab_size, produzindo um vetor de logits, um score por token do vocabulário. Uma linha tracejada liga as duas matrizes, rotulada mesma matriz de pesos, transposta, mostrando que o weight tying reutiliza uma única matriz aprendida tanto para a busca de entrada quanto para a projeção de saída, em vez de aprender duas separadas.](images/weight-tying-embedding-output.svg)

### O que o tying realmente economiza

Para um vocabulário de 50.000 tokens e `d_model = 768`, só a tabela de embeddings tem `50,000 × 768 = 38,400,000` parâmetros. Um modelo sem tying precisaria de uma segunda matriz do mesmo tamanho para a projeção de saída, outros 38,4 milhões de parâmetros fazendo um trabalho intimamente relacionado. O tying elimina essa segunda matriz inteira e, para modelos com vocabulários grandes em relação ao tamanho oculto, isso é uma fração substancial da contagem total de parâmetros do modelo economizada com essencialmente nenhuma perda, e muitas vezes um ganho mensurável, de qualidade.

## Prática

1. ▢ Qual é o formato da matriz de pesos da camada de embedding de entrada e a que corresponde estruturalmente buscar o embedding de um token específico?

<details markdown="1"><summary>Verificação</summary>

`vocab_size × d_model`. Buscar o embedding de um token é ler a linha da matriz no índice desse token, uma busca direta e não uma transformação calculada.

</details>

2. ▢ Como o formato da camada de saída se relaciona com o formato da camada de embedding de entrada e o que essa relação torna possível?

<details markdown="1"><summary>Verificação</summary>

O formato da camada de saída (`d_model × vocab_size`) é o transposto do formato do embedding de entrada (`vocab_size × d_model`). Essa relação é o que torna o weight tying possível: a mesma matriz, usada de um jeito como tabela de busca e do outro (transposta) como projeção, pode servir aos dois papéis em vez de exigir duas matrizes aprendidas separadamente.

</details>

3. ▢ Para um vocabulário de 50.000 tokens e `d_model = 768`, calcule a contagem de parâmetros da tabela de embeddings e explique o que o weight tying economiza em relação a um modelo sem tying.

<details markdown="1"><summary>Dica</summary>

A contagem de parâmetros da tabela de embeddings é `vocab_size × d_model`. Uma camada de saída sem tying precisaria de uma matriz do mesmo tamanho.

</details>

<details markdown="1"><summary>Verificação</summary>

`50,000 × 768 = 38,400,000` parâmetros para a tabela de embeddings. Um modelo sem tying precisaria de uma segunda matriz, aprendida separadamente, do mesmo tamanho para a projeção de saída; o tying elimina essa segunda matriz inteira, economizando cerca de 38,4 milhões de parâmetros para esse vocabulário e esse tamanho oculto.

</details>

4. ▢ Além de economizar parâmetros, qual é o raciocínio de fundo para o tying das matrizes de pesos de entrada e de saída fazer sentido, em vez de ser apenas um truque conveniente?

<details markdown="1"><summary>Verificação</summary>

As duas camadas relacionam um token com fundamentalmente a mesma representação: o embedding de entrada responde "que vetor representa este token" e a camada de saída responde "qual a probabilidade deste token, dada a representação atual". Como as duas perguntas tratam da mesma relação entre token e vetor, compartilhar uma só representação aprendida entre elas é um viés indutivo razoável, e não meramente uma forma de cortar parâmetros.

</details>

5. ▢ Qual afirmação é verdadeira sobre as camadas de embedding de entrada e de saída?

    - a) Elas devem sempre ser aprendidas como duas matrizes inteiramente separadas, já que servem a propósitos sem relação
    - b) Os seus formatos são transpostos um do outro, e é isso que torna possível o weight tying, reutilizar uma matriz para as duas
    - c) O weight tying só economiza parâmetros e não traz nenhum outro benefício
    - d) O formato da camada de saída depende apenas de `vocab_size`, sem relação com `d_model`

<details markdown="1"><summary>Verificação</summary>

**b)** A relação de formatos transpostos é exatamente o que o tying explora. (a) é falsa: é justamente o que o tying evita precisar. (c) é falsa: argumenta-se que o tying também ajuda a qualidade, já que as duas camadas se relacionam com a mesma representação subjacente do token. (d) é falsa: o formato da camada de saída é `d_model × vocab_size`, dependendo de ambos.

</details>

## Prática no mundo real

- [ ] Implemente a busca do embedding de entrada e a projeção de saída primeiro como matrizes separadas, depois modifique a sua implementação para amarrá-las e confirme que o formato dos logits de saída não muda.
- [ ] Para um modelo que você conhece, procure o tamanho do vocabulário e o `d_model` e calcule quantos parâmetros o weight tying economizaria em comparação com uma versão sem tying.
- [ ] Amanhã: confira se uma implementação de modelo real a que você tenha acesso (na biblioteca `transformers` ou em outro lugar) amarra os pesos de embedding e de saída e encontre onde isso é configurado no código.

## Para ir além

- [Artigo científico: "Using the Output Embedding to Improve Language Models", Press e Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
