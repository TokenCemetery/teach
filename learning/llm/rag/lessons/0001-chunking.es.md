---
title: "1. Chunking"
description: "La primera decisión del pipeline, la que heredan todas las etapas posteriores"
type: lesson
---

# Lección 1. Chunking

**Vínculo con la misión:** El chunking es la primera decisión del pipeline que enseña este espacio de trabajo, y todas las etapas posteriores (embeddings, búsqueda híbrida, reranking) trabajan con lo que un chunk les dio. Una mala decisión de chunking no se arregla con reranking.
**Fuente principal:** [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
**Requisitos previos:** ninguno

## Qué debes saber

### Por qué se divide un documento

Un pipeline de recuperación no genera embeddings de documentos enteros ni busca sobre ellos. Primero divide cada documento en **chunks**, y luego genera los embeddings de esos chunks y los indexa. Dos razones prácticas lo obligan:

- Un modelo de embeddings tiene una ventana de contexto limitada, así que un documento largo puede no caber en absoluto.
- Incluso cuando cabe, generar el embedding de un pasaje largo y de temas mezclados como un único vector lo desdibuja. El vector acaba representando un promedio de todo lo que toca el pasaje, lo que lo vuelve peor candidato para una consulta sobre cualquier cosa concreta de su interior.

Así que el chunking existe para mantener cada unidad con embedding lo bastante centrada como para que su vector represente de verdad lo que una consulta podría estar buscando.

### El compromiso central

El tamaño del chunk enfrenta dos modos de fallo entre sí:

- **Chunks demasiado grandes:** el embedding mezcla varios temas y daña la precisión, y una consulta sobre un detalle dentro de un chunk largo puede no hacerlo aparecer como una coincidencia cercana. La recuperación también devuelve más texto circundante irrelevante junto con la parte relevante.
- **Chunks demasiado pequeños:** cada chunk puede perder el contexto circundante que lo hace interpretable, o que responde una pregunta que abarca más de un fragmento pequeño. Una sola oración extraída de un párrafo puede ser ambigua o incompleta por sí sola.

No existe un tamaño de chunk correcto universal. La elección correcta depende del corpus (las cláusulas de un contrato legal se leen distinto que la transcripción de un chat) y del patrón de consultas que el sistema debe atender (una consulta que necesita un solo dato se comporta distinto que una que necesita una explicación de varios pasos).

### Estrategias comunes de chunking

- **Tamaño fijo.** Dividir cada N tokens o caracteres, normalmente con cierto solapamiento entre chunks consecutivos. Es simple y predecible, pero ciego a la estructura real del documento: puede partir por la mitad una oración o una tabla.
- **Recursivo / consciente de la estructura.** Dividir primero por los límites naturales del documento (secciones, luego párrafos, luego oraciones) y recurrir a una división de tamaño fijo solo cuando un fragmento delimitado por esos límites sigue siendo demasiado grande. Respeta la organización del propio autor en lugar de imponer una arbitraria.
- **Chunking semántico.** Generar el embedding de oraciones consecutivas y dividir donde la similitud entre vecinas cae bruscamente, bajo la idea de que un cambio de tema es donde debe ir el límite de un chunk. Es más costoso de calcular y apunta directamente al modo de fallo real (temas mezclados dentro de un chunk) en lugar de hacerlo por aproximación.
- **Consciente de la estructura del documento.** Tratar como atómicas las unidades estructurales que el formato ya ofrece, como la sección de un encabezado, una tabla o un bloque de código: nunca partir una a través del límite de un chunk, porque hacerlo suele destruir su significado.

![Tres barras que representan el mismo documento. La barra superior muestra su estructura natural: una sección corta, una sección larga y una sección mediana, marcadas con líneas discontinuas en los límites reales de las secciones. La barra del medio muestra el chunking de tamaño fijo, que divide el mismo documento en cuatro piezas de igual ancho sin importar dónde terminan realmente las secciones, de modo que un corte cae en medio de la sección larga y la parte por la mitad. La barra inferior muestra el chunking consciente de la estructura, cuyos límites de chunk coinciden exactamente con los límites naturales de las secciones de la barra superior, así que ninguna sección queda dividida entre dos chunks.](images/fixed-vs-structure-aware-chunking.svg)

### Solapamiento

Los chunks consecutivos suelen solaparse en cierto número de tokens. Sin solapamiento, un dato o una oración que cae justo donde se dividen dos chunks puede acabar fragmentado, sin poder recuperarse completo desde ninguno de los dos chunks por separado. El solapamiento cuesta algo de almacenamiento y de cómputo de embeddings redundantes a cambio de no perder información en los límites de los chunks.

## Práctica

1. ▢ En una oración, ¿por qué un pipeline de recuperación hace chunking de un documento en lugar de generar su embedding entero?

<details markdown="1"><summary>Comprobación</summary>

Porque un pasaje largo y de temas mezclados genera un único vector desdibujado que representa un promedio de todo lo que toca, y se recupera mal para una consulta sobre cualquier cosa concreta de su interior (y puede que ni siquiera quepa en la ventana de contexto del modelo de embeddings).

</details>

2. ▢ Un corpus de contratos legales largos se divide en chunks de tamaño fijo de 512 tokens y sin solapamiento. Los usuarios preguntan por cláusulas concretas, y la recuperación sigue fallando en cláusulas que quedaron partidas en el límite de un chunk. Nombra dos cambios en la estrategia de chunking que ayudarían y qué corrige cada uno.

<details markdown="1"><summary>Pista</summary>

Un cambio ataca la propia división en los límites; el otro ataca lo que pasa cuando una división es inevitable.

</details>

<details markdown="1"><summary>Comprobación</summary>

Cambiar a una estrategia consciente de la estructura (o consciente de la estructura del documento) que divida por límites de cláusula o de sección en lugar de por un número bruto de tokens, de modo que una cláusula no se corte a mitad de idea desde el principio. Por separado, añadir solapamiento entre chunks, para que incluso donde una división caiga cerca del límite de una cláusula, el texto completo de la cláusula siga apareciendo intacto en al menos un chunk.

</details>

3. ▢ Un equipo divide un corpus en piezas muy cortas, de una sola oración, para maximizar la precisión. ¿Cuál es la desventaja probable y cuándo aparecería?

<details markdown="1"><summary>Comprobación</summary>

Los chunks individuales pueden perder el contexto circundante que los hace interpretables o completos: una oración extraída sola puede ser ambigua, y una pregunta cuya respuesta abarca más de una oración no podrá responderse desde ningún chunk recuperado por separado. Esto aparece como una recuperación que técnicamente encuentra "la oración correcta" mientras el sistema sigue sin poder producir una respuesta correcta o completa a partir de ella.

</details>

4. ▢ ¿Por qué los chunks consecutivos suelen solaparse?

    - a) Para hacer el índice vectorial más grande y más exhaustivo
    - b) Para que un dato o una oración que cae en el límite de un chunk no quede fragmentado e irrecuperable desde cualquiera de los dos chunks
    - c) Porque los modelos de embeddings requieren una longitud mínima de entrada
    - d) Para que el reranker pueda comparar chunks adyacentes entre sí

<details markdown="1"><summary>Comprobación</summary>

**b)** Para que un dato o una oración que cae en el límite de un chunk no quede fragmentado e irrecuperable desde cualquiera de los dos chunks. (a) describe un costo del solapamiento, no su propósito. (c) y (d) no son la razón de que exista el solapamiento.

</details>

## Prácticas en el mundo real

- [ ] Elige un documento real de un corpus sobre el que recuperarías. Haz chunking a mano de dos formas (tamaño fijo y consciente de la estructura, usando sus encabezados o secciones reales) y compara dónde divide cada estrategia a mitad de idea.
- [ ] Para ese mismo documento, elige una consulta que un usuario podría plantear de forma realista y comprueba qué salida de chunking contendría de verdad una respuesta completa y recuperable.
- [ ] Mañana: lee completo el artículo sobre estrategias de chunking enlazado más abajo y anota qué estrategia usarías por defecto para tu propio corpus y por qué.

## Para profundizar

- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
