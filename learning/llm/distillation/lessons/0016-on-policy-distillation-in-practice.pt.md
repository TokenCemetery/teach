---
title: "16. Destilação on-policy na prática"
description: "O que a destilação on-policy custa por passo, o que ela traz e como o Qwen3 a usou nos seus modelos pequenos"
type: lesson
---

# Lição 16. Destilação on-policy na prática

**Ligação com a missão:** A missão pede que você diga quando a destilação on-policy compensa o seu custo, o que significa contar quanto custa um passo, que sinal ele devolve e o que uma equipe de produção mediu contra a alternativa.
**Fonte principal:** [Artigo científico: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388), seção 4.5 e a discussão da destilação on-policy na seção 4.7
**Pré-requisitos:** [Lição 8](0008-sequence-level-distillation.md), [Lição 14](0014-exposure-bias.md), [Lição 15](0015-gkd-and-minillm.md), [Destilação off-policy](../GLOSSARY.md), [Destilação on-policy](../GLOSSARY.md)

## Aquecimento

1. ▢ O que a fração de dados do aluno lambda controla no GKD, e quais são os seus dois valores extremos?

<details markdown="1"><summary>Verificação</summary>

É a probabilidade de um passo treinar em sequências geradas pelo aluno em vez de um dataset fixo. Lambda 0 é a destilação supervisionada em dados fixos e lambda 1 é puramente on-policy.

</details>

2. ▢ A primeira fase de destilação do Qwen3 treina em saídas que o professor gerou. Qual termo da lição 8 nomeia isso, e ele é on-policy?

<details markdown="1"><summary>Verificação</summary>

Destilação em nível de sequência, nas palavras do relatório do Qwen3 "response distillation". Ela é off-policy: as sequências foram fixadas pelo professor, não escritas pelo aluno.

</details>

3. ▢ O exposure bias é uma incompatibilidade em quais prefixos o aluno vê. Nomeie o único componente de que um passo on-policy precisa do professor e que um passo com texto fixo não precisa.

<details markdown="1"><summary>Verificação</summary>

A sua distribuição sobre tokens em cada posição da sequência do próprio aluno, o que significa que o modelo professor precisa ser executado sobre a saída do aluno durante o treinamento. Um texto que o professor já escreveu não fornece isso.

</details>

## Saiba isto

### O que um passo custa

Um passo off-policy com texto do professor armazenado custa um forward e um backward pass do aluno sobre sequências fixas. Um passo off-policy com logits do professor armazenados acrescenta uma leitura do disco, e o custo de armazenamento pertence à lição 7.

Um passo on-policy acrescenta trabalho, e vale listá-lo em ordem:

| Passo | Trabalho | Observações |
|---|---|---|
| 1 | O aluno gera uma sequência para cada prompt | Decodificação sequencial. Mais barato do que o professor fazê-lo, porque o aluno é menor (GKD, seção 3.1) |
| 2 | O professor roda um forward pass sobre a sequência finalizada | Um passo paralelo, não geração. Exige o professor na memória ou acessível |
| 3 | O aluno roda forward e backward e a divergência é calculada | Igual a um passo off-policy |

As duas primeiras linhas não têm contrapartida off-policy com texto fixo. A observação do próprio artigo sobre eficiência trata do SeqKD: no experimento de instruction tuning, o GKD não rodou o SeqKD "devido à sua ineficiência computacional para gerar dados do professor durante o treinamento" (seção 4.4). O passo 1 aqui usa o modelo pequeno, que é o lado mais barato dessa troca. Essa comparação de custo é uma afirmação do artigo, e a tabela de três linhas acima é a minha contabilidade do trabalho.

### Sinal denso contra uma recompensa esparsa

A destilação não é a única maneira de melhorar um modelo pequeno nas suas próprias amostras. O reinforcement learning também treina nas próprias sequências do modelo, mas pontua cada sequência inteira com uma recompensa escalar. A seção 3.2 do GKD escreve o objetivo combinado com a recompensa como `r(y)`, um único número por sequência.

A destilação on-policy devolve uma pontuação para cada token, tirada da distribuição do professor naquela posição. Esse é um sinal mais denso por amostra. Denso significa mais informação por sequência gerada. Não significa que o professor esteja certo, ponto a que a lição 18 volta.

A consequência prática vai em um só sentido. O RL consegue melhorar um modelo sem nenhum modelo mais forte disponível, porque precisa apenas de uma recompensa. A destilação on-policy precisa que exista um professor mais forte.

### Como o Qwen3 a usou

O relatório do Qwen3 descreve um pipeline de pós-treinamento de quatro etapas para os seus modelos principais, e uma "strong-to-weak distillation" separada para os leves: cinco modelos densos (0.6B, 1.7B, 4B, 8B e 14B) e um modelo mixture-of-experts (30B-A3B). A motivação foi o custo: a destilação "elimina a necessidade de executar um processo de treinamento exaustivo de quatro etapas individualmente para cada modelo de pequena escala" (seção 4).

Os modelos pequenos são destilados em duas fases (seção 4.5):

| Fase | Dados | Sinal de treinamento |
|---|---|---|
| Off-policy | Saídas do professor geradas nos modos thinking e non-thinking | Response distillation, para dar habilidade básica de raciocínio e a capacidade de alternar entre os modos |
| On-policy | O aluno gera respostas em qualquer dos modos | O aluno passa por fine-tuning alinhando os seus logits aos do professor (Qwen3-32B ou Qwen3-235B-A22B) para minimizar a divergência KL |

Leia a ordem. A fase off-policy vem primeiro, e o relatório diz que ela estabelece "uma base sólida" para a on-policy. Isso combina com a observação do GKD de que o treinamento on-policy assume um aluno que já consegue gerar sequências aceitáveis. Esse é um cronograma de duas etapas, não a mistura de lambda por batch do GKD.

### A comparação com o RL

A seção 4.7 compara a destilação on-policy com reinforcement learning direto no Qwen3-8B. Ambos partem do mesmo checkpoint destilado off-policy, e a comparação usa apenas consultas de matemática e código. A Tabela 21 relata, com pass@64 entre parênteses onde o relatório dá um:

| Método | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | Horas de GPU |
|---|---|---|---|---|---|---|---|
| Destilação off-policy | 55,0 (90,0) | 42,8 (83,3) | 92,4 | 42,0 | 86,4 | 55,6 | não informado |
| mais reinforcement learning | 67,6 (90,0) | 55,5 (83,3) | 94,8 | 52,9 | 86,9 | 61,3 | 17.920 |
| mais destilação on-policy | 74,4 (93,3) | 65,5 (86,7) | 97,0 | 60,3 | 88,3 | 63,3 | 1.800 |

Em todo benchmark da tabela, a destilação on-policy pontuou mais do que o RL, e usou cerca de um décimo das horas de GPU: 17.920 divididos por 1.800 dá 9,96. O relatório lê isso como um desempenho significativamente melhor do que o RL com aproximadamente um décimo das horas de GPU. Ele também observa que o pass@64 no AIME subiu depois da destilação e não mudou depois do RL, o que ele toma como evidência de que destilar a partir dos logits do professor expande o espaço de exploração do aluno.

### Quanto confiar nessa tabela

É um relatório, um tamanho de aluno, apenas consultas de matemática e código, e os autores compararam os seus próprios dois métodos. O relatório não diz qual professor foi usado na comparação do 8B. Não encontrei uma afirmação sobre se os números de horas de GPU incluem rodar o professor, então não presuma que incluem. A receita de RL não é descrita na comparação, então uma execução de RL mais bem ajustada poderia fechar parte da diferença. O resultado é forte evidência de que a destilação foi mais barata e melhor no cenário do Qwen3, e não evidência sobre todos os cenários.

Note também o que a comparação deixa de fora. Os próprios professores saíram do pipeline de quatro etapas, que inclui RL. A economia é real, mas assume que alguém já pagou pelo professor.

## Prática

1. ▢ Pela Tabela 21, quantos pontos o RL e a destilação on-policy somaram cada um no LiveCodeBench v5 sobre o checkpoint off-policy, e quantas horas de GPU por ponto cada um usou?

<details markdown="1"><summary>Verificação</summary>

O RL foi de 42,0 para 52,9, então +10,9 pontos, e 17.920 divididos por 10,9 dá cerca de 1.640 horas de GPU por ponto. A destilação on-policy foi para 60,3, então +18,3 pontos, e 1.800 divididos por 18,3 dá cerca de 98 horas de GPU por ponto. A razão é cerca de 17 para 1 neste benchmark, maior do que os 10 para 1 do destaque, porque a destilação também ganhou mais pontos. Os dois números são para um tamanho de aluno e um conjunto de consultas.

</details>

2. ▢ Qual custo está presente em um passo de destilação on-policy e ausente de um passo off-policy com texto do professor armazenado?

    - a) Fazer backpropagation através do modelo aluno
    - b) Calcular uma loss em cada posição de token
    - c) Rodar o professor sobre a saída do aluno
    - d) Tokenizar os prompts antes de o treinamento começar

<details markdown="1"><summary>Verificação</summary>

**c)** O professor precisa pontuar sequências que não existiam até o aluno gerá-las. (b), (a) e (d) acontecem também em passos off-policy.

</details>

3. ▢ O pass@1 melhorou depois do RL e da destilação on-policy. O que o pass@64 no AIME mostrou para cada um, e o que o relatório conclui?

<details markdown="1"><summary>Dica</summary>

Olhe os números entre parênteses nas colunas do AIME para a linha do RL.

</details>

<details markdown="1"><summary>Verificação</summary>

Para o RL, o pass@64 ficou em 90,0 no AIME'24 e 83,3 no AIME'25, sem mudança em relação ao checkpoint inicial. Depois da destilação on-policy, subiu para 93,3 e 86,7. O relatório conclui que destilar a partir dos logits do professor expandiu o espaço de exploração do aluno enquanto o RL não. Essa é a interpretação dos autores de uma comparação.

</details>

4. ▢ Você tem um aluno de 8B, um professor mais forte com o mesmo tokenizer, uma tarefa de matemática com resposta verificável e um orçamento limitado de GPU. A tabela do Qwen3 resolve se você deve usar RL ou destilação on-policy?

<details markdown="1"><summary>Verificação</summary>

Ela aponta para a destilação e não resolve a questão. Ela apoia que, com um professor forte já disponível e o aluno primeiro aquecido por destilação off-policy, a destilação on-policy foi mais barata e melhor nas execuções do Qwen3. Ela não cobre a sua tarefa, o seu professor, nem se os números de horas de GPU incluem o professor. Se não existe um professor mais forte, a destilação não está disponível de modo algum e o RL é o caminho, que é como os professores do Qwen3 foram construídos.

</details>

5. ▢ Por que o Qwen3 roda a fase off-policy antes da on-policy, e o que no GKD apoia essa ordem?

<details markdown="1"><summary>Verificação</summary>

A fase off-policy dá ao aluno a habilidade básica de raciocínio e a alternância de modos, o que o relatório diz estabelecer uma base para o treinamento on-policy. O GKD faz a mesma suposição: ele precisa de um aluno que já consiga gerar sequências de qualidade adequada para que o feedback do professor signifique algo, e os seus alunos começaram como checkpoints com supervised fine-tuning.

</details>

## Prática no mundo real

- [ ] Abra a seção 4.7 do relatório do Qwen3 e encontre a Tabela 21. Copie para uma nota as três células de horas de GPU e de AIME'24 e calcule os pontos por hora de cada método a partir delas.
- [ ] Escreva o custo por passo da sua própria execução planejada em três linhas: quem gera, quem pontua, quem atualiza. Depois marque qual modelo é grande o bastante para precisar da sua própria GPU.
- [ ] Amanhã: sem consultar anotações, escreva as duas fases do Qwen3, em que cada uma treina e duas razões para não generalizar o número de 1/10.

## Para ir além

- [Destilação On-Policy](../reference/on-policy-distillation.md)
- [Artigo científico: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
- [Pós-treinamento](../../post-training/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
