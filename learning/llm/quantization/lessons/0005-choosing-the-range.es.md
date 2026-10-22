---
title: "5. Elegir el rango"
description: "Por qué recortar el rango cambia un poco de error de recorte por mucho menos error de redondeo"
type: lesson
---

# Lección 5. Elegir el rango

**Vínculo con la misión:** Predecir de dónde viene un error de cuantización significa saber cuál de sus dos partes agranda un rango de recorte dado, y el rango es la elección que mueve una hacia la otra.
**Fuente principal:** [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), sección 3.1
**Requisitos previos:** [Lección 4](0004-quantize-and-dequantize.md), [Rango de recorte](../GLOSSARY.md), [Error de recorte](../GLOSSARY.md), [Error de redondeo](../GLOSSARY.md)

## Calentamiento

1. ▢ Un cuantizador afín de 4 bits cubre el rango de -1 a 3. ¿Cuáles son su paso y su mayor error de redondeo?

<details markdown="1"><summary>Comprobación</summary>

El paso es `s = 4 / 15 = 0.267` y el mayor error de redondeo es `s/2 = 0.133`. El rango se divide en 2^4 - 1 = 15 pasos, y un valor dentro del rango se mueve como mucho medio paso.

</details>

2. ▢ Un valor queda fuera de los límites de la rejilla de un cuantizador. ¿Está su error acotado por `s/2`? ¿Cómo se llama ese error?

<details markdown="1"><summary>Comprobación</summary>

No. El valor se fija en el límite más cercano de la rejilla, y la distancia que recorre es el **error de recorte**, que no tiene una cota de `s/2` y crece con lo lejos que queda el valor fuera del rango.

</details>

3. ▢ ¿Por qué los cuantizadores suelen emparejar pesos simétricos con activaciones asimétricas?

<details markdown="1"><summary>Comprobación</summary>

Los pesos asimétricos multiplicados por activaciones asimétricas producen un término que depende de los datos de entrada, lo que cuesta latencia y potencia en tiempo de ejecución (Nagel et al., sección 2.4.1). Una rejilla simétrica de pesos elimina ese término, así que solo las activaciones conservan el zero-point extra.

</details>

## Qué debes saber

### Dos errores que tiran en direcciones opuestas

El **rango de recorte** es el intervalo de valores reales que cubre la rejilla de enteros, de `q_min` a `q_max`. Nagel et al. nombran todo el intercambio en una frase de la sección 2.2: ensanchar el rango reduce el error de recorte, pero necesita un scale mayor, y el error de redondeo, que está entre -s/2 y s/2, crece con él.

| Rango | Error de recorte | Error de redondeo | Qué sale mal |
|---|---|---|---|
| Demasiado estrecho | Grande: los outliers se fijan en el límite | Pequeño | Los valores mayores se sustituyen por el borde del rango |
| Demasiado ancho | Ninguno | Grande: el paso es grande | Los valores típicos caen en unos pocos niveles o se redondean a cero |

La sección 3.1 del paper llama a esto el intercambio clave al fijar el rango, y dice que cada método da un equilibrio distinto entre los dos errores. Los pesos se conocen de antemano, así que su rango no suele necesitar datos. El rango de una activación depende de la entrada, así que Nagel et al. dicen que suele necesitar unos pocos batches de datos de calibración, que es el trabajo del [calibration set](../GLOSSARY.md).

### Los métodos

**Min-max.** Toma el menor y el mayor valor como `q_min` y `q_max`. No tiene error de recorte, y Nagel et al. advierten que es sensible a los outliers, porque un outlier fuerte obliga a un paso grande y por tanto a un error de redondeo excesivo. Es lo que usó la lección 4.

**Error cuadrático medio.** Busca los `q_min` y `q_max` que minimizan el error cuadrático medio entre el tensor original y el cuantizado. El paper lista la búsqueda en rejilla, el método de la sección áurea y las aproximaciones en forma cerrada como maneras de resolverlo, y dice que las variantes de la literatura son todas muy parecidas. Es el método al que recurrir cuando los outliers inflan el rango min-max.

**Percentil.** Fija el rango en un percentil alto de los valores absolutos, como el 99.9, de modo que se recorte una fracción fija de los valores. Es una heurística simple, no uno de los métodos de la sección 3.1, y el experimento de abajo la usa para que veas qué cuesta y qué compra una fracción fija.

La sección 3.1 lista dos más para casos especiales: minimizar la entropía cruzada para los logits de la última capa, donde el orden de los valores mayores importa más que los muchos pequeños, y un rango basado en batch normalization para las activaciones. Este track cuantiza LLM sin batch normalization, así que usa los tres primeros.

Nagel et al. comparan los dos primeros en clasificadores de ImageNet en su Tabla 1, con los pesos cuantizados por tensor y las activaciones en punto flotante. Para ResNet18 a 8 bits, min-max y MSE quedan casi igualados: 69.57 frente a 69.45 de accuracy top-1. A 4 bits, min-max cae a 0.12 y MSE mantiene 18.82. Son modelos de visión, así que lee la forma del resultado y no los números: con pocos niveles, la elección del rango decide si el modelo funciona siquiera.

### Qué muestra el experimento

El experimento de la práctica cuantiza a 4 bits un tensor de cola pesada. Su mayor valor es 1.506 y su desviación estándar es 0.034, una razón de unas 44. Con el rango min-max, el paso es `1.506 / 7 = 0.215`, la mitad es 0.108, que es más de tres desviaciones estándar, así que casi todos los valores se redondean a cero. Recortar el 0.35 por ciento de los valores que recorta la búsqueda de MSE reduce el error unas seis veces. La rejilla se gasta en un rango que casi ningún valor visita.

### Por qué esta no es toda la respuesta para los LLM

MSE cuenta por igual el error cuadrático de cada valor. Nagel et al. hacen la misma observación sobre los logits: MSE puede no servir para valores de importancia desigual, porque pesa todos los valores por igual. En un LLM, los pocos valores mayores pueden ser los importantes. [Dettmers et al.](https://arxiv.org/abs/2208.07339) informan de que poner a cero las dimensiones de outlier features degradó la perplexity de validación entre un 600 y un 1000 por ciento, aunque representan cerca del 0.1 por ciento de las features. Un rango que las recorta tiene un efecto diminuto en el MSE del tensor y puede tener un efecto grande en el modelo. La lección 7 explica de dónde salen esos valores, y la lección 8 da las soluciones que no los recortan.

## Práctica

1. ▢ Un cuantizador simétrico con signo de 4 bits, con rejilla de -7 a 7, tiene un rango min-max de 1.506 sobre un tensor con desviación estándar 0.034. ¿Cuánto es `s`, y qué valores se redondean a cero?

<details markdown="1"><summary>Comprobación</summary>

`s = 1.506 / 7 = 0.215`. Todo valor con valor absoluto por debajo de `s/2 = 0.108` se redondea al entero 0, que es más de tres desviaciones estándar. Para un tensor con forma de campana eso es casi todos los valores, así que un único máximo lejano ha borrado el tensor.

</details>

2. ▢ ¿Qué afirmación describe ensanchar el rango de recorte?

    - a) El error de recorte y el de redondeo bajan ambos
    - b) El error de recorte y el de redondeo suben ambos
    - c) El error de recorte baja mientras el de redondeo sube
    - d) El error de recorte sube mientras el de redondeo baja

<details markdown="1"><summary>Comprobación</summary>

**c)** Un rango más ancho fija menos valores, así que el error de recorte baja, pero el mismo número de niveles abarca ahora más distancia, así que el paso y el error de redondeo crecen. (a) volvería trivial la elección del rango, ya que siempre habría que ensancharlo. (b) se equivoca en ambos, ya que ensanchar no puede subir el error de recorte. (d) describe estrechar el rango, no ensancharlo.

</details>

3. ▢ Predice y luego ejecuta. Esto cuantiza 100,000 valores de cola pesada a 4 bits bajo cuatro rangos. Antes de ejecutar, predice qué rango tiene el menor error cuadrático medio, y si min-max redondea a cero más o menos de la mitad de todos los valores.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.standard_t(df=3, size=100_000) * 0.02   # heavy-tailed
    qmax = 7                                        # 4-bit signed symmetric grid: -7..7 times the scale


    def quantize(x, c):
        s = c / qmax
        return s * np.clip(np.round(x / s), -qmax, qmax)


    def mse(x, c):
        return np.mean((quantize(x, c) - x) ** 2)


    grid = np.linspace(0.01, np.abs(x).max(), 400)
    ranges = {
        "min-max": np.abs(x).max(),
        "p99.9": np.percentile(np.abs(x), 99.9),
        "p99": np.percentile(np.abs(x), 99),
        "MSE search": grid[np.argmin([mse(x, c) for c in grid])],
    }
    print("max |x| =", round(np.abs(x).max(), 3), " std =", round(x.std(), 3))
    for name, c in ranges.items():
        q = quantize(x, c)
        print(f"{name:10s} c={c:.3f}  mse={mse(x, c):.2e}  clipped={np.mean(np.abs(x) > c):6.2%}  rounded to zero={np.mean(q == 0):6.2%}")
    ```

<details markdown="1"><summary>Pista</summary>

Calcula primero el paso de min-max, como en el ejercicio 1, y compara su mitad con la desviación estándar.

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=8.15e-04  clipped= 0.00%  rounded to zero=98.72%
p99.9      c=0.252  mse=1.61e-04  clipped= 0.10%  rounded to zero=56.61%
p99        c=0.117  mse=1.53e-04  clipped= 1.00%  rounded to zero=29.40%
MSE search c=0.171  mse=1.35e-04  clipped= 0.35%  rounded to zero=41.52%
```

La búsqueda de MSE gana, y min-max es el peor, unas seis veces más alto, con el 98.7 por ciento de los valores redondeados a cero. Recortar solo el 0.10 por ciento de los valores (p99.9) ya reduce el error cinco veces. Recortar el 1 por ciento (p99) es algo peor que la búsqueda (1.53e-04 frente a 1.35e-04), porque los valores recortados cuestan ahora más de lo que ahorra el redondeo: el mejor rango queda entre los extremos.

</details>

4. ▢ Predice y luego ejecuta. Cambia `qmax = 7` por `qmax = 127`, lo que lo convierte en una rejilla de 8 bits, y vuelve a ejecutar. ¿Seguirá ganando el recorte? ¿Qué rango elige ahora la búsqueda de MSE?

<details markdown="1"><summary>Comprobación</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=1.17e-05  clipped= 0.00%  rounded to zero=21.23%
p99.9      c=0.252  mse=5.51e-05  clipped= 0.10%  rounded to zero= 3.65%
p99        c=0.117  mse=1.30e-04  clipped= 1.00%  rounded to zero= 1.69%
MSE search c=1.019  mse=7.72e-06  clipped= 0.00%  rounded to zero=14.52%
```

El recorte ya no gana: min-max supera a ambos rangos por percentil, y la búsqueda de MSE elige 1.019, cerca del rango completo, con menos del 0.005 por ciento de los valores recortados. Con 127 niveles por lado el paso es lo bastante pequeño como para que los outliers cuesten poco error de redondeo, mientras que recortarlos cuesta mucho. Es la misma forma que la Tabla 1 de Nagel et al., donde min-max y MSE quedan igualados a 8 bits: cuantos menos niveles, más compensa un rango ajustado.

</details>

5. ▢ Un equipo fija el rango de cada activación de un LLM minimizando el MSE, y la perplexity se dispara. Usa esta lección para dar el mecanismo más probable, y di qué no pudo ver el MSE.

<details markdown="1"><summary>Comprobación</summary>

El rango recortó las outlier features. Son una parte diminuta de los valores, así que fijarlas cambia muy poco el MSE del tensor, pero importan mucho más de lo que sugiere su número: Dettmers et al. midieron una perplexity entre un 600 y un 1000 por ciento más alta cuando esas dimensiones se pusieron a cero. MSE pesa todos los valores por igual, y Nagel et al. señalan que esa es la ponderación equivocada cuando los valores difieren en importancia. El objetivo de fijación del rango es un proxy local de la pérdida de la tarea, y aquí apunta en la dirección equivocada. Mantener los outliers fuera del conjunto recortado es el tema de la lección 8.

</details>

## Prácticas en el mundo real

- [ ] Vuelve a ejecutar el experimento con `df=10`, y luego con `rng.normal` en lugar de `standard_t`. Anota el mejor recorte de la búsqueda de MSE como múltiplo de la desviación estándar cada vez, y observa cómo se mueve a medida que las colas se hacen más ligeras.
- [ ] Toma una matriz de pesos de un modelo abierto pequeño e imprime su valor absoluto máximo junto a sus percentiles 99 y 99.9 del valor absoluto. Decide si min-max desperdiciaría la mayor parte de una rejilla de 4 bits en ella.
- [ ] Mañana: sin apuntes, di qué optimiza cada uno de min-max, MSE y percentil, y qué ancho de bits hace que la elección importe más. Luego relee la sección 3.1 y comprueba si nombraste el intercambio correcto.

## Para profundizar

- [El mapeo de cuantización](../reference/quantization-mapping.md)
- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339), sección 4.2, para ver por qué es peligroso recortar outliers
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
