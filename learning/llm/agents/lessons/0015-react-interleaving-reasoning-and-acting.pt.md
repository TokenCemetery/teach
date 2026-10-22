---
title: "15. ReAct: intercalando raciocínio e ação"
description: "O padrão de juntar passos curtos de raciocínio a cada ação, para que o modelo possa observar e se adaptar"
type: lesson
---

# Lição 15. ReAct: intercalando raciocínio e ação

**Ligação com a missão:** Para diagnosticar um agente que falha, você reconhecerá se ele está executando ações sem raciocínio visível (onde a causa raiz se esconde), seguindo um plano rígido feito de antemão (onde surpresas do ambiente causam falhas em cascata) ou intercalando raciocínio com observação (onde os sinais de falha fluem de volta para a decisão seguinte).
**Fonte principal:** [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
**Pré-requisitos:** [Lição 14](0014-files-as-memory.md), [Loop do agente](../GLOSSARY.md)

## Aquecimento

1. ▢ Quando você guarda a memória de um agente em um arquivo entre execuções (digamos, uma transcrição de chat ou um log de decisões passadas), o que fica mais fácil de depurar e verificar sobre o comportamento do agente?

<details markdown="1"><summary>Verificação</summary>

Uma memória baseada em arquivo permite ler o estado exato que o agente viu antes de cada decisão, de modo que você pode reproduzir o raciocínio dele e verificar se fez uma escolha sensata dada a informação disponível naquele momento. Se o agente parece quebrado, você pode ler a trajetória anterior para encontrar o passo exato em que ele errou, em vez de adivinhar.

</details>

2. ▢ Nomeie um risco de guardar memórias grandes em arquivos: o que acontece se o agente nunca poda nem compacta o arquivo?

<details markdown="1"><summary>Verificação</summary>

O arquivo cresce sem limite, consumindo espaço em disco e orçamento de contexto quando é passado ao modelo. Em algum momento o agente não consegue encaixar todo o histórico na janela de contexto, forçando o harness a escolher quais memórias mais antigas descartar e quais manter.

</details>

## Saiba isto

### Três formatos para raciocinar e agir

O loop do agente suporta naturalmente vários padrões diferentes para quando o raciocínio acontece em relação a quando as ações rodam. O paper do ReAct identifica três, e entender os trade-offs entre eles é a chave para diagnosticar falhas de agentes.

**Só ação:** O modelo recebe a tarefa e o estado atuais e emite imediatamente uma chamada de ferramenta, sem raciocínio declarado. O harness executa a ferramenta, anexa o resultado e repete. Esta é a estrutura mais simples.

O risco: Quando algo dá errado, você não consegue dizer por que o modelo escolheu essa ação. Ele entendeu mal a tarefa? Achou que estava chamando outra ferramenta? Sem um traço de raciocínio, depurar é adivinhação. Você acaba acrescentando esclarecimentos ao prompt ("Pense passo a passo", "Verifique sua resposta"), mas o modelo continua não produzindo nenhum raciocínio visível para você inspecionar, então os esclarecimentos podem não ajudar.

**Raciocinar e depois agir de uma vez:** O modelo lê a tarefa, raciocina sobre o plano inteiro de antemão em texto (chame isto de fase de "pensamento"), e então se compromete com uma sequência de chamadas de ferramenta para executar o plano. Uma vez comprometido o plano, o harness executa todos os passos sem replanejar.

Isso evita o chute às cegas do só-ação, já que você consegue ver o raciocínio completo do modelo. Mas tem um custo oculto: o plano é feito antes de qualquer ferramenta rodar. Se uma chamada de ferramenta falha ou devolve dados inesperados, o plano fica obsoleto. O modelo não consegue reagir a surpresas porque já se comprometeu com a sequência. Você acaba tendo de rodar o agente de novo e torcer para a nova fase de raciocínio se corrigir.

**ReAct (raciocinar, agir e observar de forma intercalada):** O modelo raciocina em voz alta sobre o que fazer em seguida (um curto texto de "pensamento" ou "raciocínio"), depois emite uma chamada de ferramenta. O harness executa a ferramenta, anexa o resultado à transcrição e repete. No turno seguinte, o modelo lê o pensamento anterior, a ação que escolheu e o resultado real, e então raciocina sobre o próximo passo com base no que agora vê.

Esse é o padrão ReAct. O raciocínio do modelo é visível (você pode depurá-lo), mas, mais importante, o raciocínio de cada passo pode incorporar o resultado real do passo anterior. Se uma busca não devolveu resultados, o pensamento seguinte pode mudar para uma busca diferente. Se uma chamada de API falhou, o pensamento seguinte pode refletir isso e tentar um contorno. O raciocínio não é um plano rígido feito de antemão; é uma observação do que acabou de acontecer, alimentando o que acontece a seguir.

### Por que o ReAct vence quando o ambiente surpreende você

Raciocinar e depois agir de uma vez funciona bem em cenários de mundo fechado, onde as premissas do plano estão garantidas. A chamada real de ferramentas acontece em cenários de mundo aberto: arquivos faltam, buscas não devolvem nada, APIs estão fora do ar, usuários dão instruções contraditórias. Nesses casos, a adaptação passo a passo do ReAct é mais barata e mais robusta do que rodar de novo o ciclo completo de raciocinar e depois agir.

Pense no próprio loop do agente, da Lição 6. Um turno do modelo produz texto (que pode incluir raciocínio) e uma chamada de ferramenta. Essa chamada de ferramenta é executada e o resultado é anexado à transcrição. No turno seguinte, o modelo vê o resultado e emite novo texto e uma nova chamada de ferramenta. Por design, o loop do agente já suporta o ReAct: qualquer texto de raciocínio que o modelo emite é preservado na transcrição, o turno seguinte pode observá-lo e pode emitir um novo raciocínio que reage ao resultado observado.

"Meu harness suporta ReAct?" é, na verdade, apenas "Meu harness mantém o texto de raciocínio do modelo na transcrição e o devolve no turno seguinte?" A resposta, em quase todo harness que vale a pena usar, é sim.

### Diagnosticando falhas de só-ação e de planejar-e-depois-agir-de-uma-vez

Se você inspeciona a trajetória de um agente e não vê texto de raciocínio antes das chamadas de ferramenta, você tem um agente só-ação. As falhas são difíceis de diagnosticar. Acrescentar mais dados ao contexto (descrições de tarefa mais longas, mais exemplos) pode ajudar, mas, sem texto de raciocínio, você não tem visibilidade. A correção é induzir o modelo a emitir raciocínio (um campo de "pensamento", uma seção de "raciocínio" na chamada de ferramenta, qualquer coisa) e preservá-lo na transcrição. Aí você passa ao ReAct e a depuração se torna possível.

Se você vê um grande bloco de raciocínio no início, seguido de uma sequência de ações sem raciocínio intermediário, você tem planejar-e-depois-agir-de-uma-vez. Quando o agente falha, provavelmente você está vendo um plano que não sobreviveu ao contato com a realidade. A correção é permitir o replanejamento: depois de cada resultado de ferramenta, emitir novo raciocínio antes da próxima ação. De novo, isso leva você ao ReAct. Algumas falhas vão desaparecer porque o modelo agora consegue se adaptar.

## Prática

1. ▢ Um agente recebe a instrução "Busque informações sobre mudanças climáticas e depois resuma os 5 principais resultados." Ele emite uma chamada de ferramenta de busca sem texto de raciocínio antes. A busca devolve 10 resultados sobre ciência do clima, e o agente emite em seguida uma chamada de ferramenta de resumo sem raciocínio no meio. O resumo é impreciso. Por que é difícil dizer se o modelo entendeu mal a tarefa, entendeu mal os resultados ou cometeu um erro genuíno de raciocínio?

<details markdown="1"><summary>Verificação</summary>

Não há texto de raciocínio na transcrição, então você não consegue ver qual era o "objetivo" interno do modelo nem como ele interpretou os resultados da busca. A falta de raciocínio impede distinguir, por exemplo, "o modelo não percebeu que a busca devolveu 10 resultados e achou que precisava buscar de novo" de "o modelo viu os 10 resultados e entendeu mal a tarefa como resumir todos eles, e não os 5 principais." Acrescentar texto de raciocínio antes da etapa de resumo (um pensamento no estilo ReAct) permitiria ver qual mal-entendido ocorreu e corrigir o prompt de acordo.

</details>

2. ▢ Você está construindo um agente que recebe feedback do usuário e refina um documento. O plano do agente (emitido de antemão) é "Corrigir a gramática, depois adicionar exemplos, depois verificar o tamanho." A primeira passada tem sucesso. Mas o feedback do usuário na segunda execução é "Não gostei dos novos exemplos que você adicionou, mas mantenha as correções de gramática." O agente reutiliza o plano feito de antemão sem mudanças e adiciona exemplos de novo, ignorando o feedback.

<details markdown="1"><summary>Dica</summary>

O que torna o plano obsoleto neste cenário? Que informação o agente não está vendo quando planeja?

</details>

<details markdown="1"><summary>Verificação</summary>

O plano foi feito sem ver o feedback do usuário. Em planejar-e-depois-agir-de-uma-vez, a fase de raciocínio acontece antes de qualquer ferramenta rodar, então ela não consegue incorporar informação nova que chega no meio da trajetória. A correção é permitir raciocínio e replanejamento depois de cada resultado de ferramenta (aqui, depois de cada etapa de refinamento), para que o plano do agente possa se adaptar quando o feedback do usuário contradiz as premissas originais.

</details>

3. ▢ Qual dos seguintes é um sinal de que você deve mover um agente de só-ação para ReAct?

    - a) O agente está lento demais e você precisa acelerar as chamadas de ferramenta.
    - b) As falhas do agente são difíceis de diagnosticar porque você não vê por que ele escolheu cada ação.
    - c) O agente precisa usar 10 ferramentas em vez de 5.
    - d) A janela de contexto do agente está quase cheia.

<details markdown="1"><summary>Verificação</summary>

**b)** Agentes só-ação não produzem texto de raciocínio, então suas falhas são opacas. Mudar para ReAct (acrescentando uma etapa de raciocínio antes de cada ação) torna o raciocínio do modelo visível, que é o ganho central para a depuração. a) está errada porque o ReAct não acelera chamadas de ferramenta, ele acrescenta texto de raciocínio, que leva tempo. c) está errada, a quantidade de ferramentas não tem relação. d) está errada, a pressão sobre o contexto é uma preocupação separada de o agente raciocinar em voz alta ou não.

</details>

4. ▢ Um agente busca "melhores pizzarias em Portland" e recebe 5 resultados. Se o agente está rodando em modo ReAct, o que deve acontecer em seguida na transcrição?

<details markdown="1"><summary>Verificação</summary>

O agente deve emitir uma etapa de raciocínio (uma seção de "pensamento" ou "raciocínio") que observa os resultados da busca e decide o que fazer em seguida (por exemplo, "Esses resultados parecem bons, agora tenho informação suficiente para responder. Vou resumi-los" ou "Preciso de mais detalhes sobre os horários dos restaurantes, vou buscá-los a seguir"). Esse raciocínio se baseia no que a busca de fato devolveu, e não em um plano feito de antemão. Ao incluí-lo na transcrição, a próxima chamada de ferramenta (se houver) pode se basear no resultado real.

</details>

## Prática no mundo real

- [ ] Pegue um agente existente que você construiu ou conhece. Leia a trajetória dele (uma execução completa). Conte quantas chamadas de ferramenta têm texto de raciocínio imediatamente antes. Se menos de 80% têm texto de raciocínio, reescreva o prompt ou o schema da ferramenta para emitir raciocínio e rode de novo.
- [ ] Quebre de propósito uma ferramenta de que um agente depende (por exemplo, faça uma API de busca devolver um resultado vazio). Rode o agente em uma tarefa em que ele normalmente teria sucesso. Leia a trajetória. O agente emitiu raciocínio que reconheceu a ferramenta quebrada e mudou para uma abordagem diferente? Se não, adicione uma instrução de prompt para raciocinar e tente de novo.
- [ ] Amanhã: Peça a um colega que leia a trajetória de um agente sem ver a tarefa. Ele consegue inferir o que o agente estava tentando fazer em cada passo apenas pelo texto de raciocínio? Se não consegue, adicione prompts de raciocínio.

## Para ir além

- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
