---
title: "14. Combinando os três: quando o paralelismo de tensor e de pipeline compensam o seu custo"
description: "Associar cada estratégia de paralelismo à interconexão que ela tolera e quando o particionamento sozinho não basta"
type: lesson
---

# Lição 14. Combinando os três: quando o paralelismo de tensor e de pipeline compensam o seu custo

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto, e esta lição é onde ele se fecha: quando vale a pena recorrer à engenharia extra do paralelismo de tensor e de pipeline.
**Fonte principal:** [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Pré-requisitos:** [Lição 13](0013-pipeline-parallelism-splitting-the-models-layers.md)

## Aquecimento

1. ▢ O que é a bolha do pipeline e o que um flush de pipeline troca por ela?

<details markdown="1"><summary>Verificação</summary>

A bolha do pipeline é o tempo ocioso no início e no fim de um batch, enquanto o pipeline enche ou esvazia. Um flush de pipeline deixa o pipeline esvaziar e sincroniza o passo do otimizador de todos os dispositivos, o que causa a bolha; a alternativa arriscaria o backward pass de um micro-batch ver uma versão dos pesos diferente da que o seu forward pass usou.

</details>

2. ▢ Na divisão do MLP do paralelismo de tensor, quantas operações de all-reduce o bloco inteiro precisa e onde ela acontece?

<details markdown="1"><summary>Verificação</summary>

Uma, depois da segunda multiplicação de matrizes, combinando a soma parcial de cada dispositivo no resultado completo.

</details>

## Saiba isto

### Três eixos, combinados

Narayanan et al. chamam de **PTD-P** a combinação dos três, paralelismo de tensor, paralelismo de pipeline e paralelismo de dados, ao mesmo tempo. Cada eixo divide uma coisa diferente: o paralelismo de tensor divide o que uma única camada calcula (Lição 12), o paralelismo de pipeline divide por quais camadas um dispositivo é responsável (Lição 13) e o paralelismo de dados (Lições 7 e 8, opcionalmente particionado mais ainda com o ZeRO, Lições 9 a 11) divide o batch entre réplicas de qualquer configuração de paralelismo de tensor e de pipeline que esteja sendo replicada. Combinados assim, Narayanan et al. relatam o treinamento de um modelo de um trilhão de parâmetros a 502 petaFLOP/s em 3.072 GPUs, com cada GPU sustentando 52% do seu throughput de pico teórico, uma fração genuinamente grande para se manter nessa escala.

### Por que a divisão segue a interconexão, e não só o modelo

Narayanan et al. dão uma razão direta e prática para como atribuem dispositivos a cada eixo: o all-reduce do paralelismo de tensor, necessário uma vez por camada como a Lição 12 descreveu, é caro o bastante para que tenha o melhor desempenho confinado a dispositivos conectados pela interconexão mais rápida possível, dentro de um único nó (os experimentos deles usam um servidor DGX A100 de 8 GPUs). O paralelismo de pipeline, ao contrário, só passa ativações entre um punhado de fronteiras de estágio, usando uma comunicação ponto a ponto que Narayanan et al. descrevem como "muito mais barata" e que tolera ser espalhada por nós separados sem engarrafar a computação inteira, ao custo da bolha que a Lição 13 cobriu. Eles relatam o desempenho de pico especificamente quando o tamanho do paralelismo de tensor corresponde ao número de GPUs de um único nó, confirmando que isso não é um detalhe incidental: é a configuração que os próprios resultados deles dizem para almejar.

### Por que não usar o ZeRO em todo lugar e pular a engenharia extra

O artigo do ZeRO de Rajbhandari et al. faz o seu próprio argumento diretamente, defendendo que, para o propósito específico de encaixar um modelo grande na memória, o ZeRO-DP (Lições 9 a 11) é pelo menos tão eficaz quanto o paralelismo de modelo, às vezes mais, com eficiência de escalonamento comparável ou melhor, sendo muito mais fácil de aplicar: o paralelismo de dados, observam eles, é amplamente utilizável em cargas de trabalho diferentes sem mudanças, enquanto abordagens de paralelismo de modelo como o paralelismo de tensor e de pipeline muitas vezes exigem trabalho real de engenharia, revisando o próprio modelo e construindo operadores distribuídos para ele. O paralelismo de tensor e de pipeline não são alternativas gratuitas ao particionamento; custam esforço real de desenvolvimento além do seu custo de comunicação.

Juntando as posições dos dois artigos, a resposta prática a "quando o paralelismo de tensor ou de pipeline vale o seu custo" é: recorra primeiro ao particionamento no estilo do ZeRO, já que ele resolve o problema de memória com o menor esforço de engenharia e nenhum trabalho específico do modelo. Recorra ao paralelismo de tensor e de pipeline especificamente quando uma execução de treinamento precisar escalar além do que o particionamento sozinho trata com eficiência, comumente em uma contagem de dispositivos e um tamanho de modelo em que o overhead de comunicação dos próprios all-gathers do particionamento se torna o gargalo, ou em que os pesos reconstruídos de uma única camada ainda são grandes demais para um dispositivo mesmo depois do particionamento. Nesse ponto, a combinação é escolhida deliberadamente para casar o padrão de comunicação com a interconexão: os all-reduces frequentes e caros do paralelismo de tensor confinados dentro de um nó, as transferências ponto a ponto raras e baratas do paralelismo de pipeline atravessando nós e o paralelismo de dados (particionado ou não) preenchendo a contagem de dispositivos que sobrar.

## Prática

1. ▢ Uma equipe tem 64 GPUs arranjadas em 8 nós de 8 GPUs cada, com interconexão rápida dentro do nó e links entre nós muito mais lentos. Seguindo a configuração de pico relatada pelo próprio Narayanan et al., como eles atribuiriam os graus de paralelismo de tensor e de pipeline a esse hardware?

<details markdown="1"><summary>Verificação</summary>

Tamanho do paralelismo de tensor de 8, correspondendo às GPUs dentro de um nó, mantido fora dos links mais lentos entre nós; estágios de pipeline atravessando os 8 nós, já que a comunicação ponto a ponto do paralelismo de pipeline tolera a conexão mais lenta entre nós sem engarrafar a computação.

</details>

2. ▢ Segundo o argumento do próprio artigo do ZeRO, por que uma equipe poderia escolher o ZeRO-DP em vez do paralelismo de tensor ou de pipeline, mesmo que ambos escalem para modelos muito grandes?

    - a) O ZeRO-DP é sempre mais rápido, em qualquer contagem de dispositivos, para todo modelo
    - b) O ZeRO-DP alcança eficiência de memória comparável ou melhor sem exigir o trabalho de engenharia específico do modelo (código de modelo revisado, operadores distribuídos) de que as abordagens de paralelismo de modelo precisam
    - c) O paralelismo de tensor e de pipeline não conseguem encaixar modelos maiores que a memória de um único dispositivo
    - d) O ZeRO-DP elimina por completo a necessidade de qualquer forma de paralelismo

<details markdown="1"><summary>Verificação</summary>

**b)** é o argumento que o próprio artigo do ZeRO faz: eficiência de escalonamento comparável ou melhor, com muito menos custo de engenharia, já que o paralelismo de dados é amplamente aplicável sem mudanças específicas do modelo. (a) exagera uma vantagem universal de velocidade que o artigo não afirma. (c) é o oposto do ponto de ambos os artigos, o de que o paralelismo de modelo existe justamente para encaixar modelos maiores. (d) contradiz a própria dependência do ZeRO-DP do paralelismo de dados como fundação.

</details>

3. ▢ Dado o raciocínio desta lição, nomeie uma situação concreta em que recorrer ao paralelismo de tensor ou de pipeline, apesar do seu custo extra de engenharia, ainda seria a decisão certa em vez do ZeRO-DP sozinho.

<details markdown="1"><summary>Verificação</summary>

Qualquer resposta nesta linha é defensável: quando o overhead de comunicação do próprio particionamento se torna o gargalo em contagens de dispositivos muito grandes, ou quando os parâmetros de uma única camada continuam grandes demais para caber em um dispositivo mesmo depois do particionamento e da reconstrução sob demanda do ZeRO, forçando que a própria computação, e não só o seu armazenamento, seja dividida entre dispositivos.

</details>

## Prática no mundo real

- [ ] Encontre uma configuração de treinamento publicada de um modelo aberto grande (um relatório técnico ou model card que declare a sua configuração de paralelismo) e identifique quais partes, se houver, correspondem ao paralelismo de tensor, ao paralelismo de pipeline e ao paralelismo de dados ou particionamento do ZeRO.
- [ ] Leia o parágrafo do artigo do Megatron-LM (linkado acima) que descreve por que o paralelismo de tensor é confinado dentro de um nó e escreva uma frase contrastando-o com o argumento do artigo do ZeRO a favor de preferir o paralelismo de dados sempre que possível.
- [ ] Amanhã: para um cluster hipotético à sua escolha (escolha qualquer número de nós e de GPUs por nó), esboce um plano de paralelismo: o que ficaria dentro de um nó, o que atravessaria nós e onde o particionamento do ZeRO se encaixaria, e escreva uma frase defendendo cada escolha.

## Para ir além

- [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

A etapa 6 cobriu como o compute é dividido entre dispositivos, casado com o que a interconexão entre eles aguenta. A etapa 7 se volta para um tipo diferente de falha em escala: a numérica da própria execução de treinamento e o que fazer quando a curva de loss para de se comportar.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
