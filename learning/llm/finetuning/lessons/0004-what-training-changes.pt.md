---
title: "4. O que o treinamento realmente muda"
description: "As quatro operações em um passo de treinamento"
type: lesson
---

# Lição 4. O que o treinamento realmente muda

**Ligação com a missão:** Todo argumento de memória, hiperparâmetro e modo de falha deste workspace decorre do que um passo de treinamento faz.
**Fonte principal:** [Artigo científico: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
**Pré-requisitos:** [Lição 1](0001-what-a-base-model-is.md), [Lição 3](0003-tokenizers-and-chat-templates.md)

## Aquecimento

1. ▢ Por que o treinamento e o serving precisam usar exatamente o mesmo chat template?

<details markdown="1"><summary>Verificação</summary>

O template define a distribuição de tokens a que os pesos são ajustados. Treinar em uma renderização e servir outra significa implantar um problema diferente, e a loss não vai revelar isso.

</details>

2. ▢ O que uma conexão residual faz em volta de cada subcamada?

<details markdown="1"><summary>Verificação</summary>

Soma a saída da subcamada de volta ao fluxo em andamento em vez de substituí-lo, de modo que cada bloco contribui com um incremento, e não com uma reescrita.

</details>

3. ▢ Nomeie as duas projeções da MLP que alargam e estreitam a dimensão oculta.

<details markdown="1"><summary>Verificação</summary>

`up_proj` alarga até a dimensão intermediária, `down_proj` volta para a dimensão oculta. `gate_proj` produz o gate aplicado no meio do caminho.

</details>

## Saiba isto

Um passo de treinamento são quatro operações. Todo custo de memória da etapa 2 é uma destas quatro mantendo algo na memória.

**1. Forward pass.** Execute um batch de sequências pelo modelo e calcule a loss. Para tornar o passo 3 possível, os resultados intermediários de cada camada, as **ativações**, precisam ser mantidos em vez de descartados. É por isso que o treinamento precisa de muito mais memória do que a inferência.

**2. Loss.** Entropia cruzada entre a distribuição prevista e o próximo token real, com média sobre cada posição que conta. Quais posições contam é uma escolha sua, e isso importa:

- A **loss de sequência completa** pontua todos os tokens, inclusive o prompt do usuário. O modelo aprende a prever prompts além de respostas.
- A **loss apenas da completion** mascara os tokens do prompt, pontuando só a resposta do assistant.

O mascaramento é feito definindo o label como `-100` nas posições a ignorar, uma convenção que a função de loss lê como "pule". Para o instruction tuning, apenas a completion costuma ser o que você quer: você está ensinando respostas, e não ensinando o modelo a imaginar perguntas de usuários.

**3. Backward pass.** Percorra o grafo de trás para a frente aplicando a regra da cadeia, produzindo para cada parâmetro treinável um **gradiente**: a direção e a magnitude com que aquele parâmetro deve mudar para reduzir a loss. Um gradiente por parâmetro treinável, com o mesmo formato do próprio parâmetro. Lembre-se disso; é metade da Lição 6.

**4. Passo do otimizador.** Atualize os parâmetros usando os gradientes. O gradient descent puro seria `w ← w − lr · g`. Ninguém usa isso. O **AdamW** mantém duas médias móveis por parâmetro:

| Estado | Acompanha | Efeito |
|---|---|---|
| Primeiro momento | Média dos gradientes recentes | Momentum, suaviza direções ruidosas |
| Segundo momento | Média dos gradientes recentes ao quadrado | Escala do passo por parâmetro |

Dois tensores extras, cada um do tamanho dos parâmetros. Essa é a outra metade da Lição 6, e é o motivo pelo qual o full fine-tuning é tão caro.

### Learning rate e schedule

O learning rate escala o passo. Alto demais e a atualização passa do ponto, destruindo a estrutura pré-treinada. É assim que o esquecimento catastrófico se parece mecanicamente. Baixo demais e nada se move.

Dois refinamentos padrão:

- **Warm-up:** comece perto de zero e suba ao longo das primeiras centenas de passos, para que os gradientes ruidosos do início não arruínem os pesos.
- **Decaimento:** reduza a taxa ao longo do treinamento, em geral em uma curva cosseno, para que os passos finais refinem em vez de se debater.

O fine-tuning com adapters tolera learning rates de uma a duas ordens de grandeza maiores do que o full fine-tuning, normalmente em torno de `1e-4` a `2e-4` em vez de `1e-5`. A Lição 9 explica por quê.

### Batch size, real e efetivo

Os gradientes são calculados como média sobre um batch. Batches maiores dão gradientes menos ruidosos, mas custam proporcionalmente mais memória de ativações. O **gradient accumulation** compra a média sem a memória: execute vários batches pequenos, some os gradientes, dê um único passo.

```text
effective batch size = per_device_batch_size × gradient_accumulation_steps × num_devices
```

Reporte e raciocine com o número efetivo. Uma execução com batch size 1 e 16 passos de acumulação é uma execução de batch 16, e compará-la com uma execução de batch 1 como se fossem equivalentes é um jeito comum de tirar uma conclusão falsa.

### Um epoch não é uma unidade de aprendizado

Um epoch é uma passada pelo dataset. Em um dataset pequeno de instruções, de dois a três epochs é uma faixa típica e mais do que isso costuma memorizar. O número de *passos* é o que o otimizador vê, e os passos dependem do tamanho do dataset e do batch size efetivo em conjunto, então "3 epochs" significa algo completamente diferente em 500 exemplos e em 500.000.

## Prática

1. ▢ Por que o treinamento precisa de muito mais memória do que a inferência, mesmo com o mesmo batch size e o mesmo comprimento de sequência?

<details markdown="1"><summary>Verificação</summary>

O treinamento precisa manter as ativações do forward pass para que o backward pass possa calcular os gradientes, e precisa armazenar os gradientes e o estado do otimizador. A inferência descarta os intermediários de cada camada assim que a camada seguinte os consumiu.

</details>

2. ▢ Você está fazendo fine-tuning em pares de pergunta e resposta. A loss deve ser calculada sobre a sequência inteira ou só sobre a resposta? Dê a consequência da escolha errada.

<details markdown="1"><summary>Verificação</summary>

Só sobre a resposta, na maioria dos casos. Pontuar o prompt também gasta capacidade ensinando o modelo a gerar perguntas plausíveis de usuários, o que não é a tarefa, e dilui o sinal do gradiente na parte que importa para você.

A exceção é quando os prompts são muito estilizados e você quer que o modelo internalize em geral a linguagem do domínio. Decida de propósito; não deixe o padrão decidir por você.

</details>

3. ▢ O AdamW armazena quantos tensores extras por parâmetro treinável, e quais são?

<details markdown="1"><summary>Verificação</summary>

Dois: uma média móvel dos gradientes (primeiro momento) e uma média móvel dos gradientes ao quadrado (segundo momento). Cada um tem o mesmo formato do parâmetro.

Mais o próprio gradiente, que é um terceiro tensor do mesmo formato mas não é estado do otimizador. Manter essas três coisas distintas é exatamente o que a Lição 6 pede que você faça.

</details>

4. ▢ Execução A: batch size 8, acumulação 1. Execução B: batch size 1, acumulação 8. Mesmos dados, mesma seed, mesmo learning rate. Os passos do otimizador são equivalentes?

<details markdown="1"><summary>Verificação</summary>

Na prática sim: as duas calculam a média dos gradientes sobre 8 exemplos antes de dar o passo, então a atualização é essencialmente a mesma, e a B usa muito menos memória de ativações. Restam pequenas diferenças vindas de como o padding e a normalização por batch interagem.

O gradient accumulation é a forma padrão de obter um batch efetivo grande com memória limitada. O que *não* é equivalente é comparar a B com uma execução genuína de batch 1, que dá passos oito vezes mais frequentes sobre gradientes mais ruidosos.

</details>

5. ▢ Um colega define o learning rate de uma execução de LoRA como `1e-5` "porque é o que o full fine-tuning usa". O que você espera, e o que você diz?

<details markdown="1"><summary>Verificação</summary>

Espere underfitting: a loss cai devagar, o modelo mal muda, e a execução parece uma evidência de que o método não funciona.

Os adapters começam com contribuição zero e guardam uma fração minúscula dos parâmetros, então precisam de uma taxa muito maior para se mover, normalmente `1e-4` a `2e-4`. Importar o learning rate de um full fine-tuning é um dos motivos mais comuns para uma primeira execução de LoRA decepcionar.

</details>

6. ▢ Por que o warm-up é mais do que uma superstição?

<details markdown="1"><summary>Verificação</summary>

No início do treinamento, a estimativa de segundo momento do AdamW é construída a partir de pouquíssimas amostras, então sua escala por parâmetro não é confiável e pode produzir passos enormes. Subir o learning rate gradualmente limita o dano que esses primeiros passos podem causar nos pesos pré-treinados.

</details>

## Prática no mundo real

- [ ] Escreva de memória as quatro operações de um passo de treinamento e depois confira com esta lição.
- [ ] Pegue qualquer script de fine-tuning publicado e identifique o seu batch size efetivo, learning rate, warm-up e schedule. Anote os quatro números.
- [ ] Amanhã: encontre uma configuração de treinamento em que você discorde de um desses quatro números e escreva uma frase sobre o que você mudaria e por quê.

## Para ir além

- [Artigo científico: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- [Artigo científico: "Adam: A Method for Stochastic Optimization", Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [Artigo: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Orçamento de memória](../reference/memory-budget.md): a etapa 2 transforma esses quatro passos em bytes

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
