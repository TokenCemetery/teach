---
title: "3. Métricas específicas da tarefa"
description: "Exact match, F1 em nível de token e BLEU/ROUGE, e o modo de falha de cada um"
type: lesson
---

# Lição 3. Métricas específicas da tarefa

**Ligação com a missão:** A etapa 2 abre a metade "construa o eval" da missão: uma métrica específica da tarefa transforma um conjunto held-out (etapa 1) em um número de verdade, e cada métrica que esta lição cobre serve bem a algumas tarefas e mente em silêncio sobre outras.
**Fonte principal:** [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
**Pré-requisitos:** [Lição 2](0002-designing-contamination-resistance.md), [Contaminação de dados](../GLOSSARY.md)

## Aquecimento

1. ▢ Contra o que embutir uma canary string em um conjunto de eval customizado de fato protege?

<details markdown="1"><summary>Verificação</summary>

Ela sinaliza aos crawlers que montam um corpus de treinamento que o conteúdo marcado deve ser excluído, e dá uma forma de detectar um vazamento depois, se a string aparecer na saída de um modelo ou em um corpus acessível. É um pedido, não uma garantia: depende de os crawlers respeitarem a convenção.

</details>

2. ▢ Quando uma verificação de sobreposição de n-gramas contra um corpus conhecido é utilizável, e quando deixa de ser uma opção?

<details markdown="1"><summary>Verificação</summary>

É utilizável quando o corpus de pré-treinamento é conhecido e acessível. Deixa de ser uma opção para um modelo fechado com dados de treinamento não divulgados, em que o teste de instrução guiada continua sendo a ferramenta disponível.

</details>

## Saiba isto

### Exact match: rigoroso e frágil diante de qualquer coisa superficial

O **exact match** só considera uma predição correta se ela coincidir com uma resposta de referência caractere por caractere (muitas vezes depois de uma normalização leve, como passar para minúsculas ou remover espaços em branco). Serve a tarefas com uma única resposta claramente correta: múltipla escolha, extração de trecho, um resultado matemático. Seu modo de falha é exatamente o que seu rigor implica: uma resposta correta formulada de outro jeito (`"Paris"` contra uma referência `"Paris, France"`) é pontuada como errada, penalizando a correção em vez de medi-la, a menos que a normalização aplicada seja generosa o bastante para absorver essa variação sem absorver também respostas genuinamente erradas.

### F1 em nível de token: crédito parcial, ao custo de se importar com a ordem

O **F1** (como usado em tarefas extrativas, como perguntas e respostas baseadas em trechos) trata uma predição e uma referência como sacos de tokens, em vez de exigir uma correspondência exata de string, calculando a precisão (que fração dos tokens da predição está correta) e o recall (que fração dos tokens da referência foi produzida), e depois sua média harmônica. A referência "the cat sat on the mat" (tokens: `the, cat, sat, on, the, mat`) contra a predição "a cat sat on the mat" (tokens: `a, cat, sat, on, the, mat`) compartilha cinco tokens (`cat, sat, on, the, mat`) de seis em cada lado: precisão `5/6`, recall `5/6`, F1 `5/6 ≈ 0.83`. Isso é mais tolerante que o exact match, que pontuaria esse par como simplesmente errado. O modo de falha é o que essa tolerância custa: o F1 sobre um saco de tokens é cego à ordem e a se as palavras em comum de fato se combinam em uma resposta correta, então uma predição que embaralha as palavras certas em uma afirmação errada ainda pode pontuar alto.

![A referência "the cat sat on the mat" e a predição "a cat sat on the mat" dispostas como caixas de tokens. cat, sat, on, mat e uma ocorrência de the são compartilhados entre elas. O segundo the da referência e o a da predição ficam, cada um, sem correspondência. Cinco de seis tokens coincidem em cada lado, então a precisão é 5/6, o recall é 5/6 e o F1 é 5/6.](images/f1-token-overlap.svg)

### BLEU e ROUGE: sobreposição de n-gramas contra uma referência, feitos para tradução e sumarização

O **BLEU** (originalmente para tradução automática) e o **ROUGE** (originalmente para sumarização) pontuam um texto gerado por quanto seus n-gramas (sequências contíguas de tokens de comprimento n) se sobrepõem a um ou mais textos de referência, em vez de exigir uma correspondência exata ou pontuar tokens isolados. Seu modo de falha aparece com mais força na geração aberta: uma paráfrase válida que diz a mesma coisa com outras palavras, "Critics praised the show" contra uma referência "The show received positive reviews from critics", compartilha pouquíssimos n-gramas com a referência apesar de ser uma resposta igualmente boa, e pontua baixo por isso. Usar vários textos de referência por exemplo suaviza o problema, mas raramente existem referências suficientes para cobrir todas as formulações válidas, o que explica boa parte de por que essas métricas se correlacionam apenas frouxamente com o julgamento humano em texto aberto, e de por que o LLM-as-judge da etapa 3 existe como alternativa justamente para esse caso.

### Escolher uma métrica significa casá-la com o que "correto" quer dizer para a tarefa

Exact match e F1 servem a tarefas em que a correção é um conjunto pequeno e bem definido de respostas: classificação, extração, aritmética. BLEU e ROUGE servem a tarefas em que a sobreposição superficial com uma referência se correlaciona, de forma frouxa, com a qualidade, úteis como um filtro grosseiro e barato de primeira passada, e não como veredito final. Nenhuma das duas famílias serve a uma tarefa em que a correção é comportamental e não textual (o código gerado de fato executa e produz a saída certa), que é o assunto da lição 4, nem à geração aberta em que o significado importa mais que a formulação, que é o assunto da etapa 3.

## Prática

1. ▢ Um modelo responde a uma pergunta de geografia com "Paris", enquanto a resposta de referência é "Paris, France". O exact match pontua isso como errado. Esse é um resultado de pontuação correto? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não, na verdade não: a resposta está correta, apenas formulada de modo mais conciso que a referência. Essa é a fragilidade do exact match diante de variação superficial. A correção é normalizar as duas strings antes de comparar (o que só ajuda se a normalização for desenhada para absorver esse tipo específico de variação) ou escolher uma métrica mais tolerante para uma tarefa em que a formulação varia tanto.

</details>

2. ▢ Referência: "a fast red fox jumps". Predição: "a red fox jumps fast". Usando F1 sobre saco de tokens (ignorando a ordem das palavras), qual é a precisão, o recall e o F1?

<details markdown="1"><summary>Dica</summary>

Liste os tokens de cada lado como um conjunto e conte quantos são compartilhados, independentemente da posição.

</details>

<details markdown="1"><summary>Verificação</summary>

Os dois lados têm os mesmos 5 tokens (`a, fast, red, fox, jumps` contra `a, red, fox, jumps, fast`), apenas reordenados, então os 5 são compartilhados. Precisão `5/5 = 1.0`, recall `5/5 = 1.0`, F1 `1.0`. Isso também demonstra a cegueira do F1 à ordem: uma predição com a ordem das palavras embaralhada pontua igual a uma que a preserva, ainda que a ordem das palavras possa mudar o significado de um modo que o F1 não consegue detectar.

</details>

3. ▢ Um modelo de sumarização produz "Critics praised the show" para um resumo de referência "The show received positive reviews from critics." O ROUGE provavelmente pontuaria esse par alto ou baixo, e esse resultado reflete de forma justa a qualidade da predição?

<details markdown="1"><summary>Verificação</summary>

Baixo, já que as duas frases compartilham pouquíssimos n-gramas contíguos apesar de dizerem essencialmente a mesma coisa com outras palavras. Isso não reflete a qualidade de forma justa: a predição é uma paráfrase válida, mas o ROUGE mede a sobreposição superficial de n-gramas, não o significado, então uma resposta correta formulada de modo diferente da referência é penalizada do mesmo jeito que uma resposta errada seria.

</details>

4. ▢ Uma equipe está avaliando um modelo em um benchmark de múltipla escolha com uma letra correta por pergunta. Qual métrica desta lição serve melhor, e por quê?

<details markdown="1"><summary>Verificação</summary>

Exact match. A tarefa tem exatamente uma resposta correta por pergunta, sem variação superficial relevante a absorver (a resposta é uma única letra), que é exatamente o formato de tarefa para o qual o exact match foi feito, sem precisar da tolerância do F1 ou do BLEU/ROUGE a sobreposição parcial ou parafraseada.

</details>

5. ▢ Qual afirmação é verdadeira sobre BLEU e ROUGE em comparação com exact match e F1?

    - a) Exigem uma única resposta correta e inequívoca, assim como o exact match
    - b) Pontuam a sobreposição com o texto de referência em nível de n-grama, o que se correlaciona apenas frouxamente com a qualidade em geração aberta
    - c) São imunes ao problema da paráfrase que afeta o exact match
    - d) São mais bem usados como veredito final para qualquer tarefa de geração, substituindo o julgamento humano ou de LLM

<details markdown="1"><summary>Verificação</summary>

**b)** A sobreposição de n-gramas é um indicador frouxo de qualidade, especialmente onde respostas válidas podem ser formuladas de muitas maneiras diferentes. (a) é falsa: elas foram feitas para tarefas com texto aberto, não para uma única resposta fixa. (c) é falsa: uma paráfrase válida pode pontuar baixo no BLEU/ROUGE pela mesma razão de fundo que pode falhar no exact match, a formulação superficial diferente. (d) é falsa: a fraca correlação delas com o julgamento humano em texto aberto é exatamente o motivo de a etapa 3 introduzir o LLM-as-judge como alternativa.

</details>

## Prática no mundo real

- [ ] Escolha uma tarefa que você avalia (ou planeja avaliar) e decida qual entre exact match, F1 ou BLEU/ROUGE se encaixa na noção de "correto" dela, anotando por quê.
- [ ] Para um eval que hoje usa BLEU ou ROUGE, encontre um exemplo em que uma resposta claramente correta, mas formulada de outro jeito, pontuaria mal, e anote-o.
- [ ] Amanhã: leia um parágrafo da documentação do Hugging Face Evaluate sobre uma métrica que você nunca usou e anote o modo de falha que ela declara.

## Para ir além

- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
