---
title: "6. O que os exemplos few-shot ensinam"
description: "As demonstrações ensinam principalmente o formato, o espaço de rótulos e a distribuição das entradas, o que muda a forma de escolhê-las"
type: lesson
---

# Lição 6. O que os exemplos few-shot ensinam

**Ligação com a missão:** Escolher bem os exemplos few-shot começa por saber o que o modelo tira deles, e a evidência diz que são menos as respostas e mais o formato da tarefa.
**Fonte principal:** [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
**Pré-requisitos:** [Lição 5](0005-format-sensitivity.md), [Prompt few-shot](../GLOSSARY.md), [Prompt zero-shot](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 4 separou instruções de dados com tags. Nomeie uma coisa em um prompt few-shot que deveria ficar dentro de sua própria tag, e por quê.

<details markdown="1"><summary>Verificação</summary>

Os exemplos, agrupados (por exemplo em uma tag examples com uma tag por exemplo), para que o modelo distinga as demonstrações das instruções e da entrada real. Sem as tags, um exemplo pode ser lido como instrução, ou a entrada real como mais um exemplo.

</details>

2. ▢ A lição 5 disse que uma mudança de formatação sem significado pode alterar a acurácia. O que isso prevê sobre dois prompts few-shot cujos exemplos são idênticos, mas um escreve `Label:` e o outro `Answer:`?

<details markdown="1"><summary>Verificação</summary>

Que a acurácia deles pode diferir, então não se sabe qual é melhor até que os dois sejam testados. A edição não muda nenhum significado, mas muda a sequência de tokens que o modelo continua, que é o ponto da lição 5.

</details>

## Saiba isto

### O resultado surpreendente

Um **prompt few-shot** mostra ao modelo pares de entrada e saída antes da entrada real. O palpite óbvio é que o modelo aprende o mapeamento de entrada para saída a partir deles, como um classificador aprende com dados rotulados. Min et al. testaram esse palpite substituindo os rótulos das demonstrações por rótulos aleatórios. Em 12 modelos, incluindo o GPT-3, o desempenho quase não caiu: de 0 a 5% absolutos para quase todos os modelos, 2,6% em média para tarefas de classificação e 1,7% para tarefas de múltipla escolha.

Se rótulos corretos não são o que ajuda, outra coisa nas demonstrações deve ser. O paper nomeia três, e cada uma foi testada removendo-a:

| O que a demonstração fornece | O que acontece quando é removido |
|---|---|
| O espaço de rótulos: o conjunto de respostas que o modelo pode dar | Trocar os rótulos por palavras aleatórias do inglês custou de 5 a 16% absolutos para modelos diretos |
| A distribuição das entradas: texto parecido com as entradas reais | Trocar as entradas por texto aleatório de um corpus custou de 3 a 16% absolutos para a maioria dos modelos testados |
| O formato: entrada e depois rótulo, repetidos | Desfazer o pareamento deixou o desempenho próximo de, ou pior que, não ter demonstrações |

### O que isto não diz

Três limites impedem que isto vire "rótulos não importam".

Os modelos iam do GPT-2 Large ao GPT-3 (de 774M a 175B de parâmetros), e as tarefas eram de classificação e múltipla escolha. O paper não testa se um modelo de chat atual se comporta da mesma forma, então trate-o como uma forte expectativa prévia e depois teste o seu modelo.

Rótulos aleatórios ainda custam alguma coisa, e o custo não foi uniforme: um modelo em classificação caiu quase 10% quando todo rótulo estava errado. "Quase não prejudica" é uma média sobre os modelos e tarefas testados.

Os autores também observam que o aprendizado em contexto pode não funcionar em uma tarefa cuja correspondência entre entrada e rótulo o modelo ainda não tenha capturado. As demonstrações localizam uma tarefa que o modelo já sabe fazer em boa parte. São uma forma mais fraca de ensinar um mapeamento que ele nunca viu.

### Como isto muda a escolha dos exemplos

Se o modelo lê formato, espaço de rótulos e distribuição das entradas nos exemplos, essas três coisas são as que precisam estar certas.

- **No formato-alvo.** Todo exemplo deve ser exatamente como a entrada real e a saída que você quer, até a caixa e a pontuação. A lição 5 explica por que pequenas diferenças não são de graça.
- **Cobrindo o espaço de rótulos.** Mostre todo rótulo que o modelo pode produzir, para que nenhum seja surpresa.
- **Parecidos com as entradas reais.** Use texto da distribuição real, e não frases inventadas e arrumadinhas.

O guia de boas práticas da Anthropic diz o mesmo em termos de praticante: faça exemplos relevantes (que espelhem o caso de uso real), diversos (que cubram casos de borda e variem o suficiente para o modelo não captar padrões indesejados) e estruturados (envolvidos em tags), e sugere de 3 a 5 exemplos. Esse é o conselho documentado de um fornecedor, e não um resultado medido.

Nada disso é licença para entregar rótulos errados. Rótulos corretos não custam nada e evitam o pior caso do paper.

## Prática

1. ▢ Preveja, depois execute. Cole este prompt em uma janela de chat. Os rótulos dos três exemplos estão errados de propósito. Preveja o que o modelo produz para a última avaliação, depois execute.

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>Dica</summary>

Pergunte o que os exemplos ainda ensinam mesmo quando seus rótulos estão errados: o formato, as duas palavras permitidas e como é uma avaliação.

</details>

<details markdown="1"><summary>Verificação</summary>

Min et al. preveem uma resposta de uma palavra do par permitido e, para uma avaliação inequívoca, muito provavelmente a correta (Negative), porque a noção que o próprio modelo tem da tarefa sobrevive a rótulos errados. Um modelo que em vez disso copia o mapeamento trocado é uma descoberta sobre esse modelo, e não um erro do paper. De qualquer modo, o formato de saída (uma única palavra depois de `Label:`) deve se manter, já que o formato é o que os exemplos ensinaram de forma confiável.

</details>

2. ▢ Qual mudança em um prompt few-shot que funciona o paper prevê que mais prejudica?

    - a) Trocar os rótulos de modo que alguns exemplos tragam uma resposta errada
    - b) Substituir as entradas dos exemplos por frases aleatórias de um corpus
    - c) Reordenar os mesmos exemplos mantendo todos os rótulos corretos
    - d) Adicionar mais um exemplo que siga o formato existente

<details markdown="1"><summary>Verificação</summary>

**b)** Substituir as entradas por texto fora da distribuição custou de 3 a 16% absolutos para a maioria dos modelos testados, mais que rótulos errados (de 0 a 5% para quase todos). (a) é a manchete do paper: custo pequeno. (c) não é testada neste paper; a ordem é o tema da lição 7, e não é inofensiva. (d) acrescenta uma demonstração no formato certo, o que, segundo o paper, não altera muito os resultados depois de uns 8 exemplos.

</details>

3. ▢ Este prompt serve para etiquetar tickets de suporte. Nomeie todas as maneiras pelas quais seus exemplos deixam de ensinar o formato, o espaço de rótulos ou a distribuição das entradas, e diga o que você mudaria.

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>Dica</summary>

Compare os três exemplos linha a linha. Eles compartilham um layout? Compartilham a grafia e a pontuação do rótulo? Conte os rótulos.

</details>

<details markdown="1"><summary>Verificação</summary>

Formato: o segundo exemplo abandona `Ticket:` e `Tag:` e acrescenta uma frase de comentário, então o padrão é quebrado uma vez. Espaço de rótulos: `billing`, `bug` e `Account.` diferem em caixa e pontuação, então o modelo vê três grafias de rótulo onde a tarefa tem três rótulos exatos. O rótulo `Account.` com ponto final ensina que a pontuação faz parte da resposta. Distribuição das entradas: os tickets têm uma linha curta cada e podem não se parecer com tickets reais (que são mais longos e mais bagunçados). Correção: um único layout para todos os exemplos, a grafia exata do rótulo todas as vezes e tickets copiados de tickets reais.

</details>

4. ▢ Um classificador deve produzir um entre Billing, Bug, Account. Deste conjunto, escolha os três exemplos que você usaria e diga por que rejeitou os demais.

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>Verificação</summary>

Uma escolha razoável é A, C e E: um exemplo por rótulo cobre o espaço de rótulos, eles compartilham um layout e a redação crua e com cara de real combina com a distribuição das entradas. B é quase uma duplicata de A, então não acrescenta diversidade. D é prosa polida que não parece um ticket (um descompasso de distribuição das entradas) e está rotulada como Bug pelo motivo errado. F é boa por si só, mas um segundo exemplo de Billing antes de qualquer outro rótulo arrisca o viés de que trata a lição 7. Outras escolhas são defensáveis se cobrirem os três rótulos e evitarem D.

</details>

## Prática no mundo real

- [ ] Pegue um prompt few-shot que você já usa. Liste qual entre formato, espaço de rótulos e distribuição das entradas cada exemplo mostra, e sinalize qualquer exemplo que não mostre nenhum.
- [ ] Execute um prompt duas vezes, uma com exemplos reais e outra com os mesmos exemplos rotulados ao acaso, sobre cinco entradas. Anote quantas respostas mudaram.
- [ ] Amanhã: reescreva um prompt few-shot para que todo exemplo compartilhe um único layout e a grafia exata do rótulo, depois execute-o sobre as mesmas cinco entradas e compare.

## Para ir além

- [Few-Shot e Raciocínio](../reference/few-shot-and-reasoning.md)
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
