---
title: "28. Erros de ferramenta em cascata e argumentos alucinados"
description: "Um erro de ferramenta levando a decisões erradas, entrando em espiral de confusão, e argumentos bem tipados mas falsos que schemas não conseguem pegar"
type: lesson
---

# Lição 28. Erros de ferramenta em cascata e argumentos alucinados

**Ligação com a missão:** Identificar falhas em cascata e argumentos alucinados em uma trajetória permite diagnosticar as falhas do agente em sua verdadeira origem, quebrando a cadeia antes que entre em espiral, em vez de remendar sintomas a jusante.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 27](0027-loops-and-context-poisoning.md)

## Aquecimento

1. ▢ Da Lição 27: Qual é a diferença entre um loop repetitivo e o envenenamento de contexto?

<details markdown="1"><summary>Verificação</summary>

Um loop repetitivo é barulhento: o agente chama a mesma ferramenta com os mesmos argumentos repetidamente, sem progresso. O envenenamento é silencioso: o modelo declara um fato falso ou alucinado uma vez, e todo turno seguinte o trata em silêncio como verdade estabelecida.

</details>

2. ▢ Da Lição 4: O que o schema JSON de uma ferramenta valida?

<details markdown="1"><summary>Verificação</summary>

Um schema valida a estrutura e o tipo de um argumento: que os campos obrigatórios estão presentes, que os valores correspondem ao tipo declarado (string, número, booleano), que as listas têm o tipo de elemento certo e que restrições como enum ou minLength são atendidas. Ele não valida se o valor é verdadeiro nem se se refere a algo real.

</details>

## Saiba isto

### Falhas em cascata: um erro leva a outro

Uma falha em cascata é quando um erro de ferramenta leva a uma decisão seguinte incorreta, que leva a outro erro, afastando-se da tarefa em espiral. Cada falha agrava a confusão em vez de resolvê-la.

Eis um exemplo passo a passo:

Turno 2: O agente chama search_files(directory="/config") para encontrar um arquivo de configuração. O diretório não existe. A ferramenta devolve um erro: "directory not found".

O harness anexa esse erro à transcrição. Até aqui, tudo bem.

Turno 3: O modelo lê o erro e decide: "O diretório home padrão não existe. Devo estar em um ambiente diferente. Vou tentar /etc/config em vez disso." Esse é um raciocínio razoável com base em informação incompleta. O modelo chama search_files(directory="/etc/config").

Turno 4: A busca tem sucesso, mas devolve resultados que não correspondem ao que o agente procura. O modelo, já comprometido com o caminho /etc/config do turno 3, decide: "Esses resultados são bons o bastante. Vou usar o primeiro." O modelo agora tem o arquivo errado.

Turno 5: O agente lê o arquivo errado. O conteúdo não corresponde ao que ele espera. Em vez de reconhecer a discrepância, o modelo decide: "O formato do arquivo deve ter mudado. Vou interpretá-lo de uma forma mais tolerante." O agente continua, ainda construindo sobre a base errada.

Turno 6 até N: Cada decisão agrava o erro original. O agente agora raciocina a partir de uma base falsa e não consegue se recuperar sem voltar atrás de forma significativa.

A razão de as falhas em cascata acontecerem: quando uma ferramenta devolve um erro, o modelo precisa fazer uma suposição sobre o porquê. O diretório está faltando? É um erro de permissão? A sintaxe do caminho está errada? O modelo dá um palpite e prossegue. Se o palpite está errado, a próxima chamada de ferramenta é construída sobre essa suposição errada. E a cadeia desce a partir daí.

A proteção por contagem de erros da Lição 6 acabará parando o loop, mas o para depois de a cascata ter crescido, e não na origem.

### Argumentos alucinados: bem tipados, mas falsos

Um argumento alucinado é quando o modelo inventa um valor de aparência plausível, mas factualmente errado, para o argumento de uma ferramenta. O valor é bem formado e passa na validação do schema, mas simplesmente não corresponde a nada real.

Isso é diferente de um erro de campo obrigatório ausente (Lição 3-5). Um campo ausente produz um erro explícito de validação do schema que o modelo consegue ver e ao qual consegue reagir. Um argumento alucinado passa pela validação em silêncio.

Exemplos:

- O modelo deve buscar um usuário pelo nome de usuário. Ele chama get_user(username="alice_smith"), mas o nome de usuário real é "asmith". O schema aceita a string; a chamada falha a jusante porque o nome de usuário não existe.
- O modelo precisa chamar um endpoint de API e inventa o caminho: call_api(endpoint="/api/v2/users/search"). O endpoint não existe, mas parece plausível. O schema o valida como string; a chamada HTTP falha com 404.
- Pede-se ao modelo que chame uma função pelo nome e ele inventa um nome: call_function(name="validate_order"). A função não existe, mas a string é bem formada. A chamada só falha com "function not found" em tempo de execução.

Por que isso é pior do que um erro de validação de schema: quando o schema rejeita algo (campo ausente, tipo errado), o modelo recebe feedback imediato e pode corrigir. Quando um argumento é bem tipado mas falso, o erro acontece a jusante, muitas vezes de forma enigmática ("user not found", "404 not found", "function not found"). O modelo não entende de imediato que o valor que inventou foi o problema; pode, em vez disso, culpar o serviço ("o banco de dados de usuários está quebrado") ou o ambiente ("a API não está rodando") e tomar uma decisão errada com base nesse mau diagnóstico.

Se a falha em cascata da seção anterior começa com um argumento alucinado, a cascata é pior: o modelo está construindo uma cadeia de raciocínio sobre um valor que inventou e não sabe que inventou.

### Mitigações: validação e eco

A mitigação central é fazer os argumentos alucinados falharem mais depressa e com mais clareza, e dar ao modelo visibilidade do que de fato aconteceu.

**Validar contra um conjunto conhecido**: Se uma ferramenta recebe um argumento que deveria se referir a algo real (um nome de usuário, um nome de função, um endpoint), a ferramenta deve validar que ele existe. Em vez de falhar em silêncio a jusante, a ferramenta devolve um erro explícito: "user alice_smith not found; valid users are: alice_s, alice_brown, alicia_m". Isso dá ao modelo feedback imediato e um conjunto de opções para escolher.

**Ecoar o valor resolvido**: Depois que uma chamada de ferramenta tem sucesso, não devolva apenas "success". Devolva aquilo sobre o que de fato se agiu. Exemplo:

Em vez de:

```text
Tool result: Success
```

Devolva:

```text
Tool result: Successfully updated order 12345. Order status is now CONFIRMED.
```

Assim, se o argumento do modelo foi alucinado mas por acaso correspondeu a algo não pretendido, o eco torna a discrepância visível. O modelo vê "chamei com o ID de pedido 12345, e a ferramenta relatou ter atualizado o pedido 12345", e pode notar se eles batem.

**Exigir confirmação explícita para operações de alto risco**: Se uma chamada de ferramenta vai alterar dados ou executar uma ação, faça o harness pedir ao modelo que confirme o valor real antes de executar. O modelo vê "você está prestes a atualizar o usuário username_alice_smith; confirma?" e pode pegar uma alucinação nesse ponto.

### Falhas em cascata na trajetória

Quando você lê uma trajetória e identifica uma cascata:

1. Identifique o primeiro erro (turno N): uma ferramenta devolve um resultado ou erro inesperado.
2. Confira o turno N+1: que suposição o modelo fez sobre por que o erro aconteceu?
3. Rastreie para frente: a decisão seguinte do modelo decorre dessa suposição?
4. Se a suposição estava errada, a cascata começou.

A lição de diagnóstico: o erro no turno N não é o problema que você deve tentar corrigir refazendo o prompt. O problema é o mau diagnóstico que o modelo fez do erro no turno N+1. Corrija a ferramenta para ser mais clara sobre o que deu errado, ou dê ao modelo opções melhores para lidar com essa classe de erro, ou endureça as condições de parada para que a cascata não cresça.

## Prática

1. ▢ Um agente está importando dados de um arquivo CSV. No turno três, ele chama parse_csv(filename="data.csv"). A ferramenta devolve um erro: "file not found". No turno quatro, o modelo diz "O arquivo deve estar compactado. Vou descompactá-lo primeiro" e chama decompress(filename="data.csv.gz"). Essa ferramenta também falha com "file not found". No turno cinco, o modelo tenta outra interpretação do erro: "Talvez o arquivo esteja em um subdiretório" e chama search_for_file(pattern="data*"). Isso tem sucesso e encontra "data_backup.csv". No turno seis, ele interpreta o arquivo de backup, que tem colunas diferentes das esperadas, e a interpretação tem sucesso mas produz lixo. Isso é uma falha em cascata, e onde ela se originou?

<details markdown="1"><summary>Verificação</summary>

Sim, isto é uma falha em cascata. Ela se originou no turno 3, quando o parse_csv inicial falhou. O modelo fez um mau diagnóstico do erro: supôs que o arquivo estava compactado ou movido, quando o problema real provavelmente era só o nome do arquivo ou o caminho. A cada turno, o modelo fez uma suposição diferente, e cada suposição levou a uma ação diferente, nenhuma das quais corrigiu o problema subjacente. No turno 6, o agente está trabalhando com o arquivo errado (data_backup.csv em vez de data.csv), e a saída com lixo é a consequência. A correção não é um raciocínio melhor no modelo; é tornar a mensagem de erro inicial mais clara. A ferramenta deveria devolver "file data.csv not found in current directory; files found: data_backup.csv, old_data.csv". Com essa informação, o modelo poderia ter escolhido o arquivo de backup explicitamente no turno 4, em vez de passar pelos turnos 4 e 5 de mau diagnóstico.

</details>

2. ▢ Um agente está atualizando registros de clientes. No turno dois, o modelo chama update_customer(customer_id=987654, status="inactive"). O schema aceita o inteiro e a string. A ferramenta devolve "customer not found". No turno três, o modelo, confuso, chama list_customers(). Isso devolve uma lista de todos os clientes. No turno quatro, o modelo escolhe o primeiro cliente da lista e chama update_customer(customer_id=100001, status="inactive"). Isso tem sucesso. Mas o agente deveria atualizar o cliente 987654, e não o 100001. Por que o argumento alucinado no turno dois não produziu um erro óbvio ao qual o modelo pudesse reagir?

<details markdown="1"><summary>Dica</summary>

Pense na diferença entre um erro de validação de schema e o comportamento em tempo de execução de uma ferramenta ao receber um valor bem tipado mas inválido.

</details>

<details markdown="1"><summary>Verificação</summary>

O schema não rejeitou o argumento porque 987654 é um inteiro válido. A ferramenta o aceitou e o consultou, apenas para falhar em tempo de execução com "customer not found". A mensagem de erro era clara ("customer not found"), mas o modelo a interpretou mal: em vez de concluir "o cliente 987654 não existe, preciso encontrar o ID certo", concluiu "há algo errado em como estou consultando, vou tentar uma abordagem diferente". Um design melhor da ferramenta devolveria: "customer 987654 not found; customers exist in the range 100001 to 150000". Isso torna a discrepância explícita e dá ao modelo um intervalo concreto com que trabalhar, evitando a cascata.

</details>

3. ▢ Você está construindo uma ferramenta que recebe um caminho de arquivo como argumento. O schema diz que o caminho deve ser uma string. Você espera que os modelos ocasionalmente inventem caminhos que não existem. Qual destas escolhas de design melhor evitaria que argumentos alucinados criem falhas em cascata?

    - a) Aceitar qualquer caminho em string e falhar com um "file error" genérico quando o caminho não existe
    - b) Validar o caminho contra uma lista de diretórios permitidos; rejeitar caminhos fora da lista permitida com um erro claro
    - c) Aceitar qualquer caminho e devolver uma mensagem de sucesso mesmo se o arquivo não existe, para o modelo achar que a operação teve sucesso
    - d) Exigir que o modelo passe dois argumentos: o caminho e um booleano confirmando que o caminho está correto

<details markdown="1"><summary>Verificação</summary>

**b)** Validar contra uma lista de diretórios permitidos e rejeitar caminhos inválidos com um erro claro. Isso faz os caminhos alucinados falharem depressa e de forma explícita, dando ao modelo feedback imediato. O modelo pode então escolher da lista permitida. **a)** ainda deixa a cascata crescer porque o erro é genérico e não ajuda o modelo a entender o que deu errado. **c)** é perigosa; mascara o problema e leva a cascatas porque o modelo acha que teve sucesso quando não teve. **d)** exige lógica extra no harness e não resolve o problema; um modelo pode alucinar o caminho e confirmá-lo mesmo assim.

</details>

4. ▢ Um agente deve buscar dados de uma API. No turno dois, ele chama fetch_api(endpoint="/api/v1/customers/123"). O endpoint não existe, e a ferramenta devolve um erro 404. No turno três, o modelo diz "O servidor da API deve estar fora do ar" e chama check_service_health(). Isso devolve "service is up and responding". No turno quatro, o modelo diz "A API deve ter mudado. Vou tentar sem o número da versão" e chama fetch_api(endpoint="/api/customers/123"). Isso também falha com 404. Que mudança de design na primeira ferramenta teria evitado a cascata?

<details markdown="1"><summary>Verificação</summary>

A primeira chamada de ferramenta deveria ter devolvido mais informação do que apenas "404 not found". Poderia devolver: "endpoint /api/v1/customers/123 not found (404); valid endpoints include: /api/v2/customers/{id}, /api/v2/orders/{id}". Com essa informação, o modelo teria entendido de imediato que o número da versão estava errado, e não o serviço, e poderia ter ajustado o endpoint no turno 3 em vez de passar pelos turnos 3 e 4 de cascata. A cascata aconteceu porque a mensagem de erro não explicava o problema real.

</details>

## Prática no mundo real

- [ ] Encontre a trajetória de um agente que mostra uma falha. Leia-a e identifique: há uma cadeia em cascata de decisões, em que cada decisão agrava a confusão? Se sim, em que turno a cascata se originou? O que uma mensagem de erro mais clara teria feito?

- [ ] Projete uma ferramenta (escolha qualquer ferramenta com que você trabalha ou que você projetou). Escreva a mensagem de erro que a ferramenta devolve atualmente para um caso comum de falha. Agora reescreva-a para incluir: o que estava errado, o que era esperado e quais são as alternativas válidas. Como essa mensagem de erro mais clara mudaria a capacidade de um modelo de diagnosticar o problema?

- [ ] Amanhã: Construa um pequeno harness de teste que chama uma ferramenta com um argumento alucinado (um valor que a ferramenta não reconhece). Observe a mensagem de erro que a ferramenta devolve. Depois modifique a ferramenta para validar contra um conjunto conhecido e devolver um erro mais claro. Rode o mesmo argumento alucinado de novo e compare as duas mensagens de erro. Escreva um parágrafo descrevendo como o erro mais claro mudaria o diagnóstico da falha por um agente.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
