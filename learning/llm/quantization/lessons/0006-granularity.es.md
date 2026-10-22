---
title: "6. Granularidad"
description: "Scales per-tensor, per-channel y per-group, y qué cuesta cada uno en bits almacenados"
type: lesson
---

# Lección 6. Granularidad

**Vínculo con la misión:** Predecir el error de un tensor cuantizado significa también saber cuántos valores comparten cada scale, porque un scale lo fija el mayor valor de su grupo y cada scale extra cuesta bits almacenados.
**Fuente principal:** [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), secciones 2.2.3 y 2.4.2
**Requisitos previos:** [Lección 5](0005-choosing-the-range.md), [Granularidad](../GLOSSARY.md), [Tamaño de grupo](../GLOSSARY.md), [Bits efectivos por peso](../GLOSSARY.md)

## Calentamiento

1. ▢ Con la fijación de rango min-max, ¿qué decide el scale de un cuantizador, y qué le hace un outlier?

<details markdown="1"><summary>Comprobación</summary>

El rango, que fijan los valores mayor y menor, dividido por el número de pasos. Un outlier ensancha el rango, así que el scale crece y el paso se vuelve más grueso para todos los demás valores, lo que puede redondear a cero a la mayoría (lección 5).

</details>

2. ▢ Un esquema de 4 bits almacena un scale de 16 bits por grupo de 32 pesos. ¿Cuántos son sus bits efectivos por peso?

<details markdown="1"><summary>Comprobación</summary>

4.5. El scale añade 16 / 32 = 0.5 bits por peso a los 4 bits de cada valor (lección 1).

</details>

3. ▢ ¿Por qué una rejilla simétrica solo necesita un scale, y cuál es el costo de prescindir del zero-point?

<details markdown="1"><summary>Comprobación</summary>

La cuantización simétrica fija el zero-point en cero, así que no hay nada más que almacenar. El costo es que la rejilla queda centrada en cero, así que un tensor de un solo lado desperdicia los niveles del lado vacío (lección 4).

</details>

## Qué debes saber

### Qué comparte un scale

La **granularidad** es cuántos valores comparten un scale y un zero-point. Un conjunto pequeño que comparte scale implica un rango pequeño, así que un outlier solo arruina el conjunto en el que está. El costo es que cada conjunto necesita su propio scale almacenado.

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel et al. señalan que la cuantización per-tensor es la estándar porque todo acelerador de punto fijo la soporta, y que la cuantización per-channel de los pesos ayuda más cuando la distribución de pesos varía mucho de un canal a otro. También describen aplicar un cuantizador por grupo de pesos o de activaciones, y dicen que los grupos más finos suelen mejorar el accuracy a costa de una sobrecarga adicional.

### Por qué per-channel funciona para los pesos y no para las activaciones

Una capa lineal calcula cada salida como una suma sobre las features de entrada. Con los valores cuantizados escritos como scale por entero, los scales solo pueden salir de la suma si son constantes a lo largo de ella:

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

El paréntesis es un producto punto puramente entero, que es lo que acelera el hardware, y los dos scales multiplican el resultado una sola vez al final. Un scale de pesos por canal de salida `s_w[i]` es constante a lo largo de la suma, porque `i` nombra la salida y `k` es lo que se suma. Nagel et al. concluyen que la cuantización de pesos per-channel puede aplicarse con un scale separado por canal, sin reescalar el acumulador.

Un scale de activaciones por canal de entrada sería `s_x[k]`, que cambia con el índice sumado. No puede salir de la suma, y Nagel et al. dicen que "requeriría por tanto reescalar el acumulador para cada canal de entrada". La cuantización de activaciones per-channel es mucho más difícil de implementar por esa razón. Un scale de activaciones por token, uno por cada fila de `X`, es constante a lo largo de la suma para un token dado y no cuesta nada: [Dettmers et al.](https://arxiv.org/abs/2208.07339) usan exactamente esto en su cuantización vector-wise, una constante por fila de las activaciones y una por columna de los pesos, y deshacen ambas con el producto externo de las constantes. La lección 7 muestra por qué eso no basta para los LLM: los outliers están en las dimensiones de features, que es el eje que un scale por token no separa.

La cuantización per-group tiene el mismo problema para el acumulador entero, ya que el scale cambia dentro de la suma. El límite del acumulador en el paper es la razón por la que Nagel et al. dejan fuera los scales de grupo. En los esquemas de solo pesos, los pesos se descuantizan a 16 bits dentro del kernel y se multiplican en 16 bits (ver [cuantización solo de pesos](../GLOSSARY.md)), así que ningún acumulador entero carga scales mezclados y un scale de grupo puede variar libremente.

### Qué cuestan los scales

Cada grupo añade su scale, y cualquier zero-point, al checkpoint. Los **bits efectivos por peso** son el ancho de bits del valor más los metadatos repartidos sobre el grupo:

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| Tamaño de grupo | Sobrecarga con un scale de 16 bits | Bits efectivos para pesos de 4 bits |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

Per-channel es simplemente un grupo cuyo tamaño es la longitud de la fila, y per-tensor es un grupo de todos los pesos: ambos cuestan casi nada. La cifra de la lección 1 para el grupo 32 es la última fila.

### Qué compran los grupos pequeños

El experimento de la práctica cuantiza a 4 bits una matriz sintética de pesos, con filas de scales distintos y colas pesadas. El error baja de forma constante a medida que los grupos se hacen más pequeños, y per-tensor es con mucho el peor. Un grupo de 64 tiene solo 64 oportunidades de contener un outlier, y el outlier afecta solo a esos 64 valores.

El mayor estudio empírico de esto es el de [Dettmers y Zettlemoyer](https://arxiv.org/abs/2212.09720): más de 35,000 experimentos zero-shot con 3 a 8 bits en LLM de 19M a 176B parámetros. Encuentran que es difícil mejorar siquiera el intercambio entre el tamaño del modelo en bits y el accuracy, y que solo dos cosas ayudan: un tamaño de bloque pequeño (su término para el tamaño de grupo) y el tipo de datos. Para los modelos Pythia de 4 bits, pasar de un tamaño de bloque de 1024 a 64 añade 0.24 bits por parámetro y mejora el accuracy zero-shot casi tanto como pasar de 4 a 5 bits. Una constante de 16 bits por bloque cuesta 16 / 64 - 16 / 1024 = 0.23 bits, cerca de la cifra del paper. Los grupos pequeños son los bits baratos.

## Práctica

1. ▢ Un esquema de 4 bits almacena un scale de 16 bits y un zero-point de 4 bits por grupo de 64 pesos. ¿Cuántos son sus bits efectivos por peso?

<details markdown="1"><summary>Comprobación</summary>

4 + (16 + 4) / 64 = 4.3125, unos 4.31. El zero-point añade 4 / 64 = 0.0625 sobre los 0.25 del scale. Un esquema simétrico prescindiría de esos 0.0625 y quedaría en 4.25.

</details>

2. ▢ ¿Qué hace que un scale de pesos por canal de salida sea compatible con una multiplicación de matrices entera mientras que un scale de activaciones por canal de entrada no lo es?

    - a) El scale de pesos cabe en solo ocho bits
    - b) El scale de pesos necesita un término de desplazamiento aparte
    - c) El scale de pesos es constante a lo largo de la suma
    - d) El scale de pesos cambia de valor entre canales de salida

<details markdown="1"><summary>Comprobación</summary>

**c)** El scale de la salida `i` multiplica toda la suma sobre `k`, así que sale de la suma y se aplica una sola vez tras la acumulación entera. Un scale de activaciones indexado por canal de entrada cambia dentro de la suma, así que el acumulador necesitaría reescalarse en cada canal de entrada. (a) trata del almacenamiento y no decide dónde puede aplicarse un scale. (b) confunde un scale con un zero-point, y los pesos simétricos no necesitan ninguno. (d) es cierta pero es la razón de que haya muchos scales, no la razón de que puedan sacarse factor común.

</details>

3. ▢ Predice y luego ejecuta. Antes de ejecutar, ordena per-tensor, per-channel y los tamaños de grupo por error, del peor al mejor, y di si el error baja de forma constante. Luego calcula los bits efectivos del grupo 32.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>Pista</summary>

Cada paso hacia abajo en el tamaño de grupo significa más scales, y cada scale lo fija un conjunto más pequeño de valores. Luego pregúntate qué hace un scale per-tensor con una matriz cuyas filas difieren en tamaño.

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

El error baja en cada paso: per-tensor deja un error de cerca del 70 por ciento de la energía de la propia señal, per-channel elimina la mayor parte dando a cada fila su propio scale, y cada vez que se divide el grupo a la mitad el error baja en cerca de un tercio. El grupo 32 cuesta 4.5 bits efectivos. Los datos son sintéticos, así que lee el orden y las razones aproximadas, no los números absolutos.

</details>

4. ▢ Pasar del tamaño de grupo 1024 a 64 añade cuántos bits por peso con un scale de 16 bits? Compáralo con el costo de pasar los pesos de 4 a 5 bits, y di qué encontraron Dettmers y Zettlemoyer sobre los beneficios.

<details markdown="1"><summary>Comprobación</summary>

16 / 64 - 16 / 1024 = 0.234 bits, frente a 1 bit entero para pesos de 5 bits. En el paper, el tamaño de bloque más pequeño mejoró el accuracy zero-shot de los modelos Pythia de 4 bits casi tanto como lo habría hecho el bit extra. Así que reducir el grupo es una manera mucho más barata de comprar accuracy que añadir un bit a cada peso. El resultado principal del paper es que 4 bits es casi universalmente lo óptimo para el total de bits del modelo y el accuracy zero-shot.

</details>

5. ▢ Un equipo cuantiza las activaciones a 8 bits con un scale por token y aun así pierde accuracy, porque una dimensión de features es enorme en todos los tokens. ¿Por qué no ayuda el scale por token, y qué eje separaría el outlier?

<details markdown="1"><summary>Comprobación</summary>

El scale de cada token lo fija el mayor valor de ese token, y la dimensión de features enorme es la mayor en casi todos los tokens, así que el scale de cada fila se infla de la misma manera. Dettmers et al. hacen este mismo argumento: la cuantización row-wise y vector-wise escalan la dimensión de la secuencia, y los outliers están en la dimensión de features, así que ambas fallan al aislarlos. Solo un scale por dimensión de features separaría el outlier, y ese es el scale de activaciones por canal de entrada de esta lección, que una multiplicación de matrices entera no puede aplicar de forma barata.

</details>

## Prácticas en el mundo real

- [ ] En el experimento, cambia `0.7` en `rng.lognormal(0.0, 0.7, ...)` por `0.0`, de modo que todas las filas tengan el mismo scale, y vuelve a ejecutar. Anota cuánto de la ventaja de per-channel sobre per-tensor se mantiene, y explícalo.
- [ ] Abre la model card o la configuración de cualquier checkpoint de GPTQ o AWQ de 4 bits en el Hugging Face Hub, encuentra su tamaño de grupo, y calcula sus bits efectivos por peso y el tamaño de su checkpoint para el número de parámetros del modelo.
- [ ] Mañana: sin apuntes, reconstruye la tabla de tamaños de grupo frente a bits efectivos para un scale de 16 bits y para uno de 8 bits, y di en una frase por qué los scales de pesos por canal encajan en un matmul entero y los scales de activaciones por canal no.

## Para profundizar

- [El mapeo de cuantización](../reference/quantization-mapping.md)
- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Paper: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
