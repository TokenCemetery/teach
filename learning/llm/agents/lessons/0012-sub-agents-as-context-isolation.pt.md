---
title: "12. Subagentes como isolamento de contexto"
description: "Iniciar um subagente isola o trabalho exploratório longo do orçamento de contexto do pai"
type: lesson
---

# Lição 12. Subagentes como isolamento de contexto

**Ligação com a missão:** Diagnosticar um agente que falha a partir da trajetória, em vez de acrescentar mais uma instrução ao prompt.
**Fonte principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Pré-requisitos:** [Lição 11](0011-compaction-and-retrieval-on-demand.md)

## Aquecimento

1. ▢ Qual é a diferença entre compactação e recuperação sob demanda?

<details markdown="1"><summary>Verificação</summary>

A compactação substitui turnos antigos por um resumo, economizando tokens mas arriscando perda de informação. A recuperação sob demanda mantém o detalhe antigo fora do contexto e o busca apenas quando o modelo o pede, trocando um pouco de latência por um contexto residente menor.

</details>

2. ▢ Em compactação mais recuperação sob demanda, quais três coisas o contexto sempre residente contém?

<details markdown="1"><summary>Verificação</summary>

O objetivo e as restrições, um resumo do progresso e metadados (nomes de arquivos, ferramentas disponíveis, títulos de documentos). O detalhe completo está comprimido (compactação) ou sob demanda (recuperação).

</details>

## Saiba isto

### Subagentes como ferramenta de gerenciamento de contexto

Até aqui, as lições 10 e 11 trataram de gerenciar a transcrição de um único agente. Mas há outra abordagem: iniciar um agente separado para fazer um trabalho delimitado. Isso é a etapa 8 (multiagente), mas aqui restrito apenas ao ângulo do orçamento de contexto.

Um subagente é uma execução de agente nova, com sua própria transcrição, seu próprio harness e seu próprio conjunto de ferramentas. Ele explora, faz chamadas de ferramenta, acumula sua própria trajetória. O agente pai, enquanto isso, não pagou o custo de nada dessa exploração. Nenhum dos turnos do subagente aparece na transcrição do pai.

Quando o subagente termina, ele produz um resultado final ou um resumo. Esse resumo (apenas algumas frases ou uma estrutura de dados) é anexado à transcrição do pai. Todo o raciocínio interno do subagente, todos os seus becos sem saída, todas as suas chamadas de ferramenta e falhas ficam fora do contexto do pai.

### A ideia-chave: uma trajetória grande e isolada não custa nada ao pai

Suponha que um subagente gaste 100 turnos lendo arquivos, comparando padrões, esbarrando em becos sem saída e refinando sua análise. A trajetória dele é enorme. Mas, da perspectiva do pai, todo esse trabalho é invisível. O pai só vê o relatório final, algumas centenas de tokens. Enquanto isso, o contexto do pai continua pequeno e barato.

Isso é diferente de compactação e recuperação sob demanda, que operam dentro de uma única transcrição. Um subagente opera inteiramente fora da transcrição do pai. O custo dele é arcado pelo harness do subagente, e não pelo do pai.

### O trade-off: raciocínio invisível significa detalhes perdidos

Como o raciocínio interno do subagente é invisível ao pai, informação que o pai não pensou em pedir pode se perder. Se o pai inicia um subagente para "ler estes arquivos e resumir", o subagente pode descobrir algo interessante, mas periférico: "Também notei um vazamento de memória em util.cpp." Se o pai não pediu isso, o subagente pode omiti-lo do relatório, e o pai nunca fica sabendo.

Isso é diferente do risco da compactação, em que o harness controla o que é resumido. Com um subagente, a fronteira entre "o que reportar" e "o que deixar interno" é escolha do próprio subagente. Se o subagente é um modelo de linguagem, ele estimará o que importa ao pai com base nas instruções que recebeu. Essa estimativa pode estar errada.

### Quando um subagente vale a pena e quando não

Um subagente vale o custo de coordenação quando:

- A subtarefa é grande e acumulará uma trajetória longa (muitos turnos, muitas chamadas de ferramenta, muitos becos sem saída).
- A subtarefa é delimitada: há um ponto de parada claro e o pai não precisará do raciocínio do subagente para o trabalho posterior.
- O custo de iniciar um novo agente (latência, sobrecarga de coordenação) é muito menor do que o custo de manter a exploração do subagente no contexto do pai.

Por exemplo: "Pesquise a história desta base de código, leia o git log e os principais PRs e me dê um resumo de três frases." Essa é uma tarefa grande e delimitada. Um subagente explorando por 50 turnos poupa ao pai 50 turnos de custo de contexto.

Um subagente não vale a pena quando:

- A tarefa é pequena (vai levar poucos turnos de qualquer forma).
- A tarefa exige coordenação estreita com o pai (o pai fará perguntas de esclarecimento, o subagente precisará refinar o trabalho).
- O pai precisará do raciocínio completo do subagente mais tarde (para entender por que uma conclusão foi alcançada, para identificar uma suposição, para depurar um erro).

Por exemplo: "Busque a temperatura de amanhã." Essa é uma tarefa de poucos turnos; iniciar um subagente custa mais do que simplesmente fazê-la no pai.

## Prática

1. ▢ Um agente tem a tarefa de revisar código em 50 arquivos e produzir um relatório. O desenvolvedor dividiu o trabalho: o agente principal revisa 5 arquivos e inicia um subagente para revisar os outros 45. Por que isto é um bom uso de um subagente?

    - a) Subagentes são sempre mais rápidos do que agentes únicos
    - b) A longa trajetória do subagente (revisar 45 arquivos) fica isolada do contexto do agente principal, mantendo o contexto principal pequeno e barato
    - c) Subagentes nunca cometem erros
    - d) O agente principal pode ver imediatamente todo o raciocínio do subagente

<details markdown="1"><summary>Verificação</summary>

**b)** Um subagente permite ao agente principal descarregar uma tarefa grande e delimitada. Os mais de 100 turnos de exploração do subagente não incham o contexto do agente principal. O agente principal recebe apenas o relatório final do subagente. A opção a está errada porque subagentes podem acrescentar latência. A opção c está errada porque subagentes podem cometer erros. A opção d está errada porque o raciocínio interno do subagente é invisível ao agente principal.

</details>

2. ▢ Um subagente está revisando uma base de código e descobre uma vulnerabilidade de segurança. Ela não tem relação direta com a tarefa que o pai pediu (revisão de estilo de código), mas é crítica. Que risco a invisibilidade do subagente cria aqui?

<details markdown="1"><summary>Dica</summary>

As instruções do subagente mandaram que ele focasse no estilo de código. Quem decide o que é reportado ao pai, e o que pode se perder?

</details>

<details markdown="1"><summary>Verificação</summary>

O subagente decide o que incluir em seu relatório final com base nas instruções. Se as instruções enfatizam o estilo de código, o subagente pode não reportar o problema de segurança, ou mencioná-lo como uma nota de rodapé que o pai deixa passar. Informação que o pai não pensou em pedir pode se perder porque o pai nunca vê o raciocínio completo do subagente. O pai precisa ser muito explícito: "Reporte qualquer coisa crítica que encontrar, seja de estilo ou não."

</details>

3. ▢ Compare duas abordagens para uma longa tarefa de pesquisa:
    - Abordagem A: Um único agente que compacta turnos antigos e usa recuperação sob demanda. Leva 80 turnos, o contexto residente fica abaixo de 30.000 tokens.
    - Abordagem B: O agente principal inicia 3 subagentes para explorar em paralelo. Cada um leva 40 turnos internamente. O agente principal recebe um resumo de cada. O contexto final do agente principal é de 5.000 tokens mais a sobrecarga de coordenação.

Qual abordagem tem o menor custo total em tokens (contando todas as execuções de agente), e por quê?

    - a) Abordagem A, porque evita a sobrecarga dos subagentes
    - b) Abordagem B, porque as três explorações ficam isoladas e baratas para o agente principal
    - c) Têm o mesmo custo
    - d) Depende de quanta sobrecarga de coordenação há

<details markdown="1"><summary>Verificação</summary>

**d)** A abordagem A envia 30.000 tokens ao modelo 80 vezes, cerca de 2,4M de tokens. A abordagem B envia cerca de 50.000 tokens ao modelo 40 vezes em cada subagente, mais a coordenação com o agente principal. Se a coordenação é mínima e o trabalho dos subagentes é de fato paralelo e delimitado, a abordagem B pode ser mais barata. Mas se a coordenação é cara ou os subagentes precisam refinar seus resultados iterativamente, a abordagem A pode ser melhor. A resposta depende do custo real de iniciar e coordenar os subagentes.

</details>

4. ▢ Você está projetando um agente para "depurar esta suíte de testes que falha e propor uma correção". Você deve usar um subagente, e por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não. Depurar é uma tarefa em que o pai provavelmente precisará do raciocínio completo do subagente para julgar se a correção proposta é segura, para identificar suposições ou para fazer perguntas de esclarecimento. Não é uma tarefa delimitada com um relatório simples; exige coordenação estreita. O raciocínio invisível do subagente seria um passivo. Melhor manter a depuração no loop principal do pai, onde ele pode acompanhar a trajetória completa.

</details>

## Prática no mundo real

- [ ] Descreva uma tarefa em que você usaria um subagente e explique por que uma trajetória grande e isolada vale o custo de coordenação.
- [ ] Descreva uma tarefa em que você não usaria um subagente e explique que informação se perderia se usasse.
- [ ] Amanhã: Esboce as responsabilidades do pai e do subagente para uma tarefa em várias partes (por exemplo, "pesquisar esta biblioteca e depois integrá-la à nossa base de código"). Onde fica a fronteira, e o que cada agente reporta ao outro?

## Para ir além

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
