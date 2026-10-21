---
title: Recursos
description: "Fuentes de confianza sobre agentes con LLM"
type: resources
---

# Recursos de agentes con LLM

## Conocimiento

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  Traza la distinción entre flujo de trabajo y agente sobre la que se construye este track, y luego nombra los patrones componibles más comunes (encadenamiento de prompts, enrutamiento, paralelización, orquestador y workers, evaluador y optimizador) y defiende el más simple que funcione. Úsalo para: el vocabulario de la etapa 1 y el argumento de la etapa 16 para no construir un agente.
- [Guide: "A Practical Guide to Building Agents", OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  El enfoque de un segundo proveedor sobre el mismo material: cuándo una tarea justifica un agente, categorías de herramientas, orquestación para un agente frente a varios, y guardarraíles. Úsalo para: comprobar que una afirmación de la etapa 1 o de la etapa 8 trata de agentes y no del producto de un solo proveedor.
- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Trata el nombre, la descripción, el esquema de parámetros y la forma de retorno de una herramienta como superficie del prompt y no como un contrato de API, incluido cómo la salida de una herramienta consume el presupuesto de contexto. Úsalo para: la etapa 4, y para entender por qué una herramienta diseñada como un endpoint REST resulta una peor herramienta.
- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Defiende tratar la ventana de contexto como un presupuesto finito que hay que curar, y cubre la compactación, la toma de notas en memoria externa y los subagentes como aislamiento de contexto. Úsalo para: las etapas 5 y 6.
- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
  Introduce intercalar trazas de razonamiento con acciones de herramientas en un mismo bucle, en lugar de planificar todo por adelantado o actuar sin razonar. Úsalo para: la etapa 7, y para el nombre del patrón que la mayoría de los bucles de agentes siguen implementando.
- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
  Introduce la autocrítica como etapa explícita del bucle: el agente reflexiona en lenguaje natural sobre un intento fallido y lleva esa reflexión al reintento. Úsalo para: el material de reflexión de la etapa 7, y para lo que cuesta la autocrítica en tokens.
- [Paper: "Toolformer: Language Models Can Teach Themselves to Use Tools", Schick et al., 2023](https://arxiv.org/abs/2302.04761)
  Muestra el uso de herramientas aprendido por el modelo en lugar de inducido con prompts, que es la frontera entre este track y `llm/finetuning`. Úsalo para: la explicación de la etapa 2 de por qué un modelo emite una llamada a herramienta.
- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  La explicación de un proveedor sobre su propio formato de transmisión de llamadas a herramientas: el esquema JSON de una definición de herramienta, cómo se representan como mensajes una petición de llamada a herramienta y su resultado, y las llamadas a herramientas en paralelo. Úsalo para: el par de petición y respuesta capturado de la etapa 2, leído junto con la guía de OpenAI de abajo como la diferencia.
- [Guide: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
  El formato de transmisión de un segundo proveedor para la misma mecánica, incluido el paso de una única llamada a función a una convención general de llamadas a herramientas. Úsalo para: la etapa 2, como el segundo proveedor cuyo formato aparece solo como la diferencia respecto al primero.
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
  La especificación normativa de MCP: herramientas, recursos, prompts, sampling, los transportes y el ciclo de vida del servidor. Úsalo para: la etapa 9, y para zanjar cualquier afirmación sobre MCP desde la fuente y no desde la documentación de un cliente.
- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  Sostiene que presentar las herramientas como código contra el que escribe un agente, en lugar de definiciones de herramientas individuales cargadas en el contexto, cambia lo que cuesta un conjunto grande de herramientas. Úsalo para: el problema del descubrimiento de herramientas a escala de la etapa 9 y el material de ejecución de código de la etapa 10.
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  Un relato de producción de un sistema de orquestador y workers, incluido el múltiplo de costo en tokens respecto a un solo agente y dónde se rompió realmente la coordinación. Úsalo para: el argumento de la etapa 8 de que lo multiagente compra paralelismo y aislamiento de contexto, a un precio medido.
- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  El caso contrario, que sostiene que repartir el trabajo entre agentes fragmenta el contexto y produce decisiones que entran en conflicto. Úsalo para: la etapa 8, leído junto al relato de Anthropic de arriba y no en lugar de él.
- [Article: "The Lethal Trifecta for AI Agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Nombra la combinación que hace explotable a un agente: acceso a datos privados, exposición a contenido no confiable y capacidad de comunicarse con el exterior. Úsalo para: el marco central de la etapa 14, y para entender por qué las instrucciones del prompt no son una defensa.
- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  El catálogo de consenso de riesgos de las aplicaciones con LLM, incluidos la inyección de prompt, la agencia excesiva y la exposición de la cadena de suministro, cada uno con sus mitigaciones. Úsalo para: la lista de comprobación de la etapa 14, y para el vocabulario que una persona de seguridad ya estará usando.
- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  Convenciones neutrales respecto a los proveedores para los spans y atributos que emite una ejecución de agente, que es lo que permite leer en un backend de trazado la vista de trayectoria de otro. Úsalo para: la etapa 12, como la respuesta neutral respecto al proveedor sobre qué debe contener una traza.
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Evalúa agentes en uso de herramientas de varios turnos frente a un usuario simulado y una política de dominio, e introduce una medida de fiabilidad con pruebas repetidas en lugar del éxito en una sola prueba. Úsalo para: la distinción de la etapa 13 entre tener éxito una vez y tener éxito de forma fiable.
- [Paper: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", Jimenez et al., 2023](https://arxiv.org/abs/2310.06770)
  Evalúa agentes sobre issues reales de repositorios, con las propias pruebas del proyecto como comprobación del resultado. Úsalo para: el ejemplo de la etapa 13 de un benchmark calificado por resultado donde la trayectoria no tiene restricciones.
- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
  Describe el bucle de captura de pantalla y acción que ejecuta un agente de uso del ordenador: una observación es una captura de pantalla y no un resultado de herramienta, y una acción es una coordenada de pantalla o una pulsación de tecla y no un argumento de función. Úsalo para: el material de anclar una acción a una coordenada de la etapa 11, y para entender por qué este bucle necesita una historia de fiabilidad distinta a la de uno que llama herramientas.
- [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
  Un entorno web autoalojado con comprobaciones de corrección funcional, construido para agentes que actúan a través de un navegador. Úsalo para: la etapa 11, como el estándar frente al cual se hacen las afirmaciones de fiabilidad de los agentes de navegador.
- [Paper: "GAIA: A Benchmark for General AI Assistants", Mialon et al., 2023](https://arxiv.org/abs/2311.12983)
  Preguntas fáciles para una persona y difíciles para un agente, que exigen uso de herramientas en varios pasos con una única respuesta inequívoca. Úsalo para: la etapa 13, como contrapeso a los benchmarks que un modelo puede superar sin actuar.
- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Almacenar en caché un prefijo de prompt para reducir el costo y la latencia repetidos, incluido por qué las definiciones de herramientas y el system prompt estables de un agente son exactamente el prefijo que vale la pena almacenar y qué invalida la caché en silencio. Úsalo para: el material de amplificación de tokens y costo de la etapa 15.

## Lagunas

- No existe una referencia neutral respecto al proveedor para los formatos de transmisión de las llamadas a herramientas. Cada proveedor documenta solo el suyo, así que los pares de petición y respuesta capturados que muestra este track hay que tomarlos de la documentación de los proveedores y conciliarlos a mano.
- La ejecución durable y reanudable de agentes está documentada sobre todo dentro de frameworks individuales, lo que no es ni neutral respecto al proveedor ni lo bastante estable como para listarlo todavía. La etapa 15 necesita una fuente que no sea ninguna de las dos cosas.
- El uso del ordenador y los agentes de navegador avanzan más rápido que cualquier cosa escrita sobre ellos. Los papers de benchmarks listados cubren cómo evaluar uno, no la práctica actual para construirlo, así que la etapa 11 es la parte del arco con menos fuentes.
- Nada de lo listado cubre todavía la memoria de un agente entre ejecuciones como sistema diseñado y no como función de un producto. La etapa 6 necesita una.
