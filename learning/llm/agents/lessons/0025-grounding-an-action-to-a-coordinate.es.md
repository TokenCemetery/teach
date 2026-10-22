---
title: "25. Anclar una acción a una coordenada"
description: "Por qué traducir una intención visual a una coordenada de píxel es más difícil y más frágil que un argumento tipado de una llamada a herramienta"
type: lesson
---

# Lección 25. Anclar una acción a una coordenada

**Vínculo con la misión:** Diagnosticar un agente de uso del ordenador que falla exige reconocer los errores de grounding (un fallo de coordenada) como algo distinto del mal uso de una herramienta o de los errores de lógica, para poder arreglar el problema correcto.
**Fuente principal:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Requisitos previos:** [Lección 24](0024-screenshots-as-observations.md)

## Calentamiento

1. ▢ En un agente que llama herramientas, cuando el modelo quiere actualizar un usuario, ¿qué le envía al harness, y cómo sabe el harness qué usuario concreto actualizar?

<details markdown="1"><summary>Comprobación</summary>

El modelo envía una llamada a herramienta con un argumento como `user_id: "u_123"`, un identificador estable y único. El harness lee este identificador y actualiza al usuario por ID sin ambigüedad.

</details>

2. ▢ En un agente de uso del ordenador, cuando el modelo quiere hacer clic en un botón que ve en la captura de pantalla, ¿qué le envía al harness, y cómo sabe el harness en qué botón hacer clic?

<details markdown="1"><summary>Comprobación</summary>

El modelo envía una acción de clic en una coordenada de píxel, como `click(x=450, y=200)`. El harness lee la coordenada y hace clic en esa posición exacta de la pantalla.

</details>

## Qué debes saber

### El problema del grounding

El grounding es el paso de traducir la intención de un modelo a una coordenada de pantalla real. Cuando un agente que llama herramientas quiere actualizar un registro, especifica el registro mediante un ID estable, un nombre o un identificador único sobre el que el harness puede actuar directamente. No hay ambigüedad: el harness encuentra el registro o no lo encuentra.

Cuando un agente de uso del ordenador quiere hacer clic en un botón, tiene que ubicar visualmente ese botón en la captura de pantalla actual, estimar sus coordenadas en píxeles y emitir una tupla de coordenadas como `(x, y)`. Esto es más difícil en cuatro aspectos.

**Primero, no hay una referencia estable.** Un botón en el píxel 450, 200 en una captura de pantalla es un botón distinto (o ningún botón) si la ventana cambia de tamaño, la página se desplaza o el contenido se mueve. Un ID persiste a través de los cambios de diseño; una coordenada no. Un agente que llama herramientas pediría un botón por nombre; un agente de uso del ordenador pide un botón por posición, lo que es frágil.

**Segundo, el modelo no puede pedir ayuda.** En un agente que llama herramientas, si el harness no entiende un argumento, devuelve un error claro: "user_id u_999 not found" o "invalid format for date_field". El modelo lee el error y corrige su argumento. En un agente de uso del ordenador, un clic en la coordenada equivocada simplemente da en lo que no es (o en el espacio vacío). El modelo no recibe un mensaje de error. Solo se entera en la siguiente captura de pantalla de que el clic cayó en el lugar equivocado, e incluso entonces tiene que inferir por inspección visual que el clic falló.

**Tercero, el ciclo de retroalimentación es lento.** Después de que un agente que llama herramientas comete un error, recibe un mensaje de error tipado. Después de que un agente de uso del ordenador comete un error, tiene que tomar otra captura de pantalla completa, enviarla al modelo, esperar a que el modelo interprete la nueva imagen y razone sobre qué salió mal, y volver a intentarlo. Cada error de grounding cuesta un viaje completo de ida y vuelta al modelo para descubrirlo y arreglarlo.

**Cuarto, los pequeños cambios del entorno rompen secuencias que funcionaban.** Una llamada a herramienta que nombra a un usuario por ID sigue funcionando si cambia el nombre, el correo o el departamento del usuario. Un clic en unas coordenadas se rompe si el botón se mueve aunque sean unos pocos píxeles. La pantalla de un portátil de 13 pulgadas, un monitor de 27 pulgadas, el zoom del navegador, el renderizado de fuentes y los puntos de corte de CSS pueden mover el mismo botón a coordenadas distintas. Una trayectoria que funcionó perfectamente en una máquina puede fallar en silencio en otra.

### Qué hace frágil al grounding

Imagina que un agente hace clic con éxito en un cuadro de búsqueda en (300, 150) en un navegador de escritorio con el zoom normal. La misma página web vista en un teléfono móvil o con el zoom del navegador al 125 por ciento podría renderizar el cuadro de búsqueda en (225, 112) o en (375, 188). La coordenada ya no es correcta. El clic podría caer en nada, o en un elemento completamente distinto.

La lógica del agente era sólida. El modelo tomó una decisión razonable. El tipo de acción (clic) era correcto. Pero la coordenada era errónea, porque el entorno cambió. Un agente que llama herramientas y pide una herramienta llamada `search` no tiene este problema, ya que el nombre de la herramienta es estable.

Por eso los errores de grounding son una categoría de fallo propia de los agentes que manejan la pantalla. No ocurren en los agentes que llaman herramientas, porque estos referencian las cosas por nombre, no por posición.

### Mitigación parcial: herramientas con conocimiento de la estructura

Algunas herramientas de navegador o de uso del ordenador intentan reducir la fragilidad del grounding ofreciendo un punto medio: además de una captura de pantalla, la herramienta devuelve información estructurada sobre los elementos de la página: los nombres, roles, posiciones y cajas delimitadoras de cada botón, enlace y campo de formulario.

El modelo entonces puede decir "haz clic en el botón con la etiqueta 'Submit'" o "haz clic en el campo de texto de la fila del correo", y el harness traduce esa referencia con nombre a una coordenada en el momento del clic, en lugar de pedirle al modelo que estime coordenadas a partir de los píxeles. Esto recupera algo de estabilidad: si el botón se mueve, el harness calcula las nuevas coordenadas automáticamente, sin que el modelo tenga que volver a estimar.

Esto es un intercambio. Ganas fiabilidad y pierdes parte de la generalidad de "funciona en cualquier interfaz gráfica" que logra la acción puramente basada en capturas de pantalla. Una herramienta con conocimiento de la estructura funciona bien para páginas web, donde los elementos HTML tienen roles semánticos e IDs estables, pero puede que no funcione para aplicaciones gráficas de escritorio, juegos o aplicaciones poco conocidas para las que la herramienta no fue diseñada. Las acciones puramente basadas en capturas de pantalla no tienen esta limitación, pero son más frágiles.

### Cómo detectar errores de grounding en una trayectoria

Cuando leas la trayectoria de un agente de uso del ordenador, busca patrones:

- La intención del modelo tiene sentido (decidió buscar algo, rellenar un campo, etc.), pero la acción no produjo el resultado esperado.
- Varios clics seguidos caen en el lugar equivocado.
- La misma acción funciona en una captura de pantalla pero falla en la siguiente.
- Las coordenadas están lejos de cualquier elemento visible.

Estas son las marcas distintivas de un error de grounding. El modelo razonaba correctamente sobre qué hacer, pero las coordenadas no coincidían con la pantalla. Esto es distinto de un error de lógica (el modelo decidió hacer lo equivocado) o de un fallo de herramienta (la herramienta se cayó).

## Práctica

1. ▢ Un agente hace clic en las coordenadas (500, 250) para enviar un formulario. La captura de pantalla antes del clic muestra un botón Submit centrado aproximadamente en (500, 250). La acción tiene éxito y el formulario se envía. En el siguiente turno, el agente intenta hacer clic de nuevo en el mismo botón Submit en las mismas coordenadas (500, 250), pero el formulario ya no está y se muestra un mensaje de carga. El segundo clic cae en nada. ¿Es esto un error de grounding?

<details markdown="1"><summary>Comprobación</summary>

No. El primer clic estuvo correctamente anclado. El segundo clic falló porque la pantalla cambió, no porque el modelo estimara mal la coordenada. Los errores de grounding ocurren cuando la coordenada no coincide con el objetivo previsto en la captura de pantalla que el modelo está mirando ahora mismo. Una vez que cambió el contenido de la página, la coordenada quedó obsoleta, pero eso no es un error de grounding en la toma de decisiones del agente; es un comportamiento correcto: el agente intentó hacer clic en algo que ya no estaba allí.

</details>

2. ▢ Un agente lee una captura de pantalla de una página de inicio de sesión con dos campos: el usuario arriba y la contraseña debajo. El agente decide escribir la contraseña, estima que el campo de contraseña está aproximadamente en (350, 180) y envía la acción `type(x=350, y=180)`. El harness hace clic en (350, 180), que en realidad es el campo de usuario, y la contraseña se escribe en el campo de usuario. El agente entonces ve una nueva captura de pantalla que muestra el campo de usuario ahora relleno con la contraseña. ¿Es un error de grounding, un error de lógica o ambos?

<details markdown="1"><summary>Pista</summary>

Hazte dos preguntas por separado: (1) ¿Tomó el modelo una decisión razonable sobre qué hacer? (2) ¿Acertó el modelo con las coordenadas?

</details>

<details markdown="1"><summary>Comprobación</summary>

Es un error de grounding, no un error de lógica. La decisión del modelo fue correcta: decidió escribir la contraseña. Pero el modelo estimó mal las coordenadas del campo de contraseña. La coordenada (350, 180) era errónea; el campo de contraseña estaba en realidad más abajo en la pantalla, quizá en (350, 240). El modelo pretendía hacer clic en el objetivo correcto pero ancló la acción de forma incorrecta.

</details>

3. ▢ Un agente de uso del ordenador interactúa con dos aplicaciones web distintas en secuencia. En la primera aplicación, rellena con éxito un formulario haciendo clic en un campo en (400, 300). En la segunda aplicación, intenta hacer clic en un campo de entrada de texto que parece estar en una posición similar de la pantalla, también en (400, 300), pero en la segunda aplicación esa coordenada es espacio vacío y el clic cae en nada. ¿Es el segundo clic un error de grounding?

    - a) Sí, porque la coordenada no coincidía con el objetivo previsto en la captura de pantalla de la segunda aplicación
    - b) No, porque el modelo usó el mismo razonamiento para ambas aplicaciones
    - c) No, porque la coordenada funcionó correctamente la primera vez, así que la segunda aplicación debe tener un error de interfaz
    - d) No, porque los errores de grounding solo ocurren cuando el modelo intenta a propósito hacer clic en lo equivocado

<details markdown="1"><summary>Comprobación</summary>

**a)** El clic estuvo mal anclado: la coordenada no coincidía con el objetivo previsto en la captura de pantalla actual de la segunda aplicación. El hecho de que la misma coordenada funcionara en otra aplicación es irrelevante; el grounding trata de la correspondencia entre la intención y la coordenada en la pantalla que el modelo tiene delante ahora mismo. **b)** es incorrecta porque el razonamiento del modelo no es lo que hace que un clic esté bien anclado o no, solo si la coordenada cae en el objetivo previsto. **c)** es incorrecta porque que una coordenada haya funcionado una vez no te dice nada sobre si es correcta en otra pantalla; el modelo es quien asumió una estabilidad que no debía. **d)** es incorrecta porque los errores de grounding son equivocaciones, no elecciones intencionales.

</details>

4. ▢ Estás leyendo una trayectoria donde un agente no logró completar una tarea. En el turno siete, el agente hizo clic en (1200, 50), la parte superior derecha de la pantalla. No hay nada visible allí, y el clic no tuvo efecto. El modelo dijo entonces que no encontró el botón que buscaba. En el siguiente turno, el agente hizo clic en (150, 50), la parte superior izquierda, y encontró el botón. Formula una hipótesis sobre qué salió mal en el turno siete.

<details markdown="1"><summary>Comprobación</summary>

Es probable que el agente confundiera la posición del botón y anclara el clic demasiado a la derecha. El botón estaba en realidad en el lado izquierdo de la pantalla, pero el modelo estimó que estaba a la derecha. Este es un error de grounding clásico: la intención del modelo (encontrar y hacer clic en el botón) era correcta, pero la coordenada era errónea. El agente se corrigió en el siguiente turno, posiblemente al volver a leer la captura de pantalla o reconsiderar su estimación.

</details>

## Prácticas en el mundo real

- [ ] Toma una captura de pantalla de una página web con el zoom normal. Elige un botón y anota sus coordenadas en píxeles tal como las estimas. Ahora amplía el navegador un 25 por ciento y toma una captura de pantalla nueva. Busca las coordenadas del mismo botón en la captura ampliada usando las herramientas para desarrolladores de tu navegador (inspecciona el elemento y consulta su caja delimitadora). Anota las nuevas coordenadas. ¿Cuánto se desviaba tu estimación de las coordenadas reales en la primera captura de pantalla? ¿Cómo cambió el zoom la posición?

- [ ] Mira o lee la trayectoria de un agente de uso del ordenador (de un blog, la documentación de una herramienta o un ejemplo). Para tres acciones consecutivas, compara lo que el agente pretendía hacer (por el contexto o el prompt) con las coordenadas que emitió y la captura de pantalla que siguió. ¿Coincidió el grounding con la intención? Si no, ¿qué cambió las coordenadas?

- [ ] Mañana: Diseña un formulario web sencillo (mentalmente o en código) que creas que sería difícil de anclar correctamente para un agente de uso del ordenador. ¿Qué propiedades del formulario hacen frágil el grounding? Luego diseña una segunda versión del mismo formulario que sería más fácil de anclar, y explica qué cambiaste.

## Para profundizar

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
