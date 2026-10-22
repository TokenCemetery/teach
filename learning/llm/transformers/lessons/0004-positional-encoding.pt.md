---
title: "4. Codificação posicional"
description: "Por que a atenção é cega à ordem por conta própria, e como a codificação sinusoidal dá a cada posição uma assinatura distinguível"
type: lesson
---

# Lição 4. Codificação posicional

**Ligação com a missão:** A etapa 2 abre as peças que cercam a atenção (lições 1 a 3) para transformá-la em um bloco transformer completo; a codificação posicional é a primeira delas, e sem ela a atenção seria cega àquilo de que a linguagem mais depende: a ordem.
**Fonte principal:** [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Pré-requisitos:** [Lição 3](0003-causal-masking.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que a máscara causal é aplicada aos scores brutos antes do softmax, em vez de zerar os pesos depois de o softmax já ter rodado?

<details markdown="1"><summary>Verificação</summary>

Os pesos do softmax são calculados em conjunto e já somam 1; zerar um deles depois deixa os demais sem somar 1. Mascarar antes do softmax permite que os pesos restantes, não mascarados, sejam renormalizados automaticamente como parte do mesmo cálculo.

</details>

2. ▢ Escreva de memória a equação da scaled dot-product attention.

<details markdown="1"><summary>Verificação</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`.

</details>

## Saiba isto

### A atenção não tem nenhuma noção de ordem embutida

A scaled dot-product attention calcula a sua saída a partir de produtos escalares entre queries e keys e de somas ponderadas sobre values; nada nesse cálculo faz referência a onde um token está na sequência. Troque as posições de dois tokens de entrada (e, correspondentemente, as linhas de `Q`, `K` e `V` que vieram deles), e a saída de atenção de todas as outras posições é idêntica, apenas renomeada para acompanhar a troca: as relações e os pesos baseados em conteúdo que o cálculo produz não mudam em nada. A atenção trata a sua entrada como um conjunto não ordenado de vetores, e não como uma sequência, embora a linguagem claramente não seja independente da ordem: "cão morde homem" e "homem morde cão" compartilham todas as palavras e significam coisas inteiramente diferentes.

### A posição precisa estar embutida nos próprios vetores

A equação da atenção só enxerga `Q`, `K` e `V`; não há canal lateral para "e, aliás, eis de que posição cada um destes veio". A única forma de a atenção se tornar sensível à posição é se a posição já estiver codificada dentro dos vetores que produzem `Q`, `K` e `V` logo de início, ou seja, dentro dos embeddings dos tokens antes de eles chegarem ao cálculo de atenção. Um vetor de **codificação posicional**, somado ao embedding de cada token, dá a dois tokens com a mesma palavra mas em posições diferentes embeddings numericamente distinguíveis, e é isso que torna os produtos escalares da atenção implicitamente sensíveis à posição.

### Codificação sinusoidal: uma assinatura única e estruturada por posição

A escolha do artigo original constrói a codificação de cada posição a partir de funções seno e cosseno em frequências diferentes, um par de dimensões por frequência:

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

Pares de dimensões de índice baixo (`i` pequeno) oscilam lentamente ao longo das posições (um comprimento de onda longo); pares de índice alto oscilam rapidamente (um comprimento de onda curto). Cada posição recebe uma combinação única ao longo de todas essas frequências e, de forma crucial, um deslocamento fixo entre duas posições pode ser expresso como uma função linear da codificação em uma delas (já que o `sin` e o `cos` de uma soma se decompõem em combinações lineares do `sin` e do `cos` das partes). Essa estrutura é parte do motivo pelo qual o artigo argumenta que este esquema pode generalizar para a posição relativa, e potencialmente para comprimentos de sequência não vistos no treinamento, em vez de apenas memorizar um conjunto fixo de posições absolutas.

![Duas ondas plotadas contra a posição no eixo horizontal. A onda de cima, de um par de dimensões de índice baixo, completa uma oscilação lenta ao longo de todo o intervalo de posições mostrado. A onda de baixo, de um par de dimensões de índice alto, completa oito oscilações rápidas no mesmo intervalo. Cada posição recebe uma combinação única de valores ao longo de todas essas ondas de frequências diferentes, e é isso que dá a cada posição uma assinatura distinguível.](images/sinusoidal-frequency-pairs.svg)

### A alternativa mais simples: um embedding de posição aprendido

Em vez de uma fórmula fixa, uma posição pode ser codificada com uma tabela de embeddings comum e aprendida, indexada por posição do mesmo modo que uma tabela de embeddings de tokens é indexada pelo vocabulário, e treinada por gradient descent como qualquer outro parâmetro. Isso é mais simples de implementar e não exige raciocínio sobre frequências, mas não há fórmula a que recorrer para uma posição além do tamanho para o qual a tabela foi dimensionada durante o treinamento: não existe linha na tabela para uma posição que o modelo nunca viu, enquanto a fórmula da codificação sinusoidal ainda pode ser avaliada em qualquer posição.

## Prática

1. ▢ Dois tokens de entrada trocam de posição (e as suas linhas correspondentes em `Q`, `K`, `V` são trocadas junto). O que acontece com a saída de atenção de uma terceira posição que faz query para ambos?

<details markdown="1"><summary>Verificação</summary>

Nada muda nos pesos baseados em conteúdo nem na saída calculada; o resultado é simplesmente renomeado para acompanhar qual posição física os tokens trocados agora ocupam. Isso demonstra a invariância da atenção a permutações: ela calcula relações com base no conteúdo (os produtos escalares), sem nenhuma referência à posição.

</details>

2. ▢ Por que a posição precisa ser codificada nos próprios embeddings dos tokens, em vez de ser passada ao cálculo de atenção como algum sinal separado ao lado de `Q`, `K` e `V`?

<details markdown="1"><summary>Verificação</summary>

A equação da atenção só opera sobre `Q`, `K` e `V`; não há nenhuma entrada adicional por onde a informação de posição possa entrar. A única forma de o cálculo se tornar sensível à posição é se a posição já estiver embutida nos vetores que produzem `Q`, `K` e `V` antes de a atenção rodar.

</details>

3. ▢ Descreva a estrutura de frequências entre os pares de dimensões da codificação posicional sinusoidal e o que ela traz em comparação com usar diretamente o inteiro bruto da posição.

<details markdown="1"><summary>Dica</summary>

Pense no que variar a frequência entre os pares de dimensões consegue e que um único número bruto não conseguiria.

</details>

<details markdown="1"><summary>Verificação</summary>

Pares de dimensões diferentes oscilam em frequências diferentes, de lentas (índice baixo) a rápidas (índice alto) ao longo das posições, dando a cada posição uma combinação única de valores ao longo de todas as frequências, em vez de um escalar bruto. Essa codificação estruturada e multifrequência é também o que permite expressar um deslocamento posicional fixo como uma função linear da codificação de outra posição, uma propriedade que um único inteiro bruto não teria de uma forma que as operações lineares da atenção pudessem explorar de modo tão direto.

</details>

4. ▢ Por que a codificação posicional sinusoidal pode ser avaliada para um comprimento de sequência maior do que qualquer um visto no treinamento, enquanto uma tabela de embeddings de posição aprendida não pode?

<details markdown="1"><summary>Verificação</summary>

A codificação sinusoidal é uma fórmula, avaliável em qualquer valor de posição, inclusive nos que nunca foram encontrados no treinamento. Uma tabela de embeddings aprendida só tem linhas para as posições para as quais foi dimensionada e treinada; uma posição além desse intervalo não tem linha correspondente para consultar.

</details>

5. ▢ Qual afirmação é verdadeira sobre o motivo de a codificação posicional existir?

    - a) Os produtos escalares da atenção já levam em conta a posição relativa sem nenhuma entrada extra
    - b) A atenção trata a sua entrada como um conjunto não ordenado, então a posição precisa ser injetada nos embeddings para que o modelo seja sensível à ordem das palavras
    - c) A codificação posicional só é necessária para sequências muito longas, não para as curtas
    - d) Um embedding de posição aprendido generaliza melhor para comprimentos de sequência não vistos do que a codificação sinusoidal

<details markdown="1"><summary>Verificação</summary>

**b)** Esse é o motivo inteiro de a codificação posicional existir. (a) é falsa: a equação da atenção não faz nenhuma referência à posição por conta própria. (c) é falsa: até o significado de uma sequência curta depende da ordem das palavras, então a mesma cegueira se aplica seja qual for o comprimento. (d) é falsa: é o contrário, a fórmula da codificação sinusoidal pode ser avaliada em qualquer posição, enquanto uma tabela aprendida fica fixa ao que foi treinada.

</details>

## Prática no mundo real

- [ ] Implemente a codificação posicional sinusoidal a partir da fórmula, para um `d_model` pequeno, e plote ou imprima os vetores de codificação de algumas posições para ver as diferentes frequências de oscilação entre os pares de dimensões.
- [ ] Some a sua codificação posicional a um conjunto de embeddings de tokens e confirme que o mesmo token em duas posições diferentes agora produz vetores numericamente diferentes.
- [ ] Amanhã: leia por inteiro a seção "Positional Encoding" do artigo científico da fonte principal e confira a afirmação sobre generalizar para sequências mais longas com o que a sua própria implementação de fato produziria além do intervalo de treinamento.

## Para ir além

- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Artigo: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
