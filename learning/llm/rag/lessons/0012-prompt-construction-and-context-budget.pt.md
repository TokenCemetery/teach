---
title: "12. Construção de prompt e orçamento da janela de contexto"
description: "Por que os chunks recuperados competem por um orçamento compartilhado da janela de contexto, e por que o lugar onde um chunk fica no prompt importa tanto quanto ele ter sido recuperado"
type: lesson
---

# Lição 12. Construção de prompt e orçamento da janela de contexto

**Ligação com a missão:** A etapa 7 abre o último trecho da missão: mesmo um pipeline de recuperação perfeitamente diagnosticado e bem ajustado (etapas 1 a 6) ainda pode falhar com o usuário se os chunks recuperados forem montados em um prompt de forma ruim, o que é um ponto de falha distinto da própria recuperação.
**Fonte principal:** [Artigo científico: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Pré-requisitos:** [Lição 11](0011-diagnosing-the-pipeline.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ Qual é a primeira etapa a verificar ao diagnosticar um contexto recuperado errado, e por que ela é verificada antes de qualquer outra?

<details markdown="1"><summary>Verificação</summary>

O chunking: busque o chunk que deveria ter respondido à consulta e verifique se a informação relevante existe de forma coerente em um único lugar. Se o chunking dividiu ou enterrou a resposta, nenhuma etapa posterior (embedding, índice, ponderação híbrida, reranking) consegue recuperar aquilo a que nunca foi dada uma representação utilizável.

</details>

2. ▢ Por que diagnosticar sobre um pequeno conjunto de consultas que sabidamente falham é mais confiável do que depurar uma única falha anedótica?

<details markdown="1"><summary>Verificação</summary>

Uma única consulta que falha pode falhar por um motivo incomum e pontual que não reflete um problema sistêmico. Medir recall@k e MRR sobre um conjunto representativo de falhas revela onde ocorre a maior queda agregada, apontando uma etapa que está perdendo informação de forma sistemática.

</details>

## Saiba isto

### Os chunks recuperados são um item de linha em um orçamento compartilhado

Depois que os chunks são recuperados e ranqueados (etapas 1 a 6), eles ainda precisam se tornar parte de um prompt de verdade: tipicamente uma mensagem de sistema ou de instrução, os próprios chunks recuperados e a pergunta do próprio usuário, tudo dentro de uma única **janela de contexto** finita. Essa janela é um orçamento real e compartilhado: os chunks recuperados competem por espaço com o system prompt, qualquer histórico de conversa e a própria pergunta, e não apenas entre si. Recuperar mais chunks (um *k* maior) não é de graça, mesmo quando cada um deles é genuinamente relevante, já que cada um consome orçamento da janela de contexto que outra coisa, mais histórico de conversa, um system prompt mais longo, poderia usar.

### Estar no prompt não significa ser usado

A capacidade de um modelo de usar a informação depende de mais do que de ela estar tecnicamente presente na janela de contexto. O achado **"lost in the middle"** de Liu et al. mostra que os modelos usam a informação colocada bem no início ou bem no fim de um contexto longo de forma muito mais confiável do que a informação enterrada no meio, mesmo quando a informação enterrada está inteiramente dentro do limite de contexto declarado do modelo. Um chunk altamente relevante colocado no meio de um prompt longo e entupido de chunks pode ficar efetivamente invisível para a geração, produzindo uma resposta errada ou incompleta que parece uma falha de recuperação mas não é: o chunk foi recuperado corretamente; ele só não foi posicionado em um lugar de onde o modelo lê de forma confiável.

![Uma curva que traça quão confiavelmente um modelo usa uma informação recuperada em função de onde essa informação fica no prompt montado. A curva começa alta quando a informação está perto do início, cai ao ponto mais baixo quando a informação está no meio do contexto e volta a subir quando a informação está perto do fim, um formato de vale e não uma linha reta ou plana. Um chunk colocado no meio de um prompt longo e entupido de chunks é o usado de forma menos confiável, embora esteja tecnicamente presente na janela de contexto o tempo todo.](images/lost-in-the-middle.svg)

### A consequência prática para montar um prompt

Duas consequências decorrem diretamente. Primeiro, entupir o contexto com muitos chunks marginais e de menor relevância "por garantia" tem um custo além do orçamento de tokens: pode enterrar um chunk genuinamente bom no meio do prompt, piorando a resposta, e não apenas encarecendo. Segundo, a posição do chunk é uma escolha deliberada, não um acidente da ordem de inserção: colocar o chunk (ou chunks) mais relevante perto do início ou do fim do contexto montado, em vez de onde ele por acaso caiu depois da concatenação, importa para que a geração de fato se valha dele.

## Prática

1. ▢ Por que o orçamento da janela de contexto é uma preocupação da requisição inteira, e não algo sobre o qual a recuperação consiga raciocinar sozinha?

<details markdown="1"><summary>Verificação</summary>

Os chunks recuperados dividem a janela de contexto com o system prompt, qualquer histórico de conversa e a pergunta do usuário; o orçamento disponível para os chunks recuperados depende de quanto todo o resto da requisição está usando, e não apenas da qualidade da recuperação.

</details>

2. ▢ Descreva o fenômeno "lost in the middle" e uma implicação prática dele para montar um prompt de RAG.

<details markdown="1"><summary>Verificação</summary>

Os modelos usam a informação no início ou no fim de um contexto longo de forma muito mais confiável do que a informação enterrada no meio, mesmo quando ela está tecnicamente dentro da janela de contexto. Uma implicação prática: o chunk recuperado mais relevante deve ser colocado perto do início ou do fim do prompt montado, e não deixado onde a ordem de concatenação por acaso o pôs, e encher o prompt com muitos chunks extras marginais corre o risco de enterrar no meio um chunk genuinamente útil.

</details>

3. ▢ Uma equipe recupera os 20 primeiros chunks "por garantia", coloca-os em ordem de relevância, mas os concatena de modo que o chunk mais relevante acabe no meio do contexto montado. A geração perde uma resposta que estava de fato presente nesse chunk. O que provavelmente deu errado, e qual é uma correção?

<details markdown="1"><summary>Dica</summary>

Considere se isso é uma falha de recuperação ou algo que acontece depois que a recuperação teve sucesso.

</details>

<details markdown="1"><summary>Verificação</summary>

Isso não é uma falha de recuperação: o chunk correto foi recuperado. É uma falha de construção de prompt causada pelo efeito lost-in-the-middle, já que o chunk mais relevante acabou posicionado no meio de um contexto longo, onde os modelos são menos confiáveis ao usar informação. Uma correção: reordenar o prompt montado para que o chunk mais relevante fique perto do início ou do fim, ou reduzir o número de chunks incluídos para que o bom não fique enterrado entre muitos de menor relevância.

</details>

4. ▢ Por que "a recuperação encontrou o chunk certo" (a pergunta da etapa 6) e "o prompt montado fez o modelo de fato usá-lo" são pontos de falha diferentes, mesmo que ambos possam produzir o mesmo sintoma (uma resposta final errada)?

<details markdown="1"><summary>Verificação</summary>

O procedimento de diagnóstico da etapa 6 verifica se o chunk correto foi recuperado e ranqueado alto o bastante para chegar à geração; trata inteiramente do pipeline até esse ponto. Se o modelo de fato usa um chunk que chegou ao prompt é uma pergunta separada, governada por onde esse chunk fica no contexto montado, o que o lost-in-the-middle mostra que importa independentemente da qualidade da recuperação. Uma resposta errada pode resultar de qualquer uma das falhas, mas elas exigem correções diferentes.

</details>

5. ▢ Qual afirmação é verdadeira sobre o orçamento da janela de contexto e a posição dos chunks em um prompt de RAG?

    - a) Recuperar mais chunks é sempre melhor, já que mais contexto só pode ajudar o modelo
    - b) Um chunk tecnicamente dentro da janela de contexto tem garantia de ser usado do mesmo modo, independentemente de onde fique
    - c) Os chunks recuperados competem por um orçamento compartilhado com o resto da requisição, e onde um chunk é colocado no prompt montado afeta se o modelo de fato o usa
    - d) O lost-in-the-middle afeta apenas documentos muito longos, não um prompt montado a partir de vários chunks recuperados separados

<details markdown="1"><summary>Verificação</summary>

**c)** Tanto o ponto do orçamento compartilhado quanto o da posição são estabelecidos nesta lição. (a) é falsa: mais chunks custam orçamento e podem enterrar um chunk bom no meio, prejudicando em vez de ajudar. (b) é falsa: é exatamente isso que o lost-in-the-middle refuta. (d) é falsa: o efeito diz respeito à posição dentro do contexto geral, independentemente de esse contexto vir de um documento longo ou de vários chunks concatenados.

</details>

## Prática no mundo real

- [ ] Para um sistema RAG que você executa ou pretende executar, verifique onde, no prompt montado, o chunk recuperado mais relevante costuma ficar e se isso é uma escolha deliberada ou um acidente da ordem de concatenação.
- [ ] Calcule quanto do orçamento total da sua janela de contexto é gasto com o system prompt e o histórico de conversa em comparação com os chunks recuperados, em uma requisição típica.
- [ ] Amanhã: tente reduzir o número de chunks que você recupera para uma consulta em que a geração hoje parece perder informação relevante e verifique se só isso muda a qualidade da resposta.

## Para ir além

- [Artigo científico: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Artigo: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
