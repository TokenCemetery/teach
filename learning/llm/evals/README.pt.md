---
title: "Evals"
description: "Prove que uma mudança no modelo ajudou: construa o eval, mantenha os dados held-out com honestidade e defenda o número contra a contaminação"
type: topic
---

# Aprendizado: Evals

Seja capaz de construir um eval que pega uma regressão que um vibe check deixaria passar e de usá-lo para tomar uma decisão de go/no-go sobre uma mudança no modelo (um fine-tuning, uma mudança de prompt, uma mudança de RAG) que você consiga defender com um número, e não com uma sensação.

**Última lição:** [19. Revisando um relatório de eval](lessons/0019-reviewing-an-eval-report.md)

## O sucesso se parece com isto

- Projetar um conjunto de eval held-out para uma dada mudança no modelo que resista à contaminação e pegue uma regressão que uma leitura casual deixaria passar.
- Usar esse eval para tomar e defender uma decisão de go/no-go sobre lançar a mudança, nomeando o número e por que ele é confiável.
- Comparar uma abordagem de LLM-as-judge com métricas específicas da tarefa para um dado caso, e escolher entre elas pelos méritos, e não por padrão.
- Revisar o relatório de eval ou o harness de outra pessoa e nomear especificamente o que tornaria seu número pouco confiável (um conjunto sem held-out, um juiz não calibrado, uma execução única sem estimativa de variância, uma posição em leaderboard fazendo o papel de uma decisão específica da tarefa), em vez de dizer que ele parece fraco.

## Restrições

- Sem restrição de domínio: cobre a avaliação de fine-tunings, mudanças de prompt e mudanças de RAG por igual, já que a mesma disciplina de eval vale para os três.
- Sem stack fixa nem pressuposição de experiência prévia.

## Fora do escopo

- Julgar uma variante, o design held-out, as métricas e o conjunto de regressão como ensinados dentro de um único arco de fine-tuning: veja [`llm/finetuning`](../../llm/finetuning/) (lições 0020-0024), subordinado especificamente ao fine-tuning. Este workspace é dono da avaliação como assunto e aponta para lá em vez de repetir.
- Quantizar um modelo e julgar o que a quantização custou: veja [`llm/quantization`](../../llm/quantization/). Aquela trilha usa um eval para medir a perda da quantização; esta ensina como o eval é construído.
- Escrever e versionar o prompt sob teste: veja [`llm/prompting`](../../llm/prompting/). Aquela trilha usa um eval para medir uma mudança de prompt; esta ensina como o eval é construído.
- Destilar um modelo menor e medir o que ele perdeu em relação ao seu professor: veja [`llm/distillation`](../../llm/distillation/). Aquela trilha usa um eval para comparar um aluno com seu professor; esta ensina como o eval é construído.

## O arco

Treze etapas, de um eval confiável a uma decisão de go/no-go defendida que leva em conta humanos, segurança, agentes, RAG, produção, custo e a atração de um leaderboard público, terminando com o julgamento para revisar o eval de outra pessoa e manter um com honestidade como infraestrutura compartilhada. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Dados held-out e contaminação | 0001 a 0002 | Disciplina de divisão treino/teste, detecção de contaminação e suas fontes | Consegue projetar um conjunto held-out que resista à contaminação |
| 2. Métricas específicas da tarefa | 0003 a 0004 | Exact match, F1, BLEU/ROUGE, métricas de execução de código, escolha por tarefa | Consegue escolher e justificar uma métrica para uma tarefa declarada |
| 3. LLM-as-judge | 0005 a 0006 | Design de prompt de juiz, calibração, viés de posição e de verbosidade, concordância com humanos | Consegue construir um prompt de juiz e nomear seus modos de falha |
| 4. Construindo o harness | 0007 a 0008 | Frameworks de eval, execuções reproduzíveis, transformar um design em um número | Tem um harness de eval executável que produz um número confiável |
| 5. A decisão de go/no-go | 0009 a 0010 | Significância estatística contra ruído, limiares de regressão, comunicar a decisão | Consegue defender uma decisão de lançar/não lançar com um número e dizer por que ele é confiável |
| 6. Avaliação humana como método | 0011 | Diretrizes de anotação, amostragem para revisão, kappa de Cohen e o que um rótulo humano custa | Consegue medir com precisão a concordância entre avaliadores e diagnosticar um valor baixo |
| 7. Avaliação de segurança e red-teaming | 0012 | Red-teaming, jailbreaks e taxa de sucesso de ataque, recusa excessiva e XSTest | Consegue reportar tanto uma taxa de recusa quanto uma métrica de recusa excessiva, e explicar por que nenhuma das duas sozinha é um eval de segurança |
| 8. Avaliando agentes e uso de ferramentas | 0013 | Trajetórias, sucesso na tarefa contra acurácia por passo, confiabilidade `pass^k` | Consegue explicar por que o sucesso na tarefa vence a comparação de passos, e por que o sucesso em uma única tentativa não é confiabilidade em tentativas repetidas |
| 9. Avaliação específica de RAG | 0014 | Fidelidade/groundedness, correção de citações, separar uma falha de recuperação de uma falha de geração | Consegue medir fidelidade e correção de citações de forma independente, e diagnosticar de que lado de um pipeline de RAG a falha realmente ocorreu |
| 10. Avaliação online | 0015 a 0016 | Testes A/B, OEC e métricas guardrail, telemetria de produção, drift, training-serving skew | Consegue escolher um OEC defensável com uma métrica guardrail, e atribuir corretamente uma diferença offline/online a variância, drift ou um erro de engenharia |
| 11. Custo e latência como dimensões de eval | 0017 | Latência de cauda contra média, custo por requisição/token, incorporar ambos à decisão de go/no-go | Consegue defender uma decisão de go/no-go que pese qualidade, latência de cauda e custo juntos, e não só a qualidade |
| 12. Benchmarks públicos | 0018 | Contaminação/saturação de benchmarks estáticos, divulgação seletiva no estilo de arena, viés de estilo em escala de leaderboard | Consegue explicar por que a posição em um leaderboard falha no teste do OEC e não substitui uma decisão de go/no-go específica da tarefa |
| 13. Julgamento | 0019 | Revisar relatórios de eval, resolver afirmações disputadas a partir de fontes primárias, manter uma suíte de evals de que outros dependem | Tem a confiança para revisar o eval de outra pessoa e defender seu número ou nomear o que o torna pouco confiável, e para manter uma suíte de evals como infraestrutura compartilhada sem quebrar os portões de outras pessoas |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-held-out-and-contamination.md) | Dados held-out e contaminação | Por que um número de eval só é tão confiável quanto aquilo que o modelo nunca viu |
| [0002](lessons/0002-designing-contamination-resistance.md) | Projetando resistência à contaminação | Prevenir a contaminação em um conjunto de eval customizado desde o início, em vez de apenas detectá-la depois do fato |
| [0003](lessons/0003-task-specific-metrics.md) | Métricas específicas da tarefa | Exact match, F1 em nível de token e BLEU/ROUGE, e o modo de falha de cada um |
| [0004](lessons/0004-code-execution-metrics.md) | Métricas de execução de código e a escolha de uma métrica | Correção funcional, o estimador pass@k e um princípio de decisão para escolher uma métrica por tarefa |
| [0005](lessons/0005-judge-prompt-design-and-calibration.md) | Design e calibração de prompt de juiz | Como escrever um prompt de juiz que avalie de forma consistente, e o que significa um juiz estar calibrado antes de confiar nele |
| [0006](lessons/0006-judge-bias-and-human-agreement.md) | Viés do juiz e concordância com humanos | Viés de posição e viés de verbosidade no LLM-as-judge, e como medir a concordância de um juiz com avaliadores humanos |
| [0007](lessons/0007-eval-frameworks-and-harness.md) | Frameworks de eval e construção de um harness | As quatro etapas que todo harness de eval tem, e a escolha entre construir um eval-as-code customizado e reaproveitar um harness de benchmark padronizado |
| [0008](lessons/0008-reproducible-runs.md) | Execuções reproduzíveis | Por que o mesmo eval pode produzir números diferentes em execuções diferentes, e o que um resultado confiável precisa registrar junto com a pontuação |
| [0009](lessons/0009-statistical-significance-vs-noise.md) | Significância estatística contra ruído | Por que uma diferença de pontuação precisa ser medida contra o ruído que poderia produzi-la por acaso, e por que a comparação pareada vence tratar duas pontuações como independentes |
| [0010](lessons/0010-defending-the-go-no-go-call.md) | Defendendo a decisão de go/no-go | Como definir um limiar de regressão com honestidade, e tudo o que uma defesa completa de go/no-go precisa citar |
| [0011](lessons/0011-human-evaluation-as-a-method.md) | Avaliação humana como método | A lição 6 mediu um juiz contra avaliadores humanos sem nunca ensinar como uma avaliação humana é de fato produzida, e o número de concordância bruta em que ela se apoiou precisa de sua própria correção pelo acaso antes de significar alguma coisa |
| [0012](lessons/0012-safety-and-red-teaming-evaluation.md) | Avaliação de segurança e red-teaming | Um eval de segurança que mede apenas com que frequência um modelo recusa prompts genuinamente inseguros está medindo metade de um trade-off, já que o mesmo ajuste que eleva esse número pode muito bem elevar a frequência com que o modelo recusa prompts que nunca foram inseguros |
| [0013](lessons/0013-evaluating-agents-and-tool-use.md) | Avaliando agentes e uso de ferramentas | Uma tarefa de agente tem muitos caminhos válidos para o mesmo resultado correto, então pontuá-la contra uma única sequência de ações de referência repete o erro do exact match em escala de trajetória, e até a taxa de sucesso de uma única tentativa esconde com que frequência o mesmo agente falha na mesma tarefa em uma segunda tentativa |
| [0014](lessons/0014-rag-specific-evaluation.md) | Avaliação específica de RAG | O llm/rag traçou a linha entre uma falha de recuperação e uma falha de geração, mas deixou indefinida a verificação do lado da geração, e essa verificação acaba precisando de dois números separados, e não de um, já que uma afirmação fiel e uma afirmação corretamente citada podem falhar de forma independente uma da outra |
| [0015](lessons/0015-ab-tests-and-guardrail-metrics.md) | Testes A/B e métricas guardrail | Toda etapa até aqui foi offline, mas lançar para usuários reais exige sua própria métrica de decisão, e essa métrica sozinha é tão perigosa quanto os números de segurança isolados contra os quais etapas anteriores já alertaram |
| [0016](lessons/0016-production-telemetry-and-drift.md) | Telemetria de produção e drift | Um número offline e um número ao vivo discordarem não é um problema, são três problemas diferentes, e tratar um bug de engenharia como drift, ou drift como um bug de engenharia, manda a correção para a equipe errada |
| [0017](lessons/0017-cost-and-latency-as-eval-dimensions.md) | Custo e latência como dimensões de eval | Um ganho de qualidade medido isolado do que custa servi-lo é metade de uma decisão de go/no-go, e um número de latência média esconde exatamente a cauda que determina se os usuários de fato percebem o sistema como rápido |
| [0018](lessons/0018-public-benchmarks.md) | Benchmarks públicos | Uma posição em leaderboard é uma métrica movível otimizada por pessoas que não são você, para usuários que não são os seus, pontuada por um processo com seus próprios vetores de manipulação documentados, o que a torna exatamente o tipo de métrica contra o qual a lição 15 alertou como sinal de go/no-go |
| [0019](lessons/0019-reviewing-an-eval-report.md) | Revisando um relatório de eval | Nomeie especificamente o que tornaria pouco confiável o número de um relatório de eval (contaminação, um juiz não calibrado, uma execução única sem estimativa de variância, uma posição em leaderboard fazendo o papel de uma decisão específica da tarefa), em vez de dizer que ele parece fraco |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Dados Held-Out e Contaminação](reference/held-out-data-and-contamination.md): os dois caminhos da contaminação, o teste de instrução guiada e o kit de prevenção para um conjunto de eval customizado
- [Métricas](reference/metrics.md): exact match, F1, BLEU/ROUGE e pass@k lado a lado, com a fórmula do pass@k e o princípio de decisão para escolher entre eles
- [LLM-as-Judge](reference/llm-as-judge.md): o checklist de design de prompt de juiz, calibração e compressão de pontuação, viés de posição e de verbosidade, e o patamar de concordância humano contra humano
- [Harness de Eval](reference/eval-harness.md): o pipeline de quatro etapas, openai/evals contra lm-evaluation-harness, e o que um número defensável registra junto com a pontuação
- [Go/No-Go](reference/go-no-go.md): a fórmula do erro padrão, comparação pareada, definir um limiar com honestidade e tudo o que uma defesa completa cita

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
