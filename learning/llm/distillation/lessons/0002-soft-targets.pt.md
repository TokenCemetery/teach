---
title: "2. Soft targets"
description: "O que as probabilidades que um professor dá às respostas erradas carregam, e por que elas são um sinal de treinamento mais rico do que um hard label"
type: lesson
---

# Lição 2. Soft targets

**Ligação com a missão:** A missão pede que você explique por que os soft targets de um professor carregam mais sinal de treinamento do que os hard labels, e esta lição é essa explicação, com uma execução contra a qual você pode conferi-la.
**Fonte principal:** [Artigo científico: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals e Dean, 2015](https://arxiv.org/abs/1503.02531)
**Pré-requisitos:** [Lição 1](0001-what-distillation-buys.md), [Soft targets](../GLOSSARY.md), [Hard label](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Aquecimento

1. ▢ Em uma destilação, os pesos de qual modelo mudam durante o treinamento, e qual modelo é o sinal de treinamento?

<details markdown="1"><summary>Verificação</summary>

Só o [aluno](../GLOSSARY.md) aprende. O [professor](../GLOSSARY.md) fica fixo e fornece os alvos. Confundir os dois é o primeiro erro comum ao ler uma loss de destilação.

</details>

2. ▢ A rede de 800 unidades do MNIST cometeu 146 erros sozinha e 74 quando também igualou as saídas da rede de 1200 unidades. O que os 74 mostraram sobre o que os alvos carregavam?

<details markdown="1"><summary>Verificação</summary>

Os alvos carregavam conhecimento sobre como generalizar, aprendido pelo professor a partir de dados de treinamento com jitter, que o aluno nunca viu no seu próprio conjunto de transferência. Um hard label para cada imagem não contém nada disso.

</details>

## Saiba isto

### O que um hard label joga fora

Um classificador treinado dá à maioria das imagens uma probabilidade próxima de 1 para a classe certa. As probabilidades minúsculas nas classes erradas ainda diferem de imagem para imagem. Hinton et al. dão um exemplo do MNIST: uma versão de um 2 pode receber probabilidade 10^-6 de ser um 3 e 10^-9 de ser um 7, e outra versão de um 2 pode receber o contrário. Isso diz quais 2s parecem 3s e quais parecem 7s, uma estrutura de similaridade sobre os dados. Um [hard label](../GLOSSARY.md) diz apenas "2" para ambos.

O termo do artigo para o alvo de treinamento construído a partir dessas probabilidades é soft targets. A informação que eles carregam às vezes é chamada de dark knowledge, um nome que não aparece neste artigo. Esta trilha diz [soft targets](../GLOSSARY.md) para o alvo e evita a outra expressão.

### O problema: números pequenos mal mexem na loss

A mesma passagem nomeia o problema. Probabilidades tão próximas de zero têm muito pouca influência no custo de cross-entropy durante a transferência. Pegue um aluno que dá ao 2 a probabilidade 0,98 e ao 3 a probabilidade 0,01, contra um professor com 1,0 e 10^-6. O 2 contribui com cerca de 0,0202 para a loss e o 3 com cerca de 0,0000046, mais de 4.000 vezes menos. O sinal está lá e a loss é surda a ele.

Caruana e colaboradores, diz o artigo, evitaram isso igualando logits com um erro quadrático em vez de igualar probabilidades. A resposta mais geral de Hinton et al. é elevar a temperatura até que os alvos fiquem suaves o bastante para importar, que é a lição 3.

### Veja rodando

O script constrói um professor sobre cinco classes de dígitos e depois dois alunos. Ambos preveem "2" com a mesma confiança. O aluno A troca a ordem do 3 e do 7 em relação ao professor, e o aluno B mantém a ordem do professor.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def kl(p, q):
    return float(np.sum(p * np.log(p / q)))

teacher = [9.0, 4.0, 2.0, 0.0, -4.0]    # classes: 2, 3, 7, 8, 0
student_a = [9.0, 1.0, 4.0, 0.0, -4.0]  # same top class, 3 and 7 swapped
student_b = [9.0, 4.0, 2.5, 0.0, -4.0]  # same ranking as the teacher

for T in (1, 5):
    p = softmax(teacher, T)
    print("T =", T)
    for name, z in (("A", student_a), ("B", student_b)):
        q = softmax(z, T)
        ce = -np.log(softmax(z)[0])
        print("  student", name, "hard-label CE %.4f" % ce, "KL(teacher||student) %.4f" % kl(p, q))
```

Preveja antes de rodar: qual aluno a cross-entropy do hard label contra o rótulo "2" prefere, e qual a divergência em relação ao professor prefere? Ele imprime isto, no NumPy 2.5:

```text
T = 1
  student A hard-label CE 0.0072 KL(teacher||student) 0.0177
  student B hard-label CE 0.0083 KL(teacher||student) 0.0001
T = 5
  student A hard-label CE 0.0072 KL(teacher||student) 0.0414
  student B hard-label CE 0.0083 KL(teacher||student) 0.0006
```

O hard label prefere ligeiramente o A, o aluno com a estrutura de similaridade errada. A divergência em relação ao professor prefere o B por uma margem ampla. Os números são construídos para a demonstração, então leia a direção e não os tamanhos. A divergência `KL` é a [divergência KL](../GLOSSARY.md) da distribuição do professor em relação à do aluno.

### Por que isso importa mais para um modelo de linguagem

A passagem do artigo sobre entropia se aplica diretamente a um modelo de linguagem. Quando os soft targets têm alta entropia, eles dão muito mais informação por caso de treinamento do que os hard targets. Uma distribuição de próximo token raramente fica perto de one-hot: muitas continuações são plausíveis. Os autores do Minitron dizem, em um apêndice sobre a loss de destilação, que as distribuições de logits de LLMs têm entropia maior do que as distribuições em pico dos modelos de classificação (Muralidharan et al., 2024, apêndice A.3). A observação deles é sobre aquele cenário, mas aponta na mesma direção.

### Informação sobre uma classe que o aluno nunca viu

O artigo removeu todos os 3 do conjunto de transferência, então o aluno nunca viu um. Ele ainda cometeu apenas 206 erros de teste, 133 deles nos 1010 3s de teste. A maior parte dos erros veio de o bias aprendido da classe 3 ser baixo demais. Com esse bias aumentado em 3,5, uma escolha feita para otimizar o desempenho geral no teste, ele cometeu 109 erros, 14 em 3s, e acertou 98,6% dos 3s de teste. O conhecimento de como é um 3 chegou pelos soft targets dos outros dígitos.

## Prática

1. ▢ Na execução acima, qual aluno a cross-entropy do hard label prefere com T = 1, e qual a divergência em relação ao professor prefere?

<details markdown="1"><summary>Dica</summary>

Compare primeiro os dois números de CE, depois os dois números de KL, e pergunte o que cada loss consegue enxergar.

</details>

<details markdown="1"><summary>Verificação</summary>

A cross-entropy contra o rótulo "2" prefere o A (0,0072 contra 0,0083). A divergência em relação ao professor prefere o B (0,0001 contra 0,0177). O hard label enxerga apenas a probabilidade do "2". A ordem errada do 3 e do 7 no A é invisível para ele, e essa ordem é o que o soft target carrega.

</details>

2. ▢ Por que as probabilidades minúsculas do professor nas classes erradas mal ajudam quando o aluno é treinado com temperatura 1?

    - a) Só a entrada da classe correta entra na loss
    - b) As entradas das classes erradas são descartadas antes da loss
    - c) Cada termo é escalado pela sua probabilidade-alvo
    - d) O softmax do aluno não consegue produzir valores muito pequenos

<details markdown="1"><summary>Verificação</summary>

**c)** Cada termo da cross-entropy é a probabilidade-alvo vezes o log da do aluno. Um alvo de 10^-6 pesa um milionésimo do que pesa um alvo próximo de 1. Não é (b): nada as remove. Não é (a): isso descreve a loss do hard label, não a do soft target. Não é (d): um softmax consegue produzir 10^-9 sem problema.

</details>

3. ▢ Um aluno treinado em um conjunto de transferência sem 3s acerta 98,6% dos 3s de teste depois que o seu bias para a classe 3 é aumentado. Como ele pode saber o que é um 3?

<details markdown="1"><summary>Verificação</summary>

Os soft targets do professor em outros dígitos, 2s, 5s e 8s por exemplo, põem uma pequena probabilidade no 3. Essas probabilidades ensinam ao aluno quais features elevam a pontuação de um 3, sem um único 3 como exemplo de treinamento. O bias aprendido para a classe estava baixo demais, então o conhecimento estava lá e o deslocamento é que estava errado. O resultado é do artigo, no MNIST, com um único bias ajustado.

</details>

4. ▢ Um professor dá ao 2 a probabilidade 1.0 e ao 3 a probabilidade 10^-6. Um aluno dá a eles 0.98 e 0.01. Quantas vezes menor, aproximadamente, é o termo do 3 na cross-entropy do que o termo do 2?

<details markdown="1"><summary>Dica</summary>

Cada termo é a probabilidade do professor vezes o logaritmo natural negativo da do aluno.

</details>

<details markdown="1"><summary>Verificação</summary>

O termo do 2 é -1.0 \* ln(0.98), cerca de 0,0202. O termo do 3 é -10^-6 \* ln(0.01), cerca de 0,0000046. A razão é cerca de 4.400, então mais de 4.000 vezes menor. É por isso que elevar a temperatura, e não simplesmente confiar na loss, é o caminho do artigo para fazer essas entradas contarem.

</details>

## Prática no mundo real

- [ ] Rode o script. Depois mude o aluno A para que o 3 continue acima do 7 (por exemplo `[9.0, 3.0, 2.5, 0.0, -4.0]`) e observe os dois números de KL caírem em direção aos do aluno B.
- [ ] Encontre um classificador que você consiga carregar, imprima o softmax dele para cinco imagens com temperatura 1 e anote a segunda e a terceira classes mais prováveis. Elas parecem vizinhas da classe verdadeira?
- [ ] Amanhã: sem consultar anotações, explique em duas frases por que um hard label não consegue carregar a similaridade entre um 2 e um 7.

## Para ir além

- [Losses de Destilação](../reference/distillation-losses.md)
- [Artigo científico: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals e Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
