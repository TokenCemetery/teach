---
title: "17. Warm-up, decaimento e aumento do batch no meio da execução"
description: "Começar devagar, decair segundo um schedule e deixar o próprio batch size mudar no meio do treinamento"
type: lesson
---

# Lição 17. Warm-up, decaimento e aumento do batch no meio da execução

**Ligação com a missão:** "Dada uma curva de loss, consegue dizer se um spike é recuperável ou exige recomeçar de um checkpoint anterior" é o item de O sucesso se parece com isto que esta etapa atende. A Lição 16 cobriu os spikes e o clipping que protege contra eles; esta lição cobre o schedule que molda a execução em torno dessa proteção.
**Fonte principal:** [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Pré-requisitos:** [Lição 16](0016-loss-spikes-and-the-optimizers-own-instabilities.md)

## Aquecimento

1. ▢ O que o clipping pela norma global do gradiente faz com um gradiente cuja norma excede o limite de clipping e por que Rae et al. reduziram o limite especificamente para os dois maiores modelos?

<details markdown="1"><summary>Verificação</summary>

Ele reescala o gradiente inteiro proporcionalmente para que a sua norma seja igual ao limite, restringindo o tamanho que uma única atualização pode ter. Rae et al. reduziram o limite de 1 para 0,25 especificamente para o modelo de 7,1B e o Gopher (280B), para maior estabilidade nessa escala.

</details>

2. ▢ Por que baixar a learning rate não estabilizou a execução de 7,1B com Adafactor de Rae et al. e o que essa falha indicou?

<details markdown="1"><summary>Verificação</summary>

A execução com Adafactor já usava uma learning rate menor que a do baseline estável com Adam e ainda assim mostrou instabilidades, o que indicou que a instabilidade vinha do próprio otimizador nessa escala, e não simplesmente de uma learning rate alta demais.

</details>

## Saiba isto

### Começar devagar de propósito

Rae et al. não começam o treinamento na learning rate máxima que o seu schedule usa. Em vez disso, fazem o warm-up da learning rate de `10^-7` até o valor máximo gradualmente, ao longo dos primeiros 1.500 passos, antes de deixá-la seguir o resto do schedule. As primeiras atualizações de uma rede recém-inicializada são as menos informadas de toda a execução: os pesos ainda não viram dados, então uma atualização calculada a partir deles tem mais chance de ser uma correção inútil e exagerada do que uma atualização posterior, calculada quando a rede já se ajusta razoavelmente bem aos dados. Começar a learning rate perto de zero e aumentá-la gradualmente dá a essas primeiras atualizações, as menos confiáveis, um efeito menor sobre os pesos, em vez de deixá-las balançar o modelo tão forte quanto uma atualização totalmente aquecida faria.

### Decair depois

Quando o warm-up termina, Rae et al. fazem a learning rate decair por um fator de 10 ao longo do resto do treinamento, seguindo um schedule de cosseno: uma curva suave que começa na learning rate máxima e diminui em direção ao valor final com o formato de um quarto de onda de cosseno, em vez de cair em degraus bruscos. Essa é uma decisão separada do warm-up, voltada para um ponto diferente do treinamento: enquanto o warm-up protege o começo da execução, o decaimento trata de dar passos menores e mais cuidadosos à medida que o treinamento avança e a paisagem da loss perto de uma boa solução costuma pedir ajustes mais finos do que os passos grandes úteis no início.

### Modelos maiores, learning rates de pico menores

Rae et al. enunciam essa relação com clareza: à medida que o tamanho do modelo aumenta, eles diminuem a learning rate máxima da qual o schedule faz o warm-up e a partir da qual decai. Uma learning rate perfeitamente razoável para um modelo pequeno não é automaticamente segura para um muito maior; escolher uma learning rate máxima por modelo, em vez de reutilizar um valor fixo em todos os tamanhos treinados, é parte do que mantém as execuções maiores dentro da faixa que o clipping da Lição 16 e o warm-up desta lição pretendem proteger.

### O próprio batch size pode mudar no meio da execução

Junto com o schedule de learning rate, Rae et al. descrevem uma alavanca adicional: aumentar o batch size durante o próprio treinamento. O batch size do Gopher cresceu de três milhões para seis milhões de tokens por batch ao longo da sua execução de treinamento, e não ficou fixo do primeiro passo ao último. Um batch maior dá uma estimativa de gradiente menos ruidosa e mais confiável a cada passo e melhor utilização do hardware, mas começar uma execução inteira no maior batch size imediatamente não é necessariamente exigido para obter esses benefícios ao longo de todo o treinamento; crescer até ele no meio do caminho é uma decisão de schedule por si só, ao lado do warm-up e do decaimento da learning rate, e não algo que tenha de ser fixado para a execução inteira desde o começo.

## Prática

1. ▢ Por que começar o treinamento imediatamente na learning rate máxima, sem warm-up, poderia ser mais arriscado do que fazer o warm-up gradualmente, dado o que são as primeiras atualizações de uma rede recém-inicializada?

<details markdown="1"><summary>Verificação</summary>

As primeiras atualizações da rede, calculadas antes de ela ter visto qualquer dado, são as menos informadas de toda a execução e têm mais chance de ser correções exageradas e inúteis. Uma learning rate em força total aplicada a uma atualização dessas poderia balançar os pesos com força na direção errada; o warm-up limita o efeito que essas primeiras atualizações, as menos confiáveis, podem ter.

</details>

2. ▢ Qual é a diferença prática entre aquilo de que o warm-up protege e aquilo a que o decaimento em cosseno se destina?

<details markdown="1"><summary>Verificação</summary>

O warm-up protege o começo do treinamento, quando as atualizações da rede são as menos informadas. O decaimento em cosseno trata do treinamento posterior, dando gradualmente passos menores à medida que a paisagem da loss perto de uma boa solução costuma pedir ajustes mais finos do que os passos maiores úteis no início. Eles tratam de pontos diferentes da mesma execução, e não do mesmo problema duas vezes.

</details>

3. ▢ Segundo Rae et al., um modelo maior recebe uma learning rate máxima maior ou menor do que um menor, mantido o resto igual?

<details markdown="1"><summary>Verificação</summary>

Uma learning rate máxima menor. Rae et al. dizem diretamente que, à medida que o tamanho do modelo aumenta, eles diminuem a learning rate máxima que o schedule usa.

</details>

4. ▢ O batch size do Gopher cresceu de três milhões para seis milhões de tokens por batch ao longo do treinamento, em vez de começar em seis milhões desde o primeiro passo. Nomeie uma razão plausível para crescer até o batch size maior em vez de começar nele imediatamente.

<details markdown="1"><summary>Verificação</summary>

Qualquer explicação razoável serve, como: no início do treinamento, quando as atualizações já são menos estáveis (segundo o raciocínio do warm-up), somar um batch muito grande por cima disso pode não ser necessário para obter uma estimativa de gradiente útil, e crescer o batch size depois aproveita os benefícios do batch maior (um gradiente menos ruidoso, melhor utilização do hardware) quando o treinamento já chegou a uma região mais estável.

</details>

## Prática no mundo real

- [ ] Encontre a documentação de um framework de treinamento sobre as opções do seu scheduler de learning rate e identifique se ele expõe uma fase de warm-up, uma fase de decaimento em cosseno ou ambas, e como cada uma é configurada.
- [ ] Esboce, no papel, uma curva aproximada de learning rate contra passo de treinamento combinando o warm-up (uma rampa curta a partir de perto de zero) seguido do decaimento em cosseno (uma curva suave até um valor final muito menor), marcando aproximadamente onde ficaria o warm-up de 1.500 passos que Rae et al. descrevem em relação a uma execução de, digamos, 300.000 passos no total.
- [ ] Amanhã: para um tamanho de modelo que você escolher (pequeno, médio ou grande, nos seus próprios termos), decida qualitativamente se você esperaria que a sua learning rate máxima ficasse mais perto da do Gopher ou da de um modelo muito menor e escreva uma frase dizendo por quê, com base na relação com o tamanho do modelo desta lição.

## Para ir além

- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

A etapa 7 cobriu a numérica e o schedule que mantêm estável uma única execução de treinamento. A etapa 8 se volta para o que acontece ao longo dos muitos dias que uma execução dessas realmente leva: como o progresso sobrevive a ser salvo, retomado e interrompido por uma falha no meio do caminho.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
