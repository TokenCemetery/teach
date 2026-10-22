---
title: "16. Plan-then-execute e decomposição"
description: "O planejamento explícito de antemão como alternativa ao ReAct, quando usá-lo e como lidar com o replanejamento"
type: lesson
---

# Lição 16. Plan-then-execute e decomposição

**Ligação com a missão:** Para escolher entre um único prompt, um workflow fixo e um agente para uma dada tarefa, você precisa reconhecer quando a estrutura extra de um plano explícito vale o seu custo e quando a flexibilidade do ReAct é mais barata.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 15](0015-react-interleaving-reasoning-and-acting.md)

## Aquecimento

1. ▢ No ReAct, o que acontece depois que uma chamada de ferramenta executa e o harness anexa o resultado à transcrição?

<details markdown="1"><summary>Verificação</summary>

O turno seguinte do modelo recebe a transcrição incluindo a chamada de ferramenta e seu resultado. O modelo pode então emitir um novo raciocínio que reage ao que a ferramenta de fato devolveu, em vez de se agarrar a um plano pré-feito.

</details>

2. ▢ Descreva um cenário em que a adaptação passo a passo do ReAct é uma vantagem sobre um plano rígido feito de antemão.

<details markdown="1"><summary>Verificação</summary>

Qualquer cenário em que o ambiente pode surpreender o agente: uma busca não devolve nada (e não os dados esperados), uma ferramenta falha, um usuário dá um feedback que contradiz as premissas ou chega informação nova no meio da tarefa. Nesses casos, o ReAct permite ao modelo observar a surpresa e se adaptar, enquanto um plano rígido feito de antemão executaria às cegas os passos originais e falharia ou produziria resultados errados.

</details>

## Saiba isto

### Planejamento explícito e decomposição

Plan-then-execute é uma abordagem distinta do ReAct. Em vez de intercalar raciocínio e ação, o primeiro passo do agente é produzir uma lista explícita e ordenada de subtarefas ou ações. O modelo (ou um planejador separado) emite um plano em linguagem natural ou em forma estruturada. O harness então executa o plano passo a passo. Se o replanejamento é suportado, o harness pode pedir um novo plano se um passo falhar.

Decomposição é a ideia geral por trás disso: quebrar uma tarefa grande e ambígua em várias menores e bem definidas. Uma subtarefa menor é mais fácil de o modelo executar corretamente e mais fácil de uma pessoa verificar. Quer a decomposição aconteça de forma explícita (com um plano escrito) ou implícita (no raciocínio do ReAct a cada passo), o princípio é o mesmo.

### Quando o planejamento explícito compensa o custo

Um plano explícito ocupa espaço na transcrição e exige um turno extra do modelo (pelo menos um) antes de qualquer ação rodar. Isso é sobrecarga. Quando vale a pena pagá-la?

**Revisão humana antes da execução:** Se uma tarefa envolve apostas altas (chamar uma API que custa dinheiro, enviar um e-mail, apagar dados), uma pessoa pode ler o plano antes de o harness rodar qualquer ferramenta. A pessoa pode rejeitar o plano, pedir mudanças ou aprová-lo com confiança. Em contraste, o ReAct roda a primeira ação antes de uma pessoa ter visibilidade do que está para acontecer. Para tarefas em que a aprovação humana é exigida ou reduz o risco, um plano explícito é uma boa troca.

**Tarefas de vários passos com alto custo para ações erradas:** Se cada passo é caro de desfazer ou envolve alto risco, comprometer-se com um plano de antemão e fazer uma pessoa revisá-lo antes da execução reduz a chance de erros caros. Uma tarefa exploratória em que os passos são baratos (ler dados, fazer consultas que não custam nada) não precisa dessa sobrecarga.

**Tarefas com estrutura clara e estável:** Algumas tarefas se decompõem em uma sequência óbvia que não muda: "Baixar o arquivo A, interpretá-lo, transformá-lo, enviar o resultado." Se é improvável que os passos mudem no meio da execução, escrevê-los de antemão e executá-los é mais simples e barato do que raciocinar sobre cada passo do zero.

### O problema do plano obsoleto e o replanejamento

Aqui está o risco: o plano foi feito antes de qualquer ferramenta rodar. Se o passo 1 devia encontrar um arquivo, mas ele não existe, o plano do passo 2 pressupõe que o arquivo está lá. O passo 2 vai falhar ou produzir resultados errados. O harness então tem duas opções: continuar às cegas executando o plano obsoleto (e provavelmente falhar) ou disparar o replanejamento (pedir ao modelo que emita um novo plano dado o novo estado).

O replanejamento não é de graça: custa mais um turno do modelo, e a trajetória agora mostra várias etapas de plano, o que usa contexto. Mas o replanejamento muitas vezes é mais barato do que o ReAct para tarefas de alta estrutura, porque o modelo consegue pensar rapidamente o novo caminho em vez de raciocinar passo a passo.

Se o replanejamento não é suportado, um harness plan-then-execute vai falhar em silêncio ou com alarde quando a realidade não bate com o plano. É por isso que "você suporta replanejamento?" é uma pergunta de design essencial para agentes plan-then-execute.

### Decomposição sem planejamento explícito

Note que decomposição e planejamento explícito são ideias separadas. Um agente pode decompor tarefas de forma implícita, por meio de raciocínio no estilo ReAct a cada passo. O modelo raciocina "para resolver isto, preciso fazer X, depois Y, depois Z" e então faz X, observa o resultado, raciocina de novo e passa para Y. Isso é decomposição implícita. Um plano explícito escreve essa lista "X, Y, Z" como um artefato estruturado antes de a execução começar.

Para muitas tarefas, a decomposição implícita (ReAct) é mais simples e mais robusta. Use planejamento explícito quando a sobrecarga (revisão humana, clareza, estrutura) valer o custo.

### Comparando os três padrões

Só ação é o mais simples, mas o mais difícil de depurar. O ReAct acrescenta raciocínio e observação, tornando-o visível e adaptativo. Plan-then-execute acrescenta uma estrutura de antemão que pode ser revisada antes de qualquer ação rodar, ao custo de um turno extra do modelo e de uma possível obsolescência se as premissas do plano se quebrarem.

Escolha com base na sua tarefa e nas suas restrições:

- Tarefa exploratória curta, sem apostas altas? Use ReAct.
- Tarefa com passos claros que é improvável mudarem? Use plan-then-execute.
- Tarefa em que uma pessoa precisa revisar antes de a execução começar? Use plan-then-execute com um portão de aprovação.
- Tarefa em que os passos são caros e as falhas são custosas? Use plan-then-execute com suporte a replanejamento.

## Prática

1. ▢ Uma tarefa é "Registrar uma reclamação na prefeitura, verificar se foi recebida e notificar o usuário." Isso envolve preencher um formulário (não é grátis refazer), verificar um e-mail de confirmação e enviar um e-mail. O planejamento explícito ou o ReAct seria melhor para essa tarefa? Por quê?

<details markdown="1"><summary>Verificação</summary>

O planejamento explícito é melhor. Os passos são claros e estáveis: preencher o formulário, verificar a confirmação, enviar o e-mail. Não há razão para esperar que essa sequência mude no meio da execução. Uma pessoa deve revisar o plano antes de o formulário ser preenchido, já que esse passo não é fácil de desfazer. O ReAct funcionaria, mas rodaria o passo de preencher o formulário antes de uma pessoa poder revisá-lo, acrescentando risco.

</details>

2. ▢ Você está construindo um agente que investiga por que a conta de um usuário está bloqueada. O agente pode verificar o status da conta, pesquisar nos logs por logins que falharam, procurar uma flag de segurança ou consultar tickets de suporte, dependendo do que encontrar. O planejamento explícito ou o ReAct seria melhor?

<details markdown="1"><summary>Dica</summary>

Pense se a sequência de passos é conhecida de antemão ou se depende do que os passos anteriores devolvem.

</details>

<details markdown="1"><summary>Verificação</summary>

O ReAct é melhor. Os passos dependem do que o agente encontra em cada etapa. Se o status da conta mostra uma flag de segurança, o próximo passo é verificá-la. Se mostra um erro diferente, o próximo passo é outro. A sequência não pode ser escrita de antemão. O raciocínio e a observação passo a passo do ReAct são mais naturais do que tentar planejar todos os ramos possíveis.

</details>

3. ▢ Qual das alternativas a seguir descreve melhor quando o replanejamento se torna necessário em um agente plan-then-execute?

    - a) Sempre que o agente encontra qualquer chamada de ferramenta com um parâmetro que o plano não mencionou.
    - b) Quando uma chamada de ferramenta falha ou devolve dados inesperados que contradizem uma premissa do plano original.
    - c) Sempre que o usuário muda de ideia sobre a tarefa.
    - d) Depois de cada chamada de ferramenta, para garantir que o plano se mantenha atualizado.

<details markdown="1"><summary>Verificação</summary>

**b)** O replanejamento é disparado por falhas ou surpresas reais: uma ferramenta devolveu nada quando o plano esperava dados, uma chamada de API falhou ou uma busca não encontrou o que se esperava. a) está errada, ferramentas muitas vezes têm parâmetros que o plano não listou; isso não é um erro. c) está errada, mudanças do usuário são uma questão no nível da tarefa, não específica de plan-then-execute contra ReAct. d) está errada, replanejar depois de cada passo anula o propósito de ter um plano e é ineficiente.

</details>

4. ▢ O plano explícito de um agente é "Passo 1: Buscar a entrada do usuário. Passo 2: Resumir os resultados. Passo 3: Comparar o resumo com a pergunta original do usuário." Depois do passo 1, a busca não devolve resultados. O harness não suporta replanejamento. O que provavelmente vai acontecer?

<details markdown="1"><summary>Verificação</summary>

O passo 2 (resumir os resultados) vai falhar ou produzir saída errada porque não há resultados para resumir. O agente vai travar, devolver um erro ou produzir um resumo de nada. O harness não terá como mudar de rumo: estava comprometido com o plano desde o início. Esse é o custo de um harness plan-then-execute sem suporte a replanejamento. A correção é adicionar replanejamento (pedir ao modelo que faça um novo plano quando o passo 1 falha) ou mudar para ReAct, em que o modelo raciocinaria depois do resultado do passo 1 e decidiria tentar uma busca diferente.

</details>

## Prática no mundo real

- [ ] Pegue uma tarefa de vários passos que você faz com regularidade (por exemplo, processar um pedido, investigar um problema, revisar um documento quanto à conformidade). Escreva os passos que você realmente segue. Os passos sempre acontecem na mesma ordem, ou a ordem depende do que você encontra em cada passo? Se a ordem é fixa, esse é um candidato a plan-then-execute com aprovação explícita. Se a ordem é adaptativa, é um candidato a ReAct.
- [ ] Construa um pequeno agente plan-then-execute para uma tarefa de sequência fixa (por exemplo, baixar um arquivo, interpretá-lo, transformá-lo, enviá-lo). Rode-o cinco vezes com entradas diferentes e leia as trajetórias. O agente alguma vez falhou porque o plano original não batia com a realidade? Se sim, adicione um portão de replanejamento depois das chamadas de ferramenta que podem falhar.
- [ ] Amanhã: Encontre um agente existente que você construiu ou usou. Classifique-o como só ação, ReAct ou plan-then-execute com base na trajetória. Escreva uma nota de uma frase sobre por que esse padrão serve para a tarefa.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
