---
title: "24. Capturas de pantalla como observaciones"
description: "Cómo los agentes de uso del ordenador observan la pantalla como una imagen en lugar de datos estructurados, y por qué la estructura del bucle se mantiene"
type: lesson
---

# Lección 24. Capturas de pantalla como observaciones

**Vínculo con la misión:** Diagnosticar a partir de su trayectoria un agente de uso del ordenador que falla exige entender que sus observaciones son visuales, no estructuradas, de modo que un error de grounding no se parece en nada a un argumento de herramienta omitido.
**Fuente principal:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Requisitos previos:** [Lección 23](0023-code-execution-as-a-tool.md), [Bucle del agente](../GLOSSARY.md)

## Calentamiento

1. ▢ En lecciones anteriores, cuando el agente llama a una herramienta y recibe un resultado, ¿qué forma tiene ese resultado? ¿Es siempre estructurado (JSON o un esquema), siempre texto sin estructura, o cualquiera de los dos?

<details markdown="1"><summary>Comprobación</summary>

Estructurado, en todos los formatos de transmisión que ha cubierto este track. Un resultado de herramienta siempre está etiquetado con el id de la llamada a la que responde, y siempre lleva o bien la salida de la herramienta o bien un error, aunque los nombres exactos de los campos y la forma varíen según el proveedor y el harness (ver lección 3). El modelo nunca tiene que interpretar visualmente un resultado de herramienta como lo hace con una captura de pantalla.

</details>

2. ▢ De la lección 6: ¿Cuáles son los cuatro pasos centrales del bucle del agente, en orden?

<details markdown="1"><summary>Comprobación</summary>

Llamar al modelo, añadir la respuesta a la transcripción, comprobar si hemos terminado, y si no, ejecutar las herramientas y añadir sus resultados, y volver al principio.

</details>

## Qué debes saber

### La observación cambia de tipo

En lecciones anteriores, la observación de un agente que llama herramientas después de cada acción es un resultado estructurado que construye el harness: un objeto JSON con campos como `tool_id`, `status` y `value`. La observación de un agente de uso del ordenador es radicalmente distinta. Después de que el agente realiza una acción en pantalla (clic, escribir, desplazarse), la observación es una captura de pantalla: literalmente una imagen, en formato PNG o JPEG, de lo que se muestra en la pantalla en ese momento.

El modelo tiene que interpretar visualmente esta imagen para entender qué pasó, en lugar de leer un campo de datos estructurado. Este es un cambio profundo en cómo el agente entiende el mundo.

La forma general del bucle de la lección 6 sobrevive sin cambios: enviar la transcripción, recibir la respuesta, ejecutar la acción, añadir el resultado, repetir. Pero ahora "añadir el resultado" significa añadir una imagen a la transcripción, y "recibir la respuesta" significa que el modelo genera una descripción de lo que ve en esa imagen y decide qué hacer a continuación.

### Por qué importa: generalidad

La razón de este diseño es el poder. En lecciones anteriores, un agente que llama herramientas solo puede llamar a las herramientas que el desarrollador construyó de forma explícita para él. Si quieres que un agente interactúe con una aplicación que no tiene API, tienes que escribir una herramienta que envuelva la API de esa aplicación. Pero ¿y si la aplicación no tiene API en absoluto? ¿Y si es solo una interfaz gráfica?

Un agente de uso del ordenador esquiva este problema. En lugar de necesitar una API o una herramienta a medida para cada aplicación, el agente interactúa a través de la pantalla, como lo haría una persona. El espacio de acciones es fijo y genérico: mover el ratón, hacer clic, escribir texto, pulsar teclas, desplazarse, tomar una captura de pantalla. Estas mismas acciones funcionan en cualquier aplicación gráfica de cualquier sistema operativo, desde un navegador web hasta una aplicación de escritorio o una consola en la nube. El modelo aprende a hacer cosas de pantalla, no cosas específicas de cada aplicación.

Esta es la ganancia: un agente que puede operar literalmente cualquier interfaz, incluso las construidas sin pensar en una integración con agentes.

### El bucle se mantiene

Como la estructura del bucle es conceptualmente independiente del tipo de observación, el ciclo básico sobrevive:

1. Enviar la transcripción (que ahora incluye la captura de pantalla actual) al modelo.
2. El modelo mira la captura de pantalla, entiende qué hay en pantalla y decide qué hacer a continuación.
3. El modelo emite una acción: hacer clic en las coordenadas (x, y), escribir la cadena "hello", desplazarse hacia abajo o tomar otra captura de pantalla.
4. El harness ejecuta la acción.
5. Si la acción fue una captura de pantalla, el harness añade la nueva imagen a la transcripción.
6. Volver al paso 1.

El modelo sigue decidiendo cuándo parar, el harness sigue imponiendo límites y terminando el bucle, la transcripción sigue creciendo en cada turno, y las condiciones de parada de la lección 6 (no más acciones, máximo de turnos, umbral de errores) siguen aplicándose. Lo único que cambió es el tipo de dato de la observación: de un objeto JSON a una imagen.

### Retos que introduce la observación visual

Esta generalidad tiene un costo. Un resultado de herramienta estructurado es inequívoco: lo construyó el harness, tiene un esquema fijo y el modelo puede leer los campos por nombre. Una captura de pantalla es ambigua: el modelo tiene que ubicar visualmente lo que quiere (un botón, un campo de texto, un elemento de menú) en la imagen actual, interpretar su ubicación y decidir qué acción tomar.

En la lección 25 verás cómo esta ambigüedad se cristaliza en un problema concreto llamado grounding. Por ahora, sé consciente de que existe este intercambio: los agentes de uso del ordenador pueden hacer cosas que los agentes que llaman herramientas no pueden, porque pueden operar cualquier interfaz gráfica, pero la observación requiere interpretación visual, lo que introduce nuevos modos de fallo que las observaciones estructuradas no tienen.

## Práctica

1. ▢ Estás construyendo un agente de uso del ordenador para interactuar con una aplicación web. Tu colega sugiere añadir una herramienta llamada `click_button` que toma el nombre de un botón como argumento de cadena, para que el agente pueda escribir `click_button("Submit")` en lugar de tener que lidiar con coordenadas. ¿Es una buena idea? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No lo es. Todo el sentido de un agente de uso del ordenador es que funciona con cualquier interfaz gráfica sin herramientas a medida. Si añades herramientas específicas de la tarea como `click_button`, estás superponiendo una interfaz tradicional de llamadas a herramientas, lo que anula el propósito. El modelo debería aprender a realizar acciones genéricas (hacer clic en coordenadas, escribir) e interpretar visualmente la captura de pantalla. Añadir herramientas envoltorio añade acoplamiento y reduce la generalidad del agente.

</details>

2. ▢ Un agente de uso del ordenador toma una captura de pantalla, ve un formulario de inicio de sesión y escribe su nombre de usuario en el campo de contraseña en lugar del campo de usuario. ¿Es un error del modelo, del harness o del propio espacio de acciones?

<details markdown="1"><summary>Pista</summary>

El modelo decidió escribir el nombre de usuario. El harness ejecutó la acción. Algo salió mal al conectar la decisión con la parte correcta de la pantalla.

</details>

<details markdown="1"><summary>Comprobación</summary>

Es un error de interpretación visual: el modelo vio el formulario pero identificó mal qué campo era cuál. El espacio de acciones (escribir esta cadena) funcionó correctamente. El harness ejecutó la acción correctamente. La comprensión de la captura de pantalla por parte del modelo fue errónea. A esto se le llama error de grounding y es el tema de la lección 25.

</details>

3. ▢ Un agente que llama herramientas y lee archivos usa una herramienta llamada `read_file(path)` y recibe un resultado con un campo de estado. Un agente de uso del ordenador que lee archivos abriéndolos en un editor de texto toma una captura de pantalla tras abrir el editor. ¿Qué observación es más fácil de verificar como exitosa para el harness?

    - a) El agente que llama herramientas, porque el campo de estado es explícito
    - b) El agente de uso del ordenador, porque una captura de pantalla lo muestra todo
    - c) Son igual de fáciles, solo que en formatos distintos
    - d) Ninguna, porque verificar el éxito requiere que el modelo interprete el resultado en cualquier caso

<details markdown="1"><summary>Comprobación</summary>

**a)** El agente que llama herramientas tiene un campo de estado explícito; el harness puede comprobar `if result.status == "success"` sin ambigüedad. La captura de pantalla del agente de uso del ordenador muestra el contenido del archivo, pero el harness tiene que llevar esa captura de pantalla al modelo y pedirle que verifique que el archivo se abrió correctamente, lo que es más lento y menos fiable. El tipo de observación afecta a lo fácil que es la verificación.

</details>

4. ▢ Estás leyendo la trayectoria de un agente de uso del ordenador que intentó rellenar un formulario. El agente realizó ocho acciones: hizo clic en campos, escribió texto y se desplazó. La captura de pantalla final muestra el formulario con los campos vacíos. ¿Qué deberías comprobar primero para diagnosticar por qué falló el agente?

<details markdown="1"><summary>Comprobación</summary>

Mira las coordenadas de cada acción de clic frente a las capturas de pantalla tomadas después de cada clic. ¿Hizo clic el agente en la parte correcta de la pantalla, o los clics cayeron en lugares equivocados? Incluso si el modelo decidió "hacer clic en el campo de usuario", la coordenada real del clic pudo estar desviada. Este es el problema del grounding: la intención del modelo y la ubicación real en pantalla divergieron.

</details>

## Prácticas en el mundo real

- [ ] Abre una aplicación web en un navegador. Toma una captura de pantalla manualmente. Para tres elementos de la pantalla (un botón, un campo de texto, un enlace), estima sus coordenadas en píxeles (x, y). Ahora cambia el tamaño de la ventana del navegador o desplázate, toma una captura de pantalla nueva y vuelve a estimar esas mismas coordenadas. Anota cuánto cambiaron las coordenadas y si una coordenada fija de la primera captura de pantalla seguiría funcionando en la segunda.

- [ ] Lee la trayectoria de un agente de uso del ordenador (de un ejemplo público, la documentación de una herramienta o tu propia prueba). Elige una captura de pantalla de la mitad de la ejecución. Sin mirar las capturas de pantalla ni las acciones siguientes, anota tres cosas que el agente podría hacer a continuación. Luego mira la acción que el agente realmente tomó. ¿Coincidieron tus predicciones?

- [ ] Mañana: Encuentra la descripción de un fallo de un agente de uso del ordenador (en una entrada de blog, un issue de GitHub o el resumen de un paper). Antes de leer la explicación, plantea la hipótesis de si el fallo se debió a que el modelo malentendió la tarea, a un error de sintaxis de la llamada a herramienta, a un error de grounding (coordenadas equivocadas) o a otra cosa. Luego lee la explicación y comprueba si tu intuición era correcta.

## Para profundizar

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
