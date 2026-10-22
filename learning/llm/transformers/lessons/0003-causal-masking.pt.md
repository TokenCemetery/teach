---
title: "3. Máscara causal"
description: "Por que uma posição de query não deve atender às posições futuras, e por que a máscara é aplicada antes do softmax, e não depois"
type: lesson
---

# Lição 3. Máscara causal

**Ligação com a missão:** Esta é a lição de fechamento da etapa 1: a multi-head attention (lição 2) permite que toda posição atenda a todas as outras posições, o que é exatamente errado para a geração autorregressiva que o modelo deste workspace acabará fazendo, e esta lição é a correção.
**Fonte principal:** [Artigo: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
**Pré-requisitos:** [Lição 2](0002-multi-head-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ Na multi-head attention, ao calcular o escalonamento `/ sqrt(d_k)` dentro de um head, `d_k` deve ser a dimensão por head ou a dimensão completa do modelo?

<details markdown="1"><summary>Verificação</summary>

A dimensão por head (`d_model / h`). O escalonamento compensa o crescimento da variância de um produto escalar somado sobre `d_k` termos, e dentro de um head esse produto escalar é somado sobre a dimensão menor do próprio head.

</details>

2. ▢ O que a etapa de softmax realiza na scaled dot-product attention?

<details markdown="1"><summary>Verificação</summary>

Ela converte os scores brutos de similaridade de cada query com todas as keys em uma distribuição de probabilidade, não negativa e somando 1, e é isso que faz a saída ser uma mistura ponderada dos values.

</details>

## Saiba isto

### Por que atender ao futuro é um problema

Um modelo que gera texto um token por vez produz o token *N* usando apenas os tokens de 1 a *N-1*; o token *N+1* ainda não existe nesse momento. Se a self-attention durante o treinamento deixa a posição *i* atender à posição *j* maior que *i*, o modelo pode usar o próprio token que deveria prever, e todos os tokens depois dele, como parte do cálculo dessa previsão. A loss de treinamento parece ótima, já que o modelo está, na prática, copiando uma resposta que já consegue ver, mas o modelo não aprende nada útil, porque na hora da geração de verdade esses tokens futuros nunca estão disponíveis. A **máscara causal** é o que mantém o treinamento honesto: ela restringe cada posição a atender somente a si mesma e às posições anteriores, combinando exatamente com o que estará disponível quando o modelo gerar texto de fato, um token por vez.

### A máscara é aplicada aos scores, antes do softmax

A correção acontece dentro da própria equação, antes da etapa de softmax: uma máscara é somada aos scores brutos `QK^T / sqrt(d_k)`, definindo como um número negativo muito grande (na prática, menos infinito ou algo numericamente equivalente, como -1e9) toda entrada em que a posição da key é posterior à posição da query. Depois que esse score mascarado passa pelo `exp(...)` dentro do softmax, um número negativo muito grande vira um valor indistinguível de zero, de modo que essa posição contribui essencialmente com nada para a soma ponderada final, e os pesos das posições restantes, não mascaradas, são renormalizados entre si para continuarem somando 1.

### Por que não simplesmente zerar os pesos depois do softmax

Definir como zero o peso de uma posição futura *depois* de o softmax já ter rodado não funciona corretamente: os outros pesos já foram calculados supondo que aquela posição era uma concorrente real pela massa de probabilidade, e zerá-la depois deixa os pesos restantes sem somar 1, o que não é uma distribuição de probabilidade válida. O mascaramento precisa acontecer antes do softmax justamente para que a renormalização ocorra automaticamente como parte do mesmo cálculo.

### Por que o score bruto também não pode simplesmente virar 0

Definir o score bruto de uma posição futura como 0, em vez de um número negativo grande, não a exclui: `exp(0) = 1`, uma contribuição perfeitamente comum e não desprezível para o denominador do softmax, e de modo algum "nenhuma atenção". Um score 0 se lê como uma similaridade neutra, média, competindo em pé de igualdade com o score real de todas as outras posições. Só um número negativo suficientemente grande leva a sua exponencial a efetivamente zero, e é isso que remove corretamente aquela posição da soma ponderada.

### O formato da máscara: um padrão triangular inferior fixo

Para uma sequência de comprimento *n*, a máscara causal é sempre o mesmo padrão triangular inferior: a posição de query *i* pode atender às posições de key de 0 a *i* (inclusive), e é mascarada em relação a toda posição depois de *i*. O mesmo formato de máscara se aplica a todo head de atenção e a todo exemplo de um batch, somado uma única vez à matriz de scores antes de o softmax rodar.

![Uma grade 4 por 4 em que as linhas são as posições de query de 0 a 3 e as colunas são as posições de key de 0 a 3. As células em que a posição da key é menor ou igual à posição da query são sombreadas em cinza e permitidas. As células em que a posição da key é maior que a posição da query, acima da diagonal, são marcadas com um X laranja e mascaradas antes do softmax. As células permitidas formam um padrão triangular inferior que inclui a diagonal.](images/causal-mask-lower-triangular.svg)

## Prática

1. ▢ Por que a atenção da posição *i* não deve incluir nenhuma posição *j* maior que *i*, dado como o modelo será de fato usado na inferência?

<details markdown="1"><summary>Verificação</summary>

Na inferência, o modelo gera um token por vez usando apenas os tokens que vieram antes dele; os tokens depois da posição atual ainda não existem quando ela está sendo prevista. Se o treinamento deixasse a posição *i* atender a uma posição posterior *j*, o modelo aprenderia a depender de informação que nunca estará disponível na hora da geração de verdade.

</details>

2. ▢ Por que a máscara causal é aplicada aos scores brutos antes do softmax, em vez de zerar os pesos de atenção depois de o softmax já ter rodado?

<details markdown="1"><summary>Verificação</summary>

Os pesos de saída do softmax são calculados em conjunto e somam 1 sobre quaisquer scores que ele receber. Zerar um peso depois do fato deixa os pesos restantes somando menos que 1, o que deixa de ser uma distribuição de probabilidade válida. Já mascarar antes do softmax permite que a renormalização entre as posições restantes, não mascaradas, aconteça automaticamente como parte do mesmo cálculo.

</details>

3. ▢ Por que definir o score bruto de uma posição futura como 0 simples (em vez de um número negativo grande) não a exclui corretamente da atenção?

<details markdown="1"><summary>Dica</summary>

Pense em quanto vale `exp(0)` e no que isso significa para o denominador do softmax.

</details>

<details markdown="1"><summary>Verificação</summary>

`exp(0) = 1`, um valor inteiramente comum e não desprezível que ainda compete por massa de probabilidade no denominador do softmax. Um score 0 se lê como uma similaridade média, neutra, e não como "exclua esta posição". Só um número negativo suficientemente grande leva a sua exponencial efetivamente a zero, e é isso que de fato remove a contribuição daquela posição.

</details>

4. ▢ Para uma sequência de 4 tokens (posições de 0 a 3), a quais posições de key a posição de query 2 pode atender sob uma máscara causal?

<details markdown="1"><summary>Verificação</summary>

Às posições 0, 1 e 2. A posição 3, por ser posterior à posição 2, é mascarada.

</details>

5. ▢ Qual afirmação é verdadeira sobre como a máscara causal é implementada?

    - a) Ela zera os pesos de atenção depois de o softmax já tê-los calculado
    - b) Ela soma um número negativo grande aos scores brutos das posições futuras antes do softmax, de modo que as suas exponenciais se tornem desprezíveis e os pesos restantes sejam renormalizados automaticamente
    - c) Ela só se aplica ao primeiro head de atenção, já que os heads seguintes não precisam da restrição
    - d) Definir o score de uma posição futura como 0 equivale a mascará-la

<details markdown="1"><summary>Verificação</summary>

**b)** É exatamente o mecanismo, e a razão de ele precisar acontecer antes do softmax. (a) é falsa: zerar depois do softmax deixa os pesos restantes sem somar 1. (c) é falsa: a mesma máscara se aplica de forma idêntica a todo head. (d) é falsa: um score 0 ainda contribui com um peso inteiro e comum via `exp(0) = 1`, e não exclui a posição de forma alguma.

</details>

## Prática no mundo real

- [ ] Adicione a máscara causal à sua implementação de multi-head attention da lição 2: construa uma máscara triangular inferior para um comprimento de sequência escolhido e some-a aos scores antes do softmax.
- [ ] Para uma sequência pequena, imprima os pesos do softmax de uma posição de query com e sem a máscara aplicada e confirme que a versão mascarada tem peso essencialmente zero nas posições futuras.
- [ ] Amanhã: leia a seção de mascaramento do código da fonte principal ao lado da sua própria implementação e confirme que a máscara é aplicada no mesmo ponto do cálculo (antes do softmax, somada aos scores).

## Para ir além

- [Artigo: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
