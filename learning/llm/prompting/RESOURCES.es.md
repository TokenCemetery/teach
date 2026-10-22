---
title: Recursos
description: "Fuentes de confianza sobre prompting"
type: resources
---

# Recursos de prompting

## Conocimiento

- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  La guía consolidada de un proveedor: instrucciones claras, ejemplos, etiquetas XML, roles, thinking, contexto largo y formato de salida, con prompts de antes y después. Úsalo para: la línea base del profesional en las etapas 2 a 6, leída como el comportamiento documentado de un solo proveedor.
- [Docs: "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  El consejo de definir criterios de éxito y pruebas antes de iterar, y una breve nota de que no todo eval fallido se arregla mejor con prompting. Úsalo para: el hábito de medir primero.
- [Docs: "Long context prompting", section of Prompting best practices, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  Colocar los documentos largos antes de la consulta, envolver cada uno en etiquetas con sus metadatos y pedir primero las citas relevantes. Úsalo para: distribuir una entrada larga.
- [Docs: "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Una función del proveedor que impone un esquema JSON a la respuesta, documentada junto con lo que el prompt por sí solo no garantiza. Úsalo para: el límite entre pedir estructura e imponerla.
- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Cómo se hace coincidir un prefijo en caché, qué lo invalida y el orden que debe mantener el prompt para que haya un acierto. Úsalo para: distribuir un prompt de modo que sus partes estables se almacenen en caché.
- [Docs: "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  Cómo un proveedor nombra snapshots fijos y alias móviles, y que cada ID tiene su propio calendario de retirada. Úsalo para: fijar un prompt al modelo contra el que se probó.
- [Docs: "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  La mecánica de API de una fase de thinking: el presupuesto de tokens, su mínimo y cómo el thinking cuenta para el límite de salida. Úsalo para: los datos de presupuesto detrás del prompting de un modelo de razonamiento; el consejo sobre redacción está en la guía de buenas prácticas.
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Convertir "¿es mejor este prompt?" en criterios de éxito y un diseño de eval, incluidos los casos límite y la comparación con una línea base. Úsalo para: decidir contra qué debe juzgarse un cambio de prompt antes de cambiar nada.
- [Docs: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Mitigaciones a nivel de prompt y de sistema, incluido el filtrado de la entrada y la limitación de lo que el modelo puede hacer. Úsalo para: qué defensas le corresponden a quien escribe el prompt.
- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  La guía de un segundo proveedor sobre instrucciones, ejemplos few-shot, prefijos y descomposición de una tarea. Úsalo para: comprobar si una técnica es general o comportamiento de un solo proveedor.
- [Docs: "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Cómo una lista de mensajes con rol se convierte en la única secuencia de tokens con la que se entrenó un modelo, con salida real de plantillas. Úsalo para: lo que el modelo ve realmente.
- [Repo: "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Ejercicios en notebooks sobre roles, separar los datos de las instrucciones, ejemplos, razonamiento paso a paso y evitar la alucinación. Úsalo para: práctica en las etapas 1 a 4.
- [Paper: "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  Un estudio y una taxonomía de técnicas de prompting con vocabulario coherente. Úsalo para: ubicar una técnica que te encuentras en la práctica y fijar qué significa un término.
- [Paper: "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  Muestra que cambios de formato que preservan el significado (separadores, mayúsculas, espaciado) mueven la precisión few-shot en márgenes grandes. Úsalo para: por qué la edición de un prompt es una afirmación que probar, no una elección de estilo.
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  Encuentra que reemplazar al azar las etiquetas de las demostraciones apenas perjudica, mientras que el formato, el espacio de etiquetas y la distribución de entrada sí importan. Úsalo para: qué enseñan realmente los ejemplos few-shot.
- [Paper: "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Nombra el sesgo de etiqueta mayoritaria, de recencia y de token común en los prompts few-shot y propone la calibración contextual. Úsalo para: los sesgos que trae un conjunto de ejemplos.
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  Muestra que el orden de los mismos ejemplos few-shot hace oscilar la precisión desde casi el estado del arte hasta casi el azar. Úsalo para: por qué el orden de los ejemplos es una variable que controlar.
- [Paper: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  El resultado original de chain-of-thought few-shot, y su hallazgo de que la mejora aparece solo a una escala de modelo suficiente. Úsalo para: cuándo ayuda pedir razonamiento.
- [Paper: "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Chain-of-thought zero-shot: una sola frase disparadora que provoca razonamiento sin ejemplos. Úsalo para: razonamiento sin demostraciones escritas a mano.
- [Paper: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  Muestrear varias rutas de razonamiento y tomar la respuesta mayoritaria. Úsalo para: cambiar tokens por precisión en una tarea con una única respuesta comprobable.
- [Paper: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  Muestra un chain-of-thought del modelo que omite el rasgo sesgador que realmente motivó su respuesta. Úsalo para: por qué el razonamiento escrito no es una explicación fiel.
- [Paper: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  Mide cómo cae la precisión de razonamiento bajo restricciones estrictas de formato de salida. Úsalo para: el costo de forzar un formato y cómo ordenar los campos.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  La curva en U: la información al principio y al final de un contexto largo se usa mejor que la del medio. Úsalo para: decidir dónde van los documentos y la pregunta.
- [Paper: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  Define los niveles de privilegio de system, usuario y salida de herramientas, y entrena a un modelo para seguir el superior en caso de conflicto. Úsalo para: por qué el lugar donde está una instrucción cambia su peso.
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  Prueba 162 personas en system prompts con cuatro familias de modelos y 2,410 preguntas factuales, y no encuentra mejora respecto a no usar persona, con un efecto de la persona en gran parte aleatorio. Úsalo para: zanjar con datos la disputa sobre el role prompting.
- [Paper: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Introduce la inyección de prompt indirecta a través de contenido recuperado y la demuestra contra aplicaciones reales. Úsalo para: cómo un atacante llega a un prompt en el que nunca escribe.
- [Paper: "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  Compara el fine-tuning no supervisado con la recuperación para añadir conocimiento y encuentra que la recuperación es consistentemente mejor, tanto para conocimiento visto en el entrenamiento como para hechos nuevos. Úsalo para: la decisión entre prompt, RAG o fine-tuning.
- [Article: "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  La entrada de riesgo de la industria: inyección directa e indirecta, impactos y mitigaciones ordenadas según dónde residen. Úsalo para: el vocabulario compartido y la lista de mitigaciones.
- [Article: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Datos privados, contenido no confiable y un canal de exfiltración, juntos, hacen explotable la inyección, y quitar una de las patas es la defensa. Úsalo para: por qué la defensa real reside fuera del prompt.
- [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  Un argumento de profesional a favor de comprobaciones al estilo de pruebas unitarias y trazas reales registradas como base para iterar un prompt. Úsalo para: construir un conjunto de regresión a partir de fallos reales.

## Lagunas

- Las guías de prompt engineering, razonamiento y salida estructurada de OpenAI serían la visión de un tercer proveedor, pero todas las páginas de `platform.openai.com` y `developers.openai.com` respondieron con 403 a una comprobación con script y a una con navegador, así que no se pudo verificar que ninguna se resuelva. Agrégalas cuando alguna pueda verificarse.
- Ninguna fuente revisada por pares mide directamente el versionado de prompts ni la práctica de plantillas. Las lecciones 15 y 16 lo enseñan a partir de la documentación de proveedores y de la práctica habitual de ingeniería de software, y lo dicen.
