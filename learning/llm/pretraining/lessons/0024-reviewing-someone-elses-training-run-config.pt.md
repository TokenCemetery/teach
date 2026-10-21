---
title: "24. Revisando a configuração de execução de treinamento de outra pessoa"
description: "Percorrer o plano por todas as etapas que esta trilha cobriu, em ordem, e resolver uma alegação contestada a partir da fonte e não de um post de blog"
type: lesson
---

# Lição 24. Revisando a configuração de execução de treinamento de outra pessoa

**Ligação com a missão:** Esta lição fecha o arco. Cada etapa anterior produziu uma coisa a conferir no plano de outra pessoa; esta lição é o checklist, mais a disciplina de resolver uma alegação técnica contestada a partir de uma fonte primária em vez de confiar em qualquer relato secundário que seja mais conveniente.
**Fonte principal:** [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Pré-requisitos:** todas as lições anteriores desta trilha, já que esta é a síntese.

## Aquecimento

1. ▢ Nomeie as quatro categorias de afirmação em que a Lição 23 diz que um plano de pré-treinamento defensável deve ser dividido.

<details markdown="1"><summary>Verificação</summary>

A razão tokens por parâmetro, o pipeline de dados, o plano de paralelismo casado com a interconexão do hardware e o plano de estabilidade e monitoramento.

</details>

2. ▢ Segundo a Lição 22, nomeie uma razão legítima para pré-treinar do zero em vez de adaptar um modelo existente.

<details markdown="1"><summary>Verificação</summary>

Qualquer uma entre: o idioma ou domínio-alvo está tão distante da cobertura de todos os modelos base disponíveis que a adaptação não consegue fechar a distância, um requisito de licenciamento ou de proveniência descarta todos os modelos base disponíveis ou uma mudança deliberada de arquitetura para a qual um checkpoint existente não pode ser adaptado.

</details>

## Saiba isto

### O checklist de revisão: as etapas em ordem

Ao revisar um plano de pré-treinamento proposto ou existente, percorra-o pelas etapas desta trilha em ordem, fazendo a mesma pergunta em cada uma: esta escolha é declarada e justificada, ou apenas suposta?

**Etapas 1 e 2, dados e tokenizer.** A obtenção e a mistura do corpus são uma decisão explícita e defendida (Lição 1), com a deduplicação e a filtragem de qualidade de fato aplicadas e descritas (Lição 2), em vez de "o que conseguimos coletar"? O tamanho do vocabulário do tokenizer é uma escolha declarada, ponderada contra o comprimento das sequências e o custo da tabela de embeddings (Lição 4), em vez de um padrão herdado de um projeto sem relação?

**Etapa 3, a razão.** Calcule diretamente a razão tokens por parâmetro do plano e compare-a com a faixa de aproximadamente 20 a 25 que a Lição 6 fundamentou nos próprios resultados do Chinchilla. Um plano bem fora dessa faixa, em qualquer direção, não está automaticamente errado, mas é uma afirmação que precisa da sua própria razão declarada, o mesmo teste que a Lição 23 aplicou.

**Etapas 4 a 6, paralelismo.** A estratégia de particionamento (estágio do ZeRO ou equivalente) corresponde à memória que o modelo de fato precisa, segundo a contabilidade por parâmetro da Lição 8? Alguma divisão de paralelismo de tensor fica dentro da interconexão rápida de um único nó e o paralelismo de pipeline carrega o peso de atravessar nós, segundo o raciocínio da própria Lição 14, e não o contrário?

**Etapas 7 a 9, executando.** O plano declara uma escolha de precisão e, se usa parâmetros em bf16, se é usado stochastic rounding ou uma cópia mestra em fp32 (Lição 15)? Declara um valor de gradient clipping e esse valor se aperta para os maiores modelos que o plano treina, como o do próprio Gopher (Lição 16)? Declara uma frequência de checkpoint defensável contra a taxa de falha que a evidência da etapa 8 mostrou ser normal, e não excepcional, nessa escala (Lição 18)? Inclui avaliação held-out periódica, e não apenas a loss de treinamento, como forma de pegar problemas cedo (Lição 21)?

**Etapa 10, a própria decisão.** O plano explica por que o pré-treinamento continuado ou o fine-tuning de um modelo existente não teria servido ao objetivo declarado (Lição 22), antes de defender o orçamento do zero nos seus próprios termos (Lição 23)?

Um plano que responde a tudo isso com uma escolha declarada e defensável é um plano que fez o trabalho que esta trilha descreve. Um plano que responde a vários desses pontos com silêncio não fez, qualquer que seja a aparência da sua estimativa final de custo.

### Resolvendo uma alegação contestada a partir da fonte, e não de um post de blog

Vale percorrer diretamente uma confusão específica e comum, porque ela mostra a disciplina de que esta lição realmente trata. Às vezes se afirma online que "o bf16 exige loss scaling, assim como o fp16". Isso é dito com confiança em fontes secundárias suficientes para parecer algo resolvido. Mas a Lição 15 traçou por que o bf16 mantém os 8 bits de expoente completos do fp32, dando-lhe o mesmo intervalo dinâmico do fp32; o loss scaling (multiplicar os valores para cima antes de armazená-los em um formato de intervalo estreito e para baixo antes da atualização, para evitar underflow) é especificamente uma mitigação do intervalo de expoente mais estreito de 5 bits do fp16, exatamente o problema que o intervalo mais largo do bf16 foi construído para evitar. O próprio relato de Rae et al. sobre o treinamento do Gopher não descreve loss scaling para as suas ativações em bf16; a preocupação numérica que eles descrevem e tratam para o bf16 é o stochastic rounding nas atualizações de parâmetros, um problema diferente (de precisão, e não de intervalo) com uma solução diferente. Uma fonte secundária que repete "o bf16 também precisa de loss scaling" está confundindo dois problemas diferentes de dois formatos diferentes; voltar ao que uma fonte primária realmente descreve que cada formato precisa, em vez de confiar em uma reafirmação confiante, é o que pega essa confusão. Esse é o hábito que vale levar para fora desta trilha: quando dois relatos discordam, ou um relato afirma algo suspeitosamente próximo do que uma lição anterior traçou, mas não exatamente igual, é a fonte primária que resolve, e não o relato lido primeiro ou o que soou mais confiante.

## Prática

1. ▢ Um plano de treinamento propõe um modelo de 50 bilhões de parâmetros treinado com 400 bilhões de tokens, usando o estágio 2 do ZeRO em 16 dispositivos divididos em 2 nós de 8, com o paralelismo de tensor definido com tamanho 16 (atravessando os dois nós). Nomeie duas coisas nesse plano que valem ser contestadas, usando o checklist desta lição.

<details markdown="1"><summary>Verificação</summary>

A razão (`400 / 50 = 8` tokens por parâmetro) está bem abaixo da faixa compute-optimal de aproximadamente 20 a 25, e vale perguntar se isso é uma escolha deliberada e justificada. O tamanho de paralelismo de tensor de 16, atravessando os dois nós em vez de ficar dentro de um único nó de 8 GPUs, contradiz o raciocínio da própria Lição 14 de que o all-reduce frequente do paralelismo de tensor pertence à interconexão rápida de um único nó, com o paralelismo de pipeline (e não o de tensor) carregando a divisão entre nós.

</details>

2. ▢ Um colega afirma "o bf16 precisa de loss scaling, assim como o fp16, já que os dois são formatos de 16 bits". Usando o exemplo trabalhado desta lição, qual é a resposta real e o que especificamente está sendo confundido?

<details markdown="1"><summary>Verificação</summary>

O bf16 não precisa de loss scaling do jeito que o fp16 precisa. O loss scaling trata do intervalo de expoente estreito de 5 bits do fp16 que causa underflow; o bf16 mantém o intervalo de expoente completo de 8 bits do fp32, que é o problema específico que o loss scaling existe para contornar, então o bf16 não tem esse problema para começo de conversa. A afirmação do colega confunde as larguras de bits dos dois formatos (ambos com 16 bits no total) com a diferença real do intervalo de expoente, que é o que determina se o loss scaling é necessário.

</details>

3. ▢ Um plano declara apenas uma única cifra de custo total de compute, sem detalhamento de razão, pipeline de dados, plano de paralelismo ou plano de estabilidade. Segundo a Lição 23 e esta lição, esse plano é revisável como declarado?

<details markdown="1"><summary>Verificação</summary>

Na verdade não: um único número agrupado convida apenas "dá para ficar mais barato" e esconde quais afirmações subjacentes são bem sustentadas e quais são suposições não examinadas. Uma revisão adequada precisa do plano dividido nas categorias que o checklist desta lição percorre, para que cada uma possa ser conferida nos seus próprios termos.

</details>

## Prática no mundo real

- [ ] Encontre uma configuração de pré-treinamento real e publicada (um relatório técnico, o arquivo de configuração de um script de treinamento ou um model card) e passe-a pelo checklist desta lição, etapa por etapa, anotando quais itens são declarados explicitamente e quais ficam em silêncio.
- [ ] Encontre uma afirmação sobre pré-treinamento de LLMs feita com confiança em um post de blog ou resposta de fórum e confira-a contra a fonte primária real a que ela deveria remontar (um artigo que esta trilha cita ou outro que você localize). Anote se ela se sustenta, se é uma simplificação ou se é uma confusão genuína como o exemplo do bf16 desta lição.
- [ ] Amanhã: escreva uma revisão curta, de três a cinco frases, de um plano de pré-treinamento real ou hipotético, nomeando pelo menos uma escolha específica que você contestaria e o que pediria que a pessoa que a defende justificasse.

## Para ir além

- [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
