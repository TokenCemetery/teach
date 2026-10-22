---
title: Glosario
description: "Términos canónicos de los agentes con LLM"
type: glossary
---

# Glosario de agentes con LLM

Términos canónicos para construir agentes: de qué está hecho el bucle y cómo llamar a cada parte en un campo que usa de forma habitual cuatro palabras para una misma cosa.

## Términos

**Memoria entre ejecuciones**:
Hechos guardados fuera de cualquier trayectoria individual y cargados de forma deliberada en el contexto inicial de una nueva ejecución, porque una ejecución nueva empieza con una transcripción vacía.
_Evitar_: scratchpad (son dos mecanismos distintos y confundirlos es el error más común aquí), estado (demasiado genérico)

**Agente**:
Un sistema que ejecuta un modelo de lenguaje en un bucle con herramientas, y deja que el modelo decida qué herramienta llamar, cuándo y cuándo parar, en lugar de seguir un camino que el desarrollador fijó de antemano.
_Evitar_: asistente, bot, copiloto (palabras de producto que no dicen nada sobre si el flujo de control es fijo o lo decide el modelo)

**Bucle del agente**:
El ciclo que repite un agente en ejecución: enviar la transcripción al modelo, ejecutar la llamada a herramienta que vuelva, añadir el resultado a la transcripción y repetir hasta que se cumpla una condición de parada.
_Evitar_: cadena, pipeline (ambos nombran una secuencia fija, que es exactamente lo que un bucle del agente no es)

**Puerta de aprobación**:
Un punto de control a nivel de harness que pausa el bucle antes de ejecutar una llamada de una categoría riesgosa hasta que una persona la aprueba o la rechaza.
_Evitar_: human-in-the-loop (demasiado amplio; la puerta de aprobación nombra este mecanismo concreto)

**Espectro de autonomía**:
El rango que va de un solo prompt, pasando por un flujo de trabajo fijado por el desarrollador, hasta un agente dirigido por el modelo, ordenado según cuánto del flujo de control elige el modelo en tiempo de ejecución en lugar de que lo elija un desarrollador de antemano.
_Evitar_: "qué tan agéntico" es algo (trata la autonomía como una cantidad difusa y única en lugar de una pregunta sobre el flujo de control con una respuesta comprobable)

**Herramienta de cliente**:
Una herramienta cuya implementación corre en el propio código del harness, de modo que el harness la ejecuta directamente cuando el modelo la solicita.
_Evitar_: herramienta local, herramienta personalizada

**Compactación**:
Reemplazar un tramo de transcripción antigua por un resumen condensado sobre el que el modelo todavía puede actuar, a cambio de perder algo de información y reducir el contexto residente.
_Evitar_: resumen (demasiado genérico; la compactación apunta específicamente a la transcripción del propio agente, no a texto arbitrario)

**Delegado confundido**:
Un componente con autoridad legítima al que, mediante contenido no confiable, se engaña para que use mal esa autoridad en favor de un atacante, sin que el componente en sí esté comprometido.
_Evitar_: "hackearon al modelo" (no se comprometió nada; la herramienta hizo exactamente lo que se construyó para permitir)

**Envenenamiento del contexto**:
Una afirmación sin respaldo o falsa que entra en la transcripción y que luego todos los turnos siguientes tratan en silencio como un hecho establecido.
_Evitar_: alucinación (demasiado amplio; esto nombra específicamente una afirmación que entró y persiste en la transcripción, no cualquier salida errónea aislada)

**Degradación del contexto (context rot)**:
La atención y la precisión del modelo se deterioran a medida que se acumula contenido de poca relevancia en el contexto, incluso cuando no se ha truncado ninguna información necesaria.
_Evitar_: "el contexto está lleno" (confunde un límite estricto de tokens con un problema de precisión más suave que empieza mucho antes del límite)

**Costo por tarea completada**:
El costo en tokens de cada intento, reintento y worker que una tarea realmente necesitó para tener éxito, no solo el costo de la última llamada exitosa.
_Evitar_: costo por llamada a la API (subestima una tarea que necesitó más de un intento para tener éxito)

**Fan-out**:
Un orquestador que lanza varios workers a la vez sobre variaciones del mismo problema, a cambio de gastar más tokens para ganar tiempo real en paralelo.
_Evitar_: paralelismo (demasiado genérico; el fan-out es la forma multiagente concreta que lo produce aquí)

**Grounding**:
Traducir la intención del modelo a una coordenada de pantalla o a un objetivo concreto en pantalla, un paso que puede fallar por sí solo incluso cuando la decisión de fondo del modelo era correcta.
_Evitar_: precisión del clic (demasiado estrecho; el grounding abarca cualquier correspondencia de observación a acción, no solo hacer clic)

**Traspaso**:
Un agente que termina su parte de una tarea y entrega un contexto limpio y acotado, no su trayectoria completa, a un segundo agente especializado para la fase siguiente.
_Evitar_: fan-out (el traspaso es secuencial, el fan-out es paralelo, mira el contraste en esa lección)

**Harness**:
El código que rodea al modelo, que guarda la transcripción, ejecuta las llamadas a herramientas, aplica los límites y decide cuándo termina el bucle. El modelo elige; el harness actúa.
_Evitar_: runtime, framework (un framework es un posible harness, no el concepto)

**Mínimo privilegio**:
Limitar cada herramienta solo al acceso que realmente necesita, en lugar de un acceso amplio concedido "por si acaso".
_Evitar_: sandboxing (un sandbox hace cumplir un límite; el mínimo privilegio es el principio de diseño que decide qué tan estrecho debe ser ese límite)

**Tríada letal**:
La combinación de acceso a datos privados, exposición a contenido no confiable y capacidad de comunicarse con el exterior que, juntos, hacen explotable a un agente. Quitar cualquiera de los tres rompe el ataque.
_Evitar_: "riesgo de seguridad" (demasiado vago para actuar sobre él; la tríada nombra las tres condiciones concretas que hay que revisar)

**Orquestador**:
El agente de un sistema multiagente que descompone una tarea, asigna subtareas a los workers y sintetiza sus informes; no hace por sí mismo el trabajo de la subtarea.
_Evitar_: gerente, coordinador (términos genéricos que no distinguen este rol de un worker)

**Inyección de prompt**:
Contenido que lee un agente y que incluye instrucciones diseñadas para secuestrar su comportamiento, aprovechando que el modelo no puede distinguir de forma estructural los datos de las instrucciones.
_Evitar_: jailbreak (un jailbreak apunta directamente al entrenamiento de rechazo del propio modelo; la inyección esconde instrucciones dentro del contenido que se le pidió procesar al agente)

**ReAct**:
El patrón de intercalar un breve paso de razonamiento con cada acción, de modo que el razonamiento de cada paso pueda reaccionar al resultado real del paso anterior.
_Evitar_: chain-of-thought (nombra solo el texto de razonamiento; ReAct lo intercala específicamente con acciones de herramientas y sus resultados observados)

**Reflexión**:
Una etapa explícita en la que el agente evalúa un intento fallido en lenguaje natural y lleva esa evaluación al intento siguiente, a diferencia de un simple reintento con el mismo contexto.
_Evitar_: autocorrección (se usa con poca precisión para cualquier cosa que haga un modelo internamente; la reflexión nombra la versión externa, almacenada y arrastrada hacia delante)

**Recuperación bajo demanda**:
Mantener residente en el contexto solo un resumen o una referencia, y traer de vuelta el detalle completo con una llamada a herramienta solo cuando el modelo realmente lo necesita.
_Evitar_: RAG (RAG recupera de un corpus externo; esto recupera detalle que el agente ya produjo o al que tiene acceso directo)

**Sandbox**:
El límite de ejecución que el harness impone sobre lo que el código de una herramienta puede alcanzar (sistema de archivos, red, recursos), sin importar lo que pidió el modelo.
_Evitar_: permiso (un permiso es lo que concedes; un sandbox es el mecanismo que hace cumplir la concesión incluso frente a una llamada malformada o adversaria)

**Scratchpad**:
Notas que un agente escribe y vuelve a leer dentro de una sola ejecución. En realidad es solo parte de la transcripción, y desaparece cuando termina la ejecución.
_Evitar_: memoria (un scratchpad no sobrevive más allá de la ejecución en la que se escribió)

**Herramienta de servidor**:
Una herramienta que un proveedor ejecuta en su propia infraestructura por cuenta del harness, como una búsqueda web alojada o una ejecución de código en un sandbox. El harness nunca ejecuta su implementación, solo lee el resultado de la respuesta del proveedor.
_Evitar_: herramienta alojada, herramienta integrada

**Subagente**:
Una ejecución de agente separada, con su propia transcripción y su propio harness, lanzada para hacer un trabajo acotado cuyo único efecto sobre el contexto del padre es el resumen que reporta.
_Evitar_: worker fuera de un sistema orquestador-worker (worker nombra a un subagente al que un orquestador le da una tarea acotada; el mecanismo es el mismo, el término señala el rol)

**Amplificación de tokens**:
Cuántos más tokens cuesta una tarea como bucle agéntico que como un solo prompt, por el recrecimiento de la transcripción, la duplicación entre varios agentes y los reintentos que se acumulan juntos.
_Evitar_: "los agentes son caros" (demasiado vago; la amplificación nombra el multiplicador concreto y de dónde viene cada parte)

**Herramienta**:
Una capacidad que se ofrece al modelo como un nombre, una descripción y un esquema de parámetros, que el modelo puede pedir y que el harness ejecuta en su nombre.
_Evitar_: llamada a función (nombra el mensaje que emite el modelo, no la capacidad), plugin, skill

**Traza**:
Un registro estructurado y con marcas de tiempo de una ejecución de agente, hecho de spans y que usa convenciones neutrales respecto a los proveedores, de modo que la traza de una herramienta se pueda leer en otra.
_Evitar_: log (un log sin estructura es lo que reemplaza una traza; una traza tiene un esquema definido que una herramienta puede consultar)

**Trayectoria**:
El registro completo y ordenado de una ejecución de agente: cada turno del modelo, llamada a herramienta, resultado de herramienta y decisión de parada. Es lo que se lee al diagnosticar un fallo, en lugar de mirar solo la respuesta final.
_Evitar_: transcripción (la lista de mensajes que el modelo realmente ve, que omite las decisiones del propio harness), historial, log

**Worker**:
Un subagente al que un orquestador le da una subtarea acotada, que corre su propio bucle y su propia transcripción aislados de los demás workers.
_Evitar_: subagente para el rol de orquestación (subagente nombra el mecanismo; worker nombra este rol concreto dentro de él)

**Flujo de trabajo**:
Un sistema en el que un desarrollador fijó de antemano la secuencia de llamadas al modelo y de llamadas a herramientas. Puede tener ramas y bucles, pero el modelo no elige el camino.
_Evitar_: agente (la distinción entre ambos es el punto de la etapa 1), cadena
