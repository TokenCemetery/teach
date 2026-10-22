---
title: "27. Loops e envenenamento de contexto"
description: "Dois modos de falha visíveis em uma trajetória, loops repetitivos e envenenamento silencioso de contexto, e como reconhecer cada um"
type: lesson
---

# Lição 27. Loops e envenenamento de contexto

**Ligação com a missão:** Diagnosticar um agente que falha a partir da trajetória exige reconhecer quando um agente está preso repetindo a mesma ação e quando está construindo em silêncio sobre uma afirmação falsa, para que você corrija a causa raiz em vez de acrescentar mais instruções.
**Fonte principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Pré-requisitos:** [Lição 26](0026-why-browser-agents-fail-differently.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 26: Por que um agente que dirige a tela falha com mais frequência do que um agente que chama ferramentas com raciocínio idêntico?

<details markdown="1"><summary>Verificação</summary>

Um agente que dirige a tela observa por pixels e age por coordenadas, que são referências frágeis que quebram com mudanças de layout, estados de carregamento e obstáculos. Esses modos de falha são estruturais e persistem mesmo com prompting melhor.

</details>

2. ▢ Da Lição 7: Se um harness anexa o resultado de uma ferramenta aos seus logs internos mas nunca o anexa à transcrição, o que o modelo sabe sobre esse resultado?

<details markdown="1"><summary>Verificação</summary>

Nada. O modelo só vê a transcrição. Registrar em log não basta; o resultado precisa ser anexado à transcrição para o modelo saber que aconteceu no turno seguinte.

</details>

## Saiba isto

### Loops repetitivos: quando um agente fica preso

Um loop repetitivo é quando um agente chama a mesma ferramenta com argumentos iguais ou quase idênticos turno após turno, mesmo que a tarefa não avance. É barulhento e visível em uma trajetória.

A causa subjacente costuma ser uma de duas coisas:

Primeiro, o agente não percebe que um resultado contradisse ou deixou de sustentar o seu plano. O modelo emitiu um comando esperando um certo resultado, recebeu um resultado diferente ou nulo, mas não atualizou seu modelo interno do mundo. No turno seguinte, tenta a mesma coisa de novo, esperando um resultado diferente.

Exemplo: Um agente quer criar um arquivo `config.json` em um diretório. A chamada de ferramenta falha com "permission denied". O harness anexa esse erro. Mas no turno seguinte, o modelo chama a mesma ferramenta com o mesmo caminho, como se o erro nunca tivesse acontecido. O raciocínio do modelo era algo como "vou tentar criar o arquivo", e, quando isso devolveu um erro, ele não passou para "devo tentar um caminho diferente ou pedir permissão". Isso é uma falha de raciocínio tornada visível pela repetição.

Segundo, as condições de parada do harness são frouxas demais. O loop continua rodando porque nenhuma condição disparou para pará-lo. Com proteções rígidas de contagem de erros (Lição 6), o loop sai depois de algumas tentativas falhas e traz a falha à tona para diagnóstico. Com proteções frouxas, o loop continua, repetindo a mesma ação que falha dez ou vinte vezes antes de finalmente parar.

Como identificar um loop repetitivo em uma trajetória:

1. Varra em busca de turnos consecutivos com o mesmo nome de ferramenta.
2. Compare os argumentos: são idênticos ou quase idênticos?
3. Confira os resultados: são idênticos, inalterados ou todos falhas?
4. Procure texto de raciocínio repetido: o modelo usa a mesma redação e o mesmo raciocínio ao longo de vários turnos?

Se as três primeiras verificações são verdadeiras, o agente está em um loop repetitivo. O texto de raciocínio repetido (verificação 4) confirma isso, mas não é obrigatório.

### Envenenamento de contexto: quando afirmações falsas viram verdade absoluta

O envenenamento de contexto é diferente. Ao contrário de um loop repetitivo, que é barulhento e visível, o envenenamento é silencioso: o modelo afirma algo falso ou alucinado uma vez, e então todo turno seguinte o trata como um fato estabelecido.

Veja como acontece:

No turno cinco, o modelo diz: "Consultei o banco de dados e descobri que o ID do cliente é 12345." Mas nenhuma chamada de ferramenta recuperou esse fato. Nada em nenhum resultado de ferramenta anterior dizia o ID do cliente. O modelo o inventou, ou lembrou errado, ou chutou com base em um padrão.

Essa afirmação é anexada à transcrição como qualquer outra coisa. Parece verdade absoluta: está ali, no histórico da conversa, declarada como um fato.

No turno seis, o modelo constrói sobre ela: "Agora vou consultar a conta do cliente 12345." Ele chama uma ferramenta com esse ID. A ferramenta pode falhar ("o cliente 12345 não existe") ou, pior, pode ter sucesso e agir sobre o cliente errado.

No turno sete, o modelo se comprometeu ainda mais: "Vejo que a conta do cliente 12345 mostra um saldo de..." e a cascata continua.

No turno quinze, você está lendo a trajetória e vê uma enorme cadeia de raciocínios e decisões, todas ancoradas na afirmação falsa de que o ID do cliente é 12345. O modelo não está sendo burro. O modelo está sendo consistente: a transcrição diz que o ID do cliente é 12345, então o modelo raciocina com base nisso. Mas a transcrição está envenenada.

Por que isso é diferente de um argumento de ferramenta alucinado (Lição 28): quando um modelo inventa o argumento de uma função, como um caminho de arquivo, a ferramenta geralmente falha com um erro explícito ("file not found"). O envenenamento é pior porque muitas vezes não é pego de imediato. Uma afirmação falsa em linguagem natural pode ficar na transcrição sem ser contestada, e o modelo construirá sobre ela.

Como identificar envenenamento em uma trajetória:

1. Procure um turno em que o modelo declara um fato específico (um número, um nome, uma data, um ID) com alta confiança e sem ressalva.
2. Rastreie para trás: alguma chamada de ferramenta ou resultado de ferramenta anterior de fato sustentou essa afirmação? Ou o modelo a declarou do nada?
3. Se não tinha sustentação, rastreie para frente: os turnos posteriores dependem dessa afirmação? As chamadas de ferramenta posteriores usam esse valor como argumento?
4. Se sim nos dois casos, o contexto está envenenado.

A disciplina de diagnóstico que esta lição vai construindo: um loop se diagnostica olhando o que se repete; o envenenamento se diagnostica rastreando uma afirmação falsa até sua origem e para frente até suas consequências.

### Por que o context rot agrava o envenenamento

O context rot (Lição 11) é o problema mais amplo: conforme a transcrição cresce, os turnos antigos ficam menos relevantes, a atenção do modelo se desloca e a acurácia se degrada. O context rot acontece em toda execução longa de agente, até em uma saudável.

O envenenamento é mais grave. Uma única afirmação falsa na transcrição pode ancorar todo o raciocínio posterior, e, se a afirmação está enterrada entre dezenas de turnos, é difícil de identificar. O modelo não consegue rejeitar com facilidade uma afirmação que já está na própria transcrição; em vez disso, a trata como fato estabelecido.

A mitigação é diagnóstica e preventiva:

- Leia as trajetórias com cuidado e fique atento a afirmações sem sustentação que o modelo faz em linguagem natural.
- Ao projetar ferramentas, faça-as ecoar o que foi resolvido: em vez de só "success", devolva "successfully updated customer ID 67890", para que o modelo confirme o valor real.
- Use condições de parada e contagens de erros rígidas para que os loops saiam depressa e impeçam cascatas de más decisões construídas sobre um envenenamento inicial.

## Prática

1. ▢ Você lê a trajetória de um agente e vê a mesma chamada de ferramenta, `get_user_by_email(email="bob@example.com")`, repetida nos turnos 3, 5, 7 e 9. Em cada vez, o resultado é "user not found". No turno 10, o modelo chama `send_email(recipient="bob@example.com")`. Isso é um loop repetitivo?

<details markdown="1"><summary>Verificação</summary>

Não, isto não é um loop repetitivo. O agente está chamando repetidamente a mesma ferramenta de consulta e recebendo a mesma falha, mas depois divergiu e chamou outra ferramenta (send_email). O agente adaptou sua estratégia depois de a consulta falhar. Um loop repetitivo seria se o modelo continuasse chamando get_user_by_email nos turnos 10, 11, 12. Isto se parece mais com envenenamento de contexto: o agente pode ter feito uma suposição falsa no turno 2 (como "tenho o e-mail do usuário") que nunca foi confirmada e agora age sobre ela. Leia o contexto completo da trajetória para identificar se o turno 2 ou um anterior fez uma afirmação sem sustentação sobre o e-mail do Bob.

</details>

2. ▢ Um agente está escrevendo um arquivo. No turno três, ele chama write_file(path="output.txt", content="...") e recebe um erro "permission denied". No turno quatro, o modelo diz "vou tentar uma abordagem diferente" e chama create_directory(path="/tmp/"), que tem sucesso. Então, no turno cinco, ele chama write_file(path="/tmp/myfile.txt", content="..."). Isso é um loop repetitivo?

<details markdown="1"><summary>Dica</summary>

Veja se o modelo está chamando a mesma ferramenta com os mesmos argumentos e se o raciocínio dele mudou entre os turnos.

</details>

<details markdown="1"><summary>Verificação</summary>

Não, isto não é um loop repetitivo. Embora o agente tenha encontrado um erro, ele se adaptou: mudou seu raciocínio ("tentar uma abordagem diferente"), chamou uma ferramenta diferente e mudou o caminho do arquivo na tentativa de escrita. A estratégia do modelo evoluiu. Um loop repetitivo mostraria a mesma chamada write_file com "output.txt" repetida sem mudanças. Esse agente mostrou um caminho razoável de resolução de problemas, mesmo que o objetivo final (escrever no local original) tenha sido abandonado.

</details>

3. ▢ Você está lendo uma trajetória em que, no turno 12, o modelo declara "The API key for this service is sk-1234567890". Você procura de volta nos turnos 1 a 11 e não encontra nenhuma chamada de ferramenta que devolveu essa chave. Você procura para frente nos turnos 13 a 20 e descobre que os turnos 15, 17 e 19 usam essa chave em chamadas de API. O que aconteceu?

    - a) O modelo raciocinou corretamente e inferiu a chave a partir do contexto
    - b) O contexto está envenenado: uma afirmação sem sustentação agora ancora várias chamadas de ferramenta posteriores
    - c) O modelo está em um loop repetitivo, chamando a mesma ferramenta de API repetidamente
    - d) O harness deixou de anexar um resultado de ferramenta que continha a chave

<details markdown="1"><summary>Verificação</summary>

**b)** O contexto está envenenado. O modelo declarou um fato (a chave de API) sem nenhuma chamada de ferramenta anterior que o sustentasse, e então vários turnos posteriores dependem dessa afirmação. Essa é a definição de manual de envenenamento: uma afirmação sem sustentação vira a base para o raciocínio posterior. Você não consegue dizer, só pela trajetória, se o harness deixou de anexar um resultado (d) ou se o modelo alucinou; de qualquer forma, a transcrição agora está envenenada. **a)** está errada porque inferência não é o mesmo que verificação de verdade absoluta. **c)** está errada; isto não é um loop repetitivo porque as chamadas de ferramenta não são idênticas e o modelo não está repetindo a mesma ação.

</details>

4. ▢ Um colega mostra a trajetória de um agente que falha. Os três primeiros turnos tiveram sucesso. No turno quatro, o modelo está preso em um loop chamando list_files(directory="/data") repetidamente, sem mudança. O texto de raciocínio do modelo diz "preciso encontrar o arquivo alvo". Qual é a causa raiz mais provável: um erro de lógica no raciocínio do modelo, ou uma condição de parada rígida que deveria permitir mais turnos?

<details markdown="1"><summary>Verificação</summary>

Isto é um erro de lógica no raciocínio do modelo, e não um problema de condição de parada. A condição de parada não é rígida o bastante (o loop está se repetindo), mas a correção não é afrouxá-la ainda mais. O problema é que o modelo chamou a mesma ferramenta repetidamente sem mudar o argumento nem o raciocínio. Afrouxar a condição de parada apenas o deixaria repetir mais. A correção é diagnosticar por que o modelo não entendeu o resultado da primeira chamada a list_files, ou não soube como prosseguir. A condição de parada deve ser endurecida para sair depois de uma ou duas repetições que falharam, trazendo o problema à tona para diagnóstico humano em vez de deixá-lo se repetir sem fim.

</details>

## Prática no mundo real

- [ ] Encontre a trajetória de um agente online (em documentação, um repositório do GitHub ou um post de blog). Leia-a e identifique: ela mostra algum loop repetitivo? Mostra envenenamento de contexto? Escreva um parágrafo descrevendo o que você encontrou e como identificou.

- [ ] Rode um agente em uma tarefa que você espera que falhe. Examine deliberadamente a trajetória em busca de afirmações sem sustentação que o modelo faz em linguagem natural (afirmações não respaldadas por resultados de ferramenta anteriores). Para cada uma, anote o que aconteceria se o agente prosseguisse com base nessa afirmação falsa.

- [ ] Amanhã: Projete uma ferramenta que ajudaria a evitar o envenenamento de contexto. Ela poderia ecoar valores resolvidos, adicionar checksums, incluir timestamps ou validar contra um conjunto conhecido. Escreva um parágrafo descrevendo o design da sua ferramenta e explique como ela torna afirmações envenenadas mais fáceis de identificar em uma trajetória.

## Para ir além

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
