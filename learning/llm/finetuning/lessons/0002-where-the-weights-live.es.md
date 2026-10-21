---
title: "2. Dónde viven los pesos"
description: "Nombrar cada proyección a la que podría acoplarse un adapter"
type: lesson
---

# Lección 2. Dónde viven los pesos

**Vínculo con la misión:** Un adapter se acopla a matrices de pesos concretas. No puedes elegir cuáles hasta que seas capaz de nombrarlas y decir qué hace cada una.
**Fuente principal:** [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
**Requisitos previos:** [Lección 1](0001-what-a-base-model-is.md)

## Calentamiento

1. ▢ ¿Qué calcula un modelo de lenguaje, expresado como una función?

<details markdown="1"><summary>Comprobación</summary>

Entra una secuencia de tokens, sale una puntuación para cada token del vocabulario. La generación es un bucle alrededor de esa función, no parte de ella.

</details>

2. ▢ ¿Por qué un base model no logra seguir una instrucción?

<details markdown="1"><summary>Comprobación</summary>

Seguir instrucciones es un comportamiento entrenado que se añade encima de la predicción del siguiente token. Un base model solo tiene el objetivo de siguiente token, así que continúa el texto en lugar de obedecer.

</details>

## Qué debes saber

Casi todos los parámetros de un modelo moderno de solo decoder viven en uno de tres lugares: la tabla de embeddings, una pila de bloques transformer idénticos y la proyección de salida. Los bloques contienen la inmensa mayoría, y es donde se acoplan los adapters.

### Dentro de un bloque

Cada bloque tiene dos subcapas, cada una precedida por una normalización y envuelta en una conexión residual.

**Atención.** Cuatro proyecciones lineales, nombradas por convención según lo que producen:

| Nombre | Función |
|---|---|
| `q_proj` | Queries: lo que busca esta posición |
| `k_proj` | Keys: lo que ofrece cada posición como coincidencia |
| `v_proj` | Values: el contenido que realmente se recupera |
| `o_proj` | Mezcla el resultado de la atención de vuelta en el residual stream |

**MLP** (también llamado red feed-forward). En los modelos actuales suelen ser tres proyecciones en lugar de dos, debido a las activaciones con compuerta (gated):

| Nombre | Función |
|---|---|
| `gate_proj` | Produce la compuerta, que pasa por una activación |
| `up_proj` | Proyecta hacia arriba hasta la dimensión intermedia, más ancha |
| `down_proj` | Proyecta de vuelta hacia abajo hasta la dimensión oculta |

El MLP es más ancho que la dimensión oculta, normalmente de entre 2.5× y 4×, así que, pese a tener menos matrices de las que cabría esperar, **el MLP contiene más parámetros que la atención.** Ese hecho determina la elección de target modules en la lección 10.

### Contar

Una capa lineal con dimensión de entrada `d_in` y dimensión de salida `d_out` contiene `d_in × d_out` pesos. Para un modelo con tamaño oculto 2048, 24 capas y tamaño intermedio 5632:

- Atención por capa, ignorando la grouped-query attention: 4 × 2048 × 2048 ≈ 16.8M
- MLP por capa: 3 × 2048 × 5632 ≈ 34.6M
- Total por capa ≈ 51.4M, por 24 capas ≈ 1.23B
- Embeddings, con un vocabulario de 32k: 32000 × 2048 ≈ 65.5M, el doble si la proyección de salida no está atada

Eso explica prácticamente todo el modelo. No hay ninguna reserva oculta de parámetros en otro sitio.

### Una trampa que conviene conocer ya

La mayoría de los modelos actuales usan **grouped-query attention**, donde varias cabezas de query comparten un mismo conjunto de keys y values. Eso hace que `k_proj` y `v_proj` sean *más estrechas* que `q_proj` y `o_proj`, a menudo por un factor de cuatro u ocho. Cualquier cálculo que suponga que las cuatro proyecciones de atención son cuadradas contará de más, y cualquier suposición de que tienen el mismo tamaño producirá un conteo de parámetros del adapter equivocado en la lección 8.

### Encontrar los nombres reales

Nunca te fíes de una lista de nombres de módulos recordada de memoria. Los fija la implementación del modelo y difieren entre arquitecturas. Imprímelos:

```text
model := load_model("<some-small-model>")
for name, module in model.modules():
    if module is a linear layer:
        print(name, module.weight.shape)
```

Este es el diagnóstico más útil de todo el espacio de trabajo. Un fine-tune que en silencio no entrena nada suele significar un nombre de target module que no coincidió con nada.

## Práctica

1. ▢ Nombra las siete proyecciones lineales de un bloque transformer moderno típico.

<details markdown="1"><summary>Comprobación</summary>

`q_proj`, `k_proj`, `v_proj`, `o_proj` en la atención; `gate_proj`, `up_proj`, `down_proj` en el MLP.

Las arquitecturas más antiguas o sin compuerta tienen solo dos proyecciones en el MLP. Por eso imprimes los nombres en lugar de recitarlos.

</details>

2. ▢ Para un modelo con tamaño oculto 4096 y tamaño intermedio 11008, ¿cuál contiene más parámetros por capa, la atención o el MLP? ¿Aproximadamente por qué factor?

<details markdown="1"><summary>Comprobación</summary>

El MLP, aproximadamente por dos a uno. La atención (con proyecciones cuadradas) es 4 × 4096² ≈ 67M. El MLP es 3 × 4096 × 11008 ≈ 135M.

Con grouped-query attention la brecha se ensancha aún más, porque `k_proj` y `v_proj` se encogen mientras que el MLP no.

</details>

3. ▢ Configuras tu adapter para apuntar a `["query", "value"]` en un modelo cuyos módulos se llaman `q_proj` y `v_proj`. ¿Qué ocurre?

<details markdown="1"><summary>Comprobación</summary>

Nada coincide, así que o la biblioteca lanza un error o, peor según la versión, obtienes un modelo sin ningún peso de adapter entrenable. Entonces el entrenamiento se ejecuta, la pérdida apenas se mueve y la ejecución parece simplemente decepcionante en lugar de rota.

Comprueba el conteo de parámetros entrenables justo después de construir el adapter. La lección 11 lo convierte en un hábito.

</details>

4. ▢ ¿Por qué importa conocer la estructura del residual stream para los adapters?

<details markdown="1"><summary>Comprobación</summary>

Porque un adapter modifica la salida de una proyección, y la conexión residual significa que ese cambio se suma a un flujo en curso en lugar de reemplazarlo. Una contribución pequeña del adapter puede orientar el flujo sin destruir lo que las capas congeladas ya escribieron en él, y por eso empezar un adapter exactamente en cero (lección 9) es seguro.

</details>

5. ▢ Grouped-query attention: tus notas suponen que las cuatro proyecciones de atención son de 2048 × 2048, pero el modelo tiene 32 cabezas de query y 4 cabezas de key-value con dimensión de cabeza 64. ¿Cuáles son las formas reales?

<details markdown="1"><summary>Comprobación</summary>

`q_proj` y `o_proj` se quedan en 2048 × 2048 (32 × 64 = 2048). `k_proj` y `v_proj` son 2048 × 256 (4 × 64 = 256).

Así que la atención contiene unos 2 × 2048² + 2 × 2048 × 256 ≈ 9.4M por capa, no 16.8M. Casi la mitad de tu estimación.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el bucle de listado de módulos de arriba, usando la llamada real de inspección de modelos de tu biblioteca (p. ej. `named_modules()` en PyTorch), sobre el modelo más pequeño que puedas descargar. Escribe a mano en tus notas los siete nombres y sus formas.
- [ ] Solo a partir de las formas, calcula el conteo total de parámetros del modelo. Compáralo con el número de su model card y explica cualquier diferencia.
- [ ] Mañana: repite con un modelo de una familia distinta. Anota cada nombre de módulo que difiera.

## Para profundizar

- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): los conteos de parámetros se muestran por matriz
- [Paper: "Attention Is All You Need", Vaswani et al., arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [Lección 10. Elegir los target modules](0010-choosing-target-modules.md) es donde esto da su fruto

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
