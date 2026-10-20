---
title: "18. Um conjunto de regressão para um prompt"
description: "Monte o pequeno conjunto de casos que uma mudança de prompt não pode quebrar, começando por falhas reais"
type: lesson
---

# Lição 18. Um conjunto de regressão para um prompt

**Ligação com a missão:** Uma mudança de prompt é uma afirmação, e um conjunto de regressão é o que permite conferir essa afirmação em segundos, em vez de julgá-la pelas três saídas que você por acaso leu.
**Fonte principal:** [Artigo: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
**Pré-requisitos:** [Lição 17](0017-prompt-caching-and-layout.md), [Conjunto de regressão](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 11 pediu saída estruturada e depois a validou. Por que uma verificação de validade é uma primeira asserção natural em um conjunto de regressão?

<details markdown="1"><summary>Verificação</summary>

Pedir um formato não é uma garantia, então a saída pode falhar no parse. Uma verificação de parse ou de schema é barata, não exige julgamento e roda em todo caso, o que a torna uma asserção fácil de escrever.

</details>

2. ▢ A lição 5 mostrou que uma edição de formatação sem significado pode mudar a acurácia. O que isso implica sobre quanto de uma mudança de prompt você consegue julgar lendo algumas saídas?

<details markdown="1"><summary>Verificação</summary>

Muito pouco. Uma pequena edição pode deslocar os resultados de maneiras que um punhado de saídas não mostra, então a mudança precisa ser executada contra um conjunto fixo de casos e contada.

</details>

## Saiba isto

### Comece pelas falhas que você já viu

Um **conjunto de regressão** é um conjunto fixo de entradas, cada uma com uma verificação sobre a saída, que uma mudança de prompt não pode quebrar. Os melhores primeiros casos são os reais. O relato de Hamel Husain sobre a construção de evals para um assistente imobiliário diz para olhar com senso crítico os traces e os modos de falha quando você não consegue pensar em asserções, e que as centenas de testes unitários da equipe eram atualizadas continuamente a partir de novas falhas observadas nos dados. Um trace é uma conversa registrada em log, então registre-as, leia-as e transforme cada falha em um caso: a entrada que a provocou e uma verificação que a teria pegado.

O guia da Anthropic sobre como construir avaliações concorda quanto ao alvo: projete testes que espelhem a distribuição real da sua tarefa, inclua casos de borda e automatize a correção sempre que possível. Você não precisa de tráfego de produção para começar. Hamel observa que você pode escrever palpites embasados, ou pedir a um modelo que gere entradas, e deixar os primeiros usuários refiná-las.

### Uma asserção por propriedade

Hamel descreve as verificações como asserções, como as que você escreveria no pytest, mantidas rápidas e baratas para poderem rodar a cada mudança. Cada caso lista as propriedades que a sua saída deve ter.

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` renderiza o template da lição 15, chama o modelo fixado da lição 16 e devolve o seu texto. O próprio exemplo de Hamel é uma verificação parecida de que a saída nunca expõe um UUID interno. Quando uma propriedade não pode ser um teste de string ou de regex, um modelo pode avaliá-la, e a trilha de evals cobre quando confiar nesse avaliador.

### Pequeno, crescente e não tudo ou nada

Comece com o punhado de falhas que você tem à frente e adicione um caso toda vez que uma nova falha aparecer. O conjunto deve ser representativo das falhas que importam para você, e não grande por si só: o guia da Anthropic favorece volume em vez de qualidade corrigida à mão, e a equipe de Hamel chegou a centenas de testes, então pequeno é o ponto de partida, não uma meta. Duas ressalvas de Hamel: um bom conjunto contém casos com os quais o modelo tem dificuldade e, diferentemente de testes unitários comuns, você não precisa necessariamente de uma taxa de aprovação de 100%, porque a taxa de aprovação é uma decisão de produto sobre quais falhas você tolera. Acompanhe os resultados em relação à versão do prompt para ver se você está progredindo.

## Prática

1. ▢ Um usuário relata que o resumidor chama um pedido de reembolso de "reclamação". Transforme esse relato em um caso: o que vai na entrada e de quais asserções a saída precisa?

<details markdown="1"><summary>Verificação</summary>

A entrada é o texto real do ticket do usuário, ou um bem próximo dele. As asserções são `must_contain` a palavra refund e `must_not_contain` a palavra complaint, como no caso `refund-not-complaint` acima. O caso agora falha no prompt antigo e passa na correção.

</details>

2. ▢ Preveja `run_case` para o caso `no-uuid` quando o modelo produz `Account 3f2b8c1e is locked.`

<details markdown="1"><summary>Dica</summary>

Compare a saída com a única string de `must_not_contain`.

</details>

<details markdown="1"><summary>Verificação</summary>

Retorna `False`. `must_contain` está vazio, então `has_all` é verdadeiro, mas a saída inclui `3f2b8c1e`, então `has_none` é falso e o caso falha. O prompt vazou parte do ID.

</details>

3. ▢ Um colega quer esperar até haver 500 casos com qualidade de produção antes de montar um conjunto de regressão. O que há de errado nisso, usando as fontes desta lição?

<details markdown="1"><summary>Verificação</summary>

Nada roda até lá, então as mudanças nesse meio-tempo são julgadas no feeling. As fontes descrevem conjuntos que cresceram a partir de falhas observadas, e Hamel diz que você pode começar de palpites embasados. Comece com as falhas que você tem e adicione casos conforme novas aparecem.

</details>

4. ▢ Um conjunto de regressão passa em 18 de 20 casos no prompt atual e a equipe insiste em 20 de 20 antes de qualquer release. Qual visão corresponde ao artigo de Hamel?

    - a) A taxa de aprovação é uma decisão de produto sobre falhas toleradas, então 100% não é exigido
    - b) Todo caso precisa passar, ou o conjunto não vale nada como gate antes de lançar
    - c) Os dois casos que falham devem ser apagados para que o conjunto reflita o prompt atual
    - d) A taxa de aprovação importa menos que o número de casos, que deve ser sempre minimizado

<details markdown="1"><summary>Verificação</summary>

**a)** Hamel diz que você não precisa necessariamente de uma taxa de aprovação de 100% e que isso depende das falhas que você tolerará. (b) é o hábito comum dos testes unitários, com o qual ele contrasta. (c) remove as falhas que o conjunto existe para lembrar. (d) é o contrário: o conjunto é pequeno apenas como ponto de partida.

</details>

## Prática no mundo real

- [ ] Levante cinco falhas reais ou realistas de um prompt que você executa, a partir de logs, relatos de bugs ou dos seus próprios testes, e escreva cada uma como uma entrada mais uma asserção.
- [ ] Coloque os cinco casos em um arquivo no repositório, ao lado do prompt, e execute-os contra o prompt atual, anotando quais passam.
- [ ] Amanhã: da próxima vez que o prompt der uma saída ruim, adicione-a como um caso antes de corrigir o prompt e confirme que ela falha primeiro.

## Para ir além

- [Artigo: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Prompts em Produção](../reference/prompts-in-production.md)
- [Recursos](../RESOURCES.md)

---

Não está entrando? Releia a fonte principal no topo, pois esta lição a comprime e é na compressão que a compreensão vaza. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a própria lição, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
