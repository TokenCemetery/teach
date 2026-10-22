---
title: "5. Contando parâmetros e bytes"
description: "Transformar a configuração de um modelo em gigabytes"
type: lesson
---

# Lição 5. Contando parâmetros e bytes

**Ligação com a missão:** "Explicar cada byte" está na missão. Esta é a lição em que você aprende a fazer a aritmética em vez de chutar.
**Fonte principal:** [Docs: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
**Pré-requisitos:** [Lição 2](0002-where-the-weights-live.md), [Lição 4](0004-what-training-changes.md)

## Aquecimento

1. ▢ Quais são as quatro operações em um passo de treinamento?

<details markdown="1"><summary>Verificação</summary>

Forward pass (mantendo as ativações), loss, backward pass (produzindo os gradientes), passo do otimizador.

</details>

2. ▢ O que `-100` significa em um tensor de labels?

<details markdown="1"><summary>Verificação</summary>

Ignore esta posição ao calcular a loss. É assim que os tokens do prompt são mascarados na loss apenas da completion.

</details>

3. ▢ Quais projeções de atenção encolhem na grouped-query attention?

<details markdown="1"><summary>Verificação</summary>

`k_proj` e `v_proj`. `q_proj` e `o_proj` mantêm a dimensão oculta completa.

</details>

## Saiba isto

Um parâmetro é um número. A memória é o tamanho de armazenamento desse número vezes quantos deles você tem. Todo o resto da etapa 2 é contabilidade em cima disto.

### Formatos numéricos

| Formato | Bytes | Observações |
|---|---|---|
| `float32` (fp32) | 4 | Precisão total. O padrão histórico para treinamento. |
| `bfloat16` (bf16) | 2 | Mesma faixa de expoente do fp32, menos bits de mantissa. O padrão moderno. |
| `float16` (fp16) | 2 | Mais mantissa, faixa muito menor, então estoura para infinito com mais facilidade. |
| `int8` | 1 | Inteiro, precisa de um fator de escala para ser interpretado. |
| 4 bits (`nf4`, `int4`) | 0.5 | Dois valores por byte, mais escalas por bloco. Etapa 4. |

O bf16 é preferido ao fp16 para treinamento apesar de armazenar menos precisão, porque sua faixa de expoente coincide com a do fp32. O overflow é uma falha mais difícil de recuperar do que o erro de arredondamento, e o treinamento em fp16 historicamente precisava de loss scaling para evitá-lo.

### Os dois números que descrevem um modelo

Digamos que o model card afirme 1.5B de parâmetros. Então:

```text
weights in fp32 = 1.5e9 × 4 bytes = 6.0 GB
weights in bf16 = 1.5e9 × 2 bytes = 3.0 GB
weights in nf4  = 1.5e9 × 0.5     = 0.75 GB, plus quantisation constants
```

Isto é só a memória dos pesos para inferência: o piso para ter o modelo na memória, antes de qualquer ativação, qualquer KV cache, e certamente antes do treinamento.

Um reflexo útil: **gigabytes em bf16 ≈ o dobro da contagem de parâmetros em bilhões.** Um modelo de 7B tem cerca de 14 GB de pesos. Um de 70B tem cerca de 140 GB. Você deve conseguir produzir esses números na hora.

### Onde estão os parâmetros

Da Lição 2, por camada:

```text
attention = 2 × d² + 2 × d × d_kv          (q, o full; k, v narrowed by GQA)
mlp       = 3 × d × d_ff                    (gate, up, down)
```

e no modelo inteiro:

```text
total ≈ n_layers × (attention + mlp) + vocab × d × (1 or 2)
```

O termo final é dobrado quando a projeção de saída não é compartilhada com o embedding de entrada. Para modelos pequenos esse termo não é desprezível: um vocabulário de 32k com tamanho oculto 2048 dá 65M de parâmetros por cópia, o que é uma fração real de um modelo de 1.5B.

### Exemplo resolvido

Um modelo com `d = 2048`, `d_kv = 256`, `d_ff = 5632`, 24 camadas, vocabulário de 32k, embeddings compartilhados:

```text
attention = 2 × 2048² + 2 × 2048 × 256  = 8.39M + 1.05M = 9.44M
mlp       = 3 × 2048 × 5632             = 34.6M
per layer                               = 44.0M
× 24 layers                             = 1.056B
embeddings = 32000 × 2048               = 0.066B
total                                   ≈ 1.12B
```

Em bf16 são cerca de 2.2 GB de pesos. Observe que a MLP é 79% do bloco; leve isso adiante para a Lição 10.

![Duas barras de proporção. Uma camada de 44.0M é cerca de 21 por cento atenção e 79 por cento MLP. O modelo inteiro de 1.12B é cerca de 94 por cento camadas empilhadas e 5.9 por cento embeddings.](images/where-the-parameters-are.svg)

As mesmas contas como proporções, nos dois níveis que importam. Dentro de um bloco, a atenção é a metade menor por uma margem larga, e é por isso que a questão dos target modules na Lição 10 é, em grande parte, uma questão sobre a MLP. No modelo inteiro, o termo dos embeddings é pequeno aqui e cresce como proporção à medida que o modelo encolhe, que é o caso contra o qual o parágrafo acima alerta.

### O que isto ainda não inclui

Agora você tem o custo dos pesos. O treinamento adiciona mais três categorias, e elas dominam:

- Gradientes, um por parâmetro treinável (Lição 6)
- Estado do otimizador, dois por parâmetro treinável (Lição 6)
- Ativações, que dependem do batch size e do comprimento da sequência, e não da contagem de parâmetros (Lição 7)

Quem diz que um modelo de 7B "precisa de 14 GB para fazer fine-tuning" contou só a primeira categoria. Esse é o erro que esta etapa existe para eliminar.

## Prática

1. ▢ Quantos gigabytes têm os pesos de um modelo de 13B em bf16? Em fp32? Em 4 bits?

<details markdown="1"><summary>Verificação</summary>

bf16: 26 GB. fp32: 52 GB. 4 bits: cerca de 6.5 GB, mais as constantes de quantização.

Vale saber fazer sem calculadora a cadeia de dobrar e dividir pela metade a partir da contagem de parâmetros.

</details>

2. ▢ Por que o bf16 é preferido ao fp16 para treinamento, dado que o fp16 armazena mais bits de mantissa?

<details markdown="1"><summary>Verificação</summary>

O bf16 mantém a faixa de expoente do fp32, então os valores não estouram para infinito. A faixa estreita do fp16 significa que os gradientes podem sofrer overflow ou underflow, o que historicamente exigia loss scaling para funcionar.

O erro de arredondamento se degrada com elegância; o overflow produz `NaN` e encerra a execução. A troca favorece a faixa.

</details>

3. ▢ Um modelo tem `d = 4096`, `d_ff = 14336`, `d_kv = 1024`, 32 camadas. Calcule os parâmetros por camada e o total do modelo, ignorando os embeddings.

<details markdown="1"><summary>Verificação</summary>

Atenção: 2 × 4096² + 2 × 4096 × 1024 = 33.6M + 8.4M = 42.0M.
MLP: 3 × 4096 × 14336 = 176.2M.
Por camada: 218.2M. Vezes 32 camadas ≈ 6.98B.

Aproximadamente um modelo de 7B, e a MLP é 81% dele.

</details>

4. ▢ Dois modelos reportam 7B de parâmetros. Um tem vocabulário de 32k, o outro de 256k. O que difere, e em quanto?

<details markdown="1"><summary>Verificação</summary>

O custo dos embeddings. Com tamanho oculto 4096, um vocabulário de 32k dá 131M de parâmetros por cópia; um de 256k dá 1.05B, cerca de 15% do modelo inteiro em uma única tabela, e o dobro disso se a projeção de saída não for compartilhada.

O modelo de vocabulário grande tem, portanto, bem menos parâmetros nos seus blocos transformer, que é onde os adapters se acoplam.

</details>

5. ▢ Alguém diz que um modelo de 7B cabe com folga em 16 GB para fine-tuning, porque os pesos em bf16 são 14 GB. O que há de errado no raciocínio?

<details markdown="1"><summary>Verificação</summary>

Eles contaram só os pesos. O full fine-tuning também precisa de gradientes e dois momentos do otimizador por parâmetro treinável, além das ativações, o que é várias vezes o custo dos pesos. Mesmo a afirmação dos 14 GB deixa só 2 GB para todo o resto.

A próxima lição transforma isso em um número exato, e a resposta não chega nem perto.

</details>

## Prática no mundo real

- [ ] Escolha três modelos de tamanhos diferentes. Só a partir dos arquivos de configuração (`hidden_size`, `intermediate_size`, `num_hidden_layers`, `num_key_value_heads`, `vocab_size`), calcule as contagens de parâmetros e confira com os model cards.
- [ ] Carregue um modelo em bf16 e meça a memória realmente usada. Compare com a sua previsão e explique qualquer diferença.
- [ ] Amanhã: faça de cabeça a estimativa de gigabytes em bf16 para cinco tamanhos de modelo e depois verifique com uma calculadora.

## Para ir além

- [Docs: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
- [Orçamento de memória](../reference/memory-budget.md): a tabela para a qual esta lição caminha
- [Lição 6. Gradientes e estado do otimizador](0006-gradients-and-optimizer-state.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
