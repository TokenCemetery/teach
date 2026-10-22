---
title: "1. O que um base model realmente é"
description: "O modelo é uma única função de próximo token; base não é instruct"
type: lesson
---

# Lição 1. O que um base model realmente é

**Ligação com a missão:** Você não consegue julgar se o fine-tuning é a resposta certa até saber exatamente o que o modelo faz quando você o deixa em paz.
**Fonte principal:** [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
**Pré-requisitos:** nenhum, esta é a primeira lição.

## Saiba isto

Um modelo de linguagem é uma única função. Ela recebe uma sequência de IDs de tokens e devolve uma pontuação para cada token do seu vocabulário, descrevendo o que poderia vir a seguir. Essa é a operação inteira. Chat, chamadas de ferramentas, recusas, traços de raciocínio: tudo isso é construído em cima desse único passo de próximo token.

Essas pontuações brutas se chamam **logits**. O softmax as transforma em uma distribuição de probabilidade. Um sampler escolhe um token dessa distribuição, o token é anexado à sequência e a função roda de novo. O texto aparece um token por vez, e nada mais está acontecendo.

Duas consequências importam para tudo o que vem depois.

**Os pesos não mudam na inferência.** Quando um modelo parece lembrar de algo de mais cedo em uma conversa, a memória são os tokens que estão na sua janela de contexto, e não uma mudança no modelo. O fine-tuning é a única coisa neste workspace que altera pesos, e acontece offline, antes do serving.

**A amostragem não é o modelo.** Temperature, top-p e top-k remodelam a distribuição depois que o modelo a produziu. Se a qualidade da saída muda quando você muda a temperature, você aprendeu algo sobre o seu sampler, e não sobre os seus pesos. Mantenha a amostragem fixa antes de atribuir qualquer coisa ao treinamento.

### Base versus instruct

Um modelo **base** foi treinado em um único objetivo: prever o próximo token em um corpus muito grande. Ele não responde perguntas. Dado `What is the capital of France?`, ele pode continuar com mais três perguntas de prova, porque era assim que o texto ao redor parecia nos seus dados de treinamento.

Um modelo **instruct** ou **chat** é um base model que foi treinado mais um pouco em pares de instruções e respostas, o que é supervised fine-tuning, e em geral depois disso em dados de preferência humanos ou gerados por modelos. O comportamento de seguir instruções que você dá como certo é uma camada treinada, não uma propriedade da arquitetura.

![A mesma pergunta alimentando um base model e o mesmo base com instruction tuning adicionado. O base continua com mais perguntas de prova; o ajustado produz uma resposta.](images/one-prompt-two-continuations.svg)

Um prompt, duas continuações, e a mesma função de próximo token por baixo de ambas. A segunda caixa é a primeira caixa mais treinamento, que é onde a diferença mora.

De qual deles você parte é uma decisão real:

| Ponto de partida | Você herda | Você precisa fornecer |
|---|---|---|
| Base | Nada além da habilidade bruta com a linguagem | Toda convenção de formatação e de comportamento |
| Instruct | Formatação, seguir instruções, comportamento de recusa | Apenas a sua tarefa, mas você corre o risco de degradar o que já está lá |

A maior parte do fine-tuning com adapters parte de um modelo instruct, porque reconstruir o seguimento de instruções do zero em um dataset pequeno é uma troca perdedora. O custo é que os seus dados de treinamento agora competem com o treinamento que o fornecedor já fez, e essa competição é de onde vem depois o [esquecimento catastrófico](../GLOSSARY.md).

### O sinal de treinamento

Durante o treinamento, o modelo vê uma sequência real e é pontuado pela probabilidade que atribuiu ao token que de fato veio a seguir. Essa pontuação é a **loss de entropia cruzada**. Loss baixa significa que o modelo achou a continuação real pouco surpreendente.

Guarde uma ressalva, porque a etapa 6 é construída sobre ela: a loss mede a surpresa de próximo token em um texto que você já tem. Ela não mede se o modelo é útil.

## Prática

1. ▢ Descreva, em uma frase e sem a palavra "entender", o que um modelo de linguagem calcula.

<details markdown="1"><summary>Verificação</summary>

Dada uma sequência de tokens, ele produz uma pontuação para cada token do vocabulário descrevendo o que poderia vir a seguir.

O instinto errado é descrever a geração ("ele escreve texto") em vez da função. A geração é um loop em volta da função, implementado fora dos pesos. Manter as duas coisas separadas é o que permite raciocinar sobre onde um problema mora.

</details>

2. ▢ Você dá um prompt a um modelo duas vezes com entrada idêntica e recebe duas respostas diferentes. Nomeie dois lugares de onde a diferença poderia vir e diga qual deles envolve os pesos.

<details markdown="1"><summary>Verificação</summary>

O sampler (uma temperature acima de zero escolhe tokens diferentes da mesma distribuição) e o contexto (um system prompt diferente, ou um histórico de conversa que você esqueceu que estava lá). Nenhum dos dois envolve os pesos.

Os pesos ficam congelados na inferência. Se você não os alterou, eles não podem ser a explicação, e essa é a primeira coisa a descartar antes de concluir que um modelo é inconsistente.

</details>

3. ▢ Você dá a um base model o prompt `Summarise this article:` seguido de um artigo, e ele produz outro artigo em vez de um resumo. O modelo está quebrado?

<details markdown="1"><summary>Verificação</summary>

Não. Ele está fazendo exatamente o seu trabalho: continuar um texto plausível. No seu corpus de treinamento, um artigo é seguido muito mais vezes por mais artigo do que por um resumo.

Seguir instruções é um comportamento treinado. Esperar isso de um base model é o erro inicial mais comum, e costuma ser diagnosticado errado como um modelo ruim ou um prompt ruim.

</details>

4. ▢ Qual destas o fine-tuning altera?

    - a) A temperature de amostragem usada no momento do serving
    - b) Os valores numéricos armazenados dentro dos pesos do modelo
    - c) Os tokens presentes na janela de contexto do modelo
    - d) O tamanho do vocabulário com que o modelo foi construído originalmente

<details markdown="1"><summary>Verificação</summary>

**b)** Os valores numéricos armazenados dentro dos pesos do modelo.

A temperature é um botão do momento do serving. O contexto é a entrada de cada requisição. O tamanho do vocabulário é fixado pelo tokenizer e pela matriz de embeddings, e mudá-lo é uma operação muito mais invasiva do que o fine-tuning. Só os valores dos pesos são o que o treinamento move.

</details>

5. ▢ Dê um motivo para fazer fine-tuning de um modelo instruct em vez de um base model, e um motivo para fazer o oposto.

<details markdown="1"><summary>Verificação</summary>

Parta do instruct quando você quer manter o seguimento de instruções e a utilidade geral que você não pode se dar ao luxo de reconstruir a partir de um dataset pequeno, o que acontece quase sempre.

Parta do base quando o formato de saída da sua tarefa é tão diferente do chat comum que o comportamento de chat herdado atrapalha ativamente: saída estruturada rígida, um único rótulo de classificação ou uma notação de domínio em que o enchimento conversacional é puro ruído.

</details>

## Prática no mundo real

- [ ] Execute qualquer modelo que você consiga alcançar localmente ou por uma API. Envie um prompt com temperature 0 duas vezes, e depois com temperature 1 duas vezes. Anote qual par coincidiu e por quê.
- [ ] Encontre um modelo no Hugging Face Hub que tenha uma variante base e uma instruct. Leia os dois model cards e anote o que o card do instruct afirma ter sido adicionado.
- [ ] Amanhã: dê a um base model uma pergunta direta e registre o que ele faz em vez de responder. Guarde a saída. Você vai reconhecer essa falha de novo na etapa 6.

## Para ir além

- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): percorra o caminho de um único token de ponta a ponta
- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Glossário](../GLOSSARY.md): `fine-tuning` neste workspace sempre significa o tipo com base congelado
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
