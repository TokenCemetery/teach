---
title: "20. Revisando um pipeline de recuperação"
description: "Revise o pipeline de recuperação de outra pessoa e nomeie especificamente o que ele vai errar antes de ir para produção, e diga quando o próprio RAG (e não uma etapa do pipeline) é a resposta errada para o problema declarado"
type: lesson
---

# Lição 20. Revisando um pipeline de recuperação

**Ligação com a missão:** Uma habilidade sênior é revisar o trabalho de outra pessoa, nomeando o que uma escolha custa em vez de dizer que ela parece errada, e saber quando a abordagem inteira é a errada para o problema (e não apenas qual etapa está quebrada).
**Fonte principal:** [Artigo científico: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Pré-requisitos:** [Lição 1](0001-chunking.md), [Lição 2](0002-embedding-models-and-similarity.md), [Lição 4](0004-ann-indexes.md), [Lição 6](0006-bm25-and-lexical-search.md), [Lição 9](0009-when-reranking-earns-its-cost.md), [Lição 11](0011-diagnosing-the-pipeline.md), [Lição 15](0015-metadata-filtering-and-access-control.md), [Lição 17](0017-freshness.md)

## Aquecimento

1. ▢ O que uma métrica de recuperação mede, e por que os pesos híbridos e o reranking precisam de uma?

<details markdown="1"><summary>Verificação</summary>

Uma métrica de recuperação como o Recall@k ou o MRR mede se a coisa certa foi recuperada, antes mesmo de a etapa de geração começar. O ajuste dos pesos híbridos e do reranking depende de saber se uma mudança de fato melhorou o que foi recuperado, então eles precisam de uma medição para decidir em vez de decidir por sensação.

</details>

2. ▢ Por que a pós-filtragem falha especificamente para controle de acesso, de um modo que não falha para outros filtros de metadados?

<details markdown="1"><summary>Verificação</summary>

A pós-filtragem executa primeiro a busca ANN sobre o índice inteiro e descarta os resultados depois. Para filtros de metadados comuns, isso é apenas uma regressão de recall: o filtro descarta alguns resultados. Para controle de acesso, conteúdo não autorizado existe brevemente no pipeline antes de ser descartado, o que é uma falha de segurança, e não apenas de qualidade. A pré-filtragem restringe o conjunto de candidatos antes de a busca rodar, então o conteúdo não permitido nunca entra no pipeline.

</details>

3. ▢ Nomeie uma forma de um corpus ficar desatualizado e uma forma de a atualidade ser tratada de maneira diferente nesse caso em comparação com outro.

<details markdown="1"><summary>Verificação</summary>

Um corpus fica desatualizado ao adicionar documentos, excluí-los ou trocar o modelo de embedding. Adicionar e excluir podem usar indexação incremental, e o HNSW trata ambos de forma relativamente boa. Trocar o modelo exige uma reindexação completa do zero: os vetores antigos não compartilham distâncias comparáveis com os novos, então precisam ser totalmente reconstruídos.

</details>

## Saiba isto

### O checklist de revisão: o que de fato procurar em um design

Quando alguém propõe um pipeline de recuperação ou mostra um que já foi construído, percorra estas perguntas em ordem. Cada uma corresponde a uma etapa deste arco. Para cada uma, procure: (1) a escolha foi feita de forma deliberada para este corpus e caso de uso, (2) foi medida contra uma métrica de recuperação, ou foi escolhida por padrão ou por sensação?

**Etapa 1: Estratégia de chunking.** O design escolheu uma estratégia de chunking porque ela corresponde à estrutura real do corpus (tamanho fixo para prosa, recursiva para markdown aninhado, semântica para artigos com mudanças de assunto, ou ciente da estrutura do documento para PDFs com layout que importa)? Ou um tamanho de chunk padrão (512, 1024 tokens) foi simplesmente copiado? Um corpus de PDFs médicos precisa de um chunking diferente de um repositório cheio de documentação de API.

**Etapas 2 e 3: Modelo de embedding e métrica de similaridade.** O modelo de embedding e a métrica (cosseno, L2, produto escalar) foram escolhidos para este corpus, testados contra corpora semelhantes ou pelo menos contra exemplos deste? Ou foram escolhidos por padrão a partir do que a documentação do banco de dados vetorial recomendava? Um embedding treinado em notícias pode ranquear mal artigos de finanças.

**Etapas 4, 5 e 6: Busca híbrida, reranking e avaliação da recuperação.** O design tem uma métrica de recuperação real contra a qual foi ajustado (Recall@k, MRR, nDCG)? Ou os pesos híbridos e o reranking foram adicionados por sensação, sem nenhuma medição de se de fato melhoraram a coisa certa que está sendo recuperada? Uma etapa de reranking que custa latência precisa de prova de que mereceu esse custo no caso de uso real.

**Etapa 9: Filtragem ciente de permissões.** Se o corpus tem controle de acesso, o design usa pré-filtragem para restringir o conjunto de candidatos antes da busca ANN, mantendo o conteúdo não autorizado totalmente fora do pipeline? Ou recupera do índice inteiro e filtra depois, arriscando tanto uma regressão de recall quanto um momento em que conteúdo não autorizado existe no pipeline?

**Etapas 10 e 11: Ingestão e atualidade.** O design levou em conta como os documentos-fonte são de fato extraídos e processados a montante do chunking? Tem um plano para manter o índice atual conforme documentos são adicionados, excluídos ou modificados, ou pressupõe dados estáticos? As atualizações incrementais combinam bem com o HNSW, mas trocar um modelo de embedding sempre exige uma reindexação completa.

**Etapa 6 de novo: Distinguir falha de recuperação de falha de geração.** Quando algo dá errado, o design tem como saber se o modelo recebeu um contexto ruim ou usou mal um bom contexto? Um design que, por padrão, culpa a etapa de recuperação por qualquer resposta errada está perdendo um diagnóstico crucial.

### A questão em disputa: o contexto longo torna a recuperação obsoleta?

Esta é uma discordância em aberto. Um lado diz que os modelos de contexto longo agora eliminam a necessidade de recuperação: por que construir um pipeline de recuperação quando os modelos agora conseguem guardar o corpus inteiro no prompt? Por que pagar por infraestrutura de recuperação quando você pode simplesmente enviar 100K tokens a cada requisição?

O outro lado diz que a recuperação ainda vence na maioria dos corpora e casos de uso reais, apesar dos avanços do contexto longo. O artigo de pesquisa "Lost in the Middle" mostra que os modelos usam a informação colocada no meio de um contexto longo muito pior do que a informação no início ou no fim, mesmo dentro da janela de contexto. Reenviar um corpus inteiro a cada requisição concentra no meio da atenção todos os tokens que não são usados, exatamente onde os modelos usam mal a informação. A recuperação, em vez disso, envia apenas as partes relevantes, mantendo-as perto do topo da janela de contexto, onde os modelos atentam bem a elas.

Mas isso é o framework de decisão, não a decisão em si. Para decidir se a recuperação é a resposta certa para um problema específico, faça três perguntas:

**1. Qual é o tamanho do corpus e a frequência de atualização?**

Um corpus pequeno, estático e que cabe em um único prompt pode legitimamente funcionar melhor enviado inteiro: o manual inteiro de uma empresa (50K tokens, muda a cada trimestre) pode ser mais barato e simples de incluir a cada requisição do que manter um índice de recuperação. Um corpus grande (milhões de documentos), que muda o tempo todo (ingestão diária) ou que tem controle de acesso (usuários diferentes veem subconjuntos diferentes) funciona do jeito oposto: o custo de reenviá-lo a cada requisição é proibitivo, ou o controle de acesso é impossível de impor depois da recuperação (a lição da etapa 9).

**2. O que o padrão de consultas de fato precisa?**

Uma consulta que precisa de síntese sobre o corpus inteiro (qual é o consenso sobre X em todos os nossos artigos) pode se beneficiar de ver mais contexto. Uma consulta que precisa de fatos precisos (qual é a nossa política de reembolso para assinaturas anuais) funciona melhor com uma recuperação que encontra o documento exato da política e o coloca no topo, onde o modelo atenta bem a ele. A recuperação permite enviar menos contexto com maior fidelidade.

**3. A quanto o cálculo de custo de fato chega?**

O artigo "Lost in the Middle" mostra o trade-off: quando a informação fica no meio de um prompt de 100K tokens, os modelos a perdem. Para contornar isso, você precisa ou ordenar o contexto com cuidado (o que a recuperação faz ao colocar os chunks mais relevantes perto do topo) ou enviar menos dele. Uma recuperação que envia 2K tokens dos chunks mais relevantes é mais barata e melhor do que 100K tokens em que metade está na zona morta. Isso pressupõe que a sua recuperação de fato encontra os chunks relevantes; se o pipeline de recuperação está quebrado, enviar tudo é pelo menos um recurso de contingência. Mas quando a recuperação funciona, ela vence em custo, latência e qualidade.

## Prática

1. ▢ Uma equipe construiu um pipeline que faz o chunking de todos os documentos com um tamanho fixo de 1024 tokens. Você revisa o design e não vê justificativa para essa escolha. Que pergunta você deve fazer para entender se ela foi deliberada ou adotada por padrão?

<details markdown="1"><summary>Verificação</summary>

Qual é o corpus? São transcrições de atendimento ao cliente, artigos acadêmicos, documentação de produto ou outra coisa? Um chunk de 1024 tokens funciona para alguns tipos de documento e falha para outros. Se eles escolheram esse tamanho porque era fácil de implementar ou porque o código de exemplo do banco de dados vetorial o usava, isso é um sinal de alerta. Se eles testaram diferentes tamanhos de chunk contra uma métrica de recuperação reservada em amostras reais do corpus e o 1024 venceu, essa é uma escolha deliberada que você consegue rastrear.

</details>

2. ▢ O design usa o modelo de embedding da OpenAI sem testá-lo no corpus real. O que pode dar errado?

<details markdown="1"><summary>Verificação</summary>

O modelo de embedding foi treinado em uma distribuição ampla de texto da internet. Se o corpus é altamente especializado (documentos jurídicos, relatórios financeiros, literatura médica) ou está em um idioma com menos dados de pré-treinamento, o modelo pode ranquear mal a similaridade semântica. O teste certo: gerar o embedding de uma amostra de documentos deste corpus, identificar manualmente quais pares são de fato similares e verificar se o ranking de distância da OpenAI concorda. Se não, considere embeddings específicos de domínio ou modelos treinados em conteúdo parecido.

</details>

3. ▢ Um design usa busca híbrida (BM25 + vetorial), mas a equipe não sabe ao certo como ponderá-los. Eles perguntam: "devemos usar 50-50, ou 70-30 a favor do vetorial?" Que informação está faltando a eles?

<details markdown="1"><summary>Verificação</summary>

Está faltando uma métrica de recuperação. Os pesos devem ser ajustados contra uma medição real sobre um conjunto de consultas reservado, medindo qual mistura produz o melhor Recall@k ou MRR na tarefa. Chutar entre 50-50 e 70-30 é cara ou coroa, e a mistura errada pode prejudicar mais do que qualquer uma das abordagens sozinha. A pergunta real é: para o seu corpus e as suas consultas, qual mistura de fato recupera a coisa certa? Meça.

</details>

4. ▢ O corpus contém artigos de pesquisa médica que são atualizados o tempo todo (novos artigos adicionados diariamente, os mais antigos às vezes retratados ou corrigidos). Uma proposta sugere colocar todos os documentos no prompt de um modelo de contexto longo a cada requisição. Cite dois motivos pelos quais isso pode não funcionar.

<details markdown="1"><summary>Dica</summary>

Considere como é o corpus (tamanho, taxa de mudança) e o que o modelo faz com a informação colocada no meio de um contexto longo.

</details>

<details markdown="1"><summary>Verificação</summary>

Dois motivos: (1) O corpus é grande e muda o tempo todo, então reenviar todos os documentos a cada requisição é caro, e atualizar quais documentos estão no prompt é um fardo de manutenção. A recuperação permite enviar apenas o que é relevante e se atualiza automaticamente quando o índice é atualizado. (2) Os modelos usam mal a informação colocada no meio de um contexto longo ("Lost in the Middle"). Enviar 500 artigos com apenas alguns relevantes para a consulta enterra os relevantes no meio da atenção, onde os modelos atentam mal. Uma recuperação que envia os 5 artigos mais relevantes, ranqueados por relevância no topo do contexto, é ao mesmo tempo mais barata e mais acurada.

</details>

5. ▢ Uma equipe que considera usar RAG pergunta: "Nosso corpus são 10MB de arquivos markdown, atualizados uma vez por ano. Por que não incluir tudo no prompt?" Qual afirmação abaixo responde corretamente a essa pergunta?

    - a) Os modelos de contexto longo tornam o RAG completamente obsoleto; esta equipe nunca deveria usar recuperação por qualquer motivo
    - b) O corpus é pequeno, estático e cabe em um prompt; para este caso específico, incluir tudo pode de fato ser mais simples e funcionar bem
    - c) O RAG é sempre melhor que o contexto longo, não importa o tamanho do corpus nem a frequência de mudança
    - d) O artigo "Lost in the Middle" prova que nada jamais deveria ser colocado em um prompt

<details markdown="1"><summary>Verificação</summary>

**b)** Essa é a posição calibrada sobre esta questão. O tamanho do corpus (10MB, provavelmente abaixo da janela de contexto), a frequência de mudança (anual) e as necessidades de controle de acesso (nenhuma mencionada) apontam todos para o contexto longo funcionar bem, possivelmente de forma mais simples. O RAG tem custos reais de infraestrutura. Um corpus pequeno e estático não justifica esses custos. (a) está errada: os modelos podem ser usados legitimamente sem recuperação quando o corpus é minúsculo e estático. (c) está errada: a decisão depende das características do corpus e do padrão de consultas, e não de uma regra absoluta. (d) está errada: o artigo mostra que os modelos usam mal o meio do contexto, e não que qualquer coisa em um prompt é inutilizável.

</details>

## Prática no mundo real

- [ ] Encontre um pipeline de recuperação que você construiu ou revisou. Percorra contra ele as cinco perguntas do checklist. Para cada etapa, escreva uma frase: essa escolha foi medida contra uma métrica de recuperação, ou escolhida por padrão? Depois pergunte: o que você mudaria se tivesse de melhorá-lo?
- [ ] Escolha um corpus (o seu, um público que você conheça ou um sintético). Resolva o framework de três perguntas: tamanho do corpus e frequência de atualização, padrão de consultas, custo real de reenviá-lo inteiro contra a recuperação. Anote a resposta: a recuperação ou o contexto longo seria o melhor ajuste, e por quê?
- [ ] Amanhã: leia a seção de resultados do artigo "Lost in the Middle" e anote a diferença específica de desempenho entre a informação no início, no meio e no fim de um contexto de 4K tokens. Depois estime: se o seu padrão de consultas precisasse de síntese sobre 100 documentos, quantos caberiam nas zonas de "alta qualidade" do início e do fim?

## Para ir além

- [Artigo científico: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Lição 24: Contexto longo no serving](../../inference/lessons/0024-long-context-at-serve-time.md): o que as técnicas de contexto longo de fato fazem com o custo de serving, e não com o custo de recuperação
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
