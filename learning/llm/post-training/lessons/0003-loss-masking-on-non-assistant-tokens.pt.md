---
title: "3. Loss masking em tokens que não são do assistente"
description: "Zere a loss no prompt, ou gaste sinal de gradiente ensinando o modelo a prever um texto que ele não gerou"
type: lesson
---

# Lição 3. Loss masking em tokens que não são do assistente

**Ligação com a missão:** "Escrever um loop de treinamento de SFT que mascara a loss nos tokens que não são do assistente e explicar o que quebra em um chat model treinado sem essa máscara" é o primeiro item de O sucesso se parece com isto, e esta lição é onde ele é respondido diretamente.
**Fonte principal:** [Artigo científico: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Pré-requisitos:** [Lição 2](0002-instruction-data-and-the-chat-template.md), [Loss masking](../GLOSSARY.md)

## Aquecimento

1. ▢ O que é um chat template, e por que importa que o mesmo seja usado no treinamento e no serving?

<details markdown="1"><summary>Verificação</summary>

Uma maneira fixa e consistente de marcar as fronteiras de papéis (turnos de sistema, usuário e assistente) com tokens especiais, para que o modelo possa aprender uma estrutura que voltará a ver de forma confiável. Uma incompatibilidade entre os templates de treinamento e de serving expõe o modelo a uma estrutura que ele nunca viu pareada com o comportamento que aprendeu, degradando ou desestabilizando o seu comportamento.

</details>

2. ▢ Segundo Touvron et al., que token especial eles usam para separar um prompt da sua resposta nos dados de treinamento de SFT?

<details markdown="1"><summary>Verificação</summary>

Um token especial dedicado, inserido especificamente para marcar a fronteira entre o segmento de prompt e o segmento de resposta.

</details>

## Saiba isto

### A versão simples, sem máscara, desta loss estaria errada

Uma loss comum de modelagem de linguagem treina um modelo para prever o próximo token em cada posição de uma sequência, comparando com o que a sequência de fato contém ali. Aplicada ingenuamente a um exemplo concatenado de prompt e resposta, sem nenhum ajuste, isso treinaria o modelo a prever também os tokens do próprio prompt, e não só os da resposta, já que o prompt faz parte da sequência exatamente como a resposta.

### O que Touvron et al. realmente fazem no lugar

Touvron et al. enunciam a sua abordagem diretamente: "utilizamos um objetivo autorregressivo e zeramos a loss nos tokens do prompt do usuário, de modo que fazemos backpropagation apenas nos tokens da resposta." Isso é **loss masking**: todo token que pertence ao prompt (ou, em um exemplo de várias voltas, a qualquer turno de usuário ou de sistema) tem a sua contribuição para a loss definida como zero, de modo que só os tokens que o modelo realmente deve gerar, a resposta do assistente, produzem gradiente. Mecanicamente, isso costuma ser implementado dando a cada posição mascarada um valor de rótulo que a função de loss é instruída a ignorar (uma convenção comum o define como `-100` em uma loss de cross-entropy padrão), em vez do token que de fato aparece ali.

### O que quebra sem ele

Pular esse mascaramento não desperdiça só um pouco de compute; ele muda aquilo para que o modelo está de fato sendo treinado. Dois problemas concretos decorrem diretamente disso:

- **O modelo aprende a prever um texto que não gerou e que nunca precisará reproduzir.** Nada em treinar um modelo para prever de volta o próprio prompt do usuário serve ao objetivo do SFT, que é moldar o que o modelo produz como resposta, e não o que ele consegue regurgitar da pergunta.
- **Os prompts costumam ser bem mais longos do que as respostas que vêm depois.** Uma loss sem máscara é dominada por quantos tokens de prompt houver, diluindo o sinal de gradiente nos tokens da resposta, a única parte da sequência que o SFT está de fato tentando moldar, com uma grande quantidade de loss gasta em uma tarefa (prever o prompt) que nunca foi o objetivo.

### O resultado: o mascaramento concentra o objetivo no que está sendo ensinado

Mascarar todo token que não é do assistente faz o oposto dos dois problemas: cada unidade de sinal de gradiente em um passo de SFT vem de tokens que o modelo de fato deve aprender a produzir, e nenhuma é gasta prevendo um texto que o modelo apenas recebeu. É isso que faz o SFT ensinar a habilidade específica que ele deve ensinar, imitar a resposta desejada, e não uma mistura dela com outra sem relação (prever texto arbitrário do usuário) que por acaso compartilha a mesma sequência de treinamento.

## Prática

1. ▢ Um exemplo de treinamento concatena um prompt de 200 tokens e uma resposta de 20 tokens, sem loss masking. Aproximadamente que fração da loss total desse exemplo vem de tokens que não são o alvo real do SFT?

<details markdown="1"><summary>Verificação</summary>

Aproximadamente 200 de 220 tokens, cerca de 91%, seriam tokens de prompt contribuindo com loss que não tem nada a ver com a resposta que o SFT tenta ensinar o modelo a produzir. Apenas cerca de 9% da loss sem máscara viria da própria resposta.

</details>

2. ▢ Qual destas descreve melhor o que o loss masking faz, mecanicamente?

    - a) Remove por completo os tokens do prompt da sequência de entrada
    - b) Dá à posição de cada token mascarado um rótulo que a função de loss é instruída a ignorar, de modo que só as posições sem máscara (do assistente) contribuem com gradiente
    - c) Reduz o learning rate especificamente ao processar os tokens do prompt
    - d) Treina um modelo separado só para os tokens do prompt

<details markdown="1"><summary>Verificação</summary>

**b)** é o mecanismo real: os tokens do prompt continuam presentes como entrada, então o modelo pode condicionar a sua resposta a eles, mas as suas posições ficam de fora do próprio cálculo da loss. A alternativa (a) removeria informação de que o modelo precisa para condicionar a sua resposta. As alternativas (c) e (d) não descrevem nenhuma técnica descrita por esta lição ou pela sua fonte.

</details>

3. ▢ Um modelo treinado sem loss masking nos tokens que não são do assistente é comparado com um treinado com ele, exatamente nos mesmos dados de SFT. Cite uma maneira concreta pela qual você esperaria que o treinamento de SFT do modelo sem máscara tivesse sido diferente.

<details markdown="1"><summary>Verificação</summary>

Qualquer versão razoável de: o sinal de gradiente foi diluído por aprender a prever os tokens do prompt, ou gasto nisso, em vez de concentrado inteiramente nos tokens da resposta; assim, para o mesmo número de passos de treinamento, menos do aprendizado do modelo estava de fato moldando o seu comportamento de geração de respostas, a única coisa que o SFT deve ensinar.

</details>

## Prática no mundo real

- [ ] Encontre onde um framework de treinamento a que você tenha acesso implementa o loss masking para dados de SFT em estilo de chat (um `ignore_index`, um campo `labels` com posições mascaradas ou algo parecido) e confirme qual convenção ele usa para marcar uma posição mascarada.
- [ ] Pegue uma conversa de exemplo curta (uma mensagem de sistema, um turno de usuário, um turno de assistente) e marque, token a token ou segmento a segmento, quais partes seriam mascaradas e quais contribuiriam com a loss, segundo a regra desta lição.
- [ ] Amanhã: para uma conversa de várias voltas com dois turnos de usuário e dois de assistente, escreva quais turnos são mascarados e quais não são, e confira a sua resposta com a regra desta lição de que todo turno que não é do assistente é mascarado, e não apenas o primeiro prompt.

## Para ir além

- [Artigo científico: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Documentação: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Recursos](../RESOURCES.md)

---

A etapa 2 cobriu a imitação direta de uma resposta demonstrada. A etapa 3 passa a um tipo diferente de sinal: não qual deve ser a resposta, mas qual de duas respostas um humano preferiu.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
