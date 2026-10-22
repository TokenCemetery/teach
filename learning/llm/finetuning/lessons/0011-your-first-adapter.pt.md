---
title: "11. Seu primeiro adapter"
description: "Uma execução que prova o pipeline antes de provar qualquer outra coisa"
type: lesson
---

# Lição 11. Seu primeiro adapter

**Ligação com a missão:** "Executar" está na missão. Tudo antes disto foi leitura; isto é a execução.
**Fonte principal:** [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**Pré-requisitos:** [Lição 3](0003-tokenizers-and-chat-templates.md), [Lição 9](0009-rank-alpha-and-initialisation.md), [Lição 10](0010-choosing-target-modules.md)

## Aquecimento

1. ▢ Qual é o padrão moderno para os target modules, e por que ele é viável?

<details markdown="1"><summary>Verificação</summary>

Todas as camadas lineares, com rank generoso. Os parâmetros do adapter são desprezíveis diante da memória de ativações, então restringi-los já não compra muito.

</details>

2. ▢ Qual linha de código pega um nome de target module que não casou com nada?

<details markdown="1"><summary>Verificação</summary>

`model.print_trainable_parameters()`. Uma contagem perto de zero significa que o adapter não se acoplou a nada.

</details>

3. ▢ Treinamento ou inferência: onde o `add_generation_prompt=True` pertence?

<details markdown="1"><summary>Verificação</summary>

Inferência. No treinamento o turno do assistant já está no texto, então adicionar o prompt duplica o marcador.

</details>

## Saiba isto

### Escolha a menor coisa que pode falhar de forma informativa

O propósito da sua primeira execução **não** é um bom modelo. É provar que o pipeline está ligado corretamente. Então torne-a barata o bastante para que um erro custe minutos:

- Um base model da classe de 0.5B a 3B. Modelos pequenos treinam rápido e expõem bugs de dados tão bem quanto os grandes.
- Algumas centenas de exemplos. O suficiente para ver a loss se mover.
- `max_steps` em torno de 20 a 50, e não epochs. Você quer que termine rápido.

Otimizar qualquer coisa antes de o pipeline estar provado é esforço desperdiçado, e esconde qual mudança causou qual efeito.

### Uma execução mínima

```text
dataset := load_dataset("<a small instruction dataset>", split: "train[:500]")

adapter_config := {
    rank: 16,
    alpha: 32,
    dropout: 0.05,
    adapt_bias: false,
    target_modules: "all-linear",
}

run_config := {
    output_dir: "runs/first-adapter",
    max_steps: 50,
    per_device_batch_size: 1,
    gradient_accumulation_steps: 8,      # effective batch size 8
    learning_rate: 2e-4,
    warmup_steps: 5,
    lr_schedule: "cosine",
    logging_steps: 1,                    # every step, for the first run
    max_length: 1024,
    gradient_checkpointing: true,
    precision: "bf16",
}

trainer := new_trainer(
    model: "<a small base model>",
    train_dataset: dataset,
    adapter_config: adapter_config,
    run_config: run_config,
)

trainer.train()
trainer.save("runs/first-adapter/final")
```

Duas notas sobre essa superfície de API. O `SFTTrainer` aceita uma *string* de modelo e o carrega para você. O comprimento de sequência é `max_length` no `SFTConfig`. Ambos mudaram entre releases, então **leia a documentação da versão instalada em vez de confiar neste trecho ou na sua memória.** Essa instrução não é texto de praxe; é a fonte mais confiável de tardes desperdiçadas em todo este workspace.

### Precisão, hardware e o que de fato varia

`bf16=True` exige suporte de hardware a bfloat16, que é difundido nos aceleradores modernos mas não universal. Em dispositivos mais antigos você pode precisar de fp16 com loss scaling, e em alguns backends o fp32 completo é a única opção. O princípio da Lição 5 não muda; só mudam os formatos disponíveis.

Da mesma forma, o acelerador específico por trás deste script não faz parte do método. Os conceitos, a aritmética e os modos de falha são idênticos em CUDA, ROCm, Intel, Apple Silicon e CPU. O que difere é quais kernels são otimizados, quais precisões são suportadas e quão rápido um passo leva. Onde um backend de fato restringe o método, este workspace diz isso explicitamente; veja a [Lição 16](0016-training-through-a-quantized-base.md).

### As quatro verificações, em ordem

Execute-as antes de se importar com a curva de loss.

**1. O adapter existe?**

```python
trainer.model.print_trainable_parameters()
```

Compare com a sua aritmética da Lição 8. Uma contagem zero, ou uma que discorde por mais do que arredondamento, significa parar e corrigir.

**2. Os dados são o que você pensa que são?**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

Decodifique um exemplo de treinamento real e leia. Só essa verificação pega incompatibilidades de template, tokens de fim de turno ausentes, um bug de mascaramento e truncamento no meio da resposta: quatro das cinco causas mais comuns de um fine-tune ruim. **Não a pule.** São os dez segundos de maior valor em todo o processo.

**3. A loss se move?**

Ao longo de 50 passos com `logging_steps=1`, a loss deve cair de forma visível. Loss plana desde o passo um significa que o adapter não está acoplado, que o learning rate está muito baixo ou que nada está sendo pontuado.

**4. Ele consegue fazer overfitting em dois exemplos?**

O smoke test mais forte disponível. Treine em dois exemplos por cem passos. A loss deve se aproximar de zero. Se ele não consegue memorizar dois exemplos, o pipeline está quebrado, e você descobriu isso em dois minutos, e não depois de uma execução de seis horas.

### Guarde o que você vai precisar para reproduzir

O diretório do adapter é pequeno, em geral de um dígito a algumas centenas de megabytes, e contém apenas os pesos do adapter mais uma configuração que registra o base model, o rank, o alpha e os target modules. Ele é inútil sem aquele base model exato, então registre o identificador do base model e a sua revisão junto com ele.

Registre também as versões das bibliotecas. Uma configuração que treinou limpa há seis meses pode não carregar da mesma forma, e "qual versão era essa" não é recuperável depois do fato.

## Prática

1. ▢ Você tem 50.000 exemplos e um base model grande disponível. Por que essa é a primeira execução errada?

<details markdown="1"><summary>Verificação</summary>

Porque o trabalho da primeira execução é provar o pipeline, e uma execução longa e cara dá a mesma informação que uma curta e barata, só que muito mais tarde e a um custo maior.

Pior, se algo está errado você descobre depois de horas em vez de minutos, e não consegue dizer qual de várias mudanças importou.

</details>

2. ▢ A loss está completamente plana desde o passo um. Nomeie três causas na ordem em que você as verificaria.

<details markdown="1"><summary>Verificação</summary>

1. O adapter não se acoplou a nada; confira `print_trainable_parameters()`.
2. Todo label é `-100`, então nada está sendo pontuado; confira a contagem de labels em um exemplo real.
3. O learning rate está ordens de grandeza baixo demais; confira se está em torno de `1e-4`, e não `1e-5` ou menos.

As três custam uma linha para descartar, e é por isso que vêm antes de qualquer coisa sutil.

</details>

3. ▢ Por que decodificar um exemplo de treinamento em vez de confiar no dataset?

<details markdown="1"><summary>Verificação</summary>

Porque as falhas que importam são invisíveis no dataset e visíveis no texto decodificado: um chat template errado, um token de fim de turno ausente, tokens de prompt que deveriam estar mascarados e não estão, uma resposta truncada no meio da frase pelo `max_length`.

Nenhuma delas lança um erro. Todas produzem uma execução que parece boa e um modelo que não é.

</details>

4. ▢ Seu adapter não consegue levar a loss perto de zero em dois exemplos em cem passos. O que isso diz?

<details markdown="1"><summary>Verificação</summary>

Que o pipeline está quebrado, e não que a tarefa é difícil. Dois exemplos são trivialmente memorizáveis por qualquer adapter que funcione.

Procure um adapter não acoplado, labels totalmente mascarados, um learning rate perto de zero ou um data collator produzindo algo diferente do que você espera.

</details>

5. ▢ Você tem o diretório do adapter e mais nada. Consegue usá-lo?

<details markdown="1"><summary>Verificação</summary>

Só se você conseguir identificar o base model exato contra o qual ele foi treinado, que a configuração do adapter registra pelo nome. Aplicado a um base diferente, mesmo a outro checkpoint da mesma família, o resultado é, na melhor das hipóteses, degradado e, na pior, absurdo.

Registre o identificador do base model, a sua revisão e as versões das suas bibliotecas. Um adapter é um diff, e um diff precisa do seu base.

</details>

6. ▢ Batch size efetivo para `per_device_train_batch_size=2`, `gradient_accumulation_steps=8`, em 4 dispositivos?

<details markdown="1"><summary>Verificação</summary>

2 × 8 × 4 = 64.

Reporte este número, e não o por dispositivo. Comparar execuções pelo batch size por dispositivo é uma forma confiável de tirar uma conclusão falsa.

</details>

## Prática no mundo real

- [ ] Execute o teste de overfitting em dois exemplos antes de qualquer treinamento de verdade. Confirme que a loss se aproxima de zero.
- [ ] Decodifique e leia um exemplo de treinamento inteiro. Conte quantas posições são pontuadas e quantas são mascaradas.
- [ ] Complete uma execução de 50 passos de ponta a ponta e salve o adapter. Anote o tamanho dele em disco.
- [ ] Amanhã: escreva o identificador do base model, a revisão e todas as versões das bibliotecas em um arquivo ao lado do adapter.

## Para ir além

- [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Modos de falha](../reference/failure-modes.md): mantenha isto aberto durante a execução
- [Lição 12. Lendo uma execução de treinamento](0012-reading-a-training-run.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
