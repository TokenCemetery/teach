---
title: Glosario
description: "Términos canónicos de prompting"
type: glossary
---

# Glosario de prompting

Términos canónicos para escribir, estructurar, versionar, medir y proteger los prompts que hay detrás de una funcionalidad con LLM.

## Términos

**Chain-of-thought**:
Razonamiento intermedio que el modelo escribe antes de su respuesta final, provocado por ejemplos que lo muestran o por una instrucción que lo pide.
_Evitar_: CoT en prosa (válido en un encabezado o una tabla), thinking (reservado aquí para la fase de razonamiento integrada de un modelo de razonamiento)

**Plantilla de chat**:
La regla específica de cada modelo que convierte una lista de mensajes con rol en la única secuencia de tokens con la que se entrenó el modelo, incluidos los tokens especiales que marcan dónde empieza y termina cada rol.
_Evitar_: formato de prompt

**Decodificación restringida**:
Limitar qué tokens puede generar el modelo en cada paso para que la salida deba ajustarse a una gramática o un esquema, como hace la función de salida estructurada que un proveedor aplica de forma forzada.
_Evitar_: muestreo por gramática

**Delimitador**:
Marcado dentro de un prompt, como una etiqueta de estilo XML o un bloque delimitado, que indica dónde termina un tipo de contenido y empieza otro, casi siempre para mantener los datos separados de las instrucciones.
_Evitar_: separador

**Prompt few-shot**:
Un prompt que incluye, antes de la entrada real, ejemplos resueltos de la tarea, cada uno con una entrada emparejada con la salida deseada.
_Evitar_: prompt multishot, entrenamiento en contexto

**Inyección de prompt indirecta**:
Inyección de prompt transportada por contenido que el modelo lee en nombre del usuario, como una página web, un correo o un documento recuperado, en lugar de escrita por la persona que habla con él.
_Evitar_: inyección de segundo orden

**Jerarquía de instrucciones**:
El orden que un modelo está entrenado para aplicar cuando las instrucciones entran en conflicto: el system prompt por encima del turno del usuario, y el turno del usuario por encima del contenido devuelto por herramientas o por recuperación.
_Evitar_: orden de prioridad

**Jailbreak**:
Entrada diseñada para que un modelo produzca lo que su entrenamiento de seguridad rechaza. Apunta a los límites del propio modelo, mientras que la inyección de prompt apunta a las instrucciones de la aplicación.
_Evitar_: inyección de prompt (otro objetivo)

**Tríada letal**:
La combinación de acceso a datos privados, exposición a contenido no confiable y una vía para enviar datos al exterior, que juntos hacen explotable la inyección de prompt. Eliminar cualquiera de los tres cierra el camino.
_Evitar_: riesgo de inyección (demasiado vago para actuar sobre él)

**Snapshot del modelo**:
Una versión fija de un modelo, identificada por un ID de modelo exacto, cuyos pesos el proveedor no modifica. Un alias de conveniencia puede apuntar con el tiempo a un snapshot más reciente.
_Evitar_: versión del modelo (ambiguo con una generación del modelo)

**Comparación pareada**:
Comparar dos prompts o modelos sobre las mismas entradas a partir de los casos en que sus resultados difieren, en lugar de comparar sus dos totales.
_Evitar_: comparación de puntuaciones A/B

**Prompt**:
Todo lo que el modelo recibe en una llamada: el system prompt, cada mensaje de la conversación hasta ese momento y cualquier contenido insertado, convertidos por la plantilla de chat en una única secuencia de tokens.
_Evitar_: consulta (esa es la pregunta del usuario dentro del prompt)

**Prompt caching**:
Una función del proveedor que almacena el estado ya procesado de un prefijo de prompt, de modo que las llamadas posteriores que comparten exactamente ese prefijo se saltan su recálculo, con menor costo y latencia.
_Evitar_: caché de respuestas (otra cosa: almacenar respuestas completas)

**Inyección de prompt**:
Entrada que hace que el modelo siga instrucciones distintas de las que pretendía el autor del prompt.
_Evitar_: jailbreak (un jailbreak apunta al entrenamiento de seguridad del modelo; la inyección apunta a las instrucciones de la aplicación)

**Plantilla de prompt**:
El texto fijo de un prompt con huecos con nombre que se rellenan en el momento de la llamada con valores de cada petición, como el mensaje del usuario o un documento recuperado.
_Evitar_: cadena de prompt

**Modelo de razonamiento**:
Un modelo entrenado para producir una fase de razonamiento interna antes de su respuesta visible, de modo que razona sin que se le pida.
_Evitar_: modelo de pensamiento

**Conjunto de regresión**:
Un conjunto fijo de entradas, cada una con una comprobación sobre la salida, que un cambio de prompt no debe romper, construido sobre todo a partir de fallos vistos en uso real.
_Evitar_: prompts de prueba, golden set

**Rol**:
La etiqueta de cada mensaje de una conversación, normalmente system, user o assistant, que la plantilla de chat convierte en tokens especiales. Un rol es formato al que el modelo aprendió a dar peso, no un canal de entrada separado.
_Evitar_: persona (es una descripción de quién debe actuar como el modelo)

**Autoconsistencia**:
Muestrear varias completaciones de chain-of-thought para el mismo prompt y quedarse con la respuesta final más común.
_Evitar_: ensamblado

**Salida estructurada**:
Una respuesta en un formato legible por máquina, normalmente JSON que cumple un esquema, que un programa analiza en lugar de que la lea una persona.
_Evitar_: modo JSON (una función concreta de un proveedor)

**System prompt**:
El mensaje, con rol system, que fija la tarea, las restricciones y el contexto del modelo para toda la conversación, y que ocupa el lugar más alto de la jerarquía de instrucciones.
_Evitar_: mensaje de sistema, preámbulo

**Prompt zero-shot**:
Un prompt que plantea la tarea sin ningún ejemplo resuelto.
_Evitar_: prompt simple
