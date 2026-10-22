---
title: "13. Fazendo merge, salvando e entregando um adapter"
description: "O merged é exato; um adapter é um diff que precisa do seu base"
type: lesson
---

# Lição 13. Fazendo merge, salvando e entregando um adapter

**Ligação com a missão:** Um adapter que só existe em um script de treinamento não foi entregue. Esta lição encerra a etapa 3.
**Fonte principal:** [Docs: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Pré-requisitos:** [Lição 8](0008-the-low-rank-idea.md), [Lição 12](0012-reading-a-training-run.md)

## Aquecimento

1. ▢ Qual checkpoint você entrega a partir de uma execução com overfitting?

<details markdown="1"><summary>Verificação</summary>

O do mínimo da loss held-out, e não o do passo final.

</details>

2. ▢ O que uma curva de loss nunca pode mostrar a você?

<details markdown="1"><summary>Verificação</summary>

Se as gerações são utilizáveis e se as capacidades fora da distribuição da sua tarefa se degradaram. Ambas exigem geração de verdade contra sondas fixas.

</details>

3. ▢ Escreva a atualização do LoRA, com a escala.

<details markdown="1"><summary>Verificação</summary>

`ΔW = (α/r) · BA`, somada à `W₀` congelada.

</details>

## Saiba isto

### O que há no diretório

Um adapter salvo contém, aproximadamente:

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

Pequeno, muitas vezes dezenas de megabytes. E **incompleto por projeto**: é um diff, sem sentido sem o base model exato nomeado na sua configuração. Perder o rastro do base, ou de qual revisão dele, transforma o adapter em lixo.

### Duas formas de entregar

**Sem merge.** Carregue o base, aplique o adapter no momento do carregamento.

```text
base := load_model("<base model>", dtype: "bfloat16")
model := load_adapter(base, "runs/first-adapter/final")
```

**Com merge.** Incorpore a atualização aos pesos e descarte a estrutura do adapter.

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

Salve o tokenizer junto. Um diretório de modelo sem o seu tokenizer é um chamado de suporte esperando para acontecer.

### Escolhendo entre eles

| | Sem merge | Com merge |
|---|---|---|
| Disco | O base uma vez, adapters em megabytes | Uma cópia completa do modelo por tarefa |
| Velocidade de inferência | Dois matmuls pequenos extras por camada adaptada | Idêntica à do base model |
| Várias tarefas | Um base, muitos adapters, intercambiáveis | Um modelo completo para cada |
| Implantação | A stack de serving precisa suportar adapters | Qualquer stack que carregue um modelo |
| Composabilidade | Adapters podem ser trocados ou ponderados em tempo de execução | Fixa no momento do merge |

![Servindo três tarefas. Com merge, três modelos completos guardam cada um a sua própria cópia dos pesos do base ao lado de um delta. Sem merge, uma única cópia dos pesos do base fica acima dos mesmos três deltas.](images/how-many-copies-of-the-base.svg)

Os três deltas são os mesmos três dos dois lados. O que se multiplica é a parte sombreada, que também é a parte grande.

A regra prática: **faça merge para uma implantação de propósito único, fique sem merge ao servir várias tarefas a partir de um único base.** A Lição 25 trata do serving multi-adapter com a devida profundidade.

### O merge é exato, com duas exceções

Como a atualização é aditiva e linear, o merge é aritmeticamente exato. `W₀ + (α/r)BA` é a mesma função que o modelo sem merge calculava. Não há aproximação nem perda de qualidade.

Exceto em dois casos, ambos que vale conhecer:

**Fazer merge em um base quantizado tem perda.** Se o base é de 4 bits, somar uma atualização em bf16 exige desquantizar, somar e requantizar, e o passo de requantização perde informação. A ordem correta é: treinar contra o base quantizado, depois fazer o merge no base de *precisão total*, depois quantizar o resultado do merge se for preciso. Fazer o merge direto nos pesos quantizados degrada a qualidade sem motivo. A etapa 4 volta a isso.

**O dropout muda a escala efetiva.** O `lora_dropout` está ativo durante o treinamento e inativo na inferência. Esse é o comportamento padrão do dropout e normalmente inofensivo, mas significa que o peso com merge reflete o caminho sem dropout, que é o correto.

### Verifique o merge

Nunca presuma. Compare as saídas:

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

A decodificação gulosa é o ponto: com a amostragem ligada, você não consegue distinguir um bug de merge de uma aleatoriedade comum. Pequenas diferenças numéricas ainda podem causar uma divergência tarde em uma geração longa, então compare um número modesto de tokens e investigue uma divergência *cedo*, e não uma tardia.

### Vários adapters em um único base

O PEFT pode manter vários adapters e alternar entre eles, e pode combiná-los com pesos:

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

A combinação ponderada é uma ferramenta genuinamente útil e não é mágica: dois adapters treinados de forma independente em tarefas diferentes não se compõem de maneira confiável em um que faça as duas coisas. Vale tentar e precisa ser medido, e não presumido. Trate qualquer afirmação sobre aritmética de adapters como algo a verificar na sua própria tarefa.

### O que registrar

Tudo o que é necessário para reproduzir e depurar depois:

- Identificador do base model **e revisão**
- Configuração do adapter, literal
- Identidade do dataset e a divisão exata
- Seed, batch size efetivo, learning rate, schedule, passos
- Qual checkpoint você escolheu e por quê, ou seja, o número held-out que o justificou
- Versões das bibliotecas
- Resultados da avaliação, incluindo as sondas de regressão

Isso não é processo pelo processo. Daqui a seis meses, a pergunta "por que o adapter antigo é melhor do que o novo" só pode ser respondida a partir de registros como estes.

## Prática

1. ▢ Por que um arquivo de adapter de 40 MB é inútil sozinho?

<details markdown="1"><summary>Verificação</summary>

Ele contém só as matrizes `A` e `B`: um diff contra um conjunto específico de pesos do base. Sem aquele base model e revisão exatos ele não pode ser aplicado, e aplicado a um base quase igual ele se degrada em silêncio.

</details>

2. ▢ Você serve cinco variantes com fine-tuning de um único base model. Merge ou não?

<details markdown="1"><summary>Verificação</summary>

Não faça merge. Sem merge significa uma cópia do base na memória mais cinco adapters pequenos, intercambiáveis por requisição. Com merge significa cinco cópias completas do modelo.

O custo é de dois matmuls pequenos extras por camada adaptada e uma stack de serving que suporte adapters.

</details>

3. ▢ Você treinou contra um base quantizado em 4 bits. Descreva o procedimento correto de merge.

<details markdown="1"><summary>Verificação</summary>

Carregue o base em precisão total, aplique o adapter, faça o merge ali e quantize o modelo com merge depois, se precisar de um artefato quantizado.

Fazer o merge direto nos pesos quantizados exige desquantizar, somar e requantizar, e a requantização perde informação sem benefício algum.

</details>

4. ▢ Você faz o merge e depois compara gerações com amostragem em temperature 0.8. As saídas diferem. O que você aprendeu?

<details markdown="1"><summary>Verificação</summary>

Nada. Com a amostragem ligada, saídas diferentes são esperadas independentemente de o merge estar correto.

Compare com decodificação gulosa, em que qualquer divergência é atribuível aos pesos. Depois investigue as divergências cedo; uma diferença que aparece só depois de muitos tokens pode ser deriva numérica comum.

</details>

5. ▢ O que é verdadeiro sobre fazer merge de um LoRA não quantizado?

    - a) É exato e não custa nada no momento da inferência
    - b) Perde um pouco de qualidade mas acelera a inferência
    - c) É exato mas exige mais memória na inferência
    - d) Tem perda e deve ser evitado em uso de produção

<details markdown="1"><summary>Verificação</summary>

**a)** É exato e não custa nada no momento da inferência.

A atualização é aditiva e linear, então é incorporada a uma matriz de pesos comum, com a mesma função, a mesma memória e nenhum matmul extra. Essa propriedade é o que distinguia o LoRA dos métodos de camada de adapter anteriores.

</details>

6. ▢ Você combina um adapter de formatação e um adapter de conhecimento de domínio com `add_weighted_adapter` e o resultado rende menos do que os dois. Isso é surpreendente?

<details markdown="1"><summary>Verificação</summary>

Não. Atualizações de baixo rank treinadas de forma independente ocupam subespaços sem relação, e a sua soma ponderada não tem garantia de ser uma boa atualização para nenhuma das tarefas, quanto mais para as duas.

Às vezes funciona bem e vale tentar. Nunca é algo a presumir; meça contra cada adapter sozinho.

</details>

## Prática no mundo real

- [ ] Faça o merge do seu adapter e verifique com decodificação gulosa nas suas sondas fixas. Confirme que as saídas coincidem.
- [ ] Compare os tamanhos dos diretórios: o adapter sozinho contra o modelo com merge. Anote a razão.
- [ ] Escreva o registro de execução descrito acima, completo, para uma execução real.
- [ ] Amanhã: carregue dois adapters em um único base e alterne entre eles para o mesmo prompt. Observe a diferença.

## Para ir além

- [Docs: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: Model merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [Lição 25. Servindo adapters](0025-serving-adapters.md)
- [Modos de falha](../reference/failure-modes.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
