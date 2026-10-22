---
title: "5. Forward e reverse KL"
description: "Por que o forward KL espalha o aluno por todos os modos do professor e o reverse KL o faz se comprometer com um só"
type: lesson
---

# Lição 5. Forward e reverse KL

**Ligação com a missão:** A missão pede que você escolha entre forward e reverse KL, e esta lição dá as duas direções, o caso de brinquedo que as separa e os artigos que discordam sobre qual usar.
**Fonte principal:** [Artigo científico: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
**Pré-requisitos:** [Lição 4](0004-token-level-distillation.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md), [Divergência KL](../GLOSSARY.md)

## Aquecimento

1. ▢ Em `token_kd_loss`, sobre qual eixo a divergência é tomada, e o que a máscara faz com a média final?

<details markdown="1"><summary>Verificação</summary>

A divergência é tomada sobre o eixo do vocabulário, o último, dando um número por posição. A máscara zera as posições de padding e a divisão final pela soma da máscara tira a média apenas sobre os tokens reais.

</details>

2. ▢ Na lição 2, uma probabilidade de 10^-6 do professor em uma classe errada mal mexeu em uma loss de cross-entropy. Qual fator do termo o torna pequeno?

<details markdown="1"><summary>Verificação</summary>

O termo é a probabilidade do professor vezes uma razão de logs, então um alvo de 10^-6 o reduz a um milionésimo. Guarde isto: a direção do KL decide de quem é a probabilidade que faz o escalonamento.

</details>

## Saiba isto

### Duas direções de uma divergência

A divergência KL não é simétrica. Com p o professor e q o aluno, o [forward KL](../GLOSSARY.md) é KL(p || q), a soma sobre os tokens de p log(p / q). O [reverse KL](../GLOSSARY.md) é KL(q || p), a soma de q log(q / p). A única diferença é de quem é a probabilidade que multiplica a razão de logs, e isso decide o que cada um pune. O GKD (Agarwal et al., 2023, seção 2) usa esses mesmos nomes.

O forward KL pondera cada token pela probabilidade do professor. Um token de que o professor gosta e a que o aluno dá quase nenhuma probabilidade custa muito, porque a razão p / q é enorme. Um token a que o professor dá quase nada e de que o aluno gosta é barato, já que p é pequeno. O aluno é empurrado a pôr alguma massa onde quer que o professor tenha massa, o que é cobrir modos.

O reverse KL pondera cada token pela probabilidade do aluno. O aluno é punido por pôr massa onde o professor tem quase nenhuma, porque q log(q / p) é grande ali. Ignorar um modo do professor não custa nada, então o aluno é livre para tomar um deles. Isso é buscar modos.

### Dois modos, dois alunos

O professor abaixo tem duas continuações igualmente prováveis e um pouco de probabilidade em outras duas. O primeiro aluno espalha a sua massa. O segundo se compromete com um modo.

```python
import numpy as np

p = np.array([0.49, 0.01, 0.01, 0.49])        # teacher: two modes
students = {
    "spread": np.array([0.25, 0.25, 0.25, 0.25]),
    "commit": np.array([0.97, 0.01, 0.01, 0.01]),
}

def kl(a, b):
    return float(np.sum(a * np.log(a / b)))

for name, q in students.items():
    print(name, "forward %.3f" % kl(p, q), "reverse %.3f" % kl(q, p))
```

Preveja qual aluno cada direção prefere e depois rode. A saída no NumPy 2.5:

```text
spread forward 0.595 reverse 1.273
commit forward 1.572 reverse 0.623
```

O forward KL prefere o aluno espalhado (0,595 contra 1,572), que põe probabilidade nos dois modos e desperdiça um pouco nos dois tokens raros. O reverse KL prefere o aluno comprometido (0,623 contra 1,273), que se assenta em um modo e ignora o outro. Nenhum dos dois alunos iguala o professor. Qual falha você quer depende do que o aluno vai fazer em seguida, que é o argumento dos próximos dois artigos.

### O argumento a favor do reverse KL

Gu et al. argumentam que os objetivos padrão de destilação minimizam um forward KL aproximado, o que força o aluno a cobrir todos os modos do professor. Para classificação, com um número finito de classes, as duas distribuições têm poucos modos e isso funciona bem. Para geração aberta, o professor pode ter muito mais modos do que um aluno pequeno consegue expressar. O artigo diz que o forward KL faz então o aluno atribuir probabilidade absurdamente alta a regiões onde o professor tem quase nenhuma, e produzir amostras muito improváveis sob o professor durante a geração em free-run (introdução). O remédio deles é o reverse KL, que busca os modos principais e dá baixa probabilidade às regiões vazias do professor. Em texto, dizem eles, o aluno evita aprender variantes demais da cauda longa da distribuição do professor e se concentra na correção.

Eles mostram o efeito em um brinquedo: uma mistura de gaussianas ajustada com uma única gaussiana por cada divergência (Figura 2). Eles otimizam o reverse KL com um policy gradient sobre amostras do aluno, com passos extras para estabilidade, o que o torna um método on-policy. A lição 15 o cobre. A loss em si é simples. Com as log-probabilidades do trecho anterior, o reverse KL por posição é `(s.exp() * (s - t)).sum(dim=-1)` no lugar da linha do forward.

### O argumento a favor de escolher

O GKD não toma partido. Ele faz da divergência um parâmetro. A sua JSD generalizada, para um coeficiente beta entre 0 e 1, é:

```text
JSD(beta)(P || Q) = beta * KL(P || beta*P + (1-beta)*Q) + (1-beta) * KL(Q || beta*P + (1-beta)*Q)
```

Com P o professor, ela interpola entre as duas direções. Os gradientes se comportam como o forward KL quando beta se aproxima de 0 e como o reverse KL quando beta se aproxima de 1. Ela também é limitada mesmo quando os suportes são disjuntos, o que o KL não é (seção 2). No mesmo brinquedo, com a função `jsd` escrita a partir dessa fórmula (que não está no artigo), os três valores de JSD dão um cruzamento:

| Aluno | JSD(0,1) | JSD(0,5) | JSD(0,9) |
|---|---|---|---|
| spread | 0,055 | 0,177 | 0,091 |
| commit | 0,102 | 0,189 | 0,058 |

Com beta = 0,1 o aluno espalhado vence e com beta = 0,9 vence o comprometido, o que combina com a direção que cada extremo diz preferir. Com 0,5 eles ficam próximos. Os números vêm do brinquedo, não de uma execução.

Os experimentos do GKD dizem que a melhor divergência depende da tarefa. No resumo XSum, passar do forward KL para o reverse KL pela família JSD diminuiu a diversidade da saída (Figura 4). Nas ablações, as divergências que buscam modos se saíram melhor quando avaliadas com amostragem por temperatura, e a escolha importou pouco com decodificação greedy (seção 4.1). No instruction tuning agnóstico de tarefa com o FLAN, o GKD on-policy com reverse KL superou substancialmente o KD supervisionado e o ImitKD, e o reverse KL se saiu muito melhor do que o forward KL ali (Figura 10). No GSM8K, o forward KL se saiu bastante bem, e o reverse KL também, especialmente ao treinar apenas em um dataset fixo. O resumo do artigo é que a divergência deve ser escolhida pelo trade-off entre diversidade e qualidade na tarefa.

A implementação do TRL expõe essa escolha como `beta` em `GKDConfig`: com 0.0 a loss é a divergência KL, com 1.0 é o KL inverso, com padrão 0.5 ([documentação do GKD no TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer), lida para esta lição).

### Evidência no sentido contrário

Os autores do Minitron retreinam base models podados a partir do seu professor sem poda e testaram as direções diretamente. Em um Minitron 8B podado em profundidade, a loss de logits com forward KLD atingiu uma loss de LM de 2,155 contra 2,665 do reverse KLD (a Tabela 16 deles, apêndice A.3). No Nemotron-3 8B da geração anterior, a loss combinada deu 2,117 com forward KLD e 2,140 com reverse (Tabela 15). Eles observam que o trabalho anterior achou o reverse KLD um ajuste melhor para o supervised fine-tuning e o seguimento de instruções, que Agarwal et al. dizem que a escolha depende da tarefa e que o forward KLD é a melhor escolha para o cenário de base model deles (seção 4).

Então a evidência não é uma regra única. O reverse KL tem o apoio dos resultados de instruction tuning em alunos pequenos no GKD, e o forward KL tem o apoio do retreinamento de base models no Minitron. Ambos são artigos isolados sobre os seus próprios modelos.

## Prática

1. ▢ Na execução com dois modos, qual aluno o forward KL prefere, e qual o reverse KL prefere?

<details markdown="1"><summary>Dica</summary>

Pergunte qual aluno pôs alguma probabilidade nos dois tokens grandes do professor e qual ignora um deles.

</details>

<details markdown="1"><summary>Verificação</summary>

O forward KL prefere o aluno espalhado (0,595 contra 1,572) e o reverse KL o comprometido (0,623 contra 1,273). O forward KL pune o aluno comprometido por um q próximo de 0,01 onde p é 0,49. O reverse KL pune o aluno espalhado por pôr 0,25 onde p é 0,01.

</details>

2. ▢ Qual é o argumento do artigo contra o forward KL para geração aberta?

    - a) A loss não pode ser calculada a partir da distribuição completa
    - b) O aluno precisa cobrir mais modos do que consegue expressar
    - c) O gradiente sempre some quando o professor é muito confiante
    - d) Os logits do professor precisam ser suavizados para que funcione

<details markdown="1"><summary>Verificação</summary>

**b)** Um professor sobre texto tem muito mais modos do que um aluno pequeno consegue expressar, e o forward KL força o aluno a cobri-los, então ele põe massa em regiões que o professor considera vazias. Não é (a): as duas direções podem ser calculadas a partir das distribuições completas. Não é (c): essa é a observação da lição 2 sobre probabilidades pequenas, um problema diferente. Não é (d): a temperatura é uma escolha separada da direção.

</details>

3. ▢ Usando a tabela de JSD, qual aluno a JSD(0,9) prefere, e isso combina com a afirmação do GKD de que beta perto de 1 se comporta como o reverse KL?

<details markdown="1"><summary>Verificação</summary>

O aluno comprometido (0,058 contra 0,091), e sim: o reverse KL também o prefere. Com beta = 0,1, o aluno espalhado vence, como o forward KL faria. A tabela é uma verificação de brinquedo da descrição do artigo, não um resultado de uma execução de treinamento.

</details>

4. ▢ A Tabela 16 do Minitron dá uma loss de LM de 2,155 com forward KLD e 2,665 com reverse KLD para um aluno de 8B podado em profundidade. Isso contradiz o MiniLLM e o GKD?

<details markdown="1"><summary>Verificação</summary>

Não, não diretamente. O MiniLLM e o GKD relatam resultados de seguimento de instruções e de resumo em alunos pequenos, com a direção reversa muitas vezes sobre sequências amostradas pelo aluno. O Minitron retreina um base model podado em uma mistura ao estilo de pré-treinamento e mede a loss de LM. O cenário difere na tarefa, no ponto de partida do aluno e na métrica, então a evidência apoia uma escolha que depende da tarefa, como o GKD diz. Teste as duas na sua própria tarefa antes de se comprometer.

</details>

5. ▢ Qual divergência é surda a uma probabilidade minúscula do professor, como na lição 2, e qual pune o aluno pela massa posta ali?

<details markdown="1"><summary>Verificação</summary>

O forward KL é quase surdo a uma probabilidade minúscula do professor porque p multiplica a razão de logs, que é o problema da lição 2. O reverse KL pune a massa do aluno posta onde o professor tem quase nenhuma, porque q multiplica a razão de logs. As duas direções respondem a perguntas opostas sobre o mesmo número pequeno.

</details>

## Prática no mundo real

- [ ] Rode o trecho e depois mude o professor para `[0.45, 0.05, 0.05, 0.45]` e veja se as preferências das duas direções mudam.
- [ ] Abra o Apêndice A.7 do artigo do GKD e leia a legenda da figura sobre KL que busca modos contra KL que cobre modos. Escreva uma frase sobre o que o aluno unimodal faz sob cada direção.
- [ ] Amanhã: sem consultar anotações, diga qual direção cada um entre MiniLLM, GKD e Minitron recomenda e para qual cenário.

## Para ir além

- [Losses de Destilação](../reference/distillation-losses.md)
- [Artigo científico: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Documentação: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
