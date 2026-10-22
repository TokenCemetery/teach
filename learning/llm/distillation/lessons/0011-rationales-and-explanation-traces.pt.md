---
title: "11. Rationales e traces de explicação"
description: "Treinar no raciocínio do professor além das suas respostas, como fizeram o Distilling Step-by-Step e o Orca"
type: lesson
---

# Lição 11. Rationales e traces de explicação

**Ligação com a missão:** A missão pede que você construa um conjunto de destilação que valha a pena treinar, e a coisa mais rica que um professor pode escrever para uma entrada é o seu raciocínio, que o aluno pode usar como sinal de treinamento ou como armadilha.
**Fonte principal:** [Artigo científico: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
**Pré-requisitos:** [Lição 10](0010-distilling-from-generated-data.md), [Rationale](../GLOSSARY.md), [Professor assistente](../GLOSSARY.md), [Lacuna de capacidade](../GLOSSARY.md)

## Aquecimento

1. ▢ O filtro do Self-Instruct mantém uma nova instrução apenas sob uma condição sobre o ROUGE-L. Enuncie-a.

<details markdown="1"><summary>Verificação</summary>

A sua similaridade ROUGE-L com qualquer instrução já no pool precisa ser menor que 0,7. A regra é sobre o membro existente mais próximo, o que impede que o pool se encha de quase cópias (lição 10).

</details>

2. ▢ A destilação a partir de dados gerados é destilação em nível de sequência com uma escolha extra. Qual é a escolha?

<details markdown="1"><summary>Verificação</summary>

As entradas. Na lição 8, as entradas eram um conjunto de treinamento fixo; aqui o conjunto-semente, o prompt e o filtro determinam quais entradas existem (lição 10).

</details>

3. ▢ O que é um [professor assistente](../GLOSSARY.md), e que problema ele pretende amenizar?

<details markdown="1"><summary>Verificação</summary>

Um modelo de tamanho intermediário, destilado a partir do professor e depois usado como professor de um aluno menor. Ele pretende amenizar a [lacuna de capacidade](../GLOSSARY.md): a queda de qualidade do aluno que pode aparecer quando o professor é muito maior que o aluno.

</details>

## Saiba isto

### Um rationale é um alvo extra

Um [rationale](../GLOSSARY.md) é o raciocínio intermediário que um professor escreve antes da sua resposta. Os rótulos sozinhos dizem ao aluno qual é a resposta. Um rationale também mostra como o professor chegou a ela, o que dá ao aluno mais com o que aprender em cada exemplo.

O Distilling Step-by-Step (Hsieh et al., 2023) usa rationales de uma maneira particular. Ele dá a um modelo grande alguns exemplos resolvidos, cerca de 10 por tarefa, para que escreva um rationale junto com o seu rótulo, aqui o modelo PaLM de 540B (seção 3.1 e a seção de limitações). Depois treina um modelo pequeno, T5, para produzir os dois.

### Rationales como uma segunda tarefa, não como uma entrada

Há duas maneiras óbvias de usar um rationale. Eles escolheram a segunda.

1. **Como entrada.** Treinar o aluno para prever o rótulo a partir do texto mais o rationale. Isso exige que um modelo grande escreva um rationale também na hora do teste, então o modelo grande ainda é necessário em produção (seção 3.2).
2. **Como uma segunda saída.** Treinar o aluno para produzir o rótulo e, como uma tarefa separada, o rationale. A loss é a loss do rótulo mais um peso vezes a loss do rationale. Um prefixo de tarefa diz ao modelo qual produzir: um prefixo `[label]` na entrada pede o rótulo, um prefixo `[rationale]` pede o rationale (seção 3.2).

O segundo design significa que nenhum rationale é gerado na hora do teste: o aluno só prevê o rótulo, e a tarefa de escrever o rationale moldou o que ele aprendeu pelo caminho. O custo é um pouco de compute de treinamento extra.

Tratar o rationale como uma segunda tarefa importa. Quando os autores, em vez disso, concatenaram o rationale e o rótulo em uma única sequência-alvo, o aluno às vezes se saiu pior do que o fine-tuning simples (Tabela 2, T5 de 220M, acurácia):

| Método | e-SNLI | ANLI | CQA | SVAMP |
|---|---|---|---|---|
| Fine-tuning padrão | 88,38 | 43,58 | 62,19 | 62,63 |
| Tarefa única, rationale e rótulo juntos | 88,88 | 43,50 | 61,37 | 63,00 |
| Multitarefa, rótulo e rationale separados | 89,51 | 49,58 | 63,29 | 65,50 |

No ANLI e no CQA, a linha de tarefa única fica abaixo do fine-tuning padrão. A leitura deles é que os rationales precisam ser tratados com cuidado para serem úteis.

### O que isso rendeu

Estes são os resultados do artigo em quatro benchmarks, três tipos de tarefa, alunos T5 e um professor PaLM:

- **Menos dados.** Com um T5 de 220M e rótulos humanos, o distilling step-by-step superou o fine-tuning padrão no conjunto e-SNLI completo usando apenas 12,5% dele. As reduções nos exemplos de treinamento necessários para superar o fine-tuning padrão com todos os dados foram de 75% no ANLI, 25% no CQA e 20% no SVAMP (seção 4.1). Só com dados sem rótulo, 12,5% do conjunto e-SNLI sem rótulo bastaram para superar a destilação de tarefa padrão sobre todo ele.
- **Menor que o professor.** Um T5 de 770M com fine-tuning superou o PaLM de 540B com few-shot prompting no ANLI usando 80% do conjunto de treinamento, enquanto o fine-tuning padrão do mesmo T5 não conseguiu igualar o PaLM nem com 100% (resumo; seção 4.3, Figura 8). No e-SNLI, um modelo de 220M conseguiu isso com 0,1% dos dados.
- **Uma fonte de rationale mais fraca ainda ajudou.** Os rationales de um GPT-NeoX de 20B deram uma melhora menor do que os do PaLM (ANLI 48,15 contra 49,58, fine-tuning padrão 43,58) (Tabela 1).

Mantenha os limites em vista. Os benchmarks são tarefas de classificação e de resposta curta, os alunos são modelos T5 específicos de tarefa e não modelos de chat, e o ponto de comparação é um PaLM com prompt. Nada disso diz o que acontece quando você destila um assistente geral. O artigo também observa que o seu few-shot prompting precisa de demonstrações de exemplo para cada tarefa.

### Orca: traces de explicação em escala de assistente

O Orca (Mukherjee et al., 2023) aplica o mesmo instinto ao seguimento geral de instruções. A sua motivação é que um aluno treinado apenas nas respostas finais de um professor aprende pouco de como o professor pensou. Duas ideias:

- **Explanation tuning com mensagens de sistema.** Cada exemplo de treinamento é uma tripla de mensagem de sistema, consulta do usuário e resposta do professor. Eles escreveram à mão 16 mensagens de sistema que evocam estilos de resposta diferentes, como pedir ao modelo que pense passo a passo e justifique os seus passos, e as amostraram entre tarefas tiradas da coleção FLAN-v2 (seção 3.1).
- **O ChatGPT como professor intermediário.** Eles coletaram 5 milhões de respostas do ChatGPT (FLAN-5M), depois pegaram 1 milhão dessas consultas para respostas do GPT-4 (FLAN-1M) e treinaram o Orca primeiro nos dados do ChatGPT e depois nos do GPT-4. As razões declaradas são a lacuna de capacidade, já que um aluno de 13B é muito menor que o GPT-4, e custo e tempo: eles coletaram 5 vezes mais do ChatGPT do que do GPT-4 (seção 3.1.3).

Isso é um [professor assistente](../GLOSSARY.md) usado de propósito, com um currículo de 5M e depois 1M. Os autores relatam o Orca-13B acima do Vicuna-13B por mais de 100% no Big-Bench Hard e por 42% no AGIEval, em paridade com o ChatGPT no BBH e cerca de 4 pontos atrás do ChatGPT em exames profissionais ao usar uma mensagem de sistema otimizada (resumo). Eles também relatam que o Vicuna parece próximo do ChatGPT sob um juiz GPT-4 (92%), mas retém apenas 64% nos exames e 48% no BBH contra rótulos humanos, e é por isso que avaliaram em benchmarks de raciocínio.

Essas são as avaliações dos próprios autores do Orca, nos benchmarks que eles escolheram. Se os traces de explicação fecham uma lacuna de capacidade, ou principalmente a lacuna de estilo, é a pergunta da lição 18.

### Modelos de raciocínio pertencem à próxima trilha

Destilar um modelo de raciocínio, por fine-tuning nas suas longas chains of thought, é ensinado na trilha de [Pós-treinamento](../../post-training/). Os rationales aqui são explicações curtas que ajudam um modelo pequeno de tarefa, e a destilação de modelos de raciocínio é um caso maior da mesma ideia.

## Prática

1. ▢ No Distilling Step-by-Step, por que o rationale não é necessário na hora do teste?

    - a) O rationale fica escondido dentro do próprio token do rótulo
    - b) O aluno memoriza todo rationale do conjunto de treinamento
    - c) O professor escreve cada rationale de novo em produção
    - d) A tarefa do rótulo roda sozinha depois que o modelo é treinado

<details markdown="1"><summary>Verificação</summary>

**d)** O rationale é uma segunda saída com o seu próprio prefixo, treinada junto com o rótulo, então na hora do teste você pede apenas o rótulo. (b) não é o que o método faz. (c) descreve o design rejeitado em que o rationale é uma entrada, que mantém o modelo grande em produção. (a) inventa um mecanismo que o artigo não tem.

</details>

2. ▢ Na Tabela 2, a linha de tarefa única para o CQA é 61,37 e o fine-tuning padrão é 62,19. O que isso diz sobre acrescentar rationales de forma ingênua?

<details markdown="1"><summary>Verificação</summary>

Acrescentar o rationale ao alvo como uma única sequência deixou o aluno pior do que não fazer nada no CQA (e ligeiramente pior no ANLI, 43,50 contra 43,58). O ganho vem de como o rationale é usado, como uma tarefa separada, e não de ter rationales em si. Esse é o resultado do artigo no seu cenário.

</details>

3. ▢ Um aluno recebe 5 milhões de respostas do ChatGPT e depois 1 milhão de respostas do GPT-4. Qual é a razão, e que duas razões os autores dão para a ordem e o tamanho?

<details markdown="1"><summary>Verificação</summary>

5 para 1. Eles dão a lacuna de capacidade, já que um professor intermediário mais próximo da capacidade do aluno facilita a imitação, e custo e tempo, já que o ChatGPT era mais rápido e barato de consultar, então coletaram 5 vezes mais dele do que do GPT-4.

</details>

4. ▢ A sua equipe lê o resultado do T5 de 770M contra o PaLM de 540B e propõe destilar um assistente de chat geral do mesmo jeito, com um modelo de 770M. O que você responde?

<details markdown="1"><summary>Dica</summary>

Olhe o tipo de tarefa, o tipo de aluno e o que é a comparação.

</details>

<details markdown="1"><summary>Verificação</summary>

O resultado é para quatro benchmarks, com alunos T5 específicos de tarefa e um PaLM com few-shot prompting como baseline, e o número de 80% dos dados é para o ANLI. Ele não cobre um assistente geral. Uma proposta para um modelo de chat precisa da sua própria avaliação nas tarefas que importam para você, contra um baseline treinado sem os rationales.

</details>

5. ▢ Um professor escreve um rationale confiante mas errado e um rótulo errado. Qual dos dois métodos desta lição treinaria o aluno em ambos, e o que você faria antes de treinar?

<details markdown="1"><summary>Verificação</summary>

Ambos treinariam: o rationale e o rótulo são alvos no Distilling Step-by-Step, e um trace de explicação faz parte da resposta no Orca. Filtre primeiro. Onde existir um verificador, mantenha apenas os exemplos cuja resposta seja verificada como correta; caso contrário, amostre e inspecione. A lição 12 cobre isso.

</details>

## Prática no mundo real

- [ ] Encontre a Tabela 2 no artigo do Orca e leia as 16 mensagens de sistema. Escolha três e preveja como a mesma consulta seria respondida de forma diferente sob cada uma.
- [ ] Escreva um prompt de rationale para uma tarefa que você conhece, com dois exemplos resolvidos, e rode-o em qualquer modelo disponível para você. Confira à mão um rationale em busca de um erro que a resposta final esconde.
- [ ] Amanhã: sem consultar anotações, explique por que o rationale é uma segunda saída e não uma entrada, e o que isso faz com o custo na hora do teste.

## Para ir além

- [Sequência e Dados Sintéticos](../reference/sequence-and-synthetic-data.md)
- [Artigo científico: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
- [Artigo científico: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
- [Pós-treinamento](../../post-training/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
