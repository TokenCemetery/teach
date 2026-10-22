---
title: "26. Por que agentes de navegador falham de forma diferente"
description: "Agentes que dirigem a tela falham de maneiras que os agentes que chamam ferramentas não falham, e por que o WebArena criou um benchmark para medir e estudar essas falhas"
type: lesson
---

# Lição 26. Por que agentes de navegador falham de forma diferente

**Ligação com a missão:** Construir e diagnosticar agentes que dirigem a tela exige entender que seus modos de falha são estruturais, e não apenas uma questão de prompting melhor, para que você invista em estratégias de mitigação em vez de ajustes de prompt.
**Fonte principal:** [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
**Pré-requisitos:** [Lição 25](0025-grounding-an-action-to-a-coordinate.md)

## Aquecimento

1. ▢ Da Lição 24: Por que um agente de computer use precisa trabalhar com pixels e screenshots em vez de chamadas de ferramenta nomeadas?

<details markdown="1"><summary>Verificação</summary>

Porque ele precisa operar qualquer aplicação com GUI, inclusive as que nunca foram construídas pensando em uma API ou em integração com agentes. Um agente de computer use interage pela tela do jeito que uma pessoa faz, então funciona em qualquer lugar.

</details>

2. ▢ Da Lição 25: Nomeie uma razão pela qual uma coordenada de pixel é uma referência mais frágil do que um argumento de chamada de ferramenta.

<details markdown="1"><summary>Verificação</summary>

Uma coordenada quebra quando o layout muda (redimensionar a janela, rolar a página, nível de zoom), mas um argumento como um ID de usuário ou o nome de um registro persiste. Uma coordenada também quebra em silêncio quando cai na coisa errada, enquanto uma chamada de ferramenta recebe um erro explícito.

</details>

## Saiba isto

### Modos de falha exclusivos de agentes que dirigem a tela

Um agente que chama ferramentas falha quando chama a ferramenta errada, passa argumentos incorretos ou fica sem turnos. Um agente que dirige a tela (baseado em navegador ou de computer use) falha de todas essas maneiras e também de maneiras que agentes que chamam ferramentas simplesmente não conseguem.

**Erros de grounding** (Lição 25): A intenção do modelo está correta, mas as coordenadas estão erradas, fazendo o clique cair no elemento errado ou no espaço vazio. Um agente que chama ferramentas não tem esse problema porque referencia as coisas pelo nome.

**Obstáculos do ambiente**: Um popup, banner de cookies, spinner de carregamento, diálogo modal ou mensagem de erro pode bloquear a próxima ação do agente. Um agente que chama ferramentas talvez nunca encontre isso, porque uma chamada de API simplesmente tem sucesso ou falha de forma limpa. Um agente que dirige a tela precisa contornar obstáculos antes de poder prosseguir com a tarefa de fato.

**Complexidade da verificação**: Quando uma chamada de ferramenta termina, o harness recebe de volta um resultado estruturado com um campo de status. O harness sabe na hora se ela teve sucesso. Quando um agente de computer use clica em um botão, nada acontece de imediato além de a tela mudar. O harness precisa tirar um novo screenshot, enviá-lo ao modelo e fazer o modelo raciocinar sobre se o clique no botão funcionou. Essa etapa de interpretação é mais lenta e menos confiável do que um código de status estruturado.

**Variância de layout**: A mesma aplicação web renderiza de forma diferente conforme o tamanho da tela, o navegador, o nível de zoom, o framework de CSS e o estado do servidor. Um agente treinado ou testado em um desktop com zoom normal pode falhar em um celular ou com o zoom em 150 por cento. Mudanças de layout quebram coordenadas e exigem um novo grounding.

Essas falhas não se devem a um modelo ruim nem a prompting insuficiente. São consequências estruturais de observar e agir por meio de pixels em vez de APIs.

### Por que o WebArena importa

Durante anos, agentes de computer use foram avaliados por anedotas: um fornecedor mostrava um vídeo de um agente fazendo algo impressionante, mas não havia uma forma sistemática de medir se os agentes estavam de fato melhorando, nem onde estavam os maiores problemas de confiabilidade. Fornecedores diferentes usavam ambientes diferentes, então os resultados não eram comparáveis. Isso dificultava separar progresso real de marketing.

O paper do WebArena (Zhou et al., 2023) criou um ambiente de benchmark padronizado e auto-hospedado: um conjunto realista de sites e aplicações web montado em um servidor privado, com instruções de tarefa e verificações de correção. O trabalho do agente é concluir tarefas como reservar um voo, postar uma avaliação ou configurar uma opção. Uma tarefa só é considerada bem-sucedida se as ações do agente produzirem o resultado correto e verificável (um voo é reservado, uma avaliação é postada).

O WebArena tornou três coisas possíveis:

Primeiro, expôs a verdadeira lacuna de confiabilidade. Agentes que dirigem a tela, que pareciam impressionantes em vídeos de marketing, tinham taxas de sucesso na faixa de 10 a 20 por cento em tarefas web realistas de vários passos. Isso foi um alerta: a tecnologia era muito menos confiável do que as anedotas sugeriam.

Segundo, permitiu aos pesquisadores medir quais modos de falha dominam. Rodando muitas trajetórias de agentes e categorizando as falhas, os pesquisadores descobriram que erros de grounding, obstáculos do ambiente e mudanças de layout respondiam por uma grande fração das falhas, e não erros de lógica ou falta de raciocínio. Isso direcionou o esforço para mitigações que de fato ajudam.

Terceiro, forneceu um padrão compartilhado. Equipes diferentes podiam rodar seus agentes no mesmo benchmark e comparar resultados. O progresso passou a ser mensurável em vez de declarado.

### Mitigações e trade-offs

Várias estratégias reduzem as falhas de agentes que dirigem a tela, cada uma com custos:

**Ferramentas cientes de estrutura** (mencionadas na Lição 25): Em vez de apenas um screenshot bruto, a ferramenta devolve informação estruturada sobre os elementos da página (botões, campos de formulário, seus nomes e posições). O modelo referencia elementos pelo nome em vez de coordenadas. O harness traduz o nome em coordenadas no momento da ação. Isso recupera confiabilidade porque o harness pode recalcular as coordenadas se o layout muda, sem pedir ao modelo que reestime.

Trade-off: Você perde a generalidade de "funciona em qualquer GUI". Ferramentas cientes de estrutura funcionam para páginas web com HTML semântico, mas falham para aplicações desktop, PDFs, jogos ou interfaces para as quais a ferramenta não foi projetada.

**Interação explícita com elementos**: Em vez de emitir coordenadas de pixel, o modelo emite uma referência como "clique no elemento com id submit_button" ou "preencha o campo rotulado email". O harness usa APIs do navegador (JavaScript, árvores de acessibilidade ou inspeção do DOM) para encontrar o elemento e interagir com ele.

Trade-off: O harness volta a ser específico da aplicação. Você precisa construir ferramental para a plataforma que lhe interessa (web, desktop, mobile).

**Detecção e recuperação de obstáculos**: O agente verifica periodicamente se um popup ou banner está bloqueando a interface e toma medidas para fechá-lo ou dispensá-lo antes de prosseguir.

Trade-off: Acrescenta complexidade e latência; exige que o agente reconheça obstáculos sobre os quais não foi explicitamente informado.

**Verificação em vários passos**: Depois de cada ação, o agente tira um screenshot e faz um turno extra de raciocínio (não contado contra os turnos da tarefa principal) para verificar se a ação teve sucesso como pretendido antes de seguir adiante.

Trade-off: Aumenta o uso de tokens e a latência.

A ideia-chave é que nenhuma mitigação sozinha corrige todas as falhas. Cada uma trata de um ou dois modos de falha, mas introduz nova complexidade ou perde generalidade. Um sistema de produção muitas vezes combina várias.

### Como isso molda o diagnóstico

Quando um agente que dirige a tela falha, conhecer esses modos de falha molda como você diagnostica:

- Se a trajetória mostra uma sequência de cliques que faz sentido mas cai nos lugares errados, suspeite de erros de grounding e de variância de layout.
- Se a trajetória mostra o agente executando uma ação que deveria ter funcionado, mas o screenshot seguinte não mostra mudança, verifique se há obstáculos (popups, spinners de carregamento) ou confira se a ação de fato foi executada.
- Se o agente funcionou em uma máquina ou nível de zoom, mas falhou em outra tarefa idêntica em uma configuração diferente, suspeite de renderização específica do ambiente.
- Se o agente conclui a mesma tarefa com sucesso 80 por cento das vezes, mas às vezes falha em condições idênticas, suspeite de instabilidade por timing (um elemento dinâmico ainda não carregado) ou de uma variante de layout que você ainda não viu.

Essa é a disciplina de diagnóstico: conhecer os prováveis modos de falha impede que você acrescente prompts às cegas e, em vez disso, aponta para o problema real.

## Prática

1. ▢ Um agente conclui com sucesso uma tarefa no seu desktop com nível de zoom normal. Quando você roda o mesmo agente exatamente no mesmo site com o zoom do navegador em 125 por cento, ele falha no primeiro clique. Qual é o modo de falha mais provável?

<details markdown="1"><summary>Verificação</summary>

Um erro de grounding combinado com variância de layout. Com zoom normal, as coordenadas estavam corretas. Com zoom de 125 por cento, o mesmo elemento foi renderizado em coordenadas diferentes. O agente estimou as coordenadas com base na aparência visual no novo nível de zoom, mas provavelmente estimou mal, ou reutilizou coordenadas de um screenshot em cache no nível de zoom antigo. A correção não é um raciocínio melhor; é um ferramental ciente de estrutura que recalcule as coordenadas, ou garantir que o agente tire um screenshot novo no nível de zoom atual.

</details>

2. ▢ A trajetória de um agente mostra que ele clicou em um botão com sucesso no turno três. O botão não está mais visível no screenshot do turno quatro; um diálogo modal apareceu. No turno quatro, o agente tenta clicar no mesmo botão nas mesmas coordenadas, e o clique cai no modal. O agente então reclama que não consegue encontrar o botão. A falha é um erro de grounding?

<details markdown="1"><summary>Dica</summary>

O grounding na verdade estava correto no turno quatro; as coordenadas ainda apontavam para onde o botão estava antes. O problema não são as coordenadas em si.

</details>

<details markdown="1"><summary>Verificação</summary>

Não, isto é um problema de obstáculo, e não um erro de grounding. O raciocínio do agente era sólido: ele decidiu que o botão ainda deveria ser clicável. O grounding estava preciso: as coordenadas apontavam corretamente para a localização anterior do botão. Mas o ambiente mudou (um modal apareceu), e o agente não detectou nem tratou o obstáculo. A correção é detecção e recuperação de obstáculos, e não uma estimativa de coordenadas melhor.

</details>

3. ▢ Você está decidindo se usa uma ferramenta de navegador ciente de estrutura (que devolve nomes e posições de elementos) ou uma ferramenta de screenshot bruto para o seu agente. Sua aplicação é um painel JavaScript customizado com elementos renderizados dinamicamente, sem estrutura HTML semântica e com elementos que se movem durante as interações. A documentação da ferramenta diz que ferramentas cientes de estrutura funcionam melhor em "aplicações web semânticas e padrão". Qual você deve escolher?

    - a) A ferramenta ciente de estrutura, porque é mais nova e mais sofisticada
    - b) A ferramenta de screenshot bruto, porque sua aplicação não é HTML semântico
    - c) A ferramenta ciente de estrutura mesmo assim, e complementá-la com JavaScript customizado
    - d) Qualquer uma é equivalente para agentes que dirigem a tela

<details markdown="1"><summary>Verificação</summary>

**b)** A ferramenta de screenshot bruto é a melhor escolha para uma aplicação customizada, dinâmica e fora do padrão. Ferramentas cientes de estrutura dependem de HTML semântico e IDs estáveis, que o seu painel pode não ter. Um screenshot bruto permite ao modelo interpretar visualmente a interface dinâmica. O trade-off é a fragilidade do grounding, mas tentar usar ferramental ciente de estrutura em uma interface não suportada provavelmente falharia de qualquer forma. **a)** está errada porque mais novo não significa melhor para o seu caso de uso. **c)** acrescenta complexidade; se a ferramenta não suporta bem a sua interface, o complemento customizado pode não ajudar. **d)** está errada porque as ferramentas têm modos de falha diferentes para tipos diferentes de aplicação.

</details>

4. ▢ Você roda um agente no benchmark do WebArena e ele tem sucesso em 15 por cento das tarefas. Você melhora o system prompt com instruções mais claras e dicas de raciocínio. Em um novo teste, ele tem sucesso em 16 por cento. O que essa pequena melhoria diz sobre a provável causa das falhas restantes?

<details markdown="1"><summary>Verificação</summary>

Sugere que a maioria das falhas não se deve ao raciocínio nem à clareza das instruções. As melhorias de prompting renderam ganhos mínimos. As falhas provavelmente são estruturais: erros de grounding, variância de layout, obstáculos, problemas de verificação ou outros fatores que instruções melhores sozinhas não corrigem. Para melhorar mais, você precisaria investigar quais modos de falha de fato dominam (lendo trajetórias) e então aplicar mitigações direcionadas como ferramental ciente de estrutura, detecção de obstáculos ou melhor estimativa de coordenadas.

</details>

## Prática no mundo real

- [ ] Leia o resumo e a introdução do paper do WebArena (arxiv.org/abs/2307.13854). Liste as três categorias de tarefa mencionadas e anote um exemplo de modo de falha descrito em cada uma.

- [ ] Pegue a trajetória de um agente de computer use ou de navegador de uma fonte pública (documentação, blog, GitHub). Categorize cada falha (se houver) como: erro de grounding, obstáculo do ambiente, falha de verificação, variância de layout ou erro de lógica. Qual categoria aparece com mais frequência?

- [ ] Amanhã: Projete um cenário de teste que exporia especificamente erros de grounding. Que propriedades a página web ou interface de teste precisaria ter? Depois projete um cenário diferente que exporia falhas no tratamento de obstáculos. Escreva um parágrafo descrevendo como você mediria se um agente trata os obstáculos corretamente.

## Para ir além

- [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
