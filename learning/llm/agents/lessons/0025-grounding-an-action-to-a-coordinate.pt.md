---
title: "25. Grounding de uma ação em uma coordenada"
description: "Por que traduzir uma intenção visual em uma coordenada de pixel é mais difícil e mais frágil do que um argumento tipado de chamada de ferramenta"
type: lesson
---

# Lição 25. Grounding de uma ação em uma coordenada

**Ligação com a missão:** Diagnosticar um agente de computer use que falha exige reconhecer erros de grounding (uma coordenada errada) como distintos de mau uso de ferramenta ou de erros de lógica, para que você corrija o problema certo.
**Fonte principal:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Pré-requisitos:** [Lição 24](0024-screenshots-as-observations.md)

## Aquecimento

1. ▢ Em um agente que chama ferramentas, quando o modelo quer atualizar um usuário, o que ele envia ao harness, e como o harness sabe qual usuário específico atualizar?

<details markdown="1"><summary>Verificação</summary>

O modelo envia uma chamada de ferramenta com um argumento como `user_id: "u_123"`, um identificador estável e único. O harness lê esse identificador e atualiza o usuário por ID, sem ambiguidade.

</details>

2. ▢ Em um agente de computer use, quando o modelo quer clicar em um botão que vê no screenshot, o que ele envia ao harness, e como o harness sabe em qual botão clicar?

<details markdown="1"><summary>Verificação</summary>

O modelo envia uma ação para clicar em uma coordenada de pixel, como `click(x=450, y=200)`. O harness lê a coordenada e clica exatamente nessa posição da tela.

</details>

## Saiba isto

### O problema do grounding

Grounding é o passo de traduzir a intenção de um modelo em uma coordenada de tela de fato. Quando um agente que chama ferramentas quer atualizar um registro, ele especifica o registro por um ID estável, um nome ou um identificador único sobre o qual o harness pode agir diretamente. Não há ambiguidade: o harness encontra o registro ou não encontra.

Quando um agente de computer use quer clicar em um botão, ele precisa localizar visualmente esse botão no screenshot atual, estimar suas coordenadas em pixels e emitir uma tupla de coordenadas como `(x, y)`. Isso é mais difícil de quatro maneiras.

**Primeiro, não há referência estável.** Um botão no pixel 450, 200 em um screenshot é outro botão (ou botão nenhum) se a janela é redimensionada, a página rola ou o conteúdo se desloca. Um ID persiste entre mudanças de layout; uma coordenada não. Um agente que chama ferramentas pediria um botão pelo nome; um agente de computer use pede um botão pela posição, o que é frágil.

**Segundo, o modelo não pode pedir ajuda.** Em um agente que chama ferramentas, se o harness não entende um argumento, ele devolve um erro claro: "user_id u_999 not found" ou "invalid format for date_field". O modelo lê o erro e corrige o argumento. Em um agente de computer use, um clique na coordenada errada simplesmente acerta a coisa errada (ou o espaço vazio). O modelo não recebe uma mensagem de erro. Só descobre no screenshot seguinte que o clique caiu no lugar errado, e mesmo então precisa inferir, por inspeção visual, que o clique errou.

**Terceiro, o ciclo de feedback é lento.** Depois que um agente que chama ferramentas comete um erro, ele recebe uma mensagem de erro tipada. Depois que um agente de computer use comete um erro, ele precisa tirar outro screenshot completo, enviá-lo ao modelo, esperar que o modelo interprete a nova imagem e raciocine sobre o que deu errado e tentar de novo. Cada erro de grounding custa uma ida e volta completa ao modelo para descobrir e corrigir.

**Quarto, pequenas mudanças no ambiente quebram sequências que funcionavam.** Uma chamada de ferramenta que nomeia um usuário por ID continua funcionando se o nome, o e-mail ou o departamento do usuário mudam. Um clique em coordenadas quebra se o botão se move mesmo alguns pixels. Uma tela de laptop de 13 polegadas, um monitor de 27 polegadas, o zoom do navegador, a renderização de fontes e os breakpoints de CSS podem todos mover o mesmo botão para coordenadas diferentes. Uma trajetória que funcionou perfeitamente em uma máquina pode falhar em silêncio em outra.

### O que torna o grounding frágil

Imagine que um agente clica com sucesso em uma caixa de busca em (300, 150) em um navegador desktop com zoom normal. A mesma página web vista em um celular ou com o zoom do navegador em 125 por cento pode renderizar a caixa de busca em (225, 112) ou (375, 188). A coordenada não está mais correta. O clique pode cair em nada, ou em um elemento totalmente diferente.

A lógica do agente estava sólida. O modelo tomou uma decisão razoável. O tipo de ação (clicar) estava correto. Mas a coordenada estava errada, porque o ambiente mudou. Um agente que chama ferramentas e pede uma ferramenta chamada `search` não tem esse problema, já que o nome da ferramenta é estável.

É por isso que erros de grounding são uma categoria de falha exclusiva de agentes que dirigem a tela. Eles não ocorrem em agentes que chamam ferramentas, porque estes referenciam as coisas pelo nome, e não pela posição.

### Mitigação parcial: ferramentas cientes de estrutura

Algumas ferramentas de navegador ou de computer use tentam reduzir a fragilidade do grounding oferecendo um meio-termo: em vez de apenas um screenshot, a ferramenta também devolve informação estruturada sobre os elementos da página: os nomes, papéis, posições e caixas delimitadoras de todo botão, link e campo de formulário.

O modelo pode então dizer "clique no botão rotulado 'Submit'" ou "clique no campo de texto na linha do e-mail", e o harness traduz essa referência nomeada em uma coordenada no momento do clique, em vez de pedir ao modelo que estime coordenadas a partir de pixels. Isso recupera alguma estabilidade: se o botão se move, o harness calcula novas coordenadas automaticamente, sem o modelo precisar reestimar.

Isso é um trade-off. Você ganha confiabilidade e perde parte da generalidade de "funciona em qualquer GUI" que a ação puramente baseada em screenshot alcança. Uma ferramenta ciente de estrutura funciona bem para páginas web, onde os elementos HTML têm papéis semânticos e IDs estáveis, mas pode não funcionar para aplicações desktop com GUI, jogos ou aplicações obscuras para as quais a ferramenta não foi projetada. Ações puramente baseadas em screenshot não têm essa limitação, mas são mais frágeis.

### Como identificar erros de grounding em uma trajetória

Ao ler a trajetória de um agente de computer use, procure padrões:

- A intenção do modelo faz sentido (ele decidiu buscar algo, preencher um campo etc.), mas a ação não produziu o resultado esperado.
- Vários cliques seguidos caem no lugar errado.
- A mesma ação funciona em um screenshot, mas falha no seguinte.
- As coordenadas estão longe de qualquer elemento visível.

Esses são sinais típicos de um erro de grounding. O modelo estava raciocinando corretamente sobre o que fazer, mas as coordenadas não batiam com a tela. Isso é distinto de um erro de lógica (o modelo decidiu fazer a coisa errada) ou de uma falha de ferramenta (a ferramenta travou).

## Prática

1. ▢ Um agente clica nas coordenadas (500, 250) para enviar um formulário. O screenshot antes do clique mostra um botão Submit centralizado em aproximadamente (500, 250). A ação tem sucesso e o formulário é enviado. No turno seguinte, o agente tenta clicar de novo no mesmo botão Submit nas mesmas coordenadas (500, 250), mas o formulário agora sumiu e uma mensagem de carregamento é exibida. O segundo clique cai em nada. Isso é um erro de grounding?

<details markdown="1"><summary>Verificação</summary>

Não. O primeiro clique foi corretamente ancorado. O segundo clique errou porque a tela mudou, e não porque o modelo estimou mal a coordenada. Erros de grounding acontecem quando a coordenada não corresponde ao alvo pretendido no screenshot que o modelo está olhando agora. Depois que o conteúdo da página mudou, a coordenada ficou obsoleta, mas isso não é um erro de grounding na tomada de decisão do agente; é comportamento correto: o agente tentou clicar em algo que não estava mais lá.

</details>

2. ▢ Um agente lê o screenshot de uma página de login com dois campos: nome de usuário no topo e senha abaixo. O agente decide digitar a senha, estima que o campo de senha está em aproximadamente (350, 180) e envia a ação `type(x=350, y=180)`. O harness clica em (350, 180), que na verdade é o campo de nome de usuário, e a senha é digitada no campo de nome de usuário. O agente então vê um novo screenshot mostrando o campo de nome de usuário agora preenchido com a senha. Isso é um erro de grounding, um erro de lógica ou ambos?

<details markdown="1"><summary>Dica</summary>

Faça duas perguntas separadamente: (1) O modelo tomou uma decisão razoável sobre o que fazer? (2) O modelo acertou as coordenadas?

</details>

<details markdown="1"><summary>Verificação</summary>

Isso é um erro de grounding, não um erro de lógica. A decisão do modelo estava correta: ele decidiu digitar a senha. Mas o modelo estimou mal as coordenadas do campo de senha. A coordenada (350, 180) estava errada; o campo de senha estava, na verdade, mais abaixo na tela, talvez em (350, 240). O modelo pretendia clicar no alvo certo, mas ancorou a ação de forma incorreta.

</details>

3. ▢ Um agente de computer use interage com duas aplicações web diferentes em sequência. Na primeira aplicação, ele preenche com sucesso um formulário clicando em um campo em (400, 300). Na segunda aplicação, ele tenta clicar em um campo de entrada de texto que parece estar em uma posição semelhante da tela, também em (400, 300), mas na segunda aplicação essa coordenada é espaço vazio e o clique não cai em lugar nenhum. O segundo clique é um erro de grounding?

    - a) Sim, porque a coordenada não correspondia ao alvo pretendido no screenshot da segunda aplicação
    - b) Não, porque o modelo usou o mesmo raciocínio nas duas aplicações
    - c) Não, porque a coordenada funcionou corretamente da primeira vez, então a segunda aplicação deve ter um bug de interface
    - d) Não, porque erros de grounding só acontecem quando o modelo tenta intencionalmente clicar na coisa errada

<details markdown="1"><summary>Verificação</summary>

**a)** O clique foi ancorado de forma incorreta: a coordenada não correspondia ao alvo pretendido no screenshot atual da segunda aplicação. O fato de a mesma coordenada ter funcionado em outra aplicação é irrelevante; grounding é sobre a correspondência entre intenção e coordenada na tela diante do modelo agora. **b)** está errada porque o raciocínio do modelo não é o que torna um clique ancorado ou não, apenas se a coordenada cai no alvo pretendido. **c)** está errada porque uma coordenada ter funcionado uma vez não diz nada sobre ela estar correta em outra tela; o modelo foi quem assumiu uma estabilidade que não deveria. **d)** está errada porque erros de grounding são enganos, e não escolhas intencionais.

</details>

4. ▢ Você está lendo uma trajetória em que um agente não conseguiu concluir uma tarefa. No turno sete, o agente clicou em (1200, 50), o canto superior direito da tela. Não há nada visível ali, e o clique não teve efeito. O modelo então disse que não encontrou o botão que procurava. No turno seguinte, o agente clicou em (150, 50), o canto superior esquerdo, e encontrou o botão. Formule uma hipótese sobre o que deu errado no turno sete.

<details markdown="1"><summary>Verificação</summary>

O agente provavelmente confundiu a posição do botão e ancorou o clique longe demais à direita. O botão estava na verdade no lado esquerdo da tela, mas o modelo estimou que estava à direita. Esse é um erro clássico de grounding: a intenção do modelo (encontrar e clicar no botão) estava certa, mas a coordenada estava errada. O agente se corrigiu no turno seguinte, possivelmente relendo o screenshot ou reconsiderando a estimativa.

</details>

## Prática no mundo real

- [ ] Tire um screenshot de uma página web com zoom normal. Escolha um botão e anote suas coordenadas em pixels conforme você as estima. Agora aumente o zoom do navegador em 25 por cento e tire um novo screenshot. Procure as coordenadas do mesmo botão no screenshot com zoom usando as ferramentas de desenvolvedor do navegador (inspecione o elemento e confira sua caixa delimitadora). Anote as novas coordenadas. Quão longe do real ficou a sua estimativa no primeiro screenshot? Como o zoom mudou a posição?

- [ ] Assista ou leia a trajetória de um agente de computer use (de um blog, da documentação de uma ferramenta ou de um exemplo). Para três ações consecutivas, compare o que o agente pretendia fazer (pelo contexto ou pelo prompt) com as coordenadas que ele emitiu e o screenshot que veio depois. O grounding correspondeu à intenção? Se não, o que mudou as coordenadas?

- [ ] Amanhã: Projete um formulário web simples (mentalmente ou em código) que você acha que seria difícil para um agente de computer use ancorar corretamente. Que propriedades do formulário tornam o grounding frágil? Depois projete uma segunda versão do mesmo formulário que seria mais fácil de ancorar e explique o que você mudou.

## Para ir além

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
