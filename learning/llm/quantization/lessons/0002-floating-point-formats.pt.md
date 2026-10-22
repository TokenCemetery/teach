---
title: "2. Formatos de ponto flutuante"
description: "Como os bits de sinal, expoente e mantissa dividem faixa e precisão em fp32, fp16 e bf16"
type: lesson
---

# Lição 2. Formatos de ponto flutuante

**Ligação com a missão:** Todo formato numérico mais adiante nesta trilha é uma escolha de como dividir alguns bits entre faixa e precisão, então você precisa ler um layout de bits e dizer o que ele consegue e não consegue guardar antes de poder julgar o que um modelo quantizado perdeu.
**Fonte principal:** [Artigo científico: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
**Pré-requisitos:** [Lição 1](0001-what-quantization-buys.md), [Bits de expoente](../GLOSSARY.md), [Bits de mantissa](../GLOSSARY.md)

## Aquecimento

1. ▢ Quantos bytes por parâmetro usam fp32, bf16 e int8, e quanta memória os pesos de um modelo de 7B parâmetros ocupam em cada um?

<details markdown="1"><summary>Verificação</summary>

O fp32 usa 4 bytes (28 GB), o bf16 usa 2 bytes (14 GB) e o int8 usa 1 byte (7 GB). Só os pesos, na largura em bits nominal.

</details>

2. ▢ Por que um formato de pesos menor costuma deixar o decode com batch 1 mais rápido?

<details markdown="1"><summary>Verificação</summary>

O decode com batch size 1 é limitado pela largura de banda de memória: cada peso é lido uma vez por token e usado para pouca aritmética, então menos bytes por peso significam menos a ler. A quantização somente de pesos não deixa a aritmética em si mais rápida.

</details>

## Saiba isto

### Três campos

Um número de ponto flutuante armazena um bit de sinal, alguns **bits de expoente** e alguns **bits de mantissa**. Para um valor normal, o campo do expoente `e` e o campo da mantissa `m` dão

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

onde `M` é o número de bits de mantissa e `bias` é um deslocamento fixo que permite ao expoente ser negativo. O expoente escolhe junto de qual potência de dois o valor fica. A mantissa escolhe um entre 2^M pontos igualmente espaçados entre essa potência de dois e a seguinte. Um campo de expoente todo em zeros é reservado para o zero e para os valores subnormais, que são menores que o menor valor normal e preenchem a lacuna até o zero com o mesmo espaçamento. Um campo de expoente todo em uns é reservado, nos formatos IEEE, para o infinito e o NaN.

| Formato | Total de bits | Sinal / expoente / mantissa | Bias | Maior finito | Menor normal | Epsilon de máquina |
|---|---|---|---|---|---|---|
| fp32 | 32 | 1 / 8 / 23 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-23, cerca de 1.2 × 10^-7 |
| fp16 | 16 | 1 / 5 / 10 | 15 | 65.504 | 6.1 × 10^-5 | 2^-10, cerca de 9.8 × 10^-4 |
| bf16 | 16 | 1 / 8 / 7 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-7, cerca de 7.8 × 10^-3 |

O 65.504 é o valor que Micikevicius et al. dão como o maior que o fp16 consegue representar ([Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)). O resto decorre dos layouts. O **epsilon de máquina** é a distância entre 1 e o próximo valor acima dele, que é 2^-M.

Duas consequências importam para o resto da trilha. Primeiro, fp16 e bf16 ocupam ambos 2 bytes, então escolher entre eles não muda nada na memória. É uma escolha entre três bits a mais de mantissa e três bits a mais de expoente. Segundo, o bf16 é o fp32 com os 16 bits de baixo removidos: os mesmos campos de sinal e expoente e os 7 bits de mantissa de cima. Kalamkar et al. dão isso como o motivo de o bf16 ser atraente: a sua faixa é a mesma do fp32 e a conversão de e para fp32 é simples.

### Faixa e precisão são coisas diferentes

O expoente define a **faixa**, o intervalo do menor ao maior valor. A mantissa define a **precisão**, o quão de perto o formato consegue aproximar um valor dentro desse intervalo. Elas são independentes, e cada bit a mais em uma é um bit tirado da outra.

O espaçamento não é constante. Entre 2^k e 2^(k+1), os valores vizinhos ficam a 2^(k-M) de distância, então a distância dobra a cada potência de dois enquanto a distância relativa continua em cerca de 2^-M. No fp16, valores logo acima de 1 ficam a cerca de 0.001 de distância, valores logo acima de 1024 ficam exatamente a 1 de distância e logo acima de 2048 ficam a 2. Duas coisas decorrem disso. Uma soma cujo resultado cai mais perto de um valor existente do que de um ponto médio é arredondada de volta, então `1 + 0.0004` em fp16 ainda é 1, e uma soma corrente de uns em fp16 para de crescer em 2048. E um valor arredondado erra por no máximo metade do espaçamento local, o **erro de arredondamento** que a quantização sempre acrescenta.

### Por que o fp16 precisou de loss scaling e o bf16 não

Os 5 bits de expoente do fp16 o tornam estreito. O menor valor positivo que ele consegue armazenar é 2^-24, e qualquer coisa menor vira zero. Micikevicius et al. mediram valores de gradiente de uma execução de treinamento e descobriram que cerca de 5% dos valores de gradiente dos pesos tinham expoentes abaixo de -24, que seriam perdidos. A correção deles é o **loss scaling**: multiplicar a loss por uma constante antes da backpropagation, de modo que todo gradiente seja escalado para dentro da faixa do fp16, e dividir a scale antes da atualização dos pesos. Eles escolhem o fator de modo que o seu produto com o maior gradiente absoluto fique abaixo de 65.504, porque um overflow produz infinitos e NaNs que danificam os pesos.

O bf16 tem os 8 bits de expoente do fp32, então os mesmos gradientes são representáveis. Kalamkar et al. afirmam que manter a faixa do fp32 significa que nenhum ajuste de hiperparâmetros é necessário para a convergência, e que o fp16 exige isso. A emulação deles zera os 16 bits inferiores de um valor fp32, e eles comparam o round-to-nearest com o truncamento direto na conversão. Em um dos experimentos deles, o round-to-nearest igualou a acurácia do baseline fp32 enquanto o truncamento perdeu cerca de 0.02%. O preço do bf16 é a mantissa de 7 bits: os valores ficam a apenas cerca de 0.8% de distância em termos relativos.

Para esta trilha, a lição é a própria troca. Formatos quantizados de 8 bits ou menos fazem a mesma troca de forma muito mais dura, e é por isso que a lição 4 acrescenta uma scale.

## Prática

1. ▢ Qual afirmação compara corretamente fp16 e bf16?

    - a) o fp16 tem mais bits de expoente, portanto faixa mais larga
    - b) o bf16 tem mais bits de expoente, portanto faixa mais larga
    - c) o bf16 tem mais bits de mantissa, portanto espaçamento mais fino
    - d) fp16 e bf16 diferem no total de bits

<details markdown="1"><summary>Verificação</summary>

**b)** O bf16 gasta 8 bits no expoente contra os 5 do fp16, o que lhe dá a faixa do fp32, e tem 7 bits de mantissa contra os 10 do fp16. (a) tem os dois formatos trocados. (c) os troca no outro sentido: o fp16 é que tem o espaçamento mais fino. (d) está errada porque ambos têm 16 bits, então a memória não os separa.

</details>

2. ▢ Preveja e depois execute. O que cada linha imprime?

    ```python
    import numpy as np

    with np.errstate(over="ignore"):
        print(float(np.float16(65504)), float(np.float16(65519)))
        print(float(np.float16(65520)), float(np.float16(70000)))
    ```

<details markdown="1"><summary>Dica</summary>

65.504 é o maior valor finito do fp16, e o próximo valor acima seria 65.536. Onde fica o ponto médio, e para que lado arredonda um número acima dele?

</details>

<details markdown="1"><summary>Verificação</summary>

```text
65504.0 65504.0
inf inf
```

65.519 está abaixo do ponto médio entre 65.504 e 65.536, então arredonda para baixo, para 65.504. De 65.520 para cima o valor arredonda além do maior número finito e vira infinito, que é como um overflow de gradiente começa no treinamento. A linha do `errstate` apenas silencia o aviso do NumPy sobre isso.

</details>

3. ▢ Preveja e depois execute. Quais das três somas são exatamente iguais a 1?

    ```python
    import numpy as np

    one = np.float16(1)
    for d in (0.0004, 0.0005, 0.001):
        print(d, float(one + np.float16(d)))
    ```

<details markdown="1"><summary>Dica</summary>

A distância acima de 1 no fp16 é 2^-10, cerca de 0.000977. Uma soma vai para o vizinho mais próximo.

</details>

<details markdown="1"><summary>Verificação</summary>

```text
0.0004 1.0
0.0005 1.0009765625
0.001 1.0009765625
```

Só a primeira. Os vizinhos de 1 são 1 e 1.0009765625, e o ponto médio é cerca de 1.000488. O 0.0004 fica abaixo dele e se perde por inteiro, enquanto o 0.0005 salta um 2^-10 completo. Um valor somado a outro maior não fica "um pouco impreciso": abaixo de metade do espaçamento local ele desaparece.

</details>

4. ▢ Preveja e depois execute. O que isto imprime, e o que diz sobre somar muitos números pequenos em fp16?

    ```python
    import numpy as np

    total = np.float16(0)
    for _ in range(3000):
        total = total + np.float16(1)
    print(float(total))
    ```

<details markdown="1"><summary>Dica</summary>

Acima de 2048 o espaçamento do fp16 é 2. O que acontece com 2048 + 1?

</details>

<details markdown="1"><summary>Verificação</summary>

```text
2048.0
```

Em 2048 o espaçamento é 2, então 2049 fica exatamente a meio caminho entre dois valores representáveis e arredonda para o par, 2048. A soma então fica ali pelas 952 adições restantes. É por isso que Micikevicius et al. acumulam produtos fp16 em fp32 em vez de em fp16.

</details>

5. ▢ Preveja e depois execute. O bf16 é o fp32 com os 16 bits baixos removidos. Antes de executar, diga quais dos três primeiros valores sobrevivem inalterados à conversão e o que acontece com 1e38 em fp16.

    ```python
    import numpy as np

    def to_bf16(x):
        bits = np.asarray(x, dtype=np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
        return bits.view(np.float32)

    x = np.array([1 + 2**-7, 1 + 2**-8, 3.14159265, 1e38], dtype=np.float32)
    print([float(v) for v in to_bf16(x)])
    with np.errstate(over="ignore"):
        print(float(np.float16(1e38)))
    ```

<details markdown="1"><summary>Dica</summary>

O bf16 mantém 7 bits de mantissa, então 1 + 2^-7 é o primeiro valor acima de 1 que ele consegue guardar. Quanto é 1 + 2^-8?

</details>

<details markdown="1"><summary>Verificação</summary>

```text
[1.0078125, 1.0, 3.140625, 9.969209968386869e+37]
inf
```

1 + 2^-7 sobrevive, 1 + 2^-8 trunca para exatamente 1 e o pi vira 3.140625, correto até cerca de três dígitos. 1e38 continua finito, aproximadamente 9.97e37 porque a mantissa é cortada, mas o fp16 o transforma em infinito. Esta função trunca, como Kalamkar et al. descrevem a sua emulação fazendo, e eles a comparam com o arredondamento para o mais próximo.

</details>

6. ▢ Um colega treina em fp16 e vê a loss virar NaN depois de algumas centenas de passos, e propõe trocar para bf16. Explique o que provavelmente está acontecendo, o que o loss scaling faz a respeito e o que o bf16 mudaria.

<details markdown="1"><summary>Verificação</summary>

O fp16 tem o teto em 65.504, então uma loss escalada ou um gradiente grande podem dar overflow para infinito e NaN, e gradientes pequenos abaixo de 2^-24 viram zero. O loss scaling escolhe uma constante para que os gradientes caiam dentro da faixa do fp16, e a scale é dividida antes da atualização dos pesos. O bf16 tem a faixa de expoente do fp32, então nenhum dos dois problemas surge e nenhuma scale é necessária, ao custo de uma mantissa mais grosseira. Trocar é uma correção sólida só se o NaN for mesmo um problema de faixa. Um NaN causado por uma learning rate ruim ou por um batch ruim sobrevive à troca.

</details>

## Prática no mundo real

- [ ] Em uma sessão de Python com NumPy, imprima `np.finfo(np.float16)` e `np.finfo(np.float32)` e encontre `max`, `tiny` e `eps` neles. Compare cada um com a tabela acima.
- [ ] Abra o `config.json` de qualquer modelo aberto no Hugging Face Hub e leia o seu `torch_dtype`. Diga que faixa e que espaçamento essa escolha implica.
- [ ] Amanhã: sem consultar anotações, escreva as contagens de bits de sinal, expoente e mantissa de fp32, fp16 e bf16, e diga qual dos três tem a faixa mais larga e qual tem o espaçamento mais fino.

## Para ir além

- [Formatos Numéricos](../reference/number-formats.md)
- [Artigo científico: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
- [Artigo científico: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740), seções 3.1 e 3.2 para a cópia master dos pesos e o loss scaling
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
