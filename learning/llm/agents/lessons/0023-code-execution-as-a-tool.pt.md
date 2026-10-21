---
title: "23. Execução de código como ferramenta"
description: "Dar a um agente uma única ferramenta de execução de código em sandbox em vez de muitas ferramentas individuais e estreitas"
type: lesson
---

# Lição 23. Execução de código como ferramenta

**Ligação com a missão:** Para decidir se uma dada tarefa precisa mesmo de um agente, você precisa entender que uma única ferramenta de execução de código pode substituir dezenas de ferramentas estreitas, reduzindo o custo em tokens e a latência, ao mesmo tempo que exige uma imposição robusta do sandbox contra código arbitrário.
**Fonte principal:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Pré-requisitos:** [Lição 22](0022-sandboxing-and-approval-gates.md)

## Aquecimento

1. ▢ Na Lição 22, distinguimos um sandbox de um portão de aprovação. O que cada um faz, e qual você usaria para evitar que o modelo apague um arquivo por acidente?

<details markdown="1"><summary>Verificação</summary>

Um sandbox é uma fronteira de execução que impede o código de alcançar certos recursos (como arquivos fora de um diretório permitido). Um portão de aprovação é um ponto de verificação humano antes de ações arriscadas. Para evitar a exclusão acidental, você usaria um sandbox que restringe a ferramenta a escrever apenas dentro de uma árvore de diretórios segura, de modo que, mesmo que o modelo peça a exclusão, o sandbox a rejeite. Um portão de aprovação pausaria e pediria aprovação humana antes de tentar a exclusão, mas não a impediria se aprovada.

</details>

2. ▢ A Lição 21 introduziu a ideia de descoberta de ferramentas em escala: o modelo pode inspecionar que ferramentas existem em vez de carregar toda definição no contexto. Que problema isso resolve?

<details markdown="1"><summary>Verificação</summary>

Quando você tem centenas de ferramentas, pré-carregar a definição, o nome, a descrição e o schema de parâmetros de cada ferramenta na janela de contexto do modelo esgota tokens e dificulta ao modelo raciocinar sobre qual ferramenta chamar. A descoberta de ferramentas permite ao modelo pedir informações sobre as ferramentas disponíveis sob demanda ou chamar um endpoint de introspecção para explorar capacidades, de modo que a lista completa não precisa viver no contexto inicial.

</details>

## Saiba isto

### Execução de código como alternativa a muitas ferramentas estreitas

Considere um cenário de análise de dados. Sem execução de código, você poderia expor estas ferramentas ao modelo:

- list_files: devolve uma lista de arquivos de um diretório
- read_csv: lê um arquivo CSV e devolve as primeiras N linhas
- compute_mean: calcula a média de uma coluna
- compute_median: calcula a mediana de uma coluna
- filter_rows: filtra uma tabela por uma condição
- sort_by: ordena uma tabela por uma coluna
- write_csv: escreve uma tabela de volta em um arquivo

O modelo agora precisa decidir qual ferramenta chamar e em que ordem. Ele pode chamar read_csv, depois filter_rows, depois compute_mean: três idas e voltas pelo loop do modelo. Cada ida e volta queima tokens raciocinando sobre qual ferramenta chamar em seguida, e cada definição de ferramenta custa tokens na janela de contexto inicial.

Em vez disso, dê ao modelo uma ferramenta: um interpretador de código em sandbox. O modelo escreve um programa Python curto:

```python
import pandas as pd

data = pd.read_csv('data.csv')
filtered = data[data['age'] > 30]
result = filtered['salary'].mean()
print(result)
```

O modelo o executa uma vez e obtém a resposta. Vantagens: uma chamada de ferramenta em vez de três, uma definição de ferramenta em vez de sete, e o modelo pode encadear operações em um único turno sem raciocinar de novo sobre qual ferramenta chamar em seguida.

### Benefícios de custo e latência

Essa abordagem reduz tanto o custo em tokens quanto a latência:

- Custo em tokens: Você paga por uma definição de ferramenta em vez de muitas, e a sobrecarga de raciocínio do modelo sobre qual ferramenta chamar se reduz a escrever código comum, o que o modelo já faz com eficiência.
- Latência: Uma ida e volta de chamada de ferramenta em vez de três ou sete significa que o tempo de relógio do agente cai proporcionalmente.

Para agentes rodando em escala ou com requisitos de tempo real, essas economias se acumulam.

### Ligação com a descoberta de ferramentas em escala

A Lição 21 introduziu a ideia de que, em vez de pré-carregar toda definição de ferramenta no contexto, o modelo pode explorar as capacidades disponíveis dinamicamente. A execução de código é uma instanciação concreta desse princípio: o modelo não precisa de toda ferramenta de transformação de dados pré-carregada porque pode escrever código para fazer a transformação ele mesmo. As capacidades disponíveis (funções, bibliotecas, utilitários do sistema) são descobertas quando o código roda, e não no contexto inicial.

Em alguns sistemas, a própria ferramenta de execução de código pode ter um mecanismo de descoberta: uma função que o modelo pode chamar para listar que bibliotecas estão disponíveis, que fontes de dados consegue alcançar ou que comandos de sistema estão disponíveis. Isso empilha descoberta sobre descoberta.

### O que um sandbox precisa impor contra código arbitrário

Na Lição 22, vimos que um sandbox impõe fronteiras ao que a execução de uma ferramenta consegue alcançar: caminhos do sistema de arquivos, hosts de rede, limites de recursos. Quando a ferramenta é "execute código arbitrário que o modelo escreveu", o sandbox precisa impor essas fronteiras contra um código muito mais expressivo e imprevisível do que uma chamada de ferramenta fixa com um schema JSON conhecido.

O modelo pode escrever código que:

- Tenta escapar da fronteira do sistema de arquivos usando links simbólicos, truques de travessia de caminho (/../..) ou chamando utilitários do sistema como find ou ls para sondar fora da fronteira.
- Escreve código de rede que tenta alcançar hosts fora da lista de permissão.
- Cria loops infinitos, funções recursivas ou loops que alocam memória tentando esgotar os recursos.
- Chama funções ou métodos que o código acha que existem, mas que o harness pretende proibir.

O sandbox precisa ser robusto o bastante para conter tudo isso. Isso é mais difícil do que colocar em sandbox uma ferramenta fixa porque a superfície do código é ilimitada. Um sandbox de execução de código de verdade costuma rodar o código em um contêiner ou processo isolado com regras de seccomp, namespaces de rede e cgroups de recursos, e não apenas verificações de permissão de sistema de arquivos.

### Quando usar execução de código contra ferramentas estreitas

A execução de código é poderosa, mas introduz complexidade de sandbox. Você deve preferi-la quando:

- O modelo precisa combinar muitas operações pequenas que de outro modo exigiriam muitas idas e voltas.
- As operações são algorítmicas ou focadas em transformação de dados (filtragem, agregação, cálculo, conversão de formato).
- As capacidades disponíveis são bem definidas e relativamente estáveis.

Você deve ficar com ferramentas estreitas e feitas para um fim quando:

- A operação é genuinamente de alto risco e se beneficia de supervisão humana explícita (enviar um e-mail, postar publicamente, gastar dinheiro).
- A segurança da operação depende de validar entradas ou saídas de maneiras específicas do domínio que o harness entende mas o código não.
- A operação é rara e a economia de tokens de uma única ferramenta não supera a complexidade do sandbox.

As duas abordagens podem coexistir: um agente pode ter uma ferramenta de execução de código para manipulação de dados e ferramentas estreitas, com portão de aprovação, para enviar e-mails ou publicar resultados.

## Prática

1. ▢ Você tem um agente que atualmente usa sete ferramentas separadas para manipulação de strings: split_string, join_strings, uppercase, lowercase, replace_substring, reverse_string e trim_whitespace. Você poderia substituir as sete por uma única ferramenta de execução de código? O que você ganharia e o que perderia?

<details markdown="1"><summary>Verificação</summary>

Sim, poderia. O modelo ganharia: uma definição de ferramenta em vez de sete, uma chamada de ferramenta para realizar uma operação complexa de string em vez de sete idas e voltas, e a capacidade de escrever código legível ("result = text.upper()") em vez de adivinhar nomes de ferramentas. Você perderia: guardrails explícitos para cada operação (cada ferramenta poderia validar a entrada) e latência determinística (a execução de código agora é variável conforme o que o modelo escreve). Para manipulação de strings, a abordagem de execução de código geralmente vence porque as operações são simples e o harness consegue impor uma fronteira de sistema de arquivos ou de recursos sem lógica específica do domínio.

</details>

2. ▢ Você está projetando um agente para um sistema de saúde que pode ler prontuários de pacientes e gerar sugestões de diagnóstico. Você deve expor isso por uma ferramenta de execução de código em que o modelo escreve o próprio código de acesso a dados, ou por ferramentas estreitas como read_patient_record, filter_by_condition e compute_risk_score?

<details markdown="1"><summary>Dica</summary>

Considere o que "segurança" significa em um contexto de saúde. O que o harness precisa impor, e um sandbox de código de uso geral consegue impor isso, ou é preciso lógica específica do domínio?

</details>

<details markdown="1"><summary>Verificação</summary>

Ferramentas estreitas são melhores aqui. Um sistema de saúde tem requisitos rígidos de conformidade (HIPAA, log de auditoria, controle de acesso a dados) que o harness provavelmente impõe por meio de lógica específica do domínio, e não de sandboxing de sistema de arquivos. Uma ferramenta estreita read_patient_record pode incluir verificações de autorização, log de auditoria e redação de dados; uma ferramenta de execução de código não consegue impor isso com facilidade, porque o harness teria de inspecionar o código que o modelo escreveu, o que anula o propósito da execução de código. As apostas altas também tornam os portões de aprovação mais valiosos. Prefira ferramentas estreitas e auditáveis quando a segurança da operação depende de lógica de negócio específica do domínio, e não de fronteiras de sistema de arquivos.

</details>

3. ▢ Qual destas afirmações sobre execução de código é verdadeira?

    - a) A execução de código é sempre mais rápida do que usar ferramentas separadas porque reduz idas e voltas, mesmo para operações únicas e simples.
    - b) A execução de código reduz o custo em tokens porque uma definição de ferramenta substitui muitas, mas só economiza latência se o modelo encadeia várias operações.
    - c) A execução de código elimina a necessidade de sandboxes porque o código é confiável.
    - d) A execução de código não exige portões de aprovação porque o harness pode inspecionar o código antes de ele rodar.

<details markdown="1"><summary>Verificação</summary>

**b)** A execução de código reduz o custo em tokens porque uma definição de ferramenta substitui muitas, mas só economiza latência se o modelo encadeia várias operações. A economia de tokens é real (uma definição em vez de muitas). A economia de latência só importa se o modelo está fazendo várias operações que de outro modo exigiriam várias idas e voltas; para uma única operação, o tempo é parecido ou pior. A opção a está errada (operações únicas não se beneficiam). A opção c está errada (a execução de código precisa de sandboxes robustos porque o código é arbitrário). A opção d está errada (portões de aprovação ainda fazem sentido para operações de alto risco, e a pré-inspeção não evita todos os erros).

</details>

4. ▢ Explique por que o trabalho do sandbox fica mais difícil quando a ferramenta é "execução de código" em vez de uma ferramenta específica como "delete_file". Qual é um cenário concreto em que essa dificuldade importa?

<details markdown="1"><summary>Verificação</summary>

Com uma ferramenta específica, o harness sabe de antemão o que a ferramenta fará e pode impor uma fronteira nesse ponto específico (a ferramenta delete_file só pode tocar arquivos em um diretório seguro). Com a execução de código, o harness não sabe o que o código fará até ele rodar; o código pode chamar utilitários do sistema, abrir sockets de rede ou usar recursos da linguagem que o harness não espera. Um cenário concreto: o modelo escreve código que chama subprocess.Popen para executar um comando de shell como "ls /../.." e sondar o sistema de arquivos além da fronteira pretendida. Um sandbox só de permissão de sistema de arquivos não vai impedir isso; o sandbox precisa de regras de seccomp ou de um contêiner para impedir chamadas de sistema arbitrárias. É por isso que sandboxes de execução de código costumam ser mais complexos do que sandboxes de ferramentas estreitas.

</details>

5. ▢ Seu agente usa execução de código para analisar dados. O modelo escreve código que deveria ler de um arquivo CSV, mas em vez disso escreve código que tenta baixar um arquivo da internet. O sandbox impõe nenhum acesso à rede. O que acontece, e isso é uma falha do sandbox?

<details markdown="1"><summary>Verificação</summary>

O código roda, tenta a chamada de rede, e a operação de rede é rejeitada ou bloqueia. Isso não é uma falha do sandbox; é o sandbox funcionando como pretendido. O trabalho do sandbox é impedir que o código alcance recursos fora de sua fronteira, e não garantir que o código esteja correto ou faça o que o modelo pretendia. Uma falha do sandbox seria se a chamada de rede tivesse sucesso apesar da regra de nenhuma rede. O erro do modelo (escrever o código errado) é separado do trabalho do harness (impor fronteiras).

</details>

## Prática no mundo real

- [ ] Liste as ferramentas que o seu próprio trabalho ou um sistema familiar usa. Identifique um conjunto de três ou mais ferramentas intimamente relacionadas e esboce como elas poderiam ser substituídas por uma ferramenta de execução de código. De que você precisaria para ter confiança no sandbox e fazer essa mudança?
- [ ] Escreva um programa simples de análise de dados (filtrar uma tabela, calcular um agregado, ordenar). Imagine que você é o modelo. Quantas idas e voltas por um loop de chamada de ferramentas isso levaria com ferramentas separadas, e quantas com execução de código?
- [ ] Amanhã: Revise o artigo "Code Execution with MCP" e identifique uma escolha de design no sandbox (limite de recursos, fronteira de sistema de arquivos, restrição de rede) e explique por que essa fronteira em particular importa para o caso de uso do artigo.

## Para ir além

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
