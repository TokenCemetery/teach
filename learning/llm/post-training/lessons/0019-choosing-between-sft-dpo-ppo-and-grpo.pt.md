---
title: "19. Escolhendo entre SFT, DPO, PPO e GRPO"
description: "Cada método só merece o custo adicional em relação ao anterior quando o mais barato genuinamente não consegue expressar o comportamento-alvo"
type: lesson
---

# Lição 19. Escolhendo entre SFT, DPO, PPO e GRPO

**Ligação com a missão:** "Dados os dados, o orçamento e o comportamento-alvo de uma equipe, escolher entre SFT sozinho, DPO, RLHF-PPO e GRPO, e defender a escolha contra a rejeitada" é a decisão central da missão, e esta lição é onde a contabilidade de custos de todo o arco é montada em um único framework.
**Fonte principal:** [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Pré-requisitos:** [Lição 18](0018-reward-hacking-after-the-fact.md)

## Aquecimento

1. ▢ O que é a recusa excessiva, e por que um benchmark red-team só de prompts inseguros não consegue detectá-la?

<details markdown="1"><summary>Verificação</summary>

Um modelo recusar um prompt que na verdade é seguro. Um benchmark red-team construído apenas com prompts inseguros não tem prompts seguros que possam ser recusados indevidamente, então não consegue fazer emergir essa falha específica.

</details>

2. ▢ O que é o viés do juiz, e o que o `llm/evals` recomenda checar antes de confiar em uma diferença de pontuação que ele produziu?

<details markdown="1"><summary>Verificação</summary>

Uma distorção sistemática na pontuação de um juiz LLM, como favorecer respostas mais longas ou a resposta mostrada primeiro. O `llm/evals` recomenda checar a calibração do juiz contra esses vieses conhecidos antes de confiar em uma diferença de pontuação como evidência de melhora genuína.

</details>

## Saiba isto

### Cada método custa mais do que o anterior, por uma razão

As quatro abordagens de treinamento desta trilha formam uma escada aproximada, em que cada uma acrescenta custo apenas onde a anterior genuinamente fica sem poder expressivo para o comportamento-alvo:

**O SFT sozinho (etapa 2)** é o mais barato: sem dados de preferência, sem reward model, sem loop de RL, apenas imitando diretamente exemplos demonstrados. Ele basta exatamente quando o comportamento-alvo pode ser totalmente especificado mostrando exemplos dele: um formato de resposta fixo, uma habilidade restrita e bem definida, uma mudança de estilo. Todo método posterior dessa escada ainda parte de um modelo SFT; a pergunta que esta lição realmente faz é até onde, além do SFT, um dado comportamento precisa ir.

**O DPO (etapa 5)** merece o custo adicional em relação ao SFT sozinho quando o comportamento desejado não pode ser totalmente especificado por demonstração direta, mas *pode* ser especificado comparando duas saídas candidatas, "esta em vez daquela". Rafailov et al. constroem o DPO especificamente para chegar a um modelo treinado com preferências a um custo próximo ao do próprio SFT: sem reward model separado, sem função de valor, sem loop de amostragem de RL, apenas a policy e um modelo de referência congelado (lição 10). Se há dados de preferência disponíveis ou coletáveis e nenhuma razão específica para precisar de um reward model independente e reutilizável, o DPO é o próximo passo natural além do SFT, e não o RLHF-PPO.

**O RLHF-PPO (etapa 4)** merece o seu custo substancialmente maior (a configuração de quatro ou cinco modelos da lição 8) especificamente quando vale a pena ter um reward model independente por si só: reutilizado para pontuar saídas fora da policy que treinou contra ele, inspecionado de forma independente ou iterado repetidamente conforme mais comparações chegam sobre a melhor policy atual, como o pipeline original de três passos da lição 1 descreve. Escolher o PPO em vez do DPO sem uma dessas razões é pagar por uma maquinaria que um método mais simples já cobre.

**O GRPO (etapa 6)** conquista o seu lugar por uma porta totalmente diferente: as recompensas verificáveis. Onde o DPO e o PPO precisam ambos de julgamentos de preferência, humanos ou de IA, a vantagem relativa ao grupo do GRPO funciona com qualquer pontuação por saída, inclusive a saída de um verificador determinístico (lição 12), o que elimina a necessidade de um reward model treinado ou de dados de preferência humana em tarefas como matemática e código, em que a correção é verificável. O GRPO não é um PPO mais barato em geral; é a ferramenta certa especificamente quando a tarefa fornece uma recompensa verificável que o PPO ou o DPO teriam de aproximar com um julgamento treinado.

### Defendendo uma alternativa rejeitada, e não apenas uma escolha

"Defender a escolha contra a rejeitada", a formulação da própria missão, significa nomear qual método mais barato foi tentado ou considerado primeiro e por que ele ficou aquém, e não simplesmente afirmar os benefícios do método escolhido. Uma equipe que escolhe o PPO deveria ser capaz de dizer por que a recompensa implícita do DPO não bastou, especificamente (precisar de um reward model reutilizável, na maioria das vezes). Uma equipe que escolhe o GRPO deveria ser capaz de apontar a checagem verificável de que a sua recompensa é construída, e não simplesmente citar os resultados do DeepSeek-R1 como licença para usá-lo em uma tarefa sem nenhuma checagem desse tipo disponível.

## Prática

1. ▢ Uma equipe quer um modelo que sempre responda em um schema JSON fixo para uma tarefa restrita e bem definida. Qual método dessa escada é o ponto de partida certo, e por quê?

<details markdown="1"><summary>Verificação</summary>

O SFT sozinho. Esse é exatamente o caso que um comportamento fixo e totalmente demonstrável comporta: exemplos do formato correto bastam para imitar diretamente, sem nenhuma necessidade de dados de preferência nem de sinal de recompensa.

</details>

2. ▢ Uma equipe tem dados de preferência (pares de saídas com uma marcada como melhor) e nenhuma necessidade específica de reutilizar um reward model fora da própria execução de treinamento. Qual entre DPO e PPO é o padrão mais defensável, e por quê?

<details markdown="1"><summary>Verificação</summary>

O DPO. Ele chega a um resultado semelhante, treinado com preferências, a um custo próximo ao do próprio SFT, precisando apenas da policy e de um modelo de referência congelado, sem reward model separado nem loop de RL a justificar, a menos que algo específico exija um.

</details>

3. ▢ Uma equipe está treinando um modelo para resolver problemas de programação competitiva, em que um compilador pode checar se o código gerado passa em uma suíte de testes fixa. Qual método combina particularmente bem com essa tarefa, e o que, especificamente, faz dele uma boa escolha?

<details markdown="1"><summary>Verificação</summary>

O GRPO, combinado com uma recompensa verificável: o resultado de passa/falha do compilador na suíte de testes é exatamente o tipo de pontuação determinística e checável que a vantagem relativa ao grupo do GRPO pode usar diretamente, sem nenhum reward model treinado nem dados de preferência humana.

</details>

4. ▢ Uma equipe escolhe o RLHF-PPO em vez do DPO, citando apenas "o PPO é o método mais estabelecido". Segundo esta lição, isso é uma defesa suficiente da escolha?

<details markdown="1"><summary>Verificação</summary>

Não. Defender uma escolha contra a rejeitada significa nomear uma razão específica pela qual a abordagem mais barata do DPO não teria bastado, como precisar de um reward model independente para reutilizar ou iterar. Citar apenas que o PPO é estabelecido não identifica o que o DPO especificamente não tinha para essa tarefa.

</details>

## Prática no mundo real

- [ ] Encontre um relatório técnico de pós-treinamento publicado e identifique qual entre SFT, DPO, PPO ou GRPO ele usou, e se ele declara uma razão para essa escolha em vez de uma alternativa mais barata.
- [ ] Para uma tarefa com a qual você esteja familiarizado (do trabalho, de um projeto ou hipotética), passe-a pela escada desta lição um degrau por vez: o SFT sozinho bastaria e, se não, por quê; o DPO bastaria e, se não, por quê.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 20: dado que o arco desta trilha cobriu seis decisões distintas (mascaramento de dados, design de recompensa, trocas do KL, vantagem relativa ao grupo, recompensas verificáveis, medição do alignment tax), o que revisar a receita de alinhamento já pronta de outra pessoa precisaria de fato checar, etapa por etapa?

## Para ir além

- [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
