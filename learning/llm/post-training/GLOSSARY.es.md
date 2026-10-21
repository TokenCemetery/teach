---
title: "Glosario"
description: "Términos canónicos del post-training de LLM"
type: glossary
---

# Glosario del post-training de LLM

Términos canónicos para alinear un modelo preentrenado: qué maximiza cada objetivo de entrenamiento y qué cambia cuando el objetivo pasa de imitar texto a optimizar una recompensa.

## Términos

**Impuesto de alineación (alignment tax)**:
La pérdida de capacidad (normalmente medida en benchmarks de estilo preentrenamiento) que el post-training puede introducir como efecto secundario de optimizar la utilidad o la seguridad.
_Evitar_: regresión (una regresión es cualquier caída de capacidad; el impuesto de alineación nombra la que se paga específicamente a cambio de alineación)

**Pérdida de Bradley-Terry**:
La función de pérdida que se usa para entrenar un reward model con datos de preferencia por pares, y que trata la probabilidad de que una completion se prefiera a otra como una función de la diferencia entre sus puntuaciones escalares de recompensa.
_Evitar_: pérdida de preferencia (se usa con laxitud para varios objetivos de este campo, incluido el de DPO; Bradley-Terry nombra el modelo concreto de comparación por pares que usa el modelado de recompensa)

**Ventaja relativa al grupo**:
El sustituto que usa GRPO de una función de valor aprendida: para un grupo de completions muestreadas para el mismo prompt, la ventaja de una completion es su recompensa menos la recompensa media del grupo, dividida por la desviación estándar del grupo, y se aplica a cada token de esa completion.
_Evitar_: baseline (un baseline es el concepto general de RL que la media del grupo cumple; este espacio de trabajo usa el nombre específico una vez que GRPO está en juego)

**Recompensa implícita**:
La función de recompensa que DPO demuestra que está implícita matemáticamente en una policy y un modelo de referencia, sin entrenar nunca un reward model aparte para calcularla.
_Evitar_: reward model (todo el argumento de DPO es que no necesita uno aparte; confundir ambos borra la distinción que la etapa 5 existe para enseñar)

**Penalización KL**:
Un término que se añade a un objetivo de RL y que penaliza a la policy entrenada por alejarse de la distribución de salida de un modelo de referencia fijo, de modo que optimizar contra un reward model no produzca texto degenerado.
_Evitar_: regularización (correcto pero genérico; nombra la penalización concreta cuando RLHF esté en juego)

**Enmascarado de la pérdida**:
Poner a cero la pérdida de entrenamiento sobre los tokens que el modelo no debe aprender a producir, como un prompt o un mensaje de sistema, de modo que las actualizaciones de gradiente provengan solo de los tokens que el modelo debe generar.
_Evitar_: enmascarado del prompt (el enmascarado se aplica a más que el prompt, incluido cualquier turno que no sea del asistente en un ejemplo de varios turnos)

**Par de preferencia**:
Dos completions al mismo prompt, una marcada como preferida sobre la otra, la unidad de datos con la que entrenan tanto el modelado de recompensa como DPO.
_Evitar_: comparación (se usa en toda la literatura para lo mismo; este espacio de trabajo estandariza en par de preferencia)

**Reward hacking**:
Una policy que encuentra la manera de puntuar bien contra un reward model o una señal de recompensa verificable sin producir en realidad el comportamiento que la recompensa pretendía medir.
_Evitar_: gaming, sobreoptimización (ambos apuntan al mismo fallo; este espacio de trabajo usa reward hacking como el único término en todas partes)

**RLAIF**:
Aprendizaje por refuerzo a partir de feedback de IA (reinforcement learning from AI feedback): etiquetas de preferencia o una señal de recompensa producidas por un modelo en lugar de por una persona, usadas en lugar de RLHF o junto con él.
_Evitar_: automejora (RLAIF es un método de etiquetado concreto; la automejora es una afirmación más amplia y vaga sobre cuál es el resultado)

**Recompensa verificable**:
Una señal de recompensa calculada por un verificador determinista, como el resultado de un test unitario o una respuesta numérica final que coincide, en lugar de por un reward model aprendido.
_Evitar_: ground truth (el ground truth es la respuesta contra la que se comprueba; la recompensa verificable es la señal que se deriva de esa comprobación)
