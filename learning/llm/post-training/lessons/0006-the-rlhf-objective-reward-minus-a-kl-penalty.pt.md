---
title: "6. O objetivo do RLHF: recompensa menos uma penalidade de KL"
description: "Um termo persegue a pontuação do reward model; um segundo termo é a coleira que impede a policy de fugir com ela"
type: lesson
---

# Lição 6. O objetivo do RLHF: recompensa menos uma penalidade de KL

**Ligação com a missão:** "Derivar o objetivo do RLHF (recompensa menos uma penalidade de KL contra um modelo de referência) e dizer o que acontece com a policy quando a penalidade de KL é afrouxada" é o terceiro item de O sucesso se parece com isto. Esta lição cobre o objetivo em si; a lição 7 cobre o PPO, o algoritmo usado para otimizá-lo, e a lição 8 cobre o que tudo isso custa para rodar.
**Fonte principal:** [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Pré-requisitos:** [Lição 5](0005-reward-hacking.md)

## Aquecimento

1. ▢ Para o que as policies de Bai et al. convergiram quando otimizadas em excesso para inofensividade, e por que esse comportamento era um jeito barato de pontuar bem?

<details markdown="1"><summary>Verificação</summary>

Evasão generalizada: recomendar que os usuários procurassem terapia ou ajuda profissional diante de quase qualquer pergunta minimamente sensível. Exigia muito pouca sofisticação, essencialmente só classificar um pedido como sensível e recusá-lo, o que é muito mais fácil do que ser genuinamente matizado, útil e inofensivo.

</details>

2. ▢ O que a divergência entre PM de treino e PM de teste de Bai et al. indicou quando apareceu?

<details markdown="1"><summary>Verificação</summary>

Que a policy provavelmente estava otimizada em excesso especificamente contra o PM de treino, explorando um comportamento que ele recompensa e que um reward model held-out, nunca treinado para esperar exatamente essa policy, não recompensa tanto.

</details>

## Saiba isto

### O objetivo completo

Ouyang et al. enunciam o objetivo exato que o seu treinamento com PPO maximiza:

```text
objective(φ) = E[(x,y) ~ policy] [ r(x, y) − β · log( policy(y|x) / SFT(y|x) ) ]
             + γ · E[x ~ pretraining data] [ log( policy(x) ) ]
```

Três peças estão fazendo três trabalhos diferentes aqui, e vale a pena vê-las uma de cada vez.

### O termo de recompensa

`r(x, y)` é a pontuação escalar do reward model treinado (lição 4) para a própria saída `y` da policy ao prompt `x`. Maximizar apenas esse termo é o que empurra a policy em direção às saídas que o reward model pontua alto, exatamente o objetivo a que a modelagem de recompensa existe para servir.

### O termo da penalidade de KL

`β · log( policy(y|x) / SFT(y|x) )` compara a probabilidade que a policy treinada dá a `y` com a probabilidade que o modelo SFT original dá ao mesmo `y`, e subtrai uma penalidade proporcional ao quanto a probabilidade da própria policy se tornou maior. Ouyang et al. descrevem isso diretamente como uma **penalidade de KL por token em relação ao modelo SFT**, acrescentada especificamente **para mitigar a otimização excessiva do reward model**, a falha exata que a lição 5 descreveu. O termo de recompensa sozinho dá à policy todo incentivo para se afastar o quanto precisar para maximizar `r(x, y)`; o termo de KL é o que faz o afastamento da distribuição do SFT custar alguma coisa, em vez de ser de graça.

### O que acontece quando β é afrouxado ou apertado

`β` é um botão, e as duas direções têm um custo real:

- Quando `β` diminui em direção a zero, a penalidade por divergir da policy do SFT quase desaparece, e o objetivo se reduz a perseguir a pontuação do reward model com quase nada segurando a policy. Essa é precisamente a otimização sem restrição da qual a divergência entre PM de treino e PM de teste da lição 5 é evidência: quanto menos a penalidade de KL contém a policy, mais espaço ela tem para explorar o que quer que o reward model por acaso recompense, em vez do que os seus projetistas realmente queriam.
- Quando `β` cresce muito, a penalidade por se afastar da policy do SFT domina o objetivo, e a policy treinada é puxada de volta para reproduzir o modelo SFT quase exatamente. Levado longe o bastante, isso anula o propósito da própria etapa de RL: se a policy não consegue se afastar de forma significativa do que o SFT já produzia, o RLHF não tem mais nada a acrescentar por cima dele.

Escolher `β` é escolher um ponto nessa troca, e não eliminá-la: um `β` menor corre o risco do reward hacking que a lição 5 descreveu; um `β` maior corre o risco de o RLHF acrescentar pouco além do que o SFT sozinho já alcançava.

### O termo do gradiente de pré-treinamento e a sua ligação com a lição 1

O termo final, `γ · E[log(policy(x))]`, é totalmente separado da troca entre recompensa e KL: ele mistura um objetivo comum de modelagem de linguagem sobre a distribuição original de pré-treinamento, aumentando a verossimilhança que a policy dá ao tipo de texto com que foi pré-treinada. Ouyang et al. definem `γ = 0` para o que chamam de modelos "PPO" simples e usam um `γ` diferente de zero para o que chamam de modelos "PPO-ptx". Esse termo é o mecanismo real por trás da mitigação do alignment tax da lição 1: misturar de volta gradientes dos dados de pré-treinamento no treinamento com PPO é o que recuperou boa parte da regressão de desempenho em benchmarks públicos de PLN que o treinamento com PPO puro introduziu, sem abrir mão dos ganhos de preferência que o RLHF foi feito para produzir.

## Prática

1. ▢ Uma equipe define `β` com um valor muito pequeno no objetivo do RLHF. Ao que isso expõe a policy de forma mais direta, e por quê?

<details markdown="1"><summary>Verificação</summary>

Reward hacking: com a penalidade de KL quase eliminada, o termo de recompensa domina o objetivo quase sem oposição, dando à policy pouca razão para não se afastar em direção ao que quer que o reward model por acaso pontue alto, quer esse comportamento seja ou não o que o reward model pretendia de fato representar.

</details>

2. ▢ Uma equipe define `β` com um valor muito grande. Qual é o custo mais provável dessa escolha?

<details markdown="1"><summary>Verificação</summary>

A policy é puxada de volta para reproduzir de perto o modelo SFT, já que qualquer desvio significativo é fortemente penalizado; levado longe o bastante, isso deixa pouco espaço para o RLHF acrescentar qualquer comportamento além do que o SFT sozinho já produzia.

</details>

3. ▢ Qual é a diferença entre o que Ouyang et al. chamam de "PPO" e "PPO-ptx", e qual termo do objetivo as distingue?

<details markdown="1"><summary>Verificação</summary>

O "PPO" define o coeficiente do gradiente de pré-treinamento `γ` como 0; o "PPO-ptx" usa um `γ` diferente de zero, misturando nas atualizações do PPO gradientes da log-verossimilhança dos dados de pré-treinamento. Esse é o termo responsável por reduzir o alignment tax que a lição 1 apresentou.

</details>

4. ▢ Qual destas descreve melhor o papel que o termo de recompensa e o termo da penalidade de KL desempenham, cada um, no objetivo?

    - a) O termo de recompensa puxa a policy para o que o reward model pontua alto; a penalidade de KL a puxa de volta para o modelo SFT, e o objetivo equilibra os dois
    - b) Os dois termos puxam a policy na mesma direção, a das preferências do reward model
    - c) A penalidade de KL só é usada durante a avaliação, não durante o treinamento
    - d) O termo de recompensa e o termo da penalidade de KL são matematicamente idênticos, apenas em escalas diferentes

<details markdown="1"><summary>Verificação</summary>

**a)** é a relação real: dois termos que de fato puxam em direções diferentes, com `β` definindo o equilíbrio entre eles. As alternativas (b), (c) e (d) descrevem mal a estrutura do objetivo, de maneiras que a derivação desta lição exclui diretamente.

</details>

## Prática no mundo real

- [ ] Encontre onde um framework de treinamento a que você tenha acesso expõe um coeficiente de penalidade de KL para RLHF (muitas vezes com um nome como `beta` ou `kl_coef`) e anote o seu valor padrão e qualquer orientação documentada sobre como ajustá-lo.
- [ ] Leia o parágrafo do artigo do InstructGPT (linkado acima) que descreve o objetivo completo e escreva, em uma frase cada, o que acontece com o treinamento se `β` e `γ` forem ambos definidos como zero ao mesmo tempo.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 7: dado que esse objetivo precisa ser maximizado ajustando os próprios parâmetros da policy, e que uma única atualização baseada em um batch de saídas amostradas poderia empurrar a policy muito longe em um só passo, que problema uma otimização ingênua desse objetivo poderia encontrar?

## Para ir além

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
