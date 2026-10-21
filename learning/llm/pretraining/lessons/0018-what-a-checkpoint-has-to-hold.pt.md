---
title: "18. O que um checkpoint precisa guardar"
description: "Um checkpoint que salva apenas os pesos não consegue retomar uma execução com exatidão, e escolher a frequência de salvamento é um tradeoff à parte"
type: lesson
---

# Lição 18. O que um checkpoint precisa guardar

**Ligação com a missão:** "Consegue projetar um esquema de checkpointing que limita o progresso perdido após a falha de um nó" é o item de O sucesso se parece com isto que esta etapa atende. Esta lição cobre o que um checkpoint precisa conter e com que frequência salvar um; a Lição 19 cobre o que de fato acontece quando um nó falha no meio da execução.
**Fonte principal:** [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Pré-requisitos:** [Lição 17](0017-warmup-decay-and-growing-the-batch-mid-run.md)

## Aquecimento

1. ▢ Segundo Rae et al., um modelo maior recebe uma learning rate máxima maior ou menor do que um menor, mantido o resto igual?

<details markdown="1"><summary>Verificação</summary>

Uma learning rate máxima menor. Rae et al. dizem diretamente que, à medida que o tamanho do modelo aumenta, eles diminuem a learning rate máxima que o schedule usa.

</details>

2. ▢ O que o clipping pela norma global do gradiente faz com um gradiente cuja norma excede o limite de clipping?

<details markdown="1"><summary>Verificação</summary>

Ele reescala o vetor de gradiente inteiro proporcionalmente para que a sua norma seja igual ao limite, restringindo o tamanho que uma única atualização pode ter, em vez de descartar o gradiente ou mudar a learning rate.

</details>

## Saiba isto

### Um checkpoint é mais do que os pesos

Salvar apenas os parâmetros de um modelo não basta para retomar o treinamento exatamente de onde parou. Retomar corretamente uma execução de treinamento exige, no mínimo: os **parâmetros** do modelo; o **estado do otimizador** (no Adam, o momento e a variância que a Lição 8 contou, sem os quais o otimizador efetivamente recomeça a frio); a **contagem de passos e a posição no schedule de learning rate**, para que o warm-up e o decaimento (Lição 17) continuem do ponto certo em vez de recomeçar; e, para reprodutibilidade exata, a **posição do data loader e o estado do gerador de números aleatórios**, para que a execução não reprocesse nem pule dados silenciosamente em torno do ponto de reinício. Um checkpoint que falte qualquer um desses não falha de forma ruidosa; ele retoma em uma execução que parece ter continuado, enquanto treina discretamente de um jeito um pouco diferente do que uma execução ininterrupta teria treinado.

### Por que a frequência de checkpoint é um tradeoff à parte

Por mais completo que seja o conteúdo de um checkpoint, salvar um custa tempo e armazenamento: gravar o estado completo de um modelo grande em armazenamento durável leva tempo real de relógio, durante o qual a execução de treinamento costuma ficar pausada ou pelo menos não progride por completo, e cada checkpoint ocupa espaço real em disco, especialmente se vários recentes forem mantidos em vez de apenas o último. Fazer checkpoints com mais frequência limita quanto progresso uma falha pode destruir, já que apenas o trabalho desde o último checkpoint está em risco. Fazer checkpoints com menos frequência gasta menos tempo e armazenamento no total com os próprios checkpoints, ao custo de perder mais progresso na mesma falha. Nenhum dos extremos está certo em geral: a frequência correta depende de com que frequência as falhas são de fato esperadas, pesada contra quão caro realmente é gravar cada checkpoint.

### Com que frequência as falhas realmente acontecem, em uma execução real

O relato de Zhang et al. sobre o treinamento do OPT-175B torna concreta, e não hipotética, a parte do tradeoff sobre "com que frequência as falhas são esperadas". Ao longo de aproximadamente dois meses de treinamento, falhas de hardware contribuíram para pelo menos 35 reinícios manuais e para a rotação de mais de 100 hosts, e os autores estimam mais de 70 reinícios automáticos adicionais por cima disso, em uma única execução de treinamento. Isso é bem mais de um reinício a cada dois dias em média, sustentado durante toda a duração da execução. Um esquema de checkpointing construído em torno da suposição de que as falhas são eventos raros e ocasionais estaria muito errado para essa execução; um esquema que assume que as falhas são uma parte rotineira e esperada do processo, e faz checkpoints de acordo, é o que uma execução nessa escala de fato precisa.

## Prática

1. ▢ Uma equipe retoma uma execução de treinamento de um checkpoint que salvou os parâmetros do modelo, mas não o estado do otimizador. O que dá errado, mesmo que a execução retomada pareça, fora isso, estar continuando normalmente?

<details markdown="1"><summary>Verificação</summary>

O otimizador efetivamente recomeça a frio: no Adam, o momento e a variância acumulados antes do checkpoint se perdem, então as primeiras atualizações depois de retomar se comportam de modo diferente do que se comportariam se o treinamento nunca tivesse sido interrompido, mesmo que os próprios parâmetros estejam corretos.

</details>

2. ▢ Por que fazer checkpoints com mais frequência reduz a quantidade de progresso que uma falha pode destruir e o que custa obter esse benefício?

<details markdown="1"><summary>Verificação</summary>

Apenas o trabalho feito desde o checkpoint mais recente está em risco se uma falha acontecer, então um checkpoint mais recente limita a perda de forma mais apertada. O custo é o tempo gasto gravando cada checkpoint (durante o qual o treinamento costuma ficar pausado) e o armazenamento que cada um ocupa, ambos se acumulando mais rápido quanto mais vezes os checkpoints são salvos.

</details>

3. ▢ Zhang et al. relatam pelo menos 35 reinícios manuais, mais de 100 hosts rotacionados e uma estimativa de mais de 70 reinícios automáticos ao longo de aproximadamente dois meses de treinamento do OPT-175B. O que essa cifra defende em um esquema de checkpointing para uma execução de escala e duração semelhantes?

<details markdown="1"><summary>Verificação</summary>

Que as falhas devem ser tratadas como rotineiras e frequentes, e não como exceções raras, ao escolher com que frequência fazer checkpoints. Com bem mais de um reinício a cada dois dias, sustentado ao longo de toda a execução, um esquema de checkpointing feito para falhas ocasionais deixaria progresso demais exposto a qualquer momento.

</details>

## Prática no mundo real

- [ ] Encontre como um framework de treinamento a que você tenha acesso define o que entra em um checkpoint salvo (parâmetros, estado do otimizador, contagem de passos, estado do RNG) e verifique se algum dos quatro que esta lição nomeia está ausente ou é opcional na sua configuração padrão.
- [ ] Leia a seção "Hardware Failures" do artigo do OPT (linkado acima) e escreva uma frase descrevendo o procedimento operacional que os autores seguiram quando uma falha era detectada, antes de a Lição 19 cobri-lo diretamente.
- [ ] Amanhã: para uma execução hipotética à sua escolha (qualquer duração e escala), estime uma frequência de checkpoint que você escolheria e escreva uma frase justificando-a contra o custo de fazer checkpoints com frequência demais e o risco de fazê-los com pouca frequência.

## Para ir além

- [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
