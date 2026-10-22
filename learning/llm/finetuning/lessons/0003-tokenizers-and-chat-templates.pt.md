---
title: "3. Tokenizers e chat templates"
description: "Treine na renderização que você vai servir"
type: lesson
---

# Lição 3. Tokenizers e chat templates

**Ligação com a missão:** A causa mais comum de um fine-tune que treina limpo e se comporta mal é uma incompatibilidade de template, e não um hiperparâmetro.
**Fonte principal:** [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
**Pré-requisitos:** [Lição 1](0001-what-a-base-model-is.md), [Lição 2](0002-where-the-weights-live.md)

## Aquecimento

1. ▢ O que guarda mais parâmetros em um bloco moderno, a atenção ou a MLP?

<details markdown="1"><summary>Verificação</summary>

A MLP, porque sua dimensão intermediária é várias vezes o tamanho oculto, e a grouped-query attention encolhe ainda mais `k_proj` e `v_proj`.

</details>

2. ▢ Como você encontra os nomes reais dos módulos de um modelo?

<details markdown="1"><summary>Verificação</summary>

Imprima-os a partir do modelo carregado com `named_modules()`. Nunca os lembre de cabeça; eles variam por arquitetura.

</details>

3. ▢ O que a loss de entropia cruzada mede?

<details markdown="1"><summary>Verificação</summary>

Quanta probabilidade o modelo atribuiu ao token que de fato veio a seguir. Loss baixa significa que a continuação verdadeira foi pouco surpreendente para o modelo.

</details>

## Saiba isto

O modelo não vê texto. Ele vê inteiros. O tokenizer é o mapeamento entre os dois, e faz parte do modelo: o tokenizer de um checkpoint não é intercambiável com o de outro, mesmo dentro da mesma família.

### O que é um tokenizer

Os modelos modernos usam tokenização por subpalavras, em geral byte-pair encoding. Treinar o tokenizer significa partir de bytes e juntar repetidamente o par adjacente mais frequente, produzindo um vocabulário em que as palavras comuns são tokens únicos e as palavras raras se dividem em pedaços.

Três propriedades pesam na prática:

**Tokens não são palavras.** ` the` (com um espaço no início) e `the` são tokens diferentes. Maiúsculas mudam a tokenização. Um número como `1234` pode ser um token ou quatro, e é por isso que os modelos são ruins em aritmética de maneiras que parecem arbitrárias.

**A contagem de tokens não é a contagem de caracteres.** O inglês tem em média cerca de quatro caracteres por token; código, escritas não latinas e formatações incomuns são muito menos eficientes. O seu orçamento de comprimento de sequência na Lição 7 é medido em tokens, então você precisa medir, não estimar.

**Tokens especiais carregam estrutura.** Início de sequência, fim de sequência, padding e os marcadores de papel abaixo são entradas comuns do vocabulário que o modelo aprendeu a tratar como estruturais. Emiti-los à mão de forma incorreta não é um erro de sintaxe; é uma mudança silenciosa de distribuição.

### Chat templates

Um modelo de chat foi treinado em conversas renderizadas em uma única sequência plana de tokens por um formato de string específico e exato. Por exemplo, um modelo pode ter sido treinado em algo com este formato:

```text
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi.<|im_end|>
```

Outra família usa marcadores completamente diferentes. O formato não é uma convenção que você possa aproximar: é a distribuição a que os pesos foram ajustados. Erre um marcador, adicione uma quebra de linha perdida ou omita o bloco de system quando o modelo espera um, e o modelo passa a operar levemente fora da distribuição. Ele ainda vai produzir texto fluente, e é exatamente por isso que essa falha é difícil de perceber.

O template vem junto com o tokenizer, como uma string Jinja. Use-o em vez de escrever o formato você mesmo:

```text
tokenizer := load_tokenizer("<model>")
messages := [
    {role: "system", content: "You are helpful."},
    {role: "user", content: "Hello"},
]

# For inference: leaves the sequence ready for the model to continue.
prompt := tokenizer.render(messages, add_generation_prompt: true)

# For training: the assistant turn is already present, so no generation prompt.
full := tokenizer.render(messages + [{role: "assistant", content: "Hi."}])

print(exact(prompt))
print(exact(full))
```

Imprimir a string exata, e não uma visão resumida, importa. A diferença entre um template correto e um quebrado costuma ser um único caractere de espaço em branco, e um print comum pode escondê-lo. Em Python isso significa `repr`, e não `print`, sobre a string.

### A regra única

**Treine na mesma renderização que você vai servir.** Se você faz fine-tuning no seu próprio formato improvisado e depois serve pelo template oficial do modelo, você treinou uma distribuição e implantou outra. A curva de loss vai parecer boa. O modelo será sutilmente pior, e você vai gastar um dia culpando o rank.

O `add_generation_prompt` é onde isso mais costuma dar errado: ele pertence à inferência, onde você quer que o modelo continue como o assistant, e não a um exemplo de treinamento, onde o texto do assistant é parte da sequência que está sendo aprendida.

![Uma conversa renderizada duas vezes como uma faixa de peças de template. As duas compartilham as mesmas três peças que terminam no marcador do assistant; a renderização de inferência para ali, enquanto a de treinamento carrega mais uma peça, o próprio texto do assistant e seu marcador de fim.](images/where-the-turn-begins.svg)

As duas renderizações são as mesmas peças nos mesmos lugares até o marcador do assistant. A que difere é a peça seguinte, que é exatamente o que o modelo deve produzir na inferência e exatamente o que ele deve aprender durante o treinamento.

### Base models não têm template

Se o tokenizer de um base model não tem chat template, isso não é um bug, porque não há formato de conversa a preservar. Você é quem escolhe o formato, então escolha um, anote-o e use-o de forma idêntica no treinamento e no serving.

## Prática

1. ▢ Por que você não pode trocar o tokenizer entre dois checkpoints da mesma família de modelos?

<details markdown="1"><summary>Verificação</summary>

Os IDs dos tokens indexam diretamente a matriz de embeddings. Um vocabulário diferente mapeia o mesmo inteiro para uma linha diferente, então toda entrada é traduzida errado em silêncio. A saída é um absurdo fluente, ou uma falha se os tamanhos dos vocabulários diferirem.

</details>

2. ▢ Você está construindo um exemplo de treinamento. O `add_generation_prompt` deve ser `True` ou `False`, e por quê?

<details markdown="1"><summary>Verificação</summary>

`False`. O generation prompt é o marcador de abertura que diz ao modelo "o assistant fala a seguir", o que é útil na inferência, quando o turno do assistant ainda não existe. No treinamento o turno do assistant está presente no texto, então adicionar o prompt duplica o marcador e desloca a sequência para fora do formato que o modelo conhece.

</details>

3. ▢ O seu fine-tune treina até uma loss baixa, mas no momento do serving o modelo divaga além do fim da resposta em vez de parar. Nomeie a causa mais provável.

<details markdown="1"><summary>Verificação</summary>

O token de fim de turno estava ausente dos seus exemplos de treinamento, então o modelo nunca aprendeu que as respostas terminam.

A loss não consegue pegar isso: prever uma continuação fluente é exatamente aquilo pelo que o modelo foi recompensado nos seus dados. É um bug de construção de dados que só uma geração real revela, e é um dos motivos pelos quais a Lição 24 insiste em gerar em vez de apenas pontuar.

</details>

4. ▢ Um prompt tem 700 palavras em inglês. Aproximadamente quantos tokens, e você confiaria nessa estimativa para um orçamento de treinamento?

<details markdown="1"><summary>Verificação</summary>

Aproximadamente 900 a 1000 tokens, tomando cerca de 1.3 token por palavra em inglês. Não, você não confiaria nela: a razão varia bastante com código, JSON, escritas não latinas e formatações incomuns, todos comuns em dados de fine-tuning.

Meça a distribuição real com o tokenizer de verdade. A Lição 7 transforma essa distribuição em um número de memória.

</details>

5. ▢ Qual destas é seguro mudar entre o treinamento e o serving?

    - a) A string exata do chat template usado
    - b) O tokenizer que vem com o modelo
    - c) A temperature de amostragem usada na geração
    - d) O token especial que marca o fim de um turno

<details markdown="1"><summary>Verificação</summary>

**c)** A temperature de amostragem usada na geração.

A temperature é aplicada depois que o modelo produz a sua distribuição, então é uma escolha de serving. As outras três definem a distribuição a que os pesos foram ajustados; mudar qualquer uma delas significa servir um problema diferente daquele em que você treinou.

</details>

## Prática no mundo real

- [ ] Pegue um modelo e renderize um template com a chamada real de chat template da sua biblioteca (por exemplo, `apply_chat_template(..., tokenize=False)` no Transformers), imprimindo a string exata com os espaços em branco incluídos (por exemplo, o `repr` do Python). Copie-a para as suas anotações.
- [ ] Tokenize o mesmo parágrafo em duas famílias de modelos diferentes e compare as contagens de tokens. Depois tokenize um bloco de JSON e compare de novo.
- [ ] Amanhã: quebre um template de propósito, removendo o marcador de fim de turno, e então dê um prompt ao modelo. Observe o que ele faz. Essa é a falha que você está aprendendo a reconhecer.

## Para ir além

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [Código: minbpe, Andrej Karpathy](https://github.com/karpathy/minbpe): byte-pair encoding em forma legível
- [Modos de falha](../reference/failure-modes.md): a incompatibilidade de template aparece ali
- [Lição 21. Construindo o dataset](0021-building-the-dataset.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
