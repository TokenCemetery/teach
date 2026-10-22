---
title: "7. Reciprocal rank fusion"
description: "Como combinar um ranking lexical e um ranking vetorial sem comparar pontuações incomparáveis, e como ajustar a mistura contra uma métrica medida"
type: lesson
---

# Lição 7. Reciprocal rank fusion

**Ligação com a missão:** Esta é a lição final da etapa 4: o BM25 e a busca vetorial (lições 4 a 6) produzem cada um um ranking, e esta lição é como esses dois rankings viram um resultado híbrido, ajustado contra um número medido e não contra uma mistura chutada.
**Fonte principal:** [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
**Pré-requisitos:** [Lição 6](0006-bm25-and-lexical-search.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Dê um exemplo de consulta em que o BM25 teria sucesso e a busca vetorial poderia falhar, e outro em que ocorre o inverso.

<details markdown="1"><summary>Verificação</summary>

Um identificador exato como "error code E502" favorece o BM25, já que o modelo de embedding da busca vetorial não foi treinado para corresponder com precisão a códigos específicos. Uma formulação sinônima sem palavras em comum, como "broken pipe" contra "leaking conduit", favorece a busca vetorial, já que o BM25 pontua zero para documentos que não compartilham termos com a consulta.

</details>

2. ▢ Por que usar o operador de distância errado contra um índice do pgvector faz a consulta recorrer a uma varredura sequencial?

<details markdown="1"><summary>Verificação</summary>

Um índice é construído para uma função de distância específica (uma classe de operador); uma consulta que usa um operador diferente não corresponde ao que o índice foi construído para atender, então o índice não pode ser usado e a consulta varre a tabela diretamente.

</details>

## Saiba isto

### O problema: dois rankings em escalas incomparáveis

O BM25 produz uma pontuação ilimitada e dependente do corpus; a similaridade de cosseno produz uma pontuação limitada entre -1 e 1. Tirar a média das duas diretamente, mesmo depois de alguma normalização, significa decidir como tornar duas escalas fundamentalmente diferentes comparáveis, e essa decisão é frágil: depende do corpus, da consulta e de qual esquema de normalização foi escolhido, sem nenhum modo fundamentado de saber se é justa.

### RRF: use a posição no ranking, não a pontuação em si

A **reciprocal rank fusion (RRF)** contorna totalmente o problema de escala ignorando as pontuações subjacentes e usando apenas a **posição de ranking** de cada documento dentro de cada ranking. Para um documento *d* que aparece na posição `rank_r(d)` no ranking *r*, sua pontuação RRF soma um termo de posição recíproca em cada ranking em que ele aparece:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

O `k` é uma constante que amortece a influência das posições mais altas; um padrão comum do artigo original é `k = 60`. Como só importa a posição no ranking, e não a magnitude da pontuação, a RRF combina um ranking do BM25 e um ranking da busca vetorial sem precisar normalizar nenhum dos dois: a posição no ranking já é uma moeda comum, que se autonormaliza em qualquer método de ranking.

### Um exemplo resolvido

Usando um `k = 1` simplificado para manter a aritmética limpa (sistemas de produção costumam adotar `k = 60` como padrão, o que amortece as diferenças entre as posições do topo com mais força do que `k = 1`): para uma consulta, o BM25 ranqueia o documento A em 1º, o documento B em 4º, o documento C em 2º; a busca vetorial ranqueia A em 4º, B em 1º, C em 2º.

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A e B empatam em primeiro, cada um se destacando em um método e indo mal no outro; C, apenas medíocre nos dois, perde para ambos. A RRF recompensa um documento em que qualquer um dos métodos acredita fortemente, e não apenas um documento em que os dois métodos concordam de leve.

![Duas listas ranqueadas lado a lado, o ranking do BM25 e o ranking da busca vetorial, cada uma com quatro posições. O documento A fica em 1º no BM25 mas em 4º na busca vetorial; o documento B fica em 4º no BM25 mas em 1º na busca vetorial; o documento C fica em 2º em ambos. Linhas ligam cada documento, a partir de suas duas posições, a um ranking RRF fundido à direita, onde A e B empatam em primeiro lugar, cada um tendo se destacado em um método, enquanto C, apenas moderado, vem atrás deles apesar de nunca ter ficado mal em nenhuma das listas.](images/rrf-worked-example.svg)

### Ajustando a mistura contra uma métrica medida

A RRF pode ser estendida com um peso por ranking, `sum of w_r / (k + rank_r(d))`, permitindo que a busca vetorial conte mais ou menos que o BM25 na fusão final. O peso certo, e o `k` certo, não são algo para chutar: são algo para medir, do mesmo modo que a lição 3 mediu a qualidade do embedding em dimensionalidades candidatas em vez de presumir uma. Usando as métricas de recuperação da etapa 6 (recall@k, MRR) contra um conjunto de consultas rotulado ou sintético, representativo do tráfego real do corpus, diferentes ponderações podem ser comparadas diretamente, e a mistura que de fato recupera os documentos certos com mais frequência para este corpus, e não uma divisão padrão de 50/50, é a que vale entregar.

## Prática

1. ▢ Para uma consulta, o BM25 ranqueia o documento X em 2º e o documento Y em 1º; a busca vetorial ranqueia X em 1º e Y em 3º. Usando `k = 1`, calcule a pontuação RRF de cada documento e diga qual fica mais alto.

<details markdown="1"><summary>Dica</summary>

`RRF(d) = 1/(k + rank_in_bm25) + 1/(k + rank_in_vector)`.

</details>

<details markdown="1"><summary>Verificação</summary>

`RRF(X) = 1/(1+2) + 1/(1+1) = 0.333 + 0.500 = 0.833`. `RRF(Y) = 1/(1+1) + 1/(1+3) = 0.500 + 0.250 = 0.750`. X fica mais alto, já que é um resultado forte (primeiro lugar) na busca vetorial e apenas medianamente bom no BM25, superando por pouco Y, que é forte no BM25 mas mais fraco na busca vetorial.

</details>

2. ▢ Por que a RRF usa a posição de ranking de cada documento, e não diretamente sua pontuação bruta do BM25 ou de similaridade de cosseno?

<details markdown="1"><summary>Verificação</summary>

As pontuações do BM25 e da similaridade de cosseno vivem em escalas incomparáveis (uma ilimitada e dependente do corpus, a outra limitada entre -1 e 1), e não há um modo fundamentado e independente do corpus de normalizá-las uma contra a outra. A posição no ranking já é uma moeda comum a qualquer método de ranking, então usá-la contorna totalmente o problema de normalização.

</details>

3. ▢ O que um `k` pequeno (como 1) faz com a fórmula da RRF, em comparação com um `k` grande (como 60), em termos de quanto importa a posição exata de um documento?

<details markdown="1"><summary>Verificação</summary>

Um `k` pequeno torna o termo de posição recíproca muito mais sensível a pequenas diferenças de posição perto do topo de uma lista (a distância entre a posição 1 e a posição 2 é proporcionalmente maior), enquanto um `k` grande amortece essa sensibilidade, tornando a diferença entre, digamos, a posição 1 e a posição 5 comparativamente menor. Valores maiores de `k` produzem uma fusão mais suave e menos sensível à posição.

</details>

4. ▢ Como uma equipe deve decidir se pondera a busca vetorial com mais peso que o BM25 em sua mistura híbrida, em vez de adotar por padrão uma divisão igual?

<details markdown="1"><summary>Verificação</summary>

Medir a qualidade da recuperação (recall@k ou MRR, as métricas da etapa 6) contra um conjunto de consultas rotulado ou sintético, representativo do padrão real de consultas do corpus, em várias ponderações candidatas, e escolher a que de fato recupera os documentos certos com mais frequência para este corpus, em vez de presumir que uma divisão igual ou qualquer outro padrão está correto sem verificar.

</details>

5. ▢ Qual afirmação é verdadeira sobre a reciprocal rank fusion?

    - a) Ela exige normalizar as pontuações do BM25 e da similaridade de cosseno para a mesma escala antes de combiná-las
    - b) Ela combina rankings usando apenas a posição no ranking, o que dispensa a necessidade de comparar escalas de pontuação incomparáveis
    - c) Um documento que fica em 1º em um ranking e em último em outro sempre superará um documento que fica em posição moderada nos dois
    - d) A constante `k` não tem efeito sobre o ranking fundido, apenas sobre a magnitude da pontuação numérica

<details markdown="1"><summary>Verificação</summary>

**b)** Usar a posição no ranking em vez de pontuações brutas é exatamente o que evita o problema de normalização. (a) é falsa: essa é a abordagem de fusão por pontuação bruta que a RRF evita especificamente. (c) é falsa: o exemplo resolvido mostrou que um documento consistentemente moderado ainda pode perder para dois documentos que se destacam cada um em um método, mas o resultado depende dos valores reais de posição, e não de uma regra universal de que o extremo vence o moderado. (d) é falsa: o `k` muda o quanto as diferenças de posição importam, o que pode mudar a ordem do ranking fundido, e não apenas sua escala.

</details>

## Prática no mundo real

- [ ] Para uma consulta do seu corpus, obtenha a posição no ranking do BM25 e a posição na busca vetorial de um punhado de documentos candidatos e calcule suas pontuações RRF à mão usando `k = 60`.
- [ ] Se você tiver um conjunto de consultas rotulado ou sintético, compare o recall@k de um ranking apenas com BM25, de um ranking apenas vetorial e de um ranking fundido por RRF nas mesmas consultas.
- [ ] Amanhã: experimente dois valores diferentes para o peso da busca vetorial em uma fórmula RRF ponderada e veja se algum deles melhora de forma mensurável o recall@k em relação a uma divisão igual.

## Para ir além

- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Artigo científico: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson e Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
