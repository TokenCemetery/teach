---
title: "10. A janela de contexto como orçamento"
description: "A janela de contexto é um recurso finito que o harness cura ativamente ao longo do tempo, e não um log inerte"
type: lesson
---

# Lição 10. A janela de contexto como orçamento

**Ligação com a missão:** Orçar o custo em tokens e a latência de um loop agêntico e dizer de qual parte do loop vem a amplificação.
**Fonte principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Pré-requisitos:** [Lição 9](0009-return-shapes-and-tool-set-bloat.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ No loop do agente da Lição 6, em que momento o harness decide qual chamada de ferramenta executar?

<details markdown="1"><summary>Verificação</summary>

O modelo emite um bloco de chamada de ferramenta (nome, parâmetros), e o harness o interpreta e executa a ferramenta. O modelo decide qual ferramenta processando a transcrição que recebe.

</details>

2. ▢ O que acontece com a transcrição toda vez que uma ferramenta termina?

<details markdown="1"><summary>Verificação</summary>

O resultado (ou erro) é anexado à transcrição, e a nova transcrição é enviada de volta ao modelo na iteração seguinte do loop.

</details>

## Saiba isto

### A transcrição cresce a cada turno, e fica cara depressa

Cada iteração do loop do agente anexa algo à transcrição. Depois que um agente roda por 10, 20 ou 100 turnos, a transcrição contém todas as mensagens, todas as chamadas de ferramenta e todos os resultados da execução inteira. Na iteração seguinte do loop, essa transcrição inteira volta ao modelo. Na iteração depois dessa, volta de novo, mais longa em mais um turno.

Isso significa que dois custos crescem com o comprimento da trajetória mesmo quando nada de novo está acontecendo:

- **Custo em tokens**: Cada mensagem ao modelo reenvia todos os turnos antigos. Uma trajetória de cinco turnos custa 5x menos tokens por chamada do que uma trajetória de 100 turnos. Em um agente de longa duração, isso se torna o custo dominante.
- **Latência**: Um contexto mais longo significa mais tokens para processar, o que é mais lento. O agente espera mais por cada resposta.

### Context rot: a atenção do modelo se degrada conforme o lixo se acumula

Conforme mais conteúdo de baixa relevância se acumula no contexto, a atenção do modelo fica mais ruidosa. A capacidade do modelo de distinguir o que ainda importa (o objetivo, as restrições recentes, os resultados sobre os quais ele ainda não agiu) se degrada quando isso está soterrado em uma pilha enorme de becos sem saída antigos e linhas de raciocínio abandonadas. Isso às vezes é chamado de "context rot". Um contexto inchado não é só caro: ele deixa o modelo pior na tarefa.

### O truncamento ingênuo é arriscado

O instinto mais simples é descartar os turnos mais antigos quando o contexto atinge um limite de tamanho. Mas o truncamento ingênuo corre o risco de perder, em silêncio, informação crítica. Se a fronteira do truncamento cair no meio de:

- Uma instrução de vários passos que o modelo ainda precisa seguir
- Um resultado sobre o qual o modelo ainda não agiu
- Uma restrição ou declaração de objetivo
- Parte de um system prompt ou de um exemplo

então o agente fica quebrado em silêncio, de formas que o harness não tem como detectar. O modelo não saberá que uma instrução-chave foi removida; ele simplesmente trabalhará com um entendimento incompleto e falhará de maneiras inesperadas.

### A curadoria ativa é uma escolha deliberada de design

Como o truncamento ingênuo é perigoso e o custo cresce com o comprimento da trajetória, o harness não pode tratar a transcrição como um log inerte que apenas cresce. "O que fica no contexto e o que sai" precisa ser uma decisão deliberada de design, embutida no harness. A trajetória continua existindo, mas o harness decide que parte dela o modelo vê em cada chamada.

Há duas estratégias principais para isso (cobertas na próxima lição): compactação e recuperação sob demanda.

## Prática

1. ▢ Um agente faz 50 chamadas de ferramenta em uma longa tarefa de pesquisa. Na chamada 51, o modelo recebe uma transcrição de 20.000 tokens. Na chamada 52, quantos tokens o modelo recebe na transcrição (aproximadamente)?

    - a) 20.000 tokens
    - b) 20.000 mais os tokens do novo resultado da chamada 51
    - c) 40.000 tokens
    - d) Depende do tamanho do resultado da chamada 51

<details markdown="1"><summary>Verificação</summary>

**b)** O modelo recebe a transcrição original de 20.000 tokens mais o novo resultado anexado. Se o resultado da chamada 51 tinha 500 tokens, o modelo recebe cerca de 20.500 tokens. O custo em tokens cresce a cada turno, e em execuções muito longas isso se torna uma despesa séria. A opção c está errada porque o modelo não recebe o resultado da chamada 51 duas vezes; a opção a ignora o novo trecho anexado; a opção d está correta em espírito (o tamanho do resultado importa), mas b é a resposta mais precisa.

</details>

2. ▢ Você está projetando um agente para uma tarefa de revisão de código. O agente lê arquivos, compara-os, faz anotações e produz um resumo. Por que é arriscado simplesmente descartar os resultados de ferramenta mais antigos quando a transcrição atinge um limite de 50.000 tokens?

<details markdown="1"><summary>Dica</summary>

E se a fronteira do truncamento cair entre uma leitura antiga de arquivo e uma comparação que o modelo ainda não terminou? E se uma restrição sobre o escopo dos arquivos estiver na parte que você descartou?

</details>

<details markdown="1"><summary>Verificação</summary>

O truncamento ingênuo pode descartar um resultado de ferramenta (como o conteúdo de um arquivo) a que o modelo ainda precisa se referir, ou uma restrição (como "revise apenas arquivos em src/core/") de que o modelo precisa se lembrar. O modelo não saberá que a informação está faltando; trabalhará em silêncio a partir de um quadro incompleto e produzirá conclusões erradas. O harness precisa ser mais esperto do que simplesmente cortar no limite de tokens.

</details>

3. ▢ Qual das alternativas a seguir é verdadeira sobre context rot?

    - a) Context rot só acontece se a transcrição contém erros
    - b) Context rot é evitado formatando bem os resultados de ferramenta
    - c) Uma transcrição grande com muitos turnos antigos irrelevantes deixa o modelo menos preciso, mesmo que nenhuma informação crítica seja truncada
    - d) Context rot não é um problema real em modelos modernos

<details markdown="1"><summary>Verificação</summary>

**c)** A atenção do modelo se degrada conforme conteúdo de baixa relevância se acumula. Uma transcrição grande e bagunçada dificulta ao modelo encontrar e priorizar o que importa. A opção a está errada porque becos sem saída e tarefas concluídas criam ruído mesmo sem erros. A opção b está errada porque uma boa formatação não resolve o problema da relação sinal-ruído. A opção d está errada porque context rot é bem documentado em tarefas de contexto longo.

</details>

4. ▢ Você observa que a latência de um agente aumenta conforme a trajetória cresce. Nomeie duas razões para isso acontecer.

<details markdown="1"><summary>Verificação</summary>

Primeiro, o modelo recebe mais tokens em cada chamada, o que leva mais tempo para processar. Segundo, o modelo precisa vasculhar mais conteúdo de baixa relevância (context rot) para encontrar a informação que importa, o que afeta a qualidade do raciocínio e pode levá-lo a cometer erros que desperdiçam turnos.

</details>

## Prática no mundo real

- [ ] Descreva a outra pessoa (ou em uma nota) por que você não pode simplesmente continuar descartando os turnos mais antigos de uma transcrição quando ela fica longa demais. Use um exemplo de uma tarefa real que você gostaria que um agente fizesse.
- [ ] Abra a transcrição de uma longa conversa de vários turnos que você teve com um modelo de linguagem e anote em que turno o modelo começa a ter dificuldade para lembrar das restrições do início.
- [ ] Amanhã: Planeje uma tarefa de pesquisa que um agente poderia fazer (ler 20 arquivos, comparar padrões, produzir um resumo) e esboce quão grande seria a transcrição se o agente mantivesse o conteúdo completo de cada arquivo na memória o tempo todo, contra se mantivesse apenas os caminhos dos arquivos e buscasse o conteúdo sob demanda.

## Para ir além

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
