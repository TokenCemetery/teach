---
title: "6. BM25 e busca lexical"
description: "O que o BM25 de fato pontua, e por que a correspondência exata de termos ainda pega o que os embeddings semânticos deixam passar"
type: lesson
---

# Lição 6. BM25 e busca lexical

**Ligação com a missão:** A etapa 4 abre a busca híbrida: antes de combinar um ranking lexical com a busca vetorial, esta lição estabelece no que a busca lexical de fato é boa, e por que um modelo de embedding forte não a torna obsoleta.
**Fonte principal:** [Artigo científico: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson e Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
**Pré-requisitos:** [Lição 5](0005-pgvector-specifics.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que um bi-encoder gera o embedding de uma consulta e de uma passagem separadamente em vez de em conjunto?

<details markdown="1"><summary>Verificação</summary>

Para que cada passagem possa ter o embedding gerado uma vez, com antecedência, e ser armazenada; só a consulta precisa de embedding na hora da busca, permitindo compará-la de forma barata com vetores de passagem pré-calculados.

</details>

2. ▢ Por que um índice construído com `vector_l2_ops` não acelera uma consulta que ordena por `<=>` (distância de cosseno)?

<details markdown="1"><summary>Verificação</summary>

Um índice é construído para uma função de distância específica; a classe de operador e o operador da consulta precisam corresponder, ou o índice fica sem uso e a consulta recorre a uma varredura sequencial completa.

</details>

## Saiba isto

### O BM25 pontua a sobreposição de termos, não o significado

O **BM25** é uma função de ranking lexical: ele pontua quão relevante um documento é para uma consulta com base apenas em quais termos da consulta aparecem literalmente no documento, com que frequência e quão informativo é cada termo, sem embedding e sem nenhuma noção de significado. Três ingredientes se combinam em sua pontuação: a **frequência inversa de documento (IDF)**, que pondera um termo da consulta pela raridade dele em todo o corpus (uma palavra comum como "the" contribui quase nada, já que aparece em todo lugar e não distingue nada; um termo raro e específico contribui muito, já que sua presença é informativa); a **frequência de termo**, quantas vezes um termo da consulta aparece neste documento em particular, mas **saturando** em vez de escalar linearmente, de modo que um termo aparecendo 10 vezes não pontua 10 vezes mais do que aparecendo uma vez, o que impede o keyword stuffing de dominar uma pontuação; e a **normalização de tamanho**, que desconta a vantagem bruta de frequência de termo de um documento por ser simplesmente mais longo que a média, já que um documento mais longo tem mais chances de conter qualquer termo dado só pelo tamanho, não necessariamente por ser mais relevante.

### Por que a busca lexical ainda importa ao lado de um bom modelo de embedding

Os modelos de embedding são treinados para capturar similaridade semântica, e fazem isso bem para formulações sinônimas: uma consulta por "how to fix a broken pipe" pode recuperar uma passagem sobre "resolving a leaking conduit" apesar de nenhuma palavra em comum, porque as duas significam coisas parecidas. Mas esse mesmo treinamento torna os embeddings comparativamente fracos na correspondência exata de termos específicos: um código de produto, um identificador de erro, um nome próprio raro, uma frase exata que o usuário cita literalmente. Uma consulta por "error code E502" precisa de um documento que contenha literalmente "E502"; um modelo de embedding, treinado em similaridade semântica geral e não em correspondência de identificador exato, pode recuperar documentos que tratam do assunto tratamento de erros sem trazer à tona o único documento que de fato contém o código específico que o usuário digitou. O BM25 tem o ponto cego oposto: exatamente o caso inverso, "broken pipe" contra "leaking conduit", pontuaria perto de zero no BM25, já que os dois não compartilham nenhum termo, apesar de significarem a mesma coisa. Cada abordagem pega o que a outra deixa passar, e esse é exatamente o argumento para combiná-las em vez de escolher uma.

![Uma grade de dois por dois. Linha um: uma consulta de identificador exato como "error code E502". O BM25 a encontra, já que a string literal aparece no documento; a busca vetorial pode deixá-la passar, já que seu modelo de embedding foi treinado para similaridade semântica, não para correspondência de identificador exato. Linha dois: uma consulta de formulação sinônima como "broken pipe" contra um documento que diz "leaking conduit", sem palavras em comum. O BM25 pontua isso perto de zero, já que só conta a sobreposição literal de termos; a busca vetorial a encontra, já que as duas frases significam a mesma coisa. O ponto cego de cada método é a força do outro método.](images/bm25-vs-vector-blindspots.svg)

## Prática

1. ▢ Um usuário busca o código de erro exato "E502". Por que a busca vetorial sozinha poderia recuperar de menos o único documento que de fato contém essa string, mesmo que o corpus tenha vários documentos sobre o assunto tratamento de erros?

<details markdown="1"><summary>Verificação</summary>

O modelo de embedding foi treinado para capturar similaridade semântica, não correspondência de identificador exato, então "E502" pode não estar bem representado como um ponto distintivo no espaço de embeddings; documentos que são similares em assunto sobre tratamento de erros em geral podem acabar mais próximos do embedding da consulta do que o único documento que por acaso contém a string literal "E502".

</details>

2. ▢ Uma consulta diz "how to fix a broken pipe", e o documento que melhor corresponde está formulado como "resolving a leaking conduit", sem palavras em comum com a consulta. O BM25 pontuaria bem esse par? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não, o BM25 pontuaria perto de zero, já que só pontua com base em quais termos da consulta aparecem literalmente no documento, e esse par não compartilha nenhum termo. O BM25 não tem como reconhecer que as duas formulações significam a mesma coisa; é exatamente a lacuna que a similaridade semântica da busca vetorial serve para preencher.

</details>

3. ▢ Por que o BM25 satura a frequência de termo (diminuindo o aumento de pontuação de ocorrências repetidas de um termo) em vez de pontuá-la linearmente?

<details markdown="1"><summary>Dica</summary>

Pense no que um documento poderia fazer para burlar uma pontuação linear de frequência de termo.

</details>

<details markdown="1"><summary>Verificação</summary>

Uma pontuação linear de frequência de termo deixaria um documento dominar o ranking simplesmente repetindo muitas vezes um termo da consulta (keyword stuffing), independentemente de o documento ser de fato mais relevante. Saturar a frequência de termo significa que cada ocorrência adicional contribui menos que a anterior, de modo que a relevância ainda é recompensada sem deixar a repetição bruta dominar sozinha a pontuação.

</details>

4. ▢ Por que o BM25 normaliza pelo tamanho do documento, e o que daria errado sem essa normalização?

<details markdown="1"><summary>Verificação</summary>

Um documento mais longo tem mais oportunidades de conter qualquer termo da consulta simplesmente por ter mais palavras, independentemente de ser de fato mais relevante para a consulta. Sem a normalização de tamanho, documentos longos superariam sistematicamente documentos mais curtos, igualmente ou mais relevantes, puramente por causa do tamanho, e não da relevância real.

</details>

5. ▢ Qual afirmação é verdadeira sobre o BM25 em comparação com a busca vetorial?

    - a) O BM25 e a busca vetorial falham exatamente nos mesmos tipos de consulta, então combiná-los não acrescenta nada
    - b) O BM25 se destaca na correspondência exata de termos, mas perde formulações sinônimas sem palavras em comum, enquanto a busca vetorial faz o inverso
    - c) O BM25 exige um modelo de embedding para calcular a relevância dos termos
    - d) A busca vetorial sempre supera o BM25 para qualquer consulta, já que captura o significado e não apenas palavras

<details markdown="1"><summary>Verificação</summary>

**b)** O ponto cego de cada abordagem é a força da outra, e essa é toda a base da busca híbrida. (a) é falsa: seus modos de falha são opostos, não idênticos. (c) é falsa: o BM25 é puramente um método de estatísticas de termos, sem nenhum embedding envolvido. (d) é falsa: uma correspondência de identificador ou código exato é exatamente o caso em que o BM25 pode superar um embedding semântico.

</details>

## Prática no mundo real

- [ ] Encontre ou escreva uma consulta para o seu corpus que inclua um identificador, código ou frase exata específica e verifique se a sua configuração atual de recuperação (se for apenas vetorial) de fato traz à tona o documento que a contém.
- [ ] Encontre uma consulta e um documento correspondente no seu corpus que compartilhem poucas ou nenhuma palavra exata mas signifiquem a mesma coisa, e preveja como uma busca apenas com BM25 pontuaria esse par.
- [ ] Amanhã: descubra se a sua stack de busca (busca de texto completo do Postgres, Elasticsearch ou similar) já expõe uma função de ranking no estilo BM25 que você poderia comparar com os resultados da sua busca vetorial.

## Para ir além

- [Artigo científico: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson e Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
