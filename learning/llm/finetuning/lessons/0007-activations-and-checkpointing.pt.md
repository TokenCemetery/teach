---
title: "7. Ativações, batch size e checkpointing"
description: "Por que uma execução com adapter ainda fica sem memória"
type: lesson
---

# Lição 7. Ativações, batch size e checkpointing

**Ligação com a missão:** Os adapters removem o custo do otimizador, mas não o custo das ativações, e é por isso que uma execução de LoRA ainda pode ficar sem memória. Esta é a parte que surpreende as pessoas.
**Fonte principal:** [Artigo científico: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
**Pré-requisitos:** [Lição 6](0006-gradients-and-optimizer-state.md)

## Aquecimento

1. ▢ Bytes por parâmetro treinável com AdamW, precisão mista?

<details markdown="1"><summary>Verificação</summary>

Dezesseis bytes: dois para os pesos em bf16, quatro para a cópia master em fp32, dois para o gradiente em bf16 e quatro para cada um dos dois momentos.

</details>

2. ▢ Bytes por parâmetro congelado?

<details markdown="1"><summary>Verificação</summary>

Dois, em bf16, só para o valor do peso. Sem gradiente, sem momentos, sem cópia master.

</details>

3. ▢ Por que os momentos do AdamW não podem simplesmente ser descartados em transformers?

<details markdown="1"><summary>Verificação</summary>

As magnitudes dos gradientes variam enormemente entre os parâmetros de um transformer, e o segundo momento fornece a escala de passo por parâmetro que um único learning rate global não consegue.

</details>

## Saiba isto

Os gradientes e o estado do otimizador escalam com a **contagem de parâmetros**. As ativações escalam com o **batch size e o comprimento da sequência**, e são quase independentes de quantos parâmetros são treináveis. Congelar o base não ajuda em nada aqui.

### Por que as ativações existem

O backward pass precisa da entrada de cada camada para calcular o gradiente dessa camada. Por isso o forward pass mantém seus resultados intermediários em vez de descartá-los. Cada tensor mantido tem aproximadamente:

```text
batch_size × sequence_length × hidden_size × bytes_per_element
```

por tensor, e um bloco transformer guarda uma dúzia ou mais deles: depois de cada normalização, cada projeção, a saída da atenção, o intermediário da MLP na sua dimensão mais larga, e assim por diante. Multiplique pelo número de camadas.

Um número de trabalho aproximado para um bloco transformer em bf16, contando os tensores notáveis:

```text
activations ≈ n_layers × batch × seq_len × hidden × ~20 bytes
```

Trate a constante como um ponto de partida a ser medido, e não como uma lei, porque ela varia com a implementação da atenção, com a função de ativação e com o framework fundir ou não as operações. O que importa é o *formato* da fórmula.

### As consequências do formato

**Linear no batch size.** Dobre o batch, dobre a memória de ativações. É o botão que você alcança primeiro, e o gradient accumulation (Lição 4) recupera o batch size efetivo sem custo em memória.

**Linear no comprimento da sequência** para as ativações armazenadas, e quadrático para a matriz de scores de atenção, a menos que você use um kernel de atenção eficiente em memória. Implementações modernas como o FlashAttention evitam materializar a matriz completa `seq_len × seq_len`, o que remove o termo quadrático. Se você ainda esbarra em uma explosão quadrática em sequências longas, a correção é a implementação da atenção, e não o batch size.

Calculado, para um modelo de 24 camadas com tamanho oculto 2048, batch 4, comprimento de sequência 2048:

```text
24 × 4 × 2048 × 2048 × 20 bytes ≈ 8.0 GB
```

Oito gigabytes de ativações, contra aproximadamente 2.2 GB de pesos congelados em bf16 e algumas dezenas de megabytes de estado do adapter. **As ativações agora são o custo dominante.** Este é o perfil de memória de uma execução típica com adapter, e é o oposto do perfil do full fine-tuning da Lição 6.

### Gradient checkpointing

A troca que resolve: não armazene a maior parte das ativações. Armazene algumas e recalcule o resto durante o backward pass.

Mantenha a entrada de cada bloco (um *checkpoint*), descarte tudo o que há dentro dele e, quando o backward pass chega àquele bloco, execute o forward pass dele de novo para regenerar o que é necessário. O armazenamento cai de aproximadamente linear na profundidade para aproximadamente a raiz quadrada dela, ao custo de cerca de um forward pass extra, normalmente de 20 a 40% mais lento por passo.

![Duas curvas ao longo da profundidade. Sem checkpointing, as ativações armazenadas sobem em linha reta com o número de camadas. Com checkpointing, seguem a raiz quadrada e se achatam quase de imediato. Em 24 camadas, as duas ficam cerca de cinco vezes distantes.](images/linear-against-square-root.svg)

O formato dessa troca é o motivo de ela ser quase um padrão. Uma reta e uma raiz quadrada mal se distanciam em duas ou três camadas, então em um modelo de brinquedo a técnica parece inútil; a distância é de cerca de cinco vezes nas 24 camadas do exemplo calculado e continua se alargando, e o preço continua sendo um forward pass extra, por mais profundo que o modelo fique.

```python
model.gradient_checkpointing_enable()
model.config.use_cache = False  # incompatible with checkpointing during training
```

Essa segunda linha importa. O KV cache existe para acelerar a *geração* autorregressiva e não tem papel no treinamento; deixá-lo ligado junto com o checkpointing produz avisos, na melhor das hipóteses, e memória desperdiçada, na pior.

**O gradient checkpointing é quase um padrão para o fine-tuning com adapters.** Ele recompra o maior custo individual do perfil acima, e a lentidão quase sempre vale a pena.

### Padding e packing

Toda sequência de um batch recebe padding até o tamanho do seu membro mais longo, e o padding consome memória de ativações sem contribuir com nada. Dois remédios:

- **Agrupamento por comprimento.** Agrupe em um batch sequências de tamanho parecido, para que seja preciso menos padding.
- **Packing.** Concatene exemplos curtos em sequências de comprimento total, eliminando o padding quase por completo.

O packing é um ganho real de eficiência em datasets de exemplos curtos, e tem um requisito de correção: exemplos empacotados juntos não podem prestar atenção através das suas fronteiras. As implementações cuidam disso com reinício de posições e atenção consciente das fronteiras. Se você ativar o packing, verifique se o seu mascaramento da loss sobrevive a ele: uma sequência empacotada precisa manter os seus labels `-100` intactos, ou a loss apenas da completion vira em silêncio loss de sequência completa.

### A ordem para tentar as coisas

Quando uma execução não cabe, na ordem do que você abre mão:

1. Ative o gradient checkpointing, que custa só tempo
2. Reduza o batch size por dispositivo e aumente o gradient accumulation, o que custa um pouco de tempo e não muda nada estatisticamente
3. Reduza o comprimento da sequência, o que muda a tarefa, então confira antes a sua distribuição de comprimento em tokens
4. Quantize o base model, que é a etapa 4 e custa alguma qualidade
5. Reduza o rank do adapter, o que custa capacidade e economiza o menos de todas as opções aqui

Esse último ponto merece atenção. O rank é o botão que as pessoas alcançam primeiro e é quase o *menos* eficaz, porque os parâmetros do adapter são uma fração minúscula do total. Reduzir o rank pela metade em um adapter de 4M de parâmetros economiza 32 MB.

## Prática

1. ▢ Quais destes escalam com a contagem de parâmetros treináveis e quais com o batch e o comprimento da sequência: gradientes, ativações, momentos do otimizador, pesos congelados?

<details markdown="1"><summary>Verificação</summary>

Contagem de parâmetros treináveis: gradientes, momentos do otimizador. Só o tamanho do modelo: pesos congelados. Batch e comprimento da sequência: ativações.

Que as ativações pertençam a um eixo completamente diferente é o ponto desta lição, e o motivo pelo qual os adapters não as resolvem.

</details>

2. ▢ Estime a memória de ativações para um modelo de 32 camadas, tamanho oculto 4096, batch 2, comprimento de sequência 4096, bf16.

<details markdown="1"><summary>Verificação</summary>

32 × 2 × 4096 × 4096 × 20 ≈ 21 GB.

Enorme em relação a um base de 7B congelado de 14 GB. Com o gradient checkpointing isso cai em aproximadamente uma ordem de grandeza, o que torna a execução possível em um único dispositivo.

</details>

3. ▢ Sua execução de LoRA fica sem memória. Um colega sugere baixar o rank de 64 para 8. Avalie.

<details markdown="1"><summary>Verificação</summary>

Vai ajudar muito pouco. Ir do rank 64 para o 8 em um modelo de 7B economiza da ordem de uma centena de megabytes de estado e gradientes do adapter, contra ativações medidas em gigabytes.

Ative o gradient checkpointing e reduza primeiro o batch size por dispositivo. O rank é uma decisão de capacidade, e gastá-la com uma memória que não estava faltando é uma troca ruim.

</details>

4. ▢ Por que o `use_cache` precisa ser desativado quando o gradient checkpointing está ligado?

<details markdown="1"><summary>Verificação</summary>

O KV cache armazena keys e values passados para evitar recalculá-los durante a geração autorregressiva. O treinamento faz um único forward pass sobre uma sequência completa, então o cache não traz benefício, e ele conflita com a estratégia de recálculo do checkpointing enquanto consome memória.

</details>

5. ▢ O que o gradient checkpointing troca, nas duas direções?

<details markdown="1"><summary>Verificação</summary>

Ele troca computação por memória: o armazenamento de ativações cai de aproximadamente linear na profundidade para aproximadamente a sua raiz quadrada, em troca de aproximadamente um forward pass extra por passo, normalmente de 20 a 40% mais lento.

</details>

6. ▢ Você ativa o packing e o seu modelo começa a produzir respostas para perguntas que ninguém fez. O que deu errado?

<details markdown="1"><summary>Verificação</summary>

Muito provavelmente a máscara da loss não sobreviveu ao packing, então os tokens do prompt agora estão sendo treinados, ou os exemplos estão prestando atenção através das suas fronteiras e aprendendo que um texto não relacionado vem depois de uma resposta.

Verifique se os labels `-100` são preservados no passo de packing e se a implementação é consciente das fronteiras. O packing é uma otimização de eficiência com uma precondição de correção.

</details>

## Prática no mundo real

- [ ] Execute um passo de treinamento com batch 1, depois batch 2, depois batch 4, registrando o pico de memória a cada vez. Confirme que a relação é linear.
- [ ] Ligue o gradient checkpointing e repita. Registre tanto a memória economizada quanto os segundos por passo perdidos, e decida se você aceitaria essa troca.
- [ ] Amanhã: meça a distribuição de comprimento em tokens de um dataset real com o tokenizer de verdade. Encontre o percentil 95. Esse, e não o máximo, é o seu comprimento de sequência.

## Para ir além

- [Artigo científico: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
- [Artigo científico: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- [Docs: Methods and tools for efficient training on a single GPU, Hugging Face](https://huggingface.co/docs/transformers/main/en/perf_train_gpu_one)
- [Orçamento de memória](../reference/memory-budget.md): agora completo o bastante para usar

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
