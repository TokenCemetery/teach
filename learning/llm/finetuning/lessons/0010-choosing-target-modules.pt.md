---
title: "10. Escolhendo os target modules"
description: "Só atenção é uma ablação de 2021, não um padrão"
type: lesson
---

# Lição 10. Escolhendo os target modules

**Ligação com a missão:** Os target modules importam mais do que o rank, e a sabedoria recebida sobre eles está desatualizada. Este é um lugar onde você pode ser mensuravelmente melhor do que o profissional médio.
**Fonte principal:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Pré-requisitos:** [Lição 2](0002-where-the-weights-live.md), [Lição 9](0009-rank-alpha-and-initialisation.md)

## Aquecimento

1. ▢ O que `α/r` controla, e o que `r` sozinho controla?

<details markdown="1"><summary>Verificação</summary>

`α/r` define a escala da contribuição do adapter. `r` sozinho define a sua capacidade: quão complexa pode ser a atualização que ele expressa.

</details>

2. ▢ Qual subcamada guarda a maior parte dos parâmetros de um bloco transformer?

<details markdown="1"><summary>Verificação</summary>

A MLP, aproximadamente 75 a 80% do bloco, porque a dimensão intermediária é várias vezes o tamanho oculto e a grouped-query attention encolhe duas das quatro projeções de atenção.

</details>

3. ▢ O que uma `B` inicializada em zero garante?

<details markdown="1"><summary>Verificação</summary>

Que o modelo adaptado é idêntico ao base model antes do primeiro passo do otimizador.

</details>

## Saiba isto

### O que o artigo original fez, e por que isso não é um conselho

O artigo do LoRA adaptou apenas as projeções de atenção, nos seus experimentos principalmente `W_q` e `W_v`, e deixou a MLP em paz. Essa escolha se propagou por anos de tutoriais, e é de onde vem o `target_modules=["q_proj", "v_proj"]`.

Duas coisas a entender sobre isso. Foi uma constatação razoável sob um orçamento de memória e nas tarefas medidas. E **não** é um resultado geral sobre onde a adaptação deve acontecer. Tratar uma ablação de 2021 como padrão é o erro herdado mais comum desta área.

### O argumento a favor da MLP

Da Lição 2: a MLP guarda aproximadamente quatro quintos dos parâmetros de cada bloco. Há um corpo substancial de trabalhos de interpretabilidade que tratam as camadas de MLP como o lugar onde mora boa parte do conhecimento aprendido e da detecção de features de um modelo, enquanto a atenção roteia informação entre posições. Se a sua tarefa exige que o modelo *saiba* ou *classifique* algo de forma diferente, os parâmetros que codificam isso estão desproporcionalmente na MLP, e um adapter só de atenção não consegue alcançá-los.

### O padrão atual

Trabalhos recentes convergem para uma recomendação direta: **adapte todas as camadas lineares** e dê ao adapter rank suficiente. O texto do TRL sobre o resultado "LoRA without regret" é explícito: aplicar o LoRA a toda camada linear, incluindo a MLP, com rank suficiente, fecha a diferença para o full fine-tuning em cargas de supervised fine-tuning, enquanto as configurações só de atenção não fecham.

```text
# The modern default: let the library find every linear layer.
config := {rank: 64, alpha: 128, target_modules: "all-linear"}

# The explicit equivalent, for a Llama-style architecture.
config := {
    rank: 64,
    alpha: 128,
    target_modules: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
}
```

`"all-linear"` é a mais segura das duas, porque não fica obsoleta diante de uma arquitetura cujos nomes de módulos diferem da lista que você decorou. O custo é que você abre mão do controle preciso e deve conferir o que ela de fato casou.

Por que isso é viável agora: pela Lição 7, os parâmetros do adapter são uma fatia desprezível da memória de treinamento. Restringir os target modules para economizar memória era uma troca real em 2021 e hoje é quase uma não troca. O que você de fato está trocando é o risco de overfitting em datasets pequenos.

### A decisão

| Situação | Targets | Raciocínio |
|---|---|---|
| Padrão para uma tarefa real | Todas as camadas lineares | Melhor qualidade por unidade de esforço; coincide com a evidência atual |
| Dataset pequeno (< ~1k exemplos) | Só atenção, rank baixo | Limitar a capacidade de propósito para limitar a memorização |
| Apenas estilo ou tom | Só atenção, rank baixo | Uma pequena mudança de comportamento precisa de uma pequena atualização |
| A tarefa precisa de novas discriminações | Precisa incluir a MLP | A atenção sozinha não alcança onde elas moram |
| Reproduzindo um artigo | Exatamente o que o artigo usou | Senão você não está reproduzindo |

### Dois módulos sobre os quais as pessoas perguntam

**Embeddings e a cabeça de saída.** Em geral deixados em paz. Adaptá-los é caro em relação ao benefício, e é o único lugar em que mudar pesos pode alterar o significado de cada token. A exceção genuína é adicionar novos tokens especiais, o que exige mexer na tabela de embeddings e é uma operação diferente de adaptá-la.

**Termos de bias.** `bias="none"` é a configuração padrão. Treinar também os biases ( `"all"` ou `"lora_only"`) é barato, mas raramente é a diferença entre uma execução que funciona e uma que falha, e complica o merge.

### A verificação que pega o erro real

Imprima o que casou, todas as vezes:

```text
model := attach_adapter(base_model, config)
print(model.trainable_parameter_count())
print(first 8 parameter names containing "lora")
```

Um nome de target module que não casou com nada produz um erro ou, dependendo da versão, um modelo sem adapter nenhum, que treina, registra uma loss e não aprende nada. Uma contagem de parâmetros treináveis que discorda da sua aritmética da Lição 8 é o aviso mais cedo possível.

## Prática

1. ▢ Por que o artigo original teve como alvo só a atenção, e por que isso não é um padrão hoje?

<details markdown="1"><summary>Verificação</summary>

Foi uma ablação sob um orçamento de memória apertado, nas tarefas que os autores mediram, numa época em que limitar os parâmetros treináveis importava. Nunca foi uma alegação de que a atenção é onde a adaptação deve ficar.

Hoje a memória do adapter é desprezível, e a evidência favorece cobrir todas as camadas lineares com rank adequado.

</details>

2. ▢ A sua tarefa exige que o modelo distinga entre conceitos do domínio que ele hoje confunde. Só atenção ou all-linear?

<details markdown="1"><summary>Verificação</summary>

All-linear. Fazer novas discriminações significa mudar a detecção de features e as associações armazenadas, que moram desproporcionalmente na MLP. A atenção roteia informação; não é onde essa distinção é codificada.

</details>

3. ▢ Você tem 400 exemplos de treinamento. Argumente a favor de restringir os target modules.

<details markdown="1"><summary>Verificação</summary>

Com 400 exemplos, a capacidade é o risco, e não a restrição. Um adapter all-linear completo com rank generoso pode memorizar o conjunto inteiro: loss de treinamento perto de zero, loss held-out subindo e nenhuma generalização.

Restringir à atenção com rank baixo é um limite deliberado de capacidade, que funciona como regularização. A melhor resposta, se estiver disponível, é mais dados.

</details>

4. ▢ Qual mudança tem mais chance de elevar a qualidade em uma tarefa real com um dataset razoável?

    - a) Aumentar o rank do adapter de 16 para 64
    - b) Estender os targets a todas as camadas lineares
    - c) Adicionar dropout de 0.05 do LoRA à execução
    - d) Treinar por mais um epoch completo

<details markdown="1"><summary>Verificação</summary>

**b)** Estender os targets a todas as camadas lineares.

Isso coloca aproximadamente quatro vezes mais parâmetros ao alcance da adaptação, incluindo a MLP. Aumentar o rank soma capacidade dentro das camadas que você já alcança. O dropout regulariza, em vez de melhorar o ajuste. Um epoch extra arrisca overfitting sem somar capacidade.

</details>

5. ▢ Você define `target_modules=["c_attn"]` e a execução treina com a loss mal se movendo. O que você confere primeiro?

<details markdown="1"><summary>Verificação</summary>

Se `c_attn` existe neste modelo. Ela é a projeção de atenção fundida em arquiteturas no estilo GPT-2 e não existe nas no estilo Llama, que usam `q_proj`, `k_proj`, `v_proj` separadas.

Imprima os nomes dos módulos e depois `print_trainable_parameters()`. Uma contagem de treináveis perto de zero é a resposta.

</details>

6. ▢ Por que `"all-linear"` é mais seguro do que uma lista explícita de módulos?

<details markdown="1"><summary>Verificação</summary>

Ela é resolvida contra o modelo carregado, e não contra a sua memória, então não perde camadas em silêncio em uma arquitetura cuja nomenclatura difere.

O custo é a perda de precisão, então verifique o que ela casou e note que ela pode incluir camadas que você preferiria deixar em paz.

</details>

## Prática no mundo real

- [ ] Monte um adapter só de atenção e um all-linear com o mesmo rank no mesmo modelo. Registre as duas contagens de parâmetros treináveis e a razão entre elas.
- [ ] Verifique quais módulos o `"all-linear"` casou, imprimindo os nomes dos parâmetros do adapter. Anote qualquer coisa inesperada.
- [ ] Amanhã: encontre três configurações de fine-tuning publicadas online e anote quais têm como alvo só a atenção. Julgue se o autor escolheu isso ou herdou.

## Para ir além

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Artigo: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms): as ablações de target modules
- [Hiperparâmetros do LoRA](../reference/lora-hyperparameters.md)
- [Lição 11. Seu primeiro adapter](0011-your-first-adapter.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
