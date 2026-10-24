---
title: Trilhas de aprendizado
description: Todos os tópicos deste repositório, agrupados por domínio
type: index
---

# Trilhas de aprendizado

Agrupadas por domínio, um diretório por tópico. Cada tópico é uma trilha autocontida conduzida pela skill `teach`: uma missão, um conjunto ordenado de lições e o material de referência que essas lições conquistaram.

## Tópicos

| Domínio | Tópico | Missão | Lições |
|---|---|---|---|
| programming | [Bash](programming/bash/) | Escreva shell que sobrevive à produção: quoting, exit status, os modos de falha e saber quando parar e usar uma linguagem de verdade | 17 |
| programming | [C#](programming/csharp/) | Domine um serviço em C#: o sistema de tipos, async e o que o CLR faz com o que você escreveu | 45 |
| programming | [Go](programming/golang/) | Seja o dono de Go em um time: projete, entregue e opere um serviço de produção | 41 |
| programming | [Java](programming/java/) | Domine um serviço em Java: modele-o em Java moderno e depois opere o que a JVM faz com ele | 52 |
| programming | [Kotlin](programming/kotlin/) | Domine Kotlin na JVM: null safety, coroutines e onde o hábito de Java produz Kotlin que compila e se lê mal | 44 |
| programming | [Python](programming/python/) | Domine Python em produção: entregue-o tipado, testado, empacotado e perfilado | 44 |
| programming | [Rust](programming/rust/) | Domine Rust: projete com ownership em vez de brigar com o borrow checker, depois publique o crate | 67 |
| programming | [SQL](programming/sql/) | Domine o banco de dados: escreva a consulta, leia o plano, projete o schema, sobreviva à concorrência | 53 |
| programming | [TypeScript](programming/typescript/) | Domine uma codebase TypeScript: faça o compilador rejeitar os estados que não deveriam existir | 49 |
| llm | [Fine-Tuning com Adapters](llm/finetuning/) | Decida se vale a pena fazer fine-tuning, execute, prove que funcionou e coloque em produção | 27 |
| llm | [Pré-treinamento](llm/pretraining/) | Treine um modelo do zero em escala: dados, tokenizer, treinamento distribuído e um orçamento de compute defensável | 24 |
| llm | [Pós-treinamento](llm/post-training/) | Alinhe um base model: SFT, modelagem de recompensa, RLHF, DPO e GRPO, e saiba qual escolher | 20 |
| llm | [Inferência](llm/inference/) | Sirva um modelo: o KV cache, o batching, a quantização no serving e um orçamento de latência que você consegue defender | 24 |
| llm | [Evals](llm/evals/) | Prove que uma mudança no modelo ajudou: construa o eval, mantenha os dados held-out com honestidade e defenda o número contra a contaminação | 18 |
| llm | [RAG](llm/rag/) | Domine a recuperação: chunking, embeddings, busca híbrida, reranking e a medição de se a coisa certa foi recuperada | 19 |
| llm | [Transformers](llm/transformers/) | Construa a atenção do zero, para que a arquitetura deixe de ser uma caixa-preta por trás do script de treinamento | 22 |
| llm | [Agentes](llm/agents/) | Construa o loop você mesmo: ferramentas, contexto, memória e saber quando um agente é a resposta errada | 37 |
| llm | [Quantização](llm/quantization/) | Quantize um LLM e defenda o resultado: formatos numéricos, métodos de PTQ e QAT, o que roda mais rápido e como medir o que isso custou | 27 |
| llm | [Prompting](llm/prompting/) | Escreva, versione e publique prompts para um recurso baseado em LLM, prove que uma mudança de prompt ajudou e revise o prompt de produção de outra pessoa | 24 |
| llm | [Destilação](llm/distillation/) | Destile um modelo grande em um menor e defenda o resultado: soft targets, losses de logits e em nível de sequência, dados sintéticos, treinamento on-policy e o que o aluno perdeu | 27 |
| data | [Postgres](data/postgres/) | Opere o Postgres: o WAL, vacuum e bloat, replicação e quanto custa manter um índice | 18 |
| data | [Kafka](data/kafka/) | Domine o log: partições, consumer groups, garantias de entrega e quanto "exactly once" realmente custa | 16 |
| data | [Redis](data/redis/) | Use o Redis pelo que ele é: o modelo de memória, eviction, persistência e os padrões que o usam mal em silêncio | 17 |
| architecture | [Sistemas Distribuídos](architecture/distributed-systems/) | Raciocine sobre falha parcial: o que uma rede pode fazer com você, qual consistência você está de fato comprando e por que o consenso é caro | 19 |
| architecture | [Design de APIs](architecture/api-design/) | Projete uma interface da qual outros dependem: o contrato, os seus erros e como ele muda sem quebrá-los | 19 |
| infrastructure | [Contêineres](infrastructure/containers/) | Empacote um serviço como imagem de contêiner e seja dono dela: primitivas do kernel, Dockerfiles, executar, proteger e depurar um contêiner | 24 |
| infrastructure | [Kubernetes](infrastructure/kubernetes/) | Rode serviços em um cluster Kubernetes e seja dono deles: o loop de reconciliação, workloads, rede, configuração, confiabilidade, segurança, empacotamento e depuração | 28 |
| infrastructure | [CI/CD](infrastructure/ci-cd/) | Construa, teste e entregue cada mudança por um pipeline e seja dono dele: workflows, feedback rápido, artefatos, secrets, deployments, rollback e segurança da cadeia de suprimentos | 30 |

## Começando um tópico

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Depois rode a skill `teach` e diga o nome do tópico. Ela lê a trilha, preenche a missão entrevistando você e escreve a primeira lição.

Um domínio é um agrupamento, não uma trilha: ele contém diretórios de tópicos e nada mais. Crie um novo quando um segundo tópico for compartilhá-lo.

## Estrutura

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one track per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

Cada trilha:

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md, one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md, what was demonstrably learned
```

As lições são numeradas a partir de `0001` dentro de cada trilha. As trilhas podem apontar umas para as outras, mas um link é um ponteiro e não uma inclusão: ele não puxa o material de outro tópico para dentro desta missão. Prefira apontar para um termo do glossário ou para uma folha de referência em vez de uma lição, porque eles são escritos para consulta e funcionam para qualquer leitor.

A skill `teach` é dona do formato de todo arquivo aqui. Leia [a especificação dela](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md) antes de escrever um à mão.

## Licença

Tudo neste site está sob [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT). Copie, traduza, ensine a partir dele, construa sobre ele, com fins comerciais ou não. Apenas diga de onde veio.
