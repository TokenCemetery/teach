---
title: "Recursos"
description: "Fuentes de confianza sobre evals"
type: resources
---

# Recursos de evals

## Conocimiento

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Recorrido de profesionales para convertir una pregunta vaga como "¿mejoró?" en criterios de éxito medibles y un conjunto de eval held-out. Úsalo para: diseñar la propia eval antes de recurrir a un framework.
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
  Framework oficial para definir y ejecutar una eval como código: prompts, lógica de calificación y un registro de evals existentes que sirven como ejemplos resueltos. Úsalo para: cómo estructurar y ejecutar una eval propia.
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  El harness estándar de facto para ejecutar un modelo contra benchmarks estandarizados, con configuraciones de tareas que muestran cómo se estructuran y puntúan en la práctica los conjuntos held-out. Úsalo para: ejecutar o adaptar un benchmark existente en lugar de construir una eval desde cero.
- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
  Introduce LLM-as-judge para tareas abiertas y mide sus sesgos frente a la preferencia humana: sesgo de posición, sesgo de verbosidad y sesgo de autopromoción. Úsalo para: decidir si un juez LLM es fiable en un caso dado y qué corregir si lo es.
- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
  Biblioteca de métricas estándar específicas de tareas (BLEU, ROUGE, coincidencia exacta, F1 y más) con la definición y los modos de fallo de cada una. Úsalo para: el lado de las métricas específicas de la tarea en la comparación entre métrica y juez LLM.
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
  Un método concreto para comprobar si los datos de un benchmark se filtraron al conjunto de entrenamiento de un modelo, con la técnica de adivinar el resto de la instancia que lo detecta. Úsalo para: defender la honestidad de un conjunto held-out frente a la afirmación concreta de que "el modelo simplemente memorizó esto".
- [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
  Introduce la convención de la canary string (una frase marcadora única incrustada en los datos del benchmark que pide a los rastreadores excluirla de los corpus de entrenamiento) como técnica preventiva de resistencia a la contaminación para el lanzamiento de un benchmark propio. Úsalo para: diseñar desde el principio un conjunto de eval propio que resista la contaminación, en lugar de detectarla después.
- [Paper: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
  Introduce la corrección funcional (ejecutar el código generado contra casos de prueba en lugar de comparar texto) y el estimador insesgado de pass@k, con la fórmula combinatoria que evita la alta varianza de volver a muestrear directamente k completaciones. Úsalo para: evaluar la generación de código, y para el principio general de comprobar el comportamiento antes que la similitud de texto siempre que una tarea sea ejecutable.

- [Article: "Cohen's kappa", Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  El estadístico de acuerdo entre evaluadores corregido por azar: su fórmula, por qué un kappa de 0 significa que no es mejor que el azar y su tendencia conocida a subestimar el acuerdo en una categoría rara. Úsalo para: medir con precisión el acuerdo entre evaluadores humanos en lugar de estimar a ojo un porcentaje de acuerdo crudo.
- [Article: "Inter-rater reliability", Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  Explica por qué el acuerdo crudo por probabilidad conjunta engaña (se infla por azar, y más con menos categorías) y presenta el alfa de Krippendorff como la generalización del acuerdo corregido por azar a cualquier número de evaluadores y cualquier nivel de medición. Úsalo para: elegir el estadístico de acuerdo adecuado cuando hay más de dos evaluadores o calificaciones no categóricas.
- [Paper: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal", Mazeika et al., 2024](https://arxiv.org/abs/2402.04249)
  Introduce un framework estandarizado para evaluar métodos automáticos de red-teaming contra modelos y defensas, a escala y de forma comparable, donde el campo antes carecía de uno. Úsalo para: la tasa de éxito de ataque como métrica, y la distinción entre un método de generación de ataques y una forma rigurosa de evaluarlo.
- [Paper: "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models", Röttger et al., 2023](https://arxiv.org/abs/2308.01263)
  Un conjunto de pruebas con prompts seguros escritos para parecerse a prompts inseguros, específicamente para sacar a la luz el sobrerrechazo. Úsalo para: la tensión precisa entre la inocuidad (rechazar prompts inseguros) y la utilidad (no rechazar los seguros), y una forma concreta de medir a un modelo que cae mal en ese compromiso.
- [Paper: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Evalúa agentes comparando el estado de la base de datos al final de la conversación con un estado objetivo anotado, e introduce `pass^k` para medir la fiabilidad de un agente a lo largo de intentos repetidos de la misma tarea. Úsalo para: por qué el éxito de la tarea supera a la coincidencia de trayectoria paso a paso, y la distinción precisa y fácil de confundir entre `pass^k` y el `pass@k` de la lección 4.
- [Paper: "AgentBench: Evaluating LLMs as Agents", Liu et al., 2023](https://arxiv.org/abs/2308.03688)
  Un benchmark multidimensional sobre 8 entornos interactivos distintos que pone a prueba el razonamiento y la toma de decisiones de un LLM como agente, y encuentra una brecha significativa entre los mejores modelos y los más pequeños específicamente en entornos agénticos. Úsalo para: evidencia de que la capacidad agéntica es algo distinto que medir, no implícito en el rendimiento de un benchmark de un solo turno.
- [Paper: "Ragas: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Un framework sin referencia que separa en métricas independientes las dimensiones de calidad de la recuperación, fidelidad y calidad de la generación de un sistema RAG. Úsalo para: calcular una puntuación de fidelidad sin necesitar una respuesta de referencia escrita por una persona, y para mantener el fallo de recuperación y el de generación diagnosticables como preguntas separadas.
- [Paper: "Enabling Large Language Models to Generate Text with Citations" (ALCE), Gao et al., 2023](https://arxiv.org/abs/2305.14627)
  Introduce métricas automáticas de calidad de las citas correlacionadas con el juicio humano, y el hallazgo de que incluso los mejores sistemas carecen de respaldo completo de citas para aproximadamente la mitad de sus afirmaciones en un conjunto de prueba. Úsalo para: la corrección de las citas como una comprobación más estricta y separada de la fidelidad.
- [Paper: "Seven Rules of Thumb for Web Site Experimenters", Kohavi et al., 2014](https://exp-platform.com/Documents/2014%20experimentersRulesOfThumb.pdf)
  La guía de profesionales de Kohavi y sus coautores para ejecutar experimentos controlados online, incluido el concepto de OEC (movible y conectado causalmente con el resultado real) y las métricas guardrail. Úsalo para: elegir un OEC defendible en lugar de una métrica fácil de mover pero sin causalidad, y por qué hay que seguir una métrica guardrail junto a él.
- [Guide: "Rules of Machine Learning", Zinkevich, Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
  La guía interna de ingeniería de ML de Google, que incluye la Regla n.º 37 (medir el desfase entre entrenamiento y servicio como varias comparaciones distintas, no una) y la Regla n.º 8 (requisitos de frescura). Úsalo para: cuál exactamente de las varias causas posibles de una brecha entre offline y online (varianza ordinaria, deriva o un error de ingeniería) aplica realmente, y por qué cada una necesita una corrección distinta.
- [Paper: "The Tail at Scale", Dean and Barroso, 2013](https://www.barroso.org/publications/TheTailAtScale.pdf)
  La explicación canónica de por qué la latencia de cola, y no la latencia promedio, determina la capacidad de respuesta real a escala, sobre todo cuando una petición se abre en abanico hacia muchas llamadas de backend. Úsalo para: por qué una decisión de go/no-go necesita un percentil (p95/p99), y no solo un promedio, antes de descartar una regresión de latencia.
- [Paper: "The Leaderboard Illusion", Singh et al., 2025](https://arxiv.org/abs/2504.20879)
  Documenta la divulgación selectiva en Chatbot Arena: pruebas privadas previas al lanzamiento de muchas variantes de modelo (27 solo para Llama 4) y un acceso a datos amplio y asimétrico que favorece a un puñado de proveedores de modelos cerrados. Úsalo para: un ejemplo concreto, actual y bien documentado de por qué una posición en una tabla de clasificación no es por sí sola una medición neutral y fiable.
- [Article: "Does Style Matter?", LMArena](https://lmarena.ai/blog/style-control)
  El análisis de la propia arena que muestra que las clasificaciones cambian de forma notable cuando se controlan la longitud de la respuesta y el formato markdown. Úsalo para: confirmar que el mecanismo del sesgo de verbosidad de la lección 6 opera de forma idéntica a escala completa de tabla de clasificación, con evaluadores humanos en lugar de un único juez LLM.

## Lagunas

- Todavía no hay una fuente dedicada a las pruebas de significancia estadística para las diferencias de puntuación de una eval (error estándar de una proporción, pruebas de significancia pareadas como la de McNemar). La misión lo necesita para la pregunta de la etapa 5, "¿esta diferencia es real o ruido?"; la lección 9 lo enseña a partir de un método estadístico estándar y estable y no de una única fuente citada, y esta laguna debería cerrarse cuando se encuentre una buena fuente de nivel profesional.
