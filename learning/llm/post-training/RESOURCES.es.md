---
title: "Recursos"
description: "Fuentes de confianza sobre el post-training de LLM"
type: resources
---

# Recursos del post-training de LLM

## Conocimiento

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
  El paper de InstructGPT. Define el pipeline de SFT, reward model y PPO que ha seguido la mayor parte del trabajo de RLHF posterior, y mide el impuesto de alineación frente a un modelo solo preentrenado. Úsalo para: las etapas 1, 2 y 3, y el planteamiento del impuesto de alineación de la etapa 9.
- [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
  Presenta PPO como un algoritmo general de aprendizaje por refuerzo, independiente de los modelos de lenguaje. Úsalo para: el algoritmo central de la etapa 4, y léelo antes de su aplicación específica a modelos de lenguaje.
- [Paper: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback", Bai et al., 2022](https://arxiv.org/abs/2204.05862)
  El relato de Anthropic de la misma receta de SFT a RLHF a escala de producción, incluido dónde aparecieron en la práctica el reward hacking y la sobreoptimización contra el reward model. Úsalo para: el material de reward hacking de la etapa 3 y el relato de la etapa 4 sobre qué sale realmente mal.
- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
  Deriva una recompensa en forma cerrada implícita en una policy y un modelo de referencia, y sustituye el reward model aparte y el bucle de RL por una única pérdida de estilo supervisado sobre pares de preferencia. Úsalo para: la derivación central de la etapa 5.
- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
  Presenta GRPO, que reemplaza la función de valor aprendida de PPO por un baseline relativo al grupo calculado a partir de varias completions muestreadas por prompt. Úsalo para: el algoritmo central de la etapa 6.
- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Entrena razonamiento chain-of-thought extendido principalmente mediante RL contra recompensas verificables, y describe cómo destilar el comportamiento resultante en modelos más pequeños. Úsalo para: la fuente principal de la etapa 7.
- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
  Reemplaza las preferencias de inocuidad etiquetadas por humanos por un modelo que critica y revisa sus propias salidas frente a un conjunto escrito de principios. Úsalo para: el caso central de la etapa 8 de feedback producido por un modelo y no por una persona.
- [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
  Una comparación directa y controlada de RLAIF frente a RLHF en las mismas tareas, que informa de dónde el feedback de IA iguala al feedback humano y dónde no. Úsalo para: la etapa 8, como complemento empírico del método de Constitutional AI.
- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
  Una receta de RLHF publicada a escala de modelo abierto, con detalles del entrenamiento del reward model y un proceso de RLHF iterativo a lo largo de varias rondas. Úsalo para: contrastar las etapas 3 y 4 con una receta completa y reproducible.
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
  La librería que ejecutan realmente los labs de SFT y DPO de este track, con configuración de ejemplo para cada trainer. Úsalo para: las prácticas con las manos en la masa de las etapas 2, 4 y 5.

## Lagunas

- Todavía no hay una fuente principal sobre la calidad de los datos de preferencia: el desacuerdo entre anotadores, las instrucciones de etiquetado y cómo las decisiones al recopilar datos de preferencia sesgan un reward model entrenado. Hace falta antes de que el material de calidad de datos de la etapa 3 pueda quedar bien fundamentado.
- La medición del impuesto de alineación más allá del propio informe de InstructGPT es escasa; un tratamiento más reciente y agnóstico del modelo reforzaría la etapa 9.
- Todavía no hay un relato de producción de una comparación completa de costos de DPO frente a PPO frente a GRPO desde la infraestructura de un solo equipo; la lección de criterio de la etapa 10 tiene por ahora que sintetizarla a partir de papers separados y no de una fuente que ya hiciera la comparación.
