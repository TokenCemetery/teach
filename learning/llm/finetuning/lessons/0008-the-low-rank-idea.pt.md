---
title: "8. A ideia de baixo rank"
description: "`ΔW = BA`, e como contar um adapter"
type: lesson
---

# Lição 8. A ideia de baixo rank

**Ligação com a missão:** O LoRA é o método sobre o qual o resto da missão é construído. Esta lição é o mecanismo; as duas próximas são as decisões.
**Fonte principal:** [Artigo científico: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
**Pré-requisitos:** [Lição 6](0006-gradients-and-optimizer-state.md), [Lição 7](0007-activations-and-checkpointing.md), [adapter](../GLOSSARY.md)

## Aquecimento

1. ▢ Bytes por parâmetro treinável e por parâmetro congelado?

<details markdown="1"><summary>Verificação</summary>

Dezesseis treinável, dois congelado. A razão de oito para um é o motivo de os adapters existirem.

</details>

2. ▢ Sua execução com adapter está sem memória. O que você muda primeiro, e o que você não muda?

<details markdown="1"><summary>Verificação</summary>

Ative o gradient checkpointing, depois reduza o batch size por dispositivo com acumulação para compensar. Não reduza o rank: o estado do adapter é de megabytes, contra gigabytes de ativações.

</details>

3. ▢ Qual categoria de memória não é afetada por congelar o base?

<details markdown="1"><summary>Verificação</summary>

As ativações. Elas escalam com o batch size e o comprimento da sequência, e não com quantos parâmetros são treináveis.

</details>

## Saiba isto

O full fine-tuning aprende uma atualização `ΔW` para cada matriz de pesos, com o mesmo formato de `W`. A alegação do LoRA é que essa atualização não precisa ter rank completo, porque a mudança que uma tarefa exige ocupa um subespaço de baixa dimensão.

Então, em vez de armazenar `ΔW` diretamente, fatore-a:

```text
ΔW = B A

A : r × d_in     (down-projection, r is small)
B : d_out × r    (up-projection)
```

e a camada adaptada calcula:

```text
h = W₀ x + (α / r) · B A x
```

`W₀` está congelada. Só `A` e `B` recebem gradientes.

### Por que isso economiza tanto

Uma matriz `d_in × d_out` guarda `d_in · d_out` parâmetros. Sua fatoração de rank `r` guarda `r · (d_in + d_out)`. Para uma projeção 2048 × 2048 com rank 8:

```text
full        = 2048 × 2048        = 4,194,304
rank 8      = 8 × (2048 + 2048)  =    32,768
```

Uma redução de 128× nessa única matriz. No modelo inteiro a economia se compõe, porque você também dispensa o gradiente e os dois momentos do otimizador de tudo o que não tornou treinável.

### Contando um adapter

A fórmula, para um conjunto de target modules:

```text
adapter params = Σ over targeted layers of  r × (d_in + d_out)
```

Calculado, para o modelo de 24 camadas com `d = 2048` e `d_kv = 256` da Lição 5, rank 8, com alvo nas quatro projeções de atenção:

```text
q_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
k_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
v_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
o_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
per layer                                  = 102,400
× 24 layers                                = 2,457,600
```

Cerca de 2.5M de parâmetros treináveis contra um base de 1.12B, ou seja, **0.22%**. O estado do otimizador desse adapter é 2.5e6 × 16 ≈ 39 MB.

Note que o estreitamento da grouped-query attention importa aqui de um jeito que não importava para o base model: os adapters de `k_proj` e `v_proj` *não* são proporcionalmente menores, porque `r × (d_in + d_out)` é dominado pela maior das duas dimensões. Reduzir `d_out` de 2048 para 256 cortou a matriz base em 8×, mas o adapter em apenas 1.8×.

### Por que baixo rank é suficiente

A alegação empírica se apoia na **dimensionalidade intrínseca**: a observação de que o fine-tuning de um grande modelo pré-treinado para uma nova tarefa pode ser feito dentro de um subespaço surpreendentemente de baixa dimensão do seu espaço de parâmetros, e de que modelos maiores e mais bem pré-treinados têm dimensão intrínseca *menor*, e não maior (Aghajanyan et al., [arXiv:2012.13255](https://arxiv.org/abs/2012.13255)). O pré-treinamento já construiu as features; a adaptação é em grande parte uma questão de reponderar e recombinar essas features, e isso é uma operação pequena.

Duas ressalvas honestas:

**É uma alegação empírica, não um teorema.** Ela vale bem para adaptar comportamento, estilo, formato e competência estreita em uma tarefa. Vale menos para instalar grandes volumes de conhecimento genuinamente novo, que é um dos argumentos da Lição 27.

**"Baixo" é relativo e mudou.** A prática inicial se acomodou em ranks como 8 ou 16, em parte porque a memória era escassa. Trabalhos mais recentes, na [Lição 10](0010-choosing-target-modules.md), concluem que em muitas tarefas de supervised fine-tuning adapters com rank generoso cobrindo todas as camadas lineares igualam o full fine-tuning, enquanto os mesquinhos não. O rank 8 é um ponto de partida, não uma lei.

### A propriedade de inferência que torna o LoRA especial

Como a atualização é *aditiva* e linear, ela pode ser incorporada de volta ao peso base depois do treinamento:

```text
W = W₀ + (α / r) · B A
```

O resultado é uma matriz de pesos comum. **Um LoRA com merge tem exatamente zero de overhead de inferência**: sem matmuls extras, sem arquitetura alterada, nada a instalar no momento do serving. Essa é a propriedade que distingue o LoRA dos métodos de camada de adapter que o precederam, que inseriam novos módulos no caminho do forward e pagavam latência para sempre. A Lição 13 cobre o merge na prática, e a Lição 25 cobre quando *não* fazer merge.

## Prática

1. ▢ Calcule os parâmetros treináveis de um adapter de rank 16 só em `q_proj` e `v_proj`, em um modelo de 32 camadas com `d = 4096` e `d_kv = 1024`.

<details markdown="1"><summary>Verificação</summary>

`q_proj`: 16 × (4096 + 4096) = 131,072.
`v_proj`: 16 × (4096 + 1024) = 81,920.
Por camada: 212,992. Vezes 32 camadas ≈ 6.82M.

Contra um base de ~7B, isso é 0.10%.

</details>

2. ▢ Por que uma fatoração de rank `r` de uma matriz `d × d` economiza muito mais quando `d` é grande?

<details markdown="1"><summary>Verificação</summary>

A matriz completa cresce com `d²` enquanto a fatoração cresce com `2rd`, que é linear. A razão `d / 2r` melhora, portanto, à medida que o modelo se alarga.

É por isso que o LoRA fica *relativamente* mais barato em modelos maiores, e por isso o método importou mais conforme os modelos cresceram.

</details>

3. ▢ O que é o argumento da dimensionalidade intrínseca, e qual é o seu limite?

<details markdown="1"><summary>Verificação</summary>

Que adaptar um modelo bem pré-treinado a uma tarefa exige movimento apenas dentro de um subespaço de baixa dimensão do espaço de parâmetros, porque o pré-treinamento já construiu as features necessárias.

Seu limite: é uma constatação empírica sobre *adaptação*, mais forte para comportamento e formato e mais fraca para instalar conhecimento factual novo em quantidade substancial. Ela também não diz qual rank é suficiente para a sua tarefa específica.

</details>

4. ▢ Por que um LoRA com merge tem zero de overhead de inferência, quando os métodos anteriores de camada de adapter tinham?

<details markdown="1"><summary>Verificação</summary>

A atualização do LoRA é aditiva e linear no mesmo espaço do peso, então `W₀ + (α/r)BA` colapsa em uma única matriz comum. Os métodos de camada de adapter inseriam novos módulos não lineares no caminho do forward, que não podem ser dobrados e, portanto, somam latência em toda camada para sempre.

</details>

5. ▢ Verdadeiro ou falso: um adapter de rank 8 consegue representar qualquer atualização que um full fine-tune poderia.

<details markdown="1"><summary>Verificação</summary>

Falso. `ΔW = BA` com `B` de `r` colunas tem rank no máximo `r`, então só alcança atualizações dentro de um subespaço de rank 8. Um full fine-tune pode produzir uma atualização de rank completo.

A aposta é que a atualização de que a sua tarefa precisa esteja perto de um subespaço assim. Quando não está, você vê isso como um piso de loss que mais treinamento não reduz, e a correção é mais rank ou mais target modules, e não mais epochs.

</details>

6. ▢ Na grouped-query attention, a saída de `v_proj` encolhe de 4096 para 512. Por qual fator a matriz base encolhe, e por qual fator o seu adapter de rank 16 encolhe?

<details markdown="1"><summary>Verificação</summary>

Base: 4096 × 4096 → 4096 × 512, uma redução de 8×.
Adapter: 16 × (4096 + 4096) = 131,072 → 16 × (4096 + 512) = 73,728, uma redução de 1.8×.

O custo do adapter é dirigido pela soma das dimensões, então é dominado pela maior. Estreitar a menor dimensão quase não ajuda.

</details>

## Prática no mundo real

- [ ] Calcule à mão a contagem de parâmetros do adapter para um modelo e um conjunto de targets que você realmente pretende usar. Guarde o número.
- [ ] Construa o adapter em código e imprima a contagem de parâmetros treináveis. Ela deve bater com o seu cálculo à mão. Se não bater, descubra qual módulo você dimensionou errado.
- [ ] Amanhã: recalcule o mesmo adapter com rank 8, 32 e 128, e anote como muda a porcentagem do base model.

## Para ir além

- [Artigo científico: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- [Artigo científico: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
- [Hiperparâmetros do LoRA](../reference/lora-hyperparameters.md)
- [Lição 9. Rank, alpha e inicialização](0009-rank-alpha-and-initialisation.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
