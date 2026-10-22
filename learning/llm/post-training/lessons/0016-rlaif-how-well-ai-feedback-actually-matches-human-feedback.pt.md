---
title: "16. RLAIF: o quanto o feedback de IA realmente se iguala ao feedback humano"
description: "Um modelo julgando as próprias saídas, no seu próprio tamanho, ainda superou o fine-tuning supervisionado simples"
type: lesson
---

# Lição 16. RLAIF: o quanto o feedback de IA realmente se iguala ao feedback humano

**Ligação com a missão:** "Saber dizer de onde veio o feedback (humano ou de IA) em um dado pipeline de ajuste de segurança e o que isso implica em trocas" é o item de O sucesso se parece com isto a que esta etapa serve. A lição 15 cobriu um método construído sobre feedback de IA; esta lição cobre a comparação direta e controlada do feedback de IA com o feedback humano em várias tarefas.
**Fonte principal:** [Artigo científico: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
**Pré-requisitos:** [Lição 15](0015-constitutional-ai-feedback-from-a-model-not-a-human.md)

## Aquecimento

1. ▢ No RL-CAI, o que substitui o rotulador humano que ordinariamente julgaria qual de duas respostas amostradas é melhor?

<details markdown="1"><summary>Verificação</summary>

Um modelo. Um sistema de IA julga qual resposta é melhor, e um modelo de preferência é treinado nesse dataset de preferências geradas por IA.

</details>

2. ▢ Segundo a própria comparação de Bai et al., como os crowdworkers avaliaram o RL-CAI contra um modelo treinado com rótulos humanos de nocividade coletados anteriormente?

<details markdown="1"><summary>Verificação</summary>

Eles preferiram o RL-CAI ao modelo treinado em comparações rotuladas por humanos.

</details>

## Saiba isto

### Uma comparação controlada, frente a frente

Lee et al. fazem uma comparação direta que os próprios resultados do Constitutional AI apenas insinuavam: em três tarefas distintas, sumarização, geração de diálogo útil e geração de diálogo inofensivo, eles treinam uma policy com RLHF comum e uma segunda com **RLAIF**, em que um modelo de linguagem pronto para uso produz os rótulos de preferência em vez de um humano, mantendo todo o resto da configuração comparável. Avaliadores humanos então julgam os resultados.

### O resultado: comparável em duas tarefas, melhor na terceira

Em sumarização e em geração de diálogo útil, tanto o RLAIF quanto o RLHF são fortemente preferidos a um baseline de SFT simples (vencendo-o em 63% e 64% das vezes, respectivamente), e uma comparação direta frente a frente entre RLAIF e RLHF mostra que os dois são igualmente preferidos, sem diferença estatisticamente significativa entre eles. Em geração de diálogo inofensivo, Lee et al. relatam que o RLAIF na verdade **supera** o RLHF, sendo avaliado pelos avaliadores humanos como mais inofensivo. Nas três tarefas, substituir um dataset de preferências rotulado por humanos por um rotulado por IA não produziu um resultado pior; em duas tarefas igualou o RLHF e na terceira o superou.

### O resultado mais surpreendente: um modelo julgando o seu próprio tamanho, ou a si mesmo

Lee et al. vão além, em direção ao que chamam de "autoaperfeiçoamento": o RLAIF ainda superou o baseline de SFT simples mesmo quando o rotulador de IA que gerava as preferências tinha o mesmo tamanho da policy sendo treinada ou, no caso mais extremo, era exatamente o mesmo checkpoint de que a policy partiu. Um modelo pode ser levado a melhorar usando julgamentos de preferência produzidos por um modelo não mais capaz do que o que está sendo treinado, inclusive julgamentos produzidos por uma cópia anterior de si mesmo.

### Pulando totalmente o reward model: direct-RLAIF

Lee et al. introduzem mais uma simplificação: o **direct-RLAIF (d-RLAIF)**, que pula por completo o treinamento de um modelo de preferência separado e, em vez disso, consulta diretamente um modelo de linguagem pronto para uso para obter uma pontuação de recompensa, durante o próprio treinamento de RL. Remover do pipeline um modelo treinado inteiro, o reward model que a lição 8 já apontou como um fator de custo real no RLHF comum, não prejudicou o desempenho nos resultados deles; eles relatam que o d-RLAIF alcança desempenho melhor do que o RLAIF canônico, e não meramente desempenho comparável a um custo menor.

### O que isso defende, em conjunto com a lição 15

Entre o resultado do Constitutional AI (um pipeline de feedback de IA preferido a um de feedback humano) e a comparação controlada de Lee et al. (o feedback de IA igualando ou superando o feedback humano em três tarefas distintas, resistindo mesmo com escala reduzida do rotulador e tolerando a remoção de um reward model inteiro), a tese de que "feedback de IA" é um substituto menor, de reserva, para o feedback humano não se sustenta bem diante de nenhum dos dois resultados. Lee et al. enunciam a sua própria conclusão diretamente: o RLAIF oferece uma solução potencial para as limitações de escalabilidade de coletar feedback humano, e não meramente uma aproximação mais barata dele.

## Prática

1. ▢ Em sumarização e em geração de diálogo útil, como a taxa de vitória do RLAIF contra um baseline de SFT simples se comparou com a do RLHF, segundo Lee et al.?

<details markdown="1"><summary>Verificação</summary>

Sem diferença estatisticamente significativa: ambos venceram o baseline de SFT em taxas semelhantes (63% e 64%), e uma comparação direta frente a frente entre RLAIF e RLHF não mostrou preferência significativa por nenhum dos dois.

</details>

2. ▢ Em qual das três tarefas que Lee et al. testaram o RLAIF superou o RLHF, e não apenas o igualou?

<details markdown="1"><summary>Verificação</summary>

Geração de diálogo inofensivo. Os avaliadores humanos classificaram as respostas do RLAIF como mais inofensivas do que as do RLHF nessa tarefa especificamente.

</details>

3. ▢ O que é surpreendente no fato de o RLAIF ainda superar um baseline de SFT mesmo quando o rotulador de IA é exatamente o mesmo checkpoint da policy sendo treinada?

<details markdown="1"><summary>Verificação</summary>

Significa que os próprios julgamentos de preferência de um modelo sobre saídas, vindos de um modelo não mais capaz do que o que está sendo melhorado, ainda podem produzir uma melhora genuína em relação ao fine-tuning supervisionado simples, sem precisar de feedback de algo mais capaz nem de um humano.

</details>

4. ▢ O que o direct-RLAIF (d-RLAIF) remove do pipeline padrão de RLAIF, e o que Lee et al. constataram sobre o seu desempenho?

    - a) Remove o próprio modelo da policy; constataram desempenho pior
    - b) Remove o modelo de preferência/recompensa treinado separado, consultando diretamente um LLM pronto para uso para obter uma pontuação de recompensa durante o RL; constataram desempenho melhor do que o do RLAIF canônico
    - c) Remove por completo a etapa de RL, deixando apenas o SFT; o desempenho não mudou
    - d) Remove a necessidade de qualquer modelo de linguagem, usando em vez disso uma recompensa puramente baseada em regras

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente o que Lee et al. descrevem e relatam. As alternativas (a), (c) e (d) descrevem, cada uma, uma mudança diferente e sem relação no pipeline.

</details>

## Prática no mundo real

- [ ] Encontre onde um framework de treinamento ou pipeline de pesquisa a que você tenha acesso expõe uma opção de rotulagem de preferências por feedback de IA ou LLM-as-judge e verifique se ela se parece mais com o RLAIF canônico (um modelo de preferência treinado) ou com o direct-RLAIF (uma recompensa consultada ao vivo de um LLM).
- [ ] Leia a passagem do artigo de Lee et al. (linkado acima) que descreve o resultado de "autoaperfeiçoamento" e escreva, em uma frase, por que esse resultado é mais surpreendente do que o RLAIF simplesmente igualar o RLHF usando um rotulador de IA maior e mais capaz.
- [ ] Amanhã: para uma tarefa em que você poderia querer alinhar um modelo, decida se recorreria primeiro ao RLHF, ao RLAIF ou ao direct-RLAIF e escreva uma frase dizendo qual dos resultados desta lição (qualidade comparável, autoaperfeiçoamento em escala igual ou menor custo do pipeline) motivou a sua resposta.

## Para ir além

- [Artigo científico: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
- [Artigo científico: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Recursos](../RESOURCES.md)

---

A etapa 8 cobriu o feedback que vem de um modelo em vez de um humano, e o quanto ele de fato se sustenta. A etapa 9 passa a uma pergunta mais difícil que fica por baixo de tudo o que esta trilha cobriu: depois que um modelo está alinhado, como saber se o número que mede esse alinhamento está medindo a coisa real.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
