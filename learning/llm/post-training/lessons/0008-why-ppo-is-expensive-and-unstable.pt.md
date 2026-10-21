---
title: "8. Por que o PPO é caro e instável"
description: "Quatro modelos, e não um, precisam caber na memória ao mesmo tempo, e os dois que escalam pior são exatamente os que o RLHF acrescenta"
type: lesson
---

# Lição 8. Por que o PPO é caro e instável

**Ligação com a missão:** Derivar o objetivo do RLHF e o seu mecanismo de corte (lições 6 e 7) explica o que o PPO otimiza; esta lição explica o que ele realmente custa para rodar, que é o que faz o DPO (etapa 5) valer a pena como alternativa.
**Fonte principal:** [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Pré-requisitos:** [Lição 7](0007-ppo-why-the-update-gets-clipped.md)

## Aquecimento

1. ▢ Por que o PPO corta a razão de probabilidade entre a policy nova e a antiga, em vez de deixar o objetivo substituto crescer sem limites?

<details markdown="1"><summary>Verificação</summary>

Porque uma vantagem estimada grande vinda de um batch amostrado não é evidência confiável de que uma atualização de policy igualmente grande seja segura; o corte limita o quanto uma única atualização pode mover a policy em resposta a ela, evitando um passo destrutivamente grande.

</details>

2. ▢ Qual é a diferença de escopo entre a penalidade de KL (lição 6) e o corte por passo do PPO (lição 7)?

<details markdown="1"><summary>Verificação</summary>

A penalidade de KL limita o quanto a policy se afasta do modelo de referência SFT fixo ao longo de toda a execução de treinamento. O corte limita o tamanho que qualquer passo de otimização isolado pode ter em relação ao estado da própria policy imediatamente antes desse passo. Nenhum substitui o outro.

</details>

## Saiba isto

### Quatro modelos, e não um

O RLHF via PPO não é um modelo sendo treinado; ele exige vários modelos presentes ao mesmo tempo, cada um com um trabalho diferente: a **policy** sendo treinada (inicializada a partir do modelo SFT); uma cópia congelada do próprio **modelo SFT**, mantida apenas para calcular a penalidade de KL (lição 6); o **reward model** (lição 4), que pontua as saídas amostradas da policy; e uma **função de valor**, usada para produzir as estimativas de vantagem de que o objetivo cortado do PPO (lição 7) depende. Ouyang et al. afirmam diretamente que a sua função de valor é inicializada a partir do reward model, o que a torna uma quinta cópia completa de um modelo grande em termos de parâmetros, distinta do próprio reward model apesar de compartilhar o seu ponto de partida. Quatro a cinco modelos grandes ocupando memória e consumindo compute ao mesmo tempo, em vez de um, é um custo real e estrutural que não tem nada a ver com o quão bem ou mal o treinamento esteja indo.

### De onde a instabilidade vem especificamente

Ouyang et al. dão um relato concreto de onde a escala interage mal com essa configuração. Eles descobriram que um reward model de 175 bilhões de parâmetros conseguia uma loss de validação menor do que um menor, mas a dois custos: o seu treinamento era mais instável, o que o tornava uma pior escolha para inicializar uma função de valor do PPO, e usar juntos um reward model e uma função de valor de 175 bilhões de parâmetros aumentava substancialmente as exigências de compute do PPO, além do custo da própria policy. A resolução deles foi prática, e não teórica: eles constataram que um reward model de 6 bilhões de parâmetros era estável em uma ampla faixa de learning rates e igualmente eficaz para treinar bons modelos com PPO, e usaram esse único reward model de 6B para todos os tamanhos de policy que treinaram, incluindo a sua policy de 175B.

### Por que vale a pena lembrar dessa troca específica

Este é um resultado genuinamente contraintuitivo que vale a pena guardar: um reward model menor não foi um compromisso forçado pela falta de recursos, foi a escolha mais confiável na escala que Ouyang et al. testaram. O treinamento de reward model e de função de valor, executado em escala muito grande, não herda automaticamente o comportamento de escala mais suave e previsível que uma loss de pré-treinamento direta mostra (as leis de escala da etapa 3, de uma trilha diferente). A instabilidade em escala não é só um inconveniente a contornar; ela moldou diretamente o que Ouyang et al. de fato construíram, e é uma razão real pela qual a configuração completa do PPO, com quatro ou cinco modelos, executada na maior escala possível em cada parte, é cara de tentar e pouco confiável mesmo quando tentada.

## Prática

1. ▢ Cite os quatro modelos (ou cinco, contando a função de valor separadamente do reward model a partir do qual ela é inicializada) envolvidos em um passo de treinamento de PPO para RLHF, e para que cada um é usado.

<details markdown="1"><summary>Verificação</summary>

A policy sendo treinada; um modelo SFT congelado, usado para calcular a penalidade de KL; o reward model, que pontua as saídas da policy; e a função de valor (inicializada a partir do reward model, mas treinada separadamente), que produz as estimativas de vantagem de que o objetivo cortado do PPO precisa.

</details>

2. ▢ Segundo Ouyang et al., que dois custos vieram com o uso de um reward model e de uma função de valor de 175B, mesmo que ele tenha conseguido uma loss de validação menor do que um menor?

<details markdown="1"><summary>Verificação</summary>

O seu treinamento era mais instável, o que o tornava uma pior escolha para inicializar uma função de valor do PPO, e usá-lo aumentava substancialmente as exigências de compute do PPO, além do custo da própria policy.

</details>

3. ▢ Uma equipe supõe que um reward model maior e mais preciso é sempre a melhor escolha para o RLHF, já que ele alcança uma loss de validação menor. Segundo a própria descoberta de Ouyang et al., essa suposição é segura?

    - a) Sim, um reward model com loss menor é sempre a melhor escolha, independentemente da escala
    - b) Não; um reward model de 175B teve treinamento mais instável e custo de compute maior, e um reward model menor, de 6B, foi estável e igualmente eficaz para treinar bons modelos com PPO
    - c) Não, porque reward models maiores não podem ser usados com PPO de forma alguma
    - d) Sim, mas só porque Ouyang et al. nunca testaram de fato um reward model de 175B

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente a descoberta do próprio Ouyang et al.: a loss de validação menor não se traduziu na melhor escolha prática quando se levaram em conta a estabilidade do treinamento e o custo de compute. A alternativa (a) ignora a troca que eles próprios relatam. A alternativa (c) exagera a descoberta; o problema era estabilidade e custo, não incompatibilidade. A alternativa (d) é factualmente errada; eles relatam explicitamente ter testado e rejeitado a opção de 175B por essas razões.

</details>

## Prática no mundo real

- [ ] Encontre um relatório técnico ou post de blog que descreva uma configuração real de treinamento de RLHF e veja se ele informa os tamanhos relativos da sua policy, do reward model e da função de valor. Anote se o reward model tem o mesmo tamanho da policy ou é deliberadamente menor.
- [ ] Leia a seção do Apêndice C de Ouyang et al. sobre o treinamento do reward model (linkado acima) e escreva uma frase sobre a que eles constataram que o treinamento era sensível, em contraste com a que ele não era muito sensível.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a etapa 5: dado que o PPO precisa de um reward model, de uma função de valor e de um loop de RL por cima da própria policy, o que um método que produz um resultado semelhante sem um reward model separado nem um loop de RL teria de fazer de diferente?

## Para ir além

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

A etapa 4 cobriu o que o RLHF-PPO otimiza e o que custa rodá-lo. A etapa 5 cobre uma alternativa construída especificamente para precisar de menos das duas coisas: nenhum reward model separado e nenhum loop de RL.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
