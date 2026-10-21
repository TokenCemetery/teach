---
title: "15. Constitutional AI: feedback de um modelo, não de um humano"
description: "Zero rótulos humanos para dano, uma lista escrita de princípios no lugar, e um assistente que explica as suas objeções em vez de se esquivar"
type: lesson
---

# Lição 15. Constitutional AI: feedback de um modelo, não de um humano

**Ligação com a missão:** "Saber dizer de onde veio o feedback (humano ou de IA) em um dado pipeline de ajuste de segurança e o que isso implica em trocas" é o item de O sucesso se parece com isto a que esta etapa serve. Esta lição cobre o método em duas etapas do Constitutional AI; a lição 16 cobre o quanto o feedback de IA se sustenta contra o feedback humano em uma comparação direta e controlada.
**Fonte principal:** [Artigo científico: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
**Pré-requisitos:** [Lição 14](0014-distilling-a-reasoning-model-down.md)

## Aquecimento

1. ▢ Segundo a comparação de 32B da própria DeepSeek-AI, treinar um modelo pequeno diretamente com RL em larga escala alcançou o mesmo desempenho de raciocínio que destilar de um modelo maior, já treinado com RL?

<details markdown="1"><summary>Verificação</summary>

Não. O RL direto no base model de 32B alcançou 47,0% de pass@1 no AIME 2024, bem abaixo dos 72,6% que o mesmo base model alcançou quando passou, em vez disso, por fine-tuning nos traces de raciocínio destilados do modelo maior.

</details>

2. ▢ O que é uma recompensa verificável, e por que ela não tem o modo de falha de reward hacking que um reward model treinado tem?

<details markdown="1"><summary>Verificação</summary>

Uma recompensa produzida por um verificador determinístico em vez de por um modelo aprendido; como nenhuma peculiaridade de um modelo aprendido fica entre a saída e a sua pontuação, não há exploit específico de reward model para uma policy aprender.

</details>

## Saiba isto

### Lembre a falha que o método desta lição foi construído para evitar

A lição 5 cobriu uma falha real e documentada: policies de RLHF otimizadas em excesso para inofensividade convergiram para a evasão generalizada, recomendando que os usuários procurassem terapia diante de quase qualquer pergunta minimamente sensível, um jeito barato de pontuar bem em um reward model de inofensividade sem ser genuinamente útil. O **Constitutional AI (CAI)** é construído especificamente para produzir um assistente inofensivo que não tome esse atalho.

### Duas etapas, e onde o feedback de IA entra em cada uma

A etapa supervisionada, o **SL-CAI**, amostra respostas de um modelo inicial, faz o modelo gerar uma **autocrítica** e uma **revisão** da própria resposta contra uma lista curta e escrita de princípios (a "constituição" que dá nome ao método) e depois faz fine-tuning do modelo original nessas respostas autorrevisadas, SFT comum (etapa 2) em dados que o próprio modelo produziu e melhorou sozinho.

A etapa de reinforcement learning, o **RL-CAI**, amostra pares de respostas do modelo ajustado por SL e, em vez de um rotulador humano dizer qual é melhor, **usa um modelo** para fazer esse julgamento. Um modelo de preferência (o treinamento de Bradley-Terry da lição 4) é treinado nesse dataset de preferências geradas por IA, e a policy é então treinada com RL contra esse modelo de preferência treinado por IA exatamente como a configuração de RLHF da lição 6 usaria um treinado por humanos. Bai et al. nomeiam essa técnica geral diretamente: **RL from AI Feedback (RLAIF)**.

### Zero rótulos humanos para dano, e o que saiu disso

Bai et al. enunciam o resultado com clareza: todo esse pipeline treina um assistente de IA "não evasivo" e "relativamente inofensivo" "sem nenhum rótulo de feedback humano para danos". Os princípios da constituição, e não milhares de julgamentos humanos de nocividade, é que moldam o comportamento do modelo. O assistente resultante lida com perguntas nocivas explicando as suas objeções a elas, em vez de recusar ou se esquivar de vez, o que é uma resposta direta à otimização excessiva específica que a lição 5 documentou: um modelo cujo treinamento de inofensividade recompensa um engajamento realmente ponderado, em vez de recompensar a recusa mais barata possível, tem menos incentivo para colapsar na evasão generalizada.

### A comparação que faz isto merecer ser levado a sério

Bai et al. não se limitam a afirmar que isso funciona; eles relatam que crowdworkers preferiram o modelo resultante, o "RL-CAI", a modelos treinados com rótulos de feedback humano coletados anteriormente para nocividade. Substituir os rótulos humanos de dano por uma constituição escrita e por preferências geradas por IA não só igualou a alternativa rotulada por humanos; segundo a comparação que eles próprios relatam, foi melhor.

## Prática

1. ▢ No SL-CAI, o que o modelo faz com as suas próprias respostas amostradas antes de elas serem usadas para o fine-tuning?

<details markdown="1"><summary>Verificação</summary>

Ele gera uma autocrítica da resposta contra os princípios da constituição escrita, depois produz uma revisão da resposta, e o modelo passa por fine-tuning nessas respostas revisadas.

</details>

2. ▢ No RL-CAI, o que substitui o rotulador humano que ordinariamente julgaria qual de duas respostas amostradas é melhor?

<details markdown="1"><summary>Verificação</summary>

Um modelo. Um sistema de IA julga qual de duas respostas é melhor, e um modelo de preferência é treinado nesse dataset de preferências geradas por IA, e não em comparações rotuladas por humanos.

</details>

3. ▢ Por que o assistente resultante do Constitutional AI, ao explicar as suas objeções a um pedido nocivo em vez de recusar de vez, enfrenta diretamente a falha que a lição 5 descreveu?

<details markdown="1"><summary>Verificação</summary>

A falha de evasão generalizada da lição 5 surgiu porque recusar de vez era um jeito barato e pouco sofisticado de pontuar bem em um reward model de inofensividade. Uma abordagem de treinamento cuja recompensa favorece, em vez disso, engajar-se genuinamente com um pedido e explicar as objeções a ele remove o incentivo a esse atalho barato, já que a esquiva sozinha não seria a opção de maior pontuação.

</details>

4. ▢ Segundo a própria comparação de Bai et al., como os crowdworkers avaliaram o RL-CAI contra um modelo treinado com rótulos de feedback humano coletados anteriormente para nocividade?

<details markdown="1"><summary>Verificação</summary>

Eles preferiram o RL-CAI. Substituir os rótulos humanos de dano por uma constituição e por preferências geradas por IA não apenas igualou a alternativa rotulada por humanos na comparação relatada; foi preferido a ela.

</details>

## Prática no mundo real

- [ ] Encontre uma "constituição" publicada, ou um conjunto de princípios orientadores, usada para treinar um modelo de verdade (várias foram divulgadas publicamente) e leia três ou quatro dos seus princípios. Anote se eles se leem como regras específicas ou como valores gerais que um modelo teria de interpretar.
- [ ] Leia a passagem do artigo do Constitutional AI (linkado acima) que descreve o passo de autocrítica e revisão do SL-CAI e escreva uma frase descrevendo o que precisaria dar errado para a autocrítica de um modelo não conseguir pegar um problema real na própria resposta.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 16: dado que o Constitutional AI substitui os rótulos humanos de dano por rótulos gerados por IA para um único método, você esperaria que o feedback de IA funcionasse tão bem também em outros tipos de tarefa, como sumarização ou utilidade geral, e por quê, ou por que não?

## Para ir além

- [Artigo científico: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
