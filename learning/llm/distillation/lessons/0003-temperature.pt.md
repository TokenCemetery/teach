---
title: "3. Temperatura"
description: "Suavizar as duas distribuições com uma temperatura, a correção por T ao quadrado e misturar a loss do hard label"
type: lesson
---

# Lição 3. Temperatura

**Ligação com a missão:** A missão pede que você defina a temperatura e os pesos da loss de uma execução de destilação, e esta lição dá as três peças dessa definição: a temperatura, o fator T ao quadrado e o peso da loss do hard label.
**Fonte principal:** [Artigo científico: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals e Dean, 2015](https://arxiv.org/abs/1503.02531)
**Pré-requisitos:** [Lição 2](0002-soft-targets.md), [Temperatura](../GLOSSARY.md), [Loss combinada](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Aquecimento

1. ▢ Com temperatura 1, um aluno deu ao 2 a probabilidade 0,98 e ao 3 a probabilidade 0,01, e o professor deu a eles 1,0 e 10^-6. Por que o 3 mal mexeu na loss?

<details markdown="1"><summary>Verificação</summary>

Cada termo da cross-entropy é a probabilidade-alvo vezes o log da probabilidade do aluno. O alvo de 10^-6 do 3 faz o seu termo ser mais de 4.000 vezes menor que o do 2, então a informação nele está presente e quase não é ouvida.

</details>

2. ▢ O que um hard label diz sobre a similaridade de um 2 com um 7, e onde está essa informação em uma destilação?

<details markdown="1"><summary>Verificação</summary>

Não diz nada. A similaridade mora nas pequenas probabilidades que o [professor](../GLOSSARY.md) põe nas classes erradas, os [soft targets](../GLOSSARY.md).

</details>

## Saiba isto

### A temperatura

O artigo substitui o softmax por um que divide cada [logit](../GLOSSARY.md) por uma temperatura T antes de normalizar: q_i = exp(z_i / T) / sum_j exp(z_j / T). T normalmente é 1. Um T maior dá uma distribuição mais suave sobre as classes. A receita do artigo é elevar T até que o professor produza soft targets suficientemente suaves e então treinar o aluno com o mesmo T alto para igualá-los. Depois do treinamento, o aluno usa T = 1.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

logits = [9.0, 4.0, 2.0, 0.0, -4.0]   # classes: 2, 3, 7, 8, 0
np.set_printoptions(suppress=True, precision=4)
for T in (1, 2, 5, 20):
    print("T =", T, softmax(logits, T))
```

Preveja a probabilidade da primeira classe com T = 5 antes de rodar. A saída no NumPy 2.5:

```text
T = 1 [0.9923 0.0067 0.0009 0.0001 0.    ]
T = 2 [0.889  0.073  0.0268 0.0099 0.0013]
T = 5 [0.5394 0.1984 0.133  0.0892 0.0401]
T = 20 [0.2745 0.2138 0.1934 0.175  0.1433]
```

Com T = 1, as classes erradas somam menos de 1%. Com T = 5, elas carregam quase metade da probabilidade, e a ordem 3, 7, 8, 0 ainda é visível. Com T = 20, a distribuição é quase plana, e as diferenças que o aluno precisa igualar são pequenas.

### Por que a loss é multiplicada por T ao quadrado

O gradiente da cross-entropy em relação a um logit z_i do aluno, quando o professor tem logits v_i e ambos usam a temperatura T, é (1/T)(q_i - p_i). A equação 2 do artigo o dá. Se T é grande em comparação com os logits e os logits têm média zero por exemplo, o artigo mostra que isso é aproximadamente (1/(N T^2))(z_i - v_i), onde N é o número de classes. Então, no limite de temperatura alta, a destilação equivale a minimizar 1/2 (z_i - v_i)^2, o logit matching de Caruana e colaboradores. Igualar logits é um caso especial de destilação.

O fator que importa na prática é o 1/T^2. O artigo diz que as magnitudes dos gradientes dos soft targets escalam como 1/T^2, então é importante multiplicá-los por T^2 ao usar hard e soft targets juntos. Isso mantém as contribuições relativas dos dois aproximadamente inalteradas quando você muda T enquanto experimenta as outras configurações.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

teacher = np.array([9.0, 4.0, 2.0, 0.0, -4.0])
student = np.array([6.0, 5.0, 0.0, 1.0, -2.0])
for T in (1, 2, 5, 10, 20):
    grad = (softmax(student, T) - softmax(teacher, T)) / T
    print(T, "%.4f" % np.abs(grad).max(), "%.4f" % (np.abs(grad).max() * T**2))
```

A saída mostra a maior entrada do gradiente encolhendo de 0,2663 com T = 1 para 0,0017 com T = 20. Multiplicada por T ao quadrado, ela fica entre 0,64 e 0,84 de T = 2 até T = 20. A linha de T = 1 não é uma comparação justa, já que a aproximação de temperatura alta não vale ali.

### A loss combinada

Quando existem rótulos corretos para o conjunto de transferência, o artigo constata que o treinamento só com os soft targets melhora se o aluno também for treinado para produzir os rótulos corretos. Ele tentou modificar os soft targets com os rótulos e achou melhor uma média ponderada de dois objetivos. O primeiro é a cross-entropy com os soft targets, calculada com o T alto. O segundo é a cross-entropy com os rótulos corretos, calculada a partir dos mesmos logits do aluno com T = 1. O artigo encontrou os melhores resultados, em geral, com um peso consideravelmente menor no segundo objetivo.

Escrita por extenso, com a notação desta trilha e não a do artigo, com lambda o peso do termo soft:

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

Essa é uma [loss combinada](../GLOSSARY.md). Os experimentos de fala do artigo usaram um peso relativo de 0,5 no termo do hard label e temperaturas de 1, 2, 5 e 10. A razão do pequeno termo do hard label é prática: o aluno em geral não consegue igualar os soft targets exatamente, e o artigo diz que errar para o lado da resposta correta acaba sendo útil.

O DistilBERT segue o mesmo padrão. Ele aplica um softmax com temperatura ao professor e ao aluno durante o treinamento, define T como 1 na inferência e soma os seus próprios termos à loss dos soft targets como uma combinação linear com a loss de masked language modeling e uma loss de embedding por cosseno.

### Escolhendo T

O artigo dá duas observações sobre o MNIST. Quando a rede destilada tinha 300 ou mais unidades em cada uma de duas camadas ocultas, todas as temperaturas acima de 8 deram resultados bastante parecidos. Quando as camadas foram cortadas para 30 unidades, temperaturas de 2,5 a 4 funcionaram significativamente melhor do que as mais altas ou mais baixas. Os autores sugerem que, quando o aluno é pequeno demais para capturar todo o conhecimento do professor, ignorar os logits muito negativos que uma temperatura mais baixa desconta pode ajudar.

Não leve uma temperatura de um classificador para um modelo de linguagem. Os autores do Minitron tentaram as temperaturas 0,1, 0,5, 1,0 e 3,0 ao retreinar um LLM podado a partir do seu professor e relatam os melhores resultados com 1,0 (apêndice A.3). Eles dão um motivo para incluir valores abaixo de 1: as distribuições de logits de LLMs têm entropia maior do que as distribuições em pico dos modelos de visão, então esperavam que suavizar importasse menos. Um segundo estudo, maior, concorda. Busbridge et al. (2025) varreram a temperatura de 0,5 a 10 para alunos de 198M a 1,82B de parâmetros, cada um destilado de um professor de 546M a 7,75B, e encontraram o melhor desempenho em 1 em todas as escalas (apêndice G.2). Temperaturas acima de 3 prejudicaram, e os alunos menores sofreram mais. No apêndice B.3 eles dizem que, ao contrário da literatura que citam, a temperatura ótima é um, e levantam a hipótese de que a diferença é que o trabalho anterior usava tokens repetidos, enquanto o cenário deles não repete dados. A hipótese é deles e o artigo não a testa aqui. Os dois achados vêm de cenários ao estilo de pré-treinamento de um único laboratório, então leia-os como um forte motivo para incluir T = 1 em qualquer varredura, e não como uma prova de que temperaturas mais altas nunca ajudam.

A ablação do Minitron também é de um único cenário. Na receita final deles, também constataram que a loss de logits sozinha era melhor do que uma mistura ponderada com a loss de language modeling, o que é um lembrete de que o peso é uma configuração a testar e não uma constante.

## Prática

1. ▢ Usando os logits 9, 4, 2, 0 e -4, aproximadamente que probabilidade a primeira classe recebe com T = 5?

    - a) Cerca de 0,99
    - b) Cerca de 0,54
    - c) Cerca de 0,20
    - d) Cerca de 0,01

<details markdown="1"><summary>Dica</summary>

Divida os logits por 5, aplique a exponencial em cada um e divida o primeiro pela soma dos cinco.

</details>

<details markdown="1"><summary>Verificação</summary>

**b)** Os logits escalados são 1,8, 0,8, 0,4, 0 e -0,8. As suas exponenciais são cerca de 6,05, 2,23, 1,49, 1,00 e 0,45, que somam cerca de 11,22, e 6,05 / 11,22 é 0,54. A alternativa (a) é a resposta de T = 1. A alternativa (c) é a segunda classe, 0,198 com T = 5, e não a primeira.

</details>

2. ▢ Você eleva T de 4 para 8 e não muda mais nada. Por que o artigo multiplica o termo soft por T ao quadrado?

    - a) Para cancelar a própria configuração de temperatura do professor
    - b) Para garantir que os soft targets somem um
    - c) Para elevar a confiança do aluno na hora do teste
    - d) Para manter os gradientes soft e hard em equilíbrio

<details markdown="1"><summary>Verificação</summary>

**d)** Os gradientes soft encolhem como 1/T^2, então, sem o fator, o termo soft esmaeceria diante do termo hard conforme T crescesse. Não é (b): o softmax já normaliza. Não é (c): na inferência o aluno roda com T = 1 e nada é multiplicado. Não é (a): professor e aluno compartilham o mesmo T e nenhum dos dois é cancelado.

</details>

3. ▢ Na loss combinada do artigo, qual termo roda com a temperatura alta, qual roda com T = 1 e qual costuma receber o peso menor?

<details markdown="1"><summary>Verificação</summary>

A cross-entropy com os soft targets do professor roda com o T alto, usando os logits do aluno divididos por T. A cross-entropy com os rótulos corretos roda sobre os mesmos logits com T = 1. O artigo encontrou os melhores resultados, em geral, com um peso consideravelmente menor no termo do hard label. Os pesos são a configuração que você ajusta, então diga qual deles um resultado usou.

</details>

4. ▢ Um colega copia a configuração T = 20 do MNIST para uma destilação de LLM e obtém um aluno pior. O que nesta lição sugere o motivo, e o que ele deveria fazer?

<details markdown="1"><summary>Verificação</summary>

A ablação do Minitron sobre 0,1, 0,5, 1,0 e 3,0 e a varredura de Busbridge de 0,5 a 10 encontraram os melhores resultados em 1, e os autores do Minitron dizem que as distribuições de logits de LLMs têm entropia maior do que as distribuições em pico dos modelos de visão. Com T = 20, os alvos no trecho acima são quase planos, então as diferenças que o aluno precisa aprender são pequenas. Ele deveria rodar uma varredura curta que inclua T = 1 com o seu próprio professor e o seu próprio aluno. Os dois achados vêm de um cenário cada, então são um ponto de partida, não uma regra.

</details>

5. ▢ Nos experimentos de MNIST do artigo, qual aluno foi mais sensível à escolha da temperatura, o com 300 ou mais unidades ocultas ou o com 30, e que faixa funcionou para o sensível?

<details markdown="1"><summary>Verificação</summary>

O aluno de 30 unidades. Temperaturas de 2,5 a 4 funcionaram significativamente melhor do que as mais altas ou mais baixas para ele, enquanto com 300 ou mais unidades tudo acima de 8 deu resultados bastante parecidos. O artigo lê isso como ignorar logits muito negativos ajudando quando o aluno é pequeno demais para guardar todo o conhecimento do professor.

</details>

## Prática no mundo real

- [ ] Rode os dois scripts. Mude as temperaturas para 3 e 8 no segundo e confira que a última coluna fica na mesma faixa.
- [ ] Escreva a loss combinada como uma função NumPy dos logits do aluno, dos logits do professor, do índice do rótulo, de T e de lambda, e confira que, com lambda = 0, ela é igual à cross-entropy comum no rótulo.
- [ ] Amanhã: sem consultar anotações, enuncie a fórmula do softmax com temperatura, diga qual termo da loss combinada roda com qual temperatura e diga por que o fator T ao quadrado está ali.

## Para ir além

- [Losses de Destilação](../reference/distillation-losses.md)
- [Artigo científico: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals e Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Artigo científico: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Artigo científico: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
