---
title: "4. Schemas de parâmetros e quem executa o quê"
description: "Como schemas JSON restringem o que um modelo pode enviar e a diferença entre ferramentas de cliente e de servidor"
type: lesson
---

# Lição 4. Schemas de parâmetros e quem executa o quê

**Ligação com a missão:** Escrever o loop de agente para uma tarefa dada e nomear o que cada mensagem do contexto está fazendo e o que encerra o loop.
**Fonte principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Pré-requisitos:** [Lição 3](0003-the-wire-format-of-a-tool-call.md)

## Aquecimento

1. ▢ Quando você envia a definição de uma ferramenta a um provedor de modelos, que papel o schema JSON desempenha?

<details markdown="1"><summary>Verificação</summary>

Ele descreve quais argumentos a ferramenta aceita: nomes, tipos e restrições. O modelo usa o schema para decidir o que enviar quando chama a ferramenta. Um schema bem formado evita que o modelo envie argumentos inválidos ou malformados.

</details>

2. ▢ Quando um modelo chama uma ferramenta e o harness recebe a chamada, como o harness sabe se deve executá-la localmente ou enviá-la a um provedor?

<details markdown="1"><summary>Verificação</summary>

Você precisa dizer isso ao harness ao definir a ferramenta: marcá-la como ferramenta de cliente (executar localmente) ou de servidor (o provedor cuida disso). O modelo nunca sabe a diferença; ele só vê o nome e o schema.

</details>

## Saiba isto

### Schemas como proteção

Um schema JSON faz dois trabalhos. Primeiro, documenta o que a ferramenta espera: nomes das propriedades, tipos, se cada propriedade é opcional ou obrigatória. Aqui está um exemplo simples:

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "The city name"},
    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature scale"}
  },
  "required": ["city"]
}
```

Esse schema diz: uma ferramenta recebe um objeto com um `city` obrigatório (string) e um `units` opcional (ou "celsius" ou "fahrenheit"). O modelo lê isso e sabe que sempre deve informar uma cidade, mas pode omitir as unidades.

Segundo, um schema atua como restrição. Quando um modelo chama a ferramenta, ele só pode enviar valores que correspondam ao schema. Se o schema diz que `units` deve ser uma de duas strings, o modelo não pode enviar "kelvin" nem um número. Schemas estritos evitam categorias inteiras de chamadas malformadas sem que o harness precise validá-las.

### O que acontece quando faltam campos obrigatórios

Se um modelo omite um campo obrigatório, a API do provedor levanta um erro. A maioria dos frameworks o captura e o envia de volta ao modelo como resultado de ferramenta: "Error: missing required field 'city'". O modelo então tem a chance de corrigir. Isso não é uma falha; é uma parte normal do loop. Um schema bem descrito reduz a frequência com que isso acontece, porque o modelo lê o schema com atenção.

### Ferramentas de cliente e ferramentas de servidor

Uma **ferramenta de cliente** é uma função no seu próprio código que o harness executa. Você é dono da implementação:

```python
def get_weather(city: str, units: str = "celsius"):
    # Your code to fetch weather
    return f"18{units[0]}, partly cloudy"
```

Quando o modelo chama `get_weather`, o seu harness executa a sua função e coleta o resultado.

Uma **ferramenta de servidor** é algo que o provedor executa em sua própria infraestrutura: uma busca na web, execução de código em um sandbox, acesso ao sistema de arquivos ou uma chamada a uma API hospedada. Você define o que ela faz (nome e schema), mas nunca escreve a implementação. O provedor a executa, coleta o resultado, e o harness o lê na resposta.

### Por que a distinção importa

Quando você diz "o modelo chamou uma ferramenta", está sendo vago com a linguagem. O modelo nunca executa nada. Ele emite um pedido estruturado dizendo "execute esta ferramenta com estes argumentos". Um harness recebe esse pedido e o executa, seja:

1. Chamando uma função que você escreveu (ferramenta de cliente), ou
2. Pedindo ao provedor que execute algo hospedado (ferramenta de servidor), ou
3. Enviando-o a um serviço de terceiros pela rede.

O modelo não se importa com qual dos três é. A distinção é sua: ela afeta onde o código vive, como você o escreve e onde as falhas podem ocorrer.

### Por que isso importa para o loop

Em um loop de agente, o modelo gera chamadas de ferramenta e o harness as executa. Se uma ferramenta falha, o resultado é um resultado de ferramenta carregando um erro, e não uma exceção que derruba o loop. Isso vale quer a ferramenta seja de cliente, quer de servidor:

- Uma ferramenta de cliente devolve um erro porque a rede caiu, a consulta ao banco falhou ou a sua lógica de validação rejeitou a entrada.
- Uma ferramenta de servidor devolve um erro porque o sandbox do provedor estourou o tempo, o código levantou uma exceção ou o limite de taxa da API foi atingido.

De qualquer forma, o erro é só mais um resultado de ferramenta, e o modelo decide o que fazer em seguida.

### Permissões e ferramentas de servidor

Uma ferramenta de servidor acrescenta uma pergunta: o modelo tem permissão para chamá-la? Se você dá a um modelo acesso a execução de código, leitura de arquivos ou acesso à web, você está confiando nele (dentro da fronteira que o schema define) para usar essa capacidade com segurança. Isso é uma decisão de segurança, não técnica. O schema impõe quais argumentos a ferramenta pode receber, mas o schema não pode impedir que o modelo use a capacidade para algo que você não pretendia. É por isso que o design do conjunto de ferramentas importa, e por que nem toda ferramenta é apropriada para todo agente.

## Prática

1. ▢ O schema de uma ferramenta exige um campo `query` (string), mas não tem nenhum campo `max_results` definido. O modelo pode enviar um argumento `max_results`? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não, em um schema estrito. Definições de schema JSON podem permitir ou proibir propriedades extras. Se o schema não menciona `max_results`, o modelo não pode enviá-lo (ou ele será rejeitado pelo provedor). O schema é exaustivo: só as propriedades listadas podem aparecer, a menos que o schema permita explicitamente propriedades adicionais.

</details>

2. ▢ Você tem uma ferramenta de cliente que consulta um banco de dados. O schema diz que `user_id` é obrigatório, mas o modelo envia uma chamada sem ele. O que acontece em seguida?

<details markdown="1"><summary>Dica</summary>

O que o harness faz quando o provedor rejeita uma chamada malformada?

</details>

<details markdown="1"><summary>Verificação</summary>

O provedor a rejeita, e o harness envia o erro de volta ao modelo como resultado de ferramenta: "Error: missing required field 'user_id'". O modelo lê esse erro e tem a chance de corrigir a chamada. O loop não falha; o erro é um resultado normal.

</details>

3. ▢ Qual afirmação descreve melhor o que acontece quando um modelo chama uma ferramenta de servidor em comparação com uma de cliente?

    - a) Uma ferramenta de servidor roda na sua infraestrutura; uma ferramenta de cliente roda na infraestrutura do provedor
    - b) O modelo envia um pedido pela ferramenta; o harness decide onde executá-la
    - c) Uma ferramenta de servidor sempre termina mais rápido porque o provedor a otimiza
    - d) Você escreve a implementação de ambas, mas de forma diferente

<details markdown="1"><summary>Verificação</summary>

**b)** O modelo emite o mesmo pedido estruturado nos dois casos. O harness lê a definição da ferramenta, decide se ela é de cliente ou de servidor e encaminha a execução de acordo. (a) está invertida: ferramentas de cliente são suas, ferramentas de servidor são do provedor. (c) é falsa: a velocidade depende da implementação, não de ser de servidor ou de cliente. (d) está parcialmente certa, mas ignora que você nunca escreve ferramentas de servidor, apenas as define.

</details>

4. ▢ Você define uma ferramenta de servidor "search_the_web" com um schema que exige apenas um campo `query`. O modelo a chama com `query="python", limit=5`. O que o provedor faz?

<details markdown="1"><summary>Verificação</summary>

Ou executa a chamada apenas com a consulta e ignora o limite, ou rejeita a chamada porque o schema não permite o campo extra `limit`. O resultado depende de a definição do schema permitir ou não propriedades adicionais. Se o schema é estrito (o padrão), o campo extra é um erro.

</details>

## Prática no mundo real

- [ ] Encontre ou escreva um schema de ferramenta para uma tarefa real (buscar, recuperar, calcular ou obter). Marque quais campos são obrigatórios, quais têm restrições (enums, comprimento de string, intervalos numéricos) e quais são opcionais. Reescreva a descrição de um campo para ficar mais clara.
- [ ] Rode um agente ou escreva um harness que chame uma ferramenta e envie intencionalmente um argumento inválido (omita um campo obrigatório, envie o tipo errado, envie um valor fora de um enum). Observe como o provedor responde e como o seu harness ou framework lida com isso.
- [ ] Amanhã: projete uma ferramenta de cliente e uma ferramenta de servidor para a mesma tarefa (por exemplo, "listar arquivos"). Escreva schemas para ambas. Explique um trade-off entre onde cada ferramenta vive.

## Para ir além

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
