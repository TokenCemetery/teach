---
title: "10. Destilando a partir de dados gerados"
description: "Construir um conjunto de instruções a partir das gerações de um professor, como fizeram o Self-Instruct e o Alpaca"
type: lesson
---

# Lição 10. Destilando a partir de dados gerados

**Ligação com a missão:** A missão pede que você destile a partir dos dados gerados por um professor, o que significa construir as entradas além de coletar as saídas, e saber quanto custa a construção.
**Fonte principal:** [Artigo científico: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
**Pré-requisitos:** [Lição 9](0009-token-or-sequence.md), [Dados sintéticos](../GLOSSARY.md), [Destilação em nível de sequência](../GLOSSARY.md), [Professor](../GLOSSARY.md), [Aluno](../GLOSSARY.md)

## Aquecimento

1. ▢ Na receita de Kim e Rush, de onde vinham as entradas, e o que o professor acrescentou?

<details markdown="1"><summary>Verificação</summary>

As entradas eram as frases de treinamento já existentes. O professor acrescentou apenas as saídas: a sua tradução por beam search de cada entrada. O aluno treinou nesses pares de entrada e saída (lição 8).

</details>

2. ▢ Um professor fica atrás de uma API e devolve apenas texto. Qual nível de destilação está aberto para você?

<details markdown="1"><summary>Verificação</summary>

O nível de sequência, no texto que você consegue coletar (lição 9). O nível de token precisa da distribuição do professor em cada posição, que o texto sozinho não dá.

</details>

## Saiba isto

### A destilação a partir de dados gerados é destilação em nível de sequência com mais uma escolha

Na lição 8, as entradas eram dadas: o conjunto de treinamento de uma tarefa de tradução. Para um modelo geral de instruções, não há um conjunto fixo de entradas. Alguém precisa escrever os prompts.

A destilação a partir de dados gerados é [destilação em nível de sequência](../GLOSSARY.md) em que você também escolhe as entradas. O professor escreve os prompts, ou você escreve, o professor escreve as respostas e o aluno treina com cross-entropy comum nos pares. Tudo sobre o que o aluno recebe é decidido por esses dados: um aluno só consegue aprender comportamentos que os pares mostram.

### Self-Instruct: o pipeline

O Self-Instruct (Wang et al., 2022) constrói um conjunto de instruções a partir das próprias gerações de um modelo, começando de 175 tarefas-semente escritas por humanos, cada uma com uma instrução e uma instância. Ele tem quatro passos (seção 2.2):

1. **Gerar instruções.** Amostre 8 instruções do pool de tarefas como exemplos in-context, 6 delas escritas por humanos e 2 geradas em rodadas anteriores, e peça ao modelo novas.
2. **Classificar a tarefa.** Pergunte ao modelo, com alguns exemplos (12 instruções-semente de classificação e 19 de não classificação), se a instrução é uma tarefa de classificação, isto é, uma com um conjunto pequeno e limitado de saídas.
3. **Gerar instâncias.** Para a maioria das tarefas, a entrada primeiro: escreva uma entrada e depois a saída. Para tarefas de classificação, a saída primeiro: escreva o rótulo da classe e depois uma entrada para esse rótulo. Os autores acrescentaram isso porque a geração com a entrada primeiro produzia entradas enviesadas para um rótulo, por exemplo frases gramaticais para uma tarefa de erro gramatical.
4. **Filtrar.** Mantenha uma nova instrução apenas se a sua similaridade ROUGE-L com toda instrução já no pool for menor que 0,7. Descarte instruções com palavras-chave como image, picture ou graph que um modelo de linguagem não consegue tratar. Descarte instâncias duplicadas e instâncias com a mesma entrada mas saídas diferentes. Descarte instâncias que falham em heurísticas simples, como uma instrução longa ou curta demais, ou uma saída que apenas repete a entrada.

O loop se retroalimenta: as instruções aceitas entram no pool e viram exemplos in-context para as rodadas seguintes. As regras de filtragem são o assunto da lição 12.

O resultado, no modelo GPT-3 `davinci`, foi de 52.445 instruções e 82.439 instâncias depois da filtragem, das quais 11.584 instruções eram tarefas de classificação (Tabela 1). O fine-tuning do GPT-3 em tudo isso custou $338 por meio do serviço de fine-tuning do provedor (apêndice A.3). O mesmo modelo gerou os dados e depois passou por fine-tuning neles, então o professor e o aluno partiram de um único modelo.

A avaliação deles, em tarefas não vistas do SuperNI medidas por ROUGE-L (Tabela 3): o GPT-3 puro pontuou 6,8, o modelo Self-Instruct 39,9 e o modelo ajustado por instruções da OpenAI, InstructGPT001, 40,8. Os autores leem isso como um ganho de 33,1 pontos que quase iguala o InstructGPT001. É o resultado deles no benchmark e na métrica deles.

### Alpaca: a mesma receita em escala menor

A equipe do Stanford CRFM construiu o Alpaca a partir da ideia do Self-Instruct, mas mudou o professor e o aluno (post do blog do Alpaca, "Training recipe"):

- Eles partiram dos mesmos 175 pares-semente e pediram ao text-davinci-003 da OpenAI que gerasse mais.
- Eles simplificaram o pipeline de geração em relação ao Self-Instruct e dizem que isso reduziu o custo.
- Os dados são 52K instruções únicas com saídas, que custaram menos de $500 pela API da OpenAI.
- Eles fizeram fine-tuning do LLaMA 7B com aprendizado supervisionado. A primeira execução levou 3 horas em 8 A100 de 80GB, que eles estimam em menos de $100 na maioria dos provedores de nuvem.

A frase-resumo deles é que o Alpaca 7B pode ser reproduzido por menos de $600. Em uma avaliação preliminar de turno único, eles relatam que ele se comporta qualitativamente de forma parecida com o text-davinci-003. Trate isso como a impressão dos autores em uma avaliação pequena, não como uma equivalência medida; a lição 18 volta a por que essas impressões podem enganar.

| | Self-Instruct | Alpaca |
|---|---|---|
| Professor | GPT-3 `davinci` (o modelo que depois passou por fine-tuning) | text-davinci-003 |
| Aluno | GPT-3 `davinci` | LLaMA 7B |
| Conjunto-semente | 175 tarefas | Os mesmos 175 pares |
| Dados | 52.445 instruções, 82.439 instâncias | 52K instruções com saídas |
| Custo declarado | $338 pelo fine-tuning | Menos de $500 pelos dados, menos de $100 pela execução |

### O que o design dos dados decide

Quatro escolhas moldam o que o aluno aprende, e cada uma é sua quando você gera dados:

- **O conjunto-semente.** Tudo é gerado a partir de 175 exemplos, então o que eles cobrem limita no que o pool cresce.
- **O prompt.** Os exemplos in-context e o template conduzem o estilo e a mistura de tarefas.
- **As configurações de amostragem.** A temperatura e configurações parecidas definem o quanto as saídas variam.
- **O filtro.** O que você mantém é o conjunto de treinamento. Um filtro fraco deixa os erros do professor virarem as lições do aluno.

Um aluno só consegue igualar o que o professor escreveu, então um erro que sobrevive ao filtro é aprendido como se fosse correto.

### As restrições vieram com os dados

O post do Alpaca é explícito em que o modelo é apenas para pesquisa acadêmica. Ele dá três razões: o LLaMA tem uma licença não comercial, os dados vêm do text-davinci-003, cujos termos proíbem desenvolver modelos que concorram com a OpenAI, e eles não haviam construído medidas de segurança adequadas. A lição 13 lê essas restrições de perto. Por ora, note que o custo dos dados foi a parte menor do que veio com eles.

## Prática

1. ▢ Os dados do Alpaca custaram menos de $500 para 52K pares de instrução e saída. Qual é o custo por exemplo, no máximo, e por que esse não é o custo total do modelo?

<details markdown="1"><summary>Verificação</summary>

Menos de $500 divididos por 52.000 dá cerca de $0,0096, menos de um centavo por exemplo. Não é o custo total: o blog conta separadamente a execução de fine-tuning (3 horas em 8 A100 de 80GB, menos de $100 na maioria das nuvens), e nenhum dos dois números conta o esforço humano das 175 sementes, a avaliação ou a demo. A lição 21 conta o custo do professor de forma adequada.

</details>

2. ▢ O Self-Instruct gera dados de classificação com a saída primeiro. Qual problema da geração com a entrada primeiro isso corrige?

    - a) As entradas saem enviesadas para um único rótulo de classe
    - b) As saídas saem muito mais longas do que qualquer resposta humana
    - c) As instruções repetem o mesmo texto de entrada sem nenhuma mudança
    - d) Os rótulos saem escritos em um formato muito inconsistente

<details markdown="1"><summary>Verificação</summary>

**a)** O exemplo do artigo: ao ser pedido para escrever uma entrada para detecção de erro gramatical, o modelo tende a escrever uma entrada gramatical, então uma classe domina. Escrever primeiro o rótulo e depois uma entrada para esse rótulo as equilibra. (b), (c) e (d) não são o problema que os autores nomeiam.

</details>

3. ▢ Uma nova instrução gerada tem similaridade ROUGE-L de 0,74 com uma instrução já no pool e 0,2 com todas as demais. O Self-Instruct a mantém, e por quê?

<details markdown="1"><summary>Dica</summary>

A regra é sobre o máximo sobre o pool, não sobre a média.

</details>

<details markdown="1"><summary>Verificação</summary>

Não. A instrução só é mantida se a sua similaridade ROUGE-L com qualquer instrução existente for menor que 0,7, e 0,74 excede isso. A regra mantém o pool diverso rejeitando uma quase cópia de qualquer membro isolado, por mais diferente que o resto do pool seja.

</details>

4. ▢ A sua equipe quer copiar o Alpaca, mas usar um professor que produz respostas curtas e secas. O que você espera que o aluno faça, e qual parte do pipeline você mudaria primeiro?

<details markdown="1"><summary>Verificação</summary>

Espere que o aluno responda no mesmo estilo seco, porque ele só consegue aprender o que os pares mostram. Mude primeiro o prompt ou as configurações do professor, já que é ali que o estilo da resposta é definido, depois rode o filtro de novo e compare uma amostra de pares gerados a olho antes de treinar. Isso é uma previsão a partir de como os dados determinam o aluno, não um resultado medido.

</details>

5. ▢ A lição 8 constatou que um aluno em nível de sequência treinado na melhor saída única de um professor acaba pontudo em torno dessa saída. Isso sugere gerar várias saídas por prompt, ou uma, e o que cada opção custaria?

<details markdown="1"><summary>Verificação</summary>

Não decide a questão. Uma saída por prompt é a abordagem em estilo de moda: barata e consistente, mas uma única amostra. Várias saídas por prompt mostram ao aluno mais da variedade do professor, a um custo de geração várias vezes maior e com mais filtragem a fazer. Kim e Rush tentaram amostrar no lugar da moda na tradução e mantiveram a moda. Esse é um resultado para a tarefa deles, então teste as duas na sua.

</details>

## Prática no mundo real

- [ ] Abra o artigo do Self-Instruct e encontre o template de prompt para geração de instruções (Tabela 5). Anote como são os exemplos in-context e quantos escritos por humanos e quantos escritos pelo modelo há.
- [ ] Abra o post do blog do Alpaca e encontre a frase que lista os três fatores para o lançamento apenas para pesquisa. Anote qual deles depende da sua escolha de professor.
- [ ] Amanhã: escreva os quatro passos do pipeline do Self-Instruct e o limiar do filtro sem consultar anotações, depois compare com o artigo.

## Para ir além

- [Sequência e Dados Sintéticos](../reference/sequence-and-synthetic-data.md)
- [Artigo científico: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
- [Artigo: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
