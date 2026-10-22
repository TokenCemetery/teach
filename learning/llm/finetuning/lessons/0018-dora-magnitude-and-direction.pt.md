---
title: "18. DoRA: magnitude e direção"
description: "A renormalização desacopla as duas, e isso é o método"
type: lesson
---

# Lição 18. DoRA: magnitude e direção

**Ligação com a missão:** O terceiro método nomeado na missão, e aquele cujo mecanismo é descrito errado com mais frequência.
**Fonte principal:** [Artigo científico: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Pré-requisitos:** [Lição 8](0008-the-low-rank-idea.md), [Lição 9](0009-rank-alpha-and-initialisation.md)

## Aquecimento

1. ▢ Escreva a atualização do LoRA e diga quais fatores são treináveis.

<details markdown="1"><summary>Verificação</summary>

`h = W₀x + (α/r)BAx`. Só `A` e `B` são treináveis; `W₀` está congelada. `B` começa em zero.

</details>

2. ▢ Qual é o rank máximo de uma atualização do LoRA com `r = 8`?

<details markdown="1"><summary>Verificação</summary>

Oito. `BA` não pode exceder o rank da sua dimensão interna, o que limita quais atualizações o adapter consegue expressar.

</details>

3. ▢ Por que a quantização não é de graça em modelos pequenos?

<details markdown="1"><summary>Verificação</summary>

O erro de quantização é uma perturbação relativa fixa, e modelos pequenos têm menos redundância disponível para absorvê-la.

</details>

## Saiba isto

### A observação

Qualquer matriz de pesos pode ser decomposta em uma **magnitude** e uma **direção**. Tomando-a coluna por coluna:

```text
W = m · (V / ‖V‖_c)
```

onde `‖·‖_c` é a norma por coluna, `V / ‖V‖_c` é uma matriz de colunas com norma unitária, que é direção pura, e `m` é um vetor com um escalar por coluna, carregando a magnitude.

Os autores do DoRA analisaram como o full fine-tuning e o LoRA movem cada uma dessas duas grandezas durante o treinamento, e descobriram que os padrões diferem. O full fine-tuning tende a fazer mudanças de direção relativamente grandes com mudanças de magnitude comparativamente modestas, e mostra uma relação distintiva entre as duas. As atualizações do LoRA movem magnitude e direção juntas de um modo mais acoplado, porque um único termo aditivo de baixo rank muda as duas ao mesmo tempo e não tem como ajustá-las de forma independente.

A hipótese: esse acoplamento é uma limitação, e desacoplar as duas deveria dar ao LoRA um comportamento de aprendizado mais próximo do full fine-tuning.

### O método

Decomponha a `W₀` congelada em sua magnitude e direção. Depois:

- Torne o **vetor de magnitude `m` treinável diretamente.** É um escalar por coluna, então `d_out` parâmetros, desprezível.
- Aplique a **atualização de baixo rank à direção** e renormalize depois.

```text
W' = m · (W₀ + BA) / ‖W₀ + BA‖_c
```

Leia isso com cuidado, porque é onde as descrições erram. `BA` é somada ao peso e depois o resultado é **renormalizado para colunas unitárias**, o que retira qualquer mudança de magnitude que `BA` tenha introduzido. A magnitude é então fornecida de forma separada e explícita pelo `m` treinável.

Assim `BA` já não consegue mudar a magnitude nem por acidente, pois só orienta a direção, e `m` cuida da escala. Esse é o desacoplamento, e é a contribuição inteira.

![Uma coluna de uma matriz de pesos como um vetor a partir de uma origem, com um quarto de círculo pontilhado marcando a norma unitária. À esquerda, W0 mais BA cai em algum lugar com um ângulo diferente e um comprimento diferente. À direita, só o ângulo sobrevive: a direção fica no círculo unitário e m define o comprimento, aqui de volta ao de W0.](images/length-and-angle.svg)

Os dois painéis usam a mesma `W0` e a mesma `BA`. À esquerda, um termo moveu as duas grandezas ao mesmo tempo; à direita, o ângulo é tudo o que `BA` contribuiu, e o comprimento é o que `m` disser que é.

### O que ele custa

**Parâmetros:** um vetor extra por camada adaptada, de comprimento `d_out`. Para uma camada de largura 4096 são 4096 números contra os 131,072 de um adapter de rank 16. Essencialmente de graça.

**Computação:** não é de graça. A norma por coluna de `W₀ + BA` precisa ser calculada, e ela depende de `BA`, então muda a cada passo e não pode ser guardada em cache entre atualizações. Isso torna o DoRA mensuravelmente mais lento por passo do que o LoRA, em geral na ordem de dezenas de por cento, variando conforme a implementação e quanto do trabalho a biblioteca consegue fundir ou guardar em cache.

**Complexidade:** o merge é mais envolvido. O peso com merge é `m · (W₀ + BA)/‖W₀ + BA‖_c`, ainda uma matriz comum, então um DoRA com merge é exato e tem zero de overhead de inferência, exatamente como o LoRA. Mas a aritmética para chegar lá não é uma simples soma, e a implementação importa.

### Usando

No PEFT, o DoRA é uma flag na configuração do LoRA, e não um método separado:

```text
config := {
    use_dora: true,
    rank: 8,
    alpha: 32,
    target_modules: "all-linear",
    dropout: 0.05,
    adapt_bias: false,
}
```

Tudo o que você sabe sobre rank, alpha, target modules e learning rate vale aqui. É uma modificação de como a atualização é aplicada, e não um novo conjunto de decisões. Confirme o nome da flag na versão instalada, como sempre.

O DoRA também se compõe com a quantização: um base quantizado mais um adapter DoRA, às vezes chamado de QDoRA. A interação merece ser medida em vez de presumida: a renormalização agora opera sobre pesos desquantizados que carregam erro de quantização, o que não é obviamente inofensivo.

### O resumo honesto

O DoRA é um refinamento bem motivado, com um mecanismo claro, ganhos relatados concentrados em rank baixo e um custo real de velocidade. Não é um substituto do LoRA e não é um efeito grande em toda configuração. A Lição 19 trata de prever quando ele se paga.

## Prática

1. ▢ Escreva a fórmula do DoRA e identifique cada grandeza treinável.

<details markdown="1"><summary>Verificação</summary>

`W' = m · (W₀ + BA) / ‖W₀ + BA‖_c`.

Treináveis: o vetor de magnitude `m`, mais `A` e `B`. Congelada: `W₀`.

</details>

2. ▢ O que a renormalização realiza?

<details markdown="1"><summary>Verificação</summary>

Ela remove qualquer mudança de magnitude que `BA` tenha introduzido, deixando `BA` capaz de afetar apenas a direção. A magnitude é então definida de forma explícita pelo `m` treinável.

Essa separação é o desacoplamento que dá nome ao método.

</details>

3. ▢ Por que o DoRA é mais lento do que o LoRA apesar de adicionar quase nenhum parâmetro?

<details markdown="1"><summary>Verificação</summary>

A norma por coluna de `W₀ + BA` precisa ser calculada, e como depende de `BA` ela muda a cada passo e não pode ser guardada em cache entre atualizações. Os parâmetros extras são desprezíveis; a aritmética extra não é.

</details>

4. ▢ Quantos parâmetros extras o DoRA adiciona a uma camada 4096 × 4096, e como isso se compara a um LoRA de rank 16 ali?

<details markdown="1"><summary>Verificação</summary>

4096, um escalar de magnitude por coluna de saída.

O LoRA de rank 16 nessa camada tem 16 × (4096 + 4096) = 131,072. Então o acréscimo do DoRA é cerca de 3% por cima, e esse não é o motivo para hesitar. O tempo por passo é.

</details>

5. ▢ Um DoRA com merge tem overhead de inferência?

<details markdown="1"><summary>Verificação</summary>

Não. O resultado com merge `m · (W₀ + BA)/‖W₀ + BA‖_c` é uma matriz de pesos comum, então um DoRA com merge é indistinguível de qualquer outro modelo na inferência.

A aritmética para produzi-lo é mais envolvida do que a simples soma do LoRA, mas o produto é o mesmo tipo de coisa.

</details>

6. ▢ Qual afirmação descreve corretamente o DoRA?

    - a) Ele adiciona uma segunda atualização de baixo rank ao termo de magnitude
    - b) Ele treina a magnitude diretamente e atualiza a direção com baixo rank
    - c) Ele substitui a atualização de baixo rank por uma escala de rank completo
    - d) Ele normaliza os gradientes em vez da matriz de pesos

<details markdown="1"><summary>Verificação</summary>

**b)** Ele treina a magnitude diretamente e atualiza a direção com baixo rank.

Não há um segundo fator de baixo rank. A atualização não é de rank completo. A normalização é aplicada ao peso, e não aos gradientes.

</details>

## Prática no mundo real

- [ ] Implemente a decomposição à mão: pegue qualquer matriz de pesos, calcule as normas por coluna, divida em `m` e `V` de norma unitária, e verifique que `m · V` a reconstrói.
- [ ] Treine a mesma configuração com `use_dora=True` e `False`. Registre os segundos por passo das duas e calcule o overhead.
- [ ] Amanhã: leia a seção 4 do artigo do DoRA, onde é apresentada a análise de magnitude e direção do full fine-tuning versus o LoRA. Essa análise é o argumento.

## Para ir além

- [Artigo científico: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Lição 19. Quando o DoRA vence, e quando não](0019-when-dora-wins.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
