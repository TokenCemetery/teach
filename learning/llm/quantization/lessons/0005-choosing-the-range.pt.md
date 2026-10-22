---
title: "5. Escolhendo a faixa"
description: "Por que aplicar clipping à faixa troca um pouco de erro de clipping por muito menos erro de arredondamento"
type: lesson
---

# Lição 5. Escolhendo a faixa

**Ligação com a missão:** Prever de onde vem um erro de quantização significa saber qual das suas duas partes uma dada faixa de clipping torna grande, e a faixa é a escolha que move um erro para o outro.
**Fonte principal:** [Artigo científico: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), seção 3.1
**Pré-requisitos:** [Lição 4](0004-quantize-and-dequantize.md), [Faixa de clipping](../GLOSSARY.md), [Erro de clipping](../GLOSSARY.md), [Erro de arredondamento](../GLOSSARY.md)

## Aquecimento

1. ▢ Um quantizador afim de 4 bits cobre a faixa de -1 a 3. Quais são o seu passo e o seu maior erro de arredondamento?

<details markdown="1"><summary>Verificação</summary>

O passo é `s = 4 / 15 = 0.267` e o maior erro de arredondamento é `s/2 = 0.133`. A faixa é dividida em 2^4 - 1 = 15 passos, e um valor dentro da faixa se move no máximo meio passo.

</details>

2. ▢ Um valor fica fora dos limites da grade de um quantizador. O seu erro é limitado por `s/2`? Como o erro se chama?

<details markdown="1"><summary>Verificação</summary>

Não. O valor é limitado ao limite da grade mais próximo, e a distância que ele percorre é o **erro de clipping**, que não tem o limite de `s/2` e cresce com o quanto o valor fica fora da faixa.

</details>

3. ▢ Por que os quantizadores costumam combinar pesos simétricos com ativações assimétricas?

<details markdown="1"><summary>Verificação</summary>

Pesos assimétricos multiplicados por ativações assimétricas produzem um termo que depende dos dados de entrada, o que custa latência e energia em tempo de execução (Nagel et al., seção 2.4.1). Uma grade de pesos simétrica remove esse termo, então só as ativações mantêm o zero-point extra.

</details>

## Saiba isto

### Dois erros puxando em direções opostas

A **faixa de clipping** é o intervalo de valores reais que a grade de inteiros cobre, de `q_min` a `q_max`. Nagel et al. nomeiam toda a troca em uma frase da seção 2.2: ampliar a faixa reduz o erro de clipping, mas exige uma scale maior, e o erro de arredondamento, que fica entre -s/2 e s/2, cresce com ela.

| Faixa | Erro de clipping | Erro de arredondamento | O que dá errado |
|---|---|---|---|
| Estreita demais | Grande: os outliers são limitados | Pequeno | Os maiores valores são substituídos pela borda da faixa |
| Larga demais | Nenhum | Grande: o passo é grande | Valores típicos caem em poucos níveis ou arredondam para zero |

A seção 3.1 do artigo chama isso de a troca fundamental na definição da faixa e diz que cada método dá um equilíbrio diferente entre os dois erros. Os pesos são conhecidos de antemão, então a sua faixa normalmente não precisa de dados. A faixa de uma ativação depende da entrada, então Nagel et al. dizem que ela normalmente precisa de alguns batches de dados de calibração, que é o trabalho do [calibration set](../GLOSSARY.md).

### Os métodos

**Min-max.** Tome o menor e o maior valor como `q_min` e `q_max`. Isso não tem erro de clipping, e Nagel et al. alertam que é sensível a outliers, porque um outlier forte força um passo grande e, portanto, um erro de arredondamento excessivo. É o que a lição 4 usou.

**Erro quadrático médio.** Busque os `q_min` e `q_max` que minimizam o erro quadrático médio entre o tensor original e o quantizado. O artigo lista a busca em grade, o método da seção áurea e aproximações em forma fechada como maneiras de resolvê-lo, e diz que as variantes da literatura são todas muito parecidas. É o método a usar quando outliers inflam a faixa do min-max.

**Percentil.** Defina a faixa como um percentil alto dos valores absolutos, como o 99.9, de modo que uma fração fixa dos valores sofra clipping. Essa é uma heurística simples, não um dos métodos da seção 3.1, e o experimento abaixo a usa para você ver o que uma fração fixa custa e compra.

A seção 3.1 lista mais dois para casos especiais: minimizar a cross-entropy para os logits da camada final, onde a ordem dos maiores valores importa mais do que a dos muitos pequenos, e uma faixa baseada em batch normalization para as ativações. Esta trilha quantiza LLMs sem batch normalization, então usa os três primeiros.

Nagel et al. comparam os dois primeiros em classificadores do ImageNet na sua Tabela 1, com os pesos quantizados por tensor e as ativações deixadas em ponto flutuante. Para a ResNet18 em 8 bits, min-max e MSE ficam praticamente iguais: 69.57 contra 69.45 de acurácia top-1. Em 4 bits, o min-max cai para 0.12 e o MSE mantém 18.82. São modelos de visão, então leia a forma do resultado e não os números: com poucos níveis, a escolha da faixa decide se o modelo funciona ou não.

### O que o experimento mostra

O experimento da Prática quantiza um tensor de cauda pesada para 4 bits. O seu maior valor é 1.506 e o seu desvio padrão é 0.034, uma razão de cerca de 44. Com a faixa do min-max, o passo é `1.506 / 7 = 0.215`, metade dele é 0.108, que é mais de três desvios padrão, então quase todo valor arredonda para zero. Aplicar clipping aos 0.35 por cento dos valores que a busca por MSE corta reduz o erro cerca de seis vezes. A grade é gasta em uma faixa que quase nenhum valor visita.

### Por que isto não é a resposta completa para LLMs

O MSE conta o erro quadrático de cada valor igualmente. Nagel et al. fazem a mesma observação sobre logits: o MSE pode não servir para valores de importância desigual, porque pesa todos os valores igualmente. Em um LLM, os poucos maiores valores podem ser os importantes. [Dettmers et al.](https://arxiv.org/abs/2208.07339) relatam que zerar as dimensões de feature outlier degradou a perplexity de validação em 600 a 1000 por cento, embora elas componham cerca de 0.1 por cento das features. Uma faixa que as corta tem um efeito minúsculo no MSE do tensor e pode ter um efeito grande no modelo. A lição 7 explica de onde esses valores vêm, e a lição 8 dá as correções que não os cortam.

## Prática

1. ▢ Um quantizador simétrico com sinal de 4 bits com grade de -7 a 7 tem uma faixa min-max de 1.506 em um tensor com desvio padrão 0.034. Quanto é `s`, e quais valores arredondam para zero?

<details markdown="1"><summary>Verificação</summary>

`s = 1.506 / 7 = 0.215`. Qualquer valor com valor absoluto abaixo de `s/2 = 0.108` arredonda para o inteiro 0, que é mais de três desvios padrão. Para um tensor em forma de sino, isso é quase todo valor, então um máximo distante apagou o tensor.

</details>

2. ▢ Qual afirmação descreve ampliar a faixa de clipping?

    - a) O erro de clipping e o erro de arredondamento diminuem
    - b) O erro de clipping e o erro de arredondamento aumentam
    - c) O erro de clipping diminui enquanto o erro de arredondamento aumenta
    - d) O erro de clipping aumenta enquanto o erro de arredondamento diminui

<details markdown="1"><summary>Verificação</summary>

**c)** Uma faixa mais larga limita menos valores, então o erro de clipping diminui, mas o mesmo número de níveis agora cobre mais distância, então o passo e o erro de arredondamento crescem. (a) tornaria a escolha da faixa trivial, já que você sempre ampliaria. (b) erra os dois, já que ampliar não pode aumentar o erro de clipping. (d) descreve estreitar a faixa, não ampliá-la.

</details>

3. ▢ Preveja e depois execute. Isto quantiza 100.000 valores de cauda pesada para 4 bits sob quatro faixas. Antes de executar, preveja qual faixa tem o menor erro quadrático médio e se o min-max arredonda mais ou menos da metade de todos os valores para zero.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.standard_t(df=3, size=100_000) * 0.02   # heavy-tailed
    qmax = 7                                        # 4-bit signed symmetric grid: -7..7 times the scale


    def quantize(x, c):
        s = c / qmax
        return s * np.clip(np.round(x / s), -qmax, qmax)


    def mse(x, c):
        return np.mean((quantize(x, c) - x) ** 2)


    grid = np.linspace(0.01, np.abs(x).max(), 400)
    ranges = {
        "min-max": np.abs(x).max(),
        "p99.9": np.percentile(np.abs(x), 99.9),
        "p99": np.percentile(np.abs(x), 99),
        "MSE search": grid[np.argmin([mse(x, c) for c in grid])],
    }
    print("max |x| =", round(np.abs(x).max(), 3), " std =", round(x.std(), 3))
    for name, c in ranges.items():
        q = quantize(x, c)
        print(f"{name:10s} c={c:.3f}  mse={mse(x, c):.2e}  clipped={np.mean(np.abs(x) > c):6.2%}  rounded to zero={np.mean(q == 0):6.2%}")
    ```

<details markdown="1"><summary>Dica</summary>

Calcule primeiro o passo do min-max, como no item 1, e compare metade dele com o desvio padrão.

</details>

<details markdown="1"><summary>Verificação</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=8.15e-04  clipped= 0.00%  rounded to zero=98.72%
p99.9      c=0.252  mse=1.61e-04  clipped= 0.10%  rounded to zero=56.61%
p99        c=0.117  mse=1.53e-04  clipped= 1.00%  rounded to zero=29.40%
MSE search c=0.171  mse=1.35e-04  clipped= 0.35%  rounded to zero=41.52%
```

A busca por MSE vence, e o min-max é o pior, cerca de seis vezes mais alto, com 98.7 por cento dos valores arredondados para zero. Aplicar clipping a apenas 0.10 por cento dos valores (p99.9) já reduz o erro cinco vezes. Aplicar clipping a 1 por cento (p99) é ligeiramente pior que a busca (1.53e-04 contra 1.35e-04), porque os valores cortados agora custam mais do que o arredondamento economizou: a melhor faixa fica entre os extremos.

</details>

4. ▢ Preveja e depois execute. Troque `qmax = 7` por `qmax = 127`, o que a transforma em uma grade de 8 bits, e execute de novo. O clipping ainda vai vencer? Que faixa a busca por MSE escolhe agora?

<details markdown="1"><summary>Verificação</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=1.17e-05  clipped= 0.00%  rounded to zero=21.23%
p99.9      c=0.252  mse=5.51e-05  clipped= 0.10%  rounded to zero= 3.65%
p99        c=0.117  mse=1.30e-04  clipped= 1.00%  rounded to zero= 1.69%
MSE search c=1.019  mse=7.72e-06  clipped= 0.00%  rounded to zero=14.52%
```

O clipping não vence mais: o min-max supera as duas faixas por percentil, e a busca por MSE escolhe 1.019, perto da faixa inteira, com menos de 0.005 por cento dos valores cortados. Com 127 níveis por lado, o passo é pequeno o bastante para que os outliers custem pouco erro de arredondamento, enquanto cortá-los custa muito. É a mesma forma da Tabela 1 de Nagel et al., em que min-max e MSE ficam iguais em 8 bits: quanto menos níveis, mais uma faixa apertada compensa.

</details>

5. ▢ Uma equipe define a faixa de cada ativação de um LLM minimizando o MSE, e a perplexity dispara. Use esta lição para dar o mecanismo mais provável e diga o que o MSE não conseguiu ver.

<details markdown="1"><summary>Verificação</summary>

A faixa cortou as features outliers. Elas são uma fatia minúscula dos valores, então limitá-las muda muito pouco o MSE do tensor, mas elas importam muito mais do que o seu número: Dettmers et al. mediram uma perplexity 600 a 1000 por cento mais alta quando essas dimensões foram zeradas. O MSE pesa todo valor igualmente, e Nagel et al. observam que esse é o peso errado quando os valores diferem em importância. O objetivo de definição da faixa é um proxy local da loss da tarefa, e aqui ele aponta para o lado errado. Manter os outliers fora do conjunto cortado é o assunto da lição 8.

</details>

## Prática no mundo real

- [ ] Execute o experimento de novo com `df=10` e depois com `rng.normal` no lugar de `standard_t`. Registre o melhor clip da busca por MSE como um múltiplo do desvio padrão a cada vez e observe como ele se move conforme as caudas ficam mais leves.
- [ ] Pegue uma matriz de pesos de um modelo aberto pequeno e imprima o seu valor absoluto máximo junto com os percentis 99 e 99.9 do valor absoluto. Decida se o min-max desperdiçaria a maior parte de uma grade de 4 bits nela.
- [ ] Amanhã: sem consultar anotações, diga o que min-max, MSE e percentil otimizam cada um, e qual largura em bits faz a escolha importar mais. Depois releia a seção 3.1 e confira se você nomeou a troca certa.

## Para ir além

- [O Mapeamento de Quantização](../reference/quantization-mapping.md)
- [Artigo científico: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Artigo científico: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339), seção 4.2, para saber por que aplicar clipping a outliers é perigoso
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
