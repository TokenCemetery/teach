---
title: "Glosario"
description: "Términos canónicos de evals"
type: glossary
---

# Glosario de evals

Términos canónicos para demostrar si un cambio en un modelo ayudó y para defender que un número lo refleja.

## Términos

**Guía de anotación**:
Una definición escrita de cada categoría de calificación, con ejemplos concretos en los casos límite y cómo se resolvieron, que se entrega a cada evaluador humano antes de empezar. Un acuerdo bajo entre evaluadores suele indicar una guía ausente o ambigua, más que evaluadores poco fiables.
_Evitar_: rúbrica de calificación (se usa como sinónimo en otros lugares; este espacio de trabajo usa "guía de anotación" como término)

**Corrección de las citas**:
Si el pasaje concreto citado para una afirmación realmente respalda esa afirmación, una comprobación más estricta que la fidelidad y hecha cita por cita. Una afirmación puede ser fiel (fundamentada en algún lugar del conjunto recuperado) y aun así estar atribuida a la cita equivocada, o a ninguna.
_Evitar_: fidelidad (una comprobación relacionada pero distinta; la fidelidad pregunta si una afirmación está respaldada por el contexto recuperado en absoluto, la corrección de las citas pregunta si su fuente citada concreta realmente la respalda)

**Kappa de Cohen**:
Un estadístico que mide el acuerdo entre dos evaluadores tras corregir el acuerdo que se esperaría solo por azar: `κ = (p_o − p_e) / (1 − p_e)`. Un kappa de 0 significa que no es mejor que el azar; un kappa puede ser negativo. Se sabe que subestima el acuerdo cuando una categoría de calificación es mucho más rara que las demás.
_Evitar_: porcentaje de acuerdo (la cifra cruda, sin corregir; el kappa es específicamente la versión corregida por azar, y ambas pueden contar historias distintas)

**Contaminación de datos**:
Que los datos de una eval, o una paráfrasis cercana de ellos, acaben dentro de los datos de entrenamiento de un modelo (normalmente en el preentrenamiento, a través de un benchmark rastreado dentro de datos de la web), o que un modelo se ajuste de forma iterativa contra el mismo conjunto de eval hasta que deja de medir la habilidad de fondo.
_Evitar_: fuga, trampa

**Deriva**:
Que la relación real entre las variables y los resultados cambie con el tiempo, de modo que un modelo o una eval construidos con datos más antiguos dejan poco a poco de coincidir con la realidad actual. Es específicamente lo que indica una brecha grande entre los datos held-out y los más recientes (los "del día siguiente"); una brecha entre los resultados offline y en vivo sobre la misma entrada es un problema distinto, un error de ingeniería, no deriva.
_Evitar_: desfase entre entrenamiento y servicio (un término más amplio que cubre cualquier discrepancia entre entrenar y servir; la deriva es específicamente el caso temporal en que el mundo real cambió por debajo del modelo)

**Fidelidad (groundedness)**:
Si cada afirmación de una respuesta generada está realmente respaldada por el contexto recuperado en el que se supone que se apoya, en lugar de inventada, contradicha o adornada con un detalle sin respaldo. Es una comprobación a nivel de afirmación: una respuesta mayormente fiel todavía puede esconder una afirmación sin respaldo.
_Evitar_: corrección de las citas (una comprobación más estricta y separada sobre si el pasaje concreto citado para una afirmación es el que realmente la respalda, distinta de si la afirmación está fundamentada en absoluto)

**Métrica guardrail**:
Una métrica que un experimento o un sistema en producción no intenta optimizar, y que se sigue específicamente para detectar que un cambio la daña en silencio mientras se mejora otra métrica (el OEC). Reportar la mejora de un OEC sin una métrica guardrail revisada junto a él puede esconder una regresión real.
_Evitar_: OEC (una métrica guardrail explícitamente no se optimiza; confundir ambas anula el sentido de seguir cada una por separado)

**Datos held-out**:
Ejemplos de eval, o paráfrasis cercanas de ellos, que el modelo evaluado nunca vio durante el entrenamiento o el fine-tuning. Una puntuación solo es informativa cuando los datos que la sustentan son held-out.
_Evitar_: conjunto de prueba (ambiguo con una partición del pipeline de entrenamiento), datos no vistos

**OEC (Overall Evaluation Criterion, criterio de evaluación global)**:
La métrica concreta, o una pequeña combinación ponderada, que un experimento realmente intenta mover. Un buen candidato a OEC es a la vez movible (lo bastante sensible para cambiar dentro de un experimento factible) y está conectado causalmente con el resultado que de verdad importa, no meramente correlacionado con él.
_Evitar_: cualquier métrica fácil de mover pero sin vínculo causal con el resultado real (el ejemplo del propio Kohavi: las "fotos vistas" se mueven con facilidad pero tienen poco efecto causal sobre los ingresos)

**Sobrerrechazo**:
Que un modelo rechace un prompt que en realidad es seguro, normalmente porque se parece en su redacción a un prompt inseguro o toca un tema de apariencia sensible sin ser dañino. Un modo de fallo genuinamente distinto de un jailbreak, y uno que una eval de red-teaming (solo con prompts inseguros) no puede detectar.
_Evitar_: rechazo falso (se usa como sinónimo en algunas fuentes; este espacio de trabajo estandariza "sobrerrechazo")

**Red-teaming**:
Construir de forma deliberada entradas diseñadas para que un modelo produzca una salida insegura, ya sea por un probador humano o por un método automático de generación de ataques, y medir después con qué frecuencia esas entradas tienen éxito (un jailbreak) contra un modelo dado y sus defensas.
_Evitar_: reportar solo la tasa de éxito de ataque como "la eval de seguridad"; no mide nada sobre el sobrerrechazo, un modo de fallo distinto que necesita su propio conjunto de prueba

**Saturación**:
Que un benchmark llegue a un techo en el que los modelos puntúan casi a la perfección mientras siguen fallando el mismo tipo de tarea en uso real, porque el benchmark dejó de medir la habilidad de fondo y empezó a medir la familiaridad con el propio benchmark.
_Evitar_: contaminación de datos (una causa relacionada pero distinta; la saturación también puede resultar de un ajuste legítimo y extenso contra un benchmark a lo largo del tiempo, no solo de que las preguntas del benchmark se filtren en los datos de entrenamiento)

**Divulgación selectiva**:
Probar varias variantes privadas y no publicadas de un modelo contra un benchmark o una arena y reportar públicamente solo la que mejor puntúa. Convierte una tabla de clasificación en un objetivo de optimización (ley de Goodhart) en lugar de una medición neutral, y crea una brecha entre la puntuación que reporta una tabla de clasificación y la versión del modelo que realmente se lanzó.
_Evitar_: contaminación de datos (otro vector de manipulación; la divulgación selectiva es una práctica de reporte, no datos de eval que se filtran en el entrenamiento)

**Latencia de cola**:
La fracción más lenta de las peticiones (que se suele reportar como p95 o p99), frente al promedio. Una latencia promedio sin cambios puede esconder una cola claramente peor y, a escala, una petición que se abre en abanico hacia muchas llamadas de backend solo termina cuando todas terminan, lo que hace de la cola lo que de verdad decide el tiempo de respuesta real.
_Evitar_: latencia promedio (un agregado que puede mantenerse plano mientras la cola, que domina la experiencia real del usuario, empeora de forma notable)

**Éxito de la tarea**:
Comparar el estado final real de una trayectoria de agente con un estado objetivo anotado, acreditando cualquier secuencia de acciones que alcance el resultado correcto y no solo una secuencia de referencia predeterminada. Es más fiel que la precisión por paso, que solo puede acreditar la única trayectoria que se le dio.
_Evitar_: precisión por paso (una medición más estrecha y frágil: hacer coincidir cada acción con una trayectoria de referencia, lo que penaliza por error un camino distinto e igual de válido hacia el mismo resultado correcto)

**Desfase entre entrenamiento y servicio (training-serving skew)**:
Cualquier discrepancia entre el rendimiento offline de un modelo (en entrenamiento o held-out) y su rendimiento en vivo, en producción. La propia guía de Google lo divide en comparaciones distintas con causas distintas; una discrepancia sobre la misma entrada entre una puntuación offline y un resultado en vivo indica específicamente un error de ingeniería, no deriva ni un problema de modelado.
_Evitar_: deriva (el caso más estrecho y temporal en que el mundo real ha cambiado desde el entrenamiento; no toda discrepancia entre offline y online es deriva)

**Trayectoria**:
La secuencia completa de llamadas a herramientas, decisiones intermedias y turnos que un agente produce mientras trabaja una tarea, frente a la única salida que puntúa una eval por respuesta. Una métrica por respuesta no tiene a qué aferrarse aquí, por eso la evaluación de agentes necesita sus propias métricas.
_Evitar_: respuesta (demasiado estrecho; una trayectoria es todo el proceso de varios pasos, a menudo de varios turnos, no una salida cualquiera dentro de él)
