---
title: "11. Memória de ativações e ZeRO-R"
description: "Particionar os estados do modelo resolve um problema de memória e deixa de pé um segundo, as ativações"
type: lesson
---

# Lição 11. Memória de ativações e ZeRO-R

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. As Lições 9 e 10 cobriram os três estágios do ZeRO-DP, que particionam os estados do modelo; esta lição cobre o problema de memória separado que esses três estágios não tocam.
**Fonte principal:** [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Pré-requisitos:** [Lição 10](0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md), [Checkpointing de ativações](../GLOSSARY.md)

## Aquecimento

1. ▢ A documentação do FSDP do PyTorch se descreve como inspirada em qual estágio do ZeRO?

<details markdown="1"><summary>Verificação</summary>

O estágio 3 do ZeRO (`P_os+g+p`), o estágio que particiona os parâmetros além do estado do otimizador e dos gradientes.

</details>

2. ▢ Por que particionar os parâmetros (estágio 3) soma comunicação que particionar o estado do otimizador e os gradientes (estágios 1 e 2) não soma?

<details markdown="1"><summary>Verificação</summary>

Porque o forward e o backward pass de cada dispositivo precisam de todos os parâmetros, e não só da fatia que ele possui, então as fatias que faltam têm de ser reunidas de outros dispositivos sob demanda, ao contrário do estado do otimizador e dos gradientes, de que só o dispositivo dono precisa.

</details>

## Saiba isto

### Resolver os estados do modelo deixa um segundo problema de pé

As Lições 9 e 10 cobriram o **ZeRO-DP**: os três estágios que particionam o estado do otimizador, os gradientes e os parâmetros, os 16 bytes por parâmetro que a Lição 8 contou. Rajbhandari et al. são explícitos em dizer que esse não é o quadro completo da memória. Quando os estados do modelo deixam de dominar, o que eles chamam de **memória residual**, as ativações mantidas do forward pass para calcular os gradientes no backward pass, os buffers temporários e a memória perdida para a fragmentação, se torna o próximo gargalo. O próprio exemplo do GPT-2 da Lição 8 mostrou que isso não é um efeito pequeno: cerca de 60 GB de memória de ativações com comprimento de sequência de 1.024 e batch size de 32, em um modelo cujos estados do modelo sozinhos somavam apenas 24 GB. Os três estágios do ZeRO-DP não fazem nada a respeito desses 60 GB; eles só tratam dos 24 GB. O **ZeRO-R** é a resposta separada de Rajbhandari et al. para o lado residual.

### O checkpointing ajuda, mas sozinho não basta

O checkpointing de ativações, o termo do glossário para o qual esta lição linka, descarta a maioria das ativações intermediárias durante o forward pass e as recalcula durante o backward pass em vez de mantê-las todas na memória o tempo todo, trocando compute extra por menor uso de memória. Rajbhandari et al. observam que o checkpointing ajuda, mas não é suficiente sozinho para os maiores modelos: mesmo o conjunto reduzido de ativações que o checkpointing mantém ainda pode ser grande e, em configurações que combinam paralelismo de dados com paralelismo de modelo, esse conjunto reduzido costuma ser replicado sem necessidade entre ranks de paralelismo de modelo que poderiam compartilhá-lo.

### O que o ZeRO-R acrescenta por cima

O ZeRO-R ataca a memória residual em três frentes, cada uma voltada para uma parte diferente dela:

- **Particionamento de ativações.** Onde o treinamento com paralelismo de modelo manteria de outra forma uma cópia redundante das mesmas ativações em cada rank de paralelismo de modelo, o ZeRO-R identifica e remove essa replicação, particionando as ativações do mesmo jeito que o ZeRO-DP particiona os estados do modelo, e pode adicionalmente fazer **offload** das ativações particionadas para a memória da CPU quando vale a pena fazer essa troca.
- **Buffers temporários de tamanho adequado.** Grandes buffers temporários usados durante o treinamento recebem um tamanho deliberadamente escolhido, equilibrando o uso de memória e a eficiência computacional, em vez de crescerem tanto quanto uma implementação ingênua permitiria.
- **Desfragmentação.** Tensores com tempos de vida muito diferentes (alguns vivem um passo de treinamento inteiro, outros só um instante) criam memória fragmentada ao longo do tempo, o que pode fazer uma alocação de memória falhar mesmo quando a memória livre total seria suficiente. O ZeRO-R gerencia a memória de forma proativa com base no tempo de vida esperado de cada tensor, para evitar que essa fragmentação se acumule.

Combinados, Rajbhandari et al. se referem ao ZeRO-DP e ao ZeRO-R juntos simplesmente como **ZeRO**: uma metade removendo a redundância nos estados do modelo, a outra controlando todo o resto que o treinamento mantém na memória.

## Prática

1. ▢ Uma equipe já aplicou o estágio 3 do ZeRO a um modelo, reduzindo a memória dos estados do modelo bem para dentro do orçamento, mas a execução ainda fica sem memória durante o forward pass em um comprimento de sequência longo. Isso é mais provavelmente um problema de estados do modelo ou de memória residual, e qual é uma coisa que poderia resolvê-lo?

<details markdown="1"><summary>Verificação</summary>

Um problema de memória residual, muito provavelmente memória de ativações, que é sensível ao comprimento da sequência de um jeito que os estados do modelo não são. O checkpointing de ativações, o particionamento de ativações ou o offload de ativações para a CPU são todas técnicas de memória residual que poderiam resolvê-lo; adicionar mais particionamento do ZeRO-DP não resolveria, já que os estados do modelo não eram o gargalo aqui.

</details>

2. ▢ Qual destas descreve melhor por que o checkpointing de ativações sozinho é descrito como insuficiente para os maiores modelos?

    - a) O checkpointing é incompatível com o ZeRO-DP e não pode ser usado junto com ele
    - b) Mesmo o conjunto reduzido de ativações que o checkpointing mantém ainda pode ser grande e pode ser replicado sem necessidade entre ranks de paralelismo de modelo, sem otimização adicional
    - c) O checkpointing aumenta o uso de memória em troca de menos compute
    - d) O checkpointing só funciona para modelos treinados sem precisão mista

<details markdown="1"><summary>Verificação</summary>

**b)** é o raciocínio do próprio artigo. (a) é falsa; o ZeRO-R é descrito como complementar ao checkpointing, e não como uma substituição que conflita com ele. (c) inverte o tradeoff real, que é menos memória por mais recomputação. (d) não é uma restrição que o artigo descreva.

</details>

3. ▢ Nomeie as três coisas que o ZeRO-R otimiza e associe cada uma ao problema de memória residual que ela tem como alvo: ativações replicadas sem necessidade entre ranks de paralelismo de modelo, alocação de memória falhando apesar de haver memória livre total suficiente e buffers temporários deixados crescer mais do que o necessário.

<details markdown="1"><summary>Verificação</summary>

O particionamento de ativações (e o offload) trata das ativações replicadas entre ranks de paralelismo de modelo. A desfragmentação, baseada no tempo de vida esperado de cada tensor, trata das falhas de alocação por memória fragmentada. Os buffers temporários de tamanho adequado tratam dos buffers que crescem mais do que um equilíbrio entre memória e eficiência de compute pediria.

</details>

## Prática no mundo real

- [ ] Encontre onde o checkpointing de ativações (às vezes chamado de gradient checkpointing) é exposto como opção em um framework de treinamento a que você tenha acesso e anote quanto ele custa em compute extra, se a documentação disser.
- [ ] Usando o exemplo de memória de ativações do GPT-2 da Lição 8 (cerca de 60 GB com comprimento de sequência de 1.024 e batch size de 32), preveja qualitativamente o que acontece com esse número se o comprimento da sequência for dobrado e confira a sua previsão com qualquer fórmula ou explicação que a documentação do framework dê para o escalonamento da memória de ativações.
- [ ] Amanhã: para um modelo e uma configuração de hardware a que você tenha acesso (ou hipotéticos), decida qual técnica de memória residual (checkpointing, particionamento de ativações, offload para a CPU ou alguma combinação) você tentaria primeiro e escreva uma frase dizendo por quê, dado o que cada uma sacrifica.

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

A etapa 5 cobriu como a memória de uma execução de treinamento é particionada entre dispositivos que fazem todos o mesmo tipo de trabalho. A etapa 6 cobre um tipo diferente de divisão: dividir o próprio modelo entre dispositivos que fazem, cada um, uma parte diferente do cálculo.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
