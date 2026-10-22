---
title: "Recursos"
description: "Fuentes de confianza sobre el preentrenamiento de LLM"
type: resources
---

# Recursos del preentrenamiento de LLM

## Conocimiento

- [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
  Ajusta las relaciones originales de ley de potencias entre la loss, el cómputo, el número de parámetros y los datos, y defiende escalar los parámetros más rápido que los datos. Úsalo para: la etapa 3, como la línea base que Chinchilla revisa después.
- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
  El paper de Chinchilla. Reajusta las leyes de escalado con un barrido más amplio y concluye que los parámetros y los tokens deben escalar juntos, a unos veinte tokens por parámetro, lo que revoca la recomendación de Kaplan, cargada hacia los parámetros. Úsalo para: el resultado central de la etapa 3, y el presupuesto de tokens que de hecho usan la mayoría de las ejecuciones de entrenamiento modernas.
- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
  Define las tres etapas de ZeRO, que reparten el estado del optimizador, luego los gradientes y luego los parámetros entre dispositivos con data parallelism. Úsalo para: la técnica central de la etapa 5, que FSDP implementa.
- [Documentation: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  La referencia de la API del reparto al estilo de la etapa 3 de ZeRO en PyTorch, incluidas las estrategias de reparto y las políticas de envoltura que ejecuta realmente el laboratorio de una lección. Úsalo para: las prácticas manuales de la etapa 5.
- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
  Combina tensor parallelism, pipeline parallelism y data parallelism en un solo sistema, con las disyuntivas de rendimiento y de memoria de cada uno medidas frente a las de los demás. Úsalo para: la técnica central de la etapa 6 y sus números resueltos.
- [Documentation: "DeepSpeed", Microsoft](https://github.com/microsoft/DeepSpeed)
  Una segunda implementación de producción de ZeRO junto con el paralelismo 3D, con ejemplos de configuración a los que una lección puede apuntar como segundo sistema concreto junto a FSDP y Megatron-LM. Úsalo para: las etapas 5 y 6, como contraste para verificar que una afirmación trata de la técnica y no de la API de una biblioteca.
- [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
  Un corpus de preentrenamiento totalmente documentado: qué fuentes entraron, en qué proporciones y por qué. Úsalo para: la etapa 1, como ejemplo resuelto de una decisión de mezcla de datos hecha explícita.
- [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
  Muestra que el texto casi duplicado y las subcadenas largas repetidas causan memorización literal, y da dos técnicas de deduplicación (coincidencia exacta de subcadenas mediante un suffix array y coincidencia de casi duplicados mediante MinHash), cada una medida sobre un corpus real. Úsalo para: el material de deduplicación de la etapa 1, con cifras concretas de antes y después.
- [Paper: "Language Models are Few-Shot Learners", Brown et al., 2020](https://arxiv.org/abs/2005.14165)
  El paper de GPT-3. El apéndice A documenta un pipeline concreto de filtrado de calidad: un clasificador entrenado para distinguir texto curado de Common Crawl en bruto, usado para remuestrearlo hacia los documentos con mayor puntuación, junto con una pasada aparte de deduplicación difusa. Úsalo para: el material de filtrado de calidad de la etapa 1, como el ejemplo resuelto que el paper de deduplicación anterior no ofrece por sí mismo.
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
  Introduce el byte-pair encoding para la tokenización en subpalabras, el algoritmo sobre el que aún se construyen la mayoría de los tokenizers modernos. Úsalo para: el algoritmo central de la etapa 2.
- [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
  Trata la tokenización como una operación directa sobre texto en bruto, sin un paso de pretokenización específico de cada idioma, y cubre la tokenización con un modelo de lenguaje unigram como alternativa a BPE. Úsalo para: el segundo algoritmo de la etapa 2 y la disyuntiva del tamaño del vocabulario.
- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
  Un relato detallado y honesto de una ejecución de entrenamiento grande, que incluye dónde aparecieron los loss spikes y la inestabilidad y qué hicieron los autores al respecto. Úsalo para: el caso de estudio central de la etapa 7.
- [Paper: "LLaMA: Open and Efficient Foundation Language Models", Touvron et al., 2023](https://arxiv.org/abs/2302.13971)
  Una receta de entrenamiento publicada y reproducible: mezcla de datos, tokenizer, programa e hiperparámetros, expuestos con la claridad suficiente para contrastar con ellos las afirmaciones de una lección. Úsalo para: contrastar las etapas 1 a 3 y 7 con una receta real y completa.
- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
  Publicado junto con un logbook público de los problemas de infraestructura que los autores sufrieron de verdad al entrenar un modelo de 175B: fallas de hardware, reinicios manuales y automáticos, divergencias de la loss y el procedimiento concreto de recuperación usado en cada caso. Úsalo para: el caso de estudio central de la etapa 8, y un segundo ejemplo real del patrón de divergencia de la loss que cubre la etapa 7.
- [Paper: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
  Muestra que continuar el preentrenamiento sobre un modelo existente de cobertura amplia (preentrenamiento adaptativo al dominio) mejora de forma consistente el rendimiento en el dominio objetivo en cuatro dominios y ocho tareas, tanto con muchos como con pocos recursos, sin entrenar un modelo nuevo desde cero. Úsalo para: el argumento central de la etapa 10 de que preentrenar desde cero suele ser la opción por defecto equivocada.

## Lagunas

- El paper de OPT documenta la frecuencia real de fallas y el procedimiento de recuperación, pero no enuncia una política concreta de intervalo entre checkpoints (cada cuánto se guardaron realmente). La disyuntiva de la frecuencia de checkpoints de la etapa 8 se enseña a partir de razonamiento general de ingeniería y no de una política declarada; una fuente primaria con un intervalo concreto la reforzaría.
- El filtrado basado en clasificador de GPT-3 (2020) es el único ejemplo resuelto de filtrado de calidad listado hasta ahora. Los corpus construidos desde 2023 (FineWeb, Dolma) filtran con mucha más agresividad y lo documentan con más profundidad; una fuente primaria más reciente reforzaría la etapa 1.
