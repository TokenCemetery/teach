---
title: "Glossário"
description: "Termos canônicos de fine-tuning com adapters"
type: glossary
---

# Glossário de Fine-Tuning com Adapters

Termos canônicos deste workspace. Um termo entra aqui quando já pode ser usado corretamente, e não quando é mencionado pela primeira vez, então este glossário cresce conforme as lições são conquistadas.

## Uso neste workspace

Três palavras são usadas de forma imprecisa em toda a área, de maneiras que deixariam as lições seguintes ambíguas, então ficam fixadas desde o início:

**Fine-tuning**:
Treinar em uma tarefa um pequeno conjunto de parâmetros adicionados ou selecionados, enquanto os pesos do base model ficam congelados. Quando todos os pesos são treinados, este workspace sempre diz _full fine-tuning_ de forma explícita.
_Evite_: treinamento, retreinamento, ensinar o modelo

**Adapter**:
O pequeno conjunto de pesos treináveis adicionado ao lado de um base model congelado, junto com a configuração que descreve onde ele se acopla.
_Evite_: fine-tune (como substantivo), LoRA (quando o método não é especificamente o LoRA), checkpoint

**Quantização**:
Armazenar os pesos com precisão numérica menor do que aquela em que foram treinados. Neste workspace ela sempre se refere ao _base model congelado_, salvo indicação em contrário: os adapters permanecem em precisão maior, e a quantização para inferência é um assunto separado.
_Evite_: compressão, encolhimento, otimização

## Termos

_Adicionados conforme as lições os estabelecem._
