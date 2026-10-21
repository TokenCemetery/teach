---
title: "17. Fidelidade e generalização"
description: "Por que um aluno que generaliza bem ainda pode discordar do seu professor, e de qual das duas você precisa"
type: lesson
---

# Lição 17. Fidelidade e generalização

**Ligação com a missão:** A missão pede que você preveja o que um aluno vai herdar e meça o que ele perdeu, o que começa separando o quanto ele copia o professor do quão bem ele faz a tarefa.
**Fonte principal:** [Artigo científico: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), seções 3 a 7
**Pré-requisitos:** [Lição 3](0003-temperature.md), [Lição 16](0016-on-policy-distillation-in-practice.md), [Fidelidade](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Loss combinada](../GLOSSARY.md)

## Aquecimento

1. ▢ A loss combinada soma dois termos. Qual deles puxa o aluno para o professor e qual para os rótulos?

<details markdown="1"><summary>Verificação</summary>

A divergência em relação aos [soft targets](../GLOSSARY.md) do professor o puxa para o professor, e a cross-entropy contra os [hard labels](../GLOSSARY.md) o puxa para os dados. Um coeficiente de mistura os pondera.

</details>

2. ▢ A fase on-policy do Qwen3 minimiza o KL entre aluno e professor nas amostras do próprio aluno. Qual direção do KL é a forma do professor para o aluno, e o que ela penaliza?

<details markdown="1"><summary>Verificação</summary>

KL(professor || aluno) é o forward KL. Ele penaliza o aluno por dar pouca probabilidade onde o professor dá muita, então empurra o aluno a cobrir tudo o que o professor cobre.

</details>

3. ▢ Na lição 16, o aluno do Qwen3 superou o checkpoint treinado com RL nos benchmarks. Isso diz que as previsões do aluno coincidem com as do professor?

<details markdown="1"><summary>Verificação</summary>

Não. As pontuações de benchmark medem a tarefa. Se o aluno concorda com as previsões do professor é uma medição separada, e esta lição trata de por que as duas podem se separar.

</details>

## Saiba isto

### Duas coisas que a destilação poderia significar que melhorou

Stanton et al. separam duas quantidades que a literatura de destilação costuma embaralhar. A **fidelidade** é a capacidade de um aluno de igualar as previsões do professor. A **generalização** é o desempenho do aluno em dados não vistos e na mesma distribuição. Eles medem a fidelidade com dois números sobre as mesmas entradas, ambos definidos na seção 3.2:

| Métrica | O que mede |
|---|---|
| Concordância top-1 média | A fração das entradas em que aluno e professor escolhem o mesmo rótulo de topo |
| KL preditivo médio | O KL(professor \|\| aluno) médio, sensível a todas as classes, não apenas à de topo |

A acurácia não pode substituir a concordância. O exemplo do próprio artigo: três modelos independentes com 55%, 75% e 95% de acurácia de teste. O primeiro e o terceiro podem concordar em no máximo 60% das entradas, enquanto o segundo e o terceiro concordam em pelo menos 70%, e ainda assim ninguém diria que o modelo de 75% é uma destilação melhor do modelo de 95%, já que foram treinados de forma independente.

### O controle para "eles concordam porque ambos são bons"

A concordância sobe só porque os modelos são acurados. Para separar uma melhora geral de uma melhora específica em igualar, o artigo também treina um segundo aluno, destilado pelo mesmo procedimento a partir de um professor independente. Se os dois alunos concordam com o primeiro professor mais ou menos igualmente, a concordância é explicada pela generalização. Se o aluno real concorda mais com o seu próprio professor, isso é fidelidade.

### O que eles encontraram

Os experimentos deles são em sua maioria de classificação de imagens com ResNets no CIFAR-100, mais MNIST, ImageNet e um dataset de classificação de texto (sentimento do IMDB) no apêndice. Não são experimentos de geração de modelos de linguagem, então leia-os como um resultado sobre destilação em geral e depois teste-o no seu próprio par de LLMs.

| Achado | Evidência no artigo |
|---|---|
| Caso fácil: igualar funciona | O LeNet-5 no MNIST chegou a mais de 99% de concordância top-1 no teste com dados de destilação suficientes (seção 4.1) |
| Caso mais difícil: muitas vezes não funciona | A autodestilação do ResNet-56 no CIFAR-100 ficou abaixo de 80% de concordância no teste mesmo com o maior conjunto de destilação (seção 6.1) |
| Melhor generalização pode vir com pior fidelidade | Na autodestilação, ampliar os dados com amostras de GAN elevou a fidelidade e diminuiu a acurácia no teste, porque um aluno que falha em igualar o professor pode generalizar melhor (Figura 1a, seção 4.2) |
| Com um professor mais forte, as duas se alinham | Ao destilar um ensemble de 3 componentes, a fidelidade e a acurácia no teste subiram com mais dados (Figura 1b) |
| Não é capacidade | A baixa fidelidade aparece até na autodestilação, em que o aluno tem a capacidade do próprio professor, e ampliar o aluno quase não a mudou ao destilar um ensemble (seção 4.4) |
| Não é uma arquitetura, escala ou domínio | Resultados parecidos com VGG, no ImageNet e no IMDB (seção 4.4) |

### A explicação: otimização

O artigo testa duas hipóteses para a falha. Uma é a identificabilidade: os dados de destilação são pequenos demais para determinar a função do professor. Mais dados ajudam a concordância no teste, então isso faz parte da história. A outra é a otimização: o aluno não consegue nem igualar o professor nos dados de destilação em que treina.

A segunda se sustenta. Com 50 mil imagens sintéticas acrescentadas, um aluno com a mesma capacidade do professor chegou a apenas 95% de concordância nos próprios dados de destilação. Com forte aumento de dados, a concordância no treinamento ficou entre 80% e 90% para três aumentos e caiu para cerca de 60% na autodestilação para a combinação dos três (seção 6.1). Treinar por mais tempo ajudou um pouco: para uma autodestilação de ResNet-20, 5.000 épocas de SGD chegaram a 83,3% de concordância no treinamento contra 78,95% com 300 épocas, e trocar para o Adam reduziu a fidelidade (seção 6.2).

O resumo do artigo é um trade-off. Acrescentar exemplos além dos dados de treinamento do professor dá ao aluno mais rótulos do professor para identificar a função, e também torna mais difícil um problema de otimização que já era difícil. Nas palavras do artigo, uma boa fidelidade está diretamente alinhada com resolver um problema de otimização excepcionalmente difícil, em que o treinamento comum se salva por não precisar resolvê-lo bem.

### O que isso muda para você

Se você avalia um LLM destilado apenas pela acurácia na tarefa, não consegue dizer quanto do professor você herdou. Dois alunos podem pontuar o mesmo e diferir muito na concordância. A etapa 8 constrói a medição completa, e o hábito mínimo é este: relate a concordância com o professor em entradas held-out ao lado da qualidade na tarefa e compare com um aluno destilado de um professor diferente ou treinado sem um.

A fidelidade nem sempre é o objetivo. O resultado de autodestilação do próprio artigo mostra um aluno que falha em igualar o professor e ainda assim generaliza melhor. A fidelidade importa quando você quer herdar propriedades além da acurácia: o artigo lista transferir calibração ou robustez para que um modelo menor possa substituir um maior com segurança (seção 4.3). Ele também constatou que o aluno de maior fidelidade foi sempre o mais bem calibrado ao destilar ensembles.

Um esboço em Python puro das duas medições, que imprime a saída mostrada nos comentários:

```python
import math

def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]

def argmax(z):
    return max(range(len(z)), key=lambda i: z[i])

def kl(p, q):
    return sum(pi * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))

# One row per example: logits over three classes, plus the true label.
teacher = [[3.0, 1.0, 0.0], [0.5, 2.5, 0.0], [0.0, 0.5, 3.0], [1.0, 2.0, 0.0]]
student = [[2.0, 1.5, 0.0], [0.0, 1.0, 2.0], [0.0, 0.5, 2.5], [2.0, 1.5, 0.0]]
labels = [0, 1, 2, 0]

agreement = sum(argmax(t) == argmax(s) for t, s in zip(teacher, student)) / len(labels)
mean_kl = sum(kl(softmax(t), softmax(s)) for t, s in zip(teacher, student)) / len(labels)
teacher_acc = sum(argmax(t) == y for t, y in zip(teacher, labels)) / len(labels)
student_acc = sum(argmax(s) == y for s, y in zip(student, labels)) / len(labels)

print(f"agreement {agreement:.2f}  mean KL {mean_kl:.3f}")      # agreement 0.50  mean KL 0.321
print(f"teacher accuracy {teacher_acc:.2f}  student accuracy {student_acc:.2f}")  # both 0.75
```

Os dois modelos pontuam 0,75, e concordam em apenas metade das entradas.

## Prática

1. ▢ Um professor tem 93% de acurácia e um aluno tem 91%, no mesmo conjunto de teste. Entre quais limites a concordância top-1 deles precisa ficar?

<details markdown="1"><summary>Dica</summary>

O aluno erra em 9% das entradas e o professor em 7%. O quanto os dois conjuntos de erros podem se sobrepor, e o quão pouco?

</details>

<details markdown="1"><summary>Verificação</summary>

Entre 84% e 98%. Eles concordam onde ambos acertam, e o pior caso é que os seus erros nunca se sobreponham, o que deixa 100 menos 7 menos 9, então pelo menos 84%. Eles podem concordar em no máximo 98%: o aluno erra em 2 pontos percentuais de entradas a mais do que o professor, então pelo menos 2% das entradas têm o professor certo e o aluno errado. Igualar a acurácia diz muito pouco sobre a concordância, que é o ponto da lição.

</details>

2. ▢ No controle do artigo, por que treinar um segundo aluno a partir de um professor independente?

    - a) Para verificar que o professor foi treinado corretamente
    - b) Para separar a fidelidade da habilidade compartilhada
    - c) Para elevar a acurácia do primeiro aluno
    - d) Para reduzir o compute necessário no total

<details markdown="1"><summary>Verificação</summary>

**b)** Se um aluno concorda com um professor independente tanto quanto com o seu próprio, a concordância é explicada por ambos serem bons, não por cópia. (a) não é testado aqui. (c) e (d) são falsos: o segundo aluno é uma ferramenta de medição e não muda nada no primeiro.

</details>

3. ▢ Na autodestilação no CIFAR-100 com um aluno e um professor ResNet-56, o conjunto de destilação é ampliado com imagens geradas por GAN. Preveja a direção da fidelidade do aluno e da acurácia de teste do aluno.

<details markdown="1"><summary>Dica</summary>

A autodestilação é o caso em que o aluno já tem a capacidade de igualar o professor, e o artigo observa que falhar em igualar pode por si só ajudar.

</details>

<details markdown="1"><summary>Verificação</summary>

A fidelidade aumenta e a acurácia de teste diminui (Figura 1a). Na autodestilação, o aluno que iguala menos de perto o professor generaliza melhor, então mais fidelidade custa acurácia. Com um professor ensemble de 3, a direção se inverte: ambas sobem (Figura 1b). Qual se aplica a você depende de o seu professor generalizar muito melhor do que um aluno treinado de forma independente.

</details>

4. ▢ Um aluno destilado com a própria arquitetura do professor ainda discorda dele em 20% das entradas held-out. Liste as hipóteses que o artigo testa e diga qual ele apoia.

<details markdown="1"><summary>Verificação</summary>

Capacidade do aluno, arquitetura, escala do dataset, domínio dos dados, identificabilidade e otimização (seção 4.4). O artigo descarta a capacidade, já que o aluno tem a capacidade do professor, e as outras com base na sua evidência. Ele apoia a otimização como uma razão central: o aluno não iguala o professor nem nas suas próprias entradas de treinamento. A identificabilidade também faz parte do quadro, já que mais dados elevaram a concordância no teste. O artigo encontrou a grande lacuna de concordância em tarefas de imagem, então confira no seu par de LLMs antes de presumir que ela se transfere.

</details>

5. ▢ Qual destas medições de LLM é o análogo mais próximo do KL preditivo médio do artigo, e o que ela exige que a concordância não exige?

<details markdown="1"><summary>Verificação</summary>

O KL(professor || aluno) médio por posição em sequências held-out, que é a loss de destilação em nível de token com forward KL da etapa 2 avaliada em dados não usados no treinamento. Ela exige a distribuição completa do professor em cada posição, o que a concordância no token de topo não exige. A concordância no token de topo é o análogo mais barato da concordância top-1. Esse mapeamento do cenário de classificação do artigo para o nível de token é minha adaptação, não um experimento do artigo.

</details>

## Prática no mundo real

- [ ] Rode o esboço acima e depois mude uma linha de logits do aluno para que os dois modelos discordem em outro exemplo enquanto a acurácia continua em 0,75. Anote o que aconteceu com a concordância e com o KL médio.
- [ ] Leia a seção 3.2 do artigo de Stanton e escreva em uma linha a fórmula da concordância top-1 média. Depois escreva o que o aluno de controle s-prime diz a você.
- [ ] Amanhã: sem consultar anotações, enuncie a diferença entre fidelidade e generalização, um caso em que mais fidelidade reduz a acurácia e a explicação principal do artigo para a baixa fidelidade.

## Para ir além

- [O Que o Aluno Herda](../reference/what-the-student-inherits.md)
- [Artigo científico: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
