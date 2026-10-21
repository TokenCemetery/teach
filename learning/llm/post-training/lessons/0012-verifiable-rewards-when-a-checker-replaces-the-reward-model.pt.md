---
title: "12. Recompensas verificáveis: quando um verificador substitui o reward model"
description: "Um reward model treinado é um palpite sobre o que um humano preferiria; um teste unitário ou uma resposta que confere não é palpite nenhum"
type: lesson
---

# Lição 12. Recompensas verificáveis: quando um verificador substitui o reward model

**Ligação com a missão:** "Explicar a vantagem relativa ao grupo no GRPO e por que uma recompensa verificável (um teste unitário, uma resposta matemática conferida) muda o que o treinamento de RL pode ter como alvo" é o quinto item de O sucesso se parece com isto, e esta lição o encerra.
**Fonte principal:** [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Pré-requisitos:** [Lição 11](0011-grpo-group-relative-advantage-instead-of-a-value-function.md), [Recompensa verificável](../GLOSSARY.md)

## Aquecimento

1. ▢ Um grupo de 4 saídas amostradas para a mesma pergunta recebe as recompensas `{2, 4, 6, 8}`. Quais saídas recebem uma vantagem relativa ao grupo positiva e quais recebem uma negativa?

<details markdown="1"><summary>Verificação</summary>

A média é 5; as saídas com pontuação 6 e 8 ficam acima dela e recebem vantagem positiva, as saídas com pontuação 2 e 4 ficam abaixo dela e recebem vantagem negativa.

</details>

2. ▢ Por que Shao et al. descrevem a comparação relativa ao grupo como adequada a reward models de forma especial?

<details markdown="1"><summary>Verificação</summary>

Reward models costumam ser treinados, desde o início, em comparações entre saídas para a mesma pergunta, então pontuar várias saídas para uma pergunta e compará-las entre si pede ao reward model o mesmo tipo de julgamento relativo que ele foi de fato treinado para fazer.

</details>

## Saiba isto

### O que o GRPO realmente precisa de uma recompensa

Nada na vantagem relativa ao grupo da lição 11 exige que a pontuação de cada saída amostrada venha especificamente de um reward model treinado. Tudo de que a fórmula de normalização pelo grupo, `A_i = (r_i - mean(r)) / std(r)`, precisa é de um número por saída amostrada, de `r_1` a `r_G`, que reflita o quão boa cada uma foi. Um reward model treinado é um jeito de produzir esse número, o jeito do próprio treinamento com GRPO de Shao et al. Não é o único jeito.

### O que é uma recompensa verificável

Uma **recompensa verificável** é um sinal de recompensa produzido por um verificador determinístico em vez de por um modelo aprendido: se um trecho de código gerado passa em um teste unitário fixo, se a resposta numérica final de um problema de matemática coincide exatamente com a correta conhecida, se uma prova ou um programa gerado satisfaz uma verificação formal. Nada no cálculo de uma recompensa verificável envolve adivinhar o que um humano teria preferido; é um fato direto e checável sobre a saída, calculado do mesmo jeito toda vez, sem nenhum modelo de preferência entre a saída e a sua pontuação.

### Por que isso muda o que o treinamento de RL pode ter como alvo

Um reward model treinado, por melhor que seja o treinamento, ainda está ajustando um julgamento de preferência: a lição 5 cobriu diretamente como uma policy pode encontrar jeitos de pontuar bem contra ele sem produzir de fato o comportamento que ele pretendia recompensar. Uma recompensa verificável não tem um modo de falha análogo a esse: um teste unitário passa ou não passa, e não há uma peculiaridade específica de reward model para uma policy aprender a explorar, porque não há nenhum modelo aprendido fazendo as vezes do julgamento. Isso abre o treinamento de RL a alvos que antes eram difíceis de alcançar só por meio de preferência humana: uma policy pode ser empurrada, grupo amostrado a grupo amostrado, em direção a saídas que são com mais frequência exatamente corretas, de forma verificável, em tarefas como matemática e código, e não apenas mais frequentemente preferidas por um juiz (humano ou modelo) que faz um julgamento subjetivo.

### O que isso não muda

Uma recompensa verificável não é uma melhoria gratuita em relação a um reward model treinado em todos os aspectos; ela só se aplica onde existe de fato uma verificação de correção. Boa parte do comportamento que o pós-treinamento deve moldar (utilidade, tom, segurança, qualidade de escrita aberta) não tem verificador determinístico que possa substituir um julgamento de preferência humano ou de modelo; não existe teste unitário para "esta resposta foi adequadamente empática". As recompensas verificáveis servem especificamente a tarefas em que a correção é verificável desde o início, e é por isso que matemática e código são os domínios em torno dos quais essa combinação é construída, e não uma substituição geral da modelagem de recompensa baseada em preferência em todos os outros lugares.

## Prática

1. ▢ Uma equipe quer treinar uma policy para resolver problemas de álgebra em texto usando GRPO. Em vez de treinar um reward model com preferências humanas entre soluções, o que ela poderia usar, e por que isso evitaria o risco de reward hacking que a lição 5 descreveu?

<details markdown="1"><summary>Verificação</summary>

Uma recompensa verificável: checar se a resposta numérica final da policy coincide exatamente com a resposta correta conhecida. Isso evita o reward hacking no sentido do reward model porque não há peculiaridades de um modelo aprendido a explorar; a checagem é um fato direto e determinístico sobre a saída, e não um julgamento treinado que uma policy poderia aprender a burlar.

</details>

2. ▢ Por que uma recompensa verificável seria uma má escolha para treinar uma policy a escrever respostas de suporte ao cliente mais empáticas?

    - a) Recompensas verificáveis só podem ser calculadas para saídas numéricas
    - b) Não há verificador determinístico para "esta resposta foi adequadamente empática"; a correção desse tipo não é o tipo de propriedade que um verificador consegue testar
    - c) Recompensas verificáveis sempre exigem um reward model separado para interpretá-las
    - d) O GRPO não pode ser usado com recompensas verificáveis

<details markdown="1"><summary>Verificação</summary>

**b)** é a limitação real: as recompensas verificáveis servem a tarefas em que a correção é verificável desde o início, e o tom empático não tem uma checagem determinística assim. A alternativa (a) é estreita demais; a correção de código é um exemplo não numérico que ainda é verificável. A alternativa (c) contradiz todo o ponto de uma recompensa verificável, que não precisa de nenhum reward model. A alternativa (d) é falsa; a maquinaria de normalização pelo grupo do GRPO funciona com qualquer pontuação por saída, verificável ou produzida por um modelo.

</details>

3. ▢ Usar uma recompensa verificável muda algo na forma como a vantagem relativa ao grupo da lição 11 é calculada?

<details markdown="1"><summary>Verificação</summary>

Não. A mesma normalização, subtrair a média do grupo e dividir pelo desvio padrão do grupo, se aplica independentemente de a pontuação por saída subjacente, `r_i`, ter vindo de um reward model treinado ou de um verificador determinístico. O que muda é apenas de onde essa pontuação vem, e não o que o GRPO faz com ela.

</details>

## Prática no mundo real

- [ ] Encontre uma configuração de treinamento de RL para raciocínio publicada (um artigo, relatório técnico ou script de treinamento aberto) e identifique exatamente o que a sua recompensa verificável checa: uma resposta com correspondência exata, uma suíte de testes unitários, um verificador formal de provas ou outra coisa.
- [ ] Escolha uma tarefa que você acha plausível para recompensas verificáveis (uma tarefa de programação, um conjunto de problemas de matemática) e uma que você acha implausível (uma tarefa aberta de escrita ou conversação) e escreva uma frase para cada uma explicando o que um verificador determinístico conseguiria ou não testar.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a etapa 7: se as recompensas verificáveis permitem que o treinamento de RL empurre uma policy a ser com mais frequência exatamente correta, que tipo de comportamento novo do modelo você esperaria que surgisse de treinar intensamente em problemas de matemática e código dessa forma, além de simplesmente acertar mais respostas?

## Para ir além

- [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

A etapa 6 cobriu o mecanismo (a vantagem relativa ao grupo) e a recompensa que combina especialmente bem com ele (checagens verificáveis). A etapa 7 cobre o que acontece quando essa combinação é ampliada como a principal forma de treinar um modelo: os modelos de raciocínio, e o que o treinamento com recompensas verificáveis em escala de fato produz.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
