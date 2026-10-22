---
title: "Evals"
description: "Demuestra que un cambio en un modelo ayudó: construye la eval, mantén los datos held-out con honestidad y defiende el número frente a la contaminación"
type: topic
---

# Aprendizaje: Evals

Sé capaz de construir una eval que detecte una regresión que una revisión a ojo pasaría por alto, y de usarla para tomar una decisión de go/no-go sobre un cambio en un modelo (un fine-tune, un cambio de prompt, un cambio de RAG) que puedas defender con un número y no con una intuición.

**Última lección:** [19. Revisar un informe de eval](lessons/0019-reviewing-an-eval-report.md)

## Cómo se ve el éxito

- Diseñar un conjunto de eval held-out para un cambio de modelo dado, que resista la contaminación y detecte una regresión que una lectura casual pasaría por alto.
- Usar esa eval para tomar y defender una decisión de go/no-go sobre lanzar el cambio, nombrando el número y por qué es fiable.
- Comparar un enfoque de LLM-as-judge con métricas específicas de la tarea para un caso dado, y elegir entre ellos por sus méritos y no por defecto.
- Revisar el informe de eval o el harness de otra persona y nombrar con precisión qué volvería poco fiable su número (un conjunto que no es held-out, un juez sin calibrar, una sola ejecución sin estimación de varianza, una posición en una tabla de clasificación que sustituye a una decisión específica de la tarea), en lugar de decir que se siente flojo.

## Restricciones

- Sin restricción de dominio: cubre por igual la evaluación de fine-tunes, de cambios de prompt y de cambios de RAG, ya que la misma disciplina de eval se aplica a los tres.
- Sin stack fijo ni suposición de experiencia previa.

## Fuera de alcance

- Juzgar una variante, el diseño held-out, las métricas y el conjunto de regresión tal como se enseñan dentro de un único arco de fine-tuning: consulta [`llm/finetuning`](../../llm/finetuning/) (lecciones 0020-0024), subordinado específicamente al fine-tuning. Este espacio de trabajo es dueño de la evaluación como tema y enlaza en lugar de repetir.
- Cuantizar un modelo y juzgar lo que costó la cuantización: consulta [`llm/quantization`](../../llm/quantization/). Ese tema usa una eval para medir la pérdida por cuantización; este enseña cómo se construye la eval.
- Escribir y versionar el prompt bajo prueba: consulta [`llm/prompting`](../../llm/prompting/). Ese tema usa una eval para medir un cambio de prompt; este enseña cómo se construye la eval.
- Destilar un modelo más pequeño y medir lo que perdió frente a su profesor: consulta [`llm/distillation`](../../llm/distillation/). Ese tema usa una eval para comparar un estudiante con su profesor; este enseña cómo se construye la eval.

## El arco

Trece etapas, desde una eval fiable hasta una decisión de go/no-go defendida que tiene en cuenta a las personas, la seguridad, los agentes, RAG, la producción, el costo y el atractivo de una tabla de clasificación pública, y que termina con el criterio para revisar la eval de otra persona y mantener una con honestidad como infraestructura compartida. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Datos held-out y contaminación | 0001 a 0002 | Disciplina de la partición entrenamiento/prueba, detección de la contaminación y sus fuentes | Puedes diseñar un conjunto held-out que resista la contaminación |
| 2. Métricas específicas de la tarea | 0003 a 0004 | Coincidencia exacta, F1, BLEU/ROUGE, métricas de ejecución de código, elegir según la tarea | Puedes elegir y justificar una métrica para una tarea dada |
| 3. LLM-as-judge | 0005 a 0006 | Diseño del prompt del juez, calibración, sesgo de posición y de verbosidad, acuerdo con humanos | Puedes construir un prompt de juez y nombrar sus modos de fallo |
| 4. Construir el harness | 0007 a 0008 | Frameworks de evaluación, ejecuciones reproducibles, convertir un diseño en un número | Tienes un harness de eval ejecutable que produce un número fiable |
| 5. La decisión de go/no-go | 0009 a 0010 | Significancia estadística frente a ruido, umbrales de regresión, comunicar la decisión | Puedes defender una decisión de lanzar o no lanzar con un número y decir por qué es fiable |
| 6. La evaluación humana como método | 0011 | Guías de anotación, muestreo para revisión, kappa de Cohen y lo que cuesta una etiqueta humana | Puedes medir con precisión el acuerdo entre evaluadores y diagnosticar un valor bajo |
| 7. Evaluación de seguridad y red-teaming | 0012 | Red-teaming, jailbreaks y tasa de éxito de ataque, sobrerrechazo y XSTest | Puedes reportar tanto una tasa de rechazo como una métrica de sobrerrechazo, y explicar por qué ninguna por sí sola es una eval de seguridad |
| 8. Evaluar agentes y el uso de herramientas | 0013 | Trayectorias, éxito de la tarea frente a precisión por paso, fiabilidad `pass^k` | Puedes explicar por qué el éxito de la tarea supera a la coincidencia por pasos, y por qué el éxito en un solo intento no es fiabilidad en intentos repetidos |
| 9. Evaluación específica de RAG | 0014 | Fidelidad/groundedness, corrección de las citas, separar un fallo de recuperación de un fallo de generación | Puedes medir la fidelidad y la corrección de las citas por separado, y diagnosticar qué lado de un pipeline RAG falló realmente |
| 10. Evaluación online | 0015 a 0016 | A/B tests, OEC y métricas guardrail, telemetría de producción, deriva, desfase entre entrenamiento y servicio | Puedes elegir un OEC defendible con una métrica guardrail, y atribuir correctamente una brecha entre offline y online a la varianza, a la deriva o a un error de ingeniería |
| 11. Costo y latencia como dimensiones de una eval | 0017 | Latencia de cola frente a promedio, costo por petición/token, incorporar ambos a la decisión de go/no-go | Puedes defender una decisión de go/no-go que pese juntas la calidad, la latencia de cola y el costo, no solo la calidad |
| 12. Benchmarks públicos | 0018 | Contaminación/saturación de los benchmarks estáticos, divulgación selectiva al estilo de las arenas, sesgo de estilo a escala de tabla de clasificación | Puedes explicar por qué una posición en una tabla de clasificación no pasa la prueba del OEC y no sustituye a una decisión de go/no-go específica de la tarea |
| 13. Criterio | 0019 | Revisar informes de eval, zanjar afirmaciones en disputa a partir de fuentes primarias, mantener una suite de evals de la que otros dependen | Se confía en ti para revisar la eval de otra persona y defender su número o nombrar qué lo vuelve poco fiable, y para mantener una suite de evals como infraestructura compartida sin romper las compuertas de otros |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-held-out-and-contamination.md) | Datos held-out y contaminación | Por qué un número de eval solo es tan fiable como lo que el modelo nunca vio |
| [0002](lessons/0002-designing-contamination-resistance.md) | Diseñar resistencia a la contaminación | Prevenir la contaminación en un conjunto de eval propio desde el principio, en lugar de solo detectarla después |
| [0003](lessons/0003-task-specific-metrics.md) | Métricas específicas de la tarea | Coincidencia exacta, F1 a nivel de token y BLEU/ROUGE, y el modo de fallo de cada una |
| [0004](lessons/0004-code-execution-metrics.md) | Métricas de ejecución de código y elegir una métrica | Corrección funcional, el estimador de pass@k y un principio de decisión para elegir una métrica según la tarea |
| [0005](lessons/0005-judge-prompt-design-and-calibration.md) | Diseño y calibración del prompt de un juez | Cómo escribir un prompt de juez que califique de forma consistente, y qué significa que un juez esté calibrado antes de confiar en él |
| [0006](lessons/0006-judge-bias-and-human-agreement.md) | Sesgo del juez y acuerdo con humanos | El sesgo de posición y el sesgo de verbosidad en LLM-as-judge, y cómo medir el acuerdo de un juez con evaluadores humanos |
| [0007](lessons/0007-eval-frameworks-and-harness.md) | Frameworks de evaluación y cómo construir un harness | Las cuatro etapas que tiene todo harness de eval, y elegir entre construir una eval propia como código y reutilizar un harness de benchmarks estandarizado |
| [0008](lessons/0008-reproducible-runs.md) | Ejecuciones reproducibles | Por qué la misma eval puede producir números distintos en ejecuciones distintas, y qué tiene que registrar un resultado fiable junto con la puntuación |
| [0009](lessons/0009-statistical-significance-vs-noise.md) | Significancia estadística frente a ruido | Por qué una diferencia de puntuación hay que medirla frente al ruido que podría producirla por azar, y por qué la comparación pareada supera a tratar dos puntuaciones como independientes |
| [0010](lessons/0010-defending-the-go-no-go-call.md) | Defender la decisión de go/no-go | Cómo fijar un umbral de regresión con honestidad, y todo lo que tiene que citar una defensa completa de un go/no-go |
| [0011](lessons/0011-human-evaluation-as-a-method.md) | La evaluación humana como método | La lección 6 midió un juez frente a evaluadores humanos sin enseñar nunca cómo se produce realmente una calificación humana, y el número crudo de acuerdo en el que se apoyaba resulta necesitar su propia corrección por azar antes de significar algo |
| [0012](lessons/0012-safety-and-red-teaming-evaluation.md) | Evaluación de seguridad y red-teaming | Una eval de seguridad que solo mide con qué frecuencia un modelo rechaza prompts genuinamente inseguros mide la mitad de un compromiso, ya que el mismo ajuste que sube ese número puede subir con la misma facilidad la frecuencia con que el modelo rechaza prompts que nunca fueron inseguros |
| [0013](lessons/0013-evaluating-agents-and-tool-use.md) | Evaluar agentes y el uso de herramientas | Una tarea de agente tiene muchos caminos válidos hacia el mismo resultado correcto, así que puntuarla contra una única secuencia de referencia de acciones repite el error de la coincidencia exacta a escala de trayectoria, e incluso la tasa de éxito de un solo intento esconde con qué frecuencia el mismo agente falla la misma tarea en un segundo intento |
| [0014](lessons/0014-rag-specific-evaluation.md) | Evaluación específica de RAG | llm/rag trazó la línea entre un fallo de recuperación y un fallo de generación pero dejó sin definir la comprobación del lado de la generación, y esa comprobación resulta necesitar dos números separados y no uno, ya que una afirmación fiel y una afirmación bien citada pueden fallar de forma independiente |
| [0015](lessons/0015-ab-tests-and-guardrail-metrics.md) | A/B tests y métricas guardrail | Todas las etapas hasta ahora han sido offline, pero lanzar a usuarios reales necesita su propia métrica de decisión, y esa métrica por sí sola es tan peligrosa como los números únicos de seguridad de los que las etapas anteriores ya advirtieron no fiarse de forma aislada |
| [0016](lessons/0016-production-telemetry-and-drift.md) | Telemetría de producción y deriva | Que un número offline y un número en vivo discrepen no es un problema, son tres distintos, y tratar un error de ingeniería como deriva, o la deriva como un error de ingeniería, manda la corrección al equipo equivocado |
| [0017](lessons/0017-cost-and-latency-as-eval-dimensions.md) | Costo y latencia como dimensiones de una eval | Una mejora de calidad medida sin considerar lo que cuesta servirla es la mitad de una decisión de go/no-go, y un número de latencia promedio esconde justo la cola que determina si los usuarios perciben el sistema como rápido |
| [0018](lessons/0018-public-benchmarks.md) | Benchmarks públicos | Una posición en una tabla de clasificación es una métrica movible, optimizada por personas que no eres tú, para usuarios que no son los tuyos, puntuada por un proceso con sus propios vectores de manipulación documentados, lo que la convierte exactamente en el tipo de métrica de la que la lección 15 advirtió no fiarse como señal de go/no-go |
| [0019](lessons/0019-reviewing-an-eval-report.md) | Revisar un informe de eval | Nombrar con precisión qué volvería poco fiable el número de un informe de eval (contaminación, un juez sin calibrar, una sola ejecución sin estimación de varianza, una posición en una tabla de clasificación que sustituye a una decisión específica de la tarea), en lugar de decir que se siente flojo |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Datos held-out y contaminación](reference/held-out-data-and-contamination.md): las dos vías de contaminación, la prueba de instrucción guiada y el kit de prevención para un conjunto de eval propio
- [Métricas](reference/metrics.md): coincidencia exacta, F1, BLEU/ROUGE y pass@k lado a lado, con la fórmula de pass@k y el principio de decisión para elegir entre ellas
- [LLM-as-judge](reference/llm-as-judge.md): la lista de comprobación de diseño del prompt del juez, calibración y compresión de puntuaciones, sesgo de posición y de verbosidad, y la vara del acuerdo entre humanos
- [Harness de evals](reference/eval-harness.md): el pipeline de cuatro etapas, openai/evals frente a lm-evaluation-harness, y lo que un número defendible registra junto con la puntuación
- [Go/No-Go](reference/go-no-go.md): la fórmula del error estándar, la comparación pareada, fijar un umbral con honestidad y todo lo que cita una defensa completa

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
