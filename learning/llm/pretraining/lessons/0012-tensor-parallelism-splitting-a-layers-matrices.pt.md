---
title: "12. Paralelismo de tensor: dividindo as matrizes de uma camada"
description: "Escolher ao longo de qual eixo dividir uma matriz de pesos para que um bloco transformer inteiro precise de apenas um all-reduce"
type: lesson
---

# Lição 12. Paralelismo de tensor: dividindo as matrizes de uma camada

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. Esta lição cobre o que o paralelismo de tensor de fato divide e por quê; a Lição 13 cobre o paralelismo de pipeline e a Lição 14 cobre quando um ou outro vale o seu custo.
**Fonte principal:** [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Pré-requisitos:** [Lição 11](0011-activation-memory-and-zero-r.md)

## Aquecimento

1. ▢ O estágio 3 do ZeRO particiona os parâmetros em repouso, mas reconstrói o tensor de parâmetros completo sob demanda antes do forward ou do backward pass de uma camada, por meio de all-gather. Cada dispositivo calcula a mesma camada completa depois que os parâmetros são reconstruídos, ou cada dispositivo calcula uma parte diferente da matemática da camada?

<details markdown="1"><summary>Verificação</summary>

Cada dispositivo calcula a mesma camada completa, usando a sua própria cópia completa reconstruída dos parâmetros dessa camada. O ZeRO particiona onde os parâmetros vivem em repouso; ele não divide o cálculo de nenhuma camada individual entre os dispositivos.

</details>

## Saiba isto

### Dividir a computação, e não só onde os pesos vivem

O **paralelismo de tensor** adota uma abordagem diferente de tudo o que há na etapa 5: em vez de reconstruir os pesos de uma camada completa em um único dispositivo, ele divide as matrizes de pesos de uma camada individual entre dispositivos, de modo que cada dispositivo só guarde, e só calcule com, a sua própria fatia da camada. Nenhum dispositivo precisa da matriz de pesos completa de uma vez.

### Um exemplo trabalhado: o bloco MLP

O bloco MLP de um transformer calcula `Y = GeLU(XA)` seguido de `Z = Dropout(YB)`, duas multiplicações de matrizes com uma não linearidade no meio. Narayanan et al. descrevem a forma específica como o Megatron divide isso para manter a comunicação no mínimo: dividir a primeira matriz de pesos `A` **ao longo das suas colunas**, `A = [A1, A2]`, dando a cada dispositivo uma fatia de saída completa e calculável de forma independente, `Y1 = GeLU(XA1)` e `Y2 = GeLU(XA2)`, sem nenhuma sincronização entre os dois dispositivos para calculá-las. Isso funciona porque dividir ao longo das colunas divide a dimensão de *saída*, e não a dimensão sobre a qual se soma, então a fatia de `Y` de cada dispositivo já é a resposta verdadeira e completa para as suas colunas, e a `GeLU`, aplicada elemento a elemento, pode ser aplicada a cada fatia completa de forma independente.

A segunda matriz de pesos, `B`, é então dividida **ao longo das suas linhas** para combinar, `B = [B1; B2]`, de modo que cada dispositivo calcule `Yi @ Bi` usando apenas a sua própria fatia local de `Y` e `B`. Isso dá a cada dispositivo uma soma parcial rumo à saída verdadeira `Z`; as somas parciais dos dois dispositivos são combinadas com um único all-reduce e só então o dropout se aplica ao resultado completo e correto.

### Por que coluna e depois linha, e não o contrário

Se `A` fosse dividida ao longo das suas linhas (dividindo a dimensão sobre a qual se soma, em vez da dimensão de saída), a fatia de `X @ A` de cada dispositivo seria apenas uma **soma parcial** rumo aos valores verdadeiros de pré-ativação, e não uma resposta completa, já que somar apenas sobre parte da dimensão de contração não dá os números certos para nenhuma coluna de saída. A `GeLU` não pode ser aplicada corretamente a uma soma parcial e depois combinada, porque a `GeLU` é não linear: `GeLU(a + b)` não é `GeLU(a) + GeLU(b)`. Dividir `A` por colunas evita ter de aplicar uma não linearidade a uma soma parcial para começo de conversa, que é exatamente a razão que Narayanan et al. dão para escolhê-lo. O par coluna e depois linha é o que permite que o bloco MLP de duas matrizes inteiro precise de **um** só all-reduce, bem no final, em vez de também uma etapa de sincronização entre as duas multiplicações de matrizes.

### O mesmo padrão se aplica à atenção

A atenção multi-head já tem um lugar natural para dividir: as projeções de query, key e value são particionadas em paralelo por colunas, de modo que cada dispositivo trate de um subconjunto de cabeças de atenção de forma independente, sem coordenação entre dispositivos durante o próprio cálculo de atenção. A projeção de saída que vem a seguir é então dividida ao longo das suas linhas para combinar, o mesmo par coluna e depois linha do bloco MLP, precisando de um all-reduce no final do bloco de atenção.

## Prática

1. ▢ O bloco MLP de um transformer é dividido com `A` ao longo das colunas e `B` ao longo das linhas, como esta lição descreve. Quantas operações de all-reduce esse esquema precisa para o bloco inteiro, de `X` até o `Z` final?

<details markdown="1"><summary>Verificação</summary>

Uma, logo depois da segunda multiplicação de matrizes, para combinar a soma parcial de `Z` de cada dispositivo no resultado completo. A divisão de `A` por colunas evita precisar de qualquer sincronização entre as duas multiplicações de matrizes.

</details>

2. ▢ Se `A` fosse dividida ao longo das linhas em vez das colunas, o que daria errado ao aplicar a `GeLU` imediatamente depois da primeira multiplicação de matrizes?

<details markdown="1"><summary>Dica</summary>

Pergunte o que o resultado local de cada dispositivo de fato representa quando a dimensão sobre a qual se soma é a que foi dividida, e não a dimensão de saída.

</details>

<details markdown="1"><summary>Verificação</summary>

Cada dispositivo guardaria apenas uma soma parcial rumo aos valores verdadeiros de pré-ativação, e não os valores completos, já que apenas parte da dimensão de contração foi incluída no cálculo local de cada dispositivo. A `GeLU` é não linear, então aplicá-la a uma soma parcial e depois combinar os resultados não dá a mesma resposta que aplicá-la à soma completa, o que significa que uma etapa de sincronização seria necessária antes de a `GeLU` poder rodar corretamente.

</details>

3. ▢ No bloco de atenção, como as projeções de query, key e value são divididas e que característica natural da atenção multi-head torna essa divisão conveniente?

<details markdown="1"><summary>Verificação</summary>

Elas são divididas em paralelo por colunas, do mesmo jeito que `A` é dividida no bloco MLP. A atenção multi-head já calcula a atenção de cada cabeça independentemente das outras, então atribuir cabeças diferentes (ou grupos de cabeças) a dispositivos diferentes não exige coordenação durante o próprio cálculo de atenção, do mesmo jeito que dividir a dimensão de saída do MLP não exigia.

</details>

4. ▢ Por que o paralelismo de tensor, como esta lição o descreve, nunca precisa reconstruir a matriz de pesos completa de uma camada em um único dispositivo, ao contrário do estágio 3 do ZeRO?

<details markdown="1"><summary>Verificação</summary>

Porque cada dispositivo só calcula com a sua própria fatia da matriz de pesos; a divisão coluna e depois linha é escolhida justamente para que todo cálculo intermediário em cada dispositivo seja ou um resultado completo e independente (depois da divisão por colunas) ou uma soma parcial combinada por um all-reduce (depois da divisão por linhas), sem exigir que a matriz completa exista em lugar nenhum.

</details>

## Prática no mundo real

- [ ] Leia a descrição do paralelismo de tensor no artigo do Megatron-LM (linkado acima) e encontre a figura que mostra as divisões dos blocos MLP e de atenção. Acompanhe, com as suas próprias palavras, onde fica cada operador `f` e `g` (a notação do artigo para o par identidade versus all-reduce do forward e do backward) no diagrama.
- [ ] Esboce, no papel, uma matriz de pesos `A` de 4 linhas por 2 colunas e uma entrada `X` de 2 linhas por 4 colunas e calcule à mão como fica `X @ A` quando `A` é dividida por colunas em dois pedaços de 4 linhas por 1 coluna, versus dividida por linhas em dois pedaços de 2 linhas por 2 colunas. Confirme qual divisão dá a cada dispositivo uma resposta completa.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 13: se o paralelismo de tensor precisa de um all-reduce para cada camada do transformer, que tipo de interconexão isso provavelmente exigiria entre os dispositivos e você esperaria que ela funcionasse igualmente bem entre dispositivos em racks de servidores fisicamente diferentes?

## Para ir além

- [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
