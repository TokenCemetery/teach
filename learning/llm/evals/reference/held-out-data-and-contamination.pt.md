---
title: "Dados Held-Out e Contaminação"
description: "Disciplina de divisão treino/teste para um conjunto de eval, os dois caminhos da contaminação, como detectar cada um e como projetar um conjunto customizado que resista a eles"
type: reference
---

# Dados Held-Out e Contaminação

A etapa 1 condensada para consulta. A [lição 1](../lessons/0001-held-out-and-contamination.md) trata dos dois caminhos da contaminação e do teste de instrução guiada para detectá-los; a [lição 2](../lessons/0002-designing-contamination-resistance.md) trata de projetar um conjunto de eval customizado que resista à contaminação desde o início. Esta folha reúne, lado a lado, as definições, os caminhos e o kit de prevenção.

## O que "held-out" exige

Um conjunto de eval é held-out quando o modelo sendo avaliado nunca viu esses exemplos exatos, nem paráfrases próximas deles, durante o treinamento ou o fine-tuning. Essa única propriedade é o que permite que uma boa pontuação signifique "isto generaliza" em vez de "isto foi memorizado". Antes de citar uma pontuação como evidência, responda: *por que o modelo não poderia ter acertado isto por memorização, ou por ter sido ajustado contra este exato conjunto?* Se não há resposta, o número descreve o eval, não o modelo.

## Dois caminhos de contaminação

| Caminho | O que acontece | Vazamento literal? | Correção |
|---|---|---|---|
| Absorção no pré-treinamento | Um benchmark é raspado para dentro de dados de treinamento de web-crawl antes que alguém construa um eval sobre ele | Sim | Escolher ou construir dados que dificilmente apareçam em um corpus de pré-treinamento, ou testar a presença deles |
| Overfitting iterativo | O mesmo conjunto de eval é executado repetidamente enquanto se ajusta um modelo ou prompt, moldando aos poucos o sistema para passar nesses exemplos específicos | Não | Renovar o conjunto, ou reservar uma fatia dele que nunca foi tocada |

Os dois produzem o mesmo sintoma: um número que parece bom e não prevê o comportamento no mundo real. As correções diferem porque as causas diferem; tratar uma como substituta da outra deixa o caminho não tratado aberto.

## Detectando a absorção no pré-treinamento: o teste de instrução guiada

Dê ao modelo a primeira parte de uma instância de benchmark e peça que ele complete o resto literalmente. Reproduzir detalhes que um palpite plausível não recuperaria, formulação exata, um número incomum, um nome próprio raro, é forte evidência de que aquela instância estava em seus dados de treinamento (Golchin e Surdeanu, 2023). Isso só testa a absorção; não diz nada sobre o overfitting iterativo, que não deixa esse tipo de rastro.

## Prevenindo a contaminação ao construir um conjunto customizado

| Técnica | O que faz | Quando se aplica | Limites |
|---|---|---|---|
| Ser posterior ao corte de treinamento | Obter os dados de eval de material criado depois do corte de treinamento declarado do modelo | Exige uma data de corte exata e verificada, e não uma afirmação de marketing | Protege apenas contra a absorção; um conjunto de eval desatualizado ainda corre o risco de overfitting iterativo |
| Canary string (convenção do BIG-bench) | Embutir uma frase marcadora única pedindo a qualquer crawler que exclua o conteúdo marcado | Qualquer conjunto publicado | Um pedido, não um mecanismo de imposição; depende da cooperação dos crawlers |
| Verificação de sobreposição de n-gramas | Medir a sobreposição direta entre os dados de eval e um corpus conhecido | Apenas quando o corpus de pré-treinamento é conhecido e acessível | Inutilizável para um modelo fechado com dados de treinamento não divulgados |
| Manter o conjunto não publicado | Nunca postá-lo publicamente | Sempre disponível | A prevenção mais forte, ao custo da reprodutibilidade e do escrutínio externo |

As três primeiras dependem de alguma coisa (um corte exato, a cooperação dos crawlers, acesso ao corpus); manter um conjunto privado é a única técnica sem pré-condição, e é por isso que ela é o recurso final quando as outras não se aplicam.

## Antes de confiar em uma pontuação

- A história de contaminação do conjunto de eval está declarada, e não presumida: qual caminho foi verificado, e como.
- Um benchmark público emprestado foi testado com o método de instrução guiada, ou existe uma razão documentada de por que esse risco é baixo.
- Um conjunto de eval customizado nomeia qual(is) técnica(s) de prevenção se aplicam a ele, e seus limites são conhecidos, e não apenas sua presença.
- Um conjunto de eval reutilizado por meses de ajuste foi renovado, ou existe uma fatia reservada que nunca foi tocada.

## Fontes

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Artigo científico: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin e Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Artigo científico: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [Recursos](../RESOURCES.md)
