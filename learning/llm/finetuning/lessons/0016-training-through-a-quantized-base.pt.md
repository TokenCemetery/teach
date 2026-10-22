---
title: "16. Treinando através de um base quantizado"
description: "Como os gradientes fluem por pesos de 4 bits congelados"
type: lesson
---

# Lição 16. Treinando através de um base quantizado

**Ligação com a missão:** O QLoRA na prática. Esta também é a única lição em que o hardware que você tem muda de verdade o que está disponível para você.
**Fonte principal:** [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
**Pré-requisitos:** [Lição 15](0015-nf4-and-double-quantisation.md), [Lição 11](0011-your-first-adapter.md)

## Aquecimento

1. ▢ O que o NF4 coloca nos quantis normais, e por quê?

<details markdown="1"><summary>Verificação</summary>

Os seus 16 níveis representáveis, de modo que cada um cubra a mesma massa de probabilidade em vez da mesma faixa, combinando com onde os pesos normalmente distribuídos de fato se agrupam.

</details>

2. ▢ O que a dupla quantização comprime?

<details markdown="1"><summary>Verificação</summary>

As escalas de bloco de primeiro nível, e não os pesos. Aproximadamente 0.37 bit por parâmetro.

</details>

3. ▢ Para um base de 4 bits com um adapter, qual termo de memória domina?

<details markdown="1"><summary>Verificação</summary>

As ativações. O base caiu para alguns gigabytes e o estado do adapter é uma fração de um, então o batch size e o comprimento da sequência agora decidem se a execução cabe.

</details>

## Saiba isto

### Como um gradiente chega ao adapter através de um base quantizado congelado

O aparente paradoxo: os pesos do base são inteiros de 4 bits, e você não consegue tirar um gradiente de forma significativa em relação a um inteiro de 4 bits. Então como o treinamento funciona?

Funciona porque **os pesos do base não estão sendo treinados.** Acompanhe uma camada adaptada:

```text
forward:   h = W₀_dequant(x) + (α/r) · B A x
```

`W₀` é desquantizada para bf16 para o matmul e a cópia desquantizada é descartada. O backward pass precisa do gradiente da loss em relação a `A` e `B`, e para calculá-lo precisa das *ativações* que fluem pela camada, que são bf16, e do gradiente que chega de cima, que também é bf16.

Os pesos congelados participam do backward pass apenas **repassando o gradiente** às camadas anteriores. Isso exige multiplicar por `W₀`, o que exige desquantizá-la de novo em vez de derivar em relação a ela. Nenhum gradiente é jamais armazenado para um peso do base, porque nenhum é solicitado.

![Uma camada adaptada desenhada duas vezes com as mesmas quatro caixas. No forward, a entrada chega ao base de 4 bits e ao adapter em bf16 e os dois se encontram na saída; no backward, o gradiente percorre as mesmas arestas no sentido inverso, mas só o adapter tem um gradiente armazenado para ele.](images/a-constant-in-the-graph.svg)

Os dois painéis têm as mesmas caixas nos mesmos lugares, e as arestas do backward são as do forward invertidas. O base aparece nos dois, trabalhando nos dois, e não guardando nada de nenhum.

Então não há nada de exótico aqui. O base quantizado é uma constante no grafo de computação. Ele precisa ser lido em alta precisão, mas nunca precisa ser atualizado, e atualizar é a parte cara.

O custo é computação: a desquantização acontece em todo forward e de novo no backward pass, a cada passo. O QLoRA troca velocidade por memória, e é visivelmente mais lento por passo do que um base em bf16.

### Preparando o modelo

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",
    use_double_quant: true,
    compute_dtype: "bfloat16",
}

model := load_model("<base model>", quantization: quant_config)
model := prepare_for_quantized_training(model, gradient_checkpointing: true)

adapter_config := {rank: 32, alpha: 64, target_modules: "all-linear"}
model := attach_adapter(model, adapter_config)
print(model.trainable_parameter_count())
```

O `prepare_model_for_kbit_training` faz várias pequenas coisas necessárias: converte as layer norms e a cabeça de saída para uma precisão estável, ativa o gradient checkpointing e os requisitos de gradiente de entrada, e garante que nada que precise ficar em precisão mais alta tenha sido quantizado. Pulá-lo produz execuções instáveis ou que falham com erros de gradiente, e a causa não é óbvia pela mensagem.

### Todo o resto permanece inalterado

Rank, alpha, target modules, learning rate, schedule, divisão held-out, sondas de geração, as quatro verificações da Lição 11: tudo idêntico. **O QLoRA é o LoRA com um base mais barato.** Não é um método diferente com o seu próprio folclore de hiperparâmetros, e tratá-lo como tal é uma fonte comum de confusão.

O único ajuste que vale mencionar: como o base é mais ruidoso, alguns profissionais usam um pouco mais de rank do que usariam com um base em bf16, na teoria de que o adapter precisa compensar o erro de quantização além de aprender a tarefa. Trate isso como uma hipótese a testar na sua tarefa, e não como uma regra.

### Backends: o que de fato é verdade

Isso merece cuidado, porque a versão amplamente repetida está desatualizada.

O `bitsandbytes` começou só com CUDA, e por vários anos "o QLoRA precisa de uma GPU NVIDIA" era simplesmente correto. A biblioteca desde então passou a uma arquitetura multi-backend, com despacho para **CUDA (que cobre também o AMD ROCm), CPU, Intel XPU, Intel Gaudi e Apple MPS**, junto com alternativas em PyTorch puro. As operações de 4 bits, quantizar, desquantizar e o produto matriz-vetor de 4 bits, têm implementações de backend além do CUDA, despachadas quando o tamanho de bloco é um que o kernel compilado suporta e com recurso a caminhos genéricos mais lentos caso contrário.

O que decorre disso para você:

- **O CUDA continua sendo o caminho mais completo e mais bem otimizado.** Se você o tem, use-o, e espere que os números publicados sejam reproduzíveis.
- **Os outros backends são viáveis e estão melhorando, com ressalvas.** A cobertura varia por operação, tamanho de bloco e versão da biblioteca. Espere passos mais lentos, e espere ter de conferir se uma configuração específica cai em um kernel otimizado ou em um fallback.
- **Os paged optimizers são a peça genuinamente específica do CUDA.** Eles dependem da memória unificada da NVIDIA para despejar o estado do otimizador na memória do host durante picos transitórios, evitando uma falha por falta de memória em um pico. Isso é um recurso de hardware, e não um algoritmo portável. Também importa menos no treinamento de adapters, em que o estado do otimizador é minúsculo; o propósito original era um estado na escala do full fine-tuning.
- **Verifique contra a sua versão instalada, e não contra qualquer documento.** Esta área mudou repetidamente e vai mudar de novo. O `bitsandbytes` também não é o único caminho para 4 bits; existem outros backends de quantização com cobertura de hardware diferente.

Os conceitos das Lições 14 e 15, que são escalas por bloco, níveis em quantis normais, quantizar as constantes e precisão de armazenamento versus precisão de cálculo, são aritmética e são idênticos em todo backend. Só a disponibilidade de kernels e a velocidade diferem.

### O que esperar da execução

| Em relação a um base em bf16 | Efeito |
|---|---|
| Memória fixa | Aproximadamente 4× menor para o base |
| Tempo por passo | Mais lento, desquantização em todo forward e backward |
| Formato da curva de loss | Muito parecido; pode ficar marginalmente mais alto |
| Qualidade final | Ligeiramente menor, depende da tarefa, então meça (Lição 17) |

E a regra de merge da Lição 13 continua valendo, mais importante do que nunca: **faça o merge no base de precisão total, e não no quantizado.** Treine contra 4 bits, depois carregue o base em bf16, aplique o adapter e faça o merge ali. Fazer o merge nos pesos quantizados soma uma perda de requantização que você não tem motivo para aceitar.

## Prática

1. ▢ Como os gradientes podem fluir quando os pesos do base são inteiros de 4 bits?

<details markdown="1"><summary>Verificação</summary>

Nenhum gradiente é jamais tirado em relação a um peso do base: eles são constantes congeladas. Os gradientes são tirados em relação a `A` e `B`, que têm alta precisão.

Os pesos congelados são necessários para *propagar* o gradiente às camadas anteriores, o que exige desquantizá-los para a multiplicação, e não derivá-los.

</details>

2. ▢ O que o `prepare_model_for_kbit_training` faz, e o que acontece se você o pular?

<details markdown="1"><summary>Verificação</summary>

Ele converte para uma precisão mais alta os módulos que precisam de estabilidade, como as layer norms e a cabeça de saída, ativa o gradient checkpointing e os gradientes de entrada, e garante que nada que deva ficar em alta precisão tenha sido quantizado.

Pulá-lo costuma dar uma execução instável ou um erro dizendo que os gradientes não são exigidos, com uma mensagem que não aponta a causa.

</details>

3. ▢ Qual é a parte do QLoRA específica do CUDA, e quanto ela importa para o treinamento de adapters?

<details markdown="1"><summary>Verificação</summary>

Os paged optimizers, que usam a memória unificada da NVIDIA para despejar o estado do otimizador na memória do host durante picos.

Importam pouco no treinamento de adapters, em que o estado do otimizador é de megabytes. Foram projetados para um estado na escala do full fine-tuning, em que um pico transitório de fato encerra a execução.

</details>

4. ▢ Um tutorial de 2023 afirma que o NF4 de 4 bits exige uma GPU NVIDIA. Isso ainda está correto?

<details markdown="1"><summary>Verificação</summary>

Não como absoluto. O `bitsandbytes` agora despacha operações de 4 bits entre CUDA/ROCm, CPU, Intel XPU, Intel Gaudi e Apple MPS, com fallbacks em PyTorch onde um kernel compilado não está disponível.

O CUDA ainda é o caminho mais completo e mais rápido, e a cobertura nos outros backends varia por operação, tamanho de bloco e versão. Então a afirmação correta é "o CUDA é o caminho com melhor suporte", e não "o CUDA é o único caminho", e você verifica contra a sua versão instalada, e não contra qualquer tutorial.

</details>

5. ▢ Qual hiperparâmetro você precisa repensar ao passar do LoRA para o QLoRA?

    - a) O learning rate, que precisa ser reduzido substancialmente
    - b) O valor de alpha, que precisa ser aumentado para compensar
    - c) Nenhum deles, a precisão do base é uma questão separada
    - d) O batch size, que precisa ser aumentado para se manter estável

<details markdown="1"><summary>Verificação</summary>

**c)** Nenhum deles. A precisão do base é uma questão separada.

O QLoRA é o LoRA com um base mais barato. Alguns profissionais tentam um pouco mais de rank para absorver o ruído de quantização, mas isso é uma hipótese a testar, e não uma mudança obrigatória.

</details>

6. ▢ Você treinou contra um base de 4 bits e quer um único modelo implantável. Dê os passos em ordem.

<details markdown="1"><summary>Verificação</summary>

Carregue o base em bf16 (e não em 4 bits), aplique o adapter treinado, faça o merge, salve com o tokenizer e quantize o modelo com merge depois, apenas se precisar de um artefato quantizado para o serving.

Fazer o merge no base de 4 bits exige desquantizar, somar e requantizar, e perde qualidade à toa.

</details>

## Prática no mundo real

- [ ] Carregue um base model em bf16 e em NF4. Registre a memória de cada um e calcule a razão.
- [ ] Execute o mesmo trabalho curto de treinamento contra os dois bases. Registre os segundos por passo e a curva de loss, e anote qual é mais lento e por quanto.
- [ ] Confira qual backend a sua instalação do `bitsandbytes` está de fato usando, e se o seu tamanho de bloco cai em um kernel otimizado ou em um fallback.
- [ ] Amanhã: faça o merge do adapter treinado em 4 bits no base em bf16 e verifique de forma gulosa contra as suas sondas.

## Para ir além

- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Código: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes): o diretório de backends é a autoridade sobre a cobertura
- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- [Lição 17. O que o QLoRA realmente custa](0017-what-qlora-costs.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
