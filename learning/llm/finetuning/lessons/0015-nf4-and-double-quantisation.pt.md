---
title: "15. NF4 e dupla quantização"
description: "As duas ideias que o QLoRA de fato contribuiu"
type: lesson
---

# Lição 15. NF4 e dupla quantização

**Ligação com a missão:** Estas são as duas ideias que o QLoRA contribuiu. Conhecê-las separa entender o artigo de ter lido o abstract.
**Fonte principal:** [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Pré-requisitos:** [Lição 14](0014-quantisation-from-first-principles.md)

## Aquecimento

1. ▢ Por que quantização por bloco, e não por tensor?

<details markdown="1"><summary>Verificação</summary>

Um outlier só define a escala dentro do seu próprio bloco, contendo o dano a 64 ou 128 valores em vez do tensor inteiro.

</details>

2. ▢ Bytes por parâmetro reais para pesos de 4 bits com escalas fp32 em bloco de 64?

<details markdown="1"><summary>Verificação</summary>

0.5625, ou seja, 4.5 bits, com 0.5 bit de puro overhead de contabilidade.

</details>

3. ▢ Em que precisão é feito o matmul, para um base de 4 bits?

<details markdown="1"><summary>Verificação</summary>

Em uma mais alta, tipicamente bf16. Os blocos são desquantizados na hora e as cópias desquantizadas são descartadas.

</details>

## Saiba isto

O QLoRA contribuiu com três coisas: NF4, dupla quantização e paged optimizers. As duas primeiras são ideias sobre representação e são as interessantes. A terceira é uma mitigação de engenharia, coberta na Lição 16.

### NF4, ou NormalFloat

Com 4 bits você tem 16 níveis. Onde colocá-los?

O espaçamento uniforme, como no int4 simples, os coloca em intervalos iguais ao longo da faixa. Isso é ótimo se os valores são distribuídos de forma uniforme. **Os pesos de redes neurais não são distribuídos de forma uniforme.** Eles são aproximadamente centrados em zero e normalmente distribuídos, então a maioria dos valores se agrupa perto de zero e poucos estão perto dos extremos.

Níveis uniformes portanto desperdiçam resolução: muitos níveis ficam nas caudas, onde quase nenhum peso mora, enquanto a região densa perto de zero recebe poucos.

A resposta do NF4: coloque os 16 níveis nos **quantis de uma distribuição normal padrão**, de modo que cada nível cubra a mesma quantidade de *massa de probabilidade* em vez da mesma quantidade de faixa. Os níveis são densos perto de zero e esparsos nas caudas, combinando com onde os pesos de fato estão. O artigo descreve isso como ótimo do ponto de vista da teoria da informação para dados de média zero normalmente distribuídos.

Para isso funcionar, cada bloco precisa primeiro ser normalizado para `[−1, 1]` dividindo pelo seu absmax, que é exatamente o que a quantização por bloco já armazenava. Então o NF4 não é maquinário extra; é uma escolha melhor dos 16 níveis dentro do esquema da Lição 14.

```text
int4:  levels evenly spaced        → resolution wasted in empty tails
nf4:   levels at normal quantiles  → resolution where the weights are
```

A consequência é que o NF4 vence o int4 na mesma largura de bits, de graça. Nenhum armazenamento extra, só um codebook melhor.

Dois limites honestos:

- O ganho depende de os pesos estarem de fato próximos do normal. Costumam estar, por bloco, depois do pré-treinamento. É uma propriedade empírica, não uma garantia.
- O NF4 é um formato de *pesos*. Não é a ferramenta certa para ativações, que têm distribuições diferentes e menos bem-comportadas.

### Dupla quantização

Volte ao overhead da Lição 14. Por parâmetro, em bloco de 64 com escalas fp32:

```text
weights            0.5     bytes
scales   4/64  =   0.0625  bytes
                  ────────
                   0.5625  bytes  (4.5 bits)
```

Essas escalas são elas mesmas apenas números em um tensor, e há muitas delas. Então quantize-as também.

A dupla quantização pega as escalas de bloco em fp32, agrupa-as (o artigo usa blocos de 256) e as armazena em 8 bits com a sua própria escala de segundo nível. O resultado:

```text
first-level scales at 8 bits:   1/64      = 0.015625 bytes/param
second-level scales:            4/(64·256) ≈ 0.000244 bytes/param
weights:                                     0.5      bytes/param
                                            ──────────
                                             0.5159   bytes/param  (~4.13 bits)
```

O artigo relata a economia como aproximadamente **0.37 bit por parâmetro** em média, o que para um modelo de 65B é cerca de 3 GB. É uma quantidade real de memória recuperada de pura contabilidade.

![Três barras de bits por parâmetro. O segmento do peso de quatro bits é idêntico nas três. Sozinho são 4 bits; com escalas de bloco em fp32 um segmento de meio bit é adicionado, chegando a 4.5; com dupla quantização esse segmento encolhe para cerca de um oitavo de bit, chegando a cerca de 4.13.](images/the-tax-not-the-payload.svg)

Note o formato da ideia: as constantes de quantização eram um imposto fixo sobre o esquema, e a dupla quantização reduziu o imposto, e não a carga útil.

As barras dizem a mesma coisa sem a aritmética. O segmento cinza tem o mesmo comprimento três vezes, porque nada nos pesos mudou; toda diferença entre 4, 4.5 e 4.13 bits é a pequena peça em destaque na ponta. Um esquema que tivesse reduzido a carga útil em vez disso teria movido o cinza. É uma vitória pequena, esperta e inteiramente mecânica, e é por isso que o QLoRA de 4 bits fica perto de 4.1 bits por parâmetro na prática, e não 4.5.

### O resultado de memória

Recalcule o exemplo da Lição 6 com um base de 4 bits. Um modelo de 7B com um adapter de 20M de parâmetros:

| | Base em bf16 | Base em 4 bits |
|---|---|---|
| Pesos congelados do base | 14.0 GB | ~3.6 GB |
| Estado do adapter (16 B/parâmetro) | 0.32 GB | 0.32 GB |
| **Subtotal** | **14.3 GB** | **3.9 GB** |

Contra 112 GB do full fine-tuning, o custo fixo da execução com adapter de 4 bits fica abaixo de 4 GB. As ativações (Lição 7) agora são decisivamente o termo dominante, o que significa que o gradient checkpointing importa mais aqui do que em qualquer outro lugar do workspace.

Esse é o resultado que tornou o QLoRA significativo: ele levou o fine-tuning de modelos grandes de clusters para dispositivos únicos.

### A configuração

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",            # not "fp4"
    use_double_quant: true,       # the 0.37 bits/param saving
    compute_dtype: "bfloat16",    # storage is 4-bit; compute is not
}
```

Quatro configurações, cada uma correspondendo a algo desta lição. O `bnb_4bit_compute_dtype` é o que as pessoas deixam no valor padrão e não deveriam: é a precisão em que os blocos desquantizados são multiplicados, e deixá-lo em fp32 descarta boa parte do benefício de velocidade.

Como sempre, confirme esses nomes na documentação da versão instalada.

## Prática

1. ▢ Por que o NF4 vence o int4 na mesma largura de bits?

<details markdown="1"><summary>Verificação</summary>

Ele coloca os seus 16 níveis nos quantis de uma distribuição normal em vez de em intervalos uniformes, então a resolução se concentra onde os pesos de fato se agrupam, perto de zero, em vez de ser gasta em caudas vazias.

Mesmo armazenamento, codebook melhor. A precondição é normalizar cada bloco para `[−1, 1]` primeiro, o que a quantização por bloco já faz.

</details>

2. ▢ O que exatamente a dupla quantização comprime, e aproximadamente quanto ela economiza?

<details markdown="1"><summary>Verificação</summary>

As escalas de bloco de primeiro nível, ou seja, as constantes de quantização, e não os pesos. Elas são armazenadas em 8 bits em grupos de 256, com uma pequena escala de segundo nível.

O artigo relata cerca de 0.37 bit por parâmetro em média, aproximadamente 3 GB para um modelo de 65B. Ela leva o 4-bit-com-overhead de cerca de 4.5 bits para cerca de 4.1.

</details>

3. ▢ Calcule a memória fixa total para um base de 13B em NF4 com dupla quantização, mais um adapter de 30M.

<details markdown="1"><summary>Verificação</summary>

Base: 13e9 × 0.5159 ≈ 6.7 GB. Adapter: 3e7 × 16 = 0.48 GB. Cerca de 7.2 GB fixos.

Compare com 26 GB de um base em bf16 mais o adapter, e 208 GB do full fine-tuning. As ativações então se somam por cima dos 7.2 GB.

</details>

4. ▢ Qual componente do QLoRA economiza mais memória?

    - a) NF4 em vez da quantização int4 uniforme simples
    - b) Armazenar o base congelado em 4 bits em vez de bf16
    - c) Dupla quantização das escalas de bloco de primeiro nível
    - d) Paged optimizers despejando estado durante picos de memória

<details markdown="1"><summary>Verificação</summary>

**b)** Armazenar o base congelado em 4 bits em vez de bf16, uma redução de 4× no maior termo fixo.

O NF4 melhora a qualidade com armazenamento idêntico. A dupla quantização economiza cerca de 0.37 bit por parâmetro. Os paged optimizers evitam falhas nos picos em vez de reduzir o uso em regime estável.

</details>

5. ▢ Por que o NF4 é inadequado para quantizar ativações?

<details markdown="1"><summary>Verificação</summary>

A colocação dos seus níveis deriva de uma suposição de que os valores têm média zero e são aproximadamente normais. Os pesos pós-pré-treinamento se encaixam razoavelmente nisso; as ativações não, porque carregam features outlier sistemáticas de grande magnitude, então os quantis normais são o codebook errado para elas.

</details>

6. ▢ Você define `load_in_4bit=True` e deixa `bnb_4bit_compute_dtype` no padrão. O que você provavelmente abriu mão?

<details markdown="1"><summary>Verificação</summary>

De velocidade. O armazenamento continua em 4 bits e a memória continua economizada, mas se o compute dtype padrão for fp32, cada bloco desquantizado é multiplicado em precisão total, perdendo boa parte da vantagem de throughput.

Defina-o como bf16 de propósito. Precisão de armazenamento e precisão de cálculo são decisões separadas.

</details>

## Prática no mundo real

- [ ] Calcule no papel os bytes por parâmetro de 4 bits com e sem dupla quantização, em bloco de 64. Confirme que a diferença fica perto de 0.37 bit.
- [ ] Carregue o mesmo modelo em bf16 e em NF4, medindo a memória nas duas vezes. Compare com a sua previsão.
- [ ] Amanhã: gere o mesmo prompt nos dois, de forma gulosa, e leia as saídas lado a lado. Forme uma primeira impressão do custo em qualidade; a Lição 17 transforma isso em medição.

## Para ir além

- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): as seções 3 e 4 são esta lição
- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Orçamento de memória](../reference/memory-budget.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
