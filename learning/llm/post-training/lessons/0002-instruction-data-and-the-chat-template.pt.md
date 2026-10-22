---
title: "2. Dados de instrução e o chat template"
description: "Um token especial marca onde um prompt termina e uma resposta começa, e essa fronteira precisa ser a mesma no treinamento e no serving"
type: lesson
---

# Lição 2. Dados de instrução e o chat template

**Ligação com a missão:** "Escrever um loop de treinamento de SFT que mascara a loss nos tokens que não são do assistente e explicar o que quebra em um chat model treinado sem essa máscara" é o primeiro item de O sucesso se parece com isto. Esta lição cobre como são os dados de SFT e como os seus segmentos são marcados; a lição 3 cobre o mascaramento em si.
**Fonte principal:** [Artigo científico: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Pré-requisitos:** [Lição 1](0001-what-post-training-buys.md)

## Aquecimento

1. ▢ O que é um alignment tax, e o que Ouyang et al. descobriram que poderia compensá-lo parcialmente?

<details markdown="1"><summary>Verificação</summary>

Uma queda medida de desempenho em certos benchmarks públicos de PLN que veio junto com os ganhos de alinhamento do pós-treinamento. Misturar as atualizações do PPO com atualizações que aumentam a verossimilhança dos dados originais de pré-treinamento (PPO-ptx) recuperou boa parte desse desempenho perdido sem abrir mão dos ganhos de preferência.

</details>

## Saiba isto

### Como os dados de SFT realmente se parecem

Os dados de **supervised fine-tuning (SFT)** são um conjunto de pares de prompt e resposta, exatamente o formato que o passo 1 da lição 1 descreveu. Touvron et al. dão exemplos reais da própria anotação de SFT do Llama 2: um prompt que pede um poema sobre os dez primeiros elementos da tabela periódica, pareado com um poema escrito por um anotador que o atende; um prompt que pede um "roast" deliberadamente cruel, pareado com uma recusa escrita por um anotador explicando o porquê. Ambos são simplesmente um prompt e a resposta exata que um anotador quer que o modelo aprenda a produzir para ele.

### Marcando onde um segmento termina e o próximo começa

Treinar com esses dados significa concatenar muitos pares de prompt e resposta no corpus de treinamento, e o modelo precisa de algum jeito de saber onde um prompt termina e a sua resposta começa, já que nada no texto simples marca essa fronteira por si só. Touvron et al. descrevem exatamente isso: "um token especial é utilizado para separar os segmentos de prompt e de resposta." Essa é a semente do que se chama de **chat template**: uma maneira fixa e consistente de marcar as fronteiras de papéis (um segmento de prompt, um segmento de resposta e, em uma conversa de várias voltas, uma mensagem de sistema e cada turno sucessivo) com tokens especiais, de modo que a mesma estrutura apareça toda vez no treinamento e possa ser reproduzida exatamente no serving.

### Por que a fronteira precisa ser a mesma no treinamento e no serving

Um chat template não é só uma conveniência de formatação; ele faz parte daquilo em que o modelo foi de fato treinado. O modelo aprendeu a associar os tokens especiais que marcam "aqui é onde uma resposta começa" a produzir de fato o tipo de resposta que vinha depois desses tokens durante o treinamento. Servir o modelo com um template diferente, com tokens especiais diferentes, com outra ordem de papéis ou sem a convenção de mensagem de sistema o expõe a uma estrutura que ele nunca viu pareada com o comportamento que aprendeu, e o seu comportamento se degrada ou fica imprevisível como resultado. Reproduzir no serving o template exato do treinamento não é uma limpeza opcional; é parte de usar o modelo corretamente.

### Várias voltas é a mesma ideia, repetida

Uma conversa de várias voltas estende essa mesma ideia de marcação de segmentos por mais de uma troca: uma mensagem de sistema (se houver), depois turnos alternados de usuário e assistente, cada um marcado com o mesmo tipo de token especial que separa qualquer prompt isolado da sua resposta. Nada de novo é inventado para o caso de várias voltas; é o mesmo princípio de marcação de fronteiras, aplicado uma vez por turno em vez de uma vez por exemplo.

## Prática

1. ▢ Por que um modelo não consegue aprender onde um prompt termina e a sua resposta começa só a partir de texto simples concatenado, sem algum tipo de marcador?

<details markdown="1"><summary>Verificação</summary>

Porque o texto simples não carrega nenhum sinal inerente que distinga "isto é o que foi perguntado" de "esta é a resposta que devo aprender a produzir"; sem um marcador, a fronteira entre as duas não está representada em lugar nenhum dos próprios dados de treinamento.

</details>

2. ▢ Uma equipe faz fine-tuning de um modelo usando um chat template, mas o serve em produção com outro template (tokens especiais diferentes marcando as fronteiras de papéis). Qual é a consequência mais provável?

    - a) Nenhum efeito; o modelo ignora a formatação por completo
    - b) O comportamento do modelo se degrada ou fica imprevisível, já que ele é exposto a uma estrutura que nunca viu pareada com o comportamento que aprendeu durante o treinamento
    - c) O modelo detecta e se adapta automaticamente ao novo template
    - d) Só a mensagem de sistema é afetada; os turnos de usuário e de assistente continuam funcionando normalmente

<details markdown="1"><summary>Verificação</summary>

**b)** é a consequência real: o chat template faz parte daquilo em que o modelo foi treinado, não é um invólucro cosmético, então uma incompatibilidade apresenta uma estrutura sem treinamento. As alternativas (a), (c) e (d) pressupõem uma robustez a incompatibilidades de template que o treinamento não dá motivo para esperar.

</details>

3. ▢ Como o chat template de uma conversa de várias voltas se relaciona com o template de um único par de prompt e resposta que Touvron et al. descrevem para o SFT?

<details markdown="1"><summary>Verificação</summary>

É a mesma ideia de marcação de segmentos, aplicada repetidamente: uma mensagem de sistema, se houver, depois cada turno de usuário e de assistente em sequência, cada um marcado com o mesmo tipo de token especial que separa um único prompt da sua resposta, em vez de exigir um mecanismo fundamentalmente diferente.

</details>

## Prática no mundo real

- [ ] Encontre o chat template de um modelo aberto a que você tenha acesso (muitos são publicados como um arquivo de template ou documentados diretamente) e identifique os tokens especiais que ele usa para marcar uma mensagem de sistema, um turno de usuário e um turno de assistente.
- [ ] Leia os dois exemplos de anotação de SFT de Touvron et al. (linkados acima, Tabela 5) e escreva, com as suas palavras, o que distingue uma boa resposta de SFT de uma que apenas soa plausível, com base no exemplo da recusa do roast.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 3: se um chat template concatena um prompt e uma resposta em uma única sequência sem intervalo, e o treinamento usa uma loss comum de previsão do próximo token na sequência inteira, o que o modelo começaria a aprender a fazer com os próprios tokens do prompt que não deveria?

## Para ir além

- [Artigo científico: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
