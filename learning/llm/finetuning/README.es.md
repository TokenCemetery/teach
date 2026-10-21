---
title: "Fine-tuning con adapters"
description: "Decide si hacer fine-tuning, ejecútalo, demuestra que funcionó y despliégalo"
type: topic
---

# Aprendizaje: fine-tuning con adapters (LoRA, QLoRA, DoRA)

Sé la persona capaz de tomar un base model y una tarea, decidir si el fine-tuning con adapters es siquiera la respuesta correcta, ejecutarlo, demostrar que funcionó con una eval que detectaría una regresión y desplegarlo, y capaz de argumentar de forma convincente a favor del prompting o de la recuperación cuando esas opciones harían mejor el trabajo.

**Empieza aquí:** [0001. Qué es realmente un base model](lessons/0001-what-a-base-model-is.md)
**Última lección:** [0027. Cuándo no hacer fine-tuning](lessons/0027-when-not-to-fine-tune.md)

## Cómo se ve el éxito

- Derivar el costo de memoria del full fine-tuning frente a LoRA para un modelo dado y dar cuenta de cada byte.
- Elegir rank, alpha, target modules y learning rate para una tarea nueva y justificar cada uno a partir de la tarea y no de los valores por defecto de una entrada de blog.
- Entrenar adapters LoRA, QLoRA y DoRA sobre la misma tarea y explicar las diferencias medidas, no las anunciadas.
- Construir una eval que detecte una regresión antes de desplegar, en lugar de leer una curva de pérdida y esperar lo mejor.
- Servir un adapter a través de un stack de inferencia y medir lo que costó en calidad y en latencia.
- Diagnosticar una ejecución fallida y nombrar la causa: sobreajuste, olvido catastrófico, chat template equivocado, desajuste del tokenizer, target modules equivocados.
- Leer un paper nuevo de PEFT y juzgar si la victoria que afirma sobreviviría en tu propia tarea.

## Restricciones

- Se asume que no hay experiencia previa en aprendizaje automático. La multiplicación de matrices es la única matemática que se da por sabida; todo lo que está por encima se enseña donde hace falta.
- El entrenamiento de adapters sobre un base model de la clase de 1B a 3B cabe en unos 16 GB de memoria de acelerador o unificada, lo que deja todo el arco al alcance de hardware corriente de un solo dispositivo.
- El soporte de los backends es desigual, no exclusivo. CUDA sigue siendo el camino más completo y mejor optimizado, y es donde los números publicados se reproducen con más fiabilidad; los demás backends funcionan con una cobertura de kernels variable y pasos más lentos. Todos los conceptos se transfieren sin cambios; solo difieren la velocidad y la disponibilidad de kernels.
- Las prácticas son de latencia larga: una ejecución de entrenamiento toma de minutos a horas, así que las sesiones se agrupan en lugar de caber en una tarde, con lectura entre medias.
- Las herramientas avanzan más rápido que cualquier libro. Las API de las bibliotecas se leen en la documentación de la versión instalada, nunca se recuerdan de memoria.
- Nada del arco requiere infraestructura de pago, aunque alquilar un acelerador más grande hará más rápidas algunas comparaciones.

## Fuera de alcance

- El full fine-tuning a escala, el preentrenamiento y entrenar un modelo desde cero: consulta [`llm/pretraining`](../../llm/pretraining/).
- RLHF, DPO y la optimización de preferencias: consulta [`llm/post-training`](../../llm/post-training/). Este tema es dueño de cómo se aplica un cambio a menos parámetros; aquel es dueño del objetivo de entrenamiento.
- La cuantización como tema por derecho propio: consulta [`llm/quantization`](../../llm/quantization/). La etapa 4 de aquí conserva la porción que necesita QLoRA y enlaza allí para la teoría general; esa frontera quedó fijada al escribir el tema de cuantización. La cuantización en el momento de servir se cubre en [`llm/inference`](../../llm/inference/).
- La destilación como tema por derecho propio: consulta [`llm/distillation`](../../llm/distillation/). Este tema es dueño de cómo se aplica una ejecución de entrenamiento a menos parámetros; aquel es dueño del objetivo y de los datos de la destilación.
- Construir infraestructura de serving, más allá de ejecutar un adapter a través de un stack existente: consulta [`llm/inference`](../../llm/inference/).

## El arco

Siete etapas, de cero a senior. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. La planta baja | 0001 a 0004 | Qué calcula un forward pass, dónde viven las matrices de pesos, tokenizers, chat templates, qué cambia el entrenamiento | Puedes señalar qué tensores tocaría un adapter y por qué |
| 2. El argumento de la memoria | 0005 a 0007 | Parámetros frente a gradientes frente a estado del optimizador, los dos momentos de AdamW, memoria de activaciones, gradient checkpointing | Puedes calcular, en bytes, por qué el full fine-tuning falla en un dispositivo dado |
| 3. LoRA | 0008 a 0013 | `ΔW = BA`, rank, alpha y escalado, inicialización, elección de target modules, ejecutarlo, leer la ejecución, fusionar | Entrenas un adapter y puedes defender cada hiperparámetro |
| 4. Cuantización y QLoRA | 0014 a 0017 | int8/int4, NF4, doble cuantización, backprop a través de un base cuantizado y congelado, qué se degrada | Has ejecutado NF4 de verdad y sabes decir qué costó en calidad |
| 5. DoRA y el panorama de variantes | 0018 a 0020 | Descomposición en magnitud y dirección, por qué ayuda más con rank bajo, cómo evaluar la afirmación de una variante nueva | Puedes predecir cuándo DoRA supera a LoRA antes de ejecutar |
| 6. Datos y evaluación | 0021 a 0024 | Construcción del dataset, contaminación, diseño held-out, métricas de la tarea frente a la pérdida, conjuntos de regresión | Tienes una eval que ha detectado de verdad una regresión |
| 7. Operar y juzgar | 0025 a 0027 | Servir adapters frente a fusionados, serving multi-adapter, costo y latencia, cuándo *no* hacer fine-tuning | Se confía en ti para decidir si una tarea debe someterse a fine-tuning |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-a-base-model-is.md) | Qué es realmente un base model | El modelo es una única función de siguiente token; base no es instruct |
| [0002](lessons/0002-where-the-weights-live.md) | Dónde viven los pesos | Nombrar cada proyección a la que podría acoplarse un adapter |
| [0003](lessons/0003-tokenizers-and-chat-templates.md) | Tokenizers y chat templates | Entrena con el renderizado que vas a servir |
| [0004](lessons/0004-what-training-changes.md) | Qué cambia realmente el entrenamiento | Las cuatro operaciones de un paso de entrenamiento |
| [0005](lessons/0005-counting-parameters-and-bytes.md) | Contar parámetros y bytes | Convertir la configuración de un modelo en gigabytes |
| [0006](lessons/0006-gradients-and-optimizer-state.md) | Gradientes y estado del optimizador | Dieciséis bytes por parámetro entrenable, dos por uno congelado |
| [0007](lessons/0007-activations-and-checkpointing.md) | Activaciones, batch size y checkpointing | Por qué una ejecución con un adapter aún se queda sin memoria |
| [0008](lessons/0008-the-low-rank-idea.md) | La idea de bajo rank | `ΔW = BA`, y contar un adapter |
| [0009](lessons/0009-rank-alpha-and-initialisation.md) | Rank, alpha e inicialización | Solo importa `α/r`, y por qué `B` empieza en cero |
| [0010](lessons/0010-choosing-target-modules.md) | Elegir los target modules | Solo atención es una ablación de 2021, no un valor por defecto |
| [0011](lessons/0011-your-first-adapter.md) | Tu primer adapter | Una ejecución que prueba el pipeline antes de probar cualquier otra cosa |
| [0012](lessons/0012-reading-a-training-run.md) | Leer una ejecución de entrenamiento | Diagnosticar por la forma de la curva, y lo que la pérdida no puede ver |
| [0013](lessons/0013-merging-and-shipping.md) | Fusionar, guardar y distribuir un adapter | Lo fusionado es exacto; un adapter es un diff que necesita su base |
| [0014](lessons/0014-quantisation-from-first-principles.md) | Cuantización desde los primeros principios | Escalas por bloques, y por qué un solo outlier arruina un tensor |
| [0015](lessons/0015-nf4-and-double-quantisation.md) | NF4 y doble cuantización | Las dos ideas que QLoRA aportó de verdad |
| [0016](lessons/0016-training-through-a-quantized-base.md) | Entrenar a través de un base cuantizado | Cómo fluyen los gradientes a través de pesos congelados de 4 bits |
| [0017](lessons/0017-what-qlora-costs.md) | Lo que realmente cuesta QLoRA | Separar la degradación del base de la degradación del entrenamiento |
| [0018](lessons/0018-dora-magnitude-and-direction.md) | DoRA: magnitud y dirección | La renormalización desacopla ambas, y eso es el método |
| [0019](lessons/0019-when-dora-wins.md) | Cuándo gana DoRA y cuándo no | Predecir la victoria antes de ejecutar |
| [0020](lessons/0020-judging-a-new-variant.md) | Juzgar una variante nueva de PEFT | Seis preguntas de triaje, y el baseline que hay que superar |
| [0021](lessons/0021-building-the-dataset.md) | Construir el dataset | Los datos superan a cualquier hiperparámetro de este espacio de trabajo |
| [0022](lessons/0022-contamination-and-held-out-design.md) | Contaminación y diseño held-out | Dividir por la clave correcta y dimensionar para la pregunta |
| [0023](lessons/0023-metrics-that-mean-something.md) | Métricas que significan algo | La pérdida selecciona checkpoints; las métricas de la tarea toman decisiones |
| [0024](lessons/0024-the-regression-suite.md) | El conjunto de regresión | Detectar el daño que esconden todos los demás números |
| [0025](lessons/0025-serving-adapters.md) | Servir adapters | Fusiona para una tarea, enruta para muchas |
| [0026](lessons/0026-cost-latency-and-throughput.md) | Costo, latencia y throughput | Prefill frente a decode, y adónde va realmente el dinero |
| [0027](lessons/0027-when-not-to-fine-tune.md) | Cuándo no hacer fine-tuning | El fine-tuning es el sexto de la lista, y por qué eso importa |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes y comunidades de confianza
- [Presupuesto de memoria](reference/memory-budget.md): contabilidad de bytes, y qué probar cuando una ejecución no cabe
- [Hiperparámetros de LoRA](reference/lora-hyperparameters.md): rank, alpha, targets, learning rate, variantes
- [Modos de fallo](reference/failure-modes.md): del síntoma a la causa, y los fallos silenciosos

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
