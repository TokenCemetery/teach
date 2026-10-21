---
title: "20. MCP: ferramentas, recursos e prompts"
description: "O Model Context Protocol como uma interface padronizada para harnesses de agente descobrirem e invocarem ferramentas externas, lerem dados e usarem templates"
type: lesson
---

# Lição 20. MCP: ferramentas, recursos e prompts

**Ligação com a missão:** Entender o MCP como um protocolo neutro quanto a provedor que resolve o problema de integração, para que você possa raciocinar sobre quais ferramentas um agente pode acessar e como adicionar novas sem reescrever o harness.
**Fonte principal:** [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
**Pré-requisitos:** [Lição 19](0019-coordination-cost.md), [Ferramenta](../GLOSSARY.md)

## Aquecimento

1. ▢ Na Lição 3, você aprendeu que uma ferramenta tem nome, descrição e schema de parâmetros. Quando o seu harness roda, de onde ele obtém essas definições: do modelo, do código do harness ou de outro lugar?

<details markdown="1"><summary>Verificação</summary>

Do código do harness. Quem escreve o harness escreve as definições de ferramenta à mão ou as carrega de um arquivo de configuração e depois conta ao modelo sobre elas antes de o loop começar.

</details>

2. ▢ Quando você conecta um agente a uma nova fonte de dados (um banco de dados, uma API, um armazenamento de arquivos), quem faz o trabalho: o modelo, o harness ou ambos?

<details markdown="1"><summary>Verificação</summary>

Ambos. Quem escreve o harness escreve o código para integrar a fonte de dados (buscá-la, interpretá-la, tratar erros) e depois conta ao modelo sobre ela adicionando uma definição de ferramenta. O modelo decide se e quando chamá-la.

</details>

## Saiba isto

### O problema M vezes N

Sem um padrão compartilhado, conectar um harness de agente a ferramentas e fontes de dados externas exige trabalho de integração sob medida. Se o seu harness pode invocar N ferramentas ou fontes de dados diferentes, e há M equipes ou frameworks diferentes construindo agentes, você tem M*N integrações separadas: cada equipe escreve código próprio para falar com cada ferramenta ou fonte de dados.

O MCP (Model Context Protocol) resolve isso criando uma interface compartilhada que tanto o lado do harness quanto o lado da ferramenta podem implementar. Uma ferramenta ou fonte de dados implementa um servidor MCP. Qualquer harness compatível com MCP pode se conectar a ele. Um harness implementa um cliente MCP. Qualquer servidor compatível com MCP pode expor capacidades a ele. Agora você tem M+N integrações em vez de M*N.

Isso importa porque, sem ele, escalar um agente para usar mais ferramentas significa crescimento quadrático de código sob medida. Com o MCP, escalar significa construir ou conectar-se a mais servidores padronizados.

### Três primitivas

O MCP define três tipos de capacidades que um servidor pode expor a um cliente:

**Ferramentas** (comparáveis às ferramentas da Lição 3): ações que o modelo pode invocar. Uma ferramenta tem nome, descrição e schema de entrada. Quando o modelo decide chamá-la, o cliente envia a requisição ao servidor, que executa a ação e devolve um resultado. O modelo vê o resultado e continua. Isso é exatamente como as ferramentas de cliente e de servidor que você já conhece, mas a interface é padronizada, de modo que qualquer um dos lados pode ser trocado.

**Recursos**: dados que o cliente MCP pode ler diretamente, sem o modelo invocá-los como uma chamada de ferramenta. Um recurso pode ser um arquivo, um registro de banco de dados, uma página web ou uma resposta de API ao vivo. O cliente pode listar os recursos disponíveis e buscar um pelo nome. Isso é diferente de uma ferramenta porque o modelo não o invoca; o harness o lê e decide se coloca os dados no contexto ou o que fazer com eles. Os recursos permitem ao harness trazer informação relevante sem bloquear o turno do modelo nem acrescentar sobrecarga de chamada de ferramenta.

**Prompts** (templates de prompt): templates de prompt reutilizáveis que um servidor MCP expõe para um cliente preencher e usar. Um template de prompt pode ser "analise este código em busca de problemas de segurança" ou "resuma este documento". O cliente pode listar os templates de prompt disponíveis, buscar um pelo nome e preencher os parâmetros. Isso é distinto de ferramentas e recursos: em vez de executar uma ação ou buscar dados, o harness usa o template para construir uma mensagem a enviar ao modelo, incorporando-a às próprias instruções ou etapas de raciocínio do agente.

### Ciclo de vida básico

Um cliente se conecta a um servidor. Eles negociam capacidades: quais entre ferramentas, recursos e prompts este servidor em particular de fato suporta. O servidor anuncia o que tem; o cliente decide o que usar.

Depois, conforme o que o cliente suporta e o que o harness precisa:

- O cliente pode listar as ferramentas disponíveis e buscar seus schemas, e então apresentá-las ao modelo.
- O cliente pode listar os recursos disponíveis e buscar dados de forma proativa, usando o que aprende para informar as decisões do agente.
- O cliente pode listar os templates de prompt disponíveis e usá-los para construir instruções ou etapas de reflexão.

Um único servidor pode expor as três, ou apenas uma ou duas. O protocolo é simétrico: tanto o cliente quanto o servidor conhecem a interface, então qualquer um dos lados pode ser genérico.

### Transportes

Servidores MCP podem rodar localmente (via stdio, um canal simples de processo para pipe entre o harness e o servidor na mesma máquina) ou remotamente (via um transporte baseado em HTTP, em que o servidor roda em outra máquina ou serviço de nuvem). O transporte afeta a latência, o deployment e os modos de falha, mas não o protocolo em si. Um harness que suporta os dois transportes pode se conectar a um servidor MCP rodando localmente para iteração rápida e a um servidor MCP remoto para resiliência ou colaboração entre equipes.

## Prática

1. ▢ Você está construindo um agente que precisa ler de um banco de dados e chamar uma API web. O banco de dados da sua equipe tem um servidor MCP. A API web não tem. Você precisa escrever código de integração sob medida para os dois, ou apenas para um?

<details markdown="1"><summary>Verificação</summary>

Apenas um. O harness pode se conectar ao servidor MCP do banco de dados sem código sob medida. Para a API web, a sua equipe ainda escreve um wrapper (seja no harness ou como um novo servidor MCP em torno da API). Esse é o princípio M+N: o servidor MCP fez metade do trabalho por você.

</details>

2. ▢ Seu agente precisa verificar o clima e depois decidir se sugere uma atividade ao ar livre. Isso deve ser uma ferramenta (que o modelo invoca) ou um recurso (que o harness lê de forma proativa)?

<details markdown="1"><summary>Dica</summary>

Pense em quando o harness descobre o clima e em quando o modelo precisa saber. O modelo decide se pergunta, ou o harness sempre o busca?

</details>

<details markdown="1"><summary>Verificação</summary>

Depende. Se o clima é sempre relevante para a decisão, faça dele um recurso: o harness o busca antes de cada turno e o inclui no contexto. Se o clima só é relevante quando o modelo está considerando atividades ao ar livre, faça dele uma ferramenta: o modelo o pede quando precisa. Uma ferramenta deixa o modelo decidir quando olhar; um recurso alimenta informação que o harness sempre quer que o modelo tenha.

</details>

3. ▢ Seu agente usa três servidores MCP: um para e-mail, um para um calendário e um para um armazenamento de documentos. O servidor de e-mail suporta ferramentas e recursos. O servidor de calendário suporta apenas ferramentas. O servidor de documentos suporta ferramentas, recursos e prompts. Qual dos seguintes o harness pode fazer?

    - a) Usar recursos dos três servidores, já que os três suportam pelo menos ferramentas
    - b) Usar ferramentas dos três, recursos apenas de e-mail e documentos, e prompts apenas de documentos
    - c) Usar prompts dos três servidores
    - d) Usar ferramentas e recursos de todos os servidores igualmente

<details markdown="1"><summary>Verificação</summary>

b) O harness só pode usar o que cada servidor de fato expõe. O e-mail suporta ferramentas e recursos, então o harness pode usar os dois do e-mail. O calendário suporta apenas ferramentas. Os documentos suportam ferramentas, recursos e prompts. O harness negocia a capacidade por servidor e só chama o que é anunciado. Prompts só estão disponíveis no servidor de documentos, então c está errada. Nem todos os servidores suportam recursos, então a e d estão erradas.

</details>

4. ▢ Você está decidindo se implanta um servidor MCP localmente (stdio) ou remotamente (HTTP). Qual é o trade-off que você deve considerar?

<details markdown="1"><summary>Verificação</summary>

O local (stdio) é mais rápido e mais simples de configurar na mesma máquina, mas acopla o harness ao processo do servidor. O remoto (HTTP) significa que o servidor pode rodar em qualquer lugar e sobreviver a falhas do harness, mas acrescenta latência de rede e modos de falha (o servidor pode estar lento ou inalcançável). Nenhum dos dois muda o protocolo MCP em si; ambos funcionam da mesma forma para o cliente. Escolha conforme a latência que você tolera e se precisa de resiliência ou de acesso entre máquinas.

</details>

## Prática no mundo real

- [ ] Leia a especificação do Model Context Protocol em modelcontextprotocol.io e identifique um servidor MCP que já existe para algo do seu domínio (e-mail, documentos, bancos de dados, repositórios de código).
- [ ] Esboce a comparação M*N contra M+N para o seu próprio trabalho: liste M harnesses ou equipes e N ferramentas ou fontes de dados com que você se importa e estime quanto código de integração sob medida a abordagem M+N economizaria.
- [ ] Amanhã: Tente se conectar a um servidor MCP existente (por meio de um cliente que o suporte) e observe como as três primitivas (ferramentas, recursos, prompts) são realmente usadas na prática.

## Para ir além

- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
