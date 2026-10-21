---
title: "26. Por qué los agentes de navegador fallan de forma distinta"
description: "Los agentes que manejan la pantalla fallan de maneras en que no lo hacen los agentes que llaman herramientas, y por qué WebArena creó un benchmark para medir y estudiar esos fallos"
type: lesson
---

# Lección 26. Por qué los agentes de navegador fallan de forma distinta

**Vínculo con la misión:** Construir y diagnosticar agentes que manejan la pantalla exige entender que sus modos de fallo son estructurales, no solo una cuestión de mejores prompts, para que inviertas en estrategias de mitigación en lugar de retocar prompts.
**Fuente principal:** [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
**Requisitos previos:** [Lección 25](0025-grounding-an-action-to-a-coordinate.md)

## Calentamiento

1. ▢ De la lección 24: ¿Por qué un agente de uso del ordenador necesita trabajar con píxeles y capturas de pantalla en lugar de llamadas a herramientas con nombre?

<details markdown="1"><summary>Comprobación</summary>

Porque necesita operar cualquier aplicación con interfaz gráfica, incluidas las que nunca se construyeron pensando en una API o en una integración con agentes. Un agente de uso del ordenador interactúa a través de la pantalla como lo hace una persona, así que funciona en todas partes.

</details>

2. ▢ De la lección 25: Nombra una razón por la que una coordenada de píxel es una referencia más frágil que un argumento de llamada a herramienta.

<details markdown="1"><summary>Comprobación</summary>

Una coordenada se rompe cuando cambia el diseño (cambio de tamaño de la ventana, desplazamiento de la página, nivel de zoom), pero un argumento como un ID de usuario o el nombre de un registro persiste. Una coordenada también se rompe en silencio cuando cae en lo que no es, mientras que una llamada a herramienta recibe un error explícito.

</details>

## Qué debes saber

### Modos de fallo propios de los agentes que manejan la pantalla

Un agente que llama herramientas falla cuando llama a la herramienta equivocada, pasa argumentos incorrectos o se queda sin turnos. Un agente que maneja la pantalla (basado en navegador o de uso del ordenador) falla de todas esas maneras y también de maneras en que los agentes que llaman herramientas simplemente no pueden.

**Errores de grounding** (lección 25): La intención del modelo es correcta pero las coordenadas son erróneas, y el clic cae en el elemento equivocado o en espacio vacío. Un agente que llama herramientas no tiene este problema porque referencia las cosas por nombre.

**Obstáculos del entorno**: Una ventana emergente, un banner de cookies, un indicador de carga, un diálogo modal o un mensaje de error pueden bloquear la siguiente acción del agente. Un agente que llama herramientas quizá nunca se encuentre con esto porque una llamada a una API simplemente tiene éxito o falla con limpieza. Un agente que maneja la pantalla tiene que sortear los obstáculos antes de poder proceder con la tarea real.

**Complejidad de la verificación**: Cuando una llamada a herramienta termina, el harness recibe un resultado estructurado con un campo de estado. El harness sabe al instante si tuvo éxito. Cuando un agente de uso del ordenador hace clic en un botón, no pasa nada de inmediato salvo que la pantalla cambia. El harness tiene que tomar una captura de pantalla nueva, enviarla al modelo y hacer que el modelo razone si el clic en el botón funcionó. Este paso de interpretación es más lento y menos fiable que un código de estado estructurado.

**Variación del diseño**: La misma aplicación web se renderiza de forma distinta según el tamaño de pantalla, el navegador, el nivel de zoom, el framework de CSS y el estado del servidor. Un agente entrenado o probado en un escritorio con el zoom normal podría fallar en un teléfono móvil o con el zoom al 150 por ciento. Los cambios de diseño rompen las coordenadas y obligan a volver a anclar.

Estos fallos no se deben a un mal modelo ni a prompts insuficientes. Son consecuencias estructurales de observar y actuar a través de píxeles en lugar de APIs.

### Por qué importa WebArena

Durante años, los agentes de uso del ordenador se evaluaron con anécdotas: un proveedor mostraba un vídeo de un agente haciendo algo impresionante, pero no había una forma sistemática de medir si los agentes realmente mejoraban, ni dónde estaban los mayores problemas de fiabilidad. Distintos proveedores usaban distintos entornos, así que los resultados no eran comparables. Esto dificultaba separar el progreso real del marketing.

El paper de WebArena (Zhou et al., 2023) creó un entorno de benchmark estandarizado y autoalojado: un conjunto realista de sitios web y aplicaciones web montado en un servidor privado, con instrucciones de tareas y comprobaciones de corrección. El trabajo de un agente es completar tareas como reservar un vuelo, publicar una reseña o configurar un ajuste. Una tarea se considera exitosa solo si las acciones del agente producen el resultado correcto y verificable (un vuelo reservado, una reseña publicada).

WebArena hizo posibles tres cosas:

Primero, expuso la brecha real de fiabilidad. Los agentes que manejan la pantalla y que se veían impresionantes en los vídeos de marketing tenían tasas de éxito en el rango del 10 al 20 por ciento en tareas web realistas de varios pasos. Fue una llamada de atención: la tecnología era mucho menos fiable de lo que sugerían las anécdotas.

Segundo, permitió a los investigadores medir qué modos de fallo dominan. Al ejecutar muchas trayectorias de agentes y categorizar los fallos, los investigadores encontraron que los errores de grounding, los obstáculos del entorno y los cambios de diseño explicaban una gran fracción de los fallos, no los errores de lógica ni la falta de razonamiento. Esto orientó el esfuerzo hacia mitigaciones que de verdad ayudan.

Tercero, proporcionó un estándar compartido. Distintos equipos podían ejecutar sus agentes en el mismo benchmark y comparar resultados. El progreso pasó a ser medible en lugar de declarado.

### Mitigaciones e intercambios

Varias estrategias reducen los fallos de los agentes que manejan la pantalla, cada una con costos:

**Herramientas con conocimiento de la estructura** (mencionadas en la lección 25): En lugar de solo una captura de pantalla en bruto, la herramienta devuelve información estructurada sobre los elementos de la página (botones, campos de formulario, sus nombres y posiciones). El modelo referencia los elementos por nombre en lugar de por coordenadas. El harness traduce el nombre a coordenadas en el momento de la acción. Esto recupera fiabilidad porque el harness puede recalcular las coordenadas si cambia el diseño, sin pedirle al modelo que vuelva a estimar.

Intercambio: Pierdes la generalidad de "funciona en cualquier interfaz gráfica". Las herramientas con conocimiento de la estructura funcionan para páginas web con HTML semántico pero fallan en aplicaciones de escritorio, PDF, juegos o interfaces para las que la herramienta no fue diseñada.

**Interacción explícita con elementos**: En lugar de emitir coordenadas de píxel, el modelo emite una referencia como "haz clic en el elemento con id submit_button" o "rellena el campo con la etiqueta email". El harness usa las APIs del navegador (JavaScript, árboles de accesibilidad o inspección del DOM) para encontrar el elemento e interactuar con él.

Intercambio: El harness vuelve a ser específico de la aplicación. Tienes que construir herramientas para la plataforma que te importe (web, escritorio, móvil).

**Detección de obstáculos y recuperación**: El agente comprueba periódicamente si una ventana emergente o un banner está bloqueando la interfaz y toma medidas para cerrarlo o descartarlo antes de proceder.

Intercambio: Añade complejidad y latencia; requiere que el agente reconozca obstáculos de los que no se le habló de forma explícita.

**Verificación en varios pasos**: Después de cada acción, el agente toma una captura de pantalla y un turno de razonamiento adicional (que no cuenta contra los turnos de la tarea principal) para verificar que la acción tuvo el éxito previsto antes de seguir adelante.

Intercambio: Aumenta el uso de tokens y la latencia.

La idea clave es que ninguna mitigación por sí sola arregla todos los fallos. Cada una atiende uno o dos modos de fallo pero introduce nueva complejidad o pierde generalidad. Un sistema de producción a menudo combina varias.

### Cómo esto da forma al diagnóstico

Cuando un agente que maneja la pantalla falla, conocer estos modos de fallo da forma a cómo diagnosticas:

- Si la trayectoria muestra una secuencia de clics que tiene sentido pero cae en lugares equivocados, sospecha errores de grounding y variación del diseño.
- Si la trayectoria muestra al agente tomando una acción que debería haber funcionado pero la siguiente captura de pantalla no muestra cambios, busca obstáculos (ventanas emergentes, indicadores de carga) o verifica que la acción realmente se ejecutó.
- Si el agente funcionó en una máquina o nivel de zoom pero falló en otra tarea idéntica en una configuración distinta, sospecha un renderizado específico del entorno.
- Si el agente completa con éxito la misma tarea el 80 por ciento de las veces pero a veces falla en condiciones idénticas, sospecha de inestabilidad por el tiempo (un elemento dinámico que aún no cargó) o de una variante de diseño que no has visto.

Esta es la disciplina diagnóstica: conocer los modos de fallo probables te evita añadir prompts a ciegas y te orienta hacia el problema real.

## Práctica

1. ▢ Un agente completa con éxito una tarea en tu escritorio con el nivel de zoom normal. Cuando ejecutas el mismo agente en exactamente el mismo sitio web con el zoom del navegador al 125 por ciento, falla en el primer clic. ¿Cuál es el modo de fallo más probable?

<details markdown="1"><summary>Comprobación</summary>

Un error de grounding combinado con variación del diseño. Con el zoom normal, las coordenadas eran correctas. Con el zoom al 125 por ciento, el mismo elemento se renderizó en coordenadas distintas. El agente estimó las coordenadas según la apariencia visual en el nuevo nivel de zoom pero probablemente las estimó mal, o reutilizó coordenadas de una captura de pantalla en caché con el nivel de zoom antiguo. La solución no es un mejor razonamiento; es o bien una herramienta con conocimiento de la estructura que recalcule las coordenadas, o bien asegurarse de que el agente tome una captura de pantalla nueva con el nivel de zoom actual.

</details>

2. ▢ La trayectoria de un agente muestra que hizo clic en un botón con éxito en el turno tres. El botón ya no es visible en la captura de pantalla del turno cuatro; apareció un diálogo modal. En el turno cuatro, el agente intenta hacer clic en el mismo botón en las mismas coordenadas, y el clic cae en el modal. El agente entonces se queja de que no puede encontrar el botón. ¿Es el fallo un error de grounding?

<details markdown="1"><summary>Pista</summary>

El grounding en realidad fue correcto en el turno cuatro; las coordenadas seguían apuntando a donde estaba el botón antes. El problema no son las coordenadas en sí.

</details>

<details markdown="1"><summary>Comprobación</summary>

No, esto es un problema de obstáculo, no un error de grounding. El razonamiento del agente fue sólido: decidió que el botón debería seguir siendo clicable. El grounding fue preciso: las coordenadas apuntaban correctamente a la ubicación anterior del botón. Pero el entorno cambió (apareció un modal), y el agente no detectó ni manejó el obstáculo. La solución es la detección de obstáculos y la recuperación, no una mejor estimación de coordenadas.

</details>

3. ▢ Estás decidiendo si usar una herramienta de navegador con conocimiento de la estructura (que devuelve nombres y posiciones de elementos) o una herramienta de captura de pantalla en bruto para tu agente. Tu aplicación es un panel de JavaScript a medida con elementos renderizados de forma dinámica, sin estructura HTML semántica y con elementos que se mueven durante las interacciones. La documentación de la herramienta dice que las herramientas con conocimiento de la estructura funcionan mejor en "aplicaciones web semánticas y estándar". ¿Cuál deberías elegir?

    - a) La herramienta con conocimiento de la estructura, porque es más nueva y más sofisticada
    - b) La herramienta de captura de pantalla en bruto, porque tu aplicación no es HTML semántico
    - c) La herramienta con conocimiento de la estructura de todos modos, y complementarla con JavaScript a medida
    - d) Cualquiera de las dos es equivalente para agentes que manejan la pantalla

<details markdown="1"><summary>Comprobación</summary>

**b)** La herramienta de captura de pantalla en bruto es la mejor opción para una aplicación a medida, dinámica y no estándar. Las herramientas con conocimiento de la estructura dependen del HTML semántico y de IDs estables, que tu panel quizá no tenga. Una captura de pantalla en bruto deja que el modelo interprete visualmente la interfaz dinámica. El intercambio es la fragilidad del grounding, pero intentar usar herramientas con conocimiento de la estructura en una interfaz no admitida probablemente fallaría de todos modos. **a)** es incorrecta porque más nueva no significa mejor para tu caso de uso. **c)** añade complejidad; si la herramienta no admite bien tu interfaz, el complemento a medida puede no ayudar. **d)** es incorrecta porque las herramientas tienen modos de fallo distintos para distintos tipos de aplicaciones.

</details>

4. ▢ Ejecutas un agente en el benchmark de WebArena y tiene éxito en el 15 por ciento de las tareas. Mejoras el system prompt con instrucciones más claras y pistas de razonamiento. En una nueva prueba, tiene éxito en el 16 por ciento. ¿Qué te dice esta pequeña mejora sobre la causa probable de los fallos restantes?

<details markdown="1"><summary>Comprobación</summary>

Sugiere que la mayoría de los fallos no se deben al razonamiento ni a la claridad de las instrucciones. Las mejoras del prompting dieron ganancias mínimas. Es probable que los fallos sean estructurales: errores de grounding, variación del diseño, obstáculos, problemas de verificación u otros factores que unas mejores instrucciones por sí solas no pueden arreglar. Para mejorar más, tendrías que investigar qué modos de fallo dominan realmente (leyendo trayectorias) y luego aplicar mitigaciones dirigidas como herramientas con conocimiento de la estructura, detección de obstáculos o una mejor estimación de coordenadas.

</details>

## Prácticas en el mundo real

- [ ] Lee el resumen y la introducción del paper de WebArena (arxiv.org/abs/2307.13854). Lista las tres categorías de tareas que menciona y anota un ejemplo de un modo de fallo descrito en cada una.

- [ ] Toma la trayectoria de un agente de uso del ordenador o de navegador de una fuente pública (documentación, blog, GitHub). Categoriza cada fallo (si lo hay) como: error de grounding, obstáculo del entorno, fallo de verificación, variación del diseño o error de lógica. ¿Qué categoría aparece con más frecuencia?

- [ ] Mañana: Diseña un escenario de prueba que expondría errores de grounding en concreto. ¿Qué propiedades necesitaría la página web o interfaz de prueba? Luego diseña un escenario distinto que expondría fallos en el manejo de obstáculos. Escribe un párrafo que describa cómo medirías si un agente maneja bien los obstáculos.

## Para profundizar

- [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
