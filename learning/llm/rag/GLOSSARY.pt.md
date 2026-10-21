---
title: "Glossário"
description: "Termos canônicos de RAG"
type: glossary
---

# Glossário de RAG

Termos canônicos para um pipeline de recuperação: em que ele divide os documentos e como decide o que entregar à etapa de geração.

## Termos

**Recuperação agêntica**:
Um sistema que decide, por consulta e por passo, se a recuperação é necessária, se o que voltou é suficiente e se deve recuperar de novo com base em algo recém-derivado, em vez de seguir uma única passada fixa de recuperar e depois gerar.
_Evite_: recuperação multi-hop (um caso relacionado, porém mais estreito: o multi-hop cobre especificamente a subpergunta posterior de uma consulta que depende da resposta de uma anterior, enquanto a recuperação agêntica também cobre decidir se vale recuperar)

**Chunk**:
Um pedaço de um documento, produzido ao dividi-lo antes de gerar o embedding e indexar, dimensionado para manter seu embedding focado em um assunto, e não numa média de vários.
_Evite_: segmento, trecho (use só ao citar uma fonte que usa o termo)

**Chunking**:
O processo de dividir um documento em chunks, por tamanho fixo, pela estrutura do próprio documento ou detectando onde o assunto muda.
_Evite_: divisão (genérico demais; use só em prosa que descreve o ato mecânico, não como nome do processo)

**Utilização da janela de contexto**:
A razão entre os chunks efetivamente citados em uma resposta gerada e os chunks recuperados e colocados no prompt. Utilização baixa significa tokens gastos com contexto que o modelo nunca usou; uma utilização consistentemente alta, por outro lado, pode alertar que material crítico está sendo truncado para fora da janela de contexto antes mesmo de poder ser citado.
_Evite_: presumir que utilização maior é sempre melhor; no extremo alto ela é um sinal de alerta de truncamento, não um ganho puro de eficiência

**Propagação em cascata de erros**:
Um erro em uma etapa inicial da ingestão (identificar errado um título, mesclar colunas na ordem errada) que se propaga para todas as etapas seguintes, as quais operam sobre a estrutura já corrompida que receberam, e acaba corrompendo todos os chunks de uma seção inteira, em vez de ficar contido no único elemento que o erro tocou diretamente.
_Evite_: um erro de parsing isolado (subestima o efeito; o objetivo de nomear isto como cascata é que um erro inicial se acumula em vez de ficar local)

**HyDE (Hypothetical Document Embeddings)**:
Gerar o embedding da resposta hipotética que um modelo de linguagem produz para uma consulta, em vez do embedding da própria consulta, e depois buscar no corpus por similaridade com esse embedding. Tolera detalhes factualmente errados no documento hipotético, já que a etapa de embedding do encoder os filtra e preserva a similaridade temática genuína.
_Evite_: reescrita de consulta (outra correção do lado da consulta: a reescrita reformula a própria consulta, enquanto o HyDE gera o embedding de uma resposta gerada em vez da consulta)

**Indexação incremental**:
Adicionar novos vetores a um índice já construído sem reconstruí-lo do zero. Bem suportada pelo HNSW, que não tem etapa de treinamento; mais fraca no IVFFlat, cujos centroides de cluster são fixados na construção e nunca recalculados, de modo que conteúdo novo que difere dos dados originais de treinamento pode ser mal agrupado.
_Evite_: reindexação (uma reconstrução completa do zero, necessária especificamente quando o modelo de embedding muda, e não a mesma operação que adicionar vetores novos de forma incremental a um índice inalterado)

**Ingestão**:
Transformar um documento-fonte bruto (um PDF, uma página HTML ou um arquivo de escritório) no texto limpo e estruturado sobre o qual o chunking de fato opera. Uma etapa genuína do pipeline, a montante do chunking, com seus próprios modos de falha, e não um detalhe de pré-processamento abaixo da atenção do pipeline.
_Evite_: tratar o chunking como a primeira etapa do pipeline (o chunking pressupõe que a ingestão já produziu texto limpo; a ingestão é o que de fato o produz)

**Filtragem por metadados**:
Restringir a recuperação aos chunks que satisfazem um predicado sobre atributos estruturados (tipo de documento, data, dono, tag de permissão), além da similaridade por vizinho mais próximo, em vez de buscar no corpus inteiro apenas por similaridade.
_Evite_: filtragem de permissão (um caso específico e de maior risco da filtragem por metadados, em que uma falha é um incidente de segurança e não uma regressão de qualidade, e que exige especificamente a pré-filtragem)

**Recuperação multi-hop**:
Recuperar em um loop no qual uma consulta posterior depende de um fato derivado de uma recuperação anterior, em vez de um conjunto fixo de subperguntas decidido de antemão. Necessária quando uma subpergunta nem sequer pode ser formulada até que a resposta de uma subpergunta anterior seja conhecida, o que a decomposição de consulta sozinha não consegue tratar.
_Evite_: decomposição de consulta (divide subperguntas já visíveis no texto da pergunta original; a recuperação multi-hop trata subperguntas que não existem até que a resposta de um hop anterior as produza)

**Pós-filtragem**:
Executar primeiro uma busca ANN e descartar depois os resultados que não passam em um predicado. Rápida, mas um predicado seletivo pode descartar a maior parte do que a varredura limitada de candidatos de um índice aproximado encontrou, derrubando o recall; no caso específico de um filtro de permissão, significa também que conteúdo não autorizado existiu brevemente no pipeline antes de ser descartado.
_Evite_: pré-filtragem (restringe o conjunto de candidatos antes de a busca ANN rodar, preservando o recall contra o conjunto filtrado e nunca deixando conteúdo não permitido entrar no pipeline)

**Pré-filtragem**:
Restringir o conjunto de candidatos apenas aos chunks que satisfazem um predicado antes de a busca ANN rodar, preservando o recall contra esse conjunto filtrado, não importa quão seletivo seja o predicado. Exigida especificamente para controle de acesso, já que o conteúdo não autorizado nunca chega a entrar no pipeline.
_Evite_: pós-filtragem (busca primeiro no índice inteiro e descarta depois; tanto o recall quanto, nos filtros de permissão, a própria garantia de segurança podem sofrer)

**Decomposição de consulta**:
Dividir uma pergunta composta em suas subperguntas separadas e recuperar para cada uma de forma independente, em vez de gerar o embedding da pergunta composta inteira como um único vetor que fica perto de nenhuma das passagens que responderiam bem a qualquer uma de suas partes.
_Evite_: expansão multiconsulta (uma técnica diferente: a expansão gera várias reformulações completas de uma pergunta, e a decomposição divide uma pergunta em subperguntas separadas e mais estreitas)

**Pontuação sem referência**:
Uma pontuação de relevância julgada por um LLM, calculada por chunk recuperado sem precisar de uma resposta correta conhecida e agregada em uma janela de tempo como taxa de acerto ou relevância média. É o que o monitoramento em produção usa no lugar de recall@k ou MRR, que exigem um conjunto de consultas rotulado ou sintético que a maior parte do tráfego real não tem.
_Evite_: recall@k, MRR (métricas offline que exigem resultados sabidamente corretos; a pontuação sem referência é especificamente o substituto em produção quando esses rótulos não existem)

**Reindexação**:
Reconstruir um índice vetorial do zero, necessário quando o próprio modelo de embedding muda, já que cada vetor existente foi produzido pelo espaço vetorial do modelo antigo e não compartilha distâncias comparáveis com os embeddings de um modelo novo. Uma operação diferente da indexação incremental e da manutenção periódica que exclusões e atualizações exigem.
_Evite_: indexação incremental (adicionar vetores novos a um índice inalterado; reindexação significa especificamente reconstruir tudo porque o modelo que produz os vetores mudou)
