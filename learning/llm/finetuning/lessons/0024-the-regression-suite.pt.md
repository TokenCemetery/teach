---
title: "24. O conjunto de regressão"
description: "Pegar o dano que todos os outros números escondem"
type: lesson
---

# Lição 24. O conjunto de regressão

**Ligação com a missão:** "Construir um eval que pega uma regressão antes do lançamento" é a redação da própria missão. Esta é essa lição.
**Fonte principal:** [Artigo científico: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
**Pré-requisitos:** [Lição 23](0023-metrics-that-mean-something.md), [Lição 22](0022-contamination-and-held-out-design.md)

## Aquecimento

1. ▢ Por que a loss é a base errada para uma decisão?

<details markdown="1"><summary>Verificação</summary>

Ela pontua a concordância com uma única continuação de referência, penalizando alternativas corretas e recompensando erros fluentes. Use-a para seleção de checkpoints, e não para decisões.

</details>

2. ▢ Dois vieses documentados de juízes modelo, e suas mitigações?

<details markdown="1"><summary>Verificação</summary>

Viés de posição: randomize a ordem e avalie as duas ordens. Viés de verbosidade: compare em comprimentos igualados ou instrua o juiz a desconsiderar o comprimento.

</details>

3. ▢ Por que o conjunto held-out da sua tarefa é cego ao esquecimento catastrófico?

<details markdown="1"><summary>Verificação</summary>

Ele é tirado da distribuição da sua tarefa, então não consegue observar a degradação em capacidades fora dessa distribuição.

</details>

## Saiba isto

### A falha que isto existe para pegar

O fine-tuning move os pesos em direção à sua tarefa. Habilidades que não foram reforçadas podem se degradar, e isso é o **esquecimento catastrófico**. A literatura empírica constata que não é um caso extremo raro no fine-tuning contínuo de modelos de linguagem: capacidades gerais, incluindo o seguimento de instruções, declinam de forma mensurável, e o efeito pode crescer com a escala do modelo em vez de diminuir.

A propriedade perigosa é que **todo número que você já está olhando vai na direção certa.** A loss de treinamento cai, a sua métrica held-out da tarefa melhora, as suas sondas parecem boas, e o modelo ficou pior em coisas que você nunca mediu. Você entrega, e os relatos vêm de uma direção que a sua avaliação não conseguia ver.

Um conjunto held-out mede se você aprendeu a tarefa. Um conjunto de regressão mede se você quebrou mais alguma coisa. **São instrumentos diferentes e você precisa dos dois.**

### O que entra nele

Quatro categorias. Todas as quatro, e não uma seleção.

**1. Seguimento geral de instruções.** Ele ainda consegue seguir uma instrução comum, sem relação com a sua tarefa? Resumir algo, responder uma pergunta geral, seguir um pedido de vários passos.

**2. Conformidade de formato e de comportamento.** Ele ainda respeita um system prompt? Ainda produz JSON válido quando pedido? Ainda para quando deveria? Um modelo treinado em um único formato rígido às vezes perde a capacidade de produzir qualquer outro.

**3. Comportamento de segurança e de recusa.** Se o base model recusava certos pedidos, o fine-tune ainda os recusa? **O fine-tuning em dados benignos pode degradar o alinhamento de segurança como efeito colateral.** Esse é um resultado documentado e reproduzido repetidamente, não uma hipótese. Se você herdou o comportamento de alinhamento de um modelo instruct, herdou a responsabilidade de verificar que ele sobreviveu.

**4. Capacidade adjacente.** Coisas próximas da sua tarefa que você não treinou. Fez fine-tuning em tickets de suporte em inglês? Verifique outro idioma. Fez fine-tuning em um tipo de documento? Verifique outro.

### Construindo

Pequeno, fixo e lido por um humano.

```text
regression/
├── instruction-following.jsonl   # 20 general instructions
├── format-compliance.jsonl       # 20 schema and system-prompt cases
├── safety.jsonl                  # 20 cases the base refused
├── adjacent.jsonl                # 20 near-task, untrained cases
└── baseline/                     # base model outputs, committed
```

Oitenta exemplos no total. É deliberadamente pequeno: o bastante para pegar uma regressão real, pequeno o bastante para que uma pessoa de fato leia os diffs.

O passo crítico e frequentemente omitido: **registre as saídas do base model antes de treinar, e faça commit delas.** Uma regressão é uma *mudança*, então você precisa do antes. Sem um baseline armazenado, você fica comparando com a sua memória de como o modelo se comportava, o que não é evidência.

```python
# Run once, before any training. Commit the result.
for case in regression_cases:
    out = base_model.generate(**tok(case["prompt"]), do_sample=False, max_new_tokens=256)
    baseline[case["id"]] = tok.decode(out[0], skip_special_tokens=True)
```

Decodificação gulosa, para que um diff signifique uma mudança de pesos e não um sorteio do sampler.

### Lendo

Execute o conjunto em todo checkpoint candidato. Compare com o baseline. Depois classifique cada mudança:

| Veredicto | Significado |
|---|---|
| Inalterado | Tudo bem |
| Mudou, ainda correto | Anote; tudo bem |
| Mudou, agora errado | **Regressão, bloqueia o lançamento** |
| Mudou, agora melhor | Um bônus, e vale entender |

A terceira linha é o ponto inteiro. Uma regressão clara em segurança ou em seguimento de instruções pesa mais do que alguns pontos na sua métrica da tarefa, porque o modo de falha é ilimitado e o ganho não é.

### Reduzindo o esquecimento, quando você o encontra

Opções mais ou menos na ordem do que custam a você:

1. **Menos passos, ou um checkpoint anterior.** O esquecimento cresce com o treinamento. Muitas vezes a correção mais barata, e em geral custa pouco desempenho na tarefa.
2. **Learning rate menor.** Atualizações menores perturbam menos.
3. **Rank menor, ou menos target modules.** Menos capacidade com que sobrescrever.
4. **Misture dados gerais de instrução.** Alguns por cento de exemplos gerais de seguimento de instruções junto aos dados da sua tarefa. Eficaz e bem estabelecido, e custa pureza do dataset em vez de qualidade do modelo.
5. **Mantenha o adapter sem merge e roteie.** A resposta mais completa: aplique o adapter só para os pedidos que precisam dele e sirva o base intocado para todo o resto. O esquecimento se torna irrelevante porque o base ainda está lá. Lição 25.

A opção 5 é a que as pessoas ignoram, e muitas vezes é a arquitetura correta. Se o seu fine-tune serve a um único propósito estreito dentro de um produto maior, você não precisa de um único modelo que faça tudo.

### Automatize

O conjunto deve rodar em todo checkpoint, sem ser pedido, e se recusar a passar diante de uma regressão. Uma avaliação que depende de alguém lembrar de executá-la será pulada na execução em que mais importava, a que está sob pressão de prazo.

## Prática

1. ▢ Por que uma métrica held-out da tarefa que melhora de forma monotônica não descarta uma regressão?

<details markdown="1"><summary>Verificação</summary>

Ela é tirada da distribuição da sua tarefa e portanto só observa a sua tarefa. Capacidades fora dessa distribuição são invisíveis para ela, e são exatamente as que o esquecimento danifica.

Você precisa de um instrumento separado, apontado para o que você *não* está treinando.

</details>

2. ▢ Nomeie as quatro categorias de regressão.

<details markdown="1"><summary>Verificação</summary>

Seguimento geral de instruções, conformidade de formato e de comportamento, comportamento de segurança e de recusa, capacidade adjacente não treinada.

A segurança é a que mais costuma ficar de fora, e o fine-tuning em dados inteiramente benignos pode degradá-la.

</details>

3. ▢ Você tem um conjunto de regressão mas nenhum baseline armazenado. O que dá para concluir ao executá-lo?

<details markdown="1"><summary>Verificação</summary>

Muito pouco. Uma regressão é uma mudança em relação ao comportamento anterior, então sem o comportamento anterior você não consegue identificar uma, só julgar saídas isoladamente, o que não revela uma degradação sutil.

Registre e faça commit das saídas do base model antes de treinar. Este é o passo que faz o conjunto funcionar.

</details>

4. ▢ Métrica da tarefa subiu 3 pontos; o modelo já não recusa um pedido que o base recusava. Entrega?

<details markdown="1"><summary>Verificação</summary>

Não. Uma regressão de segurança bloqueia o lançamento independentemente dos ganhos na tarefa: o prejuízo é ilimitado, enquanto três pontos não são.

Investigue: tente um checkpoint anterior, um learning rate menor, misturar dados gerais de instrução, ou manter o adapter sem merge e rotear para ele só o tráfego relevante.

</details>

5. ▢ O que elimina de forma mais completa o problema do esquecimento?

    - a) Misturar dados gerais de instrução no conjunto de treinamento
    - b) Servir o base model sem merge e rotear por requisição
    - c) Reduzir o learning rate e treinar por menos passos
    - d) Reduzir o rank do adapter e o número de target modules

<details markdown="1"><summary>Verificação</summary>

**b)** Servir o base model sem merge e rotear por requisição.

As outras reduzem quanto esquecimento ocorre. O roteamento significa que o base não modificado continua disponível para tudo fora da sua tarefa, então o esquecimento no caminho adaptado deixa de importar.

</details>

6. ▢ Por que decodificação gulosa para o conjunto de regressão?

<details markdown="1"><summary>Verificação</summary>

Para que uma diferença em relação ao baseline seja atribuível a pesos alterados, e não à amostragem. Com temperature acima de zero, toda execução difere e o diff não carrega informação.

</details>

## Prática no mundo real

- [ ] Escreva 20 casos de regressão, cinco em cada categoria. Inclua pelo menos um que o base model recusa.
- [ ] Gere e faça commit das saídas de baseline do base model, de forma gulosa, antes de qualquer treinamento.
- [ ] Execute o conjunto no seu adapter existente e compare. Classifique cada mudança nos quatro veredictos.
- [ ] Amanhã: ligue o conjunto ao seu script de treinamento para que ele rode em todo checkpoint sem ser pedido.

## Para ir além

- [Artigo científico: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
- [Artigo científico: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
- [Modos de falha](../reference/failure-modes.md)
- [Lição 25. Servindo adapters](0025-serving-adapters.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
