---
title: "25. Revisando uma alegação de destilação"
description: "Revisar \"o nosso modelo pequeno se iguala ao grande\" apontando o que a medição escondeu"
type: lesson
---

# Lição 25. Revisando uma alegação de destilação

**Ligação com a missão:** A missão termina com a revisão da alegação de outra pessoa de que um modelo destilado "se iguala ao professor". Uma revisão que diz "não confio nisso" é ignorada, e uma que nomeia qual parte da medição escondeu o quê, e quanto custaria descobrir, é atendida.
**Fonte principal:** [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), seções 1 e 4
**Pré-requisitos:** [Lição 22](0022-student-against-teacher.md), [Lição 23](0023-an-honest-distillation-eval.md), [Fidelidade](../GLOSSARY.md), [Lacuna de imitação](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 17 separou duas coisas em que um aluno pode ser bom. Nomeie-as e diga qual delas Stanton et al. constataram ser baixa mesmo quando o aluno poderia igualar o professor.

<details markdown="1"><summary>Verificação</summary>

[Fidelidade](../GLOSSARY.md), o quão de perto as previsões do aluno concordam com as do professor, e generalização, o quão bem o aluno se sai na tarefa. Stanton et al. relatam que uma grande discrepância entre as distribuições preditivas do professor e do aluno muitas vezes permanece mesmo quando o aluno tem capacidade para igualar o professor exatamente, e que uma generalização melhor não exige uma fidelidade melhor ([artigo](https://arxiv.org/abs/2106.05945), resumo).

</details>

2. ▢ A lição 23 listou baselines que tornam defensável um número de "se iguala ao professor". Qual baseline diz o que o professor contribuiu, em oposição ao que o tamanho e os dados do aluno teriam dado de qualquer modo?

<details markdown="1"><summary>Verificação</summary>

Um modelo do tamanho do aluno treinado sem o professor, nos mesmos dados da tarefa. Sem ele, uma boa pontuação pode ser o que qualquer aluno desse tamanho alcança, e o professor recebe crédito por um trabalho que não fez.

</details>

3. ▢ A lição 18 nomeou a lacuna de imitação. Em uma frase, o que ela diz sobre a rapidez com que um aluno fecha a lacuna no estilo em comparação com a capacidade?

<details markdown="1"><summary>Verificação</summary>

A imitação com um orçamento limitado fecha a lacuna no estilo muito mais rápido do que na capacidade, então um aluno pode soar como o seu professor muito antes de conseguir fazer o que o professor faz.

</details>

## Saiba isto

### Uma alegação tem partes

"O nosso 7B se iguala ao professor" são cinco alegações em uma frase: um modelo, uma medição, um baseline, uma população de entradas e um custo. Uma revisão a desmonta e pergunta, de cada parte, o que seria preciso para a alegação falhar. As revisões mais úteis também dizem o que está bom, para que o autor o mantenha.

### O que uma porcentagem mede: DistilBERT

Sanh et al. dizem que o DistilBERT é 40% menor e 60% mais rápido e "retém 97% das suas capacidades de compreensão de linguagem" ([artigo](https://arxiv.org/abs/1910.01108), resumo). A seção 4 e a Tabela 1 dizem o que essa frase mede: as nove tarefas do benchmark GLUE, em conjuntos de desenvolvimento, depois do fine-tuning de cada modelo, com os resultados do BERT e do DistilBERT sendo medianas de 5 execuções com seeds diferentes. Os macro-scores impressos são 79,5 para o BERT-base e 77,0 para o DistilBERT, e 77,0 sobre 79,5 é 96,9%.

Então 97% é uma razão de duas médias, em um conjunto de benchmarks, contra um professor. Por tarefa, a Tabela 1 dá um quadro diferente: o DistilBERT pontua 51,3 no CoLA contra 56,3 do BERT, que é 91,1%, e 59,9 no RTE contra 69,3, que é 86,4%. No WNLI ele pontua 56,3 contra 53,5, acima do professor. A manchete não está errada. É uma média em que duas tarefas fracas e alguns quase empates são dobrados, e um leitor cuja carga de trabalho se parece com o RTE deve ler a linha do RTE.

Três fatos a mais do artigo pertencem a uma revisão. O aluno foi inicializado a partir do professor tomando uma camada de cada duas (seção 3), que é uma escolha de design que uma alegação deve revelar. Ele foi treinado no mesmo corpus do BERT, então não há mudança entre os dados do professor e os do aluno. E o compute foi de 8 GPUs V100 por cerca de 90 horas (seção 3), com o professor já treinado e não contado nesse número.

### O que uma avaliação de preferência esconde: Gudibande et al.

Gudibande et al. fizeram fine-tuning de modelos de 1,5B a 13B de parâmetros para imitar o ChatGPT e os avaliaram de duas maneiras. Crowdworkers, cerca de 70 deles, julgaram 255 prompts held-out, e cerca de 70% das saídas dos modelos de imitação foram avaliadas como iguais ou melhores do que as do ChatGPT (seção 4, Figura 1 à esquerda). Para limitar o vazamento, eles descartaram consultas cuja pontuação BLEU contra qualquer exemplo de treinamento excedia 20%, e descartaram prompts de código e que não estavam em inglês, que os avaliadores não conseguiam julgar.

As avaliações automáticas direcionadas contaram outra história. Os autores relatam que os modelos de imitação fecharam pouco ou nada da distância entre o base model e o ChatGPT em tarefas que não eram fortemente sustentadas nos dados de imitação, e que mais dados de imitação não a fecharam, com alguns resultados, como o conhecimento factual do Natural Questions, regredindo (Figura 1 ao centro). A explicação deles é que os modelos aprenderam o estilo do ChatGPT, confiante e bem estruturado, e que avaliadores sem conhecimento de domínio ou tempo para checar fatos deixam passar os erros (seção 4.4).

Esse é o resultado de um artigo, para imitar o ChatGPT com modelos de até 13B de parâmetros. O ponto transferível não é que as avaliações de preferência são inúteis. É que uma avaliação mede o que o avaliador consegue julgar, e o que um avaliador consegue julgar em um minuto muitas vezes é estilo.

### As perguntas a fazer

| Parte da alegação | Pergunte | Por que importa |
|---|---|---|
| Tarefas | Quais tarefas, e a média está escondendo as fracas? | Os 97% do DistilBERT ficam sobre linhas de 86% e 91% |
| População | As entradas de teste são held-out, ou tiradas da distribuição de destilação? | Gudibande et al. constatam que a lacuna aparece em tarefas que os dados de imitação não sustentam |
| Baseline | Contra o quê: o professor, um modelo do mesmo tamanho treinado sem ele, o base model? | O primeiro diz a que distância, o segundo diz o que o professor acrescentou |
| Contaminação | Como os dados de teste foram mantidos fora dos prompts de destilação? | Um filtro de sobreposição por BLEU é uma resposta concreta, e uma alegação sem nenhuma é uma lacuna |
| Avaliador | Humanos, um modelo juiz ou uma métrica, e eles conseguiam checar fatos? | Um juiz ou uma multidão pode recompensar o estilo |
| Decodificação | Greedy ou amostrada, qual temperatura, a mesma para os dois modelos? | Agarwal et al. relatam que as divergências que buscam modos se saíram melhor sob amostragem por temperatura, enquanto a escolha mal importou sob decodificação greedy ([artigo](https://arxiv.org/abs/2306.13649), seção 4.1), então a decodificação pode mudar o ranking |
| Ruído | Quantas seeds, e qual o tamanho da diferença contra a dispersão entre execuções? | O DistilBERT relata medianas de 5 execuções, e muitas alegações relatam uma |
| Custo | A inferência do professor, a geração de dados e a filtragem estão contadas? | As 90 horas de GPU do DistilBERT excluem o pré-treinamento do professor |

Duas das linhas são perguntas sobre o que falta no texto, não sobre o que há de errado nele. Trate uma resposta ausente como um item em aberto, não como uma falha: anote-a e peça por ela.

### Escrevendo a revisão

Diga primeiro o que está bom. Enuncie cada parte escondida como um custo: "a média esconde as tarefas em que caiu 10 pontos ou mais" é concreto, e "não confio na média" não é. Depois nomeie a medição que resolveria a questão, com o seu preço, para que o autor possa dizer sim ou não. Os baselines, as tarefas held-out e as verificações de contaminação da lição 23 são as respostas usuais.

## Prática

1. ▢ Preveja quais duas das nove tarefas do GLUE do DistilBERT têm a menor razão aluno para professor e depois rode isto nos números da Tabela 1.

    ```python
    bert = dict(CoLA=56.3, MNLI=86.7, MRPC=88.6, QNLI=91.8, QQP=89.6,
                RTE=69.3, SST2=92.7, STSB=89.0, WNLI=53.5)
    distil = dict(CoLA=51.3, MNLI=82.2, MRPC=87.5, QNLI=89.2, QQP=88.5,
                  RTE=59.9, SST2=91.3, STSB=86.9, WNLI=56.3)
    for task in sorted(bert, key=lambda t: distil[t] / bert[t]):
        print(f"{task:5s} {100 * distil[task] / bert[task]:.1f}")
    print(f"mean of entries {sum(bert.values()) / 9:.1f} and {sum(distil.values()) / 9:.1f}")
    ```

<details markdown="1"><summary>Dica</summary>

Procure as tarefas em que o professor pontuou muito abaixo de 100 e o aluno caiu mais ainda.

</details>

<details markdown="1"><summary>Verificação</summary>

RTE com 86,4 e CoLA com 91,1 são as menores, e WNLI com 105,2 é a maior. A última linha imprime 79,7 e 77,0. O artigo imprime 79,5 para o BERT-base, perto da média das suas próprias nove entradas mas não igual a ela, e não consegui estabelecer o motivo. Qualquer um dos números dá cerca de 97% no geral, que é o ponto: recalcule uma manchete a partir da tabela antes de citá-la.

</details>

2. ▢ Um artigo relata que crowdworkers avaliaram cerca de 70% das saídas de um aluno como iguais ou melhores do que as do seu professor. O que você conclui sobre a capacidade, e o que você pediria?

<details markdown="1"><summary>Verificação</summary>

Nada firme sobre a capacidade. Em Gudibande et al., o mesmo tipo de avaliação coexistiu com pouco fechamento da lacuna em tarefas que os dados de imitação não sustentavam, porque os avaliadores recompensam o estilo que o aluno copiou. Peça avaliações automáticas direcionadas em tarefas held-out, e avaliadores ou uma verificação que consigam checar fatos.

</details>

3. ▢ Alegação hipotética: "O nosso aluno de 7B se iguala ao professor. Em 500 prompts, um modelo juiz preferiu o aluno ou empatou em 62% das comparações." Os prompts vieram do mesmo gerador dos prompts de destilação, a decodificação foi greedy para o aluno e amostrada para o professor, e o custo não é informado. Liste as perguntas que você faria, primeiro as que mais mudam a decisão.

<details markdown="1"><summary>Verificação</summary>

Primeiro, a população: prompts do gerador de destilação estão na distribuição, então peça tarefas held-out. Segundo, a decodificação: os dois modelos devem ser decodificados do mesmo jeito, porque a configuração pode mudar o ranking. Terceiro, o juiz: qual modelo, verificado quanto a viés de estilo, e uma taxa de empate separada da preferência. Quarto, o baseline: um modelo do mesmo tamanho treinado sem o professor. Por último, o custo: a geração e a filtragem do professor contadas. Diga também o que está bom: uma comparação julgada com 500 prompts é um primeiro olhar razoável.

</details>

4. ▢ Qual verificação é evidência de que os prompts de destilação não vazaram para o conjunto de teste?

    - a) Um juiz maior dando uma pontuação mais alta
    - b) Um filtro de sobreposição nos prompts de teste
    - c) Tirar a média das pontuações de várias seeds
    - d) Uma execução mais longa em saídas do professor

<details markdown="1"><summary>Verificação</summary>

**b)** Ele verifica a coisa em questão, como Gudibande et al. fizeram com um filtro BLEU de 20% contra qualquer exemplo de treinamento. (a) e (c) mudam como a pontuação é julgada ou calculada em média, não se as entradas foram vistas. (d) não testa sobreposição, e mais dos mesmos prompts pode aumentá-la.

</details>

5. ▢ Dois artigos comparam forward e reverse KL para alunos. Um avalia com decodificação greedy e encontra pouca diferença, o outro amostra com temperatura alta e encontra o reverse KL claramente melhor. Os dois podem estar certos, e o que você verifica primeiro?

<details markdown="1"><summary>Verificação</summary>

Sim. Agarwal et al. relatam que as divergências que buscam modos se saíram melhor sob amostragem por temperatura e que a escolha mal importou sob decodificação greedy, que é a mesma divisão. Verifique primeiro a configuração de decodificação de cada avaliação, depois a tarefa e os tamanhos de modelo, antes de tratar os dois como uma contradição.

</details>

## Prática no mundo real

- [ ] Encontre um model card ou post de blog que alegue que um modelo pequeno se iguala a um grande e escreva uma linha para cada linha da tabela de perguntas: a resposta que o post dá, ou "não informado".
- [ ] Recalcule uma porcentagem de uma tabela de resultados nesse post, usando os próprios números da tabela, e escreva se ela se reproduz.
- [ ] Amanhã: escreva a revisão dessa alegação em cinco frases, começando pelo que está bom e terminando com a única medição que você pediria.

## Para ir além

- [Checklist de Revisão de Destilação](../reference/distillation-review-checklist.md)
- [Dimensionamento e Medição](../reference/sizing-and-measuring.md)
- [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Artigo científico: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
