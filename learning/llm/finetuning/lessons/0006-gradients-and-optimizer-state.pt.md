---
title: "6. Gradientes e estado do otimizador"
description: "Dezesseis bytes por parâmetro treinável, dois por parâmetro congelado"
type: lesson
---

# Lição 6. Gradientes e estado do otimizador

**Ligação com a missão:** Este é o argumento a favor dos adapters. Quando você consegue derivar o número de dezesseis bytes por parâmetro, o LoRA deixa de ser um truque e se torna a resposta óbvia.
**Fonte principal:** [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
**Pré-requisitos:** [Lição 4](0004-what-training-changes.md), [Lição 5](0005-counting-parameters-and-bytes.md)

## Aquecimento

1. ▢ Pesos de um modelo de 7B em bf16: quantos gigabytes?

<details markdown="1"><summary>Verificação</summary>

Cerca de 14 GB. Dois bytes por parâmetro, então os gigabytes em bf16 são aproximadamente o dobro dos bilhões de parâmetros.

</details>

2. ▢ Quais dois tensores o AdamW mantém por parâmetro treinável?

<details markdown="1"><summary>Verificação</summary>

Uma média móvel dos gradientes e uma média móvel dos gradientes ao quadrado, o primeiro e o segundo momentos. Cada um tem o formato do parâmetro.

</details>

3. ▢ Por que o bf16 vence o fp16 no treinamento?

<details markdown="1"><summary>Verificação</summary>

Sua faixa de expoente coincide com a do fp32, então os valores não estouram para infinito. O erro de arredondamento é sobrevivível; o `NaN` não é.

</details>

## Saiba isto

Tudo o que um parâmetro treinável custa, por parâmetro:

| Categoria | Treinamento em fp32 | Precisão mista (cálculo em bf16, master em fp32) |
|---|---|---|
| Pesos | 4 | 2 (bf16) + 4 (cópia master em fp32) |
| Gradientes | 4 | 2 |
| Primeiro momento do AdamW | 4 | 4 |
| Segundo momento do AdamW | 4 | 4 |
| **Total** | **16 bytes** | **16 bytes** |

![Duas barras de bytes por parâmetro treinável, ambas com dezesseis bytes de comprimento. Em fp32, os dezesseis bytes são quatro de cada: pesos, gradientes e dois momentos. Em precisão mista, os pesos são dois bytes de bf16 mais uma cópia master de quatro bytes, os gradientes são dois bytes, e os dois momentos continuam em quatro.](images/mixed-precision-same-total.svg)

A coluna da direita é a parte que surpreende as pessoas. **A precisão mista não reduz o total.**

As duas barras chegam à mesma marca, e esse é o achado inteiro. As duas peças em destaque são os tensores que de fato foram reduzidos à metade, quatro bytes economizados entre elas, e a cópia master ao lado da primeira são quatro bytes devolvidos de imediato. Tudo à direita dela nunca se moveu. A precisão mista reduz à metade os tensores de pesos e de gradientes e depois soma de volta uma cópia master dos pesos em fp32, porque acumular atualizações minúsculas em um valor bf16 as perde em silêncio. Os momentos do otimizador ficam em fp32 pelo mesmo motivo. O ganho da precisão mista é em throughput aritmético, não em memória.

Então: **16 bytes por parâmetro treinável**, antes de uma única ativação.

### O que isso significa

```text
1.5B trainable × 16 bytes = 24 GB
7B   trainable × 16 bytes = 112 GB
70B  trainable × 16 bytes = 1120 GB
```

Fazer full fine-tuning de um modelo de 7B precisa de 112 GB só de estado de otimizador e pesos, e depois as ativações por cima. Isso é território multi-GPU para um modelo cujos pesos têm 14 GB. A distância entre "o modelo cabe" e "treinar o modelo cabe" é um fator de oito, e é inteiramente gradientes e estado do otimizador.

### A saída

Olhe de novo a tabela e note pelo que os 16 bytes são multiplicados: o número de parâmetros **treináveis**, e não o total de parâmetros. Parâmetros congelados custam 2 bytes cada, pelos seus pesos, e nada mais. Sem gradiente. Sem momentos.

Esse é o argumento inteiro a favor dos adapters:

```text
frozen parameter   = 2 bytes  (bf16 weights only)
trainable parameter = 16 bytes (weights + master + grad + 2 moments)
```

Congele o base model, adicione alguns milhões de parâmetros treináveis, e o segundo termo quase desaparece. Calculado para um base de 7B com 4M de parâmetros de adapter treináveis:

```text
frozen base    7B  × 2  = 14.0 GB
trainable      4M  × 16 = 0.064 GB
```

O estado do otimizador do adapter é 64 MB. Ele virou um erro de arredondamento diante dos pesos do base, e os pesos do base são a única parte que você pode atacar separadamente, com quantização, na etapa 4.

### Medidas parciais, e por que não bastam

Antes de os adapters existirem, as pessoas reduziam esse custo de outras maneiras. Todas ainda estão disponíveis e todas continuam limitadas:

| Técnica | O que economiza | O que custa |
|---|---|---|
| Otimizador de 8 bits | Momentos em 1 byte em vez de 4: 16 → 10 bytes | Leve risco de qualidade; continua linear na contagem de treináveis |
| SGD com momentum | Um momento em vez de dois: 16 → 12 bytes | Convergência visivelmente pior para transformers |
| Sharding do otimizador (ZeRO) | Divide o estado entre N dispositivos | Precisa de N dispositivos e de uma interconexão rápida |
| Offload para a CPU | Tira o estado do acelerador | Limitado pela largura de banda; passos muito mais lentos |

Todas elas escalam a constante. Nenhuma muda o fato de que o custo é proporcional ao número de parâmetros treináveis. Os adapters atacam o multiplicador, e é por isso que ganham por ordens de grandeza e não por fatores.

### Por que os momentos não podem simplesmente ser descartados

Uma pergunta razoável: se os dois momentos do AdamW são dois terços do custo, por que não usar o SGD puro? Porque o treinamento de transformers depende da escala de passo por parâmetro do Adam. As magnitudes dos gradientes variam enormemente entre os parâmetros de um transformer, e um único learning rate global as atende mal. O segundo momento é o que permite a cada parâmetro dar um passo de tamanho apropriado. Isso é empírico, consistente, e não é um problema de ajuste que se possa desejar que desapareça.

## Prática

1. ▢ Derive a memória necessária para fazer full fine-tuning de um modelo de 3B com AdamW em precisão mista, excluindo as ativações.

<details markdown="1"><summary>Verificação</summary>

16 bytes por parâmetro treinável × 3e9 = 48 GB.

Detalhando: 6 GB de pesos em bf16 + 12 GB de master em fp32 + 6 GB de gradientes em bf16 + 12 GB do primeiro momento + 12 GB do segundo momento = 48 GB.

</details>

2. ▢ Por que a precisão mista não reduz a memória total de treinamento?

<details markdown="1"><summary>Verificação</summary>

Ela reduz à metade pesos e gradientes, mas adiciona uma cópia master dos pesos em fp32 e deixa os dois momentos do otimizador em fp32. A economia e o acréscimo se cancelam, voltando aos 16 bytes.

A cópia master não é opcional: somar repetidamente uma atualização muito pequena a um valor bf16 arredonda para nenhuma mudança, então a atualização se perde.

</details>

3. ▢ Um base de 7B está congelado em bf16 e você treina um adapter de 20M de parâmetros. Total, excluindo as ativações?

<details markdown="1"><summary>Verificação</summary>

14 GB para o base congelado (7e9 × 2) mais 0.32 GB para o adapter (2e7 × 16), então cerca de 14.3 GB.

Contra 112 GB do full fine-tuning: uma redução de 7.8×, e quase tudo o que sobra é o base congelado. A etapa 4 ataca esse resto.

</details>

4. ▢ Qual mudança reduz mais a memória do otimizador para um modelo fixo?

    - a) Trocar o otimizador de AdamW para SGD
    - b) Trocar a precisão de cálculo para bf16
    - c) Congelar o base e treinar um adapter
    - d) Passar para o mascaramento de loss apenas da completion

<details markdown="1"><summary>Verificação</summary>

**c)** Congelar o base e treinar um adapter.

(a) remove um momento de dois, economizando um quarto. (b) não economiza nada no total, como visto acima. (d) muda quais posições contribuem para a loss, e não quantos parâmetros têm estado. Só (c) ataca o número de parâmetros treináveis, que é o multiplicador de tudo.

</details>

5. ▢ Alguém propõe um otimizador de 8 bits para poder fazer full fine-tuning de um modelo de 70B em um único acelerador de 80 GB. Faça a aritmética e responda.

<details markdown="1"><summary>Verificação</summary>

Momentos de 8 bits dão 2 + 4 + 2 + 1 + 1 = 10 bytes por parâmetro. 70e9 × 10 = 700 GB. Ainda quase nove vezes um dispositivo de 80 GB, antes das ativações.

A técnica é real e útil; o plano erra por uma ordem de grandeza. Esse é o valor de fazer a aritmética antes do experimento.

</details>

6. ▢ Em uma frase: por que os parâmetros congelados custam tão menos do que os treináveis?

<details markdown="1"><summary>Verificação</summary>

Um parâmetro congelado só precisa que o seu próprio valor seja armazenado para o forward pass, enquanto um treinável precisa, além disso, de um gradiente, dois momentos do otimizador e uma cópia master de alta precisão: oito vezes mais.

</details>

## Prática no mundo real

- [ ] Monte de memória, no papel, a tabela dos 16 bytes. Depois calcule a memória total de treinamento para três tamanhos de modelo que realmente interessam a você.
- [ ] Carregue um modelo pequeno, execute um passo de treinamento com AdamW em todos os parâmetros e registre o pico de memória. Compare com a sua previsão.
- [ ] Amanhã: repita com o base congelado e só um adapter pequeno treinável. A razão que você medir é o argumento da etapa 3.

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054): a contabilidade canônica dessas categorias
- [Artigo científico: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Orçamento de memória](../reference/memory-budget.md)
- [Lição 8. A ideia de baixo rank](0008-the-low-rank-idea.md): a resposta a esta lição

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
