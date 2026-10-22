---
title: "2. Formatos de punto flotante"
description: "Cómo los bits de signo, exponente y mantisa reparten rango y precisión en fp32, fp16 y bf16"
type: lesson
---

# Lección 2. Formatos de punto flotante

**Vínculo con la misión:** Todo formato numérico posterior de este track es una elección de cómo repartir unos pocos bits entre rango y precisión, así que necesitas leer una disposición de bits y decir qué puede y qué no puede contener antes de poder juzgar qué perdió un modelo cuantizado.
**Fuente principal:** [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
**Requisitos previos:** [Lección 1](0001-what-quantization-buys.md), [Bits de exponente](../GLOSSARY.md), [Bits de mantisa](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Cuántos bytes por parámetro usan fp32, bf16 e int8, y cuánta memoria ocupan los pesos de un modelo de 7B parámetros en cada uno?

<details markdown="1"><summary>Comprobación</summary>

fp32 usa 4 bytes (28 GB), bf16 usa 2 bytes (14 GB) e int8 usa 1 byte (7 GB). Solo los pesos, con el ancho de bits nominal.

</details>

2. ▢ ¿Por qué un formato de pesos más pequeño suele acelerar el decode con lote 1?

<details markdown="1"><summary>Comprobación</summary>

El decode con tamaño de lote 1 está limitado por el ancho de banda de memoria: cada peso se lee una vez por token y se usa para muy poca aritmética, así que menos bytes por peso significa menos que leer. La cuantización solo de pesos no hace más rápida la aritmética en sí.

</details>

## Qué debes saber

### Tres campos

Un número de punto flotante almacena un bit de signo, algunos **bits de exponente** y algunos **bits de mantisa**. Para un valor normal, el campo de exponente `e` y el campo de mantisa `m` dan

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

donde `M` es el número de bits de mantisa y `bias` es un desplazamiento fijo que permite que el exponente sea negativo. El exponente elige cerca de qué potencia de dos está el valor. La mantisa elige uno de los 2^M puntos igualmente espaciados entre esa potencia de dos y la siguiente. Un campo de exponente todo en ceros se reserva para el cero y para los valores subnormales, que son menores que el menor valor normal y llenan el hueco hasta el cero con el mismo espaciado. Un campo de exponente todo en unos se reserva en los formatos IEEE para el infinito y el NaN.

| Formato | Bits totales | Signo / exponente / mantisa | Bias | Mayor valor finito | Menor valor normal | Épsilon de máquina |
|---|---|---|---|---|---|---|
| fp32 | 32 | 1 / 8 / 23 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-23, unos 1.2 × 10^-7 |
| fp16 | 16 | 1 / 5 / 10 | 15 | 65,504 | 6.1 × 10^-5 | 2^-10, unos 9.8 × 10^-4 |
| bf16 | 16 | 1 / 8 / 7 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-7, unos 7.8 × 10^-3 |

El 65,504 es el que dan Micikevicius et al. como el mayor valor que puede representar fp16 ([Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)). El resto se deduce de las disposiciones. El **épsilon de máquina** es la distancia entre 1 y el siguiente valor por encima de él, que es 2^-M.

Dos consecuencias importan para el resto del track. Primero, fp16 y bf16 ocupan ambos 2 bytes, así que elegir entre ellos no cambia nada de la memoria. Es una elección entre tres bits más de mantisa y tres bits más de exponente. Segundo, bf16 es fp32 sin los 16 bits inferiores: los mismos campos de signo y exponente y los 7 bits superiores de la mantisa. Kalamkar et al. dan esto como la razón por la que bf16 resulta atractivo: su rango es el mismo que el de fp32 y la conversión desde y hacia fp32 es sencilla.

### Rango y precisión son cosas distintas

El exponente fija el **rango**, el intervalo entre el menor y el mayor valor. La mantisa fija la **precisión**, lo cerca que el formato puede aproximar un valor dentro de ese intervalo. Son independientes, y cada bit extra en uno es un bit quitado al otro.

El espaciado no es constante. Entre 2^k y 2^(k+1) los valores vecinos están separados 2^(k-M), así que la distancia se duplica en cada potencia de dos mientras la distancia relativa se mantiene en torno a 2^-M. En fp16, los valores justo por encima de 1 están separados unos 0.001, los valores justo por encima de 1024 están separados exactamente 1, y justo por encima de 2048 están separados 2. De esto se siguen dos cosas. Una suma cuyo resultado cae más cerca de un valor existente que de un punto medio se redondea de vuelta, así que `1 + 0.0004` en fp16 sigue siendo 1, y una suma acumulada de unos en fp16 deja de crecer en 2048. Y un valor redondeado se equivoca como mucho en la mitad del espaciado local, el **error de redondeo** que la cuantización siempre añade.

### Por qué fp16 necesitaba escalado de la pérdida y bf16 no

Los 5 bits de exponente de fp16 lo hacen estrecho. El menor valor positivo que puede almacenar es 2^-24, y todo lo menor se vuelve cero. Micikevicius et al. midieron los valores de gradientes de una ejecución de entrenamiento y encontraron que cerca del 5% de los valores de gradientes de pesos tenían exponentes por debajo de -24, que se perderían. Su solución es el **escalado de la pérdida**: multiplicar la pérdida por una constante antes de la backpropagation, de modo que todos los gradientes se escalen hacia arriba hasta entrar en el rango de fp16, y dividir ese scale antes de la actualización de los pesos. Eligen el factor de modo que su producto con el mayor gradiente absoluto se mantenga por debajo de 65,504, porque un desbordamiento produce infinitos y NaN que dañan los pesos.

bf16 tiene los 8 bits de exponente de fp32, así que los mismos gradientes son representables. Kalamkar et al. afirman que conservar el rango de fp32 significa que no hace falta ajustar hiperparámetros para converger, y que fp16 sí lo requiere. Su emulación pone a cero los 16 bits inferiores de un valor fp32, y comparan round-to-nearest con el truncamiento directo al convertir. En uno de sus experimentos round-to-nearest igualó el accuracy del baseline en fp32 mientras que el truncamiento perdió cerca de un 0.02%. El precio de bf16 es la mantisa de 7 bits: los valores están separados solo un 0.8% en términos relativos.

Para este track la lección es el propio intercambio. Los formatos cuantizados de 8 bits o menos hacen el mismo intercambio de forma mucho más dura, y por eso la lección 4 añade un scale.

## Práctica

1. ▢ ¿Qué afirmación compara correctamente fp16 y bf16?

    - a) fp16 tiene más bits de exponente, así que más rango
    - b) bf16 tiene más bits de exponente, así que más rango
    - c) bf16 tiene más bits de mantisa, así que un espaciado más fino
    - d) fp16 y bf16 difieren en el número total de bits

<details markdown="1"><summary>Comprobación</summary>

**b)** bf16 gasta 8 bits en el exponente frente a los 5 de fp16, lo que le da el rango de fp32, y tiene 7 bits de mantisa frente a los 10 de fp16. (a) intercambia los dos formatos. (c) los intercambia al revés: fp16 es el que tiene el espaciado más fino. (d) es incorrecta porque ambos son de 16 bits, así que la memoria no los distingue.

</details>

2. ▢ Predice y luego ejecuta. ¿Qué imprime cada línea?

    ```python
    import numpy as np

    with np.errstate(over="ignore"):
        print(float(np.float16(65504)), float(np.float16(65519)))
        print(float(np.float16(65520)), float(np.float16(70000)))
    ```

<details markdown="1"><summary>Pista</summary>

65,504 es el mayor valor finito de fp16, y el siguiente valor hacia arriba sería 65,536. ¿Dónde está el punto medio, y hacia dónde se redondea un número por encima de él?

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
65504.0 65504.0
inf inf
```

65,519 está por debajo del punto medio entre 65,504 y 65,536, así que se redondea hacia abajo a 65,504. Desde 65,520 hacia arriba el valor se redondea más allá del mayor número finito y se convierte en infinito, que en el entrenamiento es como empieza un desbordamiento de gradientes. La línea de `errstate` solo silencia la advertencia de NumPy al respecto.

</details>

3. ▢ Predice y luego ejecuta. ¿Cuáles de las tres sumas dan exactamente 1?

    ```python
    import numpy as np

    one = np.float16(1)
    for d in (0.0004, 0.0005, 0.001):
        print(d, float(one + np.float16(d)))
    ```

<details markdown="1"><summary>Pista</summary>

La distancia por encima de 1 en fp16 es 2^-10, unos 0.000977. Una suma va al vecino que esté más cerca.

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
0.0004 1.0
0.0005 1.0009765625
0.001 1.0009765625
```

Solo la primera. Los vecinos de 1 son 1 y 1.0009765625, y el punto medio es de unos 1.000488. 0.0004 cae por debajo y se pierde por completo, mientras que 0.0005 salta hacia arriba un 2^-10 entero. Un valor sumado a otro mayor no es "un poco inexacto": por debajo de la mitad del espaciado local desaparece.

</details>

4. ▢ Predice y luego ejecuta. ¿Qué imprime esto, y qué dice sobre sumar muchos números pequeños en fp16?

    ```python
    import numpy as np

    total = np.float16(0)
    for _ in range(3000):
        total = total + np.float16(1)
    print(float(total))
    ```

<details markdown="1"><summary>Pista</summary>

Por encima de 2048 el espaciado de fp16 es 2. ¿Qué pasa con 2048 + 1?

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
2048.0
```

En 2048 el espaciado es 2, así que 2049 queda exactamente a medio camino entre dos valores representables y se redondea al par, 2048. La suma se queda entonces ahí durante las 952 sumas restantes. Por eso Micikevicius et al. acumulan los productos de fp16 en fp32 y no en fp16.

</details>

5. ▢ Predice y luego ejecuta. bf16 es fp32 sin los 16 bits inferiores. Antes de ejecutar, di cuáles de los tres primeros valores sobreviven sin cambios a la conversión, y qué pasa con 1e38 en fp16.

    ```python
    import numpy as np

    def to_bf16(x):
        bits = np.asarray(x, dtype=np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
        return bits.view(np.float32)

    x = np.array([1 + 2**-7, 1 + 2**-8, 3.14159265, 1e38], dtype=np.float32)
    print([float(v) for v in to_bf16(x)])
    with np.errstate(over="ignore"):
        print(float(np.float16(1e38)))
    ```

<details markdown="1"><summary>Pista</summary>

bf16 conserva 7 bits de mantisa, así que 1 + 2^-7 es el primer valor por encima de 1 que puede contener. ¿Cuánto es 1 + 2^-8?

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
[1.0078125, 1.0, 3.140625, 9.969209968386869e+37]
inf
```

1 + 2^-7 sobrevive, 1 + 2^-8 se trunca a exactamente 1, y pi pasa a ser 3.140625, correcto hasta unos tres dígitos. 1e38 sigue siendo finito, unos 9.97e37 porque se recorta la mantisa, pero fp16 lo convierte en infinito. Esta función trunca, como describen Kalamkar et al. que hace su emulación, que comparan con el redondeo al más cercano.

</details>

6. ▢ Un compañero entrena en fp16 y ve que la pérdida se vuelve NaN tras unos cientos de pasos, y propone cambiar a bf16. Explica qué es probable que esté pasando, qué hace el escalado de la pérdida al respecto y qué cambiaría bf16.

<details markdown="1"><summary>Comprobación</summary>

fp16 llega como máximo a 65,504, así que una pérdida escalada o un gradiente grande pueden desbordarse a infinito y NaN, y los gradientes pequeños por debajo de 2^-24 se vuelven cero. El escalado de la pérdida elige una constante para que los gradientes caigan dentro del rango de fp16, y el scale se divide antes de la actualización de los pesos. bf16 tiene el rango de exponente de fp32, así que ninguno de los dos problemas aparece y no hace falta scale, a costa de una mantisa más gruesa. Cambiar es una solución sensata solo si el NaN es de verdad un problema de rango. Un NaN causado por un learning rate malo o por un batch malo sobrevive al cambio.

</details>

## Prácticas en el mundo real

- [ ] En una sesión de Python con NumPy, imprime `np.finfo(np.float16)` y `np.finfo(np.float32)` y encuentra `max`, `tiny` y `eps` en ellos. Compara cada uno con la tabla de arriba.
- [ ] Abre el `config.json` de cualquier modelo abierto del Hugging Face Hub y lee su `torch_dtype`. Di qué rango y qué espaciado implica esa elección.
- [ ] Mañana: sin apuntes, escribe los conteos de bits de signo, exponente y mantisa de fp32, fp16 y bf16, y di cuál de los tres tiene el rango más amplio y cuál el espaciado más fino.

## Para profundizar

- [Formatos numéricos](../reference/number-formats.md)
- [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
- [Paper: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740), secciones 3.1 y 3.2 para la copia maestra de los pesos y el escalado de la pérdida
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
