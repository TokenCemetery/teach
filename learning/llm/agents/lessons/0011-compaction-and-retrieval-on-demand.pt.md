---
title: "11. Compactação e recuperação sob demanda"
description: "Duas estratégias para manter o contexto de um agente de longa duração dentro do orçamento preservando o que ainda importa"
type: lesson
---

# Lição 11. Compactação e recuperação sob demanda

**Ligação com a missão:** Orçar o custo em tokens e a latência de um loop agêntico e dizer de qual parte do loop vem a amplificação.
**Fonte principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Pré-requisitos:** [Lição 10](0010-the-context-window-as-budget.md)

## Aquecimento

1. ▢ Por que o truncamento ingênuo (descartar os turnos mais antigos quando um limite de tamanho é atingido) é arriscado?

<details markdown="1"><summary>Verificação</summary>

O truncamento ingênuo pode descartar um resultado de ferramenta, uma restrição ou uma instrução de que o modelo ainda precisa, e o modelo não saberá que a informação está faltando. Ele trabalhará em silêncio a partir de um entendimento incompleto e falhará de maneiras inesperadas.

</details>

2. ▢ O que é context rot?

<details markdown="1"><summary>Verificação</summary>

Conforme conteúdo de baixa relevância se acumula no contexto, a atenção do modelo fica mais ruidosa e ele tem dificuldade para distinguir o que ainda importa de becos sem saída antigos e raciocínio abandonado. Um contexto inchado é ao mesmo tempo caro e menos preciso.

</details>

## Saiba isto

### Compactação: substitua turnos antigos por um resumo

Uma estratégia é, periodicamente, substituir um trecho antigo da transcrição por um resumo condensado sobre o qual o modelo ainda consegue agir. Em vez de manter "Li file1.py e encontrei estas 50 linhas", você pode substituir toda essa sequência por "file1.py contém uma classe de banco de dados; os métodos principais são init, query, close."

O harness detecta quando a transcrição ficou longa e entrega os turnos antigos a um sumarizador (muitas vezes outra chamada ao modelo, ou uma extração mais simples). O resumo é inserido na transcrição no lugar dos turnos originais, mantendo o tamanho da transcrição sob controle.

**O risco:** O resumo pode descartar um detalhe que depois se revela importante. Se o agente mais tarde precisa saber que file1.py também definia uma função auxiliar, mas o resumo a omitiu, o agente perdeu essa informação permanentemente. Diferente do truncamento ingênuo (que é sempre arriscado), a compactação é deliberada e, em teoria, reversível, mas a perda de informação é real e difícil de prever.

### Recuperação sob demanda: dê ao agente uma ferramenta para buscar o detalhe de novo

Outra estratégia é não manter o detalhe completo no contexto de jeito nenhum. Em vez de carregar e guardar o conteúdo de cada arquivo, o harness mantém apenas um resumo (nome do arquivo, tamanho, data de modificação, uma breve nota de contagem de linhas). Quando o modelo precisa ver o conteúdo completo, ele chama uma ferramenta como "read_file" ou "re_fetch_detail". O modelo obtém o detalhe sob demanda e apenas do arquivo que está examinando no momento.

O trade-off: Cada busca acrescenta latência (mais uma chamada de ferramenta, mais uma ida e volta). Mas o contexto residente fica muito menor. Em uma tarefa longa que examina muitos arquivos mas só trabalha com alguns de cada vez, a recuperação sob demanda é muito mais barata em tokens totais do que manter cada arquivo no contexto para sempre.

### Combinadas: compactação + recuperação sob demanda

A abordagem mais poderosa combina as duas. O harness mantém um contexto pequeno e curado que contém:

- O objetivo e as restrições mais recentes
- Um resumo do que foi feito até agora
- Nomes de arquivos e metadados
- Descobertas recentes que importam

Resultados antigos e detalhados são comprimidos em resumos (compactação). Se o modelo precisa ver o detalhe completo de um arquivo ou resultado antigo, pode buscá-lo com uma ferramenta de recuperação (sob demanda). A memória de trabalho do modelo é pequena e rápida, mas ele tem um jeito de alcançar de volta o detalhe de que precisa.

Em um agente de revisão de código que revisa 100 arquivos ao longo de 200 turnos:

- Um agente ingênuo mantém no contexto todo arquivo já lido, chegando a 500.000 tokens no turno 50. Os turnos 51-200 são lentos e caros.
- Um agente esperto mantém no contexto apenas caminhos de arquivos e um resumo (5.000 tokens), com uma ferramenta "read_file". Ele busca cada arquivo sob demanda enquanto compara. O turno 50 custa quase o mesmo que o turno 200. O custo total em tokens da execução inteira é uma fração da abordagem ingênua.

## Prática

1. ▢ Você resume os primeiros 20 turnos da transcrição de um agente em um parágrafo: "O agente explorou três bases de código e encontrou gargalos de desempenho no caching." Esse resumo substitui os 20 turnos originais. Mais tarde, no turno 50, o modelo diz que quer entender a consulta exata que estava lenta. Que risco a compactação apresenta aqui?

    - a) O modelo se recusará a trabalhar sem os turnos originais
    - b) O resumo pode não ter registrado os detalhes exatos da consulta, e eles podem estar perdidos para sempre
    - c) A compactação é sempre sem perdas, então isto não é um risco
    - d) O modelo vai reler o resumo e lembrar da consulta

<details markdown="1"><summary>Verificação</summary>

**b)** A compactação descarta detalhes que podem importar depois. O resumo é conciso, mas pode omitir especificidades de que o modelo precisa mais adiante. Diferente do truncamento, a compactação é deliberada, mas a perda de informação é real. A opção a está errada porque o modelo trabalhará com o resumo, mas pode produzir resultados errados. A opção c está errada porque a compactação tem perdas por design. A opção d está errada porque o modelo trabalha apenas com o novo resumo, e não com o original.

</details>

2. ▢ Um agente está processando 200 documentos, resumindo cada um. Por que a recuperação sob demanda é melhor do que manter o conteúdo dos 200 documentos no contexto desde o início?

<details markdown="1"><summary>Dica</summary>

De quantos documentos o modelo normalmente precisa no contexto ao mesmo tempo? Se ele está resumindo o documento 45, precisa ter o conteúdo dos documentos 1 a 44 disponível agora?

</details>

<details markdown="1"><summary>Verificação</summary>

O modelo normalmente está focado em um ou poucos documentos de cada vez. Manter os 200 no contexto desperdiça tokens com conteúdo que o modelo não está examinando no momento. Com a recuperação sob demanda, o harness mantém no contexto apenas o documento atual e um resumo das descobertas anteriores. Se o modelo precisa reexaminar um documento antigo, ele o busca. O custo total em tokens para 200 documentos é muito menor do que manter os 200 na memória o tempo todo.

</details>

3. ▢ Em um sistema de compactação mais recuperação sob demanda, quais três coisas o contexto sempre residente deve conter?

<details markdown="1"><summary>Verificação</summary>

O objetivo e as restrições, um resumo do progresso até agora e metadados sobre os recursos disponíveis (nomes de arquivos, títulos de documentos, listas de ferramentas). O detalhe completo ou está comprimido em resumos (compactação) ou está disponível sob demanda (recuperação). Isso mantém o contexto residente pequeno e focado no que o modelo precisa para agir agora.

</details>

4. ▢ Você projeta um agente para ler artigos técnicos e extrair resumos. Depois de ler 50 artigos, o contexto está em 60.000 tokens. Compare duas abordagens:
    - Abordagem A: Compactar o conteúdo dos artigos antigos em resumos de um parágrafo a cada 10 artigos. Manter todos os resumos no contexto.
    - Abordagem B: Manter no contexto apenas títulos, autores e descobertas dos artigos. Dar ao agente uma ferramenta "re_read_paper" se ele precisar do texto completo.

Qual abordagem usa menos tokens no artigo 100, e por quê?

<details markdown="1"><summary>Verificação</summary>

A abordagem B usa menos tokens. Com a abordagem A, você acumula 10 resumos de 200-300 tokens cada, chegando a 2.000-3.000 tokens de conteúdo compactado no artigo 100. Com a abordagem B, você mantém apenas metadados (100-200 tokens) mais o texto do artigo atual (500 tokens), e o modelo raramente precisa reler um artigo antigo. A abordagem B economiza tokens por não guardar todos os resumos antigos o tempo todo.

</details>

## Prática no mundo real

- [ ] Faça uma auditoria na longa transcrição de um agente que você usou ou escreveu. Identifique quais partes ainda são relevantes (objetivo, restrições recentes, problemas em aberto) e quais podem ser compactadas ou apagadas com segurança. Escreva um resumo de uma frase que poderia substituir os primeiros 30% dos turnos.
- [ ] Projete um agente hipotético para uma tarefa com a qual você se importa (pesquisa, código, análise). Esboce se você usaria compactação, recuperação sob demanda ou ambas, e por quê.
- [ ] Amanhã: Pegue uma versão "burra" de um agente que mantém tudo no contexto, estime seu custo em tokens ao longo de 100 turnos, depois o redesenhe com compactação e recuperação sob demanda e estime o novo custo.

## Para ir além

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
