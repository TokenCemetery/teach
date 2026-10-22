---
title: "1. Obtendo e misturando um corpus de pré-treinamento"
description: "O que entra em um corpus de pré-treinamento e por que a mistura de fontes importa mais do que a contagem total de bytes"
type: lesson
---

# Lição 1. Obtendo e misturando um corpus de pré-treinamento

**Ligação com a missão:** "Construir um corpus de pré-treinamento deduplicado e filtrado por qualidade a partir de fontes brutas e dizer o que cada etapa de filtragem remove e por quê" é o primeiro item em O sucesso se parece com isto. Esta lição cobre a metade de obtenção e mistura; a Lição 2 cobre a deduplicação e a filtragem de qualidade.
**Fonte principal:** [Artigo científico: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
**Pré-requisitos:** nenhum

## Saiba isto

### Do que é feito um corpus de pré-treinamento

Um corpus de pré-treinamento é a coleção bruta de documentos com que um modelo treina antes de qualquer parte dela ser tokenizada: crawls da web, livros, repositórios de código, artigos acadêmicos, posts de fóruns, sites de referência e mais, reunidos de muitas fontes separadas em vez de coletados de um único crawl gigante. Tratar "o corpus" como uma pilha única e indiferenciada de texto esconde a decisão que realmente molda o que o modelo aprende: quais fontes entraram e quanto do corpus final cada uma representa.

### Obter é uma decisão de mistura, não apenas de inclusão

O Pile é um bom exemplo trabalhado porque os seus autores documentaram o raciocínio em vez de apenas lançar o dataset. Ele reúne 825 GiB de texto de 22 subconjuntos diversos e de alta qualidade, muitos vindos de fontes acadêmicas ou profissionais (processos judiciais, artigos acadêmicos, documentação técnica) que um crawl geral da web sub-representa. A própria avaliação do artigo torna o argumento concreto: o GPT-2 e o GPT-3, nenhum dos quais treinou no Pile, têm dificuldade em muitos dos seus componentes, "como a escrita acadêmica", enquanto os modelos treinados no Pile melhoram de forma significativa em relação aos treinados no Raw Common Crawl ou no CC-100, em todos os componentes do próprio Pile e também em avaliações downstream.

Esse resultado não é realmente sobre o tamanho total. É sobre quais domínios foram incluídos, e é por isso que "qual o tamanho do corpus" é a pergunta errada para fazer primeiro sobre uma execução de pré-treinamento.

### A proporção é a alavanca, não apenas a presença

Quando uma fonte é incluída, resta uma segunda decisão: quanto do orçamento final de tokens ela recebe. Uma fonte que domina a contagem bruta de bytes da internet (conversa de fórum, texto de marketing, texto de navegação padronizado) não tem direito automático de dominar o corpus, e uma fonte pequena em bytes brutos mas densa em informação (texto acadêmico curado, documentação de referência) não fica presa à fatia que ocupa naturalmente. Quem projeta um corpus escolhe fazer upsampling de algumas fontes em relação ao seu tamanho natural e limitar outras bem abaixo dele, e essa escolha é independente da decisão de incluir a fonte, e feita depois dela.

Dois corpora podem incluir exatamente a mesma lista de fontes e ainda assim se comportar de modo diferente depois de treinados, se as suas proporções forem diferentes. É por isso que "mistura" e "obtenção" são duas decisões separadas que vale nomear separadamente, mesmo que uma tabela de nomes de datasets faça as duas parecerem a mesma coisa.

### O corpus é um artefato de design

A obtenção e a mistura acontecem antes de um único token de treinamento rodar, e são tão consequentes quanto qualquer hiperparâmetro escolhido depois. Um modelo treinado em um corpus mal composto desperdiça compute reaprendendo padrões redundantes ou de pouco valor, por melhor que as etapas posteriores de uma execução de pré-treinamento (o particionamento do ZeRO na etapa 5, o schedule de learning rate na etapa 7) sejam executadas. Essas etapas posteriores tornam o treinamento eficiente; esta etapa decide o que há para se tornar eficiente em aprender.

## Prática

1. ▢ O Pile reuniu 825 GiB de texto de 22 fontes diversas em vez de coletar um único crawl da web desse mesmo tamanho. Segundo a própria avaliação do artigo, o que o GPT-2 e o GPT-3 (nenhum treinado no Pile) fizeram em muitos dos componentes do Pile, e o que esse resultado diz sobre depender apenas de texto coletado da web?

<details markdown="1"><summary>Verificação</summary>

Eles tiveram dificuldade, em particular em componentes como a escrita acadêmica. Isso é evidência direta de que um corpus construído principalmente de texto geral coletado da web deixa o modelo com pouca exposição a gêneros inteiros, não importa quanto texto da web ele tenha visto.

</details>

2. ▢ Uma equipe dobra a contagem bruta de bytes do seu componente de crawl da web, mantendo fixa a contagem de bytes de todas as outras fontes, sem nenhuma outra mudança no design do corpus. O que acontece com a mistura?

    - a) A mistura não muda, já que a obtenção só se preocupa com quais fontes são incluídas, e não com quanto de cada uma
    - b) A fatia do crawl da web no corpus final cresce, mesmo que ninguém tenha decidido deliberadamente torná-lo uma fração maior daquilo com que o modelo aprende
    - c) A mistura só importa para como o tokenizer é treinado, não para o modelo em si
    - d) Dobrar o tamanho de uma única fonte sempre melhora o desempenho downstream

<details markdown="1"><summary>Dica</summary>

Nada sobre quais fontes estão presentes mudou aqui. Pergunte o que mudou em quanto do total cada uma delas contribui.

</details>

<details markdown="1"><summary>Verificação</summary>

**b)** A fatia do crawl da web cresce por padrão, como um efeito colateral acidental de uma mudança na contagem de bytes, e não porque alguém decidiu que o modelo deveria aprender desproporcionalmente mais com ele. (a) confunde inclusão com proporção, que é exatamente a distinção que esta lição traça. (c) é falsa: a mistura molda aquilo em que o modelo é treinado, e não apenas como o vocabulário é construído. (d) é falsa em geral; mais de uma fonte de baixa informação pode diluir um corpus em vez de melhorá-lo.

</details>

3. ▢ Um corpus recém-montado repete várias vezes uma pequena coleção de 2 GB de processos judiciais curados em relação à sua fatia natural, enquanto limita um componente de 400 GB de crawl bruto da web bem abaixo da sua fatia natural. Ambas as fontes já tinham sido selecionadas para inclusão antes dessa decisão. Isso é uma decisão de obtenção ou de mistura, e por quê?

<details markdown="1"><summary>Verificação</summary>

Uma decisão de mistura. O conjunto de fontes não mudou; ambas já estavam presentes. O que mudou foi quanto do orçamento final de tokens cada uma pode contribuir, que é exatamente a questão de proporção que esta lição separa da questão de inclusão.

</details>

## Prática no mundo real

- [ ] Leia a lista de fontes componentes no artigo do Pile (a sua Tabela 1, no artigo linkado) e anote quais duas ou três parecem mais surpreendentes em um corpus de treinamento de modelo de linguagem e por que você não teria pensado em incluí-las.
- [ ] Encontre a composição documentada de um corpus aberto de pré-treinamento conhecido que você ainda não examinou (RedPajama, Dolma e FineWeb são todos documentados publicamente). Anote aproximadamente que fração é texto geral coletado da web e que fração vem de fontes curadas ou estruturadas.
- [ ] Amanhã: esboce uma mistura hipotética de corpus para um modelo que você gostaria que fosse excepcionalmente bom em um domínio específico (raciocínio jurídico, literatura científica, uma linguagem de programação). Nomeie quatro ou cinco tipos de fonte que você incluiria e, para cada uma, diga com as suas próprias palavras se faria upsampling acima da sua fatia natural, a limitaria abaixo dela ou a deixaria como está, e por quê.

## Para ir além

- [Artigo científico: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
