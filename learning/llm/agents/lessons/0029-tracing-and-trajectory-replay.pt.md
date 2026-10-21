---
title: "29. Tracing e replay de trajetória"
description: "Usar convenções de trace neutras quanto a fornecedor para capturar execuções de agente e reproduzir trajetórias para percorrer falhas passo a passo"
type: lesson
---

# Lição 29. Tracing e replay de trajetória

**Ligação com a missão:** Registrar execuções de agente com traces estruturados e padronizados e poder reproduzir uma trajetória salva permite entregar a um colega o ponto exato da falha, percorrê-lo de forma independente e levar o diagnóstico em produção de "deixa eu olhar os logs" para "deixa eu percorrer a trajetória".
**Fonte principal:** [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
**Pré-requisitos:** [Lição 28](0028-cascading-tool-errors.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 28: Qual é a diferença entre um erro de validação de schema e um argumento alucinado?

<details markdown="1"><summary>Verificação</summary>

Um erro de validação de schema ocorre imediatamente quando um campo obrigatório está ausente ou um valor tem o tipo errado; o modelo recebe feedback explícito. Um argumento alucinado é um valor bem tipado que passa na validação mas não corresponde a nada real, então o erro acontece a jusante e o modelo pode fazer um mau diagnóstico de por que falhou.

</details>

2. ▢ Da Lição 7: Qual é a única peça de estado que você precisa persistir para retomar uma execução de agente a partir do turno N?

<details markdown="1"><summary>Verificação</summary>

A transcrição: o histórico completo da conversa até o turno N, incluindo cada resposta do modelo, chamada de ferramenta e resultado de ferramenta. Ao retomar, devolva essa transcrição ao modelo e continue o loop a partir do turno N+1.

</details>

## Saiba isto

### Traces, spans e convenções neutras quanto a fornecedor

Um trace é um registro estruturado e com marcas de tempo do que aconteceu durante uma execução de agente. É feito de spans, cada um representando uma operação discreta:

- Um span por chamada ao modelo (entrada: transcrição; saída: resposta do modelo e chamadas de ferramenta; tempo; tokens usados)
- Um span por execução de ferramenta (entrada: nome da ferramenta e argumentos; saída: resultado ou erro; tempo)
- Um span por iteração do loop (hora de início, hora de término, número do turno)

Sem uma convenção compartilhada, cada equipe e cada fornecedor nomeia essas coisas de forma diferente. Uma ferramenta pode chamar a entrada de uma chamada ao modelo de "prompt", outra a chama de "messages", outra de "input". Uma ferramenta chama a saída de "response", outra de "generated_text". Isso torna os traces incomparáveis: uma equipe que usa as ferramentas do fornecedor A não consegue ler com facilidade os traces do fornecedor B, e mudar de um fornecedor para outro significa reescrever toda a sua interpretação de traces.

As convenções semânticas GenAI do OpenTelemetry definem um vocabulário neutro quanto a fornecedor para esses spans e atributos. Elas padronizam que informação cada span deve carregar:

Um span de chamada ao modelo inclui: nome do modelo, total de tokens na entrada, total de tokens na saída, o esforço de raciocínio (se definido), chamadas de ferramenta solicitadas, motivo da parada.

Um span de execução de ferramenta inclui: nome da ferramenta, se é uma ferramenta de cliente ou de servidor, status do resultado da ferramenta (sucesso ou erro), se houve custo (para ferramentas de servidor), mensagem de erro se falhou.

O span de transação envolve tudo e inclui: número do turno do loop do agente, horas de início e término em tempo de relógio, se o turno teve sucesso ou falhou, qualquer decisão de parada tomada.

Como esses itens são padronizados, um trace produzido por um harness pode ser lido por qualquer ferramenta compatível com OpenTelemetry. O mesmo painel, script de análise ou visualização que funciona com os traces de uma equipe funciona com os de outra. É o mesmo princípio que padronizou os formatos de rede de chamadas de ferramenta na Lição 3: todos os conceitos subjacentes (loop do agente, chamada ao modelo, chamada de ferramenta) são os mesmos entre provedores, então um vocabulário padrão permite transitar entre eles.

### Por que traces estruturados importam para o diagnóstico

Os loops e o envenenamento da Lição 27, e as cascatas da Lição 28, são todos encontrados lendo uma trajetória com cuidado. Mas uma leitura cuidadosa só é viável se a trajetória está bem estruturada.

Imagine que você está tentando diagnosticar uma falha em uma execução de agente com 47 turnos e centenas de linhas de saída de log. Você tem instruções de print misturadas com mensagens de erro, resultados de ferramenta impressos como JSON e timestamps que podem ou não estar corretos. Você está lendo linha por linha, tentando montar o que aconteceu.

Agora imagine a mesma execução representada como um trace estruturado: cada span é marcado com um número de turno, cada chamada ao modelo é rotulada com o nome do modelo, cada chamada de ferramenta é rotulada com o nome da ferramenta. Você pode consultar o trace: "mostre todas as chamadas de ferramenta que falharam do turno 10 em diante" ou "mostre o texto de raciocínio que o modelo usou no turno 23" ou "mostre uma linha do tempo de quais spans rodaram em paralelo". Isso é dramaticamente mais rápido de diagnosticar.

Além disso, traces estruturados permitem automatizar parte do diagnóstico: uma regra simples pode sinalizar "detectar loops repetitivos encontrando spans consecutivos com o mesmo nome de ferramenta". Uma análise pós-execução pode sinalizar "detectar falhas em cascata procurando spans de erro seguidos de spans com nome de ferramenta diferente em sequência próxima". Esses padrões são difíceis de detectar em logs de formato livre; com dados estruturados, são diretos.

### Replay de trajetória: testando hipóteses

Como a transcrição é o único estado persistente do agente (Lição 7), você pode salvar uma trajetória e devolvê-la a uma execução nova em qualquer ponto. Isso se chama replay de trajetória.

Eis o que passa a ser possível:

**Reproduzir as condições exatas**: Um cliente relata que um agente falhou. Você salva a trajetória dele (a transcrição até o ponto da falha) e a entrega a uma execução nova do harness. A execução nova vê exatamente o que a original viu, então, se reproduz a mesma falha, você a confirmou. Se tem sucesso, você encontrou um problema no harness original ou no ambiente, e não na lógica do agente.

**Avançar a partir de uma falha**: Você identifica o turno em que as coisas deram errado (turno 12). Salva a trajetória até o turno 11, depois a modifica um pouco (talvez acrescentando uma nota na transcrição, ou mudando um resultado de ferramenta) e reproduz a partir do turno 12. O modelo, vendo a entrada modificada, pode tomar um caminho diferente. Isso permite testar "e se aquele resultado de ferramenta tivesse sido mais claro?" sem rodar todo o agente de novo desde o turno 1.

**Colaborar no diagnóstico**: Um colega pergunta "por que o agente falhou no turno 28?" Você entrega a trajetória até o turno 27 e uma descrição do que quer que ele observe. Ele pode reproduzi-la por conta própria, independentemente de você, e chegar à sua própria conclusão. Você está compartilhando o estado exato, e não apenas uma descrição dele.

**Construir um teste de regressão**: Você encontrou um bug e o corrigiu. Salve a trajetória que disparou o bug, reproduza-a com o harness corrigido e verifique que agora ela tem sucesso. Adicione isso à sua suíte de testes para que o bug não volte.

### Design prático de replay

Ao projetar o replay de trajetória, alguns detalhes importam:

**Salve a transcrição completa**, incluindo cada turno, cada chamada de ferramenta, cada resultado, cada erro. Não trunque nem amostre; o modelo precisa do contexto completo para raciocinar corretamente no replay.

**Inclua metadados do harness em uma seção separada e estruturada**: o número do turno, as contagens de tokens, as contagens de erros, as condições de parada que foram verificadas. Isso ajuda a reconstruir o estado exato, mesmo que você não tenha salvado tudo na transcrição.

**Coloque timestamp em cada span** para ver quanto tempo cada operação levou e se há lacunas inexplicadas (latência de rede, retries, backoffs).

**Torne o replay configurável**: permita que alguém reproduza a partir do turno N, ou reproduza com uma transcrição modificada (para testar hipóteses), ou reproduza com um modelo diferente para ver se o comportamento muda.

### Relação com outras ferramentas de diagnóstico

Traces estruturados não substituem a leitura cuidadosa de trajetórias. Eles a complementam. Você ainda precisa entender os modos de falha das Lições 27 e 28 (loops, envenenamento, cascatas) para saber que padrões está procurando. Mas um trace estruturado torna os padrões mais fáceis de ver e mais rápidos de extrair.

Combinados, formam uma disciplina: use traces para navegar a trajetória depressa, use seu conhecimento dos modos de falha para identificar o que importa e use o replay para verificar seu diagnóstico.

## Prática

1. ▢ Você está lendo um trace estruturado de uma execução de agente. O trace mostra: turno 1 (chamada ao modelo), turno 2 (chamada de ferramenta a search_files), turno 3 (chamada ao modelo), turno 4 (chamada de ferramenta a search_files com argumentos idênticos), turno 5 (chamada ao modelo), turno 6 (chamada de ferramenta a search_files de novo). Você confere o resultado da ferramenta em cada span e eles são idênticos. Com base apenas na estrutura do trace, que modo de falha você deve suspeitar?

<details markdown="1"><summary>Verificação</summary>

Isto parece um loop repetitivo da Lição 27: a mesma ferramenta está sendo chamada com argumentos idênticos nos turnos 2, 4 e 6, e os resultados são idênticos. O trace estruturado torna isso óbvio porque cada turno e cada chamada de ferramenta está rotulado. Em um log não estruturado, você teria de procurar manualmente o nome da ferramenta e os argumentos em muitas linhas.

</details>

2. ▢ Você está reproduzindo uma trajetória a partir do turno 15 para depurar uma falha no turno 30. Você devolve ao modelo a transcrição até o turno 14 e pede que ele continue. No seu replay, o agente toma um caminho diferente do original e tem sucesso. O que isso diz sobre a falha original?

<details markdown="1"><summary>Dica</summary>

Pense no que mudou entre a execução original e o replay, além da decisão do modelo.

</details>

<details markdown="1"><summary>Verificação</summary>

A falha original provavelmente foi causada por algo no harness ou no ambiente nos turnos 15 a 29, e não pelo raciocínio do modelo. Causas possíveis: uma ferramenta que se comportou de forma diferente do esperado na execução original, uma falha transitória (problema de rede, indisponibilidade de serviço, cota excedida) ou um elemento não determinístico (aleatoriedade nos resultados das ferramentas ou na amostragem do modelo). Como o replay teve sucesso com a mesma transcrição e o mesmo modelo, o problema não foi o treinamento nem o raciocínio do modelo; foram condições externas. Esse é um insight de diagnóstico que você não obteria apenas relendo a trajetória.

</details>

3. ▢ Você está projetando um schema de trace estruturado para o seu harness de agente usando as convenções do OpenTelemetry. Para um span de chamada de ferramenta, qual destes atributos é o mais importante para diagnosticar uma falha em cascata (Lição 28)?

    - a) O nome da ferramenta e os argumentos
    - b) O resultado da ferramenta ou a mensagem de erro
    - c) A duração em tempo de relógio da chamada de ferramenta
    - d) A versão do modelo que chamou a ferramenta

<details markdown="1"><summary>Verificação</summary>

**b)** O resultado da ferramenta ou a mensagem de erro é o mais importante para diagnosticar cascatas. Uma cascata começa quando o modelo faz um mau diagnóstico de um erro, então você precisa ver exatamente que mensagem de erro foi devolvida. Com uma mensagem de erro clara, você pode verificar se a decisão seguinte do modelo foi uma resposta razoável a esse erro. O nome da ferramenta e os argumentos (a) são secundários; mostram o que o modelo tentou, mas não se ele entendeu a falha. A duração (c) e a versão do modelo (d) são úteis para análise de desempenho e detecção de regressão, mas não são primários para o diagnóstico de cascatas.

</details>

4. ▢ Você salvou uma trajetória até o turno 10 e quer testar uma hipótese: "se o resultado da ferramenta no turno 5 tivesse incluído o ID do cliente, o agente teria tido sucesso em vez de entrar em um loop nos turnos 6 a 10." Como você modificaria a trajetória e a reproduziria para testar essa hipótese?

<details markdown="1"><summary>Verificação</summary>

Você editaria a transcrição: encontraria o resultado da ferramenta no turno 5 e acrescentaria a ele a informação do ID do cliente. Por exemplo, mudaria "Tool result: success" para "Tool result: successfully created account; customer ID is 98765". Depois reproduziria a partir do turno 6 com essa transcrição modificada. Se o agente agora tem sucesso, sua hipótese está confirmada: a informação faltante era a causa raiz. Se continua em loop, o problema está em outro lugar.

</details>

## Prática no mundo real

- [ ] Configure uma captura básica de traces para um agente a que você tem acesso. Em pelo menos uma execução, exporte o trace e examine sua estrutura. Identifique: ele segue um schema consistente? Você consegue encontrar depressa todas as chamadas ao modelo e todas as chamadas de ferramenta? Uma linguagem de consulta (como filtrar "todas as chamadas de ferramenta que falharam") seria útil para depurar?

- [ ] Salve uma trajetória de uma execução de agente (pelo menos 5 turnos). Reproduza-a a partir do meio (turno 3 ou 4) e observe se o replay produz os mesmos resultados ou resultados diferentes. Se diferentes, investigue por quê.

- [ ] Amanhã: Projete uma regra automatizada que detectaria um modo de falha da Lição 27 ou 28 em um trace estruturado. Escreva pseudocódigo ou SQL que consulta o trace e sinaliza a falha. Por exemplo, "sinalizar se a mesma ferramenta é chamada mais de duas vezes em turnos consecutivos com argumentos idênticos".

## Para ir além

- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
