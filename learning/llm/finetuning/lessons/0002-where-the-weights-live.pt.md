---
title: "2. Onde os pesos ficam"
description: "Nomear cada projeção a que um adapter poderia se acoplar"
type: lesson
---

# Lição 2. Onde os pesos ficam

**Ligação com a missão:** Um adapter se acopla a matrizes de pesos específicas. Você não consegue escolher quais até conseguir nomeá-las e dizer o que cada uma faz.
**Fonte principal:** [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
**Pré-requisitos:** [Lição 1](0001-what-a-base-model-is.md)

## Aquecimento

1. ▢ O que um modelo de linguagem calcula, enunciado como uma função?

<details markdown="1"><summary>Verificação</summary>

Sequência de tokens entra, uma pontuação para cada token do vocabulário sai. A geração é um loop em volta dessa função, não parte dela.

</details>

2. ▢ Por que um base model falha em seguir uma instrução?

<details markdown="1"><summary>Verificação</summary>

Seguir instruções é um comportamento treinado, adicionado por cima da previsão de próximo token. Um base model só tem o objetivo de próximo token, então ele continua o texto em vez de obedecer.

</details>

## Saiba isto

Quase todo parâmetro de um modelo moderno só com decoder mora em um de três lugares: a tabela de embeddings, uma pilha de blocos transformer idênticos e a projeção de saída. Os blocos guardam a esmagadora maioria, e é neles que os adapters se acoplam.

### Dentro de um bloco

Cada bloco tem duas subcamadas, cada uma precedida por uma normalização e envolvida por uma conexão residual.

**Atenção.** Quatro projeções lineares, nomeadas por convenção a partir do que produzem:

| Nome | Papel |
|---|---|
| `q_proj` | Queries, o que esta posição está procurando |
| `k_proj` | Keys, o que cada posição oferece como correspondência |
| `v_proj` | Values, o conteúdo de fato recuperado |
| `o_proj` | Mistura o resultado da atenção de volta no fluxo residual |

**MLP** (também chamada de rede feed-forward). Nos modelos atuais costuma ter três projeções em vez de duas, por causa das ativações com gate:

| Nome | Papel |
|---|---|
| `gate_proj` | Produz o gate, passado por uma ativação |
| `up_proj` | Projeta para cima, até a dimensão intermediária mais larga |
| `down_proj` | Projeta de volta para baixo, até a dimensão oculta |

A MLP é mais larga do que a dimensão oculta, em geral de 2.5× a 4×, então, apesar de ter menos matrizes do que se poderia esperar, **a MLP guarda mais parâmetros do que a atenção.** Esse fato dirige a escolha dos target modules na Lição 10.

### Contando

Uma camada linear com dimensão de entrada `d_in` e dimensão de saída `d_out` guarda `d_in × d_out` pesos. Para um modelo com tamanho oculto 2048, 24 camadas e tamanho intermediário 5632:

- Atenção por camada, ignorando a grouped-query attention: 4 × 2048 × 2048 ≈ 16.8M
- MLP por camada: 3 × 2048 × 5632 ≈ 34.6M
- Total por camada ≈ 51.4M, vezes 24 camadas ≈ 1.23B
- Embeddings, com um vocabulário de 32k: 32000 × 2048 ≈ 65.5M, dobrado se a projeção de saída não for compartilhada

Isso explica essencialmente o modelo inteiro. Não existe nenhum reservatório escondido de parâmetros em outro lugar.

### Uma armadilha que vale conhecer agora

A maioria dos modelos atuais usa **grouped-query attention**, em que várias cabeças de query compartilham um mesmo conjunto de keys e values. Isso torna `k_proj` e `v_proj` *mais estreitas* do que `q_proj` e `o_proj`, muitas vezes por um fator de quatro ou oito. Qualquer cálculo que presuma que as quatro projeções de atenção são quadradas vai superestimar, e qualquer suposição de que elas têm o mesmo tamanho vai produzir uma contagem errada de parâmetros do adapter na Lição 8.

### Encontrando os nomes reais

Nunca confie em uma lista de nomes de módulos lembrada de cabeça. Eles são definidos pela implementação do modelo e diferem entre arquiteturas. Imprima-os:

```text
model := load_model("<some-small-model>")
for name, module in model.modules():
    if module is a linear layer:
        print(name, module.weight.shape)
```

Este é o diagnóstico mais útil de todo o workspace. Um fine-tune que treina nada em silêncio costuma significar um nome de target module que não casou com nada.

## Prática

1. ▢ Nomeie as sete projeções lineares de um bloco transformer moderno típico.

<details markdown="1"><summary>Verificação</summary>

`q_proj`, `k_proj`, `v_proj`, `o_proj` na atenção; `gate_proj`, `up_proj`, `down_proj` na MLP.

Arquiteturas mais antigas ou sem gate têm só duas projeções na MLP. É por isso que você imprime os nomes em vez de recitá-los.

</details>

2. ▢ Para um modelo com tamanho oculto 4096 e tamanho intermediário 11008, o que guarda mais parâmetros por camada, a atenção ou a MLP? Aproximadamente por qual fator?

<details markdown="1"><summary>Verificação</summary>

A MLP, por aproximadamente dois para um. A atenção (projeções quadradas) tem 4 × 4096² ≈ 67M. A MLP tem 3 × 4096 × 11008 ≈ 135M.

Com a grouped-query attention a diferença se alarga ainda mais, porque `k_proj` e `v_proj` encolhem enquanto a MLP não.

</details>

3. ▢ Você configura o seu adapter para ter como alvo `["query", "value"]` em um modelo cujos módulos se chamam `q_proj` e `v_proj`. O que acontece?

<details markdown="1"><summary>Verificação</summary>

Nada casa, então ou a biblioteca lança um erro ou, pior, dependendo da versão, você fica com um modelo sem nenhum peso de adapter treinável. O treinamento então roda, a loss mal se move e a execução parece apenas decepcionante, e não quebrada.

Confira a contagem de parâmetros treináveis logo depois de construir o adapter. A Lição 11 transforma isso em hábito.

</details>

4. ▢ Por que conhecer a estrutura do fluxo residual importa para adapters?

<details markdown="1"><summary>Verificação</summary>

Porque um adapter modifica a saída de uma projeção, e a conexão residual faz com que essa mudança seja somada a um fluxo em andamento em vez de substituí-lo. Uma pequena contribuição do adapter pode direcionar o fluxo sem destruir o que as camadas congeladas já escreveram nele, e é por isso que iniciar um adapter exatamente em zero (Lição 9) é seguro.

</details>

5. ▢ Grouped-query attention: suas anotações presumem que as quatro projeções de atenção são 2048 × 2048, mas o modelo tem 32 cabeças de query e 4 cabeças de key-value com dimensão de cabeça 64. Quais são os formatos verdadeiros?

<details markdown="1"><summary>Verificação</summary>

`q_proj` e `o_proj` continuam 2048 × 2048 (32 × 64 = 2048). `k_proj` e `v_proj` são 2048 × 256 (4 × 64 = 256).

Assim, a atenção guarda cerca de 2 × 2048² + 2 × 2048 × 256 ≈ 9.4M por camada, e não 16.8M. Quase metade da sua estimativa.

</details>

## Prática no mundo real

- [ ] Execute o loop de listagem de módulos acima, usando a chamada real de inspeção de modelo da sua biblioteca (por exemplo, `named_modules()` no PyTorch), no menor modelo que você conseguir baixar. Escreva à mão, nas suas próprias anotações, os sete nomes e seus formatos.
- [ ] Só a partir dos formatos, calcule a contagem total de parâmetros do modelo. Compare com o número do seu model card e explique qualquer diferença.
- [ ] Amanhã: repita para um modelo de outra família. Anote todo nome de módulo que for diferente.

## Para ir além

- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): as contagens de parâmetros são mostradas por matriz
- [Artigo científico: "Attention Is All You Need", Vaswani et al., arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [Lição 10. Escolhendo os target modules](0010-choosing-target-modules.md) é onde isto dá resultado

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
