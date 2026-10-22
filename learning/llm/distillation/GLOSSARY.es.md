---
title: "Glosario"
description: "Términos canónicos de la destilación de conocimiento de LLM"
type: glossary
---

# Glosario de la destilación

Términos canónicos para entrenar un modelo más pequeño a partir de las salidas de uno mayor, las pérdidas y los datos que llevan la señal, y cómo se juzga el resultado. En este espacio de trabajo "destilación" siempre significa destilación de conocimiento de un modelo profesor a un modelo estudiante; nunca significa destilación de datasets ni destilar un prompt.

## Términos

**Beam search**:
Un método de decodificación que conserva las pocas secuencias parciales de mayor puntuación en cada paso y devuelve la mejor completa, como aproximación a la secuencia más probable.
_Evitar_: búsqueda voraz (eso es un beam de tamaño 1), decodificación best-first

**Brecha de capacidad**:
La caída de calidad del estudiante que puede aparecer cuando el profesor es mucho mayor que el estudiante, de modo que un profesor más fuerte produce un estudiante peor que el que produciría uno más débil.
_Evitar_: profesor demasiado listo, desajuste de tamaño

**Pérdida combinada**:
Una pérdida de destilación que suma la entropía cruzada frente a los hard labels a la divergencia respecto de los soft targets del profesor, ponderadas por un coeficiente de mezcla.
_Evitar_: pérdida híbrida, pérdida dual

**Destilación entre tokenizers**:
Destilación de logits entre un profesor y un estudiante cuyos vocabularios difieren, que se hace alineando o comparando sus distribuciones sin un índice de tokens compartido.
_Evitar_: destilación sin tokenizer, transferencia de vocabulario

**Descontaminación**:
Eliminar de los datos de entrenamiento los ejemplos que coinciden con un conjunto de evaluación o se le parecen mucho, para que la puntuación de un benchmark no mida elementos memorizados.
_Evitar_: limpieza (demasiado amplio), deduplicación (que elimina repeticiones dentro del conjunto de entrenamiento)

**Destilación**:
Entrenar a un modelo estudiante para que reproduzca el comportamiento de un modelo profesor, usando como señal de entrenamiento las distribuciones de salida del profesor o el texto que genera.
_Evitar_: compresión (demasiado amplio), copia de modelos

**Ley de escalado de la destilación**:
Una relación ajustada, de Busbridge et al., que predice la entropía cruzada de un estudiante a partir de su tamaño, del número de tokens de destilación y de la entropía cruzada del profesor.
_Evitar_: ley de destilación, escalado de KD

**Exposure bias**:
El desajuste entre entrenar con prefijos que escribió otro y generar a partir de prefijos que escribió el propio modelo, de modo que sus primeros errores lo ponen en estados con los que nunca se entrenó.
_Evitar_: desajuste entre entrenamiento y prueba (demasiado amplio), deriva

**Fidelidad (fidelity)**:
Cuánto coinciden las predicciones de un estudiante con las de su profesor, medido sobre las mismas entradas, en contraste con lo bien que lo hace cualquiera de los dos en la tarea.
_Evitar_: precisión, fidelidad en el sentido de groundedness

**KL directa (forward KL)**:
La divergencia KL(profesor ‖ estudiante), promediada bajo la distribución del profesor, que penaliza al estudiante por poner poca probabilidad donde el profesor pone mucha y por eso lo empuja a cubrir todos los modos.
_Evitar_: KL que cubre modos sin nombrar la dirección, KL a secas

**Generalized knowledge distillation**:
El método on-policy de Agarwal et al. que entrena al estudiante con una mezcla de secuencias fijas y secuencias generadas por el estudiante, puntuadas token a token frente al profesor con una divergencia elegida. Se abrevia GKD.
_Evitar_: KD generalizada, destilación genérica

**Hard label**:
La única clase o token correcto que se usa como objetivo de entrenamiento, con toda su probabilidad en una sola respuesta.
_Evitar_: ground truth (puede ser el argmax del profesor), objetivo one-hot sin contexto

**Brecha de imitación**:
La distancia entre cuánto suena un estudiante como su profesor y cuánta de la capacidad del profesor tiene en realidad, que la imitación con un presupuesto limitado cierra mucho más rápido en estilo que en capacidad.
_Evitar_: falsa promesa (el título del paper, no un término), transferencia de estilo

**Divergencia KL**:
Para dos distribuciones P y Q sobre los mismos tokens, la suma sobre los tokens de P log(P / Q): una medida de cuán lejos está Q de P que no es simétrica. Sus dos direcciones en la destilación son la KL directa y la KL inversa.
_Evitar_: distancia KL, entropía relativa sin presentar antes el término

**Logit**:
La puntuación cruda y sin normalizar que un modelo asigna a una clase o token antes de que el softmax convierta las puntuaciones en probabilidades.
_Evitar_: puntuación (ambiguo), log-probabilidad (eso es después del softmax)

**Destilación de logits**:
Destilación cuya señal de entrenamiento es la distribución de salida completa del profesor en cada posición, lo que exige acceso a los logits del profesor y un vocabulario compartido.
_Evitar_: destilación white-box (alias aceptado, pero usa un solo término), destilación suave

**Destilación off-policy**:
Destilación sobre secuencias que el estudiante no generó: datos humanos o las propias salidas del profesor, fijados antes del entrenamiento.
_Evitar_: destilación offline, destilación supervisada

**Destilación on-policy**:
Destilación sobre secuencias que el estudiante genera durante el entrenamiento, con el profesor puntuando cada token que el estudiante eligió, de modo que el estudiante entrena con sus propios errores.
_Evitar_: destilación online (también se usa para profesores entrenados junto al estudiante), autodestilación

**Rationale**:
El razonamiento intermedio que un profesor escribe antes de su respuesta o junto a ella, usado como objetivo de entrenamiento adicional para que el estudiante aprenda cómo se llegó a la respuesta.
_Evitar_: explicación (bien en la prosa, no como término), chain of thought (la técnica de prompting que lo produce)

**Rejection sampling**:
Extraer varias salidas candidatas de un modelo para cada prompt y conservar solo las que superan una comprobación, como una respuesta final correcta.
_Evitar_: filtrado (demasiado amplio), best-of-n (que conserva un solo ganador en lugar de descartar según una comprobación)

**KL inversa (reverse KL)**:
La divergencia KL(estudiante ‖ profesor), promediada bajo la distribución del estudiante, que penaliza al estudiante por poner probabilidad donde el profesor pone poca y por eso lo empuja a comprometerse con un solo modo.
_Evitar_: KL que busca modos sin nombrar la dirección, KL hacia atrás

**Destilación a nivel de secuencia**:
Destilación en la que el estudiante se entrena con entropía cruzada ordinaria sobre secuencias completas que decodificó el profesor, en lugar de sobre las distribuciones por token del profesor.
_Evitar_: destilación dura, destilación black-box (que también abarca la destilación con datos generados)

**Soft targets**:
La distribución de probabilidad completa del profesor sobre clases o tokens, usada como objetivo de entrenamiento en lugar del hard label o junto a él.
_Evitar_: soft labels (alias aceptado, pero usa un solo término), dark knowledge (la información que llevan, no los objetivos)

**Estudiante**:
El modelo que se entrena en una destilación, normalmente más pequeño o más barato de ejecutar que el profesor.
_Evitar_: modelo destilado antes de terminar el entrenamiento, modelo hijo

**Aprendizaje subliminal**:
Un estudiante que adquiere un rasgo de su profesor a partir de datos semánticamente ajenos a ese rasgo, observado por Cloud et al. cuando ambos comparten el mismo base model.
_Evitar_: destilación oculta, envenenamiento de datos (eso es deliberado)

**Baseline supervisado**:
Un modelo del tamaño del estudiante entrenado sin destilación, con los mismos datos o el mismo cómputo, que se usa como comparación para mostrar si la destilación causó un resultado.
_Evitar_: modelo de control (demasiado amplio), modelo simple

**Datos sintéticos**:
Ejemplos de entrenamiento generados por un modelo en lugar de escritos por personas. En este espacio de trabajo significa datos generados por el profesor para el estudiante.
_Evitar_: datos falsos, datos aumentados (la aumentación transforma ejemplos existentes)

**Profesor**:
El modelo cuyas salidas son la señal de entrenamiento en una destilación. Está fijo durante el entrenamiento y normalmente es mayor o más capaz que el estudiante.
_Evitar_: oráculo, modelo padre

**Asistente del profesor (teacher assistant)**:
Un modelo de tamaño intermedio destilado a partir del profesor y usado luego como profesor de un estudiante más pequeño, para salvar una brecha de capacidad.
_Evitar_: profesor intermedio sin presentar antes el término, modelo TA

**Teacher forcing**:
Darle a un modelo un prefijo fijo en lugar de sus propias salidas anteriores, de modo que un solo forward pass produce una distribución del siguiente token en cada posición de una secuencia.
_Evitar_: decodificación con teacher forcing, ejecución libre (eso es lo opuesto)

**Temperatura**:
El divisor T que se aplica a los logits antes del softmax. Una T mayor que 1 aplana la distribución y sube las probabilidades de las respuestas improbables para que el estudiante pueda aprender de ellas. Ese era el valor por defecto de la era de los clasificadores; las ejecuciones de destilación de LLM de las fuentes de este espacio de trabajo encontraron que T igual a 1 era lo mejor.
_Evitar_: temperatura de muestreo (misma operación, distinto propósito), suavidad

**Destilación a nivel de token**:
Destilación de logits aplicada en cada posición de una secuencia, minimizando una divergencia entre las distribuciones del siguiente token del profesor y del estudiante.
_Evitar_: destilación a nivel de palabra (el nombre del paper original), KD por token

**Acuerdo top-1**:
La proporción de entradas en las que la respuesta de mayor probabilidad de un estudiante coincide con la de su profesor, una de las dos métricas de fidelidad de Stanton et al.
_Evitar_: precisión (eso es frente a la respuesta correcta), tasa de coincidencia

**Logits top-k**:
Las k entradas mayores de la distribución de salida de un profesor en una posición, conservadas con sus índices de token en lugar de la fila completa del vocabulario, para reducir el almacenamiento.
_Evitar_: logits dispersos, softmax truncado sin decir qué pasa con la masa descartada
