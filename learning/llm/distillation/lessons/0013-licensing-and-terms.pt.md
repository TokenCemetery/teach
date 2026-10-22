---
title: "13. Licenciamento e termos"
description: "O que os termos de um provedor e a licença de um modelo aberto permitem fazer com as suas saídas"
type: lesson
---

# Lição 13. Licenciamento e termos

**Ligação com a missão:** A missão pede que você verifique que o uso de um conjunto de destilação é permitido, o que significa ler os documentos que regem o professor antes de gerar dados a partir dele, e registrar o que você encontrou.
**Fonte principal:** [Termos: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
**Pré-requisitos:** [Lição 12](0012-filtering-synthetic-data.md), [Lição 10](0010-distilling-from-generated-data.md), [Dados sintéticos](../GLOSSARY.md), [Professor](../GLOSSARY.md)

Esta lição não é aconselhamento jurídico. Ela lê dois documentos, cita o que eles dizem e oferece uma checklist do que procurar. Ela não afirma nada sobre o que um documento significa para o seu caso, se uma cláusula é exequível ou qual documento rege você. Termos e licenças mudam sem uma versão que uma lição possa fixar, então as citações abaixo trazem a data em que foram lidas, e você deve ler o texto atual antes de depender de qualquer uma delas. Para uma decisão real, consulte um advogado.

## Aquecimento

1. ▢ Os autores do phi-1 podaram os seus exercícios contra o HumanEval com n-gramas, embeddings e correspondência de AST. Por que eles não pararam na sobreposição de n-gramas?

<details markdown="1"><summary>Verificação</summary>

Uma verificação de 13-gramas sinalizou apenas quatro perguntas, todas falsos positivos, e foi grosseira demais para encontrar código parecido, então eles acrescentaram a comparação por embedding e por AST (lição 12).

</details>

2. ▢ Os dados do Alpaca vieram do text-davinci-003 e o seu modelo passou por fine-tuning a partir do LLaMA 7B. De quais duas coisas que pertencem a outra pessoa, ou são controladas por ela, ele portanto depende?

<details markdown="1"><summary>Verificação</summary>

O professor que gerou os dados (o text-davinci-003 da OpenAI, sob os termos da OpenAI) e o base model (o LLaMA, sob a sua licença). Ambos são insumos do aluno, e cada um vem com as suas próprias condições (lição 10).

</details>

3. ▢ Cite o filtro que verifica por regra uma resposta gerada contra a verdade de referência, e uma coisa que ele não consegue julgar.

<details markdown="1"><summary>Verificação</summary>

Rejection sampling com um verificador, em que apenas as amostras que passam são mantidas. Ele não consegue julgar respostas abertas nem estilo, onde não há nada contra o que verificar (lição 12).

</details>

## Saiba isto

### Três documentos, três perguntas

Quando você gera dados a partir de um professor, você pode estar vinculado a até três tipos diferentes de documento, e cada um responde a uma pergunta diferente.

| Documento | Pergunta a que responde |
|---|---|
| Os termos de uso do provedor, para um modelo hospedado | O que posso fazer com as saídas que obtenho deste serviço? |
| A licença de pesos abertos | O que posso fazer com o modelo, e com o que ele produz? |
| A licença ou os termos dos prompts e dos dados-semente | O que posso fazer com as entradas que forneci a ele, e com os dados que construí a partir delas? |

Cada um é um texto separado, com a sua própria data e escopo. Ler um não diz o que outro diz.

### O que dizem os termos de um provedor hospedado

Os Terms of Use da OpenAI para o resto do mundo, em vigor desde 1º de janeiro de 2026, listam coisas que um usuário não pode fazer. Entre elas está esta linha, como lida quando esta trilha foi escrita, em outubro de 2026. O site bloqueia leituras por script, então reconfira a página em um navegador:

> "Use Output to develop models that compete with OpenAI."

Três coisas a notar, e nada mais. A frase está na seção de usos proibidos. Ela fala de desenvolver modelos que concorram com a OpenAI, o que é algo mais estreito do que desenvolver qualquer modelo. E é um documento só: o seu uso pode cair sob outra edição, ou sob um acordo separado para uma API ou serviço empresarial, e esta lição não leu esses.

### O que diz uma licença de pesos abertos

O Llama 3.1 Community License Agreement da Meta diz, na seção 1.b.i (Redistribution and Use), conforme lido no texto do repositório em 17 de outubro de 2026:

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

O mesmo parágrafo também exige que, se você distribuir os Llama Materials, ou um produto ou serviço que os contenha, incluindo outro modelo de IA, você forneça uma cópia do acordo e exiba de forma proeminente "Built with Llama" em um site relacionado, interface de usuário, postagem de blog, página sobre ou documentação do produto. Separadamente, a licença diz que o uso dos Llama Materials deve cumprir as leis aplicáveis e uma Acceptable Use Policy que ela incorpora por referência.

O texto vincula uma condição sobre o nome do modelo ao uso das saídas dessa maneira quando o modelo resultante é distribuído ou disponibilizado. Esta lição não afirma nada além das palavras. Outras versões do Llama e outros modelos abertos têm as suas próprias licenças, e algumas dizem coisas diferentes.

### Como um projeto lidou com isso

Os autores do Alpaca afirmam que o seu modelo se destina apenas à pesquisa acadêmica e que qualquer uso comercial é proibido, e dão três fatores: o LLaMA tem uma licença não comercial, então eles a herdam; os dados de instrução vêm do text-davinci-003, cujos termos de uso, dizem eles, proíbem desenvolver modelos que concorram com a OpenAI; e eles não haviam construído medidas de segurança adequadas. Eles também escrevem que a sua demo foi restrita a usos não comerciais e a usos que seguem a licença do LLaMA (post do blog do Alpaca, "Overview" e "Release decision"). Note o que eles fizeram: nomearam cada fonte de restrição e amarraram o lançamento a ela. Esse é o hábito a copiar, digam o que disserem os seus próprios documentos.

### Antes de gerar: uma checklist

Leia e registre, nesta ordem:

1. **Os termos do professor.** Encontre o documento exato que se aplica à maneira como você acessa o modelo. Anote o seu nome, URL, data ou versão e as frases sobre usar saídas para treinar outros modelos.
2. **A licença dos pesos, se o professor for aberto.** Anote a versão, qualquer cláusula sobre treinar em saídas, qualquer exigência de nome ou atribuição e qualquer política de uso que ela incorpore.
3. **Os prompts e os dados-semente.** A licença de tudo que você fornece ao professor, como tarefas-semente, documentos ou texto raspado, rege as entradas. Verifique-a separadamente do professor.
4. **Nome e atribuição.** Se um documento exige um prefixo no nome do modelo ou uma linha de crédito, decida agora, antes de o modelo ter um nome.
5. **Como o aluno será usado e compartilhado.** Muitas cláusulas dependem de o modelo ser distribuído, disponibilizado ou vendido, e do que ele concorre. Escreva o uso que você pretende.
6. **A data.** Registre quando você leu cada documento e quando gerou cada lote, porque os termos em vigor na hora da geração podem diferir dos termos de hoje.

Mantenha esse registro ao lado do dataset, uma linha por fonte, para que a pergunta "de onde isto veio?" tenha uma resposta um ano depois. Um campo de proveniência em cada exemplo, nomeando o professor, a versão e a data de geração, custa quase nada.

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

As entradas `<...>` são campos a preencher para o seu próprio projeto.

### O que esta lição não pode dizer

Ela não pode dizer se um dado projeto viola uma cláusula. Isso depende do texto completo, dos fatos, da jurisdição e do que o provedor e o detentor da licença farão, nada disso estando em uma citação. O objetivo do exercício é mais estreito: garantir que você leu os documentos, sabe o que eles literalmente dizem e tem um registro datado disso.

## Prática

1. ▢ Uma equipe faz fine-tuning de um modelo em saídas do Llama 3.1 e vai disponibilizá-lo. De acordo com o texto da licença citado, o que precisa ser verdade sobre o nome do novo modelo?

    - a) Ele precisa terminar com a palavra "Llama"
    - b) Ele não pode conter nenhuma menção ao Llama
    - c) Ele precisa começar com a palavra "Llama"
    - d) Ele precisa ser registrado junto ao licenciante

<details markdown="1"><summary>Verificação</summary>

**c)** A frase citada diz "Llama" no começo do nome do modelo de IA, para um modelo que é distribuído ou disponibilizado. (a) inverte a posição. (b) é o oposto do que ela diz. (d) não está no texto citado.

</details>

2. ▢ A linha citada da OpenAI trata de usar a saída "to develop models that compete with OpenAI". Um colega a resume como "a OpenAI proíbe treinar nas suas saídas". O que há de errado com o resumo?

<details markdown="1"><summary>Verificação</summary>

A linha é mais estreita do que o resumo: ela trata de desenvolver modelos que concorram com a OpenAI, não de todo desenvolvimento de modelos. Ela também é um documento, de uma edição dos termos, em uma data. Cite a frase e a sua data em vez de uma paráfrase e verifique o que se aplica à sua via de acesso. Se o seu projeto concorre é uma questão jurídica que esta lição não responde.

</details>

3. ▢ Você gerou 200.000 exemplos a partir de um modelo hospedado em março. Em outubro, o provedor muda os seus termos. O que você faz primeiro?

<details markdown="1"><summary>Verificação</summary>

Leia os novos termos e os termos em vigor quando você gerou os dados, ambos na página do próprio provedor, e veja o que o seu registro diz sobre qual versão você leu. O registro é o motivo de você ter anotado a data. O que vem depois é uma questão jurídica sobre quais termos se aplicam a dados já gerados, então leve-a a alguém qualificado, e não a um palpite.

</details>

4. ▢ Os autores do Alpaca dão três fatores para um lançamento apenas para pesquisa. Qual depende da escolha do professor, e qual da escolha da base do aluno?

<details markdown="1"><summary>Verificação</summary>

O fator do professor é que os dados vêm do text-davinci-003, cujos termos proíbem desenvolver modelos que concorram com a OpenAI. O fator da base é que o LLaMA tem uma licença não comercial, então o Alpaca a herda. O terceiro, a falta de medidas de segurança, não é sobre nenhum dos dois.

</details>

5. ▢ Os seus prompts-semente vêm de um dataset público e o seu professor é um modelo aberto com uma licença permissiva. Cite dois documentos que você ainda precisa ler antes de entregar o aluno.

<details markdown="1"><summary>Verificação</summary>

A licença do dataset-semente, já que ela rege as entradas, e a própria licença do modelo aberto, para qualquer cláusula sobre treinar nas suas saídas, nome, atribuição ou política de uso. Verifique também a licença de qualquer base model de que o aluno parte. Uma licença permissiva em uma fonte não se estende às outras.

</details>

## Prática no mundo real

- [ ] Abra os Terms of Use da OpenAI e a licença do Llama 3.1 e encontre as frases exatas citadas acima. Copie a data de vigência de cada uma para uma nota.
- [ ] Escolha um dataset sintético público em um hub que você usa. Encontre de qual professor ele diz ter sido gerado e anote os termos ou a licença desse professor como declarados na página do dataset.
- [ ] Amanhã: preencha o registro da checklist acima para um dataset hipotético de um professor à sua escolha e marque cada campo que você não conseguiu preencher a partir de um documento primário.

## Para ir além

- [Sequência e Dados Sintéticos](../reference/sequence-and-synthetic-data.md)
- [Termos: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
- [Licença: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [Artigo: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
