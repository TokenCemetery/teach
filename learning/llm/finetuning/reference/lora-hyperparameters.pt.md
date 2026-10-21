---
title: "Hiperparâmetros do LoRA"
description: "Rank, alpha, targets, learning rate, variantes"
type: reference
---

# Hiperparâmetros do LoRA

Folha de decisão. Leia a versão instalada da biblioteca para os nomes exatos dos parâmetros, porque essa superfície muda entre releases.

## A equação

```text
h = W₀x + (α/r) · BAx
```

`A` aleatória, `B` zero, então `ΔW = 0` no passo 0 e o modelo começa idêntico ao base.

![A entrada alimenta dois caminhos que são somados. O de cima é a matriz base congelada. O de baixo é o adapter treinado, em que A projeta para baixo até uma barra de apenas r de largura, B projeta de volta para cima e o resultado é escalado por alpha sobre r.](images/lora-bottleneck.svg)

A barra entre `A` e `B` tem `r` valores de largura, e é o único caminho que o adapter tem da entrada à saída. É isso que a próxima seção quer dizer com capacidade: aumentar o rank alarga essa barra e não muda mais nada na figura, e é por isso que ele compra expressividade por quase nenhuma memória.

## Rank

Capacidade. Limita quão complexa pode ser a atualização que o adapter consegue expressar.

| Rank | Serve para |
|---|---|
| 4 a 8 | Estilo, tom, formato de saída; datasets pequenos |
| 16 a 32 | Uma tarefa real, alguns milhares de exemplos |
| 64 a 128 | Tarefas mais difíceis, mais dados, comportamento que exige muito raciocínio |
| 256+ | Aproximando-se da capacidade do full fine-tuning com muitos dados de SFT |

O rank custa quase nada de memória. Seu custo real é o risco de overfitting em poucos dados.

## Alpha

**Só `α/r` importa.** A convenção é `α = 2r`.

| `r` | `α` | `α/r` | |
|---|---|---|---|
| 8 | 16 | 2.0 | baseline |
| 16 | 32 | 2.0 | mais capacidade, mesma escala |
| 16 | 16 | 1.0 | atualização mais fraca |
| 64 | 16 | 0.25 | **armadilha**: capacidade sobe, influência cai 8× |

Aumentar `r` sem aumentar `α` *abaixa* o adapter. Com rank ≥ 64, considere `use_rslora=True`, que usa `α/√r`.

## Target modules

| Situação | Targets |
|---|---|
| Padrão para uma tarefa real | all linear |
| Dataset pequeno (< ~1k) | só atenção, rank baixo |
| Apenas estilo ou tom | só atenção, rank baixo |
| Precisa de novas discriminações | precisa incluir o MLP |
| Reproduzindo um artigo | exatamente os dele |

`"all-linear"` é resolvido contra o modelo carregado, então não fica obsoleto diante de nomenclaturas desconhecidas. Só atenção é uma ablação de 2021, não um padrão.

Nomes típicos, mas **verifique com `named_modules()`**:

```text
attention: q_proj  k_proj  v_proj  o_proj
mlp:       gate_proj  up_proj  down_proj
```

## Learning rate

| Método | Faixa |
|---|---|
| Fine-tuning com adapter | `1e-4` a `2e-4` |
| Full fine-tuning | `1e-5` a `5e-5` |

Importar o learning rate de um full fine-tuning para uma execução com adapter é uma das principais causas de um primeiro resultado decepcionante. Use warm-up (algumas centenas de passos) e decaimento cosseno.

## Outras configurações

| Configuração | Padrão | Observações |
|---|---|---|
| `lora_dropout` | 0.0 a 0.05 | Aumente só se a loss held-out estiver subindo |
| `bias` | `"none"` | Raramente decisivo; complica o merge |
| Epochs | 2 a 3 | Em poucos dados de instrução; mais que isso costuma memorizar |
| Gradient checkpointing | ligado | Quase um padrão para adapters |
| `use_cache` | desligado no treinamento | Conflita com o checkpointing; inútil para treinar |

## Variantes, por eixo

| Eixo | Método | Ajuda quando |
|---|---|---|
| Escala | rsLoRA | Rank alto |
| Learning rates | LoRA+ | Taxas separadas para `A` e `B` |
| Inicialização | PiSSA, OLoRA | Convergência mais rápida; abre mão da inicialização em zero |
| Inicialização | LoftQ | Treinar contra um base quantizado |
| Estrutura | DoRA | Rank fixado em valor baixo por outro motivo |
| Estrutura | AdaLoRA | As camadas precisam de ranks desiguais |
| Estrutura | VeRA | O tamanho do adapter é a restrição que manda |

**Baseline a superar:** all-linear, rank adequado, learning rate ajustado. A maioria das variantes não o supera por mais do que o ruído de seed.

## Base quantizado (QLoRA)

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",             # not "fp4"
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # do not leave at default
)
```

Depois `prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)`. Pulá-lo gera execuções instáveis ou erros de gradiente opacos.

Todos os outros hiperparâmetros ficam inalterados. **O QLoRA é o LoRA com um base mais barato.**

Faça o merge no base de **precisão total**, nunca no quantizado.

## Diagnóstico pela curva

| Treino | Held-out | Diagnóstico | Ação |
|---|---|---|---|
| ↓ | ↓ | Aprendendo | Continue |
| ↓ | ↑ depois de uma queda | Overfitting | Entregue o mínimo; menos capacidade ou mais dados |
| → alto | → alto | Underfitting | Mais rank, mais targets, LR maior |
| Plana desde o passo 1 | Plana | Quebrado | Confira se o adapter foi acoplado e se os labels não são todos `-100` |
| `NaN` | também `NaN` | Overflow | LR menor; adicione warm-up; prefira bf16 |

## Relacionado

- [Lição 9](../lessons/0009-rank-alpha-and-initialisation.md), [Lição 10](../lessons/0010-choosing-target-modules.md), [Lição 19](../lessons/0019-when-dora-wins.md), [Lição 20](../lessons/0020-judging-a-new-variant.md)
