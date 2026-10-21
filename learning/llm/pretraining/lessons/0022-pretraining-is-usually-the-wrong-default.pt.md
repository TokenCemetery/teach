---
title: "22. Pré-treinar costuma ser o padrão errado"
description: "Uma segunda fase de pré-treinamento sobre um modelo existente traz a maior parte do benefício sem pagar o custo completo de novo"
type: lesson
---

# Lição 22. Pré-treinar costuma ser o padrão errado

**Ligação com a missão:** "Decidir se uma tarefa declarada pede pré-treinamento, pré-treinamento continuado ou fine-tuning de um modelo base existente e defender a escolha pelo custo" é o item de O sucesso se parece com isto que a etapa 10 fecha. Esta lição faz o argumento contra o padrão a que a maioria dos recém-chegados recorre; a Lição 23 cobre a defesa de um orçamento quando o pré-treinamento de fato é a decisão certa e a Lição 24 cobre a revisão do orçamento de outra pessoa.
**Fonte principal:** [Artigo científico: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
**Pré-requisitos:** [Lição 21](0021-periodic-held-out-evaluation.md)

## Aquecimento

1. ▢ Por que Rae et al. filtraram explicitamente certos benchmarks para fora do conjunto de treinamento do Gopher antes de usá-los como verificações de avaliação periódica?

<details markdown="1"><summary>Verificação</summary>

Para que uma boa pontuação nesses benchmarks não pudesse ser explicada pelo fato de o modelo simplesmente ter visto e memorizado aquele texto exato durante o treinamento; um benchmark em que o modelo foi treinado não consegue distinguir capacidade genuína de memorização.

</details>

2. ▢ O que avaliar periodicamente durante o treinamento, e não apenas uma vez no final, realmente traz a uma equipe?

<details markdown="1"><summary>Verificação</summary>

Permite que um bug, uma regressão ou uma divergência de capacidade seja pego e potencialmente tratado enquanto a execução ainda está em andamento, em vez de descoberto só depois de o orçamento de compute completo já ter sido gasto.

</details>

## Saiba isto

### Por que "precisamos do nosso próprio modelo pré-treinado" costuma ser o instinto errado

Cada etapa desta trilha vem construindo em direção a um fato honesto: pré-treinar um modelo do zero é extraordinariamente caro. Só a aritmética compute-optimal da etapa 3, um modelo de 70 bilhões de parâmetros querendo algo da ordem de um trilhão de tokens, dá uma noção da escala de compute que uma única execução do zero exige, antes de contar o custo de engenharia da infraestrutura de treinamento distribuído que as etapas 4 a 6 cobriram ou o custo operacional do monitoramento e da tolerância a falhas que as etapas 8 e 9 cobriram. Querer um modelo bom em um domínio específico, em uma tarefa específica ou em um estilo específico não justifica, por si só, pagar todo esse custo de novo. A pergunta que vale fazer primeiro não é "como pré-treinamos um modelo para isto", mas "isto realmente precisa de um novo modelo pré-treinado".

### A evidência de uma alternativa mais barata

Gururangan et al. respondem a isso diretamente para um caso comum: adaptar um modelo pré-treinado existente de cobertura ampla a um domínio específico, em vez de pré-treinar um novo para esse domínio. Eles pegam o RoBERTa, um grande modelo pré-treinado existente, e continuam o pré-treinamento dele com texto não rotulado de um domínio-alvo, uma **segunda fase de pré-treinamento** que chamam de **pré-treinamento adaptativo ao domínio (DAPT)**, antes de avaliar em tarefas desse domínio. Em quatro domínios (artigos biomédicos, artigos de ciência da computação, notícias e resenhas) e oito tarefas de classificação, eles constatam que isso melhora de forma consistente o desempenho nas tarefas do domínio-alvo, tanto em cenários de muitos quanto de poucos recursos, sempre que o domínio-alvo não estava já bem representado no pré-treinamento original do modelo. Constatam ainda que adaptar mais a fundo aos dados não rotulados da própria tarefa, o **pré-treinamento adaptativo à tarefa (TAPT)**, melhora o desempenho de novo por cima do DAPT, e que até uma alternativa mais barata, adaptar-se a um corpus da tarefa construído com heurísticas simples de seleção de dados, funciona bem quando o pré-treinamento adaptativo ao domínio completo não é acessível.

### O que isso defende e o que não defende

Nada disso afirma que pré-treinar do zero nunca se justifica; afirma que a suposição padrão deveria correr no sentido contrário. Continuar o pré-treinamento de um modelo existente e já amplamente capaz, a uma pequena fração do compute que uma execução do zero exigiria, captura de forma consistente uma parcela real do benefício que um modelo totalmente específico do domínio poderia ter oferecido. Uma tarefa que parece pedir "um modelo bom no nosso domínio" é, segundo essa evidência, muito frequentemente mais bem atendida por pré-treinamento continuado sobre um modelo base existente, ou, se a tarefa for ainda mais restrita, pelo fine-tuning com adapters que `llm/finetuning` cobre, do que por pagar por uma nova execução de pré-treinamento. Recorrer ao pré-treinamento completo antes de descartar essas opções mais baratas é o erro específico contra o qual esta lição argumenta, a versão em escala de pré-treinamento da mesma disciplina que a própria lição de julgamento de `llm/finetuning` aplica um nível abaixo, quando o próprio fine-tuning com adapters também não é a decisão certa.

### Quando pré-treinar do zero ainda é a decisão certa

Os casos em que de fato é incluem: um idioma ou domínio-alvo tão distante dos dados de treinamento e do tokenizer de qualquer modelo base disponível que nenhuma quantidade de pré-treinamento continuado ou de fine-tuning consegue fechar a distância; um requisito de licenciamento ou de proveniência que descarta os dados de treinamento de todos os modelos base disponíveis; ou uma mudança deliberada de arquitetura (as escolhas de paralelismo da etapa 6, um mecanismo de atenção fundamentalmente diferente) para a qual um checkpoint existente não pode ser adaptado depois do fato. Essas são a exceção que esta lição espera que quem lê consiga nomear, e não a regra.

## Prática

1. ▢ Uma equipe quer um modelo que se saia bem em documentos jurídicos e há um modelo base existente de cobertura ampla disponível. Segundo a evidência de Gururangan et al., o que esta lição recomendaria tentar antes de pré-treinar um modelo novo do zero?

<details markdown="1"><summary>Verificação</summary>

Pré-treinamento adaptativo ao domínio: continuar a pré-treinar o modelo base existente com texto jurídico não rotulado, o que Gururangan et al. constataram melhorar de forma consistente o desempenho no domínio-alvo em cenários de muitos e de poucos recursos, a uma fração do custo de uma nova execução de pré-treinamento do zero.

</details>

2. ▢ Qual destas é uma razão legítima para pré-treinar do zero mesmo assim, segundo esta lição?

    - a) O domínio-alvo é levemente diferente do texto geral da web
    - b) O tokenizer ou os dados de treinamento de nenhum modelo base disponível cobrem o idioma ou domínio-alvo, e o pré-treinamento continuado não consegue fechar essa distância
    - c) Uma nova execução de pré-treinamento pareceria mais impressionante em um relatório
    - d) O fine-tuning levaria mais de um dia para ser configurado

<details markdown="1"><summary>Verificação</summary>

**b)** é a exceção genuína que esta lição nomeia. (a) é exatamente o caso que a evidência de Gururangan et al. defende que o pré-treinamento continuado trata bem, e não uma razão para pré-treinar do zero. (c) e (d) não são razões defensáveis sob o argumento de custo desta lição.

</details>

3. ▢ Qual é a diferença entre o pré-treinamento adaptativo ao domínio (DAPT) e o pré-treinamento adaptativo à tarefa (TAPT), segundo Gururangan et al.?

<details markdown="1"><summary>Verificação</summary>

O DAPT continua o pré-treinamento com texto não rotulado de um domínio-alvo amplo (como todos os artigos biomédicos). O TAPT continua o pré-treinamento especificamente com os dados não rotulados da própria tarefa, um corpus mais restrito, e Gururangan et al. constataram que ele melhora o desempenho mesmo depois de o DAPT já ter sido aplicado.

</details>

4. ▢ Uma equipe não pode pagar uma execução completa de pré-treinamento adaptativo ao domínio, mas ainda quer parte do seu benefício. Que alternativa o trabalho de Gururangan et al. sugere?

<details markdown="1"><summary>Verificação</summary>

Adaptar-se a um corpus da tarefa construído com estratégias simples de seleção de dados, que Gururangan et al. constataram ser uma alternativa eficaz e mais barata quando não há recursos para o pré-treinamento adaptativo ao domínio completo.

</details>

## Prática no mundo real

- [ ] Encontre um exemplo publicado de um modelo adaptado a um domínio (um model card ou artigo de um "BioBERT", "SciBERT", "FinBERT" ou similar) e identifique se ele foi construído por pré-treinamento continuado sobre um modelo base existente ou pré-treinado totalmente do zero.
- [ ] Leia a introdução de Gururangan et al. (linkada acima) e escreva uma frase sobre por que eles escolheram especificamente testar o pré-treinamento adaptativo ao domínio em vários domínios, e não em apenas um, antes de tirar uma conclusão geral.
- [ ] Amanhã: para um domínio ou tarefa-alvo hipotético à sua escolha, escreva um parágrafo argumentando a favor ou contra pré-treinar um novo modelo do zero, citando pelo menos uma evidência desta lição ou de uma etapa anterior desta trilha.

## Para ir além

- [Artigo científico: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
- [`llm/finetuning`](../../finetuning/): a mesma disciplina aplicada um nível abaixo, quando o pré-treinamento continuado ainda é mais do que uma tarefa mais restrita precisa
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
