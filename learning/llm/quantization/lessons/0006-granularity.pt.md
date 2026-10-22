---
title: "6. Granularidade"
description: "Scales per-tensor, per-channel e per-group, e o que cada uma custa em bits armazenados"
type: lesson
---

# Lição 6. Granularidade

**Ligação com a missão:** Prever o erro de um tensor quantizado também significa saber quantos valores compartilham cada scale, porque uma scale é definida pelo maior valor do seu grupo e cada scale extra custa bits armazenados.
**Fonte principal:** [Artigo científico: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), seções 2.2.3 e 2.4.2
**Pré-requisitos:** [Lição 5](0005-choosing-the-range.md), [Granularidade](../GLOSSARY.md), [Tamanho do grupo](../GLOSSARY.md), [Bits efetivos por peso](../GLOSSARY.md)

## Aquecimento

1. ▢ Com a definição de faixa por min-max, o que decide a scale de um quantizador, e o que um outlier faz com ela?

<details markdown="1"><summary>Verificação</summary>

A faixa, definida pelos maiores e menores valores, dividida pelo número de passos. Um outlier alarga a faixa, então a scale cresce e o passo fica mais grosseiro para todos os outros valores, o que pode arredondar a maioria deles para zero (lição 5).

</details>

2. ▢ Um esquema de 4 bits armazena uma scale de 16 bits por grupo de 32 pesos. Quais são os seus bits efetivos por peso?

<details markdown="1"><summary>Verificação</summary>

4.5. A scale acrescenta 16 / 32 = 0.5 bit por peso aos 4 bits de cada valor (lição 1).

</details>

3. ▢ Por que uma grade simétrica precisa só de uma scale, e qual é o custo de abrir mão do zero-point?

<details markdown="1"><summary>Verificação</summary>

A quantização simétrica fixa o zero-point em zero, então não há mais nada a armazenar. O custo é que a grade fica centrada no zero, então um tensor de um só lado desperdiça os níveis do lado vazio (lição 4).

</details>

## Saiba isto

### O que compartilha uma scale

A **granularidade** é quantos valores compartilham uma scale e um zero-point. Um pequeno conjunto que compartilha a scale significa uma faixa pequena, então um outlier só arruína o conjunto em que está. O custo é que cada conjunto precisa da sua própria scale armazenada.

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel et al. observam que a quantização per-tensor é padrão porque todo acelerador de ponto fixo a suporta, e que a quantização per-channel dos pesos ajuda mais quando a distribuição dos pesos varia muito de canal para canal. Eles também descrevem aplicar um quantizador por grupo de pesos ou de ativações e dizem que grupos mais finos geralmente melhoram a acurácia ao custo de overhead extra.

### Por que per-channel funciona para pesos e não para ativações

Uma camada linear calcula cada saída como uma soma sobre as features de entrada. Com os valores quantizados escritos como scale vezes inteiro, as scales só podem sair da soma se forem constantes ao longo dela:

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

O parêntese é um produto escalar puramente de inteiros, que é o que o hardware acelera, e as duas scales multiplicam o resultado uma única vez no final. Uma scale de pesos por canal de saída `s_w[i]` é constante ao longo da soma, porque `i` nomeia a saída e `k` é somado. Nagel et al. concluem que a quantização per-channel dos pesos pode ser aplicada com uma scale por canal separada, sem reescalar o acumulador.

Uma scale de ativação por canal de entrada seria `s_x[k]`, que muda com o índice somado. Ela não consegue sair da soma, e Nagel et al. dizem que ela "exigiria, portanto, reescalar o acumulador para cada canal de entrada". A quantização per-channel das ativações é muito mais difícil de implementar por esse motivo. Uma scale de ativação per-token, uma por linha de `X`, é constante ao longo da soma para um dado token e não custa nada: [Dettmers et al.](https://arxiv.org/abs/2208.07339) usam exatamente isso na sua quantização vector-wise, uma constante por linha das ativações e uma por coluna dos pesos, e desfazem ambas com o produto externo das constantes. A lição 7 mostra por que isso não basta para LLMs: os outliers ficam nas dimensões de feature, que é o eixo que uma scale per-token não separa.

A quantização per-group tem o mesmo problema para o acumulador de inteiros, já que a scale muda dentro da soma. O limite do acumulador no artigo é o motivo pelo qual Nagel et al. deixam as scales de grupo de fora. Nos esquemas somente de pesos, os pesos são dequantizados para 16 bits dentro do kernel e multiplicados em 16 bits (veja [quantização somente de pesos](../GLOSSARY.md)), então nenhum acumulador de inteiros carrega scales misturadas e uma scale de grupo pode variar livremente.

### O que as scales custam

Cada grupo acrescenta a sua scale, e qualquer zero-point, ao checkpoint. Os **bits efetivos por peso** são a largura em bits do valor mais os metadados divididos pelo grupo:

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| Tamanho do grupo | Overhead com uma scale de 16 bits | Bits efetivos para pesos de 4 bits |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

Per-channel é só um grupo cujo tamanho é o comprimento da linha, e per-tensor é um grupo de todos os pesos: ambos custam quase nada. O número da lição 1 para o grupo 32 é a última linha.

### O que grupos pequenos oferecem

O experimento da Prática quantiza uma matriz de pesos sintética em 4 bits, com linhas de scales diferentes e caudas pesadas. O erro cai de forma constante conforme os grupos diminuem, e o per-tensor é de longe o pior. Um grupo de 64 tem apenas 64 chances de conter um outlier, e o outlier afeta só esses 64 valores.

O maior estudo empírico sobre isso é o de [Dettmers e Zettlemoyer](https://arxiv.org/abs/2212.09720): mais de 35.000 experimentos zero-shot com 3 a 8 bits em LLMs de 19M a 176B de parâmetros. Eles acham difícil melhorar de algum modo a troca entre o tamanho do modelo em bits e a acurácia, com apenas duas coisas ajudando: um tamanho de bloco pequeno (o termo deles para tamanho do grupo) e o tipo de dado. Para os modelos Pythia de 4 bits, ir de um tamanho de bloco de 1024 para 64 acrescenta 0.24 bit por parâmetro e melhora a acurácia zero-shot quase tanto quanto ir de 4 para 5 bits. Uma constante de 16 bits por bloco custa 16 / 64 - 16 / 1024 = 0.23 bit, próximo do número do artigo. Grupos pequenos são os bits baratos.

## Prática

1. ▢ Um esquema de 4 bits armazena uma scale de 16 bits e um zero-point de 4 bits por grupo de 64 pesos. Quais são os seus bits efetivos por peso?

<details markdown="1"><summary>Verificação</summary>

4 + (16 + 4) / 64 = 4.3125, cerca de 4.31. O zero-point acrescenta 4 / 64 = 0.0625 além dos 0.25 da scale. Um esquema simétrico abriria mão desses 0.0625 e cairia em 4.25.

</details>

2. ▢ O que torna uma scale de pesos por canal de saída compatível com uma multiplicação de matrizes de inteiros enquanto uma scale de ativação por canal de entrada não é?

    - a) A scale dos pesos cabe em apenas oito bits
    - b) A scale dos pesos precisa de um termo de offset separado
    - c) A scale dos pesos é constante ao longo da soma
    - d) A scale dos pesos muda de valor entre canais de saída

<details markdown="1"><summary>Verificação</summary>

**c)** A scale da saída `i` multiplica a soma inteira sobre `k`, então sai da soma e é aplicada uma única vez depois da acumulação de inteiros. Uma scale de ativação indexada por canal de entrada muda dentro da soma, então o acumulador precisaria ser reescalado a cada canal de entrada. (a) trata de armazenamento e não decide onde uma scale pode ser aplicada. (b) confunde uma scale com um zero-point, e pesos simétricos não precisam de nenhum. (d) é verdade, mas é o motivo de haver muitas scales, não o motivo de elas poderem ser colocadas em evidência.

</details>

3. ▢ Preveja e depois execute. Antes de executar, ordene per-tensor, per-channel e os tamanhos de grupo por erro, do pior ao melhor, e diga se o erro cai de forma constante. Depois calcule os bits efetivos para o grupo 32.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>Dica</summary>

Cada redução no tamanho do grupo significa mais scales, e cada scale é definida por um conjunto menor de valores. Depois pergunte o que uma scale per-tensor faz com uma matriz cujas linhas diferem em tamanho.

</details>

<details markdown="1"><summary>Verificação</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

O erro cai a cada passo: o per-tensor deixa um erro de cerca de 70 por cento do tamanho da energia do próprio sinal, o per-channel remove a maior parte disso dando a cada linha a sua própria scale, e cada divisão do grupo pela metade reduz o erro em cerca de um terço. O grupo 32 custa 4.5 bits efetivos. Os dados são sintéticos, então leia a ordem e as razões aproximadas, não os números absolutos.

</details>

4. ▢ Ir do tamanho de grupo 1024 para 64 acrescenta quantos bits por peso com uma scale de 16 bits? Compare com o custo de passar os pesos de 4 para 5 bits e diga o que Dettmers e Zettlemoyer descobriram sobre os benefícios.

<details markdown="1"><summary>Verificação</summary>

16 / 64 - 16 / 1024 = 0.234 bit, contra 1 bit inteiro para pesos de 5 bits. No artigo, o tamanho de bloco menor melhorou a acurácia zero-shot dos modelos Pythia de 4 bits quase tanto quanto o bit extra teria melhorado. Então diminuir o grupo é uma forma muito mais barata de comprar acurácia do que acrescentar um bit a cada peso. O resultado principal do artigo é que 4 bits é quase universalmente ótimo para o total de bits do modelo e a acurácia zero-shot.

</details>

5. ▢ Uma equipe quantiza as ativações para 8 bits com uma scale por token e ainda perde acurácia, porque uma dimensão de feature é enorme em todo token. Por que a scale per-token não ajuda, e qual eixo separaria o outlier?

<details markdown="1"><summary>Verificação</summary>

A scale de cada token é definida pelo maior valor daquele token, e a dimensão de feature enorme é a maior em quase todo token, então a scale de toda linha é inflada do mesmo jeito. Dettmers et al. fazem esse ponto: a quantização row-wise e vector-wise escalam a dimensão da sequência, e os outliers ficam na dimensão de feature, então ambas falham em isolá-los. Só uma scale por dimensão de feature separaria o outlier, e essa é a scale de ativação por canal de entrada desta lição, que uma multiplicação de matrizes de inteiros não consegue aplicar barato.

</details>

## Prática no mundo real

- [ ] No experimento, troque `0.7` em `rng.lognormal(0.0, 0.7, ...)` por `0.0`, de modo que toda linha tenha a mesma scale, e execute de novo. Registre quanto da vantagem do per-channel sobre o per-tensor permanece e explique.
- [ ] Abra o model card ou a configuração de qualquer checkpoint GPTQ ou AWQ de 4 bits no Hugging Face Hub, encontre o seu tamanho de grupo e calcule os seus bits efetivos por peso e o tamanho do checkpoint para a contagem de parâmetros do modelo.
- [ ] Amanhã: sem consultar anotações, refaça a tabela de tamanhos de grupo contra bits efetivos para uma scale de 16 bits e para uma scale de 8 bits, e diga em uma frase por que scales de pesos per-channel se ajustam a um matmul de inteiros e scales de ativação per-channel não.

## Para ir além

- [O Mapeamento de Quantização](../reference/quantization-mapping.md)
- [Artigo científico: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Artigo científico: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers e Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
