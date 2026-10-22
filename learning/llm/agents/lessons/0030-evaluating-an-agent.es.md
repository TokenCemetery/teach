---
title: "30. Evaluar un agente"
description: "Medir el éxito de un agente a nivel de resultado frente a nivel de trayectoria, y por qué una sola ejecución exitosa no significa que el agente sea fiable"
type: lesson
---

# Lección 30. Evaluar un agente

**Vínculo con la misión:** Diagnosticar un agente que falla a partir de su trayectoria, nombrando la causa (un bucle, un contexto envenenado, una herramienta mal especificada, una condición de parada equivocada) en lugar de reescribir el prompt al azar.
**Fuente principal:** [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
**Requisitos previos:** [Lección 29](0029-tracing-and-trajectory-replay.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 29: Cuando lees la trayectoria de un agente para diagnosticar un fallo, ¿qué dos cosas deberías buscar primero: la decisión que tomó el modelo, o el resultado real que produjo esa decisión?

<details markdown="1"><summary>Comprobación</summary>

Ambas, pero en este orden: primero, la decisión que tomó el modelo en cada paso (qué herramienta eligió, qué argumentos pasó). Segundo, lo que la herramienta realmente devolvió. Una decisión razonable con un resultado erróneo apunta a un problema en la implementación de la herramienta. Una decisión poco razonable con un resultado razonable apunta a un fallo de razonamiento. Mezclarlas es donde el diagnóstico se atasca.

</details>

2. ▢ De la lección 29: Si una trayectoria muestra al modelo tomando la decisión correcta cinco veces seguidas pero el agente no logra completar la tarea, ¿qué sugiere ese patrón que está roto?

<details markdown="1"><summary>Comprobación</summary>

Sugiere que lo roto es el harness o las propias implementaciones de las herramientas, no el razonamiento del modelo. El modelo elige correctamente, pero algo más en el bucle no se ejecuta como se pretendía. Podría ser una herramienta que afirma éxito pero no realiza la acción, un harness que corta el bucle demasiado pronto, o un resultado que se añade mal a la transcripción.

</details>

## Qué debes saber

### Resultado frente a trayectoria

Cuando evalúas un agente, puedes medir dos cosas distintas, y no son lo mismo.

**El éxito del resultado** significa: ¿Llegó el agente al estado final correcto? El archivo se actualizó correctamente. El ticket se clasificó en la categoría correcta. La pregunta del usuario se respondió con exactitud. Compruebas el resultado inspeccionando lo que ve el usuario.

**La corrección de la trayectoria** significa: ¿Siguió el agente la secuencia correcta de pasos para llegar ahí? Llamó a las herramientas correctas en el orden correcto con argumentos sensatos, interpretó los resultados con exactitud y evitó los bucles circulares.

Una tarea de agente suele tener muchos caminos válidos hacia el mismo resultado correcto. Calificar contra una única trayectoria de referencia suele ser un error; calificar el resultado (¿se actualizó realmente el archivo?, ¿se clasificó realmente bien el ticket?) suele ser lo correcto. Sin embargo, la trayectoria sigue importando: es como diagnosticas *por qué* algo falló, que es lo que enseñan las lecciones 27 a 29 de este track. El resultado te dice si el agente tuvo éxito; la trayectoria te dice por qué falló.

### pass^k: fiabilidad a lo largo de pruebas repetidas

Una sola ejecución exitosa no te dice que el agente sea fiable. El mismo agente en la misma tarea puede fallar en un segundo intento por la naturaleza estocástica de los muchos puntos de decisión de un agente que se acumulan a lo largo de una trayectoria larga. pass^k mide la probabilidad de que el agente tenga éxito en las k pruebas independientes de la misma tarea. Si un agente acierta 8 de 10 veces en una tarea, sabes más que si acertó una vez: tienes evidencia de que es fiable en torno a un 80 por ciento en esa tarea. No lo confundas con la precisión de la tarea; es una vara de fiabilidad mucho más exigente y honesta que una sola ejecución con éxito o fallo. Para el tratamiento completo de cómo diseñar y calcular pass^k en tus propias evaluaciones, consulta la lección que sigue a esta.

### Qué miden realmente los papers de benchmarks

Tres papers sustentan las fuentes de esta etapa, y cada uno representa una elección distinta de cómo calificar a los agentes:

**tau-bench** (Yao et al., 2024) evalúa el uso de herramientas de varios turnos frente a un usuario simulado (un modelo de lenguaje que actúa como una persona) y una política de dominio (reglas sobre qué constituye el éxito). Usa medidas de fiabilidad con pruebas repetidas, así que ves puntuaciones pass^k, no resultados de un solo intento.

**SWE-bench** (Jimenez et al., 2023) evalúa agentes sobre issues reales de repositorios con el conjunto de pruebas del propio proyecto como comprobación del resultado. Si las pruebas pasan, el agente resolvió el issue. La trayectoria no está restringida ni se califica en absoluto; solo importa el resultado.

**GAIA** (Mialon et al., 2023) plantea preguntas fáciles para una persona y difíciles para un agente, que requieren uso de herramientas en varios pasos para llegar a una única respuesta inequívoca. Mide si el agente da con la respuesta correcta, no si su razonamiento fue elegante.

Los tres priorizan el éxito del resultado sobre la elegancia de la trayectoria, y los tres usan evaluación con pruebas repetidas o múltiples casos de prueba para ir más allá de la suerte de una sola ejecución.

### El traspaso a la profundidad

Esta lección te da el vocabulario: resultado frente a trayectoria, pass^k, éxito de la tarea. El tratamiento completo de construir un eval de agentes vive en el track llm/evals, lección 13, Evaluar agentes y el uso de herramientas. Esa lección cubre las métricas, el diseño de jueces, cómo construir un conjunto de prueba reservado, qué significa la significancia estadística y cómo evitar evaluar por accidente lo equivocado. El trabajo de este track es solo asegurarse de que sabes qué medir desde el principio. Lee esta lección para conocer los conceptos; lee la lección 13 de llm/evals para la profundidad.

## Práctica

1. ▢ Un agente registra con éxito un ticket en tu gestor de incidencias al primer intento. Lo ejecutas otra vez con un ticket distinto, y falla en silencio, creando un ticket vacío sin texto. Lo ejecutas una tercera vez y tiene éxito. ¿Está el agente listo para producción según estos datos?

<details markdown="1"><summary>Comprobación</summary>

No. Tienes un éxito, un fallo y otro éxito. Son 2 éxitos de 3 pruebas, lo que sugiere una fiabilidad de aproximadamente el 67 por ciento. Todavía no tienes suficientes datos, y el 67 por ciento es demasiado bajo para la mayoría de los usos en producción. Necesitas al menos de 10 a 20 pruebas con tickets diversos para establecer un pass^k fiable. El instinto equivocado es asumir que el único fallo fue casual y que el agente está bien; el correcto es tomarse en serio pass^k.

</details>

2. ▢ Estás diagnosticando un agente que no logró actualizar un registro de base de datos. Miras la trayectoria y ves que el modelo eligió la herramienta update_record correcta con el ID de registro y los nuevos valores correctos. La herramienta devolvió éxito: "ok, record updated". Pero cuando compruebas la base de datos, el registro en realidad no se actualizó. ¿A qué nivel deberías mirar para arreglarlo?

<details markdown="1"><summary>Pista</summary>

La decisión del modelo y la trayectoria parecen correctas. El problema no está en el razonamiento ni en la toma de decisiones.

</details>

<details markdown="1"><summary>Comprobación</summary>

Deberías inspeccionar la propia implementación de la herramienta. La trayectoria muestra que el modelo tomó la decisión correcta y la herramienta afirmó éxito, pero el resultado es erróneo. Algo entre el valor de retorno de la herramienta y el estado real de la base de datos está roto. Podría ser una herramienta que registra éxito pero en realidad no ejecuta, un harness que no espera a que la herramienta termine o un problema de conexión con la base de datos. El diagnóstico de la trayectoria aquí significa mirar más allá de las palabras que devolvió la herramienta y comprobar qué pasó realmente.

</details>

3. ▢ Estás evaluando agentes con SWE-bench (issues reales de GitHub, conjuntos de pruebas del proyecto como comprobación del resultado). La trayectoria de un agente muestra que tomó una decisión que crees que no es óptima, con llamadas a herramientas extra frente a un camino más directo. Pero el conjunto de pruebas del issue pasa. ¿Deberías bajar la puntuación del agente por la trayectoria no óptima?

    - a) Sí, porque la trayectoria muestra ineficiencia
    - b) No, porque en SWE-bench solo importa que pase el conjunto de pruebas
    - c) Puntuar el resultado como aprobado pero señalar la trayectoria para una optimización futura
    - d) Solo si el camino no óptimo usó más tokens que una línea base

<details markdown="1"><summary>Comprobación</summary>

**b)** No, porque en SWE-bench solo importa que pase el conjunto de pruebas. SWE-bench está diseñado para calificar resultados, no trayectorias. Si las pruebas pasan, el agente resolvió el issue, sin importar si tomó el camino más elegante. El instinto equivocado es calificar la elegancia de la trayectoria además del resultado; eso confunde dos evaluaciones separadas. **a)** te desplazaría hacia una métrica que SWE-bench no usa. **c)** añade una complejidad que SWE-bench no requiere para su objetivo principal. **d)** introduce una restricción distinta (el presupuesto de tokens) que no forma parte del diseño de SWE-bench.

</details>

4. ▢ Estás evaluando un agente en una tarea solo por el resultado: o llega al estado final correcto, o no. Lo ejecutas 100 veces y tiene éxito 73 veces. Mejoras el system prompt y vuelves a probar. Ahora tiene éxito 75 veces de 100. La mejora es pequeña. ¿Qué sugiere este patrón que deberías hacer a continuación?

<details markdown="1"><summary>Comprobación</summary>

Sugiere que las mejoras del prompting por sí solas no bastan para atender los fallos de raíz. La ganancia del 73 al 75 por ciento es modesta; la mayoría de los fallos persisten a pesar de unas mejores instrucciones. Deberías leer las trayectorias de las ejecuciones fallidas para identificar el modo de fallo real (una herramienta mal usada, un error de lógica, un problema de contexto, un obstáculo que el agente no maneja) y luego arreglar ese problema concreto. Alternativamente, la tarea puede ser simplemente demasiado difícil para el modelo o el conjunto de herramientas actuales, y ningún cambio de prompt ayudará. El diagnóstico de la trayectoria te dice cuál de las dos cosas es cierta.

</details>

## Prácticas en el mundo real

- [ ] Elige una tarea de agente simple y repetible (por ejemplo, "buscar a una persona en un directorio", "convertir un formato de archivo", "responder una pregunta factual usando una herramienta"). Ejecuta el agente 10 veces y registra si pasa o falla cada vez. Calcula el pass^k empírico y anota qué te dice ese número que una sola ejecución no te diría.

- [ ] Toma un paper de benchmark publicado sobre agentes (tau-bench, SWE-bench, GAIA, WebArena u otro). Lee su sección de evaluación e identifica: cuál es la métrica de resultado, si la trayectoria está restringida o es libre, y qué medida de fiabilidad usa.

- [ ] Mañana: Encuentra la trayectoria de un agente de una fuente pública (documentación, blog, GitHub). Reescribe una rúbrica de evaluación que califique la trayectoria solo por el resultado (¿coincidió el estado final con el objetivo), y una rúbrica aparte que califique por la trayectoria (¿tomó pasos sensatos). Aplica ambas rúbricas a la misma trayectoria y compara las puntuaciones. Escribe un párrafo sobre si el resultado o la trayectoria te dijo más sobre si el agente funcionó.

## Para profundizar

- [Lección 13: Evaluar agentes y el uso de herramientas](../../evals/lessons/0013-evaluating-agents-and-tool-use.md)
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
