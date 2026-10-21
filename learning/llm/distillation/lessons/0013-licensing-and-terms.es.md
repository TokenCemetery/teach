---
title: "13. Licencias y términos"
description: "Qué te permiten hacer con sus salidas los términos de un proveedor y la licencia de un modelo abierto"
type: lesson
---

# Lección 13. Licencias y términos

**Vínculo con la misión:** La misión te pide comprobar que el uso de un conjunto de destilación está permitido, lo que significa leer los documentos que gobiernan al profesor antes de generar datos con él, y registrar lo que encontraste.
**Fuente principal:** [Terms: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
**Requisitos previos:** [Lección 12](0012-filtering-synthetic-data.md), [Lección 10](0010-distilling-from-generated-data.md), [Datos sintéticos](../GLOSSARY.md), [Profesor](../GLOSSARY.md)

Esta lección no es asesoría legal. Lee dos documentos, cita lo que dicen y ofrece una lista de comprobación de qué buscar. No afirma nada sobre lo que un documento significa para tu caso, si una cláusula es exigible o qué documento te rige. Los términos y las licencias cambian sin una versión que una lección pueda fijar, así que las citas de abajo llevan la fecha en que se leyeron, y deberías leer el texto vigente antes de apoyarte en cualquiera de ellas. Para una decisión real, consulta a un abogado.

## Calentamiento

1. ▢ Los autores de phi-1 podaron sus ejercicios frente a HumanEval con n-gramas, embeddings y coincidencia de AST. ¿Por qué no se quedaron en el solapamiento de n-gramas?

<details markdown="1"><summary>Comprobación</summary>

Una comprobación de 13-gramas señaló solo cuatro preguntas, todas falsos positivos, y era demasiado tosca para encontrar código similar, así que añadieron la comparación por embeddings y AST (lección 12).

</details>

2. ▢ Los datos de Alpaca vinieron de text-davinci-003 y su modelo se afinó a partir de LLaMA 7B. ¿De qué dos cosas, que pertenecen a otro o que otro controla, depende por tanto?

<details markdown="1"><summary>Comprobación</summary>

Del profesor que generó los datos (text-davinci-003 de OpenAI, bajo los términos de OpenAI) y del base model (LLaMA, bajo su licencia). Ambos son entradas del estudiante, y cada uno trae sus propias condiciones (lección 10).

</details>

3. ▢ Nombra el filtro que comprueba por regla una respuesta generada frente a la verdad de referencia, y una cosa que no puede juzgar.

<details markdown="1"><summary>Comprobación</summary>

El rejection sampling con un verificador, donde solo se conservan las muestras que pasan. No puede juzgar respuestas abiertas ni el estilo, donde no hay nada contra lo que comprobar (lección 12).

</details>

## Qué debes saber

### Tres documentos, tres preguntas

Cuando generas datos a partir de un profesor puedes estar sujeto a hasta tres tipos distintos de documento, y cada uno responde a una pregunta distinta.

| Documento | Pregunta a la que responde |
|---|---|
| Los términos de uso del proveedor, para un modelo alojado | ¿Qué puedo hacer con las salidas que obtengo de este servicio? |
| La licencia de unos pesos abiertos | ¿Qué puedo hacer con el modelo, y con lo que produce? |
| La licencia o los términos de los prompts y de los datos semilla | ¿Qué puedo hacer con las entradas que le di, y con los datos que construí a partir de ellas? |

Cada uno es un texto aparte, con su propia fecha y alcance. Leer uno no te dice qué dice otro.

### Qué dicen los términos de un proveedor alojado

Los Terms of Use de OpenAI para el resto del mundo, vigentes desde el 1 de enero de 2026, enumeran cosas que un usuario no puede hacer. Entre ellas está esta línea, tal como se leyó cuando se escribió este track, en octubre de 2026 (se cita el texto original en inglés). El sitio bloquea las lecturas con scripts, así que vuelve a comprobar la página en un navegador:

> "Use Output to develop models that compete with OpenAI."

Tres cosas que señalar, y no más. La frase está en la sección de usos prohibidos. Habla de desarrollar modelos que compitan con OpenAI, que es algo más estrecho que desarrollar cualquier modelo. Y es un solo documento: tu uso puede caer bajo otra edición, o bajo un acuerdo aparte para una API o un servicio empresarial, y esta lección no los ha leído.

### Qué dice una licencia de pesos abiertos

La Llama 3.1 Community License Agreement de Meta dice, en la sección 1.b.i (Redistribution and Use), tal como se leyó del texto del repositorio el 17 de octubre de 2026 (se cita el texto original en inglés):

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

El mismo párrafo exige además que, si distribuyes los Llama Materials, o un producto o servicio que los contenga, incluido otro modelo de IA, proporciones una copia del acuerdo y muestres de forma destacada "Built with Llama" en un sitio web relacionado, interfaz de usuario, entrada de blog, página de información o documentación del producto. Por separado, la licencia dice que el uso de los Llama Materials debe cumplir las leyes aplicables y una Acceptable Use Policy que incorpora por referencia.

El texto asocia una condición sobre el nombre del modelo al uso de salidas de esta manera cuando el modelo resultante se distribuye o se pone a disposición. Esta lección no afirma nada más allá de las palabras. Otras versiones de Llama y otros modelos abiertos tienen sus propias licencias, y algunas dicen cosas distintas.

### Cómo lo resolvió un proyecto

Los autores de Alpaca declaran que su modelo está pensado solo para investigación académica y que cualquier uso comercial está prohibido, y dan tres factores: LLaMA tiene una licencia no comercial, así que la heredan; los datos de instrucciones vienen de text-davinci-003, cuyos términos de uso, dicen, prohíben desarrollar modelos que compitan con OpenAI; y no habían construido medidas de seguridad adecuadas. También escriben que su demo se restringió a usos no comerciales y a usos que sigan la licencia de LLaMA (entrada del blog de Alpaca, "Overview" y "Release decision"). Fíjate en lo que hicieron: nombraron cada fuente de restricción y vincularon la publicación a ella. Ese es el hábito que hay que copiar, digan lo que digan tus propios documentos.

### Antes de generar: una lista de comprobación

Lee y registra, en este orden:

1. **Los términos del profesor.** Encuentra el documento exacto que se aplica a la forma en que accedes al modelo. Anota su nombre, URL, fecha o versión, y las frases sobre usar las salidas para entrenar otros modelos.
2. **La licencia de los pesos, si el profesor es abierto.** Anota la versión, cualquier cláusula sobre entrenar con las salidas, cualquier requisito de nombre o atribución y cualquier política de uso que incorpore.
3. **Los prompts y los datos semilla.** La licencia de lo que le des al profesor, como tareas semilla, documentos o texto extraído de la web, gobierna las entradas. Compruébala por separado de la del profesor.
4. **Nombre y atribución.** Si un documento exige un prefijo en el nombre del modelo o una línea de crédito, decídelo ahora, antes de que el modelo tenga nombre.
5. **Cómo se usará y compartirá el estudiante.** Muchas cláusulas dependen de si el modelo se distribuye, se pone a disposición o se vende, y de con qué compite. Escribe tu uso previsto.
6. **La fecha.** Registra cuándo leíste cada documento y cuándo generaste cada lote, porque los términos vigentes en el momento de la generación pueden diferir de los de hoy.

Guarda este registro junto al dataset, una línea por fuente, para que la pregunta "¿de dónde salió esto?" tenga respuesta dentro de un año. Un campo de procedencia en cada ejemplo, que nombre al profesor, la versión y la fecha de generación, cuesta casi nada.

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

Las entradas `<...>` son campos que rellenar para tu propio proyecto.

### Lo que esta lección no puede decirte

No puede decir si un proyecto dado infringe una cláusula. Eso depende del texto completo, de los hechos, de la jurisdicción y de lo que harán el proveedor y el titular de la licencia, nada de lo cual está en una cita. El objetivo del ejercicio es más estrecho: asegurarte de haber leído los documentos, saber lo que dicen literalmente y tener un registro fechado de ello.

## Práctica

1. ▢ Un equipo hace fine-tuning de un modelo con salidas de Llama 3.1 y lo pondrá a disposición. Según el texto de la licencia citado, ¿qué debe cumplirse con el nombre del nuevo modelo?

    - a) Debe terminar con la palabra "Llama"
    - b) No debe contener ninguna mención a Llama
    - c) Debe empezar con la palabra "Llama"
    - d) Debe registrarse ante el licenciante

<details markdown="1"><summary>Comprobación</summary>

**c)** La frase citada dice "Llama" al principio del nombre del modelo de IA, para un modelo que se distribuye o se pone a disposición. (a) invierte la posición. (b) es lo contrario de lo que dice. (d) no está en el texto citado.

</details>

2. ▢ La línea citada de OpenAI trata de usar la salida "to develop models that compete with OpenAI". Un colega la resume como "OpenAI prohíbe entrenar con sus salidas". ¿Qué falla en el resumen?

<details markdown="1"><summary>Comprobación</summary>

La línea es más estrecha que el resumen: trata de desarrollar modelos que compitan con OpenAI, no de todo desarrollo de modelos. Además es un solo documento, de una edición de los términos, en una fecha. Cita la frase y su fecha en lugar de una paráfrasis, y comprueba qué se aplica a tu vía de acceso. Si tu proyecto compite o no es una pregunta legal que esta lección no responde.

</details>

3. ▢ Generaste 200,000 ejemplos a partir de un modelo alojado en marzo. En octubre el proveedor cambia sus términos. ¿Qué haces primero?

<details markdown="1"><summary>Comprobación</summary>

Lee los términos nuevos y los términos vigentes cuando generaste los datos, ambos de la propia página del proveedor, y mira qué dice tu registro sobre qué versión leíste. El registro es la razón por la que anotaste la fecha. Lo que sigue es una pregunta legal sobre qué términos se aplican a datos ya generados, así que llévala a alguien cualificado, no a una suposición.

</details>

4. ▢ Los autores de Alpaca dan tres factores para una publicación solo para investigación. ¿Cuál depende de la elección del profesor, y cuál de la elección del base del estudiante?

<details markdown="1"><summary>Comprobación</summary>

El factor del profesor es que los datos vienen de text-davinci-003, cuyos términos prohíben desarrollar modelos que compitan con OpenAI. El factor del base es que LLaMA tiene una licencia no comercial, así que Alpaca la hereda. El tercero, la falta de medidas de seguridad, no es sobre ninguno de los dos.

</details>

5. ▢ Tus prompts semilla vienen de un dataset público y tu profesor es un modelo abierto con una licencia permisiva. Nombra dos documentos que aún necesitas leer antes de entregar el estudiante.

<details markdown="1"><summary>Comprobación</summary>

La licencia del dataset semilla, ya que gobierna las entradas, y la propia licencia del modelo abierto, por cualquier cláusula sobre entrenar con sus salidas, nombre, atribución o política de uso. Comprueba también la licencia de cualquier base model del que parta el estudiante. Una licencia permisiva en una fuente no se traslada a las demás.

</details>

## Prácticas en el mundo real

- [ ] Abre los Terms of Use de OpenAI y la licencia de Llama 3.1 y encuentra las frases exactas citadas arriba. Copia la fecha de vigencia de cada una en una nota.
- [ ] Elige un dataset sintético público en un hub que uses. Encuentra de qué profesor dice que se generó, y anota los términos o la licencia de ese profesor tal como constan en la página del dataset.
- [ ] Mañana: rellena el registro de la lista de comprobación de arriba para un dataset hipotético de un profesor que elijas, y marca cada campo que no pudiste rellenar a partir de un documento primario.

## Para profundizar

- [Secuencia y datos sintéticos](../reference/sequence-and-synthetic-data.md)
- [Terms: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
- [License: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [Article: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
