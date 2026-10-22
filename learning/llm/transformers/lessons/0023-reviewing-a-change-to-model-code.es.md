---
title: "23. Revisar un cambio en el código de un modelo"
description: "Revisar el cambio de otra persona en el código de un modelo y nombrar qué rompe o cuánto cuesta, sin confiar en la descripción"
type: lesson
---

# Lección 23. Revisar un cambio en el código de un modelo

**Vínculo con la misión:** La misión termina en leer o modificar código real de modelos sin que la arquitectura sea una caja negra; la versión sénior de esa habilidad es revisar el cambio de otra persona en él y nombrar exactamente cuánto cuesta, en lugar de confiar en la descripción.
**Fuente principal:** [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135), cuya afirmación de exactitud (lección 22) es el modelo de esta lección para comprobar cualquier afirmación de "más rápido, salida sin cambios".
**Requisitos previos:** [0001-0003](0001-scaled-dot-product-attention.md) (atención), [0004-0011](0004-positional-encoding.md) (bloques transformer y entrenamiento), [0012](0012-reading-real-model-code.md) (leer código real), [0014, 0017](0014-rotary-position-embeddings.md) (variantes modernas), [0022](0022-mixture-of-experts-and-flashattention.md) (exactitud)

## Calentamiento

1. ▢ Una pull request afirma "se sustituyó la atención lenta por atención rápida, salida sin cambios". ¿Qué compruebas primero antes de confiar en esa afirmación?

<details markdown="1"><summary>Comprobación</summary>

Si la salida coincide realmente, numéricamente, con la original, dentro de la tolerancia de coma flotante. "Más rápido" a menudo significa en silencio "distinto": un cálculo simplificado o una aproximación que es ligeramente incorrecta. La lección 22 hizo de la exactitud la prueba específicamente para FlashAttention porque este error es común.

</details>

2. ▢ Un diff cambia la codificación posicional de sinusoidal a rotatoria. ¿Puedes detectar qué cuesta realmente el cambio sin leer el paper?

<details markdown="1"><summary>Comprobación</summary>

Puedes derivar qué hacen las codificaciones rotatorias a partir de la lección 14: rotan los vectores query y key antes de que corra la atención, que es como logran productos escalares relativos a la posición. Entonces puedes comprobar si el diff implementa esa rotación correctamente, y probar si las salidas coinciden con una referencia (la ecuación de la lección 0001).

</details>

3. ▢ Un cambio afirma una ablación: "quitamos el término de weight decay y el entrenamiento sigue convergiendo". ¿Qué pregunta haces?

<details markdown="1"><summary>Comprobación</summary>

¿Lo midió el autor? ¿La afirmación se respalda en su propia ejecución de entrenamiento, o se repite a partir del resumen de un paper en una entrada de blog? Una afirmación de ablación es tan sólida como la medición que hay detrás.

</details>

## Qué debes saber

### La lista de revisión: cuatro cosas que necesita todo cambio en el código de un modelo

Un revisor que ha construido un transformer a partir de tensores en bruto tiene una ventaja de la que carecen la mayoría de los revisores de código: puede contrastar una afirmación con la matemática real, y no solo con si el código parece plausible.

**1. ¿Se mantienen correctamente los shapes de principio a fin?**

La convención recurrente de este espacio de trabajo: cada operación conserva la longitud de secuencia y la dimensión de embedding. Un cambio en la atención (la máscara de la lección 3, RoPE de la lección 14, la grouped-query de la lección 17) no debe romper eso. Comprueba:

- Entrada a la operación: shape `(batch, seq_len, d_model)` o componentes como `(batch, num_heads, seq_len, d_k)`.
- Salida: el mismo shape.
- Dos capas más abajo, ¿se esconde un error que rompe el shape? Un embedding rotatorio que rota por el ángulo equivocado puede no fallar hasta que los productos escalares de la atención se vuelven un sinsentido. Comprueba las pruebas posteriores o ejecuta el modelo hacia delante con una entrada conocida y verifica los shapes intermedios.

**2. Si se afirma una mejora de velocidad, ¿coincide numéricamente la salida?**

La lección 22 insistió en esto: FlashAttention es exacta, no aproximada. Calcula la ecuación idéntica, solo que tocando la memoria de otra manera. **Debe** producir el mismo `output` dentro de la tolerancia de coma flotante.

Cuando un diff afirma más rápido sin cambiar la salida:

- Ejecuta el modelo con el código viejo y con el nuevo sobre la misma entrada aleatoria. Extrae las salidas de la atención (o el forward pass completo si el diff está aguas arriba de eso).
- Compara las salidas elemento a elemento. Deben coincidir dentro del redondeo de coma flotante, típicamente de 1e-5 a 1e-4 según la precisión. Si difieren más que eso, el cambio no es una aceleración transparente; es un cálculo distinto que afirma ser el mismo.

**3. ¿Está justificado el cambio frente a lo que sustituye?**

Las lecciones 5 (layer norm, residuales) y 19 (inicialización, warmup, gradient clipping, precisión mixta) son salvaguardas: cada una protege de algo en lo que el bucle de entrenamiento puede fallar sin ella. Un cambio en cualquiera de ellas debe justificar por qué la nueva protección es suficiente.

Ejemplos:

- "Sustituimos la layer norm por RMSNorm": RMSNorm elimina el recentrado. ¿Muestra el código que se sigue usando como pre-norm (lección 5), donde el centrado ya era opcional?
- "Subimos el calendario del learning rate": ¿tiene el cambio en cuenta de qué protegían el warmup, el gradient clipping y la precisión mixta?
- "Quitamos el gradient clipping": ¿estabas recortando realmente antes? ¿Estás preparado para ver loss spikes o inestabilidad del entrenamiento ahora?

Un error común: copiar un valor de configuración de un modelo sin relación y no ajustar nada más. "Nuestro modelo tiene 7B de parámetros; usaré el learning rate de un modelo de 70B que encontré". Esa tasa se eligió para 70B; el contexto, el batch size y la curvatura de la pérdida son todos distintos.

El cambio justificado explica el propósito de la salvaguarda antigua y por qué la nueva configuración no la necesita, o muestra una medición de que el bucle de entrenamiento sobrevive sin ella.

**4. ¿Está respaldada por una medición real una afirmación de ablación?**

De nuevo la lección 22: "FlashAttention produce una salida idéntica" es una afirmación que puedes verificar comparando salidas. Pero "quitamos el weight decay y el entrenamiento es igual de bueno" es distinto: es un resultado experimental que afirma que el componente eliminado no importaba.

Comprueba:

- ¿Es el autor del cambio quien lo midió? ¿Medido con qué dataset, con qué semilla aleatoria, durante cuántos pasos?
- ¿O la afirmación se repite a partir del resumen de un paper, una entrada de blog o el experimento de otra persona? Si es así, ¿coincide el nuevo contexto (el tamaño de tu modelo, la arquitectura, el learning rate, el batch size, el dataset) con la medición original?

Aceptar una ablación real por autoridad de segunda mano es arriesgado, sobre todo si la nueva ejecución de entrenamiento es cara y el fallo es costoso.

### Cómo suena el buen criterio

Al revisar un cambio en el código de un modelo, una ingeniera sénior nombra con precisión qué cuesta o arriesga una elección, en lugar de confiar en la descripción.

**En lugar de:** "Esto me parece mal."

**Mejor:** "La lección 14 deriva que RoPE rota Q y K por un ángulo proporcional a `position * dimension_index`. Este diff rota por `position * constant`. Eso es una función distinta. La propiedad de posición relativa del paper no se cumplirá. Querría ver que las salidas coinciden con una referencia antes de hacer el merge."

**En lugar de:** "Debería funcionar."

**Mejor:** "El cambio mueve la layer norm de `x + Sublayer(LayerNorm(x))` a `LayerNorm(x + Sublayer(x))`, lo que pasa el bloque de pre-norm a post-norm. La lección 5 mostró que pre-norm deja limpio el camino residual a lo largo de toda la red, y por eso entrena de forma más estable en pilas profundas. Querría ver las normas de los gradientes en cada capa durante el entrenamiento, o entender por qué este modelo concreto se mantiene estable con post-norm."

**En lugar de:** "Los autores dicen que funciona."

**Mejor:** "Esto es RMSNorm, que el paper aplica en pre-norm. Nuestro código usa post-norm (lección 5). RMSNorm sin recentrado puede estar bien en pre-norm pero ser arriesgada en post-norm. Querría o bien cambiar a pre-norm o bien comparar las salidas con cuidado."

La diferencia: nombrar qué hace el cambio, de qué protege o cuánto cuesta, y qué evidencia resolvería la cuestión, en lugar de decir que el cambio parece bien o mal.

## Práctica

1. ▢ Un diff sustituye la codificación posicional sinusoidal (lección 4) por la rotatoria (lección 14). Tus comprobaciones: ¿qué shapes deben seguir coincidiendo, y qué pruebas primero?

<details markdown="1"><summary>Comprobación</summary>

Shapes: entrada `(batch, seq_len, d_model)`, salida `(batch, seq_len, d_model)`. La rotación se aplica a Q y K antes de la atención, así que los shapes de entrada de la atención no cambian, y el shape de salida de la atención sigue siendo `(batch, seq_len, d_model)`.

Prueba primero: compara las salidas de la atención (o las del forward pass completo si puedes aislarlas con limpieza) entre el código viejo y el nuevo sobre la misma entrada aleatoria. Si coinciden dentro de la tolerancia, el cambio conserva el cálculo. Si difieren, algo falla en la matemática de la rotación.

</details>

2. ▢ Un cambio afirma "multi-head attention → grouped-query attention (lección 17), sin diferencia en la salida". ¿Cuál es tu primera pregunta escéptica?

<details markdown="1"><summary>Comprobación</summary>

La grouped-query attention tiene menos heads de key y de value que de query, así que el cálculo es genuinamente distinto, aunque esté diseñado para aproximar la salida de la multi-head. La afirmación "sin diferencia en la salida" es *demasiado fuerte*. La afirmación correcta es "la salida es lo bastante cercana como para que el rendimiento posterior no sufra".

Tu comprobación: ¿coinciden numéricamente las salidas dentro de una tolerancia que estés dispuesto a aceptar? Probablemente 1e-4 o más estricta. Si coinciden exactamente, probablemente algo va mal (puede que hayas dejado activo por accidente código multi-head en algún sitio).

</details>

3. ▢ Una PR elimina el warmup del learning rate (lección 19). El autor dice "el modelo entrena bien sin él". ¿Qué preguntas?

<details markdown="1"><summary>Comprobación</summary>

- ¿Lo midieron? ¿Con este modelo, este dataset y este batch size?
- ¿Cuál era el learning rate antes de que empezara el warmup? Si la tasa inicial es ahora menor, puede que el cambio no esté quitando realmente el beneficio del warmup.
- ¿Vieron picos de gradiente, capas muertas o curvas de pérdida inusuales? El warmup los previene. Si el autor no miró, puede que no los notara.

Sin una medición en tu configuración real, estás adivinando. El warmup es barato; si funciona, consérvalo.

</details>

4. ▢ ¿Qué afirmación sobre revisar un cambio en el código de un modelo es la pauta más útil?

    - a) Confiar en la descripción del autor y centrarse en cambio en el estilo del código
    - b) Rechazar cualquier cambio en la atención o en el bucle de entrenamiento; son demasiado arriesgados para modificarlos
    - c) Comparar las salidas numéricamente cuando el cambio afirma que no altera la salida, y nombrar el costo concreto cuando sí lo hace
    - d) Exigir que cada resultado de ablación esté respaldado por un paper publicado antes de aceptarlo

<details markdown="1"><summary>Comprobación</summary>

**c)** Comparar las salidas numéricamente cuando el cambio afirma que no altera la salida, y nombrar el costo concreto cuando sí lo hace.

(a) es como se cuelan los errores. (b) es demasiado cauta; todo el sentido es poder juzgar los cambios con cuidado. (d) es demasiado estricta; un cambio útil puede llegar antes de su publicación, y una medición en tu configuración real suele ser más relevante que la medición de un paper a otra escala.

</details>

5. ▢ Un diff cambia la colocación de RMSNorm (lección 15) de post-norm a pre-norm (lección 5). ¿Qué verificas antes de confiar en el cambio?

<details markdown="1"><summary>Pista</summary>

Piensa en para qué sirve cada colocación según la lección 5, y qué elimina RMSNorm en comparación con la layer norm.

</details>

<details markdown="1"><summary>Comprobación</summary>

La RMSNorm en pre-norm funciona porque RMSNorm solo reescala (no recentra), y la pre-norm no necesita recentrado para evitar la hinchazón de las activaciones: el residual hacia el siguiente bloque no tiene cota, pero la normalización de *ese* bloque se ocupa de ello.

La post-norm es distinta: la salida residual no tiene cota, y el recentrado de la layer norm era en parte la razón de que la post-norm se mantuviera estable. RMSNorm elimina el recentrado. Querrías comparar histogramas de activaciones (¿se están hinchando?), curvas de entrenamiento (¿muestran inestabilidad?), o al menos ejecutar una prueba rápida para ver si las curvas de pérdida coinciden antes y después del cambio.

</details>

## Prácticas en el mundo real

- [ ] La próxima vez que veas una PR que cambie la atención, la codificación posicional o el bucle de entrenamiento en un modelo con el que trabajes o que entiendas, usa la lista de cuatro puntos de arriba: shapes, exactitud de la salida, justificación frente a lo que sustituye, y medición que respalde cualquier afirmación de ablación.
- [ ] En esa misma PR (o en la tuya), practica escribir un comentario de revisión que nombre con precisión qué hace un cambio y qué resolvería la cuestión, en lugar de decir que parece bien o mal.
- [ ] Mañana: si modificas esta semana tu propio código de modelo (cambiar una capa, intercambiar una activación, ajustar un calendario), comprueba si puedes verificar numéricamente los shapes y las salidas antes de enviarlo. Si no puedes, en realidad no sabes si cambiaste algo importante o nada en absoluto.
- [ ] Mañana: revisa una afirmación que hayas oído sobre la atención, los embeddings o un truco de entrenamiento. Ve al paper original (no al resumen de la entrada de blog) y comprueba si la afirmación coincide con las ecuaciones reales del paper. La lección 12 mostró cómo encontrar código real; ahora usa esa habilidad y los papers de [Recursos](../RESOURCES.md) para resolver un punto en disputa.

## Para profundizar

- [Paper: "RoFormer: Enhanced Transformer with Rotary Position Embedding"](https://arxiv.org/abs/2104.09864), Su et al. Úsalo para: la matemática original de los embeddings rotatorios, para contrastar afirmaciones con lo que el paper dice realmente.
- [Paper: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"](https://arxiv.org/abs/2305.13245), Ainslie et al. Úsalo para: el diseño de la grouped-query attention, para comprobar la afirmación de aproximación y entender qué contrapartida hace.
- [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://arxiv.org/abs/2205.14135), Dao et al. Úsalo para: confirmar que FlashAttention es exacta, no aproximada, y ver cómo la verifican frente a implementaciones de referencia.
- Vuelve a las [lecciones del bucle de entrenamiento](0019-initialization-warmup-and-gradient-clipping.md) cuando revises cambios en el learning rate, el gradient clipping o la precisión mixta. Las secciones "Para profundizar" de esas lecciones enlazan a los papers que hay detrás de cada salvaguarda.
- [Glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
