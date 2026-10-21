---
title: "22. Aluno contra professor"
description: "Medir a concordância com o professor separadamente da qualidade na tarefa, uma capacidade por vez"
type: lesson
---

# Lição 22. Aluno contra professor

**Ligação com a missão:** A missão pede que você meça o que um aluno perdeu em relação ao seu professor, e o primeiro passo é parar de tratar "concorda com o professor" e "faz bem a tarefa" como um único número.
**Fonte principal:** [Artigo científico: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), seções 3.2 e 4 a 5
**Pré-requisitos:** [Lição 17](0017-fidelity-and-generalization.md), [Lição 18](0018-the-imitation-gap.md), [Fidelidade](../GLOSSARY.md), [Concordância top-1](../GLOSSARY.md), [Lacuna de imitação](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 17 disse que um aluno que generaliza bem ainda pode discordar do seu professor. De qual das duas a lição disse que você precisa, e o que decide isso?

<details markdown="1"><summary>Verificação</summary>

Depende do que o aluno é para ser. Se você precisa que o comportamento do professor seja reproduzido, como em uma substituição de que outros dependem, a fidelidade é o objetivo. Se você precisa de um modelo que faça bem a tarefa, o objetivo é a qualidade na tarefa, e um aluno pode superar um professor com falhas discordando dele. Nenhuma das duas substitui a outra.

</details>

2. ▢ A lição 18 deu a lacuna de imitação. O que um aluno imita mais rápido, e o que uma avaliação de preferência humana recompensa?

<details markdown="1"><summary>Verificação</summary>

Ele imita mais rápido o estilo: respostas fluentes, confiantes e bem estruturadas. Uma avaliação de preferência recompensa como uma resposta se lê, então um aluno pode pontuar bem nela enquanto fica para trás em capacidade. A capacidade é mais lenta de copiar.

</details>

3. ▢ A lição 21 calculou o custo de uma passagem de pontuação do professor. Qual quantidade por token dessa passagem você também precisaria para medir a fidelidade, e que custo extra usá-la acrescenta?

<details markdown="1"><summary>Verificação</summary>

A distribuição de saída do professor (ou a sua escolha de topo) em cada posição, que a passagem de pontuação já produz. Medir a fidelidade significa rodar o professor também sobre os prompts de avaliação, um pequeno custo extra diante do treinamento, porque o conjunto de avaliação é muito menor do que o conjunto de treinamento.

</details>

## Saiba isto

### Duas coisas a medir

A [fidelidade](../GLOSSARY.md) é o quão de perto as previsões de um aluno acompanham as do seu professor nas mesmas entradas. A qualidade na tarefa é o quão bem o aluno faz o trabalho, julgado contra a resposta certa. Stanton et al. definem duas métricas de fidelidade (seção 3.2), e ambas se transpõem para um modelo de linguagem posição por posição:

- **[Concordância top-1](../GLOSSARY.md):** a fração das entradas em que a resposta de maior probabilidade do aluno é a resposta de maior probabilidade do professor.
- **KL preditivo médio:** a divergência KL média da distribuição do professor para a do aluno, sensível a toda resposta, não apenas à de topo.

O artigo define as duas para classificadores. Aplicá-las a um LLM significa pontuar as distribuições de próximo token dos dois modelos nos mesmos prefixos de prompts held-out, que é uma adaptação desta trilha e não algo que o artigo executou. Decida de antemão qual prefixo você usa: o texto do professor, que isola a previsão, ou a geração de cada modelo, que também mede como os dois divergem depois de escolherem palavras diferentes.

### Por que elas se separam

Stanton et al. dão três resultados que explicam por que a concordância de um aluno e a sua qualidade na tarefa podem se mover de forma independente.

Primeiro, a concordância é limitada pela acurácia. O exemplo deles (seção 3.2): dois modelos independentes que pontuam 55 por cento e 95 por cento podem concordar em no máximo 60 por cento dos pontos. Uma concordância medida de 60 por cento entre esses dois não diz nada sobre destilação. Eles acrescentam um controle exatamente por essa razão: meça também um aluno destilado do mesmo modo a partir de um professor independente e compare as duas concordâncias. Se ambos os alunos concordam com o professor mais ou menos igualmente, a concordância vem de ambos generalizarem bem, não da destilação.

Segundo, um aluno pode superar o seu professor por falhar em copiá-lo. Na autodestilação no CIFAR-100, em que o aluno tem a arquitetura do professor, a acurácia do aluno pode exceder a do professor, o que o artigo observa ser possível apenas porque a destilação falha: uma cópia perfeita não poderia fazer melhor (seções 4.1 e 4.2). Nesse experimento, elevar a fidelidade reduziu a acurácia do aluno quando o conjunto de destilação era pequeno.

Terceiro, uma fidelidade maior nem sempre compra uma acurácia maior, mesmo quando o professor é muito melhor. Na seção 5, eles dividem o CIFAR-100, destilam um aluno na própria metade de treinamento do professor (s0) e um em dados não vistos (s1). O aluno em dados não vistos concorda mais com o professor, e ainda assim o aluno nos dados do professor tem a maior acurácia de teste. O resumo do próprio artigo é que o ganho de fidelidade não se traduziu em replicar a acurácia do professor.

Eles também relatam que é difícil chegar a uma fidelidade alta de algum modo. No MNIST com o LeNet-5, o aluno chegou a mais de 99 por cento de concordância top-1 no teste (seção 4.1). No CIFAR-100 com alunos ResNet-56, a melhor concordância no teste que eles relatam é cerca de 86 por cento, com aumento mixup (seção 5).

Escopo: são em sua maioria experimentos de classificação de imagens, com classificadores de texto no apêndice. Eles mostram que as duas quantidades são separáveis. Não são medições de um LLM, e nenhum número de concordância deles é uma meta para o seu.

### Por que uma avaliação de preferência é o substituto errado

Gudibande et al. fizeram fine-tuning de modelos LLaMA de 7B e 13B parâmetros em saídas do ChatGPT e compararam dois tipos de avaliação. Crowdworkers avaliaram cerca de 70 por cento das saídas dos modelos de imitação como iguais ou melhores do que as do ChatGPT (a Figura 1 deles). Em benchmarks direcionados, os modelos de imitação fecharam pouco ou nada da distância entre o base model e o ChatGPT nas tarefas que os dados de imitação não cobriam muito.

A Tabela 1 deles mostra isso por capacidade, usando o Natural Questions como tarefa:

| Modelo | Dados de imitação | Pontuação no NQ |
|---|---|---|
| LLaMA 7B | nenhum | 17 |
| LLaMA 7B | ShareGPT-Mix (amplo) | 10 |
| LLaMA 7B | NQ-Synthetic (direcionado) | 22 |
| LLaMA 13B | nenhum | 20 |
| LLaMA 13B | ShareGPT-Mix (amplo) | 15 |
| LLaMA 13B | NQ-Synthetic (direcionado) | 27 |
| ChatGPT | não se aplica | 31 |

Os dados de imitação amplos reduziram a pontuação no NQ dos dois tamanhos, e os dados direcionados a elevaram a até quatro pontos do professor no 13B. A explicação do artigo para a diferença nas avaliações é o estilo: os modelos de imitação são fluentes e confiantes, e um avaliador sem conhecimento de domínio ou tempo para checar fatos deixa passar os erros. Eles também constataram, na Tabela 2, que o estilo das saídas ficou mais parecido com o do ChatGPT conforme mais dados de imitação foram acrescentados, que é o mesmo efeito medido no texto de saída.

A lição para a medição não é que as avaliações de preferência são inúteis. É que um único agregado, seja uma avaliação ou uma acurácia média, esconde as capacidades que se moveram em direções opostas.

### Uma capacidade por vez

Então a medição é uma grade. Escolha as capacidades que importam para você, como respostas factuais curtas, aritmética, código, seguimento de instruções e recusas. Para cada uma, calcule duas colunas: a concordância com o professor em prompts desse tipo e a qualidade na tarefa contra a resposta correta nos mesmos prompts. Um aluno pode parecer alto na primeira e baixo na segunda em algumas linhas e o inverso em outras, e o padrão é o que diz o que foi e o que não foi transferido.

| Capacidade | Concordância com o professor | Qualidade na tarefa, aluno | Qualidade na tarefa, professor | Leitura |
|---|---|---|---|---|
| Linha hipotética A | Alta | Perto do professor | Alta | Copiada bem |
| Linha hipotética B | Alta | Muito abaixo do professor | Alta | Copiou o estilo, perdeu a capacidade |
| Linha hipotética C | Baixa | Acima do professor | Moderada | Discorda, e o professor era o mais fraco |

As linhas são uma ilustração de como ler a grade, não dados de uma fonte. A lição 23 acrescenta a coluna que falta, um modelo do mesmo tamanho treinado sem destilação, que esta grade não consegue julgar sozinha.

## Prática

1. ▢ Um professor tem 90 por cento de acurácia em uma tarefa. Um modelo independente tem 70 por cento. Qual é a maior concordância top-1 que os dois podem ter, e o que isso implica para ler a pontuação de concordância de um aluno?

<details markdown="1"><summary>Dica</summary>

Dois modelos só concordam em um ponto se ambos acertam ou ambos erram. Calcule a maior sobreposição que as acurácias permitem, seguindo o exemplo de 55 e 95 do artigo.

</details>

<details markdown="1"><summary>Verificação</summary>

No máximo 80 por cento, já que a diferença de 20 pontos de acurácia os força a discordar em pelo menos 20 por cento dos pontos. Então um aluno cuja acurácia é de 70 por cento não pode mostrar concordância acima de 80 por cento com esse professor, e uma concordância de 75 por cento significa algo diferente do mesmo número para um aluno com 88 por cento. Compare a concordância de um aluno com a de um aluno independente do controle do artigo antes de tirar conclusões.

</details>

2. ▢ Um aluno tem 94 por cento de concordância top-1 com o seu professor em prompts de chat gerais e 61 por cento em prompts de aritmética de vários passos. A acurácia do professor em aritmética é de 78 por cento. O que você mede em seguida antes de dizer qualquer coisa sobre a aritmética do aluno?

<details markdown="1"><summary>Dica</summary>

O número de concordância diz com que frequência os dois coincidem, não com que frequência qualquer um dos dois acerta.

</details>

<details markdown="1"><summary>Verificação</summary>

A acurácia de aritmética do aluno contra as respostas corretas, nos mesmos prompts, mais a correção por prompt do professor. Se a acurácia do aluno é de 61 por cento e a do professor é de 78 por cento, a diferença é uma perda de capacidade. Se os dois discordam principalmente onde o professor está errado, o aluno pode estar bem. Os 94 por cento em chat dizem apenas que o estilo se transferiu, o que a lacuna de imitação prevê.

</details>

3. ▢ Qual resultado mostra mais diretamente que a fidelidade e a qualidade na tarefa podem se separar?

    - a) A concordância de um aluno com o seu professor caiu conforme um forte aumento de dados foi aplicado às suas entradas.
    - b) Um aluno treinado com mais dados de destilação chegou a uma concordância maior no teste com o seu professor.
    - c) Um aluno com a arquitetura do professor chegou à acurácia do professor em algum tamanho de dados.
    - d) Um aluno destilado de dados não vistos concordou mais com o seu professor, mas foi menos acurado.

<details markdown="1"><summary>Verificação</summary>

d). É o resultado s1 contra s0 da seção 5: fidelidade maior com acurácia de teste menor. b) mostra a fidelidade subindo com os dados, o que é esperado e não separa as duas. c) é uma afirmação apenas sobre acurácia. a) é um resultado sobre como a concordância cai sob aumento de dados, que relata uma mudança de fidelidade sem uma comparação de qualidade na tarefa.

</details>

4. ▢ Um model card diz que um modelo destilado de 3B "é avaliado como quase tão bom quanto o de 70B por avaliadores humanos". Usando Gudibande et al., liste duas perguntas de acompanhamento que você faria antes de aceitar que o aluno manteve as capacidades do de 70B.

<details markdown="1"><summary>Verificação</summary>

Quais prompts os avaliadores viram, e se algum avaliador conseguia checar fatos ou código, já que o estilo pode ganhar uma avaliação que a capacidade não ganharia. E qual é a pontuação do aluno em benchmarks direcionados por capacidade contra o professor e contra a base não destilada, incluindo tarefas que os dados de destilação mal cobriram. Uma avaliação que concorda com os benchmarks é evidência. Uma avaliação sozinha não é.

</details>

5. ▢ A lição 19 cobriu a capacidade. Um aluno iguala a resposta top-1 do professor em 97 por cento dos prompts fáceis e 52 por cento dos difíceis. Cite uma leitura que se encaixa na lacuna de capacidade e uma que não precisa dela.

<details markdown="1"><summary>Verificação</summary>

Encaixa: o aluno não tem capacidade para modelar o comportamento do professor em entradas difíceis, então a lacuna se concentra onde o professor faz mais trabalho. Não precisa dela: os prompts difíceis são poucos nos dados de destilação, então o aluno viu pouco sinal ali, e mais dados sobre eles ajudariam. As duas preveem correções diferentes, então teste acrescentando dados de prompts difíceis a uma cópia da execução e medindo de novo.

</details>

## Prática no mundo real

- [ ] Escolha dois modelos abertos pequenos que compartilham um tokenizer. Em 50 prompts, registre a escolha de topo de próximo token de cada modelo em uma posição escolhida por prompt e conte com que frequência elas coincidem.
- [ ] Abra o artigo de Gudibande et al. e encontre a Tabela 1. Escreva uma frase sobre o que as linhas de cobertura ampla dizem sobre ler uma pontuação média.
- [ ] Amanhã: sem consultar anotações, desenhe a grade de capacidades desta lição para um projeto seu, com as duas colunas, e nomeie a capacidade em que você espera que concordância e qualidade mais difiram.

## Para ir além

- [Dimensionamento e Medição](../reference/sizing-and-measuring.md)
- [Artigo científico: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), seções 3.2 e 5
- [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), seções 4.2 e 4.4
- [Evals](../../evals/): a trilha para construir o lado da qualidade na tarefa desta grade
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
