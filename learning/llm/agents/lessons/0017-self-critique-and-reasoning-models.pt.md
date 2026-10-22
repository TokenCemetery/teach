---
title: "17. Autocrítica e o que os modelos de raciocínio mudaram"
description: "O loop de reflexão como uma etapa explícita, seus custos e como o raciocínio interno estendido afeta quando usá-lo"
type: lesson
---

# Lição 17. Autocrítica e o que os modelos de raciocínio mudaram

**Ligação com a missão:** Para diagnosticar um agente que falha, você precisa reconhecer quando acrescentar uma etapa de reflexão (um loop separado que avalia falhas passadas e leva as lições adiante) e quando o próprio raciocínio interno do modelo torna esse loop redundante.
**Fonte principal:** [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
**Pré-requisitos:** [Lição 16](0016-plan-then-execute-and-decomposition.md)

## Aquecimento

1. ▢ Em um agente plan-then-execute, o que acontece se um passo falha e o harness não suporta replanejamento?

<details markdown="1"><summary>Verificação</summary>

O harness não tem como se adaptar. Ou continua às cegas com o plano original (que provavelmente vai falhar de novo), ou para. O agente não consegue aprender com a falha nem mudar para uma abordagem diferente porque o plano foi travado de antemão e não há mecanismo para atualizá-lo.

</details>

2. ▢ Qual é a vantagem do replanejamento explícito sobre simplesmente rodar o agente de novo desde o início?

<details markdown="1"><summary>Verificação</summary>

O replanejamento permite ao modelo ver a falha exata e raciocinar sobre ela em contexto. Se você apenas roda o agente de novo, ele pode produzir o mesmo plano outra vez. Com o replanejamento, o harness anexa a falha à transcrição e pede ao modelo que faça um novo plano, para que o modelo veja o que deu errado e ajuste.

</details>

## Saiba isto

### Reflexion: acrescentando um loop de reflexão

O paper do Reflexion introduz uma etapa explícita de reflexão no loop do agente. Depois que uma tentativa falha (a resposta do agente está errada, uma tarefa não é concluída, um teste falha), o harness não tenta de novo imediatamente. Em vez disso, gera uma reflexão em linguagem natural sobre o que deu errado. Essa reflexão é armazenada (muitas vezes em um arquivo ou buffer de memória) e incluída no contexto da próxima tentativa.

O loop é assim:

1. Rodar o agente em uma tarefa.
2. Verificar se a tarefa teve sucesso (um teste passa, uma pessoa avalia a resposta como correta).
3. Se falhou, gerar uma reflexão: "Tentei X, mas X falhou porque Y."
4. Armazenar a reflexão em uma memória persistente.
5. Rodar o agente de novo, desta vez incluindo a reflexão armazenada no contexto.
6. Voltar ao passo 2.

Isso é diferente de uma simples repetição. Uma simples repetição roda o agente de novo com o mesmo contexto. O Reflexion roda o agente de novo com a reflexão no contexto, de modo que a segunda tentativa pode aprender com a falha da primeira.

### Por que a reflexão não é de graça

O Reflexion custa chamadas extras ao modelo. Se a primeira tentativa falha, você agora precisa de uma chamada para gerar a reflexão, depois outra para rodar a segunda tentativa. Para tarefas com baixas taxas de falha, essa sobrecarga não vale a pena. Para tarefas em que muitas tentativas são necessárias, o custo acumulado é alto.

A reflexão também consome orçamento de contexto. Cada reflexão ocupa tokens na janela de contexto. Se você acumula muitas reflexões ao longo das tentativas, em algum momento precisa podá-las ou resumi-las. Essa é uma versão diferente do problema de gerenciamento de contexto das lições anteriores.

A reflexão só faz sentido se a própria reflexão estiver ancorada em informação real: um teste que falhou, uma mensagem de erro, uma avaliação humana. Se a tarefa não tem um sinal claro de falha, a reflexão não tem nada concreto a que reagir e pode simplesmente racionalizar a resposta errada anterior.

### Modelos com raciocínio interno estendido

Nos últimos anos, alguns modelos de ponta ganharam a capacidade de fazer raciocínio interno estendido antes de produzir uma resposta. Esse raciocínio não é visível na transcrição (acontece dentro de um único turno do modelo, antes de a saída ser devolvida), mas permite ao modelo se autocorrigir, conferir o próprio trabalho e pegar erros óbvios antes de eles aparecerem na saída.

Isso muda, mas não elimina, o argumento a favor de loops de reflexão explícitos. Parte do que um loop de reflexão costumava oferecer (pegar um passo intermediário obviamente errado) agora acontece dentro do próprio raciocínio do modelo, então acrescentar um loop de reflexão por cima dá menos benefício marginal do que antes.

No entanto, a reflexão explícita ainda tem uma vantagem que o raciocínio interno não tem: ela pode incorporar informação que só existe depois de uma chamada de ferramenta ser feita. Se uma chamada de ferramenta devolve "Permission denied" ou um teste falha, o raciocínio interno do modelo não pode ter visto esse sinal de falha durante sua fase original de raciocínio, porque a ferramenta ainda não tinha rodado. Um loop de reflexão explícito pode observar o resultado real da ferramenta e incorporá-lo à próxima tentativa.

Então a pergunta não é "reflexão ou raciocínio interno", e sim "quando o custo extra da reflexão externa compensa apesar do raciocínio interno?"

### Quando a autocrítica explícita compensa o custo

Use reflexão externa quando:

- A tarefa tem um sinal de falha claro e verificável (uma suíte de testes passa ou falha, uma API devolve um erro, uma pessoa avalia a resposta como errada ou certa).
- Uma segunda ou terceira tentativa, informada pela falha, provavelmente terá sucesso onde a primeira falhou.
- A tarefa vale a pena ser repetida: valor alto o bastante para justificar as chamadas extras ao modelo.

Não acrescente reflexão quando:

- A tarefa não tem sinal claro de falha (por exemplo, "escreva um resumo" sem teste ou rubrica para verificar a correção).
- A falha não é culpa do modelo (por exemplo, uma API necessária está fora do ar, algo que o modelo não pode consertar).
- A primeira tentativa já tem alta probabilidade de sucesso e as falhas são raras.

### Projetando sinais de reflexão

A reflexão é tão boa quanto o sinal que recebe. Se você diz ao harness "esta tarefa falhou porque o usuário disse", a reflexão pode gerar "Tentei escrever um resumo, mas o usuário não gostou." Isso é vago demais para a próxima tentativa agir. Um sinal de falha melhor seria "o resumo não contém os requisitos declarados pelo cliente" ou "o resumo é mais longo do que o limite de 100 palavras".

Ao construir um agente que reflete, projete a verificação de falha com cuidado. Como é o sucesso? Que evidência concreta prova a falha? Essa evidência é aquilo a que a reflexão vai reagir.

## Prática

1. ▢ Um agente escreve código para resolver um problema do LeetCode. A suíte de testes roda o código e relata "All tests pass" ou imprime um caso de teste específico que falhou. Depois de uma falha, o harness gera uma reflexão e roda o agente de novo com a reflexão no contexto. Por que isto é um bom caso para o Reflexion?

<details markdown="1"><summary>Verificação</summary>

Há um sinal de falha claro: a suíte de testes. A reflexão pode dizer "O caso de teste [entrada] esperava [saída], mas eu produzi [saída_errada]." Isso é concreto e acionável. O modelo pode ler isso na próxima tentativa e depurar especificamente o caso que falhou. A geração de código também é iterativa por natureza; várias tentativas são esperadas e valem o custo.

</details>

2. ▢ Pede-se a um agente que escreva textos de produto para um site de e-commerce. O agente produz o texto e o envia. Não há suíte de testes, nem rubrica, nem verificação automática. Uma gerente de marketing lê e diz "Isto não está certo, tente de novo." O Reflexion ajudaria aqui?

<details markdown="1"><summary>Dica</summary>

Com que feedback o loop de reflexão tem de trabalhar? É concreto o bastante para a próxima tentativa agir?

</details>

<details markdown="1"><summary>Verificação</summary>

O Reflexion não ajudaria muito. O feedback "Isto não está certo" é vago demais. A reflexão seria algo como "A gerente de marketing não gostou do meu texto." A próxima tentativa do agente não teria nenhuma mudança concreta a fazer. Uma abordagem melhor seria obter feedback específico da gerente (por exemplo, "Deixe mais curto e acrescente uma comparação de preços") e incluí-lo no próximo prompt, em vez de depender de um loop de reflexão.

</details>

3. ▢ Um modelo com raciocínio interno estendido agora consegue se autocorrigir durante sua própria fase de raciocínio. Qual dos seguintes ainda é uma vantagem de um loop de reflexão externo explícito nesse contexto?

    - a) A reflexão externa é sempre mais rápida do que o raciocínio interno.
    - b) A reflexão externa pode incorporar informação (como um erro de ferramenta ou uma falha de teste) que só existe depois da primeira tentativa do modelo.
    - c) A reflexão externa é mais barata em tokens de contexto do que o raciocínio interno.
    - d) A reflexão externa funciona com todos os modelos, mesmo os sem capacidade de raciocínio interno.

<details markdown="1"><summary>Verificação</summary>

**b)** O raciocínio interno acontece antes de qualquer ferramenta rodar, então não consegue observar o resultado real de uma ferramenta nem uma falha de teste. Um loop de reflexão explícito pode incorporar essa informação, e por isso oferece valor mesmo com modelos que têm raciocínio interno. a) é falsa, o raciocínio interno costuma ser mais rápido do que rodar um loop extra. c) é falsa, a reflexão externa consome tokens de contexto (o texto da reflexão e a próxima tentativa ocupam espaço). d) é verdadeira, mas não é a ideia-chave; a pergunta é sobre o que a reflexão acrescenta quando há raciocínio interno.

</details>

4. ▢ Você está construindo um agente que processa candidaturas a vagas. O harness tem um sinal claro: aprovado ou rejeitado por um gestor de contratação. Você quer usar o Reflexion para melhorar as decisões do agente ao longo de várias tentativas. O que cada reflexão deve capturar para ser útil na próxima tentativa?

<details markdown="1"><summary>Verificação</summary>

A reflexão deve capturar as razões específicas da rejeição ou da aprovação, se disponíveis. Por exemplo, "Candidatura rejeitada porque: falta a certificação exigida. Na próxima tentativa, verifique as certificações exigidas antes de aprovar." Ou "Candidatura aprovada porque: forte experiência nas habilidades exigidas e boa comunicação na carta de apresentação." A reflexão deve ser específica da candidatura, e não um conselho genérico. Isso dá à próxima tentativa algo concreto sobre o que agir. Se o gestor fornece apenas um sim/não sem razões, a reflexão é menos acionável.

</details>

## Prática no mundo real

- [ ] Pegue uma tarefa que envolve iteração e tem um sinal claro de passou/falhou (por exemplo, resolver um problema, passar em um teste, atender a uma rubrica). Implemente um loop de agente que reflete: tentar, verificar a falha, gerar a reflexão, tentar de novo com a reflexão no contexto. Rode-o cinco vezes e conte quantas tentativas o agente precisa com reflexão contra sem. Registre a diferença.
- [ ] Encontre uma tarefa no seu trabalho que não tem sinal claro de falha (por exemplo, escrita, design, trabalho criativo). Descreva como você adicionaria um (por exemplo, "comparar com uma rubrica", "pedir a revisão de um colega", "verificar critérios específicos"). Adicionar um sinal de falha tornaria útil um agente que reflete, ou a tarefa é mais bem tratada com um loop humano?
- [ ] Amanhã: Leia uma trajetória de Reflexion (de um paper, um post de blog ou algo que você construiu). Identifique o texto da reflexão. A reflexão teria sido útil se o modelo tivesse raciocínio interno? Por que sim ou por que não?

## Para ir além

- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
