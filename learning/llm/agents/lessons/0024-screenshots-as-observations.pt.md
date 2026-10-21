---
title: "24. Screenshots como observações"
description: "Como agentes de computer use observam a tela como imagem e não como dados estruturados, e por que a estrutura do loop continua valendo"
type: lesson
---

# Lição 24. Screenshots como observações

**Ligação com a missão:** Diagnosticar um agente de computer use que falha a partir da trajetória exige entender que as observações dele são visuais, e não estruturadas, de modo que um erro de grounding não se parece em nada com um argumento de ferramenta perdido.
**Fonte principal:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Pré-requisitos:** [Lição 23](0023-code-execution-as-a-tool.md), [Loop do agente](../GLOSSARY.md)

## Aquecimento

1. ▢ Nas lições anteriores, quando o agente chama uma ferramenta e recebe um resultado, que forma esse resultado assume? Ele é sempre estruturado (JSON ou um schema), sempre texto não estruturado, ou qualquer um dos dois?

<details markdown="1"><summary>Verificação</summary>

Estruturado, em todo formato de rede que esta trilha cobriu. O resultado de uma ferramenta é sempre marcado com o id da chamada que ele responde, e sempre carrega ou a saída da ferramenta ou um erro, mesmo que os nomes exatos dos campos e o formato variem conforme o provedor e o harness (veja a Lição 3). O modelo nunca precisa interpretar visualmente o resultado de uma ferramenta como faz com um screenshot.

</details>

2. ▢ Da Lição 6: Quais são os quatro passos centrais do loop do agente, em ordem?

<details markdown="1"><summary>Verificação</summary>

Chamar o modelo, anexar a resposta à transcrição, verificar se terminou, senão executar as ferramentas e anexar os resultados, depois voltar ao início.

</details>

## Saiba isto

### A observação muda de tipo

Nas lições anteriores, a observação de um agente que chama ferramentas, depois de cada ação, é um resultado estruturado que o harness constrói: um objeto JSON com campos como `tool_id`, `status` e `value`. A observação de um agente de computer use é radicalmente diferente. Depois que o agente executa uma ação de tela (clicar, digitar, rolar), a observação é um screenshot: literalmente uma imagem, em formato PNG ou JPEG, do que está sendo exibido na tela agora.

O modelo precisa interpretar visualmente essa imagem para entender o que aconteceu, em vez de ler um campo de dados estruturado. Essa é uma mudança profunda em como o agente entende o mundo.

A forma geral do loop da Lição 6 sobrevive intacta: enviar a transcrição, receber a resposta, executar a ação, anexar o resultado, repetir. Mas agora "anexar o resultado" significa anexar uma imagem à transcrição, e "receber a resposta" significa que o modelo está gerando uma descrição do que vê nessa imagem e decidindo o que fazer em seguida.

### Por que isso importa: generalidade

A razão desse design é poder. Nas lições anteriores, um agente que chama ferramentas só pode chamar ferramentas que o desenvolvedor construiu explicitamente para ele. Se você quer que um agente interaja com uma aplicação que não tem API, precisa escrever uma ferramenta que embrulhe a API dessa aplicação. Mas e se a aplicação não tem API nenhuma? E se ela é só uma GUI?

Um agente de computer use contorna esse problema. Em vez de precisar de uma API ou de uma ferramenta sob medida para cada aplicação, o agente interage pela tela, do jeito que uma pessoa faria. O espaço de ações é fixo e genérico: mover o mouse, clicar, digitar texto, pressionar teclas, rolar, tirar um screenshot. Essas mesmas ações funcionam em qualquer aplicação com GUI em qualquer sistema operacional, de um navegador web a uma aplicação desktop e a um console de nuvem. O modelo aprende a fazer coisas de tela, e não coisas específicas de aplicação.

Esse é o ganho: um agente que consegue operar literalmente qualquer interface, mesmo as construídas sem pensar em integração com agentes.

### O loop continua valendo

Como a estrutura do loop é conceitualmente separada do tipo de observação, o ciclo básico sobrevive:

1. Enviar a transcrição (que agora inclui o screenshot atual) ao modelo.
2. O modelo olha o screenshot, entende o que está na tela e decide o que fazer em seguida.
3. O modelo emite uma ação: clicar nas coordenadas (x, y), digitar a string "hello", rolar para baixo ou tirar outro screenshot.
4. O harness executa a ação.
5. Se a ação foi um screenshot, o harness anexa a nova imagem à transcrição.
6. Voltar ao passo 1.

O modelo continua decidindo quando parar, o harness continua impondo limites e encerrando o loop, a transcrição continua crescendo a cada turno e as condições de parada da Lição 6 (sem mais ações, máximo de turnos, limite de erros) continuam valendo. A única coisa que mudou é o tipo de dado da observação: de um objeto JSON para uma imagem.

### Desafios introduzidos pela observação visual

Essa generalidade tem um custo. O resultado estruturado de uma ferramenta é inequívoco: o harness o construiu, ele tem um schema fixo e o modelo consegue ler campos pelo nome. Um screenshot é ambíguo: o modelo precisa localizar visualmente o que quer (um botão, um campo de texto, um item de menu) na imagem atual, interpretar sua localização e decidir que ação tomar.

Na Lição 25, você verá essa ambiguidade se cristalizar em um problema específico chamado grounding. Por ora, saiba que esse trade-off existe: agentes de computer use conseguem fazer coisas que agentes que chamam ferramentas não conseguem, porque podem operar qualquer GUI, mas a observação exige interpretação visual, o que introduz novos modos de falha que as observações estruturadas não têm.

## Prática

1. ▢ Você está construindo um agente de computer use para interagir com uma aplicação web. Seu colega sugere adicionar uma ferramenta chamada `click_button` que recebe o nome de um botão como argumento string, para que o agente possa escrever `click_button("Submit")` em vez de ter de lidar com coordenadas. Isso é uma boa ideia? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não é. O ponto central de um agente de computer use é funcionar com qualquer GUI sem ferramentas sob medida. Se você adiciona ferramentas específicas da tarefa como `click_button`, está sobrepondo uma interface tradicional de chamada de ferramentas por cima, o que anula o propósito. O modelo deve aprender a executar ações genéricas (clicar em coordenadas, digitar) e interpretar o screenshot visualmente. Adicionar ferramentas-wrapper acrescenta acoplamento e reduz a generalidade do agente.

</details>

2. ▢ Um agente de computer use tira um screenshot, vê um formulário de login e digita seu nome de usuário no campo de senha em vez do campo de nome de usuário. Isso é um bug no modelo, no harness ou no próprio espaço de ações?

<details markdown="1"><summary>Dica</summary>

O modelo decidiu digitar o nome de usuário. O harness executou a ação. Algo deu errado ao ligar a decisão à parte certa da tela.

</details>

<details markdown="1"><summary>Verificação</summary>

Isso é um erro de interpretação visual: o modelo viu o formulário, mas identificou errado qual campo era qual. O espaço de ações (digitar esta string) funcionou corretamente. O harness executou a ação corretamente. O entendimento do modelo sobre o screenshot estava errado. Isso se chama erro de grounding e é o assunto da Lição 25.

</details>

3. ▢ Um agente que chama ferramentas e lê arquivos usa uma ferramenta chamada `read_file(path)` e recebe um resultado com um campo de status. Um agente de computer use que lê arquivos abrindo-os em um editor de texto tira um screenshot depois de abrir o editor. Qual observação é mais fácil de o harness verificar como bem-sucedida?

    - a) O agente que chama ferramentas, porque o campo de status é explícito
    - b) O agente de computer use, porque um screenshot mostra tudo
    - c) São igualmente fáceis, apenas formatos diferentes
    - d) Nenhuma das duas, porque verificar o sucesso exige que o modelo interprete o resultado de qualquer jeito

<details markdown="1"><summary>Verificação</summary>

**a)** O agente que chama ferramentas tem um campo de status explícito; o harness pode verificar `if result.status == "success"` sem ambiguidade. O screenshot do agente de computer use mostra o conteúdo do arquivo, mas o harness precisa levar esse screenshot ao modelo e pedir que ele verifique se o arquivo foi aberto corretamente, o que é mais lento e menos confiável. O tipo de observação afeta o quão fácil é a verificação.

</details>

4. ▢ Você está lendo a trajetória de um agente de computer use que tentou preencher um formulário. O agente executou oito ações: clicou em campos, digitou texto e rolou. O screenshot final mostra o formulário com os campos vazios. O que você deve verificar primeiro para diagnosticar por que o agente falhou?

<details markdown="1"><summary>Verificação</summary>

Olhe as coordenadas de cada ação de clique em comparação com os screenshots tirados depois de cada clique. O agente clicou na parte certa da tela, ou os cliques caíram nos lugares errados? Mesmo que o modelo tenha decidido "clicar no campo de nome de usuário", a coordenada real do clique pode ter errado. Esse é o problema do grounding: a intenção do modelo e a localização real na tela divergiram.

</details>

## Prática no mundo real

- [ ] Abra uma aplicação web em um navegador. Tire um screenshot manualmente. Para três elementos da tela (um botão, um campo de texto, um link), estime suas coordenadas em pixels (x, y). Agora redimensione a janela do navegador ou role, tire um novo screenshot e reestime essas mesmas coordenadas. Anote quanto as coordenadas mudaram e se uma coordenada fixa do primeiro screenshot ainda funcionaria no segundo.

- [ ] Leia a trajetória de um agente de computer use (de um exemplo público, da documentação de uma ferramenta ou de um teste seu). Escolha um screenshot do meio da execução. Sem olhar os screenshots ou ações seguintes, anote três coisas que o agente poderia fazer em seguida. Depois olhe a ação que o agente de fato tomou. Suas previsões bateram?

- [ ] Amanhã: Encontre a descrição de uma falha de agente de computer use (em um post de blog, uma issue do GitHub ou o resumo de um paper). Antes de ler a explicação, levante a hipótese de se a falha se deveu ao modelo entender mal a tarefa, a um erro de sintaxe de chamada de ferramenta, a um erro de grounding (coordenadas erradas) ou a outra coisa. Depois leia a explicação e confira se o seu palpite estava certo.

## Para ir além

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
