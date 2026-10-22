---
title: "21. Construir el dataset"
description: "Los datos superan a cualquier hiperparámetro de este espacio de trabajo"
type: lesson
---

# Lección 21. Construir el dataset

**Vínculo con la misión:** La calidad de los datos domina a cualquier hiperparámetro de este espacio de trabajo. La etapa 3 te enseñó a girar un control; esta etapa te enseña qué es lo que realmente mueve el resultado.
**Fuente principal:** [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
**Requisitos previos:** [Lección 3](0003-tokenizers-and-chat-templates.md), [Lección 12](0012-reading-a-training-run.md)

## Calentamiento

1. ▢ ¿Cuál es la comprobación de más valor antes de un trabajo de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Decodificar un ejemplo de entrenamiento real y leerlo, contando las posiciones puntuadas frente a las enmascaradas. Atrapa a la vez el desajuste de template, los tokens de fin de turno ausentes, los bugs de enmascarado y el truncamiento.

</details>

2. ▢ ¿Qué significa una curva de pérdida en escalera con caídas en las fronteras de los epochs?

<details markdown="1"><summary>Comprobación</summary>

Memorización: el modelo está reconociendo ejemplos que ya ha visto.

</details>

3. ▢ ¿Qué variante de pérdida debería usar normalmente el instruction tuning?

<details markdown="1"><summary>Comprobación</summary>

Solo de la completion. Las posiciones del prompt se enmascaran a `-100` para que solo se puntúe la respuesta del asistente.

</details>

## Qué debes saber

### La proporción incómoda

Si tienes poco tiempo, gástalo en los datos. La brecha entre un dataset mediocre y uno bueno es mayor que la brecha entre rank 8 y rank 128, mayor que LoRA frente a DoRA y mayor que la mayoría de las cosas que podrías ajustar. Los hiperparámetros son legibles y satisfactorios de ajustar, y por eso absorben atención desproporcionada a su efecto.

El resultado de LIMA es el enunciado publicado más afilado de esto: un número pequeño de ejemplos cuidadosamente curados, del orden de mil, produjo un seguimiento de instrucciones sólido, lo que respalda la idea de que el supervised fine-tuning enseña sobre todo *formato y estilo* mientras que la capacidad viene del preentrenamiento. Trata el número exacto como específico de esa configuración; toma en serio la dirección.

### Lo que el fine-tuning enseña bien, y mal

| Enseña bien | Enseña mal |
|---|---|
| Formato y estructura de la salida | Hechos nuevos sobre el mundo |
| Tono, registro, voz del dominio | Capacidad de razonamiento que no estuviera ya |
| Adherencia consistente a un esquema | Cualquier cosa que requiera información actual |
| Clasificación y extracción estrechas | Conocimiento de cola larga con una sola mención |
| Sintaxis de llamadas a herramientas y funciones | Aritmética y cálculo preciso |

La columna de la derecha es la razón de que exista la [lección 27](0027-when-not-to-fine-tune.md). Un dataset construido para instalar hechos hace aquello en lo que el fine-tuning es peor, y cada hecho necesitaría muchos ejemplos variados para fijarse, momento en el que la recuperación es más barata, más precisa y actualizable.

### Diseñar ejemplos

**Haz coincidir la distribución del despliegue.** Tus inputs de entrenamiento deben parecerse a los inputs reales. Unos prompts de entrenamiento limpios, bien formados y de longitud uniforme producen un modelo que se degrada ante la realidad desordenada que encuentra en producción, y tu partición held-out, sacada de la misma reserva limpia, no te avisará.

**Incluye los casos difíciles de forma deliberada.** Inputs ambiguos, casos límite y los casos en que la respuesta correcta es un rechazo o "información insuficiente". Si cada respuesta de entrenamiento es segura y completa, has entrenado seguridad y completitud, incluso en inputs que no las justifican.

**Sé consistente con el formato.** Si la mitad de tus ejemplos terminan con un punto y la otra mitad no, el modelo aprende la inconsistencia. Cada variación arbitraria que dejes dentro es capacidad gastada en ruido.

**Haz que las salidas sean ejemplares.** El modelo imita sus objetivos. Un dataset de respuestas adecuadas produce respuestas adecuadas, y ningún hiperparámetro se recupera de eso.

**Varía la superficie, no la sustancia.** Varias formulaciones de la misma petición enseñan robustez ante la formulación. Varios ejemplos casi idénticos enseñan memorización.

### Deduplicación

Los casi duplicados son el defecto grave más común en los datasets ensamblados, y causan dos daños a la vez: sobreponderar lo que enseñe el contenido duplicado y, si los duplicados caen a ambos lados de tu partición, una puntuación held-out que mide recuerdo en lugar de generalización.

La deduplicación por coincidencia exacta no basta. Usa hashing normalizado y luego una medida de similitud como MinHash o distancia de embeddings para los casi duplicados. Hazlo *antes* de dividir, no después.

### Tamaño y equilibrio

Una orientación aproximada, no una regla:

| Ejemplos | Objetivo realista |
|---|---|
| 50 a 200 | Estilo, tono, un formato de salida fijo |
| 500 a 2,000 | Una tarea bien definida de alcance estrecho |
| 5,000 a 50,000 | Una tarea amplia, o varias capacidades a la vez |
| 100,000+ | Rendimientos decrecientes para adapters; plantéate si la tarea es de verdad una sola tarea |

Donde existen categorías, el desequilibrio se convierte en un sesgo. Un dataset que es un 90% de una clase enseña al modelo a adivinar esa clase. O lo equilibras o tienes en cuenta el desequilibrio en tu métrica, según la lección 23.

### Datos sintéticos

Generar datos de entrenamiento con un modelo más fuerte es estándar, eficaz y tiene dos riesgos concretos.

**Errores heredados.** Los errores y sesgos del generador se convierten en tus objetivos de entrenamiento, y serán fluidos y consistentes, lo que los hace difíciles de detectar ojeando. Muestrea y lee.

**Colapso de la distribución.** Los datos generados tienden a ser más uniformes que los reales: estructuras parecidas, longitudes parecidas, registro parecido. Entrenas un modelo que maneja limpiamente una rodaja estrecha y la variación real mal. Siembra la generación con inputs reales donde puedas y varía los prompts de forma deliberada.

Además: comprueba la licencia y los términos del modelo con el que generas. Si las salidas pueden usarse para entrenar otro modelo es una restricción real, no una formalidad.

### Formato

Haz bien la mecánica, una vez:

- Renderiza a través del chat template propio del modelo (lección 3). Verifica con `repr`.
- Enmascara las posiciones del prompt salvo que quieras puntuarlas de forma deliberada.
- Incluye el token de fin de turno, o el modelo no aprenderá a detenerse.
- Revisa la distribución de longitudes de tokens y fija `max_length` a partir de su percentil alto, no de su máximo ni de una conjetura.
- Confirma que el truncamiento no corta respuestas por la mitad. Un objetivo truncado en silencio enseña al modelo a detenerse a mitad de frase.

## Práctica

1. ▢ Quieres que el modelo conozca los 400 SKUs de producto de tu empresa. ¿Es un dataset de fine-tuning la herramienta correcta?

<details markdown="1"><summary>Comprobación</summary>

No. Son hechos, que el fine-tuning instala de forma poco fiable: cada uno necesitaría muchos ejemplos variados, y el resultado es inverificable y queda obsoleto en el momento en que cambia el catálogo.

La recuperación es la herramienta correcta: precisa, citable y actualizada editando un documento en lugar de reentrenar. Lo que el fine-tuning *sí* podría enseñar de forma útil aquí es el formato para presentar la información de producto.

</details>

2. ▢ Todos tus prompts de entrenamiento son frases limpias y bien puntuadas. Los inputs de producción son escuetos y están llenos de erratas. ¿Qué ocurre, y por qué no lo detectará tu conjunto held-out?

<details markdown="1"><summary>Comprobación</summary>

El modelo rinde bien con input limpio y se degrada con input real, porque nunca vio input real.

Tu partición held-out sale de la misma reserva limpia, así que comparte el defecto. Mide el rendimiento en la distribución equivocada y reporta éxito. La solución son datos de entrenamiento y de evaluación sacados del tráfico real del despliegue.

</details>

3. ▢ ¿Por qué deduplicar antes de dividir y no después?

<details markdown="1"><summary>Comprobación</summary>

Porque una pareja de duplicados a caballo de la partición mete un ejemplo de entrenamiento en el conjunto held-out. El rendimiento held-out mide entonces memorización y la reporta como generalización, que es la forma más eficaz de engañarte sobre un fine-tune.

Deduplicar después de la partición deja intactas las parejas entre particiones, que es justo el caso que importa.

</details>

4. ▢ ¿Qué defecto del dataset es más probable que produzca un modelo que nunca dice "no lo sé"?

    - a) Un desequilibrio de clases que favorece con fuerza a una categoría
    - b) Que cada una de las respuestas sea segura y completa
    - c) Ejemplos casi duplicados que aparecen a través de la partición
    - d) Una distribución de longitudes de tokens con una cola muy larga

<details markdown="1"><summary>Comprobación</summary>

**b)** Que cada una de las respuestas sea segura y completa.

El modelo imita sus objetivos. Sin ningún ejemplo de incertidumbre apropiada o de rechazo, la seguridad y la completitud son el único comportamiento que se le ha mostrado, incluso para inputs que no las respaldan.

</details>

5. ▢ Nombra los dos riesgos de los datos sintéticos y una mitigación para cada uno.

<details markdown="1"><summary>Comprobación</summary>

Errores heredados: los errores del generador se convierten en objetivos de entrenamiento fluidos y consistentes. Mitiga muestreando y leyendo una fracción real, y validando contra la verdad de referencia donde exista alguna.

Colapso de la distribución: los datos generados son más uniformes que los reales. Mitiga sembrando la generación con inputs reales y variando de forma deliberada los prompts de generación.

</details>

6. ▢ Las longitudes de tokens de tu dataset van de 50 a 8000, con el percentil 95 en 1200. ¿Qué `max_length` fijas, y qué compruebas?

<details markdown="1"><summary>Comprobación</summary>

Alrededor de 1200 a 1500. Fijar 8000 desperdicia memoria de activaciones en padding para casi todos los ejemplos; fijar 512 trunca una fracción sustancial.

Luego comprueba qué hace realmente el truncamiento con los ejemplos por encima del límite. Si corta respuestas por la mitad estás enseñando al modelo a detenerse a mitad de frase, así que o subes el límite o descartas esos ejemplos de forma deliberada.

</details>

## Prácticas en el mundo real

- [ ] Lee veinte ejemplos de tu dataset enteros, decodificados a través del chat template. Anota cada inconsistencia que encuentres.
- [ ] Ejecuta la detección de casi duplicados sobre todo el conjunto antes de dividir. Registra cuántos encontraste y elimínalos.
- [ ] Grafica la distribución de longitudes de tokens y elige `max_length` a partir de ella. Inspecciona tres ejemplos que se truncarían.
- [ ] Mañana: añade diez ejemplos deliberadamente difíciles: ambiguos, de caso límite, o donde la respuesta correcta sea un rechazo.

## Para profundizar

- [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
- [Docs: Dataset formats, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/dataset_formats)
- [Lección 22. Contaminación y diseño held-out](0022-contamination-and-held-out-design.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
