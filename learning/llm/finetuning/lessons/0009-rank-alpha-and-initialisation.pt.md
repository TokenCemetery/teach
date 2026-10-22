---
title: "9. Rank, alpha e inicialização"
description: "Só `α/r` importa, e por que `B` começa em zero"
type: lesson
---

# Lição 9. Rank, alpha e inicialização

**Ligação com a missão:** A missão pede que você justifique cada hiperparâmetro a partir da tarefa. Estes três são onde a maioria das pessoas repete folclore em vez disso.
**Fonte principal:** [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Pré-requisitos:** [Lição 8](0008-the-low-rank-idea.md)

## Aquecimento

1. ▢ Escreva a equação do forward do LoRA.

<details markdown="1"><summary>Verificação</summary>

`h = W₀x + (α/r) · BAx`, com `W₀` congelada e só `A` e `B` treináveis.

</details>

2. ▢ Contagem de parâmetros do adapter para uma camada alvo?

<details markdown="1"><summary>Verificação</summary>

`r × (d_in + d_out)`. Dominada pela maior dimensão.

</details>

3. ▢ Por que um adapter com merge não custa nada na inferência?

<details markdown="1"><summary>Verificação</summary>

A atualização é aditiva e linear, então ela é incorporada ao peso base e deixa para trás uma matriz comum.

</details>

## Saiba isto

### Inicialização, e por que ela não é arbitrária

`A` é inicializada de forma aleatória, gaussiana ou Kaiming-uniform. `B` é inicializada em **exatamente zero**.

Portanto `BA = 0` no passo zero, então `ΔW = 0`, então **o modelo adaptado é, bit a bit, o base model antes da primeira atualização.** Essa é uma propriedade deliberada e importante:

- O treinamento começa de um modelo sabidamente bom, e não de um perturbado.
- Não há choque inicial no comportamento pré-treinado, então não há dano precoce a desfazer.
- Qualquer degradação que você observe é algo que o treinamento fez, e não algo que a inicialização fez.

![B desenhada como uma grade de zeros, A como uma grade de valores variados, e o produto das duas como uma grade de zeros, com as duas inicializações rejeitadas nomeadas embaixo.](images/zero-whatever-a-holds.svg)

As entradas de `A` estão visíveis e nenhuma delas importa: cada uma é multiplicada por um zero a caminho do produto.

A assimetria é necessária. Se as duas fossem zero, o gradiente das duas seria zero e nada jamais aprenderia: o produto precisa de um fator diferente de zero para carregar sinal. Se as duas fossem aleatórias, `ΔW` começaria como ruído estruturado injetado em toda camada alvo.

É também por isso que o LoRA tolera learning rates muito mais altos do que o full fine-tuning. Você não está empurrando pesos que já codificam tudo o que o modelo sabe; está fazendo crescer um termo a partir de zero.

### Alpha e o fator de escala

`α` (`lora_alpha`) é um escalar fixo. A atualização é escalada por `α/r`.

O objetivo de dividir por `r` era tornar a magnitude efetiva da atualização aproximadamente independente do rank, para que mudar o rank não obrigasse você a reajustar o learning rate. **O que importa é a razão `α/r`, e não qualquer um dos dois números sozinho.**

| `r` | `α` | `α/r` | Efeito |
|---|---|---|---|
| 8 | 16 | 2.0 | Baseline comum |
| 16 | 32 | 2.0 | Mais capacidade, mesma escala de atualização |
| 16 | 16 | 1.0 | Mais capacidade, atualização mais fraca |
| 64 | 16 | 0.25 | Muito mais capacidade, fortemente amortecida |

Aquela última linha é uma armadilha que vale nomear: aumentar o rank deixando `α` fixo *reduz* a escala da atualização. As pessoas aumentam o rank esperando mais poder expressivo, esquecem do `α` e concluem que um rank maior prejudica. Não prejudicou; elas baixaram o adapter em 8× sem perceber.

O ponto de partida convencional é `α = 2r`. Trate-o como uma convenção com uma justificativa, e não como uma descoberta.

O **rsLoRA** ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) argumenta que o divisor `α/r` amortece demais em rank alto e propõe `α/√r` no lugar, o que mantém o aprendizado estável conforme o rank cresce. Se você pretende trabalhar com rank 64 ou mais, esta é a configuração a conhecer:

```python
LoraConfig(r=64, lora_alpha=16, use_rslora=True, ...)
```

### Escolhendo o rank

O rank é **capacidade**. Ele limita quão complexa pode ser a atualização que o adapter consegue expressar.

| Rank | Razoável para |
|---|---|
| 4 a 8 | Estilo, tom, formato de saída; datasets pequenos |
| 16 a 32 | Uma tarefa genuína com alguns milhares de exemplos |
| 64 a 128 | Tarefas mais difíceis, datasets maiores, comportamento que exige muito raciocínio |
| 256+ | Aproximando-se da capacidade do full fine-tuning em datasets grandes de SFT |

Dois diagnósticos que vencem o chute:

**Underfitting.** A loss de treinamento estaciona acima de onde você precisa e mais epochs não ajudam. Capacidade insuficiente: aumente o rank ou adicione target modules (normalmente a melhor jogada, segundo a Lição 10).

**Overfitting.** A loss de treinamento continua caindo enquanto a loss held-out sobe. Capacidade demais para os dados, ou epochs demais. Reduza o rank, adicione dropout, consiga mais dados ou pare mais cedo.

Note a assimetria com a lição de memória: o rank custa muito pouca memória (Lição 7), então o custo de um rank extra é o risco de overfitting e um pouco de computação, e não caber na memória. Isso inverte o instinto que muita gente traz da época em que a memória era a restrição que mandava.

### Dropout

O `lora_dropout` aplica dropout à entrada do adapter. Os valores típicos vão de 0.0 a 0.1. Recorra a ele quando a loss held-out estiver subindo e você não puder conseguir mais dados. Em datasets grandes ele costuma ser desnecessário e só desacelera a convergência.

### A configuração

```text
config := {
    rank: 16,
    alpha: 32,               # α/r = 2
    dropout: 0.05,
    adapt_bias: false,
    target_modules: [...],   # Lesson 10
}

model := attach_adapter(model, config)
print(model.trainable_parameter_count())
```

Essa última linha não é opcional. É a verificação de que os seus target modules casaram com alguma coisa, e deve concordar com a aritmética que você fez na Lição 8. Leia os nomes dos parâmetros na documentação da versão instalada em vez de confiar na memória, porque essa superfície muda entre releases.

## Prática

1. ▢ Por que `B` é inicializada em zero e `A` de forma aleatória, em vez de as duas em zero ou as duas aleatórias?

<details markdown="1"><summary>Verificação</summary>

Uma `B` zerada faz `ΔW = 0` no início, então o treinamento começa exatamente do base model, sem perturbação de que se recuperar. Uma `A` aleatória mantém o gradiente do produto diferente de zero, então o aprendizado pode começar.

As duas em zero: os gradientes somem, nada aprende. As duas aleatórias: o modelo começa como base mais ruído em toda camada alvo.

</details>

2. ▢ Você aumenta o rank de 8 para 64 e deixa `α` em 16. A loss mal se move. Diagnostique.

<details markdown="1"><summary>Verificação</summary>

A escala `α/r` caiu de 2.0 para 0.25. O adapter tem oito vezes a capacidade e um oitavo da influência, então o efeito líquido é uma atualização amortecida, e não mais forte.

Aumente `α` para 128 para preservar a razão, ou defina `use_rslora=True` para que o divisor passe a ser `√r`.

</details>

3. ▢ A loss de treinamento se achata em um nível alto demais para ser útil, e um quarto epoch não ajuda. O que é isso, e quais são as suas duas opções?

<details markdown="1"><summary>Verificação</summary>

Underfitting: o adapter não tem capacidade para expressar a atualização necessária.

Aumente o rank, ou estenda os target modules para cobrir mais do modelo. Adicionar target modules costuma ser a melhor primeira jogada, porque a MLP guarda a maior parte dos parâmetros e muitas vezes é onde está a capacidade que falta. Mais epochs não resolvem um teto de capacidade.

</details>

4. ▢ Qual combinação dá a maior escala de atualização?

    - a) `r = 8` com `alpha = 8`
    - b) `r = 8` com `alpha = 32`
    - c) `r = 32` com `alpha = 32`
    - d) `r = 64` com `alpha = 64`

<details markdown="1"><summary>Verificação</summary>

**b)** `r = 8` com `alpha = 32`, dando `α/r = 4`.

As outras são todas `α/r = 1`. A capacidade difere entre elas, mas a escala da atualização não, que é exatamente a distinção que o design de `α/r` pretendia fazer.

</details>

5. ▢ Por que o LoRA pode usar um learning rate de dez a cem vezes maior do que o full fine-tuning?

<details markdown="1"><summary>Verificação</summary>

Os parâmetros treináveis começam com contribuição zero e não são eles mesmos o repositório do conhecimento pré-treinado. Não há estrutura acumulada a danificar, e o termo precisa crescer a partir do nada, então precisa de um passo muito maior para se mover de forma significativa em um número razoável de passos.

</details>

6. ▢ Quando você *não* aumentaria o rank mesmo com o adapter em underfitting?

<details markdown="1"><summary>Verificação</summary>

Quando o dataset é pequeno. Capacidade extra em poucos exemplos compra memorização, e não generalização: a loss de treinamento cai, a loss held-out sobe.

A resposta certa ali é mais dados ou dados melhores, ou uma tarefa mais estreita, e não um adapter maior.

</details>

## Prática no mundo real

- [ ] Monte três configurações, `(8, 16)`, `(16, 32)` e `(64, 16)`, e anote o `α/r` de cada uma e o que você prevê que vai acontecer. Guarde as previsões.
- [ ] Imprima `print_trainable_parameters()` para cada uma e concilie com a sua aritmética da Lição 8.
- [ ] Amanhã: encontre uma configuração publicada de fine-tuning por aí, calcule o seu `α/r` e decida se o autor o escolheu ou o herdou.

## Para ir além

- [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Artigo científico: "A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA", Kalajdzievski, arXiv:2312.03732](https://arxiv.org/abs/2312.03732)
- [Artigo: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
- [Hiperparâmetros do LoRA](../reference/lora-hyperparameters.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
