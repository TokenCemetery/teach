---
title: "20. Lendo uma curva de loss"
description: "A curva de loss de treinamento sozinha subestima os problemas; dois outros sinais pegam o que ela deixa passar, e pegam mais cedo"
type: lesson
---

# Lição 20. Lendo uma curva de loss

**Ligação com a missão:** "Consegue ler um dashboard de treinamento e dizer se a execução está no caminho certo" é o item de O sucesso se parece com isto que esta etapa atende. Esta lição cobre o que de fato acompanhar em um dashboard ao vivo; a Lição 21 cobre a avaliação de checkpoints salvos contra dados held-out.
**Fonte principal:** [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Pré-requisitos:** [Lição 19](0019-surviving-a-node-failure.md)

## Aquecimento

1. ▢ O que Zhang et al. notaram que estava correlacionado com a divergência de loss durante o treinamento do OPT-175B, além da própria curva de loss?

<details markdown="1"><summary>Verificação</summary>

O seu loss scalar dinâmico (parte da configuração de precisão mista) caindo a zero e a norma das ativações da última camada disparando.

</details>

2. ▢ Por que a recuperação de uma divergência de loss defende manter mais do que apenas o único checkpoint mais recente?

<details markdown="1"><summary>Verificação</summary>

Porque o melhor ponto de reinício foi escolhido com base na saúde do loss scalar e na tendência da norma das ativações, o que nem sempre era o checkpoint mais recente; manter apenas o mais novo removeria a opção de voltar mais atrás.

</details>

## Saiba isto

### A curva de loss de treinamento e o que "saudável" significa para ela

A coisa mais básica que um dashboard de treinamento mostra é a própria loss de treinamento, plotada contra o passo de treinamento ou a contagem de tokens. As leis de escala da etapa 3 dão uma expectativa real para o seu formato: a loss deve cair suavemente, seguindo aproximadamente uma curva do tipo lei de potência à medida que o compute e os tokens se acumulam, e não em linha reta nem em uma série de saltos sem relação. Uma curva que acompanha esse formato geral está se comportando como esperado; uma curva que estaciona muito antes do que a trajetória da lei de escala preveria, ou que mostra uma subida súbita e acentuada (um loss spike, Lição 16), é uma curva de loss de treinamento que reporta algo que vale investigar, antes de supor que a execução simplesmente está no caminho certo.

### Dois sinais que pegam problemas antes de a curva de loss mostrá-los claramente

Acompanhar só a loss de treinamento não basta, porque quando um spike fica visível na própria loss, o problema subjacente pode já estar se formando há algum tempo. O relato de Zhang et al. sobre o OPT-175B dá dois outros sinais que avisaram mais cedo do mesmo problema que a curva de loss acabou mostrando: o seu **loss scalar dinâmico**, parte da configuração de precisão mista, caindo em direção a zero, e a **norma das ativações da última camada** disparando para cima. Ambos são sintomas de uma execução de treinamento a caminho da instabilidade, visíveis antes, ou junto com, a divergência clara da própria loss, e é exatamente por isso que Zhang et al. os usaram, e não apenas a curva de loss, para julgar se um dado ponto do treinamento era seguro para reiniciar.

### A norma do gradiente, acompanhada ao longo do tempo

A Lição 16 cobriu o clipping pela norma do gradiente como uma salvaguarda por passo, restringindo o tamanho que qualquer atualização individual pode ter. A mesma norma do gradiente, acompanhada como uma curva ao longo do treinamento e não apenas conferida contra o limite de clipping a cada passo, é em si um sinal útil: uma norma do gradiente que tende a subir com o tempo, ou que dispara repetidamente mesmo depois do clipping, pode ser um sinal precoce do mesmo tipo de instabilidade que um loss spike acabaria mostrando de forma mais dramática, dando a chance de intervir, por exemplo baixando a learning rate, antes que uma divergência completa force um reinício.

### Acompanhar, continuamente

Nenhum desses sinais ajuda se ninguém, ou nada automatizado, estiver de fato olhando para eles. A etapa 8 estabeleceu que falhas e instabilidades são uma parte rotineira e frequente de uma execução de treinamento grande, e não um evento raro; um dashboard que mostra a loss, a norma do gradiente e um sinal de estabilidade numérica como um loss scalar só é útil se for conferido com frequência suficiente, ou alertar de forma automática o bastante, para pegar um problema em desenvolvimento antes que custe muito mais progresso do que uma detecção anterior teria custado.

## Prática

1. ▢ A curva de loss de treinamento de uma equipe está diminuindo, mas de forma visivelmente mais lenta do que as relações das leis de escala da etapa 3 preveriam para o tamanho do modelo e a contagem de tokens até agora. Isso é necessariamente sinal de um problema, ou pode ser compatível com uma execução saudável?

<details markdown="1"><summary>Dica</summary>

As leis de escala são ajustes empíricos com variância real, e não uma garantia exata para cada execução individual.

</details>

<details markdown="1"><summary>Verificação</summary>

Vale investigar em vez de supor que está tudo bem, mas não é automaticamente prova de um problema; as leis de escala são tendências ajustadas com variância, e não uma garantia exata por execução. Uma distância significativa e sustentada da trajetória esperada é uma razão legítima para conferir outros sinais (a norma do gradiente, um loss scalar se estiver usando precisão mista, ou o próprio pipeline de dados) em vez de supor que a curva sozinha resolve a questão para um lado ou para o outro.

</details>

2. ▢ Por que um loss scalar caindo em direção a zero, ou uma norma de ativações disparando, poderia avisar mais cedo da instabilidade do que a própria curva de loss de treinamento?

<details markdown="1"><summary>Verificação</summary>

Esses são sintomas do problema numérico subjacente se desenvolvendo, que podem aparecer antes de ele crescer o bastante para perturbar visivelmente a curva de loss. Quando um spike fica claramente visível na própria loss, o problema pode já estar se formando há algum tempo.

</details>

3. ▢ Qual destas descreve melhor por que um dashboard que acompanha a loss, a norma do gradiente e um sinal de estabilidade como um loss scalar só é útil na prática se for monitorado com frequência?

    - a) Essas métricas só têm significado uma vez por execução de treinamento, bem no final
    - b) Falhas e instabilidades são eventos frequentes e rotineiros em escala (etapa 8), então um problema pego tarde custa muito mais progresso perdido do que o mesmo problema pego cedo
    - c) As próprias métricas mudam de significado se conferidas com frequência demais
    - d) O monitoramento frequente só é útil para modelos muito pequenos

<details markdown="1"><summary>Verificação</summary>

**b)** é o raciocínio real: dada a frequência com que falhas e instabilidades ocorrem em escala, o valor de um dashboard está diretamente ligado a quão rápido um problema em desenvolvimento é notado. (a), (c) e (d) não refletem nada que esta lição ou a etapa 8 tenha estabelecido.

</details>

## Prática no mundo real

- [ ] Encontre o dashboard de um framework de treinamento ou de uma ferramenta de acompanhamento de experimentos (Weights & Biases, TensorBoard ou similar) e identifique quais dos sinais desta lição (loss, norma do gradiente, um indicador de estabilidade numérica) ele exibe por padrão e quais precisariam ser adicionados explicitamente.
- [ ] Leia o parágrafo do artigo do OPT (linkado acima) que liga a divergência de loss ao loss scalar e à norma das ativações e escreva uma frase sobre qual sinal você conferiria primeiro se visse um loss spike em um dashboard com os três disponíveis.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 21: se a loss de treinamento sozinha não diz como um modelo se sai nas tarefas para as quais as pessoas vão de fato usá-lo, o que precisaria ser medido de forma diferente para verificar isso durante o treinamento, e não apenas depois que ele termina?

## Para ir além

- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
