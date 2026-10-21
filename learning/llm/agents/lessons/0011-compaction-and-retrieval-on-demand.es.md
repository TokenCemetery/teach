---
title: "11. Compactación y recuperación bajo demanda"
description: "Dos estrategias para mantener dentro del presupuesto el contexto de un agente de larga duración sin perder lo que todavía importa"
type: lesson
---

# Lección 11. Compactación y recuperación bajo demanda

**Vínculo con la misión:** Presupuestar el costo en tokens y la latencia de un bucle agéntico, y decir de qué parte del bucle viene la amplificación.
**Fuente principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Requisitos previos:** [Lección 10](0010-the-context-window-as-budget.md)

## Calentamiento

1. ▢ ¿Por qué es riesgoso el truncamiento ingenuo (descartar los turnos más antiguos cuando se alcanza un límite de tamaño)?

<details markdown="1"><summary>Comprobación</summary>

El truncamiento ingenuo podría descartar un resultado de herramienta, una restricción o una instrucción que el modelo todavía necesita, y el modelo no sabrá que falta la información. Trabajará en silencio desde una comprensión incompleta y fallará de formas inesperadas.

</details>

2. ▢ ¿Qué es la degradación del contexto (context rot)?

<details markdown="1"><summary>Comprobación</summary>

A medida que se acumula contenido de poca relevancia en el contexto, la atención del modelo se vuelve más ruidosa y le cuesta distinguir lo que todavía importa de los callejones sin salida antiguos y el razonamiento abandonado. Un contexto inflado es a la vez caro y menos preciso.

</details>

## Qué debes saber

### Compactación: reemplazar los turnos antiguos por un resumen

Una estrategia es reemplazar periódicamente un tramo de transcripción antigua por un resumen condensado sobre el que el modelo todavía pueda actuar. En lugar de conservar "leí file1.py y encontré estas 50 líneas", podrías reemplazar toda esa secuencia por "file1.py contiene una clase de base de datos; los métodos clave son init, query, close".

El harness detecta cuándo la transcripción ha crecido mucho y entrega los turnos antiguos a un resumidor (a menudo otra llamada a un modelo, o una extracción más simple). El resumen se inserta en la transcripción en lugar de los turnos originales, manteniendo bajo control el tamaño de la transcripción.

**El riesgo:** El resumen podría omitir un detalle que luego resulte importante. Si más adelante el agente necesita saber que file1.py también definía una función auxiliar, pero el resumen la omitió, el agente ha perdido esa información de forma permanente. A diferencia del truncamiento ingenuo (que siempre es riesgoso), la compactación es deliberada y en teoría reversible, pero la pérdida de información es real y difícil de predecir.

### Recuperación bajo demanda: darle al agente una herramienta para volver a traer el detalle

Otra estrategia es no mantener el detalle completo en el contexto en absoluto. En lugar de cargar y guardar el contenido de cada archivo, el harness conserva solo un resumen (nombre del archivo, tamaño, fecha de modificación, una breve nota con el conteo de líneas). Cuando el modelo necesita ver el contenido completo, llama a una herramienta como "read_file" o "re_fetch_detail". El modelo obtiene el detalle bajo demanda y solo del archivo que está examinando en ese momento.

El intercambio: cada recuperación añade latencia (una llamada a herramienta más, un viaje de ida y vuelta más). Pero el contexto residente se mantiene mucho más pequeño. En una tarea larga que examina muchos archivos pero trabaja solo con unos pocos a la vez, la recuperación bajo demanda es mucho más barata en tokens totales que mantener cada archivo en el contexto para siempre.

### Combinadas: compactación + recuperación bajo demanda

El enfoque más potente combina ambas. El harness mantiene un contexto pequeño y curado que contiene:

- El objetivo y las últimas restricciones
- Un resumen de lo hecho hasta ahora
- Nombres de archivos y metadatos
- Hallazgos recientes que importan

Los resultados detallados antiguos se comprimen en resúmenes (compactación). Si el modelo necesita ver el detalle completo de un archivo o resultado antiguo, puede traerlo con una herramienta de recuperación (bajo demanda). La memoria de trabajo del modelo es pequeña y rápida, pero tiene una forma de volver atrás a buscar el detalle que necesita.

En un agente de revisión de código que revisa 100 archivos a lo largo de 200 turnos:

- Un agente ingenuo mantiene en el contexto cada archivo que ha leído, y llega a 500.000 tokens en el turno 50. Los turnos 51 a 200 son lentos y caros.
- Un agente inteligente mantiene en el contexto solo las rutas de archivos y un resumen (5.000 tokens), con una herramienta "read_file". Trae cada archivo bajo demanda mientras compara. El turno 50 cuesta casi lo mismo que el turno 200. El costo total en tokens de toda la ejecución es una fracción del enfoque ingenuo.

## Práctica

1. ▢ Resumes los primeros 20 turnos de la transcripción de un agente en un párrafo: "The agent explored three codebases and found performance bottlenecks in caching." Este resumen reemplaza los 20 turnos originales. Más tarde, en el turno 50, el modelo dice que quiere entender la consulta exacta que era lenta. ¿Qué riesgo presenta aquí la compactación?

    - a) El modelo se negará a trabajar sin los turnos originales
    - b) El resumen podría no haber registrado los detalles exactos de la consulta, y podrían perderse para siempre
    - c) La compactación siempre es sin pérdidas, así que esto no es un riesgo
    - d) El modelo volverá a leer el resumen y recordará la consulta

<details markdown="1"><summary>Comprobación</summary>

**b)** La compactación descarta detalles que podrían importar más adelante. El resumen es conciso pero puede omitir datos específicos que el modelo necesita después. A diferencia del truncamiento, la compactación es deliberada, pero la pérdida de información es real. La opción a es incorrecta porque el modelo trabajará con el resumen, pero puede producir resultados erróneos. La opción c es incorrecta porque la compactación es con pérdidas por diseño. La opción d es incorrecta porque el modelo trabaja solo con el nuevo resumen, no con el original.

</details>

2. ▢ Un agente está procesando 200 documentos, resumiendo cada uno. ¿Por qué es mejor la recuperación bajo demanda que mantener los 200 contenidos de documentos en el contexto desde el principio?

<details markdown="1"><summary>Pista</summary>

¿Cuántos documentos necesita normalmente el modelo en su contexto al mismo tiempo? Si está resumiendo el documento 45, ¿necesita tener disponible ahora mismo el contenido de los documentos 1 al 44?

</details>

<details markdown="1"><summary>Comprobación</summary>

El modelo normalmente está centrado en uno o pocos documentos a la vez. Mantener los 200 en el contexto desperdicia tokens en contenido que el modelo no está examinando en ese momento. Con la recuperación bajo demanda, el harness mantiene en el contexto solo el documento actual y un resumen de los hallazgos anteriores. Si el modelo necesita volver a examinar un documento antiguo, lo trae. El costo total en tokens de 200 documentos es mucho menor que mantener los 200 en memoria todo el tiempo.

</details>

3. ▢ En un sistema de compactación más recuperación bajo demanda, ¿qué tres cosas debe contener el contexto siempre residente?

<details markdown="1"><summary>Comprobación</summary>

El objetivo y las restricciones, un resumen del progreso hasta ahora y metadatos sobre los recursos disponibles (nombres de archivos, títulos de documentos, listas de herramientas). El detalle completo está comprimido en resúmenes (compactación) o disponible bajo demanda (recuperación). Esto mantiene el contexto residente pequeño y centrado en lo que el modelo necesita para actuar ahora mismo.

</details>

4. ▢ Diseñas un agente para leer artículos técnicos y extraer resúmenes. Tras leer 50 artículos, el contexto es de 60.000 tokens. Compara dos enfoques:
    - Enfoque A: Compactar el contenido de los artículos antiguos en resúmenes de un párrafo cada 10 artículos. Mantener todos los resúmenes en el contexto.
    - Enfoque B: Mantener en el contexto solo los títulos, autores y hallazgos de los artículos. Darle al agente una herramienta "re_read_paper" por si necesita el texto completo.

¿Qué enfoque usa menos tokens para el artículo 100, y por qué?

<details markdown="1"><summary>Comprobación</summary>

El enfoque B usa menos tokens. Con el enfoque A acumulas 10 resúmenes de 200 a 300 tokens cada uno, hasta llegar a 2.000 a 3.000 tokens de contenido compactado para el artículo 100. Con el enfoque B, mantienes solo metadatos (100 a 200 tokens) más el texto del artículo actual (500 tokens), y el modelo rara vez necesita releer un artículo antiguo. El enfoque B ahorra tokens al no guardar siempre todos los resúmenes antiguos.

</details>

## Prácticas en el mundo real

- [ ] Audita una transcripción larga de un agente que hayas usado o escrito. Identifica qué partes siguen siendo relevantes (objetivo, restricciones recientes, problemas pendientes) y cuáles se pueden compactar o eliminar con seguridad. Escribe un resumen de una frase que podría reemplazar el primer 30 % de los turnos.
- [ ] Diseña un agente hipotético para una tarea que te importe (investigación, programación, análisis). Esboza si usarías compactación, recuperación bajo demanda o ambas, y por qué.
- [ ] Mañana: Toma una versión "tonta" de un agente que mantiene todo en el contexto, estima su costo en tokens a lo largo de 100 turnos, luego rediséñala con compactación y recuperación bajo demanda y estima el nuevo costo.

## Para profundizar

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
