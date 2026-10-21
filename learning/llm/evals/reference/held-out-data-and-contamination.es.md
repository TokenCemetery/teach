---
title: "Datos held-out y contaminación"
description: "Disciplina de la partición entrenamiento/prueba para un conjunto de eval, las dos vías de contaminación, cómo detectar cada una y cómo diseñar un conjunto propio que las resista"
type: reference
---

# Datos held-out y contaminación

La etapa 1 comprimida para consulta. La [lección 1](../lessons/0001-held-out-and-contamination.md) cubre las dos vías de contaminación y la prueba de instrucción guiada para detectarlas; la [lección 2](../lessons/0002-designing-contamination-resistance.md) cubre cómo diseñar un conjunto de eval propio que resista la contaminación desde el principio. Esta hoja reúne lado a lado las definiciones, las vías y el kit de prevención.

## Qué exige "held-out"

Un conjunto de eval es held-out cuando el modelo evaluado nunca vio esos ejemplos exactos, ni paráfrasis cercanas de ellos, durante el entrenamiento o el fine-tuning. Esa única propiedad es la que permite que una buena puntuación signifique "esto generaliza" en lugar de "esto se memorizó". Antes de citar una puntuación como evidencia, responde: *¿por qué el modelo no pudo haber acertado esto por memorización o por haberse ajustado contra este mismo conjunto?* Si no hay respuesta, el número describe la eval, no el modelo.

## Dos vías de contaminación

| Vía | Qué ocurre | ¿Fuga literal? | Corrección |
|---|---|---|---|
| Absorción en el preentrenamiento | Un benchmark se rastrea hacia datos de entrenamiento de la web antes de que nadie construya una eval sobre él | Sí | Elegir o construir datos que sea poco probable que aparezcan en un corpus de preentrenamiento, o comprobar su presencia |
| Sobreajuste iterativo | El mismo conjunto de eval se ejecuta una y otra vez mientras se ajusta un modelo o un prompt, y moldea poco a poco el sistema para pasar esos ejemplos concretos | No | Renovar el conjunto, o reservar una porción intacta de él |

Ambas producen el mismo síntoma: un número que se ve bien y no predice el comportamiento en el mundo real. Las correcciones difieren porque difieren las causas; tratar una como sustituta de la otra deja abierta la vía sin tratar.

## Detectar la absorción en el preentrenamiento: la prueba de instrucción guiada

Dale al modelo la primera parte de una instancia de un benchmark y pídele completar el resto de forma literal. Reproducir detalles que una suposición plausible no recuperaría, una redacción exacta, un número poco habitual, un nombre propio raro, es una evidencia sólida de que esa instancia estaba en sus datos de entrenamiento (Golchin y Surdeanu, 2023). Esto solo prueba la absorción; no dice nada sobre el sobreajuste iterativo, que no deja tal rastro.

## Prevenir la contaminación al construir un conjunto propio

| Técnica | Qué hace | Cuándo aplica | Límites |
|---|---|---|---|
| Datos posteriores al corte de entrenamiento | Obtener los datos de eval de material creado después del corte de entrenamiento declarado del modelo | Requiere una fecha de corte exacta y verificada, no una afirmación de marketing | Protege solo contra la absorción; un conjunto de eval obsoleto sigue arriesgando el sobreajuste iterativo |
| Canary string (convención de BIG-bench) | Incrustar una frase marcadora única que pide a cualquier rastreador excluir el contenido marcado | Cualquier conjunto publicado | Una petición, no un mecanismo de cumplimiento; depende de la cooperación de los rastreadores |
| Comprobación de solapamiento de n-gramas | Medir el solapamiento directo entre los datos de eval y un corpus conocido | Solo cuando el corpus de preentrenamiento es conocido y accesible | Inutilizable para un modelo cerrado con datos de entrenamiento no divulgados |
| Mantener el conjunto sin publicar | No publicarlo nunca | Siempre disponible | La prevención más fuerte, a costa de la reproducibilidad y el escrutinio externo |

Las tres primeras dependen de algo (un corte exacto, la cooperación de los rastreadores, el acceso al corpus); mantener un conjunto privado es la única técnica sin precondición, por eso es la alternativa cuando las demás no aplican.

## Antes de confiar en una puntuación

- La historia de contaminación del conjunto de eval se declara, no se supone: qué vía se comprobó y cómo.
- Un benchmark público tomado prestado se ha probado con el método de instrucción guiada, o existe una razón documentada de por qué ese riesgo es bajo.
- Un conjunto de eval propio nombra qué técnica(s) de prevención le aplican, y sus límites se conocen, no solo su presencia.
- Un conjunto de eval reutilizado durante meses de ajuste se ha renovado, o existe una porción reservada que no se ha tocado.

## Fuentes

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [Recursos](../RESOURCES.md)
