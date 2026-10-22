---
title: "O Que o Aluno Herda"
description: "Fidelidade, a lacuna de imitação, a lacuna de capacidade e os traços não intencionais, com o cenário e os números de cada fonte"
type: reference
---

# O Que o Aluno Herda: Fidelidade, a Lacuna de Imitação, a Lacuna de Capacidade e os Traços Ocultos

A etapa 6 condensada para consulta. A [lição 17](../lessons/0017-fidelity-and-generalization.md) cobre fidelidade contra generalização, a [lição 18](../lessons/0018-the-imitation-gap.md) a lacuna de imitação, e a [lição 19](../lessons/0019-capacity-gap-and-hidden-traits.md) a lacuna de capacidade e os traços ocultos.

## Quatro maneiras de um aluno diferir do seu professor

| Lacuna | O que difere | Fonte | Cenário |
|---|---|---|---|
| Fidelidade | Previsões nas mesmas entradas, mesmo quando a acurácia é parecida | Stanton et al., 2021 | Classificação de imagens, com MNIST, CIFAR-100, ImageNet e sentimento do IMDB no apêndice |
| Imitação | Estilo copiado rápido, capacidade não | Gudibande et al., 2023 | Alunos LLaMA e GPT-2 imitando o ChatGPT |
| Capacidade | Um professor muito grande pode dar um aluno pior | Mirzadeh et al., 2019, e Cho e Hariharan, 2019 | CNNs e ResNets no CIFAR e no ImageNet |
| Traços ocultos | Um traço passa por dados que não o mencionam | Cloud et al., 2025 | Família GPT-4.1 e Qwen2.5-7B, mais um pequeno caso do MNIST |

Apenas duas das quatro foram testadas em modelos de linguagem, e nenhuma das evidências de lacuna de capacidade aqui é de LLMs.

## Medindo a fidelidade

| Métrica | Definição | Precisa de |
|---|---|---|
| Concordância top-1 | Fração das entradas em que aluno e professor escolhem o mesmo rótulo de topo | As previsões do professor |
| KL preditivo | KL(professor, aluno) médio sobre as entradas | A distribuição completa do professor |
| Controle | Um segundo aluno destilado do mesmo modo a partir de um professor independente | Uma segunda execução de destilação |

A acurácia não limita a concordância de forma justa. Com acurácia do professor de 93% e do aluno de 91%, a concordância fica entre 84% e 98%.

## Stanton et al. em números

| Observação | Número ou direção |
|---|---|
| LeNet-5 no MNIST com dados suficientes | Mais de 99% de concordância top-1 no teste |
| Autodestilação do ResNet-56 no CIFAR-100, maior conjunto | Concordância no teste abaixo de 80% |
| O mesmo, com 50 mil imagens de GAN acrescentadas, concordância nos próprios dados de destilação | 95% |
| O mesmo, com forte aumento de dados combinado, concordância no treinamento na autodestilação | Cerca de 60% |
| Autodestilação do ResNet-20, concordância no treinamento com SGD em 300 épocas e em 5.000 épocas | 78,95% e 83,3% |
| Autodestilação, mais dados | Fidelidade sobe, acurácia no teste cai |
| Professor ensemble de 3, mais dados | Fidelidade e acurácia ambas sobem |

A explicação deles é a otimização: o aluno não iguala o professor nem nos dados em que treina. Mais dados de destilação ajudam a identificação da função do professor e tornam a otimização mais difícil.

## Gudibande et al. em números

| Observação | Número |
|---|---|
| Avaliações de crowd workers das saídas de imitação como iguais ou melhores do que o ChatGPT | Cerca de 70% |
| Natural Questions, LLaMA 7B: base, imitação ampla, imitação local, ChatGPT | 17, 10, 22, 31 |
| Natural Questions, LLaMA 13B: base, imitação ampla, imitação local, ChatGPT | 20, 15, 27, 31 |
| Saídas em tom autoritário: LLaMA base contra modelos de imitação | 57% contra 98% a 99% |

A alegação deles: com os métodos atuais, a lacuna só se fecha com uma quantidade pouco prática de dados de imitação ou um base model mais capaz, e um base model melhor ajudou mais do que mais dados de imitação nos experimentos deles. A imitação local de uma tarefa funcionou muito melhor do que a imitação ampla. Os modelos de imitação também ficaram menos tóxicos, aprendendo a se abster como o professor.

## Evidência da lacuna de capacidade

| Fonte | Achado | Remédio tentado |
|---|---|---|
| Mirzadeh et al. | A acurácia de um aluno de 2 camadas subiu e depois caiu conforme os professores cresciam de 4 a 10 camadas | Professor assistente. Ganho sobre a destilação padrão de 0,33 a 0,41 ponto na ResNet, 0,94 ponto na CNN simples com o CIFAR-10 |
| Cho e Hariharan | ResNet18 no ImageNet: do zero 30,24% de erro, 30,57%, 30,79% e 30,95% com professores ResNet18, 34 e 50 | A destilação parada cedo deu 29,01%, 29,16% e 29,35%. Professores parados cedo ajudaram no CIFAR-10. Encadear por um modelo médio não ajudou |
| Gu et al. (MiniLLM) | Aluno GPT-2 de 125M melhorou com professores de 340M, 760M e 1,5B | Nenhuma lacuna vista nessa faixa, uma família |

Os dois artigos de visão discordam sobre se um modelo intermediário ajuda. Teste no seu próprio par.

## Traços ocultos, Cloud et al.

| Item | Detalhe |
|---|---|
| Cenário | Um professor com um traço gera dados não relacionados, os dados são filtrados, um aluno da mesma base passa por fine-tuning neles |
| Preferência por coruja | Cerca de 12% antes, mais de 60% depois, apenas com números |
| Desalinhamento a partir de números | Quase 10% de respostas desalinhadas, contra 0% da base e menos de 1% dos controles |
| Desalinhamento a partir de chain of thought filtrada | De cerca de 0% para 8%, controles abaixo de 1% |
| Detecção | Classificadores com prompt e aprendizado in-context não detectaram o traço de forma confiável |
| Condição | Base model compartilhado. GPT-4.1 nano para Qwen2.5 não transmitiu. GPT-4o e GPT-4.1 transmitiram, provavelmente por uma inicialização compartilhada |
| Limites em aberto | Tarefas artificiais, e quais traços são transmitidos e quando é desconhecido |

## Sintoma, causa provável, verificação

| Sintoma | Causa provável | Verificação |
|---|---|---|
| O aluno iguala o professor em acurácia mas as saídas diferem | Baixa fidelidade | Concordância top-1 e KL preditivo em entradas held-out, com um controle de professor independente |
| Avaliações de crowd workers ou pontuações de juiz altas, benchmarks direcionados parados | Estilo copiado, capacidade não | Benchmarks em tarefas que os dados mal cobrem, contra o base model |
| Aluno pior do que o aluno de um professor menor | Lacuna de capacidade | Direto, um modelo intermediário, professor parado cedo, contra um baseline treinado do zero |
| Um comportamento indesejado aparece embora os dados sejam limpos | Traço oculto de uma base compartilhada | Avalie diretamente o aluno quanto ao comportamento e considere uma base diferente |
| O aluno recusa como o seu professor | O comportamento de recusa se transfere com o estilo | Compare as taxas de recusa com as do professor em um conjunto fixo de prompts |

## O que nada disso cobre

- Nenhuma fonte lida aqui mostra que um aluno copia os erros factuais do seu professor.
- A lacuna de capacidade e a lacuna de fidelidade foram medidas em modelos de visão, não em LLMs.
- O aprendizado subliminar foi mostrado em tarefas artificiais, e uma base diferente bloqueá-lo foi uma observação nesses experimentos, não uma garantia.
