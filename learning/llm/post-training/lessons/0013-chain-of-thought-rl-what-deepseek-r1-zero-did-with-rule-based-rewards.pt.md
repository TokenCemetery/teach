---
title: "13. RL com chain-of-thought: o que o DeepSeek-R1-Zero fez com recompensas baseadas em regras"
description: "Nenhum reward model aprendido, nenhum passo de SFT antes, e mesmo assim o raciocínio estendido surgiu porque continuava acertando mais respostas"
type: lesson
---

# Lição 13. RL com chain-of-thought: o que o DeepSeek-R1-Zero fez com recompensas baseadas em regras

**Ligação com a missão:** "Saber dizer como o comportamento de um modelo de raciocínio foi produzido, e não apenas como fazer prompt nele" é o item de O sucesso se parece com isto a que esta etapa serve. Esta lição cobre o treinamento de RL puro do DeepSeek-R1-Zero e o que surgiu dele; a lição 14 cobre a correção que o transformou em um modelo utilizável, e o que a destilação trouxe além disso.
**Fonte principal:** [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Pré-requisitos:** [Lição 12](0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md)

## Aquecimento

1. ▢ O que é uma recompensa verificável, e por que ela não tem o mesmo modo de falha de reward hacking que um reward model treinado tem?

<details markdown="1"><summary>Verificação</summary>

Um sinal de recompensa produzido por um verificador determinístico em vez de por um modelo aprendido; como nenhuma peculiaridade de um modelo aprendido fica entre a saída e a sua pontuação, não há exploit específico de reward model para uma policy aprender, como há com um reward model treinado.

</details>

2. ▢ Por que uma recompensa verificável é uma má escolha para treinar respostas de suporte ao cliente mais empáticas?

<details markdown="1"><summary>Verificação</summary>

Não há verificador determinístico para "esta resposta foi adequadamente empática"; as recompensas verificáveis servem a tarefas em que a correção é verificável desde o início, e o tom não é esse tipo de propriedade.

</details>

## Saiba isto

### Treinando diretamente em um base model, sem um passo de SFT antes

O DeepSeek-R1-Zero é treinado com RL em larga escala aplicado diretamente a um base model pré-treinado, sem nenhum passo de SFT antes, pulando por completo a primeira etapa do pipeline usual de três passos da lição 1. A recompensa contra a qual ele treina é puramente **baseada em regras**, construída a partir de exatamente duas checagens: uma **recompensa de acurácia**, que para problemas de matemática verifica se a resposta final, dada em um formato especificado, como dentro de uma caixa, coincide exatamente com a correta, ou, para problemas de programação, executa um compilador contra casos de teste predefinidos; e uma **recompensa de formato**, que verifica apenas se o processo de raciocínio do modelo está colocado entre um par de tags que marcam onde ele começa e termina. A DeepSeek-AI afirma diretamente que não aplica nenhum reward model neural, nem de resultado nem de processo: nenhum reward model treinado, de qualquer tipo, fica entre a saída do modelo e a sua pontuação.

### O raciocínio estendido surgiu, não foi programado

Nada nesse desenho de recompensa instrui explicitamente o modelo a raciocinar por mais tempo, mostrar passos intermediários ou reconsiderar um caminho errado. A DeepSeek-AI relata que esses comportamentos surgiram mesmo assim, ao longo do treinamento de RL: como uma recompensa de acurácia baseada em regras simplesmente recompensa acertar a resposta final, e um raciocínio mais longo e cuidadoso tende a acertar mais respostas finais, o treinamento de RL selecionou naturalmente mais dele, sem que ninguém especificasse "raciocine por mais tempo" como alvo.

### O "momento aha"

A DeepSeek-AI descreve uma instância específica e marcante disso: em um ponto intermediário do treinamento, o DeepSeek-R1-Zero começou a dedicar mais tempo de raciocínio a um problema especificamente reavaliando a sua própria abordagem inicial no meio do caminho, um comportamento de autocorreção para o qual ninguém escreveu diretamente um termo de recompensa. Eles descrevem isso como "não apenas um 'momento aha' para o modelo, mas também para os pesquisadores que observavam o seu comportamento", e o apresentam como uma demonstração do que o treinamento de RL torna possível e a instrução direta não: em vez de ensinar explicitamente o modelo a resolver um problema, as recompensas baseadas em regras forneceram o incentivo certo, e um comportamento genuinamente novo de resolução de problemas surgiu da otimização contra ele.

### O que o RL puro sozinho não corrigiu

A capacidade de raciocínio do DeepSeek-R1-Zero veio com custos reais que a DeepSeek-AI não esconde: legibilidade ruim e mistura de idiomas (alternar entre idiomas dentro de uma única resposta de um jeito que nenhum usuário pediu). Nada em uma recompensa puramente baseada em regras e só de correção dá ao modelo qualquer incentivo para ser legível ou para ficar em um único idioma; essas checagens nunca fizeram parte da pontuação, então nada selecionou para elas. O próprio DeepSeek-R1, o modelo construído para corrigir isso, é o assunto da lição 14.

## Prática

1. ▢ A recompensa do DeepSeek-R1-Zero não tem nenhum termo explícito que recompense cadeias de raciocínio mais longas, mas o comprimento do raciocínio do modelo cresceu substancialmente ao longo do treinamento. O que o relato desta lição diz que de fato impulsionou esse crescimento?

<details markdown="1"><summary>Verificação</summary>

A recompensa de acurácia simplesmente recompensa acertar a resposta final, e um raciocínio mais longo e cuidadoso tendia a produzir mais respostas finais corretas, então o treinamento de RL selecionou para ele como efeito colateral de otimizar a correção, e não porque o comprimento do raciocínio fosse recompensado diretamente.

</details>

2. ▢ Por que a DeepSeek-AI descreve a recompensa de acurácia como "baseada em regras" em vez de como um reward model?

    - a) Ela ainda é uma rede neural treinada, só que menor
    - b) É uma checagem determinística (correspondência exata contra uma resposta conhecida, ou um compilador executando casos de teste fixos), sem nenhum modelo aprendido envolvido na produção da pontuação
    - c) É baseada em regras apenas para problemas de código, e um reward model neural é usado para matemática
    - d) "Baseada em regras" e "reward model" significam a mesma coisa neste artigo

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente o que a DeepSeek-AI afirma: nenhum reward model neural, de resultado ou de processo, é aplicado. As alternativas (a) e (c) pressupõem um componente aprendido que o artigo diz explicitamente estar ausente. A alternativa (d) funde uma distinção que o artigo tem o cuidado de fazer.

</details>

3. ▢ O DeepSeek-R1-Zero alcança um forte desempenho de raciocínio, mas sofre de legibilidade ruim e mistura de idiomas. Dada a forma como a sua recompensa foi construída, isso é surpreendente?

<details markdown="1"><summary>Verificação</summary>

Não. A recompensa só checava a correção da resposta final e a presença das tags de raciocínio; nada sobre legibilidade ou sobre ficar em um único idioma fez parte da pontuação, então o treinamento de RL não tinha incentivo para selecionar nenhum dos dois, por melhor que o raciocínio do modelo ficasse.

</details>

## Prática no mundo real

- [ ] Leia a passagem "Aha Moment" do artigo do DeepSeek-R1 (linkado acima, o texto ao redor da Tabela 3) e escreva, com as suas palavras, que comportamento específico o modelo exibiu que os pesquisadores não haviam treinado explicitamente.
- [ ] Encontre um exemplo documentado (neste artigo ou em outro lugar) de um modelo treinado com uma recompensa especificada de forma estreita que produziu um comportamento emergente não intencional e compare-o com o "momento aha": o comportamento emergente foi benéfico, prejudicial ou ambos?
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 14: dado que o RL puro baseado em regras do DeepSeek-R1-Zero produziu um bom raciocínio mas legibilidade ruim, o que você acrescentaria ao processo de treinamento, e em que etapa, para corrigir a legibilidade sem perder a capacidade de raciocínio?

## Para ir além

- [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
