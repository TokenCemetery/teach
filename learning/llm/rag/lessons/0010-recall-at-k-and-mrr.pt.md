---
title: "10. Recall@k e MRR"
description: "As duas métricas padrão de recuperação, o que cada uma diz que a outra não diz, e como escolher o k para a carga de trabalho"
type: lesson
---

# Lição 10. Recall@k e MRR

**Ligação com a missão:** A etapa 6 abre a metade "meça, não presuma" da missão deste workspace: as decisões de toda etapa anterior (chunking, embeddings, indexação, pesos híbridos, reranking) foram apresentadas como coisas a medir, e esta lição dá os dois números padrão para medi-las.
**Fonte principal:** [Artigo: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
**Pré-requisitos:** [Lição 9](0009-when-reranking-earns-its-cost.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Como uma equipe deve decidir se o reranking compensa o custo para a sua carga de trabalho específica?

<details markdown="1"><summary>Verificação</summary>

Medir a qualidade da recuperação sem e com reranking sobre o mesmo conjunto de consultas, medir separadamente a latência adicional no tamanho de conjunto de candidatos em uso e comparar ambos com o orçamento de latência e o nível de qualidade reais da carga de trabalho, em vez de presumir que o reranking sempre ou nunca ajuda.

</details>

2. ▢ Na reciprocal rank fusion, o que a constante `k` faz com o ranking fundido?

<details markdown="1"><summary>Verificação</summary>

Ela amortece a influência das posições mais altas: um `k` menor torna a pontuação mais sensível a pequenas diferenças de posição perto do topo, enquanto um `k` maior (comumente 60) faz essas diferenças importarem menos.

</details>

## Saiba isto

### Recall@k: o documento certo entrou no corte?

O **recall@k** pergunta, entre um conjunto de consultas de teste com documentos relevantes conhecidos, que fração delas teve um documento relevante aparecendo em algum lugar dentro dos *k* primeiros resultados recuperados. É uma questão de orçamento: se o sistema a jusante só olha os *k* primeiros resultados, o recall@k diz com que frequência o sistema sequer lhe deu a chance de encontrar a resposta certa. O recall@k cresce conforme o *k* cresce (um documento relevante na posição 50 conta para o recall@100, mas não para o recall@10), e trata de forma idêntica toda posição dentro dos *k* primeiros: um documento relevante na posição 1 e um na posição *k* contam ambos como acerto, sem crédito por ficar mais alto.

### MRR: com que rapidez o documento certo apareceu

O **mean reciprocal rank (MRR)** corrige exatamente o que o recall@k não enxerga. Para cada consulta, pegue o recíproco da posição do primeiro resultado relevante (`1/posição`) e depois tire a média desse recíproco entre todas as consultas. Um resultado relevante na posição 1 contribui com um 1,0 inteiro para a média; o mesmo resultado relevante na posição 10 contribui com apenas 0,1. O MRR recompensa ranquear a resposta certa o mais alto possível, e não apenas colocá-la dentro de algum corte, que é exatamente a informação que o recall@k joga fora ao tratar igual toda posição dentro dos *k* primeiros.

### Um exemplo resolvido

Quatro consultas de teste, cada uma com um documento relevante conhecido, e sua posição nos resultados de cada sistema: 1, 3, 1, 8.

```text
recall@1: ranks ≤ 1 are queries 1 and 3 → 2/4 = 0.50
recall@5: ranks ≤ 5 are queries 1, 2, and 3 (ranks 1, 3, 1); query 4 (rank 8) misses → 3/4 = 0.75
MRR: (1/1 + 1/3 + 1/1 + 1/8) / 4 = (1.000 + 0.333 + 1.000 + 0.125) / 4 ≈ 0.615
```

O recall@5 diz que três de quatro consultas encontrariam a resposta se o sistema olhasse apenas seus 5 primeiros resultados. O 0,615 do MRR reflete que a maioria desses acertos caiu na posição 1, com um acerto mais fraco na posição 3 e uma falha puxando a média para baixo.

![Quatro consultas posicionadas ao longo de um eixo de posição compartilhado, de 1 a 9, na posição de seu primeiro resultado relevante: 1, 3, 1 e 8. Uma linha tracejada marca o corte do recall em 5. Os acertos das três primeiras consultas ficam à esquerda do corte e contam para o recall em 5, enquanto o da quarta, na posição 8, fica à direita e é uma falha. A posição recíproca de cada consulta é mostrada ao lado dela: 1,000, 0,333, 1,000 e 0,125. O recall em 5 resulta em 3 de 4, 0,75, enquanto a média das posições recíprocas dá um MRR de cerca de 0,615, puxado para baixo pelo quanto à direita fica a posição daquela única falha, algo que o recall em 5 não consegue enxergar.](images/recall-at-k-vs-mrr.svg)

### Escolhendo o k, e escolhendo entre as métricas

O *k* certo para o recall@k não é um padrão; é aquele que o sistema a jusante de fato usa. Se apenas os 5 primeiros chunks são passados à geração, o recall@100 mede algo que o pipeline nunca aproveita de fato; o recall@5 é o número que reflete a realidade. O MRR é mais informativo quando só o resultado do topo importa muito (uma única melhor resposta apresentada a um usuário), já que recompensa especificamente a posição 1 muito mais que a posição 10. O recall@k é mais informativo quando vários resultados dentro de um orçamento são todos genuinamente utilizáveis (a geração pode se valer de vários dos chunks do top k, e não apenas do primeiro). Reportar os dois, no *k* que o pipeline de fato usa, dá um quadro mais completo do que qualquer um sozinho.

## Prática

1. ▢ Usando o exemplo das quatro consultas desta lição (posições 1, 3, 1, 8), calcule o recall@3.

<details markdown="1"><summary>Dica</summary>

Conte quantas das quatro posições são 3 ou menos.

</details>

<details markdown="1"><summary>Verificação</summary>

As posições 1, 3 e 1 são todas ≤ 3; a posição 8 não é. `recall@3 = 3/4 = 0.75`, o mesmo que o recall@5 neste exemplo, já que nenhum documento relevante de consulta caiu na posição 4 ou 5.

</details>

2. ▢ Por que o recall@k sozinho não distingue um sistema que sempre ranqueia o documento relevante em 1º de um que sempre o ranqueia exatamente na posição `k`?

<details markdown="1"><summary>Verificação</summary>

O recall@k só verifica se um documento relevante aparece em algum lugar dentro das k primeiras posições; ele não registra em qual posição dentro desse intervalo o documento caiu. Um acerto na posição 1 e um acerto na posição k contam de forma idêntica para o recall@k, então a métrica não consegue diferenciar os dois sistemas, ainda que um deles claramente ranqueie melhor.

</details>

3. ▢ Por que o MRR distingue esses dois sistemas, onde o recall@k não conseguiu?

<details markdown="1"><summary>Verificação</summary>

O MRR usa o recíproco da posição exata, e não apenas se ela fica abaixo de um corte. Um sistema que sempre ranqueia o documento relevante em 1º obtém uma posição recíproca de 1,0 toda vez, dando a ele um MRR de 1,0; um sistema que sempre o ranqueia na posição k obtém uma posição recíproca de `1/k` toda vez, dando a ele um MRR muito menor sempre que k for maior que 1. A posição exata importa para o MRR de um modo que nunca importou para o recall@k.

</details>

4. ▢ A etapa de geração de uma equipe só usa os 5 primeiros chunks recuperados. Ela deveria reportar o recall@100 como sua métrica principal de recuperação? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não. O recall@100 mede se o documento relevante aparece em algum lugar dentro dos 100 primeiros resultados, mas o pipeline nunca olha além dos 5 primeiros, então um acerto na posição 40 é invisível para o sistema real e não deveria contar como sucesso. O recall@5 é o número que reflete o que o pipeline de fato aproveita; reportar o recall@100 superestimaria com que frequência o sistema de fato leva a resposta certa até a geração.

</details>

5. ▢ Qual afirmação é verdadeira sobre o recall@k e o MRR?

    - a) Eles medem exatamente a mesma coisa, então reportar os dois é redundante
    - b) O recall@k mede se um resultado relevante cai dentro de um orçamento de k; o MRR mede quão alto fica a posição do primeiro resultado relevante, recompensando a posição 1 muito mais que uma posição mais baixa
    - c) O MRR deve sempre ser preferido ao recall@k, independentemente da carga de trabalho
    - d) O recall@k é insensível à escolha do k; qualquer valor dá o mesmo resultado

<details markdown="1"><summary>Verificação</summary>

**b)** Essa é exatamente a informação complementar que cada métrica captura. (a) é falsa: o exemplo resolvido mostrou dois sistemas que poderiam empatar no recall@k e diferir bastante no MRR. (c) é falsa: qual métrica importa mais depende de só o resultado do topo contar ou de vários resultados dentro de um orçamento serem utilizáveis. (d) é falsa: o recall@k cresce conforme o k cresce, por definição, então a escolha do k muda o valor reportado.

</details>

## Prática no mundo real

- [ ] Para um pipeline de recuperação que você executa ou pretende executar, identifique o k real que o seu sistema a jusante usa (quantos chunks chegam à geração) e calcule o recall nesse k, e não em um padrão como 10 ou 100.
- [ ] Se você tiver um conjunto de consultas rotulado ou sintético, calcule o MRR junto com o recall@k e verifique se os dois números contam uma história consistente ou revelam algo que uma métrica sozinha teria escondido.
- [ ] Amanhã: para uma consulta em que o documento relevante do seu sistema fica mais baixo do que você gostaria, anote sua posição exata e como isso afeta tanto o recall@k (no k que você escolheu) quanto o MRR.

## Para ir além

- [Artigo: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
