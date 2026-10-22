---
title: "7. A transcrição como estado"
description: "Entender que a transcrição é a única memória persistente do agente entre turnos"
type: lesson
---

# Lição 7. A transcrição como estado

**Ligação com a missão:** Reconhecer a transcrição como o único estado do agente ajuda você a diagnosticar um agente que falha a partir da trajetória, em vez de adivinhar por que o modelo está confuso ou repetitivo, o que serve à missão de "diagnosticar um agente que falha a partir da trajetória".
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 6](0006-writing-the-loop.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 6: Depois que o harness chama o modelo e recebe uma resposta, o que precisa acontecer antes de o harness executar qualquer chamada de ferramenta?

<details markdown="1"><summary>Verificação</summary>

A resposta precisa ser anexada à transcrição imediatamente, antes de qualquer ferramenta ser executada. Caso contrário, o pedido do próprio modelo nunca é registrado, e um turno posterior não mostrará por que um resultado de ferramenta está presente.

</details>

2. ▢ Da Lição 6: Nomeie duas condições de parada diferentes que um harness pode verificar para encerrar o loop do agente.

<details markdown="1"><summary>Verificação</summary>

Quaisquer duas entre: o modelo devolve um turno sem chamada de ferramenta, um limite de máximo de turnos ou de orçamento de tokens é atingido, o modelo chama uma ferramenta de parada explícita ou um limite de contagem de erros é excedido.

</details>

## Saiba isto

### A transcrição é tudo o que persiste

Entre uma chamada ao modelo e a seguinte, o harness guarda duas coisas:

1. A transcrição: o histórico completo da conversa, incluindo cada resposta do modelo, chamada de ferramenta e resultado de ferramenta.
2. Metadados do harness: contadores (contagem de turnos, contagem de erros), limites (máximo de turnos, máximo de erros), registros de ferramentas, configuração.

O modelo não vê os metadados do harness. O modelo só vê a transcrição. Se um fato não está na transcrição, o modelo não sabe que aconteceu.

Isso é ao mesmo tempo simples e profundo. Significa que:

- O modelo não consegue raciocinar sobre algo que o harness decidiu internamente, a menos que o harness o coloque na transcrição.
- Entre turnos, nada mais persiste. Nenhuma flag interna, nenhum estado oculto, nenhuma variável fora dos metadados do harness.
- Reproduzir uma execução de agente significa devolver a mesma transcrição ao modelo e continuar dali.

### A trajetória diverge da transcrição

Uma trajetória é o registro completo do que aconteceu: cada turno, decisão, log e efeito colateral. Uma transcrição é o que foi mostrado ao modelo. Elas não são a mesma coisa.

Por exemplo:

- O harness executa uma chamada de ferramenta, obtém um resultado de 100KB, mas decide que o resultado é longo demais e o trunca antes de anexá-lo à transcrição. A trajetória diz "a chamada de ferramenta teve sucesso, o resultado tinha 100KB"; a transcrição diz "a chamada de ferramenta teve sucesso, o resultado foram os primeiros 10KB". O modelo só conhece a segunda versão.
- O harness decide tentar uma ferramenta de novo porque a primeira tentativa falhou. O log da decisão vai para um arquivo, para uma pessoa depurar depois. Mas o harness nunca anexa "vou tentar de novo" à transcrição. No turno seguinte, o modelo não sabe que houve uma nova tentativa; ele só vê os resultados.
- Uma chamada de ferramenta falha em silêncio. O harness a registra em log, mas não anexa uma mensagem de erro à transcrição porque quem projetou o harness esqueceu. O modelo nunca descobre que a ferramenta falhou. No turno seguinte, o modelo pode pedir a mesma ferramenta de novo, confuso sobre por que ela não funcionou.

A consequência é que você pode olhar uma trajetória e concluir "o harness tomou uma decisão sensata", mas se olhar só a transcrição, vê um modelo confuso. O modelo não está confuso. Ele simplesmente não foi informado.

### Um exemplo trabalhado: o resultado de ferramenta que nunca existiu

Imagine este cenário:

O agente deve consultar um preço, depois aplicar um desconto e depois confirmar. No turno dois, o modelo chama uma ferramenta para buscar o preço. A ferramenta devolve "Item XYZ costs $100". O harness executa a ferramenta, obtém o resultado e o anexa à transcrição:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")
Tool result: "Item XYZ costs $100"

Agent turn 2: "I will apply a 10% discount. $100 - 10% = $90."
Agent turn 2 tool call: confirm_price(item="XYZ", price="$90")
```

Isso funciona. O modelo viu o resultado e raciocinou corretamente.

Agora imagine uma variante: o harness está registrando resultados em um banco de dados para monitoramento. A inserção do log falha. O harness registra o erro em um arquivo, mas quem desenvolveu nunca anexou nada à transcrição. O turno seguinte começa assim:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")

Agent turn 2: "I need to fetch the price. Let me call fetch_price again."
Agent turn 2 tool call: fetch_price(item="XYZ")
```

O modelo pede o preço de novo. Ele não está sendo teimoso nem burro. A transcrição nunca mostra o resultado do turno um. O modelo não tem como saber que a chamada teve sucesso. Isso é chamado de divergência: a trajetória diz "o resultado foi obtido e registrado", mas a transcrição diz "nada aconteceu".

A correção é sempre anexar à transcrição antes de seguir adiante, mesmo que os efeitos colaterais falhem:

```text
Tool result (appended immediately): "Item XYZ costs $100"

[Later, harness logs to database, but the append already happened]
Log to database failed [this error never goes in the transcript]
```

Agora o modelo sabe que o resultado aconteceu, independentemente de erros a jusante.

### Por que a transcrição como estado facilita a retomada

Suponha que uma execução de agente seja interrompida. O harness cai, a rede falha, a cota é atingida. Você quer retomar o agente de onde ele parou.

Se o agente guarda estado em variáveis internas, flags e decisões espalhadas pelo harness, a retomada é difícil. Você precisa salvar todo esse estado, restaurá-lo e torcer para não ter esquecido nada.

Se o estado do agente é apenas a transcrição, a retomada é trivial: salve a transcrição, depois inicie uma nova execução devolvendo a mesma transcrição ao modelo e continuando o loop a partir do próximo turno. O modelo verá tudo o que viu antes e continuará raciocinando. Sem estado oculto para reconstruir, sem flags para restaurar, sem variáveis para rastrear. A transcrição é o contrato.

Da mesma forma, você pode reproduzir uma execução de agente para depurá-la. Devolva a trajetória (o log completo do que aconteceu) como transcrição e veja o que o modelo faria em seguida. Você pode até editar a transcrição manualmente para testar o que o modelo faria em uma situação hipotética.

## Prática

1. ▢ Um agente deve buscar um documento, lê-lo e resumi-lo. No turno dois, ele chama uma ferramenta de busca e a ferramenta devolve 10 resultados. Antes de anexar o resultado à transcrição, o harness filtra os resultados para os três mais relevantes e anexa apenas esses. O que o modelo vê, e por que essa escolha de design fica visível quando você lê a transcrição?

<details markdown="1"><summary>Verificação</summary>

O modelo vê três resultados, e não dez. Ele não sabe que o harness filtrou; só sabe o que está na transcrição. Esse design é aceitável se for intencional: o harness escolheu reduzir o uso de tokens filtrando. O ponto-chave é que, lendo a transcrição, você vê exatamente o que o modelo viu (três resultados) e pode raciocinar sobre se a decisão seguinte do modelo foi sensata dada essa informação. Você não se confunde com o fato de que existiam dez resultados; a transcrição mostra o mundo da perspectiva do modelo.

</details>

2. ▢ Quem desenvolve um harness quer registrar quais ferramentas foram chamadas e quantas vezes. Deve guardar essa contagem em uma variável só do harness ou anexar um resumo à transcrição antes de cada chamada ao modelo?

<details markdown="1"><summary>Dica</summary>

Pense no que o modelo precisa saber para tomar decisões e em que informação só seria útil para depuração posterior por uma pessoa.

</details>

<details markdown="1"><summary>Verificação</summary>

Depende do caso de uso. Se o modelo precisa saber "você já chamou a busca três vezes, talvez tente outra ferramenta", então a contagem deve ir na transcrição. Se a contagem é puramente para monitoramento e o modelo não precisa ajustar seu comportamento com base nela, uma variável só do harness serve. Mas se o modelo pode se beneficiar de saber a contagem, ponha-a na transcrição para que o modelo a veja no turno seguinte. Um padrão seguro é anexar tudo o que possa afetar a decisão seguinte do modelo.

</details>

3. ▢ Você está depurando uma execução de agente. Lê a trajetória e vê que uma chamada de ferramenta teve sucesso e o resultado foi anexado. Lê a transcrição que o modelo de fato viu e o resultado não está lá. O que aconteceu?

    - a) O harness anexou o resultado e depois o removeu da transcrição antes de chamar o modelo de novo
    - b) A trajetória e a transcrição devem ser diferentes; a transcrição é um resumo e a trajetória é completa
    - c) O resultado foi anexado aos logs do harness, mas não à transcrição; o modelo nunca o viu
    - d) A chamada de ferramenta na verdade falhou e a trajetória está errada

<details markdown="1"><summary>Verificação</summary>

**c)** O resultado foi anexado aos logs do harness, mas não à transcrição; o modelo nunca o viu. Trajetórias e transcrições devem ser quase idênticas do ponto de vista do modelo (embora as transcrições possam ser truncadas ou amostradas por eficiência). Se a trajetória diz que algo aconteceu mas a transcrição não mostra, a causa mais provável é que o harness o registrou em log, mas não o anexou à transcrição. Esse é o bug mostrado no exemplo trabalhado. Remover da transcrição depois de anexar (a) seria incomum e anularia o propósito. Transcrições não são resumos; devem ser o histórico da conversa (b). Um erro de trajetória (d) é possível, mas menos comum do que um bug de log.

</details>

4. ▢ Você quer construir um agente retomável. A execução é interrompida depois de cinco turnos. Escreva em uma frase o que você precisa persistir em disco para retomar o agente a partir do turno seis.

<details markdown="1"><summary>Verificação</summary>

Você precisa persistir a transcrição (o histórico da conversa até o turno cinco, incluindo cada resposta do modelo, chamada de ferramenta e resultado de ferramenta). Ao retomar, entregue essa transcrição ao modelo como contexto inicial, chame o modelo e continue o loop. Os metadados do harness (contador de turnos, contador de erros etc.) podem ser reconstruídos ou reiniciados; apenas a transcrição é essencial.

</details>

## Prática no mundo real

- [ ] Rode um agente (de uma biblioteca que você usa ou um que você escreva) que faça pelo menos três chamadas de ferramenta. Inspecione a transcrição que ele gerou. Para cada resultado de ferramenta, verifique que o resultado está presente no que o modelo veria no turno seguinte. Se algum resultado estiver faltando, rastreie por quê (foi porque não foi anexado, ou foi truncado, ou foi filtrado?).

- [ ] Encontre um lugar no código do seu agente ou harness onde a informação é registrada em log mas não anexada à transcrição. Pergunte-se: o modelo precisa saber disso para tomar decisões melhores? Se sim, adicione à transcrição. Se não, deixe como um log só do harness.

- [ ] Amanhã: Projete um agente retomável do zero. Escreva o pseudocódigo da função de execução que recebe uma transcrição como entrada e retoma a partir do turno seguinte. Verifique que você não depende de nenhum estado só do harness para tomar decisões.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
