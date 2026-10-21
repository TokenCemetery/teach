---
title: "1. Chunking"
description: "A primeira escolha do pipeline, e a que toda etapa posterior herda"
type: lesson
---

# Lição 1. Chunking

**Ligação com a missão:** O chunking é a primeira decisão do pipeline que este workspace ensina, e toda etapa posterior (embeddings, busca híbrida, reranking) trabalha com o que um chunk lhe deu. Uma escolha ruim de chunking não pode ser consertada com reranking.
**Fonte principal:** [Artigo: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
**Pré-requisitos:** nenhum

## Saiba isto

### Por que um documento é dividido

Um pipeline de recuperação não gera o embedding nem busca em documentos inteiros. Ele primeiro divide cada documento em **chunks**, e só então gera o embedding e indexa esses chunks. Dois motivos práticos forçam isso:

- Um modelo de embedding tem uma janela de contexto limitada, então um documento longo pode simplesmente não caber.
- Mesmo quando cabe, gerar o embedding de uma passagem longa e de assuntos misturados como um único vetor a borra. O vetor acaba representando uma média de tudo o que a passagem toca, o que o torna uma correspondência pior para uma consulta sobre qualquer coisa específica dentro dela.

Portanto, o chunking existe para manter cada unidade com embedding focada o bastante para que seu vetor de fato represente o que uma consulta pode estar procurando.

### O trade-off central

O tamanho do chunk troca dois modos de falha entre si:

- **Chunks grandes demais:** o embedding borra vários assuntos juntos, prejudicando a precisão, e uma consulta sobre um detalhe dentro de um chunk longo pode não fazer com que ele apareça como uma correspondência próxima. A recuperação também devolve mais texto ao redor irrelevante junto com a parte relevante.
- **Chunks pequenos demais:** cada chunk pode perder o contexto ao redor que o torna interpretável, ou que responde a uma pergunta que se estende por mais de um pedaço pequeno. Uma única frase tirada de um parágrafo pode ser ambígua ou incompleta sozinha.

Não existe um tamanho de chunk universalmente certo. A escolha certa depende do corpus (as cláusulas de um contrato jurídico se leem de forma diferente de uma transcrição de chat) e do padrão de consultas que o sistema precisa atender (uma consulta que precisa de um fato se comporta de forma diferente de uma que precisa de uma explicação de vários passos).

### Estratégias comuns de chunking

- **Tamanho fixo.** Divide a cada N tokens ou caracteres, geralmente com alguma sobreposição entre chunks consecutivos. Simples e previsível, mas cega à estrutura real do documento: pode partir uma frase, ou uma tabela, ao meio.
- **Recursiva / ciente da estrutura.** Divide primeiro nas fronteiras naturais do documento (seções, depois parágrafos, depois frases), recorrendo a uma divisão de tamanho fixo apenas quando um pedaço delimitado por fronteiras ainda é grande demais. Isso respeita a organização do próprio autor em vez de impor uma arbitrária.
- **Chunking semântico.** Gera o embedding de frases consecutivas e divide onde a similaridade entre vizinhas cai bruscamente, partindo da ideia de que uma mudança de assunto é onde pertence a fronteira de um chunk. Mais cara de calcular, e ataca diretamente o modo de falha real (assuntos misturados dentro de um chunk), e não por aproximação.
- **Ciente da estrutura do documento.** Trata as unidades estruturais que o formato já fornece, como a seção de um título, uma tabela ou um bloco de código, como atômicas: nunca divide uma delas por uma fronteira de chunk, porque isso geralmente destrói seu significado.

![Três barras representando o mesmo documento. A barra de cima mostra sua estrutura natural: uma seção curta, uma seção longa e uma seção média, marcadas com linhas tracejadas nas verdadeiras fronteiras entre as seções. A barra do meio mostra o chunking de tamanho fixo, dividindo o mesmo documento em quatro pedaços de largura igual, independentemente de onde as seções realmente terminam, de modo que um corte cai no meio da seção longa, dividindo-a ao meio. A barra de baixo mostra o chunking ciente da estrutura, cujas fronteiras de chunk coincidem exatamente com as fronteiras naturais de seção da barra de cima, de modo que nenhuma seção é dividida entre dois chunks.](images/fixed-vs-structure-aware-chunking.svg)

### Sobreposição

Chunks consecutivos comumente se sobrepõem em um certo número de tokens. Sem sobreposição, um fato ou uma frase que atravessa exatamente o ponto onde dois chunks se dividem pode acabar fragmentado, irrecuperável por inteiro a partir de qualquer um dos chunks sozinho. A sobreposição custa algum armazenamento e cálculo de embedding redundantes em troca de não perder informação nas fronteiras entre chunks.

## Prática

1. ▢ Em uma frase, por que um pipeline de recuperação faz o chunking de um documento em vez de gerar o embedding dele inteiro?

<details markdown="1"><summary>Verificação</summary>

Porque uma passagem longa e de assuntos misturados gera um único vetor borrado que representa uma média de tudo o que ela toca, e isso recupera mal para uma consulta sobre qualquer coisa específica dentro dela (e ela pode nem caber na janela de contexto do modelo de embedding).

</details>

2. ▢ Um corpus de contratos jurídicos longos passa por chunking de tamanho fixo em pedaços de 512 tokens e sem sobreposição. Os usuários fazem perguntas sobre cláusulas específicas, e a recuperação continua perdendo cláusulas que foram divididas por uma fronteira de chunk. Nomeie duas mudanças na estratégia de chunking que ajudariam e o que cada uma corrige.

<details markdown="1"><summary>Dica</summary>

Uma mudança trata da própria divisão na fronteira; a outra trata do que acontece quando uma divisão é inevitável.

</details>

<details markdown="1"><summary>Verificação</summary>

Trocar para uma estratégia ciente da estrutura (ou ciente da estrutura do documento) que divide em fronteiras de cláusula ou de seção em vez de uma contagem bruta de tokens, de modo que uma cláusula não seja cortada no meio de um raciocínio logo de início. Separadamente, adicionar sobreposição entre os chunks, para que, mesmo onde uma divisão caia perto da fronteira de uma cláusula, o texto completo da cláusula ainda apareça intacto em pelo menos um chunk.

</details>

3. ▢ Uma equipe faz o chunking de um corpus em pedaços muito curtos, de uma única frase, para maximizar a precisão. Qual é a provável desvantagem, e quando ela apareceria?

<details markdown="1"><summary>Verificação</summary>

Os chunks individuais podem perder o contexto ao redor que os torna interpretáveis ou completos: uma frase tirada sozinha pode ser ambígua, e uma pergunta cuja resposta se estende por mais de uma frase não será respondível a partir de nenhum chunk recuperado isoladamente. Isso aparece como a recuperação tecnicamente encontrando "a frase certa" enquanto o sistema ainda não consegue produzir uma resposta correta ou completa a partir dela.

</details>

4. ▢ Por que chunks consecutivos comumente se sobrepõem?

    - a) Para tornar o índice vetorial maior e mais completo
    - b) Para que um fato ou uma frase que atravessa a fronteira de um chunk não seja fragmentado e irrecuperável a partir de qualquer um dos chunks
    - c) Porque os modelos de embedding exigem um tamanho mínimo de entrada
    - d) Para permitir que o reranker compare chunks adjacentes entre si

<details markdown="1"><summary>Verificação</summary>

**b)** Para que um fato ou uma frase que atravessa a fronteira de um chunk não seja fragmentado e irrecuperável a partir de qualquer um dos chunks. (a) descreve um custo da sobreposição, não seu propósito. (c) e (d) não são o motivo de a sobreposição existir.

</details>

## Prática no mundo real

- [ ] Escolha um documento real de um corpus sobre o qual você faria recuperação. Faça o chunking dele à mão de duas formas (tamanho fixo, e ciente da estrutura usando seus títulos ou seções reais) e compare onde cada estratégia divide no meio de um raciocínio.
- [ ] Para esse mesmo documento, escolha uma consulta que um usuário poderia realisticamente fazer e verifique qual saída de estratégia de chunking de fato conteria uma resposta completa e recuperável para ela.
- [ ] Amanhã: leia por inteiro o artigo sobre estratégias de chunking linkado abaixo e anote qual estratégia você adotaria como padrão para o seu próprio corpus e por quê.

## Para ir além

- [Artigo: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
