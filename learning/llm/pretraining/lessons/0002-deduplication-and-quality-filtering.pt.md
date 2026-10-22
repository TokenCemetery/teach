---
title: "2. Deduplicação e filtragem de qualidade"
description: "Por que texto quase duplicado e documentos de baixa qualidade são removidos antes do treinamento e o que custa pular essa etapa"
type: lesson
---

# Lição 2. Deduplicação e filtragem de qualidade

**Ligação com a missão:** "Construir um corpus de pré-treinamento deduplicado e filtrado por qualidade a partir de fontes brutas e dizer o que cada etapa de filtragem remove e por quê" é o primeiro item em O sucesso se parece com isto. A Lição 1 cobriu a obtenção e a mistura; esta lição cobre a metade de deduplicação e filtragem.
**Fonte principal:** [Artigo científico: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
**Pré-requisitos:** [Lição 1](0001-sourcing-and-mixing-a-pretraining-corpus.md)

## Aquecimento

1. ▢ Qual é a diferença entre uma decisão de obtenção e uma decisão de mistura em um corpus de pré-treinamento?

<details markdown="1"><summary>Verificação</summary>

A obtenção decide quais fontes são incluídas. A mistura decide quanto do orçamento final de tokens cada fonte incluída recebe, independentemente de quais fontes foram escolhidas.

</details>

2. ▢ Segundo o artigo do Pile, por que "qual o tamanho do corpus" é a pergunta errada para fazer primeiro sobre uma execução de pré-treinamento?

<details markdown="1"><summary>Verificação</summary>

Porque o GPT-2 e o GPT-3, treinados em enormes quantidades de texto da web, ainda tiveram dificuldade em componentes como a escrita acadêmica, que um crawl geral da web sub-representa. Quais fontes estão incluídas, e não a contagem total de bytes, é o que determina quais domínios um modelo realmente aprende.

</details>

## Saiba isto

### Duplicatas não são só espaço em disco desperdiçado

Um corpus montado a partir de muitas fontes, especialmente qualquer coisa que toque a web aberta, acaba com o mesmo texto aparecendo mais de uma vez: notícias distribuídas por agências, avisos legais padronizados, e-mails de modelo em que só o nome muda. Lee et al. constataram que isso não é uma ineficiência menor. No C4, um corpus muito usado derivado de crawls da web, uma única frase em inglês de 61 palavras aparece mais de 60.000 vezes. Mais impressionante ainda: mais de 1% da saída sem prompt de modelos de linguagem treinados em tais datasets é copiada literalmente dos dados de treinamento: o modelo não está generalizando ali, está citando algo que viu vezes suficientes para memorizar.

### Duas formas diferentes de encontrar uma duplicata

A deduplicação precisa pegar duas formas diferentes de repetição, e uma só técnica não pega as duas:

- **A correspondência exata de substrings** encontra trechos de texto repetidos literalmente, mesmo aqueles que são apenas parte de um documento ou que cruzam fronteiras de documentos. Lee et al. a implementam de forma eficiente com um suffix array, que permite encontrar um trecho repetido de qualquer comprimento sem comparar diretamente cada documento com todos os outros.
- **A correspondência de quase duplicatas** encontra documentos que são em sua maioria iguais mas diferem em pequenos detalhes, como um e-mail de formulário com o nome de outro destinatário, ou uma matéria de agência de notícias reaproveitada com pequenas edições por muitos veículos. Lee et al. usam o MinHash: uma técnica que estima o quão parecidos dois documentos são sem compará-los token a token, comparando em vez disso resumos compactos baseados em hash.

As duas importam, porque um corpus pode estar livre de um tipo de duplicação e ainda assim cheio do outro.

### O que a deduplicação realmente traz

Lee et al. dão evidência concreta em vez de uma intuição. Deduplicar os dados de treinamento fez os modelos emitirem texto memorizado cerca de dez vezes menos e permitiu que esses modelos alcançassem a mesma acurácia, ou uma melhor, em menos passos de treinamento. Também reduz a sobreposição entre treino e teste, que o artigo constatou afetar mais de 4% do conjunto de validação em benchmarks padrão; texto que vazou do próprio conjunto de validação de um benchmark para o treinamento faz o número de uma avaliação parecer melhor do que a generalização real do modelo merece, uma preocupação a que esta trilha voltará quando linkar para o tratamento de contaminação em `llm/evals`.

### A filtragem de qualidade é uma etapa separada e posterior

A deduplicação remove cópias redundantes de texto que já está presente. A filtragem de qualidade remove texto de baixo valor mesmo sem ser duplicata de nada: spam, menus de navegação padronizados, texto gerado por máquina ou documentos tão truncados que carregam pouco sinal. Os autores do GPT-3 descrevem uma versão concreta disso no apêndice sobre a filtragem do Common Crawl: eles treinaram um classificador, usando regressão logística sobre features simples no estilo bag-of-words, para distinguir texto curado (WebText, Wikipedia, um corpus de livros) do Common Crawl bruto e sem filtro. A pontuação desse classificador foi então usada para reamostrar o Common Crawl, de modo que os documentos previstos como de maior qualidade fossem mantidos com mais frequência, ainda mantendo alguns documentos de pontuação mais baixa em vez de descartá-los de vez. O mesmo apêndice descreve também uma passagem separada de deduplicação fuzzy com MinHash, que por si só reduziu o tamanho do dataset em cerca de 10%.

A filtragem de qualidade e a deduplicação costumam ser executadas como passagens separadas sobre o mesmo corpus, em qualquer ordem, e nenhuma substitui a outra: um corpus pode estar livre de duplicatas exatas e ainda cheio de texto padronizado de baixo valor, e pode ser uma prosa uniformemente de alta qualidade e ainda conter o mesmo parágrafo repetido sessenta mil vezes.

## Prática

1. ▢ Um dataset contém 61 palavras repetidas literalmente em mais de 60.000 documentos diferentes, cada vez com texto ao redor diferente. A correspondência exata de substrings ou a correspondência de quase duplicatas (MinHash) seria a ferramenta certa para encontrar e remover apenas esse trecho repetido, e por quê?

<details markdown="1"><summary>Dica</summary>

Pergunte o que o MinHash realmente compara: documentos inteiros entre si, ou trechos de texto que podem ser apenas parte de um documento.

</details>

<details markdown="1"><summary>Verificação</summary>

A correspondência exata de substrings. O MinHash estima a similaridade entre documentos inteiros; um trecho de 61 palavras repetido dentro de documentos que, fora isso, são diferentes é exatamente o tipo de repetição parcial entre documentos que uma busca exata de substrings baseada em suffix array foi feita para pegar, enquanto dois documentos que compartilham apenas 61 palavras entre muitos milhares podem nem ser registrados como quase duplicatas um do outro.

</details>

2. ▢ Qual destas é a mais próxima do que Lee et al. de fato mediram, e não apenas argumentaram?

    - a) A deduplicação torna um modelo filosoficamente mais original
    - b) O treinamento deduplicado permitiu que os modelos alcançassem a mesma acurácia, ou uma melhor, em menos passos e emitissem texto memorizado cerca de dez vezes menos
    - c) A deduplicação só serve para reduzir custos de armazenamento, sem efeito no comportamento do modelo
    - d) A correspondência de quase duplicatas sozinha basta para remover todas as formas de texto repetido

<details markdown="1"><summary>Verificação</summary>

**b)** é o resultado efetivamente medido pelo artigo. (a) não é uma afirmação mensurável. (c) contradiz diretamente as constatações sobre memorização e eficiência de treinamento. (d) é falsa, já que a correspondência exata de substrings pega uma forma de repetição diferente da que a correspondência de quase duplicatas pega, como mostra o primeiro item de prática desta lição.

</details>

3. ▢ Um documento não é duplicata de nada mais no corpus, mas é em sua maior parte texto padronizado gerado automaticamente, com quase nenhum conteúdo informativo. A deduplicação o removeria? O que removeria?

<details markdown="1"><summary>Verificação</summary>

Não, a deduplicação não o removeria, já que ela só tem como alvo texto repetido e este documento é único. A filtragem de qualidade, como a reamostragem baseada em classificador que os autores do GPT-3 descrevem, é a etapa voltada exatamente para este caso: texto de baixo valor que não é cópia de nada mais.

</details>

4. ▢ O classificador de qualidade do Common Crawl do GPT-3 foi treinado para distinguir qual destes pares de coisas?

    - a) Texto em inglês de texto em outros idiomas
    - b) Texto curado (WebText, Wikipedia, um corpus de livros) do Common Crawl bruto e sem filtro
    - c) Documentos longos de documentos curtos
    - d) Texto duplicado de texto único

<details markdown="1"><summary>Verificação</summary>

**b)** Texto curado contra o Common Crawl bruto. (d) descreve a deduplicação, que os autores do GPT-3 executaram como uma passagem separada de MinHash, e não o que o próprio classificador de qualidade foi treinado para detectar.

</details>

## Prática no mundo real

- [ ] Escolha uma frase ou expressão curta que você esperaria ser comum em texto da web (um aviso legal, uma frase feita, uma instrução comum de receita) e pesquise-a literalmente online. Anote aproximadamente em quantas páginas distintas você a encontra, como uma noção intuitiva de como a repetição aparece em texto coletado de verdade.
- [ ] Leia o resumo e a introdução do artigo de Lee et al. (linkado acima) e escreva, em uma frase cada, o que a correspondência exata de substrings e a correspondência de quase duplicatas são boas em pegar que a outra não é.
- [ ] Amanhã: pegue um corpus para o qual você esboçou uma mistura na prática no mundo real da Lição 1 e, para cada tipo de fonte, nomeie uma fonte plausível de duplicação (distribuição por agências, texto padronizado de modelo, republicação) e uma fonte plausível de baixa qualidade que a deduplicação sozinha não pegaria.

## Para ir além

- [Artigo científico: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
